# NFR Design Plan (Part 1) — `memo-agent-core` (C4 / U4)

**Phase / Stage**: BUILD → NFR Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: cluster unit **4 of 4 — the LAST** (where the LLM enters) · FD ✅ → NFR Requirements ✅ (approved 2026-07-06) → **NFR Design ← here** → [Infra likely SKIP] → Code-Gen.
**Unit**: U4 `memo-agent-core` · **Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** · **Depth**: **comprehensive** (invariant-bearing; CON-BR2 load-bearing; determinism despite an LLM).
**Status**: **Plan COMPLETE — eleven `[Answer]:` tags filled (all A); ambiguity-check CLEAN (2026-07-06); Part 2 GENERATED 2026-07-06** (`nfr-design-patterns.md` + `logical-components.md`, both Mermaid validated; three folds applied — Q5 fixed total cross-source order for `missing_information` [memo_hash byte-stability, DET-2 class], `MemoHashAdapter` naming unified, shared retry-cap constant across both retry tests). **Awaiting the NFR-Design 2-option gate.**

Built **ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) + the frozen C4 contract + the **approved 15 `NFR-MEMO-*` targets** (`nfr-requirements.md`) — **re-opening none**. NFR Design selects a **named design pattern per target** and a **logical-component blueprint**; each pattern **structurally meets** its target and is verifiable against the **injected fake `ProviderAbstraction`** (no live LLM).

**Central pattern principle**: every pattern below is chosen so its target is a **structural / deterministic** property — provable against the fake, no network, no live model — mirroring intake / rules-engine / audit-store NFR Design.

---

## 1. What NFR Design builds ON (frozen — not re-opened)

- **Frozen C4 contract**: `draft`, `validate_citations`, `route_borderline` (Phase-2 seam), `ProviderAbstraction.complete` (temp=0 central).
- **Frozen FD**: three-region `DecisionMemo` (L / D / RO / M); `MemoAgentInput` (clean-only); `CitationValidationResult`; LangGraph sub-flow (draft→validate→retry/finalize, checkpointer YES / interrupt NO); `memo_hash` via shared CANON-SER.
- **Approved NFR targets**: the 15 `NFR-MEMO-*` (CONBR2-TYPE/-STATE/-COMMIT, GROUND-1, CITE-1, CITE-FAILURE, MISSINGINFO-1, HASH-1, SEC1-1, REPLAY-1, TEMP0-1, ADVISORY-1, PROV-1, PERF-1, OBS-1).
- **Reference-not-own**: rules-engine `RuleResultReport`/`evaluation_output`/`Rulebook`; intake `ApplicantProfile`; shared `backend/common/canon_ser.py` (**unchanged**) + `decimal_context`; audit-store persist/replay (`ReplayService` re-evaluates rules only, **excludes `memo_hash`**); LLM provider (injected; fake in tests); `outlier-model` `OutlierResult` (Phase 2); `memo-extensions` (Claude/Ollama/MCP/`route_borderline` — Phase 2); `observability`; `quality-gates`.

---

## 2. Draft pattern map (each `NFR-MEMO-*` → a design pattern — finalized after answers)

| Target(s) | Design pattern (draft) |
|---|---|
| CONBR2-TYPE | **Schema-unrepresentability** — the model's structured-output type declares only `narrative_prose` + `cited_rule_ids`; `recommendation`/`confidence` are `RO` on `DecisionMemo`, injected by the assembler, no setter. |
| CONBR2-STATE | **Read-only graph channel** — `recommendation`/`confidence` are input-only LangGraph state channels; no node has write access; the reducer forbids writes. |
| CONBR2-COMMIT | **No-commit-path / bypass** — the unit constructs no `DecisionCommitService`; the committed rec routes `rules-engine → DecisionCommitService` via `recommendation_id`, never from the memo. |
| GROUND-1 | **Prompt-scoping** — the `PromptBuilder` reads **only** `MemoAgentInput`; no MCP client constructed in P1. |
| CITE-1 | **Report-membership citation check** — `CitationValidator` asserts every `cited_rule_id ∈ RuleResultReport` (authoritative) + belt-and-suspenders `∈ rulebook`; pure function. |
| CITE-FAILURE | **Bounded-retry policy in the graph** — capped retry edge; the **scripted call-count-aware fake** exercises **both** directions (recover-within-cap → finalize; exhaust-cap → flag, recommendation stands). |
| MISSINGINFO-1 | **Deterministic derivation** — `MissingInfoDeriver` maps the 3 signals (DocumentManifest MISSING/UNPARSEABLE, `RuleStatus.NOT_EVALUATED`, `profile.incomplete`) → `MissingInformationItem{source, detail}`; no LLM. |
| HASH-1 | **Local `CanonSerAdapter`** — compute `memo_hash` at `finalize` by delegating to the **unchanged shared `canon_ser`**; hashed content = stable fields, volatile excluded. |
| REPLAY-1 | **Standalone verify outside the rules-replay path** — a `verify(recorded_hash, memo_content) -> bool` (recompute-and-compare, no LLM), owned here; **not** part of audit-store's `ReplayService` (which excludes `memo_hash`). |
| SEC1-1 | **Schema-exclusion** — `MemoAgentInput` (and every LLM-bound payload) declares no `original_span`/`SanitizationReport` field; structural, plus a serialized-payload assertion. |
| TEMP0-1 | **Central temp=0 in the abstraction** — `temperature=0` fixed inside `ProviderAbstraction`, not passed per-call; the fake records params. |
| ADVISORY-1 | **Advisory-only naming + prompt template** — fields/enums use "recommendation"; a static system-prompt template asserts advisory language. |
| PROV-1 | **Injected `ProviderAbstraction` Protocol** — Gemini adapter (P1) + fake (tests); Claude/Ollama/MCP/`route_borderline` named-not-wired stubs. |
| PERF-1 | **Observed-not-gated** — duration emitted; no latency-failing check. |
| OBS-1 | **Emit-only allowlist `TelemetryEmitter`** — ids/enums/int counts/timing; no prose/demographic/free-text/`original_span`. |
| (orchestration) | **LangGraph sub-flow pattern** — `draft → validate_citations → retry/finalize` (+ flag); checkpointer YES / interrupt NO; gate external. |

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

## Question 1 — CON-BR2 three independent structural patterns
A) **Three separate patterns, one per layer** — TYPE = schema-unrepresentability (model output type has no rec/confidence field); STATE = read-only LangGraph channel (input-only, reducer forbids node writes); COMMIT = no-commit-path (unit constructs no `DecisionCommitService`; committed rec bypasses via `recommendation_id`). Each independently verifiable; no single point of trust. *(Recommended — CON-BR2 load-bearing.)*
B) One combined "recommendation is protected" pattern (rejected — collapses the three layers). · C) Other.

[Answer]: A — three separate patterns, one per layer: TYPE = schema-unrepresentability (model output type has no rec/confidence field); STATE = read-only LangGraph channel (input-only, reducer forbids node writes); COMMIT = no-commit-path (unit constructs no DecisionCommitService; committed rec bypasses via recommendation_id). Each independently verifiable; no single point of trust.

## Question 2 — LangGraph sub-flow pattern (checkpointer / interrupt / state)
A) **LangGraph scoped to the C4 memo sub-flow only** (`draft → validate_citations → retry/finalize`, + `flag`); **checkpointer YES** (retry loop + durability + 100%-step tracing), **interrupt NO** (human gate EXTERNAL — `DecisionCommitService`); `recommendation`/`confidence` are read-only input channels; `route_borderline` not wired. Exercised with the fake. *(Recommended.)*
B) In-graph interrupt for the gate (rejected — contradicts the FD). · C) Other.

[Answer]: A — LangGraph scoped to the C4 memo sub-flow only (draft → validate_citations → retry/finalize, + flag); checkpointer YES (retry loop + durability + tracing), interrupt NO (human gate external — DecisionCommitService); recommendation/confidence are read-only input channels; route_borderline not wired. Exercised with the fake.

## Question 3 — Prompt-scoping + citation-validation patterns (GROUND-1 / CITE-1)
A) **`PromptBuilder` reads only `MemoAgentInput`** (no MCP client in P1); **`CitationValidator` = report-membership check** (every `cited_rule_id ∈ RuleResultReport`, belt-and-suspenders `∈ rulebook`) as a **pure function** (Hypothesis ∀). Grounding + hallucination guard both structural. *(Recommended.)*
B) Let the validator fetch descriptions via MCP (rejected — Phase-2; retrieval-miss risk). · C) Other.

[Answer]: A — PromptBuilder reads only MemoAgentInput (no MCP client in P1); CitationValidator = report-membership check (every cited_rule_id ∈ RuleResultReport, belt-and-suspenders ∈ rulebook) as a pure function (Hypothesis ∀). Grounding + hallucination guard both structural.

## Question 4 — Bounded-retry pattern + the both-directions test harness (CITE-FAILURE)
A) **Capped-retry edge in the graph** (`validate` → `retry` → `draft` while retries left; → `flag` when exhausted; → `finalize` when valid). The **scripted, call-count-aware fake** drives **both** explicit named tests — **recover-within-cap → finalize** and **exhaust-cap → flag** (injected recommendation unchanged). Retry cap is a named constant. *(Recommended.)*
B) Unbounded retry / single-direction test (rejected — non-terminating; misses a direction). · C) Other.

[Answer]: A — capped-retry edge in the graph (validate → retry → draft while retries left; → flag when exhausted; → finalize when valid). The scripted, call-count-aware fake drives both explicit named tests — recover-within-cap → finalize and exhaust-cap → flag (injected recommendation unchanged). Retry cap is a named constant.

## Question 5 — Deterministic `missing_information` derivation (MISSINGINFO-1)
A) **`MissingInfoDeriver`** — a pure function over the 3 signals: (i) `DocumentManifest.entries[].status ∈ {missing, unparseable}`, (ii) `RuleResult.status == not_evaluated`, (iii) `profile.incomplete` → `MissingInformationItem{source, detail}`, in a **fixed canonical order** (so the structured list is byte-stable ×N, independent of fake output). Not LLM-authored. *(Recommended.)*
B) LLM-authored / order-dependent (rejected — non-reproducible; G3/CON-DET-1). · C) Other.

[Answer]: A — MissingInfoDeriver, a pure function over the 3 signals: (i) DocumentManifest.entries[].status ∈ {missing, unparseable}, (ii) RuleResult.status == not_evaluated, (iii) profile.incomplete → MissingInformationItem{source, detail}, in a fixed canonical order (byte-stable ×N, independent of fake output). Not LLM-authored.

## Question 6 — `memo_hash`: local CanonSerAdapter, compute + standalone verify (HASH-1 / REPLAY-1)
A) **A local `MemoHashAdapter` delegating to the unchanged shared `canon_ser`** — **compute** at `finalize` (hashed content = `narrative_prose` + `cited_rule_ids` + `missing_information` + `recommendation` + `confidence`; volatile excluded) **AND a standalone `verify(recorded_hash, memo_content) -> bool`** (recompute-and-compare, **no LLM**), invoked **OUTSIDE** the rules-replay path. audit-store stores `memo_hash` (str only) + cannot re-derive; its `ReplayService` excludes it. No fork, no shared-code edit. *(Recommended — closes the carry-forward with corrected ownership.)*
B) Re-declare a memo-local serializer / put verify inside ReplayService (rejected — fork/drift; ReplayService structurally can't). · C) Other.

[Answer]: A — a local MemoHashAdapter delegating to the unchanged shared canon_ser — compute at finalize (hashed content = narrative_prose + cited_rule_ids + missing_information + recommendation + confidence; volatile excluded) AND a standalone verify(recorded_hash, memo_content) -> bool (recompute-and-compare, no LLM), invoked OUTSIDE the rules-replay path. audit-store stores memo_hash (str only) + cannot re-derive; its ReplayService excludes it. No fork, no shared-code edit.

## Question 7 — SEC-1-FORENSIC schema-exclusion pattern (SEC1-1)
A) **`MemoAgentInput` (and every LLM-bound payload) declares no `original_span`/`SanitizationReport` field** — structural; the `PromptBuilder` references only clean artifacts; a schema-level + serialized-payload assertion proves no forensic span can reach the LLM. *(Recommended.)*
B) Runtime filter (rejected — not structural). · C) Other.

[Answer]: A — MemoAgentInput (and every LLM-bound payload) declares no original_span/SanitizationReport field — structural; the PromptBuilder references only clean artifacts; a schema-level + serialized-payload assertion proves no forensic span can reach the LLM.

## Question 8 — Injected `ProviderAbstraction` pattern + central temp=0 (TEMP0-1 / PROV-1)
A) **`ProviderAbstraction` Protocol** injected — **Gemini adapter (P1)** with `temperature=0` fixed **centrally** (not per-call) + XML→Pydantic; **deterministic scripted fake (tests)** recording call params; **Claude/Ollama/MCP/`route_borderline` = named not-wired stubs (Phase-2)**. All targets fake-verifiable; no live LLM in the suite. *(Recommended.)*
B) Per-call temperature / wire Phase-2 now (rejected — non-central; scope creep). · C) Other.

[Answer]: A — ProviderAbstraction Protocol injected — Gemini adapter (P1) with temperature=0 fixed centrally (not per-call) + XML→Pydantic; deterministic scripted fake (tests) recording call params; Claude/Ollama/MCP/route_borderline = named not-wired stubs (Phase-2). All targets fake-verifiable; no live LLM in the suite.

## Question 9 — Emit-only allowlist telemetry (PERF-1 / OBS-1)
A) **A `TelemetryEmitter` with a structural allowlist** (ids/enums/int counts/timing) — no prose/demographic/free-text/`original_span` field can be emitted; **PERF observed-not-gated** (duration emitted, no failing check); Langfuse 100%-step tracing wired by `observability` (reference-not-own). *(Recommended.)*
B) Free-form structured logging / hard latency gate (rejected — SEC leak risk; provider-bound). · C) Other.

[Answer]: A — a TelemetryEmitter with a structural allowlist (ids/enums/int counts/timing) — no prose/demographic/free-text/original_span field can be emitted; PERF observed-not-gated (duration emitted, no failing check); Langfuse 100%-step tracing wired by observability.

## Question 10 — Logical-component decomposition
A) **Named components**: `MemoAgentInputBuilder`, `PromptBuilder`, `ProviderAbstraction` (Protocol) + `GeminiAdapter` + scripted `FakeProvider`, `CitationValidator`, `MissingInfoDeriver`, `MemoHashAdapter` (compute + verify), `MemoAssembler` (finalize), `LangGraphOrchestrator` (the sub-flow + bounded-retry policy), `TelemetryEmitter` — each mapping to ≥1 `NFR-MEMO-*` target, no reference-not-own violation. *(Recommended.)*
B) Fewer/coarser components (describe). · C) Other.

[Answer]: A — named components: MemoAgentInputBuilder, PromptBuilder, ProviderAbstraction (Protocol) + GeminiAdapter + scripted FakeProvider, CitationValidator, MissingInfoDeriver, MemoHashAdapter (compute + verify), MemoAssembler (finalize), LangGraphOrchestrator (sub-flow + bounded-retry policy), TelemetryEmitter — each mapping to ≥1 NFR-MEMO-* target, no reference-not-own violation.

## Question 11 — Depth + artifacts (Mermaid required)
A) **Comprehensive** — two artifacts: **`nfr-design-patterns.md`** (one §-section per pattern, each structurally meeting its target + a validated Mermaid pattern-integration diagram + text alt) + **`logical-components.md`** (the component blueprint + ownership table + reference-not-own check + a validated component-relationship Mermaid + text alt). Same class as intake/rules-engine/audit-store. *(Recommended.)*
B) Lighter / no Mermaid (rejected — invariant-bearing unit). · C) Other.

[Answer]: A — comprehensive: two artifacts, nfr-design-patterns.md (one section per pattern, each structurally meeting its target + a validated Mermaid pattern-integration diagram + text alt) + logical-components.md (component blueprint + ownership table + reference-not-own check + a validated component-relationship Mermaid + text alt). Same class as intake/rules-engine/audit-store.

---

## 4. Named logical components (draft — finalized after Q10)

`MemoAgentInputBuilder` · `PromptBuilder` · `ProviderAbstraction` (Protocol) + `GeminiAdapter` (P1) + scripted `FakeProvider` (tests) · `CitationValidator` · `MissingInfoDeriver` · `MemoHashAdapter` (compute + standalone verify) · `MemoAssembler` (finalize) · `LangGraphOrchestrator` (sub-flow + bounded-retry policy) · `TelemetryEmitter`. Referenced-not-owned: rules-engine `RuleResultReport`/`Rulebook`, intake `ApplicantProfile`, shared `canon_ser`, audit-store persist/replay, `outlier-model` (Phase 2), `memo-extensions` (Phase 2), `observability`.

## 5. Constraints & settled items held (not re-opened)
- Frozen FD + frozen C4 contract + approved 15 `NFR-MEMO-*` targets are the inputs — patterns realize them, re-opening none.
- **Reference-not-own** throughout (list in §1). Shared `canon_ser` **unchanged**.
- **CON-BR2 load-bearing** — three independent patterns. **The LLM only drafts prose** — no LLM in the deterministic path / tests (fake) / replay.
- **`memo_hash`** compute + verify owned solely here; audit-store stores it + can't re-derive; `ReplayService` excludes it (verify runs outside the rules-replay path).
- **`outlier_result` Phase-2-optional** (None in P1). Runtime **Python 3.12**; **DATA-4** synthetic only.

## 6. Next step (STOP here)
Fill the eleven `[Answer]:` tags. On your signal I will read the answers, run the mandatory ambiguity-check (adding a clarification only if needed), then **generate Part 2** — `nfr-design-patterns.md` + `logical-components.md` (Mermaid validated before write) — and stop at the NFR-Design 2-option gate. **NO NFR-Design artifacts are generated until the answers are in, checked, and you give the explicit go.**
