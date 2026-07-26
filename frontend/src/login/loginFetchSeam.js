// C2 (login/loginFetchSeam) — the own-local seam for R8/R9 (WIRE1-Fold-5). MIRRORS the
// ui-queue / ui-memo-view / ui-approval-gate fetchSeam pattern but is NOT imported from any of
// them (all frozen, kept decoupled). Owns request-building + failure NORMALIZATION only; it makes
// no real network call itself — the real transport is injected at the composition root, or a
// capturing double in tests.
//
// Cross-unit consistency here comes from the WIRE-1 contract, NEVER from importing a sibling.

// R8. WIRE-1 §5 pins the login body as exactly { user_id, password } — no more. The password is
// carried here and nowhere else: it is never stored, never logged, and never placed in a URL.
export function buildLoginRequest({ user_id, password }) {
  return { method: 'POST', path: '/login', body: { user_id, password } };
}

// R9. NO body — the session is identified by the cookie alone, which the browser attaches
// automatically (same-origin; confirmed in a real browser at this pass's Step 0).
export function buildLogoutRequest() {
  return { method: 'POST', path: '/logout' };
}

// Normalize ANY failure to a well-formed WIRE-1 §4 envelope { error: { code, message, detail } },
// the SAME shape every sibling seam produces, so the view (ERROR-1) never unpacks a raw exception.
// A parsed non-2xx body that is already well-formed passes through untouched; a transport error or
// a missing/malformed body becomes a synthesized network_error envelope.
//
// ⚑ NOTE WHAT THIS DELIBERATELY DOES NOT DO: it does not inspect, classify, or re-map the server's
// code or message. A 401 for a wrong password and a 401 for a locked-out account are IDENTICAL on
// the wire — by design, because distinguishing them is a user-enumeration oracle — and this seam
// preserves that indistinguishability rather than trying to recover it.
export function normalizeError(cause) {
  if (
    cause && typeof cause === 'object' &&
    cause.error && typeof cause.error === 'object' &&
    typeof cause.error.code === 'string' && typeof cause.error.message === 'string'
  ) {
    const { code, message, detail } = cause.error;
    return { error: { code, message, detail: detail ?? {} } };
  }
  return { error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} } };
}

/**
 * createLoginFetch(transport) -> { submitLogin, submitLogout }
 *
 * ⚑ NOT registered in seams.js (Q13a) — the login client follows sessionClient.js's non-seam
 * precedent: a one-shot handshake, not a per-unit data seam. app.test.jsx's five-key seam
 * assertion therefore stays green, untouched.
 *
 * R8 answers 204 with NO body, so success resolves to undefined rather than a parsed payload.
 */
export function createLoginFetch(transport) {
  async function run(request) {
    let response;
    try {
      response = await transport(request);
    } catch (cause) {
      throw normalizeError(cause);
    }
    if (!response || !response.ok) {
      throw normalizeError(response ? response.body : undefined);
    }
    return undefined;
  }

  return {
    submitLogin: (credentials) => run(buildLoginRequest(credentials)),
    submitLogout: () => run(buildLogoutRequest()),
  };
}
