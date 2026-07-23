# Register Item #19 — `COMMITTED-TRANSITION-NEVER-PERFORMED` (G2) · SCOPING PLAN

**Stage**: POST-BUILD → register-item remediation · the first work started after **SCOPE B CLOSED**
**Status**: 🟡 **SCOPING / PLANNING ONLY — NO CODE GENERATED.** Stopped at the plan-file gate.
**Date**: 2026-07-21T11:17:26Z
**Origin**: register item **#19**, opened by the **Scope B in-place composition-root wiring pass**
(`guide-docs/build/composition-root/scope-b-wiring-summary.md` §2 G2, §5, §8) and deliberately **not fixed there**
under **Q6d-ii** — *"the fix straddles the commit boundary (COMMITBOUND-1), sits outside the frozen service's
transaction, and must not be folded into a wiring pass as a convenience."*
**Owner recorded in the register**: **U24 + `audit-store`, needing its own commit-boundary (COMMITBOUND-1) review.**
This pass is that review, begun.

**Register severity, quoted, not softened**: *"⛔ **THE MOST SERIOUS OPEN ITEM.** Non-blocking for the wiring's
correctness, but **double-commit is a genuine BFSI-relevant defect** and must be treated as such."*

---

## 0. What this document is and is not

* **IS**: a scoping plan. Ground truth, the design tension, and **five open questions** for the user to answer.
* **IS NOT**: a fix, a design, or an authorization. **No code is generated. No unit is reopened.** Whether a
  reopening is even required is **Q2**, and the answer is the user's.

**Every `[Answer]` tag below is BLANK. None is pre-filled.** Recommendations are given where grounded and are
explicitly marked as recommendations, never as decisions.

---

## 1. Ground truth — re-established from disk, not from any summary

Four checkpoints were re-verified against the actual current files. **All four confirm the gap exactly as
disclosed.** One divergence from the task brief was found and is reported in §1.5 rather than absorbed.

### 1.1 `backend/case_lifecycle/states.py` — ✅ CONFIRMED

| Property | On disk |
|---|---|
| `(DRAFTED, COMMITTED)` legal | ✅ `LEGAL_TRANSITIONS` L52-60 |
| `COMMITTED` terminal | ✅ `TERMINAL_STATES` L63 |
| Any code performing it | ❌ **NONE** |

A repo-wide re-scan for `COMMITTED` across `backend/**/*.py` returns **11 hits, of which ZERO are a production
transition**:

| Location | What it is |
|---|---|
| `states.py:47 / :58 / :63` | the enum member · the legal tuple · the terminal set — **declaration only** |
| `tests/fixtures.py:255 / :258` | `COMMITTED` appearing **only inside the *illegal*-transition collection** |
| `tests/test_states.py:43 / :82 / :84` | asserts the tuple **is** legal · asserts an illegal skip raises |
| `tests/test_project.py:41` | asserts `COMMITTED` projects to `"pending"` on the wire |
| `app/routes/not_wired.py:209` | ⚑ **the register-#19 disclosure docstring itself** |

**The gap stands exactly as described. Nothing on disk contradicts it.**

### 1.2 `pipeline.py` · `provider.py` · `store.py` — ✅ CONFIRMED, plus two load-bearing finds

**`CaseStore` Protocol (`store.py`), as it exists today:**
`atomic()` · `put_application` · `get_application` · `put_recommendation` · `get_recommendation` ·
`recommendation_for_application` · `list_application_ids()` *(added by reopening #1)*.

**`CasePipeline` (`pipeline.py`)**: `submit()` · `draft()` · `read()` · **private `_transition(application, dst)`**
(L163). ⚑ `_transition` already performs **exactly the shape a commit transition needs** — `assert_legal` →
`atomic()` → `put_application` with a rebuilt aggregate. But it is **private**, and **`CasePipeline` is deliberately
NEVER constructed in the composition root** (`dependencies.py:112-117`, Scope B Q3-D — *"keeping the pipeline out
means the five-unit LLM-bearing composition never enters the request path at all"*). **R5 cannot reach it.**

**`PendingCommitContextProvider` (`provider.py`)**: `get(recommendation_id) -> CommitContext`. **Assembly inputs
only.** Its return type makes *"the provider committed something"* structurally unrepresentable — a deliberate
P-CASE-3 property. It performs no authz and no write.

> ### ⚑ FIND 1 — `put_application` is an UNCONDITIONAL UPSERT
> `PostgresCaseStore.put_application` (`repository.py:82-105`) issues
> `insert(...).on_conflict_do_update(index_elements=["application_id"], set_={"state": ..., ...})`.
> **A state change IS expressible through the existing Protocol surface** — `get_application`, rebuild with the new
> state, `put_application` inside `atomic()`. Note also that `set_` **excludes** `profile_canonical` /
> `profile_content_hash`, so a state-only write **preserves the profile** rather than rewriting it.
> ⚠️ **But the upsert is UNCONDITIONAL — it carries NO compare-and-swap semantics.** It overwrites whatever state is
> there, whoever wrote it, whenever. This is the hinge of **Q1(b)** and **Q2**.

> ### ⚑ FIND 2 — READS DO NOT PARTICIPATE IN `atomic()` (the decisive one)
> `PostgresCaseStore.get_application` (`repository.py:107-113`) opens **`self._engine.connect()` — a FRESH
> connection** — and never touches `self._conn`, the transaction handle `atomic()` sets. Only `_execute` (writes)
> requires `self._conn`; the docstring on `list_application_ids` confirms the rule verbatim: *"the
> `_execute`-inside-`atomic()` discipline governs **WRITES only**."*
>
> **Consequence, and it is load-bearing:** a `get_application` → check → `put_application` sequence written *inside*
> `with store.atomic():` is **NOT atomic**. The read happens on a different connection, outside the transaction, at
> whatever the default isolation gives it. Two concurrent commit attempts can **both** read `drafted` and **both**
> proceed. **The existing Protocol surface cannot express a compare-and-swap at all** — not merely "awkwardly", but
> *structurally*. Any option in Q1 that depends on CAS therefore depends on Q2 answering "yes, reopen".

### 1.3 R5's handler — ✅ CONFIRMED

`backend/app/routes/not_wired.py:184-238`, `commit_recommendation`, wired **in place** per Q9-A.

```
1. closed-enum wire-shape check on body.action        -> 422 if outside {approve, override}
2. service.commit(recommendation_id, identity.user_id, body.action, body.reason)
3. except UnauthorizedCommit            -> 403
   except UnknownPendingRecommendation  -> 404
   except CommitRejected                -> 409 commit_conflict
4. return committed.model_dump(mode="json")
```

⚑ **What happens to `case_lifecycle` state after a successful commit: NOTHING. There is no post-commit statement of
any kind.** The handler's dependencies are `Depends(require_commit)` and `Depends(get_commit_service)` — **it holds
no `CaseStore` reference today**; the store reaches it only indirectly, two levels down inside the provider
(`get_commit_service` → `get_commit_context_provider` → `get_case_store`).

### 1.4 `backend/audit_store/commit_service.py` — ✅ CONFIRMED FROZEN AND HOOK-FREE

`commit()` (L74-95), exact order verified on disk:

| Step | Line | What |
|---|---|---|
| 1 | 82 | `_gate(...)` — the CON-BR4 total-function predicate (GATE-1), **before any assembly** |
| 2 | 84-87 | independent `authorizer.authorize(underwriter_id, RBAC_COMMIT)` re-check (AUTHZ-1) |
| 3 | 89 | `context_provider.get(recommendation_id)` — the §1.5 seam |
| 4 | 91 | `_assemble(...)` — the **complete** `AuditRecord`, Pydantic-validated **before BEGIN** (TUPLE-1) |
| 5 | 93-94 | `with self._repository.atomic(): self._repository.insert(record)` (ATOMIC-1) |
| — | 95 | `return record.committed_decision` |

⚑ **There is NO hook, NO callback, NO extension point, NO post-write seam.** All five injected seams
(`repository`, `context_provider`, `authorizer`, `id_generator`, `clock`) are consumed **before or during** the
write; **none is invoked after it**. The service also **has no concept of `case_lifecycle` state** and cannot detect
an already-committed case on its own.

> **This single fact determines the shape of the whole fix:** a state transition **cannot** execute inside the frozen
> service's transaction. It must happen **before `commit()` is called** or **after it returns**. That is what makes
> **Q1** a genuine decision rather than a formality.

### 1.5 ⚠️ DIVERGENCE FROM THE TASK BRIEF — reported, not absorbed

The brief states U24 was **"reopened three times"** and instructs that a new reopening be logged as **the fourth**.
**The disk does not support this.** The record is **consistent at TWO** across four independent artifacts:

| Artifact | Says |
|---|---|
| `scope-b-wiring-summary.md` §1 | *"It was reopened **twice**"* — with exactly two subsections, Reopening #1 and Reopening #2 |
| `guide-state.md:3513` | *"reopening #1 2026-07-20T08:41:12Z · reopening #2 2026-07-20T11:03:25Z"* |
| `scope-b-wiring-plan.md:1009 / :1027` | *"Reopening #2 (Q14-A) adds a new production module"* |
| `BUILD-COMPLETION-REPORT.md:158` | *"U24 was **already reopened twice**"* |

The two are **#1 `list_application_ids()` (Q1-A)** and **#2 `memo_from_canonical()` (Q14-A)**.

The likely source of the "three" is **`audit.md:4101`**, whose *section heading* reads *"⚑ U24 THIRD REOPENING
AUTHORIZED (Q14-A)"*. That heading is **contradicted by its own entry body**, which calls the reopening *"distinct
from, and in addition to, **the** list-method reopening (Q1-A)"* — **one** prior, not two — and then explicitly
contrasts it with *"**THE FIRST REOPENING**"*; and it is contradicted by **`audit.md:4145`**, in the same file, which
calls the identical change ***"U24 reopening #2."*** **The heading is a stale mislabel; the substance is two.**

⚑ **Consequence, recorded so nothing is silently mis-numbered later: if Q2 concludes a reopening is needed, it is
U24's THIRD authorized reopening — not its fourth.** The `audit.md:4101` heading is **left unedited**: it is a
historical log line, and correcting a past entry in place would damage the append-only record. It is **superseded**
in the new audit entry, not rewritten.

---

## 2. The design tension, stated precisely

**`DecisionCommitService` and `CaseStore` are two different transactional boundaries — and, on disk, two different
database engines bound to two different roles:**

| Boundary | Owner | Engine | Transaction |
|---|---|---|---|
| `AuditRepository.atomic()` → `insert(AuditRecord)` | `audit-store` (**frozen**) | `AUDIT_WRITER_URL` (`dependencies.py:84-91`) | its own |
| `CaseStore.atomic()` → `put_application(state=...)` | `case-lifecycle` (U24) | `DATABASE_URL`, the owner (`dependencies.py:119-121`, per register #20) | its own |

**They cannot be merged into one atomic operation without editing a frozen unit** — which every prior pass in this
build has refused to do, and which this pass's holds forbid outright. Two separate engines also means even a shared
connection is unavailable: this is not one transaction with two statements, it is two transactions.

**Therefore no option below achieves true cross-store atomicity.** Each one either **prevents** the duplicate before
`commit()` is reached, **records** the transition after it returns, or **both** — each with a *differently-shaped*
residual failure window. **Naming which is which honestly is the substance of Q1 and Q4.** Any claim of "atomic
double-commit prevention" in this pass would be false, and this plan will not make one.

**Three distinct sub-defects hide inside register #19. They are not fixed by the same mechanism, and an answer to Q1
should be clear about which ones it addresses:**

| | Sub-defect | Fixed by |
|---|---|---|
| **D1** | The same `recommendation_id` can be committed **repeatedly**, writing a **duplicate `AuditRecord` each time** | **prevention** *before* `commit()` |
| **D2** | A committed case reports `status: "ready"` on R4 **forever** | **recording** the transition, *whenever* it happens |
| **D3** | WIRE-1 §4's *"already-committed recommendation → 409"* is **UNENFORCED** | a **detection point** that can see case state (Q3) |

---

## 3. THE OPEN QUESTIONS

> **Instructions**: write your choice after each `[Answer]:` tag. Multiple letters are fine where the options
> compose. **Nothing proceeds until every tag is filled.** Once answered, the full Q&A is embedded back into this
> document and the ambiguity-check runs before any code is written.

---

### Q1 — Where does the `drafted → committed` transition actually execute?

**The constraint (§1.4):** `DecisionCommitService.commit()` has **no post-write hook**. The transition must run
**before** `commit()` or **after it returns**. It cannot run inside the frozen service's transaction.

**Options:**

- **(a) — Post-commit, in R5's route.** The handler calls the state transition immediately after `commit()` returns
  successfully, outside the frozen service's atomic write.
  * **Fixes**: **D2** (R4 stops reporting `ready` forever). **D3 only if paired with a read pre-check** — the
    transition alone records state but nothing consults it.
  * **Does NOT fix D1.** ⚑ **Stated plainly: option (a) as literally framed does NOT prevent duplicate
    `AuditRecord`s.** Writing `committed` does not stop the next request, because nothing reads it before calling
    `commit()`. Adding a naive read-check makes it TOCTOU-racy (**FIND 2**: reads bypass the transaction), which
    narrows the window to milliseconds but does not close it.
  * **Residual**: a crash between `insert` and the state update leaves **AuditRecord written, case still `drafted`** —
    a **narrower, disclosed** race, not today's unbounded double-commit. Reconcilable later (see Q4).
  * **Needs no U24 reopening** — expressible through `get_application` + `put_application` + `atomic()` today (FIND 1).

- **(b) — CAS guard before `commit()` is ever called.** A compare-and-swap update on the case row
  (`UPDATE ... SET state='committed' WHERE application_id=:id AND state='drafted'`); `rowcount == 1` wins and
  proceeds to `commit()`, `rowcount == 0` fails fast with 409 **without ever reaching the frozen service**.
  * **Fixes D1, D2, and D3.** ⚑ **This is the ONLY option that genuinely eliminates duplicate `AuditRecord`s**,
    because the database serializes concurrent writers on a single row — the guarantee comes from Postgres, not from
    application timing.
  * ⚠️ **Requires a U24 reopening (Q2).** Per **FIND 2**, the existing Protocol **structurally cannot** express CAS:
    `put_application` is an unconditional upsert, and `get_application` reads on a **separate connection outside the
    transaction**, so read-then-write is not atomic even inside `atomic()`.
  * **Residual — a DIFFERENT and arguably worse shape**: the state flips to `committed` **before** the audit write. A
    crash between the CAS and the `insert` leaves the case **`committed` with NO `AuditRecord`** — and because
    `COMMITTED` is **terminal**, the underwriter's genuine commit action is **lost and un-retryable**. For a system
    whose §5.3/§11.3 invariant is *full auditability*, a **silently unauditable human decision** may be worse than a
    duplicate record. **A compensating rollback** (`committed → drafted` on commit failure) mitigates the *raised-
    exception* case but not the *crash* case, and would itself require declaring a currently-illegal reverse
    transition — a state-machine amendment worth deciding explicitly, not assuming.

- **(c) — Both.** An idempotency guard before `commit()` to prevent the common case, **plus** a best-effort state
  update after it returns; **explicitly accepting** that a crash mid-window is a narrow, disclosed residual risk
  rather than claiming perfect atomicity across two separately-owned stores.
  * **What it actually buys depends entirely on which guard is used, and this must not be blurred:**
    * guard = **CAS** → this is **(b)** with a redundant trailing write; duplicates eliminated, but the state is
      already flipped before the audit write, so **(b)'s residual applies, not (a)'s**.
    * guard = **plain read-check** → duplicates are **narrowed, NOT eliminated** (TOCTOU per FIND 2), and the
      residual is **(a)'s**. This is the *honest* reading of "guard before + best-effort after" using today's
      surface, and it needs **no reopening**.
  * ⚑ A **third shape** exists and is worth naming: a **two-step claim** — CAS `drafted → committing` before, then
    `committing → committed` after. This makes the crash window **explicitly visible as its own state** rather than
    ambiguous, so reconciliation is trivial (any case stuck in `committing` is exactly the crashed set). **Cost**: a
    **new `CaseState` member**, which touches `LEGAL_TRANSITIONS`, `TERMINAL_STATES`, the `case_to_memo_view_state`
    projection (the new state must project to `pending` or `ready` — a WIRE-1-adjacent decision), and register #14's
    two-value `Literal`. **Larger blast radius; named for completeness, not slipped in.**

- **(d) — Idempotency in the audit store instead**, e.g. a `UNIQUE` constraint on `audit_record.recommendation_id`,
  making the duplicate write fail at the database.
  * ⚑ **Named for completeness and NOT recommended**: it requires a **migration change to a frozen unit's schema**,
    which this pass's holds forbid. It would also change `audit_store`'s append-only semantics (superseding decisions
    legitimately share a `recommendation_id` — see `AuditRecord.supersedes_decision_id` / `DecisionStatus`), so the
    constraint is likely **wrong on the domain**, not merely forbidden. **Recorded so it is visibly rejected on the
    merits rather than silently unconsidered.**

**Recommendation (grounded, not a decision):** **(b)**, on the ground that **D1 — duplicate `AuditRecord`s — is the
BFSI-relevant defect** the register calls *"the most serious open item"*, and **(b) is the only option that actually
eliminates it**; (a) and read-check-(c) merely narrow a race and would leave register #19 **partly open under a
claim of being fixed**, which is the outcome this project's disclosure discipline exists to prevent. ⚠️ **The
recommendation is conditional on Q4** accepting **(b)'s inverted residual** (`committed` with no audit record, and a
terminal state making it un-retryable). **If that residual is judged unacceptable for an auditability-first system,
then (a) — with its "audit exists, case drafted" residual, which is reconcilable and safely retryable — is the
better answer, and register #19 should then be narrowed rather than closed.** That trade is a genuine domain
judgment and is deliberately left to the user.

**[Answer]**: (c), specifically the two-step claim-state shape — CAS drafted→committing before commit() is called, then committing→committed after commit() returns successfully. This is the only option that both genuinely eliminates duplicate AuditRecords (the CAS on drafted→committing is a true database-serialized guarantee, not a race narrowed by timing) and never risks the worse residual of a terminal, unretryable, audit-record-less commit. A crash mid-window leaves the case in an explicit, non-terminal, distinguishable "committing" state rather than silently masquerading as either "still drafted" or "finalized with nothing to show for it."

---

### Q2 — Does this require reopening U24, or does the existing `CaseStore` surface suffice?

**Preference stated in the brief, honored here**: prefer the option requiring **no** reopening if the existing
surface is sufficient. It was checked before assuming, per §1.2.

**What the existing surface CAN do** (no reopening): `get_application(id)` → rebuild the aggregate with
`state=COMMITTED` → `put_application(...)` inside `with store.atomic():`. The upsert's `set_` includes `state` and
**excludes** `profile_canonical`, so the profile is preserved. **Sufficient for option Q1(a), and for the plain-
read-check flavor of Q1(c).**

**What the existing surface CANNOT do** (**FIND 2**, decisive): **express a compare-and-swap.** `put_application` is
an **unconditional** upsert, and `get_application` opens a **separate connection outside `atomic()`'s transaction**.
A read-then-write sequence is therefore **not atomic even when written inside `atomic()`** — two concurrent
requests can both observe `drafted` and both write `committed`. **Q1(b) is not implementable against U24's public
surface as built** — precisely the same shape of finding that justified reopening #1 for R2.

**Options:**

- **(a) — No reopening.** Perform the transition via the existing Protocol from `backend/app/`. **Locks the answer
  to Q1 into (a) or read-check-(c)** — duplicates narrowed, never eliminated. ⚠️ Also raises a **second concern
  independent of concurrency**: constructing a `PendingApplication` with a new state inside `backend/app/` puts
  **U24-shaped domain knowledge in the composition root**, which is the exact invariant (*"no domain logic / owns no
  persistence"*) that reopening #1 was authorized to protect — and Scope B rejected its option (B) on precisely this
  ground.
- **(b) — Reopen U24 (its THIRD authorized reopening, per §1.5) to add ONE CAS method** to the `CaseStore` Protocol,
  `PostgresCaseStore`, and `InMemoryCaseStore` — e.g.
  `mark_committed(application_id) -> bool` (a conditional `UPDATE ... WHERE state='drafted'`, returning whether it
  won). Keeps the SQL and the state knowledge **inside U24**, where every comparable decision in this build has put
  it, and exposes a **boolean** to the composition root — a wire-shape answer, not a domain decision.
  ⚑ Follows reopening #1's precedent **exactly**: methods added to **existing modules**, so
  `EXPECTED_PRODUCTION_MODULES` stays at **8** — the same call reopening #1 correctly made, for the same reason.
- **(c) — Reopen U24 and expose the transition on `CasePipeline`** (e.g. promote/extend `_transition`).
  ⚠️ **Conflicts with Scope B Q3-D**: the composition root deliberately **never constructs `CasePipeline`**, which
  is what makes R4 side-effect-free *by construction rather than by discipline*. Wiring the pipeline into R5 to reach
  a transition would **undo a load-bearing structural guarantee** to gain nothing the store cannot give.
  **Not recommended.**

**Recommendation (grounded):** **(b)** — **but only if Q1 selects (b) or CAS-flavored (c)**. If Q1 selects (a) or
read-check-(c), then **(a) here is correct and no reopening should be opened**, exactly per the brief's stated
preference. ⚑ **Q1 and Q2 are therefore ONE decision, not two**: the reopening exists *only* to make CAS possible,
and CAS is the *only* thing that eliminates duplicates. **If a reopening is authorized, it is logged as U24's THIRD
authorized reopening — with its own rationale, distinct from #1 (`list_application_ids`, enumeration for R2) and #2
(`memo_from_canonical`, memo rehydration for R4) — BEFORE any code is written.**

**[Answer]**: (b) — reopen U24 as its third authorized reopening. Add the minimum surface needed for the two-step model: a CAS method performing drafted→committing (returning whether it won), a finalize method performing committing→committed, and a recovery method performing committing→drafted for the crash-reconciliation path. Add CaseState.COMMITTING as a new, explicitly non-terminal state; update LEGAL_TRANSITIONS to include DRAFTED→COMMITTING, COMMITTING→COMMITTED, and COMMITTING→DRAFTED (recovery only); COMMITTED remains the sole terminal state. case_to_memo_view_state's Literal must map COMMITTING → "pending" (a case mid-commit should never present as "ready" on the wire) — disclose this explicitly as a further widening of register #14, which already tracks the internal-state-vs-wire-shape gap from the wiring pass.

---

### Q3 — How does R5 map "already committed" to WIRE-1 §4's 409 `commit_conflict`?

**Confirmed on disk, so this is not in doubt**: the frozen `DecisionCommitService` **imports nothing from
`case_lifecycle`, holds no case state, and has no way to know a case is already committed** (§1.4). It raises
`CommitRejected` **only** from `_gate` (missing `underwriter_id`, action outside the closed enum, blank-reason
override) and `UnauthorizedCommit` from AUTHZ-1. **An already-committed case is invisible to it.** ⚑ **Confirmed:
this check CANNOT live inside the frozen service. It must live in the route or in the Q1 guard.**

**Context that must not be misread**: the wiring pass **rejected "a route-level pre-check"** as *"duplicating
enforcement."* ⚑ **That rejection was about duplicating the CON-BR4 approval gate** — re-implementing a check the
frozen service already performs. **Detecting an already-committed case is NOT a duplicate of anything**, because the
frozen service performs no such check and structurally cannot. The precedent is **G1/Q13-A**, where a
**closed-enum wire-shape check** was accepted in the same handler precisely because *"it inspects no authorization
and no business rule, and the frozen `_gate` still runs and still rejects independently."* A state check has the same
character — provided it is expressed as *state membership*, not as a re-derived approval decision.

**Options:**

- **(a) — The Q1 guard IS the detection point.** The CAS returns `False` (lost the race / already terminal); R5 maps
  that **one** boolean to `409 commit_conflict` and never calls `commit()`. **No separate read, no TOCTOU window, no
  duplicated logic** — detection and prevention are literally the same operation. **Requires Q1(b)/CAS-(c).**
- **(b) — An explicit read pre-check in the route**: `get_application` → if `state is COMMITTED` → 409, else call
  `commit()`. Works with **no reopening**; ⚠️ **TOCTOU-racy** (FIND 2), so it narrows rather than closes, and it
  places a `CaseState` comparison inside `backend/app/` — a mild domain-knowledge leak, weaker than (a) on both axes.
- **(c) — A dedicated exception from U24**, e.g. `AlreadyCommitted`, raised by the CAS method and caught by R5
  alongside the existing `except` clauses. Cosmetic over (a) — same mechanism, exception-shaped instead of
  boolean-shaped. ⚠️ Mildly **worse for R5's current mapping discipline**: the handler's existing `except
  CommitRejected → 409` is honest *because* every `CommitRejected` reaching it is unambiguously a gate rejection
  (G1/Q13-A). Adding a second 409-producing exception type reopens exactly the ambiguity Q13-A closed.

**Recommendation (grounded):** **(a)** — one operation that both prevents and detects, mapping a **boolean** (not a
domain verdict) to 409. It is the only option with **no** window between check and act, it keeps `CaseState` out of
`backend/app/`, and it preserves the Q13-A property that every `CommitRejected` reaching the handler is a gate
rejection. **Conditional on Q1(b)/Q2(b).** If Q1 selects (a) or read-check-(c), then **(b) here is the only
available answer**, and its TOCTOU window must be **disclosed in the same breath** as the 409 it enables — a 409
that is *usually* correct is not the same as WIRE-1 §4 being enforced, and this plan will not let the two be
conflated.

**[Answer]**: (a) — the CAS operation on drafted→committing is the detection point. A False result (already committing or already committed) maps directly to 409 commit_conflict, and commit() is never invoked in that branch. This preserves the Q13-A property that every CommitRejected reaching the handler is unambiguously a gate rejection, since the committed-check never touches that exception path at all.

**Sub-question Q3.1 — WIRE-1 §4 status after the fix.** `guide-docs/build/wire-1/api-contract.md:68` maps 409 to
*"commit-gate conflict — override with a blank/missing reason (BR-COMMIT-GATE), **or an already-committed
recommendation**."* Under (a)/(c), that second clause becomes **genuinely enforced for the first time**. Under (b),
it becomes **enforced-except-under-concurrency**. ⚑ **Either way, WIRE-1's text is NOT amended** (standing hold) —
the contract already anticipates this 409; the fix makes the code meet the contract, not the reverse. **Confirm the
honest claim to record:**
- **(i)** *"WIRE-1 §4's already-committed 409 is now ENFORCED"* — available **only** under (a)/(c).
- **(ii)** *"…is now enforced except under concurrent access, where a duplicate remains possible"* — the honest
  claim under (b).

**[Answer]**: (i) — record the honest claim as "WIRE-1 §4's already-committed 409 is now genuinely enforced, including under concurrent access." The CAS eliminates the race entirely rather than narrowing it, so this stronger claim is earned, not aspirational.

---

### Q4 — What happens to a case mid-attempt when a crash occurs between the two boundaries?

**This plan will not claim cross-store atomicity.** Two engines, two transactions, one frozen (§2). **A window
exists in every option.** The only real question is **which window, and is it acceptable and reconcilable.**

**The two window shapes, named plainly:**

| | Window | Arises under | The resulting state |
|---|---|---|---|
| **W-A** | crash **after** `insert`, **before** the state update | Q1(a), read-check-(c) | **`AuditRecord` EXISTS, case shows `drafted`.** The human's decision **is** recorded and auditable. A retry would write a **duplicate**. |
| **W-B** | crash **after** the CAS, **before** `insert` | Q1(b), CAS-(c) | **Case shows `committed`, NO `AuditRecord`.** The human's decision is **LOST** — and since `COMMITTED` is **terminal**, retry is **structurally impossible**. |

**Options:**

- **(a) — Accept W-A as the disclosed end-state.** *"An audit record exists but the case shows drafted"* is
  **detectable and reconcilable**: cross-reference `recommendation_id` presence in `audit_record` against any case in
  `drafted`. ⚑ **Preserves the auditability invariant** — the human's action is never lost. **Ships with a named
  reconciliation procedure** (below).
- **(b) — Accept W-B as the disclosed end-state.** Duplicates are genuinely impossible; the cost is that a crashed
  attempt yields a **terminal case with no audit record**. ⚠️ **This directly contradicts PROJECT-BRIEF §5.3/§11.3
  (full auditability) and §5.6 (no decision finalised without underwriter action recorded)** — the case *reads* as
  finalised while no record of the human's action exists. **Detectable** by the same cross-reference (a `committed`
  case with no `AuditRecord`), but **NOT repairable** without an illegal reverse transition.
- **(c) — Two-step claim state** (`drafted → committing → committed`, per Q1(c)'s third shape). Makes the window an
  **explicit state** rather than an inference, so reconciliation is exact and unambiguous. **Cost**: a new
  `CaseState`, touching `LEGAL_TRANSITIONS` / `TERMINAL_STATES` / the projection `Literal` / register #14.
- **(d) — A stronger mechanism** (two-phase commit, or a transactional outbox in the case store drained after the
  audit write). ⚑ **Genuinely eliminates the window** — and **requires either editing frozen `audit_store` internals
  or introducing a distributed-transaction dependency**. **Both are forbidden by this pass's holds.** Named for
  completeness and so the reason for rejection is **the holds, not ignorance of the option.**

**Recommendation (grounded):** **(a)** *if* Q1 selects (a); **(b) with an explicit, loud disclosure** *if* Q1 selects
(b). ⚑ **The honest framing either way: this fix REPLACES an unbounded, always-reachable defect with a narrow,
crash-only window. That is a real improvement and it is NOT perfect atomicity, and the closing documentation must say
exactly that** — the same discipline as Q11-A's *"exercisable after running the seed script"*, which was deliberately
narrower than "end-to-end". ⚠️ **Whichever is chosen, register #19 should be recorded as NARROWED-and-partly-
discharged, with the surviving window as its own new register item** — not marked closed. Closing it outright would
be the same failure mode the §5 fold note exists to correct.

**Sub-question Q4.1 — is a reconciliation mechanism in scope for this pass?**
- **(i)** Ship the fix; **document** the reconciliation query in prose only (no code).
- **(ii)** Ship the fix **plus** a reconciliation **read-only check** (a query or CLI) that lists mismatched cases.
  ⚠️ Note the collision: a CLI entrypoint touches the same ground as open register **#8
  `DEPLOY-MIGRATE-DEFERRED`**, and `admin-cli` (U17) is a **frozen** unit — so this is likely its own change, not an
  add-on here.
- **(iii)** Out of scope entirely; open it as a **new register item** with a named owner.

**[Answer]** *(Q4)*: (c) — the two-step claim state, as chosen in Q1. The surviving window (a crash while a case sits in COMMITTING) is explicit, detectable by a simple query, and reconcilable in a determinate way: if the recommendation_id exists in audit_record, advance to COMMITTED; if it doesn't, revert to DRAFTED for retry. Record this surviving window as its own new, narrower register item once the fix ships — do not claim register #19 is closed outright; state precisely what is and isn't guaranteed, exactly as this project's disclosure discipline has required throughout.

**[Answer]** *(Q4.1)*: (ii) — ship the fix plus a read-only reconciliation script (not a CLI entrypoint on the frozen admin-cli, avoiding the collision with #8/DEPLOY-MIGRATE-DEFERRED you correctly flagged) that lists any case stuck in COMMITTING beyond a reasonable threshold, cross-referenced against audit_record presence, with the two recovery actions it would take named but not necessarily automated in this pass. Place it in backend/scripts/, mirroring where the seed script already lives.

---

### Q5 — Test strategy: how is double-commit prevention actually verified?

**What tier-U can and cannot prove, established from disk:**

* **`InMemoryCaseStore`** (`case_lifecycle/tests/fixtures.py:136-196`) is a **single-threaded buffering fake**.
  ⚑ **It cannot prove CAS.** A single-threaded test cannot interleave two transactions — the exact vacuity trap
  `store.py`'s own header warns about for `atomic()` (*"a single method body cannot half-execute in a single-threaded
  test — so EAGER-1's 'no partial row' assertion would be VACUOUS"*). **A tier-U test asserting "the second commit
  returns 409" against this fake would prove the CALL SEQUENCE, not the CONCURRENCY GUARANTEE**, and must not be
  described as proving the latter.
* **What tier-U CAN prove, genuinely**: that R5 calls the guard **before** `commit()`; that a guard returning
  `False` yields **409** and that `commit()` was **never invoked** (a spy assertion — this is the real
  duplicate-prevention tooth at tier-U); that a successful commit **does** record the transition; that the state
  machine still rejects illegal transitions; that a `committed` case projects correctly on R4.
* **tier-I already has a known-good pattern**: `case_lifecycle/tests/test_persist_integration.py` (PERSIST-1) uses
  `testcontainers` + `postgres:16` + **`database`'s clean-skip guard verbatim** (`_docker_available()` pinged
  **inside the fixture body, before any container is constructed**) — which is exactly why U24's tier-I tests
  **SKIP cleanly** where `audit_store`'s `importorskip`-only pattern **ERRORS**. ⚑ **U24 adds ZERO errors**, and the
  standing hold (**the 5 `audit_store` Docker errors stay exactly 5**) is therefore **safe under this pattern** — a
  new tier-I test adds **skips**, never errors. **Any new tier-I test MUST reuse this guard verbatim.**

**Options:**

- **(a) — tier-U only.** Cheapest; **does not prove the fix works under real concurrency.** ⚑ For a CAS-based fix
  this is a **material gap**: the entire guarantee lives in the database, and tier-U cannot see the database.
- **(b) — tier-U + a new tier-I concurrency test** using the existing testcontainers pattern: two real connections,
  both attempting the CAS on the same `drafted` row, asserting **exactly one wins** and the loser observes
  `rowcount == 0`. **The only way to actually prove D1 is eliminated.** Cost: **+N skips** when Docker is absent
  (must be predicted and disclosed in advance, as U24's `+5` was), **0 new errors**.
- **(c) — tier-U + tier-I + a route-level integration test** driving two concurrent HTTP commits end-to-end and
  asserting exactly one `AuditRecord`. **Strongest evidence** (it proves the property at the layer the defect was
  reported at) and the **most expensive** — needs both the audit and case schemas live in one container, crossing
  the two-engine boundary in a test.

**Sub-question Q5.1 — where does a new tier-I test live?** `case_lifecycle/tests/` (with the reopening, alongside
PERSIST-1, reusing the fixture directly — natural if Q2(b)) **or** `app/tests/` (⚠️ which has **no testcontainers
pattern today**, so one would be introduced there for the first time).

**Recommendation (grounded):** **(b)**, with the tier-I test living in **`case_lifecycle/tests/`** beside PERSIST-1
and reusing its `_docker_available()` guard **verbatim**. Rationale: if the fix's entire correctness claim rests on a
database-level CAS, then **a test suite that never touches a database has not verified the claim** — and this build's
standing discipline is that a test which cannot fail for the right reason is disclosed as vacuous rather than
counted. **(c) is better evidence and can be a named follow-on**; it is not recommended for this pass because the
two-engine setup is a materially larger piece of test infrastructure than the defect itself, and the tier-I CAS test
already proves the load-bearing property. ⚑ **If Q1 selects (a)/read-check-(c) instead — i.e. no CAS — then (b)'s
concurrency test would PROVE THE RACE EXISTS rather than prove it is closed**; in that case tier-U plus an
**explicitly-named disclosure test** documenting the surviving window is the honest configuration, and the skip-count
delta should be predicted before anything is written either way.

**[Answer]** *(Q5)*: (b) — tier-U logic tests plus a new tier-I concurrency test, reusing database's/U24's known-good clean-skip testcontainers guard verbatim (the ping-inside-the-fixture-body pattern that lets U24's existing tier-I tests skip cleanly rather than error). Tier-U alone cannot prove a database-level CAS guarantee, and this build's standing discipline has consistently refused to let a test that can't fail for the right reason stand in as proof of one.

**[Answer]** *(Q5.1)*: case_lifecycle/tests/, directly beside PERSIST-1, reusing its fixture and guard.

---

## 4. Holds for this pass — verified, all currently upheld

| Hold | Status at plan time |
|---|---|
| No edit to `backend/audit_store/commit_service.py` or **any** frozen-23 unit's internals | ✅ Untouched — `DecisionCommitService` is **composed with, never modified**, exactly as every prior pass held |
| WIRE-1's contract text **not amended** | ✅ Untouched — §4's already-committed 409 **already exists** in the contract; the fix makes code meet it (Q3.1) |
| `not_wired.py` **not renamed** | ✅ Untouched — register **#13** stays open and undischarged |
| U23's frozen test **not edited** | ✅ Untouched — no route added, so the filename set and `(path, method)` set are both unchanged |
| The `audit_store` Docker-guard gap **untouched** — 5 errors stay exactly 5 | ✅ Untouched — and U24's tier-I pattern **adds skips, never errors** (§Q5) |
| **tier-B not authorized** | ✅ Not invoked — nothing here needs the corpus or a live LLM |
| **No new route** under `backend/app/routes/` | ✅ None proposed — R5 is modified **in place**, per Q9-A |
| **U24 reopening logged BEFORE any code**, with its own rationale | ⏸️ **Not yet triggered** — whether one is needed is **Q2**. If authorized it is U24's **THIRD** (§1.5), not fourth |
| **No code generated in this pass** | ✅ **Zero code written. Zero files under `backend/` touched.** |

**Test state carried forward, NOT re-run by this pass**: backend **1492 passed / 0 failed / 37 skipped / 5
pre-existing `audit_store` Docker-absence errors**, coverage **99.87%**. **Nothing was executed or modified.**

---

## 5. What happens after the answers

1. Answers recorded verbatim in `audit.md`; **the full Q&A embedded back into this document** (§3 becomes the
   answered record).
2. **The mandatory ambiguity-check runs** against the answer set — surface-and-stop if not clean, per the standing
   discipline.
3. **If and only if Q2 authorizes a reopening**: it is logged to `audit.md` **and** `guide-state.md` as **U24's THIRD
   authorized reopening**, with its own rationale distinct from #1 and #2, **BEFORE any code is written**.
4. A **code-generation plan** is written and separately approved. **Only then does any code exist.**
5. On completion: register **#19** updated to its true post-fix status — **narrowed, partly discharged, or closed**,
   whichever the evidence supports — with any surviving window opened as **its own register item**.

---

**STOPPED AT THE PLAN-FILE GATE.** No code. No reopening. The next decision is the user's.

---

## 6. MANDATORY AMBIGUITY-CHECK — ⛔ **NOT CLEAN. SURFACE-AND-STOP.**

**Run**: 2026-07-21 · against the full Q1–Q5 answer set plus §1–§2's re-established ground truth.
**Result**: **2 GENUINE BLOCKERS (A1, A2)** · **1 determinate finding requiring disclosure (A3)** ·
**1 non-obvious consequence carried into the code-gen plan (A4)** · **3 directed checks resolved (i)/(ii)/(iii)**.

⚑ **The code-generation plan is NOT written.** Per the standing surface-and-stop discipline, two items in the answer
set cannot be resolved without inventing a decision that is the user's. **No code exists and none was written.**

---

### ⛔ A1 — BLOCKER: `TERMINAL_STATES` — the answer contradicts what is on disk

**Q2's answer states**: *"COMMITTED remains **the sole terminal state**."*

**On disk** (`states.py:63`), verified this pass:

```python
TERMINAL_STATES: frozenset[CaseState] = frozenset({CaseState.COMMITTED, CaseState.FAILED})
```

**`FAILED` is terminal today, and has been since U24 was built.** So *"COMMITTED remains the sole terminal state"*
is either (a) a **restatement that COMMITTING is not terminal** — in which case `TERMINAL_STATES` is **unchanged at
two members** and nothing needs doing — or (b) an instruction to **remove `FAILED`** from the terminal set.

**Reading (b) would be a significant, unrequested change to U24's failure semantics:**

* it breaks `test_no_transition_leaves_a_terminal_state` (`test_states.py:74-77`) for `FAILED`;
* it contradicts **COMMITBOUND-1(c)** and the **FAILED-1** family, whose whole point is that *"the failed path and
  the commit path structurally do not intersect"* (`provider.py` header);
* it would make `FAILED → <anything>` newly expressible, which **no answer in this set asked for**.

⚑ **Reading (a) is almost certainly what was meant** — but "almost certainly" is exactly the standard this project's
ambiguity-check exists to refuse. **Not improvised. Confirm explicitly.**

**[Answer A1]**: ✅ **RESOLVED — (i).** *"The first reading — COMMITTING is simply not terminal; TERMINAL_STATES stays exactly frozenset({COMMITTED, FAILED}), unchanged from what's already on disk. There is no intent anywhere in this fix to remove FAILED's terminal status, reopen FAILED→anything, or touch FAILED-1/COMMITBOUND-1(c) in any way. My phrasing was sloppy and created a real ambiguity; thank you for refusing to guess at it."*

**Consequence**: `TERMINAL_STATES` is **not edited at all**, and `test_no_transition_leaves_a_terminal_state`
(`test_states.py:74-77`) and `test_failed.py:45` (`assert CaseState.FAILED in TERMINAL_STATES`) both need **no edit**.

**Options as presented (retained for the record):**
- **(i)** `TERMINAL_STATES` **UNCHANGED** at `{COMMITTED, FAILED}`; the phrase meant only that **COMMITTING is not
  terminal**. *(Recommended — consistent with every other answer and with FAILED-1/COMMITBOUND-1(c).)*
- **(ii)** Remove `FAILED` from `TERMINAL_STATES`, making `COMMITTED` literally the sole member — **a deliberate
  change to U24's failure semantics**, with its own rationale required.

---

### ⛔ A2 — BLOCKER: the CAS method's KEY is unspecified, and the choice is load-bearing

**The mismatch, established from disk:**

* **R5 is keyed by `recommendation_id`** (`not_wired.py:185`, WIRE-1 R5 `POST /recommendations/{recommendation_id}/commit`).
* **The case state lives on `PendingApplication`, keyed by `application_id`** (`schemas.py` / `repository.py:33-44`).
* The two are joined **only** through `PendingRecommendation.application_id`.

**Q2's answer specifies *"a CAS method performing drafted→committing (returning whether it won)"* but not what it is
keyed by.** The two choices are materially different, and one of them re-introduces a defect this fix exists to
remove:

- **(i) — Keyed by `recommendation_id`.** U24 performs the join internally
  (`UPDATE pending_application SET state='committing' FROM pending_recommendation WHERE ... AND state='drafted'`),
  in **one statement, one round trip, one serialization point**.
  * ✅ **The CAS stays genuinely atomic.**
  * ✅ Matches how R5 is actually keyed — the composition root passes through the id it already has.
  * ✅ Keeps the application↔recommendation join **inside U24**, where the domain knowledge belongs.
  * ✅ Can distinguish **"no such recommendation" (→404)** from **"lost the CAS" (→409)** in a single result — which
    **Q3(a) needs**, since R5 must still produce 404 for an unknown id and today gets that from
    `UnknownPendingRecommendation` raised *inside* `commit()` — a path Q3(a) now bypasses for the conflict case.
- **(ii) — Keyed by `application_id`.** The composition root must first call `get_recommendation(recommendation_id)`
  to resolve `.application_id`, then CAS.
  * ⛔ **Re-introduces a TOCTOU window** *between the resolve and the CAS* — the exact defect class this fix removes.
  * ⛔ Puts the **application↔recommendation relationship inside `backend/app/`** — U24-shaped domain knowledge in the
    composition root, the invariant reopening #1 was authorized to protect and whose violation Scope B rejected as
    its option (B).
  * ⛔ Costs an extra round trip on the write path.

**Recommendation: (i)**, on all four grounds. ⚑ **But this materially determines the reopening's public surface —
the method signature, its return type, and whether R5 can still produce a correct 404 — so it is the user's call,
not an implementation detail to be settled while writing code.**

**Sub-question A2.1 — what does the CAS return?** Q3(a) maps a `False` to 409, but **three outcomes** must be
distinguishable if R5's existing status mapping is to survive intact:

| Outcome | R5 must produce |
|---|---|
| won the CAS (was `drafted`) | proceed to `commit()` |
| lost / already `committing` / already `committed` | **409** `commit_conflict` |
| **no such `recommendation_id`** | **404** — WIRE-1 §4, and R5's current behaviour |

⚑ **A bare `bool` collapses the second and third into one value**, which would silently turn today's **404 into a
409** for an unknown id — **a WIRE-1 §4 regression introduced by the fix.** Options: a **3-valued enum**; a `bool`
**plus** a pre-existing `get_recommendation` existence check in R5 (⚠️ reintroduces a read, though a benign one — a
non-existent id cannot race into existence under this build's write paths); or **`Optional[bool]`** (`None` =
unknown). **Recommended: a small 3-valued enum returned by U24** — explicit, unambiguous at the call site, and it
keeps the distinction inside the unit that owns the data.

**[Answer A2]**: ✅ **RESOLVED — keyed by `recommendation_id`.** *"Confirmed — key the CAS (and the finalize and recovery methods) by recommendation_id, not application_id. U24 performs the join internally (recommendation_id → its owning application_id → the state update) inside one CAS statement, so the composition root never resolves the mapping itself and no TOCTOU window is reintroduced at the call site."*

**[Answer A2.1]**: ✅ **RESOLVED — a 3-valued enum.** *"Confirmed — a 3-valued result, not a bool. Something like a CommitClaimResult enum with WON, LOST (already committing or committed), and NOT_FOUND (no such recommendation_id at all). R5 maps WON → proceed to commit(), LOST → 409 commit_conflict, NOT_FOUND → 404 not_found — preserving today's correct 404 behavior for an invalid recommendation_id rather than silently regressing it to a 409."*

---

### ⚠️ A3 — DETERMINATE FINDING (not a blocker): three exact-set assertions break and need manual edits

This is the **direct answer to directed check (i)**, and it is **partly yes, partly no** — reported precisely rather
than waved through.

✅ **The exhaustiveness guarantee DOES hold automatically.** `test_states.py:50-62` derives the illegal set as
`set(itertools.product(CaseState, CaseState)) - LEGAL_TRANSITIONS`. Adding `COMMITTING` makes the cross-product
**7×7 = 49**; the three new legal tuples are subtracted; **all 41 remaining pairs are swept with no test edit.** The
companion `test_the_derived_illegal_set_covers_the_whole_cross_product` asserts
`len(illegal) + len(LEGAL) == len(CaseState)**2` and **also self-adjusts** (41 + 8 = 49). **`states.py`'s P-CASE-4
claim — *"a newly added state instantly appears in the derived illegal set with no test edit"* — is TRUE and
survives this change.**

⚠️ **But three sibling assertions in the same file are hardcoded exact-set comparisons and WILL fail:**

| Test | Line | Why it breaks | Edit needed |
|---|---|---|---|
| `test_the_five_states_plus_the_internal_failed_state_exist` | 25-28 | asserts the value set **equals** the exact six strings | add `"committing"`; **the test's NAME becomes wrong too** ("the five states") |
| `test_the_legal_table_is_the_expected_happy_path_plus_failure` | 37-44 | asserts `LEGAL_TRANSITIONS` **equals** an exact 5-tuple frozenset | add the three new tuples |
| `test_no_transition_leaves_a_terminal_state` | 74-77 | iterates `TERMINAL_STATES` | **no edit if A1(i)**; breaks if A1(ii) |

⚑ **These are U24's OWN tests, not frozen-23 tests**, so editing them is squarely inside the authorized reopening's
scope and violates no hold. **They are flagged because the phrase "exhaustiveness is automatic" is true of the sweep
and NOT true of the file as a whole** — and a reader of the P-CASE-4 header could reasonably assume otherwise.
**Recorded so the edits are planned deliberately, not discovered as surprise red tests.** `fixtures.py`'s
`illegal_transition_cases()` (6 landmarks, **unsplittable**) needs **no edit** — every landmark it names stays
illegal — though adding a `COMMITTING` landmark is worth considering as a **deliberate addition**, not a repair.

---

### ⚠️ A4 — NON-OBVIOUS CONSEQUENCE: every R5 failure branch must now recover the state

**Directly implied by the answer set, easy to miss, and it would be a new defect if missed.**

Under Q1(c)/Q3(a), the CAS flips `drafted → committing` **before** `commit()` is called. `commit()` can then still
fail in **three** ways that are **not** crashes: `UnauthorizedCommit` (→403), `UnknownPendingRecommendation` (→404),
and any other `CommitRejected` (→409 — e.g. a blank-reason override). It can also raise an infrastructure error.

⛔ **In every one of those branches the case is left in `COMMITTING` with no audit record and no crash** — a case
stuck in a claim state by an *ordinary, expected, everyday rejection*. A blank-reason override — a routine user
error the UI is built around (U8 `ui-override-form`) — would **permanently strand the case** until the
reconciliation script ran.

**The fix is determinate** (the recovery method `COMMITTING → DRAFTED` chosen in Q2 already exists for exactly this),
so this is **carried into the code-gen plan rather than raised as a blocker**: **every** `except` branch in R5 must
recover the state before raising its `WireError`, and the recovery must itself be failure-tolerant (a recovery that
throws must not mask the original rejection). ⚑ **This deserves its own named tier-U test per branch** — three
tests, one per exception type, asserting the case is back at `drafted` and re-committable. **Without them the fix
would trade an unbounded double-commit for a routine stranding, which would be a worse defect than the one it
closes.**

---

### ✅ Directed check (ii) — the legal-transition table: NO GAP. Confirmed.

Proposed `LEGAL_TRANSITIONS` (8 tuples):

```
SUBMITTED  -> PROFILED
PROFILED   -> EVALUATED
EVALUATED  -> DRAFTED
EVALUATED  -> FAILED
DRAFTED    -> COMMITTING     (new — the CAS)
COMMITTING -> COMMITTED      (new — finalize)
COMMITTING -> DRAFTED        (new — recovery)
```
*(`DRAFTED → COMMITTED` is **removed**: under the two-step model the direct edge must no longer be legal, or the
one-step transition the fix exists to replace would remain expressible. ⚑ **This is a deletion the answer set did
not state explicitly** — flagged here, and it is the only reading consistent with Q1(c). If the direct edge is
retained, confirm why.)*

| Claim | Verdict |
|---|---|
| **No path INTO `COMMITTING` except from `DRAFTED`** | ✅ Exactly one in-edge: `DRAFTED → COMMITTING`. |
| **No path OUT of `COMMITTING` except `COMMITTED` or back to `DRAFTED`** | ✅ Exactly two out-edges, both named. |
| **`COMMITTING` is non-terminal** | ✅ Has out-edges, so it must be excluded from `TERMINAL_STATES` — consistent with A1(i). |
| **`COMMITTED` unreachable except via `COMMITTING`** | ✅ Once `DRAFTED → COMMITTED` is deleted, `COMMITTING` is its sole predecessor — **the fix's guarantee is structural, not conventional**. |
| **`COMMITTING → FAILED` absent** | ✅ Correct and deliberate: a failed *commit* is retryable (recover to `DRAFTED`), unlike a failed *drafting*, which is terminal. The two failure kinds stay distinct. |

⚑ **One intended cycle exists**: `DRAFTED → COMMITTING → DRAFTED`. **This is correct** — it is the retry path — but
it makes `LEGAL_TRANSITIONS` **cyclic for the first time**. No current test or invariant assumes acyclicity
(verified: nothing computes reachability or topological order). **Recorded because it is a new property of the graph,
not because it is a problem.**

---

### ✅ Directed check (iii) — the reconciliation script's two-engine read: ACHIEVABLE, no third read path. Confirmed.

**The script needs**: case state (from `DATABASE_URL`) **and** *"does an `AuditRecord` exist for this
`recommendation_id`?"* (from `AUDIT_READER_URL`) — the same two-engine boundary the fix itself straddles.

**Both bindings already exist** (`dependencies.py:71-91`): `app_engine()` → `DATABASE_URL`, `reader_engine()` →
`AUDIT_READER_URL`, `writer_engine()` → `AUDIT_WRITER_URL`. **The script needs the two READ engines only, and no
third path.** ✅

⚠️ **One real gap found, and it resolves cleanly.** The frozen audit read surface exposes **`get(decision_id)`,
`browse(application_id)`, `exists_superseding(decision_id)`** — **there is NO lookup by `recommendation_id`**
(`audit_service.py:27-38`, `repository.py:26-30`, both verified). The reconciliation query is therefore **not
directly expressible** as a single call.

**It IS expressible without touching a frozen unit**: `AuditService.browse_history(application_id=None)` returns
**all** records; the script builds a `set` of `record.recommendation_id` **once** and tests membership per stuck
case. **One read, no N+1, no new method, no frozen edit.** ✅ *(The alternative — raw SQL against `audit_record` in
the script — is **rejected**: `backend/scripts/` sits outside both structural-scan roots, so a hand-rolled query
there would be **structurally invisible** to every guard in the build. That is precisely the reasoning that made an
ad hoc `canon_deserialize` the wrong call during the wiring pass.)*

⚑ **Engine-construction convention, worth stating so it is not improvised**: the seed script does **not** import
`dependencies.py` — it calls `sa.create_engine(get_settings().DATABASE_URL)` directly
(`seed_demo_cases.py:218`), keeping FastAPI's `Depends` graph out of an out-of-band script. **The reconciliation
script should mirror that exactly**, constructing its two engines from `get_settings()` rather than importing the
composition root's `lru_cache`d providers. Same two URLs, no DI layer, no third read path.

**Sub-question A-iii.1 — the script reads `AUDIT_READER_URL`, whose role is SELECT-only on `audit_record` +
`applicant_profile_snapshot`, and `DATABASE_URL` (owner) for the pending tables** (register **#20**: the pending
tables carry **no explicit grants** and are owner-only). **A read-only script therefore needs the OWNER engine** to
see case state — the same binding `dependencies.py` already uses and justifies. **No new grant is invented and
register #20 stays open and untouched.** ✅ Confirm this is the intended binding rather than an occasion to revisit
#20 — **which this pass does NOT do.**

**[Answer A-iii.1]**: ✅ **RESOLVED — `browse_history(None)` + a membership set, with the cost disclosed.** *"Confirmed — the reconciliation script resolves the 'does this recommendation_id already have an AuditRecord' check via the frozen audit surface's browse_history(None) plus a membership set, exactly as you found, rather than any raw SQL or a third read path. State this explicitly in the code-gen plan as the sanctioned mechanism, and note the performance shape honestly (browse_history(None) loading the full decision history to build one membership set) as a disclosed cost of reusing the existing frozen surface rather than adding a new one — this is a low-volume reconciliation script, not a request-path route, so the tradeoff is acceptable, but it should be stated rather than left implicit."*

---

### ✅ A4 — CARRIED FORWARD, NOT BLOCKING (user-directed)

**A4 is carried into the code-gen plan rather than blocking here.** Under Q1(c)/Q3(a) the CAS flips
`drafted → committing` **before** `commit()` is called, so **every** path on which `commit()` fails without crashing
must run the **recovery** method (`committing → drafted`) before raising its `WireError`, or the case is stranded in
a claim state by an ordinary rejection.

**Dedicated tier-U test required per failure branch, stated explicitly:**

| # | Branch | Trigger | Assert |
|---|---|---|---|
| **1** | **blank-reason override** → `CommitRejected` → **409** | an `override` action with a blank/whitespace reason — **a routine user error the whole U8 `ui-override-form` unit is built around** | case is back at `drafted` **and re-committable** |
| **2** | **a bad action that somehow still reaches `commit()`** → `CommitRejected` → **409** | an action passing R5's closed-enum wire-check but rejected by the frozen `_gate` (defence-in-depth: the two checks are independent, so this must not be assumed unreachable) | case is back at `drafted` |
| **3** | **unauthorized caller** → `UnauthorizedCommit` → **403** | a caller passing `require_commit` but rejected by the frozen service's own independent AUTHZ-1 re-check | case is back at `drafted` |

⚑ **Plus**: the recovery must be **failure-tolerant** — a recovery that itself raises must **not mask the original
rejection**, or a 409 would surface as a 500. **Without these three tests the fix would trade an unbounded
double-commit for a routine stranding — a worse defect than the one it closes.**

---

### Summary — what is blocked and what is not

| Item | Status |
|---|---|
| **A1** `TERMINAL_STATES` wording vs. disk | ⛔ **BLOCKER — answer required** |
| **A2** CAS method key (+ **A2.1** return shape / the 404 regression) | ⛔ **BLOCKER — answer required** |
| **A3** three exact-set tests need manual edits | ⚠️ Determinate; **disclosed**, no answer needed |
| **A4** R5 failure branches must recover state | ⚠️ Determinate; **carried into the code-gen plan**, no answer needed |
| **(i)** complement sweep auto-incorporates `COMMITTING` | ✅ **Confirmed** — with A3's caveat |
| **(ii)** no stray paths in/out of `COMMITTING` | ✅ **Confirmed** — plus the flagged `DRAFTED → COMMITTED` **deletion** |
| **(iii)** two-engine reconciliation read | ✅ **Confirmed achievable** — via `browse_history`, no third path |

⛔ **STOPPED. The code-generation plan is NOT written.** It follows once **A1**, **A2**, **A2.1** and **A-iii.1** are
answered. **No code has been written and no `backend/` file has been touched by this pass.**

---

## 7. AMBIGUITY-CHECK — ROUND 2 (post A1/A2/A2.1/A-iii.1)

**Run**: 2026-07-21 · against the **complete** answer set (Q1–Q5 + Q3.1/Q4.1/Q5.1 + A1/A2/A2.1/A-iii.1) and §1–§2's
ground truth.

**Result**: ✅ **All four round-1 blockers RESOLVED.** ✅ **All three directed checks (i)/(ii)/(iii) CONFIRMED CLEAN.**
⚠️ **ONE NEW ITEM SURFACED that the four answers introduced** — **B1**, an invariant-test narrowing that needs
explicit sign-off before implementation. It is **flagged in advance here, not left to be discovered in a diff** —
the **ADAPTER-1 precedent** from the Scope B pass.

---

### ✅ Directed check (i) — `CommitClaimResult` vs COMMITBOUND-1: CLEAN. Confirmed against the actual scan.

**The scan, read from disk** (`tests/structural.py:59`, `tests/test_commitbound.py:39-48`):

```python
FORBIDDEN_COMMIT_TOKENS = ("audit_record", "authorize", "RBAC_COMMIT")
# for each production module:  code = executable_text(parse(path))
#                              assert forbidden not in code
```

| Proposed identifier | Contains a forbidden token? |
|---|---|
| `CommitClaimResult` | ❌ no · ✅ safe |
| `WON` / `LOST` / `NOT_FOUND` | ❌ no · ✅ safe |
| the three method names | ❌ no · ✅ safe |

✅ **`NOT_FOUND` is a plain row-existence check, unambiguously on the correct side of the boundary.** It inspects
**no role, no permission, no `underwriter_id`, no business rule** — it answers *"does this PK exist?"* and nothing
more. ⚑ **The strongest grounding is precedent, not argument**: U24 **already** does exactly this and it was
**already accepted under COMMITBOUND-1** — `PendingCommitContextProvider.get()` raises
`UnknownPendingRecommendation` for an unknown id, R5 maps it to **404**, and
`test_commitbound.py:98-102` asserts that behaviour **inside the COMMITBOUND-1 file itself**. `NOT_FOUND` is the
same check relocated earlier in the request, **not a new capability**.

> ⚠️ **NAMING CONSTRAINT, recorded because the scan is a SUBSTRING test, not word-boundary.**
> `test_commitbound.py:46` uses `assert forbidden not in code` — plain `in`, **not** `structural.contains_token`'s
> word-boundary matcher. So **any identifier containing `authorize` as a substring trips it** — including
> **`authorized`** and **`unauthorized`**. ⛔ **No U24 production identifier may contain those.** Harmless once
> known; a genuine trap if discovered at red-test time. *(`backend/scripts/` and `backend/app/` are outside
> `production_py_files()`, whose root is `UNIT_DIR = backend/case_lifecycle` — so the reconciliation script may
> name `audit_record` freely.)*

> ⚑ **`EXPECTED_PRODUCTION_MODULES` must stay at 8 — and that requires a deliberate placement decision.**
> The set (`structural.py:26-35`) currently holds 8 modules. **Placing `CommitClaimResult` in a NEW module would
> change it 8→9.** **Recommended: put the enum in `states.py`** — it is a state-transition outcome, `states.py`
> already owns `CaseState`/`LEGAL_TRANSITIONS`/`IllegalTransition`, and this keeps the reopening's shape identical
> to **reopening #1** (methods/symbols on **existing** modules, set **unchanged**) rather than **reopening #2**
> (a new module, 7→8). **Same call as #1, for the same reason.** Recorded in the code-gen plan.

---

### ✅ Directed check (ii) — the `recommendation_id`-keyed CAS join: EXPRESSIBLE. No schema change.

**Verified against `migrations/0001_case_lifecycle.sql` and `repository.py`'s table definitions:**

| Requirement | On disk |
|---|---|
| `pending_recommendation.recommendation_id` is the **PK** | ✅ `CONSTRAINT pk_pending_recommendation PRIMARY KEY (recommendation_id)` |
| `pending_recommendation.application_id` **FKs** to `pending_application` | ✅ `CONSTRAINT fk_pending_recommendation_application FOREIGN KEY (application_id) REFERENCES pending_application (application_id)` |
| both tables declared in `repository.py`'s SQLAlchemy metadata | ✅ L33-57 |
| `pending_application.state` is a writable `VARCHAR` | ✅ `state VARCHAR NOT NULL` (`CaseState.value`, no native ENUM) |

✅ **The join is expressible in ONE statement, through the existing table objects, with NO new column, NO new index,
and NO migration change** — e.g. a scalar-subquery `UPDATE`:

```
UPDATE pending_application
   SET state = 'committing'
 WHERE application_id = (SELECT application_id FROM pending_recommendation
                          WHERE recommendation_id = :rid)
   AND state = 'drafted'
```

**`rowcount == 1` ⇒ WON.** The whole guarantee is one row-level write lock held by Postgres — **the serialization
comes from the database, not from application timing**, which is exactly what Q1(c) requires. ⚑ **U24's existing
migration is sufficient as published** — no `0002_*.sql` is needed, which matters because U24's migrations are
**forward-only and immutable once published** (the file says so).

> ⚑ **ONE NUANCE, resolved rather than glossed: `rowcount == 0` is AMBIGUOUS on its own.** It means *either* "not
> `drafted`" (**LOST**) *or* "no such `recommendation_id`" (**NOT_FOUND**) — and A2.1 requires distinguishing them.
> **Resolution**: on the `rowcount == 0` branch only, issue a **second, existence-only** query
> (`SELECT 1 FROM pending_recommendation WHERE recommendation_id = :rid`) → present ⇒ `LOST`, absent ⇒ `NOT_FOUND`.
> **This is NOT a TOCTOU reintroduction**: it runs only on the *failure* path, it decides no write, and a
> recommendation row is **never deleted anywhere in this build** — so "absent" is a stable fact, not a racing one.
> Both statements run inside **one `atomic()` opened INSIDE the method** (see **B1**). ✅

---

### ✅ Directed check (iii) — the three exact-set test edits: NOW FULLY ENUMERATED. Plus two corrections.

**Complete enumeration, by file and test name — a repo-wide scan of every `CaseState` / `LEGAL_TRANSITIONS` /
`TERMINAL_STATES` / `case_to_memo_view_state` reference across `case_lifecycle/tests`, `app/`, `app/tests` and
`scripts/`:**

| # | File | Test / symbol | Why it must change |
|---|---|---|---|
| **1** | `case_lifecycle/tests/test_states.py:25-28` | `test_the_five_states_plus_the_internal_failed_state_exist` | asserts the value set **equals** the exact six strings → add `"committing"`. ⚑ **The test's NAME also becomes wrong** ("the five states") → rename |
| **2** | `case_lifecycle/tests/test_states.py:37-44` | `test_the_legal_table_is_the_expected_happy_path_plus_failure` | asserts `LEGAL_TRANSITIONS` **equals** an exact 5-tuple frozenset → **+3 new tuples, −1 removed** (`DRAFTED→COMMITTED`) |
| **3** | `case_lifecycle/tests/test_project.py:36-41` | the `@parametrize` projection table | ⚑ **ADDITION, not a repair** — the table is explicit-by-design; add `(CaseState.COMMITTING, "pending")` to keep it exhaustive |

**⚑ CORRECTION 1 — `test_no_transition_leaves_a_terminal_state` is NOT in this list.** It was listed as a
*conditional* third item in round 1 (*"only if A1(ii)"*). **A1 resolved to (i)**, so `TERMINAL_STATES` is untouched
and **this test needs no edit**. Same for `test_failed.py:45`.

**⚑ CORRECTION 2 — `case_to_memo_view_state` needs NO LOGIC CHANGE.** Q2's answer said the projection *"must map
COMMITTING → `pending`"*. **It already does.** The function is
`return "ready" if case.state is CaseState.DRAFTED else "pending"` (`states.py:94`) — a new state falls into the
`else` branch **automatically**, and the `Literal["ready","pending"]` return type is **already correct**. ⚑ Confirmed
by `test_project.py:49`, which comprehends over **all** `CaseState` members and therefore **auto-exercises**
`COMMITTING` with no edit. **What changes is the DOCSTRING** (naming `COMMITTING` alongside `failed` as a
disclosed projection, per the register-#14 widening) **and the test table row above — not the logic.** Recorded so
the code-gen plan does not "fix" something that is already correct.

**No other file needs an edit.** `fixtures.py::illegal_transition_cases()` — every landmark it names **stays
illegal** ✅ (adding a `COMMITTING` landmark is an optional deliberate addition, not a repair).
`app/tests/conftest.py`, `factories.py`, `test_wire1_pending_shapes.py`, `test_eager.py`, `test_trigger.py`,
`test_persist_integration.py`, `test_commitbound.py` all reference **specific** states (`DRAFTED`, `EVALUATED`,
`SUBMITTED`, `FAILED`) and assert nothing about the **set** ✅.

---

### ⚠️ B1 — NEW ITEM: `INT-FAITHFUL-1` must be NARROWED, and that needs explicit sign-off

**Surfaced by A2's confirmation that R5 drives the CAS.** Not present in round 1, because round 1 had not yet
established that the composition root would call a *write* method on the case store.

**What is on disk** — `app/tests/test_no_write_route.py`, titled ***"every write goes through the frozen
`DecisionCommitService`"***, asserting over **every production file under `backend/app/`**:

```python
for forbidden in (".insert(", ".atomic("):
    assert forbidden not in code, f"{path}: {forbidden}"
commit_callers == {"not_wired.py"}
```

**Two distinct consequences:**

**(1) A hard design constraint — determinate, no decision needed.** ⛔ **The three new methods MUST open their own
`atomic()` INTERNALLY.** If R5 were to call `with store.atomic():` itself, `.atomic(` would appear under
`backend/app/` and **this assertion would break**. Encapsulating the transaction inside U24 is required **anyway**
for the CAS to be atomic — so the constraint and the correct design coincide. **Binding on the code-gen plan.**
*(Also verified safe: a method named e.g. `claim_for_commit(` does **not** match the `.commit(` literal, so the
`commit_callers == {"not_wired.py"}` assertion is unaffected either way — but names must be checked against that
literal before use.)*

**(2) The file's THESIS becomes false as written — and that needs authorization.** Its title and header claim
***every*** write goes through the frozen service. Once R5 claims and finalizes pending state, **that is no longer
true**: there are now writes that legitimately do **not** go through `DecisionCommitService` — they go through
U24's own methods, against a **different table, a different engine and a different unit's boundary**.

⚑ **The precedent for what to do is exact and was set by this same file.** The Scope B pass hit this identically —
Scope A's *"zero write-CAPABLE routes"* became false when R5 was wired — and it **narrowed each assertion rather
than deleting it**, recording *"deleting the assertions would have left the file asserting nothing."* **The same
treatment applies here**, and the narrowed guarantee should be:

> **Every `audit_record` write goes through the frozen `DecisionCommitService`; every *pending-state* write goes
> through U24's own methods, and `backend/app/` still opens no transaction and writes no row itself
> (`.insert(` / `.atomic(` still appear nowhere).**

**That is strictly more specific, not more permissive** — it keeps both halves falsifiable and adds a claim the
current file cannot make. ⚠️ **But it edits a test that encodes a load-bearing invariant (INT-FAITHFUL-1), so it is
raised for explicit sign-off rather than performed as a side effect.** **It violates no standing hold** — it is
`backend/app/`'s **own** test, **not** a frozen-23 unit test and **not** U23's frozen `NFR-DEP-ROUTES-1`, both of
which remain untouched.

**[Answer B1]**:
- **(i)** **Narrow `INT-FAITHFUL-1` as stated above** — thesis, title and header updated; both halves kept
  falsifiable; the change disclosed in the code summary. *(Recommended — the exact ADAPTER-1 / Scope-B precedent.)*
- **(ii)** Leave the file untouched and **find a design that writes no pending state from `backend/app/`** —
  ⚠️ this effectively **rules out Q1(c)/Q3(a)**, since R5 is the only place that knows a commit succeeded.
- **(iii)** Something else — specify.

---

### Round-2 summary

| Item | Status |
|---|---|
| **A1** `TERMINAL_STATES` | ✅ **RESOLVED** — (i), set unchanged; **two tests drop off the edit list** |
| **A2** CAS key | ✅ **RESOLVED** — keyed by `recommendation_id`, join internal to U24 |
| **A2.1** return shape | ✅ **RESOLVED** — 3-valued `CommitClaimResult`; 404 preserved |
| **A-iii.1** reconciliation read | ✅ **RESOLVED** — `browse_history(None)` + membership set, cost disclosed |
| **A4** per-branch recovery | ✅ Carried into the code-gen plan with **3 named tests** |
| **(i)** enum vs COMMITBOUND-1 | ✅ **CLEAN** — with the `authorize`-substring naming trap + the `states.py` placement call recorded |
| **(ii)** CAS join expressibility | ✅ **CLEAN** — one statement, no schema change; `rowcount==0` ambiguity resolved |
| **(iii)** test-edit enumeration | ✅ **COMPLETE** — **3 edits**, plus 2 corrections (one test drops off; the projection needs **no logic change**) |
| **B1** `INT-FAITHFUL-1` narrowing | ⚠️ **NEW — needs sign-off before implementation** |

⚑ **The code-generation plan IS written** (`fix-register-19-code-gen-plan.md`), since all four round-1 blockers and
all three directed checks are resolved. **B1 is flagged at the top of that plan as the single item requiring
authorization before implementation begins.** **No code has been written.**
