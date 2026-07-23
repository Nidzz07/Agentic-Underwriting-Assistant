"""NFR-CASE-NOMETRIC-1 (P-CASE-13) — no new metric. BR-CASE-14.

Mirrors `llm-judge`'s NOMETRIC-1 exactly: a PROVENANCE scan over U24's own tree (the claim
nothing else makes) plus a CORROBORATING read-only property check.

⚑ NEITHER observability's NOR deploy-config's SUITE IS RE-RUN — both artifacts are read read-only.
"""
from __future__ import annotations

from backend.case_lifecycle.tests import structural as sg
from backend.observability.metrics import METRIC_DEFINITIONS   # READ-ONLY import


def test_no_u24_module_declares_a_metric_definition():
    scanned = 0
    for path in sg.production_py_files():
        tree = sg.parse(path)
        called, assigned = sg.called_names(tree), sg.assigned_names(tree)
        for token in sg.METRIC_TOKENS:
            assert token not in called, (path.name, token)
            assert token not in assigned, (path.name, token)
        scanned += 1
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)


def test_no_u24_production_module_imports_observability():
    for path in sg.production_py_files():
        assert "backend.observability" not in path.read_text(encoding="utf-8"), path.name


def test_detector_a_synthetic_metric_definition_is_flagged():
    assert "MetricDefinition" in sg.called_names(
        sg.parse_source('X = MetricDefinition(name="case_runs_total")\n')
    )


def test_detector_a_synthetic_metric_constant_is_flagged():
    assert "METRIC_DEFINITIONS" in sg.assigned_names(sg.parse_source("METRIC_DEFINITIONS = ()\n"))


def test_observabilitys_frozen_five_metrics_are_unchanged():
    assert len(METRIC_DEFINITIONS) == 5
    assert len({m.name for m in METRIC_DEFINITIONS}) == 5


def test_the_dashboard_still_declares_exactly_five_panels():
    panels = sg.load_dashboard()["panels"]
    assert len(panels) == 5
    assert not any("panels" in p for p in panels)      # no row-nesting under-count
    assert {p["targets"][0]["expr"] for p in panels} == {m.name for m in METRIC_DEFINITIONS}
