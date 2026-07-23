# Tech-Stack Decisions — `admin-cli` (U17)

**Stage**: BUILD → NFR Requirements (per-unit) · **Depth**: LIGHTER overall + FULL rigor on the two invariant-bearing mutations.
**Unit**: U17 `admin-cli` · **Date**: 2026-07-08. Out-of-band rulebook-version + user/role management (no admin UI); US-ADMIN-1/2, PER-3/6, FR-RULES-6.
**Principle**: name only what makes the `NFR-ADMIN-*` targets **checkable**; consume the four frozen surfaces **call-only**; **introduce no new production dependency**. **No LLM; no rule-eval; no secret VALUES; no decision path.**

---

## Decisions

| # | Decision | Rationale / notes |
|---|---|---|
| **D1** | **Python 3.12 + pytest** (tiers U + Integration) | The backend-wide runtime + test runner; the `NFR-ADMIN-*` unit targets run here, offline, in CI. |
| **D2** | **CLI = stdlib `argparse`** (Q4-A) — **no new dependency** | `python -m backend.admin_cli <subcommand>` with `publish-rulebook` / `create-user` / `set-role`; no click/typer. Package `backend/admin_cli/`, folds into the root pytest run (`--cov=backend/admin_cli`). |
| **D3** | **Publish validation = `rules_engine.build_rulebook` / `RulebookLoader`** (call-only) | The **sole** rulebook validator (schema + hash + declared-version) — PUBLISH-1 / PUBVALID-1. Publish is pure **file-IO over `tmp_path`** at tier U (no Docker). |
| **D4** | **Canonical-role gate = `auth_rbac.roles.Role`** (call-only, single-sourced) | The gate validates `role ∈ Role` **before** any connection is acquired (ROLEGATE-1(a)); auto-agrees if the enum extends. No local role set. |
| **D5** | **`app_user` write = injected `sqlalchemy.Engine` + parameterized SQL** | `AppUserWriter(engine)` mirrors auth-rbac's `pg_repository.py`; no `database`/`auth_rbac` production import, no DDL/CHECK (REFNOTOWN-1). SEC-3: the URL/engine is injected, never a literal. |
| **D6** | **Spy engine for the gate-before-SQL proof** (ROLEGATE-1(a), ADMIN-NFR-Fold-2) | A test double whose **`connect()` and `begin()`** are recorded — the only Engine→DB entry points in **SQLAlchemy 2.0** (`Engine` has no `.execute`). A non-canonical role → **neither** called (no connection acquired → no SQL possible). Tier U, no Docker. |
| **D7** | **testcontainers `postgres:16`** (`@pytest.mark.integration`, Docker-gated) — **already used by auth-rbac/database, no new dependency** | The real INSERT/UPDATE + explicit already-exists/no-such-user errors (CREATE-1/SETROLE-1) + the fault-injection sole-gate proof (ROLEGATE-1(b)) run here. Disposable per-fixture container, `_docker_available()` skip, auto-skip local / run in CI (ADMIN-NFR-Fold-1). |
| **D8** | **Test-only minimal `app_user` harness** (ADMIN-NFR-Fold-3, SCOPE-1) | The integration fixture seeds its OWN `app_user (user_id VARCHAR PK, subject VARCHAR, role VARCHAR NOT NULL)` — **open VARCHAR, no CHECK** (faithful to the real column so the fault-injection is valid); it is **NOT** database's migration and asserts nothing about database's schema (that is database's FIDELITY-1). Exact auth-rbac `test_pg_adapter.py` posture. |
| **D9** | **Coverage: split pure vs SQL shim** (Q3-A) | The `AppUserWriter` real-SQL shim is **omitted from unit coverage** (`*/admin_cli/<pg-writer>.py` in `[tool.coverage.run].omit`, like every `*/pg_repository.py`); the **pure** role-gate + publisher + dispatch + error-mapping stay counted to **≥90%** (QA-6). |
| **D10** | **Typed-exception taxonomy** (Q4-A) | `AdminCliError` base → `RulebookPublishError` / `UserWriteError` / `RoleValidationError`; the entrypoint maps typed errors → non-zero exit + a **no-secret** stderr message; success → exit 0 + a names-only status line (CLIERR-1 / NOSECRET-1). |
| **D11** | **Structural guards (AST/import scan, self-tested)** | REFNOTOWN-1 / NOSECRET-1 / SCOPE-1 / PROVIDER-DEFER-1 — a stdlib-`ast` scan of `backend/admin_cli/` (no `database`/`auth_rbac` production import, no local hasher/rulebook-schema/DDL, no secret literal, no LLM/rule-eval/commit import, no `set-provider`); non-vacuous self-test. Mirrors the `corpus_generator`/`quality_gates` precedent. |

---

## Deferred / referenced (not decided here)
- **Provider-config management** → **deferred to Phase-2** (Q3-B); no `set-provider`, no config store; active provider a static composition-root value.
- **The composition root** that builds the injected `Engine` from `secrets-config`'s `DATABASE_URL` → the FastAPI/app wiring (not admin-cli's own code); admin-cli takes the engine as a parameter.
- **Concrete CLI arg names + stderr message wording + exact publish source format** → **Code-Gen** (still no secret VALUE, still validate-by-load).

**No new production dependency** beyond the already-declared backend stack (argparse [stdlib], pytest, coverage, sqlalchemy) + the already-present **testcontainers** test substrate (auth-rbac/database use it). **No LLM; no secret VALUES; no rule-eval; no decision path; WIRE-1 untouched.**
