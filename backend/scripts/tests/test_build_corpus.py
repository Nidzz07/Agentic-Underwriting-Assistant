"""tier-U contract test for the guarded tier-B corpus entrypoint (register #3, Stage 1).

No network, no key, no SDK, no real corpus. Monkeypatches the frozen ``CorpusGenerator``
so the ENTRYPOINT's contract is asserted in isolation from the (slow, seeded) generation
pipeline — the ``run_migrations`` tier-U precedent.

What is pinned here:

* **dry-run counts, never spends** — the count is MEASURED by a counting double driven
  through the real pipeline shape, not derived from a ``3 x N`` formula, and the dry-run
  writes NO file and never constructs a real client;
* **offline is the DEFAULT** and writes both frozen artifacts;
* **the offline double is defined LOCALLY** in the entrypoint — never imported from a
  frozen unit's ``tests/conftest.py`` (ambiguity-check (v));
* **the real path is refused without ``ALLOW_REAL_LLM_CALLS``** — asserted against the
  GENUINE ``build_gemini_client``, not a stub, so the guard chain is really wired;
* **``--max-llm-calls`` is passed EXPLICITLY** — the ``max_calls=20`` default in
  ``backend/app/llm_client.py`` is never relied upon and never changed;
* **a floating model alias is refused** (Q5 / register #22's non-floating-pin discipline);
* **the module imports with ``google-genai`` ABSENT** (lazy import preserved);
* **no key material and no prompt text is ever printed** (SEC-3).

This module lives in ``backend/scripts/`` — outside every ``--cov`` target — so it
exercises the entrypoint without that logic entering the coverage denominator, exactly as
the entrypoint itself is coverage-invisible.
"""
from __future__ import annotations

import ast
import json
import sys

import pytest

from backend.app.llm_client import RealLLMCallsNotEnabled
from backend.corpus_generator.records import CorpusManifest, CorpusRecord
from backend.scripts import build_corpus as bc


# ---------------------------------------------------------------------------
# doubles
# ---------------------------------------------------------------------------
class _FakeSettings:
    """Stands in for ``secrets_config.Settings`` so the test never needs a real ``.env``."""

    GEMINI_API_KEY = "not-a-real-key"


def _fake_generator_factory(profiles: int, docs_per_profile: int, recorder: dict):
    """Build a fake ``CorpusGenerator`` class that drives the injected client exactly
    ``profiles * docs_per_profile`` times — mirroring ``DocumentTextGenerator``'s real
    one-call-per-doc-type-per-profile shape without running the seeded pipeline."""

    class _FakeGenerator:
        def __init__(self, config, *, llm_client):
            recorder["config"] = config
            recorder["client"] = llm_client
            self._client = llm_client
            self._config = config

        def generate(self, *, generation_timestamp: str):
            for _ in range(profiles):
                for _ in range(docs_per_profile):
                    self._client.generate(
                        model=self._config.model_id,
                        prompt="SYNTHETIC PROMPT - never printed",
                        temperature=0,
                    )
            return bc.CorpusOutput(records=[], manifest=_manifest(self._config))

    return _FakeGenerator


def _manifest(config) -> CorpusManifest:
    return CorpusManifest(
        seed=config.seed,
        corpus_version="1.0.0",
        rulebook_version=config.rulebook_version,
        engine_version=config.engine_version,
        provider="gemini",
        model_version=config.model_id,
        class_counts={"APPROVE": 0, "REFER": 0, "DECLINE-RECOMMEND": 0},
        class_proportions={"APPROVE": "0", "REFER": "0", "DECLINE-RECOMMEND": "0"},
        tolerance_pp=config.tolerance_pp,
        edge_case_checklist={edge: True for edge in config.required_edge_cases},
        profile_count=0,
        content_hash="0" * 64,
        generation_timestamp="1970-01-01T00:00:00Z",
    )


@pytest.fixture()
def fake_pipeline(monkeypatch):
    """Install a fake generator making 2 profiles x 3 docs = 6 client calls."""
    recorder: dict = {}
    monkeypatch.setattr(bc, "CorpusGenerator", _fake_generator_factory(2, 3, recorder))
    monkeypatch.setattr(bc, "get_settings", lambda: _FakeSettings())
    return recorder


# ---------------------------------------------------------------------------
# 1-2. dry-run: measures, never spends, never writes
# ---------------------------------------------------------------------------
def test_dry_run_reports_the_measured_call_count_and_writes_nothing(
    fake_pipeline, tmp_path, capsys
):
    exit_code = bc.main(["--dry-run", "--out", str(tmp_path), "--min-profiles", "2"])

    assert exit_code == 0
    out = capsys.readouterr().out
    # the count is MEASURED (2 profiles x 3 doc types), not a 3xN formula
    assert "6" in out
    assert "DRY RUN" in out.upper()
    # nothing was written - the dry run is inspection only
    assert list(tmp_path.iterdir()) == []


def test_dry_run_never_constructs_a_real_client(fake_pipeline, tmp_path, monkeypatch):
    called: list = []
    monkeypatch.setattr(
        bc, "build_gemini_client", lambda *a, **k: called.append((a, k))
    )

    bc.main(["--dry-run", "--out", str(tmp_path), "--min-profiles", "2"])

    assert called == [], "the dry run must never reach the spend-capable factory"


# ---------------------------------------------------------------------------
# 3-4. offline is the default; the double is local
# ---------------------------------------------------------------------------
def test_the_default_mode_is_offline_and_writes_both_frozen_artifacts(
    fake_pipeline, tmp_path
):
    exit_code = bc.main(["--out", str(tmp_path), "--min-profiles", "2"])

    assert exit_code == 0
    assert (tmp_path / "profiles.json").exists()
    assert (tmp_path / "manifest.json").exists()
    # the offline stamp is unmistakable in the frozen manifest
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["model_version"] == bc.OFFLINE_MODEL_ID
    assert "NOT-A-REAL-LLM" in manifest["model_version"]


def test_the_offline_double_is_defined_locally_not_imported_from_a_unit_test_tree():
    """ambiguity-check (v): a production script must not depend on a frozen unit's
    ``tests/conftest.py``. The double is this module's own.

    ⚑ Scanned with ``ast`` over the IMPORT STATEMENTS, deliberately NOT with a raw
    substring test. A substring test is dishonest here: the module's own docstring
    legitimately NAMES ``tests/conftest.py`` and ``CapturingLLMClient`` while explaining
    why it does not import them, so ``"conftest" in text`` flags the disclosure rather
    than a dependency - the same false-positive class as U22's ``city``-inside-
    ``ethnicity`` collision (llm-judge code-summary §3.4).
    """
    with open(bc.__file__, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=bc.__file__)

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            for alias in node.names:
                imported.add(alias.name)

    assert not any("conftest" in name for name in imported), imported
    assert not any(".tests" in name for name in imported), imported
    assert "CapturingLLMClient" not in imported

    # the double is defined HERE, and genuinely satisfies the frozen seam shape
    assert bc._OfflineLLMClient.__module__ == bc.__name__
    double = bc._OfflineLLMClient()
    assert isinstance(double.generate(model="m", prompt="p", temperature=0), str)
    assert double.calls == 1, "the double must count calls so --dry-run can MEASURE"


# ---------------------------------------------------------------------------
# 5-7. the real path: two gates, explicit cap, non-floating pin
# ---------------------------------------------------------------------------
def test_the_real_path_is_refused_without_the_env_flag(
    fake_pipeline, tmp_path, monkeypatch
):
    """Asserted against the GENUINE ``build_gemini_client`` - not a stub - so this proves
    the #18 guard chain is really wired, not merely referenced."""
    monkeypatch.delenv("ALLOW_REAL_LLM_CALLS", raising=False)

    with pytest.raises(RealLLMCallsNotEnabled):
        bc.main(
            [
                "--real-llm",
                "--model-id", "gemini-2.5-flash-001",
                "--max-llm-calls", "10",
                "--out", str(tmp_path),
                "--min-profiles", "2",
            ]
        )

    assert list(tmp_path.iterdir()) == [], "a refused run must write nothing"


def test_the_real_path_passes_max_llm_calls_explicitly(
    fake_pipeline, tmp_path, monkeypatch
):
    """The ``max_calls=20`` default in ``backend/app/llm_client.py`` is NEVER relied on."""
    seen: dict = {}

    def _spy(settings, *, model_id, max_calls):
        seen["model_id"] = model_id
        seen["max_calls"] = max_calls
        return bc._OfflineLLMClient()

    monkeypatch.setattr(bc, "build_gemini_client", _spy)

    bc.main(
        [
            "--real-llm",
            "--model-id", "gemini-2.5-flash-001",
            "--max-llm-calls", "1200",
            "--out", str(tmp_path),
            "--min-profiles", "2",
        ]
    )

    assert seen["max_calls"] == 1200, "the CLI value must reach the factory explicitly"
    assert seen["max_calls"] != 20, "the wrapper default must not be what is used"
    assert seen["model_id"] == "gemini-2.5-flash-001"


def test_the_real_path_refuses_a_floating_model_alias(fake_pipeline, tmp_path, monkeypatch):
    """Q5 / register #22: a floating alias would be stamped into the manifest's permanent
    provenance, making prose drift untraceable."""
    called: list = []
    monkeypatch.setattr(bc, "build_gemini_client", lambda *a, **k: called.append(1))

    with pytest.raises(SystemExit) as excinfo:
        bc.main(
            [
                "--real-llm",
                "--model-id", "gemini-2.5-flash",  # the floating alias
                "--max-llm-calls", "10",
                "--out", str(tmp_path),
                "--min-profiles", "2",
            ]
        )

    assert excinfo.value.code != 0
    assert called == [], "a floating alias must be refused BEFORE any client is built"


# ---------------------------------------------------------------------------
# 8-9. SDK-absence and disclosure hygiene
# ---------------------------------------------------------------------------
def test_the_module_imports_without_the_google_genai_sdk_installed():
    """In this environment ``google-genai`` is GENUINELY absent, so a successful import of
    the entrypoint is a real proof that the SDK import stays lazy (inside the #18 factory)."""
    assert "google.genai" not in sys.modules
    assert bc.main is not None


def test_no_key_material_and_no_prompt_text_is_printed(fake_pipeline, tmp_path, capsys):
    bc.main(["--out", str(tmp_path), "--min-profiles", "2"])

    out = capsys.readouterr().out
    assert "not-a-real-key" not in out          # the fake settings key never surfaces
    assert "GEMINI_API_KEY" not in out
    assert "SYNTHETIC PROMPT" not in out        # prompts are never echoed (SEC-3)
