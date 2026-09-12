"""Drillstring component models.

Diameters are stored in metres. Convert millimetres or inches at the
application boundary. Version 1 typically uses a single drillpipe
interval; HWDP and BHA segments can be appended without changing SI
field names.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mpd_engine.units.validation import (
    PositiveFloat,
    validate_monotonically_increasing,
    validate_pipe_wall,
)


class DrillstringComponentType(StrEnum):
    """Mechanical role of a drillstring interval."""

    DRILLPIPE = "drillpipe"
    HWDP = "hwdp"
    BHA = "bha"


class DrillstringComponent(BaseModel):
    """One constant-diameter drillstring interval."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    component_type: DrillstringComponentType
    od_m: PositiveFloat = Field(description="Outer diameter, m.")
    id_m: PositiveFloat = Field(description="Inner diameter, m.")
    length_m: PositiveFloat = Field(description="Along-hole length, m.")

    @model_validator(mode="after")
    def check_wall(self) -> DrillstringComponent:
        validate_pipe_wall(self.od_m, self.id_m, name=self.component_type.value)
        return self


class Drillstring(BaseModel):
    """Ordered drillstring from surface toward the bit.

    Components are stored top-down. Version 1 may contain a single
    drillpipe component whose length equals well TD.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    components: list[DrillstringComponent] = Field(min_length=1)

    @model_validator(mode="after")
    def check_components(self) -> Drillstring:
        lengths = [component.length_m for component in self.components]
        validate_monotonically_increasing(
            [sum(lengths[: index + 1]) for index in range(len(lengths))],
            name="drillstring.cumulative_length_m",
            strict=True,
        )
        return self

    @property
    def total_length_m(self) -> float:
        """Sum of component along-hole lengths, m."""
        return sum(component.length_m for component in self.components)

    @classmethod
    def uniform_drillpipe(
        cls,
        *,
        od_m: float,
        id_m: float,
        length_m: float,
        name: str = "drillpipe",
    ) -> Drillstring:
        """Build a single-pipe string used by version-1 hydraulics cases."""
        return cls(
            components=[
                DrillstringComponent(
                    name=name,
                    component_type=DrillstringComponentType.DRILLPIPE,
                    od_m=od_m,
                    id_m=id_m,
                    length_m=length_m,
                )
            ]
        )
