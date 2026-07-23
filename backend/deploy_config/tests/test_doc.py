"""NFR-DEP-DOC-1: the deploy doc is checklist-complete — every required marker token present
(Q3). A precise TOKEN-SET match, not a heading match, not a prose-quality judgement (Req-Fold-2).
"""
from __future__ import annotations

from backend.deploy_config.tests import structural as sg

#: The five required section markers (NFR Design / Infra §3.7). Exact literals.
REQUIRED_TOKENS = (
    "ROUTE-STATUS:",
    "Q1-B-DIVERGENCE:",
    "AC-7-CONTINGENCY:",
    "FREE-TIER:",
    "ENV-SHAPES:",
)


def _missing(doc: str) -> list[str]:
    return [t for t in REQUIRED_TOKENS if t not in doc]


def test_deploy_doc_contains_every_required_token():
    assert _missing(sg.read(sg.DEPLOY_DOC)) == []


def test_detector_flags_a_doc_missing_a_section():
    doc = sg.read(sg.DEPLOY_DOC).replace("AC-7-CONTINGENCY:", "REMOVED")
    assert "AC-7-CONTINGENCY:" in _missing(doc)


def test_an_unrelated_heading_does_not_satisfy_the_check():
    # Non-vacuity: matching is on the TOKEN SET, not any heading — an unrelated heading fails.
    assert set(_missing("## Some Unrelated Heading\ntext")) == set(REQUIRED_TOKENS)
