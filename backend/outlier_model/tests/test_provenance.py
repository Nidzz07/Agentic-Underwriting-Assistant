"""NFR-OUT-PROV-1 — provenance completeness; corpus-relative + label-independent (BR-OUT-4).

Every ``OutlierResult`` carries ``corpus_version`` AND ``seed`` AND ``outlier_model_version`` —
none omitted (by schema); ``seed == CorpusManifest.seed``; provenance carries NO
``rulebook_version`` (the score never reads the corpus label).
"""
from __future__ import annotations

from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.model import OutlierModel
from backend.outlier_model.schemas import OutlierProvenance
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.outlier_model.tests import fixtures as F


def test_every_result_carries_the_full_provenance_triple():
    manifest = F.make_manifest(seed=4242, corpus_version="corpus-test-v1")
    profiles = CorpusSource.profiles(F.corpus_records())
    fitted = OutlierModel.fit(profiles, manifest, ShapExplainer())

    for profile in (F.typical_profile(), F.outlier_profile(), F.missing_optional_profile()):
        prov = fitted.score(profile).provenance
        assert prov.corpus_version == "corpus-test-v1"
        assert prov.seed == manifest.seed
        assert prov.outlier_model_version  # non-empty
        assert prov.outlier_model_version.startswith("outlier-model/")


def test_provenance_has_no_rulebook_version():
    assert "rulebook_version" not in OutlierProvenance.model_fields
    assert set(OutlierProvenance.model_fields) == {
        "corpus_version",
        "seed",
        "outlier_model_version",
    }
