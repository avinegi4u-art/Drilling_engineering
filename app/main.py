"""FastAPI application exposing drilling-engineering calculators.

The service serves a small single-page frontend from ``app/static`` and a JSON
API under ``/api`` that wraps the pure functions in :mod:`app.calculations`.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__, calculations

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Drilling Engineering Toolkit",
    version=__version__,
    description="A collection of common drilling-engineering calculators.",
)


class HydrostaticRequest(BaseModel):
    mud_weight_ppg: float = Field(..., gt=0, examples=[9.5])
    tvd_ft: float = Field(..., ge=0, examples=[10000])


class ECDRequest(BaseModel):
    mud_weight_ppg: float = Field(..., gt=0, examples=[9.5])
    annular_pressure_loss_psi: float = Field(..., ge=0, examples=[250])
    tvd_ft: float = Field(..., gt=0, examples=[10000])


class BuoyancyRequest(BaseModel):
    mud_weight_ppg: float = Field(..., ge=0, examples=[12.0])


class AnnularVelocityRequest(BaseModel):
    flow_rate_gpm: float = Field(..., gt=0, examples=[500])
    hole_diameter_in: float = Field(..., gt=0, examples=[8.5])
    pipe_diameter_in: float = Field(..., gt=0, examples=[5.0])


class DoglegRequest(BaseModel):
    inclination_1_deg: float = Field(..., examples=[15.0])
    azimuth_1_deg: float = Field(..., examples=[20.0])
    inclination_2_deg: float = Field(..., examples=[25.0])
    azimuth_2_deg: float = Field(..., examples=[45.0])
    course_length_ft: float = Field(..., gt=0, examples=[100.0])


class KillMudRequest(BaseModel):
    current_mud_weight_ppg: float = Field(..., gt=0, examples=[9.5])
    sidpp_psi: float = Field(..., ge=0, examples=[300])
    tvd_ft: float = Field(..., gt=0, examples=[10000])


class ResultResponse(BaseModel):
    value: float
    unit: str


def _compute(func, unit: str, **kwargs) -> ResultResponse:
    try:
        return ResultResponse(value=round(func(**kwargs), 4), unit=unit)
    except ValueError as exc:  # domain validation errors
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.post("/api/hydrostatic-pressure", response_model=ResultResponse)
def api_hydrostatic_pressure(req: HydrostaticRequest) -> ResultResponse:
    return _compute(
        calculations.hydrostatic_pressure,
        "psi",
        mud_weight_ppg=req.mud_weight_ppg,
        tvd_ft=req.tvd_ft,
    )


@app.post("/api/ecd", response_model=ResultResponse)
def api_ecd(req: ECDRequest) -> ResultResponse:
    return _compute(
        calculations.equivalent_circulating_density,
        "ppg",
        mud_weight_ppg=req.mud_weight_ppg,
        annular_pressure_loss_psi=req.annular_pressure_loss_psi,
        tvd_ft=req.tvd_ft,
    )


@app.post("/api/buoyancy-factor", response_model=ResultResponse)
def api_buoyancy_factor(req: BuoyancyRequest) -> ResultResponse:
    return _compute(
        calculations.buoyancy_factor,
        "dimensionless",
        mud_weight_ppg=req.mud_weight_ppg,
    )


@app.post("/api/annular-velocity", response_model=ResultResponse)
def api_annular_velocity(req: AnnularVelocityRequest) -> ResultResponse:
    return _compute(
        calculations.annular_velocity,
        "ft/min",
        flow_rate_gpm=req.flow_rate_gpm,
        hole_diameter_in=req.hole_diameter_in,
        pipe_diameter_in=req.pipe_diameter_in,
    )


@app.post("/api/dogleg-severity", response_model=ResultResponse)
def api_dogleg_severity(req: DoglegRequest) -> ResultResponse:
    return _compute(
        calculations.dogleg_severity,
        "deg/100ft",
        inclination_1_deg=req.inclination_1_deg,
        azimuth_1_deg=req.azimuth_1_deg,
        inclination_2_deg=req.inclination_2_deg,
        azimuth_2_deg=req.azimuth_2_deg,
        course_length_ft=req.course_length_ft,
    )


@app.post("/api/kill-mud-weight", response_model=ResultResponse)
def api_kill_mud_weight(req: KillMudRequest) -> ResultResponse:
    return _compute(
        calculations.kill_mud_weight,
        "ppg",
        current_mud_weight_ppg=req.current_mud_weight_ppg,
        sidpp_psi=req.sidpp_psi,
        tvd_ft=req.tvd_ft,
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# Serve static assets (CSS/JS) under /static.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
