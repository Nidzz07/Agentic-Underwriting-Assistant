"""Composition root — ``python -m backend.authn`` (omitted from unit coverage).

⚑ **This file was specified by the approved code-gen plan (AUTHN-Fold-1, step 7) and MISSED
in execution.** Without it ``backend/authn/admin.py`` was a pure library with nothing runnable:
``python -m backend.authn.admin set-password …`` imported the module, found no ``__main__``
guard, and exited **0 with no output and no rows written** — a silent no-op that looked like
success. Found during manual login verification, not by the suite.

Builds the injected ``Engine`` from ``secrets-config``'s ``DATABASE_URL`` and delegates to
:func:`backend.authn.admin.run`. The URL VALUE flows **opaquely** into ``create_engine`` and is
never printed or logged (SEC-3). This is the **only** ``authn`` file that imports
``secrets_config`` or builds an engine; every other module receives what it needs injected and
stays credential-free — the same allowlist shape ``admin_cli/__main__.py`` holds.

⚑ The password is read with :func:`getpass.getpass`, **never from ``sys.argv``**: an argument
would land in shell history, in ``ps`` output, and in any shell-audit log. ``admin.py``'s own
docstring requires this, and a test asserts it structurally.
"""
from __future__ import annotations

import sys
from getpass import getpass

import sqlalchemy as sa

from backend.authn import admin
from backend.authn.repository import PostgresCredentialStore, PostgresUserDirectory
from backend.secrets_config.settings import get_settings


def main() -> int:
    engine = sa.create_engine(get_settings().DATABASE_URL)
    try:
        return admin.run(
            sys.argv[1:],
            store=PostgresCredentialStore(engine),
            users=PostgresUserDirectory(engine),
            prompt=getpass,
        )
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
