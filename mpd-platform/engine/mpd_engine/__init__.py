"""MPD hydraulics calculation engine.

Decision-support only. This package does not send commands to field equipment
and must remain usable without FastAPI or Streamlit.

Version 1 implements validated domain models and SI unit conversions.
Hydraulics equations are added in later phases.
"""

from mpd_engine.models.case import HydraulicsCase
from mpd_engine.models.drillstring import Drillstring, DrillstringComponentType, DrillstringSegment
from mpd_engine.models.fluids import FluidProperties, RheologyModel
from mpd_engine.models.operating_conditions import OperatingConditions, OperatingMode
from mpd_engine.models.pressure_window import PressureWindowCurve, PressureWindowPoint
from mpd_engine.models.well import AnnularSectionType, TrajectoryStation, Well, WellSection

__version__ = "0.1.0"
CALCULATION_VERSION = "1.0.0-steady-state-bingham-v1"

__all__ = [
    "CALCULATION_VERSION",
    "AnnularSectionType",
    "Drillstring",
    "DrillstringComponentType",
    "DrillstringSegment",
    "FluidProperties",
    "HydraulicsCase",
    "OperatingConditions",
    "OperatingMode",
    "PressureWindowCurve",
    "PressureWindowPoint",
    "RheologyModel",
    "TrajectoryStation",
    "Well",
    "WellSection",
    "__version__",
]
