# Functional Design Plan — `memo-agent-core` (C4 / U4)

**Phase / Stage**: BUILD → Functional Design (per-unit, plan-then-generate)
**Cluster**: Deterministic-core cluster-FD-first — **unit 4 of 4, the LAST cluster unit**
(`intake`+`document-sanitizer` ✅, `rules-engine` ✅, `audit-store` ✅ approved 2026-07-03;
**`memo-agent-core` ← here**; **all four FDs designed before any Code-Gen**).
**Unit covered**: U4 `memo-agent-core` (C4, Phase 1) — where the **LLM finally enters**, downstream
of the deterministic results.
**Date**: 2026-07-03
**Status**: **Plan — awaiting `[Answer]:` tags.** No FD artifacts generated yet. Stop after this plan.

This plan follows `.project-guide-rule-details/build/functional-design.md`. It is the **altitude
drop to INTERNALS**: the `DecisionMemo` field-level schema (with the **read-only recommendation +
confidence**), the LangGraph memo sub-flow (draft → validate-citations → finalize), the grounding +
citation-validation rules, and `memo_hash` production. **The contract *shapes* are frozen at
Application Design (`component-methods.md` C4) — Functional Design fills the internals, it does NOT
re-open the contract shape.** This unit **consumes** what the other three cluster units produce.

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 `memo-agent-core` (U4, C4, Phase 1)
- **Purpose** (`unit-of-work.md §3` U4): draft an audit-ready, **rule-cited memo AFTER deterministic
  results exist — prose only, never touching the recommendation**.
- **Modules**: `langgraph-orchestrator`, **`provider-abstraction` (Gemini primary — a MODULE here,
  not a unit)**, `memo-schema` (XML→Pydantic), `rule-citation-validator` (hallucination guard).
- **Stories**: US-MEMO-1 (draft without altering the recommendation), US-MEMO-2 (temperature=0 +
  structured output behind provider abstraction, Gemini primary), US-MEMO-3 (cite every triggered
  rule + validate cited IDs), US-MEMO-4 (advisory-only language). Gherkin ACs in `stories.md §5`.
- **Owned invariants** (`unit-of-work.md §5`): **CON-BR2** (read-only recommendation; the LLM cannot
  change it — QA-5 asserts, in `quality-gates`), FR-MEMO-1..4, FR-PROV-1/3. Cites **strictly** from
  the handed `RuleResultReport`; **MCP is supplementary only (Phase 2, in `memo-extensions`)**.
- **Depth**: **comprehensive** (LangGraph state, structured output, determinism — invariant-bearing).

### 1.2 Frozen contract shapes (from `component-methods.md` C4 — internals only below)
- `draft(profile, rule_report: RuleResultReport, outlier_result: OutlierResult | None) ->
  DecisionMemo` — draft advisory-only prose **after** deterministic results exist; **reads
  `rule_report.recommendation` read-only**.
- `validate_citations(memo_draft, rulebook) -> CitationValidationResult` — assert every cited rule
  ID exists in the active YAML (hallucination guard).
- `route_borderline(rule_report, outlier_result) -> ThinkingMode` — **Phase 2** (borderline
  extended-thinking; named here only to mark the seam, not designed in this P1 FD).
- `DecisionMemo` = structured memo **prose** + **cited rule IDs** + **`confidence`** (Low/Med/High,
  **produced deterministically upstream in the core, received read-only** — C4 does NOT generate it)
  + an explicit **`missing_information` list** (a named output, surfaced to the underwriter).
  **No field that can alter `recommendation`.**
- **CON-BR2 (from `component-methods.md`)**: `DecisionMemo` carries **no** recommendation-override
  field; **QA-5 asserts the LLM cannot change the recommendation**. **MCP access,
  secondary/showcase providers, borderline routing are Phase 2.**

### 1.3 Carry-forward into this FD (the consumer of the whole cluster — held, not re-opened)
- **CON-BR2 is the load-bearing invariant here**: the memo drafts **PROSE ONLY** and **cannot alter
  the recommendation** — it receives the recommendation as a **read-only** field; `DecisionMemo`
  has **no** field that can change it (structural; QA-5).
- **G6 grounding**: the memo cites **ONLY** from the handed `RuleResultReport` rules-engine produced
  (`rule_results` + `recommendation` + `confidence`). **MCP `rulebook-tools` = SUPPLEMENTARY
  human-readable descriptions only — never used to re-derive/re-fetch what fired** (retrieval-miss
  guard). (MCP itself is Phase 2 / `memo-extensions`.)
- **temperature=0 + provider abstraction WITH the Gemini adapter stay in `memo-agent-core` (P1)**;
  the **secondary (Claude) / showcase (Ollama) adapters are the Phase-2 `memo-extensions` unit** —
  **NOT** this unit. This FD is **Phase-1 `memo-agent-core` only**.
- **`memo_hash`**: the memo produces `memo_hash`, which **`audit-store` persists** in the 6-tuple and
  **`ReplayService` verifies by hash** (replay **never re-drafts** the memo — it re-evaluates rules
  and verifies the memo by `memo_hash` comparison). **The `memo_hash` contract must match what
  `audit-store`'s `ReplayService` expects** (CANON-SER discipline, `audit-store` FD).
- **Deterministic `confidence` is produced UPSTREAM (rules-engine, per G2)** and enters the memo
  **read-only** — the memo does **NOT** generate confidence.
- **`missing_information` list** is an explicit `DecisionMemo` output **+** a UI element (reviewer G3).
- **LangGraph is scoped to the C4 memo sub-flow ONLY** — the deterministic pipeline
  (intake→rules→outlier) ran **before** the graph; the recommendation is **injected as immutable
  state** (the CON-BR2 structural separation, `services.md §1`).
- **SEC-1-FORENSIC boundary (from intake)**: the sanitization report / original suspicious span is
  **AUDIT-ONLY and must NEVER re-enter LLM-bound context** — `memo-agent-core` must **not ingest it**.

### 1.4 Binding constraints held through this FD (guardrails skill)
- **CON-BR2**: recommendation read-only; no LLM in the decision path; the LLM only drafts/explains.
- **temperature=0** on all production calls (FR-MEMO-2), regardless of provider (Gemini P1).
- **Full explainability / hallucination guard**: cite every triggered rule by ID; validate cited IDs
  against the YAML (FR-MEMO-3, failure mode #1).
- **Advisory-only language** (FR-MEMO-4): "recommendation", never "decision" — enforced in the
  system prompt.
- **CON-DET-1 boundary**: temperature=0 gives reproducible prose for eval, but the **memo is NOT in
  the deterministic replay equality set** (that is rules-engine's output); memo integrity on replay
  is via **`memo_hash`** (audit-store), not re-draft.
- **DATA-4**: synthetic inputs only.

### 1.5 Cluster-FD-first position (unit 4 of 4 — the consumer)
- **Consumes** `rules-engine`'s `RuleResultReport` (grounding source), the read-only `recommendation`
  + `confidence`, and the intake `ApplicantProfile` (facts, read-only).
- **Produces** the `DecisionMemo` + `memo_hash` + `model_version` that **`audit-store`** persists in
  the 6-tuple and `ReplayService` verifies — the `memo_hash`/`model_version` fields `audit-store`
  reserved (its FD §7) are **defined here**, closing the cluster contract before any Code-Gen.

---

## 2. Functional Design execution plan (checkboxes — Step 2)

Artifacts to be generated **after** answers are collected and ambiguity-checked:
`guide-docs/build/memo-agent-core/functional-design/` → `domain-entities.md`, `business-rules.md`,
`business-logic-model.md`. (No `frontend-components.md` — backend unit; the memo VIEW / missing-info
UI element are the C5 `ui-memo-view` unit.)

- [x] **P1. Analyze unit context** (§1 above — done).
- [x] **P2. Collect `[Answer]:` tags** (§3); run the mandatory ambiguity-check (§4 of the rule
  file); raise a clarification file only if any answer is vague/combined/contradictory. **DONE
  2026-07-03 — all 12 answered; ambiguity-check essentially CLEAN (no clarification file needed).
  ONE cross-answer Phase-boundary reconciliation surfaced: Q7/Q9 mention `route_borderline` /
  borderline-extended-thinking in the Phase-1 graph, but Q10 + §1.2 place borderline routing in
  Phase-2 `memo-extensions` — resolved via the settled Phase boundary (Phase-1 graph = draft →
  validate_citations → retry/finalize; route_borderline stays a NOT-wired Phase-2 seam; checkpointer
  justified by retry/durability/tracing). Plus 5 design-elaboration resolutions (see audit
  2026-07-03T15:20 entry). Awaiting explicit go to generate.**
- [x] **P3. `domain-entities.md`** — the field-by-field **`DecisionMemo`** (LLM-authored prose +
  `cited_rule_ids`; the **read-only** `recommendation` + `confidence` injected, NOT LLM-authored;
  the explicit `missing_information` list; `memo_hash` + `model_version`; **no recommendation-override
  field** — CON-BR2 structural), `CitationValidationResult`, the memo-agent input contract (what the
  agent is handed — clean artifacts only, **never** the SEC-1 forensic span). Entity/schema Mermaid
  (validated + text alternative).
- [x] **P4. `business-rules.md`** — the **grounding rule** (cite only from the handed
  `RuleResultReport`; MCP supplementary-only/Phase-2); the **citation-validation rule** (every cited
  ID in the rulebook + the report → else citation failure, memo blocked, deterministic recommendation
  stands); the **read-only-recommendation rule** (CON-BR2 — LLM cannot author it); the
  **advisory-only language rule**; the **missing_information derivation rule**; the **SEC-1-FORENSIC
  non-ingestion rule**; **temperature=0** rule. Every rule states its condition explicitly.
- [x] **P5. `business-logic-model.md`** — the **LangGraph memo sub-flow** (draft → validate_citations
  → conditional retry/finalize → `DecisionMemo` + `memo_hash`); the **immutable-recommendation state**
  model (no node can mutate it — CON-BR2 structural); the **checkpointer/interrupt** pattern (gate is
  OUTSIDE the graph); provider-abstraction + temperature=0 call path (Gemini P1); `memo_hash`
  production matching `audit-store` `ReplayService`; the Phase-2 seams (MCP, secondary/showcase,
  borderline) marked not-built. Data-flow Mermaid (validated + text alternative); invariant self-check
  table (as prior units).
- [x] **P6. Cross-consumer / cluster-closure check** — verify `DecisionMemo` + `memo_hash` +
  `model_version` match `audit-store`'s reserved fields, the grounding source matches rules-engine's
  `RuleResultReport`, and the read-only `confidence`/`recommendation` contracts hold — closing the
  4-unit cluster contract before any Code-Gen.
- [x] **P7. Guardrail compliance pass + present the standardized 2-option completion message**
  — **APPROVED at the gate 2026-07-03** (Continue to Next Stage). **The cluster-FD-first group is
  COMPLETE** — all 4 contract-bearing deterministic-core FDs designed + cross-unit-consistent.
  (CON-BR2 no-LLM-in-decision, temperature=0, hallucination guard, advisory-only, SEC-1-FORENSIC
  non-ingestion; record compliant/N/A per Security-Guardrails control). Next BUILD step = user's
  decision point (Code-Gen the cluster vs continue FD for remaining Phase-1 units) — surfaced, not
  acted on.

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These decide **internals only** — the C4 contract shapes in §1.2 stay frozen.

### A. `DecisionMemo` schema & the read-only recommendation (CON-BR2 structural)

## Question 1 — `DecisionMemo` field-by-field + the structural read-only recommendation
CON-BR2 requires the LLM structurally cannot alter the recommendation. How is `DecisionMemo` shaped?

A) **Two structurally separate regions**: (i) **LLM-authored** = `prose` + `cited_rule_ids` +
   (the rendered) `missing_information`; (ii) **injected read-only** = `recommendation` + `confidence`
   (copied through from `rule_report` by the orchestrator, **never** part of the XML→Pydantic parse
   the model fills). The schema has **no writable `recommendation` field** the model can populate —
   CON-BR2 holds **by construction** (QA-5 asserts). Plus `memo_hash` + `model_version` (metadata).
B) One flat schema the LLM fills including a `recommendation` field, validated after to equal the
   engine's (rejected — the model could author it; only a post-hoc check).
C) The LLM authors everything and a downstream step overwrites the recommendation.
D) Other (please describe after [Answer]: tag below)

[Answer]: DecisionMemo carries LLM-written prose fields (narrative, cited_rule_ids, missing_information) and READ-ONLY echo fields the LLM cannot write (recommendation, confidence — both produced upstream). The type has NO field/setter through which LLM output can alter the recommendation — structural CON-BR2 at the type level (QA-5 asserts the LLM cannot change the recommendation).

## Question 2 — How the read-only `recommendation` reaches the memo (echo vs authored)
The memo displays/cites the recommendation. How does the value get there without the LLM authoring it?

A) The orchestrator **sets `recommendation` and `confidence` on the `DecisionMemo` from
   `rule_report`** (read-only pass-through) **outside** the model's structured-output parse; the
   prompt may *show* the recommendation as context so the prose is consistent, but the **persisted
   field is the injected value**, never the parsed-from-LLM value. A validation asserts the memo's
   recommendation is identical to `rule_report.recommendation` (QA-5).
B) The LLM writes the recommendation into the XML and it is trusted.
C) The recommendation is omitted from the memo entirely.
D) Other (please describe after [Answer]: tag below)

[Answer]: The recommendation enters the memo sub-flow as IMMUTABLE injected graph state (read before the LLM runs); the LLM reads it for narration only. The COMMITTED recommendation routes around the LLM entirely (rules-engine → DecisionCommitService directly) — dual path, so even contradictory memo prose cannot change what commits. CON-BR2 structural separation.

## Question 3 — `missing_information` list derivation (G3 — explicit output)
The `missing_information` list is an explicit `DecisionMemo` output + a UI element. How is it derived?

A) **Derived deterministically from the handed inputs** — the `not_evaluated` rules + `profile.incomplete`
   + missing/`unparseable` documents in the manifest — assembled into a **structured
   `missing_information` field**; the LLM prose may *render* it but the **structured list is
   deterministic, not LLM-invented** (grounded, explainable). Surfaced to the underwriter (UI element).
B) The LLM reads the profile and free-forms a missing-info paragraph (rejected — non-deterministic,
   ungrounded).
C) Only a boolean "is-incomplete" flag, no itemized list.
D) Other (please describe after [Answer]: tag below)

[Answer]: missing_information is a structured DecisionMemo output DERIVED DETERMINISTICALLY from intake's completeness manifest + the not_evaluated rule results — NOT LLM-generated (so it's reproducible). Surfaced in the memo and as a MemoView UI element (G3).

### B. Grounding & citation validation (G6, hallucination guard)

## Question 4 — Grounding source (cite ONLY from the handed report)
FR-MEMO-3 / G6: the memo cites only from the handed `RuleResultReport`. How is grounding enforced?

A) **The prompt is built ONLY from the handed artifacts** — the `RuleResultReport` (`rule_results`
   + `recommendation` + `confidence`) + the read-only profile facts. The system prompt instructs the
   model to **cite only `rule_id`s present in the handed report**. **MCP `rulebook-tools` is NOT
   called in Phase 1** to fetch/re-derive what fired (it is Phase-2 supplementary human-readable
   descriptions only, in `memo-extensions`) — the retrieval-miss guard.
B) The model may query the rulebook/MCP to decide which rules to cite (rejected — retrieval-miss).
C) Grounding is left to prompt wording only, no structural input restriction.
D) Other (please describe after [Answer]: tag below)

[Answer]: Grounding (G6) — the memo cites ONLY from the handed RuleResultReport (the authoritative what-fired). In Phase-1 memo-agent-core there is NO MCP: grounding is report-only. MCP rulebook-tools (Phase-2 memo-extensions) provides supplementary human-readable rule DESCRIPTIONS only, never to re-derive or re-fetch what fired.

## Question 5 — Citation validation + hallucinated-citation handling (FR-MEMO-3, failure mode #1)
`validate_citations` asserts cited IDs exist. What happens on a hallucinated citation?

A) **`validate_citations` asserts every `cited_rule_id` exists in BOTH the active rulebook AND the
   handed `RuleResultReport`**. A cited ID not present → **citation failure → the memo is BLOCKED,
   not surfaced** (`services.md §6` Scenario 2); a **bounded retry** may re-draft, and if it still
   fails the memo is **flagged** while the **deterministic recommendation from C2 still stands** (the
   LLM is out of the decision path). No hallucinated rule ever reaches the underwriter.
B) Log a warning but surface the memo anyway (rejected — a hallucinated citation reaches the user).
C) Drop the offending citation silently and surface the rest (rejected — hides the failure).
D) Other (please describe after [Answer]: tag below)

[Answer]: Every cited rule_id in the drafted memo is validated against the RuleResultReport before the memo is surfaced. A cited rule_id not present in what actually fired (hallucinated/nonexistent) → citation failure → memo BLOCKED, not surfaced (services.md §6 Scenario-2 hallucination guard).

## Question 6 — SEC-1-FORENSIC non-ingestion (intake carry-forward)
The sanitization report / original suspicious span is AUDIT-ONLY and must never re-enter LLM context.
How is that guaranteed at the memo boundary?

A) **The memo agent's input contract is `clean` artifacts only** — the `ApplicantProfile` (whose
   free-text already flows as `SanitizedText.clean_text`) + the `RuleResultReport`. The
   `SanitizationReport` / `original_span` is **structurally never passed** to `memo-agent-core` (it
   travels a separate audit path to `audit-store`); the memo prompt-builder has **no reference** to
   it. Tests assert no LLM-bound payload can reference `original_span`.
B) The memo agent receives the full intake output incl. the sanitization report and is told to
   ignore it (rejected — it would be in LLM-bound context).
C) The forensic span is redacted at prompt-build time (weaker — relies on redaction, not exclusion).
D) Other (please describe after [Answer]: tag below)

[Answer]: memo-agent-core NEVER ingests the sanitization report / original suspicious span (SEC-1-FORENSIC audit-only). Its LLM-bound context contains ONLY sanitized fields + the RuleResultReport + the read-only recommendation/confidence — the neutralized injection cannot re-enter through the memo.

### C. LangGraph orchestration (scoped to C4; interrupt / checkpointer)

## Question 7 — Graph node topology (the memo sub-flow)
What are the LangGraph nodes for the memo sub-flow?

A) **`draft` → `validate_citations` → conditional: (citation failure → bounded `retry` back to
   draft, capped) OR (valid → `finalize`)** → produce `DecisionMemo` + compute `memo_hash`. The
   deterministic pipeline (intake→rules→outlier) ran **before** the graph; its outputs enter as
   state. Provider calls happen inside `draft` via the provider-abstraction (temperature=0).
B) A single node that drafts and returns (no citation-validation node).
C) A graph that also runs rules/outlier inside it (rejected — deterministic pipeline is pre-graph).
D) Other (please describe after [Answer]: tag below)

[Answer]: A memo sub-flow LangGraph (draft → validate_citations → route_borderline) scoped to C4 ONLY. The deterministic pipeline (intake/rules) ran BEFORE the graph; the human gate is EXTERNAL to the graph. The graph does not include intake/rules/commit.

## Question 8 — Recommendation as immutable graph state (CON-BR2 structural)
How is the recommendation held in the graph so no node can mutate it?

A) **`recommendation` + `confidence` enter as read-only/immutable state channels** injected before
   the graph runs; **no node writes them**, and the graph's output `DecisionMemo` has **no writable
   recommendation field**. The structural CON-BR2 guarantee lives in the state shape, not in a
   post-hoc check. (LangGraph state: the recommendation channel is input-only.)
B) The recommendation is a mutable state field nodes could overwrite, guarded by convention.
C) The recommendation is re-derived inside the graph (rejected — no rules in the graph).
D) Other (please describe after [Answer]: tag below)

[Answer]: recommendation + confidence are injected into the graph's initial state as IMMUTABLE; the state schema marks them read-only and NO node has write access. The graph's output is prose + citations + missing_information — never a recommendation. Structural CON-BR2 inside the graph.

## Question 9 — Checkpointer / interrupt pattern (the human gate is OUTSIDE the graph)
Does the graph use a checkpointer, and does it interrupt for the human approval gate?

A) **The graph uses a checkpointer** (state durability + retry + 100%-step Langfuse tracing), but
   **does NOT interrupt for the human approval gate** — the gate is **OUTSIDE** the graph
   (`services.md §1` Q6). The graph yields a **pending** `DecisionMemo`; the FastAPI pipeline hands
   the **pending recommendation + memo** to the UI, and the human gate (`DecisionCommitService`, in
   `audit-store`) is a **separate external step**. (Observability/checkpointer detail may firm up in
   NFR/Infra design.)
B) The graph interrupts and waits for the underwriter inside the graph (rejected — gate is external).
C) No checkpointer at all (weaker — loses durability/retry/tracing).
D) Other (please describe after [Answer]: tag below)

[Answer]: Checkpointer YES (for the borderline extended-thinking step / resumability); interrupt NO. The human approval gate is EXTERNAL (the DecisionCommitService gate), NOT an in-graph interrupt_after — the memo produces advisory output and finishes; the human acts outside the graph.

### D. Provider abstraction · temperature=0 · `memo_hash` · Phase boundary

## Question 10 — Provider-abstraction scope for Phase 1 (Gemini primary here; the rest is memo-extensions)
What ships in `memo-agent-core` (P1) vs the Phase-2 `memo-extensions` unit?

A) **`memo-agent-core` (P1) ships**: the **provider-abstraction interface** + the **Gemini primary
   adapter** + **central `temperature=0`** enforcement + structured **XML→Pydantic** output. **Phase-2
   `memo-extensions` (NOT this unit)**: the **secondary (Claude) / showcase (Ollama) adapters**, the
   **MCP servers**, and **borderline extended-thinking routing** (`route_borderline`, FR-MEMO-6/7).
   This FD designs the P1 scope and marks the Phase-2 seams without building them.
B) All adapters (Gemini + Claude + Ollama) + MCP ship in memo-agent-core now (rejected — that is the
   Phase-2 memo-extensions scope).
C) No provider abstraction in P1 — call Gemini directly (rejected — FR-PROV-1 abstraction).
D) Other (please describe after [Answer]: tag below)

[Answer]: Phase-1 memo-agent-core uses the provider abstraction with GEMINI at temperature 0. The secondary(Claude)/showcase(Ollama) adapters, MCP, and the borderline-router extensions are the Phase-2 memo-extensions unit — NOT this unit. (Reproducibility rests on the deterministic core + memo_hash verification, not on the LLM reproducing byte-identical prose — the memo is advisory; replay verifies it by hash, never re-drafts.)

## Question 11 — `memo_hash` production (contract match with `audit-store` ReplayService)
`audit-store` persists `memo_hash` and `ReplayService` verifies by hash (never re-drafts). How is
`memo_hash` computed so the contracts match?

A) **`memo_hash` = a hash over the CANONICAL-serialized `DecisionMemo` content** (the same CANON-SER
   discipline `audit-store` uses — stable key order, no volatile fields), computed **once at
   `finalize`**. It is handed to `audit-store` for the 6-tuple; `ReplayService` verifies the stored
   memo by **recomputing/comparing the hash** — it **never re-drafts** the memo (no LLM in replay).
   The hashed content is the memo's stable fields (prose + cited IDs + missing_information +
   recommendation + confidence), excluding volatile metadata (`timestamp`).
B) Hash a non-canonical serialization (rejected — replay could false-mismatch on ordering).
C) `audit-store` computes the hash itself (rejected — memo-agent-core owns memo_hash production).
D) Other (please describe after [Answer]: tag below)

[Answer]: memo_hash is a deterministic hash over the memo's canonically-serialized content, computed by memo-agent-core, persisted by audit-store in the 6-tuple, and VERIFIED (not re-drafted) by ReplayService. Its canonicalization aligns with audit-store's single CANON-SER convention so the hash the memo computes is the hash ReplayService checks.

## Question 12 — Memo determinism vs the replay equality set (CON-DET-1 boundary)
temperature=0 makes the prose reproducible, but is the memo in the deterministic replay equality set?

A) **No.** The **replay equality set is rules-engine's evaluation output** (`rule_results` +
   `recommendation` + `confidence`) — the memo is **NOT** part of it. temperature=0 gives
   **best-effort reproducible prose for evals/quality** (LLM-as-judge, calibration), but the memo's
   **audit/replay integrity is via `memo_hash`** (byte-identity of the committed memo), **not**
   re-drafting and **not** a deterministic equality on prose. Clean boundary: deterministic core =
   replay-compared; memo = hash-verified. (Consistent with `audit-store` FD.)
B) The memo prose IS in the replay equality set and must byte-match on re-draft (rejected —
   re-drafting is non-deterministic across engine/provider changes and violates the audit-store boundary).
C) The memo is re-drafted on replay and compared (rejected — LLM in replay, non-deterministic).
D) Other (please describe after [Answer]: tag below)

[Answer]: The memo is OUTSIDE the replay evaluation-equality-set (rule_results + recommendation + confidence). Replay re-evaluates the deterministic rules and verifies the memo by memo_hash comparison — it NEVER re-drafts the memo or calls the LLM (which would be non-deterministic). Consistent with audit-store's replay projection.

---

## 4. Constraints & settled items held (not re-opened)
- C4 contract **shapes** frozen at Application Design (`component-methods.md`) — FD fills internals
  only (`draft` / `validate_citations` / `route_borderline`; `DecisionMemo` shape with read-only
  recommendation + confidence + missing_information; **no recommendation-override field**).
- Cluster-FD-first: unit 4 of 4 (the last) — this FD **closes the cluster contract**
  (`DecisionMemo` + `memo_hash` + `model_version` match `audit-store`'s reserved fields; grounding
  matches rules-engine's `RuleResultReport`) before any Code-Gen.
- Carry-forwards (§1.3): CON-BR2 read-only recommendation (load-bearing); G6 grounding (cite only
  from the handed report; MCP supplementary/Phase-2); temperature=0 + Gemini P1 (Claude/Ollama +
  MCP + borderline = Phase-2 `memo-extensions`); `memo_hash` matches `audit-store` ReplayService;
  confidence read-only from rules-engine (G2); `missing_information` explicit output (G3); LangGraph
  scoped to the memo sub-flow, gate external; SEC-1-FORENSIC non-ingestion.
- Guardrails (§1.4): CON-BR2, temperature=0, hallucination guard, advisory-only, CON-DET-1 boundary,
  DATA-4.
- Three settled non-edits stay closed: `PROJECT-BRIEF.md`, OOS-7 README/case-study doc commitment,
  `user-journey.md`.

---

## 5. Next step (STOP here)
Fill the twelve `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory
ambiguity-check (adding a clarification file only if needed), then generate the three
`memo-agent-core` Functional Design artifacts and present the 2-option completion message. **No FD
artifacts or code are generated until the answers are in and checked.** This is the **final
cluster-FD-first unit** — on its approval, all four contract-bearing deterministic-core FDs are done.
