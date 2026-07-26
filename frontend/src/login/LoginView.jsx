import { useState } from 'react';
import { Panel } from '../shell/components/Panel.jsx';
import { LOGIN_COPY } from './copy.js';
import { LoginStateView } from './components/LoginStateView.jsx';

// C1 — the login form. The ONLY stateful component in this unit.
//
// State machine (mirroring the sibling views' FETCH-1 shape, adapted for a write):
//   idle -> submitting -> (success: handed to onAuthenticated | error: idle + error shown)
//   error --submit--> submitting
//
// ⚑ WHAT THIS COMPONENT DELIBERATELY DOES NOT DO:
//   * It does not decide who the user is. R8 answers 204 with NO body, so a successful submit
//     proves only "that worked" — the identity comes from re-running the session check, which
//     is the caller's job via onAuthenticated (Q3a). There is exactly ONE definition of "who is
//     the current user" in the app, and it is not here.
//   * It does not classify failures. A wrong password and a locked-out account return the SAME
//     401 with the SAME message; this view renders the server's message verbatim (ERROR-1) and
//     counts nothing. Reconstructing that distinction client-side would re-open the
//     user-enumeration oracle the backend closed on purpose.
//   * It does not persist, log, or echo the password. It lives in component state for exactly
//     as long as the submit takes, and is cleared on failure.
//
// Role-invariant by construction: it renders before any role is known, so it consults no role
// and imports no RoleGate.
export function LoginView({ loginSeam, onAuthenticated, testid = 'login-view' }) {
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const canSubmit = userId.trim() !== '' && password !== '' && !submitting;

  async function onSubmit(event) {
    event.preventDefault();
    if (!canSubmit) return;

    setSubmitting(true);
    setError(null);
    try {
      await loginSeam.submitLogin({ user_id: userId, password });
      // ⚑ Clear the secret before handing off, so it does not outlive the request.
      setPassword('');
      onAuthenticated();
    } catch (envelope) {
      setError(envelope);
      // The identifier is NOT a secret and is kept — retyping it after every typo is the
      // fastest way to make a login form hated. The password is cleared.
      setPassword('');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Panel testid={testid} title={LOGIN_COPY.title}>
      <form onSubmit={onSubmit} data-testid="login-form">
        <label htmlFor="login-user-id">{LOGIN_COPY.userIdLabel}</label>
        <input
          id="login-user-id"
          data-testid="login-input-user-id"
          type="text"
          autoComplete="username"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />

        <label htmlFor="login-password">{LOGIN_COPY.passwordLabel}</label>
        <input
          id="login-password"
          data-testid="login-input-password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit" data-testid="login-action-submit" disabled={!canSubmit}>
          {submitting ? LOGIN_COPY.submittingLabel : LOGIN_COPY.submitLabel}
        </button>
      </form>

      {error ? <LoginStateView error={error} /> : null}
    </Panel>
  );
}

export default LoginView;
