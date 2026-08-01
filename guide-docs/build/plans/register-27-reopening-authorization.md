# U24 `case-lifecycle` — FOURTH AUTHORIZED REOPENING (request)

**Artifact type**: standalone reopening authorization — **not** an execution plan, **not** a code-gen plan
**Status**: ✅ **APPROVED 2026-08-01 (§6). U24's fourth reopening is authorized as scoped in §3 — four files, six
changes, nothing beyond.** Execution proceeds via a separate code-gen plan, with the reopening as step 0.
Superseded status line, preserved: *"⛔ AWAITING EXPLICIT WRITTEN SIGN-OFF. No code written. No frozen file
touched."*
**Date**: 2026-08-01
**Approved design**: `register-27-remediation-plan.md` — answers **Q1(D)+(A) · Q2(a) · Q3(a) · Q7(a) · Q8(a)**,
ambiguity-check **CLEAN** (§4.1)
**Precedent**: `fix-register-19-plan.md` — U24's third reopening, same shape (design approved standalone, applied as
step 0 of its own execution pass)

---

## 1. What is being requested

Authorization to modify **four files inside the frozen `backend/case_lifecycle/` tree**, to remediate register
**#27 `DUPLICATE-PENDING-RECOMMENDATION-ROWS`** and a **second, more severe defect found during its investigation**
(a terminal `COMMITTED` case silently resurrected to `EVALUATED`), which Q2(a) directs to be split into its own
register item.

**This document authorizes the reopening only.** The execution/code-gen plan is a **separate** artifact, written
**after** this is signed off.

---

## 2. Prior reopenings — this is the FOURTH

Authoritative record: `BUILD-COMPLETION-REPORT.md:198` and `:303`.

| # | Reopening | Reason |
|---|---|---|
| 1 | `list_application_ids()` | no enumeration primitive existed (Scope B wiring, Q1-A) |
| 2 | `memo_from_canonical()` | no memo rehydration existed anywhere in the build |
| 3 | the two-step commit claim | register **#19**'s fix (`fix-register-19-code-gen-plan.md`) |
| **4** | **this request** | register **#27** + the terminal-state breach |

⚑ **Honesty note.** `case_lifecycle` is **NOT** in `test_frozen_untouched.py`'s `FROZEN_UNITS` set — that guard
covers the original eleven units. **U24's frozen status is a project-convention and authorization discipline, not a
mechanically enforced one.** No test will fail if this authorization is exceeded. **This document is the only real
control**, which is why its file list is exhaustive and why anything outside it must come back for a fresh request.

---

## 3. ⛔ FROZEN files this reopening covers — exhaustive

### 3.1 `backend/case_lifecycle/pipeline.py`

**Three changes, all in one file. `DraftOutcome` is defined here (`:42`), so Q8(a) adds no additional frozen file.**

| Change | Where | Authority | Why |
|---|---|---|---|
| **(a)** `submit()` reads the existing application first; if present and progressed beyond `EVALUATED`, return it **unchanged** instead of overwriting | `submit()`, `:79-99` | **Q7(a)** | ⛔ **The root cause.** `put_application`'s upsert writes `state`, so every re-submission resets `DRAFTED`/`COMMITTED` → `EVALUATED`. This is what defeats the re-draft guard *and* what resurrects terminal cases. |
| **(b)** Move the legality check **above** `draft_memo` (`:116`) and have it return a `DraftOutcome` failure instead of raising — using the existing pure `is_legal` rather than `assert_legal` | `draft()`, currently `:138` | **Q1(D) costs (1)+(2)** | ⚑ That guard is **dead code today** — it can never fire, because `submit()` has always already reset the state. Change (a) makes it **reachable for the first time**; without this it would raise, *late*, after paying the full drafting cost (real money under `--real-llm`). |
| **(c)** Add a distinct field to `DraftOutcome` (e.g. `skipped: bool`) so a benign "already drafted" is **structurally** distinguishable from a real drafting failure | `DraftOutcome`, `:38-51` | **Q8(a)** | `succeeded` is `memo is not None` and the only other channel is a prose `failure_reason` — so a routine re-seed would print `FAILED (…)`, training the operator to ignore exactly the line register #18's citation defect hid behind. |

⚑ **(b) follows an existing, tested convention rather than inventing one**: `test_trigger.py:58`
(`test_drafting_an_unknown_application_returns_a_failure_outcome` — *"No exception for a domain miss — an ordinary
`DraftOutcome` (Q4-A)"*) already pins this behaviour, and `pipeline.py:106`'s unknown-application early return is
the same shape.

### 3.2 `backend/case_lifecycle/repository.py`

| Change | Where | Authority | Why |
|---|---|---|---|
| **(d)** Add `ORDER BY` + `LIMIT 1` to the `recommendation_for_application` lookup | `_recommendation_row`, `:145-149` | **Q1(A)** | The query is unordered and unlimited over `application_id`, which has **no uniqueness guarantee** (non-unique index only; PK is `recommendation_id`). The row served is **undefined by SQL semantics**. |

⛔ **`put_application` is NOT touched** — that is the whole point of Q7(a). It must remain a faithful state-writing
upsert, because it is the sole state-writing primitive for `draft()`'s `EVALUATED → DRAFTED` (`:140`),
`_transition`'s `EVALUATED → FAILED` (`:166`), and **register #19's CAS inside both test doubles**.

⚠️ **What (d) does NOT claim.** `recommendation_id` is `f"REC-{application_id}-{uuid4().hex[:8]}"` — a **random**
suffix. `ORDER BY recommendation_id` therefore buys **determinism, not chronology**: a *stable* row, not the
*newest*. It exists to make **pre-existing** duplicate data behave predictably; **change (a) is what stops new
duplicates being created at all.** (d) is hardening, not the fix.

### 3.3 `backend/case_lifecycle/tests/fixtures.py`

| Change | Where | Authority | Why |
|---|---|---|---|
| **(e)** Mirror (d)'s ordering in the in-memory double's `recommendation_for_application` | `:183-189` | **Q3(a)** | The double iterates an insertion-ordered dict and always returns the **first inserted** — **deterministic where Postgres is not**. `:194` claims *"PERSIST-1 is what keeps this fake and `PostgresCaseStore` honest about agreeing"*; **for this method that claim is currently false.** |
| **(f)** New/extended tier-U tests covering (a), (b), (c) | `tests/` | **Q1/Q7/Q8** | New test files under a frozen tree are part of the reopening. |

⛔ **`_swap_state` (`:212-224`) is NOT touched** — Q7(a) leaves `put_application` alone, so register #19's claim
mechanism is unaffected at tier-U. ⚑ Under the rejected Q7(b)/(c) this file **would** have needed a `_swap_state`
rewrite; that is a concrete reason Q7(a) was chosen.

### 3.4 Files touched that are **NOT** frozen — listed for completeness, not authorized here

| File | Change | Frozen? |
|---|---|---|
| `backend/app/tests/factories.py` | same double-parity fix as (e) | **No** — `backend/app/` is the composition root |
| `backend/scripts/seed_demo_cases.py` | print the third state (`skipped, already drafted`) beside `drafted` / `FAILED` | **No** — a script, outside every `--cov` and structural-scan root |
| `backend/scripts/tests/test_seed_demo_cases.py` | cover the skip path | **No** |
| `guide-docs/**` | plan, register (#27 + the new item per Q2(a)), audit, guide-state | **No** |

---

## 4. What this authorization does NOT cover

Anything not listed in §3 requires a **fresh request**. Explicitly excluded:

- ⛔ **No migration, no schema change.** Q4 is **N/A** under Q1(D) — no new column, no UNIQUE constraint, no
  `.sql` file, and therefore **no change to U24's `checksums.json`** and no new entanglement with register **#26**.
- ⛔ **`put_application` is not modified** (§3.2).
- ⛔ **Neither double's `_swap_state` is modified** (§3.3).
- ⛔ **No WIRE-1 change.** R5's 404-vs-409 mapping constrains the design but is not amended.
- ⛔ **No other frozen unit** — `audit_store/`, `outlier_model/`, `common/`, `intake/`, `rules_engine/`,
  `memo_agent_core/` are untouched.
- ⛔ **No deletion of any `pending_recommendation` row from application code.** `repository.py:250` reasons
  load-bearingly that *"a `pending_recommendation` row is never deleted anywhere in this build, so 'absent' is a
  stable fact"* — the basis for `claim_for_commit` disambiguating `NOT_FOUND` from `LOST`, and therefore for R5's
  404 not becoming a 409. ✅ **This design preserves that assumption exactly**: nothing here deletes or replaces a
  row. (Manual cleanup of *existing* duplicates is an operator action, not application behaviour.)
- ⛔ **#27 is not closed by this authorization** — only by the executed fix plus its live verification.

---

## 5. Risk assessment

| Risk | Assessment |
|---|---|
| **Register #19's CAS** | ✅ **Untouched.** The real `_swap_state` issues its own `sa.update()`; the doubles' versions go through `put_application`, which this design does not modify. |
| **Commit boundary (R5)** | ✅ **Unaffected.** `provider.py:41` resolves via `get_recommendation(recommendation_id)` — by primary key. |
| **Existing tests** | ⚑ **No test pins the behaviour being changed.** `IllegalTransition` appears only in `test_states.py` (`:70/:113/:127/:138`), exercising `assert_legal` **directly**, never through `draft()`. Expect **additions**, and a change to `seed()`'s output expectations. |
| **Re-seed workflow** | ⚠️ **Changes deliberately.** A second seed no longer re-drafts an already-drafted case; it **skips and says so**. Accepted knowingly under Q1(D) cost (3). |
| **Blast radius of (c)** | ✅ Small — `DraftOutcome` is referenced outside `pipeline.py` only in a docstring (`test_trigger.py:59`), and the field is **additive**. |
| **Overreach** | ⚠️ **Not mechanically detectable** (§2). Mitigated by §3's exhaustive list and by `git status` review at the execution gate. |

---

## 6. Sign-off

Authorization is requested for **exactly** the four frozen files in §3, for **exactly** changes (a)–(f), on the
design approved in `register-27-remediation-plan.md`.

- [x] **APPROVED** — U24's fourth reopening is authorized as scoped above. Proceed to write the execution/code-gen
      plan as a separate artifact; the reopening is applied as **step 0** of that pass (Q5(a)).
- [ ] **APPROVED WITH CHANGES** — note them here: ______________________
- [ ] **DECLINED** — #27 and the terminal-state item remain open; the design stands as a recorded, unexecuted
      deliverable.

**Signed**: Nidhi Dhyani (approved in writing, this session)  **Date**: 2026-08-01

**Approval text, verbatim**: *"APPROVED — U24's fourth reopening is authorized exactly as scoped in
register-27-reopening-authorization.md §3: the four named files (pipeline.py changes (a)(b)(c), repository.py change
(d), fixtures.py changes (e)(f)), and nothing beyond that list. put_application, both doubles' _swap_state, any
migration/schema change, WIRE-1, and every other frozen unit remain explicitly out of scope per §4."*

### ⚑ Scope clarification recorded at sign-off — the §8 documentation fix is NOT a case_lifecycle file

The approval directs that `not_wired.py:176`'s *"third"* → *"second"* correction be included, on the stated rationale
*"while other case_lifecycle files are already being touched under this authorization."*

⛔ **That rationale does not hold, and the correction does not rely on it.** `not_wired.py` lives at
**`backend/app/routes/not_wired.py`** — the **composition root**, not `backend/case_lifecycle/`. It is **not a
frozen file** and **not in §3's list**, so it needs **no reopening authority at all**. It is included in the
execution pass as an ordinary non-frozen edit (the §3.4 category), and **§3's four-file list is unchanged by it**.

Recorded rather than silently accepted, because a reopening's file list must never expand by inference.

⛔ **No file under `backend/case_lifecycle/` is touched until the execution plan is separately reviewed.**
