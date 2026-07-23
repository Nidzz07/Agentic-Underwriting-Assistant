# Business Rules — `database` (EPIC-6 / U15)

**Stage**: BUILD → Functional Design (per-unit) · story-less shared infrastructure
**Unit**: U15 `database`
**Date**: 2026-07-06
**Scope**: The **integrity + governance rules** the production schema enforces or mandates. Each rule
states its **condition explicitly**. These are **schema-level** rules (structure, constraints, role
semantics, dialect, co-location) — they do **not** re-open any consuming unit's business logic. Grant
**execution** and connection **provisioning** are named as the Infrastructure-Design boundary, not
performed here (SEC-3).

---

## 1. Structural integrity rules

### BR-DB-1 — Primary keys
- **Condition**: `audit_record.decision_id` is the **primary key** (unique, NOT NULL);
  `applicant_profile_snapshot.decision_id` is its primary key; `app_user.user_id` is its primary key.
- **Why**: one row per committed decision, addressable by `decision_id` (audit-store `get`/`browse`).

### BR-DB-2 — The co-located foreign key
- **Condition**: `applicant_profile_snapshot.decision_id` is a **foreign key → `audit_record.decision_id`**.
  A profile-snapshot row **cannot exist without** its parent `audit_record` row.
- **Why**: makes the profile snapshot a genuine co-located child so audit-store's **two-row insert is
  one atomic both-or-neither write** (ATOMIC-1; BR-DB-7).

### BR-DB-3 — NOT-NULL / nullability (exactly as verified against the built repository)
- **Condition**: **NOT NULL** on `audit_record`: `decision_id`, `application_id`, `recommendation_id`,
  `rulebook_version`, `rule_results`, `timestamp`, `model_version`, `memo_hash`, `engine_version`,
  `underwriter_id`, `action`, `status`. **Nullable**: `reason`, `supersedes_decision_id`. On
  `applicant_profile_snapshot`: all four NOT NULL. On `app_user`: all three NOT NULL.
- **Why**: the 6-tuple + commit linkage must be complete on every committed decision (TUPLE-1);
  `reason` is nullable because free-text is only mandatory **on override** (enforced at the service
  gate, BR-DB-8); `supersedes_decision_id` is null until a Phase-3 supersession.

### BR-DB-9 — `action` / `status` are varchar, not native PG ENUM (fold #3)
- **Condition**: `audit_record.action` and `audit_record.status` are **`VARCHAR`** columns storing the
  enum **`.value` strings** the built repository writes (`approve`/`override`; `active`/`superseded`).
  An **optional `CHECK` constraint** on the allowed value set MAY be declared. A **native PostgreSQL
  `ENUM` type is NOT used**.
- **Why**: column-for-column fidelity with the built `pg_repository.py` (which writes `.value` strings);
  a native ENUM would accept the same values but diverge from the built code and complicate later value
  additions.

---

## 2. Append-only + role governance (SEC-4 / SEC-5 / CON-AUDIT-1)

### BR-DB-4 — Append-only on committed audit rows
- **Condition**: **No `UPDATE` and no `DELETE`** on `audit_record` or `applicant_profile_snapshot`
  committed rows. Writes are **INSERT-only**. Corrections (Phase 3) happen via a **new superseding
  row** (BR-DB-8), never in-place mutation.
- **Realization (two layers)**: (a) **service layer** — audit-store exposes no mutation path; (b)
  **DB-role layer** — the `audit_writer` role is granted **INSERT + SELECT only** (no UPDATE/DELETE),
  so append-only holds even if the service were bypassed. This is the DB-role half of audit-store's
  **APPEND-1** integration tests.

### BR-DB-5 — Role semantics: `audit_writer` / `audit_reader`
- **Condition**: **`audit_writer`** may **`INSERT` + `SELECT`** on the audit tables (no `UPDATE`, no
  `DELETE`). **`audit_reader`** may **`SELECT` only** (SEC-4 read-only auditor — no write of any kind).
  Both are scoped to `audit_record` + `applicant_profile_snapshot`.
- **FD vs Infrastructure boundary**: this FD **pins the role semantics** (what each role may do — a
  governance invariant). The **grant DDL text** (`CREATE ROLE …; GRANT …;`) and its **execution /
  credential binding** (which Postgres instance, local Docker vs Render, secrets via `secrets-config`)
  belong to **Infrastructure Design + `secrets-config`** — **not executed here** (SEC-3). See
  `business-logic-model.md §3`.

---

## 3. Dialect + topology rules

### BR-DB-6 — DATA-5: PostgreSQL only, no SQLite (per-tier)
- **Condition**: the schema runs on **PostgreSQL in every tier** — dev (Docker Postgres), test/CI
  (**real Postgres via testcontainers**, the pattern audit-store already uses:
  `@pytest.mark.integration`, never SQLite), prod (Render Postgres). **SQLite is used nowhere.**
- **Structural guard**: the schema uses **Postgres-specific types** (`BYTEA`, `TIMESTAMPTZ`) so it
  **cannot silently run on SQLite**. The **CI check** that no SQLite URL is configured is a
  **`quality-gates`/CI** concern (referenced, not owned here).
- **Why**: dialect drift could break decision replay/versioning — the exact risk DATA-5 forbids.

### BR-DB-7 — Co-location (ATOMIC-1): one database, one schema, one transaction
- **Condition**: `audit_record` and `applicant_profile_snapshot` live in **one PostgreSQL database and
  one schema namespace**, reachable on **a single connection**. They are **never split across separate
  databases/services**.
- **Why**: audit-store's ATOMIC-1 both-or-neither commit is a **single `engine.begin()` ACID
  transaction**; it is only valid if both tables are co-located on one connection. This rule is the
  `database`-unit satisfaction of the tracked ATOMIC-1 cross-unit constraint.

---

## 4. Seam + consumer-scope rules

### BR-DB-8 — OOS-7: `status = active` only in Phase 1/2
- **Condition**: `audit_record.status` ∈ {`active`, `superseded`}; **Phase 1/2 writes `active` only**;
  `supersedes_decision_id` is **always null** in Phase 1/2. The supersession **write path is not built**
  (documented OOS-7); the columns exist so a Phase-3 append-only amendment slots in **without migrating
  existing rows**.
- **`status` default**: `status` is **NOT NULL** and the **application always writes it** explicitly
  (the built repository sets `record.status.value`). A DB-level **`DEFAULT 'active'` is optional
  belt-and-suspenders** and is **explicitly not something the built code relies on** (fold #2).

### BR-DB-11 — `underwriter_id` is a logical reference, not a DB FK (Phase 1)
- **Condition**: `audit_record.underwriter_id` references `app_user.user_id` **logically** but is
  **NOT a database-enforced foreign key** in Phase 1.
- **Why**: matches the built repository (plain `String`, no FK); avoids coupling audit-store's insert
  path to `app_user` row existence, which would break audit-store's integration tests (they create
  audit rows with underwriter ids that need not pre-exist in `app_user`). A DB FK, if ever wanted, is a
  Phase-later forward-only migration decision, co-designed with `auth-rbac`.

### BR-DB-12 — `app_user.role` is open, not a closed enum (fold #1)
- **Condition**: `app_user.role` is an **open `VARCHAR` dimension**. Phase-1 known values are
  `underwriter` and `auditor` (the SEC-4 distinction the built commit-gate re-check relies on). The
  column is **not a closed 2-value enum** — further roles (e.g. `admin` for `admin-cli`, a future
  senior-underwriter escalation role) can be added **without a breaking migration**.
- **Ownership**: `auth-rbac`'s own FD **owns closing or extending** the role set + the rest of the
  user/role model. `database` provides only the substrate + the migration slot (reference-not-own, in
  reverse). No auth-rbac business-logic decision is made here.

### BR-DB-13 — SEC-3: no secrets in the schema
- **Condition**: **no credentials, passwords, or connection strings** appear anywhere in this unit's
  schema or FD artifacts. Database usernames/passwords/URLs are owned by **`secrets-config`** (env /
  secrets) and wired at **Infrastructure Design**.

### BR-DB-14 — Rulebook-version registry deferred (Q2)
- **Condition**: **no `rulebook_version` table** is defined in Phase 1. Rulebook versioning is
  file-based content-hashed YAML (as built). A published-version registry is a **reserved forward-only
  migration slot**, authored by `admin-cli` later — **no columns pinned now**.

---

## 5. Replay byte-fidelity rule

### BR-DB-10 — Opaque CANON-SER storage (no normalization)
- **Condition**: `rule_results` and `profile_canonical` are stored as **`BYTEA`, byte-for-byte as
  produced by the shared CANON-SER**. The schema **does not parse, normalize, re-encode, or add
  first-class columns** for their contents. **`JSONB` is not used** for these columns.
- **Why**: replay compares canonically-serialized bytes; a DB-side transform (key re-ordering, number
  re-encoding) could produce a **false byte-mismatch**, breaking audit-store's **REPLAY-1** and
  rules-engine's **DET-2** determinism. `content_hash` stays a plain verifiable `VARCHAR` alongside.

---

## 6. Rule index

| Rule | Condition summary | Traces |
|---|---|---|
| BR-DB-1 | PKs on all three tables | audit-store record; schema authority |
| BR-DB-2 | snapshot.decision_id FK → audit_record | ATOMIC-1 co-location |
| BR-DB-3 | NOT-NULL set / nullability as verified | TUPLE-1; built repo |
| BR-DB-4 | append-only, no UPDATE/DELETE (service + role) | CON-AUDIT-1; APPEND-1; SEC-5 |
| BR-DB-5 | audit_writer INSERT+SELECT / audit_reader SELECT-only | SEC-4; APPEND-1/READ-1 |
| BR-DB-6 | PostgreSQL only, no SQLite, per-tier | DATA-5 |
| BR-DB-7 | one DB/schema/transaction co-location | ATOMIC-1 |
| BR-DB-8 | status=active only P1/2; DB default optional | OOS-7; fold #2 |
| BR-DB-9 | action/status varchar, not native ENUM | built repo; fold #3 |
| BR-DB-10 | opaque BYTEA CANON-SER, no JSONB | REPLAY-1; DET-2 |
| BR-DB-11 | underwriter_id logical ref, not DB FK (P1) | built repo; no coupling |
| BR-DB-12 | app_user.role open, not closed enum | auth-rbac; fold #1 |
| BR-DB-13 | no secrets in schema | SEC-3 |
| BR-DB-14 | rulebook-version registry deferred | Q2; admin-cli |

---

## 7. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (schema unit)** | No untrusted input parsed here; the schema stores already-validated `ApplicantProfile`/`RuleResultReport` as opaque bytes. Validation lives in intake/rules-engine. |
| Prompt-injection defense | **N/A** | No LLM/prompt path in this unit. |
| Secrets management | **Compliant** | BR-DB-13 — no credentials in schema; owned by `secrets-config`. |
| Read-only DB access for audit role | **Compliant** | BR-DB-5 — `audit_reader` SELECT-only; `audit_writer` INSERT+SELECT (no UPDATE/DELETE). |
| Audit logging | **Compliant** | BR-DB-4 append-only substrate underpins the CON-AUDIT-1 audit trail. |

No blocking finding.
