"""Fitting the outlier model from the committed corpus — a COMPOSITION concern (Q4(a)).

⛔ **THIS MODULE DECLARES A HARD RUNTIME DEPENDENCY OF THE DEPLOYED BACKEND.** See
``CORPUS_ON_RENDER`` below. Read that before changing anything here.

⚑ **RELOCATED HERE 2026-08-02 (WIRE1-Fold-6, stage 3) from ``backend/scripts/seed_demo_cases.py``,
where ``build_outlier_model`` and ``CORPUS_DIR`` were first written.** The execution plan's step
3.4 says *"reusing ``build_outlier_model``"* — and reuse from ``backend/app/`` was not possible
while it lived in ``backend/scripts/``, a tree that is outside every ``--cov=`` entry and
deliberately out-of-band. **Relocating rather than duplicating was the right call here** because
this is REAL production logic (fit a model from a committed corpus), and duplicating it would
have duplicated the corpus path and the loud-failure message — two things that must never drift.

⚑ **The import direction is the ESTABLISHED one, not a new edge.** ``seed_demo_cases.py`` already
imports ``backend.app.llm_client`` and ``backend.app.outlier_canonical``; it now imports this too.
Scripts depend on the composition root; the composition root depends on no script.

⚠️ **Contrast with ``offline_memo_double.py``, which was DUPLICATED rather than moved** — and the
distinction is deliberate. That one is a **test double**, and the seed script's docstring
explicitly wants it kept out of the production tree. This one is production logic that the
request path genuinely needs. Same boundary, opposite answers, for a stated reason.

⚑ **This reopens no frozen unit.** ``outlier_model`` (U18) itself is untouched: its own invariant
BR-OUT-8 / NFR-OUT-CORPUS-1 binds *the unit*, which still builds, tests and imports with no
``corpus/`` present. It does not bind a CALLER that chooses to supply one — which is exactly what
``CorpusSource.from_file`` exists for.
"""
from __future__ import annotations

import json
from pathlib import Path

from backend.corpus_generator.records import CorpusManifest
from backend.outlier_model.corpus_source import CorpusSource
from backend.outlier_model.model import FittedOutlierModel, OutlierModel
from backend.outlier_model.shap_explainer import ShapExplainer

#: The committed corpus the outlier model is fitted from. Module-level and named once so a test
#: can point it elsewhere — mirroring ``dependencies.RULEBOOK_DIR``'s single-source shape.
CORPUS_DIR = Path(__file__).resolve().parents[2] / "corpus"

#: ⛔ **THE CARRIED-FORWARD DEPLOYMENT QUESTION, ANSWERED AND CLOSED HERE — Q4's forced follow-up.**
#:
#: It was carried from the outlier pass (its plan §7 item 2) as *"OPEN, and deliberately not
#: answered: whether ``corpus/`` ships to the DEPLOYED backend"*, on the grounds that
#: *"seeding is not part of deployment at all — so nothing today depends on the answer."*
#:
#: ⚑ **R11 is what makes that reasoning obsolete.** Outlier scoring is now on an HTTP path any
#: authenticated underwriter can reach, so the corpus is no longer a seed-script convenience —
#: it is a **runtime dependency of the deployed service**. Q4(a) was chosen knowing this, and
#: the answer recorded at that gate was: **YES, ``corpus/`` ships.**
#:
#: ⚑ Declared as a NAMED CONSTANT rather than a comment so the deployment pass finds it by
#: grepping the production tree instead of by remembering a plan document. A test asserts it
#: exists (``test_the_deployment_dependency_is_declared_in_code_not_only_in_prose``).
#:
#: ⛔ **NOT IMPLEMENTED HERE, AND DELIBERATELY SO**: ``render.yaml`` is untouched by this pass.
#: Placing and VERIFYING the corpus on the deployed backend is the deployment pass's work, and
#: doing it here would be deployment work smuggled into a wiring pass. What this pass owes that
#: pass is an unambiguous, discoverable statement of the requirement — this constant is it.
CORPUS_ON_RENDER = (
    "HARD DEPLOYMENT DEPENDENCY (WIRE1-Fold-6, Q4(a)): corpus/profiles.json and "
    "corpus/manifest.json MUST be present on the deployed backend (Render). R11 fits the "
    "outlier model from them on first use; if they are absent the fit raises FileNotFoundError "
    "and drafting fails loudly rather than silently serving outlier=null. render.yaml neither "
    "places nor verifies them today - the deployment pass must do both."
)


def build_outlier_model(corpus_dir: Path | str | None = None) -> FittedOutlierModel:
    """Fit the outlier model from the COMMITTED corpus. Fails LOUDLY if it is absent (Q6(a)).

    ⚑ **Why a missing corpus is an ERROR and not a graceful degrade.** The rejected alternative
    (Q6(b)) was to fall back to ``outlier=None`` — which silently reproduces the exact defect the
    outlier wiring exists to fix. A silent null is indistinguishable from the legitimate Phase-1
    behaviour and would be very hard to notice; a named failure cannot be missed.

    ⚠️ **~2.6 s.** Never call this per request — it is held for the process lifetime behind
    ``dependencies.outlier_model()``'s ``lru_cache``.
    """
    corpus_dir = Path(corpus_dir) if corpus_dir is not None else CORPUS_DIR
    profiles_path = corpus_dir / "profiles.json"
    manifest_path = corpus_dir / "manifest.json"

    for path in (profiles_path, manifest_path):
        if not path.is_file():
            raise FileNotFoundError(
                f"outlier corpus not found at {path} - outlier scoring cannot run without it. "
                f"The corpus is committed to this repository; if it is missing here, restore "
                f"it. If it is missing on a DEPLOYED backend, see CORPUS_ON_RENDER: it must be "
                f"shipped, and scoring a case with a null outlier instead is not a fallback "
                f"this system offers."
            )

    records = CorpusSource.from_file(profiles_path)
    manifest = CorpusManifest.model_validate(
        json.loads(manifest_path.read_text(encoding="utf-8"))
    )
    return OutlierModel.fit(CorpusSource.profiles(records), manifest, ShapExplainer())
