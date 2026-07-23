# Functional Design — Plan (Part 1) — `observability` (U21, EPIC-6, **Phase 2**)

**Stage**: BUILD → per-unit loop → **Functional Design Part 1 (Plan)** · **Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Depth (recommended)**: **lighter at FD** (see §1.4 — this is the unit's *actual* classification, verified on disk, not assumed) · **Date**: 2026-07-17
**Built ON** the frozen contracts this unit observes — re-read, **re-derived none**: the four P1 **emit-only `TelemetryEmitter`** seams (`intake`, `rules_engine`, `audit_store`, `memo_agent_core`); U4's LangGraph orchestrator + graph-checkpointer seam; the P2 surfaces it depends on (`outlier-model` U18, `memo-extensions` U19); `secrets-config` (SEC-3) for keys. **NO FD artifact generated yet. NO code. `backend/observability/` NOT created.**

**Status**: **PART 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** **FIVE `[Answer]` tags (§5) are BLANK.** On the filled answers I run the mandatory ambiguity-check (surface-and-stop on any genuine gap, no improvising), then FD Part 2 **on the explicit go**. This is the **1st of U21's stages** and the **4th of 6 Phase-2 units** to enter the loop (U18 + U20 + U19 complete).

---

## 0. DISCOVER-carryover check + frozen-substrate re-read (verified on disk this session — not assumed)

- **Greenfield P2 unit; no reverse-engineering.** **No prior U21 artifacts** — `backend/observability/` does **not** exist; `guide-docs/build/observability/` does **not** exist. Clean start.
- **Story / requirements (frozen)**: **US-PLAT-9** (`stories.md:601`) — *"every agent/tool step traced and a metrics dashboard … observable end to end"*; gherkin: **Langfuse captures traces for 100% of agent/tool steps** + **one Grafana dashboard, ~5 metrics** (decision latency · decisions by recommendation type · rule-evaluation duration · LLM-call errors · outlier-flag rate). Traces **NFR-OBS-1** (Langfuse 100% of agent/tool steps), **NFR-OBS-2** (Prometheus+Grafana, one dashboard, ~5 metrics), **AC-7** (100% of agent steps traced — Langfuse trace audit).
- **Dependency edges (frozen, `unit-of-work-dependency.md:50`)**: `observability` (P2) → **`memo-agent-core`, `memo-extensions`, `outlier-model`** — *"traces 100% of agent/tool steps."* Also a **`secrets-config` (SEC-3) consumer** (`:55`) — reads keys from env/secrets, never hardcoded. Cross-cutting unit — in the §1 matrix, **not** the diagram (`:114`); *"wraps the built system"* (`:200`).
- **The emit-only architecture is ALREADY BUILT (the decisive finding).** Four P1 units each ship their **own** `TelemetryEmitter` + a **typed, allowlist, demographic-free** event schema, **emit-only**, **stack-agnostic**, each with a docstring that names THIS unit as the wirer:
  - `intake/telemetry.py`: *"Emit-only … the `observability` unit wires it to Langfuse/Prometheus/Grafana. The emitted signal set is {counts, enums, durations, statuses} — nothing else."*
  - `rules_engine/telemetry.py`: allowlist Pydantic event; only `str` leaves are rulebook metadata; *"observed-only"* `evaluate_micros`; CON-BR1 extends to telemetry by construction (NFR-RULES-OBS-1).
  - `audit_store/telemetry.py`: allowlist events; only `str` leaves are metadata ids; commit/replay `*_micros` *"emitted … never gated"* (NFR-AUDIT-OBS-1).
  - `memo_agent_core/telemetry.py`: `MemoTelemetryEvent` (application_id, recommendation/confidence enum values, outcome, cited_rule_count, missing_info_count, draft_attempts, duration_ms); *"**Langfuse 100%-step tracing is wired by `observability` (reference-not-own) via the graph checkpointer**."*
- **⚠️ Asymmetry (material, verified): the two P2 units U21 depends on have NO emit seam.** `backend/outlier_model/` and `backend/memo_extensions/` contain **no `telemetry.py`** — unlike the four P1 units. Their traceable outcomes exist only as **return values / observable state** (U18: `OutlierResult.outlier_score`/`is_outlier`; U19: the `ThinkingMode` routing decision, `SupplementaryContext.retrieval_ok` MCP hit/miss, provider selection across the three adapters, and the frozen `CitationValidationResult` pass/fail). This directly shapes **Q1** and **Q3**.
- **`ui-outlier-view` (U20) is correctly NOT a dependency edge** — a frontend display unit; not a traced backend step. Confirmed against `:50`.

---

## 1. Unit context

### 1.1 What `observability` IS
The **sink/wiring** unit that makes the already-built system observable: it **consumes** the units' **already-emitted, stack-agnostic telemetry** and the **agent/tool graph steps**, and exposes them to **two sinks** — **Langfuse** (per-step traces, 100%) and **Prometheus/Grafana** (one dashboard, ~5 aggregate metrics). It is the **first unit whose entire purpose is to observe what other completed units already do**, not to perform new domain work.

### 1.2 What it is NOT
- It is **not** a domain-logic unit — no rule, no score, no memo, no recommendation. It **emits/exports signals only**; it can never change an outcome (advisory-only is inherited trivially — it has no output contract that a decision flows through).
- It is (almost certainly) **not** the place where frozen units get *edited to add instrumentation* — they **already self-emit** (that is the whole point of the four `TelemetryEmitter` seams). **Q1 pins this.**

### 1.3 The emit-only seam model (inherited, not invented here)
Every instrumented unit owns a **thin, stack-agnostic emitter** that appends typed events to an injectable sink (`TelemetryEmitter(sink: list | None)`). `observability` provides the **real sinks/adapters** those events flow into. This is the exact *"reference-not-own"* language the frozen docstrings use. The **live binding** (handing each unit's emitter the real sink; plugging a Langfuse callback into U4's graph checkpointer; mounting a `/metrics` endpoint) is an **integration concern** — the parallel to how the **composition root** was handled as a separate deviation, not baked into any single unit. **Q1 + Q3 pin how much of that lands in U21 vs composition/deploy-config.**

### 1.4 Depth — the ACTUAL classification (verified, not assumed)
`unit-of-work.md:248`: *"`observability` … **Depth: comprehensive at Infrastructure Design (wiring-heavy)**."* `unit-of-work.md:262` lists `observability` among the **pure-wiring units** that are the ***lighter* candidates**. Read together, the frozen classification is explicit and split:
- **Functional Design → lighter.** The FD defines **trace/metric schemas + sink interfaces + metric-derivation contracts** — there is little independent business logic to model; the heavy lifting is wiring.
- **Infrastructure Design → comprehensive** (reserved there; *"wiring-heavy"*). This is where the real Langfuse/Prometheus/Grafana topology lands (contrast `memo-extensions`, whose Infra was a logged SKIP — **U21's Infra is expected to be a REAL comprehensive stage**, likely the 2nd real non-skip after `database`; assessed at that stage, not pre-committed).
- **Recommendation: run FD at `lighter` depth.** *(If you prefer standard/comprehensive FD, say so at the gate — depth is your call; the classification is a recommendation, not a locked floor.)*

---

## 2. What FD Part 2 will decide (at lighter depth) — pending the §5 answers
- The **module/interface surfaces** of `backend/observability/` (structure is **open** — see Q4).
- The **trace-side contract**: how a 100%-step Langfuse trace is represented and captured (a trace/span schema + a callback/handler interface that a graph checkpointer drives), and how tier-U proves 100% coverage **without a live LLM** (a recording fake — see Q3).
- The **metric-side contract**: the **~5 metric definitions** (name, type counter/gauge/histogram, labels), a registry/collector interface, and how each metric is **derived from the already-emitted allowlist events** — **demographic-free by construction, inherited** (no metric may carry prose/PII; labels are enum values / ids only).
- The **reference-not-own** boundary: which frozen event schemas/seams U21 consumes and how (Q1/Q5), asserting **no frozen unit is edited**.
- The **FD↔Infra/composition boundary**: exactly what is *defined* here vs *wired* at Infrastructure Design / composition (Q1/Q3).

**No new domain contract; no recommendation-producing path; advisory-only inherited trivially.**

---

## 3. Frozen seams referenced (reference-not-own — re-declared by none, modified by none)

| Seam / surface | Origin (frozen) | How U21 relates to it |
|---|---|---|
| `TelemetryEmitter` + typed allowlist event | `intake`, `rules_engine`, `audit_store`, `memo_agent_core` (`telemetry.py` ×4) | **consumes emitted events** via the injectable sink; **exports** to Langfuse/Prometheus. **No edit.** (Q1/Q5) |
| LangGraph orchestrator + **graph checkpointer** | `memo_agent_core.orchestrator` (frozen) | the **100%-step trace hook** — a Langfuse callback plugs into the checkpointer **at composition** (U4's docstring says so). U21 **defines** the callback/handler; composition **wires** it. (Q1/Q3) |
| `OutlierResult` (score/flag) | `outlier_model.schemas` (U18) | a traced STEP outcome — **no emit seam exists** in U18 (Q1/Q3); reached by shape / at the graph node, never by editing U18 |
| `ThinkingMode` routing · `SupplementaryContext.retrieval_ok` (MCP hit/miss) · provider selection · `CitationValidationResult` | `memo_extensions` (U19) · `memo_agent_core.citation_validator` | traced STEP outcomes — **no emit seam exists** in U19 (Q1/Q3); observed at the graph/orchestration boundary, never by editing U19 |
| keys / endpoints (Langfuse public/secret, Prometheus) | `secrets-config` (SEC-3) | read from env/secrets, **never hardcoded**; no key at tier-U |

**The ~5 metrics span more units than the three declared edges** — *rule-evaluation duration* → `rules-engine`, *decision latency* → `audit-store`/memo, *outlier-flag rate* → `outlier-model`, *LLM-call errors* → memo path, *decisions by recommendation type* → memo/audit. Under the **emit-only/stack-agnostic** model U21 consumes **emitted events** through a generic sink and needs **no code import** of each emitting unit — but whether U21 references those event *schemas* (or a common seam) is **genuinely open → Q5.**

---

## 4. Draft module structure (PROPOSED — layout is OPEN, unlike `memo-extensions`; pending Q4)

`unit-of-work.md:86` names `observability/` as a **directory unit** but **enumerates NO files** (contrast `memo-extensions`, whose four files were named). So U21 has **no frozen file layout to honor** — the structure is designed here. A candidate (Q4 decides whether to adopt / how many modules):
- `trace_schema.py` — the trace/span representation + the 100%-step coverage contract.
- `langfuse_sink.py` — the Langfuse trace-callback/handler adapter (interface + offline recording fake at tier-U).
- `metrics.py` — the ~5 metric definitions + registry/collector + derivations from emitted events.
- `prometheus_sink.py` — the Prometheus exporter/registry adapter (interface; `/metrics` mount is composition/deploy-config).
- `tests/` — schema/interface correctness + demographic-free-by-construction scans + a recording fake proving 100%-step coverage.

*(Whether trace and metrics are one unit with two clearly-separated sub-components, or need distinct mechanisms, is **Q2**.)*

---

## 5. Clarifying questions (fill each `[Answer]:`; full text; lettered options) — **do not improvise; flag-and-stop**

### Q1 — What does `observability` actually *do* to the units it observes — instrument them (touch frozen code) or define trace/metric sinks a composition pass wires in?
The four P1 units already **self-emit** via their own `TelemetryEmitter`; U4's docstring says Langfuse tracing is *"wired by `observability` … via the graph checkpointer"* **at composition**. Editing any frozen unit to add instrumentation would be a **hold violation**.

- **A. Sink/adapter + schema definer; live wiring deferred to composition/deploy-config (the composition-root parallel).** U21 **defines** the Langfuse trace-callback/handler + the Prometheus metric registry/derivations + the trace/metric **schemas**, and **consumes the already-emitted events**. It **edits no frozen unit**. The **live binding** — handing each unit's emitter the real sink, plugging the Langfuse callback into U4's frozen graph checkpointer, mounting `/metrics` — lands at **composition / deploy-config (Scope B/C)**, exactly as the composition root was a separate deviation rather than baked into any unit. Tier-U proves the adapters/derivations against fake/recorded events. *(Recommended — matches every frozen `telemetry.py` docstring verbatim [“reference-not-own”, “wired by observability … at composition”]; the only reading that touches no frozen code.)*
- **B. U21 owns thin instrumentation shims for the two P2 units that lack an emit seam** (`outlier-model`, `memo-extensions`) — U21-local wrappers/decorators applied **at the call site in composition** (still no edit to U18/U19 source), plus the A-style sinks for everyone else. More self-contained tracing of the P2 steps, but introduces U21-owned wrapping logic and leans harder on composition.
- **C. Flag as needing a composition-root/deviation decision and STOP** — if you consider "who plugs the Langfuse callback into the frozen graph checkpointer" a composition-root Scope-B/C question that must be answered *there* before U21's FD can define its surface.

`[Answer]:` A

### Q2 — Are Langfuse LLM/agent traces and Prometheus/Grafana metrics one concern or two, within this one unit?
NFR-OBS-1 (per-step **traces**, 100%) and NFR-OBS-2 (aggregate **metrics**, ~5, one dashboard) are different data models, sinks, and wiring.

- **A. Two genuinely separate sub-concerns in the one unit, with distinct mechanisms.** Traces = span/step capture via a callback on the graph checkpointer (event-per-step, 100% coverage). Metrics = time-series counters/gauges/histograms in a registry, **derived from the emitted allowlist events**, scraped via `/metrics` → one Grafana dashboard. U21 keeps them as **two clearly-separated sub-components** (own schemas, own sink adapters) under one unit. *(Recommended — they are different observability planes; conflating them would blur the trace-callback and the metric-registry mechanisms and the AC-7 [trace] vs NFR-OBS-2 [dashboard] acceptance surfaces.)*
- **B. One unified pipeline** (a single event bus feeding both sinks). Fewer moving parts, but couples the 100%-step trace contract to the aggregate-metric contract and makes the demographic-free-by-construction argument span both at once.
- **C. Other (describe).**

`[Answer]:` A

### Q3 — How does "trace an agent/tool step" interact with units built to have ZERO live LLM/network at tier-U — is U21's Code-Gen-time testable surface schema/interface correctness rather than live capture?
`outlier-model` and `memo-extensions` (and the whole agent path) run with **no live LLM, no network, no key** at tier-U. A real Langfuse trace needs a running composition + real providers.

- **A. Tier-U tests SCHEMA/INTERFACE correctness + adapter/derivation logic against fake/recorded events; live capture is a composition/deploy-config concern.** U21 proves at tier-U: the trace/metric schemas are demographic-free by construction; a **recording fake** callback proves **every graph step yields a span** (100% coverage over a fake step sequence); each metric **derives correctly** from fake emitted events. **Live end-to-end trace capture** (real Langfuse/Prometheus over a running system) becomes meaningful **only once composition Scope B/C exists** → deferred, exactly like every prior unit's *"no network, no key"* tier-U discipline and the frozen *"observed, not gated"* posture. *(Recommended — consistent with the whole build; U21 cannot and should not stand up a live trace backend at tier-U.)*
- **B. U21 attempts a live/integration trace tier now** (e.g., a local Langfuse/Prometheus via testcontainers). Closer to end-to-end, but stands up infrastructure the rest of the build deferred to deploy-config, and tier-B/Docker are not authorized.
- **C. Other (describe).**

`[Answer]:` A

### Q4 — Does U21 have a "no fifth module beyond a frozen layout" constraint like `memo-extensions`, or is its module structure open?
`unit-of-work.md:86` names `observability/` as a **directory** but **enumerates no files** (contrast `memo-extensions`, whose four files `unit-of-work.md:70-71` named explicitly).

- **A. The module structure is OPEN — designed at FD; no frozen file layout to honor.** U21 proposes a cohesive structure (e.g., the §4 candidate: trace schema · langfuse sink · metrics/registry · prometheus sink · tests), sized to the two sub-concerns (Q2), **not** constrained to a fixed file count. *(Recommended — the frozen decomposition names only the directory; no `unit-of-work.md` line enumerates U21's files, so there is no "frozen four" analog to violate.)*
- **B. Constrain to a single module** (`observability.py`) for a pure-wiring lighter unit. Minimal surface, but crowds the two distinct sub-concerns (traces vs metrics) into one file.
- **C. Other (describe).**

`[Answer]:` A

### Q5 — How does U21 reference the emitted-event schemas — import each unit's event type, depend on a common seam, or stay structural/duck-typed? (edge scope)
U21's **declared** edges are exactly three (`memo-agent-core`, `memo-extensions`, `outlier-model`), yet the ~5 metrics also draw on `rules-engine` and `audit-store` emitted events (§3). Under emit-only/stack-agnostic, U21 receives **events**, not imports.

- **A. Consume events via a generic, duck-typed/structural sink — import no emitting unit's event type into production; the metric derivations read the typed fields by shape.** Keeps U21's production import surface minimal and honors the three declared edges as *trace-step* edges (the graph nodes), while the metric side consumes generic emitted events with **no new code edge** to `rules-engine`/`audit-store`. Tier-U drives fake events shaped by value. *(Recommended — matches the "thin, stack-agnostic seam" the frozen docstrings describe; avoids widening U21's edges beyond the frozen three; no frozen event schema is imported/owned.)*
- **B. Import each unit's frozen event schema** (`MemoTelemetryEvent`, the rules/audit/intake events) for typed derivations. Stronger typing, but **widens U21's dependency edges beyond the declared three** (adds `rules-engine`, `audit-store`, `intake`) — a decomposition-edge question that should be decided deliberately, not by import.
- **C. Flag the edge-set mismatch as a decomposition gap and STOP** — if you consider the ~5-metric span vs the three declared edges a `unit-of-work-dependency.md` inconsistency to resolve before U21's FD proceeds.

`[Answer]:` A

---

## 5.5 MANDATORY AMBIGUITY-CHECK — RUN 2026-07-17 against Q1–Q5 (all A) + the frozen substrate → **CLEAN (3 folds; no surface-and-stop)**

Checked against the four P1 `TelemetryEmitter` docstrings; **U4's ACTUAL frozen `orchestrator.py`** (re-read this session — nodes + checkpointer + the emit shape); `unit-of-work-dependency.md:50` declared edges; the NFR-OBS-2 five-metric span. **Each of the user's three flagged checks resolved against a frozen fact, none improvised.**

### FD-OBS-Fold-1 — [CHECK (i)] the 100%-step coverage proof is GROUNDED in U4's real node list; and the graph-node vs all-agent/tool-step boundary is NAMED, not glossed
**U4's frozen memo graph has exactly four nodes** — `draft` · `validate` · `finalize` · `flag` — with edges `START→draft→validate→{finalize | draft(retry) | flag}→END`, compiled with a `MemorySaver` checkpointer (the docstring's *"100%-step tracing"* hook), and **one** `MemoTelemetryEvent` emitted at end of `run()`. So the recording-fake step sequence for the 100%-coverage proof is the **real** node list — a happy path `draft→validate→finalize` and a retry/blocked path `draft→validate→draft→…→validate→flag` — **not an invented sequence**.
**The honest boundary (disclosed, not glossed)**: *"100% of agent/tool steps"* resolves in two grounded parts — **(a)** every **graph node** is auto-traced **by construction** because the Langfuse callback fires per checkpointer step (provable at tier-U: the recording fake yields exactly one span per node over the real sequence); **(b)** the **non-graph tool steps** that are NOT nodes of this frozen graph — U18 outlier scoring (upstream of the memo graph), U19 `route_borderline`/adapter-selection (at composition, before the graph) and MCP retrieval (U19's `McpToolService`, which the frozen `_draft_node` does **not** call — it calls `PromptBuilder.build` directly) — are traced by a **general span API** (a context-manager/decorator U21 defines) that **composition applies at those call sites**. So U21 defines **two trace mechanisms** (the checkpointer callback for graph nodes + the span API for wrapped tool steps); the **system-wide 100% audit is AC-7's deploy-time Langfuse trace audit**, not a tier-U unit assertion. **No frozen unit is edited** (the callback attaches to the frozen checkpointer at composition; the span API wraps call sites at composition). This is a direct consequence of Q1-A + Q3-A + the frozen orchestrator — named here so Code-Gen cannot invent an arbitrary step set.

### FD-OBS-Fold-2 — [CHECK (ii)] a single occurrence in BOTH planes needs no NEW shared concept — it draws on TWO pre-existing FROZEN streams
A memo completion is **one graph node** (`finalize`/`flag` → a span, trace plane) **and** emits **one `MemoTelemetryEvent`** carrying `recommendation` (→ the *decisions by recommendation type* metric, metric plane). These are **two already-existing frozen streams** — the checkpointer's node executions **and** the emitters' event lists — **not** one bus that must be invented. The two Q2-A sub-components each consume one stream; a single business occurrence legitimately appears in both **without** conflating the mechanisms (that would be Q2-B, rejected). The FD **names** the two frozen source streams explicitly so the separation is principled, not accidental. **No shared upstream concept is missing.**

### FD-OBS-Fold-3 — [CHECK (iii)] Q5 duck-typed consumption has a concrete NON-VACUITY mechanism (the detector-self-test analog)
*"Consumes events structurally"* must not become *"trusts events blindly."* The mechanism (mirroring every prior unit's detector self-test): U21's derivations/sinks read **only the enumerated allowlist field names by shape**, and a **detector self-test feeds a synthetic event carrying a forbidden attribute** (a free-text / demographic / `original_span`-style field) and asserts U21's sink/derivation **does not read or propagate it** — the forbidden value never reaches a trace attribute or a metric label. Plus a **structural scan**: no U21 sink reads a non-allowlisted attribute name. So U21's *own* demographic-free-by-construction guarantee for its sinks is **verified, not assumed** — even though the upstream emitters already enforce it at emit time. (The 2 of 5 metrics with no frozen emitter field — *LLM-call errors*, *outlier-flag rate* — derive from **step outcomes** observed at the span-API boundary, tested at tier-U against fake step outcomes; their real capture is composition-wired.)

**Verdict: CLEAN — no genuine gap requires a decision.** All three checks resolve against frozen facts (U4's real 4-node graph + emit shape; the two frozen streams; the allowlist-read + detector-self-test discipline). The graph-node/tool-step boundary and the 2-source metric split are **named** (Fold-1/-3), not improvised. → **Part 2 authorized.**

---

## 6. HOLDS (binding on Part 2)
- **No frozen unit edited** — `memo-agent-core` (U4) + all 17 frozen P1 units, `outlier-model` (U18), `memo-extensions` (U19), `ui-outlier-view` (U20) are **read-only references**; their `telemetry.py` emitters and the graph checkpointer are **consumed, never modified**.
- **WIRE-1 untouched**; the **closed composition root untouched** (the live wiring parallel is *named* here, not performed); **tier-B NOT authorized** (and N/A); the **`audit_store` Docker-guard gap untouched**.
- **No live LLM call, no key, no network, no live Langfuse/Prometheus** at tier-U; keys are `secrets-config`'s (SEC-3).
- **Demographic-free by construction is inherited** — U21 may not introduce a trace/metric field that carries prose/PII/`original_span`; the allowlist discipline the four emitters already enforce extends to every sink.
- **No new domain contract; no recommendation-producing path.** **No other unit started.** The **23-unit decomposition unchanged.**
- **No FD artifact, no code, no `backend/observability/`** until the five answers are filled, the ambiguity-check runs, and Part 2 is explicitly authorized.

## 7. Gate
- [x] **(1)** **Q1–Q5 answered — all A**; full question text + answers embedded (§5) per the standing convention.
- [x] **(2)** Mandatory **ambiguity-check RUN** (§5.5) → **CLEAN** (3 folds, no surface-and-stop) — the three user-flagged checks resolved against frozen facts (U4's real 4-node graph + emit shape; the two frozen streams; the allowlist-read + detector-self-test discipline).
- [x] **(3)** **FD Part 2 GENERATED** — `guide-docs/build/observability/functional-design/`: `domain-entities.md` + `business-rules.md` (**BR-OBS-1..7**) + `business-logic-model.md` (validated rectangle-only Mermaid + text alternative).
- [ ] **(4)** **FD 2-option completion gate — AWAITING USER.** (1. Request Changes / 2. Continue to Next Stage → **NFR Requirements**.)

**STOPPED at the FD 2-option completion gate.** NFR Requirements does **not** begin until the gate is answered.

**STOPPED — no FD artifact, nothing under `backend/observability/`.** Part 2 does **not** begin until the five answers are filled and the ambiguity-check runs.
