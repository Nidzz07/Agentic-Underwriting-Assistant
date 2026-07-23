"""Active zero-real-PII guard (NFR-INT-DATA4 / DATA-4).

An ENFORCED build/test check — not a policy note. It scans fixtures and
committed data artifacts for real-PII-SHAPED patterns (SSN, PAN, Aadhaar, credit
card, email, E.164 phone) and FAILS (non-zero exit / non-empty findings) if any
appear. All of this unit's fixtures are synthetic (curated corpora C/L + seeded
Faker profiles), so a clean run is the invariant.

Test SOURCE files (``test_*.py``) are skipped: they legitimately carry
PII-shaped positive-case vectors to prove the guard is active. This module skips
itself for the same reason.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

_PII_PATTERNS: dict[str, re.Pattern] = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "pan": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    "aadhaar": re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone_e164": re.compile(r"\+\d{10,15}\b"),
}

_SCANNABLE_SUFFIXES = {".py", ".json", ".txt", ".csv", ".md"}
_SKIP_NAMES = {"pii_guard.py"}


@dataclass(frozen=True)
class Finding:
    source: str
    line: int
    pattern: str
    match: str


def scan_text(text: str, source: str = "<text>") -> list[Finding]:
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for name, pattern in _PII_PATTERNS.items():
            for m in pattern.finditer(line):
                findings.append(Finding(source=source, line=lineno, pattern=name, match=m.group()))
    return findings


def _iter_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def scan_for_real_pii(roots: Iterable[str | Path]) -> list[Finding]:
    findings: list[Finding] = []
    for root in roots:
        for path in _iter_files(Path(root)):
            if path.name.startswith("test_") or path.name in _SKIP_NAMES:
                continue
            if "__pycache__" in path.parts or path.suffix not in _SCANNABLE_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):  # pragma: no cover - unreadable file
                continue
            findings.extend(scan_text(text, str(path)))
    return findings


def main(argv: list[str]) -> int:
    roots = argv[1:] or ["backend"]
    findings = scan_for_real_pii(roots)
    for f in findings:
        print(f"REAL-PII-SHAPED [{f.pattern}] {f.source}:{f.line}: {f.match}")
    if findings:
        print(f"FAIL: {len(findings)} real-PII-shaped finding(s) (DATA-4).")
        return 1
    print("OK: no real-PII-shaped patterns (DATA-4).")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv))
