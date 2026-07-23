# NFR Design — Plan (Part 1) — `outlier-model` (U18, C3, **Phase 2**)

**Stage**: BUILD → per-unit loop → **NFR Design Part 1 (Plan)** · **Unit**: U18 `outlier-model` · C3 · **Phase 2** · **Depth**: comprehensive · **Date**: 2026-07-16
**Built ON** the frozen FD (**BR-OUT-1..10**; the four-component inventory + method signatures; `OutlierResult`/`FlaggedFeature`/`OutlierProvenance`; the imputation policy) **and** the approved NFR Requirements (**thirteen `NFR-OUT-*`**; the RNG-leak-proof determinism teeth; the threshold positivity guard; the forward-looking-scan self-test discipline; folds **CG-NFR-OUT-Fold-1..3**) — **re-opening none.** One section per pattern, each structurally meeting its target(s) + traced. Adapted for a **backend Python unit** — "component relationship" here means **module/class relationships + numpy/sklearn API usage + Python data flow**, not a JSX component tree.

**Status**: **Part 1 ANSWERED (Q1–Q4 all A, embedded §3) → ambiguity-check RUN (§3.5) → CLEAN (3 folds, each a design clarification) → Part 2 GENERATED** (`nfr-design-patterns.md` + `logical-components.md`). STOPPED at the NFR Design 2-option completion gate. Full Q&A re-embedded here (standing convention).

---

## 1. Unit context

### 1.1 Inputs this stage builds on (frozen — not re-opened)
- **BR-OUT-1..10** + the **thirteen `NFR-OUT-*`** targets (BIAS-1 + DET-1 load-bearing at full-highest; FEAT/IMPUTE/PROV/COMPOSE/THRESHOLD/EXPLAIN/CORPUS/ADVISORY/SCOPE at full; PERF soft; SEC governance).
- The **four components** (`FeatureVectorBuilder`, `CorpusSource`, `OutlierModel`, `ShapExplainer`) + method signatures; the `OutlierResult`/`FlaggedFeature`/`OutlierProvenance` schemas; the `OUTLIER_FEATURE_FIELDS` allow-list; the corpus-median imputation policy; `Z_SCORE_FLAG_THRESHOLD` (name + 3.0 default + **strictly-positive** invariant, CG-NFR-OUT-Fold-2).

### 1.2 What NFR Design produces (the "how")
For each `NFR-OUT-*` "what", a **named design pattern** ("how") + the **logical component** that realizes it. The load-bearing targets get **by-construction** patterns (structural impossibility), with the StructuralGuard scans as the **regression layer on top** — the discipline used throughout this build.

| Target(s) (the "what") | Pattern to design (the "how") | Component |
|---|---|---|
| **NFR-OUT-BIAS-1** (+ FEAT-1) | **P-OUT-1 AllowlistProjectionPattern** — demographic field structurally unreachable | `FeatureVectorBuilder` |
| **NFR-OUT-DET-1** | **P-OUT-2 SeedLocalDeterminismPattern** — global numpy RNG never touched | `OutlierModel` |
| NFR-OUT-IMPUTE-1 + NFR-OUT-THRESHOLD-1 | **P-OUT-3 ImputeThresholdCompositionPattern** — "imputed-cannot-flag" as a *composed* property | `FeatureVectorBuilder` (imputer) + `OutlierModel` (threshold) |
| NFR-OUT-EXPLAIN-1 | **P-OUT-4 SoleExplainerConstructionPattern** — a flag cannot be built without SHAP at the call site | `ShapExplainer` + `OutlierModel` |
| NFR-OUT-COMPOSE-1 | **P-OUT-5 ScoreFlagExplainCompositionPattern** — the 1:1 map to score/flags/explanation | `OutlierModel` |
| NFR-OUT-CORPUS-1 | **P-OUT-6 DualSourceSeamPattern** — mirrors `corpus_loader.py`, tier-B-independent | `CorpusSource` |
| NFR-OUT-PROV-1 | **P-OUT-7 VersionAnchoredProvenancePattern** — corpus_version + seed + outlier_model_version | `OutlierModel` / `OutlierProvenance` |
| NFR-OUT-SCOPE-1 + ADVISORY-1 (+ structural halves of BIAS/DET/CORPUS) | **P-OUT-8 StructuralGuardPattern** — import/AST scans + detector self-tests (single substrate) | test substrate |
| NFR-OUT-PERF-1 + SEC-1 | **P-OUT-9 ReferencedObservedBoundaryPattern** — soft/observed/governance, not over-specified | (referenced) |

### 1.3 Guardrails held (skill)
- **#5/#6 Reproducibility + bias-free** → P-OUT-1/2/3 (by construction); **#8 Full explainability** → P-OUT-4; **#1/#3 advisory-only/no-LLM** → P-OUT-8 (ADVISORY scan). The `quality-gates` bias-swap suite stays the **external** CON-BR1 verifier; this unit's patterns prove the **structural mechanism**.

### 1.4 Ownership boundaries (reference-not-own — carried from NFR Requirements)
- **Consumed by shape**: `intake.ApplicantProfile`; `corpus_generator.records` (`CorpusRecord`/`CorpusManifest`, call-only via `CorpusSource`); `rules_engine.report_schema.Recommendation` (label space, unused). `secrets-config` (thin config seam).
- **Explicitly excluded (P-OUT-8 scans)**: **no import** of `quality_gates` (U18 has no edge — mirrors `corpus_loader.py`, never imports it), `memo_agent_core`, `ui-outlier-view` (U20, forward-looking), `observability` (U21, forward-looking). `quality_gates` + `memo_agent_core` **exist** (non-vacuous today); the two U20/U21 scans are **forward-looking regression guards proven by the detector self-test** (CG-NFR-OUT-Fold-3).

## 2. NFR Design execution plan (checkboxes)
- [ ] **P1. Unit context** (§1) — DONE (this plan).
- [ ] **P2. Collect `[Answer]:` tags** (§3) + run the mandatory ambiguity-check (surface-and-stop on any genuine gap).
- [ ] **P3. Generate `nfr-design-patterns.md`** — P-OUT-1..9, each meeting its `NFR-OUT-*` target + a **validated module-relationship Mermaid** (7 rules) showing the demographic-exclusion + RNG-isolation as **visible structural properties** + text alternative.
- [ ] **P4. Generate `logical-components.md`** — the five logical components (four + the StructuralGuard substrate) with responsibilities, ownership, **exact method signatures that enforce each by-construction guarantee**, the reference-not-own check, and a component→target coverage table (no orphan).
- [ ] **P5. NFR Design 2-option completion gate.**

## 2.5 Draft pattern set (P-OUT-*) — sketched; finalized in Part 2

- **P-OUT-1 AllowlistProjectionPattern** (BIAS-1/FEAT-1) — `FeatureVectorBuilder` projects the vector by iterating **`OUTLIER_FEATURE_FIELDS`** and pulling each named value through a **fixed accessor map keyed only on those names** — `demographics` has **no accessor entry**, so it is structurally absent from the projection (the rules-engine `NamespaceBuilder` precedent). The exact strength (accessor-map vs a typed intermediate projection whose input **has no** demographics field) is **Q2**.
- **P-OUT-2 SeedLocalDeterminismPattern** (DET-1) — the model's only randomness source is a **seed-local `RandomState`** (verified: `IsolationForest` accepts a `np.random.RandomState` **instance**, and even an `int random_state` is seed-local); **global `np.random.*` is never read/written**. int-vs-injected-instance strength is **Q3**.
- **P-OUT-3 ImputeThresholdCompositionPattern** (IMPUTE-1/THRESHOLD-1) — a missing optional is imputed to the **corpus median**, which makes its **z-score exactly 0**; the threshold is **strictly `> 0`** (CG-NFR-OUT-Fold-2); therefore `|0| < threshold` **always**, so an imputed feature **cannot flag** — a *composed* guarantee, not two coincident facts.
- **P-OUT-4 SoleExplainerConstructionPattern** (EXPLAIN-1) — a `FlaggedFeature` is **required** to carry `shap_value` (schema, FD) **and** is constructed **only** through a path that consumes the `ShapExplainer` output, so a flag cannot be assembled without SHAP **at the call site**, not merely rejected after the fact. The exact call-site mechanism is **Q4**.
- **P-OUT-5 ScoreFlagExplainCompositionPattern** (COMPOSE-1) — `OutlierModel.score` composes IsolationForest score + z-score flags + SHAP into the `OutlierResult` (BR-OUT-5), 1:1 with the brief.
- **P-OUT-6 DualSourceSeamPattern** (CORPUS-1) — `CorpusSource.{from_records, from_file}` mirrors `corpus_loader.py` (never imports it); tier-B (`from_file`) not required for build/test.
- **P-OUT-7 VersionAnchoredProvenancePattern** (PROV-1) — every `OutlierResult` carries `{corpus_version, seed, outlier_model_version}`, populated by construction; label-independent.
- **P-OUT-8 StructuralGuardPattern** (SCOPE-1/ADVISORY-1 + structural halves) — one test substrate of import/AST scans (no-forbidden-import, no-demographic-read, no-global-RNG, no-write/LLM, no-verdict) each with a **detector self-test**.
- **P-OUT-9 ReferencedObservedBoundaryPattern** (PERF-1/SEC-1) — SHAP/fit runtime observed-soft; the Security-Guardrails governance table; not over-specified.

**Component → pattern**: `FeatureVectorBuilder`→P-OUT-1,3; `OutlierModel`→P-OUT-2,3,4,5,7; `ShapExplainer`→P-OUT-4; `CorpusSource`→P-OUT-6; StructuralGuard substrate→P-OUT-8; referenced→P-OUT-9. **No orphan** (§2 table covers all thirteen targets).

## 3. Clarifying questions (Step 3 — fill each `[Answer]:`; full text, lettered options)

> Fill these; I then run the ambiguity-check, then Part 2 (`nfr-design-patterns.md` + `logical-components.md`) **on explicit approval**. **Do not improvise on any ambiguity — flagged and stopped.**

### Q1 — The by-construction MECHANISM for a Python unit (the meta-question): does "header comments + narrow method signatures" transfer, or does Python data-flow need a different mechanism?

**Context**: the frozen UI units made guarantees by-construction via **JSX prop signatures** (a component literally has no prop for the forbidden data) + header comments. `outlier-model` has **no component tree** — its guarantees are about **Python data flow + numpy/sklearn API usage**. The question is what "by-construction" concretely *means* here.

- **A.** **Python-native structural mechanisms as the PRIMARY guarantee, header comments as documentation only** — realize each by-construction guarantee through the mechanism Python actually affords: **(i) typed/narrow signatures + frozen Pydantic/dataclasses** where the forbidden thing is *unrepresentable* (e.g. an intermediate projection type with no demographic field — Q2; a `FlaggedFeature` that cannot exist without `shap_value` — already FD); **(ii) injected dependencies** (a seed-local `RandomState`, the `imputer`) so the only inputs are explicit and global state is never reached (Q3); **(iii) the `StructuralGuard` AST/import scans + detector self-tests** as the **regression layer**; **(iv) header comments** documenting the guarantee for the reader — but **NOT** as the enforcement (unlike the UI prop-signature, a comment enforces nothing in Python). *(Recommended — uses Python's real affordances; the scan is the safety net, not the guarantee; consistent with rules-engine's `NamespaceBuilder` (a real assert) + `test_no_forbidden_imports` (the scan).)*
- **B.** **Header comments + narrow signatures as the primary guarantee** (the UI-unit approach ported directly). *(Weaker — a header comment is not load-bearing in Python; a narrow signature helps only where the type can exclude the forbidden field, which is exactly what A(i) formalizes.)*
- **C.** **Scans/tests only** (no structural impossibility; rely on the StructuralGuard to catch violations). *(Weaker — abandons the by-construction philosophy the load-bearing targets deserve; makes BIAS-1/DET-1 test-only rather than structural.)*

`[Answer]:` A

### Q2 — Demographic exclusion (BIAS-1): accessor-map over the allow-list, or a typed intermediate projection with no demographics field?

**Context**: `FeatureVectorBuilder.build(profile, imputer)` must read profile fields, so `profile.demographics` is reachable *in principle*. How strongly is it made unreachable?

- **A.** **Typed intermediate projection** — an internal step extracts **only** the `OUTLIER_FEATURE_FIELDS` numeric values into a small **frozen `FeatureInputs` dataclass/dict that has no `demographics` field**, and the vector is built **from that**, never from the raw `ApplicantProfile`. A demographic field is then **structurally absent** from the builder's working type — the closest Python analog to the UI prop-signature isolation (the "props" the vector-builder sees literally exclude demographics). The AST scan + swap-invariance teeth remain the regression layer. *(Recommended — strongest by-construction; mirrors ui-memo-view's StructuralIsolationCompositionPattern in Python terms; the swap test then confirms a design property, not the only safeguard.)*
- **B.** **Accessor map keyed only on allow-list names** — the builder iterates `OUTLIER_FEATURE_FIELDS` and pulls each via a `{name: accessor}` map with **no demographics entry** (the rules-engine `NamespaceBuilder` precedent: `assert set(namespace)==ALLOWED_INPUT_FIELDS`). Reachable-but-unreferenced; the scan catches a violation. Simpler; slightly weaker than A (the raw profile is still in scope). 
- **C.** **Both** — the typed projection (A) built via the accessor map (B). Maximal, marginally more code.

`[Answer]:` A

### Q3 — Seed-locality (DET-1): inject an explicit local `RandomState` instance, or pass an int `random_state`?

**Context**: both are seed-local (verified: an int `random_state` builds its own internal `RandomState`; a passed **instance** is also local). The question is which the SeedLocalDeterminismPattern uses, given the goal is to make RNG leakage **structurally hard to introduce**.

- **A.** **Construct and inject an explicit `np.random.RandomState(seed)` instance** into IsolationForest (seed single-sourced from `CorpusManifest.seed`), and pair it with a **StructuralGuard scan forbidding any `np.random.<global>` call** in a scoring path. The local RandomState is **visible in the code** (self-documenting seed-locality) and the scan makes a global-RNG call a **build failure** — so leakage is structurally hard to introduce, not just caught by the determinism teeth. *(Recommended — most explicit about the seed-locality the DET-1 perturbation teeth verify; the injected instance + the no-global-RNG scan are complementary.)*
- **B.** **Pass an int `random_state=seed`** — simplest, and seed-local (sklearn builds the local RandomState internally). But global-RNG-locality is then an *sklearn* property the reader must know, not a visible code property; a stray `np.random.*` elsewhere in a scoring path would not be as obviously wrong.
- **C.** **Both** — inject the instance **and** keep the no-global-RNG scan, treating the int form as disallowed. *(Effectively A; listed for completeness.)*

`[Answer]:` A

### Q4 — Zero-unexplained at the call site (EXPLAIN-1): how do `OutlierModel` / `ShapExplainer` signatures compose so a flag cannot be built without SHAP?

**Context**: the schema already makes `shap_value` **required** on `FlaggedFeature` (a flag can't be *validated* without it). The user asks to extend this to the **call site** — so a flag can't even be *assembled* without going through SHAP.

- **A.** **`ShapExplainer` is the SOLE constructor of `FlaggedFeature`** — `OutlierModel.score` computes the candidate flags (feature + z + direction) but does **not** build `FlaggedFeature` objects; it hands the candidates to `ShapExplainer.explain(...) -> list[FlaggedFeature]`, which is the **only** code path that constructs a `FlaggedFeature` (attaching the `shap_value`). A flag is therefore **born from SHAP by construction** — no call site can produce one without an explanation (mirrors ui-approval-gate's single-call-site guarantee). A StructuralGuard scan asserts `FlaggedFeature(` is constructed in **exactly one** place (the explainer) + self-test. *(Recommended — extends the schema guarantee to the call site; makes "zero unexplained" a single-constructor structural property, not just a validation.)*
- **B.** **Schema-only + a `make_flag(feature, z, shap_value, direction)` factory** requiring all four positionally — the only builder, so `shap_value` is always supplied, but the factory could in principle be called with a placeholder. Weaker than A (no single-source guarantee that the value came from SHAP).
- **C.** **Schema-only** (the FD's required field), no call-site pattern. *(Weakest — leaves "the value actually came from SHAP" unenforced structurally; a flag could be built with a fabricated shap_value.)*

`[Answer]:` A

---

## 3.5 Ambiguity-check (RUN 2026-07-16, against Q1–Q4 all-A + the frozen FD + NFR Requirements) — **CLEAN to proceed; three folds — one a substantive design clarification (check i)**

Run against the four answers + BR-OUT-1..10 + the thirteen NFR-OUT-* + the folds. The three user-requested checks each resolve; **check (i) surfaced a real inconsistency in the frozen FD's phrasing** and is reconciled by a design clarification that **preserves the frozen intent** (NFR-Design's remit is the HOW). Per the CR-Fold-7 discipline the user endorsed: derive the one sound resolution, disclose prominently, flag for gate confirmation. **No re-opening of the FD** — the intent ("an imputed feature never flags") stands; only the *mechanism* is made correct.

- **🟠 CG-ND-OUT-Fold-1 (check i — HEADLINE: the FD's "median imputation" and "z exactly 0" are inconsistent; the projection MUST track imputed-ness).** **Verified numerically**: a missing optional imputed to the **corpus median** yields a flagging z-score of **≈ −0.43 for a right-skewed feature (income-like)**, **NOT exactly 0** — because z is computed against the corpus **mean/std**, and for a skewed feature `median ≠ mean`. So `domain-entities.md §2.3` / BR-OUT-3's two literal claims ("impute to median" AND "z-score exactly 0 by construction") **cannot both hold** as stated. The frozen **intent** is unambiguous (BR-OUT-3: "an imputed feature never contributes to flagged_features"); the stated **mechanism** was slightly wrong. **Resolution (design clarification, intent preserved)**: (1) imputation happens **after** the raw extraction, filling a missing optional with the **corpus median** — used as the **IsolationForest score input** (a reasonable central value for the multivariate model, unchanged); (2) the **`FeatureInputs` projection tracks which features were imputed** (an `imputed` mask — directly answering the user's check: **yes, the type must represent "value or imputed" distinctly, a plain float is NOT sufficient**); (3) at **flagging**, an imputed feature's z-score is **0 by design** — a **missing value is not anomaly evidence**, which is semantically correct, not a hack — so it can never reach the strictly-positive threshold. This makes IMPUTE-1's "imputed never flags" a **real by-construction property** (an imputed feature is excluded from flag candidacy / assigned z=0 by the mask, not by the median coinciding with the mean), and **reconciles both frozen claims** (median for the score; z=0 for imputed at flagging). **Folded into P-OUT-3 + the `FeatureVectorBuilder`/`OutlierModel` signatures; flagged for confirmation at the NFR-Design gate** (Request Changes if a different reconciliation — e.g. mean imputation — is wanted).
- **🟢 CG-ND-OUT-Fold-2 (check ii — the sole-constructor pattern handles zero flags cleanly).** `OutlierModel.score` computes candidate flags (features with `|z| >= threshold`, excluding imputed ones per Fold-1) and hands them to `ShapExplainer.explain(candidates, ...) -> list[FlaggedFeature]`. For a **normal applicant with zero candidates**, `explain([])` **short-circuits to `[]`** — it runs **no SHAP computation** (so a normal applicant incurs no SHAP cost) and constructs **zero** `FlaggedFeature` objects. This is **clean and non-degenerate**: the sole-constructor pattern holds trivially (zero flags built through the one path), no special-case branch, no "explain nothing" awkwardness. **Confirmed — no change needed.**
- **🟢 CG-ND-OUT-Fold-3 (check iii — the seed flows ONLY into OutlierModel).** Confirmed the injected `RandomState` never needs threading through the other two components: **`CorpusSource`** is deterministic I/O/parsing (no randomness); **`FeatureVectorBuilder`** imputes to the **corpus median** — a **deterministic statistic** (percentile/sort, no RNG) — so it needs no seed; **`OutlierModel` → IsolationForest** is the **sole randomized step** (the injected instance goes here); **`ShapExplainer`** uses **TreeExplainer**, which is **deterministic for a tree model** (exact path-dependent Shapley values, no sampling), so it needs no seed either. **Caveat noted**: if Code-Gen ever fell back to a *sampling-based* explainer (KernelExplainer), the same injected-`RandomState` discipline would extend to it — but the pinned TreeExplainer fast path (OUT-D3) keeps the seed local to `OutlierModel`. **Confirmed — the seed is single-component by design.**

**Verdict: CLEAN to generate `nfr-design-patterns.md` + `logical-components.md`.** No genuine multi-way fork requiring a stop. CG-ND-OUT-Fold-1 is a substantive **mechanism clarification** (imputed-mask + z=0-by-design) that makes the frozen FD's guarantee correct and is **disclosed here + carried into both artifacts + flagged at the gate**; Folds 2 & 3 are clean confirmations. None improvised.

---

## 4. Gate

**Part 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** The four `[Answer]` tags (Q1–Q4) are **BLANK**. On the filled answers: run the mandatory **ambiguity-check** against the answers + the frozen FD + the approved NFR Requirements + the underwriting-rules skill — **surface-and-stop on any genuine gap, do not improvise** — then, **on explicit approval**, generate `nfr-design-patterns.md` (P-OUT-1..9 + a validated module-relationship Mermaid, 7 rules, demographic-exclusion + RNG-isolation as visible structural properties) + `logical-components.md` (the five components + exact by-construction method signatures + reference-not-own check + component→target coverage, no orphan), embedding the full Q&A here (standing convention). **NO NFR-Design artifact generated in Part 1; no code.** Holds: WIRE-1 untouched; the 17 frozen P1 units untouched; the closed composition root untouched; **tier-B corpus run NOT authorized** (not required — NFR-OUT-CORPUS-1); the `audit_store` Docker-guard gap untouched; no other unit started; the 23-unit decomposition unchanged.
