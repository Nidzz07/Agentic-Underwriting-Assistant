"""Real subprocess parse-worker entrypoint (pdfplumber).

Runs in an ephemeral, resource-bounded CHILD process: it applies the POSIX
rlimits, parses ONE untrusted PDF with pdfplumber, and writes a canonical,
DATA-ONLY IpcCodec result to stdout (NO pickle). The parent reads and decodes
those bytes. A parse failure/limit-kill exits the child non-zero, which the
parent maps to a deterministic ``unparseable``.

Omitted from coverage (``pyproject.toml``): it executes only inside a subprocess
with a real PDF, exercised via integration rather than in-process import.
"""
from __future__ import annotations

import os
import sys

from backend.intake.ipc_codec import IpcCodec
from backend.intake.resource_limits import apply_resource_limits

_DEFAULT_CPU_SECONDS = 5
_DEFAULT_MEM_BYTES = 256 * 1024 * 1024


def main(argv: list[str]) -> int:
    apply_resource_limits(
        int(os.environ.get("INTAKE_CPU_SECONDS", _DEFAULT_CPU_SECONDS)),
        int(os.environ.get("INTAKE_MEM_BYTES", _DEFAULT_MEM_BYTES)),
    )
    source_path = argv[1]
    import pdfplumber

    texts: list[str] = []
    with pdfplumber.open(source_path) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
    result = {"extracted_text": "\n".join(texts), "structured_fields": {}}
    sys.stdout.buffer.write(IpcCodec.encode(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv))
