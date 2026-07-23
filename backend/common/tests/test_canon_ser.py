"""Tests for the single shared CANON-SER utility (Step 1).

Maps: NFR-INT-DET-2 (ApplicantProfile round-trip byte-identity — the replay
dependency). CANON-SER is the ONE serialization spec defined by
``audit-store domain-entities.md §2.1`` and shared (single implementation, no
copy-paste) by intake's ``CanonSerAdapter`` and by ``audit-store``.

Sharpening 3 (folded in): this suite asserts §2.1's FOUR properties EXPLICITLY,
not merely round-trip byte-identity (round-trip alone does not prove
lexicographic key ordering). The four properties:

  P1  stable lexicographic key ordering (never dict-insertion / hash order)
  P2  Decimal as string (never IEEE float)
  P3  canonical scalar forms — enums as declared value, null explicit,
      no environment-dependent number/date formatting
  P4  no volatile fields injected (no wall-clock, no run-scoped ids)

Property-based (Hypothesis) is used for the universal-quantifier round-trip
invariant; explicit example tests pin the four named properties.
"""
from __future__ import annotations

import time
from decimal import Decimal
from datetime import date, datetime, timezone
from enum import Enum

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.common.canon_ser import (
    CanonSerError,
    canon_ser,
    canon_deserialize,
    content_hash,
)


class _Color(Enum):
    RED = "red"
    BLUE = "blue"


# --------------------------------------------------------------------------
# P1 — stable lexicographic key ordering
# --------------------------------------------------------------------------
def test_p1_key_order_is_lexicographic_not_insertion_order():
    # Same logical content, two different INSERTION orders -> identical bytes.
    a = canon_ser({"b": 1, "a": 2, "c": 3})
    b = canon_ser({"c": 3, "a": 2, "b": 1})
    assert a == b

    # And the bytes are actually in lexicographic key order (a < b < c).
    text = a.decode("utf-8")
    assert text.index('"a"') < text.index('"b"') < text.index('"c"')


def test_p1_nested_dicts_also_sorted():
    out = canon_ser({"z": {"y": 1, "x": 2}}).decode("utf-8")
    assert out.index('"x"') < out.index('"y"')


# --------------------------------------------------------------------------
# P2 — Decimal as string, never float
# --------------------------------------------------------------------------
def test_p2_decimal_serialized_as_string_preserving_scale():
    out = canon_ser(Decimal("25.00")).decode("utf-8")
    # Scale preserved verbatim ("25.00", not "25" or 25.0), and carried as a
    # tagged STRING value, never a bare JSON number.
    assert '"25.00"' in out
    assert "25.0," not in out  # no bare float form leaking


def test_p2_float_input_is_rejected():
    # IEEE float must never enter the canonical form (CON-DET-1).
    with pytest.raises(CanonSerError):
        canon_ser(1.5)
    with pytest.raises(CanonSerError):
        canon_ser({"x": 0.1})


def test_p2_non_finite_decimal_rejected():
    with pytest.raises(CanonSerError):
        canon_ser(Decimal("NaN"))
    with pytest.raises(CanonSerError):
        canon_ser(Decimal("Infinity"))


# --------------------------------------------------------------------------
# P3 — canonical scalar forms: enums by value, null explicit, stable dates
# --------------------------------------------------------------------------
def test_p3_enum_serialized_by_declared_value():
    assert canon_ser(_Color.RED) == canon_ser("red")


def test_p3_null_is_explicit():
    assert canon_ser(None) == b"null"
    assert b"null" in canon_ser({"missing": None})


def test_p3_dates_are_iso_and_environment_independent():
    d = canon_ser(date(2026, 1, 5)).decode("utf-8")
    assert "2026-01-05" in d
    dt = canon_ser(datetime(2026, 1, 5, 10, 30, tzinfo=timezone.utc)).decode("utf-8")
    assert "2026-01-05T10:30:00+00:00" in dt


def test_p3_bool_is_canonical():
    assert canon_ser(True) == b"true"
    assert canon_ser(False) == b"false"


# --------------------------------------------------------------------------
# P4 — no volatile fields injected by the serializer
# --------------------------------------------------------------------------
def test_p4_serializer_injects_nothing_time_dependent():
    payload = {"application_id": "APP-1", "income": Decimal("50000.00")}
    first = canon_ser(payload)
    time.sleep(0.01)  # wall-clock advances
    second = canon_ser(payload)
    assert first == second  # no timestamp / run-id injected


def test_p4_reserved_dollar_keys_rejected():
    # $-prefixed keys are reserved for type envelopes; real data must not use
    # them, so the format cannot be ambiguous.
    with pytest.raises(CanonSerError):
        canon_ser({"$dec": "oops"})


def test_non_string_dict_key_rejected():
    with pytest.raises(CanonSerError):
        canon_ser({1: "a"})


def test_unserializable_type_rejected():
    with pytest.raises(CanonSerError):
        canon_ser(object())


def test_deserialize_requires_bytes():
    with pytest.raises(CanonSerError):
        canon_deserialize("not-bytes")  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# Round-trip: byte-identity + type fidelity (the replay dependency)
# --------------------------------------------------------------------------
def test_round_trip_preserves_decimal_type():
    restored = canon_deserialize(canon_ser(Decimal("40.00")))
    assert isinstance(restored, Decimal)
    assert restored == Decimal("40.00")


def test_round_trip_preserves_date_types():
    assert canon_deserialize(canon_ser(date(2026, 6, 14))) == date(2026, 6, 14)
    dt = datetime(2026, 6, 14, 9, 0, tzinfo=timezone.utc)
    assert canon_deserialize(canon_ser(dt)) == dt


def test_content_hash_is_deterministic_and_hex():
    payload = {"a": Decimal("1.00"), "b": [1, 2, 3], "c": None}
    h1 = content_hash(payload)
    h2 = content_hash({"c": None, "b": [1, 2, 3], "a": Decimal("1.00")})
    assert h1 == h2
    assert len(h1) == 64  # sha256 hex


# Recursive strategy over the canonical value space (str keys, no '$' prefix).
_dict_keys = st.text(min_size=1, max_size=8).filter(lambda s: not s.startswith("$"))
_leaves = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-(10**9), max_value=10**9),
    st.text(max_size=20),
    st.decimals(
        min_value=Decimal("-1000000"),
        max_value=Decimal("1000000"),
        allow_nan=False,
        allow_infinity=False,
        places=2,
    ),
)
_canonical_values = st.recursive(
    _leaves,
    lambda children: st.one_of(
        st.lists(children, max_size=4),
        st.dictionaries(_dict_keys, children, max_size=4),
    ),
    max_leaves=15,
)


@pytest.mark.property
@settings(max_examples=200)
@given(value=_canonical_values)
def test_round_trip_byte_identity_property(value):
    once = canon_ser(value)
    twice = canon_ser(canon_deserialize(once))
    assert once == twice  # serialize -> deserialize -> serialize is byte-identical
