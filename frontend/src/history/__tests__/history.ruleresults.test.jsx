import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { RuleResultsRegion } from '../components/RuleResultsRegion.jsx';
import { historyRuleResultTestid } from '../testids.js';
import { openDetail, unsortedRuleResults, singleRuleResult, singleRuleResultRecord } from './fixtures.js';

// RULERESULTS-1 (NFR-HIST-Fold-C) — faithful disclosure: EVERY rule_results entry is rendered, in the
// delivered order, none dropped/truncated/re-sorted, in BOTH the collapsed and the expanded state.
//
// The "all N present" assertion uses a DOM-LEVEL query (getAllByTestId / querySelectorAll), which
// finds MOUNTED-BUT-HIDDEN nodes — deliberately NOT a visibility-filtering role/text query, which
// would miss the collapsed entries and false-fail (Fold-C).
const expectedOrder = unsortedRuleResults.map((r) => historyRuleResultTestid(r.rule_id));

function renderRegion(entries) {
  const report = { rule_results: entries, recommendation: 'REFER', confidence: 'Low' };
  return render(<RuleResultsRegion ruleResults={report} />);
}

describe('RuleResultsRegion — RULERESULTS-1: every entry mounted, input order preserved (teeth)', () => {
  it('renders all N deliberately-unsorted entries in the INPUT order (no client re-sort)', () => {
    const { container } = renderRegion(unsortedRuleResults);
    const rendered = [...container.querySelectorAll('[data-testid^="history-detail-ruleresult-"]')]
      .map((el) => el.dataset.testid);
    expect(rendered).toHaveLength(unsortedRuleResults.length);
    expect(rendered).toEqual(expectedOrder);
    // the input is genuinely NOT sorted — a client sort would reorder it (the teeth are non-vacuous).
    expect(expectedOrder).not.toEqual([...expectedOrder].sort());
  });

  it('holds in BOTH the collapsed and the expanded state — collapse is hidden, never unmount', () => {
    const { container } = renderRegion(unsortedRuleResults);
    const list = screen.getByTestId('history-detail-ruleresults-list');
    const idsNow = () => [...container.querySelectorAll('[data-testid^="history-detail-ruleresult-"]')]
      .map((el) => el.dataset.testid);

    // collapsed by default: out of the a11y tree, but every entry still MOUNTED.
    expect(list).toHaveAttribute('hidden');
    expect(idsNow()).toEqual(expectedOrder);

    fireEvent.click(screen.getByTestId('history-detail-ruleresults-toggle'));
    expect(list).not.toHaveAttribute('hidden');
    expect(idsNow()).toEqual(expectedOrder);

    fireEvent.click(screen.getByTestId('history-detail-ruleresults-toggle'));
    expect(list).toHaveAttribute('hidden');
    expect(idsNow()).toEqual(expectedOrder);
  });

  it('the length-1 fixture passes too', () => {
    const { container } = renderRegion(singleRuleResult);
    expect(container.querySelectorAll('[data-testid^="history-detail-ruleresult-"]')).toHaveLength(1);
    expect(screen.getByTestId(historyRuleResultTestid('INCOME_MIN'))).toBeInTheDocument();
  });

  it('the disclosure toggle is keyboard-focusable and reports its state (A11Y-1)', () => {
    renderRegion(unsortedRuleResults);
    const toggle = screen.getByTestId('history-detail-ruleresults-toggle');
    expect(toggle.tagName).toBe('BUTTON');
    toggle.focus();
    expect(toggle).toHaveFocus();
    expect(toggle).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
  });
});

describe('DecisionDetail — RULERESULTS-1 through the real master-detail render', () => {
  it('a large-N report renders all N entries in order inside the detail', async () => {
    await openDetail('dec-21');
    await screen.findByTestId('history-detail');
    expect(screen.getAllByTestId(/^history-detail-ruleresult-/).map((el) => el.dataset.testid))
      .toEqual(expectedOrder);
  });

  it('a length-1 report renders its single entry inside the detail', async () => {
    await openDetail('dec-21', { detail: [{ resolve: singleRuleResultRecord }] });
    await screen.findByTestId('history-detail');
    expect(screen.getAllByTestId(/^history-detail-ruleresult-/)).toHaveLength(1);
  });
});
