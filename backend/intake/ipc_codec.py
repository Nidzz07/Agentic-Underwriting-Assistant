"""IpcCodec — data-only canonical codec for the subprocess parse boundary.

NFR-INT-SEC1-SANDBOX (IPC contract, NFR Design §1). The untrusted-PDF parse
runs in an ephemeral subprocess; only its **extracted data** crosses back to the
parent — never a live object, never a pickle. IpcCodec encodes that data as
canonical UTF-8 JSON with stable key ordering, so:

  * the same PDF -> byte-identical IPC bytes on a single run (no process-hop
    non-determinism), and
  * the parent never executes code from the worker's output (JSON is inert data;
    there is no unsafe deserialization path).

Allowed wire types are the JSON-native primitives only: ``str``, ``int``,
``bool``, ``None``, ``list``, ``dict`` (str keys). ``float`` is excluded
deliberately — monetary values are parsed to ``Decimal`` **in-process after
decode**, not carried across the boundary. Anything else is refused rather than
smuggled through.

Distinct from CANON-SER: IpcCodec canonicalises the *parse-result shape*;
CANON-SER canonicalises the *ApplicantProfile* (with Decimal/date envelopes).
"""
from __future__ import annotations

import json
from typing import Any

_ALLOWED_SCALARS = (str, int, bool, type(None))


class IpcCodecError(ValueError):
    """Raised when a value cannot cross the IPC boundary, or bytes are invalid."""


def _validate_data_only(value: Any) -> None:
    """Reject anything that is not a plain JSON-native data value (no pickle)."""
    # bool is a subclass of int; both are allowed scalars, handled by the tuple.
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return
    if isinstance(value, float):
        raise IpcCodecError("float is not allowed across IPC; parse to Decimal in-process")
    if isinstance(value, list):
        for item in value:
            _validate_data_only(item)
        return
    if isinstance(value, dict):
        for key, val in value.items():
            if not isinstance(key, str):
                raise IpcCodecError(f"IPC dict keys must be str, got {type(key)!r}")
            _validate_data_only(val)
        return
    raise IpcCodecError(f"type {type(value)!r} may not cross the IPC boundary")


class IpcCodec:
    """Stateless canonical data-only codec for the parse-result shape."""

    @staticmethod
    def encode(result: Any) -> bytes:
        _validate_data_only(result)
        text = json.dumps(
            result,
            sort_keys=True,           # stable field ordering
            separators=(",", ":"),    # no incidental whitespace
            ensure_ascii=False,       # explicit UTF-8, stable
            allow_nan=False,
        )
        return text.encode("utf-8")

    @staticmethod
    def decode(data: bytes) -> Any:
        if not isinstance(data, (bytes, bytearray)):
            raise IpcCodecError("IpcCodec.decode expects bytes")
        try:
            return json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IpcCodecError(f"malformed IPC bytes: {exc}") from exc
