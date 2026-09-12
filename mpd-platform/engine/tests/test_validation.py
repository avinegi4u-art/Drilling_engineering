"""Input validation helper tests."""

from __future__ import annotations

import math

import pytest

from mpd_engine.units.validation import (
    require_finite,
    require_nonnegative,
    require_positive,
    validate_annular_clearance,
    validate_monotonically_increasing,
    validate_pipe_wall,
    validate_pressure_window_ordering,
    validate_tvd_not_greater_than_md,
)


def test_require_finite_rejects_nan_and_inf() -> None:
    with pytest.raises(ValueError, match="finite"):
        require_finite(math.nan, "density")
    with pytest.raises(ValueError, match="finite"):
        require_finite(math.inf, "flow")
    with pytest.raises(ValueError, match="real number"):
        require_finite(True, "flag")  # type: ignore[arg-type]


def test_require_positive_and_nonnegative() -> None:
    assert require_positive(1.2, "hole_id_m") == 1.2
    assert require_nonnegative(0.0, "flow") == 0.0
    with pytest.raises(ValueError, match="greater than zero"):
        require_positive(0.0, "hole_id_m")
    with pytest.raises(ValueError, match="greater than or equal to zero"):
        require_nonnegative(-0.5, "flow")


def test_invalid_geometry_hole_smaller_than_pipe() -> None:
    with pytest.raises(ValueError, match="must be greater than pipe_od_m"):
        validate_annular_clearance(hole_id_m=0.10, pipe_od_m=0.127)


def test_invalid_geometry_pipe_id_not_smaller_than_od() -> None:
    with pytest.raises(ValueError, match="must be smaller"):
        validate_pipe_wall(od_m=0.1016, id_m=0.1016, name="drillpipe")


def test_valid_annular_clearance() -> None:
    validate_annular_clearance(hole_id_m=0.31115, pipe_od_m=0.127)


def test_depth_must_increase() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_monotonically_increasing([0.0, 1000.0, 1000.0], name="md_m")
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_monotonically_increasing([0.0, 800.0, 500.0], name="md_m")


def test_tvd_cannot_exceed_md() -> None:
    with pytest.raises(ValueError, match="must not exceed"):
        validate_tvd_not_greater_than_md(md_m=1000.0, tvd_m=1000.5)
    validate_tvd_not_greater_than_md(md_m=1000.0, tvd_m=1000.0)
    validate_tvd_not_greater_than_md(md_m=1500.0, tvd_m=1200.0)


def test_pressure_window_ordering() -> None:
    validate_pressure_window_ordering(
        pore_pressure_pa=30_000_000.0,
        fracture_pressure_pa=45_000_000.0,
        collapse_pressure_pa=32_000_000.0,
    )
    with pytest.raises(ValueError, match="pore_pressure_pa"):
        validate_pressure_window_ordering(
            pore_pressure_pa=50_000_000.0,
            fracture_pressure_pa=45_000_000.0,
        )
    with pytest.raises(ValueError, match="collapse_pressure_pa"):
        validate_pressure_window_ordering(
            pore_pressure_pa=30_000_000.0,
            fracture_pressure_pa=45_000_000.0,
            collapse_pressure_pa=46_000_000.0,
        )
