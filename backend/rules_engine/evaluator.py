"""RuleEvaluator — the pure per-rule evaluation (Step 7).

FD ``business-logic-model.md §2`` + ``business-rules.md §1``; NFR Design §1/§4.
Iterates the rulebook's rules in the **fixed canonical order (sorted by
``rule_id``)** and, for each, resolves operands **only** from that rule's
``input_fields`` against the demographic-excluded namespace, applies
``operator`` vs ``threshold`` in ``Decimal``, and emits a **tri-state**
``RuleResult`` recording the **exact** ``actual_value`` + comparison (FR-RULES-3).

Determinism (NFR-RULES-DET-1): **no I/O, no wall-clock, no unseeded randomness,
no dict-order reliance** — a pure function of ``(rulebook, namespace)``.
Boundary exactness (NFR-RULES-BND-1): every comparison is explicit and inclusive
exactly as the rule's ``operator``/``threshold`` declares. A missing operand →
``not_evaluated`` + ``refer_trigger`` with ``actual_value == null`` (never a
silent pass/fail, never a divide/compare error).
"""
from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any

from backend.rules_engine.report_schema import (
    Operator,
    OutcomeTier,
    RuleResult,
    RuleStatus,
    ThresholdRepr,
)
from backend.rules_engine.rulebook_schema import DecimalRange, Rule, Rulebook

_NUMERIC_OPS = (Operator.LTE, Operator.LT, Operator.GTE, Operator.GT)


def _canonical_scalar(value: Any) -> Any:
    """The comparable form of an operand/literal — enums by their ``.value``."""
    return value.value if isinstance(value, Enum) else value


def _to_decimal(value: Any) -> Decimal:
    """Coerce a numeric operand to ``Decimal`` (int → Decimal; never via float)."""
    return value if isinstance(value, Decimal) else Decimal(value)


def _record_actual(value: Any) -> Any:
    """The value stored on the RuleResult: ``Decimal`` for numerics, ``str`` for
    categoricals (enum → ``.value``)."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (int, Decimal)) and not isinstance(value, bool):
        return _to_decimal(value)
    return value  # a plain string (e.g. occupation)


def _record_threshold(threshold: Any) -> ThresholdRepr:
    """The threshold as stored on the RuleResult. A bare ``str`` literal (a
    categorical ``eq``) is wrapped as a singleton list (``eq x ≡ in {x}``) so it
    fits the report ThresholdRepr without a bare ``str``."""
    return [threshold] if isinstance(threshold, str) else threshold


def _compare(operator: Operator, actual: Any, threshold: Any) -> bool:
    """Apply ``operator`` to ``actual`` vs ``threshold`` (explicit + boundary-exact)."""
    if operator in _NUMERIC_OPS:
        left, right = _to_decimal(actual), _to_decimal(threshold)
        if operator is Operator.LTE:
            return left <= right
        if operator is Operator.LT:
            return left < right
        if operator is Operator.GTE:
            return left >= right
        return left > right  # GT
    if operator is Operator.BETWEEN:
        value = _to_decimal(actual)
        low_ok = value >= threshold.low if threshold.low_inclusive else value > threshold.low
        high_ok = value <= threshold.high if threshold.high_inclusive else value < threshold.high
        return low_ok and high_ok
    if operator is Operator.IN:
        return _canonical_scalar(actual) in [_canonical_scalar(v) for v in threshold]
    # EQ — scalar literal (numeric Decimal or categorical str)
    if isinstance(threshold, Decimal):
        return _to_decimal(actual) == threshold
    return _canonical_scalar(actual) == _canonical_scalar(threshold)


def _render(template: str, actual_value: Any, threshold: Any) -> str:
    """Render ``rationale_message`` with ``{actual_value}`` / ``{threshold}``,
    tolerating templates that use neither (advisory-only vocabulary)."""
    shown = "null" if actual_value is None else actual_value
    try:
        return template.format(actual_value=shown, threshold=threshold)
    except (KeyError, IndexError, ValueError):
        return template


def _evaluate_rule(rule: Rule, namespace: dict[str, Any]) -> RuleResult:
    operands = {field: namespace.get(field) for field in rule.input_fields}
    threshold_repr = _record_threshold(rule.threshold)
    if any(value is None for value in operands.values()):  # missing/uncomputable operand
        return RuleResult(
            rule_id=rule.rule_id, category=rule.category, status=RuleStatus.NOT_EVALUATED,
            actual_value=None, operator=rule.operator, threshold=threshold_repr,
            outcome_tier=OutcomeTier.REFER_TRIGGER,           # never decline on missing
            message=_render(rule.rationale_message, None, rule.threshold),
        )
    primary = operands[rule.input_fields[0]]                  # the compared operand
    passed = _compare(rule.operator, primary, rule.threshold)
    recorded = _record_actual(primary)
    return RuleResult(
        rule_id=rule.rule_id, category=rule.category,
        status=RuleStatus.PASS if passed else RuleStatus.FAIL,
        actual_value=recorded, operator=rule.operator, threshold=threshold_repr,
        outcome_tier=OutcomeTier.PASS_ONLY if passed else rule.outcome,
        message=_render(rule.rationale_message, recorded, rule.threshold),
    )


def evaluate_rules(rulebook: Rulebook, namespace: dict[str, Any]) -> list[RuleResult]:
    """Evaluate every rule (fixed canonical order by ``rule_id``) → tri-state results."""
    return [_evaluate_rule(rule, namespace)
            for rule in sorted(rulebook.rules, key=lambda r: r.rule_id)]
