"""C8 ``CorpusGenerator`` — DET-1 (2-run byte-identity), LABEL-1 (all records),
FREEZE-1, and the tier-S offline smoke (Fold NFR-1)."""
from __future__ import annotations

from backend.common.canon_ser import canon_ser
from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.generator import CorpusGenerator
from backend.corpus_generator.manifest_builder import determinism_projection
from backend.corpus_generator.skew_audit import SkewAudit
from backend.corpus_generator.tests.conftest import (
    CapturingLLMClient,
    ENGINE_VERSION,
    RULEBOOK_DIR,
    RULEBOOK_VERSION,
)


def _gen_config(**overrides) -> GenerationConfig:
    base = dict(
        seed=42, rulebook_version=RULEBOOK_VERSION, rulebook_dir=RULEBOOK_DIR,
        engine_version=ENGINE_VERSION, model_id="gemini-2.5-flash",
        attempt_budget=10_000, min_profiles=30,
    )
    base.update(overrides)
    return GenerationConfig(**base)


# --- DET-1: two runs, same seed -> byte-identical structured content --------
def test_two_runs_same_seed_are_byte_identical_excluding_prose():
    config = _gen_config()
    out1 = CorpusGenerator(config, llm_client=CapturingLLMClient()).generate(generation_timestamp="t1")
    out2 = CorpusGenerator(config, llm_client=CapturingLLMClient()).generate(generation_timestamp="t2")
    # documents_text excluded from the determinism comparison (Q4 / §6.5)
    assert canon_ser(determinism_projection(out1.records)) == canon_ser(determinism_projection(out2.records))
    # provenance timestamp differs but the content_hash (over records) is identical
    assert out1.manifest.content_hash == out2.manifest.content_hash


# --- LABEL-1: every record's label is the engine's authority ----------------
def test_every_record_label_equals_the_engine_recommendation(oracle):
    config = _gen_config()
    out = CorpusGenerator(config, llm_client=CapturingLLMClient()).generate(generation_timestamp="t")
    for record in out.records:
        assert record.label == oracle.label(record.profile)
        # intended_class is provenance only — the stored label is the authority
        assert record.label == oracle.label(record.profile)


# --- FREEZE-1: single rulebook_version + valid frozen manifest --------------
def test_manifest_pins_single_rulebook_version_and_all_edges():
    config = _gen_config()
    out = CorpusGenerator(config, llm_client=CapturingLLMClient()).generate(generation_timestamp="t")
    assert out.manifest.rulebook_version == RULEBOOK_VERSION
    assert out.manifest.profile_count == len(out.records)
    assert all(present for present in out.manifest.edge_case_checklist.values())  # every DATA-2 edge


def test_records_carry_frozen_document_prose():
    config = _gen_config()
    out = CorpusGenerator(config, llm_client=CapturingLLMClient()).generate(generation_timestamp="t")
    assert all(record.documents_text for record in out.records)   # prose frozen onto each record


# --- tier-S offline smoke (Fold NFR-1) --------------------------------------
class _SpySkewAudit(SkewAudit):
    def __init__(self) -> None:
        self.audited = False

    def audit(self, **kwargs) -> None:
        self.audited = True
        super().audit(**kwargs)


def test_tier_s_smoke_exercises_wiring_and_the_gate(test_scoped_config):
    spy = _SpySkewAudit()
    generator = CorpusGenerator(test_scoped_config, llm_client=CapturingLLMClient(), skew_audit=spy)
    out = generator.smoke()
    # wiring + a valid manifest + the gate INVOKED — never asserts the real 40/35/25 band
    assert spy.audited is True
    assert out.manifest.profile_count == len(out.records) >= test_scoped_config.min_profiles
    assert out.manifest.content_hash
    assert out.manifest.seed == test_scoped_config.seed
