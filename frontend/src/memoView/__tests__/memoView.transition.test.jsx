import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoView } from '../MemoView.jsx';
import { emptyListsReadyMemoView, pendingMemoView } from './fixtures.js';

// FETCH-1 — one consolidated transition test (Q5-A) on the single injected capturing double (Fold-A):
// loading->ready, loading->pending, loading->error, error--retry-->loading.
describe('MemoView — FETCH-1 state transitions (single injected double)', () => {
  it('loading -> ready', async () => {
    render(<MemoView memoFetchSeam={async () => emptyListsReadyMemoView} applicationId="app-1" />);
    expect(await screen.findByTestId('memo-view')).toBeInTheDocument();
  });

  it('loading -> pending', async () => {
    render(<MemoView memoFetchSeam={async () => pendingMemoView} applicationId="app-1" />);
    expect(await screen.findByTestId('memo-state-pending')).toBeInTheDocument();
  });

  it('loading -> error -> (retry) -> ready', async () => {
    let fail = true;
    const seam = async () => {
      if (fail) { fail = false; throw { error: { code: 'x', message: 'boom', detail: {} } }; }
      return emptyListsReadyMemoView;
    };
    render(<MemoView memoFetchSeam={seam} applicationId="app-1" />);
    fireEvent.click(await screen.findByTestId('memo-error-retry'));
    expect(await screen.findByTestId('memo-view')).toBeInTheDocument();
  });
});
