# NFR Requirements — `outlier-model` (U18, C3, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U18 `outlier-model` · C3 · **Phase 2** · **Depth**: comprehensive · **Date**: 2026-07-16 · Stories **US-OUT-1/2/3** · FR-OUT-1/2/3, CON-BR1, CON-DET-1, NFR-EXPLAIN-1, DATA-4.
**Built ON** the frozen FD (**BR-OUT-1..10**; the four-component inventory + method signatures; `OUTLIER_FEATURE_FIELDS`; the `OutlierResult`/`FlaggedFeature`/`OutlierProvenance` schemas; the missing-value **corpus-median imputation** policy; the fit/score lifecycle) — **re-opening none.** Each `NFR-OUT-*` is a **pass/fail testable assertion** traced to its BR-OUT-*. Answers **Q1–Q3 all A** + folds **CG-NFR-OUT-Fold-1..3** (plan §3.5) folded in. **Advisory-only; no LLM; no live tier-B corpus** (a small **seeded fixture corpus** exercises fit/score/SHAP at tier-U).

**Tiers**: **tier-U** = fast, seeded, deterministic, in CI (the default path — no Docker, no LLM, no `corpus/`); **tier-S** = offline smoke (optional); **tier-B** = out-of-band real 300+ corpus (**NOT triggered / NOT required** — BR-OUT-8 / NFR-OUT-CORPUS-1). Every lint/scan carries a **detector self-test** so it can never pass vacuously (CG-NFR-OUT-Fold-3).

---

## 1. Finalized `NFR-OUT-*` targets (pass/fail; acceptance; tier; rigor)

### FULL RIGOR — the two LOAD-BEARING targets

#### NFR-OUT-BIAS-1 — CON-BR1 demographic exclusion, by construction + swap-invariance (BR-OUT-1) — **LOAD-BEARING**
- **Assertion**: the feature vector is built from **only** `OUTLIER_FEATURE_FIELDS`; no demographic identifier can enter it; a name/gender/city swap over identical financials changes **nothing** downstream.
- **Acceptance**: **(a) structural/AST scan** — `FeatureVectorBuilder` references **only** the allow-list fields and **never** `.demographics` / `full_name` / `gender` / `city` in a feature path; `set(FeatureVectorBuilder.field_order()) == OUTLIER_FEATURE_FIELDS`; **+ detector self-test** (a synthetic `profile.demographics.city` feature read is flagged). **(b) swap-invariance teeth** — two profiles with **identical financials** but **swapped `full_name`/`gender`/`city`** produce a **byte-identical feature vector AND a byte-identical `OutlierResult`** (score, flags, provenance). **Teeth**: fails if the scan finds any demographic reference, or if a swap changes any output byte.
- **Boundary with quality-gates**: the `quality-gates` bias-swap suite remains the **external** CON-BR1 delta verifier; this unit proves the **structural mechanism** + owns the swap regression (the rules-engine precedent).
- **Tier**: structural (AST) + component (teeth). **Rigor**: **full (highest)**.

#### NFR-OUT-DET-1 — seeded, version-anchored, RNG-leak-proof determinism (BR-OUT-4 / CON-DET-1) — **LOAD-BEARING**
- **Assertion**: scoring is a pure function of `(profile, corpus_version, seed, outlier_model_version)`; identical inputs → identical output, and no scoring path depends on global RNG / wall-clock / dict-ordering.
- **Acceptance**: **(a) determinism teeth** — same corpus + seed + inputs → **byte-identical `OutlierResult` across N≥2 repeated runs** (within one environment). **(b) global-RNG-perturbation teeth (CG-NFR-OUT-Fold-1)** — between the two runs, **perturb numpy's global RNG state** (`np.random.seed(x)` + draws); the result stays **byte-identical**, proving the scoring is **seed-local** (verified: `IsolationForest(random_state=int)` constructs its own local `RandomState` and does not consume the global RNG) and failing loudly if any path leaked to `np.random.*`. **(c) structural scan** — no `random.`/`np.random.`(uses seeded local only)/`time.`/`datetime.now`/unordered-`set`-iteration in a scoring path; the feature field order is a **stable sort** (+ self-test). Cross-process determinism is **optional** tier-U hardening (BR-OUT-4's stable-sort + Pydantic-deterministic serialization already cover PYTHONHASHSEED/dict-order).
- **Tier**: component (teeth) + structural. **Rigor**: **full (highest)**.

### FULL RIGOR

#### NFR-OUT-FEAT-1 — numeric-only allow-list; documented categorical exclusions (BR-OUT-2)
- **Acceptance**: every field in `OUTLIER_FEATURE_FIELDS` maps to a **numeric** profile value; `employment_type` / `smoking_status` / `occupation` are **absent**; `domain-entities.md §2.2` documents **each** exclusion (structural + doc check).
- **Tier**: structural. **Rigor**: full.

#### NFR-OUT-IMPUTE-1 — a missing optional imputes deterministically and never flags (BR-OUT-3)
- **Acceptance**: a fixture profile with a **deliberately-missing optional** (`bmi_derived` / `existing_debt_obligations_annual` / `dti_ratio` = `None`) scores **deterministically**; the imputed feature's **z-score is exactly 0** and it **never appears in `flagged_features`**; same `(corpus, seed)` → identical imputed value. **Guaranteed robust by NFR-OUT-THRESHOLD-1's positivity guard** (CG-NFR-OUT-Fold-2): `|z|=0` can never reach a strictly-positive threshold. **Teeth**: fails if an imputed feature flags, or if the imputed value varies across runs.
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-OUT-PROV-1 — provenance completeness; corpus-relative + label-independent (BR-OUT-4 / CG-OUT-Fold-2)
- **Acceptance**: **every** `OutlierResult` carries `corpus_version` **and** `seed` **and** `outlier_model_version` — **none omitted** (a result missing any fails validation, by schema); `seed == CorpusManifest.seed`; provenance carries **no** `rulebook_version` (the score is fit on feature vectors and never reads the corpus `label`).
- **Tier**: component. **Rigor**: full.

#### NFR-OUT-COMPOSE-1 — score/flag/explain composition (BR-OUT-5)
- **Acceptance**: `outlier_score` comes from IsolationForest; `flagged_features` are **exactly** the features with `|z| >= Z_SCORE_FLAG_THRESHOLD` (threshold strictly positive — NFR-OUT-THRESHOLD-1); each flag carries a `shap_value` + `direction`; a **normal applicant → `flagged_features == []`** with a valid score + populated provenance.
- **Tier**: component. **Rigor**: full.

#### NFR-OUT-THRESHOLD-1 — one fixed, strictly-positive, parameterized-in-tests threshold (BR-OUT-6 / CG-NFR-OUT-Fold-1 §Q3 / CG-NFR-OUT-Fold-2)
- **Acceptance**: **(a)** exactly **one** fixed named `Z_SCORE_FLAG_THRESHOLD` constant exists — a module-level literal, **not** computed/random. **(b) positivity guard (CG-NFR-OUT-Fold-2)** — asserted **strictly `> 0`** (a z-score flag threshold ≤ 0 is degenerate — it would flag every feature, including exact-mean and imputed ones — so it is *invalid*, not a tuning option; this is what makes BR-OUT-3's "imputed never flags" calibration-robust). **(c) parameterized behavior (Q3-A)** — flag-selection is tested **off the same named constant** the production code reads (a feature with `|z| >= threshold` flags; `|z| < threshold` does not), **never** a hardcoded `3.0`, so a future calibration is a **one-constant edit with tests still green**; plus **one explicit inclusive-boundary case** at the current default (`|z| == threshold` ⇒ flagged).
- **Tier**: component. **Rigor**: full.

#### NFR-OUT-EXPLAIN-1 — zero unexplained flags, by construction (BR-OUT-7 / NFR-EXPLAIN-1)
- **Acceptance**: **construction-time** — `FlaggedFeature` **cannot be instantiated without `shap_value`**: a construction attempt **omitting** `shap_value` **raises** a validation error (not merely that existing flags happen to carry one); `extra="forbid"`, no default on `shap_value`; every flag in every scored result carries a **finite** `shap_value`.
- **Tier**: component (construction). **Rigor**: full.

#### NFR-OUT-CORPUS-1 — dual-source seam; tier-B independence (BR-OUT-8)
- **Acceptance**: `CorpusSource.from_records` **and** `from_file` yield the **same downstream `profile` shape**; **`from_file` is never invoked/required by the default (tier-U) test path** — the unit builds + unit-tests **fully on the in-memory fixture with no `corpus/` present**; `corpus_generator.records` imported **call-only** (mirrors `corpus_loader.py`, never imports `quality_gates`); + detector self-test.
- **Tier**: component + structural. **Rigor**: full.

#### NFR-OUT-ADVISORY-1 — advisory-only; no verdict / LLM / write / persistence (BR-OUT-9)
- **Acceptance**: structural — no module produces a `Recommendation` value; **no LLM client / write transport / DB import** under `backend/outlier_model/`; `OutlierResult` has a score + flags + provenance only, **no verdict field** (+ self-test).
- **Tier**: structural. **Rigor**: full.

#### NFR-OUT-SCOPE-1 — reference-not-own; forward-looking regression guard proven non-vacuous (BR-OUT-10 / CG-NFR-OUT-Fold-3)
- **Acceptance**: structural scans find **no import** of `quality_gates`, `memo_agent_core`, `ui-outlier-view`, or `observability`; the only `backend.*` imports are `corpus_generator.records` (call-only) + `intake.schema` types by shape. **(CG-NFR-OUT-Fold-3)** — `quality_gates` + `memo_agent_core` **exist** (P1), so the scan against them is **non-vacuous today**; `ui-outlier-view` (U20) + `observability` (U21) **do not exist yet**, so those are **forward-looking regression guards** — proven by a **mandatory detector self-test** that feeds a synthetic `from backend.ui_outlier_view import X` / `from backend.observability import Y` line and asserts the detector **flags it** (the scan *mechanism* works, so the forward-looking half is a guard, not a tautology).
- **Tier**: structural. **Rigor**: full.

### SOFT / OBSERVED

#### NFR-OUT-PERF-1 — SHAP + fit cost observed, non-gating (Q2-A)
- **Assertion / Acceptance**: SHAP correctness (a finite value per flagged feature; zero unexplained) is **gating** at **tier-U** on a **small seeded fixture**, kept fast by fixture size + the **tree-model TreeExplainer fast path** (IsolationForest is tree-based); SHAP + fit **runtime is recorded/observed**, **no hard SLO** — consistent with every prior unit's soft-perf posture. The explainer choice (TreeExplainer vs a model-agnostic fallback) is a **Code-Gen realization**.
- **Tier**: observed / soft. **Rigor**: soft.

### GOVERNANCE

#### NFR-OUT-SEC-1 — scoped exclusions *(not a runtime test)*
- **Statement**: the set tests **only** `outlier-model`'s scoring behavior. It does **not** test other units, the WIRE-1 routes, or the tier-B corpus build. It **mirrors** `corpus_loader.py`'s dual-source pattern **without importing it**, consumes frozen shapes **by shape**, and introduces **no write path / no LLM**. Enforced by review + the structural scans above.
- **Tier**: N/A (governance).

---

## 2. Traceability (target → BR-OUT-* / requirement → tier → rigor)

| Target | BR-OUT / requirement | Tier | Rigor |
|---|---|---|---|
| **NFR-OUT-BIAS-1** | BR-OUT-1 / CON-BR1 / FR-OUT-3 | structural + component | **full (highest)** |
| **NFR-OUT-DET-1** | BR-OUT-4 / CON-DET-1 / FR-OUT-1 | component + structural | **full (highest)** |
| NFR-OUT-FEAT-1 | BR-OUT-2 / CON-BR1 | structural | full |
| NFR-OUT-IMPUTE-1 | BR-OUT-3 / CON-DET-1 | component | full |
| NFR-OUT-PROV-1 | BR-OUT-4 / CG-OUT-Fold-2 | component | full |
| NFR-OUT-COMPOSE-1 | BR-OUT-5 / FR-OUT-1/2 | component | full |
| NFR-OUT-THRESHOLD-1 | BR-OUT-6 / CG-OUT-Fold-1 | component | full |
| NFR-OUT-EXPLAIN-1 | BR-OUT-7 / NFR-EXPLAIN-1 / US-OUT-2 | component | full |
| NFR-OUT-CORPUS-1 | BR-OUT-8 | component + structural | full |
| NFR-OUT-ADVISORY-1 | BR-OUT-9 / skill #1/#3 | structural | full |
| NFR-OUT-SCOPE-1 | BR-OUT-10 | structural | full |
| NFR-OUT-PERF-1 | SHAP/fit cost | observed | soft |
| NFR-OUT-SEC-1 | governance | N/A | governance |

**No orphaned BR-OUT rule**: 1→BIAS-1, 2→FEAT-1, 3→IMPUTE-1, 4→DET-1+PROV-1, 5→COMPOSE-1, 6→THRESHOLD-1, 7→EXPLAIN-1, 8→CORPUS-1, 9→ADVISORY-1, 10→SCOPE-1. PERF-1 / SEC-1 cover the SHAP-cost + governance concerns.

---

## 3. Security-Guardrails extension — compliance (enabled extension)

`outlier-model` is a **deterministic statistical scorer** — no secrets used by scoring, no LLM, no persistence, **no write path**, and **demographic-excluded by construction**.

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | Scores an already-validated `intake.ApplicantProfile`; application-input validation is `intake`'s SEC-2. The feature builder additionally rejects any non-allow-list field **by construction** (BIAS-1). |
| Prompt-injection defense | **N/A** | **No LLM / prompt path** in `outlier-model` (skill #3). It is pure statistical Python; the LLM is downstream in the memo. |
| Secrets management | **N/A** | **No secret is used by scoring**; the `secrets-config` seam is config-only (SEC-3 stays that unit's). |
| Read-only DB access | **N/A** | **No DB access, no persistence** — reads the corpus via `CorpusSource` (in-memory fixture / frozen file), writes nothing (BR-OUT-9). |
| Audit logging | **N/A (producer of provenance)** | Persists nothing; it **emits** the `provenance{corpus_version, seed, outlier_model_version}` an auditor/observability consumer records — it does not log itself. |
| Error hygiene (no secret/PII leak) | **Compliant** | The `OutlierResult` carries a score + flags + provenance only — **no demographic field, no PII, no secret** (BIAS-1 by construction; PROV-1 carries versions/seed, not data). |
| **Bias-free by design (CON-BR1)** | **Compliant (load-bearing)** | The feature vector is **demographic-excluded by construction** (BIAS-1: allow-list + AST scan + swap-invariance teeth). The imputation default is a **corpus statistic carrying no demographic signal** (IMPUTE-1). The `quality-gates` bias-swap suite is the external delta verifier. |
| **Reproducibility (CON-DET-1)** | **Compliant (load-bearing)** | Seeded, RNG-leak-proof, version-anchored determinism (DET-1 + PROV-1); no unseeded randomness / wall-clock / dict-ordering. |
| **Full explainability (NFR-EXPLAIN-1)** | **Compliant** | Zero unexplained flags **by schema construction** (EXPLAIN-1: `FlaggedFeature` cannot exist without `shap_value`). |

**No blocking finding.**

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-OUT-1..10 + schemas + imputation policy + four-component inventory) is the substrate — targets attach to it.
- **Q1-A** (behavioral determinism, no golden numbers) — DET-1 tests run-to-run identity + RNG-leak-resistance, **not** sklearn's internal numerics; a version change is caught by the recorded `outlier_model_version`.
- **Q2-A** (SHAP tier-U correctness gating + soft-observed runtime, no hard SLO) — PERF-1; the tree-model fast path keeps it fast; explainer choice → Code-Gen.
- **Q3-A** (threshold parameterized off the named constant) — THRESHOLD-1; calibration = a one-constant edit.
- **Deferred to NFR-Design / Code-Gen**: the exact `Z_SCORE_FLAG_THRESHOLD` value (post-calibration), IsolationForest hyper-parameters (`n_estimators`, `contamination`), the exact `outlier_model_version` string / sklearn lock, the SHAP explainer selection, the seeded-fixture corpus construction. **tier-B corpus build stays out-of-band / not required** (NFR-OUT-CORPUS-1).
