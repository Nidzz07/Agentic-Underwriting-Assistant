"""TIERU-1: U21's tier-U surface uses NO socket / NO key / NO Docker (BR-OBS-6). No U21 test
IMPORTS a network / live-SDK / testcontainers dependency; the injected fakes are plain classes.
The 31 skips + 5 pre-existing audit_store Docker errors are unchanged (U21 adds none) — verified
at the full-suite run in the completion gate.

Detection is AST import-based (via the structural helper) so a forbidden name appearing only as
DATA (e.g. a token literal) is not misread as a dependency.
"""
from __future__ import annotations

import pathlib

from backend.observability.tests import structural as sg

_TESTS_DIR = pathlib.Path(__file__).resolve().parent

# Forbidden IMPORT roots at tier-U — network / live-SDK / container deps.
_FORBIDDEN_IMPORT_ROOTS = {
    "socket",
    "langfuse",
    "prometheus_client",
    "testcontainers",
    "docker",
    "requests",
    "httpx",
}


def _u21_test_files() -> list[pathlib.Path]:
    return [p for p in _TESTS_DIR.glob("*.py") if p.name != "__init__.py"]


def _forbidden_import_roots(modules: set[str]) -> set[str]:
    roots = {m.split(".")[0] for m in modules}
    return roots & _FORBIDDEN_IMPORT_ROOTS


def test_no_network_key_or_docker_import_in_any_u21_test():
    for path in _u21_test_files():
        modules = sg.imported_modules(sg.parse(path))
        assert _forbidden_import_roots(modules) == set(), f"{path.name} imports a live dep"


def test_no_forbidden_import_in_any_u21_production_module():
    for path in sg.production_py_files():
        assert _forbidden_import_roots(sg.imported_modules(sg.parse(path))) == set(), path.name


def test_detector_flags_a_synthetic_live_sink_import():
    modules = sg.imported_modules(
        sg.parse_source("import socket\nfrom langfuse import Langfuse\nimport prometheus_client\n")
    )
    flagged = _forbidden_import_roots(modules)
    assert {"socket", "langfuse", "prometheus_client"} <= flagged


def test_the_injected_fakes_are_plain_classes_no_live_client():
    from backend.observability.tests.fixtures import (
        RecordingMetricExporter,
        RecordingTraceSink,
    )

    assert RecordingTraceSink().spans == []
    assert RecordingMetricExporter().contributions == []
