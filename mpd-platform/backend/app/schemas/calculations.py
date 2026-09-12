"""Calculation request and response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CalculateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    created_by: str = Field(default="engineer")


class RunRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    scenario_id: str
    status: str
    calculation_version: str
    created_by: str
    created_at: datetime | None = None
    error_message: str | None = None
    assumptions: list[str]


class ResultRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: str
    calculation_version: str
    assumptions: list[str]
    summary: dict[str, Any]
    profile: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    connection: dict[str, Any] | None = None
