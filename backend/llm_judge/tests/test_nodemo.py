"""NFR-JUDGE-NODEMO-1 (P-JUDGE-11) — no demographic identifier anywhere. BR-JUDGE-10 / CON-BR1.

⚑ SCOPE (CG-JUDGE-Fold-3) — deliberately ASYMMETRIC to ADVISORY-1's token scan: this scan
ALSO covers ``tests/fixtures.py``, because the FD explicitly requires the HAND-AUTHORED
REFERENCE MEMO be demographic-free. (ADVISORY-1's verdict scan must exclude fixtures, since
the frozen U4 ``DecisionMemo.recommendation`` field is required.)

Belt and braces: the scan is the belt; the braces are structural — ``JudgedSample`` carries
``memo`` + ``rule_report`` + ``provider`` ONLY, with NO ``ApplicantProfile`` field, so no
demographic value can enter a judged sample at all.
"""
from __future__ import annotations

from dataclasses import fields

from backend.llm_judge.schemas import JudgedSample
from backend.llm_judge.tests import fixtures as fx
from backend.llm_judge.tests import structural as sg


def _demographic_hits(text: str) -> list[str]:
    return [t for t in sg.DEMOGRAPHIC_TOKENS if sg.contains_token(text, t)]


def test_no_demographic_token_in_any_u22_module_including_the_fixtures():
    scanned = 0
    for path in sg.authored_py_files():
        if path.name in {"structural.py", "test_nodemo.py", "test_structural_guard.py"}:
            # These three hold demographic tokens BY NECESSITY: the token list itself, the
            # planted detector token, and the substrate's whole-word collision guard.
            # Every other U22 module - all four production modules and the fixtures that
            # carry the reference memo - IS scanned.
            continue
        hits = _demographic_hits(path.read_text(encoding="utf-8"))
        assert not hits, f"{path.name}: {hits}"
        scanned += 1
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)  # non-vacuity


def test_the_reference_memo_carries_no_demographic_identifier():
    memo = fx.reference_memo()
    hits = _demographic_hits(memo.narrative_prose)
    assert not hits, hits


def test_every_judged_sample_prose_is_demographic_free():
    for sample in fx.exemption_composition() + list(fx.anchoring_pair()):
        assert not _demographic_hits(sample.memo.narrative_prose), sample.sample_id


def test_detector_a_planted_demographic_token_is_flagged():
    """The scan is non-vacuous: a synthetic memo carrying a demographic token IS caught."""
    planted = (
        "The applicant full_name Asha Rao of city Pune has a debt-to-income ratio of 46 "
        "percent; the recommendation is to refer."
    )
    hits = _demographic_hits(planted)
    assert "full_name" in hits
    assert "city" in hits


def test_detector_flags_each_demographic_token_individually():
    for token in sg.DEMOGRAPHIC_TOKENS:
        assert _demographic_hits(f"prose containing {token} here") == [token]


def test_judged_sample_structurally_carries_no_applicant_profile():
    """The braces: a demographic field cannot structurally enter a judged sample."""
    names = {f.name for f in fields(JudgedSample)}
    assert names == {"sample_id", "memo", "rule_report", "provider"}
    assert "applicant_profile" not in names
    assert "demographics" not in names
