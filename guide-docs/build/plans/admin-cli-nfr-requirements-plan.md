# NFR Requirements Plan (Part 1) — `admin-cli` (U17)

**Phase / Stage**: BUILD → NFR Requirements, **Part 1 (Planning)** (plan-then-generate; numbered `[Answer]` tags to fill)
**Loop position**: `admin-cli` (U17) — FD ✅ **APPROVED (Continue)** → **NFR Requirements Part 1 ← here.**
**Unit**: U17 `admin-cli` · **Date**: 2026-07-08 · **Depth**: **LIGHTER overall (CLI scaffolding) + FULL rigor on the two invariant-bearing mutations** (canonical-role sole gate — SEC-4; rulebook publish validate-then-append-only — FR-RULES-6/CON-DET-1) · Stories **US-ADMIN-1/2**.
**Status**: **Four `[Answer]` tags FILLED (all A); ambiguity-check CLEAN (three named checks resolved as folds ADMIN-NFR-Fold-1/2/3, §4A); Part 2 GENERATED** (`nfr-requirements.md` + `tech-stack-decisions.md`). This plan re-saved with the filled answers + resolved folds embedded (standing convention). STOPPED at the NFR-Requirements 2-option gate.

Built **ON** the frozen FD — **BR-ADMIN-1..9**, the module inventory (argparse entrypoint + `publish_rulebook`/`create_user`/`set_role` handlers + `RulebookPublisher` + `AppUserWriter`), the **injected-`Engine` seam**, the **sole-gate-vs-open-VARCHAR** analysis (ADMIN-Fold-1), the five locked answers (A/A/B/A/A), the three ADMIN-Folds (`guide-docs/build/admin-cli/functional-design/` + the FD plan) — **re-opening none**. Each BR-ADMIN maps to a **pass/fail-testable `NFR-ADMIN-*` target** at an explicit test tier.

---

## 1. What NFR Requirements produces (Part 2 preview — NOT generated yet)
- `nfr-requirements.md` — the finalized `NFR-ADMIN-*` targets (pass/fail assertions + acceptance criteria + tier + traceability to BR-ADMIN-* + Security-Guardrails table).
- `tech-stack-decisions.md` — the test/verification substrate decisions (argparse; tmp_path for publish file-IO; spy engine for the gate-before-SQL proof; testcontainers `@pytest.mark.integration` for the real `app_user` write + fault-injection; coverage omit for the pg-writer shim), each justified against a target; **no new production dependency**.

## 2. Test tiers (explicit — matching the auth-rbac/database precedent)

| Tier | Meaning | Runs in CI? |
|---|---|---|
| **U — unit / offline** | pure, no DB: publish file-IO over a **`tmp_path`** rulebook dir; the **canonical-role gate** proven with a **spy engine** (asserts `.execute` is **never** called on a non-canonical role); AST/import structural scans; no-secret-values; CLI-only scope; provider-deferred governance | **Yes** |
| **Integration — testcontainers `postgres:16`** (`@pytest.mark.integration`) | the **real** `app_user` INSERT/UPDATE + explicit "already exists"/"no such user" errors over a **test-only minimal `app_user`** (a test harness, NOT database's migration — SCOPE-1); the **fault-injection** "DB accepts a bad role via raw SQL" proof | **Yes in CI; auto-skipped locally without Docker** (mirrors auth-rbac `test_pg_adapter.py` + database conftest) |

> The `AppUserWriter`'s real-SQL shim is **omitted from unit-tier coverage** (like every `pg_repository.py`), while the **pure** role-gate + publisher + dispatch + error-mapping stay counted to **≥90%** (QA-6). Publish is pure file-IO → fully tier-U (no Docker).

---

## 3. BR-ADMIN → draft `NFR-ADMIN-*` target map (every rule mapped; no orphan)

| Target | BR | Draft pass/fail assertion | Tier | Rigor |
|---|---|---|---|---|
| **NFR-ADMIN-PUBLISH-1** | BR-ADMIN-1 | **(a)** a valid new `{version}.yaml` publishes + `load_rulebook(version)` succeeds; **(b) append-only teeth** — re-publishing an existing version is **rejected** with the existing file **unmodified** (byte-identical before/after); **(c)** a schema-invalid source is **rejected by `build_rulebook`** leaving **no** published file; **(d)** a declared-`rulebook_version` ≠ target is rejected | U (tmp_path) | full |
| **NFR-ADMIN-PUBVALID-1** | BR-ADMIN-2 | **structural** — the publish path imports + calls `build_rulebook`/`RulebookLoader`; **no** local rulebook schema / allowlist / threshold-shape / hasher in `backend/admin_cli/` | U (structural) | full |
| **NFR-ADMIN-CREATE-1** | BR-ADMIN-3 | real INSERT of `app_user(user_id, subject, role)` succeeds; a duplicate `user_id`/`subject` raises an **explicit "already exists"** error (UNIQUE violation surfaced, not a silent upsert) | Integration | standard |
| **NFR-ADMIN-SETROLE-1** | BR-ADMIN-4 | real UPDATE of `role WHERE user_id` changes the role; an **absent** user (0 rows) raises an **explicit "no such user"** error (not a silent no-op) | Integration | standard |
| **NFR-ADMIN-ROLEGATE-1** | BR-ADMIN-5 | **HIGHEST rigor — two parts:** **(a) gate-before-SQL** (tier U, spy engine) — a non-canonical role (`superuser`, `Admin`, blank) is **rejected before any SQL runs** (`.execute`/`.connect` **never called**); a canonical role passes the gate; **(b) sole-gate evidence** (Integration, fault-injection) — a **raw SQL** INSERT of a non-canonical role **directly** (bypassing `AppUserWriter`) is **accepted by the DB** (no error), proving the open-VARCHAR has no CHECK ⇒ admin-cli's gate is the SOLE enforcement (ADMIN-Fold-1) | U + Integration | **full** |
| **NFR-ADMIN-REFNOTOWN-1** | BR-ADMIN-6 | **structural** — no `database`/`auth_rbac` **production** import; no local DDL/CHECK; the write is a parameterized injected-`Engine` call; **non-vacuous self-test** flags a planted local re-implementation | U (structural) | full |
| **NFR-ADMIN-NOSECRET-1** | BR-ADMIN-7 | **structural** — no secret literal in `backend/admin_cli/`; command output / error messages contain **no** injected URL / credential VALUE (SEC-3) | U (structural) | full |
| **NFR-ADMIN-SCOPE-1** | BR-ADMIN-8 | **structural** — no LLM client / rule-evaluation / commit-service import; argparse CLI only (no admin UI) | U (structural) | standard |
| **NFR-ADMIN-PROVIDER-DEFER-1** | BR-ADMIN-9 | **governance/structural** — no `set-provider` command and no provider-config store exist in `backend/admin_cli/` (Q3-B deferral honored) | U (governance) | soft |

**No orphan** — BR-ADMIN-1..9 each map to a target.

---

## 4. Clarifying questions (fill each `[Answer]` tag; last option = Other)

These decide **NFR-tier realization** — they do **not** re-open the FD, the BR-ADMIN rules, the five answers, or the three ADMIN-Folds.

### Question 1 — `app_user`-write test substrate (NFR-ADMIN-CREATE-1 / SETROLE-1 / ROLEGATE-1(a))
How are the DB-touching write tests substrate-verified?
A) **Split by concern, matching the auth-rbac/database precedent**: the **pure** canonical-role gate is proven at **tier U with a spy engine** (records whether `.execute`/`.connect` was called → asserts **never** on a non-canonical role, no DB needed); the **real** INSERT/UPDATE + explicit "already exists"/"no such user" errors run at **`@pytest.mark.integration` testcontainers `postgres:16`** over a **test-only minimal `app_user`** (a test harness, NOT database's migration — SCOPE-1), auto-skipped locally without Docker, run in CI. **Recommended.**
B) **In-memory fake engine only** (no real Postgres) — lighter, but does not exercise real UNIQUE-violation / 0-rows-affected semantics, so the explicit-error teeth would be simulated, not real.
C) Other.

[Answer]: A

### Question 2 — Fault-injection "DB accepts a bad role" construction (NFR-ADMIN-ROLEGATE-1(b))
How is the sole-gate evidence built **without** weakening BR-ADMIN-5's gate?
A) A **testcontainers integration** test that INSERTs a non-canonical role via **raw SQL directly** (`conn.exec_driver_sql`), **bypassing `AppUserWriter` entirely**, and asserts the DB **accepts** it (no error) — proving the open-VARCHAR column has no CHECK (BR-DB-12) ⇒ admin-cli's pre-write gate is the sole enforcement. Because it **never** calls admin-cli's write path, it **cannot** weaken the gate — it characterizes the DB's permissiveness, which is exactly what makes the gate necessary. **Recommended.**
B) Insert the bad role **through `AppUserWriter`** with the gate disabled/mocked — **rejected** (mutating the unit-under-test's gate to prove a point about the DB is a false/weakening construction).
C) Other.

[Answer]: A

### Question 3 — Coverage architecture for the pg-writer (QA-6 fold)
How does the DB-touching code fold into the ≥90% root coverage?
A) **Split `AppUserWriter`**: a **pure** role-gate + validation module (unit-covered, counted) and a **thin SQL-exec shim** (the parameterized INSERT/UPDATE via the injected `Engine`) that is **omitted from unit-tier coverage** (added to `[tool.coverage.run].omit`, like every `*/pg_repository.py`), exercised at the integration tier. The pure gate + publisher + dispatch + error-mapping stay counted to **≥90%**. **Recommended.**
B) No split — count everything (would force the real SQL under unit coverage, needing Docker for the unit run — diverges from precedent). C) Other.

[Answer]: A

### Question 4 — CLI error-mapping / exit-code convention (NFR-ADMIN scaffolding — LIGHTER)
How do handler errors surface?
A) A small **typed-exception taxonomy** (`AdminCliError` base → `RulebookPublishError` / `UserWriteError` / `RoleValidationError`); handlers **raise typed**, the argparse entrypoint **maps them to a non-zero exit code + a human-readable stderr message** containing **no** secret VALUE; success → exit 0 + a status line (names only). Unit-tested at tier U (each error path → its exit code/message). **Recommended.**
B) Handlers print + `sys.exit` inline (no typed taxonomy) — harder to test discretely. C) Other.

[Answer]: A

---

## 5. Carried FD answers + folds (referenced, not re-derived — the substrate NFR builds on)
**Five locked answers (A/A/B/A/A):** Q1 admin-cli owns the `app_user` write via injected `Engine`, canonical-`Role`-validated before writing · Q2 publish = write `{version}.yaml` + validate-by-load (`build_rulebook`/`RulebookLoader`) + append-only refuse-overwrite + version==filename · Q3 provider-config management **deferred to P2** · Q4 argparse, `backend/admin_cli/` · Q5 create-user + set-role with explicit already-exists/no-such-user errors.
**Three ADMIN-Folds:** ADMIN-Fold-1 (the DB is open-VARCHAR/no-CHECK → admin-cli's pre-write `Role` gate is the SOLE enforcement) → drives **NFR-ADMIN-ROLEGATE-1**; ADMIN-Fold-2 (validate-then-append-only publish) → **NFR-ADMIN-PUBLISH-1**; ADMIN-Fold-3 (provider-config deferred, no store) → **NFR-ADMIN-PROVIDER-DEFER-1**.

### 4A. Newly-resolved NFR-tier folds (ambiguity-check — three named checks CLEAN, no genuine gap, no STOP)
Grounded on the SQLAlchemy 2.0 API + the auth-rbac/database test precedent on disk. No user-facing decision the FD + answers don't determine. Three determinate realizations:
- **ADMIN-NFR-Fold-1 — fault-injection isolation** *(check i)*: the ROLEGATE-1(b) raw-SQL insert runs **only** against the **disposable per-fixture `PostgresContainer("postgres:16")`** (ephemeral, random port, torn down via `eng.dispose()`), gated by `@pytest.mark.integration` + a `_docker_available()` skip, connected via the container's generated URL — **never** `DATABASE_URL` or a persistent/production-adjacent DB. Same isolation every prior unit's integration tier uses.
- **ADMIN-NFR-Fold-2 — spy asserts on `connect`/`begin`, not `.execute`** *(check ii)*: in **SQLAlchemy 2.0** the `Engine` exposes **no `.execute`** — the only Engine→DB entry points are `engine.connect()` and `engine.begin()` (`.execute` is on `Connection`). So the spy engine records **`connect()` and `begin()`** and asserts **neither** is called on a non-canonical role; the role gate runs **before** any connection is acquired — the true "no SQL touched the DB" boundary (tightens ROLEGATE-1(a); supersedes the Q1-A phrasing of ".execute/.connect").
- **ADMIN-NFR-Fold-3 — test-only `app_user` is a harness (SCOPE-1)** *(check iii)*: the integration fixture seeds its **own** minimal `app_user` (`user_id`/`subject`/`role`, **open VARCHAR, no CHECK** — faithful to the real column so the fault-injection is valid); it is **NOT** database's migration and **asserts nothing** about database's schema correctness (that is database's FIDELITY-1) — the exact auth-rbac `test_pg_adapter.py` posture. Reference-not-own preserved.

## 6. Settled items held (not re-opened)
The frozen FD (BR-ADMIN-1..9, the module inventory, the injected-`Engine` seam, the sole-gate analysis) is the substrate — NFR builds pass/fail targets **on** it. **Reference-not-own** — the four surfaces call-only, none edited; `build_rulebook` sole rulebook validator; `Role` sole canonical set; no schema/CHECK added. **Canonical-role sole gate** (SEC-4). **SEC-3** no secret VALUES. **Provider-config management deferred to P2.** **No LLM; no rule-eval; no decision/commit; no admin UI; WIRE-1 untouched; tier-B NOT authorized; no other unit started.**

## 7. Next step (STOP here — DONE)
Four answers filled (all A); ambiguity-check **CLEAN** (ADMIN-NFR-Fold-1/2/3, §4A); **Part 2 GENERATED** — `guide-docs/build/admin-cli/nfr-requirements/nfr-requirements.md` (ten `NFR-ADMIN-*` targets + acceptance criteria + tier + traceability to BR-ADMIN-1..9 + Security-Guardrails table) and `tech-stack-decisions.md` (D1–D11; argparse + spy-engine + testcontainers, **no new dependency**; coverage split like `pg_repository.py`; typed-exception taxonomy). This plan re-saved (standing convention). **STOPPED at the standardized NFR-Requirements 2-option gate (1. Request Changes / 2. Continue → NFR Design)** — did not advance. **WIRE-1 untouched; tier-B run NOT authorized; no other unit started.**
