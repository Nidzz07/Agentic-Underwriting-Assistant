# GUIDE-AI-SDP State Tracking

## Project Information
- **Project Name**: Agentic Underwriting Assistant
- **Project Type**: Greenfield
- **Start Date**: 2026-06-14T09:01:22Z
- **Current Stage**: DISCOVER - Requirements Analysis (Comprehensive Depth)

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

## Stage Progress

### 🔵 DISCOVER PHASE
- [x] Workspace Detection — Completed 2026-06-14T09:01:22Z (Greenfield)
- [x] Reverse Engineering — SKIPPED (greenfield, no existing code)
- [ ] Requirements Analysis — IN PROGRESS (comprehensive depth; requirements.md generated, awaiting approval at gate)
- [ ] User Stories — TBD (Workflow Planning will decide)
- [ ] Workflow Planning — PENDING
- [ ] Application Design — TBD
- [ ] Units Generation — TBD

### 🟢 BUILD PHASE
- [ ] Functional Design (per-unit) — TBD
- [ ] NFR Requirements (per-unit) — TBD
- [ ] NFR Design (per-unit) — TBD
- [ ] Infrastructure Design (per-unit) — TBD
- [ ] Code Generation (per-unit) — PENDING (ALWAYS)
- [ ] Build and Test — PENDING (ALWAYS)

### 🟡 DEPLOY PHASE
- [ ] Deploy — PLACEHOLDER

## Deferred Decisions (carry forward — see requirement-verification-questions.md "Deferred Decisions Register")
- Phase boundaries / whether a Phase 3 exists → decide at Workflow Planning / Units Generation
- SSO/OAuth timing → revisit once phasing is finalized
- Synthetic corpus generation timing relative to phases → re-raise at a later stage
- Senior-underwriter escalation persona (Q5-B) → deferred unless escalation enters scope

## Current Status
- **Lifecycle Phase**: DISCOVER
- **Current Stage**: Requirements Analysis (comprehensive depth)
- **Next Step**: User to review/approve requirements.md at the Requirements approval gate; on approval, proceed to next DISCOVER stage (User Stories assessment / Workflow Planning)
- **Status**: requirements.md generated (comprehensive) and REVISED twice per user change-requests. Round 1: DATA-4 +Skill source; FR-MEMO-5 provider-adapter note; AC-6 Ollama exemption; occupation initially deferred. Round 2: occupation RESOLVED 2026-06-17 — legitimate underwriting input AND proxy-checked, mirroring income (may influence the decision ONLY through the occupation-risk rule); §12 occupation row marked resolved (no longer deferred); proxy check still covers all three (pincode/occupation/income). STOPPED at approval gate awaiting explicit user approval.