"""BorderlineRouter (C-MEXT-1) — the deterministic, provider-agnostic borderline
trigger (BR-MEXT-1/2/3 · NFR-MEXT-ROUTE-1/SIGNAL-1/AGNOSTIC-1/SCOPE-1).

**Header-comment deliverable (documentation only — NEVER enforcement):**
- This module holds **no LLM client, no provider, no adapter, no network** — a
  provider is *structurally un-injectable* because ``route_borderline`` has **no
  ``client``/``provider`` parameter to pass one through** (NFR-MEXT-ROUTE-1).
- **Both triggers are deterministic** (FR-MEMO-6): rule-proximity within a single
  named margin OR outlier score above a single named cutoff. No wall-clock, no RNG,
  no per-run computed constant. Identical ``(rule_report, outlier_signal)`` → identical
  ``ThinkingMode`` (purity).
- The outlier value is **handed in, never imported** (Q2-A): it is read through the
  U19-local ``OutlierSignal`` structural Protocol — U18's ``outlier-model`` is reached
  only *by shape*, with no import and no edge (NFR-MEXT-SIGNAL-1).
- ``OutlierSignal``'s narrowness (**exactly** ``is_outlier`` + ``outlier_score``) is
  itself the scope guard: ``flagged_features``/``shap_value``/``provenance`` are **not on
  the type**, so the prose-bearing fields are structurally unreachable from the router —
  holding ``OUTLIER-IN-PROSE`` out of scope (BR-MEXT-13 / NFR-MEXT-SCOPE-1).

Realization notes (Code-Gen, disclosed):
- ``RULE_PROXIMITY_MARGIN`` is a **relative** margin (a fraction of the threshold),
  so a single named constant is unit-agnostic across heterogeneous rule thresholds
  (age-years vs DTI-fraction vs BMI vs money amounts). Provisional post-calibration
  value; every threshold test parameterizes OFF the named constant (the
  ``Z_SCORE_FLAG_THRESHOLD`` / CG-OUT-Fold-1 precedent).
- Proximity is computed with a **deterministic** ``float()`` of a ``Decimal`` ratio.
  This is *routing*, NOT rule evaluation — the recommendation is already decided by the
  deterministic engine — so CON-DET-1's no-float-in-evaluation rule is not in scope here;
  ``float(Decimal)`` is deterministic (same input → same routing), which the ROUTE-1
  purity teeth prove.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Final, Protocol, runtime_checkable

from backend.memo_agent_core.schemas import ThinkingMode
from backend.rules_engine.report_schema import Recommendation

if TYPE_CHECKING:  # annotation-only; no runtime import (Fold-3)
    from backend.rules_engine.report_schema import RuleResultReport

#: The single named rule-proximity margin (RELATIVE — a fraction of the threshold).
#: Provisional post-calibration value; tests parameterize OFF this constant.
RULE_PROXIMITY_MARGIN: Final[float] = 0.05

#: The single named outlier-score cutoff. Compared against the handed
#: ``OutlierSignal.outlier_score`` (a float). Provisional post-calibration value.
OUTLIER_SCORE_CUTOFF: Final[float] = 0.5


@runtime_checkable
class OutlierSignal(Protocol):
    """The MINIMAL outlier read-surface the router may see (Q2-A / P-MEXT-5).

    Satisfied structurally BY SHAPE by ``outlier_model.schemas.OutlierResult`` —
    with **no import, no edge**. The two members below are the ONLY ones the router
    reads; ``flagged_features``/``shap_value``/``provenance`` are deliberately NOT
    declared, so they do not exist on this type (NFR-MEXT-SCOPE-1).
    """

    is_outlier: bool
    outlier_score: float


def route_borderline(
    rule_report: "RuleResultReport",
    outlier_signal: OutlierSignal | None = None,
) -> ThinkingMode:
    """Decide ``STANDARD`` vs ``EXTENDED`` from two deterministic triggers only.

    ``EXTENDED`` when ANY of: the recommendation is ``REFER``; the handed
    ``outlier_signal`` scores **at or above** ``OUTLIER_SCORE_CUTOFF``; or any rule's
    actual value is **within** ``RULE_PROXIMITY_MARGIN`` of its threshold. Otherwise
    ``STANDARD``. ``outlier_signal=None`` means the outlier half is unavailable →
    routing runs on rule-proximity (and REFER) alone (FR-MEMO-7). Pure function; holds
    no state; no LLM/provider/network.
    """
    # REFER is always borderline (BR-MEXT-1: "including any REFER").
    if rule_report.recommendation is Recommendation.REFER:
        return ThinkingMode.EXTENDED

    # Outlier cutoff — inclusive boundary (>=), explicit.
    if outlier_signal is not None and outlier_signal.outlier_score >= OUTLIER_SCORE_CUTOFF:
        return ThinkingMode.EXTENDED

    # Rule-proximity — inclusive boundary (<=), explicit.
    if _within_rule_proximity(rule_report):
        return ThinkingMode.EXTENDED

    return ThinkingMode.STANDARD


def _numeric_bounds(threshold: object) -> list:
    """The numeric threshold bound(s) proximity is measured against.

    A scalar ``Decimal`` → itself; a ``DecimalRange`` → both bounds; a set/list
    (categorical ``in`` threshold) → none (not a numeric proximity). Duck-typed so
    the router imports neither ``Decimal`` nor ``DecimalRange`` (allow-list discipline).
    """
    if isinstance(threshold, list):
        return []
    if hasattr(threshold, "low") and hasattr(threshold, "high"):
        return [threshold.low, threshold.high]
    return [threshold]


def _within_rule_proximity(rule_report: "RuleResultReport") -> bool:
    """True iff any rule's numeric actual value is within the RELATIVE margin of a
    numeric threshold bound. Non-numeric (``str``) and ``not_evaluated`` (``None``)
    actual values carry no proximity and are skipped."""
    for result in rule_report.rule_results:
        actual = result.actual_value
        if actual is None or isinstance(actual, str):
            continue
        for bound in _numeric_bounds(result.threshold):
            if bound == 0:
                proximity = float(abs(actual - bound))
            else:
                proximity = float(abs(actual - bound) / abs(bound))
            if proximity <= RULE_PROXIMITY_MARGIN:  # inclusive boundary, explicit
                return True
    return False
