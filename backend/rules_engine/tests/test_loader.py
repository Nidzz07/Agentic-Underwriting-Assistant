"""Tests for RulebookLoader (Step 6).

Maps: NFR-RULES-BR1-1 (load-time demographic/unknown ``input_fields`` reject),
NFR-RULES-SCHEMA-1 (operator↔threshold-shape reject), NFR-RULES-AUDIT-1
(deterministic ``content_hash`` recomputed + tamper-verified at load),
NFR-RULES-AUDIT-2 (append-only immutable versions — a published version is never
mutated; old versions stay loadable; a frozen Rulebook cannot be mutated).

Load-rejection is proved BOTH as a Hypothesis universal-quantifier (∀
demographic/unknown ``input_fields`` → load rejects) AND with curated bad
rulebooks as regression anchors (Q2 + Q4 — curated ON TOP OF the property).
"""
from __future__ import annotations

from decimal import Decimal

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.rules_engine.canon_adapter import RulebookCanonAdapter
from backend.rules_engine.loader import (
    RulebookLoadError,
    RulebookLoader,
    RulebookNotFoundError,
    build_rulebook,
)
from backend.rules_engine.rulebook_schema import ALLOWED_INPUT_FIELDS, Rulebook


# --------------------------------------------------------------------------
# Raw (dict/YAML) rulebook builders — thresholds authored as STRINGS so pyyaml
# never yields a float (CON-DET-1); the Number type rejects IEEE float.
# --------------------------------------------------------------------------
def _valid_rule_dict(**over):
    d = dict(
        rule_id="DTI-1",
        category="financial_dti",
        input_fields=["dti_ratio"],
        operator="lte",
        threshold="0.40",
        outcome="decline_fail",
        rationale_message="DTI over ceiling",
        irdai_ref="",
    )
    d.update(over)
    return d


def _valid_rulebook_dict(rules=None, version="1.0.0", content_hash=""):
    return dict(
        rulebook_version=version,
        content_hash=content_hash,
        rules=rules if rules is not None else [_valid_rule_dict()],
        confidence_bands=dict(high_margin="0.15", low_margin="0.03"),
    )


def _write(dir_path, version, data=None):
    data = data if data is not None else _valid_rulebook_dict(version=version)
    path = dir_path / f"{version}.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# build_rulebook (pure core) — validate + freeze + stamp hash
# --------------------------------------------------------------------------
def test_build_valid_rulebook_stamps_computed_hash():
    rb = build_rulebook(_valid_rulebook_dict())
    assert isinstance(rb, Rulebook)
    assert len(rb.content_hash) == 64  # sha256 hex
    assert rb.content_hash == RulebookCanonAdapter.content_hash(rb)


def test_build_rejects_non_mapping_source():
    with pytest.raises(RulebookLoadError):
        build_rulebook("not-a-mapping")  # type: ignore[arg-type]


def test_build_tamper_mismatch_rejected():
    good = build_rulebook(_valid_rulebook_dict())
    tampered = _valid_rulebook_dict(content_hash="0" * 64)
    with pytest.raises(RulebookLoadError, match="content_hash mismatch"):
        build_rulebook(tampered)
    # sanity: the good hash is not all-zeros
    assert good.content_hash != "0" * 64


def test_build_accepts_matching_declared_hash():
    computed = build_rulebook(_valid_rulebook_dict()).content_hash
    rb = build_rulebook(_valid_rulebook_dict(content_hash=computed))
    assert rb.content_hash == computed


# --------------------------------------------------------------------------
# Load-time rejection — curated bad rulebooks (BR1-1 / SCHEMA-1)
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "bad_field",
    ["demographics.gender", "demographics.city", "gender", "city", "full_name", "name", "region"],
)
def test_load_rejects_demographic_or_unknown_input_field(bad_field):
    data = _valid_rulebook_dict(rules=[_valid_rule_dict(input_fields=[bad_field])])
    with pytest.raises(RulebookLoadError):
        build_rulebook(data)


def test_load_rejects_empty_input_fields():
    data = _valid_rulebook_dict(rules=[_valid_rule_dict(input_fields=[])])
    with pytest.raises(RulebookLoadError):
        build_rulebook(data)


@pytest.mark.parametrize(
    "operator,threshold",
    [
        ("lte", ["a", "b"]),               # numeric op with a set threshold
        ("between", "0.40"),                # between needs a DecimalRange
        ("in", "0.40"),                     # in needs a list/set
        ("gt", dict(low="1", low_inclusive=True, high="2", high_inclusive=True)),  # gt needs scalar
        ("eq", ["x", "y"]),                  # eq needs a scalar literal, not a set
    ],
)
def test_load_rejects_operator_threshold_mismatch(operator, threshold):
    data = _valid_rulebook_dict(
        rules=[_valid_rule_dict(operator=operator, threshold=threshold)]
    )
    with pytest.raises(RulebookLoadError):
        build_rulebook(data)


def test_load_rejects_unquoted_float_threshold():
    # An unquoted YAML number parses to float -> rejected (CON-DET-1, no drift).
    data = _valid_rulebook_dict(rules=[_valid_rule_dict(threshold=0.40)])
    with pytest.raises(RulebookLoadError):
        build_rulebook(data)


# --------------------------------------------------------------------------
# Load-time rejection — Hypothesis universal-quantifier (BR1-1)
# --------------------------------------------------------------------------
_DEMOGRAPHIC_PATHS = [
    "demographics", "demographics.gender", "demographics.city", "demographics.full_name",
    "gender", "city", "full_name", "name", "ethnicity", "religion", "marital_status",
]

_bad_field = st.one_of(
    st.sampled_from(_DEMOGRAPHIC_PATHS),
    st.text(min_size=1, max_size=20).filter(lambda s: s not in ALLOWED_INPUT_FIELDS),
)


@settings(max_examples=200, deadline=None)
@given(field=_bad_field)
@pytest.mark.property
def test_forall_out_of_allowlist_field_rejected_at_load(field):
    """∀ demographic/unknown input_fields → load rejects (raises)."""
    data = _valid_rulebook_dict(rules=[_valid_rule_dict(input_fields=[field])])
    with pytest.raises(RulebookLoadError):
        build_rulebook(data)


# --------------------------------------------------------------------------
# RulebookLoader (file-backed) — resolve/verify/cache/version
# --------------------------------------------------------------------------
def test_load_valid_rulebook_from_file(tmp_path):
    _write(tmp_path, "1.0.0")
    loader = RulebookLoader(tmp_path)
    rb = loader.load_rulebook("1.0.0")
    assert rb.rulebook_version == "1.0.0"
    assert rb.rules[0].rule_id == "DTI-1"
    assert rb.rules[0].threshold == Decimal("0.40")


def test_missing_version_raises_not_found(tmp_path):
    _write(tmp_path, "1.0.0")
    loader = RulebookLoader(tmp_path)
    with pytest.raises(RulebookNotFoundError):
        loader.load_rulebook("9.9.9")


def test_file_version_mismatch_rejected(tmp_path):
    # File named 1.0.0.yaml but declares a different rulebook_version.
    _write(tmp_path, "1.0.0", data=_valid_rulebook_dict(version="2.0.0"))
    loader = RulebookLoader(tmp_path)
    with pytest.raises(RulebookLoadError, match="version mismatch"):
        loader.load_rulebook("1.0.0")


def test_append_only_two_versions_both_loadable_distinct_hash(tmp_path):
    _write(tmp_path, "1.0.0")
    # v1.1.0 changes the threshold -> different content_hash (append-only, not mutate).
    _write(
        tmp_path, "1.1.0",
        data=_valid_rulebook_dict(version="1.1.0", rules=[_valid_rule_dict(threshold="0.35")]),
    )
    loader = RulebookLoader(tmp_path)
    v1 = loader.load_rulebook("1.0.0")
    v11 = loader.load_rulebook("1.1.0")
    # Old version STILL loadable after the newer one exists.
    assert loader.load_rulebook("1.0.0").content_hash == v1.content_hash
    assert v1.content_hash != v11.content_hash


def test_loaded_rulebook_is_frozen_immutable(tmp_path):
    _write(tmp_path, "1.0.0")
    rb = RulebookLoader(tmp_path).load_rulebook("1.0.0")
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        rb.rulebook_version = "9.9.9"  # frozen -> cannot mutate a published version


def test_cache_returns_same_frozen_object(tmp_path):
    _write(tmp_path, "1.0.0")
    loader = RulebookLoader(tmp_path)
    assert loader.load_rulebook("1.0.0") is loader.load_rulebook("1.0.0")
