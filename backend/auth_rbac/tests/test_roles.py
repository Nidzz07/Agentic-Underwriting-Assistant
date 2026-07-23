"""Unit tests — C2 Role + C4 to_role (Step 2).

`to_role` is a TOTAL function: raw `app_user.role` (str | None) -> canonical Role or
None. It fail-closes to None for None / blank / non-canonical, with NO exception as
control flow. This is what makes DENY-1's cases (ii) non-canonical and (iii) blank
independently constructible from case (i) unknown user.
"""
from __future__ import annotations

import pytest

from backend.auth_rbac.roles import Role, to_role


def test_role_set_is_exactly_the_three_canonical():
    assert {r.value for r in Role} == {"underwriter", "auditor", "admin"}


# canonical exact match -> the Role member
@pytest.mark.parametrize("raw,expected", [
    ("underwriter", Role.UNDERWRITER),
    ("auditor", Role.AUDITOR),
    ("admin", Role.ADMIN),
])
def test_to_role_canonical_exact_match(raw, expected):
    assert to_role(raw) is expected


# case (i)-source: None (no row) -> None
def test_to_role_none():
    assert to_role(None) is None


# case (iii): blank / whitespace -> None
@pytest.mark.parametrize("raw", ["", " ", "   ", "\t", "\n"])
def test_to_role_blank(raw):
    assert to_role(raw) is None


# case (ii): non-canonical -> None (incl. wrong case / surrounding whitespace = fail-close)
@pytest.mark.parametrize("raw", ["wizard", "UNDERWRITER", "Underwriter", " underwriter ", "under", "adminx"])
def test_to_role_noncanonical(raw):
    assert to_role(raw) is None


def test_to_role_is_total_and_deterministic():
    # every input has a defined result; repeated calls are identical
    for raw in (None, "", "admin", "wizard"):
        assert to_role(raw) == to_role(raw)
