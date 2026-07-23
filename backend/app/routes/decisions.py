"""R6 + R7 — the decision-history read surface. The two routes ``ui-history`` (U9) consumes.

R6 ``GET /decisions?page=&size=``  -> the §3 list wrapper of §5 ``DecisionSummary``
R7 ``GET /decisions/{decision_id}`` -> the §5 ``AuditRecord``; missing -> 404 ``not_found``

Both are GET-only reads on the SELECT-only reader engine, and both enforce READ_AUDIT via the
frozen auth-rbac guard (Q1-B — see ``dependencies.require_read_audit`` for the RECORDED,
UNRESOLVED divergence with WIRE-1 §3's "any role" wording).

Pagination is IN-APP (Decision 4) — ``audit-store`` stays frozen.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from backend.app.dependencies import Identity, get_audit_service, require_read_audit
from backend.app.errors import NOT_FOUND, WireError
from backend.app.projections import DEFAULT_PAGE_SIZE, audit_record_wire, decision_list_wrapper
from backend.audit_store.audit_service import AuditService

router = APIRouter()


@router.get("/decisions")
def list_decisions(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100),
    _identity: Identity = Depends(require_read_audit),
    service: AuditService = Depends(get_audit_service),
) -> dict[str, Any]:
    """R6. `page` is 1-based (A4). Order is browse()'s decision_id order (Q3-A, see projections)."""
    records = service.browse_history()
    return decision_list_wrapper(records, page=page, size=size)


@router.get("/decisions/{decision_id}")
def get_decision(
    decision_id: str,
    _identity: Identity = Depends(require_read_audit),
    service: AuditService = Depends(get_audit_service),
) -> dict[str, Any]:
    """R7. A non-existent decision_id -> 404 not_found, the generic path ui-history expects."""
    record = service.get(decision_id)
    if record is None:
        # The message is static and carries no caller-supplied value (WIRE-1 §4: no secret
        # VALUE in message/detail) — the id is the caller's own, but it is not echoed back.
        raise WireError(NOT_FOUND, "No such decision.")
    return audit_record_wire(record)
