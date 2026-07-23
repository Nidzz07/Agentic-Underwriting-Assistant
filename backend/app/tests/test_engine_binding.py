"""INT-ENGINE-1 — the two-engine least-privilege binding, asserted WITHOUT a live database.

Derived from the frozen ``0002_grants.sql`` (not chosen): ``audit_reader``/``audit_writer`` hold
grants on ``audit_record`` + ``applicant_profile_snapshot`` ONLY — **neither can read
``app_user``**. Therefore R1 must use the DATABASE_URL (owner) engine and R6/R7 the
AUDIT_READER_URL (SELECT-only) engine. Binding the wrong engine would fail at runtime for R1 and
would silently over-privilege the audit reads.

This is verified structurally: ``sa.create_engine`` is intercepted, so no server is needed —
the same reason it survives without Docker, like every other unit's tier-U tests.
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa

from backend.app import dependencies as deps

APP_URL = "postgresql://owner@localhost/app"
READER_URL = "postgresql://audit_reader@localhost/app"
WRITER_URL = "postgresql://audit_writer@localhost/app"


class FakeSettings:
    DATABASE_URL = APP_URL
    AUDIT_READER_URL = READER_URL
    AUDIT_WRITER_URL = WRITER_URL
    AUDIT_WRITER_PASSWORD = "unused"
    AUDIT_READER_PASSWORD = "unused"
    GEMINI_API_KEY = "unused-in-scope-a"   # Q5-A: required by frozen Settings, never used here


@pytest.fixture
def created_urls(monkeypatch):
    """Intercept engine creation; record every URL the app asks for."""
    urls: list[str] = []

    def fake_create_engine(url, *args, **kwargs):
        urls.append(url)
        return object()   # never connected to

    deps.app_engine.cache_clear()
    deps.reader_engine.cache_clear()
    deps.writer_engine.cache_clear()
    monkeypatch.setattr(deps, "get_settings", lambda: FakeSettings())
    monkeypatch.setattr(sa, "create_engine", fake_create_engine)
    yield urls
    deps.app_engine.cache_clear()
    deps.reader_engine.cache_clear()
    deps.writer_engine.cache_clear()


class TestEachEngineBindsItsIntendedUrl:
    def test_app_engine_binds_database_url(self, created_urls):
        deps.app_engine()
        assert created_urls == [APP_URL]

    def test_reader_engine_binds_audit_reader_url(self, created_urls):
        deps.reader_engine()
        assert created_urls == [READER_URL]

    def test_engines_are_cached_not_rebuilt_per_request(self, created_urls):
        deps.app_engine(); deps.app_engine(); deps.reader_engine(); deps.reader_engine()
        assert created_urls == [APP_URL, READER_URL]


class TestRouteToEngineBinding:
    def test_r1s_role_repository_uses_the_owner_engine(self, created_urls):
        # app_user is readable ONLY by the owner — no audit role has a grant on it.
        deps.get_user_role_repository()
        assert created_urls == [APP_URL]

    def test_r6_r7s_audit_service_uses_the_reader_engine(self, created_urls):
        # least privilege: the audit read surface gets the SELECT-only role (SEC-4).
        deps.get_audit_service()
        assert created_urls == [READER_URL]

    def test_the_two_surfaces_never_share_an_engine(self, created_urls):
        deps.get_user_role_repository()
        deps.get_audit_service()
        assert created_urls == [APP_URL, READER_URL]
        assert len(set(created_urls)) == 2


class TestTheWriterUrlIsReadExactlyOnceAndOnlyForR5:
    """⚑ REVISED BY THE SCOPE B WIRING PASS.

    Previously ``TestTheWriterUrlIsNeverRead`` — true under Scope A, where no write path existed.
    R5 is now wired, so the writer IS constructed. The guarantee narrows from *never* to
    **exactly once, only for the commit path, and never by a read provider**.
    """

    def test_no_read_provider_ever_constructs_the_writer(self, created_urls):
        """The R1/R6/R7 surface must still never touch the writer URL."""
        deps.get_user_role_repository()
        deps.get_audit_service()
        deps.app_engine()
        deps.reader_engine()
        assert WRITER_URL not in created_urls

    def test_the_pending_read_store_uses_the_owner_engine_not_the_writer(self, created_urls):
        """⚑ R2/R3/R4 read pending state on the OWNER engine.

        U24's migration grants no audit role on the pending tables, so the audit reader cannot
        see them — the same derived-not-chosen reasoning that binds R1 to the owner engine.
        """
        deps.get_case_store()
        assert created_urls == [APP_URL]
        assert WRITER_URL not in created_urls
        assert READER_URL not in created_urls

    def test_the_commit_service_constructs_the_writer_exactly_once(self, created_urls):
        store = deps.get_case_store()
        provider = deps.get_commit_context_provider(store)
        deps.get_commit_service(provider, deps.get_user_role_repository())
        assert created_urls.count(WRITER_URL) == 1

    def test_the_writer_engine_is_cached_not_rebuilt_per_request(self, created_urls):
        deps.writer_engine()
        deps.writer_engine()
        deps.writer_engine()
        assert created_urls.count(WRITER_URL) == 1

    def test_the_writer_is_lazy_and_unbuilt_until_r5_is_exercised(self, created_urls):
        """⚑ Importing the app and serving reads must construct NO writer (Q6b).

        This is what keeps ``create_app()`` environment-free: the writer appears only when a
        commit actually happens.
        """
        from backend.app.main import create_app

        create_app()
        deps.get_audit_service()
        deps.get_case_store()
        assert WRITER_URL not in created_urls

    def test_the_provider_is_u24s_real_one_over_the_owner_engine(self, created_urls):
        """The commit CONTEXT is read from pending state, never from the audit database."""
        from backend.case_lifecycle.provider import PendingCommitContextProvider

        provider = deps.get_commit_context_provider(deps.get_case_store())
        assert isinstance(provider, PendingCommitContextProvider)
        assert created_urls == [APP_URL]


class TestSettingsIsTheSingleSourceOfConfiguration:
    def test_the_app_reads_urls_only_through_secrets_config(self, created_urls):
        # SEC-3: no os.environ read here. Swapping get_settings swapped EVERY url the app used —
        # which would be impossible if any module bypassed secrets-config.
        deps.app_engine()
        deps.reader_engine()
        deps.writer_engine()
        assert created_urls == [APP_URL, READER_URL, WRITER_URL]

    def test_all_three_engines_are_distinct(self, created_urls):
        deps.app_engine()
        deps.reader_engine()
        deps.writer_engine()
        assert len(set(created_urls)) == 3
