// Custom ESLint rule(s) for ui-override-form (U8, Q1-A). Frontend-wide build infra — NOT a
// src/shell, src/queue, src/memoView, or src/approvalGate file. ui-override-form REUSES ui-shell's
// no-inline-label / advisory-vocabulary lints (the ONE FORBIDDEN_TERMS, no new word-list); this file
// adds ONLY the override testid convention, mirroring eslint-rules/approvalGate.js and leaving
// eslint-rules/index.js untouched.
//
//   override-testid-convention -> TESTID-1: a literal data-testid follows override-<element>-<purpose>
//     (incl. override-form-view, override-form-panel, override-state-*, override-error-*,
//      override-affordance-button, override-reason-input, override-reason-hint, override-confirm-*,
//      override-committed-*, override-recommendation-*, override-confidence-value).
//
// NOTE the `+` (one-or-more) tail: the override convention requires the full
// override-<element>-<purpose> shape (>=3 segments), so a bare two-segment testid is rejected. This
// mirrors the ui-queue testid regex, not the two-segment ui-memo-view/ui-approval-gate form.

// TESTID-1 detector: the override-<element>-<purpose> naming convention.
export const OVERRIDE_TESTID_PATTERN = /^override-[a-z]+(-[a-z0-9]+)+$/;
export function isValidOverrideTestid(value) {
  return typeof value === 'string' && OVERRIDE_TESTID_PATTERN.test(value);
}

export const rules = {
  'override-testid-convention': {
    meta: {
      type: 'problem',
      docs: { description: 'A literal data-testid in ui-override-form must follow the override-<element>-<purpose> convention (TESTID-1).' },
      schema: [],
    },
    create(context) {
      return {
        JSXAttribute(node) {
          if (!node.name || node.name.name !== 'data-testid') return;
          const v = node.value;
          if (v && v.type === 'Literal' && typeof v.value === 'string' && !isValidOverrideTestid(v.value)) {
            context.report({ node, message: `data-testid "${v.value}" violates the override-<element>-<purpose> convention (TESTID-1).` });
          }
        },
      };
    },
  },
};

export default rules;
