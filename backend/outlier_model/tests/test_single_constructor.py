"""NFR-OUT-EXPLAIN-1 (structural half) — ``FlaggedFeature`` is constructed in exactly one place.

AST scan: the ONLY call-site that constructs a ``FlaggedFeature(...)`` across all production
modules is in ``shap_explainer.py`` (the sole constructor — P-OUT-4). A ``class FlaggedFeature``
definition and ``-> list[FlaggedFeature]`` annotations are NOT calls, so they do not count.
"""
from __future__ import annotations

import ast

from backend.outlier_model.tests import structural


def _flagged_feature_construction_sites(tree: ast.AST) -> int:
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "FlaggedFeature"
    )


def test_flagged_feature_constructed_in_exactly_one_place():
    sites = {
        path.name: _flagged_feature_construction_sites(structural.parse(path))
        for path in structural.production_py_files()
    }
    constructing = {name: n for name, n in sites.items() if n > 0}
    assert constructing == {"shap_explainer.py": 1}, f"construction sites: {sites}"


def test_scan_sees_the_real_production_modules():
    names = {p.name for p in structural.production_py_files()}
    assert structural.EXPECTED_PRODUCTION_MODULES <= names


def test_detector_flags_a_synthetic_second_constructor():
    synthetic = (
        "a = FlaggedFeature(feature='x', z_score=1.0, shap_value=0.1, direction=d)\n"
        "b = FlaggedFeature(feature='y', z_score=2.0, shap_value=0.2, direction=d)\n"
    )
    assert _flagged_feature_construction_sites(structural.parse_source(synthetic)) == 2
