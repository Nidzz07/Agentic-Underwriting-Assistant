// submission/fetchSeam — the injected R10/R11 seam (WIRE1-Fold-6, register #2).
//
// Duck-typed, NO formal interface — the same discipline every other unit's seam uses. This module
// owns request-building + failure NORMALIZATION only; it makes NO real network call itself. The
// real transport is wired at the composition root (`src/app/seams.js`); tests inject a capturing
// double.
//
// ⚑ TWO OPERATIONS, ONE SEAM — because Q3(a) made submission two-phase. R10 creates the case and
// returns fast (LLM-free); R11 is the separate, explicit drafting trigger. They share a seam
// because they are one user-facing workflow, and splitting them would register two `seams.js`
// keys for one unit — which no other unit does.
//
// ⛔ `normalizeError` PRESERVES `detail`, and that is load-bearing rather than incidental. WIRE-1
// §4's `detail` is where intake's `reason_category` / `field_errors` / `missing_items` travel, and
// a normalizer that flattened it to a message would reduce every rejection to "something was
// wrong" — discarding precisely the structured rejection that choosing Q8(a) bought.

// Build the WIRE-1 R10 request. `documents` is ALWAYS present and ALWAYS `[]` under Fold-6.
export function buildSubmitRequest(formFields, documents = []) {
  return {
    method: 'POST',
    path: '/applications',
    body: { form_fields: formFields, documents },
  };
}

// Build the WIRE-1 R11 request. No body — the application id is the whole input.
export function buildDraftRequest(applicationId) {
  return {
    method: 'POST',
    path: `/applications/${encodeURIComponent(applicationId)}/draft`,
  };
}

// Normalize ANY failure to a well-formed error envelope { error: { code, message, detail } } so no
// state view ever has to unpack a raw exception. A parsed non-2xx body that is already a
// well-formed envelope passes through UNCHANGED, detail included.
export function normalizeError(cause) {
  if (
    cause && typeof cause === 'object' &&
    cause.error && typeof cause.error === 'object' &&
    typeof cause.error.code === 'string' && typeof cause.error.message === 'string'
  ) {
    const { code, message, detail } = cause.error;
    return { error: { code, message, detail: detail ?? {} } };
  }
  return { error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} } };
}

async function send(transport, request) {
  let response;
  try {
    response = await transport(request);
  } catch (cause) {
    throw normalizeError(cause);
  }
  if (response && response.ok) {
    return response.body;
  }
  throw normalizeError(response && response.body);
}

/**
 * createSubmissionFetch(transport) -> { submit, triggerDraft }
 *
 * `transport(request)` is INJECTED — a capturing double in tests, the real HTTP transport at the
 * composition root. It resolves `{ ok, body }` and may throw on a transport failure.
 *
 *   submit(formFields, documents = [])  -> resolves { application_id, status } (R10)
 *   triggerDraft(applicationId)         -> resolves { application_id, status, outcome } (R11)
 *
 * Both REJECT with a well-formed `{ error: { code, message, detail } }` envelope — never a raw
 * exception, and never with `detail` stripped.
 */
export function createSubmissionFetch(transport) {
  return {
    submit: (formFields, documents = []) =>
      send(transport, buildSubmitRequest(formFields, documents)),
    triggerDraft: (applicationId) => send(transport, buildDraftRequest(applicationId)),
  };
}

export default createSubmissionFetch;
