// C2 (overrideForm/overrideFetchSeam) — the own-local DUAL-OPERATION, REASON-CARRYING seam. MIRRORS
// ui-queue's / ui-memo-view's / ui-approval-gate's fetchSeam pattern but is NOT imported from any of
// them (all frozen, kept decoupled — OVR-Fold-4; enforced by noApprovalGateImport et al.). Owns
// request-building + failure NORMALIZATION only; it makes NO real network call itself — the real
// transport is wired at the composition root (deferred / Build & Test), or a capturing double in
// tests. PERF-1: both operations target a single bounded resource (never a list/all-rows path).
//
// Vocabulary (consistent across this module and the C5/C6/C7/C8 header comments):
//   - "the seam"           = the object returned by createOverrideFetch(transport): { fetchContext, submitOverride }.
//   - "the commit trigger" = the onConfirm invocation (in OverrideFormView) that calls submitOverride.
//   - "the single call site" = OverrideConfirmDialog's Confirm handler (the only path that fires onConfirm).

// Build the WIRE-1 R4 request for exactly ONE memo by applicationId (a single bounded resource — PERF-1).
export function buildMemoRequest(applicationId) {
  return { method: 'GET', path: `/applications/${applicationId}/memo` };
}

// Build the WIRE-1 R5 OVERRIDE commit request (P4 / BODY-1, by-construction). Takes recommendationId
// AND `reason` as a REQUIRED positional parameter — the inverse of ui-approval-gate's narrow
// buildCommitRequest(recommendationId) (which structurally could emit only { action:'approve' } and had
// NO reason parameter). This builder STRUCTURALLY CANNOT omit `reason`, and has NO `underwriter_id`
// parameter (session-derived, WIRE1-Fold-1). `reason` is serialized AS-ENTERED — NO trim here; the
// non-blank UX gate is the orchestrator's runtime predicate (P2), not the serializer's
// (ND-OVR-Fold-iii). `recommendation_id` is in the path.
export function buildOverrideRequest(recommendationId, reason) {
  return {
    method: 'POST',
    path: `/recommendations/${recommendationId}/commit`,
    body: { action: 'override', reason },
  };
}

// Normalize ANY failure to a well-formed error envelope { error: { code, message, detail } } — the
// SAME shape as WIRE-1 §4 (and the sibling seams' normalizeError), so CommitStateView (ERROR-1) never
// unpacks a raw exception. The cross-unit consistency comes from the shared WIRE-1 contract, NOT from
// importing a sibling (own-local). A parsed non-2xx body already well-formed passes through; a
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
 * createOverrideFetch(transport) -> the dual-operation seam { fetchContext, submitOverride }.
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
 * submitOverride(recommendationId, reason):
 *   - POSTs the override body `{ action: 'override', reason }` (buildOverrideRequest — no underwriter_id).
 *   - `reason` is REQUIRED and sent VERBATIM (as-entered, no trim); non-blankness is the orchestrator's
 *     gate (P2 / BR-OVR-8), NOT the seam's, and the backend `_gate` is the single source of truth
 *     (CON-BR4). A blank reason that slips past the UI is rejected server-side (generic 409).
 *   - resolves the R5 `CommittedDecision` `{ recommendation_id, underwriter_id, action, reason }` on
 *     success (ok === true);
 *   - REJECTS on any failure, the rejection ALWAYS carrying the well-formed envelope.
 */
export function createOverrideFetch(transport) {
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

  async function submitOverride(recommendationId, reason) {
    let response;
    try {
      response = await transport(buildOverrideRequest(recommendationId, reason));
    } catch (cause) {
      throw normalizeError(cause);
    }
    if (response && response.ok) return response.body;
    throw normalizeError(response && response.body);
  }

  return { fetchContext, submitOverride };
}
