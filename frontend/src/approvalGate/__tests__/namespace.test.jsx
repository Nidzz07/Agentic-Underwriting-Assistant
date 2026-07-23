import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CommittedConfirmation } from '../components/CommittedConfirmation.jsx';
import { COMMIT_ACTION_LABELS } from '../../shell/copy/index.js';
import { FORBIDDEN_TERMS } from '../../shell/copy/forbiddenTerms.js';
import { LINT_FORBIDDEN_TERMS } from '../../../eslint-rules/index.js';
import { makeCommittedDecision, makeMemoView } from './fixtures.js';

// NAMESPACE-1 — the human `approve` (CommitAction namespace) is rendered from COMMIT_ACTION_LABELS,
// never as/with the system Recommendation namespace; and the ONE FORBIDDEN_TERMS source is reused
// (no second word-list).
describe('NAMESPACE-1', () => {
  it('renders the human action label from COMMIT_ACTION_LABELS (not a Recommendation label)', () => {
    render(<CommittedConfirmation decision={makeCommittedDecision({ action: 'approve' })} context={makeMemoView()} />);
    expect(screen.getByTestId('approval-committed-action')).toHaveTextContent(COMMIT_ACTION_LABELS.approve);
  });

  it('the human override label never appears in the approve-only committed render', () => {
    render(<CommittedConfirmation decision={makeCommittedDecision({ action: 'approve' })} context={makeMemoView()} />);
    expect(document.body.innerHTML).not.toContain(COMMIT_ACTION_LABELS.override); // 'Override'
  });

  it('reuses the single FORBIDDEN_TERMS source object (no second word-list)', () => {
    expect(LINT_FORBIDDEN_TERMS).toBe(FORBIDDEN_TERMS);
  });
});
