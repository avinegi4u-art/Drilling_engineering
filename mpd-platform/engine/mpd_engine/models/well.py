"""Well trajectory and annular geometry domain models.

All lengths are stored in metres (SI). Display units such as millimetres
must be converted at the application boundary before constructing a model.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from mpd_engine.models.base import EngineModel
from mpd_engine.units.validation import (
    FiniteFloat,
    FiniteNonNegative,
    FinitePositive,
    require_monotonic_increasing,
    require_tvd_not_greater_than_md,
)


class AnnularSectionType(StrEnum):
    """Outer wall that defines the annulus for a well section."""

    CASING = "casing"
    OPEN_HOLE = "open_hole"


class TrajectoryStation(EngineModel):
    """One survey / trajectory station.

    Version 1 assumes a vertical well (inclination 0°). Inclination is stored
    so later phases can compute TVD from a directional survey.
    """

    md_m: FiniteNonNegative = Field(description="Measured depth from a common datum, m.")
    tvd_m: FiniteNonNegative = Field(description="True vertical depth from the same datum, m.")
    inclination_deg: float = Field(
        default=0.0,
        ge=0.0,
        le=180.0,
        description="Hole inclination from vertical, degrees. 0 is vertical.",
    )

    @model_validator(mode="after")
    def _tvd_versus_md(self) -> TrajectoryStation:
        require_tvd_not_greater_than_md(tvd_m=self.tvd_m, md_m=self.md_m)
        return self


class WellSection(EngineModel):
    """One casing or open-hole interval.

    Version 1 typically uses a single section. Multiple sections are allowed
    so later phases can stack casing, liner, and open hole.
    """

    name: str = Field(min_length=1, description="Section name, for example '8.5 in open hole'.")
    top_md_m: FiniteNonNegative = Field(description="Section top measured depth, m.")
    bottom_md_m: FinitePositive = Field(description="Section bottom measured depth, m.")
    top_tvd_m: FiniteNonNegative = Field(description="Section top true vertical depth, m.")
    bottom_tvd_m: FinitePositive = Field(description="Section bottom true vertical depth, m.")
    hole_id_m: FinitePositive = Field(
        description="Open-hole inner diameter, m. Always required for geometry records."
    )
    casing_id_m: FinitePositive | None = Field(
        default=None,
        description="Casing/liner inner diameter, m. Required when annular_section_type is casing.",
    )
    annular_section_type: AnnularSectionType = Field(
        description="Whether the annulus is inside casing or open hole."
    )

    @model_validator(mode="after")
    def _section_geometry(self) -> WellSection:
        if self.bottom_md_m <= self.top_md_m:
            raise ValueError("bottom_md_m must be greater than top_md_m.")
        if self.bottom_tvd_m < self.top_tvd_m:
            raise ValueError("bottom_tvd_m must be greater than or equal to top_tvd_m.")
        require_tvd_not_greater_than_md(tvd_m=self.top_tvd_m, md_m=self.top_md_m)
        require_tvd_not_greater_than_md(tvd_m=self.bottom_tvd_m, md_m=self.bottom_md_m)
        if self.annular_section_type is AnnularSectionType.CASING and self.casing_id_m is None:
            raise ValueError("casing_id_m is required when annular_section_type is casing.")
        return self

    @property
    def annular_outer_diameter_m(self) -> float:
        """Inner diameter of the outer wall of the annulus, m."""
        if self.annular_section_type is AnnularSectionType.CASING:
            if self.casing_id_m is None:
                raise ValueError("casing_id_m is required for a casing annulus.")
            return self.casing_id_m
        return self.hole_id_m

    @property
    def length_md_m(self) -> float:
        """Section length along measured depth, m."""
        return self.bottom_md_m - self.top_md_m


class Well(EngineModel):
    """Well header, trajectory, and annular sections.

    Version 1 expects a vertical well. Trajectory stations are still required
    so TVD is explicit rather than implied.
    """

    name: str = Field(min_length=1, description="Well name.")
    kelly_bushing_elevation_m: FiniteFloat = Field(
        default=0.0,
        description="Kelly bushing elevation above the chosen datum, m. Reserved for later use.",
    )
    water_depth_m: FiniteNonNegative = Field(
        default=0.0,
        description="Water depth, m. Zero for land wells. Reserved for later use.",
    )
    trajectory: list[TrajectoryStation] = Field(
        min_length=1,
        description="Trajectory stations ordered by increasing measured depth.",
    )
    sections: list[WellSection] = Field(
        min_length=1,
        description="Casing and open-hole sections covering the well.",
    )

    @model_validator(mode="after")
    def _well_consistency(self) -> Well:
        require_monotonic_increasing(
            [station.md_m for station in self.trajectory],
            name="trajectory measured depth",
        )
        require_monotonic_increasing(
            [station.tvd_m for station in self.trajectory],
            name="trajectory true vertical depth",
            allow_equal=True,
        )
        section_bottoms = [section.bottom_md_m for section in self.sections]
        require_monotonic_increasing(section_bottoms, name="section bottom measured depth")
        for previous, current in zip(self.sections, self.sections[1:], strict=False):
            if current.top_md_m < previous.bottom_md_m:
                raise ValueError("Well sections must not overlap in measured depth.")
        return self

    @property
    def total_depth_md_m(self) -> float:
        """Deepest measured depth from trajectory or sections, m."""
        return max(
            self.trajectory[-1].md_m,
            self.sections[-1].bottom_md_m,
        )

    @property
    def total_depth_tvd_m(self) -> float:
        """Deepest true vertical depth from trajectory or sections, m."""
        return max(
            self.trajectory[-1].tvd_m,
            self.sections[-1].bottom_tvd_m,
        )
