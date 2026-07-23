"""ReportBuilder — assemble the RuleResultReport (Step 10).

NFR Design §1 (DET-2) + §6 (AUDIT-3). Assembles the frozen ``RuleResultReport``
from the evaluator results + the aggregation + the banded confidence + the
injected provenance (``rulebook_version`` / ``content_hash`` / ``engine_version``).

**DET-2 — every order-derived list field in the ONE canonical order** (``canon_ser``
sorts dict keys but PRESERVES list order, so any list left in iteration order would
make a permuted run byte-different): ``rule_results`` is re-sorted by ``rule_id``
here, and ``decline_reasons`` / ``refer_reasons`` arrive already sorted from the
Aggregator. With every list canonically ordered, a **permuted evaluation → a
byte-identical whole report**.

**AUDIT-3 — output-vs-provenance separation.** :func:`evaluation_output` projects
the report to its **replay equality set** (per-rule rows + recommendation +
confidence + reasons), **excluding** the provenance triple. This mirrors the
projection ``audit-store``'s ReplayService applies — provided here only so the
report's separation is testable; the match/mismatch **comparison/orchestration is
audit-store's** (reference-not-own). ``content_hash`` verifies rulebook byte-identity;
``engine_version`` distinguishes engine drift from a real regression — neither is
part of equality.
"""
from __future__ import annotations

from typing import Any

from backend.rules_engine.aggregator import Aggregation
from backend.rules_engine.report_schema import Confidence, RuleResult, RuleResultReport


def build_report(
    *,
    results: list[RuleResult],
    aggregation: Aggregation,
    confidence: Confidence,
    rulebook_version: str,
    content_hash: str,
    engine_version: str,
) -> RuleResultReport:
    """Build the report with ALL order-derived list fields in canonical order."""
    return RuleResultReport(
        rule_results=sorted(results, key=lambda r: r.rule_id),   # DET-2
        recommendation=aggregation.recommendation,
        confidence=confidence,
        rulebook_version=rulebook_version,
        content_hash=content_hash,
        engine_version=engine_version,
        decline_reasons=list(aggregation.decline_reasons),        # already sorted
        refer_reasons=list(aggregation.refer_reasons),            # already sorted
    )


def evaluation_output(report: RuleResultReport) -> dict[str, Any]:
    """The replay EQUALITY set — evaluation output only, provenance EXCLUDED.

    ``rulebook_version`` / ``content_hash`` / ``engine_version`` are forensic
    (verification), never equality — so engine drift alone is not a false
    mismatch (AUDIT-3).
    """
    return {
        "rule_results": [r.model_dump() for r in report.rule_results],
        "recommendation": report.recommendation.value,
        "confidence": report.confidence.value,
        "decline_reasons": list(report.decline_reasons),
        "refer_reasons": list(report.refer_reasons),
    }
