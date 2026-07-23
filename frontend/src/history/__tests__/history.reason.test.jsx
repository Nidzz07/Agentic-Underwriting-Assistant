import { describe, it, expect } from 'vitest';
import { screen, within } from '@testing-library/react';
import { openDetail, overrideRecord, approveRecord } from './fixtures.js';

// REASON-1 (P10) — the conditional reason, confined to the HUMAN namespace. The test FAILS if the
// reason appeared on `approve` or was absent on `override`.
describe('CommittedActionRegion — REASON-1: reason iff override (teeth)', () => {
  it('an OVERRIDE record renders the reason INSIDE the human region', async () => {
    await openDetail('dec-22', { detail: [{ resolve: overrideRecord }] });
    const human = await screen.findByTestId('history-detail-human-region');

    const reason = within(human).getByTestId('history-detail-reason');
    expect(reason).toHaveTextContent(overrideRecord.committed_decision.reason);
    expect(within(human).getByTestId('history-detail-action')).toHaveTextContent('Override');
    expect(within(human).getByTestId('history-detail-underwriter')).toHaveTextContent('uw-7');
  });

  it('an APPROVE record renders NO reason node at all', async () => {
    await openDetail('dec-21', { detail: [{ resolve: approveRecord }] });
    await screen.findByTestId('history-detail-human-region');

    expect(screen.queryByTestId('history-detail-reason')).toBeNull();
    expect(screen.getByTestId('history-detail-action')).toHaveTextContent('Approve');
    expect(screen.getByTestId('history-detail-underwriter')).toHaveTextContent('uw-7');
  });

  it('the action label is looked up from COMMIT_ACTION_LABELS by value — never a bare enum value', async () => {
    await openDetail('dec-22', { detail: [{ resolve: overrideRecord }] });
    const action = await screen.findByTestId('history-detail-action');
    expect(action).toHaveTextContent('Override');
    expect(action).not.toHaveTextContent('override'); // the wire value is never shown raw
  });
});
