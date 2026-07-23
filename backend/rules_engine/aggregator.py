"""Aggregator — per-rule results → the recommendation (Step 8).

FD ``business-rules.md §3`` + NFR Design §6. A **pure set-reduction** over the
``outcome_tier`` contributions under **fixed precedence** — order-independent
(NFR-RULES-AGG-1, feeds DET-2):

  1. **any** ``decline_fail`` ⇒ ``DECLINE-RECOMMEND`` (decline dominates, even if
     also incomplete);
  2. else **any** ``refer_trigger`` — including the ``incomplete`` insufficient-info
     trigger and every ``not_evaluated`` → ``refer_trigger`` ⇒ ``REFER``;
  3. else all pass ⇒ ``APPROVE``.

``incomplete`` / ``not_evaluated`` contribute **only** ``refer_trigger``, never
``decline_fail`` → **thin-file → REFER, never DECLINE**. ``decline_reasons`` /
``refer_reasons`` collect the driving ``rule_id``s in the **one canonical order**
(sorted — by ``rule_id`` then message). The ``-RECOMMEND`` suffix is mandatory.
"""
from __future__ import annotations

from typing import NamedTuple

from backend.rules_engine.report_schema import OutcomeTier, Recommendation, RuleResult

#: The distinct insufficient-information trigger raised by ``profile.incomplete``
#: (intake's flag) — a ``refer_trigger``, NOT a rule pass/fail.
INCOMPLETE_REASON = (
    "profile_incomplete: application flagged incomplete at intake "
    "(insufficient information)"
)


class Aggregation(NamedTuple):
    """The aggregation output — recommendation + the canonical-order reason lists."""
    recommendation: Recommendation
    decline_reasons: list[str]
    refer_reasons: list[str]


def _reason(result: RuleResult) -> str:
    return f"{result.rule_id}: {result.message}"


def aggregate(results: list[RuleResult], incomplete: bool = False) -> Aggregation:
    """Reduce the ``outcome_tier`` set to a recommendation under fixed precedence."""
    decline_reasons = sorted(
        _reason(r) for r in results if r.outcome_tier is OutcomeTier.DECLINE_FAIL
    )
    refer_reasons = sorted(
        [_reason(r) for r in results if r.outcome_tier is OutcomeTier.REFER_TRIGGER]
        + ([INCOMPLETE_REASON] if incomplete else [])
    )

    if decline_reasons:                       # tier 1 — decline dominates
        recommendation = Recommendation.DECLINE_RECOMMEND
    elif refer_reasons:                       # tier 2 — any refer (incl. incomplete)
        recommendation = Recommendation.REFER
    else:                                     # tier 3 — all pass
        recommendation = Recommendation.APPROVE

    return Aggregation(recommendation, decline_reasons, refer_reasons)
