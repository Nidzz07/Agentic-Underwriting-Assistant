import { RECOMMENDATION_LABELS } from '../copy/index.js';
import { STATUS_ACCENT } from '../tokens/tokens.js';

// C2 — looks up its label from shell/copy BY VALUE and applies a token accent per value.
// Inlines NO display string (BR-UI-1 / COPY-1). value in {APPROVE, REFER, DECLINE-RECOMMEND}.
export function RecommendationBadge({ value, testid = 'shell-recommendationbadge-value' }) {
  return (
    <span
      data-testid={testid}
      className="shell-badge shell-badge-recommendation"
      style={{ color: STATUS_ACCENT[value] }}
    >
      {RECOMMENDATION_LABELS[value]}
    </span>
  );
}

export default RecommendationBadge;
