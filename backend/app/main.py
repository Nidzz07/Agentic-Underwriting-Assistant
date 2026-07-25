"""The FastAPI composition root — ``backend/app/main.py``.

The in-process wiring across backend units (``unit-of-work.md §2``: "the monorepo composition
root… **not a 24th unit of work**"). Authored in an explicitly-logged OUT-OF-BAND integration
pass (see ``guide-docs/build/plans/composition-root-integration-plan.md``), because Build & Test
— the venue the frozen plan named for its VERIFICATION — cannot run until all 23 units complete.

**SCOPE B — ALL SEVEN WIRE-1 ROUTES ARE LIVE.** Scope A wired only R1/R6/R7 and registered
R2-R5 as ``501`` markers, because no pending-application store existed. ``case-lifecycle`` (U24)
built that store, and this pass wired the remaining four IN PLACE:

    R1  GET  /session                              REAL   (app_user, DATABASE_URL engine)
    R2  GET  /applications?page=&size=             REAL   (pending_application, DATABASE_URL engine)
    R3  GET  /applications/{id}                    REAL   (pending_application, DATABASE_URL engine)
    R4  GET  /applications/{id}/memo               REAL   (pending state; a PURE read — never drafts)
    R5  POST /recommendations/{id}/commit          REAL   (frozen DecisionCommitService, AUDIT_WRITER_URL)
    R6  GET  /decisions?page=&size=                REAL   (audit_record, AUDIT_READER_URL engine)
    R7  GET  /decisions/{decision_id}              REAL   (audit_record, AUDIT_READER_URL engine)

COMPOSITION ONLY — this module (and this package) contains no domain logic. Every behaviour
belongs to a frozen unit or to U24, constructed in ``dependencies.py`` and injected. No frozen
unit is edited or re-implemented anywhere under ``backend/app/``.

⚑ **INV-FAITHFUL, RESTATED FOR THE WIRED SLICE.** Scope A's guarantee was *"no write path is
reachable"*. That is **FALSE BY DESIGN** now — R5 is a real commit. The guarantee this app makes
is the one that actually matters, and it is **stronger than the absence of writes**:

    EVERY WRITE PATH GOES THROUGH THE FROZEN ``DecisionCommitService``.

Its CON-BR4 gate and its independent ``RBAC_COMMIT`` re-check run **inside** ``commit()``, before
any assembly, so no route can bypass them. R5 is still the ONLY non-GET route; R2/R3/R4 remain
pure reads that invoke no pipeline step (``CasePipeline`` is not even constructed in this
package), so **no read can trigger drafting** (BR-CASE-4 / TRIGGER-1). Advisory-only holds: a
``CommittedDecision`` exists only as the result of an explicit underwriter action.
Asserted in ``tests/test_no_write_route.py``.

⚑ The R2-R5 handlers live in ``routes/not_wired.py`` — a **knowingly stale filename**, kept
because U23's frozen ``NFR-DEP-ROUTES-1`` asserts exact-set equality over this directory's
filenames (register #13; renaming it and relaxing that test are a matched pair for a future
authorized change).
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.errors import (
    WireError,
    http_exception_handler,
    validation_error_handler,
    wire_error_handler,
)
from backend.app.routes import auth, decisions, not_wired, session


def create_app() -> FastAPI:
    """Build the app. Constructs NO engine and reads NO setting — those are per-request
    dependencies (``dependencies.py``), so importing this module never requires an environment.
    """
    app = FastAPI(
        title="Agentic Underwriting Assistant — composition root (Scope B)",
        description="Advisory-only. Wires all seven WIRE-1 routes (R1-R7). Every write goes through the frozen DecisionCommitService.",
        version="0.2.0-scope-b",
    )

    # Every non-2xx leaves as the WIRE-1 §4 envelope — no route can emit a non-contract body.
    app.add_exception_handler(WireError, wire_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    app.include_router(auth.router)        # R8, R9 — the handshake (WIRE1-Fold-5)
    app.include_router(session.router)     # R1
    app.include_router(decisions.router)   # R6, R7
    app.include_router(not_wired.router)   # R2-R5 (stale filename — register #13)

    return app


app = create_app()
