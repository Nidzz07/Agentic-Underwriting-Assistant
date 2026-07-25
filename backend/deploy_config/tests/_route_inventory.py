"""The DECLARED route inventory — the single place the route surface is written down.

⚑ **MIRROR COPY.** The composition root declares the routes, so
``backend/app/tests/_route_inventory.py`` is the AUTHORITATIVE copy and this one is the
deployment-verification mirror. The two are held identical by
``backend/app/tests/test_route_inventory_sync.py``, which fails loudly on any drift.

⚑ **Why DUPLICATED rather than shared** (relaxation design Q1(c)): U23's own
``test_routes.py`` asserts that its scan *"imports only the PRODUCTION composition root,
never ``backend/app/tests``"* — so importing the authoritative copy from this tree is
forbidden by a frozen assertion, and importing this copy from ``backend/app/tests`` would
make a frozen unit's test helper a dependency of the composition root's tests. Duplication
with a **cross-check that reads both files as TEXT** achieves the anti-drift property with
**zero new import edges**.

**Why this file exists** (frozen-assertion relaxation, ``frozen-assertion-relaxation-plan.md``):
the guards' strength is the **EXACT-SET EQUALITY**, not the literal being inline. Moving the
literal here keeps every comparison at equality while making growth a **reviewable one-line
diff in a named, greppable place**.

⚑ **Keep this file byte-equivalent in CONTENT to the authoritative copy.** The cross-check
compares the parsed inventories, not the prose, so these docstrings may legitimately differ —
the tuples may not.
"""
from __future__ import annotations

#: Every route the application exposes, as ``(path, method)`` with method LOWERCASE
#: (matching OpenAPI's own casing, which ``_route_set`` reads).
#:
#: WIRE-1 R1-R7 — the pinned contract surface (``guide-docs/build/wire-1/api-contract.md`` §3).
ROUTE_INVENTORY: tuple[tuple[str, str], ...] = (
    ("/session", "get"),                                      # R1 — identity + Role delivery (§6)
    ("/applications", "get"),                                 # R2 — the queue
    ("/applications/{application_id}", "get"),                # R3 — one application's profile
    ("/applications/{application_id}/memo", "get"),           # R4 — MemoView
    ("/recommendations/{recommendation_id}/commit", "post"),  # R5 — the human approval gate
    ("/decisions", "get"),                                    # R6 — decision history
    ("/decisions/{decision_id}", "get"),                      # R7 — one committed decision
)

#: The routes permitted to be non-GET, each with the reason it must be.
#:
#: ⚑ A non-GET route is an exception that must be argued for, not a default. The
#: companion assertion in ``test_no_write_route.py`` additionally requires that only the
#: commit route reaches domain state — being non-GET is necessary but never sufficient.
NON_GET_ALLOWLIST: tuple[tuple[str, str], ...] = (
    # R5 — the ONLY route that changes underwriting state. An explicit underwriter action
    # is the sole way a CommittedDecision comes into existence (WIRE-1 §2 advisory-only).
    ("/recommendations/{recommendation_id}/commit", "post"),
)

#: The exact set of modules permitted under ``backend/app/routes/``.
#:
#: Read by ``test_route_modules_are_exactly_the_declared_inventory``. A sixth module fails
#: that assertion until it is named here.
ROUTE_MODULE_INVENTORY: tuple[str, ...] = (
    "__init__.py",
    "session.py",     # R1
    "decisions.py",   # R6, R7
    "not_wired.py",   # R2-R5 (name is stale — register #13, deliberately still open)
)
