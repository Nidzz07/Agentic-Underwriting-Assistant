import { RoleGate } from '../../shell/components/RoleGate.jsx';
import { OVERRIDE_COPY } from '../copy.js';

// C6 — the override affordance (RoleGate composition, mirror of U7's ApproveAffordance). BY-CONSTRUCTION
// (P1 / P2 / header-comment self-evidence):
//   props { onOverride, disabled } only — no submitOverride/seam/onConfirm; opens the dialog, cannot
//   commit; disabled derived from the one reason predicate.
// Its prop set is { onOverride, disabled, testid } — it receives NO submitOverride, NO seam instance,
// NO onConfirm, NO transport — nothing that can issue a commit. Its onClick calls onOverride(), whose
// only effect (wired by OverrideFormView) is to OPEN the confirm dialog. A premature commit is
// therefore STRUCTURALLY UNWRITABLE here. `disabled` is DERIVED from OverrideFormView's single
// isReasonPresent predicate (P2) — never independently recomputed — so the affordance can never be
// enabled while the reason is blank.
//
// RoleGate can="act" is COSMETIC ONLY (defense-in-depth) — it hides the affordance from
// non-underwriters (auditor/admin/null) but makes NO authorization decision. AUTHZ-1 (audit-store's
// DecisionCommitService backend re-check) is the real gate; a 403 surfaces as a genuine error.
export function OverrideAffordance({ onOverride, disabled, testid = 'override-affordance-button' }) {
  return (
    <RoleGate can="act">
      <button type="button" data-testid={testid} onClick={onOverride} disabled={disabled}>
        {OVERRIDE_COPY.overrideLabel}
      </button>
    </RoleGate>
  );
}

export default OverrideAffordance;
