"""A genuinely parseable minimal PDF (DATA-4: synthetic only, never real PII).

⚑ **Why build one rather than commit a file.** Committing a binary fixture would put an opaque
blob in the repository that `pii_guard`'s scanner cannot read and no reviewer can diff. This is
602 bytes of legible PDF structure, generated deterministically, and **pdfplumber really does
extract text from it** — asserted in `test_submission_documents.py`, so the fixture cannot silently
rot into something unparseable and make a test pass for the wrong reason.
"""
from __future__ import annotations


def minimal_pdf(text: str = "Gross monthly salary 100000") -> bytes:
    """A one-page PDF whose only content is ``text``. Structurally valid, xref included."""
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n".encode()
        + b"%%EOF\n"
    )
    return bytes(out)


def corrupt_pdf() -> bytes:
    """Bytes that claim to be a PDF and are not — the ``unparseable`` path."""
    return b"%PDF-1.4\nthis is not a pdf at all\n%%EOF\n"
