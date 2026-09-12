"""Well request and response schemas."""

from __future__ import annotations

from datetime import datetime

from mpd_engine.models.well import AnnularSectionType, TrajectoryStation, WellSection
from pydantic import BaseModel, ConfigDict, Field


class WellCreate(BaseModel):
    """Create a vertical well, or supply a full trajectory and section list.

    Lengths are metres. Convert millimetres or feet before calling the API.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        examples=["EXAMPLE-1"],
        description="Engineer-facing well name.",
    )
    created_by: str = Field(default="engineer", description="Audit label. Version 1 has no auth.")
    td_m: float | None = Field(default=None, description="Total depth for a vertical well, m.")
    hole_id_m: float | None = Field(
        default=None, description="Open-hole or casing inner diameter, m."
    )
    annular_section_type: AnnularSectionType = Field(
        default=AnnularSectionType.OPEN_HOLE,
        description="Outer wall of the annulus.",
    )
    casing_id_m: float | None = Field(
        default=None, description="Required when annular_section_type is casing, m."
    )
    trajectory: list[TrajectoryStation] | None = Field(
        default=None, description="Survey or planned wellpath. TVD equals MD for vertical wells."
    )
    sections: list[WellSection] | None = Field(
        default=None, description="Constant-diameter wellbore intervals."
    )


class WellRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    created_by: str
    created_at: datetime | None = None
    well: dict = Field(description="Persisted engine Well payload in SI units.")
