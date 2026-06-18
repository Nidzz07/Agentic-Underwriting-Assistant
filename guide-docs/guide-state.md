# GUIDE-AI-SDP State Tracking

## Project Information
- **Project Name**: Agentic Underwriting Assistant
- **Project Type**: Greenfield
- **Start Date**: 2026-06-14T09:01:22Z
- **Current Stage**: DISCOVER - Workflow Planning (execution-plan.md generated; awaiting approval at the Workflow Planning gate before Application Design)

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

### 🔵 DISCOVER PHASE
- [x] Workspace Detection — Completed 2026-06-14T09:01:22Z (Greenfield)
- [x] Reverse Engineering — SKIPPED (greenfield, no existing code)
- [x] Requirements Analysis — COMPLETED 2026-06-17 (comprehensive depth; requirements.md approved at gate after 2 revision rounds)
- [x] User Stories — COMPLETED 2026-06-18 (Part 1 plan + Part 2 artifacts approved at gate; stories.md, personas.md, user-journey.md final and committed/pushed)
- [~] Workflow Planning — IN PROGRESS (ALWAYS; execution-plan.md generated 2026-06-19, awaiting approval at gate)
- [ ] Application Design — EXECUTE (recommended; per execution-plan.md)
- [ ] Units Generation — EXECUTE (recommended; per execution-plan.md)

### 🟢 BUILD PHASE
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
- **Lifecycle Phase**: DISCOVER
- **Current Stage**: Workflow Planning — execution-plan.md GENERATED; STOPPED at the approval gate (awaiting explicit user approval before Application Design)
- **Next Step**: User reviews `execution-plan.md` at the Workflow Planning gate and chooses Request Changes / Add Skipped Stages / Approve & Continue. On approval, advance to **Application Design** (CONDITIONAL — recommended EXECUTE): load `discover/application-design.md`, load prior context, execute at the approved depth, stop at its completion gate. User has reserved the lighten/skip-depth decision for THIS gate.
- **Status**: requirements.md APPROVED 2026-06-17. User Stories APPROVED at gate 2026-06-18. Workflow Planning execution-plan.md generated 2026-06-19 (greenfield; single validated GUIDE-stage Mermaid diagram + text alternative; all conditional stages recommended EXECUTE at comprehensive depth with per-unit depth-variation notes for the gate; Phase 1→2 as BUILD-loop annotation referencing stories.md §8; REFER-gate resolution carried in, not re-opened). guide-state.md L7 stale Current-Stage header corrected as part of this Step 8 update. STOPPED at the Workflow Planning approval gate per protocol.

## Open Items Carried Into Workflow Planning
- *(none open — the REFER human-approval-gate item was **RESOLVED 2026-06-18** and moved to Resolved Decisions above. Synthetic-corpus generation timing remains a deferred item under Deferred Decisions, not an open blocker for Workflow Planning.)*