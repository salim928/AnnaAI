"""AnnaAi settings — Pydantic v2 BaseSettings."""
from __future__ import annotations

import logging
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application --------------------------------------------------------
    APP_NAME: str = "AnnaAi"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    SECRET_KEY: str = ""
    ENCRYPTION_KEY: str = ""  # 32-byte urlsafe Fernet key

    # --- Supabase -----------------------------------------------------------
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_DB_URL: str = ""

    # --- Anthropic ----------------------------------------------------------
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 4096

    # --- Embeddings ---------------------------------------------------------
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # --- Resend -------------------------------------------------------------
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "anna@annaai.app"
    RESEND_FROM_NAME: str = "Anna · AnnaAi"

    # --- URLs ---------------------------------------------------------------
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # --- Google OAuth -------------------------------------------------------
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # --- Image generation ---------------------------------------------------
    POLLINATIONS_BASE_URL: str = "https://image.pollinations.ai/prompt"
    POLLINATIONS_WIDTH: int = 1200
    POLLINATIONS_HEIGHT: int = 630

    # --- Redis --------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379"

    # --- Scheduler ----------------------------------------------------------
    SCHEDULER_SECRET: str = ""

    # --- Scraping -----------------------------------------------------------
    SCRAPE_MAX_PAGES: int = 20
    SCRAPE_TIMEOUT_SECONDS: int = 30

    # --- Plan limits --------------------------------------------------------
    MAX_RUNS_PER_DAY_FREE: int = 1
    MAX_DRAFTS_PER_RUN_FREE: int = 3
    MAX_DRAFTS_PER_RUN_PRO: int = 10

    # --- Paystack (Batch 6) -------------------------------------------------
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""

    # --- Sentry -------------------------------------------------------------
    SENTRY_DSN: str = ""  # leave empty to disable error tracking

    # --- CORS ---------------------------------------------------------------
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8000",
        ]
    )

    # --- Derived helpers ----------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def cors_origins(self) -> list[str]:
        origins = list(self.CORS_ORIGINS)
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins

    # --- Validation ---------------------------------------------------------
    @model_validator(mode="after")
    def _validate(self) -> "Settings":
        if self.is_production:
            missing = []
            if not self.SUPABASE_URL:
                missing.append("SUPABASE_URL")
            if not self.SUPABASE_SERVICE_ROLE_KEY:
                missing.append("SUPABASE_SERVICE_ROLE_KEY")
            if not self.ANTHROPIC_API_KEY:
                missing.append("ANTHROPIC_API_KEY")
            if not self.SECRET_KEY:
                missing.append("SECRET_KEY")
            if not self.ENCRYPTION_KEY:
                missing.append("ENCRYPTION_KEY")
            if not self.SCHEDULER_SECRET:
                missing.append("SCHEDULER_SECRET")
            if missing:
                raise ValueError(
                    f"Required env vars missing in production: {', '.join(missing)}"
                )
        else:
            if not self.SECRET_KEY:
                logger.warning("SECRET_KEY is empty — JWT signature verification disabled (dev only)")
            if not self.ENCRYPTION_KEY:
                logger.warning("ENCRYPTION_KEY is empty — OAuth token encryption disabled (dev only)")
        return self


settings = Settings()
