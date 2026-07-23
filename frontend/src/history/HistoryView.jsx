import { useState, useEffect, useCallback } from 'react';
import { Panel } from '../shell/components/Panel.jsx';
import { HistoryStateView } from './components/HistoryStateView.jsx';
import { HistoryList } from './components/HistoryList.jsx';
import { HistoryPagination } from './components/HistoryPagination.jsx';
import { DecisionDetail } from './components/DecisionDetail.jsx';
import { HISTORY_COPY } from './copy.js';

const DEFAULT_PAGE_SIZE = 20;

// C1 — the ONLY fetch-stateful component and the SOLE holder of the injected `fetchSeam`
// (`{ fetchList, fetchDetail }`, Q1-A prop injection; the real transport is wired at the composition
// root — deferred). It owns the seven-state MasterDetailStateMachinePattern (P5 / STATEMACHINE-1):
//   listLoading -> list | listEmpty | listError ;  list --select--> detailLoading -> detail | detailError
//   listError --retry--> listLoading ;  detailError --retry--> detailLoading ;  list --page--> listLoading
//   detail --back--> list
//
// StateRetentionAcrossNavigationPattern (P6 / BACKPRESERVE-1): `{page, items, pageInfo}` live HERE, so
// entering `detail` is a SUB-STATE, not a remount — Back returns to the list at the SAME page with the
// SAME rows and issues NO new fetch (the frozen QueueView position-preserving discipline, extended to
// a master-detail navigation).
// PerOperationRetryTargetingPattern (P8 / ERROR-1): Retry is targeted per-operation — a listError
// re-fetches the LAST-REQUESTED page (never page 1), a detailError re-fetches the SAME decision_id.
// ArrayLengthEmptyPattern (P7 / EMPTY-1): `listEmpty` is derived from `items.length` (an array-length
// check — deliberately NOT ui-memo-view's `status` discriminator, which has no analog in R6).
// RoleInvariantRenderingPattern (P11 / VIEWONLY-1): reads NO Role, composes NO RoleGate (`can="read"`
// is deliberately unused — it would cosmetically exclude `admin`, diverging from R6/R7's
// authenticated-any-role contract), imports NO router. The auditor read-only distinction is enforced
// server-side (auth-rbac SEC-4), not here.
// INV-FAITHFUL (P3 / FAITHFUL-1): holds NO write/commit reference — there is no write path in this
// unit at all. It emits nothing upward.
export function HistoryView({ fetchSeam, size = DEFAULT_PAGE_SIZE, testid = 'history-view' }) {
  const [state, setState] = useState('listLoading');
  const [page, setPage] = useState(1);
  const [items, setItems] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, size, total: 0 });
  const [record, setRecord] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [error, setError] = useState(null);

  const loadList = useCallback(async (targetPage) => {
    setState('listLoading');
    setError(null);
    try {
      const body = await fetchSeam.fetchList(targetPage, size);
      setItems(body.items);
      setPageInfo(body.page);
      setPage(body.page.page);
      setState(body.items.length === 0 ? 'listEmpty' : 'list');
    } catch (envelope) {
      // envelope is always a well-formed { error: {...} } (the seam normalizes).
      setError(envelope);
      setPage(targetPage); // preserve position so Retry re-fetches THIS page (HIST-Fold-1).
      setState('listError');
    }
  }, [fetchSeam, size]);

  const loadDetail = useCallback(async (decisionId) => {
    setSelectedId(decisionId); // remember the id so Retry re-fetches THE SAME record (ERROR-1).
    setState('detailLoading');
    setError(null);
    try {
      const body = await fetchSeam.fetchDetail(decisionId);
      setRecord(body);
      setState('detail');
    } catch (envelope) {
      setError(envelope);
      setState('detailError');
    }
  }, [fetchSeam]);

  useEffect(() => { loadList(1); }, [loadList]);

  // Per-operation Retry targeting (P8): the failing READ decides which op is retried, and with what.
  const onRetry = useCallback(() => {
    if (state === 'detailError') {
      loadDetail(selectedId);
    } else {
      loadList(page);
    }
  }, [state, selectedId, page, loadDetail, loadList]);

  const onSelect = useCallback((decisionId) => { loadDetail(decisionId); }, [loadDetail]);
  const onPageChange = useCallback((next) => { loadList(next); }, [loadList]);

  // Back: a pure state transition. It deliberately calls NO loader — `page`/`items`/`pageInfo` were
  // retained across the detail excursion, so the list re-renders at the same position with zero
  // refetch (BACKPRESERVE-1).
  const onBack = useCallback(() => {
    setRecord(null);
    setState('list');
  }, []);

  return (
    <Panel testid={testid}>
      {state === 'list' ? (
        <>
          <HistoryList items={items} onSelect={onSelect} />
          <HistoryPagination
            page={pageInfo.page}
            size={pageInfo.size}
            total={pageInfo.total}
            onPageChange={onPageChange}
          />
        </>
      ) : state === 'detail' ? (
        <>
          <DecisionDetail record={record} />
          <button type="button" data-testid="history-detail-back" onClick={onBack}>
            {HISTORY_COPY.backLabel}
          </button>
        </>
      ) : (
        <HistoryStateView state={state} error={error} onRetry={onRetry} />
      )}
    </Panel>
  );
}

export default HistoryView;
