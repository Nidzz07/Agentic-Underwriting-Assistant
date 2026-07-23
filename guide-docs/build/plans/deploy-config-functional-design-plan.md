# Functional Design Plan (Part 1) — `deploy-config` (EPIC-6 / U23, Phase 2)

**Phase / Stage**: BUILD → Functional Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `deploy-config` (U23) **STARTED** → **FD ← here (the 1st of its 5 stages)**.
**Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Date**: 2026-07-19 · Story **US-PLAT-11** · NFR-DEPLOY-1.
**Status**: **Plan — awaiting `[Answer]:` tags. NO FD artifact generated; no code; `deploy-config`/root deploy files NOT created. Stop after this plan.**

DISCOVER-carryover check: greenfield P2, no reverse-engineering, **NO prior U23 artifacts** (`guide-docs/build/deploy-config/`
and `backend/deploy_config/` both **absent** — verified). Frozen substrate re-read on disk (re-derived none): the U23
definition + edges + classification; NFR-DEPLOY-1; the composition-root Scope-A integration summary; the app code that exists to
deploy; and the three open register items that name `deploy-config`.

---

## 1. Unit context (analyzed — NOT re-opened)

### 1.1 The frozen definition + classification (VERIFIED, not assumed)
- **`unit-of-work.md:250`**: U23 = *"**validation** deploy on Render + Vercel, free-tier (distinct from Phase-3 production).
  US-PLAT-11. NFR-DEPLOY-1. **Depth: comprehensive at Infrastructure Design.**"*
- **`unit-of-work.md:262`**: `deploy-config` is listed among the **pure-wiring "lighter candidates"** — lighter **except** at
  Infrastructure Design. ⇒ **verified split classification: FD depth = LIGHTER (recommended); comprehensive reserved for
  Infrastructure Design** (the same pattern as `observability` U21 and `database` U15 — assessed at that stage, not pre-committed).
- **`NFR-DEPLOY-1`** (`requirements.md:193`): *"Deploy a working demo to **Render (backend) + Vercel (frontend)** as a
  **validation/staging deployment confirming cloud-readiness**."* **OOS-4**: **production** cloud deploy is **Phase 3**; the
  validation/staging deploy is Phase 2. **NFR-CONSTRAINTS-1**: open-source + **free-tier only**.

### 1.2 Dependency edges (frozen)
- **`unit-of-work-dependency.md:52`**: `deploy-config` depends on **`database`, all `backend/*`, all `frontend/*`** — it
  *"packages the validation deploy (Render + Vercel)"*; **`:200`** — the P2 wrap-units *"wrap the built system."* The edge is a
  **PACKAGING** relationship over the already-built system, not an application-integration relationship.

### 1.3 What already exists to deploy (verified on disk)
- **Backend** `backend/app/` (composition-root Scope A, **frozen for this pass**): `create_app()` + `app`; **R1/R6/R7 REAL**
  (`GET /session`, `GET /decisions`, `GET /decisions/{id}`); **R2–R5 = explicit `501 not_implemented` markers**
  (`routes/not_wired.py`). Boots via `secrets_config.Settings` **fail-closed** (all six Phase-1 vars required, incl.
  `GEMINI_API_KEY` — required-but-unused, a dummy satisfies it, Scope-A Q5-A).
- **Frontend** `frontend/src/`: React 18 author-only modules + `frontend/src/app/` (Scope A). **NO build entry** — no
  `index.html`, no `main.jsx`, no `vite.config.js`, **no `build` script** (only `vitest`/`eslint`). **Scope-A §9 verbatim**:
  *"The frontend **cannot run in a browser** — no bundler; **`deploy-config` (U23, P2) owns that** and was deliberately not
  pulled forward."* ⇒ the **frontend bundler/build is squarely U23's**.
- **No root deploy files** (`render.yaml`/`vercel.json`/`Dockerfile`/`Procfile` — all absent; correct).

### 1.4 Guardrails held (skill)
NFR-DEPLOY-1 (validation/staging, free-tier); **SEC-3** (no secret/key/URL **values** in artifacts — only variable-name shapes);
**no frozen unit edited** (the composition root is CLOSED for this pass; the 17 P1 units + U18/U19/U20/U21 frozen); **advisory-only**
(deploy-config wires no domain logic); **no new domain route** (R2–R5 stay 501 markers). **tier-B N/A + NOT authorized.** The
**`audit_store` Docker-guard gap untouched.**

---

## 2. Decisive scope findings (the three register items + Scope A §9 — triaged, NOT resolved here)

**`deploy-config` is the convergence point MULTIPLE frozen units named for env/pipeline wiring** — this is strong grounding that
its scope is **deployment pipeline / topology / env-wiring / build**, NOT application-integration code:

| Frozen hand-off TO deploy-config | Source | In U23's config scope? |
|---|---|---|
| Render release / pre-deploy **migration-run step** + runtime **role-connection env wiring** (`AUDIT_WRITER_URL`/`AUDIT_READER_URL`, `DATABASE_URL`) | `database` Infra Design §5/§6 | **Yes (env/pipeline)** — shapes only, SEC-3 |
| The Prometheus **`/metrics` scrape config** + the **Grafana dashboard-as-code file** + the **`LANGFUSE_*` env values** | `observability` `OBS-SINK-DEFERRED` §3 | **Deployment half: yes** (scrape/dashboard/env). **Code-attachment half: composition's** (see Q1) |
| The reserved Phase-2 env-var **shapes** (`LANGFUSE_*`, `ANTHROPIC_API_KEY`, `OLLAMA_HOST`) | `secrets-config` `.env.example` (BR-SEC-6) | **Yes (env wiring)** — deploy-config sets real per-env values; shapes only in artifacts |
| The **frontend bundler / browser-runnable build** | Scope-A §9 (explicit) | **Yes — squarely U23's** |
| **R2–R5 route wiring** (the core queue→memo→commit path) | Scope-A §9 | **NO — un-designed domain state, Scope B/C** (see Q2) |
| The **live MCP transport binding** | `MCP-TRANSPORT-DEFERRED` (U19) | **Application-integration code — NOT deploy-config's** (see Q1) |
| The **composition-root Q1-B divergence** | Scope-A §3 | **NO — a contract-reconciliation decision, separately owned** |

**Scope-A §9 (verbatim, load-bearing)**: R2–R5 *"stay unbacked because the pending-application/recommendation lifecycle is
**un-designed domain state, which belongs in its own stage (Scope B/C), not smuggled into a wiring pass**."* The frozen
decomposition therefore **already decided deploy-config proceeds WITHOUT R2–R5** — so U23 is **not** blocked on them.

---

## 3. Proposed FD structure (LIGHTER depth) + layout OPEN

At lighter depth the FD pins **WHAT deploy-config is** (a deployment-packaging/config unit that wraps the built system for a
free-tier Render+Vercel validation deploy) and its **scope boundary** — deferring the actual Render/Vercel topology, build
commands, env manifests, the migration release step, and the observability scrape/dashboard config to **Infrastructure Design
(comprehensive)**. The **artifact/layout is OPEN** — `unit-of-work.md` names `deploy-config` but enumerates no files; a
deployment-config unit is largely **declarative** (`render.yaml`/`vercel.json`/build config/env manifest) and may need **no
`backend/deploy_config/` Python package** at all (unlike prior wiring units) — a Q5 decision, finalized at Infra/Code-Gen.

The FD would produce (lighter 3-artifact set, on approval): `domain-entities.md` (the unit's config surfaces + the
reference-not-own boundary + the deferred-to-Infra list), `business-rules.md` (**BR-DEP-\*** checkable invariants — no frozen
edit; no domain route wired; SEC-3 shapes-only; free-tier; the honest partial-deploy documentation; the frontend build produces
a static bundle Vercel serves; the backend boots via fail-closed `Settings`), `business-logic-model.md` (the deploy lifecycle +
a validated Mermaid).

---

## 4. Clarifying questions (fill each `[Answer]:` tag)

Letter after each `[Answer]:` tag; if none fit, choose the last (Other) and describe. These decide the **scope boundary** — they
do **not** re-open any frozen contract.

## Question 1 — Is deploy-config's scope the deployment pipeline/topology ONLY, or ALSO the live sink-binding integration code?
`OBS-SINK-DEFERRED` and `MCP-TRANSPORT-DEFERRED` name deploy-config among their discharge points — but "deployment config" (env
wiring, service provisioning, build steps) and "application integration" (attaching the langfuse callback in `main.py`, binding
the MCP transport in the memo flow) are **genuinely different scopes**.

A) **Deployment pipeline / topology / env-wiring / build ONLY** (the packaging reading, `:52`/`:200`): deploy-config owns the
   **deployment half** of the deferred items — provisioning Render+Vercel+Prometheus+Grafana on free-tier, the `/metrics`
   **scrape config**, the **Grafana dashboard-as-code file**, the **migration release step**, and **env wiring** (setting the
   real `LANGFUSE_*` / role-URL / `DATABASE_URL` values, **shapes only in artifacts**, SEC-3). It does **NOT** write
   application-integration code: the live langfuse **callback attachment** and the per-internal-graph-node passthrough live at the
   **composition root** (CLOSED this pass); the **MCP transport binding** is **application-integration code** owned by
   composition/memo-extensions' consumer — **NOT deploy-config**. So `OBS-SINK-DEFERRED`'s deployment half is dischargeable here;
   its code-attachment half and `MCP-TRANSPORT-DEFERRED` remain **separately owned even after U23 exists**.
B) **Full discharge** — deploy-config also writes the live callback/MCP integration code (rejected — that edits the CLOSED
   composition root / frozen units; contradicts `:52`'s packaging scope; conflates config with application logic).
C) **Even narrower** — only Render+Vercel process config, with all observability/env wiring left to a further pass (rejected —
   the frozen hand-offs from `database`/`observability`/`secrets-config` explicitly name deploy-config for the env/scrape/dashboard
   half).
D) Other (describe after [Answer]:)

[Answer]: A

## Question 2 — Does deploy-config complete the composition root's remaining unwired routes (R2–R5)?
R2–R5 are `501` markers (the core queue→memo→commit path). Is finishing that wiring in scope here?

A) **Explicitly OUT of scope** (Scope-A §9, verbatim): R2–R5 are *"un-designed domain state ... belongs in its own stage
   (Scope B/C), not smuggled into a wiring pass."* deploy-config is a **deployment-config** unit, not application logic; it deploys
   the system **as it stands** (R1/R6/R7 real, R2–R5 honest `501` markers). Completing R2–R5 is a **separate future decision**
   (Scope B/C domain-state design), **not** U23's — and **not a blocking dependency** for U23 (see Q3).
B) In scope — deploy-config finishes R2–R5 as part of "making the demo work" (rejected — invents un-designed domain state; edits
   the closed composition root; contradicts Scope-A §9 and U23's packaging scope).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 3 — Deploy the system AS IT STANDS (partial, documented), or is deployability contingent on more wiring first?
The core demo path can't run end-to-end even after Scope A (R2–R5 are `501`). Is that a **documented limitation** of the validation
deploy, or a **blocking dependency** this FD must name and stop behind?

A) **Deploy the system as it currently stands, with the partial-runnability clearly documented — NOT contingent, NOT blocked.**
   NFR-DEPLOY-1 is a **"validation/staging deployment confirming cloud-readiness"** — not a fully-functional end-to-end demo. The
   current slice (R1/R6/R7 real + `ui-history` end-to-end + R2–R5 honest `501`s) **is** deployable and **validates cloud-readiness**
   (the backend boots on Render via fail-closed `Settings`, the DB connects, the frontend builds+serves on Vercel, the wired routes
   answer). The FD **documents** the partial scope explicitly (which routes are live, which return `501`). The frozen edge
   (deploy-config depends on the **built system as-is**) + Scope-A §9 (bundler assigned to U23, R2–R5 left to Scope B/C) together
   confirm the decomposition **intends** U23 to proceed now.
B) **Contingent/blocked** — deployability requires R2–R5 (Scope B/C) first, so this FD must name it as a blocking dependency and
   stop (rejected — contradicts NFR-DEPLOY-1's validation/staging framing and the frozen edge that U23 depends only on already-built
   units; would strand the last-but-one P2 unit on un-designed domain state).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 4 — Are the depth classification, the dependency edges, and PROJECT-BRIEF's "Working deployed demo" language mutually consistent about what "done" looks like?
Cross-check (the same rigor applied to observability's Infra classification): **NFR-DEPLOY-1** = *"validation/staging ... confirming
cloud-readiness"*; **Brief §7.1** deliverable header = *"Working deployed demo — Render + Vercel"*; **OOS-4** = production deploy is
Phase 3. Do these agree on "done"?

A) **Consistent under the validation-deploy reading — the frozen NFR governs the looser Brief header.** "Done" for U23 =
   **the current system deployed and reachable on Render/Vercel free-tier, wired routes (R1/R6/R7) working, unwired routes returning
   their honest `501` markers, all documented** — i.e. cloud-readiness validated, not every route functional. **⚑ Surfaced phrasing
   tension (not improvised)**: Brief §7.1's *"Working deployed demo"* is the **looser** wording; **NFR-DEPLOY-1** tightens it to
   *"validation/staging deployment confirming cloud-readiness"*, and **OOS-4** puts full production behind Phase 3 — so the three are
   consistent once the frozen NFR's precise language is taken as governing (Brief §7 is the deliverable list, NFR-DEPLOY-1 is the
   testable requirement). The FD records this reading explicitly.
B) **Genuinely inconsistent** — "Working deployed demo" demands end-to-end functionality that the current slice can't provide, so
   the artifacts conflict and this FD must surface-and-stop (rejected — NFR-DEPLOY-1 + OOS-4 + Scope-A §9 resolve the tension
   without conflict; "working" scopes to the wired slice + a proven pipeline, not every route).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 5 — FD depth + artifact set + module/layout
Depth and the FD deliverables?

A) **LIGHTER FD** (per `:250`/`:262` — comprehensive reserved for Infrastructure Design), the standard **lighter 3-artifact set**
   (`domain-entities.md` + `business-rules.md` **BR-DEP-\*** + `business-logic-model.md` with a validated Mermaid + text
   alternative). The **module/layout is OPEN** — a deployment-config unit is largely **declarative** (`render.yaml`/`vercel.json`/
   frontend build config/env manifest at the workspace root) and **may need no `backend/deploy_config/` Python package**; the exact
   deliverable set is pinned at **Infrastructure Design (comprehensive) / Code-Gen**, not here.
B) Comprehensive FD now (rejected — `unit-of-work.md:250` pins comprehensive **at Infrastructure Design**, not at FD; over-invests
   the design-what stage).
C) Other (describe after [Answer]:)

[Answer]: A

---

## 4.5 Mandatory ambiguity-check (RAN against the five answers + the frozen substrate) → **CLEAN (3 folds; no surface-and-stop)**

Grounded in NFR-DEPLOY-1 + OOS-4 + the dependency edges + Scope-A `integration-summary.md` §3/§9 + the frozen hand-offs from
`database`/`observability`/`secrets-config`, and AC-7's exact text (`requirements.md:238` — *"Observability · 100% of agent steps
traced · Langfuse trace audit"*). The three user-flagged checks each resolve against a frozen fact:

- **DEP-FD-Fold-1 [check i] — every named deferred item is resolved on ONE side; no gray area survives.** All four halves land
  cleanly on the **env-wiring/provisioning vs consumption-code** line: **(1)** `OBS-SINK-DEFERRED` deployment half (provision
  Langfuse/Prometheus/Grafana free-tier · `/metrics` **scrape config** · the **Grafana dashboard-as-code FILE**, which
  `observability` Infra explicitly left as a *"Code-Gen/deploy-config deliverable, home named-not-created"* · **set** the
  `LANGFUSE_*` env values) → **deploy-config**. **(2)** `OBS-SINK-DEFERRED` code-attachment half (the live langfuse **callback
  attachment** in `main.py` + the per-internal-graph-node passthrough) → **composition (CLOSED)**, NOT deploy-config. **(3)**
  `MCP-TRANSPORT-DEFERRED` (the live MCP protocol binding in the memo flow) → **application-integration code**, NOT deploy-config.
  **(4)** the reserved `secrets-config` shapes: **the split is set-vs-consume, not item-vs-item** — deploy-config **SETS** every env
  shape in the deploy environment (`LANGFUSE_*`, and the reserved `ANTHROPIC_API_KEY`/`OLLAMA_HOST` for the Claude/Ollama adapters),
  while the **code that CONSUMES** them (the provider adapters, the langfuse SDK read) is composition/application's. The migration
  **release-step wiring** (`database` hand-off) is likewise env/pipeline (deploy-config) while the migration **runner** is a
  `database` Code-Gen deliverable. So the ANTHROPIC/OLLAMA/LANGFUSE env vars are set-but-not-necessarily-consumed in the current
  slice — the same clean split, not a gray area.
- **DEP-FD-Fold-2 [check ii] — AC-7 is PROVISIONED-FOR but NOT dischargeable by deploy-config in the current slice; it is
  observability/AC-7-owned and contingent on a deferred composition binding.** AC-7 (*"100% of agent steps traced"*, a **deploy-time
  Langfuse trace audit**) can only fire once **live traces flow**, which requires the langfuse **callback attachment** — the
  **composition-owned code-attachment half of `OBS-SINK-DEFERRED`** (DEP-FD-Fold-1, deferred). So deploy-config's pipeline
  **provisions the substrate AC-7 needs** (the Langfuse backend + `LANGFUSE_*` env), but AC-7's **actual pass is contingent on the
  deferred composition binding** and is **not** deploy-config's acceptance to assert. In the current validation deploy AC-7 is
  therefore **not yet dischargeable** — recorded as part of the **honest partial-runnability documentation** (Q3-A). No conflict:
  AC-7 is a trace-completeness audit (not a route), owned by observability/AC-7, provisioned-for here.
- **DEP-FD-Fold-3 [check iii] — the Q1-B divergence is deployed AS-BUILT and DOCUMENTED, not resolved or hidden.** deploy-config
  packages R1/R6/R7 with their **as-built** behavior — R6/R7 enforce `READ_AUDIT` (admin→403), which diverges from WIRE-1 §3's
  *"authenticated (any role)"* (Scope-A §3, **still OPEN**, **separately owned**, plan §2 table). So deploy-config documents R1/R6/R7
  as *"working per the as-built composition-root behavior"* and **names the Q1-B divergence as a carried-open item** affecting R6/R7
  admin authz — it **neither resolves nor obscures it** (honest-partial-deploy rule, BR-DEP-7). deploy-config deploys the code that
  has the divergence; the reconciliation stays composition/contract-owned.

**No frozen contract re-opened, no scope smuggled in, no secret value surfaced.** Proceed to generate the lighter FD artifact set.

---

## 5. Constraints & settled items held (not re-opened)
- The frozen U23 definition + NFR-DEPLOY-1 + the dependency edges + Scope-A's integration summary are the substrate — the FD
  **maps** them, re-opening none. **Depth verified (not assumed): lighter FD, comprehensive Infra.**
- **No frozen unit edited**: the **CLOSED composition root** (`backend/app/**`, `frontend/src/app/**`) + the 17 P1 units +
  `outlier-model` (U18) / `ui-outlier-view` (U20) / `memo-extensions` (U19) / `observability` (U21) — **untouched**.
- **No new domain route / no domain state invented**: R2–R5 stay `501` markers (Q2); the pending-application lifecycle is Scope B/C.
- **SEC-3 / BR-SEC-6**: no secret/key/URL **values** — only variable-name **shapes** + the `secrets-config` contract.
- **NFR-CONSTRAINTS-1**: free-tier only; **NFR-DEPLOY-1**: validation/staging (production is Phase-3 OOS-4).
- The **composition-root Q1-B divergence** stays OPEN and separately owned (not resolved here). **`OBS-SINK-DEFERRED`'s
  code-attachment half + `MCP-TRANSPORT-DEFERRED`** remain composition/application-owned (Q1).
- **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit
  decomposition unchanged** (deploy-config is a numbered unit; the composition root is not).

---

## 6. Next step (STOP here)
Fill the five `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check (grounded in the
frozen NFR-DEPLOY-1 + Scope-A §9 + the `database`/`observability`/`secrets-config` hand-offs; surfacing-and-stopping on any genuine
gap), then generate the lighter FD artifact set (with validated Mermaid + text alternative) and present the standardized 2-option
completion message (1. Request Changes / 2. Continue → **NFR Requirements**). **No FD artifacts or code are generated until the
answers are in and checked.**
