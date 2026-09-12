"""Pore, collapse, and fracture pressure-window models.

Pressures are stored in pascal. Convert kPa or psi at the application
boundary. Version 1 interpolates in TVD between discrete points.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mpd_engine.units.validation import (
    PositiveFloat,
    validate_monotonically_increasing,
    validate_pressure_window_ordering,
)


class PressureWindowPoint(BaseModel):
    """Pressure limits at one true vertical depth."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tvd_m: PositiveFloat = Field(description="True vertical depth, m.")
    pore_pressure_pa: PositiveFloat = Field(description="Formation pore pressure, Pa.")
    fracture_pressure_pa: PositiveFloat = Field(description="Fracture pressure, Pa.")
    collapse_pressure_pa: PositiveFloat | None = Field(
        default=None,
        description="Wellbore collapse / hole-stability pressure, Pa, if defined.",
    )

    @model_validator(mode="after")
    def check_ordering(self) -> PressureWindowPoint:
        validate_pressure_window_ordering(
            self.pore_pressure_pa,
            self.fracture_pressure_pa,
            self.collapse_pressure_pa,
        )
        return self


class PressureWindow(BaseModel):
    """Discrete pressure-window curve versus TVD.

    Points must be strictly increasing in TVD. Version 1 requires at
    least two points so later interpolation has an interval.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    points: list[PressureWindowPoint] = Field(min_length=2)

    @model_validator(mode="after")
    def check_curve(self) -> PressureWindow:
        validate_monotonically_increasing(
            [point.tvd_m for point in self.points],
            name="pressure_window.tvd_m",
            strict=True,
        )
        return self
