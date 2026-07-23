import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueueRow } from '../components/QueueRow.jsx';
import { COMMIT_ACTION_LABELS, RECOMMENDATION_LABELS } from '../../shell/copy/index.js';
import { FORBIDDEN_TERMS } from '../../shell/copy/forbiddenTerms.js';
import { LINT_FORBIDDEN_TERMS } from '../../../eslint-rules/index.js';

function renderRow(summary) {
  return render(<table><tbody><QueueRow summary={summary} onSelect={() => {}} /></tbody></table>);
}

// NAMESPACE-1 — the queue renders only the SYSTEM Recommendation, never a human CommitAction;
// and it reuses the ONE FORBIDDEN_TERMS source (no second word-list).
describe('NAMESPACE-1', () => {
  it('renders the system Recommendation label, never the human override label', () => {
    renderRow({ application_id: 'app-1', recommendation: 'DECLINE-RECOMMEND', confidence: 'Low' });
    expect(screen.getByTestId('queue-row-recommendation-app-1'))
      .toHaveTextContent(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
    // the commit-only 'Override' label (distinct namespace) must not appear anywhere in the queue row
    expect(document.body.innerHTML).not.toContain(COMMIT_ACTION_LABELS.override);
  });

  it('reuses the single FORBIDDEN_TERMS source object (no second word-list)', () => {
    expect(LINT_FORBIDDEN_TERMS).toBe(FORBIDDEN_TERMS);
  });
});
