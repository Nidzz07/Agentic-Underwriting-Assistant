"""ENUMERATE-1 — the AUTHORIZED U24 REOPENING's enumeration primitive (Scope B wiring, Q1-A).

⚑ **Why this target exists.** R2 (``GET /applications?page=&size=``) is a **paginated list**, and
the ``CaseStore`` Protocol previously exposed **no enumeration primitive at all** — every method
was keyed by a single id. R2 was therefore **not implementable** against U24's public surface.
This file is the tier-U half of the reopening that fixes it; **PERSIST-1** (tier-I) is what checks
the SQL shim agrees with the fake.

⚑ **The load-bearing property asserted here**: ``list_application_ids`` returns **IDS ONLY** and
performs **no rehydration**, so ``repository.py`` stays free of any canonicalization call and
**ADAPTER-1's positive assertion is not weakened**. That is asserted STRUCTURALLY below, not just
described — a returns-ids-shaped test would pass on an implementation that rehydrated internally
and threw the aggregates away.
"""
from __future__ import annotations

from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.tests import fixtures as fx
from backend.case_lifecycle.tests import structural as sg


def _store_with(*application_ids: str) -> fx.InMemoryCaseStore:
    """Populate through the real ``submit()`` path — never by reaching into the fake."""
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(store, fx.drafting_success_double(), fx.recommendation_id_factory)
    _, raw = fx.clean_case()
    for application_id in application_ids:
        pipeline.submit(application_id, raw)
    return store


def test_an_empty_store_enumerates_to_an_empty_list():
    """Not an error, not None — an empty list is a truthful answer to a valid query."""
    assert fx.InMemoryCaseStore().list_application_ids() == []


def test_every_stored_application_id_is_returned():
    store = _store_with("case-b", "case-a", "case-c")
    assert set(store.list_application_ids()) == {"case-a", "case-b", "case-c"}


def test_the_order_is_deterministic_and_sorted():
    """The fake mirrors the shim's ``ORDER BY application_id`` so the two agree (PERSIST-1)."""
    assert _store_with("case-c", "case-a", "case-b").list_application_ids() == [
        "case-a",
        "case-b",
        "case-c",
    ]


def test_enumeration_is_a_pure_read_and_mutates_nothing():
    store = _store_with("case-a", "case-b")
    entries_before = store.atomic_entries
    store.list_application_ids()
    store.list_application_ids()
    assert store.atomic_entries == entries_before, "enumeration must open no transaction"
    assert set(store.list_application_ids()) == {"case-a", "case-b"}


def test_ids_only_no_aggregate_is_returned():
    """⚑ The wire-shape guarantee: ids, never rehydrated ``PendingApplication`` objects."""
    for application_id in _store_with("case-a").list_application_ids():
        assert isinstance(application_id, str)


# --- the structural half — ADAPTER-1 must not be weakened by this reopening ---------------

def test_the_shim_enumeration_performs_no_canonicalization():
    """⚑ STRUCTURAL, not behavioural.

    A returns-ids test would still pass on an implementation that rehydrated internally and
    discarded the aggregates. This asserts the shim contains **no canonicalization call at all**
    — the same POSITIVE assertion ADAPTER-1 makes — re-checked HERE so the reopening cannot
    quietly erode it in a future edit.
    """
    tree = sg.parse(sg.module_file("repository.py"))
    called = sg.called_names(tree)
    for forbidden in (*sg.FORBIDDEN_CANON_CALLS, "canonical_bytes", "content_hash", "model_dump"):
        assert forbidden not in called
    assert "CanonSerAdapter" not in sg.imported_roots(tree)


def test_the_list_method_reopening_added_no_production_module():
    """⚑ THIS reopening's blast radius: METHODS on existing modules, never a new module.

    The list method went into ``store.py``/``repository.py``, both of which already existed, so
    the Q1-A reopening contributed **nothing** to ``EXPECTED_PRODUCTION_MODULES`` — the
    correction issued during the Scope B wiring pass's ambiguity-check.

    ⚑ Asserted by NAME, not by COUNT, deliberately. A count assertion would break every time an
    unrelated authorized reopening added a module — as Q14-A's ``memo_adapter.py`` immediately
    did — and would say nothing about whether THIS reopening stayed in its lane. The names are
    what the claim is actually about.
    """
    modules = {p.name for p in sg.production_py_files()}
    assert modules >= sg.EXPECTED_PRODUCTION_MODULES
    for owned_by_this_reopening in ("store.py", "repository.py"):
        assert owned_by_this_reopening in sg.EXPECTED_PRODUCTION_MODULES
    # the list method added no module of its own — there is no "enumerate"/"list" module
    assert not any("enumerat" in name or name.startswith("list") for name in modules)


def test_the_protocol_and_the_fake_expose_the_same_enumeration_method():
    """Non-vacuity: the Protocol declares it and the tier-U fake implements it."""
    from backend.case_lifecycle.store import CaseStore

    assert hasattr(CaseStore, "list_application_ids")
    assert callable(fx.InMemoryCaseStore().list_application_ids)
