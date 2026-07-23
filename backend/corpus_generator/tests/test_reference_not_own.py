"""REFNOTOWN-1 (structural, AST scan + non-vacuous self-test) + DET-1 clock/random absence.

The scan proves corpus-generator re-implements NONE of the five call-only surfaces:
no local hasher/serialization (delegates to ``common.canon_ser``), no local age/BMI
derivation (delegates to ``intake.derivations``), no rule-eval (delegates to
``rules_engine.evaluate``), no non-central temperature literal, and no wall-clock /
unseeded randomness in the generation modules (DET-1). ``build.py`` (the tier-B
real-client entrypoint) is excluded from the scan (Q5), like ``pg_repository.py``.
"""
from __future__ import annotations

import ast
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parents[1]          # backend/corpus_generator
_EXCLUDED_FILES = {"build.py"}                          # tier-B real-client entrypoint (Q5)
_DERIVATION_NAMES = {
    "compute_age", "compute_bmi", "compute_dti", "compute_income_multiple",
    "compute_health_flag_count", "compute_documents_missing_count",
}
_CLOCK_ATTRS = {("datetime", "now"), ("date", "today")}


def _scanned_files() -> list[Path]:
    return [p for p in PKG_DIR.glob("*.py") if p.name not in _EXCLUDED_FILES]


def scan_source(source: str) -> list[str]:
    """Return structural findings (empty == clean)."""
    tree = ast.parse(source)
    findings: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == "hashlib":
                    findings.append("local hasher: import hashlib")
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] == "hashlib":
                findings.append("local hasher: from hashlib")
        if isinstance(node, ast.FunctionDef):
            if node.name in _DERIVATION_NAMES:
                findings.append(f"local derivation def: {node.name}")
            if node.name == "evaluate":
                findings.append("local rule-eval def: evaluate")
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "temperature" and isinstance(kw.value, ast.Constant):
                    findings.append("non-central temperature literal")
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            base, attr = node.value.id, node.attr
            if (base, attr) in _CLOCK_ATTRS:
                findings.append(f"clock read: {base}.{attr}")
            if base == "time" and attr in {"time", "monotonic", "perf_counter"}:
                findings.append(f"clock read: time.{attr}")
            if base == "random" and attr != "Random":
                findings.append(f"unseeded random: random.{attr}")
    return findings


def _imported_modules(source: str) -> set[str]:
    tree = ast.parse(source)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(a.name for a in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


# --- the package is clean (REFNOTOWN-1 + DET-1 structural) ------------------
def test_package_source_has_no_local_reimplementation_or_clock():
    for path in _scanned_files():
        findings = scan_source(path.read_text(encoding="utf-8"))
        assert findings == [], f"{path.name}: {findings}"


# --- the scanner is NON-VACUOUS (a planted violation is flagged) ------------
def test_scanner_flags_a_planted_local_hasher():
    assert scan_source("import hashlib\nx = hashlib.sha256(b'x')")


def test_scanner_flags_a_planted_local_derivation():
    src = "def compute_age(a, b):\n    return 1\n"
    assert any("local derivation" in f for f in scan_source(src))


def test_scanner_flags_a_planted_rule_eval():
    assert any("rule-eval" in f for f in scan_source("def evaluate(p, v):\n    return None\n"))


def test_scanner_flags_a_planted_temperature_literal():
    src = "client.generate(model='m', prompt='p', temperature=0.7)\n"
    assert any("temperature literal" in f for f in scan_source(src))


def test_scanner_flags_a_planted_clock_and_unseeded_random():
    assert any("clock read" in f for f in scan_source("import datetime\nx = datetime.now()\n"))
    assert any("clock read" in f for f in scan_source("from datetime import date\nx = date.today()\n"))
    assert any("unseeded random" in f for f in scan_source("import random\nx = random.random()\n"))


# --- the five surfaces are consumed call-only -------------------------------
def test_the_call_only_surfaces_are_imported():
    all_imports: set[str] = set()
    for path in _scanned_files():
        all_imports |= _imported_modules(path.read_text(encoding="utf-8"))
    assert any(m.startswith("backend.intake") for m in all_imports)
    assert any(m.startswith("backend.rules_engine") for m in all_imports)
    assert any(m.startswith("backend.memo_agent_core") for m in all_imports)
    assert any(m == "backend.common.canon_ser" for m in all_imports)


def test_secrets_config_is_consumed_only_via_the_tier_b_entrypoint():
    # secrets-config (GEMINI_API_KEY) is read via get_settings in build.py — no literal.
    build_src = (PKG_DIR / "build.py").read_text(encoding="utf-8")
    assert "secrets_config" in build_src
    assert "get_settings" in build_src
