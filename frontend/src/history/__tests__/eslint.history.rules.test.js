import { RuleTester } from 'eslint';
import { describe, it, expect } from 'vitest';
import shellRules, { LINT_FORBIDDEN_TERMS, findForbiddenSystemOutput } from '../../../eslint-rules/index.js';
import historyRules, { isValidHistoryTestid } from '../../../eslint-rules/history.js';
import { FORBIDDEN_TERMS } from '../../shell/copy/forbiddenTerms.js';
import { HISTORY_COPY } from '../copy.js';

// COPY-1 + ADVISORY-1 (the REUSED shell lints — the ONE FORBIDDEN_TERMS, no new word-list, applied
// UNMODIFIED per NFR-HIST-Fold-D) + TESTID-1 (history-<element>-<purpose>). Each proven NON-VACUOUS
// via RuleTester invalid fixtures + a detector self-test.
RuleTester.describe = describe;
RuleTester.it = it;
RuleTester.itOnly = it.only;

const ruleTester = new RuleTester({
  languageOptions: { ecmaVersion: 'latest', sourceType: 'module', parserOptions: { ecmaFeatures: { jsx: true } } },
});

const HFILE = 'src/history/components/Sample.jsx';

ruleTester.run('no-inline-label (reused for history / COPY-1)', shellRules['no-inline-label'], {
  valid: [
    { code: 'const x = <span>{RECOMMENDATION_LABELS[value]}</span>;', filename: HFILE },
    { code: 'const x = <span>{COMMIT_ACTION_LABELS[action]}</span>;', filename: HFILE },
    { code: 'const x = <span>History</span>;', filename: HFILE },
  ],
  invalid: [
    { code: 'const x = <span>Decline-Recommend</span>;', filename: HFILE, errors: 1 },
    { code: "const x = 'Override';", filename: HFILE, errors: 1 },
    { code: "const x = 'Refer';", filename: HFILE, errors: 1 },
  ],
});

ruleTester.run('advisory-vocabulary (reused UNMODIFIED for history / ADVISORY-1)', shellRules['advisory-vocabulary'], {
  valid: [
    // the Fold-D binding rule in action: the PLURAL passes, the token-avoiding wording passes.
    { code: 'const x = <span>No decisions yet</span>;', filename: HFILE },
    { code: "const x = <span>Underwriter's committed action</span>;", filename: HFILE },
    { code: 'const x = <span>Committed outcome</span>;', filename: HFILE },
    { code: 'const x = <span>System recommendation</span>;', filename: HFILE },
    { code: 'const x = <span>Rulebook version</span>;', filename: HFILE },
    { code: "const x = { path: `/decisions/${id}` };", filename: HFILE },
  ],
  invalid: [
    // the STANDALONE SINGULAR is flagged — the wording constraint is non-vacuous.
    { code: "const x = <span>Underwriter's decision</span>;", filename: HFILE, errors: 1 },
    { code: 'const x = <span>Decision history</span>;', filename: HFILE, errors: 1 },
    { code: "const x = 'the application was approved';", filename: HFILE, errors: 1 },
    { code: "const x = 'the application was declined';", filename: HFILE, errors: 1 },
    // CG-HIST-Fold-2: a HYPHEN-delimited "decision" testid segment is flagged too.
    { code: 'const x = <div data-testid="history-detail-decision-id" />;', filename: HFILE, errors: 1 },
  ],
});

ruleTester.run('history-testid-convention (TESTID-1)', historyRules['history-testid-convention'], {
  valid: [
    { code: 'const x = <div data-testid="history-detail-system-region" />;', filename: HFILE },
    { code: 'const x = <div data-testid="history-state-empty" />;', filename: HFILE },
    { code: 'const x = <div data-testid={testid} />;', filename: HFILE },
    { code: 'const x = <li data-testid={`history-row-${id}`} />;', filename: HFILE },
  ],
  invalid: [
    { code: 'const x = <div data-testid="queue-row-1" />;', filename: HFILE, errors: 1 },
    { code: 'const x = <div data-testid="historyView" />;', filename: HFILE, errors: 1 },
    { code: 'const x = <div data-testid="history_detail" />;', filename: HFILE, errors: 1 },
    { code: 'const x = <div data-testid="history-detail-RECORD" />;', filename: HFILE, errors: 1 },
  ],
});

describe('ADVISORY-1 — the ONE FORBIDDEN_TERMS source (no second word-list)', () => {
  it('the lint and shell/copy share a single source object', () => {
    expect(LINT_FORBIDDEN_TERMS).toBe(FORBIDDEN_TERMS);
  });
  it('every HISTORY_COPY string is clean against the REAL word-boundary detector (Fold-D)', () => {
    const flatten = (o) => Object.values(o).flatMap((v) => (typeof v === 'object' ? flatten(v) : [v]));
    for (const value of flatten(HISTORY_COPY)) {
      expect(findForbiddenSystemOutput(value), `HISTORY_COPY value: ${value}`).toEqual([]);
    }
  });
  it('detector self-test: the real detector flags the standalone singular but not the plural', () => {
    expect(findForbiddenSystemOutput("Underwriter's decision")).toContain('decision');
    expect(findForbiddenSystemOutput('Decision history')).toContain('decision');
    expect(findForbiddenSystemOutput('history-detail-decision-id')).toContain('decision');
    expect(findForbiddenSystemOutput('No decisions yet')).toEqual([]);
    expect(findForbiddenSystemOutput('decision_id')).toEqual([]);
    expect(findForbiddenSystemOutput('/decisions?page=1&size=20')).toEqual([]);
  });
});

describe('detector self-tests (non-vacuous)', () => {
  it('isValidHistoryTestid enforces history-<element>-<purpose>', () => {
    expect(isValidHistoryTestid('history-detail-system-region')).toBe(true);
    expect(isValidHistoryTestid('history-detail-human-region')).toBe(true);
    expect(isValidHistoryTestid('history-row-dec-21')).toBe(true);
    expect(isValidHistoryTestid('history-error-code')).toBe(true);
    expect(isValidHistoryTestid('queue-row-1')).toBe(false);
    expect(isValidHistoryTestid('historyView')).toBe(false);
    expect(isValidHistoryTestid('history')).toBe(false);
  });
});
