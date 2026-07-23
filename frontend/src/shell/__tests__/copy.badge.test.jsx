import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import RecommendationBadge from '../components/RecommendationBadge.jsx';
import ConfidenceBadge from '../components/ConfidenceBadge.jsx';
import { RECOMMENDATION_LABELS, CONFIDENCE_LABELS } from '../copy/index.js';

// COPY-1(b) — the badge renders its label by LOOK-UP from the domain value (never an inlined string).

describe('NFR-UI-COPY-1(b) — badges look up their label by value', () => {
  it('RecommendationBadge renders the canonical DECLINE-RECOMMEND label from shell/copy', () => {
    render(<RecommendationBadge value="DECLINE-RECOMMEND" />);
    const el = screen.getByTestId('shell-recommendationbadge-value');
    expect(el).toHaveTextContent(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
    expect(el).toHaveTextContent('Decline-Recommend'); // -RECOMMEND preserved, not a bare "Decline"
  });

  it('RecommendationBadge renders APPROVE and REFER by look-up', () => {
    const { rerender } = render(<RecommendationBadge value="APPROVE" />);
    expect(screen.getByTestId('shell-recommendationbadge-value')).toHaveTextContent(
      RECOMMENDATION_LABELS.APPROVE,
    );
    rerender(<RecommendationBadge value="REFER" />);
    expect(screen.getByTestId('shell-recommendationbadge-value')).toHaveTextContent(
      RECOMMENDATION_LABELS.REFER,
    );
  });

  it('ConfidenceBadge renders its label by look-up', () => {
    render(<ConfidenceBadge value="High" testid="shell-confidencebadge-value" />);
    expect(screen.getByTestId('shell-confidencebadge-value')).toHaveTextContent(
      CONFIDENCE_LABELS.High,
    );
  });
});
