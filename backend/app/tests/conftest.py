"""Composition-root test fixtures.

The app is exercised through FastAPI's ``TestClient`` with each frozen unit's OWN in-memory
fake substituted for its Postgres repository — ``InMemoryAuditRepository`` (audit-store) and
``InMemoryUserRoleRepository`` (auth-rbac). Both are the units' own published test doubles, so
the SERVICES under test are the real frozen ones; only the storage adapter is swapped.

This is the project's established tier-U convention: no Docker, no live database, nothing
skipped. The Postgres engine BINDING (which url backs which route) is asserted separately and
structurally in ``test_engine_binding.py`` — it needs no live server to verify.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from datetime import datetime, timezone

from backend.app.dependencies import (
    get_audit_service,
    get_case_store,
    get_commit_service,
    get_user_role_repository,
)
from backend.app.dependencies import SESSION_COOKIE_NAME, get_auth_service
from backend.app.main import create_app
from backend.authn.constants import SESSION_TTL
from backend.authn.service import AuthenticationService, session_id_for
from backend.authn.store import InMemoryCredentialStore, InMemorySessionStore, SessionRecord
from backend.app.tests.factories import (
    InMemoryCaseStore,
    make_case,
    make_override_record,
    make_pending_recommendation,
    make_record,
)
from backend.audit_store.audit_service import AuditService
from backend.audit_store.commit_service import DecisionCommitService
from backend.audit_store.repository import InMemoryAuditRepository
from backend.audit_store.seams import FixedClock, SequenceIdGenerator
from backend.auth_rbac.authorizer import AuthRBAC
from backend.auth_rbac.repository import InMemoryUserRoleRepository
from backend.case_lifecycle.provider import PendingCommitContextProvider
from backend.case_lifecycle.states import CaseState

#: The seeded app_user table: one user per canonical role + one unknown-role user.
USERS = {
    "UW-1": "underwriter",
    "AUD-1": "auditor",
    "ADM-1": "admin",
    "GHOST-1": "",  # present but role blank -> to_role fail-closes -> 401
}

#: ⚑ MIGRATED 2026-07-25 (register #25 / WIRE1-Fold-5). These were ``{"X-User-Id": "..."}``
#: until ``current_identity`` stopped trusting that header. They remain **dicts passed as
#: ``headers=``**, so every existing call site works verbatim — only the contents changed,
#: from a forgeable id to a real session cookie. An explicit ``Cookie`` header is simply how
#: you send a cookie.
#:
#: ⚑ **Why sessions are SEEDED rather than obtained by calling R8.** (1) Argon2id is
#: deliberately slow, and paying that cost in ~98 route tests would buy nothing — they test
#: ROUTING, not the handshake. (2) It would couple every route test to R8, so one login
#: regression would cascade into ~98 unrelated failures. (3) The real login path IS proven
#: end-to-end, once, in ``test_auth_routes.py``. This is the same seam the fixtures already
#: use for ``app_user`` via ``InMemoryUserRoleRepository(USERS)``.
#: ⚑ Includes ORPHAN-1, which deliberately has NO ``app_user`` row. It is how the suite tests
#: the distinction the header stub used to test with an unknown id: a session that RESOLVES
#: but whose user cannot be found is a failure to AUTHENTICATE (401), never to authorize (403).
SESSION_TOKENS = {
    **{user_id: f"test-session-{user_id}" for user_id in USERS},
    "ORPHAN-1": "test-session-ORPHAN-1",
}

UNDERWRITER = {"Cookie": f"{SESSION_COOKIE_NAME}={SESSION_TOKENS['UW-1']}"}
AUDITOR = {"Cookie": f"{SESSION_COOKIE_NAME}={SESSION_TOKENS['AUD-1']}"}
ADMIN = {"Cookie": f"{SESSION_COOKIE_NAME}={SESSION_TOKENS['ADM-1']}"}

#: A live session for a user whose ``app_user.role`` is BLANK — ``to_role`` fail-closes to 401.
#: ⚑ This is what the GHOST-1 seed exists for; without a cookie constant it would be dead code.
GHOST = {"Cookie": f"{SESSION_COOKIE_NAME}={SESSION_TOKENS['GHOST-1']}"}

#: A live session whose user has NO ``app_user`` row at all.
ORPHAN = {"Cookie": f"{SESSION_COOKIE_NAME}={SESSION_TOKENS['ORPHAN-1']}"}


def seeded_auth_service() -> AuthenticationService:
    """An AuthenticationService with one live session per seeded user.

    ⚑ ``GHOST-1`` gets a session too, deliberately: its test asserts that a **blank role**
    fail-closes to 401. If it had no session it would fail at session lookup instead, and the
    test would silently stop testing what it was written to test.
    """
    sessions = InMemorySessionStore()
    now = datetime.now(timezone.utc)
    for user_id, token in SESSION_TOKENS.items():
        sessions.create(SessionRecord(
            session_id=session_id_for(token), user_id=user_id,
            created_at=now, expires_at=now + SESSION_TTL, revoked_at=None,
        ))
    return AuthenticationService(credentials=InMemoryCredentialStore(), sessions=sessions)


@pytest.fixture
def records():
    """Three synthetic records: two approve + one override, ids DEC-1..DEC-3."""
    return [make_record(1), make_override_record(2), make_record(3)]


@pytest.fixture
def audit_repository(records):
    repository = InMemoryAuditRepository()
    # insert() must run inside atomic() (the fake mirrors audit-store's ATOMIC-1 contract).
    with repository.atomic():
        for record in records:
            repository.insert(record)
    return repository


@pytest.fixture
def client(audit_repository):
    """A TestClient over the REAL app with in-memory storage adapters injected."""
    app = create_app()
    app.dependency_overrides[get_auth_service] = seeded_auth_service
    app.dependency_overrides[get_user_role_repository] = lambda: InMemoryUserRoleRepository(dict(USERS))
    app.dependency_overrides[get_audit_service] = lambda: AuditService(audit_repository)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def empty_client():
    """A TestClient whose audit store is EMPTY — the empty-page / not-found paths."""
    app = create_app()
    app.dependency_overrides[get_auth_service] = seeded_auth_service
    app.dependency_overrides[get_user_role_repository] = lambda: InMemoryUserRoleRepository(dict(USERS))
    app.dependency_overrides[get_audit_service] = lambda: AuditService(InMemoryAuditRepository())
    with TestClient(app) as test_client:
        yield test_client


# --- R2-R5 (Scope B wiring pass) ---------------------------------------------------------
# The pending-state routes get the same treatment as the audit routes above: U24's REAL objects
# (PendingCommitContextProvider) and the REAL frozen DecisionCommitService are exercised; only
# the STORAGE adapters are swapped for in-memory ones. No behaviour under test is faked.

@pytest.fixture
def case_store():
    """A drafted case + its pending recommendation, plus a second case still ``evaluated``."""
    return InMemoryCaseStore().seed(
        make_case("APP-1", state=CaseState.DRAFTED),
        make_pending_recommendation("REC-1", "APP-1"),
        make_case("APP-2", state=CaseState.EVALUATED),
    )


@pytest.fixture
def commit_repository():
    """The audit repository R5 writes into — in-memory, so no writer engine is constructed."""
    return InMemoryAuditRepository()


@pytest.fixture
def wired_client(audit_repository, case_store, commit_repository):
    """A TestClient with ALL SEVEN routes live.

    ⚑ The commit service here is the REAL frozen ``DecisionCommitService`` over U24's REAL
    ``PendingCommitContextProvider`` — the CON-BR4 gate and the authz re-check genuinely run.
    Only the two repositories are in-memory.
    """
    role_repository = InMemoryUserRoleRepository(dict(USERS))
    # ⚑ ONE generator for the LIFETIME OF THE CLIENT, not one per request (register #19).
    # Constructing it inside the lambda gave every request a fresh sequence, so every commit
    # produced decision_id "DEC-1" and the in-memory repository — which keys by decision_id —
    # SILENTLY OVERWROTE the previous row. A test asserting "only one AuditRecord exists" would
    # then have passed even while duplicates were genuinely being written: vacuous for exactly
    # the reason register #19 exists. Hoisting it makes ids distinct (DEC-1, DEC-2, …) so the
    # duplicate-write assertion can actually fail. First commit in each test is still "DEC-1" —
    # the fixture is function-scoped — so existing decision_id assertions are unaffected.
    id_generator = SequenceIdGenerator()
    app = create_app()
    app.dependency_overrides[get_auth_service] = seeded_auth_service
    app.dependency_overrides[get_user_role_repository] = lambda: role_repository
    app.dependency_overrides[get_audit_service] = lambda: AuditService(audit_repository)
    app.dependency_overrides[get_case_store] = lambda: case_store
    app.dependency_overrides[get_commit_service] = lambda: DecisionCommitService(
        repository=commit_repository,
        context_provider=PendingCommitContextProvider(case_store),
        authorizer=AuthRBAC(role_repository),
        id_generator=id_generator,
        clock=FixedClock(datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
    )
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def empty_case_client(audit_repository):
    """A TestClient whose PENDING store is empty — R2's empty page, R3/R4's 404."""
    app = create_app()
    app.dependency_overrides[get_auth_service] = seeded_auth_service
    app.dependency_overrides[get_user_role_repository] = lambda: InMemoryUserRoleRepository(dict(USERS))
    app.dependency_overrides[get_audit_service] = lambda: AuditService(audit_repository)
    app.dependency_overrides[get_case_store] = lambda: InMemoryCaseStore()
    with TestClient(app) as test_client:
        yield test_client
