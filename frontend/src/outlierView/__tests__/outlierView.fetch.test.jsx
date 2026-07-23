import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OutlierView } from '../OutlierView.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import {
  makePendingBody,
  makeReadyNullOutlierBody,
  makeReadyPopulatedBody,
  makeCapturingTransport,
  makeFailingTransport,
} from './fixtures.js';

// NFR-OUTV-FETCH-1 (P-OUTV-6 / Fold-A / D-OUTV-1) — R4 is driven through a SINGLE injected,
// capturing fetchSeam double. One double construction per test; the capture is what proves the
// same-resource Retry contract. No live backend, no MSW, no network.

describe('FETCH-1 — the four-state machine is driven end-to-end through ONE injected double', () => {
  it.each([
    ['READY', makeReadyPopulatedBody(), 'outlier-view'],
    ['NOT_AVAILABLE (pending body)', makePendingBody(), 'outlier-state-notavailable'],
    ['NOT_AVAILABLE (ready + null outlier)', makeReadyNullOutlierBody(), 'outlier-state-notavailable'],
  ])('LOADING -> %s through the single double', async (_label, body, expectedTestid) => {
    const transport = makeCapturingTransport(body);
    const fetchSeam = createOutlierFetch(transport);

    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-4" />);

    // LOADING is the initial state before the double resolves.
    expect(screen.getByTestId('outlier-state-loading')).toBeInTheDocument();

    expect(await screen.findByTestId(expectedTestid)).toBeInTheDocument();
    expect(screen.queryByTestId('outlier-state-loading')).toBeNull();

    // Exactly ONE R4 request, for the requested applicationId.
    expect(transport.calls).toEqual([{ method: 'GET', path: '/applications/app-4/memo' }]);
  });

  it('LOADING -> ERROR through the single double', async () => {
    const transport = makeFailingTransport('envelope');
    const fetchSeam = createOutlierFetch(transport);

    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-4" />);
    expect(screen.getByTestId('outlier-state-loading')).toBeInTheDocument();
    expect(await screen.findByTestId('outlier-state-error')).toBeInTheDocument();
    expect(transport.calls).toHaveLength(1);
  });

  it('fetches exactly once per applicationId (no redundant re-fetch)', async () => {
    const transport = makeCapturingTransport(makeReadyPopulatedBody());
    const fetchSeam = createOutlierFetch(transport);
    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-5" />);
    await screen.findByTestId('outlier-view');
    expect(transport.calls).toHaveLength(1);
  });

  it('the seam is INJECTED — the view constructs no transport of its own', async () => {
    // The view is driven entirely by the prop; nothing is fetched if the prop never resolves.
    const fetchSeam = () => new Promise(() => {});
    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-6" />);
    expect(screen.getByTestId('outlier-state-loading')).toBeInTheDocument();
  });

  it('honours a custom ready-root testid', async () => {
    const fetchSeam = createOutlierFetch(makeCapturingTransport(makeReadyPopulatedBody()));
    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-7" testid="outlier-view-custom" />);
    expect(await screen.findByTestId('outlier-view-custom')).toBeInTheDocument();
  });
});
