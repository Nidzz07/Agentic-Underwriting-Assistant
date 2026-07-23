// =============================================================================================
// C2 (history/historyFetchSeam) — the own-local READ-ONLY DUAL-READ seam. (NFR-DESIGN-Fold-1 / P3 —
// the self-evidence header comment is an EXPLICIT Code-Gen deliverable, mirroring the frozen
// queue/fetchSeam.js + memoView/memoFetchSeam.js JSDoc precedent.)
//
// READ-ONLY, BY CONSTRUCTION — the guarantee this module exists to make self-evident:
//
//   * The exported surface is EXACTLY these four read members, and nothing else:
//         { createHistoryFetch, buildHistoryListRequest, buildHistoryDetailRequest, normalizeError }
//     (no default export either).
//   * BOTH builders emit ONLY `{ method: 'GET', path }` — no other method, no `body` key, ever.
//   * There is DELIBERATELY NO request-body builder and NO `submit*` function — no
//     `buildCommitRequest`/`buildOverrideRequest` analog exists here (contrast the frozen write-path
//     units U7 `ui-approval-gate` / U8 `ui-override-form`, whose records this unit merely READS).
//     A WRITE CAPABILITY IS STRUCTURALLY ABSENT: issuing a POST/PUT/PATCH/DELETE would require adding
//     an entirely new builder plus a body — an obvious, reviewable change that could not pass review
//     silently. It is not merely linted against (INV-FAITHFUL / BR-HIST-3 / FAITHFUL-1).
//
// So the no-write guarantee holds when reading THIS module in isolation; the StructuralGuard
// `noWriteSeam` AST scan (C12) is the regression guard on top of it, not the only safeguard.
//
// This module owns request-building + failure NORMALIZATION only; it makes NO real network call —
// the real transport is wired at the composition root (deferred / Build & Test), or is the capturing
// dual-read double in tests. Duck-typed: no formal interface/Protocol (NFR-HIST-D-Fold — in a no-TS
// React codebase no interface construct exists, so the ui-queue D-Fold-1 reasoning holds a fortiori).
// It MIRRORS the frozen sibling read seams (ui-queue's list seam, ui-memo-view's by-id seam) but
// IMPORTS neither — the structural consistency comes from the shared WIRE-1 contract, not coupling.
//
// PERF-1 (bounded): R6 builds exactly ONE page (`page` + `size` always present — no all-rows path);
// R7 builds exactly ONE record by `decision_id` (no N+1 per-row enrichment).
// =============================================================================================

// Build the WIRE-1 R6 request for exactly ONE bounded page. GET-only; `size` is required (the caller
// owns the page-size default) so no request can ever be built without its bound (PERF-1).
export function buildHistoryListRequest(page, size) {
  return { method: 'GET', path: `/decisions?page=${page}&size=${size}` };
}

// Build the WIRE-1 R7 request for exactly ONE AuditRecord by id. GET-only.
export function buildHistoryDetailRequest(decisionId) {
  return { method: 'GET', path: `/decisions/${decisionId}` };
}

// Normalize ANY failure — from EITHER read — to a well-formed WIRE-1 §4 error envelope
// `{ error: { code, message, detail } }`, so HistoryStateView (ERROR-1) never unpacks a raw exception.
// Own-local (NOT imported from a sibling unit); a parsed non-2xx body that is already a well-formed
// envelope passes through (so R7's 404 `not_found` flows through the GENERIC path — HIST-Fold-3); a
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
 * createHistoryFetch(transport) -> { fetchList, fetchDetail }   — TWO READS, NO WRITE.
 *
 * `transport(request)` is INJECTED (a capturing dual-read double in tests; a real HTTP transport at
 * the composition root — deferred). It resolves `{ ok: boolean, body }` and may throw on a transport
 * failure. Duck-typed — no formal interface (NFR-HIST-D-Fold).
 *
 * fetchList(page, size):
 *   - resolves the R6 page wrapper `{ items: DecisionSummary[], page: { page, size, total } }`
 *   - REJECTS with a well-formed `{ error: { code, message, detail } }` envelope on any failure.
 *
 * fetchDetail(decisionId):
 *   - resolves the R7 `AuditRecord`
 *   - REJECTS with the same well-formed envelope on any failure, INCLUDING 404 `not_found`, which is
 *     surfaced through the generic detail-error path with no special-casing (HIST-Fold-3).
 *
 * The returned object has exactly these two members. There is no third, write-capable member.
 */
export function createHistoryFetch(transport) {
  async function read(request) {
    let response;
    try {
      response = await transport(request);
    } catch (cause) {
      throw normalizeError(cause);
    }
    if (response && response.ok) {
      return response.body;
    }
    throw normalizeError(response && response.body);
  }

  return {
    fetchList: (page, size) => read(buildHistoryListRequest(page, size)),
    fetchDetail: (decisionId) => read(buildHistoryDetailRequest(decisionId)),
  };
}
