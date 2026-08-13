# Document Upload — Execution / Code-Gen Plan (six stages)

**Stage**: POST-BUILD → execution plan. **Part 1 (planning) written 2026-08-02. Part 2 (generation) EXECUTED
2026-08-03.**
**Status**: ✅ **ALL SIX STAGES EXECUTED · BOTH SUITES GREEN · §9 MANUAL VERIFICATION COMPLETE (ALL 12 STEPS, REAL
POSTGRES) · BOTH FOLLOW-UP FIXES CLOSED · ⛔ READY FOR COMMIT DECISION · NOTHING COMMITTED.**
Superseded status lines, preserved in order:
*"⛔ PLAN-FILE GATE — awaiting review before any implementation."* →
*"⚠️ ALL SIX STAGES EXECUTED · BOTH SUITES GREEN · MANUAL VERIFICATION NOT RUN · NOTHING COMMITTED."*
**Date**: 2026-08-02 (plan) · **2026-08-03** (execution) · status header corrected 2026-08-07T09:05:21Z ·
**status header + §9 + §12.4 + §12.6 corrected 2026-08-13T14:05:13Z**
**Approved design**: `document-upload-plan.md` — Q1–Q14 all answered; ambiguity-check **CLEAN** (§4.2) with
**four recorded constraints**
**Baselines**: backend **1691 / 0 / 44 / 5 / 99.64%** · frontend **778 / 152** (commit `d43b661`)

---

## ✅ STATUS AS MEASURED 2026-08-13 — supersedes the 2026-08-07 block below

⛔ **Four things changed after 2026-08-07, and the 2026-08-07 block is PRESERVED BELOW UNALTERED** rather than
edited in place, on this project's supersede-not-rewrite discipline: what a document *claimed* at a given date is
part of the record.

| | |
|---|---|
| **Backend suite** | ✅ **1774 passed / 0 failed / 45 skipped / 5 errors / 99.49%** (was 1771 / 99.45%). The 5 errors are the unmoved pre-existing `audit_store` real-Postgres collection errors. |
| **Frontend suite** | ✅ **808 passed / 154 files** — unmoved; both fixes are backend-only. |
| **⛔ §12.4's SHORTFALL** | ✅ **CLOSED 2026-08-09.** Q8(c) is implemented — `intake_telemetry.py` is new, `dependencies.py:354` passes it, **J8 and J9 exist.** See §12.4's correction note. |
| **⛔ §12.6's uncovered branch** | ✅ **CLOSED 2026-08-09.** `routes/submission.py` is now **100%** (63/63 statements, 12/12 branches). See §12.6's correction note. |
| **⛔ §9 manual verification** | ✅ **COMPLETE — ALL 12 STEPS**, user-run against a real local PostgreSQL, 2026-08-10 → 2026-08-13. ⛔ **`DOCS-COMPLETE-1` PASSES** and ⛔ **`incomplete=false`** — both firsts in this project's history. Optional step 13 not run. Full results: `audit.md` 2026-08-13T14:05:13Z; narrative: `guide-state.md`. |
| **`guide-state.md`** | ✅ **BACKFILLED 2026-08-13**, with the live evidence, as the deferral intended. |
| **Commit** | ⛔ **STILL NONE.** HEAD is `d43b661`. Commit grouping presented; awaiting explicit approval. |
| **⚠️ Still unrecoverable** | The six-stage execution's internal **RED/GREEN sequence and stop-gate history**. Unchanged — the outcome is now verified, the process history is not recovered. |

⚑ **One stray file removed**: `uw.txt`, an untracked and un-gitignored `curl` cookie jar left by the walkthrough
carrying a **live session token**. Deleted 2026-08-13 before any commit could sweep it in.

---

## ⚠️ STATUS AS MEASURED 2026-08-07 — stated plainly, WITHOUT execution narrative — **SUPERSEDED, see above**

⛔ **This block records only what is verifiable from the working tree and from re-running both suites today.**
The execution itself (2026-08-03, mtimes 00:36–01:46) produced **no `audit.md` entry and no `guide-state.md`
entry**, so **what happened during it — which tests went RED first, which stop-gates fired, whether stage 4's
`python-multipart`-vs-hand-rolled decision was taken at its gate — is NOT RECOVERABLE and is deliberately not
narrated here.** Nothing below is inferred about process; every figure is measured.

| | |
|---|---|
| **Code** | ✅ **All six stages present.** Fold-7 in `api-contract.md`; `upload_storage.py`, `parse_concurrency.py`, `multipart_reader.py` new; `submission.py`/`dependencies.py`/`main.py`/`errors.py` amended; `DocumentInputs.jsx`, `OptionalFields.jsx` new. **17 modified + 14 new files.** |
| **Backend suite** | ✅ **1771 passed / 0 failed / 45 skipped / 5 errors / 99.45%.** The 5 errors are the pre-existing `audit_store` real-Postgres collection errors, unmoved. |
| **Frontend suite** | ✅ **808 passed / 154 files.** |
| **Prediction variance** | ⚠️ **RECONCILED 2026-08-07 — see §12.** Backend **+81 collected vs +48 predicted**; frontend **+30 vs +34**. ⛔ **One genuine SHORTFALL found by the reconciliation: J8/J9 do not exist and Q8(c) is NOT implemented** (§12.4). |
| **G3** | ✅ **Confirmed EMPTY**, exactly as §0 predicted. `deploy_config/tests/_route_inventory.py` untouched. |
| **Stop-gate 9** | ✅ **No frozen unit touched** — nothing under `intake/`, `rules_engine/`, `case_lifecycle/`, `common/`. |
| **Coverage thresholds** | ✅ **Unedited** on both sides — `pyproject.toml` is not in `git status`. |
| **§9 manual verification** | ⛔ **NOT RUN.** Written 2026-08-07; user-run. |
| **Commit** | ⛔ **NONE.** HEAD is still `d43b661`. |
| **`guide-state.md` / `audit.md`** | ⛔ **NEITHER records this pass.** Backfill **deliberately deferred until after §9 runs**, so one entry can carry live evidence rather than a reconstruction that would then need superseding. |

---

## 0. The three gates, and what each one actually edits

⚑ **Stated first, following register #2's precedent** — that pass's ambiguity-check found the staging easy to get
wrong, and stating it up front is what stopped it being got wrong.

| Gate | Sign-off for | Files EDITED |
|---|---|---|
| **G1** | **WIRE1-Fold-7** — the contract amendment (§1 · §2 · §3-note · §4 · §5 · §7.4) | `guide-docs/build/wire-1/api-contract.md` **only** |
| **G2** | the **filesystem guard** — `_FILESYSTEM_WRITE_MODULES`, **created before the module it guards exists** | `backend/app/tests/test_no_write_route.py` |
| **G3** | the **route-set** touch, **if any** | ⚑ **Possibly EMPTY — see below** |

⛔ **G3 may edit nothing at all, and that is a finding, not an oversight.** Q1(a) amends R10's **request media
type**; it adds **no route**. `ROUTE_INVENTORY` records `(path, method)` — `("/applications", "post")` is already
there. `NON_GET_ALLOWLIST` already lists it. `ROUTE_MODULE_INVENTORY` already lists `submission.py`. **So no
inventory changes** unless a new module lands under `backend/app/routes/`, which this design does not require.
**G3 is therefore reserved, not scheduled** — if execution shows it empty, it is dropped and the fact recorded.

⚑ **G2 is the inverse of register #2's G3.** There, a guard existed and was narrowed. Here, **a guard is
created** — and per Q14(a) it is created **before** the module it constrains, so the writing module's first
encounter with it is a failure. That ordering is the whole point and is why G2 precedes stage 4.

---

## 1. Stage 1 — WIRE1-Fold-7 + the filesystem guard

**Predicted Δ: +3.** ⚑ **This stage is GREEN throughout** — unlike register #2's stage 1, nothing here declares a
surface that does not yet exist, so there is no RED-by-construction window. **It is independently committable.**

| # | Step | File | Gate |
|---|---|---|---|
| 1.1 | Confirm both baselines | — | — |
| 1.2 | **Draft Fold-7**: **§1** a `DocType` row (the first **client-authored** enum) · **§2** a `multipart/form-data` request convention, worded **"JSON *or* multipart" for R10** (Constraint 4) · **§3** the note block only — the R10 **row** is unchanged · **§4** a **413** row · **§5** the request shape + superseding *"MUST be `[]` under this fold"* · **§7.4** the fold record, **including the stated retention guarantee** (Q5) | `api-contract.md` | **G1** ⛔ |
| 1.3 | ⚑ **Verify R1–R11 byte-unchanged row-by-row** — Fold-5's and Fold-6's sign-off ritual, hash captured **before** editing | — | **G1** |
| 1.4 | **Create `_FILESYSTEM_WRITE_MODULES`** as an exact set, currently **empty**, plus the scan asserting no module under `backend/app/` calls `open(`/`write_bytes`/`write_text`/`mkdir`/`tempfile`/`shutil` outside it | `test_no_write_route.py` | **G2** ⛔ |
| 1.5 | ⚑ **Prove the guard bites BEFORE anything writes** — a synthetic module writing a file must fail it, demonstrated on the real tree **and** pinned by a committed detector test | `test_no_write_route.py` | **G2** |
| 1.6 | Confirm G3 is empty — all three inventory tuples already cover R10 | — | **G3** |

### ⚑ Stage 1's real risk

**The guard's scope, not the contract.** A guard that names only `open(` misses `Path.write_bytes`, `shutil.copy`
and `tempfile.NamedTemporaryFile`. **Step 1.5 is the guard against that**, and — exactly as register #2's step 1.7
was — it is **mandatory, not optional**. The detector must be fed **each** forbidden construct separately, not one
representative.

---

## 2. Stage 2 — the temp-file lifecycle + the startup sweep. **No route. No multipart.**

**Predicted Δ: +12.** ⚑ **Testable with no HTTP at all**, which is why Q12(a) gave it its own stage: a retention
bug is invisible to a green suite, and isolating it is the only way to review it honestly.

| # | Step | Test / change | RED? | Δ |
|---|---|---|---|---|
| 2.1 | **A1** `a temp dir is created under the app-owned root, not the system default` · **A2** `it is removed on the success path` · **A3** `it is removed when the body raises` | `app/tests/` | ✅ | +3 |
| 2.2 | ⚑ **A4** `the file is written with owner-only permissions` · **A5** `the path is never echoed into any WireError detail` (it names a real applicant's document) | `app/tests/` | ✅ | +2 |
| 2.3 | **B1** `the sweep removes an orphan older than the threshold` · **B2** `it leaves a FRESH directory alone` — ⛔ **the load-bearing half: a sweep that deleted live temp dirs would break concurrent requests** · **B3** `it tolerates a missing root` | `app/tests/` | ✅ | +3 |
| 2.4 | ⛔ **B4** `a sweep that RAISES does not prevent startup` (Fold B's constraint — fail-open, log, never fail-closed) | `app/tests/` | ✅ | +1 |
| 2.5 | Implement the temp-dir helper + the sweep, wired as a **`lifespan` hook** — ⛔ **never in `create_app()`'s body** | `app/`, `main.py` | → greens A1–B4 | 0 |
| 2.6 | ⛔ **Add the writing module to `_FILESYSTEM_WRITE_MODULES`** — the exact-set guard from stage 1 fails until this is a deliberate one-line edit | `test_no_write_route.py` | → green | 0 |
| 2.7 | **C1** `create_app() still fits no model` (register #2's laziness guard, re-run) · **C2** `create_app() itself sweeps nothing — only lifespan does` | `app/tests/` | ✅ | +2 |
| 2.8 | ⚑ **C3** `the app-owned root is NOT the system temp default` — so the sweep can never delete another process's files | `app/tests/` | ✅ | +1 |

### ⚑ Stage 2's two constraints, carried from the check

* **The sweep is a `lifespan` hook and must be failure-tolerant.** It runs in **every** `conftest` fixture (each
  enters `with TestClient(app)`), so it must also be cheap — a `listdir`, not a walk.
* **Step 2.6 is where the stage-1 guard first bites.** If it does **not** fail before that edit, the guard is
  vacuous and **stop-gate 3 applies**.

---

## 3. Stage 3 — concurrency bounding. **Still no route.**

**Predicted Δ: +6.** ⚑ Independently testable and independently revertable. A capacity bug is the other thing
invisible to a green suite.

| # | Step | Δ |
|---|---|---|
| 3.1 | **D1** `the bound is a NAMED CONSTANT, not a literal` · **D2** `concurrent callers beyond the bound WAIT rather than proceed` (asserted by observed overlap, not by timing) | +2 |
| 3.2 | ⛔ **D3** `it is an asyncio.Semaphore, acquired in the async caller` (Constraint 2) — a threading primitive here would block the event loop, and **that failure is invisible in a single-request test** | +1 |
| 3.3 | ⛔ **D4** `the blocking work runs in a threadpool, NOT on the event loop` (Constraint 1) — pinned by asserting the worker thread differs from the loop thread | +1 |
| 3.4 | Implement the bounded-offload helper | 0 |
| 3.5 | **D5** `the semaphore is RELEASED when the wrapped work raises` — ⚑ a leaked permit degrades to a permanent hang, the worst failure shape here · **D6** `a released permit is reusable` | +2 |

⚠️ **D2 must not be a sleep-based timing test.** Assert *overlap* (two entries before either exit) via recorded
enter/exit events — a timing assertion would be flaky and would not say **why** it failed.

---

## 4. Stage 4 — the multipart reader. ⛔ **The hard one. Its own stage, per Q13(b).**

**Predicted Δ: +18.** Hand-rolled stream consumption is *"genuinely hard to get right"* — the answer said so, and
this stage is that acknowledgement made structural.

| # | Step | Test / change | Δ |
|---|---|---|---|
| 4.1 | ⛔ **E1** `a 403 reads ZERO bytes of the stream` — **the property Fold A found degraded and Q13(b) exists to restore.** Assert the recorded read-count is 0, not merely that intake was not called | +1 |
| 4.2 | **E2** `a well-formed 3-part upload yields 3 temp files` · **E3** `each part's declared doc_type maps to a DocType member` · **E4** `an unknown doc_type is a 400` | +3 |
| 4.3 | ⛔ **The adversarial set, named in Q13's answer**: **F1** malformed boundary · **F2** truncated stream · **F3** a part with no `filename` · **F4** ⚑ **a `Content-Length` that LIES (understates the real body)** — the streaming counter must still 413 · **F5** zero parts · **F6** a part that is empty | +6 |
| 4.4 | **G1** `a file over the per-file cap is 413` · **G2** `a fourth document is 400` (Q6: the cap is `len(DocType)`) · **G3** ⚑ `two parts of the SAME doc_type is 400, never last-wins` | +3 |
| 4.5 | ⛔ **G4** `the cap fires BEFORE the bytes are on disk` — assert the temp dir holds less than the cap at the moment of refusal. **This is Q6's central promise and the only test that can falsify it** | +1 |
| 4.6 | Implement the streaming reader + the `Content-Length` fast-reject middleware | 0 |
| 4.7 | ⚑ **H1** `the middleware is an OPTIMIZATION, not the control` — with the middleware removed, F4 still passes | +1 |
| 4.8 | **H2** `the JSON path is byte-unchanged` (Constraint 4) · **H3** `Content-Type routing picks the right path` · **H4** `a malformed JSON body still yields the same 400 envelope` (Constraint 3) | +3 |

### ⛔ Stage 4's real risk

**A parser that is permissive where it should refuse.** Every F-test is a case where the safe answer is *reject*,
and a hand-rolled parser's natural failure is to accept something malformed and carry on. ⚠️ **Consider
`python-multipart`'s own streaming API rather than parsing bytes by hand** — it is already a declared dependency,
it is what starlette itself uses, and using it at the streaming level keeps the byte-cap control while not
re-implementing boundary handling. **Decide this at the stage-4 gate, with the trade stated.**

---

## 5. Stage 5 — wire it into R10, end to end

**Predicted Δ: +9.**

| # | Step | Δ |
|---|---|---|
| 5.1 | **J1** `R10 with 3 real PDFs persists a case whose manifest has 3 PARSED entries` · **J2** ⛔ **`documents_missing_count == 0`, so DOCS-COMPLETE-1 PASSES** — **the pass's whole point** | +2 |
| 5.2 | **J3** `an unparseable PDF yields status=unparseable, NOT a 500` · **J4** `and the case still persists` — a bad document is a REFER, never a crash | +2 |
| 5.3 | ⚑ **J5** `the temp dir is gone after the request, on BOTH the success and the unparseable path` | +1 |
| 5.4 | **J6** `the semaphore is actually acquired on the R10 path` (stage 3's bound, wired) | +1 |
| 5.5 | ⛔ **J7** `incomplete is STILL true with 3 parsed documents and no optional fields` — **§0.2's finding, pinned so nobody later reads document-completeness as completeness** | +1 |
| 5.6 | **J8** `neutralization_count reaches telemetry when a document carries an injection pattern` (Q8(c)) · **J9** `no verbatim span and no PII leaves the sanitizer` | +2 |
| 5.7 | Wire R10's multipart branch to intake with real documents | 0 |

---

## 6. Stage 6 — the frontend, and the optional fields

**Predicted Δ: +34 frontend.**

| # | Step | Δ |
|---|---|---|
| 6.1 | ⛔ **`httpTransport.js`: detect `FormData`, pass it through, set NO Content-Type** · a test that the **JSON path is byte-unchanged** (it is shared by all six seams) | +4 |
| 6.2 | The seam gains a documents argument; `buildSubmitRequest` emits `FormData` when documents are present, JSON when not | +5 |
| 6.3 | File inputs per `DocType`, with per-document state — **selected / uploading / parsed / unparseable** — ⛔ **visible, never silently downgraded** (Q7) | +8 |
| 6.4 | ⛔ **The 413 and per-document error paths** rendered distinctly from the 400 rejection path | +5 |
| 6.5 | **The six optional fields** (Q10) — ⛔ **`REQUIRED_FIELDS` pinned at exactly the original seven**, so an optional field can never become mandatory by UI accident | +8 |
| 6.6 | ⚠️ **The `health_flags` disclosure in the form's copy** (Q11) — *"attaching every document does not by itself mark an application complete"* | +2 |
| 6.7 | The upload-latency affordance (Q3(a): *disclosed, not engineered away*) | +2 |

---

## 7. Named stop-gates

1. **Any test green on arrival** → vacuous; demonstrate RED by inverting the implementing change, or stop.
2. ⛔ **Any WIRE-1 row R1–R11 differing byte-for-byte** at step 1.3. Fold-7 is **additive or it is nothing**.
3. ⛔ **The filesystem guard failing to bite** at step 1.5, or **not failing** at step 2.6 → the guard is vacuous. Stop.
4. ⛔ **`Content-Length` treated as a security control** anywhere → it can lie; F4 and H1 exist to prove the
   streaming counter is the real bound.
5. ⛔ **A blocking call on the event loop** — `subprocess.run` reachable from an `async def` without
   `run_in_threadpool`. D4 pins it; a regression freezes the whole process, not one request.
6. ⛔ **A temp file surviving a request** on any path, including every adversarial case in 4.3.
7. ⛔ **The JSON path changing behaviour** — Constraint 4. ~15 existing tests and the shipped frontend depend on it.
8. **Counts ≠ prediction** → report the corrected figure **with its cause**; never trim tests to hit a number.
9. ⛔ **Any frozen unit in `git status`** — `intake/`, `rules_engine/`, `case_lifecycle/`, `common/`. Under the
   answered set **none is expected**; `deploy_config/tests/_route_inventory.py` is expected **untouched** too
   (§0's G3 finding).
10. **Frontend ≠ 778** before stage 6, or **either** coverage threshold edited at any point.
11. ⛔ **`incomplete=false` claimed anywhere** — §0.2. Document-completeness is one clause of seven.
12. **Any commit before its stage's gate.**

---

## 8. Predicted totals

| Stage | Backend Δ | Frontend Δ | Independently committable? |
|---|---|---|---|
| 1 — Fold-7 + the guard | **+3** | — | ✅ **Yes** — nothing is declared-but-unserved |
| 2 — temp lifecycle + sweep | **+12** | — | ✅ Yes |
| 3 — concurrency bounding | **+6** | — | ✅ Yes |
| 4 — the multipart reader | **+18** | — | ✅ Yes — the reader is unit-testable before R10 uses it |
| 5 — R10 wired | **+9** | — | ✅ Yes |
| 6 — frontend + optional fields | — | **+34** | ✅ Yes |
| **Total** | **1691 + 48 = 1739** | **778 + 34 = 812** | |

⚑ **Every stage is independently committable here** — unlike register #2, whose stage 1 declared a route surface
nothing served. Nothing in stage 1 promises a capability that arrives later.

---

## 9. Manual verification — USER-RUN (after stage 6)

> ⛔ **REWRITTEN 2026-08-07, AFTER ALL SIX STAGES SHIPPED, against the constants the code actually defines.**
> The original ten items are preserved verbatim immediately below. ⚠️ **One of them was UNPERFORMABLE AS
> WRITTEN** — item 8's *"restart, and confirm the sweep removed the orphan"* — because
> `ORPHAN_MAX_AGE_SECONDS = 3600` means a **freshly** orphaned directory is **deliberately left alone**. Leaving
> that step as written would have produced a "failure" that is the design working correctly. Superseded rather
> than rewritten away, on register #2's §6 precedent: *why* a verification step was wrong is worth more than the
> step.
>
> **The original, verbatim:**
>
> > 0. **Prerequisites**: an `underwriter` and an `auditor` credential · `corpus/` present · **three real PDFs**, plus one deliberately corrupt file and one file over the size cap.
> > 1. Reset the pending tables (⛔ **never drop**).
> > 2. Submit **with all three documents attached** through the UI → watch each reach **parsed**.
> > 3. `psql`: the manifest carries **3 `parsed` entries**; ⛔ **`documents_missing_count = 0`**.
> > 4. R4/the memo: ⛔ **`DOCS-COMPLETE-1` PASSES** — the point of the pass, read off a real decision.
> > 5. ⚠️ **Confirm `incomplete` is STILL true** with the optional fields left blank — and **false** once they are filled, ⛔ **except** for `health_flags` (Q11's disclosed limitation, observed rather than described).
> > 6. **The corrupt file** → `unparseable`, the case still persists, the outcome is a REFER not a crash.
> > 7. **The oversized file** → **413**, and ⛔ `ls` the temp root: **nothing left behind**.
> > 8. ⛔ **Kill the server mid-upload** (the window with no in-process answer), restart, and confirm **the sweep removed the orphan**.
> > 9. **Authorization**: submit as an **auditor** → **403**, and ⚑ **confirm the temp root is untouched** — proving zero bytes were consumed, which is Fold A's finding closed by observation rather than by test.
>
> **What changed, and why:**
>
> | # | Correction | Why the original was wrong or incomplete |
> |---|---|---|
> | **8** | Split into **three observations**: orphan exists → **survives** the first restart → is swept only once **backdated past the threshold** | `ORPHAN_MAX_AGE_SECONDS = 3600`. A fresh orphan surviving restart is **test B2 (`it_leaves_a_FRESH_directory_alone`) working as designed** — the load-bearing half, since a sweep that took fresh directories would destroy **concurrent live requests**. The original would have read that as a failure. |
> | **5** | Rewritten as the **J7 four-way matrix**, and the `health_flags` clause **corrected** | The original said `incomplete` goes false *"except for `health_flags`"*, implying it can never go false. **It can** — `health_flags` is a real input the form now collects, so filling it clears the clause. The limitation is that leaving it **empty** keeps you incomplete, which is the opposite framing. |
> | **2** | The three `DocType` **part names** and the **5 MiB** per-file cap stated | §9 never named the constants a verifier has to hit. |
> | **new 4** | ⛔ **The malformed-multipart 400 added** | §12.6 found `submission.py:149–150` (`MultipartInvalid → 400`) is **uncovered by any test**. This step is the only thing that exercises it. |
> | **new 6** | The **concurrency bound** added | The original never verified `MAX_CONCURRENT_PARSES` at all, though Q4 gave it its own stage. |
> | **new 11** | The **JSON-only path** added | Constraint 4 is the pass's largest regression risk and the original never checked it. |
> | **0** | Prerequisites made concrete — exact commands to build every fixture file | The original said *"one file over the size cap"* without saying the cap is **5 MiB**. |

### ⚑ Step 0 — PREREQUISITES

**Credentials**: one `underwriter` and one `auditor`, as in register #2's §6. **`corpus/profiles.json` + `corpus/manifest.json` present** — drafting raises `FileNotFoundError` by design without them.

**The constants this walkthrough hits** (all measured from the shipped code — do not assume):

| Constant | Value | Where |
|---|---|---|
| `MAX_DOCUMENT_BYTES` | **5 MiB** (`5 * 1024 * 1024`) per file | `multipart_reader.py:59` |
| `MAX_DOCUMENTS` | **3** — `len(DocType)`, domain-derived | `multipart_reader.py:68` |
| `MAX_TOTAL_BYTES` | **15 MiB** | `multipart_reader.py:71` |
| `MAX_CONCURRENT_PARSES` | **2** | `parse_concurrency.py:58` |
| `UPLOAD_TEMP_ROOT` | `<system temp>/underwriting-uploads` | `upload_storage.py:50` |
| `REQUEST_DIR_PREFIX` | `req-` | `upload_storage.py:54` |
| ⚠️ `ORPHAN_MAX_AGE_SECONDS` | **3600** — **step 10 depends on this** | `upload_storage.py:62` |

**Part names are the `DocType` values, exactly**: `salary_slip` · `bank_statement` · `medical_questionnaire`, plus one `form_fields` part carrying a **JSON string**.

**Build the fixture files** (Git Bash):

```bash
mkdir -p /tmp/docverify && cd /tmp/docverify
# three real PDFs — any will do; the seeded corpus PDFs or any PDF on your machine
cp /path/to/some.pdf salary.pdf && cp /path/to/some.pdf bank.pdf && cp /path/to/some.pdf medical.pdf
# a file that is NOT a PDF but is named like one -> exercises `unparseable`
printf 'this is not a pdf at all\n' > corrupt.pdf
# 6 MiB -> over the 5 MiB per-file cap
head -c 6291456 /dev/urandom > oversize.pdf
```

**Set `T` to the temp root** — you will `ls` it repeatedly:

```bash
T="${TMPDIR:-/tmp}/underwriting-uploads"   # Git Bash on Windows: usually /c/Users/<you>/AppData/Local/Temp
ls -la "$T" 2>/dev/null || echo "(root does not exist yet — expected before the first upload)"
```

**Log in and keep the cookie** (needed for every `curl` step):

```bash
curl -s -c uw.txt -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"<underwriter>","password":"<pw>"}' -o /dev/null -w '%{http_code}\n'   # expect 204
curl -s -c aud.txt -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"<auditor>","password":"<pw>"}' -o /dev/null -w '%{http_code}\n'       # expect 204
```

---

### The steps

**1. Reset the pending tables.** ⛔ **`DELETE`, never `DROP`** — dropping re-runs `0002_grants.sql`'s unguarded
`CREATE ROLE` and destroys the accumulated audit evidence (the override pass's `AuditRecord a7b67ca8-…` and
register #2's `9d39d4e1-…`). Then confirm the temp root is empty or absent:

```sql
DELETE FROM pending_recommendation; DELETE FROM pending_application;
```

---

**2. ⛔ THE CORE PATH — submit through the UI with all three documents attached.**

Log in as the **underwriter**, fill the **seven required fields**, and attach a real PDF to **each of the three
slots**: *Salary slip* · *Bank statement* · *Medical questionnaire*.

* ⚑ Money fields are free text on purpose — intake's **BR-TYP-1 refuses a JSON float**. Enter `1200000`, never
  `1200000.50`.
* Watch each document's status region (`data-testid="submission-docstatus-salary-slip"`, etc.) move
  **"Ready to upload" → "Checking…" → "Read successfully."**
* ⚠️ **The submit is slower than register #2's** — up to ~15 s with three documents. **That is Q3(a) working**:
  parsing is synchronous and the latency is *disclosed* ("Checking documents can take a few seconds."), not
  engineered away. **Not a hang.**

Then confirm on the wire and in the database:

```sql
SELECT application_id, state, length(profile_canonical) AS bytes FROM pending_application;
SELECT convert_from(profile_canonical,'UTF8')::json -> 'documents' FROM pending_application;
```

⛔ **Expect three manifest entries, every one `parsed`.** Then:

```sql
SELECT convert_from(profile_canonical,'UTF8')::json ->> 'documents_missing_count' FROM pending_application;
```

⛔ **Expect `0`** — this is what makes `DOCS-COMPLETE-1` pass, and it is the whole point of the pass.

---

**3. `DOCS-COMPLETE-1` PASSES, read off a real decision.** Trigger drafting from the accepted panel
(*"Start assessment"*), then fetch the memo and find the rule by ID:

```bash
curl -s -b uw.txt http://localhost:8000/applications/<APP-ID>/recommendation | python -m json.tool | grep -A4 DOCS-COMPLETE-1
```

⛔ **Expect `passed`.** ⚑ In every prior verification in this project's history this rule has **failed**. This is
the first time it has not.

* ⚠️ The first draft is **~2.6 s slower** — the lazy corpus fit, once per process. Expected.
* ⛔ **Drafting is only triggerable immediately after submitting** — register #2's named residual, unchanged by
  this pass. Do not reload before clicking.

---

**4. ⚑ NEW — the malformed-multipart 400 at the route.** §12.6 found this path
(`submission.py:149–150`) is **covered by no test**. It is worth one command:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -b uw.txt -X POST http://localhost:8000/applications \
  -H 'Content-Type: multipart/form-data; boundary=----zzz' \
  --data-binary $'------zzz\r\nContent-Disposition: form-data; name="form_fields"\r\n\r\nnot-json\r\n------zzz--\r\n'
```

⛔ **Expect `400`**, a WIRE-1 §4 envelope with `code: "invalid_request"` (not a 500, not a stack trace), and
`ls "$T"` **empty**.

---

**5. The size and count caps, and their actual statuses.**

| Do this | Expect | Why |
|---|---|---|
| Attach `oversize.pdf` (6 MiB) in the UI | ⛔ **413**, message *"That file is too large. Choose a smaller PDF."*, **you stay on the form with your typed values intact** | The **streaming counter** refuses mid-body. ⚑ There is **no `Content-Length` middleware** — step 4.6's fast-reject was not built, and the counter is the sole control, which is the stronger outcome (stop-gate 4). |
| Two parts with the **same** `doc_type` (`curl`, below) | ⛔ **400**, never last-wins | Q6: silently discarding an uploaded document is the worst option |
| An **unknown** `doc_type` part name | ⛔ **400** | WIRE-1 §1's `DocType` row — the first client-authored enum |

```bash
# duplicate doc_type -> 400
curl -s -o /dev/null -w 'duplicate: %{http_code}\n' -b uw.txt -X POST http://localhost:8000/applications \
  -F 'form_fields={"full_name":"A B","city":"Pune","gender":"female","date_of_birth":"1990-01-01","as_of_date":"2026-08-07","verifiable_income_annual":"1200000","requested_cover_amount":"5000000"}' \
  -F 'salary_slip=@salary.pdf' -F 'salary_slip=@bank.pdf'

# unknown doc_type -> 400
curl -s -o /dev/null -w 'unknown:   %{http_code}\n' -b uw.txt -X POST http://localhost:8000/applications \
  -F 'form_fields={"full_name":"A B","city":"Pune","gender":"female","date_of_birth":"1990-01-01","as_of_date":"2026-08-07","verifiable_income_annual":"1200000","requested_cover_amount":"5000000"}' \
  -F 'salary_slip=@salary.pdf' -F 'passport=@bank.pdf'
```

⛔ **After each: `ls "$T"` must be empty.** Stop-gate 6 — no temp file survives a request on **any** path.

⚑ **A fourth document cannot be constructed**, and that is by design: `MAX_DOCUMENTS = len(DocType)` and `DocType`
is closed, so a fourth part necessarily carries either an unknown name (400) or a duplicate name (400). The count
cap is **derived from the domain**, not invented — there is no separate "too many documents" error to observe.

---

**6. ⚑ NEW — the concurrency bound (`MAX_CONCURRENT_PARSES = 2`).**

⚠️ **Stated honestly: a bound of 2 cannot be observed by clicking**, because one browser submits one request at a
time. The minimum bar is that it **does not visibly break a normal single submission** — which step 2 already
established. To actually exercise it, fire four concurrent uploads and watch them all succeed:

```bash
for i in 1 2 3 4; do
  ( curl -s -o /dev/null -w "req$i: %{http_code} in %{time_total}s\n" -b uw.txt \
      -X POST http://localhost:8000/applications \
      -F "form_fields={\"full_name\":\"Load $i\",\"city\":\"Pune\",\"gender\":\"female\",\"date_of_birth\":\"1990-01-01\",\"as_of_date\":\"2026-08-07\",\"verifiable_income_annual\":\"1200000\",\"requested_cover_amount\":\"5000000\"}" \
      -F 'salary_slip=@salary.pdf' -F 'bank_statement=@bank.pdf' -F 'medical_questionnaire=@medical.pdf' ) &
done; wait
```

⛔ **Expect four `200`s and no `500`, no timeout, no dropped connection.** ⚑ **The bound converts a crash into a
wait** (Q4(a)) — so later requests should show **visibly longer `time_total`** than the first two. That
stagger *is* the semaphore. **The health check must stay responsive throughout** — run
`curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/health` in another shell while the four are in
flight. ⛔ **If it blocks, Constraint 1 has regressed** (blocking work back on the event loop), and that is the
single worst failure this pass can have — it degrades the whole process, not one request.

---

**7. Per-document status must be VISIBLE and DISTINCT.**

In the UI, attach **`corrupt.pdf` to the medical-questionnaire slot** and **real PDFs to the other two**. Submit.

⛔ **Expect three *different* per-document outcomes rendered side by side**, not one aggregate:

| Slot | Expected status text |
|---|---|
| Salary slip | *"Read successfully"* |
| Bank statement | *"Read successfully"* |
| Medical questionnaire | ⛔ *"Could not be read — the application was still accepted"* |

Then confirm the case **still persisted** and that a bad document is a **REFER, never a crash**:

```sql
SELECT convert_from(profile_canonical,'UTF8')::json -> 'documents' FROM pending_application
 ORDER BY application_id DESC LIMIT 1;
```

⛔ **Expect two `parsed` and one `unparseable`, `state = evaluated`, and NO 500.** ⚑ This is `IntakeGate` refusing
to be lied to — a client cannot assert a document is fine.

`ls "$T"` — ⛔ **empty**, on the unparseable path too.

---

**8. The optional fields must be genuinely OPTIONAL.**

⛔ **The submit button must enable with every optional field blank.** Fill only the seven required fields and
confirm submit is enabled *before* touching anything in *"Additional details (optional)"*. Then fill an optional
field, clear it again, and confirm submit **stays enabled**.

⚑ **This is the UI-accident guard**: `REQUIRED_FIELDS` is pinned at exactly the original seven (`copy.js:22`) and
`OPTIONAL_FIELDS` is a disjoint tuple. If an optional field ever silently joined the required set, this is the
step that catches it.

**Also confirm the disclosure is on screen**, in the form's copy, not a code comment (Q11(a)):

> *"Attaching every document does not by itself mark an application complete. Leaving health notes empty will
> also keep it marked incomplete, even when nothing is wrong — write "none reported" if that is the case."*

---

**9. ⛔ THE J7 COMPLETABILITY PROOF — `incomplete = false` for the first time in this project's history.**

⚑ **This is the single most significant observation in the walkthrough.** Every prior verification in this
project has read `incomplete = true`. Do all four cases and read each from `psql` — ⛔ **not from the UI**, which
does not display it.

The query, run after each submission:

```sql
SELECT application_id,
       convert_from(profile_canonical,'UTF8')::json ->> 'incomplete' AS incomplete
  FROM pending_application ORDER BY application_id DESC LIMIT 1;
```

| # | Submit | Expect |
|---|---|---|
| **9a** | 3 documents, **all optional fields blank** | `incomplete = true` — ⚑ **documents fix ONE clause of SEVEN** (§0.2) |
| **9b** | **No documents**, every optional field filled | `incomplete = true` — the documents clause alone now fails |
| **9c** | ⛔ **3 documents + EVERY optional field, health notes non-empty** | ⛔ **`incomplete = false`** ← **THE FIRST TIME** |
| **9d** | 3 documents + every optional field **except health notes left blank** | `incomplete = true` — **Q11's disclosed limitation, observed live** |

For **9c**, fill *all seven* optional inputs: **Height (cm)** `175` · **Weight (kg)** `70` ·
**Existing annual debt obligations** `200000` · **Occupation** `Engineer` · **Employment type** `Salaried` ·
**Smoking status** `Non-smoker` · **Health notes** `none reported`.

⚑ **"Health notes" is a single free-text input sent as a one-element list** (`SubmissionView.jsx:43`), so any
non-blank text supplies exactly one health flag. ⚠️ **`none reported` is not a fabricated clinical assertion** —
it is the applicant stating they have nothing to report, which is what the disclosure asks for. Q11(c)'s rejected
option was a *sentinel the UI submits on the applicant's behalf*; this is the applicant typing it.

⛔ **If 9c does not yield `false`, stop and report it** — every other step can pass with this one broken, and it
is the pass's headline claim.

---

**10. ⛔ THE MID-UPLOAD SERVER KILL — the retention window with no in-process answer.**

⚑ **This has never been exercised, by any test, in any pass.** `try/finally` covers three of Q5's four windows;
this is the fourth, and it is the *normal* case on Render's free tier, where spin-down is routine.

**10a — leave an orphan.** In shell A, start an upload big enough to still be streaming, then kill the server in
shell B while it is in flight:

```bash
# shell A — a ~4.9 MiB file, under the cap so it will not 413, slow enough to catch
head -c 5138022 /dev/urandom > slow.pdf
curl -s -o /dev/null -w '%{http_code}\n' -b uw.txt -X POST http://localhost:8000/applications \
  --limit-rate 400k \
  -F 'form_fields={"full_name":"Kill Test","city":"Pune","gender":"female","date_of_birth":"1990-01-01","as_of_date":"2026-08-07","verifiable_income_annual":"1200000","requested_cover_amount":"5000000"}' \
  -F 'salary_slip=@slow.pdf'
```

```bash
# shell B — while shell A is still streaming (~12 s at 400k), kill HARD. SIGKILL, not Ctrl-C:
#   Ctrl-C would let the finally block run and there would be no orphan to find.
taskkill //F //IM python.exe          # Windows
# kill -9 <uvicorn-pid>               # POSIX
```

⛔ **Now confirm the leak is REAL:**

```bash
ls -la "$T"
```

**Expect one surviving `req-…` directory containing `salary_slip.pdf`.** ⚑ **This is the failure mode the sweep
exists for, observed rather than argued.** ⚠️ Note the file is named from the **`DocType`, never the client's
filename** — path-traversal safety, visible right here.

**10b — restart, and expect the orphan to SURVIVE.** ⛔ **This is not a bug. It is the design.**

```bash
uvicorn backend.app.main:app --port 8000     # restart
ls -la "$T"                                   # the req-… directory is STILL THERE
```

⚑ `ORPHAN_MAX_AGE_SECONDS = 3600`, and the sweep removes only directories **older** than that. A sweep that took
fresh directories would **delete the temp dirs of concurrent live requests** — which is exactly why
`test_it_leaves_a_FRESH_directory_alone` is described in §2 as *"the load-bearing half."* **You are observing that
protection work.**

**10c — backdate past the threshold, restart again, and NOW the sweep takes it.** Stop the server, then:

```bash
ORPHAN=$(ls -d "$T"/req-* | head -1); echo "$ORPHAN"
touch -d '3 hours ago' "$ORPHAN"        # older than ORPHAN_MAX_AGE_SECONDS
uvicorn backend.app.main:app --port 8000
ls -la "$T"
```

⛔ **Expect the `req-…` directory to be GONE, and the application to have started normally.**

⚑ **Both halves are now observed**: the sweep removes a genuine orphan, and it refuses to touch a live one. **The
retention guarantee stated in WIRE-1 §7.4 is closed by observation for the first time.**

**10d — the sweep must never take the service down.** Make the root unreadable (or replace it with a *file*
named `underwriting-uploads`) and restart:

```bash
rm -rf "$T" && printf 'not a directory' > "$T"
uvicorn backend.app.main:app --port 8000
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/health   # expect 200
rm -f "$T"                                                              # clean up
```

⛔ **The application MUST boot.** Fold B's constraint: a sweep that fails closed is **strictly worse** than the
leaked file it exists to remove.

---

**11. ⛔ THE JSON-ONLY PATH MUST BE BYTE-UNCHANGED (Constraint 4).**

⚑ **The pass's largest regression risk**: ~15 backend tests and the frontend shipped at `d43b661` both send JSON.

```bash
curl -s -o /dev/null -w 'json submit: %{http_code}\n' -b uw.txt -X POST http://localhost:8000/applications \
  -H 'Content-Type: application/json' \
  -d '{"form_fields":{"full_name":"Json Path","city":"Pune","gender":"female","date_of_birth":"1990-01-01","as_of_date":"2026-08-07","verifiable_income_annual":"1200000","requested_cover_amount":"5000000"},"documents":[]}'
```

⛔ **Expect `200`** and a persisted case, exactly as register #2 delivered it. Also confirm **in the UI** that a
submission with **no documents attached** still works — it takes the JSON encoding, not multipart.

Two negatives that must also hold:

```bash
# a malformed JSON body still yields the SAME WIRE-1 400 envelope (Constraint 3 — this is now hand-written code)
curl -s -b uw.txt -X POST http://localhost:8000/applications -H 'Content-Type: application/json' -d '{"nope":1}'
# a documents ARRAY in a JSON body is still refused — Fold-7 did NOT make JSON document-bearing
curl -s -b uw.txt -X POST http://localhost:8000/applications -H 'Content-Type: application/json' \
  -d '{"form_fields":{},"documents":[{"doc_type":"salary_slip","status":"present"}]}'
```

⛔ **Both `400`**, both carrying `code: "invalid_request"` with per-field `detail`.

---

**12. Authorization — and ⛔ ZERO BYTES CONSUMED. Fold A closed by observation.**

```bash
rm -rf "$T"    # start from nothing so the check is unambiguous
curl -s -o /dev/null -w 'auditor multipart: %{http_code}\n' -b aud.txt -X POST http://localhost:8000/applications \
  -F 'form_fields={"full_name":"Auditor","city":"Pune","gender":"female","date_of_birth":"1990-01-01","as_of_date":"2026-08-07","verifiable_income_annual":"1200000","requested_cover_amount":"5000000"}' \
  -F 'salary_slip=@oversize.pdf'
ls -la "$T" 2>/dev/null || echo "root absent — ZERO bytes were written"
```

⛔ **Expect `403`, and the temp root absent or empty — even though a 6 MiB file was offered.**

⚑ **This is the finding that reshaped the whole design, closed by observation.** Fold A measured that FastAPI
reads the body *before* resolving dependencies — so under the rejected `UploadFile` design the server would have
written 6 MiB to disk **and then** returned 403. Q13(b) removed the body parameter entirely, so `body_field is
None`, so the framework never touches the stream, so **a wrong-role caller now causes literally zero I/O**. That
is what register #2's C4 spy stood in for and could not itself enforce — **and here it is on screen.**

Also repeat the UI submit as an auditor → **403**, as in register #2's §6.

---

### ⚠️ What this walkthrough deliberately does NOT claim

* ⛔ **`structured_fields` extraction remains OUT** (Q9). Nothing here should be read as populating a profile
  field from a document's contents. `parse_worker.py` still returns `{}`, always. **Documents buy
  document-COMPLETENESS, not document-derived DATA.**
* ⚠️ **SUPERSEDED 2026-08-13 — this bullet was ALREADY FALSE when the walkthrough ran.** Preserved verbatim:
  > *"⛔ **Q8(c)'s `neutralization_count` is NOT implemented** (§12.4) — **there is nothing to verify here**, and
  > no step above pretends otherwise. PROJECT-BRIEF §10 failure mode #4 becomes reachable with this pass and its
  > evidence channel is still unwired."*

  **Q8(c) was implemented 2026-08-09**, the day before the walkthrough began (§12.4's correction note).
  ⚑ **The replacement claim is narrower than simply deleting this bullet would imply**: the evidence channel is now
  wired and pinned by **J8/J9 at tier-U**, but ⛔ **no §9 step observes it live** — none was written, because when
  §9 was drafted on 2026-08-07 there was nothing to observe. **So `neutralization_count` reaching a real log sink
  is proven by test and NOT by this walkthrough**, and that distinction is the honest one. A live observation would
  need a step that submits a poisoned PDF and greps the server log for `underwriting.intake.telemetry`; it is
  **not** claimed here. ⚠️ Q8's deferred half — the durable verbatim-span sink — remains **OUT**, now tracked as
  **register #30**.
* ⚠️ **`MAX_CONCURRENT_PARSES` is confirmed, not stress-proven.** Step 6 shows the bound does not break real
  concurrent traffic and that the event loop stays live. It does not measure peak RSS — ⛔ **and the Render
  free-tier 512 MB figure remains DOCUMENTED, NOT MEASURED** (§11 item 1).

---

## 10. Holds

⛔ No frozen unit edited · WIRE-1 amended **only** under G1 · the filesystem guard created **only** under G2 · no
migration · no commit before each stage's gate · frontend untouched until stage 6 · `render.yaml` untouched
(**⚠️ but see §11 item 1**).

---

## 11. Carried forward

1. ⛔ **The deployment pass now owes THREE things**: `corpus/` placed and verified (register #2) · a **writable
   temp location** confirmed on Render · **the free-tier memory figure measured**, since Q4's bound depends on it
   and 512 MB is **documented, not measured**.
2. ⚑ **Two register items open by their own answers** — Q8's deferred verbatim-span sink, and Q11's
   `health_flags` completeness limitation.
3. ⚠️ **Register #2's residual** — a pending case has no UI draft affordance outside the post-submit flow.
   Untouched by this pass.
4. ⛔ **`structured_fields` extraction remains OUT** (Q9). Nothing in this pass should be described as
   populating profile fields from a document.

---

## 12. ⚠️ STOP-GATE 8 RECONCILIATION — the count variance, re-derived 2026-08-07

⛔ **Stop-gate 8 requires the corrected figure be reported WITH ITS CAUSE.** The execution left no contemporaneous
record, so the cause was **re-derived by reading and categorizing the actual test files** — not inferred from the
diff and not narrated from memory. Baseline counts were measured in a throwaway `git worktree` at `d43b661`.

### 12.1 The arithmetic

**Collected** counts, not passed counts — `passed` excludes skips and the skip column moved:

| | Baseline (`d43b661`) | Now | Δ |
|---|---|---|---|
| Backend **collected** | 1691 + 44 = **1735** | 1771 + 45 = **1816** | **+81** |
| Backend **passed** | 1691 | 1771 | +80 |
| Backend **skipped** | 44 | 45 | **+1** |
| Frontend | 778 | 808 | **+30** |

⚑ **The `+80 passed / +1 skipped` split is fully explained**: the single new skip is
`test_upload_storage.py::test_the_directory_is_owner_only` — **step 2.2's A4**, present and correct but guarded
`resource.setrlimit unavailable (non-POSIX); runs in Linux CI`. **Nothing is silently disabled.**

### 12.2 Backend — **+81 actual vs +48 predicted, variance +33**

| Stage | File | Predicted | Actual | Δ |
|---|---|---|---|---|
| 1 | `test_no_write_route.py` | +3 | **+4** | +1 |
| 2 | `test_upload_storage.py` | +12 | **+17** | +5 |
| 3 | `test_parse_concurrency.py` | +6 | **+10** | +4 |
| 4 | `test_multipart_reader.py` | +18 | **+28** | +10 |
| 5 | `test_submission_documents.py` | +9 | **+22** | +13 |
| — | `test_submission_routes.py` | 0 | **0** | 0 — **two tests SUPERSEDED IN PLACE**, not added |
| — | `test_error_envelope.py` | 0 | **0** | 0 — one cardinality assertion superseded (`len(STATUS_TABLE)` 8 → 9) |
| **Total** | | **+48** | **+81** | **+33** |

⚑ **Three plan items realized as ZERO new tests, correctly.** **C1** (*"`create_app()` still fits no model"*) is
register #2's existing guard **re-run**, not a new test — the plan budgeted +1 for it. **H2** (*"the JSON path is
byte-unchanged"*) is realized as **the ~31 unchanged tests in `test_submission_routes.py` continuing to pass** —
the correct expression of "byte-unchanged" is *no new assertion*. **H3/H4 relocated** from stage 4 into
`test_submission_documents.py`, where the real route exists to assert against.

### 12.3 The +33, categorized by cause

**A — non-vacuity partners (~12 tests). The single largest cause.** Stop-gate 1 forbids a test that is green on
arrival, and the discipline was applied per named assertion; **the plan budgeted the assertion but never its
partner.** `test_the_detector_permits_reads_and_prose` (stage 1 — guards the detector being over-broad, the exact
risk §1's *"Stage 1's real risk"* names) · `test_startup_DOES_sweep` (C2 says `create_app` sweeps nothing; without
this, a sweep that never runs would also pass) · `test_the_bound_is_not_merely_SERIALIZING_everything` (D2 passes
identically at a bound of 1) · `test_an_AUTHORIZED_caller_DOES_reach_the_stream` (**E1's partner — without it, a
route broken shut also reads zero bytes**) · `test_a_submission_with_NO_documents_still_fails_that_rule` (J2's
partner) · and ⚑ **two fixture-reality tests** — `test_pdfplumber_really_extracts_text_from_the_fixture` and
`test_the_corrupt_fixture_is_genuinely_unparseable` — **without which every J-test could pass against a fixture
that is not a PDF at all.**

**B — the hand-rolled parser's real failure surface is wider than F1–F6 (~6 tests).** Q13's answer named six
adversarial cases from the outside; the implementation found more from the inside. `F1b` a **missing** boundary
parameter and `F1c` a **non-multipart** Content-Type are distinct code paths from F1's *malformed* boundary ·
`test_a_missing_form_fields_part_is_refused` + `test_a_non_json_form_fields_part_is_refused` are **Constraint 3's
territory** (`form_fields` lost Pydantic validation), which §4.2 recorded as a constraint and §4 budgeted **no
tests for** · `test_a_body_split_across_MANY_small_chunks_parses_identically` — **chunk-boundary independence, the
likeliest defect in any hand-rolled stream parser and covered by no F-test** · ⛔
`test_the_client_filename_is_NEVER_used_as_the_on_disk_name` — **path traversal via a client-supplied filename,
contemplated nowhere in the plan.**

**C — Constraints 1 and 2 needed pinning at BOTH levels (~5 tests).** The plan pinned them once (D3/D4) against
the helper. The implementation re-pinned them against the **real R10 handler**
(`test_the_blocking_work_does_not_run_on_the_event_loop`), and added
`test_the_limiter_survives_being_used_from_TWO_event_loops` + `test_the_limiter_is_one_instance_per_process` — ⚑
**Q4(a) said "process-wide" and nothing in D1–D6 asserted the "process-wide" half.**

**D — the retention guarantee is PER EXIT PATH, not per stage (~4 tests).** J5 was budgeted as one test covering
"success and unparseable". Realized as **four** — success · unparseable · **rejected intake** · **413** — because
stop-gate 6 says *no temp file surviving a request on **any** path*, and each exit is a separate path. Plus stage
2's `test_it_tolerates_an_UNREMOVABLE_entry_and_keeps_going` and
`test_two_concurrent_requests_get_DIFFERENT_directories`.

**E — Fold A closed by committed assertion rather than by probe (2 tests).**
`test_the_handler_declares_NO_UploadFile_parameter` and
`test_no_spooled_temp_file_is_constructed_for_a_real_multipart_request` turn §4.2's throwaway design-time probe
into permanent guards. ⚑ **The entire Q13(b) design exists to serve this property and the plan budgeted nothing to
protect it from regression.**

**F — J7 widened from one test to a four-way matrix (+3).** Budgeted as a single negative. Realized as: documents
alone (still incomplete) · documents **+ every optional field** (complete) · every optional field **without**
documents (still incomplete) · and ⛔
**`test_J7_an_applicant_reporting_NO_health_flags_CANNOT_be_complete`**, which converts **Q11's disclosed
limitation from prose into an executable assertion.** The plan asked for none of these three.

### 12.4 ⛔ 12.3 is all OVERSHOOT. Here is the one SHORTFALL — and it is the more important finding

> ## ✅ **CLOSED 2026-08-09 (15:28–15:38Z). The section below is PRESERVED VERBATIM as the finding that caused the fix.**
>
> `backend/app/intake_telemetry.py` is **new** and supplies a real `TelemetryEmitter` sink on the named logger
> `underwriting.intake.telemetry`; `dependencies.py:354` now constructs
> `IntakePipeline(parse_worker=SubprocessParseWorker(), telemetry=build_intake_telemetry())`. **J8**
> (`test_J8_neutralization_count_reaches_telemetry_for_a_poisoned_document`) and **J9**
> (`test_J9_no_verbatim_span_and_no_PII_leaves_the_sanitizer`) exist — step 5.6's predicted **+2**, delivered.
> ⚑ The grep this section reports as returning *"no match anywhere"* now returns **8 hits**.
>
> **Three properties of the fix that the plan did not specify** — recorded because they are what makes it non-vacuous:
> **(1)** J8 asserts **both directions in one test** (clean → `0`, poisoned → `>= 1`), because asserting only the
> poisoned case passes identically against a sink emitting a constant. **(2)** J9 checks the **rendered log line**
> as well as the structured payload, and asserts the emitted key set **equals** the six-member allowlist, so a
> future free-text field on `TelemetryEvent` fails there rather than shipping. **(3)** Both assert **through the
> real route against the real production provider** — the defect was *precisely* a composition-root omission, and a
> test that composed its own pipeline could not have seen it.
>
> ⚠️ **Q8(c) only.** The durable verbatim-span sink stays deferred, now tracked as **register #30**
> (`INJECTION-SPAN-SINK-DEFERRED`) — ⚑ opened **late**, in the 2026-08-13 `guide-state.md` backfill, because Q8's
> answer said to open it and it never was.
>
> ⛔ **This closure is NOT observed by §9** — see §9's superseded disclaimer. Proven by test, not by walkthrough.

**Step 5.6's J8 and J9 DO NOT EXIST, and Q8(c) IS NOT IMPLEMENTED.** Predicted **+2**; delivered **0**.

Measured, not inferred:

* `grep -rn "neutralization" backend/app/` → **no match anywhere**, tests included.
* `dependencies.py:337` constructs `IntakePipeline(parse_worker=SubprocessParseWorker())` — ⛔ **with no
  `telemetry=` argument**, so it falls back to `intake`'s default `TelemetryEmitter()`.

⛔ **Q8(c) was chosen precisely because this pass is what makes PROJECT-BRIEF §10 failure mode #4 — prompt
injection in an uploaded document — reachable for the first time.** §1.2 item 5 of the design plan states it
directly: *"With user-uploaded PDFs it becomes the forensic record of prompt-injection attempts — and it goes
nowhere."* **The pass that creates the risk did not deliver the evidence channel.** The sanitizer still runs and
still neutralizes; only the **count** that would make an attempt visible is unwired.

⚠️ **This does not block §9** — no verification step depends on it — **but it must not be lost.** It is a real
open item and, on the design plan's own Q8 reasoning, the answer's whole purpose.

### 12.5 Frontend — **+30 actual vs +34 predicted, variance −4**

Entirely in the two new files; `form.test.jsx` is **net 0** (one assertion superseded in place — the seam gained a
second argument).

| Step | Predicted | Actual | Δ |
|---|---|---|---|
| 6.1 transport `FormData` + JSON byte-unchanged | +4 | **6** | +2 |
| 6.2 seam chooses the encoding | +5 | **4** | −1 |
| 6.3 per-document state, visible | +8 | **7** | −1 |
| 6.4 **413 + per-document error paths** | +5 | **1** | ⚠️ **−4** |
| 6.5 the optional fields + `REQUIRED_FIELDS` pinned | +8 | **9** | +1 |
| 6.6 the `health_flags` disclosure | +2 | **2** | 0 |
| 6.7 the latency affordance | +2 | **1** | −1 |
| **Total** | **+34** | **30** | **−4** |

⚑ **6.4 is the whole variance.** It collapsed to one test (`a 413 is recoverable and keeps the user on the form`)
because (i) the **400 rejection path was already covered** by the pre-existing, unchanged `rejection.test.jsx`
(12 tests) and needed no new assertion to stay distinct, and (ii) per-document error rendering was absorbed into
6.3's `⛔ shows PARSED and UNPARSEABLE per document, never one aggregate` — which is the assertion 6.4 would have
duplicated. **A legitimate consolidation, not a gap** — but recorded because 6.4's second clause, *"rendered
**distinctly** from the 400 rejection path"*, is now pinned only indirectly.

### 12.6 Coverage 99.64% → 99.45%, with cause — ⚠️ **now 99.49%, see the corrected row**

> ⚑ **RE-MEASURED 2026-08-13**: **10 missed statements / 13 partial branches of 3908 → 99.49%.** The two recovered
> statements are exactly `routes/submission.py:149–150`; the statement total rose 3897 → 3908 because
> `intake_telemetry.py` (10 statements) is new. **Every other row below is unchanged and still accurate.**

**As measured 2026-08-07: 12 missed statements / 13 partial branches of 3897.** The threshold is **unedited** and
the 90% gate passes.
The drop is concentrated in this pass's own new modules and is **not** a regression elsewhere:

| Module | Uncovered | What it is |
|---|---|---|
| `multipart_reader.py` | 143, 147, 175, 195→exit, 201 | Four **defensive refusals** no test constructs an input for: a part with no `name` at all · a **duplicated** `form_fields` part · the **total-request** cap (as distinct from the per-file cap, which G1 covers) · a `form_fields` part that is valid JSON but **not an object**. All refuse — the safe direction — but all are unasserted. |
| ✅ `routes/submission.py` | ~~**149–150**~~ → **NONE** | ⚠️ **SUPERSEDED 2026-08-13 — CLOSED 2026-08-09. The original row, verbatim:** *"⛔ `except MultipartInvalid → 400` is UNCOVERED at the route. F1–F6 prove the reader refuses; nothing proves the route turns that refusal into WIRE-1's 400 envelope. (The 413 sibling at 147–148 is covered.) §9 step 4 exercises this by hand."* ⚑ **`test_a_MALFORMED_multipart_body_is_a_400_in_the_WIRE1_ENVELOPE` closes it; the module is now 100% (63/63 statements, 12/12 branches).** ⛔ **And this changes what §9 step 4 IS**: it was *the only thing exercising the branch*; it is now an independent live confirmation of a **covered** path — the weaker claim, and the one now made. |
| `upload_storage.py` | 120→119 | The sweep's `is_dir() and startswith(prefix)` filter — the false branch (a stray *file* in the root) is never constructed. |
| `intake/resource_limits.py` | 18, 33–34 | **Windows-unreachable POSIX `setrlimit`** — the same cause as the one new skip. Would be covered in Linux CI. |

⚑ **This is the most actionable output of the reconciliation**: `submission.py:149–150` is a real, named,
one-test gap on a **user-reachable 400 path**, and it is exactly what §9's malformed-upload step observes live.

### 12.7 One further plan-vs-code deviation, found while writing §9

**Step 4.6 said** *"Implement the streaming reader **+ the `Content-Length` fast-reject middleware**."* The
reader shipped; ⛔ **the middleware did not.** `grep -rn "middleware" backend/app/` returns **one comment and no
implementation**, and `main.py` adds none.

⚑ **This costs no tests and is arguably the stronger outcome.** H1's realized form is
`test_the_reader_never_receives_content_length_at_all` — the reader is not merely *independent* of
`Content-Length`, it **never sees it**, which makes stop-gate 4 (*"`Content-Length` treated as a security
control → stop"*) unfalsifiable by construction rather than by assertion. Q13's answer called the middleware
*"a thin fast-reject only… an early cheap 413"*, i.e. an **optimization**, and §4.2 said in terms: *"the
middleware fast-reject is an optimization, NOT the security control."*

⚠️ **Recorded because it is a deviation from an approved plan step, however benign.** The consequence is
operational, not correctness: an oversized upload is refused **mid-stream by the counter** rather than
**pre-stream by the header**, so the client pays some upload bandwidth before the 413. **§9 step 5 observes
exactly this.**
