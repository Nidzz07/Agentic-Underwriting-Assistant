import { describe, it, expect } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import {
  makeOverrideDouble, makeMemoView, makeCommittedOverride,
  readErrorEnvelope, conflictEnvelope, NONBLANK_REASON, resolved, rejected, renderForm,
} from './fixtures.js';

// FETCH-1 (transitions) — one consolidated transition test file covering all legs of the machine,
// INCLUDING both split-error recovery paths and the reason-carrying states, all on the same
// dual-operation reason-carrying double (Q7-A / Fold-A).
describe('FETCH-1 — consolidated state-machine transitions', () => {
  it('loading -> ready -> confirming -> Cancel -> ready (zero POST across the confirm/cancel legs)', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderForm({ seam });

    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button')); // ready -> confirming
    await screen.findByTestId('override-confirm-dialog');
    fireEvent.click(screen.getByTestId('override-confirm-cancel')); // confirming -> ready
    await waitFor(() => expect(screen.queryByTestId('override-confirm-dialog')).toBeNull());
    expect(seam.submitOverride.calls.length).toBe(0);
  });

  it('confirming -> Confirm -> submitting -> committed (reason carried)', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.resolveWith(makeCommittedOverride());
    renderForm({ seam });
    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    expect(await screen.findByTestId('override-committed-view')).toBeInTheDocument();
    expect(seam.submitOverride.calls[0]).toEqual(['rec-1', NONBLANK_REASON]);
  });

  it('loading -> errorRead -> Retry -> loading -> ready', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.sequence([rejected(readErrorEnvelope), resolved(makeMemoView())]);
    renderForm({ seam });
    fireEvent.click(await screen.findByTestId('override-error-retry'));
    expect(await screen.findByTestId('override-recommendation-context')).toBeInTheDocument();
  });

  it('submitting -> errorCommit -> Back -> ready (reason preserved)', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.rejectWith(conflictEnvelope);
    renderForm({ seam });
    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    await screen.findByTestId('override-state-error');
    fireEvent.click(screen.getByTestId('override-error-back'));
    expect(await screen.findByTestId('override-affordance-button')).toBeInTheDocument();
    expect(screen.getByTestId('override-reason-input')).toHaveValue(NONBLANK_REASON);
  });
});
