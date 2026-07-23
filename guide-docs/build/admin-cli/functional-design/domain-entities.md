# Domain Entities — `admin-cli` (U17)

**Stage**: BUILD → Functional Design (per-unit) · out-of-band admin CLI · **Depth**: LIGHTER overall + FULL rigor on the two invariant-bearing mutations
**Unit**: U17 `admin-cli` · **Date**: 2026-07-08 · Stories **US-ADMIN-1/2** · PER-3/6, FR-RULES-6.
**Scope**: A CLI-wiring unit's "entities" are its **module inventory** (the argparse entrypoint + three subcommand handlers + the two mutation surfaces), the **consumed frozen shapes** it wraps, the **injected `Engine` seam**, and the **reserved (not authored) P2 provider-config seam**. admin-cli **wraps** invariant-bearing surfaces; it re-implements **no** rulebook validation, defines **no** `Role`, and adds **no** schema/CHECK.

Built exactly on the **five locked FD-plan answers (A/A/B/A/A)** and the **three ADMIN-Folds** in
`guide-docs/build/plans/admin-cli-functional-design-plan.md` — re-opening none.

---

## 1. Module inventory (the CLI entrypoint + subcommand handlers + mutation surfaces)

`admin-cli` lives at **`backend/admin_cli/`** (Q4-A — realized per-unit convention; supersedes the older `unit-of-work.md` tree's `backend/cli/`). It is an **out-of-band argparse CLI** (`python -m backend.admin_cli <subcommand>`) — **no admin UI, no LLM, no rule evaluation, no recommendation/commit**.

| Module | Kind | Responsibility | Trace |
|---|---|---|---|
| **`__main__` / entrypoint** | arg dispatch | argparse root; routes `<subcommand>` to a handler; injects the `Engine` / rulebook-dir from the composition root; maps handler errors to a non-zero exit + a human message (no secret VALUE) | US-ADMIN-1/2 |
| **`publish_rulebook` handler** | mutation (FULL) | write a new `{version}.yaml`, **validate by load** (`build_rulebook`/`RulebookLoader`), **refuse overwrite**, declared-version == target | FR-RULES-6 |
| **`create_user` handler** | mutation (FULL gate) | validate `role` against canonical `Role`, then INSERT `app_user(user_id, subject, role)`; explicit "already exists" error | PER-3 |
| **`set_role` handler** | mutation (FULL gate) | validate `role` against canonical `Role`, then UPDATE `app_user.role WHERE user_id`; explicit "no such user" error | PER-3 |
| **`RulebookPublisher`** | publish surface | owns the write-then-validate-then-append-only publish logic (delegating validation to `build_rulebook`) | FR-RULES-6 |
| **`AppUserWriter`** | write surface | owns the parameterized `app_user` INSERT/UPDATE via the **injected `sqlalchemy.Engine`** (reference-not-own of database's schema) | PER-3 |

---

## 2. Consumed frozen shapes (reference-not-own — call-only, none edited)

| Consumed surface | From unit | Used for | Answer / Fold |
|---|---|---|---|
| `rules_engine.loader.build_rulebook(data) -> Rulebook` / `RulebookLoader.load_rulebook(version)` | `rules-engine` | the **sole** publish-validation (Pydantic load-gate: allowlist + threshold shapes + recompute/stamp `content_hash` + declared-hash tamper-verify + file-version==filename) | Q2, ADMIN-Fold-2 |
| `auth_rbac.roles.Role` (+ its `.value` set) | `auth-rbac` | the **canonical role set** the write is validated against **before** persisting (single-sourced; auto-agrees if the enum extends) | Q1/Q5, ADMIN-Fold-1 |
| `database` `app_user` columns (`user_id` PK, `subject` UNIQUE, `role` **open VARCHAR, NO CHECK**) | `database` | the write target — parameterized INSERT/UPDATE; admin-cli adds **no** schema/CHECK (BR-DB-12 referenced) | Q1/Q5, ADMIN-Fold-1 |
| `secrets-config` `DATABASE_URL` (**indirect**) | `secrets-config` | the composition root builds the injected `Engine`; admin-cli reads **no** secret VALUE (SEC-3) | Q1 |

> **Reference-not-own (binding).** admin-cli **imports/calls** `build_rulebook`/`RulebookLoader` and `Role`; it re-implements **no** rulebook validation/schema/hashing, defines **no** `Role`, owns **no** `app_user` schema/CHECK, and imports **no** `database`/`auth_rbac` *production write* module (it takes an injected `Engine` + parameterized SQL, mirroring auth-rbac's `pg_repository.py` read posture). It edits **none** of the four surfaces.

---

## 3. The injected-`Engine` seam (mirrors auth-rbac's `pg_repository.py`)

| Aspect | Shape |
|---|---|
| Construction | `AppUserWriter(engine: sqlalchemy.Engine)` — the `Engine` is **injected** by the composition root (built from `secrets-config`'s `DATABASE_URL`); no connection string / credential VALUE appears in admin-cli (SEC-3). |
| Write — create | parameterized `INSERT INTO app_user (user_id, subject, role) VALUES (:user_id, :subject, :role)` (after the `Role` gate) |
| Write — set-role | parameterized `UPDATE app_user SET role = :role WHERE user_id = :user_id` (after the `Role` gate) |
| Ownership | admin-cli **owns the write operation**; `database` owns the **schema** (no CHECK added — BR-DB-12); admin-cli asserts no schema/FIDELITY of its own (that is database's concern). |

---

## 4. The RulebookPublisher surface (validate-then-append-only — Q2 / ADMIN-Fold-2)

| Step | Shape |
|---|---|
| Write candidate | write the source as `{version}.yaml` (with `content_hash: ""` so the loader **recomputes + stamps**) into the rulebook dir |
| Validate by load | `build_rulebook(data)` / `RulebookLoader.load_rulebook(version)` — the **sole** validator (schema + hash); a validation failure leaves **no** published file |
| Append-only | **refuse to overwrite** an existing `{version}.yaml` (a published version is never mutated); reject if the file's declared `rulebook_version` ≠ `<version>` |

---

## 5. Reserved (NOT authored) P2 provider-config seam (ADMIN-Fold-3)

Per **Q3-B**, provider-config **management is deferred to Phase-2** — **named here, not built**:
- Phase-1 admin-cli scopes to **rulebook-publish + user/role only**; there is **no `set-provider` subcommand** and **no config store**.
- The **active provider** (gemini/claude/ollama, FR-PROV-1/2) stays a **static composition-root value** (env/config read at startup, not CLI-mutated). A future P2 unit may add a provider-config store + a `set-provider` command; **no frozen surface defines one yet**, so inventing it now would be scope creep. This seam is a **placeholder note**, contributing no Phase-1 module.

---

## 6. Boundary — what `admin-cli` does NOT own
- **No rulebook validation/schema/hash re-implementation** — `build_rulebook` is the sole validator (reference-not-own).
- **No `Role` definition** — validates against auth-rbac's `Role` (imported call-only); the canonical set is single-sourced.
- **No `app_user` schema or DB CHECK** — database owns the schema; `role` stays open VARCHAR (BR-DB-12); admin-cli owns only the **write**, gated by its own `Role` validation (§4.1 of the plan / ADMIN-Fold-1).
- **No secret VALUE** read or printed (SEC-3); the `Engine`/URL is injected.
- **No provider-config management in Phase 1** (deferred to P2).
- **No LLM; no rule evaluation; no recommendation/decision/commit; no admin UI. WIRE-1 untouched; tier-B NOT authorized.**
