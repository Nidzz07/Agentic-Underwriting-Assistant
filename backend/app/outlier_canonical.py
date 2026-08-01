"""The Decimal-quantized projection that lets an ``OutlierResult`` cross the persistence boundary.

⛔ **WHY THIS MODULE EXISTS — barrier #5.** ``CanonSerAdapter.canonical_bytes`` rejects IEEE float
outright (``CanonSerError: float is not permitted; use Decimal (CON-DET-1)``), because binary
float is not portably reproducible and the audit chain's whole value is byte-reproducibility.
But **every numeric field of ``OutlierResult`` is a ``float``** — ``outlier_score`` comes from
IsolationForest, ``shap_value`` from SHAP, ``z_score`` from the corpus statistics. U24's
``pipeline.py:134`` serializes the seam's return with exactly that adapter, so **a real outlier
score could not be persisted at all**: ``CasePipeline.draft()`` raised before it ever wrote a row.

**The resolution, and why it is this one.** ``CaseSeams.score_outlier`` is typed
``Optional[object]`` and U24 serializes whatever it is handed — so handing it a Decimal-typed
projection travels U24's existing path with **no frozen unit reopened**. The alternatives each
required one: relaxing CANON-SER would reopen frozen ``common/`` *and* deliberately break
CON-DET-1; converting inside U24's pipeline, or switching that column to plain JSON, would reopen
``case_lifecycle`` a fourth time.

⚑ **WHAT THIS DOES NOT CLAIM.** This is a **quantized projection of the model's float output**.
It is **NOT** a claim that the underlying ML computation is bit-for-bit reproducible across
library versions. CANON-SER's guarantee applies to the **persisted representation** — the same
logical value serializes to the same bytes — and to nothing else. Floating-point computation is
reproducible only within a pinned ``(sklearn, numpy, platform)`` combination, which is precisely
why ``OUTLIER_MODEL_VERSION`` bundles the sklearn version into the provenance triple. **Nothing
in this stack promises cross-version FP identity, and quantization must never be read as
supplying it.**

What quantization *does* buy: two runs that compute the same score persist **identical bytes**, a
stored score reads back **unambiguously**, and the replay path has a stable value to compare.
Round-trip losslessness holds **AT the named precision** — a float carrying more than
``OUTLIER_QUANT_DECIMAL_PLACES`` significant decimals is deliberately narrowed. That narrowing is
the design, not a rounding defect.

**Location** (Q8(a)): ``backend/app/`` is the composition root and is not frozen — the layer whose
job is exactly this translation. The schema is imported **by value** from U18, which is WIRE-1's
own framing of how ``OutlierResult`` travels. Both directions live here: the seed script quantizes
on the way in, ``projections.py`` dequantizes on the way out.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any, Final

from pydantic import BaseModel, ConfigDict

from backend.outlier_model.schemas import (
    FlagDirection,
    FlaggedFeature,
    OutlierProvenance,
    OutlierResult,
)

#: The single named precision for every persisted outlier number. **Changeable in exactly one
#: place** — never spelled inline at a call site. 12 decimal places is the precision Fold A/E
#: actually observed (the reference score ``0.667071302659``), so the determinism spot-check and
#: the stored value agree by construction rather than by coincidence.
OUTLIER_QUANT_DECIMAL_PLACES: Final[int] = 12

#: The ``quantize`` exponent DERIVED from the constant above, so the two can never drift apart.
OUTLIER_QUANT_EXPONENT: Final[Decimal] = Decimal(1).scaleb(-OUTLIER_QUANT_DECIMAL_PLACES)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class QuantizedFlaggedFeature(_Frozen):
    """``FlaggedFeature`` with its two float fields projected to fixed-precision ``Decimal``."""

    feature: str
    z_score: Decimal
    shap_value: Decimal
    direction: FlagDirection


class QuantizedOutlierResult(_Frozen):
    """``OutlierResult`` as persisted: same shape, same fields, Decimal instead of float.

    ⚑ Still advisory-only — score + explained flags + provenance, **no verdict field** (BR-OUT-9).
    The projection must never widen what the source schema carries.
    """

    outlier_score: Decimal
    is_outlier: bool
    flagged_features: list[QuantizedFlaggedFeature]
    provenance: OutlierProvenance


def _quantize(value: float) -> Decimal:
    """One float -> fixed-precision Decimal.

    ⚑ ``Decimal(str(value))`` and not ``Decimal(value)``: the latter captures the full binary
    expansion of the float (``Decimal(0.1)`` is ``0.1000000000000000055511151231257827…``), which
    would make the pre-quantization value depend on binary representation artifacts. Going through
    ``str`` takes Python's shortest round-trip repr first, so the quantized result is the one a
    human reading the score would predict.

    ``ROUND_HALF_EVEN`` is Decimal's default and is stated explicitly rather than inherited, so the
    tie-breaking rule is visible to a reader and cannot change under us with a context change.
    """
    return Decimal(str(value)).quantize(OUTLIER_QUANT_EXPONENT, rounding=ROUND_HALF_EVEN)


def quantize_outlier(result: OutlierResult) -> QuantizedOutlierResult:
    """``OutlierResult`` -> the persistable projection. Numeric-only: nothing else is touched."""
    return QuantizedOutlierResult(
        outlier_score=_quantize(result.outlier_score),
        is_outlier=result.is_outlier,
        flagged_features=[
            QuantizedFlaggedFeature(
                feature=flag.feature,
                z_score=_quantize(flag.z_score),
                shap_value=_quantize(flag.shap_value),
                direction=flag.direction,
            )
            for flag in result.flagged_features
        ],
        provenance=result.provenance,
    )


def dequantize_outlier(data: Any) -> OutlierResult:
    """The projection (or its CANON-SER-deserialized mapping) -> the real ``OutlierResult``.

    Accepts what ``canon_deserialize`` returns, so the read path is
    ``bytes -> canon_deserialize -> dequantize_outlier`` — mirroring the two existing
    ``*_from_canonical`` adapters' ``model_validate(canon_deserialize(...))`` shape rather than
    inventing a new one.

    ⚑ ``float(Decimal)`` is exact for any value at this precision, so the wire carries the same
    number that was stored. It is also what keeps the frontend unchanged: JSON does not
    distinguish Decimal from float once serialized, so ``outlierView`` sees the shape it was
    built against.
    """
    quantized = (
        data
        if isinstance(data, QuantizedOutlierResult)
        else QuantizedOutlierResult.model_validate(data)
    )
    return OutlierResult(
        outlier_score=float(quantized.outlier_score),
        is_outlier=quantized.is_outlier,
        flagged_features=[
            FlaggedFeature(
                feature=flag.feature,
                z_score=float(flag.z_score),
                shap_value=float(flag.shap_value),
                direction=FlagDirection(flag.direction),
            )
            for flag in quantized.flagged_features
        ],
        provenance=quantized.provenance,
    )
