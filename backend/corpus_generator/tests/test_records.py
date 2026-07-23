"""Frozen output records — ``CorpusRecord`` + ``CorpusManifest`` (FD §4/§5)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.corpus_generator.records import CorpusManifest, CorpusRecord
from backend.intake.schema import (
    ApplicantProfile,
    Demographics,
    DocumentManifest,
    Gender,
)
from backend.rules_engine.report_schema import Recommendation


def _profile() -> ApplicantProfile:
    return ApplicantProfile(
        application_id="corpus-1-0",
        date_of_birth=date(1986, 1, 1),
        as_of_date=date(2026, 1, 1),
        age_years_derived=40,
        verifiable_income_annual=Decimal("200000"),
        requested_cover_amount=Decimal("200000"),
        demographics=Demographics(full_name="Jane Doe", gender=Gender.FEMALE, city="Pune"),
        documents=DocumentManifest(expected_count=0, satisfied_count=0, entries=[]),
    )


def test_corpus_record_holds_profile_label_and_provenance():
    record = CorpusRecord(
        profile=_profile(),
        documents_text={"salary_slip": "prose"},
        label=Recommendation.APPROVE,
        intended_class=Recommendation.APPROVE,
        edge_case_tags=["age_18"],
    )
    assert record.label is Recommendation.APPROVE
    assert record.edge_case_tags == ["age_18"]
    assert record.profile.application_id == "corpus-1-0"


def test_records_are_frozen_and_forbid_extra():
    record = CorpusRecord(profile=_profile(), label=Recommendation.REFER, intended_class=Recommendation.REFER)
    with pytest.raises(ValidationError):
        record.label = Recommendation.APPROVE
    with pytest.raises(ValidationError):
        CorpusRecord(profile=_profile(), label=Recommendation.REFER, intended_class=Recommendation.REFER, junk=1)


def test_manifest_shape():
    manifest = CorpusManifest(
        seed=42,
        corpus_version="1.0.0",
        rulebook_version="1.0.0",
        engine_version="e1",
        provider="gemini",
        model_version="gemini-2.5-flash",
        class_counts={"APPROVE": 120, "REFER": 105, "DECLINE-RECOMMEND": 75},
        class_proportions={"APPROVE": "0.4", "REFER": "0.35", "DECLINE-RECOMMEND": "0.25"},
        tolerance_pp=Decimal("3"),
        edge_case_checklist={"age_18": True},
        profile_count=300,
        content_hash="abc",
        generation_timestamp="2026-01-01T00:00:00Z",
    )
    assert manifest.provider == "gemini"
    assert manifest.profile_count == 300
    with pytest.raises(ValidationError):
        manifest.seed = 0  # frozen
