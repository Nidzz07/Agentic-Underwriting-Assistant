import { describe, it, expect } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { NarrativeRegion } from '../components/NarrativeRegion.jsx';

// L region — renders narrative prose, composes the citations list, and (by construction) holds NO
// recommendation/confidence node (SEPARATION-1 at the component level).
describe('NarrativeRegion — L region', () => {
  it('renders narrative prose and composes the citations list; no rec/conf inside', () => {
    render(<NarrativeRegion narrative="Meets the threshold." citedRuleIds={['R-1']} />);
    const region = screen.getByTestId('memo-region-narrative');
    expect(region).toHaveTextContent('Meets the threshold.');
    expect(within(region).getByTestId('memo-region-citations')).toBeInTheDocument();
    expect(within(region).queryByTestId('memo-recommendation')).toBeNull();
    expect(within(region).queryByTestId('memo-confidence')).toBeNull();
  });

  it('renders with no citations (default prop) -> neutral citations copy', () => {
    render(<NarrativeRegion narrative="x" />);
    expect(screen.getByTestId('memo-region-citations')).toHaveTextContent('No rules cited');
  });
});
