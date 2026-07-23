"""C2 RulebookPublisher — validate-then-append-only publish (NFR-ADMIN-PUBLISH-1, tier U).

Uses the frozen, known-valid ``1.0.0.yaml`` as the canonical valid source (reference-not-
own: rules-engine owns the rulebook schema; this test authors no rulebook of its own).
"""
from __future__ import annotations

import pathlib

import pytest

from backend.admin_cli.exceptions import RulebookPublishError
from backend.admin_cli.rulebook_publisher import RulebookPublisher
from backend.rules_engine.loader import RulebookLoader

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_VALID_SOURCE = _REPO_ROOT / "backend" / "rules_engine" / "rulebook" / "1.0.0.yaml"


def _valid_source_text() -> str:
    return _VALID_SOURCE.read_text(encoding="utf-8")


def test_valid_version_publishes_and_loads(tmp_path):
    RulebookPublisher(tmp_path).publish("1.0.0", _valid_source_text())
    published = tmp_path / "1.0.0.yaml"
    assert published.is_file()
    # validate-by-load succeeds (NFR-ADMIN-PUBLISH-1 a)
    rb = RulebookLoader(tmp_path).load_rulebook("1.0.0")
    assert rb.rulebook_version == "1.0.0"


def test_republish_is_rejected_and_leaves_file_byte_identical(tmp_path):
    pub = RulebookPublisher(tmp_path)
    pub.publish("1.0.0", _valid_source_text())
    before = (tmp_path / "1.0.0.yaml").read_bytes()
    # append-only teeth (NFR-ADMIN-PUBLISH-1 b) — re-publish rejected, no mutation
    with pytest.raises(RulebookPublishError, match="already exists"):
        pub.publish("1.0.0", _valid_source_text())
    after = (tmp_path / "1.0.0.yaml").read_bytes()
    assert before == after


def test_schema_invalid_source_is_rejected_with_no_file_left(tmp_path):
    with pytest.raises(RulebookPublishError, match="validation failed"):
        RulebookPublisher(tmp_path).publish("2.0.0", "{}")  # missing required fields
    assert not (tmp_path / "2.0.0.yaml").exists()  # nothing published (NFR-ADMIN-PUBLISH-1 c)


def test_malformed_yaml_source_is_rejected_with_no_file_left(tmp_path):
    with pytest.raises(RulebookPublishError, match="validation failed"):
        RulebookPublisher(tmp_path).publish("3.0.0", "key: : : not valid yaml")
    assert not (tmp_path / "3.0.0.yaml").exists()


def test_declared_version_mismatch_is_rejected(tmp_path):
    # source declares 1.0.0; target 2.0.0 (NFR-ADMIN-PUBLISH-1 d)
    with pytest.raises(RulebookPublishError, match="declared version"):
        RulebookPublisher(tmp_path).publish("2.0.0", _valid_source_text())
    assert not (tmp_path / "2.0.0.yaml").exists()
