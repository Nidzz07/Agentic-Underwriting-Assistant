"""Tests for DecisionCommitService (Step 5).

Maps: NFR-AUDIT-GATE-1 (closed negative matrix + Hypothesis ∀ blank/whitespace
reason → reject), NFR-AUDIT-AUTHZ-1 (backend authz re-check, independent of the
API), NFR-AUDIT-TUPLE-1 (assemble-complete-BEFORE-BEGIN from the 4 gate fields +
the fetched CommitContext + the seams), NFR-AUDIT-ATOMIC-1 (both-or-neither on
the fake — reject→0, accept→1, fault→rollback).
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone

import pytest
from hypothesis import given
from hypothesis import strategies as st

from backend.audit_store import record_schema as rs
from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.audit_store.commit_service import (
    CommitRejected,
    DecisionCommitService,
    UnauthorizedCommit,
)
from backend.audit_store.repository import InMemoryAuditRepository
from backend.audit_store import seams
from backend.audit_store.tests import factories as f

_CLOCK = seams.FixedClock(datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))


def _service(repo=None, allow_uw="UW-1", context=None):
    repo = repo if repo is not None else InMemoryAuditRepository()
    context = context if context is not None else f.make_context()
    return DecisionCommitService(
        repository=repo,
        context_provider=seams.DictCommitContextProvider({"REC-1": context}),
        authorizer=seams.AllowRolesAuthorizer({allow_uw: {seams.RBAC_COMMIT}}),
        id_generator=seams.SequenceIdGenerator(),
        clock=_CLOCK,
    ), repo


def _commit(svc, **over):
    kw = dict(recommendation_id="REC-1", underwriter_id="UW-1",
              action=rs.CommitAction.APPROVE, reason=None)
    kw.update(over)
    return svc.commit(**kw)


# --------------------------------------------------------------------------
# GATE-1 — the closed negative matrix
# --------------------------------------------------------------------------
@pytest.mark.parametrize("over", [
    dict(underwriter_id=""),                                        # empty WHO
    dict(underwriter_id="   "),                                     # whitespace WHO
    dict(underwriter_id=None),                                      # missing WHO
    dict(action=None),                                              # missing WHAT
    dict(action="reject"),                                          # WHAT outside the closed enum
    dict(action=rs.CommitAction.OVERRIDE, reason=None),            # override, null reason
    dict(action=rs.CommitAction.OVERRIDE, reason=""),             # override, empty reason
    dict(action=rs.CommitAction.OVERRIDE, reason="  \t "),        # override, whitespace reason
])
def test_gate_rejects_the_negative_matrix(over):
    svc, repo = _service()
    with pytest.raises(CommitRejected):
        _commit(svc, **over)
    assert repo.browse() == []                                     # nothing written on reject


@pytest.mark.parametrize("over", [
    dict(action=rs.CommitAction.APPROVE, reason=None),             # approve needs no reason
    dict(action=rs.CommitAction.OVERRIDE, reason="irregular income"),  # override with a reason
    dict(action="approve", reason=None),                           # enum value string accepted
])
def test_gate_accepts_accountable_commits(over):
    svc, repo = _service()
    result = _commit(svc, **over)
    assert isinstance(result, rs.CommittedDecision)
    assert len(repo.browse()) == 1


@given(reason=st.text(alphabet=" \t\n\r\f\v", max_size=8))
def test_forall_blank_override_reason_rejected(reason):
    """∀ whitespace/empty reason → an override cannot commit (GATE-1)."""
    svc, _ = _service()
    with pytest.raises(CommitRejected):
        _commit(svc, action=rs.CommitAction.OVERRIDE, reason=reason)


# --------------------------------------------------------------------------
# AUTHZ-1 — backend re-check, independent of the API layer
# --------------------------------------------------------------------------
def test_auditor_is_rejected_at_the_service_even_with_valid_payload():
    # The API layer is bypassed entirely (we call the service directly); the
    # backend re-check still rejects a non-underwriter.
    svc, repo = _service(allow_uw="UW-1")
    with pytest.raises(UnauthorizedCommit):
        _commit(svc, underwriter_id="AUD-1")          # auditor id not granted RBAC_COMMIT
    assert repo.browse() == []


def test_underwriter_passes_the_recheck():
    svc, repo = _service(allow_uw="UW-1")
    _commit(svc, underwriter_id="UW-1")
    assert len(repo.browse()) == 1


# --------------------------------------------------------------------------
# TUPLE-1 — assembled record is complete, from context + seams
# --------------------------------------------------------------------------
def test_commit_assembles_complete_record_from_context_and_seams():
    context = f.make_context()
    svc, repo = _service(context=context)
    _commit(svc, action=rs.CommitAction.OVERRIDE, reason="borderline dti")
    rec = repo.get("DEC-1")                            # decision_id from the injected SequenceIdGenerator
    assert rec is not None
    # tuple assembled from the fetched CommitContext
    assert rec.audit_tuple.rule_results == context.rule_results
    assert rec.audit_tuple.memo_hash == context.memo_hash
    assert rec.audit_tuple.model_version == context.model_version
    assert rec.audit_tuple.engine_version == context.engine_version
    assert rec.audit_tuple.rulebook_version == context.rulebook_version
    assert rec.audit_tuple.timestamp == _CLOCK.now()   # timestamp from the injected clock
    # snapshot = the exact profile + its CANON-SER content_hash
    assert rec.applicant_profile_snapshot.profile == context.applicant_profile
    assert rec.applicant_profile_snapshot.content_hash == CanonSerAdapter.content_hash(
        context.applicant_profile)
    # linkage + seam
    assert rec.committed_decision.action is rs.CommitAction.OVERRIDE
    assert rec.committed_decision.reason == "borderline dti"
    assert rec.status is rs.DecisionStatus.ACTIVE and rec.supersedes_decision_id is None
    assert rec.application_id == context.applicant_profile.application_id


# --------------------------------------------------------------------------
# ATOMIC-1 (behavioral, on the fake) + assemble-before-BEGIN
# --------------------------------------------------------------------------
def test_atomic_reject_writes_zero_accept_writes_one():
    svc, repo = _service()
    with pytest.raises(CommitRejected):
        _commit(svc, underwriter_id="")               # reject
    assert repo.browse() == []                         # 0
    _commit(svc)                                       # accept
    assert len(repo.browse()) == 1                     # exactly 1 logical AuditRecord


def test_atomic_fault_mid_persist_rolls_back():
    repo = InMemoryAuditRepository(fail_on_insert=True)
    svc, _ = _service(repo=repo)
    from backend.audit_store.repository import FaultInjected
    with pytest.raises(FaultInjected):
        _commit(svc)
    assert repo.get("DEC-1") is None                   # both-or-neither: nothing committed


class _AtomicSpyRepo(InMemoryAuditRepository):
    """Counts how many times the transaction boundary is entered."""
    def __init__(self):
        super().__init__()
        self.atomic_entries = 0

    @contextmanager
    def atomic(self):
        self.atomic_entries += 1
        with super().atomic():
            yield


@pytest.mark.parametrize("over,exc", [
    (dict(underwriter_id=""), CommitRejected),         # gate failure
    (dict(underwriter_id="AUD-1"), UnauthorizedCommit),  # authz failure
    (dict(recommendation_id="REC-missing"), KeyError), # context-fetch failure
])
def test_pre_write_failure_opens_no_transaction(over, exc):
    # assemble-before-BEGIN: a failure before the write NEVER opens a transaction.
    repo = _AtomicSpyRepo()
    svc, _ = _service(repo=repo)
    with pytest.raises(exc):
        _commit(svc, **over)
    assert repo.atomic_entries == 0                    # no half-open transaction


def test_happy_path_enters_the_transaction_exactly_once():
    repo = _AtomicSpyRepo()
    svc, _ = _service(repo=repo)
    _commit(svc)
    assert repo.atomic_entries == 1
