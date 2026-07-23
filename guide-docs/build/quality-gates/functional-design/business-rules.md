# Business Rules — `quality-gates` (U13)

**Stage**: BUILD → Functional Design (per-unit) · the four blocking verification gates · **Depth**: COMPREHENSIVE
**Unit**: U13 `quality-gates` · **Date**: 2026-07-08 · **single verification authority** for CON-BR1 / CON-BR2·AC-1 / QA-3 / AC-5 · Stories **US-PLAT-3/4/5/6**.
**Scope**: The **enforceable verification rules** the four gates obey. Each states its **condition** and, where checkable, names the **mechanism** (landing at NFR / Code-Gen). **Verification only** — `quality-gates` asserts invariants hold; it does not enforce or re-define them. Built exactly on the seven locked answers + the five QG-Folds — re-opening none.

---

## 1. Bias-swap invariance (CON-BR1 — single verification authority)

### BR-QG-1 — Bias-swap delta = 0; any delta blocking (US-PLAT-3)
- **Condition**: for an applicant profile, swapping the segregated demographic identifiers `{full_name, gender, city}` (via `ApplicantProfile.model_copy(update={"demographics": ...})`) while holding **all** financial/medical fields identical leaves the engine `recommendation` **unchanged**. **Bias-swap delta = 0. Any delta is a blocking bug, not a warning.**
- **Why**: CON-BR1 (no demographic proxy); `quality-gates` bias-swap is the **one authority** that asserts the invariant holds (delta=0) — distinct from `rules-engine`/`outlier-model` *enforcement* and from `corpus-generator`'s own layered-respect check.
- **Checkable**: for each profile from the `CorpusLoader`, `evaluate(profile).recommendation == evaluate(swapped).recommendation`; the `BiasSwapReport.delta_count` must be 0 (blocking pytest test). Compared via the engine recommendation (and, for a full projection, `evaluation_output()`).

### BR-QG-2 — Proxy-variable check over occupation + income; pincode N/A (QG-Fold-5)
- **Condition**: the suite adds a proxy check over `occupation` and `income` — they may differ **only** through their **sanctioned rules** (occupation-risk / affordability). Any recommendation change when they vary is attributable to those rules, never to a demographic proxy. **`pincode` is N/A** — no such field exists on `ApplicantProfile` (documented explicitly, not silently skipped).
- **Why**: US-PLAT-3 proxy-variable requirement; guards against demographic leakage through financial proxies while respecting legitimate rule inputs.
- **Checkable**: varying `occupation`/`income` changes the recommendation only in accordance with the sanctioned rule outcomes; a documented note records `pincode` as absent from the schema.

---

## 2. Reproducibility (CON-BR2 / AC-1 — deterministic engine output)

### BR-QG-3 — Reproducibility 100% over the deterministic engine output (US-PLAT-4)
- **Condition**: running the **same input 10×** through `evaluate(profile, rulebook_version)` yields an **identical `evaluation_output()` projection** each run (identical APPROVE/REFER/DECLINE-RECOMMEND + rule results + reasons). **Decision reproducibility = 100%**, asserted on the **deterministic engine output**, **not** on LLM memo wording. The **seeded-outlier** determinism clause is **deferred to when `outlier-model` (P2) lands** (documented, not dropped).
- **Why**: CON-BR2 / AC-1 / NFR-REPRO-1; identical input → identical decision, enforced via `temperature=0` + the deterministic engine (+ seeded outlier, P2).
- **Checkable**: `evaluation_output(evaluate(p, v))` is byte-identical across 10 runs per profile; `ReproducibilityReport.reproducibility_pct == 100` (blocking). Uses the **imported** `evaluation_output()` projection (reference-not-own — the same one ReplayService uses).

---

## 3. Rule coverage (QA-3 / AC-4)

### BR-QG-4 — Every rule definitely evaluated over the corpus; uncovered = blocking (US-PLAT-5)
- **Condition**: every `rule_id` in the **loaded rulebook** (via `RulebookLoader.load_rulebook(manifest.rulebook_version)`) must reach a **definite PASS or FAIL** (status **not** `not_evaluated`) in **≥1** corpus record's `RuleResultReport`. **Rule coverage = 100%. Any never-definitively-evaluated rule is a blocking test failure.**
- **Why**: QA-3 / AC-4 — no rule ships untested; the rulebook is loaded at the **exact version** the corpus was labeled against (QG-Fold-2), so coverage is measured against the right rule set.
- **Checkable**: iterate `evaluate()` over the `CorpusLoader` profiles; collect, per `rule_id`, whether a definite PASS/FAIL was observed; `RuleCoverageReport.uncovered_rule_ids` must be empty / `coverage_pct == 100` (blocking).

---

## 4. Code-coverage gate (AC-5 / QA-6)

### BR-QG-5 — Binding ≥90% stays in pyproject; coverage_gate is a wiring meta-assertion + evidence (QG-Fold-3)
- **Condition**: the **binding** code-coverage enforcement (**≥90%**, build-failing) **stays in `pyproject.toml`** (`--cov-fail-under=90`, already proven across nine units). `coverage_gate.py`'s **collected pytest test** is a **structural wiring meta-assertion** — it asserts the `pyproject` gate is **present and set to ≥90** (because a collected test cannot read the final coverage % mid-session). The coverage **percentage evidence** is a **separately generated report** from the coverage data artifact. **This is not a second enforcement mechanism.**
- **Why**: AC-5 / QA-6; TDD binding gate from day one; avoids a divergent/duplicate coverage enforcer.
- **Checkable**: the meta-assertion reads `pyproject` and asserts `--cov-fail-under` is present with value ≥90 (`CoverageGateReport.wiring_present and fail_under_configured >= 90`); the % evidence report is produced from the coverage data (informational).

---

## 5. Corpus source & tiering (the registered gap)

### BR-QG-6 — Corpus-source abstraction; tier-U/S now, tier-B separate (QG-Fold-1)
- **Condition**: the gates obtain profiles through an injected **`CorpusLoader`** that reads the frozen `corpus/profiles.json` (via `CorpusRecord.model_validate`) **or** accepts an **in-memory** `CorpusRecord`/profile list. **Tier-U/S** runs every gate's **logic** over a **small test-scoped stub** (+ a controlled rulebook) in CI; the **real full-corpus acceptance runs** read the **committed tier-B artifact** as a **separate, later, out-of-band step** — **not a Code-Gen hard dependency**.
- **Why**: the registered Deferred-Decisions constraint — the real frozen corpus exists only after the out-of-band tier-B build (never in CI); `quality-gates` Code-Gen must complete + pass CI on the stub.
- **Checkable**: the gates accept an injected corpus source; CI tests pass on the in-memory stub with **no** committed `corpus/` present; the frozen-file path is exercised only when a tier-B corpus exists.

---

## 6. Reference-not-own, evidence & blocking form

### BR-QG-7 — Verification only; reference-not-own; no enforcement/definition
- **Condition**: the consumed surfaces (`rules-engine` `evaluate`/`evaluation_output`/`RulebookLoader`, `corpus-generator` `CorpusRecord`/`CorpusManifest`, `intake` `ApplicantProfile`/`Demographics`, `audit-store` `ReplayService` pattern) are **call-only / reference-not-own; none edited**. `quality-gates` re-implements **no** rule evaluation, hashing, derivation, or second engine, and **does not enforce or re-define** CON-BR1 / CON-DET-1 (enforcement lives in `rules-engine`/`outlier-model`) or re-own memo's structural CON-BR2.
- **Why**: single-verification-authority-vs-enforcement boundary (unit-of-work.md §A.1 rule 4); no invariant is re-defined, so nothing can drift.
- **Checkable**: a structural check finds no local rule-eval/hasher/derivation and no production edit in the consumed units; the gates only import + call.

### BR-QG-8 — Auditor evidence: each gate emits a human-readable read-only artifact
- **Condition**: each gate emits a **reproducible, human-readable** evidence record (`BiasSwapReport` / `ReproducibilityReport` / `RuleCoverageReport` / `CoverageGateReport`) — the auditor-consumable read-only artifact of US-PLAT-3/4/5.
- **Why**: US-PLAT-3/4/5 "viewable by the auditor as a read-only artifact"; auditor-voiced evidence.
- **Checkable**: each gate run produces its report record; the report is deterministic (pure function of corpus/rulebook/engine).

### BR-QG-9 — Blocking form: each gate is a collected pytest test that fails the build on violation
- **Condition**: each gate is a **collected pytest test** that **fails the build** on violation — bias-swap `delta ≠ 0`, any reproducibility run differing, any uncovered rule, or (coverage-gate) the `pyproject` wiring absent/`< 90`. Runs in CI.
- **Why**: US-PLAT-3/4/5/6 — the gates are blocking, not advisory; QA/AC enforced in CI.
- **Checkable**: the pytest tests are collected in the root run; a violation is a test failure (the coverage-gate's live-% enforcement is `pyproject`'s `--cov-fail-under`, QG-Fold-3).

---

## 7. Rule index

| Rule | Condition summary | Traces |
|---|---|---|
| BR-QG-1 | bias-swap `{name,gender,city}` delta=0; any delta blocking | CON-BR1, NFR-BIAS-1, QA-2, AC-3, US-PLAT-3 |
| BR-QG-2 | proxy check over occupation+income via sanctioned rules; pincode N/A | CON-BR1, US-PLAT-3 |
| BR-QG-3 | reproducibility ×10 identical `evaluation_output()`; 100%; engine-deterministic; outlier deferred P2 | CON-BR2, NFR-REPRO-1, QA-1, AC-1, US-PLAT-4 |
| BR-QG-4 | every rule definite PASS/FAIL over the corpus at `manifest.rulebook_version`; uncovered blocking | QA-3, AC-4, US-PLAT-5 |
| BR-QG-5 | binding ≥90% stays in `pyproject`; coverage_gate = wiring meta-assertion + evidence (not a 2nd enforcer) | AC-5, QA-6, US-PLAT-6 |
| BR-QG-6 | `CorpusLoader` (frozen file or in-memory); tier-U/S now, tier-B separate; not a Code-Gen dep | DATA-3 (consumer), registered gap |
| BR-QG-7 | verification only; reference-not-own; no enforcement/definition | unit-of-work §A.1 rule 4 |
| BR-QG-8 | each gate emits a human-readable read-only auditor evidence artifact | US-PLAT-3/4/5 |
| BR-QG-9 | each gate is a collected blocking pytest test in CI | US-PLAT-3/4/5/6 |

---

## 8. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | The unit reads already-validated frozen `ApplicantProfile`s (Pydantic-valid by construction at intake/corpus-generator); it validates no new application input. |
| Prompt-injection defense | **N/A** | No LLM is invoked here — the gates verify the deterministic engine; no untrusted document is parsed. |
| Secrets management | **N/A** | No provider key is read (no LLM path); the tier-B corpus is consumed as committed data, not regenerated. |
| Read-only DB access for audit role | **N/A** | The unit reads the frozen `corpus/` artifact / in-memory stub, not the audit DB. |
| Audit logging | **N/A (produces evidence)** | The gate **evidence reports** are the auditor-consumable artifacts (US-PLAT-3/4/5); this is not the runtime audit trail (SEC-5 is `audit-store`'s). |
| **No real PII / synthetic-only** | **Compliant (referenced)** | All profiles are synthetic (corpus-generator BR-CORP-10); `quality-gates` introduces no real PII. |

No blocking finding.
