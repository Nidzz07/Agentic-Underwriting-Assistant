// ui-outlier-view dynamic-testid builder (Q2-A realization; the frozen history/testids.js precedent).
//
// The outlier-<element>-<purpose> convention (regex ^outlier-[a-z0-9]+(-[a-z0-9]+)*$, Q1-A) requires
// lower-case, kebab-safe segments — but the interpolated segment of `outlier-flag-<feature>` comes
// from the WIRE-1 R4 `flagged_features[].feature` string, whose real U18 values are snake_case
// (`age_years_derived`, `dti_ratio`, ...). A naive template literal would emit
// `outlier-flag-age_years_derived`, whose underscores VIOLATE the convention.
//
// The generated ids are template literals, so the outlier-testid-convention lint (which inspects
// LITERAL data-testid attributes only) cannot see them — `slugSegment` + its self-test over all NINE
// real U18 feature names are the ONLY possible enforcement here (CG-OUTV-Fold-3).
//
// CG-OUTV-Fold-3: the SLUG is the identifier; the RAW wire string is what the row DISPLAYS (Q3-A,
// faithful-renderer BR-OUTV-6). The asymmetry is intentional — do not collapse one into the other.

export function slugSegment(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// One flagged-feature row (BR-OUTV-8); `feature` is the R4 wire value.
export function outlierFlagTestid(feature) {
  return `outlier-flag-${slugSegment(feature)}`;
}
