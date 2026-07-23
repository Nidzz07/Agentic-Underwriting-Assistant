# Tech-Stack Decisions — `memo-agent-core` (C4 / U4)

**Phase / Stage**: BUILD → NFR Requirements, **Part 2** · cluster unit **4 of 4 — the LAST** (where the LLM enters)
**Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** · **Depth**: comprehensive
**Rule**: choices realize the `NFR-MEMO-*` targets **ON** the frozen FD + C4 contract — **re-opening neither**; **reference-not-own** throughout. **No new cross-cutting dependency** beyond what the cluster already uses + the LangGraph/provider stack the C4 contract already names.

---

## D1 — LangGraph (the C4 memo sub-flow ONLY)
- **Decision**: LangGraph orchestrates **only** the C4 memo sub-flow: `inject → draft → validate_citations → retry/finalize` (+ `flag`). The deterministic pipeline (intake → rules → outlier) ran **before** the graph.
- **Checkpointer: YES** — for the citation-validation **retry loop**, state durability, and 100%-step Langfuse tracing.
- **In-graph interrupt: NO** — the human approval gate is **EXTERNAL** (`DecisionCommitService` in audit-store, reached via FastAPI). No `interrupt_after` for the gate.
- **Realizes**: NFR-MEMO-CONBR2-STATE (read-only channels, no node write), NFR-MEMO-CITE-FAILURE (bounded retry via the checkpointer), NFR-MEMO-CONBR2-COMMIT (gate external — this unit never commits).
- **FD**: `business-logic-model.md §1/§2.2`.

## D2 — Injected `ProviderAbstraction` (Protocol) + Gemini adapter (P1) + deterministic scripted fake (tests)
- **Decision**: `ProviderAbstraction.complete(prompt, schema) -> StructuredOutput` is an **injected Protocol** with:
  - a **Gemini adapter** (production, P1) — `temperature=0` enforced **centrally** in the abstraction, XML→Pydantic structured output;
  - a **deterministic fake** (tests) that returns **canned/scripted** structured output and **records every call's params** (so `temperature=0` is asserted at the boundary).
- **Scripted / call-count-aware fake (sharpening #2)**: the fake supports a **per-call scripted response sequence** so the bounded-retry path is tested in **BOTH** directions as explicit named tests —
  - `recover-within-cap → finalize`: hallucinated cite on early draft(s), then a **valid** cite within the cap → the graph finalizes a valid memo;
  - `exhaust-cap → flag`: always-hallucinate → cap exhausted → memo flagged/blocked, injected recommendation unchanged.
- **Realizes**: NFR-MEMO-PROV-1, NFR-MEMO-TEMP0-1, NFR-MEMO-CITE-1/-FAILURE, and — because the fake drives the whole sub-flow — **every** CON-BR2 / missing_info / memo_hash / SEC-1 target with **no live LLM / no network** in the unit suite. Mirrors the audit-store injected-seam + fake pattern.
- **FD**: `component-methods.md` C4 (`ProviderAbstraction`), `business-logic-model.md §1`.

## D3 — Pydantic v2 (memo schema + XML→Pydantic structured output)
- **Decision**: The `DecisionMemo` / `MemoAgentInput` / `CitationValidationResult` / `MissingInformationItem` shapes are **Pydantic v2** value objects (`frozen=True`, `extra="forbid"` — same discipline as intake/rules-engine/audit-store). The model's structured output is parsed **XML→Pydantic** into a schema that contains **only** `narrative_prose` + `cited_rule_ids`.
- **Realizes**: NFR-MEMO-CONBR2-TYPE (no recommendation/confidence field for the model to fill — structurally `RO`), NFR-MEMO-SEC1-1 (no `original_span` field on any LLM-bound payload — schema-level), NFR-MEMO-CITE-1 (validated ids).
- **FD**: `domain-entities.md §2/§2.1/§3/§4`.

## D4 — Shared CANON-SER referenced UNCHANGED, via a memo-agent-core-local adapter (closes the carry-forward — corrected ownership)
- **Decision**: `memo_hash` is computed via a **`memo-agent-core`-local adapter that delegates to the single shared `backend/common/canon_ser.py`** (audit-store §2.1 spec authority) — **referenced, UNCHANGED, never re-declared / never forked**. Hashed content = `narrative_prose` + `cited_rule_ids` + `missing_information` + `recommendation` + `confidence`; **volatile metadata excluded** (CANON-SER P4). Guaranteed byte-identical to any independent recompute via the same util.
- **Ownership (corrected — verified against the built `replay_service.py` + `record_schema.py`)**: **`memo-agent-core` is the SOLE owner of BOTH `memo_hash` compute (at finalize) AND verify (a separate, standalone recompute-and-compare, no LLM).** **`audit-store` stores `memo_hash` (a `str`; it does NOT store the memo text) and structurally cannot re-derive it.** **audit-store's `ReplayService` re-evaluates rules ONLY and EXCLUDES `memo_hash` from its equality set — it never checks/verifies/recomputes it.** The memo-integrity verify is invoked **OUTSIDE** the rules-replay path. This closes the Deferred-Decisions carry-forward "memo-hash-verification ownership → memo-agent-core" with accurate wording.
- **Realizes**: NFR-MEMO-HASH-1, NFR-MEMO-REPLAY-1.
- **FD**: `domain-entities.md §5`, `business-logic-model.md §3/§4.2`.

## D5 — `rules-engine` `RuleResultReport` / `Rulebook` referenced (reference-not-own)
- **Decision**: Import rules-engine's **`RuleResultReport`** (the sole grounding source: `rule_results` + read-only `recommendation` + `confidence`) and the active **`Rulebook`** (belt-and-suspenders citation check) — **read-only, never re-declared / re-derived**. `RuleStatus.NOT_EVALUATED` is consumed for `missing_information` signal (ii).
- **Realizes**: NFR-MEMO-GROUND-1, NFR-MEMO-CITE-1, NFR-MEMO-MISSINGINFO-1 (signal ii).
- **FD**: `domain-entities.md §1.2/§4`.

## D6 — `intake` `ApplicantProfile` referenced (reference-not-own)
- **Decision**: Import intake's **`ApplicantProfile`** (clean facts; `documents.DocumentManifest.entries[].status` for signals i, `incomplete: bool` for signal iii). **`original_span` is structurally excluded** (it lives on `SanitizationReportEntry`, AUDIT-ONLY, segregated) — never handed to this unit.
- **Realizes**: NFR-MEMO-MISSINGINFO-1 (signals i, iii), NFR-MEMO-SEC1-1.
- **FD**: `domain-entities.md §4`.

## D7 — `outlier_result` Phase-2-optional (always `None` in P1)
- **Decision**: `draft(profile, rule_report, outlier_result: OutlierResult | None = None)` — in **P1 always `None`** (`outlier-model` is Phase 2, not built). `OutlierResult` is **referenced-not-owned** (Phase 2). The memo handles `None` cleanly; no outlier content in P1.
- **FD**: `business-logic-model.md §5`, `component-methods.md` C4.

## D8 — Phase-2 seams named, NOT wired
- **Decision**: **Claude / Ollama adapters**, **MCP `rulebook-tools`**, and **`route_borderline`** are **Phase-2 (`memo-extensions`)** — present as **named seams / not-wired stubs**, exercised by no P1 execution path.
- **Realizes**: NFR-MEMO-PROV-1 (Gemini-only P1), NFR-MEMO-GROUND-1 (no MCP in P1).
- **FD**: `business-logic-model.md §5`.

## D9 — Test toolchain: pytest + pytest-cov (≥90%, QA-6) + Hypothesis — NO live LLM
- **Decision**: **pytest + pytest-cov** (`--cov-fail-under=90`, QA-6) **+ Hypothesis** (the `validate_citations` ∀ property) **+ the deterministic fake `ProviderAbstraction`**. The LangGraph sub-flow — including the retry loop — is exercised **entirely with the fake**. **No live LLM / no network** in the unit suite. Same base toolchain as intake / rules-engine / audit-store.
- **Realizes**: the central testability principle — every `NFR-MEMO-*` is pass/fail testable against the fake.

## D10 — Observability: emit-only allowlist telemetry (reference-not-own tracing)
- **Decision**: A structural **allowlist** telemetry emitter (ids / enums / int counts / timing) — **no demographic / free-text / prose / `original_span`**. Langfuse 100%-step tracing is wired by `observability` (reference-not-own) via the checkpointer.
- **Realizes**: NFR-MEMO-OBS-1, NFR-MEMO-PERF-1 (duration emitted, not gated).

## D11 — No LLM in the deterministic path / tests / replay
- **Decision**: The LLM drafts **prose only**, downstream of deterministic results. `missing_information`, `memo_hash` (compute + verify), citation validation, and CON-BR2 are **pure/deterministic** and **fake-testable**. Replay never invokes the LLM.
- **Realizes**: NFR-MEMO-MISSINGINFO-1, NFR-MEMO-HASH-1, NFR-MEMO-REPLAY-1, NFR-MEMO-CONBR2-*.

## D12 — Python 3.12 (build-wide pin) · no new dependency
- **Decision**: Runtime **Python 3.12** (`.python-version` + `pyproject requires-python`), matching every completed unit. New libraries limited to **LangGraph** (the C4 orchestrator the contract already names) + the **Gemini provider SDK** behind the adapter; everything else (Pydantic v2, shared `canon_ser` / `decimal_context`, pytest/pytest-cov/Hypothesis) is already in the stack. **No shared-code edit.**

---

## Summary map — target → decision

| `NFR-MEMO-*` | Realizing decision(s) |
|---|---|
| CONBR2-TYPE | D3 (Pydantic schema — no rec field) |
| CONBR2-STATE | D1 (LangGraph read-only channels) |
| CONBR2-COMMIT | D1 (gate external; no commit path here) |
| GROUND-1 | D5, D8 (report-only; no MCP in P1) |
| CITE-1 | D3, D5, D9 (Hypothesis ∀) |
| CITE-FAILURE | D1, D2 (scripted fake — both retry directions) |
| MISSINGINFO-1 | D5, D6, D11 (deterministic from 3 signals) |
| HASH-1 | D4, D11 (shared CANON-SER; compute + verify owned here) |
| SEC1-1 | D3, D6 (no `original_span` on any LLM-bound payload) |
| REPLAY-1 | D4, D11 (standalone verify outside rules-replay; ReplayService excludes memo_hash) |
| TEMP0-1 | D2 (central temp=0; fake records params) |
| ADVISORY-1 | D3 (advisory-only fields/enums + prompt template) |
| PROV-1 | D2, D8 (Gemini P1; Phase-2 seams not wired) |
| PERF-1 | D10 (observed, not gated) |
| OBS-1 | D10 (allowlist emit-only) |

**No Mermaid in this artifact.** All decisions reference-not-own; no frozen FD/contract re-opened; no new cross-cutting dependency beyond LangGraph + the Gemini adapter.

---

*End of tech-stack-decisions.md.*
