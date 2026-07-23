"""SanitizerEngine — SEC-1 injection defense (FD §3 / NFR Design §2).

Composes the :class:`ObfuscationNormalizer` (deterministic detection view +
origin map) and the :class:`PatternRegistry` (versioned matchers + inert
placeholder). For each free-text field:

    normalize -> match on the detection view -> map matches back to ORIGINAL
    spans -> defang each original span to the inert placeholder -> log the
    verbatim original span to the SanitizationReport (audit-only).

Never raises on suspicious content (SR-NEUTRALIZE): a suspicious document is
cleaned, not rejected — rejection is the SEC-2 gate's job, and only for
structural reasons. No LLM (D4). Idempotent GIVEN placeholder-inertness (pinned
in the registry-invariant test): re-sanitising ``clean_text`` is a no-op.

``original_span`` is preserved in the report ONLY (SR-FORENSIC); ``clean_text``
carries the inert placeholder, never the raw injection.
"""
from __future__ import annotations

from backend.intake.schema import SanitizationReportEntry, SanitizedText
from backend.intake.sanitizer.normalizer import ObfuscationNormalizer
from backend.intake.sanitizer.pattern_registry import PatternRegistry


class SanitizerEngine:
    """Deterministic, LLM-free prompt-injection sanitizer."""

    def __init__(
        self,
        normalizer: ObfuscationNormalizer | None = None,
        registry: PatternRegistry | None = None,
    ) -> None:
        self._normalizer = normalizer or ObfuscationNormalizer()
        self._registry = registry or PatternRegistry()

    def sanitize(self, raw_text: str, source_ref: str = "") -> SanitizedText:
        """Neutralize injection spans in one free-text field.

        ``source_ref`` labels the field the text came from (populates
        ``SanitizedText.source_ref`` / each report entry's ``source_field``);
        it is a passthrough label, not a new behaviour.
        """
        view = self._normalizer.normalize(raw_text)
        matches = self._registry.find_matches(view.text)

        if not matches:  # SR-CLEAN-BOUNDARY
            return SanitizedText(
                source_ref=source_ref,
                clean_text=raw_text,
                was_modified=False,
                report=[],
            )

        # Map each normalized match back to its ORIGINAL span and rebuild
        # clean_text in a single left-to-right pass. Normalized matches are
        # already merged non-overlapping and ``origin`` is monotonic, so original
        # spans are ordered; a ``cursor`` clamp absorbs the rare case where one
        # original char (NFKC-expanded) underlies two adjacent matches.
        placeholder = self._registry.placeholder
        report: list[SanitizationReportEntry] = []
        pieces: list[str] = []
        cursor = 0
        for m in matches:
            os, oe = view.original_span(m.start, m.end)
            if oe <= cursor:  # pragma: no cover - defensive: NFKC-expansion overlap
                continue
            os = max(os, cursor)  # clamp any overlap with the consumed prefix
            pieces.append(raw_text[cursor:os])
            pieces.append(placeholder)
            report.append(
                SanitizationReportEntry(
                    source_field=source_ref,
                    original_span=raw_text[os:oe],   # verbatim, AUDIT-ONLY
                    neutralized_span=placeholder,
                    pattern_category=m.category,      # type: ignore[arg-type]
                )
            )
            cursor = oe
        pieces.append(raw_text[cursor:])

        return SanitizedText(
            source_ref=source_ref,
            clean_text="".join(pieces),
            was_modified=True,
            report=report,
        )
