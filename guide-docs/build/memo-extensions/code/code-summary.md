# Code Summary — `memo-extensions` (U19, C4, Phase 2)

**Stage**: BUILD → per-unit loop → **Code Generation Part 2 (generated)** · **Unit**: U19 `memo-extensions` · C4 · **Phase 2** · **Depth**: comprehensive · **Date**: 2026-07-17.
**Built ON** the frozen FD (**BR-MEXT-1..13**), approved NFR Requirements (**fifteen `NFR-MEXT-*`**), approved NFR Design (**`P-MEXT-1..11`** / **`C-MEXT-1..6`**) — re-opening none. TDD tests-first, leaf-first; `python -m pytest`. **This was the LAST stage for `memo-extensions`.**

**Result**: backend **1096 passed / 31 skipped** (1011 baseline + **85** new; the 5 pre-existing `audit_store` Docker-absence errors unchanged) · `backend/memo_extensions` **100%** statements/branches on every file · global gate `--cov-fail-under=90` holds at **99.85%** · U4's frozen suite green **and not double-collected**.

---

## 1. Modules generated (`backend/memo_extensions/` — the frozen four + tests)

| Module | Components | Role |
|---|---|---|
| `__init__.py` | — | package doc |
| `borderline_router.py` | **C-MEXT-1** `BorderlineRouter` + the `@runtime_checkable OutlierSignal` Protocol | deterministic, provider-agnostic extended-thinking trigger; `route_borderline(rule_report, outlier_signal=None) -> ThinkingMode`; `RULE_PROXIMITY_MARGIN` + `OUTLIER_SCORE_CUTOFF` |
| `mcp_tools.py` | **C-MEXT-2** `RulebookTools`, **C-MEXT-3** `DecisionsTools`, **C-MEXT-4** `McpToolService` + `RuleDescription`/`PrecedentSummary`/`PrecedentQuery`/`SupplementaryContext`/`DecisionRecordSource` + `SUPPLEMENT_MARKER` | two read-only supplementary/demographic-free surfaces + the append-only prompt composer |
| `provider_secondary.py` | **C-MEXT-5** `ClaudeAdapter` + `ThinkingLLMClient` (R2 seam) + `_parse_xml` | Claude Opus 4.8 secondary (tested); central `temperature=0`; construction-time thinking |
| `provider_showcase.py` | **C-MEXT-5** `OllamaAdapter` | Ollama showcase (wired-only ≠ untested); same seam + central `temperature=0` |
| `tests/` | **C-MEXT-6** `StructuralGuard` (`structural.py`) + `fixtures.py` + 15 `test_*.py` | 85 TDD tests |

**No fifth module. No new dependency (`requirements.txt` NOT edited). No new LLM-output Pydantic contract.**

## 2. Test → target map (15/15 `NFR-MEXT-*`, each at its NFR-pinned tier)

| Target | Test file | Tier / rigor |
|---|---|---|
| **ROUTE-1** (load-bearing) | `test_route_borderline.py` (15) + `test_structural_guard.py` scan 1 | structural + component / **full-highest** |
| **FROZEN-1** (load-bearing) | `test_frozen_boundary.py` (3) + scan 7 | component + structural / **full-highest** |
| GROUND-1 | `test_grounding.py` (4) + scan 8 | component + structural / full |
| SIGNAL-1 | `test_signal.py` (5) + scan 2 | component + structural / full |
| AGNOSTIC-1 | `test_agnostic.py` (3) | component + structural / full |
| THINK-1 | `test_adapters_think.py` (7) | component (offline doubles) + structural / full |
| TEMP0-1 | `test_adapters_temp0.py` (6) | component + structural / full |
| MISS-1 | `test_miss.py` (3) | component (teeth) / full |
| MCPRO-1 | `test_readonly.py` (5) + scan 5 | structural / full |
| BIAS-1 | `test_bias.py` (4) + scan 4 | structural + component (teeth) / full |
| CONTRACT-1 | `test_contract.py` (3) + scan 6 | structural / full |
| SCOPE-1 | scan 3 | structural / full |
| PROVGATE-1 | `test_provgate.py` (2) | component + governance / full |
| PERF-1 | `test_perf_observed.py` (1) | observed / soft |
| SEC-1 | governance (the scans + review) | N/A |

**StructuralGuard = eight AST scans, each with a mandatory detector self-test**: (1) router import allow-list · (2) no `outlier_model` import · (3) no `flagged_features`/`shap_value`/`provenance` · (4) no demographic read over `mcp_tools` · (5) no write member / no write-transport import (semantic) · (6) no LLM-output model / no `Recommendation`-producing path (Q5-A) · (7) `backend.* ⊆ {memo_agent_core, rules_engine, audit_store}` + no `memo_agent_core.tests.*` · (8) no append to `cited_rule_ids`. **Scan 1 ⊂ Scan 7 by construction** (the router's allow-list excludes `audit_store`).

## 3. Realization notes (Code-Gen decisions — disclosed, none improvised)

### R2 — the thinking-aware client seam (the one genuine gap surfaced at the ambiguity-check, resolved by user decision)
**The gap found**: the frozen `memo_agent_core.LLMClient` Protocol is `generate(*, model: str, prompt: str, temperature: float) -> str` — **three kwargs, no thinking channel** — yet `NFR-MEXT-THINK-1(b)` (full rigor) requires an adapter constructed with `thinking_mode=EXTENDED` to **produce an observable thinking-configured outgoing request** (recorded by a capturing double), with `temperature` fixed at 0 and the citable prompt unaltered. That observability cannot be achieved faithfully through the frozen 3-kwarg seam.
**Resolution (R2, user-approved)**: U19's two new adapters drive a **U19-local thinking-aware client seam** — `ThinkingLLMClient.generate(*, model, prompt, temperature, thinking: bool)` — defined in `provider_secondary.py`. The capturing double implements it, so `EXTENDED → thinking=True` / `STANDARD → thinking=False` is a **real, non-vacuous, provider-API-faithful** request parameter (thinking is a request parameter on the actual Claude/Gemini APIs, not a model change). The deviation is scoped to the **two new adapters only**; the frozen `memo_agent_core.LLMClient` / Gemini path is left completely **untouched**.
**Why R1 rejected**: encoding thinking in the frozen seam's `model` string would misrepresent the real Claude/Gemini APIs (thinking is a request parameter, not a model). **Why R3 rejected**: baking thinking only into the injected client (per FD §2.2's literal words) would make the adapter's `thinking_mode` param causally inert and THINK-1(b) vacuous — against this project's non-vacuity discipline.

### CONTRACT-1 scan scope (Q5-A)
Scan #6 is scoped **semantically**: it asserts the adapters' `complete()` return type is the frozen `MemoDraftOutput` (no U19-declared LLM-output model) and that no production field/return is annotated `Recommendation`/`Confidence`. It **permits** the two frozen-declared handler-side read projections `PrecedentSummary`/`RuleDescription` (`BaseModel`, `extra="forbid"`) — honoring the authoritative frozen patterns file over the plan/NFR-Req's looser "zero `BaseModel`" phrasing. Confirmed at the ambiguity-check as a legitimate Code-Gen realization of already-consistent intent (not an NFR-Design amendment): BIAS-1 (P-MEXT-6) load-bearingly *requires* `PrecedentSummary` to be a typed model with no demographic field, so the literal reading was never internally satisfiable.

### Rule-proximity realization
`RULE_PROXIMITY_MARGIN` is a **relative** margin (fraction of the threshold), so one named constant is unit-agnostic across heterogeneous thresholds. Proximity uses a **deterministic `float()`** of a `Decimal` ratio — this is *routing*, not rule evaluation (CON-DET-1's no-float-in-evaluation rule is out of scope; determinism is proven by the ROUTE-1 purity teeth). Both `RULE_PROXIMITY_MARGIN` (0.05) and `OUTLIER_SCORE_CUTOFF` (0.5) are **provisional post-calibration** values; every threshold test parameterizes OFF the named constant (CG-OUT-Fold-1 precedent). The router imports neither `Decimal` nor `DecimalRange` — threshold shapes are duck-typed — keeping its import allow-list tight.

### Realization-deferred strings (Q4-A)
`SUPPLEMENT_MARKER` = an explicit `===== SUPPLEMENTARY CONTEXT (NON-CITABLE) =====` banner (asserted present by GROUND-1). Model strings arrive at construction (`model=`) from injected config — never hardcoded live endpoints; tier-U tests drive the injected double, so the literal value is immaterial.

## 4. HOLDS honored
- **U4 (frozen) untouched** — production module imported only, never its test file (`no memo_agent_core.tests.*` — scan 7, verified); `PromptBuilder` output only appended to; `CitationValidator` used unchanged as the single citation gate; `route_borderline` stub stays not-wired.
- **U18 never imported** — reached only by shape via `OutlierSignal`; interop self-test builds `OutlierResult` **by value**.
- **rules-engine / audit-store** consumed read-only via their frozen edges; audit-store runs through the **injected `DecisionRecordSource`** (no live DB — the Docker-guard gap stays out of U19's path and untouched).
- **No new dependency**; **`OUTLIER-IN-PROSE`** held out of scope structurally (`OutlierSignal` narrowness + scan 3); **`MCP-TRANSPORT-DEFERRED`** stays open + non-blocking (every BR-MEXT-6/7/8/9 tooth verified at tier-U with no MCP package present).
- **`ui-outlier-view` (U20) / WIRE-1 / the closed composition root / the 17 frozen P1 units** untouched; **tier-B** N/A + NOT authorized; **no other unit started**; the 23-unit decomposition unchanged.
