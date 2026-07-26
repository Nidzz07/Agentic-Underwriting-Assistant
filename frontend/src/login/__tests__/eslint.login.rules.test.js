import { RuleTester } from 'eslint';
import { describe, it, expect } from 'vitest';
import shellRules from '../../../eslint-rules/index.js';

// COPY-1 + ADVISORY-1 — the shell lints REUSED UNMODIFIED for the login unit. No new word-list
// and no new rule: the same ONE FORBIDDEN_TERMS source every other unit is held to. Proven
// non-vacuous by RuleTester invalid fixtures.
RuleTester.describe = describe;
RuleTester.it = it;
RuleTester.itOnly = it.only;

const ruleTester = new RuleTester({
  languageOptions: { ecmaVersion: 'latest', sourceType: 'module', parserOptions: { ecmaFeatures: { jsx: true } } },
});

const LFILE = 'src/login/components/Sample.jsx';

ruleTester.run('advisory-vocabulary (reused UNMODIFIED for login / ADVISORY-1)', shellRules['advisory-vocabulary'], {
  valid: [
    // ⚑ A sign-in failure is NOT an underwriting outcome. "failed" is fine; the verdict
    // vocabulary is reserved and must never leak into auth copy.
    { code: "const x = 'Sign in failed';", filename: LFILE },
    { code: "const x = 'Password';", filename: LFILE },
  ],
  invalid: [
    { code: "const x = 'Your sign-in was declined';", filename: LFILE, errors: 1 },
    { code: "const x = 'approved';", filename: LFILE, errors: 1 },
  ],
});

describe('the login unit reuses the shell FORBIDDEN_TERMS source, never a second word-list', () => {
  it('holds — and the lint rule the login unit is checked by is the shell rule object itself', () => {
    expect(shellRules['advisory-vocabulary']).toBeDefined();
    expect(shellRules['no-inline-label']).toBeDefined();
  });
});
