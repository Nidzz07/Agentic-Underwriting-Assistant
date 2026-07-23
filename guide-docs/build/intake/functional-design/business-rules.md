# Business Rules — `intake` + `document-sanitizer`

**Stage**: BUILD → Functional Design (per-unit) · cluster-FD-first unit 1 of 4
**Units**: U1 `intake` (SEC-2 gate + derivations) · U2 `document-sanitizer` (SEC-1)
**Date**: 2026-07-03
**Scope**: Field-level validation, derivation, and sanitization rules. Every rule states its
comparison explicitly and its boundary behaviour. Technology-agnostic.

**Invariants held**: SEC-2 (intake gate, single source), SEC-1 (sanitizer, single source),
CON-BR2 (no recommendation here), CON-DET-1 (no wall-clock / determinism), CON-BR1 (demographics
never influence outcome), DATA-4 (synthetic only).

---

## 1. SEC-2 validation-gate rules (U1 — `validate_gate`)

Runs on the **sanitized** extracted draft, **before any agent**. Produces `ApplicantProfile`
(valid, possibly `incomplete=true`) **or** `RejectedIntake`. Reject reasons map to
`reason_category ∈ {malformed, unparseable, missing_required}`.

### 1.1 Required primitives (Q11 — absent VALUE ⇒ reject `missing_required`)

| Rule | Field | Condition to PASS | On fail |
|---|---|---|---|
| BR-REQ-2 | `date_of_birth` | present, valid ISO date, `date_of_birth <= as_of_date` | reject `malformed` if unparseable/out-of-order; `missing_required` if absent |
| BR-REQ-3 | `as_of_date` | present, valid ISO date | reject `missing_required` (absent) / `malformed` (unparseable) |
| BR-REQ-4 | `verifiable_income_annual` | present, `Decimal`, `>= 0` | `missing_required` (absent) / `malformed` (non-numeric or `< 0`) |
| BR-REQ-5 | `requested_cover_amount` | present, `Decimal`, `> 0` | `missing_required` (absent) / `malformed` (`<= 0` or non-numeric) |

> **`missing_required` triggers on a missing VALUE, not a missing document** (see §4).
>
> **`application_id` is NOT a gate-checked input.** It is **system-assigned** by intake at
> successful gate pass (`domain-entities.md §2`, marker `S`) — the audit-store correlation key.
> It can therefore never be "missing" and carries **no `BR-REQ` rule**. The required primitives
> above are the applicant-supplied values that must be establishable from some source; the
> identity/correlation key is **generated, not validated**. (Rule IDs start at `BR-REQ-2`; the
> `BR-REQ-1` slot is intentionally retired, not renumbered, to keep cross-references stable.)

### 1.2 Optional-and-flagged fields (absent ⇒ valid, may set `incomplete=true`)

| Rule | Field(s) | Behaviour |
|---|---|---|
| BR-OPT-1 | `height_cm`, `weight_kg` | Both present ⇒ derive `bmi_derived` (DR-BMI). Exactly one present, or neither ⇒ `bmi_derived` absent and `incomplete=true` (never reject). |
| BR-OPT-2 | `existing_debt_obligations_annual` | Present ⇒ validated `Decimal >= 0`. Absent ⇒ `incomplete=true` (DTI un-computable downstream — rules-engine handles the missing operand). |
| BR-OPT-3 | `employment_type`, `smoking_status`, `occupation`, `health_flags` | Absent/`unknown` ⇒ valid; set `incomplete=true` when materially absent. Present ⇒ validated against the enum/type in `domain-entities.md`. |

### 1.3 Type / range validation (present values)

| Rule | Field | Comparison |
|---|---|---|
| BR-TYP-1 | monetary fields | must parse as `Decimal`; **never coerced through float** (Q4 — preserves exact thresholds) |
| BR-TYP-2 | `height_cm`, `weight_kg` | `Decimal`, strictly `> 0` |
| BR-TYP-3 | enums | value ∈ declared set (else `malformed`) |
| BR-TYP-4 | `age_years_derived` | `0 <= age <= 120` sanity (see boundary note) |

> **Boundary note (CON-BR2):** intake does **not** apply the eligibility band. An applicant with
> `age = 17` or `age = 70` is a **valid** `ApplicantProfile`; the `>= 18` / `<= 65` band decision
> is `rules-engine`'s (REFER/DECLINE-RECOMMEND). Intake's `age_years_derived` sanity guard is the
> only age check here: it rejects as `malformed` **iff** `age_years_derived < 0` **or**
> `age_years_derived > 120` — both bounds are **inclusive-valid** (`0` and `120` pass; `-1` and
> `121` reject). No `>= 18` / `<= 65` comparison is made at intake.

---

## 2. Reject-vs-REFER boundary rule (Resolution 2 — the key rule)

**Principle**: reject only what is **structurally unrecoverable**; everything merely **incomplete**
is a valid profile the `rules-engine` routes to REFER. Intake never emits a recommendation
(CON-BR2). This honours FR-INTAKE-3 (thin-file / single-missing-document stay processable).

**The document-vs-value distinction** (the manifest, Q6, tracks document presence separately from
field presence):

| Situation | Value present? | Document present? | Outcome |
|---|:--:|:--:|---|
| Income stated on the application form, salary slip **not** uploaded | ✅ | ❌ (`missing`) | **Valid `ApplicantProfile`, `incomplete=true`** → `rules-engine` REFER |
| Salary slip uploaded but **unparseable**, income also absent from form | ❌ | ⚠️ (`unparseable`) | **`RejectedIntake`** — `reason_category` = `unparseable`, income in `missing_items` |
| Income absent from form **and** no income document at all | ❌ | ❌ | **`RejectedIntake`** — `missing_required`, income in `missing_items` |
| All required values present, one optional document missing | ✅ | ❌ | **Valid, `incomplete=true`** → REFER |
| PDF corrupt / no text extractable at all | ❌ | ⚠️ | **`RejectedIntake`** — `malformed`/`unparseable` |

**DocumentManifest four-state coverage** — every `DocumentEntry.status` in `domain-entities.md §4`
maps to exactly one gate effect; **no state-combination is unhandled**. Outcome is driven by
**required-VALUE availability**; document `status` only modulates whether a present value is
corroborated:

| `DocumentEntry.status` | Meaning | Effect at the gate |
|---|---|---|
| `parsed` | extracted OK; value available from the document | value present ⇒ contributes to a **valid** `ApplicantProfile` |
| `missing` | expected type not supplied | no value from this document ⇒ **required value present elsewhere** (form field or another `parsed` doc) → **valid, `incomplete=true`** → REFER; **required value unavailable anywhere** → **reject `missing_required`** |
| `unparseable` | supplied but parse failed | no value from this document ⇒ **required value present elsewhere** → **valid, `incomplete=true`** → REFER; **required value unavailable anywhere** → **reject `unparseable`** |
| `present` | uploaded, not yet parsed | **transient only** — parse always runs to completion before the gate, so at gate time every entry is `parsed` / `missing` / `unparseable`. A residual `present` at gate time is treated as **`unparseable`** for the gate decision (never silently admitted). |

> **Coverage guarantee**: value-missing (from *every* source) ⇒ **reject**;
> document-missing-but-value-present ⇒ **valid + `incomplete`** ⇒ REFER. There is no
> `(value, status)` combination without a defined outcome.

- **BR-GATE-BOUNDARY (reject)**: reject iff a **required primitive VALUE** (BR-REQ-2..5) cannot be
  established from **any** source (form field or parseable document), **or** input is structurally
  `malformed`/`unparseable`.
- **BR-GATE-INCOMPLETE (REFER path)**: if all required values are present but any corroborating
  **document** or optional operand is `missing`/absent, produce a **valid** `ApplicantProfile` with
  `incomplete=true`. **Intake sets the flag; `rules-engine` decides REFER.**

- **BR-GATE-REASON (reject `reason_category` precedence)** — *pinned at Code-Gen 2026-07-04; the
  design owns the behavior the implementation decided.* When the gate rejects, the
  `reason_category` is chosen by a **fixed precedence** over the reject conditions above, so the
  outcome is deterministic and total:
  1. **`malformed`** — a **structurally invalid** input: a non-mapping draft, a present-but-unparseable
     required value (bad date, non-numeric money), a cross-field violation (`date_of_birth > as_of_date`,
     `income < 0`, `requested_cover <= 0`), an invalid enum, `age_years_derived` outside the `0..120`
     sanity band, or **any** unexpected error caught at the fail-closed boundary. *Structural
     corruption dominates — it is reported before mere absence.*
  2. **`unparseable`** — no structural fault, but a **required VALUE is absent from every source AND at
     least one expected document is `unparseable`** (a `present`-at-gate document is treated as
     `unparseable`, `domain-entities.md §4`). The parse failure is the proximate cause of the missing
     value.
  3. **`missing_required`** — no structural fault and no unparseable document, but a **required VALUE is
     plainly absent** from every source.

  Precedence order is **`malformed` > `unparseable` > `missing_required`**. `missing_items` lists the
  absent required primitives plus any `unparseable` document types (`domain-entities.md §6`). This rule
  makes `RejectedIntake.reason_category` a single-valued function of the input — no reject can match two
  categories ambiguously. (Realized by `IntakeGate`; **NFR-INT-SEC2-TOTAL/-COVERAGE** exercise every
  branch, incl. `test_each_reason_category_is_reachable`.)

---

## 3. Deterministic derivation rules (U1 — CON-DET-1, no wall-clock)

### DR-AGE — age from `date_of_birth` + `as_of_date`
- `age_years_derived` = number of **completed** whole years from `date_of_birth` to `as_of_date`
  (floor). Computed purely from the two **stored** dates — **no system clock is ever read**.
- **Birthday-not-yet-reached rule (explicit comparison)**: if `(as_of_date.month, as_of_date.day)`
  is **strictly less than** `(date_of_birth.month, date_of_birth.day)`, subtract 1 from the raw
  year difference. Equality on month/day ⇒ the birthday **has** occurred (age increments **on** the
  birthday).
- **Leap-day convention (documented, deterministic)**: for a Feb-29 birth date in a non-leap
  `as_of_date` year, the birthday is treated as reached on **Mar 1**. Stated so replay is exact.
- **Boundary**: `as_of_date == date_of_birth` ⇒ `age = 0`. Exactly-18 / exactly-65 land on the
  intended side for `rules-engine`'s `>= 18` / `<= 65` comparison because age is completed years.

### DR-BMI — BMI from `height_cm` + `weight_kg`
- `height_m = height_cm / 100` (`Decimal`); `bmi_derived = weight_kg / (height_m * height_m)`.
- **Fixed rounding**: quantize to **2 decimal places, `ROUND_HALF_UP`** — a single declared mode so
  the value is reproducible on replay and the 25.00 / 30.00 boundaries are exact.
- All arithmetic in `Decimal` (Q4) — **no float** at any step.
- **Boundary**: a derived `25.00` or `30.00` is stored exactly; `rules-engine` owns the band
  comparison operators (`< 25`, `25 <= x < 30`, `>= 30`), not intake.

> Derivations are **stored** on the profile (`age_years_derived`, `bmi_derived`) so every consumer
> reads one fixed value — no consumer re-derives (Q5 single-sourcing).

---

## 4. SEC-1 sanitization rules (U2 — `document-sanitizer`)

### 4.1 Scope (Q8)
- **SR-SCOPE**: sanitize **only free-text / narrative fields** that can flow toward the LLM memo
  (e.g. `medical_questionnaire` free-text notes, free remarks). **Numeric, structured, enum, and
  demographic fields are NOT sanitized** — they are validated by the SEC-2 gate and (demographics)
  never reach the LLM.

### 4.2 Detection + neutralization (Q7 — neutralize-and-log, never hard-fail)
- **SR-DETECT**: scan free-text for instruction-like injection patterns, categorized as
  `instruction_override` (e.g. imperative "ignore previous instructions" style directives),
  `role_injection` (system/assistant role or persona takeovers), `delimiter_escape` (prompt
  delimiter / code-fence / XML-tag escapes), `tool_mimic` (fake tool-call or function-call syntax).
- **SR-NEUTRALIZE**: defang each matched span (strip or replace with an inert placeholder) and keep
  the cleaned text flowing forward. **Never reject on suspicion** — a suspicious document is
  cleaned, not failed (rejection is the SEC-2 gate's job, and only for structural reasons).
- **SR-LOG**: append a `SanitizationReportEntry` for every neutralization — `source_field`,
  `original_span` (verbatim, audit-only), `neutralized_span`, `pattern_category`. Set
  `was_modified=true`.
- **SR-CLEAN-BOUNDARY**: no pattern matched ⇒ `clean_text` equals the input, empty `report`,
  `was_modified=false`.

### 4.3 Ordering + invariant boundary
- **SR-ORDER**: sanitize runs **after parse, before the SEC-2 gate** (`parse → sanitize → gate`,
  `unit-of-work-dependency.md §2`). The gate validates **sanitized** text.
- **SR-FORENSIC (invariant, cross-ref)**: the `SanitizationReport` / `original_span` is
  **audit-only and must never re-enter any LLM-bound context** — full statement and enforcement in
  `business-logic-model.md §4`.
- **Ownership**: SR-* rules belong to `document-sanitizer` (SEC-1) only; BR-* gate rules belong to
  `intake` (SEC-2) only. Two units, two invariants, one pipeline pass.

---

## 5. Rule → requirement / invariant traceability

| Rule group | Satisfies |
|---|---|
| BR-REQ-*, BR-TYP-*, §2 boundary | SEC-2, FR-INTAKE-2, FR-INTAKE-3 |
| §2 BR-GATE-INCOMPLETE | FR-INTAKE-3 (thin-file / single-missing → REFER), CON-BR2 |
| DR-AGE, DR-BMI | CON-DET-1 (deterministic, no wall-clock), reproducibility |
| BR-OPT-2 (`existing_debt_obligations`) | Resolution 1 (single-sourced DTI operands) |
| Demographics segregation (via `domain-entities.md §3`) | CON-BR1 |
| SR-* | SEC-1, failure mode #4 |
| Decimal (BR-TYP-1) | AC exact-threshold boundary testing (Q4) |

**CON-BR2 restated**: no rule in this document emits or implies a recommendation. `incomplete` is a
structural flag; the recommendation originates in `rules-engine`.

---

*End of business-rules.md. Pipeline orchestration & algorithms → `business-logic-model.md`;
schema → `domain-entities.md`.*
