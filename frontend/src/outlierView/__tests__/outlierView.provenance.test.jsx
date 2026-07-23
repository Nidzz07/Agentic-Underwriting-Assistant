import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OutlierView } from '../OutlierView.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import {
  makeReadyPopulatedBody,
  makeCapturingTransport,
  SENTINEL_SEED,
  SENTINEL_CORPUS_VERSION,
  SENTINEL_MODEL_VERSION,
} from './fixtures.js';

// NFR-OUTV-PROV-1 (P-OUTV-3) — the NEGATIVE teeth. Q5-A: the D-OUTV-4 / Fold-D sentinels VERBATIM.
// Q6-A: the outlier_model_version footnote is OMITTED, so provenance is entirely absent from the
// render and only the negative invariant is tested (CG-OUTV-Fold-2).
//
// The sentinels are distinctive and collision-proof by construction: they cannot overlap a score, a
// z_score, a feature name or a testid — so "sentinel absent" is sound in BOTH directions (no false
// fail from incidental overlap, no false pass from a weak sentinel).

describe('PROV-1 — provenance is never rendered; seed/corpus_version never reach the DOM', () => {
  async function renderReady() {
    const body = makeReadyPopulatedBody();
    // The fixture really does carry provenance — the absence below is about the VIEW, not the data.
    expect(body.outlier.provenance).toEqual({
      corpus_version: SENTINEL_CORPUS_VERSION,
      seed: SENTINEL_SEED,
      outlier_model_version: SENTINEL_MODEL_VERSION,
    });

    const fetchSeam = createOutlierFetch(makeCapturingTransport(body));
    const { container } = render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
    await screen.findByTestId('outlier-view');
    return container;
  }

  it('the seed sentinel is absent from the rendered output', async () => {
    const container = await renderReady();
    expect(screen.queryByText(String(SENTINEL_SEED))).toBeNull();
    expect(container.textContent).not.toContain(String(SENTINEL_SEED));
  });

  it('the corpus_version sentinel is absent from the rendered output', async () => {
    const container = await renderReady();
    expect(screen.queryByText(SENTINEL_CORPUS_VERSION)).toBeNull();
    expect(container.textContent).not.toContain(SENTINEL_CORPUS_VERSION);
  });

  it('Q6-A — the model_version sentinel is absent too (the footnote is OMITTED)', async () => {
    const container = await renderReady();
    expect(screen.queryByText(SENTINEL_MODEL_VERSION)).toBeNull();
    expect(container.textContent).not.toContain(SENTINEL_MODEL_VERSION);
    expect(screen.queryByTestId('outlier-provenance-modelversion')).toBeNull();
  });

  it('the ready view DID render (the absences above are not vacuous)', async () => {
    const container = await renderReady();
    expect(container.textContent).toContain('0.87');
    expect(screen.getByTestId('outlier-region-flags')).toBeInTheDocument();
  });

  // The sentinels are only meaningful if they could have been caught. Prove the assertion technique
  // detects a sentinel that IS present.
  it('sentinel detection is non-vacuous (a rendered sentinel WOULD be caught)', () => {
    const { container } = render(<div>{SENTINEL_CORPUS_VERSION}</div>);
    expect(container.textContent).toContain(SENTINEL_CORPUS_VERSION);
  });
});
