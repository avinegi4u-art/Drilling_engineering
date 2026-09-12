"""HTTP routers."""

from app.api.calculations import router as calculations_router
from app.api.health import router as health_router
from app.api.reports import router as reports_router
from app.api.scenarios import router as scenarios_router
from app.api.wells import router as wells_router

__all__ = [
    "calculations_router",
    "health_router",
    "reports_router",
    "scenarios_router",
    "wells_router",
]
