"""Shared seeded synthetic corpus + applicant factory (Q3-A) — one factory, reused everywhere.

Builds plain frozen ``CorpusRecord`` / ``ApplicantProfile`` objects (real ``intake`` /
``corpus_generator`` schemas — a TEST module, so schema imports are fine; ``tests/`` is excluded
from every StructuralGuard scan). Provides: (i) a small deterministic NORMAL corpus for the fit;
(ii) a profile with a deliberately-MISSING optional (IMPUTE-1 teeth); (iii) a SWAP-INVARIANCE
pair — identical financials, swapped name/gender/city (BIAS-1 teeth); (iv) an OUTLIER profile
with extreme financials (COMPOSE-1). No RNG, no wall-clock — every value is fixed.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from backend.corpus_generator.records import CorpusManifest, CorpusRecord
from backend.intake.schema import (
    ApplicantProfile,
    Demographics,
    DocumentEntry,
    DocumentManifest,
    DocStatus,
    DocType,
    Gender,
)
from backend.rules_engine.report_schema import Recommendation

_DOB = date(1988, 5, 4)
_AS_OF = date(2026, 1, 1)


def _documents(missing: int) -> DocumentManifest:
    """A 3-document manifest with ``missing`` required documents unsatisfied."""
    types = [DocType.SALARY_SLIP, DocType.BANK_STATEMENT, DocType.MEDICAL_QUESTIONNAIRE]
    entries = [
        DocumentEntry(
            doc_type=t,
            status=DocStatus.MISSING if i < missing else DocStatus.PARSED,
            content_hash="" if i < missing else f"hash-{i}",
        )
        for i, t in enumerate(types)
    ]
    return DocumentManifest(expected_count=3, satisfied_count=3 - missing, entries=entries)


def make_profile(
    *,
    application_id: str = "app-000",
    age: int = 40,
    income: Decimal = Decimal("600000"),
    cover: Decimal = Decimal("3000000"),
    bmi: Optional[Decimal] = Decimal("24.0"),
    debt: Optional[Decimal] = Decimal("120000"),
    health_flag_count: int = 0,
    missing_docs: int = 0,
    full_name: str = "Applicant Zero",
    gender: Gender = Gender.FEMALE,
    city: str = "Pune",
) -> ApplicantProfile:
    """One applicant. Money fields are ``Decimal`` (never ``float`` — BR-TYP-1)."""
    return ApplicantProfile(
        application_id=application_id,
        date_of_birth=_DOB,
        as_of_date=_AS_OF,
        age_years_derived=age,
        bmi_derived=bmi,
        verifiable_income_annual=income,
        requested_cover_amount=cover,
        existing_debt_obligations_annual=debt,
        health_flags=[f"flag_{i}" for i in range(health_flag_count)],
        demographics=Demographics(full_name=full_name, gender=gender, city=city),
        documents=_documents(missing_docs),
    )


def _corpus_income(i: int) -> Decimal:
    return Decimal(500000 + i * 10000)


def _corpus_cover(i: int, income: Decimal) -> Decimal:
    # Genuine spread in income_multiple (4.0 → ...): NOT an analytically constant column.
    return (income * (Decimal("4.0") + Decimal(i) * Decimal("0.2"))).quantize(Decimal("1"))


def _corpus_debt(i: int, income: Decimal) -> Decimal:
    # Genuine spread in dti_ratio (0.15 → ...): NOT an analytically constant column.
    return (income * (Decimal("0.15") + Decimal(i) * Decimal("0.01"))).quantize(Decimal("1"))


def normal_corpus_profiles(n: int = 12) -> list[ApplicantProfile]:
    """A small deterministic normal corpus — real spread in income/cover/age/bmi/dti/multiple.

    ``health_flag_count`` (0) and ``documents_missing_count`` (0) are held integer-constant so
    the model's exact ``std == 0`` zero-variance branch is exercised on real data.
    """
    profiles: list[ApplicantProfile] = []
    for i in range(n):
        income = _corpus_income(i)
        profiles.append(
            make_profile(
                application_id=f"corpus-{i}",
                age=30 + i,
                income=income,
                cover=_corpus_cover(i, income),
                bmi=Decimal("22.0") + Decimal(i) * Decimal("0.3"),
                debt=_corpus_debt(i, income),
                health_flag_count=0,
                missing_docs=0,
            )
        )
    return profiles


def typical_profile() -> ApplicantProfile:
    """An applicant squarely inside the corpus (a mid member) → no flags, an inlier (COMPOSE-1)."""
    i = 6
    income = _corpus_income(i)
    return make_profile(
        application_id="app-typical",
        age=30 + i,
        income=income,
        cover=_corpus_cover(i, income),
        bmi=Decimal("22.0") + Decimal(i) * Decimal("0.3"),
        debt=_corpus_debt(i, income),
        health_flag_count=0,
        missing_docs=0,
    )


def corpus_records(profiles: Optional[list[ApplicantProfile]] = None) -> list[CorpusRecord]:
    """Wrap profiles as ``CorpusRecord``s (label present but unused by scoring)."""
    profiles = profiles if profiles is not None else normal_corpus_profiles()
    return [
        CorpusRecord(
            profile=p,
            documents_text={},
            label=Recommendation.APPROVE,
            intended_class=Recommendation.APPROVE,
            edge_case_tags=[],
        )
        for p in profiles
    ]


def make_manifest(*, seed: int = 4242, corpus_version: str = "corpus-test-v1") -> CorpusManifest:
    """A minimal valid frozen manifest — only ``seed`` + ``corpus_version`` are read by the model."""
    return CorpusManifest(
        seed=seed,
        corpus_version=corpus_version,
        rulebook_version="rb-test-v1",
        engine_version="engine-test-v1",
        provider="gemini",
        model_version="model-test-v1",
        class_counts={"APPROVE": 12},
        class_proportions={"APPROVE": "1.0"},
        tolerance_pp=Decimal("0.05"),
        edge_case_checklist={},
        profile_count=12,
        content_hash="deadbeef",
        generation_timestamp="2026-01-01T00:00:00Z",
    )


def missing_optional_profile() -> ApplicantProfile:
    """A thin-file profile: ``bmi_derived`` / debt / dti all ``None`` (IMPUTE-1)."""
    return make_profile(
        application_id="app-missing",
        age=41,
        income=Decimal("610000"),
        cover=Decimal("3050000"),
        bmi=None,
        debt=None,
    )


def swap_pair() -> tuple[ApplicantProfile, ApplicantProfile]:
    """Two profiles: identical financials, swapped name/gender/city (BIAS-1)."""
    base = dict(
        application_id="app-swap",
        age=44,
        income=Decimal("640000"),
        cover=Decimal("3200000"),
        bmi=Decimal("25.0"),
        debt=Decimal("128000"),
        health_flag_count=1,
        missing_docs=1,
    )
    a = make_profile(**base, full_name="Asha Rao", gender=Gender.FEMALE, city="Pune")
    b = make_profile(**base, full_name="Bhaskar Iyer", gender=Gender.MALE, city="Chennai")
    return a, b


def outlier_profile() -> ApplicantProfile:
    """Extreme financials — well outside the corpus distribution (COMPOSE-1)."""
    return make_profile(
        application_id="app-outlier",
        age=64,
        income=Decimal("50000000"),
        cover=Decimal("900000000"),
        bmi=Decimal("41.0"),
        debt=Decimal("45000000"),
        health_flag_count=6,
        missing_docs=2,
    )
