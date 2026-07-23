import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoView } from '../MemoView.jsx';
import { emptyListsReadyMemoView, pendingMemoView } from './fixtures.js';

// FETCH-1 — the four per-state renders, each on the single injected capturing double (Fold-A).
describe('MemoView — FETCH-1 four render states', () => {
  it('loading: shows the loading state while the fetch is in flight; no memo region', () => {
    const pending = () => new Promise(() => {}); // never resolves
    render(<MemoView memoFetchSeam={pending} applicationId="app-1" />);
    expect(screen.getByTestId('memo-state-loading')).toBeInTheDocument();
    expect(screen.queryByTestId('memo-region-narrative')).toBeNull();
  });

  it('ready: status "ready" -> the memo-view composition', async () => {
    const seam = async () => emptyListsReadyMemoView;
    render(<MemoView memoFetchSeam={seam} applicationId="app-1" />);
    expect(await screen.findByTestId('memo-view')).toBeInTheDocument();
  });

  it('pending: status "pending" -> the not-yet-drafted state', async () => {
    const seam = async () => pendingMemoView;
    render(<MemoView memoFetchSeam={seam} applicationId="app-1" />);
    expect(await screen.findByTestId('memo-state-pending')).toBeInTheDocument();
  });

  it('error: rejection envelope -> error state with message', async () => {
    const seam = async () => { throw { error: { code: 'internal_error', message: 'kaboom', detail: {} } }; };
    render(<MemoView memoFetchSeam={seam} applicationId="app-1" />);
    expect(await screen.findByTestId('memo-state-error')).toBeInTheDocument();
    expect(screen.getByTestId('memo-error-message')).toHaveTextContent('kaboom');
  });
});
