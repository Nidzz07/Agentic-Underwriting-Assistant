"""The memo-provider selector, the model-ID/stamp split, and the per-draft boundary.

⛔ **NO DAEMON, NO NETWORK.** The Ollama branch is exercised by monkeypatching the SDK's ``Client``,
never by contacting one. The point of ``build_ollama_client``'s injected-seam design is that this
file needs no running Ollama.

⚑ **WHY A SEPARATE FILE FROM ``test_ollama_client.py``.** That one tests the CLIENT in isolation;
this one tests the COMPOSITION — which adapter is chosen, which strings reach the orchestrator, and
whether the per-draft scope is opened. The register #18 defect was *precisely* a composition-root
omission, and a test that composed its own seams could not have seen it (the J8/J9 lesson).
"""
from __future__ import annotations

import pytest

from backend.app import dependencies as dep
from backend.app.offline_memo_double import OFFLINE_MODEL_VERSION, OfflineMemoLLMClient
from backend.app.ollama_client import CappedOllamaClient
from backend.memo_agent_core.provider import GeminiAdapter
from backend.memo_extensions.provider_showcase import OllamaAdapter


class _FakeSDK:
    """Stands in for ``ollama.Client``. Records nothing; answers ``show`` with a digest."""

    def __init__(self, host=None, timeout=None):
        pass

    def generate(self, **kwargs):
        class R:
            response = "<memo><narrative_prose>x</narrative_prose></memo>"

        return R()

    def show(self, model_id):
        return {"digest": "sha256:abcdef0123456789abcdef0123456789"}


@pytest.fixture
def fake_ollama(monkeypatch):
    import ollama

    monkeypatch.setattr(ollama, "Client", _FakeSDK)


def _adapter(seams) -> object:
    """The adapter the orchestrator was actually built with."""
    return seams._orchestrator._provider


def _stamp(seams) -> str:
    return seams._orchestrator._model_version


class TestTheSelectorFailsSafe:
    """⛔ Q9's opt-in decision, enforced mechanically rather than by documentation."""

    def test_an_UNSET_variable_yields_the_offline_double(self, monkeypatch):
        monkeypatch.delenv(dep.MEMO_PROVIDER_ENV, raising=False)
        assert dep.ollama_is_selected() is False
        seams = dep._CompositionSeams()
        assert isinstance(_adapter(seams), GeminiAdapter)
        assert isinstance(seams._llm_client, OfflineMemoLLMClient)

    @pytest.mark.parametrize(
        "value", ["Ollama", "OLLAMA", "ollama ", " ollama", "true", "1", "yes", "gemini", ""]
    )
    def test_only_the_EXACT_literal_selects_the_live_provider(self, monkeypatch, value):
        """⛔ **THE POLARITY IS THE POINT.** A near-miss must fail SAFE, never fail open — a
        fat-fingered variable can never put a real model in front of a user."""
        monkeypatch.setenv(dep.MEMO_PROVIDER_ENV, value)
        assert dep.ollama_is_selected() is False
        assert isinstance(_adapter(dep._CompositionSeams()), GeminiAdapter)

    def test_the_exact_literal_DOES_select_ollama(self, monkeypatch, fake_ollama):
        """⚑ The non-vacuity partner. Without it every test above passes against a selector that
        is simply broken shut."""
        monkeypatch.setenv(dep.MEMO_PROVIDER_ENV, "ollama")
        assert dep.ollama_is_selected() is True
        seams = dep._CompositionSeams()
        assert isinstance(_adapter(seams), OllamaAdapter)
        assert isinstance(seams._llm_client, CappedOllamaClient)


class TestTheModelIdStampSplit:
    """⛔ The §1.2 conflation, pinned so it cannot return."""

    def test_the_offline_path_is_byte_unchanged(self, monkeypatch):
        """⚠️ The historical behaviour: model AND stamp are both ``OFFLINE_MODEL_VERSION``. That
        is correct for the double, whose ``generate`` ignores ``model`` entirely."""
        monkeypatch.delenv(dep.MEMO_PROVIDER_ENV, raising=False)
        seams = dep._CompositionSeams()
        assert _adapter(seams).model_version == OFFLINE_MODEL_VERSION
        assert _stamp(seams) == OFFLINE_MODEL_VERSION

    def test_the_model_ID_and_the_STAMP_are_DIFFERENT_strings(self, monkeypatch, fake_ollama):
        """⛔ **THE WHOLE POINT OF THE SPLIT.** Before this pass both arguments were one string.
        A live provider needs the ID to be resolvable and the stamp to be provenance."""
        monkeypatch.setenv(dep.MEMO_PROVIDER_ENV, "ollama")
        seams = dep._CompositionSeams()
        model_id = _adapter(seams).model_version   # the adapter's ``model`` — the resolvable ID
        stamp = _stamp(seams)
        assert model_id == dep.OLLAMA_MODEL_ID
        assert stamp != model_id
        assert model_id in stamp                   # the ID is a COMPONENT of the stamp
        # ⚑ The stamp LEADS with the marker (stage 6), not with the model id — asserted here so a
        # later reordering that buried the marker mid-string would fail rather than pass quietly.
        assert stamp.startswith(dep.NOT_QUALITY_GATED_MARKER)

    def test_the_stamp_carries_all_THREE_components(self, monkeypatch, fake_ollama):
        monkeypatch.setenv(dep.MEMO_PROVIDER_ENV, "ollama")
        stamp = _stamp(dep._CompositionSeams())
        assert dep.OLLAMA_MODEL_ID in stamp
        assert "abcdef012345" in stamp             # the digest, truncated
        assert "ollama-python-" in stamp

    def test_the_digest_is_truncated_not_dropped(self, monkeypatch, fake_ollama):
        monkeypatch.setenv(dep.MEMO_PROVIDER_ENV, "ollama")
        stamp = _stamp(dep._CompositionSeams())
        assert "abcdef0123456789abcdef0123456789" not in stamp   # not the full digest
        assert len("abcdef012345") == dep.OLLAMA_DIGEST_CHARS

    def test_a_digest_lookup_FAILURE_still_yields_a_usable_stamp(self):
        """⚠️ Fail-soft, asserted. A provenance detail must never break a draft, and the stamp must
        SAY the digest is unknown rather than silently looking complete."""
        class Broken:
            def show_digest(self, model_id):
                raise RuntimeError("daemon said no")

        stamp = dep.build_ollama_stamp("m", Broken())
        assert dep.OLLAMA_DIGEST_UNAVAILABLE in stamp
        # ⚑ The other two components survive a digest failure — the stamp degrades, it does not
        # collapse. (The marker leads the string from stage 6 onward.)
        assert stamp.startswith(f"{dep.NOT_QUALITY_GATED_MARKER}+m+")
        assert "ollama-python-" in stamp

    def test_a_client_without_show_digest_is_tolerated(self):
        stamp = dep.build_ollama_stamp("m", object())
        assert dep.OLLAMA_DIGEST_UNAVAILABLE in stamp


class TestTheNonQualityGatedMarker:
    """⛔ Q9 / G2 option D — the marker half. The rendered half lives in the frontend unit."""

    def test_the_ollama_stamp_LEADS_with_the_marker(self, monkeypatch, fake_ollama):
        """⚑ Leading, not merely containing: it must be the first thing visible wherever
        ``model_version`` travels — psql, R4, R7 and the UI's forensic tuple."""
        monkeypatch.setenv(dep.MEMO_PROVIDER_ENV, "ollama")
        assert _stamp(dep._CompositionSeams()).startswith(dep.NOT_QUALITY_GATED_MARKER)

    def test_the_OFFLINE_stamp_does_NOT_carry_the_marker(self, monkeypatch):
        """⛔ The non-vacuity partner, and it is not pedantry. The offline double is not a
        quality-gate question at all — it is not a model. Marking it would dilute the marker to
        meaninglessness, and its own stamp already says what it is."""
        monkeypatch.delenv(dep.MEMO_PROVIDER_ENV, raising=False)
        assert dep.NOT_QUALITY_GATED_MARKER not in _stamp(dep._CompositionSeams())

    def test_the_marker_value_matches_the_frontend_predicate(self):
        """⛔ The two halves of G2-D are matched BY VALUE across the stack, and nothing else pins
        them together. ⚑ Same reference-not-own discipline the build applies to ``RBAC_COMMIT``
        and to ``OFFLINE_MODEL_VERSION``'s two copies: read the frontend's literal off disk and
        assert equality, so a rename on either side fails here rather than silently un-rendering
        the notice in production."""
        from pathlib import Path

        source = (
            Path(__file__).resolve().parents[3]
            / "frontend" / "src" / "memoView" / "components" / "ProviderGateNotice.jsx"
        ).read_text(encoding="utf-8")
        assert f"'{dep.NOT_QUALITY_GATED_MARKER}'" in source


class TestThePerDraftBoundary:
    """⛔ §5.2's counting scope, opened where it costs no ``case_lifecycle`` reopening."""

    def test_draft_memo_opens_a_new_counting_scope(self, monkeypatch, fake_ollama):
        monkeypatch.setenv(dep.MEMO_PROVIDER_ENV, "ollama")
        seams = dep._CompositionSeams()
        calls: list[int] = []
        monkeypatch.setattr(
            seams._llm_client, "begin_draft", lambda: calls.append(1)
        )
        monkeypatch.setattr(seams._orchestrator, "run", lambda _inp: None)
        monkeypatch.setattr(seams._builder, "build", lambda **kw: object())

        seams.draft_memo(object(), object(), None)
        seams.draft_memo(object(), object(), None)
        assert calls == [1, 1], "begin_draft must fire once per draft_memo, not once per process"

    def test_the_offline_path_has_no_begin_draft_and_still_drafts(self, monkeypatch):
        """⚠️ The guard's other half. ``OfflineMemoLLMClient`` has no such method; the offline
        path must stay byte-unchanged rather than acquiring an AttributeError."""
        monkeypatch.delenv(dep.MEMO_PROVIDER_ENV, raising=False)
        seams = dep._CompositionSeams()
        assert not hasattr(seams._llm_client, "begin_draft")
        monkeypatch.setattr(seams._orchestrator, "run", lambda _inp: "drafted")
        monkeypatch.setattr(seams._builder, "build", lambda **kw: object())
        assert seams.draft_memo(object(), object(), None) == "drafted"


class TestConstructionCosts:
    def test_the_digest_is_looked_up_ONCE_at_construction_not_per_draft(
        self, monkeypatch, fake_ollama
    ):
        """⚑ A per-draft ``show()`` would add a network round-trip to every memo for a string that
        cannot change while the process runs."""
        monkeypatch.setenv(dep.MEMO_PROVIDER_ENV, "ollama")
        lookups: list[str] = []
        original = CappedOllamaClient.show_digest

        def counting(self, model_id):
            lookups.append(model_id)
            return original(self, model_id)

        monkeypatch.setattr(CappedOllamaClient, "show_digest", counting)
        seams = dep._CompositionSeams()
        monkeypatch.setattr(seams._orchestrator, "run", lambda _inp: None)
        monkeypatch.setattr(seams._builder, "build", lambda **kw: object())
        seams.draft_memo(object(), object(), None)
        seams.draft_memo(object(), object(), None)
        assert lookups == [dep.OLLAMA_MODEL_ID]

    def test_the_thinking_mode_reaches_the_adapter(self, monkeypatch, fake_ollama):
        """⚑ Pins that the adapter is constructed with a mode at all — Fold-1's constraint is that
        it arrives at CONSTRUCTION, the frozen ``complete()`` admitting no such parameter."""
        monkeypatch.setenv(dep.MEMO_PROVIDER_ENV, "ollama")
        seams = dep._CompositionSeams()
        assert _adapter(seams)._thinking_mode is not None
