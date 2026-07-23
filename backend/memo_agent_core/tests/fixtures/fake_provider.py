"""Scripted, call-count-aware FakeProvider — the ``ProviderAbstraction`` fake used
in ALL memo-agent-core tests (no live LLM, no network).

Returns the i-th canned ``MemoDraftOutput`` on the i-th ``complete()`` call
(the last entry repeats), and records every call's ``(prompt, schema)``. The
two CITE-FAILURE scripts are built by helpers whose length is **derived from
``MEMO_CITATION_RETRY_CAP``** — never a hardcoded parallel literal — so a change
to the cap can never silently desync the scripts from the cap.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from backend.memo_agent_core.schemas import MemoDraftOutput

#: A citation id that is never in any factory report/rulebook → always fails.
HALLUCINATED_ID = "R-HALLUCINATED-999"


@dataclass
class RecordedCall:
    prompt: str
    schema: type


class FakeProvider:
    """Implements ``ProviderAbstraction.complete(prompt, schema)`` deterministically."""

    def __init__(self, script: Sequence[MemoDraftOutput]) -> None:
        if not script:
            raise ValueError("FakeProvider needs at least one scripted output")
        self._script = list(script)
        self.calls: list[RecordedCall] = []

    def complete(self, prompt: str, schema: type[MemoDraftOutput]) -> MemoDraftOutput:
        index = min(len(self.calls), len(self._script) - 1)  # last repeats
        self.calls.append(RecordedCall(prompt=prompt, schema=schema))
        return self._script[index]

    @property
    def call_count(self) -> int:
        return len(self.calls)


def valid_output(cited_rule_ids: Sequence[str]) -> MemoDraftOutput:
    return MemoDraftOutput(
        narrative_prose="Advisory memo prose. This is a recommendation for underwriter review.",
        cited_rule_ids=list(cited_rule_ids),
    )


def hallucinated_output() -> MemoDraftOutput:
    return MemoDraftOutput(
        narrative_prose="Advisory memo prose citing a non-existent rule.",
        cited_rule_ids=[HALLUCINATED_ID],
    )


def recover_within_cap_script(cap: int, *, valid_cited: Sequence[str]) -> list[MemoDraftOutput]:
    """``(cap - 1)`` hallucinated drafts, then a valid draft at attempt ``k = cap``.

    Length derived from ``cap`` — a cap change re-derives the script, so the two
    can never desync (NFR-Design §5 sharpening).
    """
    return [hallucinated_output() for _ in range(cap - 1)] + [valid_output(valid_cited)]


def always_hallucinate_script() -> list[MemoDraftOutput]:
    """A single hallucinated output; ``FakeProvider``'s last-repeats rule makes it
    hallucinate on **every** attempt regardless of ``cap`` → exhaust-cap."""
    return [hallucinated_output()]
