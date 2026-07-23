"""Structural test — fold 1: NO production import of `audit_store`/`database` (Step 8).

Verifies the reference-not-own boundary **structurally**, not by inspection: it parses
every `auth-rbac` PRODUCTION `.py` file with `ast` (robust against comments/strings that
a naive text search would misfire on) and asserts none imports `backend.audit_store` or
`backend.database` — via either `import X` or `from X import ...`.

Robustness guards (so this cannot pass vacuously):
- `test_scan_sees_the_real_production_modules` — the file set actually includes the
  at-risk modules (`authorizer.py`, `api_guard.py`, `pg_repository.py`).
- `test_scanner_detects_a_forbidden_import` — a self-test proving the detection logic
  flags a synthetic forbidden import (it is not a no-op).
"""
from __future__ import annotations

import ast
import pathlib

# backend/auth_rbac/  (parent of this tests/ dir)
_AUTH_RBAC_DIR = pathlib.Path(__file__).resolve().parent.parent
_FORBIDDEN_PREFIXES = ("backend.audit_store", "backend.database")


def _production_py_files() -> list[pathlib.Path]:
    """Every `.py` under backend/auth_rbac/ EXCLUDING the tests package."""
    return [p for p in _AUTH_RBAC_DIR.rglob("*.py") if "tests" not in p.parts]


def _imported_modules(path: pathlib.Path) -> set[str]:
    """The set of top-level module names imported by a file (absolute imports)."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:  # absolute `from X import ...`
                modules.add(node.module)
    return modules


def _is_forbidden(module: str) -> bool:
    return any(module == fp or module.startswith(fp + ".") for fp in _FORBIDDEN_PREFIXES)


def test_no_audit_store_or_database_import():
    offenders: list[str] = []
    for path in _production_py_files():
        for module in _imported_modules(path):
            if _is_forbidden(module):
                offenders.append(f"{path.name}: imports {module}")
    assert offenders == [], f"forbidden production imports found: {offenders}"


def test_scan_sees_the_real_production_modules():
    # guard against a vacuous pass: the at-risk modules ARE in the scanned set.
    names = {p.name for p in _production_py_files()}
    assert {"authorizer.py", "api_guard.py", "pg_repository.py", "repository.py", "roles.py"} <= names


def test_scanner_detects_a_forbidden_import(tmp_path):
    # self-test: the detection logic genuinely flags a synthetic forbidden import.
    f = tmp_path / "synthetic.py"
    f.write_text(
        "from backend.database import app_user\nimport backend.audit_store.seams\n",
        encoding="utf-8",
    )
    detected = {m for m in _imported_modules(f) if _is_forbidden(m)}
    assert any(m.startswith("backend.database") for m in detected)
    assert any(m.startswith("backend.audit_store") for m in detected)
