# Functional Design Plan — `database` (EPIC-6 / U15)

**Phase / Stage**: BUILD → Functional Design (per-unit, plan-then-generate)
**Unit covered**: U15 `database` (EPIC-6, Phase 1) — **STORY-LESS shared infrastructure**: the
PostgreSQL schema + migrations substrate depended on by `audit-store`, `rules-engine`, `auth-rbac`,
and `admin-cli`.
**Date**: 2026-07-06
**Status**: **Plan — awaiting `[Answer]:` tags.** No FD artifacts generated yet. Stop after this plan.

This plan follows `.project-guide-rule-details/build/functional-design.md`. It is the **altitude
drop to INTERNALS** for a unit that has **no user story and no frozen `component-methods.md`
contract** — the design authority here is (a) the **built consuming units' schema references**
(audit-store's `pg_repository.py`, banner-marked TEST-only), (b) the **cross-unit dependency matrix**
(`unit-of-work-dependency.md`), and (c) the **tracked cross-unit constraint** (ATOMIC-1 co-location +
the `audit_writer`/`audit_reader` grants). **This unit owns the schema; it does NOT re-design the
business logic of the units that consume it** — reference-not-own applied *in reverse*.

> **First stage of the `database` per-unit BUILD loop.** Per the analysis approved 2026-07-06:
> Functional Design is the genuine next stage (new schema/data model, FD Execute-IF); and unlike the
> four prior cluster units, **Infrastructure Design WILL be a real stage** for this unit (it *is* the
> persistence topology — `unit-of-work.md` pins it "comprehensive at Infrastructure Design"). This FD
> designs the **schema + integrity rules + migration model**; Infrastructure Design later provisions
> the **Postgres instances, role/grant execution, connection/pooling, Docker + Render topology**.

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 `database` (U15, EPIC-6, Phase 1) — story-less shared infra
- **Purpose** (`unit-of-work.md §3` U15): shared **PostgreSQL schema + migrations** depended on by
  `audit-store` and others; **no SQLite** (DATA-5). **Story-less by design** — exercised via
  US-PLAT-8 (owned by `audit-store`); it provides the *substrate*, it does not own a story.
- **Owned invariant** (`unit-of-work.md §5`): **DATA-5** (PostgreSQL everywhere).
- **Depended on by** (`unit-of-work-dependency.md`): `audit-store` (persist the 6-tuple +
  `applicant_profile_snapshot`), `rules-engine` (rulebook_version store), `auth-rbac` (user/role
  store; OIDC-ready seam), `admin-cli` (publish versions; manage users/provider config). It is a
  **dependency leaf** — it depends on nothing (all its deps are built / none).
- **Depth**: **comprehensive** at both Functional Design (this stage) and Infrastructure Design.

### 1.2 Design inputs (there is NO frozen `component-methods.md` shape for this unit)
Because `database` is story-less infra, its FD authority is the built + specified consumers, held as
**references, not re-designed**:

- **DATA-5 (exact, `requirements.md:180`)**: "Database = **PostgreSQL everywhere** (local via Docker
  + Postgres in deployment); **no SQLite**, to avoid dialect drift that could break decision
  replay/versioning." (Traces US-PLAT-8.)
- **ATOMIC-1 co-location (exact, Deferred Decisions register)**: audit-store's ATOMIC-1 rests on a
  **single ACID transaction** spanning only tables **"co-located in ONE Postgres database reachable
  within a single connection/transaction."** → "The `database` unit's schema **MUST** place
  audit-store's tables (`audit_record` + any normalized `applicant_profile_snapshot` child row) in
  **one Postgres database/schema — NOT split across separate databases/services**." Also: the
  `database` unit **owns the `audit_writer` (INSERT-only) + `audit_reader` (SELECT-only) role-grant
  DDL** that audit-store's APPEND-1/READ-1 integration tests reference.
- **audit-store's built interim schema reference** (`backend/audit_store/pg_repository.py`,
  banner-marked **TEST-ONLY, NOT production**): a 2-table normalized shape —
  - `audit_record` (14 cols): `decision_id` (PK), `application_id` (idx), `recommendation_id`,
    the 6-tuple (`rulebook_version`, `rule_results` [CANON-SER `LargeBinary`], `timestamp` [tz],
    `model_version`, `memo_hash`, `engine_version`), the CON-BR4 commit linkage (`underwriter_id`,
    `action`, `reason` [nullable]), and the **OOS-7 seam** (`status`, `supersedes_decision_id`
    [nullable]).
  - `applicant_profile_snapshot` (child, FK → `audit_record.decision_id`): `decision_id` (PK/FK),
    `application_id`, `profile_canonical` (CANON-SER `LargeBinary`), `content_hash`.
  - **The production schema (single-table vs normalized) + the role-grant DDL are OWNED BY THIS UNIT,
    "bound only by the co-location constraint."** This FD is **not obligated to copy** the interim
    shape — only to honor co-location + provide the two roles + carry every column the built
    `pg_repository.py` reads/writes so the consuming code keeps working unchanged.
- **OOS-7 / OOS-8 seams (Phase-1 reserved, `requirements.md:252-253`)**: `decision_id` + `status`
  (`active`/`superseded`, **Phase-1/2 writes `active` only**) + nullable `supersedes_decision_id`
  (OOS-7 append-only supersession seam); `engine_version` captured now (OOS-8 forensic). The
  field-level schema for these seams was designed in audit-store's FD and realized in its record; the
  `database` schema must **carry these columns** so a Phase-3 amendment slots in without migrating
  existing rows.

### 1.3 Cross-unit consumers to scope (reference-not-own, in reverse)
This unit owns the **schema substrate**; it must **not** dictate the business logic of its consumers.
The FD scopes *what persistent shape each consumer needs*, at the altitude the consumer has already
fixed, and defers anything a not-yet-designed consumer will pin at its own FD:

- **`audit-store`** — schema is **fully determined** (built + FD-frozen): the two co-located tables
  above. This unit's schema must match the columns `pg_repository.py` uses.
- **`rules-engine`** — the dependency matrix names a **"rulebook_version store."** But the built
  `rules-engine` loads rulebooks from **versioned YAML files** (`backend/rules_engine/rulebook/*.yaml`),
  not a DB table. Whether `database` owns a `rulebook_version` **table** in Phase 1 (published-version
  registry) or that store is **deferred/admin-cli-owned** is a genuine scoping decision → **Q2**.
- **`auth-rbac`** — a **Phase-1 unit not yet designed**. It needs a **user/role store** (OIDC-ready
  seam). How much of that schema this unit pins *now* vs leaves to auth-rbac's own FD is a
  reference-not-own-reverse decision → **Q8**.
- **`admin-cli`** — consumes the above stores; owns no new tables of its own here.
- **Deferred (Phase-2/3 consumers):** `outlier-model` corpus metadata, `observability` stores,
  `deploy-config` — their persistent needs belong to those units' own design, **not** this FD.

### 1.4 Binding constraints held through this FD (guardrails skill + project constraints)
- **DATA-5**: PostgreSQL **only** — no SQLite in dev, test, CI, or prod (dialect-drift guard that
  protects replay/versioning). Test tier uses **real Postgres** (testcontainers), per audit-store's
  established pattern.
- **ATOMIC-1 co-location**: audit-store's tables live in **one Postgres database/schema reachable in
  a single connection/transaction** — the schema shape must make audit-store's single
  `engine.begin()` both-or-neither write valid.
- **Append-only (CON-AUDIT-1 / SEC-5)**: the audit tables are append-only by construction — the
  schema + role grants must make **UPDATE/DELETE on committed audit rows** impossible for the write
  role (this is the DB-role half of audit-store's APPEND-1).
- **SEC-4 read-only segregation**: `audit_reader` is **SELECT-only**; `audit_writer` is
  **INSERT+SELECT** (no UPDATE/DELETE). The grants are this unit's deliverable.
- **SEC-3 (no hardcoded secrets)**: this FD names **no credentials / connection strings** — DB
  usernames, passwords, and connection URLs are owned by **`secrets-config`** (env/secrets) and wired
  at Infrastructure Design. The schema is credential-free.
- **Reproducibility / replay integrity**: `rule_results` + `profile_canonical` are stored as
  **CANON-SER bytes** (opaque, byte-fidelity preserved) so replay comparison stays exact — the schema
  must not "helpfully" normalize or re-encode them → **Q10**.
- **Advisory-only naming**: the table storing the human's committed choice is correctly named around
  **decision** (`audit_record` / `decision_id`) — the one place "decision" is right (the human's
  committed action); nothing in the schema implies the *system* decides.

---

## 2. Functional Design execution plan (checkboxes — Step 2)

Artifacts to be generated **after** answers are collected and ambiguity-checked, under
`guide-docs/build/database/functional-design/`:
- `domain-entities.md` — the field-by-field **schema**: every table, column, type, nullability, PK/FK,
  index, and the reserved OOS-7 seam columns; an **ER Mermaid diagram** (validated per
  visual-and-syntax-standards, with a text alternative).
- `business-rules.md` — the **integrity + governance rules**: PK/FK/uniqueness/NOT-NULL constraints,
  the **append-only rule** (no UPDATE/DELETE on committed rows) and its DB-role realization, the
  **role-grant semantics** (`audit_writer`/`audit_reader`), the **DATA-5 no-SQLite rule**, the
  **co-location rule**, and the OOS-7 `status=active`-only Phase-1/2 rule. Each rule states its
  condition explicitly.
- `business-logic-model.md` — the **schema-lifecycle model**: the **migrations strategy** (versioned,
  forward-only), the **connection/transaction model** that makes ATOMIC-1 valid (single DB, single
  transaction), the **FD-vs-Infrastructure-Design boundary** (what this FD pins vs what Infra
  provisions), and a **consumer→table mapping**; a data/flow **Mermaid** (validated + text
  alternative) + an invariant self-check table (as the prior units').

- [ ] **P1. Analyze unit context** (§1 above — done).
- [ ] **P2. Collect `[Answer]:` tags** (§3); run the mandatory ambiguity-check (§4 of the rule file);
  raise a clarification file only if any answer is vague/combined/contradictory.
- [ ] **P3. Generate `domain-entities.md`** (field-by-field schema + ER Mermaid).
- [ ] **P4. Generate `business-rules.md`** (integrity, append-only, role grants, DATA-5, co-location,
  OOS-7 seam rules).
- [ ] **P5. Generate `business-logic-model.md`** (migrations model, connection/transaction model,
  FD↔Infra boundary, consumer→table map, invariant self-check).
- [ ] **P6. Cross-consumer contract check** — verify the schema covers every known Phase-1 need
  (audit-store's built columns exactly; the rulebook-version + user/role scope per the answers) and
  that it does **not** silently commit not-yet-designed consumers' internals.
- [ ] **P7. Guardrail compliance pass + present the standardized 2-option completion message**
  (DATA-5, ATOMIC-1 co-location, append-only/SEC-4/SEC-5, SEC-3 no-secrets, replay byte-fidelity,
  advisory-only naming; record compliant/N-A per Security-Guardrails control). Then Request Changes /
  Continue to Next Stage → **NFR Requirements** for `database`.

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These decide the **schema internals + scope** — they do **not** re-open any built consuming unit's
frozen contract (audit-store's record shape stays as built; this unit's DDL must *match* it).

### A. Phase-1 schema ownership scope

## Question 1 — What tables does `database` own at Phase 1?
`database` is depended on by audit-store, rules-engine, auth-rbac, admin-cli. Which persistent schema
does THIS unit own now vs defer?

A) **The Phase-1 consumers' persistent schema, co-located in one Postgres database**: audit-store's
   tables (`audit_record` + `applicant_profile_snapshot`, ATOMIC-1 co-located) **now, in full**;
   the rules-engine rulebook-version store and the auth-rbac user/role store **scoped per Q2 / Q8**
   (foundational shape or deferred slot); **Phase-2/3 consumer tables deferred** to those units'
   own design (outlier corpus metadata, observability, etc.). One database, one schema namespace.
B) Only audit-store's two tables now; every other consumer's schema is deferred to when that
   consumer's unit is built.
C) A single monolithic schema pre-defining every Phase-1 and Phase-2 table now.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — the Phase-1 consumers' persistent schema, co-located in one Postgres database: audit-store's tables (audit_record + applicant_profile_snapshot, ATOMIC-1 co-located) now in full; rules-engine's rulebook-version store and auth-rbac's user/role store scoped per Q2/Q8; Phase-2/3 consumer tables deferred to those units' own design. One database, one schema namespace.

## Question 2 — The rules-engine "rulebook_version store" (dependency matrix) vs the built YAML loader
The dependency matrix lists `rules-engine → database` (rulebook_version store), but the **built**
rules-engine loads rulebooks from **versioned YAML files** and never writes a DB table. Does this unit
own a rulebook-version table now?

A) **Defer the rulebook-version DB table** — in Phase 1 the rulebook is **file-based + content-hashed
   YAML** (as built; `content_hash` + semver already give replay-exact versioning), so no DB table is
   required for the audit/replay path to work. `database` **reserves a migration slot** for a
   published-version **registry** (owned/authored later by `admin-cli` when version-publishing lands),
   but pins **no columns now** — avoids designing a store the built system does not use. Record as a
   deferred item.
B) Define a `rulebook_version` registry table now (columns: version, content_hash, published_at,
   published_by, active) even though nothing writes it yet in Phase 1.
C) Store the full rulebook YAML *content* in the DB now (replace the file loader).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — defer the rulebook-version DB table. The built rules-engine loads from versioned, content-hashed YAML files (content_hash + semver already give replay-exact versioning), so no DB table is required for the audit/replay path to work now. database reserves a migration slot for a published-version registry (owned/authored later by admin-cli when version-publishing lands), pins no columns now. Record as a deferred item in the register.

### B. Co-location satisfaction & schema shape

## Question 3 — Which schema shape satisfies ATOMIC-1 co-location for audit-store's data?
audit-store's ATOMIC-1 needs a single ACID transaction across its data. Which shape does the
production schema adopt, and how does it explicitly satisfy "one database, one transaction"?

A) **Adopt the 2-table normalized shape** (`audit_record` + `applicant_profile_snapshot` child,
   FK → `audit_record.decision_id`), **both tables in one Postgres database + one schema namespace**,
   so audit-store's single `engine.begin()` transaction inserts **both rows atomically** (the FK makes
   it a genuine multi-row both-or-neither write, which is exactly what its `test_pg_integration.py`
   exercises). Co-location is satisfied **because both tables share one database/schema reachable on
   one connection** — not merely declared, but structurally: there is no second database/service in
   the write path. Matches the built `pg_repository.py` column-for-column (consuming code unchanged).
B) **Single-table** shape — fold the profile snapshot columns into `audit_record` (one row per
   decision, no child table). Trivially co-located, but **diverges from the built repository's 2-row
   insert** (would require changing audit-store's built code — a reference-not-own violation).
C) Split audit_record and the profile snapshot into **separate databases/schemas** (rejected —
   directly violates ATOMIC-1 co-location; breaks the single-transaction guarantee).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — adopt the 2-table normalized shape (audit_record + applicant_profile_snapshot child, FK → audit_record.decision_id), both tables in one Postgres database + one schema namespace, so audit-store's single engine.begin() transaction inserts both rows atomically. Co-location satisfied structurally (no second database/service in the write path). Matches the built pg_repository.py column-for-column — consuming code unchanged.

## Question 4 — Schema namespace + PK/FK/index specifics carried from the built repository
The production DDL must let the built `pg_repository.py` run unchanged. What does the FD pin?

A) **One named schema** (e.g. the default `public` or a single dedicated schema) holding both tables;
   `audit_record.decision_id` **PK** (str); `application_id` **indexed** (browse-by-application);
   `applicant_profile_snapshot.decision_id` **PK + FK** → `audit_record.decision_id`; NOT-NULL on
   every 6-tuple + commit-linkage column; `reason` + `supersedes_decision_id` **nullable**; `status`
   NOT-NULL default `active`. Types match the built repository (str/varchar, tz-aware timestamp,
   `BYTEA` for the two CANON-SER columns — see Q10). All in one schema = co-location.
B) Multiple schemas (one per consumer) in the same database — co-located at the DB level but
   split at the schema level (adds cross-schema FK complexity for no Phase-1 benefit).
C) Leave PK/FK/index/nullability unspecified at FD; decide at Code-Gen.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — one named schema holding both tables; audit_record.decision_id PK (str); application_id indexed; applicant_profile_snapshot.decision_id PK+FK → audit_record.decision_id; NOT-NULL on every 6-tuple + commit-linkage column; reason + supersedes_decision_id nullable; status NOT-NULL default active. Types match the built repository (varchar, tz-aware timestamp, BYTEA for the two CANON-SER columns). All in one schema = co-location.

### C. Role grants — FD schema-side vs Infrastructure Design provisioning

## Question 5 — `audit_writer` / `audit_reader` role-grant definition split
The `database` unit owns the two role grants that audit-store's APPEND-1/READ-1 tests reference. What
does THIS FD pin vs what does Infrastructure Design later provision?

A) **This FD pins the role SEMANTICS as schema-governance rules** (in `business-rules.md`):
   `audit_writer` = **INSERT + SELECT only** (no UPDATE, no DELETE — the DB-role half of append-only);
   `audit_reader` = **SELECT only** (SEC-4 read-only auditor); both scoped to the audit tables. The
   **grant DDL text** (`CREATE ROLE … ; GRANT … ;`) and its **execution/provisioning** (which
   Postgres instance, how roles are created in local Docker vs Render, credential binding via
   `secrets-config`) belong to **Infrastructure Design + secrets-config** — named here as the boundary,
   not executed here. (The FD defines *what the roles may do*; Infra defines *how they are created and
   bound*.)
B) Pin the full grant DDL **and** the provisioning here in the FD (collapses the FD/Infra boundary).
C) Leave role semantics entirely to Infrastructure Design (rejected — the append-only + SEC-4
   guarantees are schema-governance invariants, not just deployment detail).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — this FD pins the role SEMANTICS as schema-governance rules: audit_writer = INSERT+SELECT only (no UPDATE/DELETE — the DB-role half of append-only); audit_reader = SELECT only (SEC-4). The grant DDL text and its execution/provisioning (Docker vs Render, credential binding via secrets-config) belong to Infrastructure Design + secrets-config — named here as the boundary, not executed here.

### D. Migrations strategy (FD level)

## Question 6 — Migrations model at FD altitude (tool choice deferred)
DATA-5 needs the same schema across local Docker, test/CI, and Render. How is schema evolution
modelled at FD level?

A) **Versioned, forward-only migrations as the single source of truth for the schema**: an ordered
   sequence of immutable migration steps (initial schema = the Phase-1 tables + roles), applied
   identically in dev (Docker Postgres), test/CI (testcontainers Postgres), and prod (Render Postgres);
   **never edit a published migration in place** (mirrors the rulebook append-only-version discipline
   — a schema change is a **new** migration, not a mutation). The **tool** (e.g. Alembic vs raw-SQL
   runner) is a **Code-Gen/Infrastructure tech-stack detail, deferred**; the FD pins only the
   *model* (versioned + forward-only + one authoritative sequence + no-SQLite everywhere).
B) No migrations — create tables ad hoc from application `MetaData.create_all` at startup (rejected —
   no versioned evolution; drift risk across environments).
C) Hand-maintained SQL applied manually per environment (rejected — non-reproducible).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — versioned, forward-only migrations as the single source of truth for the schema: an ordered sequence of immutable migration steps, applied identically across dev (Docker Postgres), test/CI (testcontainers Postgres), and prod (Render Postgres); never edit a published migration in place. Tool choice (Alembic vs raw-SQL runner) deferred to Code-Gen/Infrastructure; FD pins only the model.

### E. DATA-5 enforcement

## Question 7 — How is "PostgreSQL only, no SQLite" enforced across dev/test/CI/prod?
DATA-5 forbids SQLite anywhere to avoid dialect drift breaking replay/versioning. How does the FD make
that a checkable invariant, not a hope?

A) **PostgreSQL is the only dialect in every tier, structurally**: dev = Docker Postgres; test/CI =
   **real Postgres via testcontainers** (the pattern audit-store already uses — its DB-touching tests
   are `@pytest.mark.integration` on real Postgres, never SQLite); prod = Render Postgres. The schema
   uses **Postgres-specific types where they matter** (`BYTEA`, tz-aware `TIMESTAMPTZ`) so it
   **cannot silently run on SQLite**. The FD states DATA-5 as a `business-rules.md` invariant with the
   per-tier realization; the CI guard that no SQLite URL is configured is a **quality-gates/CI**
   concern referenced, not owned here.
B) Enforce Postgres in prod only; allow SQLite for local/test convenience (rejected — the exact
   dialect-drift DATA-5 forbids).
C) State DATA-5 as documentation only, no structural enforcement.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — PostgreSQL is the only dialect in every tier, structurally: dev = Docker Postgres; test/CI = real Postgres via testcontainers (audit-store's established pattern); prod = Render Postgres. The schema uses Postgres-specific types (BYTEA, TIMESTAMPTZ) so it cannot silently run on SQLite. DATA-5 stated as a business-rules.md invariant with per-tier realization; the CI no-SQLite guard is a quality-gates/CI concern referenced, not owned here.

### F. Cross-unit consumers — reference-not-own, in reverse

## Question 8 — auth-rbac's user/role store: how much does `database` pin now?
`auth-rbac` (Phase-1, **not yet designed**) needs a user/role store with an OIDC-ready seam. This unit
owns the schema but must not pre-empt auth-rbac's business logic.

A) **Pin only a foundational, OIDC-ready skeleton** that auth-rbac's own FD will complete: e.g.
   `app_user` (id, subject/identifier, role) + a role concept sufficient to distinguish the
   **underwriter** vs **auditor** roles the built system already relies on (SEC-4 segregation,
   audit-store's role re-check), with an **OIDC-ready `subject`/issuer seam column reserved** —
   and **explicitly mark the detailed user/role model as co-designed when `auth-rbac` reaches FD**
   (reference-not-own-reverse: `database` provides the substrate + the migration slot; `auth-rbac`
   fixes its internal model). Nothing here dictates auth-rbac's authn flow.
B) Fully design the complete user/role/permission model now, ahead of auth-rbac's own FD (risks
   pre-empting a unit not yet designed).
C) Define no user/role tables at all now; defer the entire store to auth-rbac's FD (leaves the
   Phase-1 SEC-4 role distinction the built audit-store re-check assumes without a schema home).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — pin only a foundational, OIDC-ready skeleton that auth-rbac's own FD will complete: e.g. app_user (id, subject/identifier, role) + a role concept sufficient to distinguish underwriter vs auditor (SEC-4 segregation, audit-store's role re-check), with an OIDC-ready subject/issuer seam column reserved. Explicitly mark the detailed user/role model as co-designed when auth-rbac reaches FD — database provides the substrate + migration slot; auth-rbac fixes its internal model.

## Question 9 — Schema authority vs the consuming units' own SQLAlchemy `Table` definitions
audit-store's `pg_repository.py` defines its own SQLAlchemy `Table` metadata (banner-marked TEST-only).
Who is the authoritative source of the production schema, and how do the two stay in sync?

A) **`database` owns the authoritative production DDL/migrations** (the single source of truth); the
   consuming units keep their SQLAlchemy `Table`/query objects as a **conforming read/write mapping**
   whose columns MUST match the authoritative schema. The FD's job is to make the authoritative schema
   **carry every column the built `pg_repository.py` reads/writes** (so consuming code runs unchanged),
   and to record that the interim TEST DDL is **superseded by** this unit's migrations. No consuming
   unit's code is edited by this FD (reference-not-own); the contract is the **column set**, verified
   at P6.
B) Make audit-store's `pg_repository.py` `MetaData` the source of truth; `database` just runs
   `create_all` from it (rejected — inverts ownership; the TEST-only metadata is explicitly not the
   production schema).
C) Maintain two independent schemas and hope they match (rejected — drift risk).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — database owns the authoritative production DDL/migrations (the single source of truth); consuming units keep their SQLAlchemy Table/query objects as a conforming read/write mapping whose columns MUST match the authoritative schema. The authoritative schema carries every column the built pg_repository.py reads/writes (consuming code runs unchanged); the interim TEST DDL is recorded as superseded. No consuming unit's code is edited by this FD; the contract is the column set, verified at P6.

### G. Replay byte-fidelity

## Question 10 — How are the CANON-SER columns (`rule_results`, `profile_canonical`) stored?
Replay compares canonically-serialized bytes; audit-store writes them as `LargeBinary`. What column
type does the production schema use, and does it normalize/re-encode?

A) **Store both as opaque `BYTEA`** (Postgres binary), **byte-for-byte as produced by CANON-SER** —
   the schema **does not parse, normalize, re-encode, or add first-class columns for the contents**.
   Byte-fidelity is what makes replay-match meaningful (audit-store's REPLAY-1 / rules-engine's DET-2
   determinism depend on it); a "helpful" DB-side transform would risk a false byte-mismatch. The
   `content_hash` column stays a plain indexed/verifiable string alongside. (Matches the built
   `LargeBinary` mapping.)
B) Store as `JSONB`, letting Postgres parse/normalize the structure (rejected — JSONB re-orders keys
   / re-encodes numbers, breaking byte-identity and replay comparison).
C) Store as `TEXT` (base64/utf-8) (works but wastes space vs BYTEA; acceptable only if a concrete
   reason emerges).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — store both rule_results and profile_canonical as opaque BYTEA, byte-for-byte as produced by CANON-SER — no parsing, normalization, re-encoding, or first-class columns for the contents. Byte-fidelity is what makes replay-match meaningful (REPLAY-1/DET-2 depend on it); a "helpful" DB-side transform would risk a false byte-mismatch. content_hash stays a plain indexed/verifiable string alongside. Matches the built LargeBinary mapping.

## Question 11 — Depth confirmation for this FD
`database` is invariant-bearing infra (DATA-5, ATOMIC-1 co-location, append-only, SEC-4 grants). What
depth does this FD run at?

A) **Comprehensive** — full field-by-field schema, explicit integrity + governance rules, the
   migrations + connection/transaction model, and the FD↔Infrastructure-Design boundary — matching
   `unit-of-work.md`'s "comprehensive" classification and the invariant weight (replay/versioning
   integrity rests on this schema).
B) Standard — tables + a short rules list, lighter on the lifecycle model.
C) Minimal — schema sketch only.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — comprehensive. Full field-by-field schema, explicit integrity + governance rules, the migrations + connection/transaction model, and the FD↔Infrastructure-Design boundary — matching unit-of-work.md's "comprehensive" classification and the invariant weight (replay/versioning integrity rests on this schema).

---

## 4. Constraints & settled items held (not re-opened)
- **No `component-methods.md` contract** exists for this story-less unit — the FD authority is the
  built consumers + the dependency matrix + the tracked ATOMIC-1 constraint (§1.2), held as
  **references, not re-designed**.
- **audit-store's built record shape is frozen** — this unit's schema must **match** the columns
  `pg_repository.py` reads/writes (Q9); this FD does **not** edit any consuming unit's code.
- **ATOMIC-1 co-location** (one DB/schema, one transaction) and the **`audit_writer`/`audit_reader`
  grants** are this unit's deliverables (register carry-forward — being satisfied HERE).
- **OOS-7 / OOS-8 seams** carried as reserved columns (`status`/`supersedes_decision_id`;
  `engine_version` present) — Phase-1/2 writes `status=active` only; amendment behavior is Phase 3.
- **DATA-5** PostgreSQL-only across all tiers (no SQLite); **SEC-3** no credentials/secrets in the
  schema (owned by `secrets-config`); **SEC-4/SEC-5** read-only auditor + append-only; **replay
  byte-fidelity** (opaque CANON-SER bytes).
- **Infrastructure Design is a distinct, REAL later stage** for this unit — it provisions the Postgres
  instances, executes the role grants, and wires connection/pooling + Docker/Render topology; this FD
  pins the schema + rules + migration *model*, not the provisioning.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, the OOS-7/OOS-8 doc
  commitments (this FD designs seam **columns**, not the docs).

---

## 5. Next step (STOP here)
Fill the eleven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory
ambiguity-check (adding a clarification file only if needed), then generate the three `database`
Functional Design artifacts (`domain-entities.md`, `business-rules.md`, `business-logic-model.md`) and
present the standardized 2-option completion message. **No FD artifacts or code are generated until the
answers are in and checked.**
