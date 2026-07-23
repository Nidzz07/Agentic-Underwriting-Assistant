"""NFR-CASE-MIGNAME-1 (P-CASE-11) — migration namespacing + the collision guard. BR-CASE-11.

⚑ The hazard: the shared `applied_migrations` table is keyed by the BARE FILENAME, so a name
shared with U15's sequence would be seen as already applied and SILENTLY SKIPPED — a no-op, not
an error. The guard runs IN PRODUCTION and raises loudly instead.
"""
from __future__ import annotations

import pytest

from backend.case_lifecycle.migrate import (
    CASE_MANIFEST_PATH,
    CASE_MIGRATIONS_DIR,
    MigrationNameCollision,
    assert_no_collision_with_database,
    case_migration_names,
    database_migration_names,
)
from backend.database.migration_checksum import verify_checksums


def test_u24_filenames_are_disjoint_from_databases():
    ours = case_migration_names()
    theirs = database_migration_names()
    assert ours, "non-vacuity — U24 must actually have a migration"
    assert theirs, "non-vacuity — database's sequence must be readable"
    assert ours.isdisjoint(theirs)


def test_the_production_guard_passes_for_the_real_sequences():
    assert_no_collision_with_database() is None


def test_the_descriptive_namespace_carries_the_unit_name():
    """The runner globs NNNN_*.sql, so a `u24_` prefix would not match — the namespace lives
    in the descriptive part."""
    assert "0001_case_lifecycle.sql" in case_migration_names()


def test_both_sequences_may_share_a_numeric_prefix_without_colliding():
    """The tracking PK is the whole filename, so 0001 vs 0001 is fine when names differ."""
    ours = {n.split("_", 1)[0] for n in case_migration_names()}
    theirs = {n.split("_", 1)[0] for n in database_migration_names()}
    assert ours & theirs                       # they DO share a numeric prefix
    assert case_migration_names().isdisjoint(database_migration_names())  # yet do not collide


def test_detector_a_synthetic_colliding_filename_is_flagged():
    """⚑ The guard must actually catch a collision."""
    collision = case_migration_names() & {"0001_case_lifecycle.sql"}
    assert collision                            # the name really is ours
    # Simulate the collision the guard defends against.
    ours = {"0001_initial_schema.sql"}
    theirs = database_migration_names()
    assert ours & theirs, "a shared filename must be detectable as an intersection"


def test_the_guard_raises_on_a_real_intersection(monkeypatch):
    import backend.case_lifecycle.migrate as migrate

    monkeypatch.setattr(migrate, "case_migration_names", lambda: {"0001_initial_schema.sql"})
    with pytest.raises(MigrationNameCollision):
        migrate.assert_no_collision_with_database()


def test_verify_checksums_passes_against_u24s_own_manifest():
    verify_checksums(migrations_dir=CASE_MIGRATIONS_DIR, manifest_path=CASE_MANIFEST_PATH)
