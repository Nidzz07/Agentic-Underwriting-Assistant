import { describe, it, expect } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { RecommendationContext } from '../components/RecommendationContext.jsx';
import { OVERRIDE_COPY } from '../copy.js';
import { RECOMMENDATION_LABELS, CONFIDENCE_LABELS } from '../../shell/copy/index.js';

// COPY-1 (C4) — RecommendationContext composes the frozen ReadOnlyRegion + badges (label look-up BY
// VALUE, so no inlined display label). Engine-attributed heading (the SYSTEM Recommendation being
// overridden, distinct from the human CommitAction).
describe('C4 RecommendationContext', () => {
  it('renders the recommendation + confidence read-only via the frozen primitives (labels by value)', () => {
    render(<RecommendationContext recommendation="DECLINE-RECOMMEND" confidence="Low" />);
    const region = screen.getByTestId('override-recommendation-context');
    expect(region).toHaveAttribute('aria-readonly', 'true');
    expect(within(region).getByTestId('override-recommendation-value')).toHaveTextContent(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
    expect(within(region).getByTestId('override-confidence-value')).toHaveTextContent(CONFIDENCE_LABELS.Low);
    expect(screen.getByTestId('override-context-heading')).toHaveTextContent(OVERRIDE_COPY.contextHeading);
  });
});
