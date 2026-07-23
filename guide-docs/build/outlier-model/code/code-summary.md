# Code Summary — `outlier-model` (C3 / U18, **Phase 2**)

**Phase / Stage**: BUILD → per-unit loop → **Code Generation (Part 2 complete)** · the **FIRST Phase-2 unit** (U18–U23)
**Date**: 2026-07-17 · **Runtime**: Python **3.12** (matches the pin) · **Depth**: comprehensive
**Result**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓** — `outlier-model` is the **first fully-complete Phase-2 unit**. A **deterministic statistical scorer**: advisory-only, no LLM, no write path, no persistence, demographic-excluded by construction, seeded + version-anchored.

**No LLM / no DB / no write transport anywhere in the unit** — pure `scikit-learn` / `numpy` / `shap`. Every test runs seeded + deterministic at **tier-U** on in-memory fixtures (no Docker, no `corpus/`). The **tier-B real-corpus run stays UNAUTHORIZED / NOT required** — the unit builds + tests fully on `tests/fixtures.py`.

---

## 1. Modules (`backend/outlier_model/`) — 7 source modules (+ `__init__`), all 100% covered

| Module | Component | Realizes (by-construction + targets) |
|---|---|---|
| `feature_fields.py` | constants + projection type | `OUTLIER_FEATURE_FIELDS` (9 numeric) + `FeatureInputs` (`values`+`imputed` only — **no demographics field**) | P-OUT-1 / BIAS-1, FEAT-1 |
| `corpus_source.py` | C-OUT-2 `CorpusSource` | dual-source seam (`from_records`/`from_file`/`profiles`/`corpus_version`); **mirrors — never imports —** `corpus_loader.py`; `corpus_generator.records` call-only | P-OUT-6 / CORPUS-1 |
| `feature_vector.py` | C-OUT-1 `FeatureVectorBuilder` + `CorpusImputer` | `field_order`/`fit_imputer`/`project`/`build_matrix`; allow-list accessor map + module-load `assert set(_ACCESSORS)==OUTLIER_FEATURE_FIELDS`; median impute **+ `imputed` mask**; mirror-derived `dti_ratio`/`income_multiple` | P-OUT-1/3 / BIAS-1, IMPUTE-1 |
| `schemas.py` | schemas | `OutlierResult`/`FlaggedFeature`/`OutlierProvenance`/`FlagDirection` (frozen, `extra="forbid"`; `shap_value` **required**, no default; no verdict field; no `rulebook_version`) | P-OUT-4/7 / EXPLAIN-1, PROV-1, ADVISORY-1 |
| `shap_explainer.py` | C-OUT-4 `ShapExplainer` + `FlagCandidate` | `explain(...)` — the **SOLE `FlaggedFeature` constructor**; empty-candidate short-circuit; `shap.TreeExplainer` (tree fast path) | P-OUT-4 / EXPLAIN-1 |
| `model.py` | C-OUT-3 `OutlierModel` / `FittedOutlierModel` | `fit` injects `RandomState(manifest.seed)` into IsolationForest (global `np.random.*` never touched); `score` composes IF score + non-imputed z-flags + SHAP + provenance; `Z_SCORE_FLAG_THRESHOLD=3.0` + `>0` guard; `_z_scores`/`_is_flag`/`_candidates` pure helpers | P-OUT-2/3/5/7 / DET-1, THRESHOLD-1, COMPOSE-1, PROV-1 |
| `tests/structural.py` + `tests/fixtures.py` | C-OUT-5 `StructuralGuard` substrate + seeded corpus factory | AST scan helpers; one seeded synthetic `CorpusRecord[]` (normal / missing-optional / swap-pair / outlier), reused across all teeth | P-OUT-8 (test harness) |

**Imports read-only, unchanged**: `intake.schema.ApplicantProfile` (by shape); `corpus_generator.records.{CorpusRecord,CorpusManifest}` (call-only, via `CorpusSource`). **No `quality_gates` / `memo_agent_core` / `ui_outlier_view` / `observability` import; no consumer import; no frozen-unit edit.** `rules_engine` derivation semantics are **mirrored locally, not imported** (SCOPE-1).

---

## 2. Test → target map (all thirteen `NFR-OUT-*`, each at its NFR-pinned tier)

| Target | Named test(s) |
|---|---|
| **BIAS-1** *(load-bearing)* | `test_no_demographic_read::test_no_production_module_reads_a_demographic_attribute` (AST + self-test), `::test_field_order_equals_the_allowlist`; `test_swap_invariance::test_swap_yields_byte_identical_feature_inputs`, `::test_swap_yields_byte_identical_outlier_result` |
| **DET-1** *(load-bearing)* | `test_determinism::test_same_corpus_seed_inputs_byte_identical_across_two_fits`, `::test_global_rng_perturbation_does_not_change_the_result`; `test_no_global_rng::test_no_global_rng_or_wallclock_in_production` (+ self-test + **negative** self-test allowing `from numpy.random import RandomState`) |
| **FEAT-1** | `test_feature_fields::test_allowlist_is_the_nine_numeric_names`, `::test_categoricals_and_demographics_absent`, `::test_domain_entities_documents_each_categorical_exclusion` |
| **IMPUTE-1** | `test_imputation::test_missing_optionals_are_masked_as_imputed`, `::test_imputed_feature_never_flags`, `::test_imputed_feature_z_score_is_exactly_zero`, `::test_fit_imputer_takes_median_over_present_values_only`, `::test_imputation_is_deterministic` |
| **THRESHOLD-1** | `test_threshold::test_threshold_is_strictly_positive`, `::test_exactly_one_threshold_literal_at_module_level`, `::test_flag_predicate_is_inclusive_at_the_boundary`, `::test_candidate_selection_is_parameterized_off_the_constant` |
| **EXPLAIN-1** | `test_flagged_feature_schema::test_flagged_feature_requires_shap_value`, `::test_flagged_feature_forbids_extra_fields`, `::test_every_flag_in_a_scored_result_carries_a_finite_shap_value`; `test_single_constructor::test_flagged_feature_constructed_in_exactly_one_place` (+ self-test) |
| **COMPOSE-1** | `test_score_compose::test_outlier_score_comes_from_isolation_forest`, `::test_flagged_features_are_exactly_the_nonimputed_over_threshold`, `::test_normal_applicant_has_no_flags_but_a_valid_score`, `::test_empty_candidate_shortcircuit_returns_no_flags` |
| **CORPUS-1** | `test_corpus_source::test_from_records_and_from_file_yield_the_same_profile_shape`, `::test_default_path_needs_no_corpus_file`, `::test_corpus_version_reads_the_manifest` |
| **PROV-1** | `test_provenance::test_every_result_carries_the_full_provenance_triple`, `::test_provenance_has_no_rulebook_version` |
| **SCOPE-1** | `test_reference_not_own::test_no_consumer_or_quality_gates_import`, `::test_non_vacuity_the_existing_consumers_are_real`, `::test_detector_flags_synthetic_violations` (incl. forward-looking `ui_outlier_view`/`observability`) |
| **ADVISORY-1** | `test_advisory_only::test_no_llm_db_or_verdict_import_in_production`, `::test_outlier_result_has_no_verdict_field`, `::test_detector_flags_synthetic_llm_and_db_imports` |
| **PERF-1** *(observed / soft)* | `test_perf_observed::test_fit_and_score_runtime_observed` (records fit+score+SHAP ≈ 0.37s; correctness gating, runtime non-gating) |
| **SEC-1** | governance — the Security-Guardrails table (no runtime test) |

**Every `NFR-OUT-*` mapped; no orphan.** No test imports a consumer, a `quality_gates` module, or exercises the real tier-B corpus.

---

## 3. Flagged realization notes (Code-Gen-deferred items, honestly recorded)

1. **Mirror-not-import derivations** — `dti_ratio` = debt/income, `income_multiple` = cover/income (guard-before-divide → `None`), `documents_missing_count` = `max(expected−satisfied, 0)`, `health_flag_count` = `len(health_flags)`: computed locally in `feature_vector.py`, **mirroring** the frozen `rules_engine` semantics, NOT imported (SCOPE-1's "only `corpus_generator.records` + `intake.schema`"). `Decimal → float` at the numeric feature boundary (`FeatureInputs.values: tuple[float,…]`).
2. **Near-zero-variance z-guard** (`_has_variance`, `_STD_EPSILON = 1e-9` relative) — a feature whose std is float-noise on an analytically-constant column would explode `z`; it is treated as zero-variance → `z=0` (mirrors sklearn `StandardScaler` near-constant handling). Exact-`std==0` integer-constant columns (`health_flag_count`, `documents_missing_count`) also handled. Composes with the imputed-mask so BR-OUT-3's "imputed never flags" is skew- **and** noise-robust.
3. **IsolationForest hyper-parameters** — `n_estimators=100`, `contamination="auto"` (FD §5 / NFR-Req §4 deferred). Deterministic given the injected seed.
4. **`outlier_model_version`** — `f"outlier-model/1.0.0+sklearn-{sklearn.__version__}+fv1"` (bundles the sklearn version + feature-schema version). PROV-1 asserts presence + shape, not the literal.
5. **SHAP explainer** — `shap.TreeExplainer(fitted_forest)` with `check_additivity=False` (empirically verified on `IsolationForest`, shap 0.52.0 / sklearn 1.9.0 / numpy 2.4.6). The tree fast path keeps PERF-1 soft.
6. **`imputed → z=0` observability** — proven by unit-testing the pure `_z_scores` helper directly; the public API stays `score() -> OutlierResult`.

---

## 4. Coverage / quality gate

- **`backend/outlier_model` — 100%** (7 production modules; branch coverage). Added `--cov=backend/outlier_model` to `pyproject` `addopts`; the `--cov-fail-under=90` gate is **unchanged**, held at **99.84%** total.
- **Backend suite: 1011 passed / 31 skipped** — **960 baseline + 51 new**, no regression; the 31 skips + the **5 pre-existing Docker-absence errors** (`audit_store` pg_integration) are **unchanged** (U18 adds none).
- **No P1-unit file touched; the closed composition root (`backend/app/`, `frontend/src/app/`) untouched; WIRE-1 untouched; tier-B NOT authorized (not required).**
