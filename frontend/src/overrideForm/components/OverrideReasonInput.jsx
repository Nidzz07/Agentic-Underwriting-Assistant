import { ReadOnlyRegion } from '../../shell/components/ReadOnlyRegion.jsx';
import { OVERRIDE_COPY } from '../copy.js';

// C5 — the mandatory-reason input (the NEW capability-free component U7 had no analog for).
// BY-CONSTRUCTION (P9 / CAPFREE-1 / header-comment self-evidence):
//   controlled textarea, { value, onChange } only, no seam reference, holds text not a commit capability.
// Its props are { value, onChange, testid } ONLY — it holds NO reference to `submitOverride`, the
// override seam, or `onConfirm`. Holding the reason *text* is NOT a commit capability (the refined
// invariant: capability = holding the trigger/seam, not the payload). It displays `value` and reports
// edits via `onChange`; it belongs to ready(idle) and is NOT rendered during `confirming` (the reason
// is frozen there — ND-OVR-Fold-i), which keeps P2's belt-and-suspenders re-check optional.
export function OverrideReasonInput({ value, onChange, testid = 'override-reason-input' }) {
  return (
    <div>
      <label htmlFor="override-reason-field">{OVERRIDE_COPY.reasonPromptLabel}</label>
      <textarea
        id="override-reason-field"
        data-testid={testid}
        aria-label={OVERRIDE_COPY.reasonPromptLabel}
        placeholder={OVERRIDE_COPY.reasonPlaceholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      <ReadOnlyRegion testid="override-reason-hint">{OVERRIDE_COPY.reasonRequiredHint}</ReadOnlyRegion>
    </div>
  );
}

export default OverrideReasonInput;
