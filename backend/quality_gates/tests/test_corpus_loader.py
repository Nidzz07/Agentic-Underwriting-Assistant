"""LOADER-1 (BR-QG-6 / P6) — CI green with ZERO committed corpus/ (from_records stub).

The gates obtain profiles through the injected ``CorpusLoader``; CI runs entirely on
the in-memory stub with no ``corpus/profiles.json`` present. ``from_file`` round-trips
a frozen JSON array only when a tier-B corpus exists.
"""
from __future__ import annotations

import json

from backend.corpus_generator.records import CorpusRecord
from backend.quality_gates.corpus_loader import CorpusLoader


def test_from_records_needs_no_committed_corpus(stub_records) -> None:
    records = CorpusLoader.from_records(stub_records)
    profiles = CorpusLoader.profiles(records)
    assert [p.application_id for p in profiles] == ["stub-0", "stub-1", "stub-2"]


def test_manifest_version_projects_rulebook_version(stub_manifest) -> None:
    assert CorpusLoader.manifest_version(stub_manifest) == "qg-test-0.0.1"


def test_from_file_round_trips_a_frozen_corpus(stub_records, tmp_path) -> None:
    path = tmp_path / "profiles.json"
    path.write_text(json.dumps([r.model_dump(mode="json") for r in stub_records]), encoding="utf-8")
    loaded = CorpusLoader.from_file(path)
    assert len(loaded) == len(stub_records)
    assert all(isinstance(r, CorpusRecord) for r in loaded)
    assert CorpusLoader.profiles(loaded)[0].application_id == "stub-0"
