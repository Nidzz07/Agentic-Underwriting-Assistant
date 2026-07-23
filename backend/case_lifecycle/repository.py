"""C-CASE-3 — the SQL-exec shim. **The ONLY module in U24 that issues SQL.**

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced in
C-CASE-8): holds no LLM; edits no frozen unit; declares no verdict; **never re-implements the
commit gate, the authz check, or a write to ``audit_record``**.

⚑ **DUAL STATUS (CASE-Req-Fold-3) — read this before touching the coverage config.**

  * **OMITTED FROM COVERAGE** — exercised via testcontainers at **tier-I**, never import-covered at
    tier-U. This follows ``pg_repository.py``'s precedent **verbatim**.
  * **INCLUDED IN ADAPTER-1's SCAN SET** — the coverage omit governs *where this module is
    exercised*, **NEVER** *what it may contain*. If the scan inherited the omit, a direct
    ``canon_ser(...)`` call hidden here would be **structurally invisible**.

**This module performs NO canonicalization.** It receives **already-canonicalized bytes** and only
executes SQL — and ADAPTER-1 asserts that **positively**, so the claim is a *tested property*
rather than a design intention.

Reached only through the ``CaseStore`` Protocol; the tier-U fake stands in its place.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

import sqlalchemy as sa

from backend.case_lifecycle.schemas import PendingApplication, PendingRecommendation
from backend.case_lifecycle.states import CaseState, CommitClaimResult

metadata = sa.MetaData()

pending_application = sa.Table(
    "pending_application",
    metadata,
    sa.Column("application_id", sa.String, primary_key=True),
    sa.Column("state", sa.String, nullable=False),
    sa.Column("profile_canonical", sa.LargeBinary, nullable=False),
    sa.Column("profile_content_hash", sa.String, nullable=False),
    sa.Column("rule_results_canonical", sa.LargeBinary, nullable=True),
    sa.Column("rule_results_content_hash", sa.String, nullable=True),
    sa.Column("rulebook_version", sa.String, nullable=True),
    sa.Column("engine_version", sa.String, nullable=True),
)

pending_recommendation = sa.Table(
    "pending_recommendation",
    metadata,
    sa.Column("recommendation_id", sa.String, primary_key=True),
    sa.Column("application_id", sa.String, nullable=False),
    sa.Column("memo_canonical", sa.LargeBinary, nullable=False),
    sa.Column("memo_hash", sa.String, nullable=False),
    sa.Column("model_version", sa.String, nullable=False),
    sa.Column("engine_version", sa.String, nullable=False),
    sa.Column("rulebook_version", sa.String, nullable=False),
    sa.Column("outlier_canonical", sa.LargeBinary, nullable=True),
)


class PostgresCaseStore:
    """The tier-I ``CaseStore`` implementation. Satisfies the Protocol; adds nothing."""

    def __init__(self, engine: sa.Engine) -> None:
        self._engine = engine
        self._conn: Optional[sa.Connection] = None

    @contextmanager
    def atomic(self) -> Iterator[None]:
        """One real transaction — both-or-neither, from the driver."""
        with self._engine.begin() as conn:
            self._conn = conn
            try:
                yield
            finally:
                self._conn = None

    def _execute(self, statement):
        if self._conn is None:
            raise RuntimeError("store writes must run inside atomic()")
        return self._conn.execute(statement)

    def put_application(self, application: PendingApplication) -> None:
        self._execute(
            sa.dialects.postgresql.insert(pending_application)
            .values(
                application_id=application.application_id,
                state=application.state.value,
                profile_canonical=application.profile_canonical,
                profile_content_hash=application.profile_content_hash,
                rule_results_canonical=application.rule_results_canonical,
                rule_results_content_hash=application.rule_results_content_hash,
                rulebook_version=application.rulebook_version,
                engine_version=application.engine_version,
            )
            .on_conflict_do_update(
                index_elements=["application_id"],
                set_={
                    "state": application.state.value,
                    "rule_results_canonical": application.rule_results_canonical,
                    "rule_results_content_hash": application.rule_results_content_hash,
                    "rulebook_version": application.rulebook_version,
                    "engine_version": application.engine_version,
                },
            )
        )

    def get_application(self, application_id: str) -> Optional[PendingApplication]:
        with self._engine.connect() as conn:
            row = conn.execute(
                sa.select(pending_application).where(
                    pending_application.c.application_id == application_id
                )
            ).mappings().first()
        if row is None:
            return None
        return PendingApplication(
            application_id=row["application_id"],
            state=CaseState(row["state"]),
            profile_canonical=bytes(row["profile_canonical"]),
            profile_content_hash=row["profile_content_hash"],
            rule_results_canonical=(
                bytes(row["rule_results_canonical"])
                if row["rule_results_canonical"] is not None
                else None
            ),
            rule_results_content_hash=row["rule_results_content_hash"],
            rulebook_version=row["rulebook_version"],
            engine_version=row["engine_version"],
        )

    def put_recommendation(self, recommendation: PendingRecommendation) -> None:
        self._execute(
            pending_recommendation.insert().values(
                recommendation_id=recommendation.recommendation_id,
                application_id=recommendation.application_id,
                memo_canonical=recommendation.memo_canonical,
                memo_hash=recommendation.memo_hash,
                model_version=recommendation.model_version,
                engine_version=recommendation.engine_version,
                rulebook_version=recommendation.rulebook_version,
                outlier_canonical=recommendation.outlier_canonical,
            )
        )

    def _recommendation_row(self, clause):
        with self._engine.connect() as conn:
            return conn.execute(
                sa.select(pending_recommendation).where(clause)
            ).mappings().first()

    @staticmethod
    def _to_recommendation(row) -> PendingRecommendation:
        return PendingRecommendation(
            recommendation_id=row["recommendation_id"],
            application_id=row["application_id"],
            memo_canonical=bytes(row["memo_canonical"]),
            memo_hash=row["memo_hash"],
            model_version=row["model_version"],
            engine_version=row["engine_version"],
            rulebook_version=row["rulebook_version"],
            outlier_canonical=(
                bytes(row["outlier_canonical"])
                if row["outlier_canonical"] is not None
                else None
            ),
        )

    def get_recommendation(
        self, recommendation_id: str
    ) -> Optional[PendingRecommendation]:
        row = self._recommendation_row(
            pending_recommendation.c.recommendation_id == recommendation_id
        )
        return None if row is None else self._to_recommendation(row)

    def recommendation_for_application(
        self, application_id: str
    ) -> Optional[PendingRecommendation]:
        row = self._recommendation_row(
            pending_recommendation.c.application_id == application_id
        )
        return None if row is None else self._to_recommendation(row)

    def list_application_ids(self) -> list[str]:
        """⚑ AUTHORIZED U24 REOPENING (Scope B wiring pass, Q1-A) — R2's enumeration primitive.

        ⚑ **Selects the PK column ONLY.** It rehydrates nothing and therefore performs **no
        canonicalization** — ADAPTER-1's positive assertion that this shim *"contains no
        canonicalization call at all"* holds **unchanged**.

        A plain read outside ``atomic()``, mirroring ``get_application``/``_recommendation_row``
        (the ``_execute``-inside-``atomic()`` discipline governs WRITES only).
        """
        with self._engine.connect() as conn:
            rows = conn.execute(
                sa.select(pending_application.c.application_id).order_by(
                    pending_application.c.application_id
                )
            ).scalars().all()
        return list(rows)

    # --- register #19: the two-step commit claim ------------------------------------------

    def _owning_application_id(self):
        """The join U24 performs INTERNALLY (A2) — recommendation -> its owning application.

        A correlated scalar subquery, so the whole compare-and-swap stays **one statement** and
        the composition root never resolves the mapping itself.
        """
        return (
            sa.select(pending_recommendation.c.application_id)
            .where(pending_recommendation.c.recommendation_id == sa.bindparam("rid"))
            .scalar_subquery()
        )

    def _swap_state(self, recommendation_id: str, expected: CaseState, new: CaseState) -> int:
        """One conditional ``UPDATE``; returns the row count. **Opens its own transaction.**

        ⚑ The ``AND state = :expected`` clause is the entire guarantee. Concurrent callers
        serialize on the row's write lock, so **exactly one** sees ``rowcount == 1`` — the
        property that eliminates duplicate ``AuditRecord``s, provided by Postgres rather than
        by application timing. Proven at tier-I in ``test_claim_integration.py``.
        """
        statement = (
            sa.update(pending_application)
            .where(
                pending_application.c.application_id == self._owning_application_id(),
                pending_application.c.state == expected.value,
            )
            .values(state=new.value)
        )
        with self._engine.begin() as conn:
            return conn.execute(statement, {"rid": recommendation_id}).rowcount

    def _recommendation_exists(self, recommendation_id: str) -> bool:
        """Existence only — **not** an authorization decision (COMMITBOUND-1)."""
        with self._engine.connect() as conn:
            return conn.execute(
                sa.select(sa.literal(1)).where(
                    pending_recommendation.c.recommendation_id == recommendation_id
                )
            ).first() is not None

    def claim_for_commit(self, recommendation_id: str) -> CommitClaimResult:
        """CAS ``drafted -> committing``. See :class:`CommitClaimResult`.

        ⚑ ``rowcount == 0`` is AMBIGUOUS on its own — it means *either* "not drafted" *or*
        "no such recommendation". The existence check that disambiguates runs **only on that
        failure branch**, decides no write, and races with nothing: a ``pending_recommendation``
        row is never deleted anywhere in this build, so "absent" is a stable fact.
        """
        if self._swap_state(recommendation_id, CaseState.DRAFTED, CaseState.COMMITTING):
            return CommitClaimResult.WON
        if self._recommendation_exists(recommendation_id):
            return CommitClaimResult.LOST
        return CommitClaimResult.NOT_FOUND

    def finalize_commit(self, recommendation_id: str) -> None:
        """``committing -> committed``, after the frozen service's audit write returned."""
        self._swap_state(recommendation_id, CaseState.COMMITTING, CaseState.COMMITTED)

    def release_claim(self, recommendation_id: str) -> None:
        """``committing -> drafted`` — recovery, so a rejected attempt stays retryable."""
        self._swap_state(recommendation_id, CaseState.COMMITTING, CaseState.DRAFTED)
