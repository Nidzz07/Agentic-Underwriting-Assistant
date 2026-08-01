"""C-CASE-5 — the case pipeline. Drives the frozen units in order; owns no domain computation.

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced in
C-CASE-8): holds no LLM of its own; edits no frozen unit; declares no verdict; **never
re-implements the commit gate, the authz check, or a write to ``audit_record``**; no network at
tier-U (every LLM-bearing dependency is INJECTED and driven by an offline double).

**P-CASE-5 (BR-CASE-3)** — ``submit()`` advances ``submitted -> profiled -> evaluated`` **EAGERLY,
inside ONE ``store.atomic()``**. All three steps are **LLM-FREE**, so submission either reaches
``evaluated`` or leaves **NO partial row**.

**P-CASE-6 (BR-CASE-4)** — drafting sits behind its **own explicit trigger**. ``draft()`` is never
called by a read path, so R4 stays a **pure, side-effect-free GET**.

**P-CASE-10 (BR-CASE-10)** — ⚑ ``route_borderline`` is **NOT internal to the frozen orchestrator**
(measured: zero routing references there). U24 **calls it explicitly** and threads the resulting
``ThinkingMode`` into the adapter. ``ThinkingMode`` is deliberately **NOT persisted**: it is a pure
deterministic function of ``(rule_report, outlier_signal)``, both of which ARE persisted, so it is
**exactly re-derivable from stored state** — its absence is a decision, not an oversight.

**Q4-A** — ``draft()`` returns a :class:`DraftOutcome` rather than raising, so success and failure
are **ordinary testable return values** and the caller's ``drafted``-vs-``failed`` branch is **one
visible decision**. The frozen orchestrator's existing ``DecisionMemo | None`` maps straight onto
it — **U24 invents no new failure vocabulary**.

``temperature=0`` stays **centrally fixed inside U19's frozen adapters**; U24 neither sets nor
overrides it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Protocol

from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.case_lifecycle.schemas import PendingApplication, PendingRecommendation
from backend.case_lifecycle.states import CaseState, assert_legal, is_legal
from backend.case_lifecycle.store import CaseStore
from backend.memo_extensions.borderline_router import route_borderline


@dataclass(frozen=True)
class DraftOutcome:
    """Success-with-artifacts or failure-with-reason. Q4-A.

    ⚑ **THREE outcomes, not two** (U24's fourth reopening, change (c)). ``succeeded`` splits
    "produced a memo" from "did not", but *not producing one* has two very different meanings:

      * a **real failure** — drafting ran and came back empty (citation validation gave up; the
        shape behind register #18, where every seeded case silently FAILED), and
      * a **benign skip** — the case was already drafted, so nothing was attempted.

    ``skipped`` is a **field, not a parsed string**, deliberately. Callers print
    ``"drafted" if succeeded else f"FAILED ({failure_reason})"``; without a discriminator a routine
    re-seed reports **FAILED** on every already-drafted case, which trains an operator to ignore
    FAILED lines — precisely how #18 stayed invisible. Matching on ``failure_reason``'s prose would
    couple callers to wording; a field cannot drift.

    ⚑ **Additive with a default**, so every existing construction and every existing caller is
    unaffected.
    """

    memo: Optional[object] = None
    outlier: Optional[object] = None
    thinking_mode: Optional[object] = None
    failure_reason: Optional[str] = None
    skipped: bool = False

    @property
    def succeeded(self) -> bool:
        return self.memo is not None


class CaseSeams(Protocol):
    """The frozen units, injected. tier-U supplies offline doubles."""

    def profile(self, raw: object) -> object: ...
    def evaluate(self, profile: object) -> object: ...
    def score_outlier(self, profile: object) -> Optional[object]: ...
    def draft_memo(self, profile: object, report: object, thinking_mode: object) -> Optional[object]: ...


class CasePipeline:
    """Composes the frozen units. Strictly downstream; nothing feeds back into generation."""

    def __init__(
        self,
        store: CaseStore,
        seams: CaseSeams,
        recommendation_id_factory: Callable[[str], str],
    ) -> None:
        self._store = store
        self._seams = seams
        self._new_recommendation_id = recommendation_id_factory

    # --- eager, atomic advance (BR-CASE-3) ---------------------------------------------

    def submit(self, application_id: str, raw: object) -> PendingApplication:
        """``submitted -> profiled -> evaluated`` in ONE transaction. LLM-free throughout.

        ⚑ **A case that has PROGRESSED BEYOND ``evaluated`` is returned UNCHANGED** — register #27
        and #28 (U24's fourth authorized reopening, change (a)).

        ``put_application`` is an upsert whose ``set_`` includes ``state``, so this method used to
        rewrite an existing row's state to ``evaluated`` unconditionally. Two defects followed:

          * **#27** — the reset re-legalized ``(evaluated -> drafted)``, so ``draft()``'s guard
            never fired and a **new ``pending_recommendation`` row was inserted on every re-seed**,
            unbounded, with nothing to order them by.
          * **#28** — a **terminal** ``committed`` case was silently reset and became re-draftable
            **after it had already been committed to the audit trail**. Measured, not inferred.

        ⚑ **The guard belongs HERE, not in ``put_application``** (remediation-plan Q7(a)). That
        upsert is the sole state-writing primitive for ``draft()``'s ``evaluated -> drafted``, for
        ``_transition``'s ``evaluated -> failed``, **and for register #19's CAS inside both test
        doubles**. Making it stop writing ``state`` would break all three. ``submit()`` is the only
        caller that is not performing a transition, so it is the only correct place to refuse.

        ⚑ **An ``evaluated`` case is still refreshed**, deliberately: it has not been drafted, so
        re-submitting is an ordinary re-evaluation (e.g. against an updated rulebook) and stays
        useful. Only *progression* is protected.

        ⚠️ **Consequence, disclosed rather than discovered:** a ``failed`` case is also returned
        unchanged, because ``FAILED`` is in ``TERMINAL_STATES`` and resetting it would be the same
        class of illegal write as #28. A re-seed therefore no longer retries a failed case — that
        now requires clearing the row deliberately, which is the honest behaviour for a state the
        machine calls terminal.
        """
        assert_legal(CaseState.SUBMITTED, CaseState.PROFILED)
        assert_legal(CaseState.PROFILED, CaseState.EVALUATED)

        existing = self._store.get_application(application_id)
        if existing is not None and existing.state is not CaseState.EVALUATED:
            return existing

        profile = self._seams.profile(raw)
        report = self._seams.evaluate(profile)

        application = PendingApplication(
            application_id=application_id,
            state=CaseState.EVALUATED,
            profile_canonical=CanonSerAdapter.canonical_bytes(profile),
            profile_content_hash=CanonSerAdapter.content_hash(profile),
            rule_results_canonical=CanonSerAdapter.canonical_bytes(report),
            rule_results_content_hash=CanonSerAdapter.content_hash(report),
            rulebook_version=report.rulebook_version,
            engine_version=report.engine_version,
        )
        with self._store.atomic():
            self._store.put_application(application)
        return application

    # --- the explicit drafting trigger (BR-CASE-4/5/10) ---------------------------------

    def draft(self, application_id: str) -> DraftOutcome:
        """The ONLY LLM-bearing step. Returns an outcome; never raises for a domain failure."""
        application = self._store.get_application(application_id)
        if application is None:
            return DraftOutcome(failure_reason="unknown application")

        # ⚑ THE LEGALITY CHECK, MOVED HERE from just above the write (U24's fourth reopening,
        # change (b)). Two reasons it belongs at the top rather than the bottom:
        #
        #   1. It was DEAD CODE until change (a). `submit()` always reset the state to
        #      `evaluated` first, so `(evaluated -> drafted)` was always legal and this could
        #      never fire. Now that `submit()` leaves a progressed case alone, a re-draft
        #      genuinely reaches here — for the first time.
        #   2. ⚑ Below `draft_memo` it would refuse only AFTER the LLM-bearing call had run.
        #      Under `--real-llm` that spends money on a memo the refusal then discards.
        #
        # `is_legal` (pure) rather than `assert_legal`: a re-draft is a DOMAIN failure, and this
        # method's contract is that it "never raises for a domain failure" (Q4-A) — the same
        # shape as the unknown-application miss immediately above.
        if not is_legal(application.state, CaseState.DRAFTED):
            return DraftOutcome(
                skipped=True,
                failure_reason=f"already {application.state.value}; not re-drafted",
            )

        profile = CanonSerAdapter.profile_from_canonical(application.profile_canonical)
        report = CanonSerAdapter.report_from_canonical(application.rule_results_canonical)
        outlier = self._seams.score_outlier(profile)

        # ⚑ EXPLICIT — the frozen router is not reached by the orchestrator (P-CASE-10).
        thinking_mode = route_borderline(report, outlier)

        memo = self._seams.draft_memo(profile, report, thinking_mode)
        if memo is None:
            self._transition(application, CaseState.FAILED)
            return DraftOutcome(
                outlier=outlier,
                thinking_mode=thinking_mode,
                failure_reason="drafting produced no memo",
            )

        recommendation = PendingRecommendation(
            recommendation_id=self._new_recommendation_id(application_id),
            application_id=application_id,
            memo_canonical=CanonSerAdapter.canonical_bytes(memo),
            memo_hash=memo.memo_hash,
            model_version=memo.model_version,
            engine_version=application.engine_version,
            rulebook_version=application.rulebook_version,
            outlier_canonical=(
                CanonSerAdapter.canonical_bytes(outlier) if outlier is not None else None
            ),
        )
        # ⚑ COMMITBOUND-1(d): the drafted transition AND the recommendation share ONE atomic().
        # ⚑ The `assert_legal(application.state, CaseState.DRAFTED)` that stood here has MOVED to
        # the top of this method (change (b)) — same check, same table, earlier and non-raising.
        # It is not weakened: nothing between there and here mutates `application.state`, which is
        # read once into a frozen dataclass.
        with self._store.atomic():
            self._store.put_application(
                PendingApplication(
                    application_id=application.application_id,
                    state=CaseState.DRAFTED,
                    profile_canonical=application.profile_canonical,
                    profile_content_hash=application.profile_content_hash,
                    rule_results_canonical=application.rule_results_canonical,
                    rule_results_content_hash=application.rule_results_content_hash,
                    rulebook_version=application.rulebook_version,
                    engine_version=application.engine_version,
                )
            )
            self._store.put_recommendation(recommendation)
        return DraftOutcome(memo=memo, outlier=outlier, thinking_mode=thinking_mode)

    # --- pure read path (BR-CASE-4) -----------------------------------------------------

    def read(self, application_id: str) -> Optional[PendingApplication]:
        """The R4-facing read. ⚑ Invokes NO pipeline step and mutates NOTHING."""
        return self._store.get_application(application_id)

    # --- internal ------------------------------------------------------------------------

    def _transition(self, application: PendingApplication, dst: CaseState) -> None:
        assert_legal(application.state, dst)
        with self._store.atomic():
            self._store.put_application(
                PendingApplication(
                    application_id=application.application_id,
                    state=dst,
                    profile_canonical=application.profile_canonical,
                    profile_content_hash=application.profile_content_hash,
                    rule_results_canonical=application.rule_results_canonical,
                    rule_results_content_hash=application.rule_results_content_hash,
                    rulebook_version=application.rulebook_version,
                    engine_version=application.engine_version,
                )
            )
