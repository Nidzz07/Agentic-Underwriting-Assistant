# NFR Design Patterns — `deploy-config` (U23, EPIC-6, Phase 2)

**Stage**: BUILD → NFR Design (per-unit) · **Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Depth**: lighter ·
**Date**: 2026-07-19.
**Built ON** the frozen FD (**BR-DEP-1..9**) + the approved **eleven `NFR-DEP-*`** (`nfr-requirements.md`) — re-opening none.
The **eleven patterns `P-DEP-1..11`** with the mechanism each uses to structurally meet its target. Answers **Q1–Q3 (all A)** +
folds **NFR-ND-DEP-Fold-1..3**.

> **Declarative-unit posture (Q1-A/Q3-A)**: these patterns describe **config-validation mechanisms** (path scans, secret-value
> scans, in-process route introspection, token-set matching, config-format parsing) — the honest shape for a unit whose deliverables
> are **config files + a deploy doc**, not application logic. **pytest is the RUNNER; the teeth read committed artifacts.** The
> **load-bearing trio is P-DEP-1/2/3** (NOEDIT-1/SEC3-1/ROUTES-1); **BUILD-1/BOOT-1** are the honest **two-part** target (P-DEP-5).

---

## 1. Patterns

### P-DEP-1 FrozenPathScanPattern — NFR-DEP-NOEDIT-1 **[LOAD-BEARING]**
**How it structurally meets the target**: a `pathlib`-based scan enumerates every path a U23 deliverable authors and asserts **none**
lies under a frozen `backend/<unit>/` or `frontend/src/<unit>/` tree or under `backend/app/**` / `frontend/src/app/**` (the CLOSED
composition root) — U23 owns only **root-level declarative config** + the frontend build entry. The scan is the build-wide mtime/path
discipline made explicit for a config unit.
- **Mechanism (spelled out)**: `ALLOWED_U23_PREFIXES` (root deploy files + the build-entry path) vs `FROZEN_PREFIXES` (the frozen
  trees + the composition root); assert the authored set ⊆ allowed and disjoint from frozen. **Detector self-test**: a synthetic
  authored path under `backend/app/` (or a frozen unit tree) is **flagged** — the scan cannot pass vacuously.

### P-DEP-2 SecretValueScanPattern — NFR-DEP-SEC3-1 **[LOAD-BEARING]**
**How it meets it**: a regex/text scan over **every committed U23 artifact** (config files, env manifest, deploy doc) for secret-value
patterns — asserting **only variable-name shapes** appear, never a value.
- **Mechanism**: patterns `sk-…` / `pk-…` / `postgresql://<user>:<pass>@…` / obvious key literals; a variable NAME (`LANGFUSE_SECRET_KEY`)
  is permitted, an assigned VALUE (`LANGFUSE_SECRET_KEY="sk-…"`) is not. **Detector self-test**: a synthetic `LANGFUSE_SECRET_KEY="sk-…"`
  **and** a `postgresql://user:pass@host/db` value are both **flagged**; a bare name shape is **not** flagged (non-vacuity of the permit).

### P-DEP-3 InProcessRouteIntrospectionPattern — NFR-DEP-ROUTES-1 **[LOAD-BEARING]**
**How it meets it**: reads the deployed route set **in-process** and asserts it equals the frozen composition root's unchanged — **no
live server, no live DB** (NFR-ND-DEP-Fold-3).
- **Mechanism (reuses the composition-root pass's technique — NOT a new one, Req-Fold-1)**: `create_app().openapi()["paths"]` — route
  registration is **env-free** (the handlers' `Depends(...)` resolve only at request time, never invoked by `openapi()`), so the app is
  built and introspected with **no env/Settings, no engine, no server**. Assert the path+method set == **R1 `GET /session` · R6
  `GET /decisions` · R7 `GET /decisions/{id}` · R2 `GET /applications` · R3 `GET /applications/{id}` · R4 `GET /applications/{id}/memo`
  · R5 `POST /recommendations/{id}/commit`** (the frozen R1/R6/R7 + the four R2–R5 markers) and that **no U23 deliverable adds a route
  file** under `backend/app/`. **Importing the production `backend.app.main` read-only to introspect is not editing** (NOEDIT-1 forbids
  writes) — ROUTES-1 and NOEDIT-1 **agree by construction**. **Detector self-test**: a synthetic extra route (or a synthetic new
  route-file path) is **flagged**.

### P-DEP-4 TokenSetChecklistPattern — NFR-DEP-DOC-1
**How it meets it**: asserts the deploy doc carries **each required marker token** — a precise **token-set** match, **not** a heading
match, **not** a prose-quality judgement (Req-Fold-2).
- **Mechanism**: `REQUIRED_TOKENS = {ROUTE-STATUS, Q1-B-DIVERGENCE, AC-7-CONTINGENCY, FREE-TIER, ENV-SHAPES}` (each a canonical heading
  **plus** a machine-checkable anchor; exact literals finalized at Code-Gen); assert every required token is present. **Detector
  self-test**: a doc with a required token removed is **flagged**; a doc with only an unrelated heading does **not** pass (the scan
  matches the token set, so it cannot pass vacuously on an unrelated section).

### P-DEP-5 PresencePlusDeployTimeFactPattern — NFR-DEP-BUILD-1, NFR-DEP-BOOT-1
**How it meets it (the honest two-part target)**: **(a)** a tier-U **presence/reference** check + **(b)** a **named-not-tested
deploy-time fact** — kept **visibly distinct within the one pattern** (Q3-A / NFR-ND-DEP-Fold-1).
- **(a) tier-U presence/reference**: BUILD-1 — the build entry (`index.html` + a `main` mounting the **frozen `App.jsx`**) + build
  config + a `build` script **exist** and reference `App.jsx` **unmodified**; BOOT-1 — `render.yaml`'s start command targets
  `backend.app.main:app` + the env manifest lists the **six** Phase-1 required shapes. **Detector self-test**: a missing entry /
  missing required shape is **flagged**.
- **(b) named deploy-time fact (observed-never-gated)**: the **actual** bundle build (Vercel) / **actual** backend boot (Render) are
  **verified at Infrastructure Design / deploy**, **NOT** given fabricated tier-U teeth — stated as the target's acceptance, not
  asserted at tier-U.

### P-DEP-6 ConfigTokenScanPattern — NFR-DEP-FREETIER-1
**How it meets it**: a config-token scan asserts **free-tier plan tokens** are present and **no paid-tier token** appears; the deploy is
labelled validation/staging (not production). **Detector self-test**: a synthetic paid-tier token is **flagged**.

### P-DEP-7 ScopeBoundaryScanPattern — NFR-DEP-SCOPE-1
**How it meets it**: a structural scan asserts U23 owns the observability **deployment half** (scrape config / dashboard file /
`LANGFUSE_*` env) but writes **no** callback-attachment code into `backend/app/main.py` and **no** MCP transport module; env vars are
**set-not-consumed** by U23 (DEP-FD-Fold-1). **Detector self-test**: a synthetic callback-attachment into `main.py` / a synthetic
MCP-transport import is **flagged**.

### P-DEP-8 ConfigFormatValidationPattern — cross-cutting (precondition for FREETIER-1 / BUILD-1 / BOOT-1)
**How it meets it**: `render.yaml` parses via **`pyyaml`** (already floored+installed) + names expected keys; `vercel.json` parses via
stdlib **`json`** + names build/output keys. Well-formedness is a **precondition** of the token/presence scans — a malformed config
fails before its tokens are checked. *(Cross-cutting: supports the config-reading targets; not a 1:1-to-target pattern.)*

### P-DEP-9 GovernanceAssertionPattern — NFR-DEP-ADVISORY-1, NFR-DEP-SEC-1
**How it meets it**: governance + a light token check — no U23 deliverable declares/emits a `Recommendation`/verdict; the
Security-Guardrails posture holds (SEC-3 the load-bearing one, machine-checked by P-DEP-2).

### P-DEP-10 ObservedNotGatedPattern — NFR-DEP-PERF-1
**How it meets it**: U23 owns **no** runtime SLO; the validation deploy's responsiveness is provider-managed free-tier behavior,
**observed-never-gated** — recorded, never asserted-as-failure.

### P-DEP-11 DetectorSelfTestSubstratePattern — cross-cutting (NOEDIT-1 / SEC3-1 / ROUTES-1 / SCOPE-1 / DOC-1 / FREETIER-1)
**How it meets it**: the shared substrate guaranteeing **every scan-bearing target carries a detector self-test + a non-vacuity
assertion** (Req-Fold-3) — the project's no-vacuous-scan discipline extended to a declarative unit. Each scan has (i) a positive
assertion over the real committed artifacts and (ii) a synthetic-violation detector proving the scan actually bites. *(Cross-cutting:
composes with P-DEP-1/2/3/4/6/7.)*

---

## 2. Pattern-relationship diagram (validated — rectangle-only, alphanumeric IDs, quoted labels, no special characters)

```mermaid
flowchart TD
    ARTIFACTS["config artifacts render and vercel and env manifest and deploy doc"]
    VALIDATORS["deploy validators scans each with a detector self test"]
    PRESENCE["presence and reference checks plus named deploy time facts"]
    FROZEN["frozen system composition root and all frozen unit trees"]
    COMP["composition and application own the live callback and MCP binding"]

    ARTIFACTS --> VALIDATORS
    ARTIFACTS --> PRESENCE
    VALIDATORS -.reads.-> FROZEN
    VALIDATORS -.blocked.-> FROZEN
    ARTIFACTS -.packaged.-> FROZEN
    VALIDATORS -.deferred.-> COMP
```

### Text alternative (always included)
- The **config artifacts** (`render.yaml`, `vercel.json` + build entry, env manifest, deploy doc) flow into the **deploy validators**
  (the scans — each with a detector self-test) and into the **presence/reference checks** (which also carry the **named deploy-time
  facts** for BUILD-1/BOOT-1).
- **No-edit is a visible structural property**: the validators **read** the **frozen system** (dashed **reads** — ROUTES-1's
  in-process `openapi()` introspection) but a **blocked** dashed edge shows they **never write** it; the artifacts **package** the
  frozen system (dashed **packaged**), never edit it.
- The dashed **deferred** edge shows the live callback attachment + MCP binding are **composition/application-owned**, not U23's.

---

## 3. Traceability — pattern → target → tier → rigor (no orphan)

| Pattern | Target(s) | Tier | Rigor |
|---|---|---|---|
| **P-DEP-1 FrozenPathScan** | NFR-DEP-NOEDIT-1 | tier-U structural/path scan | **full-highest (load-bearing)** |
| **P-DEP-2 SecretValueScan** | NFR-DEP-SEC3-1 | tier-U secret-value scan | **full-highest (load-bearing)** |
| **P-DEP-3 InProcessRouteIntrospection** | NFR-DEP-ROUTES-1 | tier-U in-process introspection | **full-highest (load-bearing)** |
| **P-DEP-4 TokenSetChecklist** | NFR-DEP-DOC-1 | tier-U token-set scan | standard |
| **P-DEP-5 PresencePlusDeployTimeFact** | NFR-DEP-BUILD-1, NFR-DEP-BOOT-1 | tier-U presence + **named deploy-time fact** | standard |
| **P-DEP-6 ConfigTokenScan** | NFR-DEP-FREETIER-1 | tier-U config-token scan | standard |
| **P-DEP-7 ScopeBoundaryScan** | NFR-DEP-SCOPE-1 | tier-U structural scan | standard |
| **P-DEP-8 ConfigFormatValidation** | *(cross-cutting — FREETIER-1/BUILD-1/BOOT-1 precondition)* | tier-U parse | supporting |
| **P-DEP-9 GovernanceAssertion** | NFR-DEP-ADVISORY-1, NFR-DEP-SEC-1 | governance | standard |
| **P-DEP-10 ObservedNotGated** | NFR-DEP-PERF-1 | soft/observed | soft |
| **P-DEP-11 DetectorSelfTestSubstrate** | *(cross-cutting — every scan-bearing target)* | tier-U | **substrate (non-vacuity)** |

**All eleven `NFR-DEP-*` covered; no orphan.** P-DEP-8/P-DEP-11 are **cross-cutting supporting** patterns (NFR-ND-DEP-Fold-2),
precedented by prior units' substrate patterns — not orphan patterns.

## 4. Settled items held (not re-opened)
- The frozen FD (**BR-DEP-1..9**) + the eleven `NFR-DEP-*` + Req-Fold-1..3 are the substrate.
- **Q1-A**: the config artifacts are first-class components, tagged declarative + layout-open (DEP-D8). **Q2-A**: one shared
  `deploy_validators` substrate + per-target scan functions each with a detector self-test; file home a Code-Gen decision. **Q3-A**:
  one P-DEP-5 carrying both halves visibly distinct.
- **NFR-ND-DEP-Fold-1**: C-DEP-2/3 map to BUILD-1/BOOT-1's tier-U presence half; the deploy-time fact is named-not-tested (honest, not
  a gap). **Fold-2**: cross-cutting patterns are supporting, not orphans. **Fold-3**: ROUTES-1 introspection is env-free/DB-free via
  `create_app().openapi()`; import-to-read ≠ edit → ROUTES-1 and NOEDIT-1 agree.
- **Deferred to Infrastructure Design (comprehensive)**: the actual Render/Vercel topology + build commands + env manifest contents +
  migration release step + the observability scrape/dashboard config. **Deferred to Code-Gen**: the exact token literals, the
  scan-module file home, the config filenames.
- **No new dependency**; **no frozen unit edited**; the CLOSED composition root untouched; **tier-B N/A + NOT authorized**; the
  **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit
  decomposition unchanged**.
