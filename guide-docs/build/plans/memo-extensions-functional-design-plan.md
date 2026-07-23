# Functional Design Plan (Part 1) — `memo-extensions` (U19, C4, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U19 `memo-extensions` · C4 · **Phase 2** (the 3rd P2 unit attempted) · **Date**: 2026-07-17
**Status**: **PART 1 (PLAN) ANSWERED 2026-07-17 — Q1–Q7 filled (Q4/Q5/Q6 = N/A per Q1=A); ambiguity-check RUN → CLEAN (5 folds); Part 2 (FD artifact set) GENERATED.**
**~~⚠️ BLOCKING scope question (Q1)~~ → RESOLVED 2026-07-17 by the user: Q1=A.** The blocking finding was **accepted**: the original framing (outlier-in-prose as self-evidently in U19's scope) was **incorrect**. U19 proceeds at its **frozen scope**; the outlier-in-prose capability gap is carried as its own **named entry in the deferred-decisions register** (§4.3).

---

## 1. DISCOVER-carryover check — CLEAN ✓ (verified on disk)

| Check | Result |
|---|---|
| `guide-docs/build/memo-extensions/` | **ABSENT** ✓ |
| `guide-docs/build/plans/memo-extensions-*` | **ABSENT** ✓ (this plan is the first) |
| `backend/memo_extensions/` | **ABSENT** ✓ |

## 2. Depth — **comprehensive** (VERIFIED, not assumed)

`unit-of-work.md:245` — U19: **"Depth: comprehensive (MCP boundary, provider adapters)."**

U19 is **not** in the *lighter* candidate list at `unit-of-work.md:259–263` (that list is the display-only UI units + the pure-wiring units `secrets-config`/`admin-cli`/`deploy-config`/`observability`). Checked the same way `outlier-model`'s and `ui-outlier-view`'s classifications were checked — by reading the line, not by pattern-matching the phase.

## 3. Frozen scope of U19 — read, not re-derived (`unit-of-work.md:236–245`)

> **U19 — `memo-extensions` (C4; Phase 2) [grouped per F4]**
> - **Purpose**: Extend `memo-agent-core` with grounding + routing + provider breadth.
> - **Modules**: `mcp-tools` (two read-only servers — supplementary only), `borderline-router` (deterministic routing to extended thinking), **secondary (Claude) / showcase (Ollama) provider adapters** that **extend the `provider-abstraction` module** of `memo-agent-core` (module boundary named, **not** a separate provider unit).
> - **Stories**: US-MEMO-5, US-MEMO-6, US-MEMO-7.
> - **Key invariants**: FR-MEMO-5/6/7, FR-PROV-2/5, FR-PROV-GATE-2; MCP retrieval-miss guard (cite only from handed report). `temperature=0` holds for all three providers.

**F4 resolution — CONFIRMED still frozen** (checked, not assumed): `unit-of-work.md:69–71` places `providers/` as a **MODULE of memo-agent-core — "not a unit"**, and `extensions/` as the **UNIT** carrying `mcp_tools.py` · `borderline_router.py` · `provider_secondary.py` · `provider_showcase.py`. `unit-of-work.md:17–18` restates it: *"`provider-abstraction` is a **module of `memo-agent-core`**, not a unit."* The secondary/showcase adapters **extend** that module from inside U19. **The F4 grouping stands.**

**Frozen dependency edges** (`unit-of-work-dependency.md:48`): `memo-extensions` (2) → **`memo-agent-core`, `rules-engine` `R`, `audit-store` `R`**. Purpose column: *"extends provider module; MCP read-only grounding (supplementary)"*.

### 3.1 What U19 builds ON (read on disk this session; re-derived none)

| Frozen artifact | What it fixes for U19 |
|---|---|
| `memo_agent_core/provider.py` (U4) | `ProviderAbstraction` Protocol — `complete(prompt, schema) -> MemoDraftOutput`, **no temperature parameter** (TEMP0-1 part ii: `temperature=0` fixed **centrally inside each adapter**, never caller-controlled). `GeminiAdapter` takes an **injected client** (`LLMClient` seam) so `temperature=0` is unit-tested offline. Header states Phase-2 is **named, not wired**: *"there are **no** Claude/Ollama adapters and **no** MCP here."* |
| `memo_agent_core/provider.py::route_borderline` | The **frozen Phase-2 seam**: `route_borderline(*args, **kwargs) -> ThinkingMode`, raising `NotImplementedError("...not wired in Phase 1")`. **Untyped signature** — see **Q2**. |
| `memo_agent_core/schemas.py::ThinkingMode` | `STANDARD` / `EXTENDED` — *"a **named Phase-2 seam** (`memo-extensions`); NOT wired in Phase 1 (FR-MEMO-6/7)"*. U19's router returns this. |
| `memo_agent_core/schemas.py::MemoAgentInput` | `{applicant_profile, rule_report, recommendation, confidence}` — **frozen=True, extra="forbid"**. **NO outlier field.** |
| `memo_agent_core/schemas.py::MemoDraftOutput` | `{narrative_prose, cited_rule_ids}` — **CON-BR2-TYPE**: no `recommendation`/`confidence` field, so "the LLM changed the recommendation" is *unrepresentable*. |
| `memo_agent_core/schemas.py::DecisionMemo` | `{narrative_prose(L), cited_rule_ids(L), missing_information(D), recommendation(RO), confidence(RO), memo_hash(M), model_version(M)}`, frozen. **No outlier field.** |
| `memo_agent_core/prompt_builder.py` | **ADVISORY-1 is enforced by PROMPT ONLY today**: the system template instructs *"Always use the word 'recommendation'; never call it a 'decision'"*. There is **no post-generation prose scan** in U4. |
| `memo_agent_core/citation_validator.py` | The **hallucination guard** — a **post-generation** validation of `cited_rule_ids` against the rulebook → `CitationValidationResult{all_valid, offending_cited_ids, outcome}`. **So U4's precedent has BOTH shapes: prompt-only for vocabulary, post-validation for citations.** |
| `outlier_model/schemas.py` (U18) | `OutlierResult{outlier_score, is_outlier, flagged_features[], provenance}`; `FlaggedFeature{feature, z_score, shap_value, direction}` — `shap_value` **REQUIRED (no default)**, so "zero unexplained flags" holds **by schema construction**. **No verdict field** (advisory-only). |
| `PROJECT-BRIEF.md §3 C4` | *"Memo must cite: every triggered rule by ID, confidence level, missing documents list, **outlier flags**"*. |
| `services.md:81–84` | The assembled end-state: *"C3 Outlier shown for the assembled end-state — **Phase 1 omits the OUT calls and drafts from rule_report**"*, then `API->>OUT: score profile + corpus_version` → `OUT-->>API: OutlierResult + SHAP` → **`API->>MEMO: draft profile + rule_report + outlier_result`**. |

---

## 4. ⚠️ BLOCKING FINDING — the outlier-in-prose premise is NOT in U19's frozen scope

**This must be resolved before the FD can be scoped. I am flagging, not improvising.**

The request frames U19 as *"the first unit where an LLM-authored narrative must reference outlier data"*, with `OutlierResult` as *"the new input this unit's memo drafting must now be able to cite"*. **The frozen decomposition does not say that.** Four independent frozen sources agree:

1. **U19's module list** (`unit-of-work.md:238–241`) is `mcp-tools` · `borderline-router` · `provider_secondary` · `provider_showcase`. **No outlier-citation module.**
2. **U19's three stories** are US-MEMO-5 (MCP tools + provider adapters), US-MEMO-6 (borderline routing), US-MEMO-7 (secondary/showcase providers). **None mentions prose citation of outlier data.** (Read in full at `stories.md:331–372`.)
3. **U19's dependency edges** (`unit-of-work-dependency.md:48`) are `memo-agent-core`, `rules-engine` `R`, `audit-store` `R`. **There is NO `outlier-model` edge.** By contrast `observability` (`:50`) and `llm-judge` (`:51`) *do* carry explicit `memo-extensions`/`outlier-model` edges, and `ui-outlier-view` (`:49`) carries an explicit *(orchestrated)* `outlier-model` `R` edge. The omission is not an oversight pattern — the matrix names outlier edges where they exist.
4. **The one real outlier↔U19 link is FR-MEMO-6/7 — a DETERMINISTIC ROUTING TRIGGER, not prose.** FR-MEMO-6: *"Borderline = rule-proximity ... **OR outlier-flag above cutoff**. **Both triggers are deterministic**."* FR-MEMO-7: *"The outlier-driven half of the borderline trigger depends on the outlier model; **until it lands, routing runs on rule-proximity alone**."* US-MEMO-6's Gherkin says the same. **In U19's frozen scope the outlier value decides a routing MODE; the LLM never sees it.** U18 has now landed, so this half can finally be enabled — that is the genuine, in-scope U18→U19 consequence.

### 4.1 So where does "the memo cites outlier flags" actually live?

**Nowhere, currently.** It is a real brief-level capability (`PROJECT-BRIEF §3 C4`; `services.md:84`) that has fallen between the units:

- **`memo-agent-core` (U4)** — **frozen and complete**, built before U18 existed. `MemoAgentInput` has **no outlier field**; the module has **zero** `outlier` references anywhere; its FD calls `rule_report` the **"sole grounding source"** (`domain-entities.md:119`) and U4's unit definition says *"Cites strictly from the handed `RuleResultReport`"* (`unit-of-work.md:156`).
- **`memo-extensions` (U19)** — modules/stories/edges don't include it (§4 above).
- **`ui-outlier-view` (U20)** — renders `R4.outlier` in **React**; frozen and complete. Not prose.

`services.md:81` shows this was **deliberate, not forgotten**: outlier→memo was drawn as the *assembled end-state* with Phase 1 explicitly omitting it. But **no unit was ever assigned the job of closing it.**

### 4.2 Why this can't be quietly absorbed into U19

Handing `outlier_result` to the LLM requires a field on **`MemoAgentInput`** — the type the prompt is built from. That type is **frozen, `extra="forbid"`, and owned by U4, a frozen P1 unit your standing guardrail forbids touching** (*"do not touch memo-agent-core (U4) or any other frozen P1 unit"*). So the premise as stated **collides with your own hold**. That collision is precisely why this is a decision for you and not a judgement call for me.

### 4.3 ⚑ REGISTER ENTRY — `OUTLIER-IN-PROSE` (NEW named open item, opened 2026-07-17 by Q1=A)

> **Logged, not folded into U19; not silently dropped.** Carried as its **own named entry** in the
> deferred-decisions register — the same treatment as the composition-root's **Q1-B
> READ_AUDIT-vs-WIRE-1 divergence**, which is carried as its own item rather than being resolved
> inside whatever pass happened to surface it.

| Field | Value |
|---|---|
| **Name** | **`OUTLIER-IN-PROSE`** — "the LLM-authored memo narrative cites outlier flags" |
| **Status** | **OPEN — unassigned to any unit.** Awaiting a future *deliberate* decision. |
| **Opened** | 2026-07-17, at U19's FD Part 1, by the Q1=A resolution |
| **Real?** | **Yes** — `PROJECT-BRIEF §3 C4` ("Memo must cite: … **outlier flags**") and `services.md:84` (`API->>MEMO: draft profile + rule_report + outlier_result`) both name it. It is a **genuine capability gap**, not a documentation error. |
| **Why NOT U19** | The four frozen sources in §4 (below) |
| **Why not silently absorbable** | Requires a field on the **frozen, `extra="forbid"` `MemoAgentInput`** owned by **U4** (a frozen P1 unit under a standing do-not-touch hold). See §4.2. |
| **Future options (all deliberate, none pre-judged)** | (a) a **new unit**; (b) a **U4 amendment** considered **on its own merits** with the hold explicitly lifted; (c) **Phase 3**. |
| **Deliberate deferral, not an oversight** | `services.md:81` drew outlier→memo as the **assembled end-state** with *"Phase 1 omits the OUT calls and drafts from `rule_report`"* — the omission was intentional; **no unit was ever assigned the job of closing it.** |

**The four cited sources that PROVE it is out of U19's scope** (recorded here verbatim so a future reader need **not** re-derive the finding):

| # | Source | What it says |
|---|---|---|
| 1 | **Module list** — `unit-of-work.md:238–241` | U19's modules are `mcp-tools` · `borderline-router` · `provider_secondary` · `provider_showcase`. **No outlier-citation module.** |
| 2 | **Stories** — `stories.md:331–372` | US-MEMO-5 (MCP + provider adapters) · US-MEMO-6 (borderline routing) · US-MEMO-7 (secondary/showcase providers). **None mentions prose citation of outlier data.** |
| 3 | **Dependency edges** — `unit-of-work-dependency.md:48` | U19 → `memo-agent-core`, `rules-engine` `R`, `audit-store` `R`. **NO `outlier-model` edge.** The matrix **names outlier edges where they exist** (`:49` `ui-outlier-view` *(orchestrated)* `outlier-model` `R`; `:50` `observability`; `:51` `llm-judge`) — so the omission is **not** an oversight pattern. |
| 4 | **FR-MEMO-6/7 text** — `requirements.md:122–123` | *"Borderline = rule-proximity … **OR** outlier-flag above cutoff. **Both triggers are deterministic**"*; *"until it lands, routing runs on **rule-proximity alone**"*. The **one** real outlier↔U19 link is a **deterministic routing trigger, not prose** — the outlier value decides a routing **MODE**; **the LLM never sees it.** |

**The genuine, in-scope U18→U19 consequence** (what *did* change when U18 landed): FR-MEMO-7's outlier-driven **half of the borderline trigger** can finally be **enabled**. That is routing, not narration.

---

## 5. `[Answer]` questions

> Every question in full, lettered options, with a recommendation where I have grounds for one. **Q1 is BLOCKING — Q4/Q5/Q6 are conditional on it and are marked so.** **ANSWERED 2026-07-17 — Q1/Q2/Q3/Q7 = A; Q4/Q5/Q6 = N/A (rendered inapplicable by Q1=A).**

### Q1 — **[BLOCKING]** Is "the memo narrative cites outlier flags" in U19's scope at all?

Per §4 the frozen decomposition assigns U19 **MCP tools + borderline-router + provider adapters**, with outlier appearing **only** as FR-MEMO-6's deterministic routing trigger. The capability you described is real and unassigned, but adopting it here means amending frozen artifacts.

- **(A) NO — U19 proceeds at its frozen scope** (MCP + borderline-router + provider adapters; outlier used **only** as the FR-MEMO-6/7 routing trigger, which U18's landing now enables). "Memo cites outlier flags in prose" is logged as a **separate, named open scope gap** for you to decide independently (new unit / U4 amendment / Phase 3), and this FD does **not** touch it. **(Recommended)** — it is the only option that re-opens no frozen artifact, honours your "don't touch U4 / don't touch frozen P1" hold, and keeps U19's story-map assignment (US-MEMO-5/6/7) intact. It also leaves the gap *visible* rather than silently absorbed.
- **(B) YES — amend U19's frozen scope to add outlier-citation.** Requires, at minimum: re-opening `unit-of-work.md` (module list + a new `outlier-model` dependency edge), **and** amending the frozen `MemoAgentInput`/`DecisionMemo` in U4 (or building a parallel U19-owned input type that bypasses U4's "sole grounding source" invariant). **Directly contradicts your standing do-not-touch-U4 hold** — I will not do this without you explicitly lifting that hold.
- **(C) DEFER the whole U19 unit** and resolve the outlier-in-prose scope gap first, since it may change U19's shape.

**[Answer]**: **A** — the original framing that prompted this FD (treating outlier-in-prose citation as self-evidently in U19's scope) **was incorrect, and that correction is accepted**. U19 proceeds at its **frozen scope** (MCP tools + borderline-router + provider adapters); outlier data is used **only** as FR-MEMO-6/7's **deterministic routing trigger**, now enabled because U18 has landed. "Memo cites outlier flags in prose" is a **real, currently-unassigned capability gap** — logged as a **separate, explicitly named open item in the deferred-decisions register** (**`OUTLIER-IN-PROSE`**, §4.3) — **not folded into U19's scope, not silently dropped** — for a future deliberate decision (a new unit, a U4 amendment considered on its own merits, or Phase 3). This is the **same treatment as the composition-root's Q1-B divergence**, which is carried as its own named open item rather than resolved inside whatever pass happened to surface it.

### Q2 — How does the outlier flag reach `route_borderline`, given U19 has **no** `outlier-model` dependency edge?

FR-MEMO-6's outlier trigger needs an outlier value, but `unit-of-work-dependency.md:48` gives U19 no `outlier-model` edge, and the frozen seam `route_borderline(*args, **kwargs)` is **untyped** — it pins no answer. `services.md:84` shows the **API composing** `outlier_result` and handing it to MEMO, which is consistent with "no direct edge". This question stands **regardless of Q1**.

- **(A) HANDED IN — the router receives an already-computed outlier value** (a score/flag, or `None`) from the caller/orchestrator; U19 **imports no `outlier-model`**, matching the frozen edge list and mirroring how `ui-outlier-view` reaches U18 only via R4. FR-MEMO-7's "until it lands, rule-proximity alone" degrades naturally to `None`. **(Recommended)** — the only option consistent with the frozen matrix as written.
- **(B) DIRECT READ — U19 imports `outlier-model` and scores.** Contradicts the frozen dependency matrix and would need it amended; also duplicates orchestration.
- **(C) Flag it as a genuine gap in the frozen matrix and stop for a decomposition amendment.**

**[Answer]**: **A** — **handed in**; the router receives an **already-computed outlier value** from the caller/orchestrator; **U19 imports no `outlier-model`**, consistent with the frozen dependency matrix and **mirroring how `ui-outlier-view` reaches U18 only via R4**. FR-MEMO-7's *"until it lands, rule-proximity alone"* **degrades naturally to `None`**.

> **Post-answer corroboration found during the ambiguity-check** (strengthens A; changes nothing): the plan called the seam *untyped*, which is true of the **Python stub** — but the **frozen C4 contract** `component-methods.md:73` **does** type it: **`route_borderline(rule_report, outlier_result) -> ThinkingMode` · `(RuleResultReport, OutlierResult?)` → `ThinkingMode`**, described as the *"Deterministic, provider-agnostic borderline trigger (rule-proximity OR outlier cutoff)"*. The **handed-in, nullable** shape is therefore **frozen, not merely inferred** — and the `?` **is** FR-MEMO-7's degradation. The *typed-as-`OutlierResult`* vs *imports-no-outlier-model* tension is resolved at **FD-MEXT-Fold-3** (§5.8).

### Q3 — Is the provider-abstraction extension (secondary/showcase adapters) genuinely in this pass, or separable?

`unit-of-work.md:238–241` groups all three concerns into U19 **[per F4]**, and US-MEMO-7 (FR-PROV-2 / FR-PROV-GATE-2) is one of U19's three assigned stories. Splitting it would leave a story unassigned mid-flight.

- **(A) IN SCOPE — the FD covers all three module groups** (mcp-tools, borderline-router, provider adapters) as one comprehensive FD, exactly as F4 grouped them; Code-Gen may still sequence them internally. **(Recommended)** — F4 grouped them deliberately, and the story map assigns US-MEMO-5/6/7 to U19 as a set; dropping one silently would break the "all 40 stories assigned exactly once" proof.
- **(B) SEPARABLE — FD covers MCP + router now; provider adapters deferred** to a later pass within U19 (US-MEMO-7 explicitly parked, story map annotated).
- **(C) Provider adapters FIRST**, MCP + router deferred (US-MEMO-7 is the lowest-dependency third).

**[Answer]**: **A** — **in scope**; the FD covers **all three module groups** (mcp-tools, borderline-router, provider adapters) as **one comprehensive FD**, exactly as **F4 grouped them** and as the story map assigns **US-MEMO-5/6/7 as a set**. **Code-Gen may sequence them internally.**

### Q4 — *(CONDITIONAL on Q1=B)* The enforcement surface for advisory-only framing **inside LLM prose**

You correctly identify that there is no React prop signature to lean on here. **The frozen U4 precedent already contains both candidate shapes**: `prompt_builder.py` enforces advisory vocabulary by **prompt instruction only**, while `citation_validator.py` enforces citation integrity by **post-generation validation**. So this is a choice between two *existing* project patterns, not an invention. *(If Q1=A, this question is moot for U19 — the LLM never receives outlier data — and should travel with the scope gap instead.)*

- **(A) BOTH — prompt constraint + a post-generation validation gate.** The prompt instructs the model never to use verdict language about outlier flags; a post-generation scan then **verifies** the emitted `narrative_prose`, mirroring how `citation_validator` verifies `cited_rule_ids` rather than trusting the prompt. **(Recommended if Q1=B)** — the hard constraint (advisory-only) is exactly the class where U4 already chose *verify, don't trust*; a prompt alone is an unverified claim about a non-deterministic component.
- **(B) PROMPT ONLY** — consistent with U4's current ADVISORY-1 treatment of vocabulary; lighter, but unverified.
- **(C) POST-GENERATION GATE ONLY** — verified, but wastes a cheap prompt-side constraint and turns every violation into a late failure.
- **(D) Reuse the frontend's `FORBIDDEN_TERMS` word-list as the backend gate's source.** *(Note: this would create a cross-stack coupling the project has so far avoided — `ui-shell`'s list is a **frontend** artifact. Flagging as a real design consequence, not a recommendation.)*

**[Answer]**: **N/A — correctly rendered INAPPLICABLE by the Q1=A resolution.** Q4 was explicitly *(CONDITIONAL on Q1=B)*. Under Q1=A **the LLM never receives outlier data**, so there is no outlier-verdict-language surface in U19 to enforce. **Deliberately left unanswered — no placeholder content embedded and none carried into the FD.** The question **travels with the `OUTLIER-IN-PROSE` register entry** (§4.3) and becomes live only if that item is ever resolved toward (a) or (b).

### Q5 — *(CONDITIONAL on Q1=B)* How does zero-unexplained-flags translate into U19's citation discipline?

U18 makes "zero unexplained flags" hold **by schema construction** — `FlaggedFeature.shap_value` is **required, no default**, so a flag cannot exist without its SHAP value. The question is whether the *memo prose* inherits a matching obligation, the way `cited_rule_ids` must be traceable to a real rule ID.

- **(A) NEW BR-level invariant, mirroring the rule-citation guard** — if the narrative mentions a flagged feature, it must cite that feature's SHAP-backed explanation, validated post-generation against the handed `OutlierResult.flagged_features` (a structural sibling of `citation_validator`). **(Recommended if Q1=B)** — it is a *new* obligation on a *new* data class, not a restatement of the rule-citation guard.
- **(B) EXTENSION of the existing citation invariant** — generalize `citation_validator` to validate both rule IDs and flagged-feature references under one guard.
- **(C) NEITHER — U18's schema guarantee is sufficient**; the memo may reference flags freely because every flag it could reference already carries SHAP.

**[Answer]**: **N/A — correctly rendered INAPPLICABLE by the Q1=A resolution.** Q5 was explicitly *(CONDITIONAL on Q1=B)*. Under Q1=A the memo prose **never references a flagged feature**, so no prose-level citation obligation on `OutlierResult.flagged_features` arises in U19. **Deliberately left unanswered — no placeholder content embedded and none carried into the FD.** Travels with the **`OUTLIER-IN-PROSE`** register entry (§4.3).

### Q6 — *(CONDITIONAL on Q1=B)* Does U19 need its own frozen output-contract addition?

Mirrors the WIRE1-Fold-4 question for R4. `DecisionMemo.narrative_prose` is free text and could carry outlier discussion with **no schema change** — but then the outlier citation is unstructured and unvalidatable, unlike `cited_rule_ids`.

- **(A) NO schema change — `narrative_prose` is a sufficient free-text carrier.** Lightest, but makes Q5's citation guard hard to enforce (nothing structured to validate against).
- **(B) YES — add a structured `cited_outlier_features[]` (or equivalent) to `MemoDraftOutput`/`DecisionMemo`**, mirroring `cited_rule_ids`, so the Q5 guard has a structured target. **Requires amending frozen U4 schemas** — same hold collision as Q1=B.
- **(C) U19-owned extension type** that composes `DecisionMemo` without modifying it (extend-not-replace, honouring F4's "extend the module" spirit).

**[Answer]**: **N/A — correctly rendered INAPPLICABLE by the Q1=A resolution.** Q6 was explicitly *(CONDITIONAL on Q1=B)*. Under Q1=A **U19 adds no field to any output contract** — `MemoDraftOutput` / `DecisionMemo` are consumed **frozen and unchanged**, and `ThinkingMode` (already frozen in U4's `schemas.py`) is the router's return type, **not a new addition**. **Deliberately left unanswered — no placeholder content embedded and none carried into the FD.** Travels with the **`OUTLIER-IN-PROSE`** register entry (§4.3).

### Q7 — The MCP "supplementary only" guard — what exactly is being guarded?

`unit-of-work.md:242–243` pins *"MCP retrieval-miss guard (cite only from handed report)"*, and `unit-of-work.md:156–157` (U4) says *"MCP is supplementary only (that path is Phase 2, in `memo-extensions`)"*. `unit-of-work-dependency.md:93` restates: *"read-only grounding, supplementary only"*.

- **(A) The handed `RuleResultReport` remains the SOLE citable grounding source; MCP may enrich context but a citation may NEVER originate from an MCP retrieval** — so a retrieval miss can never produce an uncitable/hallucinated rule. The existing `citation_validator` remains the single enforcement point, unchanged. **(Recommended)** — this is the literal reading of both frozen phrases and preserves U4's "sole grounding source" invariant intact.
- **(B) MCP retrievals are citable but must be cross-validated** against the handed report before citation.
- **(C) Flag as ambiguous and stop for a decision.**

**[Answer]**: **A** — the **handed `RuleResultReport` remains the SOLE citable grounding source**; **MCP may enrich context but a citation may NEVER originate from an MCP retrieval**, so a **retrieval miss can never produce an uncitable or hallucinated rule**. The **existing `citation_validator` remains the single enforcement point, unchanged.**

> **Post-answer corroboration found during the ambiguity-check** (gives A **structural teeth**, not prompt-hope): the frozen `CitationValidator` is **constructed with the handed report** and requires every cited id to be a **member of that report** *and* of the active `Rulebook`. So a rule that exists in the rulebook — i.e. one MCP could describe — but was **not evaluated for this applicant** is **rejected** (`citation_failure`) **by the frozen gate**, with no change to it. Q7-A is therefore **enforced by construction**, not by instruction. See **FD-MEXT-Fold-4** (§5.8).

---

## 5.8 MANDATORY AMBIGUITY-CHECK — RUN 2026-07-17 against the filled answers + the frozen contracts → **CLEAN (5 folds; no surface-and-stop)**

Checked against: `unit-of-work.md`, `unit-of-work-dependency.md`, `component-methods.md`, `stories.md`, `requirements.md`, `services.md`, `memo_agent_core/provider.py` + `schemas.py` + `prompt_builder.py` + `citation_validator.py` + **`tests/test_provider.py`**, `outlier_model/schemas.py`. **Two frozen P1 tests were read this session and are decisive (Fold-2).**

### FD-MEXT-Fold-1 — **LOAD-BEARING** — `ThinkingMode` cannot ride `complete()`; it is supplied at **construction**
`ProviderAbstraction.complete(prompt, schema)` carries **no thinking parameter**, and the frozen test `test_provider.py::test_complete_has_no_temperature_parameter` asserts the signature **exactly**: `params == ["self", "prompt", "schema"]`. So the mode the router returns **cannot** be threaded through `complete`, and U4 cannot be amended to add it.
**Resolved by the frozen `CitationValidator` precedent — the identical shape, in this unit's own parent**: *"The authoritative grounding source … is supplied at **construction** … so the frozen signature is preserved unchanged."* U19's adapters therefore take their `ThinkingMode` **at construction**; the orchestrator constructs the adapter for the mode the router returned. **No frozen signature changes.**
**Extends cleanly to Gemini (the PRIMARY) without touching U4** — FR-PROV-5's *"Gemini thinking budget"* clause is reachable because **`LLMClient` is an INJECTED seam** and `provider.py` already states the real client *"is wrapped to this minimal `LLMClient` seam **at composition time** (a deploy-config/secrets concern)"*. A thinking-configured client is **another `LLMClient` implementation**, selected at construction — so the frozen `GeminiAdapter` gets extended thinking **by injection**, not by modification, and U19 adds **no Gemini module** (none is in its frozen module list). The **capability/config binding** lands where U4 **already** frozen-deferred the real client (deploy-config / composition) — exactly as the Gemini API key does. U19 owns and **tests the mapping offline** with a capturing double (the **TEMP0-1 part i** precedent: *"a capturing test double records the outgoing request; no network, no key"*).

### FD-MEXT-Fold-2 — **LOAD-BEARING** — the two frozen P1 tests **ENFORCE** extend-don't-modify; they do **not** collide with U19
A frozen test literally named `test_only_gemini_adapter_is_present_no_claude_ollama_mcp` asserts *"no Claude, no Ollama, no MCP"* — which is **U19's entire job to add**. **Verified, not assumed — both tests stay green:**
- It scans **`dir(provider_module)`** where `provider_module` is **`backend.memo_agent_core.provider`** — U4's namespace **only**. U19's adapters live in **`backend/memo_extensions/provider_secondary.py`** / `provider_showcase.py` / `mcp_tools.py` — **different modules**. The assertion stays true **forever**, and it is precisely what **forbids** U19 from adding its adapters **into U4's file**.
- `test_route_borderline_is_a_not_wired_stub` asserts U4's stub **keeps raising `NotImplementedError`**. So U19 must **NOT** wire U4's stub; it owns the **real** router at **`extensions/borderline_router.py`** — **the exact file the frozen layout `unit-of-work.md:70–71` names for U19**. U4's stub remains a **named marker**, by frozen-test mandate.

**Consequence**: the frozen test-suite is the **enforcement mechanism** for the F4 architecture, not an obstacle. U19 **extends from its own modules; it modifies nothing.**

### FD-MEXT-Fold-3 — the frozen contract types the param `OutlierResult?` while Q2-A forbids importing `outlier-model`
`component-methods.md:73` types the trigger `(RuleResultReport, OutlierResult?) -> ThinkingMode`, but `unit-of-work-dependency.md:48` gives U19 **no `outlier-model` edge** and **Q2-A** says *"U19 imports no outlier-model"*.
**Resolved by the U20 precedent** (the immediately-prior unit, same frozen-U18-shape situation): *"`outlier-model` (U18) untouched and **never imported** — reached only `(orchestrated)` via R4; its nine feature names **mirrored by value**"*. U19 therefore reads the outlier value through a **U19-local structural Protocol** over the **minimal** surface the router needs — satisfying the frozen contract **by shape**, creating **no edge**, importing **nothing**. FR-MEMO-7's degradation is the contract's own **`?`** → `None`.

### FD-MEXT-Fold-4 — MCP enrichment vs the frozen `PromptBuilder` (scoped to `MemoAgentInput` and nothing else)
`prompt_builder.py` is frozen and builds **only** from `MemoAgentInput` — its docstring: *"**no tool fetch / no MCP** re-derives what fired (retrieval-miss guard)"*. Yet US-MEMO-5 wants drafting *"grounded in live tools rather than memorised content"*.
**Both hold, via the more-specific frozen resolution** `services.md:46`: `rulebook-tools` provides *"**supplementary human-readable rule descriptions only** — the memo cites strictly from the handed `RuleResultReport`, never re-deriving what fired via MCP"*. "Live tools not memorised content" governs the **descriptions**; the **citable set** stays the handed report.
**Realized by composition, not modification**: U19 **appends** an explicitly-marked **non-citable** supplementary section to the string U4's frozen `build()` returns. **Q7-A then gets structural teeth from the frozen gate** (see Q7's corroboration): an MCP-described-but-not-evaluated rule id is **rejected by `CitationValidator`** because it fails **report-membership**. The retrieval-miss guard is **enforced**, not instructed.

### FD-MEXT-Fold-5 — `decisions-tools` could **reintroduce demographics that U4 deliberately excluded** (no user decision — the compliant path is forced)
U19's second MCP server exposes the **decisions DB** (via its `audit-store` `R` edge), whose records concern **other applicants**. The frozen `prompt_builder.py` states: *"Demographic identifiers (name, city, gender) are **deliberately excluded** from the prompt — bias-free by design; the memo prose never sees them."* A `decisions-tools` surface returning **raw** decision records would **defeat that deliberate exclusion** through the back door — violating **CON-BR1** / **FR-OUT-3** / brief §11.5 / underwriting-rules skill **#6**.
**Not a question for the user** — a hard constraint admits only the compliant path: the MCP tool surfaces are **demographic-free by construction**, encoded as **BR-MEXT-9** with a checkable scan. Flagged here because it is a **real, non-obvious consequence** of adding a decisions-DB tool to a pipeline that had deliberately excluded demographics — surfaced rather than silently handled.

**Verdict: CLEAN.** No genuine gap requires a user decision. All five folds resolve against a **frozen artifact, frozen test, or an established project precedent** — **none by improvisation**, none re-opening anything. → **Part 2 generated.**

---

## 6. HOLDS (binding on any Part 2)

- **`memo-agent-core` (U4, frozen P1) NOT touched** — U19 **extends** it (imports `ProviderAbstraction`, `ThinkingMode`, `MemoDraftOutput`); it does not modify or replace it. **Q1=B / Q6=B would violate this hold and are therefore blocked on your explicit instruction.**
- **`outlier-model` (U18, frozen) and `ui-outlier-view` (U20, frozen) NOT touched.** All 17 frozen P1 units NOT touched. The closed composition root NOT touched. **WIRE-1 NOT touched.**
- **`temperature=0` holds for all three providers** — fixed **centrally inside each adapter**, never a caller-controlled parameter (the frozen TEMP0-1 discipline U19's new adapters must inherit).
- **No LLM in the deterministic path** — the borderline router is **deterministic** (FR-MEMO-6: *"Both triggers are deterministic"*); it must not call an LLM to decide routing.
- **Advisory-only** — no output of this unit may finalise an outcome; CON-BR2 / CON-BR2-TYPE stand (`MemoDraftOutput` carries no `recommendation`/`confidence`).
- **tier-B NOT authorized**; the `audit_store` Docker-guard gap NOT touched; **no other unit started.**
- **No code, no FD artifact** until this plan's answers are filled, the ambiguity-check runs, and Part 2 is explicitly authorized.

## 7. Gate — **PART 1 COMPLETE; PART 2 GENERATED; STOPPED at the FD 2-option completion gate**

- [x] **(1)** Q1–Q7 answered — **Q1/Q2/Q3/Q7 = A**; **Q4/Q5/Q6 = N/A** (correctly rendered inapplicable by Q1=A; no placeholder content embedded).
- [x] **(2)** **`OUTLIER-IN-PROSE`** logged as a **new named entry** in the deferred-decisions register (§4.3), with the **four proving sources cited**.
- [x] **(3)** Mandatory **ambiguity-check RUN** → **CLEAN**, 5 folds (§5.8), no surface-and-stop.
- [x] **(4)** **Part 2 GENERATED** at **comprehensive** depth — the 3-artifact FD set at `guide-docs/build/memo-extensions/functional-design/`, mirroring the P1 comprehensive units' structure.
- [ ] **(5)** **FD 2-option completion gate — AWAITING USER.** (1. Request Changes / 2. Continue to Next Stage → NFR Requirements.)

**Q1 is RESOLVED (=A)**: U19's FD covers **three** module groups — its frozen scope. The outlier-citation capability is **out of scope and separately registered**, not absorbed.

**STOPPED — no code, nothing under `backend/memo_extensions/`.** NFR Requirements does **not** begin until the gate is answered.
