"""C5 ``SkewAudit`` — SKEW-BAND-1 + SKEW-EDGE-1, conjunctive but INDEPENDENT (Fold 2)."""
from __future__ import annotations

from decimal import Decimal

import pytest

from backend.corpus_generator.config import DATA2_EDGE_CASES, GenerationConfig
from backend.corpus_generator.exceptions import SkewAuditError
from backend.corpus_generator.skew_audit import (
    SkewAudit,
    band_lower_edge_count,
    band_ok,
    class_proportions,
    edge_checklist,
    edges_ok,
)

ALL_EDGES = set(DATA2_EDGE_CASES)
ON_BAND = {"APPROVE": 40, "REFER": 35, "DECLINE-RECOMMEND": 25}       # 0.40/0.35/0.25
OFF_BAND = {"APPROVE": 50, "REFER": 25, "DECLINE-RECOMMEND": 25}      # APPROVE off by 0.10


def _config(**overrides) -> GenerationConfig:
    base = dict(
        seed=1, rulebook_version="1.0.0", rulebook_dir="/x", engine_version="e",
        model_id="m", attempt_budget=1000, min_profiles=300,
    )
    base.update(overrides)
    return GenerationConfig(**base)


# --- SKEW-BAND-1 -----------------------------------------------------------
def test_band_ok_passes_within_and_fails_outside_the_band():
    cfg = _config()
    assert band_ok(ON_BAND, cfg) is True
    assert band_ok(OFF_BAND, cfg) is False


def test_band_computation_does_not_consult_the_edge_checklist():
    # band_ok's signature takes ONLY counts + config — it cannot see edges (independence)
    cfg = _config()
    assert band_ok(ON_BAND, cfg) is True    # regardless of any edge state
    assert band_ok(OFF_BAND, cfg) is False


def test_class_proportions_exact_decimal():
    props = class_proportions(ON_BAND)
    assert props["APPROVE"] == Decimal(40) / Decimal(100)
    assert class_proportions({"A": 0})["A"] == Decimal(0)


# --- SKEW-EDGE-1 -----------------------------------------------------------
def test_edges_ok_requires_every_required_edge():
    cfg = _config()
    assert edges_ok(ALL_EDGES, cfg) is True
    assert edges_ok(ALL_EDGES - {"bmi_30"}, cfg) is False       # any one absent -> fail


def test_edge_checklist_reports_each_required_edge():
    cfg = _config(required_edge_cases=("age_18", "bmi_30"))
    checklist = edge_checklist({"age_18"}, cfg)
    assert checklist == {"age_18": True, "bmi_30": False}


# --- conjunction independence (both directions) ----------------------------
def test_audit_passes_only_when_both_hold():
    SkewAudit().audit(class_counts=ON_BAND, present_edges=ALL_EDGES, config=_config())


def test_audit_raises_on_band_failure_even_with_all_edges_present():
    # independence direction 1: edges OK, band off -> still raises
    with pytest.raises(SkewAuditError):
        SkewAudit().audit(class_counts=OFF_BAND, present_edges=ALL_EDGES, config=_config())


def test_audit_raises_on_missing_edge_even_when_band_is_satisfied():
    # independence direction 2: band OK, one edge missing -> still raises (never averaged)
    with pytest.raises(SkewAuditError):
        SkewAudit().audit(
            class_counts=ON_BAND, present_edges=ALL_EDGES - {"dti_40"}, config=_config()
        )


# --- ND-Fold-1 band lower-edge arithmetic ----------------------------------
def test_band_lower_edge_uses_the_lower_edge_not_the_center():
    cfg = _config(min_profiles=300)   # APPROVE target 0.40, tol 0.03
    # lower edge = ceil(300 * (0.40 - 0.03)) = ceil(111) = 111  (NOT the center 120)
    assert band_lower_edge_count(Decimal("0.40"), cfg) == 111


def test_band_lower_edge_floors_at_zero():
    cfg = _config(min_profiles=10, tolerance_pp=Decimal("50"))
    assert band_lower_edge_count(Decimal("0.40"), cfg) == 0
