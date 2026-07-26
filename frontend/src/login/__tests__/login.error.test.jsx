import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { LoginView } from '../LoginView.jsx';

// ERROR-1 (ErrorEnvelopeToRenderPattern), and the one property this unit must protect above all
// others: the frontend MUST NOT reconstruct a distinction the backend deliberately withholds.

function renderWithFailure(envelope) {
  const submitLogin = vi.fn(async () => { throw envelope; });
  render(<LoginView loginSeam={{ submitLogin, submitLogout: vi.fn() }} onAuthenticated={vi.fn()} />);
  return submitLogin;
}

function submit({ password = 'whatever' } = {}) {
  fireEvent.change(screen.getByTestId('login-input-user-id'), { target: { value: 'UW-1' } });
  fireEvent.change(screen.getByTestId('login-input-password'), { target: { value: password } });
  fireEvent.click(screen.getByTestId('login-action-submit'));
}

const UNIFORM_401 = {
  error: { code: 'unauthenticated', message: 'Authentication failed.', detail: {} },
};

describe('LoginView error rendering (ERROR-1)', () => {
  it("renders the server's message VERBATIM, exposes the code hidden, and never renders detail", async () => {
    renderWithFailure({
      error: { code: 'unauthenticated', message: 'Authentication failed.', detail: { attempts: 3 } },
    });
    submit();

    await waitFor(() => expect(screen.getByTestId('login-state-error')).toBeInTheDocument());
    expect(screen.getByTestId('login-error-message')).toHaveTextContent('Authentication failed.');

    const code = screen.getByTestId('login-error-code');
    expect(code).toHaveTextContent('unauthenticated');
    expect(code).not.toBeVisible();

    // detail is NEVER rendered — not visibly, not hidden, not anywhere.
    expect(screen.getByTestId('login-state-error').textContent).not.toContain('attempts');
    expect(screen.getByTestId('login-state-error').textContent).not.toContain('3');
  });

  it('falls back to a generic message when the envelope is malformed — never a raw throw', async () => {
    renderWithFailure({ nonsense: true });
    submit();

    await waitFor(() => expect(screen.getByTestId('login-state-error')).toBeInTheDocument());
    expect(screen.getByTestId('login-error-message').textContent).toBeTruthy();
    expect(screen.getByTestId('login-error-code')).toHaveTextContent('unknown_error');
  });

  it('⚑ CANNOT distinguish a wrong password from a lockout — five failures render IDENTICALLY', async () => {
    // THE LOAD-BEARING TEST OF THIS UNIT. The backend returns the SAME 401 with the SAME message
    // for a wrong password, an unknown user, a missing credential row AND a locked-out account,
    // because telling them apart is a user-enumeration oracle. A frontend that counted attempts
    // and warned "you may be locked out" would REBUILD that oracle client-side and undo the
    // backend's deliberate choice.
    //
    // So: drive the exact sequence that trips the backend's 5-attempt lockout and assert the
    // rendered output is byte-identical every time, and that nothing accumulates.
    renderWithFailure(UNIFORM_401);

    const renderings = [];
    for (let attempt = 1; attempt <= 5; attempt += 1) {
      submit({ password: `wrong-${attempt}` });
      // eslint-disable-next-line no-await-in-loop
      await waitFor(() => expect(screen.getByTestId('login-state-error')).toBeInTheDocument());
      renderings.push(screen.getByTestId('login-state-error').textContent);
    }

    expect(new Set(renderings).size).toBe(1);
    expect(renderings[4]).toBe(renderings[0]);
    // No attempt counter, no countdown, no lockout hint has appeared anywhere in the view.
    const view = screen.getByTestId('login-view').textContent.toLowerCase();
    for (const leak of ['lock', 'attempt', 'remaining', 'try again in', '5', '4', '3']) {
      expect(view).not.toContain(leak);
    }
  });
});
