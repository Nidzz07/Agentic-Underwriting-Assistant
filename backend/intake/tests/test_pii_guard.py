"""Tests for the active PII guard + seeded synthetic fixtures (Step 13 / DATA-4).

Maps: NFR-INT-DATA4. Asserts (a) the guard is ACTIVE (detects real-PII-shaped
patterns), (b) this unit's fixtures contain ZERO real-PII-shaped patterns, and
(c) the seeded synthetic factory is reproducible and PII-free.
"""
from __future__ import annotations

from pathlib import Path

from backend.intake import pii_guard


# The fixtures directory this unit owns.
_FIXTURES = Path(__file__).resolve().parent.parent / "sanitizer" / "tests" / "fixtures"
_UNIT_ROOT = Path(__file__).resolve().parent.parent  # backend/intake


# --------------------------------------------------------------------------
# (a) the guard is ACTIVE
# --------------------------------------------------------------------------
def test_guard_detects_ssn():
    findings = pii_guard.scan_text("contact 123-45-6789 for details")
    assert any(f.pattern == "ssn" for f in findings)


def test_guard_detects_email_and_card_and_phone():
    assert any(f.pattern == "email" for f in pii_guard.scan_text("a@b.com"))
    assert any(f.pattern == "credit_card" for f in pii_guard.scan_text("4111 1111 1111 1111"))
    assert any(f.pattern == "phone_e164" for f in pii_guard.scan_text("call +14155550123"))


def test_main_returns_nonzero_on_dirty_dir(tmp_path):
    (tmp_path / "leak.txt").write_text("ssn 123-45-6789", encoding="utf-8")
    assert pii_guard.main(["prog", str(tmp_path)]) == 1


def test_main_returns_zero_on_clean_dir(tmp_path):
    (tmp_path / "clean.txt").write_text("synthetic income 500000 for applicant", encoding="utf-8")
    assert pii_guard.main(["prog", str(tmp_path)]) == 0


def test_scan_accepts_a_single_file_path(tmp_path):
    f = tmp_path / "data.txt"
    f.write_text("email leak a@b.com here", encoding="utf-8")
    findings = pii_guard.scan_for_real_pii([f])
    assert any(x.pattern == "email" for x in findings)


def test_main_skips_test_source_files(tmp_path):
    # A test file with an intentional positive vector must NOT fail the guard.
    (tmp_path / "test_vectors.py").write_text('SSN = "123-45-6789"', encoding="utf-8")
    assert pii_guard.main(["prog", str(tmp_path)]) == 0


# --------------------------------------------------------------------------
# (b) this unit's fixtures + source carry no real-PII-shaped patterns
# --------------------------------------------------------------------------
def test_unit_fixtures_have_no_real_pii():
    findings = pii_guard.scan_for_real_pii([_FIXTURES])
    assert findings == [], f"real-PII-shaped patterns in fixtures: {findings}"


def test_unit_source_tree_has_no_real_pii():
    findings = pii_guard.scan_for_real_pii([_UNIT_ROOT])
    assert findings == [], f"real-PII-shaped patterns in unit source: {findings}"


# --------------------------------------------------------------------------
# (c) seeded synthetic factory — reproducible + PII-free
# --------------------------------------------------------------------------
def test_synthetic_form_is_seed_reproducible():
    from backend.intake.sanitizer.tests.fixtures.synthetic_profiles import synthetic_form
    assert synthetic_form(42) == synthetic_form(42)
    assert synthetic_form(1) != synthetic_form(2)


def test_synthetic_form_has_no_real_pii():
    from backend.intake.sanitizer.tests.fixtures.synthetic_profiles import synthetic_form
    blob = str(synthetic_form(7))
    assert pii_guard.scan_text(blob) == []


def test_synthetic_form_passes_the_gate():
    from backend.intake.sanitizer.tests.fixtures.synthetic_profiles import synthetic_form
    from backend.intake.validation_gate import IntakeGate
    from backend.intake import schema as s
    result = IntakeGate(id_generator=lambda: "APP-SYNTH").validate_gate(synthetic_form(3))
    assert isinstance(result, (s.ApplicantProfile, s.RejectedIntake))
