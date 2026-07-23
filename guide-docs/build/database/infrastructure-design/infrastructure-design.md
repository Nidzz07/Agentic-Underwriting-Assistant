# Infrastructure Design — `database` (EPIC-6 / U15)

**Stage**: BUILD → Infrastructure Design (per-unit) · **the first NON-SKIP Infrastructure Design in the build**
**Unit**: U15 `database` · **Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: comprehensive.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`), the approved
`nfr-requirements.md` (`NFR-DB-*`), and the approved NFR Design (`nfr-design-patterns.md` + `logical-components.md`,
components **C1–C6**) — **re-opening none of them**. This stage designs the **deferred halves** NFR Design explicitly
handed here: **Postgres provisioning, grant-DDL execution, connection/pooling, and migration execution per
environment**. **It does NOT re-open C1's migration model or C2's grant-DDL text** — it designs **how they are
provisioned / executed / connected** per tier.

> **SEC-3 held throughout**: **no credential or connection-string VALUES** appear in this artifact — only variable-name
> **shapes** and the `secrets-config` contract. The build fails on a hardcoded secret (BR-DB-13).

---

## 1. Component → infrastructure mapping (C1–C6)

The 6 NFR-Design components are either **provisioned** (given a real per-tier home) or **noted as app/test logic**
needing no cloud topology. The migration sequence (C1) stays the **sole schema authority** — Infrastructure Design
**executes** it, it does **not** author schema.

| Component | Kind | Infrastructure realization (this stage) |
|---|---|---|
| **C1 MigrationSequence** | schema authority | **Executed** as an explicit migration step against the provisioned Postgres of each tier (§3.4). Infra pins the **execution point** + the instance; the **model** (forward-only, one authoritative sequence) is unchanged. |
| **C2 GrantDDL** | text step within C1 | **Executed** as part of the same migration run in **every** tier (§3.2). Role login passwords are **substituted from `secrets-config` at execution time** via a placeholder token — the committed file never holds a value. |
| **C3 DbUrlGuard** | pure app config logic | **No cloud topology.** Runs at application/config load against the injected `DATABASE_URL` (§4). Named, not provisioned. |
| **C4 SchemaIntrospector** | test logic | **No cloud topology.** Reads the live migration-produced schema of the **CI testcontainer**. Named, not provisioned. |
| **C5 FidelityComparator** | test logic | **No cloud topology.** Reads `pg_repository` metadata read-only in CI. Named, not provisioned. |
| **C6 MigrationChecksum** | test logic | **No cloud topology.** Hashes the committed migration files (incl. the grants file) in CI/unit. Named, not provisioned. |

**Infra provisions the substrate C1/C2 run on; C3–C6 are app/test logic that need only a Postgres to run against.**

---

## 2. Mandatory infra-category sweep (all seven categories — explicit applicability + justification)

| # | Category | Applicability | Justification |
|---|---|---|---|
| 1 | **Deployment Environment** | **Applicable** | Three tiers — **dev** (local Docker Postgres, Compose), **CI** (testcontainers Postgres, ephemeral per run), **prod** (Render Postgres, managed, Phase-2 validation deploy). §3.1. |
| 2 | **Storage Infrastructure** | **Applicable (core)** | `database` **IS** the storage topology: one Postgres instance + **one co-located database/schema** per tier holding the two audit tables + `app_user` (ATOMIC-1 / COLOC-1). `postgres:16` pinned. §3.1, §3.3. |
| 3 | **Compute Infrastructure** | **N/A (justified)** | No compute service is provisioned by `database`. Postgres is a **managed service**; migrations run as a **short deploy step** (§3.4), not a long-running compute this unit owns. The app's web compute is `deploy-config`'s Render service. |
| 4 | **Messaging Infrastructure** | **N/A (justified)** | No queue / event bus. ATOMIC-1 is a **single synchronous ACID transaction**, not an outbox/saga (BR-DB-7); a schema unit has no async/eventing concern. |
| 5 | **Networking Infrastructure** | **Applicable (narrow)** | Render **internal/private** connection URL where available + **`sslmode=require`**; external URL only for migration/admin from CI/deploy. **No LB / API gateway / custom VPC** for a managed single-instance Postgres (§3.5, `deployment-architecture.md`). |
| 6 | **Monitoring Infrastructure** | **Applicable (narrow)** | Provider-level only: **Render managed Postgres metrics** (connections, storage, CPU) + a **`SELECT 1` readiness probe** and pool `pre_ping`. App-level DB metrics/traces deferred to **`observability` (U21)**. No demographic-derived metric (CON-BR1). |
| 7 | **Shared Infrastructure** | **Applicable (central)** | `database` **IS** shared infra — one Postgres, one schema, shared by `audit-store` now (and `auth-rbac` / `admin-cli` later); isolation via **DB roles**, not separate instances. See `shared-infrastructure.md`. |

**No category silently skipped.** Compute + Messaging are **N/A with justification**, recorded in the completion
compliance summary.

---

## 3. Deferred-halves execution design

### 3.1 Postgres provisioning per tier (Storage + Deployment)

| Tier | Provisioning | Notes |
|---|---|---|
| **dev** | Local **Docker Postgres** via `docker-compose.yml` — a **`postgres:16`** service, named volume, healthcheck, mapped port. | Mirrors the CI image/version → dialect parity. `deployment-architecture.md §2`. |
| **CI** | **testcontainers Postgres** — **`PostgresContainer("postgres:16")`**, ephemeral per run, auto-torn-down. | The **already-established** pattern — confirmed in the built `backend/audit_store/tests/test_pg_integration.py:45`. Hermetic. |
| **prod** | **Render Postgres** — managed, **free-tier** (Phase-2 validation deploy, distinct from Phase-3 production), **SSL required**. | Single managed instance; connection values from `secrets-config`. |

Every tier holds **one database + one schema** with the two co-located audit tables + `app_user` (ATOMIC-1 / COLOC-1,
BR-DB-7). **No SQLite anywhere** (DATA-5, BR-DB-6). `postgres:16` is pinned across all three tiers so dev/CI/prod share
the **same major version** — dialect parity protects replay/versioning byte-fidelity (BR-DB-10, REPLAY-1/DET-2).

### 3.2 Grant-DDL execution — the pinned placeholder-substitution mechanism (Infra half of APPEND-1) — **FOLD #1**

C2's grant-DDL **text** is a fixed step in the migration sequence (a database-unit Code-Gen deliverable). Infrastructure
Design owns only its **per-tier execution + credential binding**. The mechanism is pinned **concretely** so it is
implementable at Code-Gen and provably SEC-3-safe:

1. **The committed grants migration file carries a PLACEHOLDER TOKEN only — never a real value.** The
   `CREATE ROLE audit_writer … LOGIN PASSWORD` statement contains a named parameter, e.g.
   **`${AUDIT_WRITER_PASSWORD}`** (and `${AUDIT_READER_PASSWORD}` for `audit_reader`). No password literal is ever
   committed to the repository.
2. **The migration runner substitutes the token from the environment at execution time** — reading the
   `AUDIT_WRITER_PASSWORD` / `AUDIT_READER_PASSWORD` env vars (supplied by `secrets-config`, §5) and rendering the final
   SQL **in memory** immediately before it is sent to Postgres.
3. **MIGRATE-2's checksum hashes the placeholder-bearing committed file** (C6). Because the committed content is the
   token (not the secret), the checksum is **stable** — yet an **edited grant statement is still caught** (a weakened
   `audit_reader` grant, a changed role name, an added `INSERT` → changed hash → fail). **The secret lives entirely
   outside the checksummed content.**
4. **The rendered / substituted SQL is never logged** (SEC-3). Only the placeholder-bearing form is ever written to
   disk or logs; the runtime-rendered form exists transiently in memory for the single execution.
5. **Applied identically in every tier**: in **CI** the testcontainer uses ephemeral throwaway passwords; in **prod**
   the values come from `secrets-config`. The versioned runner applies the grants migration **once** per instance
   (idempotency via C1's forward-only version tracking). **APPEND-1's role enforcement is therefore real in every
   environment** — CI proves the write matrix (`audit_writer`: INSERT/SELECT ok, UPDATE/DELETE raise; `audit_reader`:
   SELECT ok, all writes raise) on real Postgres roles.

> **Boundary held**: no component/step here executes grants against a **deployed** instance during design — the NFR
> tests apply them to an **ephemeral** container (NFR Design §2). This stage designs the **execution wiring** the
> `deploy-config` release step invokes; it does not run production DDL.

### 3.3 Connection / pooling configuration (Networking)

A **SQLAlchemy engine config** naming the knobs only (values from `secrets-config`, SEC-3):

- **Bounded connection pool** — `pool_size` + `max_overflow` sized for the Render **free-tier connection cap** (a small
  bounded pool; unbounded pools exhaust the cap).
- **`pool_timeout`** — bounded wait for a pooled connection.
- **`pool_pre_ping=True`** — drop stale connections before use (important on Render free-tier, which may recycle idle
  connections).
- **`sslmode=require`** on Render (prod); dev/CI (local/container) may use a smaller pool + `sslmode=disable` locally.

Host/user/password come from `secrets-config` via `DATABASE_URL` (and the role-scoped URLs, §5) — **this design names
the pool/SSL knobs, never the credentials.** No external connection-pooler service (e.g. PgBouncer) is provisioned now
(premature for the Phase-2 validation deploy; revisit only if the free-tier cap is hit).

### 3.4 Migration execution per environment (how C1 runs — not a re-opening of its model)

C1 stays **forward-only, one authoritative sequence, idempotent-apply** (model unchanged). Infra pins the **execution
point** in each tier's lifecycle; the **tool** (Alembic vs a raw-SQL runner) is deferred to Code-Gen:

| Tier | Migration execution point |
|---|---|
| **dev** | A Compose / `make migrate` target run against the local Docker Postgres. |
| **CI** | Migrations run against the testcontainer **before** the integration tests, so ATOMIC-1 / APPEND-1 / FIDELITY-1 / BYTEA-1 / SCOPE-1 all run on the **migrated** schema. |
| **prod** | A **Render release command / pre-deploy step** (wired by `deploy-config`) applies the full sequence **before** the app serves traffic. |

Migrations are **not** run at app startup (rejected — races across instances; a failed migration would block startup;
the checksum/immutability discipline prefers an explicit gated step).

### 3.5 Networking (summary — full topology in `deployment-architecture.md`)

Narrow + managed: on Render the app connects via the **internal/private** connection URL where available (lower
latency, not public) with **`sslmode=require`**; the **external** URL is used only for migration/admin from CI/deploy.
**No load balancer, API gateway, or custom VPC** is designed for a managed single-instance Postgres — those are N/A for
a schema unit (justified). Connection values come from `secrets-config`.

---

## 4. `DbUrlGuard` (C3) placement

`require_postgres_url(url)` runs at **application / config load** against the injected `DATABASE_URL`, raising on any
non-`postgresql://` scheme (SQLite rejected — DATA-5, DATA5-1). It is **pure app logic** needing **no cloud topology**;
Infra names **where** it runs (config load, every tier) but provisions nothing for it.

---

## 5. `secrets-config` contract (SHAPES only — no values) — **FOLD #2 + FOLD #4**

`secrets-config` (U16) owns **all credential/connection-string VALUES**; this design names only the **variable-name
shapes** (SEC-3, BR-DB-13). **Only variable NAMES appear below — never a value.**

| Variable (shape) | Purpose | Required? |
|---|---|---|
| **`DATABASE_URL`** | The app/owner connection (`postgresql://…` scheme, validated by C3's `DbUrlGuard`). Used for schema-owning operations + migration/admin. | **Required** |
| **`AUDIT_WRITER_PASSWORD`** | Substituted into the `CREATE ROLE audit_writer … LOGIN PASSWORD ${AUDIT_WRITER_PASSWORD}` grants migration at execution time (§3.2). Never committed. | **Required** (roles must exist + be granted) |
| **`AUDIT_READER_PASSWORD`** | Substituted into `CREATE ROLE audit_reader … LOGIN PASSWORD ${AUDIT_READER_PASSWORD}` at execution time. Never committed. | **Required** |
| **`AUDIT_WRITER_URL`** | The **least-privilege role-scoped connection** the application's **write path** uses at runtime (connects **as `audit_writer`**). | **REQUIRED for the APPEND-1 prod guarantee** — see below |
| **`AUDIT_READER_URL`** | The **least-privilege role-scoped connection** the **auditor read surface** uses at runtime (connects **as `audit_reader`**). | **REQUIRED for the APPEND-1 prod guarantee** — see below |

### 5.1 Why `AUDIT_WRITER_URL` / `AUDIT_READER_URL` are REQUIRED, not "optional" (FOLD #2)

`database` **guarantees the roles exist and are granted** — proven in CI (APPEND-1 write matrix on real Postgres roles).
But that guarantee is only **real in production** if the running application **actually connects via the
least-privilege `audit_writer` / `audit_reader` connections** at runtime:

- If the app connected as the **owner/superuser** role at runtime, DB-role enforcement would be **bypassed** — APPEND-1
  would be **vacuous in prod** even though CI proves the roles work correctly. Append-only would then rest on the
  **service layer alone** (BR-DB-4 layer (a)), losing the DB-role belt-and-suspenders (layer (b)).
- Therefore these two role-scoped URLs are **required for the guarantee**, not a nice-to-have. They are marked
  **REQUIRED** here so `secrets-config` supplies them and `deploy-config` wires them.

**Ownership boundary (reference-not-own):** **this unit guarantees the roles exist + are granted**; it does **not** own
**how the application chooses which role to connect as** at runtime. The actual application wiring of the
`AUDIT_WRITER_URL` / `AUDIT_READER_URL` connections is **delegated to `audit-store` / `deploy-config`** (audit-store's
runtime engine selection + deploy-config's env wiring). `database` names the contract shape and states the dependency;
it does not implement the connection selection.

### 5.2 Dev `.env` hygiene (SEC-3) — **FOLD #4**

The local dev `.env` holds a **real local dev connection string** (a non-secret local default or a developer's local
password). It **MUST be gitignored and never committed** — a real connection value must not enter the repository. This
**enforcement is owned by `secrets-config`** (env/secrets governance + `.gitignore`); it is **named here as a
dependency**, not implemented in the `database` unit. No `.env` value is echoed anywhere in these artifacts.

---

## 6. Reference boundaries (owned elsewhere — named, not authored here)

| Concern | Owner |
|---|---|
| All credential / connection-string **values**; `.env`/`.gitignore` governance | **`secrets-config`** (U16) |
| The Render/Vercel **deploy pipeline** the migration-execution step plugs into; runtime **role-connection wiring** | **`deploy-config`** |
| **App-level** DB metrics / traces / Grafana dashboards | **`observability`** (U21) |
| Repo-wide **no-SQLite CI aggregation** | **`quality-gates`** |
| Runtime **selection of which role-scoped connection** the app uses (write path as `audit_writer`, reads as `audit_reader`) | **`audit-store`** (runtime engine) + **`deploy-config`** (env wiring) |

---

## 7. Deferred decision recorded this stage — **FOLD #3**

**Whether `auth-rbac` wants its OWN dedicated PostgreSQL DB role scoped to `app_user`** (a least-privilege DB role for
the auth service, **distinct from** `audit_writer` / `audit_reader`) is **`auth-rbac`'s own future design decision —
NOT resolved here.** The current three-role model (`audit_writer` / `audit_reader` / app-owner) covers the **audit**
tables. Note that `app_user.role` **column** values (`underwriter` / `auditor` / `admin`) are **application-level** data
values, entirely distinct from PostgreSQL **DB roles** — so auth-rbac needs no new DB role merely to store `app_user`
rows. A future dedicated auth DB role, if `auth-rbac` chooses one, is a **forward-only migration addition** that does
**not** disturb the audit roles. **Recorded in the Deferred Decisions register** and in `shared-infrastructure.md §4`.

---

## 8. Constraints & settled items held (not re-opened)

- FD + approved `NFR-DB-*` targets + NFR Design patterns/components (C1–C6) are the substrate — Infra maps them,
  re-opening none. **C1's migration model + C2's grant-DDL text are NOT re-opened** — only their execution/provisioning
  per tier is designed.
- **SEC-3**: no credential/connection-string **values** — only variable-name shapes + the `secrets-config` contract
  (§5). The rendered grant SQL is never logged (§3.2).
- **DATA-5**: PostgreSQL every tier (Docker dev / testcontainers CI / Render prod), `postgres:16` pinned; no SQLite.
  **ATOMIC-1 / COLOC-1**: one co-located database/schema per tier. **APPEND-1**: roles created + granted per tier,
  enforcement real in CI + prod (contingent on the required role-scoped runtime connections, §5.1).
- **CON-BR1**: no demographic-derived infra, metric, or index. **Advisory-only**: nothing here implies the system
  decides. **No LLM anywhere in `database`.**
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, the OOS-7/OOS-8 doc commitments, and **no consuming unit's code**
  (audit-store's `pg_repository.py` is imported read-only by C5's test only — never edited).
