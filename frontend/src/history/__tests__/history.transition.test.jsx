import { describe, it, expect } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import {
  renderHistory,
  makeListBody,
  emptyListBody,
  approveRecord,
  listErrorEnvelope,
  notFoundEnvelope,
} from './fixtures.js';

// STATEMACHINE-1 — the ONE consolidated transition test (Q6-A: its own file, alongside the per-state
// history.state.test.jsx). Every leg of the master-detail machine, all on the SAME dual-read double
// (NFR-HIST-Fold-A). A deferred promise lets the intermediate *Loading states be observed.
function deferred() {
  let resolve;
  const promise = new Promise((r) => { resolve = r; });
  return { promise, resolve };
}

describe('HistoryView — STATEMACHINE-1: all transition legs (consolidated)', () => {
  it('listLoading -> list', async () => {
    const gate = deferred();
    renderHistory({ list: [{ resolve: () => gate.promise }] });
    expect(screen.getByTestId('history-state-loading')).toBeInTheDocument();
    gate.resolve(makeListBody());
    await screen.findByTestId('history-list');
  });

  it('listLoading -> listEmpty', async () => {
    renderHistory({ list: [{ resolve: emptyListBody }] });
    await screen.findByTestId('history-state-empty');
  });

  it('listLoading -> listError, and listError --retry--> listLoading -> list', async () => {
    const gate = deferred();
    const seam = renderHistory({
      list: [{ reject: listErrorEnvelope }, { resolve: () => gate.promise }],
    });
    await screen.findByTestId('history-state-error-list');

    fireEvent.click(screen.getByTestId('history-error-retry'));
    expect(screen.getByTestId('history-state-loading')).toBeInTheDocument(); // back through listLoading
    gate.resolve(makeListBody());
    await screen.findByTestId('history-list');
    expect(seam.fetchList.calls).toHaveLength(2);
  });

  it('list --select--> detailLoading -> detail', async () => {
    const gate = deferred();
    renderHistory({ detail: [{ resolve: () => gate.promise }] });
    await screen.findByTestId('history-list');

    fireEvent.click(screen.getByTestId('history-row-select-dec-21'));
    expect(screen.getByTestId('history-state-loading')).toBeInTheDocument();
    gate.resolve(approveRecord);
    await screen.findByTestId('history-detail');
  });

  it('list --select--> detailLoading -> detailError, and detailError --retry--> detailLoading -> detail', async () => {
    const gate = deferred();
    const seam = renderHistory({
      detail: [{ reject: notFoundEnvelope }, { resolve: () => gate.promise }],
    });
    await screen.findByTestId('history-list');

    fireEvent.click(screen.getByTestId('history-row-select-dec-22'));
    await screen.findByTestId('history-state-error-detail');

    fireEvent.click(screen.getByTestId('history-error-retry'));
    expect(screen.getByTestId('history-state-loading')).toBeInTheDocument();
    gate.resolve(approveRecord);
    await screen.findByTestId('history-detail');
    expect(seam.fetchDetail.calls).toEqual([['dec-22'], ['dec-22']]);
  });

  it('list --page--> listLoading -> list', async () => {
    const gate = deferred();
    renderHistory({
      list: [{ resolve: makeListBody({ page: 2 }) }, { resolve: () => gate.promise }],
    });
    await screen.findByTestId('history-list');

    fireEvent.click(screen.getByTestId('history-pagination-next'));
    expect(screen.getByTestId('history-state-loading')).toBeInTheDocument();
    gate.resolve(makeListBody({ page: 3 }));
    await waitFor(() => expect(screen.getByTestId('history-page-indicator')).toHaveTextContent('3 / 3'));
  });

  it('detail --back--> list (a pure state transition, no loading leg, no refetch)', async () => {
    const seam = renderHistory({ detail: [{ resolve: approveRecord }] });
    await screen.findByTestId('history-list');
    fireEvent.click(screen.getByTestId('history-row-select-dec-21'));
    await screen.findByTestId('history-detail');

    fireEvent.click(screen.getByTestId('history-detail-back'));
    // straight to `list` — Back never passes through listLoading, because it never re-reads.
    expect(screen.getByTestId('history-list')).toBeInTheDocument();
    expect(screen.queryByTestId('history-state-loading')).toBeNull();
    expect(seam.fetchList.calls).toHaveLength(1);
  });
});
