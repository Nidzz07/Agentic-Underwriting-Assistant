"""C4 AppUserWriter — Integration tier over testcontainers postgres:16.

Real INSERT/UPDATE + explicit already-exists/no-such-user (NFR-ADMIN-CREATE-1 /
NFR-ADMIN-SETROLE-1) + the fault-injection sole-gate evidence (NFR-ADMIN-ROLEGATE-1 b /
ADMIN-Fold-1). ``@pytest.mark.integration``, auto-skipped without Docker.
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa

from backend.admin_cli.app_user_writer import AppUserWriter
from backend.admin_cli.exceptions import UserWriteError
from backend.admin_cli.pg_writer import PgWriter

pytestmark = pytest.mark.integration

_GET_ROLE = sa.text("SELECT role FROM app_user WHERE user_id = :user_id")


def _writer(engine) -> AppUserWriter:
    return AppUserWriter(PgWriter(engine))


def _role_of(engine, user_id):
    with engine.connect() as conn:
        return conn.execute(_GET_ROLE, {"user_id": user_id}).scalar_one_or_none()


def test_create_user_inserts_and_reads_back(app_user_engine):
    _writer(app_user_engine).create_user("u1", "s1", "underwriter")
    assert _role_of(app_user_engine, "u1") == "underwriter"


def test_duplicate_user_id_raises_already_exists(app_user_engine):
    w = _writer(app_user_engine)
    w.create_user("u1", "s1", "underwriter")
    with pytest.raises(UserWriteError, match="already exists"):
        w.create_user("u1", "s2", "auditor")  # PK user_id collision


def test_duplicate_subject_raises_already_exists(app_user_engine):
    w = _writer(app_user_engine)
    w.create_user("u1", "s1", "underwriter")
    with pytest.raises(UserWriteError, match="already exists"):
        w.create_user("u2", "s1", "auditor")  # UNIQUE subject collision (needs the constraint)


def test_set_role_updates_existing_user(app_user_engine):
    w = _writer(app_user_engine)
    w.create_user("u1", "s1", "underwriter")
    w.set_role("u1", "auditor")
    assert _role_of(app_user_engine, "u1") == "auditor"


def test_set_role_absent_user_raises_no_such_user(app_user_engine):
    with pytest.raises(UserWriteError, match="no such user"):
        _writer(app_user_engine).set_role("ghost", "admin")


def test_fault_injection_db_accepts_noncanonical_role_bypassing_the_writer(app_user_engine):
    # ROLEGATE-1 (b): a RAW insert of a non-canonical role, BYPASSING AppUserWriter, is
    # accepted by the DB (no CHECK) -> proves the open VARCHAR is not a gate, so admin-
    # cli's pre-write RoleGate is the SOLE enforcement (ADMIN-Fold-1). Never touches the
    # write path, so it cannot weaken the gate.
    with app_user_engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO app_user (user_id, subject, role) VALUES ('x', 'xs', 'superuser')"
        )
    assert _role_of(app_user_engine, "x") == "superuser"  # DB stored a non-canonical role
