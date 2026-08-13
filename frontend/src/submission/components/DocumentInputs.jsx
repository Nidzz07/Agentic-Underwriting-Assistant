import { DOC_TYPES, SUBMISSION_COPY } from '../copy.js';
import { documentInputTestid, documentStatusTestid } from '../testids.js';

// PRESENTATIONAL — one file input per `DocType`, each with its own VISIBLE status.
//
// ⛔ Q7, verbatim: per-document status must be *"visible to the user, not silently downgraded"*.
// A document that fails to read still lets the application through, but it changes the
// assessment — `DOCS-COMPLETE-1` counts only documents that parsed — so an applicant who is
// never told which file failed cannot fix it. Rendering one aggregate "uploaded" for all three
// would be exactly the silent downgrade Q7 forbids.
//
// ⚑ `statuses` is a `{ docType: 'selected' | 'uploading' | 'parsed' | 'unparseable' }` map the
// parent derived from the server's manifest.
export function DocumentInputs({ files, statuses, onSelect, disabled }) {
  return (
    <div data-testid="submission-documents">
      <h3>{SUBMISSION_COPY.documentsHeading}</h3>
      <p>{SUBMISSION_COPY.documentsHint}</p>
      {DOC_TYPES.map((docType) => {
        const inputId = documentInputTestid(docType);
        const status = statuses[docType];
        return (
          <div key={docType}>
            <label htmlFor={inputId}>{SUBMISSION_COPY.documentLabels[docType]}</label>
            <input
              id={inputId}
              data-testid={inputId}
              type="file"
              accept="application/pdf"
              disabled={disabled}
              onChange={(event) => onSelect(docType, event.target.files[0] ?? null)}
            />
            {status ? (
              <p data-testid={documentStatusTestid(docType)}>
                {SUBMISSION_COPY.documentStatusLabels[status]}
              </p>
            ) : null}
            {files[docType] ? (
              <button
                type="button"
                data-testid={`${inputId}-remove`}
                disabled={disabled}
                onClick={() => onSelect(docType, null)}
              >
                {SUBMISSION_COPY.removeDocumentLabel}
              </button>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

export default DocumentInputs;
