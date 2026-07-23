"""C6 StructuralGuard — reference-not-own / no-secret / scope / provider-deferred.

A stdlib-``ast`` scan of ``backend/admin_cli/`` production files (REFNOTOWN-1 /
NOSECRET-1 / SCOPE-1 / PROVIDER-DEFER-1) with **non-vacuous self-tests** — mirroring
``auth_rbac/tests/test_no_forbidden_imports.py`` and
``corpus_generator/tests/test_reference_not_own.py``. Lives in ``tests/`` (not counted
toward production coverage). The ``secrets_config`` / ``create_engine`` allowlist is
scoped to ``__main__.py`` **only** (per-file, ADMIN-CG-Fold-1).
"""
from __future__ import annotations

import ast
import pathlib

_PKG = pathlib.Path(__file__).resolve().parent.parent  # backend/admin_cli/


def _production_files() -> list[pathlib.Path]:
    """Every ``.py`` under ``backend/admin_cli/`` EXCLUDING the tests package."""
    return [p for p in _PKG.rglob("*.py") if "tests" not in p.parts]


def _imported_modules(source: str) -> set[str]:
    tree = ast.parse(source)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                modules.add(node.module)
    return modules


def _string_constants(source: str) -> list[str]:
    tree = ast.parse(source)
    return [
        n.value for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    ]


def _looks_like_secret(value: str) -> bool:
    """A credential/URL VALUE literal (NOSECRET-1)."""
    return value.startswith(("postgresql://", "postgres://"))


_LLM_TOP_LEVEL = {"anthropic", "openai", "google", "ollama", "langchain", "langgraph", "vertexai"}


def _is_forbidden_import(module: str, filename: str) -> bool:
    """True if ``module`` must not be imported from the file named ``filename``."""
    top = module.split(".")[0]
    if top in _LLM_TOP_LEVEL:                                   # SCOPE-1 — no LLM SDK
        return True
    if module.startswith("backend.database"):                  # REFNOTOWN-1
        return True
    if module.startswith("backend.audit_store"):               # REFNOTOWN-1 / no commit path
        return True
    if module.startswith("backend.memo_agent_core"):           # SCOPE-1 — no decision path
        return True
    if module in {                                             # SCOPE-1 — no rule evaluation
        "backend.rules_engine.engine",
        "backend.rules_engine.evaluator",
        "backend.rules_engine.aggregator",
    }:
        return True
    if module.startswith("backend.auth_rbac") and module != "backend.auth_rbac.roles":
        return True                                            # only .roles (call-only) allowed
    if module.startswith("backend.secrets_config") and filename != "__main__.py":
        return True                                            # allowlisted to __main__ ONLY
    return False


# --- REFNOTOWN-1 / SCOPE-1 -----------------------------------------------------------

def test_no_forbidden_production_imports():
    for path in _production_files():
        source = path.read_text(encoding="utf-8")
        for module in _imported_modules(source):
            assert not _is_forbidden_import(module, path.name), (
                f"{path.name} imports forbidden module {module!r}"
            )


def test_publish_path_delegates_to_build_rulebook():  # PUBVALID-1
    src = (_PKG / "rulebook_publisher.py").read_text(encoding="utf-8")
    assert "backend.rules_engine.loader" in _imported_modules(src)
    assert "build_rulebook" in src and "RulebookLoader" in src


def test_role_gate_uses_the_canonical_role():
    src = (_PKG / "role_gate.py").read_text(encoding="utf-8")
    assert "backend.auth_rbac.roles" in _imported_modules(src)


# --- NOSECRET-1 ----------------------------------------------------------------------

def test_no_secret_literal_in_the_package():
    for path in _production_files():
        for value in _string_constants(path.read_text(encoding="utf-8")):
            assert not _looks_like_secret(value), f"{path.name} contains a secret-like literal"


# --- PROVIDER-DEFER-1 ----------------------------------------------------------------

def test_no_set_provider_command_or_config_store():
    names = {p.name for p in _production_files()}
    assert not any("provider" in n for n in names)  # no provider-config store module
    # A subcommand name is a STRING LITERAL (add_parser("set-provider")); a docstring
    # mentioning the deferral is a different constant, so check exact-equality — not a
    # substring-in-text scan (which would misfire on prose).
    for path in _production_files():
        consts = _string_constants(path.read_text(encoding="utf-8"))
        assert "set-provider" not in consts and "set_provider" not in consts


# --- Non-vacuous self-tests (the guard is not a no-op) -------------------------------

def test_scan_sees_the_real_production_modules():
    names = {p.name for p in _production_files()}
    assert {"role_gate.py", "app_user_writer.py", "pg_writer.py", "cli.py", "__main__.py"} <= names


def test_scanner_detects_a_forbidden_import():
    assert _is_forbidden_import("backend.database", "cli.py")
    assert "backend.database" in _imported_modules("import backend.database\n")


def test_scanner_detects_a_secret_literal():
    values = _string_constants("x = 'postgresql://user:pw@host:5432/db'\n")
    assert any(_looks_like_secret(v) for v in values)


def test_scanner_detects_a_set_provider_subcommand_literal():  # PROVIDER-DEFER-1 non-vacuous
    consts = _string_constants('sub.add_parser("set-provider")\n')
    assert "set-provider" in consts


def test_secrets_config_allowlist_is_scoped_to_main_only():  # ADMIN-CG-Fold-1
    # forbidden in any non-main module, allowed in __main__.py only (per-file, not package-wide)
    assert _is_forbidden_import("backend.secrets_config.settings", "cli.py")
    assert not _is_forbidden_import("backend.secrets_config.settings", "__main__.py")
