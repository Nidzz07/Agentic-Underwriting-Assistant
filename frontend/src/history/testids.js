// ui-history dynamic-testid builders (Q5-A realization detail). The history-<element>-<purpose>
// convention (queue-family, regex ^history-[a-z]+(-[a-z0-9]+)+$) requires lower-case, kebab-safe
// segments — but the interpolated segments come from BACKEND ids (`decision_id`, `rule_id`) which may
// carry upper-case letters or underscores (e.g. `INCOME_MIN`). These builders slug the dynamic segment
// so every generated id satisfies the convention. The generated ids are template literals, so the
// history-testid-convention lint (which inspects literal data-testid attributes only) does not see
// them — `slugSegment` + its self-test are the enforcement here.
//
// CG-HIST-Fold-2: the literal prefixes below are deliberately token-free ("history-row-",
// "history-detail-ruleresult-") — a hyphen-delimited "decision" segment would fail the reused
// advisory-vocabulary lint.

export function slugSegment(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// One history list row (US-UI-6: "history rows carry data-testid"); `decision_id` is the R7 key.
export function historyRowTestid(decisionId) {
  return `history-row-${slugSegment(decisionId)}`;
}

// One rule_results entry — the shape the RULERESULTS-1 DOM-level query targets (NFR-HIST-Fold-C).
export function historyRuleResultTestid(ruleId) {
  return `history-detail-ruleresult-${slugSegment(ruleId)}`;
}
