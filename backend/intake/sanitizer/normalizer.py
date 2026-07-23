"""ObfuscationNormalizer — deterministic, detection-only normalization pre-pass.

FD ``business-logic-model`` + NFR Design §3. Builds a normalized DETECTION view
via a fixed, declared pipeline applied identically every run:

    NFKC  ->  case-fold  ->  collapse-whitespace  ->  strip-zero-width

The view is TRANSIENT — it is what the matchers scan; it NEVER becomes
``clean_text``. Neutralization edits map back to the ORIGINAL span via the
origin index map, so faithful output is preserved except for defanged spans.

Determinism note: NFKC output depends on the Unicode version bundled with the
Python runtime, pinned by the Python-version pin (tech-stack D6); the pipeline
is byte-stable for the pinned runtime. This serves single-run reproducibility +
the neutralization test — not replay (replay never re-sanitizes).

Implementation: NFKC + case-fold are applied per code point so an exact origin
index can be carried for every normalized character (each normalized char
records the ORIGINAL index it derives from). This is a detection normalization,
not a canonical text transform.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedView:
    """A normalized detection view plus provenance back to the original text.

    ``origin[i]`` is the original index of ``text[i]``; ``original_len`` is the
    length of the source string.
    """

    text: str
    origin: tuple[int, ...]
    original_len: int

    def original_span(self, ns: int, ne: int) -> tuple[int, int]:
        """Map a normalized span ``[ns, ne)`` to an original span ``[os, oe)``.

        ``os`` is the origin of the first matched normalized char; ``oe`` is one
        past the origin of the last matched normalized char, so the returned
        slice covers exactly the original characters the match derives from.
        """
        if ne <= ns:
            start = self.origin[ns] if ns < len(self.origin) else self.original_len
            return start, start
        os = self.origin[ns]
        oe = self.origin[ne - 1] + 1
        return os, oe


class ObfuscationNormalizer:
    """Fixed-pipeline, deterministic detection-only normalizer."""

    def normalize(self, original: str) -> NormalizedView:
        # Pass 1 — NFKC + case-fold, per code point, carrying provenance.
        chars: list[str] = []
        origin: list[int] = []
        for i, ch in enumerate(original):
            folded = unicodedata.normalize("NFKC", ch).casefold()
            for fc in folded:
                chars.append(fc)
                origin.append(i)

        # Pass 2 — collapse runs of whitespace to a single space.
        c2: list[str] = []
        o2: list[int] = []
        prev_ws = False
        for ch, oi in zip(chars, origin):
            if ch.isspace():
                if prev_ws:
                    continue
                c2.append(" ")
                o2.append(oi)
                prev_ws = True
            else:
                c2.append(ch)
                o2.append(oi)
                prev_ws = False

        # Pass 3 — strip zero-width / format (Unicode category "Cf") characters.
        c3: list[str] = []
        o3: list[int] = []
        for ch, oi in zip(c2, o2):
            if unicodedata.category(ch) == "Cf":
                continue
            c3.append(ch)
            o3.append(oi)

        return NormalizedView(
            text="".join(c3), origin=tuple(o3), original_len=len(original)
        )
