"""C5 ``SkewAudit`` — the blocking conjunctive gate (SKEW-BAND-1 + SKEW-EDGE-1, Fold 2).

Two **independent** sub-checks, AND-ed **only at the top level, never blended into
one score**:

  * ``band_ok`` — each realized class proportion is within ``±tolerance_pp`` of the
    ``target_split``, computed **only** from class counts / total (it does NOT
    consult the edge checklist);
  * ``edges_ok`` — **every** required DATA-2 edge case is present — a checklist,
    never averaged into the band.

The gate reads ``(target_split, tolerance_pp)`` from the SAME ``GenerationConfig``
the ``RejectionSampler`` pre-flight reads (ND-Fold-1) — one band definition, two
uses, cannot independently disagree. On any failure it raises ``SkewAuditError``
(build-blocking; no partial/ungated corpus).

``band_lower_edge_count`` is the shared band arithmetic the pre-flight feasibility
guard uses (band LOWER edge, not the center — ND-Fold-1).
"""
from __future__ import annotations

from decimal import Decimal
from math import ceil

from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.exceptions import SkewAuditError


def class_proportions(class_counts: dict[str, int]) -> dict[str, Decimal]:
    """Realized proportion per class (exact ``Decimal``; empty total -> all zero)."""
    total = sum(class_counts.values())
    if total == 0:
        return {cls: Decimal(0) for cls in class_counts}
    return {cls: Decimal(count) / Decimal(total) for cls, count in class_counts.items()}


def band_lower_edge_count(target_proportion: Decimal, config: GenerationConfig) -> int:
    """The band LOWER-edge required count for a class (ND-Fold-1).

    ``ceil(min_profiles * (target_prop - tolerance))`` — the lower band edge, NOT
    the center ``min_profiles * target_prop`` (which would false-raise on
    band-feasible configs). Floored at 0.
    """
    lower = config.min_profiles * (target_proportion - config.tolerance)
    if lower <= 0:
        return 0
    return ceil(lower)


def band_ok(class_counts: dict[str, int], config: GenerationConfig) -> bool:
    """Each class proportion within ``±tolerance`` of its target (band only)."""
    proportions = class_proportions(class_counts)
    for cls, target in config.target_split.items():
        realized = proportions.get(cls, Decimal(0))
        if abs(realized - target) > config.tolerance:
            return False
    return True


def edges_ok(present_edges: set[str], config: GenerationConfig) -> bool:
    """Every required DATA-2 edge case is present (checklist; never averaged)."""
    return all(edge in present_edges for edge in config.required_edge_cases)


def edge_checklist(present_edges: set[str], config: GenerationConfig) -> dict[str, bool]:
    """Each required edge -> present true/false (for the manifest)."""
    return {edge: edge in present_edges for edge in config.required_edge_cases}


class SkewAudit:
    """The blocking conjunctive skew-audit gate."""

    def check_band(self, class_counts: dict[str, int], config: GenerationConfig) -> bool:
        return band_ok(class_counts, config)

    def check_edges(self, present_edges: set[str], config: GenerationConfig) -> bool:
        return edges_ok(present_edges, config)

    def audit(
        self,
        *,
        class_counts: dict[str, int],
        present_edges: set[str],
        config: GenerationConfig,
    ) -> None:
        """Run BOTH sub-checks independently and AND them at the top. Raise on failure."""
        band = self.check_band(class_counts, config)          # independent
        edges = self.check_edges(present_edges, config)        # independent
        if not (band and edges):                               # AND-ed only at the top
            missing = sorted(e for e in config.required_edge_cases if e not in present_edges)
            raise SkewAuditError(
                f"skew-audit failed: band_ok={band}, edges_ok={edges}; "
                f"class_counts={class_counts}, missing_edges={missing}"
            )
