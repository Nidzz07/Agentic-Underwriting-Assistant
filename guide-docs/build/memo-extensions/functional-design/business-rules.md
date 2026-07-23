# Business Rules — `memo-extensions` (U19, C4, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U19 `memo-extensions` · C4 · **Phase 2** · **Date**: 2026-07-17 · Stories **US-MEMO-5/6/7**.
**Nature**: `memo-extensions` owns **no rulebook rules** and **no authorization/commit path**. It is an **extension** of `memo-agent-core` along three axes — **grounding** (MCP), **routing** (borderline → extended thinking), and **provider breadth** (Claude secondary / Ollama showcase). The rules below (**BR-MEXT-\***) are **checkable** invariants, each grounded in a frozen contract, a frozen **test**, or a settled answer — **none introduces domain rule logic**, and **none re-opens a frozen artifact**. The **load-bearing** ones are **BR-MEXT-1** (deterministic, LLM-free routing), **BR-MEXT-6** (the handed report is the sole citable source), and **BR-MEXT-11** (extend-don't-modify, enforced by frozen tests).

Built on **Q1/Q2/Q3/Q7 = A**, **Q4/Q5/Q6 = N/A**, and **FD-MEXT-Fold-1..5** (plan §5.8), re-opening none.

---

## Rules

### BR-MEXT-1 — The borderline trigger is DETERMINISTIC and holds NO LLM (FR-MEMO-6 / US-MEMO-6) — **load-bearing**
`route_borderline` decides `STANDARD` vs `EXTENDED` from **two deterministic triggers only** — **rule-proximity** (within a configurable margin of a threshold, **including any REFER**) **OR** **outlier-score above cutoff**. Both are **single fixed named constants** (`RULE_PROXIMITY_MARGIN`, `OUTLIER_SCORE_CUTOFF`) — never computed per-run, never wall-clock or RNG dependent. **No LLM client, no provider, no network** in the routing path: the router is a **pure function** of `(rule_report, outlier_signal | None)`.
- **Grounded**: FR-MEMO-6 (*"Both triggers are deterministic"*); `component-methods.md:73` (*"Deterministic, provider-agnostic borderline trigger"*); requirement Q12=C (*"both triggers stay deterministic … so routing does not break the reproducibility guarantee"*); skill #3/#5; CON-DET-1.
- **Checkable**: no LLM/provider/network import under `borderline_router.py` (structural scan + self-test); the same `(report, signal)` routes identically across repeated calls; exactly one constant per trigger, each a module-level literal; a REFER report routes `EXTENDED`; boundary values **exactly at** the margin/cutoff land on the intended side, with the comparison (`<=` vs `<`) stated explicitly.

### BR-MEXT-2 — The outlier value is HANDED IN; U19 imports no `outlier-model`; `None` degrades to rule-proximity alone (FR-MEMO-7 / Q2-A / Fold-3)
The router receives an **already-computed** outlier value from the caller/orchestrator, read through a **U19-local structural Protocol** (`OutlierSignal` = `{is_outlier, outlier_score}`) satisfied **by shape** by U18's `OutlierResult`. U19 **imports no `outlier-model`** — matching the frozen edge list and **mirroring how `ui-outlier-view` reaches U18 only via R4**. `outlier_signal=None` is a **first-class, tested** input meaning *"the outlier half is unavailable"* → routing falls back to **rule-proximity alone**.
- **Grounded**: `unit-of-work-dependency.md:48` (**no `outlier-model` edge**); `component-methods.md:73` (`OutlierResult?` — the **frozen nullable** shape); FR-MEMO-7; `services.md:84` (the **API composes** and hands to MEMO); the U20 *"never imported, mirrored by value"* precedent; Q2-A.
- **Checkable**: no `outlier_model` import anywhere under `backend/memo_extensions/` (structural scan); the router accepts **any** object exposing `{is_outlier, outlier_score}` (a U19-local fake drives every test — no U18 import in tests either); `route_borderline(report, None)` returns the **same** result as the rule-proximity-only computation over that report; a U18 `OutlierResult` **satisfies** the Protocol (an interop self-test constructing it **by value**, not by import).

### BR-MEXT-3 — The routing OUTCOME is provider-agnostic; provider capability degrades at the ADAPTER, never at the trigger (FR-PROV-5 / US-MEMO-6)
The trigger's result depends **only** on `(rule_report, outlier_signal)` — **never** on which provider is active. A provider that cannot do extended thinking (**Ollama**, FR-PROV-5) **does not change the routing outcome**; it changes only how its **adapter** handles `EXTENDED`. This keeps the trigger deterministic **and** provider-agnostic, and keeps *"where supported"* an **adapter-level** fact.
- **Grounded**: FR-PROV-5 (*"The borderline routing trigger is provider-agnostic and deterministic"*); US-MEMO-6 gherkin (*"routes … **where supported**"* + *"the routing trigger is deterministic and provider-agnostic"*); `component-methods.md:73`.
- **Checkable**: the router's signature/body reference **no** provider or adapter (structural scan); the identical `(report, signal)` yields the identical `ThinkingMode` under **all three** provider selections; an Ollama adapter constructed with `EXTENDED` still **completes** (degrades) rather than raising.

### BR-MEXT-4 — `ThinkingMode` is supplied at CONSTRUCTION; no frozen signature is changed (Fold-1) — **inherited-frozen**
Every U19 adapter receives its `ThinkingMode` **at construction**, because the frozen `ProviderAbstraction.complete(prompt, schema)` admits **no** such parameter and U4 must not be amended. This **mirrors the frozen `CitationValidator`**, which takes its per-invocation authoritative state at construction *"so the frozen signature is preserved unchanged."* The **orchestrator** constructs the adapter for the mode the router returned. Gemini reaches its **thinking budget** the same way — via the **injected `LLMClient`** seam, whose real wrapping U4 **already** deferred to composition/deploy-config.
- **Grounded**: frozen `provider.py` (`complete(prompt, schema)`; `LLMClient` injected; *"wrapped … at composition time (a deploy-config/secrets concern)"*); frozen `test_provider.py::test_complete_has_no_temperature_parameter` (asserts `params == ["self","prompt","schema"]` **exactly**); the frozen `citation_validator.py` construction-time precedent; FR-PROV-5.
- **Checkable**: every U19 adapter's `complete` has parameters **exactly** `["self","prompt","schema"]` (the frozen assertion, applied to the new adapters); each adapter `isinstance(...)` the `runtime_checkable` `ProviderAbstraction`; a capturing double proves `EXTENDED` construction produces a thinking-configured outgoing request and `STANDARD` does not — **offline, no network, no key**; **U4's `provider.py` is byte-unchanged** (mtime/scan).

### BR-MEXT-5 — `temperature=0` is fixed CENTRALLY inside EVERY new adapter, for all three providers (FR-PROV-3 / TEMP0-1 / brief §8) — **inherited-frozen**
The Claude and Ollama adapters inherit U4's TEMP0-1 discipline **verbatim**: `temperature=0` is set **centrally inside the adapter**, **never** a caller-controlled per-call parameter. This holds **regardless of provider** and **regardless of `ThinkingMode`** — extended thinking **never** implies a non-zero temperature.
- **Grounded**: FR-PROV-3 (*"`temperature=0` MUST be enforced on **all** production calls regardless of provider"*); US-MEMO-7 gherkin (*"temperature=0 holds for all three"*); `unit-of-work.md:244`; frozen `provider.py` (`_PRODUCTION_TEMPERATURE = 0`, *"central; not caller-controlled"*); skill #4.
- **Checkable**: a capturing client records `temperature == 0` on **every** call from **every** adapter, in **both** thinking modes, offline (the TEMP0-1 part i precedent); no adapter's `complete` exposes a `temperature` parameter (part ii).

### BR-MEXT-6 — The handed `RuleResultReport` is the SOLE citable grounding source; MCP enriches but never cites (Q7-A / FR-MEMO-5 / failure-mode #2) — **load-bearing**
MCP may **enrich context**; a **citation may NEVER originate from an MCP retrieval**. The **frozen `CitationValidator` remains the single enforcement point, unchanged** — it is constructed with the handed report and requires every `cited_rule_id` ∈ **report** *and* ∈ **rulebook**. So a rule that exists in the rulebook (**exactly what MCP can describe**) but was **not evaluated for this applicant** fails **report-membership** → `citation_failure`. **A retrieval miss can therefore never produce an uncitable or hallucinated rule — by construction, not by instruction.**
- **Grounded**: Q7-A; `unit-of-work.md:243` (*"MCP retrieval-miss guard (cite only from handed report)"*); `services.md:46` (*"supplementary human-readable rule descriptions only … never re-deriving what fired via MCP"*); `unit-of-work-dependency.md:93`; frozen `citation_validator.py` (report-membership is **authoritative**); frozen `prompt_builder.py` (*"no tool fetch / no MCP re-derives what fired"*); brief §10 FM1/FM2; skill #8.
- **Checkable**: U19 **does not modify** `citation_validator.py` (mtime/scan); a memo citing a rulebook id **absent from the handed report** yields `citation_failure` with that id (the direct retrieval-miss test); the supplementary section is **explicitly marked non-citable** in the prompt; **no U19 code path adds an id to `cited_rule_ids`**.

### BR-MEXT-7 — Both MCP servers are READ-ONLY; neither can write (FR-MEMO-5 / SEC-4)
`rulebook-tools` and `decisions-tools` expose **read** operations only — **no** write/commit/mutate surface exists on either. Neither can reach `DecisionCommitService`, publish a rulebook version, or alter a decision record. **The human approval gate remains the only path to a committed decision** (CON-BR4, skill #2), and it is **outside** this unit entirely.
- **Grounded**: `unit-of-work.md:238` (*"two read-only servers"*); `services.md:46` (*"two servers, **read-only** … **neither can write**"*); `unit-of-work-dependency.md:93` (*"read-only grounding"*); SEC-4; skill #2.
- **Checkable**: neither server exposes a write/mutate/commit method (surface scan); no `DecisionCommitService` / write-transport / session-write import under `mcp_tools.py`; the `rules-engine` and `audit-store` edges are exercised **read-only**.

### BR-MEXT-8 — A retrieval miss is NON-FATAL: degrade to the handed report; never block, never invent (brief §10 FM2)
If an MCP retrieval fails, times out, or returns nothing, drafting **continues on the handed report alone** — the supplementary section is simply **absent**. A miss **never** blocks the memo, **never** substitutes a remembered description, and **never** relaxes BR-MEXT-6. This is exactly why MCP is *supplementary*: the **citable** set never depended on it.
- **Grounded**: `services.md:46` / `unit-of-work.md:243` (**supplementary** only); brief §10 FM2 (retrieval miss is a first-class documented failure mode); FR-MEMO-7's degradation precedent (a missing input degrades, never fails).
- **Checkable**: with **both** MCP servers unavailable, drafting still produces a valid `MemoDraftOutput` whose citations pass the frozen validator; the failure path adds **no** content to the prompt; a miss is **observable** (surfaced for U21's traces), not silent.

### BR-MEXT-9 — MCP surfaces are DEMOGRAPHIC-FREE BY CONSTRUCTION; U19 may not reintroduce what U4 deliberately excluded (CON-BR1 / FR-OUT-3 / skill #6 / Fold-5)
`decisions-tools` reads committed decision records **about other applicants**. The frozen `prompt_builder.py` states demographics are *"**deliberately excluded** … the memo prose never sees them."* A tool surface returning **raw** records would **defeat that deliberate exclusion through the back door**. Therefore **both** MCP surfaces return **demographic-free projections only** — `full_name` / `gender` / `city` are **never** in a returned field, so they are **structurally unnameable** in the supplementary context.
- **Grounded**: frozen `prompt_builder.py` (the deliberate exclusion, verbatim); CON-BR1; FR-OUT-3; brief §11.5 (*"never on demographic identifiers"*); skill #6; the U18 **BR-OUT-1** *"structurally unnameable"* precedent; Fold-5.
- **Checkable**: no `full_name` / `gender` / `city` / `.demographics` reference in any `mcp_tools.py` return path (structural scan + self-test); a **name/gender/city swap over identical financials** yields **byte-identical** supplementary context (a U19-owned swap test, on top of the external `quality-gates` bias-swap suite); the returned projections' field sets equal a declared allow-list.

### BR-MEXT-10 — Ollama is exempt from MEMO-QUALITY gates ONLY — never from the DECISION-LEVEL gates (FR-PROV-GATE-1/2 / US-MEMO-7)
**Ollama is wired but NOT tested against the acceptance-criteria memo-quality gates** — groundedness ≥4/5 (AC-6 / QA-4) and memo calibration **do not** apply to it (FR-PROV-GATE-2). **But the decision-level gates apply to ALL providers** (FR-PROV-GATE-1): **reproducibility 100%** and **bias-swap delta 0**, *"because the decision is provider-independent (CON-BR2)"*. **Claude (secondary) is fully tested** and **is** held to the memo-quality gates. *"Wired-only"* means **exempt from AC gates**, **not** untested code — the Ollama adapter is unit-tested offline like every other.
- **Grounded**: FR-PROV-2; FR-PROV-GATE-1 / FR-PROV-GATE-2; AC-6 / QA-4 (*"Gemini + Claude only; **Ollama exempt** as showcase-only"*); US-MEMO-7 gherkin; `unit-of-work.md:243–244`.
- **Checkable**: the Ollama adapter is exercised by offline unit tests (constructed, `temperature=0` asserted, XML→Pydantic parsed) but is **absent** from the promptfoo groundedness target set; **`temperature=0` and CON-BR2-TYPE hold for it identically**; the exemption is **explicit and documented**, never implicit.

### BR-MEXT-11 — EXTEND, DON'T MODIFY: U19 owns its own modules; U4's stub stays not-wired; the frozen tests stay green (F4 / Fold-2) — **load-bearing**
U19 **extends** `memo-agent-core` by **implementing its Protocol from U19's own modules** — it **modifies nothing**. **Two frozen P1 tests are the enforcement mechanism**, and **both were verified to stay green**:
- `test_only_gemini_adapter_is_present_no_claude_ollama_mcp` scans **`dir(provider_module)`** — **U4's namespace only**. U19's adapters live in `backend/memo_extensions/`, so the assertion stays true **forever**; it is precisely what **forbids** adding them to U4's file.
- `test_route_borderline_is_a_not_wired_stub` requires U4's `route_borderline` to **keep raising `NotImplementedError`**. So U19 does **not** wire U4's stub — it owns the **real** router at `extensions/borderline_router.py`, **the exact file the frozen layout names for U19**. U4's stub remains a **named marker, by frozen-test mandate**.
- **Grounded**: `unit-of-work.md:69–71` (`providers/` = a **MODULE**, *"not a unit"*; `extensions/` = the **UNIT** carrying those four files); `:17–18`; `:239–241` (*"**extend** the `provider-abstraction` module … module boundary named, **not** a separate provider unit"*); the two frozen tests; Fold-2.
- **Checkable**: the full frozen backend suite stays green with U19 added (**1011 passed / 31 skipped** baseline — **zero regression**, purely additive); **no file under `backend/memo_agent_core/` is modified** (mtime/scan); U19's `backend.*` imports are exactly `memo_agent_core`, `rules_engine`, `audit_store` — **its three frozen edges**.

### BR-MEXT-12 — Advisory-only inherited: U19 adds NO output contract and cannot alter a recommendation (CON-BR2 / CON-BR2-TYPE / skill #1)
U19 introduces **no new schema**. The LLM's output stays **`MemoDraftOutput` = `{narrative_prose, cited_rule_ids}`** — which declares **no** `recommendation`/`confidence` field, so *"the LLM changed the recommendation"* stays **unrepresentable** through **every** new provider and **both** thinking modes. Adding a provider or a routing mode **widens no authority**. All language stays **"recommendation"**, never "decision".
- **Grounded**: CON-BR2 / CON-BR2-TYPE (frozen `schemas.py`); FR-PROV-GATE-1 (*"the decision is provider-independent"*); Q6 = N/A (no contract addition); skill #1; brief §11.2.
- **Checkable**: no U19 module declares a Pydantic model or emits a `Recommendation`; `MemoDraftOutput`/`DecisionMemo` are **unmodified** (mtime/scan); QA-5 (*"a test MUST assert the LLM cannot change a recommendation"*) holds for **Claude and Ollama** exactly as for Gemini; no "decision"-as-verdict wording in U19 strings.

### BR-MEXT-13 — OUT OF SCOPE, explicitly: the memo narrative does NOT cite outlier flags (Q1-A / the `OUTLIER-IN-PROSE` register item) — **a negative rule, so Code-Gen cannot drift into it**
**In U19 the outlier value decides a routing MODE; the LLM never sees it.** No outlier data reaches the prompt, the `MemoAgentInput`, or the prose. The router reads **only** `{is_outlier, outlier_score}` (§3) — it **never** touches `flagged_features`, `shap_value`, or `provenance`, so **the minimal read surface is itself the scope guard**. The capability *"memo cites outlier flags in prose"* is **real, unassigned, and registered** as **`OUTLIER-IN-PROSE`** for a future deliberate decision — **it is not silently dropped, and not folded in here.**
- **Grounded**: the four frozen sources (plan §4.3) — module list `unit-of-work.md:238–241`; stories `stories.md:331–372`; edges `unit-of-work-dependency.md:48`; FR-MEMO-6/7 `requirements.md:122–123`. Plus §4.2: absorbing it would require a field on the **frozen `extra="forbid"` `MemoAgentInput`** owned by **U4**.
- **Checkable**: no `flagged_features` / `shap` / `provenance` reference anywhere under `backend/memo_extensions/` (structural scan); the prompt's supplementary section contains **no** outlier content; `MemoAgentInput` is **unmodified**.

---

## Rule → source traceability

| Rule | Frozen source / decision |
|---|---|
| BR-MEXT-1 | FR-MEMO-6, `component-methods.md:73`, Q12=C, CON-DET-1, skill #3/#5 |
| BR-MEXT-2 | `unit-of-work-dependency.md:48`, `component-methods.md:73`, FR-MEMO-7, `services.md:84`, U20 precedent, Q2-A, Fold-3 |
| BR-MEXT-3 | FR-PROV-5, US-MEMO-6 gherkin, `component-methods.md:73` |
| BR-MEXT-4 | frozen `provider.py` + `test_provider.py`, `citation_validator.py` precedent, FR-PROV-5, Fold-1 |
| BR-MEXT-5 | FR-PROV-3, US-MEMO-7 gherkin, `unit-of-work.md:244`, frozen TEMP0-1, skill #4 |
| BR-MEXT-6 | Q7-A, `unit-of-work.md:243`, `services.md:46`, frozen `citation_validator.py` + `prompt_builder.py`, FM1/FM2, skill #8, Fold-4 |
| BR-MEXT-7 | `unit-of-work.md:238`, `services.md:46`, `unit-of-work-dependency.md:93`, SEC-4, skill #2 |
| BR-MEXT-8 | `services.md:46`, brief §10 FM2, FR-MEMO-7 degradation precedent |
| BR-MEXT-9 | frozen `prompt_builder.py`, CON-BR1, FR-OUT-3, skill #6, U18 BR-OUT-1 precedent, Fold-5 |
| BR-MEXT-10 | FR-PROV-2, FR-PROV-GATE-1/2, AC-6/QA-4, US-MEMO-7 gherkin |
| BR-MEXT-11 | `unit-of-work.md:17–18/69–71/239–241`, the two frozen P1 tests, F4, Fold-2 |
| BR-MEXT-12 | CON-BR2 / CON-BR2-TYPE, FR-PROV-GATE-1, QA-5, Q6=N/A, skill #1 |
| BR-MEXT-13 | the four §4.3 sources, Q1-A, the `OUTLIER-IN-PROSE` register item |

**No orphan** — every U19 invariant from `unit-of-work.md:243–244` lands: **FR-MEMO-5** → BR-MEXT-6/7/8/9; **FR-MEMO-6** → BR-MEXT-1/3; **FR-MEMO-7** → BR-MEXT-2; **FR-PROV-2** → BR-MEXT-10; **FR-PROV-5** → BR-MEXT-3/4; **FR-PROV-GATE-2** → BR-MEXT-10; **MCP retrieval-miss guard** → BR-MEXT-6/8; **`temperature=0` for all three** → BR-MEXT-5. Inherited-and-not-widened: CON-BR2 → BR-MEXT-12; CON-BR1 → BR-MEXT-9; the F4 module boundary → BR-MEXT-11; the Q1-A scope line → BR-MEXT-13.

**Story coverage** (US-MEMO-5/6/7 as a set, per Q3-A): **US-MEMO-5** → BR-MEXT-6/7/8/9 (+ the adapters' structured-output breadth, BR-MEXT-4); **US-MEMO-6** → BR-MEXT-1/2/3/4; **US-MEMO-7** → BR-MEXT-5/10/12.
