"""Unit conversions between common oilfield units and SI.

Internal calculation units
--------------------------
- length: metre (m)
- pressure: pascal (Pa)
- density: kilogram per cubic metre (kg/m³)
- volumetric flow: cubic metre per second (m³/s)
- dynamic viscosity: pascal-second (Pa·s)

Never mix units inside an engineering equation. Convert at the
application boundary, then call engine functions with SI values.

Factors below are exact definitions or NIST-traceable conversions.
They are isolated here so hydraulics code does not embed magic numbers.
"""

from __future__ import annotations

from mpd_engine.units.validation import require_finite

# ---------------------------------------------------------------------------
# Conversion factors (multiply source unit by the factor to obtain SI)
# ---------------------------------------------------------------------------

# Pressure. 1 lbf/in² (psi) using standard gravity and the avoirdupois pound.
PSI_TO_PA = 6_894.757_293_168
KPA_TO_PA = 1_000.0
BAR_TO_PA = 100_000.0

# Density. 1 pound per US gallon (ppg).
PPG_TO_KG_M3 = 119.826_427_316

# Length. The international foot is defined as exactly 0.3048 m.
FT_TO_M = 0.3048
IN_TO_M = 0.0254
MM_TO_M = 0.001

# Volume / flow. 1 oil barrel = 42 US gallons = 0.158987294928 m³.
BBL_TO_M3 = 0.158_987_294_928
L_TO_M3 = 0.001

# Viscosity. 1 centipoise = 0.001 Pa·s.
CP_TO_PA_S = 0.001


def _as_finite(value: float, name: str) -> float:
    return require_finite(value, name)


# ---------------------------------------------------------------------------
# Pressure
# ---------------------------------------------------------------------------

def psi_to_pa(value_psi: float) -> float:
    """Convert pound-force per square inch to pascal."""
    return _as_finite(value_psi, "value_psi") * PSI_TO_PA


def pa_to_psi(value_pa: float) -> float:
    """Convert pascal to pound-force per square inch."""
    return _as_finite(value_pa, "value_pa") / PSI_TO_PA


def kpa_to_pa(value_kpa: float) -> float:
    """Convert kilopascal to pascal."""
    return _as_finite(value_kpa, "value_kpa") * KPA_TO_PA


def pa_to_kpa(value_pa: float) -> float:
    """Convert pascal to kilopascal."""
    return _as_finite(value_pa, "value_pa") / KPA_TO_PA


def bar_to_pa(value_bar: float) -> float:
    """Convert bar to pascal."""
    return _as_finite(value_bar, "value_bar") * BAR_TO_PA


def pa_to_bar(value_pa: float) -> float:
    """Convert pascal to bar."""
    return _as_finite(value_pa, "value_pa") / BAR_TO_PA


# ---------------------------------------------------------------------------
# Density
# ---------------------------------------------------------------------------

def ppg_to_kg_m3(value_ppg: float) -> float:
    """Convert pounds per gallon (US) to kilogram per cubic metre."""
    return _as_finite(value_ppg, "value_ppg") * PPG_TO_KG_M3


def kg_m3_to_ppg(value_kg_m3: float) -> float:
    """Convert kilogram per cubic metre to pounds per gallon (US)."""
    return _as_finite(value_kg_m3, "value_kg_m3") / PPG_TO_KG_M3


# ---------------------------------------------------------------------------
# Length
# ---------------------------------------------------------------------------

def ft_to_m(value_ft: float) -> float:
    """Convert international foot to metre."""
    return _as_finite(value_ft, "value_ft") * FT_TO_M


def m_to_ft(value_m: float) -> float:
    """Convert metre to international foot."""
    return _as_finite(value_m, "value_m") / FT_TO_M


def mm_to_m(value_mm: float) -> float:
    """Convert millimetre to metre."""
    return _as_finite(value_mm, "value_mm") * MM_TO_M


def m_to_mm(value_m: float) -> float:
    """Convert metre to millimetre."""
    return _as_finite(value_m, "value_m") / MM_TO_M


def inch_to_m(value_in: float) -> float:
    """Convert inch to metre. Useful for bit and pipe sizes."""
    return _as_finite(value_in, "value_in") * IN_TO_M


def m_to_inch(value_m: float) -> float:
    """Convert metre to inch."""
    return _as_finite(value_m, "value_m") / IN_TO_M


# ---------------------------------------------------------------------------
# Flow rate
# ---------------------------------------------------------------------------

def lpm_to_m3_s(value_lpm: float) -> float:
    """Convert litre per minute to cubic metre per second."""
    return _as_finite(value_lpm, "value_lpm") * L_TO_M3 / 60.0


def m3_s_to_lpm(value_m3_s: float) -> float:
    """Convert cubic metre per second to litre per minute."""
    return _as_finite(value_m3_s, "value_m3_s") / L_TO_M3 * 60.0


def bbl_min_to_m3_s(value_bbl_min: float) -> float:
    """Convert oil-barrel per minute to cubic metre per second."""
    return _as_finite(value_bbl_min, "value_bbl_min") * BBL_TO_M3 / 60.0


def m3_s_to_bbl_min(value_m3_s: float) -> float:
    """Convert cubic metre per second to oil-barrel per minute."""
    return _as_finite(value_m3_s, "value_m3_s") / BBL_TO_M3 * 60.0


# ---------------------------------------------------------------------------
# Viscosity
# ---------------------------------------------------------------------------

def cp_to_pa_s(value_cp: float) -> float:
    """Convert centipoise to pascal-second."""
    return _as_finite(value_cp, "value_cp") * CP_TO_PA_S


def pa_s_to_cp(value_pa_s: float) -> float:
    """Convert pascal-second to centipoise."""
    return _as_finite(value_pa_s, "value_pa_s") / CP_TO_PA_S
