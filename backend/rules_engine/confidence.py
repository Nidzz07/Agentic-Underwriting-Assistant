"""ConfidenceBander — deterministic confidence banding (Step 9).

FD ``business-rules.md §4`` + NFR Design §7. ``confidence ∈ {High, Medium, Low}``
is a **pure function** of (a) the normalized **proximity** of each numeric
``actual_value`` to its nearest threshold and (b) profile completeness, banded on
the **fixed versioned ``ConfidenceBands`` constants** (``high_margin`` /
``low_margin``). No randomness, no wall-clock — identical inputs + rulebook version
→ **identical band ×N** (NFR-RULES-CONF-1). Produced HERE, **never by the LLM**.

Banding (order-independent — all inputs are counts):
  * **Low**  — a ``not_evaluated`` result (material incompleteness), OR ≥2
    near-boundary numeric hits, OR any hit at/under ``low_margin`` proximity.
  * **Medium** — exactly one near-boundary hit, OR a single incompleteness
    (``profile.incomplete``), with no Low trigger.
  * **High** — every numeric rule clears its boundary by more than ``high_margin``
    and the profile is complete.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
from typing import Optional

from backend.common.decimal_context import CANON_DECIMAL_CONTEXT
from backend.rules_engine.report_schema import (
    Confidence,
    DecimalRange,
    RuleResult,
    RuleStatus,
)
from backend.rules_engine.rulebook_schema import ConfidenceBands

_ONE = Decimal(1)


def _proximity(result: RuleResult) -> Optional[Decimal]:
    """Normalized distance of a numeric ``actual_value`` to its nearest threshold.

    ``None`` for categorical / not-evaluated results (no numeric proximity).
    Normalization = ``distance / max(|nearest bound|, 1)`` under the single shared
    Decimal context (deterministic).
    """
    if result.status is RuleStatus.NOT_EVALUATED or not isinstance(result.actual_value, Decimal):
        return None
    actual = result.actual_value
    threshold = result.threshold
    if isinstance(threshold, Decimal):
        nearest, distance = threshold, abs(actual - threshold)
    elif isinstance(threshold, DecimalRange):
        low_d, high_d = abs(actual - threshold.low), abs(actual - threshold.high)
        nearest, distance = (threshold.low, low_d) if low_d <= high_d else (threshold.high, high_d)
    else:  # categorical (list) — no numeric proximity
        return None
    with localcontext(CANON_DECIMAL_CONTEXT):
        return distance / max(abs(nearest), _ONE)


def band_confidence(
    results: list[RuleResult], incomplete: bool, bands: ConfidenceBands
) -> Confidence:
    """Band confidence deterministically from proximity + completeness."""
    not_evaluated = sum(1 for r in results if r.status is RuleStatus.NOT_EVALUATED)
    near = low_prox = 0
    for result in results:
        proximity = _proximity(result)
        if proximity is None:
            continue
        if proximity <= bands.high_margin:
            near += 1
        if proximity <= bands.low_margin:
            low_prox += 1

    if not_evaluated >= 1 or near >= 2 or low_prox >= 1:
        return Confidence.LOW
    if near >= 1 or incomplete:
        return Confidence.MEDIUM
    return Confidence.HIGH
