"""Pressure-window classification and calculation-service tests."""

from __future__ import annotations

import pytest

from mpd_engine.models.drillstring import Drillstring
from mpd_engine.models.fluids import FluidProperties
from mpd_engine.models.operating_conditions import OperatingConditions, OperatingMode
from mpd_engine.models.pressure_window import PressureWindow, PressureWindowPoint
from mpd_engine.models.well import Well
from mpd_engine.mpd.pressure_window import (
    PressureWindowStatus,
    classify_pressure_window,
    interpolate_pressure_window,
)
from mpd_engine.results.export import result_to_csv
from mpd_engine.services.calculation_service import HydraulicsCase, run_hydraulics
from mpd_engine.units.conversions import inch_to_m, lpm_to_m3_s


def _window() -> PressureWindow:
    return PressureWindow(
        points=[
            PressureWindowPoint(
                tvd_m=100.0,
                pore_pressure_pa=1_200_000.0,
                fracture_pressure_pa=1_800_000.0,
                collapse_pressure_pa=1_300_000.0,
            ),
            PressureWindowPoint(
                tvd_m=3000.0,
                pore_pressure_pa=36_000_000.0,
                fracture_pressure_pa=54_000_000.0,
                collapse_pressure_pa=38_000_000.0,
            ),
        ]
    )


def test_window_classification_below_pore() -> None:
    interpolated = interpolate_pressure_window(_window(), 3000.0)
    status, warnings = classify_pressure_window(10_000_000.0, interpolated)
    assert status is PressureWindowStatus.BELOW_PORE_PRESSURE
    assert warnings[0].code == "BELOW_PORE_PRESSURE"


def test_window_classification_above_fracture() -> None:
    interpolated = interpolate_pressure_window(_window(), 3000.0)
    status, warnings = classify_pressure_window(60_000_000.0, interpolated)
    assert status is PressureWindowStatus.ABOVE_FRACTURE_PRESSURE
    assert warnings[0].severity.value == "high"


def test_window_classification_collapse_lower_bound() -> None:
    interpolated = interpolate_pressure_window(_window(), 3000.0)
    # Between pore (36 MPa) and collapse (38 MPa).
    status, warnings = classify_pressure_window(36_500_000.0, interpolated)
    assert status is PressureWindowStatus.ABOVE_COLLAPSE_LIMIT
    assert "below the collapse-pressure" in warnings[0].explanation


def test_window_classification_within() -> None:
    interpolated = interpolate_pressure_window(_window(), 3000.0)
    status, warnings = classify_pressure_window(40_000_000.0, interpolated)
    assert status is PressureWindowStatus.WITHIN_OPERATING_WINDOW
    assert warnings == []


def test_window_tvd_outside_curve_is_invalid() -> None:
    interpolated = interpolate_pressure_window(_window(), 50.0)
    status, warnings = classify_pressure_window(500_000.0, interpolated)
    assert status is PressureWindowStatus.INVALID_INPUT
    assert warnings[0].code == "WINDOW_TVD_OUT_OF_RANGE"


def _case(**operating_kwargs: float | str) -> HydraulicsCase:
    well = Well.vertical("EXAMPLE-1", 3000.0, inch_to_m(12.25))
    drillstring = Drillstring.uniform_drillpipe(
        od_m=inch_to_m(5.0), id_m=inch_to_m(4.276), length_m=3000.0
    )
    fluid = FluidProperties(
        mud_density_kg_m3=1200.0,
        plastic_viscosity_pa_s=0.02,
        yield_stress_pa=9.576,
        temperature_c=50.0,
    )
    operating = OperatingConditions(
        flow_rate_m3_s=float(operating_kwargs.get("flow_rate_m3_s", lpm_to_m3_s(400.0))),
        surface_backpressure_pa=float(operating_kwargs.get("surface_backpressure_pa", 0.0)),
        operating_mode=OperatingMode(str(operating_kwargs.get("operating_mode", "drilling"))),
        max_surface_backpressure_pa=3_447_378.646584,
    )
    return HydraulicsCase(
        well=well,
        drillstring=drillstring,
        fluid=fluid,
        operating=operating,
        pressure_window=_window(),
        target_bottomhole_pressure_pa=40_000_000.0,
        depth_step_m=500.0,
    )


def test_calculation_service_persists_version_and_profile() -> None:
    result = run_hydraulics(_case())
    assert result.calculation_version.startswith("1.0.0")
    assert result.summary.bottomhole_pressure_pa == pytest.approx(
        result.summary.hydrostatic_pressure_pa
        + result.summary.annular_friction_pressure_pa
        + result.summary.surface_backpressure_pa
    )
    assert result.profile[-1].tvd_m == 3000.0
    assert result.connection is not None
    csv_text = result_to_csv(result)
    assert "annular_pressure_pa" in csv_text
    assert "3000.0" in csv_text


def test_pump_off_zero_friction() -> None:
    result = run_hydraulics(
        _case(flow_rate_m3_s=0.0, operating_mode="pump_off", surface_backpressure_pa=1_500_000.0)
    )
    assert result.summary.annular_friction_pressure_pa == 0.0
    assert result.summary.bottomhole_pressure_pa == pytest.approx(
        result.summary.hydrostatic_pressure_pa + 1_500_000.0
    )


def test_short_drillstring_rejected() -> None:
    well = Well.vertical("EXAMPLE-1", 3000.0, inch_to_m(12.25))
    drillstring = Drillstring.uniform_drillpipe(
        od_m=inch_to_m(5.0), id_m=inch_to_m(4.276), length_m=1000.0
    )
    fluid = FluidProperties(
        mud_density_kg_m3=1200.0,
        plastic_viscosity_pa_s=0.02,
        yield_stress_pa=9.576,
        temperature_c=50.0,
    )
    with pytest.raises(ValueError, match="shorter than well TD"):
        HydraulicsCase(
            well=well,
            drillstring=drillstring,
            fluid=fluid,
            operating=OperatingConditions(
                flow_rate_m3_s=lpm_to_m3_s(400.0),
                surface_backpressure_pa=0.0,
                operating_mode=OperatingMode.DRILLING,
            ),
            pressure_window=_window(),
        )
