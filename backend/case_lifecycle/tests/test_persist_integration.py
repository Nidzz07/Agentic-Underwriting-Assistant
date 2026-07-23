"""NFR-CASE-PERSIST-1 (P-CASE-12) — the tier-I SQL round-trip. Q1-A.

⚑ Uses `database`'s KNOWN-GOOD clean-skip guard VERBATIM: `_docker_available()` pings the daemon
INSIDE the fixture body, BEFORE any container is constructed. That is precisely why it SKIPS
CLEANLY where `audit_store`'s importorskip-only pattern reaches container construction and ERRORS
(the 5 pre-existing errors). **U24 adds ZERO errors.**

⚑ SELF-CONTAINED (CASE-Req-Fold-1): applies ONLY U24's sequence. No U15 migration is needed —
no cross-unit FK, no U15 role required, and `applied_migrations` is created idempotently.

⚑ CG-CASE-Fold-3: the fixture calls `apply_case_migrations()` — the PRODUCTION entry point — so
the production collision guard is exercised ON THE PATH THIS TEST VERIFIES, never bypassed.
"""
from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("testcontainers.postgres")

import sqlalchemy as sa
from testcontainers.postgres import PostgresContainer

from backend.case_lifecycle.migrate import apply_case_migrations
from backend.case_lifecycle.repository import PostgresCaseStore
from backend.case_lifecycle.schemas import PendingApplication, PendingRecommendation
from backend.case_lifecycle.states import CaseState
from backend.case_lifecycle.tests import fixtures as fx

pytestmark = pytest.mark.integration


def _docker_available() -> bool:
    try:
        import docker

        docker.from_env().ping()
        return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def case_engine():
    """One postgres:16 container with ONLY U24's sequence applied."""
    if not _docker_available():
        pytest.skip("Docker unavailable — case-lifecycle integration tests run in CI")
    with PostgresContainer("postgres:16") as pg:
        engine = sa.create_engine(pg.get_connection_url())
        apply_case_migrations(engine)          # ⚑ the PRODUCTION entry point (guard included)
        yield engine
        engine.dispose()


def test_the_migration_creates_both_tables(case_engine):
    inspector = sa.inspect(case_engine)
    tables = set(inspector.get_table_names())
    assert {"pending_application", "pending_recommendation"} <= tables


def test_the_migration_did_not_create_any_u15_table(case_engine):
    """Self-containment: U24's sequence alone, so U15's tables must be ABSENT."""
    tables = set(sa.inspect(case_engine).get_table_names())
    assert "audit_record" not in tables
    assert "applicant_profile_snapshot" not in tables


def test_bytea_round_trips_byte_identically(case_engine):
    store = PostgresCaseStore(case_engine)
    profile = fx.make_profile("case-persist-1")
    from backend.audit_store.canon_adapter import CanonSerAdapter

    raw = CanonSerAdapter.canonical_bytes(profile)
    digest = CanonSerAdapter.content_hash(profile)

    with store.atomic():
        store.put_application(
            PendingApplication(
                application_id="case-persist-1",
                state=CaseState.EVALUATED,
                profile_canonical=raw,
                profile_content_hash=digest,
            )
        )

    loaded = store.get_application("case-persist-1")
    assert loaded.profile_canonical == raw            # byte-identical
    assert CanonSerAdapter.content_hash(
        CanonSerAdapter.profile_from_canonical(loaded.profile_canonical)
    ) == digest


def test_the_scalar_stamps_round_trip(case_engine):
    store = PostgresCaseStore(case_engine)
    with store.atomic():
        store.put_application(
            PendingApplication(
                application_id="case-persist-2",
                state=CaseState.EVALUATED,
                profile_canonical=b"{}",
                profile_content_hash="h",
                rulebook_version="rb-1",
                engine_version="eng-1",
            )
        )
        store.put_recommendation(
            PendingRecommendation(
                recommendation_id="rec-persist-2",
                application_id="case-persist-2",
                memo_canonical=b"{}",
                memo_hash="mh",
                model_version="mv",
                engine_version="eng-1",
                rulebook_version="rb-1",
            )
        )

    app = store.get_application("case-persist-2")
    rec = store.get_recommendation("rec-persist-2")
    assert app.rulebook_version == "rb-1" and app.engine_version == "eng-1"
    assert rec.memo_hash == "mh" and rec.model_version == "mv"
    assert store.recommendation_for_application("case-persist-2").recommendation_id == "rec-persist-2"


def test_a_failed_transaction_writes_nothing(case_engine):
    """The real driver's both-or-neither, matching the tier-U fake's behaviour."""
    store = PostgresCaseStore(case_engine)
    with pytest.raises(RuntimeError):
        with store.atomic():
            store.put_application(
                PendingApplication(
                    application_id="case-persist-3",
                    state=CaseState.EVALUATED,
                    profile_canonical=b"{}",
                    profile_content_hash="h",
                )
            )
            raise RuntimeError("injected")
    assert store.get_application("case-persist-3") is None


def test_enumeration_agrees_with_the_tier_u_fake(case_engine):
    """⚑ ENUMERATE-1 (tier-I half) — the AUTHORIZED U24 REOPENING's list primitive.

    PERSIST-1's whole job is that the SQL shim and the in-memory fake agree on the SAME Protocol.
    The reopening added a method, so it gets the same treatment: real Postgres must return the
    ids it was given, sorted, exactly as ``InMemoryCaseStore.list_application_ids`` does.
    """
    store = PostgresCaseStore(case_engine)
    for application_id in ("case-enum-b", "case-enum-a"):
        with store.atomic():
            store.put_application(
                PendingApplication(
                    application_id=application_id,
                    state=CaseState.EVALUATED,
                    profile_canonical=b"{}",
                    profile_content_hash="h",
                )
            )

    ids = store.list_application_ids()
    assert {"case-enum-a", "case-enum-b"} <= set(ids)
    assert ids == sorted(ids), "the shim's ORDER BY must match the fake's sorted() order"

    fake = fx.InMemoryCaseStore()
    for application_id in ("case-enum-b", "case-enum-a"):
        with fake.atomic():
            fake.put_application(
                PendingApplication(
                    application_id=application_id,
                    state=CaseState.EVALUATED,
                    profile_canonical=b"{}",
                    profile_content_hash="h",
                )
            )
    assert fake.list_application_ids() == ["case-enum-a", "case-enum-b"]
