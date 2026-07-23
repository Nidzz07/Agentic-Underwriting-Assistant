"""Structural test — NFR-SEC-LEAF-1: secrets-config is a dependency leaf (Step 5).

AST-scans every `secrets_config` PRODUCTION `.py` (excluding `tests/`) and asserts none
imports `backend.database` or any consumer package — proving the dependency-leaf /
no-circular-dependency property structurally (BR-SEC-5), not by inspection.

Robustness guards: a non-vacuous guard verifies the scan sees THIS unit's OWN real
modules (`settings.py`, `url_validation.py` — fold 1, NOT copy-pasted auth_rbac names);
a self-test proves the detector flags a synthetic forbidden import.
"""
from __future__ import annotations

import ast
import pathlib

# backend/secrets_config/  (parent of this tests/ dir)
_SECRETS_DIR = pathlib.Path(__file__).resolve().parent.parent
_FORBIDDEN_PREFIXES = (
    "backend.database",
    "backend.audit_store",
    "backend.memo_agent_core",
    "backend.auth_rbac",
    "backend.intake",
)


def _production_py_files() -> list[pathlib.Path]:
    return [p for p in _SECRETS_DIR.rglob("*.py") if "tests" not in p.parts]


def _imported_modules(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                modules.add(node.module)
    return modules


def _is_forbidden(module: str) -> bool:
    return any(module == p or module.startswith(p + ".") for p in _FORBIDDEN_PREFIXES)


def test_no_database_or_consumer_import():
    offenders: list[str] = []
    for path in _production_py_files():
        for module in _imported_modules(path):
            if _is_forbidden(module):
                offenders.append(f"{path.name}: imports {module}")
    assert offenders == [], f"forbidden production imports: {offenders}"


def test_scan_sees_own_modules():
    # non-vacuous (fold 1): the scan covers THIS unit's own real modules.
    names = {p.name for p in _production_py_files()}
    assert {"settings.py", "url_validation.py"} <= names


def test_scanner_detects_a_forbidden_import(tmp_path):
    f = tmp_path / "synthetic.py"
    f.write_text(
        "from backend.database import x\nimport backend.auth_rbac.authorizer\n",
        encoding="utf-8",
    )
    detected = {m for m in _imported_modules(f) if _is_forbidden(m)}
    assert any(m.startswith("backend.database") for m in detected)
    assert any(m.startswith("backend.auth_rbac") for m in detected)
