# Register #19 — CODE GENERATION PLAN (Part 1: the PLAN. No code.)

**Stage**: POST-BUILD → register-item remediation · **U24's THIRD authorized reopening** (Q2-b)
**Status**: 🟡 **PLAN ONLY — NO CODE WRITTEN.** Stopped at the plan-file gate.
**Date**: 2026-07-21
**Scoping plan of record**: `fix-register-19-plan.md` — Q1–Q5 + Q3.1/Q4.1/Q5.1 + A1/A2/A2.1/A-iii.1 all answered;
§6 round-1 ambiguity-check, §7 round-2.
**Discipline**: TDD, **leaf-first**, ambiguity-checked — the same as every prior pass in this build.

---

## ⚠️ 0. ONE ITEM REQUIRES AUTHORIZATION BEFORE IMPLEMENTATION BEGINS

> ### B1 — `INT-FAITHFUL-1` must be NARROWED (`app/tests/test_no_write_route.py`)
>
> That file's thesis — ***"every write goes through the frozen `DecisionCommitService`"*** — **becomes false as
> written** once R5 claims and finalizes pending state. The narrowed guarantee (§7 of the scoping plan):
>
> > **Every `audit_record` write goes through the frozen `DecisionCommitService`; every *pending-state* write goes
> > through U24's own methods, and `backend/app/` still opens no transaction and writes no row itself.**
>
> **Strictly more specific, not more permissive.** Violates **no standing hold** — it is `backend/app/`'s own test,
> **not** a frozen-23 unit test and **not** U23's frozen `NFR-DEP-ROUTES-1`. **Flagged in advance, per the ADAPTER-1
> precedent — not left to be discovered in a diff.** **Step 8 below does not execute without this sign-off.**

**Everything else in this plan is determinate** and follows from the answered questions.

---

## 1. Change inventory

| # | File | Kind | Frozen? |
|---|---|---|---|
| 1 | `backend/case_lifecycle/states.py` | `CaseState.COMMITTING` · `CommitClaimResult` · `LEGAL_TRANSITIONS` · docstrings | U24 — **reopened** |
| 2 | `backend/case_lifecycle/store.py` | 3 new `CaseStore` Protocol methods | U24 — **reopened** |
| 3 | `backend/case_lifecycle/repository.py` | `PostgresCaseStore` impl of the 3 methods | U24 — **reopened** |
| 4 | `backend/case_lifecycle/tests/fixtures.py` | `InMemoryCaseStore` impl of the 3 methods | U24 test support |
| 5 | `backend/case_lifecycle/tests/test_states.py` | 2 exact-set edits (§7 (iii)) | U24 test |
| 6 | `backend/case_lifecycle/tests/test_project.py` | 1 parametrize row (§7 (iii)) | U24 test |
| 7 | `backend/case_lifecycle/tests/test_claim.py` | **NEW** — tier-U CLAIM-1 | U24 test |
| 8 | `backend/case_lifecycle/tests/test_claim_integration.py` | **NEW** — tier-I CLAIM-CONCURRENT-1 | U24 test |
| 9 | `backend/app/routes/not_wired.py` | R5 handler: claim → commit → finalize; 3-way mapping; recovery | composition root |
| 10 | `backend/app/tests/test_not_wired.py` (or a new sibling) | R5 tier-U tests incl. A4's 3 recovery tests | composition root test |
| 11 | `backend/app/tests/test_no_write_route.py` | **B1 narrowing** — ⚠️ gated on §0 | composition root test |
| 12 | `backend/scripts/reconcile_committing_cases.py` | **NEW** — read-only reconciliation | out-of-band script |

**⛔ NOT TOUCHED, verified**: `backend/audit_store/**` (incl. `commit_service.py`) · every other frozen-23 unit ·
`guide-docs/build/wire-1/api-contract.md` · `not_wired.py`'s **filename** · U23's frozen `NFR-DEP-ROUTES-1` ·
the `audit_store` Docker guard · `dependencies.py`'s engine bindings · **no new route**.

---

## 2. Design decisions already settled (do not re-derive)

| Decision | Value | Source |
|---|---|---|
| Transition shape | **two-step claim**: CAS `drafted→committing` **before** `commit()`; `committing→committed` **after** | Q1(c) |
| Method key | **`recommendation_id`** — U24 joins internally | A2 |
| Return type | **`CommitClaimResult`** = `WON` / `LOST` / `NOT_FOUND` | A2.1 |
| `TERMINAL_STATES` | **UNCHANGED** — `frozenset({COMMITTED, FAILED})` | A1 |
| `DRAFTED→COMMITTED` | **REMOVED** from `LEGAL_TRANSITIONS` | §6 check (ii) |
| Enum placement | **`states.py`** — keeps `EXPECTED_PRODUCTION_MODULES` at **8** | §7 check (i) |
| `case_to_memo_view_state` | **NO logic change** — the `else` branch already yields `"pending"`; **docstring only** | §7 check (iii) Correction 2 |
| Transaction ownership | each new method opens its **own `atomic()` internally**; `backend/app/` opens none | §7 B1(1) |
| Reconciliation lookup | `browse_history(None)` + a membership set | A-iii.1 |
| Test tiers | tier-U + tier-I concurrency in `case_lifecycle/tests/` | Q5 / Q5.1 |

**⚠️ Naming constraints, binding** — no U24 production identifier may contain the substring **`authorize`**
(so **not** `authorized` / `unauthorized`), `audit_record`, or `RBAC_COMMIT`: `test_commitbound.py:46` uses a plain
substring test, **not** word-boundary. Method names must also not contain the literal **`.commit(`** pattern in a
way that would add a caller to `test_no_write_route.py`'s `commit_callers` set — `claim_for_commit(` is safe.

---

## 3. TDD, leaf-first execution order

Leaf-first = **`states.py` → `store.py` → `repository.py`/fixtures → R5 → script**. Each step is **RED → GREEN**,
tests written before implementation, suite green before the next step.

### Step 1 — `states.py` (the leaf)

- [ ] **RED**: extend `test_states.py`
      - `test_the_five_states_plus_the_internal_failed_state_exist` → add `"committing"`, **rename** the test
        (the "five states" name is now wrong)
      - `test_the_legal_table_is_the_expected_happy_path_plus_failure` → **+3 tuples, −`(DRAFTED, COMMITTED)`**
      - **NEW** `test_the_direct_drafted_to_committed_edge_is_gone` — ⚑ asserts the one-step transition the fix
        replaces is **no longer expressible**, making the two-step guarantee **structural**
      - **NEW** `test_committing_is_not_terminal` — `COMMITTING not in TERMINAL_STATES`
      - **NEW** `test_committed_is_reachable_only_from_committing` — derive predecessors from `LEGAL_TRANSITIONS`
      - **NEW** `test_terminal_states_is_unchanged` — pins `{COMMITTED, FAILED}` **explicitly**, so A1's decision is
        recorded as a test rather than a memory
- [ ] **RED**: `test_project.py` → add `(CaseState.COMMITTING, "pending")` to the parametrize table
- [ ] **GREEN**: add `CaseState.COMMITTING = "committing"`; add the 3 tuples; **remove** `(DRAFTED, COMMITTED)`;
      add `CommitClaimResult(str, Enum)` = `WON`/`LOST`/`NOT_FOUND`; **`TERMINAL_STATES` untouched**;
      update the module docstring + `case_to_memo_view_state`'s docstring (register **#14 widening**)
- [ ] **VERIFY (no edit)**: the STATE-2 complement sweep and its length assertion **self-adjust** — 7×7=49, 41+8=49

> ⚑ **`case_to_memo_view_state`'s BODY is not edited.** `return "ready" if ... is DRAFTED else "pending"` already
> maps `COMMITTING → "pending"`, and the `Literal` is already correct. **Docstring only.**

### Step 2 — `store.py` (the Protocol)

- [ ] **GREEN** (Protocol-only, no test of its own — exercised through both implementations):

```
claim_for_commit(recommendation_id: str) -> CommitClaimResult   # CAS drafted -> committing
finalize_commit(recommendation_id: str) -> None                 # committing -> committed
release_claim(recommendation_id: str) -> None                   # committing -> drafted (recovery)
```

- [ ] Docstrings must state: **keyed by `recommendation_id`** (U24 joins internally, A2); **each opens its own
      `atomic()`**; the CAS guarantee is **database-level row serialization, not application timing**

### Step 3 — `repository.py` (`PostgresCaseStore`) + `fixtures.py` (`InMemoryCaseStore`)

- [ ] **RED**: `test_claim.py` (**NEW**, tier-U, target **CLAIM-1**) against `InMemoryCaseStore`
      — WON from `drafted` · LOST from `committing` · LOST from `committed` · LOST from `evaluated`/`failed` ·
      `NOT_FOUND` for an unknown id · finalize moves `committing→committed` · release moves `committing→drafted`
      and the case is **re-claimable** · illegal transitions still raise
- [ ] **GREEN — `PostgresCaseStore`**: single-statement scalar-subquery `UPDATE` (§7 (ii)); `rowcount==1` ⇒ `WON`;
      on `rowcount==0`, an **existence-only** `SELECT 1` disambiguates `LOST` vs `NOT_FOUND`; **both inside one
      `atomic()` opened by the method**
- [ ] **GREEN — `InMemoryCaseStore`**: mirror the semantics; **buffer-and-flush** like its siblings so atomicity
      stays non-vacuous
- [ ] ⚑ **ADAPTER-1 unaffected** — these methods perform **no canonicalization**; `repository.py`'s positive
      "contains no canonicalization call at all" assertion **still holds**

> ⚑ **NO MIGRATION FILE.** The join needs no new column and no new index — `recommendation_id` is already the PK and
> the FK already exists. U24's migrations are **forward-only and immutable once published**; adding a `0002_*.sql`
> here would be **wrong, not merely unnecessary**.

### Step 4 — tier-I concurrency (**CLAIM-CONCURRENT-1**)

- [ ] **NEW** `case_lifecycle/tests/test_claim_integration.py`, beside PERSIST-1 (Q5.1), **reusing
      `_docker_available()` verbatim** — the ping-inside-the-fixture-body pattern, **the reason U24's tier-I tests
      SKIP CLEANLY rather than ERROR**
- [ ] **3 tests**: two real concurrent connections both claiming the same `drafted` row → **exactly one WON, one
      LOST** · a claim against a `committed` row → `LOST` · a claim against an absent id → `NOT_FOUND`
- [ ] ⚑ **SKIP-COUNT PREDICTION, STATED IN ADVANCE** (the U24 `+5` precedent): PERSIST-1 currently contributes
      **6** cleanly-skipping tier-I tests. **Docker-absent skips: 37 → 40 (+3). ERRORS: 5 → 5, UNCHANGED.** ⛔ **Any
      deviation is a finding to report, not to absorb.**

### Step 5 — R5's handler (`app/routes/not_wired.py`)

- [ ] **RED**: R5 tier-U tests — `WON` → 200 + finalize called · `LOST` → **409** + **`commit()` never invoked**
      (spy assertion — **this is the duplicate-prevention tooth at tier-U**) · `NOT_FOUND` → **404** ·
      **plus A4's three recovery tests** (below)
- [ ] **GREEN** — handler shape:

```
1. closed-enum wire-shape check on body.action              -> 422        (UNCHANGED)
2. result = store.claim_for_commit(recommendation_id)
   NOT_FOUND -> 404   |   LOST -> 409 commit_conflict (commit() NEVER called)   |   WON -> continue
3. try:      committed = service.commit(...)                                (UNCHANGED call)
   except:   release_claim(...) FIRST, then raise the SAME WireError as today  (403/404/409)
4. store.finalize_commit(recommendation_id)
5. return committed.model_dump(mode="json")                                 (UNCHANGED)
```

- [ ] `store: CaseStore = Depends(get_case_store)` added — **`get_case_store` already exists**; **no new provider,
      no `dependencies.py` change**
- [ ] ⛔ **The route calls NO `atomic()` and NO `.insert(`** — B1(1); every transaction is inside U24
- [ ] ⛔ **The route re-implements no gate and no authz** — the frozen `_gate` and AUTHZ-1 still run inside
      `commit()`, independently, exactly as today
- [ ] **Rewrite the register-#19 docstring** at `not_wired.py:209` — from *"KNOWN DEFECT"* to what is now true,
      naming the surviving `COMMITTING` window and its new register item

**A4's three recovery tests — each asserts the case returns to `drafted` and is re-committable:**

| # | Branch | Trigger |
|---|---|---|
| 1 | `CommitRejected` → **409** | **blank-reason override** — a routine user error U8 is built around |
| 2 | `CommitRejected` → **409** | a bad action passing R5's wire-check but rejected by the frozen `_gate` |
| 3 | `UnauthorizedCommit` → **403** | a caller passing `require_commit` but rejected by AUTHZ-1 |

- [ ] **Plus**: a **failure-tolerant recovery** test — a `release_claim` that itself raises **must not mask** the
      original rejection (a 409 must not surface as a 500)

### Step 6 — the reconciliation script

- [ ] **NEW** `backend/scripts/reconcile_committing_cases.py` — **READ-ONLY**, reports; automates nothing
- [ ] Engines built from `get_settings()` **directly**, mirroring `seed_demo_cases.py:218` — **does NOT import
      `dependencies.py`**, keeping FastAPI's `Depends` graph out of an out-of-band script
- [ ] Owner engine (`DATABASE_URL`) for pending state — per register **#20**, the pending tables carry no explicit
      grants. **No grant is invented; #20 stays open and untouched.**
- [ ] `AUDIT_READER_URL` for the audit read, via `AuditService.browse_history(None)` → **one membership set** of
      `recommendation_id` → membership-test each stuck case
- [ ] **Recommends, does not perform**: `recommendation_id` present ⇒ advance to `COMMITTED`; absent ⇒ revert to
      `DRAFTED`
- [ ] ⚑ **Docstring must state the performance shape honestly** (A-iii.1): *`browse_history(None)` loads the **full
      decision history** to build one membership set — a disclosed cost of reusing the existing frozen surface
      rather than adding a `recommendation_id` lookup to a frozen unit. Acceptable because this is a low-volume,
      out-of-band reconciliation script and **not a request-path route**.*
- [ ] ⛔ **NO raw SQL** — `backend/scripts/` is outside both structural-scan roots, so a hand-rolled query there
      would be **structurally invisible to every guard in the build**

### Step 7 — full-suite verification

- [ ] `pytest backend` — expect **1492 + N passed / 0 failed / 40 skipped / 5 errors**
- [ ] ⛔ **The 5 `audit_store` Docker errors must remain EXACTLY 5, by name** — a standing hold
- [ ] Coverage gate **≥90%** held (currently 99.87%)
- [ ] `EXPECTED_PRODUCTION_MODULES` **still 8** — no new module
- [ ] `python -m compileall` over `case_lifecycle` + `app` + `scripts` exits 0

### Step 8 — ⚠️ B1 (GATED ON §0 SIGN-OFF)

- [ ] Narrow `INT-FAITHFUL-1` in `app/tests/test_no_write_route.py` — thesis/title/header updated, **both halves
      kept falsifiable**, narrowing disclosed in the code summary

### Step 9 — documentation

- [ ] `guide-docs/build/case-lifecycle/code/code-summary.md` — the third reopening's delta
- [ ] **Register #19 → NARROWED, NOT CLOSED** (Q4). Claim of record (Q3.1-i): *"WIRE-1 §4's already-committed 409 is
      now genuinely enforced, including under concurrent access."*
- [ ] **NEW register item** for the surviving `COMMITTING` crash window, with the reconciliation script as its
      mitigation and its own owner
- [ ] **Register #14 widened** — `COMMITTING` joins `failed` as an internal state with no wire representation
- [ ] `audit.md` + `guide-state.md` — completion entries with live figures

---

## 4. What this fix will and will not guarantee — the honest claim

**WILL**: ✅ **Duplicate `AuditRecord`s are ELIMINATED, not narrowed** — the guarantee is a Postgres row-level write
lock, proven at tier-I under real concurrency · ✅ WIRE-1 §4's already-committed **409 genuinely enforced** · ✅ a
committed case no longer reports `ready` forever · ✅ ordinary rejections (403/404/409) leave the case
**re-committable**.

**WILL NOT**: ⛔ **achieve cross-store atomicity.** `DecisionCommitService` and `CaseStore` remain **two
transactional boundaries on two engines**, and merging them would require editing a frozen unit. **A crash between
the CAS and the audit write leaves the case in `COMMITTING`** — explicit, non-terminal, detectable, and reconcilable,
but **real**. ⚑ **This is a narrow, disclosed window replacing an unbounded, always-reachable defect. It is a genuine
improvement and it is NOT perfect atomicity, and the closing documentation must say exactly that** — the same
discipline as Q11-A's deliberately-narrower *"exercisable after running the seed script."*

---

## 5. Holds — all upheld

`commit_service.py` + every frozen-23 unit's internals **untouched** · WIRE-1's text **not amended** ·
`not_wired.py` **not renamed** (register #13 stays open) · U23's frozen test **not edited** · `audit_store`
Docker-guard gap **untouched (5 stays 5)** · **tier-B not authorized** · **no new route** · register **#20** left
open and undecided.

---

**STOPPED AT THE PLAN-FILE GATE. No code written.** Implementation begins only after this plan is approved **and**
**B1 (§0)** is signed off.
