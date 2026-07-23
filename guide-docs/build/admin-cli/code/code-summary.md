# Code Summary — `admin-cli` (U17)

**Stage**: BUILD → Code Generation (per-unit), **Part 2** · out-of-band admin CLI · **Depth**: LIGHTER overall + FULL rigor on the two invariant-bearing mutations
**Unit**: U17 `admin-cli` · **Date**: 2026-07-08 · Stories **US-ADMIN-1/2** · PER-3/6, FR-RULES-6.
**Built ON** the frozen FD + approved NFR-Req + approved NFR-Design (BR-ADMIN-1..9, ten `NFR-ADMIN-*`, P1–P6, C1–C6, nine carried folds + three ADMIN-NFRD-Folds + three ADMIN-CG-Folds) — re-opening none. TDD, leaf-first, per plan §3. Six answers all **A**.

---

## 1. Modules delivered (`backend/admin_cli/`)

| Component | Module | Coverage | Notes |
|---|---|---|---|
| C5 ExceptionTaxonomy | `exceptions.py` | **100%** | `AdminCliError`(1) → `RulebookPublishError`(2) / `UserWriteError`(3) / `RoleValidationError`(4); exit codes as class attrs |
| C3 RoleGate | `role_gate.py` | **100%** | pure `check(role)`; `role ∈ Role.value` (auth-rbac, call-only); rejects non-canonical/blank/None before any DB |
| C2 RulebookPublisher | `rulebook_publisher.py` | **100%** | pure-validate (`build_rulebook`, sole validator) → **atomic exclusive-create** `open(path,"x")` → validate-by-load (`RulebookLoader`) |
| C4 AppUserWriter | `app_user_writer.py` | **100%** | gate-first; parameterized INSERT/UPDATE; IntegrityError → "already exists"; `rowcount==0` → "no such user"; no upsert/no pre-SELECT |
| C4 (SQL shim) | `pg_writer.py` | **omitted** | the only `engine.begin()`+`execute` code; integration-tested, omitted like `pg_repository.py` |
| C1 ArgparseEntrypoint | `cli.py` | **100%** | `build_parser()` (3 subparsers) + injection-pure `main(argv,*,engine,rulebook_dir)`; typed-error → exit code + no-secret stderr |
| C1 (composition root) | `__main__.py` | **omitted** | builds injected `Engine` from `secrets_config` settings; only file allowed to import `secrets_config`/`create_engine` (ADMIN-CG-Fold-1); URL never printed |
| C6 StructuralGuard | `tests/test_reference_not_own.py` | `tests/` | AST scan (REFNOTOWN-1/NOSECRET-1/SCOPE-1/PROVIDER-DEFER-1) + non-vacuous self-tests |

Coverage wiring (`pyproject.toml`): added `--cov=backend/admin_cli`; omit `*/admin_cli/pg_writer.py` + `*/admin_cli/__main__.py`.

---

## 2. Test → target map (all ten `NFR-ADMIN-*`, at NFR-pinned tiers)

| Target | Test file · case(s) | Tier | Result |
|---|---|---|---|
| PUBLISH-1 | `test_rulebook_publisher.py` — valid publish+load; re-publish rejected + byte-identical; schema-invalid no-file; malformed-YAML no-file; declared-version mismatch | U | ✅ pass |
| PUBVALID-1 | `test_reference_not_own.py::test_publish_path_delegates_to_build_rulebook` + no-local-schema scan | U | ✅ pass |
| ROLEGATE-1 (a) | `test_app_user_writer.py` — non-canonical → `connect()`+`begin()` both **0 calls**; canonical reaches begin() | U (spy) | ✅ pass |
| ROLEGATE-1 (b) | `test_app_user_writer_integration.py::test_fault_injection_...` — raw SQL bad-role accepted by DB (bypasses writer) | Integration | ⏭️ skip (Docker; runs in CI) |
| CREATE-1 | `test_app_user_writer_integration.py` — INSERT+read-back; duplicate user_id / duplicate subject → "already exists" | Integration | ⏭️ skip (CI) |
| SETROLE-1 | `test_app_user_writer_integration.py` — UPDATE changes role; absent user → "no such user" | Integration | ⏭️ skip (CI) |
| REFNOTOWN-1 | `test_reference_not_own.py` — no forbidden prod import + non-vacuous self-test | U | ✅ pass |
| NOSECRET-1 | `test_reference_not_own.py` (no secret literal + self-test) + `test_cli.py::test_no_secret_value_in_any_output` | U | ✅ pass |
| SCOPE-1 | `test_reference_not_own.py` — no LLM/rule-eval/commit import | U | ✅ pass |
| CLIERR-1 | `test_cli.py` — each typed error → its exit code + no-secret stderr; success → exit 0 names-only; `test_exceptions.py` | U | ✅ pass |
| PROVIDER-DEFER-1 | `test_reference_not_own.py` — no `set-provider` literal / no provider store + self-test | U | ✅ pass |

The tier-U spy tests **also** exercise the result-interpretation branches (already-exists / no-such-user) without Docker, so the counted logic is fully covered; the **real** DB behaviour is the Integration tier's acceptance evidence.

---

## 3. Results

- **admin-cli alone**: **49 passed, 6 skipped** (the 6 = Docker-gated `@pytest.mark.integration`, auto-skipped without Docker; run in CI).
- **Full backend suite**: **850 passed, 31 skipped**; **coverage 99.82% ≥ 90% (QA-6 gate PASSED)**; admin-cli's counted modules all **100%**.
- **Pre-existing, NOT a regression**: 5 errors in `audit_store/tests/test_pg_integration.py` — `DockerException` because that unit's integration fixture (unlike auth-rbac/database/admin-cli) lacks a `_docker_available()` skip-guard, so it *errors* instead of *skips* when Docker is absent locally. These pass in CI (Docker present). admin-cli's own integration fixture uses the guard and skips cleanly.
- **ui-shell frontend** suite untouched (no file/`--cov` change on that track).

---

## 4. Holds honoured (verified)
- No production code edited in `rules-engine` / `auth-rbac` / `database` / `secrets-config` (call-only; structurally scanned).
- No local rulebook schema/hash/second validator — `build_rulebook`/`RulebookLoader` sole validator (PUBVALID-1 scan green).
- RoleGate distinct (C3), invoked FIRST by AppUserWriter — spy-test-enforced (`connect()`+`begin()` = 0 on non-canonical role).
- No schema/CHECK added to `app_user` (test-only harness DDL is a harness, ADMIN-NFR-Fold-3).
- Zero secret VALUES in output/logs (NOSECRET-1 scan + behavioural check green; `secrets_config` allowlisted to `__main__.py` only, per-file, ADMIN-CG-Fold-1).
- No LLM / rule-eval / commit-service import (SCOPE-1 scan green); no admin UI.
- Provider-config absent — no `set-provider`, no config store (PROVIDER-DEFER-1 scan green).
- **WIRE-1 untouched; tier-B run unauthorized + out of scope; no other unit started.**

## 5. Realization folds (ambiguity-check, all CLEAN)
- **ADMIN-CG-Fold-1** (check i): the C6 AST scan enforces the `secrets_config`/`create_engine` allowlist **per-file** (`__main__.py` only) — proven by `test_secrets_config_allowlist_is_scoped_to_main_only`.
- **ADMIN-CG-Fold-2** (check ii): `build_rulebook`'s raised messages (verified in `loader.py`) carry only field-validation detail + hashes — no credential/URL VALUE, no filesystem path in the post-write path — so `"rulebook validation failed: {loader_message}"` is safe; NOSECRET-1 is checked by no-secret-literal + no-URL-in-output, not a brittle blanket scan.
- **ADMIN-CG-Fold-3** (check iii): the harness's `subject NOT NULL UNIQUE` + open `role` VARCHAR is **required** — CREATE-1(b)'s duplicate-subject teeth depend on the constraint firing; the test asserts admin-cli's catch behaviour, not database's schema correctness (reference-not-own preserved).
