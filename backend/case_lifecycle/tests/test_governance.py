"""NFR-CASE-SEC-1 (P-CASE-15) — the Security-Guardrails governance posture.

Scoped exclusions (not a runtime test): this suite tests ONLY `case-lifecycle`. It does NOT test
other units, the WIRE-1 route bindings (a later wiring pass), the frozen commit enforcement
(U12's), memo generation (U4's), routing LOGIC (U19's — U24 asserts only that it is INVOKED), or
the tier-B corpus (NOT authorized).
"""
from __future__ import annotations

from backend.case_lifecycle.tests import structural as sg

_NETWORK_ROOTS = ("requests", "httpx", "urllib", "socket", "subprocess", "aiohttp")
_SECRET_TOKENS = ("api_key", "secret_key", "sk-", "os.environ", "getenv")


def test_no_production_module_opens_a_network_connection_or_spawns_a_process():
    for path in sg.production_py_files():
        roots = sg.imported_roots(sg.parse(path))
        assert not (roots & set(_NETWORK_ROOTS)), path.name


def test_no_u24_module_reads_a_secret_or_an_environment_variable():
    """Engines come from secrets-config (SEC-3); NO key is read at tier-U."""
    scanned = 0
    for path in sg.authored_py_files():
        if path.name == "test_governance.py":
            continue  # holds the token list itself
        text = path.read_text(encoding="utf-8")
        for token in _SECRET_TOKENS:
            assert token not in text, (path.name, token)
        scanned += 1
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)


def test_u24_declares_no_route_and_no_verdict():
    """Precise: EXACT annotation identifiers, never a substring (``PendingRecommendation``
    legitimately contains ``Recommendation``)."""
    for path in sg.production_py_files():
        tree = sg.parse(path)
        code = sg.executable_text(tree)
        assert "APIRouter" not in code, path.name
        # the FROZEN verdict type must appear in no U24 annotation
        assert "Recommendation" not in sg.annotation_names(tree), path.name
        assert "Confidence" not in sg.annotation_names(tree), path.name


def test_u24_adds_no_new_dependency_beyond_the_standard_library_and_frozen_units():
    allowed = {"backend", "dataclasses", "enum", "typing", "__future__", "contextlib",
               "pathlib", "sqlalchemy"}
    for path in sg.production_py_files():
        roots = sg.imported_roots(sg.parse(path))
        assert roots <= allowed, (path.name, roots - allowed)


def test_the_two_register_items_are_named_and_not_discharged():
    """#13 NOTWIRED-FILENAME-STALE (amplified) and #14 MEMOVIEW-FAILED-STATE-UNMODELLED."""
    from backend.case_lifecycle import states

    doc = states.__doc__ or ""
    assert "MEMOVIEW-FAILED-STATE-UNMODELLED" in doc
    assert "claims NO discharge" in doc


def test_the_header_comments_document_but_do_not_enforce():
    for path in sg.production_py_files():
        if path.name == "__init__.py":
            continue
        doc = path.read_text(encoding="utf-8")
        assert "DOCUMENTATION ONLY" in doc, path.name
        assert "never enforcement" in doc, path.name
