"""DEMOFREE-1: the SINGLE detector self-test lives AT the allowlist utility (Fold-2) — the
single-sourced guarantee gets a single-sourced test. A forbidden attribute (demographic /
free-text / non-scalar object) is DROPPED by ``project_allowlisted``; only allowlisted scalars pass.
"""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from backend.observability.allowlist import _is_scalar, project_allowlisted


_ALLOWED = frozenset({"recommendation", "duration_ms"})


def test_forbidden_attribute_is_dropped_the_detector_self_test():
    fields = {
        "recommendation": "APPROVE",      # allowlisted scalar — kept
        "duration_ms": 1234,              # allowlisted scalar — kept
        "full_name": "Jane Doe",          # demographic — dropped (not in allowed)
        "memo_prose": "free text",        # free-text — dropped
        "original_span": object(),        # non-scalar — dropped
    }
    projected = project_allowlisted(fields, _ALLOWED)
    assert projected == {"recommendation": "APPROVE", "duration_ms": 1234}
    assert "full_name" not in projected
    assert "original_span" not in projected


def test_non_scalar_value_on_an_allowlisted_name_is_still_dropped():
    # allow-listed NAME but non-scalar VALUE — dropped (scalar-only projection).
    assert project_allowlisted({"duration_ms": [1, 2, 3]}, _ALLOWED) == {}
    assert project_allowlisted({"recommendation": None}, _ALLOWED) == {}


def test_is_scalar_accepts_only_allowlist_leaves():
    assert _is_scalar("x") and _is_scalar(1) and _is_scalar(1.5) and _is_scalar(True)
    assert not _is_scalar(object()) and not _is_scalar([1]) and not _is_scalar(None)
    assert not _is_scalar({"a": 1})


@pytest.mark.property
@given(
    forbidden_key=st.text(min_size=1).filter(lambda s: s not in _ALLOWED),
    value=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False), st.booleans()),
)
def test_property_any_non_allowlisted_key_is_always_dropped(forbidden_key, value):
    projected = project_allowlisted({forbidden_key: value}, _ALLOWED)
    assert forbidden_key not in projected


@pytest.mark.property
@given(value=st.one_of(st.lists(st.integers()), st.none(), st.dictionaries(st.text(), st.integers())))
def test_property_any_non_scalar_value_is_always_dropped(value):
    assert project_allowlisted({"recommendation": value}, _ALLOWED) == {}
