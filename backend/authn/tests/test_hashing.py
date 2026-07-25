"""Argon2id hashing guardrails (Q4.1a + Q4's non-negotiables).

Each of Q4's stated properties is asserted here rather than assumed. The password never
leaves this layer: it is verified against an encoded hash and discarded.
"""
from __future__ import annotations

import ast
from pathlib import Path

from backend.authn.hashing import hash_password, verify_password

_PASSWORD = "correct horse battery staple"


def test_the_same_password_hashes_differently_every_time():
    # ⚑ PER-USER SALT (Q4). argon2-cffi generates a random salt per call and embeds it in
    # the encoded string, so two hashes of the SAME password must differ — and both verify.
    first, second = hash_password(_PASSWORD), hash_password(_PASSWORD)
    assert first != second, "identical hashes imply a missing or constant salt"
    assert verify_password(first, _PASSWORD)
    assert verify_password(second, _PASSWORD)


def test_it_is_argon2id_specifically_not_a_weaker_variant():
    # argon2i and argon2d exist and are NOT what Q4.1(a) chose; the encoded string names
    # the variant, so this pins the primitive rather than merely "some argon2".
    assert hash_password(_PASSWORD).startswith("$argon2id$")


def test_the_wrong_password_does_not_verify():
    encoded = hash_password(_PASSWORD)
    for wrong in ("", " ", _PASSWORD + " ", _PASSWORD.upper(), "correct horse battery stapl"):
        assert not verify_password(encoded, wrong), f"accepted a wrong password: {wrong!r}"


def test_a_malformed_hash_returns_FALSE_rather_than_raising():
    # ⚑ A corrupt or truncated stored hash must FAIL CLOSED, not explode: an exception here
    # would turn a data problem into a 500 and could distinguish it from a wrong password,
    # which is the enumeration oracle Q4's uniform-failure rule forbids.
    for junk in ("", "not-a-hash", "$argon2id$truncated", "$argon2i$v=19$m=1,t=1,p=1$YQ$YQ"):
        assert verify_password(junk, _PASSWORD) is False


def test_verification_uses_the_library_never_a_hand_rolled_comparison():
    # ⚑ CONSTANT-TIME (Q4), asserted STRUCTURALLY. A hand-rolled `==` or `!=` against a hash
    # would be a timing oracle regardless of how the function reads. The module must delegate
    # to argon2-cffi's own verify() and must not compare hash material itself.
    source = (Path(__file__).resolve().parents[1] / "hashing.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    compares = [n for n in ast.walk(tree) if isinstance(n, ast.Compare)]
    for node in compares:
        for op in node.ops:
            assert not isinstance(op, (ast.Eq, ast.NotEq)), (
                "hashing.py performs an equality comparison; hash material must only ever be "
                "checked through argon2-cffi's constant-time verify()"
            )

    called = {
        n.func.attr for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
    }
    assert "verify" in called, "hashing.py must delegate to the library's verify()"
