"""NFR-CASE-ADAPTER-1 (P-CASE-2) — LOAD-BEARING (full-highest). BR-CASE-8.

⚑ **The STRUCTURAL half of a deliberate PAIR.** This file reads the **AST** — what code may
invoke, and how. Its partner ``test_canon.py`` (CANON-1) reads the **bytes**.

**Neither alone is sufficient**: CANON-1 would still pass on a **correct-but-FORKED** serializer;
this file would still pass on a **broken** one. Two targets → two files (the measured
``test_noedit.py`` / ``test_nometric.py`` precedent), with the pairing carried here in prose.

⚑ **``repository.py`` IS IN THE SCAN SET** (CASE-Req-Fold-3). The coverage `omit` governs *where*
it is exercised (tier-I), **never** *what it may contain*. This file additionally asserts
**positively** that the shim contains **no canonicalization call at all** — so *"the shim doesn't
canonicalize"* is a **tested property, not a design intention**.
"""
from __future__ import annotations

from backend.case_lifecycle.tests import structural as sg


def test_no_production_module_serializes_directly_no_exception_anywhere():
    """⚑ The SERIALIZE direction — forbidden EVERYWHERE, with NO allowlist, ever.

    U24 canonicalizes **only** through the frozen ``CanonSerAdapter``. The Q14-A reopening
    narrowed the DESERIALIZE half (below); it did **not** touch this one, and this assertion is
    deliberately kept separate so the two can never be relaxed together by accident.
    """
    scanned = 0
    for path in sg.production_py_files():
        called = sg.called_names(sg.parse(path))
        for forbidden in sg.FORBIDDEN_CANON_CALLS_UNIVERSAL:
            assert forbidden not in called, (path.name, forbidden)
        scanned += 1
    # non-vacuity: the scan really covered the production set
    assert {p.name for p in sg.production_py_files()} >= sg.EXPECTED_PRODUCTION_MODULES
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)


def test_only_the_allowlisted_module_deserializes_directly():
    """⚑ ADAPTER-1 NARROWED (Q14-A) — ``canon_deserialize`` in EXACTLY ONE module.

    *Before* the reopening: no production module may call it. *After*: exactly one designated
    module may, for rehydration only. **Strictly more specific, not more permissive** — every
    module outside the allowlist is still held to the original prohibition, asserted here.
    """
    for path in sg.production_py_files():
        called = sg.called_names(sg.parse(path))
        if path.name in sg.CANON_DESERIALIZE_ALLOWLIST:
            continue
        assert "canon_deserialize" not in called, (
            f"{path.name} is not on the canon_deserialize allowlist"
        )


def test_the_allowlist_holds_exactly_one_module_and_it_exists():
    """The allowlist is a NARROW exception, not an open door — one entry, and it is real."""
    assert sg.CANON_DESERIALIZE_ALLOWLIST == {"memo_adapter.py"}
    assert sg.module_file("memo_adapter.py").exists()


def test_the_allowlisted_adapter_is_thin_and_rehydrates_only():
    """⚑ POSITIVE assertion — the exception buys rehydration, nothing else.

    An allowlist that only said "this module may call ``canon_deserialize``" would permit
    arbitrary logic to accumulate behind the exemption. This asserts what the module actually
    contains: it deserializes and validates, it does **not** serialize, and it re-implements no
    reduction of its own.
    """
    tree = sg.parse(sg.module_file("memo_adapter.py"))
    called = sg.called_names(tree)

    assert "canon_deserialize" in called, "non-vacuity: the adapter really is the rehydration seam"
    assert "model_validate" in called, "it validates into the frozen schema, never a raw dict"

    # the serialize direction stays with the FROZEN adapter — no fork here
    assert "canon_ser" not in called
    assert "canonical_bytes" not in called
    assert "content_hash" not in called
    # and no model_dump reduction is re-implemented (the P2 Decimal-fidelity hazard)
    assert "model_dump" not in called
    assert sg.keyword_values(tree, "mode") == []


def test_detector_a_synthetic_deserialize_outside_the_allowlist_is_flagged():
    """Non-vacuity for the allowlist: the scan really would catch an unlisted caller."""
    called = sg.called_names(sg.parse_source("x = canon_deserialize(b'{}')\n"))
    assert "canon_deserialize" in called
    assert "pipeline.py" not in sg.CANON_DESERIALIZE_ALLOWLIST


def test_no_production_module_reimplements_the_model_dump_reduction():
    """⚑ `mode="json"` would pre-stringify Decimals so the `$dec` envelope never fires,
    SILENTLY losing P2 fidelity. Only the frozen adapter may perform the reduction."""
    for path in sg.production_py_files():
        tree = sg.parse(path)
        assert "model_dump" not in sg.called_names(tree), path.name
        assert sg.keyword_values(tree, "mode") == [], path.name


def test_the_sql_exec_shim_is_in_the_scan_set():
    """⚑ CASE-Req-Fold-3 — coverage-omitted does NOT mean scan-excluded."""
    names = {p.name for p in sg.production_py_files()}
    assert "repository.py" in names


def test_the_shim_contains_no_canonicalization_call_at_all():
    """A POSITIVE assertion about the omitted module's contents."""
    tree = sg.parse(sg.module_file("repository.py"))
    called = sg.called_names(tree)
    for forbidden in (*sg.FORBIDDEN_CANON_CALLS, "canonical_bytes", "content_hash", "model_dump"):
        assert forbidden not in called
    assert "CanonSerAdapter" not in sg.imported_roots(tree)


def test_canonicalization_goes_through_the_frozen_adapter():
    """The pipeline and provider USE the frozen adapter — non-vacuity for the scans above."""
    for name in ("pipeline.py", "provider.py"):
        called = sg.called_names(sg.parse(sg.module_file(name)))
        assert called & {"canonical_bytes", "content_hash", "profile_from_canonical",
                         "report_from_canonical"}, name


def test_detector_a_synthetic_direct_canon_ser_call_is_flagged():
    called = sg.called_names(sg.parse_source("x = canon_ser({'a': 1})\n"))
    assert "canon_ser" in called


def test_detector_a_synthetic_model_dump_json_mode_is_flagged():
    tree = sg.parse_source('x = model.model_dump(mode="json")\n')
    assert "model_dump" in sg.called_names(tree)
    assert sg.keyword_values(tree, "mode") == ["json"]


def test_no_dollar_prefixed_key_appears_in_any_u24_payload():
    """CANON-SER reserves `$`-prefixed keys."""
    for path in sg.authored_py_files():
        if path.name in {"structural.py", "test_adapter.py"}:
            continue  # hold the reserved-prefix token by necessity
        for literal in sg.string_constants(sg.parse(path)):
            assert not literal.startswith("$"), (path.name, literal)
