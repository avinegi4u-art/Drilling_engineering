"""Hydrostatic pressure for an incompressible column."""

from __future__ import annotations

from mpd_engine.constants import STANDARD_GRAVITY_M_S2
from mpd_engine.units.validation import require_nonnegative, require_positive


def calculate_hydrostatic_pressure(
    mud_density_kg_m3: float,
    tvd_m: float,
    gravity_m_s2: float = STANDARD_GRAVITY_M_S2,
) -> float:
    """Return hydrostatic pressure of a constant-density column, Pa.

    P_h = ρ g TVD

    Version 1 assumptions:
    - Constant mud density (no compressibility, no cuttings loading).
    - No temperature correction.
    - TVD is the true vertical depth of the point of interest, m.

    Args:
        mud_density_kg_m3: Fluid density, kg/m³.
        tvd_m: True vertical depth, m. Zero is valid (surface).
        gravity_m_s2: Gravitational acceleration, m/s².

    Returns:
        Hydrostatic pressure in pascal.
    """
    density = require_positive(mud_density_kg_m3, "mud_density_kg_m3")
    tvd = require_nonnegative(tvd_m, "tvd_m")
    gravity = require_positive(gravity_m_s2, "gravity_m_s2")
    return density * gravity * tvd
