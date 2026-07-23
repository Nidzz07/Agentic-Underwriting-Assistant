"""C2 ``ProfileFactory`` — seeded construction of valid ``ApplicantProfile`` records.

Every structured field is a pure function of the injected seeded ``random.Random``
+ seeded ``Faker`` — no wall-clock (a fixed ``_AS_OF_ANCHOR`` is used, never
``date.today()``), no unseeded randomness (DET-1 / BR-CORP-1). Age/BMI are derived
**only** via ``intake.derivations`` (single-sourced, boundary-exact; no local
re-implementation — REFNOTOWN-1 / PROFILE-1). The synthetic ``application_id`` is
``corpus-<seed>-<index>`` (Q2 / BR-CORP-9).

Demographics (name / gender / city) are populated **seeded-independently** into the
already-segregated ``Demographics`` sub-object and NEVER influence the financial /
medical fields or the engine label (BR-CORP-7 layered-respect; the CON-BR1 *suite*
lives in ``quality-gates``).

The recipes construct raw inputs biased toward a target class / edge case; the
engine remains the label authority (``LabelingOracle``) — the stored label is
always the engine's, never the ``intended_class`` here (Fold 1/3).
"""
from __future__ import annotations

import random
from datetime import date
from decimal import Decimal
from typing import Optional

from faker import Faker

from backend.intake.derivations import compute_age, compute_bmi
from backend.intake.schema import (
    ApplicantProfile,
    Demographics,
    DocStatus,
    DocType,
    DocumentEntry,
    DocumentManifest,
    EmploymentType,
    Gender,
    SmokingStatus,
)
from backend.rules_engine.report_schema import Recommendation

#: Fixed clock-free anchor for age derivation (DET-1 — never ``date.today()``).
_AS_OF_ANCHOR = date(2026, 1, 1)
_LOW_RISK_OCCUPATION = "engineer"  # within the rulebook's sanctioned low-risk set
_GENDERS = tuple(Gender)
_THREE_DOC_TYPES = (DocType.SALARY_SLIP, DocType.BANK_STATEMENT, DocType.MEDICAL_QUESTIONNAIRE)


class ProfileFactory:
    """Seeded factory producing valid frozen ``ApplicantProfile`` records."""

    def __init__(self, rng: random.Random, faker: Faker, seed: int) -> None:
        self._rng = rng
        self._faker = faker
        self._seed = seed

    # -- helpers ------------------------------------------------------------
    def _demographics(self) -> Demographics:
        """Seeded-independent demographic identifiers — never a label input."""
        return Demographics(
            full_name=self._faker.name(),
            gender=self._rng.choice(_GENDERS),
            city=self._faker.city(),
        )

    @staticmethod
    def _dob_for_age(age: int) -> date:
        return date(_AS_OF_ANCHOR.year - age, _AS_OF_ANCHOR.month, _AS_OF_ANCHOR.day)

    @staticmethod
    def _documents(missing: int = 0) -> DocumentManifest:
        entries = []
        for idx, doc_type in enumerate(_THREE_DOC_TYPES):
            is_missing = idx < missing
            entries.append(
                DocumentEntry(
                    doc_type=doc_type,
                    status=DocStatus.MISSING if is_missing else DocStatus.PARSED,
                    content_hash="" if is_missing else f"synthetic-doc-hash-{idx}",
                )
            )
        return DocumentManifest(
            expected_count=len(_THREE_DOC_TYPES),
            satisfied_count=len(_THREE_DOC_TYPES) - missing,
            entries=entries,
        )

    def _build(
        self,
        index: int,
        *,
        age: int = 40,
        height_cm: Optional[str] = "175",
        weight_kg: Optional[str] = "70",
        income: str = "200000",
        cover: str = "200000",
        debt: Optional[str] = "20000",
        employment: EmploymentType = EmploymentType.SALARIED,
        smoking: SmokingStatus = SmokingStatus.NON_SMOKER,
        occupation: Optional[str] = _LOW_RISK_OCCUPATION,
        health_flags: tuple[str, ...] = (),
        missing_docs: int = 0,
    ) -> ApplicantProfile:
        dob = self._dob_for_age(age)
        height = Decimal(height_cm) if height_cm is not None else None
        weight = Decimal(weight_kg) if weight_kg is not None else None
        bmi = compute_bmi(height, weight) if (height is not None and weight is not None) else None
        return ApplicantProfile(
            application_id=f"corpus-{self._seed}-{index}",
            date_of_birth=dob,
            as_of_date=_AS_OF_ANCHOR,
            age_years_derived=compute_age(dob, _AS_OF_ANCHOR),
            height_cm=height,
            weight_kg=weight,
            bmi_derived=bmi,
            verifiable_income_annual=Decimal(income),
            requested_cover_amount=Decimal(cover),
            existing_debt_obligations_annual=Decimal(debt) if debt is not None else None,
            employment_type=employment,
            smoking_status=smoking,
            occupation=occupation,
            health_flags=list(health_flags),
            incomplete=False,
            demographics=self._demographics(),
            documents=self._documents(missing_docs),
        )

    def _jittered_income(self) -> str:
        """A seeded income safely above the IRDAI floor (keeps the class stable)."""
        return str(150_000 + self._rng.randint(0, 150) * 1_000)

    # -- class-target recipes (bulk band fill) ------------------------------
    def build_approve(self, index: int) -> tuple[ApplicantProfile, list[str]]:
        income = self._jittered_income()
        return self._build(index, income=income, cover=income), []

    def build_refer(self, index: int) -> tuple[ApplicantProfile, list[str]]:
        # a smoker — SMOKE-STATUS-1 refer_trigger; everything else clean
        income = self._jittered_income()
        return self._build(index, income=income, cover=income, smoking=SmokingStatus.SMOKER), []

    def build_decline(self, index: int) -> tuple[ApplicantProfile, list[str]]:
        # age 70 — outside the 18-65 band -> AGE-BAND-1 decline_fail
        income = self._jittered_income()
        return self._build(index, age=70, income=income, cover=income), []

    # -- edge-case recipes (deterministic; each carries its DATA-2 tag) ------
    def build_edge(self, index: int, edge: str) -> tuple[ApplicantProfile, list[str]]:
        builder = _EDGE_BUILDERS.get(edge)
        if builder is None:
            raise ValueError(f"unknown edge case {edge!r}")
        return builder(self, index), [edge]

    def _edge_age_18(self, index: int) -> ApplicantProfile:
        return self._build(index, age=18)                       # boundary pass -> APPROVE

    def _edge_age_65(self, index: int) -> ApplicantProfile:
        return self._build(index, age=65)                       # boundary pass -> APPROVE

    def _edge_bmi_25(self, index: int) -> ApplicantProfile:
        return self._build(index, height_cm="200", weight_kg="100")   # bmi 25.00 -> APPROVE

    def _edge_bmi_30(self, index: int) -> ApplicantProfile:
        return self._build(index, height_cm="200", weight_kg="120")   # bmi 30.00 -> REFER

    def _edge_dti_40(self, index: int) -> ApplicantProfile:
        # dti = 80000 / 200000 = 0.40 exactly -> DTI-CEIL-1 pass boundary -> APPROVE
        return self._build(index, income="200000", cover="200000", debt="80000")

    def _edge_thin_file(self, index: int) -> ApplicantProfile:
        return self._build(index, missing_docs=2)               # minimal doc history -> REFER

    def _edge_single_missing_document(self, index: int) -> ApplicantProfile:
        return self._build(index, missing_docs=1)               # one missing doc -> REFER

    def _edge_self_employed_irregular(self, index: int) -> ApplicantProfile:
        return self._build(index, employment=EmploymentType.SELF_EMPLOYED)  # -> REFER


#: edge name -> bound builder method (module-level so the mapping is explicit).
_EDGE_BUILDERS = {
    "age_18": ProfileFactory._edge_age_18,
    "age_65": ProfileFactory._edge_age_65,
    "bmi_25": ProfileFactory._edge_bmi_25,
    "bmi_30": ProfileFactory._edge_bmi_30,
    "dti_40": ProfileFactory._edge_dti_40,
    "thin_file": ProfileFactory._edge_thin_file,
    "single_missing_document": ProfileFactory._edge_single_missing_document,
    "self_employed_irregular": ProfileFactory._edge_self_employed_irregular,
}

#: the intended (generation-target) class each recipe biases toward — provenance
#: only; the engine label is always the authority.
INTENDED_CLASS_FOR_EDGE: dict[str, Recommendation] = {
    "age_18": Recommendation.APPROVE,
    "age_65": Recommendation.APPROVE,
    "bmi_25": Recommendation.APPROVE,
    "dti_40": Recommendation.APPROVE,
    "bmi_30": Recommendation.REFER,
    "thin_file": Recommendation.REFER,
    "single_missing_document": Recommendation.REFER,
    "self_employed_irregular": Recommendation.REFER,
}
