import { useState, useEffect, useCallback } from 'react';
import { Panel } from '../shell/components/Panel.jsx';
import { QueueStateView } from './components/QueueStateView.jsx';
import { QueueTable } from './components/QueueTable.jsx';
import { PaginationControls } from './components/PaginationControls.jsx';
import { DEFAULT_PAGE_SIZE } from './fetchSeam.js';

// C1 — the ONLY stateful component. FourStateMachinePattern (P5 / FETCH-1): loading -> ready|empty|error;
// error --Retry--> loading; ready --page--> loading. Retry re-fetches the LAST-requested page
// (Fold-B / RETRY-1, position-preserving). `fetchSeam` is INJECTED as a prop (Q3-A). RoleInvariant:
// reads NO Role, composes NO RoleGate (VIEWONLY-1). Emits onSelect upward only (no router, SELECT-1).
export function QueueView({ fetchSeam, onSelect, size = DEFAULT_PAGE_SIZE, testid = 'queue-view' }) {
  const [state, setState] = useState('loading');
  const [page, setPage] = useState(1);
  const [items, setItems] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, size, total: 0 });
  const [error, setError] = useState(null);

  const load = useCallback(async (targetPage) => {
    setState('loading');
    setError(null);
    try {
      const body = await fetchSeam(targetPage, size);
      setItems(body.items);
      setPageInfo(body.page);
      setPage(body.page.page);
      setState(body.items.length === 0 ? 'empty' : 'ready');
    } catch (envelope) {
      // envelope is always a well-formed { error: {...} } (CG-Fold-1).
      setError(envelope);
      setPage(targetPage); // preserve position so Retry re-fetches THIS page (Fold-B).
      setState('error');
    }
  }, [fetchSeam, size]);

  useEffect(() => { load(1); }, [load]);

  const onRetry = useCallback(() => { load(page); }, [load, page]);       // last-requested page (Fold-B)
  const onPageChange = useCallback((next) => { load(next); }, [load]);

  return (
    <Panel testid={testid}>
      {state === 'ready' ? (
        <>
          <QueueTable items={items} onSelect={onSelect} />
          <PaginationControls
            page={pageInfo.page}
            size={pageInfo.size}
            total={pageInfo.total}
            onPageChange={onPageChange}
          />
        </>
      ) : (
        <QueueStateView state={state} error={error} onRetry={onRetry} />
      )}
    </Panel>
  );
}

export default QueueView;
