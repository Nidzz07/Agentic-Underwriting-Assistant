import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ReadOnlyRecommendationRegion } from '../components/ReadOnlyRecommendationRegion.jsx';
import { RECOMMENDATION_LABELS, CONFIDENCE_LABELS } from '../../shell/copy/index.js';

// COPY-1 (label look-up) + the RO region composes the frozen ReadOnlyRegion (aria-readonly).
describe('ReadOnlyRecommendationRegion — RO region', () => {
  it('composes ReadOnlyRegion (aria-readonly) and renders badges by value look-up', () => {
    render(<ReadOnlyRecommendationRegion recommendation="DECLINE-RECOMMEND" confidence="Low" />);
    const ro = screen.getByTestId('memo-region-readonly');
    expect(ro).toHaveAttribute('aria-readonly', 'true');
    expect(screen.getByTestId('memo-recommendation')).toHaveTextContent(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
    expect(screen.getByTestId('memo-confidence')).toHaveTextContent(CONFIDENCE_LABELS.Low);
  });
});
