# NFR Requirements — `intake` + `document-sanitizer` (coupled pair)

**Stage**: BUILD → NFR Requirements (per-unit) · cluster unit 1 (dependency-first)
**Units**: U1 `intake` (SEC-2) + U2 `document-sanitizer` (SEC-1)
**Depth**: comprehensive (security-critical)
**Date**: 2026-07-04
**Scope**: The unit's **testable non-functional targets**, built **ON the frozen, approved Functional
Design** — the `ApplicantProfile` contract, the `parse → sanitize → gate` pipeline, and the
deterministic derivations are **settled and NOT re-opened**. Every target below is stated as a
**pass/fail assertion** that becomes a pytest test at Code-Gen (TDD, pytest-cov ≥ 90% per QA-6).

**How to read a target**: each `NFR-INT-*` has an **ID**, a **statement**, a **measurable
assertion** (the pass/fail check), and **traceability**. "Blocking in `quality-gates`" means this
unit *authors* the test and *defines* the target; the `quality-gates` unit *aggregates* it as a
blocking gate — this unit does **not** re-implement the harness (reference-not-own).

---

## 1. Security — SEC-1 (`document-sanitizer`: injection defense + sandboxed parsing)

### NFR-INT-SEC1-NEUT — injection-neutralization robustness
- **Statement**: on a **curated adversarial injection corpus `C`**, every known injection pattern is
  neutralized; sanitization is idempotent; false positives stay within a **pinned budget**.
- **Measurable assertions** (pass/fail):
  - **Neutralization rate = 100% of `C`** — for every item in `C`, `clean_text` contains **no
    residual** pattern of any category (`instruction_override`, `role_injection`,
    `delimiter_escape`, `tool_mimic`, + obfuscation variants). `assert neutralization_rate(C) == 1.0`.
  - **Idempotence** — `∀x: sanitize(sanitize(x).clean_text).clean_text == sanitize(x).clean_text`
    (re-sanitizing is a no-op; empty report on the second pass).
  - **False-positive budget — PINNED**: measured against a **legitimate-text corpus `L`** (benign
    documents that superficially resemble instructions), the FP rate **≤ 2.0%**
    (`assert fp_rate(L) <= Decimal("0.02")`). *Rationale for the value*: a non-zero budget is honest
    (perfect precision is unachievable on adversarial-looking benign text); 2% is a **strict starting
    ceiling** for a synthetic-data showcase, revisitable at Code-Gen if `L` proves it too tight/loose.
    *(If the team prefers a method over a fixed number: the ceiling is set to the observed FP rate on
    `L` at first green + a 0.5% margin, frozen thereafter — either form is testable.)*
- **Traceability**: SEC-1, failure mode #4, FD `business-rules.md` SR-DETECT/SR-NEUTRALIZE. Corpora
  `C`/`L` authored here; **blocking in `quality-gates`**.

### NFR-INT-SEC1-SANDBOX — sandboxed parsing (Q1=B, subprocess isolation)
- **Statement**: untrusted-PDF parsing (pdfplumber) runs in a **resource-bounded, killable
  subprocess**; a hostile/malformed document cannot crash, hang, or exhaust the main service.
- **Measurable assertions** (pass/fail):
  - **Isolation scope** — the subprocess wraps the **untrusted-PDF parse step ONLY**; the
    deterministic derivations (age/BMI/`Decimal`) run **in-process, post-validation**, outside the
    subprocess. (Asserted structurally: the derivation code has no subprocess dependency.)
  - **Resource bounds** — memory / CPU / **wall-time** limits are enforced; a parse exceeding the
    **timeout** is killed and mapped to a **deterministic `unparseable`** `DocumentEntry.status`
    (never a hang, never a main-process crash). `assert parse(malicious_pdf).status == unparseable`
    for the timeout/oom/crash fixtures.
  - **Boundary encoding is canonical** — the parse result crossing the IPC boundary is
    **canonically/deterministically encoded** (stable field order, explicit encoding) so the **same
    PDF → same extracted fields** on a single run (no ordering/encoding non-determinism introduced by
    the process hop).
  - **Outside the replay path (stated invariant)** — **replay never re-parses**: `audit-store`'s
    `ReplayService` feeds the **persisted `ApplicantProfile` snapshot**, not the raw PDF. The
    subprocess is therefore **entirely outside the replay determinism boundary** (it runs once at
    intake, upstream of persistence). *(No test needed on this unit — it is a boundary fact;
    audit-store's replay suite owns the snapshot-round-trip check, see NFR-INT-DET-2.)*
- **Traceability**: SEC-1 ("sandbox"), Brief §10 FM4, CON-DET-1 (boundary). Decision recorded in
  `tech-stack-decisions.md`.

---

## 2. Security — SEC-1-FORENSIC (audit-only span never leaks — LLM context **and telemetry**)

### NFR-INT-FORENSIC — the forensic span is audit-only, everywhere
- **Statement**: the `SanitizationReport` / `original_span` (and, to be safe, the neutralized span
  **content**) is **audit-only** — it reaches **only** the audit lane (`audit-store`), and **never**
  (a) any LLM-bound context, **nor** (b) any emitted telemetry (spans/metrics/logs).
- **Measurable assertions** (pass/fail):
  - **(a) LLM-context exclusion — structural + tested**: `memo-agent-core`'s `MemoAgentInput` type
    structurally cannot carry the forensic span (designed in memo-agent-core FD), **AND** an
    assertion test proves **no LLM-bound payload derived from intake can reference `original_span`**.
    `assert original_span not in any_llm_bound_payload(...)`.
  - **(b) Telemetry exclusion (the headline extension)**: emitted spans/metrics/logs carry **ONLY
    non-forensic signals** — counts, enum categories, durations, statuses/booleans — and **NO span
    text** (neither `original_span` **nor** the `neutralized_span` content). An assertion test proves
    **no emitted telemetry payload contains span text**. `assert no_span_text_in(emitted_telemetry)`.
  - The full `SanitizationReport` (both spans) travels the **separate audit path** to `audit-store`
    **only**.
- **Traceability**: SEC-1-FORENSIC (FD `business-logic-model.md §4`), SEC-1, DATA-4. **Blocking in
  `quality-gates`.**

---

## 3. Security / reliability — SEC-2 (`intake` gate: total function + reject-vs-REFER)

### NFR-INT-SEC2-TOTAL — the validation gate is a total function (never raises)
- **Statement**: `validate_gate` **never raises to the caller** — **every** input maps to exactly one
  of `ApplicantProfile` (valid, possibly `incomplete`) or `RejectedIntake` (structured
  `reason_category` + per-field errors + missing-items).
- **Measurable assertions** (pass/fail):
  - **Negative-input test matrix** — malformed, adversarial, empty, oversized, wrong-type, truncated,
    injection-laden, and corrupt-PDF inputs each produce a **handled** `ApplicantProfile` **or**
    `RejectedIntake` — **no unhandled exception, no partial-profile leak**.
    `assert isinstance(validate_gate(x), (ApplicantProfile, RejectedIntake))` for every matrix row.
  - Each `reason_category ∈ {malformed, unparseable, missing_required}` is exercised at least once.
- **Traceability**: SEC-2, FR-INTAKE-2, Brief §10 FM5. **Blocking in `quality-gates`.**

### NFR-INT-SEC2-COVERAGE — exhaustive reject-vs-REFER combination coverage
- **Statement**: every `(DocumentManifest.status × required-field-value presence)` combination maps to
  **exactly one** defined outcome (reject vs valid+`incomplete`→REFER) — no unhandled combination
  (the FD's four-state coverage table under stress).
- **Measurable assertions** (pass/fail):
  - A **combination test suite** covers all four states (`present`/`parsed`/`missing`/`unparseable`)
    × value-available / value-unavailable, incl. degenerate cases (all-missing, all-unparseable,
    value-present-doc-missing, transient `present` at gate).
  - **Invariant assertion**: thin-file / single-missing-document → **valid + `incomplete` → REFER**,
    **never** a hard reject. `assert outcome(thin_file) == VALID_INCOMPLETE`.
- **Traceability**: FR-INTAKE-3, FD `business-rules.md §2` (four-state coverage + BR-GATE-BOUNDARY),
  CON-BR2 (intake flags, C2 decides REFER). **Blocking in `quality-gates`.**

---

## 4. Reproducibility — CON-DET-1 (byte-identical; the replay dependency)

### NFR-INT-DET-1 — byte-identical deterministic derivations
- **Statement**: `age_years_derived`, `bmi_derived`, and all `Decimal` money fields re-derive
  **identically** on repeated runs of the same input.
- **Measurable assertions** (pass/fail):
  - **Same-input ×N≥10** — run each derivation ≥10× on identical input; assert **all runs identical**
    (mirrors NFR-REPRO-1's same-input×10 discipline). `assert len(set(runs)) == 1`.
  - **Boundary-case determinism** — explicit cases: age **exactly 18** and **exactly 65**, BMI
    **exactly 25.00** and **30.00**, leap-day DOB, `as_of_date == date_of_birth`, and money **exactly
    at a threshold** — each yields the exact expected value every run.
  - **No non-determinism sources** — no wall-clock, no unseeded randomness, no dict-order reliance in
    any derivation (asserted by construction + the ×N test).
- **Traceability**: CON-DET-1, NFR-REPRO-1, FD DR-AGE/DR-BMI, Q4 `Decimal`. **Feeds `quality-gates`
  reproducibility-suite.**

### NFR-INT-DET-2 — `ApplicantProfile` CANON-SER round-trip (byte-identical; replay dependency)
- **Statement**: the `ApplicantProfile` is **round-trip stable** under the **single CANON-SER
  convention defined in `audit-store` `domain-entities.md §2.1`** — **referenced, NOT re-declared**.
- **Measurable assertions** (pass/fail):
  - **Round-trip byte-identity** — `serialize → deserialize → serialize` yields **byte-identical**
    output for every profile fixture (all fields: `Decimal`-as-string, canonical enums, `null`
    explicit, the segregated `demographics` sub-object, the nested `DocumentManifest`).
    `assert canon_ser(deserialize(canon_ser(p))) == canon_ser(p)`.
  - **Shared-spec (no drift)** — the round-trip uses audit-store's §2.1 spec; **this unit does not
    define a parallel convention**. This is the **replay dependency**: `audit-store` persists the
    snapshot via CANON-SER and `ReplayService` deserializes it back to feed `evaluate()`; a
    non-stable round-trip would break replay.
- **Traceability**: CON-DET-1, CON-AUDIT-1 (replay), audit-store FD §2.1/§4. **Blocking in
  `quality-gates`** (jointly with audit-store's replay suite).

---

## 5. Data handling — DATA-4 (synthetic-only, zero real PII)

### NFR-INT-DATA4 — active zero-real-PII guard
- **Statement**: all inputs/fixtures are synthetic; **zero real PII** at any stage.
- **Measurable assertions** (pass/fail):
  - **Active CI guard** — a build/test check **FAILS the build** if any real-PII pattern appears in
    test data, fixtures, or committed artifacts (not a policy note — an enforced check).
    `assert scan_for_real_pii(repo_fixtures) == []`.
  - **Demographics segregated + not correlatable in logs** — the segregated `demographics` sub-object
    (CON-BR1, already in the FD) is **never logged in a way that could correlate** to financial/medical
    facts (ties to NFR-INT-FORENSIC telemetry rule — no sensitive content in telemetry).
- **Traceability**: DATA-4, CON-BR1, Brief §8. **Blocking in CI / `quality-gates`.**

---

## 6. Performance — scoped soft budget + hard bounds (not an SLA)

### NFR-INT-PERF — parse→sanitize→gate envelope
- **Statement**: a **soft latency budget** for the `parse → sanitize → gate` path on a typical
  synthetic profile, plus the **hard bounds** (the subprocess timeout) as the real guarantees.
- **Measurable assertions** (pass/fail):
  - **Soft budget** — a documented **p95 target** for parse+sanitize+gate on a typical **3-document**
    synthetic profile (observed/best-effort; recorded, not a breach-failure SLA).
  - **Hard bound** — the subprocess **wall-time timeout** (NFR-INT-SEC1-SANDBOX) is enforced and
    tested: a document exceeding it is killed → `unparseable`.
  - **Priority order** — correctness + security + determinism **take precedence over speed** (skill:
    explainability/consistency over automation speed). This is a validation/portfolio build, not a
    latency-SLA product.
- **Traceability**: Brief §6 (targets), SEC-1 (timeout bound). Soft budget is **observed**, not
  blocking; the hard bound **is** tested.

---

## 7. Observability — EMIT-ONLY (scope boundary; forensic-free)

### NFR-INT-OBS — this unit emits, the observability unit owns the stack
- **Statement**: `intake`+`document-sanitizer` **emits** structured trace spans / metrics; it does
  **NOT** design or own the Langfuse / Prometheus / Grafana stack (that is the `observability` unit,
  NFR-OBS-1/2).
- **Measurable assertions** (pass/fail) / commitments:
  - **Emitted signal set (forensic-free)** — spans/events for `parse`, `sanitize` (incl. a
    **neutralization-count** — a number), `validate_gate` (incl. reject `reason_category` — an enum),
    plus rejection / `incomplete` counters and derivation timings. **No span text** (ties to
    NFR-INT-FORENSIC (b)).
  - **Reference-not-own** — this unit does **not** implement Langfuse/Prometheus wiring; it exposes
    the signals for the `observability` unit to wire. `assert emitted_signals ⊆ {counts, enums, durations, statuses}`.
- **Traceability**: NFR-OBS-1/2 (scope boundary only), SEC-1-FORENSIC (b). Stack owned by
  `observability`.

---

## 8. Traceability & ownership summary

| NFR ID | Invariant / Req | Test lives (authored) | Aggregated / owned |
|---|---|---|---|
| NFR-INT-SEC1-NEUT | SEC-1, FM4 | this unit (corpora C/L) | `quality-gates` (blocking) |
| NFR-INT-SEC1-SANDBOX | SEC-1, CON-DET-1 boundary | this unit | — (unit-local) |
| NFR-INT-FORENSIC | SEC-1-FORENSIC | this unit (LLM + telemetry asserts) | `quality-gates` (blocking) |
| NFR-INT-SEC2-TOTAL | SEC-2, FM5 | this unit (negative matrix) | `quality-gates` (blocking) |
| NFR-INT-SEC2-COVERAGE | FR-INTAKE-3 | this unit (combination suite) | `quality-gates` (blocking) |
| NFR-INT-DET-1 | CON-DET-1, NFR-REPRO-1 | this unit (×N + boundary) | `quality-gates` reproducibility |
| NFR-INT-DET-2 | CON-DET-1, CON-AUDIT-1 | this unit + audit-store | `quality-gates` (joint) |
| NFR-INT-DATA4 | DATA-4, CON-BR1 | this unit (CI guard) | CI / `quality-gates` |
| NFR-INT-PERF | Brief §6 | this unit (hard bound) | observed (soft) |
| NFR-INT-OBS | NFR-OBS-1/2 (scope) | this unit (emit set) | `observability` (stack) |

**Ownership held (reference-not-own)**: observability stack → `observability`; secrets → SEC-3 /
`secrets-config`; the blocking-gate harness → `quality-gates`; persistence → `audit-store` /
`database`. **Infrastructure Design remains SKIPPED** for this unit (pure-logic; sandboxed-parsing is
a security NFR here, not cloud topology) — the skip is logged in `audit.md`.

---

*End of nfr-requirements.md. Tech choices + the subprocess-isolation decision → `tech-stack-decisions.md`.*
