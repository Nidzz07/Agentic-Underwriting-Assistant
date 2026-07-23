"""C6 ``CoverageWiringGate`` + C7 ``CoverageEvidenceGate`` — AC-5 / QA-6 (P4 + P5).

**Two DISTINCT producers of one ``CoverageGateReport`` shape (ND-QG-Fold-1) — never
conflated:**

- **C6 CoverageWiringGate (COVWIRE-1)** — the collected pytest test cannot read the
  final coverage % mid-session (QG-Fold-3), so its check is a **structural wiring
  meta-assertion**: read ``pyproject.toml`` via stdlib ``tomllib`` and assert
  ``--cov-fail-under`` is **present** and **≥ 90**. It **sets ``passed``**. The
  binding, build-failing enforcement stays ``pyproject``'s ``--cov-fail-under`` —
  C6 only guarantees that gate stays wired.
- **C7 CoverageEvidenceGate (COVEVID-1)** — read a coverage-data artifact and
  extract ``measured_pct`` as **informational** auditor evidence. It does **NOT**
  read ``pyproject`` and does **NOT** set the coverage verdict (``passed`` here
  means only "evidence extracted"). ``measured_pct`` never affects a pass/fail.
"""
from __future__ import annotations

import json
import tomllib
from pathlib import Path

from backend.quality_gates.reports import CoverageGateReport

#: The binding threshold the wiring must meet (AC-5 / QA-6).
COV_FAIL_UNDER_MIN = 90
_COV_FAIL_UNDER_FLAG = "--cov-fail-under"


class CoverageWiringGate:
    """P4 — asserts ``pyproject``'s ``--cov-fail-under`` wiring is present and ≥90."""

    def __init__(self, pyproject_path: str | Path) -> None:
        self._path = Path(pyproject_path)

    def run(self) -> CoverageGateReport:
        data = tomllib.loads(self._path.read_text(encoding="utf-8"))
        addopts = data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("addopts", [])
        fail_under = _extract_fail_under(addopts)
        wiring_present = fail_under is not None
        passed = wiring_present and fail_under >= COV_FAIL_UNDER_MIN
        return CoverageGateReport(
            passed=passed,
            wiring_present=wiring_present,
            fail_under_configured=fail_under,
        )


class CoverageEvidenceGate:
    """P5 — extracts the coverage % as informational evidence (distinct from C6)."""

    def __init__(self, coverage_data_path: str | Path) -> None:
        self._path = Path(coverage_data_path)

    def run(self) -> CoverageGateReport:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        measured_pct = float(data["totals"]["percent_covered"])
        # ``passed`` = "evidence extracted"; the % is informational and NEVER a
        # coverage verdict (that is C6's / pyproject's). wiring fields stay unset.
        return CoverageGateReport(passed=True, measured_pct=measured_pct)


def _extract_fail_under(addopts: list[str]) -> int | None:
    """Parse ONLY the ``--cov-fail-under`` token from the addopts list.

    Orthogonal to the ``--cov=`` path entries (incl. ``--cov=backend/quality_gates``)
    — those are never matched here (CG-QG-Fold-1), so the Step-0 addopts addition and
    this wiring check cannot create a circular/confusing self-reference.
    """
    for opt in addopts:
        if opt.startswith(_COV_FAIL_UNDER_FLAG):
            _, _, value = opt.partition("=")
            if value.strip():
                return int(value.strip())
    return None
