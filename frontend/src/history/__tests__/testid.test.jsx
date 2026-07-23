import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { isValidHistoryTestid } from '../../../eslint-rules/history.js';
import { slugSegment, historyRowTestid, historyRuleResultTestid } from '../testids.js';
import { openDetail, renderHistory, pageKRows, unsortedRuleResults } from './fixtures.js';

// TESTID-1 (BR-HIST-10) — the PRESENCE half (the lint half lives in eslint.history.rules.test.js).
// US-UI-6 requires every history ROW to carry a data-testid; the two REGION-level ids make BR-HIST-2's
// namespace separation structurally testable.
const DETAIL_FIELD_IDS = [
  'history-detail-record-id',
  'history-detail-recommendation-id',
  'history-detail-recommendation',
  'history-detail-confidence',
  'history-detail-action',
  'history-detail-underwriter',
  'history-detail-rulebook-version',
  'history-detail-model-version',
  'history-detail-engine-version',
  'history-detail-memo-hash',
  'history-detail-content-hash',
  'history-detail-timestamp',
  'history-detail-status',
  'history-detail-ruleresults-toggle',
  'history-detail-profile-application',
  'history-detail-profile-hash',
  'history-detail-back',
];

describe('TESTID-1 — every list row carries history-row-<decision_id>', () => {
  it('each of the N rows carries its own id, and each id follows the convention', async () => {
    renderHistory();
    await screen.findByTestId('history-list');
    for (const row of pageKRows) {
      const node = screen.getByTestId(historyRowTestid(row.decision_id));
      expect(node).toBeInTheDocument();
      expect(isValidHistoryTestid(node.dataset.testid)).toBe(true);
    }
    expect(screen.getAllByRole('listitem')).toHaveLength(pageKRows.length);
  });
});

describe('TESTID-1 — the two region testids are present AND distinct', () => {
  it('system and human region ids both exist and are different nodes', async () => {
    await openDetail('dec-21');
    const system = await screen.findByTestId('history-detail-system-region');
    const human = screen.getByTestId('history-detail-human-region');
    expect(system).not.toBe(human);
    expect(isValidHistoryTestid('history-detail-system-region')).toBe(true);
    expect(isValidHistoryTestid('history-detail-human-region')).toBe(true);
  });

  it('every per-field detail id is present and convention-compliant', async () => {
    await openDetail('dec-21');
    await screen.findByTestId('history-detail');
    for (const id of DETAIL_FIELD_IDS) {
      expect(screen.getByTestId(id)).toBeInTheDocument();
      expect(isValidHistoryTestid(id)).toBe(true);
    }
    for (const entry of unsortedRuleResults) {
      const id = historyRuleResultTestid(entry.rule_id);
      expect(screen.getByTestId(id)).toBeInTheDocument();
      expect(isValidHistoryTestid(id)).toBe(true);
    }
  });
});

describe('TESTID-1 — the dynamic-segment slugger (detector self-test, non-vacuous)', () => {
  it('slugSegment produces convention-safe segments from raw backend ids', () => {
    expect(slugSegment('dec-21')).toBe('dec-21');
    expect(slugSegment('INCOME_MIN')).toBe('income-min');
    expect(slugSegment('R-3')).toBe('r-3');
    expect(slugSegment('  weird/id  ')).toBe('weird-id');
  });
  it('every generated id satisfies the convention even for an ugly raw id', () => {
    expect(historyRowTestid('DEC_99/x')).toBe('history-row-dec-99-x');
    expect(isValidHistoryTestid(historyRowTestid('DEC_99/x'))).toBe(true);
    expect(isValidHistoryTestid(historyRuleResultTestid('INCOME_MIN'))).toBe(true);
    // a raw, unslugged id would VIOLATE the convention — so the slugger is load-bearing.
    expect(isValidHistoryTestid('history-detail-ruleresult-INCOME_MIN')).toBe(false);
  });
});
