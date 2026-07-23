import { MEMO_COPY } from '../copy.js';

// C4 — a MINIMAL identifying context header (Q2-A): application_id, applicant name, derived age, and
// requested cover. Read-only, no affordance. `demographics` is display-only here (never a rule/feature
// input) so CON-BR1 is unaffected. Field labels come from the memo-local copy (never inlined).
export function ProfileContextHeader({ profile }) {
  if (!profile) return null;
  return (
    <header data-testid="memo-header-context">
      <span data-testid="memo-header-application">{profile.application_id}</span>
      <span>{MEMO_COPY.headers.applicant}: {profile.demographics?.full_name}</span>
      <span>{MEMO_COPY.headers.age}: {profile.age_years_derived}</span>
      <span>{MEMO_COPY.headers.requestedCover}: {profile.requested_cover_amount}</span>
    </header>
  );
}

export default ProfileContextHeader;
