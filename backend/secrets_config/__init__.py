"""`secrets-config` (U16) — the SEC-3 single source for credential/URL values.

A typed Pydantic-v2 `Settings` over the six Phase-1 required env-var shapes, an
independent `postgresql://` scheme validator (`is_postgres_url`), and a plain
`get_settings()` factory (the fail-closed entry point). **No credential/URL VALUE**
lives here — values are sourced from the environment at runtime.

Boundaries held (FD / NFR Design):
- **Dependency leaf** — production code imports **no** consumer / ``backend.database``
  module (the scheme check is this unit's own, using only third-party ``sqlalchemy``).
  Structurally verified by ``tests/test_no_forbidden_imports.py``.
- **SEC-3** — no value in any committed file; the dev ``.env`` is gitignored; the
  committed ``.env.example`` is placeholder-only.
- **Fail-closed** — a missing/invalid required var raises at ``Settings()``
  construction. **Deterministic** (pure validation). **No LLM.**
"""
from __future__ import annotations

from backend.secrets_config.settings import Settings, get_settings
from backend.secrets_config.url_validation import is_postgres_url

__all__ = ["Settings", "get_settings", "is_postgres_url"]
