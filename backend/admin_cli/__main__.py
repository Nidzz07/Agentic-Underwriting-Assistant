"""C1 composition root — ``python -m backend.admin_cli`` (omitted from unit coverage).

Builds the injected ``Engine`` from ``secrets-config``'s ``DATABASE_URL`` and resolves
the rulebook dir, then delegates to :func:`backend.admin_cli.cli.main`. The URL VALUE
flows **opaquely** into ``create_engine`` and is **never printed/logged** (SEC-3: no
secret LITERAL here, no VALUE echoed).

This is the **only** admin-cli file permitted to import ``secrets_config`` / build an
``Engine`` — the C6 structural scan allowlists it **by name** (ADMIN-CG-Fold-1); every
other module receives the engine injected and stays credential-free. Omitted from unit
coverage (composition-root entry, like other unit entrypoints). No LLM.
"""
from __future__ import annotations

import os
import sys

import sqlalchemy as sa

from backend.admin_cli import cli
from backend.secrets_config.settings import get_settings

#: Where published ``{version}.yaml`` files live (rules-engine's versioning dir);
#: overridable for out-of-band operation. Not a secret.
_DEFAULT_RULEBOOK_DIR = os.path.join("backend", "rules_engine", "rulebook")


def main() -> int:
    settings = get_settings()
    engine = sa.create_engine(settings.DATABASE_URL)
    rulebook_dir = os.environ.get("RULEBOOK_DIR", _DEFAULT_RULEBOOK_DIR)
    try:
        return cli.main(sys.argv[1:], engine=engine, rulebook_dir=rulebook_dir)
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
