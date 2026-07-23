# Tech-Stack Decisions — `outlier-model` (U18, C3, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U18 `outlier-model` · C3 · **Phase 2** · **Date**: 2026-07-16.
**Scope**: the technology decisions the `NFR-OUT-*` set rests on. **No NEW dependency** beyond the ML stack already floored in `requirements.txt` (verified on disk) and already installed (`sklearn 1.9.0`, `shap 0.52.0`, `numpy 2.4.6`). Built on the frozen FD + **Q1–Q3 all A** + folds **CG-NFR-OUT-Fold-1..3** — re-opening none.

---

## 1. Decisions

| # | Decision | Choice | Rationale | Traceability |
|---|---|---|---|---|
| **OUT-D1** | **Outlier estimator** | **`sklearn.ensemble.IsolationForest`**, `random_state = CorpusManifest.seed` (single-sourced) | FR-OUT-1 names it explicitly; a tree ensemble gives a holistic multivariate anomaly score (BR-OUT-5). The **int `random_state` constructs a seed-LOCAL `RandomState`** — verified byte-identical across a numpy global-RNG perturbation — so determinism is **RNG-leak-proof by construction** (NFR-OUT-DET-1 / CG-NFR-OUT-Fold-1). Already floored `scikit-learn>=1.5.0`. | FR-OUT-1, BR-OUT-4/5, NFR-OUT-DET-1 |
| **OUT-D2** | **Per-feature anomaly signal** | **z-scores** vs the fitted-corpus mean/std (numpy) | FR-OUT-1 names z-scores; they give the **per-feature `flagged_features`** (BR-OUT-5) and make "which feature is anomalous" explicit. `|z| >= Z_SCORE_FLAG_THRESHOLD` (strictly-positive) selects flags — so an imputed feature (`z == 0`) can never flag (NFR-OUT-THRESHOLD-1 / CG-NFR-OUT-Fold-2). | FR-OUT-1, BR-OUT-3/6, NFR-OUT-THRESHOLD-1 |
| **OUT-D3** | **Explainability** | **`shap`** (the tree-model fast path — `TreeExplainer` — for the tree-based IsolationForest); explainer selection finalized at Code-Gen | FR-OUT-2 / NFR-EXPLAIN-1 require a SHAP explanation per flag. The **tree fast path** keeps SHAP correctness **gating at tier-U on a small seeded fixture** without a hard perf SLO (NFR-OUT-PERF-1 / Q2-A). Already floored `shap>=0.46.0`. | FR-OUT-2, NFR-EXPLAIN-1, US-OUT-2, NFR-OUT-EXPLAIN-1/PERF-1 |
| **OUT-D4** | **Feature vector + missing values** | **numpy** float vector over the **`OUTLIER_FEATURE_FIELDS`** allow-list; missing optional → **deterministic corpus-median imputation** stored on the fitted model | Numeric-only, demographic-excluded **by construction** (BR-OUT-1). Corpus-median imputation is deterministic (a seeded-corpus statistic) and demographic-signal-free (NFR-OUT-IMPUTE-1 / BR-OUT-3). No `pandas` needed for v1 (plain numpy arrays); `pandas` stays available but unused unless Code-Gen finds a need. | BR-OUT-1/3, NFR-OUT-BIAS-1/IMPUTE-1 |
| **OUT-D5** | **Output schema** | **Pydantic v2** `OutlierResult` / `FlaggedFeature` / `OutlierProvenance`, `frozen=True`, `extra="forbid"` | Consistent with every frozen unit's schema discipline. `FlaggedFeature` makes `shap_value` a **required** field, so **zero-unexplained-flag holds by construction** (NFR-OUT-EXPLAIN-1); provenance completeness holds by schema (NFR-OUT-PROV-1). | BR-OUT-7, CG-OUT-Fold-2, NFR-OUT-EXPLAIN-1/PROV-1 |
| **OUT-D6** | **Provenance / version anchoring** | record **`outlier_model_version`** (bundles the sklearn version + the feature-vector schema version) alongside `corpus_version` + `seed` on every result | Reproducibility across a dependency upgrade (Q2-A / CG-OUT-Fold-2): a replay knows the exact library it must match — the same version-anchored discipline as the frozen `engine_version`/`model_version`. The exact string format is a Code-Gen realization. | CON-DET-1 skill #7, NFR-OUT-PROV-1 |
| **OUT-D7** | **Corpus source** | own-local **`CorpusSource`** dual-source seam (`from_records` / `from_file`), **mirroring — never importing —** `quality_gates/corpus_loader.py`; imports `corpus_generator.records` **call-only** | U18's one `R` edge is to `corpus-generator`; it has **no edge to `quality_gates`** (importing `CorpusLoader` is Q4-C, rejected). tier-B (`from_file`) is **not triggered / not required** for build+test (NFR-OUT-CORPUS-1). | BR-OUT-8/10, NFR-OUT-CORPUS-1/SCOPE-1 |
| **OUT-D8** | **Test substrate** | **Vitest-analog for Python = pytest** at **tier-U** on a **small seeded fixture corpus** (synthetic `CorpusRecord[]`), no Docker / no LLM / no `corpus/` | The determinism, swap-invariance, imputation, and SHAP-correctness teeth all run fast + seeded in CI (BR-OUT-8 tier-B-independence). Detector self-tests make every structural scan non-vacuous (CG-NFR-OUT-Fold-3). | NFR-OUT-CORPUS-1, all component/structural targets |
| **OUT-D9** | **Runtime** | **Python 3.12 (pinned minor)** | Build-wide determinism pin (`.python-version` = 3.12, `pyproject requires-python ">=3.12,<3.13"`) — reused, not re-declared. | CON-DET-1, intake D6 carry-forward |

---

## 2. `outlier_model_version` — the version-anchoring discipline (OUT-D6 in detail)

scikit-learn does **not** guarantee cross-version numeric identity (a legitimate upgrade can change tree splits / SHAP values under the same seed). A bare seed is therefore reproducible **only within a version**. Recording `outlier_model_version` (sklearn version + feature-schema version) makes reproducibility **version-anchored**: a stored `OutlierResult` declares the exact library state it was produced under, so a replay can detect a mismatch rather than silently diverge — the same discipline the frozen audit tuple applies with `engine_version`/`model_version`. The NFR tests **never** assert absolute numeric values (Q1-A), so they do **not** break on such an upgrade; they assert run-to-run identity, which the seed guarantees within any single version. The exact string format + the sklearn floor/lock are Code-Gen realizations.

## 3. Explicitly NOT chosen here (owned by other units / deferred — reference-not-own)
- **`quality_gates.CorpusLoader`** — **not imported** (U18 has no edge to `quality_gates`); its dual-source pattern is **mirrored** in `CorpusSource` (OUT-D7).
- **The tier-B corpus build** — an out-of-band, separately-authorized step; **not triggered, not required** for U18 build/test (NFR-OUT-CORPUS-1).
- **Orchestrator wiring + `memo-agent-core` / `ui-outlier-view` consumption** — those units' own FDs (Q3-A); U18 pins only the `OutlierResult` contract.
- **`secrets-config` seam shape** — thin config seam, confirmed at NFR-Design; no key is used by scoring.
- **The exact `Z_SCORE_FLAG_THRESHOLD` value + IsolationForest hyper-parameters** — post-calibration Code-Gen realizations (CG-OUT-Fold-1); the FD/NFR pin the name, the 3.0 default, and the strictly-positive invariant.

## 4. No new dependencies
Every library is **already floored in `requirements.txt`** (verified): `scikit-learn>=1.5.0`, `shap>=0.46.0`, `numpy>=1.26.0`, `pandas>=2.2.0` — and installed (`sklearn 1.9.0`, `shap 0.52.0`, `numpy 2.4.6`). **`outlier-model` adds no dependency.** Pydantic v2 (schemas) + pytest (tests) are build-wide. The exact sklearn floor/lock supporting `outlier_model_version` is finalized at Code-Gen.
