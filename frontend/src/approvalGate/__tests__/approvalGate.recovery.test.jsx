import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import {
  makeCommitDouble, makeMemoView, makeCommittedDecision,
  readErrorEnvelope, conflictEnvelope, resolved, rejected, renderGate,
} from './fixtures.js';

// RECOVERY-1 (two-directional teeth) — cause-differentiated recovery.
describe('RECOVERY-1 — cause-differentiated recovery', () => {
  it('(a) an ErrorRead Retry re-issues exactly one fetchContext for the SAME applicationId', async () => {
    const seam = makeCommitDouble();
    // fail the first read, then succeed on Retry — a sequence distinct from the static ERROR-1 table
    seam.fetchContext.sequence([rejected(readErrorEnvelope), resolved(makeMemoView({ application_id: 'app-X' }))]);
    renderGate({ seam, applicationId: 'app-X' });

    const retry = await screen.findByTestId('approval-error-retry');
    expect(seam.fetchContext.calls.length).toBe(1);
    expect(seam.fetchContext.calls[0][0]).toBe('app-X');

    fireEvent.click(retry);
    await screen.findByTestId('approval-recommendation-context');
    expect(seam.fetchContext.calls.length).toBe(2);
    expect(seam.fetchContext.calls[1][0]).toBe('app-X'); // SAME applicationId
  });

  it('(b) an ErrorCommit returns to ready(idle) with NO automatic resubmit; a fresh cycle is required', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.rejectWith(conflictEnvelope);
    renderGate({ seam });

    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
    await screen.findByTestId('approval-state-error');
    expect(seam.submitApprove.calls.length).toBe(1);

    // return to ready — NOT an automatic resubmit
    fireEvent.click(screen.getByTestId('approval-error-back'));
    await screen.findByTestId('approval-affordance-approve');
    await Promise.resolve();
    expect(seam.submitApprove.calls.length).toBe(1); // still 1 — no auto-retry

    // a fresh Approve -> Confirm is required to reach a second attempt
    seam.submitApprove.resolveWith(makeCommittedDecision());
    fireEvent.click(screen.getByTestId('approval-affordance-approve'));
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
    await screen.findByTestId('approval-committed');
    expect(seam.submitApprove.calls.length).toBe(2);
  });
});
