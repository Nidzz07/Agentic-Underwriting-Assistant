# Infrastructure Design — `observability` (U21, EPIC-6, Phase 2)

**Stage**: BUILD → Infrastructure Design (per-unit) · **the SECOND non-skip Infrastructure Design in the build** (after `database` U15)
**Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Date**: 2026-07-18 · **Depth**: **comprehensive** (the wiring-heavy stage).
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` **BR-OBS-1..7** / `business-logic-model.md`), the approved
`nfr-requirements.md` (**eleven `NFR-OBS-*`** + `tech-stack-decisions.md` **OBS-D1..D9** + **`OBS-SINK-DEFERRED`**), and the approved
NFR Design (`nfr-design-patterns.md` **P-OBS-1..11** + `logical-components.md` **C-OBS-1..4**) — **re-opening none of them**. This
stage designs the **deferred halves** `OBS-SINK-DEFERRED` explicitly handed here: **the live Langfuse binding, the `/metrics` mount +
scrape, the one Grafana dashboard topology, the `secrets-config` key delivery, and AC-7's deploy-time trace audit.** It designs **how
the frozen sinks/derivations are bound / mounted / scraped / delivered per environment** — it does **NOT** re-open the `TraceSink`/
`MetricExporter` Protocols, the derivations, or the allowlist. Answers **Q1–Q9 (all A)** + folds **INFRA-OBS-Fold-1..3** (plan §3.5).

> **SEC-3 / BR-SEC-6 held throughout**: **no credential / key / endpoint VALUES** appear in this artifact — only variable-name
> **shapes** (the reserved `LANGFUSE_*` names) + the `secrets-config` contract. The **frozen `secrets_config.Settings` model is NOT
> edited** (`extra="ignore"` is the sanctioned Phase-2 seam). **BR-OBS-1 / NOEDIT-1 held**: no frozen unit is edited — the live
> binding is composition/deploy-config's; **U4's `LangGraphOrchestrator` is NOT edited**.

---

## 1. Component → infrastructure mapping (C-OBS-1..4)

The four NFR-Design components are either **bound to a real per-environment sink** (given a live home at composition/prod) or **noted
as app/test logic** needing no cloud topology. The `TraceSink`/`MetricExporter` Protocols + the derivations + the allowlist stay the
**sole telemetry authority** — Infrastructure Design **binds** them, it does **not** author telemetry shape.

| Component | Kind | Infrastructure realization (this stage) |
|---|---|---|
| **C-OBS-1 `trace-side`** (`TraceSink` + `TraceRecorder.on_step`/`span`) | injected trace sink + two callers | **Bound** at composition to the real `langfuse` `TraceSink` adapter (§3.1). The **run-level span** + **tool-step spans** wrap at composition **with no U4 edit** (Fold-1b). The **per-internal-graph-node** callback is the **only** deferred bit (Fold-1c, §3.1). Interface unchanged. |
| **C-OBS-2 `metric-side`** (`MetricExporter` + `derive_from_event`/`derive_from_step_outcome`) | injected exporter + registry | **Bound** at composition to the `prometheus-client` registry behind the `MetricExporter` Protocol; `/metrics` mounted on the **existing** FastAPI service (§3.2). The `MemoTelemetryEvent`-sourced derivations ride U4's **existing** `telemetry` seam (Fold-1a). Derivations unchanged. |
| **C-OBS-3 `allowlist`** (`project_allowlisted`) | pure app logic | **No cloud topology.** Runs in-process on every span/label projection; named, not provisioned. |
| **C-OBS-4 `StructuralGuard`** | test-only | **No cloud topology.** The five AST scans run in CI/unit; named, not provisioned. |

**Infra binds the sinks C-OBS-1/C-OBS-2 export through; C-OBS-3/C-OBS-4 are app/test logic that need only the running process.**

---

## 2. Mandatory infra-category sweep (all seven categories — explicit applicability + justification)

| # | Category | Applicability | Justification |
|---|---|---|---|
| 1 | **Deployment Environment** | **Applicable** | Three tiers — **dev** (observability optional/local, opt-in Compose profile), **CI** (**no live sinks** — offline recording fakes; 31 skips + 5 Docker errors unchanged), **prod** (Render backend `/metrics` + Langfuse Cloud + Prometheus + Grafana, free-tier). §3 + `deployment-architecture.md`. Q1-A. |
| 2 | **Storage Infrastructure** | **N/A-as-owned (narrow)** | `observability` provisions **no** persistence. **Trace retention is Langfuse's** store; **metric retention is Prometheus's** TSDB — both **provider-managed**. Named, not provisioned. Q7-A. |
| 3 | **Compute Infrastructure** | **N/A-as-owned (narrow)** | **No new long-running compute.** `/metrics` rides `deploy-config`'s **existing** Render web service; the Langfuse callback runs **in-process**; Prometheus/Grafana are **managed free-tier** services. Q3-A / Q7-A. |
| 4 | **Messaging Infrastructure** | **N/A (justified)** | **No queue / event bus.** Traces flow via an in-process callback / the SDK, **not** an outbox/saga; a telemetry sink has no async/eventing concern. Q7-A. |
| 5 | **Networking Infrastructure** | **Applicable (narrow)** | The `/metrics` **scrape path** exposure; **HTTPS egress** to the Langfuse host; Prometheus→backend **scrape**; Grafana→Prometheus **datasource**. SSL is provider-managed; keys via `secrets-config`. **No LB / gateway / custom VPC.** §3.2 + `deployment-architecture.md §4`. |
| 6 | **Monitoring Infrastructure** | **Applicable (CORE)** | `observability` **IS** the monitoring infra — the **Langfuse** trace backend, the **Prometheus** scrape, the **one Grafana dashboard**. §3.1–§3.3. Q2/Q3/Q4/Q6. |
| 7 | **Shared Infrastructure** | **Applicable (narrow)** | The stack is **shared-by-observation** (all traced units feed it), but U21 provisions **no shared instance** (unlike `database`'s Postgres); the sinks are **single composition-wired consumption points**. **No separate `shared-infrastructure.md`** (Q8-A) — captured in `deployment-architecture.md`. |

**No category silently skipped.** Storage / Compute / Messaging are **N/A-as-owned / justified**, recorded in the completion
compliance summary.

---

## 3. Deferred-halves execution design

### 3.1 The live Langfuse binding — the composition-level mechanism (Q2-A / P-OBS-1 / Fold-1) — **FOLD #1**

C-OBS-1's `TraceSink` Protocol + `TraceRecorder` (`on_step` callback + `span` context-manager) are **injected**; this stage pins their
**per-environment binding** without editing any frozen unit. The binding has **three sub-cases — two already free of U4, one deferred**:

1. **Metric-plane memo completion — already wired via U4's existing seam (Fold-1a).** The frozen `LangGraphOrchestrator.__init__`
   **already** accepts `telemetry: Optional[TelemetryEmitter]`, and `_emit` fires **one** `MemoTelemetryEvent` per `run()`. At
   composition the orchestrator is constructed with a `TelemetryEmitter` whose sink drives U21's `derive_from_event` (→ *decisions by
   recommendation type*, *decision latency*). **No U4 edit** — this is the frozen constructor seam used as intended.
2. **Trace-plane run-level + tool-step spans — wrapped at composition (Fold-1b).** The composition root constructs the real `langfuse`
   `TraceSink` adapter, injects it into `TraceRecorder`, and drives `TraceRecorder.span("memo_run", …)` **around** the `orchestrator.run()`
   call, and `TraceRecorder.span(…)` around each **non-graph tool step** (U18 outlier scoring; U19 `route_borderline` / adapter selection
   / MCP retrieval) at their call sites. **No U4 edit** — the span API wraps callers, it does not reach inside the graph.
3. **Trace-plane per-INTERNAL-graph-node spans — the ONLY deferred item (Fold-1c).** Emitting `draft` / `validate` / `finalize` / `flag`
   as **separate** spans requires LangGraph's **per-node callback**, which the frozen `run()` (building its invoke `config` internally,
   with **no `callbacks` key**) does not forward, and whose `MemorySaver` checkpointer is a private compiled-graph internal. Its shape is
   **dictated by LangGraph's `invoke(config={"callbacks": […]})` contract** → a future **minimal additive `callbacks` / `config`
   passthrough on `run()`** that merges an injected `LangfuseCallbackHandler` (the `TraceRecorder.on_step` adapter) into the existing
   invoke config. **Recorded with that named shape as an `OBS-SINK-DEFERRED` composition item — NOT taken this stage, NOT a U4 edit.**
   U4 stays **frozen**; TRACE-1's tier-U proof (the recording fake over the real node list) is unchanged; the **system-wide 100%** is
   AC-7's deploy-time audit (§3.5).

> **Boundary held**: this stage designs **what composition attaches** (the injected `TraceSink`/`TraceRecorder`), never **attaches** it —
> the live construction lives at the **closed composition root** (`backend/app/main.py`), untouched here. **BR-OBS-1 / NOEDIT-1 real.**

### 3.2 The Prometheus `/metrics` mount + scrape (Q3-A / OBS-D3) — Networking + Monitoring

C-OBS-2's `MetricExporter` Protocol is **injected**; `prometheus-client` is the **deploy-time adapter behind it** (OBS-D3/D4 — not
exercised at tier-U). The binding:

1. **The in-memory registry C-OBS-2's derivations write to is the same registry the exporter reads.** At composition the `MetricExporter`
   Protocol is bound to the `prometheus-client` `CollectorRegistry`; `derive_from_event` / `derive_from_step_outcome` contributions land
   in it.
2. **`/metrics` is mounted on the EXISTING FastAPI web service** (`backend/app/main.py` — `deploy-config`'s Render service) via
   `prometheus-client`'s ASGI/route exporter. **No new compute** — `/metrics` rides the existing process (Q7-A Compute N/A-as-owned).
3. **Prometheus scrapes the `/metrics` path** at a fixed interval — a **Grafana Cloud agent** or a **Render-hosted Prometheus** (Q1-A,
   free-tier). Pull-based: **no app-side key** on `/metrics` (Q5-A).

> **Boundary held**: U21 **defines** the `MetricExporter` Protocol; the **route mount + scrape config** are a **composition / deploy-config**
> deliverable this stage *names*, never mounts (BR-OBS-1).

### 3.3 The one Grafana dashboard topology (Q4-A / NFR-OBS-2) — **FOLD #2**

**One dashboard** (NFR-OBS-2), datasource = **Prometheus**, **five panels mapped 1:1 to the five frozen metrics** (`domain-entities.md §4`):

| Panel | Metric (frozen) | Kind → panel | Label(s) — allowlist only |
|---|---|---|---|
| 1 | decision latency | histogram → latency-quantile / heatmap | — |
| 2 | decisions by recommendation type | counter → bar / stat by `recommendation` | `recommendation` (enum value) |
| 3 | rule-evaluation duration | histogram → duration panel | — |
| 4 | LLM-call errors | counter → stat / timeseries | — |
| 5 | outlier-flag rate | counter-gauge → stat / gauge | — |

**Every label is an enum value / count — no demographic, no per-applicant, no free-text panel** (CON-BR1, inherited from the frozen
allowlist labels). **This stage designs the panel→metric TOPOLOGY** (Fold-2). The committed **dashboard-as-code JSON / provisioning file**
is a **Code-Gen / deploy-config deliverable** (keeps this stage's *"no code / no `backend/observability/`"* hold); its home is
**named-not-created** — a committed dashboards path finalized at Code-Gen. The live Grafana instance is provider-managed (Q1-A). No U23
is required to design the topology now.

### 3.4 `secrets-config` key delivery (Q5-A / SEC-3 / BR-SEC-6) — **FOLD #3 (secrets)**

`secrets-config` (U16) owns **all key/endpoint VALUES**; the frozen `Settings` model validates only the six Phase-1 vars and uses
**`extra="ignore"`** (Phase-2 vars ignored, not errors). `.env.example` **reserves** the three observability keys as
**"reserved-not-authored (BR-SEC-6)"**. This stage **authors the observability secret shapes** (moving them from *reserved* to
*named-and-consumed*) — **variable NAMES only, never a value**, and **without editing the frozen `Settings` model**.

| Variable (shape) | Purpose | Delivery |
|---|---|---|
| **`LANGFUSE_PUBLIC_KEY`** | Langfuse client auth (public) | Phase-2 env var, wired per-tier by `deploy-config`; consumed at the **sink-binding boundary at composition** (the `langfuse` SDK reads `LANGFUSE_*` from env by convention, or composition passes them to the injected `TraceSink` adapter). **Ignored by frozen `Settings`** via `extra="ignore"`. |
| **`LANGFUSE_SECRET_KEY`** | Langfuse client auth (secret) | as above — never committed; never logged (SEC-3). |
| **`LANGFUSE_HOST`** | Langfuse endpoint (cloud or self-hosted) | as above — a **host shape**, never a concrete URL value in any artifact. |

- **Prometheus** scrape is **pull-based** → **no app-side key** on `/metrics`. **Grafana** auth is **provider-managed** → **no
  app-authored secret**. So the **only** new secret shapes are the three reserved `LANGFUSE_*` names.
- **Why not extend `Settings`?** Adding `LANGFUSE_*` fields would **edit frozen `secrets-config` (U16)** — a BR-OBS-1 / NOEDIT-1 hold
  violation. The frozen model's **`extra="ignore"` is the sanctioned Phase-2 seam** the `.env.example` reservation already anticipated;
  the keys reach the SDK **without** passing through `Settings` validation. `Settings` stays **frozen**.

> **Boundary held (reference-not-own)**: `secrets-config` owns the vault/env wiring + `.gitignore` governance; `deploy-config` wires the
> real per-tier values; this artifact names **only the shapes**.

### 3.5 AC-7's deploy-time 100%-trace audit (Q6-A / BR-OBS-6 / TRACE-1 split) — **FOLD #3 (audit)**

**AC-7 ("100% of agent steps traced") is a DEPLOY-TIME acceptance check, not a tier-U assertion** — the explicit TRACE-1 / BR-OBS-6 split.
After the live binding (§3.1–§3.2), the deploy validation confirms that for a **sample request** the observed Langfuse span set
**⊇ `{draft, validate, finalize, flag}`** (U4's **real** node list) **+ the composition-wrapped tool steps** (§3.1 case 2). Named here as
the **`deploy-config` + AC-7 acceptance**, grounded in the **frozen node list**; the **exact verification mechanism** (Langfuse API query
vs UI inspection) is **`deploy-config`'s / AC-7's to own — not prescribed here** (Fold-3). **Not run at this stage** (no live sink here).
It is the **`OBS-SINK-DEFERRED` closing condition** — the register item is discharged only once AC-7 passes at deploy.

---

## 4. Reference boundaries (owned elsewhere — named, not authored here)

| Concern | Owner |
|---|---|
| All Langfuse key/endpoint **VALUES**; `.env` / `.gitignore` governance | **`secrets-config`** (U16) |
| The Render/Vercel **deploy pipeline** + per-tier env wiring + the `/metrics` route mount + the scrape config + the committed dashboard-as-code file | **`deploy-config`** (U23) |
| The **live sink construction + attachment** (the `TraceSink`/`MetricExporter` adapters, the run-level/tool-step span wraps) | **the closed composition root** (`backend/app/main.py`) |
| The frozen `LangGraphOrchestrator` (nodes + `MemorySaver` checkpointer + `run()`); the future `callbacks` passthrough, if ever taken | **`memo-agent-core`** (U4) |
| **AC-7** deploy-time trace-audit **verification mechanics** | **`deploy-config`** + **AC-7** |

---

## 5. Deferred decisions recorded this stage

- **`OBS-SINK-DEFERRED` (OPEN, refined — NOT closed here)**: the live binding is **designed** (§3.1–§3.5) but **not wired** — the register
  item is discharged only at composition/deploy-config once AC-7 passes. **Refinement**: the **only** genuinely U4-blocked sub-item is the
  **per-internal-graph-node callback** (Fold-1c), whose shape is now **named** (a minimal `callbacks`/`config` passthrough on `run()`) so a
  future composition pass does not start from zero. **NON-blocking, NON-dependency** (both SDKs floored+installed).
- **The dashboard-as-code file home** is **named-not-created** (Fold-2) — finalized at Code-Gen / deploy-config.

---

## 6. Constraints & settled items held (not re-opened)

- FD + approved `NFR-OBS-*` + `P-OBS-1..11` + `C-OBS-1..4` are the substrate — Infra **maps** them, re-opening none. **The `TraceSink`/
  `MetricExporter` Protocols + the derivations + the allowlist are NOT re-opened** — only their **binding / mount / scrape / dashboard /
  key delivery** per environment is designed.
- **BR-OBS-1 / NOEDIT-1**: **no frozen unit edited** — the live binding is composition/deploy-config's. **U4's `LangGraphOrchestrator`
  NOT edited**; the **frozen `secrets_config.Settings` model NOT edited** (`extra="ignore"` is the sanctioned seam).
- **SEC-3 / BR-SEC-6**: no key/endpoint **values** — only variable-name **shapes** (the reserved `LANGFUSE_*`) + the `secrets-config`
  contract; keys never logged. **CON-BR1**: no demographic label, metric, or dashboard panel.
- **Observed-never-gated** (CONTRACT-1 / PERF-1): latencies recorded, never asserted-as-failure; no hard SLO.
- **AC-7 is deploy-time** (BR-OBS-6), not tier-U — **tier-U stays offline** (no live sink); **31 skips + 5 Docker errors unchanged**.
- **No new dependency** (`langfuse` + `prometheus-client` floored + installed); `requirements.txt` NOT edited.
- **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition
  unchanged**. Settled non-edits stay closed: WIRE-1 · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · the
  17 frozen P1 units · the closed composition root.
