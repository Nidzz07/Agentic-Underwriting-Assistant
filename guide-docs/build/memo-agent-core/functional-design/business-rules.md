# Business Rules — `memo-agent-core` (C4 / U4)

**Stage**: BUILD → Functional Design (per-unit) · cluster-FD-first unit 4 of 4 (the last)
**Unit**: U4 `memo-agent-core` (grounding, citation validation, CON-BR2, SEC-1-FORENSIC, advisory-only)
**Date**: 2026-07-03
**Scope**: The grounding rule, the citation-validation + hallucinated-citation rule, the
`missing_information` derivation rule, the SEC-1-FORENSIC non-ingestion rule, CON-BR2 across three
layers, temperature=0, advisory-only language. Every rule states its condition explicitly.

**Invariants held**: **CON-BR2** (LLM cannot alter the recommendation — QA-5), **temperature=0**
(FR-MEMO-2), **hallucination guard** (FR-MEMO-3, failure mode #1), **advisory-only** (FR-MEMO-4),
**SEC-1-FORENSIC** non-ingestion (intake carry), CON-DET-1 boundary, DATA-4.

---

## 1. Grounding (G6 — cite ONLY from the handed report; NO MCP in Phase 1)

### BR-GROUND
- The memo cites **ONLY** from the handed `RuleResultReport` (`rule_results` + `recommendation` +
  `confidence`) — the **authoritative what-fired** for this applicant. The prompt is built **only**
  from the handed clean artifacts (`MemoAgentInput`, `domain-entities.md §4`).
- **Phase 1 has NO MCP.** `memo-agent-core` does **not** call any tool to fetch/re-derive which
  rules fired — that would reintroduce the **retrieval-miss** inconsistency.
- **MCP `rulebook-tools` is Phase 2** (`memo-extensions`) and, even then, supplies **supplementary
  human-readable rule descriptions ONLY** — **never** used to decide *what fired* (that is always
  the handed report).

---

## 2. Citation validation + hallucinated-citation handling (FR-MEMO-3, failure mode #1)

`validate_citations(memo_draft, rulebook) -> CitationValidationResult`.

### BR-CITE-VALIDATE
- **Authoritative check**: every `cited_rule_id` in the draft **must be a member of the handed
  `RuleResultReport`** (the rules that were actually evaluated for this applicant). Membership is the
  grounding guard (BR-GROUND).
- **Belt-and-suspenders**: since the frozen signature also takes the `rulebook`, the check **may
  additionally confirm** each cited ID **exists in the active rulebook** — an ID absent from the
  rulebook is a pure hallucination; an ID in the rulebook but **not** in the report is a
  misapplication. **Both are `citation_failure`.**

### BR-CITE-FAILURE
- On any offending cited ID → **`outcome = citation_failure` → the memo is BLOCKED, not surfaced**
  (`services.md §6` Scenario 2). A **bounded retry** may re-draft (capped, `business-logic-model.md
  §2`); if it still fails, the memo is **flagged** and **the deterministic recommendation from C2
  still stands** — the LLM is out of the decision path (CON-BR2). **No hallucinated rule ever
  reaches the underwriter.**

---

## 3. CON-BR2 — the LLM cannot alter the recommendation (three non-overlapping layers)

The recommendation is read-only through **three** independent structural layers — no single point of
trust:

### BR-CONBR2-TYPE (type layer)
- `DecisionMemo` has **no writable `recommendation` field** the model populates
  (`domain-entities.md §2`): `recommendation`/`confidence` are **injected read-only** (`RO`); the
  model's structured output only fills `narrative_prose` + `cited_rule_ids`. "The LLM changed the
  recommendation" is **unrepresentable** at the type level.

### BR-CONBR2-STATE (graph-state layer)
- In the LangGraph memo sub-flow, `recommendation` + `confidence` enter as **read-only immutable
  state channels**; **no node has write access** to them (`business-logic-model.md §2`). The graph's
  output is prose + citations + `missing_information` — **never** a recommendation.

### BR-CONBR2-COMMIT (commit-path layer)
- The **committed** recommendation routes **`rules-engine` → `DecisionCommitService`** (in
  `audit-store`) **via `recommendation_id`**, **bypassing the memo entirely** (`business-logic-model.md
  §4`, the dual path). The commit **never** sources the recommendation from `DecisionMemo`. Even a
  contradictory memo prose cannot change what commits.

> **QA-5** (in `quality-gates`) asserts the LLM cannot change the recommendation — these three
> layers make that assertion hold structurally, not by post-hoc check.

---

## 4. `missing_information` derivation (deterministic — G3, the Q1↔Q3 fix)

### BR-MISSINGINFO
- The **structured `missing_information` list is derived DETERMINISTICALLY** from the handed inputs:
  intake's **completeness manifest** (documents `missing` / `unparseable`) **+** the
  **`not_evaluated` rule results** (rules whose operand was absent) **+** `profile.incomplete`.
- It is **NOT LLM-authored** → **reproducible** and grounded. The LLM `narrative_prose` **may render
  or reference** the list, but the **authoritative, persisted, surfaced** `missing_information` is
  the **deterministic structured field** (`domain-entities.md §2.1`) — the C5 MemoView UI element.
- Any divergence between the prose's wording and the structured list is resolved in favour of the
  **structured list** (it is the record).

---

## 5. SEC-1-FORENSIC non-ingestion (intake carry-forward)

### BR-SEC1-NOINGEST
- `memo-agent-core`'s LLM-bound context contains **ONLY** the sanitized fields (`ApplicantProfile`
  with free-text already `SanitizedText.clean_text`), the `RuleResultReport`, and the read-only
  `recommendation`/`confidence`.
- The `SanitizationReport` / `original_span` (the preserved raw injection) is **AUDIT-ONLY** and
  **structurally never handed** to this unit (it flows a separate audit path to `audit-store`). The
  prompt-builder has **no reference** to it. **Tests assert no LLM-bound payload can reference
  `original_span`.** The neutralized injection **cannot re-enter** through the memo.

---

## 6. Production-call rules (temperature=0, advisory-only)

### BR-TEMP0
- **Every production memo LLM call uses `temperature=0`**, enforced **centrally** in the
  provider-abstraction (Gemini primary, P1), regardless of provider (FR-MEMO-2, FR-PROV). Structured
  **XML→Pydantic** output.

### BR-ADVISORY
- The system prompt enforces **advisory-only language**: the memo uses **"recommendation"** and
  **never** frames itself as a final **"decision"** (FR-MEMO-4). "decision" is reserved for the
  human's committed action (in `audit-store`).

---

## 7. Rule → requirement / invariant traceability

| Rule group | Satisfies |
|---|---|
| §1 BR-GROUND | FR-MEMO-3 (cite from the report), G6 (retrieval-miss guard), MCP Phase-2 boundary |
| §2 BR-CITE-VALIDATE / BR-CITE-FAILURE | FR-MEMO-3 (failure mode #1), US-MEMO-3, `services.md §6` Scenario 2 |
| §3 BR-CONBR2-TYPE/STATE/COMMIT | **CON-BR2**, US-MEMO-1, QA-5 |
| §4 BR-MISSINGINFO | reviewer **G3**, CON-DET-1 (deterministic, reproducible) |
| §5 BR-SEC1-NOINGEST | **SEC-1-FORENSIC** (intake), SEC / failure mode #4 |
| §6 BR-TEMP0 / BR-ADVISORY | FR-MEMO-2, FR-MEMO-4, US-MEMO-2/4, FR-PROV-1/3 |

**CON-DET-1 boundary restated**: the memo is **not** in the deterministic replay equality set
(rules-engine's output is); the memo's audit integrity is via `memo_hash` (`domain-entities.md §5`),
not re-draft. temperature=0 gives best-effort reproducible prose for evals only.

---

*End of business-rules.md. LangGraph sub-flow / replay boundary → `business-logic-model.md`;
schema → `domain-entities.md`.*
