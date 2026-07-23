import { describe, it, expect } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { makeOverrideDouble, makeMemoView, NONBLANK_REASON, renderForm } from './fixtures.js';

// CANCEL-1 (teeth, full-highest) — opening then canceling the confirm dialog has NO side effect, and
// the typed reason is PRESERVED (BR-OVR-12 / P8).
describe('CANCEL-1 — cancelable-without-side-effect teeth', () => {
  it('open then Cancel: zero calls on both operations, context identical, back to ready(idle), reason preserved', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderForm({ seam });

    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    const before = screen.getByTestId('override-recommendation-context').innerHTML;

    fireEvent.click(screen.getByTestId('override-affordance-button')); // open
    const cancel = await screen.findByTestId('override-confirm-cancel');
    fireEvent.click(cancel); // cancel

    await waitFor(() => expect(screen.queryByTestId('override-confirm-dialog')).toBeNull());
    // teeth: neither operation was called across open+cancel (fetchContext stays at its post-mount 1)
    expect(seam.submitOverride.calls.length).toBe(0);
    expect(seam.fetchContext.calls.length).toBe(1);
    // context identical; still in ready(idle) with the affordance present; reason preserved
    expect(screen.getByTestId('override-recommendation-context').innerHTML).toBe(before);
    expect(screen.getByTestId('override-affordance-button')).toBeInTheDocument();
    expect(screen.getByTestId('override-reason-input')).toHaveValue(NONBLANK_REASON);
  });
});
