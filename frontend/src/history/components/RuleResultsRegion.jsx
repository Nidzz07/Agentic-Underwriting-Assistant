import { useState } from 'react';
import { HISTORY_COPY } from '../copy.js';
import { historyRuleResultTestid } from '../testids.js';

// C10 — MountedButHiddenFaithfulDisclosurePattern (P9 / RULERESULTS-1 / NFR-HIST-Fold-C).
//
// FAITHFUL disclosure: EVERY `rule_results` entry is rendered MOUNTED, in the delivered order, with
// none dropped, truncated or client-re-sorted (BR-HIST-5 / full-explainability). The progressive
// disclosure collapses via the HTML `hidden` attribute — which removes the collapsed entries from the
// ACCESSIBILITY TREE (a screen reader does not announce them, so no separate `aria-hidden` is needed)
// while keeping every entry in the DOM. Entries are NEVER unmounted: unmounting would drop data, and
// the faithfulness guarantee must hold in both the collapsed and the expanded state.
//
// This component owns ONLY its local disclosure state (the Code-Gen mechanic the plan assigned it). It
// holds no fetch seam, no Role, no router and no write reference — HistoryView remains the only
// fetch-stateful component.
export function RuleResultsRegion({ ruleResults, testid = 'history-detail-ruleresults' }) {
  const [expanded, setExpanded] = useState(false);
  const entries = ruleResults.rule_results;

  return (
    <section data-testid={testid} aria-label={HISTORY_COPY.ruleResultsHeading}>
      <h3>{HISTORY_COPY.ruleResultsHeading}</h3>
      <button
        type="button"
        data-testid="history-detail-ruleresults-toggle"
        aria-expanded={expanded}
        onClick={() => setExpanded((v) => !v)}
      >
        {expanded ? HISTORY_COPY.collapseLabel : HISTORY_COPY.expandLabel}
      </button>
      {/* hidden => out of the a11y tree, but every entry stays MOUNTED (Fold-C). */}
      <ul data-testid="history-detail-ruleresults-list" hidden={!expanded}>
        {entries.map((entry) => (
          <li key={entry.rule_id} data-testid={historyRuleResultTestid(entry.rule_id)}>
            <span>{entry.rule_id}</span>
            <span>{entry.status}</span>
            <span>{entry.outcome_tier}</span>
            <span>{entry.message}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default RuleResultsRegion;
