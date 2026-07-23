# NFR Requirements — `database` (EPIC-6 / U15)

**Stage**: BUILD → NFR Requirements (per-unit) · story-less shared infrastructure
**Unit**: U15 `database` — the shared PostgreSQL schema + migrations substrate.
**Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: comprehensive.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) —
**re-opening none of it**. Each `NFR-DB-*` target is a **pass/fail testable assertion** traced to its
FD rule (BR-DB-1..14) + invariant, with an explicit **test tier**. **No target waits on Infrastructure
Design's deliverables.** No credentials/connection strings appear here (SEC-3).

---

## 0. Central testability principle + direction of truth

- **`database`'s core invariants are DB-substrate properties only real PostgreSQL can prove** — atomic
  rollback, role-grant enforcement, type behavior, byte-fidelity. So the integration targets run on
  **real Postgres via testcontainers** and validate the **PRODUCTION migrations** (not audit-store's
  interim TEST-only DDL). Structural/config targets run in the **unit tier** (no container).
- **This unit owns every deliverable its targets need** — the **migration sequence**, the **grant-DDL
  text**, and the **config guard** are all **this unit's own Code-Gen deliverables**. Infrastructure
  Design owns only **per-environment execution + credential binding** (SEC-3). **No target requires
  Infrastructure Design's deliverables to be written or run.**
- **Direction of truth (fold #3, emphasis)**:
  - **`database` is the SCHEMA AUTHORITY** — its **migrations are the production source of truth** for
    the schema.
  - **`audit-store`'s `pg_repository.py` Table metadata is the CONSUMING REFERENCE** — it expresses the
    column set audit-store's built code depends on.
  - **`NFR-DB-FIDELITY-1` is a one-directional CONSISTENCY GUARD**, never an inversion of authority: it
    checks that the authority's schema still satisfies the consumer's expected columns. **Production
    code never imports across this boundary** — only the fidelity **test** imports `pg_repository`'s
    metadata, **read-only**. `audit_store` does not import a `database` module → **no circular
    dependency**.

---

## 1. Finalized `NFR-DB-*` targets (pass/fail; test tier stated)

### NFR-DB-ATOMIC-1 — co-location both-or-neither (BR-DB-2 / BR-DB-7; ATOMIC-1)
- **Assertion**: on real Postgres, with the schema materialized **from this unit's production
  migrations**, a two-row insert (`audit_record` + `applicant_profile_snapshot`) with a **fault
  injected on the 2nd insert** leaves **0 rows in BOTH tables** after rollback. **Pass** = both empty;
  **fail** = any partial row.
- **Independence**: the test drives its inserts off **reflection of the migration-produced schema** (or
  raw SQL) — it does **not** reuse audit-store's interim TEST DDL, and does **not** import
  `pg_repository`'s Table objects for the insert (that import is reserved for FIDELITY-1). audit-store's
  own `test_pg_integration.py` stays unchanged and separate.
- **Test tier**: **integration** (testcontainers Postgres; `@pytest.mark.integration`; auto-skip
  locally without Docker; runs in CI).

### NFR-DB-COLOC-1 — one database, one schema (BR-DB-7; structural)
- **Assertion**: the two audit tables are provably in **one database + one schema namespace**,
  reachable on one connection — no cross-database/service split in the write path (which is what makes
  ATOMIC-1's single transaction valid).
- **Test tier**: **structural** on the migration-produced schema (introspection of the schema/namespace
  of both tables; may piggyback the integration container or run as a DDL/structural assertion).

### NFR-DB-APPEND-1 — append-only via DB roles (BR-DB-4 / BR-DB-5; APPEND-1, SEC-4/SEC-5)
- **Assertion**: with the **production grant-DDL** applied on real Postgres — connecting as
  **`audit_writer`**: INSERT + SELECT succeed, **UPDATE and DELETE raise**; connecting as
  **`audit_reader`**: SELECT succeeds, **INSERT / UPDATE / DELETE all raise**.
- **Grant-DDL ownership (fold #1)**: the **grant-DDL text** (`CREATE ROLE …; GRANT …;`) is a
  **`database`-unit Code-Gen deliverable, authored alongside the migrations** — so **this target is
  writable and runnable at THIS unit's own Code-Gen**, applying that DDL onto the testcontainer.
  Infrastructure Design owns only **per-environment execution + credential binding** (which instance,
  Docker vs Render, secrets via `secrets-config`) — **SEC-3**. **APPEND-1 does not wait on
  Infrastructure Design.**
- **Test tier**: **integration** (testcontainers Postgres; real role connections).

### NFR-DB-DATA5-1 — PostgreSQL only, no SQLite (BR-DB-6; DATA-5)
- **Assertion (two layers)**: (i) **structural** — the migration DDL uses `BYTEA` / `TIMESTAMPTZ` /
  DB-roles and therefore **cannot faithfully apply on SQLite** (a test that pointing the schema at a
  SQLite target fails); (ii) **config guard** — the DB URL must be a **`postgresql://` scheme**; a
  `sqlite://` URL is **rejected at config load** (a pure `database`-unit function).
- **Testable-today note**: the config guard is a **unit-tier** function of this unit — writable and
  runnable with **no container and no deployment code**. Repo-wide "no SQLite anywhere" CI aggregation
  is **`quality-gates`**' concern (referenced, not owned here).
- **Test tier**: **unit** (config guard) + **structural/integration** (DDL-on-SQLite-fails).

### NFR-DB-MIGRATE-1 — apply-from-empty + forward-only (business-logic-model §1)
- **Assertion**: applying the **full migration sequence from an empty database** yields the **exact
  expected schema** (introspected schema == expected column/constraint set); the model is
  **forward-only** (a fresh apply is always the source of truth — no down-migration relied upon for
  correctness).
- **Test tier**: **integration** (fresh testcontainers Postgres; introspect after apply).

### NFR-DB-MIGRATE-2 — published-migration immutability (business-logic-model §1)
- **Assertion**: a **content-checksum** over the applied migration files detects any **in-place edit of
  a published migration** — an edited step changes its checksum → **test fails** (mirrors the
  append-only discipline: change = a new migration, never a mutation).
- **Test tier**: **unit** (hash the migration files; compare to the recorded checksum set — no
  container).

### NFR-DB-FIDELITY-1 — ongoing column-for-column consistency guard (BR-DB / schema authority)
- **Assertion**: an automated regression test **introspects the migration-produced schema** and
  compares it — **column-for-column** — against the **column set audit-store's `pg_repository.py` Table
  metadata expects**, imported **read-only**. **Drift on EITHER side fails**: a migration that changes a
  column, OR a `pg_repository.py` edit expecting a column the schema lacks. Converts the one-time 18/18
  verification into a **permanent automated invariant**.
- **Comparison scope (fold #2 — explicit)**: the compared attributes are **name / PostgreSQL type /
  nullability / PK / FK / index ONLY. CHECK constraints are EXCLUDED from the comparison.** This is the
  mechanism that keeps an **optional** `action`/`status` CHECK from ever causing a false mismatch
  (`pg_repository.py` has none), and correspondingly keeps **`role`'s absence of a CHECK** from being
  flagged either.
- **Direction of truth**: `database` migrations = authority; `pg_repository` metadata = consuming
  reference; this test = one-directional consistency guard (imports read-only; no production import
  across the boundary; no circular dependency).
- **Implementation guidance (non-binding)**: extract a **normalized column-spec dict**
  (`{name, type, nullable, pk, fk, index}`) from `pg_repository`'s Table objects for the compare —
  resilient to non-schema refactors; genuine **schema drift remains the intended tripwire**.
- **Test tier**: **integration** (introspect the real migration-produced schema) + read-only import of
  the consuming metadata.

### NFR-DB-BYTEA-1 — opaque byte-fidelity round-trip (BR-DB-10; REPLAY-1 / DET-2)
- **Assertion**: a **round-trip** of arbitrary CANON-SER byte sequences through the `rule_results` /
  `profile_canonical` `BYTEA` columns — **including bytes a `JSONB` column would re-order or re-encode**
  (non-canonical key order, number formatting, whitespace) — reads back **byte-identical**; the DB
  performs **no normalization**. `content_hash` recomputed over the readback matches.
- **Independence**: inserts driven off reflection of the migration-produced schema (not the
  `pg_repository` import).
- **Test tier**: **integration** (testcontainers Postgres round-trip).

### NFR-DB-SCOPE-1 — deferred/foundational scope, no consumer business logic (BR-DB-11/12/14)
- **Assertion — only**: (a) the `app_user` skeleton **exists** and `role` is **extensible** — inserting
  a **novel role value** (e.g. `admin`) **succeeds without a migration and without any CHECK rejecting
  it** (the NEGATIVE property proving `role` carries no closing CHECK); (b) the **rulebook-version table
  does not exist** (deferred slot).
- **Explicitly NOT tested**: nothing about auth-rbac's authn/permission logic or rules-engine's
  evaluation. **`role` no-CHECK / `action`,`status` MAY-CHECK consistency**: **no target asserts a CHECK
  EXISTS on `action`/`status`** (that stays optional per BR-DB-9 — "may", not "must"); the only
  CHECK-related assertion is the `role` **negative** one.
- **Test tier**: **integration** (app_user novel-value insert) + **structural** (rulebook table absent).

### NFR-DB-PERF-1 — soft budget, observed not gated (infra)
- **Assertion**: migration-apply + insert latency is **observed against a soft budget** — **no hard
  SLO** at the schema-unit tier. No demographic-derived metric (CON-BR1).
- **Test tier**: **observed** (measured, non-gating).

### NFR-DB-OBS-1 — observability owned elsewhere (referenced)
- **Assertion**: DB metrics/traces are **`observability`'s** concern — **N/A here** (referenced, not
  owned). The schema emits no application telemetry of its own.
- **Test tier**: **N/A**.

---

## 2. Traceability (target → FD rule → invariant)

| Target | FD rule | Invariant | Tier |
|---|---|---|---|
| NFR-DB-ATOMIC-1 | BR-DB-2, BR-DB-7 | ATOMIC-1 | integration |
| NFR-DB-COLOC-1 | BR-DB-7 | ATOMIC-1 co-location | structural |
| NFR-DB-APPEND-1 | BR-DB-4, BR-DB-5 | APPEND-1, SEC-4/SEC-5 | integration |
| NFR-DB-DATA5-1 | BR-DB-6 | DATA-5 | unit + structural |
| NFR-DB-MIGRATE-1 | business-logic-model §1 | forward-only migrations | integration |
| NFR-DB-MIGRATE-2 | business-logic-model §1 | migration immutability | unit |
| NFR-DB-FIDELITY-1 | BR-DB-1/2/3/9; schema authority | column-for-column consistency | integration |
| NFR-DB-BYTEA-1 | BR-DB-10 | REPLAY-1 / DET-2 byte-fidelity | integration |
| NFR-DB-SCOPE-1 | BR-DB-11/12/14 | reference-not-own (reverse) | integration + structural |
| NFR-DB-PERF-1 | — | soft budget | observed |
| NFR-DB-OBS-1 | — | observability-owned | N/A |

---

## 3. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (schema unit)** | No untrusted input parsed; stored payloads are already-validated opaque bytes. |
| Prompt-injection defense | **N/A** | No LLM/prompt path in `database`. |
| Secrets management | **Compliant** | SEC-3 — no credentials in schema/tests; grant-DDL execution + credential binding deferred to `secrets-config`. |
| Read-only DB access for audit role | **Compliant** | NFR-DB-APPEND-1 — `audit_reader` SELECT-only, verified against real roles. |
| Audit logging | **Compliant** | NFR-DB-APPEND-1/ATOMIC-1 substrate underpins the CON-AUDIT-1 append-only trail. |

No blocking finding.

---

## 4. Settled items held (not re-opened)
- The frozen FD (schema + BR-DB-1..14 + lifecycle model) is the substrate — targets build **on** it.
- audit-store's built code/record shape stays frozen — FIDELITY-1 imports `pg_repository` metadata
  **read-only**; no consuming-unit code is edited (reference-not-own, in reverse).
- Grant-DDL **text** = this unit's Code-Gen deliverable (APPEND-1 needs no Infra to write/run);
  grant-DDL **execution** + provisioning + connection/credential binding = Infrastructure Design +
  `secrets-config` (SEC-3).
- FIDELITY-1 comparison scope excludes CHECK constraints; `action`/`status` CHECK stays optional;
  `role` no-CHECK verified via the negative property.
- DATA-5 (Postgres-only, structural + config guard); SEC-4/SEC-5 (read-only auditor, append-only);
  REPLAY-1/DET-2 (BYTEA byte-fidelity); CON-BR1 (no demographic-driven column/metric); no LLM.
- Infrastructure Design remains a distinct, REAL later stage.
