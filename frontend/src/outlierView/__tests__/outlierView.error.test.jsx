import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OutlierView } from '../OutlierView.jsx';
import { OutlierStateView } from '../components/OutlierStateView.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import { OUTLIER_COPY } from '../copy.js';
import { makeFailingTransport } from './fixtures.js';

// NFR-OUTV-ERROR-1 (P-OUTV-7) — message visible, code via hidden testid, detail NEVER raw.

describe('ERROR-1 — the error envelope renders message-only', () => {
  async function renderError() {
    const fetchSeam = createOutlierFetch(makeFailingTransport('envelope'));
    const { container } = render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
    await screen.findByTestId('outlier-state-error');
    return container;
  }

  it('renders error.message visibly', async () => {
    await renderError();
    expect(screen.getByTestId('outlier-error-message')).toHaveTextContent('No such application.');
  });

  it('binds error.code to a HIDDEN testid — never visible UI text', async () => {
    await renderError();
    const code = screen.getByTestId('outlier-error-code');
    expect(code).toHaveTextContent('not_found');
    expect(code.hasAttribute('hidden')).toBe(true);
  });

  it('NEVER renders error.detail raw', async () => {
    const container = await renderError();
    // The fixture's detail carries a distinctive internal hint — it must not surface.
    expect(container.textContent).not.toContain('internal detail');
    expect(container.textContent).not.toContain('hint');
  });

  it('offers a Retry affordance', async () => {
    await renderError();
    expect(screen.getByTestId('outlier-error-retry')).toHaveTextContent(OUTLIER_COPY.retryLabel);
  });
});

// The defensive fallback: fetchSeam normalization guarantees a well-formed envelope, so this branch
// is unreachable in production — it is exercised here directly (coverage + defence in depth).
describe('ERROR-1 — OutlierStateView defensive fallback for a malformed envelope', () => {
  it('falls back to the unknown-error copy when the envelope is malformed', () => {
    render(<OutlierStateView state="error" error={null} />);
    expect(screen.getByTestId('outlier-error-message')).toHaveTextContent(OUTLIER_COPY.unknownErrorMessage);
    expect(screen.getByTestId('outlier-error-code')).toHaveTextContent('unknown_error');
  });

  it('renders no Retry when no onRetry handler is supplied', () => {
    render(<OutlierStateView state="error" error={null} />);
    expect(screen.queryByTestId('outlier-error-retry')).toBeNull();
  });

  it('honours an explicit testid override on each state', () => {
    const { unmount } = render(<OutlierStateView state="loading" testid="outlier-state-custom" />);
    expect(screen.getByTestId('outlier-state-custom')).toBeInTheDocument();
    unmount();

    const second = render(<OutlierStateView state="not_available" testid="outlier-state-custom" />);
    expect(screen.getByTestId('outlier-state-custom')).toBeInTheDocument();
    second.unmount();

    render(<OutlierStateView state="error" error={null} testid="outlier-state-custom" />);
    expect(screen.getByTestId('outlier-state-custom')).toBeInTheDocument();
  });
});
