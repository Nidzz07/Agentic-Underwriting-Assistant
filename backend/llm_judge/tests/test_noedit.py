"""NFR-JUDGE-NOEDIT-1 (P-JUDGE-3) — LOAD-BEARING (full-highest). BR-JUDGE-11 / Q2-A.

The U23 ``P-DEP-1 FrozenPathScanPattern`` mechanism REUSED, not reinvented: every path a U22
deliverable authors must be a subset of ``ALLOWED_U22_PREFIXES`` and DISJOINT from
``FROZEN_PREFIXES`` (every frozen ``backend/<unit>/`` tree + the CLOSED composition root
``backend/app/**``).

Import-to-read != edit: U22 imports frozen shapes READ-ONLY. NOEDIT-1 forbids WRITES, so the
read-only imports and this scan agree by construction (the settled ROUTES-1 / Q2-A position).
"""
from __future__ import annotations

from backend.llm_judge.tests import structural as sg


def _under_any(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path == p or path.startswith(p + "/") for p in prefixes)


def test_every_authored_path_is_inside_u22s_own_tree():
    authored = [sg.repo_relative(p) for p in sg.authored_py_files()]
    assert authored  # non-vacuity: the scan found files
    for path in authored:
        assert _under_any(path, sg.ALLOWED_U22_PREFIXES), path


def test_no_authored_path_lies_under_any_frozen_tree_or_the_composition_root():
    for path in (sg.repo_relative(p) for p in sg.authored_py_files()):
        assert not _under_any(path, sg.FROZEN_PREFIXES), path


def test_the_allowed_and_frozen_prefix_sets_are_disjoint():
    for allowed in sg.ALLOWED_U22_PREFIXES:
        assert not _under_any(allowed, sg.FROZEN_PREFIXES)


def test_detector_a_synthetic_frozen_path_write_is_flagged():
    """The scan cannot pass vacuously."""
    assert _under_any("backend/app/main.py", sg.FROZEN_PREFIXES)
    assert _under_any("backend/memo_agent_core/prompt_builder.py", sg.FROZEN_PREFIXES)
    assert _under_any("backend/observability/metrics.py", sg.FROZEN_PREFIXES)
    assert not _under_any("backend/app/main.py", sg.ALLOWED_U22_PREFIXES)


def test_detector_every_frozen_prefix_is_actually_guarded():
    for prefix in sg.FROZEN_PREFIXES:
        assert _under_any(f"{prefix}/anything.py", sg.FROZEN_PREFIXES), prefix


def test_the_frozen_prefix_set_covers_the_composition_root_and_every_phase_two_unit():
    for required in (
        "backend/app",                # the CLOSED composition root
        "backend/memo_agent_core",    # U4 - the frozen P1 unit U22 reads
        "backend/outlier_model",      # U18
        "backend/memo_extensions",    # U19
        "backend/observability",      # U21
        "backend/deploy_config",      # U23
        "frontend/src",               # U20 and the ui-* units
    ):
        assert required in sg.FROZEN_PREFIXES


def test_running_this_suite_mutates_no_frozen_file():
    """Behavioural: the frozen artifacts U22 reads are byte-identical before and after."""
    before = sg.OBSERVABILITY_METRICS.read_bytes()
    dashboard_before = sg.GRAFANA_DASHBOARD.read_bytes()
    sg.load_dashboard()  # a READ
    assert sg.OBSERVABILITY_METRICS.read_bytes() == before
    assert sg.GRAFANA_DASHBOARD.read_bytes() == dashboard_before
