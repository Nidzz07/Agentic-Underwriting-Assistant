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
from backend.app.intake_telemetry import build_intake_telemetry
from backend.app.offline_memo_double import OFFLINE_MODEL_VERSION, OfflineMemoLLMClient
from backend.app.ollama_client import build_ollama_client
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
from backend.intake.parser import SubprocessParseWorker
from backend.intake.pipeline import IntakePipeline
from backend.memo_agent_core.input_builder import MemoAgentInputBuilder
from backend.memo_agent_core.orchestrator import LangGraphOrchestrator
from backend.memo_agent_core.provider import GeminiAdapter
from backend.memo_agent_core.schemas import ThinkingMode
# ⛔ THE FIRST IMPORT OF ``memo_extensions`` FROM ``backend/app/`` (live-llm-drafting, G1).
# ⚑ It is NOT the first PRODUCTION import of memo_extensions — ``case_lifecycle/pipeline.py:38``
# already imports ``borderline_router`` and calls it on every draft (``:184``). memo_extensions is
# absent from ``FROZEN_UNITS`` and no pre-existing guard forbade this; the gate was discipline, and
# ``_MEMO_EXTENSIONS_IMPORT_MODULES_FROM_APP`` exists so the NEXT such import meets an assertion.
from backend.memo_extensions.provider_showcase import OllamaAdapter
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


#: ⚑ The memo provider selector. Behavioural switch, **NOT a credential** — so reading it from
#: ``os.environ`` is not a SEC-3 violation, on the same reasoning as ``SESSION_COOKIE_SECURE_ENV``
#: directly above and ``llm_client.py``'s ``ALLOW_REAL_LLM_CALLS``. Reading it here also keeps
#: frozen ``Settings`` at exactly six fields — no ``secrets_config`` reopening (Q3-A).
#:
#: ⛔ **FAIL-SAFE, AND THE POLARITY IS THE WHOLE POINT.** Only the exact literal ``"ollama"``
#: selects the live provider. Absent, misspelt, differently-cased or any other value yields the
#: **offline double** — so a forgotten or fat-fingered variable can never silently put a real model
#: in front of a user. Mirrors ``SESSION_COOKIE_SECURE``'s exact-match rule, polarity chosen to
#: match the semantics.
#:
#: ⚑ **This is ALSO how Q9's opt-in decision is enforced.** Ollama is the SHOWCASE provider and is
#: exempt from the memo-quality gates (groundedness/promptfoo) by design — see
#: ``llm_judge/pipeline.py``'s ``IN_GATE_PROVIDERS``. Making it the DEFAULT would put
#: never-quality-gated prose in front of every user; making it opt-in keeps PROJECT-BRIEF §9's
#: "wired, NOT tested against acceptance criteria" classification literally true.
MEMO_PROVIDER_ENV = "MEMO_PROVIDER"

#: The one value that selects the live local provider.
MEMO_PROVIDER_OLLAMA = "ollama"

#: ⚑ The pinned model. **The quantization in the tag is deliberate** — fixed weights are what make
#: the digest in the stamp meaningful against register #22.
OLLAMA_MODEL_ID = "llama3.1:8b-instruct-q4_K_M"


def ollama_is_selected() -> bool:
    """``True`` only on an exact ``"ollama"``; the offline double by default."""
    return os.environ.get(MEMO_PROVIDER_ENV) == MEMO_PROVIDER_OLLAMA


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


# ⚑ SUPERSEDED 2026-08-03 (WIRE1-Fold-7). The Fold-6 stub is preserved as the record of what
# structured-only meant: a worker that REFUSED, so the fold's scope was structural rather than
# documentary. Documents have landed, so the real sandboxed worker replaces it.
#
#     class _NoDocumentParseWorker:
#         """Refuses to parse. The document path is NOT part of WIRE1-Fold-6 (Q2(a))."""
#         def parse(self, doc_type, source_path):
#             raise NotImplementedError(
#                 "document parsing is not wired: WIRE1-Fold-6 accepts structured fields only")


#: ⛔ The digest is truncated to this many characters in the stamp — git-short-hash style.
#: ⚑ The full sha256 would push ``model_version`` past what reads sensibly in the UI's forensic
#: tuple (``ForensicTupleRegion.jsx``). Truncating is preferred over DROPPING a component, because
#: a 12-char prefix still distinguishes any two model builds anyone will ever run here.
OLLAMA_DIGEST_CHARS = 12

#: ⚠️ Emitted when the daemon cannot tell us the digest. The stamp stays HONEST — it says the
#: digest is unknown rather than silently omitting the component and looking complete.
OLLAMA_DIGEST_UNAVAILABLE = "digest-unavailable"

#: ⛔ **THE NON-QUALITY-GATED MARKER** (live-llm-drafting Q9 / G2, option D).
#:
#: Ollama is the SHOWCASE provider and is **exempt from the memo-QUALITY gates by design** —
#: ``llm_judge/pipeline.py``'s ``IN_GATE_PROVIDERS`` excludes it, and PROJECT-BRIEF §9 classifies it
#: *"wired, NOT tested against acceptance criteria"*. So a memo it writes has **never been scored
#: for groundedness and never judged against the >=4/5 promptfoo rubric.**
#:
#: ⚑ **WHAT THE EXEMPTION IS AND IS NOT — and the UI copy must not overclaim it.** It is scoped to
#: memo QUALITY. Every DECISION-LEVEL gate still holds for Ollama identically: ``temperature=0``,
#: CON-BR2-TYPE (the model literally cannot represent a recommendation change), bias-swap and
#: reproducibility. The recommendation itself is produced by the deterministic rules engine with no
#: LLM involvement at all. **"Not quality-gated" must never be rendered as "untrustworthy" or
#: "wrong"** — see ``provider_showcase.py:6-9``.
#:
#: ⛔ It leads the stamp so it is the FIRST thing visible wherever ``model_version`` travels — psql,
#: R4, R7, and the UI's forensic tuple. The frontend badge keys off exactly this prefix.
NOT_QUALITY_GATED_MARKER = "NOT-QUALITY-GATED"


def build_ollama_stamp(model_id: str, client: object) -> str:
    """The three-part ``model_version`` stamp: model ID + weight digest + SDK version.

    ⛔ **WHAT THE DIGEST DOES AND DOES NOT PIN — read this before citing it as reproducibility.**
    It pins the **WEIGHTS**: the exact quantized bytes the daemon loaded. It does **NOT** pin the
    sampling stack, the daemon's own version, or the numerical libraries beneath it. It therefore
    **NARROWS register #22 (`MEMO-PROSE-NOT-BIT-REPRODUCIBLE`) and does NOT close it** — the same
    distinction ``outlier_canonical.py`` draws when it says CANON-SER guarantees the persisted
    *representation*, never the computation.

    ⚑ **The SDK version is included even though it did not generate the prose**, because it is what
    ``_SeedSeams`` records for Gemini (``seed_demo_cases.py:407``) and a stamp that dropped it would
    be less comparable across providers, not more honest.

    ⚠️ **Digest lookup FAILS SOFT.** A daemon that cannot answer ``show()`` must not break drafting;
    the stamp degrades to a named placeholder instead.
    """
    digest = OLLAMA_DIGEST_UNAVAILABLE
    try:
        show = getattr(client, "show_digest", None)
        if show is not None:
            raw = show(model_id)
            if raw:
                digest = str(raw).split(":")[-1][:OLLAMA_DIGEST_CHARS]
    except Exception:  # noqa: BLE001 - a stamp detail must never break a draft
        digest = OLLAMA_DIGEST_UNAVAILABLE
    return (
        f"{NOT_QUALITY_GATED_MARKER}+{model_id}+{digest}"
        f"+ollama-python-{_ollama_sdk_version()}"
    )


def _ollama_sdk_version() -> str:
    """The installed ``ollama`` distribution version. Mirrors ``seed_demo_cases._google_genai_version``."""
    try:
        from importlib.metadata import version

        return version("ollama")
    except Exception:  # noqa: BLE001 - a stamp detail must never break a draft
        return "unknown"


class _CompositionSeams:
    """U24's ``CaseSeams``, composed from the frozen units — the request-path counterpart of the
    seed script's ``_SeedSeams``.

    ⚑ Every unit here is REAL: ``rules_engine``'s deterministic engine and ``memo_agent_core``'s
    real ``LangGraphOrchestrator``. **The ONLY substitution is the LLM client** (Q5(a)), and the
    rules evaluation — the part that actually produces the recommendation — is genuine and
    LLM-free regardless, exactly as the deterministic-core architecture requires.
    """

    def __init__(self, *, provider: Optional[str] = None) -> None:
        loader = RulebookLoader(RULEBOOK_DIR)
        self._engine = RulesEngine(loader, engine_version=ENGINE_VERSION)
        self._builder = MemoAgentInputBuilder()
        # ⛔ THE MODEL-ID / STAMP SPLIT. Until this pass both arguments below were the single string
        # OFFLINE_MODEL_VERSION — harmless ONLY because OfflineMemoLLMClient.generate ignores
        # ``model``. Against a real provider the ID must be a resolvable model name and the stamp
        # must be an honest provenance record; they cannot be the same string. ``_SeedSeams``
        # (seed_demo_cases.py:198-205) has carried this split since register #18's pass; the
        # request path never received it until now.
        selected = provider if provider is not None else (
            MEMO_PROVIDER_OLLAMA if ollama_is_selected() else None
        )
        if selected == MEMO_PROVIDER_OLLAMA:
            self._llm_client = build_ollama_client(model_id=OLLAMA_MODEL_ID)
            adapter = OllamaAdapter(
                self._llm_client,
                model=OLLAMA_MODEL_ID,                 # the resolvable model ID
                thinking_mode=ThinkingMode.STANDARD,
            )
            model_version = build_ollama_stamp(OLLAMA_MODEL_ID, self._llm_client)  # the stamp
        else:
            self._llm_client = OfflineMemoLLMClient()
            adapter = GeminiAdapter(self._llm_client, model=OFFLINE_MODEL_VERSION)
            model_version = OFFLINE_MODEL_VERSION
        self._orchestrator = LangGraphOrchestrator(
            adapter,
            rulebook=loader.load_rulebook(RULEBOOK_VERSION),
            model_version=model_version,
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
        """⛔ **THE PER-DRAFT BOUNDARY.** ``begin_draft`` opens a fresh counting scope for THIS
        thread's draft.

        ⚑ **WHY HERE AND NOWHERE ELSE.** This method is called **exactly once per draft**
        (``case_lifecycle/pipeline.py:186``) and lives in the composition root, which is not
        frozen. The alternative — resetting inside ``CasePipeline.draft()`` — would edit
        ``case_lifecycle`` and require a **fifth authorized U24 reopening** for a bookkeeping call.
        This boundary is exactly as per-draft and costs no reopening at all.

        ⚠️ The offline double has no ``begin_draft``; the guard keeps its path byte-unchanged.
        """
        begin = getattr(self._llm_client, "begin_draft", None)
        if begin is not None:
            begin()
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

    ⚑ **WIRE1-Fold-7: the REAL sandboxed worker.** Each document is parsed in a fresh,
    ephemeral subprocess under a 5 s wall clock plus POSIX ``RLIMIT_CPU``/``RLIMIT_AS`` (256 MB),
    with only data crossing back (no pickle). Every termination mode converges on a deterministic
    ``unparseable``. Fold-6's refusing stub is preserved above as the record of what
    structured-only meant.

    ⛔ **WIRE1-Fold-7 / Q8(c): a REAL telemetry emitter, replacing a DISCARDING default.** The
    superseded construction is preserved verbatim:

        return IntakePipeline(parse_worker=SubprocessParseWorker())

    ⚑ With no ``telemetry=`` argument the pipeline fell back to ``TelemetryEmitter()``, whose
    default sink is ``lambda event: None`` — so ``neutralization_count`` was computed on every
    submission and **thrown away**. Harmless while intake was structured-only (no applicant free
    text, nothing to inject); **not harmless now that documents are uploadable**, which is what
    makes PROJECT-BRIEF §10 failure mode #4 reachable. See ``intake_telemetry`` for what the sink
    may and may not carry — counts yes, spans never.

    ⚠️ **UNCACHED, AND THAT IS LOAD-BEARING.** ``TelemetryEmitter`` appends every event to an
    unbounded ``.emitted`` list, so the emitter must die with the request. ⛔ Do not add
    ``@lru_cache`` here.
    """
    return IntakePipeline(
        parse_worker=SubprocessParseWorker(), telemetry=build_intake_telemetry()
    )


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
