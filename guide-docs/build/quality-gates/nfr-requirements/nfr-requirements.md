# NFR Requirements — `quality-gates` (U13)

**Stage**: BUILD → NFR Requirements (per-unit) · the four blocking verification gates · **Depth**: **COMPREHENSIVE**
**Unit**: U13 `quality-gates` · **Date**: 2026-07-08 · **single verification authority** for CON-BR1 (bias-swap) / CON-BR2·AC-1 (reproducibility) / QA-3 (rule-coverage) / AC-5 (code-coverage) · Stories **US-PLAT-3/4/5/6**.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-QG-1..9**, the module inventory + the **four evidence-record shapes** `BiasSwapReport`/`ReproducibilityReport`/`RuleCoverageReport`/`CoverageGateReport`, the **`CorpusLoader` tier-U/S-vs-tier-B boundary**, the **seven locked plan answers (all A)**, the **five QG-Folds**) — **re-opening none**. Each `NFR-QG-*` target is a **pass/fail testable assertion** traced to its BR-QG rule. Four NFR-tier answers (all **A**) + three resolved folds (NFR-QG-Fold-1/2/3) locked in the plan.

---

## 0. Central testability principle (tiers + folds)

`quality-gates` is verified across two of the three project tiers — **its own logic never needs tier-B**:
- **U — unit / seeded-deterministic** (CI): each gate's **logic** over a small **in-memory stub corpus** + a **controlled test rulebook**, with **injected fake engines** for the non-vacuous "teeth" cases. This is where every gate proves out.
- **S — offline in-CI acceptance-shape smoke** (CI): the gates run end-to-end over the stub through the real `CorpusLoader.from_records` path with **no committed `corpus/` present** → each gate produces a valid pass verdict + a well-formed evidence report on a clean stub.
- **B — real full-corpus acceptance run** *(external precondition, NOT a target of this unit's Code-Gen)*: the real bias-swap-delta=0 / 100%-rule-coverage runs over the committed frozen `corpus/profiles.json`; a **separate, later, out-of-band step — not authorized here, not a Code-Gen blocker**.

> **Why no own-logic tier-B target.** `quality-gates` **runs no LLM and generates no corpus**, so every own behaviour (delta=0 detection, ×10 identity, uncovered-rule detection, wiring meta-assertion, evidence determinism, blocking form) is fully provable at tier U/S over the stub + injected fakes (QG-Fold-1 / BR-QG-6). Tier-B is where the *real corpus* is consumed once committed — an external precondition, not a testability precondition.

**Folds preserved (FD):** QG-Fold-1 (`CorpusLoader` frozen-file-or-in-memory), QG-Fold-2 (rule-coverage at `manifest.rulebook_version`, definite PASS/FAIL), QG-Fold-3 (`coverage_gate` = structural wiring meta-assertion + separate % evidence, binding stays `pyproject`'s), QG-Fold-4 (imported `evaluation_output()` reference-not-own; outlier deferred P2), QG-Fold-5 (`model_copy` demographic swap `{full_name, gender, city}`, proxy over occupation+income, `pincode` N/A).

**New NFR-tier folds (ambiguity-check resolutions, §5 of the plan):**
- **NFR-QG-Fold-1 — injected-fake isolation** (check i): the gates accept an **injected engine** (the frozen `ReplayService(__init__(self, repository, engine))` pattern — `self._engine.evaluate(...)`). The biased / non-deterministic fakes are **duck-typed test doubles** with their own `.evaluate()`; when a fake is injected, the gate calls the **fake**, so the real `rules-engine` `evaluate()` is **never routed through**. Structurally isolated — no production code exercised, no `rules-engine` edit.
- **NFR-QG-Fold-2 — the loader validates the fixture** (check ii): the test-scoped rulebook is loaded via the **real `RulebookLoader.load_rulebook`**, whose Pydantic `Rulebook` schema is "the single structural gate" — a malformed/invalid fixture **fails to load** (`RulebookLoadError`) and never reaches evaluate. So the fixture is a **legitimately-loadable input by construction** (thresholds quoted-as-strings, `input_fields` in the financial/medical/lifestyle allowlist); **no bespoke/extra validation pass** is added — reuse of the real loader **is** the validation.
- **NFR-QG-Fold-3 — COVEVID-1 rigor = full** (check iii): evidence-report generation is **fully** pass/fail-testable via a **fixture coverage-data artifact** (assert the generator extracts `measured_pct` and produces a well-formed report); the % being **informational, not binding** (binding stays `pyproject`'s) is a semantic note, **not** a rigor downgrade. Rigor resolved from "soft/full" → **full**.

---

## 1. Finalized `NFR-QG-*` targets (pass/fail; tier stated)

### FULL RIGOR — invariant / acceptance-criteria-bearing

#### NFR-QG-BIAS-1 — bias-swap delta=0 detection, with teeth (BR-QG-1; QG-Fold-5, NFR-QG-Fold-1)
- **Assertion**: the bias-swap suite passes iff swapping `{full_name, gender, city}` (via `ApplicantProfile.model_copy(update={"demographics": ...})`) on otherwise-identical profiles leaves the engine `recommendation` unchanged (**delta = 0**); any delta is a blocking failure.
- **Acceptance criteria**: (a) **positive** — over the stub corpus with the **real** engine, `BiasSwapReport.delta_count == 0` and `passed is True`; (b) **non-vacuous (teeth)** — an **injected fake "biased" engine** whose recommendation depends on a demographic field yields `delta_count > 0` and `passed is False` (proves the suite is not always-passing); (c) the fake is a **duck-typed double** (NFR-QG-Fold-1) — with it injected the **real `evaluate()` is never called**, and no `rules-engine` code is edited.
- **Tier**: **U**.

#### NFR-QG-PROXY-1 — proxy attribution to sanctioned rules only; pincode N/A (BR-QG-2; QG-Fold-5)
- **Assertion**: varying `occupation` / `income` changes the recommendation **only** through the sanctioned rules (occupation-risk / affordability), never as a demographic proxy; `pincode` is documented **N/A**.
- **Acceptance criteria**: (a) varying `occupation`/`income` on the stub and inspecting `evaluation_output()` `rule_results`, any recommendation change corresponds to the **sanctioned rule** firing (the changed rule appears with the expected status); (b) a demographic swap alone (BIAS-1) leaves the recommendation unchanged — no proxy leakage; (c) **`pincode` is asserted absent** from `ApplicantProfile`/`Demographics` (documented N/A, not silently skipped).
- **Tier**: **U**.

#### NFR-QG-REPRO-1 — reproducibility ×10 identical projection, with teeth (BR-QG-3; QG-Fold-4, NFR-QG-Fold-1)
- **Assertion**: the reproducibility suite passes iff `evaluation_output(evaluate(p, v))` is **identical across 10 runs** per profile (`reproducibility_pct == 100`), asserted on the **deterministic engine output**, not LLM wording.
- **Acceptance criteria**: (a) **positive** — over the stub with the real engine, `ReproducibilityReport.reproducibility_pct == 100` and `passed is True` (identical projection all 10 runs); (b) **non-vacuous (teeth)** — an **injected non-deterministic fake engine** (output varies by run) makes the ×10 identity assertion **fail** (`reproducibility_pct < 100`, `passed is False`); (c) the projection is the **imported `evaluation_output()`** (reference-not-own — the same ReplayService uses); (d) the **seeded-outlier** determinism clause is **deferred to `outlier-model` (P2)** — documented, no target here.
- **Tier**: **U**.

#### NFR-QG-RULECOV-1 — uncovered-rule detection, with teeth (BR-QG-4; QG-Fold-2, NFR-QG-Fold-2)
- **Assertion**: the rule-coverage report passes iff **every** `rule_id` in the loaded rulebook (via `RulebookLoader.load_rulebook(manifest.rulebook_version)`) reaches a **definite PASS or FAIL** (not `NOT_EVALUATED`) in ≥1 corpus record (`coverage_pct == 100`); any uncovered rule is blocking.
- **Acceptance criteria**: (a) **negative (teeth)** — over a **controlled test-scoped rulebook** (2–3 rules, loaded via the **real `RulebookLoader`** from a fixture path — NFR-QG-Fold-2) with **one rule deliberately unexercised** by the stub profiles, the report lists it in `uncovered_rule_ids` and `passed is False` (`coverage_pct < 100`); (b) **positive** — a stub that exercises **every** rule to a definite PASS/FAIL → `coverage_pct == 100`, `passed is True`; (c) the rulebook is loaded at `manifest.rulebook_version` (QG-Fold-2); the fixture is **distinct from the production `1.0.0`** and is validated **by the loader itself** (NFR-QG-Fold-2).
- **Tier**: **U**.

#### NFR-QG-COVWIRE-1 — coverage-gate structural wiring meta-assertion (BR-QG-5 i; QG-Fold-3)
- **Assertion**: `coverage_gate`'s collected test asserts the **binding** coverage wiring is present — `pyproject.toml` `addopts` contains `--cov-fail-under` with value **≥ 90**.
- **Acceptance criteria**: (a) reading the real `pyproject.toml`, `CoverageGateReport.wiring_present is True` and `fail_under_configured >= 90` → `passed is True`; (b) **teeth** — a fixture `pyproject` with the setting **absent** or **< 90** → `passed is False`; (c) this is the **wiring** check for the binding gate, **not** a re-enforcement (binding stays `pyproject`'s `--cov-fail-under`).
- **Tier**: **U (structural)**.

#### NFR-QG-COVEVID-1 — coverage %-evidence report, generated separately (BR-QG-5 ii; QG-Fold-3, NFR-QG-Fold-3)
- **Assertion**: the coverage **percentage evidence** (`CoverageGateReport.measured_pct`) is produced **separately** from the coverage data artifact — an informational, auditor-consumable report — and is **not conflated** with COVWIRE-1 nor claimed to enforce ≥90.
- **Acceptance criteria**: (a) given a **fixture coverage-data artifact** (e.g. a `coverage.json`/`.coverage` sample), the evidence generator extracts and formats `measured_pct` into a well-formed `CoverageGateReport` (NFR-QG-Fold-3 — fully testable); (b) the report explicitly marks `measured_pct` **informational** (binding enforcement stays `pyproject`'s); (c) the evidence path and the COVWIRE-1 meta-assertion are **distinct code paths** (no conflation).
- **Tier**: **U**.

#### NFR-QG-LOADER-1 — CI green with zero committed `corpus/` (BR-QG-6; QG-Fold-1)
- **Assertion**: the full gate suite runs green through `CorpusLoader.from_records` (in-memory stub) with **no `corpus/profiles.json` present**; the `from_file` (tier-B) path is not required for CI.
- **Acceptance criteria**: (a) the gates accept an **injected corpus source**; the suite passes on the in-memory stub with **no committed `corpus/`**; (b) `CorpusLoader.from_file` is exercised only when a tier-B corpus exists (its absence does not fail CI); (c) proves the registered-gap accommodation — Code-Gen completes on the stub, **no hard dependency** on a committed corpus.
- **Tier**: **U/S**.

#### NFR-QG-REFNOTOWN-1 — verification-only; reference-not-own; no local re-implementation (BR-QG-7; QG-Fold-4)
- **Assertion**: the consumed surfaces (`rules-engine` `evaluate`/`evaluation_output`/`RulebookLoader`, `corpus-generator` `CorpusRecord`/`CorpusManifest`, `intake` `ApplicantProfile`/`Demographics`, `audit-store` `ReplayService` pattern) are imported **call-only** and **none edited**; `backend/quality_gates/` defines **no local** rule-eval, hasher, derivation, or second engine, and **no** enforcement/definition of CON-BR1/CON-DET-1, no re-own of memo CON-BR2.
- **Acceptance criteria**: (a) a **structural** test — the unit imports those surfaces but contains **no** local `hashlib`/SHA, **no** local age/BMI derivation, **no** rule evaluation, **no** second engine implementation; (b) **non-vacuous self-test** — a synthetic local re-implementation (a local `evaluate`/hasher) is flagged by the guard; (c) a **no-edit** check confirms no production file of a consumed unit is modified by this unit.
- **Tier**: **U (structural)**.

#### NFR-QG-EVIDENCE-1 — evidence-report determinism + human-readability (BR-QG-8; NFR-QG-Fold-3, Q3)
- **Assertion**: each gate's evidence record is a **pure function of `(corpus, rulebook, engine)`** — same inputs → **identical** report — and is **human-readable**.
- **Acceptance criteria**: (a) running a gate twice on identical inputs yields **field-by-field-equal** report value objects (Pydantic model equality — Q3-A), with any `generated_at`/provenance stamp **excluded** from the compared fields (never a pass/fail input); (b) a **light human-readability** check — the report serializes to readable JSON with the documented fields; (c) **no content-hash step** is introduced (the reports are small structured objects — Q3-A).
- **Tier**: **U**.

#### NFR-QG-BLOCKING-1 — genuine blocking pytest form (BR-QG-9; NFR-QG-Fold-1)
- **Assertion**: each gate is a **collected pytest test** (not `skip`/`xfail`) that **fails the build** on a **deliberately-violating fixture**.
- **Acceptance criteria**: (a) for each gate, a **violating fixture** (bias delta≠0 via the biased fake, a differing reproducibility run via the non-deterministic fake, an uncovered rule via the controlled rulebook, absent/`<90` coverage wiring) produces a **real test failure** (`AssertionError`/`pytest.raises`/`report.passed is False`); (b) a **structural** check confirms the gate tests are **collected** in the root pytest run and are **not** marked `skip`/`xfail`; (c) the coverage-gate's live-% enforcement remains `pyproject`'s `--cov-fail-under` (QG-Fold-3), while its collected test is the wiring meta-assertion.
- **Tier**: **U**.

---

## 2. Traceability (target → BR-QG → tier → rigor)

| Target | BR-QG | Tier | Rigor |
|---|---|---|---|
| NFR-QG-BIAS-1 | 1 | U | full |
| NFR-QG-PROXY-1 | 2 | U | full |
| NFR-QG-REPRO-1 | 3 | U | full |
| NFR-QG-RULECOV-1 | 4 | U | full |
| NFR-QG-COVWIRE-1 | 5 (i) | U (structural) | full |
| NFR-QG-COVEVID-1 | 5 (ii) | U | full *(NFR-QG-Fold-3)* |
| NFR-QG-LOADER-1 | 6 | U/S | full |
| NFR-QG-REFNOTOWN-1 | 7 | U (structural) | full |
| NFR-QG-EVIDENCE-1 | 8 | U | full |
| NFR-QG-BLOCKING-1 | 9 | U | full |

**No orphan** — BR-QG-1..9 each map to a target (BR-QG-5 splits into COVWIRE-1 + COVEVID-1). Eleven targets, all tier-U/S; **no own-logic tier-B target** (§0).

---

## 3. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | The unit reads already-validated frozen/stub `ApplicantProfile`s (Pydantic-valid by construction at intake/corpus-generator); it validates no new application input. |
| Prompt-injection defense | **N/A** | No LLM is invoked — the gates verify the **deterministic engine**; no untrusted document is parsed (SEC-1 is `document-sanitizer`'s). |
| Secrets management | **N/A** | No provider key is read (no LLM path); the tier-B corpus is consumed as committed data, never regenerated (no `GEMINI_API_KEY`). |
| Read-only DB access for audit role | **N/A** | The unit reads the frozen `corpus/` artifact / in-memory stub, not the audit DB. |
| Audit logging | **N/A (produces evidence)** | The gate **evidence reports** are auditor-consumable artifacts (US-PLAT-3/4/5); this is not the runtime audit trail (SEC-5 is `audit-store`'s). |
| **No real PII / synthetic-only** | **Compliant (referenced)** | All profiles are synthetic (corpus-generator BR-CORP-10); the stub is hand-crafted synthetic; `quality-gates` introduces no real PII. |

No blocking finding.

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-QG-1..9, the module inventory + four evidence-record shapes, the `CorpusLoader` boundary, the seven locked answers, the five QG-Folds) is the substrate — NFR builds pass/fail targets **on** it.
- **Verification only** — no enforcement/definition of CON-BR1/CON-DET-1 (stays `rules-engine`/`outlier-model`); no re-own of memo's structural CON-BR2. **Reference-not-own** — surfaces call-only, none edited; injected fakes are duck-typed doubles (NFR-QG-Fold-1), never routed through real `evaluate()`.
- **Registered corpus-gap honored** — every own-logic target is tier-U/S over the stub; **tier-B is an external precondition for the real acceptance runs, not a target of this unit's Code-Gen and not a Code-Gen blocker**; the **tier-B run is NOT authorized here**.
- **No LLM; no real PII; WIRE-1 untouched; no other unit started.** Settled non-edits stay closed: `PROJECT-BRIEF.md`, every built unit's code/design, and the four consumed surfaces.
