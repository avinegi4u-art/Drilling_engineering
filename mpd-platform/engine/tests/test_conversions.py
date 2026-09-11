"""Round-trip and known-value tests for SI unit conversions."""

from __future__ import annotations

import math

import pytest

from mpd_engine.units.conversions import (
    KG_M3_PER_PPG,
    M3_PER_OIL_BBL,
    PA_PER_PSI,
    STANDARD_GRAVITY_M_S2,
    bar_to_pa,
    bbl_min_to_m3_s,
    cp_to_pa_s,
    ft_to_m,
    kg_m3_to_ppg,
    kpa_to_pa,
    l_min_to_m3_s,
    m3_s_to_bbl_min,
    m3_s_to_l_min,
    m_to_ft,
    m_to_mm,
    mm_to_m,
    pa_s_to_cp,
    pa_to_bar,
    pa_to_kpa,
    pa_to_psi,
    ppg_to_kg_m3,
    psi_to_pa,
)

ROUND_TRIP_VALUES = (0.0, 1.0, 12.3456789, 1.0e-6, 1.0e6)


@pytest.mark.parametrize("value", ROUND_TRIP_VALUES)
def test_pressure_round_trips(value: float) -> None:
    assert pa_to_psi(psi_to_pa(value)) == pytest.approx(value, rel=1e-12, abs=1e-12)
    assert pa_to_kpa(kpa_to_pa(value)) == pytest.approx(value, rel=1e-12, abs=1e-12)
    assert pa_to_bar(bar_to_pa(value)) == pytest.approx(value, rel=1e-12, abs=1e-12)


@pytest.mark.parametrize("value", ROUND_TRIP_VALUES)
def test_density_length_flow_viscosity_round_trips(value: float) -> None:
    assert kg_m3_to_ppg(ppg_to_kg_m3(value)) == pytest.approx(value, rel=1e-12, abs=1e-12)
    assert m_to_ft(ft_to_m(value)) == pytest.approx(value, rel=1e-12, abs=1e-12)
    assert m_to_mm(mm_to_m(value)) == pytest.approx(value, rel=1e-12, abs=1e-12)
    assert m3_s_to_l_min(l_min_to_m3_s(value)) == pytest.approx(value, rel=1e-12, abs=1e-12)
    assert m3_s_to_bbl_min(bbl_min_to_m3_s(value)) == pytest.approx(value, rel=1e-12, abs=1e-12)
    assert pa_s_to_cp(cp_to_pa_s(value)) == pytest.approx(value, rel=1e-12, abs=1e-12)


def test_known_conversion_values() -> None:
    assert ft_to_m(1.0) == 0.3048
    assert mm_to_m(215.9) == pytest.approx(0.2159)
    assert kpa_to_pa(1.0) == 1000.0
    assert bar_to_pa(1.0) == 100_000.0
    assert psi_to_pa(1.0) == pytest.approx(PA_PER_PSI)
    assert cp_to_pa_s(20.0) == pytest.approx(0.020)
    assert l_min_to_m3_s(1200.0) == pytest.approx(0.02)
    assert ppg_to_kg_m3(1.0) == pytest.approx(KG_M3_PER_PPG)
    # Freshwater is approximately 8.345 ppg with the US-gallon definition.
    assert ppg_to_kg_m3(8.345404452) == pytest.approx(1000.0, rel=1e-6)
    assert M3_PER_OIL_BBL == pytest.approx(0.158987294928)
    assert STANDARD_GRAVITY_M_S2 == 9.80665


def test_negative_deltas_are_allowed_in_conversions() -> None:
    assert psi_to_pa(-10.0) == pytest.approx(-10.0 * PA_PER_PSI)


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_non_finite_conversion_inputs_are_rejected(bad: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        psi_to_pa(bad)
    with pytest.raises(ValueError, match="finite"):
        ppg_to_kg_m3(bad)
    with pytest.raises(ValueError, match="finite"):
        l_min_to_m3_s(bad)
