import { useState, useEffect, useCallback } from 'react';
import { Panel } from '../shell/components/Panel.jsx';
import { ReadOnlyRegion } from '../shell/components/ReadOnlyRegion.jsx';
import { OUTLIER_COPY } from './copy.js';
import { OutlierStateView } from './components/OutlierStateView.jsx';
import { OutlierScoreRegion } from './components/OutlierScoreRegion.jsx';
import { FlaggedFeaturesRegion } from './components/FlaggedFeaturesRegion.jsx';

// C-OUTV-1 (OutlierView) — MANDATORY header comment (NFR-ND-OUTV-Fold-1).
//
// The ONLY stateful component. FieldDerivedStateMachinePattern (P-OUTV-1 / STATE-1) — LOAD-BEARING:
//
//   State derivation is FAILURE-FIRST. A rejected fetch is routed to ERROR on a branch evaluated
//   BEFORE the `outlier`-null check is ever reached, so NOT_AVAILABLE is UNWRITABLE from a failure
//   path — the "not available" state can never mask a genuine error. See `derive()` below: the
//   REJECTED branch returns first; the null check is only reachable on the resolved (2xx) branch.
//
//   The discriminator is the `outlier` FIELD on a resolved response — NOT the R4 `status`. Contrast
//   the frozen ui-memo-view StatusDiscriminatorPattern (its `pending` derives from `view.status`):
//   here a Phase-1 `status:"ready"` body can STILL carry `outlier: null`, so a status-keyed
//   implementation would be wrong. Both null-causes (`pending`, and `ready`+null) render
//   NOT_AVAILABLE.
//
// RoleInvariant (P-OUTV-8 / VIEWONLY-1): reads NO Role, composes NO RoleGate, imports no router,
// exposes no commit affordance. Emits NOTHING upward. `fetchSeam` is INJECTED as a prop (Q1-A).
//
// Documentation only — NOT enforcement. The enforcement is the branch ORDERING in `derive()` plus
// the prop signatures of the two regions (which carry no verdict/provenance path at all).
export const OUTLIER_STATE = Object.freeze({
  LOADING: 'loading',
  READY: 'ready',
  NOT_AVAILABLE: 'not_available',
  ERROR: 'error',
});

const FETCH_STATE = Object.freeze({
  PENDING: 'pending',
  RESOLVED: 'resolved',
  REJECTED: 'rejected',
});

// The failure-first ordering, isolated so it is legible (and testable) as a pure function.
//   (1) a REJECTED fetch returns ERROR before ANY field is read
//   (2) the outlier-null check is reachable ONLY after (1) has not returned
export function deriveOutlierState(fetchState, view) {
  if (fetchState === FETCH_STATE.REJECTED) return OUTLIER_STATE.ERROR;
  if (fetchState === FETCH_STATE.PENDING) return OUTLIER_STATE.LOADING;
  if (view.outlier === null || view.outlier === undefined) return OUTLIER_STATE.NOT_AVAILABLE;
  return OUTLIER_STATE.READY;
}

export function OutlierView({ fetchSeam, applicationId, testid = 'outlier-view' }) {
  const [fetchState, setFetchState] = useState(FETCH_STATE.PENDING);
  const [view, setView] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setFetchState(FETCH_STATE.PENDING);
    setError(null);
    try {
      const body = await fetchSeam(applicationId);
      setView(body);
      setFetchState(FETCH_STATE.RESOLVED);
    } catch (envelope) {
      // envelope is always a well-formed { error: {...} } (fetchSeam normalization).
      setError(envelope);
      setFetchState(FETCH_STATE.REJECTED);
    }
  }, [fetchSeam, applicationId]);

  useEffect(() => { load(); }, [load]);

  const onRetry = useCallback(() => { load(); }, [load]);  // re-fetch the SAME applicationId (ERROR-1)

  const state = deriveOutlierState(fetchState, view ?? {});

  if (state !== OUTLIER_STATE.READY) {
    return (
      <Panel title={OUTLIER_COPY.panelHeading}>
        <OutlierStateView state={state} error={error} onRetry={onRetry} />
      </Panel>
    );
  }

  const outlier = view.outlier;
  return (
    <Panel title={OUTLIER_COPY.panelHeading}>
      <ReadOnlyRegion testid="outlier-region-readonly">
        <div data-testid={testid}>
          <p>{OUTLIER_COPY.advisoryNote}</p>
          <OutlierScoreRegion outlierScore={outlier.outlier_score} isOutlier={outlier.is_outlier} />
          <FlaggedFeaturesRegion flaggedFeatures={outlier.flagged_features} />
        </div>
      </ReadOnlyRegion>
    </Panel>
  );
}

export default OutlierView;
