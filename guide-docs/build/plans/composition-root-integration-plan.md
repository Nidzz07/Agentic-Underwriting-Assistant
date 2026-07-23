# Composition-Root Integration Pass — Plan (Part 1) — **Scope A (backed slice only)**

**Nature**: an **OUT-OF-BAND INTEGRATION PASS** — an explicitly-logged **deviation** from the strict workflow sequence, per CLAUDE.md's **Adaptive Workflow Principle** and `common/workflow-changes.md`. **NOT a numbered unit of work** (consistent with `unit-of-work.md:104-108` — the composition root is *"the in-process wiring across backend units… **not a 24th unit of work**"*). The **23-unit decomposition is unchanged and NOT re-opened**. Logged in `audit.md` via the Change Request Log Format + a `guide-state.md` entry; `execution-plan.md` deliberately untouched (user directive).
**Date**: 2026-07-16 · **Approved scope**: **A — backed slice only** · **Deviation approved in writing**: 2026-07-16.

**Why out-of-band**: Build & Test — the venue the frozen plan names for the composition root's *verification* — **cannot run until all 23 units complete** (`execution-plan.md:266`: "a single Build-and-Test pass **after all units**"; its scope at `:205` includes **groundedness** → U22 `llm-judge` and **trace audit** → U21 `observability`, both P2). The frozen documents give the composition root's **verification** a home but never assign its **authoring** — *"covered by"* ≠ *"written by"*. This pass closes that gap deliberately rather than by drift.

**Plan-gate discipline PRESERVED**: CLAUDE.md's hard rule — *no application code until the Code Generation PLAN is presented and explicitly approved in writing* — still binds. Deviation is in **sequence/venue only**. Part 1 → ambiguity-check → **explicit approval** → Part 2, exactly as all 17 units.

**Status**: **✅ CLOSED — approved as delivered 2026-07-16.** Q1–Q5 answered (§6, all embedded); ambiguity-check re-run CLEAN with CR-Fold-7 surfaced and **resolved as-derived** (§6.6.1, user-confirmed); Part 2 generated (§4 Steps 0–11). **Backend 850→960 / 31 skipped; frontend 486→524; `backend/app` + `src/app` 100%; ESLint clean; no frozen unit touched (mtime-verified).** Summary: `guide-docs/build/composition-root/integration-summary.md`. **This was an out-of-band deviation, NOT a numbered unit** — the 23-unit decomposition is unchanged. **🔴 Q1-B's READ_AUDIT-vs-WIRE-1-§3 divergence remains explicitly OPEN for future deliberate reconciliation (Option C).**

---

## 0. Why Scope A — the finding that set it

Grounding on disk established that the composition root is **not purely "wiring"** for 4 of the 7 routes:

- The Phase-1 schema (`database/migrations/0001_initial_schema.sql`) has **exactly three tables**: `audit_record`, `applicant_profile_snapshot` (a **child of `audit_record` keyed by `decision_id` — written only at commit time**), and `app_user`. There is **no pending-application table and no pending-recommendation table**.
- `audit_store/seams.py` defines `CommitContextProvider` as a **Protocol**; its **only** implementation is `DictCommitContextProvider`, labelled verbatim *"Test/fake provider — a preset recommendation_id -> CommitContext map."* `CommitContext`'s docstring says it is what *"the orchestrator/pipeline supplies"* — deferred **to this composition root**, which is why no unit built it.
- **WIRE-1 has no ingestion route** (R1–R7: nothing creates an application).

⇒ Wiring **R2–R5** would require **inventing the pending-application/recommendation lifecycle** — new domain state no unit designed and no frozen artifact pins. **Scope A refuses to smuggle un-designed domain modelling in under an integration label.** Scope B (in-memory pending store) and C (persistent store + migration `0003`) were presented and **not chosen**; either is its own explicit work if wanted later.

**Scope A therefore wires only what is genuinely backed today, and marks the rest honestly.**

---

## 1. Module map (NEW code — all additive)

### Backend — `backend/app/` (the composition root; per the `unit-of-work.md §2` tree)

| Module | Role |
|---|---|
| `backend/app/__init__.py` | package marker |
| `backend/app/main.py` | **the composition root**: `create_app(...)` factory + module-level `app`. Builds the two engines from `Settings`, constructs `PostgresUserRoleRepository` / `AuthRBAC` / `ApiAuthGuard` / `PostgresAuditRepository` / `AuditService`, registers R1/R6/R7 and the R2–R5 not-wired markers. **Composition only — no domain logic.** |
| `backend/app/dependencies.py` | FastAPI dependency providers: `get_settings` passthrough, the two engines, the services, and `current_identity` (the **stub header-based identity**, Decision 2) |
| `backend/app/errors.py` | the **WIRE-1 §4 envelope**: `{error:{code,message,detail}}` + the frozen status→code table + exception handlers. Own-local; nothing imported from a frozen unit |
| `backend/app/projections.py` | **AuditRecord → WIRE-1 §5 wire shapes**: `DecisionSummary` projection (R6) + the list wrapper `{items, page:{page,size,total}}` + in-app pagination (Decision 4). Pure functions, no I/O |
| `backend/app/routes/session.py` | **R1** `GET /session` |
| `backend/app/routes/decisions.py` | **R6** `GET /decisions?page=&size=` · **R7** `GET /decisions/{decision_id}` |
| `backend/app/routes/not_wired.py` | **R2–R5** — the explicit not-wired marker (Q2) |
| `backend/app/tests/` | integration tests (FastAPI `TestClient`) + structural guards |

### Frontend — author-only, **not runnable** (Decision 5; no bundler — `deploy-config` P2 owns it, deliberately not pulled forward)

| Module | Role |
|---|---|
| `frontend/src/app/httpTransport.js` | the **real transport** satisfying the duck-typed contract every frozen seam expects: `transport(request) -> { ok, body }`, where `request = { method:'GET', path }`. Replaces the injected double **for the backed seams only** |
| `frontend/src/app/sessionClient.js` | **R1** client → `{ user_id, role }` for `RoleProvider` |
| `frontend/src/app/App.jsx` | composes frozen `AppFrame` + `RoleProvider` + `HistoryView` with a **real** `createHistoryFetch(httpTransport)`. **No router** (Decision 6 N/A — no cross-unit navigation is backed). The other four UI units are **not mounted**: nothing real backs their seams under Scope A |
| `frontend/src/app/__tests__/` | Vitest tests |

> **Frontend reality check (accepted, eyes open)**: `App.jsx` + the transport are **authored and Vitest-tested**, not browser-runnable. `ui-queue` / `ui-memo-view` / `ui-approval-gate` / `ui-override-form` remain **unmounted** under Scope A — R2–R5 are not wired, so mounting them would imply backing that does not exist.

---

## 2. Route → unit binding table — **exactly R1/R6/R7 real; R2–R5 not-wired**

| Route | WIRE-1 shape | Status | Bound to (frozen units, **imported never edited**) | Engine |
|---|---|---|---|---|
| **R1** `GET /session` | `{user_id, role}` | ✅ **REAL** | `auth_rbac.PostgresUserRoleRepository(engine).get_role(user_id)` → `auth_rbac.to_role`; identity from the stub header (Decision 2) | **`DATABASE_URL`** — see §2.1 |
| **R2** `GET /applications?page=&size=` | list of `ApplicationSummary` | ⛔ **NOT WIRED** | *no pending-application store exists* (§0) | — |
| **R3** `GET /applications/{application_id}` | `ApplicantProfile` | ⛔ **NOT WIRED** | *no pre-commit profile store* (`applicant_profile_snapshot` is written only at commit, keyed by `decision_id`) | — |
| **R4** `GET /applications/{id}/memo` | `MemoView` | ⛔ **NOT WIRED** | *no store; no drafting trigger; sync-vs-async undecided (Decision 1 N/A)* | — |
| **R5** `POST /recommendations/{id}/commit` | `CommittedDecision` | ⛔ **NOT WIRED** | `DecisionCommitService` exists **but** requires a real `CommitContextProvider`; only a **test fake** exists (§0) | — |
| **R6** `GET /decisions?page=&size=` | list wrapper of `DecisionSummary` | ✅ **REAL** | `audit_store.AuditService(PostgresAuditRepository(engine)).browse_history()` → §5 projection + **in-app pagination** (Decision 4) | **`AUDIT_READER_URL`** |
| **R7** `GET /decisions/{decision_id}` | `AuditRecord` | ✅ **REAL** | `audit_store.AuditService(...).get(decision_id)`; `None` → **404 `not_found`** | **`AUDIT_READER_URL`** |

> **WIRE-1 additive amendment 2026-07-17 (WIRE1-Fold-4)**: R4's `MemoView` gained an additive `outlier: OutlierResult | null` field (U18 outlier data, on the case-detail view). **No effect on this plan** — R4 stays **NOT WIRED** (a `501` stub) here; the field reconciles whenever R4 is actually backed. **`backend/app/` not touched by that amendment.**

**Consequence, stated plainly**: R6/R7 are exactly the two routes `ui-history` (U9) consumes. **Scope A makes the newest unit work end-to-end against real Postgres, and nothing else.**

**INV-FAITHFUL under Q2-A (CR-Fold-7 — see §6.5).** R5 is a **POST**, so registering its 501 marker (Q2-A) **necessarily puts one POST entry in the route table**. The naive assertion "zero non-GET routes" is therefore *impossible* to combine with Q2-A. The **substantive** guarantee is asserted instead — **zero write-CAPABLE routes**: (i) the **only** non-GET route is the R5 marker; (ii) its handler **raises the 501 marker unconditionally as its first statement**, touching no service; (iii) **no writer engine is ever constructed** (`AUDIT_WRITER_URL` is never read); (iv) **no `DecisionCommitService`, and no `CommitContextProvider` (real or fake), exists anywhere under `backend/app/`**. This is **stronger** than the naive route-table check, since it constrains capability rather than HTTP verbs (INT-FAITHFUL-1).

### 2.1 Two-engine least-privilege binding (grounded in `0002_grants.sql`, not assumed)

`0002_grants.sql` grants `audit_reader` and `audit_writer` **SELECT/INSERT on `audit_record` + `applicant_profile_snapshot` only** — **neither has any grant on `app_user`**. Therefore:
- **R6/R7** (audit reads) → an engine on **`AUDIT_READER_URL`** (SELECT-only; the SEC-4 read-only role — least privilege for a read surface).
- **R1** (`app_user` read) → an engine on **`DATABASE_URL`** (the owner), because no audit role can read `app_user`.
- **No writer engine is constructed** — Scope A has no write path.

---

## 3. Test → `INT-*` target map (all tiers; TestClient integration + structural)

| Target | Assertion | Test | Tier |
|---|---|---|---|
| **INT-WIRE-1** *(load-bearing)* | every wired route's response matches the **frozen WIRE-1 §5 shape exactly** — R1 `{user_id, role}` with `role` the **exact lowercase enum value** (no re-case, §6); R6 `{items:[DecisionSummary], page:{page,size,total}}` with `DecisionSummary = {decision_id, application_id, recommendation_id, action, timestamp}`; R7 the full `AuditRecord` incl. nested `audit_tuple.rule_results` | `test_wire1_shapes.py` (TestClient + a seeded repo) | integration |
| **INT-ERR-1** | the **§4 envelope** `{error:{code,message,detail}}` on every non-2xx; the frozen status→code table honored (**401 `unauthenticated`**, **404 `not_found`**); **no secret VALUE** in `message`/`detail` | `test_error_envelope.py` (table-driven) | integration |
| **INT-AUTH-1** | stub header identity (Decision 2): valid header + known `app_user` → 200 with that role; **missing header → 401 `unauthenticated`**; **unknown user (`get_role` → None) → 401**; `to_role` fail-closes on blank/non-canonical | `test_auth_stub.py` | integration |
| **INT-ENGINE-1** | least-privilege binding (§2.1): audit reads use the **reader** engine; `app_user` reads use the **`DATABASE_URL`** engine; **no writer engine constructed**; asserted by construction-time inspection, not live DB | `test_engine_binding.py` | structural |
| **INT-PAGE-1** | in-app pagination (Decision 4): `page`/`size`/`total` correct; **1-based** page (A4); page *k* returns the right slice; `total` = full count; out-of-range page → empty `items` (**not** an error); `size` bounds respected | `test_pagination.py` | unit (pure projection) |
| **INT-NOTWIRED-1** | **R2–R5 uniformly return the marker** (Q2) in the **§4 envelope shape**; the marker is **distinct from `not_found`** so R7's 404 is never confusable with "unwired"; **no R2–R5 route silently 500s or returns a fabricated body** | `test_not_wired.py` (table-driven over all four) | integration |
| **INT-FAITHFUL-1** | **zero write-CAPABLE routes** (restated per **CR-Fold-7**; Q2-A forces one POST *marker* into the route table): the **only** non-GET route is the **R5 501 marker**; its handler **raises unconditionally as its first statement** and touches no service; **no writer engine** is constructed (`AUDIT_WRITER_URL` never read); **no `DecisionCommitService`** and **no `CommitContextProvider`** (real or fake) exists under `backend/app/` — each with a detector self-test | `test_no_write_route.py` | structural / AST |
| **INT-FROZEN-1** | **no frozen unit is edited** — `backend/app/**` and `frontend/src/app/**` **import** frozen units and define none of their symbols; a scan asserts no file outside those two trees is touched; the 17 units are composed only | `test_frozen_untouched.py` | structural |
| **INT-PROJ-1** | the R6 projection is **faithful**: `action` = `committed_decision.action` **value**, `timestamp` = `audit_tuple.timestamp` **ISO-8601**; **no re-case** of any enum (WIRE-1 §1); the projection **drops no id** | `test_projections.py` | unit |
| **INT-FE-1** | the frontend **real transport** satisfies the duck-typed contract the frozen seams expect (`{method,path}` in → `{ok, body}` out) and is **GET-only** under Scope A; `App.jsx` composes `AppFrame` + `RoleProvider` + `HistoryView` with a real `createHistoryFetch(httpTransport)`; **the four unbacked UI units are not mounted** | `frontend/src/app/__tests__/*.test.{js,jsx}` (Vitest, mocked `fetch` — **no live server**) | component / unit |
| **INT-NOREGRESS-1** | **backend 850 passed / 31 skipped** and **frontend 486 passed** hold; new tests are **additive** | full `pytest backend` + `npm run test:cov` | gate |

**No target is orphaned**; every wired route has a shape test, an error test, and an auth test.

---

## 4. Leaf-first numbered steps (Part 2 — **NOT executed**; on explicit approval)

- [ ] **Step 0 — Scaffold**: `backend/app/{__init__,main,dependencies,errors,projections}.py`, `backend/app/routes/`, `backend/app/tests/`. Confirm `pytest backend` still collects 850/31 (no route registered yet).
- [ ] **Step 1 — `errors.py`**: the WIRE-1 §4 envelope + frozen status→code table + handlers. (INT-ERR-1)
- [ ] **Step 2 — `projections.py`**: `AuditRecord → DecisionSummary`, the list wrapper, in-app pagination. Pure, no I/O — testable standalone. (INT-PAGE-1, INT-PROJ-1)
- [ ] **Step 3 — `dependencies.py`**: `Settings` → the **two** engines (§2.1) → repositories → services; the **stub `current_identity`** (Decision 2). (INT-ENGINE-1, INT-AUTH-1)
- [ ] **Step 4 — `routes/session.py`** (**R1**). (INT-WIRE-1, INT-AUTH-1)
- [ ] **Step 5 — `routes/decisions.py`** (**R6 + R7**), incl. R7 `None` → 404 `not_found`. (INT-WIRE-1, INT-ERR-1, INT-PAGE-1)
- [ ] **Step 6 — `routes/not_wired.py`** (**R2–R5** marker, uniform). (INT-NOTWIRED-1)
- [ ] **Step 7 — `main.py`**: `create_app()` composing Steps 1–6; module-level `app`. (INT-FAITHFUL-1)
- [ ] **Step 8 — Backend structural guards**: no-write-route scan, frozen-untouched scan, engine-binding — each with a detector self-test. (INT-FAITHFUL-1, INT-FROZEN-1, INT-ENGINE-1)
- [ ] **Step 9 — `frontend/src/app/`**: `httpTransport.js` → `sessionClient.js` → `App.jsx`, tests-first. (INT-FE-1)
- [ ] **Step 10 — Gate**: `pytest backend` **850/31 + new, no regression**; `npm run test:cov` **486 + new, no regression**; ESLint clean; every frozen tree untouched (mtime-verified).
- [ ] **Step 11 — Summary**: `guide-docs/build/composition-root/integration-summary.md` + `testresults.txt` refreshed + `guide-state.md` back-annotated + `audit.md` appended + this plan re-saved with answers embedded.

---

## 5. HOLDS (binding through Part 2 — restated from the user's directive)

- **All 17 frozen units imported/composed, NEVER edited.** **No file under any frozen `backend/<unit>/` or `frontend/src/<unit>/` tree is created or modified** (INT-FROZEN-1, mtime-verified).
- **WIRE-1 §4/§5 shapes honored EXACTLY**, verified via **FastAPI TestClient** integration tests. Enum values by-value, **never re-cased** (§1).
- **Advisory-only + INV-FAITHFUL preserved** — Scope A registers **no write route at all** (INT-FAITHFUL-1).
- **Backend 850/31 and frontend 486 must not regress** (INT-NOREGRESS-1); new tests additive.
- **Invents no domain state** — no pending store, no ingestion route, no `CommitContextProvider` (§0).
- **`audit-store` stays frozen** — pagination is in-app (Decision 4). **`database` stays frozen** — no migration `0003`.
- **No P2 unit started. tier-B NOT authorized. `audit_store` Docker-guard gap untouched. `execution-plan.md` untouched. The 23-unit decomposition unchanged — this is not a 24th unit.**

---

## 6. Open `[Answer]` questions — specific to Scope A

### Q1 — R6/R7 authorization: a **genuine conflict between two frozen artifacts** (surfaced by the ambiguity-check; see §6.5) — **ANSWERED: B**
`auth_rbac.roles.PERMISSION_MATRIX` grants `READ_AUDIT` to **underwriter + auditor but NOT admin** (`Role.ADMIN: frozenset({MANAGE_USERS, MANAGE_CONFIG})`). **WIRE-1 §3 says R6/R7 are "authenticated" (any role).** These cannot both hold for an `admin` caller. *(Note: `ui-history`'s frozen BR-HIST-7 already reasoned about the mirror of this and sided with WIRE-1 — it deliberately did **not** use `RoleGate can="read"` precisely because that "would cosmetically exclude admin, a UI/contract divergence from R6/R7's any-authenticated".)*
- **A.** **Authenticate only** — any authenticated role may read R6/R7; `READ_AUDIT` not enforced on these routes. **Matches WIRE-1 §3 literally and matches the frozen `ui-history` client's expectation.** Admin can read history. *(Consistent with the only frozen client that exists.)*
- **B.** **Enforce `READ_AUDIT`** via `ApiAuthGuard` — matches auth-rbac's policy datum; **admin → 403 `forbidden`**, diverging from WIRE-1 §3's "authenticated" and from the frozen UI's stated expectation.
- **C.** Enforce `READ_AUDIT` **and** amend WIRE-1 §3's wording to "authenticated, `READ_AUDIT`-permitted". *(Edits a frozen contract — flagged, not assumed.)*

`[Answer]:` **B — enforce `READ_AUDIT` on R6/R7 via the existing auth-rbac guard, exactly as the frozen `PERMISSION_MATRIX` defines it** (underwriter + auditor pass; **admin → 403**). This **applies an already-frozen policy verbatim rather than deciding to override it**, consistent with the project's established principle that **auth-rbac is the single-sourced authority for RBAC and the server is always the real gate**. **WIRE-1 is NOT amended in this pass.** The resulting divergence — WIRE-1 §3 says R6/R7 are "authenticated" (any role) while `PERMISSION_MATRIX` excludes admin from `READ_AUDIT` — is **recorded explicitly and honestly** here and in the code summary as a **flagged, UNRESOLVED contract tension** awaiting a future deliberate reconciliation (Option C). **This pass does not resolve it.** Note also that **BR-HIST-7 (ui-history's FD) sided with WIRE-1's reading on the client**, so this is a **genuine two-sided divergence, not a one-sided oversight**.

### Q2 — the R2–R5 "not wired" marker: status + code (**extends the frozen §4 status table**)
WIRE-1 §4's status table is **frozen** and has **no** status for "route exists but is deliberately unwired" (400/401/403/404/409/422/500 only).
- **A.** **`501` + code `not_implemented`**, in the **§4 envelope shape**. Honest and unambiguous; **additively extends §4's table by one row** (documented as part of this deviation, not a silent change). Distinct from `not_found` so R7's 404 stays unconfusable. *(Recommended.)*
- **B.** **Do not register R2–R5 at all** — FastAPI's default 404 with a **non-WIRE-1 body**; collides semantically with R7's `not_found` and breaks the envelope guarantee.
- **C.** **`503` + `service_unavailable`** — implies a transient outage rather than a deliberate scope boundary.

`[Answer]:` **A — an honest `501 not_implemented`** for the R2–R5 not-wired marker, **additively extending** WIRE-1's status table (**not replacing or contradicting any existing status**). Documented as an **additive extension, not a modification**, in the same divergence-tracking spirit as Q1.

### Q3 — R6 result ordering (**a real UX/contract choice the composition root must make**)
`PostgresAuditRepository.browse()` orders by **`decision_id`** (`.order_by(audit_record.c.decision_id)`) — **not** chronologically. `ui-history` renders rows in **backend-delivered order and re-sorts nothing** (BR-HIST-5), so whatever R6 emits *is* what the auditor sees. A decision **history** would conventionally read newest-first.
- **A.** **Pass through `browse()`'s `decision_id` order** unchanged — the thinnest wiring; audit-store's order is authoritative. History displays in id order, which may look arbitrary to an auditor.
- **B.** **Re-sort in-app by `audit_tuple.timestamp` DESC** (newest first) before paginating — the conventional history UX; audit-store stays frozen (sorting is the composition root's projection concern). Adds an in-app ordering decision not pinned by any frozen artifact.
- **C.** Push ordering into `audit-store`. *(Rejected — edits a frozen unit; contradicts Decision 4's spirit.)*

`[Answer]:` **A — leave R6's ordering as `browse()`'s existing `decision_id` order.** Do **not** invent a timestamp-sort requirement that would require touching frozen `audit-store`. Documented: **no frozen artifact pins R6's order**, so this is the **honest current behavior, not a designed guarantee**.

### Q4 — the stub identity header (Decision 2's concrete shape)
- **A.** **`X-User-Id: <user_id>`** — resolved against `app_user` via `PostgresUserRoleRepository.get_role`; **missing → 401 `unauthenticated`**; **unknown/blank/non-canonical role → 401** (`to_role` fail-closes). Single header, trivially replaceable by the real OIDC handshake later (WIRE-1 A6's "abstract seam, deferred"). *(Recommended.)*
- **B.** `Authorization: Bearer <user_id>` — cosmetically closer to the eventual handshake but implies a token semantic that does not exist (no validation, no issuer) — arguably **more** misleading than A.

`[Answer]:` **A — the `X-User-Id` stub header**, not `Bearer` (which would imply a token semantic that does not exist yet). Matches the **"abstract seam, deferred"** framing WIRE-1 §6/A6 already established.

### Q5 — `Settings` requires `GEMINI_API_KEY`, which Scope A never uses
`secrets_config.Settings` is **fail-closed with all six fields required and no defaults**; it is **frozen**. So the Scope-A app **cannot boot without `GEMINI_API_KEY` set**, despite wiring no LLM.
- **A.** **Accept** — set a dummy value in `.env`/CI. The fail-closed design is working as intended; `secrets-config` stays frozen; no carve-out. Documented as a known Scope-A friction. *(Recommended — the alternatives all touch a frozen unit or bypass SEC-3's single source.)*
- **B.** Read `os.environ` directly for only the needed vars — **bypasses `secrets-config`**, violating SEC-3's single-source control.
- **C.** Make `GEMINI_API_KEY` optional in `Settings` — **edits a frozen unit** and weakens its fail-closed guarantee.

`[Answer]:` **A — accept a dummy `GEMINI_API_KEY`** value in `Settings`, since Scope A wires no LLM. Rationale documented: **`Settings`' existing shape requires it, no frozen unit is touched, and no real key or cost is incurred**.

---

## 6.5 Ambiguity-check (RUN 2026-07-16) — **NOT CLEAN: one genuine gap → SURFACE-AND-STOP**

Run against the approved Scope A + decisions 2/4/5 + the frozen WIRE-1, `unit-of-work.md`, `auth_rbac`, `audit_store`, `database` migrations and `secrets_config` — all re-read on disk. **Unlike all 17 prior units, this check did NOT come back clean.** One item is a genuine conflict **between two frozen artifacts** that cannot be resolved by improvisation:

- **🔴 CR-Fold-1 (GENUINE GAP — Q1, surface-and-stop).** `auth_rbac.roles.PERMISSION_MATRIX` grants **`READ_AUDIT` to underwriter + auditor but NOT to admin**. **WIRE-1 §3 marks R6/R7 "authenticated" (any role).** For an `admin` caller these two **frozen** artifacts give opposite answers (200 vs 403). Neither is derivable from the other and no fold reconciles them. Corroborating evidence that this is real, not a misreading: the frozen `ui-history` FD (**BR-HIST-7**) independently hit the **mirror** of this and recorded it — it deliberately declined `RoleGate can="read"` because that "would cosmetically exclude `admin`… a UI/contract divergence from R6/R7's any-authenticated". So the **client** already sided with WIRE-1; the **backend policy datum** sides against it. **The composition root is the first place both meet, which is exactly why it surfaces here and not in any unit.** → **Q1. Not improvised.**
- **🟡 CR-Fold-2 (contract extension — Q2).** WIRE-1 §4's status table is **frozen** and has **no** status meaning "registered but deliberately unwired". Any honest marker (501 `not_implemented`) **additively extends** that table. Small and documented — but it *is* a contract touch, so it is surfaced rather than assumed. → **Q2.**
- **🟡 CR-Fold-3 (unpinned ordering — Q3).** `browse()` orders by **`decision_id`**, not `timestamp`; `ui-history` re-sorts nothing (BR-HIST-5). So R6's emitted order **is** the auditor's view, and no frozen artifact pins it. → **Q3.**
- **🟢 CR-Fold-4 (accepted consequence — NOT a question).** `PostgresAuditRepository.browse()` is **N+1 by construction**: it selects all `decision_id`s, then calls `_load_one` per id. With **in-app** pagination (Decision 4) the server therefore **materializes every record to serve one page**. This is the accepted cost of keeping `audit-store` frozen — the alternative (limit/offset in the repository) edits a frozen unit, which Decision 4 explicitly declined. Harmless at Phase-1 data volumes; **flagged honestly, not masked**, and recorded as a known limitation rather than silently absorbed. Note the client-side **PERF-1** ("one bounded page") is still satisfied — the bounding is real at the wire, not at the DB.
- **🟢 CR-Fold-5 (frozen fail-closed friction — Q5).** `Settings` requires all six env vars incl. `GEMINI_API_KEY`, which Scope A never uses; `secrets-config` is frozen and deliberately fail-closed. Every alternative touches a frozen unit or bypasses SEC-3. → **Q5**, recommendation **A (accept)**.
- **🟢 CR-Fold-6 (RESOLVED by grounding — no gap).** Which engine serves R1 was initially open; `0002_grants.sql` settles it — `audit_reader`/`audit_writer` hold grants on the **audit tables only**, **neither can read `app_user`** — so R1 must use the **`DATABASE_URL`** engine and R6/R7 the **`AUDIT_READER_URL`** engine (§2.1). Derived from the frozen DDL, not chosen.

**Verdict**: **STOP on Q1.** Q1 is a substantive conflict between two frozen artifacts and is the user's call — picking either side silently would bury a real contract divergence inside a "wiring" pass. Q2–Q5 are scoped choices with recommendations. **No code until Q1 is answered and Part 2 is explicitly approved.**

---

## 6.6 Ambiguity-check **RE-RUN** (2026-07-16, against the five filled answers) — **CLEAN, with one NEW fold surfaced (CR-Fold-7)**

Re-run against Q1-B / Q2-A / Q3-A / Q4-A / Q5-A + everything previously verified. **CR-Fold-1 is now answered (Q1-B) — the divergence is not resolved, it is deliberately RECORDED (below).** CR-Fold-2/3/5 are answered; CR-Fold-4/6 unchanged. **One NEW fold appeared, created by the answers themselves:**

- **🟡 CR-Fold-7 (NEW — surfaced by Q2-A; resolved by derivation, NOT improvised; flagged for confirmation at the gate).** Q2-A directs that **R2–R5** each return the 501 marker. **R5 is `POST /recommendations/{recommendation_id}/commit`** — so honoring Q2-A **necessarily registers one POST route**. That **collides with the literal reading** of the restated hold *"confirm structurally that no write route is registered."* The two instructions cannot both hold literally: dropping the R5 marker contradicts Q2-A; registering it puts a POST in the route table. **There is exactly one reading under which both are satisfiable**, and it is the substantive one the hold's own reason-clause points at (*"since R5 stays unwired"*): the guarantee is about **write CAPABILITY**, not HTTP verbs. Realized as the **stronger** assertion in §2/§3 (only non-GET route is the marker; handler raises unconditionally before touching anything; **no writer engine**, **no `DecisionCommitService`**, **no `CommitContextProvider`** anywhere under `backend/app/`). **Surfaced rather than absorbed; the user can direct the literal reading instead — i.e. drop the R5 marker and leave R5 unregistered — at the diff gate.**

### 🔴 RECORDED DIVERGENCE (Q1-B) — flagged, UNRESOLVED, deliberately carried

**`READ_AUDIT` on R6/R7 vs WIRE-1 §3 — a genuine TWO-SIDED contract divergence this pass does NOT resolve.**

| Side | Says | Consequence for `admin` on R6/R7 |
|---|---|---|
| **WIRE-1 §3** (frozen contract) | R6/R7 are **"authenticated"** — any role | **200** |
| **`auth_rbac.PERMISSION_MATRIX`** (frozen policy datum) | `READ_AUDIT` = underwriter + auditor; **admin excluded** | **403** |

**Resolution applied (Q1-B)**: enforce `READ_AUDIT` **verbatim** via the existing `ApiAuthGuard` — **applying an already-frozen policy, not deciding to override it**; auth-rbac is the single-sourced RBAC authority and the server is always the real gate. **WIRE-1 is NOT amended in this pass.**

**Why this is a genuine two-sided divergence and not a one-sided oversight**: the frozen **`ui-history` FD (BR-HIST-7)** independently hit the **mirror** of this and **sided with WIRE-1** — it deliberately declined `RoleGate can="read"` because that "would cosmetically exclude `admin`… a UI/contract divergence from R6/R7's any-authenticated". **So the client already assumed any-authenticated while the server now enforces `READ_AUDIT`.** For `admin`, the frozen UI would render a history surface that the server answers with **403**. *(Practical blast radius today is nil — the same BR-HIST-7 notes "admin has no UI journey anyway" — but the divergence is real and is carried openly, not papered over.)*

**Status: UNRESOLVED — carried forward for a future deliberate reconciliation (Option C: enforce `READ_AUDIT` **and** amend WIRE-1 §3's wording to "authenticated, `READ_AUDIT`-permitted").** Recorded here, in the code summary, in `audit.md` and in `guide-state.md`. **This composition-root pass does not resolve it and must not be read as having done so.**

### 🟡 RECORDED ADDITIVE EXTENSION (Q2-A)
**`501 not_implemented` is an ADDITIVE extension to WIRE-1 §4's status table — not a modification.** It **replaces and contradicts no existing status**; every frozen status (400/401/403/404/409/422/500) keeps its exact meaning; the envelope shape is unchanged. Recorded in the same divergence-tracking spirit as Q1.

### 🟢 RECORDED HONEST-BEHAVIOR NOTE (Q3-A)
**No frozen artifact pins R6's ordering.** R6 emits `browse()`'s **`decision_id`** order. This is the **honest current behavior, not a designed guarantee** — `ui-history` re-sorts nothing (BR-HIST-5), so `decision_id` order is what an auditor sees. Not a timestamp sort; inventing one would have required touching frozen `audit-store`.

**Verdict: CLEAN to proceed to Part 2** — no *unresolved-and-blocking* gap remains. Q1's divergence is **answered (B) and consciously recorded as unresolved**, which is a decision, not a gap. CR-Fold-7 is surfaced with its single coherent reading and flagged for confirmation at the diff gate.

### 6.6.1 CR-Fold-7 — RESOLVED (user-confirmed at the diff gate, 2026-07-16)

The user reviewed the diff and **confirmed CR-Fold-7's resolution as-derived**: *"including CR-Fold-7's resolution as-derived (the write-capability property, not a literal verb count) — I did not mean the literal reading; asserting the stronger structural guarantee was the correct call and I would have made the same choice."* The **write-CAPABILITY** guarantee (only non-GET route is the R5 marker, which raises before touching anything; no writer engine; no `DecisionCommitService`/`CommitContextProvider`; no repository write call — `test_no_write_route.py`) is the **final, approved** realization. The literal verb-count reading is **not** adopted; the R5 marker stays registered (Q2-A) and INV-FAITHFUL holds by capability, not by counting verbs. **This fold is closed.**

---

## 7. Gate

**Part 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** `[Answer]` tags Q1–Q5 are **BLANK**. The ambiguity-check has been **run and presented** (per the user's instruction to run it after presenting the plan) — **§6.5 below**. On the filled answers + **explicit approval**, execute §4 Steps 0–11 leaf-first / tests-first, marking each `[x]`. **NO code generated in Part 1; `backend/app/` NOT created; no frontend entry point created.** All 17 frozen units + WIRE-1 UNTOUCHED; backend 850/31 + frontend 486 must not regress; tier-B NOT authorized; no P2 unit started; `execution-plan.md` untouched.
