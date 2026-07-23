import { describe, it, expect } from 'vitest';
import { slugSegment, outlierFlagTestid } from '../testids.js';
import { isValidOutlierTestid } from '../../../eslint-rules/outlierView.js';

// TESTID-1 (Q2-A) — the dynamic `outlier-flag-<feature>` id. The generated ids are TEMPLATE
// LITERALS, so the outlier-testid-convention lint (which inspects literal data-testid attributes
// only) cannot see them: this self-test IS the enforcement (CG-OUTV-Fold-3).
//
// The nine names below are the REAL U18 wire values, read from
// backend/outlier_model/feature_fields.py (OUTLIER_FEATURE_FIELDS) — mirrored BY VALUE, not
// imported (cross-language reference-not-own, BR-OUTV-10).
const REAL_U18_FEATURE_FIELDS = [
  'age_years_derived',
  'bmi_derived',
  'verifiable_income_annual',
  'existing_debt_obligations_annual',
  'requested_cover_amount',
  'dti_ratio',
  'income_multiple',
  'health_flag_count',
  'documents_missing_count',
];

describe('TESTID-1 — outlierFlagTestid satisfies the convention for EVERY real U18 feature name', () => {
  it.each(REAL_U18_FEATURE_FIELDS)('%s slugs to a convention-satisfying id', (feature) => {
    const testid = outlierFlagTestid(feature);
    expect(isValidOutlierTestid(testid)).toBe(true);
    expect(testid).not.toMatch(/_/);
  });

  it('produces the expected kebab ids (the snake_case -> kebab contract)', () => {
    expect(outlierFlagTestid('age_years_derived')).toBe('outlier-flag-age-years-derived');
    expect(outlierFlagTestid('dti_ratio')).toBe('outlier-flag-dti-ratio');
    expect(outlierFlagTestid('bmi_derived')).toBe('outlier-flag-bmi-derived');
  });

  it('all nine ids are unique (no slug collision)', () => {
    const ids = REAL_U18_FEATURE_FIELDS.map(outlierFlagTestid);
    expect(new Set(ids).size).toBe(ids.length);
  });

  // The teeth: prove a NAIVE (unslugged) interpolation would have violated the convention, so this
  // builder is load-bearing rather than decorative.
  it('a naive unslugged interpolation WOULD violate the convention (non-vacuous)', () => {
    expect(isValidOutlierTestid('outlier-flag-age_years_derived')).toBe(false);
    expect(isValidOutlierTestid('outlier-flag-dti_ratio')).toBe(false);
  });
});

describe('slugSegment — detector self-tests (non-vacuous)', () => {
  it('lower-cases, kebabs, and trims', () => {
    expect(slugSegment('INCOME_MIN')).toBe('income-min');
    expect(slugSegment('dti_ratio')).toBe('dti-ratio');
    expect(slugSegment('  Mixed Case  ')).toBe('mixed-case');
    expect(slugSegment('__leading_and_trailing__')).toBe('leading-and-trailing');
    expect(slugSegment('already-kebab')).toBe('already-kebab');
  });

  it('coerces non-string input safely', () => {
    expect(slugSegment(42)).toBe('42');
  });
});

describe('Q1-A — the outlier testid pattern is the `*` (memoView/approvalGate) family', () => {
  // The three TWO-SEGMENT ids from the frozen FD §6 inventory. Under the queue/history `+` family
  // these would be REJECTED; Q1-A adopts the `*` family so the FD inventory generates verbatim.
  it('accepts the frozen FD two-segment ids', () => {
    expect(isValidOutlierTestid('outlier-view')).toBe(true);
    expect(isValidOutlierTestid('outlier-score')).toBe(true);
    expect(isValidOutlierTestid('outlier-isoutlier')).toBe(true);
  });

  it('accepts the multi-segment inventory ids', () => {
    for (const id of [
      'outlier-region-score',
      'outlier-region-flags',
      'outlier-region-readonly',
      'outlier-state-loading',
      'outlier-state-notavailable',
      'outlier-state-error',
      'outlier-error-message',
      'outlier-error-code',
      'outlier-error-retry',
    ]) {
      expect(isValidOutlierTestid(id)).toBe(true);
    }
  });

  it('rejects foreign / malformed ids (non-vacuous)', () => {
    expect(isValidOutlierTestid('memo-view')).toBe(false);
    expect(isValidOutlierTestid('outlierView')).toBe(false);
    expect(isValidOutlierTestid('outlier_region')).toBe(false);
    expect(isValidOutlierTestid('outlier')).toBe(false);
    expect(isValidOutlierTestid('Outlier-View')).toBe(false);
    expect(isValidOutlierTestid(42)).toBe(false);
  });
});
