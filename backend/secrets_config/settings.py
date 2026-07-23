"""C1 Settings + get_settings — the SEC-3 single source, fail-closed at construction.

A Pydantic-v2 `BaseSettings` over the six Phase-1 required env-var shapes. Every field
is **required (no default)** — a missing var raises "field required"; per-field
validators reject an invalid value (non-`postgresql://` URL, or empty/whitespace
secret). Both surface as a single `ValidationError` **at `Settings()` construction**
(BR-SEC-1 fail-closed).

`get_settings()` is a **plain factory** (no cache) — construction stays a pure,
deterministic validation step (DET-1; no module-global mutable state); the composition
root holds the single instance. **No credential VALUE is declared here** — values come
from the environment (SEC-3). **No LLM.** This module imports no consumer / `database`
module (dependency leaf).
"""
from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.secrets_config.url_validation import is_postgres_url


class Settings(BaseSettings):
    """The six Phase-1 required credential/URL shapes (values sourced from env)."""

    model_config = SettingsConfigDict(
        env_file=".env",              # optional dev convenience; gitignored, never committed
        env_file_encoding="utf-8",
        case_sensitive=True,          # env var name == field name exactly
        extra="ignore",              # Phase-2 / unrelated env vars are ignored, not errors
    )

    DATABASE_URL: str
    AUDIT_WRITER_URL: str
    AUDIT_READER_URL: str
    AUDIT_WRITER_PASSWORD: str
    AUDIT_READER_PASSWORD: str
    GEMINI_API_KEY: str

    @field_validator("DATABASE_URL", "AUDIT_WRITER_URL", "AUDIT_READER_URL")
    @classmethod
    def _require_postgres_scheme(cls, value: str) -> str:
        if not is_postgres_url(value):
            raise ValueError("must be a postgresql backend URL (DATA-5)")
        return value

    @field_validator("AUDIT_WRITER_PASSWORD", "AUDIT_READER_PASSWORD", "GEMINI_API_KEY")
    @classmethod
    def _require_non_empty(cls, value: str) -> str:
        if value is None or value.strip() == "":
            raise ValueError("must be a non-empty secret")
        return value


def get_settings() -> Settings:
    """Construct + validate `Settings` from the environment — the fail-closed entry
    point. Plain factory (no cache) so construction is a pure validation step; the
    composition root should call this once at startup and hold the instance."""
    return Settings()
