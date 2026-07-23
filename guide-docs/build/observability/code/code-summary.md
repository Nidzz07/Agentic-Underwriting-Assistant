# Code Summary — `observability` (U21, EPIC-6, Phase 2)

**Stage**: BUILD → Code Generation (per-unit, Part 2) · **Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Date**: 2026-07-19
· **Depth**: comprehensive · **the 5th and LAST of U21's 5 stages.**
**Built ON** the frozen FD (**BR-OBS-1..7**) + approved NFR Requirements (**eleven `NFR-OBS-*`**) + approved NFR Design
(**P-OBS-1..11** / **C-OBS-1..4**) + approved Infrastructure Design (**INFRA-OBS-Fold-1..3**) — re-opening none. Answers
**Q1–Q7 (all A)** + folds **CG-OBS-Fold-1..2** (plan §5.5).

---

## 1. Modules generated (`backend/observability/`)

| Module | Component | Contents |
|---|---|---|
| `__init__.py` | — | package docstring (sink/wiring unit; live SDK binding deferred) |
| `allowlist.py` | **C-OBS-3** | `ScalarValue`, `_is_scalar`, `project_allowlisted(fields, allowed) -> dict` — the pure, plane-neutral single source of the demographic-free guarantee |
| `trace.py` | **C-OBS-1** | `TraceSink` Protocol (`record_span`), `_SPAN_ALLOWED` frozenset, `TraceRecorder` with the **two callers** `on_step` (checkpointer callback) + `span` (context-manager); both project via `project_allowlisted`. **Header names the deferred per-node-callback shape (Q6-A, doc-only).** |
| `metrics.py` | **C-OBS-2** | `MetricExporter` Protocol (`export`), `MetricDefinition`, `MetricContribution`, the **5 metric definitions**, `_EVENT_ALLOWED`/`_STEP_ALLOWED` (disjoint), `derive_from_event` (3 metrics) + `derive_from_step_outcome` (2 metrics) |

**Header-comment deliverables (documentation only, NEVER enforcement) are explicit on all three production modules.**
**No fifth module.** `StructuralGuard` is the test-only `tests/structural.py` substrate (C-OBS-4).

## 2. Tests (`backend/observability/tests/`) — **57 tests, all green; 100% on all three production modules**

| File | Tests | Target(s) / rigor |
|---|---|---|
| `test_noedit.py` | 3 | **NOEDIT-1** (LOAD-BEARING) behavioral — injected-fake by-construction argument |
| `test_trace.py` | 6 | **TRACE-1** (LOAD-BEARING) — both real paths (finalize=3 / retry-then-flag=5 at CAP=2), single `record_span` sink two callers, span-API tool-step wrap, union coverage, allowlist projection |
| `test_metric.py` | 6 | **METRIC-1** — 3 emitter-sourced metrics |
| `test_stepmetric.py` | 7 | **STEPMETRIC-1** — 2 step-outcome metrics, `is_outlier` by value, Fold-3 consistency, disjoint allowlists |
| `test_separation.py` | 2 | **SEP-1** — two-plane same-value independence |
| `test_demofree.py` | 5 | **DEMOFREE-1** — the single detector self-test at the allowlist utility + 2 Hypothesis properties |
| `test_shape.py` | 3 | **SHAPE-1** behavioral — by-value mappings drive every derivation |
| `test_contract.py` | 3 | **CONTRACT-1** behavioral — no verdict; counts/timings/enum labels only |
| `test_perf_observed.py` | 3 | **PERF-1** — latency recorded, never gated |
| `test_governance.py` | 3 | **SEC-1** — no key value in code; demographic-free |
| `test_tieru.py` | 4 | **TIERU-1** — AST import scan: no socket/key/Docker/live-SDK in any U21 test or module |
| `test_structural_guard.py` | 12 | **C-OBS-4** — the **five AST scans** (NOEDIT-1 / SEP-1 / DEMOFREE-1 no-bypass / SHAPE-1 / CONTRACT-1), **each with a detector self-test** + non-vacuity |

`tests/fixtures.py` — capturing `RecordingTraceSink` / `RecordingMetricExporter` doubles + by-value event/step-outcome
fixtures + the grounded node sequences. `tests/structural.py` — the AST-scan substrate.

## 3. Test → target map (all 11 `NFR-OBS-*`, no orphan)

NOEDIT-1 → `test_noedit.py` + scan 1 · TRACE-1 → `test_trace.py` · SEP-1 → `test_separation.py` + scan 2 · DEMOFREE-1 →
`test_demofree.py` + scan 3 · SHAPE-1 → `test_shape.py` + scan 4 · METRIC-1 → `test_metric.py` · STEPMETRIC-1 →
`test_stepmetric.py` · TIERU-1 → `test_tieru.py` · CONTRACT-1 → `test_contract.py` + scan 5 · PERF-1 → `test_perf_observed.py`
· SEC-1 → `test_governance.py`.

## 4. Realization notes (folds — plan §5.5)

- **CG-OBS-Fold-1** — NOEDIT-1's *"no-mtime-change"* sub-clause realized as the stronger, non-vacuous *"no frozen import/mutate"*
  structural scan (a literal within-run mtime assertion would be vacuous). U21 production imports **zero** backend units.
- **CG-OBS-Fold-2** — the shared str-enum `recommendation` field across `MemoTelemetryEvent` + `EvaluationTelemetry` is handled by
  the field→metric 1:1 map; the decisions counter sources from the **memo stream** (`domain-entities §4`), stream-routing is
  composition wiring (`OBS-SINK-DEFERRED`). One `derive_from_event`, one `_EVENT_ALLOWED`.
- **`provider_call_error`** is a Code-Gen realization field name for the LLM-call-error step outcome (no frozen emitter field — the
  metric derives from a composition-wired step outcome, per `domain-entities §4`).
- **`OBS-SINK-DEFERRED`** stays OPEN (DESIGNED, not wired): the live `langfuse`/`prometheus-client` binding + the per-internal-graph-node
  callback (named in `trace.py`'s header, not stubbed) are discharged at composition/deploy-config.

## 5. Result

- **Backend: 1153 passed / 31 skipped** (1096 baseline + **57** new). The **5 pre-existing `audit_store` Docker-absence errors
  UNCHANGED** (the deferred Docker-guard gap, untouched). **Zero regression.**
- **`backend/observability` — 100%** statements + branches on `allowlist.py` / `trace.py` / `metrics.py`; global
  **`--cov-fail-under=90` holds at 99.85%**.
- **`pyproject.toml`** gained one `--cov=backend/observability` line (no `omit`). **`requirements.txt` NOT edited** (no new
  dependency). **No frozen unit edited**; U4's frozen test file never imported; `secrets-config`'s frozen `Settings` untouched.

## 6. Holds verified

No frozen unit edited (U4 orchestrator/telemetry consumed as documented, its test file never imported; `secrets-config` `Settings`
untouched); `outlier-model`/`memo-extensions`/`ui-outlier-view` reached by shape only, never imported (U21 production imports **zero**
backend units); no new dependency; no live SDK import at tier-U; no fifth module; WIRE-1 · the closed composition root · the 17 frozen
P1 units — untouched; tier-B N/A + not authorized; the `audit_store` Docker-guard gap untouched; no other unit started; the 23-unit
decomposition unchanged.
