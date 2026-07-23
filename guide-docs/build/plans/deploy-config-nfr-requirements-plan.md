# NFR Requirements Plan (Part 1) — `deploy-config` (EPIC-6 / U23, Phase 2)

**Phase / Stage**: BUILD → NFR Requirements, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `deploy-config` (U23) · **FD ✅ (approved 2026-07-19)** → **NFR Requirements ← here (the 2nd of its 5 stages)**.
**Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Date**: 2026-07-19 · **Depth**: **lighter** (consistent with FD;
comprehensive reserved for Infrastructure Design).
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR artifact generated; no code; no deploy files. Stop after this plan.**

Built **ON** the frozen FD (`domain-entities.md` config surfaces + reference-not-own boundary · `business-rules.md` **BR-DEP-1..9**
· `business-logic-model.md` the 6-step deploy lifecycle + INV-DEP-*) and the folds **DEP-FD-Fold-1..3** — **re-opening none**.

---

## 1. The central tension this stage must resolve (stated up front)

`deploy-config` is the **first genuinely DECLARATIVE unit** in the build — its deliverables are config files (`render.yaml`/
`vercel.json`/frontend build config/env manifest) + a deploy doc, **not application logic**, and the FD (Q5-A) records it **may need
no `backend/deploy_config/` Python package at all**. Every prior unit's NFR targets were **pytest teeth over Python code**; here the
**testable surface is different in kind**: **config-validation / file-presence / structural-scan** checks, plus a few facts that are
**inherently Infrastructure-Design/Code-Gen-verified** and can only be **named** at this stage. The tier convention still holds —
**no live cloud deploy at tier-U, no secret values in tests, a detector self-test on every structural scan** — but the *mechanism*
shifts from "assert Python behavior" to "validate config + scan committed artifacts." **Q1/Q3 below decide this explicitly; the plan
does not pre-assume a pytest-only shape.**

---

## 2. Tier convention (verbatim, adapted to a declarative unit)
No **live cloud deploy** at tier-U (no Render/Vercel API call, no real build-and-push, no network, no key); **no secret VALUE in any
test or committed artifact**; validation runs against the **committed config files + the deploy doc** (offline); **a detector
self-test on every structural/format scan** (the project's no-vacuous-scan discipline — extended even here); **observed-never-gated**
where a target is inherently a deploy-time fact; **tier-B N/A + unauthorized**. The **31 skips + 5 pre-existing `audit_store` Docker
errors stay unchanged** (U23 adds none).

---

## 3. Draft target map — all 9 BR-DEP mapped, NO ORPHAN + the testability split

| BR-DEP | → NFR-DEP target | Tier / mechanism (draft) |
|---|---|---|
| **BR-DEP-1** (no frozen/composition-root edit) | **NFR-DEP-NOEDIT-1** *(LOAD-BEARING)* | **structural path/mtime scan** — no U23 deliverable modifies any frozen `backend/<unit>/` / `frontend/src/<unit>/` tree or `backend/app/**` / `frontend/src/app/**`; + **detector self-test** (a synthetic frozen-path write is flagged). Mirrors the build-wide mtime/path discipline. |
| **BR-DEP-2** (frontend static bundle for Vercel) | **NFR-DEP-BUILD-1** | **config-presence + shape** (Q1/Q3): the build entry (`index.html` + a `main` mounting frozen `App.jsx`) + build config + `build` script exist and reference the frozen `App.jsx` unmodified. Whether the bundle is *actually built* is an **Infra/Code-Gen fact** (Q3). |
| **BR-DEP-3** (backend boots via fail-closed `Settings`) | **NFR-DEP-BOOT-1** | **config-presence** (Q1/Q3): the Render service config names a start command running `backend.app.main:app` + the env manifest lists the six required shapes. Actual boot is an **Infra/deploy-time fact** (named, no tier-U teeth — Q3). |
| **BR-DEP-4** (SEC-3 shapes-only) | **NFR-DEP-SEC3-1** *(LOAD-BEARING)* | **secret-value scan over committed artifacts** + **detector self-test** (a synthetic `LANGFUSE_SECRET_KEY="sk-…"` is flagged) — the no-vacuous-scan discipline extended to a declarative unit. |
| **BR-DEP-5** (free-tier / validation not production) | **NFR-DEP-FREETIER-1** | **config scan** — platform configs name **free-tier plans only**; no paid-tier token; the deploy is labelled validation/staging. |
| **BR-DEP-6** (R2–R5 stay `501`; no domain state) | **NFR-DEP-ROUTES-1** | **route-table equivalence** — the deployed app's routes == the frozen composition root's (R1/R6/R7 + the four R2–R5 markers); **no new route file** under `backend/app/`; U23 adds none. |
| **BR-DEP-7** (honest partial-deploy documentation) | **NFR-DEP-DOC-1** | **⚑ Q2 decides**: a **checklist-completeness** assertion (required sections present: live-vs-`501` split · Q1-B divergence · AC-7 contingency · free-tier · env-shapes) **OR** a governance/review item (like SEC-1 has been). |
| **BR-DEP-8** (OBS deployment-half in / code+MCP out) | **NFR-DEP-SCOPE-1** | **structural scan** — U23 deliverables include the scrape/dashboard/env config but **no** callback-attachment code into `main.py` and **no** MCP transport module; env vars are **set-not-consumed** by U23. |
| **BR-DEP-9** (advisory-only trivial) | **NFR-DEP-ADVISORY-1** | **governance** — no U23 deliverable declares/emits a `Recommendation`/verdict or any domain decision (config only). |

**Plus** **NFR-DEP-SEC-1** (Security-Guardrails governance — SEC-3 the load-bearing one here) as the standing governance target.

---

## 4. Clarifying questions (fill each `[Answer]:` tag)

Letter after each `[Answer]:` tag; if none fit, choose the last (Other) and describe. These decide the **NFR tier/mechanism** — they
do **not** re-open the FD, BR-DEP-1..9, or the folds.

## Question 1 — Does a unit this declarative have a meaningful tier-U TEST SURFACE, or are its targets necessarily config-validation/scan checks?
Every prior unit's NFR targets were **pytest teeth over Python code**. `deploy-config`'s deliverables are config files + a doc.

A) **Hybrid, config-validation-led — pytest is the RUNNER, but the teeth are file-presence / schema / structural-scan checks over
   committed artifacts, not application-behavior assertions.** The unit HAS a real tier-U surface, but it is **different in kind**:
   (a) **structural/path scans** (NOEDIT-1, SCOPE-1, ROUTES-1) — the same AST/path discipline prior units used, now over U23's
   deliverables + a frozen-tree path check; (b) **secret-value scans** (SEC3-1) with detector self-tests; (c) **config-format
   validation** (FREETIER-1, and, if the configs are YAML/JSON, a **schema/parse** check that `render.yaml`/`vercel.json` are
   well-formed and name the expected keys); (d) **presence/reference checks** (BUILD-1, BOOT-1) that the build entry + start command
   + env manifest shapes exist and reference the frozen entrypoints. **pytest** remains the runner (no new dependency); the assertions
   read files, not behavior. A **few** targets (BUILD-1's actual bundle, BOOT-1's actual boot) are **inherently deploy-time facts**
   NAMED here without tier-U teeth (Q3).
B) No meaningful tier-U surface — defer ALL verification to Infrastructure Design / a manual deploy check (rejected — NOEDIT-1 /
   SEC3-1 / ROUTES-1 / SCOPE-1 are **genuinely tier-U-scannable** and load-bearing; skipping them would drop the build's
   no-frozen-edit + SEC-3 + no-vacuous-scan discipline exactly where a config unit could silently violate it).
C) Full pytest teeth as if it were application code (rejected — over-claims; there is no application behavior to assert; most
   "teeth" would be vacuous or fabricated).
D) Other (describe after [Answer]:)

[Answer]: A

## Question 2 — How is BR-DEP-7 (honest partial-deploy documentation) made pass/fail-testable?
It is fundamentally a documentation-completeness requirement, not executable logic.

A) **A lightweight checklist-completeness assertion**: the deploy doc must contain a set of **required sections/markers** (the
   live-vs-`501` route split · the Q1-B divergence · AC-7's contingency · free-tier · the env-shape list), and a scan asserts each
   **required marker is present** (+ a detector self-test: a doc missing a section is flagged). This gives BR-DEP-7 **real
   non-vacuous teeth** without asserting prose quality — the same "structure present, content is the author's" line the header-comment
   deliverables drew.
B) **Treat it as a governance/review item** (like SEC-1 has been in every prior unit) — recorded, reviewed, not machine-checked
   (available if you prefer; weaker — a required section could silently go missing).
C) Other (describe after [Answer]:)

[Answer]: A

## Question 3 — Proceed as if there will be Python-testable code, or explicitly plan a HYBRID (mostly file/schema/scan checks, few or no pytest behavior teeth)?
The FD (Q5-A) records U23 may need **no `backend/deploy_config/` Python package** at all.

A) **Plan an explicit HYBRID, and record which targets are inherently deploy-time facts NAMED without tier-U teeth.** Most NFR-DEP-*
   are **config-validation / structural-scan / presence** checks (run under pytest as the runner, reading committed files); the tests
   likely live in a **`tests/`-style location that scans the repo's committed deploy artifacts** (exact home a Code-Gen decision).
   **BUILD-1's actual bundle build + BOOT-1's actual backend boot are inherently Infrastructure-Design/deploy-time facts** — named as
   targets with their acceptance stated as *"verified at Infra/deploy, not tier-U"* (observed-never-gated), **not** given fabricated
   tier-U teeth. This keeps every target honest: teeth where a committed artifact can be scanned, named-only where the fact is
   deploy-time. **No new dependency** beyond pytest (+ a YAML/JSON parse if the configs are YAML — Q-tech, resolved in Part 2's
   tech-stack-decisions).
B) Proceed as if a full Python package with behavior teeth will exist (rejected — contradicts FD Q5-A; would invent code the unit
   does not need).
C) Defer the code/no-code decision entirely to Code-Gen and write NFR targets tooling-agnostically (partially — the layout IS a
   Code-Gen decision, but the NFR stage must still pin the **mechanism class** per target so Infra/Code-Gen have a testable contract;
   A does this while leaving the file home open).
D) Other (describe after [Answer]:)

[Answer]: A

---

## 4.5 Mandatory ambiguity-check (RAN against the three answers + the frozen FD) → **CLEAN (3 folds; no surface-and-stop)**

Grounded in the frozen FD (BR-DEP-1..9 + config surfaces + DEP-FD-Fold-1..3) + the tier convention. The three user-flagged checks
each resolve with a concrete, in-scope mechanism:

- **NFR-DEP-Req-Fold-1 [check i] — ROUTES-1 is a STATIC comparison against the committed composition-root SOURCE, no live deploy.**
  U23 has no runtime access to `backend/app/`, and none is needed: the composition-root **route table is a fixed, committed fact** in
  `backend/app/routes/{session,decisions,not_wired}.py` + `main.py`'s router registration. ROUTES-1 is a **static/structural scan**
  that (a) the committed route set is exactly R1/R6/R7 + the four R2–R5 markers (read from the frozen route decorators / `main.py`
  registration, AST or the FastAPI `app.openapi()["paths"]` built **in-process without a live server** — the same TestClient-free
  introspection Scope-A used), and (b) **no U23 deliverable adds a route file** under `backend/app/`. No Render/Vercel call, no live
  deploy. **Detector self-test**: a synthetic extra route (or a synthetic new route file path) is flagged.
- **NFR-DEP-Req-Fold-2 [check ii] — DOC-1's "marker present" is a PRECISE structured check, not a vague heading match.** Each
  required section is keyed to an **explicit, unambiguous marker token** the deploy doc must carry — a canonical heading string **and**
  a machine-checkable anchor (e.g. a required literal like `ROUTE-STATUS:` / `Q1-B-DIVERGENCE:` / `AC-7-CONTINGENCY:` /
  `FREE-TIER:` / `ENV-SHAPES:`, exact tokens finalized at Code-Gen). The scan asserts **each required token is present** (not merely
  "some heading exists"). **Detector self-test**: a doc with a required token removed is flagged; a doc with only an unrelated heading
  does **not** pass (the scan matches the token set, not any heading) — so the check cannot pass vacuously on an unrelated section.
- **NFR-DEP-Req-Fold-3 [check iii] — a detector self-test on EVERY structural/scan target, not just the two load-bearing ones.**
  The project's no-vacuous-scan discipline applies to **all five scan-bearing targets**: **NOEDIT-1** (synthetic frozen-path write
  flagged), **SEC3-1** (synthetic `LANGFUSE_SECRET_KEY="sk-…"` flagged), **ROUTES-1** (synthetic extra route/route-file flagged),
  **SCOPE-1** (synthetic callback-attachment into `main.py` / synthetic MCP-transport import flagged), **DOC-1** (missing-section
  flagged) — each carries its **own** detector self-test + a **non-vacuity** assertion that the scan sees the real committed
  artifacts. FREETIER-1 (a config-token scan) likewise gets one (a synthetic paid-tier token flagged). BUILD-1/BOOT-1 are
  **presence/reference** checks (not behavior scans) whose deploy-time halves are **named observed-never-gated** (Q3) — they carry a
  presence-detector (a synthetic missing entry flagged) but assert no deploy behavior.

**No frozen contract re-opened, no live-deploy dependency introduced, no secret value surfaced.** Proceed to generate Part 2.

---

## 5. Constraints & settled items held (not re-opened)
- The frozen FD (**BR-DEP-1..9** + config surfaces + reference-not-own + the 6-step lifecycle + DEP-FD-Fold-1..3) is the substrate —
  NFR Requirements **maps** it, re-opening none.
- **No frozen unit edited**; the **CLOSED composition root** + the 17 P1 + U18/U19/U20/U21 untouched; **no new domain route**.
- **SEC-3 / BR-SEC-6**: no secret **value** in any test or artifact — shapes only. **Free-tier only** (NFR-CONSTRAINTS-1);
  **validation/staging**, not production (NFR-DEPLOY-1 / OOS-4).
- **AC-7** is **provisioned-for, not dischargeable** here (DEP-FD-Fold-2); the **Q1-B divergence** is deployed as-built + documented,
  not resolved (DEP-FD-Fold-3); the **`OBS-SINK-DEFERRED` code half + `MCP-TRANSPORT-DEFERRED`** stay composition/application-owned
  (DEP-FD-Fold-1).
- **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged);
  **no other unit started**; the **23-unit decomposition unchanged**.

---

## 6. Next step (STOP here)
Fill the three `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check (grounded in the
frozen FD + the tier convention; surfacing-and-stopping on any genuine gap), then generate Part 2 — `nfr-requirements.md` (the
`NFR-DEP-*` targets, each pass/fail + acceptance + tier + rigor; the load-bearing NOEDIT-1/SEC3-1 pair; traceability, no orphan; the
Security-Guardrails table) + `tech-stack-decisions.md` (the config-validation tooling; no new dependency unless a genuine one — e.g.
a YAML parser — is surfaced and flagged) — and present the standardized 2-option completion message (1. Request Changes / 2. Continue
→ **NFR Design**). **No NFR artifacts or code are generated until the answers are in and checked.**
