"""Rules-engine output contract — the frozen C2 shapes (FD ``domain-entities.md §6``).

Pydantic v2 realization of the tri-state ``RuleResult`` and the
``RuleResultReport``. Value objects: ``frozen=True`` + ``extra="forbid"``. Money
/ threshold values are ``Decimal`` and REJECT IEEE ``float`` (CON-DET-1 / no
boundary drift).

This module also holds the **shared value types** (``Operator`` / ``RuleCategory``
/ ``OutcomeTier`` / ``RuleStatus`` / ``DecimalRange``) that both the rulebook
input schema and this output contract reference — placed here (the schema leaf)
so ``rulebook_schema`` imports them one-way (no circular import).
"""
from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Annotated, Optional, Union

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


# --------------------------------------------------------------------------
# Shared enums (declared string values are the canonical serialized forms)
# --------------------------------------------------------------------------
class Recommendation(str, Enum):
    APPROVE = "APPROVE"
    REFER = "REFER"
    DECLINE_RECOMMEND = "DECLINE-RECOMMEND"  # -RECOMMEND suffix mandatory (FR-RULES-5)


class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Operator(str, Enum):
    LTE = "lte"
    LT = "lt"
    GTE = "gte"
    GT = "gt"
    EQ = "eq"
    IN = "in"
    BETWEEN = "between"


class RuleCategory(str, Enum):
    AGE_ELIGIBILITY = "age_eligibility"
    MEDICAL_BMI = "medical_bmi"
    MEDICAL_HEALTH = "medical_health"
    FINANCIAL_DTI = "financial_dti"
    FINANCIAL_INCOME_MULTIPLE = "financial_income_multiple"
    DOCUMENT_COMPLETENESS = "document_completeness"
    LIFESTYLE_SMOKING = "lifestyle_smoking"
    LIFESTYLE_OCCUPATION = "lifestyle_occupation"
    COMPLIANCE_IRDAI = "compliance_irdai"


class RuleStatus(str, Enum):
    """Tri-state (FD §6.1)."""
    PASS = "pass"
    FAIL = "fail"
    NOT_EVALUATED = "not_evaluated"


class OutcomeTier(str, Enum):
    PASS_ONLY = "pass_only"
    REFER_TRIGGER = "refer_trigger"
    DECLINE_FAIL = "decline_fail"


def _reject_float(value: object) -> object:
    if isinstance(value, float):
        raise ValueError("float not permitted; use Decimal or a decimal string (CON-DET-1)")
    return value


Number = Annotated[Decimal, BeforeValidator(_reject_float)]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DecimalRange(_Frozen):
    """Inclusive/exclusive numeric range for the ``between`` operator (FD §2.1)."""
    low: Number
    low_inclusive: bool
    high: Number
    high_inclusive: bool


# A threshold as recorded on a result: a single bound, a range, or a set (as a
# canonical list of scalar literals). ``Decimal`` first so numeric bounds keep
# their type.
ThresholdRepr = Union[Number, DecimalRange, list]


class RuleResult(_Frozen):
    rule_id: str
    category: RuleCategory
    status: RuleStatus
    actual_value: Optional[Union[Number, str]] = None  # null when not_evaluated
    operator: Operator
    threshold: ThresholdRepr
    outcome_tier: OutcomeTier
    message: str


class RuleResultReport(_Frozen):
    rule_results: list[RuleResult] = Field(default_factory=list)  # ALL rules (passes included)
    recommendation: Recommendation
    confidence: Confidence
    rulebook_version: str
    content_hash: str
    engine_version: str
    decline_reasons: list[str] = Field(default_factory=list)
    refer_reasons: list[str] = Field(default_factory=list)
