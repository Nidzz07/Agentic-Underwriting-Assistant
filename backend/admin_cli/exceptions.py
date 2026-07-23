"""C5 ExceptionTaxonomy — ``AdminCliError`` base + typed subclasses (P5 / CLIERR-1).

Handlers raise a typed error; the entrypoint (``cli.main``) maps it to the carried
``exit_code`` + a **no-secret** stderr ``error: {message}`` line (NFR-ADMIN-CLIERR-1 /
NFR-ADMIN-NOSECRET-1). Messages carry only names/status — never a URL/credential VALUE.
No LLM. No DB.
"""
from __future__ import annotations


class AdminCliError(Exception):
    """Base for every operator-facing admin-cli error. Carries the process exit
    code the entrypoint returns for this failure class."""

    exit_code: int = 1


class RulebookPublishError(AdminCliError):
    """A rulebook publish failed — validation reject, declared-version mismatch,
    or an already-existing (append-only) version."""

    exit_code = 2


class UserWriteError(AdminCliError):
    """An ``app_user`` write failed — duplicate (``already exists``) or absent
    (``no such user``)."""

    exit_code = 3


class RoleValidationError(AdminCliError):
    """A role is not in auth-rbac's canonical ``Role`` set — rejected BEFORE any
    connection is acquired (the SOLE gate, SEC-4)."""

    exit_code = 4
