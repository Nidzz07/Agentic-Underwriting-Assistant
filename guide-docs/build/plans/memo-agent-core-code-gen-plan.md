# Code Generation Plan (Part 1) — `memo-agent-core` (C4 / U4)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: cluster unit **4 of 4 — the LAST** (where the LLM enters) · FD ✅ → NFR Requirements ✅ → NFR Design ✅ (approved 2026-07-06) → **Infrastructure Design SKIPPED-logged ✅ (2026-07-06)** → **Code-Gen ← here (Part 1 plan)**.
**Unit**: U4 `memo-agent-core` · **Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** · **Depth**: comprehensive (invariant-bearing; CON-BR2 load-bearing; determinism despite an LLM).
**Status**: **Plan — awaiting `[Answer]:` tags. NO CODE written this stage. Stop after this plan.**

Built **ON** the frozen FD + frozen C4 contract + approved **15 `NFR-MEMO-*`** targets + the **10 NFR-Design components/patterns** (`nfr-design-patterns.md` / `logical-components.md`) — **re-opening none**. **TDD, tests-first, leaf-first.** **Every test runs against the injected `FakeProvider` — no live LLM / no network anywhere in the unit suite.** Reference-not-own throughout.

**On this unit's completion**: `memo-agent-core` becomes the **FOURTH fully-complete unit** and **closes the cluster** (intake+document-sanitizer, rules-engine, audit-store, memo-agent-core). This Code-Gen **realizes the memo_hash compute+verify carry-forward** and codes CON-BR2's three structural layers.

---

## 1. Package / module layout (`backend/memo_agent_core/`)

Mirrors the established convention (`backend/<unit>/` package + `tests/` with `test_<module>.py`, `tests/fixtures/`). Imports are **read-only, unchanged**: rules-engine `RuleResultReport` / `evaluation_output` / `Rulebook`, intake `ApplicantProfile`, shared `backend/common/canon_ser.py` + `decimal_context.py`.

```text
backend/memo_agent_core/
  __init__.py
  schemas.py            # MemoAgentInput, DecisionMemo, MemoDraftOutput, CitationValidationResult,
                        #   MissingInformationItem, MissingInfoSource enum, ThinkingMode stub (Phase-2 seam)
  constants.py          # MEMO_CITATION_RETRY_CAP (>=2) — the ONE retry-cap source of truth
  memo_hash_adapter.py  # MemoHashAdapter — compute(memo_content)->str + verify(recorded_hash, memo_content)->bool
  missing_info.py       # MissingInfoDeriver — fixed TOTAL cross-source order
  citation_validator.py # CitationValidator — report-membership + belt-and-suspenders rulebook check
  provider.py           # ProviderAbstraction (Protocol) + GeminiAdapter (P1) + not-wired Phase-2 stubs
  prompt_builder.py     # PromptBuilder — scoped to MemoAgentInput; advisory-only template; no MCP
  input_builder.py      # MemoAgentInputBuilder — clean artifacts only; no original_span
  orchestrator.py       # LangGraphOrchestrator — draft->validate->retry/finalize (+flag); checkpointer YES/interrupt NO
  assembler.py          # MemoAssembler (finalize) — inject RO recommendation/confidence; compute memo_hash
  telemetry.py          # TelemetryEmitter — emit-only allowlist
  tests/
    __init__.py
    fixtures/
      __init__.py
      fake_provider.py  # scripted, call-count-aware FakeProvider (records params)
      factories.py      # synthetic MemoAgentInput / RuleResultReport / ApplicantProfile builders (DATA-4)
    test_schemas.py  test_memo_hash_adapter.py  test_missing_info.py  test_citation_validator.py
    test_provider.py  test_prompt_builder.py  test_input_builder.py  test_orchestrator.py
    test_assembler.py  test_telemetry.py  test_subflow_e2e.py   # end-to-end sub-flow against the fake
```

**Component → module map** (the 10 NFR-Design components):
MemoAgentInputBuilder→`input_builder` · PromptBuilder→`prompt_builder` · ProviderAbstraction+GeminiAdapter+FakeProvider→`provider`(+`tests/fixtures/fake_provider`) · CitationValidator→`citation_validator` · MissingInfoDeriver→`missing_info` · MemoHashAdapter→`memo_hash_adapter` · MemoAssembler→`assembler` · LangGraphOrchestrator→`orchestrator` · TelemetryEmitter→`telemetry` · (CONBR2-COMMIT = no-commit absence, asserted in `test_orchestrator`/`test_subflow_e2e`).

---

## 2. TDD test → target map (every target + binding FD rule has a test; all vs the FakeProvider)

| Target / FD rule | Test(s) (module) | Assertion |
|---|---|---|
| **CONBR2-TYPE** | `test_schemas`, `test_assembler` | `MemoDraftOutput` has only `narrative_prose` + `cited_rule_ids`; `DecisionMemo.recommendation`/`confidence` `RO`, no setter; a fake emitting a rec cannot populate it. |
| **CONBR2-STATE** | `test_orchestrator` | fake returns contradictory prose → `DecisionMemo.recommendation` == injected value; no node writes the rec/confidence channels. |
| **CONBR2-COMMIT** | `test_orchestrator`, `test_subflow_e2e` | no `DecisionCommitService` constructed anywhere in the unit; memo rec is display-only. |
| **GROUND-1** | `test_prompt_builder`, `test_input_builder` | prompt built only from `MemoAgentInput`; no MCP client constructed in P1. |
| **CITE-1** | `test_citation_validator` (Hypothesis ∀) | ∀ cited ids not in the report → `citation_failure` + offending ids; all-valid → `valid`. |
| **CITE-FAILURE** | `test_orchestrator` — `test_retry_recovers_within_cap` + `test_retry_exhausts_cap` | **both import `MEMO_CITATION_RETRY_CAP`**; recover at k≤cap→finalize; always-hallucinate→flag; injected rec unchanged. |
| **MISSINGINFO-1** | `test_missing_info` | fixed TOTAL cross-source order; identical list ×N independent of fake output; every item traces to a signal. |
| **HASH-1** | `test_memo_hash_adapter` | deterministic ×N; hashed-field change → different hash; volatile change → same hash; byte-identical to an independent `canon_ser` recompute. |
| **REPLAY-1** | `test_memo_hash_adapter` | standalone `verify` recompute-and-compare; **no `ProviderAbstraction` constructed**; memo not in the rules-equality set. |
| **SEC1-1** | `test_schemas`, `test_input_builder` | `MemoAgentInput` has no `original_span`/`SanitizationReport` field; serialized LLM-bound payload contains no forensic span. |
| **TEMP0-1** | `test_provider`, `test_orchestrator` | fake records params → `temperature==0` on every call incl. every retry draft; central, not per-call. |
| **ADVISORY-1** | `test_prompt_builder`, `test_schemas` | fields/enums use "recommendation" (`-RECOMMEND` suffix); prompt template asserts advisory language; no "decision" framing. |
| **PROV-1** | `test_provider` | `route_borderline` not-wired stub; only Gemini adapter present; abstraction injectable (fake drives all). |
| **PERF-1** | `test_telemetry` | duration emitted; no latency-failing check. |
| **OBS-1** | `test_telemetry` | emitter schema structurally carries no prose/demographic/free-text/`original_span`. |
| FD BR-GROUND / BR-CITE-* / BR-CONBR2-* / BR-MISSINGINFO / BR-SEC1-NOINGEST / BR-TEMP0 / BR-ADVISORY | as above | each binding FD rule pinned by ≥1 test. |

---

## 3. Implementation order (leaf-first, tests-first)

Each step = write the test(s) first, then the module, until green; coverage held ≥90% (QA-6) throughout.

- **Step 0** — package skeleton (`__init__`, `constants.MEMO_CITATION_RETRY_CAP`, `tests/` scaffold, factories for DATA-4 synthetic inputs).
- **Step 1** — `schemas.py` (MemoAgentInput / DecisionMemo / MemoDraftOutput / CitationValidationResult / MissingInformationItem + MissingInfoSource enum; RO recommendation/confidence; no `original_span`). → CONBR2-TYPE, SEC1-1, ADVISORY-1.
- **Step 2** — `memo_hash_adapter.py` (compute + standalone verify, delegating to unchanged `canon_ser`). → HASH-1, REPLAY-1.
- **Step 3** — `missing_info.py` (`MissingInfoDeriver`, fixed TOTAL cross-source order). → MISSINGINFO-1.
- **Step 4** — `citation_validator.py` (report-membership + rulebook check; Hypothesis). → CITE-1.
- **Step 5** — `provider.py` (`ProviderAbstraction` Protocol + `GeminiAdapter` P1 + Phase-2 not-wired stubs) + `tests/fixtures/fake_provider.py` (scripted, call-count-aware, records params). → PROV-1, TEMP0-1.
- **Step 6** — `prompt_builder.py` (scoped to MemoAgentInput; advisory template; no MCP). → GROUND-1, ADVISORY-1.
- **Step 7** — `input_builder.py` (`MemoAgentInputBuilder`; clean artifacts only). → GROUND-1, SEC1-1.
- **Step 8** — `orchestrator.py` (`LangGraphOrchestrator`; draft→validate→retry/finalize +flag; read-only rec/confidence channels; `MEMO_CITATION_RETRY_CAP`; checkpointer YES/interrupt NO). → CONBR2-STATE, CITE-FAILURE (both directions), CONBR2-COMMIT.
- **Step 9** — `assembler.py` (`MemoAssembler` finalize; inject RO rec/confidence; call `MemoHashAdapter.compute`). → CONBR2-TYPE.
- **Step 10** — `telemetry.py` (`TelemetryEmitter`, emit-only allowlist). → OBS-1, PERF-1.
- **Step 11** — `test_subflow_e2e.py` (end-to-end memo sub-flow against the fake: happy path → pending DecisionMemo; retry recover; retry exhaust → flag; CON-BR2 across the flow; no live LLM). 
- **Step 12** — coverage gate (backend-wide `--cov-fail-under=90`, QA-6) + rule-coverage/target-coverage confirmation; `testresults.txt` refreshed; code-summary written.
- **Step 13** — completion: mark plan steps [x]; back-annotate the FD **only if** a realization note arises (flagged, faithful — like intake's BR-GATE-REASON / rules-engine's derived-scalar operands); present the 2-option gate.

---

## 4. Clarifying questions (fill each `[Answer]:` tag)

## Question 1 — Test framework
A) **pytest + pytest-cov (≥90%, QA-6) + Hypothesis** (CITE-1 ∀) + the injected **scripted FakeProvider** — **no live LLM / no network** anywhere; same base toolchain as intake/rules-engine/audit-store. *(Recommended.)*
B) Add a live-provider smoke test (rejected — non-deterministic, network, cost; that is quality-gates' eval). · C) Other.

[Answer]: A — pytest + pytest-cov (≥90%, QA-6) + Hypothesis (CITE-1 ∀) + the injected scripted FakeProvider — no live LLM/no network anywhere; same base toolchain as intake/rules-engine/audit-store.

## Question 2 — FakeProvider scripting mechanism
A) **A call-count-aware scripted fake** — constructed with an ordered list of canned `MemoDraftOutput`s (returns the i-th on the i-th call, last repeats), **records every call's params** (asserts `temperature==0`); a helper builds the two CITE-FAILURE scripts (recover-at-k / always-hallucinate). Deterministic, no I/O. *(Recommended.)*
B) A fake that hashes the prompt to pick output (rejected — opaque, harder to script both directions). · C) Other.

[Answer]: A — a call-count-aware scripted fake constructed with an ordered list of canned MemoDraftOutputs (returns the i-th on the i-th call, last repeats), records every call's params (asserts temperature==0); a helper builds the two CITE-FAILURE scripts (recover-at-k / always-hallucinate). Deterministic, no I/O.

## Question 3 — LangGraph package + checkpointer class (P1)
A) **`langgraph` (pinned) with an in-process `MemorySaver` checkpointer for P1** (retry loop + step tracing within one request-scoped invocation; interrupt NO — gate external). No durable/cross-process backend provisioned here; a durable store, if ever needed, reuses the `database` unit's Postgres (reference-not-own) — consistent with the logged Infra SKIP. *(Recommended.)*
B) A Postgres-backed checkpointer now (rejected — provisions infra this unit doesn't own; Infra was SKIPPED for exactly this reason). · C) Other.

[Answer]: A — langgraph (pinned) with an in-process MemorySaver checkpointer for P1 (retry loop + step tracing within one request-scoped invocation; interrupt NO — gate external). No durable/cross-process backend provisioned here; a durable store, if ever needed, reuses the database unit's Postgres (reference-not-own) — consistent with the logged Infra SKIP.

## Question 4 — Module placement / package boundary
A) **`backend/memo_agent_core/` as a self-contained package** (§1 layout), importing rules-engine/intake/shared-common **read-only, unchanged**; no edit to any shared or sibling module (no fork of `canon_ser`). *(Recommended.)*
B) Place memo code under an existing package (rejected — breaks the one-unit-one-package convention). · C) Other.

[Answer]: A — backend/memo_agent_core/ as a self-contained package, importing rules-engine/intake/shared-common read-only, unchanged; no edit to any shared or sibling module, no fork of canon_ser.

## Question 5 — Retry-cap constant single-sourcing (NFR-Design §5 sharpening)
A) **`MEMO_CITATION_RETRY_CAP` defined ONCE in `constants.py` (value ≥ 2)** and **imported by both** `test_retry_recovers_within_cap` (recovers at k ≤ cap) **and** `test_retry_exhausts_cap` (exhausts exactly cap) — **no duplicated literals**; the orchestrator reads the same constant. *(Recommended.)*
B) Hard-code the cap in each test (rejected — divergence risk; the sharpening explicitly forbids it). · C) Other.

[Answer]: A — MEMO_CITATION_RETRY_CAP defined ONCE in constants.py (value ≥ 2) and imported by both test_retry_recovers_within_cap (recovers at k ≤ cap) and test_retry_exhausts_cap (exhausts exactly cap) — no duplicated literals; the orchestrator reads the same constant.

## Question 6 — GeminiAdapter in P1 (build vs stub) + N/A layers
A) **Build the `GeminiAdapter` (real structured-output + central temperature=0 wiring) but exercise the whole unit suite with the FakeProvider** — **NO live Gemini call in this unit's tests** (a live call needs a key + network + is non-deterministic; live groundedness is quality-gates' eval per FR-PROV-GATE-2). **N/A for this unit's Code-Gen: any live-LLM test, MCP wiring, Claude/Ollama adapters, `route_borderline` logic (Phase-2 named-not-wired stubs).** *(Recommended.)*
B) Leave GeminiAdapter a stub too (rejected — PROV-1 wants the P1 adapter present). · C) Wire a live call in tests (rejected — non-deterministic/network). · D) Other.

[Answer]: A — build the GeminiAdapter (real structured-output + central temperature=0 wiring) but exercise the whole unit suite with the FakeProvider — no live Gemini call in this unit's tests (live groundedness is quality-gates' eval per FR-PROV-GATE-2). N/A for this unit's Code-Gen: any live-LLM test, MCP wiring, Claude/Ollama adapters, route_borderline logic (Phase-2 named-not-wired stubs).

## Question 7 — Depth confirmation
A) **Comprehensive** — invariant-bearing; CON-BR2 load-bearing; determinism despite an LLM; same class as the other three cluster units. *(Recommended.)*
B) Lighter (describe). · C) Other.

[Answer]: A — comprehensive. Invariant-bearing; CON-BR2 load-bearing; determinism despite an LLM; same class as the other three cluster units.

---

## 5. Constraints & settled items held (not re-opened)
- Frozen FD + C4 contract + approved 15 `NFR-MEMO-*` + the 10 NFR-Design components/patterns are the inputs — Code-Gen realizes them, re-opening none.
- **Reference-not-own**: rules-engine `RuleResultReport`/`evaluation_output`/`Rulebook`; intake `ApplicantProfile`; shared `canon_ser`/`decimal_context` (**unchanged**, via `MemoHashAdapter`); audit-store persist/replay (`ReplayService` excludes `memo_hash`); LLM provider (injected; fake in tests); `outlier-model` (Phase 2, `None` in P1); `memo-extensions` (Claude/Ollama/MCP/`route_borderline` — Phase-2 named-not-wired); `observability`; `quality-gates`.
- **CON-BR2 load-bearing** — three independent layers coded + tested. **No LLM** in the deterministic path / tests (fake) / replay. **temperature=0** central. **Advisory-only** naming.
- **`memo_hash`** compute + verify owned solely here (named `MemoHashAdapter`) — **closes the audit-store carry-forward**; byte-identical via the shared `canon_ser`. **`missing_information`** fixed total cross-source order (byte-stability). **`MEMO_CITATION_RETRY_CAP`** single-sourced.
- Runtime **Python 3.12**; **DATA-4** synthetic only. The other cross-unit constraint (**ATOMIC-1** co-location) remains tracked on the `database` unit — not this unit's Code-Gen.

## 6. Next step (STOP here)
Fill the seven `[Answer]:` tags. On your signal I will read the answers, run the mandatory ambiguity-check (adding a clarification only if needed), then **generate Part 2** — tests-first, leaf-first, Steps 0–13 — writing code to `backend/memo_agent_core/` (never `guide-docs/`), and stop at the Code-Gen 2-option gate. **NO code is written until the answers are in, checked, and you give the explicit go.**
