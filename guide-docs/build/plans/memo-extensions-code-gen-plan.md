# Code Generation — Plan (Part 1) — `memo-extensions` (U19, C4, **Phase 2**)

**Stage**: BUILD → per-unit loop → **Code Generation Part 1 (Plan)** · **Unit**: U19 `memo-extensions` · C4 · **Phase 2** · **Depth**: comprehensive · **Date**: 2026-07-17
**Built ON** the frozen FD (**BR-MEXT-1..13**; the **four-module** inventory; the **`OutlierSignal`** structural Protocol; the **construction-time** thinking mechanism; the MCP **supplementary / read-only / demographic-free** boundary; **FD-MEXT-Fold-1..5**) **+** approved NFR Requirements (**fifteen `NFR-MEXT-*`**; the load-bearing **ROUTE-1**/**FROZEN-1** pair + **GROUND-1**; **`MCP-TRANSPORT-DEFERRED`**; **NFR-MEXT-Fold-1..4**) **+** approved NFR Design (**patterns `P-MEXT-1..11`**; **components `C-MEXT-1..6`** with exact signatures; **NFR-ND-MEXT-Fold-1..3**; **§0 the permanent record**) — **re-opening none.** **Python 3.12, pytest TDD tests-first, leaf-first** — mirroring every realized backend unit (`backend/<unit>/` + `tests/`, `pyproject` `--cov`, the `outlier-model` (U18) sibling precedent). **This plan is the single source of truth for `memo-extensions` Code Generation.**

**Status**: **PART 2 GENERATED** — the six `[Answer]` tags (§7) are FILLED (all A); the mandatory ambiguity-check RAN → **one genuine gap surfaced (THINK-1(b) vs the frozen 3-kwarg `LLMClient` seam) → resolved by user decision (R2, §7.1)**; §4 Steps 0–9 executed TDD tests-first / leaf-first (all `[x]`). `backend/memo_extensions/` realized (4 production modules + 15 test files + `structural.py`/`fixtures.py`). Backend suite **1096 passed / 31 skipped** (1011 baseline + **85** new; the 5 pre-existing Docker errors unchanged); `backend/memo_extensions` **100%**; the `--cov-fail-under=90` gate holds at **99.85%**. **STOPPED at the Code-Generation 2-option completion gate.** **This is the LAST stage for `memo-extensions`.**

**Two registered open items carried, re-opened by neither**: **`OUTLIER-IN-PROSE`** (held out of scope structurally by `OutlierSignal`'s narrowness — P-MEXT-5 — + the SCOPE-1 scan) · **`MCP-TRANSPORT-DEFERRED`** (the live MCP protocol binding deferred to composition/deploy-config U23; explicitly **non-blocking** — every BR-MEXT-6/7/8/9 tooth lives in the **handler layer**, verified at tier-U with no MCP package present).

---

## 1. What Code-Gen builds (and what it must NOT touch)

### 1.1 Builds — six logical components as code + their TDD tests, in **exactly four module files** under `backend/memo_extensions/`
The frozen layout (`unit-of-work.md:70–71`) names **four files, no fifth**: `borderline_router.py` · `mcp_tools.py` · `provider_secondary.py` · `provider_showcase.py`. The six `C-MEXT-*` components map onto those four (three handler components share `mcp_tools.py`), plus the **test-only** `StructuralGuard` substrate under `tests/`. **This is a backend Python library** (no JS/JSX — contrast the six UI units).

### 1.2 Does NOT touch (held closed)
- **`memo-agent-core` (U4, frozen P1)** — its **production** module is **imported only**, **never** its test file; **no file under `backend/memo_agent_core/` modified**.
- **`outlier-model` (U18)** — reached **only by shape** via the U19-local `OutlierSignal` Protocol; **never imported**.
- **`rules-engine` / `audit-store`** — consumed **read-only** via their frozen `R` edges (`RuleResultReport`/`Rulebook`; committed records through the injected `DecisionRecordSource`).
- **`ui-outlier-view` (U20)**, **WIRE-1**, the **closed composition root** (`backend/app/`), the **17 frozen P1 units**, **tier-B** (N/A + unauthorized), the **`audit_store` Docker-guard gap** — all untouched. **No consumer** (`observability`/`llm-judge`) imported; **no other unit started**.

### 1.3 Guardrails held (skill + NFR-Design)
- **#1 advisory-only** (CONTRACT-1 — no output contract, recommendation-change unrepresentable) · **#3 no-LLM-in-the-deterministic-path** (ROUTE-1 — the router is pure, LLM-free) · **#4 temperature=0** on all three providers, both modes (TEMP0-1) · **#5 reproducibility** (ROUTE-1 + AGNOSTIC-1) · **#6 bias-free** (BIAS-1 — demographic-free by construction) · **#8 explainability** (GROUND-1 — every citation is report-member, frozen validator unchanged). **No new dependency** (`MCP-TRANSPORT-DEFERRED` holds; `requirements.txt` NOT edited). **Header comments are explicit Code-Gen deliverables documenting each by-construction guarantee — documentation only, NEVER enforcement** (NFR-Design §0; the frozen self-evidence convention).

---

## 2. Component → module map (`backend/memo_extensions/`) — signatures pinned in `logical-components.md`

| Component | Module (frozen layout) | Exports / role | Header-comment deliverable (documentation only, never enforcement) |
|---|---|---|---|
| **C-MEXT-1 `BorderlineRouter`** + the **`OutlierSignal`** Protocol | `borderline_router.py` | `route_borderline(rule_report, outlier_signal=None) -> ThinkingMode` — **no client/provider param exists**; `@runtime_checkable class OutlierSignal(Protocol)` = exactly `{is_outlier, outlier_score}`; the two named constants `RULE_PROXIMITY_MARGIN`, `OUTLIER_SCORE_CUTOFF` | **✔ explicit**: holds **no LLM client**; **both triggers deterministic** (FR-MEMO-6); the outlier value is **handed in, never imported** (Q2-A); the minimal read surface is itself the scope guard |
| **C-MEXT-2 `RulebookTools`** (handler surface 1) | `mcp_tools.py` | `describe_rules(rule_ids: Sequence[str]) -> list[RuleDescription]` — **no applicant-shaped parameter exists** | **✔ explicit**: **read-only**; **supplementary only**; **no citation may originate from a retrieval** (Q7-A); **demographic-free by construction** (takes no applicant) |
| **C-MEXT-3 `DecisionsTools`** (handler surface 2) | `mcp_tools.py` | `recent_precedent(query: PrecedentQuery) -> list[PrecedentSummary]`; `__init__(record_source: DecisionRecordSource)` (injected; fake at tier-U) | **✔ explicit**: **read-only**; **supplementary only**; **no citation may originate here**; **`PrecedentSummary` carries no `full_name`/`gender`/`city`/`demographics` field** (demographic-free by construction) |
| **C-MEXT-4 `McpToolService`** — owns the append + marker (Q3-A) | `mcp_tools.py` | `supplementary_context(rule_report) -> SupplementaryContext`; `supplementary_block(context) -> str` (PURE); `compose_prompt(base_prompt: str, context) -> str` (PURE) = `base + SUPPLEMENT_MARKER + block` | **✔ explicit**: `compose_prompt`/`supplementary_block` are **pure, non-persisting** members (enumerated); **no `prompt_builder` import** (Fold-2); U4's `build()` output is **only appended to** — `str` immutability makes modification unrepresentable (Fold-1) |
| **C-MEXT-5 `ClaudeAdapter`** (secondary, **tested**) | `provider_secondary.py` | `__init__(client: LLMClient, *, model: str, thinking_mode: ThinkingMode = STANDARD)`; `complete(self, prompt, schema) -> MemoDraftOutput` (**exactly** 3 params); `model_version -> str` | **✔ explicit**: `temperature=0` fixed **centrally, never caller-controlled** (TEMP0-1 part ii); the thinking mode arrives **at construction** because the frozen `complete()` admits no such parameter (Fold-1) |
| **C-MEXT-5 `OllamaAdapter`** (showcase, **wired-only ≠ untested**) | `provider_showcase.py` | identical constructor + `complete` shape; `model_version -> str` | **✔ explicit**: same central `temperature=0`; thinking arrives at construction; **exempt from memo-quality gates only**, never the decision-level gates (BR-MEXT-10) |
| **C-MEXT-6 `StructuralGuard`** substrate | `tests/structural.py` (+ `tests/*`) | the **eight** AST/import scans of P-MEXT-10, each with a **mandatory detector self-test**; **not a runtime dependency** | — (test-only) |

**Read-projection types U19 declares** (handler-side, **not** LLM-output contracts — the CONTRACT-1 carve-out, P-MEXT-9): `RuleDescription`, `PrecedentSummary` (frozen, `extra="forbid"`, **no demographic field**), plus the small helper types `SupplementaryContext`, `PrecedentQuery`, and the injected Protocols `DecisionRecordSource`, `McpTransport` (fake at tier-U; its real binding is **`MCP-TRANSPORT-DEFERRED`**). **See Q5** — the CONTRACT-1 scan must target **LLM-output / `Recommendation`-producing** models, not "all `BaseModel` subclasses", so it does not false-flag these read projections.

**Tests** live in `backend/memo_extensions/tests/` (mirroring every realized backend unit: `fixtures.py`, `structural.py`, `test_*.py`). **No file under any frozen `backend/<unit>/` tree is created or modified.**

---

## 3. TDD test → `NFR-MEXT-*` target map (every target at its NFR-pinned tier; **15/15, no orphan**)

| Target | Test (file :: focus) | Tier / Rigor |
|---|---|---|
| **ROUTE-1** *(load-bearing, full-highest)* | `test_route_borderline.py` — **purity teeth** (same `(report, signal)` → identical `ThinkingMode` across N≥2, no retained state); **trigger teeth** (REFER ⇒ EXTENDED; within margin ⇒ EXTENDED; outside ⇒ STANDARD; score above cutoff ⇒ EXTENDED); **boundary teeth** (value **exactly at** each threshold lands on the intended side, `<=` vs `<` **explicit**); **constants parameterized OFF the named constant**, never a hardcoded number (CG-OUT-Fold-1 precedent) · **+ `structural.py` scan #1**: router **import ALLOW-LIST** subset check **+ synthetic `import anthropic` detector self-test** | structural (AST) + component (teeth) / **full (highest)** |
| **FROZEN-1** *(load-bearing, full-highest)* | `test_frozen_boundary.py` — the **two mirrored facts re-asserted locally against U4's PRODUCTION module** (`from backend.memo_agent_core.provider import route_borderline`; `import ... as provider_module`): `route_borderline()` **raises `NotImplementedError`** (mirrors frozen `test_route_borderline_is_a_not_wired_stub`); `dir(provider_module)` has **no** `Claude`/`Ollama`/`Mcp`/`MCP` name (mirrors frozen `test_only_gemini_adapter_is_present_no_claude_ollama_mcp`); **U4's test file is NOT imported** · **+ `structural.py` scan #7**: U19's `backend.*` imports ⊆ **{`memo_agent_core`, `rules_engine`, `audit_store`}** + **no `memo_agent_core.tests.*`** + self-test | component (behavioral) + structural / **full (highest)** |
| **GROUND-1** | `test_grounding.py` — **direct retrieval-miss test against the REAL frozen `CitationValidator`** (a rule in the `Rulebook` but ABSENT from the handed report → `citation_failure` with that id); **append-only composition** proven via **`str` immutability** (`base` unchanged; `composed is not base`); the **`SUPPLEMENT_MARKER` non-citable marker** present in the composed prompt · **+ scan #8**: no U19 path appends to `cited_rule_ids` + self-test | component (teeth) + structural / full |
| **SIGNAL-1** | `test_signal.py` — **by-shape fake** drives every routing test (no U18 import in tests); **interop self-test** building a **real U18 `OutlierResult` BY VALUE** (never imported) and asserting `isinstance(..., OutlierSignal)` against the **`@runtime_checkable`** Protocol (verified discriminating on 3.12.10); **`None`-degrades teeth** (`route_borderline(report, None)` == rule-proximity-only result) · **+ scan #2**: no `outlier_model` import + self-test | component + structural / full |
| **AGNOSTIC-1** | `test_agnostic.py` — identical `(report, signal)` → identical `ThinkingMode` under **all three** provider selections; router source references **no** provider/adapter name; an **Ollama** adapter constructed with `EXTENDED` **still completes** (degrades, never raises) | component + structural / full |
| **THINK-1** | `test_adapters_think.py` — the frozen **signature assertion applied to BOTH new adapters** (`inspect.signature(complete).parameters == ["self","prompt","schema"]`; each `isinstance` the `runtime_checkable ProviderAbstraction`); **offline capturing-double**: `EXTENDED` construction → thinking-configured outgoing request, `STANDARD` → not; mode is **construction-time only** | component (offline doubles) + structural / full |
| **TEMP0-1** | `test_adapters_temp0.py` — capturing double records **`temperature == 0`** on **every** call from **every** adapter (Claude + Ollama), in **BOTH** modes; **no `temperature` parameter** on `complete` (part ii); value set **centrally** inside the adapter | component (offline doubles) + structural / full |
| **MISS-1** | `test_miss.py` — with **both** handlers unavailable (fake transport failing / timing out / empty), drafting still yields a **valid `MemoDraftOutput`** whose citations **pass** the frozen gate; failure path adds **no** prompt content; the miss is **observable**, not silent | component (teeth) / full |
| **MCPRO-1** | `test_readonly.py` — neither handler exposes a write/mutate/commit member; both edges exercised **read-only** · **+ scan #5**: no write/mutate/commit member; no `DecisionCommitService` / write-transport / session-write import — the forbidden-member list is **SEMANTIC** (persistence/mutation/transport), **not word-matching on "output-producing"**, so it **correctly does NOT flag `compose_prompt`/`supplementary_block`** (Fold-1) + self-test | structural / full |
| **BIAS-1** | `test_bias.py` — **`decisions-tools` swap teeth** (fake source seeded with records differing **ONLY** in `full_name`/`gender`/`city` over identical financials → **byte-identical** output projection); **`rulebook-tools` by-construction** (takes no applicant input ⇒ cannot leak — strictly stronger than a swap test that could not fail) · **+ scan #4**: no `full_name`/`gender`/`city`/`.demographics` read over **both** handler surfaces + synthetic-`record.demographics.city` self-test | structural + component (teeth) / full |
| **CONTRACT-1** | `test_contract.py` — `MemoDraftOutput`/`DecisionMemo`/`MemoAgentInput` **unmodified**; **QA-5** (the LLM cannot change a recommendation) holds for **Claude and Ollama** exactly as for Gemini (unrepresentable — no recommendation field) · **+ scan #6**: no **LLM-output model** declared / no `Recommendation`-producing path under `backend/memo_extensions/` (**scoped per Q5**, so the two read projections are not false-flagged) + self-test | structural / full |
| **SCOPE-1** | **`structural.py` scan #3** — **zero** `flagged_features`/`shap_value`/`provenance` references anywhere under `backend/memo_extensions/` **+ mandatory detector self-test** (synthetic `result.flagged_features` read must be flagged, so it cannot pass vacuously); the supplementary section contains **no** outlier content | structural / full |
| **PROVGATE-1** | `test_provgate.py` — the **Ollama** adapter **IS** unit-tested offline (constructed; `temperature=0` asserted; structured output parsed) — *"wired-only" ≠ untested*; decision-level gates hold identically; its groundedness/promptfoo exemption is a **governance fact recorded** (owned by `llm-judge` U22), **NOT a U19 code test** | component (a/b) + governance (c) / full · governance |
| **PERF-1** | `test_perf_observed.py` — adapter/handler cost **recorded/observed, non-gating**; nothing timed at tier-U (every provider + transport is a double) | observed / soft |
| **SEC-1** | governance — the Security-Guardrails table (no runtime test); enforced by review + the scans above | N/A (governance) |

**Every `NFR-MEXT-*` mapped; no orphan.** No test imports a consumer, U4's test file, `outlier_model`, or exercises a live LLM / live MCP server / tier-B corpus.

### 3.1 The `StructuralGuard` substrate (`tests/structural.py`) — the eight scans of P-MEXT-10 (each AST-based, each with a mandatory detector self-test)
1. **router import ALLOW-LIST** (subset check; synthetic `import anthropic` flagged) → ROUTE-1
2. **no `outlier_model` import** → SIGNAL-1
3. **no `flagged_features`/`shap_value`/`provenance` reference** → SCOPE-1
4. **no demographic read** over **both** handler surfaces → BIAS-1
5. **no write/mutate/commit member; no write-transport import** (**SEMANTIC** list — Fold-1) → MCPRO-1
6. **no LLM-output model / no `Recommendation`-producing path** (**scoped per Q5**) → CONTRACT-1
7. **`backend.* ⊆ {memo_agent_core, rules_engine, audit_store}` + no `memo_agent_core.tests.*`** → FROZEN-1
8. **no append to `cited_rule_ids`** → GROUND-1

**Scan 1 ⊂ Scan 7 by construction** (Fold-3) — the router's allow-list is **tighter** than the unit rule (it excludes `audit_store`), so the two **agree** rather than needing reconciliation. AST-based (mirroring the frozen `auth_rbac/tests/test_no_forbidden_imports.py` + `outlier_model/tests/structural.py` precedent), robust against comments/strings a text scan would misfire on.

---

## 4. Leaf-first build order (numbered Part-2 steps — **NOT executed**; on explicit go, TDD tests-first)

- [x] **Step 0 — Scaffold** `backend/memo_extensions/` (`__init__.py`, `tests/__init__.py`) + add `--cov=backend/memo_extensions` to `pyproject` `addopts` (Q6). Backend suite still collects the **1011 passed / 31 skipped** baseline. **No new dependency; `requirements.txt` NOT edited.**
- [x] **Step 1 — `borderline_router.py`** *(leaf — deps only its allow-listed imports)*: the `@runtime_checkable OutlierSignal` Protocol (`{is_outlier, outlier_score}`), `route_borderline(rule_report, outlier_signal=None) -> ThinkingMode`, the two named constants + header comment. **Tests-first**: `test_route_borderline.py` (ROUTE-1 purity/trigger/boundary/constants), `test_signal.py` (SIGNAL-1 by-shape + interop-by-value + None-degrades), `test_agnostic.py` (AGNOSTIC-1). → **ROUTE-1, SIGNAL-1, AGNOSTIC-1, SCOPE-1**
- [x] **Step 2 — the frozen-boundary mirror** (`tests/test_frozen_boundary.py`, **depends only on `memo_agent_core`'s PRODUCTION module**): the two re-asserted facts + the no-test-file-import discipline. → **FROZEN-1** (behavioral half)
- [x] **Step 3 — `mcp_tools.py` handler surfaces**: `RulebookTools` + `DecisionsTools` + their frozen-shape `RuleDescription` / `PrecedentSummary` (frozen, `extra="forbid"`, no demographic field) + `PrecedentQuery` + the injected `DecisionRecordSource` Protocol + header comments. **Tests-first**: `test_readonly.py` (MCPRO-1), `test_bias.py` (BIAS-1 — decisions-tools swap teeth + rulebook-tools by-construction). → **MCPRO-1, BIAS-1**
- [x] **Step 4 — `mcp_tools.py` `McpToolService`**: composes both handler surfaces; owns `SUPPLEMENT_MARKER` + `supplementary_context` / `supplementary_block` / `compose_prompt` (append-only) + the injected `McpTransport` seam (fake at tier-U) + header comment (no `prompt_builder` import). **Tests-first**: `test_grounding.py` (GROUND-1 — direct retrieval-miss against the REAL frozen `CitationValidator`, str-immutability append, non-citable marker), `test_miss.py` (MISS-1). → **GROUND-1, MISS-1**
- [x] **Step 5 — `provider_secondary.py` + `provider_showcase.py`**: `ClaudeAdapter` + `OllamaAdapter` (construction-time thinking mode; central `_PRODUCTION_TEMPERATURE = 0`; `complete` exactly 3 params) + header comments. **Tests-first**: `test_adapters_think.py` (THINK-1), `test_adapters_temp0.py` (TEMP0-1), `test_provgate.py` (PROVGATE-1), `test_contract.py` (CONTRACT-1). → **THINK-1, TEMP0-1, AGNOSTIC-1 (adapter half), CONTRACT-1, PROVGATE-1**
- [x] **Step 6 — `tests/structural.py` — the remaining `StructuralGuard` scans** (§3.1 scans, each with a detector self-test; Scan 1 ⊂ Scan 7 by construction) + `tests/fixtures.py` shared seeded factory (Q2). → the **structural halves** of ROUTE/FROZEN/SIGNAL/BIAS/MCPRO/CONTRACT/GROUND + **SCOPE-1**
- [x] **Step 7 — `test_perf_observed.py`** (PERF-1, observed/soft, non-gating). → **PERF-1**
- [x] **Step 8 — Coverage / quality gate**: `backend/memo_extensions` at the comprehensive bar (`--cov-fail-under=90` unchanged); confirm the backend suite does **not regress** the **1011 passed / 31 skipped** baseline (pure **additive** module — **no P1 unit's tests touched**); confirm **U4's frozen suite stays green** — in particular the **two tests FROZEN-1 mirrors** (`test_route_borderline_is_a_not_wired_stub`, `test_only_gemini_adapter_is_present_no_claude_ollama_mcp`) and `test_complete_has_no_temperature_parameter` — **and is NOT collected twice** (U4's test file is never imported).
- [x] **Step 9 — Code summary**: `guide-docs/build/memo-extensions/code/code-summary.md` (module list + test→target map + realization notes); `testresults.txt` refreshed.

---

## 5. HOLDS (binding through Part 2)
- **`memo-agent-core` (U4, frozen) untouched** — its **production** module imported only, **never** its test file (**no `memo_agent_core.tests.*` import** — scan #7); `PromptBuilder` output **appended to, never parsed/re-templated**; `CitationValidator` **used unchanged as the single gate**; U4's `route_borderline` stub **stays not-wired**; **no file under `backend/memo_agent_core/` modified**.
- **`outlier-model` (U18)** reached **only by shape** via `OutlierSignal`, **never imported** (scan #2); the interop self-test builds `OutlierResult` **by value**.
- **`rules-engine` / `audit-store`** consumed **read-only** via their frozen `R` edges; the `audit-store` edge runs through the **injected `DecisionRecordSource`** — **no live DB**, so the **Docker-guard gap stays out of U19's test path and untouched**.
- **No new module** beyond the frozen four; **no new Pydantic LLM-output contract**; **no new dependency** (`MCP-TRANSPORT-DEFERRED` holds; `requirements.txt` NOT edited).
- **No live LLM call, no key, no network, no Docker, no live MCP server** at tier-U — every provider client + the MCP transport + the record source is an **injected double**.
- **`OUTLIER-IN-PROSE` stays OPEN and out of scope** — enforced by `OutlierSignal`'s narrowness (P-MEXT-5) + scan #3; **no `flagged_features`/`shap_value`/`provenance`** anywhere under `backend/memo_extensions/`.
- **The by-construction guarantees are HARD requirements**, each with its header comment (documentation only, never enforcement): the router's no-client signature + allow-list (P-MEXT-1); the mirrored boundary (P-MEXT-2); the sole-citation-gate + append-only str-immutability (P-MEXT-3); construction-time injection + central temp0 (P-MEXT-4); the minimal Protocol (P-MEXT-5); asymmetric demographic freedom (P-MEXT-6); the read-only handler surface (P-MEXT-7).
- **`ui-outlier-view` (U20), WIRE-1, the closed composition root, the 17 frozen P1 units — UNTOUCHED**; **tier-B NOT authorized** (and N/A); **no other unit started**; the **23-unit decomposition unchanged**.

---

## 6. Coverage / quality gate
- **Runner**: `pytest` over `backend/`, `--cov=backend/memo_extensions` added to `pyproject` `addopts` (Q6) — the **comprehensive-depth bar** this project applied to `rules-engine`/`audit-store`/`auth-rbac`/`outlier-model` (the `--cov-fail-under=90` gate **unchanged**).
- **Baseline (from the `outlier-model` completion)**: backend **1011 passed / 31 skipped** (+ the 5 pre-existing Docker-absence errors, unchanged). This is a **pure additive backend module** — **no P1 unit's tests touched**, no frozen file modified; the suite must not regress.
- **tier-U only**: every U19 test runs fast/deterministic in CI — **no Docker, no LLM, no key, no network, no live MCP server, no `corpus/`**; the 31 skips + 5 Docker errors are **unchanged** (U19 adds none). **U4's frozen test suite stays green and is NOT double-collected** (its test file is never imported).

---

## 7. Clarifying questions (`[Answer]` tags — **LEFT BLANK**; lettered; full text below)

> Fill these; I then run the mandatory **ambiguity-check** against the answers + the frozen FD (BR-MEXT-1..13) + approved NFR Requirements (fifteen `NFR-MEXT-*`) + approved NFR Design (`P-MEXT-1..11`, `C-MEXT-1..6`, all folds) — **surface-and-stop on any genuine gap, do not improvise** — then Part 2 (§4 Steps 0–9) **on your explicit go**. Per the standing convention the full Q&A is re-embedded once answered.

### Q1 — The router's import ALLOW-LIST: exact enumerated roots (ROUTE-1 / NFR-ND-MEXT-Fold-3)
The NFR-Design pins the allow-list as *"a small, enumerated, commented set … a SUBSET of FROZEN-1's `backend.* ⊆ {memo_agent_core, rules_engine, audit_store}`"*, with `audit_store` **deliberately absent** (it is `decisions-tools`' edge, not the router's). The remaining Code-Gen choice is the **exact enumerated contents**:

- **A.** The allow-list roots are exactly **`{__future__, typing, enum, dataclasses, backend.memo_agent_core.schemas, backend.rules_engine.report_schema}`** + U19-local (the module itself). `backend.rules_engine.report_schema` may be a **`TYPE_CHECKING`-only** import under `from __future__ import annotations`; the scan admits it either way. `dataclasses` is included only if a local dataclass is used, else dropped at generation and the comment says so. **The exact module paths (`…schemas` for `ThinkingMode`, `…report_schema` for `RuleResultReport`) are confirmed against the frozen files at Step 1.** *(Recommended — matches Fold-3 verbatim; tightest set that still compiles; `audit_store` deliberately excluded so Scan 1 ⊂ Scan 7 holds by construction.)*
- **B.** A **looser** allow-list also admitting `backend.memo_agent_core` at the **package root** (not just `.schemas`). Simpler to write, but widens the router's surface beyond what it needs and blurs Scan 1 ⊂ Scan 7.
- **C.** Other (describe).

`[Answer]:` A

### Q2 — Injected-double construction: the `LLMClient` capturing double, the MCP transport fake, the `DecisionRecordSource` fake
Every provider client, the MCP transport, and the decision-record source is an **injected double at tier-U** (no network, no key, no live server, no DB). Where do the doubles live and how are they shaped?

- **A.** A **shared `tests/fixtures.py`** builds: (i) a **capturing `LLMClient` double** recording each outgoing request (so THINK-1 can assert `EXTENDED`→thinking-configured / `STANDARD`→not, and TEMP0-1 can assert `temperature==0` every call) — mirroring U4's frozen `test_provider.py` capturing-double discipline; (ii) a **fake `McpTransport` / handler doubles** with **failing / timing-out / empty** variants for MISS-1; (iii) a **fake `DecisionRecordSource`** seeded with records — including a **swap pair** (identical financials, swapped `full_name`/`gender`/`city`) for BIAS-1 and a **retrieval-miss** shape; (iv) a **by-value U18 `OutlierResult`-shaped object** and a **U19-local `OutlierSignal` fake** for SIGNAL-1. One factory module reused across the teeth. *(Recommended — DRY; the `outlier-model`/`audit-store`/`memo_agent_core` shared-fixtures precedent; keeps every teeth test on the same seeded doubles.)*
- **B.** **Inline doubles per test file.** *(Rejected — the capturing client, the swap pair, and the failing-transport shapes recur across THINK-1/TEMP0-1/BIAS-1/MISS-1/PROVGATE-1.)*
- **C.** Other (describe).

`[Answer]:` A

### Q3 — Test-file organization within `backend/memo_extensions/tests/` (incl. where the frozen-boundary mirror lives)
- **A.** **One `test_*.py` per target-cluster** (the §3 map: `test_route_borderline.py`, `test_signal.py`, `test_agnostic.py`, `test_grounding.py`, `test_miss.py`, `test_readonly.py`, `test_bias.py`, `test_adapters_think.py`, `test_adapters_temp0.py`, `test_contract.py`, `test_provgate.py`, `test_perf_observed.py`) **+ a dedicated `test_frozen_boundary.py`** for the FROZEN-1 mirror (the **only** module that imports `memo_agent_core.provider` for assertion, kept isolated so the cross-unit-production-import is obvious and auditable) **+ `structural.py`** (the eight scans + self-tests) **+ `fixtures.py`**. Mirrors `outlier-model`'s `tests/` layout exactly. *(Recommended — one responsibility per file; the frozen-boundary mirror in its own file makes the deliberate production-module import self-documenting and easy to review.)*
- **B.** **Fold the frozen-boundary mirror into `structural.py`** (alongside the scans). Fewer files, but mixes a **behavioral** re-assertion (`pytest.raises`, `dir()`) into the AST-scan substrate and buries the one deliberate cross-unit import.
- **C.** Other (describe).

`[Answer]:` A

### Q4 — Realization-deferred strings & constants (`SUPPLEMENT_MARKER`, model strings, the two router constants)
These are pinned as **Code-Gen realizations** by the frozen artifacts (FD §6; NFR-Req §4 "Deferred to Code-Gen"):

- **A.** Choose at generation, each documented in-place: **`SUPPLEMENT_MARKER`** = an explicit, unmistakable non-citable delimiter (e.g. a bracketed banner line stating the section is supplementary / non-citable context — exact wording chosen at Step 4 and asserted present by GROUND-1c); **Claude/Ollama model strings** = a single module-level constant per adapter (e.g. a current Claude Opus 4.8 id and a local Ollama model name), **read from the injected config at composition — never hardcoded as a live endpoint**, with the tier-U tests driving the **injected double** so the literal value is immaterial to the suite; **`RULE_PROXIMITY_MARGIN` / `OUTLIER_SCORE_CUTOFF`** = one module-level literal each, **provisional post-calibration values** (the `Z_SCORE_FLAG_THRESHOLD=3.0` / CG-OUT-Fold-1 precedent), with **every threshold test parameterized OFF the named constant** so a future calibration is a one-constant edit with tests still green. *(Recommended — mirrors the sibling backend precedent; keeps the suite value-agnostic; a calibration change never breaks a test.)*
- **B.** **Ask for exact values now** (specific marker wording, specific model ids, specific margin/cutoff numbers) before Part 2. *(Available if you want to pin any of these explicitly rather than take the recommended provisional realizations.)*
- **C.** Other (describe).

`[Answer]:` A

### Q5 — CONTRACT-1 scan scope: **LLM-output / `Recommendation`-producing models only**, NOT "all `BaseModel` subclasses" *(a phrasing tension I am surfacing, not improvising)*
The frozen NFR-Design is **internally consistent on intent but loose in one phrasing**: `logical-components.md` C-MEXT-3 **declares `class PrecedentSummary(BaseModel)`** (a handler-side read projection), and `nfr-design-patterns.md` P-MEXT-9 explicitly carves those out — *"`PrecedentSummary`/`RuleDescription` are handler-side read projections, **not** LLM output contracts"* — scoping the scan to *"no **LLM-output model** declared"*. **But** the NFR-Design **plan** file's P-MEXT-9 line and NFR-Requirements CONTRACT-1 say *"zero `BaseModel` subclasses"* / *"no U19 module declares a Pydantic model"*, which — taken literally — would **false-flag the two frozen-declared read projections**. This must be resolved at Code-Gen (it mirrors the MCPRO-1 **semantic-not-word-match** guard, Fold-1):

- **A.** **Scope CONTRACT-1's scan #6 SEMANTICALLY**: it flags a **`Recommendation`-producing path** or an **LLM-output model** (a model returned by / parsed from an adapter's `complete`, or any model carrying a `recommendation`/`confidence`/verdict field), and **permits** the two frozen-declared handler-side read projections (`PrecedentSummary`, `RuleDescription`) — which carry **no** recommendation field and are **never** an LLM output. The scan's allow/deny is defined by **role** (LLM-output vs handler-read-projection), **never by "is it a `BaseModel`"** — with a **detector self-test** feeding a synthetic `recommendation: Recommendation` field and asserting it is flagged, and a **non-vacuity** assertion that the two read projections are present and **not** flagged. This is the reading the **authoritative frozen patterns file already states**; I adopt it rather than the plan file's looser "zero `BaseModel`" phrasing. *(Recommended — honors the frozen carve-out; the read projections are required by C-MEXT-3; avoids a scan that would contradict the frozen component definitions.)*
- **B.** **Literal "zero `BaseModel` subclasses"** — which would force `PrecedentSummary`/`RuleDescription` to be **non-`BaseModel`** (e.g. frozen `dataclass`es or `NamedTuple`s). Keeps the plain-language scan, but **changes the frozen C-MEXT-3 realization** (`PrecedentSummary(BaseModel)`, `extra="forbid"`) into a non-Pydantic shape — a larger deviation from the approved NFR-Design surface, and it loses `extra="forbid"`'s structural demographic-exclusion guarantee.
- **C.** Other (describe / or flag for a return to NFR-Design if you consider this a genuine re-open rather than a Code-Gen realization).

`[Answer]:` A

### Q6 — Test framework + coverage config for `backend/memo_extensions`
- **A.** **`pytest` (established) + `Hypothesis` where a universal-quantifier property earns it** (e.g. ROUTE-1 determinism / boundary over generated reports; BIAS-1 swap-invariance over generated demographic swaps) — parametrized tests elsewhere; **no new dependency** (both already in the stack). **Coverage**: add `--cov=backend/memo_extensions` to `pyproject` `addopts` at the **existing comprehensive bar** (`--cov-fail-under=90` **unchanged**); no `omit` (the unit has no live-DB/subprocess module). *(Recommended — matches every prior backend unit incl. the `outlier-model` sibling; Hypothesis strengthens the two load-bearing targets without a new dep.)*
- **B.** **`pytest` only** (parametrized, no Hypothesis); same coverage config. Simpler; loses generated-input strength on ROUTE-1/BIAS-1.
- **C.** Other (describe).

`[Answer]:` A

---

## 7.1 Ambiguity-check outcome + the R2 decision (embedded per the standing convention)

**Ambiguity-check RAN** against the six answers + the frozen FD (BR-MEXT-1..13) + NFR Requirements (fifteen `NFR-MEXT-*`) + NFR Design (`P-MEXT-1..11` / `C-MEXT-1..6`; all folds; §0 the permanent record), grounded in the ACTUAL frozen shapes on disk (`provider.py`, `schemas.py`, `citation_validator.py`, `report_schema.py`, `rulebook_schema.py`, `record_schema.py`).

- **Q5 determination CONFIRMED — a legitimate Code-Gen realization, NOT an NFR-Design amendment** (three grounds): the authoritative frozen NFR-Design artifacts already state the semantic scoping and one *declares* `PrecedentSummary(BaseModel)`; **BIAS-1 (P-MEXT-6) load-bearingly requires** `PrecedentSummary` to be a typed model with no demographic field, so the literal "zero `BaseModel`" reading was never internally satisfiable; Q5-A *selects* the reading the governing (later, more-specific) stage already committed — no decision changes.
- **Five of six answers clean**, each verified against a frozen shape: Q1 allow-list realizable + Scan 1 ⊂ Scan 7 holds; ROUTE-1 rule-proximity computable from `RuleResultReport` alone; GROUND-1 realizable against the real `CitationValidator`; BIAS-1 swap teeth non-vacuous (`AuditRecord` embeds `ApplicantProfileSnapshot.profile` carrying demographics); Q2/Q3/Q4/Q6 mirror the `outlier-model` precedent.

**ONE GENUINE GAP surfaced → resolved by user decision:** `NFR-MEXT-THINK-1(b)` requires an adapter constructed with `thinking_mode=EXTENDED` to produce an **observable** thinking-configured outgoing request, but the frozen `memo_agent_core.LLMClient` seam is `generate(*, model, prompt, temperature) -> str` — **three kwargs, no thinking channel** — and `C-MEXT-5` types the adapters' constructor as `client: LLMClient`.

**DECISION — R2 (user-approved):** U19's two new adapters drive a **U19-local thinking-aware client seam** — `ThinkingLLMClient.generate(*, model, prompt, temperature, thinking: bool)` (in `provider_secondary.py`) — that the capturing double implements. `thinking` is a real request parameter (as on the actual Claude/Gemini APIs); `EXTENDED → thinking=True`, `STANDARD → thinking=False`, giving THINK-1(b) real, non-vacuous teeth. The frozen `memo_agent_core.LLMClient` / Gemini path is **untouched**; the deviation is scoped to the two new adapters only. **R1 rejected** (a thinking-variant model string misrepresents the real APIs); **R3 rejected** (injection-only makes `thinking_mode` inert → THINK-1(b) vacuous). Disclosed in `code-summary.md §3`.

---

## 8. Gate
**PART 2 GENERATED — STOPPED at the Code-Generation 2-option completion gate.** The six `[Answer]` tags (Q1–Q6) are FILLED (all A); the ambiguity-check ran (§7.1 — one gap surfaced, resolved by R2); §4 Steps 0–9 executed leaf-first / tests-first (all `[x]`). **This was the LAST stage for `memo-extensions`.** Backend **1096 passed / 31 skipped** (1011 baseline + 85 new; 5 pre-existing Docker errors unchanged — **zero regression**); `backend/memo_extensions` **100%**; `--cov-fail-under=90` holds at **99.85%**; U4's frozen suite green **and not double-collected** (its three FROZEN-1-relevant tests each collected exactly once from `memo_agent_core`). WIRE-1 · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-agent-core` (U4) + all 17 frozen P1 units · the closed composition root — **UNTOUCHED**; **no new dependency**; **`OUTLIER-IN-PROSE`** and **`MCP-TRANSPORT-DEFERRED`** stay OPEN and out of scope / non-blocking; tier-B NOT authorized (N/A); the `audit_store` Docker-guard gap untouched; no other unit started; the 23-unit decomposition unchanged.
