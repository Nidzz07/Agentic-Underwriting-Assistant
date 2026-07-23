# Infrastructure Design Plan (Part 1) — `database` (EPIC-6 / U15)

**Phase / Stage**: BUILD → Infrastructure Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `database` (story-less infra) · FD ✅ · NFR Requirements ✅ · **NFR Design ✅ (approved 2026-07-06)**
→ **Infrastructure Design ← here (the REAL, comprehensive one — NOT a skip)** → Code-Gen.
**Unit**: U15 `database` · **Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: comprehensive.
**Status**: **Plan — awaiting `[Answer]:` tags. NO Infrastructure-Design artifacts generated this stage. Stop after this plan.**

This plan follows `.project-guide-rule-details/build/infrastructure-design.md`. It **maps the logical components to
actual infrastructure** across dev / CI / prod, built **ON** the frozen FD, the approved `NFR-DB-*` targets, and the
NFR Design patterns/components (C1–C6) — **re-opening none of them**. This stage designs the **deferred halves** that
NFR Design explicitly handed here: **Postgres provisioning, grant-DDL execution, connection/pooling, migration
execution, and the `secrets-config` boundary**. **It does NOT re-open C1's migration model or C2's grant-DDL text** —
it designs **how they are provisioned/executed/connected per environment**. **No credentials/connection-string
values appear here** — only variable-name **shapes** + the `secrets-config` contract (SEC-3).

> **Why this is a real stage (not a skip, unlike the four cluster units)**: `database` **IS the persistence
> topology** — Postgres instances (Docker dev + Render prod), role/grant provisioning, connection/pooling,
> migration execution. NFR Design deferred exactly these to here. `unit-of-work.md` pins database "comprehensive at
> Infrastructure Design."

---

## 1. Unit context (analyzed)

### 1.1 What Infrastructure Design maps (built ON — NOT re-opened)
- **From NFR Design (C1–C6)**: **C1 MigrationSequence** (the schema authority — its *model* is fixed; its *execution*
  per environment is designed here), **C2 GrantDDL** (the grant *text* is fixed as a migration step — its *execution*
  + role credential binding is designed here), C3 DbUrlGuard, C4 SchemaIntrospector, C5 FidelityComparator, C6
  MigrationChecksum (C3–C6 are app/test logic needing no cloud topology — noted, not provisioned).
- **From the FD/NFR**: DATA-5 (PostgreSQL everywhere; testcontainers for CI already established); ATOMIC-1
  co-location (one Postgres database/schema per environment); APPEND-1 (the `audit_writer`/`audit_reader` roles must
  be *created + granted* per environment — the Infra half); SEC-3 (no credentials in artifacts).

### 1.2 Reference boundaries (owned elsewhere)
- **`secrets-config`** owns **all credential/connection-string VALUES** (`DATABASE_URL`, role passwords) — this plan
  names the **contract shape** (variable names), never values (SEC-3).
- **`deploy-config`** owns the **Render/Vercel deploy pipeline** the migration-execution step plugs into — this plan
  designs the DB's **migration-run + provisioning** requirements that `deploy-config` wires.
- **`observability`** owns **app-level DB metrics/traces** — this plan names only the **managed-provider metrics**
  (Render's dashboard) as available, deferring app telemetry.
- **`quality-gates`** owns the **repo-wide no-SQLite CI aggregation**.

### 1.3 Guardrails held (skill)
DATA-5 (PostgreSQL everywhere, no SQLite); ATOMIC-1 (one co-located database/schema per env); APPEND-1/SEC-4/SEC-5
(role-enforced append-only + read-only auditor); SEC-3 (**no credentials in these artifacts** — `secrets-config`
supplies values); CON-BR1 (no demographic-driven infra); advisory-only. **No LLM anywhere in `database`.**

---

## 2. Mandatory infra-category pre-assessment (per the rule file — applicability + justification)

| Category | Applicability | Where |
|---|---|---|
| **Deployment Environment** | **Applicable** — dev (Docker) / CI (testcontainers) / prod (Render) | Q1, Q2 |
| **Storage Infrastructure** | **Applicable (core)** — the Postgres instance(s), version, co-location | Q1, Q2, Q11 |
| **Compute Infrastructure** | **Mostly N/A** — managed Postgres; migrations run as a **deploy step**, not a long-running compute this unit provisions | Q5, Q10 |
| **Messaging Infrastructure** | **N/A** — no queue/event bus in a schema unit (justified) | Q10 |
| **Networking Infrastructure** | **Applicable (narrow)** — Render internal vs external connection + SSL mode; no LB/gateway for a DB | Q4, Q8 |
| **Monitoring Infrastructure** | **Narrow** — provider (Render) DB metrics available; app telemetry deferred to `observability` | Q9 |
| **Shared Infrastructure** | **Applicable (central)** — `database` IS shared infra (audit-store now; auth-rbac/admin-cli later); isolation via **DB roles**, not separate instances | Q11 → `shared-infrastructure.md` |

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide the
**infrastructure mapping** — they do **not** re-open the FD, the NFR targets, or C1's migration model / C2's grant
text.

## Question 1 — Postgres provisioning topology (dev / CI / prod)
How is Postgres provisioned across the three tiers?

A) **Three-tier, all PostgreSQL (DATA-5), one co-located database/schema per environment**: **dev** = local
   **Docker Postgres** (Compose, Q7); **CI** = **testcontainers Postgres** (the established pattern — ephemeral per
   run); **prod** = **Render Postgres** (managed). Each environment has **one database + one schema** holding the
   co-located audit tables + `app_user` (ATOMIC-1). No SQLite anywhere.
B) A single shared cloud Postgres used for dev + CI + prod (rejected — non-hermetic CI; dev pollution; ATOMIC-1 fine
   but violates the hermetic testcontainers pattern).
C) SQLite for dev/CI, Postgres for prod only (rejected — DATA-5 dialect-drift).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — three-tier, all PostgreSQL, one co-located database/schema per environment: dev = local Docker Postgres (Compose); CI = testcontainers Postgres (established pattern, ephemeral per run); prod = Render Postgres (managed). Each environment has one database + one schema holding the co-located audit tables + app_user (ATOMIC-1). No SQLite anywhere.

## Question 2 — Postgres version + Render plan
What version and managed plan?

A) **Pin `postgres:16`** across all tiers — matching the testcontainers image already used
   (`PostgresContainer("postgres:16")`) so dev/CI/prod share the **same major version** (dialect parity protects
   replay/versioning, DATA-5 spirit). **Render Postgres free-tier** for the validation deploy (Phase 2; distinct from
   Phase-3 production), **SSL required**. Version pin recorded as an infra decision.
B) Let each environment float its Postgres version (rejected — version drift risks dialect differences).
C) A paid Render tier now (rejected — Phase-2 validation deploy is free-tier per `unit-of-work.md` U23).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — pin postgres:16 across all tiers, matching the testcontainers image already used, so dev/CI/prod share the same major version (dialect parity protects replay/versioning). Render Postgres free-tier for the Phase-2 validation deploy, SSL required. Version pin recorded as an infra decision.

## Question 3 — Grant-DDL execution per environment (the Infra half of APPEND-1)
C2's grant-DDL **text** lives in the migration sequence. How is it **executed** per environment, and how are role
login passwords supplied without hardcoding?

A) **The grants run as part of the migration sequence in EVERY environment** (dev/CI/prod) — one `migrate`
   invocation creates the tables **and** the `audit_writer`/`audit_reader` roles + grants, so all tiers are
   identical. **Role login passwords are NOT hardcoded** (SEC-3): the `CREATE ROLE … LOGIN PASSWORD` value is
   **injected at execution time from `secrets-config`** (an env-var / templated parameter substituted by the
   migration runner) — the **DDL text carries a placeholder, never a value**. In CI the testcontainer uses ephemeral
   throwaway passwords; in prod the values come from `secrets-config`. **APPEND-1's role enforcement is thus real in
   every environment.**
B) Create roles manually in the Render dashboard once, outside migrations (rejected — non-reproducible; drifts from
   dev/CI; not captured by the MIGRATE-2 checksum).
C) Skip roles in dev/CI, only create them in prod (rejected — APPEND-1 must be testable in CI on real roles).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — the grants run as part of the migration sequence in EVERY environment (dev/CI/prod) — one migrate invocation creates the tables and the audit_writer/audit_reader roles + grants, so all tiers are identical. Role login passwords are NOT hardcoded: the CREATE ROLE ... LOGIN PASSWORD value is injected at execution time from secrets-config (an env-var/templated parameter substituted by the migration runner) — the DDL text carries a placeholder, never a value. CI uses ephemeral throwaway passwords; prod uses secrets-config values. APPEND-1's role enforcement is thus real in every environment.

## Question 4 — Connection + pooling configuration
What connection/pool settings does the application need (no credential values)?

A) **A SQLAlchemy engine config**: a bounded **connection pool** (e.g. `pool_size` + `max_overflow` sized for the
   free-tier connection cap), a **`pool_timeout`**, **`pool_pre_ping=True`** (drop stale connections — important on
   Render free-tier which may recycle), and **`sslmode=require`** for Render. The **values** for host/user/password
   come from `secrets-config` via `DATABASE_URL` (Q6) — **this design names the pool/SSL knobs, never the
   credentials** (SEC-3). Dev/CI (local/container) may use a smaller pool + `sslmode=disable` locally.
B) Unbounded/default pool, no pre-ping, no explicit SSL (rejected — Render free-tier recycles connections + requires
   SSL; unbounded pools exhaust the connection cap).
C) A new external connection-pooler service (e.g. PgBouncer) now (rejected — premature for the Phase-2 validation
   deploy; revisit if the free-tier cap is hit).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a SQLAlchemy engine config: a bounded connection pool (pool_size + max_overflow sized for the free-tier cap), pool_timeout, pool_pre_ping=True (drop stale connections, important on Render free-tier), and sslmode=require for Render. Values for host/user/password come from secrets-config via DATABASE_URL — this design names the pool/SSL knobs, never the credentials. Dev/CI may use a smaller pool + sslmode=disable locally.

## Question 5 — Migration execution in CI/CD (how C1 actually runs per environment)
How does the migration sequence run in each environment (a deployment step, not a re-opening of C1's model)?

A) **Migrations run as an explicit step in each environment's lifecycle**: **dev** = a Compose/`make` target
   (`migrate`) against the Docker Postgres; **CI** = run migrations against the testcontainer **before** the
   integration tests (so ATOMIC-1/APPEND-1/FIDELITY-1 run on the migrated schema); **prod** = a **Render release
   command / pre-deploy step** (`deploy-config` wires it) that applies the sequence before the app serves traffic.
   **Forward-only, idempotent-apply** (C1's model, unchanged). The **tool** (Alembic vs raw-SQL runner) is chosen at
   Code-Gen — this design pins the **execution point** in each environment, not the tool.
B) Run migrations automatically at app startup (rejected — races across instances; a failed migration blocks
   startup; the checksum/immutability discipline prefers an explicit gated step).
C) Apply migrations manually per environment (rejected — non-reproducible; drift risk).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — migrations run as an explicit step in each environment's lifecycle: dev = a Compose/make target against Docker Postgres; CI = run migrations against the testcontainer before integration tests; prod = a Render release command/pre-deploy step (deploy-config wires it) applying the sequence before the app serves traffic. Forward-only, idempotent-apply (C1's model, unchanged). Tool choice (Alembic vs raw-SQL runner) stays deferred to Code-Gen — this design pins the execution point, not the tool.

## Question 6 — The `secrets-config` boundary (contract shape only — no values)
What must `secrets-config` supply, named as a dependency contract?

A) **`secrets-config` supplies all VALUES; this design names only the SHAPES** (SEC-3): a **`DATABASE_URL`** (the
   app/owner connection, `postgresql://…` scheme — validated by C3's DbUrlGuard), plus the **role credentials** the
   grants need — e.g. **`AUDIT_WRITER_PASSWORD` / `AUDIT_READER_PASSWORD`** (consumed at role-creation time, Q3) and
   optionally **`AUDIT_WRITER_URL` / `AUDIT_READER_URL`** for the role-scoped connections APPEND-1's prod path uses.
   **Only variable NAMES appear in `database`'s artifacts — never a value.** `secrets-config` (U16, SEC-3) owns the
   vault/env wiring.
B) Put credentials directly in the database unit's config files (rejected — SEC-3 violation; the build fails on a
   hardcoded secret).
C) Leave the secrets contract unspecified (rejected — `secrets-config` needs the exact variable shapes to supply).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — secrets-config supplies all VALUES; this design names only the SHAPES: a DATABASE_URL (the app/owner connection, postgresql:// scheme, validated by C3's DbUrlGuard), plus role credentials — AUDIT_WRITER_PASSWORD/AUDIT_READER_PASSWORD (consumed at role-creation time) and optionally AUDIT_WRITER_URL/AUDIT_READER_URL for role-scoped connections in prod. Only variable NAMES appear in database's artifacts — never a value.

## Question 7 — Local dev: Docker Compose matching the testcontainers pattern
What does local dev use?

A) **A `docker-compose.yml`** with a **`postgres:16`** service (same major version as testcontainers → dialect
   parity), a **named volume** for persistence, a **healthcheck**, and a mapped port; the app + the `migrate` target
   connect to it. **Mirrors the CI testcontainers image/version** so dev and CI behave identically. No credentials
   committed — local dev uses a **non-secret local default** or a `.env` **that `secrets-config`/`.gitignore`
   governs** (values never in the repo).
B) Expect developers to install Postgres natively (rejected — non-reproducible across machines; version drift).
C) Use a cloud dev database (rejected — non-hermetic; couples dev to network/credentials).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a docker-compose.yml with a postgres:16 service (same major version as testcontainers, dialect parity), a named volume for persistence, a healthcheck, and a mapped port; the app + migrate target connect to it. Mirrors the CI testcontainers image/version. No credentials committed — local dev uses a non-secret local default or a .env that secrets-config/.gitignore governs.

## Question 8 — Networking (Render connection path + SSL)
What networking does the DB need?

A) **Narrow + managed**: on Render, the app connects to Postgres via Render's **internal/private connection URL**
   where available (lower latency, not public), with **`sslmode=require`**; the external URL is used only for
   migration/admin from CI/deploy. **No load balancer, API gateway, or custom VPC** is designed for the DB (a managed
   single-instance Postgres — those are N/A for a schema unit, justified). Connection **values** come from
   `secrets-config`.
B) Expose the database on a public endpoint without SSL (rejected — insecure; Render requires SSL).
C) Design a full VPC/subnet/LB topology now (rejected — over-engineering for a managed Postgres on the Phase-2
   free-tier deploy).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — narrow + managed: the app connects via Render's internal/private connection URL where available, with sslmode=require; the external URL is used only for migration/admin from CI/deploy. No load balancer, API gateway, or custom VPC designed for the DB — those are N/A for a managed single-instance Postgres, justified. Connection values come from secrets-config.

## Question 9 — Monitoring (provider metrics vs observability unit)
What monitoring does this unit's infra design pin?

A) **Provider-level only, app-telemetry deferred**: name **Render's managed Postgres metrics** (connection count,
   storage, CPU) as the available DB-health signal for the validation deploy; **app-level DB metrics/traces + Grafana
   dashboards are `observability`'s (U21) concern** (referenced, not built here). A basic **connection/health check**
   (the pool `pre_ping` + a `SELECT 1` readiness probe) is named. No demographic-derived metric (CON-BR1).
B) Build a full Prometheus/Grafana DB-metrics stack here (rejected — that's `observability`'s unit).
C) No monitoring at all (rejected — at least provider metrics + a health probe are needed for a real deploy).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — provider-level only, app-telemetry deferred: name Render's managed Postgres metrics (connection count, storage, CPU) as the available DB-health signal; app-level DB metrics/traces + Grafana dashboards are observability's (U21) concern, referenced not built here. A basic connection/health check (pool pre_ping + a SELECT 1 readiness probe) is named. No demographic-derived metric.

## Question 10 — Compute + Messaging (explicit N/A justification)
How are these categories handled?

A) **Explicit N/A with justification**: **Compute** — no compute service is provisioned by `database`; Postgres is a
   **managed service**, and migrations run as a **short deploy step** (Q5), not a long-running compute this unit owns
   (the app's compute is `deploy-config`'s Render web service). **Messaging** — **no queue/event bus**; the schema
   unit has no async/eventing concern (audit-store's ATOMIC-1 is a single synchronous transaction, not an
   outbox/saga — explicitly recorded in the register). Both marked **N/A, justified**, in the compliance summary.
B) Provision a worker/queue for migrations (rejected — unnecessary; migrations are a deploy step).
C) Leave these categories unaddressed (rejected — the rule file requires explicit justification, not silence).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — explicit N/A with justification: Compute — no compute service provisioned by database; Postgres is a managed service, migrations run as a short deploy step, not a long-running compute this unit owns. Messaging — no queue/event bus; the schema unit has no async/eventing concern (ATOMIC-1 is a single synchronous transaction, not an outbox/saga — recorded in the register). Both marked N/A, justified, in the compliance summary.

## Question 11 — Shared Infrastructure (database IS shared infra)
How is the shared nature designed, and does it produce `shared-infrastructure.md`?

A) **Yes — produce `guide-docs/build/shared-infrastructure.md`**: the **single Postgres instance + one schema per
   environment** is **shared** by `audit-store` now (and `auth-rbac` / `admin-cli` later); **isolation is via DB
   roles** (`audit_writer` / `audit_reader`, + the app/owner role), **NOT separate instances** — co-location
   (ATOMIC-1) requires one database. Multi-consumer access is **role-scoped**, not instance-scoped. The doc records
   the shared instance, the role model, and the co-location constraint as the shared contract.
B) Give each consumer its own database/instance (rejected — breaks ATOMIC-1 co-location; audit-store's transaction
   spans its tables in one database).
C) Don't document the sharing (rejected — the rule file calls for `shared-infrastructure.md` when infra is shared).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — yes, produce guide-docs/build/shared-infrastructure.md: the single Postgres instance + one schema per environment is shared by audit-store now (and auth-rbac/admin-cli later); isolation is via DB roles (audit_writer/audit_reader + the app/owner role), NOT separate instances — co-location (ATOMIC-1) requires one database. Multi-consumer access is role-scoped, not instance-scoped. The doc records the shared instance, the role model, and the co-location constraint as the shared contract.

## Question 12 — Depth + artifacts + Mermaid
Depth, artifacts, and diagrams?

A) **Comprehensive** — three artifacts: **`infrastructure-design.md`** (the component→infrastructure mapping + the
   deferred-halves execution design), **`deployment-architecture.md`** (the dev/CI/prod topology + migration-execution
   + connection/SSL flow), and **`shared-infrastructure.md`** (Q11). **Validated Mermaid** required: a **deployment
   topology** diagram (dev/CI/prod + Postgres + migration-run + the `secrets-config`/`deploy-config`/`observability`
   boundaries) with a text alternative, against the 7 rules.
B) Standard — fewer artifacts, one diagram.
C) Minimal — a sketch.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — comprehensive: three artifacts — infrastructure-design.md (component→infrastructure mapping + the deferred-halves execution design), deployment-architecture.md (dev/CI/prod topology + migration-execution + connection/SSL flow), and shared-infrastructure.md (Q11). Validated Mermaid required: a deployment topology diagram (dev/CI/prod + Postgres + migration-run + secrets-config/deploy-config/observability boundaries) with a text alternative.

---

## 4. Artifacts to generate (after answers + ambiguity-check)
`guide-docs/build/database/infrastructure-design/` → **`infrastructure-design.md`** + **`deployment-architecture.md`**;
and **`guide-docs/build/shared-infrastructure.md`** (shared-infra doc). Each with **validated Mermaid + text
alternative**. **No credentials/connection-string values anywhere** (SEC-3).

---

## 5. Constraints & settled items held (not re-opened)
- FD + approved NFR targets + NFR Design patterns/components (C1–C6) are the substrate — Infra maps them, re-opening
  none. **C1's migration model + C2's grant-DDL text are NOT re-opened** — this stage designs their **execution +
  provisioning** per environment.
- **SEC-3**: no credential/connection-string **values** in any artifact — only variable-name **shapes** + the
  `secrets-config` contract (Q6). The build fails on a hardcoded secret.
- **DATA-5**: PostgreSQL in every tier (Docker dev / testcontainers CI / Render prod), `postgres:16` pinned; no
  SQLite. **ATOMIC-1**: one co-located database/schema per environment. **APPEND-1**: roles created + granted per
  environment (Q3), enforcement real in CI + prod.
- Reference boundaries: `secrets-config` (values), `deploy-config` (deploy pipeline), `observability` (app DB
  telemetry), `quality-gates` (no-SQLite CI aggregation) — named as dependencies, not authored here.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, the OOS-7/OOS-8 doc commitments.

---

## 6. Next step (STOP here)
Fill the twelve `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then generate the three `database` Infrastructure Design artifacts
(with validated Mermaid + text alternatives) and present the standardized completion + 2-option message
(Request Changes / Continue → **Code Generation**). **No Infrastructure-Design artifacts or code are generated until
the answers are in and checked.**
