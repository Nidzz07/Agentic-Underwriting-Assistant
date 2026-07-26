# Frontend Login — SCOPING PLAN

**Stage**: POST-BUILD → the frontend half of register **#25**'s subject. The backend half is **built, verified
against a real Postgres, and DISCHARGED** (`503a98c`).
**Status**: 🟡 **SCOPING / PLANNING ONLY — NO CODE, NO COMPONENT, NO TEST WRITTEN.** Stopped at the plan-file gate.
**Date**: 2026-07-26
**Depends on (settled, not re-litigated here)**: `login-signup-plan.md` (Q1–Q13) · `login-signup-code-gen-plan.md`
(Q1–Q5) · **WIRE1-Fold-5** (R8/R9 contracted and live).
**Suite at plan time**: backend **1615 / 0 / 43 / 5 / 99.63%** · frontend **687 / 137 / 0**.

---

## 0. ⚑ SETTLED, NOT AN OPEN QUESTION — no self-service signup

**This pass delivers a login page. It does NOT deliver public account creation, and that is not up for
discussion here.**

Accounts remain **admin-provisioned only**, via `python -m backend.authn set-password` against a user created by
`admin-cli create-user`. This **reverses no prior decision** — it is exactly **Q3(a)**, whose reasoning stands
unchanged and is restated so it is not re-opened:

> `PERMISSION_MATRIX` is **closed** over `underwriter` / `auditor` / `admin`, and `underwriter` carries
> **`RBAC_COMMIT`** — the authority to commit binding underwriting decisions. Open self-registration over that
> role set would let anyone who can reach the form grant themselves that authority. That is not a hardening
> detail; it is a **direct defeat of SEC-4's segregation of duties**, and of the human-in-the-loop gate's meaning
> (a gate anyone can appoint themselves to is not a gate). **Q3(d) was recorded as considered and rejected.**

⚑ **"Signup" in the everyday sense — a public sign-up form — is OUT OF SCOPE for this pass and is not an open
question in it.** The plan file is titled for the pair only because the register item and its predecessors are.

---

## 1. Ground truth — traced from disk, not assumed

### 1.1 What an unauthenticated user experiences TODAY in a real browser

`main.jsx` composes the transport and mounts `App`; `App`'s effect calls `loadCurrentRole(transport)` →
`GET /session` → **401** `{"error":{"code":"unauthenticated","message":"Authentication is required."}}` →
`sessionClient.js:49` catches and returns **`null`**.

| Surface | What renders |
|---|---|
| `AppFrame` | renders normally; `RoleProvider value={null}` |
| `RoleGate` | `caps = null` → `allowed = false` → every gated affordance renders its fallback (`null`) — **silently absent** |
| `QueueView` | R2 → 401 → `queue-state-error`: **visible "Authentication is required."**, hidden `queue-error-code`, a **Retry** button |
| `HistoryView` | R6 → 401 → its own equivalent error panel |
| `MemoView` / `ApprovalGateView` | never mount — no queue rows, so no selection is possible |

⚑ **It does not crash, hang, or blank.** The full chrome loads with **two polite error panels** and Retry buttons
that will fail identically forever, and **no affordance of any kind to authenticate**. A permanent, well-behaved
dead end — arguably worse than a hard failure, because nothing tells the user what to do. **That is the gap this
pass closes.**

### 1.2 The unit conventions a new view must satisfy

Every existing view (`queue`, `memoView`, `approvalGate`, `overrideForm`, `history`, `outlierView`) follows the
same shape, and a login view must too:

* `<unit>/` with `copy.js` (**all** UI strings; no inline labels — COPY-1), `fetchSeam.js` (request builders +
  `normalizeError` to the WIRE-1 §4 envelope), the stateful view component, `components/` for presentational
  parts, and `__tests__/`.
* **Four-state machine** (FETCH-1): `loading → ready | empty | error`, `error --Retry--> loading`.
* **`ErrorEnvelopeToRenderPattern` (ERROR-1)**: `message` visible, `code` in a hidden testid-only node,
  `detail` **never** rendered.
* **Per-unit lint tests** mirroring `eslint.<unit>.rules.test.js` — the **reused, unmodified** shell
  `no-inline-label` + `advisory-vocabulary` rules plus a unit testid pattern, each proven non-vacuous.
* **Structural tests**: `nots.test.js` (no `.tsx`), `refNotOwn.imports.test.js` (no backend import, no sibling-unit
  import), `boundedFetch.test.js`, `testid.test.jsx`.
* **Own-local seam**: the fetch seam **mirrors** its siblings and **imports none of them** — cross-unit
  consistency comes from the WIRE-1 contract, never from importing a sibling.

⚑ **Advisory-vocabulary applies here too**: `FORBIDDEN_TERMS.systemOutput` = `DECLINE` / `decision` / `approved` /
`declined`. Login copy must avoid them — *"Sign-in failed"* is fine; *"your sign-in was **declined**"* is a lint
error. Cheap, but real.

### 1.3 Confirmed clear

* **No backend test touches the frontend.** U23 references only `main.jsx`, `package.json`, `vercel.json`,
  `index.html`, `vite.config.js` and enumerates **no** `frontend/src` subdirectory — a new `frontend/src/login/`
  breaks nothing there.
* **No test anywhere asserts that auth UI must NOT exist.**
* **`seams.js`'s five-key set is safe** — **Q13(a)** already settled that the login client follows
  `sessionClient.js`'s **non-seam** precedent (*"a one-shot read, not a unit seam"*), so
  `app.test.jsx:259` stays green untouched. **This plan honors that; it is not re-opened.**

---

## 2. ⛔ The one material collision — `app.test.jsx:156`

```js
it('an unauthenticated session leaves a null role and still renders (fail-closed, not an error)', ...)
  // renders App with a 401 /session and asserts `history-list` IS in the document
```

**The frontend's current contract explicitly states: unauthenticated still renders the app.** A login gate
**reverses exactly that premise.** This is not an incidental breakage to fix — it is the assertion this work
changes, and it must be changed **deliberately, with its rationale recorded**. It is treated as a **named, gated
design decision** in **Q2**, not discovered at execution time.

Adjacent, non-blocking: `app.test.jsx:171` (*"mounts exactly the backed surfaces"*) pins present/absent testids and
will need the gate's two states reflected; `shell/rolegate.test.jsx:50` is unaffected and remains correct.

---

## 3. What this pass needs from the backend and WIRE-1: **NOTHING** — confirmed

| Question | Answer, verified |
|---|---|
| Any WIRE-1 change? | **No.** R8 `POST /login` and R9 `POST /logout` are **already contracted** (WIRE1-Fold-5, §2/§3/§5/§6/§7.2) and **already built and field-verified**. R1's shape is byte-unchanged. This pass **consumes** the contract; it does not amend it. |
| Any backend change? | **No.** `/login`, `/logout`, `/session` all exist and are exercised end-to-end against a real Postgres. |
| Any new route, migration, or schema? | **No.** |
| Any frozen backend test touched? | **No** — this pass writes no Python at all. |

⚑ If execution surfaces a need for **any** backend or WIRE-1 change, that is a **stop-gate**, not a quiet edit.

---

## 4. The shape of the work (design intent — the open choices are §6)

**A. The login view** — `frontend/src/login/`, following §1.2 exactly: `copy.js`, `loginFetchSeam.js`
(`buildLoginRequest({user_id, password})` → `POST /login`; `buildLogoutRequest()` → `POST /logout`;
`normalizeError`), `LoginView.jsx`, `components/`, `__tests__/`.

⚑ **The 204/401 handling is dictated by the backend and must not be "improved" on the client:**
* **204 No Content** on success — **no body**. The seam must not expect one.
* **401 for EVERY failure** — wrong password, unknown user, no credential row, **and lockout**, all with the
  **same message**. ⛔ **The frontend must NOT attempt to distinguish them, infer lockout from repeated failures,
  or show a "you may be locked out" hint.** The backend withholds that distinction deliberately, because it is a
  **user-enumeration oracle**; a client that reconstructs it re-opens the hole the backend closed. **The login
  view renders the server's message verbatim, exactly like every other view (ERROR-1).**

**B. Post-login behaviour** — see **Q3**.
**C. The unauthenticated gate** — see **Q1** and **Q2**.
**D. Logout** — see **Q4**.
**E. The `X-User-Id` legacy path** — see **Q5**.

---

## 5. ⚑ EXECUTION STEP 0 — verify BOTH cookie unknowns together, FIRST

**Before any login page is built, and not deferred.** Two predictions have been carried unverified, and they
**compound**: a `Secure` cookie is **dropped by browsers over `http://`**, and the local dev loop is
`http://127.0.0.1:5173` behind the Vite proxy.

| # | Unknown | Why it is unproven | How Step 0 settles it |
|--:|---|---|---|
| 1 | **`SESSION_COOKIE_SECURE=false` actually works for local dev over http** | The **fail-safe default** (`Secure`) was exercised in the manual verification; **its opt-out never was**. Register #25's discharge names this explicitly as **not claimed**. | Set `SESSION_COOKIE_SECURE=false`, run the backend, log in **from a real browser** at `http://127.0.0.1:5173`, and confirm the cookie is **stored and re-sent** |
| 2 | **Fold-3's `httpTransport.js` "no change needed" prediction** | It rests on `fetch` defaulting to `credentials: 'same-origin'`. **Never verified in a browser** — the manual pass used `curl` with an explicit `-b`, which bypasses cookie handling entirely. Carried on assumption **twice** already. | With the cookie set, confirm a subsequent `GET /session` **carries it automatically** with `httpTransport.js` **unmodified** |

⛔ **STOP-GATE**: if either fails, **stop and report** rather than building a login page on top of a broken
premise. Failure of (2) specifically means `httpTransport.js` — a **frozen-classified** file — needs a change,
which is its own decision, **not a quiet one-line edit** (that was an explicit stop-gate in the backend pass and
remains one here).

⚑ **This is the one step that cannot be done by me**: it needs a real browser and a running backend. It is
**yours to run**, exactly as the login verification was.

---

## 6. THE OPEN QUESTIONS

> Every `[Answer]` tag is **BLANK**. Nothing proceeds until all are filled, after which the **mandatory
> ambiguity-check** runs.

---

### Q1 — How does an unauthenticated user reach the login page?

* **(a) — Top-level gate in `App.jsx`.** `App` already calls `loadCurrentRole` on mount. Extend that one existing
  effect to a three-state gate: `checking` → `authenticated` (mount the app as today) | `unauthenticated` (render
  `LoginView` **instead of** the app). One decision point, one place, no router.
* **(b) — Gate in `main.jsx`**, choosing what to mount before `App` renders. ⛔ `main.jsx` is **U23's** file; it
  would put auth logic in the deploy unit's entry and make `App` untestable in its unauthenticated state.
* **(c) — Per-view redirect** — each view detects its own 401 and shows a login prompt. ⛔ Six views each owning
  auth logic; the "who is logged in" decision would have no single home, and every frozen view would need editing.
* **(d) — A router with a protected-route wrapper.** ⛔ **Decision 6 (no router) has held for the entire build**;
  introducing one for a two-state gate is a large, unrelated architectural change.

**Recommendation (grounded): (a).** The state already exists — `App` fetches the role on mount and already
distinguishes null from non-null; today it just **renders the app anyway**. (a) turns an existing signal into a
branch, in the one component that already owns "which surfaces are mounted" (it owns `selectedId` for exactly this
reason). It needs **no router**, touches **no frozen view**, and keeps `App` fully testable in both states. ⚑ It
does mean `App.jsx` grows a second responsibility — but it is the *same* responsibility it already has
(composition + what-to-mount), not a new one.

**[Answer]**: (a) — top-level gate in App.jsx, extending the existing loadCurrentRole effect to a three-state gate (checking/authenticated/unauthenticated). Reuses the one place that already owns "which surfaces are mounted," touches no frozen view, needs no router.

---

### Q2 — `app.test.jsx:156`'s premise reverses. What should it assert instead?

**The named, gated design decision from §2.** Today it asserts *"an unauthenticated session leaves a null role and
**still renders**"* — which a login gate makes **false by design**.

⚑ **Supersede-not-rewrite applies**: the old assertion is **preserved with a note recording what it asserted, why
it was correct, and what replaced it** — exactly as `mounts NO unbacked surface` was superseded in the wiring
pass. **It is not deleted, and it is not quietly edited to pass.**

* **(a) — Supersede it with the inverse, stated positively**: *"an unauthenticated session renders the LOGIN view
  and mounts no application surface"* — asserting `login-view` present **and** `history-list` / `queue-view`
  **absent**. The old test's real content (*unauthenticated is a state, not an error*) **survives and
  strengthens**: it is still not an error, it is now an actionable state.
* **(b) — Keep it and add a second test**, leaving the old one asserting the app renders. ⛔ **Not available** —
  the two are contradictory; the old one would simply fail.
* **(c) — Delete it.** ⛔ Against the standing discipline; the project has never deleted an assertion to make a
  change pass.

**Recommendation (grounded): (a).** It is the only option that keeps the suite honest. ⚑ And the superseding note
should record the substantive point: **the old assertion was correct for a build with no way to log in** — *the
app rendering in a fail-closed null-role state was the best available behaviour when authentication did not
exist*. It stops being correct the moment a login page does exist. That is a **premise change, not a regression**,
and the note should say so.
⚑ **`app.test.jsx:171`** (*"mounts exactly the backed surfaces"*) also needs its authenticated/unauthenticated
states reflected — same discipline, same pass.

**[Answer]**: (a) — supersede app.test.jsx:156 with the inverse, asserting login-view is present and history-list/queue-view are absent for an unauthenticated session. The superseding note should record that the old assertion was correct for a build with no way to log in — the app rendering in a fail-closed null-role state was the best available behavior before authentication existed — and that this is a premise change, not a regression. Apply the same treatment to app.test.jsx:171's authenticated/unauthenticated states in the same pass.

---

### Q3 — What happens immediately after a successful login?

R8 returns **204 with `Set-Cookie` and no body** — so the client learns *"it worked"* but **not who it is**.

* **(a) — Re-run the existing `loadCurrentRole` check.** On 204, call the same `GET /session` the gate already
  uses; on success the gate flips to `authenticated` and the app mounts. **One code path for "who am I", used at
  boot and after login.** No reload, no navigation, state preserved.
* **(b) — Full page reload** (`window.location.reload()`). Simple and guaranteed to pick up the cookie, but throws
  away all React state, flashes, and is a blunt instrument for a state change the app can already observe.
* **(c) — Have the login response carry the identity** so no second call is needed. ⛔ **Not available without a
  WIRE-1 amendment** — R8 is contracted as **204 no-content**, and §3 confirms this pass amends nothing.

**Recommendation (grounded): (a).** It reuses the **exact** mechanism the gate already depends on, so there is one
definition of "who is the current user" rather than two that could disagree. It also means the post-login path is
**already covered** by whatever tests cover the boot path. ⚑ (b) is worth naming as the fallback **if and only if**
Step 0 reveals a cookie-timing problem — but on current evidence there is none, and reaching for a reload first
would be solving a problem we have not observed.

**[Answer]**: (a) — re-run the existing loadCurrentRole check after a 204 login response, reusing the exact mechanism the gate already depends on rather than introducing a second definition of "who is the current user." Keep (b) (full reload) named as the fallback only if Step 0 reveals a real cookie-timing problem — don't reach for it preemptively.

---

### Q4 — Where does the logout affordance live?

* **(a) — In `AppFrame`** (`shell/components/AppFrame.jsx`), the app-wide chrome that already hosts the
  `RoleProvider`. ⚠️ **`AppFrame` is a FROZEN `ui-shell` component** — editing it is a frozen-unit change needing
  its own authorization.
* **(b) — In `App.jsx`**, rendered as a sibling above the mounted views. `App.jsx` is the composition root and is
  **not** frozen (the wiring pass edited it). No frozen unit touched.
* **(c) — Inside the login unit**, exported and mounted by `App.jsx` — same placement as (b), but the button and
  its copy live with the rest of the auth UI.

**Recommendation (grounded): (c), mounted by `App.jsx`.** It gets (b)'s "no frozen unit edited" property while
keeping **all** auth copy and behaviour in one unit — so the advisory-vocabulary lint, the testid convention and
the logout seam all live where the login seam does. ⚑ (a) is the *aesthetically* right home — logout belongs in
app chrome — but `AppFrame` is frozen, and a **cosmetic placement preference is not a reason to reopen a frozen
unit**. If chrome placement is genuinely wanted later, that is its own authorization.
⚑ **Note**: `RoleGate` should **not** gate logout — every authenticated role can log out, and `RoleGate`'s
`admin` row has `{act: false, read: false}`, so gating it would strand admins in a session they cannot end.

**[Answer]**: (c) — logout lives inside the login unit, mounted by App.jsx. Keeps all auth copy/behavior/lint/testid conventions in one unit without touching the frozen AppFrame. Confirm explicitly that RoleGate does not gate the logout affordance, since admin's {act: false, read: false} row would otherwise strand admins in a session they can't end.

---

### Q5 — What happens to the now-dead `VITE_USER_ID` / `X-User-Id` path?

**Fully inert**: `main.jsx:23` reads it, `httpTransport.js:42` sends `X-User-Id`, and the backend **no longer
reads it at all** (`test_the_x_user_id_header_is_no_longer_trusted` asserts exactly that). Three distinct
problems: **misleading docs** (`httpTransport.js:16` still calls it *"the client mirror of the server's deferred
handshake seam"* — false since WIRE1-Fold-5; **register #13's shape**), a **minor hygiene issue** (a user id in
every request header for no purpose), and ⚑ **two tests pin the behaviour**
(`httpTransport.test.js`: *"sends the X-User-Id stub header when a userId is configured"* / *"omits the stub header
entirely when no userId is configured"*), making removal a **matched pair**.

* **(a) — Remove entirely**: drop `userId`/`USER_ID_HEADER` from `httpTransport.js`, the `VITE_USER_ID` read from
  `main.jsx`, the `.env.local` line, **and** the two tests. ✅ No dead code, no misleading docs, no stray header.
  ⛔ Touches `httpTransport.js` and `main.jsx` (**U23's file**), and deletes two currently-green tests — a matched
  pair needing deliberate authorization.
* **(b) — Keep it inert, correct the docstrings**: leave the mechanism, supersede `httpTransport.js:16` and
  `.env.local`'s prose to say the header is **retired and ignored by the server**. ✅ Smallest diff; **no test
  deleted**; kills the #13-shaped falsehood. ⛔ Dead code survives, and the header keeps being sent.
* **(c) — Leave untouched.** ⛔ Leaves a **false docstring** describing a live mechanism that is dead — precisely
  what register #13 exists to track, in a file a maintainer reads to understand how auth reaches the server.

**Recommendation (grounded): (b) now, with (a) as its own later change if wanted.** The **falsehood** is the part
that actually costs something — a maintainer reading `httpTransport.js` today is told the `X-User-Id` header is
the auth mechanism, which is **wrong and actively misleading now that a real one exists**. (b) fixes that with a
supersession note, deletes no green test, and touches no U23 file. **(a) is the tidier end state** and I would
support it as a deliberate cleanup — but bundling a two-test deletion and a `main.jsx` edit into a *feature* pass
is exactly the scope-creep this build has refused elsewhere. ⚑ **Explicitly recorded either way**: leaving the
header inert means every request still carries a `VITE_USER_ID` value if one is configured; it is **ignored**, but
it is **sent**.

**[Answer]**: (b) — keep the X-User-Id/VITE_USER_ID mechanism inert but correct the misleading docstrings in httpTransport.js and .env.local to state plainly that the header is retired and ignored by the server. Full removal (a) is a legitimate future cleanup but is explicitly deferred — bundling a two-test deletion and a main.jsx edit into this feature pass is the scope-creep this build has consistently refused. Record this deferral by name so it isn't silently forgotten.

---

## 7. Holds for this pass — verified, all currently upheld

| Hold | Status |
|---|---|
| **No code written** | ✅ This is a plan |
| No backend file touched | ✅ Zero Python read-modified |
| **WIRE-1 untouched** | ✅ R8/R9 already contracted; §3 confirms nothing is needed |
| No frozen `ui-shell` component edited (`AppFrame`, `RoleGate`, `roleContext`) | ✅ Q4 steers away from `AppFrame` |
| `seams.js` five-key set preserved (Q13a) | ✅ Login client is **not** a seam |
| No frozen view unit edited (`queue`, `memoView`, `approvalGate`, `overrideForm`, `history`, `outlierView`) | ✅ The gate lives in `App.jsx` |
| `app.test.jsx:156` **not yet touched** | ✅ Its supersession is **Q2**, gated |
| **No commit** | ✅ |

**Suites carried, not re-run**: backend **1615 / 0 / 43 / 5 / 99.63%** · frontend **687 / 137 / 0**.

---

## 8. What happens after the answers

1. Answers recorded verbatim in `audit.md`; embedded back into §6.
2. **The mandatory ambiguity-check runs.** Named in advance: **(i)** does the Q1 gate collide with any frozen
   view's own tests beyond `app.test.jsx`; **(ii)** does the login unit's lint/testid/structural test set have a
   gap against the six existing units' conventions; **(iii)** does Q5's chosen option touch a U23-owned file; and
   **(iv)** does the gate's `checking` state introduce a flash-of-login-page before `/session` resolves — a real UX
   defect that must be designed for, not discovered.
3. **Then a code-gen plan**, with **Step 0 (§5) executed FIRST**, TDD order, predicted deltas stated in advance,
   and named stop-gates.
4. ⚑ **Nothing is built on either cookie assumption until Step 0 has actually been run in a browser.**

---

**STOPPED AT THE PLAN-FILE GATE.** No code. No component. No test. No backend file. WIRE-1 untouched. **Five
questions await answers.**

---

## 9. MANDATORY AMBIGUITY-CHECK — run against the Q1–Q5 answer set

**Run**: 2026-07-26 · **Result**: ✅ **CLEAN — 4 directed checks, 4 folds, no surface-and-stop.** Every finding
established by reading the asserting code.

### ✅ Check (i) — does the Q1 gate collide with any frozen view or shell test beyond `app.test.jsx`? **CLEAN**

A repo-wide scan for tests importing or rendering the composed `App` returns **exactly two files**, and one is a
false positive:

* `frontend/src/app/__tests__/app.test.jsx` — the real one, already scoped as **Q2**.
* `frontend/src/shell/__tests__/testid.test.jsx` — ⚑ **matched only on the substring `App`**; it renders
  **`AppFrame`** in isolation (`render(<AppFrame user={{role:'underwriter'}}>x</AppFrame>)`), never the composed
  app. **Not a collision.**

**FE-Fold-1**: every one of the six view units tests its component **in isolation**, never through `App`. The
gate changes only what `App` mounts, so **no frozen view test and no frozen shell test observes it.** The blast
radius really is the one file Q2 already names.

### ✅ Check (ii) — is the login unit's test set complete against the six units' conventions? **CLEAN**

Enumerated across `queue` / `memoView` / `approvalGate` / `overrideForm` / `history` / `outlierView`:

| Convention | Present in |
|---|---|
| `copy.js` + `<x>FetchSeam.js` + `<X>View.jsx` at unit root | **6 / 6** |
| `nots.test.js` (no `.tsx`) | **6 / 6** |
| `eslint.<unit>.rules.test.js` (reused shell rules + unit testid pattern, non-vacuous) | **6 / 6** |
| a fetch-seam test | **6 / 6** |
| state + transition tests | **6 / 6** |
| at least one import-isolation test (`noBackendImport` / `refNotOwn` / `noSiblingImport`) | **6 / 6** |
| `testid(s).test.jsx` | 5 / 6 (`queue` covers it per-component) |
| `boundedFetch.test.js` | 5 / 6 (`outlierView` uses `noWriteSeam` instead) |

**FE-Fold-2**: the baseline is **derivable, not ambiguous** — the login unit takes the 6/6 set plus
`testid.test.jsx` and `boundedFetch.test.js`. **No gap requires a question.** ⚑ One convention worth stating
because it is easy to miss: two units (`history`, `outlierView`) keep a separate `testids.js` at unit root; the
other four inline them. Either is conventional — the login unit follows whichever its testid count justifies.

### ✅ Check (iii) — does Q5(b) touch a U23-owned file? **CLEAN — and this is the check that matters most for Q5**

U23 owns: `render.yaml` · `frontend/vercel.json` · `frontend/index.html` · **`frontend/src/main.jsx`** ·
`frontend/vite.config.js` · `deploy/` · `backend/deploy_config/`.

Q5(b) edits **`frontend/src/app/httpTransport.js`** (a docstring) and **`frontend/.env.local`** (a comment).

* ⚑ **`main.jsx` is NOT touched by Q5(b)** — that is exactly why (b) was separated from (a). Option **(a)** would
  have edited `main.jsx` to drop the `VITE_USER_ID` read, putting a **U23-owned file** in a feature pass. **(b)
  avoids that entirely.**
* `httpTransport.js` is `is_under_frozen`-classified but **U23 does not own it**, and **no test asserts its
  content** — the only other reference is `app.test.jsx` importing the *function*. A docstring edit is inert.
* `.env.local` is **gitignored** (`.gitignore:4:.env.*`, verified) — the edit is not even a tracked change.

**FE-Fold-3**: Q5(b) is confirmed U23-free and test-neutral. ⚑ **The deferral of (a) is recorded by name here so
it is not silently forgotten**: *full removal of the `VITE_USER_ID` / `X-User-Id` path — dropping `userId` from
`httpTransport.js`, the `import.meta.env` read from `main.jsx`, the `.env.local` line, and the two
`httpTransport.test.js` tests that pin the behaviour — remains a legitimate future cleanup, deliberately deferred
out of this pass as scope-creep.*

### ✅ Check (iv) — does the gate flash a login page before `/session` resolves? **CLEAN, with a BINDING constraint and one disclosed limitation**

**The risk is real.** `App` today does `useState(null)` for role and renders immediately while `/session` is in
flight. A naive two-state gate would therefore render the **login page on every page load**, for a fraction of a
second, **including for already-authenticated users** — a visible flash on every navigation.

**FE-Fold-4 — BINDING**: the gate is **three-state and must start in `checking`**, rendering **neither** the app
nor the login view until `/session` resolves. This is why **Q1(a)'s answer specified three states** rather than a
boolean, and it is not optional. `checking` renders a minimal loading affordance following the units' own
`aria-busy` loading convention — **never** the login form, and **never** the app surfaces.

> ⚑ **DISCLOSED LIMITATION, a consequence of Q3(a) — recorded, not re-opened.** `loadCurrentRole` **fail-closes
> to `null` on ANY failure** — a 401 **and** a network error, a DNS failure, or a backend that is simply down are
> indistinguishable to it. So if the backend is unreachable, the gate shows the **login page**, the user submits,
> and only then sees a network error. **Q3(a) settled that the gate reuses `loadCurrentRole`**, and that is the
> right call for having one definition of "who is the current user" — this is its cost, stated plainly rather
> than discovered. Distinguishing the two would mean the gate calling `createSessionClient` directly (which
> rejects with the envelope) instead, which is a **different answer to Q3** and is **not** taken here.

### Verdict

**CLEAN.** No further ambiguity. Proceeding to the code-gen plan, whose **Step 0 is a hard gate**.
