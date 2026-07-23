"""NFR-MEXT-SIGNAL-1 — handed-in outlier signal; no outlier-model edge; None degrades
(BR-MEXT-2 / Q2-A). By-shape fake drives routing; interop self-test proves a real U18
``OutlierResult`` (built BY VALUE, never imported) satisfies the ``@runtime_checkable``
Protocol; None runs on rule-proximity alone. The no-``outlier_model``-import AST scan lives
in ``test_structural_guard.py``.
"""
from __future__ import annotations

from decimal import Decimal

from backend.memo_agent_core.schemas import ThinkingMode
from backend.rules_engine.report_schema import Recommendation
from backend.memo_extensions.borderline_router import (
    OUTLIER_SCORE_CUTOFF,
    OutlierSignal,
    route_borderline,
)
from backend.memo_extensions.tests import fixtures as fx


def _standard_report():
    return fx.make_report(
        rule_results=[fx.make_rule_result(actual_value=Decimal("0.20"), threshold=Decimal("0.40"))],
        recommendation=Recommendation.APPROVE,
    )


def test_by_shape_fake_drives_routing_no_u18_import():
    signal = fx.FakeOutlierSignal(is_outlier=True, outlier_score=OUTLIER_SCORE_CUTOFF + 0.2)
    assert route_borderline(_standard_report(), signal) is ThinkingMode.EXTENDED


def test_interop_by_value_u18_outlier_result_satisfies_protocol():
    # A real U18 OutlierResult SHAPE, constructed BY VALUE (never imported), carrying the
    # extra prose/trace fields — still satisfies the narrow OutlierSignal Protocol.
    by_value = fx.ByValueOutlierResult(
        is_outlier=True, outlier_score=0.9,
        flagged_features=["dti_ratio"], provenance={"corpus_version": "c1"},
    )
    assert isinstance(by_value, OutlierSignal)  # discriminating structural check (3.12)
    # and it routes exactly like any signal above the cutoff
    assert route_borderline(_standard_report(), by_value) is ThinkingMode.EXTENDED


def test_non_signal_object_is_rejected_by_protocol():
    assert not isinstance(object(), OutlierSignal)  # not vacuous


def test_none_degrades_to_rule_proximity_alone():
    report = _standard_report()
    # None must equal the rule-proximity-only result over the same report
    assert route_borderline(report, None) is route_borderline(report)
    assert route_borderline(report, None) is ThinkingMode.STANDARD


def test_none_still_honors_rule_proximity_trigger():
    near = Decimal("0.40") * Decimal("0.99")  # well within the relative margin
    report = fx.make_report(
        rule_results=[fx.make_rule_result(actual_value=near, threshold=Decimal("0.40"))],
        recommendation=Recommendation.APPROVE,
    )
    assert route_borderline(report, None) is ThinkingMode.EXTENDED
