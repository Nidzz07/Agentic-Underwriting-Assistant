"""NFR-JUDGE-NOMETRIC-1 (P-JUDGE-4) — LOAD-BEARING (full-highest). BR-JUDGE-11 / Q6-A / Q3-A.

⚑ TWO mechanisms, re-scoped by ND-Fold-3 to eliminate a real overlap:

  (a) PRIMARY — the PROVENANCE scan. No U22 module declares a metric name or a
      ``MetricDefinition``. **Nothing else in the build asserts this**; it is genuinely
      U22's claim to make.
  (b) CORROBORATING — the read-only property assertion, which pins the baseline U22 claims
      not to have moved and thereby makes (a) non-vacuous.

Why (b) is only corroborating: ``deploy-config``'s OWN FROZEN
``tests/test_scope.py::test_grafana_dashboard_panels_match_observabilitys_frozen_five_no_drift``
already asserts the dashboard<->metrics no-drift property in BOTH directions. A U22 check
that merely re-asserted it would near-duplicate a frozen test — and U22 cannot rely on that
test executing anyway, since the standing instruction forbids re-running either unit's suite.

⚑ PROPERTY assertions, NOT a content-hash pin (Q3-A): a hash would make ANY future
legitimate edit by U21's or U23's owners break U22's suite, and U22 would be asserting a
constant it invented — converting *"U22 changed nothing"* into *"nobody may ever change
these files"*, a stronger claim than the last unit in the build is entitled to make.

⚑ Both frozen artifacts are read READ-ONLY. NEITHER UNIT'S SUITE IS RE-RUN.
"""
from __future__ import annotations

from backend.llm_judge.tests import structural as sg
from backend.observability.metrics import METRIC_DEFINITIONS  # READ-ONLY import

# --- (a) PRIMARY: the provenance scan ----------------------------------------------------


def test_no_u22_module_declares_a_metric_definition():
    scanned = 0
    for path in sg.production_py_files():
        tree = sg.parse(path)
        called = sg.called_names(tree)
        assigned = sg.assigned_names(tree)
        for token in sg.METRIC_TOKENS:
            assert token not in called, (path.name, token)
            assert token not in assigned, (path.name, token)
        scanned += 1
    assert {p.name for p in sg.production_py_files()} >= sg.EXPECTED_PRODUCTION_MODULES
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)  # non-vacuity


def test_no_u22_production_module_imports_observability():
    for path in sg.production_py_files():
        text = path.read_text(encoding="utf-8")
        assert "backend.observability" not in text, path.name


def test_detector_a_synthetic_metric_definition_is_flagged():
    source = 'X = MetricDefinition(name="judge_runs_total")\n'
    assert "MetricDefinition" in sg.called_names(sg.parse_source(source))


def test_detector_a_synthetic_metric_constant_is_flagged():
    source = "METRIC_DEFINITIONS = ()\n"
    assert "METRIC_DEFINITIONS" in sg.assigned_names(sg.parse_source(source))


# --- (b) CORROBORATING: the read-only property assertions --------------------------------


def test_observabilitys_frozen_five_metrics_are_unchanged():
    assert len(METRIC_DEFINITIONS) == 5
    names = {m.name for m in METRIC_DEFINITIONS}
    assert len(names) == 5


def test_the_dashboard_still_declares_exactly_five_panels():
    panels = sg.load_dashboard()["panels"]
    assert len(panels) == 5


def test_the_dashboard_has_no_nested_row_panels():
    """U22's one addition: future row-nesting FAILS LOUDLY rather than silently
    under-counting a naive top-level len()."""
    panels = sg.load_dashboard()["panels"]
    assert not any("panels" in p for p in panels)
    assert not any(p.get("type") == "row" for p in panels)


def test_the_dashboard_panels_match_the_frozen_metric_topology():
    """The technique is deploy_config/tests/test_scope.py's, reused not reinvented."""
    panels = sg.load_dashboard()["panels"]
    dashboard_metrics = {p["targets"][0]["expr"] for p in panels}
    assert dashboard_metrics == {m.name for m in METRIC_DEFINITIONS}


def test_u22_adds_no_sixth_metric_and_no_sixth_panel():
    """The property U22 must not drift on, stated as one assertion."""
    assert len(METRIC_DEFINITIONS) == 5
    assert len(sg.load_dashboard()["panels"]) == 5
