"""Settings and structured-error helpers. No live PostgreSQL required."""

from __future__ import annotations

from app.core.config import Settings
from app.core.errors import error_body


def test_database_url_overrides_postgres_parts(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("POSTGRES_HOST", "ignored")
    settings = Settings(_env_file=None)
    assert settings.sqlalchemy_database_url == "sqlite:///:memory:"


def test_postgres_url_from_environment_parts(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_USER", "eng")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p@ss")
    monkeypatch.setenv("POSTGRES_HOST", "db.internal")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("POSTGRES_DB", "hydraulics")
    settings = Settings(_env_file=None)
    assert (
        settings.sqlalchemy_database_url
        == "postgresql+psycopg2://eng:p%40ss@db.internal:5433/hydraulics"
    )


def test_error_body_envelope() -> None:
    assert error_body("NOT_FOUND", "Well not found") == {
        "error": {"code": "NOT_FOUND", "message": "Well not found"}
    }
