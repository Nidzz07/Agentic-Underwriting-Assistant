"""Typed-exception taxonomy (NFR-Design §10, Q1-A) — subclass assertions."""
from __future__ import annotations

import pytest

from backend.corpus_generator.exceptions import (
    BudgetExhaustedError,
    CorpusGenerationError,
    SkewAuditError,
)


def test_subclasses_of_the_unit_base():
    assert issubclass(BudgetExhaustedError, CorpusGenerationError)
    assert issubclass(SkewAuditError, CorpusGenerationError)


def test_budget_error_catchable_as_base_and_specific():
    with pytest.raises(CorpusGenerationError):
        raise BudgetExhaustedError("boom")
    with pytest.raises(BudgetExhaustedError):
        raise BudgetExhaustedError("boom")


def test_skew_error_catchable_as_base_and_specific():
    with pytest.raises(CorpusGenerationError):
        raise SkewAuditError("boom")
    with pytest.raises(SkewAuditError):
        raise SkewAuditError("boom")


def test_the_two_subclasses_are_distinct():
    assert not issubclass(BudgetExhaustedError, SkewAuditError)
    assert not issubclass(SkewAuditError, BudgetExhaustedError)
