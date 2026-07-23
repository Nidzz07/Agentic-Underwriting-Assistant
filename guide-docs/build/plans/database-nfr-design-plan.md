# NFR Design Plan (Part 1) — `database` (EPIC-6 / U15)

**Phase / Stage**: BUILD → NFR Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `database` (story-less infra) · FD ✅ · **NFR Requirements ✅ (approved 2026-07-06)**
→ **NFR Design ← here** → **Infrastructure Design (REAL, comprehensive — NOT a skip)** → Code-Gen.
**Unit**: U15 `database` · **Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: comprehensive.
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR-Design artifacts generated this stage. Stop after this plan.**

This plan follows `.project-guide-rule-details/build/nfr-design.md` (Part 1) + the plan-then-generate discipline. It
maps each approved **`NFR-DB-*` target → a named design pattern**, built **ON** the frozen FD
(`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) **and** the approved
`nfr-requirements.md` / `tech-stack-decisions.md` — **re-opening neither**. Every pattern is verifiable by the
target's stated test tier; **no pattern requires Infrastructure Design's deliverables** to exist.

---

## 1. Unit context (analyzed)

### 1.1 What NFR Design builds ON (frozen — NOT re-opened)
- **Frozen FD**: `audit_record` (14) + `applicant_profile_snapshot` (4, FK-child) column-for-column with built
  `pg_repository.py`; `app_user` skeleton (open `role`); reserved rulebook slot; BR-DB-1..14; the versioned
  forward-only migration model + connection/transaction model + the FD↔Infra boundary.
- **Approved NFR targets**: ATOMIC-1, COLOC-1, APPEND-1, DATA5-1, MIGRATE-1, MIGRATE-2, FIDELITY-1, BYTEA-1,
  SCOPE-1, PERF-1, OBS-1 — each pass/fail with a stated tier; the **direction-of-truth** (database = schema
  authority; audit-store `pg_repository` metadata = consuming reference; FIDELITY-1 = one-directional consistency
  guard); grant-DDL **text** = this unit's Code-Gen deliverable (APPEND-1 needs no Infra); FIDELITY-1 comparison
  **excludes CHECK**.

### 1.2 Reference-not-own (in reverse)
- **Imports read-only for FIDELITY-1 ONLY**: `backend/audit_store/pg_repository.py` Table metadata (the consuming
  reference). No production code imports across the boundary; `audit_store` never imports `database` → no circular
  dependency. **No consuming-unit code is edited.**
- **Already-in-stack** (no new dep): SQLAlchemy 2.x Core (schema/introspection), testcontainers Postgres, pytest.
- **Deferred (Code-Gen / Infra + `secrets-config`)**: the migration **tool**; grant-DDL **execution** + credential
  binding; Postgres provisioning + connection/pooling + Docker/Render topology (SEC-3).

### 1.3 Central pattern principle
Every pattern is structurally verifiable by its target's tier — **integration** patterns on the **migration-produced
schema** (testcontainers), **unit/structural** patterns with no container. **The database unit's own tests drive
inserts off reflection of the migration-produced schema** (reserving the `pg_repository` import for FIDELITY-1's
comparison only) — keeping structural independence from audit-store's interim TEST DDL.

### 1.4 Guardrails held (skill)
DATA-5 (Postgres-only), ATOMIC-1 (co-location single-transaction), CON-AUDIT-1/APPEND-1/SEC-4/SEC-5 (append-only +
read-only auditor role), REPLAY-1/DET-2 (BYTEA byte-fidelity), CON-BR1 (no demographic column/metric), SEC-3 (no
credentials), advisory-only naming. **No LLM anywhere in `database`.**

---

## 2. Draft pattern map (each `NFR-DB-*` → a named pattern — finalized after the answers)

| Target | Named design pattern |
|---|---|
| ATOMIC-1 / COLOC-1 | **SingleTransactionCoLocationPattern** — one connection, one `BEGIN`, both inserts, `COMMIT`/`ROLLBACK` both-or-neither on the migration-produced schema (same reasoning as audit-store's, but validating THIS unit's production schema; inserts via reflected Table handles) |
| APPEND-1 | **GrantDDLInMigrationPattern** — the `CREATE ROLE`/`GRANT` text is a dedicated step in the migration sequence; tests apply the full sequence incl. grants onto the container, then connect as each role and assert the write matrix |
| DATA5-1 | **DbUrlGuardPattern** (a pure `require_postgres_url` validator at config load) + **PostgresOnlyTypePattern** (BYTEA/TIMESTAMPTZ/roles → structurally cannot run on SQLite) |
| MIGRATE-1 | **ForwardOnlyMigrationSequencePattern** — ordered immutable steps; apply-from-empty → introspect → exact expected schema |
| MIGRATE-2 | **ChecksumImmutabilityPattern** — a committed `{migration_file: sha256}` manifest; recompute + compare; edited published step fails; a NEW migration is an append |
| FIDELITY-1 | **SchemaIntrospectionComparatorPattern** — introspect the live migration-produced schema → normalized column-spec dict; read `pg_repository` metadata read-only → normalized dict; compare (name/type/nullability/PK/FK/index; **CHECK excluded**); drift either side fails |
| BYTEA-1 | **OpaqueRoundTripProbePattern** — an adversarial byte-probe set (bytes a JSONB column would re-order/re-encode) written → read → byte-identical + content_hash match |
| SCOPE-1 | **ExtensibleRoleInsertPattern** (insert `role='admin'` → succeeds → proves no closing CHECK) + **DeferredTableAbsencePattern** (introspect → assert no rulebook-registry table) |
| PERF-1 / OBS-1 | **ObservedSoftBudgetPattern** / **N-A (observability-owned)** |

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide the
**pattern shape + component decomposition** — they do **not** re-open the frozen FD or the approved NFR targets.

## Question 1 — ATOMIC-1/COLOC-1: the transaction/connection pattern
How is both-or-neither proven on the migration-produced schema?

A) **SingleTransactionCoLocationPattern**: open **one connection**, `BEGIN` one transaction, INSERT `audit_record`
   then INSERT `applicant_profile_snapshot`, with a **fault injected on the 2nd insert** (duplicate PK / forced
   error); on rollback assert **both tables empty**. Inserts run via **Table handles reflected from the
   migration-produced schema** (not the `pg_repository` import; not audit-store's interim DDL). Same structural
   reasoning as audit-store's ATOMIC-1, now proving THIS unit's production schema. COLOC-1 is the structural
   companion (both tables in one DB/schema on one connection).
B) Multiple connections / two transactions (rejected — cannot guarantee atomicity across connections).
C) Rely on audit-store's existing test (rejected — that validates the interim DDL, not the production migrations).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — SingleTransactionCoLocationPattern: open one connection, BEGIN one transaction, INSERT audit_record then applicant_profile_snapshot, with a fault injected on the 2nd insert; on rollback assert both tables empty. Inserts via Table handles reflected from the migration-produced schema (not the pg_repository import, not audit-store's interim DDL). COLOC-1 is the structural companion (both tables in one DB/schema on one connection).

## Question 2 — APPEND-1: where the grant-DDL text lives + how tests apply it
Given the grant-DDL text is this unit's Code-Gen deliverable, what's the pattern?

A) **GrantDDLInMigrationPattern**: the `CREATE ROLE audit_writer …; GRANT INSERT, SELECT …; CREATE ROLE
   audit_reader …; GRANT SELECT …;` text is a **dedicated step in the migration sequence** (a grants migration
   applied after the tables migration). The integration test **applies the full sequence incl. grants** onto the
   testcontainer, then **connects as each role** and asserts: `audit_writer` INSERT/SELECT ok + UPDATE/DELETE raise;
   `audit_reader` SELECT ok + INSERT/UPDATE/DELETE raise. Infra owns only per-environment **execution** + credential
   binding (SEC-3). **APPEND-1 is fully writable/runnable at this unit's Code-Gen.**
B) Keep the grant-DDL outside the migration sequence as a separate hand-run script (weaker — the grants would not be
   part of the reproducible apply-from-empty sequence; MIGRATE-1 wouldn't cover them).
C) Defer the grant-DDL text to Infrastructure Design (rejected — contradicts the approved NFR fold #1; would make
   APPEND-1 un-writable here).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — GrantDDLInMigrationPattern: the CREATE ROLE/GRANT text is a dedicated step in the migration sequence (applied after the tables migration). The integration test applies the full sequence incl. grants onto the testcontainer, then connects as each role and asserts the write matrix. Infra owns only per-environment execution + credential binding. APPEND-1 is fully writable/runnable at this unit's Code-Gen.

## Question 3 — DATA5-1: the config-guard + structural-type patterns
How is DATA-5 designed as checkable structure?

A) **DbUrlGuardPattern** — a **pure function** `require_postgres_url(url) -> url` that parses the URL scheme and
   **raises on any non-`postgresql://` scheme** (SQLite rejected), called at config load; unit-tested with
   `postgresql://` (ok), `sqlite://` (raises), and another scheme (raises) — **no container, writable today**. Plus
   **PostgresOnlyTypePattern** — the schema's `BYTEA`/`TIMESTAMPTZ`/DB-roles make the migration DDL structurally
   unable to apply on SQLite (a structural/integration assertion). Repo-wide no-SQLite CI aggregation = `quality-gates`
   (referenced).
B) Only the structural type pattern, no config guard (weaker — misses a local misconfig with a sqlite URL).
C) Only the config guard, no structural type assertion (weaker — misses the DDL-level guarantee).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — DbUrlGuardPattern: a pure function require_postgres_url(url) -> url that raises on any non-postgresql:// scheme, called at config load; unit-tested with postgresql:// (ok), sqlite:// (raises), and another scheme (raises) — no container. Plus PostgresOnlyTypePattern — BYTEA/TIMESTAMPTZ/DB-roles make the migration DDL structurally unable to apply on SQLite. CI aggregation referenced to quality-gates.

## Question 4 — Migration schema-authoring form + the single introspection baseline
How is the schema authored, and what is the baseline the MIGRATE/FIDELITY tests introspect against?

A) **The migration sequence is the sole schema author; the tests introspect the LIVE migration-produced schema**
   (reflected from the container after apply) — **no duplicate authoritative SQLAlchemy `MetaData` baseline is
   maintained in the database unit**. This avoids a **third schema copy** that could itself drift (the risk being
   migrations vs a duplicate MetaData vs pg_repository). The migration **tool** stays deferred (D4); whether the
   steps are tool-MetaData-ops or raw SQL is a Code-Gen detail — the **pattern** is "migrations author, tests
   introspect the live result." (The `expected` schema for MIGRATE-1 is asserted via the introspected shape, not a
   parallel hand-written MetaData.)
B) Maintain a canonical SQLAlchemy `MetaData` in the database unit AND migrations AND compare all three (rejected —
   a third copy; more drift surface, not less).
C) Author only via raw SQL with no introspection check (rejected — MIGRATE-1/FIDELITY-1 need introspection).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — the migration sequence is the sole schema author; tests introspect the LIVE migration-produced schema (reflected from the container after apply) — no duplicate authoritative SQLAlchemy MetaData baseline maintained in the database unit. Avoids a third schema copy that could itself drift. Migration tool stays deferred; the pattern is "migrations author, tests introspect the live result."

## Question 5 — MIGRATE-2: the immutability-checksum mechanism
How is "a published migration is never edited" made pass/fail?

A) **ChecksumImmutabilityPattern**: a **committed manifest** of `{migration_filename: sha256}` for every published
   migration; the test **recomputes the hash over each migration file** and compares to the manifest — an **edited
   published file** → changed hash → **fail**. Adding a **new** migration is an **append to the manifest** (allowed);
   editing a published one is **not**. Mirrors the append-only discipline (change = new migration, never mutation).
   Unit-tier (hash files, no container).
B) Rely on code review / git history alone (rejected — not a pass/fail test).
C) No immutability check (rejected — an edited published migration would slip through; the approved NFR pins it).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — ChecksumImmutabilityPattern: a committed manifest of {migration_filename: sha256} for every published migration; the test recomputes the hash over each migration file and compares to the manifest — an edited published file → changed hash → fail. Adding a new migration is an append to the manifest (allowed); editing a published one is not. Unit-tier, no container.

## Question 6 — FIDELITY-1: normalized column-spec fields + type-normalization
What exactly is compared, and how are SQLAlchemy-side vs introspected-Postgres types made comparable?

A) **SchemaIntrospectionComparatorPattern**: extract a **normalized column-spec dict** per table on BOTH sides —
   fields **`{name, type, nullable, pk, fk_target, indexed}`**, **CHECK EXCLUDED**. **Type-normalization**: map both
   sides to **common canonical tokens** so `LargeBinary` ↔ `BYTEA`, `String` ↔ `VARCHAR`, `DateTime(timezone=True)`
   ↔ `TIMESTAMPTZ` compare **equal** (the mapping is small + explicit). One side = the **introspected live
   migration-produced schema** (via the SchemaIntrospector utility); the other = **`pg_repository`'s Table metadata
   read-only** (the consuming reference). **Drift on either side fails.** Extract-then-compare dicts (resilient to
   non-schema refactors; schema drift is the intended tripwire).
B) Compare raw SQLAlchemy type objects directly to introspected types (rejected — `LargeBinary` != `BYTEA` object
   identity would false-mismatch; needs normalization).
C) Compare only column names (weaker — misses type/nullability/PK/FK drift).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — SchemaIntrospectionComparatorPattern: extract a normalized column-spec dict per table on both sides — {name, type, nullable, pk, fk_target, indexed}, CHECK excluded. Type-normalization maps both sides to common canonical tokens so LargeBinary↔BYTEA, String↔VARCHAR, DateTime(timezone=True)↔TIMESTAMPTZ compare equal. One side = introspected live migration-produced schema; the other = pg_repository's Table metadata read-only. Drift on either side fails.

## Question 7 — BYTEA-1: the adversarial byte-probe set
What byte sequences specifically probe the JSONB-would-reorder risk?

A) **OpaqueRoundTripProbePattern** with an adversarial probe set: **(i)** bytes representing **non-canonical JSON key
   order**, **(ii)** **differing number formatting** (e.g. `1.0` vs `1`, trailing zeros), **(iii)** **extra
   whitespace**, **(iv)** **non-UTF8 / high bytes**, **(v)** **empty bytes** — i.e. sequences a `JSONB` column would
   re-order or re-encode. Each is written to `rule_results` / `profile_canonical`, read back, and asserted
   **byte-identical**; `content_hash` recomputed over the readback matches. Proves **no DB-side normalization**
   (REPLAY-1/DET-2). Real CANON-SER output of a sample profile/report is included as a realistic case.
B) One simple ASCII byte string only (weaker — doesn't probe the reorder/re-encode risk).
C) Assert the column type is BYTEA only (rejected per approved NFR — type alone doesn't prove no transform).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — OpaqueRoundTripProbePattern with an adversarial probe set: (i) non-canonical JSON key order, (ii) differing number formatting, (iii) extra whitespace, (iv) non-UTF8/high bytes, (v) empty bytes — sequences a JSONB column would re-order or re-encode. Written to rule_results/profile_canonical, read back, asserted byte-identical; content_hash recomputed matches. Real CANON-SER output of a sample profile/report included as a realistic case.

## Question 8 — SCOPE-1: extensibility + absence patterns (and the no-CHECK-on-action/status guard)
How are the deferred/foundational consumers designed as verifiable-but-bounded?

A) **ExtensibleRoleInsertPattern**: insert an `app_user` row with a **novel `role` value (`admin`)** and assert it
   **succeeds** — the **negative property** proving `role` carries **no closing CHECK**. **DeferredTableAbsencePattern**:
   introspect the schema and assert **no rulebook-registry table exists**. **Guard**: **no pattern asserts a CHECK
   EXISTS on `action`/`status`** (that stays optional per BR-DB-9 — "may", not "must"); and **FIDELITY-1 excludes
   CHECK from its comparison** (so an optional CHECK never trips fidelity). **Nothing about auth-rbac authn/permissions
   or rules-engine evaluation is tested.**
B) Add a CHECK on `role` to validate the known set (rejected — closes the dimension; contradicts fold #1).
C) Test nothing about the skeleton/slot (rejected — leaves the reserved substrate unverified).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — ExtensibleRoleInsertPattern: insert an app_user row with a novel role value (admin) and assert it succeeds — the negative property proving role carries no closing CHECK. DeferredTableAbsencePattern: introspect and assert no rulebook-registry table exists. No pattern asserts a CHECK exists on action/status (stays optional); FIDELITY-1 excludes CHECK from comparison. Nothing about auth-rbac authn/permissions or rules-engine evaluation is tested.

## Question 9 — PERF-1/OBS-1 pattern
What's the perf/obs design posture?

A) **ObservedSoftBudgetPattern** — measure migration-apply + insert latency, **report against a soft budget,
   non-gating** (schema-infra unit; no hard SLO). **OBS-1 = N/A** (DB metrics/traces are `observability`'s concern,
   referenced). No demographic-derived metric (CON-BR1).
B) A hard latency SLO here (rejected — premature; belongs to observability/perf tuning).
C) Omit perf/obs entirely (A's explicit soft/N-A framing is clearer for the compliance summary).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — ObservedSoftBudgetPattern: measure migration-apply + insert latency, report against a soft budget, non-gating. OBS-1 = N/A (observability's concern, referenced). No demographic-derived metric.

## Question 10 — Logical component decomposition
What modules does this unit introduce?

A) **Six logical components** (under `backend/database/`): **(C1) MigrationSequence** — the versioned forward-only
   steps incl. the initial-schema migration; **(C2) GrantDDL** — the `CREATE ROLE`/`GRANT` step within the sequence
   (D5); **(C3) DbUrlGuard** — the `require_postgres_url` config-guard function; **(C4) SchemaIntrospector** — the
   reflect-live-schema → normalized column-spec utility, **shared by MIGRATE-1 + FIDELITY-1** (no duplication);
   **(C5) FidelityComparator** — reads `pg_repository` metadata read-only, normalizes, compares (CHECK excluded);
   **(C6) MigrationChecksum** — the manifest + recompute for MIGRATE-2. Test fixtures: a testcontainers-Postgres
   harness. Each component maps to ≥1 `NFR-DB-*` target; no orphan.
B) A single monolithic module (rejected — poor separation; the introspector/comparator/guard are distinct concerns).
C) Fold FIDELITY into audit-store (rejected — inverts ownership; the guard lives with the schema authority).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — six logical components under backend/database/: MigrationSequence, GrantDDL (in-sequence), DbUrlGuard, SchemaIntrospector (shared by MIGRATE-1 + FIDELITY-1, no duplication), FidelityComparator (reads pg_repository metadata read-only, CHECK excluded), MigrationChecksum. Test fixtures: testcontainers-Postgres harness. Each maps to ≥1 NFR-DB-* target, no orphan.

## Question 11 — Depth + Mermaid
Depth for this NFR Design, and diagrams?

A) **Comprehensive** — one section per pattern, each structurally meeting its `NFR-DB-*` target + traced; a
   **logical-components** blueprint with responsibilities + ownership + reference-not-own check. **Two validated
   Mermaid** required in the artifacts (a **pattern-integration** diagram + a **component-relationship** diagram),
   each against the 7 rules with a text alternative.
B) Standard — shorter, one Mermaid.
C) Minimal — no diagram.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — comprehensive: one section per pattern, each structurally meeting its target + traced; a logical-components blueprint with responsibilities + ownership + reference-not-own check. Two validated Mermaid required (pattern-integration + component-relationship), each against the 7 rules with a text alternative.

---

## 4. Named logical components (draft — finalized after the answers)
**(C1) MigrationSequence** · **(C2) GrantDDL** (in-sequence) · **(C3) DbUrlGuard** · **(C4) SchemaIntrospector**
(shared) · **(C5) FidelityComparator** (read-only pg_repository reference) · **(C6) MigrationChecksum**. Test
substrate: testcontainers Postgres harness. Artifacts to be generated after answers:
`guide-docs/build/database/nfr-design/` → `nfr-design-patterns.md` + `logical-components.md` (both with validated
Mermaid + text alternative).

---

## 5. Constraints & settled items held (not re-opened)
- Frozen FD (schema + BR-DB-1..14 + lifecycle) and the approved NFR targets are the substrate — patterns realize
  them, re-opening neither.
- Direction-of-truth intact: database = schema authority; `pg_repository` metadata = consuming reference; FIDELITY-1
  = one-directional consistency guard; no production cross-import / circular dependency.
- Grant-DDL **text** = this unit's Code-Gen deliverable (APPEND-1 needs no Infra); **execution** deferred to Infra +
  `secrets-config` (SEC-3). Migration **tool** deferred (Code-Gen/Infra).
- FIDELITY-1 excludes CHECK; `action`/`status` CHECK optional; `role` no-CHECK via the negative property.
- No new production dependency; reference-not-own (read-only `pg_repository` import for FIDELITY-1 only; no
  consuming-unit code edited). DATA-5 / SEC-3 / SEC-4 / SEC-5 / REPLAY-1 / DET-2 / CON-BR1 held. No LLM.
- Infrastructure Design remains a distinct, REAL later stage.

---

## 6. Next step (STOP here)
Fill the eleven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then generate the two `database` NFR Design artifacts
(`nfr-design-patterns.md` + `logical-components.md`, each with a validated Mermaid + text alternative) and present the
standardized 2-option completion message. **No NFR Design artifacts or code are generated until the answers are in and
checked.**
