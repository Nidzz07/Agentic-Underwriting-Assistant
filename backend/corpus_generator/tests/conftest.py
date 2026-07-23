"""Seeded fixtures, a capturing LLM double, and the test-scoped config (Fold NFR-1).

No network, no key, no live Gemini call anywhere — the ``CapturingLLMClient`` is the
only LLM seam the suite touches (BR-CORP-8 / PII-1). The real deterministic engine
oracle is built call-only from the repo rulebook directory.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.labeling_oracle import LabelingOracle

RULEBOOK_DIR = str(Path(__file__).resolve().parents[2] / "rules_engine" / "rulebook")
RULEBOOK_VERSION = "1.0.0"
ENGINE_VERSION = "corpus-test-engine-1"
MODEL_ID = "gemini-2.5-flash"


class CapturingLLMClient:
    """An offline capturing double for the injected ``LLMClient`` seam.

    Records every outgoing request and returns deterministic synthetic prose — no
    network, no key. Faithful to the seam shape ``generate(*, model, prompt,
    temperature) -> str``.
    """

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate(self, *, model: str, prompt: str, temperature: float) -> str:
        self.calls.append({"model": model, "prompt": prompt, "temperature": temperature})
        return f"[synthetic prose | model={model} | temp={temperature}]"


@pytest.fixture
def capturing_llm() -> CapturingLLMClient:
    return CapturingLLMClient()


@pytest.fixture
def real_config() -> GenerationConfig:
    """The real tier-B-shaped config (300+, ~40/35/25, all 8 DATA-2 edges)."""
    return GenerationConfig(
        seed=42,
        rulebook_version=RULEBOOK_VERSION,
        rulebook_dir=RULEBOOK_DIR,
        engine_version=ENGINE_VERSION,
        model_id=MODEL_ID,
        attempt_budget=100_000,
        min_profiles=300,
    )


@pytest.fixture
def test_scoped_config() -> GenerationConfig:
    """Fold NFR-1: a tiny-N smoke config — small ``min_profiles``, ``attempt_budget``
    generously above the pigeonhole bound, a wide tolerance + edge-subset the tiny N
    can meet. It NEVER asserts the real 40/35/25 band or the full DATA-2 checklist;
    ``min_profiles=300`` governs the real tier-B corpus only."""
    return GenerationConfig(
        seed=7,
        rulebook_version=RULEBOOK_VERSION,
        rulebook_dir=RULEBOOK_DIR,
        engine_version=ENGINE_VERSION,
        model_id=MODEL_ID,
        attempt_budget=1_000,
        min_profiles=9,
        tolerance_pp=Decimal("50"),  # wide — the smoke does not assert the real band
        required_edge_cases=("age_18", "self_employed_irregular"),
    )


@pytest.fixture
def oracle(real_config: GenerationConfig) -> LabelingOracle:
    return LabelingOracle.from_config(
        rulebook_dir=real_config.rulebook_dir,
        rulebook_version=real_config.rulebook_version,
        engine_version=real_config.engine_version,
    )
