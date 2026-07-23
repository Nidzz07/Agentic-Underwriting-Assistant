import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CommittedConfirmation } from '../components/CommittedConfirmation.jsx';
import { CommitStateView } from '../components/CommitStateView.jsx';
import { OverrideConfirmDialog } from '../components/OverrideConfirmDialog.jsx';
import { OVERRIDE_COPY } from '../copy.js';
import { RECOMMENDATION_LABELS, COMMIT_ACTION_LABELS } from '../../shell/copy/index.js';
import { makeCommittedOverride, makeMemoView, forbiddenEnvelope, conflictEnvelope, invalidEnvelope } from './fixtures.js';

// C8 — CommittedConfirmation renders from the echo + context (props only, no seam); the committed
// reason is sourced from decision.reason (ND-OVR-Fold-ii); the action label is the human namespace.
describe('C8 CommittedConfirmation', () => {
  it('renders the committed action + committer + committed reason + recommendation from props only', () => {
    render(<CommittedConfirmation decision={makeCommittedOverride({ underwriter_id: 'u-77', reason: 'the recorded justification' })} context={makeMemoView()} />);
    expect(screen.getByTestId('override-committed-title')).toHaveTextContent(OVERRIDE_COPY.committedTitle);
    expect(screen.getByTestId('override-committed-by')).toHaveTextContent('u-77');
    expect(screen.getByTestId('override-committed-action')).toHaveTextContent(COMMIT_ACTION_LABELS.override);
    expect(screen.getByTestId('override-committed-recommendation')).toHaveTextContent(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
    expect(screen.getByTestId('override-committed-reason')).toHaveTextContent('the recorded justification');
  });
});

// C3 — CommitStateView: loading / pending / errorRead / errorCommit renders (incl. the dual-cause 409
// and the defensive null-envelope fallback).
describe('C3 CommitStateView', () => {
  it('loading shows a single neutral placeholder', () => {
    render(<CommitStateView state="loading" />);
    expect(screen.getByTestId('override-state-loading')).toHaveTextContent(OVERRIDE_COPY.loadingLabel);
  });
  it('pending shows the not-yet-drafted message', () => {
    render(<CommitStateView state="pending" />);
    expect(screen.getByTestId('override-state-pending')).toHaveTextContent(OVERRIDE_COPY.pendingMessage);
  });
  it('errorRead shows message visible, code hidden, and a Retry control', () => {
    const onRetry = vi.fn();
    render(<CommitStateView state="errorRead" error={{ error: { code: 'not_found', message: 'No such application.', detail: {} } }} onRetry={onRetry} />);
    expect(screen.getByTestId('override-error-message')).toHaveTextContent('No such application.');
    expect(screen.getByTestId('override-error-code')).toHaveTextContent('not_found');
    expect(screen.getByTestId('override-error-code')).not.toBeVisible();
    fireEvent.click(screen.getByTestId('override-error-retry'));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
  it('errorCommit maps forbidden/commit_conflict to friendly copy and shows a Back control', () => {
    const onBack = vi.fn();
    const { rerender } = render(<CommitStateView state="errorCommit" error={forbiddenEnvelope} onBack={onBack} />);
    expect(screen.getByTestId('override-error-message')).toHaveTextContent(OVERRIDE_COPY.notPermittedMessage);
    // the 409 dual-cause: commit_conflict renders ONE conflict state (already-committed OR blank-reason race)
    rerender(<CommitStateView state="errorCommit" error={conflictEnvelope} onBack={onBack} />);
    expect(screen.getByTestId('override-error-message')).toHaveTextContent(OVERRIDE_COPY.conflictMessage);
    rerender(<CommitStateView state="errorCommit" error={invalidEnvelope} onBack={onBack} />);
    expect(screen.getByTestId('override-error-message')).toHaveTextContent(invalidEnvelope.error.message);
    fireEvent.click(screen.getByTestId('override-error-back'));
    expect(onBack).toHaveBeenCalledTimes(1);
  });
  it('errorRead with a missing envelope falls back to the unknown-error message', () => {
    render(<CommitStateView state="errorRead" error={null} />);
    expect(screen.getByTestId('override-error-message')).toHaveTextContent(OVERRIDE_COPY.unknownErrorMessage);
  });
});

// C7 — OverrideConfirmDialog fires onConfirm / onCancel; echoes the reason read-only; neither fires on
// mere render.
describe('C7 OverrideConfirmDialog', () => {
  it('Confirm calls onConfirm; Cancel calls onCancel; the reason is echoed read-only; neither fires on render', () => {
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    render(<OverrideConfirmDialog onConfirm={onConfirm} onCancel={onCancel} reason="my justification" />);
    expect(screen.getByTestId('override-confirm-body')).toHaveTextContent(OVERRIDE_COPY.confirmBody);
    expect(screen.getByTestId('override-confirm-reason-echo')).toHaveTextContent('my justification');
    expect(onConfirm).not.toHaveBeenCalled();
    expect(onCancel).not.toHaveBeenCalled();
    fireEvent.click(screen.getByTestId('override-confirm-submit'));
    expect(onConfirm).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByTestId('override-confirm-cancel'));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
