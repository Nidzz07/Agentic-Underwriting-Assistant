"""BARRIER #5 — the Decimal-quantized projection that lets an ``OutlierResult`` be persisted.

⛔ **The defect these tests exist for.** ``CanonSerAdapter.canonical_bytes`` rejects IEEE float
outright (``CanonSerError: float is not permitted; use Decimal (CON-DET-1)``), and every numeric
field of ``OutlierResult`` is a ``float`` — they come out of IsolationForest and SHAP. U24's
``pipeline.py:134`` serializes the seam's return with exactly that adapter, so **a real outlier
score could not be persisted at all**. The wiring plan's Fold C asserted "serialization already
works"; it does not, and that was found by running it, not by reading it.

⚑ **What the projection claims, and what it does NOT.** It claims that the same logical score
persists to the same bytes and reads back unambiguously **at the named precision**. It does NOT
claim the underlying ML computation is bit-for-bit reproducible across library versions —
CANON-SER's guarantee covers the persisted REPRESENTATION only, and nothing in this stack promises
cross-version floating-point identity (which is why ``OUTLIER_MODEL_VERSION`` bundles the sklearn
version). A float carrying more than ``OUTLIER_QUANT_DECIMAL_PLACES`` significant decimals is
deliberately narrowed; that narrowing is the design, not a rounding bug.

tier-U: no database, no network, no corpus.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from backend.app.outlier_canonical import (
    OUTLIER_QUANT_DECIMAL_PLACES,
    OUTLIER_QUANT_EXPONENT,
    dequantize_outlier,
    quantize_outlier,
)
from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.common.canon_ser import canon_deserialize
from backend.outlier_model.model import OutlierModel
from backend.outlier_model.schemas import (
    FlagDirection,
    FlaggedFeature,
    OutlierProvenance,
    OutlierResult,
)
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.outlier_model.tests.fixtures import (
    make_manifest,
    normal_corpus_profiles,
    typical_profile,
)


def _result(score: float = 0.667071302659) -> OutlierResult:
    return OutlierResult(
        outlier_score=score,
        is_outlier=True,
        flagged_features=[
            FlaggedFeature(
                feature="dti_ratio",
                z_score=3.4000000000004,
                shap_value=-0.0210000000009,
                direction=FlagDirection.HIGH,
            )
        ],
        provenance=OutlierProvenance(
            corpus_version="1.0.0", seed=42, outlier_model_version="outlier-model/1.0.0+test"
        ),
    )


class TestT7QuantizationProducesDecimals:
    def test_every_float_field_becomes_a_decimal(self):
        """T7 — the whole point: no ``float`` may survive into the persisted shape."""
        quantized = quantize_outlier(_result())

        assert isinstance(quantized.outlier_score, Decimal)
        assert isinstance(quantized.flagged_features[0].z_score, Decimal)
        assert isinstance(quantized.flagged_features[0].shap_value, Decimal)

    def test_the_precision_is_the_named_constant_not_a_magic_number(self):
        """The constant is the single source of truth, so the precision is changeable in one
        place and visible to a reader — not spelled inline at each call site."""
        assert OUTLIER_QUANT_DECIMAL_PLACES == 12
        assert OUTLIER_QUANT_EXPONENT == Decimal("1E-12")

        quantized = quantize_outlier(_result())

        for value in (
            quantized.outlier_score,
            quantized.flagged_features[0].z_score,
            quantized.flagged_features[0].shap_value,
        ):
            assert -value.as_tuple().exponent == OUTLIER_QUANT_DECIMAL_PLACES

    def test_the_non_numeric_fields_pass_through_untouched(self):
        """Quantization is numeric-only: it must not disturb the provenance triple, the flag
        identity, or the advisory-only shape."""
        quantized = quantize_outlier(_result())

        assert quantized.is_outlier is True
        assert quantized.flagged_features[0].feature == "dti_ratio"
        assert quantized.flagged_features[0].direction is FlagDirection.HIGH
        assert quantized.provenance.corpus_version == "1.0.0"
        assert quantized.provenance.seed == 42

    def test_the_projection_carries_no_verdict_either(self):
        """BR-OUT-9 survives the projection — an advisory shape must not acquire a decision field
        on its way into the database."""
        quantized = quantize_outlier(_result())

        assert set(quantized.model_dump()) == {
            "outlier_score", "is_outlier", "flagged_features", "provenance"
        }


class TestT8ThePersistedRoundTrip:
    def test_the_quantized_projection_survives_canon_ser_at_all(self):
        """⛔ THE REGRESSION TEST FOR BARRIER #5. The raw ``OutlierResult`` raises here; the
        projection must not. If this ever fails, outlier data cannot be persisted again."""
        quantized = quantize_outlier(_result())

        payload = CanonSerAdapter.canonical_bytes(quantized)

        assert isinstance(payload, bytes) and payload

    def test_the_raw_float_bearing_result_still_raises_which_is_why_this_exists(self):
        """Pins the defect itself, so the reason for the projection cannot quietly evaporate.

        ⚑ If a future change made ``OutlierResult`` directly serializable, this test fails and
        forces a deliberate decision about whether the projection is still needed — rather than
        leaving an unexplained indirection nobody dares remove.
        """
        with pytest.raises(Exception) as excinfo:
            CanonSerAdapter.canonical_bytes(_result())

        assert "float is not permitted" in str(excinfo.value)

    def test_round_tripping_is_lossless_at_the_named_precision(self):
        """T8 — quantize -> persist -> read back -> dequantize.

        ⚑ Losslessness is claimed AT the named precision, NOT against the raw float: the input
        z_score 3.4000000000004 is narrowed to 12 dp by design. What must hold is that the value
        which was STORED is the value that comes BACK.
        """
        quantized = quantize_outlier(_result())
        payload = CanonSerAdapter.canonical_bytes(quantized)

        restored = dequantize_outlier(canon_deserialize(payload))

        assert isinstance(restored, OutlierResult)
        assert restored.outlier_score == float(quantized.outlier_score)
        assert restored.flagged_features[0].z_score == float(quantized.flagged_features[0].z_score)
        assert restored.flagged_features[0].shap_value == float(
            quantized.flagged_features[0].shap_value
        )
        assert restored.flagged_features[0].direction is FlagDirection.HIGH
        assert restored.provenance == _result().provenance

    def test_a_score_within_the_named_precision_survives_exactly(self):
        """The reference value observed in Fold A has 12 decimals, so it must round-trip EXACTLY
        — this is the case the determinism spot-check actually compares against."""
        restored = dequantize_outlier(
            canon_deserialize(CanonSerAdapter.canonical_bytes(quantize_outlier(_result())))
        )

        assert restored.outlier_score == 0.667071302659

    def test_persisting_twice_yields_identical_bytes(self):
        """CANON-SER's actual guarantee, exercised on this shape: the same logical value
        serializes to the same bytes. This is what quantization buys — and it is a claim about
        the REPRESENTATION, not about floating-point computation."""
        first = CanonSerAdapter.canonical_bytes(quantize_outlier(_result()))
        second = CanonSerAdapter.canonical_bytes(quantize_outlier(_result()))

        assert first == second


class TestT9DeterminismThroughQuantization:
    def test_rescoring_the_same_profile_yields_the_identical_quantized_value(self):
        """T9 — Fold E's determinism check, extended to cover the quantization step.

        Fold E measured that two independent fits score identically. That is necessary but not
        sufficient now: the value that must be stable is the one that reaches the DATABASE, so
        the check has to run through quantization, not stop at the float.

        ⚑ This does NOT assert cross-version reproducibility. Both fits happen in this process,
        against this sklearn build. It asserts that nothing in the fit/score/quantize path
        introduces run-to-run variance — seeded randomness holding, which IS an acceptance
        criterion (§6, reproducibility 100%).
        """
        profile = typical_profile()
        first_model = OutlierModel.fit(normal_corpus_profiles(), make_manifest(), ShapExplainer())
        second_model = OutlierModel.fit(normal_corpus_profiles(), make_manifest(), ShapExplainer())

        first = quantize_outlier(first_model.score(profile))
        second = quantize_outlier(second_model.score(profile))

        assert first.outlier_score == second.outlier_score
        assert CanonSerAdapter.canonical_bytes(first) == CanonSerAdapter.canonical_bytes(second)

    def test_rescoring_on_one_fitted_model_is_stable_too(self):
        """The cheaper half of the same property: scoring is a pure function of the profile."""
        model = OutlierModel.fit(normal_corpus_profiles(), make_manifest(), ShapExplainer())
        profile = typical_profile()

        assert quantize_outlier(model.score(profile)) == quantize_outlier(model.score(profile))
