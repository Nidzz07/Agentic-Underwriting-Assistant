"""SEC-1 (governance): no key/endpoint VALUE in U21 code (SEC-3 / BR-SEC-6); the reserved
``LANGFUSE_*`` names are deploy shapes, not code literals. Labels are demographic-free (CON-BR1).
"""
from __future__ import annotations

from backend.observability.tests import structural as sg


_SECRET_VALUE_TOKENS = ("sk-", "pk-", "secret_key", "SECRET_KEY=", "Bearer ")
# a LANGFUSE_* NAME may be documented, but never assigned a value literal in code.
_KEY_ASSIGNMENT_TOKENS = ('LANGFUSE_PUBLIC_KEY="', "LANGFUSE_PUBLIC_KEY='",
                          'LANGFUSE_SECRET_KEY="', "LANGFUSE_SECRET_KEY='")


def test_no_secret_value_literal_in_any_production_module():
    for path in sg.production_py_files():
        text = path.read_text(encoding="utf-8")
        for token in _SECRET_VALUE_TOKENS:
            assert token not in text, f"{path.name} carries a secret-value token {token!r}"


def test_no_langfuse_key_is_assigned_a_value_in_code():
    for path in sg.production_py_files():
        text = path.read_text(encoding="utf-8")
        for token in _KEY_ASSIGNMENT_TOKENS:
            assert token not in text, f"{path.name} assigns a LANGFUSE key value ({token!r})"


def test_no_demographic_label_name_in_production():
    demographic = {"full_name", "gender", "city", "demographics", "age", "religion"}
    for path in sg.production_py_files():
        assert not (sg.attribute_names(sg.parse(path)) & demographic), path.name
