import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RECOMMENDATION_LABELS, CONFIDENCE_LABELS } from '../../shell/copy/index.js';
import { OutlierView } from '../OutlierView.jsx';
import { OutlierScoreRegion } from '../components/OutlierScoreRegion.jsx';
import { FlaggedFeaturesRegion } from '../components/FlaggedFeaturesRegion.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import { makeReadyPopulatedBody, makeCapturingTransport } from './fixtures.js';

// NFR-OUTV-NOVERDICT-1 (P-OUTV-2) — LOAD-BEARING, the RENDERED-ABSENCE half (the regression layer;
// the import-absence scan in noVerdictImport.test.js is the primary robust guarantee).
//
// Fold-B / D-OUTV-3: absence is asserted with RTL queryBy* returning null over an ENUMERATED FINITE
// SET using EXACT matching — never a container.textContent.includes(...) substring sweep (the
// project's text-scan-false-positive caution applies to rendered-absence assertions too).

// The enumerated finite set: the raw wire values + every shell display label for both namespaces.
const FORBIDDEN_VERDICT_TOKENS = [
  'APPROVE',
  'REFER',
  'DECLINE-RECOMMEND',
  ...Object.values(RECOMMENDATION_LABELS),
  ...Object.values(CONFIDENCE_LABELS),
];

describe('NOVERDICT-1 (rendered) — no verdict token is queryable over a populated READY view', () => {
  it('the enumerated set is non-empty and contains both namespaces (guard)', () => {
    expect(FORBIDDEN_VERDICT_TOKENS).toContain('DECLINE-RECOMMEND');
    expect(FORBIDDEN_VERDICT_TOKENS).toContain('Decline-Recommend');
    expect(FORBIDDEN_VERDICT_TOKENS).toContain('High');
    expect(FORBIDDEN_VERDICT_TOKENS.length).toBeGreaterThanOrEqual(9);
  });

  it.each(FORBIDDEN_VERDICT_TOKENS)('"%s" is NOT queryable in the rendered output', async (token) => {
    const body = makeReadyPopulatedBody();
    const fetchSeam = createOutlierFetch(makeCapturingTransport(body));
    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
    await screen.findByTestId('outlier-view');

    // EXACT matching (RTL default), over the enumerated set — not a substring sweep.
    expect(screen.queryByText(token)).toBeNull();
  });

  it('the READY view really did render its signals (the absence above is not vacuous)', async () => {
    const fetchSeam = createOutlierFetch(makeCapturingTransport(makeReadyPopulatedBody()));
    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
    await screen.findByTestId('outlier-view');
    expect(screen.getByTestId('outlier-score')).toHaveTextContent('0.87');
    expect(screen.getByTestId('outlier-region-flags')).toBeInTheDocument();
  });
});

// P-OUTV-2 / P-OUTV-3: the prop-signature exclusion — a verdict or provenance passed to either
// region is UNRENDERABLE because there is no prop through which it could enter. These assertions
// pin the guarantee at the component boundary, independent of OutlierView's composition.
describe('NOVERDICT-1 / PROV-1 (by construction) — the regions have no verdict/provenance path', () => {
  it('OutlierScoreRegion ignores any verdict/provenance prop forced upon it', () => {
    render(
      <OutlierScoreRegion
        outlierScore={0.5}
        isOutlier
        recommendation="DECLINE-RECOMMEND"
        confidence="High"
        provenance={{ seed: 987654321, corpus_version: 'SENTINEL-CORPUS-DO-NOT-RENDER' }}
      />,
    );
    expect(screen.queryByText('DECLINE-RECOMMEND')).toBeNull();
    expect(screen.queryByText('High')).toBeNull();
    expect(screen.queryByText('987654321')).toBeNull();
    expect(screen.queryByText('SENTINEL-CORPUS-DO-NOT-RENDER')).toBeNull();
    // ... while the props it DOES accept render.
    expect(screen.getByTestId('outlier-score')).toHaveTextContent('0.5');
  });

  it('FlaggedFeaturesRegion ignores any verdict/provenance prop forced upon it', () => {
    render(
      <FlaggedFeaturesRegion
        flaggedFeatures={[{ feature: 'dti_ratio', z_score: 2.9, shap_value: 0.41, direction: 'high' }]}
        recommendation="APPROVE"
        confidence="Low"
        provenance={{ seed: 987654321, corpus_version: 'SENTINEL-CORPUS-DO-NOT-RENDER' }}
      />,
    );
    expect(screen.queryByText('APPROVE')).toBeNull();
    expect(screen.queryByText('Low')).toBeNull();
    expect(screen.queryByText('987654321')).toBeNull();
    expect(screen.getByTestId('outlier-flag-dti-ratio')).toBeInTheDocument();
  });
});
