"""Well CRUD endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, status
from mpd_engine.models.well import Well as DomainWell
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import not_found, unprocessable
from app.db import repositories
from app.schemas.wells import WellCreate, WellRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["wells"])


def _domain_well(payload: WellCreate) -> DomainWell:
    if payload.trajectory is not None and payload.sections is not None:
        return DomainWell(
            name=payload.name,
            trajectory=payload.trajectory,
            sections=payload.sections,
        )
    if payload.td_m is None or payload.hole_id_m is None:
        unprocessable(
            "INVALID_GEOMETRY",
            "Provide td_m and hole_id_m for a vertical well, or supply trajectory and sections.",
        )
    try:
        return DomainWell.vertical(
            name=payload.name,
            td_m=payload.td_m,
            hole_id_m=payload.hole_id_m,
            annular_section_type=payload.annular_section_type,
            casing_id_m=payload.casing_id_m,
        )
    except (ValueError, ValidationError) as exc:
        unprocessable("INVALID_GEOMETRY", str(exc))


@router.post("/wells", response_model=WellRead, status_code=status.HTTP_201_CREATED)
def create_well(payload: WellCreate, session: Session = Depends(get_db)) -> WellRead:
    """Create a well and persist its geometry."""
    well = _domain_well(payload)
    dumped = well.model_dump(mode="json")
    sections = [section.model_dump(mode="json") for section in well.sections]
    record = repositories.add_well(
        session,
        name=well.name,
        created_by=payload.created_by,
        well_json=dumped,
        sections=sections,
    )
    session.commit()
    logger.info("Created well %s (%s)", record.id, record.name)
    return WellRead(
        id=record.id,
        name=record.name,
        created_by=record.created_by,
        created_at=record.created_at,
        well=record.well_json,
    )


@router.get("/wells", response_model=list[WellRead])
def list_wells(session: Session = Depends(get_db)) -> list[WellRead]:
    """List wells, newest first."""
    return [
        WellRead(
            id=item.id,
            name=item.name,
            created_by=item.created_by,
            created_at=item.created_at,
            well=item.well_json,
        )
        for item in repositories.list_wells(session)
    ]


@router.get("/wells/{well_id}", response_model=WellRead)
def get_well(well_id: str, session: Session = Depends(get_db)) -> WellRead:
    """Return one well by id."""
    record = repositories.get_well(session, well_id)
    if record is None:
        not_found("Well")
    return WellRead(
        id=record.id,
        name=record.name,
        created_by=record.created_by,
        created_at=record.created_at,
        well=record.well_json,
    )
