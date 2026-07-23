"""C2 ``ProfileFactory`` — DET-1, PROFILE-1, SEGREGATION-1."""
from __future__ import annotations

import random

import pytest
from faker import Faker

from backend.common.canon_ser import canon_ser
from backend.corpus_generator.profile_factory import (
    INTENDED_CLASS_FOR_EDGE,
    ProfileFactory,
    _AS_OF_ANCHOR,
)
from backend.intake.derivations import compute_age, compute_bmi
from backend.intake.schema import ApplicantProfile, Demographics, Gender
from backend.rules_engine.report_schema import Recommendation


def _factory(seed: int = 42) -> ProfileFactory:
    rng = random.Random(seed)
    faker = Faker()
    faker.seed_instance(seed)
    return ProfileFactory(rng, faker, seed)


# --- PROFILE-1 -------------------------------------------------------------
def test_every_recipe_yields_a_valid_profile_with_single_sourced_derivations():
    factory = _factory()
    builders = [
        factory.build_approve(0),
        factory.build_refer(1),
        factory.build_decline(2),
    ] + [factory.build_edge(10 + i, edge) for i, edge in enumerate(INTENDED_CLASS_FOR_EDGE)]

    for profile, _tags in builders:
        assert isinstance(profile, ApplicantProfile)          # round-trips (constructed frozen)
        # derivation equality — single-sourced via intake.derivations (no local re-impl)
        assert profile.age_years_derived == compute_age(profile.date_of_birth, profile.as_of_date)
        if profile.height_cm is not None and profile.weight_kg is not None:
            assert profile.bmi_derived == compute_bmi(profile.height_cm, profile.weight_kg)
        assert profile.as_of_date == _AS_OF_ANCHOR            # fixed clock-free anchor (DET-1)


def test_application_id_is_the_deterministic_synthetic_id():
    factory = _factory(seed=99)
    profile, _ = factory.build_approve(7)
    assert profile.application_id == "corpus-99-7"            # Q2 / BR-CORP-9


def test_exact_boundary_edge_cases_are_boundary_precise():
    factory = _factory()
    bmi25, _ = factory.build_edge(0, "bmi_25")
    bmi30, _ = factory.build_edge(1, "bmi_30")
    age18, _ = factory.build_edge(2, "age_18")
    age65, _ = factory.build_edge(3, "age_65")
    from decimal import Decimal

    assert bmi25.bmi_derived == Decimal("25.00")
    assert bmi30.bmi_derived == Decimal("30.00")
    assert age18.age_years_derived == 18
    assert age65.age_years_derived == 65


def test_unknown_edge_is_rejected():
    with pytest.raises(ValueError):
        _factory().build_edge(0, "not_a_real_edge")


# --- DET-1 (factory level) -------------------------------------------------
def test_same_seed_gives_byte_identical_structured_profiles():
    p1, _ = _factory(seed=5).build_approve(0)
    p2, _ = _factory(seed=5).build_approve(0)
    assert canon_ser(p1.model_dump(mode="python")) == canon_ser(p2.model_dump(mode="python"))


# --- SEGREGATION-1 ---------------------------------------------------------
def test_demographic_swap_leaves_the_engine_label_unchanged(oracle):
    # NOTE: this is corpus-generator's OWN layered-respect check (defense-in-depth),
    # NOT quality-gates' bias-swap suite (the CON-BR1 verification owner, delta=0
    # across the corpus). No swap pairs / bias-swap suite are authored here.
    factory = _factory()
    profile, _ = factory.build_approve(0)
    other_demographics = Demographics(full_name="Someone Else", gender=Gender.MALE, city="Chennai")
    swapped = profile.model_copy(update={"demographics": other_demographics})

    assert profile.demographics != swapped.demographics       # differ ONLY in Demographics
    assert oracle.label(profile) == oracle.label(swapped)     # same engine recommendation


def test_edge_recipes_land_on_their_intended_engine_class(oracle):
    factory = _factory()
    for edge, intended in INTENDED_CLASS_FOR_EDGE.items():
        profile, tags = factory.build_edge(0, edge)
        assert tags == [edge]
        assert oracle.label(profile) is intended              # recipe matches engine authority


def test_bulk_recipes_land_on_their_class(oracle):
    factory = _factory()
    assert oracle.label(factory.build_approve(0)[0]) is Recommendation.APPROVE
    assert oracle.label(factory.build_refer(1)[0]) is Recommendation.REFER
    assert oracle.label(factory.build_decline(2)[0]) is Recommendation.DECLINE_RECOMMEND
