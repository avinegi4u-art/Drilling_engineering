"""Hand-calculated hydraulics benchmarks for version 1.

Geometry and hydrostatic checks use textbook identities. Annular friction
uses the documented narrow-slot Bingham approximation in
``mpd_engine.hydraulics.friction`` — that correlation is an engineering
approximation, not a validated field model.
"""

from __future__ import annotations

import math

import pytest

from mpd_engine.constants import STANDARD_GRAVITY_M_S2
from mpd_engine.hydraulics.ecd import (
    calculate_bottomhole_pressure,
    calculate_ecd_kg_m3,
    calculate_required_surface_backpressure,
)
from mpd_engine.hydraulics.friction import calculate_bingham_annular_pressure_loss
from mpd_engine.hydraulics.geometry import (
    calculate_annular_area,
    calculate_annular_velocity,
    calculate_hydraulic_diameter,
)
from mpd_engine.hydraulics.hydrostatic import calculate_hydrostatic_pressure
from mpd_engine.units.conversions import inch_to_m, lpm_to_m3_s

HOLE_ID_M = inch_to_m(12.25)
PIPE_OD_M = inch_to_m(5.0)
DENSITY = 1200.0
MU_P = 0.02
TAU_Y = 9.576
LENGTH = 3000.0
TVD = 3000.0


def _slot_gradient(velocity: float, hole: float, pipe: float) -> float:
    """Independent expansion of the documented slot formula."""
    gap = (hole - pipe) / 2.0
    return 12.0 * MU_P * velocity / gap**2 + 3.0 * TAU_Y / gap


def test_annular_area_hand_calculated() -> None:
    expected = math.pi / 4.0 * (HOLE_ID_M**2 - PIPE_OD_M**2)
    assert calculate_annular_area(HOLE_ID_M, PIPE_OD_M) == pytest.approx(expected, rel=1e-12)
    assert calculate_annular_area(HOLE_ID_M, PIPE_OD_M) == pytest.approx(
        0.0633701041046308, rel=1e-12
    )


def test_hydraulic_diameter_hand_calculated() -> None:
    assert calculate_hydraulic_diameter(HOLE_ID_M, PIPE_OD_M) == pytest.approx(
        HOLE_ID_M - PIPE_OD_M, rel=0, abs=0.0
    )
    assert calculate_hydraulic_diameter(HOLE_ID_M, PIPE_OD_M) == pytest.approx(0.18415, rel=1e-12)


def test_hydrostatic_pressure_hand_calculated() -> None:
    expected = 1200.0 * 9.80665 * 3000.0
    assert expected == 35_303_940.0
    assert calculate_hydrostatic_pressure(DENSITY, TVD) == pytest.approx(expected, rel=0, abs=0.0)
    assert calculate_hydrostatic_pressure(DENSITY, 0.0) == 0.0


def test_annular_velocity_hand_calculated() -> None:
    area = calculate_annular_area(HOLE_ID_M, PIPE_OD_M)
    flow = lpm_to_m3_s(400.0)
    expected = flow / area
    assert calculate_annular_velocity(flow, area) == pytest.approx(expected, rel=1e-12)


def test_zero_flow_friction_is_zero() -> None:
    loss = calculate_bingham_annular_pressure_loss(
        DENSITY, MU_P, TAU_Y, 0.0, LENGTH, HOLE_ID_M, PIPE_OD_M
    )
    assert loss == 0.0


def test_higher_flow_gives_higher_friction() -> None:
    low = calculate_bingham_annular_pressure_loss(
        DENSITY, MU_P, TAU_Y, lpm_to_m3_s(400.0), LENGTH, HOLE_ID_M, PIPE_OD_M
    )
    high = calculate_bingham_annular_pressure_loss(
        DENSITY, MU_P, TAU_Y, lpm_to_m3_s(800.0), LENGTH, HOLE_ID_M, PIPE_OD_M
    )
    assert high > low


def test_smaller_annular_clearance_gives_higher_friction() -> None:
    wide = calculate_bingham_annular_pressure_loss(
        DENSITY, MU_P, TAU_Y, lpm_to_m3_s(400.0), LENGTH, HOLE_ID_M, PIPE_OD_M
    )
    tight = calculate_bingham_annular_pressure_loss(
        DENSITY, MU_P, TAU_Y, lpm_to_m3_s(400.0), LENGTH, HOLE_ID_M, inch_to_m(8.0)
    )
    assert tight > wide


def test_bingham_slot_friction_matches_independent_expansion() -> None:
    flow = lpm_to_m3_s(400.0)
    area = math.pi / 4.0 * (HOLE_ID_M**2 - PIPE_OD_M**2)
    velocity = flow / area
    expected = _slot_gradient(velocity, HOLE_ID_M, PIPE_OD_M) * LENGTH
    actual = calculate_bingham_annular_pressure_loss(
        DENSITY, MU_P, TAU_Y, flow, LENGTH, HOLE_ID_M, PIPE_OD_M
    )
    assert actual == pytest.approx(expected, rel=1e-12)
    assert actual == pytest.approx(944_954.1132315258, rel=1e-9)


def test_bottomhole_pressure_is_sum_of_components() -> None:
    hydro = 35_303_940.0
    friction = 944_954.1132315258
    sbp = 1_500_000.0
    assert calculate_bottomhole_pressure(hydro, friction, sbp) == pytest.approx(
        hydro + friction + sbp, rel=0, abs=1e-6
    )


def test_ecd_hand_calculated() -> None:
    bhp = 36_284_632.36903571
    expected = bhp / (STANDARD_GRAVITY_M_S2 * TVD)
    assert calculate_ecd_kg_m3(bhp, TVD) == pytest.approx(expected, rel=1e-12)
    with pytest.raises(ValueError, match="greater than zero"):
        calculate_ecd_kg_m3(bhp, 0.0)


def test_required_surface_backpressure() -> None:
    hydro = 35_303_940.0
    friction = 944_954.1132315258
    target = hydro + friction + 1_500_000.0
    assert calculate_required_surface_backpressure(target, hydro, friction) == pytest.approx(
        1_500_000.0, rel=1e-12
    )
    assert calculate_required_surface_backpressure(hydro, hydro, friction) == pytest.approx(
        -friction, rel=1e-12
    )


def test_invalid_geometry_rejected_by_hydraulics() -> None:
    with pytest.raises(ValueError, match="must be greater than pipe_od_m"):
        calculate_annular_area(0.10, 0.127)
    with pytest.raises(ValueError, match="must be greater than pipe_od_m"):
        calculate_bingham_annular_pressure_loss(
            DENSITY, MU_P, TAU_Y, lpm_to_m3_s(400.0), LENGTH, 0.10, 0.127
        )


def test_negative_inputs_rejected() -> None:
    with pytest.raises(ValueError):
        calculate_hydrostatic_pressure(-1200.0, 1000.0)
    with pytest.raises(ValueError):
        calculate_annular_velocity(-0.01, 0.05)
