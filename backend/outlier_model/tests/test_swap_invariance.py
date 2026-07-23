"""NFR-OUT-BIAS-1 (teeth) — demographic swap changes nothing (BR-OUT-1, load-bearing).

Two profiles with identical financials but swapped ``full_name`` / ``gender`` / ``city`` produce
a byte-identical ``FeatureInputs`` AND a byte-identical ``OutlierResult`` (score, flags,
provenance). Any changed output byte fails.
"""
from __future__ import annotations

from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.feature_vector import FeatureVectorBuilder
from backend.outlier_model.model import OutlierModel
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.outlier_model.tests import fixtures as F


def _fitted():
    profiles = CorpusSource.profiles(F.corpus_records())
    return OutlierModel.fit(profiles, F.make_manifest(), ShapExplainer())


def test_swap_yields_byte_identical_feature_inputs():
    fitted = _fitted()
    a, b = F.swap_pair()
    fi_a = FeatureVectorBuilder.project(a, fitted.imputer)
    fi_b = FeatureVectorBuilder.project(b, fitted.imputer)
    assert fi_a == fi_b


def test_swap_yields_byte_identical_outlier_result():
    fitted = _fitted()
    a, b = F.swap_pair()
    assert fitted.score(a).model_dump_json() == fitted.score(b).model_dump_json()
