// C-OUTV-2 (outlierView/fetchSeam) — MANDATORY header comment (NFR-ND-OUTV-Fold-1).
//
// READ-ONLY R4 seam. `buildOutlierRequest` emits ONLY a GET request; there is no request-body
// builder and no submit* export — the write path is structurally absent, not merely unused
// (P-OUTV-6 / FETCH-1, BR-OUTV-4). It makes NO real network call itself: the real transport is
// wired at the composition root (deferred — R4 is still a 501 stub), or a capturing double in
// tests (D-OUTV-1 / Fold-A).
//
// It MIRRORS the sibling read seams (memoView/memoFetchSeam, queue) WITHOUT importing them — the
// structural consistency comes from the shared WIRE-1 contract, never from a cross-unit import
// (BR-OUTV-10 / SCOPE-1). The frozen sibling trees stay untouched.
//
// Documentation only — NOT enforcement. The enforcement is the absence of any body-builder/submit
// code (asserted by the noWriteSeam scan over comment-stripped source, CG-OUTV-Fold-1).

// Build the WIRE-1 R4 request for exactly ONE application's memo view (the outlier slice is read
// off the resolved body). GET only — no method parameter, no body key.
export function buildOutlierRequest(applicationId) {
  return { method: 'GET', path: `/applications/${applicationId}/memo` };
}

// Normalize ANY failure to the well-formed WIRE-1 §4 error envelope { error: { code, message,
// detail } }, so OutlierStateView (ERROR-1 / P-OUTV-7) never unpacks a raw exception. A parsed
// non-2xx body that is already a well-formed envelope passes through; a transport error / missing
// / malformed body becomes a synthesized network_error envelope. Mirrors the sibling normalizeError
// shape via the shared contract, not by import.
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
 * createOutlierFetch(transport) -> fetchOutlier(applicationId)
 *
 * `transport(request)` is INJECTED (a capturing double in tests; a real HTTP transport at the
 * composition root — deferred). It resolves `{ ok: boolean, body }` and may throw on a transport
 * failure. Duck-typed — no formal interface (the ui-queue / ui-memo-view precedent).
 *
 * fetchOutlier(applicationId):
 *   - resolves the R4 MemoView body
 *     `{ application_id, recommendation_id|null, status:"ready"|"pending", profile|null,
 *        report|null, memo|null, outlier: OutlierResult|null }`
 *     on success (ok === true) — the view reads ONLY the `outlier` slice off it (BR-OUTV-1)
 *   - REJECTS on any failure, the rejection ALWAYS carrying a well-formed
 *     `{ error: { code, message, detail } }` envelope — never a raw exception.
 */
export function createOutlierFetch(transport) {
  return async function fetchOutlier(applicationId) {
    let response;
    try {
      response = await transport(buildOutlierRequest(applicationId));
    } catch (cause) {
      throw normalizeError(cause);
    }
    if (response && response.ok) {
      return response.body;
    }
    throw normalizeError(response && response.body);
  };
}
