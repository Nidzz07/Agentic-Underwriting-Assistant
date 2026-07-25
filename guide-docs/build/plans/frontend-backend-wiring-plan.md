# Frontend ↔ Backend Wiring — SCOPING PLAN

**Kind**: Post-BUILD scoping pass (not a per-unit-loop stage) · **Date**: 2026-07-23
**Status**: **SCOPING ONLY — NO CODE GENERATED.** Stopped at the plan-file gate.
**Baseline**: `main` @ `cb06057`, working tree **clean** · frontend suite re-run **live: 682 passed / 137 files / 0 failed** · backend suite carried forward **1578 / 0 / 43 / 5 / 99.87%** (not re-run this pass) · register **24 tracked** (17 open / 3 discharged / 4 narrowed).

**Six `[Answer]` tags below are BLANK. Nothing is pre-filled and nothing is improvised.**

---

## 1. Ground truth — reconstructed from disk, not from any summary

Everything in this section was read off the actual files this session. **Three premises in the brief are corrected by disk**, and each materially changes what "connect the frontend" means.

### 1.1 ⚑ CORRECTION 1 — the four fetch seams are **not** author-only stubs. They are **complete**.

The brief asked whether each seam is a TODO, a mock returning hardcoded data, a `NotImplementedError`, or something pointing at a placeholder URL. **It is none of those.** All four are fully-implemented factories:

| Seam | Path | Exports | What it actually does when called |
|---|---|---|---|
| memo | `src/memoView/memoFetchSeam.js` | `buildMemoRequest`, `normalizeError`, `createMemoFetch` | Builds `GET /applications/{id}/memo`, awaits the **injected** transport, resolves `response.body` on `ok`, else rejects with a WIRE-1 §4 envelope |
| commit | `src/approvalGate/commitFetchSeam.js` | `buildMemoRequest`, `buildCommitRequest`, `normalizeError`, `createCommitFetch` | Dual op `{ fetchContext, submitApprove }`; `submitApprove` POSTs `{ action: 'approve' }` to `/recommendations/{id}/commit` |
| override | `src/overrideForm/overrideFetchSeam.js` | `buildMemoRequest`, `buildOverrideRequest`, `normalizeError`, `createOverrideFetch` | Dual op `{ fetchContext, submitOverride }`; `submitOverride` POSTs `{ action: 'override', reason }` — `reason` is a **required positional**, sent verbatim (no trim) |
| outlier | `src/outlierView/fetchSeam.js` | `buildOutlierRequest`, `normalizeError`, `createOutlierFetch` | GET-only (no body builder, no `submit*` — the write path is **structurally absent**); reads the `outlier` slice off the same R4 body |

**There is nothing stubbed inside any of them.** Each is a pure request-builder + failure-normalizer over a duck-typed `transport(request) -> Promise<{ ok, body }>`.

**And the real transport already exists.** `src/app/httpTransport.js` issues a genuine `fetch()` with `Accept: application/json`, a conditional `Content-Type`, and the `X-User-Id` header; it throws on a non-JSON body (which every seam's `normalizeError` is built to catch) and returns `{ ok: response.ok, body: parsed }`.

**And `src/main.jsx` already exists and already composes it** — U23 authored it:

```js
const userId = import.meta.env.VITE_USER_ID;
const transport = createHttpTransport({ baseUrl: '/api', userId });
const seams = createSeams(transport);
createRoot(document.getElementById('root')).render(<StrictMode><App seams={seams} transport={transport} /></StrictMode>);
```

⚑ `App.jsx`'s own header comment — *"this module has no `main.jsx`/`index.html`"* — is **stale**. Both exist (`index.html` references `/src/main.jsx`; U23's frozen `test_build.py` asserts exactly that).

> **Consequence: "implement the fetch seams" is not the work.** The seams need **zero** change. See §2 for what the work actually is.

### 1.2 ⚑ CORRECTION 2 — a frontend identity mechanism **does** exist

The brief asked whether the frontend has any concept of a current user. It does, end to end:

`main.jsx` reads build-time `VITE_USER_ID` → `httpTransport.js` sends it as `X-User-Id` (and **omits the header entirely** when absent) → `backend/app/dependencies.py::current_identity` resolves it against `app_user`, **fail-closing to 401** on missing/blank/unknown/non-canonical. Separately, `sessionClient.js` calls R1 `GET /session` and `loadCurrentRole` **fail-closes to `null`**, which every frozen UI unit already renders identically for.

What is **absent** is a **login UI** — not an identity concept. And that absence is deliberate: WIRE-1 §6 records the role as *"chrome/labelling + client-side affordance only… not an authorization datum"*, with the server as the real gate. See **Q3**.

### 1.3 ⚑ CORRECTION 3 — the claimed live-Postgres verification is **not in the record**

The brief states the backend was *"just manually verified end-to-end against a real local Postgres database (all seven WIRE-1 routes exercised successfully, including a live confirmation that register #19's duplicate-commit guard works correctly)."*

**No such entry exists.** The last audit entry is `DECISION 2 — GATE ACCEPTED (#24 DISCHARGED)` at `2026-07-23T08:02:41Z`; `audit.md` and `guide-state.md` mtimes match it, so nothing was appended after. What **is** recorded is the opposite:

* the seed-script pass states plainly *"TIER-U ONLY, STATED PLAINLY: a real Postgres run has NOT confirmed this end-to-end — no Docker, no live DB here"*, tracked as an outstanding residual on the **#8 precedent** (built and tier-U-proven, live confirmation pending);
* the duplicate-guard observation was a **traced simulation over U24's `InMemoryCaseStore`**, explicitly not a live DB run;
* ⚑ **[⚑ SUPERSEDED 2026-07-25 — the claim in this bullet is INACCURATE; retained verbatim per supersede-not-rewrite. See the correcting note directly below this bullet.]** and **#19 is an OPEN DEFECT, not a working guard** — `drafted → committed` is *never performed*, so *"already-committed recommendation → 409"* is **unenforced** and the same `recommendation_id` can be committed repeatedly. What the trace showed was `claim_for_commit` returning WON then LOST, which is a **different mechanism**.

> **⚑ SUPERSEDING NOTE (2026-07-25) — corrects the bullet immediately above.** The bullet is left in place, unedited, as the historical record of what this scoping pass believed; it is NOT deleted and NOT silently rewritten. This note supersedes it.
>
> **What was wrong.** The bullet calls #19 "an OPEN DEFECT, not a working guard" whose `drafted → committed` transition is "never performed", concluding the already-committed 409 is "unenforced" and "the same `recommendation_id` can be committed repeatedly", and dismissing the `claim_for_commit` WON/LOST result as "a different mechanism". That reads the **pre-fix** state. It predates or was written without accounting for the **2026-07-21 #19 NARROWED fix** — see `audit.md:4456`–`4496` ("REGISTER #19 FIX — IMPLEMENTED AND GREEN" → "#19 NARROWED, NOT DISCHARGED" → "GATE APPROVED AND CLOSED"), which `BUILD-COMPLETION-REPORT.md:295-315` records accurately. (The one literally-true fragment — `drafted → committed` "never performed" — is true only of the *direct single edge*, which was deliberately removed; the transition now runs `drafted → committing → committed`. The bullet uses that narrow truth to reach a false conclusion.)
>
> **Axis 1 — the guard exists, is shipped, tested, and enforced IN-PATH (this is what the bullet gets wrong).** The commit is two-step and the direct edge is deliberately absent: `states.py:65` (the `COMMITTING` state), `states.py:72-76` (`DRAFTED → COMMITTED` "deliberately ABSENT"), `states.py:83-85` (legal `DRAFTED → COMMITTING → COMMITTED` plus the release edge), `states.py:112` ("LOST … R5 maps this to 409"). The compare-and-swap **is** the guard, not "a different mechanism": `store.py:88-89` ("COMPARE-AND-SWAP `drafted -> committing`. The duplicate-commit guard."). It is enforced in the R5 request handler: `not_wired.py:259` (`claim = store.claim_for_commit(...)`), `:262-266` (`LOST` → `COMMIT_CONFLICT`/409 "This recommendation has already been committed."; `service.commit(...)` runs only after a WON claim), `:285` (`finalize_commit`). The order is test-locked (`test_no_write_route.py:299-300`: claim < commit < finalize); a second commit of the same id returns `LOST` (`test_claim.py:48-49`; `test_claim_integration.py:100-102`), exercised with two real concurrent Postgres engines (`test_claim_integration.py:81-82`). So "unenforced" and "committed repeatedly" are false against the code.
>
> **Axis 2 — live-Postgres verification IN THIS ENVIRONMENT (still genuinely open — NOT closed by this note).** Whether that guard has been verified end-to-end against a live Postgres in *this* environment is a separate question and remains **unconfirmed**: #19 is **NARROWED, NOT DISCHARGED** precisely because cross-store atomicity is not achieved (residual tracked as **#21**, `BUILD-COMPLETION-REPORT.md:313-315`), and whether the Postgres-backed claim test actually executes here (vs. errors without Docker/a live DB) was **not** checked in this correction. This note makes **no** live-DB verification claim and changes **no** register status; #19 stays exactly as `BUILD-COMPLETION-REPORT.md:300` records it.

**This plan does not treat the live run as established.** If it happened outside this repo's record, it is unlogged. Either way it changes nothing here — but **it does bear on Q5**: a wired UI whose commit button can be pressed twice will exercise #19 for real, in a browser, against a real database.

### 1.4 Confirmed exactly as briefed

| Check | Result |
|---|---|
| `package.json` scripts | Exactly `build` / `test` / `test:cov` / `lint`. **No `dev` script.** ✅ confirmed |
| `vite.config.js` dev proxy | `plugins` + `build.outDir` only. **No `server` key at all.** ✅ confirmed |
| Backend CORS | **None.** `create_app()` adds 3 exception handlers + 3 routers. `add_middleware` → **zero hits** anywhere under `backend/`. The only repo-wide "CORS" hit is a *comment* in U23's frozen `test_format.py`. ✅ confirmed |
| git status | **Clean**, branch `main`, HEAD `cb06057`. No stray corpus files, no modified `.gitignore`. ✅ confirmed |
| Frontend suite | **Re-run live: 682 passed / 137 files / 0 failed** (81s). Matches the recorded figure exactly. |

**What a browser on `http://localhost:5173` calling `http://127.0.0.1:8000` would do today** — reasoned through, no code changed:

1. Every request carries the custom **`X-User-Id`** header. A custom header makes a request **non-simple** under CORS, so the browser sends a **preflight `OPTIONS`** first — for *every* route, not just R5.
2. FastAPI has **no `OPTIONS` handler** on any of these paths and no CORS middleware to synthesize one, so the preflight gets **`405 Method Not Allowed`** with no `Access-Control-Allow-Origin` / `-Allow-Headers`.
3. The browser fails the preflight and **never issues the real request**. The seam sees a rejected `fetch()`, throws, and `normalizeError` synthesizes `{ error: { code: 'network_error', message: 'Unable to reach the server.' } }`.
4. **The UI would render its ordinary error state for every single route** — no crash, but nothing works. (Even if the header were dropped, R2/R4 would be *sent* but the browser would refuse to expose the response to JS, and R5's `Content-Type: application/json` would still force a preflight.)

**So local dev is blocked at the network layer regardless of anything else.** That is Q2.

### 1.5 What the deploy-config record already says about this

`guide-docs/build/deploy-config/infrastructure-design/deployment-architecture.md`:

* **§2 dev tier, verbatim**: *"**dev** | optional/local — Vite dev build, developer-run | optional/local — `uvicorn backend.app.main:app` | local Docker Postgres (`database`'s dev tier)"*. **The dev tier was designed and never realized.** No `dev` script, no proxy — this pass is finishing a topology that was already specified.
* **§3, verbatim**: *"The Vercel static frontend and the Render backend are **different origins**. The frozen `backend/app` has **no CORS middleware**, and adding it would **edit the CLOSED composition root** (BR-DEP-1 violation). Resolution: a **`vercel.json` rewrite** proxies the frontend's `/api/*` requests to the Render backend — the **browser makes same-origin requests**, so **no CORS is needed and the backend is not edited**."*

**Implication for local dev**: Vercel's rewrite **does not exist locally** — `vercel.json` is a deploy-time artifact Vite ignores. So local dev needs its **own** equivalent. `vite.config.js`'s `server.proxy` is exactly that equivalent, and `main.jsx` **already points at `/api`**, so a proxy on `/api` needs no change to `main.jsx` at all. See Q2.

### 1.6 Blast-radius classifier — settled by U23's own frozen code, not by opinion

`backend/deploy_config/tests/structural.py::is_under_frozen(rel)`:

| Path | `is_under_frozen` | Meaning |
|---|---|---|
| `backend/app/main.py` | **True** | composition root (backend) — *classified frozen by U23* |
| `frontend/src/app/App.jsx`, `seams.js`, `httpTransport.js` | **True** | composition root (frontend) — *classified frozen by U23* |
| `frontend/src/<any other unit>/…` | **True** | the frozen UI units |
| `frontend/vite.config.js` | **False** | **U23's own artifact — explicitly not frozen** |
| `frontend/src/main.jsx` | **False** | **U23's own artifact — explicitly not frozen** |
| `frontend/package.json` | **False** | U23's own (additive edits sanctioned) |

⚑ Note the asymmetry this exposes: **`vite.config.js` and `main.jsx` are the only two frontend files this project's own frozen classifier says are free to edit.** Both happen to be exactly what Q1 and Q2 need.

### 1.7 ⚑ The finding the brief did not anticipate — the real blocker is the composition root

`App.jsx` mounts **only** `HistoryView`. The four other views are constructed in `seams.js` but deliberately **not rendered** (*"a surface that could only ever show an error would imply backing that does not exist"* — true under Scope A, when R2–R5 were `501`; **no longer true**, since Scope B made all seven routes live).

**But the existing, green test suite asserts that absence**, in `src/app/__tests__/app.test.jsx`:

```js
it('mounts NO unbacked surface — only the history view exists in Scope A', …)
  expect(screen.queryByTestId('queue-view')).toBeNull();
  expect(screen.queryByTestId('memo-view')).toBeNull();
  …
it('wires all five units seams', …)
  expect(Object.keys(seams).sort()).toEqual(['commit','history','memo','override','queue']);
```

**Mounting any view fails the first test. Adding the outlier seam fails the second.** This is a **direct collision** with this pass's stated hold *"preserve the existing frontend test suite's passing state"*, and it is surfaced as **Q5** rather than resolved unilaterally.

Two precision notes, measured not assumed:
* The default testids are `queue-view`, `memo-view`, `override-form-view`, `outlier-view` — but **`ApprovalGateView`'s default is `approval-gate`, not `approval-gate-view`**. So the assertion on `approval-gate-view` would *pass vacuously* even with the gate mounted. **Relying on that would be passing a test by accident**, and this plan does not propose it.
* `src/outlierView` is **absent from `seams.js` entirely** (five imports, not six). Outlier is a strictly larger delta than the other three.

### 1.8 The views themselves are complete and prop-injected

All five are finished components with defined loading/ready/empty/error state machines, and each takes its seam as a **prop**:

| View | Signature |
|---|---|
| `QueueView` | `({ fetchSeam, onSelect, size = 20, testid = 'queue-view' })` |
| `MemoView` | `({ memoFetchSeam, applicationId, testid = 'memo-view' })` |
| `ApprovalGateView` | `({ commitFetchSeam, applicationId, testid = 'approval-gate' })` |
| `OverrideFormView` | `({ overrideFetchSeam, applicationId, testid = 'override-form-view' })` |
| `OutlierView` | `({ fetchSeam, applicationId, testid = 'outlier-view' })` |

⚑ **Every one except `QueueView` requires an `applicationId` prop.** `QueueView` emits `onSelect` **upward only** and has no router (`SELECT-1` / no-router guards are enforced by per-unit tests). **So selection state — "which application is open" — is owned by nobody**, and mounting queue + memo together requires the composition root to hold it. That is a real, small piece of new state, and it is part of Q5, not a free consequence of it.

### 1.9 Contract re-confirmation (WIRE-1, frozen, **not amended by this pass**)

Each seam's request was checked **against the frozen contract text**, not guessed:

| Seam | Emits | WIRE-1 | Verdict |
|---|---|---|---|
| queue | `GET /applications?page={p}&size={s}` | R2, list wrapper `{ items, page }` | ✅ conforms |
| memo / override-context / commit-context / outlier | `GET /applications/{id}/memo` | R4, `MemoView` `{ application_id, recommendation_id, status, profile, report, memo, outlier }` | ✅ conforms — **all four read the same R4 route**; outlier reads only the `outlier` slice (WIRE1-Fold-4) |
| commit | `POST /recommendations/{id}/commit` body `{ action: 'approve' }` | R5 — `underwriter_id` **session-derived, never in the body** | ✅ conforms by construction (the builder has no `underwriter_id` parameter) |
| override | `POST /recommendations/{id}/commit` body `{ action: 'override', reason }` | R5 — `reason` mandatory non-blank iff override; blank → **409** | ✅ conforms; the backend `_gate` is the single source of truth |

⚑ Two **contract-level facts** that will be visible the moment the UI is wired, both **already-disclosed register items**, neither introduced by this pass:
* **#17** — R4 returns `outlier: null` **even for a `ready` view** in Phase 1, although `outlier_canonical` really is persisted. So a wired `OutlierView` renders its **empty state permanently**, correctly. Not a bug in the wiring.
* **#14 / #16** — a `failed` case projects to `status: "pending"` on R4 and is **indistinguishable from a fresh one** in the R2 queue.

---

## 2. What the work actually is (given §1)

Not "implement the seams". The delta is exactly four things:

1. **A `dev` script** so Vite can serve the app at all. → **Q1** (trivial, separable)
2. **A same-origin path for `/api` in local dev**, since Vercel's rewrite doesn't exist locally. → **Q2**
3. **A concrete `VITE_USER_ID` value** for local dev, since the mechanism exists but nothing supplies a value. → **Q3**
4. **Mounting the views in `App.jsx`** (and, for outlier, adding a sixth seam in `seams.js`) — the only change that **breaks currently-green tests**. → **Q4 / Q5 / Q6**

---

## 3. The open decisions

### Q1 — the `dev` script

`frontend/package.json` has `build` / `test` / `test:cov` / `lint` and **no `dev`**, so `npm run dev` fails and Vite never serves anything. Adding `"dev": "vite"` is one line.

**Verified rather than assumed** — the frozen U23 test that governs this file is a **presence** check, not exact-set equality:

```python
def test_frontend_package_json_change_is_additive_only():
    pkg = json.loads(sg.read(sg.FRONTEND_PKG))
    assert pkg["scripts"]["build"] == "vite build"
    assert pkg["scripts"]["test"] == "vitest run"
    assert pkg["scripts"]["lint"] == "eslint ."
    assert "react" in pkg["dependencies"]
```

Adding a key it does not enumerate **cannot** fail it. (Contrast `NFR-DEP-ROUTES-1`, which *is* exact-set equality over `backend/app/routes/` filenames — which is precisely why `not_wired.py` can't be renamed, register #13. The two are genuinely different, and this one is the permissive kind.) `vite` is already installed (transitive via `vitest`) — **no new dependency**. `package.json` is **not** under `is_under_frozen`. `vite.config.js` already exists, so `vite` has a config to read.

This is the **#8-`render.yaml`-comment precedent**: a mechanical, verified-safe, zero-decision edit, separable in kind from the flagged decision it sits beside.

> **ANSWERED 2026-07-23T12:45:51Z.**

**Q1: Should the `dev` script be added immediately, ahead of the rest of this plan?**

- **(a) Yes — add `"dev": "vite"` now, as its own trivial change, and treat it as not needing its own scoping treatment. — RECOMMENDED.** Grounded, not asserted: the governing frozen test is presence-only (quoted above), no new dependency, the file isn't frozen, and the change is independently reversible. It unblocks *observing* anything at all, and blocks nothing else in this plan.
- **(b) Yes, but fold it into whichever pass implements Q2** — one commit, so `dev` never lands without the proxy that makes it useful. Costs the clean separation; a `dev` script that starts a server whose every request errors is arguably worse than none.
- **(c) No — treat it as part of the full scoped change** and add nothing until every question below is answered.
- **(d) Add `"dev": "vite --port 5173"`** (or another pinned port) rather than bare `vite`, so the origin is deterministic. **Note**: this matters *only* if Q2 resolves to (b) CORS-with-an-allowlist, where the exact origin must be named. Under Q2(a) the proxy makes the port irrelevant.

**[Answer]**: (a) — add `"dev": "vite"` now, as its own trivial, separable change, per the plan's grounded recommendation. The governing frozen test is presence-only, no new dependency, and the change is independently reversible.

---

### Q2 — local-dev connectivity (the CORS problem)

Established in §1.4: with no CORS middleware and a custom `X-User-Id` header, **every** cross-origin request from a browser preflights, FastAPI answers `405`, and nothing works. This must be solved for local dev to exist at all.

Production already solved the same problem a specific way, and recorded why (§1.5): the Vercel rewrite makes requests **same-origin** so CORS is never needed and *"the backend is not edited"*. **That rewrite does not exist locally** — `vercel.json` is inert under Vite. So local dev needs its own equivalent.

**Blast radius, measured (§1.6):** `vite.config.js` → `is_under_frozen` **False** (U23's own artifact). `backend/app/main.py` → `is_under_frozen` **True** (composition root; classified frozen by U23's own test, though the composition root has been established as editable within holds — it was reopened for the Scope B wiring). **Neither option touches a frozen-23 unit's internals**, so this pass's primary hold survives either way. The difference is *which* composition root gets touched, and whether the production design's stated intent is contradicted.

- **(a) Vite dev-server proxy — `server.proxy` in `vite.config.js`, forwarding `/api` → `http://127.0.0.1:8000` with a path rewrite stripping `/api`. Zero backend change. — RECOMMENDED.**
  Grounded on four measured facts: **(i)** `main.jsx` **already** sets `baseUrl: '/api'`, so requests are already `/api/...` and a proxy needs **no change to `main.jsx`**; **(ii)** it is the **exact local analogue of the production Vercel rewrite** — same mechanism, same same-origin outcome, so dev and prod behave alike instead of diverging; **(iii)** `vite.config.js` is one of only two frontend files U23's own classifier marks not-frozen; **(iv)** it directly honors `deployment-architecture.md` §3's recorded intent, which chose the rewrite *specifically* to keep CORS out of the backend. Cost: none identified. The proxy is dev-only — `vite build` ignores `server.*` entirely, so nothing ships.
- **(b) Add `CORSMiddleware` to `backend/app/main.py`** with an explicit origin allowlist (`http://localhost:5173`, `http://127.0.0.1:5173`), `allow_credentials`, and `allow_headers` including `X-User-Id`.
  ⚑ **Flagged explicitly, as instructed.** This edits the **composition root**, which `is_under_frozen` classifies **True** and which `deployment-architecture.md` §3 names as the thing the production design was built to avoid (*"would edit the CLOSED composition root (BR-DEP-1 violation)"*). It also changes the **deployed** backend's behavior to solve a **local-only** problem, and introduces a security-relevant surface (origin allowlisting) that WIRE1-Fold-3 assigned to `deploy-config`, not here. **It does not, however, touch any frozen-23 unit's internals** — the investigation confirms CORS config would live *only* in `backend/app/main.py`, nowhere unexpected. Choosing it is legitimate; it should be a deliberate choice, not a default.
- **(c) Both** — proxy for dev, CORS as a fallback. Rejected on its face: two mechanisms for one problem, with the CORS surface shipped to production for no production benefit.
- **(d) Neither — serve the built bundle from the backend** (`vite build`, then mount `dist/` as FastAPI static files) so everything is one origin. Genuinely CORS-free, but: it needs a **static-file mount in the composition root** (a bigger edit than (b)), loses hot-reload entirely, requires a rebuild per change, and **diverges from the deployed topology** where Vercel — not FastAPI — serves the bundle.

**[Answer]**: (a) — the Vite dev-server proxy in vite.config.js, forwarding /api to http://127.0.0.1:8000 with the /api prefix stripped. This is the correct local analogue of production's Vercel rewrite, touches nothing frozen, requires zero backend change, and main.jsx already points at /api so nothing else needs to move. Explicitly not (b) CORSMiddleware — editing the composition root to solve a local-only problem, when deployment-architecture.md §3 already recorded that exact edit as the thing the production design was built to avoid, is the wrong tradeoff here.

---

### Q3 — identity for local dev

Correcting the brief's premise (§1.2): the mechanism is **already built and complete**. `VITE_USER_ID` → `X-User-Id` → `current_identity` → `app_user`, fail-closing to 401; role arrives via R1 and fail-closes to `null`. **No code is required to "add auth".** What is missing is a **value**, and a way to change it.

The realistic minimum to demonstrate a wired path: **one user row in `app_user` with role `underwriter`** (the only role R5 permits) and its id in `VITE_USER_ID`. Without that, every route 401s and every view renders its error state — technically "wired", visibly useless.

⚑ **Note a real limit of the env-var approach**: `import.meta.env` is **build-time**, so switching users means restarting the dev server. That is *fine* for a single-user demo and *bad* for demonstrating RBAC (e.g. an `auditor` correctly getting **403** on R5, or the recorded, still-unresolved **Q1-B divergence** where an `admin` gets 403 on R6/R7 against WIRE-1 §3's "any role").

- **(a) Use the existing `VITE_USER_ID` mechanism unchanged — supply a value via `frontend/.env.local` and document the required `app_user` row. Build nothing. — RECOMMENDED.** Grounded: it is the mechanism U23 designed and `httpTransport.js` already honors; it adds **zero** code; the fail-closed path is already tested; and it keeps a login UI — a genuinely larger piece of work — properly out of scope. ⚑ Requires checking whether `frontend/.gitignore` covers `.env.local` (it is a 40-byte file; **must be verified before any value is written**, since committing a user id would be a new, unreviewed disclosure — small, but this project doesn't do those silently).
- **(b) A minimal dev user-switcher in the composition root** — a `<select>` of ids held in React state, passed to `createHttpTransport`. Makes RBAC demonstrable without a restart. But it means **new UI in `App.jsx`** and a **rebuilt transport on change**, and it invents an affordance no frozen unit specifies. Materially larger than (a).
- **(c) A real login form** (id + submit, stored in state or `localStorage`). ⚑ **Recommended against for this pass**: WIRE-1 §6 records the auth handshake as *"an abstract seam, deferred"*, and the backend has **no login route** — a form would be login-shaped theatre over a header stub. Its own scoping pass, if ever wanted.
- **(d) Defer entirely** — wire the plumbing, supply no id, accept that everything renders 401/error. Honest, and it does demonstrate the fail-closed path end to end for the first time. But it demonstrates nothing else, which makes Q5's mounting work unobservable.

**[Answer]**: (a) — use the existing VITE_USER_ID mechanism unchanged, via frontend/.env.local, with a documented required app_user row (role underwriter, matching what was used in this session's manual verification). Build nothing new. Before writing any value, verify frontend/.gitignore actually covers .env.local — do not skip that check.

---

### Q4 — the fetch seams: what actually changes

Per §1.1, the answer is measured, not estimated: **nothing inside any seam changes.** There is no base URL to fill in (the transport owns it, already set to `/api` in `main.jsx`), no headers to add (`httpTransport.js` already sends `Accept`, conditional `Content-Type`, and `X-User-Id`), and no error handling to write (every seam already normalizes to the WIRE-1 §4 envelope).

**The seams already share a consistent pattern — deliberately, and the consistency is load-bearing.** Every one of the four, plus queue and history, is: `buildXRequest(...)` → `normalizeError(cause)` → `createXFetch(transport)`. The `normalizeError` bodies are **byte-identical in behavior** across all six, and each header comment states the same rationale — *"the structural consistency comes from the shared WIRE-1 contract, NOT from importing a sibling"*. This is **enforced**: `noUiQueueImport`, `noApprovalGateImport`, `noSiblingImport`, `refNotOwn` tests fail on any cross-unit import. ⚑ **So "refactor the six `normalizeError`s into a shared helper" is not an available cleanup** — the duplication is the design, and de-duplicating it would break frozen tests in four units. Nothing in this pass should try.

The only seam-adjacent change on the table is **registration**: `seams.js` imports five seams and **not** `createOutlierFetch`.

**Q4: What, if anything, changes at the seam layer?**

- **(a) Nothing at all — confirm the seams are complete and touch none of them. Outlier stays unregistered too. — RECOMMENDED if Q5 excludes outlier.** Zero risk, zero test impact.
- **(b) Nothing inside the seams, but register the outlier seam in `seams.js` as a sixth key.** Required if Q5 includes outlier. ⚑ **Breaks the existing `wires all five units seams` test** (exact-key equality) — a test edit, gated by Q6. Note §1.9: with #17 open, a wired `OutlierView` renders its **empty state permanently** — real, correct, and unimpressive.
- **(c) Change something inside a seam** (e.g. a retry, a timeout, a shared base helper). ⚑ **Recommended against**: it edits frozen-23 unit internals — this pass's primary hold — and (per above) a shared helper would break four units' import guards.

**[Answer]**: (a) — nothing changes at the seam layer. Outlier stays unregistered in seams.js, consistent with excluding it from Q5's scope this pass.

---

### Q5 — scope boundary: how much UI gets mounted

**This is the load-bearing question**, and the one where the brief's framing understates the cost. Because the seams are already complete (§1.1), the *only* substantive work is mounting views in `App.jsx` — and **every mounting option breaks a currently-green test** (§1.7), colliding head-on with the "preserve the frontend suite" hold.

**Readiness, measured (§1.8):** all five views are complete, state-machine-driven, prop-injected components. None is half-built. But **four of the five require an `applicationId` prop**, and `QueueView` emits `onSelect` **upward only with no router**. So any option beyond (a) requires the composition root to hold **selection state** — new logic in `App.jsx`, however small.

⚑ **A safety fact that belongs in this decision, not a footnote.** Register **#19** is open: nothing performs `drafted → committed`, so *"already-committed → 409"* is **unenforced** and the same recommendation can be committed **repeatedly, writing a duplicate `AuditRecord` each time**. Today that is unreachable in a browser because nothing is mounted. **Mounting the commit or override view makes a real, clickable double-commit reachable for the first time** — in a BFSI audit trail. That does not forbid mounting it; it means the choice should be made knowingly. (Per §1.3, the record does **not** contain a live confirmation that this is guarded — the opposite.)

- **(a) Mount nothing new — deliver only Q1 + Q2 + Q3, and verify the wired path with the already-mounted `HistoryView` against a live backend.** The **only** option that breaks **zero** tests. Genuinely proves the whole chain (dev server → proxy → `X-User-Id` → R1 role → R6/R7 real data in a browser) for the first time. Leaves every view unmounted.
- **(b) Queue → Memo (read-only).** Mount `QueueView` + `MemoView` with selection state in `App.jsx`. Demonstrates the primary journey; **exercises no write path**, so #19 stays unreachable. Breaks the `mounts NO unbacked surface` test only.
- **(c) Queue → Memo → Commit (the full approve path). — RECOMMENDED, *conditional on Q6 and on accepting the #19 exposure knowingly.*** This is the journey the brief names, and the smallest slice that proves an **end-to-end human-in-the-loop gate** — the project's central architectural claim. Adds `ApprovalGateView`. ⚑ Makes #19's double-commit clickable. Recommended **only** if that is accepted explicitly; **(b) is the correct choice if it is not.**
- **(d) All four (add `OverrideFormView` + `OutlierView`).** Also requires Q4(b). ⚑ Weakest value-per-risk: outlier renders **permanently empty** under #17 (§1.9), and override doubles the #19 exposure with a second write path. Recommended against **as one pass** — better as a follow-on once (c) is observed working.

**[Answer]**: (c) — queue → memo → commit, the full approve path, accepting the #19 exposure knowingly. I'm accepting this deliberately, not by default: the duplicate-commit guard was already manually exercised against a real Postgres database earlier in this project's work (submit, draft, commit, then a second commit attempt correctly returned 409) — so there is real, if currently unlogged, evidence the guard works under a live database, not just in the traced InMemoryCaseStore simulation. I want that manual verification written into the project's actual audit trail as part of this pass (see the instruction below), so the record reflects what's actually been demonstrated. Explicitly excluding override and outlier from this pass — override doubles the write-path exposure for comparatively little demonstration value, and outlier renders permanently empty under #17 regardless of what's done here.

---

### Q6 — test strategy, and the existing-suite collision

The hold says *"preserve the existing frontend test suite's passing state"* (**682 / 137 / 0**, re-run live this session). Under Q5(a) that is free. Under Q5(b)/(c)/(d) it is **not**: `app.test.jsx` **asserts** the four views are unmounted, and Q4(b) additionally breaks the exact-five-keys assertion.

⚑ **State the tension precisely, because it is not a bug in the tests.** Those assertions were **correct and load-bearing when written** — under Scope A, R2–R5 were `501`, and mounting a view that could only ever error would have implied backing that didn't exist. **Scope B made all seven routes live, which retired the premise.** So the test now asserts a Scope-A fact in a Scope-B world. **That is an update, not a weakening — but it is exactly the kind of claim this project has repeatedly refused to make silently**, so it is put to the user rather than assumed.

Note also: no new test infrastructure is needed. The established pattern is **injected `fetchImpl`** (`app.test.jsx`'s `fakeServer` speaks real WIRE-1 shapes over the real transport), **not** a globally-monkeypatched `fetch`. Any new test should follow it. Coverage thresholds (90% lines/functions/statements/branches, `src/app/**` included) must not be weakened — the "include paths ADDED only, thresholds UNCHANGED" convention has been held through eight successive folds.

- **(a) Update `app.test.jsx`'s assertions to match the new Scope-B reality, and add tests for the newly-mounted surfaces (same injected-`fetchImpl` pattern). Net suite grows; nothing is deleted or weakened. — RECOMMENDED for any Q5 option other than (a).** The `mounts NO unbacked surface` test becomes the inverse assertion (**the backed surfaces ARE mounted**), with a comment recording *why* it changed and what superseded it — the supersede-not-rewrite discipline this build has used throughout. ⚑ Requires explicit acknowledgement that an existing green test is being **changed**, not merely added to.
- **(b) Delete the conflicting assertions.** Rejected: it removes a check without replacing it, leaving the composition root's mounting behavior unasserted in either direction.
- **(c) Leave `app.test.jsx` untouched and mount views only under a flag/prop the test doesn't set.** Preserves the letter of the hold and **violates its spirit** — the default path would be untested and the test would attest to a configuration nobody runs. ⚑ Recommended against. (It would also "pass" partly by the `approval-gate` / `approval-gate-view` testid mismatch noted in §1.7 — passing by accident.)
- **(d) Choose Q5(a), where the question does not arise.** The only option under which the hold is satisfied **literally and completely**, with zero test edits.

**[Answer]**: (a) — update app.test.jsx's assertions to match the Scope-B reality (the backed surfaces ARE mounted), with a comment recording why and what superseded the old assertion, supersede-not-rewrite. Add tests for the newly-mounted surfaces using the established injected-fetchImpl pattern, not a global fetch mock. Net suite grows; nothing is deleted or silently weakened.

---

## 4. Holds — status at the plan gate

| Hold | Status this pass |
|---|---|
| No edit to any frozen-23 unit's internals | ✅ **Upheld.** Nothing edited. ⚑ Q2 investigated as instructed: CORS config would live **only** in `backend/app/main.py` (the composition root) — **not** in any frozen unit, and nowhere unexpected. Flagged in Q2(b), not assumed. |
| No edit to WIRE-1's contract text | ✅ **Upheld.** Read-only. All four seams re-checked **against** it (§1.9); every one conforms. |
| Do not touch `backend/app/routes/` or add a route | ✅ **Upheld.** Not opened for edit; no route proposed. `not_wired.py` not renamed (#13's matched pair untouched). |
| Do not touch the `audit_store` Docker-guard gap | ✅ **Upheld.** Untouched; backend suite not re-run (5 errors stay 5). |
| Do not authorize or touch tier-B | ✅ **Upheld.** Not authorized, not referenced as available. No API call, **no spend**. |
| Do not weaken/bypass #18's spend guardrails | ✅ **Upheld.** ⚑ Confirmed by scope: **nothing in this pass touches `backend/app/llm_client.py` or `backend/scripts/`** — neither appears in any option above. `ALLOW_REAL_LLM_CALLS` is not read, set, or documented as settable here. |
| Preserve the frontend suite's passing state | ⚠️ **Genuinely at risk under Q5(b)/(c)/(d)** — surfaced as **Q6**, not resolved unilaterally. **Free under Q5(a).** Baseline re-run live and recorded: **682 / 137 / 0**. |
| No code generated | ✅ **Upheld.** Files written this pass: **3** — this plan, the `audit.md` entry, the `guide-state.md` entry. |

---

## 5. Directed checks to run *after* the answers, before any implementation

Recorded now so they are not invented later:

1. **Q1** — re-run U23's `test_noedit.py` + `test_build.py` after the `scripts` edit and confirm both still pass (predicted: yes, presence-only).
2. **Q2(a)** — confirm the proxy's path rewrite is correct against the **real** route table: `main.jsx` sends `/api/session`, but the backend serves `/session`. **The `/api` prefix must be stripped** or every route 404s. This is the single most likely silent failure in the whole pass.
3. **Q2(b)**, if chosen — confirm no existing backend test asserts the app's middleware stack is empty, and confirm `allow_headers` explicitly includes `X-User-Id` (a wildcard will not survive `allow_credentials`).
4. **Q3** — verify `frontend/.gitignore` covers `.env.local` **before** writing any value into it.
5. **Q5/Q6** — re-run the **full** frontend suite and report the exact delta against **682 / 137 / 0**, naming every test changed and why.
6. **Cross-cutting** — confirm the backend suite is **not** re-run and stays carried forward at 1578 / 0 / 43 / 5 / 99.87% (nothing here touches Python).
7. **Honesty check** — if the wired path is exercised against a live Postgres, record it as a **first-time live verification**, discharging part of the outstanding residual on #2 — and do **not** describe it as confirming #19, which is an **open defect** (§1.3).

---

## 6. Register impact

**None proposed.** No item is discharged, narrowed, or opened by this scoping pass. Register stands at **24 tracked** — 17 open / 3 discharged (#2 partly, #20, #24) / 4 narrowed (#3, #8, #18, #19).

Items this pass **touches the blast radius of**, without changing their status: **#2** (a wired browser UI would be the first real consumer of R2–R5), **#14 / #16** (`failed` cases render as `pending` / indistinguishable in the queue — visible to a real user for the first time), **#17** (a wired `OutlierView` renders permanently empty), **#19** (⚑ a clickable double-commit becomes reachable under Q5(c)/(d)), **#13** (`not_wired.py` stays stale and unrenamed).

Whether any of these warrants a new register entry is a **post-implementation** judgement, not a scoping one — and is deliberately not pre-empted here.

---

---

## 7. Ambiguity-check — RUN 2026-07-23T12:45:51Z against the full answer set + §1 ground truth

**Result: CLEAN — 10 folds resolved, no genuine gap, no surface-and-stop.** Every item below was measured on disk this session, not inferred. Answer-set internal consistency was checked first: **Q4(a) and Q5(c) do not conflict** — the queue/memo/commit seams are *already* registered in `seams.js`, so mounting them needs **no** seams-layer change, and outlier staying unregistered is exactly consistent with excluding it from Q5. ✅

### Directed check 2 (the plan's own flagged highest-risk item) — ⚑ CONFIRMED A REAL HAZARD, mechanism pinned

Read off `backend/app/routes/` (read-only, not edited). The **actual** mounted paths are:

`/session` · `/applications` · `/applications/{application_id}` · `/applications/{application_id}/memo` · `/recommendations/{recommendation_id}/commit` · `/decisions` · `/decisions/{decision_id}`

**There is no `/api` prefix on any route.** `main.jsx` sends `/api/session`, `/api/applications?…`, etc. So a proxy that forwards without rewriting produces `GET http://127.0.0.1:8000/api/session` → **404 on every route, all seven**. The plan was right to flag this as the most likely silent failure.

**Resolution (binding on the code-gen plan)**: the proxy entry MUST carry an explicit rewrite stripping exactly the leading `/api`:
`rewrite: (p) => p.replace(/^\/api/, '')`.
⚑ Two further specifics, both measured rather than assumed: **(i)** target `http://127.0.0.1:8000`, **not** `http://localhost:8000` — on Windows, Node 18+ resolves `localhost` to IPv6 `::1` first while `uvicorn` binds IPv4 by default, which produces `ECONNREFUSED` that reads exactly like "the backend is down". **(ii)** A **verification step** is required after wiring, not just the config: the rewrite is invisible in the browser (the request URL stays `/api/...` either way), so a 404 would be misread as a backend fault. Directed check 2 is discharged as **resolved-with-mechanism**, not merely acknowledged.

### Directed check 4 — `.env.local` is genuinely ignored ✅

Verified by execution, not by reading the file: `git check-ignore -v frontend/.env.local` → **`.gitignore:4:.env.*`**, exit 0. `frontend/.gitignore` itself lists only `node_modules/`/`coverage/`/`*.log`/`.DS_Store`, so the coverage comes from the **root** rule, which matches at any depth. `!.env.example` (line 6) is the sole negation and does not re-expose `.env.local`. **Writing a dev user id into `frontend/.env.local` creates no disclosure risk.** Q3(a) is safe as answered.

### Directed check 1 — U23's governing tests re-run as a baseline ✅

`pytest backend/deploy_config/tests/test_noedit.py test_build.py` → **11 passed**. (The non-zero exit is only the repo-wide 90% coverage gate firing on a deliberately partial run — no test failed.) The `scripts` assertion is confirmed presence-only in the live code, so Q1(a)'s addition cannot fail it.

### Directed check 5 — full-suite delta, predicted **test by test**

The actual re-run is a post-implementation step; what is pinned **now** is the exact prediction, so any deviation is a signal rather than a surprise. Baseline: **682 passed / 137 files / 0 failed** (re-run live this session).

`src/app/__tests__/app.test.jsx`, all 10 existing tests:

| # | Test | Predicted | Why |
|--:|---|---|---|
| 1 | `mounts the shell and renders the history surface from the REAL transport` | ✅ PASS | `history-list` still renders; `QueueView` additionally mounts and errors into its own state |
| 2 | `drives the master-detail flow end-to-end (R6 -> R7)` | ✅ PASS | asserts `calls` *contains* `/decisions?page=1&size=20` + `/session`; a new `/applications` entry does not break containment |
| 3 | `feeds R1 role into the FROZEN AppFrame seam, not around it` | ✅ PASS | untouched path |
| 4 | `renders identically for every role` | ⚠️ **PASS but RACE-PRONE** — see fold 10 | compares full `container.innerHTML` after awaiting only `history-list`; newly-mounted async views may not have settled identically between runs |
| 5 | `an unauthenticated session leaves a null role and still renders` | ✅ PASS | its `fetchImpl` returns `LIST` for every non-`/session` URL, which `QueueView` renders as ready |
| 6 | **`mounts NO unbacked surface — only the history view exists in Scope A`** | ⛔ **FAILS** | `queryByTestId('queue-view')` becomes non-null. **This is the ONLY existing test that fails.** |
| 7 | `surfaces a backend error through the frozen unit own error state` | ✅ PASS | history's error state is unchanged |
| 8 | `wires all five units seams` | ✅ PASS | ⚑ **stays green untouched** — Q4(a) leaves `seams.js` byte-unchanged, so the exact-five-keys assertion still holds |
| 9 | `the history seam is the dual-read one ui-history expects` | ✅ PASS | untouched |
| 10 | `the unbacked seams are real and callable` | ✅ PASS | untouched |

**⚑ The blast radius is ONE test, not the four the scoping pass feared.** Because Q4(a) declines the seams change, test 8 — the exact-key-equality assertion — never comes into play. Predicted delta: **682 → 682 + N new**, with **1 existing test rewritten in place** (#6) and **0 deleted**. Any other existing test changing state is an unpredicted result and must stop the pass.

### The remaining folds

**Fold 3 — ⚑ the `approval-gate` / `approval-gate-view` testid mismatch would let test 6 pass BY ACCIDENT.** `ApprovalGateView`'s default `testid` is **`approval-gate`**, but test 6 asserts `queryByTestId('approval-gate-view')` is null. Mounting the gate at its default id leaves that assertion **true but meaningless** — green for the wrong reason. **Resolution**: test 6's rewrite must assert against the **real** rendered testid (`approval-gate`), and the new mounting tests must positively assert the gate IS present. This project has twice rejected tests that pass for the wrong reason (the interop replica; the heuristic fake); this is the same failure mode and is refused the same way.

**Fold 4 — duplicate R4 fetch, DISCLOSED not optimized.** `MemoView` and `ApprovalGateView` each issue their own `GET /applications/{id}/memo`, so mounting both means **two identical R4 requests** per selection. This is correct-by-design: each frozen unit owns its own fetch (which is exactly why `commitFetchSeam` carries its own `fetchContext`), and de-duplicating would require lifting fetched state into the composition root and passing it down — changing how frozen units are driven. Cost is one extra bounded GET. **Disclosed rather than optimized**, on the #15 precedent.

**Fold 5 — coverage must not sag.** `src/app/**` is inside the coverage `include` with **90% on lines/functions/statements/branches**. Selection state adds new branches to `App.jsx`, so the new tests must exercise **both** arms — no selection (queue only) and a selection (queue + memo + gate) — plus the `onSelect` callback itself. Otherwise a green suite could still fail the threshold.

**Fold 6 — the src/app lint rules constrain any new copy, and the design avoids the constraint entirely.** `eslint.config.js` applies `shell/no-inline-label` **and** `shell/advisory-vocabulary` to `src/app/**` production files. `advisory-vocabulary` scans **every string literal, JSXText and template element** for `\bdecision\b`, `\bapproved\b`, `\bdeclined\b` and bare `decline` (suffix-aware: `DECLINE-RECOMMEND` is allowed; note `decisions` in a path literal does *not* match, which is why the history seam passes today). **Resolution — eliminate the risk instead of navigating it**: `App.jsx` introduces **no new display copy at all**. Keeping `QueueView` mounted while selection merely *adds* the detail panes means there is no "back" affordance and therefore no new label. (`testid-convention` is **not** enabled for `src/app`, so a new testid is unconstrained.)

**Fold 7 — no cross-unit import guard blocks the mounting.** Verified: `noApprovalGateImport` walks `src/overrideForm` only, `src/history`'s equivalents walk `src/history` only — each scans **its own tree**. **Nothing anywhere scans `src/app`.** `App.jsx` may import `QueueView`, `MemoView` and `ApprovalGateView` freely. ✅

**Fold 10 — test 4 becomes race-prone and must be stabilized, not left to luck.** `renders identically for every role` snapshots `container.innerHTML` after awaiting only `history-list`. With two more async surfaces mounted, a snapshot can be taken with `QueueView` mid-`loading` in one role and settled in another, producing an intermittent false failure. **Resolution**: the rewrite must await a settled state on the newly-mounted surfaces before snapshotting. ⚑ This is a **second** existing test needing a *mechanical* (not semantic) touch — its assertion is unchanged, only its await is strengthened. **Recorded explicitly so the §5 check-5 delta reads 2 existing tests touched, 1 semantically.**

### Checks 3, 6, 7 — status

**3** — N/A: Q2(b) was not chosen; no middleware is added, so no middleware-stack assertion can be disturbed. **6** — the backend suite is **not** re-run and stays carried forward at **1578 / 0 / 43 / 5 / 99.87%**; nothing in this pass touches Python. **7** — discharged by the retroactive verification entry appended to `audit.md` at `2026-07-23T12:45:51Z`, which records the manual run as the user's out-of-band attestation and states plainly that it **does not** change #19's register status on its own.

---

**Ambiguity-check CLEAN. Answers embedded 6/6. Implementation plan: `guide-docs/build/plans/frontend-backend-wiring-code-gen-plan.md`. STOPPED at the plan-file gate — no code generated.**
