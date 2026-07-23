# Infrastructure Design Plan (Part 1) — `deploy-config` (EPIC-6 / U23, Phase 2)

**Phase / Stage**: BUILD → Infrastructure Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `deploy-config` (U23) · FD ✅ · NFR Requirements ✅ · **NFR Design ✅ (approved 2026-07-19)**
→ **Infrastructure Design ← here (the REAL, comprehensive one — NOT a skip)** → Code Generation.
**Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Date**: 2026-07-19 · **Depth**: **comprehensive** (the wiring-heavy stage).
**Status**: **Plan — awaiting `[Answer]:` tags. NO Infrastructure-Design artifacts generated; no code; no deploy files. Stop after this plan.**

This plan follows `.project-guide-rule-details/build/infrastructure-design.md`, built **ON** the frozen FD (`domain-entities.md`
config surfaces + **BR-DEP-1..9** + the 6-step lifecycle), the approved `nfr-requirements.md` (**eleven `NFR-DEP-*`** +
**DEP-D1..D8**), and the approved NFR Design (`nfr-design-patterns.md` **P-DEP-1..11** + `logical-components.md` **C-DEP-1..5**) —
**re-opening none**. It maps the **deployment topology** the whole U23 stack deferred here. **SEC-3**: no key/endpoint/connection
**VALUES** — only variable-name **shapes** + the `secrets-config` contract.

> **Why this is a real stage (NOT a skip)** — the same four-source convergence discipline `observability` got: **(1)**
> `unit-of-work.md:250` pins U23 *"comprehensive at Infrastructure Design"*; **(2)** FD `domain-entities.md §4` explicitly hands
> Infrastructure Design *"the actual Render/Vercel topology + build commands + env manifest + migration release step + observability
> scrape/dashboard config"*; **(3)** NFR Requirements names BUILD-1/BOOT-1's actual build/boot as *"verified at Infrastructure
> Design/deploy"*; **(4)** NFR Design repeats the deferred-to-Infra list. CLAUDE.md **"Skip IF"** fails on **both** prongs —
> infrastructure changes **exist** (the real Render/Vercel/DB/observability topology) and infrastructure is **not** already defined
> (every prior stage deferred it). This is the **3rd real non-skip Infrastructure Design, after `database` (U15) + `observability`
> (U21)** — both explicitly named as **hand-off sources** here.

---

## 1. Unit context (analyzed)

### 1.1 What Infrastructure Design maps (built ON — NOT re-opened)
- **From NFR Design (C-DEP-1..5)**: the **`deploy_validators`** scan logic (its *shape* fixed; not an infra concern) + the four
  **config artifacts** — `render.yaml` (C-DEP-2), `vercel.json` + the frontend build entry (C-DEP-3), the env manifest (C-DEP-4), the
  deploy doc (C-DEP-5) — whose **actual topology/content** is designed here.
- **From the FD/NFR**: NFR-DEPLOY-1 (validation/staging, Render+Vercel, free-tier); the honest-partial-deploy posture (R1/R6/R7 live,
  R2–R5 `501`, Q1-B documented, AC-7 provisioned-for-not-discharged); SEC-3 shapes-only.

### 1.2 The deferred halves this stage designs (verbatim from the frozen U23 artifacts)
1. **The Render backend service topology** — plan tier, region, runtime, build/start commands, the fail-closed `Settings` env (Q1).
2. **The Vercel frontend project** — build command, output dir, framework preset, the bundler entry (Q2).
3. **Frontend↔backend connectivity** — how the Vercel static frontend reaches the Render backend **without editing the frozen
   composition root** (CORS vs a Vercel proxy/rewrite) (Q3).
4. **Free-tier DB provisioning + the migration release step** — referencing `database`'s Infra; the release-step command (Q4).
5. **The env manifest topology** — how per-env values are set (never committed), the full shape list (Q5).
6. **The observability deployment half** — the Prometheus `/metrics` scrape target, the Grafana dashboard-as-code file's content, the
   Langfuse provisioning + `LANGFUSE_*` env (Q6).

### 1.3 Reference boundaries (owned elsewhere — named, not authored here)
- **`database` (U15) Infra Design** — owns the **Postgres topology** (Render Postgres free-tier, `postgres:16`, the grants/role
  model); deploy-config **wires the connection env + the migration release step** it already named *"a Render release command /
  pre-deploy step (wired by `deploy-config`)"* (`database` Infra §3.4/§5). **Reference-not-own.**
- **`observability` (U21) Infra Design** — owns the **sink code + the Grafana dashboard TOPOLOGY** (`OBS-SINK-DEFERRED` §3 left the
  `/metrics` scrape config + the dashboard-as-code **file** + `LANGFUSE_*` env as a *"Code-Gen/deploy-config deliverable"*); the **live
  callback attachment** stays **composition's** (NOT here). **Reference-not-own.**
- **`secrets-config` (U16)** — owns all key/endpoint **VALUES** + the env contract; this plan names **shapes only** (SEC-3).
- **the CLOSED composition root** (`backend/app/**`, `frontend/src/app/**`) + the 17 P1 + U18/U19/U21 — **packaged, never edited**.

### 1.4 Guardrails held (skill)
NFR-DEPLOY-1 (validation/staging, free-tier); **BR-DEP-1** (no frozen/composition-root edit — the deploy topology packages, never
edits); **SEC-3** (no values — shapes only); **advisory-only** (no domain logic); **no new domain route** (R2–R5 stay `501`).
**tier-B N/A + NOT authorized.** The **`audit_store` Docker-guard gap untouched.**

---

## 2. Mandatory infra-category pre-assessment (all seven — applicability + justification)

| # | Category | Applicability | Where |
|---|---|---|---|
| 1 | **Deployment Environment** | **Applicable (CORE)** — Render backend + Vercel frontend, free-tier, validation/staging (dev/CI/prod tiers) | Q1, Q2 |
| 2 | **Storage Infrastructure** | **Reference (not owned)** — the Postgres is **`database`'s** topology; deploy-config wires the connection + migration release step, does **not** re-provision | Q4 |
| 3 | **Compute Infrastructure** | **Applicable** — the **Render web service** IS the app compute deploy-config provisions; Vercel is static/CDN (no compute) | Q1, Q2 |
| 4 | **Messaging Infrastructure** | **N/A (justified)** — no queue/event bus; a deploy-config unit has no async/eventing concern | Q7 |
| 5 | **Networking Infrastructure** | **Applicable** — frontend↔backend connectivity + managed TLS + the `/metrics` scrape path exposure | Q3, Q6 |
| 6 | **Monitoring Infrastructure** | **Applicable** — the **observability deployment half** (Prometheus scrape target + Grafana dashboard file + Langfuse provisioning) | Q6 |
| 7 | **Shared Infrastructure** | **Narrow (reference)** — deploy-config packages the whole system; the shared Postgres is `database`'s; captured in `deployment-architecture.md`, no separate doc | Q7 |

**No category silently skipped.** Storage is **reference** (database's), Messaging is **N/A-justified**, Shared is **narrow** —
recorded in the completion compliance summary.

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

Letter after each `[Answer]:` tag; if none fit, choose the last (Other) and describe. These decide the **infrastructure mapping** —
they do **not** re-open the FD, the eleven `NFR-DEP-*`, `P-DEP-1..11`, or `C-DEP-1..5`.

## Question 1 — Render backend service topology
How is the backend deployed on Render?

A) **A Render free-tier Web Service**: **Python 3.12** runtime (pinned — matching `.python-version`/`pyproject`); **build command**
   `pip install -r requirements.txt`; **start command** running the frozen `backend.app.main:app` under an ASGI server (e.g.
   `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`, or gunicorn+uvicorn worker — exact server a Code-Gen detail); the
   **six Phase-1 `Settings` env shapes required** (incl. `GEMINI_API_KEY` — a **dummy** value for the LLM-less slice, Scope-A Q5-A);
   managed TLS; validation/staging (not production). **The app is packaged, not edited.**
B) A Docker-based Render service with a custom `Dockerfile` (available if you prefer container parity; heavier than the native
   Python runtime for a free-tier validation deploy — Render's native Python build suffices).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 2 — Vercel frontend project topology
How is the frontend deployed on Vercel?

A) **A Vercel free-tier static build**: **framework preset = Vite** (the bundler deploy-config's build entry uses); **build command**
   `npm run build` (the `build` script deploy-config adds — BR-DEP-2); **output directory** `dist`; the entry (`index.html` + a `main`
   mounting the **frozen `App.jsx`**) produces the static bundle Vercel serves on its CDN; managed TLS; free-tier. **The frozen
   frontend units are composed, never edited.**
B) A non-Vite bundler (e.g. plain esbuild/Rollup config) (available; Vite is the React-standard, integrates with the existing
   `@vitejs/plugin-react` devDep, and needs no new tooling family).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 3 — Frontend↔backend connectivity (WITHOUT editing the frozen composition root)
The Vercel static frontend (one origin) must reach the Render backend (another origin). The frozen `backend/app` has **no CORS
middleware** (and adding it would **edit the CLOSED composition root** — a BR-DEP-1 violation). How is cross-origin resolved?

A) **A Vercel rewrite/proxy** (`vercel.json` `rewrites`): the frontend makes **same-origin** requests (e.g. `/api/*`) that **Vercel
   proxies** to the Render backend — so the browser never makes a cross-origin call, **no CORS is needed, and the frozen backend is
   NOT edited**. The API base URL is a build/env shape. This is a **deploy-config-owned Vercel config** decision that keeps BR-DEP-1
   intact.
B) Add CORS middleware to the backend (rejected — edits `backend/app/main.py`, the CLOSED composition root; BR-DEP-1 hold violation).
C) Serve the frontend from the Render backend as static files (rejected — would edit `backend/app` to mount static; also defeats the
   Vercel deploy NFR-DEPLOY-1 names).
D) Other (describe after [Answer]:)

[Answer]: A

## Question 4 — Database provisioning + the migration release step (reference `database`'s Infra)
How is the DB provisioned and migrated at deploy?

A) **Reference `database`'s Infra topology; wire the release step**: the Postgres is **`database`'s** Render free-tier `postgres:16`
   instance (its topology, not re-designed here); deploy-config **wires the connection env** (`DATABASE_URL` + the role-scoped
   `AUDIT_WRITER_URL`/`AUDIT_READER_URL`, shapes only) and **the migration release step** — a **Render release / pre-deploy command**
   that runs `database`'s **forward-only, idempotent** migration sequence (incl. the grants migration, values from `secrets-config`)
   **before** the app serves traffic (exactly the step `database` Infra §3.4 named *"wired by `deploy-config`"*). **The migration
   runner is `database`'s; deploy-config pins WHEN/HOW it runs in the Render pipeline.**
B) Re-design the Postgres provisioning here (rejected — that is `database`'s owned topology; re-opening it duplicates/contradicts a
   frozen Infra pass).
C) Skip migrations at deploy / run them at app startup (rejected — `database` Infra explicitly rejected startup-migration; races +
   a failed migration blocks startup; an explicit gated release step is the frozen decision).
D) Other (describe after [Answer]:)

[Answer]: A

## Question 5 — Env manifest topology (how per-env values are set — shapes only)
How are env values delivered per environment, and what shapes does the manifest name?

A) **Values set in the platform, never committed** (SEC-3): Render service env (+ optionally a `render.yaml` env-var group for shared
   shapes) for the backend; Vercel project env for the frontend's API base URL. The **manifest names the full shape list** — Phase-1
   required (`DATABASE_URL`, `AUDIT_WRITER_URL`, `AUDIT_READER_URL`, `AUDIT_WRITER_PASSWORD`, `AUDIT_READER_PASSWORD`,
   `GEMINI_API_KEY`) + Phase-2 reserved (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`, `ANTHROPIC_API_KEY`,
   `OLLAMA_HOST`) — **variable NAMES only, never a value**. `GEMINI_API_KEY` gets a **dummy** in the LLM-less slice (Scope-A Q5-A); the
   Phase-2 reserved shapes are **set-not-consumed** by U23 (DEP-FD-Fold-1).
B) Commit a `.env` with real values (rejected — SEC-3; the build fails on a hardcoded secret).
C) Leave the env contract unspecified (rejected — the deploy platforms need the exact shapes to set).
D) Other (describe after [Answer]:)

[Answer]: A

## Question 6 — The observability deployment half (`/metrics` scrape + the Grafana dashboard-as-code file + Langfuse)
`observability`'s `OBS-SINK-DEFERRED` left these as a deploy-config deliverable. What does this stage pin?

A) **The deployment half only** (the code-attachment half stays composition's): **(a)** a **Prometheus scrape job** targeting the
   Render backend's `/metrics` path (a **Grafana Cloud** agent *or* a Render-hosted Prometheus, free-tier); **(b)** the **Grafana
   dashboard-as-code file** — **one dashboard, five panels 1:1 to observability's five frozen metrics** (decision latency · decisions
   by recommendation type · rule-evaluation duration · LLM-call errors · outlier-flag rate), datasource = Prometheus, committed as a
   provisioning JSON (its **topology is observability's**, its **committed file** is this deliverable — Fold-2 of observability's
   Infra); **(c)** a **Langfuse Cloud** project + the `LANGFUSE_*` env set. **The live langfuse callback attachment is NOT wired here**
   (composition's `OBS-SINK-DEFERRED` code half); **AC-7 is provisioned-for, not discharged** (DEP-FD-Fold-2).
B) Wire the live callback attachment too (rejected — edits the CLOSED composition root; that is `OBS-SINK-DEFERRED`'s code half,
   composition-owned).
C) Omit the observability deployment half (rejected — the frozen `OBS-SINK-DEFERRED` explicitly hands the scrape/dashboard/env to
   deploy-config; omitting it drops a named deliverable).
D) Other (describe after [Answer]:)

[Answer]: A

## Question 7 — Compute / Messaging / Storage / Shared (explicit applicability + justification)
How are these categories handled?

A) **Explicit per-category**: **Compute** — the Render Web Service IS the app compute (Q1); Vercel is static/CDN (no compute).
   **Storage** — **reference** `database`'s Postgres topology (Q4), not re-provisioned. **Messaging** — **N/A** (no queue/event bus;
   a deploy unit has no async concern). **Shared** — **narrow/reference** (the shared Postgres is `database`'s; the whole system is
   packaged); captured **within `deployment-architecture.md`**, **no separate `shared-infrastructure.md`**. All recorded in the
   compliance summary.
B) Provision new storage/queue/shared infra here (rejected — none is needed; storage is database's, no messaging exists).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 8 — The deploy doc topology (honest partial-deploy + AC-7 contingency)
What does Infrastructure Design pin for the deploy doc's content (validated by DOC-1)?

A) **The honest partial-deploy topology**: the doc records the **live-vs-`501` route split** (R1/R6/R7 live, R2–R5 `501`), the
   **Q1-B divergence** (R6/R7 `READ_AUDIT`, admin 403 — deployed as-built, not resolved), **AC-7's contingency** (the Langfuse trace
   audit is provisioned-for but **not dischargeable** until the composition-owned live callback binding lands — DEP-FD-Fold-2), the
   **free-tier** posture, and the **env-shape list** — each carrying its DOC-1 marker token. **Nothing over-claimed** (validation/
   staging cloud-readiness, not an end-to-end demo).
B) Document it as a fully-working end-to-end demo (rejected — over-claims; contradicts NFR-DEPLOY-1's validation/staging framing +
   the R2–R5 `501` reality).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 9 — Depth + artifacts + Mermaid
Depth, artifacts, and diagrams?

A) **Comprehensive — two artifacts** at `guide-docs/build/deploy-config/infrastructure-design/`: **`infrastructure-design.md`**
   (the component→infrastructure mapping C-DEP-1..5 + the deferred-halves topology: Render service [Q1], Vercel project [Q2],
   connectivity [Q3], DB + migration release step [Q4], env manifest [Q5], observability deployment half [Q6], the `secrets-config`
   contract shapes-only) and **`deployment-architecture.md`** (the dev/CI/prod topology + the request/deploy flow + the frontend↔
   backend + `/metrics` scrape + the `secrets-config`/`database`/`observability`/composition boundaries). **Validated deployment-
   topology Mermaid** (7 rules, rectangle-only, alphanumeric IDs, quoted labels, no special characters) + **text alternative**. **No
   separate `shared-infrastructure.md`** (Q7-A). **No code; no `backend/deploy_config/`; `requirements.txt`/`package.json` NOT edited;
   no frozen unit edited.**
B) Standard — one artifact, one diagram (rejected — `unit-of-work.md:250` pins comprehensive at Infrastructure Design).
C) Other (describe after [Answer]:)

[Answer]: A

---

## 3.5 Mandatory ambiguity-check (RAN against the nine answers + the frozen U23 stack + database's/observability's Infra) → **CLEAN (3 folds; no surface-and-stop)**

Grounded in U23's FD/NFR-Requirements/NFR-Design + `database`'s Infra (§3.4 migration release step, §5 role-URL contract) +
`observability`'s Infra (`OBS-SINK-DEFERRED §3` + the frozen five-metric panel topology). The three user-flagged checks each resolve:

- **INFRA-DEP-Fold-1 [check i] — Q3's proxied API base URL is a SHAPE, not a SEC-3-flaggable value.** The Vercel rewrite targets the
  Render backend by its **hostname**, which is (a) **not a secret** (a public service URL is not a credential — SEC-3 governs
  keys/passwords/connection-strings-with-credentials, e.g. `postgresql://user:pass@…`, never a bare public host), and (b) modeled as
  a **build/env SHAPE** (e.g. `RENDER_BACKEND_URL` / a `vercel.json` rewrite `destination` placeholder) whose **real value is set in
  the Vercel project env, never committed**. The artifacts name the **shape**, and even if an illustrative host appears it is a
  **non-secret public endpoint placeholder**, not a credential. **SEC-3's secret-value scan (SEC3-1) targets credential patterns**
  (`sk-…`, `postgresql://user:pass@…`), which a public rewrite host is not — no conflict.
- **INFRA-DEP-Fold-2 [check ii] — the migration release step and the env-shapes doc section are consistent about pre-release
  requirements.** The release step (Q4) runs `database`'s migration sequence, which needs — **before it can run** — the
  **schema-owning `DATABASE_URL`** (the owner connection C3's guard validates) **and** the role passwords
  (`AUDIT_WRITER_PASSWORD`/`AUDIT_READER_PASSWORD`) the grants migration substitutes (`database` Infra §3.2/§5). The deploy doc's
  **ENV-SHAPES** section (Q8/DOC-1) lists **exactly these** among the six Phase-1 required shapes, and the release-step wiring states
  the migration runs **after** env is set and **before** traffic (the ordering `database` Infra §3.4 pinned). So the doc's env list
  and the release-step's prerequisites **name the same set** — a shape in the release step's precondition that were missing from the
  doc's list would be the gap; here they **agree** (the six required shapes cover both the app boot and the migration run).
- **INFRA-DEP-Fold-3 [check iii] — the Grafana dashboard-as-code file is pinned to observability's FROZEN five-metric panel topology,
  no drift.** Now that the **committed file** is authored here (not just named), Infrastructure Design ties its panel definitions
  **1:1 to observability's frozen five metrics** (`domain-entities.md §4` / its Infra `deployment-architecture.md §3`): **decision
  latency · decisions by recommendation type · rule-evaluation duration · LLM-call errors · outlier-flag rate**, datasource =
  Prometheus, demographic-free labels (CON-BR1). The artifact **cites observability's topology as the authority** and states the file
  **realizes** it (deploy-config owns the committed file; observability owns the panel topology — reference-not-own), so the file
  **cannot silently drift**: a panel not in observability's five is out of scope, and the five are named explicitly. **This stage
  pins the topology binding; the exact JSON is a Code-Gen deliverable** consistent with it.

**No frozen contract re-opened, no secret value surfaced, no drift from observability's frozen topology.** Proceed to generate Part 2.

---

## 4. Artifacts to generate (after answers + ambiguity-check)
`guide-docs/build/deploy-config/infrastructure-design/` → **`infrastructure-design.md`** (component→infra mapping + deferred-halves
topology + the `secrets-config` shapes-only contract) + **`deployment-architecture.md`** (dev/CI/prod topology + request/deploy flow
+ boundaries). Each with a **validated Mermaid + text alternative**. **No key/endpoint/connection VALUES anywhere** (SEC-3). **No
separate `shared-infrastructure.md`** (Q7-A).

---

## 5. Constraints & settled items held (not re-opened)
- The frozen FD (**BR-DEP-1..9** + config surfaces + the 6-step lifecycle) + the approved **eleven `NFR-DEP-*`** + **P-DEP-1..11** +
  **C-DEP-1..5** are the substrate — Infra **maps** them, re-opening none. **Depth verified: comprehensive at Infra.**
- **BR-DEP-1**: **no frozen unit edited**; the **CLOSED composition root** is **packaged, never edited** (Q3 keeps CORS out of the
  backend via a Vercel rewrite); `database`'s + `observability`'s Infra passes are **referenced, not re-opened**.
- **SEC-3**: no key/endpoint/connection **values** — only variable-name **shapes** + the `secrets-config` contract.
- **AC-7 provisioned-for, not discharged** (DEP-FD-Fold-2); the **Q1-B divergence** deployed as-built + documented (DEP-FD-Fold-3,
  DOC-1); the **`OBS-SINK-DEFERRED` code half + `MCP-TRANSPORT-DEFERRED`** stay composition/application-owned (DEP-FD-Fold-1).
- **Free-tier only** (NFR-CONSTRAINTS-1); **validation/staging**, not production (NFR-DEPLOY-1 / OOS-4). **No new dependency**;
  **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit
  decomposition unchanged**.

---

## 6. Next step (STOP here)
Fill the nine `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check (grounded in the
frozen U23 stack + `database`'s and `observability`'s Infra passes; surfacing-and-stopping on any genuine gap), then generate the two
`deploy-config` Infrastructure Design artifacts (with validated Mermaid + text alternatives) and present the standardized completion
+ 2-option message (1. Request Changes / 2. Continue → **Code Generation**). **No Infrastructure-Design artifacts or code are
generated until the answers are in and checked.**
