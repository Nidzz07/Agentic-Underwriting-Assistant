"""The DECLARED route inventory — the single place the route surface is written down.

⚑ **AUTHORITATIVE COPY.** The composition root declares the routes, so this copy is the
source of truth; ``backend/deploy_config/tests/_route_inventory.py`` is the
deployment-verification MIRROR. The two are held identical by
``test_route_inventory_sync.py``, which fails loudly on any drift.

**Why this file exists** (frozen-assertion relaxation, ``frozen-assertion-relaxation-plan.md``):
four assertions — U23's ``test_routes.py`` route-table check, and this tree's
``test_no_write_route.py`` non-GET / whole-surface checks — each compared a live-introspected
set against a hardcoded literal. **The strength of those guards is the EXACT-SET EQUALITY,
not the literal being inline.** Moving each literal here keeps every comparison at equality
while making growth a **reviewable one-line diff in a named, greppable place** instead of
either forbidden outright or silently absorbed.

⚑ **Adding an entry here is a DELIBERATE ACT.** Every assertion that reads this file still
fails until the entry is added, so a new route cannot appear unnoticed. Each non-GET entry
carries the reason it is permitted to be non-GET — a GET-only surface is the default and the
exceptions are enumerated, never implied.

⚑ **This file previously also removed a real drift risk**: ``test_routes.py`` and
``test_no_write_route.py`` hardcoded the same seven paths **independently**, with nothing
forcing them to agree.
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
#: Read by U23's ``test_route_modules_are_exactly_the_declared_inventory``. A sixth module
#: fails that assertion until it is named here.
ROUTE_MODULE_INVENTORY: tuple[str, ...] = (
    "__init__.py",
    "session.py",     # R1
    "decisions.py",   # R6, R7
    "not_wired.py",   # R2-R5 (name is stale — register #13, deliberately still open)
)
