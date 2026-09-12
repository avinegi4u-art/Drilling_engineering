"""Pressure-window interpolation and classification.

Statuses describe where the calculated annular pressure sits relative to
the supplied geopressure curves. They are not drilling instructions.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from mpd_engine.models.pressure_window import PressureWindow, PressureWindowPoint
from mpd_engine.results.warnings import EngineeringWarning, WarningSeverity
from mpd_engine.units.validation import require_nonnegative


class PressureWindowStatus(StrEnum):
    """Classification of annular pressure at one TVD."""

    BELOW_PORE_PRESSURE = "BELOW_PORE_PRESSURE"
    WITHIN_OPERATING_WINDOW = "WITHIN_OPERATING_WINDOW"
    ABOVE_FRACTURE_PRESSURE = "ABOVE_FRACTURE_PRESSURE"
    ABOVE_COLLAPSE_LIMIT = "ABOVE_COLLAPSE_LIMIT"
    INVALID_INPUT = "INVALID_INPUT"


class InterpolatedWindow(BaseModel):
    """Pressure-window values at one TVD after linear interpolation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tvd_m: float
    pore_pressure_pa: float
    fracture_pressure_pa: float
    collapse_pressure_pa: float | None
    within_curve_range: bool


def interpolate_pressure_window(window: PressureWindow, tvd_m: float) -> InterpolatedWindow:
    """Linearly interpolate pore, collapse, and fracture pressure versus TVD.

    TVD outside the supplied curve is not extrapolated. The result is
    flagged ``within_curve_range=False`` so callers can emit INVALID_INPUT
    instead of inventing a gradient.
    """
    tvd = require_nonnegative(tvd_m, "tvd_m")
    points = window.points
    if tvd < points[0].tvd_m or tvd > points[-1].tvd_m:
        nearest = points[0] if tvd < points[0].tvd_m else points[-1]
        return InterpolatedWindow(
            tvd_m=tvd,
            pore_pressure_pa=nearest.pore_pressure_pa,
            fracture_pressure_pa=nearest.fracture_pressure_pa,
            collapse_pressure_pa=nearest.collapse_pressure_pa,
            within_curve_range=False,
        )
    for lower, upper in zip(points, points[1:], strict=False):
        if lower.tvd_m <= tvd <= upper.tvd_m:
            return InterpolatedWindow(
                tvd_m=tvd,
                pore_pressure_pa=_lerp(
                    tvd, lower.tvd_m, upper.tvd_m, lower.pore_pressure_pa, upper.pore_pressure_pa
                ),
                fracture_pressure_pa=_lerp(
                    tvd,
                    lower.tvd_m,
                    upper.tvd_m,
                    lower.fracture_pressure_pa,
                    upper.fracture_pressure_pa,
                ),
                collapse_pressure_pa=_lerp_optional(
                    tvd,
                    lower.tvd_m,
                    upper.tvd_m,
                    lower.collapse_pressure_pa,
                    upper.collapse_pressure_pa,
                ),
                within_curve_range=True,
            )
    last: PressureWindowPoint = points[-1]
    return InterpolatedWindow(
        tvd_m=tvd,
        pore_pressure_pa=last.pore_pressure_pa,
        fracture_pressure_pa=last.fracture_pressure_pa,
        collapse_pressure_pa=last.collapse_pressure_pa,
        within_curve_range=True,
    )


def _lerp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    if x1 == x0:
        return y0
    weight = (x - x0) / (x1 - x0)
    return y0 + weight * (y1 - y0)


def _lerp_optional(
    x: float,
    x0: float,
    x1: float,
    y0: float | None,
    y1: float | None,
) -> float | None:
    if y0 is None or y1 is None:
        return None
    return _lerp(x, x0, x1, y0, y1)


def classify_pressure_window(
    annular_pressure_pa: float,
    interpolated: InterpolatedWindow,
) -> tuple[PressureWindowStatus, list[EngineeringWarning]]:
    """Classify annular pressure against the interpolated window.

    Priority:
    1. INVALID_INPUT if the TVD is outside the supplied curve.
    2. ABOVE_FRACTURE_PRESSURE if P > fracture.
    3. BELOW_PORE_PRESSURE if P < pore (influx-risk review).
    4. ABOVE_COLLAPSE_LIMIT if collapse is defined and P < collapse
       (hole-stability lower bound has been crossed). The enum name is
       the requested status code; the explanation states the pressure is
       below the collapse curve.
    5. WITHIN_OPERATING_WINDOW otherwise.
    """
    pressure = require_nonnegative(annular_pressure_pa, "annular_pressure_pa")
    warnings: list[EngineeringWarning] = []
    if not interpolated.within_curve_range:
        warnings.append(
            EngineeringWarning(
                code="WINDOW_TVD_OUT_OF_RANGE",
                severity=WarningSeverity.HIGH,
                depth_m=interpolated.tvd_m,
                actual_pressure_pa=pressure,
                limit_pressure_pa=None,
                explanation=(
                    "This TVD is outside the supplied pressure-window curve. "
                    "No extrapolated gradient was used."
                ),
                recommended_engineering_review=(
                    "Extend the pore/collapse/fracture table to cover this depth "
                    "before using the result for well-control planning."
                ),
            )
        )
        return PressureWindowStatus.INVALID_INPUT, warnings

    if pressure > interpolated.fracture_pressure_pa:
        warnings.append(
            EngineeringWarning(
                code="ABOVE_FRACTURE_PRESSURE",
                severity=WarningSeverity.HIGH,
                depth_m=interpolated.tvd_m,
                actual_pressure_pa=pressure,
                limit_pressure_pa=interpolated.fracture_pressure_pa,
                explanation=(
                    "Calculated annular pressure exceeds the fracture-pressure curve "
                    "at this TVD."
                ),
                recommended_engineering_review=(
                    "Review mud weight, annular friction, and surface backpressure "
                    "against the fracture gradient. This is not a choke command."
                ),
            )
        )
        return PressureWindowStatus.ABOVE_FRACTURE_PRESSURE, warnings

    if pressure < interpolated.pore_pressure_pa:
        warnings.append(
            EngineeringWarning(
                code="BELOW_PORE_PRESSURE",
                severity=WarningSeverity.HIGH,
                depth_m=interpolated.tvd_m,
                actual_pressure_pa=pressure,
                limit_pressure_pa=interpolated.pore_pressure_pa,
                explanation=(
                    "Calculated annular pressure is below the pore-pressure curve "
                    "at this TVD."
                ),
                recommended_engineering_review=(
                    "Review hydrostatic column and surface backpressure against "
                    "pore pressure. This is not an operational order to increase SBP."
                ),
            )
        )
        return PressureWindowStatus.BELOW_PORE_PRESSURE, warnings

    if (
        interpolated.collapse_pressure_pa is not None
        and pressure < interpolated.collapse_pressure_pa
    ):
        warnings.append(
            EngineeringWarning(
                code="ABOVE_COLLAPSE_LIMIT",
                severity=WarningSeverity.REVIEW,
                depth_m=interpolated.tvd_m,
                actual_pressure_pa=pressure,
                limit_pressure_pa=interpolated.collapse_pressure_pa,
                explanation=(
                    "Calculated annular pressure is below the collapse-pressure "
                    "curve (wellbore-stability lower bound) at this TVD."
                ),
                recommended_engineering_review=(
                    "Review hole-stability inputs and the operating window. "
                    "This is not a command to change mud weight or choke position."
                ),
            )
        )
        return PressureWindowStatus.ABOVE_COLLAPSE_LIMIT, warnings

    return PressureWindowStatus.WITHIN_OPERATING_WINDOW, warnings
