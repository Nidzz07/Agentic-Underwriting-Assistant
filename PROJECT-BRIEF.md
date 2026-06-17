# PROJECT BRIEF: Agentic Underwriting Assistant
**Classification**: BFSI AI Engineering Project  
**Version**: 1.0  
**Date**: 2026-06-14

---

## 1. EXECUTIVE SUMMARY

Build a production-grade agentic underwriting assistant that ingests loan 
and insurance applications with supporting documents, evaluates them against 
a versioned deterministic rulebook, compares applicant profiles against a 
synthetic corpus using ML-based outlier detection, and produces an 
audit-ready decision memo for human underwriter review.

The system is modeled on Canara HSBC Life Insurance's OmniGen AI (launched 
November 2024 on AWS Bedrock), which reduced underwriting turnaround from 
30 minutes to near-instant at 20x lower cost ($2.00 → $0.20/case) with 
100% auditability. This build recreates that capability using open-source 
frameworks and a runtime-selectable LLM provider (Gemini primary, Claude 
secondary, Ollama showcase) behind a provider-abstraction layer.

Underwriting is the highest-stakes decision in BFSI — which is precisely 
why explainability, consistency, and human oversight take precedence over 
raw automation speed.

---

## 2. BUSINESS CONTEXT & MOTIVATION

### Problem Statement
Traditional underwriting suffers from:
- Manual, time-consuming document review (20-30 min per case)
- Inconsistent decisions across underwriters
- No structured audit trail for regulatory review
- Implicit bias in subjective assessments
- Inability to replay past decisions against updated rules

### Solution Approach
An agentic AI co-pilot that:
- Automates structured data extraction from documents
- Applies deterministic, versioned rules with full traceability
- Flags statistical anomalies with ML-based explanation
- Drafts human-readable decision memos with rule citations
- Enforces human-in-the-loop as a hard architectural constraint
- Never presents itself as the final decision-maker

### Enterprise Proof Point
Canara HSBC OmniGen AI demonstrates this pattern works at production scale.
This project is an open-source, portfolio-grade implementation of the same 
architecture using a provider-abstracted LLM (Gemini primary / Claude secondary 
/ Ollama showcase), LangGraph, FastAPI, and React.

---

## 3. SYSTEM ARCHITECTURE — 5 CORE COMPONENTS

### Component 1: Application Intake Agent
- Parse application form + supporting documents (salary slips, bank 
  statements, medical questionnaire) into a validated structured JSON profile
- Technologies: pdfplumber, Pydantic v2 structured extraction
- Output: ApplicantProfile schema with completeness validation

### Component 2: Deterministic Rulebook Engine
- 25-40 underwriting rules codified in versioned YAML
- Rule categories: income multiples, age bands (18-65), BMI/health flags, 
  debt-to-income ratio (≤40%), document completeness checks, 
  employment type flags, IRDAI 2024 compliance rules
- Pure Python evaluation — zero LLM involvement in this path
- Output: per-rule pass/fail report with rule version stamp
- Versioning: every past decision replayable against the exact rulebook 
  version active at decision time

### Component 3: Outlier Detection Agent
- Synthetic corpus of 300+ applicant profiles 
  (approve/refer/decline distribution)
- Statistical comparison using z-scores + IsolationForest
- SHAP-style feature importance for explainability
- Output: outlier score, flagged features, human-readable explanation
- Technologies: scikit-learn, SHAP, numpy, pandas

### Component 4: Decision-Memo Agent (LLM)
- Orchestrated via LangGraph state machine
- Provider-abstracted LLM, runtime-selectable via config/settings:
  PRIMARY = Gemini (less expensive); SECONDARY = Claude Opus 4.8 (tested
  fallback); Ollama = showcase-only (wired, not tested against acceptance
  criteria). temperature=0 on all production calls for deterministic memo output
- Extended thinking / reasoning enabled for complex/borderline cases where the
  active provider supports it (Claude extended thinking; Gemini thinking budget)
- Structured XML output → Pydantic validation
- Memo must cite: every triggered rule by ID, confidence level 
  (Low/Medium/High), missing documents list, outlier flags
- Hard constraint: system prompt enforces advisory-only language
- MCP servers expose rulebook and decisions DB as tools
- Output: structured DecisionMemo with recommendation 
  (APPROVE / REFER / DECLINE-RECOMMEND)

### Component 5: Underwriter UI
- React + Tailwind CSS
- Features: application queue, memo view with rule citations, 
  override with mandatory reason field, full decision history
- Human approval gate: no recommendation becomes a decision 
  without explicit underwriter action
- All UI elements have data-testid attributes for automation

---

## 4. DATA REQUIREMENTS

### Synthetic Dataset: 300+ Applicant Profiles
Distribution:
- ~40% APPROVE (clean financials, complete docs, within all rule bands)
- ~35% REFER (borderline values, incomplete docs, self-employed edge cases)
- ~25% DECLINE-RECOMMEND (multiple rule failures, high DTI, health flags)

Mandatory edge cases:
- Thin-file applicants (minimal credit/document history)
- Self-employed with irregular income patterns
- Values exactly at rule thresholds (boundary testing)
- Missing single documents (partial completeness)
- Age boundary cases (exactly 18, exactly 65)
- BMI boundary cases (exactly at 25, 30 thresholds)

Generation: Faker + Claude LLM for realistic document text
Format: JSON profiles + mock PDF documents

---

## 5. QUALITY & SAFETY REQUIREMENTS

### 5.1 Reproducibility
- Identical input → identical output, 100% of the time
- Enforced via: temperature=0, deterministic rules engine, 
  seeded random for outlier model
- Validation: calibration test suite (same input × 10 runs)

### 5.2 Bias Invariance
- Swap applicant name / gender / city across identical financials
- Decision recommendation must not change
- Automated bias-swap test suite with delta report
- Any delta found = blocking bug, not a warning

### 5.3 Rulebook Versioning
- Every decision record stores: rulebook_version, rule_results, 
  timestamp, model_version, memo_hash
- Full replay capability: given any past decision ID, 
  reproduce it against the original rulebook version

### 5.4 Rule Coverage
- Every rule in the rulebook must be exercised by ≥1 test case
- Rule coverage report generated as part of eval suite
- Uncovered rules = blocking test failure

### 5.5 Explainability
- Zero unexplained recommendations — every output cites evidence
- Every outlier flag includes SHAP feature explanation
- Every rule result includes the exact value that triggered it

### 5.6 Human-in-the-Loop
- Hard architectural constraint — not a UI preference
- No decision can be finalised without underwriter action
- System language: always "recommendation", never "decision"

---

## 6. ACCEPTANCE CRITERIA

| Criterion | Target | Test Method |
|---|---|---|
| Decision reproducibility | 100% | Calibration test × 10 runs |
| Unexplained recommendations | 0 | Eval suite groundedness check |
| Bias-swap delta | 0 | Automated bias-swap suite |
| Rule coverage | 100% of rules | Coverage report |
| Code coverage | ≥90% | pytest-cov |
| LLM-as-judge score | ≥4/5 | promptfoo rubric |
| Observability | 100% of agent steps traced | Langfuse trace audit |

---

## 7. DELIVERABLES

1. **Working deployed demo** — Render (backend) + Vercel (frontend)
2. **Eval suite** — labeled test set, accuracy/groundedness metrics, 
   LLM-as-judge rubric via promptfoo
3. **Observability** — Langfuse traces for every agent/tool step + 
   Prometheus metrics + Grafana dashboards
4. **README** — architecture diagram, local setup guide, 
   environment configuration
5. **Case study** — 2-page document mapping this build to the 
   Canara HSBC OmniGen AI enterprise proof point
6. **Failure mode analysis** — 5 documented failure modes with 
   mitigations (hallucination, retrieval miss, tool-call error, 
   prompt injection, malformed edge-case input)
7. **Bias-swap test report** — automated, reproducible, included 
   in CI pipeline
8. **Rule coverage report** — every rule exercised, included in 
   eval suite

---

## 8. TECHNICAL CONSTRAINTS

- Synthetic/mock data only — zero real PII at any stage
- Open-source frameworks and free-tier APIs only
- Human-in-the-loop approval gate for every consequential decision
- No LLM in the deterministic rules evaluation path
- All past decisions must be replayable against original rulebook version
- Temperature = 0 enforced on all production LLM calls

---

## 9. TECH STACK

| Layer | Technology | Justification |
|---|---|---|
| LLM (primary) | Gemini, temp=0, thinking on borderline cases | Less expensive provider; deterministic memo, audit-grade |
| LLM (secondary) | Claude Opus 4.8, temp=0, extended thinking | Tested fallback; best reasoning, audit-grade |
| LLM (showcase) | Ollama (local) | Offline/local capability; wired, NOT tested against acceptance criteria |
| Model switch | Runtime-selectable via config/settings behind provider-abstraction layer (Gemini / Claude / Ollama; OpenAI wireable) | Vendor independence proof |

> **Provider precedence (supersedes v1.0 Claude-primary assumption, set 2026-06-17 at Requirements Analysis Q4):**
> PRIMARY = Gemini (less expensive); SECONDARY = Claude Opus 4.8 (tested fallback);
> SHOWCASE = Ollama (wired, not tested against acceptance criteria). Runtime-selectable
> via config/settings behind the existing provider-abstraction layer. `temperature=0`
> remains enforced on all production calls regardless of provider.
| Rules engine | YAML + Python | Zero LLM, fully deterministic, versionable |
| Doc parsing | pdfplumber + Pydantic v2 | Typed extraction, validation |
| Outlier detection | scikit-learn IsolationForest + z-scores | Proven ML, interpretable |
| Explainability | SHAP | Feature-level explanation |
| Orchestration | LangGraph | State machine, conditional branching |
| Backend | FastAPI + PostgreSQL | Async, typed, production-ready |
| Frontend | React + Tailwind CSS | Underwriter queue + memo view |
| Synthetic data | Faker + Claude LLM | Realistic at scale |
| Evals | pytest + promptfoo + regression suites | LLM eval + invariance testing |
| Observability (LLM) | Langfuse | Per-step agent traces |
| Observability (app) | Prometheus + Grafana | Metrics + dashboards |
| Deployment | Render + Vercel | Free tier, CI/CD ready |
| Testing | TDD, pytest-cov ≥95% enforced | Quality gate from day 1 |

### Provider Capabilities (exercised on Claude secondary; mapped to equivalents on Gemini primary)
- **Tool use** with structured XML outputs → Pydantic validation
- **MCP servers** exposing rulebook engine and decisions DB as tools
- **Extended thinking** for edge-case memo drafting and complex 
  borderline applications (Claude extended thinking; Gemini thinking budget;
  Ollama showcase may not support this)

---

## 10. FAILURE MODES TO DOCUMENT (First-Class Deliverable)

| # | Failure Mode | Where It Occurs | Mitigation Strategy |
|---|---|---|---|
| 1 | Hallucination | Memo agent invents rule not in rulebook | Rule citation validation against YAML |
| 2 | Retrieval miss | Wrong document parsed for applicant | Document ID binding + hash verification |
| 3 | Tool-call error | LangGraph tool call fails mid-flow | Retry with exponential backoff + dead letter |
| 4 | Prompt injection | Malicious text in uploaded document | Input sanitization + sandboxed parsing |
| 5 | Malformed input | Broken PDF, missing required fields | Pydantic validation gates before agent entry |

---

## 11. ARCHITECTURE PRINCIPLES

1. **Deterministic core** — rules engine is pure Python, no LLM
2. **Advisory only** — system cannot finalise any decision
3. **Full auditability** — every field, rule, and score is logged
4. **Reproducible** — same input always produces same output
5. **Bias-free by design** — rules operate on financials only, 
   never on demographic identifiers
6. **Vendor-agnostic** — model switch supported at config level
7. **Test-first** — TDD enforced, no production code without tests