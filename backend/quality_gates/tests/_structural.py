"""C9 StructuralGuard helpers (Q4-A) — stdlib ``ast`` scans, NO pytest internals.

Two static analyses over ``backend/quality_gates/`` source + gate test modules:

- ``scan_source_for_forbidden`` (REFNOTOWN-1) — flag any LOCAL re-implementation of
  a consumed surface: a local hasher (``hashlib``), a local ``evaluate`` / derivation
  / hasher / second engine ``def``. Importing the sanctioned surfaces call-only (e.g.
  ``from backend.rules_engine.report import evaluation_output``) is NOT flagged — the
  scope is *defining* a re-implementation, not *calling* the real one (ND-QG-Fold-3:
  orthogonal to P8's consumed-surface scope, which this enforces).
- ``scan_test_for_skips`` (BLOCKING-1) — flag any ``@skip``/``@xfail`` decorator on a
  ``test_*`` function or a module-level ``pytestmark`` — proving the gate tests are
  genuinely collected and build-failing, using static analysis only.
"""
from __future__ import annotations

import ast

#: Importing these locally would mean re-implementing a hasher (reference-not-own).
FORBIDDEN_IMPORTS = frozenset({"hashlib"})
#: Defining any of these locally would re-implement a consumed surface's logic.
FORBIDDEN_FUNC_DEFS = frozenset({
    "evaluate", "evaluate_rules", "build_namespace", "build_report",
    "compute_age", "compute_bmi", "content_hash",
})
_SKIP_DECORATORS = frozenset({"skip", "xfail"})


def scan_source_for_forbidden(source: str) -> list[str]:
    """Return findings (empty == clean) for a source module (reference-not-own)."""
    tree = ast.parse(source)
    findings: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_IMPORTS:
                    findings.append(f"forbidden import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                findings.append(f"forbidden import-from {node.module}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in FORBIDDEN_FUNC_DEFS:
                findings.append(f"forbidden local def {node.name}")
    return findings


def scan_test_for_skips(source: str) -> list[str]:
    """Return findings (empty == clean) for a gate test module (blocking form)."""
    tree = ast.parse(source)
    findings: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "pytestmark":
                    findings.append("module-level pytestmark")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            for decorator in node.decorator_list:
                if _decorator_leaf(decorator) in _SKIP_DECORATORS:
                    findings.append(f"{node.name} marked {_decorator_leaf(decorator)}")
    return findings


def collected_test_names(source: str) -> list[str]:
    """The ``test_*`` functions a module contributes to collection (static)."""
    tree = ast.parse(source)
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]


def _decorator_leaf(decorator: ast.expr) -> str | None:
    """The trailing attribute/name of a decorator (``pytest.mark.skip`` -> ``skip``)."""
    node = decorator.func if isinstance(decorator, ast.Call) else decorator
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None
