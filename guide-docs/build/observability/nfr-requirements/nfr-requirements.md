# NFR Requirements — `observability` (U21, EPIC-6, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Depth**: lighter · **Date**: 2026-07-18 · Story **US-PLAT-9** · NFR-OBS-1/2, AC-7.
**Built ON** the frozen FD (**BR-OBS-1..7**; the two-sub-component inventory; the grounded checkpointer/tool-step boundary — U4's real 4-node graph; the ~5 metric definitions + sources; the demographic-free-by-construction discipline; **FD-OBS-Fold-1..3**) — **re-opening none.** Answers **Q1–Q3 (all A)** + the NFR-Req folds **NFR-OBS-Req-Fold-1..3** (plan §4.5).

**Tiers**: **tier-U** = fast, deterministic, CI — **no live network/key/Docker/Langfuse/Prometheus**; every sink is an **injected Protocol with an offline recording fake**; every structural scan carries a **mandatory detector self-test**; latency/timing is **observed, never gated**; **tier-B N/A + NOT authorized**. Keys are `secrets-config`'s (SEC-3) — none read at tier-U.

> **No new dependency** (`tech-stack-decisions.md`): `langfuse` and `prometheus-client` are **already floored AND installed** — unlike the memo-extensions MCP gap, U21 introduces none. The **live sink WIRING** (real callback→checkpointer binding, `/metrics` mount, Grafana dashboard) is **deferred to composition/deploy-config** — a *wiring* deferral, **not** a dependency gap.

---

## 1. Finalized `NFR-OBS-*` targets (pass/fail; acceptance; tier; rigor)

### FULL RIGOR — the two LOAD-BEARING targets

#### NFR-OBS-NOEDIT-1 — U21 edits no frozen unit (BR-OBS-1) — **LOAD-BEARING**
- **Assertion**: U21 **defines** sinks/schemas + **consumes**; composition **wires**. **No frozen unit source is imported for mutation or edited.**
- **Acceptance**: **(a)** a **structural (AST) scan** — no U21 production module performs an **assignment/monkeypatch into** a frozen namespace (`memo_agent_core.*` / `outlier_model.*` / `memo_extensions.*` / `intake.*` / `rules_engine.*` / `audit_store.*`); **+ detector self-test** (a synthetic `memo_agent_core.provider.X = ...` **must** be flagged). **(b)** the trace callback + span API + both sinks are **injected**, exercised against **offline fakes** — no attach to a real checkpointer at tier-U. **(c) behavioral** — running U21's suite **mutates no frozen file** (no on-disk change).
- **Tier**: structural. **Rigor**: **full (highest)**.

#### NFR-OBS-TRACE-1 — 100%-step trace coverage, grounded in U4's REAL node list (BR-OBS-2 / Fold-1 / Req-Fold-1) — **LOAD-BEARING**
- **Assertion**: every **checkpointer node execution** yields **exactly one span**; the proof uses the **actual** frozen node sequence; non-graph tool steps are traced via the **span API**.
- **Acceptance**: **(a) recording-fake teeth over BOTH real graph paths (Q1-A, one parametrized test, two cases)** — the **finalize path** `draft→validate→finalize` (**3** executions) **and** the **retry-then-flag path** `draft→validate→draft→validate→flag` (**5** executions at the frozen **`MEMO_CITATION_RETRY_CAP = 2`** — Req-Fold-1) — each asserts **span count == total node executions**, **one span per EXECUTION** (`draft`/`validate` appear **twice** on the retry path, each with its own span), **no execution missed, none double-counted**. The expected sequences mirror `orchestrator.py`'s **actual** node names `{draft, validate, finalize, flag}` **by value** (not invented); the retry length is the **frozen cap** (referenced, not invented). **(b)** the **span API** wraps a **fake non-graph tool step** and records a span (the mechanism U18 scoring / U19 routing·MCP·provider are traced by, at composition). **(c)** the span schema is **demographic-free** (→ DEMOFREE-1). **(d)** system-wide live 100% is **AC-7's deploy-time Langfuse audit — explicitly NOT a tier-U assertion** (recorded, not tested here).
- **Tier**: component (teeth) + structural. **Rigor**: **full (highest)**.

### FULL RIGOR

#### NFR-OBS-SEP-1 — traces and metrics are two separate planes (BR-OBS-3 / Fold-2 / Q3-A / Req-Fold-3)
- **Acceptance**: **(a)** a single `MemoTelemetryEvent` **value** → **exactly one span** (trace plane) **and** **one counter contribution** (*decisions by recommendation type*, metric plane), asserted by **two independent assertions from the SAME input VALUE — no shared test mechanism** (Q3-A). **(b) structural** — the trace module and the metric module **do not import each other** (**semantic** scan: flags a `trace_* ↔ metrics_*/*_sink` plane-to-plane import; **permits** both importing the **shared plane-neutral allowlist module** — Req-Fold-3) + detector self-test.
- **Tier**: component (teeth) + structural. **Rigor**: full.

#### NFR-OBS-DEMOFREE-1 — demographic-free VERIFIED, not trusted (BR-OBS-4 / Fold-3)
- **Acceptance**: **(a) detector self-test** — a synthetic event carrying a **forbidden attribute** (free-text / demographic / `original_span`-style) fed to a sink/derivation is **never read or propagated** (reaches **no** span attribute, **no** metric label). **(b) structural scan** — no U21 sink/derivation reads a **non-allowlisted** attribute name (+ flags a synthetic violation ⇒ non-vacuous). The discipline lives in the **shared plane-neutral allowlist module** (Req-Fold-3), single-sourced.
- **Tier**: structural + detector self-test. **Rigor**: full.

#### NFR-OBS-SHAPE-1 — consume by shape, import nothing (BR-OBS-5 / Q5-A)
- **Acceptance**: **structural scan** — no U21 production module imports any frozen **event type** (`MemoTelemetryEvent` or the rules/audit/intake events); the metric side adds **no** new code edge beyond the three declared trace-step edges; **fake events shaped BY VALUE** drive **every** derivation (+ detector self-test that a synthetic `from backend.memo_agent_core.telemetry import MemoTelemetryEvent` in production is flagged).
- **Tier**: structural. **Rigor**: full.

#### NFR-OBS-METRIC-1 — the 3 emitter-sourced metrics derive correctly
- **Acceptance**: teeth over **fake emitted events** — *decisions by recommendation type* (counter ← `recommendation` enum value) · *decision latency* (histogram ← `duration_ms`) · *rule-evaluation duration* (histogram ← `rules_engine` `evaluate_micros`); each derives the right contribution; **labels are enum values / ids only** (→ DEMOFREE-1).
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-OBS-STEPMETRIC-1 — the 2 span-API-boundary metrics derive from fake STEP OUTCOMES (distinct path) (Q2-A / Req-Fold-2)
- **Acceptance**: teeth over **dedicated fake-step-outcome fixtures, distinct from the emitter-event fixtures** (Q2-A) — *LLM-call errors* (counter ← a `fake_provider_error_outcome`) · *outlier-flag rate* (counter/gauge ← a `fake_outlier_step_outcome` exposing **`is_outlier` BY VALUE**, **no `outlier_model` import**, grounded in U18's real field name — Req-Fold-2). This is a **structurally different derivation path** from METRIC-1; the fixtures do not overlap, so a step-metric cannot silently read an emitter-event shape. Real capture is **composition-wired**.
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-OBS-TIERU-1 — tier-U is schema/interface correctness only (BR-OBS-6 / Q3-A of FD)
- **Acceptance**: **no** U21 test opens a socket, reads a key, or requires Docker; the sinks are injected fakes; the backend suite's **31 skips + 5 pre-existing Docker errors stay UNCHANGED** (U21 adds none). Live end-to-end trace capture is deferred to composition Scope B/C.
- **Tier**: governance + structural. **Rigor**: full.

#### NFR-OBS-CONTRACT-1 — no domain contract; observed-never-gated (BR-OBS-7)
- **Acceptance**: **structural scan** — no U21 module declares or emits a `Recommendation`/verdict/confidence-as-output field (+ detector self-test); **no** U21 test asserts a **latency/timing FAILURE** (`duration_ms`/`*_micros` observed only — no timing-gating assertion anywhere).
- **Tier**: structural. **Rigor**: full.

### SOFT / OBSERVED
#### NFR-OBS-PERF-1 — sink/derivation cost observed, non-gating
- **Assertion / Acceptance**: **no hard SLO** (the uniform prior-unit posture); nothing to time at tier-U (all sinks are fakes). Real per-sink cost → deploy-config / composition.
- **Tier**: observed / soft. **Rigor**: soft.

### GOVERNANCE
#### NFR-OBS-SEC-1 — scoped exclusions *(not a runtime test)*
- **Statement**: this set tests **only** `observability`'s behavior. It does **not** test other units, the WIRE-1 routes, the live Langfuse/Prometheus binding (deferred), or the tier-B corpus (**N/A**). It **consumes** frozen streams **by shape** and introduces **no write path**. Enforced by review + the structural scans above.
- **Tier**: N/A (governance).

---

## 2. Traceability (target → BR-OBS / requirement → tier → rigor)

| Target | BR-OBS / requirement | Tier | Rigor |
|---|---|---|---|
| **NFR-OBS-NOEDIT-1** | BR-OBS-1 / the reference-not-own hold | structural | **full (highest)** |
| **NFR-OBS-TRACE-1** | BR-OBS-2 / NFR-OBS-1 / AC-7 / Fold-1 | component + structural | **full (highest)** |
| NFR-OBS-SEP-1 | BR-OBS-3 / Fold-2 | component + structural | full |
| NFR-OBS-DEMOFREE-1 | BR-OBS-4 / CON-BR1 / skill #6 / Fold-3 | structural + self-test | full |
| NFR-OBS-SHAPE-1 | BR-OBS-5 / `unit-of-work-dependency.md:50` | structural | full |
| NFR-OBS-METRIC-1 | NFR-OBS-2 (3 emitter-sourced) | component | full |
| NFR-OBS-STEPMETRIC-1 | NFR-OBS-2 (2 step-outcome) / Req-Fold-2 | component | full |
| NFR-OBS-TIERU-1 | BR-OBS-6 | governance + structural | full |
| NFR-OBS-CONTRACT-1 | BR-OBS-7 / skill #1 | structural | full |
| NFR-OBS-PERF-1 | (soft perf) | observed | soft |
| NFR-OBS-SEC-1 | governance | N/A | governance |

**No orphaned BR-OBS rule**: 1→NOEDIT-1 · 2→TRACE-1 · 3→SEP-1 · 4→DEMOFREE-1 · 5→SHAPE-1 · 6→TIERU-1 · 7→CONTRACT-1. The **~5 metrics** → METRIC-1 (×3) + STEPMETRIC-1 (×2). PERF-1 / SEC-1 cover cost + governance.
**Story coverage**: **US-PLAT-9** → TRACE-1 + SEP-1 + METRIC-1 + STEPMETRIC-1 (the observability capability) + NOEDIT-1/SHAPE-1/DEMOFREE-1/TIERU-1/CONTRACT-1 (the discipline).

---

## 3. Security-Guardrails extension — compliance (enabled extension)

`observability` **adds two observability sinks** (a trace exporter + a metric exporter) to a system that had emit-only seams — so the controls are assessed against **exactly** those additions.

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A** | U21 has no application-input surface; it consumes already-typed emitted events + graph steps. |
| Prompt-injection defense | **N/A** | U21 runs no LLM and builds no prompt. |
| Secrets management | **Compliant (referenced)** | Langfuse/Prometheus keys+endpoints come from **`secrets-config`** (SEC-3), never hardcoded; **no key at tier-U** (injected fakes). |
| Read-only / no write path | **Compliant** | U21 **persists nothing** and reaches no DB; it exports signals only. **No `DecisionCommitService` / write path.** |
| Audit logging | **N/A (producer, not persister)** | U21 IS the observer; it emits/exports, it does not persist a decision record. |
| Error hygiene (no secret/PII leak) | **Compliant (load-bearing)** | **DEMOFREE-1** — every sink is demographic-free by construction, **verified** (detector self-test); no secret present at tier-U to leak. |
| **Bias-free by design (CON-BR1)** | **Compliant (load-bearing)** | **DEMOFREE-1** — no trace attribute or metric label may carry prose/PII/demographic; the discipline is single-sourced in the shared allowlist module and verified. |
| Reproducibility (CON-DET-1) | **Compliant** | U21 **observes**, never affects an outcome (CONTRACT-1); its tier-U tests are deterministic (injected fakes, no wall-clock gating). |
| **Advisory-only (skill #1)** | **Compliant** | **CONTRACT-1** — U21 declares **no** recommendation/verdict; there is no path an outcome flows through. |
| Full explainability | **N/A** | U21 produces no recommendation; it makes the *system* observable, it does not itself explain a decision. |
| **Deliverable transparency** | **Compliant (registered)** | The **live sink wiring** is **openly deferred** to composition/deploy-config (the composition-root parallel, Q1-A) — named, not quietly assumed done. **Non-blocking**: no U21 tier-U invariant depends on it; **no new dependency** (both SDKs already floored). |

**No blocking finding.**

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-OBS-1..7 + the two sub-components + the grounded node list + the ~5 metrics) is the substrate.
- **Q1-A** — one **parametrized** trace-coverage test over **both** real graph paths; **Req-Fold-1** grounds the retry path at the frozen `MEMO_CITATION_RETRY_CAP = 2` with a **per-EXECUTION** span invariant.
- **Q2-A** — **dedicated** fake-step-outcome fixtures for the 2 span-API-boundary metrics; **Req-Fold-2**: the outlier fixture exposes `is_outlier` **by value** (no Protocol proof — U21 has no `OutlierSignal`-style contract with U18).
- **Q3-A** — SEP-1 proved by **two independent assertions from one input value**, no shared mechanism; **Req-Fold-3**: the no-cross-import scan forbids **trace↔metric** only and **permits** a **shared plane-neutral allowlist module** (where DEMOFREE-1 lives).
- **Deferred to NFR Design / Code-Gen**: the exact span/attribute serialization; the metric registry library binding (in-memory registry at tier-U; `prometheus-client` exporter is the deploy-time adapter); the recording-fake fixtures; the shared-allowlist module's exact surface.
- **Deferred to Infrastructure Design (comprehensive) / composition / deploy-config**: the **live** Langfuse callback→checkpointer binding, the `/metrics` mount + scrape, the one Grafana dashboard, keys via `secrets-config`, and **AC-7's deploy-time 100%-trace audit**.
- **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched**; the **31 skips + 5 Docker errors stay unchanged**.
