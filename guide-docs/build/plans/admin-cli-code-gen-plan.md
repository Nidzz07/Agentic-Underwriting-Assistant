# Code Generation Plan (Part 1) — `admin-cli` (U17)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate; numbered `[Answer]` tags — **full text + options on disk**)
**Loop position**: `admin-cli` (U17) — FD ✅ · NFR Requirements ✅ · NFR Design ✅ · Infrastructure Design ⏭️ SKIPPED (logged) → **Code Generation Part 1 ← here** (the **last** stage for this unit).
**Unit**: U17 `admin-cli` · **Date**: 2026-07-08 · **Depth**: **LIGHTER overall (CLI scaffolding) + FULL rigor on the two invariant-bearing mutations** · Stories **US-ADMIN-1/2** · PER-3/6, FR-RULES-6.
**Status**: **DONE — six `[Answer]` tags FILLED (all A, §6); ambiguity-check RUN 2026-07-08 → CLEAN (three realization folds ADMIN-CG-Fold-1/2/3, §6A — no genuine gap, no STOP); Part 2 GENERATED + TESTED** (`backend/admin_cli/` — 49 passed / 6 integration-skipped; full suite 850 passed / coverage 99.82% ≥ 90% QA-6). Plan re-saved (standing convention). STOPPED at the Code-Generation 2-option completion gate.

Built **ON** the frozen FD (BR-ADMIN-1..9, module inventory, injected-`Engine` seam, sole-gate-vs-open-VARCHAR analysis), the approved **NFR Requirements** (ten `NFR-ADMIN-*` targets, tiers U/Integration, three ADMIN-NFR-Folds), and the approved **NFR Design** (P1–P6, C1–C6, three ADMIN-NFRD-Folds) — **re-opening none**. TDD per CLAUDE.md (test-first, no production code without a failing test).

---

## 1. Component → module map (concrete files under `backend/admin_cli/`)

Mirrors the realized per-unit convention (`corpus_generator`, `secrets_config`, `auth_rbac`): a `backend/<unit>/` package of small modules + a `tests/` subpackage; the engine-touching SQL shim isolated for coverage-omit exactly like `pg_repository.py`.

| Component | Module(s) | Responsibility | Coverage |
|---|---|---|---|
| **C5 · ExceptionTaxonomy** | `backend/admin_cli/exceptions.py` | `AdminCliError` base → `RulebookPublishError` / `UserWriteError` / `RoleValidationError`; each carries an intended **exit code** (class attr) | **counted** |
| **C3 · RoleGate** | `backend/admin_cli/role_gate.py` | pure `RoleGate.check(role) -> None` — validates `role ∈ Role.value` set (auth-rbac, call-only); raises `RoleValidationError` on non-canonical/blank/None; **no DB** | **counted** |
| **C2 · RulebookPublisher** | `backend/admin_cli/rulebook_publisher.py` | `publish(version, source) ` — pure-validate via `build_rulebook` → **atomic exclusive-create** write → validate-by-load via `RulebookLoader`; raises `RulebookPublishError` | **counted** |
| **C4 · AppUserWriter** | `backend/admin_cli/app_user_writer.py` (**counted**) + `backend/admin_cli/pg_writer.py` (**omitted**) | `app_user_writer.py`: `AppUserWriter.create_user(...)` / `.set_role(...)` — **invoke `RoleGate.check` FIRST**, build the parameterized statement, delegate exec to the shim, **interpret** the result (IntegrityError → "already exists"; `rowcount == 0` → "no such user"). `pg_writer.py`: the thin `engine.begin()`+`conn.execute(...)` round-trip (real DB) | **split** (interpretation counted; SQL-exec shim omitted, like `pg_repository.py`) |
| **C1 · ArgparseEntrypoint** | `backend/admin_cli/cli.py` (**counted**) + `backend/admin_cli/__main__.py` (**omitted**) | `cli.py`: `build_parser()` (three subparsers) + `main(argv, *, engine, rulebook_dir) -> int` — dispatch + typed-error → **exit code + no-secret stderr** + success → **exit 0 + names-only** status. `__main__.py`: thin composition root (`python -m backend.admin_cli`) — builds the real `Engine` + resolves the rulebook dir, calls `cli.main` | **split** (dispatch/mapping counted; composition-root entry omitted) |
| **C6 · StructuralGuard** | `backend/admin_cli/tests/test_reference_not_own.py` (+ inline `ast`-scan helpers) | AST scan of `backend/admin_cli/` for REFNOTOWN-1 / NOSECRET-1 / SCOPE-1 + PROVIDER-DEFER-1 absence + **non-vacuous self-tests** — mirrors `auth_rbac/tests/test_no_forbidden_imports.py` and `corpus_generator/tests/test_reference_not_own.py` | **`tests/`** (not production coverage) |

**Package scaffolding**: `backend/admin_cli/__init__.py`, `backend/admin_cli/tests/__init__.py`, `backend/admin_cli/tests/conftest.py` (integration fixtures — `_docker_available()` skip, `PostgresContainer("postgres:16")`, the test-only `app_user` harness DDL, `eng.dispose()` teardown).

---

## 2. TDD test → target map (every `NFR-ADMIN-*` at its NFR-pinned tier)

Test-first: each row's test is written to **fail**, then the module is implemented to green. Files under `backend/admin_cli/tests/`.

| Target | Test file · case | Asserts | Tier |
|---|---|---|---|
| **NFR-ADMIN-PUBLISH-1** | `test_rulebook_publisher.py` | (a) valid new `{version}.yaml` publishes + `RulebookLoader.load_rulebook(version)` succeeds; (b) **append-only teeth** — re-publish of an existing version **rejected** (`RulebookPublishError`) + existing file **byte-identical** before/after (hash both sides); (c) schema-invalid source **rejected by `build_rulebook`** with **no file left**; (d) declared `rulebook_version` ≠ target rejected | **U** (tmp_path) |
| **NFR-ADMIN-PUBVALID-1** | `test_reference_not_own.py` (+ `test_rulebook_publisher.py` asserts the call) | publisher **imports + calls** `build_rulebook`/`RulebookLoader`; **structural** — no local rulebook schema / allowlist / threshold-shape / hasher in `backend/admin_cli/` | **U (structural)** |
| **NFR-ADMIN-ROLEGATE-1 (a)** | `test_app_user_writer.py` · spy engine | non-canonical (`superuser`, `Admin`, `""`, `None`) → `RoleValidationError` and the **spy engine's `connect()` AND `begin()` are BOTH never called** (the reorder-guard, ADMIN-NFRD-Fold-1); canonical (`underwriter`/`auditor`/`admin`) passes the gate | **U** (spy) |
| **NFR-ADMIN-ROLEGATE-1 (b)** | `test_app_user_writer_integration.py` · fault-injection | a **raw SQL** INSERT of a non-canonical role via `conn.exec_driver_sql` (**bypassing `AppUserWriter`**) is **accepted by the DB** (no error) over the disposable testcontainers `app_user` — proving the open VARCHAR has no CHECK ⇒ the gate is the SOLE enforcement (ADMIN-Fold-1) | **Integration** |
| **NFR-ADMIN-CREATE-1** | `test_app_user_writer_integration.py` | (a) `INSERT` of `app_user(user_id, subject, role)` succeeds + reads back; (b) duplicate `user_id`/`subject` → `IntegrityError` caught → **`UserWriteError` "already exists"** (generic-but-accurate, ADMIN-NFRD-Fold-2) | **Integration** |
| **NFR-ADMIN-SETROLE-1** | `test_app_user_writer_integration.py` | (a) `UPDATE role WHERE user_id` on an existing user changes the role; (b) **`rowcount == 0`** (absent user) → **`UserWriteError` "no such user"** | **Integration** |
| **NFR-ADMIN-REFNOTOWN-1** | `test_reference_not_own.py` | AST scan: imports `build_rulebook`/`RulebookLoader` + `auth_rbac.roles.Role` (call-only) only; **no** `database`/`auth_rbac` production **write** import; **no** local `hashlib`/rulebook-schema; **no** DDL/CHECK; **non-vacuous self-test** flags a planted re-implementation | **U (structural)** |
| **NFR-ADMIN-NOSECRET-1** | `test_reference_not_own.py` (+ `test_cli.py`) | AST/string scan: **no secret literal** in the package; `test_cli.py` asserts error/stderr + status lines carry **no** URL/credential VALUE (names/status only); **non-vacuous self-test** flags a planted secret literal | **U (structural)** |
| **NFR-ADMIN-SCOPE-1** | `test_reference_not_own.py` | AST scan: **no** LLM client / rule-evaluation / commit-service import; **no** admin UI; **non-vacuous self-test** | **U (structural)** |
| **NFR-ADMIN-CLIERR-1** | `test_cli.py` | `main(argv, ...)`: each typed error → its **non-zero exit code** + a no-secret stderr message; success → **exit 0** + a names-only status line; the taxonomy base/subclasses in `test_exceptions.py` | **U** |
| **NFR-ADMIN-PROVIDER-DEFER-1** | `test_reference_not_own.py` | **governance/structural** — no `set-provider` subparser and no provider-config store module exist in `backend/admin_cli/` | **U (structural/governance)** |

---

## 3. Leaf-first build order (matching the established convention)

1. **C5 · `exceptions.py`** (no deps) — write `test_exceptions.py` → implement the taxonomy + exit-code attrs.
2. **C3 · `role_gate.py`** (deps: `auth_rbac.roles.Role`) — `test_role_gate.py` → implement the pure gate.
3. **C2 · `rulebook_publisher.py`** (deps: `rules_engine.loader.build_rulebook`/`RulebookLoader` + C5) — `test_rulebook_publisher.py` (tmp_path) → implement pure-validate → atomic exclusive-create → validate-by-load.
4. **C4 · `app_user_writer.py` + `pg_writer.py`** (deps: C3 + C5 + injected `Engine`) — `test_app_user_writer.py` (spy, tier U) + `test_app_user_writer_integration.py` (testcontainers) → implement gate-first + statement build + result interpretation (counted) and the SQL-exec shim (omitted).
5. **C1 · `cli.py` + `__main__.py`** (composes C2+C3+C4+C5) — `test_cli.py` → implement `build_parser` + `main` + error→exit mapping (counted) and the thin composition-root entry (omitted).
6. **C6 · `tests/test_reference_not_own.py`** (scans everything above) — the AST-scan guards + non-vacuous self-tests.
7. **Coverage / quality gate** — run the full root suite; confirm `backend/admin_cli` ≥90% (QA-6) with the two shims omitted; confirm no regression of the existing backend suite.

---

## 4. Explicit HOLDS (restated — enforced through Code-Gen)
- **No production code edited** in any of the four consumed surfaces — `rules-engine`, `auth-rbac`, `database`, `secrets-config`. admin-cli **imports/calls** `build_rulebook`/`RulebookLoader` + `Role` (call-only); the composition-root engine construction (Q3) reads `secrets-config` settings **only** to build the injected `Engine`, editing nothing.
- **No local rulebook schema / hash / second validator** — `build_rulebook`/`RulebookLoader` is the **sole** validator (PUBVALID-1; structurally scanned).
- **RoleGate stays a distinct component invoked FIRST by `AppUserWriter`** — the structural sole-gate property (ROLEGATE-1), **spy-test-enforced** (`connect()`/`begin()` both never called on a non-canonical role; ADMIN-NFRD-Fold-1).
- **No schema / CHECK added to `app_user`** — `database` owns the schema; `role` stays open VARCHAR (BR-DB-12); the test-only `app_user` is a **harness** (ADMIN-NFR-Fold-3), not `database`'s migration.
- **Zero secret VALUES** in output/logs (NOSECRET-1 / SEC-3) — no secret literal; injected `Engine`/URL; names/status-only messages.
- **No LLM / rule-eval / commit-service import** (SCOPE-1); **no admin UI**.
- **Provider-config management stays absent** — no `set-provider` command, no config store (PROVIDER-DEFER-1 / BR-ADMIN-9).
- **WIRE-1 untouched; tier-B run stays unauthorized and out of scope; no other unit started.**

---

## 5. Coverage / quality gate (QA-6)
- Add `--cov=backend/admin_cli` to `[tool.pytest.ini_options].addopts`; the unit folds into the existing **root pytest run** with the global `--cov-fail-under=90`.
- Add to `[tool.coverage.run].omit`: **`*/admin_cli/pg_writer.py`** (SQL-exec shim — exercised via testcontainers integration, not unit-import-covered, exactly like `*/pg_repository.py`) and **`*/admin_cli/__main__.py`** (composition-root entry — like the other entrypoint omits). The **pure** role-gate + publisher + dispatch + error-mapping + exception taxonomy stay **counted to ≥90%**.
- **No regression**: the current backend suite baseline is **828 passed / 3 skipped** (the 3 skipped = Docker-gated `integration` tests, auto-skipped without Docker locally; run in CI). admin-cli's new tier-U tests must keep the local suite green and raise the pass count; the new `@pytest.mark.integration` tests join the CI Docker-gated set. **`ui-shell`'s frontend suite is untouched** (separate track; no `--cov` or file change there).

---

## 6. Clarifying questions (fill each `[Answer]` tag; last option = Other)

These are **Code-Gen-only realization choices** — they do **not** re-open the FD, the BR-ADMIN rules, the ten `NFR-ADMIN-*` targets, the six folds, or the P1–P6 / C1–C6 design.

### Question 1 — argparse subparser structure — C1 / `cli.py`
How is the argparse CLI structured?
A) **One `build_parser()` with three subparsers** (`publish-rulebook` / `create-user` / `set-role`), each binding a `set_defaults(handler=...)` to a small per-subcommand handler function; `main(argv, *, engine, rulebook_dir) -> int` parses, dispatches to the handler, and wraps the call in the typed-error → exit-code mapping. Fully unit-testable by calling `main` with an injected fake engine + `tmp_path` rulebook dir (no `os`/process needed). **Recommended** (mirrors the stdlib-argparse convention; testable).
B) A single flat parser with a positional `command` string + manual `if/elif` dispatch — less idiomatic, harder to extend, no subparser help.
C) Other.

[Answer]: A

### Question 2 — atomic exclusive-create realization — C2 / `rulebook_publisher.py` (ADMIN-NFRD-Fold-3)
How is the no-overwrite guard realized atomically?
A) **Python's `open(path, "x")` mode** (exclusive creation) — raises `FileExistsError` if the version exists (caught → `RulebookPublishError`), never opens the existing file for writing; one portable, race-free call. **Recommended** (simplest; stdlib; cross-platform).
B) **`os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)`** then wrap the fd — equivalent atomicity, but more low-level machinery than the CLI needs.
C) Other.

[Answer]: A

### Question 3 — composition-root `Engine` construction for `python -m backend.admin_cli` — C1 / `__main__.py`
When admin-cli runs standalone, where does the real injected `Engine` come from (given the FD says the engine is *injected*, admin-cli reads *no secret VALUE*, and `cli.main` takes `engine` as a parameter)?
A) **`__main__.py` is admin-cli's thin composition root** — it calls `secrets_config.get_settings()`, builds `sqlalchemy.create_engine(settings.DATABASE_URL)`, resolves the rulebook dir, and calls `cli.main(argv, engine=..., rulebook_dir=...)`. The URL value flows **opaquely** from settings into `create_engine` and is **never printed/logged** (SEC-3 preserved: **no secret LITERAL** in source, **no VALUE** echoed). `__main__.py` is **omitted from unit coverage** (composition-root entry) and the **structural-scan allowlist** permits `secrets_config.get_settings` + `sqlalchemy.create_engine` **in `__main__.py` only** (the rest of the package stays free of `secrets_config`/engine construction; `cli.py` and below receive the injected engine). **Recommended** (the only way a standalone CLI can self-wire; keeps `cli.main` and the writers injection-pure + fully testable). 
B) admin-cli **never** self-wires — an external runner outside `backend/admin_cli/` always injects the engine — but no such external runner exists for an out-of-band CLI, so this leaves `python -m backend.admin_cli` non-functional.
C) Other.

[Answer]: A

### Question 4 — exact stderr / status message wording (names-only, no secret) — C1 / C5 (NOSECRET-1 / CLIERR-1)
What exact messages does the entrypoint emit (all names/status only, never a secret VALUE)?
A) **A small fixed message table**, e.g. success → `published rulebook {version}` / `created user {user_id} ({role})` / `set role for {user_id} -> {role}` (exit 0); errors → `error: rulebook version {version} already exists` / `error: rulebook validation failed: {loader_message}` / `error: user {user_id} already exists` / `error: no such user {user_id}` / `error: invalid role {role!r}` (non-zero exit). Only `version`/`user_id`/`role`/`subject` names + the loader's own message interpolated — **never** a URL/credential. **Recommended** (confirm/adjust the wording now; Part 2 uses it verbatim). 
B) Leave wording entirely to Part 2 implementation discretion (still no-secret) — less reviewable.
C) Other.

[Answer]: A

### Question 5 — test-only minimal `app_user` DDL for the integration fixture — `tests/conftest.py` (ADMIN-NFR-Fold-3, SCOPE-1)
What DDL does the integration fixture seed (a **harness**, not `database`'s migration)?
A) **`CREATE TABLE app_user (user_id VARCHAR PRIMARY KEY, subject VARCHAR NOT NULL UNIQUE, role VARCHAR NOT NULL)`** — **open VARCHAR, NO CHECK** on `role`, mirroring the real column's openness (`0001_initial_schema.sql:51-57`) so the fault-injection (ROLEGATE-1(b)) is faithful and the duplicate-`user_id`/duplicate-`subject` teeth (CREATE-1) are exercised. It **asserts nothing** about `database`'s schema correctness (that is `database`'s FIDELITY-1); exact `auth_rbac/tests/test_pg_adapter.py` posture. **Recommended.**
B) Reuse/apply `database`'s real `0001_initial_schema.sql` migration in the fixture — couples admin-cli's tests to `database`'s full schema (audit tables etc.), breaking the reference-not-own harness posture.
C) Other.

[Answer]: A

### Question 6 — `AppUserWriter` / `pg_writer` boundary — C4 (D9 omit pattern)
How is the counted-vs-omitted split realized so the SQL-exec shim is cleanly omittable (like `pg_repository.py`)?
A) **Separate `pg_writer.py` composed by `AppUserWriter`** — `pg_writer.py` exposes the thin `engine.begin()`+`conn.execute(stmt, params) -> Result` round-trip (the only DB-touching code; **omitted** from coverage, integration-tested); `app_user_writer.py` holds the `RoleGate` + the `pg_writer`, invokes the gate **first**, builds the parameterized `sqlalchemy.text` statement, and interprets the returned `Result`/`IntegrityError` into typed errors (**counted**, spy-tested at tier U — the spy stands in for `pg_writer`'s engine so `connect()`/`begin()` are observable). **Recommended** (matches D9's `*/admin_cli/<pg-writer>.py` omit + the `pg_repository.py` precedent; keeps the gate-before-connect assertion crisp).
B) A single `app_user_writer.py` doing `engine.begin()`+`execute` inline — then the whole module must be omitted from coverage, losing unit coverage of the (pure) gate-ordering + error-mapping logic.
C) Other.

[Answer]: A

---

## 6A. Ambiguity-check (RUN 2026-07-08 against the six filled answers + frozen FD + NFR-Req + NFR-Design) — CLEAN
Grounded on `loader.py`'s actual raised messages, the `auth_rbac`/`database` integration precedent, and the SQLAlchemy 2.0 Engine API — all re-read on disk. **No genuine gap → no STOP.** Three realization folds:
- **ADMIN-CG-Fold-1 (check i — per-file allowlist is enforceable).** C6's AST scan visits each file **with its path**, so the `secrets_config`/`create_engine` allowlist is scoped to `__main__.py` **only** (not package-wide) — proven by `test_secrets_config_allowlist_is_scoped_to_main_only` (forbidden in `cli.py`, allowed in `__main__.py`). A `secrets_config` import in any other module is flagged.
- **ADMIN-CG-Fold-2 (check ii — loader messages are safe to interpolate).** Verified in `loader.py`: `build_rulebook` raises messages containing only field-validation detail + content hashes — **no credential/URL VALUE, no filesystem path** (a path appears only in `RulebookNotFoundError`, which cannot fire in the post-write validate-by-load step). So `"rulebook validation failed: {loader_message}"` leaks no secret. NOSECRET-1 is tested precisely (no secret-URL literal in source + no `postgresql://`/`password` in output), not a brittle blanket scan.
- **ADMIN-CG-Fold-3 (check iii — harness constraints are required, not redundant).** The test-only `app_user` DDL's `subject NOT NULL UNIQUE` + open `role` VARCHAR (no CHECK) is **required**: CREATE-1(b)'s duplicate-`subject` teeth depend on the DB constraint raising `IntegrityError`, which admin-cli catches → "already exists". The test asserts admin-cli's catch behaviour, **not** database's schema correctness (reference-not-own preserved; harness ≠ database's migration, ADMIN-NFR-Fold-3). auth-rbac's read-only harness omits the UNIQUE; admin-cli's write teeth need it.

## 7. Settled items held (not re-opened)
The frozen FD + approved NFR-Req + approved NFR-Design (BR-ADMIN-1..9, the ten `NFR-ADMIN-*` targets, P1–P6, C1–C6, the injected-`Engine` seam, the sole-gate analysis, the six carried folds + the three ADMIN-NFRD-Folds) is the substrate — Code-Gen realizes it. **Reference-not-own** — the four surfaces call-only, none edited; `build_rulebook` sole rulebook validator; `Role` sole canonical set; no schema/CHECK added. **Canonical-role sole gate** (SEC-4; RoleGate before `connect()`/`begin()`, spy-enforced). **SEC-3** no secret VALUES. **Provider-config management deferred to P2.** **No new production dependency** (argparse [stdlib], sqlalchemy, pytest, coverage, testcontainers all already present). **No LLM; no rule-eval; no decision/commit; no admin UI; WIRE-1 untouched; tier-B NOT authorized; no other unit started.**

## 8. Next step (STOPPED at the Code-Generation 2-option gate) — DONE
Six `[Answer]` tags filled (all A, §6); ambiguity-check RUN → **CLEAN** (§6A, three ADMIN-CG-Folds); **Part 2 GENERATED + TESTED**: `backend/admin_cli/` (`exceptions.py` / `role_gate.py` / `rulebook_publisher.py` / `app_user_writer.py` + omitted `pg_writer.py` / `cli.py` + omitted `__main__.py` / `tests/*`) + `pyproject.toml` coverage wiring. **admin-cli 49 passed / 6 integration-skipped; full backend suite 850 passed / 31 skipped; coverage 99.82% ≥ 90% (QA-6 PASSED); admin-cli counted modules all 100%.** Artifacts: `guide-docs/build/admin-cli/code/code-summary.md`, `testresults.txt`. 5 pre-existing `audit_store` Docker-absence errors (not a regression — see code-summary §3). **STOPPED at the standardized Code-Generation 2-option completion gate (1. Request Changes / 2. Continue to Next Stage) — did NOT advance. WIRE-1 untouched; tier-B run NOT authorized; no other unit started.**
