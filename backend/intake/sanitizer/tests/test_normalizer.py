"""Tests for ObfuscationNormalizer (Step 6).

Maps: NFR-INT-SEC1-NEUT (obfuscation robustness) + CON-DET-1 (deterministic
pre-pass). The normalizer builds a DETECTION-ONLY view via a fixed pipeline
(NFKC -> case-fold -> collapse-whitespace -> strip-zero-width) and an ORIGIN
INDEX MAP so neutralization edits map back to the ORIGINAL span. The normalized
view is transient — it NEVER becomes clean_text.

Zero-width / format code points are written as explicit escapes (\\u200b ZWSP,
\\u200c ZWNJ, \\ufeff BOM, \\u2060 WORD JOINER) so the test text is unambiguous.
"""
from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.intake.sanitizer.normalizer import ObfuscationNormalizer

NORM = ObfuscationNormalizer()

ZWSP = "​"  # zero-width space
ZWNJ = "‌"  # zero-width non-joiner
BOM = "﻿"   # BOM / zero-width no-break space
WJ = "⁠"    # word joiner


def test_nfkc_folds_fullwidth_homoglyphs():
    # Fullwidth "IGNORE" -> ascii "ignore" (NFKC + casefold).
    view = NORM.normalize("ＩＧＮＯＲＥ")  # IGNORE fullwidth
    assert view.text == "ignore"


def test_casefold_lowercases():
    assert NORM.normalize("IGNORE Previous").text == "ignore previous"


def test_collapse_whitespace_runs_to_single_space():
    assert NORM.normalize("a\t\n   b").text == "a b"


def test_strip_zero_width_and_format_chars():
    # ZWSP/ZWNJ inside a word are removed so "ig<zwsp>no<zwnj>re" folds to "ignore".
    assert NORM.normalize(f"ig{ZWSP}no{ZWNJ}re").text == "ignore"
    assert NORM.normalize(f"a{BOM}b").text == "ab"


def test_detection_only_does_not_mutate_original():
    original = f"IG{ZWSP}NORE  previous"
    _ = NORM.normalize(original)
    assert original == f"IG{ZWSP}NORE  previous"  # input untouched


def test_deterministic_same_input_same_view():
    original = "ＡＣＴ  as\tSYSTEM"  # fullwidth ACT + spaces
    a = NORM.normalize(original)
    b = NORM.normalize(original)
    assert a.text == b.text
    assert a.origin == b.origin


def test_origin_map_maps_normalized_span_back_to_original():
    original = f"IG{ZWSP}NORE previous instructions"
    view = NORM.normalize(original)
    assert view.text == "ignore previous instructions"
    # The normalized substring "ignore" (0:6) must map back to the original
    # slice that INCLUDES the zero-width char.
    os, oe = view.original_span(0, 6)
    assert original[os:oe] == f"IG{ZWSP}NORE"


def test_original_span_empty_range_is_degenerate():
    view = NORM.normalize("ignore")
    assert view.original_span(3, 3) == (3, 3)  # empty normalized range
    # empty range at the very end maps to original_len
    empty = NORM.normalize("")
    assert empty.original_span(0, 0) == (0, 0)


def test_empty_and_all_stripped_inputs():
    assert NORM.normalize("").text == ""
    view = NORM.normalize(f"{ZWSP}{BOM}{WJ}")  # all format chars
    assert view.text == ""


@pytest.mark.property
@settings(max_examples=200)
@given(text=st.text(max_size=60))
def test_origin_indices_are_monotonic_and_in_bounds(text):
    view = NORM.normalize(text)
    assert len(view.origin) == len(view.text)
    prev = -1
    for oi in view.origin:
        assert 0 <= oi < len(text)
        assert oi >= prev  # non-decreasing provenance
        prev = oi
    # a span over the whole normalized view maps to a valid original slice
    if view.text:
        os, oe = view.original_span(0, len(view.text))
        assert 0 <= os <= oe <= len(text)
