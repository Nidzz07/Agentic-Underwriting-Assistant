import { HISTORY_COPY } from '../copy.js';

// C11 — the read-only ApplicantProfileSnapshot: the verbatim persisted ORIGINAL INPUT plus its
// tamper-evidence hash. Presentational, strictly read-only — no edit affordance, no mutation seam
// (FAITHFUL-1). The field subset is the Code-Gen realization the FD deferred; it mirrors the frozen
// ui-memo-view ProfileContextHeader's identifying subset (application id, applicant, derived age,
// requested cover) plus the verifiable income the rules keyed on.
//
// `demographics` is DISPLAYED FORENSIC INPUT, never a scored feature (CON-BR1 is unaffected — the
// segregation is upstream, in intake/rules-engine; showing what was persisted is the auditor's whole
// purpose here, so this is not a bias-swap concern).
//
// CG-HIST-Fold-4: `content_hash` is rendered by C9 under `history-detail-content-hash` (the FD §6
// forensic grouping); here the same value is the SNAPSHOT's own tamper-evidence marker, so it carries
// its own distinct id — both frozen prop shapes are honored without a duplicate testid.
export function ProfileSnapshotRegion({ profile, applicationId, contentHash, testid = 'history-detail-profile' }) {
  return (
    <section data-testid={testid} aria-label={HISTORY_COPY.profileSnapshotHeading}>
      <h3>{HISTORY_COPY.profileSnapshotHeading}</h3>
      <p>
        <span>{HISTORY_COPY.profile.application}</span>
        <span data-testid="history-detail-profile-application">{applicationId}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.profile.applicant}</span>
        <span data-testid="history-detail-profile-applicant">{profile.demographics.full_name}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.profile.age}</span>
        <span data-testid="history-detail-profile-age">{profile.age_years_derived}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.profile.income}</span>
        <span data-testid="history-detail-profile-income">{profile.verifiable_income_annual}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.profile.requestedCover}</span>
        <span data-testid="history-detail-profile-cover">{profile.requested_cover_amount}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.profile.snapshotHash}</span>
        <span data-testid="history-detail-profile-hash">{contentHash}</span>
      </p>
    </section>
  );
}

export default ProfileSnapshotRegion;
