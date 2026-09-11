"""Drilling-fluid properties.

Internal units:

- Density: kg/m³
- Plastic viscosity: Pa·s (not cP)
- Yield stress: Pa
- Temperature: °C (stored for later thermal models; unused in version 1)

Convert display units at the application boundary. Version 1 supports Bingham
Plastic rheology only.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from mpd_engine.models.base import EngineModel
from mpd_engine.units.validation import FiniteNonNegative, require_finite


class RheologyModel(StrEnum):
    """Rheology models. Only Bingham Plastic is implemented in version 1."""

    BINGHAM_PLASTIC = "bingham_plastic"
    NEWTONIAN = "newtonian"
    POWER_LAW = "power_law"
    HERSCHEL_BULKLEY = "herschel_bulkley"


_IMPLEMENTED_RHEOLOGY = frozenset({RheologyModel.BINGHAM_PLASTIC})


class FluidProperties(EngineModel):
    """Incompressible single-phase mud properties for version 1."""

    mud_density_kg_m3: FiniteNonNegative = Field(
        description="Mud density, kg/m³. Must be nonnegative."
    )
    plastic_viscosity_pa_s: FiniteNonNegative = Field(
        description="Bingham plastic viscosity, Pa·s. 1 cP = 0.001 Pa·s."
    )
    yield_stress_pa: FiniteNonNegative = Field(
        description="Bingham yield stress (yield point), Pa."
    )
    temperature_c: float | None = Field(
        default=None,
        description="Fluid temperature, °C. Stored for later use; unused in version 1.",
    )
    rheology_model: RheologyModel = Field(
        default=RheologyModel.BINGHAM_PLASTIC,
        description="Rheology model. Version 1 requires bingham_plastic.",
    )

    @model_validator(mode="after")
    def _supported_rheology_and_temperature(self) -> FluidProperties:
        if self.rheology_model not in _IMPLEMENTED_RHEOLOGY:
            raise ValueError(
                f"Rheology model {self.rheology_model!s} is not implemented in version 1. "
                "Use bingham_plastic."
            )
        if self.temperature_c is not None:
            require_finite(self.temperature_c, "temperature_c")
            if not (-20.0 <= self.temperature_c <= 300.0):
                raise ValueError("temperature_c must be between -20 and 300 °C when provided.")
        return self
