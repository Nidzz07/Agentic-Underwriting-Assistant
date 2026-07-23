"""C2 RulebookPublisher — validate-then-append-only rulebook publish (P1).

FR-RULES-6 / CON-DET-1. :meth:`publish`:

1. **pure-validate FIRST** via ``rules_engine.build_rulebook`` (the SOLE validator —
   schema + hash + the loader's own checks) and confirm the declared
   ``rulebook_version`` equals the target — BEFORE writing anything, so a reject
   leaves **no file** (NFR-ADMIN-PUBLISH-1 c/d);
2. **atomic exclusive-create** write of ``{version}.yaml`` (``content_hash`` blanked so
   the loader recomputes + stamps) via ``open(path, "x")`` — refuses an existing
   version and **never touches** the existing file (append-only teeth,
   NFR-ADMIN-PUBLISH-1 b);
3. **validate-by-load** via ``RulebookLoader.load_rulebook`` (confirms on-disk
   loadability, NFR-ADMIN-PUBLISH-1 a).

Reference-not-own: ``build_rulebook``/``RulebookLoader`` is the SOLE rulebook validator
(NFR-ADMIN-PUBVALID-1); no local schema/allowlist/threshold/hasher here. No LLM.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from backend.rules_engine.loader import (
    RulebookLoader,
    RulebookLoadError,
    build_rulebook,
)
from backend.admin_cli.exceptions import RulebookPublishError


class RulebookPublisher:
    """Publish an operator-authored rulebook source as an immutable ``{version}.yaml``,
    delegating all validation to rules-engine."""

    def __init__(self, rulebook_dir: str | Path) -> None:
        self._dir = Path(rulebook_dir)

    def publish(self, version: str, source_text: str) -> None:
        """Validate then append-only-publish ``source_text`` as ``{version}.yaml``.

        Raises :class:`RulebookPublishError` on any validation reject, a
        declared-version mismatch, or an already-existing version (never mutating it)."""
        # 1. pure-validate FIRST (sole validator) — no file written yet.
        try:
            data = yaml.safe_load(source_text)
        except yaml.YAMLError as exc:
            raise RulebookPublishError(f"rulebook validation failed: {exc}") from exc
        try:
            rulebook = build_rulebook(data)
        except RulebookLoadError as exc:
            raise RulebookPublishError(f"rulebook validation failed: {exc}") from exc
        if rulebook.rulebook_version != version:
            raise RulebookPublishError(
                f"declared version {rulebook.rulebook_version!r} != target {version!r}"
            )

        # 2. atomic exclusive-create write (append-only no-overwrite guard, Q3-A).
        path = self._dir / f"{version}.yaml"
        payload = {**data, "content_hash": ""}  # loader recomputes + stamps
        try:
            with open(path, "x", encoding="utf-8") as handle:
                yaml.safe_dump(payload, handle, sort_keys=False)
        except FileExistsError as exc:
            raise RulebookPublishError(
                f"rulebook version {version} already exists"
            ) from exc

        # 3. validate-by-load teeth (confirms on-disk loadability of the just-written
        # bytes; the same content already passed build_rulebook in step 1).
        try:
            RulebookLoader(self._dir).load_rulebook(version)
        except RulebookLoadError as exc:  # pragma: no cover - identical bytes just validated
            raise RulebookPublishError(f"rulebook validation failed: {exc}") from exc
