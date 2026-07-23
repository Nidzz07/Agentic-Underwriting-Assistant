"""CitationValidator — CITE-1 (report-membership + belt-and-suspenders, Hypothesis ∀)."""
from __future__ import annotations

import inspect

import pytest
from hypothesis import given, strategies as st

from backend.memo_agent_core.citation_validator import CitationValidator
from backend.memo_agent_core.schemas import CitationOutcome, MemoDraftOutput
from backend.memo_agent_core.tests.fixtures.factories import make_report, make_rulebook


def _draft(cited):
    return MemoDraftOutput(narrative_prose="prose", cited_rule_ids=list(cited))


def test_all_cited_in_report_and_rulebook_is_valid():
    report = make_report(rule_ids=("R-AGE-1", "R-DTI-1"))
    rulebook = make_rulebook(rule_ids=("R-AGE-1", "R-DTI-1"))
    result = CitationValidator(report).validate_citations(_draft(["R-AGE-1", "R-DTI-1"]), rulebook)
    assert result.all_valid is True
    assert result.outcome is CitationOutcome.VALID
    assert result.offending_cited_ids == []


def test_cited_in_rulebook_but_not_in_report_is_citation_failure():
    # A real rule that was NOT evaluated for this applicant → misapplication → fail.
    report = make_report(rule_ids=("R-AGE-1",))
    rulebook = make_rulebook(rule_ids=("R-AGE-1", "R-DTI-1"))
    result = CitationValidator(report).validate_citations(_draft(["R-DTI-1"]), rulebook)
    assert result.all_valid is False
    assert result.outcome is CitationOutcome.CITATION_FAILURE
    assert result.offending_cited_ids == ["R-DTI-1"]


def test_cited_not_in_rulebook_is_pure_hallucination_failure():
    report = make_report(rule_ids=("R-AGE-1",))
    rulebook = make_rulebook(rule_ids=("R-AGE-1",))
    result = CitationValidator(report).validate_citations(_draft(["R-FAKE-9"]), rulebook)
    assert result.outcome is CitationOutcome.CITATION_FAILURE
    assert result.offending_cited_ids == ["R-FAKE-9"]


def test_offending_ids_preserve_cited_order():
    report = make_report(rule_ids=("R-AGE-1",))
    rulebook = make_rulebook(rule_ids=("R-AGE-1",))
    result = CitationValidator(report).validate_citations(_draft(["R-X", "R-AGE-1", "R-Y"]), rulebook)
    assert result.offending_cited_ids == ["R-X", "R-Y"]


def test_validate_citations_keeps_the_frozen_2arg_signature():
    # Frozen C4 signature preserved: (self, memo_draft, rulebook). The report is
    # supplied at construction, not as a method parameter.
    params = list(inspect.signature(CitationValidator.validate_citations).parameters)
    assert params == ["self", "memo_draft", "rulebook"]
    assert list(inspect.signature(CitationValidator.__init__).parameters) == ["self", "report"]


_RULE_IDS = st.text(alphabet="ABCDR-0123", min_size=1, max_size=5)


@pytest.mark.property
@given(
    report_ids=st.lists(_RULE_IDS, max_size=6),
    rulebook_ids=st.lists(_RULE_IDS, max_size=6),
    cited=st.lists(_RULE_IDS, max_size=6),
)
def test_valid_iff_every_cited_id_in_report_and_rulebook(report_ids, rulebook_ids, cited):
    report = make_report(rule_ids=tuple(report_ids))
    rulebook = make_rulebook(rule_ids=tuple(rulebook_ids))
    result = CitationValidator(report).validate_citations(_draft(cited), rulebook)

    r_set, b_set = set(report_ids), set(rulebook_ids)
    expected_offending = [c for c in cited if c not in r_set or c not in b_set]
    if expected_offending:
        assert result.outcome is CitationOutcome.CITATION_FAILURE
        assert result.all_valid is False
        assert result.offending_cited_ids == expected_offending
    else:
        assert result.outcome is CitationOutcome.VALID
        assert result.all_valid is True
        assert result.offending_cited_ids == []
