"""MemoHashAdapter — HASH-1 (deterministic compute) + REPLAY-1 (standalone verify).

All deterministic, no provider anywhere.
"""
from __future__ import annotations

import inspect

from backend.common.canon_ser import content_hash
from backend.rules_engine.report_schema import Confidence, Recommendation
from backend.rules_engine.report import evaluation_output
from backend.memo_agent_core import memo_hash_adapter as mha_module
from backend.memo_agent_core.memo_hash_adapter import MemoHashAdapter
from backend.memo_agent_core.schemas import (
    DecisionMemo,
    MissingInfoSource,
    MissingInformationItem,
)
from backend.memo_agent_core.tests.fixtures.factories import make_report


ADAPTER = MemoHashAdapter()

_CONTENT = dict(
    narrative_prose="Advisory memo prose citing R-AGE-1.",
    cited_rule_ids=["R-AGE-1", "R-DTI-1"],
    missing_information=[
        MissingInformationItem(source=MissingInfoSource.NOT_EVALUATED_RULE, detail="R-DTI-1"),
        MissingInformationItem(source=MissingInfoSource.INCOMPLETE_FLAG, detail="profile_incomplete"),
    ],
    recommendation=Recommendation.REFER,
    confidence=Confidence.MEDIUM,
)


def _memo(memo_hash: str, *, model_version: str = "fake-1", **overrides) -> DecisionMemo:
    content = {**_CONTENT, **overrides}
    return DecisionMemo(memo_hash=memo_hash, model_version=model_version, **content)


# --------------------------------------------------------------------------
# HASH-1 — deterministic compute
# --------------------------------------------------------------------------
def test_compute_is_deterministic_across_runs():
    hashes = {ADAPTER.compute(**_CONTENT) for _ in range(5)}
    assert len(hashes) == 1


def test_byte_identical_to_an_independent_canon_ser_recompute():
    independent = content_hash({
        "narrative_prose": _CONTENT["narrative_prose"],
        "cited_rule_ids": list(_CONTENT["cited_rule_ids"]),
        "missing_information": [
            {"source": i.source.value, "detail": i.detail} for i in _CONTENT["missing_information"]
        ],
        "recommendation": _CONTENT["recommendation"].value,
        "confidence": _CONTENT["confidence"].value,
    })
    assert ADAPTER.compute(**_CONTENT) == independent


def test_each_hashed_field_change_changes_the_hash():
    base = ADAPTER.compute(**_CONTENT)
    assert ADAPTER.compute(**{**_CONTENT, "narrative_prose": "different prose"}) != base
    assert ADAPTER.compute(**{**_CONTENT, "cited_rule_ids": ["R-AGE-1"]}) != base
    assert ADAPTER.compute(**{**_CONTENT, "recommendation": Recommendation.APPROVE}) != base
    assert ADAPTER.compute(**{**_CONTENT, "confidence": Confidence.LOW}) != base
    assert ADAPTER.compute(**{**_CONTENT, "missing_information": []}) != base


def test_missing_information_order_changes_the_hash():
    # canon_ser preserves list order — a permuted list is a different hash, which
    # is exactly why MissingInfoDeriver must emit a FIXED total order (HASH-1).
    reordered = list(reversed(_CONTENT["missing_information"]))
    assert ADAPTER.compute(**{**_CONTENT, "missing_information": reordered}) != ADAPTER.compute(**_CONTENT)


# --------------------------------------------------------------------------
# REPLAY-1 — standalone verify, no LLM/provider; memo not in the rules-equality set
# --------------------------------------------------------------------------
def test_volatile_metadata_excluded_from_the_hash():
    h = ADAPTER.compute(**_CONTENT)
    # Two memos with identical content but different model_version verify against
    # the SAME hash — model_version (and memo_hash itself) are not hashed.
    assert ADAPTER.verify(_memo(h, model_version="fake-1")) is True
    assert ADAPTER.verify(_memo(h, model_version="gemini-9")) is True


def test_verify_true_on_match_false_on_content_tamper():
    h = ADAPTER.compute(**_CONTENT)
    assert ADAPTER.verify(_memo(h)) is True
    # Same recorded hash, but a tampered content field → verify fails.
    assert ADAPTER.verify(_memo(h, narrative_prose="tampered")) is False


def test_verify_constructs_no_provider():
    # REPLAY-1 structural: the memo-hash path references no ProviderAbstraction.
    src = inspect.getsource(mha_module)
    assert "ProviderAbstraction" not in src
    assert "import" in src and "provider" not in src.split("class MemoHashAdapter")[0].lower()
    # verify takes only a memo — no provider parameter.
    assert list(inspect.signature(MemoHashAdapter.verify).parameters) == ["self", "memo"]


def test_memo_is_not_in_the_rules_replay_equality_set():
    # REPLAY-1: rules-engine's evaluation_output (the replay equality set) carries
    # no memo content — the memo is verified by hash, separately.
    proj = evaluation_output(make_report())
    assert "memo_hash" not in proj
    assert "narrative_prose" not in proj
    assert set(proj) == {"rule_results", "recommendation", "confidence", "decline_reasons", "refer_reasons"}
