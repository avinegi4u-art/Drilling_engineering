"""Additional engineering-limit reviews."""

from __future__ import annotations

from mpd_engine.constants import LAMINAR_REYNOLDS_LIMIT
from mpd_engine.results.warnings import EngineeringWarning, WarningSeverity


def turbulent_flow_warning(
    reynolds_number: float, depth_m: float | None = None
) -> EngineeringWarning:
    """Return a review notice when the version-1 Re switch is turbulent."""
    return EngineeringWarning(
        code="TURBULENT_FRICTION_APPROXIMATION",
        severity=WarningSeverity.REVIEW,
        depth_m=depth_m,
        explanation=(
            f"Plastic-viscosity Reynolds number ({reynolds_number:.0f}) exceeds "
            f"{LAMINAR_REYNOLDS_LIMIT:.0f}. Annular friction used a Blasius "
            "approximation that ignores yield stress."
        ),
        recommended_engineering_review=(
            "Validate turbulent annular friction against an independent hydraulics "
            "program before using ECD for a narrow pressure window."
        ),
    )
