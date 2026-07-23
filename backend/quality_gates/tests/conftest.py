"""Fixtures — hand-crafted in-memory stub corpus + injected fake engines (Q4-A/Q5-A).

No network, no LLM, no committed ``corpus/`` — everything is a tiny controlled
synthetic stub. The **real** deterministic engine is built call-only from the repo
rulebook; the **controlled fixture** engine is built from the P3a fixture rulebook.
The biased / non-deterministic **fakes** are duck-typed doubles (they mirror the
``engine.evaluate(profile, rulebook_version)`` seam) — injecting one means the real
``evaluate()`` is never routed through (NFR-QG-Fold-1).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Optional

import pytest

from backend.corpus_generator.records import CorpusManifest, CorpusRecord
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
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader
from backend.rules_engine.report_schema import Confidence, Recommendation, RuleResultReport

# --------------------------------------------------------------------------
# Paths / versions
# --------------------------------------------------------------------------
_REPO_RULEBOOK_DIR = str(Path(__file__).resolve().parents[2] / "rules_engine" / "rulebook")
REAL_RULEBOOK_VERSION = "1.0.0"
FIXTURE_RULEBOOK_DIR = str(Path(__file__).resolve().parent / "fixtures" / "controlled_rulebook")
FIXTURE_RULEBOOK_VERSION = "qg-test-0.0.1"
FIXTURE_COVERAGE_JSON = str(Path(__file__).resolve().parent / "fixtures" / "coverage_sample.json")
ENGINE_VERSION = "qg-test-engine-1"


# --------------------------------------------------------------------------
# Stub profile builder (synthetic — no real PII)
# --------------------------------------------------------------------------
def _documents(missing: int = 0) -> DocumentManifest:
    doc_types = (DocType.SALARY_SLIP, DocType.BANK_STATEMENT, DocType.MEDICAL_QUESTIONNAIRE)
    entries = [
        DocumentEntry(
            doc_type=dt,
            status=DocStatus.MISSING if idx < missing else DocStatus.PARSED,
            content_hash="" if idx < missing else f"synthetic-{idx}",
        )
        for idx, dt in enumerate(doc_types)
    ]
    return DocumentManifest(
        expected_count=len(doc_types), satisfied_count=len(doc_types) - missing, entries=entries
    )


def make_profile(
    application_id: str = "stub-0",
    *,
    gender: Gender = Gender.MALE,
    age: int = 40,
    income: str = "200000",
    cover: str = "200000",
    debt: Optional[str] = "20000",
    height: Optional[str] = "175",
    weight: Optional[str] = "70",
    bmi: Optional[str] = "22.9",
    occupation: Optional[str] = "engineer",
    smoking: SmokingStatus = SmokingStatus.NON_SMOKER,
    employment: EmploymentType = EmploymentType.SALARIED,
    missing_docs: int = 0,
) -> ApplicantProfile:
    """A valid frozen synthetic ``ApplicantProfile``. ``height/weight/bmi=None``
    leaves ``bmi_derived`` absent (the RULECOV-1 teeth mechanism)."""
    return ApplicantProfile(
        application_id=application_id,
        date_of_birth=date(2026 - age, 1, 1),
        as_of_date=date(2026, 1, 1),
        age_years_derived=age,
        height_cm=Decimal(height) if height is not None else None,
        weight_kg=Decimal(weight) if weight is not None else None,
        bmi_derived=Decimal(bmi) if bmi is not None else None,
        verifiable_income_annual=Decimal(income),
        requested_cover_amount=Decimal(cover),
        existing_debt_obligations_annual=Decimal(debt) if debt is not None else None,
        employment_type=employment,
        smoking_status=smoking,
        occupation=occupation,
        health_flags=[],
        incomplete=False,
        demographics=Demographics(full_name="Test Person", gender=gender, city="Testville"),
        documents=_documents(missing_docs),
    )


# --------------------------------------------------------------------------
# Real + fixture engines (call-only, reference-not-own)
# --------------------------------------------------------------------------
@pytest.fixture
def real_engine() -> RulesEngine:
    """The real deterministic engine over the repo rulebook (1.0.0)."""
    return RulesEngine(RulebookLoader(_REPO_RULEBOOK_DIR), ENGINE_VERSION)


@pytest.fixture
def fixture_loader() -> RulebookLoader:
    """A loader over the P3a controlled fixture rulebook dir."""
    return RulebookLoader(FIXTURE_RULEBOOK_DIR)


@pytest.fixture
def fixture_engine(fixture_loader: RulebookLoader) -> RulesEngine:
    """The engine over the controlled fixture rulebook (qg-test-0.0.1)."""
    return RulesEngine(fixture_loader, ENGINE_VERSION)


# --------------------------------------------------------------------------
# Injected duck-typed fake engines (teeth) — NEVER route through real evaluate()
# --------------------------------------------------------------------------
def _fake_report(recommendation: Recommendation) -> RuleResultReport:
    return RuleResultReport(
        rule_results=[],
        recommendation=recommendation,
        confidence=Confidence.MEDIUM,
        rulebook_version="fake",
        content_hash="fake",
        engine_version="fake",
    )


class BiasedFakeEngine:
    """A bias BUG — the recommendation depends on a demographic field (gender)."""

    def evaluate(self, profile: ApplicantProfile, rulebook_version: str) -> RuleResultReport:
        recommendation = (
            Recommendation.APPROVE
            if profile.demographics.gender == Gender.MALE
            else Recommendation.DECLINE_RECOMMEND
        )
        return _fake_report(recommendation)


class NonDeterministicFakeEngine:
    """A determinism BUG — the output alternates between runs of the same input."""

    def __init__(self) -> None:
        self._n = 0

    def evaluate(self, profile: ApplicantProfile, rulebook_version: str) -> RuleResultReport:
        self._n += 1
        recommendation = Recommendation.APPROVE if self._n % 2 else Recommendation.REFER
        return _fake_report(recommendation)


@pytest.fixture
def biased_engine() -> BiasedFakeEngine:
    return BiasedFakeEngine()


@pytest.fixture
def nondeterministic_engine() -> NonDeterministicFakeEngine:
    return NonDeterministicFakeEngine()


# --------------------------------------------------------------------------
# Stub corpus (in-memory) + a minimal manifest
# --------------------------------------------------------------------------
@pytest.fixture
def stub_profiles() -> list[ApplicantProfile]:
    """A small clean synthetic corpus (all pass the real engine cleanly)."""
    return [
        make_profile("stub-0", gender=Gender.MALE),
        make_profile("stub-1", gender=Gender.FEMALE, income="180000", cover="180000"),
        make_profile("stub-2", gender=Gender.MALE, age=30),
    ]


@pytest.fixture
def stub_records(stub_profiles: list[ApplicantProfile]) -> list[CorpusRecord]:
    return [
        CorpusRecord(
            profile=profile,
            documents_text={},
            label=Recommendation.APPROVE,
            intended_class=Recommendation.APPROVE,
            edge_case_tags=[],
        )
        for profile in stub_profiles
    ]


@pytest.fixture
def stub_manifest() -> CorpusManifest:
    return CorpusManifest(
        seed=7,
        corpus_version="qg-stub-0",
        rulebook_version=FIXTURE_RULEBOOK_VERSION,
        engine_version=ENGINE_VERSION,
        provider="gemini",
        model_version="gemini-2.5-flash",
        class_counts={"APPROVE": 3},
        class_proportions={"APPROVE": "1.00"},
        tolerance_pp=Decimal("3"),
        edge_case_checklist={"age_18": True},
        profile_count=3,
        content_hash="stub-hash",
        generation_timestamp="2026-01-01T00:00:00Z",
    )
