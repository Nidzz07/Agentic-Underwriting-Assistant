import { describe, it, expect } from 'vitest';
import { isReasonPresent } from '../OverrideFormView.jsx';

// REASONGATE-1 (unit / documentation, FD-OVR-Fold-1) — the UI guard is String.prototype.trim()-based
// and NON-AUTHORITATIVE. It is NOT byte-identical to the backend's Python str.strip(): the C0
// separators U+001C–U+001F and NEL U+0085 are Python whitespace (str.strip removes them → the backend
// _gate rejects a reason of only those chars) but are NOT JS trim() whitespace (so the UI treats them
// as non-blank). This is a DOCUMENTED divergence, NOT a byte-equality claim — any such reason that
// slips past the UI is rejected server-side and surfaced generically (409 / BR-OVR-6). Inventing a
// custom Unicode matcher to force byte-equality is deliberately out of scope (over-build vs the
// non-authoritative design).

// Built via String.fromCharCode so NO literal control character appears in this source file.
const DIVERGENT_CHARS = [0x1c, 0x1d, 0x1e, 0x1f, 0x85].map((c) => String.fromCharCode(c));

describe('REASONGATE-1 — trim() vs str.strip() divergence (documented, non-authoritative)', () => {
  it('the guard is trim()-based: plain ASCII whitespace (and JS line terminators) are treated as blank', () => {
    for (const blank of ['', ' ', '\t', '\n', '\r', ' \t\n ']) {
      expect(isReasonPresent(blank)).toBe(false);
    }
    expect(isReasonPresent('x')).toBe(true);
  });

  it('U+001C–U+001F / U+0085 pass the JS trim() guard (non-blank) — the divergence from Python str.strip()', () => {
    for (const ch of DIVERGENT_CHARS) {
      // JS trim() does NOT strip these (they are Cc controls, not ECMAScript WhiteSpace/LineTerminator)
      // → the reason is unchanged and non-empty → the UI treats it as present.
      expect(ch.trim()).toBe(ch);
      expect(isReasonPresent(ch)).toBe(true);
      // (Python `ch.strip() == ''` → the backend _gate would reject; the backend is authoritative.)
    }
  });
});
