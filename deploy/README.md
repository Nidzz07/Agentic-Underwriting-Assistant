# Deployment — Agentic Underwriting Assistant (validation/staging)

**Unit**: `deploy-config` (U23, EPIC-6, Phase 2) · **NFR-DEPLOY-1** · free-tier Render + Vercel.
This is a **validation/staging deployment confirming cloud-readiness** — **not** a fully-functional end-to-end demo, and **not**
production (production is Phase-3, OOS-4). Everything below is the honest scope of what deploys and works.

## Topology
- **Backend** — a Render free-tier **Web Service** (`render.yaml`) running the frozen `backend.app.main:app` (Python 3.12,
  `uvicorn`). Boots via the fail-closed `secrets_config.Settings` (the six Phase-1 env shapes must be set).
- **Frontend** — a Vercel free-tier **static build** (`frontend/vercel.json` + Vite) serving the bundle from `frontend/index.html`
  + `frontend/src/main.jsx` (which mounts the frozen `App.jsx`).
- **Connectivity** — the frontend calls **same-origin `/api/*`**; `frontend/vercel.json` **rewrites** those to the Render backend
  (`main.jsx` sets `baseUrl: '/api'`). **No CORS**, and the frozen `backend/app/main.py` is **not edited**.

<!-- ROUTE-STATUS: -->
## ROUTE-STATUS — live vs not-wired
- **LIVE**: `R1 GET /session` · `R6 GET /decisions` · `R7 GET /decisions/{id}` — `ui-history` works end-to-end.
- **NOT WIRED (`501 not_implemented`)**: `R2`/`R3`/`R4` (`/applications*`) · `R5` (`POST /recommendations/{id}/commit`). These are
  honest `501` markers — the queue→memo→commit domain lifecycle is un-designed domain state (Scope B/C), **out of scope for
  deploy-config**. A seam pointed at them resolves the `501` envelope and its unit renders its ordinary error state.

<!-- Q1-B-DIVERGENCE: -->
## Q1-B-DIVERGENCE — R6/R7 authorization
R6/R7 enforce `READ_AUDIT` (underwriter + auditor; **admin → 403**) — which **diverges** from WIRE-1 §3's *"authenticated (any
role)"*. This is deployed **as-built** (the composition root's recorded, still-OPEN divergence) — deploy-config **neither resolves nor
hides it**. Blast radius is nil today (admin has no UI journey), but the divergence is real.

<!-- AC-7-CONTINGENCY: -->
## AC-7-CONTINGENCY — the 100%-trace audit
AC-7 (*"100% of agent steps traced"*, a deploy-time Langfuse trace audit) is **provisioned-for but NOT yet dischargeable**: the live
`langfuse` callback attachment is composition's (`OBS-SINK-DEFERRED` code half), and it is not wired here. This deploy provisions the
substrate AC-7 needs (a Langfuse project + `LANGFUSE_*` env, the Prometheus scrape, the Grafana dashboard) but AC-7 passes only once
that composition-owned binding lands.

<!-- FREE-TIER: -->
## FREE-TIER
Render free-tier Web Service (`plan: free`) + Vercel free-tier static + `database`'s free-tier Postgres + free-tier Prometheus/
Grafana/Langfuse. No paid resource. Validation/staging only.

<!-- ENV-SHAPES: -->
## ENV-SHAPES — variable NAMES only, never values (SEC-3)
Set these in the deploy platform (Render service env / Vercel project env) — **never committed**. Values are owned by
`secrets-config` (SEC-3).

**Phase-1 required** (the fail-closed `Settings`): `DATABASE_URL` · `AUDIT_WRITER_URL` · `AUDIT_READER_URL` ·
`AUDIT_WRITER_PASSWORD` · `AUDIT_READER_PASSWORD` · `GEMINI_API_KEY` (a **dummy** in this LLM-less slice — required-but-unused).

**Phase-2 reserved** (set-not-consumed here; consumed by composition/adapters): `LANGFUSE_PUBLIC_KEY` · `LANGFUSE_SECRET_KEY` ·
`LANGFUSE_HOST` · `ANTHROPIC_API_KEY` · `OLLAMA_HOST`.

**Frontend build** (Vercel): `VITE_USER_ID` (the stub `X-User-Id` shape) · `RENDER_BACKEND_URL` (the rewrite destination — a
**non-secret public host** shape, replace `REPLACE_WITH_RENDER_BACKEND_HOST` in `frontend/vercel.json` + `deploy/prometheus-scrape.yml`).

## MIGRATION (register #8 resolved)
`render.yaml`'s `preDeployCommand` wires **when** the migration sequences run (before traffic), and the **runnable CLI entrypoint now
exists** at `backend/scripts/run_migrations.py`. It is a **cross-unit orchestrator** (deliberately in `backend/scripts/`, not inside a
frozen unit): it builds the owner engine from `secrets-config` (`DATABASE_URL`) and applies **both** forward-only, idempotent sequences —
`database`'s (U15) via its `MigrationRunner`, then `case_lifecycle`'s (U24) via `apply_case_migrations()` (which runs the production
collision guard first). It is **idempotent** (a redeploy applies nothing new) and **fail-loud** (any error is a non-zero exit that blocks
the release step before traffic). `deploy-config` still owns only the **slot** (WHEN it runs); the runner is the entrypoint above.

## Observability deployment half
`deploy/prometheus-scrape.yml` (scrape the backend `/metrics`) + `deploy/grafana-dashboard.json` (one dashboard, **five panels 1:1 to
`observability`'s frozen metrics** — no drift). The live callback attachment stays composition's (above).
