"""MEMOCANON-1 — the memo rehydration adapter (U24's THIRD AUTHORIZED REOPENING, Q14-A).

⚑ **The behavioural half of a deliberate PAIR**, mirroring CANON-1/ADAPTER-1's split: this file
reads the **bytes** (does a memo survive the round trip intact?); ``test_adapter.py``'s narrowed
allowlist assertions read the **AST** (is the exception thin, and does it stay one module wide?).

**Neither alone is sufficient**: a bytes test would pass on an adapter that had quietly grown a
serialize direction or extra logic; the AST tests would pass on one that round-tripped wrongly.
"""
from __future__ import annotations

import pytest

from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.case_lifecycle.memo_adapter import MemoCanonAdapter
from backend.case_lifecycle.tests import fixtures as fx
from backend.memo_agent_core.schemas import DecisionMemo


def _memo() -> DecisionMemo:
    """The memo the tier-U drafting double produces — the same shape the pipeline persists."""
    return fx.drafting_success_double().draft_memo(None, None, None)


def test_a_memo_round_trips_through_canonical_bytes():
    """⚑ The load-bearing property: serialize (FROZEN adapter) -> rehydrate (this adapter)."""
    original = _memo()
    restored = MemoCanonAdapter.memo_from_canonical(
        CanonSerAdapter.canonical_bytes(original)
    )
    assert restored == original


def test_the_round_trip_preserves_the_memo_hash_exactly():
    """``memo_hash`` is a REPRODUCIBILITY stamp — a lossy round trip would corrupt replay."""
    original = _memo()
    restored = MemoCanonAdapter.memo_from_canonical(
        CanonSerAdapter.canonical_bytes(original)
    )
    assert restored.memo_hash == original.memo_hash
    assert restored.model_version == original.model_version


def test_the_round_trip_is_byte_stable_across_repeated_serialization():
    """Rehydrate-then-reserialize must reproduce the SAME bytes (CANON-SER P1-P4)."""
    once = CanonSerAdapter.canonical_bytes(_memo())
    twice = CanonSerAdapter.canonical_bytes(MemoCanonAdapter.memo_from_canonical(once))
    assert once == twice


def test_the_cited_rule_ids_survive_as_a_list_not_a_scalar():
    """A memo's citations are its audit evidence — the collection shape must not collapse."""
    original = _memo()
    restored = MemoCanonAdapter.memo_from_canonical(
        CanonSerAdapter.canonical_bytes(original)
    )
    assert isinstance(restored.cited_rule_ids, list)
    assert restored.cited_rule_ids == original.cited_rule_ids


def test_a_flipped_byte_fails_rather_than_silently_returning_a_wrong_memo():
    """⚑ Corruption must RAISE. Silently rehydrating a mangled memo would be far worse."""
    data = bytearray(CanonSerAdapter.canonical_bytes(_memo()))
    data[len(data) // 2] ^= 0xFF
    with pytest.raises(Exception):
        MemoCanonAdapter.memo_from_canonical(bytes(data))


def test_non_bytes_input_raises():
    with pytest.raises(Exception):
        MemoCanonAdapter.memo_from_canonical("not-bytes")  # type: ignore[arg-type]


def test_the_adapter_exposes_only_the_rehydration_direction():
    """⚑ No serialize half — that stays with the FROZEN adapter, unforked (Q14-A)."""
    public = {name for name in dir(MemoCanonAdapter) if not name.startswith("_")}
    assert public == {"memo_from_canonical"}
