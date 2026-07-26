import { useState } from 'react';
import { LOGIN_COPY } from './copy.js';

// C4 — the logout affordance. Mounted by the composition root (App.jsx), NOT by AppFrame:
// AppFrame is a FROZEN ui-shell component, and a cosmetic placement preference is not a reason
// to reopen a frozen unit (Q4c).
//
// ⚑ DELIBERATELY NOT WRAPPED IN RoleGate. RoleGate's cosmetic capability table gives admin
// { act: false, read: false }, so gating this control would render NOTHING for an admin and
// strand them in a session they cannot end. Logging out is a capability every authenticated
// role has, not a privilege some roles hold — it is the one control that must never be gated.
//
// Reads no role and imports no RoleGate, so it is role-invariant by construction.
export function LogoutControl({ loginSeam, onLoggedOut, testid = 'login-action-logout' }) {
  const [pending, setPending] = useState(false);

  async function onClick() {
    if (pending) return;
    setPending(true);
    try {
      await loginSeam.submitLogout();
    } catch {
      // ⚑ A failed logout still returns the user to the login view. The session may or may not
      // have been revoked server-side, and the honest response to that uncertainty is to stop
      // showing an authenticated app — never to leave them in one because a request failed.
    } finally {
      setPending(false);
      onLoggedOut();
    }
  }

  return (
    <button type="button" data-testid={testid} onClick={onClick} disabled={pending}>
      {LOGIN_COPY.logoutLabel}
    </button>
  );
}

export default LogoutControl;
