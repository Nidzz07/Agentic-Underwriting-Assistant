import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { makeCommitDouble, makeMemoView, makeCommittedDecision, renderGate } from './fixtures.js';

// NOREFETCH-1 (teeth) — after a successful commit, the confirmation renders from the echo + context
// already in hand; BOTH operation counts stay frozen (no re-fetch).
describe('NOREFETCH-1 — confirmation without re-fetch', () => {
  it('after success, both fetchContext and submitApprove counts stay at 1', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.resolveWith(makeCommittedDecision({ underwriter_id: 'u-99' }));
    renderGate({ seam });

    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
    await screen.findByTestId('approval-committed');

    // renders the echo (committer) — no separate re-fetch was needed
    expect(screen.getByTestId('approval-committed-by')).toHaveTextContent('u-99');
    const fc = seam.fetchContext.calls.length;
    const sa = seam.submitApprove.calls.length;
    // settle any microtasks, then assert nothing further fired
    await Promise.resolve();
    await Promise.resolve();
    expect(seam.fetchContext.calls.length).toBe(fc);
    expect(seam.submitApprove.calls.length).toBe(sa);
    expect(fc).toBe(1);
    expect(sa).toBe(1);
  });
});
