import { describe, it, expect } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import {
  makeOverrideDouble, makeMemoView, conflictEnvelope, NONBLANK_REASON, renderForm,
} from './fixtures.js';

// REASONKEEP-1 (two distinct assertions — P8 / BR-OVR-12):
//   (a) preservation teeth — the reason survives Cancel AND errorCommit unchanged (structurally: the
//       Cancel/errorCommit transitions never call setReason — the reason slice is orthogonal to phase);
//   (b) a dedicated read-only echo DOM assertion — override-confirm-reason-echo renders the current
//       reason read-only, DISTINCT from the post-submission committed display node.
describe('REASONKEEP-1 — reason preserved + read-only echo', () => {
  it('(a1) reason survives a Cancel of the confirm dialog', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderForm({ seam });

    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-cancel'));
    await waitFor(() => expect(screen.queryByTestId('override-confirm-dialog')).toBeNull());
    expect(screen.getByTestId('override-reason-input')).toHaveValue(NONBLANK_REASON);
  });

  it('(a2) reason survives an errorCommit returning to ready(idle)', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.rejectWith(conflictEnvelope);
    renderForm({ seam });

    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    await screen.findByTestId('override-state-error');
    fireEvent.click(screen.getByTestId('override-error-back'));
    await screen.findByTestId('override-affordance-button');
    expect(screen.getByTestId('override-reason-input')).toHaveValue(NONBLANK_REASON);
  });

  it('(b) the confirming state renders the reason as a read-only echo, distinct from the committed node', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderForm({ seam });

    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    const echo = await screen.findByTestId('override-confirm-reason-echo');
    expect(echo).toHaveTextContent(NONBLANK_REASON.trim()); // the echoed reason (heading + reason text)
    // it is the confirm-echo node, NOT the post-submission committed-reason node
    expect(screen.queryByTestId('override-committed-reason')).toBeNull();
    // and it is read-only (not an editable field) — no input/textarea inside the echo node
    expect(echo.querySelector('textarea')).toBeNull();
    expect(echo.querySelector('input')).toBeNull();
  });
});
