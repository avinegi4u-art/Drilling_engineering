"""Pore, collapse, and fracture pressure vs TVD.

Pressures are stored in Pa. Depths are stored in metres.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from mpd_engine.models.base import EngineModel
from mpd_engine.units.validation import FiniteNonNegative, require_monotonic_increasing


class PressureWindowPoint(EngineModel):
    """Pressure-window values at one true vertical depth."""

    tvd_m: FiniteNonNegative = Field(description="True vertical depth, m.")
    pore_pressure_pa: FiniteNonNegative = Field(description="Pore pressure, Pa.")
    collapse_pressure_pa: FiniteNonNegative = Field(
        description="Collapse / wellbore-stability lower bound, Pa."
    )
    fracture_pressure_pa: FiniteNonNegative = Field(description="Fracture pressure, Pa.")

    @model_validator(mode="after")
    def _window_ordering(self) -> PressureWindowPoint:
        if self.fracture_pressure_pa <= self.pore_pressure_pa:
            raise ValueError("fracture_pressure_pa must be greater than pore_pressure_pa.")
        if self.fracture_pressure_pa <= self.collapse_pressure_pa:
            raise ValueError("fracture_pressure_pa must be greater than collapse_pressure_pa.")
        return self


class PressureWindowCurve(EngineModel):
    """Pressure-window curve sampled vs TVD.

    Points must be ordered by strictly increasing TVD. Interpolation is added
    in a later phase; version 1 only validates the curve.
    """

    points: list[PressureWindowPoint] = Field(min_length=1)

    @model_validator(mode="after")
    def _increasing_tvd(self) -> PressureWindowCurve:
        require_monotonic_increasing(
            [point.tvd_m for point in self.points],
            name="pressure-window TVD",
        )
        return self
