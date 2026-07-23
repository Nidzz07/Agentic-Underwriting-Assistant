"""Injected seams (Step 3) — determinism + reference-not-own boundaries.

- ``IdGenerator`` / ``Clock`` (Q3): ``decision_id`` + ``timestamp`` are **audit
  metadata, NOT in the replay equality set**, so injecting them never threatens
  replay determinism; the seams keep tests deterministic + wall-clock/global state
  out of the service (mirrors rules-engine's injected ``engine_version`` / intake's
  ``application_id``).
- ``Authorizer`` (Q4): the backend authz re-check, referencing ``auth-rbac``'s
  ``AuthRBAC.authorize`` contract. Its ``rbac_action`` is the **RBAC OPERATION**
  (e.g. :data:`RBAC_COMMIT`) — **distinct from ``CommittedDecision.action``**
  (approve/override), so the two are never conflated. audit-store owns the
  **re-check call site**, never the policy; ``auth-rbac`` wires the real impl at the
  composition root.
- ``CommitContextProvider`` (§1.5): the confirmed 4th seam supplying the
  pending-recommendation context the frozen 4-param ``commit`` signature does not
  carry — **owned by the orchestrator/pipeline**, referenced-not-owned here.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from backend.audit_store.record_schema import CommitContext

#: The RBAC operation the commit-gate re-checks (NOT the human's approve/override).
RBAC_COMMIT = "commit"


# --------------------------------------------------------------------------
# decision_id generator
# --------------------------------------------------------------------------
@runtime_checkable
class IdGenerator(Protocol):
    def new_id(self) -> str: ...


class UuidGenerator:
    """Production ``decision_id`` generator."""
    def new_id(self) -> str:
        return str(uuid.uuid4())


class SequenceIdGenerator:
    """Deterministic test generator — ``{prefix}-1``, ``{prefix}-2``, …"""
    def __init__(self, prefix: str = "DEC") -> None:
        self._prefix = prefix
        self._n = 0

    def new_id(self) -> str:
        self._n += 1
        return f"{self._prefix}-{self._n}"


# --------------------------------------------------------------------------
# commit-time clock
# --------------------------------------------------------------------------
@runtime_checkable
class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FixedClock:
    def __init__(self, moment: datetime) -> None:
        self._moment = moment

    def now(self) -> datetime:
        return self._moment


# --------------------------------------------------------------------------
# backend authz re-check (references auth-rbac's AuthRBAC.authorize)
# --------------------------------------------------------------------------
@runtime_checkable
class Authorizer(Protocol):
    def authorize(self, user_id: str, rbac_action: str) -> bool: ...


class AllowRolesAuthorizer:
    """Test/fake authorizer — maps ``user_id -> {allowed rbac_action}``. The real
    ``auth-rbac`` impl is wired at the composition root (reference-not-own)."""
    def __init__(self, allowed: dict[str, set[str]]) -> None:
        self._allowed = allowed

    def authorize(self, user_id: str, rbac_action: str) -> bool:
        return rbac_action in self._allowed.get(user_id, set())


# --------------------------------------------------------------------------
# pending-recommendation context provider (§1.5 — orchestrator/pipeline owned)
# --------------------------------------------------------------------------
@runtime_checkable
class CommitContextProvider(Protocol):
    def get(self, recommendation_id: str) -> CommitContext: ...


class DictCommitContextProvider:
    """Test/fake provider — a preset ``recommendation_id -> CommitContext`` map."""
    def __init__(self, mapping: dict[str, CommitContext]) -> None:
        self._mapping = mapping

    def get(self, recommendation_id: str) -> CommitContext:
        if recommendation_id not in self._mapping:
            raise KeyError(f"no pending recommendation context for {recommendation_id!r}")
        return self._mapping[recommendation_id]
