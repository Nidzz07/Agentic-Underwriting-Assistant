"""C-OUT-4 ``ShapExplainer`` — the SOLE constructor of ``FlaggedFeature`` (U18 / P-OUT-4).

BY CONSTRUCTION — sole-constructor (documentation; the enforcement is the single call site +
the StructuralGuard ``single_FlaggedFeature_constructor`` scan):

  ``ShapExplainer.explain`` is the ONLY code path in the unit that constructs a
  ``FlaggedFeature``. ``OutlierModel`` computes the flag *candidates* (feature + z + direction)
  but hands them here; the explainer attaches the SHAP value and builds each flag. A flag is
  therefore **born from SHAP** — no call site can produce one without an explanation
  (NFR-EXPLAIN-1). The zero-candidate case short-circuits: ``explain(..., []) -> []`` with no
  SHAP run (CG-ND-OUT-Fold-2). TreeExplainer is deterministic for the tree model — no seed
  (CG-ND-OUT-Fold-3).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import shap

from backend.outlier_model.feature_fields import FeatureInputs
from backend.outlier_model.schemas import FlagDirection, FlaggedFeature


@dataclass(frozen=True)
class FlagCandidate:
    """A pre-explanation flag — everything a ``FlaggedFeature`` needs EXCEPT the SHAP value."""

    feature: str
    index: int
    z_score: float
    direction: FlagDirection


class ShapExplainer:
    """Attributes the IsolationForest score to features and builds every ``FlaggedFeature``."""

    def explain(
        self,
        fitted_forest,
        feature_inputs: FeatureInputs,
        candidates: Sequence[FlagCandidate],
    ) -> list[FlaggedFeature]:
        """The sole ``FlaggedFeature`` constructor. ``candidates == []`` → ``[]`` (no SHAP run)."""
        if not candidates:
            return []
        explainer = shap.TreeExplainer(fitted_forest)
        row = np.array([feature_inputs.values], dtype=float)
        attributions = np.asarray(explainer.shap_values(row, check_additivity=False))[0]
        return [
            FlaggedFeature(
                feature=candidate.feature,
                z_score=candidate.z_score,
                shap_value=float(attributions[candidate.index]),
                direction=candidate.direction,
            )
            for candidate in candidates
        ]
