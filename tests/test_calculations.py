"""Unit tests for the pure drilling-engineering calculations."""

import math

import pytest

from app import calculations as calc


def test_hydrostatic_pressure_known_value():
    # 0.052 * 9.5 * 10000 = 4940 psi
    assert calc.hydrostatic_pressure(9.5, 10000) == pytest.approx(4940.0)


def test_hydrostatic_pressure_zero_depth():
    assert calc.hydrostatic_pressure(12.0, 0) == 0.0


def test_hydrostatic_pressure_invalid_mud_weight():
    with pytest.raises(ValueError):
        calc.hydrostatic_pressure(0, 10000)


def test_equivalent_circulating_density():
    # 9.5 + 250 / (0.052 * 10000) = 9.5 + 0.4808 = 9.9808
    assert calc.equivalent_circulating_density(9.5, 250, 10000) == pytest.approx(
        9.980769, abs=1e-5
    )


def test_ecd_no_circulation_equals_mud_weight():
    assert calc.equivalent_circulating_density(10.0, 0, 8000) == pytest.approx(10.0)


def test_buoyancy_factor():
    # (65.5 - 12) / 65.5 = 0.816793...
    assert calc.buoyancy_factor(12.0) == pytest.approx(0.8167938, abs=1e-6)


def test_buoyancy_factor_rejects_heavy_mud():
    with pytest.raises(ValueError):
        calc.buoyancy_factor(70.0)


def test_annular_velocity_known_value():
    # 24.51 * 500 / (8.5^2 - 5^2) = 12255 / 47.25 = 259.36...
    assert calc.annular_velocity(500, 8.5, 5.0) == pytest.approx(259.365, abs=1e-3)


def test_annular_velocity_requires_hole_bigger_than_pipe():
    with pytest.raises(ValueError):
        calc.annular_velocity(500, 5.0, 8.5)


def test_dogleg_severity_straight_hole_is_zero():
    # Identical stations => no curvature.
    assert calc.dogleg_severity(15, 20, 15, 20, 100) == pytest.approx(0.0, abs=1e-9)


def test_dogleg_severity_pure_inclination_change():
    # Same azimuth: dogleg angle equals inclination change (10 deg over 100 ft).
    dls = calc.dogleg_severity(10, 30, 20, 30, 100)
    assert dls == pytest.approx(10.0, abs=1e-6)


def test_dogleg_severity_normalizes_course_length():
    # 10 deg change over 50 ft => 20 deg / 100 ft.
    dls = calc.dogleg_severity(10, 0, 20, 0, 50)
    assert dls == pytest.approx(20.0, abs=1e-6)


def test_kill_mud_weight():
    # 9.5 + 300 / (0.052 * 10000) = 9.5 + 0.5769 = 10.0769
    assert calc.kill_mud_weight(9.5, 300, 10000) == pytest.approx(
        10.076923, abs=1e-5
    )


def test_dogleg_matches_manual_minimum_curvature():
    # Cross-check the closed form against a direct computation.
    i1, a1, i2, a2 = 15, 20, 25, 45
    beta = math.acos(
        math.cos(math.radians(i2 - i1))
        - math.sin(math.radians(i1))
        * math.sin(math.radians(i2))
        * (1 - math.cos(math.radians(a2 - a1)))
    )
    expected = math.degrees(beta)  # course length 100 ft, normalization 100 ft
    assert calc.dogleg_severity(i1, a1, i2, a2, 100) == pytest.approx(expected)
