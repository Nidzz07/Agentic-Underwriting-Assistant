import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueueView } from '../QueueView.jsx';

// RETRY-1 (Fold-B) — Retry re-fetches the LAST-requested page, with TEETH: the test fails if the
// implementation reset to page 1 on retry.
describe('QueueView — RETRY-1: Retry re-fetches the last-requested page (teeth)', () => {
  it('fails on page 2, Retry re-requests page 2 (NOT page 1)', async () => {
    const recorded = [];
    let failPage2 = true;
    const seam = async (page) => {
      recorded.push(page);
      if (page === 2 && failPage2) {
        failPage2 = false;
        throw { error: { code: 'internal_error', message: 'boom', detail: {} } };
      }
      return {
        items: [{ application_id: `app-${page}`, recommendation: 'APPROVE', confidence: 'High' }],
        page: { page, size: 20, total: 40 },
      };
    };

    render(<QueueView fetchSeam={seam} onSelect={() => {}} />);
    await screen.findByTestId('queue-table');                          // page 1 ready
    fireEvent.click(screen.getByTestId('queue-pagination-next'));      // -> page 2 (fails)
    fireEvent.click(await screen.findByTestId('queue-error-retry'));   // retry
    await screen.findByTestId('queue-table');                          // page 2 ready

    // TEETH: the retry re-requested page 2, not page 1.
    expect(recorded[recorded.length - 1]).toBe(2);
    expect(recorded.filter((p) => p === 2).length).toBeGreaterThanOrEqual(2);
    expect(recorded[recorded.length - 1]).not.toBe(1);
  });
});
