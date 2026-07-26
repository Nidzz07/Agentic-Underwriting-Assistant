# Frontend Login — CODE-GENERATION PLAN

**Stage**: POST-BUILD → execution plan for `frontend-login-signup-plan.md` (Q1–Q5 answered; ambiguity-check CLEAN,
4 folds).
**Status**: 🟡 **PLAN ONLY — NOTHING EXECUTED. No component, no test, no code.** Stopped at the code-gen plan-file
gate.
**Date**: 2026-07-26
**Baseline**: frontend **687 / 137 / 0** · backend **1615 / 0 / 43 / 5 / 99.63%** (untouched by this pass).

---

## 0. What this plan is and is not

* **IS**: the ordered, TDD-structured execution plan — Step 0 as a hard gate, explicit before/after for every
  superseded test, predicted deltas **in advance**, named stop-gates.
* **IS NOT**: the execution. **Nothing here has been run.**
* **IS NOT** a backend or contract change. **§3 of the scoping plan confirmed: no WIRE-1 change, no backend
  change, no new route, no migration.** R8/R9 are already contracted and field-verified; this pass **consumes**
  them.

---

## 1. ⛔ STEP 0 — THE HARD GATE. Both cookie unknowns, in a real browser, BEFORE any component code

**Nothing in §2 onward may begin until the user reports both confirmed.** These are not preliminaries; they are
load-bearing premises that have been carried on assumption **twice**, and they **compound** — a `Secure` cookie is
dropped by browsers over `http://`, and local dev is `http://127.0.0.1:5173` behind the Vite proxy.

### 0.1 The two unknowns

| # | Unknown | Why it is still unproven |
|--:|---|---|
| **1** | **`SESSION_COOKIE_SECURE=false` actually works for local dev over `http://`** | The **fail-safe default** (`Secure`) was exercised in the manual verification; **its opt-out never was**. Register #25's discharge names this explicitly as **not claimed**. |
| **2** | **Fold-3's `httpTransport.js` "no change needed" prediction holds in a real browser** | It rests on `fetch` defaulting to `credentials: 'same-origin'`. The manual pass used **`curl` with an explicit `-b`**, which **bypasses cookie handling entirely** — so this has never been exercised by a browser. |

### 0.2 The procedure — for the user to run

1. Set `SESSION_COOKIE_SECURE=false` in the backend environment; start the backend on `127.0.0.1:8000`.
2. `npm run dev` in `frontend/` (Vite on `:5173`, proxying `/api` → `127.0.0.1:8000`).
3. In a **real browser**, with DevTools open on the Network + Application/Storage tabs:
   * `POST /api/login` (via the browser console `fetch`, since no login UI exists yet):
     ```js
     await fetch('/api/login', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ user_id: 'demo-underwriter', password: '<the password>' }),
     });
     ```
     **Confirm (1)**: response **204**, and the cookie **appears in Application → Cookies** for
     `127.0.0.1:5173`. If `Secure` is still set, the browser will have **silently dropped it** — that is unknown
     (1) failing.
   * Then, **without setting any header**:
     ```js
     await (await fetch('/api/session')).json();
     ```
     **Confirm (2)**: **200** with `{user_id, role}`, and the request carried the cookie **automatically**. That
     is Fold-3 holding, with `httpTransport.js` unmodified.

### 0.3 ⛔ Stop-gates on Step 0

* **(1) fails** → the local dev loop cannot hold a session. Stop and report; do not build a login page that
  cannot be exercised.
* **(2) fails** → `httpTransport.js` needs `credentials: 'include'` (or equivalent). ⚑ **That is a change to a
  frozen-classified file and is its OWN decision** — it was an explicit stop-gate in the backend pass and remains
  one here. **Stop and report; do not make a quiet one-line edit.**

**Report back both results before Step 1 begins.**

---

## 2. What gets built (post-Step-0)

### 2.1 The login unit — `frontend/src/login/`

Following the six units' conventions exactly (ambiguity-check FE-Fold-2):

| File | Contents |
|---|---|
| `copy.js` | **All** UI strings (COPY-1 — no inline labels). ⚑ Must avoid `FORBIDDEN_TERMS.systemOutput` (`DECLINE`/`decision`/`approved`/`declined`) — *"Sign-in failed"* is fine, *"…was **declined**"* is a lint error |
| `loginFetchSeam.js` | `buildLoginRequest({user_id, password})` → `POST /login` · `buildLogoutRequest()` → `POST /logout` · `normalizeError` → the WIRE-1 §4 envelope. **Own-local**: mirrors its siblings, imports none of them |
| `LoginView.jsx` | The stateful form: `idle → submitting → error`, `error --submit--> submitting` |
| `LogoutControl.jsx` | The logout affordance (Q4c), mounted by `App.jsx` |
| `components/` | Presentational parts |
| `__tests__/` | Per §4's list |

⚑ **Binding on error handling (scoping plan §4):** the view renders the server's message **verbatim** via
ERROR-1 (`message` visible, `code` hidden-testid, `detail` never). It **must not** distinguish lockout from a
wrong password, infer lockout from repeated failures, or hint at it. The backend withholds that distinction
because it is a **user-enumeration oracle**; a client that reconstructs it re-opens the hole the backend closed.

⚑ **204 has no body.** The seam must not parse or expect one.

### 2.2 The gate — `App.jsx` (Q1a)

Three states, **starting in `checking`** (FE-Fold-4, **binding**):

* `checking` — renders **neither** the app nor the login view; a minimal `aria-busy` affordance following the
  units' loading convention. **This is what prevents a login-page flash on every load for authenticated users.**
* `unauthenticated` — renders `LoginView` **instead of** the app surfaces.
* `authenticated` — renders exactly what `App` mounts today, unchanged.

**Post-login (Q3a)**: on 204, re-run the **same** `loadCurrentRole` the gate already uses; on success the gate
flips to `authenticated`. **One definition of "who is the current user"**, used at boot and after login.

⚑ **Logout is NOT wrapped in `RoleGate`** (Q4c): `RoleGate`'s `admin` row is `{act:false, read:false}`, so gating
it would **strand admins in a session they cannot end**.

### 2.3 Q5(b) — the two docstring corrections

`httpTransport.js`'s header (*"the client mirror of the server's deferred handshake seam"* — false since
WIRE1-Fold-5) and `.env.local`'s prose, both superseded to state the header is **retired and ignored by the
server**. **No behaviour change; no `main.jsx` edit; no test touched** (verified: no test asserts
`httpTransport.js` content).

⚑ **Deferral recorded by name**: *full removal of the `VITE_USER_ID` / `X-User-Id` path — dropping `userId` from
`httpTransport.js`, the `import.meta.env` read from `main.jsx` (a **U23-owned** file), the `.env.local` line, and
the two `httpTransport.test.js` tests pinning it — is a legitimate future cleanup, deliberately deferred out of
this pass.*

---

## 3. Explicit BEFORE / AFTER — the two superseded assertions (Q2a)

**Supersede-not-rewrite: the old assertion's text and rationale are preserved in a note. Neither is deleted, and
neither is quietly edited to pass.**

### 3.1 `app.test.jsx:156`

```
BEFORE  it('an unauthenticated session leaves a null role and still renders (fail-closed, not an error)')
          -> renders App with a 401 /session, asserts `history-list` IS present

AFTER   it('an unauthenticated session renders the login view and mounts no application surface')
          -> renders App with a 401 /session
          -> asserts `login-view` IS present
          -> asserts `history-list` and `queue-view` are ABSENT
```

**The superseding note must record** — this is the substantive part, not boilerplate:

> The old assertion was **CORRECT for a build with no way to log in**. With no login page in existence, rendering
> the app in a fail-closed null-role state — every gated affordance hidden, every fetch surfacing an honest error
> — was **the best available behaviour**. It stops being correct the moment a login page exists, because the
> honest response to "not authenticated" becomes "here is how to authenticate". **This is a PREMISE CHANGE, not a
> regression**, and the old test's real content — *unauthenticated is a state, not an error* — **survives and
> strengthens**: it is still not an error, and it is now actionable.

### 3.2 `app.test.jsx:171`

```
BEFORE  it('mounts exactly the backed surfaces — queue + history always; override and outlier never')
          -> single (authenticated-shaped) render; asserts queue+history present, memo/gate/override/outlier absent

AFTER   same name, extended to BOTH gate states:
          authenticated   -> queue + history present; override + outlier absent (unchanged)
          unauthenticated -> login-view present; queue, history, memo, gate, override, outlier ALL absent
```
**Not weakened**: it still pins exactly which surfaces mount, now in **both** directions across **both** states.

---

## 4. TDD execution order

| # | Step | Kind | Gate |
|--:|---|---|---|
| **0** | ⛔ **The two cookie unknowns, in a real browser** (§1) | **USER-RUN HARD GATE** | **Nothing proceeds until both are reported confirmed** |
| **1** | `npm test` baseline | verify | **687 / 137 / 0** — else **STOP** |
| **2** | **RED** `loginFetchSeam.test.js` → then `loginFetchSeam.js` | RED→GREEN | **+4** |
| **3** | **RED** `login.state.test.jsx` + `login.submit.test.jsx` → then `LoginView.jsx` + `copy.js` + `components/` | RED→GREEN | **+7** |
| **4** | **RED** `login.error.test.jsx` (401 verbatim · code hidden · **no lockout inference**) | RED→GREEN | **+3** |
| **5** | Convention tests: `nots` · `testid` · `boundedFetch` · `noBackendImport` · `eslint.login.rules` | GREEN | **+6** |
| **6** | **RED** `login.logout.test.jsx` → then `LogoutControl.jsx` | RED→GREEN | **+2** |
| **7** | **RED** the gate's three states in `app.test.jsx` → then `App.jsx`'s gate | RED→GREEN | **+3**, and §3's two supersessions land |
| **8** | Q5(b) docstring corrections | GREEN | **+0** |
| **9** | `npm test` + `npm run test:cov` | verify | **712 / 0**, coverage thresholds unchanged, EXIT 0 |
| **10** | ⚑ **Manual browser confirmation** of the built login page (user-run) | USER-RUN | log in, land on the app, log out, land back on login |

### 4.1 Predicted deltas — stated in advance

| Step | Δ | Cumulative |
|---|--:|--:|
| 2 — fetch seam (login req · logout req · envelope passthrough · envelope synthesis) | **+4** | 691 |
| 3 — form states (idle/submitting/error) + submit shape (sends exactly `{user_id, password}`; 204 handled with no body) | **+7** | 698 |
| 4 — error rendering (message verbatim · code hidden · no lockout inference) | **+3** | 701 |
| 5 — conventions (nots · testid · boundedFetch · noBackendImport · 2 lint blocks) | **+6** | 707 |
| 6 — logout (posts R9 · not RoleGate-wrapped) | **+2** | 709 |
| 7 — gate (checking renders neither · post-login re-check mounts the app · logout returns to login) | **+3** | **712** |

**Predicted final: 712 passed / 0 failed.** Steps 3.1 and 3.2's supersessions are **modifications**, not
additions — **0 net**. **Backend untouched and not re-run**, carried at 1615/0/43/5/99.63%.

⚑ **Counting convention, learned twice in this build**: each **named** test is one test. A `parametrize`/loop that
inflates the count is restructured to match the prediction, **not** allowed to drift — assertion strength is
never traded, only granularity.

---

## 5. Stop-gates

1. **Step 0's unknown (1) fails** — `SESSION_COOKIE_SECURE=false` does not yield a usable cookie over http.
2. **Step 0's unknown (2) fails** — `httpTransport.js` needs a change. **Its own decision; no quiet edit.**
3. Step 1 baseline ≠ **687 / 137 / 0**.
4. Any test outside the named set changes state.
5. ⛔ **Any frozen `ui-shell` component edited** (`AppFrame`, `RoleGate`, `roleContext`) — the design requires none.
6. ⛔ **Any frozen view unit edited** (`queue`, `memoView`, `approvalGate`, `overrideForm`, `history`,
   `outlierView`).
7. ⛔ **`seams.js`'s five-key set changes** — the login client is **not** a seam (Q13a). `app.test.jsx:259` must
   stay green **untouched**.
8. ⛔ **`main.jsx` edited** — U23-owned; Q5(b) is specified precisely to avoid it.
9. **Any backend file or WIRE-1 touched.**
10. The gate renders the login view **before** `/session` resolves (the flash FE-Fold-4 forbids).
11. The login view distinguishes lockout from a wrong password in **any** way.
12. Final count ≠ **712**.

---

## 6. Holds

| Hold | Status |
|---|---|
| **Nothing executed; no component, no test, no code** | ✅ This is a plan |
| No backend file; **WIRE-1 untouched** | ✅ §3 of the scoping plan confirms none is needed |
| No frozen `ui-shell` component or view unit edited | ✅ Gate lives in `App.jsx`; logout in the login unit |
| `seams.js` five-key set preserved | ✅ Login client is not a seam |
| **`app.test.jsx:156` not yet touched** | ✅ Its supersession is **step 7**, designed in §3.1 |
| `main.jsx` untouched (U23) | ✅ Q5(b) edits only `httpTransport.js` + `.env.local` |
| **No commit** | ✅ |

---

**STOPPED AT THE CODE-GEN PLAN-FILE GATE.** Nothing executed. ⛔ **Step 0 is user-run and blocks everything
after it** — report both cookie results before Step 1 begins.
