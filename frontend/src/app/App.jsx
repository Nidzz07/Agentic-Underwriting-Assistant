import { useState, useEffect } from 'react';
import { AppFrame } from '../shell/components/AppFrame.jsx';
import { HistoryView } from '../history/HistoryView.jsx';
import { QueueView } from '../queue/QueueView.jsx';
import { MemoView } from '../memoView/MemoView.jsx';
import { ApprovalGateView } from '../approvalGate/ApprovalGateView.jsx';
import { loadCurrentRole } from './sessionClient.js';

// The frontend composition root — the client half of the out-of-band integration pass. Now
// browser-runnable: deploy-config (U23) supplied the bundler/dev-server topology this module's
// original header said it lacked — `main.jsx` + `index.html` exist and compose this via the real
// httpTransport; the frontend-backend wiring pass added the `dev` script and the Vite dev-server
// `/api` proxy so it can be served and reach the backend locally.
//
// ROLE DELIVERY — via the shell's OWN seam, not around it:
// `AppFrame` already hosts the RoleProvider internally (`value={user ? user.role : null}`), and
// its docstring says it is "populated later by WIRE-1". This module IS that population: R1's role
// is handed to AppFrame's `user` prop, and the frozen AppFrame provides the context. Wrapping
// AppFrame in a SECOND RoleProvider would be shadowed by its inner one (nearest provider wins) —
// the shell's seam is used as designed rather than worked around.
//
// WHAT IT MOUNTS, AND WHY (Scope B, wiring pass Q5(c)):
// Scope B made all seven WIRE-1 routes live, retiring the Scope-A premise that a mounted view could
// only ever error. So the primary underwriter journey is now mounted: `ui-queue` always, and — on
// selection — `ui-memo-view` (R4) and `ui-approval-gate` (R5), the smallest slice that proves an
// end-to-end human-in-the-loop approval gate. `ui-history` (R6/R7) stays mounted as before.
// DELIBERATELY STILL UNMOUNTED: `ui-override-form` (Q5(c) excludes the second write path) and
// `ui-outlier-view` (Q4(a): its seam is unregistered, and #17 renders it permanently empty anyway).
//
// SELECTION STATE (no router — Decision 6 upheld): `ui-queue` emits `onSelect(application_id)`
// upward only and owns no router; nobody else owns "which application is open". This root holds
// exactly that one piece of state and passes it down as `applicationId`. No cross-unit navigation
// affordance and NO new display copy are introduced (keeping queue mounted means there is no "back"
// control), so the src/app advisory-vocabulary lint has nothing new to scan.
//
// Role is chrome only (the server is the real gate). `null` = unauthenticated, which every frozen
// UI unit already renders identically for.
export function App({ seams, transport, testid = 'app-root' }) {
  const [role, setRole] = useState(null);
  const [selectedId, setSelectedId] = useState(null); // "which application is open" — owned here (SELECT-1)

  useEffect(() => {
    let cancelled = false;
    // loadCurrentRole fail-closes to null — an unauthenticated shell is a state, not an error.
    loadCurrentRole(transport).then((resolved) => {
      if (!cancelled) setRole(resolved);
    });
    return () => { cancelled = true; };
  }, [transport]);

  return (
    <AppFrame user={role ? { role } : null}>
      <div data-testid={testid}>
        <QueueView fetchSeam={seams.queue} onSelect={setSelectedId} />
        {selectedId ? (
          <>
            {/* Fold 4 — DISCLOSED, not optimized (#15 precedent): MemoView and ApprovalGateView each
                issue their OWN GET /applications/{id}/memo, so a selection makes two identical R4
                requests. Each frozen unit owning its own fetch is the design (it is why
                commitFetchSeam carries fetchContext); de-duplicating would mean lifting fetched state
                into this root and changing how the frozen units are driven — out of scope. */}
            <MemoView memoFetchSeam={seams.memo} applicationId={selectedId} />
            {/* Fold 3 — testid passed EXPLICITLY (equals the default) so the assertion pins the REAL
                rendered id and cannot pass by accident against a stale `approval-gate-view`. */}
            <ApprovalGateView commitFetchSeam={seams.commit} applicationId={selectedId} testid="approval-gate" />
          </>
        ) : null}
        <HistoryView fetchSeam={seams.history} />
      </div>
    </AppFrame>
  );
}

export default App;
