"""COVWIRE-1 + COVEVID-1 (BR-QG-5 / P4 + P5) — two DISTINCT producers, never conflated.

COVWIRE-1: read the REAL pyproject.toml -> --cov-fail-under present and >=90 -> passed;
teeth: a temp pyproject omitting it / setting 85 -> passed False. COVEVID-1: read a
fixture coverage-data artifact -> measured_pct extracted (informational); it does NOT
read pyproject and does NOT set a coverage verdict (ND-QG-Fold-1 / QG-Fold-3).
"""
from __future__ import annotations

from pathlib import Path

from backend.quality_gates.coverage_gate import CoverageEvidenceGate, CoverageWiringGate

from .conftest import FIXTURE_COVERAGE_JSON

_REPO_PYPROJECT = Path(__file__).resolve().parents[3] / "pyproject.toml"

_PYPROJECT_TEMPLATE = """\
[tool.pytest.ini_options]
addopts = [
{lines}
]
"""


def _write_pyproject(tmp_path: Path, addopts: list[str]) -> Path:
    lines = "\n".join(f'    "{opt}",' for opt in addopts)
    path = tmp_path / "pyproject.toml"
    path.write_text(_PYPROJECT_TEMPLATE.format(lines=lines), encoding="utf-8")
    return path


def test_covwire_passes_on_the_real_pyproject() -> None:
    report = CoverageWiringGate(_REPO_PYPROJECT).run()
    assert report.wiring_present is True
    assert report.fail_under_configured == 90
    assert report.passed is True


def test_covwire_fails_when_wiring_absent(tmp_path) -> None:
    path = _write_pyproject(tmp_path, ["--cov=backend/quality_gates", "--strict-markers"])
    report = CoverageWiringGate(path).run()
    assert report.wiring_present is False and report.passed is False


def test_covwire_fails_when_threshold_below_90(tmp_path) -> None:
    path = _write_pyproject(tmp_path, ["--cov=backend/quality_gates", "--cov-fail-under=85"])
    report = CoverageWiringGate(path).run()
    assert report.wiring_present is True
    assert report.fail_under_configured == 85 and report.passed is False


def test_covwire_treats_a_valueless_flag_as_unwired(tmp_path) -> None:
    # "--cov-fail-under" with no "=value" -> not a valid wiring -> absent.
    path = _write_pyproject(tmp_path, ["--cov=backend/quality_gates", "--cov-fail-under"])
    report = CoverageWiringGate(path).run()
    assert report.wiring_present is False and report.passed is False


def test_covevid_extracts_measured_pct_as_informational_evidence() -> None:
    report = CoverageEvidenceGate(FIXTURE_COVERAGE_JSON).run()
    assert report.measured_pct is not None and report.measured_pct > 90.0
    # Distinct producer: C7 does NOT set the wiring verdict (never conflated with C6).
    assert report.wiring_present is False
    assert report.fail_under_configured is None
