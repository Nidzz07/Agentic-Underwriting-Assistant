import { RoleGate } from '../../shell/components/RoleGate.jsx';
import { APPROVAL_COPY } from '../copy.js';

// C5 — the approve affordance (first REAL RoleGate composition). BY-CONSTRUCTION (Q2-A / ND-Fold-1):
//   props are { onApprove } ONLY (+ the cosmetic `testid`). This component holds NO reference to
//   `submitApprove`, the commit seam, or `onConfirm` — nothing that can issue a commit. Its onClick
//   calls onApprove(), whose only effect (wired by ApprovalGateView) is to OPEN the confirm dialog. A
//   premature commit is therefore STRUCTURALLY UNWRITABLE here (not merely discouraged by convention);
//   adding one would require adding a new prop, an obvious reviewable change.
//
// RoleGate can="act" is COSMETIC ONLY (defense-in-depth) — it hides the affordance from
// non-underwriters (auditor/admin/null) but makes NO authorization decision. AUTHZ-1 (audit-store's
// DecisionCommitService backend re-check) is the real gate; a 403 surfaces as a genuine error.
export function ApproveAffordance({ onApprove, testid = 'approval-affordance-approve' }) {
  return (
    <RoleGate can="act">
      <button type="button" data-testid={testid} onClick={onApprove}>
        {APPROVAL_COPY.approveLabel}
      </button>
    </RoleGate>
  );
}

export default ApproveAffordance;
