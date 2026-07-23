"""NFR-JUDGE-CLIDEFER-1 (P-JUDGE-5) — the injected seam. BR-JUDGE-8 / Q3-A / Q2-A / Fold-1.

A TWO-PART contract, and the second part is part of the pattern, not a footnote:

  1. DELIVERED — the Protocol is SATISFIABLE and NON-VACUOUS, and no production module
     imports the promptfoo shim. The whole suite runs with no Node, no npx, no network, no
     telemetry, no key, no live LLM.
  2. ⚑ DELIBERATELY NOT DELIVERED — there is NO by-value interop replica. U19 could build
     one for U18's ``OutlierResult`` because that shape is FROZEN and ON-DISK — a verifiable
     mirror target. **For U22 that precondition is ABSENT**: the promptfoo CLI is not
     present and its output shape is external, version-dependent and unpinned. A replica
     would attest to an ASSUMPTION and pass green while the real interop was broken —
     worse than no test. Real-shape interop is the FIFTH discharge criterion instead.
"""
from __future__ import annotations

import sys

from backend.llm_judge.engine import (
    DEFERRED_REGISTER,
    PROMPTFOO_CLI_DEFERRED,
    RubricEngine,
    register_item,
)
from backend.llm_judge.tests import fixtures as fx
from backend.llm_judge.tests import structural as sg


def test_the_offline_fake_satisfies_the_protocol():
    assert isinstance(fx.DeclaredScoreEngine(), RubricEngine)


def test_the_protocol_check_is_not_vacuous():
    """The exact U19 non-vacuity assertion (``test_signal.py``)."""
    assert not isinstance(object(), RubricEngine)


def test_the_protocol_discriminates_on_the_score_method():
    class _NotAnEngine:
        def evaluate(self):  # wrong method name
            ...  # pragma: no cover

    assert not isinstance(_NotAnEngine(), RubricEngine)


def test_no_production_module_imports_the_promptfoo_shim():
    scanned = 0
    for path in sg.production_py_files():
        roots = sg.imported_roots(sg.parse(path))
        assert not (roots & sg.FORBIDDEN_PRODUCTION_IMPORTS), path.name
        scanned += 1
    # non-vacuity guard: the scan really did cover the production set
    assert {p.name for p in sg.production_py_files()} >= sg.EXPECTED_PRODUCTION_MODULES
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)


def test_detector_a_synthetic_promptfoo_import_is_flagged():
    roots = sg.imported_roots(sg.parse_source("import promptfoo\n"))
    assert roots & sg.FORBIDDEN_PRODUCTION_IMPORTS


def test_promptfoo_is_never_imported_into_the_running_test_process():
    """tier-U absence: no Node, no npx, no shim, no network."""
    assert "promptfoo" not in sys.modules


def test_the_cli_deferral_is_disclosed_with_its_five_discharge_criteria():
    item = register_item("PROMPTFOO-CLI-DEFERRED")
    assert item is PROMPTFOO_CLI_DEFERRED
    assert item.discharged is False
    assert len(item.discharge_criteria) == 5
    joined = " | ".join(item.discharge_criteria).lower()
    assert "pinned" in joined
    assert "telemetry opt-out" in joined
    assert "real-shape interop" in joined  # the criterion Q2-A newly named


def test_the_unpinned_npx_fetch_and_telemetry_concerns_are_disclosed():
    rationale = PROMPTFOO_CLI_DEFERRED.rationale.lower()
    assert "npx" in rationale
    assert "unpinned" in rationale
    assert "telemetry" in rationale


def test_no_register_item_claims_discharge():
    assert all(item.discharged is False for item in DEFERRED_REGISTER)
