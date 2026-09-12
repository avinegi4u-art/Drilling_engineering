"""Operating-condition models for MPD scenario comparison.

Flow rate is stored in m³/s. Surface backpressure is stored in Pa.
Convert L/min and kPa at the application boundary.

This module describes intended well conditions. It does not send
commands to chokes or other field equipment.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mpd_engine.units.validation import (
    MAX_FLOW_RATE_M3_S,
    MAX_SURFACE_BACKPRESSURE_PA,
    NonNegativeFloat,
    PositiveFloat,
)


class OperatingMode(StrEnum):
    """Steady-state operating mode for version-1 scenario comparison."""

    DRILLING = "drilling"
    CIRCULATION = "circulation"
    CONNECTION = "connection"
    PUMP_OFF = "pump_off"
    PUMP_ON = "pump_on"


_ZERO_FLOW_MODES = {OperatingMode.CONNECTION, OperatingMode.PUMP_OFF}


class OperatingConditions(BaseModel):
    """Flow and surface-backpressure setpoints for one calculation.

    Version 1 treats these as engineer-entered scenario values, not as
    live control setpoints. ``CONNECTION`` and ``PUMP_OFF`` require
    zero flow so the comparison is unambiguous.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    flow_rate_m3_s: NonNegativeFloat = Field(description="Pump flow rate, m³/s.")
    surface_backpressure_pa: NonNegativeFloat = Field(
        description="Applied surface backpressure, Pa. Not a choke command."
    )
    operating_mode: OperatingMode
    max_surface_backpressure_pa: PositiveFloat | None = Field(
        default=None,
        description="Engineer-configured SBP review limit, Pa. Optional.",
    )

    @model_validator(mode="after")
    def check_conditions(self) -> OperatingConditions:
        if self.flow_rate_m3_s > MAX_FLOW_RATE_M3_S:
            raise ValueError(
                f"flow_rate_m3_s ({self.flow_rate_m3_s}) exceeds the version-1 "
                f"limit of {MAX_FLOW_RATE_M3_S} m³/s"
            )
        if self.surface_backpressure_pa > MAX_SURFACE_BACKPRESSURE_PA:
            raise ValueError(
                f"surface_backpressure_pa ({self.surface_backpressure_pa}) exceeds "
                f"the version-1 limit of {MAX_SURFACE_BACKPRESSURE_PA} Pa"
            )
        if (
            self.max_surface_backpressure_pa is not None
            and self.max_surface_backpressure_pa > MAX_SURFACE_BACKPRESSURE_PA
        ):
            raise ValueError(
                "max_surface_backpressure_pa exceeds the version-1 limit of "
                f"{MAX_SURFACE_BACKPRESSURE_PA} Pa"
            )
        if self.operating_mode in _ZERO_FLOW_MODES and self.flow_rate_m3_s != 0.0:
            raise ValueError(
                f"operating_mode {self.operating_mode.value} requires flow_rate_m3_s "
                f"to be 0, got {self.flow_rate_m3_s}"
            )
        return self
