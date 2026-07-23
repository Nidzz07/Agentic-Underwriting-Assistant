"""C7 ``CorpusManifestBuilder`` / ``FreezeAdapter`` — FREEZE-1 + HASH-1."""
from __future__ import annotations

import json
import random

from faker import Faker

from backend.common.canon_ser import canon_ser
from backend.common.canon_ser import content_hash as canon_content_hash
from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.manifest_builder import (
    build_manifest,
    compute_content_hash,
    corpus_to_json,
    determinism_projection,
    manifest_to_json,
    record_projection,
)
from backend.corpus_generator.profile_factory import ProfileFactory
from backend.corpus_generator.records import CorpusRecord
from backend.corpus_generator.tests.conftest import ENGINE_VERSION, RULEBOOK_DIR, RULEBOOK_VERSION
from backend.rules_engine.report_schema import Recommendation


def _config(**overrides) -> GenerationConfig:
    base = dict(
        seed=42, rulebook_version=RULEBOOK_VERSION, rulebook_dir=RULEBOOK_DIR,
        engine_version=ENGINE_VERSION, model_id="gemini-2.5-flash",
        attempt_budget=1000, min_profiles=300,
        required_edge_cases=("age_18", "bmi_30"),
    )
    base.update(overrides)
    return GenerationConfig(**base)


def _records(prose="prose-a"):
    rng = random.Random(1)
    faker = Faker()
    faker.seed_instance(1)
    factory = ProfileFactory(rng, faker, 1)
    p_approve, tags_a = factory.build_edge(0, "age_18")
    p_refer, tags_r = factory.build_edge(1, "bmi_30")
    return [
        CorpusRecord(profile=p_approve, documents_text={"salary_slip": prose},
                     label=Recommendation.APPROVE, intended_class=Recommendation.APPROVE,
                     edge_case_tags=tags_a),
        CorpusRecord(profile=p_refer, documents_text={"salary_slip": prose},
                     label=Recommendation.REFER, intended_class=Recommendation.REFER,
                     edge_case_tags=tags_r),
    ]


# --- HASH-1: delegation to the single shared CANON-SER ----------------------
def test_content_hash_reproduces_via_shared_canon_ser():
    records = _records()
    expected = canon_content_hash([record_projection(r) for r in records])
    assert compute_content_hash(records) == expected
    manifest = build_manifest(records, _config(), generation_timestamp="t0", model_version="m")
    assert manifest.content_hash == expected


def test_mutating_provenance_leaves_the_hash_unchanged():
    records = _records()
    m1 = build_manifest(records, _config(), generation_timestamp="2026-01-01T00:00:00Z", model_version="m")
    m2 = build_manifest(records, _config(), generation_timestamp="2099-12-31T23:59:59Z", model_version="m")
    assert m1.content_hash == m2.content_hash          # provenance excluded (P4)
    assert m1.generation_timestamp != m2.generation_timestamp


def test_mutating_a_content_field_changes_the_hash():
    base = compute_content_hash(_records(prose="prose-a"))
    changed_prose = compute_content_hash(_records(prose="prose-DIFFERENT"))
    assert base != changed_prose                        # content_hash INCLUDES documents_text

    records = _records()
    relabeled = [records[0].model_copy(update={"label": Recommendation.DECLINE_RECOMMEND}), records[1]]
    assert compute_content_hash(relabeled) != base      # label change -> hash changes


# --- DET-1 field-set: determinism EXCLUDES documents_text -------------------
def test_determinism_projection_excludes_documents_text():
    a = determinism_projection(_records(prose="prose-a"))
    b = determinism_projection(_records(prose="prose-COMPLETELY-DIFFERENT"))
    assert canon_ser(a) == canon_ser(b)                 # prose excluded from determinism compare


# --- FREEZE-1: single rulebook_version + manifest shape ---------------------
def test_manifest_records_single_rulebook_version_and_counts():
    records = _records()
    manifest = build_manifest(records, _config(), generation_timestamp="t", model_version="gemini-2.5-flash")
    assert manifest.rulebook_version == RULEBOOK_VERSION
    assert manifest.provider == "gemini"
    assert manifest.profile_count == 2
    assert manifest.class_counts["APPROVE"] == 1
    assert manifest.class_counts["REFER"] == 1
    assert manifest.edge_case_checklist == {"age_18": True, "bmi_30": True}


# --- Q1-A human-readable serialization, decoupled from the hash -------------
def test_corpus_and_manifest_serialize_to_readable_json():
    records = _records()
    manifest = build_manifest(records, _config(), generation_timestamp="t", model_version="m")
    corpus_json = corpus_to_json(records)
    manifest_json = manifest_to_json(manifest)

    parsed = json.loads(corpus_json)
    assert isinstance(parsed, list) and len(parsed) == 2
    assert json.loads(manifest_json)["content_hash"] == manifest.content_hash
    assert "\n" in corpus_json                          # indent=2, human-readable
