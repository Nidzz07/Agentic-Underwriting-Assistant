import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OutlierView } from '../OutlierView.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import { OUTLIER_COPY } from '../copy.js';
import {
  makeReadyEmptyFlagsBody,
  makeReadyNullOutlierBody,
  makeCapturingTransport,
} from './fixtures.js';

// NFR-OUTV-EMPTY-1 (P-OUTV-4) — the DISTINCT-BRANCH teeth. "analyzed, no anomalies found" is NOT
// "not analyzed": they are two structurally distinct branches, different components, different
// containers, different messages. Conflating them would mislead the underwriter.

function renderBody(body) {
  const fetchSeam = createOutlierFetch(makeCapturingTransport(body));
  return render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
}

describe('EMPTY-1 — an empty flagged_features list renders READY + "no anomalies"', () => {
  it('renders the READY composition with a valid score, NOT the not-available state', async () => {
    renderBody(makeReadyEmptyFlagsBody());
    await screen.findByTestId('outlier-view');

    expect(screen.getByTestId('outlier-region-flags')).toBeInTheDocument();
    expect(screen.getByText(OUTLIER_COPY.noFlagsLabel)).toBeInTheDocument();
    expect(screen.getByTestId('outlier-score')).toHaveTextContent('0.12');

    // TEETH: an empty list must NEVER be mistaken for "not analyzed".
    expect(screen.queryByTestId('outlier-state-notavailable')).toBeNull();
    expect(screen.queryByText(OUTLIER_COPY.notAvailableMessage)).toBeNull();
  });

  it('renders no flag rows for an empty list', async () => {
    renderBody(makeReadyEmptyFlagsBody());
    await screen.findByTestId('outlier-region-flags');
    expect(screen.queryByTestId('outlier-flag-dti-ratio')).toBeNull();
    expect(screen.getByTestId('outlier-region-flags').querySelectorAll('li')).toHaveLength(0);
  });
});

describe('EMPTY-1 — the NOT_AVAILABLE state is the mirror image', () => {
  it('renders the not-available message and NOT the no-anomalies message', async () => {
    renderBody(makeReadyNullOutlierBody());
    await screen.findByTestId('outlier-state-notavailable');

    expect(screen.getByText(OUTLIER_COPY.notAvailableMessage)).toBeInTheDocument();

    // TEETH: "not analyzed" must never render as "analyzed, nothing found".
    expect(screen.queryByText(OUTLIER_COPY.noFlagsLabel)).toBeNull();
    expect(screen.queryByTestId('outlier-region-flags')).toBeNull();
    expect(screen.queryByTestId('outlier-region-score')).toBeNull();
  });
});

describe('EMPTY-1 — the two branches are structurally distinct (the core assertion)', () => {
  it('different containers and different messages for present-empty vs absent', async () => {
    const { unmount } = renderBody(makeReadyEmptyFlagsBody());
    await screen.findByTestId('outlier-view');
    const emptyBranchTestid = screen.getByTestId('outlier-region-flags').dataset.testid;
    const emptyBranchMessage = OUTLIER_COPY.noFlagsLabel;
    unmount();

    renderBody(makeReadyNullOutlierBody());
    await screen.findByTestId('outlier-state-notavailable');
    const absentBranchTestid = screen.getByTestId('outlier-state-notavailable').dataset.testid;
    const absentBranchMessage = OUTLIER_COPY.notAvailableMessage;

    expect(emptyBranchTestid).not.toBe(absentBranchTestid);
    expect(emptyBranchMessage).not.toBe(absentBranchMessage);
  });
});
