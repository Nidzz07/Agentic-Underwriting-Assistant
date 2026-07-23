"""RulebookCanonAdapter — canonicalize a Rulebook via the shared CANON-SER.

NFR-RULES-CANON-1 / NFR Design §3. Normalizes the `Rulebook` into
``backend.common.canon_ser``'s **existing** value space, then calls the
**UNCHANGED** shared utility (the `CanonSerAdapter` precedent from intake). One
canonicalization convention; no fork; no `canon_ser.py` / §2.1 change.

Normalization into canon_ser's value space:
  * ``set``-threshold  -> a **declared-sorted list** (sorted by canonical bytes,
    a deterministic total order) so the same set -> the same bytes;
  * ``DecimalRange``    -> a dict of Decimal + bool;
  * enum (operator/category/outcome) -> its ``.value``;
  * ``Decimal`` / scalar literal -> native.

``content_hash`` is over the canonicalized **rule set + confidence bands**
(sorted by ``rule_id``), NOT the version label and NOT the ``content_hash`` field
itself (no self-reference, no volatile field).
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from backend.common.canon_ser import canon_ser, content_hash as _content_hash
from backend.rules_engine.report_schema import DecimalRange
from backend.rules_engine.rulebook_schema import Rulebook, Rule


def _normalize_threshold(threshold: Any) -> Any:
    if isinstance(threshold, DecimalRange):
        return {
            "low": threshold.low,
            "low_inclusive": threshold.low_inclusive,
            "high": threshold.high,
            "high_inclusive": threshold.high_inclusive,
        }
    if isinstance(threshold, list):  # set-threshold -> declared-sorted list
        return sorted(threshold, key=lambda x: canon_ser(x))
    return threshold  # Decimal or scalar literal (native to canon_ser)


def _normalize_rule(rule: Rule) -> dict[str, Any]:
    return {
        "rule_id": rule.rule_id,
        "category": rule.category.value,
        "input_fields": list(rule.input_fields),  # authored order preserved (stable per rule)
        "operator": rule.operator.value,
        "threshold": _normalize_threshold(rule.threshold),
        "outcome": rule.outcome.value,
        "rationale_message": rule.rationale_message,
        "irdai_ref": rule.irdai_ref,
    }


class RulebookCanonAdapter:
    """Normalize a Rulebook into the shared canon_ser value space (no fork)."""

    @staticmethod
    def canonical_form(rulebook: Rulebook) -> dict[str, Any]:
        return {
            "rules": [_normalize_rule(r) for r in sorted(rulebook.rules, key=lambda r: r.rule_id)],
            "confidence_bands": {
                "high_margin": rulebook.confidence_bands.high_margin,
                "low_margin": rulebook.confidence_bands.low_margin,
            },
        }

    @staticmethod
    def canonical_bytes(rulebook: Rulebook) -> bytes:
        return canon_ser(RulebookCanonAdapter.canonical_form(rulebook))

    @staticmethod
    def content_hash(rulebook: Rulebook) -> str:
        return _content_hash(RulebookCanonAdapter.canonical_form(rulebook))
