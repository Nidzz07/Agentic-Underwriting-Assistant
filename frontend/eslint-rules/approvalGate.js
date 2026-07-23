// Custom ESLint rule(s) for ui-approval-gate (U7, Q1-A). Frontend-wide build infra — NOT a
// src/shell, src/queue, or src/memoView file. ui-approval-gate REUSES ui-shell's no-inline-label /
// advisory-vocabulary (the ONE FORBIDDEN_TERMS, no new word-list); this file adds ONLY the approval
// testid convention, mirroring eslint-rules/memoView.js and leaving eslint-rules/index.js untouched.
//
//   approval-testid-convention -> TESTID-1: a literal data-testid follows approval-<element>-<purpose>
//     (incl. approval-gate, approval-state-*, approval-error-*, approval-affordance-approve,
//      approval-confirm-*, approval-committed-*, approval-recommendation, approval-confidence).

// TESTID-1 detector: the approval-<element>[-<purpose>...] naming convention.
export const APPROVAL_TESTID_PATTERN = /^approval-[a-z0-9]+(-[a-z0-9]+)*$/;
export function isValidApprovalTestid(value) {
  return typeof value === 'string' && APPROVAL_TESTID_PATTERN.test(value);
}

export const rules = {
  'approval-testid-convention': {
    meta: {
      type: 'problem',
      docs: { description: 'A literal data-testid in ui-approval-gate must follow the approval-<element>-<purpose> convention (TESTID-1).' },
      schema: [],
    },
    create(context) {
      return {
        JSXAttribute(node) {
          if (!node.name || node.name.name !== 'data-testid') return;
          const v = node.value;
          if (v && v.type === 'Literal' && typeof v.value === 'string' && !isValidApprovalTestid(v.value)) {
            context.report({ node, message: `data-testid "${v.value}" violates the approval-<element>-<purpose> convention (TESTID-1).` });
          }
        },
      };
    },
  },
};

export default rules;
