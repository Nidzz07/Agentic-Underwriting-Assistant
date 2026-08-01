# Register #27 Remediation Plan — `DUPLICATE-PENDING-RECOMMENDATION-ROWS`

**Stage**: POST-BUILD → scoping/planning pass
**Status**: ✅ **DESIGN COMPLETE — all 8 questions answered (Q1–Q6, then Q7/Q8 surfaced by the check and answered).
Ambiguity-check RE-RUN → CLEAN (§4.1). The fourth-reopening authorization is written as a standalone artifact:
`register-27-reopening-authorization.md`. AWAITING SIGN-OFF — no code written, no backend file touched.**

Superseded status lines, preserved in order: *"⛔ PLAN GATE — 6 questions open, none pre-filled…"* → *"⛔ PLAN GATE —
Q1–Q6 ANSWERED… ambiguity-check ⛔ NOT CLEAN: Q1(D) is not implementable as worded (§3 Fold B), and TWO new
questions are open — Q7, Q8… the authorization document is DELIBERATELY NOT WRITTEN…"*
**Date**: 2026-08-01
**Predecessors**: `outlier-wiring-plan.md` (where #27 was discovered), commit `d5c2c41`, `fix-register-19-plan.md`
(the structural precedent for a U24 reopening)

---

## 0. ⛔ Read this first — #27's logged text describes the SYMPTOM, not the whole defect

#27 was opened during the outlier pass's Step 13 verification and logged accurately for what was then known: an
unordered lookup plus unbounded row accumulation. **This investigation found a third consequence of the same root
cause that #27 does not mention, and which is arguably more serious than either.**

> **A terminal, `COMMITTED` case is silently resurrected to `EVALUATED` by re-submission**, and is then re-draftable
> — producing a fresh recommendation for an application that has already been committed to the audit trail.

Executed against the real pipeline this session (read-only, nothing written):

```
state before re-submit : CaseState.COMMITTED
is terminal            : True
state AFTER re-submit  : CaseState.EVALUATED
```

That is not a UI ambiguity. **It is a state-machine breach with audit-integrity implications**, and it shares a root
cause with #27's duplicate rows: `put_application` is an unguarded upsert. **Q2 exists to classify it deliberately.**

---

## 1. Measured inventory — read from current code, not from #27's summary

### 1.1 The mechanism, end to end

| Step | Code | Behaviour |
|---|---|---|
| 1 | `pipeline.submit()` → `put_application` (`repository.py:82-105`) | `INSERT … ON CONFLICT DO UPDATE`, and the `set_` **includes `state`** (`:98`) — so an existing row's state is **overwritten to `EVALUATED`** |
| 2 | `pipeline.draft()` (`pipeline.py:138`) | `assert_legal(application.state, CaseState.DRAFTED)`. `(DRAFTED, DRAFTED)` is **absent** from `LEGAL_TRANSITIONS` — the guard is real and correct |
| 3 | — | But step 1 already reset the state to `EVALUATED`, and `(EVALUATED, DRAFTED)` **is** legal, so **the guard never fires** |
| 4 | `put_recommendation` (`repository.py:131-143`) | **plain `INSERT`** — a new row every time |

**One half of the same atomic block is re-run-safe and the other is not.** `put_application` was deliberately made
an upsert; `put_recommendation` was not.

### 1.2 ⚑ `TERMINAL_STATES` is enforced by NOTHING

`TERMINAL_STATES` (`states.py:94`) is referenced **only by tests about itself** (`test_states.py`, `test_failed.py`).
**No production code path consults it.** `put_application` applies no transition guard at all, and `submit()`'s two
`assert_legal` calls (`pipeline.py:81-82`) are **static** — constant-to-constant assertions about the transition
table, never about the current row's state. Nothing anywhere prevents an upsert from writing a state that no legal
transition permits.

### 1.3 The ambiguous lookup

`_recommendation_row` (`repository.py:145-149`) issues `SELECT … WHERE application_id = ?` with **no `ORDER BY` and
no `LIMIT`**, then takes `.first()` in Python. `application_id` has **no uniqueness guarantee** —
`0001_case_lifecycle.sql` gives it only a **non-unique** index; the PK is `recommendation_id`. **The row served is
undefined by SQL semantics** — not "earliest by PK". The observed oldest-row behaviour is an artifact of Postgres
seq-scanning an insert-only table in heap order and could change under a different plan with no code change.

### 1.4 ⚑ Blast radius — and the one place that is SAFE

**Affected** (`recommendation_for_application`): **R4** (`not_wired.py:172`) · **R2's queue** (`:129`) ·
**`reconcile_committing_cases.py:101`**.

⚑ **The commit boundary is NOT affected.** `provider.py:41` resolves via `get_recommendation(recommendation_id)` —
**by primary key**. R5, the CON-BR4 gate and `CommitContext` are all keyed by `recommendation_id`. Register #19's
CAS is likewise safe: `_owning_application_id()` (`repository.py:210-214`) is a correlated subquery keyed on the
recommendation PK.

⚠️ **But #19 interacts with duplicates in a way worth stating**: multiple recommendations share **one** application
state. Committing recommendation A drives the *application* to `COMMITTED`, after which recommendation B for the
same application is **permanently unclaimable** (`claim_for_commit` returns `LOST`). Not a new defect — a
consequence of duplicates that any fix should be checked against.

### 1.5 ⛔ A constraint every option must respect

`repository.py:250` reasons, load-bearingly:

> *"a `pending_recommendation` row is **never deleted anywhere in this build**, so 'absent' is a stable fact."*

This is what lets `claim_for_commit` disambiguate `NOT_FOUND` from `LOST` — and therefore what keeps R5's **404**
from becoming a **409** (WIRE-1 §4). **Any option that deletes or replaces rows invalidates that reasoning** and
must address it explicitly rather than incidentally.

### 1.6 Replay is NOT threatened — which widens the option space

The brief's replay guarantee (§146, §207) and the 100%-reproducibility criterion (§170) are keyed on **decision IDs
in `audit_record`**. `pending_recommendation` is **pre-commit scratch**. So "replace rather than accumulate" is
**not** inherently an auditability violation — a point worth stating, because it is the intuition that would
otherwise rule out option B on principle.

### 1.7 The test doubles mask this by construction

Both `case_lifecycle/tests/fixtures.py:183` and `app/tests/factories.py:213` implement the lookup as
`for rec in self._recommendations.values(): if rec.application_id == …: return rec` — keyed by `recommendation_id`,
iterating an **insertion-ordered dict**. They are **deterministic where Postgres is not**, and always return the
**first inserted**. `fixtures.py:194` claims *"PERSIST-1 is what keeps this fake and `PostgresCaseStore` honest
about agreeing."* ⚑ **For this method that promise is currently false.**

### 1.8 U24's freeze status — this would be the FOURTH reopening

Authoritative record (`BUILD-COMPLETION-REPORT.md:198`, `:303`): **(1)** `list_application_ids()` · **(2)**
`memo_from_canonical()` · **(3)** register #19's two-step commit claim. **A #27 fix is the fourth.**

---

## 2. Open decisions — answer inline, none pre-filled

### Q1 — which fix approach?

⚑ Read with §1.5 (the never-deleted assumption) and §1.6 (replay is not at risk) in view.

- **(A) `ORDER BY` + `LIMIT 1` on the existing lookup.** Makes the selection **deterministic but still arbitrary** —
  there is *nothing meaningful to order by* (no timestamp, no sequence). Honest half-measure: removes the
  nondeterminism, does **not** stop accumulation. Cheap, no migration, breaks no test.
- **(B) `put_recommendation` → upsert keyed on `application_id`.** Requires a **UNIQUE constraint that does not
  exist** → **new migration** (see **Q4**). Forecloses history. ⛔ Directly invalidates §1.5's never-deleted
  assumption, since an upsert replaces rows.
- **(C) Add a `created_at`/sequence column and serve the latest.** Makes "latest" meaningful, preserves history,
  respects §1.5. **New migration** (see **Q4**). Heaviest option.
- **(D) Stop `submit()` resetting `state` on conflict, so the EXISTING guard fires. — RECOMMENDED (with the caveat
  below).** Remove `"state"` from `put_application`'s `on_conflict_do_update` `set_`. Then a re-submit leaves the
  state alone, `draft()` reads `DRAFTED`, and `assert_legal(DRAFTED, DRAFTED)` refuses. **Smallest change, no
  migration, respects §1.5, and it fixes the CAUSE rather than the symptom — including the terminal-state breach
  in §1.2/Q2 as a side effect.**
- **(E) Guard `put_application` against illegal/terminal transitions.** Closes the state-machine hole generally
  rather than on one path. ⚠️ Must be checked against register #19's `_swap_state`, which deliberately writes state
  directly via `UPDATE` and would need to remain exempt or route through the same guard.

⛔ **THE COST OF (D), STATED PLAINLY — it changes what re-seeding MEANS.** Today `python -m
backend.scripts.seed_demo_cases` is *effectively idempotent-ish*: run it any number of times and you get freshly
drafted cases. Under (D), **a second run against an already-drafted case refuses**. Three consequences that must be
seen before accepting it:

1. **It raises, it does not decline gracefully.** `assert_legal` throws `IllegalTransition`. `draft()`'s own
   docstring says it *"never raises for a domain failure"* — under (D) that promise becomes false on a reachable
   path. So (D) needs a sub-decision: does the **seed script skip** already-drafted cases, or does **`draft()`
   return a `DraftOutcome` failure** instead of raising?
2. ⚑ **The guard sits AFTER the expensive work.** `draft_memo` runs at `pipeline.py:116`; `assert_legal` at `:138`.
   A refused re-seed would pay the **full memo-drafting cost** (and, with `--real-llm`, real money) and *then*
   throw. If (D) is chosen, moving the guard earlier is part of the fix, not an optimization.
3. **Demo/testing workflow changes.** Re-seeding to get fresh data would require a reset first. That is arguably
   *more* honest, but it is a change to established habit and should be accepted knowingly.

⚑ **(A) is compatible with all of the above** and can be taken as **independent cheap hardening** regardless of
which of (B)–(E) wins — it costs nothing and removes real nondeterminism.

**[Answer]**: (D) — stop submit() resetting state on conflict, so the existing LEGAL_TRANSITIONS guard fires naturally, with (A) as cheap independent hardening on the lookup itself. This fixes the cause rather than the symptom and closes the terminal-state breach as a side effect, at the smallest change with no migration.

Accepting D's full stated cost: (1) move the assert_legal guard earlier than draft_memo, so a refused re-seed fails fast without paying the drafting cost first — this is part of the fix, not optional; (2) draft() should return a DraftOutcome failure rather than raise, keeping its "never raises for a domain failure" docstring promise true; (3) the seed script should skip already-drafted cases gracefully (log/report the skip) rather than crash, so re-running the seed script multiple times remains a usable demo/testing workflow, just one that no longer produces duplicate data for already-drafted cases.

⛔ **See §4 — the ambiguity-check found this answer is NOT IMPLEMENTABLE AS WORDED.** `put_application` is the sole
state-writing primitive for three legitimate transitions; removing `state` from its upsert breaks them. The
*intent* survives intact; the *location* of the guard must move. **Q7.**

---

### Q2 — the terminal-state breach: fold into #27, or split as its own item?

§1.2's finding — a `COMMITTED` case silently resurrected to `EVALUATED` — shares #27's root cause but not its
severity class. #27 as written is *"the wrong row is served"*; this is *"a terminal state was left illegally"*.

- **(a) Split it into its own register item, classified more severely than #27. — RECOMMENDED.** Three grounds.
  **(i)** **Different severity and different owner-facing meaning**: #27 is a read-resolution ambiguity with no
  incorrect *write*; this permits an **illegal write to a terminal case's state**, which is an audit-integrity
  concern — a committed case is supposed to be closed. **(ii)** **Different reachability**: #27 needs duplicate rows
  to manifest; this needs only one re-submission of any committed case. **(iii)** ⚑ **The register's own precedent
  is to split when the *character* differs, not merely the code path** — #14 and #16 are both "no wire
  representation" but were kept separate because one is a status discriminator and one is a queue shape. Splitting
  also means that if Q1 lands on (A) — which fixes neither — the two remain independently visible rather than one
  hiding inside the other's text.
- **(b) Fold it into #27 as an additional documented consequence.** Honest to the shared root cause, and a single
  fix (Q1(D)/(E)) closes both at once — so one item could be closed once, cleanly. But it buries a
  **higher-severity** finding inside an item whose title and summary describe duplicate rows, where a reader
  triaging by severity would not look for it.
- **(c) Split, and additionally re-title #27** to make clear it is the read-side symptom of a write-side cause.
  Most precise; costs an extra supersession on an item corrected only days ago.
- **(d) Leave it recorded in this plan only.** ⛔ Rejected on the project's own standard — plans are not the
  register, and #17 is the cautionary example of a finding whose real shape lived outside the register text.

**[Answer]**: (a) — split the terminal-state breach into its own register item, classified more severely than #27. It's a different character of defect (an illegal write to a terminal case's state, not a read-resolution ambiguity) and deserves independent visibility rather than being buried inside #27's duplicate-rows framing.

---

### Q3 — are the masking test doubles fixed in this pass, or deferred?

Both doubles return the **first inserted** row deterministically; Postgres returns an **arbitrary** row. §1.7.

- **(a) In scope for this pass — fix the doubles alongside the real store. — RECOMMENDED.** ⚑ **Leaving them masked
  is how this defect reached production in the first place**: there was no failing test to write, because the fake
  could not express the failure. `fixtures.py:194` explicitly claims PERSIST-1 keeps fake and real *"honest about
  agreeing"* — a claim that is **false today for this method** and should not be left standing while the real store
  is corrected. Fixing the real store alone leaves the *next* regression of this class equally invisible.
- **(b) Defer to a follow-up pass.** Keeps this diff smaller and single-purpose. But it means shipping a fix whose
  regression guard is known-blind, and the follow-up has no forcing function once the symptom is gone.
- **(c) In scope, but only to the extent the chosen Q1 option requires** — e.g. under (D) the doubles must mirror
  the new refusal semantics anyway, so parity work is unavoidable there but optional under (A).
- **(d) Fix the doubles FIRST, as a standalone pass, and let them fail against the unfixed real store.** Maximum
  rigour — it would produce a genuine RED that the real fix then turns green. ⚠️ But the doubles are tier-U and the
  real behaviour is tier-I, so the RED would not actually appear in the same suite run; the rigour is partly
  illusory.

**[Answer]**: (a) — fix the test doubles in scope, in this same pass. Leaving them masked is how this defect reached production in the first place; shipping a fix without correcting the regression-guard blindness defeats the purpose.

---

### Q4 — a new migration, and its collision with register #26

⚑ **Live only if Q1 lands on (B), (C), or an (E) variant needing schema support.** Under (A) or (D) alone, **no
migration is needed and this question is moot** — answer "N/A" in that case.

U24's migration sequence carries its own checksum manifest, guarded by
`test_migname.py::test_verify_checksums_passes_against_u24s_own_manifest`. **That guard is already environment-
fragile under register #26** (`CRLF-CHECKSUM-MANIFEST-FRAGILE`): `core.autocrlf=true` with no `.gitattributes`
means a manifest computed against LF bytes does not match a fresh Windows checkout's CRLF bytes.

- **(a) Accept the interaction, add the migration, recompute U24's manifest, and record explicitly that the new
  entry inherits #26 identically — no better, no worse. — RECOMMENDED if a migration is needed.** Exactly the
  discipline used when `0003_auth.sql` was added under the same known fragility: the new entry is **consistent with
  the existing ones and consistently fragile**, and that is stated rather than discovered later. #26 stays open and
  is **not** claimed as addressed.
- **(b) Fix #26 first (a `.gitattributes` pinning line endings), then add the migration.** Removes the fragility
  before compounding it. ⛔ But #26's own record states the remedy is **repo-wide** and needs its **own
  authorization** — it would turn a U24 fix into a repository-configuration change.
- **(c) Choose a migration-free option (A or D) specifically to avoid this.** Legitimate — but the migration
  question should not *drive* the design; if (C) is right on the merits, #26 is a cost, not a veto.
- **(d) Add the migration and skip the manifest update.** ⛔ Rejected: it would leave the integrity guard failing
  against a real content change, which is the one thing it exists to catch.

**[Answer]**: N/A — moot under Q1(D), no migration needed.

---

### Q5 — the fourth-reopening authorization vehicle

U24 is frozen; this would be its **fourth** authorized reopening (§1.8). The project's established shape for #19
was: **design and approve the reopening standalone, then apply it as step 0 of the executing pass.**

- **(a) Follow #19's shape exactly — this plan is the standalone design; on approval the reopening is authorized in
  writing, and the fix is applied as step 0 of its own execution pass. — RECOMMENDED.** It is the precedent, it
  keeps the authorization auditable and separable from the code, and it means the reopening's scope is fixed
  **before** anyone edits a frozen file. ⚑ It also matters more here than for #19, because Q1's options differ
  wildly in what they touch — the authorization must name the *specific* files and the *specific* reason.
- **(b) Authorize a broader "U24 maintenance" reopening** covering #27 and any adjacent fixes. Fewer gates; but a
  standing open reopening on a frozen unit is exactly what freezing exists to prevent.
- **(c) Treat the repository/pipeline changes as not-a-reopening** because they fix a defect rather than add
  capability. ⛔ Rejected: the three prior reopenings include capability-adding *and* defect-fixing changes (#19 was
  a fix), so the precedent is clear that a fix still counts.
- **(d) Defer the fix; record the design only.** Legitimate if the answer to Q1 turns out to be expensive — #27 is
  non-blocking, and a verified design with no code is a real deliverable.

**[Answer]**: (a) — follow #19's shape exactly: this plan is the standalone design, the reopening is authorized in writing on approval, and the fix is applied as step 0 of its own execution pass, naming the specific files and reason.

---

### Q6 — verification depth

This project's standard (Step 7 / Step 10 / Step 12 / the outlier pass's Step 13) is **evidence from a real
database, user-run**, not a passing test.

- **(a) Full, per §3 below — reset, seed three times in sequence, prove no accumulation (or a correct refusal),
  prove the terminal-state breach no longer reproduces, and re-confirm R4/R2 serve the intended row. —
  RECOMMENDED.** The terminal-state check matters most: it is the finding with audit-integrity weight, and it is
  the one thing that **cannot** be proven by the tier-U doubles even after Q3(a), because it needs a real committed
  case.
- **(b) Full minus the terminal-state re-check.** Cheaper; leaves the most serious finding unverified live.
- **(c) Automated tests only.** ⛔ Rejected on this project's record: the 204 defect, the override gaps, and **#27
  itself** were each found by manual verification and by nothing else.

**[Answer]**: (a) — full verification including the live terminal-state re-check, since that's the one finding with real audit-integrity weight and the one thing the fixed test doubles still can't prove on their own.

---

## 3. Mandatory ambiguity-check — combined answer set

**Answer set**: Q1(D)+(A) · Q2(a) · Q3(a) · Q4(N/A) · Q5(a) · Q6(a). Every finding below was **measured on disk or
executed this session**, not inferred.

**Internal consistency, checked first**: Q2(a)'s split and Q1(D)'s fix are compatible — one fix can close two
register items, and splitting them makes that *visible* rather than conflating them. Q4's N/A follows correctly from
Q1(D) (no schema change). Q5(a)'s "name the specific files" **depends on Q7's outcome**, which is why the
authorization document is **not** written yet.

**Result: ⛔ NOT CLEAN. Q1(D) IS NOT IMPLEMENTABLE AS WORDED, and TWO NEW QUESTIONS ARE SURFACED (Q7, Q8).**
One directed check came back clean; two did not.

### ⛔ Fold A (DIRECTED) — moving the guard earlier: the *move* is clean, the *premise* is not

**The move itself is safe.** Nothing between `pipeline.py:106` and `:138` mutates `application.state` — it is read
once into a frozen dataclass. The `_transition(application, FAILED)` at `:118` is reachable only from `EVALUATED`,
which is the only legal source of `FAILED` anyway, so an early return for an illegal state removes no legal path.
**`draft_memo`'s error handling needs no restructuring.**

✅ **And no test pins the raise.** `IllegalTransition` appears only in `test_states.py` (`:70, :113, :127, :138`),
which exercises `assert_legal` **directly** — never through `draft()`. So Q1's accepted cost (2) — returning a
`DraftOutcome` failure instead of raising — **breaks no existing test**. Use the already-public pure `is_legal`
rather than `assert_legal` at the new site.

### ⛔ Fold B (DIRECTED, BLOCKING) — `put_application` is the SOLE state-writing primitive

**Q1(D) says "stop `submit()` resetting state on conflict", which reads as: remove `"state"` from
`put_application`'s `on_conflict_do_update` `set_`. That would break three legitimate state writes.** Every
`put_application` caller, enumerated:

| Call site | Purpose | Needs to write `state`? |
|---|---|---|
| `pipeline.py:98` (`submit`) | create/refresh an application | ⛔ **NO — this is the defect** |
| `pipeline.py:140` (`draft`) | `EVALUATED → DRAFTED` | ✅ **YES** |
| `pipeline.py:166` (`_transition`) | `EVALUATED → FAILED` | ✅ **YES** |
| `fixtures.py:220` / `factories.py:237` (`_swap_state`) | register **#19**'s CAS in **both doubles** | ✅ **YES** |

⚑ The real `PostgresCaseStore._swap_state` is safe — it issues its own `sa.update()` (`repository.py:224-231`) and
never routes through `put_application`. **But both doubles implement `_swap_state` via `put_application`**, so a
change there would silently break register #19's claim mechanism **at tier-U** while tier-I stayed green.

**RESOLUTION DIRECTION — the intent survives; the guard must move OUT of the store and INTO `submit()`.**
`put_application` stays a faithful state-writing upsert; `submit()` stops blindly overwriting an existing
application. **This preserves every legal transition, needs no change to either double's `_swap_state`, and still
closes both #27 and the terminal-state breach.** ⚑ It also *shrinks* Q3's scope — see Fold C. **But exactly what
`submit()` should do on an existing row is a real decision, not a fold: Q7.**

### ✅ Fold C — Q3's scope is SMALLER than feared, and contingent on Q7

Under the Fold-B resolution, **`put_application` is unchanged**, so neither double's `_swap_state` needs touching
and register #19's tier-U coverage is unaffected. The doubles then need only:

1. the **lookup-ordering parity** for `recommendation_for_application` (Q1(A)'s counterpart), and
2. whatever `submit()` no-op/refusal semantics Q7 settles, which lives in `pipeline`, **not** in the store.

**Answering the directed question: no, nothing beyond `fixtures.py` and `factories.py` is required** — *provided*
Q7 keeps the guard out of `put_application`. ⛔ If Q7 instead changes `put_application`, **both doubles'
`_swap_state` must be rewritten too**, and that is a materially larger change to a frozen unit's test surface.

### ⛔ Fold D (DIRECTED, BLOCKING) — "skip gracefully" would print as a FAILURE today

`seed()` (`seed_demo_cases.py:289-292`) prints:

```python
state = "drafted" if outcome.succeeded else f"FAILED ({outcome.failure_reason})"
```

`DraftOutcome` carries only `memo`/`outlier`/`thinking_mode`/`failure_reason`, and `succeeded` is
`memo is not None` (`pipeline.py:39-51`). **There is no way to distinguish a benign "already drafted, skipped" from
a real drafting failure** — the citation-validation failure that produced register #18's whole investigation reports
through the *same* channel. Under Q1(D) cost (3), a routine re-seed would print **`FAILED (…)`** for every
already-drafted case, which is precisely the confusion the answer set was trying to avoid.

✅ **The corpus loud-failure does NOT collide.** It is a *precondition* failure: `build_outlier_model()` raises
`FileNotFoundError` inside `main()` **before any seeding**, propagating as a traceback with a non-zero exit. The
skip is a *per-case* outcome inside `seed()`, benign, exit 0. **Different mechanism, different exit code, different
phase** — they cannot be mistaken for each other. ⚑ But they *would* both be "expected failures" in a reader's
mental model, so the skip must not be implemented as an exception, or that separation collapses.

**How the skip is signalled is a real decision, not a fold: Q8.**

---

## 4. ⛔ NEW QUESTIONS SURFACED BY THE CHECK — answer before the authorization document

### Q7 — where does the guard live, given `put_application` must stay state-writing? (Fold B)

- **(a) Guard inside `pipeline.submit()`: read the existing application first; if one exists and has progressed
  beyond `EVALUATED`, do not overwrite it — return it unchanged. `put_application` is untouched. — RECOMMENDED.**
  It preserves every legal transition, needs **no** change to either double's `_swap_state` (Fold C), keeps the fix
  inside the unit that owns the state machine, and still closes both defects. ⚑ It also puts the decision where the
  domain knowledge already is — `submit()` is the only caller that *isn't* performing a transition.
- **(b) Split the store primitive in two** — `put_application` (state-writing, for transitions) and a new
  `create_or_refresh_application` (never writes `state`, for `submit`). Architecturally cleanest and makes the
  distinction explicit in the Protocol. ⛔ But it widens the frozen-unit change to `store.py`'s Protocol,
  `repository.py`, **and both doubles**, for a distinction `submit()` can enforce by itself.
- **(c) Add a transition guard inside `put_application`** (option E from Q1). Closes the hole for *all* callers,
  not just `submit`. ⛔ Requires an explicit exemption for #19's CAS path and would make the store consult the state
  machine — pushing domain logic into the SQL shim, which its own docstring says *"only executes SQL"*.
- **(d) Leave `submit()` alone and have the SEED SCRIPT check state before calling `submit()`.** Smallest possible
  change and touches **no frozen unit at all**. ⛔ But it fixes only the demo path: any future caller re-submitting
  an application still resurrects a terminal case. It treats the symptom at the one call site we happen to know about.

**[Answer]**: (a) — guard inside pipeline.submit(): read the existing application first, and if it exists and has progressed beyond EVALUATED, return it unchanged rather than overwriting it. put_application stays untouched. This needs no change to either test double's _swap_state, keeps the fix inside the unit that already owns the state machine, and closes both defects (#27's duplicate rows and the terminal-state breach) without widening the reopening beyond what's necessary.

---

### Q8 — how is a benign skip distinguished from a real drafting failure? (Fold D)

- **(a) Add a distinct field to `DraftOutcome`** (e.g. `skipped: bool`, or a small outcome enum) and have `seed()`
  print a third state — `skipped (already drafted)` — beside `drafted` and `FAILED`. **— RECOMMENDED.** It makes
  the distinction **structural rather than textual**, so no caller can conflate them by accident; `DraftOutcome` is
  already the unit's own outcome type and is the right place for it; and it is a **small, additive** change to a
  frozen unit already being reopened. ⚑ The alternative that must be avoided is string-matching `failure_reason`,
  which would couple the script to prose.
- **(b) Have `seed()` consult U24's public `case_to_memo_view_state(app) == "ready"`** and skip before calling
  `draft()`. Uses U24's own pure projection, adds no field. ⛔ But `"ready"` means `DRAFTED` specifically — a
  `COMMITTED` case projects to `"pending"`, so it would **not** be skipped, `draft()` would refuse, and the
  confusing `FAILED (…)` line returns for exactly the case with audit weight.
- **(c) Match on `failure_reason`'s text in the seed script.** Zero schema change. ⛔ Rejected: it couples a script
  to a human-readable string, and the first reword silently reclassifies a skip as a failure.
- **(d) Leave it — accept `FAILED (already drafted)` in the seed output.** Honest in a narrow sense and costs
  nothing, but it trains the operator to ignore `FAILED` lines, which is exactly how the register #18 citation
  defect stayed invisible for so long.

**[Answer]**: (a) — add a distinct field to DraftOutcome (e.g. skipped: bool, or a small outcome enum) so seed() can print a third, honest state ("skipped, already drafted") distinct from both "drafted" and "FAILED". This makes the distinction structural rather than textual, avoiding the string-matching trap and avoiding retraining the operator to ignore FAILED lines the way register #18's citation defect did.

---

## 4.1 ✅ Ambiguity-check RE-RUN against the complete Q1–Q8 set — **CLEAN**

**Answer set**: Q1(D)+(A) · Q2(a) · Q3(a) · Q4(N/A) · Q5(a) · Q6(a) · **Q7(a)** · **Q8(a)**.

**Result: CLEAN. Both blocking folds are resolved by Q7(a)/Q8(a), no new question is surfaced, and the two directed
re-checks below both confirm.** The authorization document can now name its files.

### ✅ Re-check 1 (DIRECTED) — Q7(a) and Q1(D)'s guard-relocation compose; **both are required, neither is redundant**

`submit()` and `draft()` are indeed **different pipeline methods** (`pipeline.py:79` and `:103`), and the two guards
do different jobs at different moments:

| | `submit()` — **Q7(a)** | `draft()` — **Q1(D) costs (1)+(2)** |
|---|---|---|
| **Job** | stop the *state reset* that defeats everything downstream | refuse an *illegal transition* cleanly and early |
| **Mechanism** | read existing app; if past `EVALUATED`, return unchanged | `is_legal(state, DRAFTED)` check moved above `draft_memo` (`:116`), returning a `DraftOutcome` failure |

⚑ **The key finding: `draft()`'s guard is currently DEAD CODE, and Q7(a) is what brings it to life.** Today
`assert_legal(application.state, DRAFTED)` at `:138` can never fire, because `submit()` has always already reset the
state to `EVALUATED`. Once Q7(a) stops that reset, a re-seeded already-drafted case reaches `draft()` **still in
`DRAFTED`** — so the guard becomes **reachable for the first time**. That is precisely why cost (1) (move it above
`draft_memo`) and cost (2) (return rather than raise) are **not optional polish**: without them the newly-live guard
would raise, late, after paying the full drafting cost.

✅ **Cost (2) follows an EXISTING, TESTED convention rather than inventing one.**
`test_trigger.py:58` — `test_drafting_an_unknown_application_returns_a_failure_outcome`, docstring *"No exception
for a domain miss — an ordinary `DraftOutcome` (Q4-A)"* — already pins `draft()` returning an outcome for a domain
miss. The relocated guard is the **same shape as `pipeline.py:106`'s existing unknown-application early return**.

✅ **`DraftOutcome` lives in `pipeline.py:42`** — the *same file* as both guard changes. Q8(a) therefore adds **no
new frozen file** to the reopening, and its only reference outside that file is a docstring mention in
`test_trigger.py:59`, so the additive field has a very small blast radius.

### ✅ Re-check 2 (DIRECTED) — Q3(a)'s double scope is confirmed NARROW

Under Q7(a), **`put_application` is untouched**, so §7.6's wider-rewrite branch **does not fire**: neither double's
`_swap_state` changes and register #19's tier-U coverage is unaffected. `submit()`'s new read uses
`get_application`, which both doubles already implement. **The doubles need exactly one change each — the
lookup-ordering parity for `recommendation_for_application`** — contained to `case_lifecycle/tests/fixtures.py` and
`app/tests/factories.py`. **Confirmed as originally scoped.**

### ⚠️ One limitation of Q1(A), restated so the authorization does not overclaim

`recommendation_id` is `f"REC-{application_id}-{uuid4().hex[:8]}"` (`seed_demo_cases.py`) — a **random** suffix. So
`ORDER BY recommendation_id LIMIT 1` buys **determinism, not chronology**: it will return a *stable* row, not the
*newest* one. That is exactly option (A)'s declared limit ("deterministic but still arbitrary") and it remains the
right trade under Q1(D), because **(D) stops new duplicates from being created at all** — (A) exists to make
pre-existing duplicate data behave predictably, not to pick a winner. ⚑ **The authorization must not claim (A)
"fixes" the selection; it removes the nondeterminism only.**

### ⚑ An honesty note for the authorization

`case_lifecycle` is **NOT** in `test_frozen_untouched.py`'s `FROZEN_UNITS` set (that guard covers the original
eleven). U24's frozen status is therefore a **project-convention and authorization discipline, not a mechanically
enforced one** — which makes the written authorization the *only* real control, and worth stating plainly rather
than implying a guard will catch an overreach.

---

## 5. Manual verification plan (Q6(a) in full) — user-run

**Preconditions**: local Postgres up, migrations applied, a clean `pending_recommendation` table.

1. **Reset**: `DELETE FROM pending_recommendation;` then `DELETE FROM pending_application;` (FK order).
   ⚑ **Do NOT drop the database** — `0002_grants.sql`'s un-guarded `CREATE ROLE` would fail on re-run (roles are
   cluster-level and survive a drop), and dropping destroys the override pass's `AuditRecord a7b67ca8-…`.
2. **Seed once**: `python -m backend.scripts.seed_demo_cases --cases 3`. Confirm one recommendation per application:
   ```sql
   SELECT application_id, COUNT(*) FROM pending_recommendation GROUP BY application_id ORDER BY 1;
   ```
3. **Seed twice more, in sequence.** Then re-run the count query. **Expected depends on Q1**: under (D) the counts
   stay at **1** and the second/third runs **refuse** (message per Q1's sub-decision); under (B) the counts stay at
   **1** by replacement; under (A) alone the counts **grow** and only the *selection* is deterministic — which is
   the honest, disclosed limit of that option.
4. **R4 / R2 resolve correctly**: `curl` `GET /applications/DEMO-0001/memo` and `GET /applications`, confirming the
   `recommendation_id` served matches the intended row from `psql`.
5. ⚑ **The terminal-state breach must NOT reproduce**: commit a case through R5 so it reaches `committed`, then
   re-run the seed, then:
   ```sql
   SELECT application_id, state FROM pending_application WHERE application_id = 'DEMO-0001';
   ```
   **Expected: still `committed`.** A value of `evaluated` means the breach survives — **blocking**.
6. **Register #19 still holds**: after the above, a commit attempt on an already-committed recommendation returns
   **409**, and an unknown `recommendation_id` returns **404** (§1.5's disambiguation intact).

**Stop-gate**: any of steps 3–6 deviating → **stop and report** before any doc update or commit.

---

## 6. Holds for this pass

| Hold | Status at the plan gate |
|---|---|
| No backend file touched | ✅ Read-only throughout. One in-memory execution to confirm §1.2; nothing written. |
| No frozen unit edited | ✅ `case_lifecycle/` read only. **The reopening is proposed, not taken.** |
| WIRE-1 untouched | ✅ Not read for modification; §1.4 notes only that R5's 404/409 mapping constrains the design. |
| No code written | ✅ Files written: **1** — this plan. |
| No commit | ✅ User's call. |
| Register status unchanged | ✅ **#27 open, unmodified.** Q2 proposes a possible new item; none opened yet. |

---

## 7. Carried forward — do not lose these

1. ⚑ **The never-deleted assumption (§1.5)** is load-bearing for R5's 404-vs-409. Whichever option wins, the plan's
   execution must state explicitly whether it still holds, and if not, what replaces the reasoning.
2. ⚑ **Under Q1(D), the guard's POSITION must move** — it currently sits after `draft_memo`, so a refused re-seed
   pays the full drafting cost (real money under `--real-llm`) before throwing.
3. **The #19 duplicate interaction (§1.4)**: with duplicates present, committing one recommendation makes its
   siblings permanently unclaimable. Any fix should be checked against this rather than assumed to resolve it.
4. **`reconcile_committing_cases.py`** is a third consumer of the ambiguous lookup and is easy to forget — it is
   not a route and will not surface in wire testing.
5. ⛔ **Q7 and Q8 must be answered before the authorization document can be written** — Q7 determines which frozen files
   the reopening names, and Q5(a) requires those to be named explicitly rather than scoped loosely.

6. ⚑ **Q3(a)'s scope is CONTINGENT on Q7.** Under Q7(a) the doubles need only the lookup-ordering parity, contained
   to `fixtures.py` + `factories.py`. Under any option that changes `put_application`, **both doubles' `_swap_state`
   must be rewritten too** or register #19's claim mechanism silently breaks at tier-U.

---

## 8. ⚑ Separate small note — a documentation inconsistency, not urgent

**Two files disagree about which reopening was U24's "third".**

* `backend/app/routes/not_wired.py:176` — *"U24's OWN thin adapter (its **third** authorized reopening, Q14-A)"*
* `backend/case_lifecycle/store.py:75` — *"register #19: the two-step commit claim (U24's **THIRD** authorized
  reopening)"*

`BUILD-COMPLETION-REPORT.md:198` and `:303` are the authoritative record and support **`store.py`**: the Scope B
wiring pass required **two** reopenings (`list_application_ids()`, `memo_from_canonical()`), making #19's fix the
**third**. So `not_wired.py:176`'s "third" is off by one and should read **second**.

⚑ **Not fixed here** — it is a comment in a file this pass has no other reason to touch, and correcting it should
follow the project's **supersede-not-rewrite** discipline (preserve the original text, state what changed and why),
the same shape used for `seams.js`, `httpTransport.js`, register #17 and the `app.test.jsx` rename. **Worth
correcting for the record at some point; nothing depends on it.**

---

## 9. What fixing #27 would and would not deliver

**Would**: make R4 and R2 resolve an application's recommendation unambiguously; stop unbounded row growth (under
B/C/D); close the terminal-state breach (under D/E, subject to Q2's framing); and — under Q3(a) — remove the
test-double blindness that let this class of defect reach production unseen.

**Would not**: discharge **#2** (still no drafting trigger in the API) · address **#26** (Q4(a) inherits it, never
claims it) · touch **#17**'s deferred mount pass · change anything about the commit boundary, which resolves by
primary key and was never affected.
