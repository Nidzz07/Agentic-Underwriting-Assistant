import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoginView } from '../LoginView.jsx';

// TESTID-1 — every login testid follows `login-<element>-<purpose>` (or the bare unit root
// `login-view`), the same convention the frozen sibling units hold.
export function isValidLoginTestid(id) {
  return id === 'login-view' || /^login-[a-z]+(-[a-z]+)*$/.test(id);
}

describe('TESTID-1 — the login unit testid convention', () => {
  it('every rendered login testid follows the convention (non-vacuous)', () => {
    render(<LoginView loginSeam={{ submitLogin: vi.fn(), submitLogout: vi.fn() }} onAuthenticated={vi.fn()} />);
    const ids = Array.from(document.querySelectorAll('[data-testid]'))
      .map((n) => n.getAttribute('data-testid'))
      .filter((id) => id.startsWith('login-'));

    expect(ids.length).toBeGreaterThan(0);
    expect(ids.filter((id) => !isValidLoginTestid(id))).toEqual([]);
    expect(screen.getByTestId('login-view')).toBeInTheDocument();

    // detector self-test — a misnamed testid is rejected
    expect(isValidLoginTestid('login-Input-UserId')).toBe(false);
    expect(isValidLoginTestid('loginInput')).toBe(false);
    expect(isValidLoginTestid('login-input-user-id')).toBe(true);
  });
});
