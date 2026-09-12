"""Hand-checked unit conversion tests.

Benchmarks use the conversion factors documented in
``mpd_engine.units.conversions``. Round-trip tests confirm that converting
to SI and back recovers the original value within floating-point tolerance.
"""

from __future__ import annotations

import math

import pytest

from mpd_engine.units.conversions import (
    BBL_TO_M3,
    FT_TO_M,
    PPG_TO_KG_M3,
    PSI_TO_PA,
    bar_to_pa,
    bbl_min_to_m3_s,
    cp_to_pa_s,
    ft_to_m,
    inch_to_m,
    kg_m3_to_ppg,
    kpa_to_pa,
    lpm_to_m3_s,
    m_to_ft,
    m_to_inch,
    m_to_mm,
    m3_s_to_bbl_min,
    m3_s_to_lpm,
    mm_to_m,
    pa_s_to_cp,
    pa_to_bar,
    pa_to_kpa,
    pa_to_psi,
    ppg_to_kg_m3,
    psi_to_pa,
)


def test_psi_to_pa_hand_calculated() -> None:
    """2500 psi * 6894.757293168 Pa/psi = 17_236_893.23292 Pa."""
    expected = 2500.0 * PSI_TO_PA
    assert psi_to_pa(2500.0) == pytest.approx(expected, rel=0, abs=1e-9)
    assert psi_to_pa(2500.0) == pytest.approx(17_236_893.23292, rel=1e-12)


def test_freshwater_ppg_to_si_hand_calculated() -> None:
    """8.345404452 ppg * 119.826427316 kg/m³/ppg ≈ 1000 kg/m³."""
    freshwater_ppg = 1000.0 / PPG_TO_KG_M3
    assert ppg_to_kg_m3(freshwater_ppg) == pytest.approx(1000.0, rel=1e-12)
    assert ppg_to_kg_m3(12.0) == pytest.approx(12.0 * PPG_TO_KG_M3, rel=1e-12)


def test_flow_lpm_hand_calculated() -> None:
    """800 L/min = 800 / 60_000 m³/s = 0.0133... m³/s."""
    assert lpm_to_m3_s(800.0) == pytest.approx(800.0 / 60_000.0, rel=0, abs=1e-15)


def test_flow_bbl_min_hand_calculated() -> None:
    """1 bbl/min = 0.158987294928 / 60 m³/s."""
    assert bbl_min_to_m3_s(1.0) == pytest.approx(BBL_TO_M3 / 60.0, rel=1e-12)


def test_length_ft_is_exact_international_foot() -> None:
    """3000 ft * 0.3048 m/ft = 914.4 m (exact)."""
    assert ft_to_m(3000.0) == pytest.approx(914.4, rel=0, abs=0.0)
    assert FT_TO_M == 0.3048


def test_mm_and_inch_pipe_sizes() -> None:
    assert mm_to_m(244.5) == pytest.approx(0.2445, rel=0, abs=1e-15)
    assert inch_to_m(12.25) == pytest.approx(0.31115, rel=1e-12)


def test_pressure_kpa_and_bar() -> None:
    assert kpa_to_pa(2500.0) == pytest.approx(2_500_000.0)
    assert bar_to_pa(1.0) == pytest.approx(100_000.0)
    assert pa_to_bar(bar_to_pa(3.5)) == pytest.approx(3.5, rel=1e-12)


def test_viscosity_centipoise() -> None:
    """20 cP = 0.020 Pa·s."""
    assert cp_to_pa_s(20.0) == pytest.approx(0.02)


@pytest.mark.parametrize(
    ("forward", "reverse", "value"),
    [
        (psi_to_pa, pa_to_psi, 14.503773773),
        (kpa_to_pa, pa_to_kpa, 3450.0),
        (bar_to_pa, pa_to_bar, 0.6894757293168),
        (ppg_to_kg_m3, kg_m3_to_ppg, 12.5),
        (ft_to_m, m_to_ft, 9842.519685039),
        (mm_to_m, m_to_mm, 215.9),
        (inch_to_m, m_to_inch, 5.0),
        (lpm_to_m3_s, m3_s_to_lpm, 2000.0),
        (bbl_min_to_m3_s, m3_s_to_bbl_min, 12.6),
        (cp_to_pa_s, pa_s_to_cp, 25.0),
    ],
)
def test_conversion_round_trip(forward, reverse, value) -> None:  # type: ignore[no-untyped-def]
    si = forward(value)
    restored = reverse(si)
    assert restored == pytest.approx(value, rel=1e-12)


def test_nan_and_inf_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        psi_to_pa(math.nan)
    with pytest.raises(ValueError, match="finite"):
        lpm_to_m3_s(math.inf)
    with pytest.raises(ValueError, match="finite"):
        ppg_to_kg_m3(-math.inf)
