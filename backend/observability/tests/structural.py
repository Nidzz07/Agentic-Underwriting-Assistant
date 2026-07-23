"""Shared AST-scan substrate for the U21 StructuralGuard (C-OBS-4 / P-OBS-10).

Parses every PRODUCTION ``.py`` file under ``backend/observability/`` (EXCLUDING ``tests/``)
with ``ast`` — robust against comments/strings a text scan would misfire on. Each scan in
``test_structural_guard.py`` adds its own detector self-test + non-vacuity guard, mirroring the
frozen ``memo_extensions/tests/structural.py`` + ``outlier_model/tests/structural.py`` precedent.
"""
from __future__ import annotations

import ast
import pathlib

# backend/observability/  (parent of this tests/ dir)
UNIT_DIR = pathlib.Path(__file__).resolve().parent.parent

# The production modules that MUST be in every scan set (non-vacuity guard).
EXPECTED_PRODUCTION_MODULES = {"allowlist.py", "trace.py", "metrics.py"}

TRACE_MODULE = "trace.py"
METRICS_MODULE = "metrics.py"
ALLOWLIST_MODULE = "allowlist.py"

# The frozen-namespace roots U21 must never import/mutate in production (NOEDIT-1 / SHAPE-1).
FROZEN_BACKEND_ROOTS = {
    "memo_agent_core",
    "outlier_model",
    "memo_extensions",
    "secrets_config",
    "rules_engine",
    "audit_store",
    "intake",
    "corpus_generator",
    "auth_rbac",
    "database",
    "admin_cli",
    "quality_gates",
}

# Frozen event/result TYPE names U21 production must not import (SHAPE-1).
FROZEN_EVENT_TYPES = {
    "MemoTelemetryEvent",
    "EvaluationTelemetry",
    "CommitTelemetry",
    "IntakeTelemetry",
    "OutlierResult",
}


def production_py_files() -> list[pathlib.Path]:
    """Every ``.py`` under ``backend/observability/`` EXCLUDING the ``tests`` package."""
    return [p for p in UNIT_DIR.rglob("*.py") if "tests" not in p.parts]


def module_file(name: str) -> pathlib.Path:
    return UNIT_DIR / name


def parse(path: pathlib.Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def parse_source(source: str) -> ast.AST:
    return ast.parse(source)


def imported_modules(tree: ast.AST) -> set[str]:
    """Top-level absolute module names imported by a parsed tree (incl. TYPE_CHECKING)."""
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                modules.add(node.module)
    return modules


def imported_names(tree: ast.AST) -> set[str]:
    """Every name imported ``from X import <name>`` (for the frozen-event-type scan)."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.name)
    return names


def backend_edge_roots(modules: set[str]) -> set[str]:
    """For each ``backend.<unit>...`` import, the ``<unit>`` root — EXCLUDING U21-local
    (``backend.observability.*``), which is always permitted."""
    roots: set[str] = set()
    for module in modules:
        if not module.startswith("backend."):
            continue
        parts = module.split(".")
        if len(parts) < 2:
            continue
        unit = parts[1]
        if unit == "observability":
            continue  # U21-local self-import — always allowed
        roots.add(unit)
    return roots


def attribute_names(tree: ast.AST) -> set[str]:
    """Every attribute name read/accessed anywhere (``x.<attr>``)."""
    return {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}


def defined_type_names(tree: ast.AST) -> set[str]:
    """Every annotation type name used (AnnAssign targets' annotations + returns)."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            names |= _ann_names(node.annotation)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns is not None:
            names |= _ann_names(node.returns)
    return names


def _ann_names(node: ast.AST) -> set[str]:
    out: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            out.add(sub.id)
        elif isinstance(sub, ast.Attribute):
            out.add(sub.attr)
    return out


def record_span_call_args_are_projected(tree: ast.AST) -> bool:
    """True iff EVERY ``*.record_span(step, X)`` call has ``X`` be a ``project_allowlisted(...)``
    call — the no-bypass property (DEMOFREE-1). Vacuously True if there are no record_span calls,
    so the non-vacuity guard asserts trace.py HAS at least one."""
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr != "record_span":
            continue
        if len(node.args) < 2:
            return False
        second = node.args[1]
        if not (isinstance(second, ast.Call) and _callee_name(second) == "project_allowlisted"):
            return False
    return True


def record_span_call_count(tree: ast.AST) -> int:
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "record_span"
    )


def calls_project_allowlisted(tree: ast.AST) -> bool:
    return any(
        isinstance(node, ast.Call) and _callee_name(node) == "project_allowlisted"
        for node in ast.walk(tree)
    )


def _callee_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None
