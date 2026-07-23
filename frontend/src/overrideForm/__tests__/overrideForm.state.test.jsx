import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import {
  makeOverrideDouble, makeMemoView, pendingMemoView, makeCommittedOverride,
  readErrorEnvelope, NONBLANK_REASON, renderForm,
} from './fixtures.js';

// FETCH-1 (per-state renders) — every render state of the machine renders correctly. The seam is
// injected as a prop; the dual-op reason-carrying double is programmed per state.
describe('FETCH-1 — per-state renders', () => {
  it('loading — while the R4 read is in flight', () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.hang();
    renderForm({ seam });
    expect(screen.getByTestId('override-state-loading')).toBeInTheDocument();
  });

  it('pending — no recommendation to override (status pending / null recommendation_id)', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(pendingMemoView);
    renderForm({ seam });
    expect(await screen.findByTestId('override-state-pending')).toBeInTheDocument();
    expect(screen.queryByTestId('override-affordance-button')).toBeNull();
    expect(screen.queryByTestId('override-reason-input')).toBeNull(); // no reason input in pending
  });

  it('ready(idle) — context + reason input + a disabled affordance (blank reason)', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderForm({ seam });
    expect(await screen.findByTestId('override-recommendation-context')).toBeInTheDocument();
    expect(screen.getByTestId('override-reason-input')).toBeInTheDocument();
    expect(screen.getByTestId('override-affordance-button')).toBeDisabled(); // blank reason => disabled
    expect(screen.queryByTestId('override-confirm-dialog')).toBeNull();
  });

  it('confirming — the dialog is shown over the context (after a non-blank reason)', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderForm({ seam });
    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    expect(await screen.findByTestId('override-confirm-dialog')).toBeInTheDocument();
    // the editable input is frozen (not rendered) during confirming (P8 / ND-OVR-Fold-i)
    expect(screen.queryByTestId('override-reason-input')).toBeNull();
  });

  it('submitting — an in-flight indicator while the commit is pending', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.hang();
    renderForm({ seam });
    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    expect(await screen.findByTestId('override-state-submitting')).toBeInTheDocument();
  });

  it('committed — the confirmation state', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.resolveWith(makeCommittedOverride());
    renderForm({ seam });
    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    expect(await screen.findByTestId('override-committed-view')).toBeInTheDocument();
  });

  it('errorRead — an R4 read failure', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.rejectWith(readErrorEnvelope);
    renderForm({ seam });
    expect(await screen.findByTestId('override-state-error')).toBeInTheDocument();
    expect(screen.getByTestId('override-error-retry')).toBeInTheDocument();
  });
});
