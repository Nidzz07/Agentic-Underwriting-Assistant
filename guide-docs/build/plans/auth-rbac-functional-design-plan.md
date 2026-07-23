# Functional Design Plan — `auth-rbac` (EPIC-6 / U11)

**Phase / Stage**: BUILD → Functional Design (per-unit, plan-then-generate)
**Unit covered**: U11 `auth-rbac` (EPIC-6, Phase 1) — the **canonical role/permission model + backend
enforcement at both points** (API layer **and** the built `DecisionCommitService` commit re-check).
Story **US-PLAT-1**; owns **SEC-4** (RBAC segregation); traces **PER-4..6**. Invariant-bearing.
**Date**: 2026-07-06
**Runtime**: Python **3.12 pinned** (D6) · **Depth**: comprehensive.
**Status**: **Plan — awaiting `[Answer]:` tags.** No FD artifacts generated yet. Stop after this plan.

This plan follows the build/functional-design rule details. It is the **altitude drop to INTERNALS**
for `auth-rbac`, which — unlike the story-less `database` unit — **does have a frozen
`component-methods.md` interface** (`AuthRBAC.authorize`) and, crucially, a **built consumer that
already codes against it** (audit-store's `Authorizer` Protocol + commit re-check). The FD's job is to
**reconcile against three frozen inputs and re-open none of them**:

1. the **DISCOVER-level `unit-of-work.md` U11** definition (role model + backend enforcement at both
   points; UI-side is a thin C5 facet, Q1=A — not a second unit);
2. **`database`'s `app_user` schema** (BR-DB-12 — open `role`, OIDC `subject` seam) — **consumed, not
   re-designed** (no `database` migration edited here);
3. **audit-store's built `Authorizer` Protocol** (`backend/audit_store/seams.py`) + its commit re-check
   call site (`commit_service.py`) — auth-rbac supplies the **conforming real impl**, wired at the
   composition root; **no audit-store file is edited** (reference-not-own).

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 `auth-rbac` (U11, EPIC-6, Phase 1) — invariant-bearing platform unit
- **Purpose** (`unit-of-work.md §3` U11): the **canonical role/permission model** + **backend
  enforcement at BOTH points** — the API layer (request authz) **and** the `DecisionCommitService`
  re-check (defense in depth, so a read-only auditor is **structurally unable to reach commit**). The
  UI-side enforcement is a **thin consuming facet folded into the C5 UI units** (Q1=A at Units
  Generation — **not** a second unit; not designed here).
- **Story**: US-PLAT-1. **Owned invariant**: **SEC-4** (RBAC segregation — underwriter *acts* vs
  auditor *read-only*). **Traces**: PER-4..6 (role-based access), SEC-4.
- **Application-Design interface** (`component-methods.md` / `services.md`): `AuthRBAC.authorize(user,
  action) -> bool` — "Enforce underwriter (act) vs auditor (read-only); structured for later OIDC.
  Enforcement points: the API layer AND inside `DecisionCommitService`." **Note**: this signature is a
  DISCOVER-level sketch; the **authoritative** signature is the built seam's (§1.2, Q3).
- **Depends on** (`unit-of-work-dependency.md`): **`database`** (the `app_user` user/role store — now
  built) and is consumed by **audit-store** (the commit re-check — already built against the Protocol),
  the **C5 UI facets**, and **admin-cli** (user management). Its `database` dependency is **built** →
  `auth-rbac` is now a **ready leaf**.
- **Depth**: **comprehensive** (invariant-bearing; SEC-4 backend enforcement + the human-gate access
  boundary rest on it).

### 1.2 Frozen design inputs — reconciled against, NOT re-opened

**(a) audit-store's BUILT `Authorizer` Protocol (the authoritative interface).**
`backend/audit_store/seams.py` already ships:
```python
RBAC_COMMIT = "commit"
@runtime_checkable
class Authorizer(Protocol):
    def authorize(self, user_id: str, rbac_action: str) -> bool: ...
```
and `commit_service.py` already calls it as the AUTHZ-1 re-check:
```python
if not self._authorizer.authorize(underwriter_id, RBAC_COMMIT):
    raise UnauthorizedCommit(...)
```
The seam docstring pins the semantics auth-rbac must honor: **`rbac_action` is the RBAC OPERATION**
(e.g. `RBAC_COMMIT`), **distinct from `CommittedDecision.action`** (approve/override) — never
conflated; **audit-store owns the re-check call site, never the policy**; `auth-rbac` wires the real
impl at the composition root. There is also a test fake `AllowRolesAuthorizer(user_id -> {rbac_action})`
that encodes exactly the shape the real impl must satisfy. → **auth-rbac's real `authorize` must
structurally conform to this Protocol** (Q3), and its permission model must **grant `"commit"` to the
underwriter role and deny it to auditor** (the assumption `UnauthorizedCommit` already encodes).

**(b) `database`'s built `app_user` skeleton (the substrate, BR-DB-12).**
`0001_initial_schema.sql` provides `app_user (user_id PK, subject UNIQUE, role VARCHAR — OPEN, no
closed enum)`. BR-DB-12 explicitly hands `auth-rbac`'s **own FD** the ownership of **closing/extending
the role set** and the rest of the user/role model; `database` provides only the substrate + a
forward-only migration slot. Phase-1 known role values: `underwriter`, `auditor` (+ `admin` for
`admin-cli`). The `subject` column is the reserved **OIDC-ready** identity-binding seam. → auth-rbac
**consumes** this table (reads `user_id -> role`), **closes the role set at the application layer**
(Q1), and **does not edit `database`'s migration** (any DB-level change is a database-owned
forward-only migration).

**(c) DISCOVER-level `unit-of-work.md` U11 + US-PLAT-1 + SEC-4/PER-4..6.** The role model + both
backend enforcement points + the "UI facet is not a second unit" scoping — held as the frozen scope.

### 1.3 Reconciliation targets (reference-not-own — the boundaries the FD must respect)
| Frozen artifact | auth-rbac's FD obligation | Must NOT |
|---|---|---|
| audit-store `Authorizer` Protocol + `RBAC_COMMIT` (`seams.py`) | provide a conforming `authorize(user_id, rbac_action) -> bool`; grant `commit` to underwriter / deny auditor | edit `seams.py`/`commit_service.py`; rename/repurpose `rbac_action` |
| `database` `app_user` (BR-DB-12) | read `user_id -> role`; close the role set at the app layer | edit `0001_initial_schema.sql` or add a DB CHECK (that's a database-owned migration) |
| C5 UI RBAC facet (Q1=A) | leave it as a thin consuming facet | design a second UI unit here |
| `secrets-config` (SEC-3) | name credential/URL **shapes** only | put any credential value in the FD |

### 1.4 Binding constraints held through this FD (guardrails skill + project constraints)
- **SEC-4** — RBAC segregation is **backend-enforced at both points**; a read-only auditor is
  structurally unable to reach commit. **Fail-closed / deny-by-default**: an unknown user or an
  unlisted `rbac_action` → `authorize` returns `False`.
- **Advisory-only** — RBAC concerns **system access permission**, not the underwriting outcome. The
  word "decision" is **not** used for an authz result; auth-rbac emits no recommendation/decision
  language and never finalizes an underwriting outcome (it only gates *who may act*).
- **Human-in-the-loop** — auth-rbac **strengthens** the human gate (only an authorized underwriter can
  reach `commit`); it never auto-acts.
- **CON-BR1 / bias-free** — the authz path uses **only** `user_id -> role -> rbac_action`; **no
  demographic identifier** ever enters an authorization decision.
- **No LLM** anywhere in `auth-rbac`. **SEC-3** — no credentials/connection strings in the FD.
- **Reproducibility** — `authorize` is a deterministic function of (user's role, rbac_action, policy);
  no wall-clock/randomness in the decision.

---

## 2. Functional Design execution plan (checkboxes — Step 2)

Artifacts to be generated **after** answers are collected and ambiguity-checked, under
`guide-docs/build/auth-rbac/functional-design/`:
- `domain-entities.md` — the **consumed `app_user`** (read model) + the **canonical `Role`** value set
  (closed at the app layer) + the **`Permission` / `rbac_action`** model + the **role→permission
  matrix** + the **`AuthRBAC` service entity** (`authorize` + user/role lookup) + the reserved **OIDC
  `subject`** seam; a validated **relationship Mermaid** (+ text alternative).
- `business-rules.md` — the **BR-AUTH-\*** integrity/governance rules: role-set closed-at-app-layer
  (DB stays open, BR-DB-12), the permission matrix, **deny-by-default/fail-closed**, **commit requires
  the underwriter permission**, **auditor is read-only**, **two backend enforcement points**,
  **`Authorizer`-Protocol conformance** (reconcile-not-edit), **no-demographics-in-authz** (CON-BR1),
  the **DB-role decision** (per Q6), and the **OIDC-seam-reserved / SSO-deferred** rule. Each rule
  states its condition explicitly + Security-Guardrails compliance table.
- `business-logic-model.md` — the **`authorize()` flow model** (user_id → role lookup → permission
  check → bool), the **composition-root wiring** of the real Authorizer into audit-store's built seam,
  the **two enforcement points** (API-layer + the built commit re-check), the **FD ↔ later-stage
  boundary** (what this FD pins vs what NFR/Infra/`secrets-config` provision), a **consumer/dependency
  map**, and an **invariant self-check** table; a validated flow **Mermaid** (+ text alternative).

- [ ] **P1. Analyze unit context** (§1 above — done).
- [ ] **P2. Collect `[Answer]:` tags** (§3); run the mandatory ambiguity-check; raise a clarification
  file only if any answer is vague/combined/contradictory.
- [ ] **P3. Generate `domain-entities.md`** (app_user read model + Role/Permission model + matrix +
  AuthRBAC entity + OIDC seam + relationship Mermaid).
- [ ] **P4. Generate `business-rules.md`** (BR-AUTH-\* rules + Security-Guardrails compliance).
- [ ] **P5. Generate `business-logic-model.md`** (authorize flow, composition-root wiring, two
  enforcement points, FD↔later boundary, consumer map, invariant self-check).
- [ ] **P6. Reconciliation check** — verify the designed `authorize(user_id, rbac_action) -> bool`
  **structurally satisfies** audit-store's built `Authorizer` Protocol and grants/denies `RBAC_COMMIT`
  per role; verify the role read model matches `database`'s `app_user` columns; verify **no audit-store
  or database file is edited**.
- [ ] **P7. Guardrail compliance pass + present the standardized 2-option completion message** (SEC-4
  backend-enforced, advisory-only, CON-BR1 no-demographics, no-LLM, SEC-3 no-secrets, fail-closed).
  Then Request Changes / Continue to Next Stage → **NFR Requirements** for `auth-rbac`.

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These decide the **role/permission internals + the enforcement + the reconciliation** — they do **not**
re-open audit-store's built Protocol/record or `database`'s `app_user` migration.

### A. Role model

## Question 1 — Where is the role set closed (given DB `role` is intentionally open, BR-DB-12)?
`database`'s `app_user.role` is an **open `VARCHAR`** on purpose (BR-DB-12 defers closing to auth-rbac).
Where does auth-rbac make the role set canonical?

A) **Close the role set at the APPLICATION layer** — auth-rbac owns a canonical `Role` value set
   `{underwriter, auditor, admin}` (Phase-1) as a domain enum, validated when a role is read/assigned;
   the **DB column stays open `VARCHAR` (no DB CHECK)** so extension is a forward-only, non-breaking
   change (BR-DB-12 honored — `database`'s migration is **not** edited). auth-rbac is the single source
   of the canonical role set; unknown/blank role → treated as unauthorized (fail-closed). **Recommended**
   — reconciles "DB open" with "auth-rbac closes it", exactly as BR-DB-12 assigns.
B) Close it at the DB layer with a `CHECK` constraint (rejected — that is a **`database`-owned**
   forward-only migration; editing/adding it here violates reference-not-own).
C) Leave the role free-form with no canonical set (rejected — loses SEC-4 determinism / fail-closed).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — close the role set at the APPLICATION layer: auth-rbac owns a canonical Role value set {underwriter, auditor, admin} (Phase-1) as a domain enum, validated when a role is read/assigned; the DB column stays open VARCHAR (no DB CHECK) so extension is forward-only and non-breaking (BR-DB-12 honored — database's migration not edited). Unknown/blank role → treated as unauthorized (fail-closed).

## Question 2 — The `admin` role + the deferred senior-underwriter escalation role
Phase-1 known values are `underwriter`, `auditor`; `admin-cli` implies an `admin`. What is the Phase-1
canonical set, and how are future roles handled?

A) **Phase-1 canonical `Role` = {underwriter, auditor, admin}** — `underwriter` (act: reach commit),
   `auditor` (read-only), `admin` (user/config management via `admin-cli`, **not** an underwriting
   actor). The **senior-underwriter escalation role stays deferred** (Deferred Decisions #8 — OOS-2);
   new roles are added by extending the canonical set (app layer) with no DB migration. **Recommended.**
B) Only `{underwriter, auditor}` now; add `admin` when `admin-cli` is built (leaves `admin-cli` without
   a role home even though the DB column already anticipates it).
C) Include the senior-underwriter escalation role now (rejected — pulls deferred OOS-2 scope forward).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — Phase-1 canonical Role = {underwriter, auditor, admin}: underwriter (act, reach commit), auditor (read-only), admin (user/config management via admin-cli, not an underwriting actor). Senior-underwriter escalation role stays deferred (Deferred Decisions #8, OOS-2); new roles added by extending the canonical set at the app layer with no DB migration.

### B. Permission model

## Question 3 — `authorize` signature: conform to audit-store's BUILT `Authorizer` Protocol
audit-store's shipped `Authorizer` Protocol is `authorize(self, user_id: str, rbac_action: str) -> bool`
with `RBAC_COMMIT = "commit"`; the Application-Design sketch wrote `authorize(user, action)`. Which is
authoritative?

A) **The BUILT seam signature is authoritative** — auth-rbac's real `AuthRBAC.authorize(user_id: str,
   rbac_action: str) -> bool` **structurally conforms** to audit-store's `Authorizer` Protocol and is
   **injected at the composition root** (where `DecisionCommitService` is wired). `rbac_action` is the
   **RBAC operation** (e.g. `"commit"` = `RBAC_COMMIT`), never `CommittedDecision.action`. **audit-store
   owns the Protocol + the commit re-check call site; auth-rbac provides the conforming impl; NO
   audit-store file is edited** (reference-not-own). The DISCOVER `authorize(user, action)` sketch is
   reconciled to this. **Recommended.**
B) Introduce a different auth-rbac signature and adapt via a shim at the composition root (rejected —
   adds needless indirection; the built Protocol is already the clean contract).
C) Edit audit-store's `seams.py`/`commit_service.py` to a new interface (rejected — reference-not-own
   violation; re-opens frozen built code).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — the BUILT seam signature is authoritative: auth-rbac's real AuthRBAC.authorize(user_id: str, rbac_action: str) -> bool structurally conforms to audit-store's Authorizer Protocol, injected at the composition root. rbac_action is the RBAC operation (e.g. "commit" = RBAC_COMMIT), never CommittedDecision.action. audit-store owns the Protocol + the commit re-check call site; auth-rbac provides the conforming impl; no audit-store file is edited. The DISCOVER authorize(user, action) sketch is reconciled to this.

## Question 4 — The permission model (role → allowed `rbac_action` set)
How does `authorize` decide, and what seeds the matrix (must satisfy the built `RBAC_COMMIT` assumption)?

A) **A role→permission matrix keyed by `rbac_action` string** (data, not code branches): each canonical
   `Role` maps to a set of allowed `rbac_action`s. Phase-1 seed: `underwriter -> {commit, <read ops>}`,
   `auditor -> {<read ops>}` (**no `commit`**), `admin -> {manage_users, <config ops>}`. `authorize`
   = resolve the user's role, then test `rbac_action ∈ allowed(role)`. The built `RBAC_COMMIT="commit"`
   is a first-class member (underwriter allowed, auditor denied — satisfying audit-store's
   `UnauthorizedCommit`). Read operations (e.g. `read_audit`/`view_queue`) are named as the auditor's
   permitted set (aligning with database's `audit_reader` DB role — Q8). **Recommended.**
B) Booleanize on role only (`is_underwriter`) and hardcode `commit` (rejected — no extensible
   permission vocabulary; no auditor read operations).
C) A full resource-level ACL policy engine (rejected — over-engineered for Phase-1 scope).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a role→permission matrix keyed by rbac_action string (data, not code branches): each canonical Role maps to a set of allowed rbac_actions. Phase-1 seed: underwriter -> {commit, <read ops>}, auditor -> {<read ops>} (no commit), admin -> {manage_users, <config ops>}. authorize = resolve the user's role, then test rbac_action ∈ allowed(role). RBAC_COMMIT="commit" is a first-class member (underwriter allowed, auditor denied, satisfying UnauthorizedCommit). Read operations named as the auditor's permitted set (aligning with database's audit_reader DB role).

## Question 5 — user_id → role resolution (consuming `database`'s `app_user`)
`authorize` needs the user's role. Where does it come from?

A) **Read `database`'s `app_user` table** (`user_id` PK → `role`) via an auth-rbac read model
   (a `UserRoleRepository` lookup over the shared Postgres), **deny-by-default** (unknown `user_id` →
   `authorize` returns `False`, fail-closed SEC-4). auth-rbac **consumes** `app_user` (reference-not-own
   — it does not re-design database's schema); the FD pins the **read contract** (the `app_user` columns
   it reads) + the fail-closed semantics. **Recommended.**
B) Hold roles in an in-memory config/map instead of the DB (rejected — diverges from the `app_user`
   substrate database built for exactly this; loses persistence + admin-cli manageability).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — read database's app_user table (user_id PK → role) via an auth-rbac read model (a UserRoleRepository lookup over the shared Postgres), deny-by-default (unknown user_id → authorize returns False, fail-closed SEC-4). auth-rbac consumes app_user (reference-not-own); the FD pins the read contract (which app_user columns it reads) + the fail-closed semantics.

### C. Enforcement points (defense in depth)

## Question 6 — Which enforcement points does this FD pin?
`unit-of-work.md` U11 + `component-methods.md` require backend enforcement at BOTH the API layer AND the
commit re-check. What does the FD pin?

A) **Both backend points.** (i) **The commit re-check** — the call site is **already built** in
   audit-store (`commit_service.py` calls `authorizer.authorize(underwriter_id, RBAC_COMMIT)`);
   auth-rbac supplies the **real Authorizer** wired at the composition root (nothing in audit-store
   changes). (ii) **The API-layer request authz** — auth-rbac owns a **backend enforcement seam** (a
   FastAPI dependency/guard) that blocks an unauthorized request **before** it reaches the service.
   Both are **backend-enforced** (SEC-4), so a read-only auditor is structurally unable to reach commit.
   The **UI-side is a thin consuming facet in the C5 units** (Q1=A — folded, not designed here).
   **Recommended.**
B) Only the commit re-check (rejected — drops the API-layer half; contradicts "both points" and weakens
   defense in depth).
C) Only the API layer (rejected — the built commit re-check already assumes a real `Authorizer`;
   leaving it unimplemented breaks audit-store's `UnauthorizedCommit` path).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — both backend points: (i) the commit re-check — the call site is already built in audit-store; auth-rbac supplies the real Authorizer wired at the composition root, nothing in audit-store changes. (ii) the API-layer request authz — auth-rbac owns a backend enforcement seam (a FastAPI dependency/guard) that blocks an unauthorized request before it reaches the service. Both backend-enforced (SEC-4). UI-side stays a thin consuming facet in the C5 units, not designed here.

### D. The deferred DB-role decision (genuine — resolve as a real choice, not a rubber-stamp)

## Question 7 — Does auth-rbac provision its OWN dedicated PostgreSQL DB role scoped to `app_user`?
This is **Deferred Decisions #4**, now live. Treat it as a genuine decision (like rules-engine's
CANON-SER-authority Q5 and audit-store's ATOMIC-1 transaction mechanism), **not** a default. Both
directions are real:

A) **No new DB role in Phase 1 (app-level roles only).** `app_user.role` values
   (`underwriter`/`auditor`/`admin`) are **application-level data**, entirely distinct from PostgreSQL
   **DB roles**. auth-rbac reads/writes `app_user` over the **app-owner connection** (the same one
   `database`'s migrations and `admin-cli` user-management use) — **no dedicated auth DB role is needed
   merely to store or read `app_user` rows**. The audit tables are **already** isolated by
   `audit_writer`/`audit_reader`, so the marginal DB-privilege isolation of a separate auth role is
   modest for Phase-1 low-volume `app_user` CRUD. A future dedicated least-privilege auth DB role, if
   ever wanted, is a **forward-only migration owned by `database`** that does not disturb the audit
   roles. Matches the register's stated default; keeps the role model minimal + reference-not-own.
   **Recommended** — proportionate for Phase 1; the door to (B) stays open as a forward-only migration.
B) **A dedicated auth-rbac DB role for defense-in-depth.** Provision a least-privilege Postgres DB role
   scoped to `app_user` (e.g. an `app_user_writer` INSERT/SELECT/UPDATE + `app_user_reader` SELECT,
   **no access to the audit tables**), so a compromised auth service **cannot touch the audit tables**
   at the DB-privilege level. Stronger isolation, but it (i) adds a **role-grant migration `database`
   owns** (a new cross-unit dependency + Infra execution + a `secrets-config` credential), and (ii)
   duplicates isolation the audit roles already provide. If chosen, this FD pins the **role semantics**
   and **defers the grant DDL + execution to `database`'s migration sequence + Infrastructure Design +
   `secrets-config`** (the exact pattern the audit roles followed) — nothing executed here (SEC-3).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — no new DB role in Phase 1 (app-level roles only). app_user.role values are application-level data, entirely distinct from PostgreSQL DB roles. auth-rbac reads/writes app_user over the same app-owner connection database's migrations and admin-cli use — no dedicated auth DB role is needed merely to store or read app_user rows. The audit tables are already isolated by audit_writer/audit_reader, so the marginal DB-privilege isolation of a separate auth role is modest for Phase-1 low-volume app_user CRUD. A future dedicated least-privilege auth DB role, if ever wanted, is a forward-only migration owned by database that does not disturb the audit roles. Proportionate for Phase 1; the door to (B) stays open.

### E. Authentication scope + auditor alignment + guardrails

## Question 8 — Authn (OIDC/SSO) vs authz split for Phase 1
`app_user.subject` is the reserved OIDC seam; SSO/OAuth is Deferred #6 (OOS-3). What does this FD design?

A) **Phase-1 = AUTHZ only** over an already-resolved `user_id` — role→permission enforcement. The
   `subject` column is the **reserved OIDC-ready identity-binding seam** (external issuer/subject), but
   the **SSO/OAuth authentication FLOW is deferred to Phase 3 / OOS-3** (register #6). The FD pins how a
   resolved `user_id` maps to permissions, **not** how the user authenticates. **Recommended.**
B) Design the full OIDC authentication flow now (rejected — pulls deferred OOS-3 scope forward).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — Phase-1 = AUTHZ only over an already-resolved user_id — role→permission enforcement. The subject column is the reserved OIDC-ready identity-binding seam, but the SSO/OAuth authentication FLOW is deferred to Phase 3/OOS-3 (register #6). The FD pins how a resolved user_id maps to permissions, not how the user authenticates.

## Question 9 — Alignment of the app-level `auditor` role with database's DB-level `audit_reader`
SEC-4 read-only appears at two layers: auth-rbac's app `auditor` role and database's `audit_reader`
Postgres grant. How does the FD state their relationship?

A) **Two layers of the same SEC-4 segregation, explicitly aligned but distinct.** auth-rbac's
   **application-level `auditor`** (can read audit records via permitted read `rbac_action`s, **cannot**
   `commit`) is the app-layer counterpart of database's **DB-level `audit_reader`** (SELECT-only grant).
   auth-rbac pins the **app-role semantics**; it does **not** re-open or execute database's
   `audit_reader` grant (reference-not-own). The FD states the alignment so the two layers stay
   consistent (defense in depth: app-role check + DB-role enforcement). **Recommended.**
B) Conflate the app role with the DB role (rejected — different layers; app roles are `app_user.role`
   data, DB roles are Postgres roles).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — two layers of the same SEC-4 segregation, explicitly aligned but distinct. auth-rbac's application-level auditor (can read via permitted read rbac_actions, cannot commit) is the app-layer counterpart of database's DB-level audit_reader (SELECT-only grant). auth-rbac pins the app-role semantics; it does not re-open or execute database's audit_reader grant. The FD states the alignment so the two layers stay consistent (defense in depth).

## Question 10 — Depth + artifacts for this FD
`auth-rbac` is invariant-bearing (SEC-4 backend enforcement + the human-gate access boundary). What
depth?

A) **Comprehensive** — the three FD artifacts (`domain-entities.md`, `business-rules.md`,
   `business-logic-model.md`) with the full role/permission model, the BR-AUTH-\* rules, the
   `authorize` flow + composition-root wiring + two enforcement points, the FD↔later-stage boundary, and
   validated Mermaid diagrams (+ text alternatives) — matching the invariant weight and the prior
   invariant-bearing units. **Recommended.**
B) Standard / Minimal (rejected — invariant-bearing SEC-4 unit).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — comprehensive: the three FD artifacts (domain-entities.md, business-rules.md, business-logic-model.md) with the full role/permission model, the BR-AUTH-* rules, the authorize flow + composition-root wiring + two enforcement points, the FD↔later-stage boundary, and validated Mermaid diagrams (+ text alternatives) — matching the invariant weight of the prior invariant-bearing units.

---

## 4. Constraints & settled items held (not re-opened)
- **audit-store's built `Authorizer` Protocol + `RBAC_COMMIT` + commit re-check are FROZEN** — auth-rbac
  provides a **conforming** `authorize(user_id, rbac_action) -> bool` injected at the composition root;
  **no `seams.py`/`commit_service.py` edit** (reference-not-own). The built signature is authoritative
  over the DISCOVER `authorize(user, action)` sketch.
- **`database`'s `app_user` is FROZEN** — auth-rbac **consumes** it (reads `user_id -> role`), **closes
  the role set at the app layer** (BR-DB-12 assigns this to auth-rbac), and edits **no** `database`
  migration; any DB-level change (a CHECK, a dedicated auth DB role) is a **database-owned forward-only
  migration** (Q7-B path).
- **Deferred #4 (auth-rbac's own DB role)** is resolved **explicitly** at Q7 (both directions given) —
  not assumed. **Deferred #6 (SSO/OAuth, OOS-3)** stays deferred (Q8 — `subject` seam reserved).
  **Deferred #8 (senior-underwriter escalation)** stays deferred (Q2).
- **SEC-4** backend-enforced at both points; **fail-closed / deny-by-default**. **Advisory-only** —
  "decision" is not used for an authz result. **CON-BR1** — no demographics in the authz path.
  **No LLM**; **SEC-3** — no credentials in the FD. **Reproducible** `authorize`.
- **UI RBAC facet stays a C5-folded consuming facet** (Q1=A at Units Generation) — not a second unit,
  not designed here.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, and every built unit's code.

---

## 5. Next step (STOP here)
Fill the ten `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory
ambiguity-check (adding a clarification file only if needed), then generate the three `auth-rbac`
Functional Design artifacts (`domain-entities.md`, `business-rules.md`, `business-logic-model.md`) and
present the standardized 2-option completion message. **No FD artifacts or code are generated until the
answers are in and checked.**
