"""C1 ``CorpusLoader`` — the tier-U/S-vs-tier-B dual-source seam (P6 / NFR-QG-LOADER-1).

Supplies profiles to the gates from either the **frozen** ``corpus/profiles.json``
(``from_file`` — the tier-B path, present only after the out-of-band build) **or**
an **in-memory** ``CorpusRecord``/profile list (``from_records`` — the tier-U/S stub
CI uses). Reference-not-own: imports ``corpus_generator.records`` **call-only**;
never generates a corpus, never calls an LLM, and imposes **no** hard Code-Gen
dependency on a committed ``corpus/`` (QG-Fold-1 / BR-QG-6).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from backend.corpus_generator.records import CorpusManifest, CorpusRecord
from backend.intake.schema import ApplicantProfile


class CorpusLoader:
    """Dual-source loader — frozen file or in-memory records (never generates)."""

    @staticmethod
    def from_records(records: Iterable[CorpusRecord]) -> list[CorpusRecord]:
        """The tier-U/S stub path — accept an in-memory ``CorpusRecord`` list."""
        return list(records)

    @staticmethod
    def from_file(path: str | Path) -> list[CorpusRecord]:
        """The tier-B path — deserialize a frozen JSON array of ``CorpusRecord``.

        Decimal-as-string / date-ISO / enum-value all round-trip through the frozen
        ``CorpusRecord`` schema via ``model_validate``.
        """
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return [CorpusRecord.model_validate(row) for row in data]

    @staticmethod
    def profiles(records: Iterable[CorpusRecord]) -> list[ApplicantProfile]:
        """Project the profile stream the gates consume."""
        return [record.profile for record in records]

    @staticmethod
    def manifest_version(manifest: CorpusManifest) -> str:
        """The rulebook version the corpus was labeled against (rule-coverage loads at this)."""
        return manifest.rulebook_version
