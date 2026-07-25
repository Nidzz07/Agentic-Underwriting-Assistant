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

from backend.deploy_config.tests._route_inventory import (
    ROUTE_INVENTORY,
    ROUTE_MODULE_INVENTORY,
)

#: The declared WIRE-1 route surface — by (path, method).
#:
#: ⚑ RELAXED 2026-07-25 (frozen-assertion relaxation, R-1). This set was SEVEN INLINE
#: LITERAL TUPLES. The literal moved to ``_route_inventory.py``; **the comparison below is
#: unchanged and remains EXACT-SET EQUALITY**, which is where the guard's strength lives.
#: Growth still fails this test until the inventory is deliberately updated.
#:
#: ⚑ It also closed a real drift risk: this literal and ``test_no_write_route.py``'s
#: identical seven-path literal were maintained INDEPENDENTLY, with nothing forcing them to
#: agree. Both now read one declared inventory, cross-checked by
#: ``backend/app/tests/test_route_inventory_sync.py``.
_EXPECTED = set(ROUTE_INVENTORY)


def _route_set(openapi_paths) -> set:
    return {
        (p, method.lower())
        for p, methods in openapi_paths.items()
        for method in methods
    }


def test_route_table_equals_the_frozen_composition_root():
    got = _route_set(create_app().openapi()["paths"])
    assert got == _EXPECTED


def test_route_modules_are_exactly_the_declared_inventory():
    """The modules under ``backend/app/routes/`` are exactly the declared set.

    ⚑ RENAMED 2026-07-25 from ``test_no_new_route_file_added_under_backend_app_by_u23``
    (frozen-assertion relaxation, R-2 · Q2(a)). **Supersede-not-rewrite: the old name is
    recorded here, not erased.**

    **Why renamed**: the old name made a **provenance** claim — *"U23 adds none"* — while the
    assertion is and always was a **directory-wide exact-set guard that fires on ANY author's
    addition**. Intent and implementation diverged, and Scope B was the first pass to hit the
    difference. Leaving the stale name would have reproduced **register #13**'s exact defect
    (*a name asserting something the file no longer means*) in a third place, which is the
    outcome that register argues hardest against.

    **What did NOT change**: the assertion is still **exact-set equality**. The literal moved
    into ``_route_inventory.py``, so a sixth module still fails this test until it is
    deliberately declared.
    """
    routes_dir = sg.REPO_ROOT / "backend" / "app" / "routes"
    route_files = {p.name for p in routes_dir.glob("*.py")}
    assert route_files == set(ROUTE_MODULE_INVENTORY)


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
