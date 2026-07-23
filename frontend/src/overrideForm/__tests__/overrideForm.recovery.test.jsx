import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import {
  makeOverrideDouble, makeMemoView, makeCommittedOverride,
  readErrorEnvelope, conflictEnvelope, NONBLANK_REASON, resolved, rejected, renderForm,
} from './fixtures.js';

// RECOVERY-1 (two-directional teeth) — cause-differentiated recovery, reason preserved on the commit leg.
describe('RECOVERY-1 — cause-differentiated recovery', () => {
  it('(a) an errorRead Retry re-issues exactly one fetchContext for the SAME applicationId', async () => {
    const seam = makeOverrideDouble();
    // fail the first read, then succeed on Retry — a sequence distinct from the static ERROR-1 table
    seam.fetchContext.sequence([rejected(readErrorEnvelope), resolved(makeMemoView({ application_id: 'app-X' }))]);
    renderForm({ seam, applicationId: 'app-X' });

    const retry = await screen.findByTestId('override-error-retry');
    expect(seam.fetchContext.calls.length).toBe(1);
    expect(seam.fetchContext.calls[0][0]).toBe('app-X');

    fireEvent.click(retry);
    await screen.findByTestId('override-recommendation-context');
    expect(seam.fetchContext.calls.length).toBe(2);
    expect(seam.fetchContext.calls[1][0]).toBe('app-X'); // SAME applicationId
  });

  it('(b) an errorCommit returns to ready(idle) with NO auto-resubmit and the reason PRESERVED; a fresh cycle commits', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.rejectWith(conflictEnvelope);
    renderForm({ seam });

    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    await screen.findByTestId('override-state-error');
    expect(seam.submitOverride.calls.length).toBe(1);

    // return to ready — NOT an automatic resubmit; the reason survives the commit error (P8)
    fireEvent.click(screen.getByTestId('override-error-back'));
    await screen.findByTestId('override-affordance-button');
    await Promise.resolve();
    expect(seam.submitOverride.calls.length).toBe(1); // still 1 — no auto-retry
    expect(screen.getByTestId('override-reason-input')).toHaveValue(NONBLANK_REASON); // reason preserved

    // a fresh Override -> Confirm is required to reach a second attempt (reason still present)
    seam.submitOverride.resolveWith(makeCommittedOverride());
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    await screen.findByTestId('override-committed-view');
    expect(seam.submitOverride.calls.length).toBe(2);
    expect(seam.submitOverride.calls[1]).toEqual(['rec-1', NONBLANK_REASON]); // same preserved reason
  });
});
