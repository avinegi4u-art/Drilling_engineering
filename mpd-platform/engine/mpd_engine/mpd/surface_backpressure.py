"""Required surface backpressure helpers.

Results are engineering decision support only. They are not choke-control
setpoints and must not be sent to field equipment.
"""

from __future__ import annotations

from mpd_engine.hydraulics.ecd import calculate_required_surface_backpressure
from mpd_engine.results.warnings import EngineeringWarning, WarningSeverity
from mpd_engine.units.validation import require_nonnegative, require_positive


def required_surface_backpressure_with_limit(
    target_bottomhole_pressure_pa: float,
    hydrostatic_pressure_pa: float,
    annular_friction_pressure_pa: float,
    max_surface_backpressure_pa: float | None = None,
) -> tuple[float, list[EngineeringWarning]]:
    """Return required SBP and any limit-review warnings.

    Negative required SBP is returned unchanged so the engineer can see
    that hydrostatic plus friction already exceed the target.
    """
    required = calculate_required_surface_backpressure(
        target_bottomhole_pressure_pa,
        hydrostatic_pressure_pa,
        annular_friction_pressure_pa,
    )
    warnings: list[EngineeringWarning] = []
    if required < 0.0:
        warnings.append(
            EngineeringWarning(
                code="NEGATIVE_REQUIRED_SBP",
                severity=WarningSeverity.REVIEW,
                actual_pressure_pa=required,
                limit_pressure_pa=0.0,
                explanation=(
                    "Required surface backpressure is negative: hydrostatic plus "
                    "annular friction already exceed the target bottomhole pressure."
                ),
                recommended_engineering_review=(
                    "Review target BHP and mud weight. Do not interpret this as a "
                    "command to open or close a choke."
                ),
            )
        )
    if max_surface_backpressure_pa is not None:
        limit = require_positive(
            max_surface_backpressure_pa, "max_surface_backpressure_pa"
        )
        applied = require_nonnegative(required, "required") if required >= 0 else required
        if required > limit:
            warnings.append(
                EngineeringWarning(
                    code="REQUIRED_SBP_EXCEEDS_LIMIT",
                    severity=WarningSeverity.HIGH,
                    actual_pressure_pa=applied,
                    limit_pressure_pa=limit,
                    explanation=(
                        "Calculated required surface backpressure exceeds the "
                        "engineer-configured SBP review limit."
                    ),
                    recommended_engineering_review=(
                        "Review the SBP limit, target BHP, and mud weight. This is "
                        "not a command to apply that surface pressure."
                    ),
                )
            )
    return required, warnings
