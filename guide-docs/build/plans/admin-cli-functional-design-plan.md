# Functional Design Plan (Part 1) — `admin-cli` (U17)

**Phase / Stage**: BUILD → Functional Design, **Part 1 (Planning)** (plan-then-generate; Q1–Q5 answered, embedded §7)
**Loop position**: `admin-cli` (U17) — the **eleventh unit to enter the per-unit loop**; the sole genuinely-ready P1 leaf (deps rules-engine ✓ · auth-rbac ✓ · database ✓ · secrets-config ✓ all built; no WIRE-1 dependency). FD ← here.
**Unit**: U17 `admin-cli` · **Date**: 2026-07-08 · **Depth**: **LIGHTER overall (CLI wiring) WITH FULL rigor on the two invariant-bearing mutation operations** (user-confirmed) · Stories **US-ADMIN-1/2** · PER-3/6, FR-RULES-6.
**Status**: **Plan — Q1–Q5 answered (A/A/B/A/A); ambiguity-check CLEAN (§8, three ADMIN-Folds). NO FD artifact generated** (Part 2 generates the three FD artifacts on explicit go). STOP after this plan.

Built **ON** the frozen contracts (re-read, not re-derived): **rules-engine** (`RulebookLoader.load_rulebook(version)` immutable/cached/append-only `{version}.yaml`; `build_rulebook(data)` the single Pydantic `Rulebook` load-gate — allowlist + threshold shapes + recompute/stamp `content_hash` + declared-hash tamper-verify + file-declared version must equal filename; dir holds `1.0.0` + `1.1.0`); **auth-rbac** (`Role` {underwriter, auditor, admin}; `PERMISSION_MATRIX` admin→{manage_users, manage_config}; `to_role` fail-closed canonicalizer; `UserRoleRepository` Protocol **READ-ONLY** `get_role` — **no write path exists in any frozen unit**); **database** (`app_user` {user_id PK, subject UNIQUE OIDC-seam, role **OPEN VARCHAR, NO CHECK** per BR-DB-12}); **secrets-config** (`Settings` 6 required env fields + `get_settings()`; env-sourced, immutable-at-construction, `extra="ignore"`, **no provider-selection field, no mutation API**) — **re-opening none.**

---

## 1. Scope / owns / builds-ON / boundary

- **Owns** (unit-of-work.md §U17): an **out-of-band admin CLI** (no admin UI) with three Phase-1 subcommands — **`publish-rulebook`** (FR-RULES-6), **`create-user`** + **`set-role`** (PER-3, user/role management). **Full rigor** on the two invariant-bearing mutations; lighter on the CLI scaffolding (argparse dispatch, output).
- **Builds ON** (call-only / reference-not-own): rules-engine `build_rulebook`/`RulebookLoader` (publish validation); auth-rbac `Role` (canonical-role validation, imported call-only); database `app_user` schema (parameterized write via an **injected `sqlalchemy.Engine`** — mirroring auth-rbac's `pg_repository.py` read pattern); secrets-config `DATABASE_URL` (consumed **indirectly** — the composition root builds the injected engine; admin-cli reads no secret VALUE, SEC-3).
- **Boundary — thin wrapper over invariant-bearing surfaces, owns neither invariant's definition:**
  - Does **not** re-implement rulebook validation / schema / hashing — `build_rulebook` is the **sole** validator (reference-not-own).
  - Does **not** add a DB CHECK or edit `app_user`'s schema (database owns the schema; BR-DB-12 keeps `role` open); admin-cli owns only the **write operation**.
  - Does **not** define `Role` — validates against auth-rbac's `Role` (imported call-only, single-sourced; auto-agrees if the enum extends).
  - Does **not** manage provider-config in Phase 1 (Q3-B — deferred to P2); Phase-1 scope = rulebook-publish + user/role only.
  - Does **not** run an LLM, evaluate a rule, produce a recommendation, or reach the commit/decision path. No admin UI.

---

## 2. Dependency ledger (call-only / reference-not-own — none edited)

| Consumed surface | From unit | Used for |
|---|---|---|
| `rules_engine.loader.build_rulebook` / `RulebookLoader.load_rulebook` | `rules-engine` | the **sole** rulebook publish-validation (load-gate + hash stamp), call-only |
| `auth_rbac.roles.Role` (+ `.value` set) | `auth-rbac` | canonical-role validation **before** the `app_user` write (single-sourced) |
| `database` `app_user` schema (`user_id`, `subject`, `role`) | `database` | the write target — parameterized INSERT/UPDATE via an **injected `sqlalchemy.Engine`** (no `database` module import; no schema/CHECK added) |
| `secrets-config` `DATABASE_URL` (indirect) | `secrets-config` | the composition root builds the injected engine; admin-cli reads **no** secret VALUE (SEC-3) |

> **Reference-not-own (binding).** admin-cli imports/calls these surfaces and re-implements **none**; edits **none**. It owns **no** rulebook validation/hash logic and **no** `app_user` schema/CHECK. It is a **management wrapper**: `build_rulebook` validates the rulebook; auth-rbac's `Role` defines the canonical set; database owns the schema.

---

## 3. Subcommands → operation · invariant · rigor

| Subcommand | Operation | Invariant / trace | Rigor |
|---|---|---|---|
| **`publish-rulebook <version> <source>`** | write a new `{version}.yaml` into the rulebook dir; **validate by loading** via `build_rulebook`/`RulebookLoader`; **refuse to overwrite** an existing version; declared `rulebook_version` must equal `<version>` | FR-RULES-6; rulebook append-only immutability + replay (CON-DET-1) | **FULL** |
| **`create-user <user_id> <subject> <role>`** | INSERT `app_user(user_id, subject, role)`; **`role` validated against canonical `Role` first**; error if `user_id`/`subject` already exists | PER-3; SEC-4 authz surface | **FULL** (on the role gate) |
| **`set-role <user_id> <role>`** | UPDATE `app_user.role WHERE user_id`; **`role` validated against canonical `Role` first**; error if the user is absent | PER-3; SEC-4 authz surface | **FULL** (on the role gate) |

**No provider subcommand in Phase 1** (Q3-B — provider-config management deferred to P2; the active provider stays a static composition-root value).

---

## 4. The two invariant-bearing mutations (FULL rigor)

### 4.1 Canonical-role SOLE gate (the `app_user` write — SEC-4)
`app_user.role` is an **open VARCHAR with NO DB CHECK** (BR-DB-12). The database will **accept any string** — it will **not** reject a non-canonical role. Therefore **admin-cli's own pre-write validation against auth-rbac's `Role` is the SOLE gate** (ADMIN-Fold-1): a role not in `Role`'s canonical value set is **rejected with an explicit error BEFORE** the INSERT/UPDATE. There is **no** reliance on a DB constraint (none exists), and **no** dependence on `to_role`'s runtime fail-close (which would only silently lock the user out at auth time). Writing a non-canonical role is thus **structurally prevented**, not merely denied later.

### 4.2 Rulebook publish = validate-then-append-only (FR-RULES-6 / CON-DET-1)
Publishing (ADMIN-Fold-2): admin-cli writes the candidate as `{version}.yaml` (with `content_hash: ""` so the loader recomputes + stamps), then **validates by loading via `build_rulebook`/`RulebookLoader`** — the Pydantic load-gate (allowlist, threshold shapes, hash) is the sole validator. It **refuses to overwrite** an existing `{version}.yaml` (append-only immutability — a published version is never mutated), and rejects if the file's declared `rulebook_version` ≠ `<version>`. A failed validation leaves **no** published file.

---

## 5. Draft business rules (BR-ADMIN-* — finalized in Part 2, not frozen here)
- **BR-ADMIN-1** — Rulebook publish: write new `{version}.yaml`; validate-by-load (`build_rulebook`/`RulebookLoader`); append-only, **refuse overwrite**; declared version == target. **FULL.**
- **BR-ADMIN-2** — Publish validation reference-not-own: `build_rulebook` is the **sole** validator; no local rule/schema/hash re-implementation.
- **BR-ADMIN-3** — Create-user: INSERT `(user_id, subject, role)`; `subject` required (schema UNIQUE); explicit "already exists" error (not silent upsert).
- **BR-ADMIN-4** — Set-role: UPDATE `role WHERE user_id`; explicit "no such user" error if absent.
- **BR-ADMIN-5** — **Canonical-role SOLE gate**: role validated against auth-rbac `Role` (call-only) **before** any `app_user` write; non-canonical → explicit rejection; the open-VARCHAR DB is **not** a gate (BR-DB-12). **FULL.**
- **BR-ADMIN-6** — `app_user` write reference-not-own: parameterized SQL via injected `Engine`; no `database`/`auth_rbac` production import; no schema/CHECK added.
- **BR-ADMIN-7** — No secret VALUES: admin-cli reads/prints no credential value (SEC-3); the engine/URL is injected (secrets-config's); outputs are status/names only.
- **BR-ADMIN-8** — CLI only (argparse), out-of-band; no admin UI; no LLM; no rule evaluation; no recommendation/decision/commit.
- **BR-ADMIN-9** — Provider-config management **deferred to P2** (Q3-B); Phase-1 = rulebook-publish + user/role only (active provider a static composition-root value, reserved-not-authored).

---

## 6. Planned Part-2 structure (the three FD artifacts — generated on explicit go)
- **`domain-entities.md`** — the CLI module inventory (arg-dispatch entrypoint + the three subcommand handlers + the `app_user` write surface + the rulebook publisher) + consumed frozen shapes (`build_rulebook`/`RulebookLoader`, `Role`, `app_user` columns) + the injected-`Engine` seam + the reserved (P2) provider-config seam.
- **`business-rules.md`** — BR-ADMIN-1..9 finalized + rule index + the Security-Guardrails compliance table (SEC-3 no-secret-values; SEC-4 canonical-role gate; input validation on version/user_id/role).
- **`business-logic-model.md`** — the two mutation flows (publish: write→validate-by-load→append-only-commit; user write: validate-role→INSERT/UPDATE→explicit-error) with a 7-rule-validated Mermaid + text alternative, the sole-gate-vs-open-VARCHAR boundary, a consumer/dependency map, and an invariant self-check (FR-RULES-6, SEC-4 role gate, BR-DB-12 open-VARCHAR, SEC-3 no-secret-values, reference-not-own).

**Proposed package (Q4-A):** `backend/admin_cli/` (realized per-unit convention, matching `quality_gates`/`corpus_generator`/`secrets_config`; supersedes the older unit-of-work tree's `backend/cli/`) with an argparse entrypoint (`python -m backend.admin_cli <subcommand>`) + subcommand modules + the `app_user` writer + the rulebook publisher + `tests/`; folds into the root pytest run (`--cov=backend/admin_cli`). **Flagged for gate confirmation at the FD completion gate.**

---

## 7. Clarifying questions — ANSWERED (standing convention: full text + answers on disk)

**Depth confirmed: LIGHTER overall (CLI wiring) WITH FULL rigor on the two invariant-bearing mutations (app_user.role write — SEC-4; rulebook-version publish — FR-RULES-6/CON-DET-1) — the ui-shell 'lighter-except-full-rigor-on-invariant-facets' pattern.**

### Q1 — User/role WRITE surface ownership (the central gap: no write path exists in any frozen unit)
A) admin-cli **owns its own `app_user` WRITE surface** — parameterized INSERT/UPDATE via an **injected `sqlalchemy.Engine`** (mirroring auth-rbac's `pg_repository.py` read pattern: reference-not-own of database's schema, no `database`/`auth_rbac` production import, no schema/CHECK added), and **validates the role against auth-rbac's canonical `Role`** (call-only) **before** writing, so a non-canonical role can never be persisted. **Recommended.**
B) Add a write method to auth-rbac's repository (edits a frozen unit — rejected). C) Other.

[Answer]: A

### Q2 — Rulebook-version PUBLISH mechanism (FR-RULES-6)
A) admin-cli **writes a new `{version}.yaml`** into the rulebook dir and **validates it by loading via `build_rulebook`/`RulebookLoader`** (call-only — the Pydantic load-gate + hash stamp *is* the validation); **refuses to overwrite** an existing version (append-only; a published version is never mutated); the file's declared `rulebook_version` must equal the target. **Recommended.**
B) admin-cli re-implements rulebook validation locally (rejected — reference-not-own). C) Other.

[Answer]: A

### Q3 — Provider-config management LOCATION (genuine gap — nothing frozen defines a mutable active-provider store)
A) Manage the non-secret active-provider selection as an admin-cli-owned config record (a small DB-backed config table, or a committed non-secret config file); secrets stay env-only.
B) **Defer provider-config *management* to Phase-2**; Phase-1 admin-cli scopes to **rulebook-publish + user/role only** (the active provider stays a static env/config value read by the composition root, not CLI-mutated). **Recommended — smallest honest Phase-1 surface; invents no new store.**
C) Other.

[Answer]: B

### Q4 — CLI substrate + package location
A) stdlib **`argparse`** (no new dependency), Python 3.12, invoked `python -m backend.admin_cli <subcommand>`; package **`backend/admin_cli/`** (realized per-unit convention; supersedes the tree's `backend/cli/`); folds into the root pytest run (`--cov=backend/admin_cli`). **Recommended.**
B) A new dependency (click/typer) / the tree's `backend/cli/`. C) Other.

[Answer]: A

### Q5 — `app_user` write semantics
A) Two operations — **create-user** (INSERT `user_id` + `subject` + `role`; `subject` required by the schema's UNIQUE/OIDC seam) and **set-role** (UPDATE `role WHERE user_id`, error if the user is absent); role validated against `Role` first; **explicit "already exists" / "no such user" errors** (not silent upsert). **Recommended.**
B) A single upsert (INSERT … ON CONFLICT). C) Other.

[Answer]: A

---

## 8. Ambiguity-check result — CLEAN (three realization ADMIN-Folds; no genuine gap, no STOP)

Ran against the five answers + the frozen contracts (rules-engine `build_rulebook`/`RulebookLoader`; auth-rbac `Role`/`PERMISSION_MATRIX`/`to_role`/READ-ONLY `UserRoleRepository`; database `app_user` open-VARCHAR schema; secrets-config `Settings`), grounded on disk. **No genuine gap** — no user-facing decision the contracts + answers don't determine. Three determinate realizations (none re-opens a frozen artifact):

- **ADMIN-Fold-1 (Q1/Q5 — the named check) — admin-cli's role validation is the SOLE gate.** `app_user.role` is an **open VARCHAR with NO CHECK** (BR-DB-12, verified `0001_initial_schema.sql:54`), so the DB **accepts any string** — it will **not** reject a non-canonical role. admin-cli therefore **must** reject a role ∉ `Role` with an **explicit error BEFORE** the INSERT/UPDATE; there is **no** false reliance on a DB constraint, and **no** dependence on `to_role`'s later fail-close (which would only silently lock the user out at auth time). Confirmed: admin-cli's pre-write validation is the one structural gate.
- **ADMIN-Fold-2 (Q2) — publish = validate-by-load + append-only.** admin-cli writes `{version}.yaml` (`content_hash: ""` → loader recomputes/stamps), validates via `build_rulebook`/`RulebookLoader` (the sole validator), **refuses to overwrite** an existing version (append-only immutability), and rejects a declared-version ≠ filename mismatch. A failed validation publishes nothing.
- **ADMIN-Fold-3 (Q3) — provider-config deferred, no store invented.** Phase-1 admin-cli = rulebook-publish + user/role only; provider selection stays a static composition-root value (reserved-not-authored seam); inventing a config store now would be scope creep, not design.

---

## 9. Holds (binding through FD)
- **Reference-not-own** — the four surfaces call-only, none edited; `build_rulebook` is the sole rulebook validator; `Role` is the sole canonical set; database owns the `app_user` schema (no CHECK added).
- **Canonical-role sole gate** — the open-VARCHAR DB is not a gate; admin-cli validates before writing (SEC-4).
- **SEC-3** — no secret VALUE read or printed; the DB engine/URL is injected (secrets-config's).
- **Provider-config management deferred to P2**; Phase-1 = rulebook-publish + user/role only.
- **No LLM; no rule evaluation; no recommendation/decision/commit; no admin UI. WIRE-1 untouched; tier-B NOT authorized; no other unit started; no FD artifact generated at this plan stage.**

## 10. Next step (STOP here)
Review this plan file. On your go I run **Part 2** — generate the three FD artifacts (`guide-docs/build/admin-cli/functional-design/{domain-entities,business-rules,business-logic-model}.md`) built exactly on the five answers + three ADMIN-Folds (re-opening none), then present the standardized FD 2-option completion gate. **No FD artifact is generated until you approve this plan.** WIRE-1 stays untouched; tier-B not authorized; no other unit started.
