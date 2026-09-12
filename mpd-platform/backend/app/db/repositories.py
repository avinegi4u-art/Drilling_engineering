"""Persistence helpers."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    CalculationResultRow,
    CalculationRun,
    FluidProgram,
    PressureWindow,
    Scenario,
    Well,
    WellSection,
)


def get_well(session: Session, well_id: str) -> Well | None:
    return session.get(Well, well_id)


def list_wells(session: Session) -> list[Well]:
    return list(session.scalars(select(Well).order_by(Well.created_at.desc())))


def add_well(
    session: Session,
    *,
    name: str,
    created_by: str,
    well_json: dict[str, Any],
    sections: list[dict[str, Any]],
) -> Well:
    well = Well(name=name, created_by=created_by, well_json=well_json)
    session.add(well)
    session.flush()
    for section in sections:
        session.add(WellSection(well_id=well.id, **section))
    return well


def add_scenario(
    session: Session,
    *,
    well: Well,
    name: str,
    created_by: str,
    inputs_json: dict[str, Any],
    fluid_payload: dict[str, Any],
    window_points: list[dict[str, Any]],
) -> Scenario:
    session.add(
        FluidProgram(
            well_id=well.id,
            mud_density_kg_m3=fluid_payload["mud_density_kg_m3"],
            plastic_viscosity_pa_s=fluid_payload["plastic_viscosity_pa_s"],
            yield_stress_pa=fluid_payload["yield_stress_pa"],
            temperature_c=fluid_payload["temperature_c"],
            rheology_model=fluid_payload["rheology_model"],
            payload_json=fluid_payload,
        )
    )
    session.add(PressureWindow(well_id=well.id, points_json=window_points))
    scenario = Scenario(
        well_id=well.id,
        name=name,
        created_by=created_by,
        inputs_json=inputs_json,
    )
    session.add(scenario)
    session.flush()
    return scenario


def get_scenario(session: Session, scenario_id: str) -> Scenario | None:
    return session.get(Scenario, scenario_id)


def list_scenarios_for_well(session: Session, well_id: str) -> list[Scenario]:
    return list(
        session.scalars(
            select(Scenario).where(Scenario.well_id == well_id).order_by(Scenario.created_at.desc())
        )
    )


def list_runs(session: Session) -> list[CalculationRun]:
    return list(session.scalars(select(CalculationRun).order_by(CalculationRun.created_at.desc())))


def get_run(session: Session, run_id: str) -> CalculationRun | None:
    return session.get(CalculationRun, run_id)


def add_run(
    session: Session,
    *,
    scenario: Scenario,
    calculation_version: str,
    created_by: str,
    assumptions: list[str],
    inputs_json: dict[str, Any],
) -> CalculationRun:
    run = CalculationRun(
        scenario_id=scenario.id,
        status="pending",
        calculation_version=calculation_version,
        created_by=created_by,
        assumptions_json=assumptions,
        inputs_json=inputs_json,
    )
    session.add(run)
    session.flush()
    return run


def complete_run(
    session: Session,
    run: CalculationRun,
    *,
    result_json: dict[str, Any],
) -> CalculationResultRow:
    run.status = "completed"
    row = CalculationResultRow(
        run_id=run.id,
        summary_json=result_json["summary"],
        profile_json=result_json["profile"],
        warnings_json=result_json["warnings"],
        connection_json=result_json.get("connection"),
        result_json=result_json,
    )
    session.add(row)
    session.flush()
    return row


def fail_run(session: Session, run: CalculationRun, message: str) -> None:
    run.status = "failed"
    run.error_message = message
