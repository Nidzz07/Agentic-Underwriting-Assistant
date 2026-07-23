# Functional Design Plan (Part 1) — `quality-gates` (U13)

**Phase / Stage**: BUILD → Functional Design, **Part 1 (Planning)** (plan-then-generate; Q1–Q7 answered = all A, embedded below §7)
**Loop position**: `quality-gates` (U13) — **the tenth unit to enter the per-unit loop; the single verification authority for the four blocking gates.** FD ← here.
**Unit**: U13 `quality-gates` · **Date**: 2026-07-08 · **Depth**: **COMPREHENSIVE** (user-confirmed) · owns the four blocking gates · Stories **US-PLAT-3/4/5/6**.
**Status**: **Plan — Q1–Q7 answered (all A); ambiguity-check CLEAN (§8). NO FD artifact generated** (Part 2 generates the three FD artifacts on explicit go). STOP after this plan.

Built **ON** the frozen contracts (re-read, not re-derived): **rules-engine** (`RulesEngine.evaluate(profile, rulebook_version) -> RuleResultReport`, `Recommendation`, CON-DET-1, `report.evaluation_output()` projection, `RulebookLoader` + rulebook `1.0.0` [12 rules / 9 categories]); **audit-store** (`ReplayService` load+injected-`evaluate()`+compare-`evaluation_output()`, forensic fields excluded, reference-not-own); **corpus-generator** (`CorpusRecord {profile, documents_text, label, intended_class, edge_case_tags}`, `CorpusManifest`, the tier-B/tier-S distinction); **memo-agent-core** (CON-BR2-TYPE — `DecisionMemo` frozen, `recommendation`/`confidence` injected read-only); **intake** (`ApplicantProfile` frozen, `Demographics {full_name, gender, city}` — **no `pincode` field**) — **re-opening none.**

---

## 1. Scope / owns / builds-ON / boundary

- **Owns** (unit-of-work.md §U13): the four blocking gates as ONE CI/pytest harness — `bias-swap-suite` (delta=0), `reproducibility-suite` (100%, ×10), `rule-coverage-report` (100% of rules), `coverage-gate` (≥90%, binding). **Single verification authority** for CON-BR1 (bias-swap), CON-BR2/AC-1 (reproducibility), QA-3 (rule coverage), AC-5 (code coverage).
- **Builds ON** (call-only / reference-not-own): rules-engine `evaluate`/`evaluation_output`/`RulebookLoader`; corpus-generator `CorpusRecord`/`CorpusManifest` (via a corpus-source abstraction); intake `ApplicantProfile`/`Demographics` (for demographic swaps); audit-store `ReplayService` (pattern reference — mirrors the `evaluation_output()` equality projection); memo-agent-core CON-BR2 boundary.
- **Boundary — verification only, NOT enforcement/definition**:
  - Does **not** enforce or re-define CON-BR1 / CON-DET-1 — enforcement lives in `rules-engine` (financials-only rules) + `outlier-model` (demographic-excluded feature vector, P2); `quality-gates` is the **one authority that asserts the invariant holds** (delta=0, blocking). One verification owner + defense-in-depth enforcement ≠ a split (unit-of-work.md §A.1 rule 4).
  - Does **not** re-own memo-agent-core's structural CON-BR2 (already `DecisionMemo`-frozen / `MemoDraftOutput`-unrepresentable); here CON-BR2 is exercised **via reproducibility** (US-PLAT-4 traces CON-BR2 — the recommendation is the engine's, deterministic).
  - Does **not** own corpus generation (corpus-generator U14); reads the frozen artifact / a test-scoped stub only.
  - Does **not** re-implement rule evaluation / hashing / derivation — delegates to rules-engine (reference-not-own).

---

## 2. Dependency ledger (call-only / reference-not-own — none edited)

| Consumed surface | From unit | Used for |
|---|---|---|
| `rules_engine.engine.RulesEngine.evaluate(profile, rulebook_version)` + `report_schema.Recommendation`/`RuleResult`/`RuleResultReport` | `rules-engine` | the deterministic engine under verification (reproducibility, bias-swap, rule-coverage) |
| `rules_engine.report.evaluation_output(report) -> dict` | `rules-engine` | the **single-sourced equality projection** (same one ReplayService uses) — reproducibility ×10 identity + per-rule coverage rows |
| `rules_engine.loader.RulebookLoader.load_rulebook(version).rules[].rule_id` | `rules-engine` | the rule-ID set the rule-coverage report iterates (at the corpus's `manifest.rulebook_version`) |
| `corpus_generator.records.CorpusRecord` / `CorpusManifest` | `corpus-generator` | the corpus shape the `CorpusLoader` deserializes / accepts (call-only import) |
| `intake.schema.ApplicantProfile` / `Demographics` (+ enums) | `intake` | the profile + segregated demographics the bias-swap suite swaps via `model_copy` |
| `audit-store.ReplayService` (pattern only) | `audit-store` | reference pattern — load + injected-`evaluate()` + compare `evaluation_output()`; **not necessarily imported** |

> **Reference-not-own (binding).** `quality-gates` imports/calls these surfaces and re-implements **none**; it edits **none**; it owns **no** rule-evaluation/hashing/derivation logic. It is a **verification** unit.

---

## 3. The four gates → assertion · traces · tier

| Gate (module) | Assertion | Traces | Tier |
|---|---|---|---|
| **`bias_swap_suite`** | swap `{full_name, gender, city}` on an otherwise-identical profile → engine `recommendation` **unchanged**; **delta=0, any delta blocking**. Proxy check over `occupation`+`income` (may differ **only** via their sanctioned rules — occupation-risk / affordability); `pincode` **N/A** (no field, documented). **Single verification authority for CON-BR1.** | NFR-BIAS-1, QA-2, CON-BR1, AC-3, FR-PROV-GATE-1 · US-PLAT-3 | U/S (logic + stub) · **B** (real corpus, out-of-band) |
| **`reproducibility_suite`** | `evaluate(profile, rulebook_version)` **×10** per profile → **identical `evaluation_output()` projection** each run (engine-deterministic, NOT LLM memo wording); **100%**. Seeded-outlier determinism clause **deferred to `outlier-model` (P2)** (documented, not dropped). | NFR-REPRO-1, QA-1, AC-1, CON-BR2, FR-PROV-GATE-1 · US-PLAT-4 | U/S (+**B**) |
| **`rule_coverage_report`** | every `rule_id` in the loaded rulebook (at `manifest.rulebook_version`) reaches a **definite PASS or FAIL** (not `not_evaluated`) in ≥1 corpus record; **100%**, any never-definitively-evaluated rule is a **blocking** failure. | QA-3, AC-4 · US-PLAT-5 | U/S (logic on a controlled small rulebook+profiles) · **B** (real 100% over the actual rulebook) |
| **`coverage_gate`** | binding **≥90%** enforcement **stays in `pyproject --cov-fail-under=90`** (proven across 9 units); `coverage_gate.py` is a **thin evidence/report + wiring meta-assertion** (asserts the pyproject gate is wired at ≥90 — a *collected structural test*, since live coverage % is unavailable mid-session) + emits the % evidence artifact from the coverage data. | AC-5, QA-6 · US-PLAT-6 | U (wiring meta-assert) + report |

**Gate output form (Q7-A):** each gate is **both** a **collected pytest test** (blocking: delta≠0 / any run differs / any uncovered rule / coverage<90 fails the build) **and** emits a **human-readable auditor evidence report** (US-PLAT-3/4/5 "viewable by the auditor as a read-only artifact"). (For `coverage_gate` the blocking-in-CI part is pyproject's `--cov-fail-under`; its collected test is the wiring meta-assertion — QG-Fold-3.)

---

## 4. Registered corpus-gap accommodation (explicit — the just-registered constraint)

- The bias-swap / reproducibility / rule-coverage gates operate over **applicant profiles**. Per **Q1-A**, they take an injected **`CorpusLoader`** source: it reads the frozen `corpus/profiles.json` (`CorpusRecord` round-trip via `model_validate`) **when present**, and accepts an **in-memory `CorpusRecord`/profile list** for tests.
- **Tier-U/S (CI, now):** every gate's **logic** is designed + tested over a **small test-scoped corpus stub** (hand-crafted profiles or corpus-generator's own test-scoped factory) + a controlled rulebook — asserting the gate mechanics (delta=0 detection, ×10 identity, uncovered-rule detection) **without** the real 300+ corpus.
- **Tier-B (later, out-of-band, NOT CI):** the real acceptance runs (bias-swap delta=0 over the actual 300+ corpus, 100% rule coverage over the real rulebook) read the **committed tier-B artifact**. This is a **separate later explicit step** (real `GEMINI_API_KEY`, never CI), **NOT a Code-Gen blocker** — exactly as the Deferred Decisions register records.
- **No hard Code-Gen dependency on the committed corpus**: `quality-gates` Code-Gen completes + passes CI on the tier-U/S stub; the tier-B corpus run is authorized separately.

---

## 5. Draft business rules (BR-QG-* — finalized in Part 2, not frozen here)

- **BR-QG-1** — Bias-swap invariance: `{full_name, gender, city}` swap → recommendation unchanged; **delta=0 blocking** (CON-BR1 single verification authority).
- **BR-QG-2** — Proxy-variable check: `occupation`/`income` differ only via their sanctioned rules; `pincode` N/A (no field).
- **BR-QG-3** — Reproducibility: `evaluate()` ×10 → identical `evaluation_output()`; 100%; engine-deterministic; seeded-outlier deferred to P2.
- **BR-QG-4** — Rule-coverage: every rule_id definitely PASS/FAIL in ≥1 record over the corpus; uncovered = blocking.
- **BR-QG-5** — Code-coverage gate: binding ≥90% stays in `pyproject`; `coverage_gate` = thin evidence + wiring meta-assertion.
- **BR-QG-6** — Corpus-source abstraction: `CorpusLoader` (frozen file or in-memory); tier-U/S stub now, tier-B real run separate (not a Code-Gen dep).
- **BR-QG-7** — Reference-not-own / verification-only: the five surfaces call-only, none edited; no rule-eval/hasher/derivation re-implemented; no CON-BR1/CON-DET-1 *enforcement* (that stays rules-engine/outlier-model).
- **BR-QG-8** — Auditor evidence: each gate emits a human-readable read-only report artifact.
- **BR-QG-9** — Blocking form: each gate is a collected pytest test that fails the build on violation (coverage-gate via the pyproject `--cov-fail-under` + wiring meta-assert).

---

## 6. Planned Part-2 structure (the three FD artifacts — generated on explicit go)

- **`domain-entities.md`** — the module inventory (`bias_swap_suite`, `reproducibility_suite`, `rule_coverage_report`, `coverage_gate`, `corpus_loader`) + the consumed frozen shapes (rules-engine `evaluate`/`evaluation_output`/`RulebookLoader`, corpus-generator `CorpusRecord`/`CorpusManifest`, intake `ApplicantProfile`/`Demographics`) + report-artifact shapes (bias-swap / reproducibility / rule-coverage evidence records) + the `CorpusLoader` boundary.
- **`business-rules.md`** — BR-QG-1..9 finalized + a rule index + the Security-Guardrails compliance table.
- **`business-logic-model.md`** — the verification flow (load corpus → per-gate assertion → blocking test + evidence artifact) with a 7-rule-validated Mermaid + text alternative, the tier-U/S-vs-tier-B boundary, the single-verification-authority-vs-enforcement boundary, a consumer/dependency map, and an invariant self-check.

**Proposed package (Q6-A):** `backend/quality_gates/` (realized per-unit convention) with `bias_swap_suite.py` / `reproducibility_suite.py` / `rule_coverage_report.py` / `coverage_gate.py` / `corpus_loader.py` + `tests/`; folds into the root pytest run (`--cov=backend/quality_gates`) at NFR/Code-Gen. Auditor report artifacts under a reports output path (exact path a Code-Gen detail). *(The older `unit-of-work.md` tree wrote `backend/quality/`; Q6-A supersedes to the realized underscore convention.)* **Flagged for gate confirmation at the FD completion gate.**

---

## 7. Clarifying questions — ANSWERED (all A; standing convention: full text + answers on disk)

### Q1 — Corpus-source abstraction (the registered gap)
How do the gates obtain profiles given the real corpus exists only after the out-of-band tier-B build?
A) Suites take an injected corpus **source** (`CorpusLoader`) that reads frozen `corpus/profiles.json` when present and accepts an in-memory `CorpusRecord`/profile list for tests; tier-U/S runs every gate's logic over a small test-scoped stub, the real tier-B corpus run is a separate out-of-band step (not a Code-Gen hard dependency). **Recommended.**
B) Read `corpus/profiles.json` directly (hard dep on the committed artifact). C) Other.

[Answer]: A

### Q2 — Rule-coverage predicate (US-PLAT-5 / QA-3)
What does "every rule exercised" mean?
A) Every `rule_id` in the loaded rulebook must reach a **definite PASS or FAIL** (not `not_evaluated`) in ≥1 record over the corpus; any never-definitively-evaluated rule is a blocking failure. **Recommended.**
B) Two-sided — every rule observed **both** PASS and FAIL. C) Weaker — rule merely appears (incl. `not_evaluated`). D) Other.

[Answer]: A

### Q3 — Reproducibility scope in Phase 1 (US-PLAT-4 / AC-1 / CON-BR2 / NFR-REPRO-1)
What is asserted, and over what?
A) Assert the **deterministic engine output**: `evaluate()` **×10** per profile → identical `evaluation_output()` projection each run (the ReplayService projection, reference-not-own); the **seeded-outlier** determinism clause is **deferred to when `outlier-model` (P2) lands** (documented). **Recommended.**
B) Full-pipeline (intake→rules→memo) reproducibility now. C) Other.

[Answer]: A

### Q4 — Code-coverage gate vs the existing `pyproject --cov-fail-under=90`
Where does the binding enforcement live?
A) Binding enforcement **stays in `pyproject.toml`** (already proven across 9 units); `coverage_gate.py` is a **thin evidence/report + assertion** layer producing the auditor artifact, not a second enforcement mechanism. **Recommended.**
B) `coverage_gate.py` independently re-runs/owns enforcement (duplicates pyproject). C) Other.

[Answer]: A

### Q5 — Bias-swap swap-set + proxy check vs the actual `Demographics` schema (US-PLAT-3 / CON-BR1)
Which fields are swapped, and how is `pincode` handled?
A) Swap the **three present demographic fields** (`full_name`, `gender`, `city`) → assert engine `recommendation` unchanged (delta=0, blocking); proxy check over `occupation`+`income` (may differ only via their sanctioned rules); **`pincode` is N/A** — no such field on `ApplicantProfile` (documented, not silently skipped). **Recommended.**
B) Add a `pincode`/location proxy beyond `city` (needs a nonexistent schema field). C) Other.

[Answer]: A

### Q6 — Package name / location
A) `backend/quality_gates/` (realized per-unit convention, matching `corpus_generator`/`secrets_config`); folds into the root pytest run (`--cov=backend/quality_gates`). **Recommended.**
B) `backend/quality/` (per the older unit-of-work.md tree). C) Other.

[Answer]: A

### Q7 — Gate output form ("runs in CI" + "auditor read-only artifact")
A) **Both** — each gate is a **collected pytest test** (blocking) **and** emits a **human-readable report artifact** (auditor evidence). **Recommended.**
B) Report scripts only (not collected tests). C) Other.

[Answer]: A

---

## 8. Ambiguity-check result — CLEAN (five realization clarity-folds; no genuine gap, no STOP)

Ran against the seven answers + the frozen contracts (rules-engine `evaluate`/`evaluation_output` [verified: `evaluation_output(report) -> dict` projecting rule_results/recommendation/confidence/reasons, provenance excluded]/`RulebookLoader`; audit-store `ReplayService`; corpus-generator `CorpusRecord`/`CorpusManifest`; memo CON-BR2-TYPE; intake `ApplicantProfile`/`Demographics` [no `pincode`]). **No genuine gap** — no user-facing decision the contracts + answers don't determine. Five determinate realizations (none re-opens a frozen artifact):

- **QG-Fold-1 (Q1)** — `CorpusLoader` deserializes frozen `corpus/profiles.json` via `CorpusRecord.model_validate` (Decimal-as-string / date-ISO / enum-value all round-trip through the frozen schema) **or** accepts an in-memory list; tier-U/S over a small stub; real corpus tier-B (not a Code-Gen dep). corpus-generator `CorpusRecord`/`CorpusManifest` imported call-only.
- **QG-Fold-2 (Q2)** — the rule-coverage report loads the rulebook via `RulebookLoader` at **`manifest.rulebook_version`** (the version the corpus was labeled against), iterates `evaluate()` over the corpus, and asserts each `rule_id` reaches a definite PASS/FAIL; tier-U tests the LOGIC on a controlled small rulebook+profiles (known covered/uncovered), the real 100% assertion at tier-B.
- **QG-Fold-3 (Q4/Q7)** — a `coverage_gate` **collected pytest test cannot read the final coverage % mid-session**, so its test is a **structural wiring meta-assertion** (`pyproject --cov-fail-under=90` present + ≥90); the % **evidence** is a report from the coverage data artifact; **binding enforcement stays pyproject's** (reconciles Q4-A + Q7-A). The other three gates' collected tests assert their invariant directly over the tier-U/S corpus.
- **QG-Fold-4 (Q3)** — reproducibility + rule-coverage use rules-engine's imported `evaluation_output()` projection (reference-not-own — the same ReplayService uses); the seeded-outlier determinism clause is **deferred to P2** (documented, not dropped).
- **QG-Fold-5 (Q5)** — demographic swap via `profile.model_copy(update={"demographics": Demographics(...)})` (frozen-safe); swap-set `{full_name, gender, city}`; proxy check over `occupation`+`income` (any recommendation change attributable only to the sanctioned occupation-risk / affordability rules); `pincode` documented N/A (not a schema field).

---

## 9. Holds (binding through FD)
- **Verification only** — no enforcement/definition of CON-BR1/CON-DET-1 (stays rules-engine/outlier-model); no re-own of memo's structural CON-BR2.
- **Reference-not-own** — the five surfaces call-only, none edited; no local rule-eval/hasher/derivation.
- **Registered corpus-gap honored** — gates tier-U/S-testable now via `CorpusLoader`; the real tier-B corpus run is a separate later out-of-band step, **not a Code-Gen blocker**; **I have not authorized the tier-B run**.
- **WIRE-1 untouched**; no other unit started; no FD artifact generated at this plan stage.

## 10. Next step (STOP here)
Review this plan file. On your go I run **Part 2** — generate the three FD artifacts (`guide-docs/build/quality-gates/functional-design/{domain-entities,business-rules,business-logic-model}.md`) built exactly on the seven answers + five QG-Folds (re-opening none), then present the standardized FD 2-option completion gate. **No FD artifact is generated until you approve this plan.** WIRE-1 stays untouched; no other unit started.
