import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { makeOverrideDouble, makeMemoView, makeCommittedOverride, NONBLANK_REASON, renderForm } from './fixtures.js';

// CONFIRM-1 (teeth, full-highest) + NOFINAL-1 (behavioral) — with a non-blank reason, the commit fires
// ONLY on Confirm; the Fold-A cross-guard differentiates 0 vs 1 counts across the two operations.
describe('CONFIRM-1 — confirm-before-commit teeth', () => {
  it('Override opens the dialog with ZERO submitOverride and ONE fetchContext; only Confirm commits', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.resolveWith(makeCommittedOverride());
    renderForm({ seam });

    // type a non-blank reason so the affordance enables
    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    const overrideBtn = screen.getByTestId('override-affordance-button');
    expect(overrideBtn).not.toBeDisabled();
    // after the initial R4 read: exactly one fetchContext, zero submitOverride
    expect(seam.fetchContext.calls.length).toBe(1);
    expect(seam.submitOverride.calls.length).toBe(0);

    fireEvent.click(overrideBtn); // opens the confirm dialog — must NOT commit
    const confirm = await screen.findByTestId('override-confirm-submit');
    // the Fold-A cross-guard: still zero submit, still one fetch (differing 0 vs 1 counts)
    expect(seam.submitOverride.calls.length).toBe(0);
    expect(seam.fetchContext.calls.length).toBe(1);

    fireEvent.click(confirm); // the SINGLE call site fires
    await screen.findByTestId('override-committed-view');
    expect(seam.submitOverride.calls.length).toBe(1);
    // and it carried the reason VERBATIM (as-entered, untrimmed) alongside the recommendation_id
    expect(seam.submitOverride.calls[0]).toEqual(['rec-1', NONBLANK_REASON]);
  });
});
