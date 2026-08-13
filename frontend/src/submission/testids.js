// submission dynamic-testid builders. The submission-<element>-<purpose> convention
// (regex ^submission-[a-z0-9]+(-[a-z0-9]+)*$) requires lower-case, kebab-safe segments — but the
// interpolated segments come from INTAKE FIELD NAMES (`date_of_birth`, `verifiable_income_annual`)
// which are snake_case. These builders slug the dynamic segment so every generated id satisfies
// the convention.
//
// ⚑ The generated ids are template literals, so the submission-testid-convention lint (which
// inspects literal data-testid attributes only) does not see them — `slugSegment` and its
// self-test are the enforcement here. The same arrangement ui-history uses.
//
// ⛔ THE FIELD-ERROR BUILDER IS THE LOAD-BEARING ONE. Its input is a field name that arrives from
// the SERVER, inside `detail.field_errors[].field`. Slugging is what stops an unexpected value
// producing an id that silently fails the convention, and what lets a test address the error for
// a specific field rather than scraping text.

export function slugSegment(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// One form input, keyed by the intake field name it collects.
export function fieldInputTestid(field) {
  return `submission-input-${slugSegment(field)}`;
}

// The per-field rejection message rendered beside that input — `detail.field_errors[].field`.
export function fieldErrorTestid(field) {
  return `submission-fielderror-${slugSegment(field)}`;
}

// One entry in `detail.missing_items`.
export function missingItemTestid(item) {
  return `submission-missing-${slugSegment(item)}`;
}

// One document file input, keyed by its `DocType` value.
export function documentInputTestid(docType) {
  return `submission-doc-${slugSegment(docType)}`;
}

// The visible per-document status — ⛔ Q7 requires this be addressable, not merely rendered.
export function documentStatusTestid(docType) {
  return `submission-docstatus-${slugSegment(docType)}`;
}
