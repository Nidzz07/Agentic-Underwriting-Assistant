"""Shared AST-scan substrate for the U18 StructuralGuard (P-OUT-8 / NFR-OUT-SCOPE-1..).

Parses every PRODUCTION ``.py`` file under ``backend/outlier_model/`` (EXCLUDING ``tests/``)
with ``ast`` — robust against comments/strings a text scan would misfire on (the exact class of
bug the composition-root text pass had to fix once). Each individual scan module below adds its
own detector self-test + non-vacuity guard, mirroring the frozen
``auth_rbac/tests/test_no_forbidden_imports.py``.
"""
from __future__ import annotations

import ast
import pathlib

# backend/outlier_model/  (parent of this tests/ dir)
UNIT_DIR = pathlib.Path(__file__).resolve().parent.parent

# The production modules that MUST be in every scan set (non-vacuity guard).
EXPECTED_PRODUCTION_MODULES = {
    "feature_fields.py",
    "feature_vector.py",
    "corpus_source.py",
    "schemas.py",
    "shap_explainer.py",
    "model.py",
}


def production_py_files() -> list[pathlib.Path]:
    """Every ``.py`` under ``backend/outlier_model/`` EXCLUDING the ``tests`` package."""
    return [p for p in UNIT_DIR.rglob("*.py") if "tests" not in p.parts]


def parse(path: pathlib.Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def parse_source(source: str) -> ast.AST:
    return ast.parse(source)


def imported_modules(tree: ast.AST) -> set[str]:
    """Top-level absolute module names imported by a parsed tree."""
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                modules.add(node.module)
    return modules
