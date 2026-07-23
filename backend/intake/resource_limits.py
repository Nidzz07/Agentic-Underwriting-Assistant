"""POSIX resource-limit application for the parse subprocess (Sharpening 1).

``resource.setrlimit`` is POSIX-only and ABSENT on the Windows dev box. This
module POSIX-GUARDS the import so it never crashes on import, and no-ops cleanly
where ``resource`` is unavailable — there the parent-kill WALL-TIME timeout is
the sole bound. On the Linux deployment target (Render) the kernel-enforced
RLIMIT_CPU (CPU-spin) and RLIMIT_AS (OOM) limits are the second, independent
half of the belt-and-suspenders sandbox.

All termination modes — wall-timeout / RLIMIT_CPU / RLIMIT_AS / crash — converge
to a deterministic ``DocumentEntry.status == unparseable`` in the parent.
"""
from __future__ import annotations

try:
    import resource

    HAS_RESOURCE = True
except ImportError:  # pragma: no cover - platform-dependent (Windows dev)
    resource = None  # type: ignore[assignment]
    HAS_RESOURCE = False


def apply_resource_limits(cpu_seconds: int, mem_bytes: int) -> None:
    """Apply CPU + address-space rlimits in the current (child) process.

    No-op where ``resource`` is unavailable (non-POSIX). MUST be exercised in
    Linux CI so the setrlimit half is actually verified (the ``posix_only``
    tests do this); on Windows dev only the wall-time bound applies.
    """
    if not HAS_RESOURCE:
        return
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
