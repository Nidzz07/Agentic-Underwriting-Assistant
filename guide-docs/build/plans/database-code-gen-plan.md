# Code Generation Plan (Part 1) — `database` (EPIC-6 / U15)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags, **TDD tests-first**)
**Loop position**: `database` (story-less infra) · FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure Design ✅ (approved 2026-07-06)**
→ **Code Generation ← here (the LAST stage for `database` — completes the FIFTH fully-complete unit).**
**Unit**: U15 `database` · **Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: comprehensive.
**Status**: **Plan — awaiting `[Answer]:` tags. NO code generated this stage. Stop after this plan.**

This plan realizes the **6 approved NFR-Design components (C1–C6)** as real code under `backend/database/`, built **ON**
the frozen FD, the approved `NFR-DB-*` targets, the NFR Design patterns, and the Infrastructure Design execution model
— **re-opening none of them**. **TDD: every `NFR-DB-*` target gets its test first, at the tier the NFR Design pinned**
(integration/testcontainers vs unit/structural). **SEC-3: no credential/connection-string VALUES appear in any
generated code — only the placeholder token `${AUDIT_WRITER_PASSWORD}`/`${AUDIT_READER_PASSWORD}` in the committed
grants file and `os.environ` reads at execution time.**

> **Path-correction record (from the completion-gate review)**: on-disk verification confirmed exactly **three**
> Infrastructure Design artifacts — `guide-docs/build/database/infrastructure-design/infrastructure-design.md`,
> `.../deployment-architecture.md`, and `guide-docs/build/shared-infrastructure.md`. **No phantom fourth file**, no
> `build/shared-infrastructure-design/` directory; guide-state.md + audit.md record only the correct paths. The
> duplicate/mistaken path existed only in the on-screen completion wording and is corrected.

---

## 1. What Code-Gen builds (and what it must NOT touch)

### 1.1 Builds — the 6 components as code + their tests
The **production migration sequence** (the authoritative schema, superseding audit-store's interim TEST DDL at the
schema-authority level) + the migration **runner**, the **grants migration** (placeholder mechanism), and the four
app/test-logic components (`DbUrlGuard`, `SchemaIntrospector`, `FidelityComparator`, `MigrationChecksum`), each with
tests at its NFR-pinned tier.

### 1.2 Does NOT touch (held closed)
- **C1's migration model** + **C2's grant-DDL text semantics** — realized as written, **not re-designed**.
- **audit-store's `pg_repository.py`** — **imported read-only** by C5's test for FIDELITY-1; **never edited**. Its
  `metadata` (the two `sa.Table`s) is the consuming reference the fidelity test compares against.
- **audit-store's `test_pg_integration.py`** — its self-contained TEST-only `create_all` + interim roles stay as-is
  (a test harness, not this unit's deliverable). This unit's migrations become the **production** schema authority;
  audit-store's test files are **not rewritten**.
- No consuming unit's business logic; no `PROJECT-BRIEF.md` / `user-journey.md` edits; OOS-7/OOS-8 doc commitments stay.

### 1.3 Guardrails held (skill)
DATA-5 (PostgreSQL everywhere, no SQLite); ATOMIC-1/COLOC-1 (one co-located DB/schema); APPEND-1/SEC-4/SEC-5 (role
grants); SEC-3 (**no credential values** — placeholder token + `os.environ` only); CON-BR1 (no demographic-driven
schema/index/metric); advisory-only naming; **no LLM anywhere in `database`.**

---

## 2. Module / package layout (`backend/database/`) — C1–C6 mapping

```text
backend/database/
├── __init__.py
├── db_url_guard.py            # C3 — pure require_postgres_url(url) -> url; raises on non-postgresql scheme
├── migration_runner.py        # C1 — forward-only ordered-sequence apply; placeholder substitution for the grants file
├── schema_introspector.py     # C4 — reflect live schema -> normalized {name,type,nullable,pk,fk_target,indexed} dict
├── fidelity_comparator.py     # C5 — read pg_repository metadata read-only -> same-shape dict; compare 2 audit tables
├── migration_checksum.py      # C6 — recompute file sha256 vs the committed manifest (incl. the grants file)
├── migrations/                # C1/C2 — the authoritative forward-only sequence (the SOLE schema authority)
│   ├── 0001_initial_schema.sql     # audit_record (14) + applicant_profile_snapshot (4, FK) + app_user (3)
│   ├── 0002_grants.sql             # C2 — CREATE ROLE ... LOGIN PASSWORD ${AUDIT_WRITER_PASSWORD}; GRANT ...
│   └── checksums.json              # C6 manifest — {migration_filename: sha256} incl. 0002_grants.sql
└── tests/
    ├── __init__.py
    ├── conftest.py                 # testcontainers postgres:16 fixture (migrated schema) + role-engine helper
    ├── test_db_url_guard.py        # unit — DATA5-1 guard
    ├── test_migration_checksum.py  # unit — MIGRATE-2 immutability
    ├── test_schema_introspector.py # unit-ish/integration — normalization shape
    ├── test_migration_apply.py     # integration — MIGRATE-1 apply-from-empty exact schema + SCOPE-1
    ├── test_fidelity.py            # integration — FIDELITY-1 (imports pg_repository metadata read-only)
    ├── test_grants_roles.py        # integration — APPEND-1 role write matrix (real roles)
    ├── test_atomic_colocation.py   # integration — ATOMIC-1/COLOC-1 duplicate-PK rollback both empty
    └── test_bytea_roundtrip.py     # integration — BYTEA-1 opaque round-trip (5-case adversarial + real CANON-SER)
```

| Component | Module | Backs |
|---|---|---|
| **C1 MigrationSequence** | `migrations/*.sql` + `migration_runner.py` | ATOMIC-1, COLOC-1, MIGRATE-1, BYTEA-1, SCOPE-1, APPEND-1 (via C2) |
| **C2 GrantDDL** | `migrations/0002_grants.sql` (placeholder tokens) | APPEND-1 |
| **C3 DbUrlGuard** | `db_url_guard.py` | DATA5-1 |
| **C4 SchemaIntrospector** | `schema_introspector.py` | MIGRATE-1, FIDELITY-1 |
| **C5 FidelityComparator** | `fidelity_comparator.py` | FIDELITY-1 |
| **C6 MigrationChecksum** | `migration_checksum.py` + `checksums.json` | MIGRATE-2 |

---

## 3. TDD test → target map (every `NFR-DB-*` at its NFR-pinned tier)

| Target | Test file / name | Tier | Assertion (per the approved pattern) |
|---|---|---|---|
| **ATOMIC-1** | `test_atomic_colocation.py::test_duplicate_pk_rolls_back_both_rows` | integration (testcontainers) | Insert two rows w/ same PK inside one txn → `pytest.raises(IntegrityError)`; follow-up query asserts **both** tables 0 rows |
| **COLOC-1** | same file / `test_both_tables_one_schema` | integration | Both audit tables reflected in **one** database/schema on one connection |
| **APPEND-1** | `test_grants_roles.py::test_writer_matrix` / `::test_reader_matrix` | integration | Apply full sequence incl. grants; connect **as each role**; `audit_writer` INSERT/SELECT ok, UPDATE/DELETE raise; `audit_reader` SELECT ok, all writes raise |
| **DATA5-1** | `test_db_url_guard.py::test_scheme_guard` | unit | `postgresql://` → ok; `sqlite://` → raises; other scheme → raises |
| **MIGRATE-1** | `test_migration_apply.py::test_apply_from_empty_exact_schema` | integration | Apply from empty → introspect → exact expected schema for the 2 audit tables (via C4) + `app_user` presence assertions |
| **MIGRATE-2** | `test_migration_checksum.py::test_edited_published_migration_fails` | unit | Recompute each file sha256 vs `checksums.json`; edited published file → mismatch → fail; manifest **includes** `0002_grants.sql` (weakened `audit_reader` grant caught) |
| **FIDELITY-1** | `test_fidelity.py::test_migration_matches_pg_repository` | integration + read-only import | C4's normalized dict vs C5's `pg_repository`-metadata dict over the **two audit tables**; **CHECK excluded**; base-type tokens; length/precision ignored; drift either side fails |
| **BYTEA-1** | `test_bytea_roundtrip.py::test_opaque_roundtrip` | integration | Write the 5-case adversarial byte set + real CANON-SER output to `rule_results`/`profile_canonical`; read back **byte-identical**; recomputed `content_hash` matches |
| **SCOPE-1** | `test_migration_apply.py::test_app_user_open_role_and_rulebook_absent` | integration + structural | Insert `app_user` row with novel `role='admin'` → succeeds (no closing CHECK); introspect → **no** rulebook-registry table |
| **PERF-1** | `test_migration_apply.py::test_apply_and_insert_latency_observed` | observed (non-gating) | Measure migration-apply + insert latency; report vs soft budget; **never fails the build** |
| **OBS-1** | — | **N/A** | DB metrics/traces are `observability`-owned (documented boundary, not an orphan) |

**No `NFR-DB-*` target is unmapped; no test invents a target the NFR Design didn't approve.** No test asserts a CHECK
EXISTS on `action`/`status` (optional per BR-DB-9); nothing tests auth-rbac authn/permissions or rules-engine
evaluation (reference-not-own, in reverse).

---

## 4. Implementation order (leaf-first, tests-first per step)

0. **Scaffold**: `backend/database/__init__.py`, `tests/__init__.py`, `tests/conftest.py` (testcontainers `postgres:16`
   fixture that **applies the migration sequence** to a fresh container + a role-engine helper). Add `--cov=backend/database`
   to `pyproject` `addopts` (Q9).
1. **C1 initial-schema migration** — write `0001_initial_schema.sql` creating `audit_record` (14 cols, PK, `application_id`
   INDEX), `applicant_profile_snapshot` (4 cols, PK + FK → `audit_record.decision_id`), `app_user` (3 cols, PK, `subject`
   UNIQUE, open `role`) — **column-for-column with `pg_repository.py`** (BYTEA/TIMESTAMPTZ/VARCHAR). **Test first**:
   MIGRATE-1 apply-from-empty exact schema + SCOPE-1 (`app_user` presence, rulebook table absent).
2. **C2 grants migration** — write `0002_grants.sql`: `CREATE ROLE audit_writer LOGIN PASSWORD ${AUDIT_WRITER_PASSWORD}`
   + `GRANT INSERT, SELECT …`; `CREATE ROLE audit_reader LOGIN PASSWORD ${AUDIT_READER_PASSWORD}` + `GRANT SELECT …`.
   **Placeholder tokens only — no values.** **Test first**: APPEND-1 role write matrix on real roles.
3. **C1 migration_runner** — the forward-only ordered-file apply + the **placeholder substitution** (reads
   `os.environ`, templates `${VAR}` for the grants file only, **never logs the rendered SQL**, missing env var → hard
   error). **Test first**: substitution unit test (token → env value, on a fake env; rendered form not logged) +
   forward-only apply integration.
4. **C3 DbUrlGuard** — pure `require_postgres_url`. **Test first**: DATA5-1 unit (no container).
5. **C4 SchemaIntrospector** — reflect live schema → normalized `{name,type,nullable,pk,fk_target,indexed}` dict
   (base-type tokens; length/precision ignored). **Test first**: normalization-shape test.
6. **C5 FidelityComparator** — **import `backend.audit_store.pg_repository` metadata read-only** → same-shape dict;
   compare the two audit tables, **CHECK excluded**. **Test first**: FIDELITY-1 (match now; a simulated drift fails).
7. **C6 MigrationChecksum** — build `checksums.json` manifest (incl. `0002_grants.sql`) + recompute-and-compare.
   **Test first**: MIGRATE-2 (edit a published file → fail; append a new migration → allowed).
8. **Remaining integration tests** — ATOMIC-1/COLOC-1 (duplicate-PK rollback both empty), BYTEA-1 (5-case adversarial
   + real CANON-SER round-trip), SCOPE-1 extensibility (novel role insert).
9. **PERF-1 observed** (non-gating latency report) + confirm **OBS-1 N/A** boundary noted.
10. **Coverage gate** — run the full backend suite; `backend/database` source ≥90% (QA-6); integration-only files
    handled per Q9. Refresh `testresults.txt`.
11. **Code summary** — `guide-docs/build/database/code/code-summary.md` (module list + the test→target map + any
    flagged realization notes) + back-annotate guide-state.md; completion + 2-option gate.

---

## 5. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide
**Code-Gen realization** — they do **not** re-open the FD, the NFR targets, C1's model, or C2's grant text.

## Question 1 — Migration tool (deferred at NFR/Infra — Code-Gen must pick now)
What executes the forward-only sequence?

A) **A minimal raw-SQL versioned runner (no new dependency)** — ordered `NNNN_*.sql` files under
   `backend/database/migrations/` applied in order via SQLAlchemy `text()`; a tiny `applied_migrations` version table
   tracks what ran (idempotent, forward-only). **Recommended**: adds **no new dependency** (SQLAlchemy 2.x already in
   stack), keeps migrations as **plain `.sql`** (clean sha256 for MIGRATE-2, transparent `${VAR}` placeholder
   substitution for the grants file, tool-agnostic live-schema reflection for C4/FIDELITY-1), and matches the "no new
   dep" NFR theme.
B) **Alembic** — SQLAlchemy-native migration framework (revision chaining, `op.execute`). Mature, but **adds a new
   dependency**, stores DDL inside Python revision modules (checksum/placeholder handling less transparent than plain
   `.sql`), and brings autogenerate machinery this schema-authority unit does not need.
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a minimal raw-SQL versioned runner (no new dependency): ordered NNNN_*.sql files applied in order via SQLAlchemy text(); a tiny applied_migrations version table tracks what ran (idempotent, forward-only). Adds no new dependency (SQLAlchemy 2.x already in stack), keeps migrations as plain .sql for clean sha256/MIGRATE-2, transparent ${VAR} substitution, tool-agnostic reflection for C4/FIDELITY-1.

## Question 2 — Migration file format + ordering
How are the sequence files named/placed?

A) **Zero-padded ordered `.sql` files** — `0001_initial_schema.sql`, `0002_grants.sql`, … under
   `backend/database/migrations/`; **forward-only**, applied in filename order; a new schema change is a **new
   higher-numbered file** (never an edit to a published one, mirroring BR-DB-4 append-only + the rulebook
   append-only-version discipline).
B) A single monolithic `schema.sql` re-run each time (rejected — no forward-only history; MIGRATE-2 immutability has
   nothing to protect).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — zero-padded ordered .sql files (0001_initial_schema.sql, 0002_grants.sql, ...) under backend/database/migrations/; forward-only, applied in filename order; a new schema change is a new higher-numbered file, never an edit to a published one.

## Question 3 — Placeholder-substitution implementation (the pinned Infra mechanism, in code)
How does the runner realize `${AUDIT_WRITER_PASSWORD}`/`${AUDIT_READER_PASSWORD}`?

A) **The committed grants file carries the `${VAR}` tokens only**; the runner reads `os.environ["AUDIT_WRITER_PASSWORD"]`
   / `["AUDIT_READER_PASSWORD"]` and substitutes at execution time (a strict template — **missing env var → hard error**,
   never a silent empty password); the **rendered SQL is never logged** (only the placeholder-bearing form is ever on
   disk/in logs); substitution applies **only** to the grants file. MIGRATE-2's checksum hashes the **placeholder-bearing**
   committed file (stable; an edited grant still caught; secret lives outside the checksummed content). **No password
   value in any generated file** (SEC-3).
B) Bake passwords into the `.sql` at build time (rejected — SEC-3 violation; the checksum would change per environment;
   the build fails on a hardcoded secret).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — the committed grants file carries the ${VAR} tokens only; the runner reads os.environ["AUDIT_WRITER_PASSWORD"]/["AUDIT_READER_PASSWORD"] and substitutes at execution time (strict template — missing env var → hard error, never a silent empty password); rendered SQL never logged; substitution applies only to the grants file. MIGRATE-2's checksum hashes the placeholder-bearing committed file. No password value in any generated file.

## Question 4 — SchemaIntrospector (C4) reflection approach
How is the live schema read + normalized?

A) **SQLAlchemy `Inspector` (`sa.inspect(engine)`)** over the **live migration-produced schema** of the testcontainer
   → a normalized per-table dict `{name, type, nullable, pk, fk_target, indexed}` with **base-type tokens** (`bytea` /
   `string` / `timestamptz`), **length/precision ignored**, **CHECK excluded**. A **live read**, never a stored copy —
   the migration sequence stays the sole schema authority (no third representation).
B) Maintain a hand-written expected-schema dict as the oracle (rejected — a third schema representation the NFR Design
   explicitly forbids; `app_user` uses targeted presence assertions instead).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — SQLAlchemy Inspector (sa.inspect(engine)) over the live migration-produced schema of the testcontainer → a normalized per-table dict {name, type, nullable, pk, fk_target, indexed} with base-type tokens, length/precision ignored, CHECK excluded. A live read, never a stored copy.

## Question 5 — FidelityComparator (C5) consuming-metadata source
How does FIDELITY-1 get the consumer's declared shape?

A) **Import `backend.audit_store.pg_repository`'s `metadata` read-only** (the consumer's own `sa.Table` declaration) →
   the same normalized dict shape as C4 → compare over **exactly the two audit tables** (`audit_record` +
   `applicant_profile_snapshot`); **`app_user` excluded** (not in `pg_repository`); **drift either side fails**. A
   **one-directional consistency guard** — read-only import, no production cross-import, no circular dependency
   (`database` production code never imports `audit_store`; only C5's **test** does).
B) Copy the column list into `database` and compare to the copy (rejected — a stale duplicate; defeats the drift
   guard).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — import backend.audit_store.pg_repository's metadata read-only → the same normalized dict shape as C4 → compare over exactly the two audit tables (audit_record + applicant_profile_snapshot); app_user excluded (not in pg_repository); drift either side fails. One-directional consistency guard; database production code never imports audit_store, only C5's test does.

## Question 6 — MigrationChecksum (C6) manifest format + location
How is the immutability manifest stored/checked?

A) **A committed `backend/database/migrations/checksums.json`** — `{migration_filename: sha256}` covering **every
   published migration incl. `0002_grants.sql`**; the test recomputes each file's hash and compares. **Editing** a
   published file → mismatch → fail; **appending** a new migration + its manifest entry → allowed. Ties append-only /
   SEC-4 integrity (a weakened `audit_reader` grant is caught like an edited table migration).
B) Recompute hashes with no committed baseline (rejected — nothing to detect drift against).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a committed backend/database/migrations/checksums.json — {migration_filename: sha256} covering every published migration incl. 0002_grants.sql; the test recomputes each file's hash and compares. Editing a published file → mismatch → fail; appending a new migration + its manifest entry → allowed.

## Question 7 — Test tiering + testcontainers fixture
How are the tiers split + the container provisioned?

A) **Unit tests run locally, no Docker** (DbUrlGuard/DATA5-1, MigrationChecksum/MIGRATE-2, and the runner's pure
   substitution logic against a fake env). **Integration tests** use a **`PostgresContainer("postgres:16")`** fixture
   (matching the built `test_pg_integration.py:45`) that **applies the migration sequence** to a fresh container,
   marked **`@pytest.mark.integration`**, **auto-skipped** locally (importorskip), **run in CI**. Role-scoped engines
   built from the container URL for APPEND-1.
B) Everything as integration (rejected — the guard + checksum + substitution are unit-testable today; forcing Docker
   slows local dev).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — unit tests run locally, no Docker (DbUrlGuard/DATA5-1, MigrationChecksum/MIGRATE-2, the runner's pure substitution logic against a fake env). Integration tests use a PostgresContainer("postgres:16") fixture (matching the built test_pg_integration.py:45) that applies the migration sequence to a fresh container, marked @pytest.mark.integration, auto-skipped locally, run in CI. Role-scoped engines built from the container URL for APPEND-1.

## Question 8 — Coverage config for the new package
How is `backend/database` covered without penalizing testcontainers-only code?

A) **Add `--cov=backend/database` to `pyproject` `addopts`**; keep the pure-logic modules (DbUrlGuard,
   MigrationChecksum, SchemaIntrospector normalization, FidelityComparator, the runner's substitution) **unit-covered
   to ≥90% (QA-6)**; the **DB-apply path exercised only via testcontainers in CI** is **omitted from unit-tier
   coverage** exactly like `pg_repository.py`/`parse_worker.py` (documented in the code summary). No coverage-threshold
   change.
B) Leave coverage config untouched (rejected — the new package would be uncounted).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — add --cov=backend/database to pyproject addopts; keep the pure-logic modules unit-covered to ≥90% (QA-6); the DB-apply path exercised only via testcontainers in CI is omitted from unit-tier coverage exactly like pg_repository.py/parse_worker.py (documented in the code summary). No coverage-threshold change.

## Question 9 — Depth + completion artifacts
Depth and outputs?

A) **Comprehensive** — full TDD build of all 6 components + every `NFR-DB-*` test at its tier; a
   `guide-docs/build/database/code/code-summary.md` (module list + test→target map + any flagged realization notes);
   `testresults.txt` refreshed; guide-state.md back-annotated; then the standardized **2-option** completion gate.
B) Minimal — skeleton only (rejected — this unit IS the persistence substrate; audit-store's auto-skipped integration
   tests need the real schema/roles).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — comprehensive: full TDD build of all 6 components + every NFR-DB-* test at its tier; a code-summary.md (module list + test→target map + any flagged realization notes); testresults.txt refreshed; guide-state.md back-annotated; then the standardized 2-option completion gate.

---

## 6. SEC-3 no-credentials confirmation (explicit)
**No credential VALUE appears anywhere in the generated code.** The **only** secret-adjacent tokens are the
**placeholder `${AUDIT_WRITER_PASSWORD}` / `${AUDIT_READER_PASSWORD}`** in the committed `0002_grants.sql`, and
**`os.environ[...]` reads** in the runner. Test role passwords for the ephemeral testcontainer are **throwaway
literals scoped to the test fixture** (as in the built `test_pg_integration.py`) — never production values, never
committed as config. The rendered/substituted SQL is **never logged**. The dev `.env` (real local connection string)
is **gitignored — enforcement owned by `secrets-config`** (named as a dependency; no value echoed here).

---

## 7. Constraints & settled items held (not re-opened)
- FD + approved `NFR-DB-*` + NFR Design patterns/components (C1–C6) + Infrastructure Design execution model are the
  substrate — Code-Gen realizes them, re-opening none. **C1's migration model + C2's grant text are realized, not
  re-designed.**
- **Reference-not-own (in reverse)**: `pg_repository.py` imported read-only by C5's test only; audit-store's test files
  not rewritten; `app_user` open-role skeleton only; rulebook registry absent; no consuming business logic touched.
- **DATA-5** (Postgres-only, `postgres:16`, no SQLite), **ATOMIC-1/COLOC-1** (one co-located DB/schema),
  **APPEND-1/SEC-4/SEC-5** (role grants), **BYTEA fidelity** (REPLAY-1/DET-2), **SEC-3** (no values), **CON-BR1**,
  **advisory-only**, **no LLM** — all held.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, OOS-7/OOS-8 doc commitments.

---

## 8. Next step (STOP here)
Fill the nine `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then generate the `database` code **TDD tests-first, leaf-first** per §4,
run the suite, write the code summary, back-annotate guide-state.md, and present the standardized completion + 2-option
message (Request Changes / Continue). **No code is generated until the answers are in and checked.**
