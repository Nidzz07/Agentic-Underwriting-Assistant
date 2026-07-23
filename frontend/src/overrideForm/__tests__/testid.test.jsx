import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OverrideConfirmDialog } from '../components/OverrideConfirmDialog.jsx';
import { CommittedConfirmation } from '../components/CommittedConfirmation.jsx';
import { isValidOverrideTestid } from '../../../eslint-rules/overrideForm.js';
import { makeCommittedOverride, makeMemoView } from './fixtures.js';

// TESTID-1 (presence) — the assertion-relevant override-* testids exist and follow the convention,
// INCLUDING the distinct override-confirm-reason-echo (pre-submission client reason state) vs
// override-committed-reason (post-submission decision.reason echo) — Q6 / ND-OVR-Fold-ii.
describe('TESTID-1 — override-<element>-<purpose> presence', () => {
  it('the confirm dialog testids are present and convention-valid', () => {
    render(<OverrideConfirmDialog onConfirm={() => {}} onCancel={() => {}} reason="because X" />);
    for (const id of ['override-confirm-dialog', 'override-confirm-title', 'override-confirm-body', 'override-confirm-reason-echo', 'override-confirm-submit', 'override-confirm-cancel']) {
      expect(screen.getByTestId(id)).toBeInTheDocument();
    }
  });

  it('the committed-confirmation testids are present and convention-valid', () => {
    render(<CommittedConfirmation decision={makeCommittedOverride()} context={makeMemoView()} />);
    for (const id of ['override-committed-view', 'override-committed-title', 'override-committed-recommendation', 'override-committed-action', 'override-committed-by', 'override-committed-reason']) {
      expect(screen.getByTestId(id)).toBeInTheDocument();
    }
  });

  it('the confirm-echo and the committed-reason testids are DISTINCT (Q6 — two states, two sources)', () => {
    expect('override-confirm-reason-echo').not.toBe('override-committed-reason');
    const { unmount } = render(<OverrideConfirmDialog onConfirm={() => {}} onCancel={() => {}} reason="r" />);
    expect(screen.getByTestId('override-confirm-reason-echo')).toBeInTheDocument();
    expect(screen.queryByTestId('override-committed-reason')).toBeNull(); // NOT the committed node
    unmount();
    render(<CommittedConfirmation decision={makeCommittedOverride()} context={makeMemoView()} />);
    expect(screen.getByTestId('override-committed-reason')).toBeInTheDocument();
    expect(screen.queryByTestId('override-confirm-reason-echo')).toBeNull(); // NOT the confirm-echo node
  });

  it('every override-* testid rendered follows the convention', () => {
    render(<CommittedConfirmation decision={makeCommittedOverride()} context={makeMemoView()} />);
    const ids = Array.from(document.querySelectorAll('[data-testid]'))
      .map((n) => n.getAttribute('data-testid'))
      .filter((t) => t.startsWith('override-'));
    expect(ids.length).toBeGreaterThan(0);
    ids.forEach((t) => expect(isValidOverrideTestid(t)).toBe(true));
  });
});
