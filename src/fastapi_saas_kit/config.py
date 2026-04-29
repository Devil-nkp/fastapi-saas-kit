"""
fastapi-saas-kit — Application Configuration
Uses Pydantic Settings for type-safe environment variable management.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration. All values loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────
    APP_NAME: str = "My SaaS App"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # ── Admin ────────────────────────────────────────
    ADMIN_EMAIL: str = Field(default="", description="Platform admin email for override access")

    # ── Database ─────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/saas_kit",
        description="PostgreSQL connection string",
    )
    DB_POOL_MIN_SIZE: int = Field(default=2, description="asyncpg pool minimum connections")
    DB_POOL_MAX_SIZE: int = Field(default=10, description="asyncpg pool maximum connections")

    # ── Auth Provider ────────────────────────────────
    AUTH_PROVIDER: str = Field(default="mock", description="Auth provider: 'mock' or 'jwt'")
    AUTH_JWT_SECRET: str = Field(default="change-me-in-production", description="JWT signing secret")
    AUTH_JWT_ALGORITHM: str = "HS256"
    AUTH_JWT_EXPIRY_MINUTES: int = 60

    # ── Cache Provider ───────────────────────────────
    CACHE_PROVIDER: str = Field(default="memory", description="Cache provider: 'memory' or 'redis'")

    # ── Rate Limiting ────────────────────────────────
    RATE_LIMIT_ANONYMOUS: int = 30
    RATE_LIMIT_AUTHENTICATED: int = 60

    # ── Billing Provider ─────────────────────────────
    BILLING_PROVIDER: str = Field(default="mock", description="Billing provider: 'mock' or 'stripe'")

    # ── Validators ───────────────────────────────────
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized = value.lower().strip()
        allowed = {"development", "production", "staging", "testing"}
        if normalized not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @field_validator("FRONTEND_URL", "BACKEND_URL")
    @classmethod
    def normalize_urls(cls, value: str) -> str:
        return value.rstrip("/") if value else value

    @field_validator("RATE_LIMIT_ANONYMOUS", "RATE_LIMIT_AUTHENTICATED", "DB_POOL_MIN_SIZE", "DB_POOL_MAX_SIZE")
    @classmethod
    def validate_positive_ints(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Value must be >= 0")
        return value

    @field_validator("AUTH_JWT_EXPIRY_MINUTES")
    @classmethod
    def validate_expiry(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("AUTH_JWT_EXPIRY_MINUTES must be > 0")
        return value


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
