// C2 (queue/fetchSeam) — the injected/capturing R2 seam (Q1-A NFR-Design; Q3-A prop injection).
// Duck-typed, NO formal interface/Protocol (D-Fold-1, admin-cli injected-Engine precedent). This
// module owns request-building + failure NORMALIZATION only; it makes NO real network call itself —
// the real transport is wired at the composition root (deferred / Build & Test), or a capturing
// double in tests. PERF-1: it only ever builds a single bounded page request (never an all-rows path).

export const DEFAULT_PAGE_SIZE = 20; // Q2-A

// Build the WIRE-1 R2 request for exactly ONE page (page + size always present — PERF-1 bounded).
export function buildQueueRequest(page, size = DEFAULT_PAGE_SIZE) {
  return { method: 'GET', path: `/applications?page=${page}&size=${size}` };
}

// CG-Fold-1 (ambiguity-check ii): normalize ANY failure to a well-formed error envelope
// { error: { code, message, detail } } so QueueStateView (ERROR-1) never has to unpack a raw
// exception. A parsed non-2xx body that is already a well-formed envelope passes through; a
// transport error / missing / malformed body becomes a synthesized network_error envelope.
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
 * createQueueFetch(transport) -> fetchSeam(page, size)
 *
 * `transport(request)` is INJECTED (a capturing double in tests; a real HTTP transport at the
 * composition root — deferred). It resolves `{ ok: boolean, body }` and may throw on a transport
 * failure. Duck-typed — no formal interface (D-Fold-1).
 *
 * fetchSeam(page, size):
 *   - resolves `{ items: ApplicationSummary[], page: { page, size, total } }` on success (ok === true)
 *   - REJECTS on any failure, the rejection ALWAYS carrying a well-formed
 *     `{ error: { code, message, detail } }` envelope (CG-Fold-1) — never a raw exception.
 */
export function createQueueFetch(transport) {
  return async function fetchSeam(page, size = DEFAULT_PAGE_SIZE) {
    let response;
    try {
      response = await transport(buildQueueRequest(page, size));
    } catch (cause) {
      throw normalizeError(cause);
    }
    if (response && response.ok) {
      return response.body;
    }
    throw normalizeError(response && response.body);
  };
}
