"""NFR-CASE-MIGSCOPE-1 (P-CASE-11) — invocation confined to U24's own sequence. BR-CASE-12.

U24 applies ONLY its own migrations, authors NO CLI entrypoint (register #8
DEPLOY-MIGRATE-DEFERRED is NOT adopted and NOT made worse), and grants to NO U15-owned role —
which is what keeps the tier-I test self-contained (CASE-Req-Fold-1).
"""
from __future__ import annotations

from backend.case_lifecycle.migrate import CASE_MIGRATIONS_DIR
from backend.case_lifecycle.tests import structural as sg
from backend.database.migration_runner import MIGRATIONS_DIR as DB_MIGRATIONS_DIR


def test_u24_uses_its_own_migrations_dir_not_databases_default():
    assert CASE_MIGRATIONS_DIR != DB_MIGRATIONS_DIR
    assert CASE_MIGRATIONS_DIR.name == "migrations"
    assert CASE_MIGRATIONS_DIR.parent.name == "case_lifecycle"


def test_the_runner_is_always_constructed_with_an_explicit_migrations_dir():
    """A bare MigrationRunner(engine) would silently apply U15's sequence."""
    source = sg.module_file("migrate.py").read_text(encoding="utf-8")
    assert "migrations_dir=CASE_MIGRATIONS_DIR" in source


def test_u24_authors_no_cli_entrypoint():
    """#8 DEPLOY-MIGRATE-DEFERRED is not adopted."""
    names = {p.name for p in sg.authored_py_files()}
    assert "__main__.py" not in names
    for path in sg.production_py_files():
        text = path.read_text(encoding="utf-8")
        assert "argparse" not in text, path.name
        assert '__name__ == "__main__"' not in text, path.name


def test_u24s_migration_grants_to_no_u15_role():
    """⚑ The condition that keeps the tier-I test self-contained."""
    raw = (CASE_MIGRATIONS_DIR / "0001_case_lifecycle.sql").read_text(encoding="utf-8")
    sql = sg.sql_without_comments(raw)      # ⚑ a comment saying "NO GRANTS" is not a GRANT
    upper = sql.upper()
    assert "GRANT" not in upper
    assert "CREATE ROLE" not in upper
    assert "audit_writer" not in sql
    assert "audit_reader" not in sql


def test_u24s_migration_creates_only_its_own_two_tables():
    sql = sg.sql_without_comments(
        (CASE_MIGRATIONS_DIR / "0001_case_lifecycle.sql").read_text(encoding="utf-8")
    )
    assert sql.count("CREATE TABLE") == 2
    assert "pending_application" in sql and "pending_recommendation" in sql
    for frozen_table in ("audit_record", "applicant_profile_snapshot", "app_user"):
        assert f"CREATE TABLE {frozen_table}" not in sql


def test_no_u24_test_constructs_the_migration_runner_directly():
    """⚑ CG-CASE-Fold-3 — the tier-I test must go through apply_case_migrations() so the
    PRODUCTION collision guard is exercised on the path PERSIST-1 verifies, not bypassed."""
    for path in sg.authored_py_files():
        if path.name in {"migrate.py", "test_migscope.py"}:
            continue  # migrate.py IS the sanctioned call site; this file holds the token
        text = path.read_text(encoding="utf-8")
        assert "MigrationRunner(" not in text, path.name


def test_apply_case_migrations_runs_the_guard_BEFORE_the_runner(monkeypatch):
    """⚑ CG-CASE-Fold-3, proven at tier-U: the production entry point calls the collision
    guard FIRST, then delegates to the frozen runner with U24's OWN directory."""
    import backend.case_lifecycle.migrate as migrate

    order: list[str] = []

    def _guard() -> None:
        order.append("guard")

    class _FakeRunner:
        def __init__(self, engine, migrations_dir=None, env=None):
            order.append("runner")
            assert migrations_dir == migrate.CASE_MIGRATIONS_DIR   # never U15's default

        def apply_all(self):
            order.append("apply")
            return ["0001_case_lifecycle.sql"]

    monkeypatch.setattr(migrate, "assert_no_collision_with_database", _guard)
    monkeypatch.setattr(migrate, "MigrationRunner", _FakeRunner)

    assert migrate.apply_case_migrations(object()) == ["0001_case_lifecycle.sql"]
    assert order == ["guard", "runner", "apply"]      # guard FIRST — never bypassed
