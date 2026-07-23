# Domain Entities — `observability` (U21, EPIC-6, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Depth**: **lighter** (per `unit-of-work.md:248/262` — comprehensive reserved for Infrastructure Design) · **Date**: 2026-07-17 · Story **US-PLAT-9** · NFR-OBS-1/2, AC-7.
**Scope**: the entity/interface view of `observability` — the **sink/wiring** unit that makes the already-built system observable. Built on **Q1–Q5 = A** and the ambiguity-check folds **FD-OBS-Fold-1..3** (plan §5.5), re-opening none. **NO code in this stage.**

> **U21 adds NO new domain contract and NO new output type.** It **consumes** already-emitted, stack-agnostic telemetry (frozen `TelemetryEmitter` ×4) and the frozen LangGraph **checkpointer** step stream, and **exports** them to **two sinks** — Langfuse (traces) and Prometheus/Grafana (metrics). It **edits no frozen unit**; the **live binding** is deferred to composition/deploy-config (Q1-A — the composition-root parallel). Advisory-only is inherited **trivially**: U21 has no path a recommendation flows through.

---

## 1. Scope boundary — what this unit is, and what it is NOT

| | |
|---|---|
| **IS** (Q1-A / Q2-A) | a **schema + adapter definer** with **two clearly-separated sub-components**: **(T) trace-side** — a trace/span schema + a Langfuse callback/handler that a graph checkpointer drives + a general span API for non-graph tool steps; **(M) metric-side** — the ~5 metric definitions + a registry/collector + derivations from emitted allowlist events + a Prometheus exporter adapter |
| **IS NOT** | an **instrumenter of frozen code** — the four P1 units already self-emit; U18/U19 are observed at the graph/tool-wrap boundary, never edited. **Not** a domain-logic unit (no rule/score/memo/recommendation). **Not** the place the live wiring happens (that is composition/deploy-config — Q1-A). **Not** a live-trace-backend at tier-U (Q3-A). |

**The module layout is OPEN** (Q4-A) — `unit-of-work.md:86` names the `observability/` directory but **enumerates no files** (no "frozen four" analog like `memo-extensions`). The structure below is designed here, sized to the two sub-concerns.

---

## 2. Module / interface inventory (`backend/observability/` — proposed, Q4-A)

| Sub-component | Module (proposed) | Role | Interface surface (signatures → NFR/Code-Gen) |
|---|---|---|---|
| **(T) trace schema** | `trace_schema.py` | the demographic-free **span** representation + the **100%-step coverage** contract (grounded in U4's real node list — Fold-1) | a frozen `TraceSpan` shape `{step_name: str, attributes: mapping of allowlist scalars}`; **no** prose/PII/`original_span` field |
| **(T) Langfuse sink** | `langfuse_sink.py` | the **trace callback/handler** the frozen checkpointer drives + the **general span API** (context-manager/decorator) composition applies to non-graph tool steps (Fold-1) | `on_step(step_name, attributes) -> None` (callback); `span(step_name, attributes)` (context-manager) — an **injected sink Protocol** with an **offline recording fake** at tier-U |
| **(M) metrics** | `metrics.py` | the **~5 metric definitions** + registry/collector + **derivations from emitted allowlist events** (read **by shape** — Q5-A) | `MetricDefinition{name, kind: counter/gauge/histogram, labels: allowlist keys}`; `derive(event) -> metric contributions` reading **only** enumerated allowlist field names |
| **(M) Prometheus sink** | `prometheus_sink.py` | the **Prometheus exporter/registry** adapter (interface; the `/metrics` mount is composition/deploy-config) | an **injected exporter Protocol** with an offline fake; **no** live scrape at tier-U |
| **StructuralGuard** | `tests/` | the demographic-free/allowlist AST scans + the detector self-tests (Fold-3) | (test-only) |

> **Header-comment deliverables (documentation only, NEVER enforcement — the frozen self-evidence convention)**: `trace_schema.py` / `metrics.py` state that **every field is an allowlist scalar (id / enum value / int count / timing) — no prose, demographic, or free-text field can be represented**, inheriting the four emitters' by-construction discipline; `langfuse_sink.py` / `prometheus_sink.py` state they are **injected sinks with offline fakes** (no network, no key at tier-U) and that the **live binding is composition/deploy-config's**.

---

## 3. Consumed frozen streams + seams (reference-not-own — re-declared by none, modified by none)

### 3.1 The two frozen source streams (Fold-2)
| Stream | Origin (frozen) | Consumed by |
|---|---|---|
| **checkpointer node executions** — `draft` · `validate` · `finalize` · `flag` | `memo_agent_core.orchestrator` (`MemorySaver` checkpointer) | the **(T) trace side** — one span per node; the callback attaches **at composition** |
| **emitted allowlist events** — `MemoTelemetryEvent` (+ the `intake`/`rules_engine`/`audit_store` events) | the four `TelemetryEmitter` seams | the **(M) metric side** — derivations read the typed fields **by shape** (Q5-A), importing no event type |

### 3.2 Seams (no edit)
| Seam / surface | Origin (frozen) | Relationship |
|---|---|---|
| `TelemetryEmitter(sink)` + typed event | `intake` · `rules_engine` · `audit_store` · `memo_agent_core` | events **consumed by shape**; **no import of the event schema** into U21 production (Q5-A) |
| graph checkpointer | `memo_agent_core.orchestrator` | the trace callback the **composition** plugs in; U21 **defines** it, never wires it |
| `OutlierResult.{is_outlier, outlier_score}` (U18) · `ThinkingMode` / `SupplementaryContext.retrieval_ok` / provider selection / `CitationValidationResult` (U19 / U4) | `outlier_model` / `memo_extensions` / `memo_agent_core` | **non-graph tool-step outcomes** — traced via the span API **at composition**; **no emit seam exists** in U18/U19, so they are observed by wrapping, never by editing |
| keys / endpoints | `secrets-config` (SEC-3) | read from env/secrets; **never hardcoded**; **no key at tier-U** |

**Reference-not-own**: U21 imports **no** emitting unit's event type (Q5-A); the three **declared** edges (`memo-agent-core`, `memo-extensions`, `outlier-model`, `:50`) are honored as **trace-step** edges; the metric side adds **no** new code edge to `rules-engine`/`audit-store` (it reads generic emitted events by shape). No frozen file is edited; `observability`'s consumers, if any, import U21 — never the reverse.

---

## 4. The ~5 metrics (NFR-OBS-2) — definitions + grounded source (Fold-1/-3)

| Metric | Kind | Source (frozen) | Label(s) — allowlist only |
|---|---|---|---|
| decisions by recommendation type | counter | `MemoTelemetryEvent.recommendation` (enum value) | `recommendation` |
| decision latency | histogram | `MemoTelemetryEvent.duration_ms` (observed) | — |
| rule-evaluation duration | histogram | `rules_engine` telemetry `evaluate_micros` (observed) | — |
| LLM-call errors | counter | **step outcome** at the span-API boundary (provider-call error path) — no frozen emitter field | — |
| outlier-flag rate | counter/gauge | **step outcome** — U18 `OutlierResult.is_outlier` at the span-API boundary — no frozen emitter field | — |

**3 metrics derive from frozen emitted events; 2 derive from step outcomes** observed at the span-API boundary (their real capture is composition-wired; tier-U tests them against fake step outcomes). **Every label is an enum value / id — no prose, no demographic** (inherited CON-BR1, verified by Fold-3's detector self-test). Metric **values/labels are configurable realizations** for NFR/Code-Gen; this FD pins **names + kinds + sources + the demographic-free label rule**.

---

## 5. FD ↔ later-stage boundary
- **This FD pins**: the two sub-components + their interface surfaces (§2); the two frozen source streams (§3.1); the reference-not-own boundary (§3); the ~5 metric names/kinds/sources + demographic-free labels (§4); the two trace mechanisms (checkpointer callback + span API) and the grounded node list (Fold-1); the tier-U testable surface = schema/interface correctness + recording-fake 100%-coverage + derivation correctness + the Fold-3 detector self-test (Q3-A).
- **NFR / Code-Gen owns**: exact metric bucket bounds / registry library choice; the span/attribute serialization shape; the recording-fake fixtures.
- **Infrastructure Design (comprehensive) / composition / deploy-config owns**: the **live** Langfuse callback→checkpointer binding, the `/metrics` mount + scrape, the one Grafana dashboard topology, the Langfuse/Prometheus keys+endpoints (via `secrets-config`), and **AC-7's deploy-time 100%-trace audit**. The composition-root parallel (Q1-A): the wiring is a **separate deviation**, not baked into U21.
- **Out of scope (named-not-designed)**: `ui-outlier-view` (U20) fetch/render lifecycle (frontend display, not a traced backend step); any edit to a frozen unit's emitter.
