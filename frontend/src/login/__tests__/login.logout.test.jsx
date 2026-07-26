import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { LogoutControl } from '../LogoutControl.jsx';
import { RoleProvider } from '../../shell/session/roleContext.js';

function seam(submitLogout) {
  return { submitLogin: vi.fn(), submitLogout };
}

describe('LogoutControl', () => {
  it('posts R9 and hands control back on success', async () => {
    const submitLogout = vi.fn(async () => undefined);
    const onLoggedOut = vi.fn();
    render(<LogoutControl loginSeam={seam(submitLogout)} onLoggedOut={onLoggedOut} />);

    fireEvent.click(screen.getByTestId('login-action-logout'));

    await waitFor(() => expect(submitLogout).toHaveBeenCalledTimes(1));
    expect(submitLogout).toHaveBeenCalledWith();
    await waitFor(() => expect(onLoggedOut).toHaveBeenCalledTimes(1));
  });

  it('⚑ renders for EVERY role — it is not RoleGate-gated', () => {
    // RoleGate's admin row is { act: false, read: false }, so wrapping logout in a RoleGate
    // would render nothing for an admin and STRAND THEM in a session they cannot end. Every
    // authenticated role must be able to log out; this is a capability, not a privilege.
    for (const role of ['underwriter', 'auditor', 'admin']) {
      const { unmount } = render(
        <RoleProvider value={role}>
          <LogoutControl loginSeam={seam(vi.fn())} onLoggedOut={vi.fn()} />
        </RoleProvider>,
      );
      expect(screen.getByTestId('login-action-logout')).toBeInTheDocument();
      unmount();
    }
  });
});
