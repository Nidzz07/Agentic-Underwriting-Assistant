import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CommittedConfirmation } from '../components/CommittedConfirmation.jsx';
import { COMMIT_ACTION_LABELS, RECOMMENDATION_LABELS } from '../../shell/copy/index.js';
import { FORBIDDEN_TERMS } from '../../shell/copy/forbiddenTerms.js';
import { LINT_FORBIDDEN_TERMS } from '../../../eslint-rules/index.js';
import { makeCommittedOverride, makeMemoView } from './fixtures.js';

// NAMESPACE-1 — the human `override` (CommitAction namespace) is rendered from COMMIT_ACTION_LABELS,
// NEVER as/with the system Recommendation namespace (esp. never DECLINE-RECOMMEND); and the ONE
// FORBIDDEN_TERMS source is reused (no second word-list). BR-OVR-7: the human "override" (I disagree)
// must never read as the system verdict.
describe('NAMESPACE-1', () => {
  it('renders the human action label from COMMIT_ACTION_LABELS (not a Recommendation label)', () => {
    render(<CommittedConfirmation decision={makeCommittedOverride({ action: 'override' })} context={makeMemoView()} />);
    expect(screen.getByTestId('override-committed-action')).toHaveTextContent(COMMIT_ACTION_LABELS.override); // 'Override'
  });

  it('the committed ACTION node is never a Recommendation label (esp. never DECLINE-RECOMMEND)', () => {
    render(<CommittedConfirmation decision={makeCommittedOverride({ action: 'override' })} context={makeMemoView()} />);
    const actionText = screen.getByTestId('override-committed-action').textContent;
    for (const label of Object.values(RECOMMENDATION_LABELS)) {
      expect(actionText).not.toBe(label);
    }
    expect(actionText).not.toBe(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']); // 'Decline-Recommend'
  });

  it('reuses the single FORBIDDEN_TERMS source object (no second word-list)', () => {
    expect(LINT_FORBIDDEN_TERMS).toBe(FORBIDDEN_TERMS);
  });
});
