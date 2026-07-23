"""NFR-OUT-PERF-1 (observed / non-gating) — SHAP + fit cost recorded, correctness gating (Q2-A).

SHAP correctness (a finite value per flagged feature) is gating; the fit + SHAP RUNTIME is only
recorded/observed here — no hard SLO (the project's uniform soft-perf posture). The generous
ceiling below is a smoke bound to catch a pathological regression, not a performance contract.
"""
from __future__ import annotations

import math
import time

from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.model import OutlierModel
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.outlier_model.tests import fixtures as F


def test_fit_and_score_runtime_observed(capsys):
    profiles = CorpusSource.profiles(F.corpus_records())

    t0 = time.perf_counter()
    fitted = OutlierModel.fit(profiles, F.make_manifest(), ShapExplainer())
    result = fitted.score(F.outlier_profile())
    elapsed = time.perf_counter() - t0

    # correctness is the gating part: every flag carries a finite SHAP value
    assert result.flagged_features
    assert all(math.isfinite(f.shap_value) for f in result.flagged_features)

    # runtime is OBSERVED (recorded), non-gating — a generous smoke ceiling only
    with capsys.disabled():
        print(f"\n[PERF-1 observed] outlier-model fit+score+SHAP: {elapsed:.3f}s")
    assert elapsed < 60.0
