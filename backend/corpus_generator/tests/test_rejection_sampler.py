"""C4 ``RejectionSampler`` — BOUND-1 (happy + pre-flight pigeonhole + runtime exhaustion)."""
from __future__ import annotations

import random

import pytest
from faker import Faker

from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.exceptions import BudgetExhaustedError
from backend.corpus_generator.profile_factory import ProfileFactory
from backend.corpus_generator.rejection_sampler import RejectionSampler, _target_counts
from backend.corpus_generator.skew_audit import band_ok, edges_ok
from backend.corpus_generator.tests.conftest import ENGINE_VERSION, RULEBOOK_DIR, RULEBOOK_VERSION
from backend.rules_engine.report_schema import Recommendation


def _config(**overrides) -> GenerationConfig:
    base = dict(
        seed=42,
        rulebook_version=RULEBOOK_VERSION,
        rulebook_dir=RULEBOOK_DIR,
        engine_version=ENGINE_VERSION,
        model_id="gemini-2.5-flash",
        attempt_budget=10_000,
        min_profiles=30,
    )
    base.update(overrides)
    return GenerationConfig(**base)


def _real_factory(seed: int, oracle):
    rng = random.Random(seed)
    faker = Faker()
    faker.seed_instance(seed)
    return ProfileFactory(rng, faker, seed)


# --- happy path ------------------------------------------------------------
def test_happy_path_meets_quotas_band_and_edges(oracle):
    config = _config()
    factory = _real_factory(config.seed, oracle)
    kept = RejectionSampler().sample(config, factory, oracle)

    counts = {cls: 0 for cls in config.target_split}
    present_edges = set()
    for item in kept:
        counts[item.label.value] += 1
        present_edges.update(item.edge_case_tags)

    targets = _target_counts(config)
    assert all(counts[cls] >= targets[cls] for cls in targets)   # quotas met
    assert band_ok(counts, config)                               # within the ±3pp band
    assert edges_ok(present_edges, config)                       # every DATA-2 edge present
    # stored label is the engine's authority, never the intended target blindly
    assert all(isinstance(item.label, Recommendation) for item in kept)


# --- pre-flight pigeonhole guard (seed-independent) ------------------------
@pytest.mark.parametrize("seed", [0, 1, 7, 42, 123456])
def test_preflight_pigeonhole_raises_seed_independently(seed, oracle):
    # attempt_budget=1 but a class band lower-edge count is >= 2 -> quota > budget
    config = _config(seed=seed, attempt_budget=1, min_profiles=10)
    factory = _real_factory(config.seed, oracle)
    with pytest.raises(BudgetExhaustedError):
        RejectionSampler().sample(config, factory, oracle)
    # the guard also raises directly, before any sampling
    with pytest.raises(BudgetExhaustedError):
        RejectionSampler().preflight(config)


# --- runtime exhaustion guard ----------------------------------------------
class _AlwaysApproveOracle:
    def label(self, profile):
        return Recommendation.APPROVE


class _StubFactory:
    """A factory whose candidates the (stub) oracle always labels APPROVE."""

    def build_edge(self, index, edge):  # pragma: no cover - not used (edges empty)
        return object(), [edge]

    def build_approve(self, index):
        return object(), []

    def build_refer(self, index):
        return object(), []

    def build_decline(self, index):
        return object(), []


def test_runtime_exhaustion_raises_when_a_class_is_unreachable():
    # feasible on paper (small lower-edges <= budget) but REFER/DECLINE never produced
    config = _config(min_profiles=5, attempt_budget=50, required_edge_cases=())
    with pytest.raises(BudgetExhaustedError):
        RejectionSampler().sample(config, _StubFactory(), _AlwaysApproveOracle())


def test_runtime_guard_is_bounded_not_a_hang():
    # a very small budget makes the bounded loop terminate promptly with a raise
    config = _config(min_profiles=5, attempt_budget=3, required_edge_cases=())
    with pytest.raises(BudgetExhaustedError):
        RejectionSampler().sample(config, _StubFactory(), _AlwaysApproveOracle())
