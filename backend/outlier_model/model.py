"""C-OUT-3 ``OutlierModel`` — seeded, seed-local IsolationForest scorer (U18 / P-OUT-2/3/5/7).

BY CONSTRUCTION — seed-locality + sole-explainer delegation (documentation; the enforcement is
the injected ``RandomState`` instance + the StructuralGuard ``no_global_rng`` scan + the
single-constructor discipline):

  ``fit`` constructs an explicit ``RandomState(manifest.seed)`` and injects that INSTANCE into
  ``IsolationForest(random_state=...)``. The model's ONLY randomness source is that visible
  local instance — the global numpy RNG (``np.random.*``) is NEVER read or written anywhere in
  a scoring path (P-OUT-2 / DET-1). The seed is single-sourced from ``CorpusManifest.seed``.

  ``score`` computes candidate flags from the NON-imputed features whose ``|z| >=`` the strictly
  positive ``Z_SCORE_FLAG_THRESHOLD`` (an imputed feature's flagging z is 0 by the mask, so it
  is never a candidate — P-OUT-3), then DELEGATES construction to the ``ShapExplainer`` — it
  never builds a ``FlaggedFeature`` itself (P-OUT-4). Every ``OutlierResult`` carries its
  required ``OutlierProvenance`` (P-OUT-7). Deterministic given
  ``(profile, corpus_version, seed, outlier_model_version)``.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import sklearn
from numpy.random import RandomState   # the sanctioned local-instance constructor (NOT np.random.*)
from sklearn.ensemble import IsolationForest

from backend.corpus_generator.records import CorpusManifest
from backend.intake.schema import ApplicantProfile
from backend.outlier_model.feature_vector import CorpusImputer, FeatureVectorBuilder
from backend.outlier_model.schemas import (
    FlagDirection,
    OutlierProvenance,
    OutlierResult,
)
from backend.outlier_model.shap_explainer import FlagCandidate, ShapExplainer

# BR-OUT-6 / THRESHOLD-1: exactly ONE fixed named constant — the 3-sigma default. A z-score
# flag threshold <= 0 is degenerate (it would flag every feature, including exact-mean and
# imputed ones), so it is INVALID, not a tuning option — the strict-positivity guard below is
# what makes BR-OUT-3's "imputed never flags" calibration-robust (CG-NFR-OUT-Fold-2).
Z_SCORE_FLAG_THRESHOLD: float = 3.0
assert Z_SCORE_FLAG_THRESHOLD > 0, "Z_SCORE_FLAG_THRESHOLD must be strictly positive"

# Version-anchored replay (CG-OUT-Fold-2): bundles the sklearn version + the feature-vector
# schema version, so a replay knows the exact library it must match. Realized at Code-Gen (the
# exact string was deferred by FD §5); PROV-1 asserts presence + shape, not the literal value.
_FEATURE_SCHEMA_VERSION = "fv1"
OUTLIER_MODEL_VERSION = f"outlier-model/1.0.0+sklearn-{sklearn.__version__}+{_FEATURE_SCHEMA_VERSION}"

# IsolationForest hyper-parameters — explicitly deferred to Code-Gen by FD §5 / NFR-Req §4.
# Deterministic given the injected seed; ``contamination="auto"`` fixes the decision boundary.
_N_ESTIMATORS = 100
_CONTAMINATION = "auto"


# Relative near-zero-variance tolerance. A feature whose std is negligible relative to its
# scale carries no discriminative z-signal; its z is set to 0. This mirrors sklearn's
# ``StandardScaler`` near-constant handling and guards against float noise on an analytically
# constant column (e.g. a corpus where dti is a fixed fraction) exploding the z-score.
_STD_EPSILON = 1e-9


def _has_variance(std: float, mean: float) -> bool:
    return std > _STD_EPSILON * max(1.0, abs(mean))


def _z_scores(
    values: tuple[float, ...],
    imputed: tuple[bool, ...],
    means: tuple[float, ...],
    stds: tuple[float, ...],
) -> tuple[float, ...]:
    """Per-feature flagging z-score. An imputed feature (or a zero-/near-zero-variance feature)
    is 0 BY DESIGN — a missing value is not anomaly evidence, and a constant feature has no z
    (P-OUT-3).
    """
    out: list[float] = []
    for i, value in enumerate(values):
        if imputed[i] or not _has_variance(stds[i], means[i]):
            out.append(0.0)
        else:
            out.append((value - means[i]) / stds[i])
    return tuple(out)


def _is_flag(z: float, threshold: float) -> bool:
    """Inclusive-boundary flag predicate — parameterized off the named constant (THRESHOLD-1)."""
    return abs(z) >= threshold


def _candidates(
    z_scores: tuple[float, ...], field_order: tuple[str, ...], threshold: float
) -> list[FlagCandidate]:
    """The features whose ``|z| >= threshold``, as pre-explanation candidates."""
    candidates: list[FlagCandidate] = []
    for i, name in enumerate(field_order):
        z = z_scores[i]
        if _is_flag(z, threshold):
            direction = FlagDirection.HIGH if z > 0 else FlagDirection.LOW
            candidates.append(FlagCandidate(feature=name, index=i, z_score=z, direction=direction))
    return candidates


class OutlierModel:
    """Fits the seeded IsolationForest + corpus z-stats; scores an applicant → ``OutlierResult``."""

    @staticmethod
    def fit(
        corpus_profiles: list[ApplicantProfile],
        manifest: CorpusManifest,
        explainer: ShapExplainer,
    ) -> "FittedOutlierModel":
        rng = RandomState(manifest.seed)   # explicit local instance — seed single-sourced (P-OUT-2)
        imputer = FeatureVectorBuilder.fit_imputer(corpus_profiles)
        matrix = FeatureVectorBuilder.build_matrix(corpus_profiles, imputer)
        feature_matrix = np.array([fi.values for fi in matrix], dtype=float)
        forest = IsolationForest(
            n_estimators=_N_ESTIMATORS,
            contamination=_CONTAMINATION,
            random_state=rng,   # injected INSTANCE; global np.random.* is NEVER touched
        ).fit(feature_matrix)
        means = tuple(float(m) for m in feature_matrix.mean(axis=0))
        stds = tuple(float(s) for s in feature_matrix.std(axis=0))
        provenance = OutlierProvenance(
            corpus_version=manifest.corpus_version,
            seed=manifest.seed,
            outlier_model_version=OUTLIER_MODEL_VERSION,
        )
        return FittedOutlierModel(
            forest=forest,
            imputer=imputer,
            means=means,
            stds=stds,
            explainer=explainer,
            provenance=provenance,
        )


@dataclass(frozen=True)
class FittedOutlierModel:
    """The fitted, deterministic scorer — reused across many applicants for one corpus."""

    forest: IsolationForest
    imputer: CorpusImputer
    means: tuple[float, ...]
    stds: tuple[float, ...]
    explainer: ShapExplainer
    provenance: OutlierProvenance

    def score(self, profile: ApplicantProfile) -> OutlierResult:
        feature_inputs = FeatureVectorBuilder.project(profile, self.imputer)
        row = np.array([feature_inputs.values], dtype=float)
        outlier_score = float(-self.forest.score_samples(row)[0])   # higher = more anomalous
        is_outlier = bool(self.forest.predict(row)[0] == -1)
        z_scores = _z_scores(
            feature_inputs.values, feature_inputs.imputed, self.means, self.stds
        )
        candidates = _candidates(
            z_scores, FeatureVectorBuilder.field_order(), Z_SCORE_FLAG_THRESHOLD
        )
        flagged = self.explainer.explain(self.forest, feature_inputs, candidates)
        return OutlierResult(
            outlier_score=outlier_score,
            is_outlier=is_outlier,
            flagged_features=flagged,
            provenance=self.provenance,
        )
