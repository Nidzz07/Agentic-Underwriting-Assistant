import { useCurrentRole } from '../session/roleContext.js';

// C2 — RoleGate: COSMETIC show/hide of an affordance (defense-in-depth only). Owns NO
// authorization decision (BR-UI-4 / SEC-4). The REAL boundary is auth-rbac (backend authz) plus
// audit-store's DecisionCommitService re-check: the server rejects an unauthorized action even if
// this cosmetic guard were bypassed. Imports NO backend module; calls no authz function; issues no
// fetch. Reads the current Role INTERNALLY via useCurrentRole() — there is NO `role` prop.
//
// Cosmetic capability mirror: the frozen auth_rbac role semantics consumed as VALUE SHAPES (never
// imported) — underwriter acts + reads; auditor reads only (the read-only distinction is surfaced
// cosmetically here); admin is not an underwriting actor. Cells beyond the underwriter-acts /
// auditor-read-only distinction are cosmetic only; enforcement is entirely server-side.
const COSMETIC_CAPABILITIES = Object.freeze({
  underwriter: Object.freeze({ act: true, read: true }),
  auditor: Object.freeze({ act: false, read: true }),
  admin: Object.freeze({ act: false, read: false }),
});

// can in {"act","read"}. Renders children when the current cosmetic role permits `can`; else fallback.
export function RoleGate({ can, children, fallback = null }) {
  const role = useCurrentRole();
  const caps = role ? COSMETIC_CAPABILITIES[role] : null;
  const allowed = Boolean(caps && caps[can]);
  return allowed ? <>{children}</> : <>{fallback}</>;
}

export default RoleGate;
