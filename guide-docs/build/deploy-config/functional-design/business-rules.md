# Business Rules — `deploy-config` (U23, EPIC-6, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Depth**: lighter ·
**Date**: 2026-07-19 · Story **US-PLAT-11**.
**Nature**: `deploy-config` owns **no domain rule, no route, no score, no memo, no recommendation**. It is a **deployment-packaging/
config** unit. The rules below (**BR-DEP-\***) are **checkable** invariants, each grounded in a frozen contract, Scope-A's summary, or
a settled answer — **none introduces domain logic**, and **none re-opens a frozen artifact**. Built on **Q1–Q5 = A** and
**DEP-FD-Fold-1..3** (plan §4.5).

---

## Rules

### BR-DEP-1 — U23 EDITS NO FROZEN UNIT and NO composition root; it PACKAGES the built system (Q1-A / packaging edge) — **load-bearing**
U23 adds **root-level declarative deploy config** (`render.yaml`/`vercel.json`/frontend build config/env manifest — layout OPEN) +
the **frontend build entry**, and **packages** the frozen `backend/app/` + `frontend/src/` for deploy. It edits **no** frozen
`backend/<unit>/` or `frontend/src/<unit>/` tree, **no** `backend/app/**` or `frontend/src/app/**` (the **closed composition root**),
and writes **no** application-integration code.
- **Grounded**: `unit-of-work-dependency.md:52` (*"packages the validation deploy"*) / `:200` (*"wrap the built system"*); Q1-A;
  the composition-root Scope-A hold (frozen).
- **Checkable**: no U23 deliverable modifies a file under any frozen tree (mtime / path check); U23 config **references** the built
  entrypoints (`backend.app.main:app`; the frozen `App.jsx`) without redefining them.

### BR-DEP-2 — the FRONTEND BUILD produces a STATIC BUNDLE Vercel serves (the browser-runnability Scope-A §9 deferred here)
U23 supplies the **bundler entry** (`index.html` + a `main` entry that mounts the **frozen `App.jsx`**) + a build config + a `build`
script, producing a **static bundle** Vercel serves. The frozen `frontend/src/` units are **composed, never edited**.
- **Grounded**: Scope-A §9 (*"cannot run in a browser — no bundler; `deploy-config` (U23) owns that"*); the verified absence of any
  build entry in `frontend/`.
- **Checkable**: a build entry + config + `build` script exist and emit a static output dir; the frozen `App.jsx` is imported by the
  entry, not modified; no frozen frontend module is touched.

### BR-DEP-3 — the BACKEND BOOTS on Render via the fail-closed `Settings`
The Render backend service runs the frozen `backend/app` `create_app()`/`app` under a Python runtime + start command, with the
**six Phase-1 env vars present** (incl. `GEMINI_API_KEY` — required-but-unused, a dummy satisfies it, Scope-A Q5-A) so
`secrets_config.Settings` construction succeeds (fail-closed).
- **Grounded**: `backend/app` (frozen); `secrets_config.Settings` (frozen, all six required); Scope-A Q5-A.
- **Checkable**: the Render service config names the start command running `backend.app.main:app`; the env manifest lists the six
  required shapes; no frozen `Settings` field is made optional (no frozen edit).

### BR-DEP-4 — SEC-3 SHAPES-ONLY: no secret/key/URL VALUE in any committed deploy artifact
No deploy-config artifact or committed file carries a secret/key/connection-string **value** — only variable-name **shapes** + the
`secrets-config` contract. Real per-env values are set **in the deploy platform** (Render/Vercel dashboards), **never committed**.
- **Grounded**: SEC-3; `secrets-config` (the values owner); `database` Infra §5 (shapes-only precedent).
- **Checkable** (the detector-self-test analog): no committed deploy file matches a secret-value pattern (a synthetic
  `LANGFUSE_SECRET_KEY="sk-…"` would be flagged); every credential appears **only** as a name shape.

### BR-DEP-5 — FREE-TIER ONLY; validation/staging, NOT production (NFR-CONSTRAINTS-1 / NFR-DEPLOY-1 / OOS-4)
The deploy uses **Render free-tier + Vercel free-tier** (+ free-tier observability backends); no paid resource is provisioned.
This is a **validation/staging** deploy **confirming cloud-readiness** — **production** deploy is **Phase-3 (OOS-4)**.
- **Grounded**: NFR-CONSTRAINTS-1 (free-tier only); NFR-DEPLOY-1 (validation/staging); OOS-4 (production = Phase 3).
- **Checkable**: the platform configs name free-tier plans only; no artifact provisions a paid tier; the deploy is labelled
  validation/staging, not production.

### BR-DEP-6 — NO DOMAIN ROUTE WIRED / no domain state invented — R2–R5 stay `501` markers (Q2-A)
U23 deploys the system **as it stands**: R1/R6/R7 real, **R2–R5 = honest `501 not_implemented` markers**. It invents **no**
pending-application store, **no** commit path, **no** `0003` migration — the queue→memo→commit lifecycle is **un-designed domain
state (Scope B/C)**, explicitly not this unit's.
- **Grounded**: Scope-A §9 (verbatim — R2–R5 are Scope B/C); `routes/not_wired.py` (frozen); Q2-A.
- **Checkable**: the deployed app's route table is the frozen composition root's unchanged (R1/R6/R7 + the four R2–R5 markers); no
  U23 deliverable adds or backs a domain route.

### BR-DEP-7 — HONEST PARTIAL-DEPLOY DOCUMENTATION (Q3-A + DEP-FD-Fold-2/-3)
The deploy artifacts (a README/deploy doc) **document faithfully**: which routes are **live** (R1/R6/R7) vs return **`501`**
(R2–R5); the **Q1-B divergence** (R6/R7 enforce `READ_AUDIT` → admin 403, diverging from WIRE-1 §3's *"authenticated"*, still OPEN,
separately owned); and that **AC-7's 100%-trace audit is provisioned-for but not yet dischargeable** (contingent on the deferred
composition-owned live langfuse binding). **Nothing is hidden or claimed working that is not.**
- **Grounded**: NFR-DEPLOY-1 (validation/staging framing); Scope-A §3 (Q1-B) + §9; DEP-FD-Fold-2/-3; the honest-behavior discipline.
- **Checkable**: the deploy doc enumerates the live/`501` route split, names the Q1-B divergence, and records AC-7's contingency —
  no over-claim of end-to-end functionality.

### BR-DEP-8 — the OBS-SINK-DEFERRED DEPLOYMENT HALF is in scope; the code-attachment half + MCP-TRANSPORT-DEFERRED are NOT (Q1-A / DEP-FD-Fold-1)
U23 provisions the **deployment half** of the observability deferral — Prometheus **`/metrics` scrape config**, the **Grafana
dashboard-as-code file**, Langfuse/Prometheus free-tier provisioning, and **setting** the `LANGFUSE_*` env — and wires the
`database` **migration release step** + role-URL env. It does **NOT** write the live langfuse **callback attachment** (composition,
CLOSED) or the **MCP transport binding** (application-integration) — both remain **separately owned even after U23**.
- **Grounded**: `observability` `OBS-SINK-DEFERRED` §3; `database` Infra §5/§6; `MCP-TRANSPORT-DEFERRED` (U19); Q1-A; DEP-FD-Fold-1.
- **Checkable**: U23 deliverables include the scrape/dashboard/env config but **no** code attaching a callback into `main.py` and
  **no** MCP transport module; the env vars are **set-not-consumed** by U23 (consumption stays composition/application's).

### BR-DEP-9 — ADVISORY-ONLY inherited trivially; U23 alters no outcome
U23 declares **no** recommendation/verdict and wires **no** domain logic; it is config/packaging only. There is **no** path through
U23 a `Recommendation` flows through.
- **Grounded**: skill #1; the unit's packaging nature; CON-BR2 (LLM cannot decide) inherited.
- **Checkable**: no U23 deliverable declares or emits a `Recommendation`/verdict or any domain decision; it configures deploy only.

---

## Rule → source traceability

| Rule | Frozen source / decision |
|---|---|
| BR-DEP-1 | `unit-of-work-dependency.md:52/200`, Q1-A, the composition-root hold |
| BR-DEP-2 | Scope-A §9, the verified no-bundler frontend |
| BR-DEP-3 | frozen `backend/app` + `secrets_config.Settings`, Scope-A Q5-A |
| BR-DEP-4 | SEC-3, `secrets-config`, `database` Infra §5 |
| BR-DEP-5 | NFR-CONSTRAINTS-1, NFR-DEPLOY-1, OOS-4 |
| BR-DEP-6 | Scope-A §9, `routes/not_wired.py`, Q2-A |
| BR-DEP-7 | NFR-DEPLOY-1, Scope-A §3/§9, DEP-FD-Fold-2/-3 |
| BR-DEP-8 | `OBS-SINK-DEFERRED` §3, `database` Infra §5/§6, `MCP-TRANSPORT-DEFERRED`, Q1-A, DEP-FD-Fold-1 |
| BR-DEP-9 | skill #1, CON-BR2 inherited |

**No orphan** — US-PLAT-11 / NFR-DEPLOY-1 → BR-DEP-2/3/5/6/7; the packaging edge → BR-DEP-1/8; SEC-3 → BR-DEP-4; free-tier/OOS-4 →
BR-DEP-5; honest-partial → BR-DEP-6/7; advisory-only inherited → BR-DEP-9.
**Story coverage**: **US-PLAT-11** → BR-DEP-1..9 as a set (build/serve: 2/3/5; scope boundary: 1/6/8; honesty: 4/7/9).
