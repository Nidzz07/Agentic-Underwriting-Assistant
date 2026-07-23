import { describe, it, expect } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import {
  makeCommitDouble, makeMemoView, makeCommittedDecision,
  readErrorEnvelope, conflictEnvelope, resolved, rejected, renderGate,
} from './fixtures.js';

// FETCH-1 (transitions) — one consolidated transition test file covering all legs of the machine,
// INCLUDING both split-error recovery paths, all on the same dual-operation double (Q5-A / Fold-4).
describe('FETCH-1 — consolidated state-machine transitions', () => {
  it('loading -> ready -> confirming -> Cancel -> ready (zero POST across the confirm/cancel legs)', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderGate({ seam });

    fireEvent.click(await screen.findByTestId('approval-affordance-approve')); // ready -> confirming
    await screen.findByTestId('approval-confirm-dialog');
    fireEvent.click(screen.getByTestId('approval-confirm-cancel')); // confirming -> ready
    await waitFor(() => expect(screen.queryByTestId('approval-confirm-dialog')).toBeNull());
    expect(seam.submitApprove.calls.length).toBe(0);
  });

  it('confirming -> Confirm -> submitting -> committed', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.resolveWith(makeCommittedDecision());
    renderGate({ seam });
    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
    expect(await screen.findByTestId('approval-committed')).toBeInTheDocument();
  });

  it('loading -> errorRead -> Retry -> loading -> ready', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.sequence([rejected(readErrorEnvelope), resolved(makeMemoView())]);
    renderGate({ seam });
    fireEvent.click(await screen.findByTestId('approval-error-retry'));
    expect(await screen.findByTestId('approval-recommendation-context')).toBeInTheDocument();
  });

  it('submitting -> errorCommit -> Back -> ready', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.rejectWith(conflictEnvelope);
    renderGate({ seam });
    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
    await screen.findByTestId('approval-state-error');
    fireEvent.click(screen.getByTestId('approval-error-back'));
    expect(await screen.findByTestId('approval-affordance-approve')).toBeInTheDocument();
  });
});
