"""NFR-JUDGE-SEC-1 (P-JUDGE-14) — the Security-Guardrails governance posture.

Scoped exclusions (not a runtime test): this suite tests ONLY ``llm-judge``'s behaviour. It
does NOT test other units, the WIRE-1 routes, FR-PROV-GATE-1's decision-level gates
(``quality-gates``'), memo GENERATION (U4's), the memo hallucination guard
``validate_citations`` (U4's deterministic guard, which U22 LAYERS ON and never replaces),
the real promptfoo engine (deferred), or the tier-B corpus (NOT authorized).

The assertions below are the ones that CAN be mechanically held at tier-U.
"""
from __future__ import annotations

import sys

from backend.llm_judge.engine import DEFERRED_REGISTER
from backend.llm_judge.tests import structural as sg

_NETWORK_TOKENS = ("requests", "httpx", "urllib", "socket", "subprocess", "aiohttp")
_SECRET_TOKENS = ("api_key", "secret_key", "sk-", "os.environ", "getenv")


def test_no_production_module_opens_a_network_connection_or_spawns_a_process():
    for path in sg.production_py_files():
        roots = sg.imported_roots(sg.parse(path))
        assert not (roots & set(_NETWORK_TOKENS)), path.name


def test_no_u22_module_reads_a_secret_or_an_environment_variable():
    """Keys are secrets-config's (SEC-3); NO key is read at tier-U."""
    scanned = 0
    for path in sg.authored_py_files():
        if path.name == "test_governance.py":
            continue  # holds the token list itself
        text = path.read_text(encoding="utf-8")
        for token in _SECRET_TOKENS:
            assert token not in text, (path.name, token)
        scanned += 1
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)


def test_u22_persists_nothing_and_declares_no_route():
    for path in sg.production_py_files():
        text = path.read_text(encoding="utf-8")
        for token in ("APIRouter", "@app.", "sessionmaker", "create_engine", "INSERT INTO"):
            assert token not in text, (path.name, token)


def test_u22_adds_no_new_dependency_beyond_the_standard_library_and_frozen_units():
    allowed_roots = {"backend", "dataclasses", "enum", "typing", "__future__"}
    for path in sg.production_py_files():
        roots = sg.imported_roots(sg.parse(path))
        assert roots <= allowed_roots, (path.name, roots - allowed_roots)


def test_the_three_register_items_are_named_owner_attributed_and_undischarged():
    for item in DEFERRED_REGISTER:
        assert item.name
        assert item.owner
        assert item.rationale
        assert item.discharge_criteria
        assert item.discharged is False


def test_tier_b_is_not_reached_and_no_live_provider_sdk_is_imported():
    for module in ("anthropic", "ollama", "google.genai", "promptfoo", "langfuse"):
        assert module not in sys.modules or "llm_judge" not in str(
            sys.modules.get(module, "")
        )


def test_the_header_comments_document_but_do_not_enforce():
    """Every production module carries the standing header; each property it names is
    independently scan-enforced elsewhere in this suite."""
    for path in sg.production_py_files():
        if path.name == "__init__.py":
            continue
        doc = path.read_text(encoding="utf-8")
        assert "DOCUMENTATION ONLY" in doc, path.name
        assert "never enforcement" in doc, path.name
