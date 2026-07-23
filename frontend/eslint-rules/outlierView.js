// Custom ESLint rule(s) for ui-outlier-view (U20, Q1-A). Frontend-wide build infra — NOT a file
// under any frozen unit's src/ tree. ui-outlier-view REUSES ui-shell's no-inline-label /
// advisory-vocabulary (the ONE FORBIDDEN_TERMS, no new word-list); this file adds ONLY the outlier
// testid convention, mirroring eslint-rules/memoView.js and leaving eslint-rules/index.js untouched.
//
//   outlier-testid-convention -> TESTID-1 (BR-OUTV-8): a literal data-testid follows
//     outlier-<element>-<purpose>.
//
// Q1-A: the `*` quantifier family (the frozen memoView/approvalGate precedent), NOT the `+` family
// (queue/history). The frozen FD §6 inventory contains three TWO-SEGMENT ids — `outlier-view`,
// `outlier-score`, `outlier-isoutlier` — which the `+` family would reject; the `*` family accepts
// them, so the approved FD inventory is realized VERBATIM with no artifact re-opened.
export const OUTLIER_TESTID_PATTERN = /^outlier-[a-z0-9]+(-[a-z0-9]+)*$/;
export function isValidOutlierTestid(value) {
  return typeof value === 'string' && OUTLIER_TESTID_PATTERN.test(value);
}

export const rules = {
  'outlier-testid-convention': {
    meta: {
      type: 'problem',
      docs: { description: 'A literal data-testid in ui-outlier-view must follow the outlier-<element>-<purpose> convention (TESTID-1, BR-OUTV-8).' },
      schema: [],
    },
    create(context) {
      return {
        JSXAttribute(node) {
          if (!node.name || node.name.name !== 'data-testid') return;
          const v = node.value;
          if (v && v.type === 'Literal' && typeof v.value === 'string' && !isValidOutlierTestid(v.value)) {
            context.report({ node, message: `data-testid "${v.value}" violates the outlier-<element>-<purpose> convention (TESTID-1).` });
          }
        },
      };
    },
  },
};

export default rules;
