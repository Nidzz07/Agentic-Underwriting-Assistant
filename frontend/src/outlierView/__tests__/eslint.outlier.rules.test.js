import { RuleTester } from 'eslint';
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import shellRules, { LINT_FORBIDDEN_TERMS } from '../../../eslint-rules/index.js';
import outlierRules, { isValidOutlierTestid } from '../../../eslint-rules/outlierView.js';
import { FORBIDDEN_TERMS } from '../../shell/copy/forbiddenTerms.js';

// NFR-OUTV-ADVISORY-1 + COPY-1 (reused shell lints — the ONE FORBIDDEN_TERMS, no new word-list)
// + TESTID-1 (outlier-<element>-<purpose>, Q1-A). Each proven NON-VACUOUS via RuleTester invalid
// fixtures + a detector self-test. The lints assert STATIC view source only — never runtime R4 data.
RuleTester.describe = describe;
RuleTester.it = it;
RuleTester.itOnly = it.only;

const ruleTester = new RuleTester({
  languageOptions: { ecmaVersion: 'latest', sourceType: 'module', parserOptions: { ecmaFeatures: { jsx: true } } },
});

const OFILE = 'src/outlierView/components/Sample.jsx';

ruleTester.run('no-inline-label (reused for outlierView / COPY-1)', shellRules['no-inline-label'], {
  valid: [
    { code: 'const x = <span>{FLAG_DIRECTION_LABELS[flag.direction]}</span>;', filename: OFILE },
    { code: 'const x = <span>Above the typical range</span>;', filename: OFILE },
    { code: 'const x = <span>Anomaly score</span>;', filename: OFILE },
  ],
  invalid: [
    { code: 'const x = <span>Decline-Recommend</span>;', filename: OFILE, errors: 1 },
    // The CG-OUTV-Fold-4 trap, proven live: a bare "High" IS a CONFIDENCE_LABELS value.
    { code: "const x = 'High';", filename: OFILE, errors: 1 },
  ],
});

ruleTester.run('advisory-vocabulary (reused for outlierView / ADVISORY-1)', shellRules['advisory-vocabulary'], {
  valid: [
    { code: 'const x = <span>Advisory statistical signal for underwriter review.</span>;', filename: OFILE },
    { code: 'const x = <span>Statistical outlier analysis</span>;', filename: OFILE },
    { code: 'const x = <span>No anomalous features were flagged for this applicant.</span>;', filename: OFILE },
  ],
  invalid: [
    { code: 'const x = <span>the final decision</span>;', filename: OFILE, errors: 1 },
    { code: "const x = 'the application was approved';", filename: OFILE, errors: 1 },
    { code: "const x = 'DECLINE';", filename: OFILE, errors: 1 },
  ],
});

ruleTester.run('outlier-testid-convention (TESTID-1)', outlierRules['outlier-testid-convention'], {
  valid: [
    { code: 'const x = <div data-testid="outlier-region-score" />;', filename: OFILE },
    { code: 'const x = <div data-testid="outlier-view" />;', filename: OFILE },
    { code: 'const x = <div data-testid="outlier-isoutlier" />;', filename: OFILE },
    { code: 'const x = <div data-testid={testid} />;', filename: OFILE },
    { code: 'const x = <li data-testid={outlierFlagTestid(flag.feature)} />;', filename: OFILE },
  ],
  invalid: [
    { code: 'const x = <div data-testid="memo-view" />;', filename: OFILE, errors: 1 },
    { code: 'const x = <div data-testid="outlierView" />;', filename: OFILE, errors: 1 },
    { code: 'const x = <div data-testid="outlier_region" />;', filename: OFILE, errors: 1 },
  ],
});

describe('ADVISORY-1 — the ONE FORBIDDEN_TERMS source is reused, not re-declared', () => {
  it('the lint and shell/copy share a single source object (structural, ===)', () => {
    expect(LINT_FORBIDDEN_TERMS).toBe(FORBIDDEN_TERMS);
  });

  it('ui-outlier-view declares no word-list of its own', () => {
    const copySrc = readFileSync(
      path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'copy.js'),
      'utf8',
    );
    expect(copySrc).not.toMatch(/FORBIDDEN_TERMS\s*=/);
    expect(copySrc).not.toMatch(/systemOutput\s*:/);
  });
});

describe('detector self-test (non-vacuous)', () => {
  it('isValidOutlierTestid enforces outlier-<element>-<purpose>', () => {
    expect(isValidOutlierTestid('outlier-state-loading')).toBe(true);
    expect(isValidOutlierTestid('outlier-view')).toBe(true);
    expect(isValidOutlierTestid('memo-view')).toBe(false);
    expect(isValidOutlierTestid('outlier')).toBe(false);
  });
});
