"""Core drilling-engineering calculations.

All formulas use oilfield units unless otherwise noted:

- Mud weight (MW): pounds per gallon (ppg)
- Depth / length: feet (ft)
- Pressure: pounds per square inch (psi)
- Diameter: inches (in)
- Flow rate: gallons per minute (gpm)
- Velocity: feet per minute (ft/min)
- Angles: degrees

The functions are intentionally pure so they can be unit tested in isolation
and reused by the HTTP API layer.
"""

from __future__ import annotations

import math

# 0.052 = 12 in/ft * (1/231 gal/in^3) ... the standard oilfield pressure gradient
# constant that converts (ppg * ft) into psi.
PRESSURE_GRADIENT_CONSTANT = 0.052

# Nominal density of steel used for drill string buoyancy, in ppg.
STEEL_DENSITY_PPG = 65.5

# Annular-velocity constant that converts gpm and in^2 into ft/min.
ANNULAR_VELOCITY_CONSTANT = 24.51


def hydrostatic_pressure(mud_weight_ppg: float, tvd_ft: float) -> float:
    """Hydrostatic pressure at a given true vertical depth.

    P = 0.052 * MW * TVD
    """
    _require_positive(mud_weight=mud_weight_ppg)
    _require_non_negative(tvd=tvd_ft)
    return PRESSURE_GRADIENT_CONSTANT * mud_weight_ppg * tvd_ft


def equivalent_circulating_density(
    mud_weight_ppg: float, annular_pressure_loss_psi: float, tvd_ft: float
) -> float:
    """Equivalent Circulating Density (ECD).

    ECD = MW + APL / (0.052 * TVD)

    The ECD represents the effective mud weight the formation "sees" while
    circulating, accounting for the extra annular friction pressure.
    """
    _require_positive(mud_weight=mud_weight_ppg, tvd=tvd_ft)
    _require_non_negative(annular_pressure_loss=annular_pressure_loss_psi)
    return mud_weight_ppg + annular_pressure_loss_psi / (
        PRESSURE_GRADIENT_CONSTANT * tvd_ft
    )


def buoyancy_factor(mud_weight_ppg: float) -> float:
    """Buoyancy factor for a steel drill string.

    BF = (rho_steel - MW) / rho_steel

    Multiply the string's air weight by this factor to get its buoyed weight.
    """
    _require_non_negative(mud_weight=mud_weight_ppg)
    if mud_weight_ppg >= STEEL_DENSITY_PPG:
        raise ValueError("mud weight must be less than steel density (65.5 ppg)")
    return (STEEL_DENSITY_PPG - mud_weight_ppg) / STEEL_DENSITY_PPG


def annular_velocity(
    flow_rate_gpm: float, hole_diameter_in: float, pipe_diameter_in: float
) -> float:
    """Average annular velocity of the drilling fluid.

    AV = 24.51 * Q / (Dh^2 - Dp^2)

    Returns feet per minute.
    """
    _require_positive(
        flow_rate=flow_rate_gpm,
        hole_diameter=hole_diameter_in,
        pipe_diameter=pipe_diameter_in,
    )
    if hole_diameter_in <= pipe_diameter_in:
        raise ValueError("hole diameter must be greater than pipe diameter")
    area_term = hole_diameter_in**2 - pipe_diameter_in**2
    return ANNULAR_VELOCITY_CONSTANT * flow_rate_gpm / area_term


def dogleg_severity(
    inclination_1_deg: float,
    azimuth_1_deg: float,
    inclination_2_deg: float,
    azimuth_2_deg: float,
    course_length_ft: float,
    normalization_ft: float = 100.0,
) -> float:
    """Dogleg severity (DLS) between two survey stations.

    Uses the standard minimum-curvature dogleg angle:

        cos(beta) = cos(I2 - I1) - sin(I1) * sin(I2) * (1 - cos(A2 - A1))

    The dogleg angle beta is then normalized to a course length (default per
    100 ft) to express the well's rate of change of direction.
    """
    _require_positive(course_length=course_length_ft, normalization=normalization_ft)

    i1 = math.radians(inclination_1_deg)
    i2 = math.radians(inclination_2_deg)
    a1 = math.radians(azimuth_1_deg)
    a2 = math.radians(azimuth_2_deg)

    cos_beta = math.cos(i2 - i1) - math.sin(i1) * math.sin(i2) * (
        1 - math.cos(a2 - a1)
    )
    # Guard against tiny floating point excursions outside [-1, 1].
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta_deg = math.degrees(math.acos(cos_beta))

    return beta_deg * (normalization_ft / course_length_ft)


def kill_mud_weight(
    current_mud_weight_ppg: float, sidpp_psi: float, tvd_ft: float
) -> float:
    """Kill mud weight required to balance formation pressure after a kick.

    KMW = MW + SIDPP / (0.052 * TVD)

    SIDPP is the shut-in drill pipe pressure.
    """
    _require_positive(current_mud_weight=current_mud_weight_ppg, tvd=tvd_ft)
    _require_non_negative(sidpp=sidpp_psi)
    return current_mud_weight_ppg + sidpp_psi / (PRESSURE_GRADIENT_CONSTANT * tvd_ft)


def _require_positive(**values: float) -> None:
    for name, value in values.items():
        if value is None or value <= 0:
            raise ValueError(f"{name} must be a positive number")


def _require_non_negative(**values: float) -> None:
    for name, value in values.items():
        if value is None or value < 0:
            raise ValueError(f"{name} must be zero or a positive number")
