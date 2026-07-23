// Custom ESLint rule(s) for ui-history (U9, Q1-A). Frontend-wide build infra — NOT a src/shell,
// src/queue, src/memoView, src/approvalGate or src/overrideForm file. ui-history REUSES ui-shell's
// no-inline-label / advisory-vocabulary (the ONE FORBIDDEN_TERMS, no new word-list); this file adds
// ONLY the history testid convention, mirroring eslint-rules/queue.js and leaving
// eslint-rules/index.js untouched.
//
//   history-testid-convention -> TESTID-1 (BR-HIST-10): a literal data-testid follows
//     history-<element>-<purpose> (the queue-family form, D11).
//
// Note (CG-HIST-Fold-1): the four 2-segment ROOT ids of the FD inventory (history-view, history-list,
// history-detail, history-pagination) are testid-PROP DEFAULTS rendered as `data-testid={testid}` — a
// JSX expression, not a Literal — so this rule never evaluates them, exactly as ui-queue's rule never
// evaluates `queue-view`/`queue-pagination`. The convention below governs the LITERAL ids only.

// TESTID-1 detector: the history-<element>-<purpose> naming convention (queue-family).
export const HISTORY_TESTID_PATTERN = /^history-[a-z]+(-[a-z0-9]+)+$/;
export function isValidHistoryTestid(value) {
  return typeof value === 'string' && HISTORY_TESTID_PATTERN.test(value);
}

export const rules = {
  'history-testid-convention': {
    meta: {
      type: 'problem',
      docs: { description: 'A literal data-testid in ui-history must follow the history-<element>-<purpose> convention (TESTID-1, BR-HIST-10).' },
      schema: [],
    },
    create(context) {
      return {
        JSXAttribute(node) {
          if (!node.name || node.name.name !== 'data-testid') return;
          const v = node.value;
          if (v && v.type === 'Literal' && typeof v.value === 'string' && !isValidHistoryTestid(v.value)) {
            context.report({ node, message: `data-testid "${v.value}" violates the history-<element>-<purpose> convention (TESTID-1).` });
          }
        },
      };
    },
  },
};

export default rules;
