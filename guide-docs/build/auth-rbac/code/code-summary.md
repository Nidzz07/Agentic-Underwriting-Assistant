# Code Generation Summary — `auth-rbac` (EPIC-6 / U11)

**Stage**: BUILD → Code Generation, **Part 2 (Generation)** · **Date**: 2026-07-07
**Runtime**: Python **3.12.10** (pinned, D6) · **Depth**: comprehensive · **TDD**: tests-first, leaf-first.
**Result**: full backend suite **683 passed / 3 skipped** (the 3 `posix_only` intake tests on Windows dev);
**TOTAL coverage 99.75%** (QA-6 ≥90% reached). `auth_rbac` counted modules all **100%**; the integration smoke
actually executed (Docker up). This completes `auth-rbac` as the **SIXTH fully-complete unit** on approval.

---

## 1. Modules generated (`backend/auth_rbac/`)

| File | Component | Role |
|---|---|---|
| `__init__.py` | — | package doc + boundary statement (no `audit_store`/`database` production import; SEC-3; no LLM) |
| `roles.py` | **C2 + C3 + C4** | `Role` enum (closed at app layer), `PERMISSION_MATRIX` (immutable `dict[Role, frozenset]`), `to_role` (total canonicalization + fail-close), the `rbac_action` vocabulary (`RBAC_COMMIT="commit"` by contract) |
| `authorizer.py` | **C1** | `AuthRBAC.authorize` — the one linear fail-closed flow (`get_role → to_role → role is None ? False : action ∈ matrix`) |
| `repository.py` | **C5** | `UserRoleRepository` Protocol (`get_role -> str | None`, raw) + `InMemoryUserRoleRepository` fake |
| `pg_repository.py` | **C5** | `PostgresUserRoleRepository` — injected `Engine`, parameterized `SELECT role FROM app_user WHERE user_id`, no forbidden import, no schema assertion (integration-covered; omitted from unit cov) |
| `api_guard.py` | **C6** | `ApiAuthGuard.check(user_id, rbac_action) -> bool` — pure delegation to the one `AuthRBAC` |
| `tests/` | — | 8 test modules (84 tests) |

---

## 2. TDD test → `NFR-AUTH-*` target map (all PASSED)

| Target | Test(s) | Tier |
|---|---|---|
| **DENY-1** | `test_authorizer.py::test_deny_unknown_user / test_deny_noncanonical_role / test_deny_blank_role[×3] / test_deny_unlisted_action_for_valid_role` | unit (fake) |
| **MATRIX-1** | `test_permission_matrix.py::test_full_cross_product_defined_bool[18] / ::test_matrix_membership_is_total_hypothesis / ::test_every_role_has_a_matrix_entry`; `test_authorizer.py::test_authorize_matches_matrix_for_every_grid_cell[18]` | unit (parametrized + Hypothesis) |
| **COMMIT-1** | `test_permission_matrix.py::test_commit_only_underwriter`; `test_authorizer.py::test_commit_true_only_for_underwriter_via_authorize` | unit |
| **PROTOCOL-1** | `test_protocol_conformance.py::test_isinstance_authorizer_structural_presence` **+** `::test_call_shape_returns_bool` (two-assertion) | unit (read-only `Authorizer` import) |
| **SSOT-1** | `test_api_guard.py::test_guard_tracks_stub_true / ::test_guard_tracks_stub_false / ::test_guard_output_equals_authorize_exactly_both_directions / ::test_guard_holds_no_role_or_matrix_data_of_its_own` | unit (stub) |
| **BIAS-1** | `test_authorizer.py::test_authorize_signature_is_exactly_user_id_and_rbac_action / ::test_swap_invariance_demographics_not_an_input`; `test_repository.py::test_get_role_signature_reads_only_user_id` | unit |
| **DET-1** | `test_authorizer.py::test_repeat_invariance`; `test_roles.py::test_to_role_is_total_and_deterministic` | unit |
| **PERF-1** | `test_authorizer.py::test_authorize_latency_observed` | observed |
| **fold-1 no-import** | `test_no_forbidden_imports.py::test_no_audit_store_or_database_import` **+** `::test_scan_sees_the_real_production_modules` **+** `::test_scanner_detects_a_forbidden_import` | structural |
| **consumption smoke** | `test_pg_adapter.py::test_reads_seeded_app_user_role` | integration (Docker) |
| **SCOPE-1** | — | N/A (governance/exclusion — documented boundary) |
| **OBS-1** | — | N/A (observability-owned) |

No target unmapped; no test drives audit-store's `commit_service` or asserts `database`'s schema.

---

## 3. Coverage

`auth_rbac` counted modules (unit tier): `__init__.py`, `roles.py`, `authorizer.py`, `repository.py`, `api_guard.py`
— **all 100%**. `pg_repository.py` is **omitted from unit-tier coverage** by the existing `*/pg_repository.py` glob
(integration-covered via the testcontainers smoke, like every unit's `pg_repository.py`). `--cov=backend/auth_rbac`
added to `addopts`; **no coverage-threshold change**. TOTAL 99.75%.

---

## 4. Reference-not-own / fold-1 verification (structural, not claimed)

- **No production import of `audit_store` or `database`** anywhere in `backend/auth_rbac/` — proven by
  `test_no_forbidden_imports.py` (AST parse of every production `.py`, excluding `tests/`), with a **non-vacuous guard**
  (`test_scan_sees_the_real_production_modules` — the at-risk modules incl. `pg_repository.py` are in the scanned set)
  and a **self-test** (`test_scanner_detects_a_forbidden_import` — proves the detector flags a synthetic
  `from backend.database` / `import backend.audit_store`). The `Authorizer` Protocol import lives **only** in
  `test_protocol_conformance.py` (read-only, test).
- **Duck-typed conformance** — `AuthRBAC` does not inherit from / import `Authorizer`; `isinstance` (method presence) +
  the call-shape/return-`bool` assertion together prove PROTOCOL-1. `RBAC_COMMIT` value matched by contract (`"commit"`).
- **`app_user` consumed, not owned** — the real adapter reads raw `role` via its own parameterized query and adds **no**
  schema/FIDELITY assertion (SCOPE-1); the smoke seeds its own TEST-only `app_user`, asserting nothing about
  `database`'s migration. Fake + real share the one Protocol → no drift.
- **SSOT-1 (fold #2)** — `ApiAuthGuard.check` returns exactly `authorize(...)`; the guard holds only the injected policy
  (`test_guard_holds_no_role_or_matrix_data_of_its_own`); the stub test proves output tracks the stub in **both**
  directions. A raising `require()` is **documented-not-built** (must delegate if ever added).

---

## 5. SEC-3 / guardrails held (verified)

- **No credential VALUE anywhere** — the real adapter takes an **injected `Engine`**; the connection URL is
  `secrets-config`'s. **No LLM.** **CON-BR1** — `authorize` inputs are only `(user_id, rbac_action)` (structural
  BIAS-1). **SEC-4** fail-closed (four DENY cases). **Advisory-only** — "decision" not used for an authz result.
- **Reference-not-own** — no `audit_store`/`database` production import; audit-store's `seams.py`/`commit_service.py`
  and `database`'s `app_user` migration not edited.

---

## 6. Flagged realization notes (faithful; no frozen design re-opened)

1. **Leaf-first sequencing** — `repository.py` (the Protocol + fake leaf) was built immediately before `authorizer.py`
   (which depends on it and whose tests use the fake). A faithful ordering of §4 steps 3–4 (dependency before
   dependent); no design change.
2. **`to_role` exact-canonical match** — a wrong-case (`"Underwriter"`) or whitespace-padded (`" underwriter "`) value is
   treated as **non-canonical → `None`** (deny-safe), consistent with the FD's canonical set `{underwriter, auditor,
   admin}`. A realization choice within the frozen fail-close semantics, not a new behavior.

---

## 7. Artifacts
- Source + tests: `backend/auth_rbac/` (5 source modules + `tests/`).
- Tier-1 results: `testresults.txt` (repo root) — 683 passed / 3 skipped / 99.75%.
- This summary: `guide-docs/build/auth-rbac/code/code-summary.md`.
