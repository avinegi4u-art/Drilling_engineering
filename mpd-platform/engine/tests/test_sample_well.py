"""Phase 1 tests load the example well file as documentation, not as field data."""

from __future__ import annotations

import json
from pathlib import Path

from mpd_engine.models.drillstring import Drillstring
from mpd_engine.models.fluids import FluidProperties
from mpd_engine.models.operating_conditions import OperatingConditions, OperatingMode
from mpd_engine.models.pressure_window import PressureWindow, PressureWindowPoint
from mpd_engine.models.well import Well
from mpd_engine.units.conversions import inch_to_m

SAMPLE_PATH = Path(__file__).resolve().parents[2] / "examples" / "sample_well.json"


def test_sample_well_json_loads_into_domain_models() -> None:
    payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    well = Well.vertical(
        name=payload["well"]["name"],
        td_m=payload["well"]["td_m"],
        hole_id_m=payload["well"]["hole_id_m"],
    )
    drillstring = Drillstring.uniform_drillpipe(
        od_m=payload["drillstring"]["od_m"],
        id_m=payload["drillstring"]["id_m"],
        length_m=payload["drillstring"]["length_m"],
    )
    fluid = FluidProperties(**payload["fluid"])
    drilling = OperatingConditions(**payload["operating_conditions"]["drilling"])
    window = PressureWindow(
        points=[PressureWindowPoint(**point) for point in payload["pressure_window"]]
    )

    assert well.name == "EXAMPLE-1"
    assert well.sections[0].hole_id_m == inch_to_m(12.25)
    assert drillstring.total_length_m == 3000.0
    assert fluid.mud_density_kg_m3 == 1200.0
    assert drilling.operating_mode is OperatingMode.DRILLING
    assert len(window.points) == 3
