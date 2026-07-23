import { CONFIDENCE_LABELS } from '../copy/index.js';

// C2 — looks up its label from shell/copy BY VALUE (BR-UI-1 / COPY-1).
// value in {High, Medium, Low}.
export function ConfidenceBadge({ value, testid = 'shell-confidencebadge-value' }) {
  return (
    <span data-testid={testid} className="shell-badge shell-badge-confidence">
      {CONFIDENCE_LABELS[value]}
    </span>
  );
}

export default ConfidenceBadge;
