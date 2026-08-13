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

// Build the WIRE-1 R10 request.
//
// ⚑ TWO ENCODINGS, and the JSON one is UNCHANGED (WIRE1-Fold-7 / Constraint 4). A submission
// carrying NO documents stays plain JSON exactly as Fold-6 pinned it — an application with no
// attachments has no reason to pay multipart's cost, and ~15 backend tests plus the shipped
// frontend depend on that path being untouched.
//
// ⛔ With documents it becomes `multipart/form-data`: one `form_fields` part carrying the SAME
// JSON object, plus one file part per `DocType`. The transport sets no Content-Type, so the
// browser supplies the boundary.
export function buildSubmitRequest(formFields, documents = {}) {
  const attached = Object.entries(documents).filter(([, file]) => file);
  if (attached.length === 0) {
    return {
      method: 'POST',
      path: '/applications',
      body: { form_fields: formFields, documents: [] },
    };
  }
  const form = new FormData();
  form.append('form_fields', JSON.stringify(formFields));
  for (const [docType, file] of attached) {
    form.append(docType, file, file.name);
  }
  return { method: 'POST', path: '/applications', body: form };
}

// Build the WIRE-1 R11 request. No body — the application id is the whole input.
export function buildDraftRequest(applicationId) {
  return {
    method: 'POST',
    path: `/applications/${encodeURIComponent(applicationId)}/draft`,
  };
}

// Build the WIRE-1 R3 request — the applicant profile, and with it the DOCUMENT MANIFEST.
//
// ⛔ WHY THIS EXISTS, stated plainly because it corrects a shipped bug. R10's success body is
// `SubmissionAccepted` — `{ application_id, status }` and nothing else, byte-unchanged from
// Fold-6 through Fold-7 (WIRE-1 §5). It has NEVER carried a per-document manifest. The view read
// `body.documents` anyway, got `undefined`, and every attached document stayed on its optimistic
// `selected` label — "Ready to upload" — no matter what the server had actually parsed. Observed
// in the browser during §9's manual walkthrough.
//
// ⚑ R3 already serves the manifest and needs NO contract change: it returns
// `intake.schema.ApplicantProfile` verbatim, whose `documents` is a `DocumentManifest`
// — `{ expected_count, satisfied_count, entries: [{ doc_type, status, content_hash }] }`. That is
// the very field §9 read out of `profile_canonical` with psql. A GET is also the honest place for
// it: the manifest is state to be read, not a side effect of submitting.
export function buildProfileRequest(applicationId) {
  return {
    method: 'GET',
    path: `/applications/${encodeURIComponent(applicationId)}`,
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
 *   submit(formFields, documents = {})  -> resolves { application_id, status } (R10)
 *       `documents` is a { docTypeValue: File } map; empty -> JSON, non-empty -> multipart
 *       ⛔ TWO KEYS. No manifest — see `buildProfileRequest`; use `fetchProfile` for that.
 *   triggerDraft(applicationId)         -> resolves { application_id, status, outcome } (R11)
 *   fetchProfile(applicationId)         -> resolves ApplicantProfile, incl. `documents` (R3)
 *
 * Both REJECT with a well-formed `{ error: { code, message, detail } }` envelope — never a raw
 * exception, and never with `detail` stripped.
 */
export function createSubmissionFetch(transport) {
  return {
    submit: (formFields, documents = {}) =>
      send(transport, buildSubmitRequest(formFields, documents)),
    triggerDraft: (applicationId) => send(transport, buildDraftRequest(applicationId)),
    fetchProfile: (applicationId) => send(transport, buildProfileRequest(applicationId)),
  };
}

export default createSubmissionFetch;
