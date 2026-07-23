"""Tests for IpcCodec (Step 2) — the subprocess-boundary codec.

Maps: NFR-INT-SEC1-SANDBOX (IPC). The parse worker runs in an ephemeral
subprocess and writes its result to stdout via IpcCodec; the parent reads and
decodes those bytes. IpcCodec is DATA-ONLY, fixed-schema, stable-ordered,
explicit-UTF-8, and **NO pickle** — so a hostile parse result cannot execute
code in the parent (no unsafe deserialization) and the same PDF yields
byte-identical IPC bytes on a single run.

IpcCodec is its OWN canonical encoder for the parse-result *shape* — distinct
from CANON-SER (which is the ApplicantProfile spec). Parse results carry only
extracted text + structured primitives (str/int/bool/None/list/dict); money is
parsed to Decimal in-process AFTER decode, never across the boundary.
"""
from __future__ import annotations

import pickle

import pytest

from backend.intake.ipc_codec import IpcCodec, IpcCodecError


def _sample_result():
    return {
        "documents": [
            {
                "doc_type": "salary_slip",
                "status": "parsed",
                "content_hash": "abc123",
                "extracted_text": "Net pay 50000",
                "structured_fields": {"net_pay": "50000", "period": "2026-05"},
            },
            {
                "doc_type": "bank_statement",
                "status": "unparseable",
                "content_hash": "",
                "extracted_text": "",
                "structured_fields": {},
            },
        ],
        "form_fields": {"requested_cover_amount": "1000000"},
    }


def test_round_trip_equal():
    result = _sample_result()
    assert IpcCodec.decode(IpcCodec.encode(result)) == result


def test_encoding_is_byte_identical_for_same_input():
    a = IpcCodec.encode(_sample_result())
    b = IpcCodec.encode(_sample_result())
    assert a == b


def test_encoding_stable_under_key_insertion_order():
    r1 = {"b": 1, "a": 2, "nested": {"y": 1, "x": 2}}
    r2 = {"a": 2, "b": 1, "nested": {"x": 2, "y": 1}}
    assert IpcCodec.encode(r1) == IpcCodec.encode(r2)


def test_wire_format_is_utf8_json_not_pickle():
    payload = {"extracted_text": "unit-café-Ω"}  # non-ASCII round-trips as UTF-8
    wire = IpcCodec.encode(payload)
    assert isinstance(wire, bytes)
    # It is valid UTF-8 JSON...
    assert wire.decode("utf-8").startswith("{")
    assert IpcCodec.decode(wire)["extracted_text"] == "unit-café-Ω"
    # ...and it is NOT a pickle stream (pickle cannot load canonical JSON bytes).
    with pytest.raises(Exception):
        pickle.loads(wire)


def test_encode_rejects_non_data_types_no_pickle_of_objects():
    # Defense: only plain data crosses the boundary. Arbitrary objects, bytes,
    # and floats are refused rather than smuggled through (no pickle fallback).
    class Evil:
        pass

    with pytest.raises(IpcCodecError):
        IpcCodec.encode({"x": Evil()})
    with pytest.raises(IpcCodecError):
        IpcCodec.encode({"x": b"raw-bytes"})
    with pytest.raises(IpcCodecError):
        IpcCodec.encode({"x": 1.5})  # float excluded — data-only primitives


def test_encode_rejects_non_string_keys():
    with pytest.raises(IpcCodecError):
        IpcCodec.encode({1: "value"})


def test_decode_rejects_malformed_bytes():
    with pytest.raises(IpcCodecError):
        IpcCodec.decode(b"\x80\x03not-json")
    with pytest.raises(IpcCodecError):
        IpcCodec.decode("not-bytes")  # type: ignore[arg-type]
