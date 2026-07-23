"""Rulebook input schema + load-time validators (FD ``domain-entities.md §2/§2.1``).

Pydantic v2 realization of the frozen `Rule` / `Rulebook` / `ConfidenceBands`
shapes. The validators are the **single structural load gate** (NFR Design §4):

  * **BR1-1** — every `input_fields` entry must be in the single-sourced
    `ALLOWED_INPUT_FIELDS` allowlist; a demographic path or any unknown field is
    **rejected at load** (a malformed/adversarial rulebook fails to load).
  * **SCHEMA-1** — the `threshold` shape must match the `operator` (§2.1);
    a mismatch is rejected at load.

The allowlist is **single-sourced here** and imported by `NamespaceBuilder`
(the independent namespace-exclusion guard) so both guards agree on one set.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.rules_engine.report_schema import (
    DecimalRange,
    Number,
    Operator,
    OutcomeTier,
    RuleCategory,
)

#: The ONLY profile fields a rule may name — the demographic-EXCLUDED namespace
#: (FD §2 note) + the engine-derived operands. Single source of truth for both
#: the load-time allowlist (here) and the runtime NamespaceBuilder.
ALLOWED_INPUT_FIELDS: frozenset[str] = frozenset({
    "age_years_derived",
    "bmi_derived",
    "verifiable_income_annual",
    "existing_debt_obligations_annual",
    "requested_cover_amount",
    "employment_type",
    "smoking_status",
    "occupation",
    "health_flags",
    "documents",
    # engine-derived operands (exposed in the resolution namespace)
    "dti_ratio",
    "income_multiple",
    # derived SCALAR operands for the non-scalar categories (FD §4.2 back-annotation)
    "health_flag_count",
    "documents_missing_count",
})

# A rule threshold: a single numeric bound, a range, a set (list of literals),
# or a scalar literal. Number first so numeric bounds keep their Decimal type.
RuleThreshold = Union[Number, DecimalRange, list, str]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ConfidenceBands(_Frozen):
    high_margin: Number
    low_margin: Number


class Rule(_Frozen):
    rule_id: str
    category: RuleCategory
    input_fields: list[str]
    operator: Operator
    # left_to_right: numeric bounds authored as YAML strings ("0.40") coerce to
    # Decimal (Number tried FIRST) per §2.1, instead of smart-union keeping them
    # as str; categorical literals still fall through to list/str.
    threshold: RuleThreshold = Field(union_mode="left_to_right")
    outcome: OutcomeTier
    rationale_message: str
    irdai_ref: str = ""

    @field_validator("input_fields")
    @classmethod
    def _fields_in_allowlist(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("input_fields must be non-empty")
        bad = [f for f in value if f not in ALLOWED_INPUT_FIELDS]
        if bad:  # BR1-1 — demographic path or unknown field
            raise ValueError(
                f"input_fields {bad} are outside the allowlist "
                f"(demographic or unknown field) — rejected at load (CON-BR1)"
            )
        return value

    @model_validator(mode="after")
    def _operator_threshold_shape(self) -> "Rule":
        op, th = self.operator, self.threshold
        numeric = (Operator.LTE, Operator.LT, Operator.GTE, Operator.GT)
        if op in numeric:
            if not isinstance(th, Decimal):
                raise ValueError(f"operator {op.value} requires a single Decimal threshold")
        elif op is Operator.BETWEEN:
            if not isinstance(th, DecimalRange):
                raise ValueError("operator between requires a DecimalRange threshold")
        elif op is Operator.IN:
            if not isinstance(th, list):
                raise ValueError("operator in requires a set/list threshold")
        elif op is Operator.EQ:
            if not isinstance(th, (Decimal, str)):
                raise ValueError("operator eq requires a scalar literal threshold")
        return self


class Rulebook(_Frozen):
    rulebook_version: str
    content_hash: str
    rules: list[Rule]
    confidence_bands: ConfidenceBands
