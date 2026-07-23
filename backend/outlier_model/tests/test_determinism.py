"""NFR-OUT-DET-1 (teeth) — seeded, RNG-leak-proof determinism (BR-OUT-4, load-bearing).

(a) Same corpus + seed + inputs → byte-identical ``OutlierResult`` across N>=2 independent fits.
(b) Global-RNG-perturbation (CG-NFR-OUT-Fold-1): between two full fit+score cycles, perturb
    numpy's GLOBAL RNG state; the result stays byte-identical — proving the scoring is seed-local
    (``IsolationForest`` constructs its own local ``RandomState`` from the injected instance and
    never consumes the global RNG). Uses fixed, documented perturbation constants.
"""
from __future__ import annotations

import numpy as np

from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.model import OutlierModel
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.outlier_model.tests import fixtures as F

# Arbitrary but FIXED perturbation constants (documented for determinism).
_PERTURB_SEED_A = 1234567
_PERTURB_DRAWS = 97
_PERTURB_SEED_B = 7654321


def _fit_and_score():
    profiles = CorpusSource.profiles(F.corpus_records())
    fitted = OutlierModel.fit(profiles, F.make_manifest(), ShapExplainer())
    return fitted.score(F.outlier_profile()).model_dump_json()


def test_same_corpus_seed_inputs_byte_identical_across_two_fits():
    assert _fit_and_score() == _fit_and_score()


def test_global_rng_perturbation_does_not_change_the_result():
    first = _fit_and_score()

    # Deliberately churn numpy's GLOBAL RNG between the two cycles.
    np.random.seed(_PERTURB_SEED_A)
    np.random.random(_PERTURB_DRAWS)
    np.random.seed(_PERTURB_SEED_B)

    second = _fit_and_score()
    assert first == second, "scoring leaked to the global numpy RNG (not seed-local)"
