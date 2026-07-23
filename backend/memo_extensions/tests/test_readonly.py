"""NFR-MEXT-MCPRO-1 — both tool surfaces are READ-ONLY (BR-MEXT-7 / SEC-4 / skill #2).
Runtime member check; the semantic (not word-matched) AST read-only scan — which correctly
does NOT flag ``compose_prompt`` — lives in ``test_structural_guard.py``.
"""
from __future__ import annotations

from backend.memo_extensions.mcp_tools import (
    DecisionsTools,
    McpToolService,
    RulebookTools,
)
from backend.memo_extensions.tests import fixtures as fx

_WRITE_PREFIXES = ("commit", "write", "persist", "update", "delete", "save", "insert", "mutate")


def test_no_write_member_on_any_handler_surface():
    for cls in (RulebookTools, DecisionsTools, McpToolService):
        public = [n for n in dir(cls) if not n.startswith("_")]
        offenders = [n for n in public if n.startswith(_WRITE_PREFIXES)]
        assert offenders == [], f"{cls.__name__} exposes write-like members: {offenders}"


def test_handler_reads_are_side_effect_free():
    service = fx.make_service()
    report = fx.make_report()
    first = service.supplementary_context(report)
    second = service.supplementary_context(report)
    assert first == second  # repeated reads identical → no mutation


def test_edges_exercised_read_only():
    # describe_rules + recent_precedent return data and mutate nothing observable.
    rulebook_tools = RulebookTools(fx.make_rulebook(("DTI-1",)))
    assert [d.rule_id for d in rulebook_tools.describe_rules(["DTI-1"])] == ["DTI-1"]
    assert rulebook_tools.describe_rules(["DTI-1"]) == rulebook_tools.describe_rules(["DTI-1"])


def test_describe_rules_skips_unknown_ids():
    rulebook_tools = RulebookTools(fx.make_rulebook(("DTI-1",)))
    assert [d.rule_id for d in rulebook_tools.describe_rules(["UNKNOWN-9"])] == []
    assert rulebook_tools.describe_rules(["DTI-1", "UNKNOWN-9"]) == rulebook_tools.describe_rules(["DTI-1"])
