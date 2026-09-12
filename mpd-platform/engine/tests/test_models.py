"""Domain-model validation tests."""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from mpd_engine.models.drillstring import Drillstring, DrillstringComponentType
from mpd_engine.models.fluids import FluidProperties, RheologyModel
from mpd_engine.models.operating_conditions import OperatingConditions, OperatingMode
from mpd_engine.models.pressure_window import PressureWindow, PressureWindowPoint
from mpd_engine.models.well import (
    AnnularSectionType,
    TrajectoryStation,
    Well,
    WellSection,
    calculate_tvd_vertical,
)
from mpd_engine.units.conversions import inch_to_m, lpm_to_m3_s, mm_to_m


def test_vertical_tvd_equals_md() -> None:
    assert calculate_tvd_vertical(2500.0) == 2500.0
    with pytest.raises(ValueError):
        calculate_tvd_vertical(-1.0)


def test_vertical_well_factory() -> None:
    well = Well.vertical(
        name="EXAMPLE-1",
        td_m=3000.0,
        hole_id_m=inch_to_m(12.25),
    )
    assert well.sections[0].annular_section_type is AnnularSectionType.OPEN_HOLE
    assert well.trajectory[-1].tvd_m == well.trajectory[-1].md_m
    assert well.sections[0].hole_id_m == pytest.approx(0.31115, rel=1e-12)


def test_cased_section_requires_matching_casing_id() -> None:
    with pytest.raises(ValidationError, match="casing_id_m is required"):
        WellSection(
            name="prod",
            md_top_m=0.0,
            md_bottom_m=2000.0,
            tvd_top_m=0.0,
            tvd_bottom_m=2000.0,
            hole_id_m=mm_to_m(220.5),
            annular_section_type=AnnularSectionType.CASING,
        )


def test_trajectory_tvd_greater_than_md_rejected() -> None:
    with pytest.raises(ValidationError, match="must not exceed"):
        TrajectoryStation(md_m=1000.0, tvd_m=1100.0)


def test_gapped_sections_rejected() -> None:
    with pytest.raises(ValidationError, match="contiguous"):
        Well(
            name="gapped",
            trajectory=[
                TrajectoryStation(md_m=0.0, tvd_m=0.0),
                TrajectoryStation(md_m=2000.0, tvd_m=2000.0),
            ],
            sections=[
                WellSection(
                    name="upper",
                    md_top_m=0.0,
                    md_bottom_m=1000.0,
                    tvd_top_m=0.0,
                    tvd_bottom_m=1000.0,
                    hole_id_m=0.31115,
                    annular_section_type=AnnularSectionType.OPEN_HOLE,
                ),
                WellSection(
                    name="lower",
                    md_top_m=1500.0,
                    md_bottom_m=2000.0,
                    tvd_top_m=1500.0,
                    tvd_bottom_m=2000.0,
                    hole_id_m=0.2159,
                    annular_section_type=AnnularSectionType.OPEN_HOLE,
                ),
            ],
        )


def test_non_monotonic_trajectory_rejected() -> None:
    with pytest.raises(ValidationError, match="strictly increasing"):
        Well(
            name="bad",
            trajectory=[
                TrajectoryStation(md_m=0.0, tvd_m=0.0),
                TrajectoryStation(md_m=1500.0, tvd_m=1500.0),
                TrajectoryStation(md_m=1200.0, tvd_m=1200.0),
            ],
            sections=[
                WellSection(
                    name="oh",
                    md_top_m=0.0,
                    md_bottom_m=1500.0,
                    tvd_top_m=0.0,
                    tvd_bottom_m=1500.0,
                    hole_id_m=0.31115,
                    annular_section_type=AnnularSectionType.OPEN_HOLE,
                )
            ],
        )


def test_negative_dimensions_rejected() -> None:
    with pytest.raises(ValidationError):
        WellSection(
            name="oh",
            md_top_m=0.0,
            md_bottom_m=1000.0,
            tvd_top_m=0.0,
            tvd_bottom_m=1000.0,
            hole_id_m=-0.2,
            annular_section_type=AnnularSectionType.OPEN_HOLE,
        )


def test_nan_density_rejected() -> None:
    with pytest.raises(ValidationError, match="finite"):
        FluidProperties(
            mud_density_kg_m3=math.nan,
            plastic_viscosity_pa_s=0.02,
            yield_stress_pa=10.0,
            temperature_c=50.0,
        )


def test_fluid_density_outside_envelope_rejected() -> None:
    with pytest.raises(ValidationError, match="minimum"):
        FluidProperties(
            mud_density_kg_m3=200.0,
            plastic_viscosity_pa_s=0.02,
            yield_stress_pa=10.0,
            temperature_c=50.0,
        )


def test_valid_fluid_and_rheology_model() -> None:
    fluid = FluidProperties(
        mud_density_kg_m3=1200.0,
        plastic_viscosity_pa_s=0.02,
        yield_stress_pa=9.576,
        temperature_c=50.0,
        rheology_model=RheologyModel.BINGHAM_PLASTIC,
    )
    assert fluid.mud_density_kg_m3 == 1200.0


def test_drillstring_pipe_id_must_be_less_than_od() -> None:
    with pytest.raises(ValidationError, match="must be smaller"):
        Drillstring.uniform_drillpipe(od_m=0.127, id_m=0.127, length_m=3000.0)


def test_valid_drillstring() -> None:
    drillstring = Drillstring.uniform_drillpipe(
        od_m=inch_to_m(5.0),
        id_m=inch_to_m(4.276),
        length_m=3000.0,
    )
    assert drillstring.components[0].component_type is DrillstringComponentType.DRILLPIPE
    assert drillstring.total_length_m == 3000.0


def test_pump_off_requires_zero_flow() -> None:
    with pytest.raises(ValidationError, match="requires flow_rate_m3_s"):
        OperatingConditions(
            flow_rate_m3_s=lpm_to_m3_s(800.0),
            surface_backpressure_pa=0.0,
            operating_mode=OperatingMode.PUMP_OFF,
        )


def test_connection_with_zero_flow_is_valid() -> None:
    conditions = OperatingConditions(
        flow_rate_m3_s=0.0,
        surface_backpressure_pa=1_500_000.0,
        operating_mode=OperatingMode.CONNECTION,
        max_surface_backpressure_pa=3_447_378.646584,
    )
    assert conditions.operating_mode is OperatingMode.CONNECTION


def test_negative_flow_rejected() -> None:
    with pytest.raises(ValidationError):
        OperatingConditions(
            flow_rate_m3_s=-0.01,
            surface_backpressure_pa=0.0,
            operating_mode=OperatingMode.DRILLING,
        )


def test_pressure_window_requires_increasing_tvd() -> None:
    with pytest.raises(ValidationError, match="strictly increasing"):
        PressureWindow(
            points=[
                PressureWindowPoint(
                    tvd_m=2000.0,
                    pore_pressure_pa=24_000_000.0,
                    fracture_pressure_pa=36_000_000.0,
                ),
                PressureWindowPoint(
                    tvd_m=1500.0,
                    pore_pressure_pa=18_000_000.0,
                    fracture_pressure_pa=27_000_000.0,
                ),
            ]
        )


def test_valid_pressure_window() -> None:
    window = PressureWindow(
        points=[
            PressureWindowPoint(
                tvd_m=1000.0,
                pore_pressure_pa=12_000_000.0,
                fracture_pressure_pa=18_000_000.0,
                collapse_pressure_pa=13_000_000.0,
            ),
            PressureWindowPoint(
                tvd_m=3000.0,
                pore_pressure_pa=36_000_000.0,
                fracture_pressure_pa=54_000_000.0,
                collapse_pressure_pa=38_000_000.0,
            ),
        ]
    )
    assert len(window.points) == 2
