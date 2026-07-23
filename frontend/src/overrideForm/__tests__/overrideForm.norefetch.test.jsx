import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { makeOverrideDouble, makeMemoView, makeCommittedOverride, NONBLANK_REASON, renderForm } from './fixtures.js';

// NOREFETCH-1 (teeth) — after a successful override, the confirmation renders from the echo + context
// already in hand; BOTH operation counts stay frozen (no re-fetch). The committed reason is sourced
// from decision.reason (the echo — ND-OVR-Fold-ii), not the client slice.
describe('NOREFETCH-1 — confirmation without re-fetch', () => {
  it('after success, both fetchContext and submitOverride counts stay at 1; the echo renders', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.resolveWith(makeCommittedOverride({ underwriter_id: 'u-99', reason: 'echoed reason' }));
    renderForm({ seam });

    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    await screen.findByTestId('override-committed-view');

    // renders the echo (committer + committed reason) — no separate re-fetch was needed
    expect(screen.getByTestId('override-committed-by')).toHaveTextContent('u-99');
    expect(screen.getByTestId('override-committed-action')).toHaveTextContent('Override');
    expect(screen.getByTestId('override-committed-reason')).toHaveTextContent('echoed reason'); // from decision.reason
    const fc = seam.fetchContext.calls.length;
    const so = seam.submitOverride.calls.length;
    await Promise.resolve();
    await Promise.resolve();
    expect(seam.fetchContext.calls.length).toBe(fc);
    expect(seam.submitOverride.calls.length).toBe(so);
    expect(fc).toBe(1);
    expect(so).toBe(1);
  });
});
