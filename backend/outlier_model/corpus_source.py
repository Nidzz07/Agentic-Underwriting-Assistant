"""C-OUT-2 ``CorpusSource`` — the read-only dual-source corpus seam (U18 / P-OUT-6, BR-OUT-8).

Read-only dual-source seam supplying the corpus to ``outlier-model`` from either an
**in-memory** ``CorpusRecord`` list (``from_records`` — the tier-U/S default CI path) or a
**frozen** ``corpus/…json`` file (``from_file`` — the tier-B path, NOT required for build or
test; the unit builds + unit-tests fully on in-memory fixtures with no ``corpus/`` present).

Reference-not-own: this **MIRRORS — never imports —** ``quality_gates/corpus_loader.py``
(U18 has no edge to ``quality_gates`` — Q4-C rejected); it imports ``corpus_generator.records``
**call-only**. It never triggers a corpus build, never calls an LLM, and imposes no hard
``corpus/`` dependency (BR-OUT-8 / NFR-OUT-CORPUS-1). Deterministic I/O — no RNG, no seed
(CG-ND-OUT-Fold-3).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from backend.corpus_generator.records import CorpusManifest, CorpusRecord
from backend.intake.schema import ApplicantProfile


class CorpusSource:
    """Dual-source corpus reader — in-memory records or a frozen file (never generates)."""

    @staticmethod
    def from_records(records: Iterable[CorpusRecord]) -> list[CorpusRecord]:
        """The tier-U/S path — accept an in-memory ``CorpusRecord`` list (the default)."""
        return list(records)

    @staticmethod
    def from_file(path: str | Path) -> list[CorpusRecord]:
        """The tier-B path — deserialize a frozen JSON array of ``CorpusRecord``.

        Never invoked/required by the default (tier-U) test path — its presence is the
        dual-source seam, not a build dependency.
        """
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return [CorpusRecord.model_validate(row) for row in data]

    @staticmethod
    def profiles(records: Iterable[CorpusRecord]) -> list[ApplicantProfile]:
        """Project the ``profile`` stream the model consumes (the ``label`` is unused)."""
        return [record.profile for record in records]

    @staticmethod
    def corpus_version(manifest: CorpusManifest) -> str:
        """The corpus-selection key + provenance anchor (the score is corpus-relative)."""
        return manifest.corpus_version
