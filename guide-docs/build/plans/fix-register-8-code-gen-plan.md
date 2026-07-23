# Register Item #8 — `DEPLOY-MIGRATE-DEFERRED` · CODE-GENERATION PLAN

**Stage**: POST-BUILD → register-item remediation → **code-gen plan** (follows `fix-register-8-plan.md`,
Q1–Q6 answered, ambiguity-check clean).
**Status**: 🟡 **PLANNING ONLY — NO CODE GENERATED YET.** Stopped at the plan-file gate for approval.
**Date**: 2026-07-22T18:05:11Z
**Answers driving this plan**: Q1 = **(b)** `backend/scripts/run_migrations.py` · Q2 = **(a)** both
sequences, U15→U24, owner engine, U24 via `apply_case_migrations()` · Q3 = **(a)** hardcoded, explicitly
named · Q4 = idempotency confirmed by construction + **(a)** fail-loud · Q5 = update `render.yaml`'s
`preDeployCommand` as this pass's own named edit · Q6 = **(c)** both tier-U + tier-I, ping-guard skip
confirmed.

**Ambiguity-check outcome (embedded from `fix-register-8-plan.md` §6 / audit)**: directed checks (i) and
(ii) CLEAN; (iii) literal-CLEAN with **one adjacent doc-consistency finding surfaced** (see §6 below) —
folded into this plan as explicitly-flagged scope, not silently absorbed.

---

## 0. Baseline — measured intent, carried forward (NOT re-run by this planning step)

| Metric | Baseline (pre-#8) |
|---|---|
| Backend passed | **1549** |
| Backend failed | **0** |
| Backend skipped | **40** |
| Backend errors | **5** (the pre-existing `audit_store` Docker-absence errors, by name) |
| Coverage | **99.87%** (`--cov-fail-under=90` held) |

⚑ This environment has **no Docker**, so all predictions below are for the **no-Docker local run** (the 5
errors and the integration skips are the no-Docker figure). CI-with-Docker additionally runs the new tier-I
test green (noted per step).

---

## 1. Component inventory

| # | Artifact | New/Edit | Frozen? | Purpose |
|---|---|---|---|---|
| C1 | `backend/scripts/run_migrations.py` | **NEW** | No (outside every scan root; outside `--cov`) | The deploy-time CLI entrypoint. Cross-unit orchestrator: applies U15 then U24 (guard-first) against the owner engine built from `get_settings()`. Fail-loud. Referenced by `render.yaml`'s `preDeployCommand`. |
| C2 | `backend/scripts/__init__.py` | **NEW** (empty) | No | Make `backend/scripts` a regular package so the new tests collect consistently with the rest of the suite. Trivial; existing scripts still run via `python -m`. |
| C3 | `backend/scripts/tests/__init__.py` | **NEW** (empty) | No | Test package marker (matches every other unit's `tests/` layout). |
| C4 | `backend/scripts/tests/test_run_migrations.py` | **NEW** | No | **tier-U** orchestration-contract test (no Docker): engine-from-settings, U15-before-U24 order, U24-via-`apply_case_migrations` (never a bare runner on U24's dir — C-C), fail-loud propagation. |
| C5 | `backend/scripts/tests/test_run_migrations_integration.py` | **NEW** | No | **tier-I** integration test (testcontainers, `@pytest.mark.integration`, `_docker_available()` ping-guard → clean skip): both sequences materialize on a fresh `postgres:16`; second run applies nothing. |
| C6 | `render.yaml` | **EDIT** (value + comment) | No (`is_under_frozen`→False; §1.6 of scoping plan) | `preDeployCommand` → `python -m backend.scripts.run_migrations`; update the lines 12–16 comment so it no longer says "not the runner / deferred deliverable." **Q5-authorized.** |
| C7 | `deploy/README.md` MIGRATION section | **EDIT** (prose) | No (`is_under_frozen`→False) | ⚑ **SURFACED adjacent finding (§6)** — update lines 54–58 so "Until it exists…" no longer contradicts the now-existing entrypoint. **BEYOND the literal Q5 answer — flagged for approval at this gate.** |
| C8 | `BUILD-COMPLETION-REPORT.md` + `guide-state.md` + `audit.md` | **EDIT** (register update) | No (docs) | Register-update section for #8 (NARROWED-vs-DISCHARGED per §7), on the #18/#19/#20 supersede-don't-rewrite precedent. |

**Frozen artifacts CALLED but never edited (C-A/C-B/C-C):** `MigrationRunner`, `migration_files`,
`apply_all` (`backend/database/migration_runner.py`); `apply_case_migrations`,
`assert_no_collision_with_database` (`backend/case_lifecycle/migrate.py`); all three `.sql` migration files;
`verify_checksums`. C1 only *constructs and invokes* them.

### 1.1 C1 — the entrypoint, designed concretely

```python
"""DEPLOY-TIME migration entrypoint — register #8 DEPLOY-MIGRATE-DEFERRED.

Applies BOTH forward-only migration sequences — database (U15) then case_lifecycle (U24) — to the
database named by DATABASE_URL, in order, BEFORE the app serves traffic. This is the runnable CLI
entrypoint render.yaml's preDeployCommand invokes.

⚑ A CROSS-UNIT ORCHESTRATOR, deliberately in backend/scripts/ (register #8 / Q1-B): it must drive
BOTH U15's runner AND U24's apply_case_migrations; homing it inside backend/database/ would make a
frozen unit's package import a later one. Built from get_settings() directly (no dependencies.py
Depends graph), route-free — the same out-of-band shape as seed_demo_cases.py / reconcile_committing_cases.py.

⚑ U24 is applied ONLY through apply_case_migrations() (C-C) — the sole sanctioned path, which runs the
PRODUCTION collision guard first. A bare MigrationRunner against U24's dir would bypass P-CASE-11.

⚑ IDEMPOTENT by construction: each runner records applied files in `applied_migrations` (bare
filename) and skips them on re-run — a redeploy applies nothing new. FAIL-LOUD (Q4-a): any error
propagates to a non-zero exit so Render's release step visibly fails BEFORE traffic. The rendered SQL
is NEVER logged (the grants file carries a substituted secret — SEC-3).

Run (deploy / out of band)::
    python -m backend.scripts.run_migrations
"""
from __future__ import annotations

import argparse

import sqlalchemy as sa

from backend.case_lifecycle.migrate import apply_case_migrations
from backend.database.migration_runner import MigrationRunner
from backend.secrets_config import get_settings


def apply_all_migrations(engine: sa.Engine) -> tuple[list[str], list[str]]:
    """Apply database (U15) then case_lifecycle (U24, guard-first). Returns (u15_newly, u24_newly).

    U24 goes through apply_case_migrations() — never a bare MigrationRunner on U24's dir (C-C).
    Idempotent (skip-if-applied). Fail-loud: any error propagates.
    """
    applied_db = MigrationRunner(engine).apply_all()          # U15: default MIGRATIONS_DIR
    applied_case = apply_case_migrations(engine)              # U24: guard-first, its own dir
    return applied_db, applied_case


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args(argv)
    engine = sa.create_engine(get_settings().DATABASE_URL)    # owner connection (#20-ratified)
    try:
        applied_db, applied_case = apply_all_migrations(engine)
    finally:
        engine.dispose()
    # NEVER log rendered SQL — only filenames/counts (SEC-3).
    print(f"migrations applied: database={applied_db} case_lifecycle={applied_case}")
    return 0


if __name__ == "__main__":  # pragma: no cover - deploy-time entrypoint
    raise SystemExit(main())
```

⚑ The `try/finally` disposes the engine but **does not swallow** — an exception raised inside
`apply_all_migrations` propagates out of `main` (fail-loud, Q4-a). `# pragma: no cover` on the `__main__`
guard mirrors the two existing scripts; **and the whole file is coverage-invisible regardless** because
`backend/scripts` is not a `--cov` target (§4).

---

## 2. TDD leaf-first execution order (RED → GREEN per step)

> Order per the user's instruction: **tier-U test first, then the entrypoint, then the tier-I test, then
> `render.yaml` last** (it depends on the entrypoint existing and working), then the flagged doc edit, then
> the register update.

### Step 0 — package scaffolding (C2, C3)
Add empty `backend/scripts/__init__.py` and `backend/scripts/tests/__init__.py`.
**Verify**: `python -m backend.scripts.seed_demo_cases --help` and `... reconcile_committing_cases --help`
still import (no regression from making `scripts` a regular package); full suite still **1549 / 0 / 40 / 5 /
99.87%** (scaffolding adds no tests, changes no coverage — `backend/scripts` is not a `--cov` target).

### Step 1 — RED: tier-U orchestration-contract test (C4)
Write `test_run_migrations.py` before `run_migrations.py` exists. It **monkeypatches**
`run_migrations.MigrationRunner`, `run_migrations.apply_case_migrations`, `run_migrations.sa.create_engine`,
`run_migrations.get_settings` with spies/fakes (the established behavioral-tier-U pattern, cf.
`deploy_config/tests` monkeypatching `create_engine`). Planned assertions (**7 tests**):

1. `test_builds_engine_from_settings_database_url` — `create_engine` called once with `get_settings().DATABASE_URL`.
2. `test_applies_u15_before_u24` — recorded call order is U15's `apply_all` **then** `apply_case_migrations`.
3. `test_u24_is_applied_via_apply_case_migrations_exactly_once` — the guard path, not a bare runner.
4. `test_u15_runner_is_constructed_with_the_default_dir_never_the_case_dir` — spy on `MigrationRunner.__init__` records args; `CASE_MIGRATIONS_DIR` is **never** passed (proves C-C structurally).
5. `test_error_in_u15_apply_propagates` — U15 `apply_all` raises → `main` raises (no swallow; fail-loud).
6. `test_error_in_u24_apply_propagates` — `apply_case_migrations` raises → `main` raises; and `engine.dispose()` still called (the `finally`).
7. `test_main_returns_zero_and_disposes_on_success` — returns `0`, `engine.dispose()` called, and the printed line contains **no rendered SQL** (only counts/filenames).

**RED**: all 7 fail at import (`run_migrations` absent).

### Step 2 — GREEN: implement the entrypoint (C1)
Write `run_migrations.py` per §1.1. **Verify**: the 7 tier-U tests pass. Predicted suite:
**1556 / 0 / 40 / 5 / 99.87%** (7 new passes; coverage unchanged — file not in `--cov`).

### Step 3 — tier-I integration test (C5), CI-gated / clean-skip locally
Write `test_run_migrations_integration.py` using the `_docker_available()` **ping-guard fixture verbatim**
(the database/case_lifecycle known-good pattern — pings the daemon *inside* the fixture *before*
constructing the container, so Docker-absence is a **SKIP, never a 6th error**). The fixture sets throwaway
`AUDIT_WRITER_PASSWORD`/`AUDIT_READER_PASSWORD` env (U15's `0002_grants.sql` substitutes them) then calls
`apply_all_migrations(engine)`. Planned assertions (**3 tests**):

1. `test_applies_both_sequences_to_a_fresh_container` — resulting tables ⊇ `{audit_record,
   applicant_profile_snapshot, app_user, pending_application, pending_recommendation}`.
2. `test_applied_migrations_records_both_sequences` — the `applied_migrations` tracking table holds
   `{0001_initial_schema.sql, 0002_grants.sql, 0001_case_lifecycle.sql}`.
3. `test_second_run_applies_nothing_new` — a second `apply_all_migrations` returns `([], [])` (end-to-end
   idempotency).

**Locally (no Docker)**: all 3 **SKIP**. Predicted suite: **1556 / 0 / 43 / 5 / 99.87%** — ⚑ **errors stay
exactly 5** (ping-guard), skips 40→43. **In CI (Docker)**: the 3 run **green**.

### Step 4 — `render.yaml` edit (C6), LAST among code (Q5)
Now that the entrypoint exists and is tier-U-green (+ tier-I green in CI):
- **Value**: `preDeployCommand: "python -m backend.database.migrate"` → `"python -m backend.scripts.run_migrations"`.
- **Comment (lines 12–16)**: rewrite so it states the entrypoint **now exists** at
  `backend/scripts/run_migrations.py` and applies **both** U15's and U24's sequences (guard-first) before
  traffic — removing "is database's/composition's deliverable / not the runner."

**Verify** (against actual test content, per ambiguity-check (iii)): `deploy_config` suite green —
`test_boot.py` (`preDeployCommand` presence still true; `startCommand` unchanged), `test_format.py` (key
set intact, YAML well-formed), `test_sec3.py` (`secret_value_offenders` finds nothing in the new string;
`envVars` unchanged). No count change.

### Step 5 — `deploy/README.md` MIGRATION edit (C7) — ⚑ FLAGGED (see §6)
Update lines 54–58 so "Until it exists, the `preDeployCommand` names the intended entrypoint" is replaced
by a statement that the entrypoint **exists** at `backend/scripts/run_migrations.py` and applies both
sequences. **Verify**: `test_doc.py` green — the 5 required marker tokens (`ROUTE-STATUS:`,
`Q1-B-DIVERGENCE:`, `AC-7-CONTINGENCY:`, `FREE-TIER:`, `ENV-SHAPES:`) are all in **other** sections, so the
MIGRATION prose change leaves them intact. No count change.

### Step 6 — full-suite run + register update (C8)
Run the full backend suite live; confirm the predicted counts (§3). Then write the #8 register update
across `BUILD-COMPLETION-REPORT.md`, `guide-state.md`, `audit.md` with the outcome decided **on the evidence
actually produced** (§7), on the supersede-don't-rewrite precedent.

---

## 3. Exact count predictions, stated in advance (mirroring #18/#19 discipline)

| Point | passed | failed | skipped | errors | coverage |
|---|---|---|---|---|---|
| Baseline (pre-#8) | 1549 | 0 | 40 | 5 | 99.87% |
| After Step 0 (scaffolding) | 1549 | 0 | 40 | 5 | 99.87% |
| After Step 2 (entrypoint + tier-U) | **1556** | 0 | 40 | 5 | 99.87% |
| After Step 3 (tier-I, **no Docker here**) | **1556** | 0 | **43** | **5** | 99.87% |
| After Steps 4–5 (render.yaml + README) | 1556 | 0 | 43 | 5 | 99.87% |
| **Final (this environment, no Docker)** | **1556** | **0** | **43** | **5** | **99.87%** |
| CI reference (Docker present) | 1556 **+3 of the 43 run green** | 0 | (fewer, Docker) | (0 for these; audit_store's 5 are its own gap) | 99.87% |

⚑ **The HOLD "5 errors stay exactly 5" is preserved** — the new integration test skips (never errors)
without Docker, by the ping-guard mechanism traced in the ambiguity-check. ⚑ **Coverage is unchanged at
99.87%** — `backend/scripts` is not a `--cov` target, so `run_migrations.py` is coverage-invisible (§4).

If any actual number diverges from the above at Step 6, **stop and reconcile before the register update** —
a divergence is a finding, not a number to overwrite (the #18/#19/#20 discipline).

---

## 4. The coverage subtlety, stated honestly (Q6 tension)

`run_migrations.py` lives in `backend/scripts/`, which is **not** a `--cov` entry (verified in
`pyproject.toml`) — so even though the tier-U tests *execute* its orchestration logic, those lines are **not
measured**, and the 99.87% number neither rises nor falls. This is the **same** coverage-invisibility the
two existing scripts have, and it is why the Q6 answer chose **explicit tests (c)** rather than relying on
the coverage gate: a deploy-critical entrypoint deserves proof-by-test even though the `backend/scripts`
convention keeps it out of the coverage denominator. **The honest claim is "test-covered by tier-U + tier-I,
coverage-invisible by convention," never "covered to 99.87%."** This is stated in the register update, not
left implicit.

---

## 5. Holds — every one upheld by this plan

| Hold | How upheld |
|---|---|
| No edit to U15's `0001_initial_schema.sql` / `0002_grants.sql` | C1 **calls** `MigrationRunner`; edits no `.sql` |
| No edit to U24's checksum-locked `0001_case_lifecycle.sql` | C1 **calls** `apply_case_migrations`; edits no `.sql` |
| No edit to frozen `MigrationRunner`/`verify_checksums` — only call it (C-A) | C1 constructs + invokes only |
| U24 applied only via `apply_case_migrations` (C-C) | C1 §1.1 + tier-U test #3/#4 assert it |
| `render.yaml` edit is this pass's own **named, justified** edit, never silent | Step 4, logged in audit + register; justification = scoping §1.6–§1.7 |
| No edit to any other frozen-23 unit's internals | Only `backend/scripts/` (new), `render.yaml`, `deploy/README.md` (U23 non-frozen), docs |
| WIRE-1 contract text **not amended** | Untouched |
| `not_wired.py` **not renamed** | Untouched |
| **U23's frozen test files not edited** | `backend/deploy_config/tests/*` untouched — the edits are to `render.yaml` (config) + `deploy/README.md` (doc), both non-frozen; **distinct from the tests** (scoping §1.6) |
| `audit_store` Docker-guard gap untouched — **5 errors stay 5** | tier-I test uses ping-guard → skip, never error; audit_store untouched |
| tier-B not authorized | Not invoked — #8 needs no corpus, no LLM |
| No new route under `backend/app/routes/` | None added — this is a deploy entrypoint, not a route |

---

## 6. ⚑ The surfaced adjacent finding (directed check iii) — flagged, your call at this gate

Discharging #8 by pointing `preDeployCommand` at a **real, existing** entrypoint leaves **prose that says the
opposite** in two live locations:

1. **`render.yaml` comment, lines 12–16** — *"the runnable CLI entrypoint … is database's/composition's
   deliverable … This wires WHEN it runs, not the runner."* This is the **same file** as the Q5-authorized
   value edit, so updating the comment alongside the value is within Q5's scope and is included as **C6**.
2. **`deploy/README.md` MIGRATION section, lines 54–58** — *"Until it exists, the `preDeployCommand` names
   the intended entrypoint; deploy-config wires the slot, not the runner."* This is a **separate U23
   (non-frozen) doc**, **beyond the literal Q5 answer** — so it is **flagged here (C7)** for your explicit
   approval rather than silently absorbed, on the #20 precedent (where the ambiguity-check surfaced a second
   file the scoping missed and stopped for a decision).

Both edits are **test-neutral** (verified: `test_doc.py` matches only the 5 marker tokens, none in the
MIGRATION section; no test asserts the `render.yaml` comment). The **historical** records (`database`
Infra-Design §3.4; `BUILD-COMPLETION-REPORT.md` §5 #8) are **not** edited in place — they are superseded by
the register-update section (C8), exactly as #2/#18/#19/#20's original rows were preserved and superseded.

**Decision requested at this gate:** approve **C7** (update `deploy/README.md`'s MIGRATION prose) as part of
this fix, or exclude it. Recommendation: **include it** — leaving "Until it exists…" on disk after the
entrypoint exists is precisely the self-contradiction the #20 pass was careful to avoid.

---

## 7. Honest-claim section — what this fix will and will not guarantee (NARROWED vs DISCHARGED)

**What the fix establishes (provable here + in CI):**
- ✅ A **single command exists** (`python -m backend.scripts.run_migrations`) that applies **both** U15's
  and U24's sequences in order, guard-first, against the owner engine from `get_settings()`.
- ✅ It is **idempotent** (skip-if-applied, inherited from the frozen runners; asserted end-to-end by tier-I
  test #3) and **fail-loud** (asserted by tier-U tests #5/#6).
- ✅ `render.yaml`'s `preDeployCommand` now names an entrypoint that **exists on disk** — deploy-config's
  committed config is correct for the first time.
- ✅ Proven against a **real Postgres** via testcontainers (tier-I) — the same fidelity U15's and U24's own
  migration tests already have.

**What it does NOT guarantee (the honest residual):**
- ❌ **The actual Render release step has not been executed end-to-end.** There is no live Render deploy and
  no live Postgres in this environment; the on-Render invocation of `preDeployCommand` is a **deploy-time
  fact**, observed-not-tested here (exactly as U23's own `test_boot.py` already frames the boot itself).
- ❌ **In this environment (no Docker), the tier-I proof SKIPS** — it executes green only where Docker is
  present (CI or a Docker-equipped machine). So at the moment this fix lands *locally*, the real-schema
  proof is **written and CI-gated, not executed here**.

**The anticipated NARROWED-vs-DISCHARGED question (scoping-plan §5), addressed explicitly:**

> **Recommendation: close #8 as DISCHARGED *iff* the tier-I integration test is confirmed green in an
> environment with Docker** (CI, or a local Docker run) — because there the entrypoint's full behaviour is
> proven against a real database, and the only remaining unexercised link (Render's platform actually
> invoking the command) is `deploy-config`'s already-tested wiring plus the Render platform, not this
> entrypoint's logic. **If this pass can only run tier-U (Docker absent, as here), the honest close is
> NARROWED** — "entrypoint built, tier-U-proven, tier-I written and CI-gated but not executed in this
> environment; the live Render release step not run" — on the **#18 precedent** (real path unit-proven,
> structurally complete, but the live confirmation left to a documented step). **The outcome is decided on
> the evidence actually produced at Step 6, never pre-committed here.** Unlike #20 (a documentation-only
> discharge with no residual), #8 has a real deploy-time residual whenever the tier-I proof has not actually
> executed — which is the NARROWED shape.

No new register item is anticipated **if DISCHARGED**; if **NARROWED**, the residual is the
"live-Render-release-step-not-executed" fact, tracked on #8 itself (as #18 tracked its manual-verification
residual) rather than spawned as a new item — to be confirmed at Step 6.

---

## 8. What happens after approval

1. On approval (incl. the §6 C7 decision), execute Steps 0→6 in order, RED-before-GREEN, updating this
   plan's checkboxes as each step completes.
2. Run the full suite live at Step 6; **reconcile any divergence from §3 before** writing the register
   update.
3. Write the #8 register update with the outcome (DISCHARGED or NARROWED) **decided on the evidence**, and
   present the standardized 2-option completion message.

**STOPPED AT THE PLAN-FILE GATE. No code generated. Awaiting approval** — including your call on the §6
flagged `deploy/README.md` edit (C7).
