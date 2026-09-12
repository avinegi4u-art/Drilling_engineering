"""FastAPI application entrypoint.

Hydraulics equations live in ``mpd_engine``. This module only exposes HTTP
routes, validation, persistence, and logging.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import (
    calculations_router,
    health_router,
    reports_router,
    scenarios_router,
    wells_router,
)
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging import configure_logging
from app.db import models as _models  # noqa: F401  (register ORM mappers)

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("mpd.api")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create tables when Alembic has not been applied (SQLite / local)."""
    Base.metadata.create_all(bind=engine)
    logger.info("API started with database %s", settings.database_url.split("@")[-1])
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    description=(
        "Managed Pressure Drilling hydraulics API for engineering decision "
        "support. Version 1 does not authenticate callers, does not queue "
        "background jobs, and does not send commands to field equipment."
    ),
)


@app.middleware("http")
async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    logger.info("%s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
    return response


@app.exception_handler(StarletteHTTPException)
async def http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": exc.detail}},
    )


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": exc.errors()}},
    )


app.include_router(health_router)
app.include_router(wells_router)
app.include_router(scenarios_router)
app.include_router(calculations_router)
app.include_router(reports_router)
