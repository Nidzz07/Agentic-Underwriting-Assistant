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

import argparse
from datetime import datetime, timezone
from typing import Callable, Optional, Protocol

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


# --- CLI dispatch (injection-pure; ``__main__.py`` composes the real engine) -------------
# ⚑ Mirrors admin_cli's split exactly: the argparse + handler logic lives HERE, counted and
# unit-testable with no database and no terminal; ``__main__.py`` only builds the engine and
# calls in. That is what makes the CLI's behaviour provable at tier-U.

def build_parser() -> argparse.ArgumentParser:
    """``set-password <user_id>``. ⚑ The password is deliberately NOT an argument."""
    parser = argparse.ArgumentParser(
        prog="python -m backend.authn",
        description="Credential administration for the underwriting assistant.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p_set = sub.add_parser("set-password", help="set or replace a user's password")
    p_set.add_argument("user_id", help="an existing app_user.user_id")
    return parser


def run(
    argv: list[str],
    *,
    store: CredentialStore,
    users: UserDirectory,
    prompt: Callable[[str], str],
    now: Optional[datetime] = None,
    out: Callable[[str], None] = print,
) -> int:
    """Dispatch one command. Returns a process exit code; never raises for user error.

    ⚑ The password is read through ``prompt`` — twice, and the two must match. An admin
    cannot see what they typed, so an unconfirmed password would silently lock a user out of
    an account that looks correctly provisioned.

    ⚑ ``CredentialAdminError`` becomes a **readable one-line message and a non-zero exit**,
    never a traceback: this is an operator-facing tool, and a stack trace is not an error
    message. The password is never echoed, never logged, and never placed in any output.
    """
    args = build_parser().parse_args(argv)

    if args.command == "set-password":
        password = prompt("Password: ")
        if password != prompt("Confirm password: "):
            out("error: passwords did not match; nothing was changed")
            return 2
        if not password:
            out("error: password must not be empty; nothing was changed")
            return 2
        try:
            set_password(
                args.user_id, password,
                store=store, users=users,
                now=now if now is not None else datetime.now(timezone.utc),
            )
        except CredentialAdminError as exc:
            out(f"error: {exc}")
            return 1
        out(f"password set for {args.user_id}")
        return 0

    return 2  # pragma: no cover - argparse enforces the subcommand set
