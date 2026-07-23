"""NFR-OUT-EXPLAIN-1 (construction) — a flag cannot be built without its SHAP value (BR-OUT-7).

Construction-time: ``FlaggedFeature(...)`` omitting ``shap_value`` RAISES (required, no default);
an extra field is forbidden; every flag in every scored result carries a finite ``shap_value``.
"""
from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.model import OutlierModel
from backend.outlier_model.schemas import FlagDirection, FlaggedFeature
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.outlier_model.tests import fixtures as F


def test_flagged_feature_requires_shap_value():
    with pytest.raises(ValidationError):
        FlaggedFeature(feature="dti_ratio", z_score=3.2, direction=FlagDirection.HIGH)


def test_flagged_feature_forbids_extra_fields():
    with pytest.raises(ValidationError):
        FlaggedFeature(
            feature="dti_ratio",
            z_score=3.2,
            shap_value=0.1,
            direction=FlagDirection.HIGH,
            surprise="nope",
        )


def test_valid_construction_succeeds():
    flag = FlaggedFeature(
        feature="dti_ratio", z_score=3.2, shap_value=0.1, direction=FlagDirection.HIGH
    )
    assert flag.shap_value == 0.1


def test_every_flag_in_a_scored_result_carries_a_finite_shap_value():
    profiles = CorpusSource.profiles(F.corpus_records())
    fitted = OutlierModel.fit(profiles, F.make_manifest(), ShapExplainer())
    result = fitted.score(F.outlier_profile())
    assert result.flagged_features  # the outlier actually flags something
    for flag in result.flagged_features:
        assert math.isfinite(flag.shap_value)
