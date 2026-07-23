# Business Rules — `rules-engine` (C2)

**Stage**: BUILD → Functional Design (per-unit) · cluster-FD-first unit 2 of 4
**Unit**: U3 `rules-engine` (evaluation semantics, boundary conventions, owned derivations,
aggregation, confidence banding)
**Date**: 2026-07-03
**Scope**: Every rule's evaluation logic with **explicit operator + domain-confirmed inclusivity**
at each boundary; the DTI-ratio & income-multiple `Decimal` derivations (rules-engine-owned); the
aggregation precedence; incomplete→REFER; deterministic confidence banding. Technology-agnostic.

**Invariants held**: CON-BR2 (recommendation originates here, no LLM), CON-DET-1 (deterministic,
order-independent, Decimal not float), CON-BR1 (financials-only via `input_fields`), FR-RULES-6 /
CON-AUDIT-1 (immutable versions + replay), advisory-only naming (`-RECOMMEND` mandatory).

> **Domain confirmation (underwriting-rules skill, 2026-07-03):** age eligible `18 <= age <= 65`
> (both inclusive); DTI acceptable `dti_ratio <= 0.40` (exactly 40% passes); BMI bands `normal <25`,
> `overweight 25 <= bmi < 30`, `obese >= 30` (**exactly 25 → overweight; exactly 30 → obese**). All
> comparisons in `Decimal`.

---

## 1. Canonical boundary conventions (FR-RULES-3 — the exact-threshold discipline)

Each boundary has **one** deterministic encoded operator + inclusivity, stated in the rule's
`operator`/`threshold` (never implicit in code). The boundary value lands on the **intended** side;
the boundary test suite asserts exactly these.

| Rule (category) | Operand | PASS condition (explicit) | Boundary behaviour (exact) |
|---|---|---|---|
| **Age eligibility** (`age_eligibility`) | `age_years_derived` (int, from intake) | eligible iff **`18 <= age_years_derived <= 65`** | **18 → eligible; 65 → eligible** (both inclusive). `17 → not eligible`; `66 → not eligible`. |
| **BMI band** (`medical_bmi`) | `bmi_derived` (Decimal, from intake) | band = **normal `bmi < 25`**, **overweight `25 <= bmi < 30`**, **obese `bmi >= 30`** | **`25.00` → overweight** (not normal); **`30.00` → obese** (triggers the obese flag). |
| **DTI affordability** (`financial_dti`) | `dti_ratio` (Decimal, derived §2.1) | pass iff **`dti_ratio <= Decimal("0.40")`** | **`0.40` (exactly 40%) → pass**; `0.4001 → fail`. |
| **Income multiple** (`financial_income_multiple`) | `income_multiple` (Decimal, derived §2.2) | pass iff **`income_multiple <= ceiling`** where `ceiling` is a **YAML rulebook threshold** | boundary is `income_multiple == ceiling → pass`; ceiling value is versioned data, not hardcoded (Q9). |

> **Encoding** (each operator + inclusivity explicit, consistent with `domain-entities.md §2.1`):
> age eligibility uses `operator=between` with
> `threshold={low:18, low_inclusive:true, high:65, high_inclusive:true}` (**both ends inclusive**).
> BMI is expressed as three explicit band rules — **normal** `operator=lt, threshold=25`;
> **overweight** `operator=between, threshold={low:25, low_inclusive:true, high:30, high_inclusive:false}`
> (i.e. `25 <= bmi < 30`); **obese** `operator=gte, threshold=30`. DTI uses `operator=lte,
> threshold=0.40`; income-multiple uses `operator=lte, threshold=<ceiling>`. All thresholds are
> `Decimal`. The band an applicant lands in maps to an `outcome` tier in the rule data (e.g. obese →
> `refer_trigger` or `decline_fail` per the authored rulebook — that mapping is rule *data*, §5 /
> domain-entities §7, not fixed here).

> **CON-BR2 boundary note**: intake produced the reproducible **facts** (`age_years_derived`,
> `bmi_derived`); the **pass/fail band decision is made HERE**. Intake never applied `>= 18` /
> `>= 25` — those comparisons originate in rules-engine.

---

## 2. Owned derivations (Q5 — Decimal, rules-engine-owned)

### DR-DTI — DTI ratio
- **`dti_ratio = existing_debt_obligations_annual / verifiable_income_annual`**, computed in
  `Decimal`.
- **Quantization**: quantize to **4 decimal places, `ROUND_HALF_UP`** (single declared mode) so the
  `0.40` boundary is exact and replayable. No float at any step (Q4/Q8).
- **Operand-missing / un-computable** (Q8, note 3): if `verifiable_income_annual` is `0` or absent,
  or `existing_debt_obligations_annual` is absent, the DTI rule is **`not_evaluated`** and emits a
  **`refer_trigger`** (insufficient-info REFER) — **never** a divide error, **never** a fabricated
  ratio, **never** a silent pass. `actual_value = null` in that `RuleResult`.
- The fired rule reports the exact computed `dti_ratio` + the `<=` comparison + `0.40` threshold.

### DR-INCM — income multiple
- **`income_multiple = requested_cover_amount / verifiable_income_annual`**, computed in `Decimal`,
  quantized 4 dp `ROUND_HALF_UP`.
- **Ceiling is a versioned YAML rule threshold**, not a hardcoded constant (Q9, FR-RULES-6) — it can
  change only via a new rulebook version.
- **Operand-missing**: `verifiable_income_annual` `0`/absent ⇒ **`not_evaluated` → `refer_trigger`**
  (same insufficient-info REFER rule as DTI).
- The fired rule reports the exact `income_multiple` + comparison + the ceiling from that rulebook
  version.

> Both derivations are **exposed in the resolution namespace** (`domain-entities.md §4.2`) so a rule
> can name `dti_ratio` / `income_multiple` in its `input_fields`. They are derived per-evaluation,
> not stored on the profile (facts stay single-sourced in intake).

---

## 3. Aggregation — per-rule results → the recommendation (Q5 — fixed precedence)

**Deterministic, order-independent** (CON-DET-1): the recommendation is a pure function of the
**set** of `outcome_tier` contributions, not their evaluation order.

| Precedence (highest first) | Condition | Recommendation |
|:--:|---|---|
| 1 | **Any** `RuleResult.outcome_tier == decline_fail` | **`DECLINE-RECOMMEND`** |
| 2 | else **any** `refer_trigger` — including the `incomplete`/`not_evaluated` **insufficient-info** triggers (§3.1) and any borderline-band hit | **`REFER`** |
| 3 | else all rules `pass` / `pass_only` | **`APPROVE`** |

- **Decline dominates** (safety-conservative): a genuine `decline_fail` outranks any REFER
  contribution, even if the profile is also `incomplete`.
- **`-RECOMMEND` suffix mandatory** — never a bare "DECLINE" (FR-RULES-5).
- `decline_reasons` / `refer_reasons` on the report capture exactly which rule(s) drove the tier
  (explainability; the memo cites them).

### 3.1 Insufficient-info REFER is single-notioned (Q6 + Q8 — note 3)

Two signals both mean "insufficient information → REFER", both are `refer_trigger`, **neither is a
rule pass/fail, neither is ever silently dropped, neither carries `decline_fail` severity**:

1. **`profile.incomplete == true`** (intake set it: thin-file / single-missing-document / missing
   optional operand) → contributes a `refer_trigger` (a distinct **insufficient-information**
   trigger, **not** a rule pass/fail — keeps the intake→rules boundary clean; intake flags the
   fact, rules-engine interprets it as REFER).
2. **A rule whose required operand is missing** → `status = not_evaluated` + a `refer_trigger`
   (§2 DR-DTI/DR-INCM).

> **Thin-file preservation (skill)**: a profile that is **only** incomplete (no `decline_fail`)
> lands **REFER**, never DECLINE — precedence tier 2, exactly as the skill requires.

---

## 4. Deterministic confidence banding (Q7 — fixed constants, produced HERE)

`confidence ∈ {High, Medium, Low}`, a **pure function** of value-proximity + completeness using the
**fixed `ConfidenceBands` constants** carried in the versioned rulebook (`domain-entities.md §3`).

- **Proximity margin**: for each numeric rule, the normalized distance of `actual_value` from its
  nearest threshold. Wide margin = comfortably clear of the boundary; small margin = near-boundary.
- **Banding** (order-independent, deterministic):
  - **High** — every numeric rule clears its boundary by at least `high_margin` **and** the profile
    is complete.
  - **Medium** — at least one value sits within `high_margin` of its threshold (near-boundary), **or**
    a single incompleteness, but no `Low` trigger.
  - **Low** — multiple near-boundary hits, or material incompleteness (`actual_value == null` on a
    required rule), or at/under `low_margin` proximity.
- **Determinism**: `high_margin` / `low_margin` are **fixed declared constants** in the rulebook
  version (not data-dependent, not wall-clock, not arbitrary) — so identical inputs + `rulebook_version`
  reproduce the same `confidence` on replay (CON-DET-1, note 4). A version that changes the margins
  is itself a **new version** — replay under the original version stays exact.
- **Produced in rules-engine, never by the LLM** (CON-BR2 / reviewer G2). Confidence is read-only
  input to the memo.

---

## 5. Rule-outcome authoring (schema, not bulk data)

Each rule's `outcome` tier (`pass_only` / `refer_trigger` / `decline_fail`) is **rule data** in the
YAML (Q1). This FD fixes the **schema and boundary conventions** (§1–§4); the concrete tier
assignments for all 25–40 rules (which BMI band declines vs refers, which health flags are hard
fails, the income-multiple ceiling value, the occupation-risk table, the IRDAI clause set) are
**authored in Code-Gen** (`domain-entities.md §7`). The engine treats every rule uniformly
regardless of tier — tiers only feed the §3 aggregation.

---

## 6. Rule → requirement / invariant traceability

| Rule group | Satisfies |
|---|---|
| §1 boundary conventions | FR-RULES-3 (exact value + comparison; boundaries land intended side), US-RULES-2 |
| §2 DR-DTI, DR-INCM | FR-RULES-2 (financial: DTI ≤40%, income multiple), Q5 ownership, Decimal (intake Q4 carry) |
| §3 aggregation + §3.1 | FR-RULES-5 (exact enum, `-RECOMMEND`), US-RULES-3, CON-BR2, FR-INTAKE-3 (thin-file→REFER) |
| §4 confidence banding | reviewer G2 (deterministic confidence in core), CON-DET-1 |
| `input_fields` (domain-entities §2/§4.1) | CON-BR1 enforcement facet, US-RULES-5 |
| immutable version + `content_hash` (domain-entities §3) | FR-RULES-6, CON-AUDIT-1 |

**CON-BR2 restated**: every rule and the aggregation are **pure Python**; **no LLM anywhere** in
this path. The recommendation and confidence originate entirely here.

---

*End of business-rules.md. Pipeline / evaluation-order / replay / determinism logic →
`business-logic-model.md`; schema → `domain-entities.md`.*
