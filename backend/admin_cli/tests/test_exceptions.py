"""C5 ExceptionTaxonomy — base/subclasses + exit-code attrs (NFR-ADMIN-CLIERR-1)."""
from __future__ import annotations

import pytest

from backend.admin_cli.exceptions import (
    AdminCliError,
    RoleValidationError,
    RulebookPublishError,
    UserWriteError,
)


def test_all_subclasses_derive_from_the_base():
    for exc in (RulebookPublishError, UserWriteError, RoleValidationError):
        assert issubclass(exc, AdminCliError)


def test_each_class_carries_a_distinct_nonzero_exit_code():
    codes = {
        AdminCliError.exit_code,
        RulebookPublishError.exit_code,
        UserWriteError.exit_code,
        RoleValidationError.exit_code,
    }
    assert codes == {1, 2, 3, 4}  # distinct, all non-zero
    assert all(c != 0 for c in codes)


def test_message_is_carried_verbatim():
    exc = UserWriteError("no such user u1")
    assert str(exc) == "no such user u1"
    with pytest.raises(AdminCliError):
        raise RoleValidationError("invalid role 'x'")
