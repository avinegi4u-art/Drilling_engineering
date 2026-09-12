"""Health endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str


router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return service liveness. No authentication in version 1."""
    return HealthResponse(status="ok")
