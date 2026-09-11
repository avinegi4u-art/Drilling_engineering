"""SI unit conversions for MPD hydraulics inputs and reports.

Engineering calculations in this package use SI internally:

- pressure: Pa
- density: kg/m³
- length: m
- volumetric flow: m³/s
- viscosity: Pa·s

Convert at the application boundary. Do not mix units inside equations.

Factors below are exact where a standard definition exists, or NIST/API
conventional factors otherwise. Round-trip tests live in ``tests/test_conversions.py``.
"""

from __future__ import annotations

from mpd_engine.units.validation import require_finite

# Standard acceleration of gravity used later for hydrostatic pressure.
STANDARD_GRAVITY_M_S2 = 9.80665

# Pressure
PA_PER_PSI = 6894.757293168  # NIST conventional conversion
PA_PER_KPA = 1_000.0
PA_PER_BAR = 100_000.0

# Density. 1 lbm / US gallon.
# 1 lbm = 0.45359237 kg (exact). 1 US gallon = 3.785411784e-3 m³ (exact).
KG_M3_PER_PPG = 0.45359237 / 0.003785411784

# Length
M_PER_FT = 0.3048  # exact
M_PER_MM = 0.001  # exact

# Flow. 1 oil barrel = 42 US gallons (exact) = 0.158987294928 m³.
M3_PER_OIL_BBL = 42.0 * 0.003785411784
M3_S_PER_L_MIN = 1.0 / 60_000.0
M3_S_PER_BBL_MIN = M3_PER_OIL_BBL / 60.0

# Viscosity
PA_S_PER_CP = 0.001  # exact: 1 cP = 1 mPa·s


def _as_finite(value: float, name: str) -> float:
    return require_finite(value, name)


def psi_to_pa(value: float) -> float:
    """Convert pound-force per square inch to pascal."""
    return _as_finite(value, "psi") * PA_PER_PSI


def pa_to_psi(value: float) -> float:
    """Convert pascal to pound-force per square inch."""
    return _as_finite(value, "Pa") / PA_PER_PSI


def kpa_to_pa(value: float) -> float:
    """Convert kilopascal to pascal."""
    return _as_finite(value, "kPa") * PA_PER_KPA


def pa_to_kpa(value: float) -> float:
    """Convert pascal to kilopascal."""
    return _as_finite(value, "Pa") / PA_PER_KPA


def bar_to_pa(value: float) -> float:
    """Convert bar to pascal."""
    return _as_finite(value, "bar") * PA_PER_BAR


def pa_to_bar(value: float) -> float:
    """Convert pascal to bar."""
    return _as_finite(value, "Pa") / PA_PER_BAR


def ppg_to_kg_m3(value: float) -> float:
    """Convert pounds per US gallon (lbm/gal) to kg/m³."""
    return _as_finite(value, "ppg") * KG_M3_PER_PPG


def kg_m3_to_ppg(value: float) -> float:
    """Convert kg/m³ to pounds per US gallon (lbm/gal)."""
    return _as_finite(value, "kg/m³") / KG_M3_PER_PPG


def ft_to_m(value: float) -> float:
    """Convert international feet to metres."""
    return _as_finite(value, "ft") * M_PER_FT


def m_to_ft(value: float) -> float:
    """Convert metres to international feet."""
    return _as_finite(value, "m") / M_PER_FT


def mm_to_m(value: float) -> float:
    """Convert millimetres to metres."""
    return _as_finite(value, "mm") * M_PER_MM


def m_to_mm(value: float) -> float:
    """Convert metres to millimetres."""
    return _as_finite(value, "m") / M_PER_MM


def l_min_to_m3_s(value: float) -> float:
    """Convert litres per minute to cubic metres per second."""
    return _as_finite(value, "L/min") * M3_S_PER_L_MIN


def m3_s_to_l_min(value: float) -> float:
    """Convert cubic metres per second to litres per minute."""
    return _as_finite(value, "m³/s") / M3_S_PER_L_MIN


def bbl_min_to_m3_s(value: float) -> float:
    """Convert oil barrels per minute to cubic metres per second."""
    return _as_finite(value, "bbl/min") * M3_S_PER_BBL_MIN


def m3_s_to_bbl_min(value: float) -> float:
    """Convert cubic metres per second to oil barrels per minute."""
    return _as_finite(value, "m³/s") / M3_S_PER_BBL_MIN


def cp_to_pa_s(value: float) -> float:
    """Convert centipoise to pascal-seconds."""
    return _as_finite(value, "cP") * PA_S_PER_CP


def pa_s_to_cp(value: float) -> float:
    """Convert pascal-seconds to centipoise."""
    return _as_finite(value, "Pa·s") / PA_S_PER_CP
