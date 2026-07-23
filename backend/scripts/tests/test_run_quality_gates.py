"""tier-U contract test for the four-gate runner over a frozen corpus (Q10's floor).

No LLM, no network, no key. The runner is the missing ENTRYPOINT for U13's four blocking
gates, which exist on disk as classes exercised only by their own tests — nothing in the
build ever ran them over a real corpus.

What is pinned here:

* **all four gates run**, and each emits its evidence report;
* **rule coverage loads the rulebook at the MANIFEST's version** (QG-Fold-2) — never a
  hardcoded one, so the gate is measured against the exact rulebook the corpus was labeled
  against;
* **blocking form** — any failing gate is a NON-ZERO exit (the ``run_migrations`` fail-loud
  precedent), and an all-pass run exits 0;
* **zero LLM** — the runner imports no provider, no adapter and no LLM client, which is the
  property that makes Q10's floor free.

⚑ The runner is deliberately a SCRIPT, not a pytest test: adding a corpus-presence-skipped
test under ``backend/quality_gates/tests/`` would be flagged by BLOCKING-1
(``test_blocking_form.py`` forbids ``@skip``/``@xfail`` on its four listed modules).
"""
from __future__ import annotations

import ast
import json

import pytest

from backend.corpus_generator.records import CorpusManifest
from backend.scripts import run_quality_gates as rqg


RULEBOOK_VERSION = "1.0.0"


def _write_corpus(tmp_path, records) -> None:
    (tmp_path / "profiles.json").write_text(
        json.dumps([r.model_dump(mode="json") for r in records]), encoding="utf-8"
    )
    manifest = CorpusManifest(
        seed=42,
        corpus_version="1.0.0",
        rulebook_version=RULEBOOK_VERSION,
        engine_version="corpus-build-1",
        provider="gemini",
        model_version="OFFLINE-DOUBLE-NOT-A-REAL-LLM",
        class_counts={"APPROVE": 1, "REFER": 1, "DECLINE-RECOMMEND": 1},
        class_proportions={"APPROVE": "0.4", "REFER": "0.35", "DECLINE-RECOMMEND": "0.25"},
        tolerance_pp=3,
        edge_case_checklist={"thin_file": True},
        profile_count=len(records),
        content_hash="0" * 64,
        generation_timestamp="1970-01-01T00:00:00Z",
    )
    (tmp_path / "manifest.json").write_text(
        manifest.model_dump_json(indent=2), encoding="utf-8"
    )


def _mini_records():
    """Three GENUINE ``CorpusRecord``s — real seeded profiles labeled by the real engine.

    Built from ``corpus_generator``'s own factory + oracle rather than hand-rolled stubs, so
    the runner is exercised against the true record shape. No cross-unit test-tree coupling.
    """
    import random

    from faker import Faker

    from backend.corpus_generator.labeling_oracle import LabelingOracle
    from backend.corpus_generator.profile_factory import ProfileFactory
    from backend.corpus_generator.records import CorpusRecord

    rulebook_dir = str(
        __import__("pathlib").Path(rqg.__file__).resolve().parents[1]
        / "rules_engine"
        / "rulebook"
    )
    faker = Faker()
    faker.seed_instance(42)
    factory = ProfileFactory(random.Random(42), faker, 42)
    oracle = LabelingOracle.from_config(
        rulebook_dir=rulebook_dir,
        rulebook_version=RULEBOOK_VERSION,
        engine_version="qg-runner-test-1",
    )

    records = []
    for index, build in enumerate(
        (factory.build_approve, factory.build_refer, factory.build_decline)
    ):
        profile, tags = build(index)
        label = oracle.label(profile)
        records.append(
            CorpusRecord(
                profile=profile,
                documents_text={"salary_slip": "placeholder"},
                label=label,
                intended_class=label,
                edge_case_tags=tags,
            )
        )
    return records


@pytest.fixture()
def corpus(tmp_path):
    """A tiny but GENUINE frozen corpus on disk."""
    _write_corpus(tmp_path, _mini_records())
    return tmp_path


# ---------------------------------------------------------------------------
# 1-3. the four gates run; blocking form both ways
# ---------------------------------------------------------------------------
def test_all_four_gates_run_and_emit_evidence(corpus, tmp_path):
    reports_dir = tmp_path / "gate-reports"
    exit_code = rqg.main(["--corpus", str(corpus), "--reports", str(reports_dir)])

    assert exit_code == 0
    names = {p.name for p in reports_dir.iterdir()}
    assert names == {
        "bias-swap.json",
        "reproducibility.json",
        "rule-coverage.json",
        "coverage-wiring.json",
    }


def test_a_failing_gate_produces_a_non_zero_exit(corpus, tmp_path, monkeypatch):
    """Blocking form: a gate reporting ``passed is False`` must fail the run loudly."""

    class _FailingReport:
        passed = False

        def to_json(self, *, generated_at=None, indent=2) -> str:
            return "{}"

    class _FailingGate:
        def __init__(self, *a, **k) -> None: ...

        def run(self, *a, **k):
            return _FailingReport()

    monkeypatch.setattr(rqg, "BiasSwapGate", _FailingGate)

    exit_code = rqg.main(
        ["--corpus", str(corpus), "--reports", str(tmp_path / "r")]
    )

    assert exit_code != 0


def test_an_all_pass_run_exits_zero(corpus, tmp_path):
    assert rqg.main(["--corpus", str(corpus), "--reports", str(tmp_path / "r")]) == 0


# ---------------------------------------------------------------------------
# 4. rule coverage reads the MANIFEST's rulebook version (QG-Fold-2)
# ---------------------------------------------------------------------------
def test_rule_coverage_uses_the_rulebook_version_from_the_manifest(corpus, tmp_path, monkeypatch):
    seen: dict = {}
    real_gate = rqg.RuleCoverageGate

    class _SpyGate(real_gate):  # type: ignore[misc, valid-type]
        def run(self, profiles, rulebook_version):
            seen["version"] = rulebook_version
            return super().run(profiles, rulebook_version)

    monkeypatch.setattr(rqg, "RuleCoverageGate", _SpyGate)
    rqg.main(["--corpus", str(corpus), "--reports", str(tmp_path / "r")])

    assert seen["version"] == RULEBOOK_VERSION, (
        "the gate must be measured against the exact rulebook version the corpus was "
        "labeled against (QG-Fold-2), never a hardcoded one"
    )


# ---------------------------------------------------------------------------
# 5-6. zero-LLM property and a missing corpus fails loudly
# ---------------------------------------------------------------------------
def test_the_runner_imports_no_llm_provider_adapter_or_client():
    """Q10's floor is FREE precisely because this path holds no model. Asserted
    structurally over the import statements, not by a raw substring scan."""
    with open(rqg.__file__, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=rqg.__file__)

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            for alias in node.names:
                imported.add(alias.name)

    forbidden = ("google", "anthropic", "ollama", "llm_client", "memo_agent_core",
                 "memo_extensions", "llm_judge", "build_gemini_client")
    for token in forbidden:
        assert not any(token in name for name in imported), (token, imported)


def test_a_missing_corpus_fails_loudly(tmp_path):
    with pytest.raises((FileNotFoundError, SystemExit)):
        rqg.main(["--corpus", str(tmp_path / "absent"), "--reports", str(tmp_path / "r")])
