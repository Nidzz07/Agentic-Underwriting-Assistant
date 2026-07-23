import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderHistory, emptyListBody, makeListBody } from './fixtures.js';

// EMPTY-1 (P7) — ArrayLengthEmptyPattern. `listEmpty` is derived from `items.length` — an
// ARRAY-LENGTH check, deliberately NOT ui-memo-view's `status` discriminator (R6's list wrapper
// carries no status field, so the memo pattern has no analog here; this note is the explicit
// anti-regression guard against porting it over). The test FAILS if a non-empty list rendered empty
// or vice-versa.
describe('HistoryView — EMPTY-1: empty state derived from items.length (teeth)', () => {
  it('items: [] renders the single page-level empty state and NO list/pagination', async () => {
    renderHistory({ list: [{ resolve: emptyListBody }] });
    await screen.findByTestId('history-state-empty');

    expect(screen.getByTestId('history-state-empty')).toHaveTextContent('No decisions yet');
    expect(screen.queryByTestId('history-list')).toBeNull();
    expect(screen.queryByTestId('history-pagination')).toBeNull();
  });

  it('a non-empty body renders the list, never the empty state', async () => {
    renderHistory();
    await screen.findByTestId('history-list');

    expect(screen.queryByTestId('history-state-empty')).toBeNull();
    expect(screen.getByTestId('history-pagination')).toBeInTheDocument();
  });

  it('emptiness keys on items.length, not on total: a one-row page is NOT empty', async () => {
    // total > 0 with rows present, and a body whose `total` would mislead a total-based check.
    renderHistory({ list: [{ resolve: makeListBody({ items: [makeListBody().items[0]], total: 1, page: 1 }) }] });
    await screen.findByTestId('history-list');
    expect(screen.queryByTestId('history-state-empty')).toBeNull();
  });

  it('an empty page whose total is non-zero still renders empty (items.length is the discriminator)', async () => {
    renderHistory({ list: [{ resolve: makeListBody({ items: [], total: 45, page: 9 }) }] });
    await screen.findByTestId('history-state-empty');
    expect(screen.queryByTestId('history-list')).toBeNull();
  });
});
