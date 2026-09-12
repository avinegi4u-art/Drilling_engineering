"""Scenario request and response schemas."""

from __future__ import annotations

from datetime import datetime

from mpd_engine.models.drillstring import Drillstring
from mpd_engine.models.fluids import FluidProperties
from mpd_engine.models.operating_conditions import OperatingConditions
from mpd_engine.models.pressure_window import PressureWindow
from pydantic import BaseModel, ConfigDict, Field


class ScenarioCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, examples=["drilling-400-lpm"])
    created_by: str = Field(default="engineer")
    drillstring: Drillstring
    fluid: FluidProperties
    operating: OperatingConditions
    pressure_window: PressureWindow
    target_bottomhole_pressure_pa: float | None = None
    depth_step_m: float = 50.0


class ScenarioRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    well_id: str
    name: str
    created_by: str
    created_at: datetime | None = None
    inputs: dict
