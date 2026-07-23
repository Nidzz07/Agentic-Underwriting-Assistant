import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoView } from '../MemoView.jsx';
import { pendingMemoView, emptyListsReadyMemoView } from './fixtures.js';

// PENDING-1 (Fold-C) — `pending` derived from the R4 status DISCRIMINATOR, NOT list emptiness.
describe('MemoView — PENDING-1: status discriminator (teeth)', () => {
  it('status "pending" -> memo-state-pending, none of the three regions', async () => {
    const seam = async () => pendingMemoView;
    render(<MemoView memoFetchSeam={seam} applicationId="app-1" />);
    expect(await screen.findByTestId('memo-state-pending')).toBeInTheDocument();
    expect(screen.queryByTestId('memo-region-narrative')).toBeNull();
    expect(screen.queryByTestId('memo-region-missinginfo')).toBeNull();
    expect(screen.queryByTestId('memo-region-readonly')).toBeNull();
  });

  it('status "ready" with EMPTY lists -> renders ready, NOT pending (teeth on the discriminator)', async () => {
    const seam = async () => emptyListsReadyMemoView;
    render(<MemoView memoFetchSeam={seam} applicationId="app-1" />);
    // proves the state keys on `status`, not on missing_information/cited_rule_ids emptiness.
    expect(await screen.findByTestId('memo-region-readonly')).toBeInTheDocument();
    expect(screen.queryByTestId('memo-state-pending')).toBeNull();
    // and the empty-list neutral-copy branch is exercised (BR-MEMO-9).
    expect(screen.getByTestId('memo-region-citations')).toHaveTextContent('No rules cited');
    expect(screen.getByTestId('memo-region-missinginfo')).toHaveTextContent('No missing information');
  });
});
