"""CANON-SER — the single canonical serialization utility.

Authoritative spec: ``audit-store domain-entities.md §2.1``. This module is the
ONE implementation of that spec; both intake's ``CanonSerAdapter`` and
``audit-store`` import it (single implementation, no copy-paste). audit-store
remains the *spec authority*; ``backend/common/`` is only the shared *location*.

CANON-SER guarantees the §2.1 properties so replay comparison and
``content_hash`` integrity checks are meaningful — the same logical content
serializes to the same bytes on every run:

  P1  stable lexicographic key ordering (declared, never insertion/hash order)
  P2  ``Decimal`` as string, never IEEE float
  P3  canonical scalar forms — enums by declared value, ``null`` explicit,
      environment-independent number/date formatting
  P4  no volatile fields injected (no wall-clock, no run-scoped ids)

Type fidelity across a round-trip (``Decimal``/``date`` return as themselves,
not strings) is carried by small tagged envelopes on non-JSON-native scalars.
The ``$``-prefixed envelope keys are RESERVED; real data must not use them, so
the canonical form is never ambiguous.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

_DECIMAL_TAG = "$dec"
_DATE_TAG = "$date"
_DATETIME_TAG = "$dt"
_RESERVED_PREFIX = "$"


class CanonSerError(ValueError):
    """Raised when a value cannot be canonically serialized/deserialized."""


def _canonical_decimal_str(value: Decimal) -> str:
    """Plain fixed-point string, scale preserved, no scientific notation."""
    if not value.is_finite():
        raise CanonSerError("non-finite Decimal is not serializable")
    return format(value, "f")


def _to_envelopes(value: Any) -> Any:
    """Reduce a Python value to the JSON-native + tagged-envelope form."""
    # bool BEFORE int (bool is a subclass of int in Python).
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, Enum):  # P3 — enums by declared value
        return _to_envelopes(value.value)
    if isinstance(value, float):  # P2 — reject IEEE float outright
        raise CanonSerError("float is not permitted; use Decimal (CON-DET-1)")
    if isinstance(value, Decimal):  # P2
        return {_DECIMAL_TAG: _canonical_decimal_str(value)}
    if isinstance(value, datetime):  # P3 — check datetime before date (subclass)
        return {_DATETIME_TAG: value.isoformat()}
    if isinstance(value, date):  # P3
        return {_DATE_TAG: value.isoformat()}
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return [_to_envelopes(v) for v in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, val in value.items():
            if not isinstance(key, str):
                raise CanonSerError(f"dict keys must be str, got {type(key)!r}")
            if key.startswith(_RESERVED_PREFIX):
                raise CanonSerError(f"key {key!r} uses the reserved '$' prefix")
            out[key] = _to_envelopes(val)
        return out
    raise CanonSerError(f"type {type(value)!r} is not canonically serializable")


def _object_hook(obj: dict[str, Any]) -> Any:
    """Rebuild tagged envelopes back into their Python types."""
    if len(obj) == 1:
        if _DECIMAL_TAG in obj:
            return Decimal(obj[_DECIMAL_TAG])
        if _DATE_TAG in obj:
            return date.fromisoformat(obj[_DATE_TAG])
        if _DATETIME_TAG in obj:
            return datetime.fromisoformat(obj[_DATETIME_TAG])
    return obj


def canon_ser(value: Any) -> bytes:
    """Serialize ``value`` to canonical UTF-8 bytes per audit-store §2.1.

    Deterministic: P1 sorted keys, P2 Decimal-as-string, P3 canonical scalars,
    P4 nothing volatile injected.
    """
    enveloped = _to_envelopes(value)
    text = json.dumps(
        enveloped,
        sort_keys=True,          # P1
        separators=(",", ":"),   # no incidental whitespace
        ensure_ascii=False,      # P3 — stable UTF-8, not \uXXXX escapes
        allow_nan=False,         # P2 — never NaN/Infinity
    )
    return text.encode("utf-8")


def canon_deserialize(data: bytes) -> Any:
    """Inverse of :func:`canon_ser`, restoring Decimal/date type fidelity."""
    if not isinstance(data, (bytes, bytearray)):
        raise CanonSerError("canon_deserialize expects bytes")
    return json.loads(data.decode("utf-8"), object_hook=_object_hook)


def content_hash(value: Any) -> str:
    """SHA-256 hex digest over the canonical bytes of ``value``.

    Tamper-evidence + fast integrity check (audit-store §2.1 / §4).
    """
    return hashlib.sha256(canon_ser(value)).hexdigest()
