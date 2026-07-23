# Code Generation Plan (Part 1) — `deploy-config` (EPIC-6 / U23, Phase 2)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `deploy-config` (U23) · FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure Design ✅ (approved 2026-07-19)**
→ **Code Generation ← here (the 5th and LAST of U23's 5 stages)**.
**Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Date**: 2026-07-19 · **Depth**: **comprehensive**.
**Status**: **Plan — awaiting `[Answer]:` tags. NO code/config generated; no files created. Stop after this plan.**

Built **ON** the frozen FD (**BR-DEP-1..9**), the approved `nfr-requirements.md` (**eleven `NFR-DEP-*`** + **DEP-D1..D8**), the approved
NFR Design (**P-DEP-1..11** + **C-DEP-1..5**), and the approved Infrastructure Design (`infrastructure-design.md` +
`deployment-architecture.md`, **INFRA-DEP-Fold-1..3**) — **re-opening none**. **This is the stage where DEP-D8's "layout OPEN"
deferral finally resolves into concrete filenames/locations.**

---

## 1. Grounding resolved on disk (the DEP-D8 deferrals)
- **`frontend/package.json` explicitly reserves the bundler for U23**: its own description reads *"Bundler/dev-server + Vercel
  topology deferred to deploy-config (D6)."* — so adding the frontend build entry + a `build` script is the **sanctioned** deploy-config
  deliverable, **not** a frozen-unit edit (`package.json` is shared project config, like the `vitest.config.js`/`eslint.config.js` the
  composition-root pass extended).
- **`vite` is ALREADY installed** (`frontend/node_modules/.bin/vite` present, transitive via `vitest`) ⇒ **NO new frontend dependency**;
  U23 adds a `build` script + a `vite.config.js` + `index.html` + a `main` entry.
- **`pytest testpaths = ["backend"]`** ⇒ the `deploy_validators` scans must live **under `backend/`** to be collected by the existing
  run. Resolution (Q1/Q6): a **test-only** `backend/deploy_config/` package (no production `.py` modules — the deployable artifacts are
  the declarative config files at their platform-conventional homes).
- **`.env.example` is `secrets-config`'s frozen artifact** (already reserves the Phase-2 `LANGFUSE_*`/`ANTHROPIC_API_KEY`/`OLLAMA_HOST`)
  — U23 **references it, never edits it**; the deploy env shapes are declared in `render.yaml` (names only) + the deploy doc.

---

## 2. Component → artifact map (DEP-D8 RESOLVED — final locations, Q1)

| Component | Final artifact(s) — proposed (Q1) | Kind |
|---|---|---|
| **C-DEP-2 `render.yaml`** | **`render.yaml`** at the **repo root** (Render Blueprint convention) — a `web` service: `env: python`, `buildCommand: pip install -r requirements.txt`, `startCommand: uvicorn backend.app.main:app …`, `plan: free`, `preDeployCommand` (the migration release step), `envVars` (names only, `sync: false`) | config (YAML) |
| **C-DEP-3 `vercel.json` + build entry** | **`frontend/vercel.json`** (build + `rewrites` `/api` → `RENDER_BACKEND_URL`) + **`frontend/index.html`** + **`frontend/src/main.jsx`** (mounts the **frozen `App.jsx`**) + **`frontend/vite.config.js`** + a **`build` script** added to `frontend/package.json` | config (JSON) + build entry (JS/HTML) |
| **C-DEP-4 env manifest** | the **`render.yaml` `envVars` block** (Phase-1 six + Phase-2 reserved, **names only**) + the deploy doc's **ENV-SHAPES** section; **references frozen `.env.example`**, never edits it | config (declared in render.yaml + doc) |
| **C-DEP-5 deploy doc** | **`deploy/README.md`** (the honest partial-deploy doc, DOC-1 tokens) | doc (Markdown) |
| **observability deployment half** | **`deploy/grafana-dashboard.json`** (one dashboard, 5 panels 1:1 to observability's frozen metrics) + **`deploy/prometheus-scrape.yml`** (or a scrape note referencing the Render `/metrics` target) | config (JSON/YAML) |
| **C-DEP-1 `deploy_validators`** | **`backend/deploy_config/`** — `__init__.py` + `tests/{__init__.py, structural.py, test_*.py}` (**test-only**; no production `.py`) | scan logic (pytest) |

**No production Python package for the deploy artifacts** (they are declarative config); `backend/deploy_config/` exists **only** to
house the pytest-collected scans (DEP-D8 resolved). Exact filenames confirmable via Q1.

---

## 3. TDD test → target map (all eleven `NFR-DEP-*` at their NFR-pinned tier — NO ORPHAN)

Tests live in `backend/deploy_config/tests/`, mirroring the sibling `structural.py` substrate + per-target `test_*.py` convention.

| Target | Tier / rigor | Test file | Teeth |
|---|---|---|---|
| **NOEDIT-1** | **LOAD-BEARING full-highest** | `test_noedit.py` | `pathlib` scan — U23-authored paths ⊆ the allowed set (root `render.yaml`, `frontend/{vercel.json,index.html,src/main.jsx,vite.config.js}`, `deploy/*`, `backend/deploy_config/*`) + `frontend/package.json`'s `build` script only; **no write under any frozen `backend/<unit>/`/`frontend/src/<unit>/` tree or `backend/app/**`/`frontend/src/app/**`**; **detector self-test** (synthetic frozen-path write flagged) |
| **SEC3-1** | **LOAD-BEARING full-highest** | `test_sec3.py` | secret-value regex over **every committed U23 artifact** (Q4) — no `sk-…`/`postgresql://user:pass@…`/key literal; the **public `RENDER_BACKEND_URL` host is permitted** (Fold-1); **detector self-test** (synthetic `LANGFUSE_SECRET_KEY="sk-…"` + `postgresql://user:pass@host` flagged, bare name permitted) |
| **ROUTES-1** | **LOAD-BEARING full-highest** | `test_routes.py` | `create_app().openapi()["paths"]` **in-process, no server/DB/env** (reusing the composition-root technique, Req-Fold-1/Fold-3) — == R1/R6/R7 + the four R2–R5 markers; **no new route file** under `backend/app/`; **detector self-test** (synthetic extra route flagged) |
| **DOC-1** | standard | `test_doc.py` | token-set checklist over `deploy/README.md` — every required token present (Q3); matches the **token set, not headings/prose**; **detector self-test** (removed token flagged) |
| **BUILD-1** | standard | `test_build.py` | **(a) presence/reference** — `frontend/{index.html,src/main.jsx,vite.config.js}` exist, `main.jsx` imports the **frozen `App.jsx` unmodified**, `package.json` has a `build` script; **(b) named deploy-time fact** — the actual bundle build is *verified at deploy, observed-never-gated* (no tier-U teeth) |
| **BOOT-1** | standard | `test_boot.py` | **(a) presence** — `render.yaml` start command targets `backend.app.main:app` + `envVars` lists the six Phase-1 shapes; **(b) named deploy-time fact** — the actual boot is deploy-time (no tier-U teeth) |
| **FREETIER-1** | standard | `test_freetier.py` | config-token scan — `plan: free` (render) + Vercel free-tier; no paid-tier token; **detector self-test** (synthetic paid token flagged) |
| **SCOPE-1** | standard | `test_scope.py` | structural scan — the observability deployment half present (`deploy/grafana-dashboard.json` + scrape + `LANGFUSE_*` in `render.yaml`); **no** callback-attachment into `backend/app/main.py`, **no** MCP module; env **set-not-consumed**; **detector self-test** |
| **(format)** | supporting | `test_format.py` | `render.yaml` parses via `pyyaml` + names expected keys; `frontend/vercel.json` + `deploy/grafana-dashboard.json` parse via stdlib `json` (P-DEP-8) |
| **ADVISORY-1 + SEC-1** | governance | `test_governance.py` | no `Recommendation`/verdict token in any U23 artifact; the Security-Guardrails posture (SEC-3 machine-checked by `test_sec3.py`) |
| **PERF-1** | soft/observed | *(folded)* | no runtime SLO owned; observed-never-gated (a note in `test_governance.py`) |

**Fold-3 grounding for `deploy/grafana-dashboard.json`**: `test_scope.py` (or a dedicated assertion) verifies the dashboard's panels
are **exactly** observability's frozen five (decision latency · decisions by recommendation type · rule-evaluation duration · LLM-call
errors · outlier-flag rate) — **no sixth panel, no drift**; datasource Prometheus; demographic-free labels.

---

## 4. Leaf-first build order (TDD, per artifact)
0. **`backend/deploy_config/tests/structural.py`** substrate (repo-root path helpers, committed-artifact enumeration, secret/token
   scanners, `pyyaml`/`json` parse, `create_app().openapi()` reader, the detector-self-test harness) + `__init__.py`s.
1. **`render.yaml`** (root) → `test_boot.py` + `test_freetier.py` + `test_format.py` teeth.
2. **`frontend/` build entry** (`index.html` + `src/main.jsx` mounting frozen `App.jsx` + `vite.config.js` + `vercel.json` + the
   `package.json` `build` script) → `test_build.py` teeth.
3. **`deploy/grafana-dashboard.json`** + the scrape config → `test_scope.py` (+ the Fold-3 five-panel assertion).
4. **`deploy/README.md`** (references render.yaml/vercel.json content) → `test_doc.py` token-set teeth.
5. **The load-bearing scans** across all artifacts → `test_noedit.py`, `test_sec3.py`, `test_routes.py` (+ detector self-tests) →
   `test_governance.py`.
6. **Coverage / quality gate** (§7).

---

## 5. Clarifying questions (fill each `[Answer]:` tag) — Code-Gen-only realization choices

## Question 1 — Final file locations (DEP-D8 resolves here)
Where do the five components' files live?

A) **As in §2**: `render.yaml` at **repo root** (Render Blueprint convention); the Vercel config + build entry under **`frontend/`**
   (`vercel.json`, `index.html`, `src/main.jsx`, `vite.config.js`) + a `build` script in `frontend/package.json`; the deploy doc +
   observability deployment-half files under **`deploy/`** (`README.md`, `grafana-dashboard.json`, `prometheus-scrape.yml`); the env
   shapes declared in `render.yaml` `envVars` + the deploy doc (referencing frozen `.env.example`, never editing it); the
   `deploy_validators` scans in a **test-only `backend/deploy_config/`** (collected by `testpaths=["backend"]`).
B) A single top-level `deploy/` holding render.yaml + vercel.json too (rejected — Render Blueprint expects `render.yaml` at repo root;
   Vercel expects `vercel.json` at the frontend project root).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 2 — The frontend build entry + the `package.json` `build` script (BUILD-1)
`frontend/package.json`'s description reserves the bundler for deploy-config; `vite` is already installed. What does Code-Gen add?

A) **Add the build entry + a `build` script — no new dependency**: `frontend/index.html` + `frontend/src/main.jsx` (mounting the
   **frozen `App.jsx`**, unmodified) + `frontend/vite.config.js` (React plugin, output `dist`) + a **`"build": "vite build"` script** in
   `frontend/package.json`. **`vite` is already present** (transitive via `vitest`) — no new dependency; adding the script to the
   shared `package.json` is the **sanctioned** deploy-config deliverable its own description reserves, **not** a frozen-unit edit.
B) Add `vite` as an explicit devDependency too (available; harmless but unnecessary — it already resolves; a Code-Gen nicety, not a
   correctness need).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 3 — Exact DOC-1 token literals
What are the required marker tokens the deploy doc must carry?

A) **`ROUTE-STATUS:` · `Q1-B-DIVERGENCE:` · `AC-7-CONTINGENCY:` · `FREE-TIER:` · `ENV-SHAPES:`** — each a literal anchor the doc
   carries (under a canonical heading); `test_doc.py` asserts the **token set** is present (not headings/prose), with a detector
   self-test.
B) A different token scheme (available; A matches the NFR Design / Infra `§3.7` naming already recorded).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 4 — Exact SEC3-1 secret-value regex patterns
What patterns does the secret-value scan flag (and what does it permit)?

A) **Flag**: `sk-[A-Za-z0-9]` / `pk-[A-Za-z0-9]` (key literals) · `postgresql://<user>:<pass>@` (credential-bearing connection
   string) · `<NAME>=<non-empty-value>` for any known secret NAME in a committed file. **Permit**: a bare variable NAME shape
   (`LANGFUSE_SECRET_KEY` with no value / `sync: false`) · the **public `RENDER_BACKEND_URL` host** (a non-secret endpoint, Fold-1).
   Detector self-test: a synthetic `LANGFUSE_SECRET_KEY="sk-…"` + `postgresql://user:pass@host` flagged; a bare name + a public host
   NOT flagged (non-vacuity of the permit).
B) A stricter/looser pattern set (available; A is grounded in Fold-1's credential-vs-public-host distinction).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 5 — The `render.yaml` / `vercel.json` config key structures
What key structure do the two platform configs use?

A) **`render.yaml`**: `services:` → one `- type: web`, `env: python`, `plan: free`, `buildCommand: pip install -r requirements.txt`,
   `startCommand: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`, `preDeployCommand:` (the migration release step invoking
   `database`'s runner), `envVars:` (the Phase-1 six + Phase-2 reserved, each `sync: false` — **names only, no values**). **`vercel.json`**:
   `buildCommand: npm run build`, `outputDirectory: dist`, `rewrites: [{ source: "/api/(.*)", destination: "$RENDER_BACKEND_URL/..." }]`
   (the same-origin proxy, Fold-1). Exact field spellings verified against the platforms' current schema at generation.
B) Other (describe after [Answer]:)

[Answer]: A

## Question 6 — `deploy_validators` test integration + what "coverage" means for a declarative unit
How do the scans run, and what is the coverage/quality gate?

A) **The scans integrate into the EXISTING backend pytest run** (`backend/deploy_config/tests/` is collected by `testpaths=["backend"]`)
   — **no separate test convention**. **No `--cov=backend/deploy_config` line is added**: the package has **no production `.py`** to
   measure (the substrate is under `tests/`, omitted by `*/tests/*`), so a coverage percentage does **not** meaningfully apply here.
   The **quality gate is that the scans PASS against the actual committed artifacts** (the config validation IS the test), and the
   global `--cov-fail-under=90` **holds unchanged** (U23 adds passing tests + no uncovered production lines). **Baseline 1153 passed /
   31 skipped → additive, zero regression.**
B) Add a `--cov=backend/deploy_config` line anyway (rejected — nothing to measure; would report a meaningless 0/100% and muddy the
   gate).
C) A separate deploy-only test runner outside pytest (rejected — diverges from the established single-suite convention; the scans are
   plain pytest).
D) Other (describe after [Answer]:)

[Answer]: A

---

## 5.5 Mandatory ambiguity-check (RAN against the six answers + the frozen U23 stack + the actual frozen frontend/DB code) → **CLEAN (2 folds; no surface-and-stop)**

Grounded in the ACTUAL frozen code re-read this session — `frontend/src/app/httpTransport.js` (`baseUrl = ''` default, fetches
`${baseUrl}${path}`), `App.jsx` (`export function App({ seams, transport })` — takes both as **props**, *"mounts nothing itself"*),
`seams.js` (`createSeams(transport)`), and `backend/database/migration_runner.py` (`MigrationRunner` class, `__init__(engine, …)`,
**no CLI**):

- **CG-DEP-Fold-1 [the `/api` rewrite is CORRECT — via `main.jsx`, no frozen edit].** The frozen transport fetches `${baseUrl}${path}`
  with `baseUrl` a **constructor arg** defaulting to `''`. `App.jsx` takes `transport` as a **prop** and constructs nothing —
  **deploy-config's own `main.jsx`** (new, the entry Scope-A §9 deferred here) builds the transport as
  `createHttpTransport({ baseUrl: '/api', userId })`, builds `createSeams(transport)`, and renders `<App>`. So the frontend requests
  `/api/session` etc., and the `vercel.json` rewrite `/api/:path*` → the Render backend `/:path*` is **correct**. **No frozen edit** —
  `main.jsx` is deploy-config-authored and only *imports* the frozen `App`/`seams`/`httpTransport`. (A naive reading — that the frozen
  transport hardcodes `''` so `/api` is wrong — is refuted by `baseUrl` being an injectable constructor arg `main.jsx` supplies.)
- **CG-DEP-Fold-2 [the migration release step → DEPLOY-MIGRATE-DEFERRED].** `render.yaml`'s `preDeployCommand` wires **when** the
  migration runs (deploy-config's job), but `MigrationRunner` is a **class needing an injected `sa.Engine`** with **no CLI entrypoint** —
  wrapping it into a runnable command (engine construction from `secrets-config` + `apply_all()`) is **database/composition's** concern
  (reference-not-own: the runner is database's). Recorded as **`DEPLOY-MIGRATE-DEFERRED`** — the `preDeployCommand` references the
  intended entrypoint and the deploy doc documents the contingency (analogous to AC-7 provisioned-for-not-discharged). The BOOT-1/format
  scans check the `preDeployCommand` **field shape**, never execute it — so no scan is broken; the honest-partial doc names the gap.

**No frozen contract re-opened, no frozen edit, no secret value surfaced.** Both folds resolve against frozen facts + the
reference-not-own boundary — no user decision needed. Proceed to generate Part 2.

---

## 6. Explicit HOLDS (restated for Part 2)
- **No frozen unit or composition-root file edited**: the **Vercel rewrite mechanism lives in `frontend/vercel.json`** and **must not
  touch `backend/app/main.py`** (the whole point of Q3-A — no CORS in the backend); `backend/app/**` + `frontend/src/app/**` + all
  frozen `backend/<unit>/`/`frontend/src/<unit>/` trees **untouched**. `frontend/src/main.jsx` **imports** the frozen `App.jsx`, never
  edits it. Adding a `build` script to `frontend/package.json` is the **sanctioned shared-config extension** its description reserves —
  **not** a frozen-unit source edit.
- **`database`'s + `observability`'s Infra artifacts referenced only, not re-derived**; the migration **runner** is database's, the
  Grafana **panel topology** is observability's.
- **No new dependency**: `pyyaml` floored (backend); `vite` already installed (frontend); stdlib `json`/`ast`/`pathlib`. **No secret/
  key/URL VALUES committed** — shapes only; the **public `RENDER_BACKEND_URL` shape** is correctly distinguished from a credential
  (Fold-1).
- **The Grafana dashboard file's five panels EXACTLY match observability's frozen topology — no drift, no sixth panel** (Fold-3).
- **R2–R5 stay `501` markers** (ROUTES-1); the **17 frozen P1 units + `outlier-model` (U18)/`ui-outlier-view` (U20)/`memo-extensions`
  (U19)/`observability` (U21)** untouched; **WIRE-1 untouched**; **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap
  untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**.

---

## 7. Coverage / quality gate (declarative unit)
**pytest runs the config-validation scans against the actual committed artifacts** — the scans passing IS the gate (Q6-A). **No
`--cov=backend/deploy_config`** (no production `.py` to measure); the global `--cov-fail-under=90` **holds unchanged**. **Backend 1153
passed / 31 skipped baseline must hold** (+ the new deploy-config scan tests; the 5 pre-existing `audit_store` Docker errors
unchanged) — **zero regression, additive**. `requirements.txt` NOT edited; `frontend/package.json` gains only the `build` script.

---

## 8. Next step (STOP here)
Fill the six `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check (grounded in the
frozen U23 stack + the platforms' config conventions + the actual `create_app`/`App.jsx` shapes; surfacing-and-stopping on any genuine
gap), then generate Part 2 — the config artifacts (`render.yaml`, `frontend/vercel.json` + build entry + `package.json` `build`
script, `deploy/` docs + dashboard + scrape) + the `backend/deploy_config/tests/` scans — and present the standardized 2-option
completion message (1. Request Changes / 2. Continue to Next Stage). **No code/config is generated until the answers are in and
checked.** This is the **LAST of U23's 5 stages** — its approval closes the `deploy-config` per-unit loop and completes the **5th of 6
Phase-2 units**.
