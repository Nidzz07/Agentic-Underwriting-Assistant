# NFR Requirements Plan (Part 1) — `database` (EPIC-6 / U15)

**Phase / Stage**: BUILD → NFR Requirements, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `database` (story-less infra, the FIRST post-cluster unit) · **FD ✅ (approved 2026-07-06)**
→ **NFR Requirements ← here** → NFR Design → **Infrastructure Design (REAL, comprehensive — NOT a skip)** → Code-Gen.
**Unit**: U15 `database` — the shared PostgreSQL schema + migrations substrate (audit tables + `app_user` skeleton +
reserved rulebook slot).
**Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** (D6).
**Depth**: **comprehensive** (invariant-bearing infra — DATA-5, ATOMIC-1 co-location, append-only, SEC-4 role grants).
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR-Requirements artifacts generated this stage. Stop after this plan.**

This plan follows `.project-guide-rule-details/build/nfr-requirements.md` (Part 1) + the plan-then-generate discipline.
It is built **ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) — **re-opening
none of it**. Every `NFR-DB-*` target below is drafted to be **pass/fail testable**; the exact set is finalized into
`nfr-requirements.md` only after the `[Answer]:` tags are filled.

---

## 1. Unit context (analyzed)

### 1.1 What NFR Requirements builds ON (frozen — NOT re-opened)
- **Frozen FD schema**: `audit_record` (14 cols) + `applicant_profile_snapshot` (4 cols, FK-child) **column-for-column
  with the built `backend/audit_store/pg_repository.py`** (18/18 verified); `app_user` foundational skeleton (**open
  `role`**); the **reserved rulebook-version slot** (deferred, no columns).
- **Frozen FD rules** (`business-rules.md`): BR-DB-1..14 — PK/FK/NOT-NULL (1/2/3); append-only two-layer (4);
  `audit_writer`/`audit_reader` semantics (5); DATA-5 no-SQLite per-tier (6); co-location one-DB/schema/transaction (7);
  OOS-7 `status=active`-only + optional DB default (8); `action`/`status` varchar-not-ENUM (9); opaque BYTEA byte-fidelity
  (10); `underwriter_id` logical-ref-not-DB-FK (11); `app_user.role` open (12); SEC-3 no-secrets (13); rulebook deferred (14).
- **Frozen FD lifecycle** (`business-logic-model.md`): versioned forward-only migrations = the schema source of truth;
  the connection/transaction model that makes ATOMIC-1 valid; the **explicit FD↔Infrastructure-Design boundary**.

### 1.2 Dependencies & interfaces (reference-not-own, in reverse)
- **Serves** `audit-store` (COMPLETE): its `pg_repository.py` reads/writes this schema. The **column set is the
  consuming contract** — the fidelity target (Q5) guards it as an ongoing regression property.
- **Serves** `auth-rbac` (Phase-1, **not yet designed**): the `app_user` **skeleton** only — NFR targets assert the
  skeleton **exists + `role` is extensible**, and test **nothing** about auth-rbac's authn/permission logic (Q7).
- **Serves** `rules-engine` / `admin-cli`: the rulebook-version **slot is deferred** — NFR targets assert **no table
  exists** and nothing depends on one (Q7).
- **Owned elsewhere (referenced, not built here)**: grant **DDL execution** + Postgres **provisioning** +
  connection/credential **binding** = **Infrastructure Design + `secrets-config`** (SEC-3); the **CI no-SQLite guard**
  aggregation = `quality-gates`; DB **metrics/traces** = `observability`. This unit's NFR tests validate the **schema +
  migrations + role semantics**, not the deployment topology.

### 1.3 Guardrails held (skill)
- **DATA-5** (PostgreSQL everywhere, no SQLite — dialect-drift guard); **ATOMIC-1** (co-location → single-transaction
  both-or-neither); **CON-AUDIT-1 / APPEND-1 / SEC-4 / SEC-5** (append-only substrate + read-only auditor role);
  **REPLAY-1 / DET-2** (opaque BYTEA byte-fidelity so replay never false-mismatches); **CON-BR1** (storage ≠ influence —
  the schema adds no demographic-driven column/index); **SEC-3** (no credentials in schema/tests); **advisory-only**
  naming. **No LLM anywhere in `database`.**

### 1.4 The distinguishing NFR theme for this unit
Unlike the four cluster units (whose invariants were unit-testable against fakes), **`database`'s core invariants are
DB-substrate properties that only real PostgreSQL can prove** — atomic rollback, role-grant enforcement, type behavior,
byte-fidelity. So the NFR set leans on **real-Postgres integration tests (testcontainers)**, and it **validates the
PRODUCTION migrations** (not audit-store's interim TEST-only DDL) — which is what turns audit-store's auto-skipped-locally
integration guarantees into a production-schema-backed fact.

---

## 2. Draft `NFR-DB-*` targets (pass/fail testable — finalized after the answers)

Each target names its invariant, the FD rule it realizes, and a **pass/fail test shape**. IDs provisional.

### Co-location & atomicity
- **NFR-DB-ATOMIC-1** (BR-DB-2/7; ATOMIC-1): on **real Postgres (testcontainers)**, a two-row insert
  (`audit_record` + `applicant_profile_snapshot`) under **fault injection mid-transaction** (e.g. forced error / duplicate
  PK on the 2nd insert) leaves **0 rows in BOTH tables** — genuine both-or-neither rollback. **Against the production
  migration-produced schema**, not the interim TEST DDL. *(Test tier: integration, real Postgres. See Q1.)*
- **NFR-DB-COLOC-1** (BR-DB-7, structural): the two audit tables are provably in **one database + one schema**,
  reachable on one connection (a structural/DDL assertion — no cross-database/service split in the write path).

### Append-only & role enforcement
- **NFR-DB-APPEND-1** (BR-DB-4/5; APPEND-1, SEC-4/SEC-5): with the **production grant DDL** applied on real Postgres,
  connecting as **`audit_writer`**: INSERT + SELECT succeed; **UPDATE and DELETE raise**. Connecting as **`audit_reader`**:
  SELECT succeeds; **INSERT / UPDATE / DELETE all raise**. *(Integration, real Postgres roles. See Q2.)*

### DATA-5 (no SQLite)
- **NFR-DB-DATA5-1** (BR-DB-6): the schema is **structurally Postgres-only** — it uses types/roles SQLite cannot
  faithfully represent (`BYTEA`, `TIMESTAMPTZ`, DB roles/grants), and a **checkable guard** rejects a SQLite target
  (the exact checkable form — a test that the DDL/migration fails on SQLite, and/or a config guard rejecting a `sqlite://`
  URL — is **Q3**). CI aggregation referenced to `quality-gates`.

### Migration model
- **NFR-DB-MIGRATE-1** (business-logic-model §1): **applying the full migration sequence from an empty database produces
  the exact expected schema** (introspected/reflected schema == expected), and the sequence is **forward-only**. *(See Q4.)*
- **NFR-DB-MIGRATE-2** (immutability): a **published migration is never edited in place** — caught by a
  **content-checksum** over the applied migration set (an edited published step changes its checksum → test fails). *(Q4.)*

### Column-for-column fidelity (ongoing regression, not one-time)
- **NFR-DB-FIDELITY-1** (BR-DB / schema authority; the user's key ask): an **automated regression test** compares the
  **migration-produced schema** (introspected) against the **column set audit-store's `pg_repository.py` expects**
  (names / PostgreSQL types / nullability / PK / FK / index for both tables). **Future drift on either side** — the
  migrations OR `pg_repository.py` — **fails the test**. Not a one-time check. *(Source-of-truth + location = Q5.)*

### BYTEA opacity / byte-fidelity
- **NFR-DB-BYTEA-1** (BR-DB-10; REPLAY-1/DET-2): a **round-trip** of arbitrary CANON-SER bytes through the `BYTEA`
  columns (incl. byte sequences a `JSONB` column would re-order/re-encode) reads back **byte-identical** — the DB performs
  **no normalization/transformation**. *(Integration, real Postgres. See Q6.)*

### Scoped exclusions (reference-not-own, in reverse)
- **NFR-DB-SCOPE-1** (BR-DB-11/12/14): the only assertions about the deferred/foundational consumers are: (a) the
  `app_user` skeleton **exists** and `role` is **extensible** (a novel role value — e.g. `admin` — **inserts without a
  migration and without a CHECK rejecting it**); (b) the rulebook-version **table does not exist** (deferred slot). **No
  target tests auth-rbac's authn/permission logic or rules-engine's evaluation.** *(Consistency note: `role` must therefore
  carry NO closing CHECK — unlike `action`/`status` which MAY — see Q7.)*

### Perf / observability (soft)
- **NFR-DB-PERF-1** (soft): migration-apply + insert latency **observed against a soft budget, not gated** (infra unit —
  no hard perf SLO here). **NFR-DB-OBS-1**: DB metrics/traces are **`observability`'s** concern — **N/A / referenced**,
  not owned here. *(See Q8.)*

---

## 3. Clarifying questions (Step — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide the
**testable-target shape + tech stack** — they do **not** re-open the frozen FD.

## Question 1 — ATOMIC-1 test: against the PRODUCTION migrations, on real Postgres
How is NFR-DB-ATOMIC-1 made pass/fail, and against which schema?

A) **An integration test OWNED BY the `database` unit** materializes the schema **from this unit's production migrations**
   (not audit-store's interim TEST DDL) on **real Postgres via testcontainers**, then drives a two-row insert with a
   **fault injected on the 2nd insert** and asserts **both tables are empty** after rollback. This proves the **production**
   schema satisfies ATOMIC-1 (turning audit-store's interim-DDL guarantee into a production-backed one). Auto-skips locally
   when Docker is absent; runs in CI. *(audit-store keeps its own separate `test_pg_integration.py` unchanged.)*
B) Reuse audit-store's existing `test_pg_integration.py` as-is (rejected — it exercises the interim TEST DDL, not the
   production migrations; the database unit must validate its OWN schema).
C) Unit-test the rollback against an in-memory fake (rejected — atomicity is a real-DB property; a fake cannot prove it).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — an integration test owned by the database unit materializes the schema from this unit's production migrations (not audit-store's interim TEST DDL) on real Postgres via testcontainers, then drives a two-row insert with a fault injected on the 2nd insert and asserts both tables are empty after rollback. Proves the production schema satisfies ATOMIC-1. Auto-skips locally without Docker, runs in CI. audit-store keeps its own separate test_pg_integration.py unchanged.

## Question 2 — Append-only role enforcement: against the production grant DDL
How is NFR-DB-APPEND-1 tested?

A) **The `database` unit's integration suite applies the production role-grant DDL** (`audit_writer` = INSERT+SELECT;
   `audit_reader` = SELECT only) on real Postgres, then **connects as each role** and asserts: `audit_writer` INSERT/SELECT
   succeed, **UPDATE/DELETE raise**; `audit_reader` SELECT succeeds, **INSERT/UPDATE/DELETE raise**. This proves the FD's
   role **semantics** (BR-DB-5) are realized by the actual grant DDL. (The grant DDL is authored at NFR/Infra as the
   deliverable; its per-instance **execution** stays Infra + `secrets-config` — SEC-3.)
B) Assert append-only only at the service layer (rejected — misses the DB-role half APPEND-1 requires).
C) Trust the grants without a test (rejected — the whole point is a pass/fail guarantee).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — the database unit's integration suite applies the production role-grant DDL (audit_writer = INSERT+SELECT; audit_reader = SELECT only) on real Postgres, then connects as each role and asserts audit_writer INSERT/SELECT succeed and UPDATE/DELETE raise; audit_reader SELECT succeeds and INSERT/UPDATE/DELETE all raise. Proves the FD's role semantics are realized by the actual grant DDL; execution stays Infra + secrets-config.

## Question 3 — DATA-5 no-SQLite: the best checkable form
How is "PostgreSQL only, no SQLite" made a **checkable** property (not just prose)?

A) **Two-layer**: (i) **structural** — the schema uses `BYTEA` / `TIMESTAMPTZ` / DB-roles, so the migration DDL
   **cannot apply on SQLite** (a test asserting the DDL/typing is Postgres-only, e.g. attempting the schema on a SQLite URL
   fails); (ii) a **config guard** that the app/test DB URL must be a `postgresql://` scheme — a `sqlite://` URL is
   **rejected at startup/config load**. The repo-wide CI aggregation of "no SQLite anywhere" is referenced to
   `quality-gates` (not owned here). This makes DATA-5 both structurally true and explicitly guarded.
B) Only the CI guard (no structural test) — weaker; misses a local misconfig.
C) Documentation only, no structural or config check (rejected — DATA-5 must be checkable).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — two-layer: (i) structural — the schema uses BYTEA/TIMESTAMPTZ/DB-roles so the migration DDL cannot apply on SQLite (tested); (ii) a config guard that the app/test DB URL must be postgresql:// scheme, rejecting sqlite:// at startup/config load. Repo-wide CI aggregation referenced to quality-gates, not owned here.

## Question 4 — Migration model testability (forward-only + immutability + apply-from-empty)
Which properties are pinned as pass/fail?

A) **Three**: (i) **apply-from-empty** — running the full sequence against a fresh Postgres yields the **exact expected
   schema** (introspected schema == expected column/constraint set); (ii) **forward-only** — the model relies on no
   down-migration for correctness (a fresh apply is always the source of truth); (iii) **immutability** — a
   **content-checksum** over the applied migration files detects any **in-place edit of a published migration** (edited
   step → changed checksum → test fails), mirroring the append-only discipline. The migration **tool** stays deferred to
   Code-Gen/Infra (the tests target the *model*, not a specific tool's internals).
B) Only apply-from-empty; skip the immutability checksum (weaker — an edited published migration would slip through).
C) No migration tests at FD/NFR; defer entirely to Code-Gen (rejected — the model is invariant-bearing).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — three properties: (i) apply-from-empty (running the full sequence against fresh Postgres yields the exact expected schema, introspected); (ii) forward-only (a fresh apply is always the source of truth, no down-migration reliance); (iii) immutability via content-checksum over applied migration files (an edited published step changes its checksum → test fails). Migration tool stays deferred to Code-Gen/Infra.

## Question 5 — Column-for-column fidelity as an ONGOING regression (the key ask)
What is the source of truth, and where does the guard live, so future drift is caught automatically?

A) **A `database`-unit regression test introspects the migration-produced schema** and compares it, **column-for-column**
   (name / PostgreSQL type / nullability / PK / FK / index), against the **column set audit-store's `pg_repository.py`
   `Table` metadata expects** (imported read-only as the consuming contract). **Drift on EITHER side fails**: a migration
   that changes a column, OR a `pg_repository.py` edit that expects a column the schema lacks. Runs on real Postgres in CI.
   This makes the one-time 18/18 verification a **permanent, automated invariant** — not a doc note. *(Reference-not-own:
   the test IMPORTS pg_repository's metadata read-only; it does not edit audit-store.)*
B) Keep the 18/18 check as a one-time documented verification only (rejected — the user explicitly wants ongoing drift
   detection, not a snapshot).
C) Compare against a hand-maintained column list duplicated in the database unit (rejected — a third copy that itself
   drifts; the built `pg_repository.py` metadata is the real consuming contract).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a database-unit regression test introspects the migration-produced schema and compares it column-for-column (name/PostgreSQL type/nullability/PK/FK/index) against the column set audit-store's pg_repository.py Table metadata expects (imported read-only). Drift on either side fails. Runs on real Postgres in CI. Converts the one-time 18/18 verification into a permanent automated invariant. Reference-not-own: imports metadata read-only, never edits audit-store.

## Question 6 — BYTEA opacity / byte-fidelity round-trip
How is NFR-DB-BYTEA-1 tested?

A) **A real-Postgres round-trip**: write arbitrary CANON-SER byte sequences into the `rule_results` / `profile_canonical`
   `BYTEA` columns (**including bytes that a `JSONB` column would re-order or re-encode** — e.g. non-canonical key order,
   number formatting, whitespace), read them back, and assert **byte-identical**. Proves the DB performs **no
   normalization** — the property REPLAY-1/DET-2 depend on. `content_hash` recomputed over the readback matches.
B) Assert the column is typed `BYTEA` only (weaker — type alone; doesn't prove no round-trip transformation on real data).
C) Skip — trust that BYTEA is opaque (rejected — the whole risk is a silent transform breaking replay).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a real-Postgres round-trip: write arbitrary CANON-SER byte sequences into the BYTEA columns (including bytes a JSONB column would re-order/re-encode), read them back, assert byte-identical. Proves the DB performs no normalization — the property REPLAY-1/DET-2 depend on. content_hash recomputed over the readback matches.

## Question 7 — Scoped exclusions + the `role` no-CHECK consistency
How are the deferred/foundational consumers bounded, and how is `role` extensibility kept consistent with any CHECK
constraints?

A) **NFR-DB-SCOPE-1 asserts only**: (a) the `app_user` skeleton **exists** and `role` is **extensible** — inserting a
   **novel role value** (e.g. `admin`) **succeeds without a migration and without any CHECK rejecting it**; (b) the
   **rulebook-version table does not exist** (deferred slot). **No target tests auth-rbac authn/permissions or rules-engine
   evaluation.** **Consistency pin**: because `role` must stay open, it carries **NO closing CHECK constraint** — whereas
   `action` / `status` (closed known sets) **MAY** carry an optional CHECK on their allowed values (BR-DB-9). This keeps
   fold #1 (open role) and fold #3 (varchar action/status) mutually consistent.
B) Add a CHECK on `role` limiting it to {underwriter, auditor} (rejected — would CLOSE the dimension, contradicting fold #1;
   forces auth-rbac into a breaking migration to add `admin`).
C) Test nothing about the skeleton/slot (rejected — leaves the reserved substrate unverified).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — NFR-DB-SCOPE-1 asserts only: (a) the app_user skeleton exists and role is extensible (inserting a novel role value like admin succeeds without a migration and without any CHECK rejecting it); (b) the rulebook-version table does not exist. No target tests auth-rbac authn/permissions or rules-engine evaluation. Consistency pin: role carries NO closing CHECK constraint, whereas action/status MAY carry an optional CHECK — keeping fold #1 (open role) and fold #3 (varchar action/status) mutually consistent.

## Question 8 — Perf / observability posture (infra unit)
What perf/obs targets apply?

A) **Soft/observed, not gated**: migration-apply + insert latency observed against a **soft budget** (no hard SLO — this
   is schema infra); DB metrics/traces are **`observability`'s** concern (**N/A / referenced here**). No demographic-derived
   metric (CON-BR1). Keeps the NFR set honest — no unmeasurable/aspirational target.
B) Define a hard latency SLO here (rejected — premature; belongs to observability/perf tuning, not the schema unit).
C) Omit perf/obs entirely (acceptable-ish, but A's explicit soft/N-A framing is clearer for the compliance summary).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — soft/observed, not gated: migration-apply + insert latency observed against a soft budget (no hard SLO); DB metrics/traces are observability's concern (N/A/referenced here). No demographic-derived metric (CON-BR1).

## Question 9 — Test framework + real-Postgres substrate
What substrate do the integration targets run on?

A) **pytest + testcontainers PostgreSQL** (the exact pattern audit-store already uses), `@pytest.mark.integration`,
   **auto-skipped locally** when Docker/testcontainers are unavailable, **run in CI**. **No SQLite** in any tier (DATA-5).
   Structural/reflection tests that need no container run in the normal unit tier. Python **3.12**.
B) A shared/external Postgres for tests (rejected — non-hermetic; testcontainers is the established hermetic pattern).
C) SQLite for test convenience (rejected — DATA-5).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — pytest + testcontainers PostgreSQL (audit-store's established pattern), @pytest.mark.integration, auto-skipped locally without Docker, run in CI. No SQLite in any tier. Structural/reflection tests needing no container run in the normal unit tier. Python 3.12.

## Question 10 — Tech stack (companion `tech-stack-decisions.md`)
What does the NFR tech-stack pin vs defer?

A) **Pin**: SQLAlchemy 2.x Core for the authoritative schema/`MetaData` + introspection (already in the stack via
   audit-store); testcontainers Postgres for integration (already in the stack); Python 3.12; **no new production
   dependency**. **Defer** (to Code-Gen / Infrastructure Design): the **migration tool** (Alembic vs raw-SQL runner) and
   the grant-DDL **execution** + connection/credential binding (Infra + `secrets-config`, SEC-3). **Reference-not-own**:
   imports audit-store's `pg_repository.py` metadata **read-only** for the fidelity test; edits no shared/consuming code.
B) Pin the migration tool now (rejected — the FD deferred it deliberately; NFR shouldn't over-commit).
C) Introduce a new ORM/migration framework (rejected — no need; SQLAlchemy is already present).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — pin: SQLAlchemy 2.x Core for the authoritative schema/MetaData + introspection (already in the stack); testcontainers Postgres for integration (already in the stack); Python 3.12; no new production dependency. Defer: the migration tool (Alembic vs raw-SQL runner) and grant-DDL execution + connection/credential binding (Infra + secrets-config). Reference-not-own: imports audit-store's pg_repository.py metadata read-only for the fidelity test.

## Question 11 — Depth confirmation
What depth for this NFR Requirements stage?

A) **Comprehensive** — full pass/fail `NFR-DB-*` set across atomicity, append-only/roles, DATA-5, migrations, fidelity,
   byte-opacity, scoped exclusions, and soft perf/obs, each traced to its FD rule + invariant, matching the unit's
   invariant weight.
B) Standard — a shorter target list.
C) Minimal — targets sketch only.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — comprehensive. Full pass/fail NFR-DB-* set across atomicity, append-only/roles, DATA-5, migrations, fidelity, byte-opacity, scoped exclusions, and soft perf/obs, each traced to its FD rule + invariant, matching the unit's invariant weight.

---

## 4. Constraints & settled items held (not re-opened)
- The **frozen FD** (schema + BR-DB-1..14 + lifecycle model) is the substrate — NFR builds testable targets **on** it,
  re-opening nothing.
- **audit-store's built record shape + code stay frozen** — the fidelity target imports `pg_repository.py` metadata
  **read-only**; no consuming-unit code is edited (reference-not-own, in reverse).
- **ATOMIC-1 co-location** + the **`audit_writer`/`audit_reader` grants** are validated **against the production
  migrations** here — the register carry-forward being made a pass/fail guarantee.
- **Deferred/foundational scope**: `app_user` skeleton (open `role`, no closing CHECK) + rulebook-version slot (no table)
  — asserted as existing/deferred only; **no consumer business logic tested**.
- **DATA-5** (Postgres-only, structurally + config-guarded); **SEC-3** (no credentials in schema/tests — the open `.env`
  connection string is never echoed); **SEC-4/SEC-5** (read-only auditor role, append-only); **REPLAY-1/DET-2** (BYTEA
  byte-fidelity); **CON-BR1** (no demographic-driven column/metric). **No LLM in `database`.**
- **Infrastructure Design remains a distinct, REAL later stage** — grant-DDL execution + Postgres provisioning +
  connection/pooling + Docker/Render topology; NFR pins the **testable properties + the deliverable grant DDL/migration
  model**, not the provisioning.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, the OOS-7/OOS-8 doc commitments.

---

## 5. Next step (STOP here)
Fill the eleven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then generate the two `database` NFR Requirements artifacts
(`nfr-requirements.md` + `tech-stack-decisions.md`) and present the standardized 2-option completion message. **No NFR
Requirements artifacts or code are generated until the answers are in and checked.**
