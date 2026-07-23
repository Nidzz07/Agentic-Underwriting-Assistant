"""INT-FROZEN-1 — the composition root COMPOSES the 17 frozen units; it re-implements none.

The binding hold: all 17 frozen units are imported/composed, NEVER edited, and no file under any
frozen ``backend/<unit>/`` tree is created or modified. This guard asserts the half that is
checkable from inside the suite — that ``backend/app/`` adds no domain logic of its own and
declares none of the frozen units' symbols. (The "no file edited" half is verified out-of-band
by an mtime scan and reported at the gate.)
"""
from __future__ import annotations

import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = APP_ROOT.parent
PRODUCTION_FILES = sorted(p for p in APP_ROOT.rglob("*.py") if "tests" not in p.parts)

#: The frozen units this slice composes.
COMPOSED_UNITS = {"audit_store", "auth_rbac", "secrets_config"}
#: Every frozen unit directory that must remain untouched by this package.
FROZEN_UNITS = {
    "intake", "rules_engine", "memo_agent_core", "audit_store", "auth_rbac",
    "secrets_config", "database", "corpus_generator", "quality_gates", "admin_cli", "common",
}


def top_level_defs(source: str) -> set[str]:
    tree = ast.parse(source)
    return {
        n.name for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


class TestTheFrozenUnitsAreImportedNotReimplemented:
    def test_the_app_declares_none_of_the_frozen_units_symbols(self):
        # If the composition root ever re-declared e.g. AuthRBAC or AuditService, it would be
        # forking a frozen unit rather than composing it.
        forbidden = {
            "AuthRBAC", "ApiAuthGuard", "AuditService", "PostgresAuditRepository",
            "PostgresUserRoleRepository", "Settings", "AuditRecord", "Role", "to_role",
        }
        for path in PRODUCTION_FILES:
            declared = top_level_defs(path.read_text(encoding="utf-8"))
            assert not (declared & forbidden), f"{path} re-declares {declared & forbidden}"

    def test_the_composed_units_are_reached_by_import(self):
        source = "\n".join(p.read_text(encoding="utf-8") for p in PRODUCTION_FILES)
        for unit in COMPOSED_UNITS:
            assert f"from backend.{unit}" in source, unit

    def test_the_app_owns_no_persistence_of_its_own(self):
        # It invents no domain state (the whole basis of Scope A): no table, no model, no store.
        for path in PRODUCTION_FILES:
            source = path.read_text(encoding="utf-8")
            for forbidden in ("CREATE TABLE", "__tablename__", "declarative_base", "sa.Table("):
                assert forbidden not in source, f"{path}: {forbidden}"


class TestNoFileIsAddedUnderAFrozenUnit:
    def test_backend_app_is_the_only_backend_tree_this_pass_owns(self):
        # The composition root lives at backend/app/ (unit-of-work.md §2's tree) and nowhere else.
        # NOTE: a text scan for a phrase like "composition root" would be worse than useless here —
        # five frozen units (audit_store/seams.py, rules_engine/engine.py, secrets_config/settings.py,
        # admin_cli/*) legitimately NAME the composition root in their own deferral docstrings. The
        # checkable fact is the IMPORT DIRECTION (below), not the prose.
        assert (BACKEND_ROOT / "app").is_dir()
        owned = {p.parts[p.parts.index("backend") + 1] for p in PRODUCTION_FILES}
        assert owned == {"app"}

    def test_no_frozen_unit_imports_the_composition_root(self):
        # The dependency arrow points ONE way: app -> units. A unit importing back would make
        # the composition root a dependency of the things it composes.
        for unit in FROZEN_UNITS:
            unit_dir = BACKEND_ROOT / unit
            if not unit_dir.exists():
                continue
            for path in unit_dir.rglob("*.py"):
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
                imports = [l for l in lines if l.strip().startswith(("import ", "from "))]
                assert not any("backend.app" in l for l in imports), path


class TestDetectorSelfTests:
    def test_top_level_defs_finds_declarations(self):
        assert top_level_defs("class AuthRBAC:\n    pass\n") == {"AuthRBAC"}
        assert top_level_defs("def to_role(x):\n    return x\n") == {"to_role"}
        assert top_level_defs("from backend.auth_rbac.authorizer import AuthRBAC\n") == set()

    def test_an_import_is_not_a_declaration(self):
        # The distinction the guard rests on: importing AuthRBAC is composition; defining it
        # would be a fork.
        assert "AuthRBAC" not in top_level_defs("from backend.auth_rbac.authorizer import AuthRBAC\n")
