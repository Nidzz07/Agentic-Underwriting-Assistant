import { RuleTester } from 'eslint';
import { describe, it, expect } from 'vitest';
import shellRules from '../../../eslint-rules/index.js';
import approvalRules, { isValidApprovalTestid } from '../../../eslint-rules/approvalGate.js';

// COPY-1 + ADVISORY-1 (reused shell lints — the ONE FORBIDDEN_TERMS, no new word-list; the
// advisory-vocabulary lint UNMODIFIED, NFR-AG-Fold-2) + TESTID-1 (approval-<element>-<purpose>).
// Each proven NON-VACUOUS via RuleTester invalid fixtures + a detector self-test.
RuleTester.describe = describe;
RuleTester.it = it;
RuleTester.itOnly = it.only;

const ruleTester = new RuleTester({
  languageOptions: { ecmaVersion: 'latest', sourceType: 'module', parserOptions: { ecmaFeatures: { jsx: true } } },
});

const AFILE = 'src/approvalGate/components/Sample.jsx';

ruleTester.run('no-inline-label (reused for approvalGate / COPY-1)', shellRules['no-inline-label'], {
  valid: [
    { code: 'const x = <span>{RECOMMENDATION_LABELS[value]}</span>;', filename: AFILE },
    { code: 'const x = <span>Approve recommendation</span>;', filename: AFILE },
  ],
  invalid: [
    { code: 'const x = <span>Decline-Recommend</span>;', filename: AFILE, errors: 1 },
    { code: "const x = 'Override';", filename: AFILE, errors: 1 },
  ],
});

ruleTester.run('advisory-vocabulary (reused UNMODIFIED for approvalGate / ADVISORY-1)', shellRules['advisory-vocabulary'], {
  valid: [
    { code: 'const x = <span>Your approval will be recorded</span>;', filename: AFILE },
    { code: 'const x = <span>Recommendation from the rules engine</span>;', filename: AFILE },
  ],
  invalid: [
    { code: 'const x = <span>records your decision</span>;', filename: AFILE, errors: 1 },
    { code: "const x = 'the application was approved';", filename: AFILE, errors: 1 },
  ],
});

ruleTester.run('approval-testid-convention (TESTID-1)', approvalRules['approval-testid-convention'], {
  valid: [
    { code: 'const x = <div data-testid="approval-confirm-dialog" />;', filename: AFILE },
    { code: 'const x = <div data-testid="approval-gate" />;', filename: AFILE },
    { code: 'const x = <div data-testid={testid} />;', filename: AFILE },
  ],
  invalid: [
    { code: 'const x = <div data-testid="memo-view" />;', filename: AFILE, errors: 1 },
    { code: 'const x = <div data-testid="approvalGate" />;', filename: AFILE, errors: 1 },
    { code: 'const x = <div data-testid="approval_confirm" />;', filename: AFILE, errors: 1 },
  ],
});

describe('detector self-tests (non-vacuous)', () => {
  it('isValidApprovalTestid enforces approval-<element>-<purpose>', () => {
    expect(isValidApprovalTestid('approval-state-loading')).toBe(true);
    expect(isValidApprovalTestid('approval-gate')).toBe(true);
    expect(isValidApprovalTestid('memo-view')).toBe(false);
    expect(isValidApprovalTestid('approvalGate')).toBe(false);
    expect(isValidApprovalTestid('approval')).toBe(false);
  });
});
