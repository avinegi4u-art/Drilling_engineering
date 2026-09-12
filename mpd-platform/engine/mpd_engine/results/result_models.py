"""Typed calculation outputs.

Pandas DataFrames are not used here. Convert at the export or
visualization boundary.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from mpd_engine.mpd.connections import ConnectionComparison
from mpd_engine.mpd.pressure_window import PressureWindowStatus
from mpd_engine.results.warnings import EngineeringWarning
from mpd_engine.units.validation import FiniteFloat, NonNegativeFloat


class DepthPointResult(BaseModel):
    """Hydraulics and window status at one depth."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    md_m: NonNegativeFloat
    tvd_m: NonNegativeFloat
    hydrostatic_pressure_pa: NonNegativeFloat
    annular_friction_to_surface_pa: NonNegativeFloat
    surface_backpressure_pa: NonNegativeFloat
    annular_pressure_pa: NonNegativeFloat
    ecd_kg_m3: FiniteFloat | None = Field(
        default=None,
        description="ECD is undefined at TVD = 0 and is left as None.",
    )
    pore_pressure_pa: FiniteFloat | None = None
    collapse_pressure_pa: FiniteFloat | None = None
    fracture_pressure_pa: FiniteFloat | None = None
    window_status: PressureWindowStatus


class CalculationSummary(BaseModel):
    """TD / bottomhole headline numbers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tvd_m: NonNegativeFloat
    hydrostatic_pressure_pa: NonNegativeFloat
    annular_friction_pressure_pa: NonNegativeFloat
    surface_backpressure_pa: NonNegativeFloat
    bottomhole_pressure_pa: NonNegativeFloat
    ecd_kg_m3: FiniteFloat | None
    required_surface_backpressure_pa: float | None
    window_status: PressureWindowStatus
    operating_mode: str
    flow_rate_m3_s: NonNegativeFloat


class CalculationResult(BaseModel):
    """Complete version-1 hydraulics result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    calculation_version: str
    timestamp_utc: datetime
    assumptions: tuple[str, ...]
    summary: CalculationSummary
    profile: list[DepthPointResult] = Field(min_length=1)
    warnings: list[EngineeringWarning]
    connection: ConnectionComparison | None = None

    @classmethod
    def utc_now(cls) -> datetime:
        return datetime.now(UTC)
