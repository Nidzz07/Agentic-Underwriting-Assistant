"""NFR-OUT-BIAS-1 (structural half) — no production module reads a demographic attribute.

AST scan: no ``.demographics`` / ``.full_name`` / ``.gender`` / ``.city`` attribute access in any
production module (the feature flow is demographic-excluded BY CONSTRUCTION — a demographic value
is structurally unnameable). Plus the allow-list identity
``set(FeatureVectorBuilder.field_order()) == OUTLIER_FEATURE_FIELDS``. AST (not text) so the
header comments that legitimately mention "gender"/"city" do not misfire.
"""
from __future__ import annotations

import ast

from backend.outlier_model.feature_fields import OUTLIER_FEATURE_FIELDS
from backend.outlier_model.feature_vector import FeatureVectorBuilder
from backend.outlier_model.tests import structural

_DEMOGRAPHIC_ATTRS = {"demographics", "full_name", "gender", "city"}


def _demographic_attribute_reads(tree: ast.AST) -> set[str]:
    return {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr in _DEMOGRAPHIC_ATTRS
    }


def test_no_production_module_reads_a_demographic_attribute():
    offenders: list[str] = []
    for path in structural.production_py_files():
        hits = _demographic_attribute_reads(structural.parse(path))
        if hits:
            offenders.append(f"{path.name}: {sorted(hits)}")
    assert offenders == [], f"demographic attribute reads found: {offenders}"


def test_field_order_equals_the_allowlist():
    assert set(FeatureVectorBuilder.field_order()) == OUTLIER_FEATURE_FIELDS


def test_scan_sees_the_real_production_modules():
    names = {p.name for p in structural.production_py_files()}
    assert structural.EXPECTED_PRODUCTION_MODULES <= names


def test_detector_flags_a_synthetic_demographic_read():
    synthetic = "def f(profile):\n    return profile.demographics.city + profile.demographics.full_name\n"
    hits = _demographic_attribute_reads(structural.parse_source(synthetic))
    assert {"demographics", "city", "full_name"} <= hits
