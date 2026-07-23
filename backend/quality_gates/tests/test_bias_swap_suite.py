"""BIAS-1 + PROXY-1 (BR-QG-1/2 / P1) — CON-BR1 single verification authority.

Positive: over the real engine, swapping {full_name, gender, city} leaves the
recommendation unchanged (delta=0). Teeth: an injected biased-fake engine (keyed on
gender) makes the suite detect delta>0 and fail — proving the check is not vacuous.
PROXY-1: occupation/income changes attribute to the sanctioned rule only; a
demographic-only swap changes nothing; pincode is N/A (absent from the schema).
"""
from __future__ import annotations

from backend.quality_gates.bias_swap_suite import BiasSwapGate, swapped_demographics
from backend.quality_gates.corpus_loader import CorpusLoader

from .conftest import REAL_RULEBOOK_VERSION, make_profile


def test_bias_swap_delta_zero_over_stub(real_engine, stub_records) -> None:
    gate = BiasSwapGate(real_engine)
    profiles = CorpusLoader.profiles(stub_records)
    report = gate.run(profiles, REAL_RULEBOOK_VERSION)
    assert report.delta_count == 0 and report.passed is True
    assert report.profiles_tested == len(profiles)


def test_bias_swap_has_teeth_against_a_biased_engine(biased_engine, stub_records) -> None:
    # An engine whose recommendation depends on gender -> the suite MUST catch it.
    gate = BiasSwapGate(biased_engine)
    profiles = CorpusLoader.profiles(stub_records)
    report = gate.run(profiles, "irrelevant")
    assert report.delta_count > 0 and report.passed is False


def test_swapped_demographics_changes_all_three_identifiers() -> None:
    original = make_profile().demographics
    swapped = swapped_demographics(original)
    assert swapped.full_name != original.full_name
    assert swapped.gender != original.gender
    assert swapped.city != original.city


def test_proxy_demographic_only_swap_changes_no_rule(real_engine) -> None:
    base = make_profile("proxy-0")
    swapped = base.model_copy(update={"demographics": swapped_demographics(base.demographics)})
    gate = BiasSwapGate(real_engine)
    assert gate.changed_rules(base, swapped, REAL_RULEBOOK_VERSION) == []


def test_proxy_occupation_change_attributes_to_the_sanctioned_rule(real_engine) -> None:
    base = make_profile("proxy-1", occupation="engineer")           # low-risk -> pass
    varied = make_profile("proxy-1", occupation="pilot")            # outside set -> fail
    gate = BiasSwapGate(real_engine)
    assert gate.changed_rules(base, varied, REAL_RULEBOOK_VERSION) == ["OCC-LOWRISK-1"]


def test_pincode_is_not_a_schema_field() -> None:
    # Q5-A / QG-Fold-5 — pincode documented N/A, not silently skipped.
    profile = make_profile()
    assert not hasattr(profile, "pincode")
    assert not hasattr(profile.demographics, "pincode")
