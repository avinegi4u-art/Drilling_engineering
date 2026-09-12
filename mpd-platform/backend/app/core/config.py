"""Application settings loaded from environment variables."""

from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Secrets come from the environment, not source.

    Database resolution order:
    1. ``DATABASE_URL`` if set (tests, Docker Compose, local SQLite).
    2. Otherwise a PostgreSQL URL built from ``POSTGRES_*``.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MPD Hydraulics API"
    log_level: str = "INFO"
    created_by_placeholder: str = "engineer"

    database_url: str | None = Field(default=None, description="Optional full SQLAlchemy URL.")

    postgres_user: str = "mpd"
    postgres_password: str = "mpd"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "mpd"

    @property
    def sqlalchemy_database_url(self) -> str:
        """Return DATABASE_URL, or a PostgreSQL URL built from POSTGRES_*."""
        if self.database_url:
            return self.database_url
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+psycopg2://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings object."""
    return Settings()
