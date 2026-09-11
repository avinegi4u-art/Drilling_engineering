"""Tests for shared validation helpers."""

from __future__ import annotations

import math

import pytest

from mpd_engine.units.validation import (
    require_finite,
    require_hole_larger_than_pipe,
    require_monotonic_increasing,
    require_nonnegative,
    require_positive,
    require_tvd_not_greater_than_md,
)


def test_require_positive_and_nonnegative() -> None:
    assert require_positive(1.0, "x") == 1.0
    assert require_nonnegative(0.0, "x") == 0.0
    with pytest.raises(ValueError, match="greater than zero"):
        require_positive(0.0, "x")
    with pytest.raises(ValueError, match="greater than or equal to zero"):
        require_nonnegative(-1.0, "density")


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_non_finite_values_rejected(bad: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        require_finite(bad, "pressure")


def test_hole_must_be_larger_than_pipe() -> None:
    require_hole_larger_than_pipe(0.2159, 0.1270)
    with pytest.raises(ValueError, match="must be greater than"):
        require_hole_larger_than_pipe(0.1270, 0.1270)
    with pytest.raises(ValueError, match="must be greater than"):
        require_hole_larger_than_pipe(0.10, 0.1270)


def test_tvd_not_greater_than_md() -> None:
    require_tvd_not_greater_than_md(tvd_m=3000.0, md_m=3000.0)
    require_tvd_not_greater_than_md(tvd_m=2500.0, md_m=3000.0)
    with pytest.raises(ValueError, match="must not be greater"):
        require_tvd_not_greater_than_md(tvd_m=3100.0, md_m=3000.0)


def test_monotonic_depths() -> None:
    require_monotonic_increasing([0.0, 1000.0, 3000.0], "md")
    require_monotonic_increasing([0.0, 0.0, 10.0], "tvd", allow_equal=True)
    with pytest.raises(ValueError, match="strictly increasing"):
        require_monotonic_increasing([0.0, 1000.0, 1000.0], "md")
    with pytest.raises(ValueError, match="non-decreasing"):
        require_monotonic_increasing([0.0, -1.0], "tvd", allow_equal=True)
