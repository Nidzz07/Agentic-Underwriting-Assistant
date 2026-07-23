# Code Generation Plan (Part 1) — `intake` + `document-sanitizer` (coupled pair)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: cluster unit 1 · FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure
Design SKIPPED (logged)** → **Code-Gen ← here — the FIRST CODE of the build.**
**Units covered**: U1 `intake` (SEC-2) + U2 `document-sanitizer` (SEC-1) — same coupled pass.
**Stories**: US-INTAKE-1, US-INTAKE-2, US-INTAKE-3 (intake) + US-INTAKE-4 (document-sanitizer).
**Date**: 2026-07-04
**Status**: **Plan — awaiting `[Answer]:` tags. NO CODE, NO TESTS, NO IMPLEMENTATION this stage.**
Stop after this plan.

This plan follows `.project-guide-rule-details/build/code-generation.md` (Part 1) + the project's
plan-then-generate discipline. **TDD is binding** (QA-6, pytest-cov ≥ 90%): **tests are written
FIRST, then implementation.** Code-Gen **builds ON** the frozen FD contracts, the approved NFR
targets, the NFR design patterns, and the 10 logical components — **re-opening none of them.**

---

## 1. Unit context (analyzed — Step 1)

### 1.1 What Code-Gen builds on (frozen — NOT re-opened)
- **FD contracts** (`build/intake/functional-design/`): `ApplicantProfile` (incl. segregated
  `demographics`, derived-and-stored `age_years_derived`/`bmi_derived`, `Decimal` money,
  system-assigned `application_id`), `DocumentManifest` (four-state), `SanitizedText` +
  `SanitizationReport`, `RejectedIntake`; the `parse → sanitize → gate` pipeline; DR-AGE/DR-BMI; the
  reject-vs-REFER four-state model; the SEC-1-FORENSIC invariant.
- **NFR targets** (`build/intake/nfr-requirements/`): the 10 `NFR-INT-*` pass/fail assertions.
- **NFR design patterns + 10 components** (`build/intake/nfr-design/`): SubprocessParseWorker,
  IpcCodec, ObfuscationNormalizer, PatternRegistry, SanitizerEngine, IntakeGate (boundary wrapper),
  DerivationFunctions, CanonSerAdapter, SanitizationReportChannel, TelemetryEmitter.

### 1.2 Dependencies & interfaces
- **Consumes**: uploaded documents + form data (from the FastAPI orchestrator, `backend/app/`).
- **Produces**: `ApplicantProfile | RejectedIntake` (to `rules-engine`), `SanitizationReport` (to
  `audit-store` via the audit channel), emitted telemetry (to `observability`).
- **Shared**: the **CANON-SER** implementation (defined by `audit-store §2.1`) — a **single shared
  utility** imported by intake's `CanonSerAdapter` and by `audit-store` (see Q2).
- **N/A layers** (code-generation.md step categories that do not apply — see Q5): **API layer**
  (owned by the FastAPI orchestrator composition root, not this unit), **Repository/persistence
  layer** (owned by `audit-store` + `database`), **Frontend** (backend unit), **DB migrations**
  (owned by `database`).

### 1.3 Monorepo placement (Q5=A single monorepo — `unit-of-work.md §2`)
```
backend/
├── intake/                      # UNIT: intake (C1)
│   ├── parser.py                #   SubprocessParseWorker + parse orchestration
│   ├── ipc_codec.py             #   IpcCodec (data-only canonical, no pickle)
│   ├── schema.py                #   ApplicantProfile / DocumentManifest / SanitizedText / RejectedIntake (Pydantic v2)
│   ├── derivations.py           #   DerivationFunctions (pure; DR-AGE/DR-BMI)
│   ├── validation_gate.py       #   IntakeGate (total-function boundary wrapper)
│   ├── canon_ser_adapter.py     #   CanonSerAdapter (delegates to common CANON-SER)
│   ├── telemetry.py             #   TelemetryEmitter (allowlist schema, no free-text field)
│   ├── sanitizer/               # UNIT: document-sanitizer (C1/SEC-1)
│   │   ├── sanitizer.py         #   SanitizerEngine
│   │   ├── pattern_registry.py  #   PatternRegistry (+ inert placeholder)
│   │   ├── normalizer.py        #   ObfuscationNormalizer (NFKC pipeline)
│   │   ├── report_channel.py    #   SanitizationReportChannel (audit-only)
│   │   └── tests/               #   co-located sanitizer tests
│   └── tests/                   #   co-located intake tests + fixtures (corpora C/L, mock PDFs)
└── common/                      # shared pure utilities (see Q2) — canon_ser.py (+ decimal_context.py)
```
*(Exact module split is refined at generation; the mapping above is the plan of record.)*

### 1.4 Guardrails held (skill)
- **CON-DET-1** (byte-identical derivations + IPC + CANON-SER round-trip); **SEC-1/SEC-2**;
  **SEC-1-FORENSIC** (3 surfaces, incl. telemetry + logs); **CON-BR1** (segregated demographics never
  influence *or* leak); **DATA-4** (synthetic fixtures only + active PII guard); advisory-only naming.

---

## 2. Code-Generation execution plan (numbered steps — TDD, tests FIRST)

**Discipline**: for each component, **its test suite is written before its implementation**; the
suite encodes the mapped `NFR-INT-*` assertion(s) + FD rule(s). Implementation order is **leaf-first,
then composing components**. Application code → `backend/…` (never `guide-docs/`); markdown summaries
→ `guide-docs/build/intake/code/`.

- [x] **Step 0 — Project structure setup (greenfield)**: create the `backend/intake/` +
  `backend/intake/sanitizer/` + `backend/common/` packages, co-located `tests/` dirs, and the
  pytest/pytest-cov config (≥90% gate). *(No app code yet — skeleton + config.)* **DONE 2026-07-04**
  — `backend/` skeleton + `pyproject.toml` (cov gate ≥90% scoped to `backend/intake`+`backend/common`;
  `posix_only`/`property` markers) + `backend/conftest.py` (Sharpening 1: auto-skip `posix_only` off-POSIX).
  Hypothesis added to `requirements.txt`.
- [x] **Step 1 — Shared CANON-SER utility (leaf)**: TEST FIRST (round-trip byte-identity) → implement
  `backend/common/canon_ser.py` (+ `decimal_context.py` if split, per Q2). Maps: NFR-INT-DET-2.
  **DONE 2026-07-04** — `common/canon_ser.py` (100% cov) + `common/decimal_context.py`; 18 tests incl.
  **Sharpening 3**: all four §2.1 properties asserted explicitly (P1 lexicographic key order, P2
  Decimal-as-string/float-rejected, P3 canonical scalars/null-explicit, P4 no volatile injection) +
  Hypothesis round-trip byte-identity property. Single shared impl (imported by intake + audit-store).
- [x] **Step 2 — `IpcCodec` (leaf)**: TEST FIRST (same input → byte-identical encoding; no-pickle;
  decode round-trip) → implement `intake/ipc_codec.py`. Maps: NFR-INT-SEC1-SANDBOX (IPC).
  **DONE 2026-07-04** — `intake/ipc_codec.py` (100% cov); 7 tests: byte-identical, insertion-order
  stable, UTF-8-JSON-not-pickle, data-only (rejects objects/bytes/float/non-str-keys), decode rejects
  malformed bytes. Distinct-from-CANON-SER canonical encoder for the parse-result shape.
- [x] **Step 3 — `schema.py` (data models, leaf)**: TEST FIRST (Pydantic v2 model validation; the
  segregated `demographics`; four-state `DocumentManifest`; `RejectedIntake` shape) → implement the
  FD contracts. Maps: FD `domain-entities.md` (frozen — implement exactly). **DONE 2026-07-04** —
  `intake/schema.py` (100% cov); frozen+extra-forbid value objects; `Money` type rejects float
  (BR-TYP-1); 14 tests. No new field/behavior beyond the FD.
- [x] **Step 4 — `DerivationFunctions` (leaf)**: TEST FIRST (byte-identical ×N≥10 + boundary cases
  age 18/65, BMI 25.00/30.00, leap-day, `as_of_date==DOB`, money-at-threshold) → implement pure
  DR-AGE/DR-BMI under the single `Decimal` context. Maps: NFR-INT-DET-1. **DONE 2026-07-04** —
  `intake/derivations.py` + `common/decimal_context.py` (both 100% cov); 14 tests incl. Hypothesis
  determinism property, leap-day Mar-1 convention, HALF_UP 2dp exact boundaries.
- [x] **Step 5 — `PatternRegistry` + placeholder (leaf)**: TEST FIRST — the **registry-invariant
  test** (∀ matcher: `matcher(placeholder)==no-match`; no match spans a placeholder boundary) +
  per-category matcher tests → implement the versioned registry + inert placeholder. Maps:
  NFR-INT-SEC1-NEUT (idempotence-by-construction property). **DONE 2026-07-04** —
  `sanitizer/pattern_registry.py` (100% cov); PUA-sentinel self-delimiting placeholder (ASCII-safe
  `chr(0xE000/0xE001)`); P1 inertness + P2 no-cross-boundary Hypothesis property; per-category matchers;
  sorted/merged non-overlapping runs.
- [x] **Step 6 — `ObfuscationNormalizer` (leaf)**: TEST FIRST (deterministic fixed pipeline;
  detection-only — `clean_text` unaffected) → implement NFKC→case-fold→collapse-ws→strip-zero-width.
  Maps: NFR-INT-SEC1-NEUT (obfuscation), CON-DET-1. **DONE 2026-07-04** — `sanitizer/normalizer.py`
  (100% cov); per-codepoint pipeline carrying an origin index-map (`NormalizedView.original_span`
  maps normalized matches back to original spans); Hypothesis monotonic-provenance property. Input
  never mutated (detection-only).
- [x] **Step 7 — `SanitizerEngine` (composes 5+6)**: TEST FIRST — the **neutralization corpus test**
  (100% over `C`), **idempotence** (`sanitize∘sanitize==sanitize`), **FP budget** (≤2.0% over `L`),
  and that `original_span` goes **only** to the report → implement `sanitizer/sanitizer.py`. Maps:
  NFR-INT-SEC1-NEUT. **DONE 2026-07-04** — `sanitizer/sanitizer.py` (100% cov) + curated static
  corpora `C` (22 adversarial incl. fullwidth/zero-width obfuscation) / `L` (60 benign) — **Sharpening 4**:
  corpora are checked-in STATIC files (reproducible by being static); role matcher precision-tuned;
  53 tests incl. Hypothesis idempotence (300 ex) + span-audit-only.
- [x] **Step 8 — `IntakeGate` (composes gate + derivations)**: TEST FIRST — the **total-function
  negative-input matrix** (never raises; unexpected exception → `RejectedIntake(malformed)`) + the
  **exhaustive reject-vs-REFER combination** suite (four-state × value-presence; thin-file →
  valid+incomplete→REFER) → implement `validation_gate.py`. Maps: NFR-INT-SEC2-TOTAL / -COVERAGE.
  **DONE 2026-07-04** — `intake/validation_gate.py` (100% cov); single fail-closed wrapper; injectable
  `application_id` generator seam; 40 tests incl. Hypothesis never-raises fuzz + three reason categories.
- [x] **Step 9 — `SubprocessParseWorker` + parse orchestration (composes IpcCodec)**: TEST FIRST
  (timeout/oom/crash → deterministic `unparseable`; isolation; canonical result) → implement
  `parser.py` (subprocess mechanism per Q4). Maps: NFR-INT-SEC1-SANDBOX **+ NFR-INT-PERF (hard bound —
  Sharpening 2)**. **DONE 2026-07-04** — `parser.py` (100%) + `resource_limits.py` (POSIX-guarded) +
  `parse_worker.py` (real pdfplumber, cov-omit) + fake worker. **Sharpening 1**: parent-kill wall-time
  test runs all platforms; RLIMIT_CPU/RLIMIT_AS tests `posix_only` (skip on Windows, run in Linux CI);
  all termination modes → deterministic `unparseable`; isolation + determinism verified.
- [x] **Step 10 — `CanonSerAdapter` (composes common CANON-SER)**: TEST FIRST (`ApplicantProfile`
  round-trip byte-identical via the shared spec) → implement `canon_ser_adapter.py`. Maps:
  NFR-INT-DET-2. **DONE 2026-07-04** — `intake/canon_ser_adapter.py` (100% cov); delegates to the
  single shared `common.canon_ser` (no parallel convention); 9 tests incl. **Sharpening 3** §2.1
  properties on the profile serialization + type-fidelity (replay dependency).
- [x] **Step 11 — `TelemetryEmitter` + `SanitizationReportChannel` (forensic surfaces)**: TEST FIRST
  — **schema-level assertion** (emitter schema has **no free-text/str field**) + **no-leak assertions
  across the 3 surfaces** (no `original_span` in any LLM-bound payload, in any emitted telemetry, in
  any log) → implement `telemetry.py` + `sanitizer/report_channel.py`. Maps: NFR-INT-FORENSIC,
  NFR-INT-OBS. **DONE 2026-07-04** — both 100% cov; allowlist `TelemetryEvent` (enums/ints/bools, no
  str field, extra-forbid); audit channel disjoint sole-carrier; 13 tests across all 3 surfaces.
- [x] **Step 12 — Pipeline wiring (`parse → sanitize → gate`)**: TEST FIRST (end-to-end unit
  integration: happy path, thin-file→incomplete, RejectedIntake) → wire the components into the
  frozen pipeline. *(FastAPI orchestrator composition is Build & Test / the orchestrator, not this
  unit.)* **DONE 2026-07-04** — `intake/pipeline.py` (100% cov); `IntakePipeline` composes
  parse→sanitize→gate with telemetry per stage + report routed to audit channel only; 8 integration tests.
- [x] **Step 13 — Active PII CI guard (DATA-4)**: implement the build/test check that **fails on any
  real-PII pattern** in fixtures/artifacts; confirm all fixtures (corpora `C`/`L`, mock PDFs) are
  synthetic (Q3). Maps: NFR-INT-DATA4. **DONE 2026-07-04** — `intake/pii_guard.py` (100% cov; CLI
  exits non-zero on findings, skips `test_*.py` positive vectors) + seeded `synthetic_profiles.py`
  (**Sharpening 4** — seeded/reproducible, distinct from static corpora, PII-free); guard runs green
  over the unit tree; 13 tests.
- [x] **Step 14 — Coverage gate + documentation**: confirm pytest-cov **≥90%** for the unit; write the
  **code summary** to `guide-docs/build/intake/code/` (markdown only — modules created, tests→target
  map, coverage). *(The blocking-gate aggregation is `quality-gates`; this unit authors its own tests.)*
  **DONE 2026-07-04** — full suite **212 passed / 3 posix_only skipped / 99.53% coverage** (gate
  `--cov-fail-under=90` reached); code summary written to `guide-docs/build/intake/code/code-summary.md`.
- [x] **Step 15 — Present the standardized 2-option completion message** (code-generation.md Step 14
  format) → Request Changes / Continue → next cluster unit's Code-Gen (`rules-engine`) per the
  dependency order. **DONE 2026-07-04 — presented; STOPPED for review (do not advance to rules-engine).**

**N/A step-categories** (code-generation.md Step 2 list — justified skips): **API Layer**, **Repository
Layer**, **Frontend Components**, **Database Migration** — see §1.2 / Q5 (owned by the orchestrator /
`audit-store` / `database`; this unit is a pure-logic library). **Deployment artifacts**: none unit-local
(owned by `deploy-config`).

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These decide **Code-Gen specifics** — they do **not** re-open the FD / NFR targets / patterns.

## Question 1 — Test framework + property-based testing
What is the test toolchain (TDD, ≥90%)?

A) **pytest + pytest-cov (≥90%, QA-6)** as the base, **plus Hypothesis** for the **property-based
   invariants** (idempotence `sanitize∘sanitize==sanitize`, CANON-SER round-trip byte-identity,
   byte-identical derivations) alongside the explicit corpus/matrix/boundary tests (parametrized).
   Property-based testing is the natural fit for "holds ∀ input" invariants.
B) pytest + pytest-cov only, no property-based testing (explicit example tests only).
C) A different framework (describe).
D) Other (please describe after [Answer]: tag below)

[Answer]: pytest + Hypothesis. pytest for the suite; Hypothesis (property-based) for the universal-quantifier properties this unit rests on — idempotence (sanitize∘sanitize==sanitize ∀x), placeholder-inertness (∀ matcher: no match, no match spans a placeholder boundary), total-function-never-raises (∀ input → ApplicantProfile|RejectedIntake). Hypothesis generates adversarial inputs to falsify these, far stronger than example-based tests for "holds for all inputs" claims.

## Question 2 — Shared CANON-SER (and Decimal-context) module placement
Where does the **single** CANON-SER implementation live so intake's `CanonSerAdapter` and
`audit-store` both import it (no copy-paste)?

A) **A neutral shared package `backend/common/`** — `common/canon_ser.py` (+ `common/decimal_context.py`
   for the single declared `Decimal` context) — imported by **both** `audit-store` and intake's
   `CanonSerAdapter`. **Single implementation, no copy-paste, no awkward intake→audit-store dependency
   direction.** (audit-store §2.1 remains the *spec authority*; `common/` holds the shared *implementation*.)
B) Inside `audit-store` (`backend/services/…`), imported by intake (creates an intake→audit-store
   import dependency).
C) Duplicated per unit tuned to match (rejected — the parallel-convention drift bug the audit-store
   correction fixed).
D) Other (please describe after [Answer]: tag below)

[Answer]: backend/common/ — the single CANON-SER implementation of audit-store's §2.1 spec, placed in common so BOTH intake's CanonSerAdapter and audit-store import it (one implementation, not copy-pasted). Ownership stays audit-store's spec; common is only the shared location. Dependency direction: intake references audit-store's spec via the shared utility.

## Question 3 — Fixture / synthetic-data strategy (DATA-4)
How are the test corpora + document fixtures built, zero real PII?

A) **Unit-local synthetic fixtures** — the adversarial injection corpus `C` and legitimate-text
   corpus `L` are **curated files** under `intake/sanitizer/tests/`; mock PDFs + form data via
   **Faker** (seeded) + hand-authored samples under `intake/tests/`. The **active PII guard** (Step 13)
   scans fixtures/artifacts and **fails** on any real-PII pattern. The shared 300+ synthetic profile
   corpus (from the Phase-1 `corpus-generator` unit) is **not** a dependency of these unit tests —
   intake uses its own small deterministic fixtures. All synthetic (DATA-4).
B) Depend on `corpus-generator`'s output for intake's unit tests (couples the unit test to another
   unit's build-time artifact).
C) Other (please describe after [Answer]: tag below)

[Answer]: Seeded synthetic fixtures (reproducible), unit-local to intake's tests, scanned by the active PII CI guard (fails build on any real-PII pattern, DATA-4). These are intake's own small targeted synthetic profiles — DISTINCT from the separate CorpusGenerator unit (build-time seeded corpus, its own unit); no coupling to the corpus.

## Question 4 — Subprocess mechanism (bounded, killable, NO pickle across the boundary)
How is the ephemeral parse subprocess implemented so it honors the **no-pickle** IpcCodec design?

A) **`subprocess` running a parse-worker entrypoint** — the parent spawns a child process that runs
   pdfplumber and **writes the canonical, data-only encoded parse result to stdout** (via `IpcCodec`);
   the parent **reads + decodes those bytes** — **no pickle** (stdout is controlled bytes). Resource
   bounds via **`resource.setrlimit`** (memory/CPU) in the child on **POSIX/Linux (Render)** + a
   **wall-time timeout** on the parent read; timeout / non-zero exit → **`unparseable`**. **Windows
   (dev) fallback**: timeout-only (documented). Cleanest fit for no-pickle + setrlimit.
B) **`multiprocessing` with a Queue/Pipe** passing the **canonical bytes** (NOT the pickled return
   object) — `spawn` start method; resource bounds via `setrlimit` in the child. (Also viable, but
   care needed to avoid multiprocessing's default pickle of the return value.)
C) In-process with only a timeout (rejected — NFR-INT-SEC1-SANDBOX requires process isolation).
D) Other (please describe after [Answer]: tag below)

[Answer]: subprocess + canonical stdout bytes (the IpcCodec data-only, no-pickle encoding via stdout) + setrlimit (OS-level memory/CPU/time bounds — kernel kills on limit). Timeout enforced by the PARENT (parent kills the subprocess on timeout → deterministic `unparseable`) AND setrlimit's CPU-time limit — belt-and-suspenders, so neither a hung parse nor a CPU-spin escapes. No pickle anywhere; OS-level process isolation, not a thread.

## Question 5 — Confirm the N/A step-categories (unit scope)
code-generation.md Step 2 lists API/Repository/Frontend/DB-migration step categories. Confirm they
are **N/A** for this pure-logic unit?

A) **Confirm N/A with justification** — **API Layer** = owned by the FastAPI orchestrator composition
   root (`backend/app/`), not this unit; **Repository/persistence** = owned by `audit-store` +
   `database`; **Frontend** = backend unit; **DB migrations** = owned by `database`; **deployment
   artifacts** = owned by `deploy-config`. This unit generates **business logic + its tests + a code
   summary** only. (The pipeline's HTTP entrypoint + persistence wiring are exercised in Build & Test
   / the orchestrator.)
B) Some of these DO apply to this unit (describe which + why).
C) Other (please describe after [Answer]: tag below)

[Answer]: Confirmed N/A for this unit: API layer (FastAPI orchestrator / other units), repository + DB-migration (database + audit-store own persistence), frontend (C5 UI units). intake is a pure-logic backend library — generating these layers here would violate ownership. N/A, owned elsewhere.

---

## 4. Story traceability
| Story | Covered by (steps) |
|---|---|
| US-INTAKE-1 (parse → validated `ApplicantProfile`) | Steps 3, 8, 9, 12 |
| US-INTAKE-2 (pdfplumber + Pydantic v2; malformed rejected at the gate) | Steps 8, 9 |
| US-INTAKE-3 (thin-file / single-missing-doc → processable → REFER) | Steps 8, 12 |
| US-INTAKE-4 (document-sanitizer: neutralize injection, SEC-1) | Steps 5, 6, 7, 11 |

## 5. Constraints & settled items held (not re-opened)
- **Frozen FD contracts + approved NFR targets + design patterns + 10 components** are the inputs —
  Code-Gen implements them exactly; it re-opens none.
- **TDD binding**: tests FIRST, pytest-cov ≥ 90% (QA-6). No code this stage — **plan only**.
- **Ownership reference-not-own**: shared CANON-SER (single utility, Q2); observability stack /
  secrets / quality-gates harness / persistence / cloud infra owned elsewhere. **Infrastructure
  Design SKIPPED (logged)**.
- Three settled non-edits stay closed: `PROJECT-BRIEF.md`, OOS-7 README/case-study doc commitment,
  `user-journey.md`.

---

## 6. Next step (STOP here)
Fill the five `[Answer]:` tags above. On your signal, I will read the answers, run the ambiguity-
check (adding a clarification file only if needed), then **execute Part 2 (Generation)** — writing
the tests FIRST, then the implementation, step-by-step per §2, and present the standardized 2-option
completion message. **NO code, NO tests, NO implementation is written until the answers are in and
checked and you give the explicit go.**
