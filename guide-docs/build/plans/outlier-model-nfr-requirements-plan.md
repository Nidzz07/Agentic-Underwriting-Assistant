# NFR Requirements — Plan (Part 1) — `outlier-model` (U18, C3, **Phase 2**)

**Stage**: BUILD → per-unit loop → **NFR Requirements Part 1 (Plan)** · **Unit**: U18 `outlier-model` · C3 · **Phase 2** · **Depth**: comprehensive · **Date**: 2026-07-16
**Stories**: US-OUT-1/2/3 · **Requirements**: FR-OUT-1/2/3, CON-BR1, CON-DET-1, NFR-EXPLAIN-1, DATA-4.
**Built ON** the **frozen FD** — `domain-entities.md` (the four-component inventory + method signatures; `OUTLIER_FEATURE_FIELDS`; the `OutlierResult`/`FlaggedFeature`/`OutlierProvenance` schemas; the missing-value imputation policy), `business-rules.md` (**BR-OUT-1..10**), `business-logic-model.md` (the fit/score lifecycle) — **re-opening none of it.** FD approved 2026-07-16 (Continue), **BR-OUT-3 corpus-median imputation retained** (the 6-field-only alternative explicitly declined).

**Status**: **Part 1 ANSWERED (Q1–Q3 all A, embedded §3) → ambiguity-check RUN (§3.5) → CLEAN (3 folds, each a concrete test refinement) → Part 2 GENERATED** (`nfr-requirements.md` + `tech-stack-decisions.md`). STOPPED at the NFR Requirements 2-option completion gate. Full Q&A re-embedded here (standing convention).

---

## 1. Unit context

### 1.1 What this stage decides
The **pass/fail quality targets** (`NFR-OUT-*`) attached to the frozen FD — HOW each BR-OUT-* is verified, at what **test tier**, with what rigor. It decides **no functional behavior** (that is the frozen FD) and generates no code. The dominant NFRs are **reproducibility** (CON-DET-1 / BR-OUT-4), **bias-exclusion** (CON-BR1 / BR-OUT-1), and **faithful explanation** (NFR-EXPLAIN-1 / BR-OUT-7) — each already designed **by construction** in the FD; this stage pins the guards that verify the construction held.

### 1.2 Frozen FD carried in (NOT re-opened — targets attach to these)
- **BR-OUT-1..10** — the checkable invariants (the NFR set is the pass/fail expression of these).
- The **four components** (`FeatureVectorBuilder`, `CorpusSource`, `OutlierModel`, `ShapExplainer`) + method signatures.
- **`OUTLIER_FEATURE_FIELDS`** (numeric-only allow-list, demographic-excluded by construction) + the missing-optional **corpus-median imputation** policy (an imputed feature's z-score is 0 by construction).
- **`OutlierResult`** = `{outlier_score, is_outlier, flagged_features[], provenance{corpus_version, seed, outlier_model_version}}`; **`FlaggedFeature`** = `{feature, z_score, shap_value, direction}` (`shap_value` **required** — zero-unexplained by schema).
- The **fit/score lifecycle**; **`Z_SCORE_FLAG_THRESHOLD`** name + **3.0 default** (value confirmable at NFR/Code-Gen — CG-OUT-Fold-1).

### 1.3 Governing requirements + tier convention
- **FR-OUT-1/2/3, CON-DET-1, CON-BR1, NFR-EXPLAIN-1, DATA-4.** **NFR-OBS-1/2** referenced only for a scope boundary (observability is U21, downstream — not tested here).
- **Test tiers** (inherited vocabulary): **tier-U** = fast, deterministic, seeded, in CI (the default path — no Docker, no LLM, no tier-B corpus); **tier-S** = offline smoke (optional); **tier-B** = out-of-band, real 300+ corpus (**NOT triggered / NOT required** by U18 — BR-OUT-8). SHAP/sklearn run at **tier-U on a small seeded fixture corpus**.

### 1.4 Guardrails held (underwriting-rules skill)
- **#5/#6 Reproducibility + bias-free** (CON-DET-1/CON-BR1), **#8 Full explainability** (NFR-EXPLAIN-1), **#1/#3 advisory-only / no-LLM-in-path**. Each maps to a target below. The **quality-gates bias-swap suite stays the external CON-BR1 verifier**; this unit proves the **structural mechanism** + its own swap-invariance regression (the rules-engine precedent: the unit proves the mechanism, quality-gates verifies the delta).

## 2. NFR Requirements execution plan (checkboxes)
- [ ] **P1. Unit context** (§1) — DONE (this plan).
- [ ] **P2. Collect `[Answer]:` tags** (§3) + run the mandatory ambiguity-check (surface-and-stop on any genuine gap).
- [ ] **P3. Generate `nfr-requirements.md`** — the `NFR-OUT-*` set (§2.5) with acceptance criteria + tier + rigor + traceability + the Security-Guardrails compliance table.
- [ ] **P4. Generate `tech-stack-decisions.md`** — D-decisions (sklearn/shap/numpy already floored in `requirements.txt`; the `outlier_model_version` provenance discipline; no NEW dependency beyond the FD's ML stack; the seeded-fixture test substrate).
- [ ] **P5. FD 2-option completion gate** for NFR Requirements.

## 2.5 Draft `NFR-OUT-*` target map (every BR-OUT-* → a pass/fail target; the six user-named tests folded in)

| Target | Attaches to | Acceptance (pass/fail) | Tier | Rigor |
|---|---|---|---|---|
| **NFR-OUT-BIAS-1** *(load-bearing)* | BR-OUT-1 | **(a) structural/AST scan**: `FeatureVectorBuilder` reads **only** `OUTLIER_FEATURE_FIELDS`, **never** references `.demographics`/`full_name`/`gender`/`city` in a feature path (+ detector self-test); `set(field_order()) == OUTLIER_FEATURE_FIELDS`. **(b) swap-invariance teeth**: identical financials with **swapped name/gender/city** → **byte-identical feature vector AND `OutlierResult`**. Fails if either the scan finds a demographic reference or a swap changes any output. | structural + component (teeth) | **full (highest)** |
| **NFR-OUT-FEAT-1** | BR-OUT-2 | the allow-list is **numeric-only**; the three categoricals (`employment_type`/`smoking_status`/`occupation`) are **absent**; each exclusion has a documented rationale (structural + doc check). | structural | full |
| **NFR-OUT-IMPUTE-1** | BR-OUT-3 | **teeth**: a fixture profile with a **deliberately-missing optional** (`bmi_derived` / `existing_debt_obligations_annual` / `dti_ratio` = None) scores deterministically; the imputed feature's **z-score is exactly 0** and it **never appears in `flagged_features`**; same `(corpus, seed)` → same imputed value. | component (teeth) | full |
| **NFR-OUT-DET-1** *(load-bearing)* | BR-OUT-4 | **determinism teeth**: same corpus + seed + inputs → **byte-identical `OutlierResult` across N≥2 repeated runs** (within one environment); no `random`/`time`/`datetime.now`/unordered-set-iteration in a scoring path (scan); field order is a stable sort. **(Q1 governs whether exact numeric values are also pinned.)** | component (teeth) + structural | **full (highest)** |
| **NFR-OUT-PROV-1** | BR-OUT-4 / CG-OUT-Fold-2 | **provenance-completeness**: **every** `OutlierResult` carries `corpus_version` + `seed` + `outlier_model_version`, **none omitted**; `seed` equals `CorpusManifest.seed`; provenance carries **no** `rulebook_version` (label-independent). | component | full |
| **NFR-OUT-COMPOSE-1** | BR-OUT-5 | `outlier_score` from IsolationForest; `flagged_features` are **exactly** the features with `|z| >= Z_SCORE_FLAG_THRESHOLD`; each carries a `shap_value` + `direction`; a **normal applicant → `flagged_features == []`** with a valid score. | component | full |
| **NFR-OUT-THRESHOLD-1** | BR-OUT-6 | exactly **one** fixed named threshold constant exists (module-level literal, not computed/random); flag-selection **behavior** is verified **parameterically off that constant** (not a hardcoded 3.0) + one inclusive-boundary case at the current default. **(Q3 governs the parameterization.)** | component | full |
| **NFR-OUT-EXPLAIN-1** | BR-OUT-7 | **construction-time**: `FlaggedFeature` **cannot be instantiated without `shap_value`** (a missing-field construction attempt **raises** validation) — not merely that existing flags happen to carry one; every flag in every result carries a finite `shap_value`. | component (construction) | full |
| **NFR-OUT-CORPUS-1** | BR-OUT-8 | `from_records` **and** `from_file` yield the **same downstream `profile` shape**; **`from_file` is never invoked/required by the default (tier-U) test path** (tier-B independence — the unit builds + tests fully on the in-memory fixture with no `corpus/` present); `corpus_generator.records` imported **call-only**. | component + structural | full |
| **NFR-OUT-ADVISORY-1** | BR-OUT-9 | structural: no module produces a `Recommendation` value; **no LLM client / write transport / DB import** under `backend/outlier_model/`; `OutlierResult` has a score + flags only, no verdict field (+ self-test). | structural | full |
| **NFR-OUT-SCOPE-1** | BR-OUT-10 | structural scans: **no import of `quality_gates`, `memo_agent_core`, `ui-outlier-view`, `observability`** (P2 units U18 has no edge to; several not yet built); the only `backend.*` imports are `corpus_generator.records` (call-only) + `intake.schema` types by shape (+ detector self-tests). | structural | full |
| **NFR-OUT-PERF-1** | (SHAP/fit cost) | **observed/soft, non-gating**: SHAP + fit runtime **recorded** on the small seeded fixture; **no hard SLO** (consistent with every prior unit's soft-perf posture). **(Q2 governs whether any perf consideration is added.)** | observed / soft | soft |
| **NFR-OUT-SEC-1** | (skill guardrails) | governance: the Security-Guardrails compliance table — input-validation N/A (reads validated `ApplicantProfile`), secrets N/A (no key used by scoring), no-PII (demographic-excluded by construction), advisory-only + no-write. | governance | N/A |

**No orphan**: BR-OUT-1→BIAS-1; 2→FEAT-1; 3→IMPUTE-1; 4→DET-1+PROV-1; 5→COMPOSE-1; 6→THRESHOLD-1; 7→EXPLAIN-1; 8→CORPUS-1; 9→ADVISORY-1; 10→SCOPE-1; SHAP/fit cost→PERF-1; guardrails→SEC-1. The **six user-named tests** are: the BIAS-1 structural-scan+swap-teeth pair; the DET-1 determinism teeth + PROV-1 completeness; the EXPLAIN-1 construction-time test; the IMPUTE-1 z-score-0 teeth; the SCOPE-1 reference-not-own scans; the CORPUS-1 dual-source + tier-B-independence tests.

## 3. Clarifying questions (Step 3 — fill each `[Answer]:`; full text, lettered options)

> Fill these; I then run the ambiguity-check, then Part 2 (`nfr-requirements.md` + `tech-stack-decisions.md`) **on explicit approval**. **Do not improvise on any ambiguity — flagged and stopped.**

### Q1 — Testing the IsolationForest fit for determinism: pin exact numeric values, or "same input twice → same output twice"?

**Context**: BR-OUT-4 / CON-DET-1 require reproducibility, but IsolationForest is a **real sklearn model**, not a hand-rolled algorithm. Two ways to test its determinism: assert **exact expected numeric outputs** from a fixed fixture corpus (golden-master), or assert **run-to-run identity** (same input twice → byte-identical twice) **without** pinning specific numbers. Note two facts: (a) `outlier_model_version` was deliberately designed (Q2-A/CG-OUT-Fold-2) to **record** the sklearn version precisely because sklearn does **not** guarantee cross-version numeric identity — so golden numbers would couple the tests to one sklearn build and break on the very upgrade the provenance field exists to track; (b) absolute float values can also differ across **platforms/BLAS**, whereas run-to-run identity within one environment is what seeding actually guarantees.

- **A.** **Behavioral determinism only** — assert **byte-identical `OutlierResult` across N≥2 repeated runs** on the same corpus+seed+inputs (the invariant CON-DET-1/BR-OUT-4 actually require), **without** asserting specific numeric values. sklearn is a **trusted dependency**: the unit tests **its own** determinism (single-sourced seed, no wall-clock, stable field order), not sklearn's internal numerics. A version change is caught by the **recorded `outlier_model_version`**, not by a brittle golden-master. Mirrors how prior units tested determinism (byte-identical output across N runs, never asserting numeric internals). *(Recommended — tests the invariant that matters; avoids coupling to a sklearn build/platform; consistent with the version-anchoring design.)*
- **B.** **Golden-master exact values** — pin expected `outlier_score` / z-scores from a committed fixture corpus. Catches any output change, but **brittle**: a legitimate sklearn upgrade (which `outlier_model_version` records) breaks it, forcing test rewrites; and it tests sklearn's numerics rather than U18's logic.
- **C.** **Hybrid** — behavioral determinism as the **gating** test + a **loose, non-gating** golden check (e.g. relative ranking / flag-set stability) recorded as observed. More signal, more maintenance; the loose check still risks version drift.

`[Answer]:` A

### Q2 — SHAP's test tier + whether it needs a performance/timeout consideration (unlike any prior unit)

**Context**: US-OUT-2 / NFR-EXPLAIN-1 make SHAP correctness (zero unexplained flags) **gating**, but SHAP can be **computationally slower** than the rest of the unit — a cost no prior unit faced. Relevant fact: IsolationForest is **tree-based**, so SHAP's **TreeExplainer** (the fast path) applies, and on a **small seeded fixture corpus** the cost is bounded — so the concern is largely mitigated by construction. The open question is whether the NFR set adds a **performance gate** for SHAP or keeps the project's uniform **soft-perf** posture.

- **A.** **Tier-U functional correctness on a small seeded fixture** (SHAP produces a finite value per flagged feature; zero unexplained — gating), kept fast by **fixture size + the tree-model fast path**; SHAP/fit **runtime observed/soft** (NFR-OUT-PERF-1, **non-gating**), **no hard SLO** — consistent with every prior unit. The explainer choice (TreeExplainer vs a model-agnostic fallback) is a **Code-Gen realization**; the NFR pins the **tier + soft-perf posture**, not a millisecond budget. *(Recommended — keeps SHAP correctness gating without introducing the project's first hard perf SLO; the small fixture + tree fast path make timing a non-issue.)*
- **B.** **Add a hard performance gate / timeout** on SHAP specifically (e.g. explanation < X s). Introduces the project's **first hard perf SLO** — a departure from the soft-perf precedent, and an X no artifact backs.
- **C.** **Defer SHAP to tier-B / out-of-band** (too slow for CI). *(Rejected — SHAP correctness is US-OUT-2 core and must be tier-U + gating; deferring it would leave zero-unexplained unverified in CI.)*

`[Answer]:` A

### Q3 — Threshold testing: parameterized off the named constant, or hardcode 3.0?

**Context**: `domain-entities.md §5` / CG-OUT-Fold-1 pin `Z_SCORE_FLAG_THRESHOLD` as a **named constant with a 3.0 default, confirmable after calibration**. If tests **hardcode 3.0**, a later calibration change forces test rewrites — defeating the "confirmable later" design. The question is whether the NFR set tests threshold **behavior generically**.

- **A.** **Parameterize off the single named constant** — tests assert the **relationship** (a feature with `|z| >= Z_SCORE_FLAG_THRESHOLD` flags; `|z| <` it does not; the boundary is **inclusive** per the pinned convention), driving off the **same constant the production code reads** (BR-OUT-6), **never** a hardcoded literal. Plus **one explicit inclusive-boundary case** at the current default. So a calibration change = **one constant edit, tests still green** (they assert behavior, not the number). *(Recommended — honors CG-OUT-Fold-1's "confirmable later"; the tests verify the flag-selection logic, which is what matters, and survive re-tuning.)*
- **B.** **Hardcode 3.0** in the tests. Simple today, but **brittle** — calibration requires rewriting tests, defeating the deferred-value design.
- **C.** **Test only that a constant exists**, not its flag-selection behavior. *(Too weak — leaves the |z|≥threshold selection logic unverified.)*

`[Answer]:` A

---

## 3.5 Ambiguity-check (RUN 2026-07-16, against Q1–Q3 all-A + the frozen FD) — **CLEAN to proceed; three folds, each a concrete test refinement**

Run against the three answers + the frozen FD (BR-OUT-1..10, the schemas, the imputation policy, the four-component inventory) + the underwriting-rules skill. The three user-requested checks are **sharp and each resolves into a concrete refinement** — none is a blocking gap, none improvised.

- **🟡 CG-NFR-OUT-Fold-1 (check i — test isolation must catch numpy-global-RNG leakage, not just same-process repetition).** Q1-A's "byte-identical across N≥2 runs" is necessary but, alone, would **not** catch the bug class the user names — a scoring path accidentally consuming numpy's **global** RNG (`np.random.*`) instead of the seed-local one would still be identical across two *adjacent* in-process runs. **Verified on disk**: `IsolationForest(random_state=<int>)` constructs its **own seed-local `RandomState`** and does **not** consume the global RNG — a fit/score was **byte-identical across a deliberate global-RNG perturbation** (seed 999 → 1000 draws → seed 1234 between the two runs). So the resolution is a concrete DET-1 refinement: the determinism teeth **perturb numpy's global RNG state between the two runs** (score → `np.random.seed(x)` + draws → score) and assert **byte-identical** — which **proves seed-locality and fails loudly if any scoring path leaked to the global RNG**. Cross-process determinism is noted as **optional** tier-U hardening (PYTHONHASHSEED/dict-order), already covered by BR-OUT-4's stable-sort + no-dict-order-reliance + Pydantic-deterministic-serialization; the global-RNG-perturbation variant is the **material** addition. **Folded into NFR-OUT-DET-1.**
- **🟡 CG-NFR-OUT-Fold-2 (check ii — the imputation guarantee needs a threshold-positivity guard).** The user's interaction is real: an imputed feature has `z == 0` (BR-OUT-3), and NFR-OUT-COMPOSE-1 flags features with `|z| >= Z_SCORE_FLAG_THRESHOLD`. If the threshold were ever calibrated to **0 or negative**, then `|0| >= threshold` is **true** → an imputed feature **would** be flagged, **violating BR-OUT-3**. So BR-OUT-3's "imputed feature never flagged" holds **only under the invariant `Z_SCORE_FLAG_THRESHOLD > 0`**. Resolution: **NFR-OUT-THRESHOLD-1 gains an explicit positivity guard** — the constant is asserted **strictly > 0** (a z-score flag threshold ≤ 0 is statistically degenerate — it would flag every feature including exact-mean ones — so it is an *invalid* value, not a tuning option). This makes the imputation guarantee **calibration-robust**: as long as the threshold stays positive (which it must), `|z|=0` can never flag. **Folded into NFR-OUT-THRESHOLD-1 (positivity guard) + a cross-reference note in NFR-OUT-IMPUTE-1.**
- **🟢 CG-NFR-OUT-Fold-3 (check iii — the SCOPE-1 forward-looking scans are a regression guard proven by the self-test, not vacuous).** Correct that `ui-outlier-view` (U20) and `observability` (U21) **do not exist yet**, so the production scan for "no import of them" passes trivially today. This is **exactly** why the **detector self-test** is mandatory (the established convention on every prior unit's structural scan): the self-test feeds the detector a **synthetic** `from backend.ui_outlier_view import X` / `from backend.observability import Y` line and asserts the detector **flags it** — proving the scan **mechanism works**, so it is a **forward-looking regression guard** (it will catch a real violation the day those units exist), **not** a vacuous pass. Note the scan is **partly non-vacuous today**: `quality_gates` and `memo_agent_core` **do exist** (P1), so the "no import of them" scan runs against real importable modules right now. Resolution: **NFR-OUT-SCOPE-1 explicitly distinguishes** the production scan (passes because clean) from the **detector self-test** (proves the mechanism for all four targets), so the forward-looking half is a guard, not a tautology. **Folded into NFR-OUT-SCOPE-1's acceptance criteria.**

**Verdict: CLEAN to generate `nfr-requirements.md` + `tech-stack-decisions.md`.** No genuine multi-way fork remains. All three folds are **test-refinements derived from the checks** (DET-1 global-RNG-perturbation variant; THRESHOLD-1 positivity guard closing the imputation-flag hole; SCOPE-1 self-test-proves-mechanism) — each disclosed here and carried into the artifacts, none an improvisation.

---

## 4. Gate

**Part 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** The three `[Answer]` tags (Q1–Q3) are **BLANK**. On the filled answers: run the mandatory **ambiguity-check** against the answers + the frozen FD (BR-OUT-1..10, the schemas, the imputation policy) + the underwriting-rules skill — **surface-and-stop on any genuine gap, do not improvise** — then, **on explicit approval**, generate `nfr-requirements.md` + `tech-stack-decisions.md`, embedding the full Q&A here (standing convention). **NO NFR artifact generated in Part 1; no code.** Holds: WIRE-1 untouched; the 17 frozen P1 units untouched; the closed composition root untouched; **tier-B corpus run NOT authorized** (and not required — BR-OUT-8 / NFR-OUT-CORPUS-1); the `audit_store` Docker-guard gap untouched; no other unit started; the 23-unit decomposition unchanged.
