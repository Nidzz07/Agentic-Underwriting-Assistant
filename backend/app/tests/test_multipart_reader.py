"""The streaming multipart reader (WIRE1-Fold-7, stage 4) — ⛔ the hard stage.

⚑ **WHY THIS EXISTS AT ALL.** FastAPI reads the body **before** resolving dependencies
(`routing.py:422` vs `:473`) and starlette imposes **no size limit on file parts**, spooling them
to real disk above 1 MB. Declaring `UploadFile` parameters would therefore mean: an unauthorized
caller's 5 GB upload is fully received and written to a framework-owned temp file **before**
`require_underwriter` ever runs. Q13(b) refuses that by declaring **no body parameter** and
consuming `request.stream()` inside the handler — which only works if the reader below is correct.

⛔ **THE TRADE, DECIDED AT THIS GATE.** The plan reserved the choice between scanning bytes by
hand and driving `python-multipart`'s streaming parser. **Driving the parser is the answer**, and
the reasoning is the same reasoning that made this stage separate: boundary scanning across chunk
edges, CRLF handling, preamble/epilogue, partial-boundary carry-over — these are where a
hand-rolled parser is *"genuinely hard to get right"*, and getting them wrong means accepting
something malformed rather than rejecting it. `python-multipart` is already a declared dependency
and is what starlette itself drives. ⚑ **What we keep is exactly what Q13(b) was for**: the byte
counter and the disk writes stay ours, so the cap is enforced by us, before we write, into a
directory we own. **We delegate parsing; we do not delegate control.**
"""
from __future__ import annotations

import json
from pathlib import Path

import anyio
import pytest

from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from backend.app import multipart_reader as mr
from backend.app.dependencies import (
    Identity,
    get_auth_service,
    get_user_role_repository,
    require_underwriter,
)
from backend.app.errors import WireError, wire_error_handler
from backend.app.tests.conftest import AUDITOR, UNDERWRITER, USERS, seeded_auth_service
from backend.auth_rbac.repository import InMemoryUserRoleRepository
from backend.intake.schema import DocType

BOUNDARY = "----testboundary9f3a"
FORM = {"full_name": "Ada Byron", "city": "Metropolis"}


def build_body(parts, boundary: str = BOUNDARY) -> bytes:
    """A multipart/form-data body. ``parts`` is a list of (name, filename|None, payload)."""
    out = b""
    for name, filename, payload in parts:
        out += f"--{boundary}\r\n".encode()
        disposition = f'Content-Disposition: form-data; name="{name}"'
        if filename is not None:
            disposition += f'; filename="{filename}"'
        out += disposition.encode() + b"\r\n"
        if filename is not None:
            out += b"Content-Type: application/pdf\r\n"
        out += b"\r\n" + payload + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return out


def content_type(boundary: str = BOUNDARY) -> str:
    return f"multipart/form-data; boundary={boundary}"


def stream_of(body: bytes, chunk: int = 64):
    """An async byte stream. ⚑ CHUNKED deliberately — a reader that only works when the whole
    body arrives in one piece is a reader that does not work."""
    async def gen():
        for i in range(0, len(body), chunk):
            yield body[i:i + chunk]
    return gen()


def read(body: bytes, directory: Path, ctype: str | None = None, chunk: int = 64):
    return anyio.run(
        lambda: mr.read_submission_multipart(
            ctype if ctype is not None else content_type(), stream_of(body, chunk), directory
        )
    )


def pdf(size: int = 32) -> bytes:
    return b"%PDF-1.4 " + b"x" * max(size - 9, 0)


@pytest.fixture
def directory(tmp_path) -> Path:
    d = tmp_path / "req-1"
    d.mkdir()
    return d


class TestTheHappyPath:
    """E2–E3."""

    def test_a_well_formed_three_document_upload_yields_three_files(self, directory):
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", pdf()),
            ("bank_statement", "b.pdf", pdf()),
            ("medical_questionnaire", "m.pdf", pdf()),
        ])
        result = read(body, directory)

        assert result.form_fields == FORM
        assert set(result.documents) == set(DocType)
        for path in result.documents.values():
            assert path.parent == directory and path.read_bytes() == pdf()

    def test_each_part_name_maps_to_a_DocType_member(self, directory):
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", pdf()),
        ])
        result = read(body, directory)
        assert list(result.documents) == [DocType.SALARY_SLIP]

    def test_documents_are_OPTIONAL_form_fields_alone_is_valid(self, directory):
        """⚑ A submission may attach any subset, including none — WIRE-1 §5 (Fold-7)."""
        body = build_body([("form_fields", None, json.dumps(FORM).encode())])
        result = read(body, directory)
        assert result.form_fields == FORM and result.documents == {}

    def test_a_body_split_across_MANY_small_chunks_parses_identically(self, directory):
        """⛔ The property a hand-rolled scanner most often gets wrong: a boundary straddling a
        chunk edge. Driving the streaming parser is what buys this, and it is asserted rather
        than assumed."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", pdf(500)),
        ])
        result = read(body, directory, chunk=7)      # boundaries WILL straddle
        assert result.form_fields == FORM
        assert result.documents[DocType.SALARY_SLIP].read_bytes() == pdf(500)


class TestTheAdversarialSet:
    """F1–F6 — ⛔ every one is a case where the safe answer is REJECT, and a hand-rolled parser's
    natural failure is to accept something malformed and carry on."""

    def test_F1_a_malformed_boundary_is_refused(self, directory):
        body = build_body([("form_fields", None, b"{}")], boundary="actual")
        with pytest.raises(mr.MultipartInvalid):
            read(body, directory, ctype=content_type("declared-but-different"))

    def test_F1b_a_missing_boundary_parameter_is_refused(self, directory):
        with pytest.raises(mr.MultipartInvalid):
            read(build_body([("form_fields", None, b"{}")]), directory, ctype="multipart/form-data")

    def test_F1c_a_non_multipart_content_type_is_refused(self, directory):
        with pytest.raises(mr.MultipartInvalid):
            read(b"{}", directory, ctype="application/json")

    def test_F2_a_truncated_stream_is_refused(self, directory):
        """⛔ The dangerous one. A truncated upload that parsed 'successfully' would persist a
        HALF-WRITTEN PDF as though it were complete — and `DOCS-COMPLETE-1` would count it."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", pdf(400)),
        ])
        with pytest.raises(mr.MultipartInvalid):
            read(body[: len(body) - 60], directory)

    def test_F3_a_document_part_with_no_filename_is_refused(self, directory):
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", None, pdf()),
        ])
        with pytest.raises(mr.MultipartInvalid):
            read(body, directory)

    def test_F4_a_LYING_content_length_cannot_defeat_the_counter(self, directory):
        """⛔ **THE ONE THAT PROVES THE CONTROL IS THE COUNTER.** `Content-Length` is a client
        claim; it can understate the real body or be absent entirely. The reader never reads it —
        it counts bytes as they arrive — so a body far larger than any declared length is still
        refused mid-stream."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", pdf(mr.MAX_DOCUMENT_BYTES + 5000)),
        ])
        with pytest.raises(mr.MultipartTooLarge):
            read(body, directory)          # no Content-Length is passed to the reader AT ALL

    def test_F5_zero_parts_is_refused(self, directory):
        with pytest.raises(mr.MultipartInvalid):
            read(f"--{BOUNDARY}--\r\n".encode(), directory)

    def test_F6_an_empty_document_part_is_refused(self, directory):
        """A zero-byte PDF is not a document. Accepting it would let an applicant satisfy
        `DOCS-COMPLETE-1` with nothing at all — except it would not even parse, so it would land
        `unparseable`. Refusing at the boundary is clearer than a downstream mystery."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", b""),
        ])
        with pytest.raises(mr.MultipartInvalid):
            read(body, directory)

    def test_a_missing_form_fields_part_is_refused(self, directory):
        with pytest.raises(mr.MultipartInvalid):
            read(build_body([("salary_slip", "s.pdf", pdf())]), directory)

    def test_a_non_json_form_fields_part_is_refused(self, directory):
        with pytest.raises(mr.MultipartInvalid):
            read(build_body([("form_fields", None, b"not json at all")]), directory)


class TestTheDocumentRules:
    """E4 · G1–G3 — Q6's caps, and where they come from."""

    def test_E4_an_unknown_doc_type_is_refused(self, directory):
        """WIRE-1 §1 (Fold-7): `DocType` is the first CLIENT-asserted enum, so an unrecognised
        value must have a defined outcome — a refusal, **never a silent drop**."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("passport_scan", "p.pdf", pdf()),
        ])
        with pytest.raises(mr.MultipartInvalid):
            read(body, directory)

    def test_G1_a_file_over_the_per_file_cap_is_too_large(self, directory):
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", pdf(mr.MAX_DOCUMENT_BYTES + 1)),
        ])
        with pytest.raises(mr.MultipartTooLarge):
            read(body, directory)

    def test_G3_two_parts_of_the_SAME_doc_type_is_refused_never_last_wins(self, directory):
        """⛔ Q6, explicitly: silently discarding a document an applicant believed they supplied
        is the worst available outcome."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "a.pdf", pdf()),
            ("salary_slip", "b.pdf", pdf()),
        ])
        with pytest.raises(mr.MultipartInvalid):
            read(body, directory)

    def test_G2_a_FOURTH_document_cannot_exist_and_here_is_why(self, directory):
        """⚑ **A FINDING, not a test of new code.** The plan budgeted a separate count cap of
        `len(DocType)`. It is **structurally unreachable**: part names *are* `DocType` values, so
        a fourth document part must be either a **duplicate** (G3) or an **unknown name** (E4) —
        both already refused. The cap is implied by the closed enum, not enforced by a counter.
        Asserted so the reasoning is checked rather than believed."""
        assert mr.MAX_DOCUMENTS == len(DocType) == 3
        four = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "a.pdf", pdf()),
            ("bank_statement", "b.pdf", pdf()),
            ("medical_questionnaire", "c.pdf", pdf()),
            ("salary_slip", "d.pdf", pdf()),
        ])
        with pytest.raises(mr.MultipartInvalid):
            read(four, directory)


class TestNothingOversizedEverReachesDisk:
    """G4 — ⛔ **Q6's central promise, and the only test that can falsify it.**"""

    def test_the_cap_fires_before_the_oversized_bytes_are_written(self, directory):
        """The refusal happens mid-stream, so at most the cap is ever on disk — never the whole
        oversized document. `UploadFile` could not offer this: starlette writes the entire part
        to its own spool file before any handler code exists."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", pdf(mr.MAX_DOCUMENT_BYTES * 3)),
        ])
        with pytest.raises(mr.MultipartTooLarge):
            read(body, directory)

        on_disk = sum(p.stat().st_size for p in directory.rglob("*") if p.is_file())
        assert on_disk <= mr.MAX_DOCUMENT_BYTES, (
            f"{on_disk} bytes reached disk; the cap is {mr.MAX_DOCUMENT_BYTES}"
        )

    def test_the_reader_writes_ONLY_into_the_directory_it_was_given(self, directory):
        """⚑ The temp lifecycle (stage 2) can only delete what lands in its directory. A reader
        that wrote elsewhere — honouring a client-supplied filename, say — would leak past the
        `finally` AND past the sweep."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "../../escape.pdf", pdf()),
        ])
        result = read(body, directory)
        path = result.documents[DocType.SALARY_SLIP]
        assert path.parent == directory, f"the reader wrote outside its directory: {path}"

    def test_the_client_filename_is_NEVER_used_as_the_on_disk_name(self, directory):
        """⛔ A client-controlled filename is a path-traversal primitive. The on-disk name is
        derived from the `DocType` — a closed enum — so the client cannot influence it at all."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "totally_evil name.pdf", pdf()),
        ])
        path = read(body, directory).documents[DocType.SALARY_SLIP]
        assert "evil" not in path.name
        assert path.name.startswith(DocType.SALARY_SLIP.value)


class TestTheCapsAreNamedConstants:
    def test_the_caps_are_named_and_the_count_is_domain_derived(self):
        assert isinstance(mr.MAX_DOCUMENT_BYTES, int) and mr.MAX_DOCUMENT_BYTES > 0
        assert mr.MAX_DOCUMENTS == len(DocType)
        assert mr.MAX_TOTAL_BYTES == mr.MAX_DOCUMENT_BYTES * mr.MAX_DOCUMENTS


class TestAuthResolvesBeforeASingleByteIsRead:
    """E1 — ⛔ **THE PROPERTY FOLD A FOUND DEGRADED AND Q13(b) EXISTS TO RESTORE.**

    ⚑ **Proven here, in stage 4, because this is where the stream-consuming code first exists.**
    Stage 5 wires R10; if the property only held there, it would be discovered rather than
    designed. No route is added — the handler below is mounted on a **test-only** app, so
    ``backend/app/routes/`` is untouched and the route inventory is unchanged.

    ⛔ What makes it structural rather than lucky: the handler declares **no body parameter**, so
    ``routing.py:419`` (``if body_field:``) is false and FastAPI **never touches the body**. The
    only code that reads it is the handler body, which runs strictly after ``solve_dependencies``.
    A wrong-role caller therefore causes **literally zero I/O**.
    """

    def _app(self, reads: list):
        # ⚑ `Request` / `Identity` MUST be resolvable at MODULE scope. This file uses
        # `from __future__ import annotations`, so every annotation is a string that FastAPI
        # resolves via `get_type_hints` against the MODULE namespace — types imported inside this
        # method are invisible to it, and FastAPI then treats `request: Request` as a query
        # parameter and answers 422. Found by running; the symptom looks nothing like the cause.
        app = FastAPI()
        # ⚑ The REAL envelope handler, so a refusal becomes the same 401/403 the production app
        # emits. Without it a WireError would propagate as an unhandled exception and the test
        # would be measuring a crash rather than a refusal.
        app.add_exception_handler(WireError, wire_error_handler)

        @app.post("/probe")
        async def probe(request: Request, _identity: Identity = Depends(require_underwriter)):
            async for chunk in request.stream():
                reads.append(len(chunk))
            return {"read": sum(reads)}

        return app

    def _client(self, app, role: str):
        app.dependency_overrides[get_auth_service] = seeded_auth_service
        app.dependency_overrides[get_user_role_repository] = (
            lambda: InMemoryUserRoleRepository(dict(USERS))
        )
        return TestClient(app)

    def test_a_403_reads_ZERO_bytes_of_the_stream(self):
        """⛔ Not "intake was not called" — **zero bytes read**. That is a strictly stronger claim
        and the only one that closes the resource-exhaustion vector Fold A identified."""
        reads: list[int] = []
        with self._client(self._app(reads), "auditor") as client:
            response = client.post("/probe", content=b"x" * 3_000_000, headers=AUDITOR)

        assert response.status_code == 403
        assert reads == [], f"the server consumed {sum(reads)} bytes before refusing"

    def test_a_401_reads_ZERO_bytes_of_the_stream(self):
        reads: list[int] = []
        with self._client(self._app(reads), "none") as client:
            response = client.post("/probe", content=b"x" * 3_000_000)

        assert response.status_code == 401
        assert reads == []

    def test_an_AUTHORIZED_caller_DOES_reach_the_stream(self):
        """⚑ NON-VACUITY. If the handler never read the stream under any circumstance, both
        assertions above would pass against a route that does nothing at all."""
        reads: list[int] = []
        with self._client(self._app(reads), "underwriter") as client:
            response = client.post("/probe", content=b"x" * 1024, headers=UNDERWRITER)

        assert response.status_code == 200
        assert sum(reads) == 1024


class TestTheContentLengthFastRejectIsAnOptimizationOnly:
    """H1 — ⛔ so nobody later mistakes the fast-reject for the security control."""

    def test_the_reader_never_receives_content_length_at_all(self):
        """The strongest available form of H1: the control **cannot** consult the header, because
        the header is not a parameter of the function. This is a property of the signature, not
        of the implementation, so it cannot regress silently."""
        import inspect

        parameters = set(inspect.signature(mr.read_submission_multipart).parameters)
        assert parameters == {"content_type", "stream", "directory"}
        assert "content_length" not in parameters

    def test_the_counter_refuses_an_oversized_body_with_NO_length_declared(self, directory):
        """⚑ **H1 proper.** There is no middleware in this test and no `Content-Length` anywhere —
        the streaming counter alone refuses. Whatever fast-reject stage 5 adds in front of this is
        an optimization; remove it and the guarantee is unchanged."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", pdf(mr.MAX_DOCUMENT_BYTES + 2048)),
        ])
        with pytest.raises(mr.MultipartTooLarge):
            read(body, directory)

    def test_a_body_UNDER_the_cap_is_accepted_however_it_arrives(self, directory):
        """The other side: the counter is a cap, not a blanket refusal."""
        body = build_body([
            ("form_fields", None, json.dumps(FORM).encode()),
            ("salary_slip", "s.pdf", pdf(mr.MAX_DOCUMENT_BYTES - 1024)),
        ])
        assert read(body, directory, chunk=8192).documents[DocType.SALARY_SLIP].exists()
