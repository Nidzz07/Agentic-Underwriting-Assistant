# Domain Entities — `memo-extensions` (U19, C4, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U19 `memo-extensions` · C4 · **Phase 2** · **Depth**: comprehensive · **Date**: 2026-07-17 · Stories **US-MEMO-5/6/7** · FR-MEMO-5/6/7, FR-PROV-2/5, FR-PROV-GATE-2.
**Scope**: the entity/contract view of `memo-extensions` — the **component/module inventory** (folded here per the comprehensive-unit convention), the **consumed frozen shapes** (by shape, re-declared by none), the **U19-local structural Protocol** standing in for the outlier read-surface, and the **MCP tool surfaces**. Built on **Q1/Q2/Q3/Q7 = A**, **Q4/Q5/Q6 = N/A**, and the ambiguity-check folds **FD-MEXT-Fold-1..5** (plan §5.8), re-opening none. **NO code in this stage.**

> **U19 adds NO new output contract.** It **extends** `memo-agent-core` (U4) with grounding + routing + provider breadth. Every schema it touches — `MemoAgentInput`, `MemoDraftOutput`, `DecisionMemo`, `ThinkingMode`, `CitationValidationResult` — is **frozen in U4 and consumed unchanged** (Q6 = N/A). **Advisory-only; the LLM drafts prose only and cannot alter a recommendation** (CON-BR2 / CON-BR2-TYPE, inherited).

---

## 1. Scope boundary — what this unit is, and the ONE thing it is NOT

| | |
|---|---|
| **IS** (Q3-A — all three module groups, one FD, as F4 grouped them) | `mcp-tools` (two **read-only** servers, supplementary only) · `borderline-router` (deterministic routing to extended thinking) · **secondary (Claude) / showcase (Ollama) provider adapters** extending U4's `provider-abstraction` **module** |
| **IS NOT** (Q1-A) | **"the memo narrative cites outlier flags."** Out of U19's frozen scope on four independent frozen sources; carried as the named register item **`OUTLIER-IN-PROSE`** (plan §4.3). **In U19 the outlier value decides a routing MODE; the LLM never sees it** (BR-MEXT-13). |

**The genuine U18→U19 consequence**: U18's landing **enables** FR-MEMO-7's outlier-driven **half of the borderline trigger**. That is **routing, not narration**.

---

## 2. Component / module inventory (folded component-methods)

Four owned modules under **`backend/memo_extensions/`** — the exact files the frozen layout `unit-of-work.md:70–71` names for U19. All pure Python. **No frozen unit is edited; U4 is imported, never modified** (BR-MEXT-11).

| Component | Module (frozen layout) | Role | Method surface (signatures pinned; bodies → Code-Gen) |
|---|---|---|---|
| **`BorderlineRouter`** | `borderline_router.py` | The **deterministic, provider-agnostic** borderline trigger — **rule-proximity OR outlier cutoff** (FR-MEMO-6). **No LLM.** Realizes the frozen C4 contract `component-methods.md:73`. U4's `route_borderline` stub **stays not-wired** (Fold-2). | `route_borderline(rule_report, outlier_result=None) -> ThinkingMode` (the frozen contract shape; `outlier_result` is the **handed-in**, nullable value — Q2-A) |
| **`McpToolService`** | `mcp_tools.py` | The **two read-only** servers — **`rulebook-tools`** + **`decisions-tools`** (`services.md:46`). **Supplementary human-readable context only; neither can write** (§5). Surfaces are **demographic-free by construction** (Fold-5). | `rulebook_tools.describe_rules(rule_ids) -> list[RuleDescription]`; `decisions_tools.recent_precedent(query) -> list[PrecedentSummary]`; `supplementary_context(...) -> SupplementaryContext` |
| **`ClaudeAdapter`** (secondary) | `provider_secondary.py` | The **tested** Claude Opus 4.8 fallback (FR-PROV-2). Implements the frozen `ProviderAbstraction` Protocol. `temperature=0` **fixed centrally inside the adapter** (TEMP0-1 inherited). **Extended thinking** supplied **at construction** (Fold-1). | `__init__(client, *, model, thinking_mode=ThinkingMode.STANDARD)`; `complete(prompt, schema) -> MemoDraftOutput`; `model_version -> str` |
| **`OllamaAdapter`** (showcase) | `provider_showcase.py` | The **wired-only** local showcase (FR-PROV-2). Same Protocol, same central `temperature=0`. **Exempt from memo-quality gates only** — **never** from the decision-level gates (BR-MEXT-10). May not support extended thinking (FR-PROV-5) — the **router's outcome is unchanged** by that (BR-MEXT-3). | `__init__(client, *, model, thinking_mode=ThinkingMode.STANDARD)`; `complete(prompt, schema) -> MemoDraftOutput`; `model_version -> str` |

> **Header-comment deliverables (by-construction guarantees, EXPLICIT at Code-Gen)** — mirroring the frozen self-evidence convention: **`borderline_router.py`** states it holds **no LLM client** and that both triggers are deterministic (FR-MEMO-6), and that the outlier value is **handed in, never imported** (Q2-A); **`mcp_tools.py`** states both servers are **read-only**, **supplementary only**, that **no citation may originate from a retrieval** (Q7-A), and that surfaces are **demographic-free** (CON-BR1); **`provider_secondary.py`** / **`provider_showcase.py`** state `temperature=0` is fixed **centrally, never caller-controlled** (TEMP0-1 part ii) and that the thinking mode arrives **at construction** because the frozen `complete()` signature admits no such parameter (Fold-1).

### 2.1 Why the mode arrives at CONSTRUCTION (Fold-1 — load-bearing)

The frozen `ProviderAbstraction.complete(prompt, schema)` carries **no thinking parameter**, and the frozen test `test_provider.py::test_complete_has_no_temperature_parameter` asserts the signature **exactly** (`params == ["self", "prompt", "schema"]`). The mode therefore **cannot** ride `complete`, and U4 cannot be amended.

**The frozen `CitationValidator` is the precedent — the identical shape, in this unit's own parent**: *"The authoritative grounding source … is supplied at **construction** … so the frozen signature is preserved unchanged."* U19's adapters take `ThinkingMode` **at construction**; the **orchestrator** constructs the adapter for the mode the router returned. **No frozen signature changes.**

### 2.2 How the PRIMARY (Gemini) reaches its thinking budget without touching U4 (Fold-1, cont.)

FR-PROV-5's *"Gemini thinking budget"* clause is reachable **by injection, not modification**, and **U19 adds no Gemini module** (none is in its frozen module list):

- **`LLMClient` is an INJECTED seam** (frozen `provider.py`), and that file already states the real client *"is wrapped to this minimal `LLMClient` seam **at composition time** (a deploy-config/secrets concern)"*.
- A **thinking-configured** client is therefore just **another `LLMClient` implementation**. The frozen `GeminiAdapter(client, *, model)` gets extended thinking by being **constructed with that client** — U4 untouched, its own tests untouched.
- **The capability/config binding lands exactly where U4 ALREADY frozen-deferred the real client** — deploy-config (U23) / composition — the same place the Gemini API key lands. U19 owns and **tests the mapping offline** with a capturing double (the **TEMP0-1 part i** precedent: *"a capturing test double records the outgoing request; no network, no key"*).

**FD pins**: the mapping `ThinkingMode → which client/adapter is constructed`, and that it is **offline-testable**. **Deploy-config / composition owns**: the real per-provider capability config (Claude's extended-thinking flag, Gemini's thinking budget value).

---

## 3. The routing input — a U19-local structural Protocol (Fold-3; Q2-A)

The frozen C4 contract `component-methods.md:73` types the trigger `(RuleResultReport, OutlierResult?) -> ThinkingMode`. But `unit-of-work-dependency.md:48` gives U19 **no `outlier-model` edge**, and **Q2-A** pins *"U19 imports no outlier-model"*.

**Resolved by the U20 precedent** (the immediately-prior unit, the same frozen-U18-shape situation): *"`outlier-model` (U18) … **never imported** — reached only `(orchestrated)` via R4; its nine feature names **mirrored by value**."*

```text
OutlierSignal (U19-local structural Protocol — the MINIMAL read surface; NOT an import, NOT a re-declaration)
├── is_outlier: bool          # the IsolationForest decision-boundary crossing
└── outlier_score: float      # the holistic score, compared against the U19 cutoff

Satisfied structurally by outlier_model.schemas.OutlierResult — by SHAPE, with no import and no edge.
Passed as None when absent  ->  FR-MEMO-7: "until it lands, routing runs on rule-proximity alone".
```

- **Reads the score/flag ONLY.** It **never** reads `flagged_features`, `shap_value`, or `provenance` — those are the **prose/display/trace** concerns of the `OUTLIER-IN-PROSE` register item, `ui-outlier-view` (U20), and `observability` (U21) respectively. **The minimal surface is itself a scope guard** (BR-MEXT-13).
- **The contract's own `?` IS FR-MEMO-7's degradation** — `None` is a **first-class, tested** input, not an error path.

---

## 4. Consumed frozen shapes (by shape / by import — re-declared by none, modified by none)

| Shape | Origin (frozen) | How U19 uses it |
|---|---|---|
| `ProviderAbstraction` (Protocol) | `memo_agent_core.provider` | **Implemented** by the Claude + Ollama adapters — the F4 *"extend the module"* mechanism |
| `LLMClient` (Protocol) | `memo_agent_core.provider` | The **injected** client seam each new adapter drives; a thinking-configured client is another implementation (§2.2) |
| `GeminiAdapter` | `memo_agent_core.provider` | **Constructed, never modified** (§2.2) — U19 selects its injected client per mode |
| `ThinkingMode` = `{STANDARD, EXTENDED}` | `memo_agent_core.schemas` | The router's **return type** — already frozen; **not a new addition** (Q6 = N/A) |
| `MemoDraftOutput` = `{narrative_prose, cited_rule_ids}` | `memo_agent_core.schemas` | The adapters' return type — **unchanged**; **CON-BR2-TYPE** inherited (no recommendation/confidence field ⇒ *unrepresentable*) |
| `MemoAgentInput` | `memo_agent_core.schemas` | The frozen prompt scope — **no field added** (that is precisely the `OUTLIER-IN-PROSE` collision, §4.2 of the plan) |
| `PromptBuilder` | `memo_agent_core.prompt_builder` | **Composed, never modified** — U19 appends a marked **non-citable** supplementary section to its output (Fold-4) |
| `CitationValidator` / `CitationValidationResult` | `memo_agent_core.citation_validator` · `.schemas` | The **single, unchanged** enforcement point for Q7-A (§5.2) |
| `RuleResultReport` | `rules_engine.report_schema` | The router's rule-proximity input **and** the sole citable grounding source (its `R` edge) |
| `Rulebook` | `rules_engine.rulebook_schema` | `rulebook-tools`' read-only description source (its `R` edge) |
| committed-decision records | `audit-store` (its `R` edge) | `decisions-tools`' read-only precedent source — **demographic-free projection only** (BR-MEXT-9) |
| `OutlierResult` | `outlier_model.schemas` | **NOT imported** — satisfied structurally via `OutlierSignal` (§3) |

**Reference-not-own**: U19's `backend.*` imports are `memo_agent_core` (its primary edge), `rules_engine` (`R`), and `audit-store` (`R`) — **exactly the three frozen edges of `unit-of-work-dependency.md:48`**. **No** `outlier_model` import; **no** consumer import (`observability` / `llm-judge` import **U19**, not the reverse); **no** frozen file edited.

---

## 5. The MCP tool surfaces (`services.md:46` — two read-only servers)

### 5.1 The two servers

| Server | Reads | Returns | Never |
|---|---|---|---|
| **`rulebook-tools`** | the active `Rulebook` (`rules-engine` `R`) | **supplementary human-readable rule descriptions only** (`services.md:46`) | writes; **re-derives what fired**; supplies a citable id |
| **`decisions-tools`** | committed decision records (`audit-store` `R`) | **demographic-free** precedent summaries | writes; exposes `full_name` / `gender` / `city`; supplies a citable id |

### 5.2 The retrieval-miss guard has STRUCTURAL teeth, not prompt-hope (Q7-A; Fold-4)

The **handed `RuleResultReport` is the SOLE citable grounding source.** MCP may **enrich context**; a **citation may never originate from a retrieval**. This is **enforced by the frozen `CitationValidator`, unchanged**:

> it is **constructed with the handed report** and requires every `cited_rule_id` to be a **member of that report** *and* of the active `Rulebook`.

So a rule that exists in the rulebook — **i.e. exactly one that MCP could describe** — but was **not evaluated for this applicant** fails **report-membership** and is rejected as `citation_failure` with the offending ids. **A retrieval miss therefore cannot produce an uncitable or hallucinated rule — by construction, with no change to the frozen gate.**

### 5.3 Why "grounded in live tools" and "supplementary only" are not in conflict

US-MEMO-5 wants drafting *"grounded in live tools rather than memorised content"*; `unit-of-work.md:243` and the frozen `prompt_builder.py` say cite **only** from the handed report and that **no MCP re-derives what fired**. `services.md:46` — **the more specific frozen resolution** — reconciles them: *"supplementary human-readable rule descriptions only"*. **"Live tools not memorised content" governs the DESCRIPTIONS; the CITABLE SET stays the handed report.**

---

## 6. Schema-vs-config boundary + FD↔later boundary

- **Schema / behaviour (this FD pins)**: the four module surfaces (§2); the `OutlierSignal` minimal read surface (§3); the two MCP tool surfaces (§5); the **construction-time** thinking-mode mechanism (§2.1–2.2); the borderline **trigger names** — `RULE_PROXIMITY_MARGIN` + `OUTLIER_SCORE_CUTOFF` — as **single fixed named constants** (BR-MEXT-1).
- **NFR / Code-Gen owns**: the exact `RULE_PROXIMITY_MARGIN` / `OUTLIER_SCORE_CUTOFF` **values** (configurable per FR-MEMO-6, confirmable after calibration — the `Z_SCORE_FLAG_THRESHOLD` precedent, CG-OUT-Fold-1); the MCP server library/transport; the Claude/Ollama model strings; retry/timeout posture on a retrieval miss.
- **deploy-config / composition owns** (already frozen-deferred by U4): the **real** `LLMClient` wrapping, per-provider **capability config** (Claude extended-thinking flag; **Gemini thinking budget**), keys via `secrets-config`.
- **Out of scope (named-not-designed)**: **`OUTLIER-IN-PROSE`** (Q1-A — the registered gap); the orchestrator wiring that calls the router and constructs the adapter (**the caller's**, per Q2-A's handed-in pattern and U18's *"the unit owns the scorer; the orchestration is downstream"* boundary); `observability` (U21) / `llm-judge` (U22) consumption — **their** FDs, since they import U19, not the reverse.

## 7. Cross-consumer field-need check (contract stability)

U19 **introduces no new type**, so there is no new contract for a downstream consumer to absorb — the strongest possible stability result. Its two known consumers read **existing frozen shapes**: **`observability`** (U21, `:50`) traces U19's agent/tool steps (needs the module/step surface, not a schema); **`llm-judge`** (U22, `:51`) scores memo groundedness on `MemoDraftOutput` — **frozen and unchanged** — for **Gemini + Claude only** (FR-PROV-GATE-2 / QA-4; **Ollama exempt**, BR-MEXT-10).
