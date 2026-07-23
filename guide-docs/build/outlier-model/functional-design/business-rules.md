# Business Rules — `outlier-model` (U18, C3, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U18 `outlier-model` · C3 · **Phase 2** · **Date**: 2026-07-16 · Stories **US-OUT-1/2/3**.
**Nature**: `outlier-model` owns **no rulebook rules** and **no authorization/commit/LLM path** — it is a **deterministic statistical scorer** that produces **advisory** anomaly flags as **input to the memo**, never a recommendation or decision (underwriting-rules skill #1/#3). The rules below (**BR-OUT-\***) are **checkable** invariants governing feature construction, seeded determinism, faithful explanation, and the corpus-source boundary — each grounded in a frozen contract or a settled answer, none introducing domain rule logic. The **load-bearing** ones are **BR-OUT-1** (CON-BR1 demographic exclusion, by construction) and **BR-OUT-4** (seeded reproducibility, version-anchored).

Built on **Q1–Q5 (all A)** + **CG-OUT-Fold-1..4** (plan §3.5), re-opening none.

---

## Rules

### BR-OUT-1 — Demographic exclusion is BY CONSTRUCTION: the vector reads only `OUTLIER_FEATURE_FIELDS` (CON-BR1 / FR-OUT-3 / US-OUT-3) — **load-bearing**
The feature vector is built from a **single-sourced, U18-local `OUTLIER_FEATURE_FIELDS`** allow-list of numeric facts only; the `FeatureVectorBuilder` reads **exclusively** from it and asserts, by construction, that the produced vector's field set **equals** the allow-list. The `demographics` sub-object (`full_name`, `gender`, `city`) is **never referenced**, so a demographic name has **no resolvable target** — it is *structurally unnameable* in the vector. Mirrors the frozen `rules_engine` `ALLOWED_INPUT_FIELDS` + `assert set(...) == ...` mechanism (plan §1.4), **not imported**.
- **Grounded**: FR-OUT-3 ("demographic identifiers MUST NOT enter the feature vector"); US-OUT-3 gherkin (swap-invariance); the rules-engine by-construction precedent; skill #6; Q1-A.
- **Checkable**: no module under `backend/outlier_model/` references `.demographics` / `full_name` / `gender` / `city` in a feature path (structural scan + self-test); `set(builder.field_order()) == OUTLIER_FEATURE_FIELDS`; a **name/gender/city swap over identical financials yields a byte-identical vector and `OutlierResult`** (a U18-owned swap test, mirroring US-OUT-3, on top of the external `quality-gates` bias-swap suite).

### BR-OUT-2 — v1 is numeric-only; each categorical exclusion is documented, not silent (CG-OUT-Fold-3)
`OUTLIER_FEATURE_FIELDS` contains **only numeric** facts (the nine of `domain-entities.md §2.1`). `employment_type`, `smoking_status`, and `occupation` are **excluded from v1**, each for a **documented reason** (`occupation` = a CON-BR1 proxy-checked variable unfit for an unconstrained anomaly detector; `smoking_status`/`employment_type` = arbitrary-encoding determinism hazard for low marginal signal, already handled by their own rules). Categoricals may be added later **behind the same allow-list + a proxy-swap test**.
- **Grounded**: `requirements.md:144` (CON-BR1 proxy nuance); Q1-A; Q1-B's noted encoding hazard; CG-OUT-Fold-3.
- **Checkable**: every field in `OUTLIER_FEATURE_FIELDS` maps to a numeric profile value; the three categoricals are absent; `domain-entities.md §2.2` documents each exclusion.

### BR-OUT-3 — Missing optional → deterministic corpus-derived imputation; an imputed field never raises a flag (CG-OUT-Fold-4)
A missing optional feature (`bmi_derived`, `existing_debt_obligations_annual`, `dti_ratio` may be `None` for thin-file / edge profiles) is filled with a **fixed statistic of the fitted corpus** (the corpus median for that feature, computed **once at fit** under the seed and stored on the fitted model). It is **not** a fabricated per-applicant value; by construction the **z-score of an imputed feature is 0**, so a missing value **can never manufacture an anomaly flag**.
- **Grounded**: `corpus_generator/profile_factory.py` (nullable `bmi`/`debt` in edge profiles); the rules-engine "never fabricate a missing operand" precedent; CON-DET-1; CON-BR1 (a corpus statistic carries no demographic signal); CG-OUT-Fold-4.
- **Checkable**: imputation is a pure function of the seeded corpus (same corpus + seed → same imputer); an applicant missing an optional scores deterministically; a flag is **never** raised on an imputed feature (its `z_score == 0`); a self-test confirms two runs with the same `(corpus_version, seed)` produce identical imputed values.

### BR-OUT-4 — Seeded, version-anchored reproducibility: identical input → identical output, across a dependency upgrade (CON-DET-1 / FR-OUT-1 / US-OUT-1) — **load-bearing**
IsolationForest is constructed with `random_state = CorpusManifest.seed` (**single-sourced**, never a second seed). The `OutlierResult` carries the **provenance triple `{corpus_version, seed, outlier_model_version}`**, where `outlier_model_version` bundles the sklearn version + the feature-vector schema version — so reproducibility is anchored **both** within a version (seed-fixed) **and** across time (version-recorded), consistent with constraint #7's version-anchored replay. **No unseeded randomness, wall-clock-dependent logic, or dict-ordering assumption** anywhere in scoring; the feature field order is a **stable sort**.
- **Grounded**: FR-OUT-1 (seeded); CON-DET-1; skill #5/#7; scikit-learn's no-cross-version guarantee (plan §3.5 / Q2 context); Q2-A; CG-OUT-Fold-2.
- **Checkable**: scoring the same applicant against the same `(corpus_version, seed)` **twice yields an identical `OutlierResult`** (US-OUT-1 gherkin); the seed is read only from `CorpusManifest.seed`; a scan finds no `random`/`time`/`datetime.now`/unordered-`set`-iteration in a scoring path; `provenance` is populated on every result.

### BR-OUT-5 — Score/flag/explain composition: IsolationForest score + z-score flags + SHAP per flag (FR-OUT-1/2 / Q5-A)
The `OutlierResult` composes the two named techniques deterministically: **IsolationForest** (fit on the corpus feature matrix, scored against the applicant) → the holistic `outlier_score` + `is_outlier`; **per-feature z-scores** (vs the corpus distribution) → `flagged_features` (a feature is flagged **iff** `|z| >= Z_SCORE_FLAG_THRESHOLD`); **SHAP** → each flag's `shap_value` + `direction`. One score, explicit per-feature flags, every flag explained — the 1:1 map to PROJECT-BRIEF §C3 ("score, flagged features, explanation").
- **Grounded**: FR-OUT-1 ("z-scores + IsolationForest"); FR-OUT-2 ("score, flagged features, SHAP"); PROJECT-BRIEF §C3; Q5-A.
- **Checkable**: `outlier_score` comes from IsolationForest; `flagged_features` are exactly the features with `|z| >= threshold`; each carries a `shap_value`; a normal applicant yields `flagged_features == []` with a valid score.

### BR-OUT-6 — `Z_SCORE_FLAG_THRESHOLD` is a single fixed named constant; default |z| ≥ 3.0 (CG-OUT-Fold-1)
The flag threshold is **one deterministic named constant** — default **|z| ≥ 3.0** (3-sigma) — **never** computed per-run, never data/wall-clock-dependent. The FD pins the **name + default + fixed-constant discipline**; the exact value is **confirmable at NFR/Code-Gen** after calibration against the real corpus distribution (a statistical tuning parameter, **not** a regulatory boundary — contrast the frozen IRDAI thresholds pinned exactly by rules-engine).
- **Grounded**: FR-OUT-1; the rules-engine "deterministic constants, confirmed not arbitrary" precedent; CG-OUT-Fold-1.
- **Checkable**: exactly one threshold constant exists; it is a module-level literal (not a computed/random value); changing it changes which features flag (a self-test at the default).

### BR-OUT-7 — Zero unexplained flags, by schema construction (NFR-EXPLAIN-1 / US-OUT-2)
Every `FlaggedFeature` **cannot be constructed without** its `shap_value` (a required field), so **no flag can exist without its SHAP explanation** — the NFR-EXPLAIN-1 "zero unexplained flags" invariant holds **by construction**, not by a downstream check.
- **Grounded**: NFR-EXPLAIN-1; US-OUT-2 gherkin ("zero flags without an explanation"); skill #8; Q3-A.
- **Checkable**: the `FlaggedFeature` schema makes `shap_value` mandatory (`extra="forbid"`, no default); a constructed result with a flag missing its SHAP value fails validation; every flag in every scored result carries a finite `shap_value`.

### BR-OUT-8 — Own dual-source corpus seam, mirrored not imported; tier-B not triggered / not required (Q4-A)
U18 owns a small **`CorpusSource`** seam — `from_records` (tier-U/S in-memory) + `from_file` (tier-B frozen `corpus/`) — **mirroring, never importing,** `quality_gates/corpus_loader.py`, importing `corpus_generator.records` **call-only**. It **never triggers a corpus build**, imposes **no hard `corpus/` dependency** for Code-Gen, and selects a corpus **by `corpus_version`**.
- **Grounded**: `unit-of-work-dependency.md:47/:95` (corpus-generator R, by corpus_version); `corpus_loader.py` (the mirrored precedent); U18 has **no edge to `quality_gates`** (Q4-C rejected); Q4-A.
- **Checkable**: no module under `backend/outlier_model/` imports `quality_gates`; `corpus_generator.records` is imported call-only; both `from_records` and `from_file` yield the `profile` stream; the unit builds + unit-tests fully on an in-memory fixture with no `corpus/` present.

### BR-OUT-9 — Advisory-only, read-only: no recommendation, no decision, no write, no LLM, no persistence (skill #1/#3, INV-FAITHFUL family)
`outlier-model` emits **anomaly flags + a score**, never a `Recommendation` and never a committed decision; it holds **no LLM, no write transport, no persistence, no `Recommendation`-producing path**. Its output is **advisory input to the memo** (`services.md`: `OUT --> API --> MEMO`), downstream of the deterministic rules.
- **Grounded**: skill #1 (advisory-only), #3 (no LLM in the deterministic/scoring path); `services.md` flow; `unit-of-work.md` U18 boundary.
- **Checkable**: no module produces a `Recommendation` value; no LLM client / write seam / DB import under `backend/outlier_model/`; `OutlierResult` contains a score + flags only, no verdict field.

### BR-OUT-10 — Reference-not-own: consume frozen shapes by shape; edit no unit; import no consumer (dependency matrix)
U18 consumes `ApplicantProfile` / `CorpusRecord` / `CorpusManifest` / `Recommendation` **by shape** and re-declares none; it imports **no consumer** (`memo-agent-core` / `ui-outlier-view` / `observability`) and **edits no frozen unit**. The only cross-unit import is `corpus_generator.records` (its one `R` edge), call-only.
- **Grounded**: `unit-of-work-dependency.md:47` (the single R edge); reference-not-own discipline; Q3-A (consumer wiring deferred to those units).
- **Checkable**: the only `backend.*` import is `corpus_generator.records` (+ `intake.schema` types by shape); no consumer import; no frozen-unit file modified (mtime/scan).

---

## Rule → source traceability

| Rule | Frozen source / decision |
|---|---|
| BR-OUT-1 | FR-OUT-3, US-OUT-3, rules-engine `ALLOWED_INPUT_FIELDS` precedent, skill #6, Q1-A |
| BR-OUT-2 | `requirements.md:144` (CON-BR1 proxy), Q1-A/B, CG-OUT-Fold-3 |
| BR-OUT-3 | `profile_factory.py` nullable fields, rules-engine no-fabrication precedent, CON-DET-1, CG-OUT-Fold-4 |
| BR-OUT-4 | FR-OUT-1, CON-DET-1, skill #5/#7, Q2-A, CG-OUT-Fold-2 |
| BR-OUT-5 | FR-OUT-1/2, PROJECT-BRIEF §C3, Q5-A |
| BR-OUT-6 | FR-OUT-1, rules-engine constant discipline, CG-OUT-Fold-1 |
| BR-OUT-7 | NFR-EXPLAIN-1, US-OUT-2, skill #8, Q3-A |
| BR-OUT-8 | dependency matrix `:47/:95`, `corpus_loader.py`, Q4-A |
| BR-OUT-9 | skill #1/#3, `services.md`, U18 boundary |
| BR-OUT-10 | dependency matrix `:47`, reference-not-own, Q3-A |

**No orphan**: FR-OUT-1 → BR-OUT-4/5/6; FR-OUT-2 → BR-OUT-5/7; FR-OUT-3 → BR-OUT-1/2; CON-DET-1 → BR-OUT-3/4; NFR-EXPLAIN-1 → BR-OUT-7; CON-BR1 → BR-OUT-1/2/3; the corpus/reference boundary → BR-OUT-8/9/10.
