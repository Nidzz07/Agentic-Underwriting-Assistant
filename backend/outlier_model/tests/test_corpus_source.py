"""NFR-OUT-CORPUS-1 — dual-source seam; tier-B independence (BR-OUT-8).

``from_records`` (default) and ``from_file`` (tier-B) yield the same downstream ``profile``
shape; the unit builds + tests fully on the in-memory fixture with no ``corpus/`` present
(``from_file`` is exercised only against a temp file the test itself writes).
"""
from __future__ import annotations

import json

from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.tests import fixtures as F


def test_from_records_returns_the_record_list():
    records = F.corpus_records()
    assert CorpusSource.from_records(records) == records


def test_from_records_and_from_file_yield_the_same_profile_shape(tmp_path):
    records = F.corpus_records()
    # from_file round-trips a frozen JSON array of CorpusRecord (Decimal-as-string etc.)
    corpus_json = tmp_path / "profiles.json"
    corpus_json.write_text(
        json.dumps([r.model_dump(mode="json") for r in records]), encoding="utf-8"
    )

    from_records = CorpusSource.profiles(CorpusSource.from_records(records))
    from_file = CorpusSource.profiles(CorpusSource.from_file(corpus_json))

    assert [p.model_dump(mode="json") for p in from_records] == [
        p.model_dump(mode="json") for p in from_file
    ]


def test_default_path_needs_no_corpus_file(tmp_path):
    # tier-B independence: the default (from_records) path works with an empty dir — no corpus/.
    assert not list(tmp_path.iterdir())
    profiles = CorpusSource.profiles(CorpusSource.from_records(F.corpus_records()))
    assert len(profiles) == 12


def test_corpus_version_reads_the_manifest():
    manifest = F.make_manifest(corpus_version="corpus-abc")
    assert CorpusSource.corpus_version(manifest) == "corpus-abc"
