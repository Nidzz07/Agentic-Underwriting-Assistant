import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderHistory, makeListBody, approveRecord } from './fixtures.js';

// DUALREAD-1 (NFR-HIST-Fold-A) — READ-ATTRIBUTION teeth across the single injected dual-read double.
// Because both operations are READS there is no "zero write calls" gate (contrast U7/U8); the
// load-bearing count teeth are instead: a select hits fetchDetail ONLY, a page change hits fetchList
// ONLY. The test FAILS on any cross-attribution.
describe('HistoryView — DUALREAD-1: read attribution (teeth)', () => {
  it('selecting a row records ONE fetchDetail with that decision_id and ZERO new fetchList', async () => {
    const seam = renderHistory({ detail: [{ resolve: approveRecord }] });
    await screen.findByTestId('history-row-dec-21');

    // the mount fetch has happened; snapshot before the select.
    expect(seam.fetchList.calls).toHaveLength(1);
    expect(seam.fetchDetail.calls).toHaveLength(0);

    fireEvent.click(screen.getByTestId('history-row-select-dec-22'));
    await screen.findByTestId('history-detail');

    // exactly one detail read, for THAT id — and NOT a single extra list read (the teeth).
    expect(seam.fetchDetail.calls).toEqual([['dec-22']]);
    expect(seam.fetchList.calls).toHaveLength(1);
  });

  it('a page change records ONE fetchList for the target page and ZERO fetchDetail', async () => {
    const seam = renderHistory({
      list: [{ resolve: makeListBody({ page: 2 }) }, { resolve: makeListBody({ page: 3 }) }],
    });
    await screen.findByTestId('history-list');
    expect(seam.fetchList.calls).toEqual([[1, 20]]);

    fireEvent.click(screen.getByTestId('history-pagination-next'));
    await screen.findByTestId('history-list');

    // the second list read targets page 3 (page 2 + 1) — and NO detail read fired (the teeth).
    expect(seam.fetchList.calls).toHaveLength(2);
    expect(seam.fetchList.calls[1]).toEqual([3, 20]);
    expect(seam.fetchDetail.calls).toHaveLength(0);
  });

  it('both reads flow through ONE injected seam prop — HistoryView imports no hard-wired fetch', async () => {
    const seam = renderHistory({ detail: [{ resolve: approveRecord }] });
    await screen.findByTestId('history-list');
    fireEvent.click(screen.getByTestId('history-row-select-dec-21'));
    await screen.findByTestId('history-detail');
    // the same injected object served both operations (BR-HIST-4: one seam, two reads).
    expect(seam.fetchList.calls).toHaveLength(1);
    expect(seam.fetchDetail.calls).toHaveLength(1);
  });
});
