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

import os
import uuid
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import sqlalchemy as sa
from fastapi import Cookie, Depends, Header

from backend.app.errors import FORBIDDEN, UNAUTHENTICATED, WireError
from backend.app.offline_memo_double import OFFLINE_MODEL_VERSION, OfflineMemoLLMClient
from backend.app.outlier_canonical import quantize_outlier
from backend.app.outlier_composition import build_outlier_model
from backend.audit_store.audit_service import AuditService
from backend.audit_store.commit_service import DecisionCommitService
from backend.audit_store.pg_repository import PostgresAuditRepository
from backend.audit_store.seams import RBAC_COMMIT, SystemClock, UuidGenerator
from backend.auth_rbac.api_guard import ApiAuthGuard
from backend.auth_rbac.authorizer import AuthRBAC
from backend.auth_rbac.pg_repository import PostgresUserRoleRepository
from backend.auth_rbac.roles import READ_AUDIT, Role, to_role
from backend.authn.repository import PostgresCredentialStore, PostgresSessionStore
from backend.authn.service import AuthenticationService
from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.provider import PendingCommitContextProvider
from backend.case_lifecycle.repository import PostgresCaseStore
from backend.intake.pipeline import IntakePipeline
from backend.memo_agent_core.input_builder import MemoAgentInputBuilder
from backend.memo_agent_core.orchestrator import LangGraphOrchestrator
from backend.memo_agent_core.provider import GeminiAdapter
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader
from backend.secrets_config import get_settings

#: ⚑ SUPERSEDED 2026-07-25 (register #25 / WIRE1-Fold-5). Retained because the name is still
#: referenced by the historical record; it is NO LONGER READ by ``current_identity``. The stub
#: it named WAS authentication — any caller who knew a ``user_id`` was that user.
USER_ID_HEADER = "X-User-Id"

#: The session cookie. Opaque, server-side, revocable — never a JWT, never signed.
SESSION_COOKIE_NAME = "session"

#: ⚑ Behavioural switch, NOT a credential — so reading it from ``os.environ`` is not a SEC-3
#: violation, on the ``llm_client.py`` precedent (*"dependencies.py's rejection of os.environ
#: is scoped to credentials and secret material specifically"*). Reading it here also avoids
#: C-B: frozen ``Settings`` stays at exactly six fields.
#:
#: **FAIL-SAFE**: only the exact literal ``"false"`` disables ``Secure``. Absent, misspelt, or
#: any other value yields a Secure cookie, so a forgotten variable can never silently
#: downgrade production. Mirrors ``ALLOW_REAL_LLM_CALLS``'s exact-match rule, polarity flipped
#: to match the semantics.
SESSION_COOKIE_SECURE_ENV = "SESSION_COOKIE_SECURE"


def session_cookie_is_secure() -> bool:
    """``False`` only on an exact ``"false"``; safe by default."""
    return os.environ.get(SESSION_COOKIE_SECURE_ENV) != "false"


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


# --- U1 (intake) + the pipeline — the SUBMISSION surface behind R10/R11 (WIRE1-Fold-6) ---
#
# ⛔ **THIS REVERSES THE "NOTE what is DELIBERATELY ABSENT" ABOVE, AND DOES SO KNOWINGLY.** That
# note is preserved verbatim because it was true for R2-R5 and its reasoning still holds for
# them: no GET route may reach the pipeline. What changes is that R10/R11 are POSTs whose whole
# purpose is to call ``submit()`` and ``draft()``, so ``CasePipeline`` must be composed here.
# The invariant's SUBSTANCE survives — R4 is still side-effect-free — and the mechanical guard
# was narrowed to say exactly that (``test_no_write_route.py``, WIRE1-Fold-6 / Q9(a)).

#: The repo rulebook directory. ⚑ ``RulebookLoader`` takes this as a REQUIRED argument and has
#: no default; named here once, mirroring ``seed_demo_cases.rulebook_dir()``.
RULEBOOK_DIR = str(Path(__file__).resolve().parents[1] / "rules_engine" / "rulebook")
RULEBOOK_VERSION = "1.0.0"
ENGINE_VERSION = "composition-root-1"


class _NoDocumentParseWorker:
    """⛔ Refuses to parse. **The document path is NOT part of WIRE1-Fold-6** (Q2(a)).

    ⚑ Injecting a worker that RAISES rather than the real ``SubprocessParseWorker`` makes the
    fold's structured-only scope **structural instead of documentary**: if a future change lets a
    non-empty ``documents`` list reach intake, it fails loudly and by name here rather than
    silently spawning subprocesses from a request handler — six infrastructure costs (temp
    storage, PII retention, size limits, subprocess concurrency, Render's ephemeral filesystem,
    ``multipart/form-data``) that Q2(a) deliberately deferred to their own pass.
    """

    def parse(self, doc_type, source_path):
        raise NotImplementedError(
            "document parsing is not wired: WIRE1-Fold-6 accepts structured fields only"
        )


class _CompositionSeams:
    """U24's ``CaseSeams``, composed from the frozen units — the request-path counterpart of the
    seed script's ``_SeedSeams``.

    ⚑ Every unit here is REAL: ``rules_engine``'s deterministic engine and ``memo_agent_core``'s
    real ``LangGraphOrchestrator``. **The ONLY substitution is the LLM client** (Q5(a)), and the
    rules evaluation — the part that actually produces the recommendation — is genuine and
    LLM-free regardless, exactly as the deterministic-core architecture requires.
    """

    def __init__(self) -> None:
        loader = RulebookLoader(RULEBOOK_DIR)
        self._engine = RulesEngine(loader, engine_version=ENGINE_VERSION)
        self._builder = MemoAgentInputBuilder()
        self._orchestrator = LangGraphOrchestrator(
            GeminiAdapter(OfflineMemoLLMClient(), model=OFFLINE_MODEL_VERSION),
            rulebook=loader.load_rulebook(RULEBOOK_VERSION),
            model_version=OFFLINE_MODEL_VERSION,
        )

    def profile(self, raw: object) -> object:
        """⚑ PASS-THROUGH, and deliberately so. ``raw`` is already an ``ApplicantProfile`` here
        because **R10 runs intake in the handler** (Q8(a)) — it has to, so that a
        ``RejectedIntake`` can become a 400 without ever entering the pipeline. U24's seam is
        duck-typed at both ends (``profile(raw: object) -> object``), which is what lets an
        intake-backed submission satisfy it **with no U24 reopening at all**.
        """
        return raw

    def evaluate(self, profile: object) -> object:
        return self._engine.evaluate(profile, RULEBOOK_VERSION)

    def score_outlier(self, profile: object) -> Optional[object]:
        """Score the applicant against the committed corpus (WIRE1-Fold-6 stage 3).

        ⚑ **SUPERSEDED, preserved because it was true for the whole of stage 2**: *"``None`` for
        now — stage 3's job, not a stub standing in for something missing. A case drafted through
        R11 today carries ``outlier: null``, exactly as every case did before the outlier pass."*

        ⛔ **Returns a QUANTIZED PROJECTION, not the raw ``OutlierResult`` — barrier #5.**
        ``CanonSerAdapter.canonical_bytes`` **rejects IEEE float outright** (CON-DET-1), and every
        numeric field of ``OutlierResult`` is a float straight out of IsolationForest and SHAP.
        U24 serializes whatever this seam returns with exactly that adapter, so returning the raw
        result would make ``draft()`` RAISE before writing a row. Handing back the Decimal
        projection is what makes the score persistable **without reopening a single frozen
        unit** — ``CaseSeams.score_outlier`` is typed ``Optional[object]``, so U24's path is
        untouched.

        ⛔ **What this does NOT claim**: the projection guarantees the persisted REPRESENTATION
        round-trips at a named precision. It is **not** a claim that the ML computation is
        bit-for-bit reproducible across library versions — which is precisely why
        ``OUTLIER_MODEL_VERSION`` bundles the sklearn version.

        ⚑ The model is resolved **at call time, not in ``__init__``**, so constructing the seams
        (which happens on the first *submission*) still fits nothing. The ~2.6 s lands on the
        first *drafting* request, which is the only one that needs it.
        """
        return quantize_outlier(outlier_model().score(profile))

    def draft_memo(self, profile: object, report: object, thinking_mode: object) -> Optional[object]:
        return self._orchestrator.run(
            self._builder.build(applicant_profile=profile, rule_report=report)
        )


def _recommendation_id_factory(application_id: str) -> str:
    """⚑ Mirrors the seed script's factory. ``audit_store``'s frozen ``IdGenerator.new_id()``
    takes no argument, so it cannot key by application; a uuid4 suffix keeps ids unique.

    ⚠️ **Deterministic is not chronological** (register #27's recorded limit): the random suffix
    means ``recommendation_for_application``'s ``ORDER BY`` returns a STABLE row, not the newest.
    """
    return f"REC-{application_id}-{uuid.uuid4().hex[:8]}"


@lru_cache(maxsize=1)
def outlier_model():
    """⚑ **THE FOURTH ``lru_cache`` PROVIDER** — identical in shape to the three engines above,
    which is the whole argument for Q4(a): it introduces **no new pattern and no new artifact
    type** (Q4(c)'s persisted pickle would have added a build step, a versioning question, and a
    staleness risk against ``corpus_version`` that would silently break score replay).

    ⛔ **LAZY, AND THE LAZINESS IS LOAD-BEARING** (ambiguity-check Fold C). The ~2.6 s fit happens
    on FIRST USE — the first case actually drafted — not at import and not at ``create_app()``.
    An eager fit (Q4(b)) would cost ~2.6 s x **every** ``create_app()``, of which the test suite
    alone performs many. Pinned by ``test_create_app_does_not_fit_the_model``.

    ⚠️ Two consequences accepted openly at the Q4(a) gate: the first drafting request after a cold
    start is slow, and the deployed backend **must** carry ``corpus/`` — see
    ``outlier_composition.CORPUS_ON_RENDER``, where that stopped being a carried question.
    """
    return build_outlier_model()


@lru_cache(maxsize=1)
def case_seams() -> _CompositionSeams:
    """⚑ LAZY + CACHED, the established idiom (``app_engine``/``reader_engine``/``writer_engine``).

    The rulebook is loaded from disk and the LangGraph orchestrator is built ONCE per process,
    not per request. **The laziness is load-bearing, not incidental**: an eager build would move
    this cost onto every ``create_app()``, including the ones in the test suite.
    """
    return _CompositionSeams()


def get_intake_pipeline() -> IntakePipeline:
    """U1's pipeline — ⚑ **wired into a reachable path for the FIRST time in this build.**

    The sanitizer, the PII guard and the SEC-2 validation gate all run. Only the parse step has
    nothing to parse (Q2(a)), which is why the worker above refuses rather than exists.
    """
    return IntakePipeline(parse_worker=_NoDocumentParseWorker())


def get_case_pipeline(store: PostgresCaseStore = Depends(get_case_store)) -> CasePipeline:
    """U24's pipeline over the injected store — R10's ``submit()`` and R11's ``draft()``."""
    return CasePipeline(store, case_seams(), _recommendation_id_factory)


# --- authn (register #25 / PER-4) — credential + session construction --------------------
# ⚑ Both stores bind to the OWNER engine. ``0003_auth.sql`` grants nothing (it applies after
# ``0002_grants.sql``), so ``user_credential``/``user_session`` are owner-only by
# construction — the same posture ``app_user`` has, ratified as CORE-RATIONALE-20.

def get_auth_service() -> AuthenticationService:
    """authn's service — the ONLY place a credential is verified or a session issued."""
    engine = app_engine()
    return AuthenticationService(
        credentials=PostgresCredentialStore(engine),
        sessions=PostgresSessionStore(engine),
    )


# --- identity + authorization ----------------------------------------------------------

def current_identity(
    session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    repository=Depends(get_user_role_repository),
    auth: AuthenticationService = Depends(get_auth_service),
) -> Identity:
    """Resolve the SESSION COOKIE to an ``Identity``, fail-closing to 401.

    ⚑ **REPLACES the ``X-User-Id`` stub (register #25 / PER-4 / WIRE1-Fold-5).** The header
    is no longer read: it *was* authentication, in the sense that any caller who knew a
    ``user_id`` was that user. The caller now proves identity by presenting a session that
    this server issued against an Argon2id-verified credential.

    Missing/blank cookie -> 401. Unknown, expired or revoked session -> 401 (checked
    server-side on EVERY request, which is what makes logout and role changes immediate).
    Unknown user, or a blank/non-canonical role -> 401.

    ⚑ **Unchanged and still load-bearing**: the ROLE is never taken from the request — it is
    read from ``app_user`` through auth-rbac's own repository, and ``to_role`` is the frozen
    TOTAL canonicalizer that fail-closes. Only the *identity* mechanism changed.

    ⚑ **R1's response shape is untouched** (WIRE-1 §6, Q6a): ``{user_id, role}``.
    """
    if session is None or not session.strip():
        raise WireError(UNAUTHENTICATED, "Authentication is required.")
    user_id = auth.resolve(session)
    if user_id is None:
        raise WireError(UNAUTHENTICATED, "Authentication is required.")
    role = to_role(repository.get_role(user_id))
    if role is None:
        raise WireError(UNAUTHENTICATED, "Authentication is required.")
    return Identity(user_id=user_id, role=role)


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


def require_underwriter(
    identity: Identity = Depends(current_identity),
    guard: ApiAuthGuard = Depends(get_auth_guard),
) -> Identity:
    """Enforce ``underwriter``-only on R10/R11 (WIRE1-Fold-6, Q10(a)).

    ⚑ **Deliberately SEPARATE from ``require_commit`` despite checking the same action**, on
    that dependency's own recorded reasoning: a route's role gate should be able to move without
    dragging unrelated routes with it. Submission and commit are different operations that
    happen to share a permission today; fusing them would make a future divergence an edit to a
    shared guard rather than to the route that changed.

    ⚠️ **RECORDED COST, not an oversight.** The action checked is ``RBAC_COMMIT``, whose value is
    ``"commit"`` — so one action now gates three operations, only one of which commits. The
    rbac_action vocabulary and ``PERMISSION_MATRIX`` live in the **frozen** ``auth_rbac`` unit, so
    minting a distinct ``submit``/``draft`` action needs its own authorized reopening. Reusing
    the underwriter-only slice was the option that reopened nothing (Q7(a)); the semantic stretch
    is disclosed in WIRE-1 §3 and §7.3 rather than hidden here.

    ⚑ **Ordering matters and is guaranteed by construction.** FastAPI resolves ``Depends(...)``
    before the handler body runs, so this fires **before any intake code executes**: a wrong-role
    caller never reaches intake, so no work is wasted and **no rejection detail — field names,
    missing items — can leak to a caller with no right to it**. Pinned by a spy, not by timing.
    """
    if not guard.check(identity.user_id, RBAC_COMMIT):
        raise WireError(FORBIDDEN, "You do not have permission to submit or draft an application.")
    return identity
