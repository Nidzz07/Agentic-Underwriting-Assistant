# NFR Requirements — `auth-rbac` (EPIC-6 / U11)

**Stage**: BUILD → NFR Requirements (per-unit) · invariant-bearing platform unit
**Unit**: U11 `auth-rbac` — the canonical role/permission model + backend enforcement (API layer + the built
`DecisionCommitService` commit re-check). Story **US-PLAT-1**; owns **SEC-4**; traces PER-4..6.
**Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: comprehensive.
**Built ON** the frozen FD (`domain-entities.md` incl. the 2026-07-07 §2.5 read-contract back-annotation /
`business-rules.md` / `business-logic-model.md`) — **re-opening none of it**. Each `NFR-AUTH-*` target is a
**pass/fail testable assertion** traced to its FD rule (BR-AUTH-*) + invariant, with an explicit **test tier**.
**No credentials** appear here (SEC-3). **No LLM** in `auth-rbac`.

---

## 0. Central testability principle + scope boundary

- **`auth-rbac`'s invariants are PURE-LOGIC policy properties** — `authorize` is a deterministic function of an
  **injected role read model** + the **static role→permission matrix**. So the target set is **primarily unit-tier
  against fakes** (the audit-store / cluster pattern): a **fake `UserRoleRepository`** supplies the **raw `str | None`**
  role value; audit-store's **`Authorizer` Protocol is imported read-only** for the structural `isinstance` check.
- **Read-contract shape (per the frozen-FD §2.5 back-annotation)**: `UserRoleRepository.get_role(user_id) -> str |
  None` returns the **raw `app_user.role`** (None = no row; else the stored string, canonical or not, possibly blank).
  **Canonicalization + fail-close live in `authorize`.** This is what makes DENY-1's three cases independently
  constructible and keeps the **fake and the real Postgres-backed repository identical in shape** (no drift).
- **Scope boundary (reference-not-own)**: targets test **only** auth-rbac's own **conformance** (structural Protocol
  satisfaction), **consumption** (reads the `app_user` contract), and **policy** (matrix / fail-close / determinism /
  bias / SSOT). **No target** tests audit-store's `commit_service`/`UnauthorizedCommit` internals, `database`'s
  `app_user` migration/schema/FIDELITY, the C5 UI facet, or the deferred SSO/OAuth flow (OOS-3). See NFR-AUTH-SCOPE-1.

---

## 1. Finalized `NFR-AUTH-*` targets (pass/fail; test tier stated)

### NFR-AUTH-DENY-1 — SEC-4 fail-closed, the three cases + unlisted action, each independent (BR-AUTH-3)
- **Assertion (four independent pass/fail cases)** — with a fake `UserRoleRepository` returning the raw value:
  (i) **unknown `user_id`** → `get_role` returns `None` → `authorize(user_id, any) == False`;
  (ii) **non-canonical role** → `get_role` returns a string **not** in `{underwriter, auditor, admin}` (e.g. `"wizard"`)
  → `authorize == False`;
  (iii) **null/blank role** → `get_role` returns `""` / whitespace → `authorize == False` *(stated at the app layer
  even though `app_user.role` is `NOT NULL` in the built schema — DB-null is structurally prevented, app-layer
  fail-close is still asserted)*;
  (iv) **unlisted `rbac_action`** for a **valid** role → `authorize == False`.
  Each case is **constructed and asserted independently** (the raw `str | None` contract makes (i), (ii), (iii)
  distinct inputs / distinct code paths), so a regression in any one is caught in isolation.
- **Test tier**: **unit** (fake repository; no container).

### NFR-AUTH-MATRIX-1 — role→permission matrix total coverage (BR-AUTH-2)
- **Assertion**: for the **full `Role` × `rbac_action` cross-product** (the three canonical roles × the Phase-1
  `rbac_action` vocabulary), `authorize` returns a **defined, deterministic `bool`** matching the matrix — **no
  unhandled combination, no exception, no `None`**. Realized as a **parametrized** test over the finite grid (and/or a
  Hypothesis property over the same finite grid).
- **Test tier**: **unit**.

### NFR-AUTH-COMMIT-1 — the SEC-4 core slice (BR-AUTH-4/5)
- **Assertion**: `authorize(user_id, "commit")` is **`True` only when the user's role is `underwriter`**, and **`False`
  for `auditor` and `admin`** — the exact assumption audit-store's `UnauthorizedCommit` encodes (`"commit"` is the
  built `RBAC_COMMIT`). Called out separately because it is the human-gate invariant.
- **Test tier**: **unit**.

### NFR-AUTH-PROTOCOL-1 — Authorizer-Protocol conformance, proven by TWO assertions together (BR-AUTH-7) *(sharpening #1)*
- **Assertion (both required)**: importing audit-store's `@runtime_checkable Authorizer` Protocol **read-only** (the
  same object `commit_service.py` imports):
  1. **Structural presence** — `isinstance(AuthRBAC(...), Authorizer) is True`. *(Note: `@runtime_checkable`
     `isinstance` verifies **method presence only**, NOT the signature.)*
  2. **Call-shape / return-type** — `authorize(user_id: str, rbac_action: str)` invoked with two `str` args **returns a
     `bool`**. *(This is the assertion that actually pins the **signature + return type** the Protocol declares —
     `isinstance` alone does not.)*
  Together they prove the real impl genuinely satisfies the interface audit-store injects. **Does NOT** re-test
  audit-store's `commit_service`/`UnauthorizedCommit` behavior (reference-not-own).
- **Test tier**: **unit** (read-only Protocol import; no audit-store execution).

### NFR-AUTH-SSOT-1 — single source of truth, as a delegation test (BR-AUTH-6; fold #2) *(sharpening #2)*
- **Assertion (two parts)**:
  1. **Identity** — for a grid of `(user_id, rbac_action)` inputs, the **API-layer guard's** allow/deny is **identical**
     to `AuthRBAC.authorize(user_id, rbac_action)` for **every** pair.
  2. **Delegation-via-injected-stub (the concrete "no inlined role logic" check)** — construct the guard with a **stub
     `AuthRBAC`** whose `authorize` returns a **controlled** value; assert the **guard's decision follows the stub's
     output** (and flips when the stub flips). If the guard held any independent/inlined role logic, its decision would
     **not** track the swapped stub → the test fails. This proves the guard is a second enforcement **point** delegating
     to the **one** policy, not a second policy implementation.
- **Test tier**: **unit** (stub/spy `AuthRBAC`; no live service).

### NFR-AUTH-BIAS-1 — CON-BR1 no-demographics, structural (BR-AUTH-8)
- **Assertion (structural-primary + belt)**:
  - **Structural** — `inspect.signature(AuthRBAC.authorize)` has parameters **exactly** `{user_id, rbac_action}`
    (plus `self`), **none** typed `ApplicantProfile` / `Demographics` / any demographic shape; and the
    `UserRoleRepository` read contract takes **only** `user_id` and returns only a role `str | None` (never name /
    gender / city). A demographic field **cannot structurally enter** the authz decision.
  - **Belt** — a swap-test: same `user_id` / role under different demographic *context* → **identical** result (a
    tautology given demographics are not even an input, but it documents the invariant).
- **Test tier**: **unit** (signature/type introspection + swap).

### NFR-AUTH-DET-1 — determinism, repeat-invariance (BR-AUTH-12)
- **Assertion**: `authorize(user_id, rbac_action)` called **N times** with identical inputs + identical role/policy
  yields an **identical `bool`** every time; and a **structural** check that the decision path uses **no wall-clock, no
  randomness, no global mutable state**.
- **Test tier**: **unit**.

### NFR-AUTH-SCOPE-1 — scoped exclusions *(GOVERNANCE / EXCLUSION STATEMENT — not a runtime test)*
- **Statement (not a pass/fail runtime assertion — labeled as such, consistent with `database`'s OBS-1 boundary)**:
  the `NFR-AUTH-*` set tests **only** auth-rbac's own **conformance / consumption / policy**. It **does NOT** test, and
  no target may drift into: audit-store's `UnauthorizedCommit`/`commit_service` internals; `database`'s `app_user`
  migration / schema / FIDELITY; the C5 UI RBAC facet; the deferred SSO/OAuth flow (OOS-3). This governs the boundary of
  the whole set — it is a scoping declaration, enforced by review, not a runtime check.
- **Test tier**: **N/A (governance statement)**.

### NFR-AUTH-PERF-1 — soft budget, observed not gated
- **Assertion**: `authorize` latency (in-memory matrix check + ≤1 role lookup) is **observed against a soft budget** —
  **no hard SLO** for a pure-logic authz call. No demographic-derived metric (CON-BR1).
- **Test tier**: **observed** (non-gating).

### NFR-AUTH-OBS-1 — observability owned elsewhere (referenced)
- **Assertion**: metrics/traces for authz are **`observability`'s** concern — **N/A here** (referenced, not owned).
- **Test tier**: **N/A**.

---

## 2. Traceability (target → FD rule → invariant → tier)

| Target | FD rule | Invariant | Tier |
|---|---|---|---|
| NFR-AUTH-DENY-1 | BR-AUTH-3 | SEC-4 fail-closed | unit |
| NFR-AUTH-MATRIX-1 | BR-AUTH-2 | policy total-coverage | unit |
| NFR-AUTH-COMMIT-1 | BR-AUTH-4/5 | SEC-4 / CON-BR4 human gate | unit |
| NFR-AUTH-PROTOCOL-1 | BR-AUTH-7 | Authorizer conformance (reference-not-own) | unit |
| NFR-AUTH-SSOT-1 | BR-AUTH-6 | single source of truth (fold #2) | unit |
| NFR-AUTH-BIAS-1 | BR-AUTH-8 | CON-BR1 no-demographics | unit |
| NFR-AUTH-DET-1 | BR-AUTH-12 | reproducibility | unit |
| NFR-AUTH-SCOPE-1 | BR-AUTH-7/9 | reference-not-own boundary | N/A (governance) |
| NFR-AUTH-PERF-1 | — | soft budget | observed |
| NFR-AUTH-OBS-1 | — | observability-owned | N/A |

---

## 3. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **Compliant** | `authorize` inputs are `(user_id, rbac_action)`; unknown user / non-canonical / blank role / unlisted action fail-close (DENY-1). |
| Prompt-injection defense | **N/A** | No LLM/prompt path in `auth-rbac`. |
| Secrets management | **Compliant** | SEC-3 — no credentials/URLs in these artifacts/tests; the app-owner connection URL is `secrets-config`'s. |
| Read-only DB access for audit role | **Compliant** | NFR-AUTH-COMMIT-1 / MATRIX-1 — the app `auditor` role is read-only (no `commit`), aligned with `database`'s `audit_reader` grant. |
| Audit logging | **Compliant (referenced)** | auth-rbac gates access to the audit trail (`read_audit`); the trail itself is audit-store's append-only substrate (SEC-5), referenced not owned. |

No blocking finding.

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (role/permission model + BR-AUTH-1..12 + the authorize flow, incl. the 2026-07-07 §2.5 read-contract
  back-annotation) is the substrate — NFR builds testable targets **on** it, re-opening nothing further.
- **audit-store's built `Authorizer` Protocol + `commit_service` stay frozen** — conformance is a **read-only** Protocol
  import + `isinstance` + call-shape; **no audit-store code is edited or re-tested** (reference-not-own).
- **`database`'s `app_user` stays frozen** — consumption is tested against the **raw `str | None` read contract** (fake
  repo primary; an optional thin real-`app_user` smoke asserts nothing about `database`'s schema correctness).
- **SEC-4** fail-closed (three cases independently testable); **fold #2** SSOT is a **delegation test**, not a doc;
  **CON-BR1** no-demographics is **structural**; **determinism** is a **repeat-invariance test**; **advisory-only**
  ("decision" not used for an authz result); **SEC-3** (no credentials). **No LLM in `auth-rbac`.**
- **Infrastructure Design** for `auth-rbac` is **likely a logged SKIP** (pure-logic authz unit) — confirmed at that
  stage, not pre-committed. Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code.
