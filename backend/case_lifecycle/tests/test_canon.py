"""NFR-CASE-CANON-1 (P-CASE-1) — LOAD-BEARING (full-highest). BR-CASE-7.

⚑ **The BEHAVIOURAL half of a deliberate PAIR.** This file exercises the **bytes**: round-trip
identity, type fidelity, hash stability, mutation detection. Its partner ``test_adapter.py``
(ADAPTER-1) exercises the **call sites** via an AST scan.

**Neither alone is sufficient — that is why they are two files for two targets.** CANON-1 would
still pass on a **correct-but-FORKED** serializer; ADAPTER-1 would still pass on a **broken** one.
They read different things (bytes vs the AST), so **no single edit can weaken both.**

Why full-highest: if canonicalization drifts, hash equality breaks **silently on a later run**
and surfaces only at replay — the worst failure location for an audit system.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.case_lifecycle.tests import fixtures as fx
from backend.common.canon_ser import CanonSerError, canon_ser, content_hash


def test_profile_round_trip_is_byte_identical():
    profile = fx.make_profile()
    raw = CanonSerAdapter.canonical_bytes(profile)
    back = CanonSerAdapter.profile_from_canonical(raw)
    again = CanonSerAdapter.canonical_bytes(back)
    assert again == raw


def test_report_round_trip_is_byte_identical():
    report = fx.make_report()
    raw = CanonSerAdapter.canonical_bytes(report)
    back = CanonSerAdapter.report_from_canonical(raw)
    again = CanonSerAdapter.canonical_bytes(back)
    assert again == raw


def test_decimal_returns_as_decimal_not_string():
    """CANON-SER P2/P3 type fidelity — the `$dec` envelope must survive the round trip."""
    profile = fx.make_profile()
    back = CanonSerAdapter.profile_from_canonical(
        CanonSerAdapter.canonical_bytes(profile)
    )
    assert isinstance(back.verifiable_income_annual, Decimal)
    assert back.verifiable_income_annual == profile.verifiable_income_annual


def test_date_returns_as_date_not_string():
    profile = fx.make_profile()
    back = CanonSerAdapter.profile_from_canonical(
        CanonSerAdapter.canonical_bytes(profile)
    )
    assert back.date_of_birth == profile.date_of_birth
    assert not isinstance(back.date_of_birth, str)


def test_content_hash_is_stable_across_repeated_runs():
    """P1/P4 — no key-order drift, no volatile field injected."""
    first = CanonSerAdapter.content_hash(fx.make_profile())
    second = CanonSerAdapter.content_hash(fx.make_profile())
    assert first == second


def test_content_hash_matches_a_hash_of_the_canonical_bytes():
    profile = fx.make_profile()
    raw = CanonSerAdapter.canonical_bytes(profile)
    import hashlib

    assert CanonSerAdapter.content_hash(profile) == hashlib.sha256(raw).hexdigest()


def test_detector_a_flipped_byte_fails_the_hash_check():
    """⚑ The mutation detector — the hash must actually catch tampering."""
    profile = fx.make_profile()
    raw = CanonSerAdapter.canonical_bytes(profile)
    expected = CanonSerAdapter.content_hash(profile)

    tampered = bytearray(raw)
    tampered[len(tampered) // 2] ^= 0x01
    import hashlib

    assert hashlib.sha256(bytes(tampered)).hexdigest() != expected


def test_detector_a_float_raises_rather_than_silently_serializing():
    """P2 is ENFORCED, not hoped for — IEEE float is rejected outright."""
    with pytest.raises(CanonSerError):
        canon_ser({"amount": 1.5})


def test_key_order_does_not_change_the_bytes():
    """P1 — declared vs insertion order must produce identical bytes."""
    assert canon_ser({"b": 1, "a": 2}) == canon_ser({"a": 2, "b": 1})
    assert content_hash({"b": 1, "a": 2}) == content_hash({"a": 2, "b": 1})
