"""Register #34 ``CHECKPOINT-POISONS-REDRAFT`` — the re-draft regression test (Q9-D).

⛔ **The defect this pins**: ``_build_graph`` compiled the graph with a ``MemorySaver``
checkpointer, and ``run()`` keys the thread by ``application_id``. On the SECOND invoke of
the same application the channels are **restored rather than MISSING**, so seeding takes the
reducer branch and :func:`_reject_channel_write` fires on the **seed** — a case no node ever
wrote. Drafting the same application twice therefore raised ``RuntimeError``.

⚑ **Four independent layers (Q9-D)**, each a separate test, because each kills a different
wrong implementation:

* **(i)** both invokes return a real, citation-valid ``DecisionMemo`` — kills a test that only
  asserts "no exception was raised".
* **(ii)** the compiled graph structurally has **no checkpointer** — kills ⛔ a future
  reintroduction that is re-masked by a guard somewhere else (**the ``3a08dd8`` failure mode**).
* **(iii)** the two memos' ``memo_hash`` values are **equal** — kills a re-draft that succeeds
  but produces a different memo.
* **(iv)** the provider's call count **increments** on invoke #2 — ⛔ kills the strawman: an
  implementation that memoizes by ``application_id`` satisfies (i), (ii) and (iii) while
  reintroducing the defect in another form.

⚠️ **Construction requirements** (parent plan §1.4 / §6.3): each test builds its **own**
``LangGraphOrchestrator`` — never through ``case_seams()``, whose ``@lru_cache(maxsize=1)``
would leak state between tests — and uses the **existing** ``FakeProvider``. ⛔ **No XML and no
real client anywhere**, which is what makes this test independent of #33.
"""
from __future__ import annotations

from backend.memo_agent_core.memo_hash_adapter import MemoHashAdapter
from backend.memo_agent_core.orchestrator import LangGraphOrchestrator
from backend.memo_agent_core.tests.fixtures.factories import make_input, make_report, make_rulebook
from backend.memo_agent_core.tests.fixtures.fake_provider import FakeProvider, valid_output

_RULE_IDS = ("R-AGE-1", "R-DTI-1")
_CITED = ["R-AGE-1"]


def _build():
    """A fresh orchestrator + input. ⚠️ Its own instance, never ``case_seams()``."""
    report = make_report(rule_ids=_RULE_IDS)
    agent_input = make_input(report=report)
    orch = LangGraphOrchestrator(
        # The last scripted entry repeats, so EVERY attempt returns the same valid draft.
        FakeProvider([valid_output(_CITED)]),
        rulebook=make_rulebook(rule_ids=_RULE_IDS),
        model_version="fake-provider",
        telemetry=None,
    )
    return orch, agent_input


# --------------------------------------------------------------------------
# Layer (i) — a memo on BOTH invokes, not merely the absence of an exception
# --------------------------------------------------------------------------
def test_drafting_the_same_application_twice_returns_a_memo_BOTH_times():
    orch, agent_input = _build()

    memo1 = orch.run(agent_input)
    memo2 = orch.run(agent_input)  # ⛔ this is the invoke that used to raise

    assert memo1 is not None, "invoke #1 produced no memo"
    assert memo2 is not None, "invoke #2 produced no memo — the re-draft is still broken"
    # Not just "a memo": a VERIFIABLE one that cited a real, listed rule both times.
    assert MemoHashAdapter().verify(memo1) is True
    assert MemoHashAdapter().verify(memo2) is True
    assert memo1.cited_rule_ids == _CITED
    assert memo2.cited_rule_ids == _CITED


# --------------------------------------------------------------------------
# Layer (ii) — STRUCTURAL: the compiled graph has no checkpointer at all
# --------------------------------------------------------------------------
def test_the_compiled_graph_has_NO_checkpointer():
    """⛔ The structural pin. Without it, a reintroduced checkpointer that is merely
    re-masked by a guard elsewhere would pass every behavioural test above — which is
    precisely how ``3a08dd8``'s defect class survives a green suite."""
    orch, _ = _build()

    assert orch._graph.checkpointer is None


# --------------------------------------------------------------------------
# Layer (iii) — the SAME memo, not merely A memo
# --------------------------------------------------------------------------
def test_the_two_drafts_produce_an_IDENTICAL_memo_hash():
    orch, agent_input = _build()

    memo1 = orch.run(agent_input)
    memo2 = orch.run(agent_input)

    assert memo1.memo_hash == memo2.memo_hash


# --------------------------------------------------------------------------
# Layer (iv) — ⛔ the non-vacuity guard that kills the memoizer strawman
# --------------------------------------------------------------------------
def test_invoke_2_REALLY_re_drafts_rather_than_replaying_a_cached_memo():
    """⚑ An implementation memoizing by ``application_id`` would satisfy layers (i), (ii)
    and (iii) while never re-drafting at all. Only the provider's call count can tell the
    difference between "re-drafted successfully" and "handed back the first answer"."""
    orch, agent_input = _build()

    orch.run(agent_input)
    after_first = orch._provider.call_count
    orch.run(agent_input)
    after_second = orch._provider.call_count

    assert after_first == 1
    assert after_second == 2, (
        "the provider was not called again on invoke #2 — the memo was replayed, not re-drafted"
    )
