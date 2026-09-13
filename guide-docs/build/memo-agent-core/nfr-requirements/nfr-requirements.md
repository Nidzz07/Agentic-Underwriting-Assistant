# NFR Requirements — `memo-agent-core` (C4 / U4)

**Phase / Stage**: BUILD → NFR Requirements, **Part 2 (finalized targets)**
**Loop position**: cluster unit **4 of 4 — the LAST cluster unit** (where the LLM enters) · FD ✅ → **NFR Requirements ← here** → NFR Design → [Infra likely SKIP] → Code-Gen.
**Unit**: U4 `memo-agent-core` — grounding, citation validation, CON-BR2, SEC-1-FORENSIC non-ingestion, temperature=0, advisory-only, deterministic `missing_information`, `memo_hash` compute **and** verify.
**Date**: 2026-07-06 · **Runtime**: Python **3.12 pinned** · **Depth**: **comprehensive** (invariant-bearing; **CON-BR2 is load-bearing**; determinism must hold **despite an LLM in the loop**).
**Built ON**: the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) + the frozen C4 contract (`component-methods.md`) — **re-opening neither**. Every `NFR-MEMO-*` below is a pass/fail testable assertion.

---

## 0. Central testability principle (the load-bearing decision)

The LLM is reached **only** through an **injected `ProviderAbstraction`** (a Protocol). In the unit test suite that abstraction is a **deterministic fake** that returns canned/scripted structured output (`narrative_prose` + `cited_rule_ids`) and **records the call params** it was invoked with. Consequently:

- **Every** deterministic invariant below is unit-testable against the fake — **no live LLM, no network, anywhere in this unit's suite**, *including the bounded-retry loop* (the fake is call-count/scripted-aware).
- Live-provider **groundedness** (QA-4, LLM-as-judge ≥ 4/5) is **`quality-gates`' eval**, on Gemini + Claude only (FR-PROV-GATE-2) — **not this unit's gate**.
- The fake is the boundary at which `temperature=0` is asserted (it captures every call's params).

**Reference-not-own throughout**: rules-engine's `RuleResultReport` / `evaluation_output` / `Rulebook`; intake's `ApplicantProfile`; the shared `backend/common/canon_ser.py` (audit-store §2.1 spec authority, **unchanged**) + `decimal_context`; audit-store's persistence/replay; the LLM provider (injected; fake in tests); `outlier-model` `OutlierResult` (Phase 2); `memo-extensions` (Claude/Ollama/MCP/`route_borderline` — Phase 2); `observability`; `quality-gates`.

---

## 1. Finalized `NFR-MEMO-*` targets (pass/fail testable)

### CON-BR2 — the LLM cannot alter the recommendation (three non-overlapping structural layers)

CON-BR2 is **load-bearing**. It is held by **three independent** layers — no single point of trust; any one layer's failure is still blocked by the other two. Each layer has its **own distinct test** (not one test implicitly covering two).

#### NFR-MEMO-CONBR2-TYPE — *type layer*
- **Target**: The LLM's structured-output schema (what the model fills) contains **only** `narrative_prose` + `cited_rule_ids` — **no `recommendation` / `confidence` field**. On `DecisionMemo`, `recommendation` + `confidence` are **`RO`** (injected by the orchestrator from `rule_report`), with **no writable field/setter** through which model output can reach them.
- **Pass/fail test**: (a) assert the model output schema declares no recommendation/confidence field; (b) a fake provider that **emits** a recommendation in its structured output **cannot** populate `DecisionMemo.recommendation` — it is unrepresentable / does not parse into a recommendation. "The LLM changed the recommendation" fails to typecheck/parse.
- **Traces**: FD `business-rules.md` **BR-CONBR2-TYPE**, `domain-entities.md §2` (RO markers) · **CON-BR2**, QA-5, US-MEMO-1.

#### NFR-MEMO-CONBR2-STATE — *graph-state layer*
- **Target**: In the LangGraph memo sub-flow, `recommendation` + `confidence` enter as **read-only input channels**; **no node has write access**. The graph's output is prose + citations + `missing_information` — never a recommendation.
- **Pass/fail test**: a fake provider returning prose that **contradicts** the recommendation → `DecisionMemo.recommendation` == the **injected** value, unchanged; a structural assertion that no graph node can mutate the recommendation/confidence channels.
- **Traces**: FD `business-logic-model.md §2.1` + `business-rules.md` **BR-CONBR2-STATE** · **CON-BR2**, QA-5.

#### NFR-MEMO-CONBR2-COMMIT — *commit-path layer*
- **Target**: `memo-agent-core` has **no commit / finalize-decision path**; the memo is advisory output only. The **committed** recommendation routes `rules-engine → DecisionCommitService` (in `audit-store`) via `recommendation_id`, **bypassing the memo**; the commit **never** sources the recommendation from `DecisionMemo`.
- **Pass/fail test**: assert `memo-agent-core` instantiates **no** `DecisionCommitService` and makes **no** commit call; the memo's `recommendation` field is display/citation-only. (Consistent with the built audit-store `commit` — it takes `recommendation_id`, never a memo.)
- **Traces**: FD `business-logic-model.md §4.1` + `business-rules.md` **BR-CONBR2-COMMIT** · **CON-BR2**, QA-5.

### Grounding + citation validation (G6 / FR-MEMO-3, failure mode #1)

#### NFR-MEMO-GROUND-1
- **Target**: The prompt/context is built **only** from the handed `MemoAgentInput` clean artifacts. **Phase-1 has NO MCP / no tool fetch** to re-derive what fired (retrieval-miss guard).
- **Pass/fail test**: the prompt-builder's sole input is `MemoAgentInput`; assert **no MCP client is constructed** anywhere in the P1 unit.
- **Traces**: FD `business-rules.md §1` **BR-GROUND** · FR-MEMO-3, G6, MCP Phase-2 boundary.

#### NFR-MEMO-CITE-1
- **Target**: `validate_citations(memo_draft, rulebook) -> CitationValidationResult` — every `cited_rule_id` **must be a member of the handed `RuleResultReport`** (authoritative grounding), and, belt-and-suspenders, present in the active `rulebook`; else `outcome = citation_failure` with the offending ids listed.
- **Pass/fail test** (Hypothesis ∀): for all cited ids **not** in the report → `citation_failure` + offending ids surfaced; all-valid → `valid`. Pure function — no provider call.
- **Traces**: FD `business-rules.md §2` **BR-CITE-VALIDATE**, `domain-entities.md §3` · FR-MEMO-3, US-MEMO-3.

#### NFR-MEMO-CITE-FAILURE — *bounded retry, tested in BOTH directions*
- **Target**: On `citation_failure` the memo is **BLOCKED, not surfaced**. A **bounded retry** (capped) re-drafts; **if the retry recovers within the cap → `finalize`** (valid memo); **if the cap is exhausted → the memo is flagged/blocked** and **the deterministic recommendation from C2 still stands** (LLM out of the decision path). **No hallucinated rule ever reaches the underwriter.**
- **Pass/fail test** (two **explicit, named** tests, driven by the **scripted call-count-aware fake** — see the tech-stack decision):
  1. **recover-within-cap → finalize**: a fake scripted to cite a hallucinated id on the first draft(s) then a **valid** citation on a later attempt **within the cap** → the graph reaches `finalize` with a valid `DecisionMemo`; the injected `recommendation` is unchanged.
  2. **exhaust-cap → flag**: a fake that **always** cites a hallucinated id → after the capped retries the memo is **blocked/flagged** and `recommendation` (injected) is unchanged.
  Both run entirely against the fake — **no live LLM in the retry loop**.
- **Traces**: FD `business-rules.md §2` **BR-CITE-FAILURE**, `business-logic-model.md §1` (retry/flag edges) · FR-MEMO-3 (failure mode #1), CON-BR2.

### `missing_information` determinism (G3 / CON-DET-1)

#### NFR-MEMO-MISSINGINFO-1
- **Target**: The structured `missing_information` list is derived **DETERMINISTICALLY** from three signals in the handed inputs — **NOT LLM-authored**:
  - (i) intake `DocumentManifest` entries with `status ∈ {missing, unparseable}` (via `applicant_profile_clean.documents`),
  - (ii) `RuleResult`s with `status == not_evaluated` (via `rule_result_report.rule_results`),
  - (iii) `profile.incomplete == true` (via `applicant_profile_clean`),
  each → a `MissingInformationItem{source, detail}` (`source ∈ {missing_document, unparseable_document, not_evaluated_rule, incomplete_flag}`).
- **Pass/fail test**: same inputs → **identical** `missing_information` ×N **regardless of the (fake) LLM output** (a fake returning different prose does not change the structured list); every item traces to a deterministic signal (source enum); the prose may render the list but the **structured field is authoritative**.
- **Traces**: FD `business-rules.md §4` **BR-MISSINGINFO**, `domain-entities.md §2.1` · reviewer **G3**, CON-DET-1. *(All three signals confirmed reachable in the built contracts: `DocumentManifest.entries[].status` MISSING/UNPARSEABLE, `RuleStatus.NOT_EVALUATED`, `ApplicantProfile.incomplete: bool`.)*

### `memo_hash` — shared CANON-SER + **memo-agent-core-owned compute AND verify** (closes the audit-store carry-forward)

#### NFR-MEMO-HASH-1 — *(corrected ownership wording)*
- **Target**: `memo_hash` = a deterministic hash over the memo's **canonical content** (`narrative_prose`, `cited_rule_ids`, `missing_information`, `recommendation`, `confidence`; **volatile metadata — `timestamp`, etc. — excluded**), computed **once at `finalize`** via a **`memo-agent-core`-local adapter that delegates to the single shared `backend/common/canon_ser.py`** (audit-store §2.1 spec) — **referenced, UNCHANGED, not re-declared**.
- **Ownership (corrected — the built system, verified against `replay_service.py`)**: **`memo-agent-core` is the SOLE owner of BOTH computing `memo_hash` (at finalize) AND verifying it** (a **separate, standalone recompute-and-compare** — recorded hash vs a freshly recomputed hash of the stored memo content, **no LLM**). **`audit-store` stores `memo_hash` (a `str`, and does not store the memo text) and therefore structurally cannot re-derive it**; it never does. **The verify is NOT part of audit-store's `ReplayService`** (see NFR-MEMO-REPLAY-1) — it is this unit's own check, invoked **outside** the rules-replay path.
- **Pass/fail test**: (a) deterministic ×N (same content → same hash); (b) any hashed-field change → a different hash; volatile-metadata change → **same** hash; (c) **byte-identical** to an independent recompute via the shared util; (d) the standalone `verify(recorded_hash, memo_content) -> bool` recomputes-and-compares with **no `ProviderAbstraction` constructed** (no LLM).
- **Traces**: FD `domain-entities.md §5` + `business-logic-model.md §3` · CON-AUDIT-1, CON-DET-1. **Closes the Deferred-Decisions carry-forward** "memo-hash-verification ownership → memo-agent-core."

### SEC-1-FORENSIC non-ingestion (intake carry-forward)

#### NFR-MEMO-SEC1-1
- **Target**: `MemoAgentInput` (and **every** LLM-bound payload) **structurally cannot carry** `original_span` / the `SanitizationReport`. The neutralized injection cannot re-enter through the memo.
- **Pass/fail test** (schema-level + serialized-payload): `MemoAgentInput` declares no such field; the prompt-builder holds no reference to it; a canonical serialization of any LLM-bound payload contains **no forensic span**. *(Confirmed structurally in the built intake schema: `original_span` lives on `SanitizationReportEntry`, AUDIT-ONLY, segregated from `ApplicantProfile`.)*
- **Traces**: FD `business-rules.md §5` **BR-SEC1-NOINGEST**, `domain-entities.md §4` · **SEC-1-FORENSIC** (intake), failure mode #4.

### CON-DET-1 replay boundary

#### NFR-MEMO-REPLAY-1 — *(corrected wording)*
- **Target**: The memo is **NOT in the deterministic replay evaluation-equality set** (rules-engine's `evaluation_output` projection is — per the built `report.py`). On replay, **audit-store's `ReplayService` re-evaluates rules only and does NOT touch `memo_hash`** — the built `replay_service.py` **explicitly excludes `memo_hash` from its equality set** and never recomputes or compares it. **Memo integrity is a separate concern owned by `memo-agent-core`**: its **own standalone `memo_hash` recompute-and-compare (NFR-MEMO-HASH-1), invoked OUTSIDE the rules-replay path, never re-drafting** (no LLM in replay).
- **Pass/fail test**: (a) a structural assertion that the memo-integrity path constructs **no `ProviderAbstraction`** (never re-drafts); (b) the memo is not referenced in rules-engine's `evaluation_output` equality set; (c) the standalone verify is deterministic. **The target must not state or imply that `ReplayService` verifies `memo_hash` — it does not.**
- **Traces**: FD `business-logic-model.md §4.2` + `business-rules.md §7` (CON-DET-1 boundary) · CON-DET-1. Consistent with the built audit-store `ReplayService` (rules-only) and `AuditTuple` (stores `memo_hash` str only).

### Production-call rules

#### NFR-MEMO-TEMP0-1
- **Target**: **Every production LLM call uses `temperature=0`**, enforced **centrally** in `ProviderAbstraction.complete(prompt, schema)` (Gemini primary, P1), with structured **XML→Pydantic** output. The abstraction **cannot** issue a non-zero-temperature call.
- **Pass/fail test**: the fake provider records the params it was called with → assert `temperature == 0` on **every** call across the sub-flow (including every retry draft); a structural assertion that temperature is fixed centrally, not passed per-call by graph nodes.
- **Traces**: FD `business-rules.md §6` **BR-TEMP0** · FR-MEMO-2, FR-PROV-3, US-MEMO-2.

#### NFR-MEMO-ADVISORY-1
- **Target**: Advisory-only. Field names / enums use **"recommendation"** (`APPROVE | REFER | DECLINE-RECOMMEND`, `-RECOMMEND` suffix); the system-prompt template enforces advisory language; **"decision"** is reserved for the human's committed action (in audit-store).
- **Pass/fail test**: no user-facing/internal field or enum in this unit frames a final "decision"; the prompt-template asserts advisory language (a static template check — no provider call).
- **Traces**: FD `business-rules.md §6` **BR-ADVISORY** · FR-MEMO-4, US-MEMO-4, Brief §5.6.

#### NFR-MEMO-PROV-1
- **Target**: P1 = the **provider-abstraction interface (Protocol) + the Gemini adapter** + central temperature=0 + XML→Pydantic. **Claude / Ollama adapters, MCP `rulebook-tools`, `route_borderline` are Phase-2 (`memo-extensions`) — named seams, NOT wired here.**
- **Pass/fail test**: `route_borderline` is a not-wired stub (asserted); only the Gemini adapter is present in P1; the abstraction is **injectable** (a fake drives all unit tests).
- **Traces**: FD `business-logic-model.md §5` (phase boundary) · FR-PROV-1/2/3, FR-MEMO-5/6/7 (Phase-2).

### Performance / observability (scoped)

#### NFR-MEMO-PERF-1
- **Target**: LLM-call latency is **provider-bound + observed-only (soft budget)** — **not gated** (correctness / determinism / groundedness take precedence).
- **Pass/fail test**: duration is emitted; **no** latency-failing check exists. *(One of the two deliberate non-pass/fail-gated exceptions, mirroring rules-engine/audit-store PERF-1.)*
- **Traces**: FD scope · Brief §6 (observability), NFR posture.

#### NFR-MEMO-OBS-1
- **Target**: Telemetry is an **emit-only allowlist** (ids / enums / int counts / timing) — **no demographic / free-text / prose / `original_span`**. Langfuse tracing is owned by `observability` (reference-not-own).
- **Pass/fail test**: the telemetry schema **structurally carries no** prose/demographic/free-text/forensic field (a schema-level assertion).
- **Traces**: FD `business-rules.md §5` (SEC-1-FORENSIC extends to telemetry), phase boundary · Brief AC-7 (100% traced), SEC.

> **BACK-ANNOTATION (pinned at the register #33/#34 code-gen pass, 2026-09-12 — #34
> `CHECKPOINT-POISONS-REDRAFT`, candidate C2).**
> ⛔ **SUPERSEDED — this target's second sentence.** It read *"Langfuse 100%-step tracing **via the
> checkpointer** is wired by `observability` (reference-not-own)."* ⚠️ **That clause was false BEFORE
> C2 removed the checkpointer, and is not a consequence of the removal**: tracing was never wired
> through a checkpointer, and `observability.TraceRecorder.on_step` has **no production caller at
> all** — a gap owned by OBS-SINK-DEFERRED, not by this unit. ⚑ **OBS-1's actual requirement — the
> emit-only allowlist and its structural pass/fail test — is unchanged.** ⚠️ Brief **AC-7 (100%
> traced)** must therefore be read as **not currently met by any wiring**, which this pass records
> rather than fixes.

---

## 2. Story / invariant traceability

| Story / invariant | Target(s) |
|---|---|
| US-MEMO-1 (CON-BR2 — LLM cannot change the recommendation) | NFR-MEMO-CONBR2-TYPE / -STATE / -COMMIT |
| US-MEMO-2 / 4 (temperature=0, advisory-only) | NFR-MEMO-TEMP0-1, NFR-MEMO-ADVISORY-1 |
| US-MEMO-3 (citation / hallucination guard) | NFR-MEMO-GROUND-1, NFR-MEMO-CITE-1, NFR-MEMO-CITE-FAILURE |
| reviewer G3 (deterministic missing_information) | NFR-MEMO-MISSINGINFO-1 |
| CON-AUDIT-1 / replay (memo_hash) | NFR-MEMO-HASH-1, NFR-MEMO-REPLAY-1 |
| SEC-1-FORENSIC | NFR-MEMO-SEC1-1 |
| FR-PROV-1/3 (provider abstraction, P1 Gemini) | NFR-MEMO-PROV-1, NFR-MEMO-TEMP0-1 |
| AC-7 / SEC (observability, telemetry hygiene) | NFR-MEMO-OBS-1, NFR-MEMO-PERF-1 |

---

## 3. Security-Guardrails compliance (enabled extension — scoped)

| Guardrail | Applies | How held |
|---|---|---|
| Prompt-injection defense | ✅ | SEC-1-FORENSIC non-ingestion (**NFR-MEMO-SEC1-1**) — the neutralized span cannot re-enter the LLM context; the memo cites only from the handed report (**NFR-MEMO-GROUND-1**). |
| Input validation | ✅ | XML→Pydantic structured output; `validate_citations` rejects hallucinated ids (**NFR-MEMO-CITE-1/-FAILURE**). |
| Secrets management | N/A (this stage) | Provider API keys/config are `secrets-config` + the adapter's concern (reference-not-own); no secret is declared/handled in memo-agent-core's logic. |
| Read-only DB access for audit role | N/A | audit-store / `database` own persistence + role-grants (reference-not-own); this unit persists nothing (produces a pending memo + `memo_hash`). |
| Audit logging | ✅ (emit-only) | **NFR-MEMO-OBS-1** allowlist telemetry — no demographic/free-text/prose/forensic field. |

No blocking finding. N/A items are out of this unit's stage scope, not gaps.

---

## 4. Constraints & settled items held (not re-opened)

- **Frozen FD + frozen C4 contract** are the inputs — these targets pin testable assertions **ON** them, re-opening none.
- **Reference-not-own**: rules-engine `RuleResultReport` / `evaluation_output` / `Rulebook`; intake `ApplicantProfile`; shared `canon_ser.py` (**unchanged**) + `decimal_context`; the LLM provider (injected; fake in tests); `outlier-model` `OutlierResult` (Phase 2); `memo-extensions` (Claude/Ollama/MCP/`route_borderline` — Phase 2); `audit-store` (persist/replay); `observability`; `quality-gates`.
- **CON-BR2 is load-bearing** — the three structural layers are made testable, not re-opened.
- **The LLM only drafts prose** — no LLM in the deterministic path; **no LLM in tests** (fake provider); **no LLM in replay**.
- **`memo_hash`** shares audit-store's CANON-SER byte-for-byte; **memo-agent-core solely owns compute + verify** (audit-store stores it, cannot re-derive it; `ReplayService` excludes it).
- **`outlier_result` Phase-2-optional** (always `None` in P1). Runtime **Python 3.12**; **DATA-4** synthetic only.

---

*End of nfr-requirements.md. Tech-stack decisions → `tech-stack-decisions.md`. Next stage on approval: NFR Design (pattern selection per `NFR-MEMO-*` target).*
