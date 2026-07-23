"""NFR-CASE-CANONTIME-1 (P-CASE-9) — canonicalization at the finalizing transition. BR-CASE-9.

The two rich shapes are canonicalized in the EAGER transaction; the four version stamps land at
DRAFTING. `content_hash` is computed at the SAME call site as the bytes it attests, so it cannot
drift from them.
"""
from __future__ import annotations

import hashlib

from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.tests import fixtures as fx


def _submitted():
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(store, fx.drafting_success_double(), fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)
    return store, pipeline, application_id


def test_both_payloads_and_hashes_exist_after_submission():
    store, _pipeline, application_id = _submitted()
    stored = store.get_application(application_id)
    assert stored.profile_canonical is not None
    assert stored.rule_results_canonical is not None
    assert stored.profile_content_hash
    assert stored.rule_results_content_hash


def test_each_content_hash_matches_its_own_stored_bytes():
    """Co-located call site — the hash cannot drift from what it attests."""
    store, _pipeline, application_id = _submitted()
    stored = store.get_application(application_id)
    assert stored.profile_content_hash == hashlib.sha256(stored.profile_canonical).hexdigest()
    assert (
        stored.rule_results_content_hash
        == hashlib.sha256(stored.rule_results_canonical).hexdigest()
    )


def test_the_four_stamps_exist_after_drafting():
    store, pipeline, application_id = _submitted()
    pipeline.draft(application_id)
    rec = store.get_recommendation(fx.recommendation_id_factory(application_id))
    assert rec.memo_hash and rec.model_version and rec.engine_version and rec.rulebook_version


def test_the_application_stamps_are_first_class_scalars_not_blobs():
    store, _pipeline, application_id = _submitted()
    stored = store.get_application(application_id)
    assert isinstance(stored.rulebook_version, str)
    assert isinstance(stored.engine_version, str)
