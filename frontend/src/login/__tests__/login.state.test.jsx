import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginView } from '../LoginView.jsx';
import { LOGIN_COPY } from '../copy.js';

// The form's own state machine: idle -> submitting -> (caller-handled success | error),
// error --submit--> submitting. Mirrors the sibling views' state-test shape.

function seam({ submitLogin } = {}) {
  return { submitLogin: submitLogin ?? vi.fn(async () => undefined), submitLogout: vi.fn() };
}

function fillAndSubmit({ id = 'UW-1', password = 's3cret' } = {}) {
  fireEvent.change(screen.getByTestId('login-input-user-id'), { target: { value: id } });
  fireEvent.change(screen.getByTestId('login-input-password'), { target: { value: password } });
  fireEvent.click(screen.getByTestId('login-action-submit'));
}

describe('LoginView state', () => {
  it('starts idle — the form is present, with no error and nothing busy', () => {
    render(<LoginView loginSeam={seam()} onAuthenticated={vi.fn()} />);
    expect(screen.getByTestId('login-view')).toBeInTheDocument();
    expect(screen.getByTestId('login-input-user-id')).toBeInTheDocument();
    expect(screen.getByTestId('login-input-password')).toBeInTheDocument();
    expect(screen.queryByTestId('login-state-error')).toBeNull();
  });

  it('the password field is a password input — never a plain text field', () => {
    // ⚑ Not cosmetic: a text input renders the secret in the clear and offers it to autofill,
    // screen sharing and shoulder-surfing alike.
    render(<LoginView loginSeam={seam()} onAuthenticated={vi.fn()} />);
    expect(screen.getByTestId('login-input-password')).toHaveAttribute('type', 'password');
  });

  it('submitting disables the submit control so a double-click cannot double-post', async () => {
    let release;
    const submitLogin = vi.fn(() => new Promise((resolve) => { release = resolve; }));
    render(<LoginView loginSeam={seam({ submitLogin })} onAuthenticated={vi.fn()} />);

    fillAndSubmit();
    await waitFor(() => expect(screen.getByTestId('login-action-submit')).toBeDisabled());

    release();
  });
});

describe('LoginView copy', () => {
  it('carries no forbidden system-output vocabulary (ADVISORY-1)', () => {
    // ⚑ The shell's ONE forbidden list, reused unmodified: a login failure must never be phrased
    // as "declined"/"approved" — that vocabulary is reserved for underwriting outcomes.
    const forbidden = ['DECLINE', 'decision', 'approved', 'declined'];
    for (const value of Object.values(LOGIN_COPY)) {
      if (typeof value !== 'string') continue;
      for (const term of forbidden) {
        expect(value.toLowerCase()).not.toContain(term.toLowerCase());
      }
    }
  });
});
