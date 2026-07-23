"""C3 ``LabelingOracle`` — the engine is the label authority (LABEL-1 / CON-BR2)."""
from __future__ import annotations

import random

from faker import Faker

from backend.corpus_generator.labeling_oracle import LabelingOracle
from backend.corpus_generator.profile_factory import ProfileFactory
from backend.corpus_generator.tests.conftest import ENGINE_VERSION, RULEBOOK_DIR, RULEBOOK_VERSION
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader
from backend.rules_engine.report_schema import Recommendation


def _factory(seed: int = 3) -> ProfileFactory:
    rng = random.Random(seed)
    faker = Faker()
    faker.seed_instance(seed)
    return ProfileFactory(rng, faker, seed)


def test_label_equals_engine_recommendation(oracle):
    factory = _factory()
    profile, _ = factory.build_approve(0)
    # recomputing via a freshly constructed engine equals the oracle's label
    engine = RulesEngine(RulebookLoader(RULEBOOK_DIR), engine_version=ENGINE_VERSION)
    expected = engine.evaluate(profile, RULEBOOK_VERSION).recommendation
    assert oracle.label(profile) == expected


def test_oracle_exposes_the_single_rulebook_version(oracle):
    assert oracle.rulebook_version == RULEBOOK_VERSION


def test_from_config_constructs_call_only():
    oracle = LabelingOracle.from_config(
        rulebook_dir=RULEBOOK_DIR,
        rulebook_version=RULEBOOK_VERSION,
        engine_version="eng-x",
    )
    profile, _ = _factory().build_decline(0)
    assert oracle.label(profile) is Recommendation.DECLINE_RECOMMEND


def test_label_returns_a_recommendation_enum(oracle):
    profile, _ = _factory().build_refer(0)
    assert isinstance(oracle.label(profile), Recommendation)
