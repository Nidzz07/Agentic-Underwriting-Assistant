# Code Generation Plan (Part 1) — `case-lifecycle` (U24, Scope B)

**Phase / Stage**: BUILD → per-unit loop → **Code Generation, Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `case-lifecycle` (U24) · FD ✅ → NFR Requirements ✅ → NFR Design ✅ → **Infrastructure Design ⏭️ SKIPPED
(logged, rule-justified — the 21st skip)** → **Code Generation ← here (the 5th and LAST of U24's stages)**
**Unit**: U24 · **Scope B** · **Date**: 2026-07-20 · **Depth**: comprehensive (TDD per QA-6)
**Status**: **Q1–Q5 ANSWERED (all A) · ambiguity-check CLEAN (§6.5) · Part 2 GENERATED.** 110 tier-U tests + 5 tier-I green; every counted module at 100%; backend **1418 passed / 36 skipped / 5 pre-existing Docker errors**.

Built **ON** the frozen FD (`BR-CASE-1..14`), the approved **NFR Requirements** (seventeen `NFR-CASE-*`), the approved
**NFR Design** (`P-CASE-1..15` · `C-CASE-1..8`) and the **logged Infrastructure Design SKIP** — **re-opening NONE.**

> **⚑ U24's Code Generation completes the FIRST unit added after the original 23-unit decomposition.** The in-place
> composition-root wiring pass comes **only after this stage closes**.

**Live baseline measured this session**: `pytest backend --collect-only` → **1344 collected**, reconciling exactly with
**1308 passed / 31 skipped / 5 pre-existing `audit_store` Docker-absence errors** (1308 + 31 + 5 = 1344).

---

## 1. Component → module map (concrete files under `backend/case_lifecycle/`)

| Component | File(s) | Contents |
|---|---|---|
| **C-CASE-1** | `states.py` | `CaseState` · **`LEGAL_TRANSITIONS`** (the single source of truth) · `assert_legal()` · `IllegalTransition` · **`case_to_memo_view_state()`** (pure, `Literal["ready","pending"]`) |
| **C-CASE-2** | `schemas.py` | `PendingApplication` · `PendingRecommendation` — frozen dataclasses, `BYTEA` + `content_hash` + first-class scalar stamps |
| **C-CASE-3** | `repository.py` | the **SQL-exec shim** — the only module issuing SQL. **⚑ coverage-OMITTED *and* scan-INCLUDED** (CASE-Req-Fold-3) |
| **C-CASE-4** | `store.py` (+ the fake in `tests/fixtures.py`) | the **`CaseStore` Protocol WITH `atomic()`**; the tier-U **in-memory buffering fake** lives in `tests/` |
| **C-CASE-5** | `pipeline.py` | `CasePipeline` · **`DraftOutcome`** · the **explicit `route_borderline` call** |
| **C-CASE-6** | `provider.py` | `PendingCommitContextProvider` — the real `CommitContextProvider`, **context only** |
| **C-CASE-7** | `migrations/*.sql` + `migrations/checksums.json` + `migrate.py` | U24's own sequence + the **production collision guard** + `apply_case_migrations()` |
| **C-CASE-8** | `tests/fixtures.py` · `tests/structural.py` · `tests/test_structural_guard.py` + one file per target | the **five named families** + the in-memory fake; the **five scans** with detector self-tests |

Plus `backend/case_lifecycle/__init__.py` and `backend/case_lifecycle/tests/__init__.py`.
**⚑ Exact layout confirmed by Q1** (NFR Design left it *"OPEN — exact names finalized at Code-Gen"*).

### 1.1 Header-comment deliverables — **explicit on ALL production modules**
Each production module carries a docstring stating: *holds no LLM · edits no frozen unit · declares no verdict · reaches
no network at tier-U · **never re-implements the commit gate, the authz check, or a write to `audit_record`***. Per the
standing rule these are **documentation only, never enforcement** — every property is independently enforced by a
C-CASE-8 scan with a detector self-test.

---

## 2. TDD test → target map (all **seventeen** `NFR-CASE-*` at their NFR-pinned tier)

**TDD per QA-6**: each test is written **before** the production code it exercises, in §3's leaf-first order.

### ⚑ The three LOAD-BEARING targets — full-highest rigor

| Target | File | Teeth | Detector self-test |
|---|---|---|---|
| **CANON-1** *(behavioural)* | `test_canon.py` | round-trip **byte-identical** for both rich shapes · `Decimal`/`date` **return as themselves** · `content_hash` **stable across runs** | **a flipped byte FAILS** the hash check · a `float` **raises** `CanonSerError` |
| **ADAPTER-1** *(structural)* | `test_adapter.py` | AST scan over **every production module** — no direct `canon_ser`/`canon_deserialize`, no re-implemented `.model_dump(mode="python")`. **⚑ `repository.py` IS IN SCOPE**, with a **positive assertion it contains no canonicalization call at all** | a synthetic direct `canon_ser(...)` **is flagged** · a synthetic **`model_dump(mode="json")` is flagged** · no `$`-prefixed key |
| **COMMITBOUND-1** *(structural + behavioural)* | `test_commitbound.py` | **(a)** no U24 module implements a gate, an authz check, or an `audit_record` write · **(b)** `get()` returns a `CommitContext` and **nothing more**, raising for an unknown id · **⚑ (c) POSITIVE**: **no `PendingRecommendation` exists for any case in state `failed`**, and driving `drafting_failure_double()` to `failed` then calling the provider **raises** · **(d)** the `drafted` transition + recommendation creation share **one `atomic()`** | a synthetic gate predicate · a synthetic `authorize(...)` · a synthetic `INSERT INTO audit_record` — **each flagged** |

### The remaining targets

| Target | File | Teeth |
|---|---|---|
| **STATE-1** | `test_states.py` | every **legal** transition accepted; each driven through the corresponding **frozen seam** (spy confirms the call) |
| **STATE-2** | `test_states.py` | **⚑ exhaustiveness sweep** — `set(product(CaseState, CaseState)) - LEGAL_TRANSITIONS`, **every member asserted rejected**; plus named landmarks (skip-evaluation · a backward move · a terminal exit) via the **unsplittable** `illegal_transition_cases()` |
| **EAGER-1** | `test_eager.py` | submission reaches `evaluated`; both payloads + hashes persisted; **⚑ a fault injected mid-`atomic()` leaves NO partial row** (the buffering fake makes this non-vacuous) |
| **TRIGGER-1** | `test_trigger.py` | **the R4 read path invokes the pipeline ZERO times** (spy records no calls); state unchanged after the read |
| **FAILED-1** | `test_failed.py` | `drafting_failure_double()` drives the case to `failed`; `failed` **internally distinguishable** from `evaluated` |
| **PROJECT-1** | `test_project.py` | a `failed` case yields a **WIRE-1-VALID** `"pending"`; **DOC-1-style token checklist** for register **#14** (name + owner + rationale; no discharge claimed); **detector** — token removal fails |
| **CANONTIME-1** | `test_canontime.py` | both payloads + hashes after submission; the four stamps at drafting; `content_hash` **always matches** its stored bytes |
| **ROUTE-1** | `test_route.py` | a **spy** records `route_borderline` called with the **real** `(rule_report, outlier)` args; `REFER` → `EXTENDED` and **the adapter receives it**; **⚑ re-derivation from stored state alone reproduces the mode** |
| **MIGNAME-1** | `test_migname.py` | U24's filenames **disjoint** from U15's; **detector — a synthetic colliding filename IS flagged**; `verify_checksums` passes against U24's own manifest |
| **MIGSCOPE-1** | `test_migscope.py` | never passes U15's default `MIGRATIONS_DIR` · **no CLI entrypoint** (#8 not adopted) · **grants to no U15 role** |
| **NOMETRIC-1** | `test_nometric.py` | provenance scan (no metric declared, + detector) **+** the corroborating read-only check of U21's five and U23's five panels — **NEITHER SUITE RE-RUN** |
| **PERSIST-1** *(tier-I)* | `test_persist_integration.py` | **⚑ `@pytest.mark.integration`, using `database`'s known-good guard VERBATIM** — `_docker_available()` **ping inside the fixture body** → **CLEAN SKIP, zero errors**. Applies **only U24's** sequence to a fresh container; the two tables exist; a `BYTEA` **round-trips byte-identically** and its hash still verifies; the stamps round-trip |
| **PERF-1** | `test_perf_observed.py` | no timing assertion anywhere in U24; no SLO declared |
| **SEC-1** | `test_governance.py` | the scoped-exclusions posture; the two register items **named, not discharged** |
| *(substrate)* | `test_structural_guard.py` | the five scans' own self-tests + the `EXPECTED_PRODUCTION_MODULES` non-vacuity guard |

**No orphan** — all seventeen targets have teeth.

---

## 3. Leaf-first build order (TDD at each step)

1. **C-CASE-1 `states.py`** — no dependencies. Tests first: STATE-1, STATE-2's exhaustiveness sweep, PROJECT-1's pure
   projection.
2. **C-CASE-2 `schemas.py`** — depends on **frozen U4/U3 shapes, read-only**. CANON-1's round-trip teeth land here.
3. **C-CASE-4 `store.py` Protocol + the tier-U in-memory fake** — the fake **buffers-and-discards** (the
   `InMemoryAuditRepository` pattern), enabling EAGER-1's non-vacuous "no partial row".
4. **C-CASE-3 `repository.py`** — the SQL shim. **Built but NOT exercised at tier-U**; reached only by PERSIST-1 (tier-I).
5. **C-CASE-5 `pipeline.py`** — depends on 1/2/4 + the frozen pipeline seams. EAGER-1 · TRIGGER-1 · FAILED-1 ·
   CANONTIME-1 · ROUTE-1.
6. **C-CASE-6 `provider.py`** — depends on 2/4. COMMITBOUND-1's behavioural half.
7. **C-CASE-7 `migrations/` + `migrate.py`** — independent. MIGNAME-1 · MIGSCOPE-1 · then **PERSIST-1 (tier-I)**.
8. **C-CASE-8 `tests/structural.py` + `test_structural_guard.py`** — **scans the COMPLETED production tree**, so last.
   ADAPTER-1 · COMMITBOUND-1's structural half · MIGSCOPE-1 · NOMETRIC-1 · PROJECT-1's checklist.
9. **Coverage gate** — add the `--cov` line + the narrow omit; run the full backend suite; confirm no regression.

---

## 4. Coverage / quality gate

- **`--cov=backend/case_lifecycle`** with a **narrow omit of exactly the SQL-exec shim** (`*/case_lifecycle/repository.py`),
  following the **`pg_repository.py` precedent verbatim**. The omit comment states **which precedent it follows** and
  **which modules remain counted** (Q5).
- **Everything else counted and expected at 100%**: `states.py` · `schemas.py` · `store.py` · `pipeline.py` ·
  `provider.py` · `migrate.py`.
- **`--cov-fail-under=90` UNCHANGED.**
- **⚑ Baseline expectations, stated as anticipated deltas — not to be discovered:**
  - **The 5 pre-existing `audit_store` Docker errors MUST stay exactly 5.** U24 uses `database`'s clean-skip guard
    precisely so it **adds zero errors**.
  - **The 31 skips WILL INCREASE** when Docker is absent, by the number of U24 tier-I tests in
    `test_persist_integration.py`. **This is expected and correct** — it is what a *clean* skip looks like. The completion
    report will state the new number **and** confirm the error count is unchanged.
  - Passed count rises by U24's tier-U tests, with **zero regression** elsewhere.

---

## 5. Explicit HOLDS

- **No frozen unit edited.** `database` (U15)'s migration machinery (`MigrationRunner`, `verify_checksums`), `canon_ser.py`,
  `canon_adapter.py`, `borderline_router.py`, `DecisionCommitService`, `CommitContext` and the `CommitContextProvider`
  Protocol are all consumed **read-only / through existing seams**.
- **WIRE-1's contract text untouched · Q1-B unresolved · `not_wired.py` NOT renamed · U23's test NOT edited.**
- **The `audit_store` Docker-guard gap untouched — the 5 errors must stay exactly unchanged.**
- **tier-B NOT authorized.** **Nothing under `backend/app/` touched** — the composition-root wiring pass comes **only
  after this stage closes**.
- **The two new register items disclosed, NOT discharged**: **#13 `NOTWIRED-FILENAME-STALE`** (now **amplified** — once
  R2–R5 are wired in place the stale-named file sits on the primary user journey) · **#14
  `MEMOVIEW-FAILED-STATE-UNMODELLED`**.
- **No new dependency** — `testcontainers[postgresql]` already floored **and** installed; **`requirements.txt` NOT
  edited**. The only `pyproject.toml` change is the `--cov` line + its omit entry.
- **The five invariants bind**: advisory-only/human-in-the-loop · no LLM in the deterministic rules path ·
  `temperature=0` centrally fixed in the frozen adapters · bias-free · reproducibility.

---

## 6. Clarifying questions — fill each `[Answer]:` tag

> **Code-Gen-only choices.** None re-opens a frozen or approved decision. **C/D "Other"** — describe after the tag.

---

### Question 1 — Confirm the exact module layout

NFR Design left it *"OPEN — sized to the components; exact names finalized at Code-Gen."* The `StructuralGuard`'s
`EXPECTED_PRODUCTION_MODULES` needs a definite set.

**A) Six production modules mirroring the component names, flat (RECOMMENDED).**
`states.py` · `schemas.py` · `store.py` · `repository.py` · `pipeline.py` · `provider.py` · `migrate.py` + `migrations/`
+ `__init__.py`. **Why**: one module per C-CASE component makes the component→module map **1:1 and auditable**; flat
matches every sibling (`outlier_model`, `memo_extensions`, `observability`, `llm_judge` are all flat); and it keeps the
**omit surgical** — exactly `repository.py`, nothing else.
*(Note: `migrate.py` is a 7th small module holding `apply_case_migrations` + the collision guard — separated from
`repository.py` so the omit does not accidentally swallow the guard, which must stay counted.)*

**B) Collapse `store.py` into `repository.py`** (Protocol beside its SQL implementation). *(Fewer files; but the omit
would then swallow the **Protocol** too, and the Protocol is pure and must stay counted — it would silently reduce what
the coverage gate measures.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 2 — The exact migration filename

BR-CASE-11 requires **descriptive namespacing**: the runner globs `[0-9][0-9][0-9][0-9]_*.sql`, so a `u24_` *prefix*
would not match — the namespace must live in the **descriptive part**. U15's are `0001_initial_schema.sql` /
`0002_grants.sql`.

**A) `0001_case_lifecycle.sql` — one file (RECOMMENDED).**
Numerically independent of U15's sequence (both may be `0001` — the tracking PK is the **bare filename**, so
`0001_case_lifecycle.sql` ≠ `0001_initial_schema.sql`), and **descriptively unmistakable**. **One file only**: U24 needs
**no grants migration**, because its store is reached via the **owner engine** and **grants to no U15 role**
(MIGSCOPE-1).

**B) `0001_pending_case_store.sql`** — names the tables rather than the unit. *(Equally distinct; but "case_lifecycle"
matches the unit name, which is how a reader maps a migration back to its owner.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 3 — How does the production collision guard learn U15's filenames?

Q3-A put the guard **in production**, on the apply path. **How it obtains the other sequence's names is open**, and the
choice decides whether it can go stale.

**A) Read them live from the frozen module — `migration_files(U15_MIGRATIONS_DIR)` (RECOMMENDED).**
```python
def _assert_no_collision_with_u15() -> None:
    ours   = {p.name for p in migration_files(CASE_MIGRATIONS_DIR)}
    theirs = {p.name for p in migration_files(DB_MIGRATIONS_DIR)}   # frozen default, READ-ONLY
    if ours & theirs:
        raise MigrationNameCollision(sorted(ours & theirs))
```
**Why**: it is **always current** — if U15 ever adds `0003_*.sql`, the guard sees it **immediately**, with no U24 edit.
It reuses the **frozen parameterized helper** (`import-to-read ≠ edit`), and it cannot drift because there is **no copy**.

**B) A hardcoded frozen list of U15's two filenames.** *(No import at all; but it **goes stale silently** the moment U15
gains a migration — and a stale collision guard is worse than none, because it reads as protection.)*

**C) Compare only the numeric prefixes.** *(Rejected — the tracking PK is the **bare filename**, not the prefix, so
prefix-comparison would flag safe pairs and miss unsafe ones.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 4 — Test-file organization, and how the load-bearing pairs are shown

**Measured precedent in `llm-judge`** (15 test files, one per target):
- **EXEMPT-1 — ONE target with TWO mechanisms → ONE file** (`test_exempt.py`), *"so their complementarity is visible in
  one place."*
- **NOEDIT-1 and NOMETRIC-1 — TWO targets → TWO files** (`test_noedit.py`, `test_nometric.py`).

**A) Follow that precedent exactly (RECOMMENDED).**
**CANON-1 and ADAPTER-1 are TWO targets → TWO files** (`test_canon.py`, `test_adapter.py`), each with a **docstring
cross-reference** stating the pairing and *why neither alone is sufficient*. **COMMITBOUND-1 is ONE target with two halves
→ ONE file** (`test_commitbound.py`), so its structural and behavioural halves sit together, exactly as `test_exempt.py`
does. Everything else one file per target, plus `fixtures.py` · `structural.py` · `test_structural_guard.py`.
**Why**: it applies the sibling rule *as measured* rather than inventing a new one — **target count decides file count**,
and the pairing is carried by **cross-referencing docstrings**, which is how `llm-judge` documented its own pairs.

**B) Put CANON-1 and ADAPTER-1 in ONE file** (`test_canonicalization.py`) to make the pair visually obvious. *(Available,
and it does surface the pairing; but it breaks the one-file-per-target rule for **two distinct targets**, which the
NOEDIT/NOMETRIC precedent kept separate.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 5 — The `pyproject.toml` omit comment wording

Every existing omit entry carries a comment naming the precedent and stating what remains counted.

**A) Mirror the established wording (RECOMMENDED).**
```toml
# case-lifecycle (U24, Scope B) — the SQL-exec shim is exercised via testcontainers
# integration in CI (auto-skipped without Docker); omitted from unit-tier coverage exactly
# like pg_repository.py. All pure-logic modules — states.py (incl. LEGAL_TRANSITIONS + the
# pure wire projection), schemas.py, store.py (the Protocol), pipeline.py, provider.py and
# migrate.py (incl. the production collision guard) — stay counted and unit-covered to
# >=90% (QA-6). NOTE: repository.py is OMITTED FROM COVERAGE but REMAINS IN ADAPTER-1's
# SCAN SET (CASE-Req-Fold-3). See build/case-lifecycle/code/code-summary.md.
"*/case_lifecycle/repository.py",
```
**Why**: it matches the five existing entries' shape, and the **final NOTE** is U24's one addition — recording that the
omit is **coverage-only, never scan-exclusion**, so a future reader cannot mistake one for the other.

**B) Minimal comment** (precedent reference only). *(Shorter; but it loses the omit-vs-scan distinction, which is exactly
the thing CASE-Req-Fold-3 had to resolve.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

## 6.5 Mandatory ambiguity-check (Q1–Q5 all A) — **CLEAN**

**Ran**: 2026-07-20 · **Result**: **CLEAN — 3 folds RESOLVED, no genuine gap.** **⚑ Check (iii) surfaced a real
bypass risk, now pinned.**

### ✅ CG-CASE-Fold-1 [check (i)] — no cycle, no import-order issue

**Measured**: `backend/database/migration_runner.py` imports **only** `os` · `re` · `pathlib` · `typing` · `sqlalchemy` —
**no `backend.*` application import at all**. And `database` (U15) **predates U24 by the entire build**, so it cannot
reference it. ⇒ the dependency is **strictly one-way: `case_lifecycle → database`**. **No cycle is possible.**
**Import-order**: `MIGRATIONS_DIR` is computed from `Path(__file__)` at import — **no environment read, no engine
construction, no side effect** — so importing it from `migrate.py` is safe at any point. **`import-to-read ≠ edit`.**

### ✅ CG-CASE-Fold-2 [check (ii)] — the seven modules match every component responsibility exactly

| NFR Design responsibility | Module | ✓ |
|---|---|---|
| `CaseState` · `LEGAL_TRANSITIONS` · `assert_legal` · `case_to_memo_view_state` | `states.py` | ✓ |
| `PendingApplication` · `PendingRecommendation` | `schemas.py` | ✓ |
| the `CaseStore` Protocol **with `atomic()`** | `store.py` | ✓ |
| the SQL-exec shim | `repository.py` | ✓ |
| `CasePipeline` · `DraftOutcome` · the explicit `route_borderline` call | `pipeline.py` | ✓ |
| `PendingCommitContextProvider` | `provider.py` | ✓ |
| `apply_case_migrations` + the production collision guard | `migrate.py` | ✓ |
| the in-memory buffering fake | **`tests/fixtures.py`** *(test-side by design)* | ✓ |

**Nothing missing, nothing extra.** `EXPECTED_PRODUCTION_MODULES` = those **seven** filenames; `__init__.py` stays in
`production_py_files()` but out of the expected set, **mirroring `llm_judge`'s substrate exactly**.

### ⚑ CG-CASE-Fold-3 [check (iii)] — a REAL bypass risk, caught and pinned

**The concern is exactly right.** If PERSIST-1's fixture called `MigrationRunner(engine, migrations_dir=…)` **directly**,
the **production collision guard would be bypassed entirely** — it would never execute on the path PERSIST-1 verifies, so
the one test that exercises real migration application would **prove nothing about the guard**.

**⇒ PINNED: PERSIST-1's fixture MUST call `apply_case_migrations(engine)`**, the production entry point, so the guard
runs **on the verified path**. Calling `MigrationRunner` directly is **forbidden**, and **MIGSCOPE-1 gains an assertion**
that **no U24 test constructs `MigrationRunner` directly** — turning "the guard is on the real path" into a **tested
property rather than a convention**.

**⇒ Ambiguity-check CLEAN. Part 2 generated.**

---

## 7. Next step (STOP here)

Fill the five `[Answer]:` tags in §6. On your signal I will read the answers, run the **mandatory ambiguity-check**,
**embed the full Q&A in this plan file**, and generate **Part 2** — the modules, the test suite, the coverage line, a live
full-suite run, and `guide-docs/build/case-lifecycle/code/code-summary.md` — then present the standardized 2-option
completion message.
**NO CODE is generated until the answers are in and checked.** This is the **5th and LAST of U24's stages**, and its
approval **completes the first unit added to the original 23-unit decomposition**.
