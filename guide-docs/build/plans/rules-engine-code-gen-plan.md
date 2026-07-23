# Code Generation Plan (Part 1) — `rules-engine` (C2)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: cluster unit 2 · FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure
Design SKIPPED (logged 2026-07-05)** → **Code-Gen ← here — the SECOND unit's code** (after
intake+document-sanitizer COMPLETE).
**Unit**: U3 `rules-engine` — the deterministic rulebook engine (pure Python, **zero LLM**).
**Stories**: US-RULES-1..5 (rulebook evaluation, boundaries, recommendation, versioning, occupation/CON-BR1).
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** (D6) — the venv is already recreated on 3.12.
**Status**: **Plan — awaiting `[Answer]:` tags. NO CODE, NO TESTS, NO IMPLEMENTATION this stage.**
Stop after this plan.

This plan follows `.project-guide-rule-details/build/code-generation.md` (Part 1) + the project's
plan-then-generate discipline. **TDD is binding** (QA-6, pytest-cov ≥ 90%): **tests are written FIRST,
then implementation.** Code-Gen **builds ON** the frozen C2 contract, the frozen FD, the approved
`NFR-RULES-*` targets, the NFR design patterns, and the 9 logical components — **re-opening none of them.**

---

## 1. Unit context (analyzed — Step 1)

### 1.1 What Code-Gen builds on (frozen — NOT re-opened)
- **C2 contract** (`component-methods.md`): `load_rulebook(version: str) -> Rulebook`,
  `evaluate(profile: ApplicantProfile, rulebook_version: str) -> RuleResultReport`,
  `recommend(rule_results) -> Recommendation` (internal to `evaluate`).
- **FD** (`build/rules-engine/functional-design/`): the YAML `Rule` schema + `input_fields` CON-BR1
  mechanism + operator↔threshold §2.1 mapping; the domain-confirmed boundaries (age 18–65 incl., DTI
  ≤0.40, BMI 25/30); the `Decimal` DR-DTI/DR-INCM derivations; the fixed-precedence aggregation;
  tri-state `RuleResult`; the `RuleResultReport` shape; the deterministic `ConfidenceBands`; the §7
  schema-vs-data boundary.
- **NFR targets** (`build/rules-engine/nfr-requirements/`): the 15 `NFR-RULES-*` pass/fail assertions.
- **NFR patterns + 9 components** (`build/rules-engine/nfr-design/`): RulebookLoader(+validator),
  RulebookCanonAdapter, NamespaceBuilder, DerivationFunctions, RuleEvaluator, Aggregator,
  ConfidenceBander, ReportBuilder, TelemetryEmitter — incl. the **DET-2 sharpening** (all order-derived
  report list fields in the one canonical order by `rule_id`).

### 1.2 Dependencies & interfaces
- **Consumes**: `ApplicantProfile` (intake's frozen contract, imported from `backend.intake.schema` —
  **read, not re-declared**) + a `rulebook_version` string.
- **Produces**: `RuleResultReport` (to `memo-agent-core` read-only + to `audit-store` for persist/replay),
  emitted telemetry (to `observability`).
- **Shared (reference-not-own)**: `backend/common/canon_ser.py` (via the `RulebookCanonAdapter`,
  **unchanged**) + `backend/common/decimal_context.py` (via `DerivationFunctions`). **Imported, never
  re-declared.**
- **N/A layers** (code-generation.md step categories that do not apply — see Q6): **API layer** (FastAPI
  orchestrator composition root), **Repository/persistence** (`audit-store` + `database`), **Frontend**
  (backend unit), **DB migrations** (`database`), **replay orchestration** (`audit-store` ReplayService —
  this unit provides only pure `evaluate` + a separable report).

### 1.3 Monorepo placement (single monorepo — `unit-of-work.md §2`)
```
backend/
├── common/                       # shared (EXISTS — imported, not modified)
│   ├── canon_ser.py              #   shared CANON-SER (audit-store §2.1)
│   └── decimal_context.py        #   single Decimal context
├── intake/                       # EXISTS — ApplicantProfile imported read-only
│   └── schema.py
└── rules_engine/                 # UNIT: rules-engine (C2)  [package = rules_engine, underscore]
    ├── rulebook_schema.py        #   Rule / Rulebook / DecimalRange / ConfidenceBands (Pydantic v2) + load validators
    ├── report_schema.py          #   RuleResult / RuleResultReport / Recommendation / Confidence / tier + status enums
    ├── loader.py                 #   RulebookLoader (pyyaml safe_load + validate + freeze + versioned store)
    ├── canon_adapter.py          #   RulebookCanonAdapter (normalize -> shared canon_ser; content_hash)
    ├── namespace.py              #   NamespaceBuilder (demographic-excluded + derived operands)
    ├── derivations.py            #   DerivationFunctions (DR-DTI/DR-INCM; guard-before-divide; shared decimal_context)
    ├── evaluator.py              #   RuleEvaluator (evaluate(); fixed canonical order; tri-state RuleResult)
    ├── aggregator.py             #   Aggregator (set-reduction precedence; incomplete->REFER)
    ├── confidence.py             #   ConfidenceBander (fixed versioned constants)
    ├── report.py                 #   ReportBuilder (RuleResultReport; ALL list fields canonical order; output-vs-provenance)
    ├── telemetry.py              #   TelemetryEmitter (allowlist schema; no demographic/free-text field)
    ├── rulebook/                 #   versioned rulebook YAML data (scope per Q3)
    └── tests/                    #   co-located tests + rulebook YAML fixtures (Q2)
```
*(Exact module split is refined at generation; the mapping above is the plan of record.)*

### 1.4 Guardrails held (skill)
- **No LLM anywhere** (CON-BR2); **CON-DET-1** (pure `evaluate`, order-independent aggregation,
  `Decimal` not float, no wall-clock/unseeded-random/dict-order); **CON-BR1** (demographics unreachable —
  load-time reject + namespace exclusion, never in telemetry); **CON-AUDIT-1** (immutable versions,
  `content_hash` verifiable, forensic-not-equality); advisory-only (`-RECOMMEND`); thin-file → REFER
  never DECLINE.

---

## 2. Code-Generation execution plan (numbered steps — TDD, tests FIRST)

**Discipline**: for each component, **its test suite is written before its implementation**; the suite
encodes the mapped `NFR-RULES-*` assertion(s) + FD rule(s). Implementation order is **leaf-first, then
composing components**. Application code → `backend/rules_engine/…` (never `guide-docs/`); markdown
summary → `guide-docs/build/rules-engine/code/`.

- [x] **Step 0 — Package skeleton**: create `backend/rules_engine/` + co-located `tests/` + `rulebook/`;
  reuse the root `pyproject.toml` cov config, extending `--cov` to `backend/rules_engine`. *(No app code
  — skeleton + config.)* **DONE 2026-07-05** — package `backend/rules_engine/` + `tests/` + `tests/fixtures/`
  + `rulebook/` dirs present; `pyproject.toml` `addopts` already carries `--cov=backend/rules_engine`.
- [x] **Step 1 — `report_schema.py` (data models, leaf)**: TEST FIRST (Pydantic v2 validation; tri-state
  `RuleResult`; `RuleResultReport` with `rule_results`/`recommendation`/`confidence`/`rulebook_version`/
  `content_hash`/`engine_version`/`decline_reasons`/`refer_reasons`; enums incl. `-RECOMMEND`) →
  implement the FD output contract. Maps: FD `domain-entities.md §6` (frozen — implement exactly).
  **DONE 2026-07-05** — `rules_engine/report_schema.py` (100% cov); frozen+extra-forbid; 7 shared enums
  + `DecimalRange` (placed here as the schema leaf, imported by rulebook_schema — avoids circular import);
  Number rejects float; 12 tests.
- [x] **Step 2 — `rulebook_schema.py` (data models + load validators, leaf)**: TEST FIRST (Rule/Rulebook/
  DecimalRange/ConfidenceBands models; **operator↔threshold-shape validator rejects mismatch — SCHEMA-1**;
  **`input_fields` allowlist validator rejects demographic/unknown field — BR1-1**, incl. a **Hypothesis
  universal-quantifier** over bad field names) → implement the frozen §2/§2.1 schema + validators. Maps:
  NFR-RULES-BR1-1, NFR-RULES-SCHEMA-1; FD `domain-entities.md §2/§2.1`. **DONE 2026-07-05** —
  `rulebook_schema.py` (99% cov); single-sourced `ALLOWED_INPUT_FIELDS`; all 7 operators covered
  (sharpening 2); 25 tests incl. Hypothesis ∀ out-of-allowlist reject.
- [x] **Step 3 — `RulebookCanonAdapter` (leaf, composes shared canon_ser)**: TEST FIRST (byte-stable +
  **set-order-invariant** — same rulebook, different set/authoring order → identical bytes; normalization
  of set→sorted-list / DecimalRange→dict / enum→.value; **shared `canon_ser` unchanged**) → implement
  `canon_adapter.py`. Maps: NFR-RULES-CANON-1. **DONE 2026-07-05** — `canon_adapter.py` (100% cov);
  set-order + rule-order invariant, hash-differs-on-change, version-not-in-hash, delegates to unchanged
  shared canon_ser; 8 tests (sharpening 5 set-threshold exercised).
- [x] **Step 4 — `DerivationFunctions` (leaf, composes shared decimal_context)**: TEST FIRST (DR-DTI/
  DR-INCM `Decimal` 4dp `ROUND_HALF_UP`, boundary-exact `0.40`/ceiling; **guard-before-divide** —
  operand-missing/zero-income → `not_evaluated`+`refer_trigger`, `actual_value==null`, **no divide path
  reached**; byte-identical ×N) → implement `derivations.py`. Maps: NFR-RULES-DEC-1. **DONE 2026-07-05**
  — `derivations.py` (100% cov); guard-before-divide (returns None, no divide path); 4dp HALF_UP via
  shared decimal_context; 11 tests incl. Hypothesis determinism+4dp property.
- [x] **Step 5 — `NamespaceBuilder` (leaf)**: TEST FIRST (**namespace-exclusion assertion — demographics
  never in the namespace, BR1-2**, independent of the load gate; only demographic-excluded fields +
  derived operands present) → implement `namespace.py`. Maps: NFR-RULES-BR1-2. **DONE 2026-07-05** —
  `namespace.py` (100% cov); namespace keys == single-sourced ALLOWED_INPUT_FIELDS; demographics never
  present; derived operands computed; 6 tests.
- [x] **Step 6 — `RulebookLoader` (composes rulebook_schema)**: TEST FIRST (**load-time rejection** of a
  demographic/unknown-field or operator↔threshold-mismatch rulebook — the universal-quantifier + curated
  bad rulebooks; **frozen immutable** rulebook; **append-only** — a published version never mutated, old
  versions loadable; `content_hash` recomputed+verified) → implement `loader.py` (pyyaml `safe_load`).
  Maps: NFR-RULES-BR1-1, NFR-RULES-SCHEMA-1, NFR-RULES-AUDIT-1, NFR-RULES-AUDIT-2.
- [x] **Step 7 — `RuleEvaluator` (composes namespace + derivations + schema)**: TEST FIRST (**DET-1
  byte-identical ×N≥10** same-order; **boundary exactness BND-1** — age 18/65 incl., DTI 0.40 pass, BMI
  25→overweight/30→obese, exact `actual_value`+`operator` recorded; tri-state per rule; operands resolved
  **only** from `input_fields`) → implement `evaluator.py` (fixed canonical order by `rule_id`). Maps:
  NFR-RULES-DET-1, NFR-RULES-BND-1; FD `business-rules.md §1`.
- [x] **Step 8 — `Aggregator` (leaf reduction)**: TEST FIRST (**order-independent precedence** DECLINE >
  REFER > APPROVE via **Hypothesis permutation** of the tier set; **incomplete/`not_evaluated` → REFER,
  never DECLINE** — thin-file preserved; `decline_reasons`/`refer_reasons` collected) → implement
  `aggregator.py`. Maps: NFR-RULES-AGG-1.
- [x] **Step 9 — `ConfidenceBander` (composes constants)**: TEST FIRST (deterministic banding on the
  fixed versioned `ConfidenceBands`; identical `confidence` ×N; proximity+completeness; never LLM) →
  implement `confidence.py`. Maps: NFR-RULES-CONF-1.
- [x] **Step 10 — `ReportBuilder` (composes evaluator+aggregator+confidence+canon_adapter)**: TEST FIRST
  (**DET-2 — ALL order-derived list fields (`rule_results`, `decline_reasons`, `refer_reasons`) in the one
  canonical order by `rule_id`** → a **permuted evaluation yields a byte-identical whole report** via
  Hypothesis permutation; **output-vs-provenance separation** — a report differing only in `engine_version`
  is equal under the evaluation-output projection, `content_hash` used for verification not equality —
  AUDIT-3) → implement `report.py`. Maps: NFR-RULES-DET-2, NFR-RULES-AUDIT-3.
- [x] **Step 11 — `evaluate()` orchestration (wires loader→namespace→evaluator→aggregator→confidence→
  report)**: TEST FIRST (end-to-end pure `evaluate(profile, rulebook_version)`: happy APPROVE, boundary,
  incomplete→REFER, multi-fail→DECLINE-RECOMMEND; **DET-1 same-order ×N + DET-2 permuted whole-report
  byte-identity** end-to-end) → wire the frozen pipeline. Maps: NFR-RULES-DET-1/-DET-2, FD
  `business-logic-model.md §2`.
- [x] **Step 12 — `TelemetryEmitter` (allowlist schema)**: TEST FIRST (**schema-level assertion — no
  applicant-profile/demographic/free-text field; only rule_id/enums/int counts/timing — OBS-1**;
  emit-only; observed-only `evaluate` timing — PERF-1) → implement `telemetry.py`. Maps: NFR-RULES-OBS-1,
  NFR-RULES-PERF-1.
- [x] **Step 13 — Rulebook YAML data + fixtures (scope per Q3)**: author the versioned rulebook YAML
  (scope decided at Q3) + the curated test rulebook fixtures (Q2); confirm all synthetic + no real PII.
  Every FD `category` profile-backed. Maps: FD §7 schema-vs-data.
- [x] **Step 14 — Coverage gate + documentation**: confirm pytest-cov **≥90%** for the unit (on Python
  3.12); write the **code summary** to `guide-docs/build/rules-engine/code/` (markdown only — modules,
  tests→target map, coverage). *(Blocking-gate aggregation is `quality-gates`; this unit authors its own tests.)*
  **DONE 2026-07-05** — full backend suite **376 passed / 3 skipped / 99.62%** (rules_engine 165 tests, all
  source lines 100%; one unreachable enum-exhaustive branch in rulebook_schema); `code/code-summary.md` written.
- [x] **Step 15 — Present the standardized 2-option completion message** (code-generation.md Step 14
  format) → Request Changes / Continue → next cluster unit's Code-Gen (`audit-store`) per the dependency order.
  **APPROVED 2026-07-05.** The `medical_health` / `document_completeness` gap flagged at the gate was RESOLVED
  via option (a) (derived scalar operands `health_flag_count` / `documents_missing_count` + FD §4.2
  back-annotation, verified on disk); all 9 categories rule-exercised. **rules-engine Code-Gen COMPLETE.**

**N/A step-categories** (code-generation.md Step 2 — justified skips, see Q6): **API Layer**,
**Repository Layer**, **Frontend Components**, **Database Migration**, **replay orchestration** — owned by
the orchestrator / `audit-store` / `database`. This unit generates **business logic + its tests + a code
summary** only.

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These decide **Code-Gen specifics** — they do **not** re-open the FD / NFR targets / patterns.

## Question 1 — Test framework + property-based testing
What is the test toolchain (TDD, ≥90%)?

A) **pytest + pytest-cov (≥90%, QA-6)** as the base, **plus Hypothesis** for the **universal-quantifier
   invariants** this unit rests on — **order-independence** (permuted rule/tier order → identical result),
   **load-time CON-BR1 rejection** (∀ demographic/unknown `input_fields` → load rejects), and **DET-2
   whole-report byte-identity** under permutation — alongside explicit boundary/example tests. Same
   toolchain as intake.
B) pytest + pytest-cov only, no property-based testing.
C) Other (please describe after [Answer]: tag below)

[Answer]: A — pytest + pytest-cov (≥90%, QA-6) + Hypothesis for the universal-quantifier invariants (order-independence via permuted rule/tier order → identical result; load-time CON-BR1 rejection ∀ demographic/unknown input_fields → reject; DET-2 whole-report byte-identity under permutation) alongside explicit boundary/example tests. Same toolchain as intake.

## Question 2 — Rulebook YAML fixture strategy (test rulebooks)
How are the test rulebooks built (deterministic, PII-free)?

A) **Curated static YAML rulebook fixtures** under `rules_engine/tests/` — small, versioned, hand-authored
   rulebooks: a **valid representative** rulebook (covering the boundary rules + at least one rule per
   `category`), plus **curated bad rulebooks** (demographic-named `input_fields`, operator↔threshold
   mismatch) for the load-rejection tests. Static = reproducible by being checked in; all synthetic, no
   real PII. Distinct from the runtime production rulebook (Q3).
B) Generate rulebooks dynamically at test time only (harder to review; less stable).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — curated static YAML rulebook fixtures under rules_engine/tests/: a valid representative rulebook (boundary rules + ≥1 rule per category) plus curated bad rulebooks (demographic-named input_fields, operator↔threshold mismatch) for the load-rejection tests. Static = reproducible by being checked in; all synthetic, no real PII; distinct from the runtime production rulebook (Q3).

## Question 3 — Actual-rule-population scope (FD §7 schema-vs-data boundary)
The FD §7 defers the **bulk 25–40-rule population** to Code-Gen. What does **this unit's** Code-Gen author?

A) **Engine + schema + a MINIMAL representative rulebook** (the 4 boundary rules + ≥1 profile-backed rule
   per the 9 categories — enough to exercise every engine path and every `NFR-RULES-*`/FD assertion). The
   **full production 25–40-rule rulebook** (complete IRDAI clause set, occupation-risk table, health-flag
   catalogue) is a **dedicated data-authoring pass/deliverable**, deferred — the engine is generic, so the
   production rulebook is pure data over the same tested schema. *(Recommended — keeps this unit's Code-Gen
   about the invariant-bearing ENGINE, not bulk data entry.)*
B) **Engine + the full 25–40-rule production rulebook now** — author all production rules in this pass.
C) Other (please describe after [Answer]: tag below)

[Answer]: A — engine + schema + a MINIMAL representative rulebook (the 4 boundary rules + ≥1 profile-backed rule per the 9 categories — enough to exercise every engine path and every NFR-RULES-*/FD assertion). The full production 25–40-rule rulebook (complete IRDAI clause set, occupation-risk table, health-flag catalogue) is a dedicated data-authoring pass, deferred — the engine is generic, so the production rulebook is pure data over the same tested schema. This unit's Code-Gen is about the invariant-bearing ENGINE, not bulk data entry. Track the deferred production-rulebook authoring as an explicit follow-up item (like OOS-7) so it isn't lost.

## Question 4 — Load-rejection test-corpus (the CON-BR1 universal-quantifier)
How is the load-time rejection (BR1-1/SCHEMA-1) tested as a universal-quantifier property?

A) **Hypothesis strategies + curated bad rulebooks.** Hypothesis generates rules whose `input_fields`
   name **demographic paths** (`demographics.*`, name/gender/city) or **out-of-allowlist/unknown** fields
   → assert `load_rulebook` **rejects** (raises) for all; likewise **operator↔threshold-shape mismatches**
   → reject. Plus a small curated set of hand-authored bad rulebooks (Q2) as explicit regression anchors.
   The allowlist namespace is single-sourced.
B) A few hand-picked bad rules only (no property-based ∀ coverage).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — Hypothesis strategies + curated bad rulebooks. Hypothesis generates rules whose input_fields name demographic paths (demographics.*, name/gender/city) or out-of-allowlist/unknown fields → assert load_rulebook rejects (raises) for all; likewise operator↔threshold-shape mismatches → reject. Plus a small curated set of hand-authored bad rulebooks (Q2) as explicit regression anchors. Allowlist namespace single-sourced.

## Question 5 — Module placement + shared-utility reference
Confirm the package placement and the reference-not-own wiring.

A) **`backend/rules_engine/`** (package name `rules_engine`, underscore) with the 9 components mapped to
   modules (§1.3); it **imports** `backend/common/canon_ser.py` (via `RulebookCanonAdapter`, **unchanged**)
   and `backend/common/decimal_context.py` (via `DerivationFunctions`), and **imports intake's
   `ApplicantProfile`** from `backend.intake.schema` (read-only — **not re-declared**). The
   `RulebookCanonAdapter` is rules-engine-local. No shared-code edit.
B) A different placement / re-declare a shared utility (rejected — reference-not-own; would fork CANON-SER
   or the profile contract).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — backend/rules_engine/ (package name rules_engine, underscore), 9 components mapped to modules per §1.3; imports backend/common/canon_ser.py (via RulebookCanonAdapter, unchanged) and backend/common/decimal_context.py (via DerivationFunctions), and imports intake's ApplicantProfile from backend.intake.schema (read-only, not re-declared). RulebookCanonAdapter is rules-engine-local. No shared-code edit.

## Question 6 — Confirm the N/A step-categories (unit scope)
code-generation.md Step 2 lists API/Repository/Frontend/DB-migration step categories. Confirm N/A for this
pure-logic unit?

A) **Confirm N/A with justification** — **API Layer** = FastAPI orchestrator composition root; **Repository/
   persistence** = `audit-store` + `database`; **Frontend** = backend unit; **DB migrations** = `database`;
   **replay orchestration** = `audit-store` ReplayService (this unit provides only pure `evaluate` + a
   separable report). This unit generates **business logic + its tests + a code summary** only.
B) Some of these DO apply to this unit (describe which + why).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — confirm N/A with justification: API Layer = FastAPI orchestrator composition root; Repository/persistence = audit-store + database; Frontend = backend unit; DB migrations = database; replay orchestration = audit-store ReplayService (this unit provides only pure evaluate + a separable report). This unit generates business logic + its tests + a code summary only.

---

## 4. Story traceability
| Story | Covered by (steps) |
|---|---|
| US-RULES-1 (evaluate profile against versioned rulebook → report) | Steps 6, 7, 10, 11 |
| US-RULES-2 (boundary exactness — exact value + comparison) | Steps 7 (BND-1) |
| US-RULES-3 (recommendation enum, `-RECOMMEND`, thin-file→REFER) | Steps 8, 10, 11 |
| US-RULES-4 (immutable versioning + replay handle) | Steps 3, 6, 10 (content_hash/append-only/forensic-not-equality) |
| US-RULES-5 (occupation/income only via sanctioned rule; CON-BR1) | Steps 2, 5, 6 (load-reject + namespace exclusion) |

## 5. Constraints & settled items held (not re-opened)
- **Frozen C2 contract + FD + approved NFR targets + patterns + 9 components** are the inputs — Code-Gen
  implements them exactly; it re-opens none.
- **TDD binding**: tests FIRST, pytest-cov ≥ 90% (QA-6), on the pinned **Python 3.12**. No code this stage.
- **Reference-not-own**: shared CANON-SER (`backend/common/canon_ser.py`, unchanged via the adapter) +
  `decimal_context`; intake's `ApplicantProfile` imported read-only; observability stack / persistence /
  replay-orchestration / quality-gates verification owned elsewhere. **Infrastructure Design SKIPPED (logged)**.
- **Schema-vs-data**: the FD §7 deferral is honored — the production-rulebook authoring scope is decided
  at Q3, not assumed.
- Three settled non-edits stay closed: `PROJECT-BRIEF.md`, OOS-7 README/case-study doc commitment,
  `user-journey.md`.

---

## 6. Next step (STOP here)
Fill the six `[Answer]:` tags above. On your signal, I will read the answers, run the ambiguity-check
(adding a clarification file only if needed), then **execute Part 2 (Generation)** — writing the tests
FIRST, then the implementation, step-by-step per §2, and present the standardized 2-option completion
message. **NO code, NO tests, NO implementation is written until the answers are in and checked and you
give the explicit go.**
