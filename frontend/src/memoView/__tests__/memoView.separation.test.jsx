import { describe, it, expect } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { MemoView } from '../MemoView.jsx';
import { unsortedReadyMemoView } from './fixtures.js';

// SEPARATION-1 (the LOAD-BEARING target, Q2-A / Fold-B) — the DOM-containment teeth. The RO region is a
// DISTINCT, non-nested DOM node from the L narrative; recommendation/confidence render EXCLUSIVELY
// inside the RO region. The test FAILS if the recommendation were rendered inside/under the narrative.
describe('MemoView — SEPARATION-1: RO region structurally isolated from the L narrative (teeth)', () => {
  it('narrative and readonly are distinct, non-containing nodes; rec/conf only in RO; aria-readonly', async () => {
    const seam = async () => unsortedReadyMemoView;
    render(<MemoView memoFetchSeam={seam} applicationId="app-1" />);

    const readonly = await screen.findByTestId('memo-region-readonly');
    const narrative = screen.getByTestId('memo-region-narrative');

    // distinct nodes, neither an ancestor/descendant of the other (jsdom Node.contains, Fold-B).
    expect(readonly).not.toBe(narrative);
    expect(narrative.contains(readonly)).toBe(false);
    expect(readonly.contains(narrative)).toBe(false);

    // recommendation/confidence present INSIDE the RO region.
    expect(within(readonly).getByTestId('memo-recommendation')).toBeInTheDocument();
    expect(within(readonly).getByTestId('memo-confidence')).toBeInTheDocument();

    // ...and NOT inside the narrative region (the teeth).
    expect(within(narrative).queryByTestId('memo-recommendation')).toBeNull();
    expect(within(narrative).queryByTestId('memo-confidence')).toBeNull();

    // the RO region carries aria-readonly (the frozen ui-shell ReadOnlyRegion).
    expect(readonly).toHaveAttribute('aria-readonly', 'true');
  });
});
