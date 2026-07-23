import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { isValidOutlierTestid } from '../../../eslint-rules/outlierView.js';
import { OutlierView } from '../OutlierView.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import {
  makeReadyPopulatedBody,
  makeReadyNullOutlierBody,
  makeCapturingTransport,
  makeFailingTransport,
} from './fixtures.js';

// NFR-OUTV-TESTID-1 (P-OUTV-10 / BR-OUTV-8) — every assertion-relevant element carries a stable
// outlier-<element>-<purpose> testid, and EVERY rendered testid satisfies the convention (Q1-A).

function allTestids(container) {
  return [...container.querySelectorAll('[data-testid]')].map((el) => el.dataset.testid);
}

describe('TESTID-1 — the READY composition', () => {
  it('carries the frozen FD inventory ids, all convention-satisfying', async () => {
    const fetchSeam = createOutlierFetch(makeCapturingTransport(makeReadyPopulatedBody()));
    const { container } = render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
    await screen.findByTestId('outlier-view');

    for (const id of [
      'outlier-view',
      'outlier-region-readonly',
      'outlier-region-score',
      'outlier-score',
      'outlier-isoutlier',
      'outlier-region-flags',
      'outlier-flag-dti-ratio',
      'outlier-flag-age-years-derived',
      'outlier-flag-verifiable-income-annual',
    ]) {
      expect(screen.getByTestId(id)).toBeInTheDocument();
    }

    const rendered = allTestids(container);
    expect(rendered.length).toBeGreaterThan(0);
    for (const id of rendered) {
      expect(isValidOutlierTestid(id)).toBe(true);
    }
  });
});

describe('TESTID-1 — the state containers', () => {
  it('the not-available state id satisfies the convention', async () => {
    const fetchSeam = createOutlierFetch(makeCapturingTransport(makeReadyNullOutlierBody()));
    const { container } = render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
    await screen.findByTestId('outlier-state-notavailable');
    for (const id of allTestids(container)) expect(isValidOutlierTestid(id)).toBe(true);
  });

  it('the error state ids (message / code / retry) satisfy the convention', async () => {
    const fetchSeam = createOutlierFetch(makeFailingTransport('envelope'));
    const { container } = render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
    await screen.findByTestId('outlier-state-error');

    for (const id of ['outlier-state-error', 'outlier-error-message', 'outlier-error-code', 'outlier-error-retry']) {
      expect(screen.getByTestId(id)).toBeInTheDocument();
    }
    for (const id of allTestids(container)) expect(isValidOutlierTestid(id)).toBe(true);
  });

  it('the loading state id satisfies the convention', () => {
    const { container } = render(<OutlierView fetchSeam={() => new Promise(() => {})} applicationId="app-1" />);
    expect(screen.getByTestId('outlier-state-loading')).toBeInTheDocument();
    for (const id of allTestids(container)) expect(isValidOutlierTestid(id)).toBe(true);
  });
});
