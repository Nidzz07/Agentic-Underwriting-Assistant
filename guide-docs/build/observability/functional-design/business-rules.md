# Business Rules — `observability` (U21, EPIC-6, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Depth**: lighter · **Date**: 2026-07-17 · Story **US-PLAT-9**.
**Nature**: `observability` owns **no domain rule, no score, no memo, no recommendation**. It is a **sink/wiring** unit. The rules below (**BR-OBS-\***) are **checkable** invariants, each grounded in a frozen contract, a frozen emitter docstring, or a settled answer — **none introduces domain logic**, and **none re-opens a frozen artifact**. Built on **Q1–Q5 = A** and **FD-OBS-Fold-1..3** (plan §5.5).

---

## Rules

### BR-OBS-1 — U21 EDITS NO FROZEN UNIT; it defines sinks/schemas, composition wires them (Q1-A / the composition-root parallel) — **load-bearing**
U21 **defines** the Langfuse trace callback/handler + the general span API + the Prometheus metric registry/derivations + the trace/metric schemas, and **consumes** the already-emitted events. The **live binding** — handing each emitter its real sink, plugging the callback into U4's frozen checkpointer, mounting `/metrics` — lands at **composition/deploy-config**, never inside U21 and never by editing a frozen unit.
- **Grounded**: the four `telemetry.py` docstrings (*"the `observability` unit wires it …"*, *"wired by `observability` (reference-not-own) via the graph checkpointer"*); Q1-A; the composition-root deviation precedent.
- **Checkable**: no U21 production module imports or mutates any frozen unit's source; U21's `backend.*` imports do **not** include a write into `memo_agent_core`/`outlier_model`/`memo_extensions` (structural scan); the callback/span API are **injected**, exercised against a fake at tier-U.

### BR-OBS-2 — 100%-STEP TRACE COVERAGE is proven over U4's REAL node list; the graph/tool-step boundary is named (NFR-OBS-1 / AC-7 / Fold-1) — **load-bearing**
Every **graph node** (`draft` · `validate` · `finalize` · `flag`) yields exactly **one span** via the checkpointer callback — 100% **by construction**. **Non-graph tool steps** (U18 outlier scoring; U19 `route_borderline`/adapter-selection/MCP retrieval) are traced by the **general span API** composition applies at their call sites. The **system-wide** 100% is **AC-7's deploy-time Langfuse trace audit**, not a tier-U assertion.
- **Grounded**: U4's frozen `orchestrator.py` (4 nodes + `MemorySaver` checkpointer, *"100%-step tracing"*); Q1-A + Q3-A; Fold-1.
- **Checkable**: a **recording-fake** callback over the **real** node sequence (`draft→validate→finalize` and `draft→validate→draft→…→flag`) yields **one span per node** (count == node count, no node missed); the span API wraps a fake tool call and records a span; the fake sequence is the **actual** node list, **not** an invented one.

### BR-OBS-3 — TRACES and METRICS are two separate sub-components, distinct mechanisms (NFR-OBS-1 vs NFR-OBS-2 / Q2-A)
Traces = per-step spans (checkpointer callback + span API). Metrics = time-series counters/gauges/histograms in a registry, derived from emitted allowlist events, exported to Prometheus → one Grafana dashboard. They are **not** unified into one bus; a single occurrence may appear in both planes via the **two pre-existing frozen streams** (Fold-2), without conflating the mechanisms.
- **Grounded**: NFR-OBS-1 / NFR-OBS-2; Q2-A; Fold-2 (the checkpointer node stream + the emitter event stream).
- **Checkable**: the trace sink and the metric registry are **separate** interfaces with separate schemas; a memo completion produces **one span** (trace plane) **and** contributes to the *decisions by recommendation type* counter (metric plane) from the **same** `MemoTelemetryEvent`, with neither mechanism importing the other.

### BR-OBS-4 — EVERY sink is DEMOGRAPHIC-FREE / allowlist BY CONSTRUCTION; U21 verifies it, does not merely trust it (CON-BR1 inherited / Fold-3)
No trace attribute or metric label may carry prose, PII, free-text, or an `original_span`-style field. U21's derivations/sinks read **only** the enumerated allowlist field names by shape; a malformed / out-of-allowlist event's forbidden field is **never** propagated.
- **Grounded**: the four emitters' *"allowlist … structurally incapable … CON-BR1 extends to telemetry by construction"*; CON-BR1; skill #6; Q5-A; Fold-3.
- **Checkable** (the detector-self-test analog): a synthetic event carrying a forbidden attribute (free-text / demographic / `original_span`) is fed to a sink/derivation and asserted **not** read or propagated (never reaches a span attribute or a metric label); a structural scan finds **no** U21 sink reading a non-allowlisted attribute name (+ the scan flags a synthetic violation, so it cannot pass vacuously).

### BR-OBS-5 — U21 CONSUMES emitted events BY SHAPE; it imports no emitting unit's event type (Q5-A / edge scope)
The metric derivations read the typed fields structurally; U21 imports **no** frozen event schema into production, so the metric side adds **no** new code edge to `rules-engine`/`audit-store` beyond the three declared trace-step edges.
- **Grounded**: the emitters' *"thin, stack-agnostic seam"*; `unit-of-work-dependency.md:50` (three declared edges); Q5-A.
- **Checkable**: no U21 production module imports `MemoTelemetryEvent` or the rules/audit/intake event types (structural scan); tier-U drives **fake events shaped by value**; a fake event exposing the allowlist fields drives every derivation.

### BR-OBS-6 — TIER-U tests SCHEMA/INTERFACE correctness; live capture is deferred (Q3-A)
U21 stands up **no** live Langfuse/Prometheus at tier-U — **no network, no key, no Docker**. Its tier-U surface is schema/interface correctness + adapter/derivation logic + the recording-fake 100%-coverage proof; live end-to-end trace capture becomes meaningful only once composition Scope B/C exists.
- **Grounded**: the whole build's *"no network, no key"* tier-U discipline; the frozen *"observed, not gated"* posture; Q3-A; tier-B N/A + unauthorized.
- **Checkable**: no U21 test opens a socket / reads a key / requires Docker; the sinks are injected fakes; the 31 skips + 5 pre-existing Docker errors are **unchanged** (U21 adds none).

### BR-OBS-7 — U21 ADDS NO domain contract and cannot alter an outcome (advisory-only inherited trivially)
U21 declares **no** recommendation/verdict; it emits/exports signals only. There is **no** path through U21 that a `Recommendation` flows through.
- **Grounded**: skill #1; the unit's sink/wiring nature; NFR-OBS-* (observe, never gate).
- **Checkable**: no U21 module declares or emits a `Recommendation`/verdict; metrics are counts/timings/enum-labels only; `duration_ms`/`*_micros` are **observed, never gated** (no latency-failing assertion).

---

## Rule → source traceability

| Rule | Frozen source / decision |
|---|---|
| BR-OBS-1 | the four `telemetry.py` docstrings, Q1-A, composition-root precedent |
| BR-OBS-2 | U4 frozen `orchestrator.py` (4 nodes + checkpointer), NFR-OBS-1, AC-7, Q1-A/Q3-A, Fold-1 |
| BR-OBS-3 | NFR-OBS-1/2, Q2-A, Fold-2 |
| BR-OBS-4 | the four emitters (allowlist by construction), CON-BR1, skill #6, Q5-A, Fold-3 |
| BR-OBS-5 | `unit-of-work-dependency.md:50`, the emitters' stack-agnostic seam, Q5-A |
| BR-OBS-6 | tier-U discipline, "observed not gated", Q3-A, tier-B N/A |
| BR-OBS-7 | skill #1, NFR-OBS-* observe-not-gate |

**No orphan** — US-PLAT-9 / NFR-OBS-1 → BR-OBS-2/3; NFR-OBS-2 → BR-OBS-3/4/5; AC-7 → BR-OBS-2; the reference-not-own hold → BR-OBS-1/5; CON-BR1 inherited → BR-OBS-4; advisory-only inherited → BR-OBS-7; tier-U discipline → BR-OBS-6.
**Story coverage**: **US-PLAT-9** → BR-OBS-1..7 as a set (trace side: 1/2/3/4/6; metric side: 1/3/4/5/6; cross-cutting: 7).
