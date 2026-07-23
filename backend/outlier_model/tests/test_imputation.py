"""NFR-OUT-IMPUTE-1 (teeth) — a missing optional imputes deterministically and never flags.

A profile with a deliberately-missing optional (``bmi_derived`` / debt / ``dti_ratio`` = None)
scores deterministically; the imputed feature's flagging z-score is exactly 0 (by the mask) and
it never appears in ``flagged_features``; same ``(corpus, seed)`` → same imputed value (BR-OUT-3).
"""
from __future__ import annotations

from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.feature_vector import FeatureVectorBuilder
from backend.outlier_model.model import OutlierModel, _z_scores
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.outlier_model.tests import fixtures as F

_IMPUTED_FEATURES = {"bmi_derived", "existing_debt_obligations_annual", "dti_ratio"}


def _fitted():
    profiles = CorpusSource.profiles(F.corpus_records())
    return OutlierModel.fit(profiles, F.make_manifest(), ShapExplainer())


def test_missing_optionals_are_masked_as_imputed():
    fitted = _fitted()
    order = FeatureVectorBuilder.field_order()
    fi = FeatureVectorBuilder.project(F.missing_optional_profile(), fitted.imputer)
    imputed_names = {order[i] for i, flag in enumerate(fi.imputed) if flag}
    assert imputed_names == _IMPUTED_FEATURES
    # The imputed slots are filled with the stored corpus median (not None, not fabricated).
    for i, flag in enumerate(fi.imputed):
        if flag:
            assert fi.values[i] == fitted.imputer.medians[i]


def test_imputed_feature_never_flags():
    fitted = _fitted()
    result = fitted.score(F.missing_optional_profile())
    flagged = {f.feature for f in result.flagged_features}
    assert flagged.isdisjoint(_IMPUTED_FEATURES)


def test_imputed_feature_z_score_is_exactly_zero():
    # The mask drives z=0 regardless of the imputed value's magnitude.
    values = (999999.0, 1.0)
    imputed = (True, False)
    means = (0.0, 0.0)
    stds = (1.0, 1.0)
    zs = _z_scores(values, imputed, means, stds)
    assert zs[0] == 0.0
    assert zs[1] == 1.0


def test_fit_imputer_takes_median_over_present_values_only():
    # A corpus that itself contains a missing-optional profile: the median is computed over the
    # PRESENT values, skipping the None slots (the fit-time missing-value path).
    from statistics import median

    order = FeatureVectorBuilder.field_order()
    corpus = F.normal_corpus_profiles() + [F.missing_optional_profile()]
    imputer = FeatureVectorBuilder.fit_imputer(corpus)

    bmi_idx = order.index("bmi_derived")
    present_bmis = [float(p.bmi_derived) for p in corpus if p.bmi_derived is not None]
    assert imputer.medians[bmi_idx] == float(median(present_bmis))


def test_imputation_is_deterministic():
    fitted = _fitted()
    fi_1 = FeatureVectorBuilder.project(F.missing_optional_profile(), fitted.imputer)
    fi_2 = FeatureVectorBuilder.project(F.missing_optional_profile(), fitted.imputer)
    assert fi_1 == fi_2
    # And identical across an independent fit of the same seeded corpus.
    other = _fitted()
    fi_3 = FeatureVectorBuilder.project(F.missing_optional_profile(), other.imputer)
    assert fi_1 == fi_3
