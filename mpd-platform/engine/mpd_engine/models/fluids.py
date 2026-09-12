"""Drilling-fluid property models.

Density is stored in kg/m³. Bingham Plastic parameters are stored in
SI: plastic viscosity in Pa·s and yield stress in Pa. Convert
centipoise at the application boundary.

Temperature is stored for later thermal models. Version 1 does not
apply temperature corrections to density or rheology.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mpd_engine.units.validation import (
    MAX_MUD_DENSITY_KG_M3,
    MAX_TEMPERATURE_C,
    MIN_MUD_DENSITY_KG_M3,
    MIN_TEMPERATURE_C,
    FiniteFloat,
    NonNegativeFloat,
    PositiveFloat,
)


class RheologyModel(StrEnum):
    """Supported rheology models.

    Version 1 implements Bingham Plastic only. Additional models can be
    added without changing existing field names.
    """

    BINGHAM_PLASTIC = "bingham_plastic"


class FluidProperties(BaseModel):
    """Mud properties for a single fluid program.

    Version 1 assumptions:
    - Constant mud density (no compressibility or cuttings loading).
    - Bingham Plastic rheology.
    - Incompressible single-phase fluid.
    - Temperature is recorded but not used in hydraulics yet.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    mud_density_kg_m3: PositiveFloat = Field(description="Mud density, kg/m³.")
    plastic_viscosity_pa_s: NonNegativeFloat = Field(
        description="Bingham plastic viscosity, Pa·s (not centipoise)."
    )
    yield_stress_pa: NonNegativeFloat = Field(
        description="Bingham yield stress (yield point), Pa."
    )
    temperature_c: FiniteFloat = Field(description="Reference mud temperature, °C.")
    rheology_model: RheologyModel = RheologyModel.BINGHAM_PLASTIC

    @model_validator(mode="after")
    def check_fluid(self) -> FluidProperties:
        if self.mud_density_kg_m3 < MIN_MUD_DENSITY_KG_M3:
            raise ValueError(
                f"mud_density_kg_m3 ({self.mud_density_kg_m3}) is below the "
                f"version-1 minimum of {MIN_MUD_DENSITY_KG_M3} kg/m³"
            )
        if self.mud_density_kg_m3 > MAX_MUD_DENSITY_KG_M3:
            raise ValueError(
                f"mud_density_kg_m3 ({self.mud_density_kg_m3}) exceeds the "
                f"version-1 maximum of {MAX_MUD_DENSITY_KG_M3} kg/m³"
            )
        if self.temperature_c < MIN_TEMPERATURE_C or self.temperature_c > MAX_TEMPERATURE_C:
            raise ValueError(
                f"temperature_c ({self.temperature_c}) is outside the version-1 "
                f"range [{MIN_TEMPERATURE_C}, {MAX_TEMPERATURE_C}] °C"
            )
        if self.rheology_model is not RheologyModel.BINGHAM_PLASTIC:
            raise ValueError(
                f"Unsupported rheology_model {self.rheology_model!r}. "
                "Version 1 supports Bingham Plastic only."
            )
        return self
