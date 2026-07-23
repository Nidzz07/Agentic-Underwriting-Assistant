# Code Generation Summary — `database` (EPIC-6 / U15)

**Stage**: BUILD → Code Generation, **Part 2 (Generation)** · **Date**: 2026-07-06
**Runtime**: Python **3.12.10** (pinned, D6) · **Depth**: comprehensive · **TDD**: tests-first, leaf-first.
**Result**: full backend suite **599 passed / 3 skipped** (the 3 `posix_only` intake tests on Windows dev);
**TOTAL coverage 99.75%** (QA-6 ≥90% reached). `database` **integration tier actually executed** (Docker up,
`postgres:16` via testcontainers) — not skipped. This completes `database` as the **FIFTH fully-complete unit**
on approval.

---

## 1. Modules generated (`backend/database/`)

| File | Component | Role |
|---|---|---|
| `__init__.py` | — | package doc + boundary statement (no `audit_store` import; SEC-3; DATA-5; no LLM) |
| `migrations/0001_initial_schema.sql` | **C1** | the Phase-1 production schema — `audit_record` (14) + `applicant_profile_snapshot` (4, FK) + `app_user` (3, open role), column-for-column with `pg_repository.py` |
| `migrations/0002_grants.sql` | **C2** | role grants — `audit_writer` INSERT+SELECT / `audit_reader` SELECT-only; **`${AUDIT_WRITER_PASSWORD}` / `${AUDIT_READER_PASSWORD}` placeholder tokens only** |
| `migrations/checksums.json` | **C6** | committed `{filename: sha256}` manifest incl. the grants file |
| `migration_runner.py` | **C1** | forward-only ordered apply + `${VAR}` substitution (hard-error on missing var; rendered SQL never logged); `applied_migrations` tool-tracking table |
| `db_url_guard.py` | **C3** | pure `require_postgres_url` — rejects non-`postgresql` backends (DATA-5) |
| `schema_introspector.py` | **C4** | live-schema reflection → normalized `{type,nullable,pk,fk_target,indexed}` dict; base-type tokens; CHECK excluded |
| `fidelity_comparator.py` | **C5** | compares live schema vs a **passed-in** consumer `Table`; drift either side fails |
| `tests/` | — | conftest (testcontainers `postgres:16` fixture applying the production migrations) + factories + 10 test modules |

---

## 2. TDD test → `NFR-DB-*` target map (all PASSED)

| Target | Test(s) | Tier |
|---|---|---|
| **ATOMIC-1** | `test_atomic_colocation.py::test_duplicate_pk_rolls_back_both_rows` (dup-PK `IntegrityError` → both tables 0 rows) | integration |
| **COLOC-1** | `test_migration_apply.py::test_both_audit_tables_in_one_schema` | integration/structural |
| **APPEND-1** | `test_grants_roles.py::{test_writer_can_insert_and_select, test_writer_cannot_update, test_writer_cannot_delete, test_reader_can_select, test_reader_cannot_insert, test_reader_cannot_update_or_delete}` | integration (real roles) |
| **DATA5-1** | `test_db_url_guard.py` (11 params: postgres accepted; sqlite/other/unparseable rejected) + structural BYTEA/TIMESTAMPTZ in `0001` | unit + structural |
| **MIGRATE-1** | `test_migration_apply.py::{test_apply_from_empty_created_the_three_tables, test_audit_tables_have_their_expected_columns, test_migration_sequence_is_forward_only_and_idempotent}` | integration |
| **MIGRATE-2** | `test_migration_checksum.py` (8: committed match, grants-in-manifest, edited-fails, **weakened-grant-caught**, append-allowed, orphan/missing fail) | unit |
| **FIDELITY-1** | `test_fidelity.py::{test_migration_matches_pg_repository, test_consumer_expecting_missing_column_fails, test_consumer_type_drift_fails, test_spec_from_pg_audit_record, test_spec_from_pg_snapshot_fk}` | integration + read-only `pg_repository` import (test-only) |
| **BYTEA-1** | `test_bytea_roundtrip.py::{test_adversarial_bytes_roundtrip_byte_identical (5-case), test_real_canon_ser_roundtrip_and_content_hash}` | integration |
| **SCOPE-1** | `test_migration_apply.py::{test_app_user_role_is_open_novel_value_inserts, test_rulebook_registry_table_is_absent}` | integration + structural |
| **PERF-1** | `test_migration_apply.py::test_insert_latency_observed` (measured, printed, non-gating) | observed |
| **OBS-1** | — | **N/A — observability-owned** (documented boundary, not an orphan) |

No target unmapped; no test invents a target the NFR Design didn't approve; no test asserts a CHECK EXISTS on
`action`/`status`.

---

## 3. Coverage

`database` counted modules (unit tier): `__init__.py` **100%**, `db_url_guard.py` **100%**, `migration_checksum.py`
**100%**. The three **live-DB modules** — `migration_runner.py`, `schema_introspector.py`, `fidelity_comparator.py`
— are **omitted from unit-tier coverage exactly like `pg_repository.py`** (`[tool.coverage.run] omit`), because their
DB paths only exercise against a real Postgres; they are fully **integration-covered** in CI/here (all green). Pure
portions (substitution, base-type token, `spec_from_table`) additionally have unit tests that run without Docker.
`--cov=backend/database` added to `addopts`; **no coverage-threshold change**.

---

## 4. Flagged realization notes (faithful; no frozen design re-opened)

1. **FidelityComparator is `audit_store`-import-free in production (faithful to the frozen design, not a deviation).**
   NFR-Design `logical-components.md §4` + the plan Q5 answer both state *"database production code never imports
   `audit_store`; only C5's **test** imports `pg_repository` metadata read-only."* Realized exactly: `fidelity_comparator.py`
   takes the consumer's `Table` objects as a **parameter**; the read-only `pg_repository` import lives **only** in
   `tests/test_fidelity.py`. No circular dependency; no `audit_store` file edited.
2. **MIGRATE-1 audit-table exact parity delegated to FIDELITY-1** (the single `pg_repository`-importing test), keeping
   that import in exactly one file. MIGRATE-1 itself uses **targeted column-name presence** (a permitted "minimal
   targeted presence assertion"), not a duplicate authoritative MetaData — honoring "no third schema representation".
3. **`applied_migrations` tool-tracking table folded** (Q1 raw-SQL runner). MIGRATE-1/SCOPE-1 use **targeted
   presence/absence** checks (does `audit_record` exist with the right columns; is any `rulebook` table absent) —
   **never a closed-world "only exactly these tables exist"** check, since the tool table is legitimately present.
4. **`"timestamp"` column quoted** in the DDL (reserved word); reflects back as `timestamp`, matching
   `pg_repository`'s column name (FIDELITY-1 passes).

---

## 5. SEC-3 / guardrails held (verified)

- **No credential VALUE anywhere in generated code.** `0002_grants.sql` carries only `${AUDIT_WRITER_PASSWORD}` /
  `${AUDIT_READER_PASSWORD}` tokens (asserted by `test_committed_grants_file_holds_only_placeholder_tokens`); the
  runner reads `os.environ` and **never logs the rendered SQL**; missing env var → `MissingEnvVarError` (hard error,
  never a silent empty password). Test role passwords are throwaway fixture-scoped literals.
- **DATA-5**: PostgreSQL everywhere, no SQLite (`BYTEA`/`TIMESTAMPTZ` + `require_postgres_url`). **ATOMIC-1/COLOC-1**:
  one co-located DB/schema. **APPEND-1/SEC-4/SEC-5**: real DB-role enforcement. **BYTEA byte-fidelity** (REPLAY-1/DET-2).
  **CON-BR1**: no demographic-driven column/index/metric. **Advisory-only** naming. **No LLM** in `database`.
- **Reference-not-own (in reverse)**: `pg_repository.py` imported read-only by the fidelity **test** only;
  audit-store's test files not rewritten; `app_user` open-role skeleton; rulebook registry absent; no consuming
  business logic touched.

---

## 6. Artifacts

- Source + tests: `backend/database/` (5 source modules + `migrations/` + `tests/`).
- Tier-1 results: `testresults.txt` (repo root) — 599 passed / 3 skipped / 99.75%.
- This summary: `guide-docs/build/database/code/code-summary.md`.
