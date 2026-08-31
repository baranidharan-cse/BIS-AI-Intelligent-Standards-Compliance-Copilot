"""
Centralized configuration via environment variables.
All secrets and environment-specific settings live here.
No hardcoded values — use .env.example as a reference for required variables.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "Study Buddy"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ── Database ─────────────────────────────────────────────────────────────
    # SQLite by default; swap to postgresql+asyncpg://... for Postgres.
    DATABASE_URL: str = "sqlite+aiosqlite:///./study_buddy.db"

    # ── LLM Provider ─────────────────────────────────────────────────────────
    # Supported values: "demo" | "watsonx"
    # Use "demo" during development; switch to "watsonx" for production.
    LLM_PROVIDER: str = "demo"

    # ── watsonx.ai credentials (required when LLM_PROVIDER=watsonx) ──────────
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    WATSONX_MODEL_ID: str = "ibm/granite-13b-instruct-v2"

    # ── CORS ──────────────────────────────────────────────────────────────────
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
