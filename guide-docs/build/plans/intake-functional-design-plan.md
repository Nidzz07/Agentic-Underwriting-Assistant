# Functional Design Plan — `intake` + `document-sanitizer` (coupled pair)

**Phase / Stage**: BUILD → Functional Design (per-unit, plan-then-generate)
**Cluster**: Deterministic-core cluster-FD-first — unit 1 of 4 (`intake`+`document-sanitizer`, then `rules-engine`, `audit-store`, `memo-agent-core`; **all four FDs designed before any Code-Gen**).
**Units covered**: U1 `intake` (primary) + U2 `document-sanitizer` (coupled pair — same FD pass).
**Date**: 2026-07-03
**Status**: **Plan — awaiting `[Answer]:` tags.** No FD artifacts generated yet. Stop after this plan.

This plan follows `.project-guide-rule-details/build/functional-design.md`. It is the
**altitude drop to INTERNALS**: field-by-field `ApplicantProfile` schema, the `SanitizedText`
contract, the SEC-2 validation-gate field rules, and `RejectedIntake`'s shape. **The contract
*shape* is frozen at Application Design (`component-methods.md`) — Functional Design fills the
internals, it does NOT re-open the contract shape.**

---

## 1. Unit context (analyzed — Step 1)

### 1.1 `intake` (U1, C1, Phase 1) — primary
- **Purpose**: Turn an application form + supporting documents into one validated, typed
  `ApplicantProfile`, or reject at the Pydantic gate **before any agent runs**.
- **Modules**: `intake-parser` (pdfplumber), `applicant-profile-schema` (Pydantic v2),
  `intake-validation-gate`.
- **Stories**: US-INTAKE-1, US-INTAKE-2, US-INTAKE-3 (`unit-of-work-story-map.md` rows 1–3).
- **Owned invariant**: **SEC-2** (input-validation gate — single source, `unit-of-work.md §5`).
- **Requirements**: FR-INTAKE-1 (parse → validated `ApplicantProfile`), FR-INTAKE-2 (pdfplumber
  + Pydantic v2; malformed rejected at the gate before agent entry), FR-INTAKE-3 (single-missing-doc
  and thin-file remain **processable → route toward REFER, not hard failure**), DATA-4 (zero real PII).
- **Depth**: `applicant-profile-schema` **comprehensive** (new data model, propagates furthest);
  parser/gate standard→comprehensive.

### 1.2 `document-sanitizer` (U2, C1 / SEC-1, Phase 1) — coupled
- **Purpose**: Neutralise prompt-injection text extracted from documents so hidden instructions
  never reach the memo agent as commands. Security boundary, independently owned/tested.
- **Stories**: US-INTAKE-4 (`unit-of-work-story-map.md` row 4).
- **Owned invariant**: **SEC-1** (injection defense — single source, `unit-of-work.md §5`).
- **Requirements**: SEC-1, failure mode #4 (prompt injection).
- **Depth**: **comprehensive** (security-critical).

### 1.3 Why coupled (one FD pass, two units, two invariants)
The pipeline is **parse → SANITIZE (SEC-1) → Pydantic gate (SEC-2) → `ApplicantProfile`**
(`unit-of-work-dependency.md §2`, F5a). The sanitizer's output text-contract (`SanitizedText`)
feeds intake's SEC-2 gate, so the gate's field rules are designed against what the sanitizer
hands it — they must be designed together. **Ownership stays split**: SEC-1 lives only in
`document-sanitizer`, SEC-2 only in `intake`; coupling the design pass does not merge ownership.

### 1.4 Frozen contract shapes (from `component-methods.md` C1 — internals only below)
- `parse(documents: list[Document]) -> ApplicantProfile` (or rejection at the gate)
- `sanitize(raw_text: str) -> SanitizedText`
- `validate_gate(extracted) -> ApplicantProfile | RejectedIntake`
- `ApplicantProfile` = "the single input downstream steps trust." Downstream consumers whose
  field needs must be covered: **`rules-engine`** (reads age, BMI, DTI inputs, income, requested
  cover/loan, employment-type, document-completeness, medical/lifestyle flags — FR-RULES + Brief
  §2/§4 + skill rule categories), **`outlier-model`** (P2 feature vector — demographic-EXCLUDED,
  CON-BR1), **`memo-agent-core`** (reads profile read-only for prose).

### 1.5 Binding constraints held through this FD (guardrails skill)
- **CON-BR1 / bias-free**: demographic identifiers (name, gender, city) must be structurally
  isolated so they can never influence a rule outcome or the feature vector; bias-swap delta = 0.
- **CON-DET-1 / reproducibility**: no wall-clock, no unseeded randomness, no dict-order reliance
  in any derived field (age-from-DOB and BMI derivation are the live risks — see Q4/Q5).
- **CON-BR2**: intake does **not** emit a recommendation; incomplete/thin-file profiles are
  flagged and the **rules-engine** routes them to REFER (recommendation origin stays in C2).
- **Advisory-only naming**: field/enum/error names use "recommendation" vocabulary; "decision"
  is reserved for the human-committed record (not produced by intake).
- **DATA-4**: synthetic/mock data only — zero real PII at any stage.

---

## 2. Functional Design execution plan (checkboxes — Step 2)

Artifacts to be generated **after** answers are collected and ambiguity-checked:
`guide-docs/build/intake/functional-design/` → `business-logic-model.md`, `business-rules.md`,
`domain-entities.md`. (No `frontend-components.md` — both units are backend.)

- [x] **P1. Collect `[Answer]:` tags** below; run the mandatory ambiguity-check (§4 of the rule
  file); raise a clarification file if any answer is vague/contradictory.
- [x] **P2. `domain-entities.md`** — field-by-field internals of the frozen contracts:
  `ApplicantProfile` (every field: name, type, unit, required/optional, derived-vs-raw,
  demographic-segregation boundary, value ranges), the `Document` manifest, `SanitizedText`,
  `RejectedIntake`. Entity-relationship view (Mermaid, validated per visual-and-syntax-standards).
- [x] **P3. `business-rules.md`** — SEC-2 gate field-level validation rules; required-primitive
  set vs optional-and-flagged; the **reject-at-gate vs processable-REFER boundary** (FR-INTAKE-3);
  deterministic age/BMI derivation rules; SEC-1 sanitization/neutralization rules and what gets
  logged. Every rule states its comparison explicitly and its boundary behaviour.
- [x] **P4. `business-logic-model.md`** — the parse → sanitize → gate pipeline logic; sanitizer
  neutralization algorithm; happy path + unhappy path (`RejectedIntake`) aligned to `services.md
  §6` Scenario-1; data-flow diagram (Mermaid, validated).
- [x] **P5. Cross-consumer field-need check** — verify the `ApplicantProfile` field set covers
  every known downstream need (rules/outlier/memo) so the field-level contract is **stable for
  the whole cluster** before any Code-Gen (the cluster-FD-first rationale).
- [x] **P6. Guardrail compliance pass** — CON-BR1 demographic isolation, CON-DET-1 no wall-clock,
  CON-BR2 no recommendation in intake, advisory-only naming, DATA-4. Record compliant/N/A per
  Security-Guardrails control (SEC-1, SEC-2).
- [x] **P7. Present the standardized 2-option completion message** (Request Changes / Continue to
  Next Stage → the next cluster unit's Functional Design, `rules-engine`). **APPROVED at the gate
  2026-07-03** (Continue to Next Stage) after the review-beat correction set (4 diffs) + the
  services.md §6 Mermaid semicolon fix; user rendered §6 and confirmed it displays correctly.

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and
describe. These decide **internals only** — the contract shapes in §1.4 stay frozen.

### A. Domain model — `ApplicantProfile` field-by-field schema

## Question 1 — Demographic-identifier segregation (CON-BR1)
Name / gender / city must be captured (the bias-swap suite swaps them across identical
financials) but must **never** influence a rule outcome or the feature vector. How should they
sit in `ApplicantProfile`?

A) A separate nested `demographics` sub-object, structurally segregated from the
   financial/medical/lifestyle fields the rules and feature vector read (clearest boundary; a
   consumer must opt in to touch it)
B) Flat top-level fields, excluded by an explicit allowlist enforced at feature-vector / rule-input
   build time
C) Not stored on `ApplicantProfile` at all — injected only by the bias-swap test harness
D) Other (please describe after [Answer]: tag below)

[Answer]: A — nested `demographics` sub-object, structurally segregated so rules and the feature-vector builder never reach into it (CON-BR1 true by construction, not by allowlist discipline). The bias-swap suite swaps within this sub-object across identical financials.

## Question 2 — Age representation & determinism (CON-DET-1)
Age drives the 18–65 band (boundaries at exactly 18 and 65). Deriving age from a birth date
against "today" is wall-clock-dependent — a reproducibility risk. How is age modelled?

A) Store `date_of_birth` + an explicit `as_of_date` (application/submission date captured in
   intake) and derive integer age deterministically from those two — no wall-clock anywhere
B) Store an integer `age` field directly on the profile (no DOB); intake trusts the provided age
C) Store `date_of_birth` and derive age against the application timestamp at evaluation time
D) Other (please describe after [Answer]: tag below)

[Answer]: A — store `date_of_birth` + an explicit `as_of_date` (application/submission date captured at intake); derive integer age deterministically from those two, no wall-clock anywhere (CON-DET-1; keeps the 18/65 boundary reproducible on replay).

## Question 3 — BMI representation (medical band, boundaries 25 / 30)
BMI bands trip at exactly 25 and 30. How is BMI represented so the boundary is exact and
single-sourced?

A) Store raw `height` + `weight`, derive BMI **deterministically in intake** (single source,
   fully auditable), store the derived BMI too
B) Store a provided `bmi` value directly (trust the source document)
C) Store raw height + weight **and** a provided BMI, with a validation that they agree
D) Other (please describe after [Answer]: tag below)

[Answer]: A — store raw `height` + `weight`, derive BMI deterministically in intake (single-sourced, auditable), store the derived BMI too (exact 25/30 boundaries, single source).

## Question 4 — Monetary/numeric type for threshold-exact comparisons
DTI (≤ 40%), income multiples, and requested cover/loan are compared at exact thresholds. Float
comparisons risk boundary drift. What numeric representation for money?

A) `Decimal` (fixed-point) for all monetary values; never float for values that hit a threshold
B) Integer minor units only (paise/cents) across the board
C) Float (accept standard IEEE behaviour)
D) Other (please describe after [Answer]: tag below)

[Answer]: A — `Decimal` (fixed-point) for all monetary values and threshold-compared ratios; never float for any value that hits a rule threshold (exact-boundary correctness for DTI ≤40%, income multiples — serves the brief's exact-threshold boundary testing).

## Question 5 — Derived-field ownership across the cluster
Which derivations does **intake** compute-and-store (single-sourced for all consumers) vs. leave
to `rules-engine`? (Stabilizing this now is the point of cluster-FD-first.)

A) Intake stores stable primitives multiple consumers need — BMI (from height/weight), age (from
   DOB + as_of_date) — and leaves **rule-specific** derivations (DTI ratio, income-multiple) to
   `rules-engine`
B) Intake stores raw inputs only; every consumer derives everything itself (incl. BMI, age)
C) Intake computes **all** derivations including DTI ratio and income-multiple, and stores them
D) Other (please describe after [Answer]: tag below)

[Answer]: A — intake computes-and-stores the stable cross-consumer applicant primitives (BMI from height/weight, age from DOB+as_of_date) and leaves rule-specific derivations (DTI ratio, income-multiple) to rules-engine. Applicant-facts single-sourced in intake; rule-interpretation logic stays in C2.

### B. Document model & completeness

## Question 6 — Document-completeness modelling (FR-INTAKE-2/3)
Three supporting doc types matter: salary slip, bank statement, medical questionnaire.
Completeness feeds the rules (document-completeness check) and the thin-file/single-missing REFER
path. How is it modelled on the profile?

A) An explicit `documents` manifest: per-expected-type status
   (`present` / `parsed` / `missing` / `unparseable`) — completeness is a first-class field the
   rules read and the audit trail records
B) A set of booleans, one presence flag per document type
C) A list of successfully-parsed documents only (missing = simply absent from the list)
D) Other (please describe after [Answer]: tag below)

[Answer]: A — explicit `documents` manifest with per-expected-type status (present / parsed / missing / unparseable); completeness is a first-class field the rules read and the audit trail records (feeds the document-completeness check and the thin-file/single-missing REFER path).

### C. `document-sanitizer` (SEC-1) — sanitization internals

## Question 7 — Neutralization behaviour on suspected injection (SEC-1)
When injection-bearing / instruction-like text is detected in an uploaded document, what does the
sanitizer do?

A) **Neutralize** (strip/defang suspected instruction patterns) and pass cleaned text forward —
   never hard-fail on suspicion — logging what was neutralized so the audit trail records the
   attempt (injection can't reach the memo agent as a command)
B) **Reject** the whole intake (`RejectedIntake`) when injection patterns are detected
C) **Escape/encode** suspicious spans so they are inert but preserved verbatim for audit/forensics
D) Other (please describe after [Answer]: tag below)

[Answer]: A — neutralize (strip/defang suspected instruction patterns) and pass cleaned text forward, never hard-fail on suspicion, logging what was neutralized to the audit trail. (Note: preserve the original suspicious span in the sanitization report for forensics alongside the neutralized text.)

## Question 8 — Sanitization scope (which text is sanitized)
Sanitization sits before the SEC-2 gate. What text does it act on?

A) Only the free-text / narrative fields (e.g. medical-questionnaire notes) that can flow toward
   the LLM memo; numeric/structured fields bypass sanitization (the SEC-2 gate validates those)
B) The entire raw extracted text blob, before any field extraction
C) All string-typed fields after extraction
D) Other (please describe after [Answer]: tag below)

[Answer]: A — sanitize only the free-text/narrative fields that can flow toward the LLM memo (e.g. medical-questionnaire notes); numeric/structured fields bypass sanitization and are validated by the SEC-2 Pydantic gate.

## Question 9 — `SanitizedText` contract content (what the gate receives)
What does `SanitizedText` carry from sanitizer to gate?

A) A typed wrapper: sanitized text **+ a per-document sanitization report** (what was neutralized,
   where) so the audit trail can record injection attempts
B) Plain sanitized text only
C) Sanitized text + a single boolean `was_modified` flag
D) Other (please describe after [Answer]: tag below)

[Answer]: A — typed wrapper: sanitized text + a per-document sanitization report (what was neutralized, where, and the original span for forensics), so the audit trail records injection attempts.

### D. SEC-2 validation gate & error handling

## Question 10 — Reject-at-gate vs processable-REFER boundary (FR-INTAKE-3, CON-BR2)
Where is the line between "reject at the gate" and "valid but incomplete → REFER"?

A) The gate rejects **only structurally unrecoverable** input (unparseable PDF, missing required
   identity/financial primitives); **thin-file and single-missing-document produce a VALID
   `ApplicantProfile` flagged `incomplete`**, which `rules-engine` routes to REFER — intake never
   decides REFER itself (keeps recommendation origin in C2, CON-BR2)
B) The gate rejects any profile missing any expected document
C) Intake emits a preliminary REFER for incomplete profiles
D) Other (please describe after [Answer]: tag below)

[Answer]: A — the gate rejects only structurally unrecoverable input (unparseable PDF, missing required identity/financial primitives); thin-file and single-missing-document produce a VALID `ApplicantProfile` flagged `incomplete`, which rules-engine routes to REFER. Intake never emits a recommendation (CON-BR2 — recommendation origin stays in C2).

## Question 11 — Required-primitive set (the hard-gate minimum)
Which fields are the minimum required primitives, absent which the gate **rejects** (vs
optional-and-flagged)?

A) Required: age/DOB (+ as_of_date), income, requested cover/loan amount, and applicant identity
   linkage; everything else optional-and-flagged
B) Required: the full Brief §4 field set (strict — any missing field rejects)
C) Required: only a parseable document set (field-completeness handled downstream)
D) Other (please describe after [Answer]: tag below)

[Answer]: A — required primitives: age/DOB (+as_of_date), income, requested cover/loan amount, and applicant identity linkage; everything else optional-and-flagged (feeds the incomplete→REFER path, honoring FR-INTAKE-3).

## Question 12 — `RejectedIntake` shape (what a gate rejection returns)
What does `RejectedIntake` carry?

A) Structured: per-field validation errors + a top-level reason category
   (`malformed` / `unparseable` / `missing-required`); **no partial `ApplicantProfile` leaks
   downstream**
B) A single human-readable error-message string
C) The partial profile captured so far + the errors (so a UI could show what was extracted)
D) Other (please describe after [Answer]: tag below)

[Answer]: A — structured `RejectedIntake`: per-field validation errors + a top-level reason category (malformed / unparseable / missing-required); no partial `ApplicantProfile` leaks downstream.

---

## 4. Constraints & settled items held (not re-opened)
- Contract **shapes** frozen at Application Design (`component-methods.md`) — FD fills internals only.
- SEC-1 (`document-sanitizer`) / SEC-2 (`intake`) single-sourced; two units, one pipeline pass.
- Cluster-FD-first: this is unit 1 of 4; the field-level `ApplicantProfile` contract must be
  stable across the cluster before any Code-Gen.
- Guardrails: CON-BR1, CON-DET-1, CON-BR2, advisory-only naming, DATA-4 (§1.5).
- Three settled non-edits stay closed: PROJECT-BRIEF.md, OOS-7 doc commitment, user-journey.md.

---

## 5. Next step (STOP here)
Fill the twelve `[Answer]:` tags above. On your signal, I will read the answers, run the
mandatory ambiguity-check (adding a clarification file only if needed), then generate the three
Functional Design artifacts and present the 2-option completion message. **No FD artifacts or
code are generated until the answers are in and checked.**
