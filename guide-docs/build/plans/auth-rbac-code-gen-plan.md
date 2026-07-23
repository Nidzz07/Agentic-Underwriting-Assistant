# Code Generation Plan (Part 1) — `auth-rbac` (EPIC-6 / U11)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags, **TDD tests-first**)
**Loop position**: `auth-rbac` · FD ✅ (§2.5 back-annotated) · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure Design ✅ SKIPPED-logged 2026-07-07**
→ **Code Generation ← here (the LAST stage for `auth-rbac` — completes the SIXTH fully-complete unit).**
**Unit**: U11 `auth-rbac` · **Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: comprehensive.
**Status**: **Plan — awaiting `[Answer]:` tags. NO code generated this stage. Stop after this plan.**

This plan realizes the **6 approved NFR-Design components (C1–C6)** as code under `backend/auth_rbac/`, built **ON** the
frozen FD (incl. the §2.5 raw `str | None` read contract), the approved `NFR-AUTH-*` targets, and the NFR-Design
patterns — **re-opening none of them**. **TDD: every `NFR-AUTH-*` target gets its test first**, at the tier NFR Design
pinned (primarily unit). **No production import of `audit_store` or `database` anywhere** — structurally verified by a
test (fold 1). **No credentials** (SEC-3). **No LLM.**

---

## 1. What Code-Gen builds (and what it must NOT touch)

### 1.1 Builds — the 6 components as code + their tests
The pure-logic policy (`Role`, `PERMISSION_MATRIX`, `to_role`, `AuthRBAC.authorize`), the `UserRoleRepository` Protocol
+ in-memory fake + real Postgres adapter (consuming `database`'s `app_user` via its own query), and the `ApiAuthGuard`
delegation guard — each with its test at the NFR-pinned tier.

### 1.2 Does NOT touch (held closed)
- **audit-store's `seams.py` / `commit_service.py`** — conformance is **duck-typed**; the `Authorizer` Protocol is
  imported **read-only in the PROTOCOL-1 test only**; **never edited, never imported in production**.
- **`database`'s `app_user` migration/schema** — **consumed** (the real adapter reads `user_id`+`role` via its own
  query); **no schema/FIDELITY assertion** added (fold 3); no `database` module edited or imported in production.
- No consuming unit's business logic; no `PROJECT-BRIEF.md` / `user-journey.md` edits; the C5 UI facet + SSO (OOS-3)
  stay out of scope.

### 1.3 Guardrails held (skill)
SEC-4 fail-closed; CON-BR4 human gate (only `underwriter` reaches `commit`); CON-BR1 (no demographics in authz —
structural); advisory-only ("decision" not used for an authz result); SEC-3 (no credentials); **no production
`audit_store`/`database` import**; **no LLM.**

---

## 2. Module / package layout (`backend/auth_rbac/`) — C1–C6 mapping

```text
backend/auth_rbac/
├── __init__.py
├── roles.py            # C2 Role enum + C3 PERMISSION_MATRIX + C4 to_role  (see Q3 for split)
├── authorizer.py       # C1 AuthRBAC.authorize (the one FailClosedMatrixLookup)
├── repository.py       # C5 UserRoleRepository Protocol + InMemoryUserRoleRepository (fake)
├── pg_repository.py    # C5 real Postgres adapter (reads app_user.role; integration-covered; omit from unit cov)
├── api_guard.py        # C6 ApiAuthGuard (injected delegation; MAY route endpoint to rbac_action, MUST NOT decide)
└── tests/
    ├── __init__.py
    ├── test_roles.py                 # C2/C3/C4 — to_role totality (DENY ii/iii inputs), Role set, matrix shape
    ├── test_permission_matrix.py     # MATRIX-1 exhaustive cross-product + COMMIT-1
    ├── test_authorizer.py            # DENY-1 (four cases) + DET-1 + BIAS-1 (signature) + PERF-1 (observed)
    ├── test_protocol_conformance.py  # PROTOCOL-1 — read-only Authorizer import: isinstance + call-shape returns bool
    ├── test_api_guard.py             # SSOT-1 — stub AuthRBAC, both stub-True and stub-False directions
    ├── test_no_forbidden_imports.py  # fold 1 — structural: no from backend.audit_store / backend.database in production
    └── test_pg_adapter.py            # optional integration smoke (testcontainers) — reads a seeded app_user row
```

| Component | Module | Backs |
|---|---|---|
| **C1 AuthRBAC** | `authorizer.py` | DENY-1, MATRIX-1, COMMIT-1, PROTOCOL-1, BIAS-1, DET-1, PERF-1 |
| **C2 Role** | `roles.py` | MATRIX-1, COMMIT-1, DENY-1 |
| **C3 PERMISSION_MATRIX** | `roles.py` | MATRIX-1, COMMIT-1 |
| **C4 to_role** | `roles.py` | DENY-1 (ii)/(iii) |
| **C5 UserRoleRepository** | `repository.py` (Protocol + fake) + `pg_repository.py` (real) | DENY-1, consumption |
| **C6 ApiAuthGuard** | `api_guard.py` | SSOT-1 |

---

## 3. TDD test → target map (every `NFR-AUTH-*` at its NFR-pinned tier)

| Target | Test file / name | Tier | Assertion |
|---|---|---|---|
| **DENY-1** | `test_authorizer.py::test_deny_unknown_user / _noncanonical_role / _blank_role / _unlisted_action` | unit (fake) | four independent inputs → each `authorize == False` |
| **MATRIX-1** | `test_permission_matrix.py::test_full_cross_product` | unit (parametrized/Hypothesis) | every `Role × rbac_action` → defined `bool`, no exception/`None` |
| **COMMIT-1** | `test_permission_matrix.py::test_commit_only_underwriter` | unit | `commit` True only for `underwriter` |
| **PROTOCOL-1** | `test_protocol_conformance.py::test_isinstance_authorizer` + `::test_call_shape_returns_bool` | unit (read-only `Authorizer` import) | `isinstance(AuthRBAC(...), Authorizer)` True **AND** two-`str` call returns `bool` |
| **SSOT-1** | `test_api_guard.py::test_guard_tracks_stub_true` + `::test_guard_tracks_stub_false` | unit (stub) | guard output == stub output in **both** directions |
| **BIAS-1** | `test_authorizer.py::test_signature_excludes_demographics` + `::test_swap_invariance` | unit | `inspect.signature` params == `{user_id, rbac_action}`; no demographic-typed param; belt swap |
| **DET-1** | `test_authorizer.py::test_repeat_invariance` | unit | same inputs ×N → identical `bool`; no wall-clock/RNG/global |
| **PERF-1** | `test_authorizer.py::test_authorize_latency_observed` | observed | measured, printed, non-gating |
| **fold 1 (no import)** | `test_no_forbidden_imports.py::test_no_audit_store_or_database_import` | structural | no `from backend.audit_store` / `from backend.database` in `auth_rbac` production sources |
| **consumption smoke** | `test_pg_adapter.py::test_reads_seeded_app_user_role` | integration (optional) | real adapter reads a seeded `app_user` row; **asserts nothing about `database`'s schema** (fold 3) |
| **SCOPE-1** | — | **N/A (governance/exclusion)** | documented boundary, not a runtime test |
| **OBS-1** | — | **N/A** | observability-owned |

**No `NFR-AUTH-*` target is unmapped; no test invents a target the NFR Design didn't approve.** No test drives
audit-store's `commit_service` or asserts `database`'s schema (reference-not-own).

---

## 4. Implementation order (leaf-first, tests-first per step)

0. **Scaffold**: `backend/auth_rbac/__init__.py`, `tests/__init__.py`. Add `--cov=backend/auth_rbac` to `pyproject`
   `addopts`; omit `pg_repository.py` from unit cov (integration-only, like the other units' `pg_repository.py`) — Q6.
1. **C2 `Role`** enum + **C3 `PERMISSION_MATRIX`** — **test first** (`test_permission_matrix.py`: MATRIX-1 exhaustive +
   COMMIT-1; `Role` closed at app layer, DB stays open).
2. **C4 `to_role`** — **test first** (`test_roles.py`: totality — `None`/blank/non-canonical → `None`; canonical → member).
3. **C1 `AuthRBAC.authorize`** — the one linear fail-closed flow. **Test first** (`test_authorizer.py`: DENY-1 four
   cases via the fake + DET-1 + BIAS-1 signature + PERF-1 observed).
4. **C5 `UserRoleRepository` Protocol + `InMemoryUserRoleRepository` fake** — the raw `str | None` contract. **Test
   first** (fake used by steps 3/5's tests).
5. **C6 `ApiAuthGuard`** — injected delegation; MAY route endpoint→`rbac_action`, MUST NOT decide. **Test first**
   (`test_api_guard.py`: SSOT-1 stub, both directions).
6. **C5 real Postgres adapter** (`pg_repository.py`) — reads `app_user.role` via its **own** query (no `database`
   import, no schema assertion — fold 3). **Test first** (`test_pg_adapter.py`: optional integration smoke).
7. **PROTOCOL-1 test** (`test_protocol_conformance.py`) — **read-only** `Authorizer` import; `isinstance` + call-shape.
8. **fold-1 structural test** (`test_no_forbidden_imports.py`) — assert **no** `from backend.audit_store` /
   `from backend.database` in any `auth_rbac` production source (scan the package sources, excluding `tests/`).
9. **Coverage gate** — full backend suite; `backend/auth_rbac` source ≥90% (QA-6); `pg_repository.py` handled per Q6.
   Refresh `testresults.txt`.
10. **Code summary** — `guide-docs/build/auth-rbac/code/code-summary.md` (module list + test→target map + any flagged
    realization notes) + back-annotate guide-state.md; completion + 2-option gate.

---

## 5. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide
**Code-Gen realization** — they do **not** re-open the FD, the NFR targets, or the patterns.

## Question 1 — Test framework
What drives the tests?

A) **pytest** (established) + **Hypothesis** (already in the stack) for the MATRIX-1 exhaustiveness over the finite
   `Role × rbac_action` grid; parametrized tests elsewhere. **No new dependency.** **Recommended.**
B) pytest only, no Hypothesis (acceptable — a parametrized cross-product also covers MATRIX-1; Hypothesis just adds a
   property flavor).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — pytest (established) + Hypothesis (already in the stack) for MATRIX-1 exhaustiveness over the finite Role × rbac_action grid; parametrized tests elsewhere. No new dependency.

## Question 2 — The real Postgres adapter's query shape (consume `app_user`, no schema assertion)
How does `pg_repository.py` read the role?

A) **A minimal read-only query** — `SELECT role FROM app_user WHERE user_id = :user_id` (parameterized), returning the
   scalar `role` string or `None` (`scalar_one_or_none`), via a SQLAlchemy `Engine` **injected** at construction. It
   uses **its own** minimal statement (raw `text()` or a locally-declared `sa.Table("app_user", …)` with only
   `user_id`/`role`) — **imports no `database` / `audit_store` module**, adds **no schema/FIDELITY assertion** (fold 3),
   asserts nothing about `database`'s schema. **Recommended.**
B) Import a Table definition from `database` (rejected — `database` exposes no `app_user` Python Table; and importing
   one would create a production cross-dependency — reference-not-own violation).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a minimal read-only query: SELECT role FROM app_user WHERE user_id = :user_id (parameterized), returning the scalar role string or None, via a SQLAlchemy Engine injected at construction. Uses its own minimal statement (raw text() or a locally-declared sa.Table with only user_id/role) — imports no database/audit_store module, adds no schema/FIDELITY assertion, asserts nothing about database's schema.

## Question 3 — Module placement of `Role` / `PERMISSION_MATRIX` / `to_role`
One module or split?

A) **One `roles.py`** holding `Role` (enum), `PERMISSION_MATRIX` (immutable `dict[Role, frozenset[str]]`), and `to_role`
   (total helper) — they are small, cohesive, and co-evolve; `authorizer.py` imports from it. C4 MAY also be a private
   method of `AuthRBAC` (allowed realization detail), but a module-level `to_role` keeps it independently unit-testable.
   **Recommended.**
B) Split into `role.py` / `matrix.py` / `canonicalize.py` (rejected — over-fragmented for three tiny cohesive items).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — one roles.py holding Role (enum), PERMISSION_MATRIX (immutable dict[Role, frozenset[str]]), and to_role (total helper) — small, cohesive, co-evolve; authorizer.py imports from it. C4 may also be a private method of AuthRBAC, but a module-level to_role keeps it independently unit-testable.

## Question 4 — The `ApiAuthGuard` scope in THIS unit (class vs concrete FastAPI routes)
What does `auth-rbac` Code-Gen build for C6?

A) **The framework-agnostic `ApiAuthGuard` class** — constructor-injected `AuthRBAC`; a method like
   `check(user_id, rbac_action) -> bool` / `require(user_id, rbac_action)` that **delegates only** to `authorize`
   (MAY accept/route an endpoint's required `rbac_action`, MUST NOT decide). The **concrete FastAPI dependency + route
   wiring** (which endpoint needs which `rbac_action`, HTTP 403 on deny) is the **app-assembly unit's** Code-Gen —
   `auth-rbac` ships the reusable guard + the SSOT-1 delegation guarantee. **Recommended.**
B) Build the full FastAPI app + routes here (rejected — the API app is the app-assembly unit; auth-rbac owns the policy
   + the reusable guard, not the whole HTTP surface).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — the framework-agnostic ApiAuthGuard class — constructor-injected AuthRBAC; a method like check(user_id, rbac_action) -> bool / require(user_id, rbac_action) that delegates only to authorize (MAY route an endpoint's required rbac_action, MUST NOT decide). The concrete FastAPI dependency + route wiring is the app-assembly unit's Code-Gen — auth-rbac ships the reusable guard + the SSOT-1 delegation guarantee.

## Question 5 — The fold-1 structural no-import test mechanism
How is "no production `audit_store`/`database` import" verified?

A) **A source-scan test** — enumerate the `auth_rbac` production `.py` files (the package, **excluding `tests/`**) and
   assert **none** contains a `from backend.audit_store` / `import backend.audit_store` (or `backend.database`)
   statement (AST parse, or a robust text/regex scan). Structurally verifies fold 1, not a claim. **Recommended.**
B) Only assert it in prose (rejected — the whole point is a structural check).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a source-scan test: enumerate the auth_rbac production .py files (excluding tests/) and assert none contains a from backend.audit_store / import backend.audit_store (or backend.database) statement (AST parse, or a robust text/regex scan). Structurally verifies fold 1, not a claim.

## Question 6 — Coverage config for the new package
How is `backend/auth_rbac` covered?

A) **Add `--cov=backend/auth_rbac` to `pyproject` `addopts`**; the pure-logic modules (`roles`, `authorizer`,
   `repository` fake, `api_guard`) are **unit-covered to ≥90% (QA-6)**; the **real `pg_repository.py`** (exercised only
   via the optional testcontainers smoke) is **omitted from unit-tier coverage** exactly like the other units'
   `pg_repository.py`/`parse_worker.py`. No coverage-threshold change. **Recommended.**
B) Leave coverage config untouched (rejected — the new package would be uncounted).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — add --cov=backend/auth_rbac to pyproject addopts; the pure-logic modules (roles, authorizer, repository fake, api_guard) are unit-covered to ≥90% (QA-6); the real pg_repository.py (exercised only via the optional testcontainers smoke) is omitted from unit-tier coverage exactly like the other units' pg_repository.py/parse_worker.py. No coverage-threshold change.

## Question 7 — Infrastructure layers (confirm N/A) + depth + completion artifacts
Confirm the N/A layers and the depth.

A) **Compute / Storage / Messaging / Networking / Deployment = N/A for `auth-rbac`** (Infrastructure Design
   SKIPPED-logged — pure-logic unit; storage is `database`'s, wiring is the app unit's, connection is `secrets-config`'s).
   **Comprehensive** Code-Gen: full TDD build of all 6 components + every `NFR-AUTH-*` test at its tier; a
   `guide-docs/build/auth-rbac/code/code-summary.md` (module list + test→target map + flagged notes); `testresults.txt`
   refreshed; guide-state.md back-annotated; then the standardized **2-option** completion gate. **Recommended.**
B) Minimal — skeleton only (rejected — invariant-bearing SEC-4 unit; the whole policy + guards must be real + tested).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — Compute/Storage/Messaging/Networking/Deployment = N/A for auth-rbac (Infrastructure Design SKIPPED-logged — pure-logic unit; storage is database's, wiring is the app unit's, connection is secrets-config's). Comprehensive Code-Gen: full TDD build of all 6 components + every NFR-AUTH-* test at its tier; a code-summary.md (module list + test→target map + flagged notes); testresults.txt refreshed; guide-state.md back-annotated; then the standardized 2-option completion gate.

---

## 6. SEC-3 / reference-not-own confirmation (explicit)
- **No credential VALUE appears anywhere** in the generated code — the real adapter takes an **injected `Engine`**; the
  connection URL is `secrets-config`'s (SEC-3). No `.env` value echoed.
- **No production import of `audit_store` or `database`** anywhere in `backend/auth_rbac/` — the `Authorizer` Protocol
  is imported **read-only in `test_protocol_conformance.py` only**; the real adapter reads `app_user` via its **own**
  query. **Structurally verified** by `test_no_forbidden_imports.py` (Q5). No `seams.py`/`commit_service.py`/`database`
  file edited. **No LLM.**

---

## 7. Constraints & settled items held (not re-opened)
- FD (incl. §2.5 raw `str | None` read contract) + approved `NFR-AUTH-*` + NFR-Design patterns/components (C1–C6) are the
  substrate — Code-Gen realizes them, re-opening none.
- **Reference-not-own**: duck-typed conformance (no production `audit_store` import; Protocol read-only in the test);
  `app_user` consumed via the read contract (no schema/FIDELITY assertion); composition-root wiring + FastAPI routes are
  the app-assembly unit's; UI facet + SSO (OOS-3) out of scope.
- **SEC-4** fail-closed; **CON-BR1** structural; **determinism**; **advisory-only**; **SEC-3** no credentials; **no
  LLM**. Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code.

---

## 8. Next step (STOP here)
Fill the seven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then generate the `auth-rbac` code **TDD tests-first, leaf-first** per §4,
run the suite, write the code summary, back-annotate guide-state.md, and present the standardized completion + 2-option
message. **No code is generated until the answers are in and checked.**
