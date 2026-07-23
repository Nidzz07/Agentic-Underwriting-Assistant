import { describe, it, expect } from 'vitest';
import { screen, fireEvent, cleanup } from '@testing-library/react';
import {
  renderHistory,
  openDetail,
  makeListBody,
  approveRecord,
  listErrorEnvelope,
  unauthenticatedEnvelope,
  notFoundEnvelope,
  networkEnvelope,
  errorEnvelope,
  DETAIL_NEEDLE,
} from './fixtures.js';

// ERROR-1 (P8, Q8-A) — table-driven over the shared envelope fixtures + the capturing double.
//   message VISIBLE / code via testid only / detail NEVER in the DOM;
//   listError Retry -> the LAST-REQUESTED page (not page 1);  detailError Retry -> the SAME id;
//   the R7 404 flows through the SAME GENERIC detailError path (no dedicated not-found branch).
const LIST_ENVELOPES = [
  ['internal_error', listErrorEnvelope],
  ['unauthenticated', unauthenticatedEnvelope],
  ['network_error', networkEnvelope],
];

const DETAIL_ENVELOPES = [
  ['internal_error', errorEnvelope],
  ['not_found', notFoundEnvelope],
  ['unauthenticated', unauthenticatedEnvelope],
];

describe('HistoryView — ERROR-1: the list error path (table-driven)', () => {
  it.each(LIST_ENVELOPES)('a %s list failure renders message-only, code via testid', async (code, envelope) => {
    renderHistory({ list: [{ reject: envelope }] });
    await screen.findByTestId('history-state-error-list');

    expect(screen.getByTestId('history-error-message')).toHaveTextContent(envelope.error.message);
    const codeNode = screen.getByTestId('history-error-code');
    expect(codeNode).toHaveTextContent(code);
    expect(codeNode).not.toBeVisible(); // code is a testid binding, never visible UI text
  });

  it('error.detail content appears NOWHERE in the DOM', async () => {
    renderHistory({ list: [{ reject: listErrorEnvelope }] });
    await screen.findByTestId('history-state-error-list');
    expect(document.body.innerHTML).not.toContain(DETAIL_NEEDLE);
    expect(screen.queryByText(DETAIL_NEEDLE)).toBeNull();
  });
});

describe('HistoryView — ERROR-1: the detail error path (table-driven)', () => {
  it.each(DETAIL_ENVELOPES)('a %s detail failure renders through the generic detail error path', async (code, envelope) => {
    await openDetail('dec-21', { detail: [{ reject: envelope }] });
    await screen.findByTestId('history-state-error-detail');

    expect(screen.getByTestId('history-error-message')).toHaveTextContent(envelope.error.message);
    expect(screen.getByTestId('history-error-code')).toHaveTextContent(code);
    expect(document.body.innerHTML).not.toContain(DETAIL_NEEDLE);
  });

  it('generic-404 teeth: not_found renders the SAME markup as any other detail error', async () => {
    async function shapeFor(envelope) {
      await openDetail('dec-21', { detail: [{ reject: envelope }] });
      const container = await screen.findByTestId('history-state-error-detail');
      // strip the two envelope-carried values; what remains is the STRUCTURE.
      const shape = container.innerHTML
        .replace(envelope.error.message, '')
        .replace(envelope.error.code, '');
      expect(screen.queryByTestId('history-state-error-notfound')).toBeNull();
      cleanup();
      return shape;
    }

    // A 404 and a plain internal_error produce byte-identical structure — only code/message differ.
    // There is NO dedicated not-found branch, container or message (HIST-Fold-3).
    expect(await shapeFor(notFoundEnvelope)).toBe(await shapeFor(errorEnvelope));
  });
});

describe('HistoryView — ERROR-1: per-operation Retry targeting (teeth)', () => {
  it('a listError Retry re-fetches the LAST-REQUESTED page — never page 1', async () => {
    // succeed at page 2, move to page 3, fail there, then Retry.
    const seam = renderHistory({
      list: [
        { resolve: makeListBody({ page: 2 }) },
        { reject: listErrorEnvelope },
        { resolve: makeListBody({ page: 3 }) },
      ],
    });
    await screen.findByTestId('history-list');
    fireEvent.click(screen.getByTestId('history-pagination-next')); // -> page 3, which fails
    await screen.findByTestId('history-state-error-list');
    expect(seam.fetchList.calls[1]).toEqual([3, 20]);

    fireEvent.click(screen.getByTestId('history-error-retry'));
    await screen.findByTestId('history-list');

    // the Retry targeted page 3 — the position was preserved across the failure (the teeth).
    expect(seam.fetchList.calls).toHaveLength(3);
    expect(seam.fetchList.calls[2]).toEqual([3, 20]);
    expect(seam.fetchList.calls[2][0]).not.toBe(1);
  });

  it('a detailError Retry re-fetches the SAME decision_id, and fires no list read', async () => {
    const seam = await openDetail('dec-22', {
      detail: [{ reject: notFoundEnvelope }, { resolve: approveRecord }],
    });
    await screen.findByTestId('history-state-error-detail');
    expect(seam.fetchDetail.calls).toEqual([['dec-22']]);

    fireEvent.click(screen.getByTestId('history-error-retry'));
    await screen.findByTestId('history-detail');

    // the Retry targeted the SAME id (the teeth) — and did not fall back to the list op.
    expect(seam.fetchDetail.calls).toEqual([['dec-22'], ['dec-22']]);
    expect(seam.fetchList.calls).toHaveLength(1);
  });
});
