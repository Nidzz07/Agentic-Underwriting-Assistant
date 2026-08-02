// The composition root's seam wiring — every frozen UI unit's injected seam, bound to the REAL
// transport. This is the client-side counterpart of backend/app/dependencies.py: composition
// only. Each `create<X>Fetch` below is the frozen unit's OWN factory, imported and called — no
// seam is reimplemented, and no unit is modified.
//
// BACKING — SUPERSEDED 2026-07-26 (override wiring pass, Q1). The original block described SCOPE A
// and read: "queue -> R2 ⛔ 501 not_implemented · memo -> R4 ⛔ 501 · commit -> R5 ⛔ 501 (approve) ·
// override -> R5 ⛔ 501 (override)", followed by "The four unbacked seams are still constructed here,
// deliberately... which is why they are NOT mounted in App.jsx: a rendered surface that can only ever
// error would imply backing that does not exist."
//
// EVERY LOAD-BEARING CLAIM IN THAT BLOCK IS NOW FALSE, and leaving it would misdescribe the one thing
// this file exists to document. Scope B made all seven routes live; the wiring pass then mounted
// queue/memo/commit against a real backend, and this pass mounts override. Current reality:
//
//     session  -> R1     ✅ real
//     queue    -> R2     ✅ real   (mounted)
//     memo     -> R4     ✅ real   (mounted)
//     commit   -> R5     ✅ real   (mounted — the `approve` action)
//     override -> R5     ✅ real   (mounted — the `override` action, mandatory non-blank reason)
//     history  -> R6/R7  ✅ real   (mounted)
//
// ⚑ All five seams are now both backed AND mounted, so the "constructed but unmounted" rationale no
// longer applies to any of them. The seam SET is unchanged — override was always registered here, so
// mounting it required no edit to `createSeams` and the five-key assertion stays green untouched.
//
//     submission -> R10/R11 ✅ real   (mounted — WIRE1-Fold-6, register #2)
//
// ⚑ SUBMISSION ADDED 2026-08-02. It is the FIRST seam registered here that was not already
// present in Scope A: every other key existed before it was backed. Its unit is also the first
// built for the composition root rather than inherited frozen from the BUILD phase.
//
// ⚑ NOT registered: the outlier seam. That is still a real exclusion (#17 — a wired OutlierView would
// render permanently empty), and it is the only remaining case the old rationale still describes.

import { createQueueFetch } from '../queue/fetchSeam.js';
import { createMemoFetch } from '../memoView/memoFetchSeam.js';
import { createCommitFetch } from '../approvalGate/commitFetchSeam.js';
import { createOverrideFetch } from '../overrideForm/overrideFetchSeam.js';
import { createHistoryFetch } from '../history/historyFetchSeam.js';
import { createSubmissionFetch } from '../submission/fetchSeam.js';

/**
 * createSeams(transport) -> every unit's seam, each over the same real transport.
 *
 * ⚑ SUPERSEDED 2026-08-02 (register #2 / WIRE1-Fold-6). The line read "the five frozen
 * units' seams"; the submission seam makes it SIX. ⚠️ The count is deliberately no longer in
 * this sentence — it has now been wrong once, and the deferred outlier mount will change it
 * again. The exact-key assertion in app.test.jsx is the single place the set is pinned.
 * Duck-typed throughout — no unit exposes or requires a formal interface.
 */
export function createSeams(transport) {
  return {
    queue: createQueueFetch(transport),         // R2 — unbacked in Scope A
    memo: createMemoFetch(transport),           // R4 — unbacked in Scope A
    commit: createCommitFetch(transport),       // R5 — unbacked in Scope A
    override: createOverrideFetch(transport),   // R5 — unbacked in Scope A
    history: createHistoryFetch(transport),     // R6 + R7 — REAL
    submission: createSubmissionFetch(transport), // R10 + R11 — REAL (WIRE1-Fold-6)
  };
}

export default createSeams;
