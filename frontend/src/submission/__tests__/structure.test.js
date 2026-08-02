// Step 4.5 — the STRUCTURAL half of the completeness bar, mirroring every other unit's
// import-scan tests (`noRouterImport`, `noBackendImport`, `capabilityFree.imports`).
//
// These read the unit's own source and assert what it does NOT reach for. Behavioural tests can
// only show that something did not happen in the cases they exercise; these show it cannot.
import { describe, it, expect } from 'vitest';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { SUBMISSION_TESTID_PATTERN } from '../../../eslint-rules/submission.js';
import { fieldErrorTestid, fieldInputTestid, missingItemTestid, slugSegment } from '../testids.js';

const UNIT_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

function sourceFiles(dir = UNIT_ROOT) {
  return readdirSync(dir).flatMap((entry) => {
    const path = join(dir, entry);
    if (statSync(path).isDirectory()) {
      return entry === '__tests__' ? [] : sourceFiles(path);
    }
    return /\.jsx?$/.test(entry) ? [path] : [];
  });
}

const SOURCES = sourceFiles().map((path) => [path, readFileSync(path, 'utf8')]);

describe('the unit reaches for nothing it should not', () => {
  it('scans a non-empty set of source files', () => {
    expect(SOURCES.length).toBeGreaterThan(0);   // never vacuously empty
  });

  it('imports NO router — selection state belongs to the composition root (Decision 6)', () => {
    for (const [path, code] of SOURCES) {
      expect(code, path).not.toMatch(/from\s+['"]react-router/);
    }
  });

  it('imports NO other UI unit — one unit, one concern', () => {
    // ⚑ The shell is the ONE permitted dependency: it is the shared design system every unit
    // composes. Reaching into queue/ or memoView/ would couple two units that must stay
    // independently replaceable.
    for (const [path, code] of SOURCES) {
      for (const unit of ['queue', 'memoView', 'approvalGate', 'overrideForm', 'history',
                          'outlierView', 'login', 'app']) {
        expect(code, `${path} imports ${unit}`).not.toMatch(
          new RegExp(`from\\s+['"]\\.\\./${unit}/`),
        );
      }
    }
  });

  it('reads NO Role and composes NO RoleGate — the server is the real gate', () => {
    // ⚑ RoleInvariant. `require_underwriter` returns 403 and this unit renders it like any other
    // error. Gating the form client-side would duplicate an authorization decision the server
    // already owns, and would diverge from it the moment the role model changed.
    for (const [path, code] of SOURCES) {
      expect(code, path).not.toMatch(/RoleGate|useCurrentRole|RoleContext/);
    }
  });

  it('calls NO fetch of its own — the seam is injected', () => {
    for (const [path, code] of SOURCES) {
      expect(code, path).not.toMatch(/\bfetch\s*\(|XMLHttpRequest|axios/);
    }
  });

  it('⛔ never hardcodes the two route paths outside the seam', () => {
    // The seam owns request-building. A path literal in a component would be a second place the
    // wire surface is written down — the drift risk `_route_inventory.py` exists to remove on
    // the server side.
    for (const [path, code] of SOURCES) {
      if (path.endsWith('fetchSeam.js')) continue;
      expect(code, path).not.toMatch(/['"`]\/applications/);
    }
  });
});

describe('every literal testid follows the submission convention', () => {
  it('matches the eslint rule the lint block enforces', () => {
    // ⚑ Belt and braces with the lint: the lint fails the BUILD, this fails the SUITE. The
    // history unit does the same, because a lint can be disabled by a config edit that a test
    // run would not notice.
    for (const [path, code] of SOURCES) {
      for (const match of code.matchAll(/data-testid="([^"]+)"/g)) {
        expect(SUBMISSION_TESTID_PATTERN.test(match[1]), `${path}: ${match[1]}`).toBe(true);
      }
    }
  });

  it('the BUILT ids satisfy the convention too, for snake_case field names', () => {
    // ⛔ The builders are the enforcement for interpolated ids, which the lint cannot see — and
    // their inputs come from the SERVER (`detail.field_errors[].field`), so they are exactly the
    // ids most likely to carry an unexpected shape.
    for (const field of ['date_of_birth', 'verifiable_income_annual', 'full_name']) {
      expect(SUBMISSION_TESTID_PATTERN.test(fieldInputTestid(field))).toBe(true);
      expect(SUBMISSION_TESTID_PATTERN.test(fieldErrorTestid(field))).toBe(true);
      expect(SUBMISSION_TESTID_PATTERN.test(missingItemTestid(field))).toBe(true);
    }
  });

  it('slugSegment normalizes the shapes a backend field name can take', () => {
    expect(slugSegment('date_of_birth')).toBe('date-of-birth');
    expect(slugSegment('INCOME_MIN')).toBe('income-min');
    expect(slugSegment('__weird__')).toBe('weird');
  });
});
