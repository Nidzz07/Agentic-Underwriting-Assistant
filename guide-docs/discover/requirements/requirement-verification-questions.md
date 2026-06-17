# Requirements Verification Questions — Agentic Underwriting Assistant

**Depth**: Comprehensive (complex, high-stakes, regulated BFSI system)

PROJECT-BRIEF.md already specifies a great deal (architecture, tech stack, acceptance
criteria, failure modes, hard constraints). These questions target the decisions the
brief leaves **open or ambiguous** — they will shape scope, sequencing, and design.

**How to answer**: For each question, write your choice's letter after the `[Answer]:` tag
(e.g., `[Answer]: B`). If none fit, choose the last option **(Other)** and describe your
preference after the tag. You may select multiple letters where it makes sense (e.g.
`[Answer]: A, C`) and add free-text notes. Answer all questions, then tell me you're done.

---

## Section A — Scope & Delivery

## Question 1
What is the build scope for **this** engagement?

A) Full system end-to-end — all 5 components (Intake, Rulebook Engine, Outlier Detection, Decision-Memo Agent, Underwriter UI) plus evals, observability, and deployment
B) Phased MVP first — core decision path only (Intake → Rulebook Engine → Decision-Memo Agent → minimal UI), with Outlier Detection, full observability, and deployment in a later phase
C) Backend/engine only for now — all server-side components + evals, defer the React UI to a later phase
X) Other (please describe after [Answer]: tag below)

[Answer]: A — Full system end-to-end is the target. REASON: all five components plus evals and observability are listed deliverables, and the outlier/SHAP path and tracing are what make this portfolio/audit-grade. NOTE: the work will be delivered in phases (Phase 1 = Intake → Rules → Decision-Memo → minimal demoable UI), but the exact phase boundaries and any later phases are NOT fixed here — phasing is to be finalized during Workflow Planning / Units Generation, where the unit breakdown makes the right split clear.

## Question 2
Which underwriting product line should the rulebook and synthetic data prioritize?

A) Life/health insurance underwriting (matches the Canara HSBC proof point; BMI/age/health flags central)
B) Loan/credit underwriting (income multiple, DTI, employment central)
C) Both, as a unified rulebook with product-specific rule subsets
X) Other (please describe after [Answer]: tag below)

[Answer]: A — anchor to life/health (matches the Canara HSBC proof point). REASON: the proof point is Canara HSBC Life, so life/health gives one coherent, defensible rulebook. Implement income-multiple / DTI rules as affordability rules (premium-to-income, sum-assured-to-income), not separate credit rules — so nothing is lost from the brief's thresholds.

## Question 3
How should this build treat the rule thresholds named in the brief (DTI ≤ 40%, age 18–65, BMI 25/30, income multiples, IRDAI 2024)?

A) Authoritative — implement exactly as written in the brief
B) Illustrative starting points — implement them but expect refinement with a domain expert before production
C) I will provide a separate authoritative rule specification before rule coding begins
X) Other (please describe after [Answer]: tag below)

[Answer]: B — illustrative starting points, refinement expected. REASON: synthetic data, no domain expert in the loop, advisory-only system. Treating thresholds as illustrative-pending-expert-review is the intellectually honest position and reinforces the advisory framing central to the project.

## Question 4
The brief lists a model-switch capability (Claude / Gemini / Ollama / OpenAI). What should this build implement?

A) Claude-first — build a clean provider-abstraction layer and implement Claude (Opus 4.8) only now; wire other providers later
B) Claude + one alternate (e.g., Ollama local) to prove the switch works end-to-end
C) All four providers fully wired in this build
X) Other (please describe after [Answer]: tag below)

[Answer]: X — Gemini PRIMARY, Claude SECONDARY (tested fallback), Ollama showcase-only (wired but NOT tested against acceptance criteria), all behind a clean provider-abstraction layer with the provider runtime-selectable via config/settings. REASON: Gemini is the less expensive provider, so it is the primary; Claude is retained as a fully tested secondary to prove the switch works; Ollama demonstrates local/offline capability without being held to the calibration/bias/groundedness gates. The abstraction layer + settings selector keeps the system vendor-agnostic (per the brief). NOTE: CLAUDE.md currently names Claude as primary — CLAUDE.md is developer-owned and will be updated to reflect Gemini-primary so the project config is consistent (no contradiction left behind).

---

## Section B — Users & Access

## Question 5
Which user personas must the system serve in this build? (Select all that apply.)

A) Underwriter (primary — reviews memos, approves/overrides)
B) Senior underwriter / approver (handles REFER escalations, second-level sign-off)
C) Compliance/audit reviewer (read-only access to decision history and audit trail)
D) System administrator (manages rulebook versions, users, configuration)
X) Other (please describe after [Answer]: tag below)

[Answer]: A, C, D — Underwriter (primary), Compliance/audit reviewer (read-only), System administrator (rulebook-version + config management; keep minimal, CLI/migration acceptable rather than a full admin UI). REASON: A is mandatory; C (read-only) directly serves the "audit-ready" selling point and the segregation-of-duties requirement; D is needed because rulebook versioning requires a management role. Defer senior-underwriter escalation (B) to a later phase — it adds workflow complexity without serving an acceptance criterion.

## Question 6
What authentication/authorization model should the Underwriter UI use?

A) Single-user demo — no real auth, focus on the underwriting workflow (suitable for portfolio demo)
B) Basic login with role-based access (underwriter vs admin/auditor), JWT/session-based
C) Full SSO/OAuth integration
X) Other (please describe after [Answer]: tag below)

[Answer]: B — basic login with role-based access (JWT/session). REASON: RBAC is what actually enforces the Q5 role separation (the auditor cannot edit what they audit), which is the part this project genuinely needs. Full SSO/OAuth is federated identity that depends on a company IdP and adds demo friction with no acceptance-criterion payoff; it belongs with the eventual enterprise/production handover, not this build. Auth layer will be structured so an OIDC provider can slot in later.

---

## Section C — Technical & Data Decisions

## Question 7
Database strategy for local development and the deployed demo?

A) PostgreSQL everywhere (local via Docker + Render Postgres in deployment) — matches the brief exactly
B) SQLite for local dev, PostgreSQL in deployment (via SQLAlchemy abstraction) — faster local setup
C) PostgreSQL only, no local Docker (use a hosted dev database)
X) Other (please describe after [Answer]: tag below)

[Answer]: A — PostgreSQL everywhere (local via Docker). REASON: SQLite-local/Postgres-prod introduces dialect drift (JSON handling, types) that can break the decision-replay/versioning feature — "works locally, differs in prod" is fatal for a system selling reproducibility. Docker Postgres locally removes that risk.

## Question 8
The synthetic corpus (300+ profiles, ~40/35/25 APPROVE/REFER/DECLINE split, mandatory edge cases). For this build:

A) Generate it as part of this build using Faker + Claude for document text, including all mandatory edge cases (thin-file, self-employed, boundary values)
B) Generate a smaller seed set now (e.g., ~50 profiles) to validate the pipeline, scale to 300+ later
C) I will supply the dataset; do not generate it
X) Other (please describe after [Answer]: tag below)

[Answer]: A — full 300+ corpus with the 40/35/25 split and all mandatory edge cases is the deliverable; validate the generator on a small batch first, but ship the full corpus. REASON: the corpus size and split are acceptance-criteria-bearing, and IsolationForest/z-scores are meaningless on ~50 profiles. The corpus must be seeded, version-stamped, and skew-audited (see Build Rule 3). NOTE: exactly WHEN the corpus is generated relative to phases (it is needed in Phase 1 for the reproducibility/bias tests, while the outlier model that consumes it is later) is to be confirmed as a question at a later stage, not fixed here.

## Question 9
Which quality & safety test suites from the brief must be in scope for **this** build? (Select all that apply.)

A) Reproducibility / calibration suite (same input × 10 runs → identical output)
B) Bias-swap invariance suite (swap name/gender/city → zero delta; any delta = blocking)
C) Rule-coverage report (every rule exercised by ≥1 test case)
D) LLM-as-judge groundedness rubric (promptfoo, ≥4/5) for memo quality
X) Other (please describe after [Answer]: tag below)

[Answer]: A, B, C, D — all four are acceptance criteria in the brief, not optional; bias-swap delta=0 and rule-coverage=100% are blocking. REASON: each maps to a stated acceptance criterion. IMPORTANT SCOPE CLARIFICATION (per Build Rules): (A) reproducibility is asserted on the DECISION (APPROVE/REFER/DECLINE), which comes from the deterministic rules engine — NOT on LLM memo wording, since no LLM is deterministic even at temperature 0. (B) the bias suite asserts the DECISION is invariant and adds a proxy-variable check (pincode / occupation / income), not just name/gender/city. (D) groundedness is judged on the memo; memo wording is anchored toward a reference memo via few-shot prompting so it stays consistent without being claimed bit-identical.

## Question 10
Observability scope for this build?

A) Full stack now — Langfuse traces + Prometheus metrics + Grafana dashboards
B) Langfuse tracing first (per-agent/tool steps); add Prometheus/Grafana in a later phase
C) Minimal structured logging only for this phase; full observability later
X) Other (please describe after [Answer]: tag below)

[Answer]: A — full stack now: Langfuse traces + SCOPED Prometheus/Grafana. REASON: Langfuse satisfies the binding "100% of agent steps traced" criterion; Prometheus + Grafana satisfy deliverable #3. To avoid open-ended dashboard work, scope to ONE Grafana dashboard with ~5 metrics: decision latency, decisions by recommendation type, rule-evaluation duration, LLM-call errors, outlier-flag rate.

## Question 11
Deployment scope for this build?

A) Local-only (docker-compose / local run) — defer cloud deployment
B) Deploy the working demo to Render (backend) + Vercel (frontend) as part of this build
C) Containerize (Docker) and produce deploy configs, but I will run the actual deployment
X) Other (please describe after [Answer]: tag below)

[Answer]: B — deploy a working demo to Render (backend) + Vercel (frontend) as part of this build, treated as a validation/staging deployment to confirm cloud-readiness. REASON: a live demo is deliverable #1 and the highest-leverage portfolio artifact; the Render/Vercel deploy doubles as the "does it run in the cloud" check. Final/production cloud deployment is done separately later (timing/grouping to be settled when phasing is finalized).

## Question 12
The brief enables extended thinking for "complex/borderline" memo cases. How should the system decide a case is borderline (and route to extended thinking)?

A) Driven by the rulebook engine — e.g., any REFER outcome, or any value within a configurable margin of a threshold
B) Driven by the outlier detector — e.g., outlier score above a configured cutoff
C) Both A and B combined (rule-proximity OR outlier flag triggers extended thinking)
X) Other (please describe after [Answer]: tag below)

[Answer]: C — rule-proximity OR outlier-flag triggers extended thinking. REASON: this makes the outlier detector functional (it routes, not just reports), and both triggers stay deterministic (rule proximity is exact; the seeded outlier score is reproducible), so routing does not break the reproducibility guarantee. NOTE: the outlier-driven half (B) depends on the outlier model, which arrives in a later phase — until then routing runs on rule-proximity alone.

---

## Section D — Extensions (Governance)

## Question 13: Security Guardrails
Should the GUIDE-AI-SDP Security Guardrails be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)
B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)
X) Other (please describe after [Answer]: tag below)

[Answer]: A — enforce as blocking, SCOPED to: prompt-injection defense, input validation, secrets management, read-only DB access for the audit role, and audit logging. REASON: this is a regulated-BFSI build that explicitly lists prompt injection and malformed input as documented failure modes; each scoped control ties to something concrete (injection → failure mode #4; input validation → failure mode #5; read-only DB → Q5 auditor segregation; audit logs → the auditability selling point). Scoping keeps "enforce all" from becoming unbounded.

---

## Build Rules / Engineering Constraints (binding — lift into requirements.md)

1. **Bias test measures the DECISION, not memo text.** The bias-swap suite asserts the recommendation (APPROVE/REFER/DECLINE) is invariant across name/gender/city swaps, AND adds a proxy-variable check (pincode, occupation, income). Income is a legitimate affordability factor, so it must be tested to influence the decision ONLY through the affordability rule, never via a back-door correlation.

2. **LLM stays OUT of the decision path; temperature 0 is NOT determinism.** The APPROVE/REFER/DECLINE outcome is produced entirely by the deterministic Python rules engine. The LLM only drafts the memo prose and may not alter the recommendation. This is what makes "100% reproducibility" literally true. A test must assert the LLM cannot change a recommendation.

3. **Synthetic corpus = seeded + versioned + skew-audited; feeds 3 tests.** Generated with a fixed seed, version-stamped with a manifest, and skew-audited (asserts the 40/35/25 split and presence of all mandatory edge cases) before use. It feeds: the outlier model, the reproducibility suite, and the bias suite.

4. **"Advisory only" is enforced in the system, not as a disclaimer.** Every finalized decision requires an explicit underwriter action carrying a reason; the decision-write path rejects any record lacking underwriter_id + reason. This is a backend constraint, not UI copy.

---

## Deferred Decisions Register (re-raise at the stated GUIDE stage)

- **Phase boundaries / whether there is a Phase 3:** decide at **Workflow Planning / Units Generation** (unit breakdown will clarify the right split). Do not fix now.
- **SSO/OAuth timing:** revisit when phasing is finalized; not phase-numbered now.
- **Synthetic corpus generation timing (relative to phases):** surface as a question at the appropriate later stage.
- **Senior-underwriter escalation persona (Q5-B):** deferred; reconsider if escalation workflow enters scope.

*Per project direction: do not over-fixate decisions now. Where a decision is clearer at a
later GUIDE stage (especially the User Stories stage), defer it and re-raise it there rather
than locking it prematurely.*

---

*After you answer, I'll analyze the responses for any ambiguities or contradictions
(asking focused follow-ups if needed), then generate `requirements.md` for your approval.*