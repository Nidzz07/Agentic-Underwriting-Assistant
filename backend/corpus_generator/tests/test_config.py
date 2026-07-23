"""C1 ``GenerationConfig`` — frozen value object; single band source (DET-1 / ND-Fold-1)."""
from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.corpus_generator.config import (
    DATA2_EDGE_CASES,
    DEFAULT_TARGET_SPLIT,
    GenerationConfig,
)
from backend.rules_engine.report_schema import Recommendation


def _config(**overrides) -> GenerationConfig:
    base = dict(
        seed=1,
        rulebook_version="1.0.0",
        rulebook_dir="/x",
        engine_version="e1",
        model_id="gemini-2.5-flash",
        attempt_budget=1000,
    )
    base.update(overrides)
    return GenerationConfig(**base)


def test_defaults_are_the_frozen_data_contract():
    cfg = _config()
    assert cfg.target_split == DEFAULT_TARGET_SPLIT
    assert cfg.tolerance_pp == Decimal("3")
    assert cfg.min_profiles == 300
    assert cfg.required_edge_cases == DATA2_EDGE_CASES
    assert len(DATA2_EDGE_CASES) == 8


def test_target_split_keys_are_recommendation_values():
    cfg = _config()
    assert set(cfg.target_split) == {
        Recommendation.APPROVE.value,
        Recommendation.REFER.value,
        Recommendation.DECLINE_RECOMMEND.value,
    }
    # the DECLINE key is the hyphenated -RECOMMEND canonical value
    assert "DECLINE-RECOMMEND" in cfg.target_split


def test_tolerance_property_is_proportion():
    assert _config(tolerance_pp=Decimal("3")).tolerance == Decimal("0.03")


def test_is_frozen_and_forbids_extra():
    cfg = _config()
    with pytest.raises(ValidationError):
        GenerationConfig(  # unknown field rejected
            seed=1, rulebook_version="1", rulebook_dir="/x", engine_version="e",
            model_id="m", attempt_budget=1, nonsense=True,
        )
    with pytest.raises(ValidationError):
        cfg.seed = 2  # immutable


def test_attempt_budget_and_min_profiles_must_be_positive():
    with pytest.raises(ValidationError):
        _config(attempt_budget=0)
    with pytest.raises(ValidationError):
        _config(min_profiles=0)
