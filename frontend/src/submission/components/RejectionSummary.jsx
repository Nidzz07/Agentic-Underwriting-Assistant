import { SUBMISSION_COPY } from '../copy.js';
import { missingItemTestid } from '../testids.js';

// PRESENTATIONAL. Renders the parts of a WIRE-1 §4 `detail` that are NOT per-field: the reason
// category and the `missing_items` list.
//
// ⚑ WHY BOTH THIS AND THE PER-FIELD MESSAGES. `field_errors` and `missing_items` overlap but are
// not the same: a required value absent produces both, while a field intake could not map to any
// input at all appears ONLY in `missing_items`. Rendering only the per-field half would silently
// swallow that second case — the user would see a rejection with nothing marked.
//
// ⚑ The reason category is TRANSLATED, not echoed. `missing_required` is intake's vocabulary, not
// a sentence; showing the raw slug would leak an internal enum into the UI.
export function RejectionSummary({ detail }) {
  const reason =
    SUBMISSION_COPY.rejectionReasonLabels[detail.reason_category] ??
    SUBMISSION_COPY.rejectionFallbackReason;
  const missing = detail.missing_items ?? [];

  return (
    <div data-testid="submission-rejection" role="alert">
      <h3>{SUBMISSION_COPY.rejectionHeading}</h3>
      <p data-testid="submission-rejection-reason">{reason}</p>
      {missing.length > 0 ? (
        <div data-testid="submission-missing">
          <h4>{SUBMISSION_COPY.missingItemsHeading}</h4>
          <ul>
            {missing.map((item) => (
              <li key={item} data-testid={missingItemTestid(item)}>{item}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

export default RejectionSummary;
