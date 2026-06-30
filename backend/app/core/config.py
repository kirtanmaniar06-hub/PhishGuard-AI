"""
PhishGuard AI — Core Configuration

Centralized settings management using pydantic-settings.
All values are loaded from environment variables or .env file.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────
    APP_NAME: str = "PhishGuard AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Server ───────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/phishguard_db"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Security / JWT ───────────────────────────────────
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ─────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # ── Admin Seed ───────────────────────────────────────
    FIRST_ADMIN_EMAIL: str = "admin@phishguard.ai"
    FIRST_ADMIN_PASSWORD: str = "ChangeMe@2025!"
    FIRST_ADMIN_USERNAME: str = "superadmin"

    # ── Logging ──────────────────────────────────────────
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "logs/phishguard.log"

    # ── Threat Intelligence API Keys ─────────────────────
    VIRUSTOTAL_API_KEY: str = ""
    URLSCAN_API_KEY: str = ""
    GOOGLE_SAFE_BROWSING_API_KEY: str = ""
    ABUSEIPDB_API_KEY: str = ""

    # ── AI Explanation ───────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # ── Threat Intel Rate Limiting ───────────────────────
    # Max requests per minute per source per worker
    THREAT_INTEL_RATE_LIMIT_PER_MINUTE: int = 10
    THREAT_INTEL_TIMEOUT_SECONDS: int = 8


# Singleton settings instance — import this everywhere
settings = Settings()
