"""Register #18 tier-U guardrail suite for ``backend/app/llm_client.py``.

The FIRST production ``LLMClient`` path in this build. Every test here runs
**offline**: a hand-written fake SDK object stands in for ``google-genai``'s
client, so there is **no key, no network, and ``google-genai`` need not even be
installed**. The wrapper is SDK-agnostic by construction (it imports nothing from
``google.genai``); the guarded factory owns the ``ALLOW_REAL_LLM_CALLS`` spend gate
and the lazy SDK import — the only spend-capable path.

Shape (Q9-A): TWO pieces — a flag-free, purely-injected ``CappedGeminiClient``
wrapper + a guarded ``build_gemini_client`` factory. See
``guide-docs/build/plans/fix-register-18-code-gen-plan.md``.
"""
from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace

import pytest

from backend.app.llm_client import (
    CappedGeminiClient,
    LLMCallCapExceeded,
    RealLLMCallsNotEnabled,
    build_gemini_client,
)

#: Valid structured XML the frozen ``GeminiAdapter._parse_xml`` accepts — cites a
#: rule present in the factory report so citation validation passes for the right reason.
_VALID_XML = (
    "<memo>"
    "<narrative_prose>Advisory recommendation prose for underwriter review.</narrative_prose>"
    "<cited_rule_ids><rule_id>R-AGE-1</rule_id></cited_rule_ids>"
    "</memo>"
)

#: Citation-INVALID XML — cites a rule that is in neither report nor rulebook, so the
#: orchestrator's CITE-FAILURE retry loop re-enters the client (Test 8's whole point).
_CITATION_INVALID_XML = (
    "<memo>"
    "<narrative_prose>Prose citing a non-existent rule.</narrative_prose>"
    "<cited_rule_ids><rule_id>R-HALLUCINATED-999</rule_id></cited_rule_ids>"
    "</memo>"
)


class _FakeGenAIClient:
    """Hand-written stand-in for a ``google-genai`` client. No network, no key.

    Mirrors ONLY the surface ``CappedGeminiClient`` actually calls:
    ``.models.generate_content(model=, contents=, config=) -> obj with .text``.
    """

    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.calls: list[dict] = []
        self.models = self  # generate_content is reached via ``.models``

    def generate_content(self, *, model, contents, config):
        self.calls.append({"model": model, "contents": contents, "config": config})
        return SimpleNamespace(text=self._response_text)


class _KeyLeakingFakeClient(_FakeGenAIClient):
    """A fake whose ``repr`` embeds key material — proves the wrapper's ``repr``
    does NOT delegate to (and therefore cannot leak) the wrapped object's repr."""

    def __repr__(self) -> str:  # pragma: no cover - only its ABSENCE from wrapper repr is asserted
        return "GenAIClient(api_key='SECRET-KEY-DO-NOT-LEAK')"


# ============================================================================
# STEP 2 — the wrapper ``CappedGeminiClient`` (flag-free, purely injected)
# ============================================================================

def test_it_satisfies_the_frozen_llmclient_protocol():
    # The TEST imports the frozen runtime_checkable Protocol; PRODUCTION does not —
    # conformance is proven structurally without the wrapper coupling to the seam.
    from backend.memo_agent_core.provider import LLMClient

    wrapper = CappedGeminiClient(_FakeGenAIClient(_VALID_XML))
    assert isinstance(wrapper, LLMClient)


def test_it_passes_temperature_through_untouched():
    fake = _FakeGenAIClient(_VALID_XML)
    wrapper = CappedGeminiClient(fake)
    # A non-zero temperature proves the wrapper SETS nothing and DEFAULTS nothing.
    wrapper.generate(model="gemini-x", prompt="p", temperature=0.7)
    assert fake.calls[0]["config"]["temperature"] == 0.7


def test_it_passes_the_model_id_through_untouched():
    fake = _FakeGenAIClient(_VALID_XML)
    wrapper = CappedGeminiClient(fake)
    wrapper.generate(model="gemini-2.5-flash-001", prompt="p", temperature=0)
    assert fake.calls[0]["model"] == "gemini-2.5-flash-001"


def test_it_returns_the_sdk_response_text():
    wrapper = CappedGeminiClient(_FakeGenAIClient("RAW-XML-PAYLOAD"))
    assert wrapper.generate(model="m", prompt="p", temperature=0) == "RAW-XML-PAYLOAD"


def test_it_counts_every_call():
    wrapper = CappedGeminiClient(_FakeGenAIClient(_VALID_XML))
    assert wrapper.call_count == 0
    wrapper.generate(model="m", prompt="p", temperature=0)
    wrapper.generate(model="m", prompt="p", temperature=0)
    assert wrapper.call_count == 2


def test_it_refuses_beyond_the_cap():
    wrapper = CappedGeminiClient(_FakeGenAIClient(_VALID_XML), max_calls=3)
    for _ in range(3):
        wrapper.generate(model="m", prompt="p", temperature=0)  # max_calls OK
    with pytest.raises(LLMCallCapExceeded):
        wrapper.generate(model="m", prompt="p", temperature=0)  # max_calls + 1 raises
    assert wrapper.call_count == 3  # the refused call is NOT counted


def test_the_cap_default_is_20():
    assert inspect.signature(CappedGeminiClient.__init__).parameters["max_calls"].default == 20


def test_the_cap_counts_retries_not_just_drafts():
    """⛔ THE TOOTH — a cap counting only drafts would silently under-count.

    Drives the REAL ``LangGraphOrchestrator`` through the REAL ``GeminiAdapter`` over
    our wrapper over a fake SDK object that returns citation-invalid XML, forcing the
    ``MEMO_CITATION_RETRY_CAP`` retry loop, then asserts ``call_count > 1`` for a
    SINGLE draft — and that the cap fires MID-RETRY when set below the retry count.
    """
    from backend.memo_agent_core.constants import MEMO_CITATION_RETRY_CAP
    from backend.memo_agent_core.orchestrator import LangGraphOrchestrator
    from backend.memo_agent_core.provider import GeminiAdapter
    from backend.memo_agent_core.tests.fixtures.factories import (
        make_input,
        make_report,
        make_rulebook,
    )

    rule_ids = ("R-AGE-1", "R-DTI-1")

    # (a) with headroom, ONE draft re-enters the client and every retry is counted.
    fake = _FakeGenAIClient(_CITATION_INVALID_XML)
    wrapper = CappedGeminiClient(fake, max_calls=20)
    orch = LangGraphOrchestrator(
        GeminiAdapter(wrapper, model="gemini-2.5-flash"),
        rulebook=make_rulebook(rule_ids=rule_ids),
        model_version="test",
    )
    orch.run(make_input(report=make_report(rule_ids=rule_ids)))
    assert wrapper.call_count == MEMO_CITATION_RETRY_CAP
    assert wrapper.call_count > 1  # a spy on generate() alone would pass; this proves retries counted

    # (b) with the cap set below the retry count, it fires MID-RETRY.
    fake_low = _FakeGenAIClient(_CITATION_INVALID_XML)
    capped_low = CappedGeminiClient(fake_low, max_calls=1)
    orch_low = LangGraphOrchestrator(
        GeminiAdapter(capped_low, model="gemini-2.5-flash"),
        rulebook=make_rulebook(rule_ids=rule_ids),
        model_version="test",
    )
    with pytest.raises(LLMCallCapExceeded):
        orch_low.run(make_input(report=make_report(rule_ids=rule_ids)))
    assert capped_low.call_count == 1  # the first draft succeeded; the retry was refused


def test_its_repr_discloses_no_key_material():
    wrapper = CappedGeminiClient(_KeyLeakingFakeClient(_VALID_XML))
    rendered = repr(wrapper)
    assert "SECRET-KEY-DO-NOT-LEAK" not in rendered
    assert "api_key" not in rendered


def test_it_logs_prompt_length_never_prompt_text(caplog):
    secret_prompt = "UNIQUE-PROMPT-BODY-THAT-MUST-NEVER-BE-LOGGED"
    wrapper = CappedGeminiClient(_FakeGenAIClient(_VALID_XML))
    with caplog.at_level(logging.INFO, logger="backend.app.llm_client"):
        wrapper.generate(model="gemini-x", prompt=secret_prompt, temperature=0)
    assert str(len(secret_prompt)) in caplog.text  # the LENGTH is logged
    assert secret_prompt not in caplog.text          # the BODY is not


def test_the_wrapper_structurally_holds_no_key():
    """⚑ STRUCTURAL non-disclosure (task brief), distinct from the behavioural Q3c repr test.

    The wrapper receives an ALREADY-CONSTRUCTED SDK object; its constructor has NO key
    parameter at all, so it *cannot* hold the key — a strictly stronger property than
    'does not disclose it'. Proven from the signature, not from behaviour.
    """
    params = list(inspect.signature(CappedGeminiClient.__init__).parameters)
    assert params == ["self", "sdk_client", "max_calls"]
    assert not any("key" in p.lower() for p in params)
    # and no instance attribute holds anything key-shaped
    wrapper = CappedGeminiClient(_FakeGenAIClient(_VALID_XML))
    assert not any("key" in name.lower() for name in vars(wrapper))


# ============================================================================
# STEP 3 — the factory ``build_gemini_client`` (the ONLY spend-capable path)
# ============================================================================

def _settings(key: str = "a-real-looking-key"):
    """A minimal stand-in for the frozen ``Settings`` — only ``GEMINI_API_KEY`` is read."""
    return SimpleNamespace(GEMINI_API_KEY=key)


def test_it_refuses_without_the_env_flag(monkeypatch):
    monkeypatch.delenv("ALLOW_REAL_LLM_CALLS", raising=False)
    with pytest.raises(RealLLMCallsNotEnabled):
        build_gemini_client(_settings(), model_id="gemini-2.5-flash-001")


def test_it_refuses_when_the_flag_is_not_exactly_true(monkeypatch):
    # Exact-match, fail-closed: only the literal string "true" enables spend.
    for value in ("1", "yes", "TRUE ", "True", "true ", "TRUE", "", " true"):
        monkeypatch.setenv("ALLOW_REAL_LLM_CALLS", value)
        with pytest.raises(RealLLMCallsNotEnabled):
            build_gemini_client(_settings(), model_id="gemini-2.5-flash-001")


def test_it_fails_closed_on_an_empty_or_whitespace_key(monkeypatch):
    # Q3b(i) — the structurally-invalid key ``Settings`` alone would not catch, checked
    # BEFORE the lazy SDK import so it never depends on google-genai being installed.
    monkeypatch.setenv("ALLOW_REAL_LLM_CALLS", "true")
    for bad in ("", "   ", "\t", None):
        with pytest.raises(RealLLMCallsNotEnabled):
            build_gemini_client(_settings(bad), model_id="gemini-2.5-flash-001")


def test_the_refusal_message_contains_no_key_material(monkeypatch):
    # Q3c — the factory's refusal must never echo the configured key.
    monkeypatch.delenv("ALLOW_REAL_LLM_CALLS", raising=False)
    secret = "SECRET-KEY-abc123-DO-NOT-LEAK"
    with pytest.raises(RealLLMCallsNotEnabled) as exc:
        build_gemini_client(_settings(secret), model_id="gemini-2.5-flash-001")
    assert secret not in str(exc.value)


def test_the_wrapper_constructor_needs_no_flag(monkeypatch):
    # ⛔ Q9-A's whole point: the wrapper is constructible AND usable with the spend flag
    # completely unset — the offline suite never touches a spend flag.
    monkeypatch.delenv("ALLOW_REAL_LLM_CALLS", raising=False)
    wrapper = CappedGeminiClient(_FakeGenAIClient(_VALID_XML))
    assert wrapper.generate(model="m", prompt="p", temperature=0) == _VALID_XML


def test_the_module_imports_without_the_sdk_installed():
    """The SDK import is LAZY — inside the factory, never at module level.

    ⚑ TECHNIQUE SUPERSEDED 2026-07-25 — the assertion changed; the PROPERTY did not.

    **The old technique** asserted ``importlib.util.find_spec("google.genai") is None``
    and reasoned: *"in this environment google-genai is GENUINELY NOT installed, so a
    successful import PROVES the SDK import is lazy."* That inference was sound **only
    while the SDK was absent** — it proved laziness by observing that an eager import
    would have failed.

    **Why it broke**: ``google-genai`` is now legitimately installed. ``requirements.txt``
    declares ``google-genai>=1.0.0`` (added by register #18's pass), so a plain
    ``pip install -r requirements.txt`` produces exactly that state. The old assertion
    therefore encoded an **environmental precondition as an invariant**, and the manifest
    and the test came to contradict each other: the manifest declares the SDK a
    dependency, the test asserted its absence.

    ⚑ **Worse than merely failing — with the SDK present the old technique CANNOT prove
    the property at all.** A successful import no longer discriminates lazy from eager,
    so the test would have been vacuous even if its precondition were relaxed rather
    than fixed.

    **Why the new technique is better regardless of environment**: it inspects the
    module's own AST for the fact the test always actually wanted — that **every**
    ``google``-rooted import sits **inside a function body**, never at module level. That
    is **environment-independent** (true with or without the SDK installed), **direct**
    (it checks the structure, not a side effect of it), and **non-vacuous** (an eager
    import fails it immediately, and deleting the import entirely also fails).

    ⚑ The enclosing function is asserted to exist but is **not pinned by name**: the lazy
    import currently lives in ``_capped_client_over_real_genai`` (the real-client
    construction helper the guarded factory delegates to), **not** in
    ``build_gemini_client`` itself. Pinning a private helper's name would make an
    ordinary rename fail a test that has nothing to say about naming — the property is
    *"inside some function"*, and that is what is asserted.

    ⚑ **The test NAME is retained deliberately**: it names the *property* — the module is
    importable without the SDK — which is unchanged and still exactly what is guaranteed.
    Only the *evidence* changed, so the name does not misdescribe the test.
    """
    import ast
    import importlib
    from pathlib import Path

    source = (Path(__file__).resolve().parents[1] / "llm_client.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    def _imports(node, inside_function):
        """Yield (import_node, inside_function) for every import, scope-aware."""
        for child in ast.iter_child_nodes(node):
            nested = inside_function or isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                yield child, inside_function
            yield from _imports(child, nested)

    def _roots(import_node):
        if isinstance(import_node, ast.Import):
            return {alias.name.split(".")[0] for alias in import_node.names}
        return {(import_node.module or "").split(".")[0]}

    google_imports = [
        (node, in_func) for node, in_func in _imports(tree, False) if "google" in _roots(node)
    ]

    # (1) the load-bearing half — no eager SDK import anywhere at module level.
    module_level = sorted(node.lineno for node, in_func in google_imports if not in_func)
    assert not module_level, (
        f"the SDK must NOT be imported at module level; found at line(s) {module_level}"
    )

    # (2) non-vacuity — the lazy import must actually EXIST inside a function, so that
    #     deleting it (or moving it out of the module) fails rather than passing silently.
    assert google_imports, "expected a lazy `google` import inside a function; found none"

    # The behavioural half, unchanged and still environment-independent.
    mod = importlib.import_module("backend.app.llm_client")
    assert hasattr(mod, "CappedGeminiClient") and hasattr(mod, "build_gemini_client")
