"""C5 FidelityComparator — the column-for-column consistency guard (NFR-DB-FIDELITY-1).

Compares the LIVE migration-produced schema (via C4 ``SchemaIntrospector``) against a
**consumer's own SQLAlchemy ``Table`` declaration**, over exactly the two audit tables
(``audit_record`` + ``applicant_profile_snapshot``). **Drift on EITHER side fails** —
a migration that changes a column, OR a consumer edit expecting a column the schema
lacks. Converts the one-time 18/18 verification into a permanent automated invariant.

**Reference-not-own, in reverse (critical):** this PRODUCTION module NEVER imports
``backend.audit_store``. The consumer's ``Table`` objects are **passed in by the
caller**; only the FIDELITY-1 *test* imports ``pg_repository``'s metadata read-only
and hands it here. So there is **no production cross-import and no circular
dependency** — ``database`` production code does not depend on ``audit_store``.

**Comparison scope:** ``{name, type, nullable, pk, fk_target, indexed}`` only. **CHECK
constraints EXCLUDED** (an optional ``action``/``status`` CHECK, and ``role``'s absence
of one, never cause a false mismatch). Types are base-type tokens (length/precision
ignored) — see ``schema_introspector.base_type_token``.
"""
from __future__ import annotations

from typing import Any, Mapping

import sqlalchemy as sa

from backend.database.schema_introspector import base_type_token, normalized_table_spec

#: The exactly-two audit tables the consumer (audit-store's pg_repository) declares.
FIDELITY_TABLES = ("audit_record", "applicant_profile_snapshot")


class FidelityError(AssertionError):
    """The migration-produced schema and the consumer's declaration have drifted."""


def spec_from_table(table: sa.Table) -> dict[str, dict[str, Any]]:
    """Normalize a consumer's own ``sa.Table`` into the same shape C4 produces from
    the live schema, so the two compare like for like."""
    spec: dict[str, dict[str, Any]] = {}
    for col in table.columns:
        fk_target: str | None = None
        if col.foreign_keys:
            fk_target = next(iter(col.foreign_keys)).target_fullname  # 'table.column'
        spec[col.name] = {
            "type": base_type_token(col.type),
            "nullable": bool(col.nullable),
            "pk": bool(col.primary_key),
            "fk_target": fk_target,
            "indexed": bool(col.index),
        }
    return spec


def compare_table(engine: sa.Engine, table_name: str, consumer_table: sa.Table) -> list[str]:
    """Return human-readable drift descriptions for one table (empty == consistent)."""
    live = normalized_table_spec(engine, table_name)
    consumer = spec_from_table(consumer_table)
    diffs: list[str] = []

    live_cols, consumer_cols = set(live), set(consumer)
    for missing in sorted(consumer_cols - live_cols):
        diffs.append(f"{table_name}.{missing}: consumer expects a column the schema lacks")
    for extra in sorted(live_cols - consumer_cols):
        diffs.append(f"{table_name}.{extra}: schema has a column the consumer does not declare")
    for name in sorted(live_cols & consumer_cols):
        if live[name] != consumer[name]:
            diffs.append(
                f"{table_name}.{name}: consumer {consumer[name]} != schema {live[name]}"
            )
    return diffs


def assert_fidelity(engine: sa.Engine, consumer_tables: Mapping[str, sa.Table]) -> None:
    """Raise ``FidelityError`` if the live schema drifts from the consumer's
    declaration on any of the two audit tables. One-directional consistency guard —
    ``database`` migrations are the authority; the consumer metadata is the reference.
    """
    diffs: list[str] = []
    for table_name in FIDELITY_TABLES:
        diffs.extend(compare_table(engine, table_name, consumer_tables[table_name]))
    if diffs:
        raise FidelityError(
            "schema/consumer fidelity drift detected:\n  " + "\n  ".join(diffs)
        )
