import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HistoryStateView } from '../components/HistoryStateView.jsx';
import {
  renderHistory,
  openDetail,
  emptyListBody,
  approveRecord,
  listErrorEnvelope,
  notFoundEnvelope,
} from './fixtures.js';

// STATEMACHINE-1 (P5) — the PER-STATE renders: each of the seven HISTORY_STATE values renders its
// pinned testid and NO foreign content. The consolidated transition coverage lives in its own file
// (history.transition.test.jsx, Q6-A).
const never = (...testids) => testids.forEach((t) => expect(screen.queryByTestId(t)).toBeNull());

describe('HistoryStateView — the five non-content states in isolation', () => {
  it('listLoading renders the loading placeholder and no content', () => {
    render(<HistoryStateView state="listLoading" />);
    expect(screen.getByTestId('history-state-loading')).toHaveAttribute('aria-busy', 'true');
    never('history-list', 'history-detail', 'history-state-empty', 'history-error-message');
  });

  it('detailLoading renders the same pinned loading placeholder (one id for both reads)', () => {
    render(<HistoryStateView state="detailLoading" />);
    expect(screen.getByTestId('history-state-loading')).toBeInTheDocument();
    never('history-detail', 'history-error-message');
  });

  it('listEmpty renders the page-level empty message only', () => {
    render(<HistoryStateView state="listEmpty" />);
    expect(screen.getByTestId('history-state-empty')).toHaveTextContent('No decisions yet');
    never('history-list', 'history-pagination', 'history-state-loading');
  });

  it('listError renders the list error container with message + code + Retry', () => {
    render(<HistoryStateView state="listError" error={listErrorEnvelope} onRetry={() => {}} />);
    expect(screen.getByTestId('history-state-error-list')).toBeInTheDocument();
    expect(screen.getByTestId('history-error-message')).toHaveTextContent(listErrorEnvelope.error.message);
    expect(screen.getByTestId('history-error-retry')).toBeInTheDocument();
    never('history-state-error-detail', 'history-list');
  });

  it('detailError renders the detail error container (incl. a generic 404)', () => {
    render(<HistoryStateView state="detailError" error={notFoundEnvelope} onRetry={() => {}} />);
    expect(screen.getByTestId('history-state-error-detail')).toBeInTheDocument();
    expect(screen.getByTestId('history-error-code')).toHaveTextContent('not_found');
    never('history-state-error-list', 'history-detail');
  });

  it('an error state with no envelope falls back defensively; with no onRetry it shows no Retry', () => {
    render(<HistoryStateView state="listError" error={null} />);
    expect(screen.getByTestId('history-error-message')).toHaveTextContent('Something went wrong.');
    expect(screen.getByTestId('history-error-code')).toHaveTextContent('unknown_error');
    never('history-error-retry');
  });
});

describe('HistoryView — the two CONTENT states through the real machine', () => {
  it('list renders the rows + pagination and no detail/state screens', async () => {
    renderHistory();
    await screen.findByTestId('history-list');
    expect(screen.getByTestId('history-pagination')).toBeInTheDocument();
    never('history-detail', 'history-state-loading', 'history-state-empty', 'history-state-error-list');
  });

  it('detail renders the AuditRecord + Back and no list/pagination', async () => {
    await openDetail('dec-21', { detail: [{ resolve: approveRecord }] });
    await screen.findByTestId('history-detail');
    expect(screen.getByTestId('history-detail-back')).toBeInTheDocument();
    expect(screen.getByTestId('history-detail-system-region')).toBeInTheDocument();
    expect(screen.getByTestId('history-detail-human-region')).toBeInTheDocument();
    never('history-list', 'history-pagination', 'history-state-error-detail');
  });

  it('listEmpty is reached through the machine from an empty R6 body', async () => {
    renderHistory({ list: [{ resolve: emptyListBody }] });
    await screen.findByTestId('history-state-empty');
    never('history-list', 'history-detail');
  });
});
