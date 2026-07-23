// The composition root's seam wiring — every frozen UI unit's injected seam, bound to the REAL
// transport. This is the client-side counterpart of backend/app/dependencies.py: composition
// only. Each `create<X>Fetch` below is the frozen unit's OWN factory, imported and called — no
// seam is reimplemented, and no unit is modified.
//
// SCOPE A — what is actually backed (the rest is wired but unbacked, honestly):
//     session  -> R1  ✅ real
//     history  -> R6/R7 ✅ real           <- the only UI unit with a live backend
//     queue    -> R2  ⛔ 501 not_implemented
//     memo     -> R4  ⛔ 501
//     commit   -> R5  ⛔ 501   (approve)
//     override -> R5  ⛔ 501   (override)
//
// The four unbacked seams are still constructed here, deliberately: they are real seams over the
// real transport, so the day R2-R5 are wired they need no change. Until then a call resolves the
// server's 501 envelope, the frozen seam's `normalizeError` passes it through, and the unit
// renders its ordinary error state. That is a truthful report of the deployment's scope — which
// is why they are NOT mounted in App.jsx: a rendered surface that can only ever error would
// imply backing that does not exist.

import { createQueueFetch } from '../queue/fetchSeam.js';
import { createMemoFetch } from '../memoView/memoFetchSeam.js';
import { createCommitFetch } from '../approvalGate/commitFetchSeam.js';
import { createOverrideFetch } from '../overrideForm/overrideFetchSeam.js';
import { createHistoryFetch } from '../history/historyFetchSeam.js';

/**
 * createSeams(transport) -> the five frozen units' seams, each over the same real transport.
 * Duck-typed throughout — no unit exposes or requires a formal interface.
 */
export function createSeams(transport) {
  return {
    queue: createQueueFetch(transport),         // R2 — unbacked in Scope A
    memo: createMemoFetch(transport),           // R4 — unbacked in Scope A
    commit: createCommitFetch(transport),       // R5 — unbacked in Scope A
    override: createOverrideFetch(transport),   // R5 — unbacked in Scope A
    history: createHistoryFetch(transport),     // R6 + R7 — REAL
  };
}

export default createSeams;
