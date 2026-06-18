# User Stories — Agentic Underwriting Assistant

**Stage**: DISCOVER → User Stories (Part 2 — Generation)
**Date**: 2026-06-18
**Breakdown approach**: Q4 = **E (with refinements)** — component epics aligned
to the 5 components, UI told as a user journey, backend epics as capability
stories from the benefiting persona, plus one cross-cutting epic for
persona-benefiting NFR/quality/access stories (Q2 = B).
**Granularity**: Q3 = B (feature-level, 3–7 acceptance criteria each).
**AC format**: Q5 = A default (Gherkin), bullets for analytical/report stories.
**Traceability**: Q7 = C (per-story `Traces:` line **and** the matrix in §9).

---

## 1. How to read this backlog

- **Every story carries a mandatory `Phase:` tag (Phase 1 or Phase 2).** There
  are **no Phase 3 stories** — the former OOS-1..6 are documented-for-reference
  only in `requirements.md §2.2 / §12` (future release).
- **"What's in Phase 1" is a first-class, sliceable view** — see §8.
- Each epic lists its **anticipated build units + Definition of Done (DoD)**,
  closing the chain **requirement → epic → story → unit → test**. (Unit names are
  provisional; confirmed at the later Units Generation stage.)
- **Blocking gates keep their exact strength**: bias-swap delta = **0 (any delta
  blocking)**, decision reproducibility = **100%**, rule coverage = **100%**,
  code coverage = **≥ 90% (binding)**. These are never softened.
- **Stakeholder voicing**: stories voiced *"As a member of the implementing team"*
  (e.g. US-PLAT-6/7/9/10/11/12) refer to a build-time, non-UI engineering
  stakeholder — **not** a UI persona; auditor-consumable evidence artifacts are
  auditor-voiced.

### Phasing rationale

- **Phase 1 — Core deterministic advisory slice**: intake → versioned rules
  engine → memo (rule-cited, advisory) → underwriter UI with the human approval
  gate and override-with-reason → RBAC → the deterministic quality gates
  (reproducibility, bias-swap, rule coverage, code coverage) → synthetic corpus →
  audit tuple + replay. This is a working, auditable, advisory-only vertical.
- **Phase 2 — ML explainability, observability & validation deploy**: outlier
  detection + SHAP → borderline routing to extended thinking → secondary-provider
  fallback + Ollama showcase → MCP tool exposure → auditor portal reports →
  observability stack → LLM-as-judge → Render/Vercel **validation** deploy.
  *(Production deploy = Phase 3 / future release.)*

---

## 2. EPIC-1 — Application Intake Agent  *(backend; capability stories)*

**Component**: C1 Application Intake Agent.
**Anticipated build units**: `intake-parser` (pdfplumber), `applicant-profile-schema`
(Pydantic v2), `intake-validation-gate`, `document-sanitizer`.
**Epic DoD**: a malformed-or-clean document set always resolves to either a
validated `ApplicantProfile` or a rejection at the Pydantic gate **before** any
agent runs; thin-file/missing-doc cases stay processable; injection-bearing text
is neutralised. All units covered by tests (contributes to ≥90% coverage).

### US-INTAKE-1 — Parse application + documents into a validated profile
**Phase: 1**
*As an* underwriter, *I want* the system to parse the application form and
supporting documents (salary slips, bank statements, medical questionnaire) into
one validated structured profile, *so that* every downstream step works from a
single typed, trustworthy `ApplicantProfile`.
**Traces:** FR-INTAKE-1, FR-INTAKE-2, DATA-4

```gherkin
Given a complete application package (form + salary slip + bank statement + medical questionnaire)
When the Application Intake Agent processes it
Then it produces an ApplicantProfile that passes Pydantic v2 validation
And every extracted field is typed and traceable to its source document
And no real PII is introduced (synthetic/mock data only)
```

### US-INTAKE-2 — Reject malformed input at the validation gate before agent entry
**Phase: 1**
*As an* underwriter, *I want* broken or incomplete-beyond-recovery input rejected
at a validation gate before any agent runs, *so that* no agent ever operates on
malformed data.
**Traces:** FR-INTAKE-2, SEC-2 (failure mode #5)

```gherkin
Given a broken PDF or a package missing a required field
When intake validation runs
Then the package is rejected at the Pydantic validation gate
And the rejection occurs before any agent or LLM step executes
And the rejection reason is logged to the audit trail
```

### US-INTAKE-3 — Keep thin-file / single-missing-document cases processable
**Phase: 1**
*As an* underwriter, *I want* thin-file applicants and single-missing-document
cases to remain processable and route toward REFER, *so that* incomplete-but-valid
cases reach my judgement instead of failing silently.
**Traces:** FR-INTAKE-3 (Skill, Brief §4)

```gherkin
Given an application missing exactly one non-critical document
When intake and rule evaluation complete
Then the case is processed (not hard-failed)
And the resulting recommendation is REFER
And the missing document is listed for the underwriter
```

### US-INTAKE-4 — Sanitize / sandbox uploaded document text against prompt injection
**Phase: 1**
*As an* underwriter, *I want* text extracted from uploaded documents sanitized and
parsed in a sandbox, *so that* malicious instructions hidden in a document cannot
steer the memo agent.
**Traces:** SEC-1 (failure mode #4)

```gherkin
Given an uploaded document containing embedded instruction-like text (prompt injection)
When intake extracts and prepares the text
Then the text is sanitized and parsed in a sandboxed context
And the injected instructions do not reach the memo agent as commands
And the event is recorded for audit
```

---

## 3. EPIC-2 — Deterministic Rulebook Engine  *(backend; capability stories)*

**Component**: C2 Deterministic Rulebook Engine.
**Anticipated build units**: `rulebook-yaml` (versioned), `rules-engine` (pure
Python), `rule-result-model`, `rulebook-version-store`, `decision-replay`.
**Epic DoD**: 25–40 rules evaluated by pure Python with **zero LLM** in the path;
every fired rule reports its exact triggering value and comparison; output stamped
with `rulebook_version`; published versions immutable and replayable;
recommendation enum exact.

### US-RULES-1 — Codify 25–40 rules in versioned YAML evaluated by pure Python
**Phase: 1**
*As an* underwriter, *I want* the rulebook codified in versioned YAML and evaluated
by pure Python with no LLM, *so that* the recommendation is deterministic and
defensible.
**Traces:** FR-RULES-1, CON-BR2, CON-DET-1

```gherkin
Given a versioned YAML rulebook of 25 to 40 underwriting rules
When the rules engine evaluates an ApplicantProfile
Then evaluation uses pure Python with no LLM call in the path
And the same profile against the same rulebook version yields identical results every run
And the output is stamped with the active rulebook_version
```

### US-RULES-2 — Report exact triggering value and comparison, with correct boundaries
**Phase: 1**
*As an* underwriter, *I want* each fired rule to report the exact applicant value
that triggered it and the comparison applied, *so that* I can see precisely why a
rule passed or failed.
**Traces:** FR-RULES-3, FR-RULES-4, NFR-EXPLAIN-1

```gherkin
Given an applicant with age = 65, BMI = 25, and DTI = 40%
When the rules engine evaluates the boundary rules
Then each fired rule reports the exact applicant value and the comparison used (<= vs <)
And each boundary value (age 18/65, BMI 25/30, DTI 40%) lands on the intended side
And the per-rule pass/fail report carries the rulebook_version
```

### US-RULES-3 — Produce the exact recommendation enum from the engine only
**Phase: 1**
*As an* underwriter, *I want* the recommendation to be exactly APPROVE / REFER /
DECLINE-RECOMMEND and produced solely by the deterministic engine, *so that* no
LLM can influence the outcome.
**Traces:** FR-RULES-5, CON-BR2, QA-5

```gherkin
Given a fully evaluated ApplicantProfile
When the engine emits a recommendation
Then the value is exactly one of APPROVE, REFER, or DECLINE-RECOMMEND
And a decline always carries the mandatory -RECOMMEND suffix (never a bare "DECLINE")
And the recommendation is produced entirely by the deterministic Python engine
```

### US-RULES-4 — Version the rulebook immutably and replay any past decision
**Phase: 1**
*As a* compliance/audit reviewer, *I want* published rule versions to be immutable
and every past decision replayable against its original version, *so that* I can
reproduce any historical outcome exactly.
**Traces:** FR-RULES-6, CON-AUDIT-1, NFR-VERSION-1

```gherkin
Given a decision recorded under rulebook_version vN
When I replay that decision by its ID
Then it is re-evaluated against vN (not the latest version)
And the replayed result matches the originally recorded rule_results
And no published rule version was mutated in place (changes add a new version)
```

### US-RULES-5 — Treat occupation as a legitimate input that is also proxy-guarded
**Phase: 1**
*As an* underwriter, *I want* occupation to influence the outcome **only** through
its documented occupation-risk rule (mirroring how income works through the
affordability rule), *so that* a legitimate risk factor never becomes a back-door
demographic proxy.
**Traces:** FR-RULES-2, CON-BR1

```gherkin
Given two applicants with identical financials and medicals
When their occupation differs only in a way unrelated to the occupation-risk rule
Then the recommendation is invariant
And occupation changes the outcome only when it changes the documented occupation-risk rule result
And the same carve-out holds for income (only via the affordability rule)
```

---

## 4. EPIC-3 — Outlier Detection Agent  *(backend; capability stories)*

**Component**: C3 Outlier Detection Agent.
**Anticipated build units**: `outlier-model` (IsolationForest + z-scores, seeded),
`shap-explainer`, `outlier-feature-builder`.
**Epic DoD**: every applicant scored against the seeded synthetic corpus; every
flag carries a SHAP explanation; demographic identifiers never enter the feature
vector; results reproducible under a fixed seed.

### US-OUT-1 — Score applicants against the corpus with seeded, reproducible ML
**Phase: 2**
*As an* underwriter, *I want* each applicant compared against the synthetic corpus
using IsolationForest + z-scores with seeded randomness, *so that* statistical
anomalies surface reproducibly.
**Traces:** FR-OUT-1, CON-DET-1, CON-BR3

```gherkin
Given the seeded synthetic corpus and an applicant profile
When the outlier model scores the applicant
Then it returns an outlier score and the flagged features
And running the scoring twice with the same seed yields identical results
And no unseeded randomness or wall-clock-dependent logic is used
```

### US-OUT-2 — Explain every outlier flag with SHAP feature importance
**Phase: 2**
*As an* underwriter, *I want* every outlier flag accompanied by a SHAP
feature-importance explanation, *so that* no flag is unexplained.
**Traces:** FR-OUT-2, NFR-EXPLAIN-1

```gherkin
Given an applicant the outlier model has flagged
When I view the flag
Then it includes a SHAP explanation naming the contributing features
And there are zero flags without an explanation
```

### US-OUT-3 — Exclude demographic identifiers from the feature vector
**Phase: 2**
*As a* compliance/audit reviewer, *I want* demographic identifiers excluded from
the outlier feature vector, *so that* anomaly detection is bias-free by design.
**Traces:** FR-OUT-3, CON-BR1, DATA-4

```gherkin
Given the outlier feature builder
When it constructs the feature vector for any applicant
Then name, gender, city, and other demographic identifiers are absent from the vector
And swapping those fields across identical financials does not change the outlier result
```

---

## 5. EPIC-4 — Decision-Memo Agent (LLM)  *(backend; capability stories)*

**Component**: C4 Decision-Memo Agent.
**Anticipated build units**: `langgraph-orchestrator`, `provider-abstraction`
(Gemini primary / Claude secondary / Ollama showcase), `memo-schema`
(XML→Pydantic), `rule-citation-validator`, `borderline-router`, `mcp-servers`.
**Epic DoD**: memo drafted only after deterministic results exist and never alters
the recommendation; `temperature=0` on all production calls regardless of provider;
cited rule IDs validated against the YAML; advisory-only language enforced.

### US-MEMO-1 — Draft the memo without ever altering the recommendation
**Phase: 1**
*As an* underwriter, *I want* the memo agent (orchestrated by LangGraph) to draft
prose only after deterministic results exist and never change the recommendation,
*so that* the LLM stays out of the decision path.
**Traces:** FR-MEMO-1, CON-BR2, QA-5

```gherkin
Given deterministic rule results and a recommendation for an applicant
When the memo agent drafts the memo
Then it runs only after the deterministic results exist
And the recommendation in the memo equals the engine's recommendation
And a test asserts the LLM cannot change the recommendation
```

### US-MEMO-2 — Enforce temperature=0 and structured output behind a provider abstraction
**Phase: 1**
*As an* underwriter, *I want* all production memo calls to run at temperature=0 with
structured XML→Pydantic output behind a runtime-selectable provider abstraction
(Gemini primary), *so that* memos are reproducible and provider-independent.
**Traces:** FR-MEMO-2, FR-PROV-1, FR-PROV-2, FR-PROV-3

```gherkin
Given the memo agent configured with the primary provider (Gemini)
When it issues a production LLM call
Then temperature=0 is enforced regardless of which provider is selected
And the response is structured XML validated into a Pydantic model
And the provider can be switched at runtime via config without code changes
```

### US-MEMO-3 — Cite every triggered rule and validate cited IDs against the YAML
**Phase: 1**
*As an* underwriter, *I want* the memo to cite every triggered rule by ID with a
confidence level and the missing-documents list (and outlier flags once available),
with cited IDs validated against the rulebook, *so that* the memo can never invent
a rule.
**Traces:** FR-MEMO-3 (failure mode #1), NFR-EXPLAIN-1

```gherkin
Given a memo drafted for an evaluated applicant
When the memo is validated
Then it cites every triggered rule by ID with a confidence level (Low/Medium/High)
And it lists any missing documents
And every cited rule ID exists in the active YAML rulebook (hallucination guard)
And outlier flags are cited once the outlier model is available (Phase 2)
```

### US-MEMO-4 — Enforce advisory-only language in the system prompt
**Phase: 1**
*As an* underwriter, *I want* the memo to always use advisory language
("recommendation", never "decision"), *so that* the system never presents itself as
the final decision-maker.
**Traces:** FR-MEMO-4, CON-BR4 (language), BR4

```gherkin
Given the memo agent's system prompt
When any memo is generated
Then the memo uses "recommendation" and never frames itself as a final "decision"
And the word "decision" is reserved for the human underwriter's committed action
```

### US-MEMO-5 — Expose rulebook and decisions DB via MCP tools with provider adapters
**Phase: 2**
*As an* underwriter, *I want* the agent to access the rulebook engine and decisions
DB through MCP servers as tools, *so that* memo drafting is grounded in live tools
rather than memorised content.
**Traces:** FR-MEMO-5

```gherkin
Given MCP servers exposing the rulebook engine and the decisions DB as tools
When the memo agent needs rule or decision data
Then it retrieves it through the MCP tools
And provider-specific adapters handle structured-output / function-calling differences (not assumed Claude-shaped)
```

### US-MEMO-6 — Route borderline cases to extended thinking deterministically
**Phase: 2**
*As an* underwriter, *I want* borderline cases routed to the active provider's
extended-thinking/reasoning capability, *so that* the hardest cases get the most
careful memo.
**Traces:** FR-MEMO-6, FR-MEMO-7, FR-PROV-5

```gherkin
Given an applicant within the configurable rule-proximity margin OR with an outlier flag above cutoff
When the memo agent processes the case
Then it routes to the active provider's extended-thinking/reasoning capability where supported
And the routing trigger is deterministic and provider-agnostic
And until the outlier model lands, routing runs on rule-proximity alone
```

### US-MEMO-7 — Provide a tested secondary provider and a wired-only showcase provider
**Phase: 2**
*As an* underwriter, *I want* a tested Claude secondary fallback and a wired-only
Ollama showcase, *so that* the system proves vendor independence without claiming
untested behaviour.
**Traces:** FR-PROV-2, FR-PROV-GATE-2

```gherkin
Given the provider abstraction with Gemini primary, Claude secondary, Ollama showcase
When the primary is unavailable and the secondary is selected
Then Claude (secondary) serves memos and is held to the memo-quality gates
And Ollama is wired but exempt from the acceptance-criteria memo-quality gates (showcase-only)
And temperature=0 holds for all three
```

---

## 6. EPIC-5 — Underwriter UI  *(journey-style stories: queue → memo → flags → approve/override → history)*

**Component**: C5 Underwriter UI.
**Anticipated build units**: `ui-queue`, `ui-memo-view`, `ui-approval-gate`,
`ui-override-form`, `ui-history`, `ui-auth-rbac` (shared with EPIC-6).
**Tech**: React + Tailwind only — **TypeScript is not an approved requirement**
(FR-UI-5).
**Epic DoD**: full underwriter journey works end-to-end; no recommendation becomes
a committed decision without explicit underwriter action carrying a reason; every
interactive element carries `data-testid`; copy uses "recommendation".

### US-UI-1 — View the application queue
**Phase: 1**
*As an* underwriter, *I want* to see a queue of applications awaiting review, *so
that* I can pick the next case to work.
**Traces:** FR-UI-1, FR-UI-3, PER-1

```gherkin
Given I am logged in as an underwriter
When I open the application queue
Then I see applications awaiting review with their current recommendation
And each queue row exposes a data-testid for automation
And the queue labels the system output as a "recommendation"
```

### US-UI-2 — Review the decision memo with rule citations
**Phase: 1**
*As an* underwriter, *I want* to open a case and read its memo with every cited
rule, *so that* I understand the basis for the recommendation.
**Traces:** FR-UI-1, NFR-EXPLAIN-1, FR-MEMO-3

```gherkin
Given a selected application
When I open its decision memo
Then I see the recommendation and every triggered rule cited by ID with its triggering value
And I see the confidence level and any missing documents
And all memo-view interactive elements carry data-testid attributes
```

### US-UI-3 — Check outlier flags and SHAP explanations
**Phase: 2**
*As an* underwriter, *I want* to see outlier flags with their SHAP explanations in
the memo view, *so that* I can weigh statistical anomalies before acting.
**Traces:** FR-UI-1, FR-OUT-2

```gherkin
Given a case that the outlier model has flagged
When I view its memo
Then I see each outlier flag with its SHAP feature explanation
And flags with no explanation never appear
And the flag elements carry data-testid attributes
```

### US-UI-4 — Approve a recommendation at the human approval gate
**Phase: 1**
*As an* underwriter, *I want* a gate where I must explicitly act before any outcome
is committed, *so that* the human-in-the-loop constraint is structural, not a UI
nicety.
**Traces:** FR-UI-2, CON-BR4, BR4

```gherkin
Given a reviewed application with a recommendation
When I approve it at the human approval gate
Then the decision is committed only after my explicit action
And the committed record stores my underwriter_id and the approval
And no recommendation can become a committed decision without passing this gate
```

### US-UI-5 — Override a recommendation with a mandatory reason
**Phase: 1**
*As an* underwriter, *I want* to override a recommendation only by supplying a
mandatory reason, *so that* every deviation is captured and defensible.
**Traces:** FR-UI-1, CON-BR4, BR4

```gherkin
Given a reviewed application with a recommendation
When I choose to override and submit without a reason
Then the override is rejected and the decision is not committed
When I submit the override with a reason
Then the decision is committed with my underwriter_id and the reason
And the decision-write path rejects any record lacking underwriter_id + reason
```

### US-UI-6 — View the full decision history
**Phase: 1**
*As an* underwriter, *I want* to see the full history of past decisions, *so that*
I have continuity and context across cases.
**Traces:** FR-UI-1, CON-AUDIT-1

```gherkin
Given committed decisions exist
When I open the decision history
Then I see each past decision with its recommendation, the committed outcome, and timestamp
And each entry links to the audit tuple for that decision
And history rows carry data-testid attributes
```

### US-UI-7 — Enforce advisory-only copy and data-testid coverage across the UI
**Phase: 1**
*As an* underwriter, *I want* the whole UI to say "recommendation" (never
"decision" for system output) and every interactive element to carry data-testid,
*so that* the advisory framing and automated testing posture hold everywhere.
**Traces:** FR-UI-3, FR-UI-4, FR-UI-5

```gherkin
Given any screen in the Underwriter UI
When it renders system output
Then it uses "recommendation" and reserves "decision" for the human's committed action
And every interactive element carries a data-testid attribute
And the UI is built with React + Tailwind only (no TypeScript requirement)
```

---

## 7. EPIC-6 — Platform, Quality & Access  *(cross-cutting; persona-benefiting NFR/quality stories per Q2 = B)*

**Spans components**: auth/RBAC, the quality/eval suites, the synthetic corpus,
audit/replay persistence, observability, deployment, and the minimal admin path.
**Anticipated build units**: `auth-rbac`, `audit-store`, `bias-swap-suite`,
`reproducibility-suite`, `rule-coverage-report`, `coverage-gate`, `corpus-generator`,
`observability` (Langfuse + Prometheus/Grafana), `llm-judge` (promptfoo),
`deploy-config` (Render + Vercel), `admin-cli`, `secrets-config`.
**Epic DoD**: the blocking gates pass at full strength; auditor has read-only
evidence surfaces; admin operates via CLI; secrets never hardcoded.

### US-PLAT-1 — Enforce RBAC separation (underwriter acts, auditor read-only)
**Phase: 1**
*As a* compliance/audit reviewer, *I want* role-based access that lets underwriters
act but restricts me to read-only, *so that* I cannot edit what I audit.
**Traces:** PER-4, PER-5, SEC-4

```gherkin
Given JWT/session authentication with roles underwriter and auditor
When an auditor attempts any write/edit/approve action in the UI
Then the action is denied by RBAC
And an underwriter retains act/approve/override capability
And the auth layer is structured so an OIDC/SSO provider can be added later without rework
```

### US-PLAT-2 — Give the auditor a read-only audit trail and decision history
**Phase: 1**
*As a* compliance/audit reviewer, *I want* read-only access to decision history and
the full audit trail, *so that* I can verify every recommendation is traceable.
**Traces:** PER-2, SEC-4, SEC-5, CON-AUDIT-1

```gherkin
Given committed decisions with their audit tuples
When I browse as an auditor
Then I can open any past decision read-only and see rulebook_version, rule_results, timestamp, model_version, and memo_hash
And I cannot modify any record
And my access is backed by a read-only database role
```

### US-PLAT-3 — Bias-swap invariance report (delta = 0; any delta blocking)
**Phase: 1** *(analytical/report — bullet criteria)*
*As a* compliance/audit reviewer, *I want* an automated bias-swap report proving the
recommendation is invariant across protected-attribute swaps, *so that* I have
reproducible evidence the system is bias-free by design.
**Traces:** NFR-BIAS-1, QA-2, CON-BR1, AC-3, FR-PROV-GATE-1

- The suite swaps name / gender / city across otherwise-identical financials and asserts the recommendation is unchanged.
- It adds a proxy-variable check over **pincode, occupation, and income**; occupation and income may differ only through their sanctioned rule (occupation-risk rule / affordability rule).
- **Bias-swap delta = 0. Any delta is a blocking bug, not a warning.**
- The report is automated, reproducible, and runs in CI.
- The report is viewable by the auditor as a read-only artifact.

### US-PLAT-4 — Reproducibility / calibration suite (100%)
**Phase: 1** *(analytical/report — bullet criteria)*
*As a* compliance/audit reviewer, *I want* a calibration suite proving identical
input yields the identical decision, *so that* reproducibility is demonstrable.
**Traces:** NFR-REPRO-1, QA-1, AC-1, CON-BR2, FR-PROV-GATE-1

- Runs the same input 10 times and asserts an identical APPROVE / REFER / DECLINE-RECOMMEND each run.
- **Decision reproducibility = 100%**, asserted on the deterministic engine output, **not** on LLM memo wording.
- Enforced via temperature=0, the deterministic engine, and seeded outlier randomness.
- The result is a reproducible, CI-run report viewable by the auditor.

### US-PLAT-5 — Rule-coverage report (100% of rules)
**Phase: 1** *(analytical/report — bullet criteria)*
*As a* compliance/audit reviewer, *I want* a report proving every rule is exercised
by at least one test, *so that* no rule ships untested.
**Traces:** QA-3, AC-4

- Every rule in the rulebook is exercised by ≥ 1 test case.
- **Rule coverage = 100%. Any uncovered rule is a blocking test failure.**
- The report is generated as part of the eval suite and runs in CI.

### US-PLAT-6 — Code-coverage gate (≥ 90%, binding)
**Phase: 1** *(analytical/report — bullet criteria)*
*As a* member of the implementing team, *I want* a binding code-coverage gate, *so
that* quality is enforced from day one (TDD).
**Traces:** AC-5, QA-6

- **Code coverage ≥ 90% is binding** (95% aspirational); measured by pytest-cov.
- TDD enforced: no production code without tests.
- The gate fails the build when coverage drops below 90%.

### US-PLAT-7 — Generate the seeded, skew-audited synthetic corpus (300+, 40/35/25)
**Phase: 1** *(analytical/report — bullet criteria)*
*As a* member of the implementing team, *I want* a validated synthetic corpus, *so
that* the outlier model, reproducibility suite, and bias suite all run on
trustworthy data.
**Traces:** DATA-1, DATA-2, DATA-3, CON-BR3, FR-PROV-4

- 300+ profiles with a ~40/35/25 APPROVE / REFER / DECLINE-RECOMMEND split.
- All mandatory edge cases present: thin-file, self-employed/irregular income, exact-threshold boundaries, single-missing-document, age 18/65, BMI 25/30.
- Seeded, version-stamped via a manifest, and skew-audited **before use**.
- The generator is validated on a small batch first, then the full corpus is shipped; document text is generated with the primary provider (Gemini) and frozen by the manifest.
- Zero real PII — synthetic/mock data only.

### US-PLAT-8 — Persist the full audit tuple and support replay
**Phase: 1**
*As a* compliance/audit reviewer, *I want* every recommendation to persist its full
audit tuple, *so that* any past decision is replayable.
**Traces:** CON-AUDIT-1, SEC-5, DATA-5

```gherkin
Given any recommendation produced by the system
When it is persisted
Then the record stores rulebook_version, rule_results, timestamp, model_version, and memo_hash
And the data is stored in PostgreSQL (no SQLite, to avoid dialect drift)
And any past decision can be replayed against its original rulebook version
```

### US-PLAT-9 — Observability: Langfuse traces (100% of steps) + Prometheus/Grafana
**Phase: 2**
*As a* member of the implementing team, *I want* every agent/tool step traced and a
metrics dashboard, *so that* the system is observable end to end.
**Traces:** NFR-OBS-1, NFR-OBS-2, AC-7

```gherkin
Given the system processing applications
When agent and tool steps execute
Then Langfuse captures traces for 100% of agent/tool steps
And one Grafana dashboard shows ~5 metrics: decision latency, decisions by recommendation type, rule-evaluation duration, LLM-call errors, and outlier-flag rate
```

### US-PLAT-10 — LLM-as-judge groundedness (≥ 4/5; Gemini + Claude; Ollama exempt)
**Phase: 2** *(analytical/report — bullet criteria)*
*As a* member of the implementing team, *I want* a groundedness rubric scoring memo
quality, *so that* memos stay anchored to evidence.
**Traces:** QA-4, AC-2, AC-6, FR-PROV-GATE-2

- promptfoo LLM-as-judge groundedness rubric scores memo quality at **≥ 4/5**.
- Applies to **Gemini (primary) + Claude (secondary)**; **Ollama is exempt** (showcase-only).
- Memo wording is anchored to a reference memo via few-shot (consistency, not bit-identical).

### US-PLAT-11 — Validation/staging deploy to Render + Vercel
**Phase: 2**
*As a* member of the implementing team, *I want* a working validation deploy on
Render + Vercel, *so that* cloud-readiness is confirmed this engagement.
**Traces:** NFR-DEPLOY-1
*(Production deploy = Phase 3 / future release, OOS-4.)*

```gherkin
Given the completed application
When it is deployed for validation
Then the backend runs on Render and the frontend on Vercel as a validation/staging deployment
And the deploy uses free-tier, open-source-friendly configuration
And this validation deploy is explicitly distinct from a production deploy (Phase 3)
```

### US-PLAT-12 — Secrets management (no hardcoded keys)
**Phase: 1**
*As a* member of the implementing team, *I want* all provider keys supplied via
env/secrets, *so that* no credential is ever hardcoded.
**Traces:** SEC-3

```gherkin
Given the application configuration
When provider or service credentials are needed
Then they are read from environment/secrets, never hardcoded in source
And a check fails the build if a hardcoded secret is detected
```

### US-ADMIN-1 — Manage rulebook versions via CLI / migration (minimal)
**Phase: 1**
*As a* system administrator, *I want* to publish and manage rulebook versions via
CLI/migrations, *so that* versions stay immutable and replayable without an admin
UI.
**Traces:** PER-3, PER-6, FR-RULES-6

```gherkin
Given I operate out-of-band via CLI/migrations (no admin UI)
When I publish a new rulebook version
Then a new version is created and previously published versions remain immutable
And existing decisions still replay against their original versions
```

### US-ADMIN-2 — Manage users and configuration via CLI (minimal)
**Phase: 1**
*As a* system administrator, *I want* to manage users, roles, and provider config
via CLI, *so that* the platform is administrable without building admin screens.
**Traces:** PER-3, PER-6, FR-PROV-1, SEC-3

```gherkin
Given I operate via CLI (admin is not a UI role)
When I create a user with the underwriter or auditor role, or change the active provider
Then the change takes effect under RBAC and provider-abstraction config
And no admin UI is required for these operations
```

---

## 8. Phase view (first-class, sliceable backlog)

> "What's in Phase 1" at a glance. Phase 1 = the core deterministic advisory
> slice + its blocking quality gates; Phase 2 = ML explainability, observability,
> and the validation deploy. **No Phase 3 stories** (OOS-1..6 = documented-only).

### Phase 1 (build first — core deterministic advisory slice)

| Story | Title |
|---|---|
| US-INTAKE-1 | Parse application + documents into a validated profile |
| US-INTAKE-2 | Reject malformed input at the validation gate |
| US-INTAKE-3 | Keep thin-file / single-missing-doc cases processable (→ REFER) |
| US-INTAKE-4 | Sanitize/sandbox uploaded text (prompt-injection defense) |
| US-RULES-1 | Versioned YAML + pure-Python rules engine |
| US-RULES-2 | Exact triggering value + comparison; boundary correctness |
| US-RULES-3 | Exact recommendation enum from the engine only |
| US-RULES-4 | Immutable versioning + replay |
| US-RULES-5 | Occupation = legitimate input + proxy-guard |
| US-MEMO-1 | Memo never alters the recommendation |
| US-MEMO-2 | temperature=0 + structured output + provider abstraction (Gemini) |
| US-MEMO-3 | Cite every rule; validate cited IDs (hallucination guard) |
| US-MEMO-4 | Advisory-only language |
| US-UI-1 | View application queue |
| US-UI-2 | Review memo with rule citations |
| US-UI-4 | Human approval gate |
| US-UI-5 | Override with mandatory reason |
| US-UI-6 | View decision history |
| US-UI-7 | Advisory-only copy + data-testid coverage |
| US-PLAT-1 | RBAC separation (underwriter vs auditor) |
| US-PLAT-2 | Auditor read-only audit trail + history |
| US-PLAT-3 | Bias-swap report (delta = 0, blocking) |
| US-PLAT-4 | Reproducibility/calibration suite (100%) |
| US-PLAT-5 | Rule-coverage report (100%) |
| US-PLAT-6 | Code-coverage gate (≥ 90%, binding) |
| US-PLAT-7 | Synthetic corpus (300+, 40/35/25, skew-audited) |
| US-PLAT-8 | Audit tuple persistence + replay |
| US-PLAT-12 | Secrets management |
| US-ADMIN-1 | Rulebook version management via CLI |
| US-ADMIN-2 | User/config management via CLI |

### Phase 2 (build next — ML, observability, validation deploy)

| Story | Title |
|---|---|
| US-OUT-1 | Seeded outlier scoring (IsolationForest + z-scores) |
| US-OUT-2 | SHAP explanation for every flag |
| US-OUT-3 | Demographic identifiers excluded from feature vector |
| US-MEMO-5 | MCP tool exposure + provider adapters |
| US-MEMO-6 | Borderline routing to extended thinking |
| US-MEMO-7 | Tested secondary (Claude) + wired-only Ollama |
| US-UI-3 | Check outlier flags / SHAP in the UI |
| US-PLAT-9 | Observability (Langfuse + Prometheus/Grafana) |
| US-PLAT-10 | LLM-as-judge groundedness (≥ 4/5; Ollama exempt) |
| US-PLAT-11 | Validation/staging deploy (Render + Vercel) |

---

## 9. Traceability matrix (story ↔ requirement IDs)

| Story | Phase | Requirement IDs |
|---|:--:|---|
| US-INTAKE-1 | 1 | FR-INTAKE-1, FR-INTAKE-2, DATA-4 |
| US-INTAKE-2 | 1 | FR-INTAKE-2, SEC-2 |
| US-INTAKE-3 | 1 | FR-INTAKE-3 |
| US-INTAKE-4 | 1 | SEC-1 |
| US-RULES-1 | 1 | FR-RULES-1, CON-BR2, CON-DET-1 |
| US-RULES-2 | 1 | FR-RULES-3, FR-RULES-4, NFR-EXPLAIN-1 |
| US-RULES-3 | 1 | FR-RULES-5, CON-BR2, QA-5 |
| US-RULES-4 | 1 | FR-RULES-6, CON-AUDIT-1, NFR-VERSION-1 |
| US-RULES-5 | 1 | FR-RULES-2, CON-BR1 |
| US-OUT-1 | 2 | FR-OUT-1, CON-DET-1, CON-BR3 |
| US-OUT-2 | 2 | FR-OUT-2, NFR-EXPLAIN-1 |
| US-OUT-3 | 2 | FR-OUT-3, CON-BR1, DATA-4 |
| US-MEMO-1 | 1 | FR-MEMO-1, CON-BR2, QA-5 |
| US-MEMO-2 | 1 | FR-MEMO-2, FR-PROV-1, FR-PROV-2, FR-PROV-3 |
| US-MEMO-3 | 1 | FR-MEMO-3, NFR-EXPLAIN-1 |
| US-MEMO-4 | 1 | FR-MEMO-4, CON-BR4, BR4 |
| US-MEMO-5 | 2 | FR-MEMO-5 |
| US-MEMO-6 | 2 | FR-MEMO-6, FR-MEMO-7, FR-PROV-5 |
| US-MEMO-7 | 2 | FR-PROV-2, FR-PROV-GATE-2 |
| US-UI-1 | 1 | FR-UI-1, FR-UI-3, PER-1 |
| US-UI-2 | 1 | FR-UI-1, NFR-EXPLAIN-1, FR-MEMO-3 |
| US-UI-3 | 2 | FR-UI-1, FR-OUT-2 |
| US-UI-4 | 1 | FR-UI-2, CON-BR4, BR4 |
| US-UI-5 | 1 | FR-UI-1, CON-BR4, BR4 |
| US-UI-6 | 1 | FR-UI-1, CON-AUDIT-1 |
| US-UI-7 | 1 | FR-UI-3, FR-UI-4, FR-UI-5 |
| US-PLAT-1 | 1 | PER-4, PER-5, SEC-4 |
| US-PLAT-2 | 1 | PER-2, SEC-4, SEC-5, CON-AUDIT-1 |
| US-PLAT-3 | 1 | NFR-BIAS-1, QA-2, CON-BR1, AC-3, FR-PROV-GATE-1 |
| US-PLAT-4 | 1 | NFR-REPRO-1, QA-1, AC-1, CON-BR2, FR-PROV-GATE-1 |
| US-PLAT-5 | 1 | QA-3, AC-4 |
| US-PLAT-6 | 1 | AC-5, QA-6 |
| US-PLAT-7 | 1 | DATA-1, DATA-2, DATA-3, CON-BR3, FR-PROV-4 |
| US-PLAT-8 | 1 | CON-AUDIT-1, SEC-5, DATA-5 |
| US-PLAT-9 | 2 | NFR-OBS-1, NFR-OBS-2, AC-7 |
| US-PLAT-10 | 2 | QA-4, AC-2, AC-6, FR-PROV-GATE-2 |
| US-PLAT-11 | 2 | NFR-DEPLOY-1 |
| US-PLAT-12 | 1 | SEC-3 |
| US-ADMIN-1 | 1 | PER-3, PER-6, FR-RULES-6 |
| US-ADMIN-2 | 1 | PER-3, PER-6, FR-PROV-1, SEC-3 |

### Reverse coverage check (every requirement exercised by ≥ 1 story)

- **FR-INTAKE-1..3** → US-INTAKE-1/2/3. **FR-RULES-1..6** → US-RULES-1/2/3/4/5 (+ FR-RULES-6 via US-ADMIN-1).
- **FR-OUT-1..3** → US-OUT-1/2/3. **FR-MEMO-1..7** → US-MEMO-1/2/3/4/5/6 (FR-MEMO-7 is traced by US-MEMO-6; US-MEMO-7 carries FR-PROV-2/FR-PROV-GATE-2, not any FR-MEMO-*). **FR-UI-1..5** → US-UI-1..7.
- **FR-PROV-1..5** → US-MEMO-2/6/7, US-PLAT-7, US-ADMIN-2. **FR-PROV-GATE-1** (decision-level, provider-independent) → US-PLAT-3 / US-PLAT-4. **FR-PROV-GATE-2** (memo-quality, Gemini+Claude) → US-MEMO-7 / US-PLAT-10.
- **CON-BR1..4** → US-RULES-5/US-PLAT-3 (BR1), US-RULES-1/3 + US-PLAT-4 (BR2), US-PLAT-7 (BR3), US-UI-4/5 + US-MEMO-4 (BR4). **CON-AUDIT-1** → US-RULES-4, US-PLAT-2/8. **CON-DET-1** → US-RULES-1, US-OUT-1.
- **PER-1..6** → personas.md + US-UI-1 (PER-1), US-PLAT-1/2 (PER-2/4/5), US-ADMIN-1/2 (PER-3/6).
- **DATA-1..5** → US-PLAT-7 (1/2/3), US-INTAKE-1/US-OUT-3 (DATA-4), US-PLAT-8 (DATA-5).
- **NFR-REPRO-1/BIAS-1/EXPLAIN-1/OBS-1/2/DEPLOY-1/VERSION-1** → US-PLAT-4/3, US-RULES-2 + US-OUT-2 + US-MEMO-3, US-PLAT-9, US-PLAT-11, US-RULES-4.
- **SEC-1..5** → US-INTAKE-4/2, US-PLAT-12, US-PLAT-1/2, US-PLAT-2/8.
- **QA-1..6** → US-PLAT-4/3/5, US-PLAT-10, US-RULES-3/MEMO-1 (QA-5), US-PLAT-6 (QA-6).
- **AC-1..7** → US-PLAT-4 (AC-1), US-PLAT-10 (AC-2), US-PLAT-3 (AC-3), US-PLAT-5 (AC-4), US-PLAT-6 (AC-5), US-PLAT-10 (AC-6), US-PLAT-9 (AC-7).

*All requirement families are covered. OOS-1..6 are intentionally uncovered
(Phase 3 / future release, documented-only).*

---

*End of stories. Awaiting approval at the User Stories gate before proceeding to
Workflow Planning.*
