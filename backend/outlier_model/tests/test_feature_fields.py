"""NFR-OUT-FEAT-1 — numeric-only allow-list; documented categorical exclusions (BR-OUT-2).

Every allow-list field maps to a numeric profile value; the three categoricals
(``employment_type`` / ``smoking_status`` / ``occupation``) are absent; each exclusion is
documented in ``domain-entities.md §2.2`` (doc check). ``FeatureInputs`` is numeric-only.
"""
from __future__ import annotations

import dataclasses
import pathlib

from backend.outlier_model.feature_fields import OUTLIER_FEATURE_FIELDS, FeatureInputs

_EXPECTED_FIELDS = {
    "age_years_derived",
    "bmi_derived",
    "verifiable_income_annual",
    "existing_debt_obligations_annual",
    "requested_cover_amount",
    "dti_ratio",
    "income_multiple",
    "health_flag_count",
    "documents_missing_count",
}
_EXCLUDED_CATEGORICALS = {"employment_type", "smoking_status", "occupation"}
_DEMOGRAPHICS = {"full_name", "gender", "city", "demographics"}


def test_allowlist_is_the_nine_numeric_names():
    assert OUTLIER_FEATURE_FIELDS == _EXPECTED_FIELDS
    assert len(OUTLIER_FEATURE_FIELDS) == 9


def test_categoricals_and_demographics_absent():
    assert _EXCLUDED_CATEGORICALS.isdisjoint(OUTLIER_FEATURE_FIELDS)
    assert _DEMOGRAPHICS.isdisjoint(OUTLIER_FEATURE_FIELDS)


def test_feature_inputs_is_numeric_only():
    field_names = {f.name for f in dataclasses.fields(FeatureInputs)}
    assert field_names == {"values", "imputed"}
    assert _DEMOGRAPHICS.isdisjoint(field_names)


def test_domain_entities_documents_each_categorical_exclusion():
    doc = (
        pathlib.Path(__file__).resolve().parents[3]
        / "guide-docs" / "build" / "outlier-model" / "functional-design" / "domain-entities.md"
    )
    text = doc.read_text(encoding="utf-8")
    for categorical in _EXCLUDED_CATEGORICALS:
        assert categorical in text, f"{categorical} exclusion not documented in domain-entities.md"
