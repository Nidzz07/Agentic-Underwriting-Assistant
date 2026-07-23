import { describe, it, expect } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { makeCommitDouble, makeMemoView, renderGate } from './fixtures.js';

// CANCEL-1 (teeth, full-highest) — opening then canceling the confirm dialog has NO side effect.
describe('CANCEL-1 — cancelable-without-side-effect teeth', () => {
  it('open then Cancel: zero calls on both operations, context identical, back to ready(idle)', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderGate({ seam });

    const approve = await screen.findByTestId('approval-affordance-approve');
    const before = screen.getByTestId('approval-recommendation-context').innerHTML;

    fireEvent.click(approve); // open
    const cancel = await screen.findByTestId('approval-confirm-cancel');
    fireEvent.click(cancel); // cancel

    await waitFor(() => expect(screen.queryByTestId('approval-confirm-dialog')).toBeNull());
    // teeth: neither operation was called across open+cancel (fetchContext stays at its post-mount 1)
    expect(seam.submitApprove.calls.length).toBe(0);
    expect(seam.fetchContext.calls.length).toBe(1);
    // context identical; still in ready(idle) with the affordance present
    expect(screen.getByTestId('approval-recommendation-context').innerHTML).toBe(before);
    expect(screen.getByTestId('approval-affordance-approve')).toBeInTheDocument();
  });
});
