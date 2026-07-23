// C2 (memoView/memoFetchSeam) — the own-local injected/capturing R4 seam. MIRRORS ui-queue's
// fetchSeam pattern but is NOT imported from ui-queue (frozen, kept decoupled). Owns request-building
// + failure NORMALIZATION only; it makes NO real network call itself — the real transport is wired at
// the composition root (deferred / Build & Test), or a capturing double in tests. PERF-1: it fetches a
// single BOUNDED resource (one memo by applicationId), never a list/all-rows path.

// Build the WIRE-1 R4 request for exactly ONE memo (a single bounded resource — PERF-1).
export function buildMemoRequest(applicationId) {
  return { method: 'GET', path: `/applications/${applicationId}/memo` };
}

// CG-MEMO-Fold-1 (ambiguity-check iii): normalize ANY failure to a well-formed error envelope
// { error: { code, message, detail } } — the SAME shape as WIRE-1 §4 (and ui-queue's normalizeError),
// so MemoStateView (ERROR-1) never unpacks a raw exception. The structural consistency across both UI
// units comes from the shared WIRE-1 contract, NOT from importing ui-queue. A parsed non-2xx body that
// is already a well-formed envelope passes through; a transport error / missing / malformed body
// becomes a synthesized network_error envelope.
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
 * createMemoFetch(transport) -> memoFetchSeam(applicationId)
 *
 * `transport(request)` is INJECTED (a capturing double in tests; a real HTTP transport at the
 * composition root — deferred). It resolves `{ ok: boolean, body }` and may throw on a transport
 * failure. Duck-typed — no formal interface (D-Fold, ui-queue/admin-cli precedent).
 *
 * memoFetchSeam(applicationId):
 *   - resolves the MemoView body
 *     `{ application_id, recommendation_id|null, status:"ready"|"pending", profile|null, report|null, memo|null }`
 *     on success (ok === true)
 *   - REJECTS on any failure, the rejection ALWAYS carrying a well-formed
 *     `{ error: { code, message, detail } }` envelope (CG-MEMO-Fold-1) — never a raw exception.
 */
export function createMemoFetch(transport) {
  return async function memoFetchSeam(applicationId) {
    let response;
    try {
      response = await transport(buildMemoRequest(applicationId));
    } catch (cause) {
      throw normalizeError(cause);
    }
    if (response && response.ok) {
      return response.body;
    }
    throw normalizeError(response && response.body);
  };
}
