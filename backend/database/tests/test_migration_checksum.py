"""Unit tests — C6 MigrationChecksum / NFR-DB-MIGRATE-2 (Step 7).

No container. Proves published-migration immutability: editing a published file
fails; appending a new migration + its manifest entry is allowed; the grants file is
covered so a weakened grant is caught identically to an edited table migration.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from backend.database.migration_checksum import (
    ChecksumMismatchError,
    MANIFEST_PATH,
    compute_checksums,
    verify_checksums,
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _make_dir(tmp_path: Path, files: dict[str, str], manifest: dict[str, str]) -> tuple[Path, Path]:
    for name, body in files.items():
        (tmp_path / name).write_text(body, encoding="utf-8")
    manifest_path = tmp_path / "checksums.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path, manifest_path


# --------------------------------------------------------------------------
# the committed manifest matches the committed migrations
# --------------------------------------------------------------------------
def test_committed_manifest_matches_committed_migrations():
    verify_checksums()  # real files + real manifest — no raise


def test_committed_manifest_includes_the_grants_file():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert "0002_grants.sql" in manifest         # fold #2 — grants covered
    assert "0001_initial_schema.sql" in manifest


# --------------------------------------------------------------------------
# editing a published migration fails
# --------------------------------------------------------------------------
def test_edited_published_migration_fails(tmp_path):
    original = "CREATE TABLE audit_record (decision_id VARCHAR NOT NULL);"
    d, m = _make_dir(
        tmp_path,
        {"0001_initial_schema.sql": original, "0002_grants.sql": "GRANT SELECT ON audit_record TO audit_reader;"},
        {"0001_initial_schema.sql": _sha(original),
         "0002_grants.sql": _sha("GRANT SELECT ON audit_record TO audit_reader;")},
    )
    # edit the published table migration in place
    (d / "0001_initial_schema.sql").write_text(original + "\nALTER TABLE audit_record ADD COLUMN x VARCHAR;", encoding="utf-8")
    with pytest.raises(ChecksumMismatchError):
        verify_checksums(d, m)


def test_weakened_grant_is_caught(tmp_path):
    # A silently weakened audit_reader grant (adding INSERT) — caught because the
    # grants file is in the manifest (fold #2 / SEC-4 integrity).
    good_grant = "GRANT SELECT ON audit_record TO audit_reader;"
    d, m = _make_dir(
        tmp_path,
        {"0001_initial_schema.sql": "CREATE TABLE t (id VARCHAR);", "0002_grants.sql": good_grant},
        {"0001_initial_schema.sql": _sha("CREATE TABLE t (id VARCHAR);"),
         "0002_grants.sql": _sha(good_grant)},
    )
    (d / "0002_grants.sql").write_text("GRANT INSERT, SELECT ON audit_record TO audit_reader;", encoding="utf-8")
    with pytest.raises(ChecksumMismatchError):
        verify_checksums(d, m)


# --------------------------------------------------------------------------
# appending a new migration is allowed; a file/manifest divergence fails
# --------------------------------------------------------------------------
def test_appending_new_migration_with_entry_allowed(tmp_path):
    files = {
        "0001_initial_schema.sql": "CREATE TABLE t (id VARCHAR);",
        "0002_grants.sql": "GRANT SELECT ON t TO audit_reader;",
        "0003_add_index.sql": "CREATE INDEX ix_t ON t (id);",
    }
    d, m = _make_dir(tmp_path, files, {name: _sha(body) for name, body in files.items()})
    verify_checksums(d, m)  # append + entry -> allowed, no raise


def test_new_file_without_manifest_entry_fails(tmp_path):
    files = {"0001_initial_schema.sql": "CREATE TABLE t (id VARCHAR);",
             "0002_grants.sql": "GRANT SELECT ON t TO audit_reader;"}
    d, m = _make_dir(tmp_path, files, {name: _sha(body) for name, body in files.items()})
    # a new migration appears on disk without a manifest entry
    (d / "0003_orphan.sql").write_text("CREATE INDEX ix_t ON t (id);", encoding="utf-8")
    with pytest.raises(ChecksumMismatchError):
        verify_checksums(d, m)


def test_manifest_entry_missing_on_disk_fails(tmp_path):
    files = {"0001_initial_schema.sql": "CREATE TABLE t (id VARCHAR);"}
    manifest = {"0001_initial_schema.sql": _sha("CREATE TABLE t (id VARCHAR);"),
                "0002_grants.sql": _sha("gone")}
    d, m = _make_dir(tmp_path, files, manifest)
    with pytest.raises(ChecksumMismatchError):
        verify_checksums(d, m)


def test_compute_checksums_over_committed_files():
    cs = compute_checksums()
    assert set(cs) == {"0001_initial_schema.sql", "0002_grants.sql"}
    assert all(len(v) == 64 for v in cs.values())  # sha256 hex
