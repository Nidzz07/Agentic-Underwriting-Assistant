# NFR Design — Plan (Part 1) — `observability` (U21, EPIC-6, **Phase 2**)

**Stage**: BUILD → per-unit loop → **NFR Design Part 1 (Plan)** · **Unit**: U21 `observability` · EPIC-6 · **Phase 2** · **Depth**: **lighter** (consistent with FD/NFR-Req; comprehensive reserved for Infrastructure Design) · **Date**: 2026-07-18
**Built ON** the **frozen FD** (**BR-OBS-1..7**; the two-sub-component inventory **T**/**M**; the grounded checkpointer/tool-step boundary — U4's real 4-node graph; **FD-OBS-Fold-1..3**) **and** the **approved NFR Requirements** (**eleven `NFR-OBS-*`**; the load-bearing **NOEDIT-1**/**TRACE-1** pair; **`OBS-SINK-DEFERRED`**; **NFR-OBS-Req-Fold-1..3**) — **re-opening neither.**

**Status**: **PART 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** **THREE `[Answer]` tags (§5) are BLANK.** On the filled answers I run the mandatory ambiguity-check (surface-and-stop on any genuine gap, no improvising), then Part 2 (`nfr-design-patterns.md` + `logical-components.md`) **on the explicit go**. **NO NFR-Design artifact; no code; `backend/observability/` NOT created.** NFR Design is the **3rd of U21's 5 stages**.

**Backend Python unit** — "component relationship" = **module/class relationships + Python data flow** (the U18/U19 convention), not a JSX tree.

---

## 1. What this stage decides
**HOW** each `NFR-OBS-*` target is **structurally met** — the named **design patterns** + the **logical components** (module/class surfaces + **exact signatures**) that carry each guarantee, the **shared plane-neutral allowlist** structure (Req-Fold-3), the **reference-not-own** discipline (three distinct categories), and **component→target** coverage. It decides **no functional behavior** (frozen FD) and **no new target** (approved NFR Requirements). **No code.**

## 2. Draft pattern map — `P-OBS-1..11` (every one of the eleven targets covered)

| # | Pattern | Mechanism (by-construction where possible; honest test-only otherwise) | Target(s) | Tier / Rigor |
|---|---|---|---|---|
| **P-OBS-1** | **InjectedSinkAbstractionPattern** *(load-bearing)* | **By-construction + scan pairing**: every sink (trace callback, span API, metric exporter) is an **injected Protocol handed in at composition**, so U21 has **nothing to gain** by reaching into a frozen unit — editing one is **structurally unnecessary**, not merely forbidden. The `StructuralGuard` scan (no assignment into a frozen namespace + detector self-test) proves **nothing was touched**. *(the by-construction-plus-scan pairing used throughout this build)* | **NOEDIT-1** | structural / **full (highest)** |
| **P-OBS-2** | **DualCoverageTracePattern** *(load-bearing)* | **Two distinct, jointly-exhaustive mechanisms**: **(a)** the **checkpointer callback auto-traces graph nodes** — one span per node **execution**, by construction (the callback fires per checkpointer step) over U4's **real** node list `{draft, validate, finalize, flag}`, both real paths (finalize=3, retry-then-flag=5 at the frozen `MEMO_CITATION_RETRY_CAP=2` — Req-Fold-1); **(b)** the **span API wraps non-graph tool steps** (U18 scoring, U19 routing·MCP·provider) explicitly at composition. Union = *"100% of agent/tool steps"*; system-wide live 100% = **AC-7 deploy-time audit** (not tier-U). **Q3 decides** whether (a) and (b) emit through **one** shared span-sink interface or two. | **TRACE-1** | component (teeth) + structural / **full (highest)** |
| **P-OBS-3** | **TwoPlaneSeparationPattern** | The **trace module** and **metric module** **do not import each other** (semantic scan — the MCPRO-1 precedent). The **only** shared import is the **plane-neutral allowlist module** (Q1), which carries **no plane knowledge**, so it **cannot** become a coupling point. SEP-1's *single-value/two-planes* proof is two independent assertions from one value (Q3-A of NFR-Req). | **SEP-1** | component (teeth) + structural / full |
| **P-OBS-4** | **SingleSourcedAllowlistPattern** | The **shared plane-neutral allowlist module** is the **single source** of the demographic-free discipline; **both** planes project every attribute/label **through it**; a forbidden field is unrepresentable downstream. Detector self-test (a synthetic forbidden attribute never propagates) + scan. **Composes with SEP-1**: it is the one legitimate shared import (Q1 pins its shape). | **DEMOFREE-1** | structural + self-test / full |
| **P-OBS-5** | **ByShapeConsumptionPattern** | Emitted events are consumed **by shape through the allowlist module** — **no frozen event type imported** (SHAPE-1). **Even more minimal than U19's `OutlierSignal`**: since **no Protocol contract is warranted** (Req-Fold-2), the allowlist field-name set **is** the surface — **Q2 decides** whether any lightweight typed surface is declared at all. | **SHAPE-1** | structural / full |
| **P-OBS-6** | **EmitterSourcedDerivationPattern** | The **3** emitter-sourced metrics (recommendation-type counter · decision-latency histogram · rule-eval-duration histogram) derive from **fake emitted events**; labels are enum values/ids only (through P-OBS-4). | **METRIC-1** | component (teeth) / full |
| **P-OBS-7** | **StepOutcomeDerivationPattern** | The **2** span-API-boundary metrics (LLM-call errors · outlier-flag rate) derive from **dedicated fake step outcomes** (`is_outlier` **by value**, no `outlier_model` import — Req-Fold-2), a **structurally separate** path from P-OBS-6 (distinct fixtures, no overlap). | **STEPMETRIC-1** | component (teeth) / full |
| **P-OBS-8** | **InjectedFakeTierUPattern** | Every sink is an injected fake at tier-U — **no socket/key/Docker/live server**; the 31 skips + 5 Docker errors stay unchanged. | **TIERU-1** | governance + structural / full |
| **P-OBS-9** | **NoContractObservedNotGatedPattern** | **By-construction**: U21 declares **no** `Recommendation`/verdict (scan + self-test); `duration_ms`/`*_micros` are **observed, never gated** (no timing-failing assertion). | **CONTRACT-1**, **PERF-1** | structural / full · soft |
| **P-OBS-10** | **StructuralGuardPattern** *(mirrors U18/U19's substrate)* | One substrate of independent AST scans, **each with a mandatory detector self-test**: no-frozen-namespace-write (NOEDIT-1) · no-`trace↔metric`-cross-import (SEP-1, semantic) · no-non-allowlisted-attribute-read (DEMOFREE-1) · no-frozen-event-type-import (SHAPE-1) · no-`Recommendation`/verdict (CONTRACT-1). | the structural halves of NOEDIT/SEP/DEMOFREE/SHAPE/CONTRACT | structural / full |
| **P-OBS-11** | **ReferencedGovernancePattern** | **SEC-1** (the Security-Guardrails table — review + the P-OBS-10 scans) + **`OBS-SINK-DEFERRED`** (the live-wiring deferral recorded, **non-blocking, non-dependency**). Not over-specified. | **SEC-1** (+ OBS-SINK-DEFERRED) | referenced / governance |

**No orphan (11/11)**: NOEDIT→P1 · TRACE→P2 · SEP→P3 · DEMOFREE→P4 · SHAPE→P5 · METRIC→P6 · STEPMETRIC→P7 · TIERU→P8 · CONTRACT/PERF→P9 · (structural halves)→P10 · SEC→P11.

## 3. Draft logical components — `C-OBS-1..4`

| # | Component | Module(s) (proposed; layout OPEN per Q4-A of FD) | Responsibility / ownership | Signatures that carry the guarantee |
|---|---|---|---|---|
| **C-OBS-1** | **trace-side** | `trace_schema.py` + `langfuse_sink.py` | the demographic-free `TraceSpan` + the **span-sink Protocol** + the **checkpointer callback adapter** + the **span-API** context-manager (P-OBS-1/2) | `record_span(step_name: str, attributes: Mapping[str, ScalarValue]) -> None` (injected sink Protocol); `on_step(step_name, raw_attributes) -> None` (callback → projects via allowlist → `record_span`); `span(step_name, raw_attributes)` (context-manager, same path). **Q3 decides one shared sink vs two.** |
| **C-OBS-2** | **metric-side** | `metrics.py` + `prometheus_sink.py` | the ~5 `MetricDefinition`s + registry + the **two derivation paths** + the **exporter Protocol** (P-OBS-6/7) | `derive_from_event(fields: Mapping[str, object]) -> list[MetricContribution]`; `derive_from_step_outcome(outcome) -> list[MetricContribution]`; `export(contribution) -> None` (injected exporter Protocol; in-memory registry at tier-U) |
| **C-OBS-3** | **shared plane-neutral allowlist** (Req-Fold-3) | `allowlist.py` | the **single source** of the demographic-free projection; **no** plane-specific knowledge (P-OBS-4). **Importable by both planes without coupling.** **Q1 decides its shape.** | `project_allowlisted(fields: Mapping[str, object], allowed: frozenset[str]) -> dict[str, ScalarValue]` (pure; drops any non-allowlisted / non-scalar field) |
| **C-OBS-4** | **StructuralGuard substrate** *(test-only)* | `tests/` | the AST scans + mandatory detector self-tests (P-OBS-10); **not a runtime dependency** | the five scans of P-OBS-10 |

### 3.2 Reference-not-own — **three distinct categories, kept separate** (as instructed)

| Category | Members | Discipline |
|---|---|---|
| **1. Consumed BY SHAPE — frozen streams** | the **checkpointer node executions** (trace) · the **emitter allowlist events** `MemoTelemetryEvent`/rules/audit/intake (metric) · the **step outcomes** `is_outlier` etc. | **no import of a frozen event type** (SHAPE-1); read by shape through C-OBS-3; the interop fake is built **by value** (Req-Fold-2 — no Protocol) |
| **2. SHARED INTERNAL — U21-owned, plane-neutral** | **`allowlist.py`** (C-OBS-3) | the **only** module both planes import; **carries no plane knowledge**, so it is **not** a `trace↔metric` coupling (Req-Fold-3) |
| **3. DEFERRED to composition** | the real **`langfuse`** callback→checkpointer binding · the **`prometheus-client`** `/metrics` mount + scrape · the **Grafana** dashboard · keys via `secrets-config` · **AC-7** deploy-time audit | **`OBS-SINK-DEFERRED`** — the composition-root parallel (Q1-A of FD); **non-blocking, non-dependency** (both SDKs floored+installed) |

### 3.3 Component → target coverage (no orphan)

| Component | Targets met | Patterns |
|---|---|---|
| `trace-side` (C-OBS-1) | TRACE-1, (DEMOFREE-1 via C-OBS-3), NOEDIT-1 (injected) | P-OBS-1/2/4 |
| `metric-side` (C-OBS-2) | METRIC-1, STEPMETRIC-1, (DEMOFREE-1 via C-OBS-3), NOEDIT-1 (injected) | P-OBS-6/7/1/4 |
| `allowlist` (C-OBS-3) | DEMOFREE-1, SHAPE-1, SEP-1 (the plane-neutral shared import) | P-OBS-4/5/3 |
| `StructuralGuard` (C-OBS-4) | NOEDIT-1, SEP-1, DEMOFREE-1, SHAPE-1, CONTRACT-1 (structural halves) | P-OBS-10 |
| *(referenced/observed)* | TIERU-1, PERF-1, SEC-1 | P-OBS-8/9/11 |

### 3.4 Planned Mermaid (module-relationship; validated to the 7 rules; rectangle-only)
Both guarantees you asked to be **visible structural properties**: a **`frozen unit source`** node with a **blocked** edge from **both** planes (**no-frozen-edit**, P-OBS-1), and a **blocked** edge **between** the `trace side` and `metric side` nodes (**no-cross-import**, P-OBS-3) — while **both** connect to the shared `allowlist` node (the one legitimate shared import). Nodes: `STREAMS` · `TRACE` · `METRIC` · `ALLOW` · `GUARD` · `COMP` · `FROZEN`. All-alphanumeric IDs, quoted labels, **no hyphens/semicolons/colons/parentheses/special characters**, balanced fence, **rectangle-only** + text alternative.

---

## 4. HOLDS (binding on Part 2)
- **No frozen unit edited**; U21 imports **no** frozen event type (consume by shape). **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units UNTOUCHED.**
- **`OBS-SINK-DEFERRED` stays OPEN + non-blocking (non-dependency)**; **no new dependency**; **no live network/key/Docker** at tier-U; the **31 skips + 5 Docker errors stay unchanged**.
- **Demographic-free single-sourced + verified**; **no domain contract; observed-never-gated.** **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**.
- **Header comments document; they never enforce.** **No NFR-Design artifact, no code** until the three answers are filled, the ambiguity-check runs, and Part 2 is authorized.

## 5. Clarifying questions (fill each `[Answer]:`; full text; lettered options) — **do not improvise; flag-and-stop**

### Q1 — The shared plane-neutral allowlist module (Req-Fold-3): a PURE-FUNCTION utility, or a Protocol both planes implement?
It must be importable by both planes **without becoming a coupling point** (SEP-1). The question is its **shape**.

- **A. A PURE-FUNCTION utility with NO plane-specific knowledge** — e.g. `project_allowlisted(fields, allowed) -> dict[str, ScalarValue]`, a stateless projection that drops any non-allowlisted or non-scalar field. It knows **nothing** about spans or metrics; both planes call it and pass their own allowlist set. Being **pure and plane-agnostic**, it **cannot** carry trace→metric or metric→trace knowledge, so it is **structurally incapable** of coupling the planes. *(Recommended — the simplest thing that single-sources DEMOFREE-1 while being provably non-coupling; a pure function has no surface through which plane knowledge could leak; mirrors the project's pure-utility precedents.)*
- **B. A Protocol both planes implement independently** — each plane provides its own allowlist-conforming class. More "typed", but pushes the demographic-free logic **into** each plane (duplicated, not single-sourced — weakening DEMOFREE-1's single-source claim), and a shared Protocol can still accrete plane-specific expectations over time.
- **C. Other (describe).**

`[Answer]:` A

### Q2 — The by-shape consumption surface (SHAPE-1 / Req-Fold-2): a lightweight typed surface, or pure duck-typing through the allowlist utility?
Req-Fold-2 established U21 needs **no** `OutlierSignal`-style Protocol contract. The question is whether U21 declares **any** typed surface for the consumed events/outcomes.

- **A. Pure duck-typing THROUGH the allowlist utility — no per-event Protocol/TypedDict declared.** The **allowlist field-name set IS the surface**: derivations read only the names the allowlist utility (Q1) permits; there is **no** separate `MemoTelemetryEvent`-shaped Protocol/TypedDict in U21. Fakes are shaped **by value**. **Even more minimal than U19's `OutlierSignal`** (which existed because U19 had a real Protocol contract — U21 does not, Req-Fold-2). *(Recommended — the allowlist set already names the fields; a second typed surface would duplicate it and re-introduce a shape U21 was told it does not need; keeps SHAPE-1's "import nothing, consume by shape" cleanest.)*
- **B. A minimal `TypedDict`/`Protocol` per consumed shape** (a light `EmittedEventView` naming the allowlist fields) for readability. Slightly more self-documenting, but duplicates the allowlist field set and edges back toward the Protocol surface Req-Fold-2 said was unwarranted.
- **C. Other (describe).**

`[Answer]:` A

### Q3 — TRACE-1's two coverage mechanisms (P-OBS-2): ONE shared span-sink interface with two callers, or two distinct interfaces?
The checkpointer callback (graph nodes) and the span API (tool steps) are two mechanisms; do they emit through **one** span sink or two?

- **A. ONE shared span-sink Protocol (`record_span`), TWO callers** — the checkpointer-callback adapter **and** the span-API context-manager both project via the allowlist and call the **same** `record_span(step_name, attributes)`. The **single span schema** + single sink makes *"100% = graph nodes ∪ wrapped tool steps"* a clean **union over one span stream**; the recording fake implements the one Protocol and counts spans across both callers. *(Recommended — one span schema, one sink, one coverage assertion; the two callers are just the two grounded step sources; simplest jointly-exhaustive design.)*
- **B. Two distinct sink interfaces** (a node-trace sink + a tool-span sink). More explicit separation of the two step sources, but splits the span schema and the coverage assertion across two streams for no invariant gain, and complicates the recording fake.
- **C. Other (describe).**

`[Answer]:` A

---

## 5.5 MANDATORY AMBIGUITY-CHECK — RUN 2026-07-18 against Q1–Q3 (all A) + the frozen FD + approved NFR Requirements → **CLEAN (3 folds; no surface-and-stop)**

Checked against **BR-OBS-1..7**, the **eleven `NFR-OBS-*`**, **FD-OBS-Fold-1..3**, **NFR-OBS-Req-Fold-1..3**, and U4's real 4-node graph + `MEMO_CITATION_RETRY_CAP=2`. **Each of the user's three flagged checks resolves against a frozen fact; none improvised.**

### NFR-ND-OBS-Fold-1 — [CHECK (i)] the single `record_span` sink does NOT weaken TRACE-1's two-real-path teeth; `step_name` gives latent per-caller attribution
The two-path teeth (finalize = 3 spans; retry-then-flag = 5 spans at CAP=2) are asserted **per teeth test**, and **each test drives exactly one caller**: the graph-path teeth feed the **checkpointer-callback** a fake node sequence (only graph-node spans recorded → the recorded ordered `step_name` list **equals** the grounded sequence `[draft, validate, finalize]` / `[draft, validate, draft, validate, flag]`); the tool-step teeth feed the **span API** a fake tool step (only that span recorded). So within each test the **union count IS the per-source count** — the single sink introduces **no ambiguity**. **Latent attribution exists if ever needed**: `record_span(step_name, attributes)` records `step_name`, and graph-node names (the frozen four) are **distinct** from tool-step names — so a future per-source assertion could partition by `step_name` **without** a separate source tag. **Genuinely doesn't matter for the union coverage claim; attribution is available for free. Not a gap.**

### NFR-ND-OBS-Fold-2 — [CHECK (ii)] the allowlist utility's detector self-test IS DEMOFREE-1's (single-sourced guarantee = single-sourced test) + a no-bypass scan
Because `project_allowlisted(fields, allowed)` (Q1-A) **is** where DEMOFREE-1's guarantee lives (P-OBS-4), DEMOFREE-1's **detector self-test IS the utility's self-test** — feed it a `fields` dict containing a forbidden attribute (free-text/demographic/`original_span`-style) with an `allowed` set excluding it → assert the output **drops** it. There is **no separate, distinct** utility self-test; they are **one test at the single source**. It is **complemented** (not duplicated) by a **structural "routes-through-the-utility" scan** proving **neither plane bypasses** the utility (no plane reads a raw attribute into a span/label directly) — the utility-drops-it proof + the no-bypass proof **together** are DEMOFREE-1. **Not two tests where one suffices; one guarantee, single-sourced. Not a gap.**

### NFR-ND-OBS-Fold-3 — [CHECK (iii)] Q2's by-shape consumption and STEPMETRIC-1's `is_outlier`-by-value fixture AGREE by construction; a consistency check pins it
The `allowed` set is **per-derivation** (each derivation passes the field names its source legitimately carries; the utility drops anything else + any non-scalar). STEPMETRIC-1's `fake_outlier_step_outcome` exposes **`is_outlier`** — U18's **real** field name (Req-Fold-2, by value) — and the outlier-flag-rate derivation's `allowed` set **includes `is_outlier`**, so **fixture field ∈ derivation allowlist** — consistent, **not** divergent. Because the fixture is grounded in U18's real field name **and** the derivation reads that same name, the by-value fixture and the by-shape consumption **agree by construction**. A **consistency assertion** pins it (the derivation reads the fixture's field successfully / the fixture's names ⊆ the derivation's `allowed` set), so a rename on either side fails loudly. Same discipline for the provider-error outcome field. **Not a gap.**

**Verdict: CLEAN — no genuine gap requires a decision.** All three checks resolve against frozen facts (per-test single-caller teeth + latent `step_name` attribution; the single-sourced utility self-test + no-bypass scan; the fixture/allowlist agreement grounded in U18's real field). → **Part 2 authorized.**

---

## 6. Gate
- [x] **(1)** **Q1–Q3 answered — all A**; full text + answers embedded (§5).
- [x] **(2)** Mandatory **ambiguity-check RUN** (§5.5) → **CLEAN** (3 folds, no surface-and-stop) — the three user-flagged checks resolved against frozen facts.
- [x] **(3)** **Part 2 GENERATED** — `guide-docs/build/observability/nfr-design/`: `nfr-design-patterns.md` (`P-OBS-1..11`) + `logical-components.md` (`C-OBS-1..4`).
- [ ] **(4)** **NFR Design 2-option completion gate — AWAITING USER.** (1. Request Changes / 2. Continue → **Infrastructure Design**.)

**STOPPED at the NFR Design 2-option completion gate.** Infrastructure Design does **not** begin until the gate is answered.
