"""SubprocessParseWorker — the parent side of the sandboxed parse (NFR §1).

Each untrusted PDF is parsed in a FRESH, ephemeral, resource-bounded, killable
subprocess. Only DATA crosses back, via IpcCodec (no pickle). The sandbox is
belt-and-suspenders (Sharpening 1):

  * parent-kill WALL-TIME timeout   -> catches a hung/blocked/low-CPU parse
    (runs on every platform), and
  * child-side setrlimit CPU + AS   -> catches CPU-spin / OOM at the kernel
    level on POSIX (Linux/Render, verified by the posix_only tests in CI).

ALL termination modes — timeout / RLIMIT_CPU / RLIMIT_AS / crash / undecodable
output — converge to a deterministic ``DocumentEntry.status == unparseable``.
The subprocess runs once at intake, upstream of persistence, and is OUTSIDE the
replay path (replay never re-parses).
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from backend.intake.ipc_codec import IpcCodec, IpcCodecError
from backend.intake.schema import DocStatus, DocType, DocumentEntry

# Repo root = the directory that CONTAINS the ``backend`` package
# (.../backend/intake/parser.py -> parents[2]). The worker is spawned with this
# as cwd + on PYTHONPATH so ``python -m backend.intake...`` resolves regardless
# of the caller's working directory (the app / pytest may run from anywhere).
_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ParseOutcome:
    """A per-document parse result: the manifest entry + the extracted payload
    (empty when unparseable)."""

    entry: DocumentEntry
    payload: dict = field(default_factory=dict)


class SubprocessParseWorker:
    DEFAULT_TIMEOUT_S = 5.0
    DEFAULT_CPU_SECONDS = 5
    DEFAULT_MEM_BYTES = 256 * 1024 * 1024

    def __init__(
        self,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        cpu_seconds: int = DEFAULT_CPU_SECONDS,
        mem_bytes: int = DEFAULT_MEM_BYTES,
        worker_cmd: list[str] | None = None,
        cwd: str | None = None,
    ) -> None:
        self._timeout_s = timeout_s
        self._cpu_seconds = cpu_seconds
        self._mem_bytes = mem_bytes
        self._worker_cmd = worker_cmd or [sys.executable, "-m", "backend.intake.parse_worker"]
        # The subprocess runs with the repo root as cwd so the worker module
        # resolves independently of where the parent process was launched.
        self._cwd = cwd or str(_REPO_ROOT)

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["INTAKE_CPU_SECONDS"] = str(self._cpu_seconds)
        env["INTAKE_MEM_BYTES"] = str(self._mem_bytes)
        # Ensure the child can import the ``backend`` package even if cwd-based
        # resolution is unavailable (belt-and-suspenders with the cwd above).
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(_REPO_ROOT) + (os.pathsep + existing if existing else "")
        return env

    def parse(self, doc_type: DocType, source_path: str) -> ParseOutcome:
        """Parse one document in an isolated subprocess. Never raises: any
        failure mode returns an ``unparseable`` outcome."""
        # Resolve to an absolute path against the CALLER's cwd before the
        # subprocess (which runs in the repo root) changes relative semantics.
        cmd = [*self._worker_cmd, os.path.abspath(str(source_path))]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self._timeout_s,
                env=self._env(),
                cwd=self._cwd,
            )
        except subprocess.TimeoutExpired:
            return self._unparseable(doc_type)  # wall-time parent-kill
        except OSError:  # pragma: no cover - spawn failure is environment-specific
            return self._unparseable(doc_type)

        if proc.returncode != 0:
            # crash / RLIMIT_CPU (SIGXCPU) / RLIMIT_AS (MemoryError) -> non-zero
            return self._unparseable(doc_type)

        try:
            payload = IpcCodec.decode(proc.stdout)
        except IpcCodecError:
            return self._unparseable(doc_type)

        if not isinstance(payload, Mapping):
            return self._unparseable(doc_type)

        content_hash = hashlib.sha256(IpcCodec.encode(payload)).hexdigest()
        return ParseOutcome(
            entry=DocumentEntry(doc_type=doc_type, status=DocStatus.PARSED, content_hash=content_hash),
            payload=dict(payload),
        )

    @staticmethod
    def _unparseable(doc_type: DocType) -> ParseOutcome:
        return ParseOutcome(
            entry=DocumentEntry(doc_type=doc_type, status=DocStatus.UNPARSEABLE, content_hash=""),
            payload={},
        )
