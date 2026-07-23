"""TIER-B STAGE 1 — run U13's four BLOCKING quality gates over a frozen corpus (Q10 floor).

⚑ **This path holds NO model.** All four gates are LLM-free by construction — bias-swap,
reproducibility and rule-coverage drive only the deterministic ``RulesEngine``, and the
coverage gate reads ``pyproject.toml``. Running them over a REAL corpus therefore costs
**zero model calls**, which is what makes Q10's floor free once the corpus exists.

**Why this entrypoint had to be written**: U13's gates exist on disk as classes exercised
only by their own unit tests. A repo-wide scan finds **no production caller** — nothing in
the build ever ran them over a corpus. This is that caller.

**Why a SCRIPT, not a pytest test** (ambiguity-check (i)): adding a corpus-presence-skipped
test under ``backend/quality_gates/tests/`` would be flagged by BLOCKING-1 —
``test_blocking_form.py`` forbids ``@skip``/``@xfail`` on its four listed gate modules,
precisely so the gates can never be quietly disabled. A script sidesteps that entirely.

**Blocking form**: any gate reporting ``passed is False`` produces a **non-zero exit**
(the ``run_migrations.py`` fail-loud precedent). Evidence for every gate is written
regardless, so a failing run is still auditable.

⚑ **Manifest loading**: ``CorpusLoader`` supplies ``from_file`` (profiles) and
``manifest_version(manifest)``, but has **no manifest-FILE loader**. This module therefore
parses ``manifest.json`` itself via the frozen ``CorpusManifest.model_validate``. That is
call-only use of a frozen Pydantic model, re-implementing nothing — and this module sits
outside ``backend/quality_gates/``, so QG's REFNOTOWN scan does not apply. Recorded so the
choice is visible rather than incidental.

Run (out of band)::

    python -m backend.scripts.run_quality_gates --corpus corpus --reports corpus/gate-reports
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.corpus_generator.records import CorpusManifest
from backend.quality_gates.bias_swap_suite import BiasSwapGate
from backend.quality_gates.corpus_loader import CorpusLoader
from backend.quality_gates.coverage_gate import CoverageWiringGate
from backend.quality_gates.reproducibility_suite import ReproducibilityGate
from backend.quality_gates.rule_coverage_report import RuleCoverageGate
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader

ENGINE_VERSION = "quality-gates-run-1"

#: repo root: backend/scripts/run_quality_gates.py -> backend -> <root>
_REPO_ROOT = Path(__file__).resolve().parents[2]


#: The repo rulebook directory. ``RulebookLoader`` takes it as a REQUIRED argument — it has
#: no default — so it is named explicitly here, exactly as every other caller in the build
#: does (``corpus_generator/build.py``, ``quality_gates``' and ``rules_engine``'s conftests).
RULEBOOK_DIR = Path(__file__).resolve().parents[1] / "rules_engine" / "rulebook"


def _loader() -> RulebookLoader:
    return RulebookLoader(RULEBOOK_DIR)


def _engine(loader: RulebookLoader) -> RulesEngine:
    return RulesEngine(loader, engine_version=ENGINE_VERSION)


def load_corpus(corpus_dir: Path) -> tuple[list, CorpusManifest]:
    """Read the frozen artifacts. Fails loudly if either is absent."""
    profiles_path = corpus_dir / "profiles.json"
    manifest_path = corpus_dir / "manifest.json"
    if not profiles_path.exists():
        raise FileNotFoundError(f"no frozen corpus at {profiles_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"no corpus manifest at {manifest_path}")

    records = CorpusLoader.from_file(profiles_path)
    manifest = CorpusManifest.model_validate(
        json.loads(manifest_path.read_text(encoding="utf-8"))
    )
    return records, manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the four blocking quality gates over a frozen tier-B corpus."
    )
    parser.add_argument("--corpus", type=str, default="corpus")
    parser.add_argument("--reports", type=str, default="corpus/gate-reports")
    args = parser.parse_args(argv)

    records, manifest = load_corpus(Path(args.corpus))
    profiles = CorpusLoader.profiles(records)
    # QG-Fold-2: the EXACT rulebook version the corpus was labeled against.
    rulebook_version = CorpusLoader.manifest_version(manifest)

    loader = _loader()
    engine = _engine(loader)

    print("=" * 78)
    print("TIER-B STAGE 1 -- FOUR BLOCKING QUALITY GATES (zero model calls)")
    print(f"  corpus          : {args.corpus}  ({len(profiles)} profiles)")
    print(f"  rulebook_version: {rulebook_version}  (from the manifest)")
    print(f"  content_hash    : {manifest.content_hash}")
    print("=" * 78)

    results = [
        ("bias-swap", BiasSwapGate(engine).run(profiles, rulebook_version)),
        ("reproducibility", ReproducibilityGate(engine).run(profiles, rulebook_version)),
        ("rule-coverage", RuleCoverageGate(engine, loader).run(profiles, rulebook_version)),
        ("coverage-wiring", CoverageWiringGate(_REPO_ROOT / "pyproject.toml").run()),
    ]

    reports_dir = Path(args.reports)
    reports_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()

    failed: list[str] = []
    for name, report in results:
        (reports_dir / f"{name}.json").write_text(
            report.to_json(generated_at=generated_at), encoding="utf-8"
        )
        status = "PASS" if report.passed else "FAIL"
        print(f"  [{status}] {name}")
        if not report.passed:
            failed.append(name)

    print(f"\nevidence written to {reports_dir}/")
    if failed:
        # FAIL-LOUD: a failing blocking gate must be a non-zero exit, never a warning.
        print(f"\nBLOCKING GATE FAILURE: {', '.join(failed)}")
        return 1
    # ⚑ Deliberately says "frozen corpus", never "real corpus": these gates read ONLY
    # `record.profile` and never `documents_text`, so they attest to the DECISION PATH over
    # the corpus's profiles — NOT to document or memo quality, and not to the prose being
    # model-authored. Overstating that here would let a passing run be misread.
    print("\nAll four blocking gates PASSED over the frozen corpus.")
    print("  scope: the DECISION path over the corpus profiles.")
    print("  NOT a claim about document prose or memo quality (no gate reads documents_text).")
    return 0


if __name__ == "__main__":  # pragma: no cover - out-of-band entrypoint
    raise SystemExit(main())
