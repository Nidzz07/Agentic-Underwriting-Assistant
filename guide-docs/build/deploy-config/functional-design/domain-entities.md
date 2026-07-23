# Domain Entities — `deploy-config` (U23, EPIC-6, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Depth**: **lighter**
(per `unit-of-work.md:250/262` — comprehensive reserved for Infrastructure Design) · **Date**: 2026-07-19 · Story **US-PLAT-11** ·
NFR-DEPLOY-1.
**Scope**: the entity/interface view of `deploy-config` — the **deployment-packaging/config** unit that wraps the already-built
system for a **free-tier Render + Vercel validation deploy**. Built on **Q1–Q5 = A** and the folds **DEP-FD-Fold-1..3** (plan §4.5),
re-opening none. **NO code in this stage.**

> **U23 adds NO domain contract, NO domain route, and NO application-integration code.** It **packages** the frozen system
> (`backend/app/` + `frontend/src/`) into a deployable form (Render backend + Vercel static frontend), **provisions** the free-tier
> cloud substrate + the observability **deployment half**, and **wires env** (shapes only). It **edits no frozen unit** and the
> **closed composition root**; the **live sink/callback attachment** + the **MCP transport binding** stay composition/application-
> owned (Q1-A). Advisory-only is inherited **trivially**: U23 has no path a recommendation flows through.

---

## 1. Scope boundary — what this unit is, and what it is NOT

| | |
|---|---|
| **IS** (Q1-A / Q5-A) | a **deployment-config/packaging** unit with **largely declarative** surfaces: **(a)** the **frontend build** (a bundler entry + build config producing a **static bundle Vercel serves** — the browser-runnability Scope-A §9 assigned here); **(b)** the **Render backend service** config (runtime, start command, the fail-closed `Settings` env requirement); **(c)** the **env manifest** (variable-name **shapes** for Phase-1 required + Phase-2 reserved, SEC-3); **(d)** the **migration release-step** wiring (`database` hand-off); **(e)** the **observability deployment half** (`/metrics` scrape config + the **Grafana dashboard-as-code file** + `LANGFUSE_*` env). |
| **IS NOT** | an **application-integration** unit — it writes **no** live langfuse callback attachment, **no** MCP transport binding, **no** domain route (R2–R5 stay `501` markers — Q2-A). **Not** a resolver of the composition-root **Q1-B divergence** (separately owned — DEP-FD-Fold-3). **Not** a production deploy (that is **Phase-3 / OOS-4**); this is **validation/staging confirming cloud-readiness** (NFR-DEPLOY-1, Q3-A). **Not** an editor of any frozen unit or the closed composition root. |

**The module/layout is OPEN** (Q5-A) — `unit-of-work.md` names `deploy-config` but enumerates no files; a deployment-config unit is
**largely declarative** (`render.yaml`/`vercel.json`/frontend build config/env manifest at the workspace root) and **may need no
`backend/deploy_config/` Python package** at all. The exact deliverable set is pinned at **Infrastructure Design (comprehensive) /
Code-Gen**, not here.

---

## 2. Config surfaces (proposed — layout OPEN, Q5-A)

| Surface | Role | Owned/pinned by |
|---|---|---|
| **Frontend build** | a bundler entry (`index.html` + a `main` entry mounting frozen `App.jsx`) + build config + a `build` script → a **static bundle** Vercel serves | **U23** (the browser-runnability Scope-A §9 deferred here); **frozen `frontend/src/app/App.jsx` composed, never edited** |
| **Vercel project config** | the static-frontend deploy (build command, output dir, free-tier) | **U23** (topology at **Infra Design**) |
| **Render backend service** | the Python runtime + start command running the frozen `backend/app` `create_app()`/`app`; the fail-closed `Settings` env requirement | **U23** (topology at **Infra Design**); **frozen `backend/app` composed, never edited** |
| **Env manifest (shapes only)** | the variable-name **shapes** the deploy sets: Phase-1 required (`DATABASE_URL`, `AUDIT_WRITER_URL`, `AUDIT_READER_URL`, `AUDIT_WRITER_PASSWORD`, `AUDIT_READER_PASSWORD`, `GEMINI_API_KEY`) + Phase-2 reserved (`LANGFUSE_*`, `ANTHROPIC_API_KEY`, `OLLAMA_HOST`) | **U23** sets values **in the deploy env** (never committed, SEC-3); **`secrets-config` owns the contract** |
| **Migration release step** | the Render release/pre-deploy step that runs the `database` migration sequence before traffic | **U23** wires the step; **`database` owns the runner** (reference-not-own) |
| **Observability deployment half** | `/metrics` **scrape config** + the **Grafana dashboard-as-code file** + `LANGFUSE_*`/Prometheus provisioning | **U23** (the deployment half of `OBS-SINK-DEFERRED`, Q1-A); **`observability` owns the sink code + dashboard topology** |

---

## 3. Reference-not-own boundary (packaged/consumed — re-declared by none, modified by none)

| Concern | Owner (frozen) | U23 relationship |
|---|---|---|
| `backend/app/` (`create_app`, R1/R6/R7, R2–R5 markers) + all frozen `backend/<unit>/` | the **closed composition root** + the 17 P1 + U18/U19/U21 | **packaged + run, never edited** |
| `frontend/src/` (frozen units + `frontend/src/app/`) | the frozen frontend units + Scope-A `app/` | **composed into a build, never edited** |
| all secret/key/URL **VALUES** + the env contract | **`secrets-config`** (U16, SEC-3) | U23 sets values **in the deploy env** (shapes only in artifacts) |
| the migration **runner** + schema | **`database`** (U15) | U23 wires the **release step**; the runner is database's |
| the trace/metric **sink code** + Grafana **dashboard topology** | **`observability`** (U21) | U23 provisions the **deployment half** (scrape/dashboard-file/env) |
| the live langfuse **callback attachment** + per-node passthrough; the **MCP transport binding** | **composition (CLOSED)** / application | **DEFERRED — NOT U23's** (Q1-A; `OBS-SINK-DEFERRED` code half + `MCP-TRANSPORT-DEFERRED`) |
| the **R2–R5** domain lifecycle; the **Q1-B** contract reconciliation | **Scope B/C** / composition-contract | **out of scope — deployed as-built + documented, not resolved** (Q2-A, DEP-FD-Fold-3) |

**Reference-not-own**: U23 imports/edits **no** frozen unit and **no** composition-root file; it **packages** them. `deploy-config`'s
consumers (the deploy platform) read U23's config — never the reverse.

---

## 4. Deferred to Infrastructure Design (comprehensive) — the "wiring-heavy" half

This lighter FD pins **WHAT** deploy-config is + its **scope boundary**. **Infrastructure Design (comprehensive)** owns: the actual
**Render + Vercel topology** (services, regions, build commands, output dirs, free-tier plans), the **env manifest contents** +
per-tier wiring, the **migration release-step** command, the **`/metrics` scrape config** + the **Grafana dashboard-as-code file**,
the **frontend build config** (bundler choice + `index.html`/entry), and the **AC-7 provisioning** (the Langfuse backend the audit
would query — its **pass contingent on the deferred composition binding**, DEP-FD-Fold-2). Likely the **3rd real non-skip
Infrastructure Design** after `database` + `observability`.

---

## 5. FD ↔ later-stage boundary
- **This FD pins**: the unit's nature (deployment-packaging/config, not application logic); the config surfaces (§2); the
  reference-not-own boundary (§3); the scope triage (Q1–Q4 + DEP-FD-Fold-1..3); the honest-partial-deploy posture (R1/R6/R7 live,
  R2–R5 `501`, Q1-B documented, AC-7 provisioned-for-not-discharged); free-tier + validation/staging (not production).
- **NFR Requirements / NFR Design owns**: the pass/fail-testable deploy targets (`NFR-DEP-*`), the tier convention.
- **Infrastructure Design (comprehensive) owns**: the actual Render/Vercel topology + build commands + env manifest + migration
  release step + observability scrape/dashboard config (§4).
- **Out of scope (named-not-designed)**: R2–R5 wiring (Scope B/C); the live callback/MCP integration code (composition/application);
  the Q1-B reconciliation; production deploy (Phase-3 / OOS-4).
