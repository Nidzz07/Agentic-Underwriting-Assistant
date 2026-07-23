"""Intake data contracts — the frozen C1 shapes (FD ``domain-entities.md``).

Pydantic v2 realization of the field-by-field FD. These are value objects:
``frozen=True`` (immutable once built — CON-DET-1 discipline) and
``extra="forbid"`` (reject unknown fields — SEC-2). No field or behaviour is
introduced beyond the FD; the ``R/O/D/S`` markers below mirror it.

Money / threshold fields are ``Decimal`` and REJECT IEEE ``float`` on input
(BR-TYP-1: never coerced through float, preserving exact boundaries), while
accepting ``str``/``int`` which coerce cleanly to ``Decimal``.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


# --------------------------------------------------------------------------
# Enums (declared string values are the canonical serialized forms)
# --------------------------------------------------------------------------
class EmploymentType(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    CONTRACT = "contract"
    UNEMPLOYED = "unemployed"
    UNKNOWN = "unknown"


class SmokingStatus(str, Enum):
    SMOKER = "smoker"
    NON_SMOKER = "non_smoker"
    UNKNOWN = "unknown"


class Gender(str, Enum):
    """Demographic field — used ONLY by the bias-swap suite (CON-BR1)."""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"
    UNSPECIFIED = "unspecified"


class DocType(str, Enum):
    SALARY_SLIP = "salary_slip"
    BANK_STATEMENT = "bank_statement"
    MEDICAL_QUESTIONNAIRE = "medical_questionnaire"


class DocStatus(str, Enum):
    """Four-state document status (FD §4)."""
    PRESENT = "present"          # uploaded, not yet parsed (transient)
    PARSED = "parsed"            # extracted OK
    MISSING = "missing"          # not supplied
    UNPARSEABLE = "unparseable"  # supplied but parse failed


class ReasonCategory(str, Enum):
    MALFORMED = "malformed"
    UNPARSEABLE = "unparseable"
    MISSING_REQUIRED = "missing_required"


class PatternCategory(str, Enum):
    INSTRUCTION_OVERRIDE = "instruction_override"
    ROLE_INJECTION = "role_injection"
    DELIMITER_ESCAPE = "delimiter_escape"
    TOOL_MIMIC = "tool_mimic"
    OTHER = "other"


# --------------------------------------------------------------------------
# Money type — Decimal that refuses IEEE float (BR-TYP-1)
# --------------------------------------------------------------------------
def _reject_float(value: object) -> object:
    if isinstance(value, float):
        raise ValueError("float not permitted; use Decimal or a decimal string (BR-TYP-1)")
    return value


Money = Annotated[Decimal, BeforeValidator(_reject_float)]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# --------------------------------------------------------------------------
# Sub-objects
# --------------------------------------------------------------------------
class Demographics(_Frozen):
    """Segregated demographic sub-object (CON-BR1). Never a rule/feature input."""
    full_name: str = Field(min_length=1)
    gender: Gender
    city: str = Field(min_length=1)


class DocumentEntry(_Frozen):
    doc_type: DocType
    status: DocStatus
    content_hash: str = ""  # empty if missing


class DocumentManifest(_Frozen):
    expected_count: int
    satisfied_count: int
    entries: list[DocumentEntry] = Field(default_factory=list)


# --------------------------------------------------------------------------
# ApplicantProfile — the single validated object downstream trusts
# --------------------------------------------------------------------------
class ApplicantProfile(_Frozen):
    application_id: str                              # S — system-assigned at gate pass
    date_of_birth: date                              # R
    as_of_date: date                                 # R
    age_years_derived: int                           # D
    height_cm: Optional[Money] = None                # O
    weight_kg: Optional[Money] = None                # O
    bmi_derived: Optional[Money] = None              # D (None if height/weight absent)
    verifiable_income_annual: Money                  # R
    requested_cover_amount: Money                    # R
    existing_debt_obligations_annual: Optional[Money] = None  # O
    employment_type: Optional[EmploymentType] = None          # O
    smoking_status: Optional[SmokingStatus] = None            # O
    occupation: Optional[str] = None                          # O
    health_flags: list[str] = Field(default_factory=list)     # O
    incomplete: bool = False                                  # D — a flag, never a recommendation
    demographics: Demographics                                # R (segregated)
    documents: DocumentManifest                               # R


# --------------------------------------------------------------------------
# Sanitizer output contract (U2)
# --------------------------------------------------------------------------
class SanitizationReportEntry(_Frozen):
    source_field: str
    original_span: str          # verbatim, AUDIT-ONLY — never to any LLM-bound context
    neutralized_span: str
    pattern_category: PatternCategory


class SanitizedText(_Frozen):
    source_ref: str
    clean_text: str
    was_modified: bool
    report: list[SanitizationReportEntry] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Gate rejection output (carries no partial profile, no application_id)
# --------------------------------------------------------------------------
class FieldError(_Frozen):
    field: str
    code: str
    message: str


class RejectedIntake(_Frozen):
    reason_category: ReasonCategory
    field_errors: list[FieldError] = Field(default_factory=list)
    missing_items: list[str] = Field(default_factory=list)
