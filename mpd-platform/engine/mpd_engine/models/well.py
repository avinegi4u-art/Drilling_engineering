"""Well trajectory and wellbore geometry domain models.

All lengths are stored in metres. Convert millimetres or feet at the
API or dashboard boundary before constructing these models.

Version 1 assumption: a vertical well with a single constant-diameter
section is sufficient. Multi-section and survey interpolation can be
added later without changing the SI field names.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mpd_engine.units.validation import (
    MAX_WELL_DEPTH_M,
    NonNegativeFloat,
    PositiveFloat,
    require_nonnegative,
    validate_monotonically_increasing,
    validate_tvd_not_greater_than_md,
)


class AnnularSectionType(StrEnum):
    """Outer wall of the annulus in a wellbore interval."""

    OPEN_HOLE = "open_hole"
    CASING = "casing"


class TrajectoryStation(BaseModel):
    """One survey or planned wellpath station.

    For a vertical well, ``tvd_m`` equals ``md_m``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    md_m: NonNegativeFloat = Field(description="Measured depth from the reference, m.")
    tvd_m: NonNegativeFloat = Field(description="True vertical depth from the reference, m.")
    inclination_deg: NonNegativeFloat = Field(
        default=0.0,
        description="Hole inclination from vertical, degrees. Version 1 uses 0 for vertical wells.",
    )

    @model_validator(mode="after")
    def check_station(self) -> TrajectoryStation:
        if self.md_m > MAX_WELL_DEPTH_M:
            raise ValueError(
                f"md_m ({self.md_m}) exceeds the version-1 limit of {MAX_WELL_DEPTH_M} m"
            )
        if self.tvd_m > MAX_WELL_DEPTH_M:
            raise ValueError(
                f"tvd_m ({self.tvd_m}) exceeds the version-1 limit of {MAX_WELL_DEPTH_M} m"
            )
        if self.inclination_deg > 180.0:
            raise ValueError(f"inclination_deg ({self.inclination_deg}) must be at most 180")
        validate_tvd_not_greater_than_md(self.md_m, self.tvd_m)
        return self


class WellSection(BaseModel):
    """One wellbore interval with constant outer annular diameter.

    ``hole_id_m`` is the inner diameter of the wellbore wall: open-hole
    diameter or casing/liner ID. Store metres, not millimetres.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, description="Engineer-facing section name.")
    md_top_m: NonNegativeFloat
    md_bottom_m: PositiveFloat
    tvd_top_m: NonNegativeFloat
    tvd_bottom_m: PositiveFloat
    hole_id_m: PositiveFloat = Field(
        description="Annulus outer diameter (open-hole ID or casing ID), m."
    )
    annular_section_type: AnnularSectionType
    casing_id_m: PositiveFloat | None = Field(
        default=None,
        description="Casing inner diameter, m. Required when annular_section_type is casing.",
    )

    @model_validator(mode="after")
    def check_section(self) -> WellSection:
        if self.md_bottom_m <= self.md_top_m:
            raise ValueError(
                f"md_bottom_m ({self.md_bottom_m}) must be greater than md_top_m ({self.md_top_m})"
            )
        if self.tvd_bottom_m < self.tvd_top_m:
            raise ValueError(
                f"tvd_bottom_m ({self.tvd_bottom_m}) must be >= tvd_top_m ({self.tvd_top_m})"
            )
        validate_tvd_not_greater_than_md(self.md_top_m, self.tvd_top_m)
        validate_tvd_not_greater_than_md(self.md_bottom_m, self.tvd_bottom_m)
        if self.annular_section_type is AnnularSectionType.CASING:
            if self.casing_id_m is None:
                raise ValueError("casing_id_m is required for a cased annular section")
            if abs(self.casing_id_m - self.hole_id_m) > 1.0e-9:
                raise ValueError(
                    "For a cased section, hole_id_m is the casing inner diameter and "
                    f"must equal casing_id_m (hole_id_m={self.hole_id_m}, "
                    f"casing_id_m={self.casing_id_m})"
                )
        return self


class Well(BaseModel):
    """A well with a trajectory and one or more geometry sections.

    Version 1 typically uses a single open-hole or cased section from
    surface to TD. Additional sections can be appended later.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    trajectory: list[TrajectoryStation] = Field(min_length=1)
    sections: list[WellSection] = Field(min_length=1)

    @model_validator(mode="after")
    def check_well(self) -> Well:
        validate_monotonically_increasing(
            [station.md_m for station in self.trajectory],
            name="trajectory.md_m",
            strict=True,
        )
        validate_monotonically_increasing(
            [station.tvd_m for station in self.trajectory],
            name="trajectory.tvd_m",
            strict=False,
        )
        validate_monotonically_increasing(
            [section.md_top_m for section in self.sections]
            + [self.sections[-1].md_bottom_m],
            name="section.md",
            strict=True,
        )
        for previous, current in zip(self.sections, self.sections[1:], strict=False):
            if abs(previous.md_bottom_m - current.md_top_m) > 1.0e-6:
                raise ValueError(
                    "Well sections must be contiguous in measured depth: "
                    f"{previous.name} ends at {previous.md_bottom_m} m, "
                    f"{current.name} starts at {current.md_top_m} m"
                )
        td_md = self.sections[-1].md_bottom_m
        last_station_md = self.trajectory[-1].md_m
        if abs(last_station_md - td_md) > 1.0e-6:
            raise ValueError(
                "The last trajectory station MD must match the last section "
                f"md_bottom_m (station={last_station_md}, section={td_md})"
            )
        return self

    @classmethod
    def vertical(
        cls,
        name: str,
        td_m: float,
        hole_id_m: float,
        *,
        annular_section_type: AnnularSectionType = AnnularSectionType.OPEN_HOLE,
        casing_id_m: float | None = None,
        section_name: str = "section_1",
    ) -> Well:
        """Build a vertical well where TVD equals MD at every station.

        This is the version-1 geometry helper. Deviated-well interpolation
        will replace this factory in a later version.
        """
        if annular_section_type is AnnularSectionType.CASING:
            if casing_id_m is None:
                raise ValueError("casing_id_m is required for a cased vertical well")
            outer_id_m = casing_id_m
        else:
            outer_id_m = hole_id_m
        return cls(
            name=name,
            trajectory=[
                TrajectoryStation(md_m=0.0, tvd_m=0.0, inclination_deg=0.0),
                TrajectoryStation(md_m=td_m, tvd_m=td_m, inclination_deg=0.0),
            ],
            sections=[
                WellSection(
                    name=section_name,
                    md_top_m=0.0,
                    md_bottom_m=td_m,
                    tvd_top_m=0.0,
                    tvd_bottom_m=td_m,
                    hole_id_m=outer_id_m,
                    annular_section_type=annular_section_type,
                    casing_id_m=casing_id_m,
                )
            ],
        )


def calculate_tvd_vertical(md_m: float) -> float:
    """Return TVD for a vertical well, where TVD equals MD.

    Args:
        md_m: Measured depth in metres.

    Returns:
        True vertical depth in metres, equal to ``md_m``.

    Version 1 assumption:
        The wellpath is vertical. Survey interpolation for inclined wells
        is not implemented.
    """
    return require_nonnegative(md_m, "md_m")
