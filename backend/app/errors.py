"""The WIRE-1 §4 error envelope + the frozen status->code table (composition root).

Own-local: nothing here is imported from a frozen unit, and this module imports no unit.
Every non-2xx the app emits carries EXACTLY the frozen §4 body::

    { "error": { "code": "string_slug", "message": "human-readable", "detail": { } } }

WIRE-1 §4 also binds: *no secret VALUE ever appears in message/detail*. The messages here are
static, caller-independent strings; ``detail`` carries only route identifiers.

Status table (frozen §4) + ONE additive extension (Q2-A, recorded in the plan §6.6):
    400 invalid_request | 401 unauthenticated | 403 forbidden | 404 not_found
    409 commit_conflict | 422 unprocessable   | 500 internal_error
    501 not_implemented  <- ADDITIVE extension. It REPLACES and CONTRADICTS no frozen status;
                            every frozen status keeps its exact meaning and the envelope shape
                            is unchanged. It marks "route registered, deliberately not wired
                            in the Scope-A slice" — a state the frozen table has no word for.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# --- the frozen §4 status -> code table (+ the one additive extension) -----------------
INVALID_REQUEST = (400, "invalid_request")
UNAUTHENTICATED = (401, "unauthenticated")
FORBIDDEN = (403, "forbidden")
NOT_FOUND = (404, "not_found")
PAYLOAD_TOO_LARGE = (413, "payload_too_large")  # WIRE1-Fold-7 (upload size caps)
COMMIT_CONFLICT = (409, "commit_conflict")
UNPROCESSABLE = (422, "unprocessable")
INTERNAL_ERROR = (500, "internal_error")
NOT_IMPLEMENTED = (501, "not_implemented")  # additive extension (Q2-A)

#: Every status this app can emit, as the frozen table defines them.
STATUS_TABLE: dict[int, str] = dict(
    [INVALID_REQUEST, UNAUTHENTICATED, FORBIDDEN, NOT_FOUND, PAYLOAD_TOO_LARGE,
     COMMIT_CONFLICT, UNPROCESSABLE, INTERNAL_ERROR, NOT_IMPLEMENTED]
)


def envelope(code: str, message: str, detail: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Build the WIRE-1 §4 body. ``detail`` is always present as an object (never null)."""
    return {"error": {"code": code, "message": message, "detail": detail or {}}}


class WireError(Exception):
    """A failure that must surface as the WIRE-1 §4 envelope with a frozen-table status."""

    def __init__(self, status: tuple[int, str], message: str, detail: Optional[dict] = None) -> None:
        self.status_code, self.code = status
        self.message = message
        self.detail = detail or {}
        super().__init__(message)


# --- handlers -------------------------------------------------------------------------

async def wire_error_handler(_request: Request, exc: WireError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=envelope(exc.code, exc.message, exc.detail))


async def validation_error_handler(_request: Request, _exc: RequestValidationError) -> JSONResponse:
    """A malformed request (e.g. ``?page=abc``) -> 400 invalid_request per §4's table.

    The framework's own 422 body is deliberately NOT surfaced: it is not the §4 envelope, and
    §4 reserves 422 for 'well-formed but unprocessable'. Field errors are not echoed — they
    would risk carrying request VALUES into `detail`.
    """
    status, code = INVALID_REQUEST
    return JSONResponse(status_code=status, content=envelope(code, "The request was malformed."))


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Any framework-raised HTTPException (e.g. an unknown path's 404, a 405) -> the §4 envelope.

    Guarantees the envelope on EVERY non-2xx, so no route can leak a non-WIRE-1 body.
    """
    code = STATUS_TABLE.get(exc.status_code, "internal_error")
    return JSONResponse(status_code=exc.status_code, content=envelope(code, "The request could not be completed."))
