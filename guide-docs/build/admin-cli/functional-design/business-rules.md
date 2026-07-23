# Business Rules — `admin-cli` (U17)

**Stage**: BUILD → Functional Design (per-unit) · out-of-band admin CLI · **Depth**: LIGHTER overall + FULL rigor on the two invariant-bearing mutations
**Unit**: U17 `admin-cli` · **Date**: 2026-07-08 · Stories **US-ADMIN-1/2** · PER-3/6, FR-RULES-6.
**Scope**: The **enforceable rules** the CLI's operations obey. Each states its **condition** and, where checkable, names the **mechanism** (landing at NFR / Code-Gen). **Management wrapper only** — admin-cli re-implements no rulebook validation, defines no `Role`, adds no schema/CHECK. Built exactly on the five locked answers (A/A/B/A/A) + the three ADMIN-Folds — re-opening none.

---

## 1. Rulebook publish (FR-RULES-6 — FULL rigor)

### BR-ADMIN-1 — Publish = write new `{version}.yaml`, validate-by-load, append-only (US-ADMIN-1)
- **Condition**: `publish-rulebook <version> <source>` writes the source as `{version}.yaml` (with `content_hash: ""` so the loader recomputes + stamps), **validates it by loading** via `build_rulebook`/`RulebookLoader`, **refuses to overwrite** an existing `{version}.yaml` (append-only immutability — a published version is never mutated), and requires the file's declared `rulebook_version` to equal `<version>`. A validation failure publishes **nothing**.
- **Why**: FR-RULES-6 + the rulebook versioning/replay invariant (CON-DET-1) — a published version must be immutable + replayable at its exact bytes.
- **Checkable**: publishing a valid new version succeeds + the file loads; re-publishing an existing version is **rejected** (no overwrite); a schema-invalid source is **rejected by `build_rulebook`** with no file left; a declared-version ≠ filename is rejected.

### BR-ADMIN-2 — Publish validation is reference-not-own (`build_rulebook` sole validator)
- **Condition**: admin-cli delegates **all** rulebook validation to `build_rulebook`/`RulebookLoader`; it re-implements **no** local rule schema, allowlist, threshold-shape check, or hasher.
- **Why**: single-sourced validation — no drift between what admin-cli accepts and what the engine loads.
- **Checkable**: a structural check finds no local rulebook-schema/hash logic in `backend/admin_cli/`; the publish path imports + calls `build_rulebook`.

---

## 2. User / role management (PER-3 — FULL rigor on the role gate)

### BR-ADMIN-3 — Create-user: INSERT with required `subject`; explicit already-exists error (US-ADMIN-2)
- **Condition**: `create-user <user_id> <subject> <role>` INSERTs `app_user(user_id, subject, role)`; `subject` is **required** (schema UNIQUE / OIDC seam); a duplicate `user_id` or `subject` yields an **explicit "already exists" error** (not a silent upsert).
- **Why**: PER-3 user provisioning; the UNIQUE constraints (PK `user_id`, UNIQUE `subject`) are respected with a clear operator-facing error.
- **Checkable**: inserting a new user succeeds; a duplicate `user_id`/`subject` raises the explicit error (surfaced by the DB UNIQUE violation, reported as "already exists").

### BR-ADMIN-4 — Set-role: UPDATE with explicit no-such-user error
- **Condition**: `set-role <user_id> <role>` UPDATEs `app_user.role WHERE user_id`; if **no** row matches, it yields an **explicit "no such user" error** (0 rows affected → error, not a silent no-op).
- **Why**: PER-3 role management; a set-role against a missing user must fail loudly.
- **Checkable**: set-role on an existing user changes the role; set-role on an absent user raises the explicit error.

### BR-ADMIN-5 — Canonical-role SOLE gate (SEC-4 — FULL rigor)
- **Condition**: **before** any `app_user` write (create-user or set-role), `role` is validated against auth-rbac's canonical `Role` (imported call-only). A role **not** in `Role`'s value set is **rejected with an explicit error BEFORE the INSERT/UPDATE**. Because `app_user.role` is an **open VARCHAR with NO DB CHECK** (BR-DB-12), the database will **not** reject a non-canonical role — **admin-cli's validation is the SOLE gate** (ADMIN-Fold-1). No reliance on a DB constraint; no dependence on `to_role`'s later fail-close (which would only silently lock the user out at auth time).
- **Why**: SEC-4 authorization integrity — a persisted non-canonical role is a latent lockout / policy hole; the only structural prevention is admin-cli's pre-write check.
- **Checkable**: writing a canonical role (`underwriter`/`auditor`/`admin`) succeeds; a non-canonical role (`superuser`, `Admin`, blank) is **rejected before** any SQL runs; a fault-injection test confirms the DB itself does **not** reject it (proving admin-cli is the sole gate).

---

## 3. Reference-not-own · secrets · substrate

### BR-ADMIN-6 — `app_user` write reference-not-own
- **Condition**: the write is parameterized SQL via an **injected `sqlalchemy.Engine`**; admin-cli imports **no** `database`/`auth_rbac` production module, adds **no** schema/CHECK, and asserts no schema/FIDELITY of its own (that is `database`'s concern).
- **Why**: mirrors auth-rbac's `pg_repository.py` posture; database owns the schema, admin-cli owns only the operation.
- **Checkable**: a structural scan finds no `database`/`auth_rbac` production import and no local DDL/CHECK in `backend/admin_cli/`.

### BR-ADMIN-7 — No secret VALUES (SEC-3)
- **Condition**: admin-cli reads / prints **no** credential VALUE; the DB `Engine`/URL is injected (secrets-config's); command output is status / names only.
- **Why**: SEC-3 single-source secrets — the CLI must never echo a URL/password/key.
- **Checkable**: outputs contain no secret VALUE; the settings/URL are never printed; a structural check finds no secret literal.

### BR-ADMIN-8 — CLI only; no LLM / no rule-eval / no decision path
- **Condition**: admin-cli is an **argparse CLI** (out-of-band); it runs **no LLM**, evaluates **no rule**, produces **no recommendation/decision**, reaches **no commit path**, and ships **no admin UI**.
- **Why**: scope boundary — it manages configuration, it does not underwrite.
- **Checkable**: no LLM client / no rule-evaluation / no commit-service import in `backend/admin_cli/`.

### BR-ADMIN-9 — Provider-config management deferred to P2 (Q3-B)
- **Condition**: Phase-1 admin-cli exposes **only** `publish-rulebook` + `create-user` + `set-role`; there is **no** `set-provider` command and **no** config store. The active provider is a static composition-root value.
- **Why**: no frozen surface defines a mutable provider store; inventing one now is scope creep (ADMIN-Fold-3).
- **Checkable**: no provider-config store/command exists in `backend/admin_cli/`; the reserved seam is a documented note only.

---

## 4. Rule index

| Rule | Condition summary | Trace | Rigor |
|---|---|---|---|
| BR-ADMIN-1 | publish = write `{version}.yaml` + validate-by-load + append-only refuse-overwrite + version==filename | FR-RULES-6, CON-DET-1, US-ADMIN-1 | FULL |
| BR-ADMIN-2 | `build_rulebook` is the sole validator; no local rulebook schema/hash | FR-RULES-6 | FULL |
| BR-ADMIN-3 | create-user INSERT; `subject` required; explicit already-exists error | PER-3, US-ADMIN-2 | standard |
| BR-ADMIN-4 | set-role UPDATE; explicit no-such-user error | PER-3, US-ADMIN-2 | standard |
| BR-ADMIN-5 | canonical-role SOLE gate before any write; DB open-VARCHAR is not a gate | SEC-4, BR-DB-12 (ref) | FULL |
| BR-ADMIN-6 | `app_user` write reference-not-own; injected Engine; no schema/CHECK | reference-not-own | standard |
| BR-ADMIN-7 | no secret VALUES; injected Engine/URL; status-only output | SEC-3 | FULL |
| BR-ADMIN-8 | CLI only; no LLM / rule-eval / decision path / admin UI | scope | standard |
| BR-ADMIN-9 | provider-config management deferred to P2; no store/command | Q3-B, ADMIN-Fold-3 | standard |

---

## 5. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **Compliant (owns it)** | `role` validated against canonical `Role` (BR-ADMIN-5); `<version>` validated by `build_rulebook` (declared-version + schema); `user_id`/`subject` are parameterized (no injection) and respect the schema's PK/UNIQUE. |
| Prompt-injection defense | **N/A** | No LLM is invoked; no untrusted document is parsed. |
| Secrets management | **Compliant (owns it)** | **BR-ADMIN-7 / SEC-3** — no secret VALUE read or printed; the DB `Engine`/URL is injected (secrets-config's). |
| Read-only DB access for audit role | **N/A** | admin-cli writes `app_user` (via its own injected engine) + rulebook files; it does not touch the audit read/write roles (SEC-5 is `audit-store`'s). |
| Audit logging | **N/A** | admin-cli is out-of-band config management, not the runtime decision audit trail. |
| **Canonical-role authorization gate** | **Compliant (owns it)** | **BR-ADMIN-5 / SEC-4** — a non-canonical role is rejected **before** persistence; the open-VARCHAR DB is not a gate (BR-DB-12). |

No blocking finding.
