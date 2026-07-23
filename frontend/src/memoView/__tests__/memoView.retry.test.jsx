import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoView } from '../MemoView.jsx';
import { emptyListsReadyMemoView } from './fixtures.js';

// ERROR-1 Retry (teeth) — Retry re-fetches the SAME applicationId (single resource, no page to
// preserve). The test fails if a different/absent id were fetched on retry.
describe('MemoView — ERROR-1 Retry: re-fetches the same applicationId (teeth)', () => {
  it('fails first, Retry re-requests the same applicationId', async () => {
    const recorded = [];
    let fail = true;
    const seam = async (id) => {
      recorded.push(id);
      if (fail) { fail = false; throw { error: { code: 'internal_error', message: 'boom', detail: {} } }; }
      return emptyListsReadyMemoView;
    };

    render(<MemoView memoFetchSeam={seam} applicationId="app-1" />);
    fireEvent.click(await screen.findByTestId('memo-error-retry'));   // retry
    await screen.findByTestId('memo-region-readonly');                // ready

    // TEETH: both fetches targeted the SAME applicationId.
    expect(recorded).toEqual(['app-1', 'app-1']);
    expect(recorded[recorded.length - 1]).toBe('app-1');
  });
});
