# NFR Requirements — Plan (Part 1) — `observability` (U21, EPIC-6, **Phase 2**)

**Stage**: BUILD → per-unit loop → **NFR Requirements Part 1 (Plan)** · **Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Depth**: **lighter** (consistent with the FD decision; comprehensive reserved for Infrastructure Design, assessed when reached — **not** pre-committed here) · **Date**: 2026-07-18
**Built ON** the **frozen FD** — **BR-OBS-1..7**; the two-sub-component module inventory (**T** trace-side · **M** metric-side); the grounded **checkpointer/tool-step** boundary (U4's real 4-node graph `draft`/`validate`/`finalize`/`flag`); the **~5 metric** definitions with their sources; the **demographic-free-by-construction** discipline; **FD-OBS-Fold-1..3** — **re-opening none.**

**Status**: **PART 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** **THREE `[Answer]` tags (§4) are BLANK.** On the filled answers I run the mandatory ambiguity-check (surface-and-stop on any genuine gap, no improvising), then Part 2 (`nfr-requirements.md` + `tech-stack-decisions.md`) **on the explicit go**. **NO NFR artifact; no code; `backend/observability/` NOT created.** NFR Requirements is the **2nd of U21's 5 stages**; U21 is the **4th of 6 Phase-2 units**.

---

## 1. Tier convention (inherited verbatim from every prior backend unit — verified, not assumed)
**tier-U** = fast, deterministic, in CI — **no live network, no key, no Docker, no live Langfuse/Prometheus**. Every sink is an **injected Protocol with an offline recording fake**; every provider client / MCP transport analog is a double. **Every structural scan carries a mandatory detector self-test** (non-vacuous — the CG-NFR-OUT-Fold-3 convention). Latency/timing is **observed, never gated** (the frozen *"observed, not gated"* posture). **tier-B is N/A to U21** (it touches no corpus) and **NOT authorized**. Keys are `secrets-config`'s (SEC-3) — none read at tier-U.

---

## 2. §2.5 draft target map — every BR-OBS-1..7 mapped, NO ORPHAN (+ the metric-derivation split)

| BR rule | → Target | Tier / Rigor |
|---|---|---|
| **BR-OBS-1** (no frozen unit edited) | **NFR-OBS-NOEDIT-1** *(LOAD-BEARING)* | structural / **full (highest)** |
| **BR-OBS-2** (100%-step coverage, grounded node list) | **NFR-OBS-TRACE-1** *(LOAD-BEARING)* | component (teeth) + structural / **full (highest)** |
| BR-OBS-3 (two separate planes) | **NFR-OBS-SEP-1** | component (teeth) + structural / full |
| BR-OBS-4 (demographic-free verified) | **NFR-OBS-DEMOFREE-1** | structural + detector self-test / full |
| BR-OBS-5 (consume by shape, import nothing) | **NFR-OBS-SHAPE-1** | structural / full |
| *(the 3 emitter-sourced metrics)* | **NFR-OBS-METRIC-1** | component (teeth) / full |
| *(the 2 span-API-boundary metrics)* | **NFR-OBS-STEPMETRIC-1** | component (teeth) / full |
| BR-OBS-6 (tier-U schema/interface only) | **NFR-OBS-TIERU-1** | governance + structural / full |
| BR-OBS-7 (no domain contract; observed-never-gated) | **NFR-OBS-CONTRACT-1** | structural / full |
| *(soft perf)* | **NFR-OBS-PERF-1** | observed / soft |
| *(governance)* | **NFR-OBS-SEC-1** | N/A (governance) |

### 2.1 The two LOAD-BEARING targets (full-highest)

**NFR-OBS-NOEDIT-1 — U21 edits no frozen unit (BR-OBS-1).**
- **Assertion**: U21's production defines sinks/schemas + consumes; composition wires. **No frozen unit source is imported for mutation or edited.**
- **Acceptance**: **(a)** a **structural scan** proves no U21 production module writes/monkeypatches any frozen unit's module (no assignment into `memo_agent_core.*`/`outlier_model.*`/`memo_extensions.*`/`intake.*`/`rules_engine.*`/`audit_store.*` namespaces; no import of a frozen unit for the purpose of mutating it) **+ detector self-test** (a synthetic `memo_agent_core.provider.X = ...` is flagged). **(b)** the trace callback + span API + the two sinks are **injected**, exercised against **offline fakes** — no attach to a real checkpointer at tier-U. **(c)** **no frozen file's mtime/content changes** as a result of running U21's suite (behavioral: the run mutates nothing on disk).

**NFR-OBS-TRACE-1 — 100%-step trace coverage, grounded in U4's REAL node list (BR-OBS-2 / Fold-1).**
- **Assertion**: every **checkpointer node** yields exactly **one span**; the coverage proof uses the **actual** frozen node sequence, not an invented one; non-graph tool steps are traced via the **span API**.
- **Acceptance**: **(a) recording-fake teeth over BOTH real graph paths** — the **finalize path** `draft→validate→finalize` and the **retry-then-flag path** `draft→validate→draft→…→validate→flag` (up to `MEMO_CITATION_RETRY_CAP`) — each yields **exactly one span per node execution** (span count == node-execution count; **no node missed, none double-counted**); the fake sequence is **traced back to `memo_agent_core/orchestrator.py`'s actual node list** `{draft, validate, finalize, flag}` (a test constant mirrors the frozen node names **by value**, not an invented set — see **Q1**). **(b)** the **span API** wraps a **fake non-graph tool step** and records a span (the mechanism U18 scoring / U19 routing-MCP-provider are traced by, at composition). **(c)** the span schema is **demographic-free** (fed into DEMOFREE-1). **(d)** system-wide live 100% is **AC-7's deploy-time audit — explicitly NOT a tier-U assertion** (recorded, not tested here).

### 2.2 The other targets

**NFR-OBS-SEP-1 — traces and metrics are two separate planes (BR-OBS-3 / Fold-2).** A single `MemoTelemetryEvent` **value** produces **exactly one span** in the trace plane **and** **one counter contribution** (*decisions by recommendation type*) in the metric plane, from the **same** underlying event, with **neither mechanism importing the other** (structural: the trace module and the metric module have no cross-import). **Q3** decides the fixture discipline.

**NFR-OBS-DEMOFREE-1 — demographic-free verified, not trusted (BR-OBS-4 / Fold-3).** **(a) detector self-test**: a synthetic event carrying a **forbidden attribute** (free-text / demographic / `original_span`-style) is fed to a sink/derivation and asserted **never read or propagated** — it reaches **no** span attribute and **no** metric label. **(b) structural scan**: no U21 sink/derivation reads a **non-allowlisted** attribute name (+ the scan flags a synthetic violation, so it cannot pass vacuously).

**NFR-OBS-SHAPE-1 — consume by shape, import nothing (BR-OBS-5 / Q5-A).** **structural scan**: no U21 production module imports any frozen **event type** (`MemoTelemetryEvent` or the rules/audit/intake events) — the metric side adds **no** new code edge beyond the three declared trace-step edges; **fake events shaped BY VALUE** drive **every** derivation (+ detector self-test that a synthetic `from backend.memo_agent_core.telemetry import MemoTelemetryEvent` in production would be flagged).

**NFR-OBS-METRIC-1 — the 3 emitter-sourced metrics derive correctly.** teeth: *decisions by recommendation type* (counter, from `recommendation` enum value) · *decision latency* (histogram, from `duration_ms`) · *rule-evaluation duration* (histogram, from `rules_engine` `evaluate_micros`) — each derives the right contribution from a **fake emitted event**; labels are **enum values / ids only**.

**NFR-OBS-STEPMETRIC-1 — the 2 span-API-boundary metrics derive from fake STEP OUTCOMES (distinct path).** teeth: *LLM-call errors* (counter, from a **fake provider-call-error step outcome**) · *outlier-flag rate* (counter/gauge, from a **fake `OutlierResult`-shaped `is_outlier` step outcome**) — derived at the **span-API boundary**, a **structurally different derivation path** from the emitter-event metrics (**Q2** decides the fixture separation). Their real capture is **composition-wired**; tier-U tests the derivation against fakes.

**NFR-OBS-TIERU-1 — tier-U is schema/interface correctness only (BR-OBS-6 / Q3-A).** **no** U21 test opens a socket, reads a key, or requires Docker; the sinks are injected fakes; the backend suite's **31 skips + 5 pre-existing Docker errors stay UNCHANGED** (U21 adds none). Live end-to-end trace capture is deferred to composition Scope B/C.

**NFR-OBS-CONTRACT-1 — no domain contract; observed-never-gated (BR-OBS-7).** **structural scan**: no U21 module declares or emits a `Recommendation`/verdict/confidence-as-output field (+ detector self-test); **no** U21 test asserts a **latency/timing FAILURE** (`duration_ms`/`*_micros` are observed only — there is no timing-gating assertion anywhere).

**NFR-OBS-PERF-1** — soft/observed, **no hard SLO** (the uniform prior-unit posture); nothing to time at tier-U (all sinks are fakes).
**NFR-OBS-SEC-1** — the Security-Guardrails governance table (no runtime test); enforced by review + the scans above.

---

## 3. HOLDS (binding on Part 2)
- **No frozen unit edited** — `memo-agent-core` (U4), the four `telemetry.py` emitters, U4's checkpointer, `outlier-model` (U18), `memo-extensions` (U19), `ui-outlier-view` (U20), the 17 frozen P1 units are **read-only references**; U21 imports **no** frozen event type (Q5-A).
- **WIRE-1 · the closed composition root untouched** (the live wiring is *named*, not performed); **tier-B NOT authorized** (and N/A); the **`audit_store` Docker-guard gap untouched** — the **31 skips + 5 Docker errors stay unchanged**.
- **No live network/key/Docker/Langfuse/Prometheus** at tier-U; injected fakes only.
- **Demographic-free by construction is inherited and VERIFIED** (not merely trusted); **no new domain contract; no recommendation path; observed-never-gated.**
- **No other unit started**; the **23-unit decomposition unchanged.** **No NFR artifact, no code, no `backend/observability/`** until the three answers are filled, the ambiguity-check runs, and Part 2 is explicitly authorized.

---

## 4. Clarifying questions (fill each `[Answer]:`; full text; lettered options) — **do not improvise; flag-and-stop**

### Q1 — Does the recording-fake cover BOTH real graph paths as two separate teeth, or one parameterized test?
The FD grounds the coverage proof in U4's real node list. The frozen graph has **two** real terminal paths: **finalize** (`draft→validate→finalize`) and **retry-then-flag** (`draft→validate→draft→…→validate→flag`, up to `MEMO_CITATION_RETRY_CAP`). Their span **sequences differ** (the retry path re-enters `draft`/`validate`, terminating at `flag` not `finalize`).

- **A. One PARAMETRIZED test over BOTH real paths** — a single test body, two cases (finalize-path expected span sequence; retry-then-flag expected span sequence), each asserting **one span per node execution** against the **actual** frozen node names. **DRY**, and **both** real paths are explicitly exercised (neither branch is skipped). The parameter set is the two real terminal paths, traced to `orchestrator.py`. *(Recommended — covers both grounded paths without duplication; the expected-sequence-per-path is the whole point of the coverage proof, and one parametrized body keeps them side by side.)*
- **B. Two SEPARATE named teeth** (`test_trace_covers_finalize_path`, `test_trace_covers_retry_then_flag_path`) — maximally explicit/readable, each path its own test; slightly more duplication of the span-count assertion.
- **C. Only the finalize path** — *(rejected — misses the retry/flag branch, so the 100%-coverage claim would be unproven for the graph's other real terminal; a genuine coverage hole.)*

`[Answer]:` A

### Q2 — Do the span-API-boundary metrics need their own dedicated fake-step-outcome fixtures, distinct from the emitter-event fixtures?
Three metrics derive from **emitted allowlist events** (`MemoTelemetryEvent`-shaped); two (*LLM-call errors*, *outlier-flag rate*) derive from **step outcomes at the span-API boundary** (a provider-call error; an `OutlierResult`-shaped `is_outlier`). These are **structurally different derivation paths**.

- **A. Yes — dedicated fake-step-outcome fixtures, distinct from the emitter-event fixtures.** A `fake_provider_error_outcome` and a `fake_outlier_step_outcome` (an `is_outlier` value shaped by value, no `outlier_model` import) drive STEPMETRIC-1; the `MemoTelemetryEvent`-shaped fakes drive METRIC-1. Keeping them distinct makes the **two derivation paths honest** and prevents a metric from silently reading the wrong source shape. *(Recommended — the two paths ARE structurally different [emitted event vs step outcome]; conflating their fixtures would blur exactly the distinction FD-OBS-Fold-1/-3 drew, and would risk a step-metric passing off an emitter-event shape.)*
- **B. One shared fixture family** shaped to cover both. Fewer fixtures, but couples the emitter-event derivation and the step-outcome derivation to one shape and weakens the "distinct path" proof.
- **C. Other (describe).**

`[Answer]:` A

### Q3 — BR-OBS-3's "single event, two plane contributions": shared test infrastructure, or two independent assertions from the same input value?
NFR-OBS-SEP-1 must prove one `MemoTelemetryEvent` yields one span **and** one metric contribution — **without** the two planes coupling (they must not import each other, Q2-A).

- **A. Two independent assertions driven from the SAME input VALUE — no shared test *infrastructure*.** One assertion feeds the event value to the trace plane and asserts exactly one span; a second feeds the **same value** to the metric plane and asserts exactly one counter contribution. They **share the input value** (proving "one event → both planes") but **share no mechanism** — which is the point: forcing shared *infrastructure* would itself couple the two deliberately-separated planes. A structural check additionally asserts the trace and metric modules **do not import each other**. *(Recommended — a shared input VALUE proves the "single event, two planes" claim; a shared MECHANISM would contradict BR-OBS-3's separation. Two independent assertions from one value is both sufficient and truer to the design.)*
- **B. A shared fixture/harness** that runs one event through a combined path and checks both outputs. More "end-to-end", but introduces a shared mechanism spanning both planes — the exact coupling BR-OBS-3 forbids — and would need care not to become a de-facto unified bus (Q2-B, rejected).
- **C. Other (describe).**

`[Answer]:` A

---

## 4.5 MANDATORY AMBIGUITY-CHECK — RUN 2026-07-18 against Q1–Q3 (all A) + the frozen FD → **CLEAN (3 folds; no surface-and-stop)**

Checked against **BR-OBS-1..7**, **FD-OBS-Fold-1..3**, U4's frozen `orchestrator.py` **retry logic** (`_route_after_validate`) + **`MEMO_CITATION_RETRY_CAP = 2`** (verified on disk), and the U19 `OutlierSignal` interop precedent. **Each of the user's three flagged checks resolves against a frozen fact; none improvised.**

### NFR-OBS-Req-Fold-1 — [CHECK (i)] the retry-then-flag span sequence is CAP-GROUNDED; the coverage invariant is per-EXECUTION (repeats included)
U4's frozen router: `draft` increments `attempts`; on invalid citation, `if attempts < MEMO_CITATION_RETRY_CAP → "draft"` (retry) else `"flag"`. With the frozen **`MEMO_CITATION_RETRY_CAP = 2`**, the retry-then-flag path executes **`draft → validate → draft → validate → flag`** = **2 `draft` + 2 `validate` + 1 `flag` = 5 node executions**. So **reaching the cap matters** — the `flag` terminal is only produced at `attempts == CAP`. The coverage invariant is therefore **one span per node EXECUTION** (not per unique node): `draft`/`validate` legitimately appear **twice** and each execution gets its own span (a retry IS a distinct traced step). TRACE-1(a) is refined: the retry-then-flag fixture models **exactly `MEMO_CITATION_RETRY_CAP` draft/validate cycles then flag** (the frozen value, **referenced not invented** — import-vs-mirror is a Code-Gen realization), and the teeth assert **span count == total node executions** (5 for the retry path; 3 for the finalize path), **no execution missed, none double-counted**. The Q1-A parametrized test's two cases carry these two grounded expected sequences. **Grounded in the frozen retry logic + constant; not a gap.**

### NFR-OBS-Req-Fold-2 — [CHECK (ii)] the outlier step fixture uses `is_outlier` BY VALUE; NO Protocol interop-proof is warranted (U21 has no Protocol contract with U18)
The **distinction is real and material**: `memo-extensions` (U19) defined the **`OutlierSignal` Protocol** that a U18 `OutlierResult` had to satisfy → it needed the interop-by-value proof (`isinstance` against the `@runtime_checkable` Protocol). **U21 defines NO such Protocol** — the *outlier-flag rate* metric derives from a **step outcome at the span-API boundary** (a value composition hands the span), reading a single boolean field. So a **simpler shaped fake suffices** — but **grounded in U18's REAL field name `is_outlier`, mirrored BY VALUE (no `outlier_model` import)**, so the metric reads a field U18 actually has, not an invented one. STEPMETRIC-1's `fake_outlier_step_outcome` therefore exposes `is_outlier` by value; a full Protocol/`isinstance` proof would be over-engineering for a unit that declares no such contract. **Consistent with Q5-A (consume by shape, import nothing); not a gap.**

### NFR-OBS-Req-Fold-3 — [CHECK (iii)] the no-cross-import check forbids trace↔metric ONLY; a shared plane-NEUTRAL allowlist module both planes import is PERMITTED (and is where the demographic-free discipline lives)
BR-OBS-3's separation forbids the **trace module ↔ metric module** importing **each other** (plane-to-plane coupling). It does **not** forbid **both** importing a **shared, plane-neutral utility** — that is not a cross-import. The **demographic-free / allowlist discipline (DEMOFREE-1)** is needed identically by both planes, so it **should live in a shared, non-plane-specific module** (e.g., an `allowlist`/schema-base module) that **both** import — **DRY**, and it keeps the guarantee single-sourced. SEP-1's structural check is therefore scoped **semantically** (mirroring the memo-extensions MCPRO-1 *semantic-not-word-match* precedent): it flags a **`trace_*` ↔ `metrics_*`/`*_sink` plane-to-plane import**, and **permits** both planes importing the shared plane-neutral module. This **adds one shared module** to the open layout (Q4-A) — recorded for NFR Design / Code-Gen. **Not a forbidden cross-import; not a gap.**

**Verdict: CLEAN — no genuine gap requires a decision.** All three checks resolve against frozen facts (the CAP-grounded retry sequence + per-execution invariant; the no-Protocol distinction from U19; the plane-neutral shared-utility scoping). → **Part 2 authorized.**

---

## 5. Gate
- [x] **(1)** **Q1–Q3 answered — all A**; full question text + answers embedded (§4) per the standing convention.
- [x] **(2)** Mandatory **ambiguity-check RUN** (§4.5) → **CLEAN** (3 folds, no surface-and-stop) — the three user-flagged checks resolved against frozen facts (the CAP-grounded retry sequence + per-execution invariant; the no-Protocol distinction from U19; the plane-neutral shared-utility scoping).
- [x] **(3)** **Part 2 GENERATED** — `guide-docs/build/observability/nfr-requirements/`: `nfr-requirements.md` (**eleven `NFR-OBS-*`**; NOEDIT-1 + TRACE-1 the load-bearing pair; traceability, no orphan; Security-Guardrails table) + `tech-stack-decisions.md` (**OBS-D1..D9**; **no new dependency** — `langfuse`/`prometheus-client` already floored+installed; **`OBS-SINK-DEFERRED`** = the live-wiring deferral, a NON-dependency register item).
- [ ] **(4)** **NFR Requirements 2-option completion gate — AWAITING USER.** (1. Request Changes / 2. Continue to Next Stage → **NFR Design**.)

**STOPPED at the NFR Requirements 2-option completion gate.** **NO code; NO `backend/observability/`.** NFR Design does **not** begin until the gate is answered. WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units — **UNTOUCHED**; the 31 skips + 5 Docker errors unchanged; tier-B NOT authorized (N/A); the `audit_store` Docker-guard gap untouched; no other unit started; the 23-unit decomposition unchanged.
