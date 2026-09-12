"""Scenario endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from mpd_engine.models.well import Well as DomainWell
from mpd_engine.services.calculation_service import HydraulicsCase
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db import repositories
from app.schemas.scenarios import ScenarioCreate, ScenarioRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["scenarios"])


@router.post(
    "/wells/{well_id}/scenarios",
    response_model=ScenarioRead,
    status_code=status.HTTP_201_CREATED,
)
def create_scenario(
    well_id: str,
    payload: ScenarioCreate,
    session: Session = Depends(get_db),
) -> ScenarioRead:
    """Attach a hydraulics scenario to a well. Inputs are validated by the engine."""
    well_row = repositories.get_well(session, well_id)
    if well_row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Well not found")
    try:
        domain_well = DomainWell.model_validate(well_row.well_json)
        HydraulicsCase(
            well=domain_well,
            drillstring=payload.drillstring,
            fluid=payload.fluid,
            operating=payload.operating,
            pressure_window=payload.pressure_window,
            target_bottomhole_pressure_pa=payload.target_bottomhole_pressure_pa,
            depth_step_m=payload.depth_step_m,
        )
    except (ValueError, ValidationError) as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    inputs = {
        "well": well_row.well_json,
        "drillstring": payload.drillstring.model_dump(mode="json"),
        "fluid": payload.fluid.model_dump(mode="json"),
        "operating": payload.operating.model_dump(mode="json"),
        "pressure_window": payload.pressure_window.model_dump(mode="json"),
        "target_bottomhole_pressure_pa": payload.target_bottomhole_pressure_pa,
        "depth_step_m": payload.depth_step_m,
    }
    record = repositories.add_scenario(
        session,
        well=well_row,
        name=payload.name,
        created_by=payload.created_by,
        inputs_json=inputs,
        fluid_payload=payload.fluid.model_dump(mode="json"),
        window_points=payload.pressure_window.model_dump(mode="json")["points"],
    )
    session.commit()
    logger.info("Created scenario %s for well %s", record.id, well_id)
    return ScenarioRead(
        id=record.id,
        well_id=record.well_id,
        name=record.name,
        created_by=record.created_by,
        created_at=record.created_at,
        inputs=record.inputs_json,
    )


@router.get("/wells/{well_id}/scenarios", response_model=list[ScenarioRead])
def list_well_scenarios(well_id: str, session: Session = Depends(get_db)) -> list[ScenarioRead]:
    well_row = repositories.get_well(session, well_id)
    if well_row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Well not found")
    return [
        ScenarioRead(
            id=item.id,
            well_id=item.well_id,
            name=item.name,
            created_by=item.created_by,
            created_at=item.created_at,
            inputs=item.inputs_json,
        )
        for item in repositories.list_scenarios_for_well(session, well_id)
    ]


@router.get("/scenarios/{scenario_id}", response_model=ScenarioRead)
def get_scenario(scenario_id: str, session: Session = Depends(get_db)) -> ScenarioRead:
    """Return one scenario including stored inputs."""
    record = repositories.get_scenario(session, scenario_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return ScenarioRead(
        id=record.id,
        well_id=record.well_id,
        name=record.name,
        created_by=record.created_by,
        created_at=record.created_at,
        inputs=record.inputs_json,
    )
