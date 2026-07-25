# Frontend ↔ Backend Wiring — IMPLEMENTATION (CODE-GEN) PLAN

**Kind**: Post-BUILD implementation plan · **Date**: 2026-07-23 · **Status**: **PLAN ONLY — NO CODE GENERATED.** Stopped at the plan-file gate.
**Built on**: `frontend-backend-wiring-plan.md` — answers **Q1(a) · Q2(a) · Q3(a) · Q4(a) · Q5(c) · Q6(a)**, embedded verbatim, and its **§7 ambiguity-check (CLEAN, 10 folds)**. Re-opens none of them.
**Baseline**: `main` @ `cb06057`, tree clean apart from this pass's doc writes · frontend **682 passed / 137 files / 0 failed** (re-run live) · backend **1578 / 0 / 43 / 5 / 99.87%** (carried forward, **not** re-run — nothing here touches Python).

---

## 1. Component inventory — five items, and only five

| # | Item | File | Kind | `is_under_frozen`? | Breaks a test? |
|--:|---|---|---|---|---|
| **1** | `dev` script | `frontend/package.json` | 1-line additive | **False** (U23's own) | No |
| **2** | dev-server proxy | `frontend/vite.config.js` | `server.proxy` block | **False** (U23's own) | No |
| **3** | dev identity | `frontend/.env.local` (**untracked**) + docs | config + instructions | n/a (ignored) | No |
| **4** | mount queue → memo → gate | `frontend/src/app/App.jsx` | selection state + 3 mounts | **True** (fe composition root) | **Yes — 1** |
| **5** | test updates | `frontend/src/app/__tests__/app.test.jsx` | 1 rewrite + 1 await fix + new | n/a (test file) | — |

**Not in this plan, deliberately**: no seam file (Q4(a)) · no `seams.js` change · no `main.jsx` change (it already sends `/api`) · no backend file of any kind · no `vercel.json` change (production already correct).

---

### Item 1 — the `dev` script

**File**: `frontend/package.json`. **Change**: add one key to `scripts`.

```json
"dev": "vite",
```

Bare `vite` (not `--port 5173`): Q2(a)'s proxy makes the origin same-origin, so the port is irrelevant — pinning it would be unused ceremony. Vite's default is 5173 anyway.

**Why it is safe** — verified, not assumed: the governing frozen test `backend/deploy_config/tests/test_noedit.py::test_frontend_package_json_change_is_additive_only` asserts `build`/`test`/`lint` **by value** plus `react` in deps. It is a **presence** check, not exact-set equality over `scripts`, so a key it does not enumerate cannot fail it. Baseline re-run this pass: **11 passed**. No new dependency — `vite` is already installed transitively via `vitest`.

---

### Item 2 — the Vite dev-server proxy ⚑ the highest-risk item

**File**: `frontend/vite.config.js` (U23's own artifact; `is_under_frozen` → **False**). **Change**: add a `server` key. `plugins` and `build` are untouched.

```js
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      rewrite: (p) => p.replace(/^\/api/, ''),
    },
  },
},
```

**Three specifics, each measured — not one of them is stylistic:**

1. ⚑ **`rewrite` is mandatory, not optional.** The backend mounts `/session`, `/applications`, `/applications/{id}`, `/applications/{id}/memo`, `/recommendations/{id}/commit`, `/decisions`, `/decisions/{id}` — **no `/api` prefix on any route** (read off `backend/app/routes/` this pass). `main.jsx` sends `/api/session`. **Without the rewrite every one of the seven routes 404s.** This was the scoping plan's single most-likely-silent-failure call, and it was correct.
2. ⚑ **`127.0.0.1`, never `localhost`.** On Windows, Node 18+ resolves `localhost` to IPv6 `::1` first while `uvicorn` binds IPv4 by default — the result is `ECONNREFUSED` that reads exactly like "the backend is down", sending debugging in the wrong direction.
3. **Dev-only by construction.** `vite build` ignores `server.*` entirely, so nothing ships and `vercel.json`'s production rewrite is untouched. Dev and prod now use the same mechanism (same-origin proxy) rather than diverging — the point of Q2(a).

**Backend must be started as**: `uvicorn backend.app.main:app --port 8000` (matching `deployment-architecture.md` §2's dev tier, which named this and was never realized).

---

### Item 3 — dev identity (no code)

**Verified before anything is written** (directed check 4): `git check-ignore -v frontend/.env.local` → **`.gitignore:4:.env.*`**, exit 0. The file is ignored via the **root** rule (which matches at any depth); `!.env.example` is the only negation and does not re-expose it. **No disclosure risk.**

**`frontend/.env.local`** (created, never committed):

```
VITE_USER_ID=<the app_user.user_id used in the manual verification>
```

**Required database precondition** — documented, not automated: a row in `app_user` whose `user_id` matches, with **`role = 'underwriter'`**. Underwriter is not a preference: WIRE-1 §3 and `PERMISSION_MATRIX` **agree** that R5 commit is underwriter-only, so any other role gets a correct `403` at the approve step and the path cannot be demonstrated.

**No code is written for this item.** `main.jsx` already reads `import.meta.env.VITE_USER_ID`; `httpTransport.js` already sends it as `X-User-Id`; `dependencies.py::current_identity` already resolves it and fail-closes to 401. ⚑ Known limit, accepted under Q3(a): `import.meta.env` is **build-time**, so changing user requires restarting the dev server. Fine for a single-user demo; it does **not** demonstrate RBAC (an `auditor` correctly 403-ing on R5, or the recorded Q1-B `admin` divergence on R6/R7).

---

### Item 4 — mount the path in `App.jsx` ⚑ the only functional change

**File**: `frontend/src/app/App.jsx`. **Shape** (structure, not final code):

* new state: `const [selectedId, setSelectedId] = useState(null);`
* `<QueueView fetchSeam={seams.queue} onSelect={setSelectedId} />` — **always mounted**
* when `selectedId` is non-null, **additionally** render `<MemoView memoFetchSeam={seams.memo} applicationId={selectedId} />` and `<ApprovalGateView commitFetchSeam={seams.commit} applicationId={selectedId} />`
* `HistoryView` stays mounted exactly as today — **not moved, not conditioned, not changed**
* the stale Scope-A header comment is corrected to state Scope B and what is now mounted and why

**Four constraints this shape satisfies by construction** (each from §7's folds):

* **Fold 6 — zero new display copy.** Keeping the queue mounted means no "back" affordance and therefore **no new string literal**. This matters: `eslint.config.js` applies `shell/advisory-vocabulary` to `src/app/**`, scanning every string literal, JSXText and template element for `\bdecision\b`, `\bapproved\b`, `\bdeclined\b` and bare `decline`. The design **eliminates** the exposure rather than navigating it. (`testid-convention` is not enabled for `src/app`.)
* **Fold 3 — the gate is mounted with an explicit `testid`**, not its `approval-gate` default, so no assertion can pass by accident (see Item 5).
* **Fold 7 — imports are permitted.** Verified: `noApprovalGateImport` walks `src/overrideForm` only, history's equivalents walk `src/history` only. **Nothing scans `src/app`.**
* **Fold 4 — the duplicate R4 fetch is accepted and disclosed in a comment.** `MemoView` and `ApprovalGateView` each issue their own `GET /applications/{id}/memo`, so a selection produces **two identical R4 requests**. Each frozen unit owning its own fetch is the design (it is why `commitFetchSeam` carries `fetchContext`); de-duplicating would mean lifting fetched state into the composition root and changing how frozen units are driven. **Disclosed rather than optimized — the #15 precedent.**

**No frozen unit is edited.** All three views are consumed through their existing props.

---

### Item 5 — tests: **2 existing touched (1 semantically), N added**

**File**: `frontend/src/app/__tests__/app.test.jsx`. Pattern: the established **injected `fetchImpl`** (`fakeServer` speaking real WIRE-1 shapes over the real transport) — **never** a global `fetch` monkeypatch.

#### 5a — BEFORE / AFTER: test 6 (the only **semantic** change)

**BEFORE** (currently green):

```js
it('mounts NO unbacked surface — only the history view exists in Scope A', async () => {
  const { transport, seams } = fakeServer();
  render(<App seams={seams} transport={transport} />);
  await screen.findByTestId('history-list');
  // the four unbacked units are wired in seams.js but deliberately not rendered
  expect(screen.queryByTestId('queue-view')).toBeNull();
  expect(screen.queryByTestId('memo-view')).toBeNull();
  expect(screen.queryByTestId('approval-gate-view')).toBeNull();
  expect(screen.queryByTestId('override-form-view')).toBeNull();
});
```

**AFTER** — renamed to state the Scope-B fact, with a comment recording what superseded the old assertion and why (supersede-not-rewrite):

```js
// SUPERSEDED (2026-07-23): the assertion below replaces `mounts NO unbacked surface`, which was
// CORRECT under Scope A — R2–R5 answered 501, so mounting a view that could only ever error would
// have implied backing that did not exist. Scope B made all seven routes live, retiring that
// premise. The check is not weakened: it still pins EXACTLY which surfaces the composition root
// mounts, in both directions. Q5(c) deliberately excludes override and outlier.
it('mounts exactly the backed surfaces — queue + history always; override and outlier never', async () => {
  const { transport, seams } = fakeServer();
  render(<App seams={seams} transport={transport} />);
  await screen.findByTestId('history-list');
  expect(await screen.findByTestId('queue-view')).toBeInTheDocument();
  // no selection yet -> no detail surface
  expect(screen.queryByTestId('memo-view')).toBeNull();
  expect(screen.queryByTestId('approval-gate')).toBeNull();   // the REAL default testid — see below
  // out of scope this pass, in BOTH states
  expect(screen.queryByTestId('override-form-view')).toBeNull();
  expect(screen.queryByTestId('outlier-view')).toBeNull();
});
```

⚑ **Note the `approval-gate` / `approval-gate-view` correction.** `ApprovalGateView`'s default testid is **`approval-gate`**; the old test asserted `approval-gate-view` was null, which would have stayed **true but meaningless** once the gate was mounted — green for the wrong reason. The rewrite asserts the **real** id, and Item 4 mounts the gate with an **explicit** testid so the positive assertions below cannot pass by accident either. (This build has twice refused tests that pass for the wrong reason — the interop replica and the heuristic fake. Same refusal.)

#### 5b — BEFORE / AFTER: test 4 (**mechanical only** — assertion unchanged)

**BEFORE**: `renders identically for every role` snapshots `container.innerHTML` after awaiting only `history-list`.
**AFTER**: identical assertions; the await is strengthened to also settle the newly-mounted queue surface before snapshotting.

**Why this is required and not optional** (fold 10): with two more async surfaces mounted, a snapshot can catch `QueueView` mid-`loading` in one role and settled in another, producing an **intermittent** false failure. Flakiness introduced here would be indistinguishable from a real role-variance bug — the exact thing the test exists to detect. **The assertion's meaning is unchanged; only its synchronization is.**

#### 5c — new tests (the added coverage)

1. **selection mounts the detail surfaces** — click a queue row → `memo-view` and the gate appear, both driven by the real transport, with `applicationId` correctly propagated.
2. **no selection → no detail surfaces** (the other branch of the same condition — **fold 5**: both arms must be exercised or the 90% branch threshold can fail even with a green suite).
3. **the approve path end-to-end over the transport** — select → gate reaches `ready` → confirm → `POST /recommendations/{id}/commit` with body **exactly `{ action: 'approve' }`** and no `underwriter_id` (WIRE-1 §5 / AUTHZ-1), asserted on the recorded `calls`.
4. **a `pending` R4 renders the not-yet-drafted state**, not an error (WIRE1-Fold-2's discriminator).
5. **a commit error surfaces through the frozen unit's own error state** — e.g. `403` for a non-underwriter — with no special-casing in `App.jsx`.

**Coverage**: thresholds stay at **90 / 90 / 90 / 90** and the `include`/`exclude` lists are **not** edited — the "include paths ADDED only, thresholds UNCHANGED" convention held through eight prior folds is held here too.

---

## 2. TDD order (leaf-first, each step green before the next)

| Step | Work | Gate |
|--:|---|---|
| **0** | Re-confirm baseline: `npm test` → **682 / 137 / 0** | must match exactly before touching anything |
| **1** | Item 1 (`dev` script) | `pytest backend/deploy_config/tests/` still green; `npm test` unchanged at 682 |
| **2** | Item 2 (proxy) | `npm run dev` serves; **`curl` through the dev server to prove the `/api` strip** — see §3 |
| **3** | Item 3 (`.env.local` + `app_user` row) | R1 returns a role in the browser instead of 401 |
| **4** | **RED** — write 5c's new tests + rewrite 5a/5b against the *not-yet-mounted* `App` | new tests **fail**; 5a fails; suite red **for the predicted reasons only** |
| **5** | **GREEN** — Item 4 (`App.jsx` mounting + selection state) | full suite green; delta reconciled against §3 |
| **6** | Coverage | `npm run test:cov` — `src/app/**` ≥ 90 on all four metrics |
| **7** | Manual browser confirmation | the real queue → memo → commit journey, clicked |

Step 4 before step 5 is not ceremony: writing the rewritten assertions **first** is what proves test 6 was failing for the reason predicted (`queue-view` non-null) and not for an unrelated one.

---

## 3. Verification — predicted results, pinned now

**Suite delta (predicted test-by-test in the scoping plan's §7):** exactly **one** existing test fails before Item 4 (`mounts NO unbacked surface`); **test 8 `wires all five units seams` stays green untouched**, because Q4(a) declines the seams change. Final: **682 + N passed / 0 failed**, **2 existing tests touched (1 semantically)**, **0 deleted**.

> ⚑ **Any other existing test changing state is an unpredicted result and must STOP the pass**, not be absorbed.

**The `/api` strip must be proven, not assumed** (the rewrite is invisible in the browser — the request URL stays `/api/...` either way, so a 404 would be misread as a backend fault):

```
curl -H "X-User-Id: <id>" http://localhost:5173/api/session      # -> 200 {user_id, role}, NOT 404
curl -H "X-User-Id: <id>" http://localhost:5173/api/applications # -> 200 list wrapper
```

**Backend suite**: **not re-run**; carried forward at **1578 / 0 / 43 / 5 / 99.87%**. Nothing in this plan touches Python.

---

## 4. Holds

| Hold | How it is upheld |
|---|---|
| No frozen-23 unit internals | Items 1–3 touch non-frozen U23 artifacts; Item 4 touches the **frontend composition root**; Item 5 a test file. **No unit's own tree is opened.** |
| No WIRE-1 contract edit | Read-only. All requests re-checked **against** it; every one conforms. |
| No `backend/app/routes/`, no new route | Read **only**, to establish the real paths for the rewrite. **No backend file is written at all.** |
| `audit_store` Docker-guard gap | Untouched. Backend suite not re-run — **5 stays 5**. |
| tier-B | Not authorized, not touched, not referenced as available. **No API call, no spend.** |
| `backend/app/llm_client.py`, `backend/scripts/` | **Not touched.** Neither appears in any item above; `#18`'s spend guardrails are not reached, weakened, or documented as settable. |
| Frontend suite passing state | **Consciously and explicitly** changed under Q6(a) — 1 semantic rewrite, 1 mechanical await fix, N additions, **0 deletions**. Predicted and pinned in §3 so any deviation is caught. |
| No code this pass | **Upheld.** Files written: this plan, the updated scoping plan, 2 `audit.md` entries, 1 `guide-state.md` entry. |

---

## 5. What this delivers — and what it does not

### ✅ Delivers

**A real, clickable `queue → memo → commit` path in a browser, against a live backend and a real Postgres database.** Concretely: a Vite dev server on `:5173` proxying same-origin `/api` to `uvicorn` on `:8000`; a resolved identity (`VITE_USER_ID` → `X-User-Id` → `app_user`) yielding a real role from R1; the application queue rendered from **R2**; a memo rendered from **R4** on selection; and an **explicit human approval action** issuing **R5**, whose result is a committed decision visible in the **R6/R7** history already on screen.

That last point is the one that matters: it is the first time the project's **central architectural claim — the human-in-the-loop approval gate — is demonstrable by a person clicking it**, rather than asserted by a unit test. The advisory-only invariant holds visibly: nothing becomes committed without the explicit action.

### ❌ Does not deliver

* **No override path.** `OverrideFormView` stays unmounted (Q5(c)). The reason-carrying write path is not exercised.
* **No outlier view.** `OutlierView` stays unmounted and `createOutlierFetch` stays unregistered in `seams.js` (Q4(a)). Under **#17** it would render **permanently empty** regardless.
* **No login UI, and no auth.** `VITE_USER_ID` is a **build-time stub**, restart-to-change. WIRE-1 §6's handshake remains *"an abstract seam, deferred"*. There is no login route to call.
* **No production change.** Dev-only. `vercel.json` and `render.yaml` are untouched; **#8**'s missing migration entrypoint still blocks an actual deploy.
* **No register item resolved — none.** Specifically:
  * **#14 / #16** — a `failed` case still projects to `pending` on R4 and is still indistinguishable in the R2 queue. Wiring the UI makes this **visible to a real user for the first time**; it does not fix it.
  * **#17** — outlier data still exists in the database while the contract still forbids sending it.
  * **#19** — `drafted → committed` is still never performed. ⚑ **This pass makes a double-commit clickable in a browser for the first time**, accepted knowingly under Q5(c). The retroactive entry logged at `2026-07-23T12:45:51Z` records a manual out-of-band run in which a second commit returned `409`; per that entry, **it does not change #19's status on its own**, and this plan does not change it either.
  * **#13** — `not_wired.py` is still stale and still unrenamed.
  * **#2** — remains partly discharged. Whether a successful browser journey warrants a status change is a **separate decision**, deliberately not taken here.
* **No automated end-to-end test.** Step 7's browser confirmation is **manual and not re-creatable** by any suite — the same honest limitation as the retroactive entry it complements.

---

**STOPPED at the plan-file gate. No code generated. Awaiting review before Step 0.**
