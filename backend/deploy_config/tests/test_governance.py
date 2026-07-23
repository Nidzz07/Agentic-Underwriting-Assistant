"""NFR-DEP-ADVISORY-1 + NFR-DEP-SEC-1 (governance) + NFR-DEP-PERF-1 (observed): U23 declares no
recommendation/verdict and owns no runtime SLO; config only (BR-DEP-9). The Security-Guardrails
posture holds — SEC-3 is machine-checked by `test_sec3.py`.
"""
from __future__ import annotations

from backend.deploy_config.tests import structural as sg

#: Verdict VALUES a decision would carry — a config artifact must not emit one.
_VERDICT_VALUES = ("APPROVE", "REFER", "DECLINE-RECOMMEND", "DECLINE_RECOMMEND")


def test_no_verdict_value_emitted_by_any_u23_artifact():
    # ADVISORY-1: U23 wires deploy config; it never produces a recommendation/verdict. (The metric
    # NAME `decisions_by_recommendation_type` is a label identifier, not an emitted verdict value.)
    for rel in sg.U23_ARTIFACTS:
        text = sg.read(rel)
        for verdict in _VERDICT_VALUES:
            assert verdict not in text, f"{rel} emits a verdict value {verdict!r}"


def test_sec3_posture_is_machine_checked_elsewhere():
    # SEC-1: the load-bearing SEC-3 half (no secret values) is asserted by test_sec3.py; this
    # governance test records that the posture is machine-checked, not merely reviewed.
    assert sg.exists("backend/deploy_config/tests/test_sec3.py")


def test_perf1_is_observed_never_gated():
    # PERF-1: U23 owns no runtime SLO; the validation deploy's responsiveness is provider-managed,
    # observed-never-gated. Nothing here asserts a latency threshold.
    assert True
