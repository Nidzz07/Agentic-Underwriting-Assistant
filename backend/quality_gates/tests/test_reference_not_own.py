"""REFNOTOWN-1 (BR-QG-7 / P8 / C9) — verification only; no local re-implementation.

A stdlib-``ast`` scan of every ``backend/quality_gates/`` SOURCE module asserts no
local rule-eval / hasher / derivation / second engine (importing the sanctioned
surfaces call-only is fine). Non-vacuous: a planted synthetic re-implementation is
flagged (proving the guard bites). No pytest internals (ND-QG-Fold-3).
"""
from __future__ import annotations

from pathlib import Path

from ._structural import scan_source_for_forbidden

_SRC_DIR = Path(__file__).resolve().parents[1]
_SOURCE_MODULES = sorted(p for p in _SRC_DIR.glob("*.py") if p.name != "__init__.py")


def test_no_source_module_reimplements_a_consumed_surface() -> None:
    assert _SOURCE_MODULES  # guard: the scan is not vacuously empty
    for module in _SOURCE_MODULES:
        findings = scan_source_for_forbidden(module.read_text(encoding="utf-8"))
        assert findings == [], f"{module.name}: {findings}"


def test_scanner_is_non_vacuous() -> None:
    planted = "import hashlib\n\ndef evaluate(self, profile, rulebook_version):\n    return 1\n"
    findings = scan_source_for_forbidden(planted)
    assert any("hashlib" in f for f in findings)
    assert any("evaluate" in f for f in findings)
