# Personas — Agentic Underwriting Assistant

**Stage**: DISCOVER → User Stories (Part 2 — Generation)
**Date**: 2026-06-18
**Source**: Derived from `requirements.md` PER-1..6
**Coverage (per approved plan, Q1 = B)**: Underwriter **full**, Compliance/Audit
reviewer **full**, System administrator **minimal (CLI/migration only)**.

> Language convention (Skill, FR-UI-4, BR4): the system emits a
> **recommendation** (APPROVE / REFER / DECLINE-RECOMMEND); only the human
> underwriter makes a committed **decision**. Personas honour that distinction.

---

## Persona 1 — Underwriter (PRIMARY)

| Attribute | Detail |
|---|---|
| **Maps to** | PER-1, PER-4 |
| **Role** | Front-line life/health insurance underwriter |
| **Access** | Authenticated UI user (JWT/session); read + **act** at the human approval gate |
| **Primary surface** | React + Tailwind Underwriter UI |
| **Goals** | Clear the application queue quickly **without** sacrificing explainability; trust that every recommendation is evidence-backed; record a defensible decision |
| **Key tasks** | Open queued applications; read the decision memo with rule citations; inspect outlier flags + SHAP; **approve** a recommendation or **override with a mandatory reason**; review decision history |
| **Pain points removed** | 20–30 min manual review; inconsistent calls; no audit trail; no replay |
| **Success looks like** | Each case shows *why* it landed APPROVE / REFER / DECLINE-RECOMMEND; no recommendation is committed without an explicit human action carrying a reason |
| **Hard constraints they rely on** | Human-in-the-loop gate (FR-UI-2), advisory-only language (FR-UI-4), reproducible recommendations (NFR-REPRO-1) |

## Persona 2 — Compliance / Audit Reviewer (FULL, READ-ONLY)

| Attribute | Detail |
|---|---|
| **Maps to** | PER-2, PER-4, SEC-4, SEC-5 |
| **Role** | Compliance / internal-audit reviewer |
| **Access** | Authenticated UI user, **strictly read-only**; MUST NOT be able to edit what they audit (DB-level read-only role) |
| **Primary surface** | Read-only decision history, audit trail, and quality-report views |
| **Goals** | Verify auditability: every recommendation carries its full audit tuple; confirm bias-invariance and reproducibility evidence exists; replay any past decision against its original rulebook version |
| **Key tasks** | Browse decision history; open a past decision read-only; view `rulebook_version` / `rule_results` / `timestamp` / `model_version` / `memo_hash`; view the bias-swap and reproducibility reports |
| **Pain points removed** | No structured audit trail; inability to replay decisions against the rules that were active at the time |
| **Success looks like** | 100% of recommendations traceable; bias-swap delta = 0 and reproducibility = 100% demonstrable from artifacts; zero edit capability |
| **Hard constraints they rely on** | RBAC separation (PER-4), read-only DB access (SEC-4), audit logging (SEC-5), replay (CON-AUDIT-1) |

## Persona 3 — System Administrator (MINIMAL — CLI / migration only)

| Attribute | Detail |
|---|---|
| **Maps to** | PER-3, PER-6, FR-RULES-6, SEC-3 |
| **Role** | Platform/system administrator |
| **Access** | **Out-of-band CLI / database migrations** — *not* a UI role; no admin UI this engagement |
| **Primary surface** | Command line + migration scripts |
| **Goals** | Manage rulebook versions; manage users and configuration; keep published rule versions immutable |
| **Key tasks** | Publish a new rulebook version (never mutate a published one); manage users/roles; set provider/config via env/secrets |
| **Coverage note** | Minimal stories only (Q1 = B). Full UI-style stories would describe screens that do not exist (PER-3). Admin is excluded from the UI user-journey diagram (Q6 = B). |
| **Hard constraints they rely on** | Immutable published rule versions (FR-RULES-6), secrets management (SEC-3) |

---

## Access Model (cross-persona)

| ID | Rule |
|---|---|
| PER-4 | Authentication = basic login with role-based access (JWT/session). RBAC MUST enforce underwriter (act) vs auditor (read-only) in the UI. |
| PER-5 | Auth layer MUST be structured so an OIDC/SSO provider can slot in later without rework. *(Full SSO itself = Phase 3 / future release, OOS-3.)* |
| PER-6 | UI roles = underwriter + auditor(read-only); **admin operates out-of-band via CLI**, not a UI role. |

## Persona → Epic map

| Persona | EPIC-1 Intake | EPIC-2 Rules | EPIC-3 Outlier | EPIC-4 Memo | EPIC-5 UI | EPIC-6 Platform/Quality/Access |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Underwriter | benefits | benefits | benefits | benefits | **primary actor** | benefits |
| Auditor (read-only) | — | benefits (replay) | benefits (evidence) | benefits (memo trail) | read-only views | **primary actor** (reports, audit trail) |
| Admin (CLI) | — | acts (versions) | — | acts (provider config) | — | acts (CLI: users, config) |
