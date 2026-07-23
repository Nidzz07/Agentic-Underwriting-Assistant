# Shared Infrastructure — the single Postgres instance (owned by `database`, U15)

**Stage**: BUILD → Infrastructure Design · **Owning unit**: U15 `database` · **Date**: 2026-07-06
**Scope**: The **shared contract** for the one Postgres instance + one schema that multiple units depend on. Produced
because `database` **IS** shared infrastructure (Q11) and the rule file calls for `shared-infrastructure.md` when infra
is shared. **SEC-3**: no credential/connection-string **values** here — only the shared topology + role model.

This is the **single source of the shared persistence contract**. Consuming units (`audit-store` now; `auth-rbac` /
`admin-cli` later) read this to know what instance they share and how they are isolated.

---

## 1. The shared instance (one Postgres, one schema per environment)

There is **one Postgres instance with one database + one schema per environment** (dev Docker / CI testcontainers /
prod Render — all `postgres:16`). It is **shared** by:

- **`audit-store`** — **now**: the two co-located audit tables (`audit_record` + `applicant_profile_snapshot`).
- **`auth-rbac`** — **later**: the `app_user` foundational skeleton (open `role`) + its own forward-only extensions.
- **`admin-cli`** — **later**: consumes `app_user`; the rulebook-version registry is its future reserved slot.

**Multi-consumer access is role-scoped, NOT instance-scoped** — consumers do **not** each get their own
database/instance. Isolation is achieved with **DB roles** on the one shared instance (§2).

---

## 2. Role-based isolation model

| Role | Grants | Used by |
|---|---|---|
| **`audit_writer`** | **INSERT + SELECT** on the audit tables (no UPDATE, no DELETE) | audit-store **write path** (via `AUDIT_WRITER_URL`) |
| **`audit_reader`** | **SELECT only** on the audit tables (no write of any kind) | audit-store **auditor read surface** (via `AUDIT_READER_URL`) |
| **app / owner** | schema-owning + migration/admin | migration execution + schema ownership (via `DATABASE_URL`) |

The `audit_writer` INSERT+SELECT-only grant is the **DB-role half** of append-only (BR-DB-4 layer (b), SEC-5) — it
holds even if the service layer were bypassed. `audit_reader` SELECT-only is the SEC-4 read-only auditor. The grants are
authored as a step in the migration sequence (C2) and executed per tier with passwords substituted from `secrets-config`
at execution time (placeholder-never-value; `database/infrastructure-design/infrastructure-design.md §3.2`).

> **APPEND-1 realism depends on runtime role selection**: the DB-role guarantee is only real in prod if the app
> **connects via the least-privilege role connections** (`AUDIT_WRITER_URL` / `AUDIT_READER_URL`) rather than as the
> owner — hence those URLs are **required for the guarantee** (`infrastructure-design.md §5.1`). `database` guarantees
> the roles exist + are granted (proven in CI); the runtime wiring is `audit-store` / `deploy-config`
> (reference-not-own).

---

## 3. Why isolation is role-based, not instance-based (the ATOMIC-1 co-location rationale)

audit-store's **ATOMIC-1** guarantee (atomic both-or-neither commit + profile-snapshot persist) rests on a **single
ACID transaction** — one `engine.begin()` across `audit_record` **and** `applicant_profile_snapshot`. A single
transaction spans only tables **co-located in ONE database reachable on ONE connection** (BR-DB-7, COLOC-1).

- If the two tables were split across **separate databases/instances**, the single transaction would be impossible and
  ATOMIC-1 would require an **outbox/saga** mechanism instead — a heavier, weaker guarantee.
- Therefore the two audit tables **MUST** stay in **one co-located database/schema**, and multi-consumer isolation is
  achieved with **DB roles on that one instance**, **not** by giving each consumer its own instance.

Giving each consumer its own database (the rejected Q11 option B) would **break ATOMIC-1 co-location**. The shared
single instance + role isolation is the design that keeps ATOMIC-1 valid while still isolating consumers.

---

## 4. Deferred: `auth-rbac`'s own dedicated DB role (NOT resolved here) — flag

Whether **`auth-rbac` wants its OWN dedicated PostgreSQL DB role scoped to `app_user`** (a least-privilege DB role for
the auth service, **distinct from** `audit_writer` / `audit_reader`) is **`auth-rbac`'s own future design decision —
NOT resolved by `database`.**

- The current three-role model (`audit_writer` / `audit_reader` / app-owner) covers the **audit** tables.
- `app_user.role` **column** values (`underwriter` / `auditor` / `admin`) are **application-level data**, entirely
  distinct from PostgreSQL **DB roles** — so auth-rbac needs **no new DB role** merely to store `app_user` rows.
- A future dedicated auth DB role, if `auth-rbac` chooses one, is a **forward-only migration addition** that does
  **not** disturb the audit roles.

**Recorded in the Deferred Decisions register** (guide-state.md) as `auth-rbac`'s own call.

---

## 5. The shared contract (summary consumers rely on)

1. **One Postgres instance, one database + one schema, per environment** (`postgres:16`, DATA-5 — no SQLite).
2. **Co-location is mandatory** for audit-store's tables (ATOMIC-1 / COLOC-1 / BR-DB-7) — never split.
3. **Isolation is via DB roles** (`audit_writer` / `audit_reader` / app-owner), not separate instances.
4. **Schema authority is `database`'s migration sequence** (C1) — the sole authoritative schema; consumers keep
   conforming `Table`/query mappings whose columns must match (FIDELITY-1 guards drift). No consuming code is edited by
   `database`.
5. **Credentials/connection values are `secrets-config`'s** (SEC-3) — this doc names roles + URL shapes, never values.
6. **`auth-rbac`'s own dedicated DB role is deferred** to `auth-rbac` (§4).

---

## 6. Settled items held (not re-opened)

- ATOMIC-1 co-location + the two role grants come straight from the frozen FD (BR-DB-4/5/7) and the tracked cross-unit
  constraint — this doc records the shared contract, it does not re-open the schema or the grant text.
- **SEC-3** (no values), **DATA-5** (`postgres:16` every tier, no SQLite), **CON-BR1** (no demographic-driven infra),
  **advisory-only**, **no LLM** in `database`.
- Reference-not-own: `auth-rbac`'s role model + any dedicated auth DB role, `observability`'s DB telemetry,
  `secrets-config`'s values, `deploy-config`'s pipeline + runtime role-connection wiring — all named, none authored
  here.
