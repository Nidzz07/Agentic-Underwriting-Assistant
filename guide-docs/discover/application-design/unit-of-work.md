# Unit of Work — Agentic Underwriting Assistant

**Phase / Stage**: DISCOVER → Units Generation (Part 2 — Generation)
**Project Type**: Greenfield
**Date**: 2026-07-02
**Status**: Generated at the Units Generation completion gate — awaiting **Request Changes / Approve & Continue → BUILD**.

This artifact defines the **units of work** (definitions + responsibilities), the
**greenfield code-organization strategy** (Q5=A), the **explicit Phase tag** on every unit,
and the **carried-forward depth annotation**. It is generated from the authoritative
**§A.5 resolved 23-unit list** in `unit-of-work-plan.md` (Q1..Q6 = A, F1–F4 applied), and is
consistent with the five Application Design artifacts (`components.md`, `component-methods.md`,
`services.md`, `component-dependency.md`, `application-design.md`).

- **23 units** — **17 Phase 1**, **6 Phase 2**.
- **All 40 stories assigned exactly once** (proof in `unit-of-work-story-map.md`).
- **One unit — `database` — is story-less by design** (shared infra). `provider-abstraction`
  is a **module of `memo-agent-core`**, not a unit.
- **Binding invariants are single-sourced** (see §5): no invariant is split across two
  co-equal units in a way that lets two definitions drift.

---

## 1. How to read this document

- Each unit is a coherent story cluster bound to one component/service, sized for independent
  **design → code → test**. High-cohesion components are **grouped units with modules**
  (Q3=A); genuinely independent concerns are their own units.
- **Phase** is inherited from a unit's constituent stories (`stories.md §8`). The BUILD loop
  runs **all Phase 1 units to completion before any Phase 2 unit** (`execution-plan.md §4.1`).
- **Depth annotation** (per-unit "lighter" vs comprehensive) is a **revisitable recommendation**
  that bites at each BUILD per-unit design stage — **not** a locked floor (§4).
- A **module** carrying no story of its own is normal (e.g. `provider-abstraction`,
  `rulebook-yaml`); only a whole **unit** with no story is called out as "story-less".

---

## 2. Greenfield code-organization strategy (Q5=A — single monorepo)

**One repository, one CI.** `backend/` (Render) + `frontend/` (Vercel) + `rulebook/`
(versioned YAML) + `corpus/` (generated data + manifest) + `infra/` (deploy config).
**Tests are co-located per package** (Q5=A) — each unit's tests live beside its code; the
`quality-gates` unit *is* the cross-cutting eval/CI suite. This keeps the deterministic core
and the UI versioned together so any past decision replays against the exact code + rulebook
version (CON-AUDIT-1).

```
underwriting-project/
├── backend/                         # FastAPI + Python package (Render)
│   ├── app/                         # FastAPI orchestrator = composition root (see note)
│   │   ├── main.py                  #   request routing: C5 -> API -> C1/C2/(C3) -> C4; commit -> DCS
│   │   └── tests/
│   ├── intake/                      # UNIT: intake  (C1; parser + profile-schema + validation-gate)
│   │   ├── parser.py  schema.py  validation_gate.py
│   │   ├── sanitizer/               # UNIT: document-sanitizer (C1/SEC-1) — separate unit, mid-pipeline
│   │   │   ├── sanitizer.py
│   │   │   └── tests/
│   │   └── tests/
│   ├── rules/                       # UNIT: rules-engine (C2; modules: yaml-loader, result-report, versioning/replay)
│   │   ├── engine.py  result_report.py  version_store.py
│   │   └── tests/
│   ├── outlier/                     # UNIT: outlier-model (C3, P2; modules: model, shap, feature_vector)
│   │   ├── model.py  shap_explainer.py  feature_vector.py
│   │   └── tests/
│   ├── memo/                        # UNIT: memo-agent-core (C4, P1)
│   │   ├── orchestrator.py          #   LangGraph memo sub-flow
│   │   ├── schema.py                #   XML -> Pydantic
│   │   ├── citation_validator.py    #   hallucination guard
│   │   ├── providers/               #   MODULE: provider-abstraction (Gemini primary) — not a unit
│   │   ├── extensions/              # UNIT: memo-extensions (C4, P2): mcp-tools + borderline-router + secondary/showcase adapters
│   │   │   ├── mcp_tools.py  borderline_router.py  provider_secondary.py  provider_showcase.py
│   │   │   └── tests/
│   │   └── tests/
│   ├── services/                    # EPIC-6 services layer
│   │   ├── auth_rbac.py             # UNIT: auth-rbac (canonical role model + backend enforcement)
│   │   ├── audit_store.py           # UNIT: audit-store (DecisionCommitService + AuditService + ReplayService)
│   │   ├── corpus_generator.py      # UNIT: corpus-generator (build-time, manifest-frozen)
│   │   ├── secrets_config.py        # UNIT: secrets-config
│   │   └── tests/
│   ├── db/                          # UNIT: database (STORY-LESS shared infra: schema + migrations)
│   │   ├── models.py  migrations/
│   │   └── tests/
│   ├── quality/                     # UNIT: quality-gates (bias-swap + reproducibility + rule-coverage + coverage-gate)
│   │   ├── bias_swap_suite.py  reproducibility_suite.py  rule_coverage_report.py  coverage_gate.py
│   │   └── tests/
│   ├── observability/               # UNIT: observability (P2; Langfuse + Prometheus/Grafana)
│   ├── judge/                       # UNIT: llm-judge (P2; promptfoo groundedness)
│   └── cli/                         # UNIT: admin-cli (rulebook-version + user/config management)
├── frontend/                        # React + Tailwind (Vercel) — NO TypeScript requirement (FR-UI-5)
│   └── src/
│       ├── shell/                   # UNIT: ui-shell (ui-common): advisory-copy + data-testid convention
│       ├── auth/                    #   RBAC UI facet (consumes auth-rbac; realization, not a unit)
│       ├── queue/                   # UNIT: ui-queue
│       ├── memoView/                # UNIT: ui-memo-view
│       ├── approvalGate/            # UNIT: ui-approval-gate  (invariant-bearing)
│       ├── overrideForm/            # UNIT: ui-override-form  (invariant-bearing)
│       ├── history/                 # UNIT: ui-history
│       └── outlierView/             # UNIT: ui-outlier-view (P2; conforms to ui-shell contract)
├── rulebook/                        # versioned YAML rulebook (immutable published versions)
├── corpus/                          # generated synthetic profiles + manifest (frozen by corpus-generator)
└── infra/                           # UNIT: deploy-config (P2; Render + Vercel free-tier)
```

> **FastAPI orchestrator (composition root, not a separate unit).** Per Q1=B / `services.md`,
> FastAPI owns the deterministic request path (intake → rules → outlier) and routes the commit
> to `DecisionCommitService`. It is the **in-process wiring across backend units** — the
> monorepo composition root in `backend/app/` — not a 24th unit of work. Its behaviour is
> covered by the units it composes and by integration tests in Build & Test.

---

## 3. Unit definitions

### 3.1 Phase 1 units (17)

#### U1 — `intake`  *(C1; Phase 1)*
- **Purpose**: Turn an application form + supporting documents into one validated, typed
  `ApplicantProfile`, or reject at the Pydantic gate **before** any agent runs.
- **Modules**: `intake-parser` (pdfplumber), `applicant-profile-schema` (Pydantic v2),
  `intake-validation-gate`.
- **Stories**: US-INTAKE-1, US-INTAKE-2, US-INTAKE-3.
- **Key invariants**: **SEC-2** (validation gate — single source), FR-INTAKE-1..3, DATA-4.
- **Depth**: `applicant-profile-schema` comprehensive (new data model); parser/gate standard.

#### U2 — `document-sanitizer`  *(C1 / SEC-1; Phase 1)*
- **Purpose**: Neutralise prompt-injection text extracted from uploaded documents so hidden
  instructions never reach the memo agent as commands. A **security boundary** worth
  independent ownership + testing (Q3 split-out).
- **Stories**: US-INTAKE-4.
- **Key invariants**: **SEC-1** (injection defense — single source).
- **Depth**: comprehensive (security-critical). **Standalone unit, mid-pipeline stage** —
  see the pinned dependency edge (`unit-of-work-dependency.md §2`, F5a): parse → **sanitize**
  → Pydantic gate.

#### U3 — `rules-engine`  *(C2; Phase 1)*
- **Purpose**: Evaluate an `ApplicantProfile` against a versioned rulebook with **pure Python,
  zero LLM**, and **produce the recommendation** + deterministic `confidence`.
- **Modules**: `rulebook-yaml` (versioned; story-less module), `rule-result-report`,
  `versioning/replay` (immutable published versions).
- **Stories**: US-RULES-1, US-RULES-2, US-RULES-3, US-RULES-4, US-RULES-5.
- **Key invariants**: **CON-BR2** (recommendation originates here, never in the LLM),
  **CON-DET-1** (no unseeded randomness / wall-clock / dict-order), **CON-BR1 enforcement
  facet** (rules operate on **financials only**; occupation/income influence the outcome
  **only** through their sanctioned rule — occupation-risk / affordability — never as a
  demographic proxy; US-RULES-5), FR-RULES-1..6. *(CON-BR1 verification is single-sourced in
  `quality-gates` bias-swap, U13; this is layered enforcement, not co-ownership — see §5.)*
- **Depth**: comprehensive (versioned schema, boundary/comparison correctness, replay).

#### U4 — `memo-agent-core`  *(C4; Phase 1)*
- **Purpose**: Draft an audit-ready, rule-cited memo **after** deterministic results exist —
  prose only, never touching the recommendation.
- **Modules**: `langgraph-orchestrator`, **`provider-abstraction` (Gemini primary — module,
  not a unit)**, `memo-schema` (XML→Pydantic), `rule-citation-validator` (hallucination guard).
- **Stories**: US-MEMO-1, US-MEMO-2, US-MEMO-3, US-MEMO-4.
- **Key invariants**: **CON-BR2** (read-only recommendation; QA-5 assertion), FR-MEMO-1..4,
  FR-PROV-1/3. Cites strictly from the handed `RuleResultReport`; MCP is supplementary only
  (that path is Phase 2, in `memo-extensions`).
- **Depth**: comprehensive (LangGraph state, structured output, determinism).

#### U5 — `ui-queue`  *(C5; Phase 1)* — application queue. **US-UI-1.** FR-UI-1/3, PER-1. *Depth: lighter (display).*
#### U6 — `ui-memo-view`  *(C5; Phase 1)* — memo view with rule citations, confidence, missing-info list. **US-UI-2.** FR-MEMO-3, NFR-EXPLAIN-1. *Depth: lighter (display).*
#### U7 — `ui-approval-gate`  *(C5; Phase 1)* — the human approval gate UI facet. **US-UI-4.** FR-UI-2, **CON-BR4** (UI facet; backend enforcement single-sourced in `audit-store`). *Depth: **comprehensive** (invariant-bearing).*
#### U8 — `ui-override-form`  *(C5; Phase 1)* — override-with-mandatory-reason UI facet. **US-UI-5.** FR-UI-4, **CON-BR4** (UI facet). *Depth: **comprehensive** (invariant-bearing).*
#### U9 — `ui-history`  *(C5; Phase 1)* — decision history browse; links to audit tuple. **US-UI-6.** CON-AUDIT-1 (read surface). *Depth: lighter (display).*

#### U10 — `ui-shell` (`ui-common`)  *(C5; Phase 1)*  **[added per F1]**
- **Purpose**: Own the **UI-wide invariant** — advisory-only "recommendation" copy
  conventions + the `data-testid` lint/convention — as a **shared contract** every view unit
  conforms to (incl. the Phase-2 `ui-outlier-view`). Prevents any single view unit from owning
  app-wide conventions.
- **Stories**: US-UI-7.
- **Key invariants**: **CON-BR4 (language facet)** / advisory-only vocabulary (single source
  of the *copy* convention), FR-UI-3/4/5. React + Tailwind only (no TypeScript).
- **Depth**: standard (convention + lint), but the advisory-only rule is invariant-bearing.

#### U11 — `auth-rbac`  *(EPIC-6; Phase 1)*
- **Purpose**: The **canonical** role/permission model + **backend enforcement at both points**
  (API layer **and** the `DecisionCommitService` re-check). The UI-side enforcement is a thin
  consuming facet folded into the C5 units (Q1=A — not a second unit).
- **Stories**: US-PLAT-1.
- **Key invariants**: **SEC-4** (underwriter acts / auditor read-only — single source),
  PER-4/5; OIDC-ready seam (SSO = Phase 3 / OOS-3).
- **Depth**: comprehensive (segregation of duties, defense-in-depth).

#### U12 — `audit-store`  *(EPIC-6; Phase 1)*
- **Purpose**: The **decision-write + audit + replay backend boundary**. Owns
  `DecisionCommitService` (rejects writes lacking `underwriter_id`+`reason`; re-checks authz),
  `AuditService` (persist the CON-AUDIT-1 **6-tuple**), and `ReplayService` (re-evaluate any
  decision against its **original** `rulebook_version`, match/mismatch branch).
- **Stories**: US-PLAT-2 (read-only audit-trail surface, F2), US-PLAT-8 (audit tuple + replay, F3).
- **Naming note (not passive storage)**: despite the name, `audit-store` **is the
  decision-commit-and-audit backend boundary** — the **`DecisionCommitService` (CON-BR4
  write-gate) lives here**, single-sourced alongside `AuditService` / `ReplayService`. The
  CON-BR4 ↔ CON-AUDIT-1 coupling (a commit and its audit-tuple persistence are one atomic
  write path) is exactly why they stay in one unit; the name reads "audit" but the unit owns
  the write-gate, not just retention.
- **Key invariants**: **CON-AUDIT-1** (6-tuple + replay — single source), **CON-BR4**
  (decision-write enforcement — **single backend source**; UI facets in U7/U8 consume it),
  SEC-5. Depends on `database` (U15).
- **Depth**: comprehensive (audit tuple, replay-as-detection).

#### U13 — `quality-gates`  *(EPIC-6; Phase 1)*  **[grouped per Q4=A]**
- **Purpose**: The four blocking gates as one CI/pytest harness.
- **Modules**: `bias-swap-suite` (delta=0, blocking), `reproducibility-suite` (100%, ×10),
  `rule-coverage-report` (100% of rules), `coverage-gate` (≥90%, binding).
- **Stories**: US-PLAT-3, US-PLAT-4, US-PLAT-5, US-PLAT-6.
- **Key invariants**: **single verification authority** for CON-BR1 (bias-swap), CON-BR2/AC-1
  (reproducibility), QA-3 (rule coverage), AC-5 (code coverage). *Enforcement of CON-BR1/CON-DET-1
  lives in `rules-engine`/`outlier-model`; verification is single-sourced here.*
- **Depth**: comprehensive (blocking gates at full strength).

#### U14 — `corpus-generator`  *(EPIC-6; Phase 1)* — **build-time**, seeded, versioned, skew-audited synthetic corpus (300+, 40/35/25), frozen by a manifest. **US-PLAT-7.** **CON-BR3** (single source), DATA-1/2/3. *Depth: standard→comprehensive (skew audit).*

#### U15 — `database`  *(EPIC-6; Phase 1)*  **[STORY-LESS shared infra]**
- **Purpose**: Shared PostgreSQL schema + migrations depended on by `audit-store` and others
  (no SQLite — DATA-5). **Story-less by design**: exercised via US-PLAT-8 (owned by
  `audit-store`); provides the substrate, does not own a story.
- **Key invariants**: DATA-5 (PostgreSQL). *Depth: comprehensive at Infrastructure Design.*

#### U16 — `secrets-config`  *(EPIC-6; Phase 1)* — provider/service keys via env/secrets; build fails on hardcoded secret. **US-PLAT-12.** **SEC-3** (single source). *Depth: lighter (single control).*

#### U17 — `admin-cli`  *(EPIC-6; Phase 1)* — out-of-band rulebook-version + user/role/provider-config management (no admin UI). **US-ADMIN-1, US-ADMIN-2.** PER-3/6, FR-RULES-6. *Depth: lighter (CLI wiring).*

### 3.2 Phase 2 units (6)

#### U18 — `outlier-model`  *(C3; Phase 2)*  **[grouped per F4]**
- **Purpose**: Compare an applicant against the seeded corpus and explain anomalies, **without**
  demographic identifiers.
- **Modules**: `outlier-model` (IsolationForest + z-scores, seeded), `shap-explainer`,
  `feature-vector` (demographic-excluded).
- **Stories**: US-OUT-1, US-OUT-2, US-OUT-3.
- **Key invariants**: **CON-BR1** (no demographic identifiers in the feature vector —
  enforcement source; verified by `quality-gates` bias-swap), CON-DET-1 (seeded), FR-OUT-1..3.
- **Depth**: comprehensive (feature vector, seeded scoring, SHAP).

#### U19 — `memo-extensions`  *(C4; Phase 2)*  **[grouped per F4]**
- **Purpose**: Extend `memo-agent-core` with grounding + routing + provider breadth.
- **Modules**: `mcp-tools` (two read-only servers — supplementary only), `borderline-router`
  (deterministic routing to extended thinking), **secondary (Claude) / showcase (Ollama)
  provider adapters** that **extend the `provider-abstraction` module** of `memo-agent-core`
  (module boundary named, **not** a separate provider unit).
- **Stories**: US-MEMO-5, US-MEMO-6, US-MEMO-7.
- **Key invariants**: FR-MEMO-5/6/7, FR-PROV-2/5, FR-PROV-GATE-2; MCP retrieval-miss guard
  (cite only from handed report). `temperature=0` holds for all three providers.
- **Depth**: comprehensive (MCP boundary, provider adapters).

#### U20 — `ui-outlier-view`  *(C5; Phase 2)* — outlier flags + SHAP in the memo view; **conforms to the `ui-shell` contract** (U10). **US-UI-3.** FR-OUT-2. *Depth: lighter (display); no write/commit control → no RBAC facet.*
#### U21 — `observability`  *(EPIC-6; Phase 2)* — Langfuse traces (100% of steps) + Prometheus/Grafana (~5 metrics). **US-PLAT-9.** NFR-OBS-1/2, AC-7. *Depth: comprehensive at Infrastructure Design (wiring-heavy).*
#### U22 — `llm-judge`  *(EPIC-6; Phase 2)* — promptfoo groundedness rubric ≥4/5 (Gemini+Claude; Ollama exempt). **US-PLAT-10.** QA-4, AC-2/6. *Depth: standard.*
#### U23 — `deploy-config`  *(EPIC-6; Phase 2)* — **validation** deploy on Render + Vercel, free-tier (distinct from Phase-3 production). **US-PLAT-11.** NFR-DEPLOY-1. *Depth: comprehensive at Infrastructure Design.*

---

## 4. Carried-forward depth annotation (revisitable recommendation — not a locked floor)

The per-unit "lighter" classifications above are **recommendations revisitable at each BUILD
per-unit design stage** — a unit marked *lighter* can be given comprehensive depth when its
design stage is reached, **without amending this artifact or `execution-plan.md`**. The
**invariant-bearing UI units `ui-approval-gate` (U7) and `ui-override-form` (U8) stay
comprehensive** (FR-UI-2 / CON-BR4 / FR-UI-4), as do the deterministic-core and quality units.
Display-only UI (`ui-queue`, `ui-memo-view`, `ui-history`, `ui-outlier-view`) and pure-wiring
units (`secrets-config`, `admin-cli`, `deploy-config`, `observability`) are the *lighter*
candidates.

---

## 5. Binding-invariant single-sourcing (no invariant split across co-equal units)

| Invariant | Single owning source | Consuming / layered points (not co-owners) |
|---|---|---|
| **SEC-1** injection defense | `document-sanitizer` (U2) | `intake` pipeline invokes it |
| **SEC-2** validation gate | `intake` (U1) | — |
| **SEC-3** secrets | `secrets-config` (U16) | all provider-using units |
| **SEC-4** RBAC segregation | `auth-rbac` (U11) | C5 UI facets, `audit-store` read-only role |
| **SEC-5** audit logging | `audit-store` (U12) | — |
| **CON-BR1** no demographic proxy | **Verification — single owner:** `quality-gates` bias-swap suite (U13) is the **one authority** that asserts the invariant holds (delta = 0, blocking) | **Layered enforcement — NOT co-owners of the definition:** `rules-engine` (U3) operates on financials only, occupation/income only via their sanctioned rule (US-RULES-5); `outlier-model` (U18) uses a demographic-excluded feature vector. **One verification owner + defense-in-depth enforcement ≠ a three-way split** — no unit re-defines the invariant, so nothing can drift (satisfies §A.1 rule 4). |
| **CON-BR2** LLM cannot decide | `rules-engine` (U3) produces the recommendation | `memo-agent-core` consumes read-only; QA-5 asserts in `quality-gates` |
| **CON-BR3** seeded/frozen corpus | `corpus-generator` (U14) | `outlier-model` reads frozen corpus |
| **CON-BR4** decision-write + advisory | **backend**: `audit-store`/DecisionCommitService (U12); **copy**: `ui-shell` (U10) | UI facets `ui-approval-gate`/`ui-override-form` consume the backend gate |
| **CON-AUDIT-1** 6-tuple + replay | `audit-store` (U12) | `ui-history` links to it; `rules-engine` replay re-eval |
| **CON-DET-1** determinism | `rules-engine` + `outlier-model` (enforcement) | **verification**: `quality-gates` reproducibility |

Each invariant has exactly **one authoritative definition/verification owner**; other units
**consume** or provide **layered enforcement**, so no two co-equal units can let a definition
drift (satisfies `unit-of-work-plan.md §A.1` rule 4).

---

*End of unit-of-work.md. Story assignment proof → `unit-of-work-story-map.md`; inter-unit
dependencies → `unit-of-work-dependency.md`. Stop at the Units Generation completion gate.*
