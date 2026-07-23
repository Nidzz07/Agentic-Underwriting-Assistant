import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { makeOverrideDouble, makeMemoView, makeCommittedOverride, BLANK_REASONS, NONBLANK_REASON, renderForm } from './fixtures.js';

// REASONGATE-1 (teeth, full-highest — the NEW load-bearing pattern, P2 / BR-OVR-8). Each blank reason
// keeps the affordance DISABLED and drives the FULL Override->Confirm attempt to ZERO submitOverride
// (not merely asserting the disabled attribute); a non-blank control yields EXACTLY ONE POST carrying
// the reason VERBATIM.
describe('REASONGATE-1 — mandatory non-blank reason gate teeth', () => {
  it.each(BLANK_REASONS.map((r) => ({ label: JSON.stringify(r), reason: r })))(
    'blank reason $label keeps the affordance disabled and yields 0 submitOverride across the full attempt',
    async ({ reason }) => {
      const seam = makeOverrideDouble();
      seam.fetchContext.resolveWith(makeMemoView());
      seam.submitOverride.resolveWith(makeCommittedOverride());
      renderForm({ seam });

      const input = await screen.findByTestId('override-reason-input');
      fireEvent.change(input, { target: { value: reason } });

      const overrideBtn = screen.getByTestId('override-affordance-button');
      expect(overrideBtn).toBeDisabled();

      // drive the full attempt: a disabled button click issues no onClick, so no dialog opens
      fireEvent.click(overrideBtn);
      expect(screen.queryByTestId('override-confirm-dialog')).toBeNull();
      expect(seam.submitOverride.calls.length).toBe(0); // ZERO — the gate held
    }
  );

  it('a non-blank reason (with surrounding spaces) enables the affordance and sends the reason AS-ENTERED', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.resolveWith(makeCommittedOverride());
    renderForm({ seam });

    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    const overrideBtn = screen.getByTestId('override-affordance-button');
    expect(overrideBtn).not.toBeDisabled();

    fireEvent.click(overrideBtn);
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    await screen.findByTestId('override-committed-view');

    expect(seam.submitOverride.calls.length).toBe(1); // EXACTLY one
    expect(seam.submitOverride.calls[0]).toEqual(['rec-1', NONBLANK_REASON]); // verbatim / untrimmed
  });
});
