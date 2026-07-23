"""Tests for ReplayService (Step 6).

Maps: NFR-AUDIT-REPLAY-1 (verdict = the SINGLE-SOURCED rules-engine
``evaluation_output()`` projection on BOTH sides; engine_version/content_hash-only
diff → still match; genuine diff → blocking mismatch + forensic delta),
NFR-AUDIT-REPLAY-2 (pure rules-engine ``evaluate()`` REFERENCED, no LLM, no
re-draft, no re-commit, ×N byte-identical), NFR-AUDIT-BR1-1 (bias-swap on the
snapshot → identical projection, delta 0).

Uses a REAL injected ``RulesEngine`` over rules-engine's representative rulebook —
a genuine end-to-end re-evaluation (reference-not-own).
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import backend.rules_engine as re_pkg
from backend.common.canon_ser import canon_ser
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader
from backend.rules_engine.report import evaluation_output
from backend.rules_engine.report_schema import Recommendation
from backend.audit_store.replay_service import ReplayNotFound, ReplayService
from backend.audit_store.repository import InMemoryAuditRepository
from backend.audit_store.tests import factories as f

_RULEBOOK_DIR = Path(re_pkg.__file__).parent / "rulebook"


def _engine():
    return RulesEngine(RulebookLoader(_RULEBOOK_DIR), engine_version="eng-replay-1")


def _seed(repo, engine, *, profile=None, decision_id="DEC-1", version="1.0.0", report=None):
    """Commit a record whose recorded rule_results is the ACTUAL evaluate() output."""
    profile = profile if profile is not None else f.make_profile()
    report = report if report is not None else engine.evaluate(profile, version)
    tup = f.make_tuple(rule_results=report, rulebook_version=version)
    snap = f.make_snapshot(application_id=profile.application_id, profile=profile)
    rec = f.make_record(decision_id=decision_id, application_id=profile.application_id,
                        audit_tuple=tup, applicant_profile_snapshot=snap)
    with repo.atomic():
        repo.insert(rec)
    return rec, report


def test_replay_unchanged_record_matches():
    repo, engine = InMemoryAuditRepository(), _engine()
    _seed(repo, engine)
    verdict = ReplayService(repo, engine).replay("DEC-1")
    assert verdict.match is True and verdict.delta is None


def test_missing_decision_raises():
    with pytest.raises(ReplayNotFound):
        ReplayService(InMemoryAuditRepository(), _engine()).replay("nope")


def test_engine_version_only_difference_still_matches():
    # The recorded report carries a different engine_version (forensic) but identical
    # evaluation output -> the projection excludes it -> still a match.
    repo, engine = InMemoryAuditRepository(), _engine()
    _, report = _seed(repo, engine)
    stale = report.model_copy(update={"engine_version": "eng-OLD-sha"})
    repo2 = InMemoryAuditRepository()
    _seed(repo2, engine, report=stale)
    verdict = ReplayService(repo2, engine).replay("DEC-1")
    assert verdict.match is True                       # forensic-only diff is not a mismatch


def test_content_hash_only_difference_still_matches():
    repo, engine = InMemoryAuditRepository(), _engine()
    _, report = _seed(repo, engine)
    stale = report.model_copy(update={"content_hash": "different-rulebook-hash"})
    repo2 = InMemoryAuditRepository()
    _seed(repo2, engine, report=stale)
    assert ReplayService(repo2, engine).replay("DEC-1").match is True


def test_genuine_output_difference_is_a_blocking_mismatch_with_delta():
    repo, engine = InMemoryAuditRepository(), _engine()
    _, report = _seed(repo, engine)                    # fresh evaluate -> APPROVE
    assert report.recommendation is Recommendation.APPROVE
    tampered = report.model_copy(update={"recommendation": Recommendation.DECLINE_RECOMMEND})
    repo2 = InMemoryAuditRepository()
    _seed(repo2, engine, report=tampered)
    verdict = ReplayService(repo2, engine).replay("DEC-1")
    assert verdict.match is False
    assert verdict.delta is not None                   # forensic delta on mismatch


def test_projection_is_single_sourced_from_rules_engine():
    # The compared projection is exactly rules-engine's own evaluation_output().
    repo, engine = InMemoryAuditRepository(), _engine()
    _, report = _seed(repo, engine)
    verdict = ReplayService(repo, engine).replay("DEC-1")
    assert verdict.fresh_projection == evaluation_output(report)


def test_replay_is_read_only_no_recommit_no_extra_records():
    repo, engine = InMemoryAuditRepository(), _engine()
    _seed(repo, engine)
    before = {r.decision_id for r in repo.browse()}
    ReplayService(repo, engine).replay("DEC-1")
    assert {r.decision_id for r in repo.browse()} == before   # no re-commit / no new record


def test_replay_is_byte_identical_across_ten_runs():
    repo, engine = InMemoryAuditRepository(), _engine()
    _seed(repo, engine)
    svc = ReplayService(repo, engine)
    baseline = canon_ser(svc.replay("DEC-1").fresh_projection)
    for _ in range(10):
        assert canon_ser(svc.replay("DEC-1").fresh_projection) == baseline


def test_bias_swap_on_snapshot_yields_identical_projection():
    # BR1-1 storage != influence: swapping demographics on the snapshot, identical
    # financials, replays to the SAME projection (evaluate() excludes demographics).
    import backend.intake.schema as isch
    repo, engine = InMemoryAuditRepository(), _engine()
    base_profile = f.make_profile()
    swapped_profile = f.make_profile(
        demographics=isch.Demographics(full_name="Zed Zephyr", gender=isch.Gender.MALE, city="Gotham"))
    _seed(repo, engine, profile=base_profile, decision_id="D-BASE")
    _seed(repo, engine, profile=swapped_profile, decision_id="D-SWAP")
    svc = ReplayService(repo, engine)
    assert svc.replay("D-BASE").fresh_projection == svc.replay("D-SWAP").fresh_projection


def test_replay_uses_recorded_rulebook_version_as_load_key():
    # A record stored under 1.0.0 replays against 1.0.0 (the load key), reproducing.
    repo, engine = InMemoryAuditRepository(), _engine()
    profile = f.make_profile(existing_debt_obligations_annual=Decimal("380000"))  # dti 0.38
    _seed(repo, engine, profile=profile, version="1.0.0")
    assert ReplayService(repo, engine).replay("DEC-1").match is True
