import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CommitConfirmDialog } from '../components/CommitConfirmDialog.jsx';
import { CommittedConfirmation } from '../components/CommittedConfirmation.jsx';
import { isValidApprovalTestid } from '../../../eslint-rules/approvalGate.js';
import { makeCommittedDecision, makeMemoView } from './fixtures.js';

// TESTID-1 (presence) — the assertion-relevant approval-* testids exist and follow the convention.
describe('TESTID-1 — approval-<element>-<purpose> presence', () => {
  it('the confirm dialog testids are present and convention-valid', () => {
    render(<CommitConfirmDialog onConfirm={() => {}} onCancel={() => {}} />);
    for (const id of ['approval-confirm-dialog', 'approval-confirm-title', 'approval-confirm-body', 'approval-confirm-submit', 'approval-confirm-cancel']) {
      expect(screen.getByTestId(id)).toBeInTheDocument();
    }
  });

  it('the committed-confirmation testids are present and convention-valid', () => {
    render(<CommittedConfirmation decision={makeCommittedDecision()} context={makeMemoView()} />);
    for (const id of ['approval-committed', 'approval-committed-title', 'approval-committed-recommendation', 'approval-committed-action', 'approval-committed-by']) {
      expect(screen.getByTestId(id)).toBeInTheDocument();
    }
  });

  it('every approval-* testid rendered follows the convention', () => {
    render(<CommittedConfirmation decision={makeCommittedDecision()} context={makeMemoView()} />);
    const ids = Array.from(document.querySelectorAll('[data-testid]'))
      .map((n) => n.getAttribute('data-testid'))
      .filter((t) => t.startsWith('approval-'));
    expect(ids.length).toBeGreaterThan(0);
    ids.forEach((t) => expect(isValidApprovalTestid(t)).toBe(true));
  });
});
