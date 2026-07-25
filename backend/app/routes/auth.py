"""R8/R9 — ``POST /login`` and ``POST /logout`` (register #25 / PER-4 / WIRE1-Fold-5).

The handshake WIRE-1 §6 reserved as *"an abstract seam, deferred — Phase-1 may stub it"*, now
realized. Before this module, ``X-User-Id`` **was** authentication: any caller who knew a
``user_id`` was that user, which made SEC-4's segregation of duties unenforceable against
anyone willing to edit a header, and left ``AuditRecord.underwriter_id`` — the CON-BR4 "WHO" —
an unauthenticated string.

**Both routes are non-GET, and both reach NO domain state.** Being non-GET is *necessary but
never sufficient*: ``test_no_write_route.py`` structurally forbids any route module but the
commit handler from referencing ``CasePipeline``, ``PostgresCaseStore``,
``PendingCommitContextProvider``, ``PostgresAuditRepository`` or ``DecisionCommitService``.
This module touches the authentication service only.

**Uniform failure (WIRE-1 §3 / Q4)**: every rejection — unknown user, no credential row, wrong
password, locked account — returns the **same 401 with the same message**. The service returns
a bare ``None`` for all four, so this layer *structurally cannot* distinguish them. Anything
finer would be a user-enumeration oracle, which is why even "you are locked out" is withheld.

**204 No Content** on success (WIRE-1 §2, added by WIRE1-Fold-5): the session is the
``Set-Cookie``, not a body. The client reads its identity from R1, whose shape is unchanged.
"""
from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, Response
from pydantic import BaseModel

from backend.app.dependencies import (
    SESSION_COOKIE_NAME,
    Identity,
    current_identity,
    get_auth_service,
    session_cookie_is_secure,
)
from backend.app.errors import UNAUTHENTICATED, WireError
from backend.authn.constants import SESSION_TTL
from backend.authn.service import AuthenticationService

router = APIRouter()


class LoginRequest(BaseModel):
    """WIRE-1 §5. The password is verified and discarded — never stored, logged or echoed."""
    user_id: str
    password: str


@router.post("/login", status_code=204)
def login(
    body: LoginRequest,
    response: Response,
    auth: AuthenticationService = Depends(get_auth_service),
) -> Response:
    """R8 — authenticate and issue a session.

    ⚑ The only unauthenticated route in the contract, necessarily: it *is* the handshake.
    """
    token = auth.authenticate(body.user_id, body.password)
    if token is None:
        # ⚑ One message for every cause. The WireError carries no detail that could
        # distinguish an unknown user from a wrong password from a locked account.
        raise WireError(UNAUTHENTICATED, "Authentication failed.")

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,                       # unreachable from page JavaScript
        secure=session_cookie_is_secure(),   # fail-safe: only an exact "false" disables it
        samesite="lax",                      # cross-site POSTs carry no session
        path="/",
    )
    response.status_code = 204
    return response


@router.post("/logout", status_code=204)
def logout(
    response: Response,
    session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    identity: Identity = Depends(current_identity),
    auth: AuthenticationService = Depends(get_auth_service),
) -> Response:
    """R9 — revoke the current session.

    ⚑ Revocation is **server-side**, so the session stops working on the **next request**
    rather than at token expiry. That is the property that makes an 8-hour TTL acceptable
    (Q5a) and that a stateless JWT could not provide.

    ⚑ Requires authentication (``current_identity``): an unauthenticated caller has no
    session to revoke, and accepting one would let a third party clear an arbitrary cookie.
    The dependency having resolved is itself the proof that ``session`` is a live token.
    """
    if session:
        auth.logout(session)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    response.status_code = 204
    return response
