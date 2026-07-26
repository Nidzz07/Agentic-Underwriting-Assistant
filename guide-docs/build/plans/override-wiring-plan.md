# Override Wiring Plan — mounting the mandatory-reason decline path

**Stage**: POST-BUILD → scoping/planning pass
**Status**: ⛔ **PLAN GATE — 6 questions open, none pre-filled. No code written.**
**Date**: 2026-07-26
**Predecessors**: `frontend-backend-wiring-plan.md` (Q5(c) excluded override), `frontend-login-signup-plan.md`, the 204 regression fix (`a224c27`)

---

## 0. What this pass is — and what it is not

**This is a wiring/mounting pass, not a design pass.** Both halves already exist and are tested:

* the frontend unit `frontend/src/overrideForm/` — 8 source files, **29 test files**, full FD / NFR-Requirements / NFR-Design / Code-Gen artifacts under `guide-docs/build/ui-override-form/`, built during the original 24-unit BUILD phase;
* the backend route — R5 `POST /recommendations/{id}/commit` already accepts `action: "override"` (`_PERMITTED_COMMIT_ACTIONS` is derived from the `CommitAction` enum, which has exactly `APPROVE` / `OVERRIDE`).

**Nothing is designed here.** No new component, no new route, no new seam, no contract change. The work is: mount one already-built view, decide four disclosed-cost questions, and — the part that carries real information — **verify a path that has never run against a real database.**

⚑ **It is smaller than the queue→memo→commit pass it follows.** That pass needed new selection state in `App.jsx` and raised a seams-layer question. This one needs **neither** (§1.1, §1.2).

---

## 1. Measured inventory — what is on disk, verified this session

### 1.1 `seams.js` already registers `override` — no seam-layer change

`frontend/src/app/seams.js:36` already contains `override: createOverrideFetch(transport)`. It is **one of the five keys** the composition root wires.

⚑ **Consequence, and it is the single biggest cost reduction versus the last wiring pass**: `app.test.jsx`'s `wires all five units seams` exact-key assertion **stays green untouched**. In the previous pass, Q4(b) would have broken exactly that test by adding a sixth key. Here there is no seams question at all.

### 1.2 `App.jsx` already holds selection state

`App.jsx:45` holds `selectedId`; `:90-100` is the selection-conditional block already mounting `MemoView` + `ApprovalGateView`. Mounting override is **one JSX line inside an existing block** — no new state, no new prop threading, no new callback.

### 1.3 The unit is complete and role-aware by construction

`RoleGate can="act"` sits **inside** `OverrideAffordance` (`components/OverrideAffordance.jsx:20`), not around the view. `AppFrame` already hosts the `RoleProvider`. So mounting needs **no role prop and no `RoleGate` wrapper at the call site** — `underwriter` sees the affordance, `auditor`/`admin`/`null` do not, and that is already asserted by `overrideForm.rbac.test.jsx` across all three roles plus null.

### 1.4 ⚑ Phase-dependent testid — the accidental-pass trap, named in advance

`OverrideFormView` renders **two different testids depending on phase** (`OverrideFormView.jsx:79-98`):

| Phase | Renders `override-form-panel` | Renders `override-form-view` |
|---|---|---|
| `loading` / `pending` / `errorRead` / `errorCommit` | ✅ | ❌ |
| `committed` | ✅ | ❌ |
| `ready` / `confirming` / `submitting` | ✅ | ✅ |

**Any assertion written against `override-form-view` therefore silently depends on the R4 fixture reaching `ready`.** With `R4_PENDING` the view mounts and renders, but `override-form-view` is absent — so a "not mounted" assertion would pass **for the wrong reason**.

This is precisely the trap `app.test.jsx:323-325` records the build refusing twice before (`approval-gate` vs `approval-gate-view`). It is named here so the third instance is not walked into.

### 1.5 ⛔ CORRECTION to this pass's own scoping report

**In the pre-plan report I stated that `app.test.jsx:317` needs superseding, with both the `:329` and `:344` assertions updated. That was wrong, and the instruction to supersede it should not be executed as written.** Measured on disk:

* **`:329`** (`expect(screen.queryByTestId('override-form-view')).toBeNull()`) sits in the **no-selection** state — that test uses `fakeServer()` and never clicks a queue row. Override is inside the `selectedId` block, so it is **not mounted in that state regardless of this pass**. The assertion **stays true and stays green**.
* **`:344`** asserts the same id null in the **unauthenticated** state. Nothing mounts when unauthenticated. **Stays true, stays green, and stays meaningful.**
* `:376` (`no selection -> no detail surfaces`) never mentions override.
* `:368` (`selection mounts the detail surfaces`) asserts memo + gate present and says **nothing** about override.

**Therefore: mounting `OverrideFormView` breaks ZERO existing tests.** There is no supersession to perform for correctness.

⚑ **But there IS a real problem, and it is a comment, not an assertion.** After mounting, `:316`'s comment — *"Q5(c) deliberately excludes override and outlier — asserted absent in BOTH states"* — becomes **factually false as a description of the design**, while its assertion keeps passing for an unrelated reason (nothing is selected). A passing assertion whose stated rationale is untrue is exactly the "passing by accident" failure mode this file already twice refused. **That is Q4.**

### 1.6 The stale `seams.js` docstring

`seams.js:6-19` still reads:

```
// SCOPE A — what is actually backed (the rest is wired but unbacked, honestly):
//     queue    -> R2  ⛔ 501 not_implemented
//     memo     -> R4  ⛔ 501
//     commit   -> R5  ⛔ 501   (approve)
//     override -> R5  ⛔ 501   (override)
...
// which is why they are NOT mounted in App.jsx: a rendered surface that can only ever error would
// imply backing that does not exist.
```

**Every load-bearing claim in that block is now false.** Scope B made all seven routes live; the wiring pass mounted queue/memo/commit against a live backend and the login pass mounted a login view. This is the same class of defect as the `httpTransport.js` AUTH docstring that Q5(b) corrected in the login pass — a comment that actively misdescribes how the system works. **That is Q1.**

### 1.7 The third duplicate R4 fetch

`OverrideFormView` runs its own `fetchContext` (R4) on mount (`OverrideFormView.jsx:40-54`), exactly as `MemoView` and `ApprovalGateView` already do. `App.jsx:92-94` already discloses the existing pair as **Fold 4**:

> *MemoView and ApprovalGateView each issue their OWN GET /applications/{id}/memo, so a selection makes two identical R4 requests. Each frozen unit owning its own fetch is the design.*

Mounting override makes it **three**. **That is Q2.**

### 1.8 Backend override machinery — read, not assumed

| Fact | Evidence on disk |
|---|---|
| R5 accepts `override` | `not_wired.py:81` `_PERMITTED_COMMIT_ACTIONS = frozenset(member.value for member in CommitAction)`; `record_schema.py:35-38` `APPROVE = "approve"` / `OVERRIDE = "override"` |
| Blank reason → 409 | `commit_service.py:106-107` `if checked_action is CommitAction.OVERRIDE and (reason is None or reason.strip() == ""): raise CommitRejected` → `not_wired.py:280-283` maps `CommitRejected` → `COMMIT_CONFLICT` (409) |
| **R5 returns 200 + body, NOT 204** | `not_wired.py:286` `return committed.model_dump(mode="json")` on a `@router.post` with no `status_code=` |
| Underwriter-only | `require_commit` (`dependencies.py:255`); docstring `:270`: *"WIRE-1 §3 and PERMISSION_MATRIX AGREE on R5 (underwriter only) — there is no divergence here"* |
| #19's CAS is action-agnostic | `not_wired.py:259` `claim = store.claim_for_commit(recommendation_id)` — keyed on `recommendation_id` only, taken **before** the action reaches the gate. No `approve`/`override` branch exists in the claim path. |

**⚑ The 204 fix does not apply to R5 and does not need to.** The fix is keyed on `response.status === 204`; R5 answers 200 with a `CommittedDecision` body, which `overrideFetchSeam.js:69` expects. The two are independent. Checked, not assumed.

**⚑ Claim ordering, worth knowing before live verification**: the claim is taken *before* the gate runs, so a blank-reason override **takes the claim, is rejected, and releases it** (`_release`, `not_wired.py:282`), returning the case to `drafted` and immediately re-committable. Correct and deliberate (`not_wired.py:243-245`) — but it is a real state transition, not a no-op, which is why Step 6 verifies the release actually happened rather than only that a 409 came back.

### 1.9 ⛔ What has NEVER been verified against a real database

The register #25 discharge (`guide-state.md:5986-6010`) is the project's only live-Postgres commit evidence, and it reads:

> `{"recommendation_id":"REC-DEMO-0002-25a195b9","underwriter_id":"demo-underwriter","action":"approve","reason":null}`

with the `psql` row confirming `action=approve`.

**Consequently, and stated plainly:**

1. **`action=override` has never been committed against a real Postgres.**
2. **No `AuditRecord` row with a non-null `reason` has ever been observed on disk** — the mandatory-reason field, which is the entire point of this unit and a hard constraint of the brief ("override with mandatory reason field", §3 Component 5), has never been seen persisted.
3. **BR-COMMIT-GATE's blank-reason rejection has never been exercised over HTTP against a live database** — only against the frozen service in unit tests.

⚑ **This is the actual deliverable of the pass.** The mounting is one line. The evidence is the work.

---

## 2. Proposed scope

**In scope**: mount `OverrideFormView` in `App.jsx`; resolve Q1–Q4; add frontend tests for the newly-mounted surface; manual live verification (Step 6) of the override commit and the blank-reason rejection.

**Out of scope, explicitly**: any backend file · WIRE-1's contract text · `OutlierView` (still permanently empty under #17) · any frozen `ui-shell` component or view unit · `main.jsx` (U23-owned) · any register item's status · any commit (the user decides).

---

## 3. Open decisions — answer inline, none pre-filled

### Q1 — the stale `seams.js` docstring (§1.6)

Every backing claim in `seams.js:6-19` is false, including the explicit rationale *"which is why they are NOT mounted in App.jsx"* — which this pass makes false twice over. Precedent: Q5(b) of the login pass corrected exactly this class of defect in `httpTransport.js` rather than leaving a comment that misdescribes the system.

- **(a) Correct the docstring in this pass — rewrite the backing table to Scope-B reality and record what superseded it, matching Q5(b)'s treatment. — RECOMMENDED.** It is a comment-only edit to a file this pass already touches conceptually; `seams.js` is not frozen and no test asserts its text (verified: the only importers call `createSeams`). Leaving a false map of what is backed, in the exact file whose job is to document what is backed, is the defect Q5(b) was raised to prevent.
- **(b) Correct it, and additionally note per-route which are live.** Slightly more informative, slightly more to keep true later.
- **(c) Leave it and open a register item.** Honest bookkeeping, but it defers a two-minute comment fix into a tracked debt with no offsetting benefit.
- **(d) Leave it untouched and silent.** Rejected on this project's own precedent.

**[Answer]**: (a) — correct the seams.js docstring in this pass, rewriting the backing table to Scope-B reality and recording what superseded it, matching Q5(b)'s treatment in the login pass. A comment that actively misdescribes what's backed, in the exact file whose job is to document that, shouldn't survive another pass.

---

### Q2 — the third duplicate R4 fetch (§1.7)

Mounting override takes a selection from **two** identical `GET /applications/{id}/memo` requests to **three**. Fold 4 already disclosed the first duplicate as an accepted consequence of each frozen unit owning its own fetch.

- **(a) Leave it as a disclosed, accepted cost — extend the Fold-4 comment from "two" to "three" and move on. — RECOMMENDED.** Consistent with how the first duplicate was handled, and with the #15 precedent the comment cites. The alternative requires either lifting R4 into `App.jsx` and prop-injecting it (which changes how three frozen units receive data — a redesign, not a wiring pass) or adding a caching layer to the transport (new machinery, new failure modes, and it would silently change every other route's semantics). Three redundant GETs on a local selection is a real but small cost; the architecture that causes it is deliberate and was ratified twice.
- **(b) Address it now — introduce request de-duplication or a shared R4 read in the composition root.** Removes the waste, but is genuinely new design inside a pass scoped as mounting, and touches how frozen units are fed.
- **(c) Leave it and open a register item so it is tracked rather than merely commented.** Reasonable if you want the debt visible in the register rather than only in a code comment. Compatible with (a).
- **(d) Mount override *instead of* `ApprovalGateView` when a case is selected (see Q3(c)), which keeps the count at two.** Only coherent if Q3 goes that way.

**[Answer]**: (a) — leave the third duplicate R4 fetch as a disclosed, accepted cost, extending the Fold-4 comment from "two" to "three." The alternative is a redesign of how frozen units receive data, which this pass is correctly scoped to exclude.

---

### Q3 — two commit affordances on screen at once (UX / demonstration)

With override mounted alongside `ApprovalGateView`, a selected case shows **both** "Approve" and "Override recommendation" for the same `recommendation_id`. Both POST the same R5. Under #19's CAS the first click wins and the second returns **409 `commit_conflict`**, surfaced by whichever unit lost as its ordinary error state.

⚑ This is **correct behaviour, not a bug** — and it is arguably the most honest possible demonstration of the human-in-the-loop gate: the underwriter genuinely chooses agree-or-disagree, and the system genuinely refuses to record two outcomes for one recommendation.

- **(a) Mount both, side by side, and accept the 409-on-second-click as correct, demonstrable behaviour. — RECOMMENDED.** It matches the brief's Component 5 ("override with mandatory reason field" as a peer of approval, not a replacement), it exercises #19's guard through the UI for the first time, and it requires no new coordination state in `App.jsx`. The losing unit already renders a well-formed error envelope — no special-casing needed. ⚑ Accept knowingly: a user *can* produce a 409 by clicking both, and that will look like an error to someone who does not know why.
- **(b) Mount both, but have `App.jsx` hide the other affordance once one commits.** Friendlier, but introduces cross-unit coordination state in the composition root — the root would begin arbitrating between two frozen units, which is a design change, and it would *mask* #19's guard rather than demonstrate it.
- **(c) Mount override INSTEAD of `ApprovalGateView`.** Keeps one write path and answers Q2 for free, but removes the approve path that was just verified working — a regression in demonstrated capability.
- **(d) Mount override behind an explicit toggle/disclosure ("Disagree with this recommendation?").** Closest to real underwriting UX and reduces accidental double-commits, but it is new UI design, which this pass is scoped to exclude.

**[Answer]**: (a) — mount both Approve and Override side by side, accepting the 409-on-second-click as correct, demonstrable behavior. This is the most honest demonstration of the human-in-the-loop gate and exercises #19's guard through the UI for the first time. Accepted knowingly that a user can produce a 409 by clicking both.

---

### Q4 — `app.test.jsx:317`'s comment vs. its assertion (§1.5)

Given the correction in §1.5 — mounting breaks **zero** tests — the question is not how to supersede a failing assertion but what to do about a **true assertion with a now-false rationale**.

- **(a) Keep both assertions; rewrite ONLY `:316`'s comment to state the real reason each is true (`:329` = nothing selected; `:344` = unauthenticated), and add a NEW positive test asserting override IS mounted on selection. — RECOMMENDED.** Nothing is deleted or weakened; the misleading rationale is corrected; and the actual new behaviour gets a test that can fail. ⚑ Per §1.4 the new test must use a **`ready`** R4 fixture (`R4_READY` already satisfies `report.recommendation`) and assert `override-form-view`, not `override-form-panel` — the panel renders in every phase and would pass vacuously.
- **(b) Same as (a), but also move override's absence assertion into the no-selection test at `:376`, where it would mean something.** Strictly better coverage; slightly more churn across two tests.
- **(c) Remove override from `:329`'s assertions entirely** (it now asserts nothing about the design) and keep it only at `:344`. Defensible, but deletes a check rather than re-homing it.
- **(d) Leave the file untouched.** Rejected: it preserves a comment that misstates the design, which is the specific failure mode `:323-325` records the build refusing.

**[Answer]**: (a) — keep both existing assertions at :329 and :344 unchanged, rewrite only :316's comment to state the real reason each is true, and add a new positive test asserting override IS mounted on selection, using a ready R4 fixture and asserting override-form-view specifically (not override-form-panel), per the phase-dependent testid trap named in §1.4.

---

### Q5 — test depth for the newly-mounted surface

The established pattern is injected `fetchImpl` over the **real** transport (`backedServer`), never a global `fetch` mock. `backedServer`'s R4/R5 handlers already serve override unchanged — a POST to `/recommendations/{id}/commit` is matched by method and path, not by action.

- **(a) Mirror the approve path's existing coverage: one mount-on-selection test + one end-to-end test asserting Confirm POSTs exactly `{ action: "override", reason: "<text>" }` with no `underwriter_id`, plus one blank-reason test asserting the affordance stays disabled. — RECOMMENDED.** Directly parallels `the approve path end-to-end over the transport` (`:385`), which is the closest precedent, and pins the two properties that matter: the wire body's exact shape, and that the UI gate holds.
- **(b) (a) plus a test for the 409 double-commit collision from Q3(a)**, asserting the second unit renders its error state. Higher value if Q3(a) is chosen, since it pins the behaviour that choice knowingly accepts.
- **(c) (a) plus (b) plus a role-matrix test at the composition-root level** (auditor/admin see no override affordance through the real mount). Some duplication with `overrideForm.rbac.test.jsx`, which already covers all three roles plus null in isolation.
- **(d) Minimal — mount-on-selection only.** Leaves the reason-carrying wire body, the unit's whole reason for existing, unasserted at the composition root.

**[Answer]**: (b) — (a) plus a test for the 409 double-commit collision from Q3(a), since Q3(a) was chosen and this pins the exact behavior that choice knowingly accepts, not just the happy path.

---

### Q6 — how far the manual verification goes (§1.9, Step 6)

This is the first time `action=override` and a non-null `reason` will exist on a real database.

- **(a) Full: happy path + blank-reason rejection + claim-release confirmation + `psql` read-back of the persisted `reason`. — RECOMMENDED.** This is the only option that closes all three never-verified gaps in §1.9 in one sitting, and the blank-reason path is the one the brief's hard constraint actually rests on. Matches Step 7 / Step 10 discipline, both of which paid off — Step 10 is what found the 204 defect.
- **(b) Happy path + `psql` read-back only.** Proves the reason persists; leaves BR-COMMIT-GATE's live rejection still unverified after this pass.
- **(c) Full, plus a deliberate double-commit to observe the 409 through the UI** (only meaningful under Q3(a)).
- **(d) API-level only via `curl`, no browser.** Cheaper, but would not exercise the mounted UI — and the last two defects this project found were both found in a browser and by nothing else.

**[Answer]**: (a) — full verification: happy path, blank-reason rejection, claim-release confirmation via a successful re-commit afterward, and psql read-back of the persisted reason. This closes all three never-verified gaps in one sitting, matching the discipline that caught the 204 defect at Step 10.

---

## 3A. Mandatory ambiguity-check — combined answer set

**Answer set**: Q1(a) · Q2(a) · Q3(a) · Q4(a) · Q5(b) · Q6(a). Every item below was measured on disk this session, not inferred from the earlier plan text.

**Internal consistency, checked first**: Q3(a) mounts both write paths → Q5(b)'s collision test has a subject; Q2(a) accepts three R4 reads, which Q3(a)'s side-by-side mount is what *causes* — the two answers are mutually reinforcing, not in tension. Q4(a) and Q5(b) both touch `app.test.jsx`; their interaction is Fold B below. **No answer contradicts another.**

**Result: CLEAN — 5 folds, no genuine gap, no surface-and-stop.**

### ⚑ Fold A (DIRECTED) — can the Q3(a) + Q5(b) collision test be built deterministically?

**Yes, and there is no race to begin with — the premise of the concern does not hold in this test tier.**

The concern assumes the two commits race. They cannot. `backedServer` injects a plain JS `fetchImpl`; `fireEvent.click` dispatches synchronously; and the test `await`s each commit to settle before firing the next. **The sequence is program order, not scheduling order.** Concretely:

1. select a case → all three detail surfaces mount;
2. type a reason into `override-reason-input` (override's affordance is disabled until then);
3. `approval-affordance-approve` → `approval-confirm-submit` → **`await findByTestId('approval-committed')`** ← the barrier that makes step 4 deterministic;
4. `override-affordance-button` → `override-confirm-submit` → assert `override-state-error` with `override-error-code` = `commit_conflict`.

Three facts make this stable, each verified rather than assumed:

* **Same URL.** Both units POST `/recommendations/rec-1/commit` — `ApprovalGateView` and `OverrideFormView` both read `recommendation_id` from the same `R4_READY` fixture. A commit-call counter keyed on that path is therefore sufficient.
* **No remount, no refetch between the two commits.** `OverrideFormView`'s `loadContext` depends only on `[overrideFetchSeam, applicationId]`; `seams` is a stable prop and `selectedId` does not change. Approve's success is internal to `ApprovalGateView` and changes no `App` state, so override stays in `ready` with its typed reason intact.
* **The losing render is already specified by the frozen unit.** `CommitStateView.jsx:9-11` states that `commit_conflict` is *"the SINGLE rendered conflict state for BOTH already-committed AND the blank-reason race/bypass tail"* — **the unit was designed for exactly this collision.** No special-casing is needed in `App.jsx` or anywhere else.

**One mechanical prerequisite, named**: `backedServer`'s `commitResponse` is currently a fixed value (`app.test.jsx:91`), so it cannot answer 200-then-409. Resolution: allow `commitResponse` to be **a function**, resolved per call. This is strictly additive and **cannot alter any existing caller** — all three current callers pass objects (`okJson(COMMITTED)`, `errJson(FORBIDDEN)`, default). No new helper is introduced and `fakeServer` is not touched.

⚑ **Honesty boundary, stated rather than blurred**: this test pins the **observable contract** of #19's guard (a second commit on the same recommendation returns 409, and the losing unit renders its ordinary error state). It does **not** test the compare-and-swap itself — that is a Postgres row-lock property, unreachable from a fake, and it is verified live at **Step 6.7**. The frontend test would pass against a backend with no CAS at all. Claiming otherwise would be the kind of "test that attests to a configuration nobody runs" this build has refused before.

**Direction chosen: approve wins, override loses.** The reverse direction would exercise `approval-state-error`, which `app.test.jsx:409` (`a commit error surfaces through the frozen gate own error state`) **already covers**. The override-loses direction is the one that adds coverage.

### ⚑ Fold B (DIRECTED) — do Q4's positive test and Q5(a)'s body-shape test overlap?

**They overlap in path but not in subject, and — the part that matters for counting — Q4's test and the first item of Q5(a) are THE SAME TEST, not two.**

Q5(a)'s text reads *"one mount-on-selection test + one end-to-end test … plus one blank-reason test"*. Q4(a) independently specifies *"a new positive test asserting override IS mounted on selection"*. **These name one artifact.** Counting them separately would have inflated the predicted delta by one — recorded here so the count is right in advance rather than corrected at the gate (the 712 → 716 lesson).

On genuine consolidation of the **remaining** pair (mount-on-selection vs. end-to-end body shape): the end-to-end test necessarily passes *through* the mounted state, since `override-reason-input` and `override-affordance-button` render only in `ready`. So it incidentally subsumes the mount assertion. **They should still stay separate**, for a reason with direct precedent: the approve path carries exactly this two-test structure — `selection mounts the detail surfaces` (`:368`) and `the approve path end-to-end over the transport` (`:385`). Merging them would leave a single failure that cannot distinguish *"the composition root stopped mounting override"* from *"the wire body changed shape"* — two unrelated defects with one indistinguishable symptom.

⚑ **A cheaper alternative was found, considered, and NOT taken.** The mount assertion could be folded into the existing `:368` test as one line — that test already selects with `backedServer()`/`R4_READY`, its subject is literally what selection mounts, and the in-place-extension pattern has precedent at `:332-335`. It would cost **+0 tests** instead of +1. **Q4(a)'s answer says "add a NEW positive test", so the standalone test is what gets built.** Recorded rather than silently substituted; if you prefer the +0 variant, say so and it is a one-line change to this plan.

### Fold C — Q1's blast radius on `seams.js` is nil, re-verified independently

Editing `seams.js`'s docstring is test-neutral. Re-measured this session rather than cited from the previous pass: the source-scanning tests (`nots`, `no*Import`, `boundedFetch`, `singleCallSite`, `refNotOwn`) walk `src/approvalGate`, `src/history`, `src/memoView`, `src/outlierView`, `src/overrideForm`, `src/queue` — **never `src/app`**. `seams.js` is imported only for `createSeams`, and no test asserts its text.

### Fold D — no vitest config change is needed

`src/overrideForm/__tests__/**` is **already** in the test `include` list and `src/overrideForm/**` already in the coverage `include` — confirmed by those tests executing in this session's runs (e.g. `overrideForm.error.test.jsx`). Unlike the login pass, **no `vitest.config.js` edit is required**, so the "include paths ADDED only, thresholds UNCHANGED" convention is not even exercised. The plan's file table would otherwise have repeated the login pass's one unpredicted file touch.

### Fold E — the blank-reason UI test asserts a *disabled affordance*, not a rejected request

Per Q5(a)'s third item: with a blank reason the UI **cannot issue** the request — `OverrideAffordance` is `disabled` via the single `isReasonPresent` predicate (`OverrideFormView.jsx:107`). So the frontend test asserts the affordance stays disabled and **no POST is issued**; it does **not** assert a 409. The 409 path is unreachable from the UI by construction, which is exactly why **Step 6.6 bypasses the UI** to exercise it. Two different claims, two different tiers, neither standing in for the other.

---

## 4. Execution plan — leaf-first, RED before GREEN

**Baseline**: 719 passed / 147 files / 0 failed / coverage 99.82%, thresholds 90/90/90/90. Backend carried at 1615/0/43/5/99.63%, **not re-run** (no backend file is touched).

**Predicted final: 723 / 147 / 0 — a delta of exactly +4, stated in advance.**

| # | Step | Files | RED first? | Δ |
|---|---|---|---|---|
| 1 | Re-run frontend, confirm the **719 / 147 / 0** baseline before touching anything | — | n/a | 0 |
| 2 | Extend `backedServer`'s `commitResponse` to accept a function (Fold A); **no test behaviour changes** | `app.test.jsx` | n/a — harness | 0 |
| 3 | Add **T1** `selection mounts the override form — the mandatory-reason path is reachable` (Q4(a)/Q5(a)): select, assert **`override-form-view`** present (⚑ not `override-form-panel`, §1.4) with the `ready` fixture | `app.test.jsx` | ✅ **RED** — not yet mounted | +1 |
| 4 | **Mount `OverrideFormView`** in the existing `selectedId` block | `App.jsx` | → turns T1 GREEN | 0 |
| 5 | Add **T2** `the override path end-to-end — Confirm POSTs exactly { action: "override", reason }, no underwriter_id` (Q5(a)) | `app.test.jsx` | ✅ **RED** | +1 |
| 6 | Add **T3** `a blank reason cannot be submitted — the affordance stays disabled and NO commit is issued` (Q5(a) / Fold E) | `app.test.jsx` | ✅ **RED** | +1 |
| 7 | Add **T4** `approve then override — the second commit loses the claim and renders commit_conflict` (Q5(b) / Fold A) | `app.test.jsx` | ✅ **RED** | +1 |
| 8 | Q4(a): rewrite **only** `:316`'s comment — state the real reason `:329` and `:344` are each true. **Both assertions byte-unchanged.** | `app.test.jsx` | n/a — comment | 0 |
| 9 | Q1(a): rewrite `seams.js:6-19`'s backing table to Scope-B reality, recording what superseded it | `seams.js` | n/a — comment | 0 |
| 10 | Q2(a): extend the Fold-4 comment two → three R4 reads | `App.jsx` | n/a — comment | 0 |
| 11 | Full suite + coverage; confirm **723 / 147 / 0**, thresholds unchanged | — | n/a | — |
| 12 | **Step 6 manual live verification — USER-RUN** (§4.1) | — | n/a | — |
| 13 | Update `guide-state.md`; append **one** `audit.md` entry | docs | n/a | — |

**Files touched: 3** — `frontend/src/app/App.jsx` (one JSX line + one comment), `frontend/src/app/__tests__/app.test.jsx` (4 tests + 1 comment + 1 harness extension), `frontend/src/app/seams.js` (comment only). Plus the two doc files. **No `vitest.config.js` edit** (Fold D). **No backend file. No WIRE-1. No frozen unit.**

### Named stop-gates — halt and report, do not work around

1. **Any of T1–T4 is GREEN on arrival** (before its implementing step) → the test is vacuous. Stop. ⚑ Highest-risk here is **T1**: if it passes before step 4, the assertion is almost certainly hitting `override-form-panel` semantics or a non-`ready` fixture — the §1.4 trap, third instance.
2. **Any currently-green test goes red.** Expected blast radius is **zero**; `:329` and `:344` must stay green **untouched** (§1.5). If either fails, the §1.5 correction was wrong and the whole Q4 answer needs revisiting.
3. **The five-key `wires all five units seams` assertion changes state.** It must not — override is already registered (§1.1). If it moves, something edited `seams.js`'s exports rather than its comments.
4. **Final count ≠ 723.** Report the corrected number **before** proceeding, with the cause named — never adjust tests to hit the prediction (the 712 → 716 precedent).
5. **Coverage thresholds weakened, or any threshold number edited.** Forbidden.
6. **Any backend file, WIRE-1, `main.jsx`, or any frozen `ui-shell`/view unit appears in `git status`.** Stop immediately.
7. **`seams.js`'s exported `createSeams` body changes.** Q1 authorizes a comment rewrite only.
8. **Step 6.5's `psql` row shows a null, trimmed, or altered `reason`** → stop and report before any doc update or commit.
9. **Step 6.6 leaves the case non-re-committable** (claim not released) → a real defect. Stop; do not document around it.
10. **Any commit.** Not authorized in this pass.

### §4.1 Step 6 — manual end-to-end verification (user-run, unchanged from §3's Q6(a))

The procedure is as specified under Q6 above, run in full: login → select → reason-gate observed in the browser → override commits 200 → **`psql` read-back of `action=override` with the exact non-null `reason`** → blank-reason bypass returns **409** → **claim-release confirmed by a successful re-commit afterwards** → optional double-commit 409 through the UI.

⚑ **This is the pass's actual deliverable.** Steps 1–11 are one JSX line and four tests. Step 6 produces the **first `AuditRecord` row in this project's history carrying `action=override` and a non-null `reason`**, and the **first live-database exercise of BR-COMMIT-GATE's blank-reason rejection** (§1.9).

### Step 6 — manual end-to-end verification (user-run, matching Step 7 / Step 10)

**Preconditions**: local Postgres up with `0003_auth.sql` applied; backend running; `npm run dev`; a case in `drafted` with a drafted recommendation.

1. **Log in** as `demo-underwriter` → app mounts (not the login view).
2. **Select a case** in the queue → memo, approval gate, **and the override form** all render.
3. **Confirm the reason gate in the browser**: with the reason box empty, the "Override recommendation" affordance is **disabled**. Type a reason → it enables.
4. **Commit the override** → expect **200** and the committed confirmation, showing the action and the reason echoed back.
5. ⚑ **`psql` read-back — the load-bearing evidence**:
   ```sql
   SELECT decision_id, underwriter_id, action, reason FROM audit_record ORDER BY ... LIMIT 1;
   ```
   Expect `action=override` and the **exact reason text, non-null**. ⚑ **This row will be the first of its kind in the project's history** — the persisted row, not a projection of it.
6. **Blank-reason rejection, over HTTP, against the live DB for the first time** — bypass the UI gate (the UI cannot send a blank reason by construction, which is the point) with a direct call:
   ```
   POST /recommendations/{id}/commit   body: { "action": "override", "reason": "   " }
   ```
   Expect **409**. ⚑ Then confirm the **claim was released** (`not_wired.py:282`): the case must be back in `drafted` and **immediately re-committable** — verify by committing it successfully afterwards, not by assuming. A 409 that left the case stuck in `committing` would be a real defect and this is the only step that would catch it.
7. **Optional (Q6(c))**: click Approve and Override in sequence → the second returns **409 `commit_conflict`**, rendered as the losing unit's ordinary error state.

**Stop-gate**: if the `psql` row shows a null or trimmed `reason`, or if step 6 leaves the case non-re-committable, **stop and report** — do not proceed to docs or commit.

⚑ **Reason is stored AS-ENTERED, not trimmed.** The seam sends it verbatim (`overrideFetchSeam.js:22-24`), and the gate trims only for the *blank check* (`commit_service.py:106`), passing the original through to `_assemble`. So a reason of `"  needs manual review  "` persists **with its surrounding whitespace**. That is current behaviour, not a defect to fix here — but it should be *observed* at step 5 rather than discovered later.

---

## 5. Holds for this pass

| Hold | Status at the plan gate |
|---|---|
| No backend file touched | ✅ Read-only. R5, the gate, and the enum were read to ground §1.8; nothing opened for edit. |
| WIRE-1 contract text untouched | ✅ Read-only. Override's body shape is *consumed* as already specified, not amended. |
| No frozen `ui-shell` component or view unit edited | ✅ `overrideForm/` is mounted, not modified. `RoleGate` untouched. |
| `main.jsx` (U23-owned) untouched | ✅ Not in scope. |
| No code written this pass | ✅ Files written: **1** — this plan. |
| No commit | ✅ User's call. |
| Register status unchanged | ✅ 26 tracked — 18 open / 4 discharged / 4 narrowed. **#19 is exercised by this pass, not resolved by it.** |

---

## 6. What this pass will and will not deliver

**Will**: a clickable override path against a live backend; the **first `AuditRecord` row in the project's history carrying `action=override` and a non-null `reason`**; the **first live-database exercise of BR-COMMIT-GATE's blank-reason rejection**; and confirmation that the claim-then-release path does not strand a case.

**Will not**: resolve #19 (it exercises the guard, it does not discharge the item) · mount `OutlierView` (#17 unchanged) · change any backend behaviour · alter WIRE-1 · resolve the `trim()` vs `str.strip()` divergence (documented, non-authoritative, resolves server-side as a generic 409 by design) · resolve the R6/R7 admin divergence recorded at `dependencies.py:241-248`.
