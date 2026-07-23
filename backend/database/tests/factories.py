"""Shared test factories/helpers for the `database` integration tier — synthetic only.

Row builders drive inserts off the **reflected** migration-produced schema — they do
NOT import ``pg_repository``'s Table objects (that read-only import is reserved for the
FIDELITY-1 test). Role passwords here are **throwaway, fixture-scoped literals** for
the ephemeral testcontainer — never production values, never committed as config
(SEC-3). Not a test module.
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa

#: Throwaway role passwords for the ephemeral testcontainer (SEC-3: not production).
WRITER_PASSWORD = "test_writer_pw"
READER_PASSWORD = "test_reader_pw"

#: Adversarial BYTEA probe set — bytes a JSONB column would re-order/re-encode, plus
#: high/non-UTF8 bytes and the empty case. Proves the column performs NO normalization.
ADVERSARIAL_BYTES = [
    b'{"b":1,"a":2}',                       # (i) non-canonical JSON key order
    b'{"n":1.0000}',                        # (ii) number formatting / trailing zeros
    b'{  "k" : 1 ,  "z" : 2 }',             # (iii) extra whitespace
    bytes([0xFF, 0xFE, 0x00, 0x01, 0x80]),  # (iv) non-UTF8 / high bytes
    b"",                                    # (v) empty bytes
]


def role_engine(admin_engine: sa.Engine, username: str, password: str) -> sa.Engine:
    """A least-privilege engine connecting as a DB role (APPEND-1)."""
    return sa.create_engine(admin_engine.url.set(username=username, password=password))


def sample_audit_row(decision_id: str = "D1", application_id: str = "APP-1",
                     rule_results: bytes = b"\x00\x01", **over) -> dict:
    """A complete, valid ``audit_record`` row (all NOT-NULL columns populated)."""
    row = dict(
        decision_id=decision_id,
        application_id=application_id,
        recommendation_id="REC-1",
        rulebook_version="1.0.0",
        rule_results=rule_results,
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        model_version="gemini-1.5",
        memo_hash="memo-hash-1",
        engine_version="eng-sha-1",
        underwriter_id="UW-1",
        action="approve",       # CommitAction.APPROVE.value (BR-DB-9 varchar)
        reason=None,
        status="active",         # BR-DB-8 — always written explicitly
        supersedes_decision_id=None,
    )
    row.update(over)
    return row


def sample_snapshot_row(decision_id: str = "D1", application_id: str = "APP-1",
                        profile_canonical: bytes = b"\x00\x01",
                        content_hash: str = "profile-hash-1") -> dict:
    """A complete, valid ``applicant_profile_snapshot`` child row."""
    return dict(
        decision_id=decision_id,
        application_id=application_id,
        profile_canonical=profile_canonical,
        content_hash=content_hash,
    )
