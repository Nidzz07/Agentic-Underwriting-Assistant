# Business Rules — `auth-rbac` (EPIC-6 / U11)

**Stage**: BUILD → Functional Design (per-unit) · invariant-bearing platform unit
**Unit**: U11 `auth-rbac`
**Date**: 2026-07-06
**Scope**: The **role/permission governance rules** auth-rbac enforces. Each rule states its **condition
explicitly**. These reconcile against — and **do not re-open** — audit-store's built `Authorizer`
Protocol and `database`'s `app_user` schema. **No credentials** appear here (SEC-3). **No LLM.**

---

## 1. Role model rules

### BR-AUTH-1 — Role set closed at the APP layer; DB column stays open (BR-DB-12 reconciled)
- **Condition**: the canonical `Role` set is **exactly `{underwriter, auditor, admin}`** in Phase 1,
  closed as an **application-layer domain enum** owned by `auth-rbac`. The `database` `app_user.role`
  column **remains an open `VARCHAR` with NO CHECK constraint** — auth-rbac **does not** add a DB CHECK
  and **does not** edit `database`'s migration.
- **Why**: BR-DB-12 hands auth-rbac the ownership of closing/extending the role set, while keeping the
  DB column open so a new role is a **forward-only, non-breaking** app-layer extension (no migration).
  The open DB column and the closed app enum coexist because any out-of-set value **fail-closes** at the
  app layer (BR-AUTH-3) — a DB CHECK is therefore unnecessary **and** would violate reference-not-own.

### BR-AUTH-2 — The role→permission matrix (the authorization policy)
- **Condition**: authorization is decided by a **role→allowed-`rbac_action` matrix** (data, not code
  branches):
  - `underwriter` → `{commit, view_queue, view_memo, read_audit}`
  - `auditor` → `{view_queue, view_memo, read_audit}` (**no `commit`**)
  - `admin` → `{manage_users, manage_config}`
- **Rule**: `authorize(user_id, rbac_action)` returns `True` **iff** the user's resolved `Role` is in the
  canonical set **and** `rbac_action ∈ matrix[Role]`; otherwise `False`.
- **Why**: a data-driven matrix keeps the policy in **one place** (single source of truth, BR-AUTH-6),
  extensible without new code branches.

### BR-AUTH-11 — `rbac_action` is the RBAC operation, never `CommittedDecision.action`
- **Condition**: an `rbac_action` (e.g. `commit`, `read_audit`) is the **RBAC OPERATION** being
  authorized. It is **distinct from `CommittedDecision.action`** (`approve`/`override`) and the two are
  **never conflated** — mirroring the built seam docstring.
- **Why**: audit-store's re-check passes `RBAC_COMMIT = "commit"` as the `rbac_action`; the human's
  approve/override choice is a separate concept persisted in the audit record.

---

## 2. Deny-by-default / fail-closed (fold #1 — all three cases)

### BR-AUTH-3 — Deny-by-default: authorize returns False unless an explicit allow is proven
- **Condition**: `authorize(user_id, rbac_action)` returns `False` (deny) in **every** case below —
  only an affirmative match returns `True`:
  1. **Unknown `user_id`** — no matching `app_user` row for `user_id` → **`False`**.
  2. **Role not in the Phase-1 canonical set** — the row's `role` value is not one of
     `{underwriter, auditor, admin}` → **`False`** (an unrecognized or future-but-not-yet-canonical role
     is denied, never silently allowed).
  3. **Null / blank role** — a null or empty/whitespace `role` → **`False`**. *(Note: `database`'s
     `app_user.role` is `NOT NULL` per the built `0001_initial_schema.sql`, so a DB-null is
     **structurally prevented at the DB layer**; auth-rbac **still** treats null/blank as deny at the
     app layer for completeness and defense in depth.)*
- Additionally, a **`rbac_action` not in the resolved role's allowed set** → **`False`** (BR-AUTH-2).
- **Why**: SEC-4 is a fail-closed guarantee — the absence of an explicit permission is a denial, never a
  default-allow. A read-only auditor, an unknown user, and a mis-provisioned role are all denied `commit`.

---

## 3. SEC-4 segregation rules

### BR-AUTH-4 — Commit requires the underwriter `commit` permission (satisfies the built re-check)
- **Condition**: reaching the human-approval-gate commit boundary requires `authorize(user_id,
  "commit")` to be `True`, which holds **only** for a user whose role is `underwriter` (the only role
  granted `commit` in the matrix). audit-store's built `DecisionCommitService` already enforces this:
  `if not self._authorizer.authorize(underwriter_id, RBAC_COMMIT): raise UnauthorizedCommit(...)`.
- **Why**: CON-BR4 / human-in-the-loop — only an authorized underwriter can turn a recommendation into a
  committed decision. auth-rbac supplies the real `Authorizer`; the enforcement site is audit-store's
  (unedited).

### BR-AUTH-5 — Auditor is read-only (aligned with, but distinct from, the DB `audit_reader` role)
- **Condition**: the `auditor` role's allowed set contains **only read operations** (`view_queue`,
  `view_memo`, `read_audit`) and **never `commit`**. This app-level read-only role is the **counterpart**
  of `database`'s DB-level `audit_reader` (SELECT-only) grant — **two layers of the same SEC-4
  segregation** (app-role check + DB-role enforcement). auth-rbac pins the **app-role** semantics only;
  it **does not** re-open or execute `database`'s `audit_reader` grant (reference-not-own).
- **Why**: defense in depth — even if the app check were bypassed, the DB `audit_reader` grant still
  blocks writes; even if a reader connection were mis-wired, the app role still blocks `commit`.

### BR-AUTH-6 — Two backend enforcement points, one policy
- **Condition**: authorization is enforced at **two backend points** — (i) the **API-layer guard**
  (blocks an unauthorized request before it reaches the service) and (ii) the **built commit re-check**
  inside `DecisionCommitService`. **Both call the same `AuthRBAC.authorize`** — there is exactly **one**
  authorization policy (BR-AUTH-2); the API guard is a second enforcement *point*, not a second policy
  implementation (see `business-logic-model.md §3`). The **UI-side** RBAC is a thin consuming facet in
  the C5 units (Q1=A) — not a backend enforcement point, not designed here.
- **Why**: defense in depth (a read-only auditor is structurally unable to reach commit) **without**
  policy divergence.

---

## 4. Reconciliation + boundary rules

### BR-AUTH-7 — Authorizer-Protocol conformance (reconcile, do not edit)
- **Condition**: `AuthRBAC.authorize` **structurally conforms** to audit-store's built, frozen Protocol:
  ```python
  RBAC_COMMIT = "commit"
  @runtime_checkable
  class Authorizer(Protocol):
      def authorize(self, user_id: str, rbac_action: str) -> bool: ...
  ```
  auth-rbac provides an instance satisfying this and is **injected at the composition root**. **No
  audit-store file (`seams.py` / `commit_service.py`) is edited.** The DISCOVER-level `authorize(user,
  action)` sketch is reconciled to the built signature (the built signature is authoritative).
- **Why**: audit-store already codes against this Protocol; conformance is what lets the real impl drop
  in at the composition root with no change to the consumer (reference-not-own).

### BR-AUTH-8 — No demographics in the authorization path (CON-BR1)
- **Condition**: an authorization result is a function of **only** `user_id → role → rbac_action`. **No
  demographic identifier** (name, gender, city, etc.) ever enters the authz decision, feature, or log.
- **Why**: CON-BR1 / bias-free — access control operates on identity + role, never on demographics.

### BR-AUTH-9 — Phase-1 DB-role decision: app-level roles only (Q7-A; B's forward-only path stays open)
- **Condition**: in Phase 1 **no dedicated auth-rbac PostgreSQL DB role** is provisioned.
  `app_user.role` values are **application-level data**, distinct from Postgres DB roles; auth-rbac
  reads/writes `app_user` over the **app-owner connection** (the same one `database`'s migrations and
  `admin-cli` use). The audit tables are already isolated by `audit_writer`/`audit_reader`.
- **Open path (not foreclosed)**: a dedicated least-privilege auth DB role (scoped to `app_user`, no
  audit-table access) remains a valid **future forward-only migration owned by `database`** (+ Infra
  execution + a `secrets-config` credential). Adopting it later requires **no rewrite** of the app-level
  `authorize` policy. Recorded in the Deferred Decisions register (#4).
- **Why**: proportionate for Phase-1 low-volume `app_user` CRUD; keeps the model minimal and
  reference-not-own; the stronger DB-privilege isolation stays available if the risk profile changes.

### BR-AUTH-10 — OIDC seam reserved; SSO/OAuth deferred
- **Condition**: `app_user.subject` is the **reserved** OIDC identity-binding seam; Phase-1 authz runs
  over an **already-resolved `user_id`**. The **SSO/OAuth authentication flow is deferred to Phase 3 /
  OOS-3** (Deferred Decisions #6). This FD pins how a resolved `user_id` maps to permissions, **not** how
  the user authenticates.
- **Why**: authn is out of Phase-1 scope; the seam keeps the door open without pulling OOS-3 forward.

### BR-AUTH-12 — Advisory-only, deterministic, no LLM
- **Condition**: auth-rbac gates **who may act**; it **never** produces or finalizes an underwriting
  outcome, and the word **"decision" is not used for an authorization result** (that word is reserved for
  the human's committed action). `authorize` is **deterministic** (a pure function of role + rbac_action
  + policy — no wall-clock/randomness). **No LLM** anywhere in this unit.
- **Why**: advisory-only + reproducibility invariants.

---

## 5. Rule index

| Rule | Condition summary | Traces |
|---|---|---|
| BR-AUTH-1 | Role set closed at app layer; DB `role` stays open, no CHECK | BR-DB-12; SEC-4 |
| BR-AUTH-2 | Role→permission matrix is the policy | SEC-4; PER-4..6 |
| BR-AUTH-3 | Deny-by-default — unknown user / non-canonical role / null-blank role → False | SEC-4 fail-closed (fold #1) |
| BR-AUTH-4 | Commit requires underwriter `commit` permission | CON-BR4; audit-store `UnauthorizedCommit` |
| BR-AUTH-5 | Auditor read-only; aligned with DB `audit_reader` | SEC-4; BR-DB-5 |
| BR-AUTH-6 | Two enforcement points, one policy | SEC-4 defense-in-depth (fold #2) |
| BR-AUTH-7 | Conform to built `Authorizer` Protocol; no audit-store edit | audit-store `seams.py`; reference-not-own |
| BR-AUTH-8 | No demographics in authz | CON-BR1 |
| BR-AUTH-9 | Phase-1 app-level roles only; dedicated DB role deferred-open | Deferred #4 |
| BR-AUTH-10 | OIDC `subject` seam reserved; SSO deferred | OOS-3 / Deferred #6 |
| BR-AUTH-11 | `rbac_action` ≠ `CommittedDecision.action` | audit-store seam docstring |
| BR-AUTH-12 | Advisory-only; deterministic; no LLM | advisory-only; reproducibility |

---

## 6. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **Compliant** | `authorize` inputs are `user_id` + `rbac_action`; a non-canonical role or unknown user fail-closes (BR-AUTH-3). No untrusted document parsing here. |
| Prompt-injection defense | **N/A** | No LLM / prompt path in `auth-rbac`. |
| Secrets management | **Compliant** | SEC-3 — no credentials/connection strings in this FD; the app-owner connection URL is `secrets-config`'s (BR-AUTH-9). |
| Read-only DB access for audit role | **Compliant** | BR-AUTH-5 — the app `auditor` role is read-only, aligned with `database`'s `audit_reader` SELECT-only grant. |
| Audit logging | **Compliant (referenced)** | auth-rbac gates access to the audit trail (`read_audit`); the audit trail itself is `audit-store`'s append-only substrate (SEC-5), referenced not owned. |

No blocking finding.
