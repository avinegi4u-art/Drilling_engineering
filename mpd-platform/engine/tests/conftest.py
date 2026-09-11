"""Pytest fixtures for the calculation engine."""

from __future__ import annotations

import pytest

from mpd_engine.models.case import HydraulicsCase
from tests.factories import example_vertical_well_case


@pytest.fixture
def example_case() -> HydraulicsCase:
    """Synthetic vertical-well case used by several tests."""
    return example_vertical_well_case()
