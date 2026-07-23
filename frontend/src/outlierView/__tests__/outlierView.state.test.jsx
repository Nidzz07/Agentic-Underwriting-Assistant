import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OutlierView, deriveOutlierState, OUTLIER_STATE } from '../OutlierView.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import {
  makePendingBody,
  makeReadyNullOutlierBody,
  makeReadyEmptyFlagsBody,
  makeReadyPopulatedBody,
  makeCapturingTransport,
  makeFailingTransport,
} from './fixtures.js';

// NFR-OUTV-STATE-1 (P-OUTV-1) — LOAD-BEARING. Q8-A: this file covers PER-STATE CONTAINER rendering
// incl. BOTH null-causes; the ordering/transition teeth live in outlierView.transition.test.jsx.

function renderWith(transport, applicationId = 'app-1') {
  const fetchSeam = createOutlierFetch(transport);
  return render(<OutlierView fetchSeam={fetchSeam} applicationId={applicationId} />);
}

describe('STATE-1 (a) — each of the four states renders its own container', () => {
  it('LOADING renders the loading container while the fetch is in flight', () => {
    // A transport that never settles keeps the view in LOADING.
    renderWith(() => new Promise(() => {}));
    expect(screen.getByTestId('outlier-state-loading')).toBeInTheDocument();
  });

  it('READY renders the ready composition (score + flags), not a state view', async () => {
    renderWith(makeCapturingTransport(makeReadyPopulatedBody()));
    expect(await screen.findByTestId('outlier-view')).toBeInTheDocument();
    expect(screen.getByTestId('outlier-region-score')).toBeInTheDocument();
    expect(screen.getByTestId('outlier-region-flags')).toBeInTheDocument();
    expect(screen.queryByTestId('outlier-state-notavailable')).toBeNull();
    expect(screen.queryByTestId('outlier-state-error')).toBeNull();
  });

  it('ERROR renders the error container', async () => {
    renderWith(makeFailingTransport('envelope'));
    expect(await screen.findByTestId('outlier-state-error')).toBeInTheDocument();
  });
});

// (b) THE FIELD-DERIVED TEETH — NOT_AVAILABLE renders for BOTH null-causes. The second case is what
// proves the derivation reads the `outlier` FIELD and not the R4 `status` discriminator.
describe('STATE-1 (b) — NOT_AVAILABLE is FIELD-derived, covering BOTH null-causes', () => {
  it('renders NOT_AVAILABLE for a status:"pending" body carrying outlier:null', async () => {
    renderWith(makeCapturingTransport(makePendingBody()));
    expect(await screen.findByTestId('outlier-state-notavailable')).toBeInTheDocument();
    expect(screen.queryByTestId('outlier-view')).toBeNull();
  });

  it('renders NOT_AVAILABLE for a Phase-1 status:"ready" body that STILL carries outlier:null', async () => {
    // THE load-bearing fixture: a status-keyed implementation would render READY here and fail.
    const body = makeReadyNullOutlierBody();
    expect(body.status).toBe('ready');
    expect(body.outlier).toBeNull();

    renderWith(makeCapturingTransport(body));
    expect(await screen.findByTestId('outlier-state-notavailable')).toBeInTheDocument();
    expect(screen.queryByTestId('outlier-view')).toBeNull();
    expect(screen.queryByTestId('outlier-region-score')).toBeNull();
  });

  it('a PRESENT outlier on a ready body renders READY (the discriminator really is the field)', async () => {
    renderWith(makeCapturingTransport(makeReadyEmptyFlagsBody()));
    expect(await screen.findByTestId('outlier-view')).toBeInTheDocument();
    expect(screen.queryByTestId('outlier-state-notavailable')).toBeNull();
  });
});

// The derivation as a pure function — the branch ORDER made directly assertable.
describe('STATE-1 — deriveOutlierState: the failure-first ordering as a pure function', () => {
  it('a REJECTED fetch yields ERROR regardless of any view content', () => {
    expect(deriveOutlierState('rejected', {})).toBe(OUTLIER_STATE.ERROR);
    expect(deriveOutlierState('rejected', { outlier: null })).toBe(OUTLIER_STATE.ERROR);
    expect(deriveOutlierState('rejected', { outlier: { outlier_score: 1 } })).toBe(OUTLIER_STATE.ERROR);
  });

  it('a PENDING fetch yields LOADING', () => {
    expect(deriveOutlierState('pending', {})).toBe(OUTLIER_STATE.LOADING);
  });

  it('a RESOLVED fetch with a null outlier yields NOT_AVAILABLE', () => {
    expect(deriveOutlierState('resolved', { outlier: null })).toBe(OUTLIER_STATE.NOT_AVAILABLE);
    expect(deriveOutlierState('resolved', {})).toBe(OUTLIER_STATE.NOT_AVAILABLE);
  });

  it('a RESOLVED fetch with a present outlier yields READY', () => {
    expect(deriveOutlierState('resolved', { outlier: { outlier_score: 0.5 } })).toBe(OUTLIER_STATE.READY);
  });

  it('the four states are a closed set', () => {
    expect(Object.values(OUTLIER_STATE).sort()).toEqual(['error', 'loading', 'not_available', 'ready']);
  });
});
