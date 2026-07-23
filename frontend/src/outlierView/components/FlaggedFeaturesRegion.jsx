import { OUTLIER_COPY, FLAG_DIRECTION_LABELS } from '../copy.js';
import { outlierFlagTestid } from '../testids.js';

// C-OUTV-5 (FlaggedFeaturesRegion) — MANDATORY header comment (NFR-ND-OUTV-Fold-1).
//
// Props are { flaggedFeatures, testid } ONLY.
//   - NO recommendation prop, NO confidence prop, no path to either (P-OUTV-2 / NOVERDICT-1).
//   - NO provenance prop, NO seed, NO corpus_version, no path to any (P-OUTV-3 / PROV-1).
//
// Flags render as STATISTICAL SIGNALS, never a verdict (BR-OUTV-2): `direction` goes through
// FLAG_DIRECTION_LABELS as a statistical POSITION (above/below the typical range), never a severity
// word (OUTV-FD-Fold-3). Rows render IN THE DELIVERED ORDER — no comparator, no .sort(), a faithful
// map over the array as given (P-OUTV-5 / LISTORDER-1; the backend order is a deterministic property
// of the frozen U18 model).
//
// An EMPTY flagged_features array is a distinct branch: "analyzed, nothing anomalous" (noFlagsLabel)
// — structurally different from the NOT_AVAILABLE "not analyzed" state, which lives in
// OutlierStateView entirely (P-OUTV-4 / EMPTY-1).
//
// CG-OUTV-Fold-3: the row DISPLAYS the raw wire `feature` string (Q3-A, faithful-renderer — the FD
// copy inventory has no feature-label map); its data-testid uses the SLUGGED form (Q2-A). Both derive
// from the same wire value; the asymmetry is intentional.
//
// Documentation only — NOT enforcement (the prop signature is).
export function FlaggedFeaturesRegion({ flaggedFeatures, testid = 'outlier-region-flags' }) {
  if (flaggedFeatures.length === 0) {
    return (
      <div data-testid={testid}>
        <h3>{OUTLIER_COPY.flagsHeading}</h3>
        <p>{OUTLIER_COPY.noFlagsLabel}</p>
      </div>
    );
  }

  return (
    <div data-testid={testid}>
      <h3>{OUTLIER_COPY.flagsHeading}</h3>
      <ul>
        {flaggedFeatures.map((flag) => (
          <li key={flag.feature} data-testid={outlierFlagTestid(flag.feature)}>
            <span>{flag.feature}</span>
            {' — '}
            <span>{FLAG_DIRECTION_LABELS[flag.direction]}</span>
            {' · '}
            <span>
              {OUTLIER_COPY.zScoreLabel}
              {': '}
              {flag.z_score}
            </span>
            {' · '}
            <span>
              {OUTLIER_COPY.shapValueLabel}
              {': '}
              {flag.shap_value}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default FlaggedFeaturesRegion;
