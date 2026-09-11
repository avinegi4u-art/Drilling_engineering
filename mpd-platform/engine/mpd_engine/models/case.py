"""Complete version 1 hydraulics input case.

Assembles well, drillstring, fluid, operating conditions, and pressure window
so cross-object geometry checks live in one place.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from mpd_engine.models.base import EngineModel
from mpd_engine.models.drillstring import Drillstring
from mpd_engine.models.fluids import FluidProperties
from mpd_engine.models.operating_conditions import OperatingConditions
from mpd_engine.models.pressure_window import PressureWindowCurve
from mpd_engine.models.well import Well
from mpd_engine.units.validation import require_hole_larger_than_pipe


class HydraulicsCase(EngineModel):
    """Inputs required to run a version 1 steady-state MPD hydraulics case."""

    well: Well
    drillstring: Drillstring
    fluid: FluidProperties
    operating: OperatingConditions
    pressure_window: PressureWindowCurve
    notes: str = Field(default="", description="Optional engineer notes. Not used in equations.")

    @model_validator(mode="after")
    def _pipe_fits_annulus(self) -> HydraulicsCase:
        max_pipe_od_m = self.drillstring.max_outer_diameter_m
        for section in self.well.sections:
            require_hole_larger_than_pipe(
                hole_id_m=section.annular_outer_diameter_m,
                pipe_od_m=max_pipe_od_m,
                hole_name=f"{section.name} annular outer diameter",
                pipe_name="drillstring maximum outer diameter",
            )
        return self
