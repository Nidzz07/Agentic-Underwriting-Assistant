"""NFR-OUT-THRESHOLD-1 — one fixed, strictly-positive, parameterized threshold (BR-OUT-6).

(a) Exactly one named ``Z_SCORE_FLAG_THRESHOLD`` module-level literal. (b) Strictly ``> 0``
(positivity guard — a threshold <= 0 is degenerate). (c) Flag-selection tested off the SAME
named constant the production code reads (never a hardcoded 3.0), plus an inclusive-boundary
case at ``|z| == threshold``.
"""
from __future__ import annotations

import ast

from backend.outlier_model import model as model_module
from backend.outlier_model.model import (
    Z_SCORE_FLAG_THRESHOLD,
    _candidates,
    _is_flag,
)
from backend.outlier_model.feature_vector import FeatureVectorBuilder


def test_threshold_is_strictly_positive():
    assert Z_SCORE_FLAG_THRESHOLD > 0


def test_exactly_one_threshold_literal_at_module_level():
    tree = ast.parse(model_module.__file__ and open(model_module.__file__, encoding="utf-8").read())
    assignments = [
        node
        for node in tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "Z_SCORE_FLAG_THRESHOLD"
    ]
    assert len(assignments) == 1
    assert isinstance(assignments[0].value, ast.Constant)  # a literal, not a computed/random value


def test_flag_predicate_is_inclusive_at_the_boundary():
    # |z| == threshold ⇒ flagged (inclusive); just below ⇒ not; the mirrored negative tail too.
    assert _is_flag(Z_SCORE_FLAG_THRESHOLD, Z_SCORE_FLAG_THRESHOLD) is True
    assert _is_flag(-Z_SCORE_FLAG_THRESHOLD, Z_SCORE_FLAG_THRESHOLD) is True
    assert _is_flag(Z_SCORE_FLAG_THRESHOLD - 1e-9, Z_SCORE_FLAG_THRESHOLD) is False
    assert _is_flag(0.0, Z_SCORE_FLAG_THRESHOLD) is False


def test_candidate_selection_is_parameterized_off_the_constant():
    order = FeatureVectorBuilder.field_order()
    # a z-vector: exactly one feature sits at the boundary, the rest below.
    zs = tuple(Z_SCORE_FLAG_THRESHOLD if i == 0 else 0.5 for i in range(len(order)))
    candidates = _candidates(zs, order, Z_SCORE_FLAG_THRESHOLD)
    assert [c.feature for c in candidates] == [order[0]]
    # raising the threshold above the boundary drops the candidate (parameterized, not hardcoded).
    assert _candidates(zs, order, Z_SCORE_FLAG_THRESHOLD + 1.0) == []
