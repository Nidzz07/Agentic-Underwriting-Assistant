// ⛔ The non-quality-gated provider notice (live-llm-drafting Q9 / G2, option D).
//
// ⚑ IT READS AN EXISTING FIELD. `memo.model_version` is already carried on R4 by WIRE-1 §5's
// DecisionMemo shape, so this notice needs NO contract change and NO new wire field — which is
// exactly why option D was preferred over adding one (that would have been a fifth WIRE-1 Fold).
//
// ⛔ WHAT THIS NOTICE MUST NEVER SAY. The exemption is scoped to memo QUALITY gates
// (groundedness / the >=4/5 promptfoo rubric). Every DECISION-LEVEL gate holds for this provider
// identically — temperature=0, CON-BR2-TYPE (the model cannot represent a recommendation change),
// bias-swap, reproducibility — and the recommendation itself comes from the deterministic rules
// engine with no LLM involvement at all. So the copy states what was NOT checked; it must not
// imply the memo is wrong, untrusted, or that the recommendation is affected.
//
// LINT-SUBJECT: carries no advisory-vocabulary and no value equal to a shell display label.
import { MEMO_COPY } from '../copy.js';

// The marker the composition root leads the stamp with (backend: dependencies.NOT_QUALITY_GATED_MARKER).
export const NOT_QUALITY_GATED_MARKER = 'NOT-QUALITY-GATED';

export function isNotQualityGated(modelVersion) {
  return typeof modelVersion === 'string' && modelVersion.startsWith(NOT_QUALITY_GATED_MARKER);
}

export function ProviderGateNotice({ modelVersion }) {
  if (!isNotQualityGated(modelVersion)) return null;
  return (
    <div data-testid="memo-provider-gate-notice" role="note">
      <strong>{MEMO_COPY.providerGateNoticeHeading}</strong>
      <p>{MEMO_COPY.providerGateNoticeBody}</p>
      <span data-testid="memo-provider-gate-stamp">{modelVersion}</span>
    </div>
  );
}

export default ProviderGateNotice;
