"""Tests for the injected seams (Step 3).

Maps: the determinism / reference-not-own seams — ``IdGenerator`` + ``Clock``
(Q3, audit metadata not in the replay equality set), ``Authorizer`` (Q4, the
backend authz re-check; its ``rbac_action`` is the RBAC OPERATION, DISTINCT from
``CommittedDecision.action``), and ``CommitContextProvider`` (§1.5, the confirmed
4th seam supplying the pending-recommendation context).
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.audit_store import record_schema as rs
from backend.audit_store import seams
from backend.audit_store.tests import factories as f


# --------------------------------------------------------------------------
# IdGenerator + Clock
# --------------------------------------------------------------------------
def test_uuid_generator_produces_unique_strings():
    gen = seams.UuidGenerator()
    a, b = gen.new_id(), gen.new_id()
    assert isinstance(a, str) and a != b


def test_sequence_id_generator_is_deterministic():
    gen = seams.SequenceIdGenerator(prefix="DEC")
    assert [gen.new_id() for _ in range(3)] == ["DEC-1", "DEC-2", "DEC-3"]


def test_fixed_clock_returns_the_fixed_moment():
    moment = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert seams.FixedClock(moment).now() is moment


def test_system_clock_is_timezone_aware():
    now = seams.SystemClock().now()
    assert isinstance(now, datetime) and now.tzinfo is not None


# --------------------------------------------------------------------------
# Authorizer — rbac_action is the RBAC operation, NOT CommittedDecision.action
# --------------------------------------------------------------------------
def test_authorizer_allows_and_denies_by_rbac_action():
    authz = seams.AllowRolesAuthorizer({"UW-1": {seams.RBAC_COMMIT}, "AUD-1": set()})
    assert authz.authorize("UW-1", seams.RBAC_COMMIT) is True     # underwriter may commit
    assert authz.authorize("AUD-1", seams.RBAC_COMMIT) is False   # auditor may not
    assert authz.authorize("NOBODY", seams.RBAC_COMMIT) is False  # unknown -> deny


def test_rbac_action_is_distinct_from_committed_decision_action():
    # The RBAC operation constant is "commit" — NOT the approve/override the human chose.
    assert seams.RBAC_COMMIT == "commit"
    assert seams.RBAC_COMMIT not in {rs.CommitAction.APPROVE.value, rs.CommitAction.OVERRIDE.value}


# --------------------------------------------------------------------------
# CommitContextProvider (§1.5)
# --------------------------------------------------------------------------
def test_context_provider_returns_preset_context():
    ctx = f.make_context()
    provider = seams.DictCommitContextProvider({"REC-1": ctx})
    assert provider.get("REC-1") is ctx


def test_context_provider_raises_for_unknown_recommendation():
    provider = seams.DictCommitContextProvider({})
    with pytest.raises(KeyError):
        provider.get("REC-missing")


def test_fakes_satisfy_their_protocols():
    assert isinstance(seams.SequenceIdGenerator(), seams.IdGenerator)
    assert isinstance(seams.FixedClock(seams.SystemClock().now()), seams.Clock)
    assert isinstance(seams.AllowRolesAuthorizer({}), seams.Authorizer)
    assert isinstance(seams.DictCommitContextProvider({}), seams.CommitContextProvider)
