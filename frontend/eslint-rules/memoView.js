// Custom ESLint rule(s) for ui-memo-view (U6, Q6-A). Frontend-wide build infra — NOT a src/shell or
// src/queue file. ui-memo-view REUSES ui-shell's no-inline-label / advisory-vocabulary (the ONE
// FORBIDDEN_TERMS, no new word-list); this file adds ONLY the memo testid convention, mirroring
// eslint-rules/queue.js and leaving eslint-rules/index.js untouched.
//
//   memo-testid-convention -> TESTID-1 (BR-MEMO-10): a literal data-testid follows memo-<element>-<purpose>
//     (incl. the region-level testids memo-region-*, memo-recommendation, memo-confidence, memo-view).

// TESTID-1 detector: the memo-<element>[-<purpose>...] naming convention. Accepts single-purpose root
// / badge testids in the documented inventory (memo-view, memo-recommendation, memo-confidence) as
// well as multi-segment region testids (memo-region-readonly, memo-state-loading, ...).
export const MEMO_TESTID_PATTERN = /^memo-[a-z0-9]+(-[a-z0-9]+)*$/;
export function isValidMemoTestid(value) {
  return typeof value === 'string' && MEMO_TESTID_PATTERN.test(value);
}

export const rules = {
  'memo-testid-convention': {
    meta: {
      type: 'problem',
      docs: { description: 'A literal data-testid in ui-memo-view must follow the memo-<element>-<purpose> convention (TESTID-1, BR-MEMO-10).' },
      schema: [],
    },
    create(context) {
      return {
        JSXAttribute(node) {
          if (!node.name || node.name.name !== 'data-testid') return;
          const v = node.value;
          if (v && v.type === 'Literal' && typeof v.value === 'string' && !isValidMemoTestid(v.value)) {
            context.report({ node, message: `data-testid "${v.value}" violates the memo-<element>-<purpose> convention (TESTID-1).` });
          }
        },
      };
    },
  },
};

export default rules;
