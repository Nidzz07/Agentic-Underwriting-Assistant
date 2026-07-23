"""RULECOV-1 (BR-QG-4 / P3 + P3a) — QA-3 rule coverage over the controlled fixture.

Positive: a stub that exercises every rule of the P3a controlled rulebook to a
definite PASS/FAIL -> coverage 100%. Teeth: a stub leaving bmi_derived absent
(height/weight None) -> T-BMI-UNCOVERED-1 reaches NOT_EVALUATED -> uncovered ->
the gate fails. The fixture rulebook is loaded via the REAL RulebookLoader (which
validates it — NFR-QG-Fold-2; no bespoke validator), distinct from production 1.0.0.
"""
from __future__ import annotations

from backend.quality_gates.rule_coverage_report import RuleCoverageGate

from .conftest import FIXTURE_RULEBOOK_VERSION, make_profile


def test_full_coverage_over_a_complete_stub(fixture_engine, fixture_loader) -> None:
    gate = RuleCoverageGate(fixture_engine, fixture_loader)
    # bmi present -> all three fixture rules reach a definite PASS/FAIL.
    profiles = [make_profile("cov-0", bmi="22.9", height="175", weight="70")]
    report = gate.run(profiles, FIXTURE_RULEBOOK_VERSION)
    assert report.coverage_pct == 100.0 and report.passed is True
    assert report.uncovered_rule_ids == [] and report.total_rules == 3


def test_uncovered_rule_detected_with_teeth(fixture_engine, fixture_loader) -> None:
    gate = RuleCoverageGate(fixture_engine, fixture_loader)
    # bmi absent -> T-BMI-UNCOVERED-1 is NOT_EVALUATED for every record -> uncovered.
    profiles = [make_profile("cov-1", bmi=None, height=None, weight=None)]
    report = gate.run(profiles, FIXTURE_RULEBOOK_VERSION)
    assert report.passed is False and report.coverage_pct < 100.0
    assert report.uncovered_rule_ids == ["T-BMI-UNCOVERED-1"]


def test_fixture_rulebook_is_loaded_and_validated_by_the_real_loader(fixture_loader) -> None:
    # Reuse of the real loader IS the validation (NFR-QG-Fold-2) — a legit input.
    rulebook = fixture_loader.load_rulebook(FIXTURE_RULEBOOK_VERSION)
    assert [r.rule_id for r in rulebook.rules] == ["T-DTI-1", "T-AGE-1", "T-BMI-UNCOVERED-1"]
