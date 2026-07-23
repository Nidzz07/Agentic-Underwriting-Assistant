"""Unit tests — C5 UserRoleRepository Protocol + in-memory fake (Step 3).

The read contract returns the RAW `app_user.role` value (`str | None`) — `None` for an
unknown user; otherwise the stored string exactly (canonical or not). Canonicalization
lives in `authorize`, NOT here (FD §2.5). BIAS-1: the read model reads only `user_id`.
"""
from __future__ import annotations

import inspect

from backend.auth_rbac.repository import InMemoryUserRoleRepository, UserRoleRepository


def test_fake_returns_raw_role_string():
    repo = InMemoryUserRoleRepository({"u1": "underwriter", "u2": "wizard", "u3": ""})
    assert repo.get_role("u1") == "underwriter"
    assert repo.get_role("u2") == "wizard"   # raw, non-canonical, NOT mapped here
    assert repo.get_role("u3") == ""          # raw, blank, NOT mapped here


def test_fake_unknown_user_is_none():
    repo = InMemoryUserRoleRepository({})
    assert repo.get_role("nobody") is None


def test_fake_conforms_to_protocol():
    assert isinstance(InMemoryUserRoleRepository({}), UserRoleRepository)


def test_get_role_signature_reads_only_user_id():
    # BIAS-1 (read side): the read model's only input is user_id — no demographic shape.
    sig = inspect.signature(UserRoleRepository.get_role)
    params = [p for p in sig.parameters if p != "self"]
    assert params == ["user_id"]
