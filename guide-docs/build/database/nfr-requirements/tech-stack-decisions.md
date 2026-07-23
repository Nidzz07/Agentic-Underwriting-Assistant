# Tech-Stack Decisions — `database` (EPIC-6 / U15)

**Stage**: BUILD → NFR Requirements (per-unit) · companion to `nfr-requirements.md`
**Unit**: U15 `database` · **Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** (D6)
**Principle**: pin what the `NFR-DB-*` targets need to be **written and run at this unit's own
Code-Gen**; **defer** the migration tool + all provisioning/execution to Code-Gen / Infrastructure
Design. **No new production dependency.** **No credentials anywhere** (SEC-3).

---

## Decisions

### D1 — Schema authority + introspection: **SQLAlchemy 2.x Core**
- The authoritative production schema is expressed/introspected via **SQLAlchemy 2.x Core `MetaData`
  + reflection** — **already in the stack** (audit-store's `pg_repository.py` uses it). Introspection
  backs MIGRATE-1 (apply-from-empty → introspect) and FIDELITY-1 (introspect the migration-produced
  schema). **No new dependency.**

### D2 — Real-Postgres test substrate: **testcontainers PostgreSQL**
- Integration targets (ATOMIC-1, APPEND-1, BYTEA-1, MIGRATE-1, FIDELITY-1, SCOPE-1a) run on
  **testcontainers Postgres** — the **established pattern** from audit-store — `@pytest.mark.integration`,
  **auto-skipped locally** without Docker, **run in CI**. **No SQLite** in any tier (DATA-5). **Already
  in the stack.**

### D3 — Test framework: **pytest (+ existing helpers)**
- pytest, matching every prior unit. Structural/unit targets (DATA5-1 config guard, MIGRATE-2 checksum,
  SCOPE-1b rulebook-absent) run in the **normal unit tier** — no container. No new dependency.

### D4 — Migration **model** pinned; **tool deferred**
- The FD's **versioned, forward-only, one-authoritative-sequence** model is pinned. The **migration
  tool** (e.g. Alembic vs a raw-SQL runner) is **deferred to Code-Gen / Infrastructure Design** — the
  targets test the **model** (apply-from-empty; checksum immutability), not a specific tool's internals.

### D5 — Grant-DDL **text** = this unit's Code-Gen deliverable; **execution** deferred (fold #1)
- The **grant-DDL text** (`CREATE ROLE audit_writer …; GRANT INSERT, SELECT …; CREATE ROLE
  audit_reader …; GRANT SELECT …;`) is authored **alongside the migrations at THIS unit's Code-Gen**,
  so **NFR-DB-APPEND-1 is writable and runnable here** (applied onto the testcontainer). **Deferred to
  Infrastructure Design + `secrets-config`**: per-environment **execution** of those grants + the
  credential binding (which instance, Docker vs Render, secrets) — **SEC-3**. **APPEND-1 does not wait
  on Infrastructure Design.**

### D6 — Python **3.12** (pinned, build-wide)
- Matches the build-wide `.python-version` pin (NFKC/Unicode determinism, CON-DET-1). No change.

### D7 — DATA-5 config guard = a small **`database`-unit function**
- The `postgresql://`-scheme guard (reject `sqlite://` at config load) is a **pure unit-tier function
  of this unit** — no container, no deployment code. Repo-wide no-SQLite CI aggregation = `quality-gates`
  (referenced).

### D8 — FIDELITY-1 reference import: **read-only, reference-not-own (in reverse)** (fold #3)
- The fidelity test imports **`backend/audit_store/pg_repository.py`'s Table metadata read-only** as the
  **consuming reference** and extracts a **normalized column-spec dict** (`name / type / nullable / pk /
  fk / index`) for the compare — **CHECK constraints excluded** (fold #2). **No production code imports
  across this boundary**; `database` production code never imports `audit_store`, and `audit_store` never
  imports a `database` module — **no circular dependency**. `database` = schema **authority**;
  `pg_repository` metadata = consuming **reference**; the test = one-directional **consistency guard**.

### D9 — **No LLM** anywhere in `database`
- Pure schema/persistence substrate. No LLM client, no non-deterministic step. (Guardrail 3/5.)

### D10 — No new production dependency
- Everything above (SQLAlchemy 2.x, testcontainers, pytest, Python 3.12) is **already present**. This
  unit adds **no new production dependency**; the migration tool, if it turns out to add one, is a
  **deferred Code-Gen/Infra decision** (D4).

---

## Target → decision map

| Target | Backing decision(s) |
|---|---|
| NFR-DB-ATOMIC-1 / COLOC-1 | D1, D2 |
| NFR-DB-APPEND-1 | D2, **D5 (grant-DDL text owned here)** |
| NFR-DB-DATA5-1 | **D7 (config guard)**, D1/D2 (structural) |
| NFR-DB-MIGRATE-1 | D1, D2, D4 |
| NFR-DB-MIGRATE-2 | D3 (checksum, unit) |
| NFR-DB-FIDELITY-1 | D1, D2, **D8 (read-only reference import, CHECK excluded)** |
| NFR-DB-BYTEA-1 | D2 |
| NFR-DB-SCOPE-1 | D2 (app_user insert), D3 (rulebook absent) |
| NFR-DB-PERF-1 / OBS-1 | observed / referenced (observability-owned) |

---

## Deferred (to Code-Gen / Infrastructure Design + secrets-config)
- The migration **tool** (Alembic vs raw-SQL runner) — D4.
- Grant-DDL **execution** per environment + credential binding — D5 (Infra + `secrets-config`, SEC-3).
- Postgres **provisioning** + connection/pooling + Docker/Render topology — Infrastructure Design.

## Held (not re-opened)
- The frozen FD schema, BR-DB-1..14, and lifecycle model.
- audit-store's built code — imported read-only for FIDELITY-1 only; never edited (reference-not-own).
- No credentials/connection strings in any artifact (SEC-3).
