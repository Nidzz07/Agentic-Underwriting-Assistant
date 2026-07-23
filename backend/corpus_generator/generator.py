"""C8 ``CorpusGenerator`` — the seeded build orchestrator (DET-1 + composition).

Drives the seeded build:
    construct (C2) -> derive -> label (C3) -> bounded-sample (C4) -> skew-audit gate
    (C5) -> prose (C6) -> freeze/manifest (C7).

Determinism (BR-CORP-1 / DET-1): ONE ``random.Random(seed)`` + a ``Faker`` seeded
from the same seed are the sole entropy source; no wall-clock and no unseeded
randomness. ``generation_timestamp`` is **injected** (recorded provenance), never
read from the clock inside the generation path — mirroring rules-engine's injected
``engine_version``.

The LLM client is **injected** (a capturing double drives it offline in CI; the
real google-genai client is wired only at the tier-B ``build.py`` entrypoint). The
tier-S smoke entrypoint (``smoke``) runs the full pipeline on a test-scoped config
(Fold NFR-1) — wiring + a valid manifest + the gate invoked, never the real band.
"""
from __future__ import annotations

import random
from typing import NamedTuple, Optional

from faker import Faker

from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.document_text_generator import DocumentTextGenerator
from backend.corpus_generator.labeling_oracle import LabelingOracle
from backend.corpus_generator.manifest_builder import build_manifest
from backend.corpus_generator.records import CorpusManifest, CorpusRecord
from backend.corpus_generator.rejection_sampler import RejectionSampler
from backend.corpus_generator.profile_factory import ProfileFactory
from backend.corpus_generator.skew_audit import SkewAudit
from backend.memo_agent_core.provider import LLMClient


class CorpusOutput(NamedTuple):
    """The in-memory generated corpus (frozen to disk only by the tier-B ``build.py``)."""

    records: list[CorpusRecord]
    manifest: CorpusManifest


class CorpusGenerator:
    """Composes C1–C7 into the deterministic build."""

    def __init__(
        self,
        config: GenerationConfig,
        *,
        llm_client: LLMClient,
        oracle: Optional[LabelingOracle] = None,
        skew_audit: Optional[SkewAudit] = None,
        sampler: Optional[RejectionSampler] = None,
    ) -> None:
        self._config = config
        self._llm_client = llm_client
        self._oracle = oracle or LabelingOracle.from_config(
            rulebook_dir=config.rulebook_dir,
            rulebook_version=config.rulebook_version,
            engine_version=config.engine_version,
        )
        self._skew_audit = skew_audit or SkewAudit()
        self._sampler = sampler or RejectionSampler()

    def _seeded_factory(self) -> ProfileFactory:
        rng = random.Random(self._config.seed)
        faker = Faker()
        faker.seed_instance(self._config.seed)
        return ProfileFactory(rng, faker, self._config.seed)

    def generate(self, *, generation_timestamp: str) -> CorpusOutput:
        """Run the full seeded build. Raises ``BudgetExhaustedError`` /
        ``SkewAuditError`` loudly on failure (build-blocking; no partial corpus)."""
        factory = self._seeded_factory()

        # bounded rejection-sampling (engine is the label authority)
        sampled = self._sampler.sample(self._config, factory, self._oracle)

        # blocking conjunctive skew-audit gate BEFORE freeze
        counts: dict[str, int] = {cls: 0 for cls in self._config.target_split}
        present_edges: set[str] = set()
        for item in sampled:
            counts[item.label.value] = counts.get(item.label.value, 0) + 1
            present_edges.update(item.edge_case_tags)
        self._skew_audit.audit(
            class_counts=counts, present_edges=present_edges, config=self._config
        )

        # document prose via the injected seam, then assemble frozen records
        doc_gen = DocumentTextGenerator(self._llm_client, model=self._config.model_id)
        records: list[CorpusRecord] = []
        for item in sampled:
            records.append(
                CorpusRecord(
                    profile=item.profile,
                    documents_text=doc_gen.generate_for(item.profile),
                    label=item.label,
                    intended_class=item.intended_class,
                    edge_case_tags=item.edge_case_tags,
                )
            )

        manifest = build_manifest(
            records,
            self._config,
            generation_timestamp=generation_timestamp,
            model_version=self._config.model_id,
        )
        return CorpusOutput(records=records, manifest=manifest)

    def smoke(self, *, generation_timestamp: str = "1970-01-01T00:00:00Z") -> CorpusOutput:
        """Tier-S offline end-to-end smoke entrypoint (Fold NFR-1).

        Exercises factory->derive->label->sample->gate->freeze + a valid manifest on
        the (test-scoped) config with a fixed timestamp — never asserts the real band.
        """
        return self.generate(generation_timestamp=generation_timestamp)
