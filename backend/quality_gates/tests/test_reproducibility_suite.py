"""REPRO-1 (BR-QG-3 / P2) — CON-BR2/AC-1 reproducibility over the deterministic engine.

Positive: the real engine ×10 yields an identical evaluation_output() projection per
profile (100%). Teeth: an injected non-deterministic-fake engine makes the ×10
identity assertion fail — proving the check has teeth.
"""
from __future__ import annotations

from backend.quality_gates.corpus_loader import CorpusLoader
from backend.quality_gates.reproducibility_suite import ReproducibilityGate

from .conftest import REAL_RULEBOOK_VERSION, make_profile


def test_reproducibility_100_over_deterministic_engine(real_engine, stub_records) -> None:
    gate = ReproducibilityGate(real_engine)
    profiles = CorpusLoader.profiles(stub_records)
    report = gate.run(profiles, REAL_RULEBOOK_VERSION)
    assert report.reproducibility_pct == 100.0 and report.passed is True
    assert report.runs == 10 and report.mismatches == []


def test_reproducibility_has_teeth_against_a_nondeterministic_engine(nondeterministic_engine) -> None:
    gate = ReproducibilityGate(nondeterministic_engine)
    report = gate.run([make_profile("repro-0")], "irrelevant")
    assert report.reproducibility_pct < 100.0 and report.passed is False
    assert report.mismatches  # at least one run differed
