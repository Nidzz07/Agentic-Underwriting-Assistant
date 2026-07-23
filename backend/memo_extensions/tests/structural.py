"""Shared AST-scan substrate for the U19 StructuralGuard (P-MEXT-10).

Parses every PRODUCTION ``.py`` file under ``backend/memo_extensions/`` (EXCLUDING
``tests/``) with ``ast`` — robust against comments/strings a text scan would misfire on.
Each scan in ``test_structural_guard.py`` adds its own detector self-test + non-vacuity
guard, mirroring the frozen ``outlier_model/tests/structural.py`` +
``auth_rbac/tests/test_no_forbidden_imports.py`` precedent.
"""
from __future__ import annotations

import ast
import pathlib

# backend/memo_extensions/  (parent of this tests/ dir)
UNIT_DIR = pathlib.Path(__file__).resolve().parent.parent

# The production modules that MUST be in every scan set (non-vacuity guard).
EXPECTED_PRODUCTION_MODULES = {
    "borderline_router.py",
    "mcp_tools.py",
    "provider_secondary.py",
    "provider_showcase.py",
}

# The mcp_tools handler surface (where a demographic leak or a write could be written).
HANDLER_MODULE = "mcp_tools.py"
ROUTER_MODULE = "borderline_router.py"


def production_py_files() -> list[pathlib.Path]:
    """Every ``.py`` under ``backend/memo_extensions/`` EXCLUDING the ``tests`` package."""
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


def backend_edge_roots(modules: set[str]) -> set[str]:
    """For each ``backend.<unit>...`` import, the ``<unit>`` root — EXCLUDING U19-local
    (``backend.memo_extensions.*``), which is always permitted."""
    roots: set[str] = set()
    for module in modules:
        if not module.startswith("backend."):
            continue
        parts = module.split(".")
        if len(parts) < 2:
            continue
        unit = parts[1]
        if unit == "memo_extensions":
            continue  # U19-local self-import — always allowed
        roots.add(unit)
    return roots


def attribute_names(tree: ast.AST) -> set[str]:
    """Every attribute name read/accessed anywhere (``x.<attr>``)."""
    return {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}


def mutating_calls_on_attribute(tree: ast.AST, attr_name: str) -> bool:
    """True iff the tree contains a mutation call ``<...>.<attr_name>.<append|extend|insert>(...)``
    — i.e. an APPEND into ``attr_name`` (distinct from constructing it as a keyword arg)."""
    mutators = {"append", "extend", "insert"}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr not in mutators:
            continue
        target = node.func.value
        if isinstance(target, ast.Attribute) and target.attr == attr_name:
            return True
    return False


def defined_method_names(tree: ast.AST) -> set[str]:
    """Every method/function name defined at any class level."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


def basemodel_classes_with_fields(tree: ast.AST) -> dict[str, set[str]]:
    """Map each class subclassing something named ``BaseModel`` / ``_Frozen`` to its
    annotated field names (AnnAssign targets). Used to scope the CONTRACT-1 scan."""
    out: dict[str, set[str]] = {}
    model_bases = {"BaseModel", "_Frozen"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        base_names = {b.id for b in node.bases if isinstance(b, ast.Name)}
        if not (base_names & model_bases):
            continue
        fields: set[str] = set()
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                fields.add(stmt.target.id)
        out[node.name] = fields
    return out
