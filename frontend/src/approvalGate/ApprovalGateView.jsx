import { useState, useEffect, useCallback } from 'react';
import { Panel } from '../shell/components/Panel.jsx';
import { CommitStateView } from './components/CommitStateView.jsx';
import { RecommendationContext } from './components/RecommendationContext.jsx';
import { ApproveAffordance } from './components/ApproveAffordance.jsx';
import { CommitConfirmDialog } from './components/CommitConfirmDialog.jsx';
import { CommittedConfirmation } from './components/CommittedConfirmation.jsx';
import { APPROVAL_COPY } from './copy.js';

// C1 — the ONLY stateful component: the orchestrator. It is the SOLE holder of the injected dual-
// operation `commitFetchSeam` (createCommitFetch's result). It runs the initial R4 read and owns the
// state machine:
//   loading -> ready(idle) -> confirming -> submitting -> { committed | errorCommit }  (+ pending, errorRead)
// SingleCallSiteConfirmGatedCommitPattern (P1): the commit trigger `onConfirm` (which is the ONLY
// place `commitFetchSeam.submitApprove` is invoked) is passed ONLY to CommitConfirmDialog. The
// ApproveAffordance receives only `onApprove` (opens the dialog) — it cannot commit.
//   fetchContext (R4) is invoked by this view (mount + errorRead Retry); its only inbound is the view.
export function ApprovalGateView({ commitFetchSeam, applicationId, testid = 'approval-gate' }) {
  const [phase, setPhase] = useState('loading'); // loading|pending|ready|confirming|submitting|committed|errorRead|errorCommit
  const [view, setView] = useState(null);        // R4 MemoView
  const [error, setError] = useState(null);      // WIRE-1 envelope
  const [committed, setCommitted] = useState(null); // R5 CommittedDecision echo

  const loadContext = useCallback(async () => {
    setPhase('loading');
    setError(null);
    try {
      const body = await commitFetchSeam.fetchContext(applicationId);
      setView(body);
      // ready only when a recommendation exists to approve; else pending (AG-Fold-5).
      setPhase(body.status === 'ready' && body.recommendation_id ? 'ready' : 'pending');
    } catch (envelope) {
      setError(envelope);
      setPhase('errorRead');
    }
  }, [commitFetchSeam, applicationId]);

  useEffect(() => { loadContext(); }, [loadContext]);

  const onApprove = useCallback(() => setPhase('confirming'), []);       // opens the dialog (no commit)
  const onCancel = useCallback(() => setPhase('ready'), []);             // pure toggle back to ready
  const onRetryRead = useCallback(() => loadContext(), [loadContext]);   // errorRead Retry (same applicationId)
  const onBackToReview = useCallback(() => setPhase('ready'), []);       // errorCommit -> ready (never resubmit)

  // The commit trigger — the ONLY invocation of submitApprove — passed ONLY to CommitConfirmDialog.
  const onConfirm = useCallback(async () => {
    setPhase('submitting');
    try {
      const decision = await commitFetchSeam.submitApprove(view.recommendation_id);
      setCommitted(decision);
      setPhase('committed');
    } catch (envelope) {
      setError(envelope);
      setPhase('errorCommit');
    }
  }, [commitFetchSeam, view]);

  if (phase === 'loading' || phase === 'pending' || phase === 'errorRead' || phase === 'errorCommit') {
    return (
      <Panel testid="approval-panel">
        <CommitStateView state={phase} error={error} onRetry={onRetryRead} onBack={onBackToReview} />
      </Panel>
    );
  }

  if (phase === 'committed') {
    return (
      <Panel testid="approval-panel">
        <CommittedConfirmation decision={committed} context={view} />
      </Panel>
    );
  }

  // ready | confirming | submitting
  return (
    <Panel testid="approval-panel">
      <div data-testid={testid}>
        <RecommendationContext
          recommendation={view.report.recommendation}
          confidence={view.report.confidence}
        />
        <ApproveAffordance onApprove={onApprove} />
        {phase === 'confirming' ? (
          <CommitConfirmDialog onConfirm={onConfirm} onCancel={onCancel} />
        ) : null}
        {phase === 'submitting' ? (
          <div data-testid="approval-state-submitting" aria-busy="true">{APPROVAL_COPY.submittingLabel}</div>
        ) : null}
      </div>
    </Panel>
  );
}

export default ApprovalGateView;
