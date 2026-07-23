import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { render, screen } from '@testing-library/react';
import RoleGate from '../components/RoleGate.jsx';
import { RoleContext } from '../session/roleContext.js';

// RBAC-1 (NFR-UI-RBAC-1) — RoleGate is cosmetic: it renders/hides purely on the injected
// RoleContext value (via useCurrentRole()) and calls NO authorization function. Tests inject via a
// stub RoleContext.Provider (no `role` prop anywhere).

function renderWithRole(role, ui) {
  return render(<RoleContext.Provider value={role}>{ui}</RoleContext.Provider>);
}

describe('NFR-UI-RBAC-1 — cosmetic RoleGate', () => {
  it('underwriter -> an act affordance renders', () => {
    renderWithRole(
      'underwriter',
      <RoleGate can="act" fallback={<span data-testid="shell-rolegate-fallback">hidden</span>}>
        <button data-testid="shell-rolegate-act">Act</button>
      </RoleGate>,
    );
    expect(screen.getByTestId('shell-rolegate-act')).toBeInTheDocument();
    expect(screen.queryByTestId('shell-rolegate-fallback')).not.toBeInTheDocument();
  });

  it('auditor -> the act affordance is hidden (fallback shown)', () => {
    renderWithRole(
      'auditor',
      <RoleGate can="act" fallback={<span data-testid="shell-rolegate-fallback">hidden</span>}>
        <button data-testid="shell-rolegate-act">Act</button>
      </RoleGate>,
    );
    expect(screen.queryByTestId('shell-rolegate-act')).not.toBeInTheDocument();
    expect(screen.getByTestId('shell-rolegate-fallback')).toBeInTheDocument();
  });

  it('auditor -> a read affordance renders (the read-only distinction is surfaced)', () => {
    renderWithRole(
      'auditor',
      <RoleGate can="read">
        <span data-testid="shell-rolegate-read">read</span>
      </RoleGate>,
    );
    expect(screen.getByTestId('shell-rolegate-read')).toBeInTheDocument();
  });

  it('no role (null context) -> nothing renders, default fallback is null', () => {
    renderWithRole(
      null,
      <RoleGate can="act">
        <span data-testid="shell-rolegate-act">act</span>
      </RoleGate>,
    );
    expect(screen.queryByTestId('shell-rolegate-act')).not.toBeInTheDocument();
  });

  it('admin -> not an underwriting actor: act hidden', () => {
    renderWithRole(
      'admin',
      <RoleGate can="act">
        <span data-testid="shell-rolegate-act">act</span>
      </RoleGate>,
    );
    expect(screen.queryByTestId('shell-rolegate-act')).not.toBeInTheDocument();
  });

  it('static — RoleGate imports no backend/authz module and calls no authorize()', () => {
    const src = readFileSync(
      path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../components/RoleGate.jsx'),
      'utf8',
    );
    // No authz function call.
    expect(/\bauthorize\s*\(/.test(src)).toBe(false);
    // No import from a backend path / Python module name.
    const importLines = src.split('\n').filter((l) => /^\s*import\b/.test(l));
    for (const line of importLines) {
      expect(/backend|auth_rbac|rules_engine|audit_store|memo_agent_core/.test(line)).toBe(false);
    }
  });
});
