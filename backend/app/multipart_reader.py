"""Streaming multipart reader for R10's document upload (WIRE1-Fold-7, stage 4).

⛔ **WHY A READER EXISTS INSTEAD OF ``UploadFile`` PARAMETERS.** Measured against the installed
runtime: FastAPI reads the request body at ``routing.py:422`` and solves dependencies at ``:473``
— **body first**. And starlette caps **non-file** parts only (``formparsers.py:181-188``), so file
parts stream **unbounded** into a ``SpooledTemporaryFile`` that rolls to real disk above 1 MB.
Declaring ``UploadFile`` parameters would therefore mean an unauthorized caller's arbitrarily
large upload is **fully received and written to a framework-owned temp file before
``require_underwriter`` runs**. Q13(b) refuses that: the handler declares **no body parameter**,
so the framework never touches the body, and this module consumes ``request.stream()`` after
authorization has already passed.

⚑ **DELEGATED PARSING, RETAINED CONTROL — the trade decided at the stage-4 gate.** Boundary
scanning across chunk edges, CRLF handling, preamble/epilogue and partial-boundary carry-over are
where a hand-rolled parser is *"genuinely hard to get right"*, and its natural failure is to
**accept** something malformed. ``python-multipart`` is already a declared dependency and is what
starlette itself drives, so this module drives it too — while keeping **the byte counter and every
disk write here**. We delegate parsing; we do not delegate control.

**Three properties this module owes the contract** (WIRE-1 §4/§5, Fold-7):

1. ⛔ **The cap is a STREAMING BYTE COUNTER, never ``Content-Length``.** This module never reads
   that header — it does not even receive it. A client may understate or omit it; the counter
   refuses mid-stream regardless, so at most the cap is ever written.
2. ⛔ **Every byte lands in the caller's directory, under a name derived from the closed
   ``DocType`` enum.** The client-supplied filename is **never** used on disk — it is a
   path-traversal primitive.
3. ⛔ **Reject, never silently drop.** An unknown ``doc_type``, a duplicate, a missing filename, a
   truncated stream and an empty part are all refusals. Discarding a document an applicant
   believed they supplied is the worst available outcome.

**No LLM. No credentials.** Applicant bytes pass through and are written; nothing about them is
logged, and no error raised here carries a filesystem path.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import AsyncIterator

# ⚑ Resolved the way starlette resolves it: the distribution renamed its import package from
# ``multipart`` to ``python_multipart``, and both spellings exist in the wild. Preferring the
# new name with a fallback keeps this working across the version range ``requirements.txt``
# permits (``python-multipart>=0.0.12``).
try:  # pragma: no cover - exercised by whichever spelling the installed version provides
    from python_multipart.multipart import MultipartParser, parse_options_header
except ImportError:  # pragma: no cover
    from multipart.multipart import MultipartParser, parse_options_header

from backend.app.upload_storage import document_path, open_document
from backend.intake.schema import DocType

#: The part carrying the same JSON object R10's ``application/json`` body carries.
FORM_FIELDS_PART = "form_fields"

#: ⛔ The per-document byte cap. Enforced by the counter below **before** each chunk is written,
#: so a document on disk can never exceed it.
MAX_DOCUMENT_BYTES: int = 5 * 1024 * 1024

#: ⚑ **DERIVED FROM THE DOMAIN, not chosen.** ``DocType`` is a closed enum of exactly the three
#: documents ``IntakeGate._EXPECTED_DOCS`` looks for.
#:
#: ⚑ **It is not separately enforced, and that is correct**: part names *are* ``DocType`` values,
#: so a fourth document part is necessarily either a **duplicate** or an **unknown name**, both
#: refused below. A counter here would be unreachable code. Asserted in the tests so the
#: reasoning is checked rather than believed.
MAX_DOCUMENTS: int = len(DocType)

#: The total-body ceiling — a backstop for many parts each individually under the cap.
MAX_TOTAL_BYTES: int = MAX_DOCUMENT_BYTES * MAX_DOCUMENTS

_DOC_TYPES = {member.value: member for member in DocType}


class MultipartInvalid(Exception):
    """The upload is malformed or breaks a document rule -> WIRE-1 §4 **400** ``invalid_request``."""


class MultipartTooLarge(Exception):
    """The upload exceeds a size cap -> WIRE-1 §4 **413** ``payload_too_large``."""


@dataclass
class SubmissionUpload:
    """What the handler needs: the parsed form fields and one path per supplied document."""

    form_fields: dict = field(default_factory=dict)
    documents: dict[DocType, Path] = field(default_factory=dict)


class _PartCollector:
    """Callbacks for ``multipart.MultipartParser``.

    ⚑ Header bytes arrive in fragments and part data arrives in chunks, so everything here
    accumulates incrementally — which is exactly why the byte cap can be applied *per chunk*
    rather than after the fact.
    """

    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self.result = SubmissionUpload()
        self._saw_form_fields = False
        self._ended = False
        self._total = 0
        self._parts = 0
        self._reset_part()

    def _reset_part(self) -> None:
        self._header_field = b""
        self._header_value = b""
        self._headers: dict[bytes, bytes] = {}
        self._name: str | None = None
        self._filename: str | None = None
        self._doc_type: DocType | None = None
        self._handle = None
        self._opener = None
        self._written = 0
        self._field_bytes = b""

    # -- header assembly --------------------------------------------------------------
    def on_part_begin(self) -> None:
        self._reset_part()
        self._parts += 1

    def on_header_field(self, data: bytes, start: int, end: int) -> None:
        self._header_field += data[start:end]

    def on_header_value(self, data: bytes, start: int, end: int) -> None:
        self._header_value += data[start:end]

    def on_header_end(self) -> None:
        self._headers[self._header_field.lower()] = self._header_value
        self._header_field = b""
        self._header_value = b""

    def on_headers_finished(self) -> None:
        disposition = self._headers.get(b"content-disposition", b"")
        self._name = _option(disposition, b"name")
        self._filename = _option(disposition, b"filename")

        if self._name is None:
            raise MultipartInvalid("a part carried no name")

        if self._name == FORM_FIELDS_PART:
            if self._saw_form_fields:
                raise MultipartInvalid("form_fields was supplied more than once")
            self._saw_form_fields = True
            return

        doc_type = _DOC_TYPES.get(self._name)
        if doc_type is None:
            # ⛔ WIRE-1 §1 (Fold-7): DocType is client-asserted, so an unrecognised value must
            # have a defined outcome. Never a silent drop.
            raise MultipartInvalid("unrecognised document part")
        if doc_type in self.result.documents:
            raise MultipartInvalid("the same document was supplied more than once")
        if self._filename is None:
            raise MultipartInvalid("a document part carried no filename")

        self._doc_type = doc_type
        # ⛔ THE WRITE IS DELEGATED. ``upload_storage`` owns every byte this application puts on
        # disk and derives the on-disk name from the closed ``DocType`` enum — so the client's
        # filename, a path-traversal primitive, is never consulted. This module counts and
        # streams; it does not decide where anything lands.
        self._opener = open_document(self._directory, doc_type)
        self._handle = self._opener.__enter__()
        self.result.documents[doc_type] = document_path(self._directory, doc_type)

    # -- body ------------------------------------------------------------------------
    def on_part_data(self, data: bytes, start: int, end: int) -> None:
        chunk = data[start:end]
        self._total += len(chunk)
        if self._total > MAX_TOTAL_BYTES:
            raise MultipartTooLarge("the upload exceeds the total size cap")

        if self._doc_type is None:
            self._field_bytes += chunk
            return

        # ⛔ CHECKED BEFORE THE WRITE. This is the whole promise: at most the cap ever
        # reaches disk, and the refusal happens mid-stream so the rest is never received.
        if self._written + len(chunk) > MAX_DOCUMENT_BYTES:
            raise MultipartTooLarge("a document exceeds the per-file size cap")
        self._handle.write(chunk)
        self._written += len(chunk)

    def on_part_end(self) -> None:
        if self._doc_type is not None:
            self._opener.__exit__(None, None, None)
            self._handle = None
            if self._written == 0:
                raise MultipartInvalid("a document part was empty")
            return
        if self._name == FORM_FIELDS_PART:
            try:
                parsed = json.loads(self._field_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise MultipartInvalid("form_fields was not valid JSON") from None
            if not isinstance(parsed, dict):
                raise MultipartInvalid("form_fields must be a JSON object")
            self.result.form_fields = parsed

    def on_end(self) -> None:
        # ⛔ Fires ONLY on the terminating ``--boundary--``. A stream that stops short never
        # reaches here, which is the only reliable signal that the upload was TRUNCATED — the
        # parser itself does not raise on an incomplete body, it simply stops.
        self._ended = True

    @property
    def ended(self) -> bool:
        """True only if the terminating boundary was seen — i.e. the body was complete."""
        return self._ended

    @property
    def saw_form_fields(self) -> bool:
        return self._saw_form_fields

    def close(self) -> None:
        if self._handle is not None:
            self._opener.__exit__(None, None, None)
            self._handle = None


def _option(header: bytes, key: bytes) -> str | None:
    """Pull ``key="value"`` out of a Content-Disposition header."""
    _, options = parse_options_header(header)
    raw = options.get(key)
    return None if raw is None else raw.decode("utf-8", "replace")


def _boundary(content_type: str) -> bytes:
    kind, options = parse_options_header(content_type)
    if kind.lower() != b"multipart/form-data":
        raise MultipartInvalid("the request is not multipart/form-data")
    boundary = options.get(b"boundary")
    if not boundary:
        raise MultipartInvalid("the multipart boundary is missing")
    return boundary


async def read_submission_multipart(
    content_type: str, stream: AsyncIterator[bytes], directory: Path
) -> SubmissionUpload:
    """Consume ``stream`` into ``directory``, enforcing every cap and rule as bytes arrive.

    ⛔ **``Content-Length`` IS NOT A PARAMETER OF THIS FUNCTION.** It cannot be — the control is
    the counter, and a client's declared length is a claim, not a fact. Any middleware that
    rejects early on that header is an optimization sitting in front of this, never the control.

    Raises :class:`MultipartInvalid` (-> 400) or :class:`MultipartTooLarge` (-> 413). ⚑ Partial
    files left by a refusal are removed by the caller's ``upload_temp_dir`` ``finally``; nothing
    here needs to unwind, and nothing here raises with a filesystem path in its message.
    """
    collector = _PartCollector(directory)
    parser = MultipartParser(_boundary(content_type), _callbacks(collector))
    try:
        async for chunk in stream:
            parser.write(chunk)
        parser.finalize()
    except (MultipartInvalid, MultipartTooLarge):
        raise
    except Exception as exc:                     # a parser error on a malformed body
        raise MultipartInvalid("the upload could not be parsed") from exc
    finally:
        collector.close()

    if not collector.ended:
        # ⛔ THE DANGEROUS ONE. A truncated upload that parsed "successfully" would persist a
        # HALF-WRITTEN PDF as though it were complete — and ``DOCS-COMPLETE-1`` would count it.
        # The parser does not raise here; it just stops, so this check is the whole defence.
        raise MultipartInvalid("the upload ended before its final boundary")
    if not collector.saw_form_fields:
        raise MultipartInvalid("the form_fields part is required")
    return collector.result


def _callbacks(collector: _PartCollector) -> dict:
    return {
        "on_part_begin": collector.on_part_begin,
        "on_part_data": collector.on_part_data,
        "on_part_end": collector.on_part_end,
        "on_header_field": collector.on_header_field,
        "on_header_value": collector.on_header_value,
        "on_header_end": collector.on_header_end,
        "on_headers_finished": collector.on_headers_finished,
        "on_end": collector.on_end,
    }
