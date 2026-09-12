"""Shared physical constants for the version-1 hydraulics engine."""

from __future__ import annotations

# Standard acceleration of gravity (CGPM 1901 / ISO 80000-3).
STANDARD_GRAVITY_M_S2 = 9.80665

# Version-1 laminar/turbulent switch using a plastic-viscosity Reynolds number.
# Bingham-plastic transition is better described with a Hedstrom number; that
# refinement is left for a later version. Marked as an engineering approximation.
LAMINAR_REYNOLDS_LIMIT = 2100.0

CALCULATION_VERSION = "1.0.0-steady-state-single-phase-bingham"

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
    "Annular friction uses a narrow-slot Bingham approximation (engineering screening only).",
)
