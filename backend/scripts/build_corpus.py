"""TIER-B STAGE 1 — the GUARDED out-of-band corpus build entrypoint (register #3).

╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  DEFAULT MODE IS OFFLINE AND COSTS NOTHING. The real path is opt-in and BILLABLE.         ║
║                                                                                          ║
║  Three modes, safest first:                                                              ║
║    --dry-run    ZERO cost. Runs the pipeline with a COUNTING offline double and reports   ║
║                 the exact number of model calls a real run would make. Writes NOTHING.    ║
║    (default)    ZERO cost. Full pipeline with the offline double; writes the artifacts.   ║
║                 This is the Q6(c) SHAPE-PILOT.                                            ║
║    --real-llm   BILLABLE. Requires ALSO ALLOW_REAL_LLM_CALLS=true, an explicit            ║
║                 --model-id (non-floating) and an explicit --max-llm-calls.                ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

**Why this exists rather than `corpus_generator/build.py`** (authorization plan Q4-b). U14's
own `build.py` wires a bare `_GeminiLLMClient` that takes the raw API key and has **no call
cap, no `ALLOW_REAL_LLM_CALLS` gate and no logging** — register #18's guardrails do not cover
it. It cannot simply import `backend/app/llm_client.py` either: that is a frozen unit
importing the composition root, the direction every structural scan exists to prevent. So the
guarded path lives **here**, in `backend/scripts/` — the cross-unit orchestrator location
established by `run_migrations.py` (#8) and `seed_demo_cases.py` — and drives the frozen
`CorpusGenerator` through its **injected** `llm_client` seam, editing no frozen unit.

⚑ **DISCLOSED COST of that choice**: `corpus_generator/build.py` REMAINS ON DISK, unused,
coverage-omitted and **still unguarded**. It is superseded, not deleted. That is strictly no
worse than before this script existed, but it is a real residual and is recorded, not glossed.

**Guardrails (Q3-b)** — the real path goes EXCLUSIVELY through `build_gemini_client`, so it
inherits both #18 gates (`ALLOW_REAL_LLM_CALLS` exactly `"true"`, and the non-empty-key
fail-closed check). The cap is passed EXPLICITLY; the `max_calls=20` default in
`backend/app/llm_client.py` is never relied upon and never changed. Every switch is a CLI
argument — **never a new active `.env.example` key**, which would break frozen U16's
`test_env_example_matches_settings_fields`.

**Model id (Q5)** — the real path REQUIRES an explicit, non-floating `--model-id`. A floating
alias would be stamped into `CorpusManifest.model_version`, which is permanent provenance, and
`documents_text` is inside the manifest's `content_hash` — so prose drift would change the
corpus's identity untraceably (register #22 applied to U14).

Run (out of band)::

    python -m backend.scripts.build_corpus --dry-run            # zero cost, counts only
    python -m backend.scripts.build_corpus --out .tmp-corpus    # zero cost, shape-pilot
    ALLOW_REAL_LLM_CALLS=true python -m backend.scripts.build_corpus \
        --real-llm --model-id <pinned> --max-llm-calls <n> --out corpus
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path

from backend.app.llm_client import build_gemini_client
from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.generator import CorpusGenerator, CorpusOutput
from backend.corpus_generator.manifest_builder import (
    build_manifest,
    corpus_to_json,
    manifest_to_json,
)
from backend.secrets_config import get_settings

#: Stamped into the manifest on every offline run so a placeholder corpus can never be
#: mistaken for a real one, anywhere it travels.
OFFLINE_MODEL_ID = "OFFLINE-DOUBLE-NOT-A-REAL-LLM"

#: Floating aliases refused on the real path (Q5). Not exhaustive by design — the check is a
#: guardrail against the KNOWN aliases, backed by the explicit-argument requirement.
FLOATING_ALIASES = frozenset(
    {
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    }
)

DEFAULT_SEED = 42
RULEBOOK_VERSION = "1.0.0"
ENGINE_VERSION = "corpus-build-1"


class _OfflineLLMClient:
    """A DETERMINISTIC OFFLINE STAND-IN — not a model, not inference, not for production.

    Satisfies the frozen ``LLMClient`` seam ``generate(*, model, prompt, temperature) -> str``
    and counts every call, so ``--dry-run`` can MEASURE the exact number of model calls a real
    run would make rather than deriving it from a ``3 x N`` formula.

    ⚑ Defined LOCALLY here, deliberately: a production script must never import a frozen
    unit's ``tests/conftest.py`` (which is where ``CapturingLLMClient`` lives).
    """

    def __init__(self) -> None:
        self.calls = 0

    def generate(self, *, model: str, prompt: str, temperature: float) -> str:
        self.calls += 1
        return (
            "OFFLINE PLACEHOLDER DOCUMENT - generated without a language model by the "
            "tier-B corpus shape-pilot. It carries no underwriting meaning and must never "
            "be read as real document text."
        )


def _rulebook_dir() -> str:
    return str(Path(__file__).resolve().parents[1] / "rules_engine" / "rulebook")


def _google_genai_version() -> str:
    """The installed SDK version for the real-path audit stamp (Q5-d / #22's precedent)."""
    try:
        return _pkg_version("google-genai")
    except PackageNotFoundError:  # pragma: no cover - only on the real path
        return "unknown"


def _build_config(args: argparse.Namespace, model_id: str) -> GenerationConfig:
    return GenerationConfig(
        seed=args.seed,
        rulebook_version=args.rulebook_version,
        rulebook_dir=_rulebook_dir(),
        engine_version=args.engine_version,
        model_id=model_id,
        attempt_budget=args.attempt_budget,
        min_profiles=args.min_profiles,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the tier-B synthetic corpus (Stage 1).")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=str, default="corpus")
    parser.add_argument("--rulebook-version", type=str, default=RULEBOOK_VERSION)
    parser.add_argument("--engine-version", type=str, default=ENGINE_VERSION)
    parser.add_argument("--min-profiles", type=int, default=300)
    parser.add_argument("--attempt-budget", type=int, default=100_000)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ZERO COST: measure and report the model-call count; write nothing.",
    )
    parser.add_argument(
        "--real-llm",
        action="store_true",
        help="OPT-IN: generate with the REAL Gemini client (SPENDS MONEY). ALSO requires "
        "ALLOW_REAL_LLM_CALLS=true - two independent gates.",
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default=None,
        help="REQUIRED with --real-llm: an explicit, NON-FLOATING model id.",
    )
    parser.add_argument(
        "--max-llm-calls",
        type=int,
        default=None,
        help="REQUIRED with --real-llm: the per-process real-call cap, passed explicitly.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    out_dir = Path(args.out)

    if args.real_llm:
        # -- the ONLY spend-capable branch; every check fires BEFORE a client is built --
        if not args.model_id:
            parser.error("--real-llm requires an explicit --model-id (no default, Q5)")
        if args.model_id in FLOATING_ALIASES:
            parser.error(
                f"refusing the floating alias {args.model_id!r}: the corpus manifest stamps "
                "model_version permanently and documents_text is inside its content_hash, so "
                "a floating id makes prose drift untraceable (Q5 / register #22). Pass the "
                "dated id confirmed against models.list."
            )
        if args.max_llm_calls is None:
            parser.error("--real-llm requires an explicit --max-llm-calls (no default, Q3)")

        model_id = args.model_id
        # build_gemini_client owns BOTH #18 gates: ALLOW_REAL_LLM_CALLS == "true" exactly,
        # and the non-empty-key fail-closed check. max_calls is passed EXPLICITLY - the
        # wrapper's own default of 20 is never relied upon and never changed.
        client = build_gemini_client(
            get_settings(), model_id=model_id, max_calls=args.max_llm_calls
        )
        model_version = f"{model_id}+google-genai-{_google_genai_version()}"
        print("=" * 78)
        print("TIER-B CORPUS BUILD -- REAL LLM CALLS -- THIS WILL SPEND MONEY")
        print(f"  model={model_id!r}  cap={args.max_llm_calls}  stamp={model_version!r}")
        print("=" * 78)
    else:
        model_id = OFFLINE_MODEL_ID
        client = _OfflineLLMClient()
        model_version = OFFLINE_MODEL_ID
        banner = "DRY RUN -- measuring model calls, WRITING NOTHING" if args.dry_run else (
            "OFFLINE SHAPE-PILOT -- placeholder prose, NOT real model output"
        )
        print("=" * 78)
        print(f"TIER-B CORPUS BUILD -- {banner}")
        print("=" * 78)

    config = _build_config(args, model_id)
    generator = CorpusGenerator(config, llm_client=client)
    timestamp = datetime.now(timezone.utc).isoformat()
    output: CorpusOutput = generator.generate(generation_timestamp=timestamp)

    if args.dry_run:
        calls = getattr(client, "calls", 0)
        print(f"\nDRY RUN COMPLETE -- no file written, no money spent.")
        print(f"  profiles generated : {output.manifest.profile_count}")
        print(f"  MODEL CALLS a real run would make: {calls}")
        print(f"  suggested --max-llm-calls (10% headroom): {int(calls * 1.1) + 1}")
        return 0

    # Re-stamp the manifest with the composed model_version. ``CorpusGenerator`` stamps
    # ``config.model_id`` (which must stay the bare id the SDK is called with), so the
    # SDK-version suffix is applied by calling the frozen ``build_manifest`` again -
    # call-only, editing nothing. ``content_hash`` is computed from the RECORDS, so it is
    # unchanged by this re-stamp.
    manifest = build_manifest(
        output.records,
        config,
        generation_timestamp=timestamp,
        model_version=model_version,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "profiles.json").write_text(corpus_to_json(output.records), encoding="utf-8")
    (out_dir / "manifest.json").write_text(manifest_to_json(manifest), encoding="utf-8")

    print(f"\nfroze {manifest.profile_count} profiles to {out_dir}/")
    print(f"  content_hash  : {manifest.content_hash}")
    print(f"  model_version : {manifest.model_version}")
    print(f"  class_counts  : {manifest.class_counts}")
    print(f"  edges         : {manifest.edge_case_checklist}")
    if args.real_llm:
        made = getattr(client, "call_count", None)
        if made is not None:
            print(f"\nREAL LLM calls made this run: {made} (cap {args.max_llm_calls}).")
    else:
        print("\nReminder: this prose is a PLACEHOLDER. Not real model output.")
    return 0


if __name__ == "__main__":  # pragma: no cover - out-of-band entrypoint
    raise SystemExit(main())
