import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { OutlierView, deriveOutlierState, OUTLIER_STATE } from '../OutlierView.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import { makeReadyPopulatedBody, makeFailingTransport } from './fixtures.js';

// NFR-OUTV-STATE-1 (P-OUTV-1) — LOAD-BEARING, Q8-A: the FAILURE-FIRST ORDERING / TRANSITION teeth.
// This is the file that proves NOT_AVAILABLE is UNREACHABLE from an error path.

describe('STATE-1 (c) — failure-first: a fetch failure renders ERROR and NEVER NOT_AVAILABLE', () => {
  it.each([
    ['a non-2xx envelope', 'envelope'],
    ['a raw transport throw', 'throw'],
  ])('%s routes to ERROR, with the not-available state ABSENT', async (_label, mode) => {
    const fetchSeam = createOutlierFetch(makeFailingTransport(mode));
    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);

    // Asserted BOTH ways (the plan §3.1(c) teeth):
    //   (1) the error state is present ...
    expect(await screen.findByTestId('outlier-state-error')).toBeInTheDocument();
    //   (2) ... AND the not-available state is absent — it cannot mask a genuine error.
    expect(screen.queryByTestId('outlier-state-notavailable')).toBeNull();
    expect(screen.queryByTestId('outlier-view')).toBeNull();
  });

  // The structural proof, independent of rendering: for EVERY possible view payload — including the
  // null-outlier payload that would otherwise derive NOT_AVAILABLE — a rejected fetch still yields
  // ERROR. The null-check branch is simply not reachable once the failure branch has returned.
  it('NOT_AVAILABLE is unwritable from a failure path for ANY payload (branch ordering)', () => {
    const payloads = [
      {},
      { outlier: null },
      { outlier: undefined },
      { outlier: { outlier_score: 0.9, is_outlier: true, flagged_features: [] } },
      { status: 'pending', outlier: null },
      { status: 'ready', outlier: null },
    ];
    for (const view of payloads) {
      expect(deriveOutlierState('rejected', view)).toBe(OUTLIER_STATE.ERROR);
      expect(deriveOutlierState('rejected', view)).not.toBe(OUTLIER_STATE.NOT_AVAILABLE);
    }
  });

  // The mirror image: the SAME null payload DOES derive NOT_AVAILABLE once the fetch resolved —
  // proving the test above is discriminating on fetch outcome, not on the payload being unusual.
  it('the same null payload DOES yield NOT_AVAILABLE when the fetch RESOLVED (non-vacuous)', () => {
    expect(deriveOutlierState('resolved', { status: 'ready', outlier: null })).toBe(OUTLIER_STATE.NOT_AVAILABLE);
    expect(deriveOutlierState('rejected', { status: 'ready', outlier: null })).toBe(OUTLIER_STATE.ERROR);
  });
});

describe('STATE-1 / ERROR-1 — Retry transitions ERROR -> LOADING -> re-resolve', () => {
  it('Retry re-fetches the SAME applicationId and recovers to READY', async () => {
    const calls = [];
    let failNext = true;
    const transport = async (request) => {
      calls.push(request);
      if (failNext) {
        failNext = false;
        throw new Error('socket hang up');
      }
      return { ok: true, body: makeReadyPopulatedBody('app-9') };
    };

    const fetchSeam = createOutlierFetch(transport);
    render(<OutlierView fetchSeam={fetchSeam} applicationId="app-9" />);

    fireEvent.click(await screen.findByTestId('outlier-error-retry'));

    await screen.findByTestId('outlier-view');
    expect(screen.queryByTestId('outlier-state-error')).toBeNull();

    // The capture proves Retry re-fetched the SAME resource (ERROR-1), not a different one.
    expect(calls).toEqual([
      { method: 'GET', path: '/applications/app-9/memo' },
      { method: 'GET', path: '/applications/app-9/memo' },
    ]);
  });
});
