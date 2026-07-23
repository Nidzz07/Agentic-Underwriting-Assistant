# Code Summary — `intake` + `document-sanitizer` (Code-Gen Part 2)

**Stage**: BUILD → Code Generation, **Part 2 (Generation)** · cluster unit 1
**Date**: 2026-07-04
**Discipline**: TDD (tests FIRST), pytest + Hypothesis, `pytest-cov ≥ 90%` (QA-6).
**Result**: **212 passed · 3 `posix_only` skipped (run in Linux CI) · 99.53% coverage.**
**Application code** lives at the workspace root under `backend/` (never in `guide-docs/`);
this file is the markdown summary only.

> Implements the frozen FD contracts, approved NFR targets, NFR design patterns, and the
> 10 logical components — **re-opening none of them**. No new field, contract, or behaviour was
> introduced. The four ambiguity-check sharpenings were folded in (noted below).

---

## 1. Modules created (`backend/`)

| Module | Component(s) realized | Coverage |
|---|---|---|
| `common/canon_ser.py` | shared **CANON-SER** (single impl of audit-store §2.1) | 100% |
| `common/decimal_context.py` | single declared `Decimal` context (`ROUND_HALF_UP`) | 100% |
| `intake/ipc_codec.py` | `IpcCodec` (data-only, no-pickle subprocess boundary) | 100% |
| `intake/schema.py` | `ApplicantProfile` / `Demographics` / `DocumentManifest` / `DocumentEntry` / `SanitizedText` / `SanitizationReportEntry` / `RejectedIntake` / `FieldError` + enums | 100% |
| `intake/derivations.py` | `DerivationFunctions` (DR-AGE / DR-BMI, pure) | 100% |
| `intake/validation_gate.py` | `IntakeGate` (SEC-2 total-function fail-closed wrapper) | 100% |
| `intake/canon_ser_adapter.py` | `CanonSerAdapter` (delegates to CANON-SER) | 100% |
| `intake/parser.py` | `SubprocessParseWorker` (parent) + `ParseOutcome` | 100% |
| `intake/parse_worker.py` | real pdfplumber child entrypoint | cov-omit (subprocess) |
| `intake/resource_limits.py` | POSIX `setrlimit` seam (RLIMIT_CPU / RLIMIT_AS) | 64% Win / 100% Linux CI |
| `intake/telemetry.py` | `TelemetryEmitter` + allowlist `TelemetryEvent` (no free-text) | 100% |
| `intake/pipeline.py` | `IntakePipeline` (`parse → sanitize → gate` wiring) | 100% |
| `intake/pii_guard.py` | active DATA-4 real-PII guard (+ CLI) | 100% |
| `intake/sanitizer/normalizer.py` | `ObfuscationNormalizer` (NFKC pipeline + origin map) | 100% |
| `intake/sanitizer/pattern_registry.py` | `PatternRegistry` + inert placeholder | 100% |
| `intake/sanitizer/sanitizer.py` | `SanitizerEngine` (SEC-1, no LLM) | 100% |
| `intake/sanitizer/report_channel.py` | `SanitizationReportChannel` (audit-only) | 100% |

Fixtures: `sanitizer/tests/fixtures/corpus_c.py` (22 adversarial, **static**),
`corpus_l.py` (60 benign, **static**), `synthetic_profiles.py` (**seeded** Faker).
`tests/fake_worker.py` simulates subprocess failure modes.

---

## 2. Test → target / rule map (every target has a test)

| NFR-INT-* target / binding FD rule | Test(s) | Step |
|---|---|---|
| **SEC1-NEUT** — 100% neutralization over `C`; idempotence ∀x; FP ≤ 2.0% over `L` | `test_sanitizer.py` (corpus C 100%, Hypothesis idempotence ×300, FP budget) | 7 |
| **SEC1-NEUT** — placeholder-inertness (P1/P2) | `test_pattern_registry.py` (registry-invariant + Hypothesis boundary) | 5 |
| **SEC1-NEUT** — obfuscation normalization | `test_normalizer.py` (NFKC/casefold/collapse/strip) | 6 |
| **SEC1-SANDBOX** — timeout/oom/crash → `unparseable`; isolation; canonical IPC | `test_parser.py` (wall-time all-platform; RLIMIT_CPU/AS `posix_only`) + `test_ipc_codec.py` | 2, 9 |
| **SEC2-TOTAL** — never raises; unexpected → `RejectedIntake(malformed)` | `test_validation_gate.py` (negative matrix + Hypothesis never-raises) | 8 |
| **SEC2-COVERAGE** — four-state × value-presence; thin-file → valid+incomplete | `test_validation_gate.py` (reject-vs-REFER suite) | 8 |
| **DET-1** — byte-identical derivations ×N + boundaries | `test_derivations.py` (age 18/65, BMI 25/30, leap-day, ×10) | 4 |
| **DET-2** — `ApplicantProfile` CANON-SER round-trip; §2.1 four properties | `test_canon_ser_adapter.py` + `test_canon_ser.py` | 1, 10 |
| **FORENSIC** — 3-surface no-leak; telemetry no-free-text schema | `test_telemetry.py` + `test_report_channel.py` | 11 |
| **DATA4** — active PII guard; synthetic-only | `test_pii_guard.py` (active + fixtures clean + seeded) | 13 |
| **OBS** — emit-only, allowlist `{counts, enums, durations, statuses}` | `test_telemetry.py` | 11 |
| **PERF** — hard subprocess timeout bound (Sharpening 2) | `test_parser.py` wall-time; soft budget = observed via emitted `duration_ms` | 9, 11 |

---

## 3. The four ambiguity-check sharpenings (folded in)

1. **POSIX/Windows portability** — `resource.setrlimit` is POSIX-guarded (`resource_limits.py`,
   clean no-op on Windows). The RLIMIT_CPU/RLIMIT_AS tests are `@pytest.mark.posix_only`
   (auto-skipped on Windows via `backend/conftest.py`, **run in Linux CI**); the parent-kill
   **wall-time** test runs on **all** platforms. All termination modes converge to
   `DocumentEntry.status == unparseable`.
2. **NFR-INT-PERF trace naming** — PERF named against Step 9 (hard bound) + Step 11 (soft, observed
   via `duration_ms`); no target reads as orphaned.
3. **CANON-SER §2.1-property assertions** — Steps 1 & 10 assert the four §2.1 properties explicitly
   (lexicographic key order, `Decimal`-as-string, canonical scalars/null-explicit, no volatile fields),
   not merely round-trip.
4. **Fixture terminology** — corpora `C`/`L` are curated **static** files; `synthetic_profiles.py`
   is **seeded** (Faker). Both synthetic, both covered by the active PII guard.

---

## 4. Realization notes (faithful to the frozen markers — not new design)

- `sanitize(raw_text, source_ref="")` — `source_ref` is a passthrough label populating
  `SanitizedText.source_ref` (the contract field); not a new behaviour.
- `application_id` generated via an **injectable** generator seam (default uuid) — assigned only on
  gate pass; the FD leaves the generation mechanism to Code-Gen.
- `backend/common/` holds the single CANON-SER implementation (Q2 / the module-placement detail the
  NFR design explicitly deferred to Code-Gen). audit-store §2.1 remains the spec authority.
- Reason precedence in the gate: structural-invalid → `malformed`; missing required value with an
  unparseable expected doc → `unparseable`; else plain absence → `missing_required` — a consistent
  reading of BR-REQ + the four-state table. **Now pinned in the design as `business-rules.md`
  BR-GATE-REASON** (back-annotated 2026-07-04 — the design owns the behavior the code decided).
- **Post-generation fix (2026-07-04)**: `SubprocessParseWorker` spawned the worker with an absolute
  module path (`-m backend.intake…`) that only resolved when cwd was the repo root — so running from
  any other cwd (e.g. pytest from `backend/`) made every parse fail to `unparseable`, surfacing only on
  the two success-path tests (failure-path tests passed for the wrong reason). Fixed in `parser.py` by
  spawning the subprocess with the repo root as `cwd` + on `PYTHONPATH` and resolving `source_path` to
  absolute — a real robustness bug the production path shared. parser.py back to 100%.

---

## 5. Ownership held (reference-not-own)

CANON-SER spec = audit-store §2.1 (shared util imported by both); observability stack = `observability`
(this unit emits only); persistence = `audit-store` + `database`; blocking-gate aggregation =
`quality-gates` (this unit authors its own tests + defines targets); cloud infra = `deploy-config`.
**Infrastructure Design remained SKIPPED (logged).** N/A step-categories (API / Repository / Frontend /
DB-migration) not generated here (owned elsewhere).

*End of code-summary.md.*
