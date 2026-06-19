# Application Design — Component Methods

**Stage**: DISCOVER → Application Design
**Date**: 2026-06-19
**Scope**: Method **signatures**, high-level purpose, and **I/O types** only.
**Detailed business rules, rule thresholds, validation logic, and field-by-field schema
are deferred to per-unit Functional Design (BUILD).** Types named here (e.g.
`ApplicantProfile`, `RuleResultReport`) are **interface contracts**; their internal fields
are defined in Functional Design.

> Signatures are illustrative Python-style interfaces for design clarity, not final code.

---

## Shared interface types (contracts; fields deferred to Functional Design)

| Type | Role |
|---|---|
| `ApplicantProfile` | Validated, typed applicant data produced by C1; the single input downstream steps trust. |
| `RuleResultReport` | Per-rule pass/fail + each fired rule's exact triggering value & comparison; **carries `recommendation`** and `rulebook_version`. |
| `Recommendation` | Enum — exactly `APPROVE` / `REFER` / `DECLINE-RECOMMEND`. |
| `OutlierResult` | Outlier score + flagged features + SHAP explanation (Phase 2). |
| `DecisionMemo` | Structured memo prose + cited rule IDs + confidence + missing-docs list. **No field that can alter `recommendation`.** |
| `CommittedDecision` | The human-committed outcome: links recommendation + `underwriter_id` + action + reason. |
| `AuditTuple` | `{rulebook_version, rule_results, timestamp, model_version, memo_hash}`. |

---

## C1 — Application Intake

| Method (signature) | Purpose | Input → Output |
|---|---|---|
| `parse(documents: list[Document]) -> ApplicantProfile` | Parse form + supporting docs into a validated profile, or reject at the gate. | `list[Document]` → `ApplicantProfile` (or rejection at the validation gate) |
| `sanitize(raw_text: str) -> SanitizedText` | Neutralize prompt-injection text before it can reach the memo agent (SEC-1). | `str` → `SanitizedText` |
| `validate_gate(extracted) -> ApplicantProfile` | Pydantic v2 gate; rejects malformed/unrecoverable input **before** any agent runs (SEC-2). | extracted draft → `ApplicantProfile` or `RejectedIntake` |

*Boundary/thin-file routing logic → Functional Design.*

## C2 — Deterministic Rulebook Engine

| Method (signature) | Purpose | Input → Output |
|---|---|---|
| `load_rulebook(version: str) -> Rulebook` | Load a specific immutable rulebook version. | `str` → `Rulebook` |
| `evaluate(profile: ApplicantProfile, rulebook_version: str) -> RuleResultReport` | Pure-Python evaluation; **produces the recommendation**; stamps `rulebook_version`. | `(ApplicantProfile, str)` → `RuleResultReport` |
| `recommend(rule_results) -> Recommendation` | Map evaluated results to the exact enum (internal to `evaluate`). | rule results → `Recommendation` |

*Rule thresholds, comparison operators, boundary handling → Functional Design.*
**CON-BR2**: the recommendation originates here; no LLM in this path.

## C3 — Outlier Detection (Phase 2)

| Method (signature) | Purpose | Input → Output |
|---|---|---|
| `build_features(profile: ApplicantProfile) -> FeatureVector` | Build the feature vector **excluding demographic identifiers** (CON-BR1). | `ApplicantProfile` → `FeatureVector` |
| `score(profile: ApplicantProfile, corpus_version: str) -> OutlierResult` | Seeded IsolationForest + z-scores against the corpus. | `(ApplicantProfile, str)` → `OutlierResult` |
| `explain(result: OutlierResult) -> ShapExplanation` | SHAP feature-importance for every flag (no unexplained flags). | `OutlierResult` → `ShapExplanation` |

*Feature selection details, seed/threshold values → Functional Design.*

## C4 — Decision-Memo Agent (LLM)

| Method (signature) | Purpose | Input → Output |
|---|---|---|
| `draft(profile, rule_report: RuleResultReport, outlier_result: OutlierResult | None) -> DecisionMemo` | Draft rule-cited, advisory-only memo prose **after** deterministic results exist. **Reads `rule_report.recommendation` read-only.** | `(ApplicantProfile, RuleResultReport, OutlierResult?)` → `DecisionMemo` |
| `route_borderline(rule_report, outlier_result) -> ThinkingMode` | Deterministic, provider-agnostic borderline trigger (rule-proximity OR outlier cutoff). | `(RuleResultReport, OutlierResult?)` → `ThinkingMode` |
| `validate_citations(memo_draft, rulebook) -> CitationValidationResult` | Assert every cited rule ID exists in the active YAML (hallucination guard). | `(DecisionMemo draft, Rulebook)` → `CitationValidationResult` |

*Prompt content, confidence-banding logic, XML schema fields → Functional Design.*
**CON-BR2**: `DecisionMemo` carries no recommendation-override field; QA-5 asserts the LLM
cannot change the recommendation. MCP access, secondary/showcase providers, borderline
routing are **Phase 2**.

## C5 — Underwriter UI

| View / action | Purpose | Interaction |
|---|---|---|
| `QueueView` | List applications awaiting review with their recommendation. | UI → `GET /applications` (RBAC-gated) |
| `MemoView` | Show recommendation + cited rules + confidence + missing docs (+ outlier flags, Phase 2). | UI → `GET /applications/{id}/memo` |
| `ApprovalGateAction` | Underwriter **Approve** at the human gate. | UI → `DecisionCommitService.commit(...)` |
| `OverrideForm` | **Override-with-mandatory-reason** when the underwriter disagrees. | UI → `DecisionCommitService.commit(..., reason)` |
| `HistoryView` | Full decision history; each entry links to its audit tuple. | UI → `GET /decisions` |

*All interactive elements carry `data-testid`; copy uses "recommendation". Component-level
layout/state logic → Functional Design.*

---

## Platform & Services — key method signatures (full design in `services.md`)

| Service.method (signature) | Purpose | Invariant |
|---|---|---|
| `ProviderAbstraction.complete(prompt, schema) -> StructuredOutput` | Provider-agnostic LLM call; **`temperature=0` enforced centrally**; per-provider structured-output adapters. | FR-PROV-1..5 |
| `MCPRulebookTools` / `MCPDecisionsTools` (**read-only**) | Expose rulebook + decisions DB to C4 as **read-only** grounding tools — **cannot write**. | FR-MEMO-5, SEC-4 |
| `DecisionCommitService.commit(recommendation_id, underwriter_id, action, reason=None) -> CommittedDecision` | The human-approval-gate backend boundary; **rejects any write lacking `underwriter_id` + `reason`**. | **CON-BR4** |
| `AuditStore.persist(audit_tuple: AuditTuple) -> None` | Persist the full audit tuple on every recommendation. | CON-AUDIT-1, SEC-5 |
| `ReplayService.replay(decision_id) -> RuleResultReport` | Re-evaluate a past decision against its **original** `rulebook_version`. | CON-AUDIT-1 |
| `AuthRBAC.authorize(user, action) -> bool` | Enforce underwriter (act) vs auditor (read-only); structured for later OIDC. | PER-4..6, SEC-4 |
| `CorpusGenerator.generate(seed, manifest) -> Corpus` | Seeded, version-stamped, skew-audited synthetic corpus. | CON-BR3 |

*Write path for committed decisions is `DecisionCommitService` only — never via an MCP
tool (the decisions-tools MCP server is strictly read-only).*

---

*End of component methods. Signatures are interface contracts; all business logic,
thresholds, and schema detail are defined in per-unit Functional Design (BUILD).*
