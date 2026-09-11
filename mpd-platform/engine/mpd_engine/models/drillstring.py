"""Drillstring geometry: drillpipe, HWDP, and BHA.

Diameters and lengths are stored in metres (SI).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from mpd_engine.models.base import EngineModel
from mpd_engine.units.validation import FinitePositive


class DrillstringComponentType(StrEnum):
    """Major drillstring component families used in version 1."""

    DRILLPIPE = "drillpipe"
    HWDP = "hwdp"
    BHA = "bha"


class DrillstringSegment(EngineModel):
    """One constant-diameter interval of the drillstring.

    Segments should be ordered from surface toward the bit.
    """

    component_type: DrillstringComponentType
    length_m: FinitePositive = Field(description="Segment length, m.")
    outer_diameter_m: FinitePositive = Field(description="Pipe outer diameter, m.")
    inner_diameter_m: FinitePositive = Field(description="Pipe inner diameter, m.")
    description: str = Field(default="", description="Optional engineering description.")

    @model_validator(mode="after")
    def _id_less_than_od(self) -> DrillstringSegment:
        if self.inner_diameter_m >= self.outer_diameter_m:
            raise ValueError("inner_diameter_m must be smaller than outer_diameter_m.")
        return self


class Drillstring(EngineModel):
    """Complete drillstring assembled from surface to bit."""

    segments: list[DrillstringSegment] = Field(min_length=1)

    @property
    def total_length_m(self) -> float:
        """Sum of segment lengths, m."""
        return sum(segment.length_m for segment in self.segments)

    @property
    def max_outer_diameter_m(self) -> float:
        """Largest pipe outer diameter in the string, m."""
        return max(segment.outer_diameter_m for segment in self.segments)
