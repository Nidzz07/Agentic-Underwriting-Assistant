# NFR Requirements Plan (Part 1) — `auth-rbac` (EPIC-6 / U11)

**Phase / Stage**: BUILD → NFR Requirements, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `auth-rbac` (invariant-bearing platform unit) · **FD ✅ (approved 2026-07-06)**
→ **NFR Requirements ← here** → NFR Design → [Infra likely SKIP — pure-logic authz unit] → Code-Gen.
**Unit**: U11 `auth-rbac` — the canonical role/permission model + backend enforcement (API layer + the built
`DecisionCommitService` commit re-check). Story **US-PLAT-1**; owns **SEC-4**; traces PER-4..6.
**Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** (D6). · **Depth**: **comprehensive** (invariant-bearing).
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR-Requirements artifacts generated this stage. Stop after this plan.**

This plan follows the build/nfr-requirements rule details + the plan-then-generate discipline. It is built **ON** the
frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) — **re-opening none of it**. Every
`NFR-AUTH-*` target below is drafted to be **pass/fail testable**; the exact set is finalized into `nfr-requirements.md`
only after the `[Answer]:` tags are filled.

---

## 1. Unit context (analyzed)

### 1.1 What NFR Requirements builds ON (frozen FD — NOT re-opened)
- **Canonical `Role`** set `{underwriter, auditor, admin}` closed at the **app layer** (DB `role` stays open, BR-DB-12);
  the **`rbac_action`** vocabulary (`commit` = the built `RBAC_COMMIT`, `view_queue`/`view_memo`/`read_audit`,
  `manage_users`/`manage_config`); the **role→permission matrix** (underwriter: commit + read; auditor: read-only;
  admin: manage_users + config). *(domain-entities §2.)*
- **BR-AUTH-1..12** (`business-rules.md`): role-closed-at-app-layer (1); the matrix (2); **deny-by-default all-three-cases
  (3, fold #1)**; commit-requires-underwriter (4); auditor-read-only ↔ DB `audit_reader` (5); **two points one policy
  (6, fold #2)**; **Authorizer-Protocol conformance, no audit-store edit (7)**; **no-demographics-in-authz (8, CON-BR1)**;
  Phase-1 app-level-roles-only DB decision (9); OIDC-seam-reserved / SSO-deferred (10); `rbac_action` ≠
  `CommittedDecision.action` (11); advisory-only / deterministic / no-LLM (12).
- **Behavioral model** (`business-logic-model.md`): the `authorize()` flow (role lookup → matrix → bool); the
  composition-root wiring into audit-store's built `Authorizer`; the **single-source-of-truth** statement (fold #2); the
  FD↔later-stage boundary.

### 1.2 Dependencies & interfaces (reference-not-own — the boundaries NFR targets must respect)
- **Consumes `database`'s `app_user`** (COMPLETE): reads the `user_id -> role` contract (three columns). NFR targets test
  **auth-rbac's consumption of the contract**, **not** `database`'s schema/migration correctness (that is `database`'s
  own FIDELITY-1 / MIGRATE-1). → **Q7**.
- **Conforms to audit-store's built `Authorizer` Protocol** (COMPLETE, `seams.py`): `authorize(self, user_id: str,
  rbac_action: str) -> bool`, `RBAC_COMMIT = "commit"`. NFR targets test **auth-rbac's structural conformance**, **not**
  audit-store's `UnauthorizedCommit`-raising / `commit_service` internals (audit-store owns those tests). → **Q3, Q8**.
- **Consumed by** the **C5 UI facets** (thin facet, Q1=A — not tested here) and **`admin-cli`** (the `app_user` writer /
  `manage_users`). NFR targets test **nothing** about the UI facet or admin-cli internals.
- **Owned elsewhere (referenced, not built here)**: the app-owner **connection URL** = `secrets-config` (SEC-3); the
  actual **composition-root wiring code** = the integration/app unit; **metrics/traces** = `observability`.

### 1.3 Guardrails held (skill)
- **SEC-4** (fail-closed RBAC segregation — underwriter acts / auditor read-only); **CON-BR4 / human-in-the-loop**
  (only an authorized underwriter reaches commit); **CON-BR1** (no demographics in the authz path); **advisory-only**
  ("decision" is not used for an authz result); **reproducibility** (`authorize` is a pure function); **SEC-3** (no
  credentials in NFR artifacts/tests). **No LLM anywhere in `auth-rbac`.**

### 1.4 The distinguishing NFR theme for this unit
**Unlike `database`** (whose invariants only real Postgres can prove), **`auth-rbac`'s invariants are PURE-LOGIC policy
properties** — `authorize` is a deterministic function of an **injected role read model** + the **static matrix**. So
the NFR set is **primarily UNIT-tier against fakes** (the audit-store / cluster pattern): a **fake `UserRoleRepository`**
supplies `user_id -> role`; the **`Authorizer` Protocol is imported read-only** for a structural `isinstance` check. The
only cross-boundary touches — reading `app_user`, conforming to the built Protocol — are tested **at auth-rbac's own
side of the boundary**, never by re-testing `database`'s or audit-store's internals.

---

## 2. Draft `NFR-AUTH-*` targets (pass/fail testable — finalized after the answers)

Each names its invariant, the FD rule it realizes, and a pass/fail test shape. IDs provisional; primarily **unit-tier**.

### SEC-4 fail-closed (the three deny-by-default cases, each independently testable)
- **NFR-AUTH-DENY-1** (BR-AUTH-3; SEC-4 fail-closed): `authorize` returns **`False`** in each case, tested
  **independently**: (i) **unknown `user_id`** (no row); (ii) **role not in the canonical set** (a non-canonical/unknown
  role value); (iii) **null/blank role** (stated at the app layer even though `app_user.role` is `NOT NULL` in the built
  schema); plus (iv) **`rbac_action` not in the resolved role's allowed set**. Four separate assertions. *(See Q1.)*

### Role→permission matrix (data-driven total-coverage property)
- **NFR-AUTH-MATRIX-1** (BR-AUTH-2): **every (`Role` × `rbac_action`) combination has a defined, deterministic boolean
  outcome** — an exhaustive test over the full cross-product asserts each pair returns `True`/`False` per the matrix, with
  **no unhandled combination, no exception, no `None`**. *(See Q2.)*
- **NFR-AUTH-COMMIT-1** (BR-AUTH-4/5; the SEC-4 core slice): `authorize(user, "commit")` is **`True` only for
  `underwriter`**, **`False` for `auditor` and `admin`** — the exact assumption audit-store's `UnauthorizedCommit`
  encodes. *(Sub-slice of the matrix, called out because it is the human-gate invariant.)*

### Authorizer-Protocol conformance (structural / duck-type — not a description)
- **NFR-AUTH-PROTOCOL-1** (BR-AUTH-7): import audit-store's `@runtime_checkable Authorizer` Protocol **read-only** and
  assert `isinstance(AuthRBAC(...), Authorizer)` is **`True`** (a genuine structural/duck-type check), plus that
  `authorize(user_id, rbac_action)` **returns a `bool`** for the call shape the Protocol declares. **Does not** re-test
  audit-store's `commit_service` raising behavior (reference-not-own; that is audit-store's test). *(See Q3, Q8.)*

### Single-source-of-truth (fold #2 — testable, not just documented)
- **NFR-AUTH-SSOT-1** (BR-AUTH-6): for a grid of `(user_id, rbac_action)` inputs, the **API-layer guard's** allow/deny
  is **identical** to `AuthRBAC.authorize(user_id, rbac_action)` for **every** pair — proving the guard **delegates to the
  one policy** and is **not a divergent second implementation**. (The built commit re-check side calls `authorize`
  directly, so its identity holds by construction; the test pins the API-guard side.) *(See Q4.)*

### CON-BR1 no-demographics (structural property)
- **NFR-AUTH-BIAS-1** (BR-AUTH-8; CON-BR1): **structural** — the authz path's inputs are **exactly** `(user_id: str,
  rbac_action: str)`; it takes **no** `ApplicantProfile`/demographic argument, and the role read model reads **only**
  `user_id`/`role` (never name/gender/city). A signature/type (and/or AST) assertion that a demographic field **cannot**
  enter the decision, plus a belt swap-test (same `user_id`/role under different demographic context → identical result —
  demographics are not even an input). *(See Q5.)*

### Determinism (pure function)
- **NFR-AUTH-DET-1** (BR-AUTH-12; reproducibility): `authorize(user_id, rbac_action)` called **N times** with the same
  inputs + same role/policy → **identical `bool`** every time; **no wall-clock, no randomness, no global mutable state**
  in the decision path. *(See Q6.)*

### Scoped exclusions (reference-not-own)
- **NFR-AUTH-SCOPE-1** (BR-AUTH-7/9; §1.2): NFR targets test **only** auth-rbac's own **conformance** (structural
  Protocol satisfaction), **consumption** (reads the `app_user` contract), and **policy** (matrix / fail-closed /
  determinism / bias). **No target** tests: audit-store's `UnauthorizedCommit`/`commit_service` internals; `database`'s
  `app_user` migration/schema/FIDELITY; the C5 UI facet; the SSO/OAuth flow (OOS-3). *(See Q7, Q8.)*

### Perf / observability (soft)
- **NFR-AUTH-PERF-1** (soft): `authorize` latency (in-memory matrix check + ≤1 role lookup) **observed, non-gated** — no
  hard SLO for a pure-logic authz call. **NFR-AUTH-OBS-1**: metrics/traces are **`observability`'s** concern — **N/A /
  referenced**. No demographic-derived metric (CON-BR1). *(See Q9.)*

---

## 3. Clarifying questions (Step — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide the
**testable-target shape + tech stack** — they do **not** re-open the frozen FD.

## Question 1 — SEC-4 fail-closed: the three deny-by-default cases as independent tests
How is BR-AUTH-3 made pass/fail?

A) **Each fail-closed case is its own independently-testable assertion** (`NFR-AUTH-DENY-1`): (i) unknown `user_id`
   → `False`; (ii) role not in the canonical set → `False`; (iii) null/blank role → `False` (stated at the app layer
   though `app_user.role` is `NOT NULL` in the built schema); plus (iv) an unlisted `rbac_action` for a valid role →
   `False`. Four separate cases, each proven, so a regression in any one is caught in isolation. **Recommended.**
B) One lumped "denies bad input" test (rejected — a single assertion can hide which case regressed; the user asked for
   each case independently testable).
C) Test only the "unknown user" case (rejected — leaves the non-canonical-role and null/blank cases unproven).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — each fail-closed case is its own independently-testable assertion: (i) unknown user_id → False; (ii) role not in the canonical set → False; (iii) null/blank role → False; (iv) an unlisted rbac_action for a valid role → False. Four separate cases, each proven, so a regression in any one is caught in isolation.

## Question 2 — The role→permission matrix as a data-driven total-coverage property
How is BR-AUTH-2 tested so there is no unhandled combination?

A) **An exhaustive test over the full `Role` × `rbac_action` cross-product** (`NFR-AUTH-MATRIX-1`): every combination
   returns a **defined, deterministic `bool`** matching the matrix — **no unhandled pair, no exception, no `None`**. Plus
   the called-out SEC-4 slice (`NFR-AUTH-COMMIT-1`): `commit` is `True` **only** for `underwriter`. Parametrized (and/or a
   Hypothesis property over the finite grid). **Recommended.**
B) Spot-check a few representative pairs (rejected — a new `rbac_action` or role could add an unhandled combination that
   spot-checks miss).
C) Assert only the commit slice (rejected — leaves the read-op / admin-op cells unverified).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — an exhaustive test over the full Role × rbac_action cross-product: every combination returns a defined, deterministic bool matching the matrix — no unhandled pair, no exception, no None. Plus the called-out SEC-4 slice: commit is True only for underwriter. Parametrized (and/or a Hypothesis property over the finite grid).

## Question 3 — Authorizer-Protocol conformance as a STRUCTURAL test (not a description)
How is BR-AUTH-7 proven?

A) **A structural/duck-type test** (`NFR-AUTH-PROTOCOL-1`): import audit-store's `@runtime_checkable Authorizer` Protocol
   **read-only** and assert `isinstance(AuthRBAC(...), Authorizer)` is **`True`**, and that `authorize(user_id,
   rbac_action)` **returns a `bool`**. This proves the real impl genuinely satisfies the interface audit-store injects —
   a check, not prose. It **does not** re-test audit-store's `commit_service`/`UnauthorizedCommit` internals
   (reference-not-own; those are audit-store's own tests). **Recommended.**
B) Only document that the signatures match (rejected — the user explicitly wants a structural test, not a description).
C) Test conformance by driving audit-store's `DecisionCommitService` end-to-end (rejected — that tests audit-store's
   internals, violating the scoped exclusion; conformance is auth-rbac's own structural property).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a structural/duck-type test: import audit-store's @runtime_checkable Authorizer Protocol read-only and assert isinstance(AuthRBAC(...), Authorizer) is True, and that authorize(user_id, rbac_action) returns a bool. Proves the real impl genuinely satisfies the interface. Does not re-test audit-store's commit_service/UnauthorizedCommit internals.

## Question 4 — Single-source-of-truth (fold #2) as a testable property
How is "both enforcement points, one policy" proven, not just documented?

A) **An identity test** (`NFR-AUTH-SSOT-1`): drive a grid of `(user_id, rbac_action)` through the **API-layer guard** and
   assert its allow/deny **equals `AuthRBAC.authorize(user_id, rbac_action)`** for **every** pair — proving the guard
   **delegates to the one policy** (not a divergent second implementation). The built commit re-check calls `authorize`
   directly, so its identity holds by construction; a structural check also confirms the guard holds a reference to the
   single `AuthRBAC` and contains **no inlined role logic**. **Recommended.**
B) Only assert the guard blocks an auditor (rejected — proves blocking, not that the guard shares the one policy; a
   divergent second policy could still pass that test).
C) Leave fold #2 as documentation (rejected — the user asked for it to be testable).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — an identity test: drive a grid of (user_id, rbac_action) through the API-layer guard and assert its allow/deny equals AuthRBAC.authorize(user_id, rbac_action) for every pair — proving the guard delegates to the one policy. A structural check also confirms the guard holds a reference to the single AuthRBAC and contains no inlined role logic.

## Question 5 — CON-BR1 (no demographics in authz) as a structural property
How is BR-AUTH-8 made checkable?

A) **Structural-primary** (`NFR-AUTH-BIAS-1`): assert the authz path's inputs are **exactly** `(user_id: str,
   rbac_action: str)` — it accepts **no** `ApplicantProfile`/demographic argument — and the role read model reads **only**
   `user_id`/`role` (a signature/type — and, if useful, an AST/attribute — assertion that a demographic field cannot
   enter the decision). **Belt**: a swap-test (same `user_id`/role, different demographic context → identical result,
   since demographics are not even an input). **Recommended.**
B) Only a swap-test (weaker — proves invariance for the cases tried, but not that a demographic field structurally cannot
   enter; the structural assertion is the stronger guarantee).
C) Documentation only (rejected — CON-BR1 must be checkable).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — structural-primary: assert the authz path's inputs are exactly (user_id: str, rbac_action: str) — no ApplicantProfile/demographic argument — and the role read model reads only user_id/role. A signature/type (and AST/attribute) assertion that a demographic field cannot enter the decision. Belt: a swap-test (same user_id/role, different demographic context → identical result).

## Question 6 — Determinism (pure function) as a testable property
How is BR-AUTH-12 determinism proven?

A) **A repeat-invariance test** (`NFR-AUTH-DET-1`): `authorize(user_id, rbac_action)` called **N times** with identical
   inputs + identical role/policy → **identical `bool`** every time; and a structural check that the decision path uses
   **no wall-clock / randomness / global mutable state**. **Recommended.**
B) Assume determinism because it is pure Python (rejected — the project makes reproducibility a checkable target, not an
   assumption; same discipline as the calibration suites elsewhere).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a repeat-invariance test: authorize(user_id, rbac_action) called N times with identical inputs + identical role/policy → identical bool every time; plus a structural check that the decision path uses no wall-clock/randomness/global mutable state.

## Question 7 — Role-resolution test substrate (consume `app_user` WITHOUT testing `database`'s internals)
How is the `user_id -> role` consumption tested without re-testing `database`'s schema?

A) **Against a fake `UserRoleRepository`** implementing the read contract (`user_id -> role`), **unit-tier** (the
   audit-store fake-repository pattern) — so every policy/fail-closed/matrix target runs fast with no container and tests
   **auth-rbac's own logic**. The real-Postgres `app_user` read is exercised **only** as a thin **optional integration
   smoke** (auth-rbac can read a seeded `app_user` row via the contract) that **asserts nothing about `database`'s schema
   correctness** (that is `database`'s FIDELITY-1 / MIGRATE-1). **Recommended** — keeps the scoped exclusion crisp.
B) Test role resolution only against real Postgres with `database`'s migrations (rejected — slow, and it entangles
   auth-rbac's tests with `database`'s schema-correctness, which `database` already owns).
C) Skip the consumption test (rejected — the read contract is a real dependency worth a guard).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — against a fake UserRoleRepository implementing the read contract (user_id -> role), unit-tier (the audit-store fake-repository pattern) — so every policy/fail-closed/matrix target runs fast with no container and tests auth-rbac's own logic. The real-Postgres app_user read is exercised only as a thin optional integration smoke that asserts nothing about database's schema correctness.

## Question 8 — Scoped exclusions (explicit boundary)
What does `NFR-AUTH-SCOPE-1` explicitly exclude?

A) **NFR targets test ONLY** auth-rbac's own **conformance** (structural Protocol satisfaction), **consumption** (reads
   the `app_user` contract), and **policy** (matrix / fail-closed / determinism / bias / SSOT). They **do NOT** test:
   audit-store's `UnauthorizedCommit`/`commit_service` internals; `database`'s `app_user` migration/schema/FIDELITY; the
   C5 UI facet; the SSO/OAuth flow (OOS-3). Stated explicitly so no target drifts into another unit's ownership.
   **Recommended.**
B) Leave the boundary implicit (rejected — the user asked for scoped exclusions to be explicit).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — NFR targets test ONLY auth-rbac's own conformance (structural Protocol satisfaction), consumption (reads the app_user contract), and policy (matrix/fail-closed/determinism/bias/SSOT). They do NOT test: audit-store's UnauthorizedCommit/commit_service internals; database's app_user migration/schema/FIDELITY; the C5 UI facet; the SSO/OAuth flow (OOS-3). Stated explicitly.

## Question 9 — Perf / observability posture (pure-logic unit)
What perf/obs targets apply?

A) **Soft/observed, not gated**: `authorize` latency (in-memory matrix check + ≤1 role lookup) observed against a **soft
   budget** (no hard SLO for a pure-logic call); metrics/traces = **`observability`'s** concern (**N/A / referenced**).
   No demographic-derived metric (CON-BR1). Keeps the NFR set honest. **Recommended.**
B) Define a hard latency SLO here (rejected — premature for a pure-logic authz call).
C) Omit perf/obs entirely (acceptable-ish, but A's explicit soft/N-A framing is clearer for the compliance summary).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — soft/observed, not gated: authorize latency (in-memory matrix check + ≤1 role lookup) observed against a soft budget (no hard SLO); metrics/traces = observability's concern (N/A/referenced). No demographic-derived metric.

## Question 10 — Test framework + tech stack (companion `tech-stack-decisions.md`)
What does the NFR tech-stack pin vs defer?

A) **Pin**: pytest; **unit-tier against fakes** (an injected `UserRoleRepository` fake + a read-only import of
   audit-store's `Authorizer` Protocol for the `isinstance` check); **Hypothesis** (already in the stack) optional for the
   matrix/property exhaustiveness; **Pydantic v2** (already in the stack) for the `Role` enum if used; **Python 3.12**;
   **no new production dependency**; **no LLM**. The optional thin real-`app_user` smoke reuses the **existing
   testcontainers** stack. **Reference-not-own**: import audit-store's `Authorizer` Protocol **read-only**; consume
   `database`'s `app_user` contract; **edit neither**. **Recommended.**
B) Introduce a new authz/policy framework (e.g. Casbin/OPA) (rejected — the matrix is a few lines of pure Python; a new
   dependency is unjustified for Phase-1 scope).
C) Pin a real-Postgres-only test substrate (rejected — the invariants are pure-logic; fakes are the primary tier).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — pin pytest; unit-tier against fakes (an injected UserRoleRepository fake + a read-only import of audit-store's Authorizer Protocol for the isinstance check); Hypothesis (already in stack) optional for matrix/property exhaustiveness; Pydantic v2 (already in stack) for the Role enum if used; Python 3.12; no new production dependency; no LLM. Optional thin real-app_user smoke reuses existing testcontainers stack. Reference-not-own: import audit-store's Protocol read-only; consume database's app_user contract; edit neither.

## Question 11 — Depth confirmation
What depth for this NFR Requirements stage?

A) **Comprehensive** — the full pass/fail `NFR-AUTH-*` set across fail-closed, matrix total-coverage, Protocol
   conformance, single-source-of-truth, no-demographics, determinism, scoped exclusions, and soft perf/obs — each traced
   to its FD rule + invariant, matching the unit's invariant weight (SEC-4 + the human-gate access boundary).
   **Recommended.**
B) Standard — a shorter target list.
C) Minimal — targets sketch only.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — comprehensive: the full pass/fail NFR-AUTH-* set across fail-closed, matrix total-coverage, Protocol conformance, single-source-of-truth, no-demographics, determinism, scoped exclusions, and soft perf/obs — each traced to its FD rule + invariant, matching the unit's invariant weight (SEC-4 + the human-gate access boundary).

---

## 4. Constraints & settled items held (not re-opened)
- The **frozen FD** (role/permission model + BR-AUTH-1..12 + the authorize flow) is the substrate — NFR builds testable
  targets **on** it, re-opening nothing.
- **audit-store's built `Authorizer` Protocol + `commit_service` stay frozen** — conformance is tested by a **read-only**
  Protocol import + `isinstance`; **no audit-store code is edited or re-tested** (reference-not-own).
- **`database`'s `app_user` stays frozen** — consumption is tested against the **read contract** (fake repo primary; an
  optional thin real-`app_user` smoke asserts nothing about `database`'s schema correctness).
- **Scoped exclusions explicit** (`NFR-AUTH-SCOPE-1`): no target tests audit-store's / database's internals, the C5 UI
  facet, or the deferred SSO/OAuth flow (OOS-3).
- **SEC-4** fail-closed (three cases independently testable); **fold #2** single-source-of-truth is a **test**, not a doc;
  **CON-BR1** no-demographics is **structural**; **determinism** is a **repeat-invariance test**; **advisory-only** ("decision"
  not used for an authz result); **SEC-3** (no credentials in NFR artifacts/tests). **No LLM in `auth-rbac`.**
- **Infrastructure Design** for `auth-rbac` is **likely a logged SKIP** (pure-logic authz unit — no independent cloud
  topology; the app-owner connection is `secrets-config`/deploy-config's; a future dedicated auth DB role is the
  deferred-open Q7-A/BR-AUTH-9 path owned by `database`). Confirmed at that stage, not pre-committed here.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, and every built unit's code.

---

## 5. Next step (STOP here)
Fill the eleven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then generate the two `auth-rbac` NFR Requirements artifacts
(`nfr-requirements.md` + `tech-stack-decisions.md`) and present the standardized 2-option completion message. **No NFR
Requirements artifacts or code are generated until the answers are in and checked.**
