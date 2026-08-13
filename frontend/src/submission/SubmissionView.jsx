import { useCallback, useMemo, useState } from 'react';
import { Panel } from '../shell/components/Panel.jsx';
import { SubmissionForm } from './components/SubmissionForm.jsx';
import { RejectionSummary } from './components/RejectionSummary.jsx';
import { AcceptedPanel } from './components/AcceptedPanel.jsx';
import { DocumentInputs } from './components/DocumentInputs.jsx';
import { OptionalFields } from './components/OptionalFields.jsx';
import { DOC_TYPES, OPTIONAL_FIELDS, REQUIRED_FIELDS, SUBMISSION_COPY } from './copy.js';

// C1 — the unit's ONLY stateful component, mirroring QueueView's shape. `submissionSeam` is
// INJECTED as a prop; this module makes no network call of its own and reads NO Role
// (RoleInvariant — the server is the real gate; `require_underwriter` returns 403 and this unit
// renders that like any other error).
//
// TWO state machines, because Q3(a) made the flow two-phase:
//   form  -> submitting -> accepted | rejected | error        (R10)
//   accepted: idle -> drafting -> drafted | error             (R11)
//
// ⚑ THE REJECTED STATE IS NOT AN ERROR STATE, and keeping them apart is the substance of Q8(a).
// A 400 from intake carries `detail.field_errors` / `missing_items` / `reason_category` — enough
// to mark the exact inputs at fault. Every other failure (401/403/network) carries nothing
// actionable and renders as a generic error. Collapsing the two would throw away the structured
// rejection that choosing Q8(a) bought, and would tell a user "something went wrong" when the
// server had just told us precisely what.

// ⚑ Required AND optional in one values map — but `isValid` below reads ONLY the required
// tuple, which is what keeps an optional field from becoming mandatory by accident (Q10).
const EMPTY_VALUES = Object.freeze(
  Object.fromEntries([...REQUIRED_FIELDS, ...OPTIONAL_FIELDS].map((field) => [field, ''])),
);

const NO_DOCUMENTS = Object.freeze(Object.fromEntries(DOC_TYPES.map((d) => [d, null])));

// The wire shape intake expects: blank optionals are OMITTED rather than sent as empty strings
// (the gate reads `in (None, "")` for absence, but sending nothing is the honest encoding), and
// `health_flags` is a LIST, not a string.
export function toFormFields(values) {
  const out = {};
  for (const field of REQUIRED_FIELDS) out[field] = values[field];
  for (const field of OPTIONAL_FIELDS) {
    const raw = String(values[field] ?? '').trim();
    if (raw === '') continue;
    out[field] = field === 'health_flags' ? [raw] : raw;
  }
  return out;
}

// The server's manifest -> the per-document status the user sees (Q7).
export function toDocumentStatuses(entries, selected) {
  const statuses = {};
  for (const docType of DOC_TYPES) {
    if (selected[docType]) statuses[docType] = 'selected';
  }
  for (const entry of entries ?? []) {
    if (entry && DOC_TYPES.includes(entry.doc_type)) {
      statuses[entry.doc_type] =
        entry.status === 'parsed' ? 'parsed'
          : entry.status === 'unparseable' ? 'unparseable'
            : statuses[entry.doc_type];
    }
  }
  return statuses;
}

// A plain `{ field: message }` map from WIRE-1 §4's `detail.field_errors`. Defensive about shape
// because it crosses the wire: a malformed entry must not take the whole view down.
export function toFieldErrorMap(detail) {
  const entries = (detail && detail.field_errors) || [];
  const map = {};
  for (const entry of entries) {
    if (entry && typeof entry.field === 'string') {
      map[entry.field] = entry.message || SUBMISSION_COPY.unknownErrorMessage;
    }
  }
  return map;
}

export function SubmissionView({ submissionSeam, onSubmitted, testid = 'submission-view' }) {
  const [values, setValues] = useState(EMPTY_VALUES);
  const [state, setState] = useState('form');
  const [rejection, setRejection] = useState(null);
  const [error, setError] = useState(null);
  const [accepted, setAccepted] = useState(null);
  const [draftState, setDraftState] = useState('idle');
  const [draftOutcome, setDraftOutcome] = useState(null);
  const [files, setFiles] = useState(NO_DOCUMENTS);
  const [docStatuses, setDocStatuses] = useState({});

  // ⚑ Whitespace-only counts as empty — the same discipline BR-COMMIT-GATE applies to an
  // override reason. Without it the affordance would enable on "   " and the user would learn
  // their mistake from a server round-trip instead of from the button.
  const isValid = useMemo(
    () => REQUIRED_FIELDS.every((field) => String(values[field] ?? '').trim() !== ''),
    [values],
  );

  const fieldErrors = useMemo(
    () => (rejection ? toFieldErrorMap(rejection) : {}),
    [rejection],
  );

  const onChange = useCallback((field, value) => {
    setValues((current) => ({ ...current, [field]: value }));
  }, []);

  const onSelectDocument = useCallback((docType, file) => {
    setFiles((current) => ({ ...current, [docType]: file }));
    setDocStatuses((current) => ({ ...current, [docType]: file ? 'selected' : undefined }));
  }, []);

  const onSubmit = useCallback(async () => {
    if (!isValid) return;
    setState('submitting');
    setRejection(null);
    setError(null);
    setDocStatuses((current) => {
      const next = { ...current };
      for (const docType of DOC_TYPES) if (files[docType]) next[docType] = 'uploading';
      return next;
    });
    try {
      const body = await submissionSeam.submit(toFormFields(values), files);
      // ⛔ Q7: the per-document outcome comes from the SERVER's manifest, never assumed. A
      // document that failed to parse still lets the application through, so silently showing
      // "uploaded" would hide the one thing the applicant could act on.
      setDocStatuses(toDocumentStatuses(body.documents, files));
      setAccepted(body);
      setState('accepted');
      if (onSubmitted) onSubmitted(body.application_id);
    } catch (envelope) {
      // envelope is always a well-formed { error: {...} } — the seam guarantees it.
      setDocStatuses(toDocumentStatuses(null, files));   // back to 'selected'
      if (envelope.error.code === 'payload_too_large') {
        setError(envelope);
        setState('form');            // ⚑ recoverable: choose a smaller file and resubmit
      } else if (envelope.error.code === 'invalid_request') {
        setRejection(envelope.error.detail || {});
        setState('form');           // ⚑ back to the FORM, values intact, errors attached
      } else {
        setError(envelope);
        setState('error');
      }
    }
  }, [files, isValid, onSubmitted, submissionSeam, values]);

  const onDraft = useCallback(async () => {
    setDraftState('drafting');
    setError(null);
    try {
      const body = await submissionSeam.triggerDraft(accepted.application_id);
      setDraftOutcome(body.outcome);
      setDraftState('drafted');
    } catch (envelope) {
      setError(envelope);
      setDraftState('idle');        // ⚑ recoverable: the trigger stays available
    }
  }, [accepted, submissionSeam]);

  const onStartOver = useCallback(() => {
    setValues(EMPTY_VALUES);
    setFiles(NO_DOCUMENTS);
    setDocStatuses({});
    setAccepted(null);
    setRejection(null);
    setError(null);
    setDraftOutcome(null);
    setDraftState('idle');
    setState('form');
  }, []);

  return (
    <Panel testid={testid}>
      <h2>{SUBMISSION_COPY.title}</h2>

      {state === 'submitting' ? (
        <p data-testid="submission-submitting" aria-busy="true">
          {SUBMISSION_COPY.submittingLabel}
        </p>
      ) : null}

      {rejection ? <RejectionSummary detail={rejection} /> : null}

      {error ? (
        <div data-testid="submission-error" role="alert">
          <p data-testid="submission-error-code">{error.error.code}</p>
          <p>{error.error.message || SUBMISSION_COPY.unknownErrorMessage}</p>
        </div>
      ) : null}

      {state === 'accepted' && accepted ? (
        <AcceptedPanel
          result={accepted}
          documentStatuses={docStatuses}
          draftState={draftState}
          draftOutcome={draftOutcome}
          onDraft={onDraft}
          onStartOver={onStartOver}
        />
      ) : (
        <>
          <SubmissionForm
            values={values}
            fieldErrors={fieldErrors}
            onChange={onChange}
            disabled={state === 'submitting'}
          />
          <p>{SUBMISSION_COPY.amountHint}</p>
          <DocumentInputs
            files={files}
            statuses={docStatuses}
            onSelect={onSelectDocument}
            disabled={state === 'submitting'}
          />
          <OptionalFields
            values={values}
            onChange={onChange}
            disabled={state === 'submitting'}
          />
          <p data-testid="submission-latency-hint">{SUBMISSION_COPY.uploadLatencyHint}</p>
          <button
            type="button"
            data-testid="submission-submit"
            disabled={!isValid || state === 'submitting'}
            onClick={onSubmit}
          >
            {SUBMISSION_COPY.submitLabel}
          </button>
        </>
      )}
    </Panel>
  );
}

export default SubmissionView;
