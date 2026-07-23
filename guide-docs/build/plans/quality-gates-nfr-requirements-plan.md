# NFR Requirements Plan (Part 1) — `quality-gates` (U13)

**Phase / Stage**: BUILD → NFR Requirements, **Part 1 (Planning)** (plan-then-generate; numbered `[Answer]` tags to fill)
**Loop position**: `quality-gates` (U13) — FD ✅ **APPROVED (Continue)** → **NFR Requirements Part 1 ← here.**
**Unit**: U13 `quality-gates` · **Date**: 2026-07-08 · **Depth**: **COMPREHENSIVE** (confirmed) · **single verification authority** for CON-BR1 (bias-swap) / CON-BR2·AC-1 (reproducibility) / QA-3 (rule-coverage) / AC-5 (code-coverage) · Stories **US-PLAT-3/4/5/6**.
**Status**: **Four `[Answer]` tags FILLED (all A); ambiguity-check CLEAN (three named checks resolved as folds NFR-QG-Fold-1/2/3, §5A); Part 2 GENERATED** (`nfr-requirements.md` + `tech-stack-decisions.md`). This plan re-saved with the filled answers + resolved folds embedded (standing convention). STOPPED at the NFR-Requirements 2-option gate.

Built **ON** the frozen FD — **BR-QG-1..9**, the `domain-entities.md` module inventory (`corpus_loader` + `bias_swap_suite`/`reproducibility_suite`/`rule_coverage_report`/`coverage_gate`) + the four **evidence-record shapes** (`BiasSwapReport`/`ReproducibilityReport`/`RuleCoverageReport`/`CoverageGateReport`), the **`CorpusLoader` tier-U/S-vs-tier-B boundary**, the **seven locked plan answers (all A)**, and the **five QG-Folds** (`guide-docs/build/quality-gates/functional-design/` + `guide-docs/build/plans/quality-gates-functional-design-plan.md`) — **re-opening none**. Each **BR-QG-1..9** maps to one or more **pass/fail-testable `NFR-QG-*` targets** at an explicit **test tier**.

---

## 1. What NFR Requirements produces (Part 2 preview — NOT generated yet)
- `nfr-requirements.md` — the finalized `NFR-QG-*` targets (pass/fail assertions + acceptance criteria + tier + traceability to BR-QG-* + Security-Guardrails table).
- `tech-stack-decisions.md` — the test/verification substrate decisions (pytest, folds into the root run via `--cov=backend/quality_gates`; in-memory stub corpus + injected fake engines; no new dependency), each justified against a target.

## 2. Test tiers (explicit — per the established U/S/B convention)

| Tier | Meaning | Runs in CI? |
|---|---|---|
| **U — unit / seeded-deterministic** | pure, offline: each gate's **logic** exercised over a small **in-memory stub corpus** + a **controlled test rulebook**, with **injected fake engines** for the non-vacuous "teeth" cases; **no live LLM, no real 300+ corpus, no network** | **Yes** |
| **S — offline in-CI acceptance-shape smoke** | the gates run **end-to-end over the in-memory stub** through the real `CorpusLoader.from_records` path (no committed `corpus/` present) → asserts each gate produces a valid pass verdict + a well-formed evidence report on a clean stub | **Yes** |
| **B — real full-corpus acceptance run** *(external precondition — NOT a target of this unit's Code-Gen)* | the **real** acceptance runs (bias-swap delta=0 over the actual 300+ corpus, 100% rule coverage over the real rulebook) read the **committed frozen `corpus/profiles.json`** | **No (separate, later, out-of-band step; not authorized here)** |

> **Key tiering note (per the FD + the registered gap).** **None of `quality-gates`' own logic needs a tier-B target** — this unit **runs no LLM and generates no corpus**, so every one of its own behaviours (delta=0 detection, ×10 identity, uncovered-rule detection, wiring meta-assertion, evidence determinism, blocking form) is fully provable at **tier U/S** over the stub + injected fakes. **Tier-B is only the external precondition** for the *real* acceptance runs (which consume the frozen corpus once it is committed out-of-band) — it is **not** a testability precondition for this unit's Code-Gen and **not** a Code-Gen blocker. This is exactly QG-Fold-1 (`CorpusLoader`) + BR-QG-6.

---

## 3. BR-QG → draft `NFR-QG-*` target map (every rule mapped; no orphan)

| Target | BR | Draft pass/fail assertion | Tier | Rigor |
|---|---|---|---|---|
| **NFR-QG-BIAS-1** | BR-QG-1 | **delta=0 detection with teeth**: (a) **positive** — over the stub corpus, swapping `{full_name, gender, city}` on otherwise-identical profiles leaves `evaluate().recommendation` unchanged → `BiasSwapReport.delta_count == 0`, `passed`; (b) **non-vacuous** — an **injected fake "biased" engine** whose recommendation depends on a demographic field makes the suite detect **delta ≠ 0** and **fail** (proves the check is not always-passing). Injected fake ≠ editing `rules-engine` (reference-not-own). | U | full |
| **NFR-QG-PROXY-1** | BR-QG-2 | **proxy-attribution logic**: varying `occupation`/`income` on the stub changes the recommendation **only** in accordance with the **sanctioned rules** (occupation-risk / affordability) — attribution verified against `evaluation_output()` `rule_results` (the changed rule fired), never a demographic proxy; **`pincode` documented N/A** (asserted absent from `ApplicantProfile`/`Demographics`, not silently skipped). | U | full |
| **NFR-QG-REPRO-1** | BR-QG-3 | **×10 identity with teeth**: (a) **positive** — `evaluation_output(evaluate(p, v))` byte-identical across **10** runs per stub profile → `ReproducibilityReport.reproducibility_pct == 100`, `passed`; (b) **non-vacuous** — an **injected deliberately-non-deterministic fake engine** (e.g. output varies by run) makes the ×10 identity assertion **fail** (proves teeth). Uses the **imported `evaluation_output()`** projection (reference-not-own). Seeded-outlier clause deferred to P2 (documented, no target here). | U | full |
| **NFR-QG-RULECOV-1** | BR-QG-4 | **uncovered-rule detection with teeth**: over a **controlled test rulebook** (loaded via `RulebookLoader` at `manifest.rulebook_version`) with a **deliberately-unexercised rule**, `rule_coverage_report` reports that rule in `uncovered_rule_ids` and **fails** (`coverage_pct < 100`); with a stub that exercises **every** rule to a definite PASS/FAIL, it **passes** (`coverage_pct == 100`). | U | full |
| **NFR-QG-COVWIRE-1** | BR-QG-5 (i) | **structural wiring meta-assertion**: `coverage_gate`'s collected test reads `pyproject.toml` and asserts `--cov-fail-under` is **present** and its value **≥ 90** → `CoverageGateReport.wiring_present and fail_under_configured >= 90`; a fixture with the setting **absent or < 90** makes it **fail**. This is the **binding** gate's *wiring* check, not a re-enforcement. | U (structural) | full |
| **NFR-QG-COVEVID-1** | BR-QG-5 (ii) | **evidence-report generation (explicitly NOT the enforcer)**: the coverage **percentage evidence** (`CoverageGateReport.measured_pct`) is produced **separately** from the coverage data artifact — asserted as an informational, auditor-consumable report; **the target explicitly does not conflate** this with COVWIRE-1 or claim it enforces ≥90 (binding enforcement stays `pyproject`'s — QG-Fold-3). | U | full *(NFR-QG-Fold-3)* |
| **NFR-QG-LOADER-1** | BR-QG-6 | **CI passes with zero committed `corpus/`**: the full gate suite runs green through `CorpusLoader.from_records` (in-memory stub) with **no `corpus/profiles.json` present**; the `from_file` (tier-B) path is not required for CI. Proves the registered-gap accommodation — Code-Gen completes on the stub, no hard dependency on a committed corpus. | U/S | full |
| **NFR-QG-REFNOTOWN-1** | BR-QG-7 | **structural no-edit / no-local-reimplementation**: the consumed surfaces (`rules-engine` `evaluate`/`evaluation_output`/`RulebookLoader`, `corpus-generator` `CorpusRecord`/`CorpusManifest`, `intake` `ApplicantProfile`/`Demographics`, `audit-store` `ReplayService` pattern) are imported **call-only** and **none edited**; **no local** rule-eval, hasher, derivation, or second engine exists in `backend/quality_gates/`; the guard is **non-vacuous** (self-tested). No enforcement/definition of CON-BR1/CON-DET-1; no re-own of memo CON-BR2. | U (structural) | full |
| **NFR-QG-EVIDENCE-1** | BR-QG-8 | **evidence determinism + human-readability**: each gate's evidence record is a **pure function of `(corpus, rulebook, engine)`** — same inputs → **identical report** across two runs (Q3 chooses field-equality vs hash); any `generated_at`/provenance stamp is **excluded** from the equality (never a pass/fail input); the serialization is **human-readable**. | U | full |
| **NFR-QG-BLOCKING-1** | BR-QG-9 | **genuine blocking form**: each gate is a **collected pytest test** (not `skip`/`xfail`) that **fails the build** on a **deliberately-violating fixture** — bias delta≠0, a differing reproducibility run, an uncovered rule, or absent/`<90` coverage wiring each produce a real test failure; a structural check confirms the tests are collected in the root run. | U | full |

**No orphan** — BR-QG-1..9 each map to at least one `NFR-QG-*` target (BR-QG-1→BIAS-1, BR-QG-2→PROXY-1, BR-QG-3→REPRO-1, BR-QG-4→RULECOV-1, BR-QG-5→COVWIRE-1 + COVEVID-1, BR-QG-6→LOADER-1, BR-QG-7→REFNOTOWN-1, BR-QG-8→EVIDENCE-1, BR-QG-9→BLOCKING-1). Eleven targets total.

---

## 4. Clarifying questions (fill each `[Answer]` tag; last option = Other)

These decide **NFR-tier realization** — they do **not** re-open the FD, the BR-QG rules, the seven locked answers, or the five QG-Folds.

### Question 1 — Non-vacuous "teeth" construction for the assertion-firing gates (NFR-QG-BIAS-1 / REPRO-1 / RULECOV-1 / BLOCKING-1)
How do we prove each gate's assertion actually **fires on a genuine violation** (is not vacuously always-passing)?
A) **Paired positive/negative fixtures per gate**, driven by **injected fakes** (no production edit): bias — a stub *biased engine* whose recommendation depends on a demographic field → suite detects `delta ≠ 0`; reproducibility — a stub *non-deterministic engine* (output varies by run) → ×10 identity fails; rule-coverage — a **controlled test rulebook** with a rule the stub profiles never exercise → uncovered detected; blocking — a deliberately-violating fixture makes the **collected** test fail (asserted via `pytest.raises`/`AssertionError`/`report.passed is False`, and the test is not `skip`/`xfail`). The positive fixture proves the gate passes on clean input; the negative proves it has teeth. **Recommended.**
B) **Positive fixtures only** (assert the gate passes on clean input; trust the logic) — lighter, but risks a vacuous always-pass with no proof of teeth.
C) Other.

[Answer]: A

### Question 2 — The controlled test rulebook shape (NFR-QG-RULECOV-1, and the negative case of BLOCKING-1)
What rulebook does the rule-coverage **logic** test load?
A) A **small hand-authored test-scoped rulebook** (2–3 rules) loaded via `RulebookLoader` from a **fixture/temp path**, with **one rule deliberately left unexercised** by the stub profiles so uncovered-detection fires — **distinct from the production rulebook `1.0.0`** (keeps the logic test decoupled from the real 12-rule set; the real 100% assertion is the tier-B acceptance run). **Recommended.**
B) **Reuse the production rulebook `1.0.0`** (12 rules) and craft the stub corpus to leave exactly one rule uncovered — heavier, and couples the tier-U logic test to the production rulebook's contents.
C) Other.

[Answer]: A

### Question 3 — Evidence-report determinism assertion mechanism (NFR-QG-EVIDENCE-1)
How is "same inputs → identical report" asserted?
A) **Direct field-by-field equality** of the report value object across two runs on identical inputs (Pydantic model equality on the frozen report), with provenance/`generated_at` excluded from the compared fields; plus a light human-readability check (the report serializes to readable JSON). **No separate hash needed** — the reports are small structured objects. **Recommended.**
B) A **content-hash comparison** (canonical-serialize each report and compare digests), mirroring the corpus-generator/CANON-SER hashing pattern — heavier, introduces a hashing step this verification unit does not otherwise need.
C) Other.

[Answer]: A

### Question 4 — Test/verification substrate + coverage fold (tech-stack)
Confirm the substrate and how the tests count toward coverage.
A) **pytest** (the same runner as the nine completed backend units); the `quality_gates` tests **fold into the root pytest run** (`--cov=backend/quality_gates` joins `addopts`), joining the existing backend suite — **no new dependency, no separate runner**; the frontend Vitest suite is **untouched**; fixtures are **hand-crafted in-memory stubs + injected fakes** (Faker is available but not required — the stub corpus is tiny and controlled). QA-6 ≥90% applies to `backend/quality_gates`'s own code. **Recommended.**
B) A **separate test runner / new dependency** for the gate harness (e.g. a standalone report runner outside pytest) — diverges from the established convention.
C) Other.

[Answer]: A

---

## 5. Carried FD answers + folds (referenced, not re-derived — the substrate NFR builds on)

**Seven locked plan answers (all A):** Q1 injected `CorpusLoader` (frozen-file-or-in-memory; tier-U/S stub now, tier-B separate not a Code-Gen dep) · Q2 rule-coverage predicate = every `rule_id` definite PASS/FAIL, uncovered blocking · Q3 reproducibility = deterministic engine ×10 identical `evaluation_output()`, seeded-outlier deferred P2 · Q4 binding ≥90% stays in `pyproject`; `coverage_gate` = thin evidence + assertion · Q5 swap `{full_name, gender, city}`, proxy over occupation+income, `pincode` N/A · Q6 `backend/quality_gates/` · Q7 each gate = collected pytest test **and** auditor evidence report.

**Five QG-Folds:**
1. **QG-Fold-1** — `CorpusLoader` deserializes frozen `corpus/profiles.json` via `CorpusRecord.model_validate` **or** accepts in-memory; tier-U/S stub now, tier-B not a Code-Gen dep → drives **NFR-QG-LOADER-1**.
2. **QG-Fold-2** — rule-coverage loads the rulebook at `manifest.rulebook_version`, asserts each `rule_id` definite PASS/FAIL; tier-U logic on a controlled rulebook, real 100% at tier-B → drives **NFR-QG-RULECOV-1** (+ Q2 rulebook shape).
3. **QG-Fold-3** — a `coverage_gate` collected test cannot read the final coverage % mid-session, so its test is a **structural `--cov-fail-under=90` wiring meta-assertion** while the % is a **separate evidence report**; binding enforcement stays `pyproject`'s → **splits** into **NFR-QG-COVWIRE-1** + **NFR-QG-COVEVID-1** (explicitly not conflated).
4. **QG-Fold-4** — reproducibility + rule-coverage use the **imported `evaluation_output()`** projection (reference-not-own); seeded-outlier deferred P2 → drives **NFR-QG-REPRO-1 / REFNOTOWN-1**.
5. **QG-Fold-5** — demographic swap via `profile.model_copy(update={"demographics": ...})` (frozen-safe); swap-set `{full_name, gender, city}`; proxy over occupation+income; `pincode` N/A documented → drives **NFR-QG-BIAS-1 / PROXY-1**.

### 5A. Newly-resolved NFR-tier folds (ambiguity-check — three named checks CLEAN, no genuine gap, no STOP)

Ran against the four answers (all A) + the frozen FD, grounded on the actual frozen code on disk (`backend/audit_store/replay_service.py`, `backend/rules_engine/loader.py`). No user-facing decision the FD + answers don't determine. Three determinate realizations:

6. **NFR-QG-Fold-1 — injected-fake isolation** *(check i)*: the gates take an **injected engine** — the frozen `ReplayService.__init__(self, repository, engine)` pattern (verified on disk: `self._engine.evaluate(profile, version)`). The biased / non-deterministic fakes for BIAS-1/REPRO-1/BLOCKING-1 are **duck-typed test doubles** with their own `.evaluate()`; when a fake is injected the gate calls the **fake**, so the **real `rules-engine` `evaluate()` is never routed through** and **no `rules-engine` code is exercised or edited**. Structurally isolated — reference-not-own preserved.
7. **NFR-QG-Fold-2 — the loader validates the fixture** *(check ii)*: the test-scoped rulebook (Q2-A) is loaded via the **real `RulebookLoader.load_rulebook`**, whose Pydantic `Rulebook` schema is "the single structural gate" (verified on disk: `build_rulebook` raises `RulebookLoadError` on any schema violation, thresholds must be quoted strings, `input_fields` must be allowlisted, the file must declare its own version). A malformed fixture **fails to load** at test setup — so the fixture is a **legitimately-loadable input by construction**; **no separate/bespoke validation pass** is added (reuse of the real loader **is** the validation).
8. **NFR-QG-Fold-3 — COVEVID-1 rigor = full** *(check iii)*: evidence-report generation is **fully** pass/fail-testable via a **fixture coverage-data artifact** (assert the generator extracts `measured_pct` and produces a well-formed report); the % being **informational, not binding** (binding stays `pyproject`'s) is a **semantic note**, not a rigor downgrade. Rigor resolved from "soft/full" → **full** (§3 table updated) for consistency with the other targets' labels.

## 6. Settled items held (not re-opened)
The frozen FD (BR-QG-1..9, the module inventory + four evidence-record shapes, the `CorpusLoader` boundary, the seven answers, the five folds) is the substrate — NFR builds **pass/fail targets on** it. **Verification only** — no enforcement/definition of CON-BR1/CON-DET-1 (stays `rules-engine`/`outlier-model`); no re-own of memo's structural CON-BR2. **Reference-not-own** — the consumed surfaces call-only, none edited; no local rule-eval/hasher/derivation. **Registered corpus-gap honored** — every own-logic target is tier-U/S over the stub; **tier-B is an external precondition for the real acceptance runs, not a target of this unit's Code-Gen and not a Code-Gen blocker**; **the tier-B run is NOT authorized here**. **No LLM; no real PII; WIRE-1 untouched; no other unit started.**

## 7. Next step (STOP here — DONE)
Four answers filled (all A); ambiguity-check **CLEAN** (NFR-QG-Fold-1/2/3, §5A); **Part 2 GENERATED** — `guide-docs/build/quality-gates/nfr-requirements/nfr-requirements.md` (eleven `NFR-QG-*` targets + acceptance criteria + tier + traceability to BR-QG-1..9 + Security-Guardrails table) and `tech-stack-decisions.md` (D1–D12; pytest folding into the root run, injected engine/fakes, real `RulebookLoader` for the fixture, direct field-equality for report determinism, `tomllib` for the wiring meta-assert; **no new dependency**). This plan re-saved (standing convention). **STOPPED at the standardized NFR-Requirements 2-option gate (1. Request Changes / 2. Continue → NFR Design)** — did not advance. **WIRE-1 untouched; tier-B run NOT authorized; no other unit started.**
