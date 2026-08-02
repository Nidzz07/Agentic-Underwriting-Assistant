// Shared test fixtures for the submission unit.
//
// ⚑ A PLAIN MODULE, NOT A TEST FILE — mirroring `overrideForm/__tests__/fixtures.js`. Importing
// helpers from a `*.test.jsx` would re-execute that file's `describe` blocks in every importer,
// silently running the same assertions several times and inflating the suite count. Found by
// running: the count came back 43 where 33 was expected.
import { vi } from 'vitest';
import { fireEvent, screen } from '@testing-library/react';
import { fieldInputTestid } from '../testids.js';

// A structurally complete application — every value the frozen `IntakeGate` requires.
// ⛔ Money is a decimal STRING, never a JSON float (intake's BR-TYP-1).
export const VALID = Object.freeze({
  full_name: 'Ada Byron',
  city: 'Metropolis',
  gender: 'female',
  date_of_birth: '1986-03-14',
  as_of_date: '2026-01-01',
  verifiable_income_annual: '1200000',
  requested_cover_amount: '4000000',
});

export function fillValid() {
  for (const [field, value] of Object.entries(VALID)) {
    fireEvent.change(screen.getByTestId(fieldInputTestid(field)), { target: { value } });
  }
}

export function stubSeam(over = {}) {
  return {
    submit: vi.fn(async () => ({ application_id: 'APP-1', status: 'pending' })),
    triggerDraft: vi.fn(async () => ({
      application_id: 'APP-1', status: 'ready', outcome: 'drafted',
    })),
    ...over,
  };
}
