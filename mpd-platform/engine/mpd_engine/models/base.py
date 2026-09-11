"""Shared immutable Pydantic base for engine domain models."""

from pydantic import BaseModel, ConfigDict


class EngineModel(BaseModel):
    """Immutable, strict domain model. Extra fields are rejected."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )
