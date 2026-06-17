---
name: underwriting-rules
description: >-
  Domain context and guardrails for the Agentic Underwriting Assistant (BFSI
  loan/insurance underwriting). Use this skill WHENEVER work touches the
  underwriting rulebook, rule evaluation, decision memos, applicant profile
  evaluation, or ML outlier/anomaly detection on applicants — even if the user
  doesn't name the skill explicitly. Triggers include: adding/editing rules in
  the YAML rulebook, the deterministic rules engine, scoring or evaluating an
  applicant, drafting or reviewing a decision memo, the APPROVE/REFER/
  DECLINE-RECOMMEND recommendation, outlier detection, IsolationForest/z-score/
  SHAP work on applicants, the underwriter approval gate, bias-swap or
  reproducibility tests, or rulebook versioning/replay. Encodes the project's
  hard constraints so generated code and copy never violate the advisory-only,
  human-in-the-loop, deterministic-core architecture.
---

# Underwriting Rules — Domain Context & Guardrails

This skill carries the domain knowledge and non-negotiable constraints for the
**Agentic Underwriting Assistant**. The system ingests loan/insurance
applications, evaluates them against a versioned deterministic rulebook,
compares applicants against a synthetic corpus via ML outlier detection, and
drafts an audit-ready decision memo for a **human underwriter** to act on.

Underwriting is the highest-stakes decision in BFSI. Explainability,
consistency, and human oversight always take precedence over automation speed.
When you touch any part of this system, hold the constraints below as
architectural invariants, not preferences.

## Hard constraints (never violate)

These are architectural invariants. Code, prompts, schemas, and UI copy that
break any of them are defects, not stylistic choices.

1. **Advisory only.** The system produces *recommendations*, never *decisions*.
   No code path, memo, API response, or UI string may finalise an outcome on
   its own. In all language — system prompts, memo text, field names, button
   labels, log messages — use "recommendation", never "decision". Reserve the
   word "decision" for the record of what the **human underwriter** chose.

2. **Human-in-the-loop approval gate.** No recommendation becomes a decision
   without explicit underwriter action. This is structural: there must be a
   gate the human passes through, and overrides require a mandatory reason.
   Never auto-approve, auto-finalise, or design a flow that lets a
   recommendation flow straight to a committed outcome.

3. **No LLM in the deterministic rules path.** The rulebook engine is pure
   Python evaluating versioned YAML rules. Do not call an LLM, embed an LLM
   client, or introduce any non-deterministic step inside rule evaluation. The
   LLM only drafts the memo *after* deterministic results exist.

4. **Temperature = 0 on all production LLM calls.** Every production Claude
   call uses `temperature=0` for reproducibility. If you write or review an LLM
   call and temperature is unset or non-zero, that is a bug. (Default model:
   Claude Opus 4.8, extended thinking for borderline cases.)

5. **Reproducibility.** Identical input must produce identical output, 100% of
   the time — enforced by temperature=0, the deterministic engine, and seeded
   randomness in the outlier model. Never introduce unseeded randomness,
   wall-clock-dependent logic, or dict-ordering assumptions into evaluation.

6. **Bias-free by design.** Rules and the outlier model operate on financial/
   medical/lifestyle facts only — never on name, gender, city, or other
   demographic identifiers. Swapping those fields across identical financials
   must not change the recommendation. Any delta is a blocking bug.

7. **Rulebook versioning & replay.** Every decision record stores
   `rulebook_version`, `rule_results`, `timestamp`, `model_version`, and
   `memo_hash`. Any past decision must be replayable against the exact rulebook
   version active when it was made. Never mutate a published rule version
   in place — add a new version.

8. **Full explainability.** Zero unexplained recommendations. Every rule result
   cites the exact value that triggered it; every outlier flag includes a SHAP
   feature explanation; the memo cites every triggered rule by ID.

When a request would require breaking one of these, do not silently comply.
Flag the conflict, explain which constraint it violates, and offer a compliant
alternative.

## Decision outcomes

The recommendation is always exactly one of three values. Treat this as a fixed
enum across schemas, rules, memos, and the UI:

- **APPROVE** — clean profile, complete docs, within all rule bands.
- **REFER** — borderline values, incomplete docs, or edge cases (e.g.
  self-employed with irregular income) that need underwriter judgment.
- **DECLINE-RECOMMEND** — multiple rule failures, high DTI, or health flags.
  Note the `-RECOMMEND` suffix: even a decline is advisory. Never emit a bare
  "DECLINE" that reads as a final verdict.

## Rule categories

Rules live in versioned YAML and are evaluated by pure Python. The rulebook
holds roughly 25–40 rules across three domains. Each rule, when it fires, must
report the exact applicant value that triggered it.

**Financial**
- Income multiple — requested cover/loan vs. verifiable income.
- Debt-to-income (DTI) ratio — ceiling at ≤ 40%.
- Document completeness — salary slips, bank statements present and parseable.
- Employment-type flags — e.g. self-employed / irregular income.
- IRDAI 2024 compliance rules.

**Medical**
- BMI bands — boundary thresholds at 25 and 30.
- Age bands — eligible window 18–65; boundary cases at exactly 18 and 65.
- Health flags from the medical questionnaire.

**Lifestyle**
- Smoking status.
- Occupation risk classification.

### Boundary behaviour matters

Values *exactly at* a threshold are first-class test cases (age = 18, age = 65,
BMI = 25, BMI = 30, DTI = 40%). When you write or change a rule, state the
comparison explicitly (`<=` vs `<`) and make sure a boundary value lands on the
intended side. Thin-file applicants and single-missing-document cases should
route to REFER, not a hard DECLINE.

## How the pieces fit (so you place code correctly)

```text
Intake (Pydantic profile)
        │
        ▼
Deterministic rulebook engine  ── pure Python, NO LLM ──►  per-rule pass/fail
        │                                                  + rulebook_version
        ▼
Outlier detection (IsolationForest + z-scores + SHAP, seeded)
        │
        ▼
Decision-memo agent (Claude, temperature=0)  ──►  DecisionMemo
        │      cites rule IDs, confidence (Low/Med/High), missing docs, flags
        ▼
Underwriter UI  ──►  human approval gate  ──►  committed DECISION (human-made)
```

The LLM enters only at the memo step, downstream of deterministic results. The
human gate is the only place a recommendation turns into a decision.

## When generating or reviewing code

- Put rule logic in the YAML rulebook + Python engine; never reach for the LLM
  there.
- Memo agent calls: assert `temperature=0` and structured (XML→Pydantic)
  output; validate cited rule IDs against the YAML so the model can't invent a
  rule (hallucination guard).
- Persist the full audit tuple (`rulebook_version`, `rule_results`,
  `timestamp`, `model_version`, `memo_hash`) on every recommendation.
- Keep demographic identifiers out of any feature vector, rule input, or prompt
  that influences the outcome.
- Favour seeded, deterministic constructs; the bias-swap and calibration
  (same-input × 10) suites must stay green.
- Use "recommendation" in all user-facing and internal naming; reserve
  "decision" for the human's committed action.

If you're unsure whether something belongs in the deterministic path or the LLM
path, the test is simple: anything that affects the pass/fail outcome is
deterministic Python; the LLM only explains and drafts.
