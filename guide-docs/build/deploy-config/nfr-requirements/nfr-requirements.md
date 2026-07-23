# NFR Requirements — `deploy-config` (U23, EPIC-6, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Depth**: lighter ·
**Date**: 2026-07-19 · Story **US-PLAT-11** · NFR-DEPLOY-1.
**Built ON** the frozen FD (**BR-DEP-1..9** + config surfaces + reference-not-own + the 6-step lifecycle + **DEP-FD-Fold-1..3**) —
re-opening none. Answers **Q1–Q3 (all A)** + folds **NFR-DEP-Req-Fold-1..3** (plan §4.5).

> **The declarative-unit posture (Q1-A/Q3-A)**: `deploy-config` deliverables are **config files + a deploy doc**, not application
> logic. **pytest is the RUNNER; the teeth are config-validation / file-presence / structural-scan checks over the committed
> artifacts** — not application-behavior assertions. A **detector self-test on every scan-bearing target** (the project's
> no-vacuous-scan discipline, extended here — Req-Fold-3). **BUILD-1's actual bundle + BOOT-1's actual boot are inherently
> deploy-time facts**, NAMED with their acceptance stated as *verified at Infrastructure Design/deploy, observed-never-gated* — no
> fabricated tier-U teeth (Q3-A). **No live cloud deploy, no network, no key, no secret VALUE at tier-U.**

---

## 1. The eleven `NFR-DEP-*` targets

### NFR-DEP-NOEDIT-1 — no U23 deliverable edits any frozen unit or the composition root **[LOAD-BEARING]**
- **Assertion (pass/fail)**: no U23 deliverable modifies any file under a frozen `backend/<unit>/` or `frontend/src/<unit>/` tree, or
  under `backend/app/**` / `frontend/src/app/**` (the CLOSED composition root). U23 adds only **root-level declarative config** + the
  frontend build entry.
- **Acceptance**: a **structural path scan** (the build-wide mtime/path discipline) confirms only U23-owned paths are U23-authored;
  the composition-root + frozen trees are untouched. **Detector self-test**: a synthetic frozen-path write is flagged (Req-Fold-3).
- **Tier / rigor**: tier-U structural scan · **full-highest**.

### NFR-DEP-SEC3-1 — no secret/key/URL VALUE in any committed deploy artifact **[LOAD-BEARING]**
- **Assertion**: no committed U23 artifact (config files, env manifest, deploy doc) carries a secret/key/connection-string **value** —
  only variable-name **shapes** + the `secrets-config` contract. Real values live in the deploy platform, never committed.
- **Acceptance**: a **secret-value scan** over every committed U23 artifact finds no value literal. **Detector self-test**: a synthetic
  `LANGFUSE_SECRET_KEY="sk-…"` (and a `postgresql://user:pass@host` value) is flagged (Req-Fold-3).
- **Tier / rigor**: tier-U structural scan + detector self-test · **full-highest**.

### NFR-DEP-BUILD-1 — the frontend build config produces a static bundle Vercel serves
- **Assertion**: the build **entry** (`index.html` + a `main` mounting the **frozen `App.jsx`**) + build config + a `build` script
  **exist** and **reference the frozen `App.jsx` unmodified**.
- **Acceptance**: **presence/reference check** — the entry files exist, import the frozen `App.jsx` (not a copy), and a `build` script
  is declared. **⚑ The actual bundle build is an inherently deploy-time/Infra fact** — its acceptance is *verified at Infrastructure
  Design/Code-Gen/deploy, observed-never-gated* — **NOT** a tier-U assertion. **Detector self-test**: a missing entry/reference is
  flagged (presence-detector).
- **Tier / rigor**: tier-U presence/reference (config) + a **named deploy-time fact** · standard.

### NFR-DEP-BOOT-1 — the backend service boots via the fail-closed `Settings`
- **Assertion**: the Render service config names a **start command** running the frozen `backend.app.main:app`, and the **env
  manifest** lists the **six Phase-1 required shapes** (`DATABASE_URL`, `AUDIT_WRITER_URL`, `AUDIT_READER_URL`,
  `AUDIT_WRITER_PASSWORD`, `AUDIT_READER_PASSWORD`, `GEMINI_API_KEY`).
- **Acceptance**: **presence/reference check** — the start command targets `backend.app.main:app`; the env manifest enumerates the six
  shapes. **⚑ The actual boot is an inherently deploy-time fact** — *verified at deploy, observed-never-gated* — no frozen `Settings`
  field made optional (no frozen edit). **Detector self-test**: a missing required shape is flagged.
- **Tier / rigor**: tier-U presence/reference (config) + a **named deploy-time fact** · standard.

### NFR-DEP-FREETIER-1 — free-tier only; validation/staging, not production
- **Assertion**: the platform configs name **free-tier plans only**; no paid-tier token; the deploy is labelled validation/staging
  (production is Phase-3 / OOS-4).
- **Acceptance**: a **config-token scan** confirms free-tier plan tokens and finds no paid-tier token. **Detector self-test**: a
  synthetic paid-tier token is flagged (Req-Fold-3).
- **Tier / rigor**: tier-U config scan · standard.

### NFR-DEP-ROUTES-1 — the deployed route table equals the frozen composition root's; no domain route added
- **Assertion**: the deployed app's routes are **exactly** the frozen composition root's — R1/R6/R7 + the four R2–R5 `501` markers —
  and **no U23 deliverable adds a route file** under `backend/app/`.
- **Acceptance** (Req-Fold-1): a **STATIC comparison against the committed composition-root source** — the route set read from the
  frozen route decorators / `main.py` registration (or `app.openapi()["paths"]` built **in-process, no live server**, the TestClient-
  free introspection Scope-A used) equals the expected set; no new route file exists under `backend/app/`. **No live deploy.**
  **Detector self-test**: a synthetic extra route / new route-file path is flagged.
- **Tier / rigor**: tier-U static/structural scan · **full-highest** (guards BR-DEP-6 — no smuggled domain state).

### NFR-DEP-SCOPE-1 — the OBS deployment half is present; the code-attachment half + MCP transport are absent
- **Assertion**: U23 deliverables include the observability **deployment half** (Prometheus `/metrics` scrape config, the Grafana
  dashboard-as-code file, `LANGFUSE_*` env wiring) **but NO** callback-attachment code into `main.py` and **NO** MCP transport module;
  env vars are **set-not-consumed** by U23 (DEP-FD-Fold-1).
- **Acceptance**: a **structural scan** — U23 owns the scrape/dashboard/env config; no U23 file writes a langfuse callback into
  `backend/app/` and no U23 file is an MCP transport binding. **Detector self-test**: a synthetic callback-attachment into `main.py` /
  a synthetic MCP-transport import is flagged (Req-Fold-3).
- **Tier / rigor**: tier-U structural scan · standard.

### NFR-DEP-DOC-1 — the deploy doc is checklist-complete (honest partial-deploy documentation)
- **Assertion** (Q2-A / Req-Fold-2): the deploy doc contains **every required section marker** — the **live-vs-`501` route split**,
  the **Q1-B divergence**, **AC-7's contingency**, **free-tier**, and the **env-shape list** — each keyed to an **explicit token**
  (canonical heading + a machine-checkable anchor, e.g. `ROUTE-STATUS:` / `Q1-B-DIVERGENCE:` / `AC-7-CONTINGENCY:` / `FREE-TIER:` /
  `ENV-SHAPES:`; exact tokens finalized at Code-Gen).
- **Acceptance**: a **checklist-completeness scan** asserts **each required token is present** (structure, not prose quality).
  **Detector self-test**: a doc with a required token removed is flagged; an unrelated heading does **not** satisfy the check
  (Req-Fold-2).
- **Tier / rigor**: tier-U checklist scan + detector self-test · standard (real non-vacuous teeth on structure).

### NFR-DEP-ADVISORY-1 — U23 declares no recommendation/verdict (advisory-only inherited)
- **Assertion**: no U23 deliverable declares/emits a `Recommendation`/verdict or any domain decision — config only.
- **Acceptance**: **governance** + a light scan (no `Recommendation`/verdict token in U23 deliverables).
- **Tier / rigor**: governance · standard.

### NFR-DEP-PERF-1 — (soft/observed) deploy is a one-off validation, no runtime SLO owned here
- **Assertion**: U23 owns **no** runtime performance gate; the validation deploy's responsiveness is provider-managed free-tier
  behavior, observed-never-gated.
- **Acceptance**: recorded; no hard SLO asserted at tier-U.
- **Tier / rigor**: soft/observed.

### NFR-DEP-SEC-1 — Security-Guardrails governance (SEC-3 load-bearing here)
- **Assertion**: the Security-Guardrails posture holds — **SEC-3 shapes-only** (the load-bearing one, → SEC3-1), free-tier, no
  demographic anything (trivially — config unit), advisory-only, no live-key at tier-U.
- **Acceptance**: the compliance table below; SEC3-1 carries the machine-checked half.
- **Tier / rigor**: governance.

---

## 2. Traceability (BR-DEP → NFR-DEP — no orphan)

| BR-DEP | NFR-DEP target(s) |
|---|---|
| BR-DEP-1 | **NFR-DEP-NOEDIT-1** |
| BR-DEP-2 | NFR-DEP-BUILD-1 |
| BR-DEP-3 | NFR-DEP-BOOT-1 |
| BR-DEP-4 | **NFR-DEP-SEC3-1** + NFR-DEP-SEC-1 |
| BR-DEP-5 | NFR-DEP-FREETIER-1 |
| BR-DEP-6 | **NFR-DEP-ROUTES-1** |
| BR-DEP-7 | NFR-DEP-DOC-1 |
| BR-DEP-8 | NFR-DEP-SCOPE-1 |
| BR-DEP-9 | NFR-DEP-ADVISORY-1 |
| (cross-cutting) | NFR-DEP-PERF-1 (soft), NFR-DEP-SEC-1 (governance) |

**No orphan** — every BR-DEP maps to ≥1 NFR-DEP; **US-PLAT-11 / NFR-DEPLOY-1** → BUILD-1/BOOT-1/FREETIER-1/ROUTES-1/DOC-1. The
**load-bearing pair** is **NOEDIT-1 + SEC3-1** (both full-highest, both with detector self-tests); **ROUTES-1** is the third
full-highest scan (guards the no-smuggled-domain-state hold).

## 3. Security-Guardrails compliance

| Guardrail | Status | Where |
|---|---|---|
| **SEC-3** (no secret VALUE in artifacts/tests) | **Compliant — load-bearing** | NFR-DEP-SEC3-1 (scan + detector self-test); shapes-only |
| **No-frozen-edit** (17 P1 + U18/U19/U20/U21 + composition root) | **Compliant** | NFR-DEP-NOEDIT-1 (path scan + detector self-test) |
| **No domain state / no new route** | **Compliant** | NFR-DEP-ROUTES-1 (static route-table equivalence) + NFR-DEP-SCOPE-1 |
| **Advisory-only** (no recommendation/verdict) | **Compliant** | NFR-DEP-ADVISORY-1 |
| **Free-tier / validation-not-production** (NFR-CONSTRAINTS-1 / OOS-4) | **Compliant** | NFR-DEP-FREETIER-1 |
| **CON-BR1** (no demographic anything) | **N/A (trivially)** | a config unit reads no applicant data — no demographic surface exists |
| **Honest partial-deploy transparency** | **Compliant** | NFR-DEP-DOC-1 (checklist-completeness) — the Q1-B divergence + AC-7 contingency documented, not hidden |

**No blocking finding.** Every applicable guardrail is compliant; CON-BR1 is N/A (trivially — no data surface).

## 4. Held
- **No new dependency** unless a genuine one is surfaced (a YAML/JSON parser — see `tech-stack-decisions.md`). **No frozen unit
  edited**; the CLOSED composition root untouched; **no live cloud deploy at tier-U**; **no secret VALUE** anywhere.
- **AC-7 provisioned-for, not dischargeable here** (DEP-FD-Fold-2); the **Q1-B divergence** deployed as-built + documented, not
  resolved (DEP-FD-Fold-3, DOC-1); the **`OBS-SINK-DEFERRED` code half + `MCP-TRANSPORT-DEFERRED`** stay composition/application-owned
  (DEP-FD-Fold-1, SCOPE-1).
- **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged);
  **no other unit started**; the **23-unit decomposition unchanged**.
