import { SUBMISSION_COPY } from '../copy.js';

// PRESENTATIONAL — the two-phase flow's visible seam (Q3(a)).
//
// ⛔ IT SAYS THE CASE IS NOT YET ASSESSED, AND THAT IS THE POINT. Submission is LLM-free and stops
// at `evaluated`; R4 reports that case as `pending`. A panel that read "submitted successfully"
// and stopped would let a user assume assessment had happened. The drafting trigger below is the
// second, explicit action Q3(a) chose over a background task precisely so the transition is
// visible and attributable rather than fire-and-forget.
export function AcceptedPanel({ result, draftState, draftOutcome, onDraft, onStartOver }) {
  return (
    <div data-testid="submission-accepted">
      <h3>{SUBMISSION_COPY.acceptedHeading}</h3>
      <p>
        {SUBMISSION_COPY.acceptedIdLabel}
        {': '}
        <span data-testid="submission-accepted-id">{result.application_id}</span>
      </p>

      {draftState === 'idle' ? (
        <>
          <p data-testid="submission-accepted-pending">
            {SUBMISSION_COPY.acceptedPendingMessage}
          </p>
          <button type="button" data-testid="submission-draft" onClick={onDraft}>
            {SUBMISSION_COPY.draftLabel}
          </button>
        </>
      ) : null}

      {draftState === 'drafting' ? (
        <p data-testid="submission-drafting" aria-busy="true">
          {SUBMISSION_COPY.draftingLabel}
        </p>
      ) : null}

      {draftState === 'drafted' ? (
        <p data-testid="submission-draft-outcome">
          {draftOutcome === 'skipped'
            ? SUBMISSION_COPY.skippedMessage
            : SUBMISSION_COPY.draftedMessage}
        </p>
      ) : null}

      <button type="button" data-testid="submission-startover" onClick={onStartOver}>
        {SUBMISSION_COPY.startOverLabel}
      </button>
    </div>
  );
}

export default AcceptedPanel;
