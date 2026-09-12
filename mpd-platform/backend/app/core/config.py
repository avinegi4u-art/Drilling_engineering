"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. No secrets are hardcoded."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MPD Hydraulics API"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./mpd.db"
    created_by_placeholder: str = "engineer"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings object."""
    return Settings()
