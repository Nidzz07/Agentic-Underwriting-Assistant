"""The one-way import direction: ``authn`` never imports the composition root (AUTHN-Fold-3).

⚑ **Why this test exists here rather than being inherited.** ``test_frozen_untouched.py``
already asserts that no frozen unit imports ``backend.app`` — but it iterates a **hardcoded**
``FROZEN_UNITS`` set of eleven Phase-1 packages, which does **not** include ``authn`` (nor
``case_lifecycle``, ``outlier_model``, ``memo_extensions``, ``observability``, ``llm_judge``).
So this package would be **silently uncovered** by that guard.

``case_lifecycle`` carries exactly that gap today. This closes it for ``authn`` rather than
replicating it: the composition root imports this package, **never the reverse**, and if that
ever inverts the failure is loud and local instead of undetected.

The scan is **AST-based**, so a module name appearing in prose or as scan DATA is not
mistaken for a real import.
"""
from __future__ import annotations

import ast
from pathlib import Path

AUTHN_ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_FILES = sorted(p for p in AUTHN_ROOT.rglob("*.py") if "tests" not in p.parts)


def imported_roots(source: str) -> set[str]:
    """Every dotted module path imported by ``source`` — AST, never substring matching."""
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module)
    return roots


def test_no_authn_module_imports_the_composition_root():
    # Non-vacuity (a): an empty scan set would make the guard trivially true.
    assert PRODUCTION_FILES, "no authn production modules found — the scan root is wrong"

    for path in PRODUCTION_FILES:
        roots = imported_roots(path.read_text(encoding="utf-8"))
        offending = {r for r in roots if r == "backend.app" or r.startswith("backend.app.")}
        assert not offending, f"{path.name} imports the composition root: {sorted(offending)}"

    # ⚑ Non-vacuity (b): the detector must genuinely discriminate. Proven SYNTHETICALLY,
    # because planting a real violation would mean shipping the very defect this prevents.
    assert "backend.app.dependencies" in imported_roots(
        "from backend.app.dependencies import current_identity\n"
    )
    assert "backend.app" in imported_roots("import backend.app\n")
    # ...and a mere mention in prose or a string is NOT an import.
    assert not imported_roots('"""backend.app is the composition root."""\nx = "backend.app"\n')
