# Infrastructure Design Plan (Part 1) — `observability` (EPIC-6 / U21, Phase 2)

**Phase / Stage**: BUILD → Infrastructure Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `observability` (U21) · FD ✅ · NFR Requirements ✅ · **NFR Design ✅ (approved 2026-07-18)**
→ **Infrastructure Design ← here (the REAL, comprehensive one — NOT a skip)** → Code Generation.
**Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Date**: 2026-07-18 · **Depth**: **comprehensive** (the wiring-heavy stage).
**Status**: **Plan — awaiting `[Answer]:` tags. NO Infrastructure-Design artifacts generated this stage. Stop after this plan.**

This plan follows `.project-guide-rule-details/build/infrastructure-design.md`. It **maps the logical components (C-OBS-1..4)
to actual infrastructure** across dev / CI / prod, built **ON** the frozen FD (`domain-entities.md` / `business-rules.md`
**BR-OBS-1..7** / `business-logic-model.md`), the approved `nfr-requirements.md` (**eleven `NFR-OBS-*`** + `tech-stack-decisions.md`
**OBS-D1..D9** + **`OBS-SINK-DEFERRED`**), and the approved NFR Design (`nfr-design-patterns.md` **P-OBS-1..11** +
`logical-components.md` **C-OBS-1..4**) — **re-opening none of them**. This stage designs the **deferred halves** that every
prior U21 stage explicitly handed here (the `OBS-SINK-DEFERRED` register item): **the live Langfuse callback→checkpointer
binding, the Prometheus `/metrics` mount + scrape, the one Grafana dashboard topology, the `secrets-config` key delivery, and
AC-7's deploy-time 100%-trace audit.** **No credentials/endpoints/keys as VALUES appear here** — only variable-name **shapes**
+ the `secrets-config` contract (SEC-3).

> **Why this is a real stage (NOT a skip — unlike the four cluster units and the memo-extensions Infra SKIP)**: `observability`
> **IS the monitoring/telemetry topology** — the live Langfuse trace backend, the Prometheus scrape path, the one Grafana
> dashboard, and the composition-wired sink bindings. **Three prior U21 stages named these deferrals and pointed them at this
> exact stage** (FD `domain-entities.md §5`; `tech-stack-decisions.md §3` `OBS-SINK-DEFERRED`; `logical-components.md §3`
> category 3). `unit-of-work.md:248` pins U21 **"comprehensive at Infrastructure Design (wiring-heavy)"** — the single P2 unit
> so classified, the *opposite* of every prior P2 skip. Confirmed against the completed FD/NFR-Requirements/NFR-Design: the live
> wiring, the `/metrics` mount, the Grafana topology, and the key delivery were resolved by **no** prior stage. This is the
> **2nd real non-skip Infrastructure Design in the whole build, after `database` (U15)** — planned with the same rigor.

---

## 1. Unit context (analyzed)

### 1.1 What Infrastructure Design maps (built ON — NOT re-opened)
- **From NFR Design (C-OBS-1..4)**: **C-OBS-1 `trace-side`** (`TraceSink` Protocol + `TraceRecorder.on_step`/`span`, two callers
  — its *interface* is fixed; its **live sink binding** per environment is designed here), **C-OBS-2 `metric-side`**
  (`MetricExporter` Protocol + `derive_from_event`/`derive_from_step_outcome`, distinct `_EVENT_ALLOWED`/`_STEP_ALLOWED` — its
  *derivations* are fixed; the **`/metrics` mount + Prometheus exporter binding** is designed here), **C-OBS-3 `allowlist`**
  (pure `project_allowlisted` — pure app logic, needs no cloud topology), **C-OBS-4 `StructuralGuard`** (test-only — no topology).
- **From the FD/NFR (BR-OBS-1..7 / eleven `NFR-OBS-*`)**: **BR-OBS-1 / NOEDIT-1** (U21 edits no frozen unit; composition wires
  — the live binding is composition/deploy-config, never inside U21); **BR-OBS-2 / TRACE-1** (100%-step coverage over U4's real
  4-node list — the deploy-time audit half is **AC-7**, designed here as an acceptance, not a tier-U test); **NFR-OBS-2** (one
  dashboard, ~5 metrics); **SEC-3** (no key/endpoint VALUES in artifacts); **CON-BR1** (no demographic label/metric/panel).

### 1.2 The deferred halves this stage designs (the `OBS-SINK-DEFERRED` register item — verbatim from the frozen artifacts)
1. **The live Langfuse callback→checkpointer binding** — plugging the real `langfuse` trace sink into U4's frozen graph
   step stream (Q2).
2. **The Prometheus `/metrics` mount + scrape** — the `prometheus-client` exporter on the existing web service + the scrape
   config (Q3).
3. **The one Grafana dashboard topology** — the single dashboard NFR-OBS-2 specifies, panel layout for the ~5 metrics (Q4).
4. **`secrets-config` key delivery** — how the reserved `LANGFUSE_*` env vars reach the SDK at runtime without editing frozen
   `secrets-config` (Q5).
5. **AC-7's deploy-time 100%-trace audit** — the deploy-time acceptance that every step appears in Langfuse (Q6).

### 1.3 Reference boundaries (owned elsewhere — named, not authored here)
- **`secrets-config`** (U16, SEC-3) owns **all key/endpoint VALUES**. `secrets_config.Settings` is **frozen** — it validates
  the six Phase-1 vars and uses **`extra="ignore"`** (Phase-2 vars ignored, not errors); `.env.example` **reserves**
  `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`/`LANGFUSE_HOST` as **"reserved-not-authored (BR-SEC-6)"**. This plan names the
  **variable-NAME shapes only**, never values — and **does not edit the frozen `Settings` model** (Q5).
- **`deploy-config`** (U23) owns the **Render/Vercel deploy pipeline + the per-environment env wiring** the sink bindings plug
  into — this plan designs the **binding + mount + scrape + dashboard requirements** `deploy-config` wires.
- **the closed composition root** (`backend/app/main.py`) owns the **live sink construction + attachment** — this plan names
  **what** it must attach (the injected `TraceSink`/`MetricExporter` adapters), never editing it here.
- **`memo-agent-core` (U4)** owns the frozen `LangGraphOrchestrator` (`draft`/`validate`/`finalize`/`flag` + `MemorySaver`
  checkpointer + `run()` with an internally-built invoke `config`) — **read-only**; this stage designs the binding **around** it,
  never edits it (Q2).

### 1.4 Guardrails held (skill)
NFR-OBS-* (observe, never gate); **BR-OBS-1 / NOEDIT-1** (no frozen edit — the live binding is composition's); **SEC-3** (no
key/endpoint values in artifacts — `secrets-config` supplies them; the frozen `Settings` model **not** edited); **CON-BR1** (no
demographic label/metric/panel); **advisory-only** (U21 declares no recommendation/verdict). **No LLM path in `observability`.**
**No new dependency** (`langfuse>=2.0.0` + `prometheus-client>=0.21.0` already floored + installed — verified). **tier-B N/A +
NOT authorized.** The **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged).

---

## 2. Mandatory infra-category pre-assessment (all seven — applicability + justification)

| # | Category | Applicability | Where |
|---|---|---|---|
| 1 | **Deployment Environment** | **Applicable** — dev / CI / prod tiers for the observability stack (backend `/metrics`, Langfuse, Prometheus, Grafana) | Q1 |
| 2 | **Storage Infrastructure** | **N/A as owned (narrow)** — U21 provisions no persistence; trace retention is **Langfuse's** store, metric retention is **Prometheus's** TSDB, both provider-managed. Named, not provisioned | Q7 |
| 3 | **Compute Infrastructure** | **N/A as owned (narrow)** — no new long-running compute; `/metrics` rides `deploy-config`'s existing Render web service, the Langfuse callback runs in-process; Prometheus/Grafana are managed free-tier services | Q3, Q7 |
| 4 | **Messaging Infrastructure** | **N/A (justified)** — no queue/event bus; traces flow via in-process callback / SDK, not an outbox/saga | Q7 |
| 5 | **Networking Infrastructure** | **Applicable (narrow)** — the `/metrics` scrape path exposure; HTTPS egress to the Langfuse host; Prometheus→backend scrape; Grafana→Prometheus datasource. SSL/keys via `secrets-config` | Q3, Q5 |
| 6 | **Monitoring Infrastructure** | **Applicable (CORE)** — `observability` **IS** the monitoring infra: the Langfuse trace backend, the Prometheus scrape, the one Grafana dashboard | Q2, Q3, Q4, Q6 |
| 7 | **Shared Infrastructure** | **Applicable (narrow)** — the stack is shared-by-observation (all traced units feed it), but U21 provisions no shared *instance* (unlike `database`'s shared Postgres); the sinks are single composition-wired consumption points | Q8 |

**No category silently skipped.** Storage / Compute / Messaging are **N/A-as-owned / justified**, recorded in the completion
compliance summary.

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide the
**infrastructure mapping** — they do **not** re-open the FD, the eleven `NFR-OBS-*`, `P-OBS-1..11`, or `C-OBS-1..4`.

## Question 1 — Deployment topology across tiers (dev / CI / prod)
Where do the Langfuse trace backend + Prometheus + Grafana live per tier, at what cost tier?

A) **Three-tier, free-tier throughout (matching U23's Phase-2 validation deploy)**: **dev** = observability **optional/local**
   (Langfuse self-hosted or disabled; Prometheus + Grafana via an *optional* Docker Compose profile a developer can opt into) —
   never required to run the app; **CI** = **NO live sinks** — offline recording fakes only (the frozen tier-U discipline;
   BR-OBS-6 / TIERU-1; **31 skips + 5 Docker errors unchanged**); **prod** = **Render** backend exposing `/metrics` + **Langfuse
   Cloud** (managed free-tier) for traces + **Prometheus + Grafana** (Grafana Cloud free-tier *or* Render-hosted) for metrics.
   Free-tier everywhere (distinct from Phase-3 production, per `unit-of-work.md` U23).
B) Stand up a full self-hosted Langfuse + Prometheus + Grafana cluster now (rejected — over-engineering for a Phase-2 free-tier
   validation deploy).
C) Live sinks in CI (rejected — breaks the tier-U no-network/no-key discipline; would change the 31 skips / 5 Docker errors).
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 2 — The live Langfuse callback→checkpointer binding (the frozen-orchestrator constraint)
The frozen `LangGraphOrchestrator.run()` builds its LangGraph invoke `config` **internally** as
`{"configurable": {"thread_id": …}}` and exposes **no callbacks channel**; the `MemorySaver` checkpointer is a private
compiled-graph internal. How does the **real** Langfuse trace sink attach to the graph step stream **without editing U4**?

A) **Composition-level binding via U21's injected `TraceSink`/`TraceRecorder` seam** (BR-OBS-1 / P-OBS-1 — the composition-root
   parallel): the **composition root** constructs the real `langfuse` `TraceSink` adapter and drives `TraceRecorder` at the
   boundary that invokes `orchestrator.run()`. The **metric-plane** graph-completion signal is already available **by
   construction** — the frozen `MemoTelemetryEvent` (one per `run()`) carries `recommendation`/`duration_ms`/`draft_attempts`.
   For the **per-node trace spans** (`draft`/`validate`/`finalize`/`flag`), because `run()` cannot accept LangGraph callbacks
   and its checkpointer is private, the precise per-node callback attachment is recorded as an **`OBS-SINK-DEFERRED` composition
   item** that, **if** the raw per-node callback is ever needed beyond the wrapped-tool-step span API, requires a **future
   MINIMAL additive seam** on the orchestrator (a `callbacks`/`config` passthrough) — **NOT taken here, NOT a U4 edit this
   stage**. U4 stays **frozen**; TRACE-1's tier-U proof (the recording fake over the real node list) is unchanged; the
   **system-wide 100%** is AC-7's deploy-time audit (Q6).
B) Edit `orchestrator.run()` to accept + forward LangGraph callbacks now (rejected — edits a frozen P1 unit; BR-OBS-1 / NOEDIT-1
   hold violation).
C) Monkeypatch / a global LangChain callback manager hack (rejected — hidden, fragile, not audit-clean; violates the
   injected-seam discipline).
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3 — Prometheus `/metrics` endpoint mount + scrape
Where is `/metrics` mounted and how is it scraped (no new compute)?

A) **`/metrics` mounted on the EXISTING FastAPI web service** (`backend/app/main.py` — `deploy-config`'s Render service), via
   `prometheus-client`'s ASGI/route exporter, backed by the **same in-memory registry** C-OBS-2's derivations write to (the
   `MetricExporter` Protocol U21 defines binds the `prometheus-client` registry at composition, OBS-D3). **Prometheus** (Grafana
   Cloud agent *or* a Render-hosted Prometheus) scrapes the `/metrics` path at a fixed interval. **No new compute** — `/metrics`
   rides the existing process; the mount + scrape config is a **composition/deploy-config** deliverable this stage *names* (U21
   defines the exporter Protocol, never mounts the route itself — BR-OBS-1).
B) A separate metrics sidecar/pushgateway service (rejected — premature; pull-scrape of an in-process `/metrics` is the standard
   free-tier path).
C) Push metrics to a remote-write endpoint from the app (rejected — over-engineered for the validation deploy; needs no separate
   push path).
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4 — The one Grafana dashboard topology (NFR-OBS-2's "one dashboard")
What is the single dashboard's panel layout for the ~5 metrics?

A) **ONE dashboard, provisioned as-code** (a committed dashboard-JSON / provisioning file), datasource = **Prometheus**, with
   **five panels — one per frozen metric**: *decision latency* (histogram → latency-quantile/heatmap panel) · *decisions by
   recommendation type* (counter → bar/stat by the `recommendation` label) · *rule-evaluation duration* (histogram panel) ·
   *LLM-call errors* (counter → stat/timeseries) · *outlier-flag rate* (counter-gauge → stat/gauge). **Every label is an enum
   value / count — no demographic, no per-applicant, no free-text panel** (CON-BR1, inherited from the frozen allowlist labels
   in `domain-entities.md §4`). Dashboard-as-code is **committed** (reproducible); the live Grafana instance is provider-managed
   (Q1). U21 pins the **panel→metric topology**; exact panel styling is a deploy-config realization.
B) Multiple dashboards / a per-unit dashboard each (rejected — NFR-OBS-2 specifies **one** dashboard).
C) Hand-built dashboard clicked together in the Grafana UI, not committed (rejected — non-reproducible; drifts; not
   version-controlled).
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5 — `secrets-config` key delivery (the frozen-Settings constraint) — SEC-3 / BR-SEC-6
The frozen `secrets_config.Settings` validates only the **six Phase-1 vars** and uses **`extra="ignore"`** (Phase-2 vars
ignored, not errors); `.env.example` **reserves** `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`/`LANGFUSE_HOST` as
**"reserved-not-authored (BR-SEC-6)"**. How are the Langfuse keys delivered to the SDK at runtime — and what about Prometheus/Grafana?

A) **The three `LANGFUSE_*` vars are Phase-2 env vars supplied by the deploy environment** (`deploy-config` wires real
   per-tier values). Because frozen `Settings` uses **`extra="ignore"`**, they are **NOT added to the frozen `Settings` model**
   (editing U16 = a BR-OBS-1 / NOEDIT-1 hold violation) — they are consumed at the **sink-binding boundary at composition** (the
   `langfuse` SDK reads `LANGFUSE_*` from env by its own convention, or composition passes them to the injected `TraceSink`
   adapter). Infrastructure Design **authors the observability secret shapes** — moving them from *"reserved"* to
   *"named-and-consumed"* per **BR-SEC-6** — naming only variable-NAME **shapes**, never values (SEC-3). **Prometheus** scrape is
   **pull-based** (no app-side key on `/metrics`); **Grafana** auth is **provider-managed** (no app-authored secret). So the
   only new secret shapes are the three reserved `LANGFUSE_*` names.
B) Extend the frozen `Settings` model with `LANGFUSE_*` fields (rejected — edits frozen `secrets-config` U16; hold violation).
C) Hardcode the keys in an observability config file (rejected — SEC-3; the build fails on a hardcoded secret).
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 6 — AC-7's deploy-time 100%-trace audit (the acceptance half of TRACE-1)
How is AC-7 ("100% of agent steps traced") realized — given tier-U already proves the recording-fake coverage but not live capture?

A) **AC-7 is a DEPLOY-TIME acceptance check, not a tier-U assertion** (BR-OBS-6 / TRACE-1's explicit split): after the live
   binding (Q2/Q3), the deploy validation confirms **every graph node** (`draft`/`validate`/`finalize`/`flag`, U4's real list)
   **and every composition-wrapped tool step** appears in Langfuse. Named here as the **deploy-config + AC-7 acceptance**,
   grounded in the frozen node list; **not run at this stage** (no live sink here). Recorded as the deferred acceptance owned by
   `deploy-config` (the trace audit) — the `OBS-SINK-DEFERRED` closing condition.
B) Assert 100% live-trace coverage in CI/tier-U (rejected — needs a live Langfuse backend + key + network; breaks the tier-U
   discipline; contradicts BR-OBS-6).
C) Drop AC-7 as untestable (rejected — AC-7 is a first-class acceptance criterion; it is deploy-time-testable, just not at
   tier-U).
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 7 — Compute / Messaging / Storage (explicit N/A-as-owned justification)
How are these categories handled?

A) **Explicit N/A-as-owned with justification**: **Compute** — no new long-running compute is provisioned by `observability`;
   `/metrics` rides `deploy-config`'s existing Render web service (Q3), the Langfuse callback runs in-process, and
   Prometheus/Grafana are managed free-tier services. **Messaging** — no queue/event bus; traces flow via an in-process callback
   / the SDK, not an outbox/saga (a telemetry sink has no async/eventing concern). **Storage** — U21 provisions no persistence;
   **trace retention is Langfuse's** store and **metric retention is Prometheus's** TSDB, both **provider-managed** (named, not
   provisioned). All three recorded **N/A-as-owned / justified** in the compliance summary.
B) Provision a worker/queue for trace export (rejected — unnecessary; the SDK/callback path suffices).
C) Leave these categories unaddressed (rejected — the rule file requires explicit justification, not silence).
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 8 — Shared Infrastructure (does U21 produce a separate `shared-infrastructure.md`?)
The observability stack is shared-by-observation. Does this stage author a separate shared-infra doc, like `database` did?

A) **No separate `shared-infrastructure.md`** — unlike `database` (which **owns** a shared Postgres *instance* with a role
   model), `observability` provisions **no shared instance**: the sinks are **single composition-wired consumption points** the
   traced units feed. The shared nature is captured **within `deployment-architecture.md`** as the composition-wired sink
   topology. (`database`'s existing `shared-infrastructure.md` already names `observability` as the owner of app-level
   metrics/traces — that reference-not-own boundary is kept, not re-opened.)
B) Produce a separate `observability` `shared-infrastructure.md` (available if you prefer an explicit shared-infra artifact).
C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 9 — Depth + artifacts + Mermaid
Depth, artifacts, and diagrams?

A) **Comprehensive — two artifacts** at `guide-docs/build/observability/infrastructure-design/`: **`infrastructure-design.md`**
   (the **component→infrastructure mapping** C-OBS-1..4 + the **deferred-halves execution design**: the live Langfuse binding
   [Q2], the `/metrics` mount + scrape [Q3], the Grafana dashboard topology [Q4], the `secrets-config` key-delivery contract
   [Q5, shapes only], and the AC-7 deploy-time audit [Q6]) and **`deployment-architecture.md`** (the **dev/CI/prod topology** +
   the **trace/metric flow per tier** + the **Grafana dashboard topology** + **networking** + the
   `secrets-config`/`deploy-config`/composition boundaries). **Validated deployment-topology Mermaid** (7 rules, rectangle-only,
   alphanumeric IDs, quoted labels, no special characters) + **text alternative**. **No separate `shared-infrastructure.md`**
   (Q8-A). **No code; no `backend/observability/`; `requirements.txt` NOT edited; the frozen `Settings` model NOT edited.**
B) Standard — one artifact, one diagram (available if you want it lighter).
C) Minimal — a sketch (rejected — `unit-of-work.md:248` pins U21 comprehensive at Infrastructure Design).
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## 3.5 Mandatory ambiguity-check (RAN against the nine answers + the frozen substrate) → **CLEAN (3 folds; no surface-and-stop)**

Grounded in U4's actual `orchestrator.run()`/checkpointer surface, the frozen `secrets_config.Settings` (`extra="ignore"`),
`.env.example`'s reserved `LANGFUSE_*` shapes, and the approved FD/NFR-Requirements/NFR-Design (incl. `OBS-SINK-DEFERRED` +
BR-OBS-1/NOEDIT-1). The three user-flagged checks each resolve against a frozen fact:

- **INFRA-OBS-Fold-1 [check i] — the deferred per-node-callback item has a CONCRETE, bounded shape (not "zero").** Three sub-cases,
  only one deferred: **(a) metric plane — already wired, no callback:** the frozen `LangGraphOrchestrator.__init__` already accepts
  `telemetry: Optional[TelemetryEmitter]` and `_emit` fires **one** `MemoTelemetryEvent` per `run()`; composition hands it a
  `TelemetryEmitter` whose sink is U21's `derive_from_event` — **no U4 edit**. **(b) trace plane, run-level + tool-step spans —
  wrappable at composition:** `TraceRecorder.span()` wraps the whole `run()` call and each non-graph tool step (U18 scoring, U19
  routing/MCP) at their call sites — **no U4 edit**. **(c) trace plane, per-INTERNAL-graph-node spans** (`draft`/`validate`/`finalize`/`flag`
  as *separate* spans) is the **only** deferred bit: it needs LangGraph's per-node callback, which the frozen `run()` (building its
  invoke `config` internally, no `callbacks` key) does not forward. Its shape is **dictated by LangGraph's `invoke(config={"callbacks": […]})`
  contract** → a future **minimal additive `callbacks`/`config` passthrough on `run()`** merged into the existing invoke config. Recorded
  **with that named shape, NOT taken** (U4 frozen). ⇒ a future composition pass does **not** start from zero. *Sufficient to name the shape.*
- **INFRA-OBS-Fold-2 [check ii] — the dashboard-as-code has a natural split that needs no U23.** The dashboard **TOPOLOGY** (5 panels ↔
  the 5 frozen metrics, datasource = Prometheus, demographic-free) is a **design deliverable** produced **this stage** in the two `.md`
  artifacts — it needs no `deploy-config` (U23) to exist. The committed dashboard-as-code **JSON/provisioning FILE** is a **Code-Gen /
  deploy-config deliverable** (keeps this stage's *"no code / no `backend/observability/`"* hold); its eventual home is **named-not-created**
  (a committed dashboards path finalized at Code-Gen). ⇒ genuinely a design this stage produces without U23. *Clean.*
- **INFRA-OBS-Fold-3 [check iii] — AC-7 is named + grounded, mechanics left to its owner.** AC-7 is recorded as a **deploy-time acceptance**
  grounded in U4's **frozen node list**: for a sample request the observed Langfuse span set **⊇ `{draft, validate, finalize, flag}` + the
  composition-wrapped tool steps**. The **exact verification mechanism** (Langfuse API query vs UI inspection) is **`deploy-config`'s / AC-7's**
  to own — **not prescribed here** (prescribing it would over-reach into an unbuilt unit). ⇒ naming the acceptance shape grounded in the real
  node list is sufficient. *Clean.*

**No new dependency, no frozen edit, no key value surfaced by the check.** Proceed to generate the two artifacts.

---

## 4. Artifacts to generate (after answers + ambiguity-check)
`guide-docs/build/observability/infrastructure-design/` → **`infrastructure-design.md`** (component→infra mapping +
deferred-halves execution design + the `secrets-config` shapes-only contract) + **`deployment-architecture.md`** (dev/CI/prod
topology + trace/metric flow + Grafana dashboard topology + networking + boundaries). Each with a **validated Mermaid + text
alternative**. **No key/endpoint VALUES anywhere** (SEC-3). **No separate `shared-infrastructure.md`** unless Q8-B is chosen.

---

## 5. Constraints & settled items held (not re-opened)
- The frozen FD (**BR-OBS-1..7** + the two sub-components + the grounded node list) + the approved **eleven `NFR-OBS-*`** +
  **`P-OBS-1..11`** + **`C-OBS-1..4`** are the substrate — Infra **maps** them, re-opening none. **The `TraceSink`/`MetricExporter`
  Protocols + the derivations + the allowlist are NOT re-opened** — this stage designs their **live binding / mount / scrape /
  dashboard / key delivery** per environment.
- **BR-OBS-1 / NOEDIT-1**: U21 edits **no** frozen unit — the live binding is **composition/deploy-config's**. **U4's frozen
  `LangGraphOrchestrator` is NOT edited** (Q2); the **frozen `secrets_config.Settings` model is NOT edited** (Q5, `extra="ignore"`
  is the sanctioned Phase-2 seam).
- **SEC-3 / BR-SEC-6**: no key/endpoint/connection **values** in any artifact — only variable-name **shapes** (the reserved
  `LANGFUSE_*` names) + the `secrets-config` contract. **CON-BR1**: no demographic label, metric, or dashboard panel.
- **Observed-never-gated** (CONTRACT-1 / PERF-1): `duration_ms`/`*_micros` are recorded, never asserted-as-failure; no hard SLO.
- **AC-7 is deploy-time**, not tier-U (BR-OBS-6). **tier-U stays offline** — no live sink present; **31 skips + 5 Docker errors
  unchanged**.
- **No new dependency** (`langfuse` + `prometheus-client` floored + installed); `requirements.txt` NOT edited.
- Reference boundaries: `secrets-config` (values + `.env` governance), `deploy-config` (pipeline + env wiring + the mount/scrape),
  the closed composition root (live sink construction/attachment), `memo-agent-core` (the frozen orchestrator) — **named as
  dependencies, not authored here**.
- **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit
  decomposition unchanged**. Settled non-edits stay closed: WIRE-1 · `outlier-model` (U18) · `ui-outlier-view` (U20) ·
  `memo-extensions` (U19) · the 17 frozen P1 units.

---

## 6. Next step (STOP here)
Fill the nine `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check (grounded in
the frozen orchestrator's actual `run()`/checkpointer surface + the frozen `Settings` model + the `.env.example` reserved
shapes; adding a clarification fold only if a genuine gap surfaces), then generate the two `observability` Infrastructure Design
artifacts (with validated Mermaid + text alternatives) and present the standardized completion + 2-option message
(1. Request Changes / 2. Continue → **Code Generation**). **No Infrastructure-Design artifacts or code are generated until the
answers are in and checked.**
