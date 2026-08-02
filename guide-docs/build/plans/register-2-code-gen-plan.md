# Register #2 — Execution / Code-Gen Plan (staged)

**Stage**: POST-BUILD → execution plan (Part 1: planning). **No code written yet.**
**Status**: ⛔ **PLAN-FILE GATE — awaiting review before any implementation.**
**Date**: 2026-08-01
**Approved design**: `register-2-submission-path-plan.md` — Q1–Q10 all answered; ambiguity-check **CLEAN** (§4.1)
**Baselines**: backend **1649 / 0 / 44 / 5 / 99.63%** · frontend **723 / 147** (commit `3a08dd8`)

---

## 0. The three gates, and what each one actually edits

⚑ **Stated first because the ambiguity-check found the staging is easy to get wrong** (§4.1 re-check 1).
`test_no_write_route.py` is *read-affected* by gate 2 but *edited* only by gate 3.

| Gate | Sign-off for | Files EDITED |
|---|---|---|
| **G1** | **WIRE1-Fold-6** — the contract amendment | `guide-docs/build/wire-1/api-contract.md` **only** |
| **G2** | the **route-set** widening | `backend/app/tests/_route_inventory.py` (**authoritative**) · `backend/deploy_config/tests/_route_inventory.py` (**mirror**) — ⚑ **both**, or `test_route_inventory_sync.py` fails by design |
| **G3** | the **TRIGGER-1** narrowing | `backend/app/tests/test_no_write_route.py` — **one assertion only** |

⚑ **G2 edits no test file.** `test_routes.py` and `test_no_write_route.py` both *read* `ROUTE_INVENTORY`, so the
new rows propagate automatically. **That is the whole point of the frozen-assertion relaxation** — growth is a
reviewable one-line diff in a named place, and every reading assertion still fails until it is made.

⚑ **R10/R11 are POSTs**, so each needs a `NON_GET_ALLOWLIST` entry **with its stated reason** — the inventory's own
docstring requires it (*"the exceptions are enumerated, never implied"*). Part of **G2**.

---

## 1. Stage 1 — WIRE1-Fold-6 + the two assertion widenings

**Predicted Δ: 0 new tests.** Existing assertions change state; none is added. ⚠️ **Between step 1.4 and step 2.6
the suite is RED by construction** — the inventory declares two routes that do not yet exist. That is expected and
is why **stage 1 is not independently committable** (§5 of the design plan).

| # | Step | File | Gate |
|---|---|---|---|
| 1.1 | Confirm both baselines | — | — |
| 1.2 | **Draft Fold-6**: §3 two rows (R10 `POST /applications`, R11 `POST /applications/{application_id}/draft`) · §5 request/response shapes · §7.3 the fold note · header. ⚑ **§4 NOT amended** (§4.1's scope reduction) · **§2 only if** `201` is chosen over a bare 200 | `api-contract.md` | **G1** ⛔ |
| 1.3 | ⚑ **Verify R1–R9 byte-unchanged row-by-row**, Fold-5's own sign-off ritual | — | **G1** |
| 1.4 | Add R10/R11 to **both** inventories + `NON_GET_ALLOWLIST` with reasons | 2 × `_route_inventory.py` | **G2** ⛔ |
| 1.5 | Confirm `test_route_inventory_sync.py` passes (both copies agree) and `test_routes.py` now fails **for the right reason** (declared-but-unserved) | — | **G2** |
| 1.6 | **Narrow TRIGGER-1**: preserve the current claim verbatim; replace with *"no GET route imports or invokes the pipeline; it is reachable ONLY from R10/R11"*, using the existing `_DOMAIN_WRITE_MODULES` exemption shape | `test_no_write_route.py` | **G3** ⛔ |
| 1.7 | ⚑ **Prove the narrowed guard still bites** — a synthetic GET module referencing `CasePipeline` must still fail it. **Non-vacuity, demonstrated not asserted** (the file's own `test_detector_*` precedent) | `test_no_write_route.py` | **G3** |

### ⚑ Stage 1's real risk

**Not the code — the wording.** A narrowing that is merely *more permissive* rather than *strictly more specific*
would silently retire the only mechanical enforcement of §0.2. Step 1.7 is the guard against that, and it is
**mandatory, not optional**.

---

## 2. Stage 2 — backend routes, intake wiring, rejection

**Predicted Δ: +18 tests** (range given in the design plan was +15…25; this is the concrete estimate).

RED-before-GREEN throughout. ⚑ **Auth tests come FIRST** (2.1–2.2), because Q10 makes authorization part of the
route's definition rather than a later hardening.

| # | Step | Test / change | RED? | Δ |
|---|---|---|---|---|
| 2.1 | **A1** `R10 rejects an auditor with 403` · **A2** `R10 rejects an unauthenticated caller with 401` | `app/tests/` | ✅ | +2 |
| 2.2 | **A3** `R11 rejects an auditor with 403` · **A4** `R11 rejects an unauthenticated caller with 401` | `app/tests/` | ✅ | +2 |
| 2.3 | **B1** `R10 accepts a valid structured application and returns the created application_id` · **B2** `the persisted case is at state=evaluated` · **B3** `R10 accepts an EMPTY documents list explicitly` (Q2's follow-up) | `app/tests/` | ✅ | +3 |
| 2.4 | **C1** `a rejected intake returns 400 invalid_request` · **C2** `the error detail carries field_errors / missing_items / reason_category` · **C3** `a rejected intake creates NO row` | `app/tests/` | ✅ | +3 |
| 2.5 | ⚑ **C4** `the 403 path never reaches intake` — a spy intake seam records **zero** calls (proves the Depends-before-body ordering structurally, not by timing) | `app/tests/` | ✅ | +1 |
| 2.6 | **Implement R10** — handler + `require_underwriter` + intake call + `submit()`; DI in `dependencies.py` | `app/routes/`, `dependencies.py` | → greens A1–C4 | 0 |
| 2.7 | **D1** `R11 drafts a pending case and it becomes ready` · **D2** `R11 on an already-drafted case returns the skip outcome, not a failure` (⚑ inherits #27's `DraftOutcome.skipped`) · **D3** `R11 on an unknown application is 404` | `app/tests/` | ✅ | +3 |
| 2.8 | **Implement R11** — handler + `require_underwriter` + `draft()` | `app/routes/` | → greens D1–D3 | 0 |
| 2.9 | **E1** `R4 is still side-effect-free — a GET triggers no pipeline call` (a spy, re-pinning the invariant **behaviourally** now that the structural guard is narrower) · **E2** `the full journey: R10 → R4 pending → R11 → R4 ready` | `app/tests/` | ✅ | +2 |
| 2.10 | **F1** `test_routes.py passes again` — the declared surface now equals the served surface · **F2** `the route inventory sync still holds` | — | → green | +2 |
| 2.11 | Full backend suite; confirm the predicted total | — | — | — |

**Predicted after stage 2: 1649 + 18 = 1667 passed**, skips/errors unchanged at 44/5.

### ⚑ Stage 2's two design constraints, carried from the check

* **Auth resolves before intake** (FastAPI `Depends`) — **E1/C4 pin it**, so it cannot regress into
  "validate first, authorize later", which would leak rejection detail to an unauthorized caller.
* **`RejectedIntake` never enters the pipeline** (Q8(a)) — C3 pins "no row created", the property that keeps
  `submit()`'s contract intact and avoids a half-created case.

---

## 3. Stage 3 — outlier-model composition

**Predicted Δ: +6.** ⚑ **Could be sequenced BEFORE stage 2** — it has no dependency on the routes existing, and
doing so de-risks the corpus/deployment question first (§5 of the design plan).

| # | Step | Δ |
|---|---|---|
| 3.1 | **G1** `the fitted model is cached — two calls return the SAME instance` (pins `lru_cache`, the property that keeps the fit off the per-request path) | +1 |
| 3.2 | **G2** `create_app() does NOT fit the model` — ⚑ **pins the LAZINESS**, which §4.1 Fold C found is load-bearing: an eager fit would cost ~2.6 s × every `create_app()` | +1 |
| 3.3 | **G3** `a missing corpus fails loudly and by name` (the seed script's `build_outlier_model` precedent) | +1 |
| 3.4 | Implement the fourth `lru_cache` provider in `dependencies.py`, reusing `build_outlier_model` | 0 |
| 3.5 | **G4** `a drafted case persists a real quantized OutlierResult` · **G5** `R4 serves it` · **G6** `a case drafted with no model still emits outlier: null` | +3 |
| 3.6 | Wire the model into R11's seams | 0 |

⚑ **Record `corpus/` as a declared runtime dependency here** — per Q4's forced follow-up, this is where the
carried-forward deployment question stops being carried.

### ⛔ CORPUS ON RENDER — ANSWERED AND CLOSED (2026-08-02, stage 3 as executed)

**The question**, carried since the outlier pass (its plan §7 item 2) and quoted verbatim from
`seed_demo_cases.py` as it stood: *"OPEN, and deliberately not answered here: whether `corpus/` ships to the
DEPLOYED backend. `render.yaml` neither places nor verifies it, and seeding is not part of deployment at all —
so nothing today depends on the answer."*

⚑ **R11 is what makes that reasoning obsolete.** Outlier scoring is now on an HTTP path any authenticated
underwriter can reach, so the corpus is no longer a seed-script convenience. **Answer, per Q4(a): YES, `corpus/`
ships to the deployed backend, as a HARD RUNTIME DEPENDENCY.**

| | |
|---|---|
| **What must be present** | `corpus/profiles.json` **and** `corpus/manifest.json` on the deployed backend |
| **What happens if absent** | `build_outlier_model` raises `FileNotFoundError` naming the exact path. **There is no `outlier=null` fallback** — Q6(b) was considered and refused, because a silent null is indistinguishable from legitimate Phase-1 behaviour. R11 fails loudly; R10, login and the read routes are unaffected (the fit is lazy). |
| **Where it is declared in CODE** | `backend/app/outlier_composition.py::CORPUS_ON_RENDER` — a named, greppable constant, **not a comment**. Asserted by `test_the_deployment_dependency_is_declared_in_code_not_only_in_prose`, so it cannot be deleted silently. |
| **What this pass did NOT do** | ⛔ **`render.yaml` is UNTOUCHED.** Placing and verifying the corpus is the **deployment pass's** work; doing it here would be deployment work smuggled into a wiring pass. |

⛔ **ACTION REQUIRED OF THE DEPLOYMENT PASS** — stated here so it is not inherited as a vague note a third time:
**place `corpus/` on Render and verify it at deploy time.** A deploy that omits it produces a backend where
submission works, drafting 500s, and nothing says why until someone reads the logs.

---

## 4. Stage 4 — the frontend `submission/` unit

**Predicted Δ: +32 frontend** (design-plan range +25…40).

Mirrors the six existing units exactly: `SubmissionView.jsx` · `components/` · `copy.js` · `fetchSeam.js` ·
`testids.js` · `__tests__/`. Scoped at the level the outlier and override passes' plans used.

| # | Step | Δ |
|---|---|---|
| 4.1 | Seam + transport tests (submit; draft-trigger) | +6 |
| 4.2 | Form rendering, field validation, disabled-until-valid affordance | +8 |
| 4.3 | ⚑ **The 400 rejection path** — per-field errors rendered from `detail.field_errors`. **The reason Q8(a) was worth choosing** | +6 |
| 4.4 | Success → the case appears in the queue as `pending`; the draft-trigger action on a pending case | +6 |
| 4.5 | Role-invariance, error, empty and loading states (the units' established completeness bar) | +4 |
| 4.6 | Mount in `App.jsx` behind the login gate; register the **seventh** `seams.js` key | 0 |
| 4.7 | ⛔ **Supersede `app.test.jsx`'s exact-key assertion to the seven-key set**, recording the old set and why | +2 |

⚠️ **The double-supersession, restated**: the deferred outlier mount pass will supersede **this same assertion**
(its Q4(a), already answered). **Whichever lands second inherits a seven-key set, not six** — and if outlier lands
after this, it goes to **eight**.

---

## 5. Named stop-gates

1. **Any test green on arrival** → vacuous; demonstrate RED by inverting the implementing change, or stop.
2. ⛔ **Any WIRE-1 row R1–R9 differing byte-for-byte** at step 1.3. Fold-6 is **additive or it is nothing**.
3. ⛔ **The narrowed TRIGGER-1 guard failing to bite** at step 1.7 → the narrowing is permissive, not specific. Stop.
4. **The two `_route_inventory.py` copies diverging** → `test_route_inventory_sync.py` fails. Fix both, never one.
5. **Counts ≠ prediction** → report the corrected figure **with its cause**; never trim tests to hit a number.
6. ⛔ **`CasePipeline` appearing in any module other than R10/R11's** → the exemption is being widened by drift.
7. ⛔ **Any frozen unit in `git status`** — `intake/`, `case_lifecycle/`, `deploy_config/` **production** files.
   ⚑ Under Q7(a) **none is expected**; `deploy_config/tests/_route_inventory.py` is the sole exception and is G2's.
8. **Any GET route gaining a write path** → R4's side-effect-freedom is the invariant this pass narrows the *guard*
   for, not the *property*.
9. **Frontend ≠ 723** before stage 4, or coverage threshold edited at any point.
10. **Any commit before its stage's gate.**

---

## 6. Manual verification — USER-RUN (after stage 4)

> ⛔ **CORRECTED 2026-08-02, AFTER ALL FOUR STAGES SHIPPED.** The original eight steps are preserved
> verbatim immediately below. **Two of them could not be performed as written** — they described a
> UI that the disabled-until-valid affordance and the auditor's own 403 make unreachable — and two
> more omitted behaviour that only exists because of how stage 3 and stage 4 were built. Superseded
> rather than rewritten, because *why* a verification step was wrong is worth more than the step.
>
> **The original, verbatim:**
>
> > 1. Reset the pending tables (⛔ **never drop** — `CREATE ROLE` + the audit evidence).
> > 2. **Log in as an underwriter**, submit an application **through the UI**.
> > 3. `psql`: a `pending_application` row at `state=evaluated`, ⚑ **with a profile that came through intake** — not a fixture. **The first application this system did not invent.**
> > 4. R4 shows `status: pending`; the queue lists it.
> > 5. **Trigger drafting** from the UI → `status: ready`, memo present, ⚑ **a real quantized `OutlierResult`**.
> > 6. **Commit** through the existing approval gate → an `AuditRecord` whose lineage traces to a **user-submitted** application.
> > 7. **Rejection**: submit a deliberately invalid application → **400**, per-field errors rendered, **no row created**.
> > 8. **Authorization**: repeat 2 and 5 as an **auditor** → **403** both times, and ⚑ **no case created and no draft attempted**.
>
> **What changed, and why:**
>
> | # | Correction | Why the original was wrong |
> |---|---|---|
> | **7** | Use a **semantically invalid** value, not an empty field | Step 4.2 shipped a **disabled-until-valid** affordance: an application with a missing field **cannot be submitted through the UI at all**, so "deliberately invalid" had no reachable meaning. |
> | **8** | Split — submit-as-auditor stays in the UI; **draft-as-auditor becomes `curl`** | An auditor's submit 403s, so they never reach the accepted panel, so **the UI path to R11 does not exist for them**. The original asked for something unperformable. |
> | **5** | Two notes added (trigger availability; the ~2.6 s first fit) | Neither behaviour existed when §6 was drafted. |
> | **4** | The no-reload check made explicit; the stale-recommendation limit stated | `queueEpoch` (step 4.6) did not exist when §6 was drafted. |
> | **0** | Prerequisites added | §6 assumed a seeded environment it never described. |

### ⚑ Step 0 — PREREQUISITES (added; §6 previously assumed these silently)

* **Two credentials must exist**: one `underwriter` and one `auditor` in `app_user` + `user_credential`.
  Step 8 is unperformable without the second, and nothing earlier fails to warn you.
* ⛔ **`corpus/profiles.json` AND `corpus/manifest.json` must be present.** Step 5 fits the outlier
  model from them on first use; if either is absent, drafting raises `FileNotFoundError` **by
  design** — there is no `outlier=null` fallback (Q6(b), refused). See
  `backend/app/outlier_composition.py::CORPUS_ON_RENDER`.
* The backend must be running with the rulebook reachable at `backend/rules_engine/rulebook`.

### The corrected steps

1. Reset the pending tables (⛔ **never drop** — `CREATE ROLE` + the audit evidence). **Unchanged.**

2. **Log in as an underwriter**, submit an application **through the UI**. **Unchanged.**
   ⚑ Money fields are free text on purpose: intake's **BR-TYP-1** refuses a JSON float, so enter
   whole digits (`1200000`), never `1200000.50`.

3. `psql`: a `pending_application` row at `state=evaluated`, ⚑ **with a profile that came through
   intake** — not a fixture. **The first application this system did not invent.** **Unchanged.**

4. R4 shows `status: pending`; **the queue lists it — with NO manual reload.** ⚑ **Check the
   no-reload part deliberately.** It works only because step 4.6 bumps a `queueEpoch` key that
   remounts `QueueView`; if that regressed, the symptom is *"nothing happened"* and the natural
   reaction is to reload, which would hide the failure.
   ⚠️ **Honest limit, so it is not read as a bug**: `queueEpoch` bumps on **submit**, not on
   **draft**. After step 5 the queue row still shows an empty recommendation column until the next
   submission or a manual reload. Selecting the row works correctly regardless — `MemoView` issues
   its own R4 and sees `ready` — so step 6 is unaffected.

5. **Trigger drafting** from the UI (*"Start assessment"* in the accepted panel) → `status: ready`,
   memo present, ⚑ **a real quantized `OutlierResult`**.
   * ⚠️ **The first click is ~2.6 s slower than later ones.** That is the lazy `lru_cache` fitting
     the corpus once per process (Q4(a)). **Expected, not a hang** — and the laziness is what keeps
     that cost off `create_app()` entirely.
   * ⛔ **DRAFTING IS ONLY TRIGGERABLE IMMEDIATELY AFTER SUBMITTING, and this is a REAL GAP —
     named here, not discovered later.** The trigger lives in the submission view's accepted panel.
     Once you click *"Submit another application"* or reload the page, **a pending case has no UI
     draft affordance anywhere**: the queue offers selection, memo, approve and override, but no
     trigger. Seed-created `DEMO-*` cases therefore cannot be drafted from the UI at all.
     ⚑ **This is a gap in the clickable path, not a defect in what shipped** — R11 is complete and
     correct, and Q11-A's gap (ii) is closed for the submit→draft→commit journey this pass exists
     to demonstrate. **Closing it means a draft affordance on a pending queue row, which is a
     future pass.**

6. **Commit** through the existing approval gate → an `AuditRecord` whose lineage traces to a
   **user-submitted** application. **Unchanged.** ⚑ Select the row in the queue first; the memo,
   approve and override surfaces appear on selection.

7. ⛔ **Rejection — REWRITTEN.** Submit an application that is **semantically invalid**, not empty:
   the disabled-until-valid affordance makes an empty field unsubmittable, so the original wording
   described something the UI forbids.

   | Enter this | Intake refuses with |
   |---|---|
   | `Requested cover amount` = `0` | *"requested cover must be > 0"* → `malformed` |
   | `Verifiable annual income` = `abc` | *"non-numeric value"* → `malformed` |
   | `Date of birth` **after** `Assessment date` | *"date_of_birth must be <= as_of_date"* → `malformed` |

   Expect: **400**, the per-field message rendered **beside the offending input**, the other fields
   **unmarked**, every typed value **still present**, submit **re-enabled**, and ⛔ **no row created**
   (confirm in `psql`).

   * ⚑ **`missing_required` / `missing_items` is UNREACHABLE THROUGH THE UI** — the client gate
     intercepts every empty field first, so only `malformed` can be produced by a human. That path
     is covered by tests, and by the optional sub-step below. Recorded because a verifier who
     never sees the `missing_items` list should know it was not skipped.
   * **7b (OPTIONAL, `curl`-only — for completeness):** omit a field entirely to reach the other
     reason category and see the missing-items half of the rejection body:
     ```
     curl -i -X POST http://localhost:8000/applications \
       -H 'Content-Type: application/json' \
       -H 'Cookie: session=<UNDERWRITER SESSION>' \
       -d '{"form_fields":{"full_name":"Ada Byron"},"documents":[]}'
     ```
     Expect **400** with `detail.reason_category = "missing_required"` and `detail.missing_items`
     naming the absent fields.

8. ⛔ **Authorization — SPLIT.** The original asked to *"repeat 2 and 5 as an auditor"*; **step 5 is
   unperformable for an auditor**, because their submit 403s and they therefore never reach the
   accepted panel that holds the trigger.

   * **8a — R10 as an auditor, THROUGH THE UI.** Log in as the auditor. ⚑ **The submission form is
     visible to them, deliberately** — the unit reads no Role and composes no `RoleGate`
     (RoleInvariant); the **server** is the real gate. Fill it and submit → a rendered **403**, and
     ⛔ **no row created** (confirm in `psql`).
   * **8b — R11 as an auditor, BY `curl`** (the UI cannot reach it):
     ```
     curl -i -X POST http://localhost:8000/applications/<APP-ID>/draft \
       -H 'Cookie: session=<AUDITOR SESSION>'
     ```
     Use the `APP-ID` from step 2. Expect **403** `forbidden`, and ⛔ **no draft attempted** — the
     case stays at whatever state step 5 left it in (confirm in `psql`).
   * ⚑ Together these are what keeps the **auditor read-only under SEC-4** with a spend-capable
     trigger now on the wire.

---

## 7. Holds

⛔ No frozen unit edited (G2's `deploy_config/tests/_route_inventory.py` excepted, by its own gate) · WIRE-1 amended
**only** under G1 · no migration · no commit before each stage's gate · frontend untouched until stage 4.

---

## 8. What this delivers, and what it does not

**Delivers**: Q11-A's gaps **(i)** an ingestion route and **(ii)** a clickable UI · the first-ever exercise of U1
`intake` · a submission-to-committed-decision journey the system did not seed itself.

**Does not**: discharge **#18** — memo prose stays synthetic under Q5(a), and #2's residual must say so precisely ·
deliver PDF upload (Q2(a)'s named follow-on) · close **#29** · mount the outlier view · address **#26**.
