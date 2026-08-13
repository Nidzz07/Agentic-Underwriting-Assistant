# Outlier Mount — Lightweight Plan (frontend only)

**Stage**: POST-BUILD → mount pass. **Status**: ⛔ **PLAN GATE — awaiting review before any implementation.**
**Date**: 2026-08-13T15:28:18Z
**Baselines**: backend **1774 / 0 / 45 / 5 / 99.49%** · frontend **812 / 154** (commit `d901aab`)
**Predecessor**: the outlier-wiring pass (backend half), `guide-state.md` §"OUTLIER WIRING (backend half)",
committed `d5c2c41`.

---

## 0. Why this is LIGHTWEIGHT, stated so the choice is reviewable

⚑ **No scoping questions are asked, because the one that mattered was answered a pass ago.** The outlier-wiring
pass closed with **Q4(a) answered in advance and carried forward**:

> *"The mount pass is NOT done. #17's frontend half stays deferred per Q1(a) — `seams.js` still has five keys and
> `OutlierView` is still unmounted. **Q4(a) is answered in advance** and carried forward so the mount pass inherits
> it: add `outlier` as the sixth key and supersede the exact-key assertion at `app.test.jsx:547-550`."*

Three things make this small: **(1)** the unit is **complete and frozen** — `OutlierView.jsx`, three components,
`copy.js`, `fetchSeam.js`, `testids.js` and **ten** test files all shipped in the BUILD phase; **(2)** the backend
half is **built, served and live-verified**; **(3)** the mount itself is roughly **six lines across two files**.

⚠️ **The plan's real content is therefore NOT the mount — it is the four supersessions and the verification.** A
mount that edited only `App.jsx` and `seams.js` would leave four documents asserting an exclusion that no longer
exists.

⛔ **Two figures in the inherited answer are stale and are corrected here**: `seams.js` has **six** keys, not five
(submission landed 2026-08-02), so outlier makes it **seven**, not six; and the assertion has moved from
`app.test.jsx:547-550` to **`:570-571`**. This matches the register #2 backfill's own arithmetic correction —
*"It is SIX now, and SEVEN if the outlier mount lands after this."*

---

## 1. What is already true — measured, not assumed

| | |
|---|---|
| **The unit** | ✅ Complete, unmounted. `frontend/src/outlierView/` — 5 source files + 10 test files. |
| **R4's payload** | ✅ `projections.py:167` emits `outlier` when **`status=="ready"` AND a recommendation exists AND `outlier_canonical` is non-null**; `null` otherwise. Shape: `{outlier_score, is_outlier, flagged_features[{feature,z_score,shap_value,direction}], provenance{corpus_version,seed,outlier_model_version}}`. |
| **Decimal → float** | ✅ **No frontend change needed.** Stored as a Decimal-quantized projection (barrier #5), dequantized on read; JSON does not distinguish the two once serialized, so the wire shape is byte-identical to what the frozen unit was built against. |
| **Seam factory shape** | ✅ `createOutlierFetch(transport)` returns a **bare async function**, exactly like `createQueueFetch` / `createMemoFetch`. No shape surprise, and no per-seam key assertion applies (those exist only for the object-shaped seams). |
| **The "never scored" path** | ✅ Handled on **both** sides already — see §5. |

### ⚑ One prop-name trap, pinned here because it is easy to get wrong

`OutlierView` takes **`fetchSeam`**, not `outlierFetchSeam`:

```js
export function OutlierView({ fetchSeam, applicationId, testid = 'outlier-view' })
```

Its mounted siblings use `memoFetchSeam`, `commitFetchSeam`, `overrideFetchSeam` — **outlier does not follow that
naming**, it follows `QueueView`'s. Passing `outlierFetchSeam={...}` would leave `fetchSeam` undefined and the view
would render its ERROR state rather than failing loudly.

---

## 2. The mount point

**`App.jsx`, inside the existing `selectedId` branch, after `OverrideFormView`** — alongside memo / gate / override,
exactly as the instruction scoped it.

```jsx
<OutlierView fetchSeam={seams.outlier} applicationId={selectedId} />
```

⚑ **Why the selection branch and not top-level**: the view is per-application (`applicationId` is required and it
fetches R4 for that id). Mounting it outside the branch would mean either no id to fetch or a permanently
NOT_AVAILABLE panel above the queue.

⚑ **Why AFTER override**: the panel is advisory context for a decision, and the existing order reads memo →
approve → disagree. Placing outlier last keeps the two write affordances adjacent rather than splitting them.
**Cosmetic, and stated so it is a choice rather than an accident.**

### ⚠️ 2.1 R4 becomes the FOURTH identical request — DISCLOSED, NOT REDESIGNED

`App.jsx:105` already records:

> *"MemoView, ApprovalGateView AND OverrideFormView each issue their OWN GET `/applications/{id}/memo`, so a
> selection now makes THREE identical R4 requests (was two before override was mounted)… Accepted knowingly and
> left visible rather than quietly absorbed."*

`OutlierView` fetches R4 too. **A selection will make FOUR.** Carried forward on the **#15 precedent** exactly as
override was, and **explicitly not redesigned in this pass**: removing the duplication means lifting R4 into the
composition root and prop-injecting four frozen units — a redesign, not a wiring change.

⛔ **The existing comment must be updated from THREE to FOUR.** Leaving it would make the disclosure itself wrong,
which is worse than the duplication it discloses.

---

## 3. The four supersessions

| # | File · location | Current state | Change |
|---|---|---|---|
| **S1** | `seams.js` — `createSeams` | six keys | **Add** `outlier: createOutlierFetch(transport)` + the import |
| **S2** | `seams.js:33-34` — the exclusion comment | *"⚑ **NOT registered**: the outlier seam. That is still a real exclusion (#17 — a wired OutlierView would render permanently empty)…"* | **Supersede in place**, original preserved verbatim. The premise died when the wiring pass made R4 serve real data. |
| **S3** | `app.test.jsx:570-571` — the exact-key set | `['commit','history','memo','override','queue','submission']` | **→ seven**, adding `'outlier'`. ⛔ The one hard edit; the assertion fails until it is made. |
| **S4** | `app.test.jsx:356` — the **test NAME** | *"mounts exactly the backed surfaces — queue + history always; **outlier never**; detail surfaces only on selection"* | ⛔ **Its own gate — see §4.** |

### ⚑ S5 — a comment that must change even though its assertion does NOT

`app.test.jsx:370` reads `expect(screen.queryByTestId('outlier-view')).toBeNull()` in the **no-selection** block,
commented *"outlier: genuinely never mounted (#17), which is what this line still asserts."*

⚑ **The assertion stays GREEN and stays CORRECT** — with nothing selected, outlier does not mount. But its
**reason flips** from *"excluded"* to *"nothing is selected"* — **the identical transition override made on
2026-07-26**, which that file already documents at length. The comment must be rewritten or the file will assert an
exclusion that no longer exists. Same for the unauthenticated loop at `:384`, where `'outlier-view'` stays in the
list for the different reason that **no** application surface mounts there.

⚠️ **Counted as a fifth item deliberately.** The instruction named four; this one is a comment-only change that a
diff reader could mistake for cosmetic, and it is not — it is the difference between a test that documents reality
and one that documents a retired premise.

---

## 4. ⛔ GATE G1 — the `app.test.jsx` RENAME, authorized explicitly

**This is its own sign-off, not folded into the mount**, on this file's own precedent. When override was mounted,
the identical rename was **deliberately left stale for a whole pass** because the authorizing answer covered the
comment only; it was corrected later, *"then renamed once explicitly authorized."* Repeating that discipline.

**FROM**: `mounts exactly the backed surfaces — queue + history always; outlier never; detail surfaces only on selection`
**TO**: `mounts exactly the backed surfaces — queue + history always; detail surfaces only on selection`

⚑ **Removing the clause rather than replacing it.** `"outlier never"` becomes false; `"outlier on selection"` would
be true but redundant, since *"detail surfaces only on selection"* already covers every per-application surface —
and enumerating one of four invites the same staleness again the next time the set changes. **The shorter name is
the one that cannot go stale.**

⛔ **NAME ONLY. Every assertion in the test stays byte-unchanged**, and its subject is unchanged: it still pins
exactly which surfaces mount, in both gate states. This is the **#13 `NOTWIRED-FILENAME-STALE`** shape, handled the
way this project has handled every other instance — superseded in place, old name preserved in a comment with the
reason and the date.

> **AUTHORIZATION**: granted in writing by the user, 2026-08-13: *"Grant the app.test.jsx rename its own explicit
> authorization within this plan — don't fold it in silently, per your own flagged precedent."* Recorded here so the
> rename is attributable to a decision rather than to a diff.

---

## 5. The "never scored" case — already handled, and now the DOMINANT case

**Neither side needs a change.** `deriveOutlierState` is **failure-first**: a rejected fetch returns `ERROR` on a
branch evaluated *before* the null check, so ⛔ **`NOT_AVAILABLE` is structurally unable to mask a genuine error.**
Both null-causes — a `pending` body, and a `ready` body carrying `outlier: null` — render `NOT_AVAILABLE`
(`outlier-state-notavailable`, *"Outlier analysis is not available for this application."*). `projections.py` says
the same from the other side: *"a `ready` view whose case was never scored… is every case seeded before this pass,
and it must keep working."*

### ⚠️ Measured against the live database, 2026-08-13 — this is not an edge case

| | |
|---|---|
| Applications | **13** |
| `evaluated`, never drafted → `outlier: null` | **12** |
| `drafted` with real outlier data | **1** — `APP-1d3cc48d235046b3bb44aab0a3ba68d1` (464 canonical bytes) |
| Recommendations | **1**, `outlier_canonical` non-null |

⛔ **NOT_AVAILABLE is what 12 of 13 selectable cases will render.** Any verification that only clicks the scored
case would be testing the rarest path and calling it the happy path. ⚠️ **Zero rows currently exhibit
`ready` + `outlier: null`**, so that specific sub-branch cannot be exercised against this database without
constructing one — §7 says so rather than implying coverage it does not have.

---

## 6. Predicted delta and stop-gates

**Frontend 812 → ~815 (+3).** Backend **untouched at 1774**.

| Test | Where |
|---|---|
| the seam set is seven keys (S3, superseded in place) | `app.test.jsx` — **0 net**, an edit not an addition |
| ⛔ `selection mounts the outlier view` — the **positive** mount assertion, mirroring override's | `app.test.jsx` **+1** |
| the outlier seam is the real seam, not a placeholder | `app.test.jsx` **+1** |
| a selected case with **no** outlier data renders NOT_AVAILABLE, not an error | `app.test.jsx` **+1** |

⚑ **The third is the non-vacuity partner** of the second: without it, a view mounted but permanently erroring
would satisfy "it mounts". ⚠️ Prediction is soft — this project has missed such counts in both directions, and
**stop-gate 3 applies: report the corrected figure with its cause, never trim a test to hit a number.**

**Stop-gates**: ⛔ no backend file · ⛔ no WIRE-1 file · ⛔ no frozen `outlierView/` source or test edited — **the
whole point is that the unit needs no change; if it does, stop and report** · no coverage threshold edited ·
any assertion green on arrival must be shown to bite or be dropped · **no commit before review.**

---

## 7. Manual verification — USER-RUN, and it must show BOTH states

⚑ **This is the first time outlier data will have been seen ON SCREEN.** Every prior outlier verification in this
project was `psql` and `curl` only — the wiring pass's own step 13 was explicitly API/database-level, and the view
has never rendered against a real backend in its entire existence.

**Prerequisites**: backend on `:8000`, frontend dev server, an `underwriter` login, `corpus/` present.

**Step 1 — ⛔ A REAL SCORE ON SCREEN, THE FIRST TIME EVER.** Select **`APP-1d3cc48d235046b3bb44aab0a3ba68d1`** —
the only case in the database with outlier data, and (worth noting) the same case §9's document-upload walkthrough
created. Confirm the *"Statistical outlier analysis"* panel renders with:
* an **anomaly score** (`outlier-score`) and a **flagged-as-outlier** yes/no (`outlier-isoutlier`);
* **flagged features**, each row carrying its own `z-score` and `SHAP contribution`;
* the advisory note *"Advisory statistical signal for underwriter review."*;
* ⛔ **no verdict language anywhere** — direction labels must read *"Above/Below the typical range"*, never a
  severity word. ⚑ Cross-check the rendered numbers against `curl … /applications/<id>/memo`: **the screen and the
  wire must agree.** That comparison is the whole point — it is what psql-only verification could never do.

**Step 2 — ⛔ NOT_AVAILABLE, THE CASE 12 OF 13 USERS WILL ACTUALLY HIT.** Select **any other** application from
the queue (all 12 are `evaluated`, never drafted). Confirm:
* the panel renders *"Outlier analysis is not available for this application."*
  (`outlier-state-notavailable`);
* ⛔ **it is NOT the error state** — no *"Unable to load the outlier analysis."*, and **no Retry button**. Getting
  this backwards is the single most likely failure of this pass, and it is invisible to anyone who only clicks the
  scored case.

**Step 3 — the panel follows the selection.** Switch from the scored case to an unscored one and back. Confirm the
panel swaps between the two states rather than caching the first. ⚑ `OutlierView` re-fetches via a `useEffect`
keyed on `applicationId`; this is the observation that proves it.

**Step 4 — the error state is reachable and honest.** Stop the backend, reload with a case selected, confirm the
panel shows *"Unable to load the outlier analysis."* **with** a Retry button; restart the backend and click Retry
→ the panel recovers without a page reload. ⛔ **This is what proves NOT_AVAILABLE and ERROR are genuinely
different states** rather than one label serving both.

**Step 5 — the fourth R4 request, observed rather than argued.** With DevTools' network tab open, select a case
and count requests to `/applications/{id}/memo`. ⛔ **Expect FOUR.** §2.1 predicts it in writing; this is where it
is confirmed or corrected.

### ⚠️ What this walkthrough deliberately does NOT claim

* ⛔ **The `ready` + `outlier: null` sub-branch is NOT exercised** — no such row exists (§5). Step 2 covers the
  `pending` null-cause only. Both render NOT_AVAILABLE **by the same code path**, and the unit's own tests cover
  both, but **only one is seen live** and this plan will not pretend otherwise.
* ⚠️ **Nothing here re-verifies the SCORE's correctness.** That was closed by the wiring pass on live evidence
  (determinism across two seeds, identical to twelve decimals). This pass verifies **rendering**, not scoring.

---

## 8. Register — ⛔ #17 CLOSES FULLY

**Decision, on the record and by explicit instruction rather than by implication.**

**#17 `OUTLIER-DATA-EXISTS-CONTRACT-FORBIDS` → CLOSED.** It named two halves and **both are now done**:

1. **The technical/backend half** — closed by the outlier-wiring pass on live evidence: a real score computed,
   persisted (`outlier_canonical`, 464 bytes) and served on the wire, verified against a real local PostgreSQL.
2. **The frontend half** — closed by this pass: `OutlierView` mounted against the real seam and **observed
   rendering that real data on screen** (§7 step 1).

⚑ **Its title was already known to be doubly wrong**, and row **17-C** records it: *"persists real outlier data"*
was false (every row was NULL) and *"the frozen contract forbids sending it"* was false (WIRE-1 explicitly provides
for a Phase-2 `ready` view). ⛔ **The closure is of the ITEM, not an endorsement of its title** — 17-C stands as
the correction and is not deleted.

⚠️ **What closing #17 does NOT close**, so the closure cannot be over-read:
* **Not "the system is in Phase 2."** Only the named **Phase-2-OUT** slice. `ObservabilityService`, Langfuse and
  Prometheus remain untouched; `render.yaml`'s `LANGFUSE_*` stay *"Phase-2 reserved, set-not-consumed."*
* **Not the corpus deployment question** — whether `corpus/` reaches the deployed backend is still the deployment
  pass's, tracked separately.
* **Not #5 `OUTLIER-IN-PROSE`** — a different item about memo prose, untouched here.

**Register 31 → 31 tracked, one moving from open to closed.** ⚑ No new item is opened by this pass.

---

## 9. Files — 2 changed, 0 new

`frontend/src/app/seams.js` (S1, S2) · `frontend/src/app/App.jsx` (the mount + the THREE→FOUR disclosure) ·
`frontend/src/app/__tests__/app.test.jsx` (S3, S4/G1, S5, +3 tests).

⛔ **`frontend/src/outlierView/**` is NOT edited** — not one source file, not one test. If the mount turns out to
require a change inside the unit, **that is a finding and this plan stops**, because it would mean the frozen unit
was built against a contract the backend does not serve.

**HOLDS**: no backend file · no WIRE-1 · no `guide-docs/` beyond this plan until close-out · no migration ·
no coverage threshold · **NO COMMIT** before review.
