"""Operating conditions for a steady-state hydraulics case.

Internal units:

- Flow rate: m³/s
- Surface backpressure: Pa
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from mpd_engine.models.base import EngineModel
from mpd_engine.units.validation import FiniteNonNegative


class OperatingMode(StrEnum):
    """Steady-state operating modes. None of these imply equipment control."""

    DRILLING = "drilling"
    CIRCULATION = "circulation"
    CONNECTION = "connection"
    PUMP_OFF = "pump_off"
    PUMP_ON = "pump_on"


# Modes that represent pumps-off / no annular flow in the version 1 model.
ZERO_FLOW_MODES = frozenset({OperatingMode.CONNECTION, OperatingMode.PUMP_OFF})

# Conservative sanity cap for surface backpressure (20 MPa). Not a field procedure.
_MAX_REASONABLE_SBP_PA = 20.0e6
# Conservative sanity cap for flow (~6000 L/min).
_MAX_REASONABLE_FLOW_M3_S = 0.1


class OperatingConditions(EngineModel):
    """Mud-pump and choke-side boundary conditions for one calculation.

    This model stores requested engineering inputs. It does not command a choke
    or mud pumps.
    """

    flow_rate_m3_s: FiniteNonNegative = Field(
        description="Volumetric flow rate, m³/s. Zero is valid for pump-off cases."
    )
    surface_backpressure_pa: FiniteNonNegative = Field(
        description="Applied surface backpressure, Pa."
    )
    operating_mode: OperatingMode
    max_surface_backpressure_pa: FiniteNonNegative | None = Field(
        default=None,
        description="Configured SBP limit used later for connection warnings, Pa.",
    )

    @model_validator(mode="after")
    def _mode_and_limits(self) -> OperatingConditions:
        if self.flow_rate_m3_s > _MAX_REASONABLE_FLOW_M3_S:
            raise ValueError(
                f"flow_rate_m3_s {self.flow_rate_m3_s} exceeds the version 1 sanity limit "
                f"of {_MAX_REASONABLE_FLOW_M3_S} m³/s."
            )
        if self.surface_backpressure_pa > _MAX_REASONABLE_SBP_PA:
            raise ValueError(
                f"surface_backpressure_pa exceeds the version 1 sanity limit "
                f"of {_MAX_REASONABLE_SBP_PA} Pa."
            )
        if (
            self.max_surface_backpressure_pa is not None
            and self.max_surface_backpressure_pa > _MAX_REASONABLE_SBP_PA
        ):
            raise ValueError(
                f"max_surface_backpressure_pa exceeds the version 1 sanity limit "
                f"of {_MAX_REASONABLE_SBP_PA} Pa."
            )
        if self.operating_mode in ZERO_FLOW_MODES and self.flow_rate_m3_s != 0.0:
            raise ValueError(
                f"operating_mode {self.operating_mode} requires flow_rate_m3_s = 0."
            )
        return self
