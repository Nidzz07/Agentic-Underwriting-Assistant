import { RuleTester } from 'eslint';
import { describe, it, expect } from 'vitest';
import shellRules, { LINT_FORBIDDEN_TERMS } from '../../../eslint-rules/index.js';
import { FORBIDDEN_TERMS } from '../../shell/copy/forbiddenTerms.js';
import overrideRules, { isValidOverrideTestid } from '../../../eslint-rules/overrideForm.js';
import { OVERRIDE_COPY } from '../copy.js';

// COPY-1 + ADVISORY-1 (reused shell lints — the ONE FORBIDDEN_TERMS, no new word-list; the
// advisory-vocabulary lint UNMODIFIED, NFR-OVR-Fold-3) + TESTID-1 (override-<element>-<purpose>).
// Each proven NON-VACUOUS via RuleTester invalid fixtures + a detector self-test.
RuleTester.describe = describe;
RuleTester.it = it;
RuleTester.itOnly = it.only;

const ruleTester = new RuleTester({
  languageOptions: { ecmaVersion: 'latest', sourceType: 'module', parserOptions: { ecmaFeatures: { jsx: true } } },
});

const OFILE = 'src/overrideForm/components/Sample.jsx';

ruleTester.run('no-inline-label (reused for overrideForm / COPY-1)', shellRules['no-inline-label'], {
  valid: [
    { code: 'const x = <span>{RECOMMENDATION_LABELS[value]}</span>;', filename: OFILE },
    { code: 'const x = <span>Override recommendation</span>;', filename: OFILE },
  ],
  invalid: [
    { code: 'const x = <span>Decline-Recommend</span>;', filename: OFILE, errors: 1 },
    { code: "const x = 'Override';", filename: OFILE, errors: 1 }, // the bare CommitAction label
  ],
});

ruleTester.run('advisory-vocabulary (reused UNMODIFIED for overrideForm / ADVISORY-1)', shellRules['advisory-vocabulary'], {
  valid: [
    { code: 'const x = <span>Your override and reason will be recorded</span>;', filename: OFILE },
    { code: 'const x = <span>Recommendation from the rules engine</span>;', filename: OFILE },
  ],
  invalid: [
    { code: 'const x = <span>records your decision</span>;', filename: OFILE, errors: 1 },
    { code: "const x = 'the application was declined';", filename: OFILE, errors: 1 },
  ],
});

ruleTester.run('override-testid-convention (TESTID-1)', overrideRules['override-testid-convention'], {
  valid: [
    { code: 'const x = <div data-testid="override-confirm-dialog" />;', filename: OFILE },
    { code: 'const x = <div data-testid="override-confirm-reason-echo" />;', filename: OFILE },
    { code: 'const x = <div data-testid={testid} />;', filename: OFILE },
  ],
  invalid: [
    { code: 'const x = <div data-testid="approval-gate" />;', filename: OFILE, errors: 1 },
    { code: 'const x = <div data-testid="override-form" />;', filename: OFILE, errors: 1 }, // two-segment: too short
    { code: 'const x = <div data-testid="overrideForm" />;', filename: OFILE, errors: 1 },
  ],
});

describe('ADVISORY-1 — the OVERRIDE_COPY is advisory-clean (consumed verbatim, no re-draft)', () => {
  it('reuses the single FORBIDDEN_TERMS source object (no second word-list)', () => {
    expect(LINT_FORBIDDEN_TERMS).toBe(FORBIDDEN_TERMS);
  });
  it('no OVERRIDE_COPY string contains a forbidden system-output token', () => {
    const forbidden = /\bdecision\b|\bapproved\b|\bdeclined\b|decline(?!-?recommend)/i;
    const strings = Object.values(OVERRIDE_COPY);
    expect(strings.length).toBeGreaterThan(0); // non-vacuous
    strings.forEach((s) => expect(forbidden.test(s)).toBe(false));
  });
});

describe('detector self-tests (non-vacuous)', () => {
  it('isValidOverrideTestid enforces the override-<element>-<purpose> (>=3 segment) convention', () => {
    expect(isValidOverrideTestid('override-state-loading')).toBe(true);
    expect(isValidOverrideTestid('override-confirm-reason-echo')).toBe(true);
    expect(isValidOverrideTestid('override-form')).toBe(false); // two-segment too short
    expect(isValidOverrideTestid('approval-gate')).toBe(false);
    expect(isValidOverrideTestid('overrideForm')).toBe(false);
  });
});
