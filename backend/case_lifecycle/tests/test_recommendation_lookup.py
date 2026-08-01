"""LOOKUP-1 — resolving "the" recommendation for an application must be DETERMINISTIC.

⛔ **The defect (register #27, defect (i)).** ``_recommendation_row`` issued
``SELECT … WHERE application_id = ?`` with **no ``ORDER BY`` and no ``LIMIT``**, then took
``.first()`` in Python. ``application_id`` carries **no uniqueness guarantee** —
``0001_case_lifecycle.sql`` gives it only a **non-unique** index, and the PK is
``recommendation_id``. **The row served was therefore undefined by SQL semantics.** The
oldest-row behaviour observed in production was an artifact of Postgres seq-scanning an
insert-only table in heap order; a different plan, a ``VACUUM FULL``, or any row update could
change it **with no code change and no error**.

⚠️ **What this fix does NOT claim.** ``recommendation_id`` is ``f"REC-{application_id}-{uuid4}"``
— a **random** suffix — so ordering by it buys **determinism, not chronology**: a *stable* row,
not the *newest* one. Picking a "current" row would need a column that does not exist (a
timestamp or sequence), which is a migration and was explicitly out of scope. **Change (a) is
what stops new duplicates being created at all**; this is hardening for data that already has
them.

tier-U here: the statement is captured from the REAL ``_recommendation_row`` code path through a
recording engine — no database, no Docker. The tier-I counterpart lives in
``test_persist_integration.py``.
"""
from __future__ import annotations

from sqlalchemy.dialects import postgresql

from backend.case_lifecycle.repository import PostgresCaseStore


class _EmptyResult:
    def mappings(self):
        return self

    def first(self):
        return None


class _RecordingConnection:
    """Captures the statement instead of executing it."""

    def __init__(self, sink: list) -> None:
        self._sink = sink

    def execute(self, statement, *args, **kwargs):
        self._sink.append(statement)
        return _EmptyResult()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _RecordingEngine:
    def __init__(self) -> None:
        self.statements: list = []

    def connect(self):
        return _RecordingConnection(self.statements)


def _issued_sql(application_id: str = "case-lookup-1") -> str:
    engine = _RecordingEngine()
    PostgresCaseStore(engine).recommendation_for_application(application_id)
    assert engine.statements, "the lookup issued no statement at all"
    return str(engine.statements[0].compile(dialect=postgresql.dialect()))


def test_the_lookup_is_ordered_and_limited():
    """D1 — the query must not leave row selection to the query planner."""
    sql = _issued_sql()

    assert "ORDER BY" in sql, f"an unordered lookup over a non-unique column: {sql}"
    assert "LIMIT" in sql, f"an unlimited lookup taking .first() in Python: {sql}"


def test_the_ordering_key_is_the_primary_key():
    """The only orderable column that exists. ⚑ Pins WHICH key, so a later change to something
    meaningful (a timestamp, were one ever added) is a deliberate edit here rather than a silent
    behaviour change."""
    sql = _issued_sql()

    order_by = sql.split("ORDER BY", 1)[1]
    assert "recommendation_id" in order_by, f"ordered by something else: {order_by}"


def test_the_in_memory_double_resolves_the_same_row_as_the_shim():
    """E1 — the fake must AGREE with the shim, not merely be self-consistent.

    ⛔ **This is the test whose absence let register #27 reach production.** The double iterates
    an insertion-ordered dict and returned the **first inserted**; the shim returned whatever the
    planner happened to yield. `fixtures.py` claims *"PERSIST-1 is what keeps this fake and
    ``PostgresCaseStore`` honest about agreeing"* — for this method that claim was **false**, and
    a fake that cannot express the failure cannot catch the regression.

    Insertion order here is deliberately NOT the ordering-key order, so a double that still
    returns "first inserted" fails.
    """
    from backend.case_lifecycle.tests import fixtures as fx

    store = fx.InMemoryCaseStore()
    with store.atomic():
        store.put_application(fx.make_application("case-dupe-1"))
        for suffix in ("zzz", "aaa", "mmm"):          # inserted zzz FIRST, aaa second
            store.put_recommendation(
                fx.make_recommendation(f"rec-dupe-{suffix}", "case-dupe-1")
            )

    resolved = store.recommendation_for_application("case-dupe-1")

    assert resolved.recommendation_id == "rec-dupe-aaa", (
        "the double must resolve by the same ordering key the shim uses, not by insertion order"
    )
