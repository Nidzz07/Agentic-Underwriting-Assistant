"""RulebookLoader — load + validate + freeze + version a Rulebook (Step 6).

NFR Design §4/§5. ``pyyaml`` ``safe_load`` reads a versioned YAML source; the
Pydantic-v2 ``Rule`` / ``Rulebook`` schema (the single structural gate) validates
**every** rule at load — a **demographic/unknown ``input_fields``** entry
(NFR-RULES-BR1-1) or an **operator↔threshold-shape mismatch** (NFR-RULES-SCHEMA-1)
makes the rulebook **fail to load** (it never reaches ``evaluate``). The
``content_hash`` is recomputed over the canonical bytes (NFR-RULES-AUDIT-1) and,
if the source declared one, **verified** (tamper-evidence). Versions are
**append-only + immutable** (NFR-RULES-AUDIT-2): each ``{version}.yaml`` is a
distinct frozen source; a published version is never mutated in place — a change
is a new file/semver — and old versions stay loadable.

Thresholds MUST be authored as strings/typed literals in YAML (e.g.
``threshold: "0.40"``); an unquoted YAML number parses to IEEE ``float`` and is
**rejected** by the ``Number`` type (CON-DET-1 — no boundary drift).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from backend.rules_engine.canon_adapter import RulebookCanonAdapter
from backend.rules_engine.rulebook_schema import Rulebook


class RulebookLoadError(Exception):
    """A rulebook failed to load — schema/validation reject or tamper mismatch."""


class RulebookNotFoundError(RulebookLoadError):
    """No rulebook source exists for the requested version."""


def build_rulebook(data: Any) -> Rulebook:
    """Validate a raw rulebook mapping, freeze it, and stamp its ``content_hash``.

    Pure (no I/O) so the load-time universal-quantifier (∀ bad ``input_fields`` →
    reject) can be exercised without disk. Every Pydantic validation failure —
    the BR1-1 allowlist reject and the SCHEMA-1 operator↔threshold reject
    included — is surfaced as a single :class:`RulebookLoadError`, so a
    malformed/adversarial rulebook cannot reach ``evaluate``.
    """
    if not isinstance(data, dict):
        raise RulebookLoadError("rulebook source must be a mapping")
    declared_hash = data.get("content_hash", "") or ""
    payload = {**data, "content_hash": ""}
    try:
        rulebook = Rulebook(**payload)
    except ValidationError as exc:  # BR1-1 / SCHEMA-1 / any schema violation
        raise RulebookLoadError(f"rulebook failed schema validation: {exc}") from exc
    computed = RulebookCanonAdapter.content_hash(rulebook)
    if declared_hash and declared_hash != computed:  # tamper-evidence (AUDIT-1)
        raise RulebookLoadError(
            f"content_hash mismatch: declared {declared_hash!r} != computed {computed!r}"
        )
    # content_hash is NOT part of the canonical form, so stamping it does not
    # change the hash. model_copy returns a new frozen instance.
    return rulebook.model_copy(update={"content_hash": computed})


class RulebookLoader:
    """Load immutable, hash-verified rulebooks from a versioned YAML directory.

    Append-only: each ``{version}.yaml`` is a distinct immutable source. Loaded
    versions are cached, so repeated loads of a version return the same frozen
    object (a published version is never re-read/mutated within a run).
    """

    def __init__(self, rulebook_dir: str | Path) -> None:
        self._dir = Path(rulebook_dir)
        self._cache: dict[str, Rulebook] = {}

    def load_rulebook(self, version: str) -> Rulebook:
        """Resolve a semver to its one immutable, hash-verified :class:`Rulebook`."""
        cached = self._cache.get(version)
        if cached is not None:
            return cached
        path = self._dir / f"{version}.yaml"
        if not path.is_file():
            raise RulebookNotFoundError(f"no rulebook for version {version!r} at {path}")
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        rulebook = build_rulebook(data)
        if rulebook.rulebook_version != version:  # the file must declare its own version
            raise RulebookLoadError(
                f"version mismatch: requested {version!r}, "
                f"file declares {rulebook.rulebook_version!r}"
            )
        self._cache[version] = rulebook
        return rulebook
