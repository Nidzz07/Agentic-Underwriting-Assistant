# Application Design — Services

**Stage**: DISCOVER → Application Design
**Date**: 2026-06-19
**Scope**: Service definitions + orchestration patterns + sequence diagrams.
**No business logic / thresholds / schema detail** (deferred to Functional Design).
**Decisions applied**: Q1=B (LangGraph scoped to C4 only; FastAPI owns
intake/rules/persistence; recommendation computed before the graph and injected as
immutable state), Q3=B (two read-only MCP servers), Q4=B (EPIC-6 modeled here as the
services layer), Q5=A+note (gate sequences included), Q6=A (gate outside the agent graph).

> **Vocabulary** (consistent with `user-journey.md`): the system emits a
> **recommendation**; the human makes a committed **decision** by **Approve** (agree) or
> **Override-with-reason** (disagree). The Q5 note's *Accept/Decline* maps to this:
> **Accept ↔ Approve**, **Decline ↔ Override-with-reason**. The **same uniform gate
> applies to ALL recommendations including REFER** — there is **no REFER-specific
> escalation branch** here (escalation = Phase 3 / OOS-2).

---

## 1. Orchestration model (Q1=B)

- **FastAPI** owns the **deterministic pipeline** (intake → rules → outlier) and all
  persistence. The **recommendation is computed here, before any graph runs**, and passed
  onward as **immutable state**.
- **LangGraph** orchestrates **only the C4 memo sub-flow**. No graph node can touch the
  recommendation — the cleanest structural guarantee of **CON-BR2**.
- The **human approval gate sits outside** the agent graph (Q6): the pipeline yields a
  **pending** recommendation + memo; the underwriter commits via `DecisionCommitService`.

> **CorpusGenerator is a build-time/setup step, not a per-request runtime step.**
> `CorpusGenerationService` runs **once** to produce the seeded, versioned, skew-audited
> synthetic corpus, frozen by a manifest (CON-BR3). At scoring time C3 consumes that frozen
> corpus **read-only** via `corpus_version`. This is why the corpus appears in the container
> diagram (`components.md`) but **not** in the per-request sequences below.

## 2. Service definitions (services layer; five core components stay primary)

| Service | Responsibility | Key invariant |
|---|---|---|
| `IntakeService` | Parse + validate documents to `ApplicantProfile`; sanitize injection; gate malformed input. | SEC-1/2, FR-INTAKE-* |
| `RuleEvaluationService` (wraps C2) | Pure-Python evaluation; **produces the recommendation**; stamps `rulebook_version`. | CON-BR2, CON-DET-1 |
| `OutlierService` (C3, Phase 2) | Seeded scoring + SHAP; demographic-free feature vector. | CON-BR1 |
| `MemoOrchestrationService` (C4 / LangGraph) | Drives the memo sub-flow; consumes the read-only recommendation; validates citations. | CON-BR2, FR-MEMO-* |
| `ProviderAbstractionService` | Provider-agnostic LLM calls; central `temperature=0`; per-provider adapters. | FR-PROV-1..5 |
| `MCPToolService` — **`rulebook-tools`** + **`decisions-tools`** (two servers, **read-only**) | Read-only grounding for C4; **neither can write**. | FR-MEMO-5, SEC-4 |
| `DecisionCommitService` | Human-gate backend boundary; **rejects writes lacking `underwriter_id` + `reason`**. | **CON-BR4** |
| `AuditService` / `ReplayService` | Persist audit tuple; replay any decision against its **original** rulebook version. | CON-AUDIT-1, SEC-5 |
| `AuthRBACService` | Underwriter (act) vs auditor (read-only); OIDC-ready. | PER-4..6, SEC-4 |
| `CorpusGenerationService` | Seeded, versioned, skew-audited corpus. | CON-BR3 |
| `ObservabilityService` (Phase 2) | Langfuse traces (100% of steps) + Prometheus/Grafana. | NFR-OBS-1/2 |
| `AdminCLI` | Out-of-band rulebook-version/user/config management (no admin UI). | PER-3/6 |
| `SecretsService` | Provider/service keys via env/secrets; no hardcoding. | SEC-3 |

---

## 3. Sequence — Intake → commit (happy path)

Mermaid validated before write (alphanumeric IDs; no parentheses in participant names;
`alt/else/end` balanced; text alternative below).

```mermaid
sequenceDiagram
    actor UW as Underwriter
    participant UI as Underwriter UI C5
    participant API as FastAPI
    participant INT as Intake C1
    participant RUL as Rules Engine C2
    participant OUT as Outlier C3
    participant MEMO as Memo Agent C4 LangGraph
    participant PROV as ProviderAbstraction
    participant DCS as DecisionCommitService
    participant AUD as AuditStore

    UW->>UI: open case
    UI->>API: submit application + documents
    API->>INT: parse documents
    INT-->>API: ApplicantProfile validated
    API->>RUL: evaluate profile + rulebook_version
    RUL-->>API: RuleResultReport + recommendation read-only
    API->>OUT: score profile + corpus_version
    OUT-->>API: OutlierResult + SHAP
    API->>MEMO: draft profile + rule_report + outlier_result
    MEMO->>PROV: complete prompt + schema at temperature 0
    PROV-->>MEMO: structured memo prose
    MEMO-->>API: DecisionMemo cites rules, cannot alter recommendation
    API-->>UI: pending recommendation + memo
    UW->>UI: Approve or Override-with-reason
    UI->>DCS: commit recommendation_id + underwriter_id + action + reason
    DCS->>AUD: persist audit tuple
    AUD-->>DCS: ok
    DCS-->>UI: CommittedDecision
```

**Text alternative**: Underwriter opens a case → FastAPI runs C1 parse → C2 evaluate
(**recommendation produced here, read-only**) → C3 score → C4 memo via ProviderAbstraction
at `temperature=0` (prose only) → UI shows the **pending** recommendation + memo →
underwriter **Approves or Overrides-with-reason** → `DecisionCommitService` commits (only
with `underwriter_id` + `reason`) → `AuditStore` persists the audit tuple → committed.

> **Audit tuple vs commit payload (two distinct shapes).** The **commit payload** the UI
> sends to `DecisionCommitService` is the 4 fields `{recommendation_id, underwriter_id,
> action, reason}`. The **persisted audit tuple** is the CON-AUDIT-1 **5-tuple**
> `{rulebook_version, rule_results, timestamp, model_version, memo_hash}` — the replayable
> record of the decision, distinct from the commit payload. (Field-level schema is deferred
> to Functional Design; this note only distinguishes the two record shapes.)

---

## 4. Sequence — Decision replay (auditor, read-only)

```mermaid
sequenceDiagram
    actor AUDR as Auditor
    participant UI as Underwriter UI C5
    participant API as FastAPI
    participant AUD as AuditStore
    participant REP as ReplayService
    participant RUL as Rules Engine C2

    AUDR->>UI: open a past decision read only
    UI->>API: get decision by id
    API->>AUD: get decision_id
    AUD-->>API: AuditRecord with original rulebook_version
    API->>REP: replay decision_id
    REP->>RUL: evaluate profile + original rulebook_version
    RUL-->>REP: RuleResultReport
    REP-->>API: replayed result matches recorded rule_results
    API-->>UI: read-only audit tuple + replay result
```

**Text alternative**: Auditor opens a past decision (read-only) → FastAPI fetches the
`AuditRecord` from `AuditStore` → `ReplayService` re-evaluates the profile against the
**original** `rulebook_version` (not the latest) → the replayed `RuleResultReport` matches
the recorded `rule_results` → UI shows the read-only audit tuple + replay result.
**CON-AUDIT-1**. The auditor has **no write capability** (SEC-4).

---

## 5. Sequence — Uniform human approval gate (ALL recommendations incl. REFER)

> **No REFER escalation branch.** REFER is just one recommendation value entering the
> same gate. Escalation routing is Phase 3 / OOS-2 (documented, not built/drawn).

```mermaid
sequenceDiagram
    actor UW as Underwriter
    participant UI as Underwriter UI C5
    participant DCS as DecisionCommitService
    participant AUD as AuditStore

    Note over UI: recommendation in APPROVE, REFER, or DECLINE-RECOMMEND
    UW->>UI: review pending recommendation + memo
    alt Approve - agree with recommendation
        UW->>UI: Approve
        UI->>DCS: commit underwriter_id + approval
    else Override-with-reason - disagree
        UW->>UI: Override and submit mandatory reason
        UI->>DCS: commit underwriter_id + reason
    end
    DCS->>DCS: reject if underwriter_id or reason missing
    DCS->>AUD: persist audit tuple
    AUD-->>DCS: ok
    DCS-->>UI: CommittedDecision
    Note over UW,DCS: same uniform gate for every recommendation incl REFER - escalation is Phase 3
```

**Text alternative**: The pending recommendation may be `APPROVE`, `REFER`, or
`DECLINE-RECOMMEND`. The underwriter either **Approves** (agree → commit with
`underwriter_id` + approval) or **Overrides-with-reason** (disagree → commit with
`underwriter_id` + mandatory reason). `DecisionCommitService` **rejects any write missing
`underwriter_id` or `reason`** (CON-BR4), then `AuditStore` persists the audit tuple. The
**same gate handles every recommendation including REFER**; there is **no REFER-specific
escalation path** in this engagement (Phase 3 / OOS-2).

---

*End of services. Dependency matrix + data-flow in `component-dependency.md`.*
