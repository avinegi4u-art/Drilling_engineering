"""Calculation run endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from mpd_engine.constants import CALCULATION_VERSION, VERSION_1_ASSUMPTIONS
from mpd_engine.models.drillstring import Drillstring
from mpd_engine.models.fluids import FluidProperties
from mpd_engine.models.operating_conditions import OperatingConditions
from mpd_engine.models.pressure_window import PressureWindow
from mpd_engine.models.well import Well as DomainWell
from mpd_engine.services.calculation_service import HydraulicsCase, run_hydraulics
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db import repositories
from app.schemas.calculations import CalculateRequest, ResultRead, RunRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["calculations"])


def _case_from_inputs(inputs: dict) -> HydraulicsCase:
    return HydraulicsCase(
        well=DomainWell.model_validate(inputs["well"]),
        drillstring=Drillstring.model_validate(inputs["drillstring"]),
        fluid=FluidProperties.model_validate(inputs["fluid"]),
        operating=OperatingConditions.model_validate(inputs["operating"]),
        pressure_window=PressureWindow.model_validate(inputs["pressure_window"]),
        target_bottomhole_pressure_pa=inputs.get("target_bottomhole_pressure_pa"),
        depth_step_m=inputs.get("depth_step_m", 50.0),
    )


@router.post(
    "/scenarios/{scenario_id}/calculate",
    response_model=RunRead,
    status_code=status.HTTP_201_CREATED,
)
def calculate(
    scenario_id: str,
    payload: CalculateRequest | None = None,
    session: Session = Depends(get_db),
) -> RunRead:
    """Run a synchronous version-1 hydraulics calculation and persist the result."""
    request = payload or CalculateRequest()
    scenario = repositories.get_scenario(session, scenario_id)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    run = repositories.add_run(
        session,
        scenario=scenario,
        calculation_version=CALCULATION_VERSION,
        created_by=request.created_by,
        assumptions=list(VERSION_1_ASSUMPTIONS),
        inputs_json=scenario.inputs_json,
    )
    session.flush()
    logger.info("Calculating scenario %s as run %s", scenario_id, run.id)
    try:
        result = run_hydraulics(_case_from_inputs(scenario.inputs_json))
    except (ValueError, ValidationError) as exc:
        repositories.fail_run(session, run, str(exc))
        session.commit()
        logger.exception("Calculation failed for run %s", run.id)
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    repositories.complete_run(session, run, result_json=result.model_dump(mode="json"))
    session.commit()
    logger.info("Completed run %s version %s", run.id, result.calculation_version)
    return RunRead(
        id=run.id,
        scenario_id=run.scenario_id,
        status=run.status,
        calculation_version=run.calculation_version,
        created_by=run.created_by,
        created_at=run.created_at,
        error_message=run.error_message,
        assumptions=run.assumptions_json,
    )


@router.get("/runs", response_model=list[RunRead])
def list_runs(session: Session = Depends(get_db)) -> list[RunRead]:
    """List calculation runs, newest first."""
    return [
        RunRead(
            id=run.id,
            scenario_id=run.scenario_id,
            status=run.status,
            calculation_version=run.calculation_version,
            created_by=run.created_by,
            created_at=run.created_at,
            error_message=run.error_message,
            assumptions=run.assumptions_json,
        )
        for run in repositories.list_runs(session)
    ]


@router.get("/runs/{run_id}", response_model=RunRead)
def get_run(run_id: str, session: Session = Depends(get_db)) -> RunRead:
    """Return calculation-run metadata."""
    run = repositories.get_run(session, run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Run not found")
    return RunRead(
        id=run.id,
        scenario_id=run.scenario_id,
        status=run.status,
        calculation_version=run.calculation_version,
        created_by=run.created_by,
        created_at=run.created_at,
        error_message=run.error_message,
        assumptions=run.assumptions_json,
    )


@router.get("/runs/{run_id}/results", response_model=ResultRead)
def get_results(run_id: str, session: Session = Depends(get_db)) -> ResultRead:
    """Return persisted summary, profile, and warnings."""
    run = repositories.get_run(session, run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.result is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=run.error_message or "Run has no result",
        )
    return ResultRead(
        run_id=run.id,
        status=run.status,
        calculation_version=run.calculation_version,
        assumptions=run.assumptions_json,
        summary=run.result.summary_json,
        profile=run.result.profile_json,
        warnings=run.result.warnings_json,
        connection=run.result.connection_json,
    )
