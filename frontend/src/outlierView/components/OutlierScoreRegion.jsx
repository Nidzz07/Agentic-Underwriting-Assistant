import { OUTLIER_COPY } from '../copy.js';

// C-OUTV-4 (OutlierScoreRegion) — MANDATORY header comment (NFR-ND-OUTV-Fold-1).
//
// Props are { outlierScore, isOutlier, testid } ONLY.
//   - NO recommendation prop, NO confidence prop, and no path to either (P-OUTV-2 / NOVERDICT-1):
//     a system verdict is structurally UNNAMEABLE here — there is no prop through which one could
//     enter. Mirrors the frozen ui-history CommittedActionRegion prop-exclusion precedent.
//   - NO provenance prop, NO seed, NO corpus_version, and no path to any of them (P-OUTV-3 /
//     PROV-1): the negative holds because there is NOTHING TO RENDER, not because of a rendering
//     choice a later edit could silently regress.
//
// Renders no system verdict and no provenance. The score is a STATISTICAL anomaly score under
// advisory chrome — not a decision and not a recommendation (BR-OUTV-2).
//
// Documentation only — NOT enforcement. The enforcement is the prop signature itself (plus the
// StructuralGuard scans over comment-stripped source, CG-OUTV-Fold-1).
export function OutlierScoreRegion({ outlierScore, isOutlier, testid = 'outlier-region-score' }) {
  return (
    <div data-testid={testid}>
      <h3>{OUTLIER_COPY.scoreHeading}</h3>
      <p>
        {OUTLIER_COPY.outlierScoreLabel}
        {': '}
        <span data-testid="outlier-score">{outlierScore}</span>
      </p>
      <p>
        {OUTLIER_COPY.isOutlierLabel}
        {': '}
        <span data-testid="outlier-isoutlier">
          {isOutlier ? OUTLIER_COPY.isOutlierYes : OUTLIER_COPY.isOutlierNo}
        </span>
      </p>
    </div>
  );
}

export default OutlierScoreRegion;
