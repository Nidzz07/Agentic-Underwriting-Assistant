# Domain Entities — `outlier-model` (U18, C3, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U18 `outlier-model` · C3 · **Phase 2** · **Depth**: comprehensive · **Date**: 2026-07-16 · Stories **US-OUT-1/2/3** · FR-OUT-1/2/3, CON-BR1, CON-DET-1, NFR-EXPLAIN-1, DATA-4.
**Scope**: the entity/schema view of `outlier-model` — the **demographic-excluded feature vector**, the **`OutlierResult`** output contract, the consumed frozen shapes (by shape), and the **component/module + method inventory** (folded here per the comprehensive-unit convention — every P1 comprehensive unit used the 3-artifact FD set with methods folded into `domain-entities.md`, and this unit matches it). **Advisory input to the memo; no LLM, no write path, no persistence** (underwriting-rules skill #1/#3). Consumes frozen shapes **by value/by shape**, re-declares none (reference-not-own). **NO code in this stage.**

Built on the answers **Q1–Q5 (all A)** + the ambiguity-check folds **CG-OUT-Fold-1..4** (plan §3.5), re-opening none.

---

## 1. Component / module inventory (folded component-methods)

Four owned components under `backend/outlier_model/` (module names per `unit-of-work.md` U18 + the plan). All pure Python; the only third-party imports are `scikit-learn` / `numpy` / `shap` (the ML stack) — **no backend unit is edited, no consumer is imported**.

| Component | Module (planned) | Role | Method surface (signatures pinned; bodies → Code-Gen) |
|---|---|---|---|
| **`FeatureVectorBuilder`** | `feature_vector.py` | Projects an `ApplicantProfile` onto the **numeric, demographic-excluded** feature vector, reading **only** `OUTLIER_FEATURE_FIELDS` (§2). Owns the missing-optional imputation policy (§2.3). | `field_order() -> tuple[str, ...]` (the stable, sorted field order — determinism); `build(profile, imputer) -> list[float]` (one applicant → one vector); `build_matrix(profiles, imputer) -> list[list[float]]` (the corpus → the fit matrix) |
| **`CorpusSource`** | `corpus_source.py` | The **own-local dual-source seam** (Q4-A), **mirroring — never importing —** `quality_gates/corpus_loader.py`. Imports `corpus_generator.records` **call-only**. | `from_records(records) -> list[CorpusRecord]` (tier-U/S in-memory); `from_file(path) -> list[CorpusRecord]` (tier-B frozen `corpus/`); `profiles(records) -> list[ApplicantProfile]`; `corpus_version(manifest) -> str` |
| **`OutlierModel`** | `model.py` | Fits **IsolationForest** on the corpus feature matrix (seeded) + computes the per-feature **corpus z-score statistics**; scores an applicant → the holistic `outlier_score` + the per-feature `flagged_features` (Q5-A). Holds the fitted state + the imputer + the provenance. | `fit(corpus_profiles, manifest) -> FittedOutlierModel`; `FittedOutlierModel.score(profile) -> OutlierResult` |
| **`ShapExplainer`** | `shap_explainer.py` | Attributes the IsolationForest score to features via SHAP; supplies each flagged feature's `shap_value` + `direction`, guaranteeing **zero unexplained flags** (US-OUT-2). | `explain(fitted_model, vector) -> dict[str, ShapContribution]` (feature → contribution) |

> **Header-comment deliverables (by-construction guarantees, EXPLICIT at Code-Gen)** — mirroring the frozen self-evidence convention: **`feature_vector.py`** states it reads **only** `OUTLIER_FEATURE_FIELDS` and that `demographics` is structurally unreachable (CON-BR1 by construction); **`corpus_source.py`** states it is a read-only dual-source seam that imports `corpus_generator.records` call-only and **never triggers a corpus build / never calls an LLM**; **`model.py`** states the seed is single-sourced from `CorpusManifest.seed` and the model is deterministic given `(corpus_version, seed, outlier_model_version)`.

---

## 2. The feature vector — `OUTLIER_FEATURE_FIELDS` (Q1-A: numeric-only, demographic-excluded, by construction)

### 2.1 The allow-list (single-sourced, U18-local, **not imported**)
Mirrors the frozen `rules_engine.rulebook_schema.ALLOWED_INPUT_FIELDS` precedent (plan §1.4) — a U18-local `frozenset` the `FeatureVectorBuilder` reads **exclusively** from. **v1 is numeric-only; categoricals are excluded (§2.2).**

| # | Feature field | Source (`ApplicantProfile`) | Always present? |
|---|---|---|---|
| 1 | `age_years_derived` | `age_years_derived` (D) | ✅ always (int) |
| 2 | `bmi_derived` | `bmi_derived` (D, Optional) | ⚠️ nullable → §2.3 |
| 3 | `verifiable_income_annual` | `verifiable_income_annual` (R) | ✅ always |
| 4 | `existing_debt_obligations_annual` | `existing_debt_obligations_annual` (O, Optional) | ⚠️ nullable → §2.3 |
| 5 | `requested_cover_amount` | `requested_cover_amount` (R) | ✅ always |
| 6 | `dti_ratio` | derived (debt / income) | ⚠️ nullable (None if debt missing) → §2.3 |
| 7 | `income_multiple` | derived (cover / income) | ✅ always (income R, cover R) |
| 8 | `health_flag_count` | `len(health_flags)` | ✅ always (≥0) |
| 9 | `documents_missing_count` | derived from `documents` manifest | ✅ always (≥0) |

**`OUTLIER_FEATURE_FIELDS`** = the frozenset of the nine names above. The derived operands (`dti_ratio`, `income_multiple`, `health_flag_count`, `documents_missing_count`) reuse the **same derivation semantics** the frozen rules-engine namespace already established (plan §1.4) — computed here from the profile, **never** re-deriving a different rule.

### 2.2 Why each categorical is EXCLUDED from v1 (CG-OUT-Fold-3 — documented, not merely asserted)
| Excluded field | Why out of v1 |
|---|---|
| `occupation` | A **CON-BR1 proxy-checked variable** (`requirements.md:144`): legitimate **only** through its sanctioned occupation-risk rule, never a back-door correlation. Inside an **unsupervised** anomaly detector it cannot be constrained to "one sanctioned rule," so admitting it risks a proxy entering an unconstrained model. Excluded to keep the proxy discipline intact. |
| `smoking_status` | A small-cardinality **categorical** whose numeric encoding (one-hot/ordinal) is an **arbitrary modelling choice with its own determinism surface** (Q1-B hazard). Its underwriting signal is **already handled deterministically** by the smoking rule; low marginal anomaly signal for the encoding risk it adds in v1. |
| `employment_type` | Same reasoning as `smoking_status`: small-cardinality categorical, arbitrary-encoding hazard, signal already captured by the employment-type rule. |
| all **`demographics`** (`full_name`, `gender`, `city`) | **CON-BR1 hard exclusion** — never a feature (FR-OUT-3). Structurally unnameable (§2.4). |

Any categorical can be added **later** behind the same allow-list + a **proxy-swap test** — v1 keeps the vector numeric-only and encoding-free.

### 2.3 Missing-optional handling (CG-OUT-Fold-4 — deterministic corpus-derived imputation)
Three fields (`bmi_derived`, `existing_debt_obligations_annual`, `dti_ratio`) are **nullable** — `corpus_generator/profile_factory.py` emits thin-file / edge profiles with `height/weight=None` (→ `bmi_derived=None`) or `debt=None` (→ debt/`dti_ratio=None`). IsolationForest + z-scores need **complete numeric vectors**. Policy:
- A missing optional is filled with a **fixed statistic of the fitted corpus** — the **corpus median** for that feature, computed **once at fit** under the seed and stored on the fitted model (the `imputer`).
- **Deterministic** (CON-DET-1): a fixed function of the seeded corpus — no wall-clock, no RNG, no dict-ordering.
- **CON-BR1-safe**: the imputed value is a corpus statistic carrying **no demographic signal**.
- **Not fabrication**: it is an explicit, disclosed model-level default (contrast rules-engine barring a *fabricated per-applicant DTI*). By construction the **z-score of an imputed feature is 0**, so **an imputed field never itself raises a flag** — a missing value can never manufacture an anomaly.

### 2.4 CON-BR1 by construction (US-OUT-3 / FR-OUT-3)
`FeatureVectorBuilder.build` reads **only** the fields named in `OUTLIER_FEATURE_FIELDS` and asserts, by construction, that the produced vector's field set **equals** the allow-list (the frozen `assert set(namespace) == set(ALLOWED_INPUT_FIELDS)` mechanism, mirrored). The `demographics` sub-object is **never referenced**, so a demographic name **has no resolvable target** — a demographic field is *structurally unnameable* in the vector. **Swap-invariance** (name/gender/city swap over identical financials → identical vector → identical `OutlierResult`) is therefore **true by construction**, with a U18-owned swap test + the external `quality-gates` bias-swap suite as regression guards on top.

---

## 3. `OutlierResult` — the output contract (Q3-A: pinned NOW; CG-OUT-Fold-2: `corpus_version` included)

The **stable, self-contained** shape U18 owns. Downstream **wiring** (which orchestrator node calls it; how `memo-agent-core` / `ui-outlier-view` consume it) is **deferred to those units' own FDs** — U18 has no edge to them.

```text
OutlierResult (frozen, extra="forbid")
├── outlier_score: float                     # IsolationForest holistic score (Q5-A); higher = more anomalous
├── is_outlier: bool                          # score crosses the model's decision boundary (IsolationForest predict)
├── flagged_features: list[FlaggedFeature]    # per-feature anomalies; MAY be empty (a normal applicant)
└── provenance: OutlierProvenance             # the reproducibility triple (CG-OUT-Fold-2)

FlaggedFeature (frozen)                        # ZERO-UNEXPLAINED by construction — cannot exist without its SHAP field
├── feature: str                              # one of OUTLIER_FEATURE_FIELDS (never a demographic name)
├── z_score: float                            # per-feature z vs the corpus distribution; |z| >= threshold ⇒ flagged
├── shap_value: float                         # SHAP attribution of the IsolationForest score to this feature (US-OUT-2)
└── direction: FlagDirection                  # HIGH | LOW — which tail (above/below the corpus mean)

OutlierProvenance (frozen)                     # the score is meaningless + un-replayable without all three
├── corpus_version: str                       # WHICH corpus fit the forest (CG-OUT-Fold-2 — score is corpus-relative)
├── seed: int                                 # single-sourced from CorpusManifest.seed (Q2-A)
└── outlier_model_version: str                # bundles sklearn version + the feature-vector schema version (Q2-A)
```

- **Zero-unexplained-flag is a SCHEMA property** (Q3-A): a `FlaggedFeature` **cannot be constructed without** its `shap_value`, so NFR-EXPLAIN-1 holds by construction, not by a downstream test.
- **`provenance` does NOT carry `rulebook_version`** (CG-OUT-Fold-2): unsupervised scoring fits on the feature vectors and **never reads the corpus `label`**, so the labelling rulebook is irrelevant to the score — a clean confirmation the score is label-independent.
- **`FlagDirection`** = a closed enum `{ HIGH, LOW }` — a flagged feature is either above (`HIGH`) or below (`LOW`) the corpus mean; the enum makes the direction explicit for the memo/UI rather than inferring it from the sign.

---

## 4. Consumed frozen shapes (by shape — re-declared by none)

| Shape | Origin (frozen) | How U18 uses it |
|---|---|---|
| `ApplicantProfile` | `intake.schema` | the scored unit; feature source (§2); `demographics` is the exclusion target |
| `CorpusRecord` = `{profile, documents_text, label, intended_class, edge_case_tags}` | `corpus_generator.records` | the corpus stream; U18 reads **only `profile`** (the `label` is unused — §3) |
| `CorpusManifest` = `{seed, corpus_version, rulebook_version, engine_version, content_hash, profile_count, …}` | `corpus_generator.records` | `seed` → the `random_state`; `corpus_version` → the corpus-selection key + provenance |
| `Recommendation` = `{APPROVE, REFER, DECLINE-RECOMMEND}` | `rules_engine.report_schema` | the corpus label space (present on `CorpusRecord`, **not consumed** by scoring) |

**Reference-not-own**: `corpus_generator.records` is imported **call-only** (via `CorpusSource`, mirroring `corpus_loader.py`). **No** import of `quality_gates` (U18 has no edge to it — Q4-C rejected), **no** import of any consumer (`memo-agent-core`/`ui-outlier-view`/`observability`), **no** edit to any frozen unit.

---

## 5. Schema-vs-data boundary (greenfield)

- **Schema (this FD pins)**: `OUTLIER_FEATURE_FIELDS`, the `FeatureVectorBuilder`/`CorpusSource`/`OutlierModel`/`ShapExplainer` surfaces, `OutlierResult`/`FlaggedFeature`/`OutlierProvenance`, the missing-value rule, the `Z_SCORE_FLAG_THRESHOLD` **name + 3.0 default**.
- **Data / tuning (NFR / Code-Gen)**: the exact `Z_SCORE_FLAG_THRESHOLD` value (confirmable after corpus calibration — CG-OUT-Fold-1), IsolationForest hyper-parameters (`n_estimators`, `contamination`), the exact `outlier_model_version` string / sklearn lock, the `secrets-config` seam shape.
- **Out of scope (deferred, named-not-designed)**: the orchestrator wiring; `memo-agent-core` / `ui-outlier-view` consumption; the tier-B corpus build itself (Q4-A — not triggered, not required here).

## 6. Cross-consumer field-need check (contract stability)

`OutlierResult` is the shape three not-yet-built P2 consumers will read: **`memo-agent-core`** (the memo cites the flags + explanations — needs `flagged_features[].{feature, shap_value, direction}` + `outlier_score`), **`ui-outlier-view`** (displays flags + SHAP — same fields + `is_outlier`), **`observability`** (traces the scoring step — needs `provenance`). All three needs are met by the §3 shape **without** any consumer-specific field, so pinning it now (Q3-A) stabilizes the contract before the consumers exist — the cluster-FD-first discipline the P1 units used for `RuleResultReport`.
