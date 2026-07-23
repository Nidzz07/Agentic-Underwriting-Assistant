"""C6 ``DocumentTextGenerator`` — injected LLM seam, central temperature (FR-PROV-4)."""
from __future__ import annotations

import random

from faker import Faker

from backend.corpus_generator.document_text_generator import (
    DocumentTextGenerator,
    _PROSE_TEMPERATURE,
)
from backend.corpus_generator.profile_factory import ProfileFactory
from backend.intake.schema import DocType


def _profile():
    rng = random.Random(1)
    faker = Faker()
    faker.seed_instance(1)
    profile, _ = ProfileFactory(rng, faker, 1).build_approve(0)
    return profile


def test_generates_prose_keyed_by_doctype_value(capturing_llm):
    gen = DocumentTextGenerator(capturing_llm, model="gemini-2.5-flash")
    out = gen.generate_for(_profile())
    assert set(out) == {
        DocType.SALARY_SLIP.value,
        DocType.BANK_STATEMENT.value,
        DocType.MEDICAL_QUESTIONNAIRE.value,
    }
    assert all(isinstance(v, str) and v for v in out.values())


def test_drives_the_injected_seam_at_the_central_temperature(capturing_llm):
    gen = DocumentTextGenerator(capturing_llm, model="gemini-2.5-flash")
    gen.generate_for(_profile())
    assert len(capturing_llm.calls) == 3
    assert all(call["temperature"] == _PROSE_TEMPERATURE for call in capturing_llm.calls)
    assert _PROSE_TEMPERATURE == 0                       # central temperature=0 discipline
    assert all(call["model"] == "gemini-2.5-flash" for call in capturing_llm.calls)


def test_is_offline_no_network_only_the_injected_double(capturing_llm):
    # the ONLY LLM interaction is via the injected capturing double (no key, no network)
    DocumentTextGenerator(capturing_llm, model="m").generate_for(_profile())
    assert len(capturing_llm.calls) == 3
