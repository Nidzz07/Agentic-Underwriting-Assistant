# Tech-Stack Decisions — `memo-extensions` (U19, C4, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U19 `memo-extensions` · C4 · **Phase 2** · **Date**: 2026-07-17.
**Scope**: the technology decisions the `NFR-MEXT-*` set rests on. **NO new dependency** — provider breadth is **already floored and installed**, and the **MCP protocol/SDK is deferred** (**`MCP-TRANSPORT-DEFERRED`**, §3). Built on the frozen FD + **Q1–Q4 all A** + folds **NFR-MEXT-Fold-1..4** (plan §3.5) — re-opening none.

---

## 1. Decisions

| # | Decision | Choice | Rationale | Traceability |
|---|---|---|---|---|
| **MEXT-D1** | **Secondary provider (Claude)** | **`anthropic`** SDK — **already floored `anthropic>=0.40.0`**, **installed `0.116.0`** (verified on disk; `langchain-anthropic 1.4.8` also present) | FR-PROV-2 names Claude Opus 4.8 as the **tested** fallback. The adapter implements the **frozen `ProviderAbstraction` Protocol** from **U19's own module** (`provider_secondary.py`) — U4 untouched (BR-MEXT-11). **No new dependency.** | FR-PROV-2, US-MEMO-7, NFR-MEXT-TEMP0-1/THINK-1 |
| **MEXT-D2** | **Showcase provider (Ollama)** | **`ollama`** SDK — **already floored `ollama>=0.3.0`**, **installed `0.6.2`** (verified) | FR-PROV-2 names Ollama as **wired-only showcase**. *"Wired-only" **≠ untested code***: the adapter **is** unit-tested offline; it is exempt from **memo-quality** gates only (FR-PROV-GATE-2) and **never** from the **decision-level** gates (FR-PROV-GATE-1). **No new dependency.** | FR-PROV-2, FR-PROV-GATE-1/2, NFR-MEXT-PROVGATE-1 |
| **MEXT-D3** | **`temperature=0` placement** | fixed **centrally inside each adapter**; **never** a caller-controlled parameter | Inherits U4's **TEMP0-1** discipline verbatim (`_PRODUCTION_TEMPERATURE = 0`, *"central; not caller-controlled"*). Holds for **all three** providers, in **both** thinking modes — **extended thinking never implies a non-zero temperature**. | FR-PROV-3, skill #4, BR-MEXT-5, NFR-MEXT-TEMP0-1 |
| **MEXT-D4** | **Thinking-mode delivery** | supplied at **CONSTRUCTION**, never through `complete()` | The frozen `complete(prompt, schema)` admits **no** such parameter — asserted **exactly** (`params == ["self","prompt","schema"]`) by a frozen U4 test — and U4 must not be amended. Mirrors the **frozen `CitationValidator`** precedent: per-invocation state *"supplied at **construction** … so the frozen signature is preserved unchanged."* | BR-MEXT-4, Fold-1, NFR-MEXT-THINK-1 |
| **MEXT-D5** | **Gemini extended thinking (the PRIMARY)** | reached via the **injected `LLMClient`** — a **thinking-configured client** is just another implementation of that frozen seam | FR-PROV-5 names the *"Gemini thinking budget"*, but `GeminiAdapter`/`LLMClient` are **frozen U4**. `provider.py` already states the real client *"is wrapped to this minimal `LLMClient` seam **at composition time** (a deploy-config/secrets concern)"* — so the budget binds **there**, U4 untouched, and **U19 adds no Gemini module** (none is in its frozen module list). U19 owns + **tests the mapping offline** with a capturing double. | FR-PROV-5, Fold-1, NFR-MEXT-THINK-1 |
| **MEXT-D6** | **MCP transport** | **an INJECTED seam with a fake** — tool **handlers** are **pure functions**, tested **directly**; **no live MCP server at tier-U**; the **real protocol binding is DEFERRED** (§3) | Q2-A + Q4-A. Mirrors `LLMClient` **exactly**, and the deferral is **the same shape U4 already used** for the real Gemini client. **Every BR-MEXT-6/7/8/9 tooth lives in the handler layer**, so all are verified at **full strength with no MCP package present** (Fold-2). | FR-MEMO-5, BR-MEXT-6/7/8/9, **`MCP-TRANSPORT-DEFERRED`** |
| **MEXT-D7** | **Grounding enforcement** | the **frozen `CitationValidator`, UNCHANGED**, is the **single** enforcement point | Q7-A. It is constructed with the handed report and requires **report-membership**, so an MCP-described-but-**not-evaluated** rule is **rejected** (`citation_failure`). The retrieval-miss guard is therefore **structural, not instructional** — U19 **adds no second gate** and modifies none. | BR-MEXT-6, FM1/FM2, NFR-MEXT-GROUND-1 |
| **MEXT-D8** | **Prompt composition** | **compose, never modify** — append a **marked non-citable** supplement to U4's frozen `PromptBuilder.build()` output | `prompt_builder.py` is frozen and scoped to `MemoAgentInput` only (*"no tool fetch / no MCP re-derives what fired"*). `services.md:46` reconciles US-MEMO-5's *"live tools"* with *"supplementary descriptions only"*: live-tools governs the **descriptions**; the **citable set** stays the handed report. | Fold-4 (FD), BR-MEXT-6, NFR-MEXT-GROUND-1 |
| **MEXT-D9** | **Outlier signal access** | a **U19-local structural Protocol** `OutlierSignal = {is_outlier, outlier_score}` — **never** an `outlier_model` import | `unit-of-work-dependency.md:48` gives U19 **no `outlier-model` edge**; the frozen contract `component-methods.md:73` types it `OutlierResult?`. Satisfied **by shape** — the **U20 precedent** (*"never imported, mirrored by value"*). `None` ⇒ rule-proximity alone (FR-MEMO-7). | BR-MEXT-2, Q2-A, FD Fold-3, NFR-MEXT-SIGNAL-1 |
| **MEXT-D10** | **Test substrate** | **pytest** at **tier-U** — **injected/capturing doubles for BOTH the `LLMClient` and the MCP transport**; fixture `Rulebook` / `RuleResultReport` / decision records; **no network, no key, no Docker, no live MCP server** | The frozen U4 discipline verbatim (*"No test constructs a real Gemini client, reads a key, or touches the network"*) extended to **Claude + Ollama + MCP**. **Detector self-tests** make every structural scan non-vacuous. The `audit-store` edge runs through the **`decisions-tools` seam**, so the **Docker-guard gap stays out of U19's path**. | all component/structural targets |
| **MEXT-D11** | **Frozen-boundary guard** | **mirror** the two U4 facts locally, importing **only U4's PRODUCTION module**; **behavioral + import-discipline**, **no hash/mtime pin** | Q1-A. Importing U4's **test file** would be an unprecedented cross-unit test dependency; importing U4's **production module** is **U19's own edge**, and both facts are re-assertable from it. **Fold-1**: strictly **stronger** than U4's own test (catches import-time namespace pollution U4's test can miss under collection order). **Fold-4**: a hash pin would false-fail a **deliberate** future amendment. | BR-MEXT-11, Folds 1/4, NFR-MEXT-FROZEN-1 |
| **MEXT-D12** | **Runtime** | **Python 3.12 (pinned minor)** | Build-wide determinism pin (`.python-version` = 3.12; `pyproject requires-python ">=3.12,<3.13"`) — **reused, not re-declared**. | CON-DET-1, carry-forward |

---

## 2. No new dependencies — **the streak holds** (verified on disk 2026-07-17)

| Need | Package | Status |
|---|---|---|
| Claude secondary | `anthropic>=0.40.0` | **floored ✓ · installed `0.116.0` ✓** |
| (Claude, LangChain path) | `langchain-anthropic>=0.3.0` | **floored ✓ · installed `1.4.8` ✓** |
| Ollama showcase | `ollama>=0.3.0` | **floored ✓ · installed `0.6.2` ✓** |
| Schemas / tests | `pydantic` · `pytest` | build-wide ✓ |
| **MCP protocol** | **— none —** | **NOT floored · NOT installed → DEFERRED (§3)** |

**`requirements.txt` is NOT edited by this unit.** U18's `tech-stack-decisions.md` closes with *"No new dependencies"* and U20 held the same hard line — **U19 holds it too.**

---

## 3. `MCP-TRANSPORT-DEFERRED` — the decision recorded in full (MEXT-D6 in detail)

**Decision (Q4-A)**: U19 builds the **tool-handler layer + an injected transport seam**. The **live MCP protocol/SDK binding is deferred to composition / deploy-config (U23)**. **U19 adds no new dependency.**

### 3.1 The evidence (so a future reader need not re-derive it)

| # | Evidence | How verified |
|---|---|---|
| 1 | **No MCP library is floored** — `grep -in "mcp" requirements.txt` → **NO match** | on disk, 2026-07-17 |
| 2 | **No MCP library is installed** — `import mcp` → **NOT INSTALLED**, while `anthropic` / `ollama` / `langchain-anthropic` **are** — so **provider breadth needs nothing new; only the MCP half lacked a floor** | on disk, 2026-07-17 |
| 3 | **Anticipated but unfloored** — U4's frozen `test_provider.py` asserts `"mcp" not in _top_level_imports(provider_module)`: the **name was anticipated**, but **no package was ever floored** | frozen test, read-only |
| 4 | **The composition-deferral precedent** — frozen `provider.py`: the real client *"is wrapped to this minimal `LLMClient` seam **at composition time** (a deploy-config/secrets concern)"*. U19's transport deferral is **the same shape**, not a new pattern | frozen `provider.py` |
| 5 | **The no-new-dependency streak** — U18 (*"No new dependencies"*) and U20 both held it; U19 would be the **first** to break it — worth a **deliberate** decision, not one arriving by import | frozen artifacts |
| 6 | **The deliverable language this protects** — PROJECT-BRIEF §3 C4 (*"MCP servers expose rulebook and decisions DB as tools"*) + §9; FR-MEMO-5; US-MEMO-5 | brief / requirements |

### 3.2 ⚠️ Explicit scope — what is and is NOT outstanding

- **DELIVERED by U19**: the **two read-only tool-handler surfaces** (`rulebook-tools` + `decisions-tools`) as **pure functions** over `Rulebook` / decision records, **plus an injected transport seam** with a fake.
- **NOT delivered yet**: the **live MCP protocol binding** — the handlers exposed **over MCP** to a real client.
- **NON-BLOCKING for U19 — this is the load-bearing point**: **no U19 invariant depends on the transport.** **BR-MEXT-6** (sole citable source) · **BR-MEXT-7** (read-only) · **BR-MEXT-8** (non-fatal miss) · **BR-MEXT-9** (demographic-free) are **each fully verified at tier-U with no MCP package present** (NFR-MEXT-Fold-2) — because **every one of those teeth lives in the handler layer**, which is **where a write or a leak could actually be written**. A transport binding **cannot introduce a write or a demographic the handlers do not expose**.
- **What IS outstanding is the deliverable itself** — so *"two MCP servers"* is **not** to be read as fully done at this stage. **That is precisely why this is a named register item and not a footnote.**
- **Future options**: (a) floor an MCP SDK + bind the transport in **deploy-config (U23)**; (b) a dedicated later pass; (c) Phase 3.

---

## 4. Explicitly NOT chosen here (owned by other units / deferred — reference-not-own)

- **U4's `provider.py` / `prompt_builder.py` / `citation_validator.py` / `schemas.py`** — **imported and composed, never modified** (BR-MEXT-11). U4's `route_borderline` stub **stays not-wired**; U19 owns the **real** router at `borderline_router.py` — the exact file the frozen layout names.
- **`outlier_model`** — **not imported** (no edge); reached only as a **handed-in `OutlierSignal`** (MEXT-D9).
- **The real `LLMClient` wrapping + per-provider capability config** (**Gemini thinking budget**, Claude extended-thinking flag) + keys — **composition / deploy-config**, *already* frozen-deferred by U4 (MEXT-D5).
- **The MCP protocol binding** — **`MCP-TRANSPORT-DEFERRED`** (§3).
- **The groundedness/promptfoo target set** (and Ollama's exemption from it) — **`llm-judge` (U22)**'s tooling config; a **governance fact recorded here, not a U19 code test** (NFR-MEXT-PROVGATE-1c).
- **Tracing U19's steps** — **`observability` (U21)**, which imports U19, not the reverse.
- **The orchestrator wiring** (who calls the router, who constructs which adapter with which client) — **the caller's**, per Q2-A's handed-in pattern and U18's *"the unit owns the scorer; the orchestration is downstream"* boundary.
- **The exact `RULE_PROXIMITY_MARGIN` / `OUTLIER_SCORE_CUTOFF` values** — post-calibration **Code-Gen** realizations (the CG-OUT-Fold-1 precedent); the FD/NFR pin the **names + the fixed-constant discipline + parameterized tests**.
- **tier-B** — **N/A** (U19 never touches the corpus) and **NOT authorized**. The **`audit_store` Docker-guard gap** — **untouched**, and **out of U19's test path** by MEXT-D6/D10.
