import { useState, useEffect, useCallback } from 'react';
import { Panel } from '../shell/components/Panel.jsx';
import { MemoStateView } from './components/MemoStateView.jsx';
import { ProfileContextHeader } from './components/ProfileContextHeader.jsx';
import { NarrativeRegion } from './components/NarrativeRegion.jsx';
import { MissingInfoRegion } from './components/MissingInfoRegion.jsx';
import { ReadOnlyRecommendationRegion } from './components/ReadOnlyRecommendationRegion.jsx';

// C1 — the ONLY stateful component. FourStateMachinePattern (P5 / FETCH-1):
//   loading -> ready | pending | error ;  error --Retry--> loading (re-fetch the SAME applicationId,
//   ERROR-1 — a single resource, no page position to preserve).
// StatusDiscriminatorPattern (P6 / PENDING-1): `pending` is derived from the R4 `status` DISCRIMINATOR
//   (`view.status`), NOT from an array-length check. `memoFetchSeam` is INJECTED as a prop (Q2-A).
// RoleInvariant: reads NO Role, composes NO RoleGate (VIEWONLY-1). Emits nothing (view-only, no router).
//
// StructuralIsolationCompositionPattern (P2 / SEPARATION-1) — the three regions are composed as
// SIBLINGS here: NarrativeRegion (L), MissingInfoRegion (D), ReadOnlyRecommendationRegion (RO). The RO
// region is the SOLE holder of recommendation/confidence; NarrativeRegion receives ONLY
// { narrative, citedRuleIds } — there is no wired path to render the recommendation inside the narrative.
export function MemoView({ memoFetchSeam, applicationId, testid = 'memo-view' }) {
  const [state, setState] = useState('loading');
  const [view, setView] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setState('loading');
    setError(null);
    try {
      const body = await memoFetchSeam(applicationId);
      setView(body);
      // pending derived from the status DISCRIMINATOR (not list emptiness).
      setState(body.status === 'ready' ? 'ready' : 'pending');
    } catch (envelope) {
      // envelope is always a well-formed { error: {...} } (CG-MEMO-Fold-1).
      setError(envelope);
      setState('error');
    }
  }, [memoFetchSeam, applicationId]);

  useEffect(() => { load(); }, [load]);

  const onRetry = useCallback(() => { load(); }, [load]);   // re-fetch the SAME applicationId (ERROR-1)

  if (state !== 'ready') {
    return (
      <Panel>
        <MemoStateView state={state} error={error} onRetry={onRetry} />
      </Panel>
    );
  }

  const memo = view.memo;
  return (
    <Panel>
      <div data-testid={testid}>
        <ProfileContextHeader profile={view.profile} />
        <NarrativeRegion narrative={memo.narrative_prose} citedRuleIds={memo.cited_rule_ids} />
        <MissingInfoRegion items={memo.missing_information} />
        <ReadOnlyRecommendationRegion recommendation={memo.recommendation} confidence={memo.confidence} />
      </div>
    </Panel>
  );
}

export default MemoView;
