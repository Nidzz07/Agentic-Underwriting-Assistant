"""Tier-B OUT-OF-BAND build entrypoint — the real full-corpus run (NOT CI).

This module wires the **real** google-genai client to the ``LLMClient`` seam and
reads ``GEMINI_API_KEY`` via ``secrets-config``, generates the full 300+ corpus, and
freezes ``corpus/profiles.json`` + ``corpus/manifest.json``. It is invoked
**manually / in a dedicated build job**, never as a collected pytest test (Q4), and
is **omitted from unit coverage** (Q5 — like ``pg_repository.py``). All pure-logic
C1–C8 modules stay unit-covered; only the live-Gemini wiring + full run live here.

Reference-not-own holds: it consumes ``secrets_config`` (the key) and
``memo_agent_core``'s seam shape — editing neither. ``temperature=0`` remains the
seam's single central discipline (``document_text_generator._PROSE_TEMPERATURE``).

Run (out of band):
    python -m backend.corpus_generator.build --seed 42 --out corpus
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.generator import CorpusGenerator
from backend.corpus_generator.manifest_builder import corpus_to_json, manifest_to_json


class _GeminiLLMClient:
    """Adapts the real google-genai client to the minimal ``LLMClient`` seam."""

    def __init__(self, api_key: str) -> None:
        from google import genai  # lazy — only needed for the live tier-B run

        self._client = genai.Client(api_key=api_key)

    def generate(self, *, model: str, prompt: str, temperature: float) -> str:
        from google.genai import types  # lazy import

        response = self._client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature),
        )
        return response.text or ""


def _default_rulebook_dir() -> str:
    return str(Path(__file__).resolve().parents[1] / "rules_engine" / "rulebook")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the frozen synthetic corpus (tier B).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="corpus")
    parser.add_argument("--rulebook-version", type=str, default="1.0.0")
    parser.add_argument("--engine-version", type=str, default="corpus-build-1")
    parser.add_argument("--model-id", type=str, default="gemini-2.5-flash")
    parser.add_argument("--min-profiles", type=int, default=300)
    parser.add_argument("--attempt-budget", type=int, default=100_000)
    args = parser.parse_args(argv)

    # SEC-3: the key is read via secrets-config, never a literal here.
    from backend.secrets_config.settings import get_settings

    settings = get_settings()
    client = _GeminiLLMClient(settings.GEMINI_API_KEY)

    config = GenerationConfig(
        seed=args.seed,
        rulebook_version=args.rulebook_version,
        rulebook_dir=_default_rulebook_dir(),
        engine_version=args.engine_version,
        model_id=args.model_id,
        attempt_budget=args.attempt_budget,
        min_profiles=args.min_profiles,
    )

    generator = CorpusGenerator(config, llm_client=client)
    timestamp = datetime.now(timezone.utc).isoformat()
    output = generator.generate(generation_timestamp=timestamp)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "profiles.json").write_text(corpus_to_json(output.records), encoding="utf-8")
    (out_dir / "manifest.json").write_text(manifest_to_json(output.manifest), encoding="utf-8")

    print(
        f"froze {output.manifest.profile_count} profiles to {out_dir}/ "
        f"(content_hash={output.manifest.content_hash})"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - out-of-band entrypoint
    raise SystemExit(main())
