"""The credential-setting entrypoint (Q3a · AUTHN-Fold-1).

⚑ **Why this exists at all.** Q3(a) answered signup as *"admin-provisioning only — already
built via `admin-cli create-user`"*. That is right about **user provisioning** and wrong about
**credential provisioning**: `admin_cli/cli.py` takes `user_id, subject, role` and **no
credential**, so a user it creates **cannot log in**. `admin_cli` is frozen (U17), so the
missing half is added here instead — the only option that adds the capability **without a
frozen-unit edit**.

**Injection-pure**, following `admin_cli/cli.py`'s own split: this module takes an injected
store and a password *reader*, so it is fully testable with no database, no environment and
no terminal. The thin `__main__.py` does the composition.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.authn.admin import CredentialAdminError, set_password
from backend.authn.hashing import verify_password
from backend.authn.store import InMemoryCredentialStore

_NOW = datetime(2026, 7, 25, 9, 0, 0, tzinfo=timezone.utc)


class _Users:
    """Stands in for the `app_user` existence check (auth-rbac's table, read-only)."""

    def __init__(self, known: set[str]) -> None:
        self._known = known

    def exists(self, user_id: str) -> bool:
        return user_id in self._known


def test_it_sets_a_verifiable_password_for_a_known_user():
    store = InMemoryCredentialStore()
    set_password("u1", "s3cret-passphrase", store=store, users=_Users({"u1"}), now=_NOW)

    record = store.get("u1")
    assert record is not None
    # ⚑ The PLAINTEXT must never be what is stored.
    assert record.password_hash != "s3cret-passphrase"
    assert record.password_hash.startswith("$argon2id$")
    assert verify_password(record.password_hash, "s3cret-passphrase")


def test_setting_a_password_again_replaces_it_and_clears_any_lock():
    store = InMemoryCredentialStore()
    users = _Users({"u1"})
    set_password("u1", "first-passphrase", store=store, users=users, now=_NOW)
    first = store.get("u1").password_hash

    set_password("u1", "second-passphrase", store=store, users=users, now=_NOW)
    record = store.get("u1")

    assert record.password_hash != first
    assert verify_password(record.password_hash, "second-passphrase")
    assert not verify_password(record.password_hash, "first-passphrase")
    # ⚑ An admin resetting a password must also release a lockout — otherwise the reset
    # appears to work and the user still cannot log in for another fifteen minutes.
    assert record.failed_attempts == 0 and record.locked_until is None


def test_it_refuses_an_unknown_user_rather_than_creating_an_orphan_credential():
    # ⚑ The DB enforces this with a FK, but failing HERE gives the admin a readable error
    # instead of an IntegrityError, and keeps the rule true for the in-memory store too.
    store = InMemoryCredentialStore()
    with pytest.raises(CredentialAdminError) as exc:
        set_password("ghost", "s3cret-passphrase", store=store, users=_Users({"u1"}), now=_NOW)

    assert "ghost" in str(exc.value)
    assert "s3cret-passphrase" not in str(exc.value), "the error echoed the password"
    assert store.get("ghost") is None
