// Step 4.1 — the R10/R11 seam. Mirrors every other unit's seam test: a CAPTURING transport
// double, no network, no server.
import { describe, it, expect } from 'vitest';
import {
  buildDraftRequest,
  buildSubmitRequest,
  createSubmissionFetch,
  normalizeError,
} from '../fetchSeam.js';

const FIELDS = { full_name: 'Ada Byron', verifiable_income_annual: '1200000' };

function capturing(responses) {
  const calls = [];
  const queue = [...responses];
  return {
    calls,
    transport: async (request) => {
      calls.push(request);
      const next = queue.shift();
      if (next instanceof Error) throw next.cause ?? next;
      return next;
    },
  };
}

describe('buildSubmitRequest — R10', () => {
  it('is a POST to /applications carrying form_fields and documents', () => {
    expect(buildSubmitRequest(FIELDS)).toEqual({
      method: 'POST',
      path: '/applications',
      body: { form_fields: FIELDS, documents: [] },
    });
  });

  it('sends documents as an EXPLICIT empty array, never omitted', () => {
    // ⚑ Q2(a)'s follow-up on the client side: the key is present so the wire shape is already
    // correct when upload lands. Omitting it would leave the server defaulting on the client's
    // behalf, and the day documents arrive nothing here would need to change but silently would.
    expect(buildSubmitRequest(FIELDS).body).toHaveProperty('documents');
    expect(buildSubmitRequest(FIELDS).body.documents).toEqual([]);
  });
});

describe('buildDraftRequest — R11', () => {
  it('is a POST to the application draft path with no body', () => {
    expect(buildDraftRequest('APP-7')).toEqual({
      method: 'POST',
      path: '/applications/APP-7/draft',
    });
  });

  it('encodes the application id into the path', () => {
    // Ids are server-assigned (`APP-<hex>`), but encoding is what stops a stray character
    // producing a malformed path rather than a 404.
    expect(buildDraftRequest('APP/7').path).toBe('/applications/APP%2F7/draft');
  });
});

describe('normalizeError — the envelope every state view can rely on', () => {
  it('passes a well-formed WIRE-1 envelope through, DETAIL INTACT', () => {
    // ⛔ THE LOAD-BEARING ONE for step 4.3. `detail` carries `field_errors` / `missing_items` /
    // `reason_category`, and a normalizer that dropped it would silently reduce every rejection
    // to a generic message — which is exactly what choosing Q8(a) was meant to avoid.
    const envelope = {
      error: {
        code: 'invalid_request',
        message: 'The application did not pass intake validation.',
        detail: {
          reason_category: 'missing_required',
          field_errors: [{ field: 'date_of_birth', code: 'missing', message: 'required value absent' }],
          missing_items: ['date_of_birth'],
        },
      },
    };
    expect(normalizeError(envelope)).toEqual(envelope);
  });

  it('synthesizes a network_error envelope for anything malformed', () => {
    expect(normalizeError(undefined)).toEqual({
      error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} },
    });
  });
});

describe('createSubmissionFetch', () => {
  it('resolves the created application id on a 200', async () => {
    const { transport, calls } = capturing([
      { ok: true, body: { application_id: 'APP-1', status: 'pending' } },
    ]);
    const seam = createSubmissionFetch(transport);

    await expect(seam.submit(FIELDS)).resolves.toEqual({
      application_id: 'APP-1',
      status: 'pending',
    });
    expect(calls[0].method).toBe('POST');
  });

  it('REJECTS with the rejection envelope, field errors preserved', async () => {
    const detail = {
      reason_category: 'missing_required',
      field_errors: [{ field: 'city', code: 'missing', message: 'required value absent' }],
      missing_items: ['city'],
    };
    const { transport } = capturing([
      { ok: false, body: { error: { code: 'invalid_request', message: 'no', detail } } },
    ]);
    const seam = createSubmissionFetch(transport);

    await expect(seam.submit(FIELDS)).rejects.toMatchObject({
      error: { code: 'invalid_request', detail },
    });
  });

  it('triggerDraft resolves the drafting outcome', async () => {
    const { transport, calls } = capturing([
      { ok: true, body: { application_id: 'APP-1', status: 'ready', outcome: 'drafted' } },
    ]);
    const seam = createSubmissionFetch(transport);

    await expect(seam.triggerDraft('APP-1')).resolves.toMatchObject({ outcome: 'drafted' });
    expect(calls[0].path).toBe('/applications/APP-1/draft');
  });

  it('a thrown transport failure becomes an envelope, never a raw exception', async () => {
    const boom = new Error('down');
    const { transport } = capturing([Object.assign(new Error('x'), { cause: boom })]);
    const seam = createSubmissionFetch(transport);

    await expect(seam.triggerDraft('APP-1')).rejects.toMatchObject({
      error: { code: 'network_error' },
    });
  });

  it('exposes exactly the two operations the two routes need', () => {
    // ⚑ An exact-key assertion, mirroring `createSeams`'s own. A third operation appearing here
    // would mean a third route arrived without a contract amendment.
    expect(Object.keys(createSubmissionFetch(async () => ({ ok: true, body: {} }))).sort())
      .toEqual(['submit', 'triggerDraft']);
  });
});
