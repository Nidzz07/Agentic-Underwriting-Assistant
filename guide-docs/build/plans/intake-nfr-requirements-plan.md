# NFR Requirements Plan — `intake` + `document-sanitizer` (coupled pair)

**Phase / Stage**: BUILD → NFR Requirements (per-unit, plan-then-generate)
**Loop position**: cluster unit 1 (dependency-first) · FD **APPROVED 2026-07-03** → **NFR
Requirements ← here** → NFR Design → ~~Infrastructure Design (SKIP/minimal — logged)~~ → Code-Gen.
**Units covered**: U1 `intake` (SEC-2) + U2 `document-sanitizer` (SEC-1) — same coupled pass, as at FD.
**Depth**: **comprehensive** (security-critical — `execution-plan.md §3` line 191 lists `intake-*`
comprehensive; `unit-of-work.md` U2 comprehensive).
**Date**: 2026-07-04
**Status**: **Plan — awaiting `[Answer]:` tags.** No NFR Requirements artifacts generated yet. Stop
after this plan.

This plan follows `.project-guide-rule-details/build/nfr-requirements.md`. NFR Requirements
**builds ON the frozen, approved Functional Design — it does NOT re-open it.** The `ApplicantProfile`
contract, the `parse → sanitize → gate` pipeline, the SEC-1/SEC-2 single-sourcing, the deterministic
age/BMI derivations, `Decimal` money, and the system-assigned `application_id` are **settled**; this
stage sets the **quality attributes** (security robustness, reproducibility, error-handling,
performance, observability scope) those internals must meet.

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 What this stage decides (NFRs, not functionals)
The FD defined **what** intake + document-sanitizer do. NFR Requirements defines **how well** —
scoped to this unit's binding invariants:
- **SEC-1** (`document-sanitizer`): prompt-injection defense robustness + **sandboxed parsing** (the
  brief's prompt-injection sandbox, failure mode #4 — a **security NFR**, correctly landing here, not
  in Infrastructure Design).
- **SEC-2** (`intake` gate): input-validation completeness; malformed/adversarial input handling;
  reject-vs-REFER robustness.
- **CON-DET-1**: reproducibility of the deterministic derivations (age from DOB+`as_of_date`, BMI,
  `Decimal` money) — **byte-identical re-derivation**, which `audit-store` replay depends on.
- **DATA-4**: synthetic-only data handling; zero-real-PII enforcement.
- **Performance / observability** for the `parse → sanitize → gate` path — **scoped to this unit's
  depth only**; cross-cutting observability infrastructure is owned by the `observability` unit
  (NFR-OBS-1/2), not designed here.

### 1.2 Frozen FD carried in (NOT re-opened — quality targets attach to these)
- `parse(documents) → ApplicantProfile` / `sanitize(raw_text) → SanitizedText` /
  `validate_gate(extracted) → ApplicantProfile | RejectedIntake` (frozen signatures).
- **SEC-1-FORENSIC invariant**: the `SanitizationReport` / `original_span` is **audit-only** and must
  never re-enter LLM-bound context (FD `business-logic-model.md §4`). NFR here sets its **enforcement
  robustness target**, not its definition.
- Deterministic **DR-AGE / DR-BMI** (no wall-clock, `ROUND_HALF_UP` 2dp, `Decimal`); the reject-vs-
  REFER four-state document model; `incomplete`→REFER routing.

### 1.3 Governing requirements (`requirements.md`)
- **SEC-1** (prompt-injection defense — sanitize/**sandbox**), **SEC-2** (input validation — Pydantic
  gates reject malformed before agent entry), **DATA-4** (synthetic only, zero real PII).
- **NFR-REPRO-1** (decision reproducibility 100% — asserted on the deterministic engine output; this
  unit's derivations are upstream inputs to it), **NFR-EXPLAIN-1** (every rejection/flag carries its
  triggering reason — the `RejectedIntake` reasons + `missing-items`).
- **NFR-OBS-1/2** (Langfuse 100% steps; Prometheus/Grafana) — **referenced for scope boundary only**;
  the observability stack is its own unit.
- **Verification** of CON-DET-1 / bias is single-sourced in `quality-gates` (reproducibility +
  bias-swap suites) — this unit's NFRs **feed** those gates; it does not re-own them.

### 1.4 Guardrails held (skill)
- Advisory-only naming; **bias-free by design** (CON-BR1 — demographics segregated, never influence);
  reproducibility (CON-DET-1); synthetic-only (DATA-4). Security-Guardrails extension **enabled**
  (prompt-injection defense, input validation, secrets, audit logging).

---

## 2. NFR Requirements execution plan (checkboxes — Step 2)

Artifacts to be generated **after** answers are collected and ambiguity-checked:
`guide-docs/build/intake/functional-design/` is the input; outputs →
`guide-docs/build/intake/nfr-requirements/` → `nfr-requirements.md`, `tech-stack-decisions.md`.

- [x] **P1. Analyze the frozen FD** (§1 above — done).
- [x] **P2. Collect `[Answer]:` tags** (§3); run the mandatory ambiguity-check (nfr-requirements.md
  Step 5); raise a clarification file if any answer is vague ("depends", "standard", "typical", …).
  **DONE 2026-07-04 — all 12 answered (Q1=B subprocess-isolated; rest A + notes); ambiguity-check
  CLEAN (no clarification file needed; no vague hedging). 5 design-elaborations for generation (see
  audit 2026-07-04T11:00 entry) — headline tightening: SEC-1-FORENSIC extends to TELEMETRY (no span
  text in any emitted metric/log, Q10); to pin at generation: the false-positive budget value (Q2).
  Awaiting explicit go to generate.**
- [x] **P3. `nfr-requirements.md`** — the unit's NFRs by category, each with a **measurable
  acceptance target** + traceability to SEC-1/SEC-2/CON-DET-1/DATA-4/NFR-*: (a) **Security** —
  injection-defense robustness, sandboxed-parsing model, SEC-1-FORENSIC enforcement, SEC-2 gate
  completeness/malformed-input handling; (b) **Reliability / error-handling** — parse-failure →
  `unparseable`, never-raise, reject-vs-REFER robustness; (c) **Reproducibility** — byte-identical
  derivations (CON-DET-1); (d) **Performance** — parse→sanitize→gate latency budget (scoped);
  (e) **Observability (scope only)** — which spans/metrics this unit *emits* (owned by observability);
  (f) **Maintainability / testability** — feeds `quality-gates` (reproducibility, and the security
  test surface).
- [x] **P4. `tech-stack-decisions.md`** — confirm/settle the unit-local tech choices: pdfplumber
  (parse), Pydantic v2 (gate), the **sanitizer implementation approach** (deterministic
  pattern/heuristic, **no LLM** in the sanitizer — CON-DET-1), the **sandbox mechanism** choice, and
  the `Decimal` money convention. (Most are already implied by the brief/FD — this records them as
  decisions with rationale.)
- [x] **P5. Scope-boundary check** — confirm no cross-cutting NFR owned elsewhere is redefined here
  (observability stack = `observability` unit; secrets = `secrets-config`/SEC-3; bias/repro
  *verification* = `quality-gates`); this unit only sets its **own** targets + what it emits/feeds.
- [ ] **P6. Guardrail compliance pass + present the standardized 2-option completion message**
  (per nfr-requirements.md Step 7 format) → Request Changes / Continue to Next Stage → **NFR Design**
  (per-unit).

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These set **quality targets** — they do **not** re-open the frozen FD.

### A. Security — SEC-1 injection defense + sandboxed parsing

## Question 1 — Sandboxed-parsing model (the brief's prompt-injection sandbox — SEC-1, failure mode #4)
The brief lists "input sanitization + **sandboxed parsing**" as the prompt-injection mitigation. At
what boundary is document parsing (pdfplumber) isolated?

A) **In-process resource-bounded parsing** — pdfplumber runs in-process but under strict guards:
   size/page caps, a parse **timeout**, exception containment (a malformed/hostile PDF can never
   crash the request or exhaust resources), and no network/file-system egress from parsing. Simplest
   for a free-tier single-service deploy; the "sandbox" is a hardened, bounded parse function.
B) **Out-of-process / subprocess isolation** — parsing runs in a separate sandboxed subprocess
   (resource-limited, killable) so a hostile document is contained outside the main process.
C) **Container/microVM isolation** — parsing in a separate container (heaviest; likely
   over-engineered for free-tier and a synthetic-data showcase).
D) Other (please describe after [Answer]: tag below)

[Answer]: Subprocess-isolated parsing with resource bounds (memory/time/CPU limits). pdfplumber on untrusted PDFs is an attack surface (malformed PDFs can exploit the parser, exhaust memory, or hang); a bounded subprocess contains a crash/hang/exploit to the subprocess (killed by the bound), not the main process. In-process-bounded is too weak (parser failure takes the service down); container is overkill for a library unit. The subprocess boundary must NOT affect the deterministic derivations (those run after parse, on validated data).

## Question 2 — Injection-defense robustness target (SEC-1 neutralize-and-log)
The sanitizer neutralizes suspected injection and continues (never hard-fails on suspicion). What is
the **robustness acceptance target**?

A) **A curated injection test-corpus** (the documented pattern categories: `instruction_override`,
   `role_injection`, `delimiter_escape`, `tool_mimic`, + obfuscation variants) with a **required
   neutralization rate = 100% of the corpus** (every known pattern neutralized), **idempotence
   asserted** (re-sanitizing `clean_text` is a no-op), and **zero clean-text false-positives above a
   documented budget**. This corpus feeds `quality-gates`.
B) A small smoke set of a few obvious patterns; no formal rate target.
C) Rely on the deterministic pattern list with no adversarial test-corpus.
D) Other (please describe after [Answer]: tag below)

[Answer]: Injection-defense target: on a curated adversarial test-corpus, 100% neutralization of known injection patterns + idempotence (sanitize∘sanitize == sanitize) + an explicit false-positive budget (defined acceptable rate for legitimate text that looks injection-like — not pretended to be zero).

## Question 3 — SEC-1-FORENSIC enforcement robustness (audit-only span never re-enters LLM context)
The `SanitizationReport` / `original_span` is audit-only. What **enforcement target** guarantees it
never reaches LLM-bound context?

A) **Structural + tested** — the memo-agent input contract structurally excludes it (already designed
   in memo-agent-core FD), AND this unit's suite includes an **assertion test** that no LLM-bound
   payload derived from intake can reference `original_span` (a regression guard). Target: the test
   is **blocking** in `quality-gates`.
B) Documented convention only (no automated assertion).
C) Redaction at prompt-build time (weaker — relies on redaction, not structural exclusion).
D) Other (please describe after [Answer]: tag below)

[Answer]: SEC-1-FORENSIC enforced BOTH structurally (memo-agent-core's MemoAgentInput type cannot carry the forensic span) AND by an assertion test proving the original_span never appears in any LLM-bound context. Belt-and-suspenders.

### B. Security / reliability — SEC-2 gate + error handling

## Question 4 — SEC-2 gate malformed/adversarial input handling (completeness target)
The Pydantic gate rejects malformed/unrecoverable input before any agent. What is the
**error-handling completeness target**?

A) **Total function, never raises to the caller** — every input maps to exactly one of
   `ApplicantProfile` (valid, possibly `incomplete`) or `RejectedIntake` (structured
   `reason_category` + per-field errors + missing-items); malformed/oversized/corrupt/empty/wrong-type
   inputs are all **handled paths** (no unhandled exception, no partial-profile leak). Target: a
   **negative-input test matrix** (each `reason_category` + boundary) is exercised, blocking in
   `quality-gates`.
B) Handle the common malformed cases; let truly exceptional inputs surface as 5xx.
C) Rely on Pydantic's default validation errors without a structured `RejectedIntake` mapping test.
D) Other (please describe after [Answer]: tag below)

[Answer]: The SEC-2 gate is a TOTAL FUNCTION that never raises — every input (malformed, adversarial, empty, oversized, wrong-type, truncated, injection-laden) yields either a valid ApplicantProfile or a structured RejectedIntake, never an unhandled exception. Verified by a negative-input test matrix.

## Question 5 — Reject-vs-REFER robustness (the four-state document model under stress)
The FD's four-state (`present`/`parsed`/`missing`/`unparseable`) reject-vs-REFER mapping must hold
under adversarial/degenerate inputs. What is the target?

A) **Every `(value-availability × document-status)` combination has a proven outcome** (the FD's
   coverage table), asserted by a **boundary/combination test suite** — including degenerate cases
   (all missing, all unparseable, value-present-doc-missing, transient `present` at gate). Thin-file
   / single-missing-doc **always** → valid+`incomplete`→REFER, never a hard reject. Blocking in
   `quality-gates`.
B) Test the happy path + a couple of reject cases; trust the mapping for the rest.
C) Other (please describe after [Answer]: tag below)

[Answer]: Exhaustive reject-vs-REFER coverage: test every DocumentManifest state (present/parsed/missing/unparseable) × required-field-presence combination maps to exactly one defined outcome (reject vs valid+incomplete→REFER). No unhandled combination.

### C. Reproducibility — CON-DET-1 (byte-identical re-derivation; replay depends on it)

## Question 6 — Reproducibility acceptance target for the deterministic derivations
Age (DOB+`as_of_date`), BMI (height/weight, `ROUND_HALF_UP` 2dp), and `Decimal` money must
re-derive **identically** — `audit-store` replay of this unit's outputs depends on it. What target?

A) **Byte-identical determinism, asserted ×N** — a calibration test runs the same inputs **≥10×**
   (mirroring NFR-REPRO-1's same-input×10 discipline) and asserts **identical** `age_years_derived` /
   `bmi_derived` / all `Decimal` fields every run; **explicit boundary cases** (age exactly 18/65,
   BMI exactly 25.00/30.00, leap-day DOB, `as_of_date == DOB`); **no wall-clock, no unseeded
   randomness, no dict-order reliance** anywhere in derivation. Feeds `quality-gates`
   reproducibility-suite.
B) A single-run correctness test per derivation (no repeat-run determinism assertion).
C) Other (please describe after [Answer]: tag below)

[Answer]: CON-DET-1: assert byte-identical derivation output across N≥10 repeated runs on the same input (catches hidden non-determinism — ordering, float drift, wall-clock leak), plus explicit boundary-case determinism tests (age exactly 18/65, BMI exactly 25/30, money exactly at thresholds).

## Question 7 — Serialization determinism for the profile snapshot (CANON-SER alignment)
`audit-store` persists the original `ApplicantProfile` (its `ApplicantProfileSnapshot`, by reference
to this unit's contract) using the single **CANON-SER** convention, and replay feeds it back to
`evaluate()`. What does this unit commit to?

A) **The `ApplicantProfile` is CANON-SER-serializable deterministically** — stable field order,
   `Decimal`-as-string, canonical enums, `null` explicit; **round-trip stable** (serialize →
   deserialize → identical object). This unit **references audit-store's single CANON-SER spec** (not
   a parallel convention) as the shared authority, so the persisted snapshot re-derives identically
   on replay. Target: a round-trip determinism test.
B) Leave serialization entirely to audit-store; this unit makes no round-trip guarantee.
C) Other (please describe after [Answer]: tag below)

[Answer]: ApplicantProfile CANON-SER round-trip determinism: serialize → deserialize → serialize yields byte-identical output, using audit-store's SINGLE CANON-SER spec (§2.1, referenced — NOT re-declared). This is the replay dependency: audit-store persists the snapshot via CANON-SER and ReplayService deserializes it back to feed evaluate(); a non-stable round-trip breaks replay.

### D. Data handling, performance, observability scope

## Question 8 — DATA-4 synthetic-only / zero-real-PII enforcement
The unit ingests documents + form data. What is the zero-real-PII target?

A) **Synthetic-only by construction + guarded** — all fixtures/inputs are synthetic (Faker/mock
   PDFs); a documented guard ensures no real-PII test data enters the repo or logs; **demographics
   are captured but segregated** (CON-BR1, already in the FD) and **never logged in a way that could
   correlate**. Target: recorded as a compliance NFR + a fixtures-are-synthetic check.
B) Rely on the "synthetic data only" project rule with no unit-level check.
C) Other (please describe after [Answer]: tag below)

[Answer]: DATA-4: an active CI/test guard that FAILS the build if any real-PII pattern appears in test data or fixtures (not just a policy) — synthetic-only enforced, zero real PII.

## Question 9 — Performance target for the `parse → sanitize → gate` path (scoped to this unit)
What performance envelope should the unit meet — bounded to this unit, not the whole request?

A) **A soft latency budget per document set** (e.g. a documented p95 target for parse+sanitize+gate
   on a typical 3-document synthetic profile) + the **hard bounds** from Q1 (size/page caps, parse
   timeout) as the real guarantees. Performance is **best-effort/observed**, not a strict SLA (this
   is a showcase on free tier); correctness + security + determinism take precedence over speed
   (skill: explainability/consistency over automation speed).
B) A strict enforced latency SLA with failure on breach.
C) No performance target at all.
D) Other (please describe after [Answer]: tag below)

[Answer]: A scoped SOFT latency budget (target for the parse→sanitize→gate path) + HARD bounds (the Q1 subprocess timeout — parse cannot hang indefinitely). NOT a strict production SLA — this is a validation/portfolio build; soft budget + hard safety bounds is the right rigor.

## Question 10 — Observability SCOPE for this unit (what it emits vs what it owns)
NFR-OBS-1/2 (Langfuse 100% steps, Prometheus/Grafana) are owned by the `observability` unit. What
does `intake`+`document-sanitizer` commit to **here**?

A) **Emit only** — this unit **emits** the trace spans / structured events for `parse`, `sanitize`
   (incl. a **neutralization-count** signal), and `validate_gate` (incl. reject `reason_category`),
   plus rejection/`incomplete` counters — so the `observability` unit can wire them into Langfuse +
   the Grafana dashboard. **This unit does NOT design the observability stack** (that is the
   `observability` unit / NFR-OBS-1/2). No `original_span` is ever emitted (SEC-1-FORENSIC).
B) Design the Langfuse/Prometheus wiring here (rejected — owned by the observability unit).
C) Emit nothing; observability is entirely external.
D) Other (please describe after [Answer]: tag below)

[Answer]: Observability = EMIT-ONLY for this unit: it emits spans/metrics (neutralization-count, reject-reason, derivation timings) but does NOT own the Langfuse/Prometheus/Grafana stack (owned by the observability unit). CRITICAL: the original_span / forensic content is NEVER emitted into telemetry (SEC-1-FORENSIC extends to observability — no forensic leak through metrics/logs).

### E. Tech-stack confirmations (unit-local)

## Question 11 — Sanitizer implementation approach (CON-DET-1: no LLM in the sanitizer)
The FD fixed the sanitizer as deterministic/pattern-based. Confirm the implementation approach for
`tech-stack-decisions.md`.

A) **Deterministic pattern/heuristic matching in pure Python — NO LLM** in the sanitizer (an LLM
   would reintroduce the injection surface and break CON-DET-1). Pattern set is versioned/testable;
   the injection test-corpus (Q2) is the guard. Records the decision + rationale.
B) An ML/LLM-based classifier for injection detection (rejected — CON-DET-1 + reintroduces the
   attack surface).
C) Other (please describe after [Answer]: tag below)

[Answer]: Deterministic PATTERN-BASED sanitizer — NO LLM inside the sanitizer (an LLM would be non-deterministic and itself a new injection surface; CON-DET-1). Stack: pdfplumber (parse), Pydantic v2 (SEC-2 validation gate), Decimal (money/threshold-exact). Confirmed.

## Question 12 — Parse/validation stack confirmation
Confirm the unit-local parse/validation stack (already implied by the brief/FD — recording it as a
decision).

A) **pdfplumber** (PDF text/field extraction) + **Pydantic v2** (the SEC-2 typed validation gate) +
   **`Decimal`** for all money/threshold-compared values, on **Python 3.11+**. No new dependencies
   beyond the brief's stack. Records decision + rationale + version pinning intent (exact pins are a
   Code-Gen concern).
B) A different parser or validation library (please describe — would need justification vs the brief).
C) Other (please describe after [Answer]: tag below)

[Answer]: (Tech-stack confirmation) Pydantic v2 for the validation gate, Decimal for all monetary/threshold values, deterministic pattern-based sanitizer — all consistent with the frozen FD; no LLM anywhere in intake+document-sanitizer.

---

## 4. Constraints & settled items held (not re-opened)
- The **Functional Design is frozen + approved** — NFR Requirements attaches quality targets to it,
  never re-opens the `ApplicantProfile` contract, the pipeline, or the derivations.
- **Infrastructure Design is SKIP/minimal for this unit** (logged) — pure-logic unit; infra owned by
  `database` (Postgres/DATA-5) + `deploy-config` (Render). The **sandboxed-parsing** concern is a
  **security NFR** handled here (Q1), not cloud-infra topology.
- **Ownership boundaries respected**: observability stack = `observability` unit; secrets = SEC-3 /
  `secrets-config`; CON-DET-1 / bias **verification** = `quality-gates`. This unit sets its own
  targets + what it emits/feeds.
- Guardrails: SEC-1, SEC-2, CON-DET-1, CON-BR1 (segregated demographics), DATA-4, advisory-only.
- Three settled non-edits stay closed: `PROJECT-BRIEF.md`, OOS-7 README/case-study doc commitment,
  `user-journey.md`.

---

## 5. Next step (STOP here)
Fill the twelve `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory
ambiguity-check (adding a clarification file only if needed), then generate the NFR Requirements
artifacts (`nfr-requirements.md`, `tech-stack-decisions.md`) and present the standardized 2-option
completion message. **No NFR Requirements artifacts or code are generated until the answers are in
and checked.**
