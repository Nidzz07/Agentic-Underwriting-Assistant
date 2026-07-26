import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { LoginView } from '../LoginView.jsx';

function seam(submitLogin) {
  return { submitLogin, submitLogout: vi.fn() };
}

function fillAndSubmit({ id = 'UW-1', password = 's3cret' } = {}) {
  fireEvent.change(screen.getByTestId('login-input-user-id'), { target: { value: id } });
  fireEvent.change(screen.getByTestId('login-input-password'), { target: { value: password } });
  fireEvent.click(screen.getByTestId('login-action-submit'));
}

describe('LoginView submission', () => {
  it('sends exactly { user_id, password } — the two fields the contract pins, no more', async () => {
    const submitLogin = vi.fn(async () => undefined);
    render(<LoginView loginSeam={seam(submitLogin)} onAuthenticated={vi.fn()} />);

    fillAndSubmit({ id: 'UW-1', password: 's3cret' });

    await waitFor(() => expect(submitLogin).toHaveBeenCalledTimes(1));
    expect(submitLogin).toHaveBeenCalledWith({ user_id: 'UW-1', password: 's3cret' });
    expect(Object.keys(submitLogin.mock.calls[0][0]).sort()).toEqual(['password', 'user_id']);
  });

  it('a 204 resolves with NO body and hands control to onAuthenticated', async () => {
    // ⚑ R8 answers 204 no-content, so the view must not expect or parse a payload. Who the user
    // now IS comes from re-running the session check (Q3a) — never from the login response.
    const onAuthenticated = vi.fn();
    render(<LoginView loginSeam={seam(vi.fn(async () => undefined))} onAuthenticated={onAuthenticated} />);

    fillAndSubmit();

    await waitFor(() => expect(onAuthenticated).toHaveBeenCalledTimes(1));
    expect(onAuthenticated).toHaveBeenCalledWith();
  });

  it('does not submit when either field is empty — and never calls the seam', async () => {
    const submitLogin = vi.fn();
    render(<LoginView loginSeam={seam(submitLogin)} onAuthenticated={vi.fn()} />);

    fireEvent.click(screen.getByTestId('login-action-submit'));
    fireEvent.change(screen.getByTestId('login-input-user-id'), { target: { value: 'UW-1' } });
    fireEvent.click(screen.getByTestId('login-action-submit'));

    expect(submitLogin).not.toHaveBeenCalled();
  });

  it('a failed attempt leaves the form usable and does not clear the user id', async () => {
    // ⚑ Retyping the id after every typo is the fastest way to make a login form hated. The
    // PASSWORD is cleared (below); the identifier is not a secret and is kept.
    const submitLogin = vi.fn(async () => {
      throw { error: { code: 'unauthenticated', message: 'Authentication failed.', detail: {} } };
    });
    render(<LoginView loginSeam={seam(submitLogin)} onAuthenticated={vi.fn()} />);

    fillAndSubmit({ id: 'UW-1', password: 'wrong' });

    await waitFor(() => expect(screen.getByTestId('login-state-error')).toBeInTheDocument());
    expect(screen.getByTestId('login-input-user-id')).toHaveValue('UW-1');
    expect(screen.getByTestId('login-input-password')).toHaveValue('');

    // ⚑ The submit control is DISABLED here, and correctly so: the password was just cleared,
    // and the empty-field guard (asserted above) forbids submitting without one. "Usable" means
    // the user can type a new password and go again WITHOUT retyping their id -- which is what
    // this asserts, rather than that an empty form is submittable.
    expect(screen.getByTestId('login-action-submit')).toBeDisabled();
    fireEvent.change(screen.getByTestId('login-input-password'), { target: { value: 'second-try' } });
    expect(screen.getByTestId('login-action-submit')).toBeEnabled();

    fireEvent.click(screen.getByTestId('login-action-submit'));
    await waitFor(() => expect(submitLogin).toHaveBeenCalledTimes(2));
    expect(submitLogin).toHaveBeenLastCalledWith({ user_id: 'UW-1', password: 'second-try' });
  });
});
