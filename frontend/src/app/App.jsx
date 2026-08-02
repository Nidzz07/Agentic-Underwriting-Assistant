import { useState, useEffect, useCallback } from 'react';
import { AppFrame } from '../shell/components/AppFrame.jsx';
import { HistoryView } from '../history/HistoryView.jsx';
import { QueueView } from '../queue/QueueView.jsx';
import { MemoView } from '../memoView/MemoView.jsx';
import { ApprovalGateView } from '../approvalGate/ApprovalGateView.jsx';
import { OverrideFormView } from '../overrideForm/OverrideFormView.jsx';
import { SubmissionView } from '../submission/SubmissionView.jsx';
import { LoginView } from '../login/LoginView.jsx';
import { LogoutControl } from '../login/LogoutControl.jsx';
import { createLoginFetch } from '../login/loginFetchSeam.js';
import { loadCurrentRole } from './sessionClient.js';

// The frontend composition root — the client half of the out-of-band integration pass.
//
// ROLE DELIVERY — via the shell's OWN seam, not around it:
// `AppFrame` already hosts the RoleProvider internally (`value={user ? user.role : null}`), and
// its docstring says it is "populated later by WIRE-1". This module IS that population: R1's role
// is handed to AppFrame's `user` prop, and the frozen AppFrame provides the context.
//
// ⚑ THE AUTHENTICATION GATE (register #25's frontend half, Q1a).
// Before this existed, an unauthenticated visitor got the full app chrome with two error panels
// reading "Authentication is required." and Retry buttons that failed forever — a polite,
// permanent dead end with no way to authenticate. The gate replaces that with a login page.
//
// THREE states, and the third one is load-bearing:
//   'checking'        -> render NEITHER branch. FE-Fold-4: a two-state gate would flash the login
//                        page on EVERY page load, including for already-authenticated users,
//                        because /session is in flight on mount.
//   'unauthenticated' -> the login view INSTEAD of the app.
//   'authenticated'   -> exactly what this root mounted before, unchanged.
//
// ⚑ ONE definition of "who is the current user" (Q3a): `refreshSession` is used at boot, after a
// successful login, and after logout. R8 answers 204 with NO body, so login proves only "that
// worked" — the identity always comes from re-reading R1, never from the login response.
//
// ⚑ DISCLOSED LIMITATION (a consequence of Q3a, recorded not hidden): `loadCurrentRole`
// fail-closes to null on ANY failure, so a backend that is DOWN is indistinguishable from a 401.
// An outage therefore presents as the login page. Distinguishing them would mean calling
// `createSessionClient` directly, which is a different answer to Q3 and is deliberately not taken.
//
// SELECTION STATE (no router — Decision 6 upheld): this root holds "which application is open".
// Role is chrome only; the server is the real gate.
export function App({ seams, transport, testid = 'app-root' }) {
  const [status, setStatus] = useState('checking');
  const [role, setRole] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [queueEpoch, setQueueEpoch] = useState(0);

  const loginSeam = createLoginFetch(transport);

  const refreshSession = useCallback(async () => {
    const resolved = await loadCurrentRole(transport);
    setRole(resolved);
    setStatus(resolved ? 'authenticated' : 'unauthenticated');
    return resolved;
  }, [transport]);

  useEffect(() => {
    let cancelled = false;
    loadCurrentRole(transport).then((resolved) => {
      if (cancelled) return;
      setRole(resolved);
      setStatus(resolved ? 'authenticated' : 'unauthenticated');
    });
    return () => { cancelled = true; };
  }, [transport]);

  if (status === 'checking') {
    // Neither branch. Committing to one before /session answers is exactly the flash FE-Fold-4
    // forbids. Follows the units' own loading convention (aria-busy container, no content).
    return <div data-testid="app-checking" aria-busy="true" />;
  }

  if (status === 'unauthenticated') {
    return (
      <AppFrame user={null}>
        <LoginView loginSeam={loginSeam} onAuthenticated={refreshSession} />
      </AppFrame>
    );
  }

  return (
    <AppFrame user={role ? { role } : null}>
      <div data-testid={testid}>
        {/* ⚑ NOT RoleGate-wrapped: RoleGate gives admin { act: false, read: false }, so gating
            logout would strand an admin in a session they cannot end. */}
        <LogoutControl
          loginSeam={loginSeam}
          onLoggedOut={() => { setSelectedId(null); refreshSession(); }}
        />
        {/* ⚑ MOUNTED ABOVE THE QUEUE, and behind the login gate like every other surface.
            Submission is how a case ENTERS the queue, so it reads top-down: submit, then see
            it listed. ⚠️ `queueEpoch` is bumped on a successful submission and passed as a
            React key, which REMOUNTS QueueView so it re-reads R2 — without it a user would
            submit and see nothing appear until a manual reload, because the frozen QueueView
            fetches on mount and owns its own state (no refresh prop exists to call). */}
        <SubmissionView
          submissionSeam={seams.submission}
          onSubmitted={() => setQueueEpoch((epoch) => epoch + 1)}
        />
        <QueueView key={queueEpoch} fetchSeam={seams.queue} onSelect={setSelectedId} />
        {selectedId ? (
          <>
            {/* Fold 4 — DISCLOSED, not optimized (#15 precedent): MemoView, ApprovalGateView AND
                OverrideFormView each issue their OWN GET /applications/{id}/memo, so a selection now
                makes THREE identical R4 requests (was two before override was mounted). Each frozen
                unit owning its own fetch is the design; removing the duplication would mean lifting
                R4 into this root and prop-injecting three frozen units — a redesign, not a wiring
                change. Accepted knowingly and left visible rather than quietly absorbed. */}
            <MemoView memoFetchSeam={seams.memo} applicationId={selectedId} />
            {/* Fold 3 — testid passed EXPLICITLY (equals the default) so the assertion pins the REAL
                rendered id and cannot pass by accident against a stale `approval-gate-view`. */}
            <ApprovalGateView commitFetchSeam={seams.commit} applicationId={selectedId} testid="approval-gate" />
            {/* The SECOND write path — the human's "I disagree", carrying the mandatory reason.
                ⚑ Mounted ALONGSIDE the approve gate, not instead of it: agreeing and disagreeing are
                peer choices, and showing only one would misrepresent the gate as a rubber stamp.
                ⚑ Both target the SAME recommendation, so whichever is confirmed first wins the
                register-#19 claim and the other receives 409 `commit_conflict` — accepted knowingly.
                It needs no special-casing here: OverrideFormView already renders that conflict
                through its own error state (CommitStateView's `commit_conflict` branch).
                ⚑ NOT RoleGate-wrapped here — the gate lives INSIDE OverrideAffordance, so a
                non-underwriter sees the context without the affordance. */}
            <OverrideFormView overrideFetchSeam={seams.override} applicationId={selectedId} />
          </>
        ) : null}
        <HistoryView fetchSeam={seams.history} />
      </div>
    </AppFrame>
  );
}

export default App;
