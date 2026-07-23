"""Tests for CanonSerAdapter (Step 2).

Maps: NFR-AUDIT-CANON-1 — one convention for BOTH ``rule_results`` and the profile,
delegating to the UNCHANGED shared ``backend/common/canon_ser.py``; round-trip
fidelity + ``content_hash`` tamper-evidence.
"""
from __future__ import annotations

import hashlib

from backend.common import canon_ser as cs
from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.audit_store.tests import factories as f


def test_profile_round_trip_fidelity():
    profile = f.make_profile()
    data = CanonSerAdapter.canonical_bytes(profile)
    assert CanonSerAdapter.profile_from_canonical(data) == profile   # exact intake object back


def test_report_round_trip_fidelity():
    report = f.make_report()
    data = CanonSerAdapter.canonical_bytes(report)
    assert CanonSerAdapter.report_from_canonical(data) == report


def test_content_hash_deterministic_and_hex():
    profile = f.make_profile()
    h1 = CanonSerAdapter.content_hash(profile)
    h2 = CanonSerAdapter.content_hash(profile)
    assert h1 == h2 and len(h1) == 64


def test_content_hash_is_tamper_evident():
    base = CanonSerAdapter.content_hash(f.make_profile())
    mutated = CanonSerAdapter.content_hash(f.make_profile(occupation="forger"))
    assert base != mutated   # any change to the canonical content -> different hash


def test_delegates_to_shared_canon_ser_unchanged():
    profile = f.make_profile()
    assert CanonSerAdapter.canonical_bytes(profile) == cs.canon_ser(profile.model_dump(mode="python"))


def test_content_hash_is_sha256_of_canonical_bytes():
    report = f.make_report()
    assert CanonSerAdapter.content_hash(report) == hashlib.sha256(
        CanonSerAdapter.canonical_bytes(report)).hexdigest()
