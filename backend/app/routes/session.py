"""R1 — ``GET /session``. WIRE-1 §6: how the Role reaches the client.

Authenticated, ANY role (§3) — no authorization is applied: R1 delivers identity, it gates
nothing. Returns ``{user_id, role}`` where ``role`` is the EXACT lowercase enum value
(``underwriter``/``auditor``/``admin``) — WIRE-1 §6 binds "no re-case".

Role here is chrome/labelling only, never an authorization datum: the real gate is server-side
auth-rbac on each protected route (R6/R7's READ_AUDIT).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from backend.app.dependencies import Identity, current_identity

router = APIRouter()


@router.get("/session")
def get_session(identity: Identity = Depends(current_identity)) -> dict[str, Any]:
    # .value -> the frozen wire value verbatim; ui-shell's RoleContext consumes it by value.
    return {"user_id": identity.user_id, "role": identity.role.value}
