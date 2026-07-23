"""C4 SchemaIntrospector — reflect the LIVE migration-produced schema.

Reads the live schema (``sa.inspect(engine)``) and extracts a **normalized
column-spec dict** per table: ``{col_name: {type, nullable, pk, fk_target, indexed}}``.
A **live read, never a stored copy** — the migration sequence stays the sole schema
authority (no third schema representation).

Normalization rules (shared with C5 FidelityComparator so both sides compare like
for like):
- **type** → a common canonical BASE-TYPE TOKEN — ``bytea`` / ``string`` /
  ``timestamptz`` — with **length/precision ignored** (``pg_repository`` uses
  unparameterized ``sa.String``, so a length difference must never be a false drift).
- **CHECK constraints EXCLUDED** — they are never part of the spec (an optional
  ``action``/``status`` CHECK, or ``role``'s absence of one, must not trip fidelity).

Shared by MIGRATE-1 and FIDELITY-1 (single source, no duplication). Exercised in the
integration tier against a real testcontainers Postgres.
"""
from __future__ import annotations

from typing import Any

import sqlalchemy as sa


class UnmappedTypeError(ValueError):
    """A column type falls outside the three base-type tokens the schema uses."""


def base_type_token(sqltype: Any) -> str:
    """Map a SQLAlchemy type (declared OR reflected) to a canonical base token.

    Length/precision are ignored — only the base type matters. ``LargeBinary`` and
    ``DateTime`` are checked before ``String`` (they are not ``String`` subclasses,
    but the intent is explicit). The schema uses ONLY these three types
    (``domain-entities.md §2``), so any other type is a real, surfaced mismatch.
    """
    if isinstance(sqltype, sa.LargeBinary):   # BYTEA / LargeBinary
        return "bytea"
    if isinstance(sqltype, sa.DateTime):      # TIMESTAMPTZ / DateTime(timezone=True)
        return "timestamptz"
    if isinstance(sqltype, sa.String):        # VARCHAR / String (any/no length)
        return "string"
    raise UnmappedTypeError(f"unmapped column type {sqltype!r}")


def normalized_table_spec(
    engine: sa.Engine, table_name: str, schema: str | None = None
) -> dict[str, dict[str, Any]]:
    """Reflect ``table_name`` from the live schema into the normalized column-spec
    dict. CHECK constraints and server defaults are deliberately not represented."""
    insp = sa.inspect(engine)

    pk_cols = set(
        insp.get_pk_constraint(table_name, schema=schema).get("constrained_columns") or []
    )

    fk_target: dict[str, str] = {}
    for fk in insp.get_foreign_keys(table_name, schema=schema):
        constrained = fk.get("constrained_columns") or []
        referred_table = fk.get("referred_table")
        referred_cols = fk.get("referred_columns") or []
        for i, col in enumerate(constrained):
            ref_col = referred_cols[i] if i < len(referred_cols) else ""
            fk_target[col] = f"{referred_table}.{ref_col}"

    indexed_cols: set[str] = set()
    for idx in insp.get_indexes(table_name, schema=schema):
        for col in idx.get("column_names") or []:
            if col is not None:
                indexed_cols.add(col)

    spec: dict[str, dict[str, Any]] = {}
    for col in insp.get_columns(table_name, schema=schema):
        name = col["name"]
        spec[name] = {
            "type": base_type_token(col["type"]),
            "nullable": bool(col["nullable"]),
            "pk": name in pk_cols,
            "fk_target": fk_target.get(name),
            "indexed": name in indexed_cols,
        }
    return spec


def table_names(engine: sa.Engine, schema: str | None = None) -> set[str]:
    """The set of table names in the live schema (for presence/absence assertions)."""
    return set(sa.inspect(engine).get_table_names(schema=schema))
