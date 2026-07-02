# GUIDE-AI-SDP State Tracking

## Project Information
- **Project Name**: Agentic Underwriting Assistant
- **Project Type**: Greenfield
- **Start Date**: 2026-06-14T09:01:22Z
- **Current Stage**: **DISCOVER PHASE COMPLETE (2026-07-02)** — Units Generation COMPLETED 2026-07-02 (gate approved; 23-unit decomposition, story-map 40/40, dependency matrix). **BUILD PHASE is next, not yet started** (first stage = Functional Design, per-unit).

## Workspace State
- **Existing Code**: No (only a Python `venv/` and root `requirements.txt`; no application source)
- **Programming Languages**: Python intended (per requirements.txt); React + Tailwind planned for UI (TypeScript TBD — not yet specified in brief)
- **Build System**: pip / requirements.txt (Python); npm planned for frontend
- **Project Structure**: Empty (greenfield)
- **Reverse Engineering Needed**: No
- **Workspace Root**: C:\Users\NIDHI\Desktop\underwriting-project
- **Model provider config (applied 2026-06-17)**: PROJECT-BRIEF.md updated to Gemini-primary / Claude-secondary (tested fallback) / Ollama-showcase, runtime-selectable via config/settings behind the provider-abstraction layer (per Q4); supersedes brief v1.0 Claude-primary. NOTE: CLAUDE.md contains NO model config (it is the GUIDE-AI-SDP workflow engine) — the config lives in PROJECT-BRIEF.md.

## Code Location Rules
- **Application Code**: Workspace root (NEVER in guide-docs/)
- **Documentation**: guide-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Extension Configuration
| Extension | Enabled | Decided At |
|---|---|---|
| Security Guardrails | Enabled (scoped) | Requirements Analysis (Q13 answered) |

Security Guardrails scope: prompt-injection defense, input validation, secrets management, read-only DB access for audit role, audit logging.

## Execution Plan Summary (draft — pending Workflow Planning gate approval)
- **Artifact**: `guide-docs/discover/plans/execution-plan.md` (generated 2026-06-19)
- **Stages to Execute (recommended)**: Application Design, Units Generation, Functional Design (per-unit), NFR Requirements (per-unit), NFR Design (per-unit), Infrastructure Design (per-unit), Code Generation (ALWAYS), Build and Test (ALWAYS)
- **Stages Skipped**: Reverse Engineering (greenfield); Deploy = placeholder (production deploy = Phase 3; validation deploy is a Phase 2 BUILD unit)
- **Depth**: Comprehensive recommended; lighten/skip decision reserved by user for the gate (per-unit depth-variation notes provided in execution-plan.md §3)
- **Phase 1→2 sequencing**: per-unit BUILD loop runs all Phase 1 units before Phase 2 (BUILD-loop annotation; see stories.md §8)
- **Risk**: Medium (high intrinsic complexity, greenfield so easy rollback; dominant risk = invariant correctness)

## Stage Progress

### 🔵 DISCOVER PHASE — ✅ COMPLETE (2026-07-02)
- [x] Workspace Detection — Completed 2026-06-14T09:01:22Z (Greenfield)
- [x] Reverse Engineering — SKIPPED (greenfield, no existing code)
- [x] Requirements Analysis — COMPLETED 2026-06-17 (comprehensive depth; requirements.md approved at gate after 2 revision rounds)
- [x] User Stories — COMPLETED 2026-06-18 (Part 1 plan + Part 2 artifacts approved at gate; stories.md, personas.md, user-journey.md final and committed/pushed)
- [x] Workflow Planning — COMPLETED 2026-06-18 (ALWAYS; execution-plan.md generated 2026-06-19 + 3-correction pre-approval pass, APPROVED at gate "Approve & Continue")
- [x] Application Design — COMPLETED 2026-06-29 (gate approved after reviewer-feedback batch)
- [x] Units Generation — COMPLETED 2026-07-02 (gate approved; 23-unit decomposition [17 P1 / 6 P2], story-map 40/40, dependency matrix — unit-of-work.md / unit-of-work-dependency.md / unit-of-work-story-map.md)

### 🟢 BUILD PHASE — NEXT (not yet started; awaiting user signal to start Functional Design, per-unit)
- [ ] Functional Design (per-unit) — EXECUTE (recommended; per-unit depth variation noted in execution-plan.md for gate)
- [ ] NFR Requirements (per-unit) — EXECUTE (recommended; per-unit depth variation noted for gate)
- [ ] NFR Design (per-unit) — EXECUTE (recommended; per-unit depth variation noted for gate)
- [ ] Infrastructure Design (per-unit) — EXECUTE (recommended; per-unit depth variation noted for gate)
- [ ] Code Generation (per-unit) — EXECUTE (ALWAYS)
- [ ] Build and Test — EXECUTE (ALWAYS)

### 🟡 DEPLOY PHASE
- [ ] Deploy — PLACEHOLDER

## Deferred Decisions (carry forward — see requirement-verification-questions.md "Deferred Decisions Register")
- SSO/OAuth timing → now Phase 3 (OOS-3); detailed timing within Phase 3 deferred to that release
- Synthetic corpus generation timing relative to phases → re-raise at a later stage
- Senior-underwriter escalation persona (Q5-B) → deferred unless escalation enters scope

## Resolved Decisions
- Phase boundaries / whether a Phase 3 exists → **RESOLVED 2026-06-18**: Phase 1 + Phase 2 built this engagement (every story phase-tagged 1/2); Phase 3 = documented future release (OOS-2..6 + production deploy). Validation deploy = Phase 2; production deploy = Phase 3. (Detail in requirements.md §2.2 / §12.)
- Human-approval-gate semantics for a REFER recommendation → **RESOLVED 2026-06-18** (per project direction): Phase 1/2 = the underwriter resolves every recommendation incl. REFER at the human approval gate via Accept/Decline with a mandatory reason (no REFER-specific branch built); REFER→senior-underwriter escalation routing = Phase 3 / OOS-2 (documented, not built). Gate stories (US-UI-4/5) and user-journey.md already encode this uniform gate — no story/journey edits needed. (Detail in requirements.md OOS-2 / §12.)

## Current Status
- **Lifecycle Phase**: **DISCOVER COMPLETE (2026-07-02)** → **BUILD pending** (not yet started)
- **Current Stage**: **Units Generation COMPLETED 2026-07-02** (completion gate approved). This was the **final DISCOVER stage** — the DISCOVER phase (Requirements Analysis → User Stories → Workflow Planning → Application Design → Units Generation) is now **complete**. Next phase = **BUILD** (per-unit loop, starting with Functional Design), not yet started.
- **Next Step**: **Await the user's explicit signal to start the first BUILD stage — Functional Design (per-unit).** The **23-unit decomposition (17 Phase 1 / 6 Phase 2)** in `unit-of-work.md` is the authoritative BUILD foundation; the BUILD per-unit loop runs **all Phase-1 units to completion before any Phase-2 unit** (`execution-plan.md §4.1`). Carry-forward reminders for BUILD start are recorded under "Open Items Carried Into BUILD Phase" below. Stop-before-generate discipline continues (each per-unit stage uses the standardized 2-option completion message).
- **Status**: requirements.md APPROVED 2026-06-17. User Stories APPROVED at gate 2026-06-18. Workflow Planning APPROVED at the gate 2026-06-18 ("Approve & Continue"). Application Design APPROVED at the completion gate 2026-06-29. **Units Generation APPROVED at the completion gate 2026-07-02** — three artifacts (`unit-of-work.md`, `unit-of-work-dependency.md`, `unit-of-work-story-map.md`) generated + review-corrected: 23-unit decomposition (Q1..Q6 = A + F1–F5 resolutions; `ui-shell` owns US-UI-7; `auth-rbac` one shared unit; grouped `outlier-model`/`memo-extensions`; `audit-store` = decision-commit+audit+replay boundary owning DecisionCommitService; `database` story-less infra), story-map proving **40/40 stories assigned exactly once** (per-epic 4/5/3/7/7/12/2; 30 P1 / 10 P2), dependency matrix consistent with `component-dependency.md` (document-sanitizer mid-pipeline edge pinned; phase-safe, no P1→P2 back-edge), binding invariants single-sourced. **DISCOVER phase complete — no stages remaining.**

## Open Items Carried Into Application Design
1. **Per-unit depth "lighter" classifications are RECOMMENDATIONS, not a locked floor** — the execution-plan's per-unit "lighter" depth notes (e.g. `secrets-config`, `admin-cli`, `deploy-config`, display-only `ui-queue`/`ui-history`/`ui-memo-view`) are revisitable per-unit at each BUILD design stage; any such unit can be given comprehensive depth when its design stage is reached, without amending execution-plan.md. (Invariant-bearing UI — `ui-approval-gate`, `ui-override-form` — remain comprehensive per FR-UI-2 / CON-BR4 / FR-UI-4.)
2. **Provisional-unit overlap to resolve at Units Generation**: `ui-auth-rbac` (C5 / EPIC-5) vs `auth-rbac` (EPIC-6) — confirm whether RBAC is one shared unit or two. Record/surface in Application Design; the definitive boundary call is made at Units Generation.

## Open Items Carried Into Workflow Planning (closed)
- *(none open — the REFER human-approval-gate item was **RESOLVED 2026-06-18** and moved to Resolved Decisions above. Synthetic-corpus generation timing remains a deferred item under Deferred Decisions, not an open blocker.)*

## Open Items Carried Into BUILD Phase (surfaced at DISCOVER→BUILD boundary; not yet acted on)
1. **Per-unit "lighter" depth = revisitable recommendation, NOT a locked floor.** The per-unit depth classifications in `unit-of-work.md §4` / `execution-plan.md §3` can be raised to comprehensive when a unit's BUILD design stage is reached, without amending those docs. **Invariant-bearing units stay comprehensive regardless**: `ui-approval-gate`, `ui-override-form` (FR-UI-2 / CON-BR4 / FR-UI-4), and the deterministic-core + quality units (`intake`, `document-sanitizer`, `rules-engine`, `outlier-model`, `memo-agent-core`, `auth-rbac`, `audit-store`, `quality-gates`).
2. **Functional Design is the altitude drop from interfaces to internals.** It is where the deferred detail finally gets designed: **field-by-field schema** (`ApplicantProfile`, `RuleResultReport`, `DecisionMemo`, audit 6-tuple), **rule thresholds** (age 18/65, BMI 25/30, DTI ≤40%, income multiples, etc.), and the **reserved Phase-3 seam field definitions** `decision_id` / `status` (active/superseded) / nullable `supersedes_decision_id` (OOS-7 amendment seam) + `engine_version` capture (OOS-8). Application Design deliberately held these at interface altitude; Functional Design lowers it to internals.