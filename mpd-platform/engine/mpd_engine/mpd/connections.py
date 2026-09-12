"""Pump-on versus pump-off (connection) scenario comparison.

Version 1 compares two steady states. It does not model transients,
surge/swab, or choke actuation, and it does not control equipment.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from mpd_engine.hydraulics.ecd import (
    calculate_bottomhole_pressure,
    calculate_required_surface_backpressure,
)
from mpd_engine.results.warnings import EngineeringWarning, WarningSeverity
from mpd_engine.units.validation import NonNegativeFloat


class ConnectionComparison(BaseModel):
    """Steady-state pump-on / pump-off comparison at TD."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    hydrostatic_pressure_pa: NonNegativeFloat
    pump_on_friction_pa: NonNegativeFloat
    pump_on_sbp_pa: NonNegativeFloat
    pump_on_bhp_pa: NonNegativeFloat
    pump_off_friction_pa: NonNegativeFloat = 0.0
    pump_off_sbp_same_as_pump_on_bhp_pa: NonNegativeFloat
    required_sbp_pump_off_pa: float
    connection_pressure_difference_pa: NonNegativeFloat = Field(
        description="Annular friction lost when flow goes to zero, Pa."
    )
    sbp_limit_pa: float | None = None
    sbp_limit_exceeded: bool
    warnings: list[EngineeringWarning]


def compare_connection(
    hydrostatic_pressure_pa: float,
    pump_on_friction_pa: float,
    pump_on_sbp_pa: float,
    *,
    max_surface_backpressure_pa: float | None = None,
) -> ConnectionComparison:
    """Compare pump-on BHP with the SBP needed to hold it pump-off.

    Target BHP for the connection is the pump-on bottomhole pressure.
    Pump-off friction is zero in version 1 (no gel strength).
    """
    pump_on_bhp = calculate_bottomhole_pressure(
        hydrostatic_pressure_pa, pump_on_friction_pa, pump_on_sbp_pa
    )
    pump_off_same_sbp = calculate_bottomhole_pressure(
        hydrostatic_pressure_pa, 0.0, pump_on_sbp_pa
    )
    required_sbp_off = calculate_required_surface_backpressure(
        pump_on_bhp, hydrostatic_pressure_pa, 0.0
    )
    warnings: list[EngineeringWarning] = []
    exceeded = False
    if max_surface_backpressure_pa is not None and required_sbp_off > max_surface_backpressure_pa:
        exceeded = True
        warnings.append(
            EngineeringWarning(
                code="CONNECTION_SBP_EXCEEDS_LIMIT",
                severity=WarningSeverity.HIGH,
                actual_pressure_pa=required_sbp_off,
                limit_pressure_pa=max_surface_backpressure_pa,
                explanation=(
                    "Surface backpressure required to hold pump-on BHP during a "
                    "pump-off / connection exceeds the configured review limit."
                ),
                recommended_engineering_review=(
                    "Review connection procedure, mud weight, and SBP limit. "
                    "This application does not send commands to the choke."
                ),
            )
        )
    warnings.append(
        EngineeringWarning(
            code="CONNECTION_STEADY_STATE_ONLY",
            severity=WarningSeverity.INFO,
            explanation=(
                "Connection comparison is a steady-state pump-on versus pump-off "
                "snapshot. Surge, swab, and choke-response transients are not modelled."
            ),
            recommended_engineering_review=(
                "Do not use this result as an automated connection controller."
            ),
        )
    )
    return ConnectionComparison(
        hydrostatic_pressure_pa=hydrostatic_pressure_pa,
        pump_on_friction_pa=pump_on_friction_pa,
        pump_on_sbp_pa=pump_on_sbp_pa,
        pump_on_bhp_pa=pump_on_bhp,
        pump_off_friction_pa=0.0,
        pump_off_sbp_same_as_pump_on_bhp_pa=pump_off_same_sbp,
        required_sbp_pump_off_pa=required_sbp_off,
        connection_pressure_difference_pa=pump_on_friction_pa,
        sbp_limit_pa=max_surface_backpressure_pa,
        sbp_limit_exceeded=exceeded,
        warnings=warnings,
    )
