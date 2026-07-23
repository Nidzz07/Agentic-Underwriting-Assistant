"""MemoHashAdapter — memo_hash compute + standalone verify (HASH-1 / REPLAY-1).

``memo-agent-core`` is the **sole owner** of BOTH computing ``memo_hash`` (at
finalize) AND verifying it (a standalone recompute-and-compare, **no LLM**),
invoked **outside** the rules-replay path. ``audit-store`` stores ``memo_hash``
(a ``str``; it does not store the memo text) and structurally cannot re-derive
it; its ``ReplayService`` re-evaluates rules only and **excludes** ``memo_hash``
from its equality set — it never checks it.

Named ``MemoHashAdapter`` (not ``CanonSerAdapter``): it **delegates** to the
single, shared, **unchanged** ``backend/common/canon_ser.py`` (audit-store §2.1
spec) — no re-declaration, no fork — so ``memo_hash`` is byte-identical to any
independent recompute via the same util. Hashed content = ``narrative_prose`` +
``cited_rule_ids`` + ``missing_information`` + ``recommendation`` + ``confidence``;
volatile metadata (``memo_hash``, ``model_version``, timestamps) **excluded**
(CANON-SER P4).
"""
from __future__ import annotations

from typing import Any, Sequence

from backend.common.canon_ser import content_hash
from backend.rules_engine.report_schema import Confidence, Recommendation
from backend.memo_agent_core.schemas import DecisionMemo, MissingInformationItem


class MemoHashAdapter:
    """Compute + standalone verify of the deterministic ``memo_hash``."""

    #: The memo content fields that are hashed (volatile metadata excluded).
    HASHED_FIELDS = (
        "narrative_prose",
        "cited_rule_ids",
        "missing_information",
        "recommendation",
        "confidence",
    )

    def compute(
        self,
        *,
        narrative_prose: str,
        cited_rule_ids: Sequence[str],
        missing_information: Sequence[MissingInformationItem],
        recommendation: Recommendation,
        confidence: Confidence,
    ) -> str:
        """Deterministic hash over the memo's canonical content (at finalize)."""
        return content_hash(
            self._payload(
                narrative_prose, cited_rule_ids, missing_information, recommendation, confidence
            )
        )

    def verify(self, memo: DecisionMemo) -> bool:
        """Standalone recompute-and-compare of a stored memo — **no LLM, no provider**.

        Recomputes the hash from the memo's content fields and compares to the
        recorded ``memo.memo_hash``. This is the memo-integrity check that runs
        outside the rules-replay path (audit-store's ``ReplayService`` never does it).
        """
        recomputed = self.compute(
            narrative_prose=memo.narrative_prose,
            cited_rule_ids=memo.cited_rule_ids,
            missing_information=memo.missing_information,
            recommendation=memo.recommendation,
            confidence=memo.confidence,
        )
        return recomputed == memo.memo_hash

    @staticmethod
    def _payload(
        narrative_prose: str,
        cited_rule_ids: Sequence[str],
        missing_information: Sequence[MissingInformationItem],
        recommendation: Recommendation,
        confidence: Confidence,
    ) -> dict[str, Any]:
        # Plain canon_ser-serializable structure. canon_ser sorts dict keys (P1)
        # but PRESERVES list order — missing_information arrives in the deriver's
        # fixed TOTAL order, so the whole payload is byte-stable.
        return {
            "narrative_prose": narrative_prose,
            "cited_rule_ids": list(cited_rule_ids),
            "missing_information": [
                {"source": item.source.value, "detail": item.detail}
                for item in missing_information
            ],
            "recommendation": recommendation.value,
            "confidence": confidence.value,
        }
