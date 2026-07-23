# NFR Design Plan (Part 1) — `auth-rbac` (EPIC-6 / U11)

**Phase / Stage**: BUILD → NFR Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `auth-rbac` · FD ✅ (approved 2026-07-06, §2.5 back-annotated 2026-07-07) · **NFR Requirements ✅
(approved 2026-07-07)** → **NFR Design ← here** → [Infra likely SKIP] → Code-Gen.
**Unit**: U11 `auth-rbac` — canonical role/permission model + backend enforcement (API layer + the built commit re-check).
**Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: comprehensive (invariant-bearing, SEC-4).
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR-Design artifacts generated this stage. Stop after this plan.**

This plan maps each approved **`NFR-AUTH-*`** target to a **named design pattern** + the **logical components** that
realize it, built **ON** the frozen FD (`domain-entities.md` incl. the §2.5 read-contract back-annotation /
`business-rules.md` / `business-logic-model.md`) and the approved `nfr-requirements.md` — **re-opening neither**.
**No credentials** (SEC-3). **No LLM.**

---

## 1. Unit context (analyzed)

### 1.1 What NFR Design builds ON (frozen — NOT re-opened)
- **FD**: canonical `Role` `{underwriter, auditor, admin}` (closed at app layer; DB `role` stays open, BR-DB-12); the
  `rbac_action` vocabulary (`commit` = built `RBAC_COMMIT`, `view_queue`/`view_memo`/`read_audit`,
  `manage_users`/`manage_config`); the role→permission matrix; `authorize(user_id, rbac_action) -> bool`; the **§2.5
  read contract `UserRoleRepository.get_role(user_id) -> str | None`** (raw value; canonicalization + fail-close in
  `authorize`); the two enforcement points, one policy.
- **NFR targets** (`nfr-requirements.md`): DENY-1 (four independent cases), MATRIX-1 (exhaustive), COMMIT-1,
  **PROTOCOL-1 (isinstance + call-shape, two assertions)**, **SSOT-1 (delegation-via-injected-stub)**, BIAS-1
  (structural signature), DET-1 (repeat-invariance), SCOPE-1 (governance/exclusion — not a runtime test), PERF-1 (soft),
  OBS-1 (N/A).

### 1.2 The distinguishing design theme
`auth-rbac` is a **pure-logic policy** unit. **One `authorize` implementation** — *read raw role → canonicalize +
fail-close → matrix-membership* — **naturally satisfies the whole DENY-1 / MATRIX-1 / COMMIT-1 family** (no separate
code path per case). Conformance to audit-store's `Authorizer` is **structural/duck-typed** — so **production
`auth-rbac` code does NOT import `audit_store`** (the `Authorizer` Protocol is imported **read-only in the PROTOCOL-1
test only**, exactly the reference-not-own posture `database`'s `fidelity_comparator` used). No circular dependency.

### 1.3 Guardrails held (skill)
SEC-4 fail-closed; CON-BR4 human gate (only underwriter reaches `commit`); CON-BR1 no-demographics (structural);
advisory-only ("decision" not used for an authz result); reproducibility (pure `authorize`); SEC-3 (no credentials).
**No LLM.**

---

## 2. Draft pattern → target map (finalized after the answers)

| Pattern | Backs | Shape |
|---|---|---|
| **FailClosedMatrixLookupPattern** | DENY-1, MATRIX-1, COMMIT-1 | one linear `authorize`: `get_role → canonicalize/fail-close → rbac_action ∈ matrix[Role]` — all four DENY cases + the exhaustive matrix + the commit slice satisfied by **one** implementation |
| **RawToRoleCanonicalizationPattern** | DENY-1 (ii)/(iii) | a total `to_role(raw: str | None) -> Role | None` (miss → `None`, no exception-driven control flow) — makes non-canonical + blank fail-close distinct from "no row" |
| **ImmutablePolicyMatrixPattern** | MATRIX-1, COMMIT-1 | a module-level immutable `dict[Role, frozenset[str]]` — the single policy datum |
| **StructuralProtocolConformancePattern** | PROTOCOL-1 | `AuthRBAC.authorize(self, user_id: str, rbac_action: str) -> bool` matches the Protocol member by **duck typing** — **no production import of `audit_store`**; the Protocol import + `isinstance` + call-shape assertions live in the test |
| **InjectedDelegationGuardPattern** | SSOT-1 | the API-layer guard holds a **single injected `AuthRBAC`** and its only logic is `return self._authz.authorize(...)` — no inlined role/permission data; makes the injected-stub test meaningful |
| **SignatureConstraintPattern** | BIAS-1 | `authorize` + `get_role` type hints admit **only** `user_id`/`rbac_action` (str) — no `ApplicantProfile`/`Demographics` parameter can structurally enter |
| **PureFunctionPattern** | DET-1 | `authorize` is a pure function of (injected role result, immutable matrix) — no wall-clock, no RNG, no module-global mutable state |
| **ReferencedBoundaryPattern** | SCOPE-1, PERF-1, OBS-1 | SCOPE-1 = governance/exclusion statement; PERF-1 soft-observed; OBS-1 N/A (observability-owned) |

---

## 3. Draft logical components (finalized after the answers)

- **C1 `AuthRBAC`** — the service class; `authorize(user_id, rbac_action) -> bool` (the FailClosedMatrixLookup).
- **C2 `Role`** — the canonical enum (closed at app layer; DB `role` open).
- **C3 `PERMISSION_MATRIX`** — immutable `dict[Role, frozenset[str]]`.
- **C4 `to_role`** — the raw-`str`→`Role|None` canonicalization helper *(may fold into C1 — Q9)*.
- **C5 `UserRoleRepository`** — the Protocol `get_role(user_id) -> str | None` + an **in-memory fake** (unit tests) + a
  **real Postgres-backed adapter stub** (reads `app_user.role`; wired at Code-Gen; consumes `database`, reference-not-own).
- **C6 `ApiAuthGuard`** — the API-layer delegation guard (holds the injected `AuthRBAC`; no independent policy).

---

## 4. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide the
**design-pattern shape** — they do **not** re-open the FD or the approved NFR targets.

## Question 1 — The fail-closed matrix-lookup pattern (DENY-1 / MATRIX-1 / COMMIT-1 from ONE implementation)
How is `authorize` structured so all four DENY cases + the exhaustive matrix + the commit slice are satisfied by a
single implementation, not separate per-case paths?

A) **One linear fail-closed flow**: `raw = repo.get_role(user_id)` → `role = to_role(raw)` (→ `None` for no-row / blank /
   non-canonical) → **if `role is None`: return `False`** → else `return rbac_action in PERMISSION_MATRIX[role]`. The four
   DENY cases are just the input variations that drive `role is None` or a non-member action; the exhaustive matrix and
   the commit slice are the same one-line membership test over every `(role, rbac_action)`. **One implementation, no
   branching per case.** **Recommended.**
B) Separate methods per case (`_check_unknown`, `_check_role`, …) (rejected — multiple paths to keep in sync; the
   invariant is that one flow covers them all).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — one linear fail-closed flow: raw = repo.get_role(user_id) → role = to_role(raw) (→ None for no-row/blank/non-canonical) → if role is None: return False → else return rbac_action in PERMISSION_MATRIX[role]. The four DENY cases are just input variations driving role is None or a non-member action; the exhaustive matrix and commit slice are the same one-line membership test. One implementation, no branching per case.

## Question 2 — The raw→Role canonicalization step
How is a raw `str | None` mapped to a canonical `Role` (or a fail-close `None`) without exception-driven control flow?

A) **A total helper `to_role(raw: str | None) -> Role | None`**: returns the `Role` member for an **exact** canonical
   string match; returns **`None`** for `None`, blank/whitespace, or any non-canonical string (a membership lookup, e.g.
   over `Role`'s value map — **no `try/except` as control flow**). Deterministic + total → every input has a defined
   result (supports DENY-1's independent cases). **Recommended.**
B) `Role(raw)` wrapped in `try/except ValueError` (works, but exception-as-control-flow; A's explicit total function is
   clearer and cheaper).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a total helper to_role(raw: str | None) -> Role | None: returns the Role member for an exact canonical string match; returns None for None, blank/whitespace, or any non-canonical string (a membership lookup, no try/except as control flow). Deterministic + total, supports DENY-1's independent cases.

## Question 3 — The permission matrix representation
How is the role→permission policy stored?

A) **A module-level immutable `dict[Role, frozenset[str]]`** (`PERMISSION_MATRIX`), the **single policy datum**;
   `authorize` does `rbac_action in PERMISSION_MATRIX.get(role, frozenset())`. Immutability (frozenset + never mutated)
   supports determinism (DET-1) and keeps one source of truth. **Recommended.**
B) Per-role methods / hardcoded `if role == …` branches (rejected — scatters the policy; MATRIX-1 exhaustiveness harder
   to guarantee).
C) An external policy engine / config file (rejected — over-engineered; no new dependency, tech-stack D7).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a module-level immutable dict[Role, frozenset[str]] (PERMISSION_MATRIX), the single policy datum; authorize does rbac_action in PERMISSION_MATRIX.get(role, frozenset()). Immutability supports determinism (DET-1) and one source of truth.

## Question 4 — The Protocol-conformance pattern (structural; NO production import of audit_store)
How does `AuthRBAC` satisfy audit-store's `@runtime_checkable Authorizer` for both the `isinstance` and call-shape
assertions — without coupling production code to audit-store?

A) **Duck-typed structural conformance**: `AuthRBAC` is a plain class defining exactly
   `def authorize(self, user_id: str, rbac_action: str) -> bool:`. It **does NOT inherit from / import** audit-store's
   `Authorizer` in **production** code — conformance is structural (the Protocol is `@runtime_checkable`), so
   `isinstance(AuthRBAC(...), Authorizer)` passes and the call-shape returns `bool`. The **`Authorizer` import +
   `isinstance` + call-shape assertions live ONLY in the PROTOCOL-1 test** (read-only) — exactly the reference-not-own
   posture `database`'s `fidelity_comparator` used (**no circular dependency**: `auth-rbac` production never imports
   `audit_store`). **Recommended.**
B) `class AuthRBAC(Authorizer)` explicitly subclassing the Protocol (rejected — forces a **production** import of
   `audit_store` into `auth-rbac`, creating a production cross-dependency the duck-typed approach avoids).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — duck-typed structural conformance: AuthRBAC is a plain class defining exactly authorize(self, user_id: str, rbac_action: str) -> bool. It does NOT inherit from/import audit-store's Authorizer in production code — conformance is structural (@runtime_checkable). The Authorizer import + isinstance + call-shape assertions live ONLY in the PROTOCOL-1 test (read-only) — the same reference-not-own posture database's fidelity_comparator used. No circular dependency.

## Question 5 — The delegation pattern for the API-layer guard (makes SSOT-1's stub test meaningful)
How is `ApiAuthGuard` structured so it provably holds no independent policy?

A) **Constructor-injected single `AuthRBAC`**: `ApiAuthGuard(authz: AuthRBAC)` stores the instance; its only decision
   logic is `return self._authz.authorize(user_id, rbac_action_for_endpoint)`. It holds **no `Role`/matrix data** and
   makes **no** role comparison of its own. This is exactly what makes the **delegation-via-injected-stub** test
   meaningful — swap a stub `AuthRBAC` and the guard's decision follows it. **Recommended.**
B) The guard constructs its own `AuthRBAC` internally (rejected — no injection seam; the stub test can't swap it, and an
   inlined check could hide).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — constructor-injected single AuthRBAC: ApiAuthGuard(authz: AuthRBAC) stores the instance; its only decision logic is return self._authz.authorize(user_id, rbac_action_for_endpoint). It holds no Role/matrix data and makes no role comparison of its own — exactly what makes the delegation-via-injected-stub test meaningful.

## Question 6 — The signature-constraint pattern (BIAS-1 structural)
How do the type signatures structurally exclude a demographic-shaped parameter?

A) **Explicit narrow signatures**: `authorize(self, user_id: str, rbac_action: str) -> bool` and
   `UserRoleRepository.get_role(user_id: str) -> str | None` — **no method in the authz path accepts** an
   `ApplicantProfile` / `Demographics` / any demographic type. Verifiable by `inspect.signature` (the BIAS-1 structural
   assertion). No demographic value can enter the decision. **Recommended.**
B) Accept a broader context object and "just don't read" demographics from it (rejected — weakens the structural
   guarantee; a demographic field could then enter).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — explicit narrow signatures: authorize(self, user_id: str, rbac_action: str) -> bool and UserRoleRepository.get_role(user_id: str) -> str | None — no method in the authz path accepts an ApplicantProfile/Demographics/any demographic type. Verifiable by inspect.signature. No demographic value can enter the decision.

## Question 7 — The pure-function pattern (DET-1)
How is `authorize` kept a pure, deterministic function?

A) **Pure function of (injected role read result, immutable matrix)** — **no** wall-clock, **no** RNG, **no** module-global
   mutable state (the matrix is an immutable `frozenset` dict; the repository is **injected**, not a global). Same inputs
   → same `bool`, every call. **Recommended.**
B) Allow a cached/memoized role map with mutation (rejected — introduces mutable state; determinism/testability cost for
   no Phase-1 benefit).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — pure function of (injected role read result, immutable matrix) — no wall-clock, no RNG, no module-global mutable state (the matrix is immutable frozenset; the repository is injected, not global). Same inputs → same bool, every call.

## Question 8 — The `UserRoleRepository` component (Protocol + fake + real adapter)
How is the role read model structured (per the §2.5 raw-`str | None` contract)?

A) **A `UserRoleRepository` Protocol** `get_role(user_id: str) -> str | None` (the raw contract) with **two
   implementations sharing the one Protocol**: an **in-memory fake** (dict-backed, unit tests — the primary substrate)
   and a **real Postgres-backed adapter stub** reading `app_user.role` (wired at Code-Gen; consumes `database`'s
   `app_user`, reference-not-own — asserts nothing about `database`'s schema). `AuthRBAC` depends on the **Protocol**
   (dependency inversion), never a concrete impl. Fake and real share the shape → **no drift**. **Recommended.**
B) A single concrete DB class, faked via monkeypatch (rejected — no clean Protocol seam; the audit-store fake-repository
   pattern is the established one).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a UserRoleRepository Protocol get_role(user_id: str) -> str | None (the raw contract) with two implementations sharing the one Protocol: an in-memory fake (dict-backed, unit tests, primary substrate) and a real Postgres-backed adapter stub reading app_user.role (wired at Code-Gen, consumes database's app_user, reference-not-own). AuthRBAC depends on the Protocol, never a concrete impl. Fake and real share the shape → no drift.

## Question 9 — Logical components (confirm the set)
Which components does this unit introduce?

A) **Six** (§3): C1 `AuthRBAC`, C2 `Role` enum, C3 `PERMISSION_MATRIX`, C4 `to_role` helper, C5 `UserRoleRepository`
   Protocol + fake + real adapter stub, C6 `ApiAuthGuard`. *(C4 `to_role` MAY fold into C1 as a private method — an
   allowed realization detail; the six-way split is the design view.)* **Recommended.**
B) Fewer — fold `to_role` + matrix into `AuthRBAC` and omit the guard from this unit's components (rejected — the guard
   is where SSOT-1 lives; it must be a named component).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — six components: C1 AuthRBAC, C2 Role enum, C3 PERMISSION_MATRIX, C4 to_role helper, C5 UserRoleRepository Protocol + fake + real adapter stub, C6 ApiAuthGuard. (C4 to_role may fold into C1 as a private method — an allowed realization detail; the six-way split is the design view.)

## Question 10 — Diagrams
What Mermaid do the artifacts include?

A) **Two validated Mermaid** (7-rule compliant + text alternatives, as every prior unit): a **pattern-integration**
   diagram (targets → patterns → the one `authorize` flow + the guard delegation) and a **component-relationship**
   diagram (C1–C6 + the read-only Protocol-in-test boundary). **Recommended.**
B) One diagram / none (rejected — comprehensive, invariant-bearing unit; two aids review like the prior units).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — two validated Mermaid (7-rule compliant + text alternatives): a pattern-integration diagram (targets → patterns → the one authorize flow + the guard delegation) and a component-relationship diagram (C1–C6 + the read-only Protocol-in-test boundary).

## Question 11 — Depth
What depth for this NFR Design stage?

A) **Comprehensive** — the full pattern set (each meeting its `NFR-AUTH-*` target) + the 6-component blueprint +
   reference-not-own check + both validated Mermaid, matching the unit's invariant weight. **Recommended.**
B) Standard / Minimal (rejected — invariant-bearing SEC-4 unit).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — comprehensive: the full pattern set (each meeting its NFR-AUTH-* target) + the 6-component blueprint + reference-not-own check + both validated Mermaid, matching the unit's invariant weight.

---

## 5. Constraints & settled items held (not re-opened)
- The **frozen FD** (incl. the §2.5 read-contract back-annotation) + the approved **`NFR-AUTH-*`** targets are the
  substrate — patterns/components realize them, re-opening neither.
- **No production import of `audit_store`** — conformance is duck-typed; the `Authorizer` Protocol import + `isinstance`
  live **only** in the PROTOCOL-1 test (reference-not-own; no circular dependency). **No audit-store file edited.**
- **`database`'s `app_user` consumed, not owned** — the real adapter reads the raw `role` via the Protocol; asserts
  nothing about `database`'s schema (that is `database`'s FIDELITY-1/MIGRATE-1).
- **SEC-4** fail-closed (one implementation covers all cases); **SSOT** (fold #2) realized by the injected-delegation
  guard; **CON-BR1** structural; **determinism** pure-function; **advisory-only**; **SEC-3** no credentials. **No LLM.**
- **Infrastructure Design** for `auth-rbac` remains **likely a logged SKIP** — decided at that stage.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code.

---

## 6. Next step (STOP here)
Fill the eleven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then generate the two `auth-rbac` NFR Design artifacts
(`nfr-design-patterns.md` + `logical-components.md`, each with a validated Mermaid + text alternative) and present the
standardized 2-option completion message. **No NFR-Design artifacts or code are generated until the answers are in and
checked.**
