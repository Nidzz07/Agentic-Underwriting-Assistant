# NFR Design Plan (Part 1) — `deploy-config` (EPIC-6 / U23, Phase 2)

**Phase / Stage**: BUILD → NFR Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `deploy-config` (U23) · FD ✅ · **NFR Requirements ✅ (approved 2026-07-19)** → **NFR Design ← here (the 3rd of its
5 stages)**.
**Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Date**: 2026-07-19 · **Depth**: **lighter**.
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR-Design artifact generated; no code; no deploy files. Stop after this plan.**

Built **ON** the frozen FD (**BR-DEP-1..9** + config surfaces + reference-not-own + the 6-step lifecycle) and the approved NFR
Requirements (**eleven `NFR-DEP-*`** + the load-bearing **NOEDIT-1/SEC3-1/ROUTES-1** trio + the BUILD-1/BOOT-1 deploy-time-fact
naming + **Req-Fold-1..3**) — **re-opening none**.

---

## 1. The design posture (honest to a declarative unit)

Every prior unit's NFR Design mapped targets to **patterns describing application-behavior guarantees** + **Python-module
components**. `deploy-config` is **declarative** — so the patterns here describe **config-validation mechanisms** (path scans,
secret-value scans, in-process route introspection, token-set matching, config-format parsing) **where that is genuinely what the
target is**, and the components are a **small set of validator modules** (or one) **plus the config artifacts themselves** as
first-class named entities. Two targets (**BUILD-1/BOOT-1**) are **honestly two-part** — a real tier-U presence/reference check **+**
a named-not-tested deploy-time fact — and are modeled as such, **not** forced into one mechanism. **The pattern↔component structure of
every prior unit is preserved; only the mechanism vocabulary shifts.** **Q1 decides how first-class the config artifacts are, given
DEP-D8 leaves the file layout to Code-Gen.**

---

## 2. Pattern map — ELEVEN patterns `P-DEP-1..11`, all targets covered, NO ORPHAN

| Pattern | → target | Mechanism (spelled out) |
|---|---|---|
| **P-DEP-1 FrozenPathScanPattern** *(load-bearing NOEDIT-1)* | NFR-DEP-NOEDIT-1 | a `pathlib`-based scan asserting only U23-owned paths are U23-authored + **no** write under any frozen `backend/<unit>/` / `frontend/src/<unit>/` tree or `backend/app/**` / `frontend/src/app/**`; **detector self-test** — a synthetic frozen-path write is flagged (the build-wide mtime/path discipline) |
| **P-DEP-2 SecretValueScanPattern** *(load-bearing SEC3-1)* | NFR-DEP-SEC3-1 | a regex/text scan over **every committed U23 artifact** for secret-value patterns (`sk-…`, `postgresql://user:pass@…`, key literals); **detector self-test** — a synthetic `LANGFUSE_SECRET_KEY="sk-…"` + a `postgresql://user:pass@host` value are flagged |
| **P-DEP-3 InProcessRouteIntrospectionPattern** *(load-bearing ROUTES-1)* | NFR-DEP-ROUTES-1 | reads the route set from the frozen composition root **in-process** — `app.openapi()["paths"]` built with **no live server** (**reusing the composition-root pass's established TestClient-free mechanism, Req-Fold-1 — not a new technique**) — asserts == R1/R6/R7 + the four R2–R5 markers + **no new route file**; **detector self-test** — a synthetic extra route / new route-file path is flagged |
| **P-DEP-4 TokenSetChecklistPattern** | NFR-DEP-DOC-1 | asserts the deploy doc carries **each required marker token** (a canonical heading **+** a machine-checkable anchor — `ROUTE-STATUS:` / `Q1-B-DIVERGENCE:` / `AC-7-CONTINGENCY:` / `FREE-TIER:` / `ENV-SHAPES:`); matches the **token set, not any heading, not prose quality** (Req-Fold-2); **detector self-test** — a removed token is flagged |
| **P-DEP-5 PresencePlusDeployTimeFactPattern** | NFR-DEP-BUILD-1, NFR-DEP-BOOT-1 | the **honest two-part** pattern: **(a)** a tier-U **presence/reference** check (the build entry + `main` mounting frozen `App.jsx` + `build` script exist / the Render start command targets `backend.app.main:app` + the six env shapes are listed) **+ (b)** a **named-not-tested deploy-time fact** (the actual bundle build / backend boot, *verified at Infrastructure Design/deploy, observed-never-gated*); the two halves are **explicitly distinguished** |
| **P-DEP-6 ConfigTokenScanPattern** | NFR-DEP-FREETIER-1 | a config-token scan — free-tier plan tokens present, no paid-tier token; **detector self-test** — a synthetic paid-tier token is flagged |
| **P-DEP-7 ScopeBoundaryScanPattern** | NFR-DEP-SCOPE-1 | a structural scan — the OBS deployment half present, **no** callback-attachment into `main.py`, **no** MCP transport module, env **set-not-consumed**; **detector self-test** — a synthetic callback-attachment / MCP-transport import is flagged |
| **P-DEP-8 ConfigFormatValidationPattern** | (cross-cutting, supports FREETIER-1/BUILD-1/BOOT-1) | `render.yaml` parses via `pyyaml` + names expected keys; `vercel.json` parses via stdlib `json` + names build/output keys — well-formedness as a precondition of the token/presence scans |
| **P-DEP-9 GovernanceAssertionPattern** | NFR-DEP-ADVISORY-1, NFR-DEP-SEC-1 | governance + a light token check (no `Recommendation`/verdict token; the Security-Guardrails posture) |
| **P-DEP-10 ObservedNotGatedPattern** | NFR-DEP-PERF-1 | no runtime SLO owned here; the validation deploy's responsiveness is provider-managed, observed-never-gated |
| **P-DEP-11 DetectorSelfTestSubstratePattern** | (cross-cutting — NOEDIT-1/SEC3-1/ROUTES-1/SCOPE-1/DOC-1/FREETIER-1) | the shared substrate: **every scan-bearing target carries a detector self-test + a non-vacuity assertion** (Req-Fold-3), the project's no-vacuous-scan discipline extended to a declarative unit |

**No orphan** — all eleven `NFR-DEP-*` covered; the load-bearing trio (NOEDIT-1/SEC3-1/ROUTES-1) → P-DEP-1/2/3; the two-part
BUILD-1/BOOT-1 → P-DEP-5; the detector discipline → P-DEP-11 (composing with 1/2/3/6/7/4).

---

## 3. Proposed logical components `C-DEP-*` (layout OPEN — DEP-D8)

Two categories, kept distinct: **validator modules** (the scan logic — the only plausibly-Python part) and the **config artifacts**
(declarative, not Python). **Q1 decides how first-class the config artifacts are modeled.**

| Component (proposed) | Kind | Responsibility |
|---|---|---|
| **C-DEP-1 `deploy_validators`** (one module, or a small `tests/`-scanning set — home a Code-Gen decision, DEP-D8) | scan logic | the path scan (P-DEP-1) · secret-value scan (P-DEP-2) · route introspection (P-DEP-3) · token-set checklist (P-DEP-4) · presence/reference checks (P-DEP-5a) · config-token scan (P-DEP-6) · scope scan (P-DEP-7) · format validation (P-DEP-8) · the detector-self-test substrate (P-DEP-11) |
| **C-DEP-2 `render.yaml`** | config artifact | the Render backend service (start command → `backend.app.main:app`, free-tier plan, env shapes, migration release step) |
| **C-DEP-3 `vercel.json` + frontend build entry** (`index.html` + `main` mounting frozen `App.jsx` + `build` script) | config artifact | the Vercel static-frontend build producing the bundle |
| **C-DEP-4 env manifest** (`.env.example`-style shapes; values set in the platform) | config artifact | the Phase-1 required + Phase-2 reserved variable-name **shapes** (SEC-3) |
| **C-DEP-5 deploy doc** (the honest partial-deploy README) | config artifact | the checklist-complete documentation (P-DEP-4 tokens) |

**Reference-not-own (three distinct categories, kept separate)**: **(1) frozen system — packaged, never edited** (the composition
root `backend/app/**` + `frontend/src/app/**` + the 17 P1 + U18/U19/U21 trees — read for ROUTES-1's introspection, never modified);
**(2) config artifacts — U23-owned** (C-DEP-2..5, authored by U23 at Code-Gen); **(3) deferred-to-composition/application** (the live
callback attachment + MCP transport — NOT U23's, guarded by SCOPE-1).

**Component → target coverage (no orphan)** will be a full table in Part 2: C-DEP-1 → the ten scan/check targets;
C-DEP-2/3/4/5 → the artifacts BUILD-1/BOOT-1/FREETIER-1/SEC3-1/DOC-1 validate.

**Mermaid (planned, validated 7 rules)**: config artifacts (C-DEP-2..5) → the `deploy_validators` scans (C-DEP-1) → the **frozen
system** node with a **blocked no-edit edge** (visible structural property, consistent with every prior unit) + a **packaged** edge;
a **deferred** dashed edge to composition for the live-binding half.

---

## 4. Clarifying questions (fill each `[Answer]:` tag)

Letter after each `[Answer]:` tag; if none fit, choose the last (Other) and describe. These decide the **pattern/component modeling**
— they do **not** re-open the FD, the eleven `NFR-DEP-*`, or the folds.

## Question 1 — Should the config artifacts (`render.yaml`, `vercel.json`, env manifest, deploy doc) be modeled as first-class logical components, the way Python modules were in every prior unit?
DEP-D8 leaves the actual file layout a Code-Gen decision; over-formalizing the artifacts could overstate their status.

A) **Yes — model them as first-class NAMED components (C-DEP-2..5), but explicitly tagged "config artifact (declarative), exact
   filename/home a Code-Gen decision (DEP-D8)".** They ARE the unit's primary deliverables (a config unit's "components" genuinely
   are its config files); naming them keeps the component→target coverage honest (BUILD-1/BOOT-1/FREETIER-1/SEC3-1/DOC-1 each
   validate a specific artifact) and mirrors every prior unit's structure — while the **declarative tag + the OPEN-layout caveat**
   prevent overstating them as fixed Python modules. The **validator module(s) (C-DEP-1)** are the one plausibly-Python component,
   also home-open.
B) **No — model only the validator module(s) as components; list the config artifacts as inputs/data, not components** (avoids
   overstating declarative files as components; but weakens the component→target coverage — BUILD-1/BOOT-1/DOC-1 would map to
   "inputs" rather than named components, diverging from every prior unit's table).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 2 — The validator surface: ONE `deploy_validators` module, or a scan-per-target set (mirroring the sibling `StructuralGuard` + `test_*` split)?
Prior units split a `structural.py` substrate + per-target `test_*.py`. Here the "unit under test" is committed config, not a package.

A) **One shared `deploy_validators` scan substrate + per-target scan functions each with its detector self-test** (the sibling
   `StructuralGuard`/`structural.py` shape, adapted): a single substrate module holds the path/secret/route-introspection/token/format
   helpers; each `NFR-DEP-*` target gets a scan function + a detector self-test, organized one-concern-per-target. The exact **file
   home** (a `tests/`-style location scanning the committed deploy artifacts vs a `backend/deploy_config/` package) stays a **Code-Gen
   decision** (DEP-D8) — NFR Design pins the **substrate + per-target shape**, not the path.
B) A single monolithic validator with all checks inline (rejected — poor failure locality; diverges from the established
   substrate + per-target-scan convention).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 3 — BUILD-1/BOOT-1's two-part shape: one pattern (P-DEP-5) covering both halves, or split into a tier-U-tested pattern + a separate named-fact pattern?
Req-Fold / Q3-A established these are honestly two-part (a presence/reference check + a deploy-time fact).

A) **One pattern `P-DEP-5 PresencePlusDeployTimeFactPattern` that EXPLICITLY carries both halves** — (a) the tier-U presence/reference
   check and (b) the named-not-tested deploy-time fact (observed-never-gated, verified at Infra/deploy) — kept **visibly distinct
   within the one pattern**. This models the target honestly without inventing a second pattern for a fact that has no tier-U
   mechanism.
B) Split into two patterns (a tested-presence pattern + a separate deploy-time-fact pattern) — available if you prefer maximal
   separation; but the deploy-time-fact "pattern" would have no tier-U mechanism, which risks reading as a pattern with no teeth.
C) Other (describe after [Answer]:)

[Answer]: A

---

## 4.5 Mandatory ambiguity-check (RAN against the three answers + the frozen FD + approved NFR Requirements) → **CLEAN (3 folds; no surface-and-stop)**

Grounded in the frozen FD + the eleven `NFR-DEP-*` + Req-Fold-1..3 + the **actual Scope-A composition-root test conftest**
(`backend/app/tests/conftest.py`, re-read this session):

- **NFR-ND-DEP-Fold-1 [Q1 + Q3 coverage-table interaction]** — modeling the config artifacts as first-class components (Q1-A) and
  P-DEP-5's two-part shape (Q3-A) **agree** in the component→target table: **C-DEP-2/C-DEP-3 map to the tier-U PRESENCE half** of
  BUILD-1/BOOT-1 (the entry/config exists + references the frozen `App.jsx` / start command + env shapes), while the **deploy-time
  fact** (actual bundle build / boot) is **explicitly named-not-tested** (observed-never-gated, verified at Infra/deploy) — so it is
  **not** a component-tested mechanism and its absence from the tier-U column is **honest, not a coverage gap**. Every component maps
  to a target; every target's tier-U-testable half maps to a component.
- **NFR-ND-DEP-Fold-2 [cross-cutting patterns are supporting, not orphans]** — **P-DEP-8 (ConfigFormatValidation)** and **P-DEP-11
  (DetectorSelfTestSubstrate)** are **cross-cutting/composing** patterns (a precondition + the shared no-vacuous-scan substrate), not
  1:1-to-a-target patterns — **precedented** by every prior unit's `StructuralGuard`/substrate pattern (e.g. P-OBS-10). The
  traceability table marks them **cross-cutting (supports N targets)**, so they are not read as orphan patterns.
- **NFR-ND-DEP-Fold-3 [ROUTES-1 introspection is env-free / DB-free and import-to-read ≠ edit]** — the Scope-A conftest calls
  `create_app()` **directly** and route registration is **env-free** (the handlers' `Depends(...)` resolve only at request time, never
  invoked by `openapi()`), so ROUTES-1 is `create_app().openapi()["paths"]` — **no live server, no live DB, no env/Settings needed**,
  **reusing the composition-root pass's `create_app()`+`openapi()` mechanism** (Req-Fold-1), **not** the frozen test tree. **Importing
  the production `backend.app.main` read-only to introspect is NOT editing** (NOEDIT-1 forbids *writes* to frozen paths), so **ROUTES-1
  and NOEDIT-1 agree by construction** — the introspection touches nothing.

**No frozen contract re-opened, no live-deploy/DB dependency introduced, no pattern left orphan.** Proceed to generate Part 2.

---

## 5. Constraints & settled items held (not re-opened)
- The frozen FD (**BR-DEP-1..9** + config surfaces + the 6-step lifecycle) + the approved **eleven `NFR-DEP-*`** + Req-Fold-1..3 are
  the substrate — NFR Design **maps** them, re-opening none.
- **No frozen unit edited**; the **CLOSED composition root** + the 17 P1 + U18/U19/U20/U21 untouched (read-only for ROUTES-1's
  in-process introspection); **no new domain route**.
- **SEC-3** (no secret **value** — shapes only); **free-tier / validation-not-production**; **AC-7 provisioned-for not discharged**
  (DEP-FD-Fold-2); the **Q1-B divergence** deployed as-built + documented (DEP-FD-Fold-3, DOC-1); the **`OBS-SINK-DEFERRED` code half +
  `MCP-TRANSPORT-DEFERRED`** composition/application-owned (DEP-FD-Fold-1, SCOPE-1).
- **No new dependency** (`pyyaml` already floored+installed; stdlib `json`/`ast`/`pathlib`); **tier-B N/A + NOT authorized**; the
  **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the
  **23-unit decomposition unchanged**.

---

## 6. Next step (STOP here)
Fill the three `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check (grounded in the
frozen FD + the eleven `NFR-DEP-*` + Req-Fold-1..3; surfacing-and-stopping on any genuine gap), then generate Part 2 —
`nfr-design-patterns.md` (**P-DEP-1..11**, the load-bearing trio's mechanisms spelled out, a validated Mermaid + text alternative,
pattern→target→tier→rigor traceability no orphan) + `logical-components.md` (**C-DEP-\***, the validator + the config artifacts with
the three-category reference-not-own, a validated component Mermaid + text alternative, component→target coverage no orphan) — and
present the standardized 2-option completion message (1. Request Changes / 2. Continue → **Infrastructure Design**). **No NFR-Design
artifacts or code are generated until the answers are in and checked.**
