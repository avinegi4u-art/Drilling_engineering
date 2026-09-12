"""Engineering-review warning records.

Warnings describe limit violations and model caveats. They are not
operational commands and must not be presented as choke setpoints.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from mpd_engine.units.validation import FiniteFloat, NonNegativeFloat


class WarningSeverity(StrEnum):
    """Relative importance for engineering review."""

    INFO = "info"
    REVIEW = "review"
    HIGH = "high"


class EngineeringWarning(BaseModel):
    """One review notice produced by a calculation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(min_length=1)
    severity: WarningSeverity
    depth_m: NonNegativeFloat | None = None
    actual_pressure_pa: FiniteFloat | None = None
    limit_pressure_pa: FiniteFloat | None = None
    explanation: str = Field(min_length=1)
    recommended_engineering_review: str = Field(min_length=1)
