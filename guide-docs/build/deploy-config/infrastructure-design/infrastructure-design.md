# Infrastructure Design — `deploy-config` (U23, EPIC-6, Phase 2)

**Stage**: BUILD → Infrastructure Design (per-unit) · **the THIRD non-skip Infrastructure Design in the build** (after `database`
U15 + `observability` U21) · **Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Date**: 2026-07-19 · **Depth**: **comprehensive**.
**Built ON** the frozen FD (`domain-entities.md` config surfaces + **BR-DEP-1..9** + the 6-step lifecycle), the approved
`nfr-requirements.md` (**eleven `NFR-DEP-*`** + **DEP-D1..D8**), and the approved NFR Design (`nfr-design-patterns.md` **P-DEP-1..11**
+ `logical-components.md` **C-DEP-1..5**) — **re-opening none**. This stage designs the **deployment topology** the whole U23 stack
deferred here. Answers **Q1–Q9 (all A)** + folds **INFRA-DEP-Fold-1..3** (plan §3.5).

> **SEC-3 held throughout**: **no credential / key / endpoint / connection VALUES** — only variable-name **shapes** + the
> `secrets-config` contract. **BR-DEP-1 held**: **no frozen unit edited**; the **CLOSED composition root is packaged, never edited**
> (Q3's Vercel rewrite keeps CORS out of the backend). `database`'s + `observability`'s Infra passes are **referenced, not re-opened**.

---

## 1. Component → infrastructure mapping (C-DEP-1..5)

| Component | Kind | Infrastructure realization (this stage) |
|---|---|---|
| **C-DEP-1 `deploy_validators`** | scan logic | **No cloud topology.** Runs in CI/unit over the committed deploy artifacts (path/secret/route-introspection/token/format scans). Named, not provisioned. |
| **C-DEP-2 `render.yaml`** | config artifact | **Realized** as the Render **free-tier Web Service** (§3.1) — runtime, build/start commands, env shapes, the migration release step. |
| **C-DEP-3 `vercel.json` + frontend build entry** | config artifact | **Realized** as the Vercel **free-tier static build** (§3.2) + the **rewrite/proxy** connectivity (§3.3). |
| **C-DEP-4 env manifest** | config artifact | **Realized** as the per-platform env topology (§3.5) — shapes only, values set in the platform. |
| **C-DEP-5 deploy doc** | config artifact | **Realized** as the honest partial-deploy documentation topology (§3.7). |

**Infra realizes the four config artifacts as real free-tier cloud topology; C-DEP-1 is CI/test logic needing no cloud topology.**

---

## 2. Mandatory infra-category sweep (all seven — explicit applicability + justification)

| # | Category | Applicability | Justification |
|---|---|---|---|
| 1 | **Deployment Environment** | **Applicable (CORE)** | Render backend + Vercel frontend, **free-tier**, validation/staging (dev/CI/prod tiers). §3.1, §3.2, `deployment-architecture.md`. |
| 2 | **Storage Infrastructure** | **Reference (not owned)** | The Postgres is **`database`'s** Render free-tier `postgres:16` topology; deploy-config **wires the connection env + the migration release step**, does **not** re-provision (§3.4). |
| 3 | **Compute Infrastructure** | **Applicable** | The **Render Web Service** IS the app compute deploy-config provisions (§3.1); Vercel is static/CDN — **no compute** (§3.2). |
| 4 | **Messaging Infrastructure** | **N/A (justified)** | No queue/event bus; a deploy-config unit has no async/eventing concern. |
| 5 | **Networking Infrastructure** | **Applicable** | Frontend↔backend via the **Vercel rewrite/proxy** (§3.3, no CORS, no backend edit) + managed TLS + the `/metrics` scrape path exposure (§3.6). |
| 6 | **Monitoring Infrastructure** | **Applicable** | The **observability deployment half** — the Prometheus scrape target + the Grafana dashboard-as-code file + Langfuse provisioning (§3.6). |
| 7 | **Shared Infrastructure** | **Narrow (reference)** | deploy-config packages the whole system; the shared Postgres is `database`'s; captured **within `deployment-architecture.md`** — **no separate `shared-infrastructure.md`** (Q7-A). |

**No category silently skipped.** Storage is **reference** (database's), Messaging **N/A-justified**, Shared **narrow** — recorded in
the completion compliance summary.

---

## 3. Deferred-halves topology design

### 3.1 The Render backend service (Q1-A / Compute + Deployment)
A **Render free-tier Web Service**: **Python 3.12** runtime (pinned — matching `.python-version` / `pyproject requires-python`);
**build command** `pip install -r requirements.txt`; **start command** running the **frozen** `backend.app.main:app` under an ASGI
server (`uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`; a gunicorn+uvicorn-worker variant is a Code-Gen detail);
**managed TLS**; validation/staging (not production). The service requires the **six Phase-1 `Settings` env shapes** so the fail-closed
`Settings` constructs (incl. `GEMINI_API_KEY` — a **dummy** for the LLM-less slice, Scope-A Q5-A). **The app is packaged, not edited.**

### 3.2 The Vercel frontend project (Q2-A / Deployment)
A **Vercel free-tier static build**: **framework preset = Vite**; **build command** `npm run build` (the `build` script deploy-config
adds — BR-DEP-2); **output directory** `dist`; the build entry (`index.html` + a `main` mounting the **frozen `App.jsx`**) produces the
static bundle Vercel serves on its CDN; **managed TLS**. **The frozen frontend units are composed, never edited.**

### 3.3 Frontend↔backend connectivity — the Vercel rewrite/proxy (Q3-A / Networking) — **FOLD #1 (the load-bearing decision)**
The Vercel static frontend (one origin) reaches the Render backend (another origin) via a **`vercel.json` rewrite/proxy**: the
frontend makes **same-origin** requests (e.g. `/api/*`) that **Vercel proxies** to the Render backend, so the **browser never makes a
cross-origin call** — **no CORS is needed, and the frozen `backend/app` is NOT edited** (adding CORS would edit the CLOSED composition
root, a BR-DEP-1 violation). The proxy **destination** is the Render backend's **public host** — a **build/env SHAPE**
(e.g. `RENDER_BACKEND_URL` / a rewrite `destination` placeholder), whose **real value is set in the Vercel project env, never
committed**. **SEC-3 note (Fold-1)**: a **public service host is not a credential** — SEC-3 / SEC3-1 target credential patterns
(`sk-…`, `postgresql://user:pass@…`), which a public rewrite host is not; the artifacts name the **shape**.

### 3.4 DB provisioning reference + the migration release step (Q4-A / Storage-reference + Deployment) — **FOLD #2**
**Reference `database`'s Infra topology; wire the release step**: the Postgres is **`database`'s** Render free-tier `postgres:16`
instance (its topology, **not** re-designed here); deploy-config **wires the connection env** (`DATABASE_URL` + the role-scoped
`AUDIT_WRITER_URL` / `AUDIT_READER_URL`, **shapes only**) and the **migration release step** — a **Render release / pre-deploy
command** running `database`'s **forward-only, idempotent** migration sequence (incl. the grants migration, values substituted from
`secrets-config` at execution time) **before** the app serves traffic (exactly the step `database` Infra §3.4 named *"wired by
`deploy-config`"*; startup-migration stays rejected per that pass). **The migration runner is `database`'s; deploy-config pins
WHEN/HOW it runs.**

**Pre-release env consistency (Fold-2)**: the release step needs — **before it runs** — the schema-owning **`DATABASE_URL`** + the
role passwords **`AUDIT_WRITER_PASSWORD`** / **`AUDIT_READER_PASSWORD`** (grants substitution, `database` Infra §3.2). The deploy
doc's **ENV-SHAPES** section (§3.7) lists **exactly these** among the six Phase-1 required shapes — so the doc's env list and the
release-step's prerequisites **name the same set**; the ordering is **env set → migration release step → traffic**.

### 3.5 The env manifest topology (Q5-A / SEC-3) — **shapes only, no values**
Values are **set in the deploy platform, never committed** (SEC-3): the **Render service env** (+ optionally a `render.yaml`
env-var group for shared shapes) for the backend; the **Vercel project env** for the frontend's API base-URL shape (§3.3). The
manifest names the **full shape list — variable NAMES only, never a value**:

| Shape | Phase | Purpose | Set where |
|---|---|---|---|
| `DATABASE_URL` | 1 (required) | owner connection + migration/admin (validated by C3's guard) | Render service env |
| `AUDIT_WRITER_URL` / `AUDIT_READER_URL` | 1 (required) | role-scoped runtime connections (APPEND-1 prod guarantee) | Render service env |
| `AUDIT_WRITER_PASSWORD` / `AUDIT_READER_PASSWORD` | 1 (required) | grants-migration role passwords (substituted at release) | Render service env |
| `GEMINI_API_KEY` | 1 (required) | fail-closed `Settings` — **dummy** in the LLM-less slice (Scope-A Q5-A) | Render service env |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` | 2 (reserved) | Langfuse auth/endpoint — **set-not-consumed** by U23 (the callback is composition's) | Render service env |
| `ANTHROPIC_API_KEY` / `OLLAMA_HOST` | 2 (reserved) | Claude/Ollama adapters — **set-not-consumed** (adapters not in the deployed slice) | Render service env |
| `RENDER_BACKEND_URL` (shape) | deploy | the Vercel rewrite destination (a **non-secret public host** shape) | Vercel project env |

**No value appears in any artifact.** `secrets-config` owns the values; `deploy-config` names the shapes + where they are set.

### 3.6 The observability deployment half (Q6-A / Monitoring) — **FOLD #3**
The **deployment half only** (the code-attachment half stays composition's — `OBS-SINK-DEFERRED`):
1. **Prometheus scrape job** targeting the **Render backend's `/metrics` path** (a **Grafana Cloud** agent *or* a Render-hosted
   Prometheus, **free-tier**), pull-based (no app-side key).
2. **The Grafana dashboard-as-code file** — **one dashboard, five panels 1:1 to `observability`'s FROZEN five metrics** (Fold-3):
   **decision latency** · **decisions by recommendation type** (label `recommendation`) · **rule-evaluation duration** · **LLM-call
   errors** · **outlier-flag rate**; datasource = **Prometheus**; **demographic-free labels** (CON-BR1). **`observability` owns the
   panel topology** (`domain-entities.md §4` / its Infra); **deploy-config owns the committed file that REALIZES it** — the file
   **cannot silently drift** (a panel not in observability's five is out of scope; the five are named explicitly). The exact JSON is a
   **Code-Gen deliverable** bound to this topology.
3. **A Langfuse Cloud project** + the `LANGFUSE_*` env set (§3.5).

**The live langfuse callback attachment is NOT wired here** (composition's `OBS-SINK-DEFERRED` code half); **AC-7's 100%-trace audit
is provisioned-for, NOT discharged** (contingent on that binding — DEP-FD-Fold-2, §3.7).

### 3.7 The deploy doc topology (Q8-A / honest partial-deploy — DOC-1)
The deploy doc records, each behind its DOC-1 marker token: the **live-vs-`501` route split** (`ROUTE-STATUS:` — R1/R6/R7 live, R2–R5
`501`); the **Q1-B divergence** (`Q1-B-DIVERGENCE:` — R6/R7 enforce `READ_AUDIT`, admin 403, deployed **as-built**, not resolved);
**AC-7's contingency** (`AC-7-CONTINGENCY:` — the Langfuse trace audit is provisioned-for but **not dischargeable** until the
composition-owned live callback binding lands); **free-tier** (`FREE-TIER:`); and the **env-shape list** (`ENV-SHAPES:` — §3.5).
**Nothing over-claimed** — validation/staging cloud-readiness, not an end-to-end demo.

---

## 4. `secrets-config` contract (SHAPES only — no values)
`secrets-config` (U16) owns **all key/endpoint/connection VALUES**; this design names only the **variable-name shapes** (§3.5). The
Phase-2 reserved shapes are **authored here** (moved from reserved to named-and-set per BR-SEC-6) but **set-not-consumed** by U23.
**Only variable NAMES appear — never a value.** The rendered migration SQL (role passwords) is never logged (`database` Infra §3.2).

## 5. Reference boundaries (owned elsewhere — named, not authored here)

| Concern | Owner |
|---|---|
| All key/endpoint/connection **VALUES** + the env contract | **`secrets-config`** (U16) |
| The **Postgres topology** (Render free-tier `postgres:16`, grants/role model) + the migration **runner** | **`database`** (U15) |
| The observability **sink code** + the Grafana **panel topology** + the live **callback attachment** | **`observability`** (U21) + **composition** (the callback) |
| The frozen `backend/app` (`create_app`, R1–R7) + `frontend/src/app` + the 17 P1 + U18/U19/U21 | the **CLOSED composition root** + frozen units — **packaged, never edited** |
| The **R2–R5** domain lifecycle; the **Q1-B** reconciliation; the **live callback / MCP** integration code | **Scope B/C** / composition/application |

## 6. Constraints & settled items held (not re-opened)
- FD + approved `NFR-DEP-*` + `P-DEP-1..11` + `C-DEP-1..5` are the substrate — Infra **maps** them, re-opening none. `database`'s +
  `observability`'s Infra passes are **referenced, not re-opened**.
- **BR-DEP-1**: **no frozen unit edited**; the **CLOSED composition root packaged, never edited** (Q3's Vercel rewrite keeps CORS out
  of the backend). **SEC-3**: no key/endpoint/connection **values** — shapes only. **CON-BR1**: no demographic label/metric/panel.
- **AC-7 provisioned-for, not discharged** (Fold / DEP-FD-Fold-2); the **Q1-B divergence** deployed as-built + documented (§3.7); the
  **`OBS-SINK-DEFERRED` code half + `MCP-TRANSPORT-DEFERRED`** stay composition/application-owned.
- **Free-tier only** (NFR-CONSTRAINTS-1); **validation/staging**, not production (NFR-DEPLOY-1 / OOS-4). **No new dependency**;
  `requirements.txt` / `package.json` NOT edited. **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched**
  (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**.
