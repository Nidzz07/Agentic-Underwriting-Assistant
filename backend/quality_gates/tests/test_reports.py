"""EVIDENCE-1 (BR-QG-8 / P9) — evidence-report determinism + human-readability.

Same inputs -> field-equal report (Pydantic equality); the provenance stamp is NOT
a model field, so it can never make two runs differ. Readable JSON; on-disk emit
(CG-QG-Fold-3 — the auditor artifact IS realized here, exercised via tmp_path).
"""
from __future__ import annotations

import json

from backend.quality_gates.reports import (
    BiasSwapReport,
    CoverageGateReport,
    ReproducibilityReport,
    RuleCoverageReport,
    SwapRecord,
)


def _report() -> BiasSwapReport:
    return BiasSwapReport(
        passed=True,
        profiles_tested=1,
        swaps=[
            SwapRecord(
                application_id="stub-0",
                swapped_fields=["full_name", "gender", "city"],
                baseline_recommendation="APPROVE",
                swapped_recommendation="APPROVE",
            )
        ],
        delta_count=0,
    )


def test_report_is_field_equal_across_two_runs() -> None:
    # Determinism: identical inputs -> equal models (no provenance field to differ).
    assert _report() == _report()


def test_readable_dict_carries_no_provenance() -> None:
    payload = _report().to_readable_dict()
    assert "generated_at" not in payload
    assert payload["passed"] is True and payload["delta_count"] == 0


def test_to_json_is_stable_and_provenance_is_an_envelope_only() -> None:
    plain = _report().to_json()
    assert plain == _report().to_json()  # byte-stable
    assert "generated_at" not in json.loads(plain)
    stamped = json.loads(_report().to_json(generated_at="2026-01-01T00:00:00Z"))
    assert stamped["generated_at"] == "2026-01-01T00:00:00Z"  # envelope, not a model field


def test_emit_writes_readable_json_artifact(tmp_path) -> None:
    path = _report().emit(tmp_path, generated_at="2026-01-01T00:00:00Z")
    assert path.name == "BiasSwapReport.json" and path.exists()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["passed"] is True and loaded["generated_at"].startswith("2026")


def test_all_four_report_shapes_construct_and_serialize() -> None:
    reports = [
        _report(),
        ReproducibilityReport(passed=True, profiles_tested=1, runs=10, reproducibility_pct=100.0),
        RuleCoverageReport(
            passed=True, rulebook_version="qg-test-0.0.1", total_rules=3,
            covered_rule_ids=["T-DTI-1"], uncovered_rule_ids=[], coverage_pct=100.0,
        ),
        CoverageGateReport(passed=True, wiring_present=True, fail_under_configured=90),
    ]
    for report in reports:
        assert isinstance(report.to_json(), str) and report.to_readable_dict()["passed"] is True
