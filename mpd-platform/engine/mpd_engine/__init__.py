"""MPD hydraulics calculation engine.

This package is independent of FastAPI and Streamlit. Import it from
scripts, notebooks, API services, dashboards, or future background jobs.

Version 1 scope
---------------
Steady-state, single-phase, Bingham Plastic hydraulics. Internal units
are SI (m, Pa, kg/m³, m³/s). Hydraulics functions are added in Phase 2.

This engine is for engineering decision support only. It does not
implement automatic choke control or send commands to field equipment.
"""

from mpd_engine.models import (
    AnnularSectionType,
    Drillstring,
    DrillstringComponent,
    DrillstringComponentType,
    FluidProperties,
    OperatingConditions,
    OperatingMode,
    PressureWindow,
    PressureWindowPoint,
    RheologyModel,
    TrajectoryStation,
    Well,
    WellSection,
    calculate_tvd_vertical,
)
from mpd_engine.units.conversions import (
    bar_to_pa,
    bbl_min_to_m3_s,
    cp_to_pa_s,
    ft_to_m,
    inch_to_m,
    kg_m3_to_ppg,
    kpa_to_pa,
    lpm_to_m3_s,
    m3_s_to_bbl_min,
    m3_s_to_lpm,
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

__version__ = "0.1.0"
CALCULATION_VERSION = "0.1.0-steady-state-single-phase-bingham"

VERSION_1_ASSUMPTIONS: tuple[str, ...] = (
    "Steady-state, single-phase hydraulics model.",
    "SI units internally (m, Pa, kg/m³, m³/s).",
    "Vertical well in version 1; TVD equals MD.",
    "One well section with constant annular diameter.",
    "Constant mud density; no compressibility or cuttings loading.",
    "Bingham Plastic rheology.",
    "Incompressible single-phase drilling fluid.",
    "No temperature correction of density or rheology.",
    "No gas influx.",
    "No surge and swab.",
    "No transient or multiphase model.",
    "No automated choke or equipment control.",
    "Engineering decision support only.",
)

__all__ = [
    "CALCULATION_VERSION",
    "VERSION_1_ASSUMPTIONS",
    "AnnularSectionType",
    "Drillstring",
    "DrillstringComponent",
    "DrillstringComponentType",
    "FluidProperties",
    "OperatingConditions",
    "OperatingMode",
    "PressureWindow",
    "PressureWindowPoint",
    "RheologyModel",
    "TrajectoryStation",
    "Well",
    "WellSection",
    "__version__",
    "bar_to_pa",
    "bbl_min_to_m3_s",
    "calculate_tvd_vertical",
    "cp_to_pa_s",
    "ft_to_m",
    "inch_to_m",
    "kg_m3_to_ppg",
    "kpa_to_pa",
    "lpm_to_m3_s",
    "m_to_ft",
    "m_to_mm",
    "m3_s_to_bbl_min",
    "m3_s_to_lpm",
    "mm_to_m",
    "pa_s_to_cp",
    "pa_to_bar",
    "pa_to_kpa",
    "pa_to_psi",
    "ppg_to_kg_m3",
    "psi_to_pa",
]
