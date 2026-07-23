// Shared test fixtures for ui-memo-view (Code-Gen Q4-A). Two intentional READY-memo fixtures + a
// pending view + an error envelope, reused across PENDING-1 / LISTORDER-1 / SEPARATION-1 / FETCH-1.
// `makeMemoView(overrides)` keeps the module EXTENSIBLE (a future variant = one override) so it does
// not become a dumping ground (ambiguity-check ii).

const BASE_PROFILE = {
  application_id: 'app-1',
  age_years_derived: 42,
  requested_cover_amount: '500000',
  demographics: { full_name: 'Jordan Rivera', gender: 'unspecified', city: 'Metropolis' },
};

const BASE_MEMO = {
  narrative_prose: 'The applicant meets the income threshold and has no adverse flags.',
  cited_rule_ids: [],
  missing_information: [],
  recommendation: 'APPROVE',
  confidence: 'High',
  memo_hash: 'h-abc',
  model_version: 'm-1',
};

export function makeMemoView(overrides = {}) {
  const { memo: memoOverrides, ...rest } = overrides;
  return {
    application_id: 'app-1',
    recommendation_id: 'rec-1',
    status: 'ready',
    profile: BASE_PROFILE,
    report: null,
    memo: { ...BASE_MEMO, ...(memoOverrides ?? {}) },
    ...rest,
  };
}

// (1) empty-lists READY memo — proves `ready != pending` is NOT an emptiness heuristic (PENDING-1),
//     and exercises BR-MEMO-9's empty-list neutral-copy branch (LISTORDER-1).
export const emptyListsReadyMemoView = makeMemoView({
  memo: { missing_information: [], cited_rule_ids: [] },
});

// (2) populated, deliberately NON-SORTED READY memo — proves no client re-sort (LISTORDER-1). The
//     source order (incomplete_flag first) is NOT the backend deterministic order, so a client sort
//     would reorder it — the test asserts the rendered order equals this input order.
export const unsortedReadyMemoView = makeMemoView({
  memo: {
    cited_rule_ids: ['R-3', 'R-1', 'R-2'],
    missing_information: [
      { source: 'incomplete_flag', detail: 'Application marked incomplete' },
      { source: 'missing_document', detail: 'Salary slip not provided' },
      { source: 'not_evaluated_rule', detail: 'Debt ratio rule not evaluated' },
    ],
  },
});

// pending view — memo not yet drafted (status discriminator); report/memo null.
export const pendingMemoView = {
  application_id: 'app-1',
  recommendation_id: null,
  status: 'pending',
  profile: BASE_PROFILE,
  report: null,
  memo: null,
};

export const errorEnvelope = { error: { code: 'internal_error', message: 'kaboom', detail: {} } };
