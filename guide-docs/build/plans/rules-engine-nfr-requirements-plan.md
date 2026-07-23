# NFR Requirements Plan — `rules-engine` (C2)

**Phase / Stage**: BUILD → NFR Requirements (per-unit, plan-then-generate)
**Loop position**: cluster unit 2 (dependency order, after intake+document-sanitizer COMPLETE) · FD
**APPROVED 2026-07-03** → **NFR Requirements ← here** → NFR Design → **Infrastructure Design (likely
SKIP — pure-logic deterministic library, same rationale as intake; confirmed at that stage)** →
Code-Gen.
**Unit**: U3 `rules-engine` — the deterministic rulebook engine (pure Python, **zero LLM**).
**Depth**: **comprehensive** (invariant-bearing deterministic-core unit — the
deterministic-core/quality-units-stay-comprehensive rule; `execution-plan.md §3`).
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** (build-wide, D6).
**Status**: **Plan — awaiting `[Answer]:` tags.** No NFR Requirements artifacts generated yet. Stop
after this plan.

This plan follows `.project-guide-rule-details/build/nfr-requirements.md`. NFR Requirements
**builds ON the frozen, approved Functional Design — it does NOT re-open it.** The **C2 contract**
(`load_rulebook` / `evaluate` / `recommend`), the **YAML `Rule` schema** + `input_fields` CON-BR1
mechanism + operator↔threshold §2.1 mapping, the **tri-state `RuleResult`**, the **`RuleResultReport`
shape** (`rulebook_version` + `content_hash` + `engine_version` + decline/refer reasons), the
domain-confirmed boundaries (age 18–65 incl., DTI ≤0.40, BMI 25/30), the `Decimal` DTI/income-multiple
derivations, the fixed-precedence aggregation, and the deterministic `ConfidenceBands` are **settled**;
this stage sets the **quality attributes** (reproducibility, bias-exclusion robustness, replay
verifiability, boundary exactness, error-handling, performance, observability scope) those internals
must meet — each a **pass/fail testable assertion** that becomes the Code-Gen test→target map (as the
`NFR-INT-*` targets did for intake).

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 What this stage decides (NFRs, not functionals)
The FD defined **what** rules-engine does (evaluate a profile against a versioned YAML rulebook →
`RuleResultReport`). NFR Requirements defines **how well** — scoped to this unit's binding invariants:
- **CON-DET-1** (the dominant NFR): `evaluate` is a **pure function** of `(profile, rulebook_version)`
  — **byte-identical** across repeated runs, **order-independent** aggregation, **`Decimal` never
  float**, no wall-clock / unseeded randomness / dict-order reliance. `audit-store` replay depends on it.
- **CON-BR1** (bias-free by design): demographics are **structurally unreachable** — the resolution
  namespace excludes them, and `load_rulebook` **rejects at load** any rule whose `input_fields` names
  a demographic/unknown field. A robustness target, tested as a **universal-quantifier property**.
- **CON-AUDIT-1 / FR-RULES-6** (versioning & replay): the report carries `rulebook_version` +
  `content_hash` + `engine_version`; `content_hash` is the **replay-verification handle**; versions are
  **immutable / append-only**.
- **CON-BR2** (advisory, sole-origin, no LLM): recommendation **and** confidence originate here in pure
  Python; **no LLM anywhere** in the engine.
- **Explainability / error-handling** — exact value + operator per `RuleResult`; **operand-missing →
  `not_evaluated` → `refer_trigger`** (never a divide error, never a silent pass); **`incomplete` →
  REFER**; boundary values land on the intended side.
- **Performance / observability** — scoped to this unit's depth only; the observability **stack** is
  owned by the `observability` unit.

### 1.2 Frozen FD carried in (NOT re-opened — quality targets attach to these)
- `load_rulebook(version) -> Rulebook` / `evaluate(profile, rulebook_version) -> RuleResultReport` /
  `recommend(rule_results) -> Recommendation` (frozen C2 signatures, `component-methods.md`).
- The YAML `Rule` schema (`rule_id`, `category`, `input_fields`, `operator`, `threshold`, `outcome`,
  `rationale_message`, `irdai_ref`) + the **operator↔threshold-shape** binding (§2.1) + tri-state
  `RuleResult` + `RuleResultReport`.
- The **domain-confirmed boundaries** (age `18<=x<=65`, DTI `<=0.40`, BMI `25→overweight`/`30→obese`),
  the `Decimal` **DR-DTI / DR-INCM** derivations (4dp `ROUND_HALF_UP`), the **fixed-precedence
  aggregation** (DECLINE > REFER > APPROVE, order-independent), and the deterministic **ConfidenceBands**.
- The **§7 schema-vs-data boundary**: the FD designs the schema + boundary conventions + a
  representative handful; the **bulk 25–40-rule population is deferred to Code-Gen**. *(NFR Requirements
  sets targets on the ENGINE + the loader/validator, not on authoring rule data.)*

### 1.3 Governing requirements (`requirements.md`)
- **FR-RULES-2** (financial rules: DTI ≤40%, income-multiple), **FR-RULES-3** (exact value + explicit
  comparison), **FR-RULES-5** (recommendation enum, mandatory `-RECOMMEND`), **FR-RULES-6** (immutable
  versioning + replay).
- **CON-BR1** (financials-only, demographics never influence), **CON-BR2** (advisory, no LLM in the
  rules path), **CON-DET-1** (deterministic, no wall-clock/unseeded-random/dict-order), **CON-AUDIT-1**
  (replay against the exact rulebook version), **QA-6** (TDD, pytest-cov ≥90%).
- **NFR-REPRO-1** (decision reproducibility 100% — asserted on THIS engine's output), **NFR-EXPLAIN-1**
  (every result carries its triggering value/reason). **NFR-OBS-1/2** referenced for **scope boundary
  only** (stack owned by `observability`).
- **Verification** of CON-DET-1 / CON-BR1 (reproducibility + bias-swap suites) is single-sourced in
  `quality-gates` — this unit's NFRs **feed** those gates; it does not re-own them.

### 1.4 Guardrails held (skill)
- **No LLM in the deterministic rules path**; **advisory-only** naming (`-RECOMMEND` mandatory,
  "recommendation" never "decision"); **bias-free by design** (CON-BR1); **reproducibility** (CON-DET-1,
  same-input×10 + bias-swap must stay green); **boundary behaviour is first-class**; thin-file /
  single-missing → REFER, never a hard DECLINE.

---

## 2. NFR Requirements execution plan (checkboxes — Step 2)

Input: `guide-docs/build/rules-engine/functional-design/`. Outputs (generated **after** answers +
ambiguity-check): `guide-docs/build/rules-engine/nfr-requirements/` → `nfr-requirements.md`,
`tech-stack-decisions.md`.

- [x] **P1. Analyze the frozen FD** (§1 above — done).
- [x] **P2. Collect `[Answer]:` tags** (§3); run the mandatory ambiguity-check. **DONE 2026-07-05 —
  all 11 answered A; ambiguity-check CLEAN (no clarification file). Two sharpenings folded into
  generation: (1) Q5 = `RulebookCanonAdapter` normalizes into canon_ser's existing value space, no
  §2.1/impl change, no fork, declared set→sorted-list order; (2) Q1/Q7 split into NFR-RULES-DET-1
  (same-order ×N) + NFR-RULES-DET-2 (permuted order).**
- [x] **P3. `nfr-requirements.md`** — the unit's NFRs by category, each a **measurable pass/fail
  target** (`NFR-RULES-*`) with traceability to CON-DET-1/CON-BR1/CON-AUDIT-1/CON-BR2/FR-RULES-*:
  (a) **Reproducibility/determinism** — byte-identical `evaluate` ×N≥10; **order-independent**
  aggregation; `Decimal` exactness at boundaries. (b) **Bias-exclusion robustness** — CON-BR1
  **load-time rejection** (universal-quantifier) + namespace exclusion. (c) **Replay verifiability** —
  `content_hash` determinism + immutable/append-only versioning + the forensic-vs-equality field split.
  (d) **Boundary exactness** — the domain-confirmed inclusivities as assertions. (e) **Error-handling /
  explainability** — operand-missing → `not_evaluated`→`refer_trigger`; `incomplete`→REFER; exact
  value+operator per result. (f) **Deterministic confidence** — replay-stable banding. (g)
  **Performance** — scoped soft budget. (h) **Observability (scope only)** — emit-only, forensic/demographic-free.
  **DONE 2026-07-05 — `nfr-requirements.md` generated: 15 `NFR-RULES-*` targets (DET-1/DET-2, DEC-1,
  CANON-1, BR1-1/BR1-2, SCHEMA-1, AUDIT-1/AUDIT-2/AUDIT-3, BND-1, AGG-1, CONF-1, PERF-1, OBS-1) each a
  pass/fail assertion + traceability + ownership summary. No Mermaid.**
- [x] **P4. `tech-stack-decisions.md`** — settle unit-local tech choices: the **YAML loader** +
  Pydantic-v2 schema validation at load, the **`Decimal` context** (reuse `backend/common/decimal_context`),
  **reference the shared CANON-SER** (`backend/common/canon_ser.py`, audit-store §2.1) for canonicalization
  where it applies, the **no-LLM deterministic engine**, and **Python 3.12 pinned** — no new deps.
- [x] **P5. Scope-boundary check** — **DONE** — ownership reference-not-own recorded in both artifacts
  (shared CANON-SER via `RulebookCanonAdapter` / shared `decimal_context`; observability stack =
  `observability`; bias/repro verification = `quality-gates`; persistence + replay-orchestration =
  `audit-store`; secrets = `secrets-config`; Infra likely SKIP). No cross-cutting NFR redefined here.
- [~] **P6. Guardrail compliance pass + present the standardized 2-option completion message** —
  **2-option message PRESENTED 2026-07-05; awaiting Request Changes / Continue → NFR Design.** (Do NOT
  advance to NFR Design or Code-Gen until Continue.)

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These set **quality targets** — they do **not** re-open the frozen FD.

### A. Reproducibility / determinism (CON-DET-1 — the dominant NFR)

## Question 1 — Determinism acceptance target (byte-identical + order-independence)
`evaluate` must be a pure function of `(profile, rulebook_version)`. What is the target?

A) **Byte-identical ×N≥10 AND order-independence, both asserted.** (i) Same input run **≥10×** →
   identical `RuleResultReport` every run (mirrors NFR-REPRO-1 same-input×10). (ii) **Order-independence**
   — evaluating with the rulebook's rules in **randomized/permuted order** (seeded permutations, and a
   **Hypothesis property** over permutations) yields the **same `recommendation` + `confidence` + the
   same canonical report** (the `rule_results` list is re-sorted to its fixed deterministic order).
   (iii) **No non-determinism sources** — no wall-clock, no unseeded randomness, no dict-order reliance
   (asserted by construction + the ×N/permutation tests). Feeds `quality-gates` reproducibility-suite.
B) Single-run correctness + one fixed-order run; no repeat-run or permutation assertion.
C) Other (please describe after [Answer]: tag below)

[Answer]: A — byte-identical evaluate() across N≥10 runs (pure function of (profile, rulebook_version)) + order-independent aggregation (seeded permutation of rule evaluation order + Hypothesis property → same RuleResultReport regardless of order); no wall-clock/unseeded-randomness/dict-order reliance; Decimal never float.

## Question 2 — `Decimal` derivation exactness (DR-DTI / DR-INCM)
The engine derives `dti_ratio` / `income_multiple` in `Decimal`. What is the exactness target?

A) **`Decimal` 4dp `ROUND_HALF_UP`, boundary-exact, never float** — asserted at the exact thresholds
   (DTI `== 0.40` → pass; `0.4001` → fail; income-multiple `== ceiling` → pass) and repeatable ×N;
   **operand-missing / zero-income** → `not_evaluated` → `refer_trigger` (never a divide error, never a
   fabricated ratio, `actual_value == null`). No float on any threshold-compared value.
B) Float arithmetic with rounding at the end (rejected — CON-DET-1 / boundary drift).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — DR-DTI/DR-INCM in Decimal, 4dp ROUND_HALF_UP via backend/common/decimal_context, boundary-exact, never float; operand-missing → not_evaluated → refer_trigger (never a divide error, never a silent pass).

### B. Bias-exclusion robustness (CON-BR1 — structural, load-time)

## Question 3 — CON-BR1 load-time rejection target (the universal-quantifier property)
Demographics must be **structurally unreachable**. What is the enforcement/robustness target?

A) **Load-time rejection as a tested universal-quantifier property + namespace exclusion.** (i)
   **Hypothesis property**: ∀ rule whose `input_fields` names a demographic path (`demographics.*`,
   name/gender/city) **or** any field outside the allowlist namespace → `load_rulebook` **rejects**
   (raises a load error; the rulebook does not load). (ii) **Namespace-exclusion assertion**: the
   resolution namespace built from a profile **never** contains a demographic field (demographics
   unresolvable even if named). (iii) **Operator↔threshold-shape mismatch** (§2.1) is **also** rejected
   at load. Blocking; feeds `quality-gates` bias-swap (delta = 0). *(Bias-swap delta verification stays
   single-sourced in `quality-gates`; this unit proves the structural mechanism.)*
B) Namespace exclusion only, no load-time rejection test (weaker — a bad rulebook could ship).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — (i) Hypothesis universal-quantifier property: ∀ rule whose input_fields names a demographic path or any field outside the allowlist namespace → load_rulebook rejects (rulebook does not load); (ii) namespace-exclusion assertion (resolution namespace never contains a demographic field); (iii) operator↔threshold §2.1 mismatch also rejected at load. Blocking; bias-swap delta verification stays single-sourced in quality-gates — this unit proves the structural mechanism.

### C. Replay verifiability & versioning (CON-AUDIT-1 / FR-RULES-6)

## Question 4 — `content_hash` + immutable-versioning target
The report carries `rulebook_version` + `content_hash` + `engine_version`; replay verifies against the
**original** version. What is the target?

A) **Deterministic `content_hash` + append-only immutability + the forensic/equality split.** (i)
   `content_hash` is a **deterministic** function of the canonicalized rule set — **same rules → same
   hash; any rule change → a different hash** (tamper-evidence). (ii) `rulebook_version` (semver) +
   `content_hash` are the **replay handle** — sufficient + verifiable to reconstruct the exact ruleset.
   (iii) A published version is **never mutated in place** — a change is a **new version** (append-only;
   old versions remain loadable), asserted. (iv) **Consistency with audit-store's replay projection**:
   `engine_version` + `content_hash` are **forensic/recorded**, NOT part of the replay **equality set**
   (the equality set is the evaluation-output projection — per-rule rows + `recommendation` +
   `confidence`), so an engine-SHA change alone is not a false replay mismatch.
B) `content_hash` recorded but not asserted deterministic; no append-only test.
C) Other (please describe after [Answer]: tag below)

[Answer]: A — deterministic content_hash (same rules → same hash; any change → different hash, tamper-evident); rulebook_version(semver)+content_hash as the replay handle; published versions never mutated in place (append-only, old versions remain loadable, asserted); engine_version+content_hash forensic/recorded, NOT in the replay equality set (equality set = evaluation-output projection: per-rule rows + recommendation + confidence) — consistent with audit-store's replay projection, so an engine-SHA change alone is not a false mismatch.

## Question 5 — Rulebook canonicalization authority (reference-not-own vs rulebook-specific)
How is the rule set **canonicalized** to compute `content_hash` — via the shared CANON-SER, or a
rulebook-specific canonicalization?

A) **Reference the shared CANON-SER** (`backend/common/canon_ser.py`, audit-store §2.1) for the
   rulebook canonicalization / `content_hash` **where the rule-set value space fits it** (stable key
   order, `Decimal`-as-string, canonical scalars, null explicit) — one canonicalization authority
   across the build (reference-not-own), consistent with intake's `CanonSerAdapter`.
B) **A rulebook-specific deterministic canonicalization** (declared + tested) because the YAML `Rule`
   shapes (`operator`/`threshold` unions, `DecimalRange`, `set` thresholds) differ enough from
   `ApplicantProfile` that reusing CANON-SER would be forced — still `Decimal`-as-string + stable
   ordering, but its own module. (Would be a **new** canonicalization to justify vs A.)
C) Other (please describe after [Answer]: tag below)

[Answer]: A — REFERENCE the shared CANON-SER (backend/common/canon_ser.py, audit-store §2.1) and EXTEND its coverage to the rule-set shapes (DecimalRange = two Decimals; set-threshold = sorted canonical scalars; operator unions = canonical scalars) under the SAME four §2.1 properties (stable key order, Decimal-as-string, canonical scalars/null-explicit, no volatile fields) — ONE canonicalization convention covering both value spaces, not a forked parallel implementation. Rationale: the rule shapes are expressible under §2.1's properties, so a rulebook-specific canonicalization would be avoidable drift. If any rule shape genuinely can't be expressed under §2.1, flag it rather than silently forking.

### D. Boundary exactness (FR-RULES-3)

## Question 6 — Boundary-exactness test target (domain-confirmed inclusivities)
The domain boundaries must land on the intended side. What is the target?

A) **First-class boundary assertions** at the domain-confirmed inclusivities — **age `18` → eligible,
   `65` → eligible** (`17`/`66` → not); **DTI `0.40` → pass** (`0.4001` → fail); **BMI `25.00` →
   overweight** (not normal), **`30.00` → obese** — each asserting the exact `actual_value` + the
   explicit `operator` recorded in the `RuleResult` (FR-RULES-3). Blocking in `quality-gates`.
B) A few representative near-boundary tests; trust the operator encoding for the exact points.
C) Other (please describe after [Answer]: tag below)

[Answer]: A — boundary exactness as assertions: age 18≤x≤65 inclusive, DTI ≤0.40 passes (0.40 exact passes), BMI 25→overweight / 30→obese (exactly 25→overweight, exactly 30→obese); exact value + operator recorded per RuleResult.

### E. Aggregation, insufficient-info, confidence

## Question 7 — Aggregation + insufficient-info target
Fixed precedence (DECLINE > REFER > APPROVE) + insufficient-info handling. What is the target?

A) **Order-independent precedence + single-notioned insufficient-info REFER.** (i) Aggregation is a
   pure function of the **set** of `outcome_tier`s — **DECLINE dominates** REFER dominates APPROVE —
   tested **order-independent** (permutation). (ii) **operand-missing → `not_evaluated` →
   `refer_trigger`** and (iii) **`profile.incomplete == true` → a distinct insufficient-info
   `refer_trigger`** → **REFER, never DECLINE on incompleteness alone** (thin-file preserved). (iv)
   `decline_reasons` / `refer_reasons` name exactly the driving rule(s) (explainability). Each asserted.
B) Test happy/decline/refer paths without an explicit order-independence or thin-file-preservation assertion.
C) Other (please describe after [Answer]: tag below)

[Answer]: A — order-independent aggregation DECLINE > REFER > APPROVE (same result regardless of rule order); incomplete → REFER never DECLINE (thin-file preserved); not_evaluated contributes to refer_trigger, never to decline.

## Question 8 — Deterministic confidence target
`confidence ∈ {High, Medium, Low}`, produced here (never the LLM). What is the target?

A) **Replay-stable deterministic banding.** Confidence is a **pure function** of value-proximity +
   completeness using the **fixed `ConfidenceBands` constants** carried in the versioned rulebook —
   same input + `rulebook_version` → **identical `confidence` ×N**; **no randomness, no wall-clock**;
   a margin change is itself a **new rulebook version** (replay under the original stays exact).
   Produced in rules-engine, **never by the LLM** (CON-BR2).
B) A heuristic confidence with no repeat-run determinism assertion.
C) Other (please describe after [Answer]: tag below)

[Answer]: A — deterministic confidence banding on FIXED constants (versioned with the rulebook), replay-stable, byte-identical ×N, never LLM.

### F. Performance & observability scope

## Question 9 — Performance envelope (scoped, not an SLA)
What performance target for `evaluate()` on the full rule set?

A) **A soft budget, observed — not an SLA.** A documented target for `evaluate()` over the full
   **25–40-rule** set on a typical synthetic profile (in-memory, pure-Python, **no untrusted parsing
   here** — so **no hard timeout is needed**, unlike intake's sandbox). **Correctness + determinism +
   explainability take precedence over speed** (skill). Recorded/observed, not breach-failing.
B) A strict enforced latency SLA with failure on breach.
C) Other (please describe after [Answer]: tag below)

[Answer]: A — soft budget only, NO hard timeout (no untrusted parsing here, unlike intake's sandbox — the engine operates on already-validated data). Observed/recorded, not gated.

## Question 10 — Observability SCOPE (emit-only, forensic/demographic-free)
What does rules-engine commit to here (vs the `observability` unit)?

A) **Emit-only.** Emit `evaluate` spans + counters (per-`recommendation` count, per-rule fired/`not_evaluated`
   counts, `confidence` band, aggregation-tier) for the `observability` unit to wire — this unit does
   **NOT** design the Langfuse/Prometheus/Grafana stack. **No LLM** (there is none in this path). **No
   demographic content is ever emitted** (CON-BR1 extends to telemetry — the emit schema carries only
   ids/enums/counts, never demographic fields or free text).
B) Design the observability wiring here (rejected — owned by `observability`).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — emit-only (stack owned by observability unit); no LLM; NO demographic content in telemetry (CON-BR1 extends to telemetry — same forensic-boundary discipline as intake's SEC-1-FORENSIC-to-telemetry: allowlist-schema emitter, no field can carry a demographic value).

### G. Tech-stack confirmation (unit-local)

## Question 11 — Loader + validation + determinism stack
Confirm the unit-local stack for `tech-stack-decisions.md`.

A) **`pyyaml` `safe_load`** (already in the brief's stack) → **Pydantic v2** schema-validates each
   `Rule` at load (rejecting CON-BR1 / operator↔threshold violations) + **`Decimal`** via the shared
   `backend/common/decimal_context` + **reference the shared CANON-SER** (`backend/common/canon_ser.py`)
   for canonicalization where it applies + **NO LLM anywhere** in the engine + **Python 3.12 pinned**
   (D6). No new third-party dependency. Exact pins are a Code-Gen concern.
B) A different loader/validation library (would need justification vs the brief's stack).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — pyyaml safe_load + Pydantic v2 load-validation (rejects CON-BR1 / operator↔threshold violations at load) + shared backend/common/decimal_context + reference shared CANON-SER (extended per Q5) + NO LLM anywhere + Python 3.12 pinned. No new third-party dependency; exact pins are a Code-Gen concern.

---

## 4. Constraints & settled items held (not re-opened)
- The **Functional Design is frozen + approved** — NFR Requirements attaches quality targets to it,
  never re-opens the C2 contract, the YAML `Rule` schema, tri-state `RuleResult`, `RuleResultReport`,
  the boundary conventions, or the derivations/aggregation/confidence semantics.
- **Schema-vs-data boundary honored**: the bulk 25–40-rule **data authoring is deferred to Code-Gen**
  (FD §7). NFR Requirements targets the **engine + loader/validator**, not the rule data itself.
- **Infrastructure Design is likely SKIP for this unit** (to be confirmed + logged at that stage) —
  pure-logic deterministic library, same rationale as intake; persistence/replay-orchestration owned by
  `audit-store`, deployment by `deploy-config`. No untrusted parsing here, so **no sandbox NFR** either.
- **Ownership boundaries respected** (reference-not-own): shared **CANON-SER** = audit-store §2.1 via
  `backend/common/`; observability **stack** = `observability`; CON-DET-1 / CON-BR1 **verification** =
  `quality-gates` (reproducibility + bias-swap); replay **orchestration** = `audit-store` ReplayService;
  secrets = `secrets-config`. This unit sets its own targets + what it emits/feeds.
- **No LLM anywhere in this unit** (CON-BR2); advisory-only naming (`-RECOMMEND`); Python **3.12 pinned**.
- Three settled non-edits stay closed: `PROJECT-BRIEF.md`, OOS-7 README/case-study doc commitment,
  `user-journey.md`.

---

## 5. Loop position confirmation
**NFR Requirements (← here) → NFR Design → Infrastructure Design (likely SKIP — confirm/log at that
stage) → Code-Gen.** Same per-unit sequence intake followed; Infrastructure Design is expected to be a
logged skip for this pure-logic unit (no independent cloud topology; no untrusted-parse sandbox), but
that call is made when the stage is reached, not pre-committed here.

---

## 6. Next step (STOP here)
Fill the eleven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory
ambiguity-check (adding a clarification file only if needed), then generate the NFR Requirements
artifacts (`nfr-requirements.md` with the `NFR-RULES-*` targets, `tech-stack-decisions.md`) and present
the standardized 2-option completion message. **No NFR Requirements artifacts or code are generated
until the answers are in and checked.**
