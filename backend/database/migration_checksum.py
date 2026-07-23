"""C6 MigrationChecksum — published-migration immutability (NFR-DB-MIGRATE-2).

A committed manifest ``migrations/checksums.json`` maps ``{migration_filename: sha256}``
for **every published migration, including the grants file**. ``verify_checksums``
recomputes each file's hash and compares:

- **editing** a published migration → changed hash → **fail** (mirrors append-only:
  a change is a NEW migration, never a mutation);
- **appending** a new migration + its manifest entry → **allowed**.

Because the grants file (``0002_grants.sql``) is in the manifest, a silently
**weakened ``audit_reader`` grant** (e.g. adding INSERT) is caught **identically** to
an edited table migration — tying append-only / SEC-4 integrity to the immutability
check. The manifest hashes the **placeholder-bearing** grants file (SEC-3: the secret
is never in the checksummed content, so the checksum is stable across environments).

Pure hashing over files — unit-tier, no container.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from backend.database.migration_runner import MIGRATIONS_DIR, migration_files

#: The committed immutability manifest.
MANIFEST_PATH = MIGRATIONS_DIR / "checksums.json"


class ChecksumMismatchError(AssertionError):
    """A published migration was edited in place, or the manifest/disk sets diverged."""


def file_sha256(path: Path) -> str:
    """SHA-256 hex digest over a migration file's raw bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_checksums(migrations_dir: Path = MIGRATIONS_DIR) -> dict[str, str]:
    """``{filename: sha256}`` over every ``NNNN_*.sql`` migration on disk."""
    return {path.name: file_sha256(path) for path in migration_files(migrations_dir)}


def load_manifest(manifest_path: Path = MANIFEST_PATH) -> dict[str, str]:
    return json.loads(Path(manifest_path).read_text(encoding="utf-8"))


def verify_checksums(
    migrations_dir: Path = MIGRATIONS_DIR, manifest_path: Path = MANIFEST_PATH
) -> None:
    """Raise ``ChecksumMismatchError`` if any published migration was edited in place,
    is present on disk but missing from the manifest, or listed in the manifest but
    missing on disk."""
    manifest = load_manifest(manifest_path)
    actual = compute_checksums(migrations_dir)
    problems: list[str] = []

    for name, digest in actual.items():
        if name not in manifest:
            problems.append(f"{name}: on disk but missing from the manifest (add its entry)")
        elif manifest[name] != digest:
            problems.append(f"{name}: checksum mismatch — a published migration was edited in place")
    for name in manifest:
        if name not in actual:
            problems.append(f"{name}: in the manifest but missing on disk")

    if problems:
        raise ChecksumMismatchError(
            "migration immutability violated:\n  " + "\n  ".join(problems)
        )
