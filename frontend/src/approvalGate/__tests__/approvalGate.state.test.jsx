import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import {
  makeCommitDouble, makeMemoView, pendingMemoView, makeCommittedDecision,
  readErrorEnvelope, renderGate,
} from './fixtures.js';

// FETCH-1 (per-state renders) — every render state of the machine renders correctly. The seam is
// injected as a prop; the dual-op double is programmed per state.
describe('FETCH-1 — per-state renders', () => {
  it('loading — while the R4 read is in flight', () => {
    const seam = makeCommitDouble();
    seam.fetchContext.hang(); // never resolves — stays loading
    renderGate({ seam });
    expect(screen.getByTestId('approval-state-loading')).toBeInTheDocument();
  });

  it('pending — no recommendation to approve (status pending / null recommendation_id)', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(pendingMemoView);
    renderGate({ seam });
    expect(await screen.findByTestId('approval-state-pending')).toBeInTheDocument();
    expect(screen.queryByTestId('approval-affordance-approve')).toBeNull();
  });

  it('ready(idle) — the recommendation context + the approve affordance', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderGate({ seam });
    expect(await screen.findByTestId('approval-recommendation-context')).toBeInTheDocument();
    expect(screen.getByTestId('approval-affordance-approve')).toBeInTheDocument();
    expect(screen.queryByTestId('approval-confirm-dialog')).toBeNull();
  });

  it('confirming — the dialog is shown over the context', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderGate({ seam });
    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    expect(await screen.findByTestId('approval-confirm-dialog')).toBeInTheDocument();
  });

  it('submitting — an in-flight indicator while the commit is pending', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.hang(); // commit stays in flight
    renderGate({ seam });
    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
    expect(await screen.findByTestId('approval-state-submitting')).toBeInTheDocument();
  });

  it('committed — the confirmation state', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.resolveWith(makeCommittedDecision());
    renderGate({ seam });
    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
    expect(await screen.findByTestId('approval-committed')).toBeInTheDocument();
  });

  it('errorRead — an R4 read failure', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.rejectWith(readErrorEnvelope);
    renderGate({ seam });
    expect(await screen.findByTestId('approval-state-error')).toBeInTheDocument();
    expect(screen.getByTestId('approval-error-retry')).toBeInTheDocument();
  });
});
