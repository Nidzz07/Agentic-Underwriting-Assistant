// C3 (shell/session) — the abstracted Role seam RoleGate reads. RoleGate reads the current Role
// internally via useCurrentRole(); it does NOT define wire retrieval. HOW the real session/auth
// response delivers the current user's Role into this context is owned by WIRE-1 (the FastAPI
// composition-root api-contract), NOT designed here. Until then a test/stub provider feeds it.
//
// currentRole is a VALUE SHAPE: 'underwriter' | 'auditor' | 'admin' | null. No auth_rbac Python is
// imported (first cross-language reference-not-own boundary — Python enum -> React via API JSON).
//
// JSX-free (.js) on purpose: uses createElement so no JSX transform is needed for this module.
import { createContext, createElement, useContext } from 'react';

export const RoleContext = createContext(null);

export function RoleProvider({ value = null, children }) {
  return createElement(RoleContext.Provider, { value }, children);
}

export function useCurrentRole() {
  return useContext(RoleContext);
}
