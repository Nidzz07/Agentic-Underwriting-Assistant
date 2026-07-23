# Code Summary — `llm-judge` (U22, EPIC-6, Phase 2)

**Stage**: BUILD → Code Generation (per-unit), **Part 2 (Generation)** · **Unit**: U22 `llm-judge` · EPIC-6 · **Phase 2** ·
**Date**: 2026-07-19.
**Built ON** the frozen FD (`BR-JUDGE-1..11`), the approved NFR Requirements (eleven `NFR-JUDGE-*`), the approved NFR Design
(`P-JUDGE-1..14` · `C-JUDGE-1..5`) and the **logged Infrastructure Design SKIP** — **re-opening NONE.**
Answers **Q1–Q5 (all A)** + folds **CG-JUDGE-Fold-1..3** (plan §6.5).

> **⚑ U22 is the LAST unit of the 23-unit decomposition.** Its Code Generation is the final stage of the build.

---

## 1. Modules delivered

| File | Component | Contents |
|---|---|---|
| `backend/llm_judge/__init__.py` | — | **Deliberately empty of re-exports** (Q5-A): U22 is the terminal unit and **nothing in the build imports it**, so an export surface would be speculative API. |
| `backend/llm_judge/schemas.py` | **C-JUDGE-1** | `ProviderScopeTag` · `EvalTier` · `EXEMPT_REASON_MEMO_QUALITY` · `RubricDimension` · `GroundednessRubric` · `JudgedSample` · `DimensionScore` · `SampleScore` · `EvalRunResult` — frozen dataclasses |
| `backend/llm_judge/rubric.py` | **C-JUDGE-1** | the canonical `GROUNDEDNESS_RUBRIC` (threshold **4**, scale **5**) + its two dimensions |
| `backend/llm_judge/engine.py` | **C-JUDGE-3** | the `RubricEngine` **Protocol** + `DeferredItem` + **`DEFERRED_REGISTER`** (the three items) + `register_item()` |
| `backend/llm_judge/pipeline.py` | **C-JUDGE-2** | `IN_GATE_PROVIDERS` · `partition_by_scope` · **`is_nonvacuous_exemption_set`** · `meets_threshold` · `aggregate_sample` · `run_eval` · `score_for` |
| `backend/llm_judge/tests/fixtures.py` | **C-JUDGE-4** | the **five named families** + the **`DeclaredScoreEngine`** fake + `exemption_composition()` + `anchoring_engine()` |
| `backend/llm_judge/tests/structural.py` | **C-JUDGE-5** | the scan substrate — `production_py_files()` (**excludes `tests/`**), `authored_py_files()`, AST helpers, token sets, `load_dashboard()` |
| 15 × `tests/test_*.py` | — | one test file per target (Q4-A), mirroring the sibling convention |

**`pyproject.toml`**: one line added — `--cov=backend/llm_judge` after `--cov=backend/observability`, **no omit**, with the
standing comment. **`--cov-fail-under=90` UNCHANGED.** **`requirements.txt` NOT edited; no new dependency.**

### Header-comment deliverables
All four production modules carry the standing header (*holds no LLM · edits no frozen unit · declares no verdict · no
network/Node/npx at tier-U*), each marked **"DOCUMENTATION ONLY … never enforcement"**. `test_governance.py` asserts the
header is present; **every property it names is independently scan-enforced** elsewhere with a detector self-test.

---

## 2. Test → target map (114 tests, all green)

| Target | File | Tests |
|---|---|---|
| **EXEMPT-1** *(LOAD-BEARING — both mechanisms)* | `test_exempt.py` | 12 |
| **NOEDIT-1** *(LOAD-BEARING)* | `test_noedit.py` | 7 |
| **NOMETRIC-1** *(LOAD-BEARING)* | `test_nometric.py` | 8 |
| THRESH-1 | `test_threshold.py` | 10 |
| INGATE-1 | `test_ingate.py` | 5 |
| EXEMPTSCOPE-1 | `test_exempt_scope.py` | 5 |
| ANCHOR-1 | `test_anchor.py` | 7 |
| CLIDEFER-1 | `test_clidefer.py` | 9 |
| EVALDEFER-1 | `test_evaldefer.py` | 5 |
| DISCLOSE-1 | `test_disclose.py` | 9 |
| NODEMO-1 | `test_nodemo.py` | 6 |
| ADVISORY-1 / NOVERDICT-1 | `test_advisory.py` | 9 |
| PERF-1 | `test_perf_observed.py` | 3 |
| SEC-1 | `test_governance.py` | 7 |
| the scan substrate | `test_structural_guard.py` | 12 |

**No orphan** — all eleven `NFR-JUDGE-*` + PERF-1 + SEC-1 have teeth.

### The two load-bearing pairs, as realized
- **EXEMPT-1** — `test_exemption_positive_witness_over_the_three_sample_composition` (`scored_count == 2` ∧
  `exempt_count == 1` ∧ the Ollama sample **present**), its detector (`scored_count` reads **3** on a mis-partition), **and**
  the genuinely-separate `is_nonvacuous_exemption_set` guard, with `test_a_degenerate_set_would_report_exempt_count_zero`
  demonstrating **why** the guard exists: the degenerate set is otherwise *indistinguishable* from a correct in-gate run.
  Three tests assert the fixture families' ids are **disjoint**.
- **NOEDIT-1 / NOMETRIC-1** — the frozen-path scan (+ detector over every frozen prefix) **and** the **provenance** scan
  (no U22 module declares a metric), with the read-only property assertions **corroborating**. `test_noedit.py` also asserts
  **behaviourally** that running the suite leaves both frozen artifacts **byte-identical**.

---

## 3. ⚑ Disclosed realization notes

### 3.1 The `fixtures.py`-vs-`fakes.py` discrepancy (Q1 / CG-JUDGE-Fold-1) — **disclosed, NOT retro-edited**
The approved `nfr-design/logical-components.md` writes the fake's home as a parenthetical **`(tests/fakes.py)`**. **Measured
on disk: NO unit in this build has a `tests/fakes.py`** — every fake class lives in that unit's **`tests/fixtures.py`**
(U19's `CapturingThinkingClient`, `FakeDecisionRecordSource`, `FakeOutlierSignal`; U21's `RecordingTraceSink`,
`RecordingMetricExporter`). **The code follows the on-disk convention: `DeclaredScoreEngine` lives in `tests/fixtures.py`.**

**Why this is a clarification and not a violation**: what the approved artifact states as **binding** is *"the fake lives in
`tests/`, **NEVER** in production — so no production module can depend on it, and CLIDEFER-1's scan has a clean production
set."* **`fixtures.py` IS in `tests/`**, so every binding clause holds. The filename is load-bearing on **nothing**:
`EXPECTED_PRODUCTION_MODULES` names only the four production modules, and C-JUDGE-5's scan **excludes `tests/` wholesale**.

**Disposition — identical to the ND-Fold-1 / ANCHOR-1 disclosure at NFR Design**: the approved artifact is **left
un-retro-edited** (approved artifacts are built ON, not revised), and the discrepancy is **disclosed here** instead.

### 3.2 ADVISORY-1's verdict scan is PRODUCTION-ONLY, and that is FORCED (CG-JUDGE-Fold-2)
The frozen U4 `DecisionMemo.recommendation` field is **REQUIRED**, so every memo fixture **must** carry a verdict value.
That is the memo **under judgment — judge INPUT**, which the approved NFR text already distinguishes from a verdict *"used
as a judge OUTPUT"*. The **structural half** (no U22-owned type declares a `Recommendation`-typed field) carries the real
teeth and is unaffected by fixture content.

### 3.3 NODEMO-1's scan is deliberately ASYMMETRIC to ADVISORY-1's (CG-JUDGE-Fold-3)
NODEMO-1 **also** scans `tests/fixtures.py`, because the FD explicitly requires the hand-authored **reference memo** be
demographic-free. Three files are excluded **by necessity** — `structural.py` (holds the token list), `test_nodemo.py`
(holds the planted detector token) and `test_structural_guard.py` (holds the whole-word collision guard); **every other U22
module, including all four production modules and the fixtures carrying the reference memo, IS scanned.**
Structural braces beyond the scan: **`JudgedSample` carries no `ApplicantProfile` field**, so no demographic value can
structurally enter a judged sample (asserted in `test_judged_sample_structurally_carries_no_applicant_profile`).

### 3.4 A real defect found and fixed during TDD: a substring collision in the demographic detector
The first scan implementation used a naive substring test, which flagged **`"city"` inside `"ethnicity"`** — it would have
reported the *wrong* attribute and masked which one actually appeared. **Fixed to whole-word matching**
(`contains_token` uses `\b` boundaries), with `test_contains_token_matches_whole_words_only` added as a **regression
guard**. Recorded because the detector's honesty is the point of the target.

### 3.5 `SampleScore.aggregate`/`.passed` are `None` for exempt records — deliberately not `0.0`/`False`
`0.0`/`False` would read as *"failed"* rather than *"not scored"* — an unacceptable ambiguity in an advisory system.
`exempt_reason` then names the exemption's **scope** (EXEMPTSCOPE-1).

### 3.6 `EXEMPT_REASON_MEMO_QUALITY` is a Code-Gen realization of an approved target
EXEMPTSCOPE-1 requires the exempt record to *"carry an explicit reason tag naming memo-quality as the exemption's scope."*
The constant + the `SampleScore.exempt_reason` field are that tag's realization — **not a new FD entity**.

---

## 4. The three register items — disclosed by name, **NONE discharged**

Realized as `engine.DEFERRED_REGISTER`, each carrying **name · owner · rationale · `discharge_criteria` · `discharged=False`**
— a **structured** subject, so the negative assertion is `discharged is False` rather than prose-matching (Q3-A).

| Item | Owner | Status |
|---|---|---|
| **`PROMPTFOO-CLI-DEFERRED`** | `llm-judge` (U22) | **OPEN** — 5 criteria incl. **real-shape interop** (the criterion Q2-A named). The npx-unpinned-fetch + posthog-telemetry concerns are disclosed in the rationale. |
| **`JUDGE-EVAL-DEFERRED`** | `llm-judge` (U22) | **OPEN** — needs tier-B + live keys, **with the CLI item discharged FIRST** (the one-way prerequisite, asserted disjoint from the CLI criteria). |
| **`FEWSHOT-ANCHOR-UNIMPLEMENTED`** | **`memo-agent-core` (U4)** or a future explicitly-authorized change | **OPEN — never U22's to discharge.** |

**Anti-conflation is asserted in BOTH directions** (`test_disclose.py`): one item's presence does **not** mask the other's
removal.

---

## 5. Verification

- **Backend full suite**: **1308 passed / 31 skipped / 5 pre-existing `audit_store` Docker-absence errors** — baseline was
  **1194 / 31 / 5**, so **+114 new tests, ZERO regression**; **skips and Docker errors both exactly unchanged**.
- **Coverage**: `backend/llm_judge` at **100%** on every production module with **no omit**; global **99.86%**,
  `--cov-fail-under=90` **held**.
- **tier-U held**: no live LLM, no key, no network, no Docker, **no Node, no npx, no promptfoo import, no telemetry**.
  `test_promptfoo_is_never_imported_into_the_running_test_process` asserts it at run time.
- **tier-B**: **NOT authorized, NOT required, not reached.**

**Holds verified**: no frozen unit edited (U4's `DecisionMemo`/`RuleResultReport` imported **read-only**, its test tree
untouched; U19's adapters **not imported at all** — U22 drives no adapter at tier-U; U21's `METRIC_DEFINITIONS` and U23's
`grafana-dashboard.json` read **read-only**, **neither suite re-run**, both asserted **byte-identical after the run**);
**no new dependency**; the CLOSED composition root untouched; **no other unit started**; the **23-unit decomposition
unchanged**.
