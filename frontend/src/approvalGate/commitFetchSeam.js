// C2 (approvalGate/commitFetchSeam) — the own-local DUAL-OPERATION seam. MIRRORS ui-queue's /
// ui-memo-view's fetchSeam pattern but is NOT imported from either (both frozen, kept decoupled).
// Owns request-building + failure NORMALIZATION only; it makes NO real network call itself — the real
// transport is wired at the composition root (deferred / Build & Test), or a capturing double in
// tests. PERF-1: both operations target a single bounded resource (never a list/all-rows path).
//
// Vocabulary (CG-Fold-3, consistent across this module and the C5/C6/C7 header comments):
//   - "the seam"          = the object returned by createCommitFetch(transport): { fetchContext, submitApprove }.
//   - "the commit trigger" = the onConfirm invocation (in ApprovalGateView) that calls submitApprove.
//   - "the single call site" = CommitConfirmDialog's Confirm handler (the only path that fires onConfirm).

// Build the WIRE-1 R4 request for exactly ONE memo by applicationId (a single bounded resource — PERF-1).
export function buildMemoRequest(applicationId) {
  return { method: 'GET', path: `/applications/${applicationId}/memo` };
}

// Build the WIRE-1 R5 approve-only commit request (P3 / BODY-1, by-construction).
// Takes ONLY recommendationId; the body is the literal { action: 'approve' } — there is NO `reason`
// and NO `underwriter_id` parameter, so this builder STRUCTURALLY CANNOT emit either. `underwriter_id`
// is derived server-side from the authenticated session (WIRE1-Fold-1); `recommendation_id` is in the path.
export function buildCommitRequest(recommendationId) {
  return {
    method: 'POST',
    path: `/recommendations/${recommendationId}/commit`,
    body: { action: 'approve' },
  };
}

// Normalize ANY failure to a well-formed error envelope { error: { code, message, detail } } — the
// SAME shape as WIRE-1 §4 (and ui-queue's / ui-memo-view's normalizeError), so CommitStateView
// (ERROR-1) never unpacks a raw exception. The cross-unit consistency comes from the shared WIRE-1
// contract, NOT from importing a sibling. A parsed non-2xx body already well-formed passes through; a
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
 * createCommitFetch(transport) -> the dual-operation seam { fetchContext, submitApprove }.
 *
 * `transport(request)` is INJECTED (a capturing double in tests; a real HTTP transport at the
 * composition root — deferred). It resolves `{ ok: boolean, body }` and may throw on a transport
 * failure. Duck-typed — no formal interface (ND-D-Fold; no-TS React, so no Protocol construct).
 *
 * fetchContext(applicationId):
 *   - resolves the R4 MemoView body
 *     `{ application_id, recommendation_id|null, status:"ready"|"pending", profile|null, report|null, memo|null }`
 *     on success (ok === true);
 *   - REJECTS on any failure, the rejection ALWAYS carrying a well-formed
 *     `{ error: { code, message, detail } }` envelope (never a raw exception).
 *
 * submitApprove(recommendationId):
 *   - POSTs the approve-only body `{ action: 'approve' }` (buildCommitRequest — no underwriter_id / no reason);
 *   - resolves the R5 `CommittedDecision` `{ recommendation_id, underwriter_id, action, reason|null }`
 *     on success (ok === true);
 *   - REJECTS on any failure, the rejection ALWAYS carrying the well-formed envelope.
 */
export function createCommitFetch(transport) {
  async function fetchContext(applicationId) {
    let response;
    try {
      response = await transport(buildMemoRequest(applicationId));
    } catch (cause) {
      throw normalizeError(cause);
    }
    if (response && response.ok) return response.body;
    throw normalizeError(response && response.body);
  }

  async function submitApprove(recommendationId) {
    let response;
    try {
      response = await transport(buildCommitRequest(recommendationId));
    } catch (cause) {
      throw normalizeError(cause);
    }
    if (response && response.ok) return response.body;
    throw normalizeError(response && response.body);
  }

  return { fetchContext, submitApprove };
}
