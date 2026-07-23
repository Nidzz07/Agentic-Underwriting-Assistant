import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { RecommendationContext } from '../components/RecommendationContext.jsx';
import { CommittedConfirmation } from '../components/CommittedConfirmation.jsx';
import { CommitStateView } from '../components/CommitStateView.jsx';
import { CommitConfirmDialog } from '../components/CommitConfirmDialog.jsx';
import { APPROVAL_COPY } from '../copy.js';
import { RECOMMENDATION_LABELS, CONFIDENCE_LABELS } from '../../shell/copy/index.js';
import { makeCommittedDecision, makeMemoView, forbiddenEnvelope, conflictEnvelope, invalidEnvelope } from './fixtures.js';

// C4 — RecommendationContext composes the frozen ReadOnlyRegion + badges (label look-up by value).
describe('C4 RecommendationContext', () => {
  it('renders the recommendation + confidence read-only via the frozen primitives', () => {
    render(<RecommendationContext recommendation="DECLINE-RECOMMEND" confidence="Low" />);
    const region = screen.getByTestId('approval-recommendation-context');
    expect(region).toHaveAttribute('aria-readonly', 'true');
    expect(within(region).getByTestId('approval-recommendation')).toHaveTextContent(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
    expect(within(region).getByTestId('approval-confidence')).toHaveTextContent(CONFIDENCE_LABELS.Low);
    expect(screen.getByTestId('approval-context-heading')).toHaveTextContent(APPROVAL_COPY.contextHeading);
  });
});

// C7 — CommittedConfirmation renders from the echo + context (props only, no seam).
describe('C7 CommittedConfirmation', () => {
  it('renders the committed action + committer + recommendation from props only', () => {
    render(<CommittedConfirmation decision={makeCommittedDecision({ underwriter_id: 'u-77' })} context={makeMemoView()} />);
    expect(screen.getByTestId('approval-committed-title')).toHaveTextContent(APPROVAL_COPY.committedTitle);
    expect(screen.getByTestId('approval-committed-by')).toHaveTextContent('u-77');
    expect(screen.getByTestId('approval-committed-recommendation')).toHaveTextContent(RECOMMENDATION_LABELS.APPROVE);
  });
});

// C3 — CommitStateView: loading / pending / errorRead / errorCommit renders.
describe('C3 CommitStateView', () => {
  it('loading shows a single neutral placeholder', () => {
    render(<CommitStateView state="loading" />);
    expect(screen.getByTestId('approval-state-loading')).toHaveTextContent(APPROVAL_COPY.loadingLabel);
  });
  it('pending shows the not-yet-drafted message', () => {
    render(<CommitStateView state="pending" />);
    expect(screen.getByTestId('approval-state-pending')).toHaveTextContent(APPROVAL_COPY.pendingMessage);
  });
  it('errorRead shows message visible, code hidden, and a Retry control', () => {
    const onRetry = vi.fn();
    render(<CommitStateView state="errorRead" error={{ error: { code: 'not_found', message: 'No such application.', detail: {} } }} onRetry={onRetry} />);
    expect(screen.getByTestId('approval-error-message')).toHaveTextContent('No such application.');
    expect(screen.getByTestId('approval-error-code')).toHaveTextContent('not_found');
    expect(screen.getByTestId('approval-error-code')).not.toBeVisible();
    fireEvent.click(screen.getByTestId('approval-error-retry'));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
  it('errorCommit maps forbidden/commit_conflict to friendly copy and shows a Back control', () => {
    const onBack = vi.fn();
    const { rerender } = render(<CommitStateView state="errorCommit" error={forbiddenEnvelope} onBack={onBack} />);
    expect(screen.getByTestId('approval-error-message')).toHaveTextContent(APPROVAL_COPY.notPermittedMessage);
    rerender(<CommitStateView state="errorCommit" error={conflictEnvelope} onBack={onBack} />);
    expect(screen.getByTestId('approval-error-message')).toHaveTextContent(APPROVAL_COPY.conflictMessage);
    rerender(<CommitStateView state="errorCommit" error={invalidEnvelope} onBack={onBack} />);
    expect(screen.getByTestId('approval-error-message')).toHaveTextContent(invalidEnvelope.error.message);
    fireEvent.click(screen.getByTestId('approval-error-back'));
    expect(onBack).toHaveBeenCalledTimes(1);
  });
  it('errorRead with a missing envelope falls back to the unknown-error message', () => {
    render(<CommitStateView state="errorRead" error={null} />);
    expect(screen.getByTestId('approval-error-message')).toHaveTextContent(APPROVAL_COPY.unknownErrorMessage);
  });
});

// C6 — CommitConfirmDialog fires onConfirm / onCancel; rendering it does not commit on its own.
describe('C6 CommitConfirmDialog', () => {
  it('Confirm calls onConfirm; Cancel calls onCancel; neither fires on mere render', () => {
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    render(<CommitConfirmDialog onConfirm={onConfirm} onCancel={onCancel} />);
    expect(screen.getByTestId('approval-confirm-body')).toHaveTextContent(APPROVAL_COPY.confirmBody);
    expect(onConfirm).not.toHaveBeenCalled();
    expect(onCancel).not.toHaveBeenCalled();
    fireEvent.click(screen.getByTestId('approval-confirm-submit'));
    expect(onConfirm).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByTestId('approval-confirm-cancel'));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
