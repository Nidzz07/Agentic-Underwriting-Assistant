# Register #27 — Execution / Code-Gen Plan

**Stage**: POST-BUILD → execution plan (Part 1: planning). **No code written yet.**
**Status**: ⛔ **PLAN-FILE GATE — awaiting review before any implementation.**
**Date**: 2026-08-01
**Approved design**: `register-27-remediation-plan.md` (Q1(D)+(A) · Q2(a) · Q3(a) · Q4 N/A · Q5(a) · Q6(a) · Q7(a) · Q8(a); ambiguity-check CLEAN §4.1)
**Authorization**: `register-27-reopening-authorization.md` — **APPROVED 2026-08-01**, U24's **fourth** reopening,
four frozen files, changes (a)–(f), nothing beyond

---

## 1. Baselines — confirm before touching anything

| Suite | Baseline |
|---|---|
| Backend | **1636 passed · 0 failed · 43 skipped · 5 errors · 99.63%** (commit `d5c2c41`) |
| Frontend | **723 / 147** — ⚑ **not touched by this pass at all** and must end unchanged |

The 5 errors are Docker-absence collection errors in `audit_store/tests/test_pg_integration.py`. The 43 skips
include U24's own Docker-gated tier-I tests, which **`pytest.skip()`** cleanly (`test_persist_integration.py:47`).

---

## 2. Predicted deltas — stated in advance, per change

**+13 tests written. Locally: +12 passed, +1 skipped** (one tier-I test skips without Docker).

**Predicted final: 1648 passed · 0 failed · 44 skipped · 5 errors.**

| Change | Tests | Δ passed | Δ skipped |
|---|---|---|---|
| **(a)** `submit()` guard | A1–A4 | +4 | 0 |
| **(b)** relocated/softened `draft()` guard | B1–B2 | +2 | 0 |
| **(c)** `DraftOutcome.skipped` | C1–C2 | +2 | 0 |
| **(d)** `ORDER BY` + `LIMIT 1` | D1 (tier-U), **D2 (tier-I)** | +1 | **+1** |
| **(e)** double parity | E1 | +1 | 0 |
| seed script (non-frozen) | S1–S2 | +2 | 0 |
| **Totals** | **13** | **+12 → 1648** | **+1 → 44** |

⚑ **Predicted existing-test changes: NONE.** Verified by inspection — every `.submit()` call site in the suite
submits a **fresh** application id once per test, so (a)'s guard never fires for them; every `draft()` call drafts
once, so (b) never fires; (c) is an **additive field with a default**; (d)/(e) run against single-row fixtures. ⚑
**And no existing test asserts the seed script's printed output** (no `capsys` anywhere in
`test_seed_demo_cases.py`), so the new third state breaks nothing. **This is a falsifiable claim — stop-gate 2.**

---

## 3. Execution order — RED before GREEN

**Step 0 is the reopening itself** (Q5(a)): record in `audit.md` that the authorized fourth reopening is now being
applied, naming the four files. No code in step 0.

| # | Step | File | RED first? | Δ |
|---|---|---|---|---|
| 0 | **Apply the authorized reopening** — log it; no code | docs | n/a | 0 |
| 1 | Confirm both baselines before touching anything | — | n/a | 0 |
| 2 | **A1** `submit on a DRAFTED application returns it unchanged` | `case_lifecycle/tests/` | ✅ RED | +1 |
| 3 | **A2** `submit does NOT resurrect a COMMITTED terminal application` ⚑ *the breach* | `case_lifecycle/tests/` | ✅ RED | +1 |
| 4 | **A3** `submit on a FRESH application still creates it at EVALUATED` ⚠️ *vacuous on arrival* | `case_lifecycle/tests/` | ⚠️ see §4 | +1 |
| 5 | **A4** `submit on an EVALUATED application still refreshes its report` | `case_lifecycle/tests/` | ⚠️ see §4 | +1 |
| 6 | **Change (a)** — `submit()` reads the existing application; if past `EVALUATED`, return unchanged | **`pipeline.py`** | → greens A1/A2 | 0 |
| 7 | **B1** `drafting an already-drafted case returns a failure outcome, does NOT raise` | `case_lifecycle/tests/` | ✅ RED | +1 |
| 8 | **B2** `the refusal happens BEFORE draft_memo is called` (spy seam, `calls == []`) | `case_lifecycle/tests/` | ✅ RED | +1 |
| 9 | **Change (b)** — move the legality check above `draft_memo`; use `is_legal`; return a `DraftOutcome` | **`pipeline.py`** | → greens B1/B2 | 0 |
| 10 | **C1** `a refusal is marked skipped` · **C2** `a REAL drafting failure is NOT marked skipped` | `case_lifecycle/tests/` | ✅ RED | +2 |
| 11 | **Change (c)** — add the discriminating field to `DraftOutcome` | **`pipeline.py`** | → greens C1/C2 | 0 |
| 12 | **D1** `the lookup SQL carries ORDER BY + LIMIT 1` (tier-U, compiled-SQL assertion, no DB) | `case_lifecycle/tests/` | ✅ RED | +1 |
| 13 | **D2** `with duplicate rows, repeated reads return the SAME row` (**tier-I, Docker-gated → SKIPS locally**) | `test_persist_integration.py` | ✅ RED *(in CI)* | +1 skip |
| 14 | **Change (d)** — `ORDER BY recommendation_id` + `LIMIT 1` on `_recommendation_row` | **`repository.py`** | → greens D1 | 0 |
| 15 | **E1** `the in-memory double resolves the SAME row the shim would` | `case_lifecycle/tests/` | ✅ RED | +1 |
| 16 | **Change (e)** — mirror (d)'s ordering in **both** doubles | **`fixtures.py`** + `app/tests/factories.py` | → greens E1 | 0 |
| 17 | **S1** `seed reports a skipped case distinctly` · **S2** `re-seeding creates no second recommendation` | `scripts/tests/` | ✅ RED | +2 |
| 18 | **Seed script** — print the third state beside `drafted` / `FAILED` | `seed_demo_cases.py` | → greens S1/S2 | 0 |
| 19 | Full backend suite; confirm **1648 / 0 / 44 / 5**, coverage ≥ threshold; **frontend re-run, expect 723** | — | n/a | — |
| 20 | **Open register #28** for the terminal-state breach (Q2(a)) | `BUILD-COMPLETION-REPORT.md` | n/a | 0 |
| 21 | **Doc correction** — `not_wired.py:176` *"third"* → *"second"*, supersede-not-rewrite | `app/routes/not_wired.py` | n/a | 0 |
| 22 | **Manual verification — USER-RUN** (§6) | — | n/a | — |
| 23 | Docs: `guide-state.md` + `audit.md` — **only after §6 reports back** | docs | n/a | — |

**Frozen files touched: 3** — `pipeline.py`, `repository.py`, `case_lifecycle/tests/fixtures.py` (+ new test files
under `case_lifecycle/tests/`, which change (f) covers). **Non-frozen**: `app/tests/factories.py`,
`seed_demo_cases.py` + its tests, `not_wired.py`, docs. ⛔ **No migration. No WIRE-1. No other frozen unit.**

---

## 4. ⚠️ Two tests are VACUOUS ON ARRIVAL — how their RED is demonstrated

**A3 and A4 pin *current* behaviour** (a fresh submit still works; an `EVALUATED` submit still refreshes), so they
pass before change (a) exists. That is stop-gate 1 territory, and the project's established remedy applies —
**observe RED by temporarily inverting the implementing change, then restore** (the override pass's T1 precedent,
re-used for the outlier pass's T1 and T6).

* **A3** — after (a) lands, temporarily make the guard unconditional (refuse *every* submit). A3 must fail. Restore.
* **A4** — after (a) lands, temporarily widen the guard to also refuse `EVALUATED`. A4 must fail. Restore.

⚑ **Both RED observations must be seen on screen and reported, not asserted.** If either cannot be made to fail, the
test is not pinning what it claims and must be rewritten.

---

## 5. Named stop-gates — halt and report, do not work around

1. **Any of A1–E1 / S1–S2 green on arrival** → vacuous. ⚠️ **Known: A3 and A4 are** — handled per §4. Any *other*
   test passing on arrival is a stop.
2. ⚑ **ANY existing test changes state.** §2 predicts **zero**. If one moves, the analysis is wrong — **stop, and do
   not adjust the test.**
3. **Backend ≠ 1648 / 0 / 44 / 5.** Report the corrected figure **with its cause** before proceeding. **Never trim
   or reshape tests to hit the prediction** (the 712→716 and the outlier pass's +6→+21 precedents).
4. **Frontend ≠ 723.** This pass must not touch it.
5. **Coverage threshold weakened, or any threshold number edited.** Forbidden.
6. ⛔ **Any file outside the authorization's §3 list appears in `git status` under `backend/case_lifecycle/`.** The
   authorized set is `pipeline.py`, `repository.py`, `tests/fixtures.py`, and new files under `tests/`. ⚑ **No test
   enforces this** (`case_lifecycle` is absent from `test_frozen_untouched.py`'s `FROZEN_UNITS`), so it is checked
   by `git status` review — the authorization is the only control.
7. **`put_application` appears in the diff.** ⛔ Explicitly out of scope (§4 of the authorization) — its upsert must
   remain state-writing or three legal transitions break.
8. **Either double's `_swap_state` appears in the diff.** ⛔ Out of scope — register #19's tier-U coverage depends
   on it routing through `put_application` unchanged.
9. **Any `.sql` file or `checksums.json` appears in the diff.** ⛔ Q4 is N/A — no schema change, no new
   entanglement with register #26.
10. **Any `pending_recommendation` DELETE appears in application code.** ⛔ `repository.py:250`'s never-deleted
    assumption is what keeps R5's **404** from becoming a **409**.
11. **WIRE-1's `api-contract.md` appears in `git status`.** Stop.
12. **Any commit.** Not authorized in this pass.

---

## 6. Manual verification — USER-RUN (Q6(a) in full)

**Preconditions**: local Postgres up, migrations applied.

1. **Reset the pending tables** (FK order):
   ```sql
   DELETE FROM pending_recommendation;
   DELETE FROM pending_application;
   ```
   ⛔ **Do NOT drop the database** — `0002_grants.sql`'s un-guarded `CREATE ROLE` would fail on re-run (roles are
   cluster-level and survive a drop), and dropping destroys the override pass's `AuditRecord a7b67ca8-…`.
2. **Seed three times in sequence**: `python -m backend.scripts.seed_demo_cases --cases 3`, ×3.
   * Run 1: cases drafted normally.
   * Runs 2 and 3: ⚑ **must report `skipped (already drafted)`** — **not** `FAILED`, and **not** a traceback.
3. ⚑ **No accumulation**:
   ```sql
   SELECT application_id, COUNT(*) FROM pending_recommendation GROUP BY application_id ORDER BY 1;
   ```
   **Expect exactly 1 per application.** Any count > 1 → **blocking**.
4. **R4 / R2 resolve the intended row**: `curl GET /applications/DEMO-0001/memo` and `GET /applications`; the
   `recommendation_id` served matches the single row in `psql`.
5. ⛔ **The terminal-state breach must NOT reproduce** — the check with real audit weight:
   * commit a case through R5 so it reaches `committed`;
   * re-run the seed;
   * ```sql
     SELECT application_id, state FROM pending_application WHERE application_id = 'DEMO-0001';
     ```
   * **Expect `committed`, still.** A value of `evaluated` means the breach survives → **blocking**.
6. **Register #19 still holds**: a commit attempt on an already-committed recommendation returns **409**; an unknown
   `recommendation_id` returns **404**. (§1.5's `NOT_FOUND`-vs-`LOST` disambiguation intact.)

**Stop-gate**: any deviation in steps 2–6 → **stop and report** before any doc update or commit.

---

## 7. Register work in this pass (step 20)

**Open #28** for the terminal-state breach, per **Q2(a)** — classified **more severely** than #27, because it
permits an **illegal write to a terminal case's state** rather than an ambiguous read:

* **What**: `pipeline.submit()` overwrote an existing application's `state` unconditionally (via
  `put_application`'s upsert), so re-submitting a `COMMITTED` case silently reset it to `EVALUATED`, making it
  re-draftable after it had already been committed to the audit trail.
* **Evidence**: executed 2026-08-01 — `COMMITTED` → re-submit → `EVALUATED`.
* **Why #27 didn't cover it**: #27 is a **read-resolution ambiguity**; this is a **write-side state-machine
  breach**. Same root cause, different character and severity.
* ⚑ **Also record**: `TERMINAL_STATES` is referenced **only by tests about itself** — **no production code path
  consults it**. That is the general weakness; #28's fix (change (a)) closes the one reachable path, **not** the
  general hole. Do not claim otherwise.
* **Status at open**: opened **and closed in the same pass** — permissible only because the fix and its live
  verification (§6 step 5) both land here. If §6 step 5 is not run, **#28 stays open**.

---

## 8. Holds for this pass

| Hold | Commitment |
|---|---|
| Frozen files touched | **Exactly 3** + new tests under `case_lifecycle/tests/` — the authorized §3 set, nothing more |
| `put_application` | ⛔ **Untouched** |
| Either double's `_swap_state` | ⛔ **Untouched** |
| Migration / schema | ⛔ **None** — Q4 N/A |
| WIRE-1 | ⛔ **Untouched** |
| Frontend | ⛔ **Untouched**, must end at 723 |
| Commit | ⛔ **Not authorized in this pass** |

---

## 9. What this pass will and will not deliver

**Will**: stop duplicate `pending_recommendation` rows being created; make the existing lookup deterministic for
data that already has duplicates; close the terminal-state breach on its one reachable path; make the seed script
re-runnable with an honest third outcome; and remove the test-double blindness that let this class of defect reach
production unseen.

**Will not**: close the *general* `TERMINAL_STATES`-is-unenforced hole (§7) · make `ORDER BY recommendation_id`
mean *"newest"* — the id carries a **random** uuid suffix, so it buys determinism, **not** chronology · clean up
**existing** duplicate rows in anyone's database (that is an operator action) · discharge **#2**, **#26**, or
#17's deferred mount pass.
