import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoView } from '../MemoView.jsx';
import { unsortedReadyMemoView } from './fixtures.js';
import { isValidMemoTestid } from '../../../eslint-rules/memoView.js';

// TESTID-1 (MEMO-Fold-2) — the region-level testids (+ rec/conf) are present on a ready memo and
// follow the memo-<element>-<purpose> convention.
describe('TESTID-1 — memo-<element>-<purpose> incl. region testids', () => {
  it('the four region testids + rec/conf render on a ready memo', async () => {
    render(<MemoView memoFetchSeam={async () => unsortedReadyMemoView} applicationId="app-1" />);
    await screen.findByTestId('memo-view');
    for (const id of [
      'memo-region-narrative', 'memo-region-citations', 'memo-region-missinginfo',
      'memo-region-readonly', 'memo-recommendation', 'memo-confidence',
    ]) {
      expect(screen.getByTestId(id)).toBeInTheDocument();
      expect(isValidMemoTestid(id)).toBe(true);
    }
  });

  it('detector self-test (non-vacuous)', () => {
    expect(isValidMemoTestid('memo-region-readonly')).toBe(true);
    expect(isValidMemoTestid('memo-view')).toBe(true);
    expect(isValidMemoTestid('memo-recommendation')).toBe(true);
    expect(isValidMemoTestid('memoView')).toBe(false);
    expect(isValidMemoTestid('shell-panel')).toBe(false);
    expect(isValidMemoTestid('memo_region')).toBe(false);
  });
});
