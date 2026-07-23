"""C1 ArgparseEntrypoint (dispatch) — ``build_parser`` + ``main`` (P5 / CLIERR-1).

argparse root with three subparsers (``publish-rulebook`` / ``create-user`` /
``set-role``), each binding a handler via ``set_defaults``. ``main(argv, *, engine,
rulebook_dir)`` parses, dispatches, and maps a raised :class:`AdminCliError` -> its
``exit_code`` + a **no-secret** stderr ``error: {message}`` line; success -> exit 0 + a
names-only status line on stdout.

**Injection-pure**: the ``Engine`` + rulebook dir are parameters (the composition root
is ``__main__.py``), so this module is fully unit-testable with a fake engine +
``tmp_path`` — and reads/prints **no** secret VALUE (NFR-ADMIN-NOSECRET-1). No LLM.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence, TextIO

import sqlalchemy as sa

from backend.admin_cli.app_user_writer import AppUserWriter
from backend.admin_cli.exceptions import AdminCliError
from backend.admin_cli.pg_writer import PgWriter
from backend.admin_cli.role_gate import RoleGate
from backend.admin_cli.rulebook_publisher import RulebookPublisher


def build_parser() -> argparse.ArgumentParser:
    """The argparse root with the three Phase-1 subcommands (no ``set-provider`` —
    provider-config management is deferred to P2, NFR-ADMIN-PROVIDER-DEFER-1)."""
    parser = argparse.ArgumentParser(
        prog="admin-cli",
        description="Out-of-band rulebook publishing + user/role management.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pub = sub.add_parser("publish-rulebook", help="publish an immutable rulebook version")
    p_pub.add_argument("version", help="target semver, e.g. 1.2.0")
    p_pub.add_argument("source", help="path to the rulebook YAML source")
    p_pub.set_defaults(handler=_handle_publish)

    p_create = sub.add_parser("create-user", help="create an app_user")
    p_create.add_argument("user_id")
    p_create.add_argument("subject")
    p_create.add_argument("role")
    p_create.set_defaults(handler=_handle_create_user)

    p_set = sub.add_parser("set-role", help="set an existing app_user's role")
    p_set.add_argument("user_id")
    p_set.add_argument("role")
    p_set.set_defaults(handler=_handle_set_role)

    return parser


def _handle_publish(args: argparse.Namespace, *, engine: sa.Engine, rulebook_dir, out: TextIO) -> None:
    source_text = Path(args.source).read_text(encoding="utf-8")
    RulebookPublisher(rulebook_dir).publish(args.version, source_text)
    print(f"published rulebook {args.version}", file=out)


def _handle_create_user(args: argparse.Namespace, *, engine: sa.Engine, rulebook_dir, out: TextIO) -> None:
    AppUserWriter(PgWriter(engine), RoleGate()).create_user(args.user_id, args.subject, args.role)
    print(f"created user {args.user_id} ({args.role})", file=out)


def _handle_set_role(args: argparse.Namespace, *, engine: sa.Engine, rulebook_dir, out: TextIO) -> None:
    AppUserWriter(PgWriter(engine), RoleGate()).set_role(args.user_id, args.role)
    print(f"set role for {args.user_id} -> {args.role}", file=out)


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    engine: sa.Engine,
    rulebook_dir,
    out: Optional[TextIO] = None,
    err: Optional[TextIO] = None,
) -> int:
    """Parse ``argv``, dispatch to the bound handler, map typed errors to exit codes.

    Returns 0 on success; a typed :class:`AdminCliError`'s ``exit_code`` on failure,
    printing ``error: {message}`` to ``err`` (no secret VALUE)."""
    out = out if out is not None else sys.stdout
    err = err if err is not None else sys.stderr
    args = build_parser().parse_args(argv)
    try:
        args.handler(args, engine=engine, rulebook_dir=rulebook_dir, out=out)
    except AdminCliError as exc:
        print(f"error: {exc}", file=err)
        return exc.exit_code
    return 0
