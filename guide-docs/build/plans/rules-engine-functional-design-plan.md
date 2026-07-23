# Functional Design Plan — `rules-engine` (C2)

**Phase / Stage**: BUILD → Functional Design (per-unit, plan-then-generate)
**Cluster**: Deterministic-core cluster-FD-first — **unit 2 of 4** (`intake`+`document-sanitizer` ✅ approved 2026-07-03; **`rules-engine` ← here**; then `audit-store`, `memo-agent-core`; **all four FDs designed before any Code-Gen**).
**Unit covered**: U3 `rules-engine` (C2, Phase 1).
**Date**: 2026-07-03
**Status**: **Plan — awaiting `[Answer]:` tags.** No FD artifacts generated yet. Stop after this plan.

This plan follows `.project-guide-rule-details/build/functional-design.md`. It is the **altitude
drop to INTERNALS**: the versioned YAML rule-definition schema, the pure-Python evaluation +
recommendation-aggregation logic, the exact boundary operators, the DTI / income-multiple
derivations rules-engine **owns**, deterministic confidence banding, and the field-by-field
`RuleResultReport`. **The contract *shapes* are frozen at Application Design
(`component-methods.md` C2) — Functional Design fills the internals, it does NOT re-open the
contract shape.**

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 `rules-engine` (U3, C2, Phase 1)
- **Purpose**: Evaluate a validated `ApplicantProfile` against a **versioned YAML rulebook** with
  **pure Python, zero LLM**, and **produce the recommendation** (`APPROVE` / `REFER` /
  `DECLINE-RECOMMEND`) + a **deterministic `confidence`** (Low/Med/High), stamped with
  `rulebook_version`.
- **Modules** (`unit-of-work.md §3` U3): `rulebook-yaml` (versioned; story-less module),
  `rule-result-report`, `versioning/replay` (immutable published versions).
- **Stories**: US-RULES-1..5 (`unit-of-work-story-map.md`); gherkin ACs in `stories.md §3`.
- **Owned invariants** (`unit-of-work.md §5`): **CON-BR2** (the recommendation **originates here**,
  never in the LLM), **CON-DET-1** (no unseeded randomness / wall-clock / dict-order),
  **CON-BR1 enforcement facet** (rules operate on **financials/medical/lifestyle facts only**;
  occupation & income influence the outcome **only** via their sanctioned rule — occupation-risk /
  affordability — never as a demographic proxy; US-RULES-5). CON-BR1 **verification** stays
  single-sourced in `quality-gates` (U13) bias-swap — this is layered enforcement, not co-ownership.
- **Requirements**: FR-RULES-1 (25–40 rules in versioned YAML, pure Python, zero LLM), FR-RULES-2
  (Financial / Medical / Lifestyle domains incl. IRDAI 2024; occupation proxy carve-out),
  FR-RULES-3 (**exact triggering value + comparison `<=` vs `<`; boundaries land on the intended
  side**), FR-RULES-4 (per-rule pass/fail report stamped `rulebook_version`), FR-RULES-5
  (recommendation enum exactly `APPROVE`/`REFER`/`DECLINE-RECOMMEND`, mandatory `-RECOMMEND`
  suffix), FR-RULES-6 (published versions **immutable**; changes add a new version). Also
  **CON-AUDIT-1** (replay a past decision against its **original** `rulebook_version`).
- **Depth**: **comprehensive** (versioned schema, boundary/comparison correctness, replay,
  invariant-bearing) — `unit-of-work.md §3` U3.

### 1.2 Frozen contract shapes (from `component-methods.md` C2 — internals only below)
- `load_rulebook(version: str) -> Rulebook` — load a specific **immutable** rulebook version.
- `evaluate(profile: ApplicantProfile, rulebook_version: str) -> RuleResultReport` — pure-Python
  evaluation; **produces the recommendation**; stamps `rulebook_version`.
- `recommend(rule_results) -> Recommendation` — map evaluated results to the exact enum (**internal
  to `evaluate`**).
- `RuleResultReport` = per-rule pass/fail + each fired rule's **exact triggering value & comparison**;
  **carries `recommendation`**, the **deterministic `confidence`** (Low/Med/High, produced in the
  core), and `rulebook_version`.
- `Recommendation` = enum, exactly `APPROVE` / `REFER` / `DECLINE-RECOMMEND`.

### 1.3 Carry-forward from `intake` FD (unit 1 — held, not re-opened)
- **Reads the frozen `ApplicantProfile`** (intake's FD, now approved): `age_years_derived` and
  `bmi_derived` are **facts single-sourced in intake**; `verifiable_income_annual`,
  `existing_debt_obligations_annual`, `requested_cover_amount` are **operands intake supplies**;
  `application_id` is a **system-assigned** key; `demographics` is a **segregated sub-object
  rules-engine MUST NOT read** (CON-BR1).
- **Decimal convention (intake Q4)** propagates: DTI-ratio and income-multiple are computed in
  **`Decimal`** with exact threshold comparisons — never float on a value that hits a threshold.
- **Derivation-ownership split (intake Q5)**: rules-engine **OWNS** DTI-ratio and income-multiple
  (the rule-interpretation derivations); intake owned age + BMI (applicant facts). No field is
  double-owned.
- **Band decisions live HERE**: the 18–65 age band and 25/30 BMI band **pass/fail** decisions are
  rules-engine's; intake produced the reproducible values, rules-engine applies the comparison
  (**CON-BR2** — the recommendation originates entirely in C2).
- **`incomplete` flag**: intake sets it (thin-file / single-missing-doc / missing optional operand);
  rules-engine **routes those to REFER** (never a hard DECLINE on incompleteness alone).

### 1.4 Binding constraints held through this FD (guardrails skill)
- **CON-BR2**: recommendation produced **entirely** by deterministic Python; **no LLM anywhere in
  this path**; a test asserts the LLM cannot change a recommendation (QA-5, lives in `quality-gates`).
- **CON-DET-1 / reproducibility**: identical `(profile, rulebook_version)` ⇒ identical
  `RuleResultReport` every run — no wall-clock, no unseeded randomness, no dict-order reliance;
  rule evaluation order is deterministic.
- **CON-BR1 enforcement facet**: engine reads an **allowlisted financial/medical/lifestyle field
  set only**; occupation & income affect the outcome only via their one sanctioned rule each.
- **CON-AUDIT-1 / FR-RULES-6**: published versions are **immutable**; replay re-evaluates against
  the **original** version (never latest).
- **Advisory-only naming**: `recommendation` vocabulary throughout; `-RECOMMEND` suffix mandatory;
  "decision" reserved for the human-committed record (not produced here).

### 1.5 Cluster-FD-first downstream consumers of `RuleResultReport` (stabilize the contract now)
- **`audit-store` (U12)** persists `rule_results` in the audit 6-tuple and **replays** them
  (match/mismatch). The `RuleResultReport` field set must be **serializable + replay-comparable**.
- **`memo-agent-core` (U4)** cites **strictly from the handed `RuleResultReport`** (every fired
  rule ID, the exact value, `confidence`); it must not re-derive what fired. So the report must
  carry everything the memo needs to cite — designed here, before either unit's Code-Gen.
- **`outlier-model` (U18, P2)** is independent of the report (reads the profile), but the
  deterministic `confidence` half of the memo's borderline trigger (FR-MEMO-6) originates here.

### 1.6 Greenfield note
**No rulebook YAML exists yet** (workspace is greenfield). The **rule-definition schema is this
FD's to design** (not reverse-engineered). The concrete 25–40 rule instances are a Code-Gen /
data-authoring concern; this FD designs the **schema, evaluation semantics, and the canonical
boundary operators**, plus a representative rule set to prove the schema.

---

## 2. Functional Design execution plan (checkboxes — Step 2)

Artifacts to be generated **after** answers are collected and ambiguity-checked:
`guide-docs/build/rules-engine/functional-design/` → `domain-entities.md`, `business-rules.md`,
`business-logic-model.md`. (No `frontend-components.md` — backend unit.)

- [x] **P1. Analyze unit context** (§1 above — done).
- [x] **P2. Collect `[Answer]:` tags** (§3); run the mandatory ambiguity-check (§4 of the rule
  file); raise a clarification file only if any answer is vague/combined/contradictory. **DONE
  2026-07-03 — all 12 answered; ambiguity-check CLEAN (no clarification file needed); Q4 boundary
  conventions CONFIRMED against the underwriting-rules skill (age 18–65 inclusive, DTI ≤40% passes,
  BMI ≥25 overweight / ≥30 obese — exactly-30 triggers). 7 design-elaboration notes surfaced for
  generation (see audit 2026-07-03T10:50 entry). Awaiting explicit go to generate.**
- [x] **P3. `domain-entities.md`** — the YAML **rule-definition schema** (field-by-field: `rule_id`,
  `category`, operand/field reference, `comparison` operator, `threshold`, on-fire
  outcome-contribution/severity, human-readable description/message template), the `Rulebook`
  (versioned collection + `rulebook_version`), the field-by-field **`RuleResultReport`** and its
  per-rule `RuleResult` rows, the `Recommendation` enum, and the deterministic `confidence` enum.
  Entity-relationship view (Mermaid, validated per visual-and-syntax-standards, text alternative).
- [x] **P4. `business-rules.md`** — the **canonical boundary operators** (age `18`/`65`, BMI
  `25`/`30`, DTI `40%`, income-multiple) each stated as explicit `<=`/`<` with the boundary value
  on the intended side; the **DTI-ratio** and **income-multiple** derivation rules (Decimal,
  rounding, operand-missing behavior); the **recommendation-aggregation** rule (per-rule pass/fail
  → `APPROVE`/`REFER`/`DECLINE-RECOMMEND`, with precedence and the `incomplete`→REFER path); the
  **deterministic confidence-banding** rule; the CON-BR1 financials-only enforcement rule
  (occupation/income carve-out). Every rule states its comparison and boundary behavior explicitly.
- [x] **P5. `business-logic-model.md`** — the `load_rulebook → evaluate (iterate rules, collect
  RuleResult, aggregate recommendation, band confidence) → RuleResultReport` pipeline; the
  deterministic evaluation-order guarantee; the immutable-versioning + **replay** model and its
  **ownership boundary with `audit-store` ReplayService**; happy + edge flows (all-pass APPROVE,
  boundary case, incomplete→REFER, multi-fail→DECLINE-RECOMMEND); data-flow diagram (Mermaid,
  validated + text alternative).
- [x] **P6. Cross-consumer contract check** — verify the `RuleResultReport` field set covers every
  known downstream need (`audit-store` persistence/replay-comparability; `memo-agent-core`
  citation of every fired rule ID + exact value + confidence) so the report contract is **stable
  for the cluster** before any Code-Gen.
- [x] **P7. Guardrail compliance pass + present the standardized 2-option completion message**
  — **APPROVED at the gate 2026-07-03** (Continue to Next Stage → `audit-store` FD) after the
  review-beat correction set (category-population coverage §7 + operator↔threshold §2.1 + BMI
  DecimalRange inclusivity; smoking/occupation seam confirmed Case A, no intake back-edit).
  (CON-BR2 no-LLM-in-path, CON-DET-1 determinism, CON-BR1 financials-only, FR-RULES-6 immutability,
  advisory-only naming; record compliant/N/A per Security-Guardrails control). Then Request Changes
  / Continue to Next Stage → the next cluster unit's Functional Design, **`audit-store`**.

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and
describe. These decide **internals only** — the C2 contract shapes in §1.2 stay frozen.

### A. YAML rulebook — rule-definition schema & versioning

## Question 1 — Rule-definition schema (how a rule is expressed in YAML)
FR-RULES-1 requires 25–40 rules in versioned YAML evaluated by **pure Python, zero LLM**. How is a
single rule expressed so the engine interprets it **generically** (data-driven), keeping evaluation
deterministic and each rule self-describing for FR-RULES-3 (exact value + comparison)?

A) **Fully declarative schema** — each rule = `{ id, category, operand (a named field/derivation
   path on the profile, e.g. age_years_derived / bmi_derived / dti_ratio), comparison operator
   (<= / < / >= / > / == / in), threshold (Decimal or set), on-fire outcome-contribution
   (severity: hard-fail / soft-refer / pass-only), human description + message template }`. A
   **generic Python evaluator** reads operand + operator + threshold and records the exact value
   and comparison — no per-rule Python function. (Cleanest FR-RULES-3 traceability; new rules =
   data, not code.)
B) YAML holds **parameters only** (thresholds); each rule's logic is a hand-written Python
   function keyed by `rule_id`.
C) Hybrid — declarative for simple threshold rules, Python callables for a few composite rules.
D) Other (please describe after [Answer]: tag below)

[Answer]: Fully-structured-per-rule YAML schema — each rule an object with: id, category, input_fields (explicit list — the ONLY fields the rule may read), operator, threshold, outcome (pass / fail-decline / refer-trigger), rationale/message, irdai_ref. Rules are DATA, not code; the explicit input_fields list is what makes CON-BR1 structural (a rule can only read fields it names; demographic fields are unnameable).

## Question 2 — Immutable-version representation (FR-RULES-6, CON-AUDIT-1)
Published rule versions are immutable; changes add a new version; any past decision replays against
its original version. How is a rulebook version stored/identified?

A) **One immutable file/directory per version** (e.g. `rulebook/v1.yaml`, `rulebook/v2.yaml`),
   each stamped with its own `rulebook_version` string; `load_rulebook(version)` loads exactly that
   file; a published version is **never edited in place** (a new file is added). Optionally a
   content-hash recorded for tamper-evidence.
B) A single file with all versions embedded under version keys.
C) External version store / DB table keyed by version.
D) Other (please describe after [Answer]: tag below)

[Answer]: Immutable versioning = semantic version (human-readable, e.g. 1.2.0) + content hash (tamper-evident), frozen at load, append-only — a changed rulebook is a NEW version; old versions retained. rulebook_version is what CON-AUDIT-1 replay loads to re-evaluate against the ORIGINAL rules.

## Question 3 — Rule-category organization (FR-RULES-2, incl. IRDAI 2024)
Rules span Financial / Medical / Lifestyle (and IRDAI 2024 compliance). How is category modelled?

A) A `category` enum on each rule (`financial` / `medical` / `lifestyle` / `compliance_irdai`),
   used for grouping/reporting only — it does **not** change evaluation semantics; every rule is
   evaluated uniformly and each fired rule reports its category in the `RuleResultReport`.
B) Separate YAML files per category, loaded and merged.
C) Category is implicit (inferred from the operand), not stored.
D) Other (please describe after [Answer]: tag below)

[Answer]: Organize rules by underwriting domain/category (age-eligibility, medical/BMI, financial/DTI+income, document-completeness); carry the IRDAI reference as an inline field on each rule (irdai_ref), not a separate structure — so the regulatory basis travels with the rule for audit tracing.

### B. Evaluation, boundaries & recommendation

## Question 4 — Canonical boundary operators (FR-RULES-3 — the exact-threshold discipline)
Boundaries are first-class test cases (age 18/65, BMI 25/30, DTI 40%). The FD must pin each
comparison so a boundary value lands on the **intended** side. Which canonical set?

A) **Eligibility & bands (inclusive where the skill says "eligible window / ceiling"):**
   age **eligible iff `18 <= age_years_derived <= 65`** (exactly 18 and exactly 65 are IN-band);
   BMI bands **normal `bmi < 25`**, **overweight `25 <= bmi < 30`**, **obese `bmi >= 30`** (25.00
   → overweight, 30.00 → obese); DTI **pass iff `dti_ratio <= 0.40`** (exactly 40% passes);
   income-multiple **pass iff `income_multiple <= <ceiling>`**. All comparisons in `Decimal`; each
   fired rule records the exact value **and** the operator used.
B) Exclusive eligibility (`18 < age < 65`, `bmi < 25` … `bmi > 30`, `dti < 0.40`).
C) Mixed per rule — define individually with no single convention.
D) Other (please describe after [Answer]: tag below)

[Answer]: Explicit operator + inclusivity stated PER THRESHOLD in the YAML (never implicit in code). Recommended conventions, TO BE CONFIRMED against IRDAI/underwriting convention via the underwriting-rules skill: age eligible if >=18 AND <=65 (both bounds inclusive); DTI acceptable if <=40% (exactly 40% passes); BMI thresholds stated with explicit inclusivity at 25 and 30 (confirm whether exactly 30 triggers the flag). Every boundary has ONE deterministic encoded answer — this is the exact-threshold discipline the boundary test suite checks.

## Question 5 — Recommendation-aggregation logic (per-rule pass/fail → the enum, FR-RULES-5)
How do the collected per-rule results map to exactly `APPROVE` / `REFER` / `DECLINE-RECOMMEND`?

A) **Severity-tiered aggregation with explicit precedence** — each rule declares a severity
   (`hard-fail` / `soft-refer` / `pass`). Precedence: **any `hard-fail` (or ≥ N hard fails) →
   `DECLINE-RECOMMEND`**; **else any `soft-refer`, any borderline-band hit, OR `profile.incomplete`
   → `REFER`**; **else all clear → `APPROVE`**. Deterministic, order-independent, fully traceable
   (the memo can cite exactly which rule(s) drove the tier). `-RECOMMEND` suffix mandatory.
B) Weighted numeric score summed across fired rules with two cut points.
C) A decision-table keyed on category-level fail counts.
D) Other (please describe after [Answer]: tag below)

[Answer]: Deterministic aggregation by fixed precedence, order-independent (CON-DET-1): any DECLINE-level rule fails → DECLINE-RECOMMEND; else any refer-trigger OR incomplete-profile flag → REFER; else APPROVE. Safety-conservative (decline dominates).

## Question 6 — `incomplete`-profile routing (CON-BR2 carry-forward, FR-INTAKE-3 ↔ rules)
intake sets `profile.incomplete=true` for thin-file / single-missing-document / missing optional
operand. How does rules-engine treat it?

A) **`incomplete=true` (or a required rule-operand unavailable, e.g. `existing_debt_obligations`
   absent so DTI is un-computable) contributes a `soft-refer` → the profile routes to `REFER`, not
   a hard `DECLINE-RECOMMEND`.** Thin-file / single-missing-doc never hard-declines on
   incompleteness alone (skill: thin-file → REFER). A rule whose operand is missing reports
   `not-evaluated` (never a silent pass/fail).
B) Missing operand → treat the rule as failed (fail-closed).
C) Missing operand → skip the rule silently and evaluate the rest.
D) Other (please describe after [Answer]: tag below)

[Answer]: intake's `incomplete` flag → treated as a distinct REFER-trigger in aggregation (insufficient-information REFER), NOT a rule pass/fail. Keeps the intake→rules boundary clean: intake flags the fact, rules-engine interprets it as REFER.

## Question 7 — Deterministic `confidence` banding (Low/Med/High — produced HERE, in the core)
`RuleResultReport` carries a **deterministic** `confidence` (per Application Design: produced in the
core, read-only to the memo). How is it derived, purely and reproducibly?

A) **Deterministic function of threshold-proximity + completeness** — `confidence` is a pure
   function of how close the driving values sit to their nearest thresholds (margin) and whether the
   profile is `incomplete`: e.g. clear pass/fail with wide margins + complete docs → **High**;
   near-boundary values (within a versioned margin) or a single incompleteness → **Medium**;
   multiple borderline hits or material incompleteness → **Low**. No randomness, no wall-clock; the
   margin thresholds live in the versioned rulebook so confidence replays exactly.
B) Fixed mapping from the recommendation only (APPROVE→High, REFER→Medium, DECLINE→High).
C) Confidence is deferred to the memo agent (C4).  *(Note: conflicts with the Application Design
   decision that confidence is produced deterministically in the core — flagged for you.)*
D) Other (please describe after [Answer]: tag below)

[Answer]: Deterministic confidence = a function of rule-margin/proximity to thresholds (comfortable pass on all rules → high; near a boundary → low), banded (high/medium/low), computed IN rules-engine, never the LLM (realizes reviewer G2). Band thresholds are themselves deterministic constants (confirm they're fixed, not arbitrary), so same inputs → same confidence on replay.

### C. Owned derivations — DTI ratio & income-multiple (Decimal, owned here per intake Q5)

## Question 8 — DTI-ratio derivation (owned by rules-engine)
DTI is the affordability ceiling (`<= 40%`). intake supplies the operands
(`existing_debt_obligations_annual`, `verifiable_income_annual`) but **not** the ratio. How is it
computed and compared?

A) **`dti_ratio = existing_debt_obligations_annual / verifiable_income_annual` in `Decimal`**,
   compared **`dti_ratio <= Decimal("0.40")`** to pass; a declared quantization (e.g. 4 dp,
   `ROUND_HALF_UP`) so the 40% boundary is exact and replayable; **income = 0 or the debt operand
   absent → the rule is `not-evaluated` and contributes `soft-refer` (REFER)**, never a divide
   error or silent pass. The fired rule reports the exact computed ratio + the `<=` comparison.
B) Compute in float, compare `<= 0.40`.
C) Compute as an integer percentage (0–100) and compare `<= 40`.
D) Other (please describe after [Answer]: tag below)

[Answer]: DTI-ratio owned by rules-engine (Q5 ownership), Decimal: total_debt_obligations / income. Operand missing (no income or no debt figure) → cannot-compute → contributes to incomplete→REFER, never a fabricated ratio.

## Question 9 — Income-multiple derivation + its threshold (owned by rules-engine)
Income-multiple compares requested cover/loan vs verifiable income. How is it computed, and where
does its ceiling live?

A) **`income_multiple = requested_cover_amount / verifiable_income_annual` in `Decimal`**, compared
   **`income_multiple <= <ceiling>`** to pass, where **`<ceiling>` is a versioned rule parameter in
   the YAML rulebook** (not hardcoded in Python) so it can change only via a new rulebook version
   (FR-RULES-6); income = 0 → `not-evaluated` → `soft-refer` (REFER). The fired rule reports the
   exact multiple + comparison + the threshold from that rulebook version.
B) Hardcode a fixed multiple ceiling in the engine.
C) Derive the ceiling dynamically from other profile fields.
D) Other (please describe after [Answer]: tag below)

[Answer]: income-multiple owned by rules-engine, Decimal: requested_cover / income. The acceptable-multiple CEILING is a YAML rule threshold (tunable, versioned, auditable), NOT a hardcoded constant.

### D. `RuleResultReport` internals, replay boundary & CON-BR1

## Question 10 — `RuleResultReport` field-by-field (the cluster-stable contract)
What does the report carry, so `audit-store` can persist/replay it and `memo-agent-core` can cite
strictly from it (FR-RULES-3/4, CON-AUDIT-1, FR-MEMO-3)?

A) **A list of per-rule `RuleResult` rows** — each `{ rule_id, category, status (pass / fail /
   not-evaluated), applicant_value (the exact triggering value, Decimal/typed), comparison
   (operator + threshold), severity, message }` — **plus top-level** `recommendation`,
   deterministic `confidence`, `rulebook_version`, and an `engine_version` hook (git SHA of the
   engine, per the audit 6-tuple, for code-drift detection on replay). Fully serializable and
   **replay-comparable** (a replay re-evaluates and compares `rule_results`).
B) Only the fired (failing) rules + the recommendation (drop passes).
C) A flat map of `rule_id → bool` + the recommendation.
D) Other (please describe after [Answer]: tag below)

[Answer]: RuleResultReport carries: per-rule results (id, pass/fail, actual_value vs threshold), the aggregate recommendation, the deterministic confidence band, rulebook_version (for replay), and structured decline/refer reasons. This is the sole thing the memo grounds on (G6 — memo cites ONLY from this report) and what audit persists.

## Question 11 — Replay ownership boundary (rules-engine ↔ `audit-store` ReplayService)
`services.md §4` shows `ReplayService` (owned by `audit-store`, U12) calling C2 to re-evaluate a
past decision against its **original** `rulebook_version`, then branching match/mismatch. What does
**rules-engine** own vs `audit-store`?

A) **rules-engine owns pure, stateless re-evaluation**: `load_rulebook(original_version)` +
   `evaluate(profile, original_version)` returns a fresh `RuleResultReport` — deterministic, no
   knowledge of history. **`audit-store`'s `ReplayService` owns** fetching the `AuditRecord`,
   invoking the re-evaluation, and the **match/mismatch comparison + blocking-failure flag**. Clean
   split: C2 re-computes, audit-store compares. (`engine_version` distinguishes engine code drift
   from a real regression.)
B) rules-engine owns the whole replay incl. the match/mismatch comparison against stored results.
C) audit-store re-implements evaluation for replay (no C2 call).
D) Other (please describe after [Answer]: tag below)

[Answer]: Clean split — rules-engine owns pure deterministic evaluate(profile, rulebook_version); audit-store's ReplayService owns replay ORCHESTRATION (loads original rulebook_version + profile, CALLS evaluate to re-derive, compares to recorded result). rules-engine does not own "replay" as a concept; replay USES its evaluation.

## Question 12 — CON-BR1 structural demographic-exclusion (financials-only enforcement)
The engine must never let name/gender/city (the segregated `demographics` sub-object) influence a
result, and occupation/income must act only via their sanctioned rule (US-RULES-5). How is this
enforced structurally in the FD?

A) **The evaluator reads operands only from an explicit allowlist of financial/medical/lifestyle
   fields** (`age_years_derived`, `bmi_derived`, incomes, debt, requested cover, employment_type,
   smoking_status, occupation, health_flags, documents) and is **structurally never handed the
   `demographics` sub-object**; occupation & income appear as operands of exactly **one** sanctioned
   rule each (occupation-risk / affordability) and nowhere else. CON-BR1 holds **by construction**;
   `quality-gates` bias-swap remains the single verification owner (delta = 0, blocking).
B) Pass the whole profile but rely on rule authors not referencing demographics.
C) Strip demographics into a separate object only at test time.
D) Other (please describe after [Answer]: tag below)

[Answer]: CON-BR1 structural — the engine reads ONLY fields explicitly named in a rule's input_fields (Q1). Demographic fields live in the segregated sub-object (intake Q1) and are therefore unnameable/unreachable by any rule — demographic exclusion true by construction, not by filter. occupation/income influence outcome only via their sanctioned rules (US-RULES-5).

---

## 4. Constraints & settled items held (not re-opened)
- C2 contract **shapes** frozen at Application Design (`component-methods.md`) — FD fills internals
  only (`load_rulebook` / `evaluate` / `recommend`; `RuleResultReport` / `Recommendation`).
- Cluster-FD-first: this is unit 2 of 4; the `RuleResultReport` field-level contract must be stable
  across the cluster (`audit-store`, `memo-agent-core`) before any Code-Gen.
- Carry-forwards from intake FD (§1.3) held: Decimal for DTI/income-multiple; Q5 derivation
  ownership (rules-engine owns DTI-ratio + income-multiple; intake owned age + BMI); reads the
  frozen `ApplicantProfile` (application_id system-assigned; existing_debt operand; demographics
  segregated + NOT read); 18–65 & 25/30 band pass/fail decided here (CON-BR2).
- Guardrails (§1.4): CON-BR2 (no LLM in path), CON-DET-1 (determinism), CON-BR1 (financials-only),
  FR-RULES-6 / CON-AUDIT-1 (immutable versions + replay), advisory-only naming (`-RECOMMEND`).
- Three settled non-edits stay closed: `PROJECT-BRIEF.md`, OOS-7 doc commitment, `user-journey.md`.

---

## 5. Next step (STOP here)
Fill the twelve `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory
ambiguity-check (adding a clarification file only if needed), then generate the three rules-engine
Functional Design artifacts and present the 2-option completion message. **No FD artifacts or code
are generated until the answers are in and checked.**
