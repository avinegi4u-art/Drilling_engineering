"""Finite-number and geometry input checks used by domain models.

These helpers reject NaN, infinities, and physically impossible inputs
before any hydraulics calculation runs. Callers must not substitute
default values when validation fails.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Annotated

from pydantic import AfterValidator, Field

# Conservative operating envelopes for version 1. Values outside these
# ranges are rejected rather than silently clamped.
MAX_FLOW_RATE_M3_S = 0.1  # 6_000 L/min
MAX_SURFACE_BACKPRESSURE_PA = 34_473_786.46584  # 5_000 psi
MAX_MUD_DENSITY_KG_M3 = 3_000.0
MIN_MUD_DENSITY_KG_M3 = 500.0
MAX_TEMPERATURE_C = 250.0
MIN_TEMPERATURE_C = -20.0
MAX_WELL_DEPTH_M = 15_000.0
MIN_ANNULAR_CLEARANCE_M = 1.0e-4  # 0.1 mm


def require_finite(value: float, name: str = "value") -> float:
    """Return *value* if it is a finite float.

    Raises:
        ValueError: If *value* is NaN or infinite.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a real number, got {type(value).__name__}")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number (not NaN or Inf)")
    return number


def require_positive(value: float, name: str = "value") -> float:
    """Return *value* if it is finite and strictly greater than zero."""
    number = require_finite(value, name)
    if number <= 0.0:
        raise ValueError(f"{name} must be greater than zero, got {number}")
    return number


def require_nonnegative(value: float, name: str = "value") -> float:
    """Return *value* if it is finite and greater than or equal to zero."""
    number = require_finite(value, name)
    if number < 0.0:
        raise ValueError(f"{name} must be greater than or equal to zero, got {number}")
    return number


def _finite_after(value: float) -> float:
    return require_finite(value)


FiniteFloat = Annotated[float, AfterValidator(_finite_after)]
PositiveFloat = Annotated[float, AfterValidator(_finite_after), Field(gt=0.0)]
NonNegativeFloat = Annotated[float, AfterValidator(_finite_after), Field(ge=0.0)]


def validate_annular_clearance(hole_id_m: float, pipe_od_m: float) -> None:
    """Require a positive annular gap: hole ID must exceed pipe OD.

    Both arguments are inner/outer diameters in metres.
    """
    hole_id = require_positive(hole_id_m, "hole_id_m")
    pipe_od = require_positive(pipe_od_m, "pipe_od_m")
    clearance = hole_id - pipe_od
    if clearance <= 0.0:
        raise ValueError(
            f"hole_id_m ({hole_id}) must be greater than pipe_od_m ({pipe_od})"
        )
    if clearance < MIN_ANNULAR_CLEARANCE_M:
        raise ValueError(
            "Annular clearance is below the version-1 minimum of "
            f"{MIN_ANNULAR_CLEARANCE_M} m "
            f"(hole_id_m={hole_id}, pipe_od_m={pipe_od})"
        )


def validate_pipe_wall(od_m: float, id_m: float, name: str = "pipe") -> None:
    """Require a positive wall thickness: OD must exceed ID."""
    outer = require_positive(od_m, f"{name}_od_m")
    inner = require_positive(id_m, f"{name}_id_m")
    if inner >= outer:
        raise ValueError(
            f"{name} ID ({inner} m) must be smaller than {name} OD ({outer} m)"
        )


def validate_monotonically_increasing(
    values: Sequence[float],
    name: str = "depth",
    *,
    strict: bool = True,
) -> None:
    """Require a depth-like sequence to increase.

    Args:
        values: Sequence of finite numbers, typically measured depth or TVD.
        name: Field name used in the error message.
        strict: If True, each value must be greater than the previous one.
    """
    if len(values) == 0:
        raise ValueError(f"{name} sequence must contain at least one value")
    previous: float | None = None
    for index, raw in enumerate(values):
        current = require_finite(raw, f"{name}[{index}]")
        if previous is not None:
            if strict and current <= previous:
                raise ValueError(
                    f"{name} must be strictly increasing: "
                    f"{name}[{index}]={current} is not greater than {previous}"
                )
            if not strict and current < previous:
                raise ValueError(
                    f"{name} must be non-decreasing: "
                    f"{name}[{index}]={current} is less than {previous}"
                )
        previous = current


def validate_tvd_not_greater_than_md(
    md_m: float,
    tvd_m: float,
    *,
    index: int | None = None,
) -> None:
    """Require TVD <= MD, which holds for vertical and conventionally surveyed wells.

    A 1 mm tolerance absorbs floating-point noise from unit conversions.
    """
    md = require_nonnegative(md_m, "md_m")
    tvd = require_nonnegative(tvd_m, "tvd_m")
    location = f" at station {index}" if index is not None else ""
    if tvd > md + 1.0e-3:
        raise ValueError(
            f"tvd_m ({tvd}) must not exceed md_m ({md}){location}. "
            "Version 1 assumes a vertical or conventionally surveyed well."
        )


def validate_pressure_window_ordering(
    pore_pressure_pa: float,
    fracture_pressure_pa: float,
    collapse_pressure_pa: float | None = None,
) -> None:
    """Require a usable drilling window: pore < fracture, collapse < fracture.

    Collapse pressure may be above or below pore pressure depending on
    wellbore-stability conditions. It is not forced to sit between pore
    and fracture.
    """
    pore = require_positive(pore_pressure_pa, "pore_pressure_pa")
    fracture = require_positive(fracture_pressure_pa, "fracture_pressure_pa")
    if pore >= fracture:
        raise ValueError(
            f"pore_pressure_pa ({pore}) must be less than "
            f"fracture_pressure_pa ({fracture})"
        )
    if collapse_pressure_pa is not None:
        collapse = require_positive(collapse_pressure_pa, "collapse_pressure_pa")
        if collapse >= fracture:
            raise ValueError(
                f"collapse_pressure_pa ({collapse}) must be less than "
                f"fracture_pressure_pa ({fracture})"
            )
