# Code Summary — `deploy-config` (U23, EPIC-6, Phase 2)

**Stage**: BUILD → Code Generation (per-unit, Part 2) · **Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Date**: 2026-07-19
· **Depth**: comprehensive · **the 5th and LAST of U23's 5 stages** — closes the U23 loop; the **5th of 6 Phase-2 units**.
**Built ON** the frozen FD (**BR-DEP-1..9**) + NFR Requirements (**eleven `NFR-DEP-*`**) + NFR Design (**P-DEP-1..11** / **C-DEP-1..5**)
+ Infrastructure Design (**INFRA-DEP-Fold-1..3**) — re-opening none. Answers **Q1–Q6 (all A)** + folds **CG-DEP-Fold-1..2** (plan §5.5).

---

## 1. Deploy artifacts generated (DEP-D8 RESOLVED — declarative config, at platform-conventional homes)

| Component | File(s) | Notes |
|---|---|---|
| **C-DEP-2** | `render.yaml` (repo root) | Render free-tier web service; `runtime: python`; `uvicorn backend.app.main:app`; `preDeployCommand` (migration release slot); `envVars` names-only `sync: false` |
| **C-DEP-3** | `frontend/vercel.json` · `frontend/index.html` · `frontend/src/main.jsx` · `frontend/vite.config.js` + `"build": "vite build"` in `frontend/package.json` | Vite static build → `dist`; **rewrite `/api/:path*` → the backend host** (no CORS, no backend edit); `main.jsx` mounts the **frozen `App.jsx`** with `baseUrl: '/api'` |
| **C-DEP-4** | `render.yaml` `envVars` block + `deploy/README.md` ENV-SHAPES | Phase-1 six + Phase-2 reserved, **names only**; references frozen `.env.example` |
| **C-DEP-5** | `deploy/README.md` | honest partial-deploy doc, the five DOC-1 tokens + MIGRATION (DEPLOY-MIGRATE-DEFERRED) |
| **obs deployment half** | `deploy/grafana-dashboard.json` (one dashboard, 5 panels) · `deploy/prometheus-scrape.yml` | 1:1 to observability's frozen five metrics (no drift) |
| **C-DEP-1** | `backend/deploy_config/__init__.py` + `tests/{__init__.py, structural.py, test_*.py}` | **test-only** (no production `.py`) |

**`vite` already installed** (transitive via `vitest`) — **no new dependency**. Adding the `build` script is the sanctioned deliverable
`frontend/package.json`'s own description reserves — **not** a frozen edit.

## 2. Tests — **41 scans, all green against the REAL committed artifacts; 100% pass**

| File | Tests | Target(s) / rigor |
|---|---|---|
| `test_noedit.py` | 5 | **NOEDIT-1** (LOAD-BEARING) — frozen-path allowlist + additive-package.json + detector |
| `test_sec3.py` | 4 | **SEC3-1** (LOAD-BEARING) — credential-value scan + detector (flag + non-vacuous permit; public host allowed, Fold-1) |
| `test_routes.py` | 4 | **ROUTES-1** (LOAD-BEARING) — `create_app().openapi()` == the 7 frozen route templates; no new route file; import-to-read ≠ edit |
| `test_doc.py` | 3 | **DOC-1** — the five-token checklist (not headings/prose) + detector |
| `test_build.py` | 6 | **BUILD-1** — presence/reference (entry mounts frozen `App.jsx`, `build` script) + the named deploy-time fact |
| `test_boot.py` | 5 | **BOOT-1** — start command + six env shapes + preDeployCommand slot + the named deploy-time fact |
| `test_freetier.py` | 3 | **FREETIER-1** — `plan: free`, no paid token + detector |
| `test_scope.py` | 4 | **SCOPE-1** — obs deployment half present + no live-binding/MCP import + **Fold-3 five-panel no-drift** (vs observability's `METRIC_DEFINITIONS`) |
| `test_format.py` | 4 | **P-DEP-8** — `render.yaml`/`vercel.json`/dashboard/scrape well-formed |
| `test_governance.py` | 3 | **ADVISORY-1 + SEC-1 + PERF-1** — no verdict value; SEC-3 machine-checked elsewhere; observed-never-gated |

`tests/structural.py` — the substrate (repo-root path helpers, credential/token scanners, `pyyaml`/`json` loaders, the
frozen-vs-allowed path classifier, AST import detection). All eleven `NFR-DEP-*` covered, no orphan.

## 3. Realization notes (folds — plan §5.5)

- **CG-DEP-Fold-1** — the `/api` Vercel rewrite is **correct** because deploy-config's **own `main.jsx`** constructs the transport with
  `baseUrl: '/api'` (baseUrl is the frozen transport's constructor arg; `App.jsx` takes `transport` as a prop). **No frozen edit** —
  `main.jsx` only imports the frozen `App`/`seams`/`httpTransport`.
- **CG-DEP-Fold-2 (`DEPLOY-MIGRATE-DEFERRED`)** — `render.yaml`'s `preDeployCommand` wires **when** the migration runs; `MigrationRunner`
  is a class needing an injected engine with **no CLI** — the runnable entrypoint is **database's/composition's** (reference-not-own),
  a **carried dependency** honestly documented in `deploy/README.md` (analogous to AC-7 provisioned-for-not-discharged).
- The `RENDER_BACKEND_URL` rewrite destination is a **placeholder public-host shape** (`REPLACE_WITH_RENDER_BACKEND_HOST`), never a
  credential (Fold-1) — permitted by SEC3-1's non-vacuous permit side.
- Two scans initially self-matched their own token literals (`test_scope`, `test_routes`) → rewritten to **AST import detection**
  (robust: a token as scan DATA is not read as a dependency) — same fix pattern as observability's TIERU scan.

## 4. Result

- **Backend: 1194 passed / 31 skipped** (1153 baseline + **41** new; the **5 pre-existing `audit_store` Docker-absence errors
  UNCHANGED**) — **zero regression**. **Global `--cov-fail-under=90` holds at 99.85%** — **NO `--cov=backend/deploy_config` line added**
  (the unit has no production `.py` to measure; a coverage % does not meaningfully apply — DEP-D8 / Q6-A). The scans passing **against
  the real committed artifacts** IS the gate.
- **Frontend: 682 passed / 137 files** (unchanged baseline) · **ESLint clean** — the new build entry did not regress it.
- **`requirements.txt` NOT edited**; `frontend/package.json` gained **only** the `build` script.

## 5. Holds verified

No frozen unit or composition-root file edited — the Vercel rewrite lives in `frontend/vercel.json`, **never** `backend/app/main.py`;
`main.jsx` imports the frozen `App`/`seams`/`httpTransport`, edits none. `database`'s + `observability`'s Infra referenced only. No new
dependency (`pyyaml` floored, `vite` already installed). No secret values — shapes only (`RENDER_BACKEND_URL` a non-secret public host).
The Grafana **five panels exactly match observability's frozen `METRIC_DEFINITIONS`** — no drift, no sixth panel. **R2–R5 stay `501`**
(ROUTES-1). The 17 frozen P1 units + `outlier-model` (U18)/`ui-outlier-view` (U20)/`memo-extensions` (U19)/`observability` (U21) +
WIRE-1 + the closed composition root — untouched. tier-B N/A + not authorized; the `audit_store` Docker-guard gap untouched; no other
unit started; the 23-unit decomposition unchanged.
