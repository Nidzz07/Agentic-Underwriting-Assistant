import { useState, useEffect, useCallback } from 'react';
import { Panel } from '../shell/components/Panel.jsx';
import { CommitStateView } from './components/CommitStateView.jsx';
import { RecommendationContext } from './components/RecommendationContext.jsx';
import { OverrideReasonInput } from './components/OverrideReasonInput.jsx';
import { OverrideAffordance } from './components/OverrideAffordance.jsx';
import { OverrideConfirmDialog } from './components/OverrideConfirmDialog.jsx';
import { CommittedConfirmation } from './components/CommittedConfirmation.jsx';
import { OVERRIDE_COPY } from './copy.js';

// The SINGLE reason predicate (P2 / REASONGATE-1 / BR-OVR-8). Computed in ONE place and reused for the
// affordance's derived `disabled` AND the onConfirm belt-and-suspenders re-check, so the enablement can
// never drift from a second predicate. The `trim()` is the NON-AUTHORITATIVE UX guard (FD-OVR-Fold-1):
// String.prototype.trim() is NOT byte-identical to Python str.strip() (e.g. U+001C–U+001F / U+0085 pass
// this guard but the backend `_gate` rejects them), so the backend `_gate` remains the single source of
// truth (CON-BR4) and any divergence resolves server-side via the generic 409.
export function isReasonPresent(reason) {
  return reason.trim() !== '';
}

// C1 — the ONLY stateful component: the orchestrator. It is the SOLE holder of the injected dual-
// operation `overrideFetchSeam` (createOverrideFetch's result). It runs the initial R4 read and owns
// TWO orthogonal state slices:
//   - the phase machine: loading -> ready(idle) -> confirming -> submitting -> { committed | errorCommit }
//                        (+ pending, errorRead)
//   - the independent `reason` slice (P8): Cancel/errorCommit set ONLY the phase — they STRUCTURALLY do
//     not call setReason — so the typed reason survives cancel and a commit error by-construction.
// SingleCallSiteConfirmGatedCommitPattern (P1): the commit trigger `onConfirm` (the ONLY place
// `overrideFetchSeam.submitOverride` is invoked, closing over the current reason) is passed ONLY to
// OverrideConfirmDialog. OverrideAffordance receives only `onOverride` (opens the dialog) + a `disabled`
// DERIVED from the single isReasonPresent predicate — it cannot commit and cannot be enabled blank.
//   fetchContext (R4) is invoked by this view (mount + errorRead Retry); its only inbound is the view.
export function OverrideFormView({ overrideFetchSeam, applicationId, testid = 'override-form-view' }) {
  const [phase, setPhase] = useState('loading'); // loading|pending|ready|confirming|submitting|committed|errorRead|errorCommit
  const [view, setView] = useState(null);        // R4 MemoView
  const [error, setError] = useState(null);      // WIRE-1 envelope
  const [committed, setCommitted] = useState(null); // R5 CommittedDecision echo
  const [reason, setReason] = useState('');      // INDEPENDENT reason slice (P8) — orthogonal to `phase`

  const loadContext = useCallback(async () => {
    setPhase('loading');
    setError(null);
    try {
      const body = await overrideFetchSeam.fetchContext(applicationId);
      setView(body);
      // ready only when a recommendation exists to override; else pending (OVR-Fold-5).
      setPhase(body.status === 'ready' && body.recommendation_id ? 'ready' : 'pending');
    } catch (envelope) {
      setError(envelope);
      setPhase('errorRead');
    }
  }, [overrideFetchSeam, applicationId]);

  useEffect(() => { loadContext(); }, [loadContext]);

  const onOverride = useCallback(() => setPhase('confirming'), []);      // opens the dialog (no commit)
  const onCancel = useCallback(() => setPhase('ready'), []);            // pure toggle back to ready; reason preserved (no setReason)
  const onRetryRead = useCallback(() => loadContext(), [loadContext]);  // errorRead Retry (same applicationId)
  const onBackToReview = useCallback(() => setPhase('ready'), []);      // errorCommit -> ready; reason preserved (no setReason)

  // The commit trigger — the ONLY invocation of submitOverride — passed ONLY to OverrideConfirmDialog.
  // It closes over the current reason and re-applies the SAME single isReasonPresent predicate as a
  // belt-and-suspenders guard (ND-OVR-Fold-i): optional insurance only, since the reason is frozen
  // during `confirming` (the editable input belongs to ready(idle)); it guards a future refactor that
  // might make the reason editable during `confirming`, and keeps the one-predicate invariant explicit.
  const onConfirm = useCallback(async () => {
    if (!isReasonPresent(reason)) { setPhase('ready'); return; }
    setPhase('submitting');
    try {
      const decision = await overrideFetchSeam.submitOverride(view.recommendation_id, reason);
      setCommitted(decision);
      setPhase('committed');
    } catch (envelope) {
      setError(envelope);
      setPhase('errorCommit');
    }
  }, [overrideFetchSeam, view, reason]);

  if (phase === 'loading' || phase === 'pending' || phase === 'errorRead' || phase === 'errorCommit') {
    return (
      <Panel testid="override-form-panel">
        <CommitStateView state={phase} error={error} onRetry={onRetryRead} onBack={onBackToReview} />
      </Panel>
    );
  }

  if (phase === 'committed') {
    return (
      <Panel testid="override-form-panel">
        <CommittedConfirmation decision={committed} context={view} />
      </Panel>
    );
  }

  // ready | confirming | submitting
  return (
    <Panel testid="override-form-panel">
      <div data-testid={testid}>
        <RecommendationContext
          recommendation={view.report.recommendation}
          confidence={view.report.confidence}
        />
        {phase === 'ready' ? (
          <>
            {/* editable reason input belongs to ready(idle) only — frozen during confirming (P8) */}
            <OverrideReasonInput value={reason} onChange={setReason} />
            <OverrideAffordance onOverride={onOverride} disabled={!isReasonPresent(reason)} />
          </>
        ) : null}
        {phase === 'confirming' ? (
          <OverrideConfirmDialog onConfirm={onConfirm} onCancel={onCancel} reason={reason} />
        ) : null}
        {phase === 'submitting' ? (
          <div data-testid="override-state-submitting" aria-busy="true">{OVERRIDE_COPY.submittingLabel}</div>
        ) : null}
      </div>
    </Panel>
  );
}

export default OverrideFormView;
