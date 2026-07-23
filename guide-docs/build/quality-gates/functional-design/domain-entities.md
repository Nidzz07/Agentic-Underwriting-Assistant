# Domain Entities — `quality-gates` (U13)

**Stage**: BUILD → Functional Design (per-unit) · the four blocking verification gates · **Depth**: COMPREHENSIVE
**Unit**: U13 `quality-gates` · **Date**: 2026-07-08 · **single verification authority** for CON-BR1 / CON-BR2·AC-1 / QA-3 / AC-5 · Stories **US-PLAT-3/4/5/6**.
**Scope**: A verification unit's "entities" are its **module inventory** (the four gates + the corpus-source seam), the **consumed frozen shapes** it verifies against, and the **human-readable evidence records** each gate emits. `quality-gates` **verifies**; it does **not** enforce or re-define any invariant, and re-implements **no** rule evaluation.

Built exactly on the **seven locked FD-plan answers (all A)** and the **five QG-Folds** in
`guide-docs/build/plans/quality-gates-functional-design-plan.md` — re-opening none.

---

## 1. Module inventory (the four gates + the corpus seam)

`quality-gates` lives at **`backend/quality_gates/`** (Q6-A — realized per-unit convention; supersedes the older `unit-of-work.md` tree's `backend/quality/`). It is a **CI/pytest harness**: each gate is **both a collected pytest test (blocking) and an evidence-report emitter** (Q7-A).

| Module | Kind | Responsibility | Verifies (traces) |
|---|---|---|---|
| **`corpus_loader`** | source seam | yields `ApplicantProfile`s from the frozen `corpus/profiles.json` **or** an in-memory `CorpusRecord`/profile list (QG-Fold-1) — the tier-U/S-vs-tier-B seam | — (enabler for all gates) |
| **`bias_swap_suite`** | gate | swap `{full_name, gender, city}` on an otherwise-identical profile → engine `recommendation` **unchanged**; **delta = 0, any delta blocking**; proxy check over `occupation`+`income` | CON-BR1, NFR-BIAS-1, QA-2, AC-3, FR-PROV-GATE-1 · US-PLAT-3 |
| **`reproducibility_suite`** | gate | `evaluate()` **×10** per profile → **identical `evaluation_output()` projection** each run; **100%**; engine-deterministic, not LLM wording | CON-BR2, NFR-REPRO-1, QA-1, AC-1, FR-PROV-GATE-1 · US-PLAT-4 |
| **`rule_coverage_report`** | gate | every `rule_id` in the loaded rulebook reaches a **definite PASS or FAIL** in ≥1 corpus record; **100%**, any uncovered rule blocking | QA-3, AC-4 · US-PLAT-5 |
| **`coverage_gate`** | gate | **structural wiring meta-assertion** that `pyproject --cov-fail-under=90` is present + ≥90 (QG-Fold-3) + a coverage-% **evidence** report; **binding enforcement stays in `pyproject`** | AC-5, QA-6 · US-PLAT-6 |

**Offline testability (QG-Fold-1/2):** all four gates run their **logic** at tier-U/S over a **small test-scoped corpus stub** + a controlled rulebook — no live LLM, no real 300+ corpus, no network. The **real full-corpus acceptance runs** (bias-swap delta=0 over the actual corpus, 100% rule coverage over the real rulebook) are **tier-B**, out-of-band, **not a Code-Gen blocker** (§4 boundary).

---

## 2. Consumed frozen shapes (reference-not-own — call-only, none edited)

| Consumed surface | From unit | Used for | Answer / Fold |
|---|---|---|---|
| `rules_engine.engine.RulesEngine.evaluate(profile, rulebook_version) -> RuleResultReport` | `rules-engine` | the deterministic engine under verification (all three engine-driven gates) | Q3, QG-Fold-4 |
| `rules_engine.report.evaluation_output(report) -> dict` | `rules-engine` | the **single-sourced equality projection** (`rule_results` rows + `recommendation` + `confidence` + reasons; **provenance excluded**) — reproducibility ×10 identity + bias-swap delta + per-rule coverage rows | Q3, QG-Fold-4 |
| `rules_engine.loader.RulebookLoader.load_rulebook(version).rules[].rule_id` | `rules-engine` | the rule-ID set the coverage report iterates, **at `manifest.rulebook_version`** | Q2, QG-Fold-2 |
| `rules_engine.report_schema.Recommendation` / `RuleResult` / `RuleStatus` | `rules-engine` | comparison values (`recommendation`, per-rule `status` PASS/FAIL/NOT_EVALUATED) | Q2/Q3/Q5 |
| `corpus_generator.records.CorpusRecord` / `CorpusManifest` | `corpus-generator` | the corpus shape `corpus_loader` deserializes / accepts; `manifest.rulebook_version` for coverage | Q1, QG-Fold-1/2 |
| `intake.schema.ApplicantProfile` / `Demographics` (+ enums) | `intake` | the profile + segregated demographics the bias-swap suite swaps via `model_copy` | Q5, QG-Fold-5 |
| `audit_store.replay_service.ReplayService` (pattern only) | `audit-store` | reference pattern — load + injected-`evaluate()` + compare `evaluation_output()`; **not re-implemented** | reference |

> **Reference-not-own (binding).** `quality-gates` **imports and calls** these shapes; it **re-implements none** (no local rule-eval, no hasher, no derivation, no second engine), **edits none**, and owns **no** rule-evaluation or enforcement logic. It is a **verification** unit — it asserts invariants hold; the *enforcement/definition* lives in `rules-engine` (financials-only rules) and `outlier-model` (demographic-excluded vector, P2). Mirrors audit-store's `ReplayService` reference-not-own posture toward `evaluate()`.

---

## 3. `CorpusLoader` — the tier-U/S-vs-tier-B seam (QG-Fold-1)

| Method | Shape | Meaning |
|---|---|---|
| `from_file(path) -> list[CorpusRecord]` | reads `corpus/profiles.json` (a JSON array of `CorpusRecord`) via `CorpusRecord.model_validate` — Decimal-as-string / date-ISO / enum-value all round-trip through the frozen schema | the **tier-B** real corpus path (only present after the out-of-band build; **not required for CI**) |
| `from_records(records) -> list[CorpusRecord]` | accepts an **in-memory** list (hand-crafted or corpus-generator's test-scoped factory) | the **tier-U/S** stub path used in CI |
| `profiles(records) -> list[ApplicantProfile]` | projects `record.profile` | the profile stream the gates consume |
| `manifest_version(manifest) -> str` | `manifest.rulebook_version` | the version the rule-coverage report loads the rulebook at (QG-Fold-2) |

**Boundary (QG-Fold-1):** the loader **never generates** a corpus (that is corpus-generator U14), **never re-calls Gemini**, and imposes **no hard Code-Gen dependency** on a committed `corpus/` — CI runs on the in-memory stub; the frozen file is consumed only when a tier-B corpus has been committed.

---

## 4. Evidence-record shapes (each gate's human-readable auditor artifact — Q7-A)

Each gate emits a **read-only, reproducible** evidence record (serialized human-readably — the auditor artifact of US-PLAT-3/4/5). These are `quality-gates`' **own output shapes** (frozen value objects; finalized at Code-Gen):

| Record | Key fields | Pass condition |
|---|---|---|
| **`BiasSwapReport`** | `profiles_tested` · `swaps` (list of `{application_id, swapped_fields, baseline_recommendation, swapped_recommendation}`) · `delta_count` · `passed` | **`delta_count == 0`** (any delta blocking) |
| **`ReproducibilityReport`** | `profiles_tested` · `runs` (= 10) · `mismatches` (list of `{application_id, run_index, projection_diff}`) · `reproducibility_pct` · `passed` | **`reproducibility_pct == 100`** (identical `evaluation_output()` all runs) |
| **`RuleCoverageReport`** | `rulebook_version` · `total_rules` · `covered_rule_ids` · `uncovered_rule_ids` · `coverage_pct` · `passed` | **`coverage_pct == 100`** (every rule definite PASS/FAIL; any uncovered blocking) |
| **`CoverageGateReport`** | `fail_under_configured` (the `pyproject` value) · `wiring_present` (bool) · `measured_pct` (optional, from the coverage data artifact) · `passed` | **`wiring_present and fail_under_configured >= 90`** (structural, QG-Fold-3); the % is **evidence**, not a second enforcement |

> **Determinism of the evidence (CON-DET-1 discipline):** every report is a pure function of `(corpus, rulebook, engine)` — no wall-clock, no unseeded randomness in the assertion path (a `generated_at` provenance stamp, if recorded, is never an input to a pass/fail). This is what makes the reports *reproducible* auditor evidence.

---

## 5. Boundary — what `quality-gates` does NOT own

- **No enforcement / definition of CON-BR1 or CON-DET-1** — enforcement lives in `rules-engine` (rules operate on financials only) + `outlier-model` (demographic-excluded feature vector, P2). `quality-gates` is the **one authority that asserts the invariant holds** (delta=0, blocking). One verification owner + defense-in-depth enforcement ≠ a split (unit-of-work.md §A.1 rule 4).
- **No re-own of memo-agent-core's structural CON-BR2** — `DecisionMemo` is already frozen / `MemoDraftOutput` is already recommendation-less; here CON-BR2 is exercised **via reproducibility** (the recommendation is the engine's, deterministic).
- **No corpus generation** — reads the frozen artifact / an in-memory stub only (corpus-generator U14 owns generation; `quality-gates` never re-calls Gemini).
- **No second coverage-enforcement mechanism** — binding `--cov-fail-under=90` stays in `pyproject` (QG-Fold-3).
- **No rule-eval / hasher / derivation re-implementation; no live LLM; no real PII; WIRE-1 untouched.**
- **Tier-B corpus run is a separate, later, out-of-band step — NOT authorized here and NOT a Code-Gen blocker.**
