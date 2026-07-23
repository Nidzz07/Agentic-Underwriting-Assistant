"""StructuralGuard (C-OBS-4 / P-OBS-10) — FIVE AST/import scans, EACH with a mandatory detector
self-test (non-vacuous, per the project convention). Covers the structural halves of
NOEDIT-1 / SEP-1 / DEMOFREE-1 / SHAPE-1 / CONTRACT-1.
"""
from __future__ import annotations

from backend.observability.tests import structural as sg


# ===========================================================================
# Non-vacuity: the scans actually see the three production modules.
# ===========================================================================
def test_scan_set_sees_the_real_production_modules():
    names = {p.name for p in sg.production_py_files()}
    assert sg.EXPECTED_PRODUCTION_MODULES <= names


# ===========================================================================
# Scan 1 — NOEDIT-1: no U21 production module imports/mutates any frozen unit source.
# ===========================================================================
def test_scan1_no_frozen_backend_import_in_production():
    for path in sg.production_py_files():
        roots = sg.backend_edge_roots(sg.imported_modules(sg.parse(path)))
        assert roots == set(), f"{path.name} imports a non-observability backend unit: {roots}"
        assert not (roots & sg.FROZEN_BACKEND_ROOTS)


def test_scan1_detector_flags_a_synthetic_frozen_import():
    roots = sg.backend_edge_roots(
        sg.imported_modules(sg.parse_source("from backend.memo_agent_core.orchestrator import X\n"))
    )
    assert "memo_agent_core" in roots


# ===========================================================================
# Scan 2 — SEP-1: no trace <-> metric cross-import; the shared allowlist is permitted.
# ===========================================================================
def _imports_plane(modules: set[str], plane: str) -> bool:
    target = f"backend.observability.{plane}"
    return any(m == target for m in modules)


def test_scan2_trace_does_not_import_metric_and_vice_versa():
    trace_mods = sg.imported_modules(sg.parse(sg.module_file(sg.TRACE_MODULE)))
    metric_mods = sg.imported_modules(sg.parse(sg.module_file(sg.METRICS_MODULE)))
    assert not _imports_plane(trace_mods, "metrics")
    assert not _imports_plane(metric_mods, "trace")
    # the shared allowlist is the ONE legitimate shared import (permitted, non-vacuity)
    assert _imports_plane(trace_mods, "allowlist")
    assert _imports_plane(metric_mods, "allowlist")


def test_scan2_detector_flags_a_synthetic_cross_plane_import():
    mods = sg.imported_modules(sg.parse_source("from backend.observability.metrics import x\n"))
    assert _imports_plane(mods, "metrics")


# ===========================================================================
# Scan 3 — DEMOFREE-1 no-bypass: every record_span attributes arg is a project_allowlisted call;
#          both derivations route through project_allowlisted.
# ===========================================================================
def test_scan3_no_bypass_trace_projects_every_span_attribute():
    tree = sg.parse(sg.module_file(sg.TRACE_MODULE))
    assert sg.record_span_call_count(tree) >= 1          # non-vacuity: record_span IS called
    assert sg.record_span_call_args_are_projected(tree)


def test_scan3_metric_derivations_route_through_the_allowlist():
    assert sg.calls_project_allowlisted(sg.parse(sg.module_file(sg.METRICS_MODULE)))


def test_scan3_detector_flags_a_synthetic_raw_record_span():
    raw = "self._sink.record_span(step, raw_attributes)\n"          # NOT projected
    assert not sg.record_span_call_args_are_projected(sg.parse_source(raw))
    projected = "self._sink.record_span(step, project_allowlisted(raw, A))\n"
    assert sg.record_span_call_args_are_projected(sg.parse_source(projected))


# ===========================================================================
# Scan 4 — SHAPE-1: no import of any frozen event TYPE in production.
# ===========================================================================
def test_scan4_no_frozen_event_type_imported_in_production():
    for path in sg.production_py_files():
        imported = sg.imported_names(sg.parse(path))
        assert not (imported & sg.FROZEN_EVENT_TYPES), path.name


def test_scan4_detector_flags_a_synthetic_frozen_event_type_import():
    names = sg.imported_names(
        sg.parse_source("from backend.memo_agent_core.telemetry import MemoTelemetryEvent\n")
    )
    assert "MemoTelemetryEvent" in names & sg.FROZEN_EVENT_TYPES


# ===========================================================================
# Scan 5 — CONTRACT-1: no Recommendation/Confidence type declared in production.
# ===========================================================================
_VERDICT_TYPES = {"Recommendation", "Confidence"}


def test_scan5_no_recommendation_or_confidence_type_in_production():
    for path in sg.production_py_files():
        assert not (sg.defined_type_names(sg.parse(path)) & _VERDICT_TYPES), path.name


def test_scan5_detector_flags_a_synthetic_recommendation_annotation():
    names = sg.defined_type_names(sg.parse_source("class M:\n    recommendation: Recommendation\n"))
    assert "Recommendation" in names & _VERDICT_TYPES
