"""NFR-MEXT-BIAS-1 — the MCP surfaces are DEMOGRAPHIC-FREE BY CONSTRUCTION (BR-MEXT-9 /
CON-BR1 / skill #6 / Q3-A). Asymmetric: swap teeth on ``decisions-tools``' OUTPUT
PROJECTION (where the leak could live), a stronger by-construction argument for
``rulebook-tools`` (takes no applicant input). The shared demographic AST scan + its
detector self-test live in ``test_structural_guard.py``.
"""
from __future__ import annotations

import inspect

from backend.memo_extensions import mcp_tools as mt
from backend.memo_extensions.tests import fixtures as fx


def test_decisions_tools_swap_over_demographics_yields_identical_projection():
    a, b = fx.demographic_swap_pair()  # identical financials/recommendation; swapped name/gender/city
    projection_a = mt.DecisionsTools(fx.FakeDecisionRecordSource([a])).recent_precedent(mt.PrecedentQuery())
    projection_b = mt.DecisionsTools(fx.FakeDecisionRecordSource([b])).recent_precedent(mt.PrecedentQuery())
    assert projection_a == projection_b
    # byte-identical projection (directly proving the demographics are dropped)
    assert [p.model_dump() for p in projection_a] == [p.model_dump() for p in projection_b]


def test_rulebook_tools_takes_no_applicant_parameter():
    # strictly stronger than a swap test that could not fail — no applicant can ENTER.
    params = list(inspect.signature(mt.RulebookTools.describe_rules).parameters)
    assert params == ["self", "rule_ids"]


def test_projection_and_query_types_declare_no_demographic_field():
    demographic = {"full_name", "gender", "city", "demographics"}
    for model in (mt.PrecedentSummary, mt.RuleDescription, mt.PrecedentQuery, mt.SupplementaryContext):
        assert not (set(model.model_fields) & demographic), model.__name__


def test_precedent_summary_is_frozen_extra_forbid():
    # the FeatureInputs analog: a demographic is unrepresentable (extra="forbid").
    assert mt.PrecedentSummary.model_config.get("frozen") is True
    assert mt.PrecedentSummary.model_config.get("extra") == "forbid"
