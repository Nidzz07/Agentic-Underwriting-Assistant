"""MissingInfoDeriver — MISSINGINFO-1 (deterministic, fixed total cross-source order)."""
from __future__ import annotations

import inspect

from backend.intake.schema import DocStatus, DocType, DocumentEntry
from backend.memo_agent_core.missing_info import MissingInfoDeriver
from backend.memo_agent_core.schemas import MissingInfoSource
from backend.memo_agent_core.tests.fixtures.factories import make_input, make_profile, make_report


DERIVER = MissingInfoDeriver()


def _entry(doc_type: DocType, status: DocStatus) -> DocumentEntry:
    return DocumentEntry(doc_type=doc_type, status=status, content_hash="")


def test_no_gaps_when_clean():
    result = DERIVER.derive(make_input())  # all parsed, all evaluated, not incomplete
    assert result == []


def test_derives_from_all_three_signal_sources():
    profile = make_profile(
        incomplete=True,
        entries=[
            _entry(DocType.SALARY_SLIP, DocStatus.MISSING),
            _entry(DocType.BANK_STATEMENT, DocStatus.UNPARSEABLE),
        ],
    )
    report = make_report(rule_ids=("R-AGE-1", "R-DTI-1"), not_evaluated=("R-DTI-1",))
    result = DERIVER.derive(make_input(profile=profile, report=report))
    got = [(i.source, i.detail) for i in result]
    assert got == [
        (MissingInfoSource.MISSING_DOCUMENT, "salary_slip"),
        (MissingInfoSource.UNPARSEABLE_DOCUMENT, "bank_statement"),
        (MissingInfoSource.NOT_EVALUATED_RULE, "R-DTI-1"),
        (MissingInfoSource.INCOMPLETE_FLAG, "profile_incomplete"),
    ]


def test_fixed_total_order_is_source_major_then_detail():
    # Two missing docs supplied OUT of doc_type order → sorted within source.
    profile = make_profile(
        entries=[
            _entry(DocType.MEDICAL_QUESTIONNAIRE, DocStatus.MISSING),
            _entry(DocType.BANK_STATEMENT, DocStatus.MISSING),
        ],
    )
    result = DERIVER.derive(make_input(profile=profile))
    details = [i.detail for i in result]
    assert details == ["bank_statement", "medical_questionnaire"]  # within-source sorted
    assert all(i.source is MissingInfoSource.MISSING_DOCUMENT for i in result)


def test_byte_stable_regardless_of_input_iteration_order():
    # Same set of gaps, entries + rules listed in DIFFERENT orders → SAME output.
    entries_a = [
        _entry(DocType.SALARY_SLIP, DocStatus.MISSING),
        _entry(DocType.BANK_STATEMENT, DocStatus.UNPARSEABLE),
    ]
    entries_b = list(reversed(entries_a))
    report_a = make_report(rule_ids=("R-AGE-1", "R-DTI-1"), not_evaluated=("R-AGE-1", "R-DTI-1"))
    report_b = make_report(rule_ids=("R-DTI-1", "R-AGE-1"), not_evaluated=("R-AGE-1", "R-DTI-1"))
    out_a = DERIVER.derive(make_input(profile=make_profile(incomplete=True, entries=entries_a), report=report_a))
    out_b = DERIVER.derive(make_input(profile=make_profile(incomplete=True, entries=entries_b), report=report_b))
    assert out_a == out_b


def test_deterministic_across_runs():
    agent_input = make_input(
        profile=make_profile(incomplete=True, entries=[_entry(DocType.SALARY_SLIP, DocStatus.MISSING)]),
        report=make_report(not_evaluated=("R-DTI-1",)),
    )
    outputs = [DERIVER.derive(agent_input) for _ in range(5)]
    assert all(o == outputs[0] for o in outputs)


def test_derive_takes_only_the_agent_input_no_provider():
    # MISSINGINFO-1 is fully deterministic — no provider parameter.
    assert list(inspect.signature(MissingInfoDeriver.derive).parameters) == ["self", "agent_input"]
