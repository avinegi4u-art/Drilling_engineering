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

from mpd_engine.constants import CALCULATION_VERSION, VERSION_1_ASSUMPTIONS
from mpd_engine.hydraulics import (
    calculate_annular_area,
    calculate_annular_velocity,
    calculate_bingham_annular_pressure_loss,
    calculate_bottomhole_pressure,
    calculate_ecd_kg_m3,
    calculate_hydraulic_diameter,
    calculate_hydrostatic_pressure,
    calculate_required_surface_backpressure,
)
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
from mpd_engine.mpd import (
    ConnectionComparison,
    PressureWindowStatus,
    compare_connection,
)
from mpd_engine.results.result_models import CalculationResult
from mpd_engine.results.warnings import EngineeringWarning
from mpd_engine.services import HydraulicsCase, run_hydraulics
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

__all__ = [
    "CALCULATION_VERSION",
    "VERSION_1_ASSUMPTIONS",
    "AnnularSectionType",
    "CalculationResult",
    "ConnectionComparison",
    "Drillstring",
    "DrillstringComponent",
    "DrillstringComponentType",
    "EngineeringWarning",
    "FluidProperties",
    "HydraulicsCase",
    "OperatingConditions",
    "OperatingMode",
    "PressureWindow",
    "PressureWindowPoint",
    "PressureWindowStatus",
    "RheologyModel",
    "TrajectoryStation",
    "Well",
    "WellSection",
    "__version__",
    "bar_to_pa",
    "bbl_min_to_m3_s",
    "calculate_annular_area",
    "calculate_annular_velocity",
    "calculate_bingham_annular_pressure_loss",
    "calculate_bottomhole_pressure",
    "calculate_ecd_kg_m3",
    "calculate_hydraulic_diameter",
    "calculate_hydrostatic_pressure",
    "calculate_required_surface_backpressure",
    "calculate_tvd_vertical",
    "compare_connection",
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
    "run_hydraulics",
]
