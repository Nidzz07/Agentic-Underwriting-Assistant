// Shared test fixtures for ui-history (Code-Gen Q2-A / Q3-A / Q8-A). ONE dual-read double factory +
// one named fixture set, reused across every teeth test. All fixtures are plain JS objects shaped to
// WIRE-1 R6/R7 + audit_store.record_schema BY SHAPE — no backend import, no real network (SCOPE-1).
//
// JSX-free (.js) on purpose — uses createElement, mirroring the frozen ui-approval-gate fixtures.
import { createElement } from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { HistoryView } from '../HistoryView.jsx';
import { historyRowTestid, slugSegment } from '../testids.js';

// ---------------------------------------------------------------------------------------------
// Q2-A — the single capturing DUAL-READ double (NFR-HIST-Fold-A).
//
// `{ fetchList, fetchDetail }` — each an INDEPENDENTLY-counted spy recording its OWN args
// (`fetchList.calls[i] === [page, size]`, `fetchDetail.calls[i] === [decision_id]`), programmable and
// SEQUENCEABLE per operation (the last behavior sticks, so a `[reject, resolve]` sequence drives the
// ERROR-1 fail-then-Retry legs). A FRESH instance per test + RTL auto-cleanup isolates the counts, so
// a simple before/after snapshot of `fetchList.calls.length` around Back suffices for BACKPRESERVE-1
// (NFR-HIST-Fold-2 — no before/after-mount discrimination is built into the double).
//
// Because BOTH operations are READS there is NO "zero write calls" gate here (contrast the U7/U8
// asymmetric read+write doubles). The load-bearing count teeth are read-ATTRIBUTION instead.
// ---------------------------------------------------------------------------------------------
function makeSpy(behaviors) {
  const calls = [];
  let i = 0;
  const fn = async (...args) => {
    calls.push(args);
    const behavior = behaviors[Math.min(i, behaviors.length - 1)];
    i += 1;
    if (behavior && 'reject' in behavior) throw behavior.reject;
    const value = behavior ? behavior.resolve : undefined;
    return typeof value === 'function' ? value(...args) : value;
  };
  fn.calls = calls;
  return fn;
}

export function makeHistoryDouble({ list = [], detail = [] } = {}) {
  return { fetchList: makeSpy(list), fetchDetail: makeSpy(detail) };
}

// ---------------------------------------------------------------------------------------------
// Q3-A — the named fixture set.
// ---------------------------------------------------------------------------------------------

// (i) a multi-page LIST fixture — page k (k >= 2) with stable, distinguishable rows, so
//     BACKPRESERVE-1 can assert `page === k` and identical `items` (same rows, same order) after Back.
export const PAGE_K = 2;

export const pageKRows = Object.freeze([
  Object.freeze({ decision_id: 'dec-21', application_id: 'app-21', recommendation_id: 'rec-21', action: 'approve', timestamp: '2026-07-02T09:00:00Z' }),
  Object.freeze({ decision_id: 'dec-22', application_id: 'app-22', recommendation_id: 'rec-22', action: 'override', timestamp: '2026-07-02T10:00:00Z' }),
  Object.freeze({ decision_id: 'dec-23', application_id: 'app-23', recommendation_id: 'rec-23', action: 'approve', timestamp: '2026-07-02T11:00:00Z' }),
]);

export function makeListBody({ page = PAGE_K, size = 20, total = 45, items = pageKRows } = {}) {
  return { items, page: { page, size, total } };
}

export const emptyListBody = makeListBody({ page: 1, total: 0, items: [] });

const BASE_PROFILE = Object.freeze({
  application_id: 'app-21',
  date_of_birth: '1984-01-05',
  as_of_date: '2026-07-02',
  age_years_derived: 42,
  verifiable_income_annual: '900000',
  requested_cover_amount: '500000',
  incomplete: false,
  demographics: Object.freeze({ full_name: 'Jordan Rivera', gender: 'unspecified', city: 'Metropolis' }),
  documents: Object.freeze({ expected_count: 2, satisfied_count: 2, entries: [] }),
});

// (ii) rule_results with N DELIBERATELY-UNSORTED entries — the source order is NOT sorted by rule_id,
//      so a client re-sort would visibly reorder it. RULERESULTS-1's DOM-level query asserts the
//      rendered order equals THIS input order and that all N are present. `rule_id`s deliberately
//      include upper-case/underscore forms so the testids.js slugging is exercised.
export const unsortedRuleResults = Object.freeze([
  Object.freeze({ rule_id: 'R-3', category: 'financial', status: 'pass', actual_value: 3, operator: 'lte', threshold: '5', outcome_tier: 'neutral', message: 'Debt ratio within range' }),
  Object.freeze({ rule_id: 'INCOME_MIN', category: 'financial', status: 'fail', actual_value: 1, operator: 'gte', threshold: '2', outcome_tier: 'refer', message: 'Income below the minimum multiple' }),
  Object.freeze({ rule_id: 'R-1', category: 'health', status: 'pass', actual_value: 'none', operator: 'eq', threshold: 'none', outcome_tier: 'neutral', message: 'No adverse health flags' }),
  Object.freeze({ rule_id: 'A-10', category: 'age', status: 'pass', actual_value: 42, operator: 'lte', threshold: '65', outcome_tier: 'neutral', message: 'Age within band' }),
  Object.freeze({ rule_id: 'R-2', category: 'documents', status: 'not_evaluated', actual_value: null, operator: 'eq', threshold: 'n/a', outcome_tier: 'neutral', message: 'Rule not evaluated' }),
]);

export const singleRuleResult = Object.freeze([unsortedRuleResults[1]]);

function makeReport(ruleResults) {
  return {
    rule_results: ruleResults,
    recommendation: 'DECLINE-RECOMMEND',
    confidence: 'Medium',
    rulebook_version: '1.4.0',
    content_hash: 'ch-report-1',
    engine_version: 'eng-sha-1',
    decline_reasons: ['Income below the minimum multiple'],
    refer_reasons: [],
  };
}

export function makeAuditRecord(overrides = {}) {
  const { committed_decision: committed, audit_tuple: tuple, rule_results: ruleResults, ...rest } = overrides;
  return {
    decision_id: 'dec-21',
    application_id: 'app-21',
    recommendation_id: 'rec-21',
    audit_tuple: {
      rulebook_version: '1.4.0',
      rule_results: makeReport(ruleResults ?? unsortedRuleResults),
      timestamp: '2026-07-02T09:00:00Z',
      model_version: 'model-1',
      memo_hash: 'memo-hash-1',
      engine_version: 'eng-sha-1',
      ...(tuple ?? {}),
    },
    applicant_profile_snapshot: {
      application_id: 'app-21',
      profile: BASE_PROFILE,
      content_hash: 'ch-profile-1',
    },
    committed_decision: {
      recommendation_id: 'rec-21',
      underwriter_id: 'uw-7',
      action: 'approve',
      reason: null,
      ...(committed ?? {}),
    },
    status: 'active',
    supersedes_decision_id: null,
    ...rest,
  };
}

// (iii) an OVERRIDE record (with a reason) and an APPROVE record (no reason) — REASON-1 / SEPARATION-1.
export const overrideRecord = makeAuditRecord({
  decision_id: 'dec-22',
  committed_decision: { action: 'override', reason: 'Verified a second income source by phone.' },
});

export const approveRecord = makeAuditRecord({ decision_id: 'dec-21' });

export const singleRuleResultRecord = makeAuditRecord({ rule_results: singleRuleResult });

// ---------------------------------------------------------------------------------------------
// Q8-A — the named ENVELOPE fixtures (well-formed WIRE-1 §4 shapes), driven table-style by ERROR-1.
// `detail` carries a DISTINCTIVE value so a DOM scan can prove it is rendered NOWHERE.
// ---------------------------------------------------------------------------------------------
export const DETAIL_NEEDLE = 'zzz-detail-never-rendered-zzz';

export const errorEnvelope = { error: { code: 'internal_error', message: 'kaboom', detail: { trace: DETAIL_NEEDLE } } };
export const listErrorEnvelope = { error: { code: 'internal_error', message: 'The history could not be loaded.', detail: { trace: DETAIL_NEEDLE } } };
export const unauthenticatedEnvelope = { error: { code: 'unauthenticated', message: 'Your session has expired.', detail: { trace: DETAIL_NEEDLE } } };
// R7 404 — surfaced through the SAME generic detailError path, no dedicated branch (HIST-Fold-3).
export const notFoundEnvelope = { error: { code: 'not_found', message: 'That record could not be found.', detail: { trace: DETAIL_NEEDLE } } };
export const networkEnvelope = { error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} } };

// ---------------------------------------------------------------------------------------------
// Render helpers (the ui-approval-gate `renderGate` convention) — a FRESH double per call.
// ---------------------------------------------------------------------------------------------

// Mount HistoryView on a double whose list read resolves page k and whose detail read resolves
// `record`; returns the double so the teeth can read `.calls`.
export function renderHistory({ list, detail } = {}) {
  const seam = makeHistoryDouble({
    list: list ?? [{ resolve: makeListBody() }],
    detail: detail ?? [{ resolve: approveRecord }],
  });
  render(createElement(HistoryView, { fetchSeam: seam }));
  return seam;
}

// list -> select the given row -> detail (or detailError). Awaits the list first so the click is real,
// and flushes the detail read INSIDE act(): this helper returns across an extra await boundary, so
// without it the resolved-read state update would land outside the caller's act scope.
export async function openDetail(decisionId = 'dec-21', options = {}) {
  const seam = renderHistory(options);
  await screen.findByTestId(historyRowTestid(decisionId));
  await act(async () => {
    fireEvent.click(screen.getByTestId(`history-row-select-${slugSegment(decisionId)}`));
  });
  return seam;
}
