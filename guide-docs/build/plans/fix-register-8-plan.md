# Register Item #8 — `DEPLOY-MIGRATE-DEFERRED` · SCOPING PLAN

**Stage**: POST-BUILD → register-item remediation · the **fourth** item taken up after **SCOPE B CLOSED**
(after **#19 NARROWED**, **#18 NARROWED**, **#20 DISCHARGED**).
**Status**: 🟡 **SCOPING / PLANNING ONLY — NO CODE GENERATED.** Stopped at the plan-file gate.
**Date**: 2026-07-22T17:41:24Z
**Origin**: register item **#8** (`BUILD-COMPLETION-REPORT.md` §5 #8; carried on the AC-7
*provisioned-for-not-discharged* pattern), opened at the close of the BUILD phase.
**Owner recorded in the register**: **`database` / composition.**

**Register severity, quoted, not softened**: *"**Non-blocking** at build time; **blocking for an actual
deploy**."* (Unlike #20, this item has a **real functional gap** — a genuine missing artifact — so it is
closer in character to #18/#19 than to #20. But like all four, whether and how it resolves is the user's
to decide, and this pass generates no code.)

---

## 0. What this document is and is not

* **IS**: a scoping plan. Ground truth re-verified from disk, the design tension, the constraints, and
  **six open questions** for the user to answer.
* **IS NOT**: a fix, a design, an implementation, or an authorization. **No code is generated. No file
  under `backend/` is created or edited. `render.yaml` is not touched.** Whether the entrypoint lives in a
  frozen unit's tree, whether `render.yaml` is updated, and how it is tested are **all** the user's to
  decide (Q1, Q5, Q6).

**Every `[Answer]` tag below is BLANK. None is pre-filled.** Recommendations are given where grounded and
are explicitly marked as recommendations, never as decisions.

---

## 1. Ground truth — re-established from disk, not from any summary

Five Step-1 checkpoints were re-verified against the actual current files. **All five confirm the gap
exactly as located.** Two additional findings that materially shape Q5 and Q6 are reported in §1.6–§1.7
rather than absorbed.

### 1.1 `render.yaml`'s `preDeployCommand` — ✅ CONFIRMED, and the entrypoint it names is ABSENT

| Property | On disk |
|---|---|
| `preDeployCommand` present | ✅ `render.yaml:17` |
| Its exact value | `"python -m backend.database.migrate"` |
| Does that entrypoint exist? | ❌ **NO** — see §1.2 |

The surrounding comment (`render.yaml:12–16`), quoted verbatim:

> `# Migration release step (DEPLOY-MIGRATE-DEFERRED): run database's forward-only,`
> `# idempotent migration sequence BEFORE traffic. database owns the MigrationRunner`
> `# (reference-not-own); the runnable CLI entrypoint that builds the engine from`
> `# secrets-config and calls apply_all() is database's/composition's deliverable.`
> `# See deploy/README.md (MIGRATION). This wires WHEN it runs, not the runner.`

⚑ **The `preDeployCommand` names an intended entrypoint that was never built.** A fresh Render deploy would
run `python -m backend.database.migrate`, hit `No module named backend.database.migrate`, and **fail the
release step before serving traffic.**

### 1.2 `backend/database/migrate.py` — ✅ CONFIRMED ABSENT

`backend/database/migrations/` contains exactly `0001_initial_schema.sql`, `0002_grants.sql`, and
`checksums.json` — no `migrate.py` module anywhere in `backend/database/`. The Read tool returns *"File
does not exist."* **It has not appeared since #8 was first disclosed.**

### 1.3 How U15's migrations get applied today — ✅ every caller constructs `MigrationRunner` DIRECTLY

There is **no** in-process CLI-like wrapper for U15's sequence. Every existing caller builds the runner by
hand against U15's own default `MIGRATIONS_DIR`:

| Caller | How | Purpose |
|---|---|---|
| `backend/database/tests/conftest.py:48` | `MigrationRunner(engine, env=env).apply_all()` | CI testcontainer fixture |
| `backend/database/tests/test_migration_apply.py:52` | `MigrationRunner(migrated_engine, env=env).apply_all()` | idempotency re-apply assertion |
| `backend/scripts/seed_demo_cases.py:207` | `MigrationRunner(engine).apply_all()` | demo seed (U15 half) |

⚑ **No `python -m` module and no `apply_all()`-wrapping function exists.** The gap is precisely that: the
frozen `MigrationRunner` class is a *tool taking an injected engine*; nothing builds the engine from
`secrets-config` and drives it as a standalone command.

### 1.4 How `seed_demo_cases.py` applies migrations — ✅ the closest precedent, scoped as demo

`seed_demo_cases.py:201–209`, `apply_all_migrations(engine)`:

```python
def apply_all_migrations(engine: sa.Engine) -> None:
    """Apply BOTH sequences: ``database``'s (U15) then U24's (guard-first).

    ⚑ Register #8 ``DEPLOY-MIGRATE-DEFERRED`` is NOT discharged by this — it asks for a
    deployment CLI entrypoint (``render.yaml``'s ``preDeployCommand``), which this is not.
    """
    applied_db = MigrationRunner(engine).apply_all()
    applied_case = apply_case_migrations(engine)
    print(f"  migrations: database={len(applied_db)} case_lifecycle={len(applied_case)}")
```

The script's module docstring (L31–33) states this explicitly: *"this script applies BOTH sequences … via
each one's own runner. ⚑ Register item #8 `DEPLOY-MIGRATE-DEFERRED` **STAYS OPEN**: this is a DEMO-PATH
convenience, **not** the deployment CLI entrypoint that item calls for, and it does not discharge it."*

⚑ **This is the load-bearing precedent for Q1/Q2.** The exact two-line body a real entrypoint needs —
`MigrationRunner(engine).apply_all()` then `apply_case_migrations(engine)` — **already exists and runs**,
inside a demo script that is deliberately out-of-band, coverage-omitted, and route-free. #8 is about
lifting that same body into a *deploy-time correctness* entrypoint, not inventing new apply logic.

### 1.5 The ordering constraint — ✅ CONFIRMED, and it is WEAKER than the register's framing implies

The register/task framing suggests "U15 first, then U24." The disk evidence is more precise:

- U24's `0001_case_lifecycle.sql` creates `pending_application` and `pending_recommendation` with FKs
  **only between themselves** (`fk_pending_recommendation_application`, both U24-owned) — **no FK, view, or
  reference to any U15 table** (`audit_record`, `applicant_profile_snapshot`, `app_user`).
- U24's collision guard (`case_lifecycle/migrate.py:61–68`) reads U15's filenames **live** via
  `migration_files(DB_MIGRATIONS_DIR)` — it works whether or not U15 has been *applied*; it inspects
  filenames on disk, not applied state.
- The shared `applied_migrations` tracking table is created idempotently by whichever runner runs first
  (`MigrationRunner._ensure_tracking_table` uses `CREATE TABLE IF NOT EXISTS`).

⚑ **Therefore there is NO hard schema dependency in either direction.** The two sequences are safely
applicable in either order, provided **both** complete before the app boots. The seed script's U15-then-U24
order is a **reasonable convention** (it mirrors `applied_migrations` accumulating U15's rows first, and
keeps the collision guard's "U15 already there" mental model), and Q2 recommends preserving it — but it is
**convention, not a constraint the schema forces.** This is reported so the ordering logic is *chosen*, not
assumed.

### 1.6 ⚑ FIND — `render.yaml` is NOT a frozen artifact (decisive for Q5)

U23's own frozen-vs-allowed path classifier, `backend/deploy_config/tests/structural.py:66`
(`is_under_frozen`), returns **False** for `render.yaml`, and `test_noedit.py:45` asserts this explicitly:

```python
assert not sg.is_under_frozen("render.yaml")
```

The classifier freezes `backend/<unit>/…` (except `deploy_config`) and `frontend/src/<unit>/…`.
`render.yaml` is **root-level declarative config**, a U23 *deliverable* but **outside every frozen tree**.
NFR-DEP-NOEDIT-1 (`test_noedit.py`) governs *what U23 may not touch* (frozen units + composition root); it
does **not** freeze `render.yaml` against a later value change. **Editing `render.yaml`'s `preDeployCommand`
value does not cross NOEDIT-1.**

### 1.7 ⚑ FIND — no test asserts the `preDeployCommand` VALUE (decisive for Q5)

`backend/deploy_config/tests/test_boot.py:36`, `test_migration_release_step_is_wired_before_traffic`, is
the **only** test touching `preDeployCommand`, and it asserts **presence, not value**:

```python
def test_migration_release_step_is_wired_before_traffic():
    svc = _service(sg.load_yaml(sg.RENDER_YAML))
    assert "preDeployCommand" in svc
```

A repo-wide grep confirms the literal string `backend.database.migrate` appears in **no test file** (only
`render.yaml`, `deploy/README.md`, and the three `guide-docs/` records). `test_format.py` checks
render.yaml's *key set* (`type`, `runtime`, `plan`, `buildCommand`, `startCommand`, `envVars`) — it does
not read `preDeployCommand`. `test_boot.py:24` (`test_start_command_runs_the_frozen_composition_root`)
asserts `backend.app.main:app` is in `startCommand` — untouched by any `preDeployCommand` change.

⚑ **Consequence:** updating `preDeployCommand`'s value (Q5) would **break no existing test**. The frozen
U23 test suite is fully compatible with pointing the slot at a real entrypoint.

### 1.8 What `database`'s own Infrastructure Design said about this — ✅ it deferred the TOOL, authored no entrypoint

`guide-docs/build/database/infrastructure-design/infrastructure-design.md:111–123` (§3.4, *"Migration
execution per environment — how C1 runs, not a re-opening of its model"*):

- Pins the **execution point** per tier; the **tool** (Alembic vs raw-SQL runner) is *"deferred to
  Code-Gen"*.
- **dev**: *"A Compose / `make migrate` target."*
- **CI**: migrations run against the testcontainer before integration tests.
- **prod**: *"A **Render release command / pre-deploy step** (wired by `deploy-config`) applies the full
  sequence **before** the app serves traffic."*
- Explicitly **rejects** app-startup migration (*"races across instances; a failed migration would block
  startup"*) in favour of *"an explicit gated step."*

⚑ **U15's Infra Design named the pre-deploy step and named `make migrate` for dev, but authored no runnable
Python entrypoint** — it deferred the tool to Code-Gen, and Code-Gen shipped the `MigrationRunner` *class*
(taking an injected engine), not a standalone command. **The entrypoint fell in the seam between "U15's
tool" and "deploy-config wires when it runs," and neither built it.** This is the substance of Q1's
"reopening" question: U15 *contemplated* a prod pre-deploy step but never authored the CLI half.

---

## 2. The design tension, stated precisely — and the constraints that bound every option

Unlike #20 (a pure disclosure gap over an already-correct posture), **#8 is a real missing artifact.** A
deploy cannot run its migrations because the command it invokes does not exist. The tension is **not**
"is anything wrong" (something is) but **"where does the missing entrypoint belong, given that the two
obvious homes are both partly frozen and partly not."**

> **The apply *logic* already exists and is proven** (§1.4 — the seed script's two-line body runs both
> sequences today). What is missing is a **standalone, secrets-config-driven, deploy-invokable command**
> that runs that same logic outside the demo path. The whole of #8 is: **where does that command live,
> exactly what does it run, and how is its correctness verified without a live Render deploy.**

**Three constraints, verified on disk, bound every option and must be stated up front:**

* ⚑ **C-A — the frozen migration machinery may be CALLED but not EDITED.** `MigrationRunner`, `migration_files`,
  `apply_all`, `verify_checksums` are frozen (HOLD). The entrypoint may only *construct and invoke* them —
  exactly as `seed_demo_cases.py` and `conftest.py` already do. This rules out any "just add a `main()` to
  `migration_runner.py`" shortcut.
* ⚑ **C-B — the `.sql` migration files are untouchable.** U15's `0001`/`0002` and U24's checksum-locked
  `0001_case_lifecycle.sql` are HOLDs (and U24's is hash-pinned, so even a comment edit breaks its
  manifest). #8 **invokes** existing migrations; it changes none. Nothing in this item requires editing a
  migration.
* ⚑ **C-C — U24's sequence must be applied through `apply_case_migrations()`, never a bare `MigrationRunner`.**
  `case_lifecycle/migrate.py:71–79` runs `assert_no_collision_with_database()` **first**, then
  `MigrationRunner(engine, migrations_dir=CASE_MIGRATIONS_DIR).apply_all()`. The docstring names this *"the
  ONLY sanctioned way to apply U24's migrations."* A real entrypoint that applied U24's dir via a raw
  `MigrationRunner` would **bypass the production collision guard** — the exact hazard P-CASE-11 was written
  to defend. The entrypoint must call `apply_case_migrations(engine)`, not reconstruct its body.

---

## 3. THE OPEN QUESTIONS

> **Instructions**: write your choice after each `[Answer]:` tag. Multiple letters are fine where the
> options compose. **Nothing proceeds until every tag is filled.** Once answered, the full Q&A is embedded
> back into this document and the mandatory ambiguity-check runs before anything else happens.

---

### Q1 — Where does the CLI entrypoint live?

This is the crux. The `preDeployCommand` names `backend.database.migrate`, but that home sits **inside a
frozen unit's tree**, while this build's established precedent for out-of-band operational commands is
`backend/scripts/`. The options genuinely differ in what they imply about "reopening."

**What "reopening a frozen unit" has meant in this build (grounded):** #18 and #19 were remediated by
adding **new** code — but that code went into `backend/app/llm_client.py` (composition root) and
`backend/scripts/` (out-of-band), **not** into a frozen P1 unit's package. U24's three authorized
reopenings each added methods *to U24 itself* under explicit per-reopening authorization. **No register fix
in this build has added a new module inside a *frozen P1 unit's* package** (`backend/database/` is U15,
frozen). Whether creating `backend/database/migrate.py` counts as "reopening U15" is therefore a real,
unsettled question — it is a *new* file (not an edit to frozen code), inside a *frozen unit's tree*, doing
work U15's Infra Design *contemplated* (§1.8) but never authored.

**Options:**

- **(a) — `backend/database/migrate.py`** (matches `render.yaml`'s existing reference verbatim; no
  `render.yaml` edit needed). Pros: the `preDeployCommand` already points here, so Q5 collapses to "leave
  render.yaml alone"; it is thematically U15's deliverable (it drives U15's runner), and U15's Infra Design
  named a prod pre-deploy step. Cons: it places a **new module inside the frozen U15 package** — the first
  register fix to add code inside a frozen P1 unit's tree; and this entrypoint must *also* apply **U24's**
  sequence (Q2), so a file named `backend/database/migrate.py` that imports `case_lifecycle` is arguably
  mis-homed (it is a *cross-unit deploy orchestrator*, not a `database`-internal concern). ⚑ Must confirm no
  structural scan asserts a closed file-set for `backend/database/` — none was found, but this is Q1's to
  verify at ambiguity-check.
- **(b) — a new script under `backend/scripts/`** (e.g. `backend/scripts/run_migrations.py`), consistent
  with `seed_demo_cases.py` and `reconcile_committing_cases.py`. Pros: matches the build's **established
  precedent exactly** — out-of-band operational commands live in `backend/scripts/`, built from
  `get_settings()` directly, no FastAPI `Depends` graph, no route, coverage-omittable; it is honestly a
  *cross-unit orchestrator*, which is what `scripts/` is for; it adds **no** code to any frozen unit's tree.
  Cons: **requires updating `render.yaml`'s `preDeployCommand`** from `python -m backend.database.migrate`
  to `python -m backend.scripts.run_migrations` — which is Q5's decision (shown in §1.6–§1.7 to break no
  test and cross no freeze, but it *is* a deliberate config edit that must be named).
- **(c) — elsewhere** (e.g. a new top-level `backend/migrate.py`, or inside a new `backend/deploy_config/`
  runnable — **rejected on sight**: `backend/deploy_config/` is *test-only* by BR-DEP-1/NFR-DEP-NOEDIT-1, so
  a runnable there would violate U23's own contract). Any "elsewhere" must be named with its own rationale.

**Recommendation (grounded): (b), composed with Q5's `render.yaml` update.** Three reasons from disk: (1)
the entrypoint is inherently a **cross-unit orchestrator** — it must drive *both* U15's runner *and* U24's
`apply_case_migrations` (Q2, C-C) — which is exactly what `backend/scripts/` is for and exactly what
`seed_demo_cases.py:201` already does; a home *inside `backend/database/`* would make U15's package import
U24, coupling a frozen unit to a later one. (2) It honours the build's **strongest precedent** — every
out-of-band operational command (#18's seed path, #19's reconcile script) lives in `backend/scripts/`,
built from `get_settings()`, route-free. (3) It **adds no code to any frozen unit's tree**, sidestepping the
"reopening U15" question entirely rather than answering it — the most conservative posture. The cost is a
one-line `render.yaml` value edit (Q5), which §1.6–§1.7 prove is test-neutral and freeze-neutral. ⚑ *This is
a recommendation, not a decision; the counter-case for (a) — "the `preDeployCommand` already names it, so
touch nothing declarative" — is real and the user's to weigh.*

**[Answer]**: (b) — a new script under `backend/scripts/` (e.g. `backend/scripts/run_migrations.py`), matching the established precedent of `seed_demo_cases.py` and `reconcile_committing_cases.py`. This entrypoint is inherently a cross-unit orchestrator — it must drive both U15's runner and U24's `apply_case_migrations` — and putting it inside `backend/database/` would mean a frozen unit's package importing a later one, which is backwards. Adding no code to any frozen unit's tree sidesteps the "does this count as reopening U15" question entirely, which is the more conservative and more honest posture given the question is genuinely unsettled.

---

### Q2 — What exactly does the entrypoint do?

**Confirmed from §1.4–§1.5 and C-C:** a single `preDeployCommand` invocation must make a **fresh deploy's
schema fully correct**, which means **both** sequences, because U15's tables (`audit_record`,
`applicant_profile_snapshot`, `app_user`) and U24's tables (`pending_application`,
`pending_recommendation`) are **both** required for the wired R1–R7 surface to function. Applying only one
leaves the app booting against a half-built schema.

**Options:**

- **(a) — Both sequences, U15 then U24, in one invocation** (mirrors `seed_demo_cases.py:201–209`):
  `MigrationRunner(engine).apply_all()` then `apply_case_migrations(engine)`. The engine is built once from
  `get_settings().DATABASE_URL` (the owner connection — migrations are owner/admin operations, per U15 Infra
  Design §3.5 and #20's ratified owner-only posture). U24's half **must** go through
  `apply_case_migrations()` (C-C), never a bare `MigrationRunner` against U24's dir.
- **(b) — U15 only.** ❌ Rejected: leaves `pending_application`/`pending_recommendation` absent; R2–R5 (now
  wired) would fail at runtime. Does not make a fresh deploy correct.
- **(c) — U24 only.** ❌ Rejected symmetrically: leaves the audit trail + `app_user` absent; R1/R5–R7 fail.
- **(d) — Both, but order-agnostic / U24-then-U15.** Defensible on §1.5 (no hard dependency), but gains
  nothing and departs from the seed-script precedent's readable "base schema first, then the pending
  overlay" order. Prefer (a) for consistency unless a concrete reason to reorder surfaces.

**On idempotency of "both" (feeds Q4):** because each sequence tracks its own applied files in the shared
`applied_migrations` table (keyed by bare filename), a re-run applies nothing new — proven for U15 by
`test_migration_apply.py:48` (`test_migration_sequence_is_forward_only_and_idempotent`, asserts `newly ==
[]` on re-apply).

**Recommendation (grounded): (a).** Both sequences are required (b/c rejected on the wired surface); U15
then U24 preserves the established precedent's order and the collision guard's "U15 already present" mental
model, while §1.5 confirms the order is safe rather than forced. Engine built once from the owner
`DATABASE_URL`; U24 applied via `apply_case_migrations()` (C-C). ⚑ *Recommendation, not decision — (d)'s
order-agnosticism is technically sound and the user may prefer to state it explicitly.*

**[Answer]**: (a) — both sequences, U15 then U24, in one invocation, engine built once from `get_settings().DATABASE_URL` (the owner connection), with U24's half applied exclusively through `apply_case_migrations()` per C-C. Both sequences are required for the wired R1–R7 surface to function; applying only one leaves a half-built schema. U15-then-U24 preserves the seed script's established, readable order even though §1.5 confirms it isn't schema-forced.

---

### Q3 — Hardcoded two-sequence invocation, or an extensible discovery mechanism?

Only two migration sequences exist today (U15's and U24's). A future unit *could* add a third. The question
is whether the entrypoint should **name the two explicitly** or **discover** sequences dynamically (e.g.
scan for `migrations/` directories under `backend/`).

**Options:**

- **(a) — Hardcoded, explicitly named two-sequence invocation.** The entrypoint literally calls U15's
  runner then `apply_case_migrations()`. A third sequence, if ever added, is a **one-line, reviewed edit**
  to this entrypoint under its own change. Pros: matches this build's **pervasive preference for explicit,
  named things over dynamic discovery** — the collision guard reads U15's dir by an explicit constant, the
  seed script names both sequences, `deploy_config`'s scans enumerate explicit artifact lists, U22's
  register is an explicit `DEFERRED_REGISTER`. It also keeps C-C **structurally visible** (the call to
  `apply_case_migrations` is right there in source), whereas discovery would re-derive U24's application
  path and risk bypassing the guard.
- **(b) — Discovery mechanism** (glob for `**/migrations/*.sql` directories and apply each). Pros: "future
  units get picked up automatically." Cons: (1) **contraindicated by C-C** — a generic "apply every
  `migrations/` dir with a bare `MigrationRunner`" would apply U24's dir *without* its collision guard,
  reintroducing the P-CASE-11 silent-skip hazard; honouring the guard would require special-casing U24,
  which defeats the "generic" premise; (2) **ordering becomes implicit** — discovery order (filesystem or
  alphabetical) is not obviously correct and is fragile; (3) it is exactly the kind of **dynamic magic this
  build has consistently rejected** (cf. `not_wired.py`'s explicit route pinning, the explicit checksum
  manifest). A newly-added sequence silently picked up with no reviewed entrypoint change is a *feature* only
  until it applies in the wrong order or bypasses a guard.

**Recommendation (grounded): (a) — hardcoded, explicitly named.** The codebase's conventions point
decisively here: explicit-over-dynamic is a stated pattern, and C-C makes discovery actively hazardous (it
would either bypass U24's guard or special-case U24 anyway). Two sequences exist; naming them costs two
lines and makes the whole apply order + guard usage auditable at a glance. A third sequence is a deliberate,
reviewed future edit — which is the *right* cost, not an inconvenience. ⚑ *Recommendation, not decision.*

**[Answer]**: (a) — hardcoded, explicitly named two-sequence invocation. This matches the codebase's consistent preference for explicit, named things over dynamic discovery, and discovery is actively disqualified by C-C: a generic scan-and-apply mechanism would either bypass U24's collision guard or need to special-case U24 anyway, which defeats the entire point of being "generic." A third future sequence is a deliberate, reviewed one-line addition to this entrypoint, which is the right cost for something this consequential.

---

### Q4 — Idempotency and safe re-runnability — verified, not assumed

A redeploy re-runs `preDeployCommand`. The entrypoint **must** be safely re-runnable: a second run must not
fail and must not double-apply. This must be confirmed against the **actual frozen behaviour**, not
asserted.

**What the frozen machinery guarantees (verified on disk):**

- `MigrationRunner.apply_all()` (`migration_runner.py:91–110`) calls `_ensure_tracking_table()`
  (`CREATE TABLE IF NOT EXISTS applied_migrations`), reads the applied set, and **skips any file already in
  it** (`if path.name in already: continue`). Each file is applied + recorded in **one transaction**, so a
  partial failure rolls back that step.
- Proven idempotent for U15 by `test_migration_apply.py:48` — re-applying the full sequence returns
  `newly == []` and the tracking table holds exactly the two U15 filenames.
- U24's `apply_case_migrations()` runs the **same** `MigrationRunner` against U24's dir, so it inherits the
  identical skip-if-applied idempotency; and it runs `assert_no_collision_with_database()` first every time
  (cheap, filename-only, no writes).

**So the entrypoint is idempotent by construction — provided it only *calls* the frozen runners and adds no
apply logic of its own.** The genuinely-open sub-question is what the entrypoint does on a **hard error**
(e.g. `MissingEnvVarError` from `substitute_placeholders` when a grant password env is unset, or a real SQL
failure):

- **(a) — Fail loud, non-zero exit, no swallowing.** Let the exception propagate; the entrypoint's `main()`
  returns non-zero (or the exception aborts the process), so Render's release step **fails visibly** and
  traffic is not served against a half-migrated schema. Matches U15 Infra Design's explicit *"a failed
  migration would block startup"* reasoning (it *should* block) and SEC-3's *"missing env var is a hard
  error, never a silent empty password."*
- **(b) — Catch-and-report / best-effort.** ❌ Rejected: swallowing a migration failure and serving traffic
  anyway is exactly the hazard the gated pre-deploy step exists to prevent.

**Recommendation (grounded): idempotency is CONFIRMED (skip-if-applied + per-file transaction, tested), and
the entrypoint should (a) fail loud on any error** — construct engine, apply both sequences, let any
exception propagate to a non-zero exit, and **never log rendered SQL** (`migration_runner.py` NOTE — the
grants file contains a substituted secret). No re-runnability code is needed *in* the entrypoint; it is a
property of the frozen runner the entrypoint merely inherits. ⚑ *Recommendation, not decision.*

**[Answer]**: Confirmed — idempotency holds by construction (skip-if-applied tracking, per-file transactions, already proven for U15 by `test_migration_apply.py`), and the entrypoint adds no re-runnability logic of its own beyond inheriting the frozen runner's behavior. On error: (a) — fail loud, let the exception propagate, non-zero exit, no swallowing, and never log rendered SQL (since the grants file contains a substituted secret). A failed migration must visibly block the release step, exactly as U15's own Infrastructure Design reasoned.

---

### Q5 — Does this pass update `render.yaml`, and does editing a config value cross a "reopening" threshold?

`deploy-config` (U23) is a frozen-23 unit. The task asks whether updating a **config value in a non-Python
file** crosses the same "reopening" threshold as editing a frozen unit's Python internals. **§1.6–§1.7
answer this decisively from disk:**

- **`render.yaml` is NOT under any frozen tree.** U23's own `is_under_frozen()` returns False for it,
  asserted by `test_noedit.py:45`. NOEDIT-1 freezes `backend/<unit>/` and `frontend/src/<unit>/`; root-level
  `render.yaml` is a U23 *deliverable* but explicitly **not** frozen against a value change.
- **No test asserts the `preDeployCommand` value** (§1.7). `test_boot.py:36` checks only presence; the
  string `backend.database.migrate` is in no test. Updating the value **breaks no test.**
- ⚑ **The HOLD's own distinction, confirmed:** the task's HOLD says *"U23's frozen test not edited (distinct
  from render.yaml itself, which is config, not test)."* On disk this distinction is real and enforced: the
  **frozen tests** live in `backend/deploy_config/tests/` (Python, under the one non-frozen backend tree U23
  authors); **`render.yaml` is declarative config at repo root.** Editing `render.yaml`'s value touches
  neither a frozen unit's Python internals **nor** any test. It is categorically different from a frozen-code
  edit.

**Options (conditional on Q1):**

- **(a) — Update `preDeployCommand`** to reference the new entrypoint (only *required* if Q1 = (b)/(c); under
  Q1 = (a) the value already matches and `render.yaml` is untouched). This makes deploy-config's committed
  config **correct for the first time** — the slot would finally name an entrypoint that exists. Justified as
  its own explicitly-named decision: it is a **one-line value edit to non-frozen root config, breaking no
  test and crossing no freeze** (§1.6–§1.7). It does **not** re-open U23 in any meaningful sense — U23's
  *code and tests* are untouched; only a config *value* U23 always intended to point at a real runner is
  updated to do so.
- **(b) — Leave `render.yaml` unchanged, treat the value as deploy-config's to update separately.** Coherent
  only under Q1 = (a) (where the value already matches). Under Q1 = (b)/(c), leaving it stale means the
  entrypoint exists but the deploy still invokes a non-existent module — **#8 would not actually be
  discharged**, since the whole point is a deploy that can run migrations.

**Recommendation (grounded):** **If Q1 = (b)**, then **(a)** — update the value, treated as this pass's own
explicitly-named, justified edit (test-neutral, freeze-neutral per §1.6–§1.7), because leaving it stale
would fail to discharge #8. **If Q1 = (a)**, then **(b)** — the value already matches and `render.yaml` is
correctly left untouched. Either way, **#8 is only discharged when the string in `preDeployCommand` names an
entrypoint that exists on disk.** ⚑ *Recommendation, not decision — and if any `render.yaml` edit is made,
it is logged as its own named change with this justification, never a silent edit (per the HOLD).*

**[Answer]**: Conditional per the plan's own logic — since Q1 selected (b), this resolves to (a): update `render.yaml`'s `preDeployCommand` to reference the new `backend/scripts/run_migrations.py` entrypoint. Treat this explicitly as this pass's own named, justified edit: a one-line config value change, confirmed test-neutral (§1.7) and freeze-neutral (§1.6) on disk, made because leaving the value stale would mean #8 remains functionally undischarged regardless of what code exists — the deploy would still invoke a nonexistent module. Log this edit by name in the audit trail, never silently.

---

### Q6 — How is the entrypoint tested without an actual Render deployment?

The entrypoint drives real Postgres DDL; its correctness cannot be fully proven at tier-U alone, but a live
Render deploy is not available in CI. The precedent scripts (`seed_demo_cases.py`,
`reconcile_committing_cases.py`) carry `# pragma: no cover - out-of-band entrypoint` and are coverage-
omitted — but those are *demo/ops* tools; this one is **deploy-time correctness**, which argues for more
than zero coverage.

**Options (not mutually exclusive):**

- **(a) — An integration test using the existing testcontainers pattern.** Apply **both** sequences to a
  fresh `postgres:16` container via the entrypoint, then assert the resulting schema contains **both** U15's
  tables (`audit_record`, `applicant_profile_snapshot`, `app_user`) **and** U24's (`pending_application`,
  `pending_recommendation`) — reusing exactly the reflection/`table_names` helpers `test_migration_apply.py`
  already uses. Also assert **idempotency end-to-end**: a second entrypoint run applies nothing new. This is
  the strongest evidence short of a live deploy, and the substrate already exists (`conftest.py`'s
  `migrated_engine` pattern, `@pytest.mark.integration`, Docker-auto-skip). ⚑ Would live under the Q1-chosen
  home's test dir, or a new integration test module; must respect the Docker-absence skip so it does **not**
  add to the 5 pre-existing `audit_store` errors or change the skip count materially (a new
  `@pytest.mark.integration` test *skips* without Docker, adding to the skip tally, not the error tally —
  confirm at ambiguity-check that this is acceptable given the HOLD "5 errors stay exactly 5" governs
  *errors*, not skips).
- **(b) — A tier-U test of just the ordering / argument-parsing / wiring logic** with a **fake engine and
  fake/spy runners**, asserting the entrypoint (i) builds the engine from `get_settings()`, (ii) calls U15's
  apply **before** U24's `apply_case_migrations`, (iii) calls U24 via `apply_case_migrations` (not a bare
  runner — proving C-C is honoured), (iv) propagates errors (Q4). No container needed; runs everywhere. Does
  **not** prove real DDL applies, but proves the orchestration contract.
- **(c) — Both (a) and (b).** The tier-U test pins the orchestration contract (order, guard usage, error
  propagation) portably; the integration test proves the real schema materialises and is idempotent. Highest
  confidence, modest cost, and matches how the build already splits "portable contract" from "real-Postgres
  behaviour" (cf. U15's `test_migration_apply` integration tier + its unit-tier checksum tests).

**Recommendation (grounded): (c) — both.** (b) is cheap, portable, and the only way to assert C-C (U24 via
its guard) and Q2's ordering deterministically without Docker; (a) is the only way to prove the real
two-sequence schema materialises and re-runs cleanly, and its substrate already exists. Together they mirror
U15's own unit+integration split. ⚑ **Confirm at ambiguity-check** that the new integration test's
Docker-absence behaviour is a *skip* (raising the skip count) and not a new *error*, so the HOLD's "5 errors
stay exactly 5" is preserved. If keeping the error/skip counts *exactly* fixed is required, (b) alone is the
fallback (pure tier-U, no container, no skip-count change). ⚑ *Recommendation, not decision.*

**[Answer]**: (c) — both. The tier-U test pins the orchestration contract (engine construction, U15-before-U24 ordering, U24 called via `apply_case_migrations` specifically and never a bare `MigrationRunner`, error propagation) portably and without Docker. The integration test proves the real two-sequence schema actually materializes on a fresh Postgres container and that a second run applies nothing new. Confirm explicitly at the ambiguity-check that the new integration test's Docker-absence behavior is a skip, not an error, so the HOLD's "5 errors stay exactly 5" is preserved untouched — if that can't be confirmed cleanly, fall back to (b) alone as the plan itself names.

---

## 4. Holds for this pass — verified, all currently upheld

| Hold | Status at plan time |
|---|---|
| No edit to U15's `0001_initial_schema.sql` / `0002_grants.sql` | ✅ Untouched — this item **invokes** them, edits neither |
| No edit to U24's checksum-locked `0001_case_lifecycle.sql` | ✅ Untouched — invoked via `apply_case_migrations`, never edited |
| No edit to frozen `MigrationRunner` / `verify_checksums` machinery — only new code that CALLS it (C-A) | ✅ Not written; the entrypoint *constructs and invokes* the frozen runner, adds no apply logic |
| If `render.yaml` edited, it is its own explicitly-named Q5 decision with justification, never a silent edit | ✅ Not touched this pass; Q5 names it as a decision, with the §1.6–§1.7 justification pre-stated |
| No edit to any other frozen-23 unit's internals | ✅ Untouched |
| WIRE-1's contract text **not amended** | ✅ Untouched — #8 does not touch the wire contract |
| `not_wired.py` **not renamed** | ✅ Untouched — register #13 stays open |
| U23's frozen test **not edited** (distinct from `render.yaml`, which is config not test — §1.6) | ✅ Untouched — the distinction is confirmed on disk; a `render.yaml` value edit touches no test |
| The `audit_store` Docker-guard gap **untouched** — 5 errors stay exactly 5 | ✅ Untouched; Q6 flags the new integration test must *skip* (not *error*) without Docker |
| **tier-B not authorized** | ✅ Not invoked — #8 needs no corpus and no LLM |
| **No new route** under `backend/app/routes/` | ✅ None proposed — #8 is a deploy-time migration entrypoint, not a route |
| **No code generated in this pass** | ✅ **Zero code written. Zero files under `backend/` touched. `render.yaml` untouched.** Only `guide-docs/` (this plan + the start-of-work log) |

**Test state carried forward, NOT re-run by this pass**: backend **1549 passed / 0 failed / 40 skipped / 5
pre-existing `audit_store` Docker-absence errors**, coverage **99.87%**. **Nothing was executed or modified
under `backend/`.**

---

## 5. What happens after the answers

1. Answers recorded verbatim in `audit.md`; **the full Q&A embedded back into this document** (§3 becomes
   the answered record).
2. **The mandatory ambiguity-check runs** against the answer set + §1 ground truth — surface-and-stop on any
   genuine gap, per the standing discipline (the #20 pass is the precedent: it caught a missed second
   in-code reference). Likely directed checks: (i) does the Q1-chosen home collide with any structural
   file-set scan (none found, but verify); (ii) does the Q6 integration test's Docker-absence behaviour add
   to *errors* vs *skips* (HOLD guards errors at 5); (iii) if Q5 updates `render.yaml`, re-confirm no test
   asserts the value (§1.7) and the update is logged as its own named edit.
3. **If the answers select a code-generating path** (the likely shape: a new entrypoint + tests, ±a
   `render.yaml` value edit): a **code-generation plan** with explicit TDD steps (RED-before-GREEN,
   leaf-first) and a green-run verification is written and **separately approved** before any code is
   generated. #8 stays **OPEN** until that entrypoint ships and (Q5) `render.yaml` names it.
4. **The discharge bar for #8** (unlike #20's documentation-only close): #8 is discharged only when a single
   command applies both migration sequences correctly on a fresh database, `render.yaml`'s `preDeployCommand`
   names an entrypoint that **exists**, and the entrypoint's correctness is verified per Q6. Because a **live
   Render deploy cannot be run here**, the honest outcome may be **NARROWED** (structurally complete +
   test-proven, but the actual on-Render release step not executed end-to-end) rather than fully DISCHARGED —
   mirroring #18's precedent, where the real-API path was unit-proven but the live confirmation was left to a
   documented manual step. This is stated now so the outcome is decided **on the evidence actually produced**,
   not pre-committed.

---

**STOPPED AT THE PLAN-FILE GATE.** No code. No `render.yaml` edit. No reopening. No register status change.
The next decision is the user's — answer Q1–Q6 and the mandatory ambiguity-check runs before anything else
happens.
