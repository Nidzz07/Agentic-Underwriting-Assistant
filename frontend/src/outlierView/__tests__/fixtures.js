// Q4-A — the four R4 body builders + a failing transport, mirroring the frozen
// memoView/history __tests__/fixtures.js precedent. The three outlier fixtures are the
// NFR-Requirements Fold-C / D-OUTV-2 pin; makeFailingTransport backs the STATE-1 failure teeth.
//
// The `pending`-null and `ready`-null bodies are deliberately TWO NAMED builders rather than one
// parameterized factory: the load-bearing "field-derived, not status-derived" distinction stays
// greppable at every call site (Q4-A rationale).

// Q5-A — the D-OUTV-4 / Fold-D sentinel pin, VERBATIM (no Code-Gen drift). Chosen so they cannot
// overlap any legitimately-rendered value (a score, a z_score, a feature name, a testid), making the
// PROV-1 "sentinel absent" assertion sound in BOTH directions.
export const SENTINEL_SEED = 987654321;
export const SENTINEL_CORPUS_VERSION = 'SENTINEL-CORPUS-DO-NOT-RENDER';
export const SENTINEL_MODEL_VERSION = 'SENTINEL-MODEL-DO-NOT-RENDER';

export function makeProvenance() {
  return {
    corpus_version: SENTINEL_CORPUS_VERSION,
    seed: SENTINEL_SEED,
    outlier_model_version: SENTINEL_MODEL_VERSION,
  };
}

// Fixture 1a — a `pending` body: the pipeline has not produced a memo, so `outlier` is null.
export function makePendingBody(applicationId = 'app-1') {
  return {
    application_id: applicationId,
    recommendation_id: null,
    status: 'pending',
    profile: null,
    report: null,
    memo: null,
    outlier: null,
  };
}

// Fixture 1b — a Phase-1 `ready` body that STILL carries `outlier: null` (WIRE1-Fold-4 binding
// semantics). THE field-derived teeth: a status-keyed implementation would render READY here and
// crash/mis-render; a field-derived one renders NOT_AVAILABLE.
export function makeReadyNullOutlierBody(applicationId = 'app-1') {
  return {
    application_id: applicationId,
    recommendation_id: 'rec-1',
    status: 'ready',
    profile: { applicant_name: 'Test Applicant' },
    report: { rule_results: [] },
    memo: { narrative_prose: 'Narrative text.' },
    outlier: null,
  };
}

// Fixture 2 — `outlier` PRESENT with an empty flagged_features list: a normal applicant. Analyzed,
// nothing anomalous (EMPTY-1) — a valid score, NOT a not-available state.
export function makeReadyEmptyFlagsBody(applicationId = 'app-1') {
  return {
    application_id: applicationId,
    recommendation_id: 'rec-1',
    status: 'ready',
    profile: { applicant_name: 'Test Applicant' },
    report: { rule_results: [] },
    memo: { narrative_prose: 'Narrative text.' },
    outlier: {
      outlier_score: 0.12,
      is_outlier: false,
      flagged_features: [],
      provenance: makeProvenance(),
    },
  };
}

// Fixture 3 — `outlier` PRESENT and populated. The flagged_features list is DELIBERATELY NOT SORTED
// (not by feature name, not by |z_score|, not by shap_value) so LISTORDER-1 has real teeth: any
// client-side re-sort would reorder it detectably.
export function makeReadyPopulatedBody(applicationId = 'app-1') {
  return {
    application_id: applicationId,
    recommendation_id: 'rec-1',
    status: 'ready',
    profile: { applicant_name: 'Test Applicant' },
    report: { rule_results: [] },
    memo: { narrative_prose: 'Narrative text.' },
    outlier: {
      outlier_score: 0.87,
      is_outlier: true,
      flagged_features: [
        { feature: 'dti_ratio', z_score: 2.9, shap_value: 0.41, direction: 'high' },
        { feature: 'age_years_derived', z_score: -3.4, shap_value: 0.52, direction: 'low' },
        { feature: 'verifiable_income_annual', z_score: 2.1, shap_value: 0.18, direction: 'low' },
      ],
      provenance: makeProvenance(),
    },
  };
}

// The delivered order of fixture 3 — asserted verbatim by LISTORDER-1.
export const POPULATED_FEATURE_ORDER = Object.freeze([
  'dti_ratio',
  'age_years_derived',
  'verifiable_income_annual',
]);

// A transport double that RESOLVES the given body. Captures every request (Fold-A / D-OUTV-1) so
// Retry can be asserted to re-fetch the SAME applicationId.
export function makeCapturingTransport(body) {
  const calls = [];
  const transport = async (request) => {
    calls.push(request);
    return { ok: true, body };
  };
  transport.calls = calls;
  return transport;
}

// A transport double that FAILS. `mode: 'envelope'` rejects with a well-formed WIRE-1 §4 envelope
// (a parsed non-2xx); `mode: 'throw'` throws a raw transport exception (normalized by fetchSeam).
export function makeFailingTransport(mode = 'envelope') {
  const calls = [];
  const transport = async (request) => {
    calls.push(request);
    if (mode === 'throw') throw new Error('socket hang up');
    return {
      ok: false,
      body: { error: { code: 'not_found', message: 'No such application.', detail: { hint: 'internal detail' } } },
    };
  };
  transport.calls = calls;
  return transport;
}
