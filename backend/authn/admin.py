"""Credential provisioning — the half `admin-cli create-user` does not cover (Q3a).

⚑ **The gap this fills, stated plainly.** `admin_cli/cli.py:43-47` creates an `app_user` row
from `user_id, subject, role` and **sets no credential**, so a user it provisions **cannot log
in**. `admin_cli` is a FROZEN unit (U17), so adding `set-password` there would be a
frozen-unit edit needing its own authorization. Q3(a) chose this instead: the capability lives
in the package that already owns hashing, and no frozen unit is touched.

**Disclosed cost, not hidden**: the project now has **two** admin entrypoints — `admin-cli`
for roles and rulebooks, `authn.admin` for credentials. Unifying them is a future U17
reopening decision, not this pass's.

**Injection-pure (AUTHN-Fold-1)**, mirroring `admin_cli/cli.py`: no engine construction, no
`get_settings`, no I/O. `__main__.py` composes it. The password arrives as an argument from a
caller that read it from **stdin/prompt — never from `argv`**, which would leak it into shell
history and the process table.

**No LLM. No logging** — this module handles a plaintext password, so it deliberately has no
logger to misuse.
"""
from __future__ import annotations

from datetime import datetime
from typing import Protocol

from backend.authn.hashing import hash_password
from backend.authn.store import CredentialStore


class CredentialAdminError(Exception):
    """A credential could not be set. Carries the user id — never the password."""


class UserDirectory(Protocol):
    """Read-only existence check against `app_user` (auth-rbac's table; never written here)."""

    def exists(self, user_id: str) -> bool: ...


def set_password(
    user_id: str,
    password: str,
    *,
    store: CredentialStore,
    users: UserDirectory,
    now: datetime,
) -> None:
    """Set (or replace) a user's password.

    Refuses an unknown `user_id` rather than creating an orphan credential: the database
    enforces this with a foreign key, but failing here yields a readable error instead of an
    `IntegrityError` and keeps the rule true for the in-memory store as well.

    Replacing a password also **clears any lockout** — an admin reset that left the account
    locked would appear to succeed while the user still could not log in.
    """
    if not users.exists(user_id):
        raise CredentialAdminError(f"no such user: {user_id}")
    store.set_password(user_id, hash_password(password), now)
