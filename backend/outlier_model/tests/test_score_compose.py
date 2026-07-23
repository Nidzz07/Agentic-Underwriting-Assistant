"""NFR-OUT-COMPOSE-1 — score / flag / explain composition (BR-OUT-5).

``outlier_score`` comes from IsolationForest; ``flagged_features`` are exactly the non-imputed
features with ``|z| >= Z_SCORE_FLAG_THRESHOLD``, each carrying a ``shap_value`` + ``direction``; a
normal applicant → ``flagged_features == []`` with a valid score + populated provenance. Also the
zero-candidate short-circuit ``ShapExplainer.explain(..., []) -> []`` (no SHAP run).
"""
from __future__ import annotations

import numpy as np

from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.feature_vector import FeatureVectorBuilder
from backend.outlier_model.model import (
    OutlierModel,
    Z_SCORE_FLAG_THRESHOLD,
    _candidates,
    _z_scores,
)
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.outlier_model.tests import fixtures as F


def _fitted():
    profiles = CorpusSource.profiles(F.corpus_records())
    return OutlierModel.fit(profiles, F.make_manifest(), ShapExplainer())


def test_outlier_score_comes_from_isolation_forest():
    fitted = _fitted()
    profile = F.outlier_profile()
    fi = FeatureVectorBuilder.project(profile, fitted.imputer)
    expected = float(-fitted.forest.score_samples(np.array([fi.values], dtype=float))[0])
    assert fitted.score(profile).outlier_score == expected


def test_flagged_features_are_exactly_the_nonimputed_over_threshold():
    fitted = _fitted()
    profile = F.outlier_profile()
    fi = FeatureVectorBuilder.project(profile, fitted.imputer)
    order = FeatureVectorBuilder.field_order()
    zs = _z_scores(fi.values, fi.imputed, fitted.means, fitted.stds)
    expected = {c.feature for c in _candidates(zs, order, Z_SCORE_FLAG_THRESHOLD)}

    result = fitted.score(profile)
    assert {f.feature for f in result.flagged_features} == expected
    for flag in result.flagged_features:
        assert flag.direction is not None
        assert abs(flag.z_score) >= Z_SCORE_FLAG_THRESHOLD


def test_normal_applicant_has_no_flags_but_a_valid_score():
    fitted = _fitted()
    result = fitted.score(F.typical_profile())
    assert result.flagged_features == []
    assert result.is_outlier is False
    assert isinstance(result.outlier_score, float)
    assert result.provenance.corpus_version == "corpus-test-v1"


def test_empty_candidate_shortcircuit_returns_no_flags():
    fitted = _fitted()
    fi = FeatureVectorBuilder.project(F.typical_profile(), fitted.imputer)
    assert ShapExplainer().explain(fitted.forest, fi, []) == []
