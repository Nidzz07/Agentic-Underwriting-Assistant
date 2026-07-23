# NFR Requirements — `memo-extensions` (U19, C4, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U19 `memo-extensions` · C4 · **Phase 2** · **Depth**: comprehensive · **Date**: 2026-07-17 · Stories **US-MEMO-5/6/7** · FR-MEMO-5/6/7, FR-PROV-2/3/5, FR-PROV-GATE-1/2, CON-BR1, CON-BR2, CON-DET-1.
**Built ON** the frozen FD (**BR-MEXT-1..13**; the four-module inventory; the **`OutlierSignal`** structural Protocol; the **construction-time** thinking-mode mechanism; the MCP **supplementary / read-only / demographic-free** boundary; the **BR-MEXT-13** negative scope guard) — **re-opening none.** Each `NFR-MEXT-*` is a **pass/fail testable assertion** traced to its BR-MEXT-\*. Answers **Q1–Q4 all A** + folds **NFR-MEXT-Fold-1..4** (plan §3.5) folded in.

**Tiers**: **tier-U** = fast, deterministic, in CI — **the default path: no live LLM call, no key, no network, no Docker, no live MCP server** (the frozen U4 discipline, verbatim: *"No test constructs a real Gemini client, reads a key, or touches the network"*), extended to **Claude and Ollama**; **tier-S** = offline smoke (optional); **tier-B** = **N/A to U19** (it never touches the corpus) and **NOT authorized**. Every lint/scan carries a **detector self-test** so it can never pass vacuously (the CG-NFR-OUT-Fold-3 convention).

> **`MCP-TRANSPORT-DEFERRED` (Q4-A, plan §3.6)** — U19 delivers the **tool-handler layer + an injected transport seam**; the **live MCP protocol binding** is deferred to composition/deploy-config. **This blocks none of U19's invariants**: GROUND-1 / MCPRO-1 / MISS-1 / BIAS-1 are **each fully verified at tier-U with no MCP package present** (NFR-MEXT-Fold-2).

---

## 1. Finalized `NFR-MEXT-*` targets (pass/fail; acceptance; tier; rigor)

### FULL RIGOR — the two LOAD-BEARING targets

#### NFR-MEXT-ROUTE-1 — deterministic, LLM-free, provider-free borderline routing (BR-MEXT-1) — **LOAD-BEARING**
- **Assertion**: `route_borderline` is a **pure function** of `(rule_report, outlier_signal | None)` — no LLM, no provider, no network, no wall-clock, no RNG. **The deterministic core stays deterministic** (skill #3/#5).
- **Acceptance**: **(a) purity teeth** — the same `(report, signal)` yields an **identical `ThinkingMode` across N≥2 calls**; no state is retained between calls. **(b) structural/AST scan** — **zero** LLM / provider / adapter / network / `httpx` / `requests` / client imports **anywhere** under `borderline_router.py`, **+ mandatory detector self-test** (a synthetic LLM-client import line is fed to the detector and must be **flagged**). **(c) trigger teeth** — a **REFER** report routes `EXTENDED`; rule-proximity **within** `RULE_PROXIMITY_MARGIN` ⇒ `EXTENDED`; outside ⇒ `STANDARD`; `outlier_score` **above** `OUTLIER_SCORE_CUTOFF` ⇒ `EXTENDED`. **(d) boundary teeth** — a value **exactly at** each threshold lands on the **intended** side, with the comparison (`<=` vs `<`) **explicit** (the skill's boundary-behaviour discipline). **(e) constants** — exactly **one** module-level literal per trigger; flag-selection is tested **parameterically off the same named constant the production code reads**, **never** a hardcoded number (the **NFR-OUT-THRESHOLD-1 / Q3-A precedent**), so a future calibration is a **one-constant edit with tests still green**.
- **Tier**: structural (AST) + component (teeth). **Rigor**: **full (highest)**.

#### NFR-MEXT-FROZEN-1 — extend-don't-modify; the frozen U4 boundary holds (BR-MEXT-11 / Q1-A) — **LOAD-BEARING**
- **Assertion**: U19 **extends** U4 from its **own modules** and **modifies nothing**; U4's Phase-2 seams **stay seams**.
- **Acceptance**: **(a) the two frozen facts, MIRRORED locally (Q1-A)** — U19's suite imports **only U4's PRODUCTION module** (`memo_agent_core.provider` — **already U19's legitimate edge**; **no U4 test file is imported**, so no double-collection and no coupling to U4's test-function names) and re-asserts: **`route_borderline()` raises `NotImplementedError`**, and **`dir(provider_module)` contains no `Claude`/`Ollama`/`Mcp`/`MCP` name**. **(b) import-discipline scan (NFR-MEXT-Fold-4)** — U19's only `backend.*` imports are **`memo_agent_core`, `rules_engine`, `audit_store`** — **exactly its three frozen edges** (`unit-of-work-dependency.md:48`) — **+ detector self-test**. **(c) adapters live outside U4's namespace** — none of U19's adapter names appears in `dir(memo_agent_core.provider)`. **(d) the full frozen backend suite stays green** with U19 added (**1011 passed / 31 skipped** baseline — **zero regression, purely additive**).
- **Why (a) is NOT a duplicate of U4's own suite (NFR-MEXT-Fold-1)**: `dir(provider_module)` inspects a **live namespace** in whatever **import state** the session is in. U4's test module imports **only U4**, and under pytest's default collection order (`memo_agent_core` **before** `memo_extensions`) U19 may **not yet be imported** when it runs — so a **module-level namespace pollution originating in U19** (an accidental import-time monkeypatch of U4's module) **would escape U4's own test**. U19's mirror runs where U19's adapters **are** imported, so it **catches it**. **The mirror is strictly stronger in the one context that matters.**
- **Why NOT a file-hash/mtime pin (NFR-MEXT-Fold-4)**: mtime is meaningless across a git checkout, and a hash pin would **false-fail a deliberate future amendment** (e.g. if `OUTLIER-IN-PROSE` is ever resolved toward a U4 change **with the hold explicitly lifted**) — turning a guard into an obstacle. **No prior unit did this**; session-level mtime checks are a **reviewer/agent** discipline, **never a test**. The **behavioral + import-discipline** guards fail loudly on a **real** violation and stay green through a **deliberate** one.
- **Tier**: component (behavioral) + structural. **Rigor**: **full (highest)**.

### FULL RIGOR

#### NFR-MEXT-GROUND-1 — the retrieval-miss guard is STRUCTURAL, via the frozen validator (BR-MEXT-6 / Q7-A / FM1–FM2) — **called out: the groundedness target**
- **Assertion**: the handed `RuleResultReport` is the **sole citable grounding source**; **no citation may originate from an MCP retrieval**; the **frozen `CitationValidator` is the single enforcement point, unchanged**.
- **Acceptance**: **(a) the direct retrieval-miss test** — a memo draft citing a rule that **exists in the `Rulebook` but is ABSENT from the handed `RuleResultReport`** (**precisely what MCP can describe**) → the frozen validator returns **`citation_failure`** with that id in `offending_cited_ids`. **The guard is proven by construction, not by prompt.** **(b)** `citation_validator.py` is **unmodified** (import-discipline + behavioral scan). **(c)** the supplementary section is **explicitly marked non-citable** in the composed prompt. **(d)** **no U19 code path appends to `cited_rule_ids`** (structural scan + detector self-test). **(e)** the composed prompt = U4's frozen `PromptBuilder.build()` output **+ an appended** supplement — U4's builder is **composed, never modified**.
- **Tier**: component (teeth) + structural. **Rigor**: full.

#### NFR-MEXT-SIGNAL-1 — handed-in outlier signal; no `outlier-model` edge; `None` degrades (BR-MEXT-2 / Q2-A / Fold-3)
- **Acceptance**: **(a) by-shape teeth** — a **U19-local fake** satisfying `OutlierSignal` structurally drives **every** routing test (**no U18 import in tests either** — the U20 *"never imported"* discipline). **(b) interop self-test** — a **real U18 `OutlierResult` constructed BY VALUE (never by import)** is shown to **satisfy the Protocol structurally**, proving the frozen `component-methods.md:73` contract `(RuleResultReport, OutlierResult?)` is honored **without an edge**. **(c) `None`-degrades teeth** — `route_borderline(report, None)` **equals** the rule-proximity-only result over that report (**FR-MEMO-7**: *"until it lands, routing runs on rule-proximity alone"*); `None` is a **first-class tested input**, not an error path. **(d) scan** — **no `outlier_model` import** under `backend/memo_extensions/` (+ detector self-test).
- **Tier**: component + structural. **Rigor**: full.

#### NFR-MEXT-AGNOSTIC-1 — the routing outcome is provider-agnostic; capability degrades at the adapter (BR-MEXT-3 / FR-PROV-5)
- **Acceptance**: the **identical** `(report, signal)` yields the **identical** `ThinkingMode` under **all three** provider selections; the router's source references **no** adapter/provider name (scan); an **Ollama** adapter constructed with `EXTENDED` **still completes** (degrades) rather than raising — *"where supported"* is an **adapter-level** fact, never a **trigger-level** one.
- **Tier**: component + structural. **Rigor**: full.

#### NFR-MEXT-THINK-1 — the thinking mode is supplied at CONSTRUCTION; no frozen signature changes (BR-MEXT-4 / Fold-1)
- **Acceptance**: **(a) the frozen signature assertion, applied to EACH new adapter** — `inspect.signature(...).parameters` is **exactly** `["self", "prompt", "schema"]` for the Claude **and** Ollama adapters (U4's own assertion, extended); each `isinstance(...)` the `runtime_checkable` `ProviderAbstraction`. **(b) capturing-double teeth, OFFLINE** — an adapter constructed with **`EXTENDED`** produces a **thinking-configured outgoing request**; constructed with **`STANDARD`** it does **not** — recorded by a capturing double, **no network, no key, no live call** (the TEMP0-1 part i pattern). **(c)** the mode appears in **no** `complete` signature — it is **construction-time only**.
- **Tier**: component (offline doubles) + structural. **Rigor**: full.

#### NFR-MEXT-TEMP0-1 — `temperature=0` centrally, for all three providers, in both modes (BR-MEXT-5 / FR-PROV-3 / skill #4)
- **Acceptance**: the capturing double records **`temperature == 0`** on **every** call from **every** adapter (**Claude and Ollama**), in **BOTH** thinking modes; **no** adapter's `complete` exposes a `temperature` parameter (TEMP0-1 part ii); the value is set **centrally inside the adapter**, never caller-controlled. **Extended thinking never implies a non-zero temperature.**
- **Tier**: component (offline doubles) + structural. **Rigor**: full.

#### NFR-MEXT-MISS-1 — a retrieval miss is NON-FATAL (BR-MEXT-8 / brief §10 FM2)
- **Acceptance**: with **both** MCP handlers **unavailable** (fake transport failing / timing out / returning empty), drafting still yields a **valid `MemoDraftOutput`** whose citations **pass** the frozen validator; the failure path adds **no** content to the prompt; the miss is **observable** (surfaced for U21's traces), **not silent**. **A miss never blocks a memo and never relaxes GROUND-1** — the citable set never depended on MCP.
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-MEXT-MCPRO-1 — both tool surfaces are READ-ONLY (BR-MEXT-7 / SEC-4 / skill #2)
- **Acceptance**: **neither** handler surface exposes a **write / mutate / commit** method (surface scan); **no** `DecisionCommitService` / write-transport / session-write import under `mcp_tools.py` (+ detector self-test); the `rules-engine` and `audit-store` edges are exercised **read-only**. **The human approval gate is untouched and outside this unit.**
- **Scope note (NFR-MEXT-Fold-2)**: under Q4-A the *"server"* at this stage is the **tool-handler surface** — **which is where a write could actually be written**, so the invariant is verified at **full strength with no protocol present**; a deferred transport **cannot introduce a write the handlers do not expose**.
- **Tier**: structural. **Rigor**: full.

#### NFR-MEXT-BIAS-1 — the MCP surfaces are DEMOGRAPHIC-FREE BY CONSTRUCTION (BR-MEXT-9 / CON-BR1 / skill #6 / Q3-A + Fold-3)
- **Assertion**: U19 **may not reintroduce through MCP what U4's frozen `PromptBuilder` deliberately excluded** (*"Demographic identifiers … are **deliberately excluded** … the memo prose never sees them"*).
- **Acceptance** — **asymmetric, matched to where the risk actually lives (Q3-A)**:
  - **(a) shared structural scan (BOTH modules)** — no `full_name` / `gender` / `city` / `.demographics` reference in **any** `mcp_tools.py` return path, **+ mandatory detector self-test** (a synthetic `record.demographics.city` read is fed to the detector and must be **flagged**).
  - **(b) `decisions-tools` — FULL SWAP TEETH on the OUTPUT PROJECTION (Fold-3)** — seed the fake decision-record source with records differing **ONLY** in `full_name`/`gender`/`city` over **identical financials** → the returned projection / supplementary context is **byte-identical**. This is the **real** teeth: `decisions-tools` reads **stored records about other applicants**, so the demographics live in **the data it returns**, not in the caller's request — this **directly proves the projection drops them**.
  - **(c) `rulebook-tools` — a STRONGER by-construction assertion (Q3-A)** — `describe_rules(rule_ids)` **takes no applicant input at all**, so it **cannot leak a demographic**; asserted structurally (its parameter/return types carry **no** applicant-derived or demographic field). **This is strictly stronger than a swap test that could not fail** — a swap test here would have **nothing to swap** and would pass **vacuously**, exactly the false confidence the detector-self-test convention exists to prevent.
  - **(d) input side, both surfaces** — the query/parameter types carry **no** demographic field (the same by-construction argument), so a demographic **cannot enter** either surface.
- **Boundary with quality-gates**: the `quality-gates` bias-swap suite remains the **external** CON-BR1 delta verifier; U19 proves the **structural mechanism** + owns this regression (the rules-engine / U18 precedent).
- **Tier**: structural + component (teeth). **Rigor**: full.

#### NFR-MEXT-CONTRACT-1 — no new output contract; a recommendation-change stays unrepresentable (BR-MEXT-12 / CON-BR2-TYPE / QA-5 / skill #1)
- **Acceptance**: structural — **no** U19 module declares a Pydantic model, and **none** declares or emits a `Recommendation` field or value (+ detector self-test); `MemoDraftOutput` / `DecisionMemo` / `MemoAgentInput` are **unmodified**; **QA-5** (*"a test MUST assert the LLM cannot change a recommendation"*) holds for **Claude and Ollama** exactly as for Gemini — the model's output type declares **no** recommendation field, so the change is **unrepresentable** through every provider and both modes; no "decision"-as-verdict wording in U19 strings.
- **Tier**: structural. **Rigor**: full.

#### NFR-MEXT-SCOPE-1 — the negative scope rule: no outlier data reaches the prose (BR-MEXT-13 / Q1-A)
- **Acceptance**: structural — **zero** references to `flagged_features` / `shap_value` / `provenance` **anywhere** under `backend/memo_extensions/`, **+ mandatory detector self-test** (a synthetic `result.flagged_features` read is fed to the detector and must be **flagged**, so the scan **cannot pass vacuously**); the composed prompt's supplementary section contains **no** outlier content; `MemoAgentInput` **unmodified**. **The `OutlierSignal` minimal read surface (`{is_outlier, outlier_score}`) is itself the guard** — the router structurally cannot reach the prose-bearing fields.
- **Guards**: the registered **`OUTLIER-IN-PROSE`** gap — **so Code-Gen cannot drift into it.**
- **Tier**: structural. **Rigor**: full.

#### NFR-MEXT-PROVGATE-1 — Ollama is exempt from MEMO-QUALITY gates only, never from DECISION-LEVEL gates (BR-MEXT-10 / FR-PROV-GATE-1/2)
- **Acceptance**: **(a)** the **Ollama** adapter **IS** unit-tested offline — constructed; `temperature=0` asserted; structured output parsed. ***"Wired-only" ≠ untested code.*** **(b)** `temperature=0` (TEMP0-1) **and** CON-BR2-TYPE (CONTRACT-1) hold for it **identically** — because **FR-PROV-GATE-1's decision-level gates (reproducibility 100%, bias-swap delta 0) apply to ALL providers**, *"because the decision is provider-independent (CON-BR2)"*. **(c) GOVERNANCE, not a code test** — its **absence from the groundedness/promptfoo target set** (AC-6 / QA-4 / FR-PROV-GATE-2) is a **Code-Gen / tooling-config fact owned by `llm-judge` (U22)**, **NOT a code fact needing a test here**; recorded as a **documented, explicit** exemption — **never implicit**.
- **Tier**: component (a/b) + governance (c). **Rigor**: full (a/b) · governance (c).

### SOFT / OBSERVED

#### NFR-MEXT-PERF-1 — adapter / handler cost observed, non-gating
- **Assertion / Acceptance**: **no hard SLO** — consistent with **every** prior unit's soft-perf posture. **No live call is timed because there are none at tier-U** (every provider + transport is an injected double). Real per-provider latency is a **deploy-config / observability (U21)** concern, not U19's.
- **Tier**: observed / soft. **Rigor**: soft.

### GOVERNANCE

#### NFR-MEXT-SEC-1 — scoped exclusions *(not a runtime test)*
- **Statement**: this set tests **only** `memo-extensions`' behavior. It does **not** test other units, the WIRE-1 routes, the live MCP protocol (**`MCP-TRANSPORT-DEFERRED`**), or the tier-B corpus (**N/A**). It **composes** U4 without modifying it, consumes frozen shapes **by shape**, and introduces **no write path**. Enforced by review + the structural scans above.
- **Tier**: N/A (governance).

---

## 2. Traceability (target → BR-MEXT-* / requirement → tier → rigor)

| Target | BR-MEXT / requirement | Tier | Rigor |
|---|---|---|---|
| **NFR-MEXT-ROUTE-1** | BR-MEXT-1 / FR-MEMO-6 / CON-DET-1 / skill #3/#5 | structural + component | **full (highest)** |
| **NFR-MEXT-FROZEN-1** | BR-MEXT-11 / F4 / the two frozen U4 tests | component + structural | **full (highest)** |
| **NFR-MEXT-GROUND-1** | BR-MEXT-6 / FR-MEMO-5 / Q7-A / FM1–FM2 / skill #8 | component + structural | full |
| NFR-MEXT-SIGNAL-1 | BR-MEXT-2 / FR-MEMO-7 / `component-methods.md:73` | component + structural | full |
| NFR-MEXT-AGNOSTIC-1 | BR-MEXT-3 / FR-PROV-5 | component + structural | full |
| NFR-MEXT-THINK-1 | BR-MEXT-4 / FR-PROV-5 | component + structural | full |
| NFR-MEXT-TEMP0-1 | BR-MEXT-5 / FR-PROV-3 / skill #4 | component + structural | full |
| NFR-MEXT-MISS-1 | BR-MEXT-8 / brief §10 FM2 | component | full |
| NFR-MEXT-MCPRO-1 | BR-MEXT-7 / SEC-4 / skill #2 | structural | full |
| NFR-MEXT-BIAS-1 | BR-MEXT-9 / CON-BR1 / skill #6 | structural + component | full |
| NFR-MEXT-CONTRACT-1 | BR-MEXT-12 / CON-BR2-TYPE / QA-5 / skill #1 | structural | full |
| NFR-MEXT-SCOPE-1 | BR-MEXT-13 / Q1-A | structural | full |
| NFR-MEXT-PROVGATE-1 | BR-MEXT-10 / FR-PROV-2 / FR-PROV-GATE-1/2 / AC-6 | component + governance | full · governance |
| NFR-MEXT-PERF-1 | (adapter/handler cost) | observed | soft |
| NFR-MEXT-SEC-1 | governance | N/A | governance |

**No orphaned BR-MEXT rule**: 1→ROUTE-1 · 2→SIGNAL-1 · 3→AGNOSTIC-1 · 4→THINK-1 · 5→TEMP0-1 · 6→GROUND-1 · 7→MCPRO-1 · 8→MISS-1 · 9→BIAS-1 · 10→PROVGATE-1 · 11→FROZEN-1 · 12→CONTRACT-1 · 13→SCOPE-1. PERF-1 / SEC-1 cover the cost + governance concerns.

**Story coverage**: **US-MEMO-5** → GROUND-1 + MCPRO-1 + MISS-1 + BIAS-1 (+ THINK-1's structured-output breadth) · **US-MEMO-6** → ROUTE-1 + SIGNAL-1 + AGNOSTIC-1 + THINK-1 · **US-MEMO-7** → TEMP0-1 + PROVGATE-1 + CONTRACT-1.

---

## 3. Security-Guardrails extension — compliance (enabled extension)

`memo-extensions` **adds an LLM provider surface and a retrieval surface** to a pipeline that had neither in Phase 1 — so the controls below are assessed against **exactly** those two additions.

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | U19 drafts from an already-validated `MemoAgentInput` assembled by U4 from clean artifacts; application-input validation is `intake`'s SEC-2, sanitization is `document-sanitizer`'s SEC-1. U19 adds **no** application-input surface. |
| **Prompt-injection defense** | **Compliant (inherited + not widened)** | The prompt is U4's frozen `PromptBuilder` output **plus a supplementary section marked non-citable** (GROUND-1e). MCP returns **authored rulebook descriptions + demographic-free precedent projections** — **not** applicant-supplied document text (that path is sanitized upstream by SEC-1, before it ever reaches C4). **Crucially, injection cannot widen authority**: even a hostile supplement **cannot** produce a citation (report-membership, GROUND-1a) and **cannot** alter a recommendation (unrepresentable, CONTRACT-1). |
| Secrets management | **Compliant (referenced)** | Claude/Ollama keys+endpoints come from **`secrets-config`** via env/secrets (`unit-of-work-dependency.md:54`), **never hardcoded**; **no key is read at tier-U** — every adapter takes an **injected client** (*"no network, no key"*). |
| **Read-only DB access** | **Compliant (load-bearing here)** | Both MCP surfaces are **read-only** (MCPRO-1) — **neither can write**; **no** `DecisionCommitService` / write-transport import. The `audit-store` edge is **`R`**. The **human approval gate is untouched and outside this unit** (skill #2). |
| Audit logging | **N/A (producer, not persister)** | U19 persists nothing. Its steps are **traced by `observability` (U21)**, which imports U19 — not the reverse. |
| Error hygiene (no secret/PII leak) | **Compliant** | A retrieval miss degrades **without** surfacing transport internals into the prompt (MISS-1); the supplementary context is **demographic-free by construction** (BIAS-1); no secret is present at tier-U to leak. |
| **Bias-free by design (CON-BR1)** | **Compliant (load-bearing)** | **BIAS-1** — U19 **may not reintroduce via MCP what U4 deliberately excluded**: shared demographic scan over both modules + **swap teeth on `decisions-tools`' output projection** + a **by-construction** argument for `rulebook-tools` (takes no applicant input). `quality-gates` remains the external delta verifier. |
| **Reproducibility (CON-DET-1)** | **Compliant (load-bearing)** | **ROUTE-1** (pure, LLM-free, constant-driven, boundary-explicit) + **AGNOSTIC-1** (provider-independent outcome) + **TEMP0-1** (`temperature=0` on all three providers, both modes). Adding two providers **cannot** change a recommendation (CONTRACT-1), which is why FR-PROV-GATE-1's decision-level gates apply to **all three**. |
| **Advisory-only (skill #1)** | **Compliant** | **CONTRACT-1** — U19 adds **no** output contract; `MemoDraftOutput` still declares **no** recommendation/confidence field, so a recommendation-change is **unrepresentable** through every new provider and mode. |
| **Full explainability (skill #8)** | **Compliant** | **GROUND-1** — every cited rule id must be a **member of the handed report** (frozen validator, unchanged); an MCP-described-but-not-evaluated rule is **rejected**. Retrieval **cannot** produce an unexplained citation. |
| **Deliverable transparency** | **Compliant (registered)** | **`MCP-TRANSPORT-DEFERRED`** is an **explicit named register item** (plan §3.6) — the live protocol binding is **openly outstanding**, not quietly assumed done. **Non-blocking**: no U19 invariant depends on it. |

**No blocking finding.**

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-MEXT-1..13 + the module inventory + `OutlierSignal` + the MCP boundary) is the substrate — targets attach to it.
- **Q1-A** — the frozen-boundary guard **mirrors** the two facts locally against U4's **production** module (no test-file import); **Fold-1** shows this is **strictly stronger** than U4's own test in U19's import context; **Fold-4** rules out a brittle hash/mtime pin.
- **Q2-A** — handlers tested **directly** as pure functions; the **transport is an injected seam with a fake**, mirroring `LLMClient`; **no live MCP server at tier-U**.
- **Q3-A + Fold-3** — swap teeth on **`decisions-tools`' output projection** (where the leak lives); **by-construction** for `rulebook-tools`; shared scan over both.
- **Q4-A** — **no new dependency**; the MCP protocol/SDK is deferred → **`MCP-TRANSPORT-DEFERRED`** (plan §3.6), **explicitly non-blocking** for BR-MEXT-6/7/8/9.
- **Deferred to NFR-Design / Code-Gen**: the exact `RULE_PROXIMITY_MARGIN` / `OUTLIER_SCORE_CUTOFF` **values** (configurable per FR-MEMO-6; confirmable after calibration — the CG-OUT-Fold-1 precedent); the Claude/Ollama model strings; the thinking-config shape per provider; retry/timeout posture on a miss; the fake-transport fixture construction.
- **Deferred to composition / deploy-config (U23)** — *already frozen-deferred by U4*: the **real `LLMClient` wrapping**, per-provider **capability config** (**Gemini thinking budget**, Claude extended-thinking flag), keys, and the **MCP protocol binding**.
- **tier-B**: **N/A to U19** and **NOT authorized**. The **`audit_store` Docker-guard gap** stays **out of U19's test path** (the `decisions-tools` seam replaces any live DB) and **untouched**.
