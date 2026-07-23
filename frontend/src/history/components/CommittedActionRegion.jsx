import { COMMIT_ACTION_LABELS } from '../../shell/copy/index.js';
import { HISTORY_COPY } from '../copy.js';

// =============================================================================================
// C8 — CommittedActionRegion. StructuralIsolationCompositionPattern (P2 / SEPARATION-1) +
// ConditionalFieldRenderingPattern (P10 / REASON-1). The self-evidence header comment is an EXPLICIT
// Code-Gen deliverable — the mirror of C7's.
//
// BY CONSTRUCTION — props are `{ action, reason, underwriterId, testid }` ONLY.
//   * This region is the SOLE holder / SOLE render site of the HUMAN committed action (sourced from
//     R7's `committed_decision`): WHAT (`action`), WHY (`reason`), WHO (`underwriter_id`).
//   * It has NO `recommendation` / `confidence` prop and NO PATH by which the SYSTEM namespace could
//     reach it. Rendering the system recommendation here would require FIRST adding a new prop to the
//     wrong component — an obvious, reviewable change (BR-HIST-2 / WIRE-1 §1 / CON-BR4).
//   * It is a SIBLING of SystemRecommendationRegion, never an ancestor or descendant of it.
//   * The human `override` is rendered ONLY via COMMIT_ACTION_LABELS.override ("Override") — it is
//     NOT, and must never render as, the system `DECLINE-RECOMMEND`.
//
// P10: `reason` renders IFF `action === 'override'` (present/non-blank per the frozen U7/U8 gate) and
// is ABSENT on `approve`; `action` and `underwriterId` always render.
// COPY-1: the CommitAction label is looked up BY VALUE from the frozen shell/copy — never inlined.
// HIST-Fold-4 / NFR-HIST-Fold-D: the heading is namespace-distinct while avoiding the standalone
// singular lexical token, so the reused blanket advisory-vocabulary lint stays UNMODIFIED.
// =============================================================================================
export function CommittedActionRegion({ action, reason, underwriterId, testid = 'history-detail-human-region' }) {
  return (
    <section data-testid={testid} aria-label={HISTORY_COPY.committedActionHeading}>
      <h3>{HISTORY_COPY.committedActionHeading}</h3>
      <p>
        <span>{HISTORY_COPY.committedOutcomeHeading}</span>
        <span data-testid="history-detail-action">{COMMIT_ACTION_LABELS[action]}</span>
      </p>
      {action === 'override' ? (
        <p>
          <span>{HISTORY_COPY.reasonHeading}</span>
          <span data-testid="history-detail-reason">{reason}</span>
        </p>
      ) : null}
      <p>
        <span>{HISTORY_COPY.underwriterHeading}</span>
        <span data-testid="history-detail-underwriter">{underwriterId}</span>
      </p>
    </section>
  );
}

export default CommittedActionRegion;
