"""IntakeGate — the SEC-2 total-function validation gate (FD §1/§2, NFR §4).

A single fail-closed boundary wrapper around the Pydantic v2 contract. It is the
SOLE exit of ``validate_gate`` and provably returns ``ApplicantProfile |
RejectedIntake`` — every input, including arbitrary garbage, maps to exactly one
of them and NO input can cause an unhandled raise (unexpected exception ->
``RejectedIntake(malformed)``, fail-closed).

Reject-vs-REFER (FD §2): reject only what is structurally unrecoverable;
everything merely incomplete becomes a valid ``ApplicantProfile(incomplete=True)``
that ``rules-engine`` routes to REFER. Intake never emits a recommendation
(CON-BR2). Reason precedence: structural-invalid -> ``malformed``; else a missing
required value with an unparseable expected doc -> ``unparseable``; else plain
absence -> ``missing_required``.

``application_id`` is system-assigned ONLY on gate pass via an injectable
generator seam (default uuid-based); a ``RejectedIntake`` never receives one.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Callable, Optional
from uuid import uuid4

from backend.intake import schema as s
from backend.intake.derivations import compute_age, compute_bmi

_EXPECTED_DOCS: tuple[s.DocType, ...] = (
    s.DocType.SALARY_SLIP,
    s.DocType.BANK_STATEMENT,
    s.DocType.MEDICAL_QUESTIONNAIRE,
)
_AGE_SANITY_MIN = 0
_AGE_SANITY_MAX = 120


class _Malformed(Exception):
    """Internal: a structurally invalid (present-but-bad) value."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field
        self.message = message


def _parse_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise _Malformed("date", "date must be an ISO string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise _Malformed("date", f"unparseable date: {value!r}") from exc


def _parse_decimal(value: Any, field: str) -> Decimal:
    # BR-TYP-1: never coerce through float.
    if isinstance(value, float):
        raise _Malformed(field, "float not permitted; use a decimal string")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (str, int)):
        try:
            return Decimal(str(value))
        except InvalidOperation as exc:
            raise _Malformed(field, f"non-numeric value: {value!r}") from exc
    raise _Malformed(field, f"unsupported money value type: {type(value)!r}")


class IntakeGate:
    """The single fail-closed SEC-2 gate."""

    def __init__(self, id_generator: Optional[Callable[[], str]] = None) -> None:
        self._new_id: Callable[[], str] = id_generator or (lambda: f"APP-{uuid4().hex}")

    def validate_gate(self, extracted: Any) -> s.ApplicantProfile | s.RejectedIntake:
        """Total function: returns exactly one handled result, never raises."""
        try:
            return self._evaluate(extracted)
        except _Malformed as m:
            return s.RejectedIntake(
                reason_category=s.ReasonCategory.MALFORMED,
                field_errors=[s.FieldError(field=m.field, code="malformed", message=m.message)],
                missing_items=[],
            )
        except Exception:  # fail-closed — no leak, no crash, no raise
            return s.RejectedIntake(
                reason_category=s.ReasonCategory.MALFORMED,
                field_errors=[s.FieldError(field="_gate", code="unexpected_error",
                                           message="gate caught an unexpected error")],
                missing_items=[],
            )

    # -- internals -----------------------------------------------------------
    def _evaluate(self, extracted: Any) -> s.ApplicantProfile | s.RejectedIntake:
        if not isinstance(extracted, Mapping):
            return s.RejectedIntake(
                reason_category=s.ReasonCategory.MALFORMED,
                field_errors=[s.FieldError(field="_root", code="not_a_mapping",
                                           message="extracted draft must be a mapping")],
                missing_items=[],
            )

        manifest = self._build_manifest(extracted.get("documents"))

        # Required primitives (present-but-invalid raises _Malformed -> malformed).
        missing: list[str] = []
        dob = self._opt(extracted, "date_of_birth", lambda v: _parse_date(v), missing)
        as_of = self._opt(extracted, "as_of_date", lambda v: _parse_date(v), missing)
        income = self._opt(extracted, "verifiable_income_annual",
                           lambda v: _parse_decimal(v, "verifiable_income_annual"), missing)
        cover = self._opt(extracted, "requested_cover_amount",
                          lambda v: _parse_decimal(v, "requested_cover_amount"), missing)

        # Structural cross-field checks on present values.
        if income is not None and income < 0:
            raise _Malformed("verifiable_income_annual", "income must be >= 0")
        if cover is not None and cover <= 0:
            raise _Malformed("requested_cover_amount", "requested cover must be > 0")
        if dob is not None and as_of is not None and dob > as_of:
            raise _Malformed("date_of_birth", "date_of_birth must be <= as_of_date")

        if missing:  # a required VALUE is unrecoverable from any source
            has_unparseable_doc = any(
                e.status is s.DocStatus.UNPARSEABLE for e in manifest.entries
            )
            reason = (s.ReasonCategory.UNPARSEABLE if has_unparseable_doc
                      else s.ReasonCategory.MISSING_REQUIRED)
            unparseable_docs = [e.doc_type.value for e in manifest.entries
                                if e.status is s.DocStatus.UNPARSEABLE]
            return s.RejectedIntake(
                reason_category=reason,
                field_errors=[s.FieldError(field=f, code="missing", message="required value absent")
                              for f in missing],
                missing_items=missing + unparseable_docs,
            )

        # Deterministic derivations (stored).
        assert dob is not None and as_of is not None  # guaranteed by `missing` check
        age = compute_age(dob, as_of)
        if not (_AGE_SANITY_MIN <= age <= _AGE_SANITY_MAX):
            raise _Malformed("age_years_derived", f"age {age} out of sanity range")

        height = self._opt(extracted, "height_cm",
                           lambda v: _parse_decimal(v, "height_cm"), [])
        weight = self._opt(extracted, "weight_kg",
                           lambda v: _parse_decimal(v, "weight_kg"), [])
        if height is not None and height <= 0:
            raise _Malformed("height_cm", "height_cm must be > 0")
        if weight is not None and weight <= 0:
            raise _Malformed("weight_kg", "weight_kg must be > 0")
        bmi = compute_bmi(height, weight) if (height is not None and weight is not None) else None

        debt = self._opt(extracted, "existing_debt_obligations_annual",
                         lambda v: _parse_decimal(v, "existing_debt_obligations_annual"), [])
        if debt is not None and debt < 0:
            raise _Malformed("existing_debt_obligations_annual", "debt must be >= 0")

        employment = self._enum(extracted, "employment_type", s.EmploymentType)
        smoking = self._enum(extracted, "smoking_status", s.SmokingStatus)
        occupation = extracted.get("occupation")
        health_flags = list(extracted.get("health_flags") or [])
        demographics = self._build_demographics(extracted)

        # incomplete: any optional operand/document materially absent.
        incomplete = (
            bmi is None
            or debt is None
            or employment is None
            or smoking is None
            or not occupation
            or not health_flags
            or any(e.status is not s.DocStatus.PARSED for e in manifest.entries)
        )

        return s.ApplicantProfile(
            application_id=self._new_id(),
            date_of_birth=dob,
            as_of_date=as_of,
            age_years_derived=age,
            height_cm=height,
            weight_kg=weight,
            bmi_derived=bmi,
            verifiable_income_annual=income,  # type: ignore[arg-type]
            requested_cover_amount=cover,     # type: ignore[arg-type]
            existing_debt_obligations_annual=debt,
            employment_type=employment,
            smoking_status=smoking,
            occupation=occupation,
            health_flags=health_flags,
            incomplete=incomplete,
            demographics=demographics,
            documents=manifest,
        )

    @staticmethod
    def _opt(extracted: Mapping, key: str, parse: Callable[[Any], Any],
             missing: list[str]) -> Any:
        """Parse an optionally-present value; record absence in ``missing``."""
        if key not in extracted or extracted.get(key) in (None, ""):
            missing.append(key)
            return None
        return parse(extracted[key])

    @staticmethod
    def _enum(extracted: Mapping, key: str, enum_cls) -> Any:
        value = extracted.get(key)
        if value in (None, ""):
            return None
        try:
            return enum_cls(value)
        except ValueError as exc:
            raise _Malformed(key, f"invalid {key}: {value!r}") from exc

    def _build_manifest(self, raw: Any) -> s.DocumentManifest:
        entries: list[s.DocumentEntry] = []
        rows = raw.get("entries") if isinstance(raw, Mapping) else raw
        if isinstance(raw, s.DocumentManifest):
            rows = list(raw.entries)
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, s.DocumentEntry):
                    entry = row
                else:
                    status = s.DocStatus(row["status"])
                    if status is s.DocStatus.PRESENT:  # never silently admit
                        status = s.DocStatus.UNPARSEABLE
                    entry = s.DocumentEntry(
                        doc_type=s.DocType(row["doc_type"]),
                        status=status,
                        content_hash=row.get("content_hash", ""),
                    )
                entries.append(entry)
        present_types = {e.doc_type for e in entries}
        for dt in _EXPECTED_DOCS:
            if dt not in present_types:
                entries.append(s.DocumentEntry(doc_type=dt, status=s.DocStatus.MISSING))
        satisfied = sum(1 for e in entries if e.status is s.DocStatus.PARSED)
        return s.DocumentManifest(
            expected_count=len(_EXPECTED_DOCS), satisfied_count=satisfied, entries=entries
        )

    @staticmethod
    def _build_demographics(extracted: Mapping) -> s.Demographics:
        # Demographics are required (R) and validated here; the schema enforces
        # non-empty full_name/city and a valid gender. Absence/empty -> the
        # outer wrapper maps the ValidationError to malformed (structural).
        return s.Demographics(
            full_name=extracted.get("full_name"),      # type: ignore[arg-type]
            gender=s.Gender(extracted.get("gender", s.Gender.UNSPECIFIED.value)),
            city=extracted.get("city"),                # type: ignore[arg-type]
        )
