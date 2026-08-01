"""OUT-OF-BAND DEMO SEED SCRIPT — makes the wired API layer exercisable.

╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  THE MEMOS THIS SCRIPT PRODUCES ARE SYNTHETIC PLACEHOLDERS, NOT REAL LLM OUTPUT.      ║
║                                                                                          ║
║  By DEFAULT (no --real-llm) this script drafts with ``_OfflineLLMClient`` — a             ║
║  DETERMINISTIC OFFLINE DOUBLE defined in this file. It makes no network call, uses        ║
║  no API key, and costs nothing. Register #18 is NARROWED: a production ``LLMClient``      ║
║  is now reachable via --real-llm (which ALSO requires ALLOW_REAL_LLM_CALLS=true).         ║
║                                                                                          ║
║  ⛔ A memo seeded by this script MUST NEVER be read as a genuine drafted recommendation.  ║
║     It exists so R4's ``ready`` branch and R5's commit path are EXERCISABLE — nothing     ║
║     more. Every seeded memo is stamped ``model_version="OFFLINE-DOUBLE-NOT-A-REAL-LLM"``  ║
║     so the placeholder is visible in the API response, the database and any audit record  ║
║     it is committed into.                                                                ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

**Why a script and not a route** (Scope B, Q2-A): WIRE-1 pins EXACTLY seven routes and contains
no ingestion route, and U23's frozen ``NFR-DEP-ROUTES-1`` asserts the deployed (path, method) set
equals that surface. Adding ``POST /applications`` would amend a frozen contract AND break a
load-bearing frozen test. So ingestion lives here, outside the route layer, where it costs
neither.

**Why the pipeline is constructed HERE and not in the composition root** (Q3-D): none of
R2/R3/R4/R5 calls ``submit()`` or ``draft()`` — the four routes need only the store, the pure
``case_to_memo_view_state`` projection, and the commit-context provider. Keeping ``CasePipeline``
out of ``backend/app/`` means the LLM-bearing composition never enters the request path, which is
what makes R4 side-effect-free BY CONSTRUCTION rather than by discipline (BR-CASE-4 / TRIGGER-1).

**Migrations** (Q9-B): this script applies BOTH sequences — ``database``'s (U15) and U24's — via
each one's own runner. ⚑ Register item **#8 ``DEPLOY-MIGRATE-DEFERRED`` STAYS OPEN**: this is a
DEMO-PATH convenience, **not** the deployment CLI entrypoint that item calls for, and it does not
discharge it.

**Location**: ``backend/scripts/`` is outside ``backend/app/`` and ``backend/case_lifecycle/`` —
outside BOTH structural-scan roots and absent from every ``--cov=`` entry — so the offline double
below cannot be mistaken for, or accidentally wired into, a production path.

Run (out of band)::

    python -m backend.scripts.seed_demo_cases --cases 3
"""
from __future__ import annotations

import argparse
import json
import re
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version as _pkg_version

import sqlalchemy as sa

from backend.app.llm_client import build_gemini_client
from backend.app.outlier_canonical import quantize_outlier
from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.case_lifecycle.migrate import apply_case_migrations
from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.repository import PostgresCaseStore
from backend.corpus_generator.records import CorpusManifest
from backend.database.migration_runner import MigrationRunner
from backend.intake import schema as isch
from backend.memo_agent_core.input_builder import MemoAgentInputBuilder
from backend.memo_agent_core.orchestrator import LangGraphOrchestrator
from backend.memo_agent_core.provider import GeminiAdapter
from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.model import FittedOutlierModel, OutlierModel
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader
from backend.secrets_config import get_settings

#: ⚠️ Stamped onto every seeded memo so the placeholder is visible everywhere it travels.
OFFLINE_MODEL_VERSION = "OFFLINE-DOUBLE-NOT-A-REAL-LLM"

#: ⚑ Register #18 / Q6 — the real path pins an EXPLICIT, NON-FLOATING model id (never the
#: ``gemini-2.5-flash`` alias, and never ``GeminiAdapter``'s frozen default) so provider-side
#: model drift is bounded and the audit stamp is falsifiable. The exact dated/versioned suffix
#: Google currently serves must be CONFIRMED at manual verification (see
#: guide-docs/build/composition-root/real-llm-verification.md) — the real path is opt-in and
#: out-of-band, never run in CI.
REAL_MODEL_ID = "gemini-2.5-flash-001"

#: ⚑ Register #18 / Q5c — a conservative per-process real-call cap (overridable via
#: ``--max-llm-calls``) so a deliberate larger run is possible but accidental spend is not. The
#: cap lives INSIDE the wrapper (Q5b), so it counts the citation-retry loop too.
REAL_CALL_CAP = 20

RULEBOOK_VERSION = "1.0.0"
ENGINE_VERSION = "seed-script-1"


def rulebook_dir() -> str:
    """The repo rulebook directory.

    ⚑ `RulebookLoader` takes this as a REQUIRED argument — it has no default. Named here once,
    mirroring `run_quality_gates.py:RULEBOOK_DIR` and `corpus_generator/build.py`.
    """
    return str(Path(__file__).resolve().parents[1] / "rules_engine" / "rulebook")


#: The committed corpus the outlier model is fitted from (Q5(a)/Q6(a)). Module-level and named
#: once so a test can point it elsewhere — mirroring ``rulebook_dir()``'s single-source shape.
CORPUS_DIR = Path(__file__).resolve().parents[2] / "corpus"


def build_outlier_model(corpus_dir: Path | str | None = None) -> FittedOutlierModel:
    """Fit the outlier model from the COMMITTED corpus. Fails LOUDLY if it is absent (Q6(a)).

    ⚑ **Why a missing corpus is an ERROR and not a graceful degrade.** The rejected alternative
    (Q6(b)) was to fall back to ``outlier=None`` — which silently reproduces the exact defect this
    wiring exists to fix, in the one script whose entire job is producing COMPLETE demo data. A
    silent null here is indistinguishable from the Phase-1 behaviour and would be very hard to
    notice; a named failure cannot be missed.

    ⚑ **This does NOT violate BR-OUT-8 / NFR-OUT-CORPUS-1.** That invariant binds ``outlier_model``
    itself — the unit still builds, tests and imports with no ``corpus/`` present, and its own 51
    tier-U tests never read one. It does not bind a CALLER that chooses to supply a corpus, which
    is exactly what ``CorpusSource.from_file`` exists for.

    ⚠️ OPEN, and deliberately not answered here: whether ``corpus/`` ships to the DEPLOYED backend.
    ``render.yaml`` neither places nor verifies it, and seeding is not part of deployment at all —
    so nothing today depends on the answer. Carried to the deployment pass (plan §7 item 2).
    """
    corpus_dir = Path(corpus_dir) if corpus_dir is not None else CORPUS_DIR
    profiles_path = corpus_dir / "profiles.json"
    manifest_path = corpus_dir / "manifest.json"

    for path in (profiles_path, manifest_path):
        if not path.is_file():
            raise FileNotFoundError(
                f"outlier corpus not found at {path} - the demo seed cannot produce complete "
                f"data without it. The corpus is committed to this repository; if it is missing, "
                f"restore it rather than seeding cases with a null outlier."
            )

    records = CorpusSource.from_file(profiles_path)
    manifest = CorpusManifest.model_validate(
        json.loads(manifest_path.read_text(encoding="utf-8"))
    )
    return OutlierModel.fit(CorpusSource.profiles(records), manifest, ShapExplainer())


#: Matches a rule id as it appears in U4's prompt (e.g. ``DTI-CEIL-1``, ``IRDAI-EMP-SALARIED-1``).
_RULE_ID_PATTERN = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b")


def _first_cited_rule_id(prompt: str) -> str:
    """The first rule id appearing in the prompt, or ``""`` if none does.

    ⚑ DISCOVERED, never hardcoded — see DEFECT FIX 2. Returning ``""`` when the prompt genuinely
    contains no rule id is correct and deliberate: the draft is then legitimately blocked by
    `CitationValidator`, which is the honest outcome rather than inventing a citation.
    """
    match = _RULE_ID_PATTERN.search(prompt)
    return match.group(0) if match else ""


class _OfflineLLMClient:
    """⚠️ A DETERMINISTIC OFFLINE STAND-IN FOR THE MISSING PRODUCTION ``LLMClient``.

    ⛔ **NOT A MODEL. NOT REAL INFERENCE. NOT FOR PRODUCTION USE.**

    It satisfies the frozen ``LLMClient`` seam (``generate(*, model, prompt, temperature) -> str``)
    by returning fixed, valid structured XML. It exists ONLY so the drafting step can run without
    a live provider — see register #18 (B4): no production ``LLMClient`` wrapper exists anywhere
    in this build, ``requirements.txt`` declares the LEGACY ``google-generativeai`` SDK while the
    code imports the NEW ``google-genai`` one, and the only real adapter
    (``corpus_generator/build.py``) is a tier-B entrypoint that is not authorized.

    ⚑ **SUPERSEDED — 2026-07-23 (C7).** All three clauses above are now out of date; the
    paragraph is kept verbatim as the historical record of why this double was written.
    Current position: (1) register **#18 is NARROWED** — a production ``LLMClient`` DOES
    exist at ``backend/app/llm_client.py`` (``CappedGeminiClient`` + ``build_gemini_client``),
    and this script reaches it via ``--real-llm``; (2) ``requirements.txt`` declares
    ``google-genai>=1.0.0`` and the legacy distribution is gone, so the manifest is
    self-consistent; (3) ``corpus_generator/build.py`` is **no longer the only real adapter
    and no longer the tier-B entrypoint** — **tier-B Stage 1 IS authorized**, and its guarded
    entrypoint is ``backend/scripts/build_corpus.py``, which routes through
    ``build_gemini_client`` and inherits both #18 spend gates. ``build.py`` remains on disk
    **unused, coverage-omitted and still unguarded** — superseded, not deleted (register #3 /
    authorization plan Q4-b). ⚑ Note that tier-B **Stage 2/3** (memo drafting, judge
    evaluation) remains **NOT authorized**, and the committed ``corpus/`` carries
    **placeholder offline prose**, never model-authored text.

    The returned prose is deliberately written to announce itself as a placeholder, so it is
    obvious even to someone reading a committed audit record with no other context.
    """

    def generate(self, *, model: str, prompt: str, temperature: float) -> str:
        # ⚑ DEFECT FIX 2 — this previously read `cited = "DTI-001" if "DTI-001" in prompt else ""`,
        # and **there is no rule `DTI-001` in this build** (the DTI rule is `DTI-CEIL-1`). The
        # condition was therefore ALWAYS False, the double emitted an EMPTY `<rule_id>`, U4's
        # `CitationValidator` rejected it, the graph retried to `MEMO_CITATION_RETRY_CAP` and
        # then FLAGGED — so every seeded case landed in `FAILED`, never `drafted`. The comment
        # that stood here asserted the opposite, which is how it survived review.
        #
        # The id is now DISCOVERED from the prompt rather than hardcoded, so this cannot drift
        # out of step with the rulebook again: whatever rule the report actually contains is
        # what gets cited, and citation validation passes for the RIGHT reason rather than by
        # coincidence or by being bypassed.
        cited = _first_cited_rule_id(prompt)
        return (
            "<memo>"
            "<narrative_prose>"
            "PLACEHOLDER MEMO - GENERATED OFFLINE BY THE DEMO SEED SCRIPT, NOT BY A LANGUAGE "
            "MODEL. This text exists only to exercise the wired API path and carries no "
            "underwriting judgement of any kind. It must not be relied upon, shown to a "
            "customer, or read as an advisory recommendation. Refer this case to a human "
            "underwriter."
            "</narrative_prose>"
            f"<cited_rule_ids><rule_id>{cited}</rule_id></cited_rule_ids>"
            "</memo>"
        )


class _SeedSeams:
    """The production ``CaseSeams`` shape, composed from the frozen units.

    ⚑ Every unit here is REAL — ``intake``'s schema, ``rules_engine``'s deterministic engine, and
    ``memo_agent_core``'s real ``LangGraphOrchestrator``. **The ONLY substitution is the LLM
    client**: by DEFAULT the ``_OfflineLLMClient`` double (below); with ``--real-llm`` the genuine
    ``CappedGeminiClient`` from ``backend/app/llm_client.py`` (register #18). The rules evaluation
    — the part that actually produces the recommendation — is fully genuine and LLM-free either
    way, exactly as the deterministic-core architecture requires.
    """

    def __init__(
        self,
        llm_client=None,
        *,
        model: str = OFFLINE_MODEL_VERSION,
        model_version: str = OFFLINE_MODEL_VERSION,
        outlier_model: FittedOutlierModel | None = None,
    ) -> None:
        # ⚑ DEFECT FIX 1 — `RulebookLoader.__init__` takes a REQUIRED `rulebook_dir` and has no
        # default. This previously read `RulebookLoader()`, so `_SeedSeams.__init__` raised
        # `TypeError` on its FIRST statement and `main()` could not complete under ANY
        # invocation. Named explicitly, exactly as every other caller in the build does.
        loader = RulebookLoader(rulebook_dir())
        self._engine = RulesEngine(loader, engine_version=ENGINE_VERSION)
        self._rulebook = loader.load_rulebook(RULEBOOK_VERSION)
        self._builder = MemoAgentInputBuilder()
        # Default (no --real-llm): the offline double, model + stamp = OFFLINE_MODEL_VERSION —
        # byte-for-byte the historical behaviour. Real path: the injected CappedGeminiClient with
        # an explicit non-floating model id and a real model_version stamp (Q4b split).
        client = llm_client if llm_client is not None else _OfflineLLMClient()
        # ⚑ INJECTED, never fitted here (ambiguity-check Fold B). Fitting the corpus costs ~2.6s
        # and would add a NEW hard failure mode to a constructor that already shipped a defect of
        # exactly that shape — `RulebookLoader()` raised on `__init__`'s FIRST statement, which is
        # why `test_seed_seams_constructs_without_raising` exists. `main()` builds and injects the
        # real model; with `None` the seam keeps its byte-identical Phase-1 behaviour, so the five
        # existing `_SeedSeams()` constructions in the tier-U suite need no corpus and pay no fit.
        self._outlier_model = outlier_model
        self._orchestrator = LangGraphOrchestrator(
            GeminiAdapter(client, model=model),
            rulebook=self._rulebook,
            model_version=model_version,
        )

    def profile(self, raw: object) -> isch.ApplicantProfile:
        """``raw`` is already a validated profile here — the script builds them directly."""
        return raw  # type: ignore[return-value]

    def evaluate(self, profile):
        return self._engine.evaluate(profile, RULEBOOK_VERSION)

    def score_outlier(self, profile):
        """Score the applicant with the INJECTED fitted model, or ``None`` if none was injected.

        ⚑ SUPERSEDED docstring, preserved verbatim because it was true for the whole of Phase 1:
        *"Phase 1 emits no outlier (``services.md`` omits the OUT call), and WIRE1-Fold-4 binds
        R4's ``outlier`` to ``null`` regardless. Returning ``None`` is the honest Phase-1
        behaviour, not a stub standing in for something that should be here."*

        What changed is the FIRST clause only: this is the **Phase-2-OUT** slice (Q2(a)) — an
        API-reachable path that computes and persists a real ``OutlierResult``. The OUT call is
        no longer omitted. ⛔ This does NOT mean "the system is in Phase 2": ``ObservabilityService``
        (Langfuse / Prometheus) is untouched and out of scope by the same answer.

        WIRE1-Fold-4 is NOT amended and did not need to be — it binds ``outlier`` null *in Phase 1*
        and explicitly provides for it being *"populated only for a Phase-2 ``ready`` view"*.
        Populating it is contract-COMPLIANT, which is why this pass touches no frozen contract.

        ``None`` remains the default and the honest answer when nothing was injected — that path
        is pinned by T1 and is what keeps the tier-U suite corpus-free.

        ⛔ **Returns a QUANTIZED PROJECTION, not the raw ``OutlierResult``** (barrier #5). U24
        serializes this return with ``CanonSerAdapter.canonical_bytes``, which rejects IEEE float
        outright — and every numeric field of ``OutlierResult`` is a float. Handing back the
        Decimal projection is what makes the score persistable **without reopening a single frozen
        unit**: ``CaseSeams.score_outlier`` is typed ``Optional[object]``, so U24's path is
        untouched. See ``backend/app/outlier_canonical.py`` for what the projection does and does
        NOT claim — in particular, it is **not** a claim of cross-version FP reproducibility.
        """
        if self._outlier_model is None:
            return None
        return quantize_outlier(self._outlier_model.score(profile))

    def draft_memo(self, profile, report, thinking_mode):
        return self._orchestrator.run(
            self._builder.build(applicant_profile=profile, rule_report=report)
        )


def _demo_profile(index: int) -> isch.ApplicantProfile:
    """A synthetic applicant. DATA-4: synthetic only, never real PII."""
    return isch.ApplicantProfile(
        application_id=f"DEMO-{index:04d}",
        date_of_birth=date(1986, 3, 14),
        as_of_date=date(2026, 1, 1),
        age_years_derived=39,
        verifiable_income_annual=Decimal("1200000"),
        requested_cover_amount=Decimal("4000000"),
        incomplete=False,
        demographics=isch.Demographics(
            full_name=f"Demo Applicant {index}",
            gender=isch.Gender.FEMALE,
            city="Metropolis",
        ),
        documents=isch.DocumentManifest(expected_count=3, satisfied_count=3, entries=[]),
    )


def _recommendation_id_factory(application_id: str) -> str:
    """⚑ Q3a resolved to the uuid4 fallback FROM DISK, not by preference.

    ``audit_store``'s frozen ``IdGenerator.new_id()`` takes NO argument, while
    ``recommendation_id_factory`` is ``Callable[[str], str]`` — the shapes do not fit, so reusing
    that seam was not available.
    """
    return f"REC-{application_id}-{uuid.uuid4().hex[:8]}"


def _report_case(application_id: str, outcome) -> None:
    """Print a case's drafting result as one of THREE states, not two (register #27/#28).

    ⛔ This previously read ``"drafted" if outcome.succeeded else f"FAILED ({...})"``, which had no
    way to distinguish a **benign skip** from a **real drafting failure**. Now that re-running the
    seed correctly refuses to re-draft an already-drafted case, that two-way split would print
    **FAILED** on every routine re-run — training an operator to ignore FAILED lines, which is
    exactly how register #18's citation defect (every seeded case silently FAILED) stayed
    invisible for so long.

    ⚑ The distinction comes from ``DraftOutcome.skipped``, a **field, not parsed prose** — so it
    cannot drift when a message is reworded.
    """
    if outcome.succeeded:
        state = "drafted"
    elif outcome.skipped:
        state = f"skipped ({outcome.failure_reason})"
    else:
        state = f"FAILED ({outcome.failure_reason})"
    print(f"  {application_id}: submitted -> {state}")


def apply_all_migrations(engine: sa.Engine) -> None:
    """Apply BOTH sequences: ``database``'s (U15) then U24's (guard-first).

    ⚑ Register #8 ``DEPLOY-MIGRATE-DEFERRED`` is NOT discharged by this — it asks for a
    deployment CLI entrypoint (``render.yaml``'s ``preDeployCommand``), which this is not.
    """
    applied_db = MigrationRunner(engine).apply_all()
    applied_case = apply_case_migrations(engine)
    print(f"  migrations: database={len(applied_db)} case_lifecycle={len(applied_case)}")


def _google_genai_version() -> str:
    """The installed ``google-genai`` SDK version, for the real-path audit stamp (Q6b).

    ``unknown`` if unresolved — only reached on the opt-in real path, where the SDK is present.
    """
    try:
        return _pkg_version("google-genai")
    except PackageNotFoundError:
        return "unknown"


def seed(engine: sa.Engine, case_count: int, seams: _SeedSeams, draft: bool = True) -> list[str]:
    """Submit ``case_count`` cases; draft all but the last so BOTH R4 branches are reachable."""
    store = PostgresCaseStore(engine)
    pipeline = CasePipeline(store, seams, _recommendation_id_factory)

    seeded: list[str] = []
    for index in range(1, case_count + 1):
        profile = _demo_profile(index)
        application = pipeline.submit(profile.application_id, profile)
        seeded.append(application.application_id)

        # Leave the LAST case at `evaluated` so R4's `pending` branch is exercisable too.
        if draft and index < case_count:
            outcome = pipeline.draft(application.application_id)
            _report_case(application.application_id, outcome)
        else:
            print(f"  {application.application_id}: submitted -> evaluated (left pending)")
    return seeded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--cases", type=int, default=3, help="how many demo cases to seed")
    parser.add_argument("--no-draft", action="store_true", help="submit only; never draft")
    parser.add_argument("--skip-migrations", action="store_true")
    parser.add_argument(
        "--real-llm",
        action="store_true",
        help="OPT-IN: draft with the REAL Gemini client (SPENDS MONEY). ALSO requires "
        "ALLOW_REAL_LLM_CALLS=true in the environment — two independent gates.",
    )
    parser.add_argument(
        "--max-llm-calls",
        type=int,
        default=REAL_CALL_CAP,
        help=f"real-path per-process call cap (default {REAL_CALL_CAP}); ignored offline.",
    )
    args = parser.parse_args(argv)

    # ⚑ FIT FIRST, BEFORE ANY DATABASE WORK. Ordering is deliberate: a missing corpus must fail
    # before migrations run or a single row is written, so a failed run leaves nothing half-seeded.
    # ~2.6s for 300 profiles, paid ONCE per invocation (this is a one-shot CLI, so "fit once at
    # startup" and "fit once per run" are the same thing). Determinism is not assumed: the fit is
    # seeded from CorpusManifest.seed via an explicit local RandomState, never the global np.random.
    #
    # ⚑ HISTORY, so this is not re-litigated: this line was added, then REVERTED on 2026-08-01
    # because injecting a real model made the script RAISE instead of seeding — `score_outlier`
    # returned a float-bearing `OutlierResult` and CANON-SER refuses float (barrier #5). It is
    # restored here only because `score_outlier` now returns the Decimal projection, which U24 can
    # actually serialize. The ordering above and the loud failure below are unchanged.
    outlier_model = build_outlier_model()

    # ⚑ TWO INDEPENDENT GATES (Q4): the --real-llm flag here, AND ALLOW_REAL_LLM_CALLS=true
    # checked inside build_gemini_client. The offline default touches neither.
    if args.real_llm:
        real_client = build_gemini_client(
            get_settings(), model_id=REAL_MODEL_ID, max_calls=args.max_llm_calls
        )
        model_version = f"{REAL_MODEL_ID}+google-genai-{_google_genai_version()}"
        seams = _SeedSeams(
            real_client,
            model=REAL_MODEL_ID,
            model_version=model_version,
            outlier_model=outlier_model,
        )
        print("=" * 78)
        print("DEMO SEED — ⚠️  REAL LLM CALLS — THIS WILL SPEND MONEY")
        print(f"            model={REAL_MODEL_ID!r}  call cap={args.max_llm_calls}  stamp={model_version!r}")
        print("=" * 78)
    else:
        real_client = None
        seams = _SeedSeams(outlier_model=outlier_model)
        print("=" * 78)
        print("DEMO SEED — ⚠️  MEMOS ARE SYNTHETIC PLACEHOLDERS, NOT REAL LLM OUTPUT")
        print(f"            every memo is stamped model_version={OFFLINE_MODEL_VERSION!r}")
        print("=" * 78)

    engine = sa.create_engine(get_settings().DATABASE_URL)
    if not args.skip_migrations:
        apply_all_migrations(engine)

    seeded = seed(engine, args.cases, seams, draft=not args.no_draft)

    print(f"\nSeeded {len(seeded)} case(s). The API layer is now exercisable:")
    print("  GET  /applications            (R2)")
    print("  GET  /applications/{id}       (R3)")
    print("  GET  /applications/{id}/memo  (R4 — 'ready' for drafted, 'pending' for the last)")
    print("  POST /recommendations/{id}/commit  (R5)")
    if args.real_llm and real_client is not None:
        print(f"\n💸 REAL LLM calls made this run: {real_client.call_count} (cap {args.max_llm_calls}).")
        print("   These memos are GENUINE model output — not placeholders.")
    else:
        print("\n⚠️  Reminder: seeded memo prose is a placeholder. Not a real recommendation.")
    return 0


if __name__ == "__main__":  # pragma: no cover - out-of-band entrypoint
    raise SystemExit(main())
