"""Argon2id password hashing — the only place a plaintext password is ever handled.

**Q4.1(a)**: Argon2id, the memory-hard OWASP-recommended primitive. Chosen over bcrypt/scrypt
because if a BFSI system is creating its first credential store in 2026 there is no reason to
create it with a weaker one, and the dependency cost is a single wheel.

**The non-negotiables (Q4), each asserted by a test in ``tests/test_hashing.py``:**

* **Per-user salt** — ``argon2-cffi`` generates a random salt per hash and embeds it in the
  encoded string, so the same password never produces the same hash twice.
* **Constant-time verification** — delegated entirely to the library's ``verify()``. This
  module performs **no equality comparison of hash material**, which the test enforces
  structurally by walking this file's AST: a hand-rolled ``==`` would be a timing oracle no
  matter how carefully it read.
* **Fail-closed on malformed input** — a corrupt or truncated stored hash returns ``False``
  rather than raising. An exception would turn a data problem into a 500 **and** would let a
  caller distinguish it from a wrong password, which is precisely the enumeration oracle the
  uniform-failure rule forbids.

**Purity**: no I/O, no DB, no environment, no logging. A password reaching this module is
verified and discarded — it is never returned, stored, echoed, or passed anywhere else.
**No LLM.**
"""
from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error, InvalidHashError

#: One shared hasher. Library defaults are deliberately NOT overridden — argon2-cffi tracks
#: the current OWASP guidance, and hand-tuning cost parameters without a benchmark is how
#: credential stores end up weaker than the library's own baseline.
_HASHER = PasswordHasher()


def hash_password(password: str) -> str:
    """Return the Argon2id **encoded string** — algorithm, parameters, salt and digest.

    The salt is generated fresh per call, so this is not a pure function of its input and
    must never be used to compare two passwords by hashing both.
    """
    return _HASHER.hash(password)


def verify_password(encoded: str, password: str) -> bool:
    """``True`` iff ``password`` matches ``encoded``. Never raises; never leaks a reason.

    ⚑ The caller cannot tell *why* verification failed — wrong password, corrupt hash, or
    unparseable stored value all return the same ``False``. That is deliberate: the reason
    is exactly the signal an attacker enumerating accounts wants.
    """
    try:
        return _HASHER.verify(encoded, password)
    except (Argon2Error, InvalidHashError, TypeError, ValueError):
        return False
