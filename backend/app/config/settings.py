"""
Sentinel AI — Application Settings

All configuration is driven by environment variables with sensible defaults.
Uses Pydantic Settings for type-safe, validated configuration.
"""

from functools import lru_cache
from typing import Any, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "Sentinel AI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "Industrial Data Quality & Pipeline Observability Platform"
    )
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── Server ───────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://sentinel:sentinel_secret@localhost:5432/sentinel_ai",
        description="Async PostgreSQL connection string",
    )
    DB_POOL_SIZE: int = Field(default=20, ge=1, le=100)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=5)
    DB_ECHO: bool = False

    # ── Redis & Background Worker ────────────────────────────────────────
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for distributed job queues",
    )
    REDIS_QUEUE_NAME: str = "sentinel_jobs"
    WORKER_POLL_INTERVAL_SECONDS: float = Field(default=1.0, ge=0.1)
    WORKER_JOB_TIMEOUT_SECONDS: int = Field(default=300, ge=1)

    # ── JWT Authentication & Secrets ──────────────────────────────────────
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-minimum-32-characters-long",
        description="Secret key for security. Must be at least 32 characters.",
    )
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-minimum-32-characters-long",
        description="Secret key for JWT encoding.",
    )
    JWT_SECRET: str = Field(
        default="dev-secret-key-change-in-production-minimum-32-characters-long",
        description="Secret key alias for JWT encoding.",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, ge=1)

    # ── Security & Middleware ────────────────────────────────────────────
    CORS_ORIGINS: Any = ["http://localhost:3000", "http://127.0.0.1:3000"]
    TRUSTED_HOSTS: list[str] = ["localhost", "127.0.0.1", "backend", "test", "testserver", "*.onrender.com", "*.vercel.app"]
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "backend", "test", "testserver", "*.onrender.com", "*.vercel.app"]

    # ── Rate Limiting ────────────────────────────────────────────────────
    AUTH_RATE_LIMIT: str = "5/minute"

    # ── Initial Admin ────────────────────────────────────────────────────
    FIRST_ADMIN_EMAIL: str = "admin@sentinel-ai.io"
    FIRST_ADMIN_PASSWORD: str = Field(
        default="ChangeMe123!",
        min_length=8,
        description="Initial admin password. Change immediately in production.",
    )
    FIRST_ADMIN_FULL_NAME: str = "System Administrator"

    # ── AI Integration ───────────────────────────────────────────────────
    OPENAI_API_KEY: str | None = None

    # ── Logging ──────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ── Computed ─────────────────────────────────────────────────────────
    @property
    def cors_origins_list(self) -> list[str]:
        if isinstance(self.CORS_ORIGINS, list):
            origins = list(self.CORS_ORIGINS)
        elif isinstance(self.CORS_ORIGINS, str):
            import json
            raw = self.CORS_ORIGINS.strip()
            if raw.startswith("[") and raw.endswith("]"):
                try:
                    origins = json.loads(raw)
                except Exception:
                    origins = [o.strip(" []\"'") for o in raw.split(",") if o.strip(" []\"'")]
            else:
                origins = [o.strip(" []\"'") for o in raw.split(",") if o.strip(" []\"'")]
        else:
            origins = ["http://localhost:3000"]

        dev_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"]
        for dev_o in dev_origins:
            if dev_o not in origins:
                origins.append(dev_o)
        return origins

    @property
    def allowed_hosts_list(self) -> list[str]:
        if isinstance(self.ALLOWED_HOSTS, list):
            hosts = list(self.ALLOWED_HOSTS)
        elif isinstance(self.ALLOWED_HOSTS, str):
            import json
            raw = self.ALLOWED_HOSTS.strip()
            if raw.startswith("[") and raw.endswith("]"):
                try:
                    hosts = json.loads(raw)
                except Exception:
                    hosts = [h.strip(" []\"'") for h in raw.split(",") if h.strip(" []\"'")]
            else:
                hosts = [h.strip(" []\"'") for h in raw.split(",") if h.strip(" []\"'")]
        else:
            hosts = ["*"]
        if "localhost" not in hosts:
            hosts.append("localhost")
        if "127.0.0.1" not in hosts:
            hosts.append("127.0.0.1")
        if "test" not in hosts:
            hosts.append("test")
        if "testserver" not in hosts:
            hosts.append("testserver")
        if "*" not in hosts and self.is_development:
            hosts.append("*")
        return hosts

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in ("production", "prod")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
