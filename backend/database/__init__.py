"""`database` (U15) — the shared PostgreSQL schema + migrations substrate.

The **sole authoritative production schema** for the co-located audit tables
(`audit_record` + `applicant_profile_snapshot`), the `app_user` foundational
skeleton, plus the forward-only migration runner and the schema-integrity guards
(DbUrlGuard, SchemaIntrospector, FidelityComparator, MigrationChecksum).

Boundaries held (FD / NFR Design):
- **Reference-not-own, in reverse** — this package's production code NEVER imports
  ``backend.audit_store``. Only the FIDELITY-1 *test* imports
  ``pg_repository``'s Table metadata read-only.
- **SEC-3** — no credential/connection-string VALUES anywhere. The grants
  migration carries only ``${AUDIT_WRITER_PASSWORD}`` / ``${AUDIT_READER_PASSWORD}``
  placeholder tokens; the runner substitutes from ``os.environ`` at execution and
  never logs the rendered SQL.
- **DATA-5** — PostgreSQL everywhere, no SQLite (``BYTEA`` / ``TIMESTAMPTZ`` +
  ``require_postgres_url`` config guard).
- **No LLM** in this unit.
"""
from __future__ import annotations
