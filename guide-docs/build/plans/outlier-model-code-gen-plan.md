# Code Generation — Plan (Part 1) — `outlier-model` (U18, C3, **Phase 2**)

**Stage**: BUILD → per-unit loop → **Code Generation Part 1 (Plan)** · **Unit**: U18 `outlier-model` · C3 · **Phase 2** · **Depth**: comprehensive · **Date**: 2026-07-16
**Built ON** the frozen FD (**BR-OUT-1..10**; the four-component inventory + method signatures; `OutlierResult`/`FlaggedFeature`/`OutlierProvenance`; the imputation policy) + approved NFR Requirements (**thirteen `NFR-OUT-*`**; the RNG-leak-proof determinism teeth; the threshold positivity guard; the forward-looking-scan self-test discipline) + approved NFR Design (patterns **P-OUT-1..9**; the five logical components + exact method signatures; **CG-ND-OUT-Fold-1's imputed-mask reconciliation**) — **re-opening none.** **Python 3.12, pytest TDD tests-first, leaf-first** — mirroring every realized backend unit (`backend/<unit>/` + `tests/`, `pyproject` `--cov`). **This plan is the single source of truth for `outlier-model` Code Generation.**

**Status**: **Part 2 GENERATED — the six `[Answer]` tags (§7) are FILLED (all A); ambiguity-check RUN → CLEAN (no surface-and-stop); §4 Steps 0–9 executed TDD tests-first / leaf-first (all `[x]`).** `backend/outlier_model/` realized (7 production modules + 15 test files + `fixtures.py`/`structural.py`). Backend suite **1011 passed / 31 skipped** (960 baseline + **51** new; + the 5 pre-existing Docker-absence errors, unchanged); `backend/outlier_model` **100%**; the `--cov-fail-under=90` gate holds at **99.84%**. **STOPPED at the diff-review gate** — awaiting approval before this last U18 stage (and the first Phase-2 unit) is considered complete. Full Q&A re-embedded (§7, standing convention). **This is the LAST stage for `outlier-model`.**

### Part-2 ambiguity-check verdict (CLEAN — no genuine gap; realizations noted, none improvised)
- **Derivations mirror-not-import**: `dti_ratio`/`income_multiple` (debt/income, cover/income; guard-before-divide) + the count derivations are **computed locally**, mirroring the frozen `rules_engine` semantics — NOT imported (SCOPE-1: only `corpus_generator.records` call-only + `intake.schema` by shape; the pervasive mirror-not-import discipline). `Decimal→float` at the numeric feature boundary (`FeatureInputs.values: tuple[float,…]`).
- **Near-zero-variance z-guard (realization)**: a corpus feature whose std is float-noise on an analytically-constant column (e.g. a fixed dti fraction) would explode `z`; the model treats std negligible *relative to its scale* as zero-variance → `z=0` (mirrors sklearn `StandardScaler` near-constant handling). Exact-`std==0` integer-constant columns (`health_flag_count`, `documents_missing_count`) also covered.
- **IsolationForest hyper-params / `outlier_model_version` string / TreeExplainer wiring**: the FD §5 / NFR-Req §4 **Code-Gen-deferred** realizations — chosen here (`n_estimators=100`, `contamination="auto"`; `outlier-model/1.0.0+sklearn-<v>+fv1`; `shap.TreeExplainer(..., check_additivity=False)` — empirically verified on IsolationForest). PROV-1 asserts presence+shape, not the literal string.
- **`imputed → z=0` observability**: proven by unit-testing the pure `_z_scores` helper (mask forces 0) — public API stays `score()`.

---

## 1. What Code-Gen builds (and what it must NOT touch)

### 1.1 Builds — the five components as code + their TDD tests (under `backend/outlier_model/`)
`FeatureVectorBuilder` + `OUTLIER_FEATURE_FIELDS` + `FeatureInputs` + `CorpusImputer` · `CorpusSource` · `OutlierModel` + the injected `RandomState` + fit/score lifecycle · `ShapExplainer` (the sole `FlaggedFeature` constructor) · the `OutlierResult`/`FlaggedFeature`/`OutlierProvenance` Pydantic schemas · the `StructuralGuard` test substrate. **JS/JSX? No — this is a backend Python library** (contrast the six UI units).

### 1.2 Does NOT touch (held closed)
- **The 17 frozen P1 units** (`backend/<unit>/`, `frontend/src/<unit>/`) — imported by shape where consumed, edited never.
- **The closed composition root** (`backend/app/`, `frontend/src/app/`).
- **WIRE-1**; the **tier-B corpus run** (unauthorized, not required); the **`audit_store` Docker-guard gap**.
- **No consumer** (`memo_agent_core`/`ui_outlier_view`/`observability`) imported; **no `quality_gates`** import.

### 1.3 Guardrails held (skill + NFR-Design)
- **#1/#3 advisory-only / no-LLM** (ADVISORY-1 scan); **#5/#6 reproducibility + bias-free** (DET-1 + BIAS-1 by construction); **#8 explainability** (EXPLAIN-1 by construction). Header comments are **explicit Code-Gen deliverables** documenting each by-construction guarantee — **documentation only, not enforcement** (Q1-A of NFR-Design).

## 2. Component → module map (`backend/outlier_model/`) — signatures pinned in `logical-components.md`

| Component | Module (planned) | Exports / role | By-construction deliverable |
|---|---|---|---|
| **constants + projection** | `feature_fields.py` | `OUTLIER_FEATURE_FIELDS: frozenset[str]` (the 9 numeric names) + `FeatureInputs` (frozen dataclass: `values: tuple[float,...]`, `imputed: tuple[bool,...]`, **no demographics field**) | header comment: numeric-only allow-list; `FeatureInputs` has no demographic/categorical field (P-OUT-1) |
| **C-OUT-1 `FeatureVectorBuilder`** | `feature_vector.py` | `field_order()`, `fit_imputer(corpus_profiles) -> CorpusImputer`, `project(profile, imputer) -> FeatureInputs`, `build_matrix(corpus_profiles, imputer)` + `CorpusImputer` (frozen, `medians`) | header comment: reads **only** `OUTLIER_FEATURE_FIELDS`; imputes missing → corpus median **and sets the `imputed` mask** (CG-ND-OUT-Fold-1); `demographics` structurally absent |
| **C-OUT-2 `CorpusSource`** | `corpus_source.py` | `from_records(records)`, `from_file(path)`, `profiles(records)`, `corpus_version(manifest)` | header comment: read-only dual-source seam; **mirrors — never imports —** `corpus_loader.py`; `corpus_generator.records` **call-only**; never triggers a build / never an LLM |
| **schemas** | `schemas.py` | `OutlierResult`, `FlaggedFeature` (`shap_value` **required**, no default), `OutlierProvenance` (`{corpus_version, seed, outlier_model_version}` required), `FlagDirection` enum — all `frozen=True`, `extra="forbid"` | header comment: zero-unexplained + provenance-complete **by schema** (P-OUT-4/7) |
| **C-OUT-4 `ShapExplainer`** | `shap_explainer.py` | `explain(fitted_forest, feature_inputs, candidates) -> list[FlaggedFeature]` — the **SOLE `FlaggedFeature` constructor**; `explain([]) -> []` short-circuit | header comment: sole constructor of `FlaggedFeature`; a flag cannot exist without a SHAP value (P-OUT-4) |
| **C-OUT-3 `OutlierModel`** | `model.py` | `fit(corpus_profiles, manifest, explainer) -> FittedOutlierModel` (constructs `np.random.RandomState(manifest.seed)`, injects the **instance**); `FittedOutlierModel.score(profile) -> OutlierResult` | header comment: seed single-sourced from `CorpusManifest.seed`; **only** RNG source is the injected local instance (global `np.random.*` never touched); constructs **no** `FlaggedFeature` (P-OUT-2/5) |
| **C-OUT-5 `StructuralGuard`** | `tests/*` (test-only) | the scan substrate (§3) | — |

**Tests** live in `backend/outlier_model/tests/` (mirroring every realized backend unit). **No file under any frozen `backend/<unit>/` tree is created or modified.**

## 3. TDD test → `NFR-OUT-*` target map (every target at its NFR-pinned tier)

| Target | Test (file :: focus) | Tier |
|---|---|---|
| **BIAS-1** *(load-bearing, full-highest)* | `test_no_demographic_read.py` (AST scan: no `.demographics`/`full_name`/`gender`/`city` in a feature path + `set(field_order())==OUTLIER_FEATURE_FIELDS` + detector self-test) · `test_swap_invariance.py` (**teeth**: identical financials, swapped name/gender/city → **byte-identical `FeatureInputs` AND `OutlierResult`**) | structural (AST) + component (teeth) |
| **DET-1** *(load-bearing, full-highest)* | `test_determinism.py` (**teeth**: same corpus+seed+inputs → **byte-identical `OutlierResult` across N≥2 runs**, **and** byte-identical **across a global-RNG perturbation between the runs** — proving seed-locality, CG-NFR-OUT-Fold-1) · `test_no_global_rng.py` (AST/scan: no global `np.random.<fn>` in a scoring path + self-test) | component (teeth) + structural |
| **FEAT-1** | `test_feature_fields.py` (allow-list numeric-only; the 3 categoricals absent; documented exclusions) | structural |
| **IMPUTE-1** | `test_imputation.py` (**mask-driven zero-flag teeth, post-Fold-1**: a profile with a deliberately-missing optional → the feature is `imputed=True`, its flagging z-score is **0 by the mask**, it **never** appears in `flagged_features`; same `(corpus,seed)`→same imputed value) | component (teeth) |
| **THRESHOLD-1** | `test_threshold.py` (exactly one named constant; **strictly `>0`** guard; flag-selection **parameterized off the constant** + one inclusive-boundary case at the default) | component |
| **EXPLAIN-1** | `test_flagged_feature_schema.py` (**construction-time**: `FlaggedFeature(...)` **raises** without `shap_value`) · `test_single_constructor.py` (structural: `FlaggedFeature(` constructed in **exactly one place** — the explainer — + self-test) | component (construction) + structural |
| **COMPOSE-1** | `test_score_compose.py` (`outlier_score` from IsolationForest; `flagged_features` are exactly the non-imputed `|z|>=threshold` features, each w/ `shap_value`+`direction`; normal applicant → `[]` + valid score) | component |
| **CORPUS-1** | `test_corpus_source.py` (`from_records` & `from_file` yield the same `profile` shape; `from_file` **never** invoked by the default path — tier-B independence; `corpus_generator.records` call-only) | component + structural |
| **PROV-1** | `test_provenance.py` (every `OutlierResult` carries `corpus_version`+`seed`+`outlier_model_version`, none omitted; `seed==CorpusManifest.seed`; no `rulebook_version`) | component |
| **SCOPE-1** | `test_reference_not_own.py` (AST no-import of `quality_gates`/`memo_agent_core`/`ui_outlier_view`/`observability`; **the two forward-looking scans carry mandatory detector self-tests**; `quality_gates`+`memo_agent_core` non-vacuous today) | structural |
| **ADVISORY-1** | `test_advisory_only.py` (no `Recommendation`-producing path, no LLM/write/DB import, no verdict field + self-test) | structural |
| **PERF-1** | `test_perf_observed.py` (SHAP+fit runtime **recorded/observed**, non-gating; tree-model TreeExplainer fast path) | observed / soft |
| **SEC-1** | governance — the Security-Guardrails table (no runtime test) | N/A |

**Every `NFR-OUT-*` mapped; no orphan.** No test imports a consumer, a `quality_gates` module, or exercises the real tier-B corpus.

## 4. Leaf-first build order (numbered Part-2 steps — NOT executed; on explicit go)

- [x] **Step 0 — Scaffold** `backend/outlier_model/` (`__init__.py`, `tests/`) + extend `pyproject` `--cov=backend/outlier_model` (Q6). Backend suite still collects **960/31** baseline. ✅
- [x] **Step 1 — `feature_fields.py`**: `OUTLIER_FEATURE_FIELDS` (9 numeric) + `FeatureInputs` (values+imputed only, no demographics field) + header comment. ✅
- [x] **Step 2 — `corpus_source.py`**: dual-source seam, mirrors `corpus_loader.py`, `corpus_generator.records` call-only + header comment. ✅
- [x] **Step 3 — `feature_vector.py`**: `CorpusImputer` + `fit_imputer`/`project`/`build_matrix` (+ `field_order`); accessor allow-list w/ module-load `assert set(_ACCESSORS)==OUTLIER_FEATURE_FIELDS`; imputation → median **+ `imputed` mask**; mirror-derived `dti`/`income_multiple`; header comment. ✅
- [x] **Step 4 — `schemas.py`**: `OutlierResult`/`FlaggedFeature`/`OutlierProvenance`/`FlagDirection` (frozen, `extra="forbid"`; `shap_value` required, no default) + header comment. ✅
- [x] **Step 5 — `shap_explainer.py`**: `explain(...)` the **sole `FlaggedFeature` constructor** + `FlagCandidate`; empty-candidate short-circuit; TreeExplainer; header comment. ✅
- [x] **Step 6 — `model.py`**: `OutlierModel.fit` (injects `RandomState(manifest.seed)`) + `FittedOutlierModel.score` (IsolationForest score + non-imputed z-flags via `_z_scores`/`_candidates` + `ShapExplainer` + provenance); `Z_SCORE_FLAG_THRESHOLD=3.0` + `>0` guard; header comment. ✅
- [x] **Step 7 — `StructuralGuard`** (`tests/structural.py` + 5 scans): `no_demographic_read` / `no_global_rng` (+ negative self-test allowing `from numpy.random import RandomState`) / `single_FlaggedFeature_constructor` / `reference_not_own` (incl. forward-looking `ui_outlier_view`/`observability`) / `advisory_only` — each AST-based with a detector self-test + non-vacuity guard. ✅
- [x] **Step 8 — Coverage / quality gate**: `backend/outlier_model` **100%**; backend suite **1011 passed / 31 skipped** (960 + 51 new, no regression); 5 pre-existing Docker errors unchanged; `--cov-fail-under=90` holds at **99.84%**. ✅
- [x] **Step 9 — Code summary**: `guide-docs/build/outlier-model/code/code-summary.md` (module list + test→target map + realization notes); `testresults.txt` refreshed. ✅

## 5. HOLDS (binding through Part 2)
- **No import** of `quality_gates`, `memo_agent_core`, `ui_outlier_view`, or `observability` (SCOPE-1); `corpus_generator.records` imported **call-only**; `intake.schema`/`rules_engine.report_schema` types by shape.
- **The seed flows ONLY into `OutlierModel`** → IsolationForest (the injected instance); `CorpusSource`/`FeatureVectorBuilder`/`ShapExplainer` need no seed (CG-ND-OUT-Fold-3).
- **No LLM / no write / no persistence / no `Recommendation`-producing path / no verdict field** anywhere (BR-OUT-9, ADVISORY-1).
- **The by-construction guarantees are HARD requirements**, each with its header comment: `FeatureInputs` demographic-exclusion (P-OUT-1); the injected local `RandomState` + no-global-RNG (P-OUT-2); `ShapExplainer` the sole `FlaggedFeature` constructor (P-OUT-4); the imputed-mask → z=0-at-flagging (P-OUT-3 / CG-ND-OUT-Fold-1).
- **tier-B corpus run stays unauthorized and NOT required** — `CorpusSource` builds/tests fully on **in-memory fixtures**; no hard `corpus/` dependency.
- **The 17 frozen P1 units + the closed composition root UNTOUCHED**; no other unit started; the 23-unit decomposition unchanged.

## 6. Coverage / quality gate
- **Runner**: `pytest` over `backend/`, `--cov=backend/outlier_model` added to `pyproject` `addopts` (Q6) — the **comprehensive-depth bar** this project applied to `rules-engine`/`audit-store`/`auth-rbac` (the `--cov-fail-under=90` gate is **unchanged**).
- **Baseline (from the composition-root pass)**: backend **960 passed / 31 skipped** (+ 5 pre-existing Docker-absence errors). This is a **pure additive backend module** — **no P1 unit's tests touched**, no frozen file modified; the suite must not regress.
- **tier-U only**: the outlier tests run seeded + deterministic in CI (no Docker, no LLM, no `corpus/`); the 31 skips + 5 Docker errors are **unchanged** (U18 adds none).

## 7. Clarifying questions (`[Answer]` tags — LEFT BLANK; lettered; full text below)

> Fill these; I then run the ambiguity-check, then Part 2 (§4 Steps 0–9) **on your explicit go**. Per the standing convention the full Q&A is re-embedded once answered.

### Q1 — Test framework
- **A.** **`pytest` (established) + `Hypothesis` where a universal-quantifier property earns it** (e.g. swap-invariance over generated financial vectors; determinism over generated inputs) — parametrized tests elsewhere. **No new dependency** (both already in the stack). *(Recommended — matches every prior backend unit; Hypothesis strengthens BIAS-1/DET-1 without a new dep.)*
- **B.** **`pytest` only** (parametrized, no Hypothesis). Simpler; loses the generated-input strength on the two load-bearing targets.
- **C.** Other (describe).

`[Answer]:` A

### Q2 — Module/file organization within `backend/outlier_model/`
- **A.** **One file per component + a small `feature_fields.py` (constants + `FeatureInputs`) + a `schemas.py`** — i.e. `feature_fields.py`, `feature_vector.py`, `corpus_source.py`, `schemas.py`, `shap_explainer.py`, `model.py` (the §2 map). Cohesive, leaf-first-friendly, mirrors `rules-engine`'s multi-module layout. *(Recommended — one responsibility per file; the schemas live apart from the logic that builds them.)*
- **B.** **Fewer files** (e.g. fold `feature_fields.py` into `feature_vector.py`, `schemas.py` into `model.py`). Fewer imports, but couples the constant/schema to one consumer and weakens the leaf-first order.
- **C.** Other (describe).

`[Answer]:` A

### Q3 — Seeded tier-U fixture corpus construction (incl. missing-optional + swap-invariance fixtures)
- **A.** **A shared `tests/fixtures.py` (or `tests/factories.py`)** building a **small seeded synthetic `CorpusRecord[]`** (plain frozen objects shaped to `corpus_generator.records` **by shape**, no backend import beyond the schema), including: (i) **normal profiles** for the fit; (ii) **≥1 profile with a deliberately-missing optional** (`bmi_derived`/`existing_debt_obligations_annual`/`dti_ratio` = None) for the IMPUTE-1 teeth; (iii) a **swap-invariance pair** — two profiles with **identical financials, swapped `full_name`/`gender`/`city`** — for BIAS-1; (iv) an **outlier profile** (extreme financials) for COMPOSE-1. One factory reused across the teeth. *(Recommended — DRY, one fixtures module, the `audit_store`/`corpus_generator` test-factory precedent; keeps every teeth test on the same seeded corpus.)*
- **B.** **Inline fixtures per test file**. *(Rejected — duplication; the missing-optional/swap/outlier shapes recur across IMPUTE-1/BIAS-1/COMPOSE-1/DET-1.)*
- **C.** Other (describe).

`[Answer]:` A

### Q4 — The DET-1 global-RNG-perturbation sequence (proving seed-locality)
- **A.** **Between the two scoring runs, perturb numpy's global RNG explicitly** — `np.random.seed(<a>); np.random.random(<n>); np.random.seed(<b>)` — then assert the second `OutlierResult` is **byte-identical** to the first (CG-NFR-OUT-Fold-1; verified: `IsolationForest(random_state=<instance>)` is seed-local, so a global perturbation cannot change the output). The exact `(a, n, b)` are arbitrary fixed constants documented in the test. *(Recommended — directly proves the global RNG has no influence; the fixed constants keep it deterministic.)*
- **B.** **Cross-process determinism** (re-run scoring in a fresh subprocess, compare). Heavier; catches PYTHONHASHSEED/dict-order — but BR-OUT-4's stable-sort + Pydantic-deterministic serialization already cover that, and the global-RNG-perturbation (A) is the material check for the leak class.
- **C.** **Both** A (gating) + B (optional hardening). More coverage, more machinery.

`[Answer]:` A

### Q5 — The StructuralGuard AST-scan + detector-self-test mechanism
- **A.** **`ast.parse` per production `.py` file (excluding `tests/`)** + two robustness guards per scan, mirroring the frozen `auth_rbac/tests/test_no_forbidden_imports.py`: (i) a **detector self-test** proving the scan flags a **synthetic violation** (a synthetic forbidden import / `profile.demographics` read / `np.random.random(` call / second `FlaggedFeature(` site), so it can't be a no-op; (ii) a **non-vacuity guard** asserting the file set actually includes the at-risk modules. Applies to `no_demographic_read`, `no_global_rng`, `single_FlaggedFeature_constructor`, `reference_not_own`, `advisory_only`. *(Recommended — the established frozen precedent; AST is robust against comments/strings a text scan would misfire on.)*
- **B.** **Text/regex source scan** (no AST). Simpler but brittle (a comment or string mentioning the forbidden token misfires — the exact problem the composition-root pass hit and fixed with comment-stripping).
- **C.** Other (describe).

`[Answer]:` A

### Q6 — Coverage config + bar for `backend/outlier_model`
- **A.** **Add `--cov=backend/outlier_model` to `pyproject` `addopts`** at the **existing comprehensive bar** (the `--cov-fail-under=90` gate unchanged); omit nothing (the unit has no live-DB/subprocess module needing an `omit`, unlike `pg_repository.py`). *(Recommended — consistent with every prior backend unit; the pure-logic unit is fully unit-coverable.)*
- **B.** Add an `omit` for some module (e.g. if a thin `__init__` or a hard-to-cover path emerges). *(Deferred — flag at Code-Gen only if a genuinely unreachable line appears, reported honestly like `ui-override-form`'s belt-and-suspenders branch.)*
- **C.** Other (describe).

`[Answer]:` A

---

## 8. Gate
**Part 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** The six `[Answer]` tags (Q1–Q6) are **BLANK**. On the filled answers: run the mandatory **ambiguity-check** against the answers + the frozen FD (BR-OUT-1..10) + approved NFR Requirements (thirteen `NFR-OUT-*`) + approved NFR Design (P-OUT-1..9; CG-ND-OUT-Fold-1) — **surface-and-stop on any genuine gap, do not improvise** — then, **on the explicit go**, execute §4 Steps 0–9 leaf-first / tests-first, marking each `[x]`. **This is the LAST stage for `outlier-model`.** NO code generated in Part 1; NO file under `backend/outlier_model/` created. WIRE-1 · the 17 frozen P1 units · the closed composition root UNTOUCHED; backend 960/31 not regressed; tier-B NOT authorized (not required); the `audit_store` Docker-guard gap untouched; no other unit started; the 23-unit decomposition unchanged.
