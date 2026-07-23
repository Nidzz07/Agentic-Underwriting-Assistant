"""Fake parse-worker for SubprocessParseWorker tests (Step 9).

Simulates each subprocess failure mode so the parent's mapping to a
deterministic ``unparseable`` can be verified without real malicious PDFs.
Applies the SAME resource limits as the real worker so the POSIX RLIMIT tests
exercise the genuine setrlimit path. Invoked as
``python -m backend.intake.tests.fake_worker <mode> <source_path>``.

Under ``tests/`` -> omitted from coverage.
"""
from __future__ import annotations

import os
import sys
import time

from backend.intake.resource_limits import apply_resource_limits


def main() -> None:
    apply_resource_limits(
        int(os.environ.get("INTAKE_CPU_SECONDS", 5)),
        int(os.environ.get("INTAKE_MEM_BYTES", 256 * 1024 * 1024)),
    )
    mode = sys.argv[1] if len(sys.argv) > 1 else "ok"

    if mode == "hang":
        time.sleep(60)  # -> parent wall-time timeout kills us
    elif mode == "crash":
        sys.exit(3)  # -> non-zero exit
    elif mode == "spin":
        while True:  # -> RLIMIT_CPU (SIGXCPU) on POSIX
            pass
    elif mode == "alloc":
        blob = bytearray()
        chunk = b"x" * (10 * 1024 * 1024)
        while True:  # -> RLIMIT_AS (MemoryError) on POSIX
            blob += chunk
    elif mode == "garbage":
        sys.stdout.buffer.write(b"\x00\x01 not ipc bytes")  # -> decode error
    elif mode == "notdict":
        from backend.intake.ipc_codec import IpcCodec

        sys.stdout.buffer.write(IpcCodec.encode([1, 2, 3]))  # valid IPC, but not a mapping
    else:  # "ok"
        from backend.intake.ipc_codec import IpcCodec

        result = {
            "extracted_text": "synthetic salary slip net pay 50000",
            "structured_fields": {"net_pay": "50000"},
        }
        sys.stdout.buffer.write(IpcCodec.encode(result))


if __name__ == "__main__":
    main()
