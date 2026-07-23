// The REAL transport — the composition root's client half. Authored in the out-of-band
// integration pass (see guide-docs/build/plans/composition-root-integration-plan.md).
//
// This is the ONE thing every frozen UI unit's seam was designed to receive. Each unit built a
// `create<X>Fetch(transport)` seam and injected a capturing DOUBLE in its tests; production was
// always deferred to "the composition root". This module is that production transport — and it
// satisfies the duck-typed contract all five seams already expect, unchanged:
//
//     transport(request) -> Promise<{ ok: boolean, body: any }>
//     request === { method, path }          (+ `body` for a write, which Scope A never issues)
//
// It THROWS on a transport-level failure (network down, non-JSON body), which is exactly what
// every seam's `normalizeError` is built to catch — so a frozen seam turns it into the WIRE-1 §4
// envelope without this module knowing anything about that shape. No seam is modified.
//
// AUTH (Decision 2 / Q4-A): the stub `X-User-Id` header, the client mirror of the server's
// deferred handshake seam (WIRE-1 §6/A6). Replacing it with real OIDC touches only this module.
//
// SCOPE A: only R1/R6/R7 are backed. R2-R5 answer 501 `not_implemented` in the §4 envelope, so a
// seam pointed at them rejects with a well-formed envelope and its unit renders its ordinary error
// state — a truthful "not wired here", not a crash.

export const DEFAULT_BASE_URL = '';
export const USER_ID_HEADER = 'X-User-Id';

/**
 * createHttpTransport({ baseUrl, userId, fetchImpl }) -> transport(request)
 *
 * `fetchImpl` is injected (defaults to global fetch) so this module is testable with no server
 * and no network — the same injection discipline every seam uses for its transport.
 */
export function createHttpTransport({ baseUrl = DEFAULT_BASE_URL, userId, fetchImpl } = {}) {
  const doFetch = fetchImpl ?? globalThis.fetch;

  return async function transport(request) {
    const { method, path, body } = request;
    const response = await doFetch(`${baseUrl}${path}`, {
      method,
      headers: {
        Accept: 'application/json',
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
        ...(userId ? { [USER_ID_HEADER]: userId } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });

    // A non-JSON body is a transport failure, not a contract error: throwing lets the seam's
    // normalizeError synthesize the network_error envelope rather than inventing one here.
    let parsed;
    try {
      parsed = await response.json();
    } catch (cause) {
      throw cause;
    }

    // `ok` is the seam's contract, NOT fetch's: a non-2xx carries the WIRE-1 §4 envelope in
    // `body`, which the seam rejects with as-is. This module never unpacks or reshapes it.
    return { ok: response.ok, body: parsed };
  };
}

export default createHttpTransport;
