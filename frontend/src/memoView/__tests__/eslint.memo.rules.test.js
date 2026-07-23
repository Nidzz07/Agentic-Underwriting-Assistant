import { RuleTester } from 'eslint';
import { describe, it, expect } from 'vitest';
import shellRules from '../../../eslint-rules/index.js';
import memoRules, { isValidMemoTestid } from '../../../eslint-rules/memoView.js';

// COPY-1 + ADVISORY-1 (reused shell lints — the ONE FORBIDDEN_TERMS, no new word-list) + TESTID-1
// (memo-<element>-<purpose>). Each proven NON-VACUOUS via RuleTester invalid fixtures + a detector
// self-test. The advisory-vocabulary lint asserts STATIC view code only — never narrative_prose
// content (BR-MEMO-2 governance).
RuleTester.describe = describe;
RuleTester.it = it;
RuleTester.itOnly = it.only;

const ruleTester = new RuleTester({
  languageOptions: { ecmaVersion: 'latest', sourceType: 'module', parserOptions: { ecmaFeatures: { jsx: true } } },
});

const MFILE = 'src/memoView/components/Sample.jsx';

ruleTester.run('no-inline-label (reused for memoView / COPY-1)', shellRules['no-inline-label'], {
  valid: [
    { code: 'const x = <span>{RECOMMENDATION_LABELS[value]}</span>;', filename: MFILE },
    { code: 'const x = <span>Narrative</span>;', filename: MFILE },
  ],
  invalid: [
    { code: 'const x = <span>Decline-Recommend</span>;', filename: MFILE, errors: 1 },
    { code: "const x = 'Refer';", filename: MFILE, errors: 1 },
  ],
});

ruleTester.run('advisory-vocabulary (reused for memoView / ADVISORY-1)', shellRules['advisory-vocabulary'], {
  valid: [
    { code: 'const x = <span>Recommendation from the rules engine</span>;', filename: MFILE },
    { code: 'const x = <span>Missing information</span>;', filename: MFILE },
  ],
  invalid: [
    { code: 'const x = <span>final decision</span>;', filename: MFILE, errors: 1 },
    { code: "const x = 'the application was approved';", filename: MFILE, errors: 1 },
  ],
});

ruleTester.run('memo-testid-convention (TESTID-1)', memoRules['memo-testid-convention'], {
  valid: [
    { code: 'const x = <div data-testid="memo-region-readonly" />;', filename: MFILE },
    { code: 'const x = <div data-testid="memo-view" />;', filename: MFILE },
    { code: 'const x = <div data-testid={testid} />;', filename: MFILE },
    { code: 'const x = <li data-testid={`memo-citation-${id}`} />;', filename: MFILE },
  ],
  invalid: [
    { code: 'const x = <div data-testid="queue-table" />;', filename: MFILE, errors: 1 },
    { code: 'const x = <div data-testid="memoView" />;', filename: MFILE, errors: 1 },
    { code: 'const x = <div data-testid="memo_region" />;', filename: MFILE, errors: 1 },
  ],
});

describe('detector self-tests (non-vacuous)', () => {
  it('isValidMemoTestid enforces memo-<element>-<purpose>', () => {
    expect(isValidMemoTestid('memo-state-loading')).toBe(true);
    expect(isValidMemoTestid('memo-recommendation')).toBe(true);
    expect(isValidMemoTestid('memo-view')).toBe(true);
    expect(isValidMemoTestid('shell-panel-memo')).toBe(false);
    expect(isValidMemoTestid('memoView')).toBe(false);
    expect(isValidMemoTestid('memo')).toBe(false);
  });
});
