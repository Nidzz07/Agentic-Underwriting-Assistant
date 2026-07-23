# Tech-Stack Decisions — `observability` (U21, EPIC-6, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Depth**: lighter · **Date**: 2026-07-18.
**Built ON** the frozen FD + the eleven `NFR-OBS-*` targets — re-opening none. Answers **Q1–Q3 (all A)** + folds **NFR-OBS-Req-Fold-1..3**.

> **HEADLINE: NO NEW DEPENDENCY — and, unlike memo-extensions, no dependency *gap* either.** `langfuse` and `prometheus-client` are **already floored AND installed** (verified this session). The only thing deferred is the **live sink WIRING** — a composition/deploy-config concern, **not** a missing library.

---

## 1. Dependency verification (on disk, not assumed)

| Library | `requirements.txt` | Installed | Role |
|---|---|---|---|
| `langfuse` | **`>=2.0.0` (floored)** | **INSTALLED** | the deploy-time **trace-callback adapter** target (the real Langfuse client the `langfuse_sink` binds at composition) |
| `prometheus-client` | **`>=0.21.0` (floored)** | **INSTALLED** | the deploy-time **metric-exporter** target (`/metrics` registry the `prometheus_sink` binds at composition) |
| pytest / hypothesis | floored + installed | INSTALLED | tier-U runner (the sibling-unit convention) |

**`requirements.txt` is NOT edited.** U21 adds no library.

## 2. Decisions (OBS-D1..OBS-D9)

- **OBS-D1 — tier-U runner**: `pytest` (+ `Hypothesis` where a universal-quantifier property earns it — e.g. DEMOFREE-1 over generated forbidden attributes; TRACE-1 span-count over generated fake sequences). No new dependency. *(Matches every prior backend unit.)*
- **OBS-D2 — sinks are INJECTED Protocols with OFFLINE recording fakes**: the Langfuse trace callback + span API and the Prometheus exporter are **injected seams**; tier-U drives **recording fakes** (no network, no key, no live server). Mirrors U4's `LLMClient` / the U19 injected-double substrate.
- **OBS-D3 — the metric registry is an in-memory structure at tier-U**: derivations + registry are **pure Python** (tested against fake events/step-outcomes); the **`prometheus-client` exporter is the deploy-time adapter** behind the injected sink Protocol. So `prometheus-client` is **not exercised at tier-U** and needs no test double beyond the injected fake.
- **OBS-D4 — the Langfuse SDK is the deploy-time adapter**: `langfuse` sits behind the injected trace-sink Protocol; tier-U uses the recording fake. The SDK is **not imported into U21's tier-U test path**.
- **OBS-D5 — consume by shape, import no frozen event type** (Q5-A / SHAPE-1): U21 production imports **no** `MemoTelemetryEvent` / rules / audit / intake event type; derivations read allowlist fields **by value**. U21's `backend.*` production imports stay **within its three declared trace-step edges** and do **not** widen to `rules-engine`/`audit-store` for the metric side.
- **OBS-D6 — the outlier step fixture uses `is_outlier` BY VALUE** (Req-Fold-2): no `outlier_model` import; no Protocol/`isinstance` proof (U21 has no `OutlierSignal`-style contract — the distinction from U19 is deliberate).
- **OBS-D7 — a SHARED plane-neutral allowlist module** (Req-Fold-3): the demographic-free/allowlist discipline is **single-sourced** in a plane-neutral module that **both** the trace and metric planes import; the SEP-1 no-cross-import scan forbids **trace↔metric** coupling only and **permits** this shared import.
- **OBS-D8 — observed-never-gated** (CONTRACT-1): `duration_ms`/`*_micros` are recorded, never asserted-as-failure; no hard SLO (NFR-OBS-PERF-1).
- **OBS-D9 — module layout OPEN** (Q4-A): sized to the two sub-concerns + the shared allowlist module (Req-Fold-3); no frozen file-count constraint. Exact module names finalized at NFR Design / Code-Gen.

## 3. `OBS-SINK-DEFERRED` — the live wiring deferral (registered, NON-dependency)

**Status: OPEN**, deferred to **composition / deploy-config (U23)** + **Infrastructure Design (comprehensive)**. **This is a WIRING deferral, not a dependency gap** (contrast `MCP-TRANSPORT-DEFERRED`, which flagged a *missing* library — here both SDKs are floored+installed).

- **DELIVERED (U21, tier-U)**: the trace-callback + span API + the two sink **Protocols** + the metric registry/derivations + the trace/metric **schemas** + the shared allowlist discipline — all proven against offline fakes.
- **NOT delivered (deferred)**: the **live binding** — plugging the real `langfuse` callback into U4's frozen graph checkpointer, mounting the `prometheus-client` `/metrics` endpoint + scrape, the one **Grafana dashboard** topology, keys via `secrets-config`, and **AC-7's deploy-time 100%-trace audit** (the composition-root parallel, Q1-A).
- **⚠️ NON-BLOCKING**: no U21 tier-U invariant depends on the live binding (TRACE-1/SEP-1/METRIC-1/STEPMETRIC-1 are each fully verified with **no** live sink present). *"Observability delivered"* is **not** to be read as fully wired at this stage — hence the named register item.

## 4. Held
- **No new dependency**; `requirements.txt` NOT edited. **No frozen unit edited.** WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units — **UNTOUCHED**. **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged). No other unit started; the 23-unit decomposition unchanged.
