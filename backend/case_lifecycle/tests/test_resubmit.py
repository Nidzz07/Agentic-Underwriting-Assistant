"""RESUBMIT-1 — re-submitting an existing application must not rewrite its state.

⛔ **The defect this file exists for (register #27 + #28).** ``submit()`` built a fresh
``PendingApplication`` at ``EVALUATED`` and handed it to ``put_application``, whose upsert writes
``state``. So **every** re-submission reset the row's state, with two consequences:

  * **#27** — the reset made ``(EVALUATED, DRAFTED)`` legal again, so ``draft()``'s guard never
    fired and a second ``pending_recommendation`` row was inserted on every re-seed, unbounded.
  * **#28** — a **terminal** ``COMMITTED`` case was silently reset to ``EVALUATED`` and became
    re-draftable, *after* it had already been committed to the audit trail. Measured, not
    inferred: ``COMMITTED`` -> re-submit -> ``EVALUATED``.

⚑ **The fix is in ``submit()``, NOT in ``put_application``** (remediation-plan Q7(a)).
``put_application`` is the sole state-writing primitive for ``draft()``'s ``EVALUATED -> DRAFTED``,
``_transition``'s ``EVALUATED -> FAILED``, **and register #19's CAS inside both test doubles** —
changing it would break all three. The guard therefore lives in the one caller that is *not*
performing a transition.

⚑ **``draft()``'s legality guard was DEAD CODE until this fix.** It could never fire, because
``submit()`` had always already reset the state. Fixing ``submit()`` makes it reachable for the
first time, which is why it also moves **above** ``draft_memo`` and returns a ``DraftOutcome``
instead of raising — otherwise a refused re-seed would raise *late*, after paying the full
drafting cost (real money under ``--real-llm``).

tier-U: no database, no network.
"""
from __future__ import annotations

from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.states import CaseState
from backend.case_lifecycle.tests import fixtures as fx


def _pipeline(store, seams=None):
    return CasePipeline(
        store, seams if seams is not None else fx.drafting_success_double(),
        fx.recommendation_id_factory,
    )


# ---------------------------------------------------------------------------
# (a) submit() must not rewrite an existing application's state
# ---------------------------------------------------------------------------
def test_submitting_an_already_drafted_application_leaves_it_drafted():
    """A1 — register #27's root cause.

    Before the fix this returned the row reset to ``EVALUATED``, which re-legalized drafting and
    let a second recommendation be inserted.
    """
    store = fx.InMemoryCaseStore()
    application_id, raw = fx.clean_case()
    pipeline = _pipeline(store)
    pipeline.submit(application_id, raw)
    pipeline.draft(application_id)
    assert store.get_application(application_id).state is CaseState.DRAFTED

    pipeline.submit(application_id, raw)

    assert store.get_application(application_id).state is CaseState.DRAFTED


def test_submitting_a_committed_application_does_not_resurrect_it():
    """A2 — register #28, the finding with audit weight.

    ⛔ A ``COMMITTED`` case is TERMINAL. Resetting it to ``EVALUATED`` made a case that had
    already been committed to the audit trail re-draftable — an illegal write to a terminal
    state, reachable from an ordinary re-seed.
    """
    store = fx.InMemoryCaseStore()
    application_id, raw = fx.clean_case()
    with store.atomic():
        store.put_application(fx.make_application(application_id, CaseState.COMMITTED))
    assert store.get_application(application_id).state is CaseState.COMMITTED

    _pipeline(store).submit(application_id, raw)

    assert store.get_application(application_id).state is CaseState.COMMITTED, (
        "a terminal committed case must never be reset by a re-submission"
    )


def test_submitting_a_fresh_application_still_creates_it_at_evaluated():
    """A3 — the regression pin: the guard must not break the ordinary first submit.

    ⚠️ VACUOUS ON ARRIVAL by design — it pins CURRENT behaviour. Its RED is demonstrated by
    execution, not asserted: with the guard made unconditional (refusing every submit), this
    test FAILS. It is green here because the guard is correctly conditional.
    """
    store = fx.InMemoryCaseStore()
    application_id, raw = fx.clean_case()

    application = _pipeline(store).submit(application_id, raw)

    assert application.state is CaseState.EVALUATED
    assert store.get_application(application_id).state is CaseState.EVALUATED


def test_resubmitting_an_evaluated_application_still_refreshes_it():
    """A4 — the guard fires only for cases that have PROGRESSED BEYOND ``evaluated``.

    An application still at ``evaluated`` has not been drafted, so re-submitting it is an
    ordinary refresh and must keep working — re-evaluating against a possibly-updated rulebook is
    exactly what a re-seed of an undrafted case is for.

    ⚠️ VACUOUS ON ARRIVAL by design. Its RED is demonstrated by widening the guard to also refuse
    ``EVALUATED``, which makes this test FAIL.
    """
    store = fx.InMemoryCaseStore()
    application_id, raw = fx.clean_case()
    seams = fx.drafting_success_double()
    pipeline = _pipeline(store, seams)
    pipeline.submit(application_id, raw)

    seams.calls.clear()
    application = pipeline.submit(application_id, raw)

    assert application.state is CaseState.EVALUATED
    # it really re-ran the evaluation rather than short-circuiting
    assert "evaluate" in seams.calls


# ---------------------------------------------------------------------------
# (b) draft()'s legality guard — now REACHABLE, so it must refuse cleanly and EARLY
#
# ⚑ Until change (a), this guard was DEAD CODE: `submit()` always reset the state to `evaluated`
# first, so `(evaluated -> drafted)` was always legal and `assert_legal` could never fire. These
# two tests are only meaningful because (a) brought it to life.
# ---------------------------------------------------------------------------
def test_drafting_an_already_drafted_case_returns_a_failure_not_an_exception():
    """B1 — `draft()` promises it "never raises for a domain failure" (Q4-A).

    Refusing a re-draft is a domain failure, so it must come back as a `DraftOutcome` — the same
    shape as the unknown-application miss that `test_trigger.py` already pins.
    """
    store = fx.InMemoryCaseStore()
    application_id, raw = fx.clean_case()
    pipeline = _pipeline(store)
    pipeline.submit(application_id, raw)
    pipeline.draft(application_id)

    outcome = pipeline.draft(application_id)      # must NOT raise

    assert not outcome.succeeded
    assert outcome.failure_reason
    assert store.get_application(application_id).state is CaseState.DRAFTED


def test_the_re_draft_refusal_happens_before_any_drafting_work():
    """B2 — the guard must sit ABOVE `draft_memo`, not below it.

    ⚑ This is the half that costs real money if it regresses: `draft_memo` is the LLM-bearing
    call, and with `--real-llm` a refused re-seed that still drafted would spend on a memo it
    then throws away. A SPY proves the work never happened, rather than inferring it from timing.
    """
    store = fx.InMemoryCaseStore()
    application_id, raw = fx.clean_case()
    seams = fx.drafting_success_double()
    pipeline = _pipeline(store, seams)
    pipeline.submit(application_id, raw)
    pipeline.draft(application_id)

    seams.calls.clear()
    pipeline.draft(application_id)

    assert "draft_memo" not in seams.calls, "the refusal must precede the LLM-bearing call"
    assert "score_outlier" not in seams.calls, "and precede outlier scoring too"


# ---------------------------------------------------------------------------
# (c) a benign skip must be STRUCTURALLY distinguishable from a real failure
#
# ⛔ Why this is a field and not a string: `seed()` prints `"drafted" if succeeded else
# f"FAILED ({failure_reason})"`, so without a discriminator a routine re-seed reports `FAILED` on
# every already-drafted case. That trains the operator to ignore FAILED lines — which is exactly
# how register #18's citation defect (every case silently FAILED) stayed invisible. Matching on
# `failure_reason`'s prose would couple the script to wording; a field cannot drift.
# ---------------------------------------------------------------------------
def test_a_re_draft_refusal_is_marked_skipped():
    """C1 — the benign case carries the discriminator."""
    store = fx.InMemoryCaseStore()
    application_id, raw = fx.clean_case()
    pipeline = _pipeline(store)
    pipeline.submit(application_id, raw)
    pipeline.draft(application_id)

    outcome = pipeline.draft(application_id)

    assert outcome.skipped is True
    assert not outcome.succeeded          # a skip is still "not a success"


def test_a_real_drafting_failure_is_not_marked_skipped():
    """C2 — the discriminator must actually DISCRIMINATE.

    ⚑ This is the half that makes C1 non-trivial: a genuine drafting failure (the memo came back
    `None` after citation validation gave up — register #18's shape) must NOT be reported as a
    skip, or the field would be worse than useless.
    """
    store = fx.InMemoryCaseStore()
    application_id, raw = fx.clean_case()
    pipeline = _pipeline(store, fx.drafting_failure_double())
    pipeline.submit(application_id, raw)

    outcome = pipeline.draft(application_id)

    assert outcome.skipped is False
    assert not outcome.succeeded
    assert store.get_application(application_id).state is CaseState.FAILED
