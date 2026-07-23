"""BLOCKING-1 (BR-QG-9 / CollectedBlockingTestConvention / C9) — genuine blocking form.

A stdlib-``ast`` static meta-check that each gate test module's ``test_*`` functions
are collected and carry NO ``skip``/``xfail`` marker (and no module-level
``pytestmark``) — proving the gates are build-failing, not silently skipped. No
pytest internals imported (ND-QG-Fold-3). Non-vacuous: a planted skip is flagged.
"""
from __future__ import annotations

from pathlib import Path

from ._structural import collected_test_names, scan_test_for_skips

_TEST_DIR = Path(__file__).resolve().parent
_GATE_TEST_MODULES = [
    "test_bias_swap_suite.py",
    "test_reproducibility_suite.py",
    "test_rule_coverage_report.py",
    "test_coverage_gate.py",
]


def test_gate_tests_are_collected_and_carry_no_skip_or_xfail() -> None:
    for name in _GATE_TEST_MODULES:
        source = (_TEST_DIR / name).read_text(encoding="utf-8")
        assert collected_test_names(source), f"{name}: no collected test_* functions"
        assert scan_test_for_skips(source) == [], f"{name}: has a skip/xfail marker"


def test_skip_meta_check_is_non_vacuous() -> None:
    planted_decorator = "import pytest\n\n@pytest.mark.skip\ndef test_x():\n    pass\n"
    assert scan_test_for_skips(planted_decorator)
    planted_module = "import pytest\npytestmark = pytest.mark.xfail\n\ndef test_y():\n    pass\n"
    assert scan_test_for_skips(planted_module)
