"""Bingham Plastic rheology helpers.

Version 1 uses Bingham Plastic only. Apparent viscosity and Reynolds number
are engineering approximations used to choose a laminar versus turbulent
friction correlation. They are not a full constitutive solver.
"""

from __future__ import annotations

from mpd_engine.units.validation import require_nonnegative, require_positive


def apparent_viscosity_bingham_slot(
    plastic_viscosity_pa_s: float,
    yield_stress_pa: float,
    velocity_m_s: float,
    radial_clearance_m: float,
) -> float:
    """Return an apparent viscosity for slot-flow Bingham Plastic, Pa·s.

    ENGINEERING APPROXIMATION. For steady slot flow the linearised
    apparent viscosity is:

        μ_app = μ_p + τ_y * δ / (3 v)

    When velocity is zero the yield term is undefined; this function
    raises rather than substituting a default.
    """
    mu_p = require_nonnegative(plastic_viscosity_pa_s, "plastic_viscosity_pa_s")
    tau_y = require_nonnegative(yield_stress_pa, "yield_stress_pa")
    velocity = require_positive(velocity_m_s, "velocity_m_s")
    gap = require_positive(radial_clearance_m, "radial_clearance_m")
    return mu_p + tau_y * gap / (3.0 * velocity)


def reynolds_number(
    mud_density_kg_m3: float,
    velocity_m_s: float,
    hydraulic_diameter_m: float,
    viscosity_pa_s: float,
) -> float:
    """Return a pipe/annulus Reynolds number, dimensionless.

    Re = ρ v D / μ

    For Bingham fluids version 1 uses either plastic viscosity or the
    slot apparent viscosity. Both choices are approximations.
    """
    density = require_positive(mud_density_kg_m3, "mud_density_kg_m3")
    velocity = require_nonnegative(velocity_m_s, "velocity_m_s")
    diameter = require_positive(hydraulic_diameter_m, "hydraulic_diameter_m")
    viscosity = require_positive(viscosity_pa_s, "viscosity_pa_s")
    return density * velocity * diameter / viscosity


def hedstrom_number(
    mud_density_kg_m3: float,
    yield_stress_pa: float,
    hydraulic_diameter_m: float,
    plastic_viscosity_pa_s: float,
) -> float:
    """Return the Hedstrom number He = ρ τ_y D² / μ_p².

    Recorded for later transition-criterion work. Version 1 does not
    use He to switch flow regimes.
    """
    density = require_positive(mud_density_kg_m3, "mud_density_kg_m3")
    tau_y = require_nonnegative(yield_stress_pa, "yield_stress_pa")
    diameter = require_positive(hydraulic_diameter_m, "hydraulic_diameter_m")
    mu_p = require_positive(plastic_viscosity_pa_s, "plastic_viscosity_pa_s")
    return density * tau_y * diameter**2 / mu_p**2
