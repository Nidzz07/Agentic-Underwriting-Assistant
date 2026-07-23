import { RuleTester } from 'eslint';
import { describe, it, expect } from 'vitest';
import shellRules from '../../../eslint-rules/index.js';
import queueRules, { isValidQueueTestid } from '../../../eslint-rules/queue.js';

// COPY-1 (reused shell no-inline-label — the ONE FORBIDDEN_TERMS, no new word-list) + TESTID-1
// (queue-<element>-<purpose>). Each proven NON-VACUOUS via RuleTester invalid fixtures + a detector self-test.
RuleTester.describe = describe;
RuleTester.it = it;
RuleTester.itOnly = it.only;

const ruleTester = new RuleTester({
  languageOptions: { ecmaVersion: 'latest', sourceType: 'module', parserOptions: { ecmaFeatures: { jsx: true } } },
});

const QFILE = 'src/queue/components/Sample.jsx';

ruleTester.run('no-inline-label (reused for queue / COPY-1)', shellRules['no-inline-label'], {
  valid: [
    { code: 'const x = <span>{RECOMMENDATION_LABELS[value]}</span>;', filename: QFILE },
    { code: 'const x = <span>Queue</span>;', filename: QFILE },
  ],
  invalid: [
    { code: 'const x = <span>Decline-Recommend</span>;', filename: QFILE, errors: 1 },
    { code: "const x = 'Refer';", filename: QFILE, errors: 1 },
  ],
});

ruleTester.run('queue-testid-convention (TESTID-1)', queueRules['queue-testid-convention'], {
  valid: [
    { code: 'const x = <div data-testid="queue-state-loading" />;', filename: QFILE },
    { code: 'const x = <div data-testid={testid} />;', filename: QFILE },
    { code: 'const x = <div data-testid={`queue-row-${id}`} />;', filename: QFILE },
  ],
  invalid: [
    { code: 'const x = <div data-testid="shell-panel-queue" />;', filename: QFILE, errors: 1 },
    { code: 'const x = <div data-testid="queuePanel" />;', filename: QFILE, errors: 1 },
    { code: 'const x = <div data-testid="queue_state" />;', filename: QFILE, errors: 1 },
  ],
});

describe('detector self-tests (non-vacuous)', () => {
  it('isValidQueueTestid enforces queue-<element>-<purpose>', () => {
    expect(isValidQueueTestid('queue-state-loading')).toBe(true);
    expect(isValidQueueTestid('queue-pagination-prev')).toBe(true);
    expect(isValidQueueTestid('shell-panel-queue')).toBe(false);
    expect(isValidQueueTestid('queuePanel')).toBe(false);
    expect(isValidQueueTestid('queue')).toBe(false);
  });
});
