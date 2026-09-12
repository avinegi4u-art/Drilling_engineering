"""Well request and response schemas."""

from __future__ import annotations

from datetime import datetime

from mpd_engine.models.well import AnnularSectionType, TrajectoryStation, WellSection
from pydantic import BaseModel, ConfigDict, Field


class WellCreate(BaseModel):
    """Create a vertical well, or supply a full trajectory and section list."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, examples=["EXAMPLE-1"])
    created_by: str = Field(default="engineer")
    td_m: float | None = Field(default=None, description="TD for a vertical well, m.")
    hole_id_m: float | None = Field(default=None, description="Open-hole or casing ID, m.")
    annular_section_type: AnnularSectionType = AnnularSectionType.OPEN_HOLE
    casing_id_m: float | None = None
    trajectory: list[TrajectoryStation] | None = None
    sections: list[WellSection] | None = None


class WellRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    created_by: str
    created_at: datetime | None = None
    well: dict
