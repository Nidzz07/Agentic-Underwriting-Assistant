// R1 client — the composition root's Role delivery (WIRE-1 §6).
//
// ui-shell's `RoleContext` was built with the wire retrieval deliberately left out: "HOW the real
// session/auth response delivers the current user's Role into this context is owned by WIRE-1 —
// NOT designed here. Until then a test/stub provider feeds it." This module is that retrieval, and
// it feeds the frozen `RoleProvider` without touching it.
//
// The role is consumed BY VALUE ('underwriter' | 'auditor' | 'admin'), exactly as R1 emits it and
// as RoleContext documents — never re-cased, never re-mapped.
//
// Role remains chrome/labelling only, never an authorization datum: the real gate is server-side
// (auth-rbac re-checks on every protected route). A client that lied about its role would change
// nothing — the server reads the role from `app_user`, not from the request.

// Own-local, mirroring — not imported from — the seam convention: this is a one-shot read, not a
// unit seam, so it builds its own request rather than borrowing a unit's builder.
export function buildSessionRequest() {
  return { method: 'GET', path: '/session' };
}

/**
 * createSessionClient(transport) -> fetchSession()
 *
 * Resolves `{ user_id, role }` (WIRE-1 §6). REJECTS with the transport's failure or the server's
 * §4 envelope — a 401 means "not authenticated", which the shell renders as a null role.
 */
export function createSessionClient(transport) {
  return async function fetchSession() {
    const response = await transport(buildSessionRequest());
    if (response && response.ok) {
      return response.body;
    }
    throw response ? response.body : undefined;
  };
}

/**
 * loadCurrentRole(transport) -> 'underwriter' | 'auditor' | 'admin' | null
 *
 * The value shape RoleContext documents. Fail-closes to `null` on ANY failure (401, network,
 * malformed body) — the same fail-closed posture as the server's `to_role`. A null role is the
 * shell's "unauthenticated" state, never an error to render.
 */
export async function loadCurrentRole(transport) {
  try {
    const session = await createSessionClient(transport)();
    const role = session && session.role;
    return typeof role === 'string' && role ? role : null;
  } catch {
    return null;
  }
}
