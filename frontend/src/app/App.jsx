import { useState, useEffect } from 'react';
import { AppFrame } from '../shell/components/AppFrame.jsx';
import { HistoryView } from '../history/HistoryView.jsx';
import { loadCurrentRole } from './sessionClient.js';

// The frontend composition root — the client half of the out-of-band integration pass.
// AUTHOR-ONLY (Decision 5): written and Vitest-tested, but NOT browser-runnable — there is no
// bundler/dev-server, and `deploy-config` (U23, P2) owns that topology. It was deliberately NOT
// pulled forward. So this module has no `main.jsx`/`index.html` and mounts nothing itself.
//
// ROLE DELIVERY — via the shell's OWN seam, not around it:
// `AppFrame` already hosts the RoleProvider internally (`value={user ? user.role : null}`), and
// its docstring says it is "populated later by WIRE-1". This module IS that population: R1's role
// is handed to AppFrame's `user` prop, and the frozen AppFrame provides the context. Wrapping
// AppFrame in a SECOND RoleProvider would be shadowed by its inner one (nearest provider wins) —
// the shell's seam is used as designed rather than worked around.
//
// WHAT IT MOUNTS, AND WHY ONLY THIS:
// Scope A backs R1 (session) and R6/R7 (decision history). `ui-history` is therefore the ONLY UI
// unit with a live backend, and it is the only surface mounted. The other four frozen UI units
// (`ui-queue`, `ui-memo-view`, `ui-approval-gate`, `ui-override-form`) have their seams wired to
// the real transport in `seams.js` — ready the day R2-R5 land — but are not rendered: a surface
// that could only ever show an error would imply backing that does not exist.
//
// NO ROUTER (Decision 6, N/A under Scope A): cross-unit navigation is the "later shell/router
// integration" every UI unit named and none owns. With exactly one mountable surface there is
// nothing to navigate between, so no router is introduced and no unit's no-router guard is
// broken. `ui-queue`'s upward `onSelect` has no destination in this slice — which is precisely
// why it is not mounted.
//
// Role is chrome only (the server is the real gate). `null` = unauthenticated, which every frozen
// UI unit already renders identically for.
export function App({ seams, transport, testid = 'app-root' }) {
  const [role, setRole] = useState(null);

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
        <HistoryView fetchSeam={seams.history} />
      </div>
    </AppFrame>
  );
}

export default App;
