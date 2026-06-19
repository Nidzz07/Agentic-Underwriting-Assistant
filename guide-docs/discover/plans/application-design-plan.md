# Application Design Plan — Agentic Underwriting Assistant

**Phase / Stage**: DISCOVER → Application Design (plan-then-generate; this is the **plan**)
**Project Type**: Greenfield
**Date**: 2026-06-19
**Depth**: Comprehensive (per execution-plan.md §3; approved at the Workflow Planning gate)
**Status**: Awaiting your answers to the questions in **Section C** below; do **not** proceed to artifact generation until all `[Answer]:` tags are filled and ambiguity-checked.

This document is the Application Design **plan**. Per the stage protocol
(`discover/application-design.md`), the plan is approved/answered **before** the five
design artifacts are generated. The approach in Section A was approved in chat on
2026-06-19; this file records it and collects the planning answers via `[Answer]:`
tags (same questions-in-a-file convention used at User Stories).

> **Scope reminder**: Application Design is **high-level component identification +
> service-layer design** — interfaces and method **signatures**, not detailed business
> logic. Rule thresholds, schema field-by-field detail, and business-rule logic are
> **deferred to per-unit Functional Design** (BUILD).

---

## A. Approved Approach (recorded)

### A.1 Component set to be designed

**Five core components** (PROJECT-BRIEF §3 / FR-SCOPE-1), plus a **Platform & Services
layer** carrying the EPIC-6 cross-cutting concerns (final modeling of that layer is
**Q4** below):

| # | Component | High-level interface (signatures detailed in `component-methods.md`) | Key invariant role |
|---|---|---|---|
| C1 | Application Intake | `IntakeService.parse(documents) → ApplicantProfile`; Pydantic v2 validation gate + `document-sanitizer` **before** any agent runs | SEC-1/2; FR-INTAKE-1..3 |
| C2 | Deterministic Rulebook Engine | `RulesEngine.evaluate(profile, rulebook_version) → RuleResultReport` (carries `recommendation`); **pure Python, zero LLM** | **Produces the recommendation** (CON-BR2, CON-DET-1); FR-RULES-1..6 |
| C3 | Outlier Detection | `OutlierService.score(profile, corpus) → OutlierResult` (seeded IsolationForest + z-scores + SHAP); feature-builder **excludes demographic identifiers** | CON-BR1, FR-OUT-1..3 (Phase 2) |
| C4 | Decision-Memo Agent (LLM) | LangGraph; `MemoAgent.draft(profile, rule_report, outlier_result) → DecisionMemo`; receives the recommendation as **immutable input**, drafts prose + cites validated rule IDs only; temperature=0 | CON-BR2, FR-MEMO-1..7 |
| C5 | Underwriter UI | queue / memo-view / approval-gate / override-form / history; advisory-only copy + `data-testid` | FR-UI-1..5 |
| — | Platform & Services | `ProviderAbstraction` (Gemini/Claude/Ollama; central temperature=0; per-provider structured-output adapters); `MCPToolLayer` (read-only rulebook + decisions tools); `DecisionCommitService` (backend human-approval-gate boundary); `AuditStore` (audit tuple + replay); `Auth/RBAC` (UI + backend facets); `CorpusGenerator` (seeded/versioned/skew-audited); persistence (PostgreSQL); quality/eval suites; observability; admin-CLI; secrets | CON-BR3/BR4, CON-AUDIT-1, PER-4..6, SEC-3/4/5 |

### A.2 How the binding invariants are honored in the design

- **CON-BR2 (LLM out of the decision path)** — the recommendation is computed by the
  C2 deterministic engine and passed into C4 as a **read-only field**; the memo schema
  has **no field that can alter it**; the design names the test seam (QA-5: "LLM cannot
  change a recommendation").
- **CON-BR1 (bias measured on the decision)** — the outlier `feature-builder` interface
  excludes name/gender/city/pincode; occupation and income influence the outcome **only**
  through their sanctioned rule (occupation-risk / affordability).
- **CON-BR3 (corpus seeded + versioned + skew-audited)** — `CorpusGenerator` produces a
  manifest-stamped, skew-audited corpus before use.
- **CON-BR4 ("advisory only" enforced in the system)** — the human approval gate is a
  **backend `DecisionCommitService` boundary**, not UI copy; the write path **rejects any
  record lacking `underwriter_id` + `reason`**.
- **CON-AUDIT-1 (audit tuple + replay)** — `AuditStore` persists
  `{rulebook_version, rule_results, timestamp, model_version, memo_hash}`; replay reads
  the **original** rulebook version.
- **Deterministic / LLM dividing line** — everything that determines the recommendation
  (intake validation → rules → outlier scoring feeding the *borderline trigger* only) is
  pure Python; the LLM (C4) is downstream and **prose-only**. This line is drawn
  explicitly in `component-dependency.md`.

### A.3 Carried-in items (honored; not re-resolved here)

1. **Per-unit "lighter" depth = revisitable recommendation, not a locked floor.** This
   bites at the BUILD per-unit design stages, not at Application Design (which runs
   comprehensive). The invariant-bearing UI components **`ui-approval-gate` and
   `ui-override-form` remain comprehensive** (FR-UI-2 / CON-BR4 / FR-UI-4).
2. **`ui-auth-rbac` (C5/EPIC-5) vs `auth-rbac` (EPIC-6) overlap.** Modeled here as **one
   Auth/RBAC capability with a UI-enforcement facet and a backend-enforcement facet**; the
   **one-unit-vs-two boundary call is deferred to Units Generation** and flagged at every
   RBAC touchpoint. Not forced in this stage.

---

## B. Methodology & Mandatory Artifact Checklist

Execution sequence for this stage (plan-then-generate):

- [x] Analyze context (requirements.md + stories.md + personas.md + user-journey.md + execution-plan.md)
- [x] Record approved approach (Section A)
- [x] Create this plan with embedded `[Answer]:` questions (Section C)
- [x] **Collect answers** — you fill every `[Answer]:` tag in Section C *(done 2026-06-19; Q1=B, Q2=N/A, Q3=B, Q4=B, Q5=A+note, Q6=A)*
- [x] **Ambiguity check** — I review answers for vague/contradictory/combined responses; add follow-up `[Answer]:` tags if needed; do not proceed until resolved *(done 2026-06-19 — all six clean; no follow-ups required; two interpretation confirmations recorded: decisions-tools MCP server is read-only with the write path = `DecisionCommitService` not MCP; the gate sequence diagrams model the uniform Accept/Override-with-reason gate for ALL recommendations incl. REFER, with NO REFER-specific escalation branch — escalation = Phase 3/OOS-2)*
- [x] **Generate the five mandatory artifacts** *(done 2026-06-19, after go-ahead)*:

  - [x] `application-design/components.md` — component name, purpose, responsibilities, interfaces **+ C4-style component (container) Mermaid diagram**
  - [x] `application-design/component-methods.md` — method **signatures**, purpose, I/O types per component *(business rules deferred to Functional Design)*
  - [x] `application-design/services.md` — service definitions, responsibilities, orchestration **+ sequence Mermaid diagram(s)** (intake→commit happy path; decision replay path; uniform gate path — Accept/Override-with-reason over all recommendations incl. REFER, no escalation branch)
  - [x] `application-design/component-dependency.md` — dependency matrix, communication patterns, **data-flow Mermaid diagram** (incl. the explicit deterministic/LLM line + read-only MCP boundary)
  - [x] `application-design/application-design.md` — **consolidation** of the four artifacts above

- [x] Validate every diagram against the Mermaid rules **before** writing each file; include a **text alternative** under each diagram *(7-rule pre-write validation; semicolons removed from two sequence-message strings as a safety pass; all diagrams passed — no text fallback needed)*
- [x] Present the Step-12 completion message (**Request Changes / Approve & Continue**; "Add Units Generation" omitted — Units Generation is EXECUTE, not skipped) → next stage **Units Generation**

**Mermaid validation rules to be applied at generation time** (no Mermaid is written in
this plan doc): alphanumeric/underscore node IDs; all special-character/parenthesis/period
labels double-quoted; parentheses only inside quoted labels; subgraphs closed; avoid the
reserved word `end` as a node id; balanced brackets; mandatory text alternative; fall back
to text if validation fails and say so.

---

## C. Planning Questions — please fill every `[Answer]:` tag

> Format: choose one option (A/B/...) per question; add notes after the choice if useful.
> If an answer is vague, combined, or contradictory, I will add a follow-up `[Answer]:`
> tag before generating artifacts.

### Q1 — Orchestration boundary (where does LangGraph sit?)

How much of the pipeline does LangGraph orchestrate?

- **A.** LangGraph orchestrates the **whole pipeline** (intake → rules → outlier → memo).
- **B. (RECOMMENDED)** LangGraph is **scoped to the C4 memo sub-flow only**; **FastAPI owns
  intake / rules / persistence**, and the deterministic pipeline lives entirely **outside**
  the LLM-orchestration framework.

**Reasoning for the recommendation (B):** CON-BR2 (LLM out of the decision path) stays
cleanest when the deterministic pipeline is not even inside the LLM-orchestration
framework — there is no graph node that *could* touch the recommendation. The brief's
wording, "memo agent orchestrated via LangGraph," points to LangGraph being the **memo
agent's** orchestrator, not the whole system's. The choice remains yours.

[Answer]: B — LangGraph scoped to the C4 memo sub-flow only; FastAPI owns intake/rules/persistence. The deterministic pipeline lives entirely outside the LLM-orchestration framework so no graph node can touch the recommendation — the cleanest structural guarantee of CON-BR2. Confirmed with project direction.

### Q2 — Recommendation placement in the graph *(depends on Q1)*

Where is the deterministic recommendation computed relative to the LangGraph graph?

- **A.** Computed **before** the graph (in FastAPI/rules) and **injected as immutable
  state** into the memo sub-flow.
- **B.** Computed **inside a hard-locked graph node** within a whole-pipeline graph.

**Dependency note:** if **Q1 = B (memo-only LangGraph)**, then the recommendation is
**necessarily computed before the graph and injected as immutable state** — i.e. **Q2 = A
is implied**, and this question is only genuinely "live" if **Q1 = A (whole-pipeline
orchestration)**. Please answer Q2 only if you pick Q1 = A; otherwise mark it "N/A — implied
by Q1 = B."

[Answer]: N/A — implied by Q1 = B. With memo-only LangGraph, the recommendation is necessarily computed before the graph (in FastAPI/rules) and injected into the memo sub-flow as immutable state.

### Q3 — MCP server granularity

How are the MCP tools exposed to the memo agent (read-only grounding only; tools cannot
mutate the recommendation)?

- **A.** **One** MCP server exposing both rulebook tools and decisions-DB tools.
- **B.** **Two** separate MCP servers (`rulebook-tools`, `decisions-tools`).

[Answer]: B — Two separate MCP servers (rulebook-tools, decisions-tools). The two tool sets have different sensitivity/access profiles: rulebook tools are read-only reference data; decisions-DB tools touch the audit/decision store (ties to SEC-4 read-only-audit and SEC-5 audit-logging, and underpins replay). Separate servers let each carry its own read-only scoping, make the read-only boundary provable per-server, and keep blast radius contained. Both remain strictly read-only grounding — neither can mutate the recommendation.

### Q4 — How to model the Platform & Services (EPIC-6) concerns

- **A.** As **first-class components** in `components.md` (auth, audit-store, observability,
  corpus, admin-CLI each elevated to a component).
- **B. (RECOMMENDED)** As a **services layer** in `services.md`, keeping the **five core
  components** primary in `components.md`.

**Reasoning for the recommendation (B):** the brief frames the system as five components;
EPIC-6 items are cross-cutting capabilities that read most naturally as a service/supporting
layer, keeping `components.md` aligned to the brief while still fully designing them in
`services.md` and the dependency matrix.

[Answer]: B — Model the EPIC-6 concerns as a services layer in services.md, keeping the five core components primary in components.md. Matches the brief's five-component framing and how stories.md already treats EPIC-6 as cross-cutting; platform concerns are still fully designed in services.md and the dependency matrix.

### Q5 — Diagram set per artifact (confirm or adjust)

Proposed: **C4-style component (container) diagram** in `components.md`; **sequence
diagram(s)** in `services.md` (intake→commit happy path; decision replay path);
**data-flow diagram** in `component-dependency.md` (with the explicit deterministic/LLM
line).

- **A.** Confirm this diagram set.
- **B.** Adjust — specify which diagram to add/drop/change in your note.

[Answer]: A — Confirm the diagram set (C4 component diagram in components.md; sequence diagrams in services.md; data-flow in component-dependency.md with the explicit deterministic/LLM line). Note: in services.md, include sequence diagrams for the gate's REFER/Accept/Decline and override-with-reason paths (not just the happy path), since that's where CON-BR4 enforcement and the uniform Accept/Decline-for-all-recommendations behavior live.

### Q6 — Human approval gate / agent boundary (confirm)

Proposed: the human approval gate sits **outside** the agent graph — the pipeline yields a
**pending** recommendation + memo, and the underwriter commits via `DecisionCommitService`
(which enforces `underwriter_id` + `reason`, CON-BR4).

- **A.** Confirm this boundary.
- **B.** I see it differently — details in your note.

[Answer]: A — Confirm. The human approval gate sits outside the agent graph: the pipeline yields a pending recommendation + memo, and the underwriter commits via DecisionCommitService, which rejects any write lacking underwriter_id + reason (CON-BR4). The LLM agent never participates in committing a decision — advisory output only.

---

*End of Application Design plan. Awaiting your answers to Section C. Once every `[Answer]:`
tag is filled, I will ambiguity-check them and only then generate the five design
artifacts — no design artifact is generated before that.*
