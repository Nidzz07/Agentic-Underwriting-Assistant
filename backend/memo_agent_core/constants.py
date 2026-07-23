"""Single-sourced constants for memo-agent-core.

``MEMO_CITATION_RETRY_CAP`` is the ONE source of truth for the bounded
citation-retry cap (NFR-Design §5). The ``LangGraphOrchestrator`` AND both
CITE-FAILURE tests import THIS constant — no duplicated literals — so a change
here can never silently desync the test scripts from the cap.

Value >= 2 is required so the two retry directions are meaningfully distinct:
``recover-within-cap`` needs room for at least one prior failed draft before a
valid draft at attempt k <= cap; ``exhaust-cap`` needs at least two attempts to
prove the loop is genuinely bounded (not a single-shot). Concrete value = 2
(the minimum that satisfies both) — a realization detail, not a new design
decision (recorded in the code summary).
"""
from __future__ import annotations

#: Max number of draft attempts in the citation-validation retry loop (>= 2).
MEMO_CITATION_RETRY_CAP: int = 2
