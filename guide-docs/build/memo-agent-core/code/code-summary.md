# Code Summary — `memo-agent-core` (C4 / U4)

**Phase / Stage**: BUILD → Code Generation (Part 2 complete) · cluster unit **4 of 4 — the LAST** (where the LLM enters)
**Date**: 2026-07-06 · **Runtime**: Python **3.12.10** (matches the pin) · **Depth**: comprehensive
**Result**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓** — `memo-agent-core` is the **FOURTH fully-complete unit** and **closes the cluster** (intake+document-sanitizer, rules-engine, audit-store, memo-agent-core). **Realizes the memo_hash compute+verify carry-forward** and codes CON-BR2's three structural layers.

**No live LLM anywhere in the unit suite** — every test runs against the injected `FakeProvider`.

---

## 1. Modules (`backend/memo_agent_core/`) — 12 source modules, all 100% covered

| Module | Component | Realizes |
|---|---|---|
| `schemas.py` | MemoAgentInput / DecisionMemo / MemoDraftOutput / CitationValidationResult / MissingInformationItem / MissingInfoSource / ThinkingMode | CONBR2-TYPE, SEC1-1, ADVISORY-1 |
| `constants.py` | `MEMO_CITATION_RETRY_CAP = 2` (single source of truth) | CITE-FAILURE |
| `memo_hash_adapter.py` | MemoHashAdapter (compute + standalone verify) | HASH-1, REPLAY-1 |
| `missing_info.py` | MissingInfoDeriver (fixed total cross-source order) | MISSINGINFO-1 |
| `citation_validator.py` | CitationValidator (report-membership + rulebook) | CITE-1 |
| `provider.py` | ProviderAbstraction (Protocol) + GeminiAdapter (injected client) + route_borderline stub | PROV-1, TEMP0-1 |
| `prompt_builder.py` | PromptBuilder (scoped to MemoAgentInput; advisory template; no MCP; demographics excluded) | GROUND-1, ADVISORY-1 |
| `input_builder.py` | MemoAgentInputBuilder (clean artifacts only) | GROUND-1, SEC1-1 |
| `orchestrator.py` | LangGraphOrchestrator (draft→validate→retry/finalize+flag; read-only channels; MemorySaver) | CONBR2-STATE, CONBR2-COMMIT, CITE-FAILURE |
| `assembler.py` | MemoAssembler (finalize; inject RO rec/confidence; compute memo_hash) | CONBR2-TYPE |
| `telemetry.py` | TelemetryEmitter + MemoTelemetryEvent (emit-only allowlist) | OBS-1, PERF-1 |
| `tests/fixtures/{fake_provider,factories}.py` | scripted FakeProvider + synthetic builders (DATA-4) | (test harness) |

**Imports read-only, unchanged**: rules-engine `RuleResultReport`/`report.evaluation_output`/`Rulebook`; intake `ApplicantProfile`/`DocumentManifest`; shared `backend/common/canon_ser.py` (via `MemoHashAdapter`). **No shared-code edit, no fork.**

---

## 2. Test → target map (all 15 `NFR-MEMO-*` + binding FD rules, all vs the FakeProvider)

| Target | Named test(s) |
|---|---|
| **CONBR2-TYPE** | `test_schemas::test_memo_draft_output_rejects_an_emitted_recommendation`, `::test_decision_memo_recommendation_is_frozen_no_setter`; `test_assembler::test_recommendation_and_confidence_come_only_from_the_injected_input` |
| **CONBR2-STATE** | `test_orchestrator::test_contradictory_prose_does_not_change_the_recommendation`, `::test_read_only_channel_reducer_raises_on_write`, `::test_a_node_writing_the_recommendation_channel_is_rejected` |
| **CONBR2-COMMIT** | `test_orchestrator::test_orchestrator_constructs_no_commit_path` |
| **GROUND-1** | `test_prompt_builder::test_prompt_grounds_only_in_the_handed_report_rule_ids`, `::test_no_mcp_client_is_constructed_in_p1` |
| **CITE-1** | `test_citation_validator::test_valid_iff_every_cited_id_in_report_and_rulebook` (Hypothesis ∀), `::test_cited_in_rulebook_but_not_in_report_is_citation_failure` |
| **CITE-FAILURE** (both directions) | `test_orchestrator::test_retry_recovers_within_cap`, `::test_retry_exhausts_cap_then_flags_recommendation_stands` (both import `MEMO_CITATION_RETRY_CAP`) |
| **MISSINGINFO-1** | `test_missing_info::test_fixed_total_order_is_source_major_then_detail`, `::test_byte_stable_regardless_of_input_iteration_order` |
| **HASH-1** | `test_memo_hash_adapter::test_byte_identical_to_an_independent_canon_ser_recompute`, `::test_each_hashed_field_change_changes_the_hash`, `::test_missing_information_order_changes_the_hash` |
| **REPLAY-1** | `test_memo_hash_adapter::test_verify_true_on_match_false_on_content_tamper`, `::test_verify_constructs_no_provider`, `::test_memo_is_not_in_the_rules_replay_equality_set` |
| **SEC1-1** | `test_schemas::test_memo_agent_input_has_no_forensic_span_field`, `test_input_builder::test_builder_has_no_forensic_span_parameter` |
| **TEMP0-1** (two parts) | part i: `test_provider::test_gemini_adapter_builds_a_temperature_zero_request_offline`; part ii: `test_provider::test_complete_has_no_temperature_parameter` |
| **ADVISORY-1** | `test_schemas::test_recommendation_enum_is_advisory_with_recommend_suffix`, `test_prompt_builder::test_prompt_enforces_advisory_language` |
| **PROV-1** | `test_provider::test_route_borderline_is_a_not_wired_stub`, `::test_only_gemini_adapter_is_present_no_claude_ollama_mcp` |
| **PERF-1** | `test_telemetry::test_emit_appends_and_is_not_latency_gated` |
| **OBS-1** | `test_telemetry::test_event_carries_only_allowlist_fields` |

---

## 3. The three folds applied

1. **TEMP0-1 corrected (two parts).** The frozen `complete(prompt, schema)` carries **no temperature**; no fake records one at that boundary. Part (i): `GeminiAdapter` takes an **injected `LLMClient`** — a capturing test double asserts `temperature==0` **offline** (no network, no key). Part (ii): structural — `complete`'s params are exactly `(self, prompt, schema)`.
2. **Recover-within-cap script derived from the constant.** `recover_within_cap_script(cap)` builds `[hallucinate]*(cap-1) + [valid]` from `MEMO_CITATION_RETRY_CAP`; both retry tests import the one constant — no parallel literal can desync.
3. **Concrete cap value recorded (realization note).** `MEMO_CITATION_RETRY_CAP = 2` — the minimum satisfying "≥2 so both directions are distinct." A realization detail, not a new design decision.

---

## 4. Realization notes (flagged, faithful — no new public contract)

- **`validate_citations` kept its frozen 2-arg signature `(memo_draft, rulebook)`** (user decision at the Step-4 flag). The **authoritative `RuleResultReport`** — required by the FD's report-membership check but absent from the frozen signature — is supplied to `CitationValidator` **at construction**. The frozen signature is preserved exactly, so **no FD/component-methods back-annotation is needed**; documented here.
- **`GeminiAdapter` injected `LLMClient` seam** (approved NFR-Design sharpening) — the real google-genai client is wrapped to the minimal `generate(model, prompt, temperature)` seam at composition (a deploy-config/secrets concern, per the logged Infra SKIP); tests inject a capturing double.
- **Prompt excludes demographics** (name/city/gender) — bias-free by design (skill constraint 6); no demographic identifier reaches the LLM.
- **Telemetry `duration_ms` uses `time.perf_counter`** — observability only; it is **not** part of the memo, the `memo_hash`, or any evaluation output, so CON-DET-1 (no wall-clock in evaluation) is unaffected.

---

## 5. Coverage (Python 3.12.10)

- **Full backend suite: 539 passed / 4 skipped / total 99.74%** (QA-6 `--cov-fail-under=90` reached). No regression in intake / rules-engine / audit-store.
- **`memo_agent_core`: 100% on every source module** (12 modules; branch coverage on).
- The 4 skips are pre-existing intake `posix_only` (run in Linux CI); the residual TOTAL misses are pre-existing intake `resource_limits.py` + one rules-engine enum-exhaustive branch — **not** in this unit.
- `pyproject.toml`: added `--cov=backend/memo_agent_core` to `addopts` (per the documented "later units are added to `--cov`" convention). No other config change.
- Tier-1 `testresults.txt` refreshed at repo root via `pytest -v --cov=backend/memo_agent_core --cov-report=term-missing`.

---

## 6. Cross-unit constraints

- **CLOSED**: the **memo_hash-verification carry-forward** — `memo-agent-core` now owns both `MemoHashAdapter.compute` (at finalize) and `MemoHashAdapter.verify` (standalone recompute-and-compare, no LLM), delegating to the unchanged shared `canon_ser`; audit-store stores `memo_hash` and its `ReplayService` excludes it (verified against the built `replay_service.py`).
- **Still tracked** (not this unit): **ATOMIC-1** co-location on the `database` unit's schema.

---

*End of code-summary.md. This is the cluster's final unit — all four contract-bearing deterministic-core units are now fully complete.*
