// Custom ESLint rule(s) for ui-queue (U5, Q6-A). Frontend-wide build infra — NOT a src/shell file.
// ui-queue REUSES ui-shell's no-inline-label / advisory-vocabulary (the ONE FORBIDDEN_TERMS, no new
// word-list); this file adds ONLY the queue testid convention, leaving eslint-rules/index.js untouched.
//
//   queue-testid-convention -> TESTID-1 (BR-QUEUE-8): a literal data-testid follows queue-<element>-<purpose>

// TESTID-1 detector: the queue-<element>-<purpose> naming convention (analogous to shell's).
export const QUEUE_TESTID_PATTERN = /^queue-[a-z]+(-[a-z0-9]+)+$/;
export function isValidQueueTestid(value) {
  return typeof value === 'string' && QUEUE_TESTID_PATTERN.test(value);
}

export const rules = {
  'queue-testid-convention': {
    meta: {
      type: 'problem',
      docs: { description: 'A literal data-testid in ui-queue must follow the queue-<element>-<purpose> convention (TESTID-1, BR-QUEUE-8).' },
      schema: [],
    },
    create(context) {
      return {
        JSXAttribute(node) {
          if (!node.name || node.name.name !== 'data-testid') return;
          const v = node.value;
          if (v && v.type === 'Literal' && typeof v.value === 'string' && !isValidQueueTestid(v.value)) {
            context.report({ node, message: `data-testid "${v.value}" violates the queue-<element>-<purpose> convention (TESTID-1).` });
          }
        },
      };
    },
  },
};

export default rules;
