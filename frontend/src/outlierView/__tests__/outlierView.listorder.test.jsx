import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OutlierView } from '../OutlierView.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import { productionFiles, readSource, stripComments } from './refNotOwn.js';
import { outlierFlagTestid } from '../testids.js';
import {
  makeReadyPopulatedBody,
  makeCapturingTransport,
  POPULATED_FEATURE_ORDER,
} from './fixtures.js';

// NFR-OUTV-LISTORDER-1 (P-OUTV-5) — the delivered order is preserved; no client re-sort. The
// backend order is a deterministic property of the frozen U18 model (NFR-OUT-DET-1); the view is a
// faithful renderer (BR-OUTV-6).

describe('LISTORDER-1 — flagged_features render in the DELIVERED order', () => {
  it('the fixture is deliberately NOT sorted (the teeth are real)', () => {
    const flags = makeReadyPopulatedBody().outlier.flagged_features;
    const names = flags.map((f) => f.feature);
    const byName = [...names].sort();
    const byAbsZ = [...flags].sort((a, b) => Math.abs(b.z_score) - Math.abs(a.z_score)).map((f) => f.feature);
    const byShap = [...flags].sort((a, b) => b.shap_value - a.shap_value).map((f) => f.feature);

    // Delivered order matches NO plausible client-side sort — so any re-sort would be detected.
    expect(names).not.toEqual(byName);
    expect(names).not.toEqual(byAbsZ);
    expect(names).not.toEqual(byShap);
    expect(names).toEqual([...POPULATED_FEATURE_ORDER]);
  });

  it('rendered row order equals the input order', async () => {
    const fetchSeam = createOutlierFetch(makeCapturingTransport(makeReadyPopulatedBody()));
    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
    await screen.findByTestId('outlier-view');

    const rows = [...screen.getByTestId('outlier-region-flags').querySelectorAll('li')];
    const renderedTestids = rows.map((li) => li.dataset.testid);

    expect(renderedTestids).toEqual(POPULATED_FEATURE_ORDER.map(outlierFlagTestid));
  });

  it('no comparator or .sort() on the list in the production source (structural)', () => {
    const offenders = productionFiles().filter((f) => {
      const src = stripComments(readSource(f));
      return /\.sort\s*\(/.test(src) || /\.reverse\s*\(/.test(src);
    });
    expect(offenders).toEqual([]);
  });

  it('detector self-test (non-vacuous)', () => {
    const sample = 'const rows = flaggedFeatures.sort((a, b) => b.z_score - a.z_score);';
    expect(/\.sort\s*\(/.test(stripComments(sample))).toBe(true);
    expect(/\.sort\s*\(/.test(stripComments('const rows = flaggedFeatures.map(render);'))).toBe(false);
  });
});
