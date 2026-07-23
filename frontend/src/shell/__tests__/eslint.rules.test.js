import { RuleTester } from 'eslint';
import { describe, it, expect } from 'vitest';
import rules, { findForbiddenSystemOutput, isValidTestid } from '../../../eslint-rules/index.js';

// COPY-1 / ADVISORY-1 / TESTID-1 — the three build-failing lints, each proven NON-VACUOUS by an
// ESLint RuleTester detector self-test (invalid fixtures MUST error). Each rule reads the SINGLE
// shell/copy + FORBIDDEN_TERMS source (fold 1).

RuleTester.describe = describe;
RuleTester.it = it;
RuleTester.itOnly = it.only;

const ruleTester = new RuleTester({
  languageOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    parserOptions: { ecmaFeatures: { jsx: true } },
  },
});

const COMPONENT = 'src/shell/components/Sample.jsx';
const COPY = 'src/shell/copy/index.js';

ruleTester.run('no-inline-label', rules['no-inline-label'], {
  valid: [
    // Look-up by value — no inlined literal.
    { code: 'const x = <span>{RECOMMENDATION_LABELS[value]}</span>;', filename: COMPONENT },
    // The copy module is EXEMPT — labels are defined there.
    { code: "export const L = { 'DECLINE-RECOMMEND': 'Decline-Recommend' };", filename: COPY },
    // An unrelated literal is fine.
    { code: 'const x = <span>Queue</span>;', filename: COMPONENT },
  ],
  invalid: [
    { code: 'const x = <span>Decline-Recommend</span>;', filename: COMPONENT, errors: 1 },
    { code: "const x = 'Refer';", filename: COMPONENT, errors: 1 },
  ],
});

ruleTester.run('advisory-vocabulary', rules['advisory-vocabulary'], {
  valid: [
    { code: "const s = 'Decline-Recommend';", filename: COMPONENT },
    { code: "const s = 'recommendation';", filename: COMPONENT },
    // The copy module is EXEMPT — it defines the forbidden list.
    { code: "export const F = ['DECLINE', 'decision'];", filename: COPY },
  ],
  invalid: [
    { code: "const s = 'DECLINE';", filename: COMPONENT, errors: 1 },
    { code: "const s = 'This decision is final';", filename: COMPONENT, errors: 1 },
    { code: "const s = 'Application approved';", filename: COMPONENT, errors: 1 },
    { code: "const s = 'Application declined';", filename: COMPONENT, errors: 1 },
    { code: 'const x = <span>DECLINE</span>;', filename: COMPONENT, errors: 1 },
  ],
});

ruleTester.run('testid-convention', rules['testid-convention'], {
  valid: [
    { code: 'const x = <div data-testid="shell-panel-queue" />;', filename: COMPONENT },
    { code: 'const x = <div data-testid={testid} />;', filename: COMPONENT },
    { code: 'const x = <div className="shell-panel" />;', filename: COMPONENT },
  ],
  invalid: [
    { code: 'const x = <div data-testid="queuePanel" />;', filename: COMPONENT, errors: 1 },
    { code: 'const x = <div data-testid="shell_panel" />;', filename: COMPONENT, errors: 1 },
    { code: 'const x = <div data-testid="Shell-Panel" />;', filename: COMPONENT, errors: 1 },
  ],
});

// Direct detector self-tests (belt-and-braces; the detectors are the rule internals).
describe('detector self-tests', () => {
  it('findForbiddenSystemOutput flags forbidden tokens and passes canonical labels', () => {
    expect(findForbiddenSystemOutput('DECLINE').length).toBeGreaterThan(0);
    expect(findForbiddenSystemOutput('declined').length).toBeGreaterThan(0);
    expect(findForbiddenSystemOutput('this decision is final').length).toBeGreaterThan(0);
    expect(findForbiddenSystemOutput('approved').length).toBeGreaterThan(0);
    expect(findForbiddenSystemOutput('Decline-Recommend')).toEqual([]);
    expect(findForbiddenSystemOutput('recommendation')).toEqual([]);
  });

  it('isValidTestid enforces the shell-<primitive>-<purpose> convention', () => {
    expect(isValidTestid('shell-panel-queue')).toBe(true);
    expect(isValidTestid('shell-recommendationbadge-value')).toBe(true);
    expect(isValidTestid('queuePanel')).toBe(false);
    expect(isValidTestid('shell_panel')).toBe(false);
    expect(isValidTestid('shell-panel')).toBe(false);
  });
});
