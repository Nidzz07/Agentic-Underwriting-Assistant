"""The CLI entrypoint — the defect this file exists because of.

⚑ **What went wrong.** The approved code-gen plan specified `backend/authn/__main__.py`
(AUTHN-Fold-1, step 7) and execution never created it. `admin.py` was a pure library, so
`python -m backend.authn.admin set-password …` imported it, found no `__main__` guard, and
exited **0 with no output and no rows written** — a silent no-op indistinguishable from
success. It was found during **manual login verification**, not by this suite.

⚑ **Why the suite missed it.** `test_admin.py` exercised `set_password()` — the *function* —
thoroughly. Nothing exercised the **invocation**. And because `__main__.py` was
coverage-omitted (correctly, as a composition root), its **absence produced no signal at
all**: a file that does not exist and is excluded from coverage is invisible twice over.

The lesson is the last test below: for an omitted composition root, **presence and shape must
be asserted structurally**, exactly as `admin_cli`'s suite asserts its own `__main__.py` is
among its module names.
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

from backend.authn.admin import run
from backend.authn.hashing import verify_password
from backend.authn.store import InMemoryCredentialStore

_NOW = datetime(2026, 7, 25, 9, 0, 0, tzinfo=timezone.utc)
_MAIN = Path(__file__).resolve().parents[1] / "__main__.py"


class _Users:
    def __init__(self, known: set[str]) -> None:
        self._known = known

    def exists(self, user_id: str) -> bool:
        return user_id in self._known


def _prompter(*values: str):
    """A getpass stand-in returning each supplied value in turn."""
    it = iter(values)
    return lambda _prompt: next(it)


def test_set_password_writes_a_verifiable_credential_and_exits_zero():
    store, out = InMemoryCredentialStore(), []
    code = run(
        ["set-password", "u1"],
        store=store, users=_Users({"u1"}),
        prompt=_prompter("s3cret-passphrase", "s3cret-passphrase"),
        now=_NOW, out=out.append,
    )
    assert code == 0
    assert verify_password(store.get("u1").password_hash, "s3cret-passphrase")
    # ⚑ The confirmation must never echo the password itself.
    assert "u1" in out[0] and "s3cret-passphrase" not in out[0]


def test_mismatched_confirmation_changes_nothing_and_exits_non_zero():
    # ⚑ An admin cannot see what they typed. An unconfirmed password would silently lock a
    # user out of an account that looks correctly provisioned.
    store, out = InMemoryCredentialStore(), []
    code = run(
        ["set-password", "u1"],
        store=store, users=_Users({"u1"}),
        prompt=_prompter("typed-one-thing", "typed-another"),
        now=_NOW, out=out.append,
    )
    assert code == 2
    assert store.get("u1") is None, "a mismatched confirmation still wrote a credential"
    assert "did not match" in out[0]


def test_an_unknown_user_is_a_readable_error_not_a_traceback():
    store, out = InMemoryCredentialStore(), []
    code = run(
        ["set-password", "ghost"],
        store=store, users=_Users({"u1"}),
        prompt=_prompter("s3cret-passphrase", "s3cret-passphrase"),
        now=_NOW, out=out.append,
    )
    assert code == 1
    assert out[0].startswith("error: ") and "ghost" in out[0]
    assert "Traceback" not in out[0] and "s3cret-passphrase" not in out[0]
    assert store.get("ghost") is None


def test_the_password_is_never_accepted_as_a_command_line_argument():
    """⚑ The property `admin.py`'s docstring requires: the password comes from a prompt.

    An argv-supplied password lands in shell history, in `ps` output, and in shell-audit
    logs. `set-password` therefore takes **only** a user_id, and a stray extra argument must
    be rejected by the parser rather than silently treated as a password.
    """
    import pytest
    with pytest.raises(SystemExit):
        run(
            ["set-password", "u1", "s3cret-passphrase"],
            store=InMemoryCredentialStore(), users=_Users({"u1"}),
            prompt=_prompter("unused", "unused"), now=_NOW, out=lambda _: None,
        )


def test_the_composition_entrypoint_exists_and_composes_rather_than_reimplements():
    """⚑ THE TEST THAT WOULD HAVE CAUGHT THE DEFECT.

    `__main__.py` is coverage-omitted as a composition root, so its **absence** produced no
    signal whatsoever. Presence and shape are therefore asserted structurally here — the same
    guarantee `admin_cli`'s suite gets from asserting `__main__.py` is among its module names.
    """
    assert _MAIN.exists(), "backend/authn/__main__.py is missing — `python -m backend.authn` is a no-op"

    tree = ast.parse(_MAIN.read_text(encoding="utf-8"))
    functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert "main" in functions

    source = ast.unparse(tree)
    # A runnable module: without this guard `python -m` imports and exits 0, silently.
    assert "__name__ == '__main__'" in source
    # Composes rather than reimplements: delegates to admin.run, builds the engine here only.
    assert "admin.run" in source and "create_engine" in source
    # ⚑ Reads the password from getpass, never from argv.
    assert "getpass" in source
    # Releases the engine even when the command fails.
    assert "dispose" in source
