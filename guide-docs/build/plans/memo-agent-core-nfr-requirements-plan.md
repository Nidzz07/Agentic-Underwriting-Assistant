# NFR Requirements Plan (Part 1) — `memo-agent-core` (C4 / U4)

**Phase / Stage**: BUILD → NFR Requirements, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: cluster unit **4 of 4 — the LAST cluster unit** · **FD ✅** → **NFR Requirements ← here** → NFR Design → [Infra likely SKIP] → Code-Gen.
(`intake`+`document-sanitizer`, `rules-engine`, `audit-store` all COMPLETE — this is the FINAL cluster unit, **where the LLM enters**.)
**Unit**: U4 `memo-agent-core` — grounding, citation validation, CON-BR2, SEC-1-FORENSIC non-ingestion, temperature=0, advisory-only.
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** · **Depth**: **comprehensive** (invariant-bearing; **CON-BR2 is load-bearing here**, plus determinism must hold **despite an LLM in the loop**).
**Status**: **Plan COMPLETE — eleven `[Answer]:` tags filled (all A); ambiguity-check CLEAN (2026-07-06); Part 2 GENERATED 2026-07-06** (`nfr-requirements.md` + `tech-stack-decisions.md`, both sharpenings folded in — HASH-1/REPLAY-1 corrected ownership wording + CITE-FAILURE both-retry-directions scripted fake). **Awaiting the NFR-Requirements 2-option gate.**

Built **ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) + the frozen C4 contract —
**re-opening neither**. Every `NFR-MEMO-*` target below is drafted **pass/fail testable**. **Central testability principle:**
the LLM is reached only through an **injected `ProviderAbstraction`**, so **every deterministic invariant is unit-testable
against a FAKE provider — no live LLM, no network** (live-provider quality is `quality-gates`' eval, not this unit's gate).

---

## 1. Unit context (analyzed)

### 1.1 What NFR Requirements builds ON (frozen — NOT re-opened)
- **Frozen C4 contract**: `draft(profile, rule_report, outlier_result|None) -> DecisionMemo`;
  `validate_citations(memo_draft, rulebook) -> CitationValidationResult`; `route_borderline(...) -> ThinkingMode`
  (**Phase-2 seam, not wired**); `ProviderAbstraction.complete(prompt, schema) -> StructuredOutput` (temperature=0 central).
- **Frozen FD**: the three-region `DecisionMemo` (`L` LLM-authored `narrative_prose`+`cited_rule_ids` / `D` deterministic
  `missing_information` / `RO` injected `recommendation`+`confidence` / `M` `memo_hash`+`model_version`); `MemoAgentInput`
  (clean read-only artifacts only); `CitationValidationResult`; the LangGraph sub-flow (draft→validate→retry/finalize,
  checkpointer YES / interrupt NO); `memo_hash` via the shared CANON-SER; BR-GROUND / BR-CITE-* / BR-CONBR2-TYPE/STATE/COMMIT
  / BR-MISSINGINFO / BR-SEC1-NOINGEST / BR-TEMP0 / BR-ADVISORY.

### 1.2 Dependencies & interfaces (reference-not-own)
- **Consumes read-only**: rules-engine's **`RuleResultReport`** (the **sole grounding source**) + its read-only
  `recommendation`/`confidence` (imported, not re-derived); intake's **`ApplicantProfile`** (clean facts; `original_span`
  **structurally excluded**); the **active `Rulebook`** (for the belt-and-suspenders citation check — rules-engine's model).
- **Produces**: `DecisionMemo` (to FastAPI→UI, pending/advisory) + **`memo_hash`** + `model_version` — the fields
  **`audit-store` reserved in its 6-tuple** (the cross-unit contract audit-store is waiting on).
- **Shared (reference-not-own)**: `backend/common/canon_ser.py` — **audit-store's §2.1 CANON-SER, referenced NOT
  re-declared** (so `memo_hash` is byte-identical to what `ReplayService` recomputes) + `decimal_context.py`.
- **Owned elsewhere / Phase-2 (referenced, not built here)**: the **LLM provider** (Gemini, via the injected
  `ProviderAbstraction`; a fake drives tests); `outlier-model` (`OutlierResult` — Phase 2, `None` in P1); `memo-extensions`
  (Claude/Ollama adapters, MCP `rulebook-tools`, `route_borderline` — Phase 2); `audit-store` (persists `memo_hash`,
  `DecisionCommitService` commits — the memo never commits); `observability` (Langfuse/traces); `quality-gates` (QA-5
  bias/calibration + live-provider groundedness evals).

### 1.3 Guardrails held (skill)
**CON-BR2** (the LLM cannot alter the recommendation — three structural layers; **load-bearing**); **temperature=0** on
every production call; **hallucination guard** (cite only from the handed report); **advisory-only** ("recommendation",
never "decision"); **SEC-1-FORENSIC** (no `original_span` in any LLM-bound payload); **CON-DET-1 boundary** (`missing_information`
+ `memo_hash` deterministic; the memo is **not** in the replay equality set; replay verifies by hash, **never re-drafts / no
LLM in replay**); **DATA-4** (synthetic only). **No LLM in the deterministic path** — the LLM only drafts prose, downstream.

---

## 2. Draft `NFR-MEMO-*` targets (pass/fail testable — finalized after the answers)

### CON-BR2 — the LLM cannot alter the recommendation (three non-overlapping layers)
- **NFR-MEMO-CONBR2-TYPE** — *type layer.* The LLM's **structured-output schema** (what the model fills) contains
  **only** `narrative_prose` + `cited_rule_ids` — **no `recommendation`/`confidence` field**; on `DecisionMemo` those are
  **`RO`**, injected by the orchestrator from `rule_report`. **Test**: the model output schema has no recommendation field;
  a fake provider that *emits* a recommendation in its structured output **cannot** populate `DecisionMemo.recommendation`
  (unrepresentable) — "the LLM changed the recommendation" fails to compile/parse into a recommendation.
- **NFR-MEMO-CONBR2-STATE** — *graph-state layer.* In the LangGraph sub-flow, `recommendation`/`confidence` are
  **read-only input channels; no node has write access**. **Test**: a fake provider returning prose that *contradicts* the
  recommendation → `DecisionMemo.recommendation` == the **injected** value, unchanged; no graph node can mutate it.
- **NFR-MEMO-CONBR2-COMMIT** — *commit-path layer.* `memo-agent-core` has **no commit/finalize-decision path**; the memo
  is advisory output only. The committed recommendation routes `rules-engine → DecisionCommitService` via
  `recommendation_id`, **bypassing the memo** (audit-store owns commit — already built; `commit` takes `recommendation_id`,
  never a memo). **Test**: memo-agent-core instantiates no `DecisionCommitService`/commit call; the memo's `recommendation`
  is display/citation-only.

### Grounding + citation validation (G6 / FR-MEMO-3)
- **NFR-MEMO-GROUND-1** — the prompt/context is built **only** from the handed `MemoAgentInput` clean artifacts;
  **Phase-1 has NO MCP / no tool fetch** to re-derive what fired. **Test**: the prompt-builder input is exactly
  `MemoAgentInput`; no MCP client is constructed in P1.
- **NFR-MEMO-CITE-1** — `validate_citations`: every `cited_rule_id` **must be a member of the handed `RuleResultReport`**
  (authoritative) + belt-and-suspenders present in the active `rulebook`; else `citation_failure`. **Test** (Hypothesis ∀):
  for all cited ids not in the report → `citation_failure` + the offending ids listed; all-valid → `valid`.
- **NFR-MEMO-CITE-FAILURE** — on `citation_failure` the memo is **BLOCKED, not surfaced**; a **bounded retry** re-drafts;
  if it still fails → the memo is **flagged** and **the deterministic recommendation from C2 still stands** (LLM out of the
  decision path). **Test**: a fake provider that always cites a hallucinated id → after the capped retries, the memo is
  blocked/flagged and `recommendation` (injected) is unchanged; **no hallucinated rule reaches the underwriter**.

### missing_information determinism (G3 / CON-DET-1)
- **NFR-MEMO-MISSINGINFO-1** — the structured `missing_information` is derived **DETERMINISTICALLY** from intake's
  completeness manifest (documents `missing`/`unparseable`) + the `not_evaluated` `RuleResult`s + `profile.incomplete` —
  **NOT LLM-authored**. **Test**: same inputs → **identical** `missing_information` ×N **regardless of the (fake) LLM
  output**; every item traces to a deterministic signal (source enum); the prose may render it but the **structured list is
  authoritative**.

### memo_hash — shared CANON-SER + verification (the cross-unit contract audit-store awaits)
- **NFR-MEMO-HASH-1** — `memo_hash` = a deterministic hash over the memo's **canonical content** (`narrative_prose`,
  `cited_rule_ids`, `missing_information`, `recommendation`, `confidence`; **volatile metadata excluded**), via the
  **single shared `backend/common/canon_ser.py` (audit-store §2.1) — referenced, UNCHANGED, not re-declared**. **Test**:
  deterministic ×N; any hashed-field change → different hash; **byte-identical to an independent recompute via the shared
  util** (the value `audit-store`'s `ReplayService` checks). **This unit also owns memo-hash VERIFICATION** (the carry-forward
  from audit-store): a `verify` recompute-and-compare that uses **no LLM** — replay verifies by hash, never re-drafts.

### SEC-1-FORENSIC non-ingestion (intake carry-forward)
- **NFR-MEMO-SEC1-1** — the `MemoAgentInput` contract **structurally cannot carry** `original_span` / the
  `SanitizationReport`; **no LLM-bound payload can reference `original_span`**. **Test** (schema-level): `MemoAgentInput`
  has no such field; the prompt-builder has no reference to it; a canon/serialize of any LLM-bound payload contains no
  forensic span.

### CON-DET-1 replay boundary
- **NFR-MEMO-REPLAY-1** — the memo is **NOT in the replay evaluation-equality set** (rules-engine's output is); memo
  integrity on replay is **`memo_hash` comparison only**, and **replay NEVER invokes the LLM / never re-drafts**. **Test**:
  the memo-hash `verify` recomputes deterministically (no provider call); a structural assertion that replay-path memo
  verification constructs no `ProviderAbstraction`. Matches audit-store's replay projection exactly (memo = hash-verified).

### Production-call rules
- **NFR-MEMO-TEMP0-1** — **every production LLM call uses `temperature=0`**, enforced **centrally** in the
  `ProviderAbstraction` (Gemini primary, P1), with structured XML→Pydantic output. **Test**: the fake provider records the
  params it was called with → `temperature == 0` on every call; the abstraction cannot issue a non-zero-temperature call.
- **NFR-MEMO-ADVISORY-1** — advisory-only: field names/enums use **"recommendation"** (`APPROVE|REFER|DECLINE-RECOMMEND`,
  `-RECOMMEND` suffix); the system-prompt template enforces advisory language; "decision" reserved for the human. **Test**:
  no user-facing/internal field or enum frames a final "decision"; the prompt template asserts advisory language.
- **NFR-MEMO-PROV-1** — the **provider-abstraction interface + the Gemini adapter (P1 only)**; **Claude/Ollama adapters,
  MCP, `route_borderline` are Phase-2 (`memo-extensions`) — named seams, NOT wired**. **Test**: `route_borderline` is a
  not-wired stub; only the Gemini adapter is present; the abstraction is injectable (a fake drives all unit tests).

### Performance / observability (scoped)
- **NFR-MEMO-PERF-1** — LLM-call latency is **provider-bound + observed-only (soft budget)**, **not gated** (correctness /
  determinism / groundedness take precedence). **Test**: duration emitted; no latency-failing check.
- **NFR-MEMO-OBS-1** — telemetry is **emit-only allowlist** (ids/enums/int counts/timing; **no demographic / free-text /
  prose / `original_span`**); Langfuse 100%-step tracing via the checkpointer is wired by `observability` (reference-not-own).
  **Test**: the telemetry schema structurally carries no prose/demographic/free-text field.

### tech-stack (to be recorded in `tech-stack-decisions.md`)
LangGraph (the C4 sub-flow only; checkpointer YES / interrupt NO) · the `ProviderAbstraction` (injected; Gemini adapter P1;
fake in tests) · Pydantic v2 (memo schema; XML→Pydantic structured output) · shared CANON-SER + `decimal_context` referenced ·
rules-engine `RuleResultReport`/`Rulebook` + intake `ApplicantProfile` referenced · **no LLM in tests (fake provider)** ·
Python 3.12. `outlier-model`/`memo-extensions`/`observability`/`audit-store` referenced.

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

## Question 1 — Test toolchain (determinism DESPITE an LLM)
A) **pytest + pytest-cov (≥90%, QA-6) + Hypothesis** (citation-validation ∀ hallucinated/absent id → `citation_failure`) +
   a **FAKE injected `ProviderAbstraction`** so **every unit test runs with NO live LLM / no network**; the LangGraph
   sub-flow is exercised with the fake. Live-provider groundedness is `quality-gates`' eval, not this unit's gate. Same
   base toolchain as intake/rules-engine/audit-store. *(Recommended.)*
B) pytest + pytest-cov only. · C) Other.

[Answer]: A — pytest + pytest-cov (≥90%, QA-6) + Hypothesis (citation-validation ∀ hallucinated/absent id → citation_failure) + a FAKE injected ProviderAbstraction so every unit test runs with no live LLM/no network; the LangGraph sub-flow exercised with the fake. Live-provider groundedness is quality-gates' eval, not this unit's gate.

## Question 2 — Provider-abstraction as an injected seam (the key testability decision)
A) **`ProviderAbstraction.complete(prompt, schema)` is an injected interface** (Protocol) with a **Gemini adapter (prod)**
   and a **deterministic fake (tests)** — the fake returns canned structured output (prose + cited ids) and **records the
   call params** (so `temperature=0` is asserted at the boundary). All CON-BR2 / missing_info / memo_hash / citation /
   SEC-1 targets are testable against the fake; **no live LLM in the unit suite**. Mirrors the audit-store seams pattern.
   *(Recommended.)*
B) Call a live provider in tests (rejected — non-deterministic, network, cost). · C) Other.

[Answer]: A — ProviderAbstraction.complete(prompt, schema) is an injected Protocol with a Gemini adapter (prod) and a deterministic fake (tests) — the fake returns canned structured output and records call params (temperature=0 asserted at the boundary). All CON-BR2/missing_info/memo_hash/citation/SEC-1 targets testable against the fake; no live LLM in the unit suite. Mirrors the audit-store seams pattern.

## Question 3 — CON-BR2 three-layer test split
A) **Test all three layers independently**: TYPE (the model's structured-output schema has no recommendation/confidence
   field; `DecisionMemo.recommendation` is `RO`), STATE (a fake provider returning a contradictory recommendation → the
   injected value is unchanged; no graph node writes it), COMMIT (memo-agent-core has no commit path; the committed rec
   bypasses via audit-store's `recommendation_id`). No single point of trust. *(Recommended — CON-BR2 is load-bearing.)*
B) A single post-hoc "did the recommendation change" check (rejected — not structural). · C) Other.

[Answer]: A — test all three CON-BR2 layers independently: TYPE (model's structured-output schema has no recommendation/confidence field), STATE (fake provider returning a contradictory recommendation → injected value unchanged, no graph node writes it), COMMIT (memo-agent-core has no commit path; committed rec bypasses via audit-store's recommendation_id). No single point of trust.

## Question 4 — memo_hash: shared CANON-SER + verification ownership (cross-unit contract)
A) **Reference the shared `backend/common/canon_ser.py` (audit-store §2.1) UNCHANGED** for `memo_hash` — no re-declaration,
   byte-identical to what `ReplayService` recomputes. **memo-agent-core owns BOTH compute (at finalize) AND verify
   (recompute-and-compare, NO LLM)** — resolving the audit-store→memo-agent-core carry-forward. A memo-agent-core-local
   adapter delegates to the shared util. *(Recommended — closes the cross-unit contract audit-store awaits.)*
B) Re-declare a memo-local serializer (rejected — fork/drift vs audit-store's replay check). · C) Other.

[Answer]: A — reference the shared backend/common/canon_ser.py (audit-store §2.1) UNCHANGED for memo_hash — no re-declaration, byte-identical to what ReplayService recomputes. memo-agent-core owns BOTH compute (at finalize) AND verify (recompute-and-compare, no LLM) — resolving the audit-store carry-forward. A memo-agent-core-local adapter delegates to the shared util.

## Question 5 — missing_information deterministic signals
A) Derive **deterministically** from **(i)** intake's `DocumentManifest` entries with status `missing`/`unparseable`,
   **(ii)** the `RuleResult`s with `status == not_evaluated`, **(iii)** `profile.incomplete` — each → a
   `MissingInformationItem{source, detail}`. **NOT LLM-authored**; reproducible ×N; the prose may render it but the
   structured list is authoritative. *(Recommended.)*
B) Let the LLM author the list (rejected — non-reproducible; violates G3/CON-DET-1). · C) Other.

[Answer]: A — derive deterministically from (i) intake's DocumentManifest entries with status missing/unparseable, (ii) RuleResults with status == not_evaluated, (iii) profile.incomplete — each → a MissingInformationItem{source, detail}. Not LLM-authored; reproducible ×N; prose may render it but the structured list is authoritative.

## Question 6 — SEC-1-FORENSIC non-ingestion
A) `MemoAgentInput` (and every LLM-bound payload) **structurally has no `original_span`/`SanitizationReport` field**; the
   prompt-builder references only the clean artifacts; a schema-level + serialized-payload assertion proves no forensic
   span can reach the LLM. *(Recommended.)*
B) Filter the span out at runtime (rejected — not structural). · C) Other.

[Answer]: A — MemoAgentInput (and every LLM-bound payload) structurally has no original_span/SanitizationReport field; the prompt-builder references only clean artifacts; a schema-level + serialized-payload assertion proves no forensic span can reach the LLM.

## Question 7 — LangGraph scope + checkpointer/interrupt
A) **LangGraph scoped to the C4 memo sub-flow ONLY** (draft → validate_citations → retry/finalize); **checkpointer YES**
   (retry loop + state durability + 100%-step tracing), **in-graph interrupt NO** (the human gate is EXTERNAL —
   `DecisionCommitService` in audit-store). `route_borderline` not wired. The graph is exercised with the fake provider.
   *(Recommended.)*
B) Put the human gate as an in-graph interrupt (rejected — contradicts the FD; gate is audit-store's). · C) Other.

[Answer]: A — LangGraph scoped to the C4 memo sub-flow only (draft → validate_citations → retry/finalize); checkpointer YES (retry loop + durability + tracing), in-graph interrupt NO (the human gate is external — DecisionCommitService in audit-store). route_borderline not wired. Graph exercised with the fake provider.

## Question 8 — Provider scope (P1) + Phase-2 seams
A) **P1 = the provider-abstraction interface + the Gemini adapter + central temperature=0 + XML→Pydantic**; **Claude/Ollama
   adapters, MCP `rulebook-tools`, `route_borderline` = Phase-2 (`memo-extensions`) — named, NOT wired here**. *(Recommended.)*
B) Wire Claude/Ollama/MCP now (rejected — Phase-2 scope creep). · C) Other.

[Answer]: A — P1 = the provider-abstraction interface + the Gemini adapter + central temperature=0 + XML→Pydantic; Claude/Ollama adapters, MCP rulebook-tools, route_borderline = Phase-2 (memo-extensions) — named, not wired here.

## Question 9 — `outlier_result` Phase-2-optional
A) `draft(..., outlier_result: OutlierResult | None = None)` — in **P1 always `None`** (the `outlier-model` is Phase 2, not
   built); `OutlierResult` is **referenced-not-owned** (Phase 2). The memo handles `None` cleanly; no outlier content in P1.
   *(Recommended.)*
B) Require an outlier_result now (rejected — outlier-model not built; Phase 2). · C) Other.

[Answer]: A — draft(..., outlier_result: OutlierResult | None = None) — in P1 always None (outlier-model is Phase 2, not built); OutlierResult referenced-not-owned. The memo handles None cleanly; no outlier content in P1.

## Question 10 — Depth confirmation
A) **Comprehensive** — invariant-bearing; **CON-BR2 is load-bearing** and determinism must hold **despite an LLM**; same
   class as intake/rules-engine/audit-store. *(Recommended.)*
B) Lighter (describe). · C) Other.

[Answer]: A — comprehensive. Invariant-bearing; CON-BR2 is load-bearing and determinism must hold despite an LLM; same class as intake/rules-engine/audit-store.

## Question 11 — Performance / observability scope
A) **Soft-budget, observed-not-gated** (LLM latency is provider-bound; correctness/determinism/groundedness take
   precedence) **+ emit-only allowlist telemetry** (no demographic/free-text/prose/`original_span`); Langfuse 100%-step
   tracing wired by `observability` (reference-not-own). *(Recommended.)*
B) A hard latency gate on the LLM call (rejected — provider-bound). · C) Other.

[Answer]: A — soft-budget, observed-not-gated (LLM latency is provider-bound; correctness/determinism/groundedness take precedence) + emit-only allowlist telemetry (no demographic/free-text/prose/original_span); Langfuse 100%-step tracing wired by observability.

---

## 4. Story traceability (targets ↔ stories)
| Story / invariant | Draft target(s) |
|---|---|
| US-MEMO-1 (CON-BR2 — LLM cannot change the recommendation) | NFR-MEMO-CONBR2-TYPE/-STATE/-COMMIT |
| US-MEMO-2/4 (temperature=0, advisory-only) | NFR-MEMO-TEMP0-1, NFR-MEMO-ADVISORY-1 |
| US-MEMO-3 (citation / hallucination guard) | NFR-MEMO-GROUND-1, NFR-MEMO-CITE-1, NFR-MEMO-CITE-FAILURE |
| reviewer G3 (deterministic missing_information) | NFR-MEMO-MISSINGINFO-1 |
| CON-AUDIT-1 / replay (memo_hash) | NFR-MEMO-HASH-1, NFR-MEMO-REPLAY-1 |
| SEC-1-FORENSIC | NFR-MEMO-SEC1-1 |
| FR-PROV-1/3 (provider abstraction, P1 Gemini) | NFR-MEMO-PROV-1, NFR-MEMO-TEMP0-1 |

## 5. Constraints & settled items held (not re-opened)
- **Frozen FD + frozen C4 contract** are the inputs — NFR Requirements pins **testable targets ON** them, re-opening none.
- **Reference-not-own**: rules-engine `RuleResultReport`/`Rulebook`; intake `ApplicantProfile`; shared CANON-SER
  (`backend/common/canon_ser.py`, unchanged) + `decimal_context`; the LLM provider (injected; fake in tests);
  `outlier-model` `OutlierResult` (Phase 2); `memo-extensions` (Claude/Ollama/MCP/route_borderline — Phase 2);
  `audit-store` (persist/replay); `observability`; `quality-gates` (QA-5 + live evals).
- **CON-BR2 is load-bearing** — the three structural layers are not re-opened, only made testable.
- **The LLM only drafts prose** — no LLM in the deterministic path; **no LLM in tests** (fake provider); **no LLM in replay**.
- **memo_hash** shares audit-store's CANON-SER byte-for-byte (the cross-unit contract). **outlier_result Phase-2-optional.**
- Runtime **Python 3.12**; **DATA-4** synthetic only.

## 6. Next step (STOP here)
Fill the eleven `[Answer]:` tags. On your signal I will read the answers, run the mandatory ambiguity-check (adding a
clarification file only if needed), then **generate Part 2** — `nfr-requirements.md` (the finalized `NFR-MEMO-*` pass/fail
targets) + `tech-stack-decisions.md` — and stop at the NFR-Requirements 2-option gate. **NO NFR-Requirements artifacts are
generated until the answers are in, checked, and you give the explicit go.**
