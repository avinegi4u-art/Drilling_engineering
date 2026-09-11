"""Domain-model validation tests. No hydraulics equations are exercised here."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from mpd_engine.models.case import HydraulicsCase
from mpd_engine.models.drillstring import Drillstring, DrillstringComponentType, DrillstringSegment
from mpd_engine.models.fluids import FluidProperties, RheologyModel
from mpd_engine.models.operating_conditions import OperatingConditions, OperatingMode
from mpd_engine.models.pressure_window import PressureWindowCurve, PressureWindowPoint
from mpd_engine.models.well import AnnularSectionType, TrajectoryStation, Well, WellSection
from tests.factories import example_vertical_well_case

SAMPLE_WELL_PATH = (
    Path(__file__).resolve().parents[2] / "examples" / "sample_well.json"
)


def test_example_case_is_valid() -> None:
    case = example_vertical_well_case()
    assert case.well.total_depth_tvd_m == 3000.0
    assert case.drillstring.total_length_m == 3000.0
    assert case.well.sections[0].annular_outer_diameter_m == 0.2159


def test_sample_well_json_loads() -> None:
    payload = json.loads(SAMPLE_WELL_PATH.read_text(encoding="utf-8"))
    case = HydraulicsCase.model_validate(payload)
    assert case.well.name == "Example Vertical Well A"
    assert case.fluid.rheology_model is RheologyModel.BINGHAM_PLASTIC


def test_negative_dimensions_rejected() -> None:
    with pytest.raises(ValidationError):
        TrajectoryStation(md_m=-1.0, tvd_m=0.0)
    with pytest.raises(ValidationError):
        FluidProperties(
            mud_density_kg_m3=-1.0,
            plastic_viscosity_pa_s=0.02,
            yield_stress_pa=1.0,
        )
    with pytest.raises(ValidationError):
        OperatingConditions(
            flow_rate_m3_s=-0.01,
            surface_backpressure_pa=0.0,
            operating_mode=OperatingMode.DRILLING,
        )


def test_nan_and_infinite_values_rejected() -> None:
    with pytest.raises(ValidationError):
        FluidProperties(
            mud_density_kg_m3=math.nan,
            plastic_viscosity_pa_s=0.02,
            yield_stress_pa=1.0,
        )
    with pytest.raises(ValidationError):
        OperatingConditions(
            flow_rate_m3_s=0.02,
            surface_backpressure_pa=math.inf,
            operating_mode=OperatingMode.DRILLING,
        )


def test_tvd_greater_than_md_rejected() -> None:
    with pytest.raises(ValidationError, match="must not be greater"):
        TrajectoryStation(md_m=1000.0, tvd_m=1001.0)


def test_non_monotonic_trajectory_rejected() -> None:
    with pytest.raises(ValidationError, match="strictly increasing"):
        Well(
            name="bad trajectory",
            trajectory=[
                TrajectoryStation(md_m=0.0, tvd_m=0.0),
                TrajectoryStation(md_m=1000.0, tvd_m=1000.0),
                TrajectoryStation(md_m=900.0, tvd_m=900.0),
            ],
            sections=[
                WellSection(
                    name="OH",
                    top_md_m=0.0,
                    bottom_md_m=1000.0,
                    top_tvd_m=0.0,
                    bottom_tvd_m=1000.0,
                    hole_id_m=0.2159,
                    annular_section_type=AnnularSectionType.OPEN_HOLE,
                )
            ],
        )


def test_casing_section_requires_casing_id() -> None:
    with pytest.raises(ValidationError, match="casing_id_m is required"):
        WellSection(
            name="9-5/8 casing",
            top_md_m=0.0,
            bottom_md_m=1500.0,
            top_tvd_m=0.0,
            bottom_tvd_m=1500.0,
            hole_id_m=0.31115,
            casing_id_m=None,
            annular_section_type=AnnularSectionType.CASING,
        )


def test_pipe_id_must_be_smaller_than_od() -> None:
    with pytest.raises(ValidationError, match="inner_diameter_m"):
        DrillstringSegment(
            component_type=DrillstringComponentType.DRILLPIPE,
            length_m=100.0,
            outer_diameter_m=0.127,
            inner_diameter_m=0.127,
        )


def test_invalid_geometry_pipe_larger_than_hole() -> None:
    case = example_vertical_well_case()
    oversized = Drillstring(
        segments=[
            DrillstringSegment(
                component_type=DrillstringComponentType.BHA,
                length_m=3000.0,
                outer_diameter_m=0.250,
                inner_diameter_m=0.050,
            )
        ]
    )
    with pytest.raises(ValidationError, match="must be greater than"):
        HydraulicsCase(
            well=case.well,
            drillstring=oversized,
            fluid=case.fluid,
            operating=case.operating,
            pressure_window=case.pressure_window,
        )


def test_pressure_window_ordering() -> None:
    with pytest.raises(ValidationError, match="fracture_pressure_pa"):
        PressureWindowPoint(
            tvd_m=1000.0,
            pore_pressure_pa=12_000_000.0,
            collapse_pressure_pa=11_000_000.0,
            fracture_pressure_pa=10_000_000.0,
        )


def test_pressure_window_depths_must_increase() -> None:
    with pytest.raises(ValidationError, match="strictly increasing"):
        PressureWindowCurve(
            points=[
                PressureWindowPoint(
                    tvd_m=1000.0,
                    pore_pressure_pa=1.0e7,
                    collapse_pressure_pa=1.1e7,
                    fracture_pressure_pa=1.6e7,
                ),
                PressureWindowPoint(
                    tvd_m=1000.0,
                    pore_pressure_pa=1.0e7,
                    collapse_pressure_pa=1.1e7,
                    fracture_pressure_pa=1.6e7,
                ),
            ]
        )


def test_unimplemented_rheology_rejected() -> None:
    with pytest.raises(ValidationError, match="not implemented"):
        FluidProperties(
            mud_density_kg_m3=1200.0,
            plastic_viscosity_pa_s=0.02,
            yield_stress_pa=4.0,
            rheology_model=RheologyModel.POWER_LAW,
        )


def test_connection_mode_requires_zero_flow() -> None:
    with pytest.raises(ValidationError, match="flow_rate_m3_s"):
        OperatingConditions(
            flow_rate_m3_s=0.02,
            surface_backpressure_pa=1.5e6,
            operating_mode=OperatingMode.CONNECTION,
        )
    conditions = OperatingConditions(
        flow_rate_m3_s=0.0,
        surface_backpressure_pa=1.5e6,
        operating_mode=OperatingMode.PUMP_OFF,
    )
    assert conditions.flow_rate_m3_s == 0.0


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        FluidProperties.model_validate(
            {
                "mud_density_kg_m3": 1200.0,
                "plastic_viscosity_pa_s": 0.02,
                "yield_stress_pa": 4.0,
                "unexpected": True,
            }
        )


def test_missing_required_fluid_fields() -> None:
    with pytest.raises(ValidationError):
        FluidProperties.model_validate({"mud_density_kg_m3": 1200.0})
