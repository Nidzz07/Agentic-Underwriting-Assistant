# Code Generation Plan (Part 1) — `observability` (EPIC-6 / U21, Phase 2)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `observability` (U21) · FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure Design ✅ (approved 2026-07-18)**
→ **Code Generation ← here (the 5th and LAST of U21's 5 stages)**.
**Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Date**: 2026-07-18 · **Depth**: **comprehensive**.
**Status**: **Plan — awaiting `[Answer]:` tags. NO code generated; NO `backend/observability/` created; `requirements.txt` NOT edited. Stop after this plan.**

Built **ON** the frozen FD (`domain-entities.md` / `business-rules.md` **BR-OBS-1..7** / `business-logic-model.md`), the approved
`nfr-requirements.md` (**eleven `NFR-OBS-*`** + `tech-stack-decisions.md` **OBS-D1..D9**), the approved NFR Design
(`nfr-design-patterns.md` **P-OBS-1..11** + `logical-components.md` **C-OBS-1..4** — exact signatures), and the approved
Infrastructure Design (`infrastructure-design.md` + `deployment-architecture.md`, **INFRA-OBS-Fold-1..3**) — **re-opening none**.
**`OBS-SINK-DEFERRED`'s refined scope is honored**: the **only** genuinely deferred item is the **per-internal-graph-node
callback** (INFRA-OBS-Fold-1c); everything else in the trace/metric binding design is **named and realized as application code here**
as the injected **Protocols + offline fakes** (the live SDK binding itself stays composition/deploy-config's — Code-Gen builds no live
integration).

---

## 1. Unit context (analyzed — NOT re-opened)

### 1.1 What Code-Gen realizes (from the frozen substrate)
- **C-OBS-1..4** (NFR Design, exact signatures): `trace-side` (`TraceSink` Protocol + `TraceRecorder.on_step`/`span`, two callers),
  `metric-side` (`MetricExporter` Protocol + `derive_from_event`/`derive_from_step_outcome` + the ~5 `MetricDefinition`s, distinct
  `_EVENT_ALLOWED`/`_STEP_ALLOWED`), the shared plane-neutral `allowlist` (`project_allowlisted`), the `StructuralGuard` substrate
  (5 AST scans, each with a detector self-test).
- **The ~5 metrics** (`domain-entities.md §4`): **emitter-sourced (3)** → `derive_from_event` — *decisions by recommendation type*
  (counter, `MemoTelemetryEvent.recommendation`) · *decision latency* (histogram, `MemoTelemetryEvent.duration_ms`) ·
  *rule-evaluation duration* (histogram, `rules_engine` telemetry `evaluate_micros`); **step-outcome (2)** → `derive_from_step_outcome`
  — *LLM-call errors* (counter, provider-error step outcome) · *outlier-flag rate* (counter-gauge, U18 `OutlierResult.is_outlier`).
- **The two real graph paths** (U4's frozen `orchestrator.py`, CAP=`MEMO_CITATION_RETRY_CAP`=2): **finalize** =
  `[draft, validate, finalize]` (**3** node executions) · **retry-then-flag** = `[draft, validate, draft, validate, flag]` (**5** at CAP=2).

### 1.2 Reference boundaries (owned elsewhere — consumed only, never authored/edited)
- **`memo-agent-core` (U4)** — the frozen `telemetry: Optional[TelemetryEmitter]` constructor seam (metric plane, Fold-1a) + the
  span-wrappable `run()` (trace plane, Fold-1b) — **consumed as documented; U4's production module + its frozen test file NOT imported**.
- **`secrets-config` (U16)** — the frozen `Settings` model (`extra="ignore"`) — **untouched**; the reserved `LANGFUSE_*` shapes are a
  deploy/composition concern, **not** code here.
- **the live `langfuse` / `prometheus-client` SDK binding** — **deferred to composition/deploy-config** (`OBS-SINK-DEFERRED`);
  Code-Gen builds the **injected Protocols + offline fakes**, no live SDK import at tier-U.
- **`outlier-model` (U18) / `memo-extensions` (U19) / `ui-outlier-view` (U20)** — reached **by shape only**, never imported.

### 1.3 Guardrails held (skill)
NFR-OBS-* (observe, never gate); **BR-OBS-1 / NOEDIT-1** (no frozen edit); **SEC-3 / BR-SEC-6** (no key value in code); **CON-BR1**
(no demographic label/metric); **advisory-only** (no `Recommendation`/verdict declared); **no LLM path**; **no new dependency**;
**tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged).

---

## 2. Component → module map (`backend/observability/` — mirrors the realized sibling convention)

Realized as **three production modules + `__init__.py`** + a `tests/` tree (`fixtures.py`, `structural.py`, `test_*.py`), matching
`backend/outlier_model/` and `backend/memo_extensions/` (Python, pytest, TDD tests-first / leaf-first). **No fifth undisclosed
module** beyond what NFR Design named (`allowlist` + `trace-side` + `metric-side` + `StructuralGuard`). Module names finalized by **Q1**.

| Component (C-OBS) | Module (proposed, Q1) | Contents (from the frozen signatures) |
|---|---|---|
| **C-OBS-3 `allowlist`** (leaf) | `allowlist.py` | `ScalarValue = str \| int \| float \| bool`; `_is_scalar`; `project_allowlisted(fields, allowed) -> dict[str, ScalarValue]` (pure, plane-neutral) |
| **C-OBS-1 `trace-side`** | `trace.py` | `TraceSink` Protocol (`record_span(step_name, attributes)`); `_SPAN_ALLOWED: frozenset[str]`; `TraceRecorder(sink)` with **two callers** — `on_step(step_name, raw_attributes)` (checkpointer callback) + `span(step_name, raw_attributes)` (context-manager, tool steps); both project via `project_allowlisted` |
| **C-OBS-2 `metric-side`** | `metrics.py` | `MetricExporter` Protocol (`export(contribution)`); `MetricContribution`; `MetricDefinition{name, kind, labels}` ×5; `_EVENT_ALLOWED`/`_STEP_ALLOWED` (distinct); `derive_from_event(fields)` (3 metrics) + `derive_from_step_outcome(outcome)` (2 metrics) |
| **C-OBS-4 `StructuralGuard`** | `tests/structural.py` (test-only) | the 5 AST scans + each detector self-test |

**Header-comment deliverables (documentation only, NEVER enforcement — the established convention) — explicit on ALL THREE
production modules**: `allowlist.py` (pure, no side effect, no plane knowledge — the single source of the demographic-free guarantee);
`trace.py` (holds no LLM; edits no frozen unit; every attribute routed through the allowlist; **the deferred per-internal-graph-node
callback shape named per Q6**); `metrics.py` (does not import `trace.py`; every label routed through the allowlist; step outcomes read
by shape; `is_outlier` by value, no `outlier_model` import). **Documentation only — the tests, not the comments, enforce.**

---

## 3. TDD test → target map (every `NFR-OBS-*` at its NFR-pinned tier — NO ORPHAN)

| Target | Tier / rigor | Test file(s) | Teeth |
|---|---|---|---|
| **NOEDIT-1** | **LOAD-BEARING — full-highest** | `test_noedit.py` + `structural.py` scan 1 | structural scan: **no U21 production module imports or mutates any frozen unit source** (`memo_agent_core`/`outlier_model`/`memo_extensions`/`secrets_config` write) + **detector self-test** (a synthetic assignment-into-frozen-namespace is flagged) + injected-sink/offline-fake + **no frozen-file-mtime change**; plus the **by-construction argument** — injected `TraceSink`/`MetricExporter` make editing frozen code **unnecessary** (nothing to gain) |
| **TRACE-1** | **LOAD-BEARING — full-highest** | `test_trace.py` | recording-fake teeth over **BOTH real paths** parameterized (Q1-A of NFR-Req): finalize `[draft,validate,finalize]`=**3**; retry-then-flag `[draft,validate,draft,validate,flag]`=**5** at CAP=2 — **one span per node execution** (draft/validate legitimately twice), span count == executions, none missed/double-counted, **the single `record_span` sink driven via the checkpointer-callback caller**; the **span-API caller** wraps a fake non-graph tool step; grounded in `orchestrator.py`'s **actual node names by value**, not invented; **system-wide 100% = AC-7 deploy-time, explicitly NOT asserted at tier-U** |
| **SEP-1** | high | `test_separation.py` + `structural.py` scan 2 | from the **same** `MemoTelemetryEvent` value: **two independent assertions** — one `record_span` span **and** one *decisions-by-recommendation* counter contribution — with **no shared mechanism** (each derived independently); + **semantic no-cross-import scan** (`trace_*↔metrics_*/*_sink` flagged; the shared `allowlist` **permitted** — the MCPRO-1 precedent) + detector self-test |
| **DEMOFREE-1** | high | `test_demofree.py` + `structural.py` scan 3 | the **single detector self-test at the allowlist utility** (feed `project_allowlisted` a forbidden attribute + an excluding `allowed` set → asserted dropped) — **IS** DEMOFREE-1's (Fold-2, single-sourced); + the **no-bypass scan** (neither plane reads a raw attribute into a span/label without routing through `project_allowlisted`) + detector self-test |
| **SHAPE-1** | high | `test_shape.py` + `structural.py` scan 4 | **no import of any frozen event type** (`MemoTelemetryEvent`/rules/audit/intake) in U21 production (structural scan + detector self-test); fakes driven **by value** |
| **METRIC-1** | standard | `test_metric.py` | `derive_from_event` produces the **3 emitter-sourced** metric contributions from allowlist fields; a fake event exposing the allowlist fields drives every derivation |
| **STEPMETRIC-1** | standard | `test_stepmetric.py` | `derive_from_step_outcome` produces the **2 step-outcome** metrics from **dedicated, non-overlapping** fixtures; **`is_outlier` by value** (U18's real field, no import); the **Fold-3 consistency assertion** — the fixture's field names **⊆ `_STEP_ALLOWED`** (a rename either side fails loudly) |
| **TIERU-1** | governance/structural | `test_tieru.py` | **no socket / no key / no Docker** in any U21 test; injected fakes only; **the 31 skips + 5 Docker errors stay unchanged** (asserted as the no-regression baseline) |
| **CONTRACT-1** | high | `test_contract.py` + `structural.py` scan 5 | **no `Recommendation`/verdict declared or emitted** by any U21 module (structural scan + detector self-test); metrics are counts/timings/enum-labels only |
| **PERF-1** | soft/observed | `test_perf_observed.py` | latencies (`duration_ms`/`*_micros`) are **recorded, never asserted-as-failure**; no hard SLO |
| **SEC-1** | governance | `test_governance.py` | the Security-Guardrails posture: **no key/endpoint value in code** (the reserved `LANGFUSE_*` are deploy shapes); demographic-free labels; advisory-only |

**Coverage**: BR-OBS-1..7 → the 11 targets; the ~5 metrics → METRIC-1 ×3 + STEPMETRIC-1 ×2; **no orphan**. **The five** AST
scans of `StructuralGuard` (scans 1–5) each carry a **mandatory detector self-test** (non-vacuity).

---

## 4. Leaf-first build order (TDD tests-first, per module)

0. **`tests/fixtures.py` + `tests/structural.py` substrate** (the recording-fake doubles + fake event/step-outcome fixtures + the AST-scan helpers) — Q2/Q3/Q5.
1. **`allowlist.py`** (leaf, no deps) — `project_allowlisted` pure function → its detector self-test (DEMOFREE-1) first.
2. **`trace.py`** — `TraceSink` Protocol + `TraceRecorder` (`record_span`, the two callers) → TRACE-1 + NOEDIT-1 (injected) teeth.
3. **`metrics.py`** — `MetricExporter` Protocol + the two derivation paths + the ~5 `MetricDefinition`s → METRIC-1 + STEPMETRIC-1 teeth.
4. **`StructuralGuard` scans (all 5, each with its detector self-test)** — NOEDIT-1 / SEP-1 / DEMOFREE-1-no-bypass / SHAPE-1 / CONTRACT-1.
5. **Coverage gate** — `--cov=backend/observability`, `--cov-fail-under=90` unchanged; no-regression check.

---

## 5. Clarifying questions (fill each `[Answer]:` tag) — Code-Gen-only realization choices

Letter after each `[Answer]:` tag; if none fit, choose the last (Other) and describe. These decide **realization details only** — they
do **not** re-open the FD, `NFR-OBS-*`, `P-OBS-1..11`, `C-OBS-1..4`, or the Infrastructure Design.

## Question 1 — Production module names / layout (FD Q4-A left this OPEN)
How are the three production modules named under `backend/observability/`?

A) **Three modules**: **`allowlist.py`** (C-OBS-3, leaf) · **`trace.py`** (C-OBS-1: `TraceSink` + `TraceRecorder`) · **`metrics.py`**
   (C-OBS-2: `MetricExporter` + the two derivations + the ~5 defs) + `__init__.py`. The **live SDK sinks are deferred** (injected
   Protocols only at tier-U — no live `langfuse_sink`/`prometheus_sink` module to house now), so a single module per plane is cleanest.
B) The FD's **four-file** split (`trace_schema.py` + `langfuse_sink.py` + `metrics.py` + `prometheus_sink.py`) — rejected: the two
   `*_sink` files would be empty-of-live-code at tier-U (the SDK binding is composition's), adding modules with no tier-U substance.
C) Other (describe after [Answer]:)

[Answer]: A

## Question 2 — Recording-fake double construction (the injected `TraceSink` / `MetricExporter` doubles + fixtures)
How are the offline doubles + fixtures built?

A) **A shared `tests/fixtures.py`** holding: a **capturing `RecordingTraceSink`** (implements `record_span`, appends
   `(step_name, attributes)` tuples to an inspectable list) · a **capturing `RecordingMetricExporter`** (implements `export`, collects
   `MetricContribution`s) · **fake emitter-event fixtures** shaped **by value** (a `MemoTelemetryEvent`-shaped mapping exposing the
   allowlist fields; a `rules_engine`-telemetry-shaped mapping with `evaluate_micros`) · **fake step-outcome fixtures** (a
   provider-error outcome; an outlier outcome exposing **`is_outlier` by value**, no `outlier_model` import) — distinct fixture families
   for the two derivation paths (Q2-A of NFR-Req). Mirrors `outlier_model`/`memo_extensions` `tests/fixtures.py`.
B) Inline ad-hoc doubles per test file (rejected — duplication; drifts; no single fixture source).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 3 — Exact grounded step-name sequences for both real graph paths
What exact sequences does the TRACE-1 recording fake feed?

A) **Exactly the two frozen paths, node names by value from `orchestrator.py`**: **finalize** = `["draft","validate","finalize"]`
   (**3**); **retry-then-flag at CAP=2** = `["draft","validate","draft","validate","flag"]` (**5**). One **parametrized** test over both
   (Q1-A of NFR-Req); teeth assert **span count == node-execution count** (3 / 5), each execution its own span, none missed or
   double-counted; a fake **non-graph tool step** exercises the `span()` caller separately. **The sequences are referenced from the
   frozen node list, not invented.**
B) A single happy path only (rejected — coverage hole; the retry-then-flag path + reaching CAP is exactly what NFR-Req-Fold-1 requires).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 4 — Exact allowlist field-name contents (`_SPAN_ALLOWED` / `_EVENT_ALLOWED` / `_STEP_ALLOWED`)
How are the three allowlist sets populated?

A) **Chosen at generation from the FROZEN scalar fields, threshold/derivation tests parameterized OFF the named constant** (the
   `memo_extensions` Q4 / CG-OUT-Fold-1 precedent — never a hardcoded duplicate literal): **`_EVENT_ALLOWED`** = the `MemoTelemetryEvent`
   scalar fields the 3 emitter metrics need (`recommendation`, `duration_ms`) + the `rules_engine` `evaluate_micros`; **`_STEP_ALLOWED`**
   = the step-outcome fields the 2 metrics need (`is_outlier` + the provider-error marker) — **U18's real field name by value**;
   **`_SPAN_ALLOWED`** = the permitted span-attribute names (ids / enum values / counts / timings — **no prose/PII/`original_span`**).
   Each set is a named `frozenset`; every test reads it **off the constant**, so a set change can't silently pass.
B) Hardcode the field-name literals directly in each test (rejected — duplicates the surface; a drift wouldn't fail loudly).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 5 — Test-file organization (mirroring the sibling backend units)
How is `tests/` organized?

A) **Mirror `outlier_model`/`memo_extensions`**: `tests/{__init__.py, fixtures.py, structural.py}` + one `test_*.py` per target —
   `test_noedit.py` · `test_trace.py` · `test_separation.py` · `test_demofree.py` · `test_shape.py` · `test_metric.py` ·
   `test_stepmetric.py` · `test_tieru.py` · `test_contract.py` · `test_perf_observed.py` · `test_governance.py` +
   `test_structural_guard.py` (the 5 scans + their detector self-tests). One clear target per file, no orphan.
B) A single monolithic `test_observability.py` (rejected — diverges from the established sibling convention; poor failure locality).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 6 — The deferred per-internal-graph-node callback — placeholder/stub acknowledgment in code?
Infrastructure Design named the deferred item's shape (INFRA-OBS-Fold-1c: a future minimal `callbacks`/`config` passthrough on U4's
`run()`). Does `trace.py` acknowledge it in code now?

A) **Documentation-only header/inline comment on `trace.py`** naming the deferred per-internal-graph-node-callback shape (a future
   minimal `callbacks` passthrough on `run()`, `OBS-SINK-DEFERRED`) — so the deferred item is **discoverable at the seam it concerns** —
   with **NO stub function, NO placeholder class, NO `langgraph` import, NO dead code**. Documentation only, never enforcement (the
   established header-comment convention). The `on_step` callback caller **already exists** as the injected seam the future passthrough
   would drive; nothing new is stubbed.
B) No comment at all (rejected — loses the discoverability Infrastructure Design deliberately named; a future composition pass would
   re-derive the shape).
C) A stub `attach_to_graph()` / placeholder function now (rejected — adds dead code / a fake seam; violates the no-live-binding hold).
D) Other (describe after [Answer]:)

[Answer]: A

## Question 7 — Test framework + coverage config
Framework and coverage wiring?

A) **`pytest` + `Hypothesis` where a universal-quantifier property earns it** (DEMOFREE-1 over generated forbidden attributes; TRACE-1
   span-count over generated fake sequences) — **no new dependency** (both already floored + installed). Add **one line**
   `--cov=backend/observability` to `pyproject.toml` `addopts`; **`--cov-fail-under=90` UNCHANGED**; `--cov-report=term-missing`
   unchanged; **no `omit`** (pure-logic unit — no live-SDK/subprocess/network module at tier-U). Target **100%** statements/branches on
   the three production modules; **backend baseline 1096 passed / 31 skipped → no regression, pure additive.**
B) Introduce a new test/mocking dependency (rejected — nothing here needs one; the injected doubles are plain classes).
C) Other (describe after [Answer]:)

[Answer]: A

---

## 5.5 Mandatory ambiguity-check (RAN against the seven answers + the frozen substrate) → **CLEAN (2 folds; no surface-and-stop)**

Grounded in the ACTUAL frozen shapes re-read on disk: `MemoTelemetryEvent{recommendation: str, duration_ms: int, …}`
(`memo_agent_core/telemetry.py`), `EvaluationTelemetry.evaluate_micros: int` (`rules_engine/telemetry.py`),
`OutlierResult.is_outlier: bool` (`outlier_model/schemas.py`), the frozen `orchestrator.py` node list + `MEMO_CITATION_RETRY_CAP`,
and `Recommendation(str, Enum)` (`rules_engine/report_schema.py`). Two folds, both resolved in-scope — no frozen artifact re-opened:

- **CG-OBS-Fold-1 [NOEDIT-1 "no-mtime-change" realization]** — the NFR-Req NOEDIT-1 sub-clause *"no frozen-file-mtime change"* is
  realized as the **stronger, non-vacuous structural scan** *"no U21 production module imports OR mutates any frozen namespace"*
  (`test_structural_guard.py` scan 1 + detector self-test) rather than a literal within-run mtime assertion — which would be **vacuous**
  (nothing in a tier-U run touches frozen files) and so is internally inconsistent with the project's non-vacuity discipline (every scan
  carries a detector self-test precisely to avoid vacuity). The guarantee is **preserved and strengthened**: U21 production imports **zero**
  backend units (only `typing`/`contextlib`/`dataclasses` + `backend.observability.allowlist`), so there is no handle to mutate.
- **CG-OBS-Fold-2 [shared `recommendation` field across two str-enum event types]** — `recommendation` is a **str-enum value** carried by
  BOTH `MemoTelemetryEvent` and `EvaluationTelemetry`, so both survive scalar-projection. Resolved by keying `derive_from_event`
  **field→metric 1:1** (`recommendation`→decisions counter, `duration_ms`→latency, `evaluate_micros`→rule-duration); per `domain-entities §4`
  the decisions counter's **source is the MEMO event stream** (one memo run = one decision), and **which emitter stream feeds the
  derivation is composition wiring** (already `OBS-SINK-DEFERRED`). `derive_from_event` is a pure field→metric mapper (correct for whatever
  fields it is given); the tier-U fixtures use a memo-shaped fake (→ recommendation + latency) and a rules-shaped fake (→ rule-duration),
  each exercising its designated shape. One `derive_from_event`, one `_EVENT_ALLOWED`, no double-count within the tested contract.

**No new dependency, no frozen edit, no key value surfaced by the check.** Proceeded to generate Part 2.

---

## 6. Explicit HOLDS (restated for Part 2)
- **No frozen unit edited**: `memo-agent-core`'s real `telemetry` seam + `run()` consumed **only as documented**; **U4's frozen test
  file never imported**; `secrets-config`'s frozen `Settings` model **untouched**.
- **Reached by shape only, never imported**: `outlier-model` (U18) / `memo-extensions` (U19) / `ui-outlier-view` (U20).
- **No new dependency**: `langfuse` / `prometheus-client` are floored + installed, but **live SDK usage stays DEFERRED to composition**
  (`OBS-SINK-DEFERRED`) — Code-Gen builds the **injected Protocols + offline fakes**, **not** a live integration; **no live SDK import at
  tier-U**.
- **No fifth undisclosed module** beyond the NFR-Design-named set (`allowlist` + `trace` + `metrics` + `StructuralGuard`).
- **WIRE-1 · the 17 frozen P1 units · the closed composition root · `memo-agent-core` (U4) — UNTOUCHED**; **tier-B N/A + NOT authorized**;
  the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the
  **23-unit decomposition unchanged**.
- **SEC-3 / BR-SEC-6** (no key value in code); **CON-BR1** (no demographic label/metric); **advisory-only** (no `Recommendation`/verdict);
  **no LLM path**; **observed-never-gated**.

---

## 7. Coverage / quality gate (comprehensive bar)
`pyproject.toml` gains **one** `--cov=backend/observability` line (no `omit`); **`--cov-fail-under=90` UNCHANGED** (holds globally);
target **100%** on `allowlist.py` / `trace.py` / `metrics.py`. **`requirements.txt` NOT edited.** Backend **1096 passed / 31 skipped**
baseline must hold (+ the new U21 tests; the 5 pre-existing `audit_store` Docker-absence errors **unchanged**) — **zero regression, pure
additive backend module.**

---

## 8. Next step (STOP here)
Fill the seven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check (grounded in the frozen
`orchestrator.py` node names + the frozen emitter/step-outcome field shapes + the sibling `tests/` convention; surfacing-and-stopping on
any genuine gap), then generate Part 2 — the three production modules + `tests/` under `backend/observability/` (TDD tests-first,
leaf-first) + the one `pyproject.toml` `--cov` line — and present the standardized 2-option completion message
(1. Request Changes / 2. Continue to Next Stage). **No code is generated until the answers are in and checked.** This is the **LAST of
U21's 5 stages** — its approval closes the `observability` per-unit loop.
