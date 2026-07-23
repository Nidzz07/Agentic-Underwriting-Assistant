# NFR Requirements Plan (Part 1) — `case-lifecycle` (U24, Scope B)

**Phase / Stage**: BUILD → per-unit loop → **NFR Requirements, Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `case-lifecycle` (U24) · **FD ✅ (approved 2026-07-19)** → **NFR Requirements ← here (the 2nd of U24's
5 stages)**
**Unit**: U24 · **Scope B** · **Date**: 2026-07-19 · **Depth**: **comprehensive** (Q1-A — U24 owns the human-in-the-loop
commit boundary, the same class of invariant `audit-store` (U12) held at comprehensive depth)
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR artifact; no code; no wiring; `backend/case_lifecycle/` ABSENT.**

Built **ON** the frozen FD — **`BR-CASE-1..14`**, the five-state model + the internal `failed` state and its **disclosed**
wire-projection, the **CANON-SER byte-identity** design, the **explicit `route_borderline`** invocation, the
**namespaced + collision-guarded** migration sequence, the `CasePipeline`'s **injected-dependency tier-U discipline**, and
the **frozen commit-boundary composition** via `PendingCommitContextProvider` — **re-opening none of it.**

---

## 1. Tier convention (inherited — extended once, for persistence)

**tier-U** = fast, deterministic, in CI — **no live LLM, no key, no network, no Docker, no live DB**. Every LLM-bearing
dependency is **injected** and driven by an **offline double**. **Every scan carries a detector self-test.**
**tier-I (integration)** = the **existing** `@pytest.mark.integration` marker — *"requires Docker + a real Postgres
(testcontainers); auto-skipped when unavailable"*. **⚑ U24 is the first Scope-B unit to need this tier — see Q1.**
**tier-B** = **NOT authorized, NOT required.**

**⚑ The standing hold this interacts with**: the backend baseline is **1308 passed / 31 skipped / 5 pre-existing
`audit_store` Docker-absence errors**, and **the 31 skips and 5 errors must stay exactly unchanged**. Any live-DB test U24
adds must therefore **skip CLEANLY**, never error — which is precisely what Q1 turns on.

---

## 2. `BR-CASE-*` → draft `NFR-CASE-*` target map (all 14 mapped — **NO ORPHAN**)

| BR | Draft target | Tier / rigor | Pass/fail teeth |
|---|---|---|---|
| **BR-CASE-1** | **STATE-1** | tier-U, standard | The **full legal transition set** is accepted: `submitted→profiled→evaluated→drafted→committed`, plus `→failed` from the drafting attempt. Each transition's artifact comes from the corresponding **frozen seam** (driven, never re-implemented). |
| **BR-CASE-2** | **STATE-2** | tier-U, **standard (paired)** | **Explicit rejection teeth over the ILLEGAL set**: `submitted→drafted` (skipping evaluation) · `submitted→committed` · every **backward** move (`evaluated→profiled`, `drafted→evaluated`, …) · any transition out of a terminal state. **Detector**: a transition table missing a rejection is caught by asserting the illegal set is **exhaustively enumerated** against the state cross-product. |
| **BR-CASE-3** | **EAGER-1** | tier-U, standard | Submission reaches **`evaluated`** in one transaction; **both** canonical payloads + hashes persisted. **On mid-way failure: NO partial row** (asserted by state count before/after). |
| **BR-CASE-4** | **TRIGGER-1** | tier-U, standard | **⚑ The R4 read path invokes the pipeline ZERO times** — the injected double records **no** calls; state is unchanged after the read. After the explicit trigger: state `drafted`, R4 reports `ready`. |
| **BR-CASE-5** | **FAILED-1** | tier-U, standard | A failing injected double drives the case to **`failed`**, and `failed` is **internally distinguishable** from `evaluated` (a never-triggered case ≠ a broken one). |
| **BR-CASE-6** | **PROJECT-1** | tier-U + **governance/disclosure** | A `failed` case yields a **WIRE-1-VALID** `MemoView` with `status == "pending"`. **Plus a DOC-1-style token checklist** for register **#14 `MEMOVIEW-FAILED-STATE-UNMODELLED`** — name + owner + rationale present, **no U24 artifact claims WIRE-1 models a failed state**, detector self-test on token removal. *(Mirrors `llm-judge`'s DISCLOSE-1 exactly.)* |
| **BR-CASE-7** | **⚑ CANON-1 — LOAD-BEARING** | tier-U, **full-highest** | **Round-trip byte-identity**: `serialize → deserialize → serialize` is **byte-identical**; `Decimal`/`date` return **as themselves** (P2/P3 fidelity); `content_hash` is **stable across runs**; **a mutated byte FAILS** the hash check. |
| **BR-CASE-8** | **⚑ ADAPTER-1 — LOAD-BEARING** | tier-U, **full-highest (structural)** | **AST scan**: **no U24 module calls `canon_ser` directly**, re-implements the `.model_dump(mode="python")` reduction, or forks §2.1 — every canonicalization goes through the **frozen `audit_store.CanonSerAdapter`**. **Detector self-tests**: a synthetic direct `canon_ser(...)` call **is flagged**; a synthetic `model_dump(mode="json")` **is flagged**. Plus: **no `$`-prefixed key** in any U24 payload. |
| **BR-CASE-9** | **CANONTIME-1** | tier-U, standard | After submission **both** payloads **and** their hashes exist; at drafting the **four stamps** exist. `content_hash` **always matches** its stored bytes (co-located call site). |
| **BR-CASE-10** | **ROUTE-1** | tier-U, standard | `route_borderline` is **actually invoked with real arguments** (a spy records the `(rule_report, outlier_result)` pair); a `REFER` report yields **`EXTENDED`** and **the adapter receives it**. **⚑ Re-derivability**: recomputing the mode **from stored state alone** reproduces the same value ⇒ non-persistence is safe. |
| **BR-CASE-11** | **MIGNAME-1** | tier-U, structural + detector | U24's migration filenames are **disjoint** from U15's; **detector self-test — a synthetic colliding filename IS flagged**; `verify_checksums` passes against **U24's own manifest**. |
| **BR-CASE-12** | **MIGSCOPE-1** | tier-U, structural | A scan asserts U24 **never** passes `database`'s default `MIGRATIONS_DIR`, **never edits U15**, and **authors no CLI entrypoint** (#8 `DEPLOY-MIGRATE-DEFERRED` **not adopted**). |
| **BR-CASE-13** | **⚑ COMMITBOUND-1 — LOAD-BEARING** | tier-U, **full-highest (structural + behavioural)** | **(a) Structural**: **no U24 module implements a gate, an authz check, or a write to `audit_record`** (+ detector self-tests for each). **(b) Behavioural**: `PendingCommitContextProvider.get()` returns a **`CommitContext` and nothing more** — it performs no authz, raises for an unknown id (R5 → 404), and **never reaches a write path**. |
| **BR-CASE-14** | **NOMETRIC-1** | tier-U, structural | **Mirrors `llm-judge`'s NOMETRIC-1 exactly**: a **provenance scan** (no U24 module declares a metric name / `MetricDefinition`, + detector) **plus** the **corroborating static byte-unchanged check** of `observability`'s five `METRIC_DEFINITIONS` and `deploy-config`'s `grafana-dashboard.json` — **read-only, NEITHER SUITE RE-RUN**. |

**Also carried (cross-cutting, as every prior unit did)**: **PERF-1** — observed-never-gated (U24 owns no runtime SLO; the
drafting step's cost is out-of-band). **SEC-1** — the Security-Guardrails governance table.

---

## 3. ⚑ The proposed LOAD-BEARING set — three targets, and why

The user asked which target(s) should carry **full-highest** rigor. **Proposed: three — CANON-1, ADAPTER-1,
COMMITBOUND-1.** Count is in band (`deploy-config` carried three; `observability` and `llm-judge` two each), and U24 is
**comprehensive** depth.

**CANON-1 + ADAPTER-1 are a deliberate PAIR covering one cluster by TWO different mechanisms** — the same structure
`llm-judge` used for EXEMPT-1 (behavioural teeth + a distinct structural safeguard) and NOEDIT-1/NOMETRIC-1 (path scan +
provenance scan):
- **CANON-1 is behavioural** — it proves the bytes actually round-trip identically and the hash actually detects a
  mutation. It would **still pass** if U24 had its own correct-but-forked serializer.
- **ADAPTER-1 is structural** — it proves U24 **uses the frozen adapter** and never bypasses or re-derives it. It would
  **still pass** on a serializer that happened to be broken.
- **⚑ Neither alone is sufficient, and that is exactly why they are two.** Together they give: *the encoding is correct*
  **and** *it is the single frozen encoding, not a fork.* A single edit cannot weaken both.
- **Why full-highest**: this cluster carries **CASE-GAP-1's whole resolution**. If it drifts, hash equality breaks
  **silently on a later run** — the failure mode is invisible at write time and only surfaces at replay, which is the
  worst possible place for an audit system.

**COMMITBOUND-1 is the third, and arguably the most consequential in the build**: it is the assertion that **U24 never
finalizes a decision**. A defect here is the one that could let the system commit without underwriter action. It carries
**both** a structural scan and a behavioural assertion for the same reason the pair above does.

---

## 4. Clarifying questions — fill each `[Answer]:` tag

> **I will improvise none of these.** Each is a genuine fork. **Options are lettered; a recommendation is given where the
> ground-truth pass produced a grounded one.** No answer is pre-filled.

---

### Question 1 — Do persistence-layer tests need a real database, and at which tier?

**Measured on disk — and the two existing guards behave DIFFERENTLY, which is decisive:**

| Guard | Mechanism | Behaviour without Docker |
|---|---|---|
| `audit_store/tests/test_pg_integration.py` | `pytest.importorskip("testcontainers.postgres")` | skips on a **missing module**, but **ERRORS at fixture setup when Docker is not running** — **these are the 5 pre-existing errors** (register #4) |
| `database/tests/conftest.py` | `_docker_available()` → `docker.from_env().ping()` | **SKIPS CLEANLY** — part of the **31 clean skips** |

**⚑ The standing hold** requires the **31 skips and 5 errors to stay exactly unchanged**, so U24's choice of guard is not
cosmetic.

**A) TWO TIERS — pure logic at tier-U with NO live DB; persistence round-trips at tier-I using `database`'s CLEAN guard
(RECOMMENDED).**
The **state machine, canonicalization, hashing, pipeline orchestration, the provider's assembly logic and the transition
rules** are **pure logic** and get **full tier-U teeth with no database at all** — CANON-1's round-trip is a pure
`bytes → object → bytes` assertion needing no table. Only the **actual SQL round-trip** (does a `BYTEA` column return the
same bytes; do the tables exist after the migration) is `@pytest.mark.integration`, guarded by **`database`'s
`_docker_available()` pattern** so it **skips cleanly and adds ZERO errors**.
**Why**: it keeps the load-bearing cluster verifiable in CI without Docker; it reuses the **known-good** guard rather than
the one that produces the existing errors; and it **respects the hold without touching the `audit_store` gap**.
**⚑ It also changes the skip count** — U24's integration tests will add **new clean skips** when Docker is absent. That is
a **visible, expected delta on the 31**, and it must be stated in the completion report rather than discovered.

**B) NO live-DB tests at all** — verify the adapter + schema-generation logic only, never execute SQL. *(Keeps the baseline
numerically identical and needs no Docker; but nothing then proves a `BYTEA` column actually round-trips bytes, or that the
migration produces the tables it claims — the persistence half would be asserted only by construction.)*

**C) Follow `audit_store`'s `importorskip` pattern for consistency with the nearest neighbour.** *(Rejected on the
evidence: that is the pattern that **produces the 5 errors**. Adopting it would grow the error count, breaking the standing
hold — and would propagate a known defect rather than the known-good guard sitting one directory away.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 2 — Does the fixture design need named families, as `llm-judge` had?

U24 has **at least five distinct scenarios needing isolation**: a **clean eager-advance** case · an **illegal-transition**
case · a **drafting-success** case · a **drafting-failure** case · a **borderline-routing** case. Precedent: `outlier-model`
(U18), `memo-extensions` (U19) and `llm-judge` (U22) each used **one shared `tests/fixtures.py` with deliberately-separate
named families**, so a change made for one target cannot silently weaken another.

**A) ONE shared `tests/fixtures.py` with deliberately-separate NAMED FAMILIES — the established convention (RECOMMENDED).**
Distinct builders: `clean_case()` (advances to `evaluated`) · `illegal_transition_cases()` (the enumerated illegal set,
returned **together** so the set cannot be silently narrowed) · `drafting_success_double()` · `drafting_failure_double()` ·
`borderline_refer_case()` (a `REFER` report that must route `EXTENDED`) · plus the offline doubles.
**⚑ Two families need the `llm-judge` treatment specifically**: `illegal_transition_cases()` returned as **one collection**
(mirroring `anchoring_pair()`'s unsplittability, so STATE-2's rejection set cannot be trimmed one case at a time), and
`drafting_failure_double()` as **its own family** (mirroring `exempt_witness_sample()`, so FAILED-1 can never be weakened
by an edit made for the success path).
**Why**: identical to the convention every prior unit followed, and the two isolation risks here are the same shape as the
ones that convention was built to prevent.

**B) Per-test inline construction, no shared module.** *(Available; but it diverges from four units' convention and makes
the illegal-transition set easy to narrow silently.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 3 — What does coverage mean for U24, given it has a persistence layer?

**⚑ The brief anticipated "`--cov` with no omit, but confirm there's no persistence-layer carve-out needed." Measured on
disk: a carve-out IS the established precedent, and it is precise.** `pyproject.toml`'s `[tool.coverage.run] omit` already
carves out **every live-DB/SQL-exec module in the build**, each with the same stated rationale:

```
"*/pg_repository.py",              # SQLAlchemy/Postgres impl — exercised via testcontainers
                                   # integration in CI, not unit-import-covered
"*/database/migration_runner.py",  # live-DB modules ... omitted from unit-tier coverage
"*/database/schema_introspector.py",  #   exactly like pg_repository.py
"*/database/fidelity_comparator.py",
"*/admin_cli/pg_writer.py",        # the SQL-exec shim ... omitted exactly like pg_repository.py
```
…and every one of those notes states the **same rule**: *"the pure-logic modules stay counted and are unit-covered to
>=90% (QA-6)."*

**A) `--cov=backend/case_lifecycle` with a NARROW persistence-shim omit, following the `pg_repository.py` precedent
verbatim (RECOMMENDED).**
**Omit exactly one thing**: U24's SQL-exec/repository shim (the module that actually issues SQL). **Everything else stays
counted and is expected at 100%** — the state machine, the transition rules, the canonicalization calls, the pipeline
orchestration, the provider's assembly logic, the migration-sequence definition. The `--cov-fail-under=90` gate is
**UNCHANGED**, and the omit comment states the precedent it follows and **which** pure-logic modules remain counted.
**Why**: it is the build's own settled answer for exactly this situation, applied without invention; omitting nothing would
force either an artificially low number or live-DB imports into the unit tier — the two outcomes the precedent exists to
avoid.

**B) NO omit at all** (the `observability` / `llm-judge` treatment). *(Those units are pure logic with **no SQL-exec
module**, so "no omit" cost them nothing. U24 has one, so the same words would mean something different here — either the
shim gets imported at tier-U or the number drops for a reason unrelated to test quality.)*

**C) Omit the whole persistence package.** *(Rejected — it would carve out the provider's **assembly logic**, which is
pure, load-bearing (COMMITBOUND-1), and fully unit-testable.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

## 4.5 Mandatory ambiguity-check (Q1–Q3 all A) — **CLEAN**

**Ran**: 2026-07-20 · **Result**: **CLEAN — 3 folds RESOLVED, no genuine gap, no surface-and-stop.**

### ✅ CASE-Req-Fold-1 [check (i)] — RESOLVED: the tier-I test is **self-contained**; U15's migrations are **NOT** needed

**Measured — `database/tests/conftest.py` is the exact template**, and it already does what U24 needs:
```python
def _docker_available() -> bool:
    try:
        import docker; docker.from_env().ping(); return True
    except Exception:
        return False

@pytest.fixture(scope="session")
def migrated_engine():
    if not _docker_available():
        pytest.skip("Docker unavailable — …")      # ⚑ INSIDE the fixture body → CLEAN SKIP
    with PostgresContainer("postgres:16") as pg:
        MigrationRunner(engine, env=env).apply_all()   # ← this unit's OWN sequence
```
**⚑ Why it skips cleanly and `audit_store` errors**: the daemon **ping happens inside the fixture body**, *before* any
container is constructed. `audit_store` reaches container construction and fails there. **U24 mirrors this template
exactly**, passing `migrations_dir=<U24's own>`.

**Does U24 need U15's migrations applied too? NO — and the reason is structural, not incidental:**
1. **No cross-unit foreign key.** `PendingRecommendation.application_id` FKs to `PendingApplication` — **both U24's own**.
   Neither references `audit_record`, `applicant_profile_snapshot` or `app_user`. The `recommendation_id` that later
   appears in `audit_record` is a **logical reference, not a DB FK** — the same posture `0001` already takes for
   `underwriter_id` (*"logical ref to app_user, **NOT a DB FK** in P1 (BR-DB-11)"*).
2. **No dependency on U15's roles.** U24's store is reached through the **`DATABASE_URL` owner engine** (Scope B
   Fold-1), so U24's migration **grants nothing to `audit_writer`/`audit_reader`** — it therefore does not require
   `0002_grants.sql` to have created those roles first.
3. **The shared tracking table is created idempotently** (`CREATE TABLE IF NOT EXISTS`) by whichever runner runs first, so
   a fresh container needs no pre-existing `applied_migrations`.

⇒ **U24's tier-I test applies ONLY U24's sequence to a fresh container. Contained.**
**⚑ One condition pinned so this stays true**: if U24's migration ever grants to a U15-owned role, this containment
breaks and the test would need U15's `0002` first. **U24's migration must grant to no U15 role** — which follows directly
from the owner-engine decision, and is recorded here so a later edit cannot silently void it.

### ✅ CASE-Req-Fold-2 [check (ii)] — RESOLVED: a `failed` case **structurally cannot** reach the commit boundary

**The concern is exactly right to raise** — if a `failed` case could be handed to `PendingCommitContextProvider`, that
would be a **real invariant violation**, not a cosmetic one.

**It cannot, by construction**: R5 is keyed by **`recommendation_id`**, which is the PK of **`PendingRecommendation`** —
and per the frozen FD (§4) a `PendingRecommendation` is **created ONLY at the `drafted` transition**. A `failed` case
**never reaches `drafted`**, so **the object R5 is keyed by never exists for it**. The provider then raises for the unknown
id and R5 returns **404**. **The failed path and the commit path do not intersect** — there is no fixture or test route
that could hand a failed case to the provider, because there is nothing to hand.

**⚑ Two things pinned so this stays structural rather than incidental:**
1. **Atomicity**: creating the `PendingRecommendation` and moving to `drafted` happen **in ONE transaction**. Otherwise a
   partial failure could leave a `PendingRecommendation` row attached to a case that ended `failed` — the *only* way the
   intersection could open. **COMMITBOUND-1 gains an explicit assertion**: **no `PendingRecommendation` exists for any case
   in state `failed`.**
2. **A positive test, not just an absence**: drive `drafting_failure_double()` to `failed`, then assert
   `provider.get(<any id>)` **raises** and that the case has **no** `recommendation_id`. *(Asserted, not assumed.)*

### ✅ CASE-Req-Fold-3 [check (iii)] — RESOLVED: **coverage-omit ≠ scan-exclusion** — the two are deliberately different sets

**This is the sharpest of the three checks, and conflating the two would be a real hole.**

**They are different mechanisms with different scopes, and ADAPTER-1's scan set is NOT narrowed by the coverage omit:**

| | `[tool.coverage.run] omit` | ADAPTER-1's structural scan |
|---|---|---|
| **Purpose** | excludes a module from **line-coverage measurement** | asserts **no U24 module bypasses the frozen adapter** |
| **Scope** | the SQL-exec shim only | **EVERY U24 production module — INCLUDING the shim** |
| **Why** | the shim is exercised at **tier-I**, not import-covered (the `pg_repository.py` precedent) | a `canon_ser` call hidden in the shim must be **caught**, not invisible |

**⚑ The shim is in the scan set precisely BECAUSE it is out of the coverage set.** Its exclusion from coverage is about
*where it is exercised*; the scan is about *what it may contain*. If the scan inherited the omit, a direct `canon_ser(...)`
call inside the shim would be **structurally invisible** — the exact failure the check anticipated.

**And the "right reason" is ASSERTED, not assumed**: ADAPTER-1 asserts the shim **contains no canonicalization call at
all** — it receives **already-canonicalized bytes** and only executes SQL. That is a **positive assertion about the shim's
contents**, so if a future edit put canonicalization inside it, ADAPTER-1 **fails** rather than shrugging. **The claim
"the shim doesn't canonicalize anything" becomes a tested property rather than a design intention.**

**⇒ Ambiguity-check CLEAN. Part 2 generated.**

---

## 5. Explicit HOLDS for Part 2

- **No NFR artifact until all `[Answer]` tags are filled**, followed by the **mandatory ambiguity-check**,
  **surfacing-and-stopping** on any genuine gap.
- **No code · no wiring · `backend/case_lifecycle/` NOT created · nothing under `backend/app/` touched ·
  `pyproject.toml` NOT edited** (the `--cov` line and any omit land at Code-Gen).
- **The frozen FD re-opened NONE** — `BR-CASE-1..14`, the five states, the CANON-SER design, the explicit routing step,
  the migration namespacing and the commit-boundary composition are **built ON, not revised**.
- **WIRE-1's contract text NOT touched · Q1-B NOT resolved · `not_wired.py` NOT renamed · U23's test NOT edited · no
  frozen unit's internals touched** (`canon_ser.py`, `canon_adapter.py`, `borderline_router.py`, `MigrationRunner`,
  `DecisionCommitService` all consumed **read-only / through existing seams**) · the **`audit_store` Docker-guard gap NOT
  touched** · **tier-B NOT authorized**.
- **The baseline hold**: **1308 passed / 31 skipped / 5 pre-existing Docker errors.** The **5 errors must stay exactly
  unchanged**; any change to the **skip count** from U24's own integration tests must be **stated, not discovered** (Q1).
- **The five invariants bind** (FD): advisory-only/human-in-the-loop · no LLM in the deterministic rules path ·
  `temperature=0` centrally fixed in the frozen adapters · bias-free · reproducibility.

---

## 6. Next step (STOP here)

Fill the three `[Answer]:` tags in §4. On your signal I will read the answers, run the **mandatory ambiguity-check**,
**embed the full Q&A in this plan file**, and generate **Part 2** — `nfr-requirements.md` (the finalized `NFR-CASE-*`
targets with acceptance/tier/rigor, the load-bearing set called out with its mechanism, a no-orphan traceability table, and
the full Security-Guardrails compliance table) + `tech-stack-decisions.md` — then present the standardized 2-option
completion message. **No NFR artifact is generated until the answers are in and checked.**
