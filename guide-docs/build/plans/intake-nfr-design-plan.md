# NFR Design Plan — `intake` + `document-sanitizer` (coupled pair)

**Phase / Stage**: BUILD → NFR Design (per-unit, plan-then-generate)
**Loop position**: cluster unit 1 · FD ✅ 2026-07-03 · NFR Requirements ✅ 2026-07-04 → **NFR Design
← here** → ~~Infrastructure Design (SKIP/minimal — log the skip)~~ → **Code-Gen (first code of the
build; TDD ≥90%)**.
**Units covered**: U1 `intake` (SEC-2) + U2 `document-sanitizer` (SEC-1) — same coupled pass.
**Depth**: comprehensive (security-critical).
**Date**: 2026-07-04
**Status**: **Plan — awaiting `[Answer]:` tags.** No NFR Design artifacts generated yet. Stop after
this plan.

This plan follows `.project-guide-rule-details/build/nfr-design.md`. NFR Design is the **"how" for
each "what"** — it turns the approved **NFR-INT-* targets** (the *what*) into concrete **design
patterns + logical components** (the *how*), built **ON the frozen FD and the approved NFR
targets — re-opening neither.** No code yet; that is Code-Gen.

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 Inputs this stage builds on (frozen — not re-opened)
- **Frozen FD** (`guide-docs/build/intake/functional-design/`): the `ApplicantProfile` contract, the
  `parse → sanitize → gate` pipeline, DR-AGE/DR-BMI, the four-state reject-vs-REFER model, the
  SEC-1-FORENSIC invariant.
- **Approved NFR Requirements** (`guide-docs/build/intake/nfr-requirements/`): the 10 testable
  `NFR-INT-*` targets + `tech-stack-decisions.md` (D1–D7: pdfplumber subprocess-isolated, Pydantic v2
  gate, deterministic pattern sanitizer **no LLM**, `Decimal`, Python 3.11+, reference CANON-SER §2.1).

### 1.2 What NFR Design produces (the "how")
For **each** approved target, a **design pattern** + the **logical components** that realize it:
| Target (the "what") | Pattern to design (the "how") |
|---|---|
| NFR-INT-SEC1-SANDBOX | The **subprocess-isolation pattern**: bounded/killable worker, the **IPC contract** (canonical parse-result encoding), `timeout → unparseable`, the **in-process/subprocess split**. |
| NFR-INT-SEC1-NEUT | The **deterministic sanitizer neutralization pattern**: pattern-matching design achieving 100% neutralization + idempotence within the FP budget (the "how" of SR-DETECT/SR-NEUTRALIZE). |
| NFR-INT-SEC2-TOTAL / -COVERAGE | The **total-function gate pattern**: every input → valid `ApplicantProfile` or `RejectedIntake`, no unhandled raise; the combination-coverage structure. |
| NFR-INT-FORENSIC | The **forensic-exclusion pattern**: structural input-type exclusion (LLM) **+** the **telemetry-scrubbing pattern** (forensic-free emitted signals). |
| NFR-INT-DET-1 / -DET-2 | The **determinism pattern**: byte-identical derivations + CANON-SER **round-trip** (referencing audit-store §2.1). |
| NFR-INT-OBS | The **emit-only observability pattern**: the forensic-free signal set + how it is emitted (stack referenced, not owned). |
| NFR-INT-PERF | The **bounded-performance pattern**: soft budget instrumentation + the hard timeout as the guarantee. |

### 1.3 Guardrails held (skill)
- **CON-DET-1** (determinism — the subprocess must not introduce non-determinism into the persisted
  outputs; replay never re-parses); **SEC-1/SEC-2** (defense patterns single-sourced); **SEC-1-FORENSIC**
  (audit-only, incl. telemetry); **CON-BR1** (segregated demographics — never in influence *or*
  telemetry); **DATA-4**; advisory-only naming.

### 1.4 Ownership boundaries (reference-not-own — carried from NFR Requirements)
- Observability **stack** → `observability` unit (this unit emits only); **secrets** → `secrets-config`
  / SEC-3; **blocking-gate harness** → `quality-gates` (this unit authors its own tests at Code-Gen);
  **persistence** → `audit-store` / `database`; **cloud infra** → `deploy-config` / `database`
  (**Infrastructure Design SKIPPED** for this unit — the sandbox is a security NFR, not cloud topology).

---

## 2. NFR Design execution plan (checkboxes — Step 2)

Artifacts to be generated **after** answers are collected and ambiguity-checked (per nfr-design.md
Step 6) → `guide-docs/build/intake/nfr-design/` → `nfr-design-patterns.md`, `logical-components.md`.
Mermaid diagrams **required** (nfr-design.md Step 6 — validated against the 7 rules + text alternative).

- [x] **P1. Analyze NFR Requirements + the frozen FD** (§1 above — done).
- [x] **P2. Collect `[Answer]:` tags** (§3); run the ambiguity-check; raise a clarification file if any
  answer is vague. **DONE 2026-07-04 — all 12 answered (all A + notes); ambiguity-check CLEAN (no
  clarification file). 5 design-elaborations for generation (see audit 2026-07-04T13:00 entry) —
  sharpenings: Q5 pin NFKC + fixed ordered detection-only pipeline; Q4 idempotence structural ONLY
  if the placeholder is provably inert (unmatched + non-combinable) — pin + registry-invariant test;
  Q7 telemetry schema has NO str field + forensic-free extends to LOGS; Q2 IpcCodec own canonical
  encoder no-pickle; Q9 CanonSerAdapter delegates to a single shared CANON-SER utility. Awaiting
  explicit go to generate.**
- [x] **P3. `nfr-design-patterns.md`** — the design pattern for each `NFR-INT-*` target (§1.2): the
  subprocess-isolation pattern (+ IPC contract + timeout→unparseable + in-proc/subproc split), the
  sanitizer neutralization pattern, the total-function gate pattern, the forensic-exclusion +
  telemetry-scrubbing pattern, the determinism + CANON-SER-round-trip pattern, the emit-only
  observability pattern, the bounded-performance pattern. Each pattern traces to its target + states
  how the target's assertion is **structurally** met. Mermaid (validated + text alternative).
- [x] **P4. `logical-components.md`** — the logical components the patterns introduce (e.g. a
  `ParseWorker`/subprocess boundary, an `IpcCodec` canonical encoder, a `SanitizerEngine` +
  `PatternRegistry`, the `ValidationGate` total-function wrapper, a `TelemetryEmitter` forensic-free
  filter, a `CanonSerAdapter` referencing audit-store §2.1) and their integration — **logical only**,
  no code. Mermaid component view (validated + text alternative).
- [x] **P5. Consistency + ownership check** — patterns build on the frozen FD + approved targets
  (re-open neither); reference-not-own held; every pattern maps to a target whose assertion it makes
  structurally achievable at Code-Gen.
- [x] **P6. Guardrail compliance pass + present the standardized 2-option completion message**
  — **APPROVED at the gate 2026-07-04** (Continue). Per the loop: **Infrastructure Design SKIPPED
  (logged, guide-state.md + audit.md) → Code-Gen Part 1 (Plan) being written** for
  `intake` + `document-sanitizer`.

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These decide **design patterns** — they do **not** re-open the FD or the approved NFR targets.

### A. Subprocess-isolation pattern (NFR-INT-SEC1-SANDBOX)

## Question 1 — Subprocess worker model + lifecycle
How is the bounded/killable parse subprocess structured?

A) **Per-parse ephemeral worker** — each document parse spawns a fresh short-lived subprocess with
   resource limits (memory/CPU/wall-time), runs pdfplumber, returns the extracted result, and exits;
   a timeout/oom/crash **kills the worker** and the parse is recorded `unparseable`. Simple, strong
   isolation (no state carried between documents), fits a stateless request path.
B) **Long-lived worker pool** — a persistent pool of sandboxed workers receives parse jobs (lower
   spawn overhead, but carries state/complexity; risk of cross-job contamination).
C) **Thread-based isolation** — rejected (a hostile PDF that hangs/segfaults a thread is not
   contained; threads share memory).
D) Other (please describe after [Answer]: tag below)

[Answer]: Ephemeral subprocess per parse (fresh worker spawned per PDF, killed after). Threads don't isolate (a native parser crash/exploit takes the process down — no memory boundary); a pool risks state bleed between parses (isolation + determinism hazard). Ephemeral = full isolation, no state carryover, clean kill-after-timeout, deterministic (each parse starts clean). Spawn overhead is acceptable (soft latency budget, not an SLA).

## Question 2 — IPC contract (canonical encoding of the parse result crossing the boundary)
What crosses the subprocess boundary, and how is it kept deterministic (NFR-INT-SEC1-SANDBOX
"canonically encoded")?

A) **A typed, canonically-encoded parse-result DTO** — the worker returns only **extracted
   text/fields** (never live objects), serialized with a **stable, deterministic encoding** (stable
   field order, explicit UTF-8, no Python-repr/pickle of arbitrary objects) so the **same PDF → same
   bytes** across the hop. The parent deserializes into the draft field-set. **No code executes in the
   parent from the worker's output** (data only — defense against a hostile parse result).
B) Pickle the pdfplumber objects across the boundary (rejected — non-canonical + unsafe
   deserialization of untrusted-derived data).
C) Shared memory / temp files with ad-hoc formatting (rejected — ordering/encoding non-determinism).
D) Other (please describe after [Answer]: tag below)

[Answer]: IPC contract = canonically-encoded, data-only, NO PICKLE. Pickle is non-deterministic (object identity/ordering) and a deserialization attack surface. The parse result crossing the boundary is data-only (extracted text + structured fields, no code/objects) in a fixed-schema canonical encoding, so the same PDF yields byte-identical IPC output — no non-determinism at the boundary.

## Question 3 — In-process / subprocess split boundary (determinism)
Where exactly is the line between subprocess and in-process work?

A) **Subprocess = the untrusted-PDF parse ONLY** (pdfplumber extraction). **In-process = everything
   after**: sanitize (SEC-1), the SEC-2 gate, and the deterministic derivations (DR-AGE/DR-BMI,
   `Decimal`). Rationale: derivations must be deterministic and are on the replay-relevant path;
   keeping them in-process (on already-validated data) avoids any process-hop non-determinism. The
   subprocess is upstream of persistence and **outside the replay path** (replay uses the snapshot).
B) Subprocess also runs sanitize + gate (rejected — pulls deterministic/security-gate logic into the
   isolated boundary unnecessarily; the gate must own the reject decision in-process).
C) Other (please describe after [Answer]: tag below)

[Answer]: Split — untrusted PARSE runs in the ephemeral subprocess; validation + the deterministic derivations (age/BMI/Decimal) run IN-PROCESS on the returned canonical data. Only the untrusted parse is isolated; the deterministic pipeline is in-process, outside the subprocess and outside the replay path.

### B. Sanitizer neutralization pattern (NFR-INT-SEC1-NEUT)

## Question 4 — Pattern-matching design (how 100% neutralization + idempotence is achieved)
What is the sanitizer's internal design?

A) **A versioned `PatternRegistry` of deterministic matchers** (one per category: `instruction_override`,
   `role_injection`, `delimiter_escape`, `tool_mimic`, + obfuscation-normalization pre-pass), applied
   in a **fixed order** over normalized text; each match is **defanged to an inert placeholder** and
   logged to the `SanitizationReport`. **Idempotence by construction**: placeholders are inert and not
   re-matched, so a second pass is a no-op. The registry is **data/versioned** (testable against corpus
   `C`), pure Python, **no LLM** (D4). FP budget managed by matcher precision + the `L`-corpus test.
B) A single monolithic regex (rejected — unmaintainable, hard to prove idempotence/coverage).
C) A stateful/learned matcher (rejected — non-deterministic, CON-DET-1).
D) Other (please describe after [Answer]: tag below)

[Answer]: Versioned PatternRegistry of deterministic matchers — fixed application order, defang-to-placeholder, idempotent BY CONSTRUCTION (once a pattern is replaced by a neutral placeholder, a re-run finds nothing to defang → sanitize∘sanitize == sanitize holds structurally, not just by test), NO LLM. The registry is versioned so the pattern set is itself auditable.

## Question 5 — Obfuscation handling (robustness within the FP budget)
Injection often hides via obfuscation (spacing, homoglyphs, casing, zero-width chars). How is that
handled without blowing the FP budget?

A) **A deterministic normalization pre-pass** (case-fold, collapse whitespace, strip zero-width,
   fold common homoglyphs) **applied only for detection** — matching runs on the normalized view, but
   **neutralization edits map back to the original span** (so `clean_text` stays faithful except for
   defanged spans). Normalization is **bounded + documented** so it doesn't over-trigger on benign
   text (keeps FP ≤ budget). Deterministic.
B) No normalization — match raw text only (rejected — trivially bypassed by obfuscation, misses
   corpus `C`).
C) Aggressive normalization that rewrites all text (rejected — high FP, corrupts benign content).
D) Other (please describe after [Answer]: tag below)

[Answer]: Obfuscation-normalization = a DETECTION-ONLY pre-pass (normalize unicode/spacing tricks for matching, don't aggressively rewrite legitimate text — stays within the FP budget). The normalization must itself be DETERMINISTIC — a fixed unicode normalization form (choose explicitly, e.g. NFKC) applied identically every run — so the pre-pass introduces no non-determinism.

### C. Total-function gate + forensic exclusion

## Question 6 — Total-function gate pattern (NFR-INT-SEC2-TOTAL, never raises)
How is "never raises — every input → `ApplicantProfile | RejectedIntake`" structurally guaranteed?

A) **A single boundary wrapper around the Pydantic v2 gate** that converts **every** failure mode into
   a structured `RejectedIntake`: Pydantic `ValidationError` → per-field errors + `reason_category`;
   parse-failure/`unparseable` → `unparseable`; empty/oversized/wrong-type/corrupt → mapped category;
   **any unexpected exception is caught at the boundary and mapped to `malformed`** (fail-closed, no
   leak, no raise). The wrapper is the **only** exit point → the return type is provably
   `ApplicantProfile | RejectedIntake`. The negative-input matrix (NFR-INT-SEC2-TOTAL) tests it.
B) Rely on Pydantic's exceptions propagating and handle them at the API layer (rejected — not a total
   function at the unit boundary; leaks raises).
C) Other (please describe after [Answer]: tag below)

[Answer]: Total-function gate = a single boundary wrapper: every failure path maps to ApplicantProfile | RejectedIntake; an UNEXPECTED exception maps to RejectedIntake(malformed), fail-closed. No input can cause an unhandled raise — an unanticipated error becomes a safe rejection, never a leak or a crash.

## Question 7 — Forensic-exclusion + telemetry-scrubbing pattern (NFR-INT-FORENSIC)
How are the two exclusions (LLM context **and** telemetry) structurally guaranteed?

A) **Two structural mechanisms**: (i) **LLM**: the `SanitizationReport`/`original_span` travels a
   **separate audit channel** to `audit-store` and is **never** placed in the object handed toward
   `memo-agent-core` (whose `MemoAgentInput` type structurally cannot carry it); (ii) **Telemetry**: a
   **`TelemetryEmitter` with an allowlisted signal schema** — it accepts only counts/enum-categories/
   durations/statuses and **structurally cannot carry span text** (no free-text field; the span types
   are not part of its schema). Both are **assertion-tested** (no LLM-bound payload / no telemetry
   payload references span text). Belt-and-suspenders (structural + test).
B) Redact span text at emit/prompt time (rejected — relies on redaction, not structural exclusion).
C) Other (please describe after [Answer]: tag below)

[Answer]: Forensic exclusion, two structural mechanisms: (1) spans go ONLY to a separate audit channel (the audit-store lane); (2) a TelemetryEmitter with an ALLOWLISTED schema that structurally cannot carry span text — it can only emit permitted fields (counts, enum categories, durations, statuses), so there is no field through which original or neutralized span text could be emitted. Structural, not disciplinary.

### D. Determinism + observability patterns

## Question 8 — Determinism pattern (NFR-INT-DET-1 byte-identical derivations)
How are the derivations structurally kept byte-identical?

A) **Pure deterministic functions** — DR-AGE/DR-BMI/`Decimal` derivations are **pure** (inputs → output,
   no wall-clock, no unseeded randomness, no dict-order reliance); a **single declared `Decimal`
   context** (precision + `ROUND_HALF_UP`) is set for the unit so rounding is identical everywhere;
   derived values are **computed once and stored** (FD) so no consumer re-derives divergently. The
   ×N≥10 + boundary tests (NFR-INT-DET-1) assert it.
B) Derive lazily per consumer (rejected — re-derivation divergence risk; FD already stores them).
C) Other (please describe after [Answer]: tag below)

[Answer]: Determinism = pure derivation functions (no side effects, no wall-clock, no randomness) + a SINGLE fixed Decimal context (precision + ROUND_HALF_UP set once, applied everywhere) — so every money/ratio derivation uses identical rounding with no per-call context drift.

## Question 9 — CANON-SER round-trip pattern (NFR-INT-DET-2, the replay dependency)
How is the `ApplicantProfile` round-trip made byte-identical against audit-store's §2.1 spec?

A) **A `CanonSerAdapter` that references audit-store's single CANON-SER spec (§2.1)** — it does **not**
   re-declare the convention; it applies the shared spec (stable field order, `Decimal`-as-string,
   canonical enums, `null` explicit) to the `ApplicantProfile` (incl. segregated `demographics` +
   nested `DocumentManifest`). Round-trip `serialize → deserialize → serialize` is byte-identical
   (tested). This is the **replay dependency**: audit-store persists via this spec and `ReplayService`
   deserializes back to feed `evaluate()`. Single source of truth, no drift.
B) A local serialization tuned to match audit-store's (rejected — parallel convention, drift risk —
   the exact cross-unit bug the audit-store correction fixed).
C) Other (please describe after [Answer]: tag below)

[Answer]: CanonSerAdapter = an adapter that REFERENCES audit-store's §2.1 CANON-SER spec (delegates to the single spec, does NOT re-implement) for the ApplicantProfile round-trip. One serialization implementation, referenced — the replay dependency stays drift-free.

## Question 10 — Emit-only observability pattern (NFR-INT-OBS)
How does the unit emit signals without owning the stack?

A) **Emit through a thin, stack-agnostic instrumentation seam** — the unit calls a small internal
   `emit(event)` interface (spans for parse/sanitize/gate; counters for neutralization-count, reject
   `reason_category`, `incomplete`; derivation timings). The **`observability` unit wires** that seam
   to Langfuse/Prometheus/Grafana. The seam enforces the **forensic-free allowlist** (Q7-ii) so no
   span text can be emitted. This unit **references, does not own**, the stack.
B) Import and configure Langfuse/Prometheus clients directly here (rejected — owned by observability).
C) Other (please describe after [Answer]: tag below)

[Answer]: Observability = an emit-only instrumentation seam: the unit emits through the allowlisted TelemetryEmitter (Q7); collection/aggregation (Langfuse/Prometheus/Grafana) is the observability unit's. Emit-only, stack referenced-not-owned.

### E. Resilience / performance patterns

## Question 11 — Resilience pattern for the parse boundary (failure handling)
Beyond the timeout kill, what is the resilience posture for parse failures?

A) **Fail-closed to a recorded outcome, no retry of hostile input** — a worker crash/timeout/oom →
   the document is recorded `unparseable` (deterministic), the pipeline continues (other documents +
   the gate decide reject-vs-REFER); **no automatic re-parse of the same untrusted input** (a hostile
   PDF would just re-trigger). Retry/backoff/dead-letter for *transient infra* faults is a
   cross-cutting concern deferred to NFR/infra of the orchestration, **not** re-designed here.
B) Retry the parse N times on failure (rejected for hostile input — wasteful, re-triggers the attack;
   and non-deterministic if timing-dependent).
C) Other (please describe after [Answer]: tag below)

[Answer]: Resilience = fail-closed-to-unparseable, NO retry of hostile input. A timed-out/failed parse → deterministic `unparseable` status; do NOT retry (retrying a malicious PDF designed to hang just re-triggers the attack). Fail closed. (Distinct from the memo's benign citation-retry — that retries the LLM's own draft; this is untrusted external input, never retried.)

## Question 12 — Performance instrumentation pattern (NFR-INT-PERF, soft budget)
How is the soft latency budget realized without becoming a hard SLA?

A) **Observed + recorded, not enforced** — emit the parse→sanitize→gate duration via the Q10 seam so
   the `observability` dashboard can track the **p95 soft budget**; the only **enforced** timing is the
   **hard subprocess timeout** (which is a security bound, tested). No latency-based failing/circuit
   behavior in this unit (correctness/security/determinism over speed). Budget breaches are a
   dashboard signal, not a build failure.
B) Enforce the latency budget with a failing check / circuit breaker (rejected — it's a soft budget,
   not an SLA; this is a validation build).
C) Other (please describe after [Answer]: tag below)

[Answer]: Performance = observed/recorded (p95 measured for visibility, NOT a gating assertion — no test fails on latency) + only the HARD subprocess timeout enforced (the kill bound). Soft budget observed, hard bound enforced.

---

## 4. Constraints & settled items held (not re-opened)
- **Frozen FD + approved NFR targets** are the inputs — NFR Design adds patterns/components, re-opens
  neither the `ApplicantProfile` contract/pipeline/derivations nor the `NFR-INT-*` assertions.
- **tech-stack decisions settled** (D1–D7): pdfplumber (subprocess-isolated), Pydantic v2 gate,
  deterministic pattern sanitizer **no LLM**, `Decimal`, Python 3.11+, **reference CANON-SER §2.1**.
- **Ownership reference-not-own**: observability stack / secrets / quality-gates harness / persistence
  / cloud infra owned elsewhere. **Infrastructure Design SKIPPED** for this unit (log the skip when
  reached) — the sandbox is a **security NFR**, not cloud topology.
- Guardrails: CON-DET-1, SEC-1, SEC-2, SEC-1-FORENSIC (incl. telemetry), CON-BR1, DATA-4, advisory-only.
- Three settled non-edits stay closed: `PROJECT-BRIEF.md`, OOS-7 README/case-study doc commitment,
  `user-journey.md`.

---

## 5. Next step (STOP here)
Fill the twelve `[Answer]:` tags above. On your signal, I will read the answers, run the ambiguity-
check (adding a clarification file only if needed), then generate the NFR Design artifacts
(`nfr-design-patterns.md`, `logical-components.md`, with validated Mermaid + text alternatives) and
present the standardized 2-option completion message. **No NFR Design artifacts or code are generated
until the answers are in and checked.** After NFR Design: **Infrastructure Design is SKIPPED (logged)
→ Code-Gen** — the first code of the build (TDD, ≥90%).
