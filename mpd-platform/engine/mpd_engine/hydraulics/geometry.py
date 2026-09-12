"""Annular geometry calculations.

All arguments and return values are SI: metres and square metres.
"""

from __future__ import annotations

import math

from mpd_engine.units.validation import (
    require_nonnegative,
    require_positive,
    validate_annular_clearance,
)


def calculate_annular_area(hole_id_m: float, pipe_od_m: float) -> float:
    """Return the concentric annular cross-section, m².

    A = π/4 * (D_hole² - D_pipe²)

    Args:
        hole_id_m: Inner diameter of the wellbore wall (open hole or casing), m.
        pipe_od_m: Outer diameter of the drillstring, m.

    Returns:
        Annular area in square metres.

    Raises:
        ValueError: If diameters are not positive or the hole does not clear the pipe.
    """
    hole_id = require_positive(hole_id_m, "hole_id_m")
    pipe_od = require_positive(pipe_od_m, "pipe_od_m")
    validate_annular_clearance(hole_id, pipe_od)
    return math.pi / 4.0 * (hole_id**2 - pipe_od**2)


def calculate_hydraulic_diameter(hole_id_m: float, pipe_od_m: float) -> float:
    """Return the concentric-annulus hydraulic diameter, m.

    D_hyd = D_hole - D_pipe

    This is the standard drilling-hydraulics definition (4A/wetted perimeter
    for a concentric annulus reduces to D_hole - D_pipe). It is not the
    slot gap (D_hole - D_pipe)/2 used inside the Bingham slot approximation.

    Args:
        hole_id_m: Inner diameter of the wellbore wall, m.
        pipe_od_m: Outer diameter of the drillstring, m.

    Returns:
        Hydraulic diameter in metres.
    """
    hole_id = require_positive(hole_id_m, "hole_id_m")
    pipe_od = require_positive(pipe_od_m, "pipe_od_m")
    validate_annular_clearance(hole_id, pipe_od)
    return hole_id - pipe_od


def calculate_radial_clearance(hole_id_m: float, pipe_od_m: float) -> float:
    """Return the concentric radial clearance (slot gap), m.

    δ = (D_hole - D_pipe) / 2
    """
    return calculate_hydraulic_diameter(hole_id_m, pipe_od_m) / 2.0


def calculate_annular_velocity(flow_rate_m3_s: float, annular_area_m2: float) -> float:
    """Return mean annular velocity, m/s.

    v = Q / A

    Zero flow is valid (pump-off / connection) and returns 0.
    """
    flow = require_nonnegative(flow_rate_m3_s, "flow_rate_m3_s")
    area = require_positive(annular_area_m2, "annular_area_m2")
    return flow / area
