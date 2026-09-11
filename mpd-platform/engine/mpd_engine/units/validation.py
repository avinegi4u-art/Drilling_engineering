"""Input validation helpers for finite numbers and well geometry.

These functions raise ``ValueError``. Pydantic field/model validators wrap
the same messages as ``ValidationError``.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Annotated

from pydantic import AfterValidator, Field

_RELATIVE_EQUALITY_TOLERANCE = 1e-12


def require_finite(value: float, name: str = "value") -> float:
    """Return ``value`` if it is a finite float; otherwise raise ``ValueError``."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{name} must be a number, got {type(value).__name__}.")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value}.")
    return float(value)


def require_positive(value: float, name: str = "value") -> float:
    """Return ``value`` if it is finite and strictly greater than zero."""
    require_finite(value, name)
    if value <= 0.0:
        raise ValueError(f"{name} must be greater than zero, got {value}.")
    return float(value)


def require_nonnegative(value: float, name: str = "value") -> float:
    """Return ``value`` if it is finite and greater than or equal to zero."""
    require_finite(value, name)
    if value < 0.0:
        raise ValueError(f"{name} must be greater than or equal to zero, got {value}.")
    return float(value)


def require_hole_larger_than_pipe(
    hole_id_m: float,
    pipe_od_m: float,
    hole_name: str = "hole inner diameter",
    pipe_name: str = "pipe outer diameter",
) -> None:
    """Require a positive annular clearance (hole ID > pipe OD)."""
    require_positive(hole_id_m, hole_name)
    require_positive(pipe_od_m, pipe_name)
    if hole_id_m <= pipe_od_m:
        raise ValueError(
            f"{hole_name} ({hole_id_m} m) must be greater than {pipe_name} ({pipe_od_m} m)."
        )


def require_tvd_not_greater_than_md(tvd_m: float, md_m: float) -> None:
    """Require TVD <= MD, allowing a tiny relative tolerance for round-off."""
    require_nonnegative(tvd_m, "tvd_m")
    require_nonnegative(md_m, "md_m")
    if tvd_m > md_m * (1.0 + _RELATIVE_EQUALITY_TOLERANCE) and tvd_m - md_m > 1e-9:
        raise ValueError(f"tvd_m ({tvd_m} m) must not be greater than md_m ({md_m} m).")


def require_monotonic_increasing(
    values: Sequence[float],
    name: str,
    *,
    allow_equal: bool = False,
) -> None:
    """Require a sequence of finite numbers that does not decrease.

    Depth curves use ``allow_equal=False`` (strictly increasing). TVD along a
    hold section may use ``allow_equal=True``.
    """
    if len(values) == 0:
        raise ValueError(f"{name} must contain at least one value.")
    previous: float | None = None
    for index, raw in enumerate(values):
        current = require_finite(raw, f"{name}[{index}]")
        if previous is not None:
            if allow_equal and current < previous:
                raise ValueError(
                    f"{name} must be non-decreasing; {current} follows {previous} at index {index}."
                )
            if not allow_equal and current <= previous:
                raise ValueError(
                    f"{name} must be strictly increasing; "
                    f"{current} follows {previous} at index {index}."
                )
        previous = current


def _finite_number(value: float) -> float:
    return require_finite(value)


FiniteFloat = Annotated[float, AfterValidator(_finite_number)]
FinitePositive = Annotated[float, AfterValidator(_finite_number), Field(gt=0)]
FiniteNonNegative = Annotated[float, AfterValidator(_finite_number), Field(ge=0)]
