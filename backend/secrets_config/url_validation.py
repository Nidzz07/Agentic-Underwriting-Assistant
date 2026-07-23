"""C2 is_postgres_url — the independent `postgresql://` scheme validator.

`secrets-config`'s **own** DATA-5-spirit scheme check, using only third-party
`sqlalchemy` — it **does NOT import** `database`'s `DbUrlGuard` (no shared `backend`
module, no circular dependency; enforced by NoForbiddenImports). Total + pure: any
non-postgresql or malformed value returns `False` (never raises). No LLM.
"""
from __future__ import annotations

from sqlalchemy.engine import make_url


def is_postgres_url(value: str) -> bool:
    """Return ``True`` iff ``value`` is a ``postgresql`` backend URL (any driver
    variant, e.g. ``postgresql+psycopg2://``). Non-postgresql schemes, empty/blank,
    and malformed URLs all return ``False`` (fail-safe — the caller rejects)."""
    if not isinstance(value, str) or value.strip() == "":
        return False
    try:
        return make_url(value.strip()).get_backend_name() == "postgresql"
    except Exception:
        return False
