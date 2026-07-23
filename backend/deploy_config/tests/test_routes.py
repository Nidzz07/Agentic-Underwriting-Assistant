"""NFR-DEP-ROUTES-1 (LOAD-BEARING — full-highest): the deployed route table EQUALS the frozen
composition root's, unchanged — R1/R6/R7 live + the four R2-R5 markers; no new route file.

Static/in-process comparison via ``create_app().openapi()["paths"]`` — **no live server, no live
DB, no env** (route registration is env-free; the handlers' ``Depends`` resolve only at request
time). Reuses the composition-root pass's TestClient-free introspection (Req-Fold-1 / Fold-3).
Importing the production ``backend.app.main`` read-only to introspect is NOT editing (NOEDIT-1
forbids writes) — ROUTES-1 and NOEDIT-1 agree by construction.
"""
from __future__ import annotations

import pathlib

from backend.app.main import create_app
from backend.deploy_config.tests import structural as sg

#: The frozen WIRE-1 route surface (R1/R6/R7 real + the four R2-R5 markers) — by (path, method).
_EXPECTED = {
    ("/session", "get"),                                        # R1
    ("/decisions", "get"),                                      # R6
    ("/decisions/{decision_id}", "get"),                        # R7
    ("/applications", "get"),                                   # R2
    ("/applications/{application_id}", "get"),                  # R3
    ("/applications/{application_id}/memo", "get"),             # R4
    ("/recommendations/{recommendation_id}/commit", "post"),    # R5
}


def _route_set(openapi_paths) -> set:
    return {
        (p, method.lower())
        for p, methods in openapi_paths.items()
        for method in methods
    }


def test_route_table_equals_the_frozen_composition_root():
    got = _route_set(create_app().openapi()["paths"])
    assert got == _EXPECTED


def test_no_new_route_file_added_under_backend_app_by_u23():
    # U23 owns no file under backend/app/ (the closed composition root). The route files are the
    # frozen three (session, decisions, not_wired); U23 adds none.
    routes_dir = sg.REPO_ROOT / "backend" / "app" / "routes"
    route_files = {p.name for p in routes_dir.glob("*.py")}
    assert route_files == {"__init__.py", "session.py", "decisions.py", "not_wired.py"}


def test_detector_flags_a_synthetic_extra_route():
    # Non-vacuity: a route table with an extra path would NOT equal the frozen set.
    tampered = dict.fromkeys(("/session", "/decisions"), {"get": {}})
    tampered["/rogue"] = {"post": {}}
    assert _route_set(tampered) != _EXPECTED


def test_routes_introspection_needs_no_frozen_test_tree():
    # The scan imports only the PRODUCTION composition root, never backend/app/tests. AST-based so
    # the strings in this assertion are not self-matched as imports.
    modules = sg.imported_modules(pathlib.Path(__file__).read_text(encoding="utf-8"))
    assert "backend.app.main" in modules
    assert not any(m.startswith("backend.app.tests") for m in modules)
