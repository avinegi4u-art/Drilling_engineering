"""Reusable synthetic cases. These are not field data."""

from __future__ import annotations

from mpd_engine.models.case import HydraulicsCase
from mpd_engine.models.drillstring import Drillstring, DrillstringComponentType, DrillstringSegment
from mpd_engine.models.fluids import FluidProperties, RheologyModel
from mpd_engine.models.operating_conditions import OperatingConditions, OperatingMode
from mpd_engine.models.pressure_window import PressureWindowCurve, PressureWindowPoint
from mpd_engine.models.well import AnnularSectionType, TrajectoryStation, Well, WellSection


def example_vertical_well_case() -> HydraulicsCase:
    """Return the synthetic example case that matches ``examples/sample_well.json``."""
    return HydraulicsCase(
        well=Well(
            name="Example Vertical Well A",
            kelly_bushing_elevation_m=0.0,
            water_depth_m=0.0,
            trajectory=[
                TrajectoryStation(md_m=0.0, tvd_m=0.0, inclination_deg=0.0),
                TrajectoryStation(md_m=3000.0, tvd_m=3000.0, inclination_deg=0.0),
            ],
            sections=[
                WellSection(
                    name="8.5 in open hole",
                    top_md_m=0.0,
                    bottom_md_m=3000.0,
                    top_tvd_m=0.0,
                    bottom_tvd_m=3000.0,
                    hole_id_m=0.2159,
                    casing_id_m=None,
                    annular_section_type=AnnularSectionType.OPEN_HOLE,
                )
            ],
        ),
        drillstring=Drillstring(
            segments=[
                DrillstringSegment(
                    component_type=DrillstringComponentType.DRILLPIPE,
                    length_m=2800.0,
                    outer_diameter_m=0.1270,
                    inner_diameter_m=0.1086,
                    description="5 in drillpipe",
                ),
                DrillstringSegment(
                    component_type=DrillstringComponentType.BHA,
                    length_m=200.0,
                    outer_diameter_m=0.1651,
                    inner_diameter_m=0.0714,
                    description="6.5 in BHA",
                ),
            ]
        ),
        fluid=FluidProperties(
            mud_density_kg_m3=1200.0,
            plastic_viscosity_pa_s=0.020,
            yield_stress_pa=4.788,
            temperature_c=50.0,
            rheology_model=RheologyModel.BINGHAM_PLASTIC,
        ),
        operating=OperatingConditions(
            flow_rate_m3_s=0.02,
            surface_backpressure_pa=1_500_000.0,
            operating_mode=OperatingMode.DRILLING,
            max_surface_backpressure_pa=5_000_000.0,
        ),
        pressure_window=PressureWindowCurve(
            points=[
                PressureWindowPoint(
                    tvd_m=0.0,
                    pore_pressure_pa=0.0,
                    collapse_pressure_pa=0.0,
                    fracture_pressure_pa=101_325.0,
                ),
                PressureWindowPoint(
                    tvd_m=3000.0,
                    pore_pressure_pa=33_000_000.0,
                    collapse_pressure_pa=34_000_000.0,
                    fracture_pressure_pa=51_000_000.0,
                ),
            ]
        ),
        notes="Synthetic example well. Not field data.",
    )
