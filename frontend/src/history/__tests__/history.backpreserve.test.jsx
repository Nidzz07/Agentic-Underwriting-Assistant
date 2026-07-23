import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderHistory, approveRecord, pageKRows, PAGE_K } from './fixtures.js';

// BACKPRESERVE-1 (NFR-HIST-Fold-2) — the position-preserving Back teeth. Returning from `detail` to
// `list` must preserve the page position and the rows and issue NO new list fetch. Because a FRESH
// double is constructed per test and RTL auto-cleans, a simple BEFORE/AFTER SNAPSHOT of
// `fetchList.calls.length` around the Back action is sufficient — no double-side discrimination.
// The test FAILS if Back reset to page 1 or triggered a refetch.
describe('HistoryView — BACKPRESERVE-1: Back preserves position and refetches nothing (teeth)', () => {
  it('Back adds ZERO fetchList calls and restores page k with the same rows in the same order', async () => {
    const seam = renderHistory({ detail: [{ resolve: approveRecord }] });
    await screen.findByTestId('history-list');

    // the list is at page k (k >= 2) — a page the "reset to page 1" bug would visibly lose.
    expect(screen.getByTestId('history-page-indicator')).toHaveTextContent(`${PAGE_K} / 3`);
    const rowsBefore = screen.getAllByRole('listitem').map((li) => li.dataset.testid);
    expect(rowsBefore).toEqual(pageKRows.map((r) => `history-row-${r.decision_id}`));

    // excursion into the detail...
    fireEvent.click(screen.getByTestId('history-row-select-dec-22'));
    await screen.findByTestId('history-detail');

    // BEFORE snapshot, taken immediately around the Back action.
    const listCallsBeforeBack = seam.fetchList.calls.length;
    fireEvent.click(screen.getByTestId('history-detail-back'));
    await screen.findByTestId('history-list');

    // (a) ZERO refetch — the teeth.
    expect(seam.fetchList.calls.length).toBe(listCallsBeforeBack);
    expect(seam.fetchList.calls).toHaveLength(1); // still only the mount read

    // (b) same page, same rows, same order.
    expect(screen.getByTestId('history-page-indicator')).toHaveTextContent(`${PAGE_K} / 3`);
    expect(screen.getAllByRole('listitem').map((li) => li.dataset.testid)).toEqual(rowsBefore);
  });

  it('the detail excursion is a SUB-STATE, not a remount: the list survives it intact', async () => {
    const seam = renderHistory({ detail: [{ resolve: approveRecord }] });
    await screen.findByTestId('history-list');

    fireEvent.click(screen.getByTestId('history-row-select-dec-21'));
    await screen.findByTestId('history-detail');
    // while in detail the list is not rendered...
    expect(screen.queryByTestId('history-list')).toBeNull();

    fireEvent.click(screen.getByTestId('history-detail-back'));
    await screen.findByTestId('history-list');
    // ...and the detail is gone, with no extra read of EITHER kind beyond the one select.
    expect(screen.queryByTestId('history-detail')).toBeNull();
    expect(seam.fetchList.calls).toHaveLength(1);
    expect(seam.fetchDetail.calls).toHaveLength(1);
  });
});
