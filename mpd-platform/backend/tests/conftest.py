"""Pytest environment for the FastAPI suite.

DATABASE_URL is set before the application is imported so tests never
require a running PostgreSQL instance. Production still uses POSTGRES_*
or DATABASE_URL.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Isolated TestClient with a fresh in-memory schema per test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
