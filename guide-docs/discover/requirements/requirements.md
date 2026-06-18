# Requirements — Agentic Underwriting Assistant

**Phase / Stage**: DISCOVER → Requirements Analysis
**Depth**: Comprehensive (complex, high-stakes, regulated BFSI system)
**Generated**: 2026-06-17
**Status**: Draft — pending user approval at the Requirements approval gate

## Sources & Traceability Convention

Every requirement traces to one of:
- `Q<n>` — an answer in `requirement-verification-questions.md`
- `BR<n>` — one of the four Build Rules in that same file (binding)
- `Brief §<n>` — `PROJECT-BRIEF.md` (as amended 2026-06-17 for provider precedence)
- `Skill` — the `underwriting-rules` domain hard constraints

ID prefixes: `FR` functional, `NFR` non-functional, `CON` binding engineering
constraint, `SEC` security, `DATA` data, `QA` quality/test, `AC` acceptance
criterion, `PER` persona/access. `MUST` = blocking; `SHOULD` = strong default.

---

## 1. Intent Analysis

Build a production-grade, **advisory-only** agentic underwriting assistant for
life/health insurance (Canara HSBC OmniGen proof point) that: ingests
applications + documents into a validated profile; evaluates them against a
versioned **deterministic** rulebook; compares each applicant against a
synthetic corpus via ML outlier detection; and drafts an audit-ready decision
memo for a **human underwriter** who is the only party that finalises an
outcome. The system is delivered end-to-end (all five components + evals +
observability + a validation deployment), in phases whose exact boundaries are
deferred to Workflow Planning / Units Generation.

The defining quality attributes — in priority order — are **explainability,
reproducibility, bias-invariance, and human oversight**, ahead of automation
speed.

---

## 2. Scope

### 2.1 In Scope (this engagement)

| ID | Requirement | Source |
|---|---|---|
| FR-SCOPE-1 | Deliver all five components end-to-end: Application Intake, Deterministic Rulebook Engine, Outlier Detection, Decision-Memo Agent, Underwriter UI. | Q1 (A), Brief §3 |
| FR-SCOPE-2 | Deliver the eval suite, observability stack, and a validation/staging cloud deployment as part of this engagement. | Q1 (A), Q10, Q11 |
| FR-SCOPE-3 | Anchor the rulebook and synthetic data to **life/health insurance** underwriting. Implement income-multiple / DTI thresholds as **affordability rules** (premium-to-income, sum-assured-to-income) so no brief threshold is lost. | Q2 (A) |
| FR-SCOPE-4 | Treat the brief's named thresholds (DTI ≤ 40%, age 18–65, BMI 25/30, income multiples, IRDAI 2024) as **illustrative starting points pending domain-expert review**, implemented as written but refinable. The advisory framing must reflect this. | Q3 (B) |

### 2.2 Phase 3 — Future Release (documented for reference; not built, no stories this engagement)

The items below are **documented for reference only**. They are **not built this engagement
and get no user stories this round**. Phase 1 + Phase 2 are built now (each story phase-tagged);
Phase 3 is a future release. Note the deployment split: a **validation/staging deploy is in
scope as Phase 2 (NFR-DEPLOY-1)**; only the **production deploy** is Phase 3.

| ID | Item | Disposition | Source |
|---|---|---|---|
| OOS-1 | ~~Exact phase boundaries / existence of a Phase 3~~ — **RESOLVED 2026-06-18** | **Phase 1 + Phase 2 built this engagement (each story phase-tagged 1/2); Phase 3 = future release.** No longer open. | Q1, Deferred Register |
| OOS-2 | Senior-underwriter / approver escalation persona & workflow — **REFER recommendations route to this escalation tier** | **Phase 3 — Future Release** (documented; not built, no stories this engagement). In Phase 1/2 the underwriter resolves every recommendation incl. REFER at the human approval gate (Accept/Decline with mandatory reason); REFER→senior-underwriter escalation routing is Phase 3. | Q5 (B excluded) |
| OOS-3 | Full SSO/OAuth federated identity | **Phase 3 — Future Release** (auth structured so OIDC can slot in later) | Q6 |
| OOS-4 | **Production** cloud deployment | **Phase 3 — Future Release.** Validation/staging deploy is **in scope (Phase 2, NFR-DEPLOY-1)**; only production deploy is Phase 3. | Q11 |
| OOS-5 | OpenAI provider | **Phase 3 — Future Release** (abstraction leaves it wireable; not wired this build) | Q4 |
| OOS-6 | Full admin UI | **Phase 3 — Future Release** (admin remains CLI/migration-based this engagement) | Q5 (D) |

---

## 3. Personas & Access

| ID | Requirement | Source |
|---|---|---|
| PER-1 | **Underwriter** (primary): reviews memos, approves/overrides, acts at the human approval gate. MUST be served. | Q5 (A), Brief §3 C5 |
| PER-2 | **Compliance/Audit reviewer**: **read-only** access to decision history and audit trail. MUST NOT be able to edit what they audit. | Q5 (C), Q13 |
| PER-3 | **System administrator**: manages rulebook versions, users, configuration. Minimal — **CLI / migration acceptable**, no full admin UI required. | Q5 (D) |
| PER-4 | Authentication = **basic login with role-based access (JWT/session)**. RBAC MUST enforce the PER-1/PER-2 separation in the UI (underwriter vs auditor). | Q6 (B) |
| PER-5 | Auth layer MUST be structured so an OIDC/SSO provider can be added later without rework. | Q6 |
| PER-6 | RBAC UI roles = underwriter + auditor(read-only); **admin operates out-of-band via CLI**, not a UI role. | Q5/Q6 (scoping) |

---

## 4. Functional Requirements (by Component)

### 4.1 Component 1 — Application Intake Agent

| ID | Requirement | Source |
|---|---|---|
| FR-INTAKE-1 | Parse application form + supporting documents (salary slips, bank statements, medical questionnaire) into a validated structured JSON `ApplicantProfile`. | Brief §3 C1 |
| FR-INTAKE-2 | Use pdfplumber + Pydantic v2 typed extraction with completeness validation. Malformed/broken input MUST be rejected at a Pydantic validation gate **before** agent entry. | Brief §3 C1, §10 FM5, SEC |
| FR-INTAKE-3 | Single-missing-document and thin-file cases MUST remain processable and route toward REFER, not a hard failure. | Skill, Brief §4 |

### 4.2 Component 2 — Deterministic Rulebook Engine

| ID | Requirement | Source |
|---|---|---|
| FR-RULES-1 | Codify ~25–40 underwriting rules in **versioned YAML**, evaluated by **pure Python with zero LLM involvement**. | Brief §3 C2, BR2, Skill |
| FR-RULES-2 | Rule domains: Financial (income multiple, DTI ≤ 40% as affordability, document completeness, employment-type flags, IRDAI 2024), Medical (BMI 25/30 bands, age 18–65 bands, health flags), Lifestyle (smoking, occupation risk). **Occupation** is a legitimate underwriting risk factor AND a proxy-checked variable: it may influence the decision **only** through its documented occupation-risk rule, never via a back-door correlation with a protected attribute (same carve-out as income). See CON-BR1. | Brief §3 C2, Q2, Skill |
| FR-RULES-3 | Each fired rule MUST report the **exact applicant value** that triggered it and the comparison applied (`<=` vs `<`), with boundary values (age 18/65, BMI 25/30, DTI 40%) landing on the intended side. | Skill, Brief §5.5 |
| FR-RULES-4 | Output a per-rule pass/fail report stamped with `rulebook_version`. | Brief §3 C2, §5.3 |
| FR-RULES-5 | The recommendation enum is exactly **APPROVE / REFER / DECLINE-RECOMMEND** (the `-RECOMMEND` suffix is mandatory; never emit a bare "DECLINE"). | Skill, Brief §3 C4 |
| FR-RULES-6 | Published rule versions are **immutable**; changes add a new version (never mutate in place). | Skill, Brief §5.3 |

### 4.3 Component 3 — Outlier Detection Agent

| ID | Requirement | Source |
|---|---|---|
| FR-OUT-1 | Compare each applicant against the synthetic corpus using z-scores + **IsolationForest**, with **seeded** randomness for reproducibility. | Brief §3 C3, §5.1, Skill |
| FR-OUT-2 | Produce an outlier score, flagged features, and a **SHAP** feature-importance explanation for every flag (no unexplained flags). | Brief §3 C3, §5.5 |
| FR-OUT-3 | Demographic identifiers MUST NOT enter the feature vector. | BR1, Skill, Brief §11.5 |

### 4.4 Component 4 — Decision-Memo Agent (LLM)

| ID | Requirement | Source |
|---|---|---|
| FR-MEMO-1 | Orchestrate via a LangGraph state machine; the LLM drafts memo prose **only after** deterministic results exist and **MUST NOT alter the recommendation**. | Brief §3 C4, BR2, Skill |
| FR-MEMO-2 | All production LLM calls use **`temperature=0`**, structured XML output → Pydantic validation. | Brief §8, CON, Skill |
| FR-MEMO-3 | Memo MUST cite every triggered rule by ID, confidence (Low/Med/High), missing-documents list, and outlier flags. Cited rule IDs MUST be validated against the YAML rulebook (hallucination guard). | Brief §3 C4, §10 FM1, Skill |
| FR-MEMO-4 | System prompt MUST enforce advisory-only language ("recommendation", never "decision"). | BR4, Skill, Brief §5.6 |
| FR-MEMO-5 | Expose rulebook engine and decisions DB to the agent via **MCP servers** as tools. MCP tool exposure and structured output may require **provider-specific adapters** behind the abstraction layer (Gemini function-calling/structured-output differs from Claude) — not assumed Claude-shaped. | Brief §9, §3 C4, FR-PROV-1 |
| FR-MEMO-6 | Route **borderline** cases to the active provider's extended-thinking / reasoning capability where supported. Borderline = rule-proximity (within a configurable margin of a threshold, incl. any REFER) **OR** outlier-flag above cutoff. Both triggers are deterministic. | Q12 (C), Brief §3 C4 |
| FR-MEMO-7 | The outlier-driven half of the borderline trigger depends on the outlier model; until it lands, routing runs on rule-proximity alone. | Q12 (note) |

### 4.5 Component 5 — Underwriter UI

| ID | Requirement | Source |
|---|---|---|
| FR-UI-1 | React + Tailwind UI with: application queue, memo view with rule citations, override with **mandatory reason** field, full decision history. | Brief §3 C5 |
| FR-UI-2 | A **human approval gate**: no recommendation becomes a committed decision without explicit underwriter action. | BR4, Skill, Brief §5.6 |
| FR-UI-3 | All interactive UI elements MUST carry `data-testid` attributes for automation. | Brief §3 C5 |
| FR-UI-4 | UI copy MUST use "recommendation"; "decision" is reserved for the human's committed action. | Skill, BR4 |
| FR-UI-5 | TypeScript is **not** an approved requirement; React + Tailwind only unless explicitly decided later. | guide-state, Q-tracking correction |

---

## 5. Binding Engineering Constraints (the four Build Rules + invariants)

These are **hard constraints**. Code, prompts, schemas, or UI that break any of
them are defects, not stylistic choices.

| ID | Constraint | Source |
|---|---|---|
| CON-BR1 | **Bias test measures the DECISION, not memo text.** The bias-swap suite asserts the recommendation (APPROVE/REFER/DECLINE-RECOMMEND) is invariant across name/gender/city swaps, AND adds a **proxy-variable check** covering **pincode, occupation, and income**. **Occupation and income** may each influence the outcome **only** through their legitimate rule (occupation → the occupation-risk rule; income → the affordability rule), never via a back-door correlation. The decision MUST be invariant to occupation and to income **except** through that one sanctioned rule each. | BR1 |
| CON-BR2 | **LLM stays OUT of the decision path; temperature 0 is NOT determinism.** The recommendation is produced entirely by the deterministic Python rules engine; the LLM only drafts prose and may not change it. A test MUST assert the LLM cannot change a recommendation. | BR2 |
| CON-BR3 | **Synthetic corpus = seeded + versioned + skew-audited.** Generated with a fixed seed, version-stamped with a manifest, and skew-audited (40/35/25 split + all mandatory edge cases present) before use. It feeds the outlier model, the reproducibility suite, and the bias suite. | BR3 |
| CON-BR4 | **"Advisory only" is enforced in the system, not as a disclaimer.** Every finalised decision requires explicit underwriter action carrying a reason; the decision-write path MUST reject any record lacking `underwriter_id` + `reason`. Backend constraint, not UI copy. | BR4 |
| CON-AUDIT-1 | Persist the full audit tuple on every recommendation: `rulebook_version`, `rule_results`, `timestamp`, `model_version`, `memo_hash`. Any past decision MUST be replayable against the exact rulebook version active at decision time. | Brief §5.3, Skill |
| CON-DET-1 | No unseeded randomness, wall-clock-dependent logic, or dict-ordering assumptions anywhere in evaluation. | Skill, Brief §5.1 |

---

## 6. Provider / Model Configuration

| ID | Requirement | Source |
|---|---|---|
| FR-PROV-1 | LLM provider is **runtime-selectable via config/settings** behind a clean provider-abstraction layer. | Q4, Brief §9 (amended) |
| FR-PROV-2 | **PRIMARY = Gemini** (less expensive); **SECONDARY = Claude Opus 4.8** (tested fallback); **SHOWCASE = Ollama** (local; wired but **not** tested against acceptance criteria). OpenAI left wireable, not wired. | Q4 |
| FR-PROV-3 | `temperature=0` MUST be enforced on **all** production calls regardless of provider. | Brief §8, Skill |
| FR-PROV-4 | The one-time synthetic-corpus document text is generated with the **primary provider (Gemini)**; output is frozen by the corpus manifest. | Q8 (resolved 2026-06-17) |
| FR-PROV-5 | Extended-thinking maps to the active provider's reasoning capability (Claude extended thinking; Gemini thinking budget; Ollama may not support it). The borderline **routing trigger** is provider-agnostic and deterministic. | Q12, FR-MEMO-6 |

### 6.1 Per-Provider Acceptance-Gate Scoping

| ID | Requirement | Source |
|---|---|---|
| FR-PROV-GATE-1 | **Decision-level** gates — reproducibility (100%) and bias-swap (delta 0) — apply to **all** providers, because the decision is provider-independent (CON-BR2). | Q4, Q9, BR2 |
| FR-PROV-GATE-2 | **Memo-quality** gates — groundedness ≥ 4/5 and memo calibration — apply to **Gemini (primary) + Claude (secondary)** only. **Ollama is exempt** (showcase-only). | Q4, Q9 |

---

## 7. Data Requirements

| ID | Requirement | Source |
|---|---|---|
| DATA-1 | Generate a **300+ profile** synthetic corpus with a ~**40/35/25** APPROVE/REFER/DECLINE-RECOMMEND split. Validate the generator on a small batch first, then ship the full corpus. | Q8 (A), Brief §4 |
| DATA-2 | Include all mandatory edge cases: thin-file, self-employed/irregular income, exact-threshold boundary values, single-missing-document, age 18/65, BMI 25/30. | Brief §4, Skill |
| DATA-3 | Corpus MUST be seeded, version-stamped via manifest, and skew-audited before use (see CON-BR3). | BR3 |
| DATA-4 | Synthetic/mock data only — **zero real PII** at any stage. | Brief §8, Skill |
| DATA-5 | Database = **PostgreSQL everywhere** (local via Docker + Postgres in deployment); no SQLite, to avoid dialect drift that could break decision replay/versioning. | Q7 (A) |

---

## 8. Non-Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| NFR-REPRO-1 | **Decision reproducibility = 100%**: identical input → identical APPROVE/REFER/DECLINE-RECOMMEND, asserted on the deterministic engine output (NOT on LLM memo wording). Validated by calibration suite (same input × 10 runs). | Q9 (A), BR2, Brief §5.1, §6 |
| NFR-BIAS-1 | **Bias-swap delta = 0** on the recommendation across name/gender/city swaps + proxy-variable check; any delta is a **blocking** bug. | Q9 (B), BR1, Brief §5.2, §6 |
| NFR-EXPLAIN-1 | Zero unexplained recommendations: every rule result cites its triggering value; every outlier flag carries a SHAP explanation; every memo cites rules by ID. | Brief §5.5, Skill |
| NFR-OBS-1 | **Langfuse** traces for **100% of agent/tool steps**. | Q10 (A), Brief §6, §7.3 |
| NFR-OBS-2 | **Prometheus + Grafana**, scoped to **one** dashboard with ~5 metrics: decision latency, decisions by recommendation type, rule-evaluation duration, LLM-call errors, outlier-flag rate. | Q10 (A) |
| NFR-DEPLOY-1 | Deploy a working demo to **Render (backend) + Vercel (frontend)** as a validation/staging deployment confirming cloud-readiness. | Q11 (B), Brief §7.1 |
| NFR-CONSTRAINTS-1 | Open-source frameworks and free-tier APIs only. | Brief §8 |
| NFR-VERSION-1 | Full rulebook versioning + replay capability per CON-AUDIT-1. | Brief §5.3 |

---

## 9. Quality & Safety Test Suites

| ID | Requirement | Source |
|---|---|---|
| QA-1 | **Reproducibility/calibration suite** — same input × 10 runs → identical decision. | Q9 (A) |
| QA-2 | **Bias-swap invariance suite** — name/gender/city swap + proxy check → zero decision delta (blocking). | Q9 (B), BR1 |
| QA-3 | **Rule-coverage report** — every rule exercised by ≥ 1 test case; uncovered rule = blocking failure. | Q9 (C), Brief §5.4 |
| QA-4 | **LLM-as-judge groundedness rubric** (promptfoo, ≥ 4/5) on memo quality; memo wording anchored to a reference memo via few-shot for consistency (not claimed bit-identical). Applies to Gemini + Claude (FR-PROV-GATE-2). | Q9 (D), Brief §6 |
| QA-5 | A test MUST assert the LLM cannot change a recommendation (enforces CON-BR2). | BR2 |
| QA-6 | TDD enforced; no production code without tests. | Brief §8, §11.7 |

---

## 10. Security Scope (Security Guardrails — Enabled, Scoped)

Security Guardrails extension = **Enabled**, enforced as blocking, **scoped** to
the five controls below (Q13). Each ties to a concrete failure mode or segregation
requirement; scoping keeps "enforce all" bounded.

| ID | Control | Ties to | Source |
|---|---|---|---|
| SEC-1 | **Prompt-injection defense** — sanitize/sandbox text from uploaded documents. | Failure mode #4 | Q13, Brief §10 |
| SEC-2 | **Input validation** — Pydantic gates reject malformed input before agent entry. | Failure mode #5 | Q13, Brief §10 |
| SEC-3 | **Secrets management** — no hardcoded keys; provider keys via env/secrets. | Free-tier/API config | Q13 |
| SEC-4 | **Read-only DB access for the audit role** — enforces PER-2 segregation. | Q5 auditor segregation | Q13 |
| SEC-5 | **Audit logging** — decision history + audit trail underpin the auditability selling point. | Auditability deliverable | Q13 |

---

## 11. Acceptance Criteria

| ID | Criterion | Target | Test Method | Source |
|---|---|---|---|---|
| AC-1 | Decision reproducibility | 100% | Calibration × 10 runs | Brief §6, Q9 |
| AC-2 | Unexplained recommendations | 0 | Eval groundedness check | Brief §6 |
| AC-3 | Bias-swap delta | 0 (blocking) | Automated bias-swap suite | Brief §6, BR1 |
| AC-4 | Rule coverage | 100% of rules | Coverage report | Brief §6 |
| AC-5 | **Code coverage** | **≥ 90%** (binding; 95% aspirational) | pytest-cov | Brief §6 (resolves §6/§9 90/95 conflict, 2026-06-17) |
| AC-6 | LLM-as-judge score | ≥ 4/5 (Gemini + Claude only; **Ollama exempt** as showcase-only, per QA-4 / FR-PROV-GATE-2) | promptfoo rubric | Brief §6, Q9 |
| AC-7 | Observability | 100% of agent steps traced | Langfuse trace audit | Brief §6, Q10 |

---

## 12. Deferred Decisions Register (re-raise at the stated GUIDE stage — do NOT decide now)

| Item | Re-raise at | Source |
|---|---|---|
| ~~Phase boundaries / whether a Phase 3 exists~~ — **RESOLVED 2026-06-18** | Decided (per project direction): **Phase 1 + Phase 2 built this engagement, every story phase-tagged (1/2); Phase 3 = documented future release** (OOS-2..6 + production deploy). Validation deploy = Phase 2; production deploy = Phase 3. No longer deferred. | Deferred Register, OOS-1 |
| ~~REFER human-approval-gate semantics~~ — **RESOLVED 2026-06-18** | Decided (per project direction): **Phase 1/2 = underwriter resolves every recommendation incl. REFER at the gate via Accept/Decline with mandatory reason; REFER→senior-underwriter escalation routing = Phase 3** (see OOS-2). No longer deferred. | OOS-2, FR-UI-2, CON-BR4 |
| SSO/OAuth timing | Phasing now finalized → SSO/OAuth is **Phase 3** (OOS-3); detailed timing within Phase 3 deferred to that release | Deferred Register, Q6 |
| Synthetic-corpus generation timing relative to phases | Appropriate later stage | Deferred Register, Q8 |
| Senior-underwriter escalation persona (Q5-B) | If/when escalation workflow enters scope | Deferred Register, Q5 |
| ~~Occupation: legitimate risk factor vs. protected bias proxy~~ — **RESOLVED 2026-06-17** | Decided: legitimate underwriting input + proxy guard, mirroring income (per proxy-check instruction). No longer deferred. | FR-RULES-2, CON-BR1 |

*Per project direction: do not over-fixate decisions now. Where a decision is
clearer at a later GUIDE stage (especially User Stories), defer and re-raise it
there rather than locking it prematurely.*

---

## 13. Extension Compliance Summary (Security Guardrails — Enabled, Scoped)

| Rule area | Status at this stage | Rationale |
|---|---|---|
| Prompt-injection defense | Compliant (captured as SEC-1) | Requirement recorded; design enforced in BUILD |
| Input validation | Compliant (SEC-2) | Requirement recorded |
| Secrets management | Compliant (SEC-3) | Requirement recorded |
| Read-only DB for audit role | Compliant (SEC-4) | Requirement recorded; ties to PER-2 |
| Audit logging | Compliant (SEC-5) | Requirement recorded |
| Crypto / network hardening / threat modeling | N/A at Requirements | Implementation-stage concerns; revisit at NFR/Infra Design |

No blocking findings at this stage.

---

*End of requirements. Awaiting approval at the Requirements approval gate before
proceeding to the next GUIDE stage.*
