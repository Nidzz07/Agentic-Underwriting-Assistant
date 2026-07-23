import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { makeCommitDouble, makeMemoView, makeCommittedDecision, renderGate } from './fixtures.js';

// CONFIRM-1 (teeth, full-highest) + NOFINAL-1 (behavioral) — the commit fires ONLY on Confirm.
describe('CONFIRM-1 — confirm-before-commit teeth', () => {
  it('Approve opens the dialog with ZERO submitApprove and ONE fetchContext; only Confirm commits', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.resolveWith(makeCommittedDecision());
    renderGate({ seam });

    const approve = await screen.findByTestId('approval-affordance-approve');
    // after the initial R4 read: exactly one fetchContext, zero submitApprove
    expect(seam.fetchContext.calls.length).toBe(1);
    expect(seam.submitApprove.calls.length).toBe(0);

    fireEvent.click(approve); // opens the confirm dialog — must NOT commit
    const confirm = await screen.findByTestId('approval-confirm-submit');
    // the Fold-1 cross-guard: still zero submit, still one fetch (differing 0 vs 1 counts)
    expect(seam.submitApprove.calls.length).toBe(0);
    expect(seam.fetchContext.calls.length).toBe(1);

    fireEvent.click(confirm); // the SINGLE call site fires
    await screen.findByTestId('approval-committed');
    expect(seam.submitApprove.calls.length).toBe(1);
  });
});
