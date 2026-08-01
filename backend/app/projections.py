"""AuditRecord -> the WIRE-1 §5 wire shapes. Pure functions, no I/O, no state.

The composition root's ONLY transformation layer: it projects the frozen ``AuditRecord``
onto the shapes WIRE-1 §5 pins, and paginates R6 IN-APP (Decision 4 — ``audit-store`` stays
frozen; no limit/offset is pushed into the repository).

WIRE-1 §1 is binding here: enum wire values are emitted BY VALUE and are NEVER re-cased or
remapped (``CommitAction`` lowercase; ``Recommendation`` UPPERCASE incl. the ``-RECOMMEND``
suffix; ``Confidence`` Title-case). This module adds no field and drops no id.

ORDERING (Q3-A, recorded honestly): R6 emits whatever order ``AuditService.browse_history()``
returns — which is ``PostgresAuditRepository.browse()``'s ``ORDER BY decision_id``. This is
the HONEST CURRENT BEHAVIOR, not a designed guarantee: no frozen artifact pins R6's order, and
``ui-history`` re-sorts nothing (BR-HIST-5), so decision_id order is what an auditor sees. A
timestamp sort was deliberately NOT invented — it would have required touching frozen
``audit-store`` or inventing an ordering contract no artifact backs.
"""
from __future__ import annotations

from typing import Any, Sequence

from backend.app.outlier_canonical import dequantize_outlier
from backend.audit_store.record_schema import AuditRecord
from backend.case_lifecycle.schemas import PendingApplication, PendingRecommendation
from backend.common.canon_ser import canon_deserialize

#: R6's page size when the client sends none. A wire-level default only.
DEFAULT_PAGE_SIZE = 20


def decision_summary(record: AuditRecord) -> dict[str, Any]:
    """AuditRecord -> WIRE-1 §5 ``DecisionSummary``.

    ``{decision_id, application_id, recommendation_id, action, timestamp}`` — exactly the five
    fields, no more. Carries the HUMAN ``action`` (from ``committed_decision``) and the tuple
    ``timestamp``; deliberately NOT the system recommendation (§5: the list item omits it — the
    reason ui-history's rows show no recommendation and R7 is its only source).
    """
    return {
        "decision_id": record.decision_id,
        "application_id": record.application_id,
        "recommendation_id": record.recommendation_id,
        # .value -> the frozen lowercase wire value; never re-cased (WIRE-1 §1).
        "action": record.committed_decision.action.value,
        "timestamp": record.audit_tuple.timestamp.isoformat(),
    }


def paginate(records: Sequence[AuditRecord], page: int, size: int) -> tuple[list[AuditRecord], int]:
    """Slice a 1-based page (A4 offset/limit). Returns ``(page_items, total)``.

    An out-of-range page yields an EMPTY slice, never an error: R6 has no frozen status for
    "page past the end", and an empty page is a truthful answer to a valid query.

    NOTE (CR-Fold-4, flagged not masked): ``browse_history()`` is N+1 by construction — it
    materializes EVERY record before this function slices one page. That is the accepted cost
    of Decision 4 (keep ``audit-store`` frozen); the alternative pushes limit/offset into a
    frozen unit. The client-side PERF-1 bound still holds: one bounded page crosses the wire.
    """
    total = len(records)
    start = (page - 1) * size
    return list(records[start:start + size]), total


def decision_list_wrapper(records: Sequence[AuditRecord], page: int, size: int) -> dict[str, Any]:
    """R6 body -> WIRE-1 §3/§5 list wrapper ``{items, page:{page,size,total}}``.

    ``total`` is the FULL count (not the page length), so the client derives its own page count.
    """
    page_items, total = paginate(records, page, size)
    return {
        "items": [decision_summary(r) for r in page_items],
        "page": {"page": page, "size": size, "total": total},
    }


# --- R2/R3/R4 — the pending-state wire shapes (Scope B wiring pass) ---------------------
# Still pure functions, no I/O, no state: the caller does every read and passes the results in.

def application_summary(
    application_id: str,
    report: Any | None,
    recommendation: PendingRecommendation | None,
) -> dict[str, Any]:
    """WIRE-1 §5 ``ApplicationSummary`` — exactly four fields, no more.

    ``{application_id, recommendation_id|null, recommendation|null, confidence|null}``. The last
    three are ``null`` until a recommendation is drafted, which is exactly what the contract says
    (*"null until a recommendation is drafted"*).

    ⚑ ``recommendation``/``confidence`` come from the RULE REPORT, not the memo: they are the
    deterministic engine's output, and the memo carries the same values by construction. Emitted
    BY VALUE and never re-cased (WIRE-1 §1: ``APPROVE``/``DECLINE-RECOMMEND`` UPPERCASE,
    ``High``/``Medium``/``Low`` Title-case).

    ⚑ NO ``status`` FIELD EXISTS in this shape, so a ``failed`` case is INDISTINGUISHABLE from a
    fresh one in the queue (Q4d, register #16). Rows are NOT filtered by state — filtering
    silently would be an undisclosed domain decision taken inside the composition root.
    """
    drafted = recommendation is not None
    return {
        "application_id": application_id,
        "recommendation_id": recommendation.recommendation_id if drafted else None,
        # .value -> the frozen wire value verbatim; never re-cased (WIRE-1 §1).
        "recommendation": report.recommendation.value if (drafted and report is not None) else None,
        "confidence": report.confidence.value if (drafted and report is not None) else None,
    }


def application_list_wrapper(summaries: Sequence[dict[str, Any]], page: int, size: int) -> dict[str, Any]:
    """R2 body -> the WIRE-1 §3/§5 list wrapper, reusing ``paginate`` VERBATIM (Q4b).

    R2 and R6 therefore behave identically on 1-based pages, a full-count ``total``, and an
    empty-not-error page past the end.

    ⚑ ORDER is the store's own (``list_application_ids``' ``ORDER BY application_id``) and is
    asserted as the honest observed behaviour, NOT a designed guarantee — the Q3-A precedent.
    """
    page_items, total = paginate(summaries, page, size)
    return {"items": list(page_items), "page": {"page": page, "size": size, "total": total}}


def memo_view(
    case: PendingApplication,
    status: str,
    profile: Any | None,
    report: Any | None,
    memo: Any | None,
    recommendation: PendingRecommendation | None,
) -> dict[str, Any]:
    """R4 body -> WIRE-1 §5 ``MemoView``, including the WIRE1-Fold-4 ``outlier`` field.

    ``status`` is supplied by U24's PURE ``case_to_memo_view_state`` — the composition root CALLS
    that projection rather than re-deriving it, because the ``failed -> "pending"`` mapping is
    domain knowledge only U24 possesses (register #14: ``failed`` has no wire representation).

    ⚑ ``outlier`` is emitted for a ``ready`` view when the case actually carries stored outlier
    data — the **Phase-2-OUT** slice (plan Q2(a)).

    ⛔ **SUPERSEDED, preserved because it was true for the whole of Phase 1**: *"``outlier`` is
    ALWAYS ``null`` here. WIRE1-Fold-4 binds it ``null`` in Phase 1 even for a ``ready`` view. U24
    DOES persist real outlier data (``PendingRecommendation.outlier_canonical``), so this is a case
    of the data existing while the frozen contract forbids sending it — disclosed as register #17,
    NOT quietly resolved by emitting it (that would amend WIRE-1)."*

    **Two of that paragraph's claims were wrong, and register #17 inherited both.** (1) *"U24 DOES
    persist real outlier data"* — it did not. Nothing computed a score in any API-reachable path,
    so ``outlier_canonical`` was NULL for every row ever written. (2) *"emitting it would amend
    WIRE-1"* — it does not. WIRE-1 binds ``outlier`` null *in Phase 1* and explicitly provides for
    it being *"populated only for a Phase-2 ``ready`` view"*. **Populating it is contract-COMPLIANT**;
    no contract was amended to do this, and none needed to be.

    ⚑ **Deserialization lives HERE by decision (plan Q8(a))** — the composition root is the layer
    whose job is this translation, it is not frozen, and doing it here reopens **no** frozen unit.
    The schema is imported **by value** from U18, which is WIRE-1's own framing of how
    ``OutlierResult`` travels. What is stored is the **Decimal-quantized projection** (barrier #5 —
    CANON-SER refuses IEEE float); ``dequantize_outlier`` returns the float shape the contract and
    ``outlierView`` expect. ⚑ **No frontend change is needed**: JSON does not distinguish Decimal
    from float once serialized, so the wire shape is byte-identical to what the frozen unit was
    built against.

    ⚑ A ``pending`` view, and a ``ready`` view whose case was never scored, both still emit
    ``null`` — the second is every case seeded before this pass, and it must keep working.

    ⚑ ``profile`` is emitted even when ``pending``: U24 reaches ``evaluated`` eagerly in ONE
    transaction, so it is always populated for any row that exists, and §5 explicitly permits it
    (*"profile may still be present once intake has parsed it"*).
    """
    outlier = (
        dequantize_outlier(canon_deserialize(recommendation.outlier_canonical))
        if (
            status == "ready"
            and recommendation is not None
            and recommendation.outlier_canonical is not None
        )
        else None
    )
    return {
        "application_id": case.application_id,
        "recommendation_id": recommendation.recommendation_id if recommendation else None,
        "status": status,
        "profile": profile.model_dump(mode="json") if profile is not None else None,
        "report": report.model_dump(mode="json") if report is not None else None,
        "memo": memo.model_dump(mode="json") if memo is not None else None,
        "outlier": outlier.model_dump(mode="json") if outlier is not None else None,
    }


def audit_record_wire(record: AuditRecord) -> dict[str, Any]:
    """R7 body -> the full ``AuditRecord`` (WIRE-1 §5 = ``audit_store.record_schema.AuditRecord``).

    Serialized by the frozen Pydantic model itself (``mode="json"``), so the wire shape is the
    schema's own — this module neither re-declares nor re-cases it.
    """
    return record.model_dump(mode="json")
