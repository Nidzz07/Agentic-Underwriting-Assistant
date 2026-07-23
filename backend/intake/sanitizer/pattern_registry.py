"""PatternRegistry — versioned, data-defined injection matchers + inert placeholder.

FD ``business-rules.md §4`` (SR-DETECT categories) + NFR Design §2/§2.1. One
deterministic matcher per category, applied over the normalized detection view
(built by :mod:`backend.intake.sanitizer.normalizer`). Pure Python, NO LLM (an
LLM would be non-deterministic and itself a new injection surface — D4).

The **inert placeholder** replaces every neutralized span. Its inertness is a
pinned property (tested in ``test_pattern_registry.py``):

  P1  it matches no matcher (a second pass finds nothing to defang), and
  P2  it is self-delimiting — bracketed by Unicode Private-Use-Area sentinels
      that appear in no matcher pattern, so no match can span its boundary.

Together these make ``sanitize∘sanitize == sanitize`` hold by construction.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from backend.intake.schema import PatternCategory

# Private-Use-Area sentinels bracket the placeholder so it is opaque and
# self-delimiting (no matcher alphabet contains these code points).
_PUA_OPEN = chr(0xE000)   # U+E000 Private Use Area sentinel (open)
_PUA_CLOSE = chr(0xE001)  # U+E001 Private Use Area sentinel (close)
PLACEHOLDER = f"{_PUA_OPEN}NEUTRALIZED{_PUA_CLOSE}"

_FLAGS = re.IGNORECASE

# One pattern per category. Detection runs on the normalized (case-folded,
# NFKC) view, so these are written against folded text; IGNORECASE is
# belt-and-suspenders.
_PATTERNS: dict[PatternCategory, str] = {
    PatternCategory.INSTRUCTION_OVERRIDE: (
        r"(?:ignore|disregard|forget|override|bypass)\b[\s\S]{0,40}?"
        r"\b(?:previous|prior|above|earlier|all|the)\b[\s\S]{0,20}?"
        r"\b(?:instructions?|prompts?|rules?|directives?|context|commands?)\b"
    ),
    PatternCategory.ROLE_INJECTION: (
        r"\b(?:you\s+are\s+now|pretend\s+to\s+be|roleplay\s+as|"
        r"new\s+persona|from\s+now\s+on\s+you)\b"
        # "act as" is precision-tuned: it only fires before a system/AI/role
        # object, so benign underwriting phrasing ("act as a co-signer") does
        # not false-positive while "act as the system admin" still matches.
        r"|\bact\s+as\s+(?:an?\s+|the\s+)?(?:system|assistant|admin\w*|root|ai|"
        r"model|bot|underwrit\w*|compliance|officer|persona|character|develop\w*)\b"
        r"|(?:(?:^|\n)\s*(?:system|assistant)\s*:)"
    ),
    PatternCategory.DELIMITER_ESCAPE: (
        r"```"
        r"|<\|[\s\S]*?\|>"
        r"|\[/?INST\]"
        r"|</?(?:system|user|assistant|im_start|im_end)\b[^>]*>"
    ),
    PatternCategory.TOOL_MIMIC: (
        r"<(?:function_calls?|invoke|tool_call|tool_use)\b"
        r"|\bfunction\.call\s*\("
        r"|\"(?:tool|function)_?call\"\s*:"
    ),
}


@dataclass(frozen=True)
class Matcher:
    category: PatternCategory
    pattern: re.Pattern


@dataclass(frozen=True, order=True)
class Match:
    start: int
    end: int
    category: PatternCategory


class PatternRegistry:
    """The versioned matcher set + the inert placeholder."""

    version = "1.0.0"
    placeholder = PLACEHOLDER

    def __init__(self) -> None:
        # Fixed, declared order (SR-DETECT category order).
        self.matchers: list[Matcher] = [
            Matcher(category=cat, pattern=re.compile(pat, _FLAGS))
            for cat, pat in _PATTERNS.items()
        ]

    def find_matches(self, text: str) -> list[Match]:
        """All matcher hits over ``text``, sorted and merged into
        non-overlapping runs (a run keeps the category of its first hit)."""
        raw: list[Match] = []
        for m in self.matchers:
            for hit in m.pattern.finditer(text):
                if hit.start() == hit.end():  # pragma: no cover - anchored patterns
                    continue  # defensive: these patterns never match zero-width
                raw.append(Match(hit.start(), hit.end(), m.category))
        if not raw:
            return []
        raw.sort()
        merged: list[Match] = [raw[0]]
        for cur in raw[1:]:
            last = merged[-1]
            if cur.start < last.end:  # overlap -> extend the run to the max end
                merged[-1] = Match(last.start, max(last.end, cur.end), last.category)
            else:
                merged.append(cur)
        return merged
