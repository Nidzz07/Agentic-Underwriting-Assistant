# NFR Design — Plan (Part 1) — `memo-extensions` (U19, C4, **Phase 2**)

**Stage**: BUILD → per-unit loop → **NFR Design Part 1 (Plan)** · **Unit**: U19 `memo-extensions` · C4 · **Phase 2** · **Depth**: **comprehensive** · **Date**: 2026-07-17
**Built ON** the **frozen FD** (**BR-MEXT-1..13**; the four-module inventory; the **`OutlierSignal`** Protocol; the **construction-time** thinking-mode mechanism; the MCP boundary) **and** the **approved NFR Requirements** (**fifteen `NFR-MEXT-*`**; the load-bearing **ROUTE-1**/**FROZEN-1** pair + **GROUND-1**; **`MCP-TRANSPORT-DEFERRED`**; folds **NFR-MEXT-Fold-1..4**) — **re-opening neither.** **NFR Requirements APPROVED 2026-07-17 (option 2, Continue → NFR Design).**

**Status**: **PART 1 ANSWERED 2026-07-17 (Q1–Q3 all A, embedded §5) → ambiguity-check RUN (§5.5) → CLEAN (3 folds) → Part 2 GENERATED** (`nfr-design-patterns.md` + `logical-components.md`). **STOPPED at the NFR Design 2-option completion gate.** Full Q&A embedded per the standing convention. **No code; `backend/memo_extensions/` NOT created.**
**§0's premise correction is retained below as part of the PERMANENT record** (at the user's explicit instruction) — not merely as one turn's exchange.

**Backend Python unit** — "component relationship" = **module/class relationships + Python data flow**, per the U18 convention (not a JSX component tree).

---

## 0. ⚠️ PERMANENT RECORD — one premise corrected before it propagated into a pattern name
> **Retained deliberately at the user's instruction (2026-07-17)**: this correction is **part of the permanent record**, not a transient turn. It is **why** `P-MEXT-1` is not named `ReadOnlySeamPattern`, **why** `P-MEXT-7` is the only pattern here that legitimately carries a ui-history-style surface argument, and **why** `P-MEXT-8` is openly test-only.

> Your brief cites *"outlier-model's **ReadOnlySeamPattern** — no import exists to call, not just a scan proving none was called"*. **Verified on disk — two corrections, and the second one changes what I can honestly promise for ROUTE-1:**

1. **`ReadOnlySeamPattern` is not U18's — it is `ui-history`'s (U9, §P3), a FRONTEND unit.** U18's patterns are `P-OUT-1..9`: `AllowlistProjectionPattern` · `SeedLocalDeterminismPattern` · `ImputeThresholdCompositionPattern` · `SoleExplainerConstructionPattern` · `ScoreFlagExplainCompositionPattern` · `DualSourceSeamPattern` · `VersionAnchoredProvenancePattern` · `StructuralGuardPattern` · `ReferencedObservedBoundaryPattern`. **None is named `ReadOnlySeamPattern`.** I will not cite a pattern by a name the artifact does not carry.
2. **The mechanism you describe does not exist for Python imports — not even in U18.** `ui-history`'s ReadOnlySeamPattern works because a **JS module's exported surface** can simply **omit** a write builder — the capability is absent because *nothing exports it*. **U18's own "no LLM / no write / no DB" guarantee is `P-OUT-8 StructuralGuardPattern` — i.e. a SCAN**, precisely the thing your brief contrasts against. That is not an oversight: **Python cannot make an import structurally impossible** — any module may `import anything` at any time. There is no type, signature, or module structure that forecloses it.

**What this means for `NFR-MEXT-ROUTE-1`, stated honestly**: Python affords by-construction guarantees for **data** (a typed projection whose type has no field for the forbidden thing — `P-OUT-1`) and for **surface** (what a class/module exposes — the `ui-history` shape). It affords **none for imports**. So the router's *signature* genuinely makes a provider **un-injectable** (no client parameter exists to pass one), but "no LLM **import** exists to call" can only be enforced by a **scan**. **Q1 asks which scan** — and offers a **strictly stronger** form than U18's denylist: an **import ALLOW-LIST**, which mirrors the project's real allow-list lineage (`ALLOWED_INPUT_FIELDS`, `OUTLIER_FEATURE_FIELDS`) rather than U18's `no-write/LLM/DB` denylist.

**I am flagging this rather than quietly naming a pattern `ReadOnlySeamPattern` and implying a guarantee Python does not provide.**

---

## 1. Unit context

### 1.1 What this stage decides
**HOW** each `NFR-MEXT-*` target is **structurally met** — the named **design patterns** + the **logical components** (module/class surfaces + **exact signatures**) that carry each guarantee, plus the **reference-not-own** discipline and **component→target** coverage. It decides **no functional behavior** (frozen FD) and **no new target** (approved NFR Requirements). **No code.**

### 1.2 The by-construction philosophy for THIS unit (inherited from U18's Q1-A, restated with §0's correction)
A "by-construction" guarantee in Python is realized through: **(i) typed/frozen structures where the forbidden thing is unrepresentable** (U18's `FeatureInputs`; here: the **`OutlierSignal`** narrowness + a **demographic-free projection type**); **(ii) signatures that admit no path** (no client parameter ⇒ a provider **cannot be injected**); **(iii) injected dependencies** (the `LLMClient`, the MCP transport) so ambient state is never reached; **(iv) `StructuralGuard` AST/import scans + detector self-tests** as the **regression layer** — and, for **imports**, the **only** layer (§0); **(v) header comments as documentation only — NEVER enforcement.**

### 1.3 Frozen substrate carried in (NOT re-opened)
BR-MEXT-1..13 · the four modules (`borderline_router.py` · `mcp_tools.py` · `provider_secondary.py` · `provider_showcase.py`) · `OutlierSignal = {is_outlier, outlier_score}` · construction-time thinking (incl. Gemini-by-injection) · the MCP **supplementary / read-only / demographic-free** boundary · the fifteen `NFR-MEXT-*` · Folds 1–4 · **`MCP-TRANSPORT-DEFERRED`**.

---

## 2. NFR Design execution plan (checkboxes)
- [x] **P1. Unit context + the §0 premise correction** — DONE (this plan; §0 retained as the **permanent record**).
- [x] **P2. Collect the three `[Answer]:` tags** (§5 — **Q1–Q3 all A**) + run the **mandatory ambiguity-check** (§5.5 — **CLEAN, 3 folds**, incl. the **user-flagged** `compose_prompt`-vs-BR-MEXT-7 check).
- [x] **P3. Generate `nfr-design-patterns.md`** — `P-MEXT-1..11`, each with its target(s) + tier + rigor; the load-bearing pair + GROUND-1 spelled out with **actual mechanisms**; validated Mermaid + text alternative; traceability (no orphan).
- [x] **P4. Generate `logical-components.md`** — `C-MEXT-1..6` with responsibilities, ownership, **exact signatures**; the **four-category** reference-not-own check; component→target coverage (no orphan); validated Mermaid + text alternative; settled items held.
- [ ] **P5. NFR Design 2-option completion gate — AWAITING USER.**

---

## 3. Draft pattern map — `P-MEXT-1..11` (every one of the fifteen targets covered)

| # | Pattern | Mechanism (the by-construction argument, or an honest "test-only") | Target(s) | Tier / Rigor |
|---|---|---|---|---|
| **P-MEXT-1** | **PureFunctionRoutingPattern** *(load-bearing)* | **Signature-level (real):** `route_borderline(rule_report, outlier_signal=None) -> ThinkingMode` is a **module-level pure function** with **no client/provider/adapter parameter** — so a provider is **structurally un-injectable**; there is no argument to pass one through. **Import-level (scan-only, §0):** an LLM call would require a **new top-level import**, caught by the `StructuralGuard`. **Q1 decides denylist vs the strictly-stronger import ALLOW-LIST.** Returns the frozen `ThinkingMode` enum — the function **cannot** return a provider-specific value. | **ROUTE-1** | structural + component / **full (highest)** |
| **P-MEXT-2** | **MirroredBoundaryAssertionPattern** *(load-bearing)* | **The exact import is `from backend.memo_agent_core.provider import route_borderline` + `import backend.memo_agent_core.provider as provider_module`** — **production only**; **no `backend.memo_agent_core.tests.*` import anywhere** (scanned). **The two re-asserted behaviors**: **(1)** `route_borderline()` **raises `NotImplementedError`** (U4's stub stays a stub); **(2)** `dir(provider_module)` contains **no** name matching `Claude`/`Ollama`/`Mcp`/`MCP`. Per **Fold-1** this is **strictly stronger** than U4's own test (it runs where U19 **is** imported, catching import-time namespace pollution U4's test can miss under collection order). Per **Fold-4**: **behavioral + import-discipline only — NO hash/mtime pin.** | **FROZEN-1** | component + structural / **full (highest)** |
| **P-MEXT-3** | **SoleCitationGatePattern + AppendOnlyPromptComposition** | **The frozen `CitationValidator` is the SINGLE structural gate** — constructed with the handed report, requiring **report-membership**; U19 **adds no second gate and modifies it not at all**. **The append point**: `base = PromptBuilder().build(agent_input)` → `prompt = base + SUPPLEMENT_MARKER + block` — **U4's output is never parsed, edited, reordered or re-templated; only appended to** (string-append, downstream of `build()`). **Q3 decides which component owns the append + the marker.** | **GROUND-1** | component + structural / full |
| **P-MEXT-4** | **ConstructionTimeInjectionPattern** | **Exact constructors** (mirroring the frozen `CitationValidator` precedent): `ClaudeAdapter(client: LLMClient, *, model: str, thinking_mode: ThinkingMode = ThinkingMode.STANDARD)` and `OllamaAdapter(client: LLMClient, *, model: str, thinking_mode: ThinkingMode = ThinkingMode.STANDARD)`. **`complete(self, prompt, schema) -> MemoDraftOutput`** — **exactly** `["self","prompt","schema"]`, **no** `thinking_mode`, **no** `temperature` (both frozen-asserted). `temperature=0` is a **module-level private constant read inside `complete`** — never a parameter (TEMP0-1 part ii **by signature**). **AGNOSTIC-1**: the router's signature contains **no provider**, so the routing outcome **cannot** vary by provider — a **signature-level** guarantee, not a test-level one. | **THINK-1**, **AGNOSTIC-1**, **TEMP0-1** | component + structural / full |
| **P-MEXT-5** | **MinimalSurfaceProtocolPattern** | **The Protocol's own narrowness IS the guard**: `OutlierSignal` declares **exactly** `is_outlier: bool` + `outlier_score: float`. `flagged_features` / `shap_value` / `provenance` are **not members of the router's input type**, so they are **structurally unreachable** — `signal.flagged_features` is an **attribute that does not exist on the declared type** (a type error, not a lint finding). This is the **U18 `FeatureInputs` mechanism applied to the router's input** (P-OUT-1's real lineage). **Q2 decides `runtime_checkable`.** | **SIGNAL-1**, **SCOPE-1** | component + structural / full |
| **P-MEXT-6** | **AsymmetricDemographicFreedomPattern** (Q3-A + Fold-3) | **`rulebook-tools` — by construction, no test needed**: `describe_rules(rule_ids: Sequence[str]) -> list[RuleDescription]` — **no applicant-shaped parameter exists in the signature**, so an applicant (and therefore a demographic) **cannot enter**. **Strictly stronger than a swap test that could not fail.** **`decisions-tools` — by construction + swap-tested**: returns a **frozen `PrecedentSummary` with no `full_name`/`gender`/`city`/`demographics` field** (the `FeatureInputs` analog — a demographic is **unrepresentable in the return type**), with the **output-projection swap teeth** (records differing **only** in demographics → **byte-identical** projection) as the **regression layer on a design-level guarantee** (Fold-3). | **BIAS-1** | structural + component / full |
| **P-MEXT-7** | **ReadOnlyHandlerSurfacePattern** | **The exposed surface omits write entirely** — the closest true analog to `ui-history`'s ReadOnlySeamPattern, and it **does** work here because it is about a **class surface**, not an import: both handler classes expose **only** read methods; there is **no** `commit*`/`write*`/`persist*`/`update*` member to call, and **no request-body/mutation builder exists**. Per **Fold-2**, the handler surface **is** the "server" at this stage — **where a write could actually be written** — so a deferred transport **cannot introduce a write the handlers do not expose**. | **MCPRO-1** | structural / full |
| **P-MEXT-8** | **NonFatalDegradationPattern** *(honestly test-only)* | **This one is behavioral, and I will not dress it as structural.** "A miss degrades rather than blocks" is a property of **control flow** (the supplement is optional; a failure yields an empty block, never an exception escaping to the draft path) — **no type or signature can encode it**. The **structural half that DOES exist**: the supplement is a **separate append** (P-MEXT-3), so the citable set **never depended on it** — the degradation is *possible* by design. The guarantee itself is **teeth**: both handlers unavailable → a valid `MemoDraftOutput` still results, citations still pass the frozen gate. | **MISS-1** | component (teeth) / full |
| **P-MEXT-9** | **NoNewContractPattern** | **U19 declares no Pydantic model at all** — so `MemoDraftOutput` remains the model's only output type, and it **declares no `recommendation`/`confidence` field** ⇒ a recommendation-change is **unrepresentable** through **every** new provider and **both** modes (CON-BR2-TYPE inherited, not re-implemented). A `StructuralGuard` scan asserts **zero `BaseModel` subclasses** and **zero `Recommendation`-producing paths** under `backend/memo_extensions/` (+ self-test). | **CONTRACT-1** | structural / full |
| **P-MEXT-10** | **StructuralGuardPattern** (one substrate, mirroring U18's `P-OUT-8`) | One substrate of independent scans, **each with a mandatory detector self-test** (non-vacuous): **router import discipline** (Q1) · **no-`outlier_model`-import** (SIGNAL-1) · **no-outlier-field-reference** (`flagged_features`/`shap_value`/`provenance` — SCOPE-1) · **no-demographic-read** over both handler modules (BIAS-1) · **no-write member / no `DecisionCommitService` import** (MCPRO-1) · **no-Pydantic-model / no-`Recommendation`** (CONTRACT-1) · **U19's `backend.*` imports ⊆ {`memo_agent_core`, `rules_engine`, `audit_store`}** + **no `memo_agent_core.tests.*` import** (FROZEN-1) · **no `cited_rule_ids` append** (GROUND-1). | **SCOPE-1** + the structural halves of ROUTE/FROZEN/SIGNAL/BIAS/MCPRO/CONTRACT/GROUND | structural / full |
| **P-MEXT-11** | **ReferencedObservedBoundaryPattern** (mirroring `P-OUT-9`) | **PROVGATE-1**: Ollama **is** unit-tested offline (constructed, `temperature=0`, parsed) — its **exemption from the promptfoo set is `llm-judge` (U22) tooling config**, a **governance fact recorded, not a U19 code test**. **PERF-1**: observed/soft, **no hard SLO**; nothing to time at tier-U (every provider + transport is a double). **SEC-1**: the Security-Guardrails table — enforced by review + the P-MEXT-10 scans. **Not over-specified.** | **PROVGATE-1**, **PERF-1**, **SEC-1** | referenced / observed / governance |

**No orphan (15/15)**: ROUTE→P1 · FROZEN→P2 · GROUND→P3 · THINK/AGNOSTIC/TEMP0→P4 · SIGNAL→P5 (+P10) · SCOPE→P5+P10 · BIAS→P6 · MCPRO→P7 · MISS→P8 · CONTRACT→P9 · PROVGATE/PERF/SEC→P11.

---

## 4. Draft logical components — `C-MEXT-1..6`

| # | Component | Module | Responsibility / ownership | Signatures that carry the guarantee |
|---|---|---|---|---|
| **C-MEXT-1** | **`BorderlineRouter`** | `borderline_router.py` | The deterministic, provider-agnostic trigger. **Owns** `RULE_PROXIMITY_MARGIN` + `OUTLIER_SCORE_CUTOFF` (one module-level literal each) and the `OutlierSignal` Protocol. | `route_borderline(rule_report: RuleResultReport, outlier_signal: OutlierSignal \| None = None) -> ThinkingMode` — **no client/provider parameter exists** (P-MEXT-1); `class OutlierSignal(Protocol)` with **exactly** `is_outlier` + `outlier_score` (P-MEXT-5) |
| **C-MEXT-2** | **`RulebookTools`** *(handler surface 1)* | `mcp_tools.py` | Read-only **supplementary rule descriptions** from the active `Rulebook` (`rules-engine` `R`). | `describe_rules(rule_ids: Sequence[str]) -> list[RuleDescription]` — **no applicant-shaped parameter exists** ⇒ demographic-free **by construction** (P-MEXT-6); **no write member** (P-MEXT-7) |
| **C-MEXT-3** | **`DecisionsTools`** *(handler surface 2)* | `mcp_tools.py` | Read-only **demographic-free precedent** from committed decision records (`audit-store` `R`), through an **injected record-source seam**. | `recent_precedent(query: PrecedentQuery) -> list[PrecedentSummary]`; **`PrecedentSummary` frozen with NO `full_name`/`gender`/`city`/`demographics` field** (P-MEXT-6 — the `FeatureInputs` analog); **no write member** (P-MEXT-7) |
| **C-MEXT-4** | **`ClaudeAdapter`** (secondary, **tested**) | `provider_secondary.py` | The Claude Opus 4.8 fallback; implements the frozen `ProviderAbstraction`. | `__init__(client: LLMClient, *, model: str, thinking_mode: ThinkingMode = STANDARD)`; `complete(self, prompt: str, schema: type[MemoDraftOutput]) -> MemoDraftOutput` (**exactly** 3 params); `model_version -> str` (P-MEXT-4) |
| **C-MEXT-5** | **`OllamaAdapter`** (showcase, **wired-only ≠ untested**) | `provider_showcase.py` | The local showcase; same Protocol, same central `temperature=0`; may not support extended thinking → **degrades at the adapter, never at the trigger**. | identical constructor + `complete` shape (P-MEXT-4); **exempt from memo-quality gates only**, never decision-level (P-MEXT-11) |
| **C-MEXT-6** | **`StructuralGuard` substrate** *(test-only)* | `tests/` | The single substrate of AST/import scans + **mandatory detector self-tests**; **not a runtime dependency**. | the eight scans of **P-MEXT-10** |

*(The **`McpTransport`** seam is an **injected Protocol with a fake at tier-U**; its real protocol binding is **`MCP-TRANSPORT-DEFERRED`** — composition/deploy-config, not a U19 component.)*

### 4.2 Reference-not-own — **four distinct categories, kept separate** (as instructed)

| Category | Members | Discipline |
|---|---|---|
| **1. Consumed by import — U19's OWN frozen edges** | **`memo_agent_core`** (`ProviderAbstraction`, `LLMClient`, `GeminiAdapter`, `ThinkingMode`, `MemoDraftOutput`, `PromptBuilder`, `CitationValidator`) · **`rules_engine`** (`RuleResultReport`, `Rulebook`) `R` · **`audit_store`** (decision records) `R` | **exactly** the three edges of `unit-of-work-dependency.md:48`; imported, used verbatim, **re-declared none**, **modified none** |
| **2. NOT imported — reached BY SHAPE** | **`outlier-model` (U18)** — via the U19-local **`OutlierSignal`** Protocol | **no import, no edge**; the U20 *"never imported, mirrored by value"* discipline; the interop self-test builds `OutlierResult` **by value** |
| **3. MIRRORED, not imported** | **U4's two test facts** (`route_borderline` raises; `dir(provider_module)` has no Claude/Ollama/MCP name) — **re-asserted locally against U4's PRODUCTION module** | **no `memo_agent_core.tests.*` import** (scanned); no double-collection; no coupling to U4 test names (Q1-A) |
| **4. DEFERRED to composition** | the **MCP protocol transport** (`MCP-TRANSPORT-DEFERRED`) · the **real `LLMClient` wrapping** + per-provider capability config (**Gemini thinking budget**, Claude extended-thinking flag) + keys | **already frozen-deferred by U4** (*"wrapped … at composition time (a deploy-config/secrets concern)"*); injected seams + fakes at tier-U |

### 4.3 Component → target coverage (no orphan)

| Component | Targets met | Patterns |
|---|---|---|
| `BorderlineRouter` | ROUTE-1, SIGNAL-1, AGNOSTIC-1, SCOPE-1 | P-MEXT-1/4/5 |
| `RulebookTools` | MCPRO-1, BIAS-1 (by-construction half), GROUND-1 (supplement source) | P-MEXT-6/7/3 |
| `DecisionsTools` | MCPRO-1, BIAS-1 (swap-tested half), MISS-1 | P-MEXT-6/7/8 |
| `ClaudeAdapter` | THINK-1, TEMP0-1, CONTRACT-1, AGNOSTIC-1 | P-MEXT-4/9 |
| `OllamaAdapter` | THINK-1, TEMP0-1, CONTRACT-1, PROVGATE-1 | P-MEXT-4/9/11 |
| `StructuralGuard` | FROZEN-1, SCOPE-1 (+ structural halves of ROUTE/SIGNAL/BIAS/MCPRO/CONTRACT/GROUND) | P-MEXT-2/10 |
| *(referenced/observed)* | PERF-1, SEC-1 | P-MEXT-11 |

### 4.4 Planned Mermaid (module-relationship; validated to the 7 rules; rectangle-only)
Both guarantees you asked to be **visible graph properties** are expressible as **blocked edges** (the U18 `DEMO -.blocked.-> FI` convention): a **`llm provider client`** node with a **blocked** edge into `BorderlineRouter` (**no-LLM-in-routing**), and a **`write or commit path`** node with a **blocked** edge into both handler surfaces (**no-write-in-handlers**). Nodes: `RPT` · `SIG` · `RTR` · `MODE` · `RBT` · `DCT` · `SUP` · `PB` · `PROMPT` · `ADP` · `DRAFT` · `CV` · `GUARD` · `LLMX` · `WRX`. All-alphanumeric IDs, quoted labels, **no hyphens/semicolons/colons/parentheses/special characters**, balanced fence, **rectangle-only** + text alternative.

---

## 5. Clarifying questions (fill each `[Answer]:`; full text, lettered options)

### Q1 — `NFR-MEXT-ROUTE-1`: the router's import discipline — **denylist scan (U18's actual shape) or an import ALLOW-LIST (strictly stronger)?**

**Context (see §0).** The signature half is settled and genuinely by-construction: `route_borderline(rule_report, outlier_signal=None) -> ThinkingMode` has **no client parameter**, so a provider **cannot be injected**. What remains is the **import** half — and **Python offers no structural mechanism**, so this is a **scan**, exactly as U18's own `P-OUT-8` is. The real choice is **which scan**:

- **(A) IMPORT ALLOW-LIST** — assert `borderline_router.py`'s **top-level import roots are a SUBSET of an explicit allow-list** (`__future__`, `typing`, `enum`/`dataclasses`, `backend.memo_agent_core.schemas` for `ThinkingMode`, `backend.rules_engine.report_schema` for the report type, U19-local) — **+ a detector self-test** feeding a synthetic `import anthropic` and asserting it is **flagged**. **Strictly stronger than a denylist**: it fails on **any** unforeseen import — including an LLM reached **transitively** through an innocuous-looking module, and including packages nobody thought to blacklist. It mirrors the project's genuine **allow-list lineage** (`ALLOWED_INPUT_FIELDS`, `OUTLIER_FEATURE_FIELDS`) rather than U18's denylist. **(Recommended)** — the router is a **small, stable, dependency-poor** module, which is exactly where an allow-list is cheap; and ROUTE-1 is **load-bearing** (skill #3: *no LLM in the deterministic path*), so the strongest available mechanism is warranted.
- **(B) DENYLIST scan** — forbid `anthropic`/`ollama`/`google`/`httpx`/`requests`/`socket`/provider/adapter imports (+ self-test). **Exactly U18's `P-OUT-8` shape**, so maximally consistent with precedent — but it only catches what it enumerates, and a transitive LLM path through an unlisted module would pass.
- **(C) BOTH** — allow-list on the router (load-bearing) + denylist across the rest of `backend/memo_extensions/`. Most coverage; two mechanisms to maintain, and the allow-list already implies the denylist **for the router**.

**[Answer]**: **A** — **the import allow-list**; asserting `borderline_router.py`'s **top-level import roots are a SUBSET of an explicit allow-list**, plus a **detector self-test** feeding a synthetic `import anthropic` and asserting it is **flagged**. **Strictly stronger than a denylist** since it catches **any** unforeseen import, **including a transitive LLM path through an innocuous module**. The router is **small and dependency-poor** — exactly where an allow-list is cheap — and **ROUTE-1 is load-bearing**, so the strongest available mechanism is warranted. A

### Q2 — `OutlierSignal`: `@runtime_checkable` Protocol with an `isinstance` assertion, or static-typing only?

**Context.** `NFR-MEXT-SIGNAL-1(b)` requires an **interop self-test** proving a **real U18 `OutlierResult`, constructed BY VALUE (never imported)**, **satisfies the Protocol structurally**. How that assertion is *written* depends on this choice. **The frozen precedent is directly on point**: U4 declares **`@runtime_checkable class ProviderAbstraction(Protocol)`** and its own test asserts **`isinstance(fake, ProviderAbstraction)`** — the exact shape U19 needs. (Python ≥3.12 supports `isinstance` against data-member Protocols; the project pins **3.12**.)

- **(A) `@runtime_checkable`, with `isinstance` used in TESTS ONLY** — the interop self-test reads `assert isinstance(built_by_value_outlier_result, OutlierSignal)`, a **direct, non-vacuous** structural proof; the U19-local fake is checked the same way. **Production stays duck-typed** (no runtime `isinstance` gate in `route_borderline` — that would add a check the frozen contract never asked for). **(Recommended)** — mirrors U4's **`@runtime_checkable` + `isinstance`-in-test** precedent exactly, and gives SIGNAL-1(b) its cleanest possible expression.
- **(B) `@runtime_checkable` + a production `isinstance` guard** at the router boundary — rejects a malformed signal loudly at runtime. But it adds an **unrequested runtime gate** to a pure function, and a `TypeError`/raise path in a router whose only contract is to return a `ThinkingMode`.
- **(C) Plain `Protocol` (static typing only)** — no `runtime_checkable`. The interop self-test then must assert **`hasattr`** on the two members, which is a **weaker, hand-rolled** restatement of what `isinstance` already does — and diverges from U4's precedent for no gain.

**[Answer]**: **A** — **`@runtime_checkable` Protocol with `isinstance` used in TESTS ONLY.** The interop self-test asserts `isinstance(built_by_value_outlier_result, OutlierSignal)` as a **direct, non-vacuous structural proof**; **production stays duck-typed**, with **no runtime `isinstance` gate added to the pure router function**. Mirrors **U4's own frozen `ProviderAbstraction` Protocol + isinstance-in-test precedent exactly.**

> **VERIFIED on the real interpreter this session (not assumed)** — `python 3.12.10`: `isinstance(fake, OutlierSignal)` → `True`; `isinstance(not_a_signal, OutlierSignal)` → `False` (**discriminating, not vacuous**); and a **frozen Pydantic model built BY VALUE** in the U18 `OutlierResult` shape → `isinstance(..., OutlierSignal)` → **`True`**. So **SIGNAL-1(b)'s interop self-test is directly expressible** under Q2-A on this project's pinned runtime.

### Q3 — `NFR-MEXT-GROUND-1`: **which component owns the prompt append + the non-citable marker?**

**Context — this is genuinely open and the FD does not settle it.** FD Fold-4 says *"U19 **appends** an explicitly-marked non-citable supplementary section to the string U4's frozen `build()` returns"*, and `GROUND-1(c)` requires *"the supplementary section is **explicitly marked non-citable in the composed prompt**"*. But **the frozen four-module inventory has no composer module**, and U19 must not add a fifth (`unit-of-work.md:70–71` names exactly four files). **Who performs the append determines whether GROUND-1(c) is testable inside U19 at all.**

- **(A) `McpToolService` owns it — inside the frozen `mcp_tools.py`, no new module** — e.g. `supplementary_block(context: SupplementaryContext) -> str` emitting the **`SUPPLEMENT_MARKER`-prefixed, explicitly non-citable** block, plus `compose_prompt(base_prompt: str, context) -> str` returning `base + marker + block`. **U4's `build()` output is passed in and only appended to — never parsed, edited, or re-templated.** **(Recommended)** — it keeps the marker **inside U19 where GROUND-1(c) is directly testable**, adds **no** module beyond the frozen four, and matches the FD's own placement of `supplementary_context(...)` on `McpToolService`.
- **(B) The ORCHESTRATOR composes** — U19 returns only a `SupplementaryContext`; the caller does `base + block`. Consistent with Q2-A's handed-in philosophy and U18's *"orchestration is downstream"* boundary — **but then GROUND-1(c) is NOT verifiable inside U19** (U19 never sees the composed prompt), and the non-citable marker becomes the **orchestrator's** responsibility, i.e. **unowned** until the composition root is reopened (which is closed).
- **(C) A fifth U19 module** (`prompt_supplement.py`). Cleanest separation of concerns — but **adds a module the frozen layout does not name**, which is exactly the class of drift the FD's Q1 discipline exists to prevent; it would need an explicit decomposition amendment.

**[Answer]**: **A** — **`McpToolService` owns the prompt append and the non-citable marker, inside the frozen `mcp_tools.py`, with no new module** beyond the frozen four. **U4's `build()` output is passed in and only appended to — never parsed or re-templated.** This keeps **GROUND-1(c) directly testable inside U19** and matches the FD's own placement of `supplementary_context(...)` on `McpToolService`.

> **User-flagged check → resolved at NFR-ND-MEXT-Fold-1 (§5.5)**: does giving `McpToolService` a `compose_prompt` method **quietly weaken P-MEXT-7's read-only surface claim** for that same module? **No — and the answer is precise, not hand-waved.** See §5.5.

---

## 5.5 MANDATORY AMBIGUITY-CHECK — RUN 2026-07-17 against Q1–Q3 (all A) + the frozen FD + the approved NFR Requirements → **CLEAN (3 folds; no surface-and-stop)**

Checked against **BR-MEXT-1..13**; the **fifteen `NFR-MEXT-*`**; **`MCP-TRANSPORT-DEFERRED`**; folds **NFR-MEXT-Fold-1..4**; the frozen `provider.py` / `prompt_builder.py` / `citation_validator.py` / `schemas.py`; `unit-of-work.md:70–71`; `unit-of-work-dependency.md:48`; `services.md:46`; the underwriting-rules skill.

### NFR-ND-MEXT-Fold-1 — **[USER-FLAGGED]** Q3-A's `compose_prompt` on `McpToolService` vs BR-MEXT-7's read-only guarantee → **genuinely distinct; P-MEXT-7 NOT weakened — and P-MEXT-3 gets STRONGER**

**A real question deserving a precise answer, not an assurance.** Giving the *read-only* module a method that *produces* something looks, at a glance, like widening it toward "write".

**1. What BR-MEXT-7 / SEC-4 actually guards.** Its acceptance criteria name the hazard exactly: *"neither server exposes a **write / mutate / commit** method"*; *"no `DecisionCommitService` / **write-transport** / **session-write** import"*; both edges exercised **read-only**. The invariant is about **mutating persistent state through a write surface** — committing a decision, publishing a rulebook version, altering a stored record. Its root is **skill #2** (the human approval gate) and **SEC-4** (*"auditor read-only cannot reach commit"*). **The guarded object is the SYSTEM'S STATE.**

**2. What `compose_prompt` actually is.** `compose_prompt(base_prompt: str, context: SupplementaryContext) -> str` — a **pure function returning a new string**. It **persists nothing**, **touches no transport / DB / session / record**, **mutates no argument**, **has no side effect**. Nothing it returns can become state: the caller hands it to an LLM adapter, which is itself read-only w.r.t. the decision record (**CON-BR2-TYPE** ⇒ the model cannot even *represent* a recommendation change).

**3. The distinction, stated crisply.** A **"write" in the SEC-4 sense** = *a mutation of persistent state through a write surface*. A **pure string transformation** shares **none** of its properties: no persistence, no transport, no mutation, no reachable state. **`compose_prompt` cannot be a step toward a commit because there is no state for it to reach** — which is precisely why P-MEXT-7's real mechanism is *"no `commit*`/`write*`/`persist*`/`update*` member exists to call, and no write-transport import exists"*, **none of which `compose_prompt` introduces**. **The read-only surface claim stands unchanged.**

**4. The fold STRENGTHENS P-MEXT-3 (verified, not asserted).** Python's `str` is **immutable**, so `base + marker + block` **cannot** mutate U4's `build()` output **even by accident** — it necessarily returns a **new object**. **Verified on the real interpreter this session**: after the append, `base` is **unchanged** and `composed is not base` → **`True`**. So *"U4's `PromptBuilder` output is never modified"* is guaranteed **by the immutability of `str`** — a genuine **by-construction** property, not a discipline we promise to keep. **P-MEXT-3 upgrades from "we only append" to "modification is unrepresentable".**

**5. Two guards adopted so this cannot drift** (recorded into P-MEXT-7 / P-MEXT-10): **(i)** the read-only scan's forbidden-member list is defined by **SEMANTICS** (persistence / mutation / transport members + write-transport imports), **never by loose word-matching on "output-producing"** — otherwise it would false-flag `compose_prompt` and, worse, invite someone to **weaken the scan** to accommodate it; **(ii)** `compose_prompt` / `supplementary_block` are **explicitly enumerated as pure, non-persisting members** in `mcp_tools.py`'s header comment **and** asserted **side-effect-free** (same input → same output; no argument mutated), so their purity is **tested**, not assumed.

**6. One real, non-blocking consequence, disclosed.** Q3-A does give `McpToolService` **two responsibilities** (read-only data source **+** prompt composer). That is a **cohesion** observation, **not** a read-only violation — and the frozen four-module layout (`unit-of-work.md:70–71`) **leaves no fifth module** for a composer, so Q3-A is the **only** option that keeps the marker where GROUND-1(c) is testable **without amending the decomposition**. **Disclosed rather than glossed.**

**Verdict: CLEAN.** `compose_prompt` is genuinely distinct from a SEC-4 write; **P-MEXT-7's claim is not quietly weakened**, and P-MEXT-3 is strengthened.

### NFR-ND-MEXT-Fold-2 — Q3-A keeps `mcp_tools.py` free of a `prompt_builder` import (a boundary bonus, worth pinning)
`compose_prompt` takes the **base prompt as a `str` parameter** — so `mcp_tools.py` **does not import `memo_agent_core.prompt_builder`**; the **orchestrator** calls `PromptBuilder().build(...)` and hands the string in. This (a) keeps the handler module's import surface minimal, (b) means **U19 never touches U4's builder even by import**, and (c) is consistent with **Q2-A's handed-in philosophy** and U18's *"the unit owns the scorer; orchestration is downstream"* boundary. **Pinned into C-MEXT-2/3 and P-MEXT-3.**

### NFR-ND-MEXT-Fold-3 — Q1-A's allow-list must admit the router's type-only imports without weakening it
The router annotates `rule_report: RuleResultReport`. Under `from __future__ import annotations` that can be a **`TYPE_CHECKING`-only** import (no runtime import) — but the allow-list must be **explicit** either way, or a future reader will "fix" a failing scan by **widening it**. **Resolution**: the allow-list is a **small, enumerated, commented set** — `__future__`, `typing`, `enum`/`dataclasses`, `backend.memo_agent_core.schemas` (`ThinkingMode`), `backend.rules_engine.report_schema` (the report type), U19-local — **and it is a SUBSET of FROZEN-1's `backend.* ⊆ {memo_agent_core, rules_engine, audit_store}`**, so the two scans **agree by construction** rather than needing reconciliation. Note `audit_store` is **deliberately ABSENT** from the **router's** allow-list (it is `decisions-tools`' edge, not the router's) — the allow-list is therefore **tighter than the unit-level rule**, which is the point.

**Verdict: CLEAN — no genuine gap requires a decision.** Fold-1 answers the flagged check precisely **and upgrades P-MEXT-3**; Folds 2–3 pin boundaries that would otherwise be improvised at Code-Gen. → **Part 2 generated.**

---

## 6. HOLDS (binding on Part 2)

- **`memo-agent-core` (U4, frozen P1) NOT modified** — imported/composed only; **`PromptBuilder`'s output is appended to, never parsed or re-templated**; **`CitationValidator` unchanged**; U4's `route_borderline` stub **stays not-wired**; **no `memo_agent_core.tests.*` import**.
- **`outlier-model` (U18) NOT touched and NOT imported** — reached only via the `OutlierSignal` Protocol; the interop self-test builds `OutlierResult` **by value**.
- **`ui-outlier-view` (U20), WIRE-1, the closed composition root, all 17 frozen P1 units — NOT touched.**
- **No new module** beyond the frozen four (`unit-of-work.md:70–71`); **no new Pydantic model**; **no new dependency** (`requirements.txt` NOT edited).
- **No live LLM call, no key, no network, no Docker, no live MCP server** at tier-U; **`MCP-TRANSPORT-DEFERRED` stays deferred and non-blocking**.
- **`OUTLIER-IN-PROSE` stays OPEN and out of scope** (BR-MEXT-13 / SCOPE-1 / P-MEXT-5).
- **tier-B NOT authorized** (and N/A); the **`audit_store` Docker-guard gap NOT touched**; **no other unit started**; the **23-unit decomposition unchanged**.
- **Header comments document; they never enforce.** **No pattern will be named for a mechanism Python does not provide (§0).**
- **No NFR-Design artifact, no code** until the three answers are filled, the ambiguity-check runs, and Part 2 is explicitly authorized.

## 7. Gate

- [x] **(1)** **Q1–Q3 answered — all A**; full question text + answers embedded (§5) per the standing convention; **§0's premise correction retained as the permanent record**.
- [x] **(2)** Mandatory **ambiguity-check RUN** (§5.5) → **CLEAN**, 3 folds, no surface-and-stop — including the **user-flagged** check that `compose_prompt` does **not** weaken P-MEXT-7's read-only claim (**it does not; and P-MEXT-3 is strengthened by `str` immutability, verified on the interpreter**).
- [x] **(3)** **Part 2 GENERATED** — `guide-docs/build/memo-extensions/nfr-design/nfr-design-patterns.md` + `logical-components.md`.
- [ ] **(4)** **NFR Design 2-option completion gate — AWAITING USER.** (1. Request Changes / 2. Continue to Next Stage → **Infrastructure Design**.)

**STOPPED — no code, nothing under `backend/memo_extensions/`.** Infrastructure Design does **not** begin until the gate is answered.
