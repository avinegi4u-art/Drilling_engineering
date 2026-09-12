"""Annular friction pressure for Bingham Plastic fluid.

ENGINEERING APPROXIMATION
-------------------------
Version 1 uses a concentric-annulus *narrow-slot* laminar Bingham model
for all flow rates. A Blasius turbulent helper is provided for later
validation but is not selected automatically, because dropping the yield
term at Re = 2100 would create a non-physical friction decrease.

These are teaching/engineering-screening correlations, not a full
Fredrickson–Bird or CFD annulus solution. Independent validation is
required before field use.
"""

from __future__ import annotations

from mpd_engine.hydraulics.geometry import (
    calculate_annular_area,
    calculate_annular_velocity,
    calculate_hydraulic_diameter,
    calculate_radial_clearance,
)
from mpd_engine.hydraulics.rheology import reynolds_number
from mpd_engine.units.validation import (
    require_nonnegative,
    require_positive,
    validate_annular_clearance,
)

# Blasius (Darcy) smooth-pipe coefficient. Engineering approximation.
_BLASIUS_COEFFICIENT = 0.3164
_BLASIUS_EXPONENT = 0.25


def laminar_bingham_slot_pressure_gradient_pa_m(
    plastic_viscosity_pa_s: float,
    yield_stress_pa: float,
    velocity_m_s: float,
    hole_id_m: float,
    pipe_od_m: float,
) -> float:
    """Return laminar Bingham slot pressure gradient, Pa/m.

    ENGINEERING APPROXIMATION (narrow-slot Bingham Plastic):

        δ = (D_hole - D_pipe) / 2
        dP/dL = 12 μ_p v / δ² + 3 τ_y / δ

    Equivalent form:

        dP/dL = 48 μ_p v / (D_hole - D_pipe)² + 6 τ_y / (D_hole - D_pipe)

    The yield term is independent of velocity, so a static fluid still
    requires a finite gradient to overcome yield stress. Version 1
    *pump-off* calculations set flow to zero and treat annular friction
    as zero (gels and start-up pressure are out of scope).
    """
    mu_p = require_nonnegative(plastic_viscosity_pa_s, "plastic_viscosity_pa_s")
    tau_y = require_nonnegative(yield_stress_pa, "yield_stress_pa")
    velocity = require_nonnegative(velocity_m_s, "velocity_m_s")
    validate_annular_clearance(hole_id_m, pipe_od_m)
    gap = calculate_radial_clearance(hole_id_m, pipe_od_m)
    return 12.0 * mu_p * velocity / gap**2 + 3.0 * tau_y / gap


def turbulent_blasius_pressure_gradient_pa_m(
    mud_density_kg_m3: float,
    plastic_viscosity_pa_s: float,
    velocity_m_s: float,
    hole_id_m: float,
    pipe_od_m: float,
) -> float:
    """Return a Blasius turbulent pressure gradient, Pa/m.

    ENGINEERING APPROXIMATION. Darcy–Weisbach on hydraulic diameter
    with f = 0.3164 / Re_pv^0.25 and Re_pv = ρ v D_hyd / μ_p.

    Yield stress is ignored in the turbulent branch (version-1 limitation).
    """
    density = require_positive(mud_density_kg_m3, "mud_density_kg_m3")
    mu_p = require_positive(plastic_viscosity_pa_s, "plastic_viscosity_pa_s")
    velocity = require_positive(velocity_m_s, "velocity_m_s")
    diameter = calculate_hydraulic_diameter(hole_id_m, pipe_od_m)
    re_pv = reynolds_number(density, velocity, diameter, mu_p)
    darcy_f = _BLASIUS_COEFFICIENT / re_pv**_BLASIUS_EXPONENT
    return darcy_f * (density * velocity**2) / (2.0 * diameter)


def calculate_bingham_annular_pressure_loss(
    mud_density_kg_m3: float,
    plastic_viscosity_pa_s: float,
    yield_stress_pa: float,
    flow_rate_m3_s: float,
    length_m: float,
    hole_id_m: float,
    pipe_od_m: float,
) -> float:
    """Return annular frictional pressure loss, Pa.

    Version 1 always uses the laminar Bingham slot approximation.
    A plastic-viscosity Reynolds number is *not* used to switch correlations
    in this version, because a Blasius branch would drop the yield-stress
    term and create a non-physical friction decrease at the 2100 threshold.

    The Blasius helper remains available for later validation. Callers
    should warn when Re_pv > 2100 so the engineer knows the slot model is
    outside its usual laminar range.

    Zero flow or zero length returns 0 (no gel/start-up pressure).

    Args:
        mud_density_kg_m3: Mud density, kg/m³ (retained for Re checks / later models).
        plastic_viscosity_pa_s: Bingham plastic viscosity, Pa·s.
        yield_stress_pa: Bingham yield stress, Pa.
        flow_rate_m3_s: Volumetric flow in the annulus, m³/s.
        length_m: Along-hole annular length, m.
        hole_id_m: Wellbore inner diameter, m.
        pipe_od_m: Drillstring outer diameter, m.

    Returns:
        Frictional pressure loss in pascal (always >= 0).
    """
    require_positive(mud_density_kg_m3, "mud_density_kg_m3")
    mu_p = require_nonnegative(plastic_viscosity_pa_s, "plastic_viscosity_pa_s")
    tau_y = require_nonnegative(yield_stress_pa, "yield_stress_pa")
    flow = require_nonnegative(flow_rate_m3_s, "flow_rate_m3_s")
    length = require_nonnegative(length_m, "length_m")
    if flow == 0.0 or length == 0.0:
        return 0.0

    area = calculate_annular_area(hole_id_m, pipe_od_m)
    velocity = calculate_annular_velocity(flow, area)
    gradient = laminar_bingham_slot_pressure_gradient_pa_m(
        mu_p, tau_y, velocity, hole_id_m, pipe_od_m
    )
    return gradient * length
