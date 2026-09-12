"""Structured API error envelope."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(description="Stable machine-readable error code.")
    message: Any = Field(description="Human-readable explanation or validation details.")


class ErrorResponse(BaseModel):
    """Body returned by every non-success JSON response."""

    model_config = ConfigDict(extra="forbid")

    error: ErrorDetail
