// ⛔ The non-quality-gated provider notice (live-llm-drafting Q9 / G2, option D).
//
// ⚑ WHY THIS UNIT NEEDED A UI CHANGE AT ALL, recorded because the cheaper option was rejected.
// Q9 required the marking be visible "not just via the existing honest model_version stamp".
// Embedding a marker in the stamp alone would have satisfied "marked" but not "visibly" — a reader
// would have to know to decode a provenance string. This renders it.
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { MemoView } from '../MemoView.jsx';
import { MEMO_COPY } from '../copy.js';
import { isNotQualityGated } from '../components/ProviderGateNotice.jsx';
import { makeMemoView } from './fixtures.js';

const OLLAMA_STAMP = 'NOT-QUALITY-GATED+llama3.1:8b-instruct-q4_K_M+abcdef012345+ollama-python-0.6.2';
const OFFLINE_STAMP = 'OFFLINE-DOUBLE-NOT-A-REAL-LLM';

function renderMemo(modelVersion) {
  const view = makeMemoView({ memo: { model_version: modelVersion } });
  const seam = async () => view;
  render(<MemoView memoFetchSeam={seam} applicationId="app-1" />);
}

describe('isNotQualityGated', () => {
  it('is true only for a stamp LEADING with the marker', () => {
    expect(isNotQualityGated(OLLAMA_STAMP)).toBe(true);
  });

  it('is false for the offline double and for a real gated provider', () => {
    // ⚑ The non-vacuity partner. Without it the predicate could simply return true.
    expect(isNotQualityGated(OFFLINE_STAMP)).toBe(false);
    expect(isNotQualityGated('gemini-2.5-flash+google-genai-1.0.0')).toBe(false);
  });

  it('does not fire on a stamp that merely CONTAINS the marker later in the string', () => {
    // ⛔ A substring match would let a model literally named "...NOT-QUALITY-GATED..." or a future
    // stamp reordering trigger it for the wrong reason.
    expect(isNotQualityGated('llama+NOT-QUALITY-GATED+x')).toBe(false);
  });

  it('tolerates a missing or non-string model_version', () => {
    expect(isNotQualityGated(undefined)).toBe(false);
    expect(isNotQualityGated(null)).toBe(false);
    expect(isNotQualityGated(42)).toBe(false);
  });
});

describe('the notice in a rendered memo', () => {
  it('is ABSENT for the offline double', async () => {
    renderMemo(OFFLINE_STAMP);
    // ⚑ Wait for READY first. Without this the absence assertion would pass while the memo was
    // still LOADING — an accidental pass for the wrong reason.
    expect(await screen.findByTestId('memo-region-readonly')).toBeTruthy();
    expect(screen.queryByTestId('memo-provider-gate-notice')).toBeNull();
  });

  it('is PRESENT, with the stamp, for the showcase provider', async () => {
    renderMemo(OLLAMA_STAMP);
    expect(await screen.findByTestId('memo-provider-gate-notice')).toBeTruthy();
    expect(screen.getByTestId('memo-provider-gate-stamp').textContent).toBe(OLLAMA_STAMP);
  });

  it('⛔ does NOT say the memo is wrong, untrusted, or unreliable', async () => {
    // The exemption is scoped to memo-QUALITY gates. The decision-level gates all still hold and
    // the recommendation is engine-authored, so copy implying the memo is defective would be a
    // FALSE statement rendered to an underwriter — a worse outcome than not marking it at all.
    renderMemo(OLLAMA_STAMP);
    const text = (await screen.findByTestId('memo-provider-gate-notice')).textContent.toLowerCase();
    for (const forbidden of ['wrong', 'untrusted', 'unreliable', 'inaccurate', 'do not trust']) {
      expect(text).not.toContain(forbidden);
    }
  });

  it('names what WAS still checked, not only what was not', async () => {
    // ⚑ The half that keeps the notice honest in the other direction.
    renderMemo(OLLAMA_STAMP);
    const text = (await screen.findByTestId('memo-provider-gate-notice')).textContent;
    expect(text).toContain('rules engine');
    expect(MEMO_COPY.providerGateNoticeBody).toContain('bias');
  });
});
