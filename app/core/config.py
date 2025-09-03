from __future__ import annotations

"""Application configuration via environment variables (.env)."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings loaded from `.env` or process environment.

    Unknown environment variables are ignored to allow compose-only variables
    (e.g., POSTGRES_DB) to coexist without validation errors.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="ignore",  # ignore unknown env vars (e.g., compose-only vars)
    )

    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./app.db")
    SYNC_DATABASE_URL: str | None = Field(default=None)
    JWT_SECRET: str = Field(default="change_me")
    ACCESS_TOKEN_TTL: int = Field(default=3600, ge=300, le=24 * 3600)
    # Messaging (RabbitMQ)
    RABBITMQ_URL: str = Field(default="amqp://guest:guest@rabbitmq:5672//")
    # Optional: prevent duplicate improvements for same resume/content
    IMPROVEMENT_DEDUP_ENABLED: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # Celery/testing
    CELERY_TASK_ALWAYS_EAGER: bool = Field(default=False)

    # API base path
    API_PREFIX: str = Field(default="/api/v1")


@lru_cache
def get_settings() -> Settings:
    """Create and cache a `Settings` instance."""
    return Settings()  # type: ignore[arg-type]


settings = get_settings()
