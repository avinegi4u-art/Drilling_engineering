"""Orchestrate a version-1 MPD hydraulics calculation.

Call this service from scripts, notebooks, FastAPI, Streamlit, or jobs.
Do not re-implement engineering equations in those layers.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mpd_engine.constants import (
    CALCULATION_VERSION,
    LAMINAR_REYNOLDS_LIMIT,
    STANDARD_GRAVITY_M_S2,
    VERSION_1_ASSUMPTIONS,
)
from mpd_engine.hydraulics.ecd import (
    calculate_bottomhole_pressure,
    calculate_ecd_kg_m3,
)
from mpd_engine.hydraulics.geometry import (
    calculate_annular_area,
    calculate_annular_velocity,
    calculate_hydraulic_diameter,
)
from mpd_engine.hydraulics.hydrostatic import calculate_hydrostatic_pressure
from mpd_engine.hydraulics.pressure_profile import (
    annular_friction_to_surface,
    hole_id_at_md,
    pipe_od_at_md,
    section_boundaries,
    tvd_at_md,
)
from mpd_engine.hydraulics.rheology import reynolds_number
from mpd_engine.models.drillstring import Drillstring
from mpd_engine.models.fluids import FluidProperties
from mpd_engine.models.operating_conditions import OperatingConditions, OperatingMode
from mpd_engine.models.pressure_window import PressureWindow
from mpd_engine.models.well import Well
from mpd_engine.mpd.connections import compare_connection
from mpd_engine.mpd.limits import turbulent_flow_warning
from mpd_engine.mpd.pressure_window import (
    PressureWindowStatus,
    classify_pressure_window,
    interpolate_pressure_window,
)
from mpd_engine.mpd.surface_backpressure import required_surface_backpressure_with_limit
from mpd_engine.results.result_models import (
    CalculationResult,
    CalculationSummary,
    DepthPointResult,
)
from mpd_engine.results.warnings import EngineeringWarning, WarningSeverity
from mpd_engine.units.validation import (
    PositiveFloat,
    require_positive,
    validate_annular_clearance,
)


class HydraulicsCase(BaseModel):
    """Complete input set for one calculation run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    well: Well
    drillstring: Drillstring
    fluid: FluidProperties
    operating: OperatingConditions
    pressure_window: PressureWindow
    target_bottomhole_pressure_pa: PositiveFloat | None = None
    depth_step_m: PositiveFloat = Field(default=50.0, description="Profile sampling interval, m.")

    @model_validator(mode="after")
    def check_string_covers_td(self) -> HydraulicsCase:
        td = self.well.sections[-1].md_bottom_m
        if self.drillstring.total_length_m + 1.0e-3 < td:
            raise ValueError(
                "Drillstring length "
                f"({self.drillstring.total_length_m} m) is shorter than well TD ({td} m)"
            )
        mid = td / 2.0
        validate_annular_clearance(
            hole_id_at_md(self.well, mid), pipe_od_at_md(self.drillstring, mid)
        )
        return self


def _profile_depths(case: HydraulicsCase) -> list[float]:
    td = case.well.sections[-1].md_bottom_m
    step = require_positive(case.depth_step_m, "depth_step_m")
    depths = {0.0, td}
    cursor = 0.0
    while cursor < td:
        cursor = min(td, cursor + step)
        depths.add(cursor)
    depths.update(section_boundaries(case.well.sections))
    depths.update(point.tvd_m for point in case.pressure_window.points if 0.0 <= point.tvd_m <= td)
    return sorted(depths)


def run_hydraulics(case: HydraulicsCase) -> CalculationResult:
    """Run the steady-state version-1 hydraulics model.

    Raises ValueError if inputs are physically invalid. Failed calculations
    are not replaced with default numeric results.
    """
    warnings: list[EngineeringWarning] = [
        EngineeringWarning(
            code="VERSION_1_STEADY_STATE",
            severity=WarningSeverity.INFO,
            explanation=" ".join(VERSION_1_ASSUMPTIONS),
            recommended_engineering_review=(
                "Confirm that version-1 assumptions are acceptable for this well "
                "before using the numbers in an operational discussion."
            ),
        )
    ]
    td_md = case.well.sections[-1].md_bottom_m
    td_tvd = tvd_at_md(case.well, td_md)
    flow = case.operating.flow_rate_m3_s
    sbp = case.operating.surface_backpressure_pa

    if flow > 0.0:
        hole_id = hole_id_at_md(case.well, td_md)
        pipe_od = pipe_od_at_md(case.drillstring, td_md)
        area = calculate_annular_area(hole_id, pipe_od)
        velocity = calculate_annular_velocity(flow, area)
        diameter = calculate_hydraulic_diameter(hole_id, pipe_od)
        if case.fluid.plastic_viscosity_pa_s > 0.0:
            re_pv = reynolds_number(
                case.fluid.mud_density_kg_m3,
                velocity,
                diameter,
                case.fluid.plastic_viscosity_pa_s,
            )
            if re_pv > LAMINAR_REYNOLDS_LIMIT:
                warnings.append(turbulent_flow_warning(re_pv, depth_m=td_md))

    profile: list[DepthPointResult] = []
    for md in _profile_depths(case):
        tvd = tvd_at_md(case.well, md)
        hydrostatic = calculate_hydrostatic_pressure(case.fluid.mud_density_kg_m3, tvd)
        friction = annular_friction_to_surface(
            case.well, case.drillstring, case.fluid, flow, md
        )
        annular = calculate_bottomhole_pressure(hydrostatic, friction, sbp)
        ecd = None
        if tvd > 0.0:
            ecd = calculate_ecd_kg_m3(annular, tvd, STANDARD_GRAVITY_M_S2)
        interpolated = interpolate_pressure_window(case.pressure_window, tvd)
        status, window_warnings = classify_pressure_window(annular, interpolated)
        if tvd > 0.0:
            warnings.extend(window_warnings)
        elif status is PressureWindowStatus.INVALID_INPUT:
            # Surface TVD is often shallower than the first window station.
            pass
        profile.append(
            DepthPointResult(
                md_m=md,
                tvd_m=tvd,
                hydrostatic_pressure_pa=hydrostatic,
                annular_friction_to_surface_pa=friction,
                surface_backpressure_pa=sbp,
                annular_pressure_pa=annular,
                ecd_kg_m3=ecd,
                pore_pressure_pa=(
                    interpolated.pore_pressure_pa if interpolated.within_curve_range else None
                ),
                collapse_pressure_pa=(
                    interpolated.collapse_pressure_pa if interpolated.within_curve_range else None
                ),
                fracture_pressure_pa=(
                    interpolated.fracture_pressure_pa if interpolated.within_curve_range else None
                ),
                window_status=(
                    status
                    if tvd > 0.0
                    else (
                        PressureWindowStatus.INVALID_INPUT
                        if not interpolated.within_curve_range
                        else PressureWindowStatus.WITHIN_OPERATING_WINDOW
                    )
                ),
            )
        )

    td_point = profile[-1]
    required_sbp: float | None = None
    if case.target_bottomhole_pressure_pa is not None:
        required_sbp, sbp_warnings = required_surface_backpressure_with_limit(
            case.target_bottomhole_pressure_pa,
            td_point.hydrostatic_pressure_pa,
            td_point.annular_friction_to_surface_pa,
            case.operating.max_surface_backpressure_pa,
        )
        warnings.extend(sbp_warnings)

    connection = None
    if case.operating.operating_mode in {
        OperatingMode.DRILLING,
        OperatingMode.CIRCULATION,
        OperatingMode.PUMP_ON,
        OperatingMode.CONNECTION,
        OperatingMode.PUMP_OFF,
    }:
        connection = compare_connection(
            td_point.hydrostatic_pressure_pa,
            td_point.annular_friction_to_surface_pa
            if flow > 0.0
            else annular_friction_to_surface(
                case.well,
                case.drillstring,
                case.fluid,
                # Reconstruct a representative pump-on rate from the case when
                # the current mode is already pump-off: use 0 friction as-is
                # and still report required SBP to hold current BHP.
                flow,
                td_md,
            ),
            sbp,
            max_surface_backpressure_pa=case.operating.max_surface_backpressure_pa,
        )
        warnings.extend(connection.warnings)

    if (
        case.operating.max_surface_backpressure_pa is not None
        and sbp > case.operating.max_surface_backpressure_pa
    ):
        warnings.append(
            EngineeringWarning(
                code="APPLIED_SBP_EXCEEDS_LIMIT",
                severity=WarningSeverity.HIGH,
                actual_pressure_pa=sbp,
                limit_pressure_pa=case.operating.max_surface_backpressure_pa,
                explanation="Entered surface backpressure exceeds the configured review limit.",
                recommended_engineering_review=(
                    "Review the applied SBP value. This application does not change "
                    "choke position."
                ),
            )
        )

    summary = CalculationSummary(
        tvd_m=td_tvd,
        hydrostatic_pressure_pa=td_point.hydrostatic_pressure_pa,
        annular_friction_pressure_pa=td_point.annular_friction_to_surface_pa,
        surface_backpressure_pa=sbp,
        bottomhole_pressure_pa=td_point.annular_pressure_pa,
        ecd_kg_m3=td_point.ecd_kg_m3,
        required_surface_backpressure_pa=required_sbp,
        window_status=td_point.window_status,
        operating_mode=case.operating.operating_mode.value,
        flow_rate_m3_s=flow,
    )
    return CalculationResult(
        calculation_version=CALCULATION_VERSION,
        timestamp_utc=CalculationResult.utc_now(),
        assumptions=VERSION_1_ASSUMPTIONS,
        summary=summary,
        profile=profile,
        warnings=warnings,
        connection=connection,
    )
