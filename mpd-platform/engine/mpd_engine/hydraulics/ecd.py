"""Bottomhole pressure and equivalent circulating density."""

from __future__ import annotations

from mpd_engine.constants import STANDARD_GRAVITY_M_S2
from mpd_engine.units.validation import require_nonnegative, require_positive


def calculate_bottomhole_pressure(
    hydrostatic_pressure_pa: float,
    annular_friction_pressure_pa: float,
    surface_backpressure_pa: float,
) -> float:
    """Return annular bottomhole pressure, Pa.

    BHP = P_hydrostatic + P_annular_friction + P_surface_backpressure

    Version 1 is a single-phase incompressible annulus. Pipe-side losses
    do not enter BHP. Surface backpressure is an engineer-entered
    scenario value, not a choke command.
    """
    hydrostatic = require_nonnegative(hydrostatic_pressure_pa, "hydrostatic_pressure_pa")
    friction = require_nonnegative(
        annular_friction_pressure_pa, "annular_friction_pressure_pa"
    )
    sbp = require_nonnegative(surface_backpressure_pa, "surface_backpressure_pa")
    return hydrostatic + friction + sbp


def calculate_ecd_kg_m3(
    bottomhole_pressure_pa: float,
    tvd_m: float,
    gravity_m_s2: float = STANDARD_GRAVITY_M_S2,
) -> float:
    """Return equivalent circulating density, kg/m³.

    ECD = BHP / (g * TVD)

    TVD must be greater than zero. This function does not substitute a
    default ECD at surface.
    """
    bhp = require_nonnegative(bottomhole_pressure_pa, "bottomhole_pressure_pa")
    tvd = require_positive(tvd_m, "tvd_m")
    gravity = require_positive(gravity_m_s2, "gravity_m_s2")
    return bhp / (gravity * tvd)


def calculate_required_surface_backpressure(
    target_bottomhole_pressure_pa: float,
    hydrostatic_pressure_pa: float,
    annular_friction_pressure_pa: float,
) -> float:
    """Return the algebraic surface backpressure needed to hit a target BHP, Pa.

    SBP_req = target_BHP - P_hydrostatic - P_annular_friction

    A negative result means hydrostatic plus friction already exceed the
    target. The value is not clamped to zero; callers must show it and
    decide whether a review of mud weight or target is required.
    """
    target = require_positive(
        target_bottomhole_pressure_pa, "target_bottomhole_pressure_pa"
    )
    hydrostatic = require_nonnegative(hydrostatic_pressure_pa, "hydrostatic_pressure_pa")
    friction = require_nonnegative(
        annular_friction_pressure_pa, "annular_friction_pressure_pa"
    )
    return target - hydrostatic - friction
