"""Composition-root dependency providers — the ONLY place frozen units are constructed.

Composition only: every object here is a frozen unit's own class, constructed and injected.
No domain logic, no re-implementation, no unit edited.

THREE-ENGINE LEAST-PRIVILEGE BINDING (derived from the frozen ``0002_grants.sql``, not chosen):
``audit_reader``/``audit_writer`` hold grants on ``audit_record`` + ``applicant_profile_snapshot``
ONLY — **neither can read ``app_user``**. Therefore:

    R1     (app_user role read)   -> DATABASE_URL      engine (the owner; no audit role may read app_user)
    R2-R5  (pending-state reads)  -> DATABASE_URL      engine (see the grants NOTE below)
    R6/R7  (audit reads)          -> AUDIT_READER_URL  engine (SELECT-only; the SEC-4 read-only role)
    R5     (the audit WRITE)      -> AUDIT_WRITER_URL  engine (the ONLY write path in the app)

⚑ **UPDATED BY THE SCOPE B WIRING PASS.** Scope A constructed no writer engine because it wired
no write path. **R5 is now wired**, so ``AUDIT_WRITER_URL`` IS read — in ``writer_engine()``,
**exactly once, and nowhere else**. The guarantee this package now makes is not "no writes exist"
(false by design) but **"every write goes through the frozen ``DecisionCommitService``"**, whose
CON-BR4 gate and independent authz re-check run INSIDE ``commit()``. Asserted in
``tests/test_no_write_route.py``.

⚑ **RESOLVED (register #20, DISCHARGED) — the pending tables are DELIBERATELY owner-only least
privilege.** U24's ``0001_case_lifecycle.sql`` grants no audit role on ``pending_application``/
``pending_recommendation``, so they are owner-only, which is why the case store binds to the OWNER
engine above. Ratified as correct: the pending tables hold pre-commit drafts; ``audit_reader`` is
scoped to the committed trail (R6/R7) and ``audit_writer`` only writes committed records through the
frozen service — neither has any wired reason to reach pre-commit state, and no caller reaches these
tables through a non-owner engine. It is the same owner-only posture the build already applies to
``app_user``. No grant is invented (register #20 resolution; was Scope B wiring, Q8a's open item).

AUTH HANDSHAKE (Decision 2 / Q4-A): a STUB ``X-User-Id`` header, resolved against ``app_user``.
This is the concrete stand-in for WIRE-1 §6/A6's "abstract seam, deferred" — deliberately NOT
``Authorization: Bearer``, which would imply a token semantic (validation, issuer, expiry) that
does not exist. Replacing this with the real OIDC handshake touches only this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import sqlalchemy as sa
from fastapi import Depends, Header

from backend.app.errors import FORBIDDEN, UNAUTHENTICATED, WireError
from backend.audit_store.audit_service import AuditService
from backend.audit_store.commit_service import DecisionCommitService
from backend.audit_store.pg_repository import PostgresAuditRepository
from backend.audit_store.seams import RBAC_COMMIT, SystemClock, UuidGenerator
from backend.auth_rbac.api_guard import ApiAuthGuard
from backend.auth_rbac.authorizer import AuthRBAC
from backend.auth_rbac.pg_repository import PostgresUserRoleRepository
from backend.auth_rbac.roles import READ_AUDIT, Role, to_role
from backend.case_lifecycle.provider import PendingCommitContextProvider
from backend.case_lifecycle.repository import PostgresCaseStore
from backend.secrets_config import get_settings

#: The stub identity header (Q4-A).
USER_ID_HEADER = "X-User-Id"


@dataclass(frozen=True)
class Identity:
    """The authenticated caller. ``role`` is the canonical frozen enum, never a raw string."""
    user_id: str
    role: Role


# --- engines (lazy + cached; Settings is read at REQUEST time, never at import) ---------
# Settings is fail-closed with all six fields required (frozen secrets-config). Scope A wires
# no LLM, so GEMINI_API_KEY is required-but-unused: a dummy value satisfies it (Q5-A). Reading
# os.environ directly instead would bypass secrets-config's SEC-3 single-source control, and
# making the field optional would edit a frozen unit — both rejected.

@lru_cache(maxsize=1)
def app_engine() -> sa.Engine:
    """The DATABASE_URL (owner) engine — the ONLY engine that may read ``app_user``."""
    return sa.create_engine(get_settings().DATABASE_URL)


@lru_cache(maxsize=1)
def reader_engine() -> sa.Engine:
    """The AUDIT_READER_URL (SELECT-only) engine — audit reads, least privilege."""
    return sa.create_engine(get_settings().AUDIT_READER_URL)


@lru_cache(maxsize=1)
def writer_engine() -> sa.Engine:
    """The AUDIT_WRITER_URL engine — **the ONLY write path in the application** (R5).

    ⚑ Constructed **exactly once and only here** (Scope B wiring, Q6b). Lazy like its two
    siblings, so it is built only when R5 is first exercised: ``create_app()`` still constructs
    no engine and reads no setting, and importing this module still requires no environment.
    """
    return sa.create_engine(get_settings().AUDIT_WRITER_URL)


# --- frozen-unit construction (overridden in tests with each unit's own in-memory fake) --

def get_user_role_repository():
    """auth-rbac's C5 role read model, on the owner engine (app_user is not audit-role-readable)."""
    return PostgresUserRoleRepository(app_engine())


def get_audit_service() -> AuditService:
    """audit-store's read service, on the READER engine (SEC-4 least privilege)."""
    return AuditService(PostgresAuditRepository(reader_engine()))


def get_auth_guard(repository=Depends(get_user_role_repository)) -> ApiAuthGuard:
    """auth-rbac's API guard over its single AuthRBAC policy. The server is the real gate."""
    return ApiAuthGuard(AuthRBAC(repository))


# --- U24 (case-lifecycle) construction — the pending-state surface behind R2-R5 ----------
# ⚑ NOTE what is DELIBERATELY ABSENT: ``CasePipeline`` is NOT constructed here (Q3-D). None of
# R2/R3/R4/R5 calls ``submit()`` or ``draft()`` — the four routes need only the store, the pure
# projection, and the commit-context provider. Keeping the pipeline out means the five-unit
# LLM-bearing composition never enters the request path at all, which is what makes R4
# side-effect-free BY CONSTRUCTION rather than by discipline (BR-CASE-4 / TRIGGER-1). The
# pipeline lives in the out-of-band seed script (``backend/scripts/seed_demo_cases.py``).

def get_case_store() -> PostgresCaseStore:
    """U24's pending-state store, on the OWNER engine (see the grants NOTE in the header)."""
    return PostgresCaseStore(app_engine())


def get_commit_context_provider(
    store: PostgresCaseStore = Depends(get_case_store),
) -> PendingCommitContextProvider:
    """U24's REAL ``CommitContextProvider`` — the frozen Protocol's first production impl.

    ⚑ Supplies **assembly inputs only**. It performs no authz and no write; its return type is
    ``CommitContext``, so *"the provider committed something"* is unrepresentable.
    """
    return PendingCommitContextProvider(store)


def get_commit_service(
    provider: PendingCommitContextProvider = Depends(get_commit_context_provider),
    repository=Depends(get_user_role_repository),
) -> DecisionCommitService:
    """The FROZEN commit service — composed, never re-implemented (Q5-A).

    ⚑ The CON-BR4 gate and the independent ``RBAC_COMMIT`` re-check run **inside** ``commit()``.
    The route cannot bypass them. ``UuidGenerator``/``SystemClock`` are audit-store's own
    PRODUCTION seam implementations (verified at the Scope B ambiguity-check — neither is a
    test fake).
    """
    return DecisionCommitService(
        repository=PostgresAuditRepository(writer_engine()),
        context_provider=provider,
        authorizer=AuthRBAC(repository),
        id_generator=UuidGenerator(),
        clock=SystemClock(),
    )


# --- identity + authorization ----------------------------------------------------------

def current_identity(
    x_user_id: str | None = Header(default=None, alias=USER_ID_HEADER),
    repository=Depends(get_user_role_repository),
) -> Identity:
    """Resolve the stub header to an ``Identity``, fail-closing to 401 (Decision 2 / Q4-A).

    Missing/blank header -> 401. Unknown user, or a role that is blank/non-canonical -> 401
    (``to_role`` is the frozen TOTAL canonicalizer and fail-closes to None). No role value is
    ever trusted from the header itself — only the user id is, and the ROLE comes from app_user.
    """
    if x_user_id is None or not x_user_id.strip():
        raise WireError(UNAUTHENTICATED, "Authentication is required.")
    role = to_role(repository.get_role(x_user_id))
    if role is None:
        raise WireError(UNAUTHENTICATED, "Authentication is required.")
    return Identity(user_id=x_user_id, role=role)


def require_read_audit(
    identity: Identity = Depends(current_identity),
    guard: ApiAuthGuard = Depends(get_auth_guard),
) -> Identity:
    """Enforce READ_AUDIT on the audit read surface (R6/R7) — **Q1-B**.

    This APPLIES the frozen ``PERMISSION_MATRIX`` verbatim rather than deciding to override it:
    auth-rbac is the single-sourced RBAC authority and the server is always the real gate.
    underwriter + auditor pass; **admin -> 403**.

    ⚠️ RECORDED DIVERGENCE (unresolved, deliberately carried — plan §6.6): WIRE-1 §3 marks
    R6/R7 "authenticated" (ANY role), while PERMISSION_MATRIX excludes admin from READ_AUDIT.
    For an admin caller the two FROZEN artifacts disagree (200 vs 403). This is TWO-SIDED, not a
    one-sided oversight: ui-history's frozen BR-HIST-7 sided with WIRE-1 on the client (it
    declined `RoleGate can="read"` precisely because it "would cosmetically exclude admin"). This
    pass does NOT resolve the divergence and must not be read as having done so — reconciliation
    (Option C: enforce READ_AUDIT *and* amend WIRE-1 §3's wording) is future deliberate work.
    WIRE-1 is NOT amended here.
    """
    if not guard.check(identity.user_id, READ_AUDIT):
        raise WireError(FORBIDDEN, "You do not have permission to read the audit trail.")
    return identity


def require_commit(
    identity: Identity = Depends(current_identity),
    guard: ApiAuthGuard = Depends(get_auth_guard),
) -> Identity:
    """Enforce ``RBAC_COMMIT`` on R5 — **DEFENCE IN DEPTH, never the authority** (Q6a).

    ⚑ This is deliberately NOT the enforcer. The frozen ``DecisionCommitService.commit()`` runs
    its OWN independent ``authorize(underwriter_id, RBAC_COMMIT)`` re-check regardless of what
    this layer did (AUTHZ-1), and that re-check is the real gate. This guard exists so an
    unauthorized caller fails FAST with the contract's 403 rather than travelling deeper —
    exactly the pattern R6/R7 already use (guard at the layer *and* rely on the service).

    ⚑ Deliberately SEPARATE from ``require_read_audit``: R5 is ``underwriter``-only per WIRE-1
    §3, a different permission from READ_AUDIT, and reusing that dependency would silently
    propagate the recorded, still-unresolved Q1-B divergence onto a route it has nothing to do
    with. WIRE-1 §3 and PERMISSION_MATRIX AGREE on R5 (underwriter only) — there is no
    divergence here, and this pass introduces none.
    """
    if not guard.check(identity.user_id, RBAC_COMMIT):
        raise WireError(FORBIDDEN, "You do not have permission to commit a decision.")
    return identity
