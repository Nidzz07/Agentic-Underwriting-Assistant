"""Output schemas — ``OutlierResult`` / ``FlaggedFeature`` / ``OutlierProvenance`` (U18).

P-OUT-4 (EXPLAIN-1) + P-OUT-7 (PROV-1), by schema construction:

  ``FlaggedFeature.shap_value`` is REQUIRED (no default) — a flag **cannot be constructed
  without** its SHAP value, so "zero unexplained flags" (NFR-EXPLAIN-1) holds by construction,
  not by a downstream check. ``OutlierResult.provenance`` is a REQUIRED ``OutlierProvenance``
  (no default) — a result cannot exist without its reproducibility triple. All models are
  ``frozen=True`` + ``extra="forbid"``. ``OutlierResult`` carries a score + flags + provenance
  ONLY — **no verdict / ``Recommendation`` field** (advisory-only, BR-OUT-9).
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class FlagDirection(str, Enum):
    """Which tail the flagged feature sits in, relative to the corpus mean."""

    HIGH = "high"   # above the corpus mean
    LOW = "low"     # below the corpus mean


class FlaggedFeature(_Frozen):
    """A per-feature anomaly — cannot exist without its SHAP explanation (EXPLAIN-1)."""

    feature: str          # one of OUTLIER_FEATURE_FIELDS (never a demographic name)
    z_score: float        # per-feature z vs the corpus distribution; |z| >= threshold ⇒ flagged
    shap_value: float     # REQUIRED — SHAP attribution of the score to this feature (US-OUT-2)
    direction: FlagDirection


class OutlierProvenance(_Frozen):
    """The reproducibility triple — the score is un-replayable without all three (PROV-1)."""

    corpus_version: str            # WHICH corpus fit the forest (the score is corpus-relative)
    seed: int                      # single-sourced from CorpusManifest.seed
    outlier_model_version: str     # bundles the sklearn version + the feature-schema version
    # NOTE: no ``rulebook_version`` — unsupervised scoring never reads the corpus label.


class OutlierResult(_Frozen):
    """The advisory output contract — score + explained flags + provenance ONLY (no verdict)."""

    outlier_score: float                          # IsolationForest holistic score; higher = more anomalous
    is_outlier: bool                              # IsolationForest decision-boundary crossing
    flagged_features: list[FlaggedFeature]        # per-feature anomalies; MAY be empty (a normal applicant)
    provenance: OutlierProvenance
