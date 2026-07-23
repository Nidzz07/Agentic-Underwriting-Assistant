"""C3 DbUrlGuard — the DATA-5 config-load guard (NFR-DB-DATA5-1).

A pure function ``require_postgres_url(url) -> url`` that rejects any
non-``postgresql`` backend (SQLite in particular). Invoked at config load so a
mis-configured non-Postgres URL fails fast, before any connection. Unit-testable
with no container and no deployment code — a ``database``-unit deliverable with no
Infrastructure dependency.

This is the config half of DATA-5; the structural half (BYTEA/TIMESTAMPTZ DDL cannot
apply on SQLite) is carried by the migration schema itself. Repo-wide "no SQLite
anywhere" CI aggregation is quality-gates' concern (referenced, not owned here).
"""
from __future__ import annotations

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class NonPostgresUrlError(ValueError):
    """The configured database URL is not a ``postgresql`` backend (DATA-5)."""


def require_postgres_url(url: str) -> str:
    """Return ``url`` unchanged iff it is a ``postgresql`` backend; else raise.

    Accepts any driver variant (``postgresql://``, ``postgresql+psycopg2://``, …)
    because the DATA-5 constraint is on the **backend**, not the driver. Rejects
    ``sqlite://`` and every other backend, and rejects an unparseable URL.
    """
    try:
        parsed = make_url(url)
    except ArgumentError as exc:
        raise NonPostgresUrlError(f"unparseable database URL: {url!r}") from exc

    backend = parsed.get_backend_name()
    if backend != "postgresql":
        raise NonPostgresUrlError(
            f"DATA-5 requires a postgresql database URL, got backend {backend!r}"
        )
    return url
