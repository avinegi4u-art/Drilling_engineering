"""Export endpoints for completed calculation runs.

CSV, Excel, and PDF bytes are produced by ``mpd_engine.results``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from mpd_engine.results.export import result_to_csv, result_to_excel_bytes
from mpd_engine.results.pdf import result_to_pdf_bytes
from mpd_engine.results.result_models import CalculationResult
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import conflict, not_found
from app.db import repositories

router = APIRouter(prefix="/api/v1", tags=["reports"])


def _load_result(session: Session, run_id: str) -> CalculationResult:
    run = repositories.get_run(session, run_id)
    if run is None:
        not_found("Run")
    if run.result is None:
        conflict("Run has no result to export")
    return CalculationResult.model_validate(run.result.result_json)


@router.post("/runs/{run_id}/export/csv")
def export_csv(run_id: str, session: Session = Depends(get_db)) -> Response:
    """Download the depth profile as CSV."""
    payload = result_to_csv(_load_result(session, run_id))
    return Response(
        content=payload,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="run-{run_id}.csv"'},
    )


@router.post("/runs/{run_id}/export/excel")
def export_excel(run_id: str, session: Session = Depends(get_db)) -> Response:
    """Download summary, profile, warnings, and assumptions as .xlsx."""
    payload = result_to_excel_bytes(_load_result(session, run_id))
    return Response(
        content=payload,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="run-{run_id}.xlsx"'},
    )


@router.post("/runs/{run_id}/export/pdf")
def export_pdf(run_id: str, session: Session = Depends(get_db)) -> Response:
    """Download a basic PDF engineering-review report."""
    payload = result_to_pdf_bytes(_load_result(session, run_id))
    return Response(
        content=payload,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="run-{run_id}.pdf"'},
    )
