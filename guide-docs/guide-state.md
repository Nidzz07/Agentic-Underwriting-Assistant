# GUIDE-AI-SDP State Tracking

## Project Information
- **Project Name**: Agentic Underwriting Assistant
- **Project Type**: Greenfield
- **Start Date**: 2026-06-14T09:01:22Z
- **Current Stage**: **SCOPE B — `case-lifecycle` (U24) COMPLETE through Code Generation, APPROVED 2026-07-20 = the FIRST unit added beyond the original 23-unit decomposition. ⚑ THE DECOMPOSITION NOW STANDS AT 24 UNITS, 24 OF 24 COMPLETE.** U24: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · **Infrastructure Design ✓ SKIPPED-logged (the 21st skip, the FIRST Scope-B determination)** · Code-Gen ✓ — backend **1418 passed / 36 skipped / 5 pre-existing `audit_store` Docker-absence errors**; baseline 1308 + **110 new tier-U tests, ZERO regression**; **the skip delta was EXACTLY +5 as predicted** (U24's cleanly-skipping tier-I tests) and **the 5 Docker errors EXACTLY unchanged**; **`backend/case_lifecycle` at 100% on every module** except the deliberately tier-I-only `repository.py`; global gate **HELD at 99.86%**. **⚑ A REAL DEFECT CLASS was found and fixed during TDD** — four scans were flagging **their own docstrings**, i.e. the prose that DOCUMENTS each prohibition (a header saying *"never writes to `audit_record`"* read as a write; a SQL comment saying *"NO GRANTS HERE"* read as a `GRANT`; `Optional[PendingRecommendation]` read as the frozen `Recommendation`). **Fixed by making the scans STRUCTURE-AWARE — `executable_text` / `annotation_names` / `sql_without_comments` — never by weakening an assertion**, mirroring `llm-judge`'s substring-collision lesson; the alternative would have been deleting the disclosures to make the scans pass. **⚑ CG-CASE-Fold-3 caught a genuine BYPASS**: had the tier-I fixture called `MigrationRunner` directly, the **production collision guard would never have executed on the path PERSIST-1 verifies** — now enforced by two tests, one proving the ordering at tier-U without Docker. **Register stands at 14 items, NONE newly discharged**, with **#13 `NOTWIRED-FILENAME-STALE` AMPLIFIED** and **#14 `MEMOVIEW-FAILED-STATE-UNMODELLED` disclosed with real tier-U teeth**. **⚑ REMAINING: exactly ONE authorized piece of Scope B work — the in-place composition-root wiring pass.** → ✅ **THAT PASS IS NOW COMPLETE (2026-07-20, verified 2026-07-21) — SCOPE B IS CLOSED. All seven WIRE-1 routes are LIVE. Backend 1492 / 37 / 5, coverage 99.87%, ZERO regression. Two authorized U24 reopenings. Register 14 → 20. See the final section of this file and `guide-docs/build/composition-root/scope-b-wiring-summary.md`.** → 🟡 **CURRENT (2026-07-21T11:17:26Z): REGISTER ITEM #19 `COMMITTED-TRANSITION-NEVER-PERFORMED` — SCOPING PASS STARTED.** The first work begun after Scope B closed. Ground truth re-established from disk at four checkpoints, **all confirming the gap exactly as disclosed**; **one divergence reported — U24 has been reopened TWICE, not three times**, so a new reopening (if Q2 concludes one is needed) is the **THIRD**. **SCOPING ONLY — no code generated, no unit reopened, every hold upheld.** Plan of record `guide-docs/build/plans/fix-register-19-plan.md` (Q1–Q5, all blank). **STOPPED at the plan-file gate.** See the final section of this file. <!-- superseded U22/23-unit-completion status below -->
<!-- superseded: - **Current Stage**: **BUILD PHASE COMPLETE — `llm-judge` (U22, EPIC-6) COMPLETE through Code Generation, APPROVED 2026-07-19 = the 23rd and FINAL complete build-loop uni ... -->
<!-- superseded: - **Current Stage**: **BUILD PHASE — `deploy-config` (U23, EPIC-6) COMPLETE through Code Generation, APPROVED 2026-07-19 = the 22nd complete build-loop unit overall and the 5th of  ... -->

## Workspace State
- **Existing Code**: No (only a Python `venv/` and root `requirements.txt`; no application source)
- **Programming Languages**: Python intended (per requirements.txt); React + Tailwind planned for UI (TypeScript TBD — not yet specified in brief)
- **Build System**: pip / requirements.txt (Python); npm planned for frontend
- **Project Structure**: Empty (greenfield)
- **Reverse Engineering Needed**: No
- **Workspace Root**: C:\Users\NIDHI\Desktop\underwriting-project
- **Model provider config (applied 2026-06-17)**: PROJECT-BRIEF.md updated to Gemini-primary / Claude-secondary (tested fallback) / Ollama-showcase, runtime-selectable via config/settings behind the provider-abstraction layer (per Q4); supersedes brief v1.0 Claude-primary. NOTE: CLAUDE.md contains NO model config (it is the GUIDE-AI-SDP workflow engine) — the config lives in PROJECT-BRIEF.md.

## Code Location Rules
- **Application Code**: Workspace root (NEVER in guide-docs/)
- **Documentation**: guide-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Extension Configuration
| Extension | Enabled | Decided At |
|---|---|---|
| Security Guardrails | Enabled (scoped) | Requirements Analysis (Q13 answered) |

Security Guardrails scope: prompt-injection defense, input validation, secrets management, read-only DB access for audit role, audit logging.

## Execution Plan Summary (draft — pending Workflow Planning gate approval)
- **Artifact**: `guide-docs/discover/plans/execution-plan.md` (generated 2026-06-19)
- **Stages to Execute (recommended)**: Application Design, Units Generation, Functional Design (per-unit), NFR Requirements (per-unit), NFR Design (per-unit), Infrastructure Design (per-unit), Code Generation (ALWAYS), Build and Test (ALWAYS)
- **Stages Skipped**: Reverse Engineering (greenfield); Deploy = placeholder (production deploy = Phase 3; validation deploy is a Phase 2 BUILD unit)
- **Depth**: Comprehensive recommended; lighten/skip decision reserved by user for the gate (per-unit depth-variation notes provided in execution-plan.md §3)
- **Phase 1→2 sequencing**: per-unit BUILD loop runs all Phase 1 units before Phase 2 (BUILD-loop annotation; see stories.md §8)
- **Risk**: Medium (high intrinsic complexity, greenfield so easy rollback; dominant risk = invariant correctness)

## Stage Progress

### 🔵 DISCOVER PHASE — ✅ COMPLETE (2026-07-02)
- [x] Workspace Detection — Completed 2026-06-14T09:01:22Z (Greenfield)
- [x] Reverse Engineering — SKIPPED (greenfield, no existing code)
- [x] Requirements Analysis — COMPLETED 2026-06-17 (comprehensive depth; requirements.md approved at gate after 2 revision rounds)
- [x] User Stories — COMPLETED 2026-06-18 (Part 1 plan + Part 2 artifacts approved at gate; stories.md, personas.md, user-journey.md final and committed/pushed)
- [x] Workflow Planning — COMPLETED 2026-06-18 (ALWAYS; execution-plan.md generated 2026-06-19 + 3-correction pre-approval pass, APPROVED at gate "Approve & Continue")
- [x] Application Design — COMPLETED 2026-06-29 (gate approved after reviewer-feedback batch)
- [x] Units Generation — COMPLETED 2026-07-02 (gate approved; 23-unit decomposition [17 P1 / 6 P2], story-map 40/40, dependency matrix — unit-of-work.md / unit-of-work-dependency.md / unit-of-work-story-map.md)

### 🟢 BUILD PHASE — IN PROGRESS (started 2026-07-02; Functional Design per-unit loop underway, cluster-FD-first)
- [~] Functional Design (per-unit) — IN PROGRESS overall (4 of 17 Phase-1 units' FDs done — the **cluster-FD-first group is COMPLETE**; the non-cluster Phase-1 units' per-unit BUILD stages remain). **cluster-FD-first: the 4 contract-bearing deterministic-core units got their FDs before any Code-Gen — all four now APPROVED 2026-07-03.** **Unit 1 of 4 — `intake` + `document-sanitizer` (coupled pair): FD APPROVED 2026-07-03** (domain-entities.md / business-rules.md / business-logic-model.md; review-beat correction set applied — application_id system-assigned, services.md §6 Option-1 reconciliation + Mermaid fix). **Unit 2 of 4 — `rules-engine`: FD APPROVED 2026-07-03** (YAML rule schema + input_fields CON-BR1-structural, domain-confirmed boundaries [age 18–65 incl., BMI 25/30, DTI ≤0.40], Decimal DTI/income-multiple, deterministic confidence, tri-state RuleResult, immutable semver+content_hash versioning; review-beat corrections — category-population coverage + operator↔threshold §2.1). **Unit 3 of 4 — `audit-store`: FD APPROVED 2026-07-03** (AuditRecord superset persisting the original ApplicantProfile-by-reference for self-contained replay, single CANON-SER spec, replay equality = evaluation-output projection excluding embedded provenance, CON-BR4 closed-enum + trim-then-empty write-gate, append-only via derived status, OOS-7 seam; review-beat corrections). **Unit 4 of 4 — `memo-agent-core` (the LAST cluster unit, where the LLM enters): FD APPROVED 2026-07-03** (three-region DecisionMemo [LLM-authored prose / deterministic missing_information / injected read-only recommendation+confidence] = structural CON-BR2 at the type level; memo_hash references audit-store's single CANON-SER byte-identically; report-only grounding + citation-validation blocking hallucinated cites; SEC-1-FORENSIC non-ingestion at the input-type level; route_borderline a named not-wired Phase-2 stub). **➡ CLUSTER-FD-FIRST COMPLETE — all shared contracts (ApplicantProfile, RuleResultReport, AuditRecord/6-tuple, DecisionMemo, CANON-SER) designed at field level and cross-unit-consistent.** **Decision point RESOLVED 2026-07-04 → Option (a): resume the default per-unit BUILD loop on the cluster units in dependency order (intake+document-sanitizer → rules-engine → audit-store → memo-agent-core), advancing each through NFR Requirements → NFR Design → [Infra SKIP] → Code-Gen.** **`database` (U15, story-less infra — the FIRST post-cluster unit): FD Part 1 (Plan) written + eleven `[Answer]:` tags filled (all A) + ambiguity-check CLEAN (column-for-column 18/18 vs built `pg_repository.py`; 1 substantive fold [auth-rbac `role` open-not-closed-enum] + 2 minor folds [`status` DB-default optional; `action`/`status` varchar-not-native-ENUM]) + FD Part 2 GENERATED 2026-07-06 — three artifacts in `guide-docs/build/database/functional-design/` (`domain-entities.md` [audit_record 14 cols + applicant_profile_snapshot 4 cols column-for-column + `app_user` open-role skeleton + rulebook-version deferred slot + ER Mermaid], `business-rules.md` [BR-DB-1..14 incl. append-only two-layer + audit_writer/audit_reader semantics + DATA-5 per-tier + co-location + OOS-7 + BYTEA byte-fidelity + SEC-3], `business-logic-model.md` [versioned forward-only migrations model + connection/transaction model + explicit FD↔Infra boundary + consumer→table map + invariant self-check + flow Mermaid]); both folds + all three applied; both Mermaid validated; reference-not-own-reverse held (no consuming code edited); SEC-3 (no credentials). **NOTE: `database` gets a REAL comprehensive Infrastructure Design (NOT a skip) after NFR — it IS the persistence topology.** **`database` FD APPROVED at the 2-option gate 2026-07-06 (all three folds verified consistent across all three artifacts; FD↔Infra boundary clean; consumer→table map edits no consuming code; 18/18 verification preserved; both Mermaid render-confirmed). Advancing to NFR Requirements → NFR Requirements Part 1 (Plan) WRITTEN 2026-07-06** (`guide-docs/build/plans/database-nfr-requirements-plan.md`; comprehensive; eleven `[Answer]:` tags; draft `NFR-DB-*` targets — ATOMIC-1 + COLOC-1 (fault-injection rollback on real Postgres, against the PRODUCTION migrations), APPEND-1 (audit_writer INSERT+SELECT-only / audit_reader SELECT-only vs real Postgres roles), DATA5-1 (structural Postgres-only + config guard), MIGRATE-1/2 (apply-from-empty exact schema + content-checksum immutability), **FIDELITY-1 (ongoing regression — introspect migration-produced schema vs audit-store `pg_repository.py` metadata imported read-only; drift EITHER side fails; makes the 18/18 permanent)**, BYTEA-1 (byte-identical round-trip, no normalization), SCOPE-1 (app_user skeleton exists + role extensible-no-CHECK / rulebook table absent; NO consumer business-logic test), PERF-1/OBS-1 soft; tech-stack pins SQLAlchemy 2.x + testcontainers already-in-stack, no new dep, migration tool + grant execution deferred to Code-Gen/Infra+secrets-config). **Eleven `[Answer]:` tags filled (all A) + ambiguity-check CLEAN (Q1 production-migration independence; Q5 no circular dep + direction-of-truth; Q7 role negative-no-CHECK; Q3 config guard unit-testable-today; every target this-unit-Code-Gen-only, no Infra dependency) + NFR Requirements Part 2 GENERATED 2026-07-06** (`guide-docs/build/database/nfr-requirements/`: **nfr-requirements.md** — 11 finalized `NFR-DB-*` targets each pass/fail with an explicit test tier [integration/testcontainers vs unit/structural] + §0 direction-of-truth + traceability + Security-Guardrails compliance; **tech-stack-decisions.md** — D1–D10). **2 sharpenings + emphasis folded: (1) grant-DDL TEXT is a database-unit Code-Gen deliverable [APPEND-1 writable/runnable at this unit's Code-Gen, no Infra wait; Infra owns only per-env execution + credential binding, SEC-3]; (2) FIDELITY-1 comparison scope = name/type/nullability/PK/FK/index ONLY, CHECK constraints EXCLUDED [optional action/status CHECK + role no-CHECK never trip fidelity]; (3) direction-of-truth explicit [database=schema authority, audit-store pg_repository metadata=consuming reference, FIDELITY test=one-directional consistency guard, no production cross-import/circular-dep].** No Mermaid needed; reference-not-own-reverse held; SEC-3 no-credentials. **`database` NFR Requirements APPROVED at the 2-option gate 2026-07-06** (direction-of-truth + no circular dep; APPEND-1 writable at this unit's Code-Gen; FIDELITY-1 CHECK-exclusion resolves role/action-status consistency; every target a clear tier with no Infra dependency). **Advancing to NFR Design → NFR Design Part 1 (Plan) WRITTEN 2026-07-06** (`guide-docs/build/plans/database-nfr-design-plan.md`; comprehensive; eleven `[Answer]:` tags; each NFR-DB-* → a named pattern [SingleTransactionCoLocationPattern, GrantDDLInMigrationPattern, DbUrlGuardPattern+PostgresOnlyTypePattern, ForwardOnlyMigrationSequencePattern, ChecksumImmutabilityPattern, SchemaIntrospectionComparatorPattern (CHECK-excluded, type-normalization), OpaqueRoundTripProbePattern, ExtensibleRoleInsertPattern+DeferredTableAbsencePattern, ObservedSoftBudgetPattern/N-A]; **6 logical components** [MigrationSequence, GrantDDL, DbUrlGuard, SchemaIntrospector (shared by MIGRATE-1+FIDELITY-1), FidelityComparator, MigrationChecksum]; two validated Mermaid required in artifacts). Plan only; no artifacts, no code. **Eleven `[Answer]:` tags filled (all A) + ambiguity-check CLEAN (Q4+Q6 no third schema representation; Q6 type-normalization complete; Q2+Q5 grants migration IS in the checksum manifest; Q1 concrete duplicate-PK IntegrityError fault; component→target all 11 covered no orphan; no reference-not-own violation) + NFR Design Part 2 GENERATED 2026-07-06** (`guide-docs/build/database/nfr-design/`: **nfr-design-patterns.md** — 9 pattern sections each meeting its NFR-DB-* target + traced + §10 validated pattern-integration Mermaid; **logical-components.md** — 6 components [C1 MigrationSequence sole authority, C2 GrantDDL, C3 DbUrlGuard, C4 SchemaIntrospector shared, C5 FidelityComparator read-only pg_repository, C6 MigrationChecksum] + no-third-schema-representation statement + ownership + reference-not-own check + component→target coverage + validated component-relationship Mermaid). **All four folds applied: (1) sole-schema-authority layering [migrations sole authority; C4 live-read; FIDELITY scope = the 2 audit tables pg_repository declares; app_user via minimal presence assertions, no duplicate MetaData]; (2) checksum manifest INCLUDES the grants migration file [weakened audit_reader grant caught like an edited table migration]; (3) concrete duplicate-PK IntegrityError fault [pytest.raises + both-empty follow-up]; (4) base-type-token normalization ignoring length/precision.** Both Mermaid validated; reference-not-own-reverse held (no component executes grants on a deployed instance / provisions / binds credentials — Infra+secrets-config); SEC-3 no-credentials. **`database` NFR Design APPROVED at the 2-option gate 2026-07-06** (all four folds consistent across both artifacts; FIDELITY scope narrowed; reference-not-own clean; all 11 targets no orphan; both Mermaid render-confirmed). **Advancing to Infrastructure Design — the REAL, comprehensive, NON-SKIP stage (the FIRST non-skip Infra in the build; the four cluster units all logged Infra SKIP) → Infrastructure Design Part 1 (Plan) WRITTEN 2026-07-06** (`guide-docs/build/plans/database-infrastructure-design-plan.md`; comprehensive; twelve `[Answer]:` tags; maps C1 migration-sequence EXECUTION + C2 grant-DDL EXECUTION per env [neither model nor grant TEXT re-opened] + provisioning; Q1 three-tier Docker-dev/testcontainers-CI/Render-prod one-co-located-DB-per-env; Q2 postgres:16 pin + Render free-tier + SSL; Q3 grants run via the migration sequence in every env + role passwords injected from secrets-config at execution [placeholder-not-value, the Infra half of APPEND-1]; Q4 bounded pool + pre_ping + sslmode=require; Q5 migration execution per env [dev make/Compose, CI-before-integration-tests, prod Render release step]; Q6 secrets-config boundary = SHAPES only [DATABASE_URL, AUDIT_WRITER_PASSWORD/AUDIT_READER_PASSWORD], never values SEC-3; Q7 docker-compose postgres:16 matching testcontainers; Q8 networking narrow [Render internal URL + SSL, no LB/VPC]; Q9 monitoring [Render provider metrics + SELECT 1 probe, app telemetry → observability]; Q10 Compute/Messaging N/A justified; Q11 shared-infrastructure.md [single Postgres + one schema shared, isolation via DB roles not instances, co-location requires one DB]; Q12 comprehensive + 3 artifacts + deployment-topology Mermaid). Plan only; no artifacts, no code. **Awaiting the user's twelve `[Answer]:` tags → ambiguity-check → Part 2 on explicit go → Infrastructure Design completion + 2-option gate → then Code Generation (the LAST stage for this unit).**
- [~] NFR Requirements (per-unit) — IN PROGRESS. **`rules-engine`: NFR Requirements APPROVED 2026-07-05** (user approved at the 2-option gate — 15 `NFR-RULES-*` targets all pass/fail testable [PERF-1 observed + tech-stack the two intentional exceptions], DET-1/DET-2 split, CANON-1/RE-D5 RulebookCanonAdapter reference-not-fork, AUDIT-3 matches audit-store projection field-for-field, CON-BR1 belt-and-suspenders, OBS-1 structural allowlist emitter). Now advancing to NFR Design (per-unit). `guide-docs/build/rules-engine/nfr-requirements/`: **nfr-requirements.md** (15 `NFR-RULES-*` pass/fail targets — DET-1 same-order-×N + DET-2 permuted-order [Q1/Q7 split], DEC-1 Decimal DR-DTI/INCM + operand-missing→not_evaluated→refer_trigger, CANON-1 `RulebookCanonAdapter`→shared canon_ser [no §2.1/impl change, no fork], BR1-1 load-time universal-quantifier reject + BR1-2 independent namespace exclusion + SCHEMA-1 operator↔threshold reject, AUDIT-1 deterministic content_hash + AUDIT-2 append-only immutable + AUDIT-3 forensic-not-equality [matches audit-store projection], BND-1 boundary exactness, AGG-1 order-independent DECLINE>REFER>APPROVE + incomplete→REFER-never-DECLINE, CONF-1 deterministic confidence, PERF-1 soft-budget-observed, OBS-1 emit-only allowlist-schema demographic-free) + **tech-stack-decisions.md** (pyyaml safe_load + Pydantic-v2 load-validation + shared decimal_context + `RulebookCanonAdapter` referencing shared CANON-SER + no-LLM + Python 3.12; no new deps). Both sharpenings folded in. No Mermaid. Plan `rules-engine-nfr-requirements-plan.md` P1–P5 [x], P6 gate presented. **`audit-store`: NFR Requirements Part 1 (Plan) WRITTEN 2026-07-05 — awaiting `[Answer]:` tags** (`guide-docs/build/plans/audit-store-nfr-requirements-plan.md`; comprehensive depth; 11 clarifying questions; draft `NFR-AUDIT-*` targets across CON-BR4 commit-gate negative matrix + SEC-4 authz re-check, CON-AUDIT-1 atomic persist + 6-tuple completeness, append-only [service + DB-role] + status-write-once + derived-superseded, replay equality-set projection [matching rules-engine `evaluation_output` field-for-field — the key cross-unit Q2] excluding volatile/forensic fields, SEC-4/5 read-only auditor backend-enforced, CON-BR1 storage≠influence bias-swap-on-snapshot, single CANON-SER reference-not-own, perf/obs soft-budget). Ambiguity-check CLEAN (11 answers all A). **`audit-store`: NFR Requirements APPROVED 2026-07-05** (user approved at the 2-option gate — 14 `NFR-AUDIT-*` targets all pass/fail testable + correctly traced; 3 sharpenings landed exactly [ATOMIC-1 decomposition-agnostic, APPEND-1 references database's real `audit_writer`/`audit_reader` roles, REPLAY-1 single-sourced-projection + reasons-redundancy citing rules-engine's aggregator/DET-2 by name]; DATA-5 test-tier split; reference-not-own intact; tech-stack D1–D12 scoped). Now advancing to NFR Design (per-unit). `guide-docs/build/audit-store/nfr-requirements/`: **nfr-requirements.md** — 14 `NFR-AUDIT-*` pass/fail targets [GATE-1 negative matrix, AUTHZ-1 backend re-check, ATOMIC-1 both-or-neither decomposition-agnostic, TUPLE-1 6-tuple completeness, APPEND-1 two-layer references database-unit `audit_writer`/`audit_reader` grants, STATUS-1 write-once+derived-superseded, REPLAY-1 single-sourced `evaluation_output` projection + reasons-redundancy, REPLAY-2 pure-evaluate/round-trip/no-LLM, BR1-1 storage≠influence bias-swap, READ-1 backend-enforced read-only, LOG-1 audit trail, CANON-1 shared-util-unchanged, PERF-1/OBS-1] each traced to FD rule + invariant + story, + unit/integration test-tier split, + security-guardrails compliance; **tech-stack-decisions.md** — D1–D12 [SQLAlchemy 2.x/psycopg, real-Postgres testcontainers, repository-abstraction fakes, shared CANON-SER referenced, intake ApplicantProfile + rules-engine evaluate()/RuleResultReport/evaluation_output referenced, injected decision_id seam, no LLM, Python 3.12, database owns provisioning/migrations/grants]). **All 3 sharpenings folded in.** No Mermaid. Loop: NFR Requirements → NFR Design → [Infra likely SKIP] → Code-Gen. **`memo-agent-core`: NFR Requirements Part 1 (Plan) WRITTEN 2026-07-05 — awaiting `[Answer]:` tags** (`guide-docs/build/plans/memo-agent-core-nfr-requirements-plan.md`; comprehensive; the LAST cluster unit + where the LLM enters; 11 questions; **central testability principle: the LLM is reached only via an INJECTED `ProviderAbstraction` → every deterministic invariant is unit-testable against a FAKE provider, no live LLM**; draft `NFR-MEMO-*`: CON-BR2 three structural layers [TYPE/STATE/COMMIT], grounding + citation-validation [∀ hallucinated id → citation_failure → memo blocked, deterministic recommendation stands], missing_information deterministic [manifest + not_evaluated + incomplete, NOT LLM], memo_hash via shared CANON-SER referenced-not-re-declared + **this unit owns compute AND verify → closes the audit-store memo_hash carry-forward**, SEC-1-FORENSIC no-original_span structural, CON-DET-1 replay-boundary [memo not in equality set, hash-verified never re-drafted, no-LLM-in-replay], temperature=0 central, advisory-only, provider-abstraction P1-Gemini-only [Claude/Ollama/MCP/route_borderline = Phase-2 memo-extensions named-not-wired], outlier_result Phase-2-optional None-in-P1, perf/obs soft-budget). Plan only — NO artifacts. **`memo-agent-core`: ambiguity-check CLEAN 2026-07-06 (11 answers all A) + NFR Requirements Part 2 GENERATED 2026-07-06 — awaiting the 2-option gate** (`guide-docs/build/memo-agent-core/nfr-requirements/`: **nfr-requirements.md** — 15 `NFR-MEMO-*` pass/fail targets [CONBR2-TYPE/-STATE/-COMMIT three independent structural layers, GROUND-1 report-only no-MCP-P1, CITE-1 Hypothesis-∀, CITE-FAILURE bounded-retry **tested BOTH directions** [recover-within-cap→finalize + exhaust-cap→flag, deterministic recommendation stands], MISSINGINFO-1 deterministic from 3 signals, HASH-1 + REPLAY-1 **corrected ownership wording** [memo-agent-core SOLELY owns memo_hash compute AND standalone verify; audit-store stores memo_hash str only + cannot re-derive; the built ReplayService excludes memo_hash from its equality set and never checks it; verify runs OUTSIDE the rules-replay path], SEC1-1 no-original_span structural, TEMP0-1 central + fake-records-params, ADVISORY-1, PROV-1 Gemini-P1-only Phase-2-seams-not-wired, PERF-1 observed-not-gated, OBS-1 allowlist] each traced to FD rule + invariant + story + security-guardrails compliance; **tech-stack-decisions.md** — D1–D12 [LangGraph C4-sub-flow-only checkpointer-YES/interrupt-NO, injected ProviderAbstraction Protocol + Gemini adapter P1 + scripted call-count-aware fake, Pydantic v2 XML→Pydantic, shared CANON-SER referenced UNCHANGED via memo-local adapter closing the carry-forward, rules-engine RuleResultReport/Rulebook + intake ApplicantProfile referenced, outlier_result Phase-2-optional None-in-P1, Claude/Ollama/MCP/route_borderline Phase-2 named-not-wired, no-LLM-in-tests, Python 3.12, no new dep]). **Both sharpenings folded in.** No Mermaid. **Closes the audit-store memo_hash-verification carry-forward.** **`memo-agent-core`: NFR Requirements APPROVED 2026-07-06** (user approved at the 2-option gate — "Continue to Next Stage"; both sharpenings correctly folded). Now advancing to NFR Design (per-unit). Loop: NFR Requirements → NFR Design → [Infra likely SKIP] → Code-Gen. **`rules-engine`: NFR Requirements Part 1 (Plan) WRITTEN 2026-07-05 — awaiting `[Answer]:` tags** (`guide-docs/build/plans/rules-engine-nfr-requirements-plan.md`; comprehensive depth; 11 clarifying questions across determinism/CON-DET-1 [byte-identical ×N + order-independence], CON-BR1 load-time rejection [universal-quantifier], CON-AUDIT-1 [content_hash determinism + append-only + forensic/equality split], rulebook-canonicalization authority [shared CANON-SER vs rulebook-specific — genuine open Q5], boundary exactness, aggregation/insufficient-info, deterministic confidence, perf soft-budget, emit-only obs, YAML-loader/Decimal/no-LLM/3.12 tech-stack). Plan only — NO artifacts generated. Loop: NFR Requirements → NFR Design → [Infra likely SKIP] → Code-Gen. **`intake` + `document-sanitizer`: NFR Requirements APPROVED 2026-07-04** (nfr-requirements.md — 10 testable NFR-INT-* targets across SEC-1 injection [100% neutralization + idempotence + FP budget ≤2.0%], SEC-1 sandbox [subprocess-isolated, parse-scoped, outside replay path], SEC-1-FORENSIC [extends to telemetry — no span text emitted], SEC-2 [total-function gate + reject-vs-REFER coverage], CON-DET-1 [byte-identical ×N + CANON-SER round-trip via audit-store §2.1], DATA-4 [active CI guard], performance [soft budget + hard bounds], observability [emit-only]; tech-stack-decisions.md — no-LLM sanitizer, pdfplumber subprocess-isolated, Pydantic v2, Decimal, no new deps). Other units' NFR Requirements still to come.
- [~] NFR Design (per-unit) — IN PROGRESS. **`rules-engine`: NFR Design APPROVED 2026-07-05** (user approved at the 2-option gate — 8 patterns each structurally meeting their NFR-RULES-* target, DET-2 all-list-fields sharpening folded in, 9 components no reference-not-own violation, both Mermaid rendered clean). Now advancing to Infrastructure Design (per-unit). `guide-docs/build/rules-engine/nfr-design/`: **nfr-design-patterns.md** (8 pattern sections — §1 determinism [DET-1 fixed-canonical-iteration + DET-2 set-reduction + **binding sharpening: ALL order-derived report list fields — rule_results/decline_reasons/refer_reasons — in the one canonical order by rule_id, since canon_ser preserves list order**], §2 Decimal guard-before-divide, §3 RulebookCanonAdapter→unchanged canon_ser, §4 Pydantic load-reject + independent NamespaceBuilder exclusion, §5 frozen content_hash + append-only, §6 fixed-precedence aggregation + forensic-not-equality report separation [audit-store owns comparison], §7 ConfidenceBander, §8 allowlist TelemetryEmitter + observed-only perf; §9 traceability; §10 validated Mermaid + text alt) + **logical-components.md** (9 components + ownership table [no reference-not-own violation] + validated component Mermaid + text alt). DET-2 sharpening folded in. Both Mermaid validated against the 7 rules. Plan `rules-engine-nfr-design-plan.md` P1–P5 [x], P6 gate presented. **`rules-engine`: NFR Design Part 1 (Plan) WRITTEN 2026-07-05 — awaiting `[Answer]:` tags** (`guide-docs/build/plans/rules-engine-nfr-design-plan.md`; comprehensive; 11 pattern-decision questions mapping each `NFR-RULES-*` target → a design pattern: pure-function evaluate + set-based order-independent aggregation [DET-1/DET-2], Decimal guard-before-divide [DEC-1], RulebookCanonAdapter [CANON-1], Pydantic-v2 load-rejection + independent NamespaceBuilder exclusion [BR1-1/BR1-2/SCHEMA-1], frozen-rulebook content_hash + append-only + output-vs-provenance report separation [AUDIT-1/2/3], fixed-precedence set-reduction [AGG-1], ConfidenceBander [CONF-1], allowlist TelemetryEmitter [OBS-1]; §4 names 9 logical components. Mermaid required in artifacts). Plan only — NO artifacts. Loop: NFR Design → [Infra likely SKIP] → Code-Gen. **`intake` + `document-sanitizer`: NFR Design APPROVED 2026-07-04** (nfr-design-patterns.md — 7 pattern sections: subprocess-isolation [ephemeral worker + IpcCodec data-only no-pickle + parse/derivations split + timeout→unparseable], sanitizer neutralization [versioned PatternRegistry + idempotence structural-GIVEN-placeholder-inertness with registry-invariant test], obfuscation-normalization [deterministic detection-only NFKC pipeline], total-function gate [single fail-closed wrapper], SEC-1-FORENSIC [3 surfaces — audit-channel + TelemetryEmitter NO-free-text-field + extends-to-logs], determinism [pure derivations + single Decimal context + CanonSerAdapter delegating to CANON-SER §2.1], observability/perf/resilience [emit-only, soft-budget+hard-timeout, fail-closed-no-retry]; logical-components.md — 10-component blueprint + relationship diagram). Ambiguity-check CLEAN (11 answers all A). **`audit-store`: NFR Design APPROVED 2026-07-05** (user approved at the 2-option gate — 8 patterns each structurally meeting their `NFR-AUDIT-*` target; both sharpenings folded [§2 co-location constraint as an explicit database-unit dependency, §3 assemble-before-BEGIN no-half-open-txn]; REPLAY-1 single-sourcing a genuine import/call not reimplementation; 6-component reference-not-own check no violation; both Mermaid validated + render-confirmed). Now advancing to Infrastructure Design (per-unit). `guide-docs/build/audit-store/nfr-design/`: **nfr-design-patterns.md** — 8 pattern sections each structurally meeting its `NFR-AUDIT-*` target [§1 fail-closed commit-gate wrapper + independent authz re-check GATE-1/AUTHZ-1; §2 single-ACID-transaction ATOMIC-1 **with the co-location constraint on the `database` unit stated**; §3 assemble+Pydantic-validate BEFORE BEGIN — no half-open txn, TUPLE-1; §4 insert-only repository + derived-superseded read over reserved `supersedes_decision_id` only APPEND-1/STATUS-1; §5 ReplayService single-sourced imported `evaluation_output()` on both sides REPLAY-1/-2/BR1-1; §6 read-only AuditService READ-1/LOG-1; §7 CanonSerAdapter→unchanged shared util CANON-1; §8 allowlist emit-only TelemetryEmitter PERF-1/OBS-1; §9 traceability; §10 validated pattern-integration Mermaid + text alt] + **logical-components.md** — 6 components [DecisionCommitService, AuditStore/repository, ReplayService, AuditService, CanonSerAdapter, TelemetryEmitter] + referenced AuthRBAC/decision_id seam + responsibilities + reference-not-own check [no violation] + validated component-relationship Mermaid + text alt). **Both sharpenings folded in** (ATOMIC-1 co-location constraint; assemble-before-BEGIN sequencing at the repository/unit-of-work seam). Both Mermaid validated against the 7 rules. Loop: NFR Design → [Infra likely SKIP] → Code-Gen. **`memo-agent-core`: NFR Design Part 1 (Plan) WRITTEN 2026-07-06 — awaiting `[Answer]:` tags** (`guide-docs/build/plans/memo-agent-core-nfr-design-plan.md`; comprehensive; 11 pattern-decision questions mapping each `NFR-MEMO-*` → a named design pattern: three independent CON-BR2 structural patterns [schema-unrepresentability / read-only LangGraph channel / no-commit-path bypass-via-recommendation_id], prompt-scoping + report-membership citation-validation + bounded-retry [scripted fake, BOTH directions], deterministic missing_info derivation from the 3 signals, local MemoHashAdapter [compute at finalize + standalone verify OUTSIDE the rules-replay path, delegating to unchanged canon_ser — ReplayService excludes memo_hash], MemoAgentInput schema-exclusion [no original_span], injected ProviderAbstraction + Gemini adapter P1 + scripted fake + Phase-2 seams-named-not-wired, emit-only allowlist telemetry, LangGraph sub-flow checkpointer-YES/interrupt-NO; §4 named components — MemoAgentInputBuilder, PromptBuilder, ProviderAbstraction+GeminiAdapter+FakeProvider, CitationValidator, MissingInfoDeriver, MemoHashAdapter, MemoAssembler, LangGraphOrchestrator, TelemetryEmitter. Mermaid required in artifacts). Plan only — NO artifacts. **`memo-agent-core`: ambiguity-check CLEAN 2026-07-06 (11 answers all A) + NFR Design Part 2 GENERATED 2026-07-06 — awaiting the 2-option gate** (`guide-docs/build/memo-agent-core/nfr-design/`: **nfr-design-patterns.md** — 10 §-pattern sections each structurally meeting its `NFR-MEMO-*` target [§1-3 three independent CON-BR2 patterns schema-unrepresentability/read-only-channel/no-commit-path; §4 prompt-scoping + report-membership citation-validation; §5 bounded-retry with the **shared `MEMO_CITATION_RETRY_CAP` ≥2 constant** across both named tests; §6 MissingInfoDeriver with the **fixed TOTAL cross-source order** {missing_document<unparseable_document<not_evaluated_rule<incomplete_flag} + within-source key — a memo_hash byte-stability requirement, the DET-2 class since canon_ser preserves list order; §7 **MemoHashAdapter** compute-at-finalize + standalone-verify OUTSIDE the rules-replay path delegating to unchanged canon_ser; §8 SEC1-1 schema-exclusion; §9 LangGraph substrate + injected ProviderAbstraction + central temp0 + advisory; §10 emit-only allowlist telemetry] + §11 validated pattern-integration Mermaid + text alt + §12 traceability; **logical-components.md** — 10 components + responsibilities + ownership table + reference-not-own check [NO violation] + validated component-relationship Mermaid + text alt + component→target coverage [no orphan]). **All three folds applied** (Q5 total cross-source order; MemoHashAdapter naming unified — no 'CanonSerAdapter' anywhere in this unit; shared retry-cap constant). Both Mermaid validated against the 7 rules. **`memo-agent-core`: NFR Design APPROVED 2026-07-06** (user approved at the 2-option gate — all three folds verified correctly applied; CON-BR2 three layers independent; corrected memo_hash ownership consistent; all 15 targets traced no orphans; reference-not-own clean; both Mermaid valid). Now advancing to Infrastructure Design (SKIPPED-logged 2026-07-06 — see Infrastructure Design line) → Code-Gen. Loop: NFR Design → [Infra SKIP] → Code-Gen. Other units' NFR Design still to come.
- [~] Infrastructure Design (per-unit) — **`audit-store`: SKIPPED 2026-07-05 (logged)** — **rule justification** (CLAUDE.md Infrastructure Design "Skip IF: No infrastructure changes / Infrastructure already defined"; `execution-plan.md §3` classes pure-logic/service units as "little independent infra"): `audit-store` is a **persistence-LOGIC + service unit** (DecisionCommitService gate/assembly, AuditStore repository interface, ReplayService, AuditService, CanonSerAdapter, TelemetryEmitter) with **no independent cloud topology it designs** — **no untrusted parsing → no subprocess sandbox NFR** (unlike intake); the **persistence topology (schema, tables, migrations, role-grants) is owned by the `database` unit** (Postgres/DATA-5, reference-not-own), and **deployment topology by `deploy-config`** (Render). audit-store owns the repository *interface* + queries + the transaction *boundary*, not the provisioned DB. **The ATOMIC-1 co-location dependency does NOT require an Infra Design stage for audit-store** — it is a **constraint ON the `database` unit's schema design** (audit-store's tables co-located in one Postgres DB/connection), not audit-store's own infrastructure; recorded in the **cross-unit constraints register** (Deferred Decisions) so the `database` design will see it. **No independent cloud resource for audit-store to map.** A **logged skip, not silent** (exactly as intake's / rules-engine's). **`rules-engine`: SKIPPED 2026-07-05 (logged)** — **rule justification** (CLAUDE.md Infrastructure Design "Skip IF: No infrastructure changes / Infrastructure already defined"; `execution-plan.md §3` classes pure-logic units as "little independent infra"): `rules-engine` is a **pure-logic deterministic library** (pyyaml load + Pydantic-v2 validate + pure `evaluate` + `Decimal` derivations) with **no independent cloud topology**. **Even more clearly a skip than intake** — it has **no untrusted parsing → no subprocess sandbox** (the one security-NFR intake had); persistence + replay-orchestration owned by `audit-store` + `database` (Postgres/DATA-5), deployment topology by `deploy-config` (Render), shared CANON-SER/`decimal_context` referenced-not-owned. **No independent cloud resource to map.** A **logged skip, not silent** (exactly as intake's). **`intake` + `document-sanitizer`: SKIPPED 2026-07-04 (logged)** — **rule justification**: CLAUDE.md Infrastructure Design "Skip IF: No infrastructure changes / Infrastructure already defined"; `execution-plan.md §3` classes pure-logic units as "little independent infra". intake+document-sanitizer is a pure-logic backend library (pdfplumber + Pydantic + deterministic sanitizer) with **no independent cloud topology** — persistence owned by `database` (Postgres/DATA-5) + `audit-store`, deployment by `deploy-config` (Render). The **sandboxed-parsing** concern is a **security NFR** already designed in NFR Design (§1), **not** cloud-infra topology. A **logged skip, not silent**. **`memo-agent-core`: SKIPPED 2026-07-06 (logged)** — **rule justification** (CLAUDE.md Infrastructure Design "Skip IF: No infrastructure changes / Infrastructure already defined"; `execution-plan.md §3` classes pure-logic/service units as "little independent infra"): `memo-agent-core` is an **LLM-orchestration LOGIC + service unit** (10 components: MemoAgentInputBuilder, PromptBuilder, ProviderAbstraction+GeminiAdapter+FakeProvider, CitationValidator, MissingInfoDeriver, MemoHashAdapter, MemoAssembler, LangGraphOrchestrator, TelemetryEmitter) with **no independent cloud topology it designs**. **Same rationale as intake/rules-engine/audit-store**: (1) **no untrusted parsing → no subprocess sandbox NFR** (unlike intake — the memo consumes already-clean artifacts, `original_span` structurally excluded); (2) **the LLM provider is accessed via the INJECTED `ProviderAbstraction`** — **Gemini API access is a `deploy-config`/`secrets-config` concern (endpoint/keys), NOT infrastructure this unit provisions** (the unit owns the abstraction interface + adapter, not the provider infra); (3) **persistence is owned by `audit-store` + `database`** (this unit produces a pending `DecisionMemo` + `memo_hash`, persists nothing); (4) **deployment topology by `deploy-config`** (Render). **Checkpointer-backend explicitly evaluated (per the user's flag — NOT assumed):** the LangGraph checkpointer's Phase-1 justification is the citation-retry loop + state durability + 100%-step tracing **within a single request-scoped memo sub-flow invocation** — an **in-process checkpointer (LangGraph `MemorySaver`) suffices for P1**, so there is **no independent persistence backend to provision here**; IF a durable cross-process checkpoint store were ever wanted, it would **reuse the `database` unit's Postgres (reference-not-own)** exactly like audit-store's persistence — never memo-agent-core's own infra. The checkpointer **class choice** is a **Code-Gen tech-stack detail** (which saver), **not a cloud-topology Infrastructure Design concern**. **No independent cloud resource for memo-agent-core to map.** A **logged skip, not silent** (exactly as intake's/rules-engine's/audit-store's). **`database`: Infrastructure Design Part 2 GENERATED 2026-07-06 — the FIRST NON-SKIP Infrastructure Design of the build — awaiting the 2-option gate.** Part 1 plan's twelve `[Answer]:` tags (all A) + ambiguity-check CLEAN (four folds pending) → three artifacts generated: **`guide-docs/build/database/infrastructure-design/infrastructure-design.md`** (C1–C6→infra mapping [C1/C2 provisioned+executed per tier; C3–C6 app/test logic no cloud topology]; deferred-halves execution design [Postgres per tier, grant-DDL execution, connection/pooling, migration execution]; the mandatory **seven-category infra sweep** [Deployment/Storage/Shared applicable; **Compute + Messaging N/A-justified**; Networking/Monitoring narrow]; the `secrets-config` contract), **`guide-docs/build/database/infrastructure-design/deployment-architecture.md`** (dev Docker / CI testcontainers `postgres:16` / prod Render topology; migration-execution flow per env; connection/SSL flow; networking [Render internal URL + SSL, no LB/VPC]; monitoring [provider metrics + `SELECT 1` probe, app telemetry→observability]; validated **deployment-topology Mermaid** [7 rules] + text alternative), and **`guide-docs/build/shared-infrastructure.md`** (single shared Postgres/schema; role-based isolation `audit_writer`/`audit_reader`/app-owner; the **ATOMIC-1 co-location rationale** for role-not-instance isolation; the deferred auth-rbac DB-role flag). **All four ambiguity-check folds applied: (1) placeholder-substitution PINNED** [committed grants file carries `${AUDIT_WRITER_PASSWORD}`/`${AUDIT_READER_PASSWORD}` token only — never a value; runner substitutes from env at execution; MIGRATE-2 checksum hashes the placeholder-bearing file → stable yet edited-grant-still-caught, secret lives outside checksummed content; rendered SQL never logged]; **(2) `AUDIT_WRITER_URL`/`AUDIT_READER_URL` marked REQUIRED** for the APPEND-1 prod guarantee [least-privilege runtime connections realize DB-role enforcement in prod — connecting as owner would make it vacuous; app-wiring delegated to audit-store/deploy-config, this unit guarantees only the roles exist+granted]; **(3) deferred auth-rbac dedicated DB-role flag → register**; **(4) dev `.env` gitignore hygiene** [secrets-config-owned, named as a dependency]. **C1's migration model + C2's grant-DDL text NOT re-opened — only execution/provisioning/connection per tier designed. SEC-3 held (no credential/connection-string VALUES anywhere, only variable-name SHAPES). postgres:16 pin matches built `test_pg_integration.py:45`. Mermaid validated (7 rules) + text alt.** No consuming code edited. **`database` Infrastructure Design APPROVED at the 2-option gate 2026-07-06** (user verified all four folds correctly applied; seven-category sweep complete no category silently skipped; C1/C2 not re-opened; no credential values; Mermaid validated render-confirmed). **Path-correction verified on disk: exactly THREE artifacts exist (infrastructure-design.md + deployment-architecture.md under build/database/infrastructure-design/, shared-infrastructure.md at build/) — no phantom fourth file, no build/shared-infrastructure-design/ dir; guide-state.md + audit.md record only correct paths (the duplicate/mistaken path was only in the on-screen completion wording, corrected).** Advancing to Code Generation (the LAST stage for `database`). Other units' Infrastructure Design still to come (comprehensive for `deploy-config`/`observability`). **`auth-rbac`: Infrastructure Design SKIPPED 2026-07-07 (logged, confirmed at this stage per instruction — NOT pre-committed)** — **rule justification** (CLAUDE.md Infrastructure Design "Skip IF: No infrastructure changes / Infrastructure already defined"; `execution-plan.md §3` classes pure-logic units as "little independent infra"): `auth-rbac` is a **pure-logic policy unit** (6 components: AuthRBAC/authorize, Role enum, PERMISSION_MATRIX, to_role, UserRoleRepository Protocol+fake+real-adapter, ApiAuthGuard) with **no independent cloud topology it designs**. (1) **No untrusted parsing → no subprocess-sandbox NFR** (unlike intake); (2) **no independent persistence** — it **consumes `database`'s `app_user` via a read contract** (raw `role` via its own query), **owns no storage**; (3) **no independent cloud topology** — the **composition-root wiring** (inject the real `AuthRBAC` into audit-store's built `DecisionCommitService`) is the **integration/app-assembly unit's**, the **app-owner connection URL** is **`secrets-config`'s** (SEC-3), the **Postgres instance** is **`database`'s** (owned), and a **future dedicated auth DB role** is **`database`'s deferred-open forward-only migration** (BR-AUTH-9 / Deferred #4) — none provisioned here; (4) the **`ApiAuthGuard`** runs inside the backend app process (the app unit's deployment), **not its own service**. **No independent cloud resource for `auth-rbac` to map.** A **logged skip, not silent** (exactly as intake's/rules-engine's/audit-store's/memo-agent-core's). Advancing to Code Generation (the LAST stage for `auth-rbac`). **`secrets-config`: Infrastructure Design SKIPPED 2026-07-07 (logged, confirmed at this stage per instruction — NOT pre-committed)** — **rule justification** (CLAUDE.md Infrastructure Design "Skip IF: No infrastructure changes / Infrastructure already defined"; `execution-plan.md §3` classes pure-wiring units as "little independent infra"): `secrets-config` is a **pure-config/wiring unit** (C1 Settings BaseSettings, C2 is_postgres_url validator, C3 typed accessors) with **no independent cloud topology it designs**. (1) **No untrusted parsing → no subprocess-sandbox NFR**; (2) **no independent persistence** — it **sources values from env/secrets**, **owns no storage**; (3) **no independent cloud topology** — **`deploy-config`** owns the **per-environment value wiring** + the **composition-root `Settings()` invocation**; `secrets-config`'s production code is a **small library consumed inside other units' processes**, not its own service; (4) the actual credential/URL VALUES are `deploy-config`'s (SEC-3), never provisioned here. **No independent cloud resource for `secrets-config` to map.** A **logged skip, not silent** (exactly as intake's/rules-engine's/audit-store's/memo-agent-core's/auth-rbac's). Advancing to Code Generation (the LAST stage for `secrets-config`). **`secrets-config`: Code Generation Part 1 (Plan) + seven `[Answer]:` tags (all A) + ambiguity-check CLEAN (five cross-checks, no gap; 3 clarity-folds) + Code-Gen Part 2 GENERATED 2026-07-07 — awaiting the 2-option gate.** TDD tests-first, leaf-first, Python 3.12.10. `backend/secrets_config/` — 2 source modules (`url_validation.py` [C2 is_postgres_url via sqlalchemy.make_url, no DbUrlGuard import], `settings.py` [C1 Settings BaseSettings six UPPERCASE required no-default fields + scheme/non-empty validators + plain get_settings() no-cache]) + `.env.example` (repo root, CHANGE_ME placeholders + commented Phase-2) + `.gitignore` `!.env.example` negation + `tests/` (conftest hermetic clean_env + 4 modules, **50 secrets_config tests all PASS**). Full backend suite **733 passed / 3 skipped (posix_only Windows) / TOTAL 99.76%** (QA-6 reached). Every `NFR-SEC-*` tested (FAILCLOSED-1 19 hermetic cases via Settings(_env_file=None) direct; SCHEME-1 accept/reject + Hypothesis fuzz; LEAF-1 AST no-forbidden-imports + own-modules guard + detector self-test; GOV-1 four checks + drift guard [uppercased model_fields == active .env.example keys, commented Phase-2 excluded]; DET-1 repeat + no-network/clock import-absence; PERF-1 observed; SCOPE-1/OBS-1 N/A). **3 folds applied**: (1) get_settings() plain factory no-cache [cleanest re DET-1] + FAILCLOSED/DET tests construct Settings() directly; (2) robust repo-root find via pyproject.toml/.git marker; (3) drift-guard active-key parse [line not starting # and containing =], commented Phase-2 excluded. **Reference-not-own verified STRUCTURALLY**: no production database/consumer import (AST test); scheme validator own (make_url), no shared backend module coupling; DbUrlGuard referenced-in-spirit not imported. SEC-3: no values anywhere, .env.example placeholder-only, real .env gitignored+untracked, fixtures throwaway dummies; no LLM. Coverage: 3 counted modules all 100% (no omit — all pure-logic). 3 flagged realization notes (faithful): plain-factory get_settings; .gitignore `!.env.example` negation; UPPERCASE field names. Code summary `guide-docs/build/secrets-config/code/code-summary.md`; `testresults.txt` refreshed. **Code-Gen APPROVED at the 2-option gate 2026-07-07 → `secrets-config` = the SEVENTH fully-complete unit** (FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓; user verified the LEAF-1 non-vacuous+self-test robustness chain, the GOV-1 bidirectional drift guard + Phase-2 exclusion, the .gitignore `!.env.example` negation fix, and the plain-factory DET-1 resolution). Do NOT advance to any further unit — awaiting the user's separate next-unit decision. **Ready Phase-1 leaves now (deps all built) = `ui-shell` (no deps; highest fan-out — unblocks 5 UI units + the human-gate commit path), `corpus-generator` (memo-agent-core + secrets-config; unblocks quality-gates + outlier-model), `admin-cli` (rules-engine + auth-rbac + database + secrets-config). `deploy-config` = Phase-2, deferred (all P1 before any P2).** **`auth-rbac`: Code Generation Part 1 (Plan) + seven `[Answer]:` tags (all A) + ambiguity-check CLEAN (five cross-checks, no gap; 1 clarity-fold = SSOT-1 surface `check->bool`) + Code-Gen Part 2 GENERATED 2026-07-07 — awaiting the 2-option gate.** TDD tests-first, leaf-first, Python 3.12.10. `backend/auth_rbac/` — 5 source modules (`roles.py` [C2 Role + C3 PERMISSION_MATRIX + C4 to_role], `authorizer.py` [C1 AuthRBAC.authorize one linear fail-closed flow], `repository.py` [C5 UserRoleRepository Protocol + InMemoryUserRoleRepository fake], `pg_repository.py` [C5 real adapter, injected Engine, parameterized query, no forbidden import, no schema assertion], `api_guard.py` [C6 ApiAuthGuard.check pure delegation]) + `tests/` (8 modules, **84 auth_rbac tests all PASS**). Full backend suite **683 passed / 3 skipped (posix_only Windows) / TOTAL 99.75%** (QA-6 reached). Every `NFR-AUTH-*` tested at its tier (DENY-1 four independent cases; MATRIX-1 exhaustive 18-cell grid ×2 + Hypothesis; COMMIT-1; PROTOCOL-1 isinstance + call-shape two-assertion read-only Authorizer import; SSOT-1 stub both directions + no-inlined-logic structural; BIAS-1 signature + swap; DET-1 repeat-invariance; PERF-1 observed; fold-1 no-forbidden-imports AST scan + non-vacuous guard + detector self-test; consumption smoke on Docker). **Reference-not-own verified STRUCTURALLY**: no production `audit_store`/`database` import anywhere in `backend/auth_rbac/` (AST-scan test, not inspection); `Authorizer` Protocol imported read-only in the PROTOCOL-1 test only; duck-typed conformance; `app_user` consumed via own query, no schema/FIDELITY assertion (SCOPE-1). SSOT fold: `ApiAuthGuard.check` returns exactly `authorize()`; `require()` documented-not-built. SEC-3: real adapter injected Engine, no credential values; no LLM. Coverage: 5 counted modules all 100%, `pg_repository.py` omitted (integration-covered, existing `*/pg_repository.py` glob). 2 flagged realization notes (faithful): leaf-first repository-before-authorizer sequencing; `to_role` exact-canonical match (wrong-case/whitespace → None deny-safe). Code summary `guide-docs/build/auth-rbac/code/code-summary.md`; `testresults.txt` refreshed. **Code-Gen APPROVED at the 2-option gate 2026-07-07 → `auth-rbac` = the SIXTH fully-complete unit** (FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓; user verified the AST-based no-forbidden-imports rigor, the pure-delegation guard, and the single linear fail-closed authorize). Do NOT advance to any further unit — awaiting the user's separate next-unit decision. **Ready leaves now = `secrets-config`, `ui-shell`** (auth-rbac's completion unblocks the UI commit path via `ui-approval-gate` once the UI track is underway; `admin-cli` depends on `auth-rbac` + `database` — both now built, but admin-cli is a later dependency-order unit). Register item #4 (auth-rbac dedicated DB role) RESOLVED-for-Phase-1 (Q7-A: none provisioned; door open). **`corpus-generator`: Infrastructure Design SKIPPED 2026-07-07 (logged, confirmed at this stage per instruction — NOT pre-committed)** — **rule justification** (CLAUDE.md Infrastructure Design "Skip IF: No infrastructure changes / Infrastructure already defined"; `execution-plan.md §3` classes pure-logic units as "little independent infra"): `corpus-generator` is a **build-time generation-LOGIC unit** (C1–C8: GenerationConfig, ProfileFactory, LabelingOracle, RejectionSampler, SkewAudit, DocumentTextGenerator, CorpusManifestBuilder/FreezeAdapter, CorpusGenerator orchestrator) with **no independent cloud topology it designs**. (1) **No untrusted parsing → no subprocess-sandbox NFR** — it constructs synthetic data (Faker + build-authored Gemini prose over synthetic inputs), parses no external document (SEC-1 is `document-sanitizer`'s); (2) **no independent persistence it provisions** — it writes flat files to repo-root `corpus/` (`profiles.json` + `manifest.json`), **not a database** (Postgres/DATA-5 is `database`'s); (3) **the tier-B real Gemini access is via `secrets-config`'s `GEMINI_API_KEY` + `memo-agent-core`'s injected `LLMClient` seam** — provider infra this unit does NOT provision; (4) the **out-of-band tier-B build invocation runs as a local/CI build step, not a deployed service** — deployment/orchestration topology (if ever needed) stays `deploy-config`'s P2 scope. **Ambiguity-check for a genuine infra concern (per instruction, not improvised): the only candidate — how tier-B runs in CI/CD — is already resolved by the frozen NFR (tier B is explicitly OUT-OF-BAND, not CI [Q7/D9]; tiers U + S run in the existing pytest CI [D1/D8]); no NEW CI/CD topology is introduced, and the frozen corpus is a committed static repo artifact, not a provisioned store. No corpus-generator-owned infra concern surfaces.** **No independent cloud resource for `corpus-generator` to map.** A **logged skip, not silent** (exactly as intake's/rules-engine's/audit-store's/memo-agent-core's/auth-rbac's/secrets-config's/ui-shell's — the **EIGHTH** unit-level Infra SKIP; `database` remains the one real non-skip). Advancing to Code Generation (the LAST stage for `corpus-generator`).
- [~] Code Generation (per-unit) — IN PROGRESS. **`rules-engine`: Code-Gen APPROVED & COMPLETE 2026-07-05** (user approved at the 2-option gate after on-disk verification of the FD back-annotation). **➡ `rules-engine` is the SECOND FULLY-COMPLETE UNIT of the build: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓.** Full backend suite **386 passed / 3 skipped / 99.62% cov** (QA-6 ≥90% reached); rules_engine = **174 tests, all source lines 100%** (one unreachable enum-exhaustive branch in rulebook_schema). 13 source modules + `rulebook/{1.0.0,1.1.0}.yaml` at `backend/rules_engine/`; code summary at `guide-docs/build/rules-engine/code/code-summary.md`; Tier-1 `testresults.txt` at repo root. All 5 sharpenings folded in (engine_version injected; all-7-operators; ≥2 versions; all-3 tiers; ≥1 set-threshold). **2 realization notes (flagged, faithful): (a) `rulebook_schema.Rule.threshold` given `union_mode="left_to_right"` — 1-line Step-2 correction so YAML string bounds coerce to Decimal per FD §2.1 (no shape/behavior change; Step-2 tests still green); (b) acceptability-as-pass authoring convention (rule pass=acceptable, outcome contributed on fail).** **✅ GAP RESOLVED (option (a), per user direction 2026-07-05): the non-scalar `medical_health` + `document_completeness` categories are now authored via TWO derived SCALAR operands — `health_flag_count` (int, `len(health_flags)`) + `documents_missing_count` (int, `max(expected−satisfied,0)`) — added to `DerivationFunctions` + `ALLOWED_INPUT_FIELDS` + NamespaceBuilder and BACK-ANNOTATED into the frozen FD `domain-entities.md §4.2` (pinned at Code-Gen, like intake's BR-GATE-REASON). Evaluator stays scalar-only (NOT extended); `int` chosen over `bool` (authors directly with numeric operators, no §2.1 change). BR1-1/BR1-2 still hold. ALL 9 CATEGORIES now rule-exercised — the minimal representative rulebook is complete.** *(Superseded prior line: Part 2 IN PROGRESS Steps 0–5.)* **`audit-store`: Code-Gen APPROVED & COMPLETE 2026-07-05** (user approved at the 2-option gate; coverage-config change documented in the code summary). **➡ `audit-store` is the THIRD FULLY-COMPLETE UNIT of the build: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓.** Part 2 (Generation) — all 13 plan steps [x]; TDD tests-first, leaf-first, Python 3.12. **82 unit tests + 1 CI-only integration module; audit_store source 100%; full backend 468 passed / 4 skipped / 99.69%.** 8 unit modules (`record_schema`, `canon_adapter`, `seams` [incl. `CommitContextProvider`], `repository`+in-memory-fake, `commit_service`, `replay_service`, `audit_service`, `telemetry`) + `pg_repository.py` (SQLAlchemy 2.x, CI-integration-covered, omitted from unit cov). All 14 `NFR-AUDIT-*` tested at the correct tier (unit via fake; ATOMIC-1/APPEND-1/READ-1/LOG-1/TUPLE-1-persisted via testcontainers real Postgres, `@pytest.mark.integration`, auto-skipped locally). `CommitContextProvider` seam + both sharpenings (TEST-DDL under tests/ with banner; `rbac_action`≠`CommittedDecision.action`) implemented; imports rules-engine/intake/shared canon_ser+decimal_context read-only unchanged (no shared-code edit). One coverage-config change: added typing-`Protocol` `...`-stub exclude patterns to `[tool.coverage.report]` (source reads 100%). Code summary `guide-docs/build/audit-store/code/code-summary.md`; Tier-1 `testresults.txt` at repo root. FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓. **`memo-agent-core`: Code-Gen APPROVED & COMPLETE 2026-07-06** (user approved at the 2-option gate after on-disk verification — 539 passed / 4 skipped / 99.74%, every memo_agent_core module 100%, no regression). **➡ `memo-agent-core` is the FOURTH FULLY-COMPLETE UNIT — and this CLOSES THE CLUSTER (intake+document-sanitizer, rules-engine, audit-store, memo-agent-core all complete).** Part 2 (Generation) — all Steps 0–13 [x]; TDD tests-first, leaf-first, Python 3.12.10. 12 source modules at `backend/memo_agent_core/` (schemas, constants, memo_hash_adapter, missing_info, citation_validator, provider, prompt_builder, input_builder, orchestrator, assembler, telemetry + tests/fixtures) — all 15 `NFR-MEMO-*` + binding FD rules tested vs the injected FakeProvider (NO live LLM anywhere, incl. the retry loop). **Step-4 gap** (validate_citations' frozen 2-arg signature omits the RuleResultReport) surfaced mid-build, flagged, resolved by **user Option B** (keep the frozen `validate_citations(memo_draft, rulebook)`; inject the report into CitationValidator at construction — frozen signature preserved, NO FD back-annotation needed). **3 folds applied** (TEMP0-1 two-part offline via injected capturing Gemini client + structural no-per-call-temperature; recover-within-cap script length derived from `MEMO_CITATION_RETRY_CAP`; concrete cap value = 2 recorded). LangGraph orchestrator (draft→validate→retry/finalize+flag; `_reject_channel_write` read-only recommendation/confidence channels; MemorySaver checkpointer; no commit path). `pyproject.toml addopts` added `--cov=backend/memo_agent_core` (documented). Imports rules-engine/intake/shared canon_ser read-only unchanged (no shared-code edit). Code summary `guide-docs/build/memo-agent-core/code/code-summary.md`; Tier-1 `testresults.txt` refreshed. **memo_hash compute+verify carry-forward CLOSED.** **`database`: Code Generation Part 1 (Plan) WRITTEN 2026-07-06 — awaiting `[Answer]:` tags** (`guide-docs/build/plans/database-code-gen-plan.md`; comprehensive; TDD tests-first, plan-then-generate; nine `[Answer]:` tags). Maps the 6 NFR-Design components → `backend/database/` modules (C1 `migration_runner.py` + `migrations/*.sql`, C2 `migrations/0002_grants.sql` placeholder tokens, C3 `db_url_guard.py`, C4 `schema_introspector.py`, C5 `fidelity_comparator.py`, C6 `migration_checksum.py` + `checksums.json`); full TDD test→target map (ATOMIC-1/COLOC-1/APPEND-1/DATA5-1/MIGRATE-1/MIGRATE-2/FIDELITY-1/BYTEA-1/SCOPE-1/PERF-1 each at its NFR-pinned tier; OBS-1 N/A); leaf-first order (initial-schema migration → grants migration w/ placeholder → DbUrlGuard → SchemaIntrospector → FidelityComparator [imports `pg_repository` metadata read-only] → MigrationChecksum → fault-injection/round-trip/extensibility integration tests → coverage gate → completion). **Migration tool choice framed as a genuine Q1** (recommended: raw-SQL versioned runner, no new dep, plain `.sql` for clean sha256 + `${VAR}` substitution + tool-agnostic reflection; Alembic = B). **SEC-3 confirmed: no credential values in generated code — only the `${AUDIT_WRITER_PASSWORD}`/`${AUDIT_READER_PASSWORD}` placeholder tokens in the committed grants file + `os.environ` reads; rendered SQL never logged; test role passwords are throwaway fixture-scoped literals.** Held: C1's model + C2's grant text realized-not-re-designed; `pg_repository.py`/audit-store tests not edited (imported read-only by C5's test only); reference-not-own in reverse. Plan only; NO code generated. **`database`: Code-Gen APPROVED & COMPLETE 2026-07-06 (user approved at the 2-option gate after on-disk verification — 599 passed / 99.75% cov / integration tier genuinely executed against real Postgres validating ATOMIC-1/APPEND-1/FIDELITY-1; all four realization notes confirmed faithful, not deviations). ➡ `database` is the FIFTH fully-complete unit (FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ [real, non-skip] · Code-Gen ✓).** TDD tests-first, leaf-first, all §4 steps 0–11 done; Python 3.12.10; Docker up so the integration tier ACTUALLY EXECUTED (testcontainers `postgres:16`), not skipped. `backend/database/` — 5 source modules (`migration_runner`, `db_url_guard`, `schema_introspector`, `fidelity_comparator`, `migration_checksum`) + `migrations/{0001_initial_schema.sql, 0002_grants.sql, checksums.json}` + `tests/` (conftest testcontainers fixture applying the PRODUCTION migrations + factories + 10 test modules, **55 database tests all PASS**). Full backend suite **599 passed / 3 skipped (posix_only on Windows) / TOTAL 99.75%** (QA-6 reached). Every `NFR-DB-*` tested at its NFR-pinned tier (ATOMIC-1 dup-PK IntegrityError→both empty; COLOC-1; APPEND-1 real-role write matrix; DATA5-1 guard; MIGRATE-1 apply-from-empty+forward-only; MIGRATE-2 immutability incl. weakened-grant-caught; FIDELITY-1 vs `pg_repository` read-only import [test-only]; BYTEA-1 5-case adversarial + real CANON-SER; SCOPE-1 novel-role insert + rulebook table absent; PERF-1 observed; OBS-1 N/A). **4 flagged realization notes (faithful, no frozen design re-opened)**: (1) `fidelity_comparator.py` is `audit_store`-import-free in PRODUCTION — the read-only `pg_repository` metadata import lives ONLY in `tests/test_fidelity.py` (exactly as NFR-Design §4 + plan Q5 state; no circular dep); (2) MIGRATE-1 audit-table exact parity delegated to FIDELITY-1 (the one pg_repository-importing test), MIGRATE-1 itself uses targeted column-name presence (no third schema representation); (3) `applied_migrations` tool-tracking table folded → MIGRATE-1/SCOPE-1 use targeted presence/absence, never closed-world; (4) `"timestamp"` quoted in DDL, reflects matching pg_repository. **SEC-3 held**: only `${AUDIT_WRITER_PASSWORD}`/`${AUDIT_READER_PASSWORD}` tokens + `os.environ` reads; rendered SQL never logged; hard-error on missing env var; test passwords throwaway fixture-scoped literals. Coverage: `db_url_guard`+`migration_checksum` counted 100%; the 3 live-DB modules omitted from unit-tier coverage exactly like `pg_repository.py` (integration-covered). Code summary `guide-docs/build/database/code/code-summary.md`; `testresults.txt` refreshed. **APPROVED 2026-07-06 → `database` = the FIFTH fully-complete unit.** Do NOT advance to any further unit — awaiting the user's separate next-unit decision. Newly-unblocked-by-database: `auth-rbac` (its `app_user` dependency is now built). Ready leaves now = `auth-rbac`, `secrets-config`, `ui-shell`. **`ui-outlier-view` (U20, C5, Phase 2): Code-Gen APPROVED & COMPLETE 2026-07-17** (user approved at the 2-option gate after diff review). **=> `ui-outlier-view` is the NINETEENTH FULLY-COMPLETE UNIT of the build and the SECOND complete Phase-2 unit: FD OK - NFR Requirements OK - NFR Design OK - Infrastructure Design SKIPPED-logged OK - Code-Gen OK.** Frontend **682 passed / 137 files** (+158 tests / +20 files over the measured 524/117 baseline, zero regression); **`src/outlierView` 100% on every metric across every file**; ESLint clean; backend mtime-verified untouched (1011/31). 9 production files + 13 test/harness files under `frontend/src/outlierView/`; **three additive shared-config edits only** (NEW `eslint-rules/outlierView.js` the Q1-A `*` family; `eslint.config.js` +1 block reusing the ONE shell FORBIDDEN_TERMS; `vitest.config.js` +include/+coverage — **thresholds UNCHANGED**); **no frozen `src/` tree touched**. Q1-Q8 all A; ambiguity-check CLEAN (**CG-OUTV-Fold-1..4**). Load-bearing pair proven with real teeth: **STATE-1** (both null-causes incl. the Phase-1 `ready`+`outlier:null` fixture proving FIELD-derivation not `status`-derivation; failure => ERROR with `outlier-state-notavailable` asserted ABSENT; the paired positive/negative `deriveOutlierState` teeth) and **NOVERDICT-1** (import-absence scan as the primary robust half + rendered `queryBy*`-null over the ENUMERATED finite set imported from `shell/copy`, EXACT matching never a substring sweep; both regions rendered WITH verdict/provenance props FORCED on them and shown to render neither). **Two self-corrections reported not silent**: `@testing-library/user-event` is NOT a devDependency (corrected to `fireEvent`, the frozen sibling convention — no new dependency); and `headerComments.test.js` failed 2/158 on a naive line-wrap matcher — **the TEST was fixed, not the source; no source was weakened to make a test pass.** Code summary at `guide-docs/build/ui-outlier-view/code/code-summary.md`; `testresults.txt` refreshed; plan re-saved with the eight answers + §7.9 folds + Steps 0-8 [x].
- [x] Code Generation (per-unit) — **`intake` + `document-sanitizer`: Code-Gen APPROVED & COMPLETE 2026-07-05** (user approved after the cwd-bug fix + BR-GATE-REASON back-annotation; verified 212 passed / 3 posix_only skipped / 0 failed / 99.53% cov, parser.py 100%). **➡ `intake` + `document-sanitizer` is the FIRST FULLY-COMPLETE UNIT of the build: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓.** Post-approval **build-wide runtime pin set** (flagged at this unit, applies to every unit): **Python 3.12 pinned** across dev/test/CI/Render for NFKC/Unicode-version determinism (CON-DET-1) — enforced via `.python-version`=3.12 (repo root; Render/pyenv/CI single source of truth) + `pyproject.toml` `requires-python=">=3.12,<3.13"` + D6 in `tech-stack-decisions.md`. **Env action pending: the dev venv is currently 3.14.4 and must be recreated on 3.12 (interpreter install, not a file edit) to match the pin.** Do NOT advance to `rules-engine` (awaiting the user's separate go). **THE FIRST CODE OF THE BUILD IS WRITTEN.** TDD tests-first across all 16 plan steps; **212 passed / 3 `posix_only` skipped (run in Linux CI) / 99.53% coverage** (QA-6 `--cov-fail-under=90` reached). App code at workspace root `backend/` (never guide-docs/). Modules: `common/canon_ser.py`+`decimal_context.py` (single shared CANON-SER of audit-store §2.1); `intake/{ipc_codec,schema,derivations,validation_gate,canon_ser_adapter,parser,parse_worker,resource_limits,telemetry,pipeline,pii_guard}.py`; `intake/sanitizer/{normalizer,pattern_registry,sanitizer,report_channel}.py`; static corpora C/L + seeded synthetic_profiles + fake_worker. All four ambiguity-check sharpenings folded in (1 POSIX/Windows setrlimit portability — wall-time all-platforms + RLIMIT_CPU/AS posix_only in Linux CI, all termination modes → deterministic `unparseable`; 2 NFR-INT-PERF trace naming; 3 CANON-SER §2.1 four-property assertions; 4 static-corpora-vs-seeded-Faker fixtures). Every NFR-INT-* target + binding FD rule has a test (map in `guide-docs/build/intake/code/code-summary.md`). Implements frozen FD/NFR/components — no new field/contract/behavior introduced. Plan `intake-code-gen-plan.md` Steps 0–15 all [x]. **Next cluster unit on approval: `rules-engine` Code-Gen (dependency order).** **PER-UNIT CODE-GEN COMPLETIONS (dependency order): `intake`+`document-sanitizer` (1st) · `rules-engine` (2nd) · `audit-store` (3rd) · `memo-agent-core` (4th) · `database` (5th, first real non-skip Infra) · `auth-rbac` (6th) · `secrets-config` (7th) · `ui-shell` (8th, first frontend/React) · `corpus-generator` (U14, 9th — Code-Gen APPROVED & COMPLETE 2026-07-08: `backend/corpus_generator/` 11 source modules + tier-B `build.py` [omitted from cov] + 12 test modules; 67 tests / 100% own-code coverage; full backend 800 passed / 3 skipped in Docker CI = 733 prior + 67, zero regression; 99.80% ≥ 90% QA-6; frontend Vitest untouched; unblocks `quality-gates` U13/P1 + `outlier-model` U18/P2 — see `guide-docs/build/corpus-generator/code/code-summary.md`).**
- [ ] Build and Test — EXECUTE (ALWAYS)

### 🟡 DEPLOY PHASE
- [ ] Deploy — PLACEHOLDER

## Deferred Decisions (carry forward — see requirement-verification-questions.md "Deferred Decisions Register")
- **~~CROSS-UNIT CONSTRAINT → `database` unit~~ → ✅ RESOLVED / CLOSED 2026-07-06 (database Code-Gen complete)**: audit-store's **ATOMIC-1** guarantee (atomic both-or-neither commit+persist) rested on a **single ACID transaction** spanning tables **co-located in ONE Postgres database on one connection**. **Now SATISFIED by `database`'s production schema**: `migrations/0001_initial_schema.sql` places `audit_record` + `applicant_profile_snapshot` (PK+FK child) in **one Postgres database/schema** — proven by **NFR-DB-COLOC-1** (`test_migration_apply::test_both_audit_tables_in_one_schema`) and **NFR-DB-ATOMIC-1** (`test_atomic_colocation::test_duplicate_pk_rolls_back_both_rows`, both tables empty after rollback) on real Postgres. The **`audit_writer` (INSERT+SELECT) / `audit_reader` (SELECT-only)** role grants that audit-store's APPEND-1/READ-1 tests reference are authored in `migrations/0002_grants.sql` and proven by **NFR-DB-APPEND-1** (`test_grants_roles`, real-role write matrix). **NFR-DB-FIDELITY-1** now guards the column-for-column match permanently. **No longer open** — if the two tables were ever split across databases, revisit with outbox/saga; not the case in Phase 1/2. (Source: `guide-docs/build/audit-store/nfr-design/nfr-design-patterns.md §2`; satisfied by `guide-docs/build/database/**` + `backend/database/`.)
- **~~CROSS-UNIT CONSTRAINT → `memo-agent-core` unit~~ → ✅ CLOSED 2026-07-06 (memo-agent-core Code-Gen)**: memo-hash integrity verification ownership belonged to `memo-agent-core`; **now RESOLVED** — `memo-agent-core`'s `MemoHashAdapter` owns BOTH `compute` (at finalize) AND `verify` (standalone recompute-and-compare, no LLM), delegating to the unchanged shared `canon_ser`. Verified against the built `audit_store/replay_service.py`: `ReplayService` re-evaluates rules only and EXCLUDES `memo_hash` from its equality set (audit-store stores `memo_hash` str-only, cannot re-derive). Tested (`test_memo_hash_adapter.py::test_verify_*`, `::test_memo_is_not_in_the_rules_replay_equality_set`). **No longer open.** (Was: audit-store `business-rules.md` BR-REPLAY-NO-MEMO.)
- SSO/OAuth timing → now Phase 3 (OOS-3); detailed timing within Phase 3 deferred to that release
- Synthetic corpus generation timing relative to phases → re-raise at a later stage
- Senior-underwriter escalation persona (Q5-B) → deferred unless escalation enters scope
- **`medical_health` + `document_completeness` rule authorability → RESOLVED 2026-07-05 (option (a))**. Surfaced at rules-engine Code-Gen Step 13 (non-scalar operands). Resolved by adding two derived SCALAR operands — `health_flag_count` (int) + `documents_missing_count` (int) — to `DerivationFunctions` + `ALLOWED_INPUT_FIELDS` + NamespaceBuilder, back-annotated into the frozen FD `domain-entities.md §4.2`; the evaluator was NOT extended (scalar-only holds). Both categories now authored in the representative rulebook → all 9 categories rule-exercised. (The full 25–40-rule production population remains deferred — below.)
- **`auth-rbac`'s own dedicated PostgreSQL DB role scoped to `app_user` → ✅ RESOLVED FOR PHASE 1 by `auth-rbac` (2026-07-07, FD Q7-A / BR-AUTH-9), door left OPEN** *(was: DEFERRED to auth-rbac's own design, recorded 2026-07-06 at database Infrastructure Design)*: auth-rbac's own FD **made the call** — **Q7 = A: NO dedicated auth DB role in Phase 1**. `app_user.role` values (`underwriter`/`auditor`/`admin`) are **application-level data**, distinct from PostgreSQL **DB roles**; auth-rbac reads `app_user` over the **app-owner connection** (no new DB role merely to store/read rows). **auth-rbac Code-Gen realized exactly this** — the real `PostgresUserRoleRepository` takes an **injected `Engine`**, provisions **no dedicated role**, authors **no grant** (verified in `backend/auth_rbac/pg_repository.py`). **NOT activated as a blocking item by Code-Gen; the decision was to NOT provision one.** **The door stays genuinely OPEN**: a future dedicated least-privilege auth DB role, if ever wanted, is a **forward-only `database`-owned migration** that does not disturb the audit roles and needs **no rewrite** of auth-rbac's app-level policy. (Source: `guide-docs/build/auth-rbac/functional-design/business-rules.md` BR-AUTH-9 + `guide-docs/build/shared-infrastructure.md §4`.)
- **WIRE-1 — frontend↔backend api/serialization contract → OPEN cross-unit constraint (recorded 2026-07-07 at `ui-shell` FD, Option A)**: no HTTP wire contract is pinned anywhere yet — verified on disk there is **no `backend/app/` composition root / `main.py` / routes / response models** and the FastAPI orchestrator is explicitly **not a per-unit-loop unit** (`unit-of-work.md §2` — deferred to Build & Test). **Owner**: a **to-be-authored `api-contract` artifact on the FastAPI composition-root layer** (named now). **HARD CHECKPOINT**: WIRE-1 **MUST be authored and pinned BEFORE `ui-queue`'s FD begins** — `ui-queue` (U5) is the **first data-consuming UI unit** and may not start against an unpinned contract. **`ui-shell` (U10) proceeds without it** because it **fetches nothing real** (abstracted `shell/session` seam + test stubs only). **Required contents when pinned**: endpoint/route list, response envelope shape, error shape, and how the current user's **Role** reaches the client (session/auth response). **Serialization invariant to preserve**: enums serialize **by value** — canonical wire map: Recommendation **UPPERCASE** (`APPROVE`/`REFER`/`DECLINE-RECOMMEND`), Confidence **Title-case** (`High`/`Medium`/`Low`), Role **lowercase** (`underwriter`/`auditor`/`admin`), CommitAction **lowercase** (`approve`/`override` — both values; `approve` = agree, `override` = disagree with a mandatory non-blank reason; a **distinct namespace** from system Recommendation — the human `override` is NOT the system `DECLINE-RECOMMEND`); the `ui-shell` copy module keys on these values and **WIRE-1 must not remap or re-case them**. (Source: `guide-docs/build/ui-shell/functional-design/business-logic-model.md §5`; `domain-entities.md §2.1`.)
- **Full production rulebook authoring (25–40 rules) → DEFERRED to a dedicated data-authoring pass** (recorded 2026-07-05 at rules-engine Code-Gen Q3=A). rules-engine Code-Gen authors the ENGINE + schema + a **minimal representative rulebook** (4 boundary rules + ≥1 profile-backed rule per the 9 categories) sufficient to exercise every engine path + every `NFR-RULES-*`/FD assertion; the complete IRDAI clause set / occupation-risk table / health-flag catalogue is **pure data over the same tested schema**, authored later. **Follow-up deliverable — do not lose** (like OOS-7). The generic engine needs no re-work when the production rulebook is authored.
- **Frozen corpus artifact (`corpus/profiles.json` + `corpus/manifest.json`) materialization → NEW register note (recorded 2026-07-08 at `corpus-generator` Code-Gen completion)**: `corpus-generator` (U14) is COMPLETE and is **CON-BR3's single source** of the seeded/versioned/skew-audited synthetic corpus, but **the real frozen artifact does NOT yet exist on disk** — it is produced **only by the out-of-band tier-B `build.py` run** (`python -m backend.corpus_generator.build`, real google-genai `LLMClient` + `secrets_config` `GEMINI_API_KEY`, 300+ profiles), which is **never run in CI** (Q4/Q7) and was **not run at Code-Gen** (repo-root `corpus/` is absent by design). CI exercises the **tier-U/S in-memory path** only — the `test_scoped_config` (min_profiles≈9, wide tolerance, edge-subset; Fold NFR-1) driven by the **injected capturing LLM double**, which **never masquerades as the real corpus**. **Consequence for downstream consumers**: `quality-gates` (U13, P1) and `outlier-model` (U18, P2) read the **frozen `corpus/` artifact only** (BR-CORP-5 freeze-and-commit; they never re-invoke the generator or Gemini) — so **before either can verify/score against the REAL 300+ corpus, the tier-B build must actually be run and its output committed** (a deliberate, tracked, manifest-versioned regeneration, Fold 4). A `quality-gates`/`outlier-model` design stage may proceed on the generator's *contract + a small test-scoped corpus*, but the **acceptance-criteria runs (bias-swap delta=0 over the corpus, rule-coverage, reproducibility ×10, outlier scoring) require the committed tier-B artifact**. **Follow-up deliverable — do not lose**: run + commit the tier-B corpus before the corpus-consuming acceptance runs. (Source: `guide-docs/build/corpus-generator/code/code-summary.md §3–§5`; `business-rules.md` BR-CORP-5/6/11.)

## Resolved Decisions
- Phase boundaries / whether a Phase 3 exists → **RESOLVED 2026-06-18**: Phase 1 + Phase 2 built this engagement (every story phase-tagged 1/2); Phase 3 = documented future release (OOS-2..6 + production deploy). Validation deploy = Phase 2; production deploy = Phase 3. (Detail in requirements.md §2.2 / §12.)
- Human-approval-gate semantics for a REFER recommendation → **RESOLVED 2026-06-18** (per project direction): Phase 1/2 = the underwriter resolves every recommendation incl. REFER at the human approval gate via Accept/Decline with a mandatory reason (no REFER-specific branch built); REFER→senior-underwriter escalation routing = Phase 3 / OOS-2 (documented, not built). Gate stories (US-UI-4/5) and user-journey.md already encode this uniform gate — no story/journey edits needed. (Detail in requirements.md OOS-2 / §12.)

## Current Status
- **Lifecycle Phase**: **DISCOVER COMPLETE (2026-07-02)** → **BUILD IN PROGRESS** (Functional Design per-unit loop; cluster-FD-first group complete 2026-07-03)
- **Current Stage**: **BUILD → per-unit loop. `rules-engine` is the SECOND FULLY-COMPLETE UNIT (2026-07-05)** — FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · **Code-Gen APPROVED ✓** (rules_engine 174 tests / 100% source cov; full backend 386 passed / 3 skipped / 99.62%; all invariants green; no intake/common regression; non-scalar-category gap resolved via derived scalar operands + FD §4.2 back-annotation). `intake` + `document-sanitizer` remains the FIRST fully-complete unit (2026-07-05). The two remaining cluster units (`audit-store`, `memo-agent-core`) have **FD approved** but their NFR/Code-Gen stages are **not started**. **Build-wide runtime pinned: Python 3.12** (`.python-version` + `pyproject` + D6; venv recreated on 3.12.10).
- **Next Step**: **`memo-agent-core` Code-Gen APPROVED & COMPLETE 2026-07-06 — the FOURTH fully-complete unit; THE CLUSTER IS CLOSED** (FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓). `backend/memo_agent_core/` — 12 source modules all 100% covered; full backend suite **539 passed / 4 skipped / total 99.74%**, no regression. Step-4 gap resolved via user Option B (frozen `validate_citations(memo_draft, rulebook)` preserved; report injected at construction). **memo_hash compute+verify carry-forward CLOSED.** **`database` (U15) is now the FIFTH FULLY-COMPLETE UNIT (2026-07-06)** — FD ✓ · NFR Requirements ✓ · NFR Design ✓ · **Infrastructure Design ✓ (real, non-skip — the first of the build)** · Code-Gen ✓ (599 passed / 99.75% / integration tier executed on live Postgres). ATOMIC-1 co-location + audit_writer/audit_reader grants landed and proven (COLOC-1/ATOMIC-1/APPEND-1/FIDELITY-1 green); the ATOMIC-1 cross-unit constraint is **RESOLVED/CLOSED** (Deferred Decisions register). **Next move (awaiting the user's separate go): the next Phase-1 unit in dependency order.** 11 P1 units remain; **ready leaves = `auth-rbac` (newly unblocked — its `app_user` dependency is now built), `secrets-config`, `ui-shell`**. **Recommended next = `auth-rbac`** — highest-leverage ready leaf: it closes the open `app_user.role` model `database` deliberately left open (BR-DB-12), gives the SEC-4 underwriter/auditor identity the built audit-store commit-gate re-check already references a real home, and is the gateway to the human-in-the-loop **UI commit path** (`ui-approval-gate`) + `admin-cli`. (`secrets-config` = low-risk alternative that closes the SEC-3 URL/password-shape wiring `database`/audit-store deferred + unblocks `deploy-config`; `ui-shell` opens the separate React frontend track.) **UPDATE 2026-07-06: user picked `auth-rbac`. Functional Design UNDERWAY — Part 1 plan written + ten `[Answer]:` tags (all A) + ambiguity-check CLEAN (five cross-checks vs the ACTUAL `seams.py`/`commit_service.py`; 2 folds recorded) + FD Part 2 GENERATED — three artifacts in `guide-docs/build/auth-rbac/functional-design/` (`domain-entities.md`, `business-rules.md`, `business-logic-model.md`) — awaiting the 2-option gate.** auth-rbac's real `AuthRBAC.authorize(user_id, rbac_action) -> bool` conforms to audit-store's built `Authorizer` Protocol (no audit-store edit); consumes `database`'s `app_user` (no schema edit, role set closed at app layer per BR-DB-12); role→permission matrix (underwriter: commit+read; auditor: read-only; admin: manage_users+config); fold #1 deny-by-default all-three-cases; fold #2 both enforcement points call the ONE `authorize` (single policy source of truth); Q7 DB-role decision = app-level-only (B's forward-only path left open); OIDC `subject` seam reserved, SSO deferred (OOS-3). **FD APPROVED 2026-07-06. NFR Requirements UNDERWAY — Part 1 plan + eleven `[Answer]:` tags (all A) + ambiguity-check that SURFACED one genuine frozen-design gap (STOP+flag, not improvised): DENY-1's three-independently-testable cases + business-logic-model §1's flow required the `UserRoleRepository` read contract to return raw `str | None`, inconsistent with FD domain-entities §2.5's `role_of -> Role | None`. RESOLVED by user option 1 → FD back-annotation APPLIED + verified on disk (domain-entities.md §2.5: `UserRoleRepository.get_role(user_id) -> str | None`, canonicalization+fail-close inside `authorize`; seam-shape clarification only, no invariant/field/behavior change). NFR Requirements Part 2 GENERATED 2026-07-07 — `guide-docs/build/auth-rbac/nfr-requirements/` (`nfr-requirements.md` 10 `NFR-AUTH-*` targets pass/fail + tiers + traceability + Security-Guardrails; `tech-stack-decisions.md` D1–D12, no new dependency). Both clarity sharpenings folded (PROTOCOL-1 = isinstance + call-shape two-assertion; SSOT-1 = delegation-via-injected-stub); SCOPE-1 labeled a governance/exclusion statement (not a runtime test). Primarily unit-tier against a fake `UserRoleRepository` + read-only `Authorizer` import; optional thin testcontainers smoke asserts nothing about database's schema.** **NFR Requirements APPROVED 2026-07-07. NFR Design UNDERWAY — Part 1 plan + eleven `[Answer]:` tags (all A) + ambiguity-check CLEAN (six cross-checks; no gap this time — the §2.5 back-annotation already resolved the read-contract issue; 3 clarity-folds recorded) + NFR Design Part 2 GENERATED 2026-07-07 — `guide-docs/build/auth-rbac/nfr-design/` (`nfr-design-patterns.md` 8 patterns each meeting its NFR-AUTH-* target + validated pattern-integration Mermaid; `logical-components.md` 6 components [C1 AuthRBAC, C2 Role enum, C3 PERMISSION_MATRIX, C4 to_role, C5 UserRoleRepository Protocol+fake+real-adapter, C6 ApiAuthGuard] + ownership + reference-not-own check + component→target coverage no-orphan + validated component-relationship Mermaid). All 3 folds applied: (1) no-audit_store-production-import stated structurally testable [no `from backend.audit_store` in auth_rbac production; real adapter + guard import no audit_store/database prod modules]; (2) SSOT guard MAY route endpoint→rbac_action but MUST NOT decide allow/deny, stub test exercises stub-True AND stub-False; (3) real adapter adds no app_user schema/FIDELITY assertion [SCOPE-1], app_user drift protection is database's. Both Mermaid 7-rule validated + text alts. No production audit_store import anywhere; SEC-3/no-LLM held. — awaiting the 2-option gate.** On gate approval → Infrastructure Design for auth-rbac (LIKELY a logged SKIP — pure-logic authz unit; confirmed at that stage). **Still-tracked cross-unit constraint: ATOMIC-1 co-location on the `database` unit's schema** (+ the two role grants). *(⚠️ The remainder of this bullet below is HISTORICAL copy-forward from the audit-store / early-memo-agent-core phase and is SUPERSEDED — memo-agent-core is now COMPLETE and the cluster is closed; the authoritative pointers are the Current Stage line, the per-unit Code Generation line, and the Deferred Decisions register above.)* On the filled answers → ambiguity-check → generate Part 2 (`nfr-requirements.md` + `tech-stack-decisions.md`) → NFR-Requirements 2-option gate. Then NFR Design → [Infra likely SKIP] → Code-Gen. **Named memo-agent-core Code-Gen spot-check files (for when its Code-Gen plan is written)**: the `DecisionMemo` three-region structural CON-BR2 realization (LLM-authored prose / deterministic missing_information / injected read-only recommendation+confidence), the citation-validation (hallucination guard vs the rule_results), and the LangGraph immutable-recommendation state. **memo_hash carry-forward lands here** — this unit owns memo_hash compute AND verify (recompute-and-compare, no LLM), byte-identical to audit-store's ReplayService via the shared CANON-SER. **The other cross-unit constraint remains tracked**: ATOMIC-1 co-location on the `database` unit's schema. The flagged commit-context gap was resolved by **adding the 4th injected `CommitContextProvider` seam** (`get(recommendation_id) -> CommitContext{rule_results, memo_hash, model_version, engine_version, rulebook_version, applicant_profile}`, orchestrator/pipeline-owned, reference-not-own; `commit` keeps its frozen 4-param signature + fetches internally; fake provider in tests) — folded into `audit-store-code-gen-plan.md` (§1.2, new §1.5, §1.3 seams, Step 3, Step 5, §4 traceability, §5). **Both sharpenings folded** (TEST-DDL under `tests/` + banner "test-harness not production prescription" — Step 9; `Authorizer.authorize(user_id, rbac_action)` param named distinctly from `CommittedDecision.action` — Step 3). **Memo-hash-verification carry-forward recorded** in the Deferred Decisions register (→ `memo-agent-core`). On the user's go → Part 2 (tests-first, leaf-first, 12 steps) → Code-Gen 2-option gate. **Then `audit-store` = THIRD fully-complete unit; `memo-agent-core` (LAST cluster unit) follows.** Do NOT write code until the user reviews the diff + gives the go. On the filled answers → ambiguity-check → Part 2 (Generation, tests-first, leaf-first) → Code-Gen 2-option gate. **Then `audit-store` becomes the THIRD fully-complete unit; the LAST cluster unit `memo-agent-core` follows** (FD approved; NFR/Code-Gen not started). **Carry-forward recorded in the Deferred Decisions register**: the `database` unit must co-locate audit-store's tables in one Postgres DB/connection (ATOMIC-1) + author the `audit_writer`/`audit_reader` grants. Do NOT write code until the answers are in and checked. The named audit-store Code-Gen spot-check files remain: `DecisionCommitService` (CON-BR4 predicate) + `ReplayService` (replay projection excluding engine_version/content_hash forensic fields). Then NFR Design → [Infra likely SKIP] → Code-Gen (per-unit). The named audit-store Code-Gen spot-check files remain: `DecisionCommitService` (CON-BR4 predicate) + `ReplayService` (replay projection excluding engine_version/content_hash forensic fields). **Named audit-store critical spot-check files (for its Code-Gen):** `DecisionCommitService` (CON-BR4 commit predicate — reject iff underwriter_id missing OR action missing OR override-with-blank-reason; append-only enforcement + derived superseded-ness) and `ReplayService` (loads the ApplicantProfileSnapshot, calls rules-engine `evaluate()`, compares the evaluation-output projection **excluding** `engine_version`/`content_hash` forensic fields). Stop-before-generate discipline continues (Part-1 plan + `[Answer]` tags → ambiguity-check → Part-2 on explicit go).
- **Status**: requirements.md APPROVED 2026-06-17. User Stories APPROVED at gate 2026-06-18. Workflow Planning APPROVED at the gate 2026-06-18 ("Approve & Continue"). Application Design APPROVED at the completion gate 2026-06-29. **Units Generation APPROVED at the completion gate 2026-07-02** — three artifacts (`unit-of-work.md`, `unit-of-work-dependency.md`, `unit-of-work-story-map.md`) generated + review-corrected: 23-unit decomposition (Q1..Q6 = A + F1–F5 resolutions; `ui-shell` owns US-UI-7; `auth-rbac` one shared unit; grouped `outlier-model`/`memo-extensions`; `audit-store` = decision-commit+audit+replay boundary owning DecisionCommitService; `database` story-less infra), story-map proving **40/40 stories assigned exactly once** (per-epic 4/5/3/7/7/12/2; 30 P1 / 10 P2), dependency matrix consistent with `component-dependency.md` (document-sanitizer mid-pipeline edge pinned; phase-safe, no P1→P2 back-edge), binding invariants single-sourced. **DISCOVER phase complete — no stages remaining.**

## Open Items Carried Into Application Design
1. **Per-unit depth "lighter" classifications are RECOMMENDATIONS, not a locked floor** — the execution-plan's per-unit "lighter" depth notes (e.g. `secrets-config`, `admin-cli`, `deploy-config`, display-only `ui-queue`/`ui-history`/`ui-memo-view`) are revisitable per-unit at each BUILD design stage; any such unit can be given comprehensive depth when its design stage is reached, without amending execution-plan.md. (Invariant-bearing UI — `ui-approval-gate`, `ui-override-form` — remain comprehensive per FR-UI-2 / CON-BR4 / FR-UI-4.)
2. **Provisional-unit overlap to resolve at Units Generation**: `ui-auth-rbac` (C5 / EPIC-5) vs `auth-rbac` (EPIC-6) — confirm whether RBAC is one shared unit or two. Record/surface in Application Design; the definitive boundary call is made at Units Generation.

## Open Items Carried Into Workflow Planning (closed)
- *(none open — the REFER human-approval-gate item was **RESOLVED 2026-06-18** and moved to Resolved Decisions above. Synthetic-corpus generation timing remains a deferred item under Deferred Decisions, not an open blocker.)*

## Open Items Carried Into BUILD Phase (surfaced at DISCOVER→BUILD boundary; not yet acted on)
1. **Per-unit "lighter" depth = revisitable recommendation, NOT a locked floor.** The per-unit depth classifications in `unit-of-work.md §4` / `execution-plan.md §3` can be raised to comprehensive when a unit's BUILD design stage is reached, without amending those docs. **Invariant-bearing units stay comprehensive regardless**: `ui-approval-gate`, `ui-override-form` (FR-UI-2 / CON-BR4 / FR-UI-4), and the deterministic-core + quality units (`intake`, `document-sanitizer`, `rules-engine`, `outlier-model`, `memo-agent-core`, `auth-rbac`, `audit-store`, `quality-gates`).
2. **Functional Design is the altitude drop from interfaces to internals.** It is where the deferred detail finally gets designed: **field-by-field schema** (`ApplicantProfile`, `RuleResultReport`, `DecisionMemo`, audit 6-tuple), **rule thresholds** (age 18/65, BMI 25/30, DTI ≤40%, income multiples, etc.), and the **reserved Phase-3 seam field definitions** `decision_id` / `status` (active/superseded) / nullable `supersedes_decision_id` (OOS-7 amendment seam) + `engine_version` capture (OOS-8). Application Design deliberately held these at interface altitude; Functional Design lowers it to internals.
## BUILD Per-Unit Loop — `admin-cli` (U17) NFR Design COMPLETE (Part 2 generated; awaiting 2-option gate) — 2026-07-08
- **Loop position**: `admin-cli` (U17) — FD ✅ · NFR Requirements ✅ APPROVED · **NFR Design ✅ Part 2 GENERATED, STOPPED at the 2-option completion gate** (1. Request Changes / 2. Continue → **Infrastructure Design**). Awaiting the user's review of both artifacts.
- **Four `[Answer]` tags**: all **A** (Q1 RoleGate distinct component composed+invoked-first before connect/begin; Q2 DB-constraint-driven atomic conflict/absence, no pre-SELECT; Q3 refuse-overwrite before write; Q4 one StructuralGuard in `tests/`).
- **Ambiguity-check (2026-07-08)**: **CLEAN** — three realization folds, no genuine gap, no STOP:
  - **ADMIN-NFRD-Fold-1 (check i)**: RoleGate ordering is **test-enforced** — the spy-engine asserts `connect()` and `begin()` are BOTH never called on a non-canonical role (a structural reorder-guard, beyond code review). Residual accepted lighter-tier limit: exercised over the two Phase-1 write methods.
  - **ADMIN-NFRD-Fold-2 (check ii)**: a generic "already exists" is **accurate for both** PK `user_id` and UNIQUE `subject`; distinguishing the constraint is an optional Code-Gen wording choice, not an NFR-Design gap.
  - **ADMIN-NFRD-Fold-3 (check iii)**: publish check-then-write **TOCTOU eliminated** by realizing the no-overwrite guard as **atomic exclusive-create** (`open(path,"x")` / `O_CREAT|O_EXCL`) — byte-identical existing file (PUBLISH-1(b)); single-operator out-of-band scope stated but not relied on for safety.
- **Artifacts** (`guide-docs/build/admin-cli/nfr-design/`): `nfr-design-patterns.md` (P1–P6, pattern-integration Mermaid + text alt, traceability no-orphan, Security-Guardrails no-blocking-finding) · `logical-components.md` (C1–C6, reference-not-own across all four surfaces verified on disk, component→target coverage no-orphan, component-relationship Mermaid + text alt with **RoleGate-before-connection a visible edge** — the connection node's only inbound edge is C3). Plan `admin-cli-nfr-design-plan.md` re-saved (§8A + folds + §10 done-state).
- **Guardrails held**: NO code; no dependency edited; no LLM run; **WIRE-1 untouched; tier-B NOT authorized; no other unit started.**

## BUILD Per-Unit Loop — `admin-cli` (U17) Infrastructure Design SKIPPED (logged); NEXT = Code Generation — 2026-07-08
- **Infrastructure Design line**: **SKIPPED (logged, explicit rule justification)** — `admin-cli` is CLI-wiring + two invariant-bearing mutations (C1–C6) with **no independent infra topology it designs**. Four-point justification: (1) no untrusted parsing / no sandbox (operator-authored rulebook YAML via rules-engine `build_rulebook`'s `yaml.safe_load` + argparse args; no pdfplumber/subprocess); (2) no persistence provisioned (writes to database's **existing** `app_user` + rules-engine's **existing** `rulebook/` dir; no new store, no migration — the test-only `app_user` is CI test-substrate, ADMIN-NFR-Fold-3); (3) no LLM/provider access (BR-ADMIN-8); (4) no deployed service / no network surface (local out-of-band CLI; injected Engine/`DATABASE_URL` is secrets-config's **existing** composition-root wiring, SEC-3; testcontainers `postgres:16` already-present test substrate, D7). Satisfies CLAUDE.md "Skip IF: No infrastructure changes / Infrastructure already defined" + execution-plan §3 "little independent infra".
- **Skip roster**: `admin-cli` joins the nine prior Infrastructure-Design SKIPs (intake / rules-engine / audit-store / memo-agent-core / auth-rbac / secrets-config / ui-shell / corpus-generator / quality-gates); `database` remains the one real non-skip (owns schema/migrations).
- **Loop position**: `admin-cli` (U17) — FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure Design ⏭️ SKIPPED (logged)** → **STOPPED at the Infra 2-option gate; NEXT = Code Generation (the LAST stage for admin-cli)**. Code Generation is Part-1-plan-then-Part-2-generate with its own approval — no code until the user reviews the plan.
- **Guardrails held**: NO infra artifact; NO code; no dependency edited; **WIRE-1 untouched; tier-B NOT authorized; no other unit started.**

## BUILD Per-Unit Loop — `admin-cli` (U17) Code Generation Part 1 (Plan) WRITTEN; STOP at plan gate (NO CODE) — 2026-07-08
- **Loop position**: `admin-cli` (U17) — FD ✅ · NFR Requirements ✅ · NFR Design ✅ · Infrastructure Design ⏭️ SKIPPED (logged) · **Code Generation Part 1 (Plan) WRITTEN → STOPPED at the plan gate awaiting filled `[Answer]` tags + review**. This is the **last** stage for admin-cli.
- **Plan file**: `guide-docs/build/plans/admin-cli-code-gen-plan.md` — §1 component→module map (C5 `exceptions.py` / C3 `role_gate.py` / C2 `rulebook_publisher.py` / C4 `app_user_writer.py` counted + `pg_writer.py` omitted / C1 `cli.py` counted + `__main__.py` omitted / C6 `tests/test_reference_not_own.py` AST guard; + `__init__`/`conftest` scaffolding under `backend/admin_cli/`); §2 TDD test→target map (all ten NFR-ADMIN-* at NFR-pinned tiers); §3 leaf-first build order C5→C3→C2→C4→C1→C6→coverage gate; §4 HOLDS restated; §5 QA-6 ≥90% (`--cov=backend/admin_cli`; omit `*/admin_cli/pg_writer.py` + `*/admin_cli/__main__.py`; baseline **828 passed / 3 skipped** no-regression; ui-shell frontend untouched); §6 **SIX open `[Answer]` tags** (Q1 argparse subparser structure; Q2 atomic exclusive-create `open(path,"x")` vs `os.open`; Q3 composition-root Engine construction for `python -m backend.admin_cli`; Q4 stderr/status wording; Q5 test-only `app_user` DDL; Q6 AppUserWriter/pg_writer split); §7 holds; §8 STOP.
- **Guardrails held**: NO code generated; NO file under `backend/admin_cli/` created; ambiguity-check NOT yet run (runs after answers filled); no dependency edited; **WIRE-1 untouched; tier-B NOT authorized; no other unit started.**
- **Next**: user fills the six `[Answer]` tags → ambiguity-check on explicit go → Part 2 (TDD code, test-first, per the build order) → Code-Gen 2-option gate.

## BUILD Per-Unit Loop — `admin-cli` (U17) Code Generation Part 2 GENERATED + TESTED; STOP at Code-Gen 2-option gate — 2026-07-08
- **Loop position**: `admin-cli` (U17) — FD ✅ · NFR Requirements ✅ · NFR Design ✅ · Infrastructure Design ⏭️ SKIPPED (logged) · **Code Generation ✅ Part 2 GENERATED + TESTED → STOPPED at the 2-option completion gate**. This was the LAST stage for admin-cli; the per-unit loop for U17 is complete pending gate approval.
- **Six `[Answer]` tags**: all **A** (Q1 argparse 3 subparsers + injection-pure main; Q2 `open(path,"x")` exclusive-create; Q3 `__main__.py` composition root, secrets_config/create_engine scan-allowlisted to that file only; Q4 fixed names-only message table; Q5 harness `app_user` DDL user_id PK / subject NOT NULL UNIQUE / role open no-CHECK; Q6 separate omitted `pg_writer.py` composed by `AppUserWriter`).
- **Ambiguity-check (2026-07-08)**: **CLEAN** — three folds: ADMIN-CG-Fold-1 (per-file allowlist enforceable, proven by a self-test) · ADMIN-CG-Fold-2 (`build_rulebook` messages verified safe to interpolate — no credential/URL/path) · ADMIN-CG-Fold-3 (harness `subject NOT NULL UNIQUE` required, not redundant — CREATE-1(b) teeth depend on it; asserts admin-cli's catch, not database's schema).
- **Delivered** (`backend/admin_cli/`): `exceptions.py` / `role_gate.py` / `rulebook_publisher.py` / `app_user_writer.py` (counted) + `pg_writer.py` (omitted) / `cli.py` (counted) + `__main__.py` (omitted) / `tests/` (8 test modules + conftest). `pyproject.toml`: `--cov=backend/admin_cli` + omit `*/admin_cli/pg_writer.py` + `*/admin_cli/__main__.py`.
- **Results**: admin-cli **49 passed / 6 integration-skipped** (Docker-gated, run in CI); full backend suite **850 passed / 31 skipped**; **coverage 99.82% ≥ 90% (QA-6 PASSED)**; admin-cli counted modules **all 100%**. 5 pre-existing `audit_store` Docker-absence errors (NOT a regression — that fixture lacks the `_docker_available()` guard; passes in CI). ui-shell frontend untouched.
- **Artifacts**: `guide-docs/build/admin-cli/code/code-summary.md`, `testresults.txt`, plan re-saved (§6A + folds + §8 done-state).
- **Guardrails held**: no edit to the four consumed surfaces (rules-engine/auth-rbac/database/secrets-config); RoleGate distinct + invoked-first, spy-enforced; no schema/CHECK on app_user; zero secret VALUES; no LLM/rule-eval/commit import; provider-config absent; **WIRE-1 untouched; tier-B NOT authorized; no other unit started.**

## ✅ `admin-cli` (U17) COMPLETE — the ELEVENTH fully-complete build-loop unit — 2026-07-08
**Top status**: BUILD IN PROGRESS · **11 build-loop units COMPLETE** (intake [+document-sanitizer co-built], rules-engine, memo-agent-core, auth-rbac, audit-store, quality-gates, corpus-generator, database, secrets-config, ui-shell, **admin-cli**). admin-cli is the ELEVENTH.

**`admin-cli` (U17) — COMPLETE**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · **Code Generation ✓** (Part 2 generated + tested; six answers all A; ambiguity-check CLEAN — ADMIN-CG-Fold-1/2/3). **admin-cli 49 tests (43 tier-U pass + 6 integration Docker-gated) / counted modules 100%** (`exceptions`/`role_gate`/`rulebook_publisher`/`app_user_writer`/`cli`; `pg_writer.py`+`__main__.py` omitted). **Full backend suite: 850 passed / 31 skipped / coverage 99.82% ≥ 90% (QA-6 PASSED)**. ui-shell frontend untouched.

**Known non-regression issue (pre-existing, unrelated to admin-cli)**: 5 errors in `audit_store/tests/test_pg_integration.py` — that unit's integration fixture lacks the `_docker_available()` skip-guard used by auth-rbac/database/admin-cli, so it ERRORS (instead of skipping) when Docker is absent locally; passes in CI. Small, low-risk hygiene fix (add the guard) — NOT a new unit, NOT caused by admin-cli.

**P1 roster status (17 P1 units, units 1–17 of the 23-unit decomposition)**:
- **Non-UI P1 (11) — ALL COMPLETE**: intake, document-sanitizer (co-built in intake), rules-engine, memo-agent-core, auth-rbac, audit-store, quality-gates, corpus-generator, database, secrets-config, admin-cli. (The "6 EPIC-6 platform P1 units" = audit-store/corpus-generator/database/secrets-config/admin-cli/quality-gates — a subset, all now complete.)
- **UI P1 (6)**: ui-shell ✓ complete; **ui-queue / ui-memo-view / ui-approval-gate / ui-override-form / ui-history = the 5 REMAINING P1 units — all BLOCKED on WIRE-1.**
- **P2 (6, units 18–23)**: outlier-model, memo-extensions, ui-outlier-view, observability, llm-judge, deploy-config — all deferred (all P1 before any P2).

**Cross-unit / Deferred Decisions register (unchanged by this unit)**:
- **WIRE-1 — OPEN.** The frontend↔backend api-contract; **HARD checkpoint — MUST be authored + pinned BEFORE `ui-queue`'s FD** (and the other 4 UI views). It is a **cross-unit contract artifact, NOT a per-unit-loop unit**. Untouched.
- **tier-B corpus run — UNAUTHORIZED / out of scope** (corpus-generator's out-of-band real-LLM full-corpus build; needs explicit user authorization).
- **audit_store Docker-guard gap** — the pre-existing hygiene issue above (add `_docker_available()` to `audit_store/tests/test_pg_integration.py`).

**Next move (user decides separately)**: (a) author WIRE-1 to unblock the 5-unit UI cluster, OR (b) fix the audit_store Docker-guard gap first. STARTED NOTHING.

## 🔗 WIRE-1 (frontend↔backend api-contract) — AUTHORED + PINNED — 2026-07-08 (Deferred Decisions register update)
**WIRE-1 status: OPEN → ✅ PINNED.** Artifact: `guide-docs/build/wire-1/api-contract.md` (a cross-unit contract artifact, NOT a per-unit-loop unit). Authored via a single lightweight contract-design pass (plan → 6 answers all A → ambiguity-check CLEAN → artifact); six answers: narrative markdown / plain REST-JSON / bare bodies + list wrapper + error envelope / offset-limit pagination / error body + status table / GET /session role delivery.
- **Covers the four scope items**: (1) route list R1–R7 (GET /session; GET /applications [queue]; GET /applications/{id}; GET /applications/{id}/memo [MemoView]; POST /recommendations/{recommendation_id}/commit [underwriter-only RBAC_COMMIT]; GET /decisions [history]; GET /decisions/{decision_id}); (2) response envelope (bare + `{items,page}` list wrapper); (3) error envelope `{error:{code,message,detail?}}` + status table 400/401/403/404/409/422/500; (4) Role delivery `GET /session {user_id, role}` (lowercase, no re-case).
- **Frozen enum wire map preserved (not remapped/re-cased)**: Recommendation UPPERCASE `APPROVE/REFER/DECLINE-RECOMMEND` · Confidence Title-case `High/Medium/Low` · Role lowercase `underwriter/auditor/admin` · CommitAction lowercase `approve/override` (distinct namespace). Grounded in the five built response shapes (ApplicantProfile / RuleResultReport / DecisionMemo three-region / AuditRecord+CommittedDecision / Role) **plus a sixth added by the 2026-07-17 additive amendment (U18 `OutlierResult`, on R4 — see WIRE1-Fold-4 below)**.
- **Ambiguity-check CLEAN — 3 folds**: WIRE1-Fold-1 (commit body explicit `{action, reason?}` — reason required-iff-override per BR-COMMIT-GATE; `underwriter_id` from the authenticated session, not the body — AUTHZ-1); WIRE1-Fold-2 (R4 MemoView `status: ready|pending` gives ui-memo-view a defined render state; sync-vs-async deferred to Build & Test); WIRE1-Fold-3 (Content-Type application/json in scope; CORS → deploy-config P2; auth-handshake an abstract deferred seam).
- **➕ Additive amendment 2026-07-17 (WIRE1-Fold-4, approved) — still the SAME pin, not a new version**: R4 `MemoView` gained an additive `outlier: OutlierResult | null` field (U18 `OutlierResult` **by value**; `null` in Phase 1 / when `status: pending`; populated only for a Phase-2 `ready` view) + a fifth §1 by-value enum `FlagDirection` (`high`/`low`), closing U20 `ui-outlier-view`'s prerequisite wire-surface gap via option (a) over a new-route (b). R1–R7 route table / envelope / error shape / role delivery byte-unchanged; advisory-only preserved (OutlierResult has no verdict field); no frozen P1 unit edited. **Implementation reconciliation deferred** — R4 is a `501` stub in the closed composition root (part of the R2–R5-unwired item); `backend/app/` NOT touched.
- **Deferred (named-not-designed)**: actual route implementation `backend/app/main.py` → Build & Test integration (unit-of-work.md §2, not a 24th unit); CORS origin allowlisting + auth-handshake mechanism → deploy-config (P2) / abstract seam.

**Register now**: WIRE-1 ✅ PINNED (unblocks the 5 UI view units). tier-B corpus run — still UNAUTHORIZED. audit_store Docker-guard hygiene gap — still open (deprioritized, non-blocking).

**Unblocked**: `ui-queue` / `ui-memo-view` / `ui-approval-gate` / `ui-override-form` / `ui-history` — their per-unit BUILD loop (starting with `ui-queue`'s FD) MAY now begin (the WIRE-1 hard checkpoint is satisfied). None started yet — awaiting the user's 2-option gate decision.

## 🧩 BUILD → `ui-queue` (U5) — Functional Design COMPLETE (three artifacts generated); STOP at FD 2-option gate — 2026-07-09
**Working sequence adopted** (sequencing choice, not matrix-forced — zero inter-UI-view edges): `ui-queue` → `ui-memo-view` → `ui-approval-gate` → `ui-override-form` → `ui-history` (revisitable).

**`ui-queue` (U5) status**: DISCOVER-carryover CLEAN → FD Part 1 plan (`guide-docs/build/plans/ui-queue-functional-design-plan.md`, Q1–Q7 all A, ambiguity-check 2 folds) APPROVED → **FD Part 2 COMPLETE** — three artifacts generated under `guide-docs/build/ui-queue/functional-design/`:
- **domain-entities.md** — component/prop inventory (QueueView / QueueStateView / QueueTable / QueueRow / PaginationControls, local per Q2-A), consumed ApplicationSummary + list/error shapes, four-state render enum, `onSelect(application_id)` event, full `queue-<element>-<purpose>` data-testid inventory (Fold-A).
- **business-rules.md** — BR-QUEUE-1..9 (copy-only labels / pending placeholder / error message-only+code-via-testid / Retry last-requested-page / selection-only / view-only-no-RoleGate / Recommendation-not-CommitAction namespace / testid convention / pagination boundaries).
- **business-logic-model.md** — fetch/render state machine (loading→ready|empty|error; error--Retry-->loading) with a validated Mermaid flowchart + text alternative; pagination flow over the R2 `page` wrapper; selection-emission flow. *(Correction 2026-07-09: §1 Mermaid labels rewritten to the project's label-validation convention — alphanumeric+spaces only, all double-quoted, no hyphens/commas/colons/semicolons/parens; re-validated against the 7 rules; text alternative in sync. Only the diagram block changed; the other two FD artifacts untouched.)*

**Depth**: lighter (display) **+ async-state addendum** (confirmed Q1=A) — no bump to comprehensive (that tier stays U7/U8). **Folds accepted as-is**: Fold-A (data-testid convention) · Fold-B (Retry re-fetches last-requested page, position-preserving). No dedicated `frontend-components.md` (hierarchy folded into domain-entities, matching ui-shell FD).

**Guardrails held**: NO application code (`frontend/src/queue/` not created); **WIRE-1 untouched** (R2 + ApplicationSummary + envelopes consumed by shape); **ui-shell (frozen, U10) untouched** — list/table kept local (Q2-A), no promotion; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**Cross-unit / Deferred Decisions register (current)**: **WIRE-1 ✅ PINNED** (`guide-docs/build/wire-1/api-contract.md`); **tier-B corpus run — UNAUTHORIZED**; **audit_store Docker-guard gap — DEFERRED** (non-blocking hygiene). ui-shell ✓ complete; ui-queue FD complete (NFR-Requirements next, pending gate); ui-memo-view / ui-approval-gate / ui-override-form / ui-history not started.

**STOPPED** at the FD 2-option completion gate (1. Request Changes / 2. Continue → NFR Requirements) — did NOT advance. Awaiting the user's review of the three artifacts.

## 🧩 BUILD → `ui-queue` (U5) — FD APPROVED; NFR Requirements Part 1 (Plan) WRITTEN; STOP at plan gate — 2026-07-09
**FD**: ✅ APPROVED at the 2-option gate (three artifacts + convention-corrected Mermaid). **Stage now**: NFR Requirements (per-unit), **Part 1 (Plan) complete**, Part 2 pending.

**NFR-Req Part 1 plan**: `guide-docs/build/plans/ui-queue-nfr-requirements-plan.md` — draft **NFR-QUEUE-\*** target map **T1–T13** mapping **BR-QUEUE-1..9** (+ NOTS/FETCH/PERF/A11Y) to **pass/fail** targets at the inherited tier convention (**Vitest + RTL + jsdom**, ESLint over the single `FORBIDDEN_TERMS`, file/import scan; **R2 mocked via a capturing/injected fetch double** — ui-queue is the first UI unit to actually fetch). No orphaned FD rule. SIX open **[Answer]** questions surfaced (Q1 fetch-double construction / Q2 loading-state assertions / Q3 dedicated state-transition test / Q4 SELECT-1 no-nav mechanism / Q5 PER-1 gating-vs-observed / Q6 a11y rigor) + Security-Guardrails applicability preview (read-only view: most N/A; least-privilege-UI-framing Compliant).

**Guardrails held**: NO NFR artifact generated (`nfr-requirements.md` / `tech-stack-decisions.md` not written); frozen FD not re-opened; NO code/test; **WIRE-1 untouched** (R2 by shape, mocked); **ui-shell (frozen) untouched** (tier convention + `FORBIDDEN_TERMS`/ESLint reused, not modified); tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the NFR-Requirements plan-file gate awaiting the user's confirmation + Q1–Q6 answers before Part 2 generation.

## 🧩 BUILD → `ui-queue` (U5) — NFR Requirements COMPLETE (two artifacts); STOP at NFR 2-option gate — 2026-07-09
**NFR-Req Part 1**: plan approved, Q1–Q6 answered (all A) + embedded. **Ambiguity-check CLEAN** — NFR-QUEUE-Fold-1 (ONE injected/capturing fetch-double serves every state/transition test; "capturing" is a superset feature, not a second construction → no divergent double patterns).

**NFR-Req Part 2 COMPLETE** — two artifacts under `guide-docs/build/ui-queue/nfr-requirements/`:
- **nfr-requirements.md** — finalized **NFR-QUEUE-\*** targets (FULL: COPY-1/PENDING-1/ERROR-1/RETRY-1/SELECT-1/VIEWONLY-1/TESTID-1/NOTS-1/FETCH-1/PAGINATION-1 · MEDIUM: NAMESPACE-1 · SOFT: PERF-1/A11Y-1 · GOVERNANCE: SCOPE-1), each Assertion+Acceptance+Tier+Rigor with Q1–Q6 folded in; traceability table (no orphaned BR-QUEUE rule); **full Security-Guardrails compliance table** (read-only view — most N/A/referenced; error-hygiene + least-privilege-UI-framing Compliant; no blocking finding).
- **tech-stack-decisions.md** — D1–D10: **inherited** React+Tailwind/no-TS/Vitest+RTL+jsdom/ESLint-over-`FORBIDDEN_TERMS`/file-import-scan; **NEW** D6 injected/capturing R2 fetch-double (Fold-1), D7 state-mechanics deferred to Code-Gen (Fold-B), D9 deferred display values (skeleton count / page `size` / token values); bundler+Vercel → `deploy-config` P2; R2 route impl → Build & Test.

**Depth**: lighter (display) + async-state addendum. **Test tier**: Vitest + RTL + jsdom, no live backend (R2 doubled).

**Guardrails held**: NO application/test code; frozen FD not re-opened; **WIRE-1 untouched** (R2 by shape, mocked); **ui-shell (frozen) untouched** — Vitest/RTL/ESLint/`FORBIDDEN_TERMS`/testid mechanisms **reused, not modified**; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**Register (current)**: WIRE-1 ✅ PINNED · tier-B UNAUTHORIZED · audit_store Docker-guard gap DEFERRED. ui-shell ✓ complete; ui-queue FD ✓ + NFR-Requirements ✓ (**NFR Design next**, pending gate); other four UI views not started.

**STOPPED** at the NFR Requirements 2-option completion gate (1. Request Changes / 2. Continue → NFR Design) — did NOT advance. Awaiting the user's review of both artifacts.

## 🧩 BUILD → `ui-queue` (U5) — NFR Requirements APPROVED; NFR Design Part 1 (Plan) WRITTEN; STOP at plan gate — 2026-07-09
**NFR Requirements**: ✅ APPROVED at the 2-option gate. **Stage now**: NFR Design (per-unit), **Part 1 (Plan) complete**, Part 2 pending.

**NFR-Design Part 1 plan**: `guide-docs/build/plans/ui-queue-nfr-design-plan.md` — draft **pattern map P1–P10** mapping the fourteen **NFR-QUEUE-\*** targets to named patterns (SharedForbiddenTermsReuse / NullRowPlaceholder / ErrorEnvelopeToRender / FetchSeam / FourStateMachine / EmissionOnlyEvent / RoleInvariantRendering / DerivedStatePagination / StructuralGuard / ReferencedObservedBoundary) + **logical components C1–C7** (QueueView / FetchSeam / QueueStateView / QueueTable / QueueRow / PaginationControls / StructuralGuard); reference-not-own check; component→target coverage (no orphan); **validated component-relationship Mermaid** (7-rule convention). FOUR open **[Answer]** questions (Q1 FetchSeam shape / Q2 state-machine component-vs-responsibility / Q3 StructuralGuard granularity / Q4 error uniform-vs-401).

**Guardrails held**: NO NFR-Design artifact generated (`nfr-design-patterns.md` / `logical-components.md` not written); frozen FD + approved NFR Requirements not re-opened; NO code/test; **WIRE-1 untouched** (R2 by shape; real FetchSeam wiring deferred to composition root / Build & Test); **ui-shell (frozen) untouched** (copy/`FORBIDDEN_TERMS`/`RoleContext`/testid reused, not modified); tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the NFR-Design plan-file gate awaiting the user's confirmation + Q1–Q4 answers before Part 2 generation.

## 🧩 BUILD → `ui-queue` (U5) — NFR Design COMPLETE (two artifacts); STOP at NFR-Design 2-option gate — 2026-07-09
**NFR-Design Part 1**: plan approved, Q1–Q4 answered (all A) + embedded. **Ambiguity-check CLEAN** — NFR-QUEUE-D-Fold-1 (`fetchSeam` is a duck-typed injected seam, **no formal Protocol/interface** — admin-cli injected-`Engine` precedent; no-TS React makes it a fortiori; JSDoc + capturing double self-document the contract; prop-vs-Context → Code-Gen).

**NFR-Design Part 2 COMPLETE** — two artifacts under `guide-docs/build/ui-queue/nfr-design/`:
- **nfr-design-patterns.md** — patterns **P1–P10** (SharedForbiddenTermsReuse / NullRowPlaceholder / ErrorEnvelopeToRender / FetchSeam / FourStateMachine / EmissionOnlyEvent / RoleInvariantRendering / DerivedStatePagination / StructuralGuard / ReferencedObservedBoundary), each meeting its `NFR-QUEUE-*` target(s) + tier with Q1–Q4 folded in; **validated pattern-integration Mermaid** + text alt; pattern→target→tier→rigor traceability (no orphan).
- **logical-components.md** — components **C1–C7** (QueueView / fetchSeam distinct-module / QueueStateView / QueueTable / QueueRow / PaginationControls + StructuralGuard substrate); **validated component-relationship Mermaid** + text alt; reference-not-own check; component→target coverage (all 14, no orphan); settled items held.

**Key decisions folded**: Q1-A fetchSeam = distinct injected/capturing module · Q2-A four-state machine = QueueView responsibility (mechanics → Code-Gen, Fold-B) · Q3-A one StructuralGuard substrate · Q4-A uniform error incl. 401 (auth-handshake deferred).

**Guardrails held**: NO application/test code; frozen FD + approved NFR Requirements not re-opened; **WIRE-1 untouched** (R2 by shape; real fetchSeam wiring deferred to composition root / Build & Test); **ui-shell (frozen) untouched** (copy/`FORBIDDEN_TERMS`/`RoleContext`/testid reused, not modified); tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**Register (current)**: WIRE-1 ✅ PINNED · tier-B UNAUTHORIZED · audit_store Docker-guard gap DEFERRED. ui-shell ✓ complete; ui-queue FD ✓ + NFR-Requirements ✓ + NFR-Design ✓ (**Infrastructure Design next**, pending gate — likely a logged SKIP per precedent); other four UI views not started.

**STOPPED** at the NFR Design 2-option completion gate (1. Request Changes / 2. Continue → Infrastructure Design) — did NOT advance. Awaiting the user's review of both artifacts.

## 🧩 BUILD → `ui-queue` (U5) — NFR Design APPROVED; Infrastructure Design SKIPPED (logged); STOP at Infra 2-option gate; NEXT = Code Generation — 2026-07-09
**NFR Design**: ✅ APPROVED at the 2-option gate.

- **Infrastructure Design line**: **SKIPPED (logged, explicit rule justification)** — `ui-queue` is a **source-level React view** (C1–C7: QueueView / fetchSeam / QueueStateView / QueueTable / QueueRow / PaginationControls / StructuralGuard) with **no independent cloud topology it designs**. Four-point justification: (1) **no untrusted parsing / no sandbox** — renders WIRE-1 R2 JSON (mocked in tests via the injected `fetchSeam`); no pdfplumber/subprocess/file parsing; (2) **no persistence provisioned** — fetches R2 through the `fetchSeam`, never touches a database directly; no new store, no migration; (3) **no LLM/provider access** whatsoever; (4) **no deployed service / no network topology it owns** — bundler/dev-server + Vercel deploy topology is `deploy-config`'s (P2), and the **real `fetchSeam` wiring + R2 route implementation** (`backend/app/main.py`) are the composition root's / Build & Test's concern, not provisioned here. Satisfies CLAUDE.md "Skip IF: No infrastructure changes / Infrastructure already defined" + execution-plan §3 "little independent infra". Ambiguity-check surfaced **no genuine ui-queue-owned infra concern**.
- **Skip roster**: `ui-queue` joins the ten prior Infrastructure-Design SKIPs (intake / rules-engine / audit-store / memo-agent-core / auth-rbac / secrets-config / ui-shell / corpus-generator / quality-gates / admin-cli) — **eleven** now; `database` remains the one real non-skip (owns schema/migrations). Consistent with `ui-shell` (the prior React unit) SKIP.
- **Loop position**: `ui-queue` (U5) — FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure Design ⏭️ SKIPPED (logged)** → **STOPPED at the Infra 2-option gate; NEXT = Code Generation (the LAST stage for ui-queue)**. Code Generation is Part-1-plan-then-Part-2-generate with its own approval — no code until the user reviews the plan.
- **Guardrails held**: NO infra artifact (`guide-docs/build/ui-queue/infrastructure-design/` not created); NO code; no dependency edited; **WIRE-1 untouched; ui-shell (frozen) untouched; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.**

## 🧩 BUILD → `ui-queue` (U5) — Infra SKIP accepted; Code Generation Part 1 (Plan) WRITTEN; STOP at plan gate — 2026-07-09
**Loop position**: `ui-queue` (U5) — FD ✅ · NFR Requirements ✅ · NFR Design ✅ · Infrastructure Design ⏭️ SKIPPED (logged) · **Code Generation Part 1 (Plan) WRITTEN → STOPPED at the plan gate awaiting filled `[Answer]` tags + review**. This is the **LAST** stage for ui-queue.

**Code-Gen Part 1 plan**: `guide-docs/build/plans/ui-queue-code-gen-plan.md` — component→module map **C1–C7 → `frontend/src/queue/`** files (`fetchSeam.js`; `components/PaginationControls|QueueStateView|QueueRow|QueueTable.jsx`; `QueueView.jsx`; C7 test-only substrate), tests in `queue/__tests__/`, **no `src/shell/` file created/modified**; full **TDD test→target map** (all 14 `NFR-QUEUE-*` at pinned tier); **leaf-first Steps 1–10** (config-extension → fetchSeam → PaginationControls → QueueStateView → QueueRow → QueueTable → QueueView → StructuralGuard → coverage gate → code-summary); HOLDS restated; **coverage/quality gate** (Vitest folded into the frontend run — baseline ui-shell **100% / 47 tests**; `src/queue` QA-6 ≥90%; backend pytest **850 passed / 31 skipped** to remain untouched). SIX open **[Answer]** questions (Q1 skeleton markup / Q2 default page size / Q3 fetchSeam prop-vs-context / Q4 fetchSeam failure convention / Q5 transition-test file / Q6 shared-config extension without touching `src/shell`).

**Ambiguity-check**: NOT yet run — deferred until AFTER the answers are filled (per the user), then Part 2 on explicit go.

**Guardrails held**: NO code generated; NO file under `frontend/src/queue/` created; frozen FD + approved NFR-Req/NFR-Design not re-opened; **WIRE-1 untouched** (R2 by shape; real fetchSeam wiring deferred to composition root); **ui-shell (frozen) untouched** (reused via import only); tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the Code-Gen plan-file gate awaiting the user's Q1–Q6 answers + review before Part 2 (code generation).

## 🧩 BUILD → `ui-queue` (U5) — Code Generation Part 2 GENERATED + TESTED (98 passed, 100%); STOP at completion gate — 2026-07-09
**Loop position**: `ui-queue` (U5) — FD ✅ · NFR Requirements ✅ · NFR Design ✅ · Infrastructure Design ⏭️ SKIPPED (logged) · **Code Generation ✅ Part 2 GENERATED + TESTED → STOPPED at the 2-option completion gate**. This was the **LAST** stage for ui-queue; the per-unit loop for U5 is complete pending gate approval.

**Code-Gen Part 2**: Q1–Q6 answered (all A) + embedded; ambiguity-check CLEAN (**CG-Fold-1** — `fetchSeam` normalizes every failure to a well-formed `{error:{code,message,detail}}` envelope, so ERROR-1 never unpacks a raw exception; config extension added include paths only, thresholds unchanged). Generated under **`frontend/src/queue/`** (production): `QueueView.jsx`, `fetchSeam.js`, `copy.js`, `components/{PaginationControls,QueueStateView,QueueRow,QueueTable}.jsx`; shared-infra additions (Q6-A) `eslint-rules/queue.js` + `eslint.config.js`/`vitest.config.js` include-path extensions — **no `src/shell/` file created or edited**. 15 test files in `queue/__tests__/`.

**Result**: **98 Vitest tests passed** (22 files); **100% coverage** on `src/queue` (all files) — QA-6 ≥90% PASSED; `src/shell` stays **100% (untouched)**; **ESLint clean**. Backend pytest suite (**850 passed / 31 skipped / 99.82%**) **untouched** (no backend file modified; separate runner/tree; not re-run). Artifacts: `guide-docs/build/ui-queue/code/code-summary.md`; `testresults.txt` frontend section refreshed.

**Every `NFR-QUEUE-*` target tested at its pinned tier** (COPY/NAMESPACE lint+structural · PENDING/ERROR/PAGINATION/FETCH/VIEWONLY RTL · RETRY page-N teeth · SELECT/NOTS/PERF structural · TESTID lint+self-test · A11Y observed).

**Guardrails held**: ui-shell (frozen) untouched — reused via import only, no new word-list; no `RoleGate`; no router import; `fetchSeam` duck-typed (D-Fold-1); WIRE-1 R2 by shape only, no real network call (transport injected), real wiring deferred to composition root; no LLM; no TypeScript; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**Register (current)**: WIRE-1 ✅ PINNED · tier-B UNAUTHORIZED · audit_store Docker-guard gap DEFERRED. **P1 UI roster**: ui-shell ✓ · **ui-queue ✓ (pending gate)** · ui-memo-view / ui-approval-gate / ui-override-form / ui-history = the 4 REMAINING P1 UI units (not started).

**STOPPED** at the Code Generation 2-option completion gate (1. Request Changes / 2. Continue) — did NOT advance. Awaiting the user's review of the diffs. Next move (a separate decision): the next UI unit per the working sequence is `ui-memo-view`.

## ✅ BUILD → `ui-queue` (U5) COMPLETE (12th unit; 2nd UI-cluster) → `ui-memo-view` (U6) STARTED; FD Part 1 gate — 2026-07-09
**`ui-queue` (U5) — COMPLETE**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED (logged) · **Code Generation ✓** (98 Vitest tests / **100% coverage on `src/queue`**, ESLint clean; **`src/shell` remains 100% UNTOUCHED**; **CG-Fold-1** `normalizeError` guarantees every `fetchSeam` rejection is a well-formed `{error:{code,message,detail}}` envelope; backend pytest **850 passed / 31 skipped** UNTOUCHED). The **TWELFTH complete unit** and the **SECOND complete UI-cluster unit after `ui-shell`**.

**P1 roster (17 P1 units)** — **13 COMPLETE**: intake, document-sanitizer, rules-engine, memo-agent-core, auth-rbac, audit-store, quality-gates, corpus-generator, database, secrets-config, admin-cli (11 non-UI) + **ui-shell, ui-queue** (2 UI). **UI P1 remaining (4)**: ui-memo-view (in progress) / ui-approval-gate / ui-override-form / ui-history.

**`ui-memo-view` (U6) — STARTED** (working sequence: ui-queue → **ui-memo-view** → ui-approval-gate → ui-override-form → ui-history). DISCOVER-carryover **CLEAN** (no `guide-docs/build/ui-memo-view/` dir). Frozen surfaces re-read: ui-shell `ReadOnlyRegion` (built for the RO memo region) + primitives/copy/tokens/session; **ui-queue's fetchSeam + StructuralGuard convention** (established sibling pattern; ui-queue now frozen); **WIRE-1 R4 MemoView** `{application_id, recommendation_id|null, status: ready|pending, profile|null, report|null, memo|null}`; **memo-agent-core DecisionMemo** three regions (L `narrative_prose`+`cited_rule_ids` / D `missing_information[]{source,detail}` / RO `recommendation`+`confidence` injected read-only / M `memo_hash`+`model_version`) + **CON-BR2-TYPE** (LLM never produces recommendation/confidence). `MissingInfoSource` has **no** display labels in `shell/copy` (frozen).

**FD Part 1**: depth recommendation (lighter/display + fetch-lifecycle addendum + a NEW three-region read-only-separation concern per CON-BR2) + SIX open **[Answer]** questions (Q1 depth / Q2 status:pending full-page state / Q3 cited_rule_ids + missing_information list rendering / Q4 MissingInfoSource labels / Q5 ReadOnlyRegion composition + CON-BR2 attribution / Q6 R4 fetch-seam reuse-vs-local) presented for confirmation **before the plan is written**.

**Guardrails held**: NO plan/FD artifact generated; **WIRE-1 untouched · ui-shell (frozen) untouched · ui-queue (now frozen) untouched**; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** for the user to confirm depth + answer Q1–Q6 before the `ui-memo-view` FD Part 1 plan is written.

## 🧩 BUILD → `ui-memo-view` (U6) — FD Part 1 (Plan) WRITTEN; ambiguity-check CLEAN; STOP at plan gate — 2026-07-09
**FD Part 1**: depth confirmed **Q1=A** (lighter/display + fetch-lifecycle addendum + three-region read-only-separation addendum); **Q2–Q6 all A** + embedded. Plan: `guide-docs/build/plans/ui-memo-view-functional-design-plan.md`.

**Ambiguity-check CLEAN** — **MEMO-Fold-1**: ui-memo-view reuses the ONE `FORBIDDEN_TERMS` (shell no-inline-label + advisory-vocabulary registered on `src/memoView`, no new word-list); its memo-local copy module is lint-subject; the lints cover the view's STATIC code, while runtime `narrative_prose` advisory conformance stays memo-agent-core's backend concern (CON-BR2 there). **MEMO-Fold-2**: three-region separation adds `memo-region-*` testids (+ a `memo-testid-convention` rule mirroring ui-queue's) so a structural test can assert the RO region is a DISTINCT node from the L narrative (concrete CON-BR2 check). Notes: N1 `pending` derived from the R4 `status` discriminator (not `items.length`); N2 view-only, no RoleGate, no commit affordance (commit is U7); N3 recommendation/confidence render ONLY in the RO region.

**Answers folded**: Q2-A single page-level pending state · Q3-A local citation + missing-info lists · Q4-A `detail` primary + `source` via memo-local copy (not shell/copy) · Q5-A compose frozen `ReadOnlyRegion` (engine-attributed) · Q6-A own local memo fetchSeam (no ui-queue import).

**Guardrails held**: NO FD artifact generated; **WIRE-1 untouched · ui-shell (frozen) untouched · ui-queue (frozen) untouched** (its fetchSeam/StructuralGuard a convention, not imported); tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the FD Part 1 plan-file gate awaiting the user's review before Part 2 (the three FD artifacts).

## 🧩 BUILD → `ui-memo-view` (U6) — Functional Design Part 2 COMPLETE (three FD artifacts generated); STOP at FD 2-option gate — 2026-07-09
**FD Part 1 plan APPROVED** → **Part 2 generated** the three FD artifacts under `guide-docs/build/ui-memo-view/functional-design/`:
- **`domain-entities.md`** — location `frontend/src/memoView/` + composition boundary (imports ui-shell incl. **first-use `ReadOnlyRegion`**; does **not** import ui-queue — mirrors its convention); consumed **MemoView / DecisionMemo / MissingInformationItem / ApplicantProfile / error** shapes by value (`report` delivered but **not** a render source in this lighter view); **four-state render enum** `MEMO_STATE {LOADING, READY, PENDING, ERROR}` (pending **from the `status` discriminator**); component/prop inventory (`MemoView` stateful owner + injected `fetchSeam` · `MemoStateView` · `ProfileContextHeader` · `NarrativeRegion` + `CitationsList` · `MissingInfoRegion` · `ReadOnlyRecommendationRegion` composing frozen `ReadOnlyRegion` + badges; **no outward event** — contrast ui-queue `onSelect`); **memo-local copy module** (`MISSING_INFO_SOURCE_LABELS` + headings/chrome, lint-subject); full **`memo-<element>-<purpose>` data-testid inventory** incl. **region-level testids** (`memo-region-narrative`/`-citations`/`-missinginfo`/`-readonly` + `memo-recommendation`/`memo-confidence` + state testids).
- **`business-rules.md`** — **BR-MEMO-1..11**: copy-only labels (shell + memo-local, never inlined); **BR-MEMO-2** reuse the ONE `FORBIDDEN_TERMS` with the explicit **scope boundary** (static view code lint-subject **vs** runtime `narrative_prose` = memo-agent-core's CON-BR2 backend concern — view neither lints nor rewrites); **BR-MEMO-3** three-region structural separation (**RO a DISTINCT node from L narrative** — the concrete CON-BR2-TYPE check); **BR-MEMO-4** RO composes frozen `ReadOnlyRegion` engine-attributed; **BR-MEMO-5** recommendation/confidence render **ONLY** in RO; **BR-MEMO-6** error message-only/code-via-testid/detail-never + Retry re-fetch same `applicationId`; **BR-MEMO-7** view-only, no RoleGate/commit/router; **BR-MEMO-8** `status:pending` → page-level state derived from `status`; **BR-MEMO-9** deterministic `missing_information` + `cited_rule_ids` order preserved; **BR-MEMO-10** testid convention incl. region testids; **BR-MEMO-11** system `Recommendation` namespace never the human `CommitAction` (no bare `DECLINE`) + rule→source traceability.
- **`business-logic-model.md`** — **two validated Mermaid diagrams** (7-rule convention): §1 fetch/state machine with a **`status`-discriminator decision node** (pending explicitly status-derived, **not** `items.length`) + text alternative; §2 ready-state three-region composition with the **RO region shown as a distinct isolated node** (frozen `ReadOnlyRegion` → badges) + the structural-isolation invariant + text alternative; §3 read-only one-direction data-flow; §4 deferrals (fetch-hook mechanics / placeholder markup / R4 route impl / navigation).

**Both folds applied as-is**: MEMO-Fold-1 (FORBIDDEN_TERMS reuse + static-view-vs-runtime-narrative scope boundary); MEMO-Fold-2 (region-level testids for the CON-BR2 structural check).

**Guardrails held**: NO application code written; NO LLM; NO TypeScript; **WIRE-1 untouched · ui-shell (frozen) untouched** (consumed by import/shape) **· ui-queue (frozen) untouched** (fetchSeam/StructuralGuard mirrored as a convention, **not** imported); tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**Pre-gate correction (2026-07-09)**: `business-logic-model.md` §1 diagram converted from a decision-diamond (`DISCRIM`) to the project's **rectangle-only convention** — the two `status` branches now render as **direct labeled edges from the single `LOAD` node** (`LOAD -->|"status ready"| READY` / `LOAD -->|"status pending"| PENDING`); diamond dropped. 7 rules re-validated PASS; text alternative synced (Loading → Ready / Pending, status-branch; N1 pending-from-status semantics preserved). §2 diagram + `business-rules.md` + `domain-entities.md` untouched.

**FD APPROVED (2026-07-09)** → `ui-memo-view` FD stage COMPLETE (three artifacts + convention correction). Advanced to **NFR Requirements** (per-unit).

## 🧩 BUILD → `ui-memo-view` (U6) — NFR Requirements Part 1 (Plan) WRITTEN; 7 open [Answer] questions; STOP at plan gate — 2026-07-09
**Plan**: `guide-docs/build/plans/ui-memo-view-nfr-requirements-plan.md` — **Part 1 (Plan) only**, built ON the frozen FD (BR-MEMO-1..11 + inventory + four-state enum + testid inventory incl. region testids + flows), re-opening none. **Tier convention inherited** from ui-shell/ui-queue (Vitest + RTL + jsdom · ESLint over the one `FORBIDDEN_TERMS` + detector self-tests · file/import scans · injected/capturing R4 fetch double, no live backend).

**Draft `NFR-MEMO-*` target map (T1–T13, no orphan)**: BR-MEMO-1→**COPY-1** (lint) · 2→**ADVISORY-1** (lint, reuse the one FORBIDDEN_TERMS, static-code-only scope) · **3/4/5→SEPARATION-1** (component, **highest rigor + teeth** — the load-bearing triad) · 6→**ERROR-1** (component + capturing double, single-resource Retry) · 7→**VIEWONLY-1** (structural + component) · 8→**PENDING-1** (component, discriminator teeth) · 9→**LISTORDER-1** (component, no re-sort) · 10→**TESTID-1** (lint + self-test) · 11→**NAMESPACE-1** (structural, medium) · + **NOTS-1** / **FETCH-1** (four-state machine) / **PERF-1** / **A11Y-1**.

**7 open [Answer] questions** (recommendation marked, `[Answer]` blank for the user): Q1 R4 fetch-double construction · **Q2 (user-flagged)** separation-teeth = direct **DOM-containment assertion** (`!narrative.contains(rec)` + `readonly.contains(rec)` + `aria-readonly`) vs testid-presence-only · **Q3 (user-flagged)** BR-MEMO-8 discriminator-teeth constructibility · Q4 same-resource Retry via captured `applicationId` · Q5 consolidated transition test · Q6 explicit FORBIDDEN_TERMS scope-exclusion wording · Q7 PERF+A11Y soft-vs-gating.

**Key analysis surfaced (not improvised)**: (Q2) recommend the **direct DOM-tree containment assertion** — genuine structural proof of CON-BR2-TYPE, not mere testid presence. (Q3) **WIRE-1 §5 guarantees co-presence keyed on `status`**, so the honest constructible teeth is a `status:"ready"` memo with **empty `missing_information`/`cited_rule_ids` arrays** (both legitimately default to `[]`) that must still render **ready, not pending** — refuting an empty⇒pending heuristic; the reverse (`status:"pending"` with a non-null memo) is a **contract violation** and is **not** fabricated.

**Guardrails held**: NO NFR artifact generated (ambiguity-check runs AFTER answers); **WIRE-1 untouched · ui-shell (frozen) untouched · ui-queue (frozen) untouched** (its Vitest/RTL/ESLint/`FORBIDDEN_TERMS`/`ReadOnlyRegion`/testid-lint mechanisms **reused/mirrored**, not modified/imported); no application/test code; no LLM; no TypeScript; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the NFR-Requirements plan-file gate awaiting the user's **Q1–Q7 answers + review** before Part 2 (`nfr-requirements.md` + `tech-stack-decisions.md`).

## 🧩 BUILD → `ui-memo-view` (U6) — NFR Requirements Part 2 COMPLETE (both artifacts generated); STOP at NFR-Requirements 2-option gate — 2026-07-09
**Q1–Q7 answered (all A)** + embedded in the plan. **Ambiguity-check CLEAN** (2 folds): **NFR-MEMO-Fold-1** (Q2 jsdom `Node.contains()` is arbitrary-depth → the **sibling non-containment** SEPARATION-1 teeth is sound, not just parent-child → tech-stack **D7**); **NFR-MEMO-Fold-2** (Q3 T6 **empty-lists** ready memo vs T7 **populated non-sorted** ready memo = **two distinct complementary fixtures**, no conflict; empty-lists fixture also exercises BR-MEMO-9's empty-list neutral-copy branch → tech-stack **D8**).

**Part 2 generated** under `guide-docs/build/ui-memo-view/nfr-requirements/`:
- **`nfr-requirements.md`** — §0 central testability principle (R4 via the **single injected/capturing double**; Fold-A single-double / Fold-B jsdom-containment / Fold-C two-fixtures) + the **BR-MEMO-2 scope-exclusion GOVERNANCE statement** (Q6 — lints assert static source only; **no target asserts `narrative_prose` content**); §1 finalized `NFR-MEMO-*` targets (COPY-1 · ADVISORY-1 · **SEPARATION-1** [highest rigor, **DOM-containment teeth**] · ERROR-1 [message/code/detail + **same-`applicationId` Retry teeth**] · VIEWONLY-1 · PENDING-1 [**discriminator teeth**] · LISTORDER-1 [no-re-sort teeth] · TESTID-1 · NOTS-1 · FETCH-1 [four-state + consolidated transition] · NAMESPACE-1 medium · PERF-1/A11Y-1 soft · SCOPE-1 governance); §2 traceability (**no orphan** — BR-MEMO-1..11 all mapped); §3 **full Security-Guardrails compliance table** (read-only view — N/A across input-validation/prompt-injection/secrets/read-only-DB/audit; **Compliant** on error-hygiene + least-privilege-UI-framing; **no blocking finding**); §4 settled items.
- **`tech-stack-decisions.md`** — **D1–D12**: inherit ui-shell/ui-queue substrate unchanged (React/Tailwind/no-TS/Vitest/RTL/jsdom/ESLint) + **new** D6 R4 fetch-double-via-prop (Q1) · D7 DOM-containment teeth (Q2) · D8 two-distinct-fixtures (Q3) · D9 state-mechanics deferred · D11 deferred display values (token values / **minimal profile-header field set** / loading-placeholder markup) · D12 **no `src/shell` edit, no `ui-queue` import**.

**Guardrails held**: frozen FD not re-opened (targets built ON BR-MEMO-1..11); **WIRE-1 untouched** (R4 by shape, mocked) · **ui-shell (frozen) untouched** (Vitest/RTL/ESLint/`FORBIDDEN_TERMS`/`ReadOnlyRegion`/testid **reused**, new `eslint.config.js` memoView block, **no `src/shell` edit**) · **ui-queue (frozen) untouched** (fetchSeam/StructuralGuard/testid-lint **mirrored as a convention, not imported**); no application/test code; no LLM; no TypeScript; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the NFR-Requirements 2-option completion gate (**1. Request Changes / 2. Continue to Next Stage — NFR Design**) — did NOT advance. Awaiting the user's review of both artifacts.

**NFR Requirements APPROVED (2026-07-09)** → `ui-memo-view` NFR-Requirements stage COMPLETE. Advanced to **NFR Design** (per-unit).

## 🧩 BUILD → `ui-memo-view` (U6) — NFR Design Part 1 (Plan) WRITTEN; 5 open [Answer] questions (Q1 structural-isolation-by-construction); STOP at plan gate — 2026-07-09
**Plan**: `guide-docs/build/plans/ui-memo-view-nfr-design-plan.md` — **Part 1 (Plan) only**, built ON the frozen FD (BR-MEMO-1..11 + inventory + enum + region testids + flows) + the approved NFR Requirements (fourteen `NFR-MEMO-*` targets; Fold-A/B/C), re-opening none. Mirrors ui-queue's NFR-Design structure (patterns → components → ref-not-own → coverage → validated rectangle-only Mermaid).

**Draft pattern map (P1–P10, no orphan)**: P1 **SharedForbiddenTermsReusePattern** (COPY-1/ADVISORY-1/NAMESPACE-1, scoped to exclude `narrative_prose`) · **P2 StructuralIsolationCompositionPattern** (SEPARATION-1 — **the load-bearing pattern, siblings-by-construction**) · P3 **ErrorEnvelopeToRenderPattern** (ERROR-1) · P4 **FetchSeamPattern** (ERROR-1/FETCH-1/PERF-1 — own-local single-resource same-`applicationId` Retry, mirror-not-import) · P5 **FourStateMachinePattern** (loading→ready|pending|error, no page transition) · P6 **StatusDiscriminatorPattern** (PENDING-1 — explicitly NOT array-length) · P7 **RoleInvariantRenderingPattern** (VIEWONLY-1) · P8 **OrderPreservingListPattern** (LISTORDER-1) · P9 **StructuralGuardPattern** (TESTID-1/NOTS-1 incl. region testids) · P10 **ReferencedObservedBoundaryPattern** (PERF-1/A11Y-1/SCOPE-1).

**Nine logical components (C1–C9, all 14 targets covered)**: MemoView · memoFetchSeam (own local, mirror-not-import) · MemoStateView · ProfileContextHeader · NarrativeRegion (**no rec/conf prop or path**) · CitationsList · MissingInfoRegion · ReadOnlyRecommendationRegion (composes frozen `ReadOnlyRegion`, **sole** rec/conf render site) · StructuralGuard (test/lint substrate).

**Validated rectangle-only Mermaid** (7 rules, no diamonds) where the **RO-region-as-sibling-not-descendant isolation is a VISIBLE GRAPH PROPERTY** — MemoView has sibling edges to NarrativeRegion/MissingInfoRegion/ReadOnlyRecommendationRegion; RecommendationBadge/ConfidenceBadge are descendants of the RO region only (via frozen ReadOnlyRegion), never of the narrative.

**5 open [Answer] questions** (recommendation marked, `[Answer]` blank): **Q1 (user-flagged)** structural-isolation-**by-construction** (component tree guarantees RO/L siblings; NarrativeRegion has no rec/conf prop; test = confirmation/regression guard) vs test-only · Q2 memoFetchSeam distinct-module vs prop-only · Q3 four-state machine responsibility vs component · Q4 StructuralGuard granularity · Q5 error uniform vs 401 special-case.

**Guardrails held**: NO NFR-Design artifact generated (ambiguity-check runs AFTER answers); **WIRE-1 untouched · ui-shell (frozen) untouched** (copy/`FORBIDDEN_TERMS`/`RoleContext`/`ReadOnlyRegion`/testid **reused**) **· ui-queue (frozen) untouched** (fetchSeam/StructuralGuard/testid-lint **mirrored, not imported**); no application/test code; no LLM; no TypeScript; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the NFR-Design plan-file gate awaiting the user's **Q1–Q5 answers + review** before Part 2 (`nfr-design-patterns.md` + `logical-components.md`).

## 🧩 BUILD → `ui-memo-view` (U6) — NFR Design Part 2 COMPLETE (both artifacts generated); STOP at NFR-Design 2-option gate — 2026-07-09
**Q1–Q5 answered (all A)** + embedded in the plan. **Ambiguity-check CLEAN** (1 fold): **NFR-DESIGN-Fold-1** — Q1-A's by-construction guarantee is made **self-evident-in-isolation** via a **`NarrativeRegion` header comment** (applying the frozen `ReadOnlyRegion.jsx` / `fetchSeam.js` comment convention) documenting props `{narrative, testid}` only, **no** rec/conf prop or path — complementing (not replacing) the SEPARATION-1 DOM-containment regression test → recorded in P2 + C5.

**Part 2 generated** under `guide-docs/build/ui-memo-view/nfr-design/`:
- **`nfr-design-patterns.md`** — P1–P10 (Q1–Q5 folded in), each stating how it structurally meets its `NFR-MEMO-*` target(s) + tier. **P2 StructuralIsolationCompositionPattern** documented as **the load-bearing pattern** with the **prop-signature by-construction argument** spelled out (`ReadOnlyRecommendationRegion` sole `{recommendation, confidence}` receiver; `NarrativeRegion` `{narrative, testid}`-only with no path; no wired way to mis-nest without an obvious reviewable prop addition) + the `NarrativeRegion` header comment (Fold-1). Validated rectangle-only **pattern-integration Mermaid** + text alternative; pattern→target→tier→rigor traceability (all 14, no orphan).
- **`logical-components.md`** — finalized **C1–C9** (Q1–Q5 folded in): MemoView (sibling composition, isolation set here) · memoFetchSeam (own local, mirror-not-import) · MemoStateView · ProfileContextHeader · **NarrativeRegion** (`{narrative, testid}`-only + header comment) · CitationsList · MissingInfoRegion · **ReadOnlyRecommendationRegion** (composes frozen `ReadOnlyRegion`, **sole** rec/conf holder) · StructuralGuard. Validated rectangle-only **component-relationship Mermaid** with the **RO-sibling-not-descendant isolation as a VISIBLE GRAPH PROPERTY** + text alternative; **reference-not-own** with **REUSED (ui-shell) vs MIRRORED-NOT-IMPORTED (ui-queue) vs CONSUMED-BY-SHAPE (WIRE-1 / `narrative_prose`)** kept distinct; component→target coverage (all 14, no orphan); settled items.

**Guardrails held**: frozen FD + approved NFR Requirements not re-opened; **WIRE-1 untouched** (R4 by shape; real `memoFetchSeam` wiring deferred) **· ui-shell (frozen) untouched** (copy/`FORBIDDEN_TERMS`/`RoleContext`/`ReadOnlyRegion`/testid **reused**, no `src/shell` edit) **· ui-queue (frozen) untouched** (fetchSeam/StructuralGuard/testid-lint **mirrored, not imported**); no application/test code; no LLM; no TypeScript; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the NFR-Design 2-option completion gate (**1. Request Changes / 2. Continue to Next Stage — Infrastructure Design**) — did NOT advance. Awaiting the user's review of both artifacts.

## 🧩 BUILD → `ui-memo-view` (U6) — NFR Design APPROVED → Infrastructure Design SKIPPED (logged); STOP at Infra 2-option gate; NEXT = Code Generation — 2026-07-09
**NFR Design APPROVED** → `ui-memo-view` NFR-Design stage COMPLETE.

**Infrastructure Design — assessed → SKIPPED (logged, explicit four-point rule justification, NOT silent)**, per CLAUDE.md "Skip IF: No infrastructure changes / Infrastructure already defined" + execution-plan §3 "little independent infra":
1. **No untrusted parsing / no sandbox** — renders WIRE-1 R4 JSON (mocked via the injected `memoFetchSeam`); no pdfplumber/subprocess/file parsing.
2. **No persistence provisioned** — fetches R4 through the seam; never touches a database directly; no store, no migration.
3. **No LLM/provider access** — *renders* LLM-authored `narrative_prose` but authors/executes none; holds no provider client.
4. **No deployed service / no independent cloud topology** — bundler/dev-server + Vercel topology → `deploy-config` (P2); real `memoFetchSeam` wiring + R4 route impl (`backend/app/main.py`) → composition root / Build & Test.

Ambiguity-check surfaced **no genuine ui-memo-view-owned infra concern** (the only topology candidate is explicitly composition-root/Build & Test/deploy-config P2) → SKIP correct, no STOP. Consistent with **ui-shell + ui-queue** (the two prior React-unit SKIPs). **NO infra artifact created** (`guide-docs/build/ui-memo-view/infrastructure-design/` not created).

**Skip roster now TWELVE**: intake · rules-engine · audit-store · memo-agent-core · auth-rbac · secrets-config · ui-shell · corpus-generator · quality-gates · admin-cli · ui-queue · **ui-memo-view**; **database** remains the one real non-skip.

**`ui-memo-view` (U6) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · **Infrastructure Design ✓ SKIPPED (logged)** · Code Generation ⏳ (the LAST stage — Part-1-plan-then-Part-2-generate, own approval).

**Guardrails held**: NO code; NO infra artifact; **WIRE-1 + ui-shell (frozen) + ui-queue (frozen) untouched**; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the Infrastructure Design 2-option completion gate (**1. Request Changes / 2. Continue → Code Generation** — the LAST stage for ui-memo-view) — did NOT advance past the gate.

## 🧩 BUILD → `ui-memo-view` (U6) — Infra SKIP accepted → Code Generation Part 1 (Plan) WRITTEN; 6 open [Answer] questions; STOP at plan gate — 2026-07-09
**Infra SKIP accepted** → advanced to **Code Generation** (per-unit, the **LAST stage** for ui-memo-view).

**Plan**: `guide-docs/build/plans/ui-memo-view-code-gen-plan.md` — **Part 1 (Plan) only, NO code**, built ON the frozen FD (BR-MEMO-1..11) + approved NFR Requirements (fourteen `NFR-MEMO-*`; D6; Fold-A/B/C) + approved NFR Design (patterns P1–P10; components C1–C9; NFR-DESIGN-Fold-1), re-opening none. **JS/JSX, no-TS, Vitest+RTL+jsdom** mirroring the realized ui-shell/ui-queue convention.

**§1 component→module map (C1–C9 → `frontend/src/memoView/`)**: `memoFetchSeam.js` · `components/{CitationsList,MissingInfoRegion,ReadOnlyRecommendationRegion,NarrativeRegion,ProfileContextHeader,MemoStateView}.jsx` · `MemoView.jsx` · `copy.js` · C9 test-only. **NarrativeRegion header comment ({narrative,testid}-only, no rec/conf path) is an EXPLICIT deliverable.** NO `src/shell` or `src/queue` file created/modified. **§2 TDD test→target map** (all 14 at pinned tier, incl. SEPARATION-1 DOM-containment teeth · PENDING-1 empty-lists-ready teeth · ERROR-1 same-`applicationId` Retry teeth · LISTORDER-1 no-re-sort teeth on both lists). **§3 leaf-first Steps 1–11** (scaffold+config → C2 → C6+C7 → C8 → C5 → C4 → C3 → C1 → C9 → coverage → summary), not started. **§4 HOLDS** (by-construction isolation HARD; ui-queue mirrored-not-imported; `narrative_prose` as-is never linted). **§5 coverage gate** (Vitest frontend run; baseline **src/shell 100% + src/queue 100%** no-regress; src/memoView QA-6 ≥90%; backend pytest **850/31 untouched**).

**6 open [Answer] questions** (recommendation marked, `[Answer]` blank): Q1 loading-placeholder markup · Q2 minimal profile-header field set · Q3 memoFetchSeam failure convention/JSDoc · Q4 the two Fold-C fixtures construction · Q5 transition-test file location · Q6 shared-config extension (+ new `eslint-rules/memoView.js` `memo-testid-convention`).

**Guardrails held**: NO code; NO `frontend/src/memoView/` file created; ambiguity-check deferred until AFTER answers; **WIRE-1 + ui-shell (frozen) + ui-queue (frozen) untouched**; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the Code-Gen plan-file gate awaiting the user's **Q1–Q6 answers + review** before Part 2 (code generation).

## ✅ BUILD → `ui-memo-view` (U6) Code Generation Part 2 COMPLETE — 161 Vitest passed / 100%; STOP at completion gate (LAST stage) — 2026-07-09
**Q1–Q6 answered (all A)** + embedded in the plan. **Ambiguity-check CLEAN**: **CG-MEMO-Fold-1** (own-local `normalizeError` produces the same `{error:{code,message,detail}}` shape as WIRE-1 §4 / ui-queue's — ERROR-1 consistency via the **shared WIRE-1 contract, NOT a ui-queue import**; ui-queue stays un-imported, enforced by `noUiQueueImport.test.js`); **(i)** all four Q2 `ProfileContextHeader` field names verified verbatim on the frozen `ApplicantProfile`; **(ii)** the shared fixtures module uses a `makeMemoView` factory + named canonical fixtures (extensible, not a dumping ground).

**Code + tests GENERATED** under `frontend/src/memoView/` (TDD/leaf-first, Steps 1–11): production C1–C8 (`MemoView.jsx` · `memoFetchSeam.js` · `copy.js` · `components/{CitationsList,MissingInfoRegion,ReadOnlyRecommendationRegion,NarrativeRegion,ProfileContextHeader,MemoStateView}.jsx`) + C9 StructuralGuard (20 `__tests__/` files incl. `fixtures.js`) + shared-infra `eslint-rules/memoView.js` (new `memo-testid-convention`) and `eslint.config.js`/`vitest.config.js` include-path extensions. **NO `src/shell` or `src/queue` file created/edited.**

**Suite**: **161 Vitest tests passed / 43 files**; **100% coverage** on `src/memoView` (every file) — QA-6 ≥90% PASSED; `src/shell` + `src/queue` stay **100% (UNTOUCHED)**; **ESLint clean** (exit 0). Backend pytest **850 passed / 31 skipped / 99.82% UNTOUCHED** (no backend file modified; separate runner/tree, not re-run). Load-bearing **SEPARATION-1 DOM-containment teeth** + PENDING-1 discriminator teeth + ERROR-1 same-`applicationId` Retry teeth + LISTORDER-1 no-re-sort teeth all green. `code-summary.md` written; `testresults.txt` frontend section refreshed (alongside, not merged); plan Steps 1–11 `[x]` + answers + §6.5 embedded.

**Guardrails held**: **ui-shell (frozen) untouched** (reused via import only incl. `ReadOnlyRegion` **first use**; no `src/shell` edit; no new word-list) **· ui-queue (frozen) untouched** (fetchSeam/StructuralGuard/testid **mirrored, never imported**) · **by-construction isolation** (`NarrativeRegion` no rec/conf prop + header comment, NFR-DESIGN-Fold-1) enforced by the SEPARATION-1 teeth · `narrative_prose` rendered as-is, never linted · no RoleGate · no router · `memoFetchSeam` duck-typed · WIRE-1 R4 by shape only, no real network · no LLM · no TypeScript · tier-B NOT authorized · no other unit started · `audit_store` Docker-guard gap still deferred.

**STOPPED** at the Code Generation 2-option completion gate (**1. Request Changes / 2. Continue** — the LAST stage for `ui-memo-view`) — did NOT advance. Awaiting the user's diff review. On approval, `ui-memo-view` (U6) becomes the **13th complete unit** (3rd UI-cluster after ui-shell, ui-queue).

## ✅ BUILD → `ui-memo-view` (U6) COMPLETE (13th unit; 3rd UI-cluster) → `ui-approval-gate` (U7) STARTED; FD Part 1 gate — 2026-07-09
**`ui-memo-view` (U6) — COMPLETE**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED (logged) · **Code Generation ✓** (161 Vitest tests / **100% coverage on `src/memoView`**, ESLint clean; **`src/shell` + `src/queue` both still 100% UNTOUCHED**; the **load-bearing SEPARATION-1 DOM-containment teeth pass = concrete verification of CON-BR2-TYPE**; **CG-MEMO-Fold-1** gives cross-unit ERROR-1 consistency via the **shared WIRE-1 error-envelope contract, not code sharing**; backend pytest **850 passed / 31 skipped** UNTOUCHED). The **THIRTEENTH complete unit** and the **THIRD complete UI-cluster unit after `ui-shell` + `ui-queue`**.

**P1 roster (17 P1 units)** — **14 COMPLETE**: intake, document-sanitizer, rules-engine, memo-agent-core, auth-rbac, audit-store, quality-gates, corpus-generator, database, secrets-config, admin-cli (11 non-UI) + **ui-shell, ui-queue, ui-memo-view** (3 UI). **UI P1 remaining (3)**: ui-approval-gate (in progress) / ui-override-form / ui-history.

**`ui-approval-gate` (U7) — STARTED** (working sequence: ui-queue → ui-memo-view → **ui-approval-gate** → ui-override-form → ui-history). DISCOVER-carryover **CLEAN** (no `guide-docs/build/ui-approval-gate/` dir; no `frontend/src/approvalGate/` code). Frozen surfaces re-read: **ui-shell `RoleGate`** (COSMETIC only — `can∈{act,read}`; `underwriter.act=true`/`auditor.act=false`/`admin.act=false`; no `role` prop; reads `useCurrentRole()` internally; imports NO backend; owns NO authz decision, BR-UI-4/SEC-4) + `AppFrame`/`Panel`/`ReadOnlyRegion`/`RecommendationBadge`/`ConfidenceBadge`/copy/tokens/session; **ui-queue + ui-memo-view fetchSeam/StructuralGuard conventions** (established sibling patterns, not imports); **WIRE-1 R5** `POST /recommendations/{recommendation_id}/commit` (`{action, reason?}` reason-non-blank iff override; `underwriter_id` from session NOT body; 403 forbidden / 409 commit_conflict [already-committed or blank-override-reason]); **auth-rbac** `Role`/`PERMISSION_MATRIX`/`RBAC_COMMIT` (ONLY underwriter holds `RBAC_COMMIT`); **audit-store `DecisionCommitService.commit(...)`** — GATE-1 (BR-COMMIT-GATE) + independent **AUTHZ-1** backend re-check (`UnauthorizedCommit` for non-underwriter), `CommitAction∈{approve,override}` — the real server-side enforcement this UI action triggers.

**FD Part 1**: depth recommendation = **CONFIRM COMPREHENSIVE** (unit-of-work.md invariant-bearing classification — first UI **write path**, first **real `RoleGate` composition**, first interactive **`CommitAction` human-namespace** affordance distinct from the system `Recommendation` namespace; unlike ui-queue/ui-memo-view's lighter depth) + SIX open **[Answer]** questions (Q1 depth confirm / Q2 approve confirmation-vs-single-click flow / Q3 RoleGate cosmetic-only defense-in-depth + AUTHZ-1 backend re-check the real gate / Q4 commit success/failure surfacing incl. 409 already-committed & 403 forbidden / Q5 structural relation to ui-memo-view compose-vs-extend-vs-stand-alone / Q6 approve-only vs approve+override, override→U8) presented for confirmation **before the plan is written**.

**Guardrails held**: NO plan/FD artifact generated; **WIRE-1 untouched · ui-shell (frozen) untouched · ui-queue (frozen) untouched · ui-memo-view (frozen) untouched**; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**UPDATE 2026-07-09**: user confirmed **COMPREHENSIVE** (Q1-A) + answered **Q2–Q6 all A** (Q2 explicit confirm step before R5 commit / Q3 RoleGate `can="act"` cosmetic defense-in-depth only, AUTHZ-1 backend re-check the real gate, 403 = genuine error / Q4 distinct per-status surfacing [success confirmation · 409 already-committed/conflict · 403 not-permitted · 400/422 generic invalid] via the shared error-envelope message-visible/code-testid/detail-never / Q5 stand-alone with own R4 fetch, composes ui-shell primitives, does NOT import ui-memo-view / Q6 approve-only [`action="approve"`, no reason], override → U8 `ui-override-form`). Loaded the `underwriting-rules` domain skill — all six answers align with the eight hard constraints. **FD Part 1 plan FILE WRITTEN** — `guide-docs/build/plans/ui-approval-gate-functional-design-plan.md` (full Q1–Q6 text + `[Answer]: A` + COMPREHENSIVE depth embedded per standing convention; §0 scope/builds-ON ledger; §3 planned Part-2 structure incl. own-local `commitFetchSeam` [R4-read + **R5-write**] / `copy` / `ApprovalGateView` + `CommitConfirmDialog` + `CommittedConfirmation`, draft **BR-AG-1..10**, state machine `loading→ready→confirming→submitting→{committed|error}` + `pending`). **Ambiguity-check CLEAN — five clarity-folds, NO STOP**: AG-Fold-1 (check i — confirm dialog is a pure client-side toggle; open/cancel does NO fetch/commit/mutation; R5 fires only on confirm), AG-Fold-2 (check ii — `CommittedDecision` echo + R4 context already in hand is ENOUGH for the confirmation state, NO re-fetch; `decision_id`/`timestamp` are ui-history's R6/R7 scope), AG-Fold-3 (check iii — `underwriter_id`-from-session restated explicitly as the FIRST commit-exercising UI unit: R5 body carries ONLY `{action:"approve"}`, `recommendation_id` in the path, AUTHZ-1 re-check server-side), AG-Fold-4 (sibling seam is CONVENTION not import; cross-unit error-shape consistency = shared WIRE-1 §4 contract, not shared code; StructuralGuard `noUiQueueImport`/`noMemoViewImport` enforces at NFR), AG-Fold-5 (R4 `status:"pending"`/`recommendation_id:null` → NO approve affordance, nothing to commit). NO FD artifact generated (`domain-entities.md`/`business-rules.md`/`business-logic-model.md` deferred to Part 2 on explicit go); NO code under `frontend/src/approvalGate/`; **WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) untouched**; tier-B NOT authorized; no other unit started. **STOPPED at the FD Part 1 plan-file gate** for the user's review before any Part 2 generation.

**UPDATE 2026-07-09 (FD Part 2 GENERATED)**: user **APPROVED the plan** (all five folds AG-Fold-1..5 accepted as-is) and directed Part 2. Re-read frozen composition targets on disk (`RoleGate {can,children,fallback}` `can∈{act,read}` cosmetic map + `useCurrentRole`; `MemoView` injected-fetch-seam orchestrator pattern; `roleContext` `RoleProvider`/`useCurrentRole`). **Three FD artifacts GENERATED — `guide-docs/build/ui-approval-gate/functional-design/`**: `domain-entities.md` (consumed frozen shapes R4 `MemoView` / R5 body `{action:"approve"}` only [`underwriter_id` NOT in body, no `reason`] / `CommittedDecision` echo / WIRE-1 §4 envelope + 4-status table [200·403·409·400/422] / `CommitAction` approve namespace; own-local `commitFetchSeam` `createCommitFetch(transport)→{fetchContext,submitApprove}` + `buildMemoRequest`/`buildCommitRequest`/`normalizeError` **NOT importing sibling seams** AG-Fold-4; `copy.js` LINT-SUBJECT advisory-only naming; component inventory `ApprovalGateView` orchestrator + `CommitStateView` + `RecommendationContext` + `ApproveAffordance`[`RoleGate can="act"`] + `CommitConfirmDialog`[pure toggle] + `CommittedConfirmation`; full state machine `loading→ready(idle)→confirming→submitting→{committed|error}` + `pending`, `confirming` pure client-side toggle no fetch/commit/mutation AG-Fold-1, no re-fetch AG-Fold-2, pending→no affordance AG-Fold-5; boundary section); `business-rules.md` (**BR-AG-1..10** each condition + mechanism-landing-at-NFR/Code-Gen; rule index; **Security-Guardrails table with REAL RBAC/authz rows** — least-privilege UI framing / authorization server-authoritative defense-in-depth / no client-side authz datum / human-in-the-loop / error-hygiene / advisory naming = Compliant; input-validation / prompt-injection / secrets / audit-persistence = N/A with rationale); `business-logic-model.md` (confirm→commit flow **7-rule-validated Mermaid** rectangle-only + text alt; §2 confirm-dialog-as-pure-toggle load-bearing invariant; §3 AUTHZ-1 defense-in-depth as a SECOND validated Mermaid structural note [RoleGate cosmetic hide → server re-check real gate → `UnauthorizedCommit`/403] + text alt; consumer/dependency map; invariant self-check advisory-only / human-in-the-loop / RoleGate-cosmetic-not-authz / namespace-distinctness / no-LLM → concrete mechanism + rule). Both Mermaid 7-rule validated + text alternatives. NO code under `frontend/src/approvalGate/`; **WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) UNTOUCHED**; tier-B NOT authorized; no other unit started. **STOPPED at the standardized FD 2-option completion gate (1. Request Changes / 2. Continue to Next Stage → NFR Requirements)** for the user's review of the three artifacts — did NOT advance past the gate.

**AMENDMENT at the FD gate (2026-07-09, Request Changes — scoped)**: the `domain-entities.md §5` error-recovery prose (R4 read error → Retry re-runs R4 read; R5 commit error → returns to `ready(idle)`, never auto-resubmit) had no checkable rule and wasn't in the diagrams. FIX (no other change to the three artifacts): (1) **added BR-AG-11** (error-recovery is cause-differentiated) to `business-rules.md` with RTL mechanism [(a) R4-error Retry re-issues exactly one R4 GET same `applicationId`; (b) R5-error → `ready(idle)`, zero automatic `submitApprove` follow-ups, fresh Approve→Confirm required] + rule-index row + reference from the Security-Guardrails **Human-in-the-loop** row (a commit failure must not silently/automatically retry the write); (2) `business-logic-model.md §1` Mermaid **SPLIT `ErrorEnv` → `ErrorRead`** (`ErrorRead --> Loading`, Retry re-issues R4 read) **and `ErrorCommit`** (`ErrorCommit --> Ready`, no auto-resubmit) in the diagram itself + §1.1 text-alt steps 2/7 updated [BR-AG-11(a)/(b)] + Mermaid **re-validated against all 7 rules = PASS**; (3) §5 invariant self-check Human-in-the-loop row extended to include **BR-AG-11** alongside BR-AG-2/BR-AG-3. The §3 defense-in-depth Mermaid untouched; `domain-entities.md` unchanged (its §5 prose now backed by BR-AG-11). **BR-AG rule set now 1..11.** NO code; WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) UNTOUCHED; tier-B NOT authorized; no other unit started. **FD 2-option gate RE-PRESENTED; HELD** for the user's review of the corrected artifacts.

**FD APPROVED 2026-07-09 (Continue, corrected — BR-AG-1..11). NFR Requirements UNDERWAY (COMPREHENSIVE)** — Part 1 plan `guide-docs/build/plans/ui-approval-gate-nfr-requirements-plan.md` WRITTEN, built on the frozen FD (re-opening none): §0 **dual-operation-seam** testability principle (`fetchContext` R4 + `submitApprove` R5, per-operation call-count teeth — the key difference from the siblings' single-op seams); §1 draft **`NFR-AG-*`** target map (commit-lifecycle teeth **NOFINAL-1**/**CONFIRM-1**/**CANCEL-1** full-highest; **RBAC-1**/**BODY-1**/**ERROR-1**/**SCOPE-APPROVE-1**/**NOREFETCH-1**/**REFNOTOWN-1**/**RECOVERY-1**/**FETCH-1** full; **COPY-1**/**ADVISORY-1**/**TESTID-1**/**NOTS-1** inherited full; **NAMESPACE-1** medium; **PERF-1**/**A11Y-1** soft; **SCOPE-1** governance) — BR-AG-1..11 each covered, **no orphan**; §2 draft traceability; §3 **SIX numbered `[Answer]` questions (BLANK)** — Q1 depth; Q2 [user-flagged] dual-operation single-double construction; Q3 [user-flagged] RoleGate stub coverage all-three-roles+null vs binary; **Q4 [GENUINE collision, flagged not improvised]** — the single `FORBIDDEN_TERMS.systemOutput` forbids the token `decision`, but this unit is the human decision point where the reserved-word rule PERMITS `decision` for the human's committed action (illustrative FD copy "This records your decision." would trip the `advisory-vocabulary` lint); rec A = apply the lint UNMODIFIED + unit copy avoids the literal `decision` token, FD string realized without it at Code-Gen (LINT-SUBJECT refinement, not an FD re-open); Q5 consolidated transition test incl. split `ErrorRead`/`ErrorCommit` recovery; Q6 PERF/A11Y soft-vs-gating given the interactive confirm dialog; §4 Part-2 structure; §5 Security-Guardrails preview; §6 holds; §7 gate. Grounded on the on-disk re-read of the sibling NFR convention + `forbiddenTerms.js`/`eslint-rules/index.js`/`shell/copy/index.js`. NO NFR artifact generated (`nfr-requirements.md`/`tech-stack-decisions.md` deferred to Part 2 on explicit go); NO code; **WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) UNTOUCHED**; tier-B NOT authorized; no other unit started. **STOPPED at the NFR-Requirements Part 1 plan-file gate** awaiting the user's six filled `[Answer]` tags → ambiguity-check → Part 2 on explicit go (plan re-saved with answers embedded per standing convention).

**UPDATE 2026-07-09 (NFR Requirements Part 2 GENERATED)**: six `[Answer]` tags filled (all **A**). Ambiguity-check CLEAN — **two clarity-folds, no STOP**: **NFR-AG-Fold-1** (check i — the single dual-operation double exposes `fetchContext`/`submitApprove` under the exact seam names, each its own call log [never a shared generic `calls`]; CONFIRM-1 pre-`Confirm` asserts BOTH `submitApprove.calls.length===0` AND `fetchContext.calls.length===1` = non-vacuous cross-guard, a wrong-counter/swapped assertion fails); **NFR-AG-Fold-2** (check ii — audited ALL 14 `APPROVAL_COPY` draft strings vs the frozen `findForbiddenSystemOutput`; EXACTLY ONE tripped — `confirmBody` "…This records your decision." [bare `decision`]; **FIXED NOW** at the FD source `domain-entities.md §3` → "…Your approval will be recorded." + §3 note rewritten [reserved-word honored **semantically**, no literal token] — a LINT-SUBJECT realization refinement the FD deferred, **not** an FD re-open; other 13 strings already clean → `advisory-vocabulary` lint applies UNMODIFIED). **Part 2 GENERATED — `guide-docs/build/ui-approval-gate/nfr-requirements/`**: `nfr-requirements.md` (§0 dual-operation testability + Fold-1 cross-guard; §1 finalized **`NFR-AG-*`** targets — NOFINAL-1/**CONFIRM-1**/**CANCEL-1** full-highest teeth + RBAC-1[all-roles+null, Q3]/BODY-1/ERROR-1[table 200·403·409·400/422]/SCOPE-APPROVE-1/NOREFETCH-1/REFNOTOWN-1/RECOVERY-1[two-directional split-error]/FETCH-1[consolidated transition, Q5]/COPY-1/ADVISORY-1[unmodified, Q4]/TESTID-1/NOTS-1 full + NAMESPACE-1 medium + PERF-1/A11Y-1 soft[Q6] + SCOPE-1 governance, each pass/fail + acceptance + tier + rigor; §2 traceability **no orphan** + 4 folds crystallized; §3 full Security-Guardrails table with REAL RBAC/authz rows; §4 Q4 advisory-vocabulary governance note [semantic-not-literal]; §5 settled items) + `tech-stack-decisions.md` (D1–D11 inherit the frozen substrate; add dual-operation double D5 + all-roles+null stub D7 + consolidated transition D8 + advisory-unmodified D4 + soft-a11y D10; **NO new dependency**). NO code under `frontend/src/approvalGate/`; **WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) UNTOUCHED** (the `domain-entities.md §3` `confirmBody` copy fix is this unit's own FD, a LINT-SUBJECT refinement); tier-B NOT authorized; no other unit started. **STOPPED at the standardized NFR-Requirements 2-option gate (1. Request Changes / 2. Continue to Next Stage → NFR Design)** for the user's review of both artifacts — did NOT advance past the gate.

**NFR Requirements APPROVED 2026-07-09 (Continue). NFR Design UNDERWAY (COMPREHENSIVE)** — Part 1 plan `guide-docs/build/plans/ui-approval-gate-nfr-design-plan.md` WRITTEN, built on the frozen FD + approved NFR-Req (re-opening none): §1 pattern→target map **P1..P10** — **P1 SingleCallSiteConfirmGatedCommitPattern** (NOFINAL-1/CONFIRM-1/CANCEL-1, **full-highest, by-construction single-call-site** — the write capability structurally lives only in `CommitConfirmDialog`) / P2 CosmeticRoleGateCompositionPattern (RBAC-1, **first real `RoleGate` use**) / P3 ApproveOnlyRequestBuilderPattern (BODY-1+SCOPE-APPROVE-1, builder signature cannot emit `reason`/`underwriter_id`) / P4 PerStatusEnvelopeToRenderPattern (ERROR-1, four-status table) / P5 ConfirmationFromEchoPattern (NOREFETCH-1) / P6 CauseDifferentiatedRecoveryPattern (RECOVERY-1) / P7 DualOperationFetchSeamPattern (FETCH-1+BODY-1+PERF-1) / P8 ExtendedStateMachinePattern (FETCH-1, ND-Fold-A View-owns) / P9 StructuralGuardPattern (COPY-1/ADVISORY-1[**unmodified, Q4-A named property**]/NAMESPACE-1/TESTID-1/NOTS-1/REFNOTOWN-1, one substrate ND-Fold-B) / P10 ReferencedObservedBoundaryPattern (PERF-1/A11Y-1/SCOPE-1 soft-governance); §2 logical components C1 `ApprovalGateView` / C2 `commitFetchSeam` / C3 `CommitStateView` / C4 `RecommendationContext` / C5 `ApproveAffordance` [**no commit capability**] / C6 `CommitConfirmDialog` [**sole commit-trigger holder**] / C7 `CommittedConfirmation` [**no seam access**] / C8 `StructuralGuard` / C9 `copy.js`; §3 reference-not-own (reused/mirrored/by-shape, none modified); §4 component→target coverage **all 19 `NFR-AG-*`, no orphan**; §5 **VALIDATED component-relationship Mermaid** (7-rule, rectangle-only, solid=invokes/dashed=provides-scans) with the **single-call-site guarantee as a VISIBLE graph property** — the only solid inbound edge into `SubmitApprove` is `Dialog→SubmitApprove`; `Affordance→Dialog` only (no edge to `SubmitApprove`); `Confirmation` has no seam edge — + text alt; §6 **FOUR numbered `[Answer]` questions (BLANK)** — Q1 depth; **Q2 [KEY, flagged] by-construction single-call-site** (`ApproveAffordance` receives only `onApprove`, no `submitApprove` access); Q3 by-construction confirmation-from-echo (`CommittedConfirmation` no seam access); Q4 by-construction approve-only request-builder (no `reason`/`underwriter_id` parameter) — the "by-construction trio"; §7 Part-2 structure + precedent-determined folds (ND-Fold-A/B, Fold-1/3); §8 holds; §9 gate. NO NFR-Design artifact generated (`nfr-design-patterns.md`/`logical-components.md` deferred to Part 2 on explicit go); NO code; **WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) UNTOUCHED**; tier-B NOT authorized; no other unit started. **STOPPED at the NFR-Design Part 1 plan-file gate** awaiting the user's four filled `[Answer]` tags → ambiguity-check → Part 2 on explicit go (plan re-saved with answers embedded per standing convention).

**UPDATE 2026-07-09 (NFR Design Part 2 GENERATED)**: four `[Answer]` tags filled (all **A** — the by-construction trio). Ambiguity-check CLEAN — **three clarity-folds, no STOP**: **ND-Fold-1** (check i — `ApproveAffordance` carries a header comment [frozen `NarrativeRegion`/`ReadOnlyRegion` self-evidence convention] "props `{onApprove}`(+cosmetic) only — no `submitApprove`/seam/`onConfirm`; opens dialog, cannot commit", discoverable reading the component alone); **ND-Fold-2** (check ii — `CommitConfirmDialog` carries a header comment marking it the SOLE commit-trigger holder, `onConfirm` = the single `submitApprove` call site, open/cancel a pure toggle); **ND-Fold-3** (check iii — `CommittedConfirmation` cannot re-fetch even indirectly: props `{decision,context}` only [no seam] + the transport-bearing seam [`createCommitFetch(transport)`] held ONLY by `ApprovalGateView` + the pure builders perform NO I/O + a StructuralGuard asserts presentational components don't import `createCommitFetch`). **Part 2 GENERATED — `guide-docs/build/ui-approval-gate/nfr-design/`**: `nfr-design-patterns.md` (§P1 load-bearing **SingleCallSiteConfirmGatedCommitPattern** with the callback-only-no-seam mechanism spelled out for BOTH components — `ApproveAffordance` props `{onApprove}`+cosmetic DO NOT include `submitApprove`/seam/`onConfirm`; `CommitConfirmDialog` props `{onConfirm,onCancel,...display}` where `onConfirm`=the wired invocation supplied only here + P2..P10; §11 validated **pattern-integration Mermaid** 7-rule rectangle-only + text alt; §12 traceability all 19 no orphan) + `logical-components.md` (C1–C9 with **EXACT prop shapes** enforcing the by-construction trio — C5 `{onApprove}` only + header comment; C6 sole `onConfirm` holder + header comment; C7 `{decision,context}` only no seam + header comment; C2 `createCommitFetch(transport)` sole holder = `ApprovalGateView`; §2 validated **component-relationship Mermaid** single-call-site VISIBLE [only solid inbound edge into `SubmitApprove` is `Dialog→SubmitApprove`; `Affordance→Dialog` only; `Confirmation` no seam edge] + text alt; §3 reference-not-own **three relationships kept distinct** reused/mirrored-not-imported/consumed-by-shape; §4 coverage all 19 no orphan; §5 settled items). Both Mermaid 7-rule validated + text alternatives. NO code under `frontend/src/approvalGate/`; **WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) UNTOUCHED**; tier-B NOT authorized; no other unit started. **STOPPED at the standardized NFR-Design 2-option gate (1. Request Changes / 2. Continue to Next Stage → Infrastructure Design)** for the user's review of both artifacts — did NOT advance past the gate.

**NFR Design APPROVED 2026-07-09 (Continue). Infrastructure Design SKIPPED-logged 2026-07-09** — assessed AT THE STAGE (not pre-committed) per CLAUDE.md ("Skip IF: no infrastructure changes / already defined") + execution-plan.md §3 "little independent infra": `ui-approval-gate` is a source-level React unit (C1–C9) with an interactive **write path** but **no independent cloud topology it designs** — (1) no untrusted parsing / no subprocess sandbox (reads typed WIRE-1 JSON, posts constant `{action:'approve'}`; document parsing is intake's SEC-2 server-side); (2) no independent persistence provisioned (the write goes through the **own-local `commitFetchSeam`** injected transport [mocked in tests], never touching a DB / audit-store persistence directly; the atomic write + audit tuple are audit-store's `DecisionCommitService` server-side); (3) no LLM/provider access; (4) bundler/dev-server + Vercel topology = `deploy-config` P2, real `commitFetchSeam` wiring + R4/R5 route impl = composition-root's / Build & Test's. **Ambiguity-check** on the flagged candidate (does the write path interact with deployment differently than a read-only view?): CORS/method [POST vs GET] = origin allowlisting already `deploy-config` P2 (WIRE1-Fold-3), all methods not per-unit; CSRF/auth-handshake = the bearer/cookie/OIDC abstract seam deferred at WIRE-1 A6 (composition-root/deploy concern); commit-conflict/idempotency [409] = enforced server-side by audit-store's write gate/`BR-COMMIT-GATE`, the UI merely surfaces it (NFR-AG-ERROR-1). The genuine write path is a new category of **application BEHAVIOR, not INFRASTRUCTURE** — it flows through the SAME deferred composition-root wiring pattern as every prior UI read path → **no genuine ui-approval-gate-owned topology decision → SKIP**. **The THIRTEENTH unit-level Infra SKIP** (`database` remains the one real non-skip; prior skips: intake, rules-engine, audit-store, memo-agent-core, auth-rbac, secrets-config, ui-shell, corpus-generator, quality-gates, admin-cli, ui-queue, ui-memo-view). No infra-design artifact filed (matching the twelve prior logged skips). Code Generation NEXT (last stage for ui-approval-gate; Part-1-plan-then-Part-2-generate with its own approval — no code written until the user reviews the plan). NO code; **WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) UNTOUCHED**; tier-B NOT authorized; no other unit started. **STOPPED at the Infrastructure-Design 2-option gate (1. Request Changes / 2. Continue to Next Stage → Code Generation)** for the user's decision.

**Infrastructure Design APPROVED 2026-07-09 (Continue, SKIP confirmed). Code Generation UNDERWAY — Part 1 (Planning) ONLY**: `guide-docs/build/plans/ui-approval-gate-code-gen-plan.md` WRITTEN (TDD tests/lint-first, leaf-first, JS/JSX no-TS, mirroring the realized `shell`/`queue`/`memoView` convention) with: §0 unit context (US-UI-3, first UI **write path**; ui-shell import-only incl. **`RoleGate` first real use**; siblings **mirrored-not-imported**; WIRE-1 R4+R5 by shape); §1 component→module map **C1–C9 → `frontend/src/approvalGate/**`** (C9 `copy.js` advisory-clean Fold-2, C2 `commitFetchSeam.js` dual-op `createCommitFetch`/`fetchContext`/`submitApprove`/`buildCommitRequest`-narrow/`normalizeError`/JSDoc, C4 `RecommendationContext`, C7 `CommittedConfirmation` `{decision,context}`-only+header, C3 `CommitStateView` four-status, C6 `CommitConfirmDialog` sole `onConfirm` holder+header, C5 `ApproveAffordance` `{onApprove}`-only RoleGate-wrapped+header, C1 `ApprovalGateView` owns machine wires `onConfirm` ONLY to C6, C8 StructuralGuard) — **header comments on C5/C6/C7 called out as EXPLICIT deliverables** (mirroring NarrativeRegion); §2 TDD test→target map every `NFR-AG-*` at NFR-pinned tier (NOFINAL single-call-site scan / **CONFIRM+CANCEL full-highest teeth** dual-op single-double / RBAC all-roles+null stub+no-backend-import / BODY deep-equality / ERROR table-driven 200·403·409·400/422 / SCOPE-APPROVE / NOREFETCH both-counts-frozen / RECOVERY two-directional / FETCH per-state+consolidated transition / COPY/ADVISORY[**unmodified**]/NAMESPACE / TESTID/NOTS/REFNOTOWN incl **`noCreateCommitFetchImportInPresentational` ND-Fold-3** / PERF/A11Y soft) **no orphan**; §3 leaf-first Part-2 Steps 0–11 UNCHECKED (Step 0 scaffold+shared-config extension → C9→C2→C4→C7→C3→C6→C5→C1→C8→coverage→summary); §4 HOLDS; §5 coverage gate (Vitest folded; baseline `src/shell`+`src/queue`+`src/memoView` **100%** no regression, QA-6 ≥90% on `src/approvalGate`; **backend pytest 850/31 untouched**, separate runner); §6 **SIX numbered `[Answer]` questions LEFT BLANK** (Q1 shared-config extension; Q2 dual-op `makeCommitDouble` factory independent-counting; Q3 ERROR-1 four-status shared envelope fixtures; Q4 `commitFetchSeam` JSDoc two-operation contract; Q5 consolidated transition own file; Q6 confirm/committed copy verification vs corrected advisory-clean `copy.js`); §7 gate. NO code generated; NO file under `frontend/src/approvalGate/` created; no dependency edited; **WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) UNTOUCHED**; tier-B NOT authorized; no other unit started. **STOPPED at the plan-file gate** awaiting the user's filled `[Answer]` tags → ambiguity-check (run AFTER the answers) → Part 2 on explicit go (plan re-saved with answers embedded per standing convention).

**UPDATE 2026-07-09 (Code-Gen Part 2 EXECUTED — FINALIZED at the completion gate; see the COMPLETE section below)**: six `[Answer]` tags filled (all **A**). Ambiguity-check CLEAN — **three clarity-folds, no STOP**: **CG-Fold-1** (check i — `makeCommitDouble()` returns a FRESH instance per call, each op an independently-counted spy with own `calls[]`; per-test construction + RTL auto-cleanup → no call-count leakage), **CG-Fold-2** (check ii — the spies are programmable/sequenceable [`resolveWith`/`rejectWith`/`hang`/`sequence`]; RECOVERY-1 uses a fail-then-succeed SEQUENCE distinct from the static ERROR-1 table, same one factory), **CG-Fold-3** (check iii — consistent module vocabulary [seam / commit trigger / single call site] across the C2 JSDoc + C5/C6/C7 header comments). Re-read the frozen primitives + sibling test/rule templates on disk. **Part 2 GENERATED exactly per plan §3 Steps 0–11 (all `[x]`)** → NEW `frontend/src/approvalGate/` (JS-native, NO TypeScript, NO Python/backend dependency, touches NO frozen unit): config extension (`vitest.config.js` + `eslint-rules/approvalGate.js` new `approval-testid-convention` + `eslint.config.js` block — no frozen-src edit) + **8 source modules** (`copy.js` advisory-clean, `commitFetchSeam.js` dual-op `createCommitFetch`/`fetchContext`/`submitApprove`/narrow-`buildCommitRequest`/`normalizeError`/JSDoc, `RecommendationContext`, `CommittedConfirmation` [header], `CommitStateView`, `CommitConfirmDialog` [header], `ApproveAffordance` [header], `ApprovalGateView` owns machine + wires `onConfirm` ONLY to C6) + **20 co-located test files**. One TDD-iteration fix (NOFINAL-1 scan corrected from bare-word to invocation/import — the header comment legitimately names `submitApprove` to document its absence). **Results: 237 Vitest tests passed (61 files); `src/approvalGate` 100% Stmts/Branch/Funcs/Lines (QA-6 ≥90% PASSED); frontend total 852/852 stmts · 210/210 branch · 44/44 funcs · 100%; `src/shell` + `src/queue` + `src/memoView` UNTOUCHED at 100%; ESLint clean.** Every `NFR-AG-*` at its NFR-pinned tier; the load-bearing commit-lifecycle teeth (NOFINAL/CONFIRM/CANCEL) + RBAC all-roles+null + BODY deep-equality + ERROR four-status table + NOREFETCH both-counts-frozen + RECOVERY two-directional + FETCH per-state+consolidated-transition all green; the four by-construction guarantees enforced by teeth + StructuralGuard + header comments; advisory-vocabulary lint UNMODIFIED. **Backend pytest 850/31 UNTOUCHED** (zero backend files modified — git-verified; separate runner/tree). Wrote `guide-docs/build/ui-approval-gate/code/code-summary.md`; refreshed `testresults.txt` (frontend result alongside, not merged); re-saved the plan (§6.5 + CG-Fold-1..3 + Steps `[x]`); appended audit. HOLDS honored (ui-shell reused-import-only incl. RoleGate first real use; ui-queue + ui-memo-view mirrored-never-imported; no local FORBIDDEN_TERMS; WIRE-1 R4/R5 by shape only, no real network; RoleGate cosmetic; no LLM; no TS). **Standardized Code-Gen 2-option gate PRESENTED; STOPPED for the user's diff review — the LAST stage for ui-approval-gate. On approval → `ui-approval-gate` (U7) becomes the 14TH fully-complete unit** (FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓) **and the 4TH completed frontend/React unit** (after ui-shell, ui-queue, ui-memo-view); unblocks `ui-override-form` (U8) next in the working sequence. WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) UNTOUCHED; tier-B NOT authorized; no other unit started.

## ✅ BUILD → `ui-approval-gate` (U7) COMPLETE — the FOURTEENTH fully-complete unit (4th UI/React unit; first real write path) — 2026-07-09
**`ui-approval-gate` (U7) — COMPLETE**: Code-Gen 2-option completion gate **APPROVED** → **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · Code-Gen ✓**. The **FOURTEENTH** fully-complete build-loop unit and the **4th** completed frontend/React unit (after `ui-shell`, `ui-queue`, `ui-memo-view`) — the **first UI unit with a real write path** (R5 `POST …/commit`). **237 Vitest tests passed (61 files); `src/approvalGate` 100% Stmts/Branch/Funcs/Lines (QA-6 ≥90% PASSED); frontend total 852/852 stmts · 210/210 branch · 44/44 funcs · 100%; `src/shell` + `src/queue` + `src/memoView` UNTOUCHED at 100%; ESLint clean; backend pytest 850/31 UNTOUCHED (git-verified, zero backend files modified — separate runner/tree).** Artifacts: `guide-docs/build/ui-approval-gate/{functional-design,nfr-requirements,nfr-design,code/code-summary.md}` + `frontend/src/approvalGate/` (8 source modules + 20 co-located test files) + refreshed `testresults.txt`.

**Concrete invariant verification (the load-bearing teeth + by-construction guarantees, all green)**: the **commit-lifecycle teeth** — **NOFINAL-1** (exactly one `.submitApprove(` call site; `ApproveAffordance` has no invocation and no seam import), **CONFIRM-1** (Approve → 0 submit / 1 fetch cross-guard, Confirm → 1 submit), **CANCEL-1** (open+Cancel → both counts unchanged, context identical) — plus **all four by-construction guarantees** (C5 `ApproveAffordance` `{onApprove}`-only [no submit capability]; C6 `CommitConfirmDialog` sole `onConfirm` holder [single call site]; C7 `CommittedConfirmation` `{decision,context}`-only [no seam]; C2 narrow `buildCommitRequest` [no `reason`/`underwriter_id`]) — pass as the **concrete verification of the confirm-gated-commit invariant and the RoleGate-cosmetic-not-authz pattern** (`RoleGate can="act"` is chrome/defense-in-depth only; AUTHZ-1 backend re-check is the real gate; 403 = genuine error). First real `RoleGate` composition in the codebase.

**Defect surfaced + correctly fixed (recorded)**: the **NOFINAL-1 scan refinement** — the single-call-site assertion was corrected from a bare-word/textual-occurrence scan to an **invocation + seam-import** scan, because the header-comment-driven design legitimately **names** `submitApprove` in C5's header comment to document its *absence*. A bare-text scan would have false-positived on that documentation; the invocation/import scan is the correct structural check. This is a **real defect the header-comment-driven design surfaced and the TDD iteration correctly fixed**.

**P1 roster (17 P1 units) — 15 COMPLETE**: 11 non-UI (intake, document-sanitizer, rules-engine, memo-agent-core, auth-rbac, audit-store, quality-gates, corpus-generator, database, secrets-config, admin-cli) + **4 UI** (ui-shell, ui-queue, ui-memo-view, **ui-approval-gate**). **UI P1 remaining (2)**: `ui-override-form` (U8) · `ui-history` (U9) — **both now unblocked**.

**Cross-unit / Deferred Decisions register (current, unchanged in substance)**: **WIRE-1 ✅ PINNED** (`guide-docs/build/wire-1/api-contract.md`; pinned since U6) — **now exercised for real by BOTH R4 (read) and R5 (commit) for the first time** (ui-approval-gate is the first consumer to touch R5); **tier-B corpus run — UNAUTHORIZED**; **audit_store Docker-guard hygiene gap — DEFERRED** (non-blocking). All frozen artifacts (WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate) UNTOUCHED; no LLM; no TypeScript.

**Next (per the working sequence `ui-queue → ui-memo-view → ui-approval-gate → ui-override-form → ui-history`)**: `ui-override-form` (U8) — **NOT started** (awaiting the user's separate go). **Inherited-but-must-re-examine (not assume-transferable)**: U8 introduces the one thing U7 deliberately deferred — the **mandatory-reason override path** (`action == "override"` → `reason` required non-blank; blank → **409** per WIRE-1 §4/§5 + `BR-COMMIT-GATE`). The R5 patterns to carry forward *deliberately*, not by default: (a) the **dual-operation `commitFetchSeam`** — U8 adds a *reason* payload, so `buildCommitRequest` is **narrow by design in U7** (no `reason`/`underwriter_id`) and must be **widened for override** — this is a genuine contract change, not a copy-paste; (b) the **by-construction single-call-site discipline** (sole `onConfirm` holder / one `.submitApprove(`) — re-examine because U8's override introduces a **required free-text input** feeding the commit body, a new surface the U7 `{onApprove}`-only affordance never carried; (c) the **RoleGate-cosmetic-not-authz** pattern transfers as-is (still `underwriter`-only, still server-side-re-enforced), but the **409 blank-reason** path is a new client-visible error state U7's ERROR-1 table did not exercise.

## 🧩 BUILD → `ui-override-form` (U8) — STARTED; FD Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-09
**`ui-override-form` (U8) — STARTED** (working sequence: ui-queue → ui-memo-view → ui-approval-gate → **ui-override-form** → ui-history). Loaded the **underwriting-rules** domain skill (advisory-only vocabulary + human-in-the-loop mandatory-override-reason). **DISCOVER-carryover CLEAN** — no `guide-docs/build/ui-override-form/` dir, no `frontend/src/overrideForm/` code, no plan file. **Frozen contracts re-read (by value/shape, none edited)**: `unit-of-work.md §U8` (comprehensive/invariant-bearing, CON-BR4/US-UI-5/FR-UI-4; CON-BR4 write-enforcement single-sourced in `audit-store`, UI = consuming facet); `audit_store/commit_service.py` `_gate` (override rejected **iff** `reason is None or reason.strip()==""` — **trim-then-empty** — + AUTHZ-1 re-check → WIRE-1 **409 commit_conflict**); WIRE-1 R5 (`{action, reason required-non-blank iff override}`, underwriter_id from session, underwriter-only); frozen `ui-shell` `RoleGate` (`can="act"` cosmetic) / `roleContext` / `copy` (**`COMMIT_ACTION_LABELS.override='Override'` already frozen**; override ≠ system `DECLINE-RECOMMEND`); frozen U7 `commitFetchSeam` (`buildCommitRequest` STRUCTURALLY emits only `{action:'approve'}` — no `reason` param → U8 needs a widened/new builder), `ApproveAffordance` ({onApprove}-only), `CommitConfirmDialog` (sole `onConfirm` = single call site), `ApprovalGateView` (machine + Q5-A standalone own-R4-read).

**Depth = COMPREHENSIVE** (classification-forced, invariant-bearing; the write-path unit exercising the mandatory-reason gate) — to be confirmed at Q1.

**FD Part 1 plan** `guide-docs/build/plans/ui-override-form-functional-design-plan.md` WRITTEN (**NO FD artifact generated**) — §0 carryover, §1 frozen-contract re-read, §2 depth, §3 contingent component/seam sketch (`overrideForm/`: `overrideFetchSeam` · `OverrideFormView` · `OverrideReasonInput` [NEW] · `OverrideAffordance` · `OverrideConfirmDialog` · `RecommendationContext` · `CommitStateView` · `CommittedConfirmation`), §4 **six open `[Answer]` questions** (Q1 depth; Q2 widened builder shape + non-blank enforcement layer [rec: new own-local `createOverrideFetch`/`buildOverrideRequest(recommendationId, reason)` + UI trim-then-empty guard as **non-authoritative** defense-in-depth, matching backend `str.strip()`, CON-BR4 single-sourced]; Q3 reason-state vs single-call-site discipline [rec: reason in orchestrator, affordance stays capability-free, "no commit capability" refined to *no seam/trigger reference* not *no payload*]; Q4 409 surfacing [rec: generic by `error.code`, AUTHZ-1-mirror defense-in-depth; 409 live because it also = already-committed]; Q5 own R4 read [rec: standalone, mirror U7 Q5-A]; Q6 two-views-vs-combined [rec: two separate views, combined screen = deferred composition-root concern given frozen U7 — flagged as the user's explicit call, not improvised]). **STOPPED at the plan-file gate** awaiting Q1–Q6.

**Guardrails held**: no FD artifact generated; **WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) UNTOUCHED**; CON-BR4 single-sourced in audit-store; no LLM; no TypeScript; tier-B NOT authorized; no other unit started. **Register unchanged**: WIRE-1 PINNED (R4+R5 now consumed by a second write-path unit); tier-B UNAUTHORIZED; audit_store Docker-guard gap DEFERRED. P1 remaining after U8: `ui-history` (U9).

## 🧩 BUILD → `ui-override-form` (U8) — Functional Design Part 2 COMPLETE (three FD artifacts); STOP at FD 2-option gate — 2026-07-09
**FD Part 1 APPROVED** — Q1–Q6 answered (**all A**), embedded in `guide-docs/build/plans/ui-override-form-functional-design-plan.md`. **Ambiguity-check CLEAN — no STOP; three folds, one a VERIFIED correction**:
- **FD-OVR-Fold-1 (check i — EMPIRICALLY VERIFIED, a real correction).** Tested CPython 3.12 `str.strip()` vs Node `String.prototype.trim()` on disk — **NOT equivalent**: Python strips **U+001C–U+001F, U+0085 (NEL)** which JS `trim()` does **not** (UI-**looser** → UI allows, backend 409s); JS strips **U+FEFF** which Python does **not** (UI-**stricter** → harmless false-block). So Q2-A's "identical to `str.strip()`" claim is **false**. **Resolved WITHOUT a STOP and WITHOUT improvising**: the approved Q2-A (guard **non-authoritative**) + Q4-A (backend **409** surfaced generically) already absorb the divergence — UI-looser cases land in exactly the race/bypass 409 tail; **CON-BR4 stays single-sourced in `audit-store`**. Corrected the binding framing (best-effort `trim()`, **NOT** byte-identical; backend authoritative; divergence resolves via 409) rather than build a custom Unicode matcher (over-build). 
- **FD-OVR-Fold-2 (check ii — confirmed extension).** The capability-free components **do** need the analogous StructuralGuard scan; U8's guard set **grows by one** for the NEW `OverrideReasonInput` (no seam import) + single `submitOverride` call site + `OverrideAffordance` no-invocation/no-import + no `createOverrideFetch` in presentational. Affirmative deliverable, not a gap.
- **FD-OVR-Fold-3 (check iii — legitimately punted).** Q6-A composability = **standard React mount** (`OverrideFormView({overrideFetchSeam, applicationId})` mounted alongside frozen `ApprovalGateView`); **no speculative composition prop added now** (YAGNI). Zero design debt.

**FD Part 2 GENERATED** — three artifacts under `guide-docs/build/ui-override-form/functional-design/`:
- `domain-entities.md` — R4 read (own, Q5-A); **R5 override body `{action:"override", reason}`**; the **widened `buildOverrideRequest(recommendationId, reason)`** (reason a required positional param — the frozen `buildCommitRequest` could emit only `{action:'approve'}`); `CommittedDecision` echo with **non-null reason**; **409 dual-cause** (already-committed + blank-reason race/bypass tail); `CommitAction` `override` ≠ system `DECLINE-RECOMMEND`; own-local `overrideFetchSeam`; advisory-clean `OVERRIDE_COPY`; component inventory incl. the **capability-free `OverrideReasonInput`**; full state machine (reason-carrying `ready`+`confirming`, **reason preserved** across Cancel/errorCommit).
- `business-rules.md` — **BR-OVR-1..12**; the new rules are **BR-OVR-8** (mandatory non-blank reason — **non-authoritative** UX guard; server `_gate` single-sourced; trim-divergence documented) and **BR-OVR-12** (reason preserved across cancel/error + echoed in the confirm dialog); rule index; Security-Guardrails table with the **mandatory-reason-gate row as real content**.
- `business-logic-model.md` — **two VALIDATED Mermaid diagrams** (7-rule compliant — checked programmatically: no forbidden label chars, balanced nodes/labels, all arrow endpoints defined) + text alternatives — the reason→confirm→override flow, and the **TWO server-authoritative gates** (authz AUTHZ-1 **+** reason BR-COMMIT-GATE) defense-in-depth; consumer/dependency map; invariant self-check.

**STOPPED at the FD 2-option completion gate** (1. Request Changes / 2. Continue to Next Stage — NFR Requirements). **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) **UNTOUCHED**; CON-BR4 single-sourced in audit-store; no LLM; no TypeScript; tier-B NOT authorized; no other unit started.

## 🧩 BUILD → `ui-override-form` (U8) — FD APPROVED (Continue, with one scoped §1 formatting fix); NFR Requirements Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-09
**FD APPROVED 2026-07-09** — user chose Continue after one Request-Changes round (business-logic-model.md §1: the orphaned sentence between the Mermaid fence and the `### 1.1 Text alternative` heading was moved into the text alternative as a closing note after step 9; no other content change). **FD final: BR-OVR-1..12** + component/prop inventory (incl. capability-free `OverrideReasonInput`) + full state machine (reason preserved across cancel/error) + two-server-gate (AUTHZ-1 + BR-COMMIT-GATE) defense-in-depth note.

**NFR Requirements UNDERWAY (COMPREHENSIVE)** — Part 1 plan `guide-docs/build/plans/ui-override-form-nfr-requirements-plan.md` WRITTEN, built on the frozen FD (re-opening none): §0 **dual-operation reason-carrying seam** testability principle (`fetchContext` + `submitOverride(recommendationId, reason)`, single injected double, each op an independently-counted spy recording args incl. the `reason` — mirror-not-import U7's NFR-AG-Fold-1); §1 draft **NFR-OVR-*** map over **BR-OVR-1..12** — load-bearing teeth **NOFINAL-1 / CONFIRM-1 / CANCEL-1**, the **NEW REASONGATE-1** (mandatory non-blank reason teeth + the `trim()` vs `str.strip()` divergence **documentation** per FD-OVR-Fold-1, non-authoritative), **RBAC-1** (all-3-roles+null), **BODY-1** (body deep-equals `{action:'override', reason}`, no `underwriter_id`), **ERROR-1** (409 dual-cause under one `commit_conflict` code), **NAMESPACE-1** (override ≠ DECLINE-RECOMMEND), **NOREFETCH-1**, **REFNOTOWN-1** (+`noApprovalGateImport` — NEW, first sibling that must also not import frozen U7), **RECOVERY-1** (reason preserved), **REASONKEEP-1** (NEW), **CAPFREE-1** (NEW — extends U7 ND-Fold-3 to the new `OverrideReasonInput`), **FETCH-1**; inherited COPY/ADVISORY (OVERRIDE_COPY preliminarily clean — no `decision`-token collision, unlike U7)/TESTID/NOTS; medium NAMESPACE-1; soft PERF-1/A11Y-1; governance SCOPE-1; §2 traceability (no orphan); **§3 FOUR open `[Answer]` questions BLANK** — Q1 depth · Q2 (flagged) `OverrideReasonInput` capability-free verification (rec: structural import-scan + prop-contract RTL) · Q3 (flagged) whitespace-variant coverage (rec: representative set + send-as-entered payload sub-decision + divergence doc; rejects the exotic-Unicode-matrix over-build) · Q4 (flagged) reason-echo vs preservation assertion structure (rec: two distinct assertions). **STOPPED at the plan-file gate** for the user's review + answers (no NFR artifact, no ambiguity-check yet).

**Guardrails held**: no NFR artifact generated; **WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) UNTOUCHED**; CON-BR4 single-sourced in audit-store; no LLM; no TypeScript; tier-B NOT authorized; no other unit started.

## 🧩 BUILD → `ui-override-form` (U8) — NFR Requirements Part 2 COMPLETE (two artifacts); STOP at NFR-Req 2-option gate — 2026-07-09
**NFR Requirements Part 1 ANSWERED** — Q1–Q4 (**all A**), embedded in `guide-docs/build/plans/ui-override-form-nfr-requirements-plan.md`. **Ambiguity-check CLEAN — no STOP; three folds, ALL VERIFIED AGAINST REAL CODE (not assumed)**:
- **NFR-OVR-Fold-1 (check i — VERIFIED).** Re-read `audit_store/record_schema.py` + `commit_service.py`: `CommittedDecision.reason` is a plain `Optional[str]=None` with **no validator/normalization**; `_gate` checks `reason.strip()==""` but **does not mutate**; `_assemble` passes it **verbatim**. So the backend stores the reason **as received** → the UI "send as-entered" (Q3-A) and the R5 `CommittedDecision.reason` echo (BR-OVR-9) are **consistent, no divergence**.
- **NFR-OVR-Fold-2 (check ii).** REASONKEEP-1's confirm-dialog echo (`confirming` state, client `reason` state, `override-confirm-reason-echo`) and NOREFETCH-1's committed display (`committed` state, R5 echo, `override-committed-reason`) are **genuinely distinct** states/nodes/sources — not the same logic tested twice.
- **NFR-OVR-Fold-3 (check iii — VERIFIED).** Audited **all 21** `OVERRIDE_COPY` strings against the real `FORBIDDEN_TERMS.systemOutput` detector (word-boundary, case-insensitive, via node) — **zero trip**; unlike U7 (whose `confirmBody` needed correction), U8's copy is **clean as-drafted** → ADVISORY-1 holds with no copy change, lint UNMODIFIED.

**NFR Requirements Part 2 GENERATED** — two artifacts under `guide-docs/build/ui-override-form/nfr-requirements/`:
- `nfr-requirements.md` — finalized **NFR-OVR-*** targets (§1) each pass/fail + acceptance + tier + rigor; load-bearing teeth **NOFINAL-1 / CONFIRM-1 / CANCEL-1**, the NEW **REASONGATE-1** (whitespace fixture set `{"", " ", "\t", "\n", " \t\n "}` → zero POSTs; non-blank control → one POST with reason **verbatim/as-entered**; trim-vs-strip divergence **documentation** test), **REASONKEEP-1** (two distinct assertions), **CAPFREE-1** (structural import-scan + prop-contract RTL); **BODY-1** (`{action:'override', reason}`, no `underwriter_id`), **ERROR-1** (409 dual-cause), **NOREFETCH-1** (echo == sent, backend un-normalized), **REFNOTOWN-1** (+`noApprovalGateImport`), RECOVERY-1, FETCH-1, inherited COPY/ADVISORY/TESTID/NOTS, medium NAMESPACE-1, soft PERF-1/A11Y-1, governance SCOPE-1; §0 dual-operation reason-carrying seam (Fold-A); §2 traceability no-orphan + 4 folds; §3 Security-Guardrails table with the **mandatory-reason-gate row as real content**; §4 governance note (both advisory-vocabulary + reason-gate single-sourcing verified).
- `tech-stack-decisions.md` — **D1–D14** inheriting the frozen substrate **unchanged, no new dependency** — adds only the dual-operation reason-carrying capturing double, the capability-free verification (Q2), the whitespace fixture set (Q3), and the two-assertion echo/preservation structure (Q4).

**STOPPED at the NFR-Requirements 2-option completion gate** (1. Request Changes / 2. Continue to Next Stage — NFR Design). **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) **UNTOUCHED**; CON-BR4 single-sourced in audit-store; no LLM; no TypeScript; tier-B NOT authorized; no other unit started.

## 🧩 BUILD → `ui-override-form` (U8) — NFR Requirements APPROVED; NFR Design Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-09
**NFR Requirements APPROVED 2026-07-09** (Continue). **NFR Design UNDERWAY (COMPREHENSIVE)** — Part 1 plan `guide-docs/build/plans/ui-override-form-nfr-design-plan.md` WRITTEN, built on the frozen FD + approved NFR-Req (re-opening none): §1 **twelve patterns P1..P12** each structurally meeting its NFR-OVR-* target(s) — **P1** SingleCallSiteConfirmGatedCommitPattern (`onConfirm` closes over trigger **+** reason), **P2** MandatoryNonBlankReasonGatePattern (**NEW** load-bearing; by-construction single-predicate-derived affordance enablement), **P3** CosmeticRoleGateCompositionPattern, **P4** OverrideRequestBuilderPattern (reason **required positional**, no `underwriter_id`), **P5** PerStatusEnvelopeToRenderPattern (dual-cause 409), **P6** ConfirmationFromEchoPattern (reason in echo), **P7** CauseDifferentiatedRecoveryPattern (reason preserved), **P8** ReasonStatePreservationPattern (**NEW**), **P9** CapabilityFreeComponentPattern (extended to `OverrideReasonInput` + header comment), **P10** DualOperationFetchSeam + ExtendedStateMachine, **P11** StructuralGuardPattern (**+`noApprovalGateImport`**), **P12** ReferencedObservedBoundaryPattern (soft/gov); §2 **ten components C1..C10** with **exact by-construction prop shapes** (`OverrideReasonInput {value,onChange,testid}`; `OverrideAffordance {onOverride,disabled,testid}` disabled **derived from the one reason predicate**; `OverrideConfirmDialog {onConfirm,onCancel,reason,testid}` sole trigger; `CommittedConfirmation {decision,context,testid}`; `buildOverrideRequest(recommendationId, reason)`); §3 reference-not-own (incl. `noApprovalGateImport`); §4 component→target coverage — **all 20 targets, no orphan**; §5 **VALIDATED Mermaid** (11 nodes/14 edges, 7-rule checked programmatically) showing **BOTH** the single-call-site (only inbound solid edge into `submitOverride` from Dialog) **AND** the reason-state flow (ReasonInput→View→{Affordance disabled, Dialog echo, submitOverride arg}) + text alt; **§6 FOUR open `[Answer]` questions BLANK** — Q1 depth · **Q2 (key)** REASONGATE by-construction single-predicate-derived enablement · Q3 builder reason-required-positional · Q4 reason preservation as an independent untouched slice; §7 planned Part-2 + precedent-determined header-comment folds (incl. NEW `OverrideReasonInput`); §8 holds; §9 gate. **STOPPED at the plan-file gate** for the user's review + answers (no NFR-Design artifact, no ambiguity-check yet).

**Guardrails held**: no NFR-Design artifact generated; **WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) UNTOUCHED**; CON-BR4 single-sourced in audit-store; no LLM; no TypeScript; tier-B NOT authorized; no other unit started.

## 🧩 BUILD → `ui-override-form` (U8) — NFR Design Part 2 COMPLETE (two artifacts); STOP at NFR-Design 2-option gate — 2026-07-09
**NFR Design Part 1 ANSWERED** — Q1–Q4 (**all A**), embedded in `guide-docs/build/plans/ui-override-form-nfr-design-plan.md`. **Ambiguity-check CLEAN — no STOP; three folds**:
- **ND-OVR-Fold-i (check i).** The belt-and-suspenders `onConfirm` re-check stays **genuinely OPTIONAL**: REASONGATE-1's teeth (driving the full `Override→Confirm` attempt) already catch a broken predicate→`disabled` wiring; the only path they don't exercise ("reason cleared blank after dialog opened") is **unreachable by design** — the reason is **frozen during `confirming`** (read-only echo, not an editable input). The re-check guards only a future-refactor hazard; retained as documented insurance (presence lightly asserted), **not** a hard gate.
- **ND-OVR-Fold-ii (check ii).** No committed-state ambiguity — the committed display's single source of truth is the **`CommittedDecision` echo (`decision.reason`)**; `CommittedConfirmation` is `{decision,context}`-only and structurally cannot read the client `reason` slice; values coincide (Fold-1), source unambiguous; pre-submission reads the client slice (confirm echo), post-submission the echo (committed) — distinct nodes/states/sources.
- **ND-OVR-Fold-iii (check iii).** One `reason` slice — the predicate applies `trim()` **transiently in the boolean only** (never written back); the builder sends the **same** slice **verbatim/as-entered**; identical underlying value, no two-copy divergence.

**NFR Design Part 2 GENERATED** — two artifacts under `guide-docs/build/ui-override-form/nfr-design/`:
- `nfr-design-patterns.md` — **§P1..§P12** each with the **by-construction prop mechanism** + how it structurally meets its `NFR-OVR-*` target(s) + tier + rigor (P1 single-call-site extended for reason; **P2 mandatory-reason gate — single-predicate-derived enablement** + optional belt-and-suspenders; P4 reason-required builder; P5 dual-cause 409; P6 confirmation-from-echo + source-of-truth note; P7 recovery; **P8 reason-state-preservation**; P9 capability-free incl. `OverrideReasonInput` header comment; P10 dual-op seam + state machine; **P11 StructuralGuard incl. `noApprovalGateImport`**; P12 soft/gov); **VALIDATED** pattern-integration Mermaid (12 nodes/17 edges, 7-rule-checked) + text alt; §14 traceability — **all 20 targets, no orphan**.
- `logical-components.md` — **C1..C10** with **EXACT by-construction prop shapes** (`OverrideAffordance {onOverride,disabled,testid}`; `OverrideReasonInput {value,onChange,testid}`; `OverrideConfirmDialog {onConfirm,onCancel,reason,testid}`; `CommittedConfirmation {decision,context,testid}`; `buildOverrideRequest(recommendationId, reason)`) + header-comment self-evidence; **VALIDATED** component-relationship Mermaid (11 nodes/14 edges) showing **BOTH** the single-call-site **AND** the reason-state flow + text alt; reference-not-own check (**reused** vs **mirrored-not-imported** vs **consumed-by-shape** kept distinct, incl. the NEW `noApprovalGateImport`); component→target coverage (no orphan); settled items.

**STOPPED at the NFR-Design 2-option completion gate** (1. Request Changes / 2. Continue to Next Stage — Infrastructure Design). **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) **UNTOUCHED**; CON-BR4 single-sourced in audit-store; no LLM; no TypeScript; tier-B NOT authorized; no other unit started.

## 🧩 BUILD → `ui-override-form` (U8) — NFR Design APPROVED; Infrastructure Design SKIPPED (logged, rule-justified); STOP at Infra 2-option gate; NEXT = Code Generation — 2026-07-09
**NFR Design APPROVED 2026-07-09** (Continue). **Infrastructure Design SKIPPED-logged 2026-07-09** — assessed **AT THE STAGE** (not pre-committed) per CLAUDE.md ("Skip IF: No infrastructure changes / already defined") + execution-plan.md §3 "little independent infra". Four-check assessment: (1) no untrusted parsing / no subprocess sandbox; (2) no independent persistence it provisions — R4 read + R5 write (with the reason) through the **own-local `overrideFetchSeam`** (mocked in tests), never touching a DB or the audit-store persistence layer directly (persistence is audit-store's, provisioned by `database` — the one real non-skip); (3) no LLM/provider access; (4) bundler/dev-server + Vercel topology stays `deploy-config` (P2); the real `overrideFetchSeam` wiring + R4/R5 route impl are the composition root's / Build & Test's. **Ambiguity-check surfaced NO genuine unit-owned infra concern** — the mandatory-reason gate is a new category of **application behavior** (a reason field + a non-authoritative client guard), **NOT** infrastructure; the write goes through the **same deferred composition-root wiring** as every prior UI unit's read/write path (mirrors the ui-approval-gate reasoning). A logged SKIP matching the **fourteen prior SKIPs** (`database` the sole real non-skip) — **not silent**. **NEXT = Code Generation** (the last stage for U8; Part-1-plan-then-Part-2-generate, its own approval gate).

**STOPPED at the Infra-Design 2-option completion gate** (1. Request Changes / 2. Continue to Next Stage — Code Generation). **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) **UNTOUCHED**; CON-BR4 single-sourced in audit-store; no LLM; no TypeScript; tier-B NOT authorized; no other unit started; no code under `frontend/src/overrideForm/`.

## 🧩 BUILD → `ui-override-form` (U8) — Infra SKIP accepted; Code Generation Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-09
**Infrastructure Design SKIP accepted 2026-07-09** (Continue). **Code Generation UNDERWAY — Part 1 (Planning) ONLY**: `guide-docs/build/plans/ui-override-form-code-gen-plan.md` WRITTEN (TDD tests/lint-first, leaf-first, JS/JSX no-TS, mirroring the realized `shell`/`queue`/`memoView`/`approvalGate` conventions), built on the frozen FD + approved NFR-Req + approved NFR-Design (re-opening none): §1 **component→module map C1..C10** → concrete files under `frontend/src/overrideForm/` (header comments on **C5/C6/C7/C8** as **explicit deliverables** — C5 `OverrideReasonInput {value,onChange}`-only, C6 `OverrideAffordance {onOverride,disabled}`-only disabled-derived, C7 `OverrideConfirmDialog` sole-`onConfirm`+reason echo, C8 `CommittedConfirmation {decision,context}`-only reason-from-echo; C2 reason-required `buildOverrideRequest`+JSDoc; C9 StructuralGuard incl. `noApprovalGateImport`); §2 **TDD test→target map** — every `NFR-OVR-*` at its NFR-pinned tier, no orphan (load-bearing NOFINAL/CONFIRM/CANCEL teeth; the **NEW REASONGATE-1** whitespace-set + verbatim-reason + `reasonTrimDivergence` doc; **REASONKEEP-1** two distinct assertions; **CAPFREE-1** structural-scan + prop-contract-RTL; ERROR-1 409-dual-cause; REFNOTOWN-1 incl. `noApprovalGateImport` + `no-createOverrideFetch-in-presentational`); §3 **leaf-first Steps 0–12 (unchecked)** C10→C2→C4→C5→C8→C3→C7→C6→C1→C9→coverage→summary; §4 HOLDS restated; §5 coverage/quality gate (baseline `shell`+`queue`+`memoView`+`approvalGate` 100% / frontend 852/852; backend pytest **850/31 untouched**); **§6 EIGHT open `[Answer]` questions BLANK** (Q1 shared-config extension · Q2 dual-op reason-carrying double factory · Q3 whitespace-fixture literals + verbatim-reason + divergence doc [exotic-Unicode over-build rejected] · Q4 ERROR 4-status fixtures 409-dual-cause · Q5 `overrideFetchSeam` JSDoc incl. reason param · Q6 distinct testid naming confirm-echo vs committed-reason · Q7 consolidated transition test own file · Q8 verbatim-clean `OVERRIDE_COPY` consumption); §7 gate. **STOPPED at the plan-file gate** for the user's review + answers (no code, no ambiguity-check yet).

**Guardrails held**: no code generated; **WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) UNTOUCHED**; no local FORBIDDEN_TERMS; CON-BR4 single-sourced in audit-store; no LLM; no TypeScript; tier-B NOT authorized; no other unit started.

## ✅ BUILD → `ui-override-form` (U8) Code Generation Part 2 COMPLETE — 340 Vitest passed; src/overrideForm 100%/98.36%br (QA-6 PASSED); STOP at completion gate (LAST stage) — 2026-07-09
**Code-Gen Part 1 plan ANSWERED** — Q1–Q8 (**all A**), embedded in `guide-docs/build/plans/ui-override-form-code-gen-plan.md`. **Ambiguity-check RUN → CLEAN, no STOP** — one consistency point resolved WITHOUT a gap: plan §2 pins TESTID-1 as `^override-[a-z]+(-[a-z0-9]+)+$` (the `queue`-family ≥3-segment `+` form, NOT the 2-segment `approval-gate` shape), which matches the plan's own `override-<element>-<purpose>` convention verbatim → every testid named 3-part (root `override-form-view`, badges `override-recommendation-value`/`override-confidence-value`, the distinct `override-confirm-reason-echo` vs `override-committed-reason`). No improvisation.

**Code-Gen Part 2 GENERATED** — leaf-first, tests-first, §3 Steps 0–12 all **[x]**, under `frontend/src/overrideForm/` (+ shared-config extension):
- **Production (C1–C10)**: `OverrideFormView.jsx` (C1 — owns the phase machine **and the independent `reason` slice** P8; exported single `isReasonPresent` predicate; `onConfirm` wired **ONLY** to the dialog, P1) · `overrideFetchSeam.js` (C2 — dual-op reason-carrying seam, `submitOverride(recommendationId, reason)`, reason-required `buildOverrideRequest`, JSDoc contract) · `components/` C3 `CommitStateView` (409 dual-cause one code) · C4 `RecommendationContext` · **C5 `OverrideReasonInput`** (NEW `{value,onChange}`-only) · C6 `OverrideAffordance` (`{onOverride,disabled}`-only, disabled derived from the one predicate, RoleGate-wrapped) · C7 `OverrideConfirmDialog` (sole `onConfirm` holder + read-only reason echo) · C8 `CommittedConfirmation` (`{decision,context}`-only, reason from `decision.reason`) · `copy.js` (C10 — 21 advisory-clean strings verbatim from FD). **Header comments** on C5/C6/C7/C8 as explicit deliverables.
- **Shared-config extension (Q1-A)**: `vitest.config.js` (include + coverage.include add `src/overrideForm`; **thresholds unchanged**), `eslint.config.js` (new `src/overrideForm` block reusing `shell/no-inline-label` + `shell/advisory-vocabulary` + new `override/override-testid-convention`), `eslint-rules/overrideForm.js`. **No file under `src/shell/`, `src/queue/`, `src/memoView/`, or `src/approvalGate/` created or edited.**
- **Tests (C9 substrate)**: 28 test files + `fixtures.js` (`makeOverrideDouble` with `submitOverride.calls[i]=[recommendationId,reason]`; `BLANK_REASONS`/`NONBLANK_REASON`; 409-reused envelopes). Every `NFR-OVR-*` at its pinned tier — load-bearing **NOFINAL-1/CONFIRM-1/CANCEL-1** teeth, the NEW **REASONGATE-1** (5 blanks → 0 POST across full attempt; non-blank → 1 POST reason verbatim) + `reasonTrimDivergence.test.js` (trim vs strip, U+001C–1F/U+0085, non-authoritative), **REASONKEEP-1** (2 assertions), **CAPFREE-1** (scan + prop-contract), **REFNOTOWN-1** incl. the **NEW `noApprovalGateImport`** + `noCreateOverrideFetchImportInPresentational`.

**Result**: **340 Vitest passed** (89 test files); **ESLint clean** (exit 0). Coverage all-files 100% stmt/func/line · 99.66% branch. **`src/overrideForm` = 100% stmt/func/line · 98.36% branch (QA-6 ≥90% PASSED)** — every component file 100%; the one sub-100% branch is `OverrideFormView.jsx:67` at 97.05% (**flagged realization note**: the `onConfirm` belt-and-suspenders `isReasonPresent` guard is **unreachable by construction** — reason frozen during `confirming` — exactly the ND-OVR-Fold-i / P2 optional insurance; presence asserted non-vacuously; reported honestly rather than contriving an invariant-bypassing test). **`src/shell` + `src/queue` + `src/memoView` + `src/approvalGate` still 100% (UNTOUCHED)**; backend pytest **850 passed / 31 skipped UNTOUCHED** (zero backend files modified; `testresults.txt` records the frontend result alongside, not merged). Deliverables written: `guide-docs/build/ui-override-form/code/code-summary.md`, refreshed `testresults.txt`, this back-annotation, appended `audit.md`, re-saved plan with the eight answers embedded.

**On approval**, `ui-override-form` (U8) becomes the **15th complete unit** and the **5th complete UI-cluster unit** (after ui-shell, ui-queue, ui-memo-view, ui-approval-gate) — the second/final UI write path. **P1 remaining after U8: `ui-history` (U9).**

**STOPPED** at the Code Generation 2-option completion gate (**1. Request Changes / 2. Continue** — the LAST stage for `ui-override-form`) — did NOT advance. **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) **UNTOUCHED**; no file under any frozen `src/` tree created or edited; CON-BR4 single-sourced in audit-store; RoleGate cosmetic + UI reason guard non-authoritative; no LLM; no TypeScript; tier-B corpus run NOT authorized; no other unit started.

**UPDATE 2026-07-14 (Code-Gen completion gate FINALIZED — APPROVED / Continue; see the COMPLETE section below)**: the standardized Code-Gen 2-option completion gate — the LAST stage for `ui-override-form` (U8) — was **APPROVED (Continue)**. No code changed at approval; the gate decision is recorded and the unit is marked complete. `ui-override-form` (U8) is now the **FIFTEENTH** fully-complete build-loop unit.

## ✅ BUILD → `ui-override-form` (U8) COMPLETE — the FIFTEENTH fully-complete unit (5th UI/React unit; second/final UI write path) — 2026-07-14
**`ui-override-form` (U8) — COMPLETE**: Code-Gen 2-option completion gate **APPROVED** → **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · Code-Gen ✓**. The **FIFTEENTH** fully-complete build-loop unit and the **5th** completed frontend/React unit (after `ui-shell`, `ui-queue`, `ui-memo-view`, `ui-approval-gate`) — the **second and final UI write path** (R5 `POST …/override`, mandatory non-blank `reason`; the counterpart to `ui-approval-gate`'s approve path). **340 Vitest tests passed (89 files); ESLint clean (exit 0); `src/overrideForm` = 100% stmt/func/line · 98.36% branch (QA-6 ≥90% PASSED — every component file 100%); `src/shell` + `src/queue` + `src/memoView` + `src/approvalGate` UNTOUCHED at 100%; backend pytest 850 passed / 31 skipped UNTOUCHED (git-verified, zero backend files modified — separate runner/tree).** Artifacts: `guide-docs/build/ui-override-form/{functional-design,nfr-requirements,nfr-design,code/code-summary.md}` + `frontend/src/overrideForm/` (C1–C10 source modules + shared-config extension + 28 co-located test files + `fixtures.js`) + refreshed `testresults.txt`.

**Honestly-reported unreachable branch (a realization note, NOT a defect)**: the single sub-100% branch is **`OverrideFormView.jsx:67` (97.05%)** — the `onConfirm` belt-and-suspenders `isReasonPresent` guard, which is **unreachable by construction** because `reason` is frozen during the `confirming` phase. This is the **correct, designed outcome of ND-OVR-Fold-i / P2 (optional-insurance / defense-in-depth)**, not a coverage gap to be papered over: presence is asserted **non-vacuously** in the single-call-site test, and the branch is **flagged and reported honestly** rather than masked by contriving an invariant-bypassing test that would defeat the guard's purpose. Reporting it as-is is the correct engineering choice.

**Concrete invariant verification (the load-bearing teeth + by-construction guarantees, all green)**: the **REASONGATE-1 teeth** — 5 blank-reason variants → **0 POST** across the full `Override → Confirm` attempt; a non-blank reason → **exactly 1 POST** with the `reason` carried **verbatim** — plus `reasonTrimDivergence` (trim-vs-strip, U+001C–1F/U+0085, non-authoritative), **REASONKEEP-1**, **CAPFREE-1** (scan + prop-contract), and the **NOFINAL/CONFIRM/CANCEL** lifecycle teeth. All **by-construction guarantees** pass, including the **NEW capability-free `OverrideReasonInput`** (`{value,onChange}`-only — no submit/seam capability) and the **NEW `noApprovalGateImport`** structural guard (plus `noCreateOverrideFetchImportInPresentational`). Together these are the **concrete verification of the mandatory-reason-gate invariant** (blank reason can never reach a POST) **and the RoleGate-cosmetic-not-authz pattern** (`RoleGate can="act"` is chrome/defense-in-depth; the backend re-check is the real gate; the UI reason guard is non-authoritative).

**P1 roster (17 P1 units) — 16 component-names COMPLETE**: 11 non-UI (intake, document-sanitizer, rules-engine, memo-agent-core, auth-rbac, audit-store, quality-gates, corpus-generator, database, secrets-config, admin-cli) + **5 UI** (ui-shell, ui-queue, ui-memo-view, ui-approval-gate, **ui-override-form**). Counted as build-loop units (intake+document-sanitizer co-built as one), `ui-override-form` is the **FIFTEENTH**. **UI P1 remaining (1)**: `ui-history` (U9) — **the last remaining P1 unit**.

**Cross-unit / Deferred Decisions register (current, unchanged in substance)**: **WIRE-1 ✅ PINNED** (`guide-docs/build/wire-1/api-contract.md`) — **unchanged; now exercised for real by BOTH R4 (read) AND R5 (write) across two sibling units** — `ui-approval-gate`'s **approve** write path and `ui-override-form`'s **override** write path both commit through it; **tier-B corpus run — UNAUTHORIZED**; **audit_store Docker-guard hygiene gap — DEFERRED** (non-blocking). All frozen artifacts (WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form) UNTOUCHED; no LLM; no TypeScript.

**Next (per the working sequence `ui-queue → ui-memo-view → ui-approval-gate → ui-override-form → ui-history`)**: `ui-history` (U9) — **NOT started** (awaiting the user's separate go); the **last remaining P1 unit**. **Inherited-but-must-re-examine (NOT assume-transferable)**: `ui-history` is a **read-only view over the audit trail (R6/R7)** that the two write-path units' commits **produce** — it is the **first UI unit to consume `decision_id` / `timestamp` / the full `AuditRecord` shape**, none of which either write-path unit needed. So the write-path lineage transfers *selectively*: (a) the **seam/testid/lint scaffolding and TDD substrate** carry as pattern, but there is **no commit/POST surface** — no `submitOverride`/`submitApprove`, no confirm-gate, no reason input, no `RoleGate can="act"` write affordance to re-examine; the R6/R7 seam is **read-only** and its narrow-builder discipline applies to *query params*, not a request body; (b) the **AuditRecord/6-tuple shape is a fresh contract-consumption surface** — `decision_id`, `timestamp`, and the full record fields must be read against WIRE-1 §R6/§R7 and the audit-store `AuditRecord` definition **directly**, not inferred from the write units' commit bodies (which carried only action + reason, never the persisted record shape); (c) **RoleGate** semantics differ — history is a **view**, so any role-gating is visibility/cosmetic over *reads*, a different question from the write units' act-affordance; do not copy the write-path RoleGate reasoning wholesale. WIRE-1 · all frozen `src/` trees UNTOUCHED; tier-B NOT authorized; no other unit started.

## 🧩 BUILD → `ui-history` (U9) — STARTED (last remaining P1 unit); DISCOVER-carryover CLEAN; Functional Design Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-14
**Unit picked**: `ui-history` (U9; C5; Phase 1) — **US-UI-6 · FR-UI-1 · CON-AUDIT-1 (read surface)** — per the working sequence (`ui-queue → ui-memo-view → ui-approval-gate → ui-override-form → ui-history`). The **last remaining P1 unit** and the **6th/final frontend/React unit**. A **read-only view over the audit trail** the two frozen write-path units (U7/U8) produce — the **first UI unit to consume `decision_id` / `timestamp` / the full `AuditRecord` shape**.

**§0 DISCOVER-carryover — CLEAN**: no `guide-docs/build/ui-history/`, no `frontend/src/history/` source, no `ui-history-*.md` plan. Greenfield unit.

**§1 Frozen contracts re-read (by value/shape, none edited)**: `unit-of-work §U9` (**"lighter (display)"**, read surface over CON-AUDIT-1); **US-UI-6 Gherkin** (row shows recommendation + committed outcome + timestamp; each entry **links to the audit tuple**; rows carry `data-testid`); **user-journey auditor path** (browse read-only; open past decision **"cannot edit"** SEC-4; view `rulebook_version`/`rule_results`/`memo_hash`; **replay = CLI/backend, OUT of U9 scope**); **WIRE-1 R6** `GET /decisions?page=&size=` → list wrapper of **DecisionSummary** `{decision_id, application_id, recommendation_id, action, timestamp}` (**authenticated ANY role**, offset/limit 1-based); **WIRE-1 R7** `GET /decisions/{decision_id}` → full **AuditRecord** (**authenticated ANY role**, single-resource-by-id, 404 `not_found`); **`audit_store.record_schema`** AuditRecord / AuditTuple(`rulebook_version, rule_results, timestamp, model_version, memo_hash, engine_version`) / CommittedDecision(`recommendation_id, underwriter_id, action, reason|null`) / ApplicantProfileSnapshot / `status`(active|superseded, write-once) / `supersedes_decision_id`(null in Phase 1/2); **shell copy** `RECOMMENDATION_LABELS` + `COMMIT_ACTION_LABELS` (frozen, **distinct namespaces** — human `override` never renders as system `DECLINE-RECOMMEND`); **RoleGate** `COSMETIC_CAPABILITIES` (underwriter `{act,read}` / auditor `{act:false,read:true}` / **admin `{act:false,read:false}`** — `can="read"` would cosmetically HIDE history from admin, a tension with R6/R7 any-role); **`queue/fetchSeam.js` + `memoView/memoFetchSeam.js`** = the read-only **list** + **by-id** seam shapes to **mirror-not-import** (PERF-1 bounded single-page, **NO write-body builder** — the write-path discipline deliberately does NOT transfer); **queue VIEWONLY-1 + `noRoleGateImport`** precedent.

**§2 Depth recommendation = LIGHTER (display)** — classification-forced (§U9); read-only, no commit/gate/mandatory-reason, R6/R7 authenticated-any-role — **plus two named display-side invariants** verified by a StructuralGuard + focused teeth (NOT comprehensive write-path rigor): **INV-FAITHFUL** (strictly read-only, no edit affordance, no write/mutation seam; never imply the forensic record could be altered — SEC-4) and **INV-NAMESPACE** (system recommendation vs human action render as distinct frozen labels). Q1 confirms; Q1-B offers heavier (comprehensive) if the user judges the immutability invariant warrants it.

**§3 Proposed approach (contingent)**: self-contained `frontend/src/history/` — `historyFetchSeam.js` (read-only `createHistoryFetch(transport) → {fetchList(page,size)[R6], fetchDetail(decision_id)[R7]}` + `normalizeError` + `DEFAULT_PAGE_SIZE`; **no write-body builder**), `HistoryView.jsx` (sole stateful orchestrator; list↔detail; reads no Role), `components/HistoryList` · `DecisionDetail` · `HistoryStateView` (loading/empty/errorList/errorDetail/404). `data-testid` `history-*` family + convention lint = realization detail for NFR/Code-Gen.

**Plan written**: `guide-docs/build/plans/ui-history-functional-design-plan.md` (§0–§6) with **SIX `[Answer]` tags LEFT BLANK** (plan + questions presented first; none answered): **Q1** depth · **Q2** list+detail structure (one `HistoryView` with list↔detail state owning both R6 + R7-by-id reads [rec A] vs emit-upward SELECT-1 vs two composed units — a genuinely **NEW in-unit master-detail** pattern, unlike queue's *cross-unit* onSelect) · **Q3** RoleGate applicability (no RoleGate / VIEWONLY-1 mirror [rec A] vs `can="read"` [hides admin — contract tension] vs per-role differentiation) · **Q4** dual system-recommendation-vs-human-action display, namespace-distinct — **AND a flagged frozen-contract tension**: US-UI-6 wants the system recommendation in each **list** row, but frozen **R6 `DecisionSummary` omits it** (only R7 detail carries it via `audit_tuple.rule_results`) → rec A shows it in the **linked detail**, honoring frozen R6; **Q4-C** (widen R6 per-row) = the user's explicit frozen-contract call, NOT improvised · **Q5** pagination (mirror queue offset/limit, **NO filtering** — R6 has no filter params [rec A]; **Q5-C** widen R6 with filter params = deferred Phase-2 seam / user's explicit call) · **Q6** detail rendering scope + INV-FAITHFUL (render forensic tuple + `rule_results` + read-only profile snapshot faithfully, no edit affordance, no replay [rec A]; profile demographics = persisted forensic input, **not** a feature vector → not a bias-swap concern; memo body absent from AuditRecord [only `memo_hash`] → C rejected).

**§4.5 Ambiguity-check — NOT yet run** (runs on the user's go after the tags are filled; flag-and-stop, no improvisation; on CLEAN the Q&A is embedded back into the plan and FD Part 2 generated).

**STOPPED** at the Functional Design Part 1 **plan-file gate** — awaiting the six answers. **No FD artifact generated; no code.** **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form (all frozen) **UNTOUCHED** (consumed by value/shape only); **no write surface introduced** (pure read consumer — INV-FAITHFUL); no LLM; no TypeScript; tier-B corpus run NOT authorized; no other unit started.

**Register (current, unchanged in substance)**: **WIRE-1 ✅ PINNED** — now additionally exercised for the first time on the **read side** by R6/R7 (history), alongside its R4 reads and R5 writes; **tier-B corpus run — UNAUTHORIZED**; **audit_store Docker-guard hygiene gap — DEFERRED** (non-blocking). **P1 roster: 15 build-loop units COMPLETE; `ui-history` (U9) IN PROGRESS = the LAST remaining P1 unit.**

## 🧩 BUILD → `ui-history` (U9) — Functional Design COMPLETE (Part 1 approved all-A + ambiguity-check CLEAN [4 folds] + Part 2 four artifacts); STOP at FD 2-option gate — 2026-07-14
**FD Part 1 APPROVED** — Q1–Q6 answered (**all A**), full Q&A + rationale embedded in `guide-docs/build/plans/ui-history-functional-design-plan.md`. **Ambiguity-check RUN → CLEAN, no STOP; FOUR clarity-folds** (three from the user's flagged checks + one surfaced while grounding):
- **HIST-Fold-1** (check i) — **page position PRESERVED** across the detail excursion: `HistoryView` holds `{page, items}` in orchestrator state; grounded in the frozen `QueueView.jsx` position-preserving RETRY-1/Fold-B (`load(page)`/`setPage(targetPage)`, never resets to page 1) → **Back returns to the same page, no refetch**.
- **HIST-Fold-2** (check ii) — `rule_results` rendering is **shape-only in FD with a faithfulness constraint** (every entry preserved, no lossy omission; "summarized" = progressive disclosure, never truncation-that-hides-data); the concrete expand/collapse widget **DEFERRED to NFR-Design** (the FD↔NFR boundary the siblings observed).
- **HIST-Fold-3** (check iii) — R7 **404 `not_found` surfaced GENERICALLY** via `detailError` (no special not-found branch); and **NO premature superseded handling** — `status` display-only (write-once `active`), `supersedes_decision_id` always `null` in Phase 1/2 → no superseded branch/dereference/affordance designed (OOS-7/Phase-3 seam, **named-not-designed**).
- **HIST-Fold-4** (**NEW — surfaced while grounding against `forbiddenTerms.js`**) — `FORBIDDEN_TERMS.systemOutput` includes `'decision'`, forbidden **as SYSTEM output** but explicitly **reserved for the HUMAN committed action**. `ui-history` is the **FIRST unit rendering the human "decision" namespace**, and Q4-A's "Underwriter's decision" framing intersects the reused **blanket lexical** advisory lint (safe for `ui-memo-view` only because it had no human-namespace copy). **Resolved at FD/intent level** (BR-HIST-2: system-output copy avoids the tokens; the human-committed region is namespace-distinct and legitimately carries the CON-BR4 "decision" concept), with the **exact lint scoping / final heading wording deferred to NFR-Design/Code-Gen WITHOUT modifying frozen `shell`**. **Surfaced transparently, not silently picked.**

**FD Part 2 GENERATED** — four artifacts under `guide-docs/build/ui-history/functional-design/`:
- `domain-entities.md` — R6 list wrapper + `DecisionSummary`; R7 `AuditRecord`/`AuditTuple`/`CommittedDecision`/`ApplicantProfileSnapshot`/`status`/`supersedes_decision_id`; the `HISTORY_STATE` master-detail machine (page preserved); component/prop inventory (read-only, **no write seam**); history-local `copy.js`; the `history-<element>-<purpose>` testid inventory (rows + region-level).
- `business-rules.md` — **BR-HIST-1..11**, each grounded + checkable; load-bearing **BR-HIST-2** (namespace-distinct **dual-display** of system `Recommendation` vs human `CommittedDecision`, incl. the HIST-Fold-4 advisory-token scope) + **BR-HIST-3** (INV-FAITHFUL: read-only, no edit affordance, **no write/mutation seam** — a `noWriteSeam` StructuralGuard) + BR-HIST-7 (VIEWONLY-1, `noRoleGateImport`) + BR-HIST-11 (immutable/version fields display-only, no premature superseded handling).
- `business-logic-model.md` — the list↔detail state machine + the detail **namespace-distinct composition**; **TWO validated Mermaid diagrams** (rectangle-only, alphanumeric node IDs, quoted labels free of hyphens/colons/semicolons/parens, balanced blocks) **each with a text alternative**; data-flow summary; deferred-to-later list.
- `frontend-components.md` — component hierarchy; single-stateful-`HistoryView` state ownership; per-component props/responsibilities; interaction flows A (browse R6) / B (detail R7) / C (back-preserving-page); WIRE-1 R6/R7 integration points; the **no-form / no-write / no-RoleGate / no-router** boundary.

**STOPPED** at the standardized Functional Design **2-option completion gate** (**1. Request Changes / 2. Continue to Next Stage → NFR Requirements**) — did NOT advance. **NO code generated.** **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form (all frozen) **UNTOUCHED** (consumed by value/shape only); **no write surface introduced** (INV-FAITHFUL — a pure read consumer); no LLM; no TypeScript; tier-B corpus run NOT authorized; no other unit started. **On approval → NFR Requirements** (per-unit loop continues for U9).

## 🧩 BUILD → `ui-history` (U9) — FD APPROVED (Continue); NFR Requirements Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-14
**FD APPROVED 2026-07-14 (Continue → NFR Requirements)** — `ui-history` (U9) Functional Design COMPLETE (all four artifacts frozen for this stage). Advanced to the per-unit **NFR Requirements** stage; wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/ui-history-nfr-requirements-plan.md`.

**Depth confirmed** = **lighter (display) + INV-FAITHFUL + INV-NAMESPACE via StructuralGuard + focused teeth** (consistent with the FD; **not comprehensive** — pure read surface, no write path). **Built ON the frozen FD** (BR-HIST-1..11 + the four-artifact component/prop inventory + the `HISTORY_STATE` master-detail machine with position-preserving Back + the namespace-distinct detail composition) — **re-opening none**.

**§1 Draft `NFR-HIST-*` target map — every BR-HIST rule mapped, NO orphan**: **T1** COPY · **T2 SEPARATION** (the **load-bearing** DOM-containment teeth — system vs human region non-nested, each namespace exclusive; **highest rigor**, mirrors `ui-memo-view` SEPARATION-1) · **T3** ADVISORY (reuse the one `FORBIDDEN_TERMS`; HIST-Fold-4 scope = Q2) · **T4 FAITHFUL** (INV-FAITHFUL **zero write-capable call site** scan; highest rigor) · **T5** DUALREAD (read-attribution: select→fetchDetail only, page→fetchList only) · **T6** RULERESULTS (faithfulness — all N entries in DOM, order preserved, none dropped) · **T7** REASON (iff `override`) · **T8** VIEWONLY (no-RoleGate/no-router scan + all-roles render) · **T9** EMPTY (`items.length`) · **T10** ERROR (table + **position/id-preserving retry** + **generic 404**) · **T11** TESTID (incl. the **two region-level testids** + self-test) · **T12** NOSUPERSEDE (no `status==='superseded'` branch / no `supersedes_decision_id` ref); addenda **T13 BACKPRESERVE** (Back = zero refetch + byte-identical page/items, HIST-Fold-1) · **T14** STATEMACHINE (seven states + one consolidated transition) · **T15** NOTS · **T16** PERF (bounded reads, **soft/non-gating**) · **T17** A11Y (**soft/non-gating**). PERF/A11Y rigor set by the sibling precedent (recorded, not asked).

**§3 THREE open `[Answer]` questions (LEFT BLANK — Part 1 gate)**: **Q1** dual-READ double shape (rec **A**: one injected `historyFetchSeam` with two independently-capturing spies; cross-guards = read-attribution + call-count teeth, **no** "zero-before-confirm" write teeth since there is no write op) · **Q2** HIST-Fold-4 resolution (rec **A**: namespace-distinct **token-avoiding** human-region wording keeping the frozen advisory lint **reused-unmodified**; **B**: system-output-scoped lint block honoring the literal "Underwriter's decision" = a **new lint mechanism**, the **user's explicit call**; **C**: defer to NFR-Design) · **Q3** `rule_results` disclosure (rec **A**: expand/collapse with **ALL entries mounted in the DOM regardless of state** [collapse = visibility-only] so the faithfulness teeth hold; **B** truncate **rejected** [drops entries, breaks INV-FAITHFUL]; **C** always-expanded = viable fallback).

**§3.5 Ambiguity-check — NOT yet run** (runs after the Q1–Q3 answers; flag-and-stop, no improvisation; on CLEAN the Q&A is embedded and Part 2 generated). **§4** Part 2 checkboxes (`nfr-requirements.md` + `tech-stack-decisions.md`) unchecked. **§5** Security-Guardrails preview (read-only view; error-hygiene + least-privilege **Compliant**; rest **N/A**).

**STOPPED** at the **NFR Requirements Part 1 plan-file gate** — awaiting the three answers. **No NFR artifact generated; no code.** **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form (all frozen) **UNTOUCHED**; **no write surface** (INV-FAITHFUL); no LLM; no TypeScript; tier-B corpus run NOT authorized; no other unit started.

## 🧩 BUILD → `ui-history` (U9) — NFR Requirements COMPLETE (Part 1 approved all-A + ambiguity-check CLEAN [3 folds] + Part 2 two artifacts); STOP at NFR-Requirements 2-option gate — 2026-07-14
**NFR Requirements Part 1 APPROVED** — Q1–Q3 answered (**all A**), full Q&A embedded in `guide-docs/build/plans/ui-history-nfr-requirements-plan.md` §3. **Ambiguity-check RUN → CLEAN, no STOP; THREE folds** (each from a user-flagged check):
- **NFR-HIST-Fold-1** (check i) — `rule_results` collapse via HTML **`hidden`/`display:none`** (removes collapsed entries from the **a11y tree** — **no separate `aria-hidden`** needed) while keeping every entry **mounted**; T6's "all N present" assertion uses a **DOM-level query** (`getAllByTestId`/`querySelectorAll`) that finds mounted-but-hidden nodes (not a visibility-filtering role/text query). T6 acceptance criterion added; detailed a11y stays soft/deferred to Code-Gen.
- **NFR-HIST-Fold-2** (check ii) — T13's "Back adds zero new `fetchList` calls" is a **simple before/after snapshot** of `fetchList.calls.length` within the single test; the **fresh-per-test double instance** (ui-approval-gate CG-Fold-1) isolates counts → **no before/after-mount discrimination** needed in the double.
- **NFR-HIST-Fold-3** (check iii — **audited against the REAL detector**) — ran representative history-local draft strings through the **actual** `eslint-rules/index.js` `findForbiddenSystemOutput`; it is a **word-boundary matcher** (`/\bdecision\b/i`), **not a substring scan**, so **plural "decisions" / `decision_id` PASS** and only standalone singular "decision"/`approved`/bare-`decline`/`declined` are flagged. Verified: `System recommendation` / `Underwriter's committed action` / `Committed outcome` / `No decisions yet` / `History` / all forensic labels = **clean**; negative controls `Underwriter's decision` / `Decision history` / `approved` / `declined` = **correctly FLAGGED**. **Q2-A is non-vacuously satisfiable with the frozen lint reused unmodified.** Binding Code-Gen rule recorded: avoid the standalone singular "decision" in static copy (title "History"/"Decisions", human region "Underwriter's committed action"); plural "decisions" is fine. Representative strings verified NOW; complete `copy.js` deferred to Code-Gen.

**NFR Requirements Part 2 GENERATED** — two artifacts under `guide-docs/build/ui-history/nfr-requirements/`:
- `nfr-requirements.md` — **T1–T17 as `NFR-HIST-*` targets**, each pass/fail + acceptance + tier + rigor; §0 central testability principle + **Folds A–D** (single dual-read double; DOM-containment; mounted-but-hidden disclosure + DOM-level query; advisory verified vs the real detector); the **load-bearing SEPARATION-1** (DOM-containment, highest) + **FAITHFUL-1** (zero write-capable call-site scan, highest) called out; traceability table (**no orphan**); full **Security-Guardrails** compliance table (error-hygiene + least-privilege **Compliant**; rest **N/A**; **no blocking finding**).
- `tech-stack-decisions.md` — **D1–D15**: inherits the frozen substrate (React/Tailwind/no-TS/Vitest/RTL/jsdom/ESLint); adds only the **dual-read double** (D6/Q1), **DOM-containment teeth** (D7), **before/after Back snapshot** (D8), **mounted-but-hidden `rule_results` disclosure + DOM-level query** (D9/Q3), **token-avoiding advisory resolution verified vs the real detector** (D10/Q2), **`history-testid-convention` regex** (D11, queue-family), and deferred items (D12–D15).

**STOPPED** at the standardized **NFR Requirements 2-option completion gate** (**1. Request Changes / 2. Continue to Next Stage → NFR Design**) — did NOT advance. **NO code generated.** **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form (all frozen) **UNTOUCHED** (reused/mirrored as convention, not modified/imported); **no write surface** (INV-FAITHFUL); no LLM; no TypeScript; tier-B corpus run NOT authorized; no other unit started. **On approval → NFR Design** (per-unit loop continues for U9).

## 🧩 BUILD → `ui-history` (U9) — NFR Requirements APPROVED (Continue); NFR Design Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-14
**NFR Requirements APPROVED 2026-07-14 (Continue → NFR Design)** — `ui-history` (U9) NFR Requirements COMPLETE. Advanced to the per-unit **NFR Design** stage; wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/ui-history-nfr-design-plan.md`, mirroring the sibling NFR-Design structure (patterns → components → reference-not-own → coverage → validated Mermaid). **Depth** unchanged: lighter (display) + INV-FAITHFUL + INV-NAMESPACE via StructuralGuard + focused teeth. **Built ON** the frozen FD + the seventeen `NFR-HIST-*` targets — re-opening none.

**§1 Pattern map — THIRTEEN named patterns, no orphan**: P1 SharedForbiddenTermsReuse · **P2 StructuralIsolationCompositionPattern** (load-bearing; mirrors ui-memo-view) · **P3 ReadOnlySeamPattern** (load-bearing, **NEW** — seam shape makes write structurally absent) · P4 DualReadFetchSeamPattern (contrasted with the write-path asymmetric double) · P5 MasterDetailStateMachinePattern · **P6 StateRetentionAcrossNavigationPattern** (NEW) · P7 ArrayLengthEmptyPattern (contrast the status-discriminator) · P8 PerOperationRetryTargetingPattern · **P9 MountedButHiddenFaithfulDisclosurePattern** (NEW) · P10 ConditionalFieldRenderingPattern · P11 RoleInvariantRenderingPattern · **P12 StructuralGuardPattern** (incl. the **NEW no-write-seam + no-superseded-branch** scans) · P13 ReferencedObservedBoundaryPattern.

**§2 Logical components C1–C12 with by-construction prop shapes**: C1 HistoryView (sole stateful; both reads; machine; `{page,items}` retention) · C2 historyFetchSeam (exports **exactly** `{createHistoryFetch, buildHistoryListRequest, buildHistoryDetailRequest, normalizeError}` — **no write builder**, GET-only) · C3 HistoryList · C4 HistoryPagination · C5 HistoryStateView · C6 DecisionDetail (sibling composition point) · **C7 SystemRecommendationRegion `{recommendation, confidence, testid}` — NO human path** · **C8 CommittedActionRegion `{action, reason, underwriterId, testid}` — NO system path** · C9 ForensicTupleRegion (status display-only, no supersede path) · C10 RuleResultsRegion (mounted-but-hidden disclosure) · C11 ProfileSnapshotRegion · C12 StructuralGuard (substrate). **§3** reference-not-own (ui-shell reused; five siblings mirrored-not-imported; audit-store by shape; **no write path**). **§4** component→target coverage (**no orphan**). **§5** validated **component-relationship Mermaid** (rectangle-only, 7 rules) — **SYS and HUM are sibling children of DecisionDetail with NO edge between them**: the namespace separation is a **visible graph property** — + text alternative.

**§6 FOUR open `[Answer]` questions (LEFT BLANK — Part 1 gate)**: **Q1** SEPARATION-1 **by-construction both directions** (rec **A**: `SystemRecommendationRegion` excludes any action/reason path AND `CommittedActionRegion` excludes any recommendation/confidence path → mis-nesting unwritable; DOM-containment test = regression guard) · **Q2** FAITHFUL-1 **ReadOnlySeamPattern by-construction** (rec **A**: the seam exports only the two GET reads + two GET builders + `normalizeError`, no request-body builder → write structurally absent; the no-write-seam scan = regression guard) · **Q3** StructuralGuard granularity (rec **A**: one substrate incl. the two new scans) · **Q4** master-detail machine as a `HistoryView` responsibility vs a dedicated component (rec **A**: responsibility, per the "sole stateful component" framing + sibling precedent).

**§6.5 Ambiguity-check — NOT yet run** (runs after the Q1–Q4 answers; flag-and-stop; on CLEAN the Q&A is embedded and Part 2 generated). **§7** Part 2 checkboxes (`nfr-design-patterns.md` + `logical-components.md`) unchecked.

**STOPPED** at the **NFR Design Part 1 plan-file gate** — awaiting the four answers. **No NFR-Design artifact generated; no code.** **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form (all frozen) **UNTOUCHED**; **no write surface introduced** (INV-FAITHFUL / P3); no LLM; no TypeScript; tier-B corpus run NOT authorized; no other unit started.

## 🧩 BUILD → `ui-history` (U9) — NFR Design COMPLETE (Part 1 approved all-A + ambiguity-check CLEAN [1 fold] + Part 2 two artifacts); STOP at NFR Design 2-option gate — 2026-07-14
**NFR Design Part 1 APPROVED** — Q1–Q4 answered (**all A**), full Q&A embedded in `guide-docs/build/plans/ui-history-nfr-design-plan.md` §6. **Ambiguity-check RUN → CLEAN, no STOP; ONE fold**:
- **NFR-DESIGN-Fold-1** (user-flagged) — the **symmetric** self-evidence refinement to Q1-A's region header comments: **`historyFetchSeam.js` carries a header comment** (the frozen `queue/fetchSeam.js` JSDoc precedent) stating it is a **READ-ONLY dual-read seam** whose exported surface is exactly `{createHistoryFetch, buildHistoryListRequest, buildHistoryDetailRequest, normalizeError}`, both builders emit **only** GET, and there is **deliberately NO request-body builder / NO `submit*` — write structurally absent** — so the no-write guarantee is **self-evident reading the seam module in isolation**, complementing the FAITHFUL-1 no-write-seam scan. Recorded into P3 + C2. No new mechanism, no gap.

**NFR Design Part 2 GENERATED** — two artifacts under `guide-docs/build/ui-history/nfr-design/`:
- `nfr-design-patterns.md` — **P1–P13**, each stating how it structurally meets its `NFR-HIST-*` target(s) + tier; the **two load-bearing patterns spelled out with the ACTUAL prop/export shapes** (not bare assertions): **P2 StructuralIsolationCompositionPattern** (system region `{recommendation, confidence, testid}` / human region `{action, reason, underwriterId, testid}` — mis-nesting unwritable) + **P3 ReadOnlySeamPattern** (seam exports exactly the four read members, both builders GET-only, no request-body builder — write structurally absent) + the region/seam header-comment convention; a validated **pattern-integration Mermaid** (rectangle-only) + text alternative; a **pattern → target → tier → rigor** traceability (**no orphan**).
- `logical-components.md` — **C1–C12** with responsibilities/ownership + **exact by-construction prop/export shapes** + the header-comment convention; the validated **component-relationship Mermaid** (**SYS and HUM sibling children of DecisionDetail, NO edge between them** — namespace separation as a visible graph property) + text alternative; the **reference-not-own** check (**reused** vs **mirrored-not-imported** vs **consumed-by-shape** kept distinct); the **component → target coverage** table (**no orphan**); settled items held.

**STOPPED** at the standardized **NFR Design 2-option completion gate** (**1. Request Changes / 2. Continue to Next Stage → Infrastructure Design**) — did NOT advance. **NO code generated.** **Guardrails held**: WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form (all frozen) **UNTOUCHED** (reused/mirrored/by-shape, none modified/imported); **no write surface introduced** (INV-FAITHFUL / P3); no LLM; no TypeScript; tier-B corpus run NOT authorized; no other unit started. **On approval → Infrastructure Design** (per-unit loop continues for U9; likely a logged SKIP — source-level view, no infra services, Vercel topology is `deploy-config` P2 — confirmed at that stage).

## 🧩 BUILD → `ui-history` (U9) — NFR Design APPROVED → Infrastructure Design SKIPPED (logged); STOP at Infra 2-option gate; NEXT = Code Generation — 2026-07-15
**NFR Design APPROVED** → `ui-history` NFR-Design stage COMPLETE.

**Infrastructure Design — assessed AT THE STAGE (not pre-committed) → SKIPPED (logged, explicit four-point rule justification, NOT silent)**, per CLAUDE.md "Skip IF: No infrastructure changes / Infrastructure already defined" + execution-plan §3 "little independent infra":
1. **No untrusted parsing / no subprocess sandbox** — renders typed WIRE-1 R6/R7 JSON (mocked via the injected dual-read `historyFetchSeam` double); no pdfplumber/subprocess/file parsing.
2. **No independent persistence provisioned** — fetches R6 (list) + R7 (detail) through the own-local seam; never touches the database or the `audit-store` persistence layer directly; no store, no migration (persistence is `audit-store`'s, provisioned by `database` — the one non-skip).
3. **No LLM/provider access** — *displays* the full `AuditRecord` shape (incl. LLM-authored fields, rendered faithfully) but authors/executes none; holds no provider client.
4. **No deployed service / no independent cloud topology** — bundler/dev-server + Vercel topology → `deploy-config` (P2); real `historyFetchSeam` wiring + R6/R7 route impl (`backend/app/main.py`) → composition root / Build & Test.

Ambiguity-check surfaced **no genuine ui-history-owned infra concern**: being a genuinely NEW read pattern (dual-read R6+R7, master-detail with position-preserving Back, namespace-distinct SystemRecommendationRegion/CommittedActionRegion display, first consumer of `decision_id`/`timestamp`/the full `AuditRecord` shape) is a new category of **application behavior**, NOT infrastructure — the reads flow through the SAME deferred composition-root wiring pattern as every prior UI unit; pagination/list-size, caching, CORS, WAF, rate-limiting → deploy-config/API-gateway (P2) or backend, not this unit's; no new secret/env var/service. → SKIP correct, no STOP. Consistent with **ui-shell + ui-queue + ui-memo-view + ui-approval-gate + ui-override-form** (the five prior React-unit SKIPs). **NO infra artifact created** (`guide-docs/build/ui-history/infrastructure-design/` not created).

**Skip roster now SIXTEEN**: intake · document-sanitizer · rules-engine · memo-agent-core · auth-rbac · audit-store · quality-gates · corpus-generator · secrets-config · admin-cli · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form · **ui-history**; **database** remains the one real non-skip.

**`ui-history` (U9) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · **Infrastructure Design ✓ SKIPPED (logged)** · Code Generation ⏳ (the LAST stage for U9 — Part-1-plan-then-Part-2-generate, own approval; U9 is the **last remaining P1 unit overall**).

**Guardrails held**: NO code; NO infra artifact; **WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form (all frozen) untouched**; tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the Infrastructure Design 2-option completion gate (**1. Request Changes / 2. Continue → Code Generation** — the LAST stage for ui-history) — did NOT advance past the gate.

## 🧩 BUILD → `ui-history` (U9) — Infrastructure Design SKIP APPROVED (Continue); Code Generation Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-15
**Infrastructure Design SKIP APPROVED (Continue → Code Generation)** → `ui-history` advanced to the per-unit **Code Generation** stage; wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/ui-history-code-gen-plan.md`. **NO code generated; NO file under `frontend/src/history/` created.**

**Grounded** (re-derived none) on the frozen FD (`frontend-components.md` — C1–C12 inventory, prop shapes, testid inventory, master-detail machine, WIRE-1 R6/R7 points), approved NFR Requirements (seventeen `NFR-HIST-*` targets + tiers + Fold-A/B/C/D), approved NFR Design (P1–P13, by-construction prop/export shapes, header-comment convention, NFR-DESIGN-Fold-1), **and the REAL frontend config on disk** (shared `vitest.config.js` include/coverage per-unit pattern; `eslint.config.js` per-unit block reusing `shell/no-inline-label` + `shell/advisory-vocabulary` + a new `<unit>-testid-convention` via `eslint-rules/<unit>.js`, queue-family regex `^history-[a-z]+(-[a-z0-9]+)+$`; `shell/copy` label + `FORBIDDEN_TERMS` exports; realized `src/<unit>/<View>.jsx` + `<seam>.js` + `copy.js` + `components/` + `__tests__/` layout).

**Plan contents**: **§1** component→module map C1–C12 → `frontend/src/history/**` files — **header comments on C2 (read-only dual-read seam, four-member export), C7 (`{recommendation,confidence,testid}`-only), C8 (`{action,reason,underwriterId,testid}`-only) called out as EXPLICIT deliverables** (C6 read-only-composer header additionally); **§2** TDD test→target map, every `NFR-HIST-*` at its NFR-pinned tier — **SEPARATION-1 (DOM-containment teeth) + FAITHFUL-1 (zero-write-call-site AST scan + four-member seam export) at full-highest**; DUALREAD-1 (dual-read double) / RULERESULTS-1 (mounted-but-hidden DOM-level query) / REASON-1 / VIEWONLY-1 (all-four-roles + `noRoleGateImport`) / EMPTY-1 (`items.length`) / ERROR-1 (table-driven + retry-targeting + generic-404) / TESTID-1 (region + row testids) / NOSUPERSEDE-1 / BACKPRESERVE-1 (before/after snapshot) / STATEMACHINE-1 (per-state + one consolidated transition) / REFNOTOWN (no-import scans incl. **NEW `noOverrideFormImport`**) / NOTS-1 / PERF-1/A11Y-1 soft / SCOPE-1 governance — **no orphan**; **§3** leaf-first Steps 0–12 (unchecked): scaffold+shared-config → `copy.js` → C2 seam → C7+C8 → C9+C11 → C10 → C6 → C5 → C3+C4 → C1 → C12 StructuralGuard (incl. **NEW `noWriteSeam` + `noSupersede` scans**) → coverage → summary; **§4** HOLDS restated; **§5** coverage gate (Vitest folded; baseline `src/shell`+`queue`+`memoView`+`approvalGate`+`overrideForm` no-regress, QA-6 ≥90% on `src/history`; backend pytest **850/31 untouched**); **§6** **EIGHT open `[Answer]` questions LEFT BLANK** (Q1 shared-config; Q2 `makeHistoryDouble` dual-read double; Q3 shared fixtures for BACKPRESERVE-1 multi-page + RULERESULTS-1 unsorted/length-1 + override/approve records; Q4 `HISTORY_COPY` advisory-clean verbatim per Fold-D; Q5 testid literals two region ids + every row; Q6 consolidated transition own file; Q7 `historyFetchSeam` read-only dual-read header/JSDoc; Q8 ERROR-1 four-status + generic-404 envelopes); **§7** gate.

**`ui-history` (U9) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · **Code Generation ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (Part-1-plan-then-Part-2-generate; ambiguity-check runs AFTER answers, Part 2 on explicit go). **This is the LAST stage for the LAST remaining P1 unit overall.**

**Guardrails held**: NO code; NO file under `frontend/src/history/`; ambiguity-check deferred until after the answers (per user); **WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form (all frozen) UNTOUCHED**; no local `FORBIDDEN_TERMS`; no LLM; no TypeScript; no write path (INV-FAITHFUL); tier-B NOT authorized; no other unit started; `audit_store` Docker-guard gap still deferred.

**STOPPED** at the Code-Gen plan-file gate awaiting the user's Q1–Q8 answers + review before Part 2.

## 🧩 BUILD → `ui-history` (U9) — Code Generation COMPLETE (Part 1 answered all-A + ambiguity-check CLEAN [4 folds] + Part 2 GENERATED: 13 modules / 25 test files / 486 tests / src/history 100%); STOP at Code-Gen 2-option gate — **the LAST stage of the LAST P1 unit** — 2026-07-16

**Code-Gen Part 1 ANSWERED** — Q1–Q8 answered (**all A**), full Q&A re-embedded in `guide-docs/build/plans/ui-history-code-gen-plan.md` §6 (standing convention). Q1 shared-config extension · Q2 `makeHistoryDouble()` dual-read double · Q3 shared named fixture set · Q4 `HISTORY_COPY` verbatim per Fold-D · Q5 one `history-<element>-<purpose>` convention · Q6 own transition file · Q7 seam header + JSDoc · Q8 shared envelope fixtures incl. `notFoundEnvelope`.

**Ambiguity-check RUN 2026-07-16 → CLEAN, no STOP; FOUR folds** (recorded in plan §6.5) — each resolves **within** the frozen artifacts, contradicting none:
- **CG-HIST-Fold-1** — the pinned queue-family regex `^history-[a-z]+(-[a-z0-9]+)+$` rejects the FD's four 2-segment root ids (`history-view`/`-list`/`-detail`/`-pagination`). **No conflict**: all four are **testid-prop defaults** rendered as `data-testid={testid}` (a JSX expression, not a `Literal`), which the rule never evaluates — exactly the frozen `ui-queue` `queue-view`/`queue-pagination` precedent. No regex change, no FD change.
- **CG-HIST-Fold-2** (**the load-bearing one**) — the reused **blanket** `advisory-vocabulary` lint also scans **testid literals**, and a **HYPHEN**-delimited "decision" **IS** flagged: Fold-D's `decision_id` passes only because `_` is a word char, whereas `-` is not. So a literal `history-detail-decision-id` would **fail the build**. Verified the frozen FD §6 inventory contains **no** such id (already lint-safe) and the seam's `/decisions?page=` / `/decisions/${id}` paths are plural and clean. Binding rule now regression-guarded by a RuleTester invalid fixture + a detector self-test.
- **CG-HIST-Fold-3** — BR-HIST-5's "decision linkage (`decision_id`, `application_id`, `recommendation_id`)" has **no** pinned testid in FD §6 and **no** region prop to carry it (C9 = `{auditTuple, contentHash, status, testid}`; only C11 takes `applicationId`). **Resolution**: C6 `DecisionDetail` (holder of the whole `record`) renders the linkage at the detail root under token-avoiding, convention-compliant ids (`history-detail-record-id` / `history-detail-recommendation-id`) — honoring the faithfulness clause without touching C7/C8's by-construction prop restrictions and without breaching Fold-2. Both nodes sit in **neither** namespace region → SEPARATION-1 teeth unaffected.
- **CG-HIST-Fold-4** — `contentHash` is a prop of **both** C9 and C11; rendering `history-detail-content-hash` in both would duplicate a testid. FD §6 assigns it to the forensic group (**C9**); **C11** renders the same value as the snapshot's own tamper-evidence marker under `history-detail-profile-hash`. Both frozen prop shapes honored, ids distinct.

**Code-Gen Part 2 GENERATED** — §3 **Steps 0–12 ALL COMPLETE `[x]`**, TDD tests-first / leaf-first. **13 production modules** under `frontend/src/history/` (C1 `HistoryView.jsx` · C2 `historyFetchSeam.js` · C3–C11 `components/*.jsx` · `copy.js` · `testids.js`) + **25 test files** (C12 StructuralGuard substrate) + `eslint-rules/history.js`. Summary: `guide-docs/build/ui-history/code/code-summary.md`.

**Result**: **486 frontend tests pass** (114 files; **+146 / +25** this unit) · **ESLint clean** (exit 0) · **`src/history` = 100% statements / branches / functions / lines on EVERY file — QA-6 (≥90%) PASSED** · all-files 100% stmt/func/line, 99.73% branch (the one sub-100% branch is `ui-override-form`'s **pre-existing, already-flagged** belt-and-suspenders guard — unchanged, not a ui-history finding). **All five frozen `src/` trees stand at their baselines** and **zero backend files were modified** — both **mtime-verified** (only `src/history/**`, `vitest.config.js`, `eslint.config.js`, `eslint-rules/history.js` written). Backend pytest **850 passed / 31 skipped** untouched (separate runner/tree, not re-run); `testresults.txt` records the frontend result **alongside**, not merged.

**Load-bearing targets realized**: **SEPARATION-1** (Fold-B DOM-containment teeth, both directions, on the `override` record where conflation would be maximally harmful) and **FAITHFUL-1** (the write-path single-call-site guard **inverted to ZERO call sites** + the seam's exact four-member GET-only export) — both at full-highest. Plus the **two NEW scans** (`noWriteSeam`, `noSupersede` — zero reads of `supersedes_decision_id`) and the **NEW `noOverrideFormImport`** guard.

**Seven realization notes flagged honestly** in the code summary (none masked): Folds 1–4 above; `testids.js` as one module beyond the plan's §1 map (Q5-A's lower-cased/kebab-safe requirement vs real upper-case `rule_id`s — its self-test proves the raw id *would* violate the convention, so the helper is load-bearing); `HistoryStateView` omitting the FD's `testid` prop per the frozen `QueueStateView` precedent; and two structural detectors needing **comment-stripping** because they flagged their **own units' header comments** (the guarantee is the absence of **code**, not of words — the frozen `ui-approval-gate` `singleCallSite` precedent), each now carrying a comment-immunity self-test.

**`ui-history` (U9) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · **Code Generation ✓ COMPLETE (Part 1 answered + ambiguity-check CLEAN + Part 2 generated) → STOPPED at the Code-Generation 2-option completion gate**. **U9 is the LAST P1 unit; this was its LAST stage.**

**Register**: **P1 roster — 16 of 16 build-loop units now code-complete** (pending this gate's approval); `ui-history` was the last remaining P1 unit. **WIRE-1 ✅ PINNED** — its **R6/R7 read side is now consumed by a realized client** (by shape; route impl still deferred to Build & Test). **tier-B corpus run — UNAUTHORIZED** (unchanged). **audit_store Docker-guard hygiene gap — DEFERRED** (non-blocking, unchanged).

**Guardrails held**: **ui-shell (frozen) reused via import only** (`Panel`/`ReadOnlyRegion`/`RecommendationBadge`/`ConfidenceBadge`/`shell/copy` incl. `COMMIT_ACTION_LABELS` + the **ONE** `FORBIDDEN_TERMS`/`RoleContext`); **all five sibling UI units (frozen) mirrored, never imported**; no file under any frozen `src/` tree created or edited; **no local `FORBIDDEN_TERMS`** (`advisory-vocabulary` applied **UNMODIFIED**, every `HISTORY_COPY` string verified in-suite against the **real** `findForbiddenSystemOutput`); **no write path anywhere** (INV-FAITHFUL — structurally absent, not merely linted); no `RoleGate` (`can="read"` deliberately unused so `admin` is not excluded); no router; no premature superseded handling; no LLM; no TypeScript; WIRE-1 R6/R7 by shape only, no real network call; **tier-B NOT authorized; no other unit started; WIRE-1 untouched**.

**STOPPED** at the Code-Generation 2-option completion gate (**1. Request Changes / 2. Continue** — the LAST stage for `ui-history` AND the LAST remaining P1 unit overall) — did NOT advance past the gate, did NOT start another unit.

## 🏁 BUILD → `ui-history` (U9) — Code Generation **APPROVED** → **ui-history COMPLETE = the SIXTEENTH complete build-loop unit — closing ALL SEVENTEEN P1 UNITS. THE ENTIRE P1 ROSTER IS BUILT THROUGH CODE GENERATION.** P1→P2 boundary reached; STOP — nothing started — 2026-07-16

**Code Generation APPROVED 2026-07-16 (option 2, Continue)** → **`ui-history` (U9) COMPLETE**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · **Code Generation ✓**. 486 Vitest tests / 114 files; ESLint clean; **`src/history` 100% statements/branches/functions/lines on EVERY file** (QA-6 ≥90% cleared); all five prior frontend trees at their existing baselines; backend **mtime-verified untouched** at 850 passed / 31 skipped.

**ROSTER ARITHMETIC (verified against the frozen `unit-of-work.md`, re-read on disk — not assumed)**: **23 units = 17 Phase 1 (U1–U17) + 6 Phase 2 (U18–U23)**. The **sixteen build-loop passes cover seventeen P1 units** because **U1 `intake` + U2 `document-sanitizer` were built as ONE combined pass** (the cluster convention). "Sixteenth complete unit" and "all seventeen P1 units complete" are both exact and mutually consistent.

**THE COMPLETE P1 ROSTER (16 passes / 17 units — ALL built through Code Generation)**: `intake`+`document-sanitizer` (U1+U2) · `rules-engine` (U3) · `audit-store` (U12) · `memo-agent-core` (U4) · `database` (U15) · `auth-rbac` (U11) · `secrets-config` (U16) · `ui-shell` (U10) · `corpus-generator` (U14) · `quality-gates` (U13) · `admin-cli` (U17) · `ui-queue` (U5) · `ui-memo-view` (U6) · `ui-approval-gate` (U7) · `ui-override-form` (U8) · **`ui-history` (U9)**.

**What `ui-history` was, in the arc of the build**:
- The **SIXTH and FINAL frontend/React unit** — closing the C5 UI cluster (`ui-shell` → `ui-queue` → `ui-memo-view` → `ui-approval-gate` → `ui-override-form` → `ui-history`).
- The **FIRST UI unit to render BOTH namespaces together** — the **system** advisory `Recommendation` (from `audit_tuple.rule_results`) and the **human** committed `CommitAction` (from `committed_decision`) — the display context where WIRE-1 §1 / CON-BR4 namespace-distinctness is most at risk and therefore most load-bearing.
- The **read surface over the audit trail the two frozen write-path units (U7/U8) produce** — its defining property being the **absence** of the write path they own.
- **The load-bearing SEPARATION-1 and FAITHFUL-1 teeth PASS — the concrete verification of the two invariants, not their mere assertion**: **SEPARATION-1** proves `!system.contains(human) && !human.contains(system)` (Fold-B, arbitrary depth) with each namespace present in its own region and **null** in the other, exercised on the **`override`** record — the case where conflating the human override with the system `DECLINE-RECOMMEND` would be maximally harmful. **FAITHFUL-1** is the write-path **single-call-site guard INVERTED TO ZERO call sites** (no `submit*`, no commit/override builder, no non-GET method, no `body:`), sitting atop C2's **exact four-member GET-only export** — so INV-FAITHFUL is realized **by construction, structurally absent**, not merely linted against.

**Two Code-Gen findings worth carrying forward**:
- **CG-HIST-Fold-2 — a GENUINE NEAR-MISS, correctly regression-guarded.** The reused **blanket** `advisory-vocabulary` lint scans **testid literals** too, and a **HYPHEN**-delimited "decision" **IS** flagged — Fold-D's `decision_id` passes only because `_` is a **word char**, whereas `-` is **not**. A literal `history-detail-decision-id` would have **failed the build**. The frozen FD §6 inventory happened to contain no such id (it was already lint-safe), so nothing broke — but the constraint was **tacit**, and is now **explicit and regression-guarded** by a RuleTester invalid fixture + a detector self-test. The near-miss is recorded rather than quietly absorbed.
- **The comment-stripping fix to the structural detectors — the CORRECT GENERALIZATION of the `ui-approval-gate` `singleCallSite` precedent.** `findRealNetwork` and `findRoleGateUsage` initially flagged **their own units' header comments** (`"a bounded single-page R6 fetch (PERF-1)"`, `` `can="read"` is deliberately NOT used ``). In a unit whose **every** by-construction guarantee is documented in **prose that names the very construct it forbids**, a raw-text scan would flag the self-evidence that makes the guarantee discoverable. The guard therefore asserts the absence of **CODE, not of words** — exactly what `ui-approval-gate` established when `ApproveAffordance`'s header names `submitApprove` — and each detector now carries a **comment-immunity self-test**.

**REGISTER — Deferred Decisions / cross-unit constraints AT THIS MILESTONE (verified, not recited)**:
- **WIRE-1 ✅ PINNED** (since U6) — and now **exercised by a realized client on EVERY route it defines**: **R1** session (ui-shell `RoleContext`), **R2** queue, **R3/R4** applications/memo, **R5** commit **approve AND override**, **R6/R7** decisions history. All consumed **by shape**; **no unit makes a real network call** (every seam transport injected). The contract is complete and fully claimed on the client side.
- **tier-B corpus run — STILL UNAUTHORIZED** (unchanged; the ±3pp band + edge-checklist audit LOGIC is unit-tested at tier U; enforcement on the real 300+ corpus awaits the user's explicit authorization).
- **`audit_store` Docker-guard hygiene gap — STILL DEFERRED** (non-blocking): its integration fixture lacks the `_docker_available()` skip-guard that `auth-rbac`/`database`/`admin-cli` use, so 5 tests **ERROR** instead of **SKIP** when Docker is absent locally; they pass in CI.
- **No other P1 gap remains open.**

**P1→P2 BOUNDARY REACHED — NOT "nothing left".** The **six Phase-2 units** are the remaining unit-list work, exactly as the original 23-unit decomposition planned: **U18 `outlier-model`** (C3 — IsolationForest + z-scores + SHAP, seeded) · **U19 `memo-extensions`** (C4 — MCP tools + borderline-router + secondary/showcase adapters) · **U20 `ui-outlier-view`** (C5 — conforms to the frozen `ui-shell` contract) · **U21 `observability`** (Langfuse + Prometheus/Grafana) · **U22 `llm-judge`** (promptfoo groundedness) · **U23 `deploy-config`** (Render + Vercel free-tier validation deploy).

**⚠️ FLAGGED — THE FASTAPI COMPOSITION ROOT REMAINS THE LARGEST PIECE OF UNFINISHED INTEGRATION WORK, AND IT IS IN NEITHER THE P1 NOR THE P2 UNIT LIST.** `backend/app/main.py` — binding all seven WIRE-1 routes to the **real seams every UI unit's tests mocked** — has been **named-and-deferred in EVERY SINGLE unit's build** ("the real transport is wired at the composition root — deferred / Build & Test"). **VERIFIED ON DISK 2026-07-16, not inferred**: `backend/app/` **DOES NOT EXIST**, and a grep for `FastAPI(` / `@app.get` / `@app.post` across the entire `backend/` tree returns **ZERO hits** — there is **no route implementation anywhere**. Every backend unit is a library; every frontend unit injects a doubled seam; **nothing yet binds them**. This is real, sized, currently-unowned work that the P1→P2 transition **must not obscure**. It is **not** started here.

**Guardrails held**: **NO P2 unit started**; **NO frozen artifact touched**; **NO composition-root wiring begun**; **tier-B corpus run NOT authorized**; WIRE-1 untouched. **STOPPED** — awaiting the user's separate decision on the next move.

## 🔀 DEVIATION (out-of-band, NOT a numbered unit) → Composition-Root Integration Pass — **Scope A approved**; Part 1 (Plan) WRITTEN; ambiguity-check RUN → **NOT CLEAN (1 genuine gap, Q1)**; STOP at plan-file gate — 2026-07-16

**Nature**: an **OUT-OF-BAND INTEGRATION PASS**, explicitly logged as a **deviation** from the strict workflow sequence per CLAUDE.md's **Adaptive Workflow Principle** ("the workflow adapts to the work") + `common/workflow-changes.md` ("Be Flexible"). **NOT a numbered unit** — consistent with `unit-of-work.md:104-108` (the composition root is *"not a 24th unit of work"*). **The 23-unit decomposition is UNCHANGED and NOT re-opened.** Logged in `audit.md` via the methodology's **Change Request Log Format**; `execution-plan.md` **deliberately untouched** (user directive).

**Why out-of-band**: Build & Test — the venue the frozen plan names for the composition root's *verification* — **cannot run until all 23 units complete** (`execution-plan.md:266` "a single Build-and-Test pass after all units"; its scope at `:205` includes **groundedness** → U22 `llm-judge` and **trace audit** → U21 `observability`, both P2). The frozen docs give the composition root's **verification** a home but never assign its **authoring** ("covered by" ≠ "written by"). This pass closes that gap deliberately rather than by drift. **Plan-gate discipline PRESERVED** — CLAUDE.md's no-code-before-approved-plan rule still binds; the deviation is **sequence/venue only**.

**Scope A APPROVED (backed slice only)** — chosen over B/C because grounding surfaced that the composition root is **not purely "wiring"** for 4 of 7 routes: the Phase-1 schema has **three tables** (`audit_record`, `applicant_profile_snapshot` [child, written only at commit], `app_user`) — **no pending-application/recommendation store exists**; `audit_store.seams.CommitContextProvider`'s **only** implementation is `DictCommitContextProvider`, labelled "**Test/fake provider**"; and **WIRE-1 defines no ingestion route**. Wiring R2–R5 would mean **inventing the pending-application/recommendation lifecycle** — un-designed domain state. **Scope A refuses to smuggle domain modelling in under an integration label.** B (in-memory pending store) / C (persistent store + migration 0003) presented and **NOT chosen**.

**Decisions (user, in writing)**: **2** auth handshake → stub header identity resolving against `app_user`. **4** R6 pagination → **in-app**, `audit-store` stays frozen. **5** frontend → **author-only** (real transport + `App.jsx` written + Vitest-tested; **not** browser-runnable; `deploy-config` P2's bundler **not** pulled forward). **6** router → **N/A** under Scope A. **1/3** (R4 sync-vs-async, live LLM) → **N/A** under Scope A.

**Part 1 (Plan) WRITTEN**: `guide-docs/build/plans/composition-root-integration-plan.md` — §1 module map (`backend/app/**` + `frontend/src/app/**`, all additive) · §2 **route→unit binding table** (**R1/R6/R7 REAL**; **R2–R5 explicit not-wired marker**) + §2.1 **two-engine least-privilege binding** · §3 test→`INT-*` target map (11 targets) · §4 numbered leaf-first Steps 0–11 · §5 HOLDS · §6 five open `[Answer]` questions · §6.5 ambiguity-check · §7 gate. **NO code generated; `backend/app/` NOT created; no frontend entry point created.**

**Key grounded findings (derived on disk, not assumed)**:
- **Only R1/R6/R7 are backed today.** R6/R7 are **exactly the two routes `ui-history` (U9) consumes** — so Scope A makes the newest unit work end-to-end against real Postgres, and nothing else. **R5 unwired ⇒ the composition root registers NO write route at all** — INV-FAITHFUL holds trivially and is asserted structurally.
- **Two-engine binding derived from `0002_grants.sql`**: `audit_reader`/`audit_writer` hold grants on the **audit tables only** — **neither can read `app_user`** — so **R1 → `DATABASE_URL`** engine, **R6/R7 → `AUDIT_READER_URL`** engine (least privilege, SEC-4). Derived from the frozen DDL, not chosen.

**Ambiguity-check RUN → ⚠️ NOT CLEAN — the FIRST non-clean check in the project (all 17 units came back clean)**:
- **🔴 CR-Fold-1 — GENUINE GAP → Q1 → SURFACE-AND-STOP.** `auth_rbac.PERMISSION_MATRIX` grants **`READ_AUDIT` to underwriter + auditor but NOT admin**; **WIRE-1 §3 marks R6/R7 "authenticated" (any role)**. For an `admin` caller the two **frozen** artifacts give **opposite answers (200 vs 403)**. Corroboration that it is real: frozen `ui-history` **BR-HIST-7** independently hit the **mirror** of this and sided with WIRE-1 (declining `RoleGate can="read"` precisely because it "would cosmetically exclude admin… a divergence from R6/R7's any-authenticated"). **The client already sided with WIRE-1; the backend policy datum sides against it. The composition root is the first place both meet — which is exactly why it surfaces here and in no unit.** NOT improvised; the user's call.
- 🟡 **CR-Fold-2** (Q2) — WIRE-1 §4's frozen status table has **no** status for "registered but deliberately unwired"; an honest 501 `not_implemented` marker **additively extends** it. Surfaced, not assumed.
- 🟡 **CR-Fold-3** (Q3) — `browse()` orders by **`decision_id`**, not `timestamp`; `ui-history` re-sorts nothing, so R6's order **is** the auditor's view, and no frozen artifact pins it.
- 🟢 **CR-Fold-4** (accepted consequence, **not** a question) — `browse()` is **N+1 by construction** (selects all ids, then `_load_one` per id), so **in-app pagination materializes every record to serve one page**. The accepted cost of Decision 4 (keep `audit-store` frozen). Harmless at Phase-1 volumes; **flagged honestly, not masked**. Client-side PERF-1 still holds — the bounding is real at the wire.
- 🟢 **CR-Fold-5** (Q5) — `Settings` requires `GEMINI_API_KEY` though Scope A wires no LLM; `secrets-config` is frozen + fail-closed by design. Recommendation: accept + dummy value.
- 🟢 **CR-Fold-6** (RESOLVED, no gap) — the R1-vs-R6/R7 engine question, settled by the grants DDL (above).

**Guardrails held**: no code; `backend/app/` not created; no frontend entry point; **all 17 frozen units + WIRE-1 UNTOUCHED**; no file under any frozen `backend/<unit>/` or `frontend/src/<unit>/` tree; `audit-store` + `database` stay frozen (no migration 0003, no repo pagination); **no P2 unit started**; **tier-B NOT authorized**; **`audit_store` Docker-guard gap untouched**; `execution-plan.md` untouched; backend 850/31 + frontend 486 unchanged (nothing run that could alter them).

**STOPPED** at the plan-file gate — awaiting the user's **Q1 answer (the genuine gap)** + Q2–Q5 + **explicit approval** before any Part 2 code generation.

## 🔀 DEVIATION (out-of-band, NOT a numbered unit) → Composition-Root Integration Pass **Scope A — Part 2 GENERATED**; ambiguity re-check CLEAN (+1 new fold CR-Fold-7); backend 850→**960**, frontend 486→**524**; STOP at the diff-review gate — 2026-07-16

**Part 2 GENERATED** on the five filled answers (**Q1-B, Q2-A, Q3-A, Q4-A, Q5-A** — embedded in `composition-root-integration-plan.md` §6). Steps 0–11 executed TDD, leaf-first. Summary: `guide-docs/build/composition-root/integration-summary.md`. **STOPPED at the diff-review gate — the deviation is NOT closed pending approval.**

**Ambiguity re-check (§6.6) → CLEAN to proceed, ONE NEW fold surfaced — not improvised**:
- **🟡 CR-Fold-7 (NEW, created by the answers themselves)** — Q2-A directs a marker on R2–R5; **R5 is a POST**, so honoring Q2-A **necessarily registers one POST route**, colliding with the *literal* reading of the "no write route is registered" hold. **Exactly one reading satisfies both** — the hold's own reason-clause ("since R5 stays unwired") points at **write CAPABILITY, not HTTP verbs**. Realized as a **stronger** five-part assertion: only non-GET route is the marker (read from `app.openapi()["paths"]`); its handler **raises as its first statement** (AST-asserted); **no writer engine** (`AUDIT_WRITER_URL` never read); **no `DecisionCommitService`/`CommitContextProvider`**; no repository write call. A verb count would pass while a real commit path sat behind a POST — this cannot. **Flagged at the gate; the literal reading (drop the R5 marker) remains available.**
- CR-Fold-1 **answered (Q1-B)** → divergence **RECORDED as UNRESOLVED**, not resolved. CR-Fold-2/3/5 answered; CR-Fold-4/6 unchanged.

**RESULT**:
- **Backend: 960 passed / 31 skipped** (was **850/31** — **+110 additive**); coverage **99.83%** (was 99.82%); **`backend/app` 100% every file**; **5 pre-existing Docker errors unchanged** (audit_store gap untouched).
- **Frontend: 524 passed / 117 files** (was **486/114** — **+38 additive**); **`src/app` 100% every metric**; **ESLint clean**; all six frozen frontend trees at baseline.
- **NO frozen unit touched — mtime-verified**: only `backend/app/**`, `frontend/src/app/**`, `pyproject.toml`, `vitest.config.js`, `eslint.config.js`.
- **`ui-history` (U9) now works end-to-end against a real backend — and nothing else does.** That is Scope A's point, achieved exactly.

**What was built**: **`backend/app/`** — `main.py` (`create_app()`), `dependencies.py` (**two-engine binding** + `X-User-Id` stub identity + `READ_AUDIT` enforcement), `errors.py` (§4 envelope + frozen status table on **every** non-2xx), `projections.py` (§5 shapes + in-app pagination), `routes/{session,decisions,not_wired}.py`, 12 test modules (110 tests). **`frontend/src/app/`** (author-only) — `httpTransport.js` (**the real transport satisfying the duck-typed contract every frozen seam already expects — no seam modified**), `seams.js` (all five units' seams over one transport), `sessionClient.js` (R1 → RoleContext shape, fail-closes to null), `App.jsx` (frozen `AppFrame` + `HistoryView`, **no router**), 3 test modules (38 tests).

**Route binding as delivered**: **R1 REAL** (`app_user`, `DATABASE_URL` engine) · **R2/R3/R4/R5 → 501 `not_implemented`** · **R6/R7 REAL** (`audit_record`, `AUDIT_READER_URL` engine). **Two-engine least-privilege binding DERIVED from the frozen `0002_grants.sql`, not chosen** — `audit_reader`/`audit_writer` hold grants on the audit tables only, **neither can read `app_user`**. **No writer engine is ever constructed.**

**Frozen design detail discovered and honored**: `AppFrame` **already hosts its own `RoleProvider`** ("populated later by WIRE-1"). An outer provider would have been **shadowed**, so R1's role is fed to AppFrame's `user` prop — **the shell's seam used as designed, not worked around**.

**Two self-corrections during generation (my errors, fixed + reported)**: (i) the route scan used a version-dependent internal (`_IncludedRouter` has no `.path`) → switched to the app's **OpenAPI schema**, a stable public accessor; (ii) a frozen-tree heuristic scanned for the phrase "composition root" and **false-positived on five frozen units' own deferral docstrings** — the exact naive-text-scan mistake previously fixed for the frontend detectors → replaced with the checkable fact (**import direction is one-way**).

### 🔴 RECORDED DIVERGENCE — UNRESOLVED, deliberately carried (Q1-B)
**`READ_AUDIT` on R6/R7 vs WIRE-1 §3.** Frozen `PERMISSION_MATRIX` → **admin 403**; frozen **WIRE-1 §3** ("authenticated", any role) → **200**. Q1-B **applies the frozen policy verbatim** (auth-rbac is the single-sourced RBAC authority; the server is always the real gate); **WIRE-1 NOT amended**. **Two-sided, not a one-sided oversight**: the frozen `ui-history` FD (**BR-HIST-7**) sided with WIRE-1 on the client, so **the frozen UI assumes any-authenticated while the server enforces `READ_AUDIT`** — an admin would see a history surface the server 403s. *(Blast radius today nil — BR-HIST-7 itself notes admin has no UI journey.)* **UNRESOLVED — carried for a future deliberate reconciliation (Option C: enforce `READ_AUDIT` AND amend WIRE-1 §3's wording). This pass does NOT resolve it.** `test_authz_read_audit.py` encodes the consequence so a future reversal must change a test **visibly, not silently**.

### 🟡 RECORDED ADDITIVE EXTENSION (Q2-A)
**`501 not_implemented` extends WIRE-1 §4's table ADDITIVELY** — replaces/contradicts nothing; all seven frozen statuses keep their exact meanings; envelope shape unchanged. Names a state the frozen table has no word for, distinct from `not_found` so R7's 404 stays unconfusable.

### 🟢 RECORDED HONEST-BEHAVIOR NOTES
**R6 ordering (Q3-A)**: emits `browse()`'s **`decision_id`** order — **no frozen artifact pins it**; the **honest current behavior, not a designed guarantee**, and **not newest-first** (asserted explicitly, consequence documented not hidden). **CR-Fold-4**: in-app pagination is **N+1 by construction** — the accepted cost of keeping `audit-store` frozen; client-side PERF-1 still holds at the wire. **Q5-A**: `GEMINI_API_KEY` required-but-unused (frozen fail-closed `Settings`); dummy value accepted.

**What this does NOT resolve (stated plainly)**: the **core underwriting path (queue → memo → commit) remains unwired** — R2–R5 stay unbacked because the pending-application/recommendation lifecycle is **un-designed domain state** belonging in its own stage (Scope B/C), not smuggled into a wiring pass. The frontend **cannot run in a browser** (no bundler; `deploy-config` U23/P2 owns it, deliberately not pulled forward). **Build & Test still cannot run until all 23 units complete.** The **Q1-B divergence remains open**.

**Guardrails held**: all 17 frozen units imported/composed never edited; no file under any frozen tree; **WIRE-1 untouched/not amended**; invented **no domain state** (no pending store, no ingestion route, no `CommitContextProvider`, no migration 0003); `audit-store` + `database` frozen; **no P2 unit started**; **tier-B NOT authorized**; **`audit_store` Docker-guard gap untouched**; `execution-plan.md` untouched; the 23-unit decomposition unchanged — **this is not a 24th unit**.

**STOPPED** at the diff-review gate — awaiting explicit approval before the deviation is considered closed.

## ✅ DEVIATION CLOSED — Composition-Root Integration Pass (Scope A) — approved as delivered 2026-07-16

**CLOSED, approved as delivered.** This was an **OUT-OF-BAND DEVIATION, NOT a numbered unit** — it is **not part of the 17 P1 or the 6 P2 count**; the **23-unit decomposition is unchanged (17 P1 + 6 P2 = 23)**. Full record: the three Change Request Log entries in `guide-docs/audit.md` (opened 06:35Z, generated 07:28Z, closed 09:11Z). **Summary → `guide-docs/build/composition-root/integration-summary.md`.** Plan → `guide-docs/build/plans/composition-root-integration-plan.md` (status CLOSED; §6.6.1 records CR-Fold-7's resolution).

**Delivered**: `backend/app/` (FastAPI composition root — R1/R6/R7 REAL against real Postgres, R2–R5 → 501 `not_implemented`, two-engine least-privilege binding, `X-User-Id` stub identity, `READ_AUDIT` enforcement, in-app pagination) + `frontend/src/app/` (author-only real transport + `App.jsx` + five-seam wiring, no router). **Backend 850→960 / 31 skipped (+110 additive), 99.83% cov, `backend/app` 100%. Frontend 486→524 (+38 additive), `src/app` 100%, ESLint clean. No frozen unit touched (mtime-verified).** `ui-history` (U9) works end-to-end against a real backend.

**CR-Fold-7 resolved as-derived (user-confirmed)**: INV-FAITHFUL asserted as **write-CAPABILITY, not a literal verb count** — the correct call, confirmed at the gate.

**🔴 Q1-B divergence remains explicitly OPEN**: R6/R7 enforce `READ_AUDIT` (frozen `PERMISSION_MATRIX`: admin→403) vs **WIRE-1 §3** "authenticated, any role" (→200); two-sided (frozen `ui-history` BR-HIST-7 sided with WIRE-1 on the client); WIRE-1 NOT amended; reconciliation deferred to future deliberate work (Option C).

**Guardrails held at closure**: all 17 frozen units untouched; WIRE-1 untouched/not amended; **no domain state invented** (no pending store, no ingestion route, no `CommitContextProvider`, no migration 0003 — R2–R5 remain unwired, the core underwriting demo path is NOT runnable end-to-end); `audit-store` + `database` frozen; **no P2 unit started; no Scope B/C work begun; tier-B NOT authorized; `audit_store` Docker-guard gap untouched; `execution-plan.md` untouched.**

**NEXT MOVE = the user's, to be decided separately**: (b) start P2 units beginning with **U18 `outlier-model`**, OR further composition-root work (**Scope B/C**). No recommendation made; nothing started.

## 🧩 BUILD → `outlier-model` (U18, C3, **Phase 2** — the FIRST P2 unit) — Functional Design COMPLETE (Part 1 all-A + ambiguity-check CLEAN [4 folds, 1 newly surfaced] + Part 2 3-artifact folded set); STOP at FD 2-option gate — 2026-07-16

**FD Part 1 APPROVED** — Q1–Q5 answered (**all A**), full Q&A embedded in `guide-docs/build/plans/outlier-model-functional-design-plan.md` §3. **Depth: comprehensive** (verified `unit-of-work.md:234`). **Carryover CLEAN** (first touch of U18).

**Ambiguity-check RUN (§3.5) → CLEAN to proceed; FOUR folds, one NEWLY surfaced — no surface-and-stop**:
- **CG-OUT-Fold-1** (check i): `Z_SCORE_FLAG_THRESHOLD` = a fixed named constant, **default |z| >= 3.0** in the FD; exact value a statistical tuning parameter **confirmable at NFR/Code-Gen** (not a regulatory boundary).
- **CG-OUT-Fold-2** (check ii, load-bearing): the IsolationForest score is **corpus-relative**, so `OutlierResult.provenance` carries **`corpus_version`** + `seed` + `outlier_model_version`. Not `rulebook_version` (unsupervised scoring never reads the corpus label).
- **CG-OUT-Fold-3** (check iii): documented per-excluded-categorical rationale (occupation = proxy-checked var; smoking_status/employment_type = arbitrary-encoding determinism hazard, already rule-handled).
- **CG-OUT-Fold-4** (**NEWLY SURFACED, derived + flagged for gate confirmation**): `profile_factory.py` emits nullable `bmi_derived`/`existing_debt_obligations_annual`/`dti_ratio`, so 3 of 9 feature fields can be None and IsolationForest needs complete vectors → **deterministic corpus-median imputation** (CON-DET-1-safe, CON-BR1-safe [corpus statistic, no demographic signal], not fabrication [imputed feature's z-score is 0, never self-flags]). Pinned as BR-OUT-3. Same CR-Fold-7 discipline the user endorsed (derive the one constraint-compatible answer, disclose, confirm at gate).

**FD Part 2 GENERATED — the 3-artifact folded set** (convention confirmed on disk: every P1 comprehensive unit used exactly these three; **no unit ever produced a separate `component-methods.md`**; methods FOLDED into `domain-entities.md §1`, as the user's 'or folded per the comprehensive-unit convention' allowed) under `guide-docs/build/outlier-model/functional-design/`:
- **`domain-entities.md`** — component/method inventory (FeatureVectorBuilder / CorpusSource / OutlierModel / ShapExplainer + signatures + header-comment deliverables); the `OUTLIER_FEATURE_FIELDS` numeric-only allow-list (9 fields) + by-construction CON-BR1 + per-categorical exclusion rationale + missing-optional imputation; the `OutlierResult`/`FlaggedFeature`/`OutlierProvenance` contract (provenance triple incl. corpus_version); consumed frozen shapes; schema-vs-data + cross-consumer field-need checks.
- **`business-rules.md`** — **BR-OUT-1..10**, each checkable + traced, no orphan. Load-bearing: BR-OUT-1 (CON-BR1 demographic exclusion by construction), BR-OUT-4 (seeded, version-anchored reproducibility). Also BR-OUT-3 (missing-value imputation), BR-OUT-5 (score/flag/explain composition), BR-OUT-7 (zero-unexplained by schema), BR-OUT-8 (own mirrored dual-source seam), BR-OUT-9 (advisory-only), BR-OUT-10 (reference-not-own).
- **`business-logic-model.md`** — fit/score two-phase lifecycle; a **validated Mermaid** (12 rectangle nodes / 15 edges; passed all 7 rules, underscore permitted per convention) + text alternative; determinism + faithful-explanation arguments; fit-vs-score + FD-later boundaries; consumer/dependency map; invariant self-check.

**Key design pins**: numeric-only demographic-excluded feature vector (allow-list, by construction) · IsolationForest holistic score + per-feature z-score flags (|z| >= 3.0 default) + SHAP per flag · provenance `{corpus_version, seed, outlier_model_version}` (version-anchored replay) · own dual-source `CorpusSource` (mirrored, tier-B not required for build/test) · advisory-only, no LLM/write/persistence.

**`outlier-model` (U18) stage status**: **Functional Design ✓ COMPLETE** · NFR Requirements ⏳ (next, on Continue) · NFR Design ⏳ · Infrastructure Design ⏳ · Code Generation ⏳. First P2 unit; 6 P2 units total (U18–U23).

**Register (unchanged)**: 23-unit decomposition intact (17 P1 done + 6 P2; U18 in progress); WIRE-1 pinned/untouched; composition-root deviation CLOSED; **Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN**; **tier-B corpus run still UNAUTHORIZED** (and not required for U18 build/test — BR-OUT-8); `audit_store` Docker-guard gap still deferred.

**Guardrails held**: NO code (FD stage); no `backend/outlier_model/` created; WIRE-1 untouched; all 17 frozen P1 units untouched; the closed composition root untouched; tier-B NOT authorized; audit_store Docker-guard gap untouched; no other unit started; the 23-unit decomposition unchanged.

**STOPPED** at the FD 2-option completion gate (1. Request Changes / 2. Continue to Next Stage → NFR Requirements) — did NOT advance past the gate.

## 🧩 BUILD → `outlier-model` (U18) — FD APPROVED (Continue; BR-OUT-3 imputation retained, 6-field alternative declined); NFR Requirements Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-16

**FD APPROVED 2026-07-16 (Continue → NFR Requirements)** — `outlier-model` Functional Design COMPLETE (3 artifacts frozen). **BR-OUT-3 corpus-median imputation RETAINED** (user declined the 6-field-only alternative — real signal from bmi_derived/existing_debt_obligations_annual/dti_ratio kept; the by-construction zero-flag-from-imputation guarantee is the accepted design).

**NFR Requirements Part 1 (Plan) WRITTEN**: `guide-docs/build/plans/outlier-model-nfr-requirements-plan.md` — built ON the frozen FD (BR-OUT-1..10, four-component inventory, OutlierResult/FlaggedFeature/OutlierProvenance schemas, the allow-list, the imputation policy, the fit/score lifecycle), re-opening none. **§2.5 draft NFR-OUT-* map** (13 targets, every BR-OUT-* mapped, no orphan): **NFR-OUT-BIAS-1** (load-bearing: structural/AST demographic-exclusion scan + swap-invariance teeth) ← BR-OUT-1; FEAT-1 ← BR-OUT-2; IMPUTE-1 (imputed field z-score exactly 0, never flagged) ← BR-OUT-3; **DET-1** (load-bearing: byte-identical OutlierResult across N runs) + PROV-1 (provenance-completeness) ← BR-OUT-4; COMPOSE-1 ← BR-OUT-5; THRESHOLD-1 ← BR-OUT-6; EXPLAIN-1 (construction-time: FlaggedFeature cannot instantiate without shap_value) ← BR-OUT-7; CORPUS-1 (dual-source + tier-B independence) ← BR-OUT-8; ADVISORY-1 ← BR-OUT-9; SCOPE-1 (no import of quality_gates/memo_agent_core/ui-outlier-view/observability) ← BR-OUT-10; PERF-1 (soft) ← SHAP/fit cost; SEC-1 (governance). **THREE [Answer] questions (BLANK)**: Q1 IsolationForest determinism (behavioral same-input-twice vs golden-master vs hybrid); Q2 SHAP tier/perf (tier-U correctness + soft-observed runtime vs hard SHAP SLO vs defer); Q3 threshold testing (parameterized off the named constant vs hardcode 3.0 vs existence-only). Each with a recommendation; none improvised.

**`outlier-model` (U18) stage status**: FD ✓ · **NFR Requirements ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers, Part 2 = nfr-requirements.md + tech-stack-decisions.md on explicit go) · NFR Design ⏳ · Infrastructure Design ⏳ · Code Generation ⏳.

**Guardrails held**: NO NFR artifact; no code; WIRE-1 untouched; all 17 frozen P1 units untouched; the closed composition root untouched; tier-B NOT authorized (and not required — BR-OUT-8/NFR-OUT-CORPUS-1); audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. **STOPPED** at the plan-file gate awaiting the user's Q1–Q3 answers.

## 🧩 BUILD → `outlier-model` (U18) — NFR Requirements COMPLETE (Part 1 all-A + ambiguity-check CLEAN [3 folds, each a concrete test refinement] + Part 2 two artifacts); STOP at NFR Requirements 2-option gate — 2026-07-16

**NFR Requirements Part 1 APPROVED** — Q1–Q3 answered (**all A**), full Q&A embedded in `guide-docs/build/plans/outlier-model-nfr-requirements-plan.md` §3. **Ambiguity-check RUN (§3.5) → CLEAN; THREE folds, each a concrete test refinement** (not a stop, none improvised):
- **CG-NFR-OUT-Fold-1** (check i): NFR-OUT-DET-1 teeth **perturb numpy's global RNG state between the two runs** and assert byte-identical — proving IsolationForest(random_state=int) is **seed-local** (verified on disk: byte-identical across a global-RNG perturbation) + catching the numpy-global-leak class. Cross-process = optional hardening.
- **CG-NFR-OUT-Fold-2** (check ii): NFR-OUT-THRESHOLD-1 gains a **strict positivity guard (`Z_SCORE_FLAG_THRESHOLD > 0`)** — an imputed feature (z==0) could flag only under a degenerate <=0 threshold, so positivity makes BR-OUT-3's 'imputed never flags' calibration-robust.
- **CG-NFR-OUT-Fold-3** (check iii): NFR-OUT-SCOPE-1's forward-looking scans (ui-outlier-view/observability don't exist yet) are **regression guards proven by the mandatory detector self-test** (synthetic import line → asserted flagged); quality_gates + memo_agent_core exist so the scan is non-vacuous today too.

**NFR Requirements Part 2 GENERATED** — two artifacts under `guide-docs/build/outlier-model/nfr-requirements/`:
- `nfr-requirements.md` — **thirteen NFR-OUT-* targets** (pass/fail + acceptance + tier + rigor); load-bearing **NFR-OUT-BIAS-1** (AST demographic-exclusion scan + swap-invariance teeth) + **NFR-OUT-DET-1** (determinism + global-RNG-perturbation teeth) at full-highest; FEAT-1/IMPUTE-1/PROV-1/COMPOSE-1/THRESHOLD-1/EXPLAIN-1(construction-time)/CORPUS-1(tier-B independence)/ADVISORY-1/SCOPE-1 at full; PERF-1 soft; SEC-1 governance. Traceability table no orphan (every BR-OUT-1..10 mapped). Full Security-Guardrails table (bias-free + reproducibility + explainability Compliant; no blocking finding).
- `tech-stack-decisions.md` — OUT-D1..D9; the outlier_model_version version-anchoring discipline; **NO new dependency** (sklearn/shap/numpy/pandas already floored in requirements.txt, verified + installed: sklearn 1.9.0 / shap 0.52.0 / numpy 2.4.6).

**`outlier-model` (U18) stage status**: FD ✓ · **NFR Requirements ✓ COMPLETE** · NFR Design ⏳ (next, on Continue) · Infrastructure Design ⏳ · Code Generation ⏳.

**Register (unchanged)**: 23-unit decomposition intact (17 P1 done + 6 P2; U18 in progress); WIRE-1 pinned/untouched; composition-root deviation CLOSED; Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN; **tier-B corpus run still UNAUTHORIZED** (and not required for U18 — NFR-OUT-CORPUS-1); audit_store Docker-guard gap still deferred.

**Guardrails held**: NO code (NFR stage); no `backend/outlier_model/` created; WIRE-1 untouched; all 17 frozen P1 units untouched; the closed composition root untouched; tier-B NOT authorized; audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. **STOPPED** at the NFR Requirements 2-option completion gate (1. Request Changes / 2. Continue → NFR Design).

## 🧩 BUILD → `outlier-model` (U18) — NFR Requirements APPROVED (Continue); NFR Design Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-16

**NFR Requirements APPROVED 2026-07-16 (Continue → NFR Design)** — `outlier-model` NFR-Requirements COMPLETE (2 artifacts frozen). Advanced to the per-unit **NFR Design** stage; confirmed the SeedLocalDeterminismPattern mechanism on disk (IsolationForest accepts a `np.random.RandomState` **instance** → construct-and-inject a local RandomState, never touch global numpy).

**NFR Design Part 1 (Plan) WRITTEN**: `guide-docs/build/plans/outlier-model-nfr-design-plan.md` — built ON the frozen FD + the thirteen NFR-OUT-* targets, re-opening none. **§2.5 draft pattern set P-OUT-1..9** (each → its NFR-OUT-* + component, no orphan): **P-OUT-1 AllowlistProjectionPattern** → BIAS-1/FEAT-1; **P-OUT-2 SeedLocalDeterminismPattern** → DET-1; **P-OUT-3 ImputeThresholdCompositionPattern** → IMPUTE-1/THRESHOLD-1 (imputed z==0 + threshold>0 ⇒ cannot-flag, composed); **P-OUT-4 SoleExplainerConstructionPattern** → EXPLAIN-1 (call-site); **P-OUT-5 ScoreFlagExplainCompositionPattern** → COMPOSE-1; **P-OUT-6 DualSourceSeamPattern** → CORPUS-1; **P-OUT-7 VersionAnchoredProvenancePattern** → PROV-1; **P-OUT-8 StructuralGuardPattern** → SCOPE-1/ADVISORY-1; **P-OUT-9 ReferencedObservedBoundaryPattern** → PERF-1/SEC-1. **FOUR [Answer] questions (BLANK)**: Q1 (meta, user-flagged) the by-construction MECHANISM for a Python unit (Python-native structural mechanisms as primary + scans as regression + header comments as documentation-only, vs comments-as-guarantee, vs scans-only); Q2 demographic exclusion (typed intermediate projection vs accessor-map vs both); Q3 seed-locality (inject explicit RandomState instance + no-global-np.random scan vs int random_state vs both); Q4 EXPLAIN-1 call-site (ShapExplainer as sole FlaggedFeature constructor vs make_flag factory vs schema-only). Each with a recommendation; none improvised.

**`outlier-model` (U18) stage status**: FD ✓ · NFR Requirements ✓ · **NFR Design ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers, Part 2 = nfr-design-patterns.md + logical-components.md on explicit go) · Infrastructure Design ⏳ · Code Generation ⏳.

**Guardrails held**: NO NFR-Design artifact; no code; WIRE-1 untouched; all 17 frozen P1 units untouched; the closed composition root untouched; tier-B NOT authorized (not required — NFR-OUT-CORPUS-1); audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. **STOPPED** at the plan-file gate awaiting the user's Q1–Q4 answers.

## 🧩 BUILD → `outlier-model` (U18) — NFR Design COMPLETE (Part 1 all-A + ambiguity-check CLEAN [3 folds; Fold-1 reconciled a frozen-FD median/z=0 inconsistency] + Part 2 two artifacts, two validated Mermaids); STOP at NFR Design 2-option gate — 2026-07-16

**NFR Design Part 1 APPROVED** — Q1–Q4 answered (**all A**), full Q&A embedded in `guide-docs/build/plans/outlier-model-nfr-design-plan.md` §3. **Ambiguity-check RUN (§3.5) → CLEAN; THREE folds**:
- **🟠 CG-ND-OUT-Fold-1 (check i — HEADLINE, a frozen-FD inconsistency reconciled)**: **verified numerically** the FD's 'impute to corpus MEDIAN' + 'imputed z-score EXACTLY 0 by construction' are **inconsistent** for a skewed feature (median imputation → z ≈ −0.43, not 0; z is vs the corpus MEAN/std). Frozen **intent** (imputed never flags) preserved; **mechanism corrected**: the `FeatureInputs` projection tracks an **`imputed` mask**, the median feeds the IsolationForest score, and at **flagging** an imputed feature's z is **0 by design** (a missing value is not anomaly evidence) — so 'imputed never flags' is a real by-construction property. Folded into P-OUT-3 + signatures; **flagged for confirmation at the gate**.
- **🟢 CG-ND-OUT-Fold-2 (check ii)**: `score()` → `ShapExplainer.explain(candidates)`; `explain([])` short-circuits to `[]` (normal applicant runs no SHAP, builds zero flags) — clean, non-degenerate; sole-constructor pattern holds trivially. Confirmed.
- **🟢 CG-ND-OUT-Fold-3 (check iii)**: the seed flows **only** into OutlierModel→IsolationForest; CorpusSource (I/O), FeatureVectorBuilder (median=deterministic statistic), ShapExplainer (TreeExplainer=deterministic) need no seed. Confirmed; caveat noted (a sampling-explainer fallback would extend the same injected-RandomState discipline).

**NFR Design Part 2 GENERATED** — two artifacts under `guide-docs/build/outlier-model/nfr-design/`:
- `nfr-design-patterns.md` — **P-OUT-1..9** each meeting its NFR-OUT-* + tier (P-OUT-1 AllowlistProjection + P-OUT-2 SeedLocalDeterminism load-bearing; P-OUT-3 ImputeThresholdComposition revised per Fold-1; P-OUT-4 SoleExplainerConstruction; P-OUT-5..9); a **validated module Mermaid** (10 nodes, 7 rules passed) with **demographic-exclusion + RNG-isolation as visible dashed 'blocked' edges** + text alt; pattern→target→tier→rigor traceability (no orphan, all 13).
- `logical-components.md` — five components (FeatureVectorBuilder/CorpusSource/OutlierModel/ShapExplainer/StructuralGuard) with **exact by-construction method signatures** (FeatureInputs frozen dataclass `values`+`imputed` mask, no demographics field; injected RandomState in OutlierModel.fit; ShapExplainer.explain sole FlaggedFeature constructor w/ empty short-circuit); a **validated component Mermaid** (6 nodes, 7 rules passed) + text alt; reference-not-own in **three distinct categories** (consumed-by-shape / mirrored-not-imported / excluded); component→target coverage (no orphan); settled items.

**`outlier-model` (U18) stage status**: FD ✓ · NFR Requirements ✓ · **NFR Design ✓ COMPLETE** · Infrastructure Design ⏳ (next, on Continue) · Code Generation ⏳.

**Register (unchanged)**: 23-unit decomposition intact (17 P1 done + 6 P2; U18 in progress); WIRE-1 pinned/untouched; composition-root deviation CLOSED; Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN; **tier-B still UNAUTHORIZED** (not required — NFR-OUT-CORPUS-1); audit_store Docker-guard gap still deferred.

**Guardrails held**: NO code (NFR-Design stage); no `backend/outlier_model/` created; WIRE-1 untouched; all 17 frozen P1 units untouched; the closed composition root untouched; tier-B NOT authorized; audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. **STOPPED** at the NFR Design 2-option completion gate (1. Request Changes / 2. Continue → Infrastructure Design).

## 🧩 BUILD → `outlier-model` (U18) — NFR Design APPROVED (Continue; imputed-mask retained) → Infrastructure Design SKIPPED (logged, rule-justified) = the 17th skip + FIRST Phase-2 skip; STOP at Infra 2-option gate; NEXT = Code Generation — 2026-07-16

**NFR Design APPROVED 2026-07-16 (Continue → Infrastructure Design)** — `outlier-model` NFR-Design COMPLETE. **CG-ND-OUT-Fold-1's imputed-mask reconciliation RETAINED** (affirmed over mean-imputation — the mask makes 'imputed never flags' skew-robust and encodes 'missingness isn't anomaly evidence', the underlying principle).

**Infrastructure Design ASSESSED (not pre-assumed) → logged SKIP.** Infra ambiguity-check surfaced **no genuine outlier-model-owned infra concern**; all four assessment points verified on disk: (1) no untrusted parsing / no subprocess sandbox (reads validated shapes; `from_file` reads a trusted self-generated corpus JSON); (2) no persistence it provisions (`CorpusSource` reads by shape, 'owns nothing persisted', no DB); (3) **no LLM/provider access whatsoever** (pure sklearn/numpy/shap — a distinguishing fact vs memo-agent-core, which HAD a real LLM infra concern); (4) no deployed service, no new dependency (sklearn/shap/numpy already floored+installed), no WIRE-1 route of its own (consumed by memo-agent-core/ui-outlier-view/observability, none of which exist yet); (5, also checked) no fitted-model-artifact persistence (fit-at-runtime; caching is a downstream/Code-Gen concern).

**Rule justification (explicit)**: CLAUDE.md Infrastructure Design 'Skip IF: No infrastructure changes' + `execution-plan.md:200` — 'pure-logic units (rules-engine, **outlier-model**, memo-agent logic) have little independent infra.' The frozen decomposition itself backs the skip.

**Skip roster now SEVENTEEN**: intake · document-sanitizer · rules-engine · memo-agent-core · auth-rbac · audit-store · quality-gates · corpus-generator · secrets-config · admin-cli · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form · ui-history · **outlier-model** — **the FIRST Phase-2 unit to receive a skip**; **database** remains the one real non-skip (verified: only `database` has an `infrastructure-design/` dir). **NO infra artifact created** (`guide-docs/build/outlier-model/infrastructure-design/` NOT created — consistent with all prior skips).

**`outlier-model` (U18) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · **Infrastructure Design ✓ SKIPPED (logged)** · **Code Generation ⏳** (the LAST stage for U18 — Part-1-plan-then-Part-2-generate, own approval gate).

**Register (unchanged)**: 23-unit decomposition intact (17 P1 done + 6 P2; U18 in progress, now through 4 of 5 stages); WIRE-1 pinned/untouched; composition-root deviation CLOSED; Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN; **tier-B still UNAUTHORIZED** (not required — NFR-OUT-CORPUS-1); audit_store Docker-guard gap still deferred.

**Guardrails held**: NO code; no `backend/outlier_model/` created; no infra artifact created; WIRE-1 untouched; all 17 frozen P1 units untouched; the closed composition root untouched; tier-B NOT authorized; audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. **STOPPED** at the Infrastructure Design 2-option completion gate (1. Request Changes / 2. Continue → Code Generation).

## 🧩 BUILD → `outlier-model` (U18) — Infrastructure Design SKIP APPROVED (Continue); Code Generation Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-16

**Infrastructure Design SKIP APPROVED 2026-07-16 (Continue → Code Generation)** → `outlier-model` advanced to the per-unit **Code Generation** stage (the LAST stage for U18); wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/outlier-model-code-gen-plan.md`. **NO code generated; NO file under `backend/outlier_model/` created.**

**Grounded** (re-derived none) on the frozen FD (BR-OUT-1..10, four-component inventory, schemas, imputation policy) + approved NFR Requirements (13 NFR-OUT-*) + approved NFR Design (P-OUT-1..9, exact method signatures, CG-ND-OUT-Fold-1 imputed-mask) **and the realized backend convention on disk** (rules-engine multi-module + tests/; the frozen `auth_rbac/tests/test_no_forbidden_imports.py` ast.parse scan-with-self-test as the StructuralGuard precedent; pyproject `--cov` addopts).

**Plan contents**: **§2 component→module map** (`feature_fields.py` [OUTLIER_FEATURE_FIELDS + FeatureInputs], `feature_vector.py` [CorpusImputer + fit_imputer/project], `corpus_source.py`, `schemas.py` [OutlierResult/FlaggedFeature (shap_value required)/OutlierProvenance], `shap_explainer.py` [sole FlaggedFeature constructor], `model.py` [injected RandomState + fit/score]) each with its **header-comment deliverable** (documentation-only, Q1-A of NFR-Design); **§3 TDD test→target map** — all 13 NFR-OUT-* at their tiers, **BIAS-1 (AST + swap teeth) + DET-1 (determinism incl. global-RNG-perturbation) at full-highest**, IMPUTE-1 (mask-driven zero-flag, post-Fold-1), THRESHOLD-1 (parameterized + positivity), EXPLAIN-1 (construction-time + single-constructor scan), COMPOSE-1, CORPUS-1 (dual-source + tier-B independence), PROV-1, SCOPE-1 (incl. forward-looking ui_outlier_view/observability scans + self-tests), ADVISORY-1, PERF-1 soft — **no orphan**; **§4 leaf-first Steps 0–9** (feature_fields → corpus_source → feature_vector → schemas → shap_explainer → model → StructuralGuard → coverage → summary); **§5 HOLDS**; **§6 coverage gate** (backend **960/31 no regression**, pure additive, comprehensive `--cov-fail-under=90` bar unchanged); **§7 SIX [Answer] questions** (Q1 pytest+Hypothesis; Q2 module organization; Q3 seeded fixture corpus incl. missing-optional + swap pair; Q4 global-RNG-perturbation sequence; Q5 AST-scan + detector-self-test mirroring auth-rbac; Q6 coverage config); **§8 gate**. All six tags BLANK, each with a recommendation.

**`outlier-model` (U18) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · **Code Generation ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers, Part 2 = §4 Steps 0–9 on explicit go). **This is the LAST stage for the FIRST Phase-2 unit.**

**Register (unchanged)**: 23-unit decomposition intact (17 P1 done + 6 P2; U18 in progress, now through 4 of 5 stages); WIRE-1 pinned/untouched; composition-root deviation CLOSED; Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN; tier-B still UNAUTHORIZED (not required); audit_store Docker-guard gap still deferred.

**Guardrails held**: NO code; NO file under `backend/outlier_model/`; WIRE-1 untouched; all 17 frozen P1 units untouched; the closed composition root untouched; tier-B NOT authorized (not required); audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. **STOPPED** at the Code-Gen plan-file gate awaiting the user's Q1–Q6 answers + review before Part 2.

## 🧩 BUILD → `outlier-model` (U18) — Code Generation COMPLETE (Q1–Q6 all-A + ambiguity-check CLEAN [realizations noted, none improvised] + Part 2 §4 Steps 0–9 executed TDD/leaf-first); STOP at diff-review gate — U18 is the FIRST fully-complete Phase-2 unit — 2026-07-17

**Code-Gen Part 1 answers FILLED (Q1–Q6 all A)** — embedded in `guide-docs/build/plans/outlier-model-code-gen-plan.md` §7 (standing convention). **Ambiguity-check RUN → CLEAN** — no surface-and-stop; every open item was an explicitly Code-Gen-deferred realization (mirror-not-import derivations; near-zero-variance z-guard; IsolationForest hyper-params; `outlier_model_version` string; TreeExplainer wiring — all empirically verified: sklearn 1.9.0 / shap 0.52.0 / numpy 2.4.6, TreeExplainer works on IsolationForest). Verdict recorded in plan §Status.

**Part 2 GENERATED** — `backend/outlier_model/` realized TDD tests-first, leaf-first per §4 Steps 0–9 (all `[x]`): **7 production modules** (`feature_fields.py`, `corpus_source.py`, `feature_vector.py`, `schemas.py`, `shap_explainer.py`, `model.py`, `__init__.py`) + **15 test files** + `tests/fixtures.py` (one seeded synthetic corpus: normal / missing-optional / swap-pair / outlier) + `tests/structural.py` (AST substrate). Summary → `guide-docs/build/outlier-model/code/code-summary.md`; `testresults.txt` refreshed.

**By-construction guarantees realized** (each with its header comment, documentation-only): `FeatureInputs` has **no demographics field** (BIAS-1); IsolationForest gets an **injected local `RandomState(manifest.seed)`** — global `np.random.*` never touched (DET-1); `ShapExplainer` is the **sole `FlaggedFeature` constructor** (EXPLAIN-1); the **imputed-mask** forces flagging z=0 so a missing value never flags (CG-ND-OUT-Fold-1 / IMPUTE-1); `Z_SCORE_FLAG_THRESHOLD=3.0` with a strict-`>0` guard (THRESHOLD-1). Five AST StructuralGuard scans, each with a detector self-test (SCOPE-1 incl. forward-looking `ui_outlier_view`/`observability`; ADVISORY-1; + the structural halves of BIAS/DET/EXPLAIN).

**Quality gate PASSED**: backend **1011 passed / 31 skipped** (960 baseline + **51** new, no regression; the 5 pre-existing `audit_store` Docker-absence errors unchanged); `backend/outlier_model` **100%**; `--cov-fail-under=90` holds at **99.84%**. `--cov=backend/outlier_model` added to `pyproject` addopts (gate unchanged, no omit). **No P1-unit file touched; the closed composition root (`backend/app`, `frontend/src/app`) untouched.**

**`outlier-model` (U18) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · **Code Generation ✓ APPROVED 2026-07-17** (Continue → Next Stage, diffs reviewed). **U18 COMPLETE — the 18th complete build-loop unit overall, the FIRST of the 6 Phase-2 units.**

## ✅ UNIT COMPLETE — `outlier-model` (U18, C3, Phase 2) — approved as delivered 2026-07-17

**CLOSED, approved as delivered** — the per-unit BUILD loop for `outlier-model` is complete (all five stages: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design SKIPPED-logged ✓ · Code-Gen ✓). **The 18th complete build-loop unit overall and the FIRST of the 6 Phase-2 units (U18–U23).** Backend **1011 passed / 31 skipped** (960 baseline + **51** new, **zero regression**; the 5 pre-existing `audit_store` Docker-absence errors unchanged); `backend/outlier_model` **100%**; project-wide `--cov-fail-under=90` gate held at **99.84%**. Both load-bearing targets passed with full teeth — **BIAS-1** (AST + swap → byte-identical) and **DET-1** (determinism + global-RNG-perturbation, incl. the **negative self-test** that discriminates the no-global-RNG scan from the sanctioned `from numpy.random import RandomState`). The **near-zero-variance relative z-guard** is a genuine defensive refinement composing with the **imputed-mask** so "imputed never flags" is robust against **both skew AND floating-point noise**. Summary → `guide-docs/build/outlier-model/code/code-summary.md`; plan (status Part-2 GENERATED, Steps 0–9 `[x]`, six answers embedded) → `guide-docs/build/plans/outlier-model-code-gen-plan.md`; `testresults.txt` refreshed. Full record: the audit.md entries (answers/generate opened 05:37:47Z, approved/closed this entry).

**Register (unchanged)**: 23-unit decomposition intact (17 P1 + 6 P2 = 23; **U18 COMPLETE**, 1 of 6 P2 done, **5 P2 remain**: U19 `memo-extensions` · U20 `ui-outlier-view` · U21 `observability` · U22 `llm-judge` · U23 `deploy-config`); WIRE-1 pinned/untouched; composition-root deviation CLOSED but its **Q1-B READ_AUDIT-vs-WIRE-1 "authenticated" divergence still OPEN**; **R2–R5 still unwired** (the core underwriting demo path is still not runnable end-to-end); **tier-B corpus run still UNAUTHORIZED** (and confirmed NOT required for U18 — `CorpusSource` builds/tests on in-memory fixtures); **audit_store Docker-guard hygiene gap still DEFERRED** (non-blocking).

**Guardrails held**: only `backend/outlier_model/` created + the `pyproject` `--cov=backend/outlier_model` line added; WIRE-1 untouched; all 17 frozen P1 units untouched; the closed composition root (`backend/app`, `frontend/src/app`) untouched; tier-B NOT authorized; audit_store Docker-guard gap untouched; **no next unit started; nothing else touched.** **STOPPED — the next-move decision is the user's.**

## 🔗 WIRE-1 additive amendment (WIRE1-Fold-4) — APPROVED + APPLIED 2026-07-17 — R4 MemoView.outlier + FlagDirection wire enum (U20 prerequisite)

**Same pin, additive — NOT a new contract version.** Approved + applied 2026-07-17 to close U20's prerequisite wire-surface gap (R1–R7 carried no outlier surface). **Option (a)** chosen over a new-route (b): R4 `MemoView` gained an additive `outlier: OutlierResult | null` field carrying U18's frozen `OutlierResult` **by value**; a fifth §1 by-value enum `FlagDirection` (`high`/`low`) added; new `OutlierResult` shape entry in §5; new §7.1 `WIRE1-Fold-4` records the rationale (services.md combined case-detail payload + same pipeline pass + minimal contract change + advisory-only preserved) and the **binding semantics** (`outlier` null in Phase 1 and when `status: pending`, populated only for a Phase-2 `ready` view). R1–R7 route table / envelope / error shape / role delivery **byte-unchanged**; advisory-only preserved (OutlierResult has no verdict field); **no frozen P1 unit edited** (MemoView is WIRE-1-owned; OutlierResult by value). **Implementation reconciliation deferred** — R4 is a `501` stub in the closed composition root; `backend/app/` NOT touched. Files touched: `api-contract.md` + one-line acks in `guide-state.md`/`integration-summary.md`/`composition-root-integration-plan.md` + `audit.md`; a same-day §8-Holds count-correction follow-up (five enums / six response shapes by value) kept the amendment internally consistent. Full record: audit.md entries 05:59:50Z (amendment) + 06:03:02Z (follow-up).

## 🧩 BUILD → `ui-outlier-view` (U20, C5, **Phase 2** — the 2nd P2 unit) — Functional Design Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-17

**FIRST touch of U20 — DISCOVER-carryover CLEAN** (no `guide-docs/build/ui-outlier-view/`, no plan, no `frontend/src/outlierView/`). **Depth VERIFIED lighter (display)** — `unit-of-work.md:247` (*"no write/commit control → no RBAC facet"*; `:261–263` lists it among the display-only lighter candidates); recommendation lighter (one story US-UI-3, one R4 field, no write path), matching the frozen `ui-memo-view`/`ui-queue`/`ui-history` lighter precedent.

**FD Part 1 (Plan) WRITTEN**: `guide-docs/build/plans/ui-outlier-view-functional-design-plan.md` — built ON (re-deriving none): the amended **WIRE-1 R4 `MemoView.outlier`** + `OutlierResult`/`FlaggedFeature`/`OutlierProvenance`/`FlagDirection` wire shapes (**WIRE1-Fold-4**); the frozen **`ui-shell` (U10)** substrate; the frozen **`outlier-model` (U18)** Python `schemas.py` (**confirmed wire↔Python field-for-field match**, plan §3); the sibling precedent **`ui-memo-view` (U6)** (own-fetch/mirror-not-import, lighter 3-artifact FD set, NFR-MEMO-SEPARATION-1, NFR-MEMO-VIEWONLY-1, NFR-MEMO-PENDING-1). The **`(orchestrated)` outlier-model edge** (`unit-of-work-dependency.md:49`) confirmed to mean **reached via R4, never imported** (and `ui_outlier_view` is exactly a name the U18 StructuralGuard forbids importing). **FIVE [Answer] questions (BLANK)**, each written in full with lettered options + a recommendation, none improvised: **Q1** structural relationship to ui-memo-view (rec A stand-alone own-fetch of R4 / B extend-frozen-tree rejected / C shared-composition rejected); **Q2** RoleGate/RBAC facet (rec A no-RoleGate view-only per :247); **Q3** display flags as statistical signals not a verdict (rec A advisory framing + reuse frozen advisory-vocabulary/no-inline-label lints + isolation-by-absence since the unit renders no Recommendation namespace / B dedicated SEPARATION-clone region); **Q4** null-`outlier` UI (A nothing-renders / rec B one explicit neutral "not available" state covering both null-causes, since a `ready` view can still carry `outlier:null` in Phase 1); **Q5** provenance display (rec A no-render-by-default + optional `outlier_model_version` footnote / B full-triple footer / C none).

**FD Part 2 GENERATED 2026-07-17** — Q1–Q5 answered (**A/A/A/B/A**), full Q&A embedded in `guide-docs/build/plans/ui-outlier-view-functional-design-plan.md` §6. **Ambiguity-check RUN → CLEAN (three folds, no surface-and-stop)**: **OUTV-FD-Fold-1** (the null-`outlier` `NOT_AVAILABLE` is a 4th distinct state derived off the field on a 2xx resolution — never masks a fetch ERROR); **OUTV-FD-Fold-2** (isolation-by-absence documented as forward-looking — a future combined memo+outlier screen's cross-panel separation is the integrator's responsibility, not a silent assumption); **OUTV-FD-Fold-3** (`direction` high/low rendered via `FLAG_DIRECTION_LABELS` as a statistical position, lint-subject, never a severity/verdict word). **Lighter 3-artifact FD set generated** under `guide-docs/build/ui-outlier-view/functional-design/`: `business-rules.md` (**BR-OUTV-1..10**) · `domain-entities.md` (composition boundary, R4 shapes by value, the 4-state render model, component/prop inventory, `FLAG_DIRECTION_LABELS`, testids, the Fold-2 forward-looking note) · `business-logic-model.md` (fetch/render lifecycle + a **validated rectangle-only Mermaid** + text alternative + advisory-only argument + reference-not-own boundary).

**FD APPROVED 2026-07-17 (Continue → NFR Requirements)** — `ui-outlier-view` Functional Design COMPLETE (3 artifacts frozen). Advanced to the per-unit **NFR Requirements** stage; verified on disk the frozen display-unit tier (Vitest + RTL + jsdom; single injected/capturing `fetchSeam` double; frozen `advisory-vocabulary`/`no-inline-label` ESLint lints — no new toolchain).

**NFR Requirements Part 1 (Plan) WRITTEN**: `guide-docs/build/plans/ui-outlier-view-nfr-requirements-plan.md` — built ON the frozen FD (BR-OUTV-1..10, the four-state model, the folds), re-opening none. **§2 draft `NFR-OUTV-*` map** (13 targets, every BR-OUTV-* mapped, no orphan): **STATE-1** (LOAD-BEARING — four-state + field-derived `NOT_AVAILABLE` reached only from a 2xx+null resolution, never a fetch failure) · **NOVERDICT-1** (no `Recommendation` namespace in rendered output) · ADVISORY-1 (frozen lints) · COPY-1 (`FLAG_DIRECTION_LABELS` statistical-position) · EMPTY-1 (empty `flagged_features` distinct from `NOT_AVAILABLE`) · LISTORDER-1 (non-sorted-fixture teeth) · ERROR-1 · VIEWONLY-1 · PROV-1 (negative: `seed`/`corpus_version` never rendered) · TESTID-1 · SCOPE-1 (no sibling/backend import + self-test) · FETCH-1 (single double, four-state machine) · NOTS-1. **THREE [Answer] questions (BLANK)**, each in full with lettered options + a recommendation, none improvised: **Q1** dedicated `NOVERDICT-1` target for the rendered-output absence-claim (rec A yes); **Q2** dedicated `EMPTY-1` target for empty-`flagged_features` vs `NOT_AVAILABLE` (rec A yes); **Q3** the optional `outlier_model_version` footnote — test both configs vs decide once at Code-Gen while always gating the `seed`/`corpus_version` negative (rec A decide once).

**NFR Requirements Part 2 GENERATED 2026-07-17** — Q1–Q3 answered (**all A**), full Q&A embedded in `guide-docs/build/plans/ui-outlier-view-nfr-requirements-plan.md` §4. **Ambiguity-check RUN → CLEAN (three folds, no surface-and-stop)**: **NFR-OUTV-Fold-B** (NOVERDICT-1 rendered-absence via `queryBy*`-null over an enumerated finite set + the import-absence scan as the primary robust half, never a substring `textContent` sweep) · **NFR-OUTV-Fold-C** (three distinct outlier fixtures: `null` / present-empty / present-populated, through the single double) · **NFR-OUTV-Fold-D** (PROV-1 distinctive collision-proof provenance sentinels). **Two artifacts generated** under `guide-docs/build/ui-outlier-view/nfr-requirements/`: `nfr-requirements.md` (**thirteen `NFR-OUTV-*`** with the **load-bearing pair STATE-1 + NOVERDICT-1**, each pass/fail + acceptance + tier, no-orphan traceability, full Security-Guardrails compliance table) · `tech-stack-decisions.md` (D-INH-1..6 inherited unchanged — React/Tailwind/Vitest/RTL/jsdom/ESLint, **no new dependency** — + D-OUTV-1..5 new: single injected/capturing `fetchSeam` double, three outlier fixtures, the rendered-absence technique, the provenance sentinels, the single-realization footnote).

**NFR Requirements APPROVED 2026-07-17 (Continue → NFR Design)** — `ui-outlier-view` NFR Requirements COMPLETE (2 artifacts frozen). Advanced to the per-unit **NFR Design** stage.

**NFR Design Part 1 (Plan) WRITTEN**: `guide-docs/build/plans/ui-outlier-view-nfr-design-plan.md` — built ON the frozen FD + the thirteen `NFR-OUTV-*` (+ Fold-A..D), re-opening none; grounded in the frozen UI NFR-Design precedent (`ui-memo-view` §P-named patterns + by-construction-via-prop-signatures; `ui-history` `CommittedActionRegion` prop-exclusion + header-comment self-evidence + visible-graph-property Mermaid). **§2 draft pattern set P-OUTV-1..10** (each → its NFR-OUTV-* + component, no orphan): **P-OUTV-1 FieldDerivedStateMachinePattern** (LOAD-BEARING — failure→ERROR routed **before** the `outlier`-null check, contrasted with ui-memo-view's status-derived) → STATE-1; **P-OUTV-2 NamespaceExclusionByPropSignaturePattern** (LOAD-BEARING — no `recommendation`/`confidence` prop or path, ui-history precedent) → NOVERDICT-1; **P-OUTV-3 ProvenanceExclusionByPropSignaturePattern** (regions never receive `provenance`/`seed`/`corpus_version` as props) → PROV-1; P-OUTV-4 DistinctBranchEmptyVsAbsent → EMPTY-1; P-OUTV-5 OrderPreservingList → LISTORDER-1; P-OUTV-6 FetchSeam → FETCH-1; P-OUTV-7 ErrorEnvelopeToRender → ERROR-1; P-OUTV-8 RoleInvariantRendering → VIEWONLY-1; P-OUTV-9 SharedForbiddenTermsReuse → ADVISORY-1/COPY-1; P-OUTV-10 StructuralGuard → SCOPE-1/TESTID-1/NOTS-1. **Six named components** (`OutlierView`/`fetchSeam`/`OutlierStateView`/`OutlierScoreRegion` `{outlierScore,isOutlier,testid}`/`FlaggedFeaturesRegion` `{flaggedFeatures,testid}` — no verdict/provenance prop/`StructuralGuard`) + reference-not-own + component→target coverage (no orphan). **THREE by-construction [Answer] questions (BLANK)**: Q1 state-machine failure-routing structural-vs-test-only (rec A structural); Q2 recommendation/confidence prop-exclusion structural-vs-test-only (rec A structural); Q3 provenance prop-exclusion structural-vs-test-only (rec A structural).

**NFR Design Part 2 GENERATED 2026-07-17** — Q1–Q3 answered (**all A — structural**), full Q&A embedded in `guide-docs/build/plans/ui-outlier-view-nfr-design-plan.md` §4. **Ambiguity-check RUN → CLEAN (one fold, no surface-and-stop)**: **NFR-ND-OUTV-Fold-1** — header comments **PINNED MANDATORY** (no longer a "candidate") on `OutlierView`/`OutlierScoreRegion`/`FlaggedFeaturesRegion`/`fetchSeam`, mirroring `ui-history` NFR-DESIGN-Fold-1 + `ui-approval-gate` (documentation only, not enforcement). **Two artifacts generated** under `guide-docs/build/ui-outlier-view/nfr-design/`: `nfr-design-patterns.md` (**P-OUTV-1..10**; the load-bearing pair **P-OUTV-1** [failure-first branch ordering spelled out as code] + **P-OUTV-2** [exact prop shapes] with mechanism not assertion; validated pattern-integration Mermaid + text alt; pattern→target→tier traceability, no orphan) · `logical-components.md` (six components + exact prop shapes — `OutlierScoreRegion {outlierScore,isOutlier,testid}` / `FlaggedFeaturesRegion {flaggedFeatures,testid}`, no verdict/provenance path; header comments mandatory; a validated component-relationship Mermaid showing the **no-verdict AND no-provenance guarantees as visible blocked edges** + text alt; reference-not-own kept in two distinct categories; component→target coverage, no orphan).

**`ui-outlier-view` (U20) stage status**: FD ✓ · NFR Requirements ✓ · **NFR Design ✓ Part 2 GENERATED → STOPPED at the NFR Design 2-option completion gate** (1. Request Changes / 2. Continue → Infrastructure Design) · Infrastructure Design ⏳ · Code Generation ⏳. **The 2nd of 6 Phase-2 units.**

**Register (unchanged)**: 23-unit decomposition intact (17 P1 done + 6 P2; U18 COMPLETE, U20 in progress — FD Part 1; 4 P2 remain beyond U20: memo-extensions/observability/llm-judge/deploy-config); WIRE-1 PINNED (+WIRE1-Fold-4 additive amendment); composition-root deviation CLOSED, its Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN; R2–R5 still unwired (core demo path not runnable end-to-end); tier-B still UNAUTHORIZED; audit_store Docker-guard gap still DEFERRED.

**Guardrails held**: NO FD artifact; `guide-docs/build/ui-outlier-view/functional-design/` NOT created; no code; no `frontend/src/outlierView/`; WIRE-1 not touched further; `outlier-model` (U18) not touched (reached only via R4, never imported); all 17 frozen P1 units + `ui-shell`/`ui-memo-view` untouched; the closed composition root untouched; tier-B NOT authorized; audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. **STOPPED** at the FD plan-file gate awaiting the user's Q1–Q5 answers before the ambiguity-check and Part 2.

## 🧩 BUILD → `ui-outlier-view` (U20) — NFR Design APPROVED (Continue) → Infrastructure Design ASSESSED → SKIPPED (logged, rule-justified) = the 18th skip + 2nd Phase-2 skip + 7th React-unit skip; STOP at Infra 2-option gate; NEXT = Code Generation — 2026-07-17

**NFR Design APPROVED 2026-07-17 (Continue → Infrastructure Design)** — `ui-outlier-view` NFR-Design COMPLETE (2 artifacts frozen: `nfr-design-patterns.md` P-OUTV-1..10 + `logical-components.md` C-OUTV-1..6). The 07:05:25Z gate is closed.

**Infrastructure Design ASSESSED AT THE STAGE (not pre-assumed) → logged SKIP.** Infra ambiguity-check surfaced **no genuine `ui-outlier-view`-owned infra concern**; all five assessment points verified against the frozen artifacts on disk:
1. **No untrusted parsing / no subprocess sandbox** — renders an already-validated typed WIRE-1 R4 JSON body (`nfr-requirements.md §3`: "renders no free input"); R4 mocked via the single injected/capturing `fetchSeam` double (D-OUTV-1 / Fold-A); no pdfplumber/subprocess/file parsing.
2. **No independent persistence it provisions** — fetches R4 through its **own-local** `fetchSeam` (C-OUTV-2: builder emits **only** `{method:'GET', path}`; no request-body builder, no `submit*` — write structurally absent); never touches a database and never touches `outlier-model`'s internals (BR-OUTV-10: **not imported**, reached only `(orchestrated)` via R4 — the reciprocal of U18's `StructuralGuard` forbidding `ui_outlier_view`); no store, no migration. `nfr-requirements.md §3`: "Read-only DB access — N/A: no DB access, no persistence." Persistence stays `audit-store`'s, provisioned by `database` (the one non-skip).
3. **No LLM/provider access whatsoever** — pure presentational React (`nfr-requirements.md §3`: "no LLM / prompt path"); renders U18's sklearn/SHAP-produced statistical signals; the R4 body's LLM-authored `memo` field is **named-not-rendered** here (`domain-entities.md §2`). Holds no provider client.
4. **No deployed service / no independent cloud topology / no new dependency / no route implementation** — a source-level React unit of six components under `frontend/src/outlierView/`. `tech-stack-decisions.md` D-INH-1..6 inherit the frozen React/Tailwind/Vitest/RTL/jsdom/ESLint substrate unchanged — "**No new runtime or dev dependency is introduced by U20**"; §3 explicitly rules out a live backend / MSW / network **and** any new component-library or charting dependency. Bundler/dev-server + **Vercel topology → `deploy-config` (P2, U23 — not yet built)**; real `fetchSeam` transport wiring + the R4 route impl (`backend/app/main.py`) → composition root / Build & Test.
5. **(also checked) No new secret / env var / service** — `nfr-requirements.md §3`: "no secret is used or rendered"; "persists nothing." No fitted-model artifact (that was U18's concern, already skip-assessed).

**The newly-amended-WIRE-1-consumer question — explicitly assessed, not waved through**: being the **first and only consumer** of R4's additive `outlier` field + the `FlagDirection` enum (both added by **WIRE1-Fold-4**, 2026-07-17) does **not** by itself create infrastructure to design. WIRE1-Fold-4 was **additive on the same pin** — one optional field on an **existing** route + one by-value enum; **no new route, no new scope item, no new topology**. **R4 remains a `501` stub in the closed composition root regardless**, so U20's reads flow through the **same deferred composition-root wiring pattern as every prior UI unit**. New data on an existing route consumed by a new display component is a new category of **application behavior, NOT infrastructure** — the identical reasoning applied to ui-shell / ui-queue / ui-memo-view / ui-approval-gate / ui-override-form / ui-history. Payload/caching/CORS/rate-limiting → deploy-config (P2) or backend, not this unit's. → **SKIP correct, no STOP.**

**Rule justification (explicit)**: CLAUDE.md Infrastructure Design "Skip IF: **No infrastructure changes** / Infrastructure already defined" + `execution-plan.md:200` — the *Lighter / minimal-footprint* classing whose UI clause reads verbatim "**`ui-*` is static hosting on Vercel**" (the UI units' only infra **is** the Vercel static-hosting topology, and that topology is `deploy-config`'s P2 scope, not each view's). The frozen decomposition itself backs the skip.

**Skip roster now EIGHTEEN**: intake · document-sanitizer · rules-engine · memo-agent-core · auth-rbac · audit-store · quality-gates · corpus-generator · secrets-config · admin-cli · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form · ui-history · outlier-model · **ui-outlier-view** — the **2nd Phase-2 skip** and the **7th React-unit skip**; **database** remains the ONE real non-skip (re-verified on disk: `guide-docs/build/database/infrastructure-design` is the only such directory). **NO infra artifact created** (`guide-docs/build/ui-outlier-view/infrastructure-design/` NOT created — consistent with all seventeen prior skips).

**`ui-outlier-view` (U20) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · **Infrastructure Design ✓ SKIPPED (logged)** · **Code Generation ⏳** (the LAST stage for U20 — Part-1-plan-then-Part-2-generate, its own approval gate; no code until the plan is reviewed).

**Register (unchanged)**: 23-unit decomposition intact (17 P1 done + 6 P2; U18 COMPLETE, **U20 through 4 of 5 stages**; 4 P2 remain beyond U20: memo-extensions/observability/llm-judge/deploy-config); WIRE-1 PINNED (+WIRE1-Fold-4 additive amendment) and not touched further; composition-root deviation CLOSED, its Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN; R2–R5 still unwired (core demo path not runnable end-to-end); tier-B still UNAUTHORIZED (N/A here — a UI unit never touches the corpus); audit_store Docker-guard gap still DEFERRED.

**Guardrails held**: NO code; no `frontend/src/outlierView/` (re-verified absent on disk); no infra artifact created; WIRE-1 not touched further; `outlier-model` (U18, frozen) not touched (read-only re-read of `schemas.py` to reconfirm the wire↔Python match; reached only via R4, never imported); `ui-shell`/`ui-memo-view`/`ui-history` + all 17 frozen P1 units untouched; U20's own FD/NFR-Requirements/NFR-Design artifacts re-read but NOT re-opened or edited; the closed composition root untouched; tier-B NOT authorized; audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. **STOPPED** at the Infrastructure Design 2-option completion gate (1. Request Changes / 2. Continue → Code Generation).

## 🧩 BUILD → `ui-outlier-view` (U20) — Infrastructure Design SKIP APPROVED (Continue); Code Generation Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-17

**Infrastructure Design SKIP APPROVED 2026-07-17 (option 2, Continue → Code Generation)** → `ui-outlier-view` advanced to the per-unit **Code Generation** stage (**the LAST stage for U20**); wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/ui-outlier-view-code-gen-plan.md`. **NO code generated; NO file under `frontend/src/outlierView/` created; no shared-config edit made.**

**Grounded by reading the REALIZED substrate on disk** (mirrored, never imported; re-opening no frozen artifact): `frontend/src/memoView/` + `frontend/src/history/` (the layout + `testids.js`/`refNotOwn.js` precedents), `frontend/eslint.config.js` (six per-unit blocks), `frontend/eslint-rules/index.js` + the five per-unit rule modules, `frontend/vitest.config.js`, `frontend/package.json`, `backend/outlier_model/feature_fields.py` (read-only).

**Baseline MEASURED, not assumed**: `npx vitest run` → **524 passed / 117 files, all green** (the previously-recorded 486/114 predated the `src/app` composition-root pass). `frontend/src/outlierView/` confirmed **ABSENT**. Coverage thresholds (v8, 90/90/90/90) + the ONE `FORBIDDEN_TERMS` (`['DECLINE','decision','approved','declined']`) + the **real** detector `findForbiddenSystemOutput` (`/decline(?!-?recommend)/i` **substring** + `\bdecision\b`/`\bapproved\b`) all read off disk.

**Plan contents**: §1 measured baseline · §2 component→module map (C-OUTV-1..6 → files under `frontend/src/outlierView/`, mirroring the realized `memoView`/`history` layout), **§2.1 the four MANDATORY header comments pinned as explicit non-optional Code-Gen deliverables, each asserted by a dedicated test** (documentation only, NOT enforcement), **§2.2 the only three shared-file edits — all additive, precedented ×6** (`eslint.config.js` new `src/outlierView/**` block reusing the shell lints + new `eslint-rules/outlierView.js`; `vitest.config.js` include + coverage.include — **thresholds UNCHANGED, all seven existing gates stand**) · §3 the full TDD test→target map (all thirteen `NFR-OUTV-*` at their pinned tiers; **load-bearing pair at full/highest rigor** — STATE-1's field-derived teeth [both null-causes] + failure-first ordering teeth asserted **both ways**; NOVERDICT-1's import-absence scan + self-test as the primary robust half + rendered `queryBy*`-null over the enumerated set, **exact matching, never a substring sweep**; no orphan) · §4 the 9-step leaf-first build order · §5 HOLDS restated · §6 the coverage gate (additive; no regression vs 524/117; QA-6 ≥90% targeting per-file 100% per the `src/history` precedent) · §7 **EIGHT `[Answer]` questions, all BLANK** · §8 the gate.

**THREE of the eight questions are genuine on-disk findings — not improvised, not resolvable without the user**:
- **Q1 (testid regex family)** — the six prior units split into **two incompatible families**: `queue`/`history` use `+` (≥2 segments after prefix); `memoView`/`approvalGate` use `*` (permits a 2-segment id — `memo-confidence` is real, in use). **The frozen FD §6 inventory has THREE two-segment ids — `outlier-view`, `outlier-score`, `outlier-isoutlier` — which the `+` family would REJECT.** Rec (A) the `*` family, so the frozen FD generates verbatim with no artifact re-opened.
- **Q2 (dynamic flag-row testid)** — `outlier-flag-<feature>` interpolates the wire feature string; the nine real U18 values are **snake_case** (`age_years_derived`, `dti_ratio`, …) → a naive literal emits `outlier-flag-age_years_derived`, **violating the kebab convention**, and the lint sees **literal** attributes only (a template literal is invisible to it). Exactly what the realized `history/testids.js` `slugSegment` solved. Rec (A) an `outlierView/testids.js` slug builder + a self-test over all nine real names.
- **Q3 (feature-name rendering)** — the frozen FD copy inventory has **no** feature-label map, so the raw wire string would render. Rec (A) raw verbatim (faithful-renderer; no new copy key; no FD re-opening).

The other five: **Q4** fixture construction (rec A — four named builders incl. the **Phase-1-ready-null** field-derived fixture + `makeFailingTransport`) · **Q5** sentinels (rec A — the D-OUTV-4/Fold-D pin verbatim) · **Q6** the `outlier_model_version` footnote — **the single-realization decision D-OUTV-5 deferred to Code-Gen** (rec A OMIT) · **Q7** `FLAG_DIRECTION_LABELS` wording **verified against the real imported detector** (rec A "Above/Below the typical range") · **Q8** test-file layout (rec A mirror the sibling state/transition split).

**`ui-outlier-view` (U20) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · **Code Generation ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = §4 Steps 0–8 on explicit go). **This is the LAST stage for the 2nd Phase-2 unit.**

**Register (unchanged)**: 23-unit decomposition intact (17 P1 done + 6 P2; U18 COMPLETE, **U20 at its last stage**; 4 P2 remain beyond U20: memo-extensions/observability/llm-judge/deploy-config); WIRE-1 PINNED (+WIRE1-Fold-4) and not touched further; composition-root deviation CLOSED, its Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN; R2–R5 still unwired (R4 still a `501` stub); tier-B still UNAUTHORIZED; audit_store Docker-guard gap still DEFERRED.

**Guardrails held**: NO code; no `frontend/src/outlierView/` created; **no shared-config edit made** (the `eslint.config.js` / `eslint-rules/outlierView.js` / `vitest.config.js` edits are PLANNED, additive-only); FD + NFR-Requirements + NFR-Design re-opened none; WIRE-1 not touched further (R4 consumed by shape only); `outlier-model` (U18, frozen) not touched (read-only re-read of `feature_fields.py`; reached only via R4, never imported); `ui-shell`/`ui-memo-view`/`ui-queue`/`ui-approval-gate`/`ui-override-form`/`ui-history` + all 17 frozen P1 units untouched (conventions **mirrored by reading**, never imported, never edited); the closed composition root untouched; tier-B NOT authorized; audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. The frontend test run was read-only. **STOPPED** at the plan-file gate.

## 🧩 BUILD → `ui-outlier-view` (U20) — Code Generation Part 2 GENERATED (Q1–Q8 all A + ambiguity-check CLEAN [4 folds]); 682/137 zero-regression; `src/outlierView` 100%; STOP at the Code-Gen 2-option gate — 2026-07-17

**Ambiguity-check RUN against the eight filled answers → CLEAN (four folds, no surface-and-stop)**:
- **CG-OUTV-Fold-1 (LOAD-BEARING)** — the four MANDATORY Fold-1 header comments deliberately **name** the tokens the scans hunt (`recommendation`/`confidence`/`provenance`/`seed`/`corpus_version`/"no request-body builder"), so a **raw**-text scan would flag the very prose that makes each guarantee self-evident. **Resolved by the frozen precedent** (`ui-approval-gate` → `ui-history` `refNotOwn.js` `stripComments`): every scan runs over **comment-stripped** source — the guarantee is the absence of **code**, not of the words. `noVerdictImport.test.js` proves the strip is load-bearing (raw source **has** the words; stripped source lacks the code).
- **CG-OUTV-Fold-2** — Q6-A leaves FD §5's `modelVersionFootnoteLabel` + §6's `outlier-provenance-modelversion` **unrealized**; both were explicitly **conditional**, so omitting **realizes** the FD faithfully rather than contradicting it.
- **CG-OUTV-Fold-3** — the Q3-A/Q2-A asymmetry is intentional: the row **displays** the raw wire string (`dti_ratio`), its testid is **slugged** (`outlier-flag-dti-ratio`). Documented in both modules.
- **CG-OUTV-Fold-4** — Q7-A verified against the **real** label values on disk: `CONFIDENCE_LABELS` **are** `High`/`Medium`/`Low`, so a bare High/Low label would have **collided exactly** — tripping `no-inline-label` AND false-failing the NOVERDICT-1 teeth. `copy.test.js` proves the trap is real and that our labels dodge it.

**Part 2 GENERATED — TDD tests-first, leaf-first (§4 Steps 0–8 all `[x]`)**: **9 production files** under `frontend/src/outlierView/` (`fetchSeam.js` · `copy.js` · `testids.js` · `components/OutlierScoreRegion.jsx` · `components/FlaggedFeaturesRegion.jsx` · `components/OutlierStateView.jsx` · `OutlierView.jsx` + exported `deriveOutlierState`/`OUTLIER_STATE`) + **13 test/harness files** (20 test files / 158 tests). **All four mandatory header comments present and ASSERTED** by `headerComments.test.js` (documentation only, never enforcement). **Three additive shared-config edits ONLY** (no frozen `src/` tree touched): NEW `eslint-rules/outlierView.js` (the Q1-A `*` family) · `eslint.config.js` +1 block reusing the shell lints · `vitest.config.js` +include/+coverage — **thresholds UNCHANGED**.

**GATES — all measured**: frontend **682 passed / 137 files** vs the measured baseline **524 / 117** ⇒ **+158 tests / +20 files, ZERO regression, purely additive**. **`src/outlierView` 100% statements / branches / functions / lines on EVERY file** (QA-6 ≥90% cleared; matches the `src/history` precedent). Project `All files` 100/99.79/100/100 — the 99.79 branch is the **pre-existing** `overrideForm/OverrideFormView.jsx:67` at its frozen baseline, untouched. **ESLint clean (exit 0)**. **Backend mtime-verified UNTOUCHED, not re-run** (newest `.py` = 11:01:01, predating this session; stays 1011 passed / 31 skipped / 5 pre-existing Docker-absence errors).

**Load-bearing pair proven with real teeth**: **STATE-1** — `NOT_AVAILABLE` for **both** null-causes (incl. the Phase-1 `ready`+`outlier:null` fixture proving **field**-derivation, not `status`); a failure ⇒ `ERROR` with `outlier-state-notavailable` **asserted absent**, both failure modes; `deriveOutlierState` exported + tested as a **pure function** so the branch **order** is directly assertable (every payload incl. null-outlier ⇒ `ERROR` when rejected, with the **mirror-image** test proving the same payload *does* yield `NOT_AVAILABLE` when resolved — non-vacuous). **NOVERDICT-1** — import-absence scan (primary robust half) + no verdict/provenance identifier in production **code** + rendered `queryBy*`-null over the **enumerated** set (imported from `shell/copy`, **exact** matching, never a substring sweep); both regions additionally rendered **with verdict/provenance props forced on them** and shown to render neither.

**Two self-corrections during generation (reported, not silent)**: (1) `@testing-library/user-event` is **NOT** a devDependency — my first Retry test would have violated the no-new-dependency hold; corrected to `fireEvent`, the frozen sibling convention. (2) `headerComments.test.js` failed 2/158 because **my matcher** was naive about line-wrapped prose — the **source was correct**; I fixed the **test** (normalize the comment block) and added a wrap-tolerance self-test. **No source was weakened to make a test pass.**

**Deltas from the plan — supersets, not shortfalls**: +`headerComments.test.js`; `noSiblingImport.test.js` consolidates the planned four per-sibling scans into one parameterized file covering **all six** sibling trees.

**`ui-outlier-view` (U20) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · **Code Generation ✓ Part 2 GENERATED + TESTED → STOPPED at the Code-Generation 2-option completion gate**. **This was the LAST stage for U20; the per-unit loop for the 2nd Phase-2 unit is complete pending gate approval.**

**Register (unchanged)**: 23-unit decomposition intact (17 P1 done + 6 P2; U18 COMPLETE, **U20 through all 5 stages pending gate**; 4 P2 remain: memo-extensions/observability/llm-judge/deploy-config); WIRE-1 PINNED (+WIRE1-Fold-4) and not touched further; composition-root deviation CLOSED, its Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN; **R2–R5 still unwired** (R4 still a `501` stub — the core demo path is still not runnable end-to-end); tier-B still UNAUTHORIZED; audit_store Docker-guard gap still DEFERRED.

**Guardrails held**: `ui-shell` (frozen) untouched — imported/composed only, nothing promoted into it; `outlier-model` (U18, frozen) **never imported** — reached only `(orchestrated)` via R4, its nine feature names mirrored **by value** in a test constant; **no backend file touched**; all sibling UI units untouched (mirrored, never imported — asserted over all six trees); **no local `FORBIDDEN_TERMS`** (the ONE shell source, asserted `===` identical); WIRE-1 consumed **by shape only**, not touched further; no LLM; no TypeScript; **no new dependency**; tier-B N/A + NOT authorized; the 17 frozen P1 units + the closed composition root untouched; audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. Artifacts: `guide-docs/build/ui-outlier-view/code/code-summary.md`; `testresults.txt` refreshed; the plan re-saved with the eight answers + §7.9 folds + Steps 0–8 `[x]`.

## ✅ UNIT COMPLETE — `ui-outlier-view` (U20, C5, Phase 2) — approved as delivered 2026-07-17

**CLOSED, approved as delivered** — the per-unit BUILD loop for `ui-outlier-view` is complete (all five stages: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · **Infrastructure Design SKIPPED-logged ✓** · Code-Gen ✓). **The 19th complete build-loop unit overall and the SECOND of the 6 Phase-2 units (U18–U23).** Frontend **682 passed / 137 files** (524/117 baseline + **158** new / +20 files, **zero regression**, purely additive); **`src/outlierView` 100% statements/branches/functions/lines on EVERY file** (QA-6 ≥90% cleared with full teeth); project-wide gate held — `All files` 100/99.79/100/100, the 99.79 branch being the **pre-existing** `overrideForm/OverrideFormView.jsx:67` at its frozen baseline; **ESLint clean (exit 0)**; **backend mtime-verified UNTOUCHED and not re-run** (stays 1011 passed / 31 skipped, the 5 pre-existing Docker-absence errors unchanged).

**The two verification facts worth carrying forward**:
1. **CG-OUTV-Fold-1 — the correct REAPPLICATION of a frozen precedent to a genuine NEW instance of the same tension.** The four MANDATORY Fold-1 header comments deliberately **name** the exact tokens the NOVERDICT-1 / PROV-1 / SCOPE-1 / VIEWONLY-1 scans hunt (`recommendation`, `seed`, `corpus_version`, "no request-body builder"), which would force a false choice between the mandatory documentation and the mandatory scans. The `ui-approval-gate` → `ui-history` `stripComments` precedent resolves it: every scan runs over **comment-stripped** source — **the guarantee is the absence of CODE, not of the words** — mirrored, never imported, and `noVerdictImport.test.js` proves the strip is load-bearing (raw source **has** the words; stripped source lacks the code).
2. **The paired positive/negative teeth on the exported pure `deriveOutlierState`** are the concrete verification of the field-derived, failure-first state invariant: **the SAME null-outlier payload is proven to yield `ERROR` under rejection AND `NOT_AVAILABLE` under resolution.** The test therefore discriminates on **fetch outcome**, not on payload shape — so `NOT_AVAILABLE` is unwritable from a failure path **by branch order**, not by assertion.

**Register (unchanged)**: 23-unit decomposition intact (17 P1 + 6 P2 = 23; **U18 + U20 COMPLETE**, 2 of 6 P2 done, **4 P2 remain**: U19 `memo-extensions` · U21 `observability` · U22 `llm-judge` · U23 `deploy-config`); WIRE-1 pinned/untouched (+WIRE1-Fold-4); composition-root deviation CLOSED but its **Q1-B READ_AUDIT-vs-WIRE-1 "authenticated" divergence still OPEN**; **R2–R5 still unwired — R4 remains a `501` stub, the core underwriting demo path is still not runnable end-to-end (explicitly UNCHANGED by this unit — U20 is a display consumer that fetches a mocked R4 in tests)**; **tier-B corpus run still UNAUTHORIZED** (and confirmed **N/A to every UI unit** — a UI unit never touches the corpus); **audit_store Docker-guard hygiene gap still DEFERRED** (non-blocking).

**Guardrails held**: only `frontend/src/outlierView/` created + the three additive shared-config edits (`eslint-rules/outlierView.js` NEW, `eslint.config.js` +1 block, `vitest.config.js` +include/+coverage, thresholds UNCHANGED); **no frozen `src/` tree touched** (verified on disk); WIRE-1 untouched; `outlier-model` (U18) untouched and never imported (reached only `(orchestrated)` via R4; its nine feature names mirrored **by value** in a test constant); all 17 frozen P1 units + every frozen sibling UI unit untouched; the closed composition root untouched; tier-B NOT authorized; audit_store Docker-guard gap untouched; **no next unit started; nothing else touched.** **STOPPED — the next-move decision is the user's.**

## 🧩 BUILD → `memo-extensions` (U19, C4, **Phase 2** — the 3rd P2 unit attempted) — FD Part 1 (Plan) WRITTEN with a **BLOCKING scope finding**; STOP at plan-file gate — 2026-07-17

**FIRST touch of U19 — DISCOVER-carryover CLEAN** (verified on disk: no `guide-docs/build/memo-extensions/`, no plan, no `backend/memo_extensions/`). **Depth VERIFIED comprehensive** — `unit-of-work.md:245` verbatim: *"Depth: comprehensive (MCP boundary, provider adapters)"*; U19 is **not** in the lighter-candidate list at `:259–263`. Checked by reading the line, not by pattern-matching the phase.

**F4 resolution CONFIRMED still frozen** (checked, not assumed): `unit-of-work.md:69–71` places `providers/` as a **MODULE** of memo-agent-core — *"not a unit"* — and `extensions/` as the **UNIT** carrying `mcp_tools.py`/`borderline_router.py`/`provider_secondary.py`/`provider_showcase.py`; `:17–18` restates *"`provider-abstraction` is a **module of `memo-agent-core`**, not a unit."* **The F4 grouping stands.**

**⚠️ BLOCKING FINDING — the outlier-in-prose premise is NOT in U19's frozen scope.** Four independent frozen sources: **(1)** U19's module list (`:238–241`) = mcp-tools / borderline-router / provider_secondary / provider_showcase — **no outlier-citation module**; **(2)** U19's three stories (`stories.md:331–372`) = US-MEMO-5 (MCP + provider adapters) / US-MEMO-6 (borderline routing) / US-MEMO-7 (secondary+showcase providers) — **none mentions prose citation of outlier data**; **(3)** U19's dependency edges (`unit-of-work-dependency.md:48`) = `memo-agent-core`, `rules-engine` R, `audit-store` R — **NO `outlier-model` edge** (while `:49`/`:50`/`:51` all name outlier/memo-extensions edges explicitly, so the omission is not an oversight pattern); **(4)** the **ONE** real outlier↔U19 link is **FR-MEMO-6/7 — a DETERMINISTIC ROUTING TRIGGER, not prose** (*"Both triggers are deterministic"*; *"until it lands, routing runs on rule-proximity alone"*). **In U19's frozen scope the outlier value decides a routing MODE; the LLM never sees it.** U18's landing now enables that half — that is the genuine in-scope U18→U19 consequence.

**"Memo narrative cites outlier flags" is currently assigned to NO unit.** It is a real brief-level capability (`PROJECT-BRIEF §3 C4`; `services.md:84` *"API->>MEMO: draft profile + rule_report + outlier_result"*) that fell between: **U4** is frozen/complete, built before U18 existed — `MemoAgentInput` has **no outlier field**, **zero** outlier references, and `rule_report` is its *"sole grounding source"* (`domain-entities.md:119`); **U19** doesn't name it; **U20** renders it in React, not prose. `services.md:81` shows the deferral was **deliberate** (*"Phase 1 omits the OUT calls and drafts from rule_report"*) — but no unit was ever assigned the job of closing it. **It cannot be quietly absorbed**: handing `outlier_result` to the LLM requires a field on the frozen, `extra="forbid"` `MemoAgentInput` owned by U4 — **which the standing do-not-touch-U4 hold forbids**. The premise collides with the user's own guardrail, so it is the user's decision.

**Also recorded (read, not re-derived)**: `ProviderAbstraction.complete(prompt, schema)` carries **no temperature parameter** (TEMP0-1 — `temperature=0` fixed **centrally inside each adapter**, never caller-controlled); `route_borderline(*args, **kwargs) -> ThinkingMode` is the frozen Phase-2 seam and is **untyped**, pinning no answer to how the outlier value arrives; `MemoDraftOutput` carries no recommendation/confidence (CON-BR2-TYPE). **Crucially: U4's frozen precedent already holds BOTH candidate enforcement shapes** — `prompt_builder.py` enforces advisory vocabulary by **prompt instruction only**, `citation_validator.py` enforces citation integrity by **post-generation validation**. The prompt-vs-gate question is a choice between two **existing** project patterns, not an invention.

**SEVEN `[Answer]` questions, all BLANK**: **Q1 [BLOCKING]** outlier-in-prose in scope at all (rec **A — no**, proceed at the frozen scope + log the gap separately; **B** would violate the do-not-touch-U4 hold and needs explicit lifting) · **Q2** how the outlier flag reaches `route_borderline` given no frozen edge + an untyped seam (rec **A — handed in**, matching `services.md:84` + the frozen matrix) — **stands regardless of Q1** · **Q3** provider adapters in this pass (rec **A — in scope**; F4 grouped them and the story map assigns US-MEMO-5/6/7 as a set) · **Q4/Q5/Q6 [CONDITIONAL on Q1=B]** prose enforcement surface / zero-unexplained-flags citation discipline / output-contract addition · **Q7** the MCP supplementary-only guard (rec **A** — the handed report stays the SOLE citable grounding source).

**`memo-extensions` (U19) stage status**: **FD ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 on explicit go) · NFR Requirements ⏳ · NFR Design ⏳ · Infrastructure Design ⏳ · Code Generation ⏳. **The 3rd of 6 Phase-2 units attempted; 4 P2 units remain overall.**

**Guardrails held**: NO FD artifact; `guide-docs/build/memo-extensions/` NOT created; no code; no `backend/memo_extensions/`; WIRE-1 not touched; `outlier-model` (U18) + `ui-outlier-view` (U20) not touched (read-only re-reads); `memo-agent-core` (U4) + all 17 frozen P1 units not touched (read-only re-reads of `provider.py`/`schemas.py`/`prompt_builder.py`/`citation_validator.py`); the closed composition root not touched; tier-B NOT authorized; audit_store Docker-guard gap untouched; no other unit started; 23-unit decomposition unchanged. **STOPPED** at the FD plan-file gate.

## 🧩 BUILD → `memo-extensions` (U19, C4, **Phase 2**) — FD Part 1 ANSWERED (Q1/Q2/Q3/Q7=A · Q4/Q5/Q6=N/A) + ambiguity-check CLEAN (5 folds) + **Part 2 GENERATED** (3 artifacts, comprehensive); STOP at the FD 2-option gate — 2026-07-17

**The BLOCKING Q1 scope finding was ACCEPTED and RESOLVED = A.** The original framing (outlier-in-prose as self-evidently in U19's scope) was **incorrect**. **U19 proceeds at its FROZEN scope** — three module groups: `mcp-tools` + `borderline-router` + provider adapters. **In U19 the outlier value decides a routing MODE; the LLM never sees it.** The genuine U18→U19 consequence is that FR-MEMO-7's **outlier-driven half of the borderline trigger** can finally be **enabled** — routing, not narration.

**⚑ NEW NAMED REGISTER ENTRY — `OUTLIER-IN-PROSE` — OPENED 2026-07-17** (plan §4.3). **Not folded into U19; not silently dropped** — carried as its **own named open item**, exactly like the composition-root's **Q1-B READ_AUDIT-vs-WIRE-1 divergence**. **Status: OPEN, unassigned to any unit.** Future options, all deliberate and none pre-judged: **(a)** a new unit · **(b)** a U4 amendment considered **on its own merits** with the hold explicitly lifted · **(c)** Phase 3. **The four proving sources are cited verbatim in the entry so no future reader must re-derive the finding**: (1) **module list** `unit-of-work.md:238–241` — no outlier-citation module; (2) **stories** `stories.md:331–372` — US-MEMO-5/6/7, none mentions prose citation of outlier data; (3) **dependency edges** `unit-of-work-dependency.md:48` — `memo-agent-core` + `rules-engine` `R` + `audit-store` `R`, **NO `outlier-model` edge**, while `:49`/`:50`/`:51` **do** name outlier edges explicitly (so the omission is not an oversight pattern); (4) **FR-MEMO-6/7** `requirements.md:122–123` — *"Both triggers are deterministic"* / *"until it lands, routing runs on rule-proximity alone"* — a **routing trigger, not prose**. Plus **why it cannot be quietly absorbed**: it needs a field on the **frozen `extra="forbid"` `MemoAgentInput`** owned by **U4**, under a standing do-not-touch hold. **`services.md:81` proves the deferral was deliberate** (*"Phase 1 omits the OUT calls and drafts from `rule_report`"*) — **but no unit was ever assigned the job of closing it.**

**Answers embedded per the standing convention**: **Q1/Q2/Q3/Q7 = A**; **Q4/Q5/Q6 = N/A**, each explicitly noted as *"correctly rendered INAPPLICABLE by the Q1=A resolution"*, deliberately left unanswered with **no placeholder content embedded and none carried into the FD**, and each recorded as **travelling with the `OUTLIER-IN-PROSE` entry**.

**MANDATORY AMBIGUITY-CHECK RUN → CLEAN (5 folds; no surface-and-stop).** Every fold resolves against a **frozen artifact, a frozen TEST, or an established precedent** — **none by improvisation**:
- **FD-MEXT-Fold-1 (LOAD-BEARING)** — `ThinkingMode` **cannot ride `complete()`**: the frozen `test_provider.py::test_complete_has_no_temperature_parameter` asserts the signature **exactly** (`params == ["self","prompt","schema"]`), and U4 cannot be amended. **Resolved by the frozen `CitationValidator` precedent in this unit's own parent** (*"supplied at **construction** … so the frozen signature is preserved unchanged"*) → adapters take the mode **at construction**. **Extends to Gemini (the PRIMARY) without touching U4**: `LLMClient` is an **injected** seam and `provider.py` already states the real client *"is wrapped … **at composition time** (a deploy-config/secrets concern)"* — a thinking-configured client is just **another `LLMClient` implementation**, so FR-PROV-5's **"Gemini thinking budget"** is reached **by injection**, **U19 adds no Gemini module** (none is in its frozen module list), and the config binding lands **exactly where U4 already frozen-deferred the real client**. The mapping is **offline-testable** via a capturing double (TEMP0-1 part i precedent).
- **FD-MEXT-Fold-2 (LOAD-BEARING)** — the frozen P1 test literally named `test_only_gemini_adapter_is_present_no_claude_ollama_mcp` asserts *"no Claude, no Ollama, no MCP"* — **which is U19's entire job to add**. **VERIFIED both frozen tests stay green**: it scans `dir(provider_module)` = **U4's namespace only**, so U19's adapters under `backend/memo_extensions/` keep it true **forever** — it is precisely what **forbids** adding them to U4's file; and `test_route_borderline_is_a_not_wired_stub` requires U4's stub to **keep raising `NotImplementedError`**, so U19 does **not** wire it but owns the **real** router at `extensions/borderline_router.py` — **the exact file the frozen layout `:70–71` names for U19**. **The frozen test-suite is the ENFORCEMENT mechanism for the F4 architecture, not an obstacle.**
- **FD-MEXT-Fold-3** — the frozen C4 contract **`component-methods.md:73` DOES type** the trigger `(RuleResultReport, OutlierResult?) -> ThinkingMode` (the plan had called the seam *untyped* — true only of the **Python stub**). This **corroborates Q2=A**: the **handed-in, nullable** shape is **frozen, not merely inferred**, and the **`?` IS FR-MEMO-7's degradation**. The *typed-as-`OutlierResult`* vs *imports-no-outlier-model* tension resolves via the **U20 precedent** (*"never imported, mirrored by value"*): a **U19-local structural Protocol** `OutlierSignal = {is_outlier, outlier_score}` satisfies the frozen contract **by shape** — no edge, no import.
- **FD-MEXT-Fold-4** — MCP enrichment vs the **frozen `PromptBuilder`** (scoped to `MemoAgentInput` only; *"no tool fetch / no MCP re-derives what fired"*) vs US-MEMO-5's *"grounded in live tools rather than memorised content"*. **Reconciled by the more-specific frozen resolution `services.md:46`** (*"supplementary human-readable rule descriptions only"*): live-tools governs the **descriptions**; the **citable set** stays the handed report. Realized by **composition, not modification**. **Q7-A thereby gains STRUCTURAL TEETH from the frozen gate**: `CitationValidator` is constructed with the handed report and requires **report-membership**, so an MCP-described-but-**not-evaluated** rulebook id is **rejected** as `citation_failure`. **The retrieval-miss guard is enforced by construction, not by instruction — the frozen gate unchanged.**
- **FD-MEXT-Fold-5** — `decisions-tools` (reading the decisions DB via the `audit-store` `R` edge) could **reintroduce demographics that the frozen `prompt_builder.py` DELIBERATELY excluded** (*"bias-free by design; the memo prose never sees them"*), violating CON-BR1/FR-OUT-3/skill #6. **Not a user decision** — a hard constraint admits only the compliant path: MCP surfaces are **demographic-free by construction** (**BR-MEXT-9**, with a checkable swap test). **Surfaced rather than silently handled.**

**PART 2 GENERATED — the 3-artifact FD set at comprehensive depth** (mirroring every P1 comprehensive unit, component-methods folded into `domain-entities.md`) at **`guide-docs/build/memo-extensions/functional-design/`**:
- **`domain-entities.md`** — the four module surfaces under `backend/memo_extensions/` (**the exact files the frozen layout names**); the **U19-local `OutlierSignal`** structural Protocol; the two MCP tool surfaces; the **construction-time** thinking mechanism incl. how **Gemini reaches its budget without touching U4**; consumed frozen shapes **by shape**. **U19 adds NO new type** — the strongest possible contract-stability result.
- **`business-rules.md`** — **BR-MEXT-1..13**, each with grounding + **checkable teeth** + full traceability. **No orphan**: every U19 invariant from `:243–244` lands. **Load-bearing**: BR-MEXT-1 (deterministic, LLM-free routing) · BR-MEXT-6 (the handed report is the **sole citable source**) · BR-MEXT-11 (**extend-don't-modify**, enforced by frozen tests). **BR-MEXT-13 is an explicit NEGATIVE rule** so Code-Gen **cannot drift into the registered gap**.
- **`business-logic-model.md`** — the **route → construct → enrich → draft → validate** lifecycle; determinism / groundedness / scope-line arguments; dependency map; FD↔later boundary; invariant self-check. **VALIDATED Mermaid** (`flowchart TD`, **15 nodes / 16 edges**): all-alphanumeric IDs, all labels quoted, **no hyphens/semicolons/colons/parentheses/special characters**, balanced fence, **rectangle-only** per this project's convention — **plus the mandatory text alternative**.

**`memo-extensions` (U19) stage status**: **FD ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the FD 2-option completion gate** · NFR Requirements ⏳ · NFR Design ⏳ · Infrastructure Design ⏳ · Code Generation ⏳. **The 3rd of 6 Phase-2 units; FD is the 1st of its 5 stages.**

**Register (UPDATED — one NEW entry)**: 23-unit decomposition intact (**17 P1 done + 6 P2**; **U18 + U20 COMPLETE**, **U19 at its 1st stage**; 3 P2 remain beyond U19: `observability` / `llm-judge` / `deploy-config`); **⚑ NEW — `OUTLIER-IN-PROSE` OPEN** (unassigned; opened by this pass's Q1=A; four proving sources cited in plan §4.3); WIRE-1 **PINNED** (+WIRE1-Fold-4) and not touched; composition-root deviation CLOSED, its **Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN**; **R2–R5 still unwired** (R4 still a `501` stub — the core demo path still not runnable end-to-end); **tier-B still UNAUTHORIZED**; **`audit_store` Docker-guard gap still DEFERRED**.

**Guardrails held**: **NO code**; **`backend/memo_extensions/` NOT created**; **`memo-agent-core` (U4) + all 17 frozen P1 units NOT touched** — read-only re-reads of `provider.py` / `schemas.py` / `prompt_builder.py` / `citation_validator.py` / `tests/test_provider.py` (the test file **read-only, not run, not modified**); **`outlier-model` (U18) NOT touched and NOT imported** (read-only re-read of `schemas.py`; reached only as a **handed-in structural signal**); **`ui-outlier-view` (U20) NOT touched**; **WIRE-1 NOT touched**; the **closed composition root NOT touched**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap NOT touched**; **no other unit started**; the **23-unit decomposition unchanged**; **no frozen artifact re-opened or re-derived**. **Only 4 files written**: the plan (answers + §4.3 register entry + §5.8 folds + gate checkboxes) and the 3 new FD artifacts. **STOPPED** at the FD 2-option completion gate (1. Request Changes / 2. Continue → NFR Requirements).

## 🧩 BUILD → `memo-extensions` (U19) — **FD APPROVED (Continue)** → NFR Requirements Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-17

**FD APPROVED 2026-07-17 (option 2, Continue → NFR Requirements)** — `memo-extensions` FD **COMPLETE** (3 artifacts frozen: `domain-entities.md` + `business-rules.md` **BR-MEXT-1..13** + `business-logic-model.md`). The FD 2-option gate is **closed**. U19 advanced to **NFR Requirements** — **the 2nd of its 5 stages**. Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/memo-extensions-nfr-requirements-plan.md`. **NO NFR artifact; no code; `backend/memo_extensions/` NOT created.**

**Depth: comprehensive** (consistent with the FD depth decision). **Built ON the frozen FD, re-opening none.**

**Tier convention VERIFIED on disk, not assumed**: **tier-U** = fast/deterministic/CI with **no live LLM call, no key, no network, no Docker, no live MCP server** — grounded in U4's frozen `test_provider.py` header **verbatim** (*"No test constructs a real Gemini client, reads a key, or touches the network"*) + the **TEMP0-1 part i** capturing-double precedent + the **mandatory detector-self-test** convention (CG-NFR-OUT-Fold-3). **tier-B is N/A to U19** (it never touches the corpus) **and NOT authorized**. The `audit-store` `R` edge is exercised through the **`decisions-tools` seam** → **no live Docker/DB**, so the Docker-guard gap stays **out of U19's path and untouched**.

**§2.5 draft target map — all 13 BR-MEXT rules mapped, NO ORPHAN**: 1→**ROUTE-1** *(load-bearing: purity teeth + zero-LLM/provider/network AST scan w/ detector self-test + REFER/proximity trigger teeth + explicit `<=` vs `<` boundary teeth + constants parameterized off the named constant per the NFR-OUT-THRESHOLD-1/Q3-A precedent)* · 2→**SIGNAL-1** *(U19-local fake by shape drives every routing test — **no U18 import in tests either**; interop self-test constructing a real U18 `OutlierResult` **BY VALUE, not by import**; None-degrades teeth)* · 3→**AGNOSTIC-1** · 4→**THINK-1** *(the frozen `params == ["self","prompt","schema"]` assertion applied to **each** new adapter + offline capturing-double proof that EXTENDED constructs a thinking-configured request and STANDARD does not)* · 5→**TEMP0-1** *(capturing-double pattern extended to **Claude and Ollama**, **both** modes)* · 6→**GROUND-1** *(load-bearing: the direct retrieval-miss test — a rule in the `Rulebook` but **ABSENT from the handed report**, i.e. exactly what MCP can describe → `citation_failure` from the **frozen, unmodified** validator)* · 7→**MCPRO-1** · 8→**MISS-1** · 9→**BIAS-1** · 10→**PROVGATE-1** *(Ollama **is** unit-tested offline; temp0 + CON-BR2-TYPE hold for it; its promptfoo absence recorded as a **governance/tooling-config fact of U22, NOT a code test** — per the user's direction)* · 11→**FROZEN-1** *(load-bearing; mechanization is Q1)* · 12→**CONTRACT-1** · 13→**SCOPE-1** *(zero `flagged_features`/`shap_value`/`provenance` refs under `backend/memo_extensions/` + mandatory detector self-test so it cannot pass vacuously)*. Plus **PERF-1** (soft/observed, no hard SLO — the uniform prior-unit posture) and **SEC-1** (governance).

**FOUR `[Answer]` questions, all BLANK** — the user's three plus **ONE genuine on-disk finding**:
- **Q1 (frozen-test regression guard mechanization)** — the named tension resolves on a distinction: importing U4's **TEST file** is an unprecedented cross-unit test dependency (brittle to a U4 test rename; double-collected by pytest), but importing U4's **PRODUCTION module** is **U19's own frozen edge** — and **both assertions are re-makeable from the production symbols alone**. Rec **(A) mirror locally against U4's production module** (the U18 *"mirrored — never imported"* / U20 *"never imported, mirrored by value"* precedent). **(C) stated honestly**: the full backend suite (**1011 passed / 31 skipped**) **already runs both tests**, so (A) is strictly a **duplicate signal** — its value is a cheap, local, self-documenting executable assertion at the unit boundary.
- **Q2 (MCP test-double strategy)** — pinned a design nuance: U19 owns the **server side**, so there are **two separable layers** — the **tool-handler functions** (pure; testable with **no protocol at all**, and **where every BR-MEXT-6/7/8/9 tooth actually lives**) and the **protocol transport**. Rec **(A) injected/fake transport + handlers tested directly**, mirroring `LLMClient` exactly, real protocol wiring deferred to composition/deploy-config **exactly where U4 already frozen-deferred the real google-genai client**.
- **Q3 (swap-test scope)** — surfaced a **real asymmetry in the frozen FD** that decides it: **`decisions-tools`** reads committed decision records about other applicants — **the only surface carrying applicant-derived data, so the only place a demographic can leak (real teeth)**; **`rulebook-tools`** (`describe_rules(rule_ids)`) **never takes an applicant**, so a swap test against it has **nothing to swap and would pass VACUOUSLY** — exactly the false confidence the detector-self-test convention exists to prevent. Rec **(A) asymmetric**: full swap teeth on `decisions-tools`; a **stronger by-construction** assertion on `rulebook-tools` (takes no applicant input ⇒ **cannot** leak) + the shared scan over both.
- **⚑ Q4 [GENUINE ON-DISK FINDING — not user-named]** — **VERIFIED this session**: `requirements.txt` floors **`anthropic>=0.40.0`** + **`ollama>=0.3.0`** (**installed**: anthropic 0.116.0, ollama 0.6.2, langchain-anthropic 1.4.8) ⇒ **US-MEMO-7's two adapters need NO new dependency** — **BUT `grep -in "mcp" requirements.txt` returns NO match and `import mcp` is NOT INSTALLED** ⇒ **US-MEMO-5's MCP half has no floored library**. Suggestive frozen detail: U4's frozen test asserts `"mcp" not in _top_level_imports(provider_module)` — **the name was anticipated but no package was ever floored**. **U20 held a hard no-new-dependency line; U18's tech-stack-decisions closes with "No new dependencies" — U19 would be the FIRST unit to break that streak**, deserving a deliberate decision rather than arriving by import. **Entangled with Q2**: under Q2-A the **handlers need no MCP library at all**. Rec **(A)** defer the protocol/SDK to composition/deploy-config (no new dep) · **(B)** floor an MCP SDK now · **(C)** flag as a decomposition/tech-stack gap and STOP (FR-MEMO-5 + PROJECT-BRIEF §9 promise MCP **servers** as a real deliverable).

**`memo-extensions` (U19) stage status**: **FD ✓ COMPLETE (approved 2026-07-17)** · **NFR Requirements ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = `nfr-requirements.md` + `tech-stack-decisions.md` on explicit go) · NFR Design ⏳ · Infrastructure Design ⏳ · Code Generation ⏳. **The 3rd of 6 Phase-2 units; 2 of 5 stages engaged.**

**Register (unchanged by this pass)**: 23-unit decomposition intact (**17 P1 done + 6 P2**; U18 + U20 COMPLETE; **U19 at its 2nd stage**; 3 P2 remain beyond U19: `observability` / `llm-judge` / `deploy-config`); **`OUTLIER-IN-PROSE` still OPEN** (unassigned; opened 2026-07-17 by the FD's Q1=A; **held out of scope by BR-MEXT-13 / NFR-MEXT-SCOPE-1**); WIRE-1 **PINNED** (+WIRE1-Fold-4) and not touched; composition-root deviation CLOSED, its **Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN**; **R2–R5 still unwired** (R4 still a `501` stub); **tier-B still UNAUTHORIZED** (**N/A to U19**); **`audit_store` Docker-guard gap still DEFERRED** (and **out of U19's test path** by the `decisions-tools` seam). **⚑ NEW open tech-stack question**: the **missing MCP dependency floor** (Q4) — asked, **not** answered by action.

**Guardrails held**: **NO NFR artifact** (`guide-docs/build/memo-extensions/nfr-requirements/` NOT created); **no code**; **no `backend/memo_extensions/`**; the **frozen FD re-opened none** (read-only); **WIRE-1 untouched**; **`outlier-model` (U18) + `ui-outlier-view` (U20) untouched**; **`memo-agent-core` (U4) + all 17 frozen P1 units untouched** (read-only re-reads only; **`test_provider.py` read-only — not run, not modified**); the **closed composition root untouched**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**; **`requirements.txt` read-only — NOT edited** (the Q4 dependency question is **asked, not resolved by action**). **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q4 before the ambiguity-check and Part 2.

## 🧩 BUILD → `memo-extensions` (U19) — NFR Requirements Part 1 ANSWERED (Q1–Q4 all A) + ambiguity-check CLEAN (4 folds) + **`MCP-TRANSPORT-DEFERRED` opened** + **Part 2 GENERATED** (2 artifacts); STOP at the NFR-Requirements 2-option gate — 2026-07-17

**Q1–Q4 all A, embedded in the plan** per the standing convention (full question text retained): **Q1** mirror the two frozen-U4 facts locally, importing **only U4's production module** (no test-file import, no double-collection, no coupling to U4's test names) · **Q2** injected/fake MCP transport, **handlers tested directly**, no live MCP server at tier-U · **Q3** asymmetric swap teeth (`decisions-tools` real teeth; `rulebook-tools` **by construction** — it takes no applicant input) · **Q4** **defer the MCP protocol/SDK; no new dependency**.

**MANDATORY AMBIGUITY-CHECK RUN → CLEAN (4 folds; no surface-and-stop)** — each resolves against a **frozen artifact or an established precedent**, none improvised. **Two folds STRENGTHEN the answers rather than merely accepting them; two pin mechanization that would otherwise have been improvised at Code-Gen:**
- **NFR-MEXT-Fold-1 — Q1-A is STRICTLY STRONGER than option C's "duplicate signal" framing** (my own earlier framing was **incomplete**): `test_only_gemini_adapter_is_present_no_claude_ollama_mcp` inspects **`dir(provider_module)`** — a **live namespace**, evaluated in whatever **import state** the session is in. U4's test module imports **only U4**, and under pytest's default collection order (`memo_agent_core` **before** `memo_extensions`) U19 may **not yet be imported** when it runs — so a **module-level namespace pollution originating in U19** (an accidental import-time monkeypatch) **would ESCAPE U4's own test**. U19's mirror runs where U19's adapters **are** imported ⇒ it **catches it**. **Not a duplicate — strictly stronger in the one context that matters.**
- **NFR-MEXT-Fold-2 — what "server" does BR-MEXT-7's read-only scan attach to, given Q4-A defers the transport?** At this stage *"server"* = the **tool-handler surface** (`mcp_tools.py`) — **which is where a write could actually be written** — so the read-only invariant is verified at **FULL strength with no protocol present**; a deferred transport **cannot introduce a write the handlers do not expose**. Same shape as U4's own `LLMClient` deferral. The **deliverable-language consequence is registered, not absorbed**.
- **NFR-MEXT-Fold-3 — SHARPENS Q3-A**: the swap teeth attach to the **OUTPUT PROJECTION**, not the caller. `decisions-tools` reads **stored** committed decision records about **other applicants**, so the demographics live in **the data it returns**, not in the request. Teeth = **seed the fake record source with records differing ONLY in demographics → assert the returned projection is byte-identical** (directly proving the projection **drops** them). The **input** side is covered by the **same by-construction argument** Q3-A applies to `rulebook-tools`. **Both halves non-vacuous; neither needs a decision.**
- **NFR-MEXT-Fold-4 — "U4 is unmodified" must be verified BEHAVIORALLY, not by a file-hash/mtime pin.** My own §2.5 draft said *"no file under `backend/memo_agent_core/` is modified"* **without pinning the mechanism**. A hash/mtime pin would be **wrong**: mtime is meaningless across a git checkout, and a hash pin would **false-fail the day U4 is legitimately amended** (e.g. if **`OUTLIER-IN-PROSE`** is ever resolved toward a U4 amendment **with the hold explicitly lifted**) — **turning a guard into an obstacle**. **No prior unit did this**; session-level mtime checks are a **reviewer/agent** discipline, **never a test**. FROZEN-1 therefore verifies via **(i)** the two **behavioral** mirror assertions + **(ii)** an **import-discipline scan** — failing loudly on a **real** violation, staying green through a **deliberate** one.

**⚑ NEW NAMED REGISTER ENTRY — `MCP-TRANSPORT-DEFERRED` — OPENED 2026-07-17** (plan §3.6 + `tech-stack-decisions.md` §3) — logged **exactly like `OUTLIER-IN-PROSE`**. **Status: OPEN**, deferred to **composition / deploy-config (U23)**. **Six evidence rows cited verbatim** so no future reader must re-derive it: **(1)** `grep -in "mcp" requirements.txt` → **NO match**; **(2)** `import mcp` → **NOT INSTALLED**, while **anthropic 0.116.0 / ollama 0.6.2 / langchain-anthropic 1.4.8 ARE** installed (**provider breadth needs nothing new — only the MCP half lacked a floor**); **(3)** U4's frozen test asserts `"mcp" not in _top_level_imports(provider_module)` — **the name was ANTICIPATED but no package was ever FLOORED**; **(4)** the **composition-deferral precedent** (frozen `provider.py`: the real client *"is wrapped to this minimal `LLMClient` seam **at composition time** (a deploy-config/secrets concern)"*) — U19's deferral is the **same shape, not a new pattern**; **(5)** the **no-new-dependency streak** U18 (*"No new dependencies"*) and U20 both held — **U19 would be the FIRST to break it**; **(6)** the **deliverable language protected** (PROJECT-BRIEF §3 C4 + §9; FR-MEMO-5; US-MEMO-5). **Explicit scope**: **DELIVERED** = the two read-only tool-handler surfaces + an injected transport seam with a fake; **NOT delivered** = the **live MCP protocol binding**; **⚠️ NON-BLOCKING — no U19 invariant depends on the transport** (BR-MEXT-6/7/8/9 each **fully verified at tier-U with no MCP package present**, because **every one of those teeth lives in the handler layer** — where a write or a leak could actually be written). **What IS outstanding is the deliverable itself — so *"two MCP servers"* is NOT to be read as fully done at this stage. That is precisely why it is a named register item and not a footnote.**

**PART 2 GENERATED — 2 artifacts** at `guide-docs/build/memo-extensions/nfr-requirements/`:
- **`nfr-requirements.md`** — the **fifteen finalized `NFR-MEXT-*` targets** (Q1–Q4 + Folds 1–4 folded in), each a **pass/fail assertion + acceptance + tier + rigor**. **Load-bearing pair called out explicitly**: **ROUTE-1** (purity teeth · zero-LLM/provider/network AST scan **+ detector self-test** · REFER/proximity/cutoff trigger teeth · **explicit `<=` vs `<` boundary teeth** · constants **parameterized off the named constant**, never a hardcoded number) and **FROZEN-1** (the Q1-A mirrored **behavioral** guard · import-discipline scan · Fold-1's strictly-stronger rationale · Fold-4's no-hash-pin rationale · **zero regression on the 1011/31 baseline**). **GROUND-1 also called out**: the **direct retrieval-miss test** — a rule **in** the `Rulebook` but **ABSENT from the handed report** → **`citation_failure`** from the **frozen, unmodified** validator (**structural, not prompt-based**). Full **traceability table, NO orphan** (BR-MEXT-1..13 → 13 targets + PERF-1 soft/observed + SEC-1 governance), story coverage (US-MEMO-5/6/7), and the **full Security-Guardrails compliance table** (11 controls) — **prompt-injection assessed honestly as inherited-and-not-widened** (even a hostile supplement **cannot** produce a citation [report-membership] **or** alter a recommendation [unrepresentable]); read-only DB · bias-free · reproducibility · advisory-only · explainability all **Compliant**; **deliverable transparency Compliant via the register item**. **No blocking finding.**
- **`tech-stack-decisions.md`** — **MEXT-D1..D12**. **NO NEW DEPENDENCY — the streak holds** (verification table: anthropic / langchain-anthropic / ollama all **floored AND installed**; MCP **neither**). **`requirements.txt` NOT edited.** **`MCP-TRANSPORT-DEFERRED` recorded in full** (§3) with its six evidence rows + explicit non-blocking scope. The **injected-double substrate pinned for BOTH `LLMClient` AND the MCP transport seam** (D6/D10), extending U4's frozen *"no network, no key"* discipline to **Claude + Ollama + MCP**. **D5** records how **Gemini (the PRIMARY)** reaches its **thinking budget by injection** without touching U4.

**`memo-extensions` (U19) stage status**: **FD ✓ COMPLETE** · **NFR Requirements ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the NFR-Requirements 2-option completion gate** · NFR Design ⏳ · Infrastructure Design ⏳ · Code Generation ⏳. **The 3rd of 6 Phase-2 units; 2 of 5 stages complete pending gate.**

**Register (UPDATED — one NEW entry; U19 has now opened TWO)**: 23-unit decomposition intact (**17 P1 done + 6 P2**; U18 + U20 COMPLETE; **U19 at its 2nd stage**; 3 P2 remain beyond U19: `observability` / `llm-judge` / `deploy-config`); **`OUTLIER-IN-PROSE` OPEN** (unassigned; opened by the FD's Q1=A; **held out of scope by BR-MEXT-13 / NFR-MEXT-SCOPE-1** with a mandatory detector self-test so the scan cannot pass vacuously); **⚑ NEW — `MCP-TRANSPORT-DEFERRED` OPEN** (deferred to composition/deploy-config U23; **explicitly NON-BLOCKING** for U19's invariants; six evidence rows cited); WIRE-1 **PINNED** (+WIRE1-Fold-4) and not touched; composition-root deviation CLOSED, its **Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN**; **R2–R5 still unwired** (R4 still a `501` stub); **tier-B still UNAUTHORIZED** (**N/A to U19**); **`audit_store` Docker-guard gap still DEFERRED** (and **out of U19's test path** by the `decisions-tools` seam).

**Guardrails held**: **NO code**; **`backend/memo_extensions/` NOT created**; **`requirements.txt` NOT edited** (verified — its only diff is the **pre-existing** `testcontainers` + `hypothesis` modification dated **2026-07-06**, present at session start); the **frozen FD re-opened none**; **WIRE-1 untouched**; **`outlier-model` (U18) + `ui-outlier-view` (U20) untouched**; **`memo-agent-core` (U4) + all 17 frozen P1 units untouched** (`test_provider.py` **read-only — not run, not modified**); the **closed composition root untouched**; **tier-B NOT authorized** (and N/A); the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (answers + §3.5 folds + §3.6 register entry + checkboxes) + the **2 new NFR artifacts**. **STOPPED** at the NFR Requirements 2-option completion gate (1. Request Changes / 2. Continue → NFR Design).

## 🧩 BUILD → `memo-extensions` (U19) — **NFR Requirements APPROVED (Continue)** → NFR Design Part 1 (Plan) WRITTEN **with a premise correction (§0)**; STOP at plan-file gate — 2026-07-17

**NFR Requirements APPROVED 2026-07-17 (option 2, Continue → NFR Design)** — U19's NFR Requirements **COMPLETE** (2 artifacts frozen: `nfr-requirements.md` **fifteen NFR-MEXT-\*** + `tech-stack-decisions.md` **MEXT-D1..D12**). Gate **closed**. U19 advanced to **NFR Design — the 3rd of its 5 stages**. Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/memo-extensions-nfr-design-plan.md`. **NO NFR-Design artifact; no code.**

**⚠️ §0 — A PREMISE IN THE BRIEF WAS CORRECTED BEFORE IT COULD PROPAGATE INTO A PATTERN NAME** (verified on disk; two parts, the second **material**):
1. **`ReadOnlySeamPattern` is NOT `outlier-model`'s — it is `ui-history`'s (U9, §P3), a FRONTEND unit.** U18's actual patterns are **P-OUT-1..9** (AllowlistProjection · SeedLocalDeterminism · ImputeThresholdComposition · SoleExplainerConstruction · ScoreFlagExplainComposition · DualSourceSeam · VersionAnchoredProvenance · StructuralGuard · ReferencedObservedBoundary) — **none is named `ReadOnlySeamPattern`**. **A pattern will not be cited by a name the artifact does not carry.**
2. **MATERIAL — the mechanism the brief describes ("no import exists to call, not just a scan proving none was called") DOES NOT EXIST for Python imports, NOT EVEN IN U18.** `ui-history`'s pattern works because a **JS module's exported surface** can omit a write builder. **U18's own "no LLM / no write / no DB" guarantee is `P-OUT-8 StructuralGuardPattern` — i.e. A SCAN**, precisely what the brief contrasts against. **Python cannot make an import structurally impossible**; no type, signature or module structure forecloses `import anything`.
**Consequence, stated honestly rather than papered over**: Python affords by-construction for **data** (a typed projection with no field for the forbidden thing — P-OUT-1) and for **surface** (what a class/module exposes), but **NONE for imports**. The router's **signature** genuinely makes a provider **un-injectable** (no client parameter exists to pass one); *"no LLM **import** exists to call"* can only be a **scan**. **Q1 therefore asks WHICH scan**, offering a **strictly stronger** form than U18's denylist: an **import ALLOW-LIST**, mirroring the project's real allow-list lineage (`ALLOWED_INPUT_FIELDS` / `OUTLIER_FEATURE_FIELDS`).

**§3 Pattern map — ELEVEN patterns `P-MEXT-1..11`, all fifteen targets covered, NO ORPHAN**: **P-MEXT-1 PureFunctionRoutingPattern** *(load-bearing — signature-level: no client/provider param exists ⇒ a provider is structurally **un-injectable**; import-level: **scan-only per §0**, Q1 decides)* · **P-MEXT-2 MirroredBoundaryAssertionPattern** *(load-bearing — the **exact** production-only import + the **two** re-asserted behaviors; Fold-1 strictly-stronger; Fold-4 behavioral-not-hash-pin)* · **P-MEXT-3 SoleCitationGatePattern + AppendOnlyPromptComposition** *(the frozen validator as the **single** gate, unmodified; U4's `build()` output **never parsed/edited/reordered/re-templated — only appended to**; Q3 decides the owner)* · **P-MEXT-4 ConstructionTimeInjectionPattern** *(exact constructors; `complete(self, prompt, schema)` **exactly 3 params** ⇒ TEMP0-1 part ii **by signature**; AGNOSTIC-1 **signature-level**)* · **P-MEXT-5 MinimalSurfaceProtocolPattern** *(the Protocol's **own narrowness IS the guard** — `signal.flagged_features` is an attribute that **does not exist on the declared type**: a **type error, not a lint finding**; the U18 `FeatureInputs` mechanism applied to the router's input)* · **P-MEXT-6 AsymmetricDemographicFreedomPattern** *(rulebook-tools: **no applicant-shaped parameter exists** ⇒ by construction, **strictly stronger than a swap test that could not fail**; decisions-tools: frozen `PrecedentSummary` with **no** demographic field + the **output-projection** swap teeth per Fold-3)* · **P-MEXT-7 ReadOnlyHandlerSurfacePattern** *(the closest **TRUE** analog to ui-history's pattern — and it **does** work here because it is about a **class surface**, not an import; per Fold-2 the handler surface **is** the "server")* · **P-MEXT-8 NonFatalDegradationPattern** *(**honestly test-only** — control flow; no type or signature can encode it; **not dressed up as structural**)* · **P-MEXT-9 NoNewContractPattern** · **P-MEXT-10 StructuralGuardPattern** *(one substrate, **eight** scans, each with a mandatory detector self-test)* · **P-MEXT-11 ReferencedObservedBoundaryPattern** *(PROVGATE/PERF/SEC — not over-specified)*.

**§4 Components `C-MEXT-1..6`** with **exact signatures**: `BorderlineRouter` (+ the `OutlierSignal` Protocol) · **`McpToolService` SPLIT into its two handler surfaces per Q2-A** — **`RulebookTools`** (`describe_rules(rule_ids)` — **no applicant param**) + **`DecisionsTools`** (`recent_precedent(query) -> list[PrecedentSummary]`, frozen summary **with no demographic field**) · `ClaudeAdapter` · `OllamaAdapter` · `StructuralGuard` substrate. The **`McpTransport`** seam is an injected Protocol with a fake; its real binding stays **`MCP-TRANSPORT-DEFERRED`**. **§4.2 reference-not-own keeps the FOUR categories distinct as instructed**: consumed-by-import (**U19's own frozen edges** `memo_agent_core` / `rules_engine` / `audit_store`) · **NOT-imported-reached-by-shape** (`outlier-model` via `OutlierSignal`) · **MIRRORED-not-imported** (U4's two test facts) · **DEFERRED-to-composition** (the MCP transport; the real `LLMClient` wrapping + Gemini thinking budget). **§4.3 component→target coverage, no orphan.** **§4.4** plans the validated Mermaid with **both** requested guarantees as **visible blocked edges** (the U18 `DEMO -.blocked.-> FI` convention): `llm provider client -.blocked.-> BorderlineRouter` and `write or commit path -.blocked.-> both handler surfaces`.

**THREE `[Answer]` questions, all BLANK**: **Q1** the router's import discipline — **import ALLOW-LIST** (rec **A**: fails on **ANY** unforeseen import incl. a **transitively-reached** LLM; mirrors the project's real allow-list lineage) vs **U18's denylist shape** vs both · **Q2** `OutlierSignal` **`@runtime_checkable` + isinstance-in-TESTS-only** (rec **A** — mirrors U4's **own frozen** `@runtime_checkable class ProviderAbstraction(Protocol)` + `isinstance(fake, ProviderAbstraction)` precedent **exactly**; production stays duck-typed, adding **no unrequested runtime gate**) vs a production isinstance guard vs plain Protocol + hand-rolled `hasattr` · **⚑ Q3 [GENUINELY OPEN — the FD does not settle it]** **which component owns the prompt append + the non-citable marker**: rec **A** `McpToolService` owns `supplementary_block()` / `compose_prompt(base, context)` **inside the frozen `mcp_tools.py`** (**no fifth module**; keeps the marker where **GROUND-1(c) is directly testable**; matches the FD's own placement of `supplementary_context(...)`) vs **B** the orchestrator composes (**then GROUND-1(c) is NOT verifiable inside U19 at all**, and the marker becomes **unowned** until the **CLOSED** composition root is reopened) vs **C** a fifth module (**not named by the frozen layout `unit-of-work.md:70–71`** — the exact drift class the FD's Q1 discipline exists to prevent).

**`memo-extensions` (U19) stage status**: **FD ✓ COMPLETE** · **NFR Requirements ✓ COMPLETE (approved 2026-07-17)** · **NFR Design ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = `nfr-design-patterns.md` + `logical-components.md` on explicit go) · Infrastructure Design ⏳ · Code Generation ⏳. **The 3rd of 6 Phase-2 units; 3 of 5 stages engaged.**

**Register (unchanged by this pass; U19 has opened TWO items to date)**: 23-unit decomposition intact (**17 P1 done + 6 P2**; U18 + U20 COMPLETE; **U19 at its 3rd stage**; 3 P2 remain beyond U19: `observability` / `llm-judge` / `deploy-config`); **`OUTLIER-IN-PROSE` OPEN** (unassigned; **held out of scope** by BR-MEXT-13 / NFR-MEXT-SCOPE-1 / **P-MEXT-5**, whose Protocol narrowness makes the prose-bearing fields **structurally unreachable**); **`MCP-TRANSPORT-DEFERRED` OPEN** (deferred to composition/deploy-config U23; **explicitly NON-BLOCKING**); WIRE-1 **PINNED** (+WIRE1-Fold-4) and not touched; composition-root deviation CLOSED, its **Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN**; **R2–R5 still unwired** (R4 still a `501` stub); **tier-B still UNAUTHORIZED** (**N/A to U19**); **`audit_store` Docker-guard gap still DEFERRED** (out of U19's test path).

**Guardrails held**: **NO NFR-Design artifact** (`guide-docs/build/memo-extensions/nfr-design/` NOT created); **no code**; **no `backend/memo_extensions/`**; **`requirements.txt` NOT edited**; the **frozen FD + approved NFR Requirements re-opened none** (read-only); **WIRE-1 untouched**; **`outlier-model` (U18) + `ui-outlier-view` (U20) untouched**; **`memo-agent-core` (U4) + all 17 frozen P1 units untouched**; the **closed composition root untouched**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q3 before the ambiguity-check and Part 2.

## 🧩 BUILD → `memo-extensions` (U19) — NFR Design Part 1 ANSWERED (Q1–Q3 all A) + ambiguity-check CLEAN (3 folds, incl. the **user-flagged** `compose_prompt`-vs-BR-MEXT-7 check) + **Part 2 GENERATED** (2 artifacts); STOP at the NFR-Design 2-option gate — 2026-07-17

**Q1–Q3 all A, embedded in the plan** (full question text retained), **and §0's premise correction RETAINED as the PERMANENT record** at the user's explicit instruction — it is now the documented reason **P-MEXT-1 is NOT named `ReadOnlySeamPattern`**, **P-MEXT-7 is the only pattern here legitimately carrying a ui-history-style surface argument**, and **P-MEXT-8 is openly test-only**.

**TWO MECHANICAL CLAIMS VERIFIED ON THE REAL INTERPRETER BEFORE THE CHECK** (`python 3.12.10`, **not assumed**): **(1) Q2-A** — `isinstance(fake, OutlierSignal)` → `True`; `isinstance(not_a_signal, OutlierSignal)` → `False` (**discriminating, not vacuous**); a **frozen Pydantic model built BY VALUE** in the U18 `OutlierResult` shape → **`True`** ⇒ **SIGNAL-1(b)'s interop self-test is directly expressible** on the pinned runtime. **(2) Q3-A** — after `composed = base + marker + block`, `base` is **unchanged** and `composed is not base` → **`True`** ⇒ **`str` immutability is a real structural property, not a hope.**

**MANDATORY AMBIGUITY-CHECK RUN → CLEAN (3 folds; no surface-and-stop)**:
- **NFR-ND-MEXT-Fold-1 — [USER-FLAGGED: does `compose_prompt` weaken BR-MEXT-7?] → genuinely distinct; P-MEXT-7 NOT weakened; and P-MEXT-3 gets STRONGER.** Answered **precisely, not by assurance**: **(1)** BR-MEXT-7/SEC-4's own acceptance criteria name the hazard (*"neither server exposes a **write/mutate/commit** method"*; *"no `DecisionCommitService` / write-transport / session-write import"*), rooted in **skill #2** + **SEC-4** ⇒ **the guarded object is the SYSTEM'S STATE**. **(2)** `compose_prompt` is a **pure function returning a new `str`** — persists nothing, touches no transport/DB/session/record, mutates no argument, no side effect; nothing it returns can become state (the adapter it feeds is itself read-only w.r.t. the decision record by **CON-BR2-TYPE**). **(3)** A **"write" in the SEC-4 sense** = *a mutation of persistent state through a write surface*; a pure string transformation shares **NONE** of those properties and **cannot be a step toward a commit because there is no state for it to reach** — exactly why P-MEXT-7's real mechanism (no `commit*`/`write*`/`persist*`/`update*` member; no write-transport import) is **untouched**. **(4) The fold STRENGTHENS P-MEXT-3**: `str` immutability means `base + marker + block` **cannot** mutate U4's `build()` output even by accident ⇒ *"U4's builder output is never modified"* holds **by LANGUAGE SEMANTICS** — upgrading P-MEXT-3 from *"we only append"* to ***"modification is unrepresentable"***. **(5) Two anti-drift guards adopted**: (i) the read-only scan's forbidden-member list is **SEMANTIC** (persistence/mutation/transport + write-transport imports), **never word-matching on "output-producing"** — which would false-flag `compose_prompt` **and invite someone to weaken the scan**; (ii) `compose_prompt`/`supplementary_block` are **enumerated as pure non-persisting members** in the header **and asserted side-effect-free** ⇒ purity **tested, not assumed**. **(6) One real non-blocking consequence DISCLOSED**: Q3-A gives `McpToolService` **two responsibilities** (read-only source + composer) — a **cohesion** note, **not** a read-only violation; the frozen four-module layout leaves **no fifth module**, so Q3-A is the **only** option keeping **GROUND-1(c) testable** without amending the decomposition.
- **NFR-ND-MEXT-Fold-2** — Q3-A keeps `mcp_tools.py` **free of a `prompt_builder` import**: `compose_prompt` takes the base as a **`str` parameter**, so the orchestrator calls `build()` and hands the string in ⇒ **U19 never touches U4's builder even by import**; consistent with Q2-A's handed-in philosophy + U18's *"orchestration is downstream"* boundary.
- **NFR-ND-MEXT-Fold-3** — Q1-A's allow-list must admit the router's **type-only** imports **without weakening it**: it is a **small, enumerated, commented set** (`__future__`, `typing`, `enum`/`dataclasses`, `memo_agent_core.schemas` for `ThinkingMode`, `rules_engine.report_schema` possibly `TYPE_CHECKING`-only, U19-local) **and is a SUBSET of FROZEN-1's `backend.* ⊆ {memo_agent_core, rules_engine, audit_store}`** ⇒ the two scans **agree by construction**. **`audit_store` is deliberately ABSENT from the router's allow-list** (it is `decisions-tools`' edge) — the allow-list is **tighter** than the unit rule, which is the point.

**PART 2 GENERATED — 2 artifacts** at `guide-docs/build/memo-extensions/nfr-design/`:
- **`nfr-design-patterns.md`** — **P-MEXT-1..11**, opening with an explicit **"what by-construction can and cannot mean in Python"** scope box (**data / signature / surface / language-semantics — and NONE for imports**). **The load-bearing pair + GROUND-1 documented with ACTUAL mechanisms, not assertions**: **P-MEXT-1** = the real signature (**no client parameter ⇒ a provider is structurally un-injectable**) + **the allow-list CONTENTS as a table** (with `audit_store` deliberately absent) + the synthetic-`import anthropic` self-test; **P-MEXT-2** = the **actual mirrored assertions as code** (the production-only import, `pytest.raises(NotImplementedError)`, the `dir()` scan) + why production-not-test-file + why strictly stronger (collection-order pollution) + why no hash pin; **P-MEXT-3** = the real append code + the **`str`-immutability upgrade**. Validated **module-relationship Mermaid** (rectangle-only, 7 rules, 15 nodes) with **`LLMX -.blocked.-> RTR`** and **`WRX -.blocked.-> RBT/DCT`** as **visible blocked edges** + text alternative. **Traceability, no orphan (15/15).**
- **`logical-components.md`** — **six components with exact signatures**: `BorderlineRouter` (+ the `@runtime_checkable OutlierSignal` whose **narrowness is the guard**) · `RulebookTools` (`describe_rules(rule_ids)` — **no applicant param**) · `DecisionsTools` (**frozen `PrecedentSummary` with no demographic field** + **injected `DecisionRecordSource`** ⇒ no live DB) · **`McpToolService`** (owns `SUPPLEMENT_MARKER` + the **append-only** `compose_prompt`, with the Fold-1 read-only argument + both anti-drift guards + the **disclosed cohesion note**) · `ClaudeAdapter`/`OllamaAdapter` · `StructuralGuard` (**eight scans**; **Scan 1 ⊂ Scan 7 by construction**). **The four-category reference-not-own kept distinct** (consumed-by-import — **noting `prompt_builder` is NOT among them** per Fold-2 · NOT-imported-reached-by-shape · MIRRORED-not-imported · DEFERRED-to-composition). Validated **component-relationship Mermaid** + text alternative. **Component→target coverage, no orphan.** Settled items held.

**`memo-extensions` (U19) stage status**: **FD ✓ COMPLETE** · **NFR Requirements ✓ COMPLETE** · **NFR Design ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the NFR-Design 2-option completion gate** · Infrastructure Design ⏳ · Code Generation ⏳. **The 3rd of 6 Phase-2 units; 3 of 5 stages complete pending gate.**

**Register (unchanged by this pass; U19 has opened TWO items to date)**: 23-unit decomposition intact (**17 P1 done + 6 P2**; U18 + U20 COMPLETE; **U19 at its 3rd stage**; 3 P2 remain beyond U19: `observability` / `llm-judge` / `deploy-config`); **`OUTLIER-IN-PROSE` OPEN** — now held out of scope **structurally** by `OutlierSignal`'s narrowness (**P-MEXT-5**: `signal.flagged_features` is an attribute that **does not exist on the declared type** — a **type error, not a lint finding**) + the SCOPE-1 scan; **`MCP-TRANSPORT-DEFERRED` OPEN** (deferred to composition/deploy-config U23; **explicitly NON-BLOCKING** — every BR-MEXT-6/7/8/9 tooth lives in the **handler layer**); WIRE-1 **PINNED** (+WIRE1-Fold-4) and not touched; composition-root deviation CLOSED, its **Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN**; **R2–R5 still unwired** (R4 still a `501` stub); **tier-B still UNAUTHORIZED** (**N/A to U19**); **`audit_store` Docker-guard gap still DEFERRED** (and **out of U19's test path** via the injected `DecisionRecordSource`).

**Guardrails held**: **NO code**; **`backend/memo_extensions/` NOT created**; **`requirements.txt` NOT edited**; the **frozen FD + approved NFR Requirements re-opened none**; **WIRE-1 untouched**; **`outlier-model` (U18) + `ui-outlier-view` (U20) untouched**; **`memo-agent-core` (U4) + all 17 frozen P1 units untouched** (**the interpreter verification ran only throwaway in-memory objects and imported no project module**); the **closed composition root untouched**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (answers + **§0 retained as permanent record** + §5.5 folds + checkboxes) + the **2 new NFR-Design artifacts**. **STOPPED** at the NFR Design 2-option completion gate (1. Request Changes / 2. Continue → Infrastructure Design).

## 🧩 BUILD → `memo-extensions` (U19) — **NFR Design APPROVED (Continue)** → Infrastructure Design **ASSESSED → SKIPPED (logged, rule-justified)** = the **19th skip** + **3rd Phase-2 skip**; STOP at the Infra 2-option gate; NEXT = Code Generation — 2026-07-17

**NFR Design APPROVED 2026-07-17 (option 2, Continue → Infrastructure Design)** — U19's NFR Design **COMPLETE** (2 artifacts frozen: `nfr-design-patterns.md` **P-MEXT-1..11** + `logical-components.md` **C-MEXT-1..6**). Gate **closed**.

**Infrastructure Design ASSESSED AT THE STAGE (not pre-assumed) → logged SKIP. NO infra artifact created** (`guide-docs/build/memo-extensions/infrastructure-design/` NOT created — consistent with all **eighteen** prior skips).

### ⚠️ The premise that drove this stage's question was FALSE ON DISK — and it INVERTS the provider-count argument
The brief supposed *"`memo-agent-core` (U4) itself **may have had a real Infrastructure Design pass** for its Gemini integration"*. **It did not.** **Verified three ways:**
1. **`ls -d guide-docs/build/*/infrastructure-design`** → **exactly one directory: `database`** — the ONE real non-skip.
2. **`guide-docs/build/memo-agent-core/`** contains only `code` / `functional-design` / `nfr-design` / `nfr-requirements` — **there is NO `infrastructure-design`**.
3. **`guide-state.md:80`** records U4 verbatim: *"`memo-agent-core` Code-Gen APPROVED & COMPLETE 2026-07-06 — the FOURTH fully-complete unit; THE CLUSTER IS CLOSED (FD ✓ · NFR Requirements ✓ · NFR Design ✓ · **Infrastructure Design SKIPPED-logged ✓** · Code-Gen ✓)"*.
**The frozen `provider.py` docstring cites it itself**: the real google-genai client is wrapped to the `LLMClient` seam at composition time *"(a deploy-config/secrets concern, **per the logged Infra SKIP**)"*.

**So the provider-count question resolves in the OPPOSITE direction from the hypothesis, and decisively**: **U4 took LLM provider integration from ZERO → ONE** — the pass where the genuinely new provider-infrastructure decisions live (which SDK, how the client is constructed, where the key comes from, what the seam is) — **and its infra was SKIPPED and logged**, with the real wrapping **deferred to composition/deploy-config**. **U19 goes ONE → THREE through that SAME already-deferred seam**, with **both SDKs already floored AND installed** (anthropic 0.116.0 · ollama 0.6.2) and **no new dependency** (**`MCP-TRANSPORT-DEFERRED`** explicitly keeps it that way). **If introducing the FIRST provider did not warrant an infra pass, adding the 2nd and 3rd through the same seam cannot.** **Provider COUNT is not an infrastructure dimension** — provider *infrastructure* is, and **U4 already skip-assessed it and deferred it to `deploy-config` (U23)**, exactly where the per-provider capability config (**Gemini thinking budget**, Claude extended-thinking flag), keys, and client wrapping land. **U19 extends an existing deferred decision; it does not add a new one.**

### Rule justification (explicit, matching the eighteen prior skips)
**CLAUDE.md** Infrastructure Design *"**Skip IF: No infrastructure changes / Infrastructure already defined**"* **+ `execution-plan.md:200`** — the *Lighter / minimal-footprint* classing whose text names this unit's own component **VERBATIM**: *"pure-logic units (`rules-engine`, `outlier-model`, **`memo-agent` logic**) have **little independent infra**; `admin-cli` has none; `ui-*` is static hosting on Vercel."* **U19 IS `memo-agent` logic (C4) — the frozen decomposition itself classes it.** Mirrors `audit-store`'s logged-skip shape (a service/logic unit with **no independent cloud topology it designs**; persistence topology owned by `database`, deployment topology by `deploy-config`).

### All five assessment points verified against the frozen artifacts on disk
1. **No untrusted parsing / no subprocess sandbox** — U19 parses no document, spawns no process; injection-bearing text is neutralised **upstream** by `document-sanitizer` (SEC-1) **before C4 is reached**, and the frozen `MemoAgentInput` structurally carries **no forensic span** (SEC1-1). Unlike `intake`, **no sandbox NFR exists here**.
2. **No independent persistence it provisions** — the `audit-store` **`R`** edge runs through the **injected `DecisionRecordSource`** seam of `DecisionsTools` (C-MEXT-3), **never a live DB**; U19 **persists nothing** — no schema, no migration, no role-grant. Persistence topology stays **`database`'s** (the ONE real non-skip). This is also **why the `audit_store` Docker-guard gap is out of U19's test path** and stays untouched.
3. **LLM/provider access exists but adds NO new provider-infrastructure decision** — see the inversion above. Both adapters implement U4's **frozen `ProviderAbstraction`** and drive U4's **frozen, injected `LLMClient`**; at tier-U every client is a **capturing double** (*"no network, no key, no CI live call"*). The real wrapping + capability config + keys were **already** deferred by **U4's own logged skip** to composition/deploy-config (U23) and by `secrets-config` (SEC-3). **U19 introduces no key, no endpoint, no service, no topology.**
4. **No deployed service / no new dependency / no route of its own** — a source-level Python package under `backend/memo_extensions/`; **no new dependency** (**`MCP-TRANSPORT-DEFERRED`** keeps the MCP protocol/SDK out; **`requirements.txt` NOT edited**); **no WIRE-1 route implementation** — U19 is **consumed by C4's orchestration**, never wired to a route directly.
5. **(also checked) No new secret / env var / service** — keys come from env/secrets via **`secrets-config`** (`unit-of-work-dependency.md:54`), whose **SEC-3 ownership is that unit's, not U19's**; **no secret is used or read at tier-U**; **no fitted-model artifact** (U18's already-skip-assessed concern) and **no corpus** (tier-B **N/A**).

### The different-calculus question — answered explicitly
U19's **LLM-adapter nature creates NO different calculus** than `outlier-model`'s or `ui-outlier-view`'s — and the reason is **sharper than analogy**. U18's skip turned on *"scores through an owned seam, provisions nothing"*; U20's on *"a display consumer reaching R4 through an injected `fetchSeam`"*; **U19's turns on the same structural fact — it reaches its providers through a seam whose real binding is ALREADY somebody else's logged, deferred concern.** The only candidate difference — **provider count** — is **not an infrastructure dimension**: adding a 2nd and 3rd implementation of an **existing frozen Protocol**, using **already-installed SDKs**, through an **already-deferred wrapping**, is **new application BEHAVIOR, not new INFRASTRUCTURE** — the identical reasoning applied to every prior unit. Payload / caching / rate-limiting / CORS / endpoint config → **`deploy-config` (P2, U23)** or the backend, **not this unit's**. → **SKIP correct, no STOP.**

**The ambiguity-check surfaced NO genuine U19-owned infra concern.** The **ClaudeAdapter/OllamaAdapter provider-count question was assessed head-on** and resolved **against** a skip-blocking finding by **U4's own logged skip** + **`execution-plan.md:200`'s verbatim naming of `memo-agent` logic**. **Nothing improvised; nothing waved through.**

**Skip roster now NINETEEN**: intake · document-sanitizer · rules-engine · memo-agent-core · auth-rbac · audit-store · quality-gates · corpus-generator · secrets-config · admin-cli · ui-shell · ui-queue · ui-memo-view · ui-approval-gate · ui-override-form · ui-history · outlier-model · ui-outlier-view · **memo-extensions** — the **3rd Phase-2 skip**; **`database` remains the ONE real non-skip** (re-verified on disk this session).

**`memo-extensions` (U19) stage status**: FD ✓ · NFR Requirements ✓ · NFR Design ✓ · **Infrastructure Design ✓ SKIPPED (logged)** · **Code Generation ⏳ — the LAST stage for U19** (Part-1-plan-then-Part-2-generate, its own approval gate; **no code until the plan is reviewed**).

**Register (unchanged)**: 23-unit decomposition intact (**17 P1 done + 6 P2**; U18 + U20 COMPLETE; **U19 through 4 of 5 stages**; 3 P2 remain beyond U19: `observability` / `llm-judge` / `deploy-config`); **`OUTLIER-IN-PROSE` OPEN** (held out of scope structurally by P-MEXT-5's Protocol narrowness + the SCOPE-1 scan); **`MCP-TRANSPORT-DEFERRED` OPEN** (non-blocking; and it is **part of why this skip holds** — no MCP dependency/protocol infra to design); WIRE-1 **PINNED** and not touched; composition-root deviation CLOSED, its **Q1-B divergence still OPEN**; **R2–R5 still unwired**; **tier-B still UNAUTHORIZED** (N/A to U19); **`audit_store` Docker-guard gap still DEFERRED** (out of U19's test path).

## 🧩 BUILD → `memo-extensions` (U19) — **Infrastructure Design SKIP APPROVED (Continue)** → Code Generation Part 1 (Plan) WRITTEN; STOP at the plan-file gate — 2026-07-17

**Infrastructure Design SKIP APPROVED 2026-07-17 (option 2, Continue → Code Generation)** — U19 advanced to **Code Generation — the 5th and LAST of its 5 stages**. Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/memo-extensions-code-gen-plan.md`. **NO code; NO `backend/memo_extensions/`; `requirements.txt` NOT edited.**

**Depth: comprehensive.** **Built ON** the frozen FD (**BR-MEXT-1..13** + the four-module inventory + `OutlierSignal` + the MCP boundary + **FD-MEXT-Fold-1..5**) + approved NFR Requirements (**fifteen `NFR-MEXT-*`** + **NFR-MEXT-Fold-1..4** + **`MCP-TRANSPORT-DEFERRED`**) + approved NFR Design (**`P-MEXT-1..11`** + **`C-MEXT-1..6`** + **NFR-ND-MEXT-Fold-1..3** + **§0 the permanent record**) — **re-opening none.** Verified on disk: the three frozen U4 test names FROZEN-1 mirrors (`test_route_borderline_is_a_not_wired_stub:92`, `test_only_gemini_adapter_is_present_no_claude_ollama_mcp:97`, `test_complete_has_no_temperature_parameter:58`) + the `pyproject` coverage convention (`--cov=backend/<unit>` in `addopts`, `--cov-fail-under=90`). Sibling precedent: `outlier-model` (U18) code-gen plan (`backend/<unit>/` + `tests/{fixtures.py, structural.py, test_*.py}`, TDD tests-first / leaf-first).

**Plan contents**: **(§2)** a component→module map onto **EXACTLY the frozen four files** — `borderline_router.py` (BorderlineRouter + the `OutlierSignal` Protocol) · `mcp_tools.py` (**RulebookTools + DecisionsTools + McpToolService**, three components one file) · `provider_secondary.py` (ClaudeAdapter) · `provider_showcase.py` (OllamaAdapter) — **NO fifth module**; the **header-comment deliverable (documentation only, never enforcement)** confirmed **explicit on all six components**. **(§3)** a full TDD test→target map, **15/15 no orphan**, each at its NFR-pinned tier: the **two load-bearing** targets at **full-highest** — **ROUTE-1** (purity/trigger/boundary teeth + constants-parameterized-off-the-named-constant + the router **import ALLOW-LIST** scan with a synthetic-`import anthropic` detector self-test) and **FROZEN-1** (the **two mirrored facts re-asserted locally against U4's PRODUCTION module, NOT importing U4's test file** + the `backend.* ⊆ {memo_agent_core, rules_engine, audit_store}` + no-`memo_agent_core.tests.*` scan) — plus **GROUND-1** (direct retrieval-miss against the **real frozen `CitationValidator`**, append-only via `str` immutability, the non-citable marker), **SIGNAL-1** (by-shape fake + interop-by-value `isinstance` against the `runtime_checkable OutlierSignal` + None-degrades), **THINK-1/AGNOSTIC-1/TEMP0-1** (frozen 3-param signature on both adapters, offline capturing-double for construction-time thinking, `temperature=0` every call both modes), **BIAS-1** (rulebook-tools by-construction + decisions-tools output-projection swap teeth), **MCPRO-1** (SEMANTIC not word-matched read-only scan that correctly does **not** flag `compose_prompt`), **MISS-1**, **CONTRACT-1**, **SCOPE-1** (mandatory detector self-test), **PROVGATE-1**; the **eight-scan `StructuralGuard`** substrate (**Scan 1 ⊂ Scan 7 by construction**). **(§4)** the **leaf-first build order** (OutlierSignal+BorderlineRouter → the frozen-boundary mirror → RulebookTools+DecisionsTools+their read-projection types → McpToolService+`compose_prompt`+marker → Claude+Ollama adapters → remaining scans → coverage gate). **(§5)** explicit HOLDS. **(§6)** the coverage/quality gate at the comprehensive bar (`--cov=backend/memo_extensions`, `--cov-fail-under=90` unchanged, **1011/31 no-regression**, pure additive, U4's frozen suite green **and not double-collected**).

**SIX `[Answer]` questions, all BLANK** (each full text + lettered options): **Q1** the router import allow-list exact enumerated roots (rec **A** — `{__future__, typing, enum, dataclasses, memo_agent_core.schemas, rules_engine.report_schema}` + U19-local; **`audit_store` deliberately absent** so Scan 1 ⊂ Scan 7 holds by construction) · **Q2** injected-double construction in a shared `tests/fixtures.py` (capturing `LLMClient` double; failing/timing-out/empty MCP transport fake; seeded `DecisionRecordSource` with a demographic **swap pair** + a retrieval-miss shape; by-value U18 `OutlierResult`) (rec **A**) · **Q3** test-file organization mirroring `outlier-model`, with the **frozen-boundary mirror in its OWN `test_frozen_boundary.py`** — the only module importing `memo_agent_core.provider` for assertion (rec **A**) · **Q4** realization-deferred strings/constants — `SUPPLEMENT_MARKER` wording, Claude/Ollama model strings, `RULE_PROXIMITY_MARGIN`/`OUTLIER_SCORE_CUTOFF` values — chosen at generation with threshold tests **parameterized OFF the named constant** (CG-OUT-Fold-1 precedent) (rec **A**) · **⚑ Q5 [SURFACED PHRASING TENSION — not improvised]** CONTRACT-1 scan scope: the **authoritative frozen patterns file** scopes scan #6 to **LLM-output / `Recommendation`-producing** models and explicitly carves out the handler-side read projections `PrecedentSummary`/`RuleDescription` (which **`C-MEXT-3` declares as `BaseModel`, `extra="forbid"`**), whereas the plan-file/NFR-Req **looser phrasing** says *"zero `BaseModel` subclasses"* — which taken literally would false-flag the frozen-declared projections; rec **A** adopts the **SEMANTIC role-based** scoping the frozen patterns file already states (with a detector self-test + non-vacuity assertion), rather than the literal phrasing (option **B** would force the projections to non-Pydantic shapes, a larger deviation from the approved NFR-Design surface losing `extra="forbid"`) · **Q6** test framework (`pytest` + `Hypothesis`, **no new dep**) + coverage config (rec **A**).

**`memo-extensions` (U19) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED (logged) · Code Generation ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check runs **AFTER** the answers; Part 2 = the six modules under `backend/memo_extensions/` + their TDD tests, on explicit go). **The 3rd of 6 Phase-2 units; 5 of 5 stages engaged; this is the LAST stage.**

**Register (unchanged by this pass)**: 23-unit decomposition intact (**17 P1 done + 6 P2**; U18 + U20 COMPLETE; **U19 at its 5th/last stage**; 3 P2 remain beyond U19: `observability` / `llm-judge` / `deploy-config`); **`OUTLIER-IN-PROSE` OPEN** (held out of scope structurally by P-MEXT-5 + the SCOPE-1 scan); **`MCP-TRANSPORT-DEFERRED` OPEN** (non-blocking); WIRE-1 **PINNED** and not touched; composition-root deviation CLOSED, its **Q1-B divergence still OPEN**; **R2–R5 still unwired** (R4 still a `501` stub); **tier-B still UNAUTHORIZED** (N/A to U19); **`audit_store` Docker-guard gap still DEFERRED** (out of U19's test path via the injected `DecisionRecordSource`).

**Guardrails held**: **NO code**; **`backend/memo_extensions/` NOT created**; **`requirements.txt` NOT edited**; the **frozen FD + approved NFR Requirements + approved NFR Design re-opened none** (read-only); **WIRE-1 untouched**; **`outlier-model` (U18) + `ui-outlier-view` (U20) untouched**; **`memo-agent-core` (U4) + all 17 frozen P1 units untouched** (read-only re-reads only; `test_provider.py` **grepped read-only** for the three `def` names — **not run, not modified**); the **closed composition root untouched**; **tier-B NOT authorized** (and N/A); the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate — ambiguity-check NOT run yet, Part 2 NOT started.

## 🧩 BUILD → `memo-extensions` (U19) — Code-Gen Q1–Q6 ANSWERED (all A) → ambiguity-check RAN (ONE gap: THINK-1(b) vs the frozen 3-kwarg `LLMClient` seam) → resolved **R2** → **Part 2 GENERATED + TESTED** → STOP at the Code-Gen 2-option gate; **U19 COMPLETE (LAST stage); 3rd Phase-2 unit** — 2026-07-17

**Q1–Q6 all A** (embedded in the plan §7 per the standing convention). **Mandatory ambiguity-check RAN**, grounded in the ACTUAL frozen shapes on disk (`provider.py` / `schemas.py` / `citation_validator.py` / `report_schema.py` / `rulebook_schema.py` / `record_schema.py`) — **five answers clean**, each verified against a frozen shape; the **Q5 semantic-scoping determination CONFIRMED as a legitimate Code-Gen realization** (three grounds; **no NFR-Design amendment** — BIAS-1/P-MEXT-6 load-bearingly *requires* `PrecedentSummary(BaseModel)` with no demographic field, so the literal "zero `BaseModel`" reading was never internally satisfiable).

**⚑ ONE GENUINE GAP surfaced → resolved by user decision (R2):** `NFR-MEXT-THINK-1(b)` needs an adapter built with `thinking_mode=EXTENDED` to produce an **observable** thinking-configured request, but the frozen `memo_agent_core.LLMClient` seam is `generate(*, model, prompt, temperature) -> str` — **no thinking channel** — and `C-MEXT-5` types the constructor `client: LLMClient`. **R2 (user-approved)**: U19's two new adapters drive a **U19-local thinking-aware seam** (`ThinkingLLMClient.generate(*, model, prompt, temperature, thinking)`); the capturing double implements it → THINK-1(b) has **real, non-vacuous, provider-API-faithful** teeth (`EXTENDED→thinking=True`, `STANDARD→False`); the frozen `LLMClient`/Gemini path stays **untouched**; the deviation is scoped to the two new adapters only. R1 rejected (model-string misrepresents real APIs); R3 rejected (vacuous THINK-1(b)). Disclosed in `code-summary.md §3`.

**PART 2 GENERATED — TDD tests-first / leaf-first, §4 Steps 0–9 all `[x]`** — `backend/memo_extensions/`: **4 production modules** (`borderline_router.py` + the `OutlierSignal` Protocol · `mcp_tools.py` = `RulebookTools` + `DecisionsTools` + `McpToolService` + the read projections + `SUPPLEMENT_MARKER` · `provider_secondary.py` = `ClaudeAdapter` + the R2 `ThinkingLLMClient` seam + `_parse_xml` · `provider_showcase.py` = `OllamaAdapter`) + `__init__.py` + **`tests/`** (`structural.py` substrate, `fixtures.py`, **15 `test_*.py` / 85 tests**). `pyproject` gained `--cov=backend/memo_extensions` (no omit); **`requirements.txt` NOT edited**.

**RESULT**: backend **1096 passed / 31 skipped** (1011 baseline + **85** new; the **5 pre-existing `audit_store` Docker-absence errors UNCHANGED** — the deferred Docker-guard gap, untouched) — **zero regression**. `backend/memo_extensions` **100%** statements/branches on **every** file; global **`--cov-fail-under=90` holds at 99.85%**. **U4's frozen suite GREEN and NOT double-collected** — verified via `--collect-only` that `test_route_borderline_is_a_not_wired_stub`, `test_only_gemini_adapter_is_present_no_claude_ollama_mcp`, and `test_complete_has_no_temperature_parameter` are each collected **exactly once** from `memo_agent_core/tests/test_provider.py` (U19's `test_frozen_boundary.py` imports the **production** module, never U4's test file). All **fifteen `NFR-MEXT-*`** tested at pinned tiers; the **eight `StructuralGuard` AST scans** each carry a **detector self-test**; **Scan 1 ⊂ Scan 7 by construction**.

**`memo-extensions` (U19) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED (logged) · Code Generation ✓ (Part 1 answered + ambiguity-check RAN [1 gap, R2-resolved] + Part 2 GENERATED + TESTED) → STOPPED at the Code-Generation 2-option completion gate.** **This was the LAST of U19's 5 stages → the per-unit loop for U19 is COMPLETE pending gate approval. U19 is the 3rd of 6 Phase-2 units complete.**

**Register (UPDATED — U19 complete pending gate)**: 23-unit decomposition intact (**17 P1 done + 6 P2**; **U18 + U20 + (pending-gate) U19 COMPLETE**; **2 P2 remain: `observability` (U21) / `llm-judge` (U22)** + `deploy-config` (U23)); **`OUTLIER-IN-PROSE` OPEN** (held out of scope structurally by `OutlierSignal`'s narrowness + the SCOPE-1 scan — realized in code); **`MCP-TRANSPORT-DEFERRED` OPEN** (non-blocking; realized as the deferred protocol binding — every BR-MEXT-6/7/8/9 tooth verified at tier-U with no MCP package present); WIRE-1 **PINNED** and not touched; composition-root deviation CLOSED, its **Q1-B divergence still OPEN**; **R2–R5 still unwired** (R4 still a `501` stub); **tier-B still UNAUTHORIZED** (N/A to U19); **`audit_store` Docker-guard gap still DEFERRED** (out of U19's test path via the injected `DecisionRecordSource`).

**Guardrails held (verified)**: **`memo-agent-core` (U4) + all 17 frozen P1 units untouched** (production module imported only; `test_provider.py` never imported; frozen `LLMClient`/Gemini seam not modified by R2's U19-local addition); **`outlier-model` (U18) never imported** (reached by shape via `OutlierSignal`; interop `OutlierResult` built by value); **`rules-engine` / `audit-store` read-only via frozen edges**; audit-store via the **injected `DecisionRecordSource`** (no live DB; Docker-guard gap out of path and untouched); **no fifth module** beyond the frozen four; **no new dependency**; **`ui-outlier-view` (U20) / WIRE-1 / closed composition root untouched**; **tier-B NOT authorized** (N/A); **no other unit started**; the **23-unit decomposition unchanged**. Files written: the 4 production modules + `__init__.py` + 17 test/harness files under `backend/memo_extensions/`, `pyproject.toml` (one `--cov` line), `guide-docs/build/memo-extensions/code/code-summary.md`, `testresults.txt`, the plan (answers + §7.1 R2 + Steps [x] + gate), this state entry, and the audit entry. **STOPPED** at the Code-Generation 2-option completion gate (1. Request Changes / 2. Continue to Next Stage).

## ✅ BUILD → `memo-extensions` (U19, C4, Phase 2) COMPLETE — the **TWENTIETH fully-complete unit overall**; the **3rd of 6 Phase-2 units** (after `outlier-model` U18 + `ui-outlier-view` U20) — 2026-07-17

**Code Generation APPROVED 2026-07-17 (option 2, Continue)** → the per-unit BUILD loop for `memo-extensions` is **CLOSED**. **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ SKIPPED-logged · Code-Gen ✓.** Backend **1096 passed / 31 skipped** (1011 baseline + **85** new — **zero regression**; the 5 pre-existing `audit_store` Docker-absence errors unchanged); `backend/memo_extensions` **100%** statements/branches on **every** file; global `--cov-fail-under=90` held at **99.85%**; **U4's frozen suite green and NOT double-collected** (its three FROZEN-1-relevant tests each collected exactly once from `memo_agent_core`).

**Two realization decisions recorded (authoritative):**
- **R2 (THINK-1(b))** — the frozen `memo_agent_core.LLMClient` seam `generate(*, model, prompt, temperature) -> str` had **no thinking channel**; resolved via a **U19-local thinking-aware seam** (`ThinkingLLMClient.generate(*, model, prompt, temperature, thinking)`) that the capturing double implements — **scoped to only the two new adapters**, giving THINK-1(b) real, non-vacuous, provider-API-faithful teeth while **leaving U4's frozen `LLMClient`/Gemini path untouched**. (R1 rejected: model-string misrepresents real APIs; R3 rejected: vacuous THINK-1(b).)
- **CONTRACT-1 semantic scoping (Q5-A)** — scan #6 targets **LLM-output / `Recommendation`-producing** models only, **permitting** the frozen-declared handler read projections `PrecedentSummary`/`RuleDescription`. Confirmed a **legitimate Code-Gen realization of already-consistent NFR-Design intent, NOT an amendment** (BIAS-1/P-MEXT-6 load-bearingly requires `PrecedentSummary(BaseModel)` with no demographic field, so the literal "zero `BaseModel`" reading was never internally satisfiable).

**COMPLETION ROSTER**: **20 of 23 units complete** — **all 17 P1** + **3 P2** (`outlier-model` U18 · `ui-outlier-view` U20 · **`memo-extensions` U19**). **3 P2 units remain: `observability` (U21) · `llm-judge` (U22) · `deploy-config` (U23).** `database` remains the one real Infrastructure-Design non-skip; the memo-extensions Infra SKIP was the **19th** logged skip.

**Deferred Decisions / cross-cutting register (carried, unchanged by this completion)**: the **23-unit decomposition unchanged**; the **composition root's Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN**; **R2–R5 still unwired** (**R4 still a `501` stub** — the core underwriting demo path still **not runnable end-to-end**); **WIRE-1 PINNED**, untouched; **tier-B corpus run still UNAUTHORIZED** and confirmed **N/A to every unit built so far**; the **`audit_store` Docker-guard hygiene gap still DEFERRED** (and stayed out of U19's path via the injected `DecisionRecordSource`); **`OUTLIER-IN-PROSE` still OPEN and unassigned** (held out of scope structurally by U19's `OutlierSignal` narrowness + the SCOPE-1 scan); **`MCP-TRANSPORT-DEFERRED` still OPEN and non-blocking** — **now doubly relevant**: U19 built the read-only handler layer that a real MCP transport would eventually bind at composition/deploy-config; **`testresults.txt` append-vs-overwrite** remains an **open housekeeping** item (refreshed per-unit).

**Guardrails held**: no unit started next; **WIRE-1 · the 17 frozen P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · the closed composition root — UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**. **The next move is the user's decision** — no work started.

## 🧩 BUILD → `observability` (U21, EPIC-6, Phase 2) STARTED → Functional Design Part 1 (Plan) WRITTEN; STOP at the plan-file gate — 2026-07-17

**User picked `observability` (U21)** — the **4th of 6 Phase-2 units** to enter the per-unit loop (U18 + U20 + U19 complete). **FD is the 1st of its stages.** Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/observability-functional-design-plan.md`. **NO FD artifact; no code; `backend/observability/` NOT created.**

**DISCOVER-carryover check**: greenfield P2, no reverse-engineering, **NO prior U21 artifacts** (`backend/observability/` + `guide-docs/build/observability/` both absent). **Frozen substrate re-read on disk (re-derived none)**: **US-PLAT-9** (`stories.md:601`) · **NFR-OBS-1** (Langfuse 100% of agent/tool steps) · **NFR-OBS-2** (Prometheus+Grafana, one dashboard, **~5 metrics**: decision latency · decisions by recommendation type · rule-evaluation duration · LLM-call errors · outlier-flag rate) · **AC-7**; edges (`unit-of-work-dependency.md:50`) = **`memo-agent-core` + `memo-extensions` + `outlier-model`** (*"traces 100% of agent/tool steps"*) + a **`secrets-config` SEC-3** consumer (`:55`).

**⚑ DEPTH — the ACTUAL classification (verified, not assumed)**: `unit-of-work.md:248` = *"comprehensive **at Infrastructure Design** (wiring-heavy)"*; `:262` lists `observability` among the pure-wiring **lighter candidates**. ⇒ **split**: **FD depth = LIGHTER (recommended)**; **comprehensive reserved for Infrastructure Design** — **U21's Infra is expected to be a REAL comprehensive stage** (likely the **2nd real non-skip after `database`**), assessed at that stage, **not pre-committed**.

**⚑ DECISIVE FINDING (verified on disk)**: the **emit-only telemetry architecture is ALREADY BUILT.** Four P1 units (`intake` · `rules_engine` · `audit_store` · `memo_agent_core`) each ship their **own** emit-only `TelemetryEmitter` + a typed **allowlist, demographic-free** event schema, **stack-agnostic**, each docstring **naming `observability` as the wirer** (U4: *"Langfuse 100%-step tracing is wired by `observability` (reference-not-own) via the graph checkpointer"*; `intake`: *"the `observability` unit wires it to Langfuse/Prometheus/Grafana"*). **ASYMMETRY (material)**: the two P2 units U21 depends on — **`outlier_model` (U18) + `memo_extensions` (U19) — have NO `telemetry.py`**; their traceable outcomes (outlier score/flag; `ThinkingMode` routing; `SupplementaryContext.retrieval_ok` MCP hit/miss; provider selection; `CitationValidationResult` pass/fail) exist only as return values / observable state. `ui-outlier-view` (U20) correctly **not** an edge (frontend display, not a traced backend step).

**Plan contents**: the **lighter-FD** depth recommendation; the **emit-only sink/wiring** unit context; the frozen seams referenced (reference-not-own — the four `TelemetryEmitter`s + U4's graph checkpointer + the two P2 step outcomes + `secrets-config` keys); a **PROPOSED module structure** noting the **layout is OPEN** (`unit-of-work.md:86` names `observability/` as a directory but **enumerates no files** — no "frozen four" analog); and **FIVE blank `[Answer]` questions**: **Q1** does U21 instrument frozen units (hold violation) **or** define trace/metric sinks a composition pass wires in (the **composition-root parallel**; rec **A**) · **Q2** Langfuse traces vs Prometheus metrics — **two separate sub-concerns**, distinct mechanisms (rec **A**) · **Q3** tracing vs **zero-live-LLM tier-U** — Code-Gen testable surface = **schema/interface correctness + recording-fake 100%-step proof**, live capture deferred to composition Scope B/C (rec **A**) · **Q4** module layout **OPEN**, no frozen-four constraint (rec **A**) · **⚑ Q5 [added — genuine edge-scope gap]** the ~5 metrics span `rules-engine` + `audit-store` **beyond the three declared edges** → consume events **duck-typed via a stack-agnostic seam** (rec **A**, widens no edge) vs import each event schema (widens edges) vs **flag as a decomposition gap and STOP**.

**`observability` (U21) stage status**: **FD ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = the FD artifact set at lighter depth, on explicit go) · NFR Requirements ⏳ · NFR Design ⏳ · **Infrastructure Design ⏳ (expected REAL/comprehensive — wiring-heavy)** · Code Generation ⏳.

**Register (unchanged by this pass)**: 20 of 23 units complete (17 P1 + U18/U20/U19); **U21 at its 1st stage**; 2 P2 remain beyond U21 (`llm-judge` U22 · `deploy-config` U23); **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN** (non-blocking); composition-root **Q1-B divergence still OPEN**; **R2–R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end); **tier-B UNAUTHORIZED** (N/A); **`audit_store` Docker-guard gap DEFERRED**; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO FD artifact**; **no code**; **no `backend/observability/`**; **no frozen unit edited** (read-only re-reads of the four `telemetry.py` emitters + `stories.md`/`requirements.md`/`unit-of-work*.md` only); **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · the 17 frozen P1 units UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q5.

## 🧩 BUILD → `observability` (U21) — FD Part 1 ANSWERED (Q1–Q5 all A) + ambiguity-check CLEAN (3 folds, grounded in U4's real orchestrator) + **FD Part 2 GENERATED** (3 artifacts, lighter depth); STOP at the FD 2-option gate — 2026-07-17

**Q1–Q5 all A** (embedded in the plan §5). **Mandatory ambiguity-check RAN (§5.5)** grounded in **U4's ACTUAL frozen `orchestrator.py`** (re-read this session) → **CLEAN (3 folds; no surface-and-stop)**. The frozen memo graph has **exactly four nodes** — `draft` · `validate` · `finalize` · `flag` (edges `START→draft→validate→{finalize | draft retry | flag}→END`), a `MemorySaver` checkpointer (the *"100%-step tracing"* hook), and **one** `MemoTelemetryEvent` emitted per `run()`.

**The three user-flagged checks resolved against frozen facts:**
- **FD-OBS-Fold-1 [check i]** — the 100%-coverage recording-fake sequence **IS U4's real node list** (not invented); the **graph-node vs all-agent/tool-step boundary is NAMED**: the checkpointer callback auto-traces graph nodes **by construction**; a **general span API** traces the **non-graph tool steps** (U18 outlier scoring upstream · U19 `route_borderline`/adapter-selection at composition · U19 MCP retrieval, which the frozen `_draft_node` does **not** call — it calls `PromptBuilder.build` directly), applied **at composition**; the **system-wide 100% is AC-7's deploy-time trace audit**. Edits no frozen unit.
- **FD-OBS-Fold-2 [check ii]** — a single occurrence in both planes needs **no new shared concept**: it draws on **two pre-existing frozen streams** (checkpointer node executions + emitter event lists); a memo completion is one span **and** a `MemoTelemetryEvent.recommendation` metric contribution, **without merging** the mechanisms (Q2-B rejected).
- **FD-OBS-Fold-3 [check iii]** — Q5 duck-typed consumption has a **concrete non-vacuity mechanism**: U21 sinks/derivations read **only enumerated allowlist field names by shape**; a **detector self-test** feeds a synthetic event with a forbidden attribute and asserts it is **not read/propagated**, plus a structural scan that no sink reads a non-allowlisted attribute. **Disclosed**: 2 of the 5 metrics (*LLM-call errors*, *outlier-flag rate*) have **no frozen emitter field** → they derive from **step outcomes** at the span-API boundary (composition-wired; tier-U tested against fake step outcomes).

**PART 2 GENERATED — 3 artifacts at LIGHTER depth** (the same 3-artifact set every lighter unit uses) at `guide-docs/build/observability/functional-design/`:
- **`domain-entities.md`** — the two sub-components (**T** trace-side · **M** metric-side) + interface surfaces; the two frozen source streams; the **reference-not-own** boundary (imports no event type — Q5-A); the **~5 metrics** with grounded sources + demographic-free labels; the **FD↔Infra/composition** boundary; **module layout OPEN** (Q4-A).
- **`business-rules.md`** — **BR-OBS-1..7**, each checkable, no orphan; **load-bearing BR-OBS-1** (edits no frozen unit; composition wires) + **BR-OBS-2** (100%-coverage grounded in U4's real node list).
- **`business-logic-model.md`** — the two-plane lifecycle + invariants + a **validated rectangle-only Mermaid** (11 nodes; alphanumeric IDs; quoted labels with no hyphens/colons/parens/semicolons; dashed `wired`/`guards` edges) + **text alternative** + invariant self-check.

**`observability` (U21) stage status**: **FD ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the FD 2-option completion gate** · NFR Requirements ⏳ · NFR Design ⏳ · **Infrastructure Design ⏳ (expected REAL/comprehensive — wiring-heavy)** · Code Generation ⏳. **The 4th of 6 Phase-2 units; FD is the 1st of its 5 stages.**

**Register (unchanged by this pass)**: 20 of 23 units complete; **U21 at its 1st stage**; 2 P2 remain beyond U21 (`llm-judge` U22 · `deploy-config` U23); **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN** (non-blocking; now doubly relevant — U19 built the handler layer, U21 defines the trace/metric sinks that composition would bind); composition-root **Q1-B divergence OPEN**; **R2–R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end); **tier-B UNAUTHORIZED** (N/A); **`audit_store` Docker-guard gap DEFERRED**; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code**; **no `backend/observability/`**; **no frozen unit edited** (read-only re-read of `orchestrator.py` + the four `telemetry.py` + `stories.md`/`requirements.md`/`unit-of-work*.md`); **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · the 17 frozen P1 units UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (answers + §5.5 folds + gate) + the **3 new FD artifacts**. **STOPPED** at the FD 2-option completion gate (1. Request Changes / 2. Continue → NFR Requirements).

## 🧩 BUILD → `observability` (U21) — **FD APPROVED (Continue)** → NFR Requirements Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-18

**FD APPROVED 2026-07-18 (option 2, Continue → NFR Requirements)** — U21's FD **COMPLETE** (3 artifacts frozen: `domain-entities.md` + `business-rules.md` **BR-OBS-1..7** + `business-logic-model.md`). Gate **closed**. U21 advanced to **NFR Requirements — the 2nd of its 5 stages**. Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/observability-nfr-requirements-plan.md`. **NO NFR artifact; no code; `backend/observability/` NOT created.** **Depth: lighter** (consistent with FD; comprehensive reserved for Infrastructure Design).

**Tier convention (verbatim)**: pytest, **no live network/key/Docker/Langfuse/Prometheus**, injected sinks with **offline recording fakes**, **detector self-test on every structural scan**, **observed-never-gated**, tier-B N/A + unauthorized.

**§2.5 draft target map — all 7 BR-OBS mapped, NO ORPHAN + the metric-derivation split**: BR-OBS-1 → **NFR-OBS-NOEDIT-1** *(LOAD-BEARING: no-U21-import/mutate-of-frozen-source scan + detector self-test + injected-sink/offline-fake + no-frozen-file-mtime-change)* · BR-OBS-2 → **NFR-OBS-TRACE-1** *(LOAD-BEARING: recording-fake teeth, one span per real checkpointer node across BOTH real paths [finalize; retry-then-flag up to `MEMO_CITATION_RETRY_CAP`], fake sequence traced to `orchestrator.py`'s actual `{draft,validate,finalize,flag}` by value; span API wraps a fake non-graph tool step; system-wide 100% = AC-7 deploy-time audit, explicitly NOT tier-U)* · BR-OBS-3 → **NFR-OBS-SEP-1** · BR-OBS-4 → **NFR-OBS-DEMOFREE-1** *(detector self-test + allowlist scan)* · BR-OBS-5 → **NFR-OBS-SHAPE-1** *(no import of any frozen event type + fakes by value)* · the 3 emitter-sourced metrics → **NFR-OBS-METRIC-1** · the 2 emitterless metrics (LLM-call errors, outlier-flag rate) → **NFR-OBS-STEPMETRIC-1** *(fake step outcomes at the span-API boundary — distinct derivation path)* · BR-OBS-6 → **NFR-OBS-TIERU-1** *(no socket/key/Docker; 31 skips + 5 Docker errors unchanged)* · BR-OBS-7 → **NFR-OBS-CONTRACT-1** *(no Recommendation/verdict + no latency-failure assertion)* · plus **NFR-OBS-PERF-1** (soft/observed) + **NFR-OBS-SEC-1** (governance).

**THREE `[Answer]` questions, all BLANK**: **Q1** recording-fake path coverage (rec **A** — one PARAMETRIZED test over BOTH real terminal paths: DRY + both grounded paths explicitly exercised; vs two separate teeth; vs finalize-only [rejected — coverage hole]) · **Q2** span-API-boundary metric fixtures (rec **A** — dedicated fake-step-outcome fixtures distinct from the emitter-event fixtures, since the two derivation paths are structurally different) · **Q3** BR-OBS-3 single-event-two-plane (rec **A** — two independent assertions from the SAME input VALUE, **no shared MECHANISM** [which would couple the deliberately-separated planes] + a structural check the two modules don't import each other).

**`observability` (U21) stage status**: **FD ✓ COMPLETE (approved 2026-07-18)** · **NFR Requirements ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = `nfr-requirements.md` + `tech-stack-decisions.md` on explicit go) · NFR Design ⏳ · **Infrastructure Design ⏳ (expected REAL/comprehensive)** · Code Generation ⏳. **4th of 6 Phase-2 units; 2 of 5 stages engaged.**

**Register (unchanged)**: 20 of 23 units complete; U21 at its 2nd stage; 2 P2 remain (`llm-judge` U22 · `deploy-config` U23); `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (non-blocking); composition-root Q1-B divergence OPEN; R2–R5 unwired (R4 a `501` stub); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO NFR artifact**; **no code**; **no `backend/observability/`**; the **frozen FD re-opened none** (read-only); **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q3.

## 🧩 BUILD → `observability` (U21) — NFR Requirements Part 1 ANSWERED (Q1–Q3 all A) + ambiguity-check CLEAN (3 folds) + **Part 2 GENERATED** (2 artifacts); STOP at the NFR-Requirements 2-option gate — 2026-07-18

**Q1–Q3 all A** (embedded in the plan §4). **Verified on disk**: **`langfuse>=2.0.0` AND `prometheus-client>=0.21.0` are already floored + installed** ⇒ **NO new dependency** (unlike memo-extensions' MCP gap); **`MEMO_CITATION_RETRY_CAP = 2`**. **Mandatory ambiguity-check RAN (§4.5) → CLEAN (3 folds; no surface-and-stop)**:
- **NFR-OBS-Req-Fold-1 [check i]** — the retry-then-flag path **IS cap-grounded**: with the frozen CAP=2 it executes `draft→validate→draft→validate→flag` = **5 node executions** (reaching the cap **matters** — `flag` fires only at `attempts==CAP`); the coverage invariant is **one span per EXECUTION** (`draft`/`validate` appear twice, each its own span). TRACE-1 refined: the retry fixture models exactly `MEMO_CITATION_RETRY_CAP` cycles then flag; teeth assert span count == total executions (5 retry / 3 finalize), none missed or double-counted.
- **NFR-OBS-Req-Fold-2 [check ii]** — a simpler shaped fake **suffices**; **no Protocol interop-proof** warranted — **U21 defines NO `OutlierSignal`-style contract with U18** (the material distinction from U19). The outlier fixture exposes **`is_outlier` BY VALUE** (U18's real field name, no `outlier_model` import) — a real field, not invented; a full `isinstance` proof would be over-engineering.
- **NFR-OBS-Req-Fold-3 [check iii]** — a **shared plane-neutral allowlist module is NOT a forbidden cross-import**. BR-OBS-3 forbids **trace↔metric** coupling; both planes importing a shared non-plane-specific allowlist/demographic-free module is legitimate + DRY. SEP-1's no-cross-import scan is scoped **semantically** (MCPRO-1 precedent): flags `trace_*↔metrics_*/*_sink`, **permits** the shared module. Adds one shared module to the open layout (Q4-A), recorded for NFR Design/Code-Gen.

**PART 2 GENERATED — 2 artifacts** at `guide-docs/build/observability/nfr-requirements/`:
- **`nfr-requirements.md`** — the **eleven `NFR-OBS-*`** targets: **NOEDIT-1 + TRACE-1** the load-bearing pair (full-highest), SEP-1, DEMOFREE-1, SHAPE-1, **METRIC-1** (3 emitter-sourced metrics), **STEPMETRIC-1** (2 step-outcome metrics), TIERU-1, CONTRACT-1, PERF-1 (soft), SEC-1 (governance) — each pass/fail + acceptance + tier + rigor; Q1–Q3 + Req-Fold-1..3 folded in; **traceability, no orphan** (BR-OBS-1..7 → 7 targets; ~5 metrics → METRIC-1×3 + STEPMETRIC-1×2); the **full Security-Guardrails table** (DEMOFREE-1 load-bearing for bias-free/error-hygiene; CONTRACT-1 advisory-only; deliverable transparency via the register item) — **no blocking finding**.
- **`tech-stack-decisions.md`** — **OBS-D1..D9**; **NO NEW DEPENDENCY** (`langfuse` + `prometheus-client` already floored+installed, verified table; the metric registry is **in-memory pure-Python at tier-U**, `prometheus-client` the **deploy-time** exporter behind the injected sink); **⚑ `OBS-SINK-DEFERRED`** = the **live-wiring deferral**, registered as a **NON-dependency** item and **contrasted explicitly** with `MCP-TRANSPORT-DEFERRED` (which flagged a *missing* library — here both SDKs exist); `requirements.txt` NOT edited.

**`observability` (U21) stage status**: **FD ✓ · NFR Requirements ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the NFR-Requirements 2-option completion gate** · NFR Design ⏳ · **Infrastructure Design ⏳ (expected REAL/comprehensive)** · Code Generation ⏳. **4th of 6 Phase-2 units; 2 of 5 stages complete pending gate.**

**Register (UPDATED — one NEW non-dependency item)**: 20 of 23 units complete; U21 at its 2nd stage; 2 P2 remain (`llm-judge` U22 · `deploy-config` U23); **⚑ NEW — `OBS-SINK-DEFERRED` OPEN** (live Langfuse/Prometheus wiring deferred to composition/deploy-config; **NON-blocking**, **NON-dependency** — both SDKs floored+installed); `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (non-blocking); composition-root Q1-B divergence OPEN; R2–R5 unwired (R4 a `501` stub); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code**; **no `backend/observability/`**; **`requirements.txt` NOT edited**; the **frozen FD re-opened none**; **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (answers + §4.5 folds + gate) + the **2 new NFR artifacts**. **STOPPED** at the NFR Requirements 2-option completion gate (1. Request Changes / 2. Continue → NFR Design).

## 🧩 BUILD → `observability` (U21) — **NFR Requirements APPROVED (Continue)** → NFR Design Part 1 (Plan) WRITTEN; STOP at plan-file gate — 2026-07-18

**NFR Requirements APPROVED 2026-07-18 (option 2, Continue → NFR Design)** — U21's NFR Requirements **COMPLETE** (2 artifacts frozen: `nfr-requirements.md` **eleven NFR-OBS-\*** + `tech-stack-decisions.md` **OBS-D1..D9**). Gate **closed**. U21 advanced to **NFR Design — the 3rd of its 5 stages**. Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/observability-nfr-design-plan.md`. **NO NFR-Design artifact; no code; `backend/observability/` NOT created.** **Depth: lighter.**

**§2 pattern map — ELEVEN patterns `P-OBS-1..11`, all targets covered, NO ORPHAN**: **P-OBS-1 InjectedSinkAbstractionPattern** *(load-bearing NOEDIT-1 — injected sink Protocols make editing a frozen unit **structurally unnecessary** [nothing to gain] + the scan proving nothing touched: the by-construction-plus-scan pairing)* · **P-OBS-2 DualCoverageTracePattern** *(load-bearing TRACE-1 — checkpointer-callback auto-traces graph nodes by construction over the real 4-node list, both paths [finalize 3 / retry-then-flag 5 at CAP=2], + span-API wraps tool steps = jointly-exhaustive; **Q3** decides one span sink vs two)* · **P-OBS-3 TwoPlaneSeparationPattern** *(SEP-1 — no `trace↔metric` cross-import, semantic; the shared allowlist is the ONLY shared import, carries no plane knowledge)* · **P-OBS-4 SingleSourcedAllowlistPattern** *(DEMOFREE-1 — both planes project through the one shared module; **Q1** pins its shape)* · **P-OBS-5 ByShapeConsumptionPattern** *(SHAPE-1 — import no frozen event type; **even more minimal than `OutlierSignal`** since no Protocol warranted, Req-Fold-2; **Q2** decides typed surface vs pure duck-typing)* · **P-OBS-6 EmitterSourcedDerivationPattern** *(METRIC-1, 3 metrics)* · **P-OBS-7 StepOutcomeDerivationPattern** *(STEPMETRIC-1, 2 metrics, `is_outlier` by value, distinct path)* · **P-OBS-8 InjectedFakeTierUPattern** *(TIERU-1)* · **P-OBS-9 NoContractObservedNotGatedPattern** *(CONTRACT-1 + PERF-1)* · **P-OBS-10 StructuralGuardPattern** *(5 AST scans, each detector self-test)* · **P-OBS-11 ReferencedGovernancePattern** *(SEC-1 + OBS-SINK-DEFERRED)*.

**§3 components `C-OBS-1..4` with exact signatures**: `trace-side` (`TraceSpan` + `record_span` injected sink Protocol + checkpointer callback + span-API context-manager) · `metric-side` (`MetricDefinition` + registry + `derive_from_event` + `derive_from_step_outcome` + `export` exporter Protocol) · **the shared plane-neutral allowlist module** `project_allowlisted(fields, allowed) -> dict` (pure) · `StructuralGuard` substrate. **§3.2 reference-not-own THREE distinct categories** (consumed-by-shape-from-frozen-streams / shared-internal-allowlist / deferred-to-composition `OBS-SINK-DEFERRED`). **§3.3 component→target coverage, no orphan.** **§3.4** plans the validated Mermaid with a **`frozen unit source`** node **blocked** from both planes (no-frozen-edit) + a **blocked** `trace↔metric` edge (no-cross-import) + both connecting to the shared allowlist node.

**THREE `[Answer]` questions, all BLANK**: **Q1** shared allowlist module shape (rec **A** — a **pure-function utility** with no plane-specific knowledge, structurally incapable of coupling; vs a Protocol both implement [duplicates the discipline, weakens single-source]) · **Q2** by-shape consumption surface (rec **A** — **pure duck-typing through the allowlist utility**, no per-event Protocol/TypedDict; vs a minimal TypedDict [duplicates the allowlist set]) · **Q3** TRACE-1's two mechanisms (rec **A** — **ONE shared span-sink Protocol `record_span` with TWO callers**, single span schema, coverage as a union over one span stream; vs two distinct sink interfaces).

**`observability` (U21) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = `nfr-design-patterns.md` + `logical-components.md` on explicit go) · **Infrastructure Design ⏳ (expected REAL/comprehensive)** · Code Generation ⏳. **4th of 6 Phase-2 units; 3 of 5 stages engaged.**

**Register (unchanged)**: 20 of 23 units complete; U21 at its 3rd stage; 2 P2 remain (`llm-judge` U22 · `deploy-config` U23); **`OBS-SINK-DEFERRED` OPEN** (non-blocking, non-dependency); `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN; composition-root Q1-B divergence OPEN; R2–R5 unwired (R4 a `501` stub); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO NFR-Design artifact**; **no code**; **no `backend/observability/`**; **`requirements.txt` NOT edited**; the **frozen FD + approved NFR Requirements re-opened none**; **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q3.

## 🧩 BUILD → `observability` (U21) — NFR Design Part 1 ANSWERED (Q1–Q3 all A) + ambiguity-check CLEAN (3 folds) + **Part 2 GENERATED** (2 artifacts); STOP at the NFR-Design 2-option gate — 2026-07-18

**Q1–Q3 all A** (embedded in the plan §5). **Mandatory ambiguity-check RAN (§5.5) → CLEAN (3 folds; no surface-and-stop)** — the three user-flagged checks resolved against frozen facts:
- **NFR-ND-OBS-Fold-1 [check i]** — the **single `record_span` sink does NOT weaken TRACE-1's two-path teeth**: each teeth test drives **exactly one caller** (graph-path → the checkpointer callback over a fake node sequence → the recorded ordered `step_name` list equals the grounded `[draft,validate,finalize]`=3 / `[draft,validate,draft,validate,flag]`=5-at-CAP=2; tool-step → the span API), so the union count **is** the per-source count. Latent attribution is free (`step_name` distinguishes graph names from tool names).
- **NFR-ND-OBS-Fold-2 [check ii]** — the **allowlist utility's detector self-test IS DEMOFREE-1's** (single-sourced guarantee = single-sourced test: feed `project_allowlisted` a forbidden attribute + an excluding `allowed` set → asserted dropped); **complemented** by a structural **no-bypass** scan (neither plane reads a raw attribute into a span/label without routing through the utility). Not a separate duplicate.
- **NFR-ND-OBS-Fold-3 [check iii]** — Q2's by-shape consumption and STEPMETRIC-1's **`is_outlier`-by-value fixture AGREE by construction**: the step-outcome derivation's `_STEP_ALLOWED` includes `is_outlier` (U18's real field, Req-Fold-2) and the fixture exposes exactly that ⇒ fixture ⊆ allowlist; a **consistency assertion** pins it so a rename either side fails loudly.

**PART 2 GENERATED — 2 artifacts** at `guide-docs/build/observability/nfr-design/`:
- **`nfr-design-patterns.md`** — **P-OBS-1..11**, each stating how it structurally meets its target; the **load-bearing pair spelled out with ACTUAL mechanisms** (P-OBS-1 = the injected `TraceSink`/`MetricExporter` Protocols + the no-frozen-namespace-write scan; P-OBS-2 = **one `record_span` sink, two callers** + the grounded `finalize=3` / `retry=5`-at-CAP=2 **ordered-`step_name`** teeth + the tool-step span wrap + the union claim); a **validated rectangle-only Mermaid** with `TRACE -.blocked.-> METRIC` (no-cross-import) and both `-.blocked.-> FROZEN` (no-frozen-edit) and both `--> ALLOW` (the one legitimate shared import) + text alternative; **traceability, no orphan (11/11)**.
- **`logical-components.md`** — **C-OBS-1..4** with **exact signatures**: `trace-side` (`TraceSink` Protocol + `TraceRecorder.on_step`/`span` — two callers) · `metric-side` (`MetricExporter` + `derive_from_event` + `derive_from_step_outcome`, distinct `_EVENT_ALLOWED`/`_STEP_ALLOWED`) · **`allowlist`** (`project_allowlisted` pure plane-neutral) · `StructuralGuard` (5 scans, each detector self-test). The **three-category reference-not-own** kept distinct; validated component Mermaid + text alt; **component→target coverage, no orphan**; settled items held.

**`observability` (U21) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the NFR-Design 2-option completion gate** · **Infrastructure Design ⏳ (expected REAL/comprehensive — the "wiring-heavy" stage; likely the 2nd real non-skip after `database`)** · Code Generation ⏳. **4th of 6 Phase-2 units; 3 of 5 stages complete pending gate.**

**Register (unchanged)**: 20 of 23 units complete; U21 at its 3rd stage; 2 P2 remain (`llm-judge` U22 · `deploy-config` U23); **`OBS-SINK-DEFERRED` OPEN** (non-blocking, non-dependency); `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN; composition-root Q1-B divergence OPEN; R2–R5 unwired (R4 a `501` stub); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code**; **no `backend/observability/`**; **`requirements.txt` NOT edited**; the **frozen FD + approved NFR Requirements re-opened none**; **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units UNTOUCHED**; **no import of a frozen event type**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (answers + §5.5 folds + gate) + the **2 new NFR-Design artifacts**. **STOPPED** at the NFR Design 2-option completion gate (1. Request Changes / 2. Continue → Infrastructure Design).

**Guardrails held**: **NO infra artifact created**; **no code**; **no `backend/memo_extensions/`**; **`requirements.txt` NOT edited**; WIRE-1 untouched; `outlier-model` (U18) + `ui-outlier-view` (U20) untouched; **`memo-agent-core` (U4) + all 17 frozen P1 units untouched** (**read-only** re-reads of `provider.py` + a directory listing of U4's build folder to settle the premise — **nothing modified**); the closed composition root untouched; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. **STOPPED** at the Infrastructure Design 2-option completion gate (1. Request Changes / 2. Continue → Code Generation).

## 🧩 BUILD → `observability` (U21) — **NFR Design APPROVED (Continue)** → Infrastructure Design **ASSESSED = REAL/comprehensive (NOT a skip)** → Infrastructure Design Part 1 (Plan) WRITTEN; STOP at the plan-file gate — 2026-07-18

**NFR Design APPROVED 2026-07-18 (option 2, Continue → Infrastructure Design)** — U21's NFR Design **COMPLETE** (2 artifacts frozen: `nfr-design-patterns.md` **P-OBS-1..11** + `logical-components.md` **C-OBS-1..4**). Gate **closed**. U21 advanced to **Infrastructure Design — the 4th of its 5 stages**. This is the stage `unit-of-work.md:248` pins **"comprehensive at Infrastructure Design (wiring-heavy)"**.

**⚑ ASSESSMENT (verified at the stage, outcome NOT pre-assumed) = REAL / COMPREHENSIVE — NOT a skip.** Four independent frozen sources converge: **(1)** `unit-of-work.md:248` — U21 **"comprehensive at Infrastructure Design (wiring-heavy)"**, the ONLY P2 unit so classified, the opposite of every prior P2 skip; **(2)** FD `domain-entities.md §5` explicitly hands Infrastructure Design the **live Langfuse callback→checkpointer binding**, the **`/metrics` mount + scrape**, the **one Grafana dashboard topology**, the **keys via `secrets-config`**, and **AC-7's deploy-time trace audit**; **(3)** `tech-stack-decisions.md §3` **`OBS-SINK-DEFERRED`** enumerates exactly those deferred items pointed at *"Infrastructure Design (comprehensive) + composition/deploy-config"*; **(4)** `logical-components.md §3` category 3 repeats the same deferred list. These are **genuine deployment-topology decisions unresolved by any prior stage** + a **live substrate tension**: frozen `secrets_config.Settings` validates only the six Phase-1 vars with **`extra="ignore"`**, while `.env.example` **reserves** `LANGFUSE_*` as **"reserved-not-authored (BR-SEC-6)"** — so how the keys reach the SDK is **unauthored and lands exactly here**. CLAUDE.md **"Skip IF"** fails on **both** prongs (infrastructure changes EXIST; infrastructure is NOT already defined). ⇒ the **2nd real non-skip Infrastructure Design in the whole build, after `database` (U15)** — planned with the same rigor.

**Substrate re-read on disk (re-derived NONE)**: the frozen FD (`domain-entities.md §5` deferral list + `business-rules.md` **BR-OBS-1..7**); NFR Requirements (**eleven NFR-OBS-\*** + **OBS-D1..D9** + `OBS-SINK-DEFERRED`); NFR Design (**P-OBS-1..11** + **C-OBS-1..4**); the three plan files. **Frozen code**: `memo_agent_core/orchestrator.py` (the **real** 4 nodes `draft`/`validate`/`finalize`/`flag` + `MemorySaver` checkpointer + `run()` building its invoke `config` **internally** with **NO callbacks channel** + one `MemoTelemetryEvent` per run); `secrets_config/settings.py` (frozen `Settings` = six Phase-1 vars, `extra="ignore"`, **no Langfuse fields**); `.env.example` (reserved `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`/`LANGFUSE_HOST`); `requirements.txt` (`langfuse>=2.0.0` + `prometheus-client>=0.21.0` floored). **Precedent**: `database`'s Infrastructure Design (plan + `infrastructure-design.md` + `deployment-architecture.md`) — the structural template.

**Wrote Part 1 (Plan) ONLY**: `guide-docs/build/plans/observability-infrastructure-design-plan.md`. **NO Infrastructure-Design artifact; no code; `backend/observability/` NOT created; `requirements.txt` NOT edited; frozen `Settings` NOT edited.** Plan mirrors the database precedent: **§1** unit context (built ON C-OBS-1..4 not re-opened + the **five deferred halves** + reference boundaries + guardrails); **§2** the mandatory **SEVEN-category** infra pre-assessment (**Deployment** = Applicable; **Storage/Compute/Messaging** = N/A-as-owned / justified; **Networking** = narrow; **Monitoring** = CORE; **Shared** = narrow); **§3** **NINE blank `[Answer]` questions**; **§4** artifacts; **§5** constraints held; **§6** STOP.

**NINE `[Answer]` questions, all BLANK** (rec **A** throughout): **Q1** deployment topology per tier (dev optional-local / **CI NO live sinks** offline-fakes / prod Render + Langfuse Cloud + Prometheus + Grafana, free-tier) · **Q2** the **live Langfuse callback→checkpointer binding** given frozen `run()` has **no callbacks channel** + private checkpointer (rec **A**: composition-level binding via the injected `TraceSink`/`TraceRecorder` seam; the metric-plane completion is already available via the frozen `MemoTelemetryEvent`; the per-node callback attachment is recorded as an `OBS-SINK-DEFERRED` composition item needing a **future MINIMAL additive seam** IF ever needed — **NOT taken here, U4 frozen**; **B** edit-`run()` rejected, **C** monkeypatch rejected) · **Q3** `/metrics` mounted on the **existing** FastAPI service backed by the same in-memory registry, pull-scrape · **Q4** the **ONE** Grafana dashboard as-code, 5 panels one-per-metric, demographic-free · **Q5** secrets delivery — the three `LANGFUSE_*` as Phase-2 env vars consumed at the sink-binding boundary, **NOT added to frozen `Settings`** (`extra="ignore"` is the sanctioned seam), Infra authors the shapes per **BR-SEC-6** names-only; Prometheus pull-based (no app key), Grafana provider-managed (**B** edit-`Settings` rejected, **C** hardcode rejected) · **Q6** **AC-7 as a DEPLOY-TIME acceptance**, not tier-U · **Q7** Compute/Messaging/Storage explicit N/A-as-owned justification · **Q8** **no separate `shared-infrastructure.md`** (U21 provisions no shared instance, unlike `database`) · **Q9** comprehensive, two artifacts (`infrastructure-design.md` + `deployment-architecture.md`) + validated Mermaid, no code.

**`observability` (U21) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ (approved 2026-07-18) · Infrastructure Design ⏳ ASSESSED = REAL/comprehensive → Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = `infrastructure-design.md` + `deployment-architecture.md` on explicit go) · Code Generation ⏳. **4th of 6 Phase-2 units; 4 of 5 stages engaged; the 2nd real non-skip Infrastructure Design after `database`.**

**Register (unchanged)**: 20 of 23 units complete; U21 at its 4th stage; 2 P2 remain (`llm-judge` U22 · `deploy-config` U23); **`OBS-SINK-DEFERRED` OPEN** (non-blocking, non-dependency — this stage DESIGNS its resolution, does not wire it); `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN; composition-root Q1-B divergence OPEN; R2–R5 unwired (R4 a `501` stub); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO Infrastructure-Design artifact**; **no code**; **no `backend/observability/`**; **`requirements.txt` NOT edited**; **the frozen `secrets_config.Settings` model NOT edited** (`extra="ignore"` is the sanctioned Phase-2 seam); **U4's frozen `LangGraphOrchestrator` NOT edited** (read-only re-read of `orchestrator.py`); the **frozen FD + approved NFR Requirements + approved NFR Design re-opened none**; **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q9.

## 🧩 BUILD → `observability` (U21) — Infrastructure Design Part 1 ANSWERED (Q1–Q9 all A) + ambiguity-check CLEAN (3 folds) + **Part 2 GENERATED** (2 artifacts); STOP at the Infrastructure-Design 2-option gate — 2026-07-18

**Q1–Q9 all A** (embedded in the plan §3). **Mandatory ambiguity-check RAN (§3.5)** grounded in **U4's ACTUAL `orchestrator.run()`/checkpointer surface** + the **frozen `Settings` (`extra="ignore"`)** + **`.env.example`'s reserved `LANGFUSE_*` shapes** + the approved FD/NFR-Requirements/NFR-Design (incl. `OBS-SINK-DEFERRED` + BR-OBS-1/NOEDIT-1) → **CLEAN (3 folds; no surface-and-stop)**:
- **INFRA-OBS-Fold-1 [check i]** — the deferred per-node-callback item has a **CONCRETE bounded shape, not "zero."** Three sub-cases, only one deferred: **(a)** metric plane **already wired** — the frozen orchestrator `__init__` already accepts `telemetry: Optional[TelemetryEmitter]`, `_emit` fires one `MemoTelemetryEvent`/run; composition drives `derive_from_event` off it, **no U4 edit**; **(b)** trace-plane **run-level + tool-step spans wrap at composition** via `TraceRecorder.span`, **no U4 edit**; **(c)** trace-plane **per-INTERNAL-graph-node spans** (`draft`/`validate`/`finalize`/`flag` separate) is the **ONLY** deferred bit — needs LangGraph's per-node callback the frozen `run()` doesn't forward; shape **dictated by `invoke(config={"callbacks":[…]})`** → a future **minimal additive `callbacks`/`config` passthrough on `run()`**, recorded **WITH that named shape, NOT taken** (U4 frozen). Not starting from zero.
- **INFRA-OBS-Fold-2 [check ii]** — the dashboard-as-code **splits cleanly, needs no U23**: the **TOPOLOGY** (5 panels 1:1 to the 5 frozen metrics, Prometheus datasource, demographic-free) is a **design deliverable produced this stage**; the committed **dashboard-as-code FILE** is a **Code-Gen/deploy-config deliverable** (keeps *no-code / no `backend/observability/`*), home **named-not-created**.
- **INFRA-OBS-Fold-3 [check iii]** — **AC-7 named + grounded, mechanics left to its owner**: recorded as a deploy-time acceptance where the observed Langfuse span set **⊇ `{draft,validate,finalize,flag}` + composition-wrapped tool steps**; the exact verification mechanism (Langfuse API vs UI) is **`deploy-config`'s/AC-7's**, **not prescribed here**.

**PART 2 GENERATED — 2 artifacts** at `guide-docs/build/observability/infrastructure-design/`:
- **`infrastructure-design.md`** — §1 component→infra mapping **C-OBS-1..4** (trace-side + metric-side **BOUND** to real sinks; allowlist + StructuralGuard = no cloud topology); §2 the mandatory **SEVEN-category** infra sweep (Deployment Applicable · Storage/Compute/Messaging N/A-as-owned/justified · Networking narrow · **Monitoring CORE** · Shared narrow); §3 the **deferred-halves execution design** (3.1 live Langfuse binding + the three sub-cases + Fold-1c deferred item · 3.2 `/metrics` mount + pull-scrape · 3.3 Grafana dashboard topology + Fold-2 · 3.4 the `secrets-config` key-delivery contract **shapes-only** + the `extra="ignore"` rationale · 3.5 AC-7 deploy-time audit + Fold-3); §4 reference boundaries; §5 deferred decisions (`OBS-SINK-DEFERRED` **refined, not closed**; dashboard file home named-not-created); §6 constraints held.
- **`deployment-architecture.md`** — §1 three-tier topology table (dev optional-local / CI offline / prod Render free-tier) · §2 trace/metric flow per tier · §3 Grafana dashboard topology · §4 networking · §5 monitoring + **shared-by-observation not shared-instance ⇒ NO separate `shared-infrastructure.md`** · §6 the **validated deployment-topology Mermaid** (rectangle-only, alphanumeric IDs, quoted labels — no hyphens/semicolons/colons/parentheses/special chars, 3 balanced subgraph/end pairs) + **full text alternative** · §7 settled items held.

**NO key/endpoint VALUES anywhere** — shapes only (the three reserved `LANGFUSE_*` names). **NO separate `shared-infrastructure.md`** (Q8-A).

**`observability` (U21) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the Infrastructure-Design 2-option completion gate** · Code Generation ⏳. **4th of 6 Phase-2 units; 4 of 5 stages complete pending gate; the 2nd real non-skip Infrastructure Design after `database`.**

**Register (UPDATED — `OBS-SINK-DEFERRED` refined, still OPEN)**: 20 of 23 units complete; U21 at its 4th stage; 2 P2 remain (`llm-judge` U22 · `deploy-config` U23); **`OBS-SINK-DEFERRED` OPEN — now DESIGNED (not wired)**: the live binding is fully designed; the **only** U4-blocked sub-item is the per-internal-graph-node callback (Fold-1c), now with a **named shape**; discharged only at composition/deploy-config once AC-7 passes (non-blocking, non-dependency); `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN; composition-root Q1-B divergence OPEN; R2–R5 unwired (R4 a `501` stub); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code**; **no `backend/observability/`**; **`requirements.txt` NOT edited**; the **frozen `secrets_config.Settings` model NOT edited** (`extra="ignore"` is the sanctioned seam); **U4's `LangGraphOrchestrator` NOT edited** (read-only re-read); the **frozen FD + approved NFR Requirements + approved NFR Design re-opened none**; **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (§3.5 folds added) + the **2 new Infrastructure Design artifacts**. **STOPPED** at the Infrastructure Design 2-option completion gate (1. Request Changes / 2. Continue → Code Generation).

## 🧩 BUILD → `observability` (U21) — **Infrastructure Design APPROVED (Continue)** → Code Generation Part 1 (Plan) WRITTEN; STOP at the plan-file gate — 2026-07-18

**Infrastructure Design APPROVED 2026-07-18 (option 2, Continue → Code Generation)** — U21's Infrastructure Design **COMPLETE** (2 artifacts frozen: `infrastructure-design.md` + `deployment-architecture.md`; **INFRA-OBS-Fold-1..3**). Gate **closed**. U21 advanced to **Code Generation — the 5th and LAST of its 5 stages**. Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/observability-code-gen-plan.md`. **NO code; NO `backend/observability/`; `requirements.txt` NOT edited.** **Depth: comprehensive.**

**Sibling convention grounded on disk**: `backend/outlier_model/` + `backend/memo_extensions/` = `backend/<unit>/` production `.py` modules + `__init__.py` + `tests/{__init__.py, fixtures.py, structural.py, test_*.py}`, TDD tests-first / leaf-first; `pyproject` addopts one `--cov=backend/<unit>` line + global `--cov-fail-under=90` + `--cov-report=term-missing`, **no `omit`** for pure-logic units. **Baseline 1096 passed / 31 skipped.**

**Plan contents**: **(§2)** component→module map onto **THREE production modules** + `__init__.py` — **`allowlist.py`** (C-OBS-3 leaf: `project_allowlisted` + `ScalarValue` + `_is_scalar`) · **`trace.py`** (C-OBS-1: `TraceSink` Protocol + `_SPAN_ALLOWED` + `TraceRecorder` with `on_step` callback + `span` context-manager, **two callers**) · **`metrics.py`** (C-OBS-2: `MetricExporter` Protocol + `MetricContribution` + `MetricDefinition` ×5 + `_EVENT_ALLOWED`/`_STEP_ALLOWED` + `derive_from_event` [3] + `derive_from_step_outcome` [2]) + **`StructuralGuard` in `tests/structural.py`**; **NO fifth undisclosed module**. **Header-comment deliverables (documentation only, NEVER enforcement) CONFIRMED explicit on all THREE** production modules (incl. `trace.py` naming the deferred per-node-callback shape per Q6). **(§3)** full TDD test→target map, **11 `NFR-OBS-*` NO ORPHAN**, each at its pinned tier: the **two LOAD-BEARING at full-highest** — **NOEDIT-1** (no-frozen-import/mutate scan + detector self-test + no-frozen-mtime + the **by-construction injected-sinks-make-editing-unnecessary** argument) and **TRACE-1** (recording-fake teeth over **BOTH real paths** parameterized: finalize `[draft,validate,finalize]`=**3** / retry-then-flag `[draft,validate,draft,validate,flag]`=**5** at CAP=2, one span per node execution via the **single `record_span` sink, two callers**, span-API wraps a fake tool step, grounded in `orchestrator.py`'s actual node names **by value**, system-wide 100% = **AC-7 deploy-time NOT tier-U**) — plus **SEP-1** (two independent same-value assertions, no shared mechanism + semantic no-cross-import scan permitting the shared allowlist), **DEMOFREE-1** (the single detector self-test **at the allowlist utility IS** DEMOFREE-1's, Fold-2, + no-bypass scan), **SHAPE-1** (no frozen event-type import), **METRIC-1** (3 emitter-sourced), **STEPMETRIC-1** (2 step-outcome, `is_outlier` by value, the **Fold-3** fixture-⊆-`_STEP_ALLOWED` consistency assertion), **TIERU-1** (no socket/key/Docker; 31 skips + 5 Docker errors unchanged), **CONTRACT-1** (no `Recommendation`/verdict + scan 5), **PERF-1** (observed), **SEC-1** (governance); the **five `StructuralGuard` AST scans** each with a **detector self-test**. **(§4)** leaf-first build order (fixtures/structural substrate → `allowlist.py` → `trace.py` → `metrics.py` → the 5 scans → coverage gate). **(§6)** explicit HOLDS. **(§7)** coverage gate (`--cov=backend/observability`, `--cov-fail-under=90` unchanged, **1096/31 no-regression**, pure additive, **100%** target on the three modules).

**SEVEN `[Answer]` questions, all BLANK** (each full text + lettered options): **Q1** production module names (rec **A** — three modules `allowlist.py`/`trace.py`/`metrics.py`, since the live SDK sinks are deferred; **B** the FD four-file split rejected — the two `*_sink` files empty-of-live-code at tier-U) · **Q2** recording-fake double construction (rec **A** — shared `tests/fixtures.py`: capturing `RecordingTraceSink` + `RecordingMetricExporter` + by-value fake event/step-outcome fixtures, distinct families per derivation path) · **Q3** exact grounded step-name sequences (rec **A** — exactly `[draft,validate,finalize]`=3 and `[draft,validate,draft,validate,flag]`=5 at CAP=2, one parametrized test, node names by value from `orchestrator.py`) · **Q4** exact allowlist field-name contents (rec **A** — chosen at generation from the frozen scalar fields, tests parameterized **OFF the named constant** per the `memo_extensions` Q4 / CG-OUT-Fold-1 precedent) · **Q5** test-file organization (rec **A** — mirror the siblings, one `test_*.py` per target + `fixtures.py` + `structural.py` + `test_structural_guard.py`) · **Q6** the deferred per-node-callback acknowledgment in code (rec **A** — **documentation-only** header/inline comment on `trace.py` naming the shape; **NO stub/placeholder/`langgraph` import/dead code**; the `on_step` caller already exists as the injected seam; **B** no-comment rejected, **C** stub function rejected) · **Q7** framework + coverage (rec **A** — `pytest` + `Hypothesis`, no new dep; one `--cov` line; `--cov-fail-under=90` unchanged; no `omit`; 100% target; 1096/31 no-regression).

**`observability` (U21) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ (approved 2026-07-18) · Code Generation ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = the three production modules + `tests/` under `backend/observability/` + the one `pyproject.toml` `--cov` line, on explicit go). **4th of 6 Phase-2 units; 5 of 5 stages engaged; this is the LAST stage — its approval closes the U21 loop.**

**Register (unchanged)**: 20 of 23 units complete; U21 at its 5th/last stage; 2 P2 remain (`llm-judge` U22 · `deploy-config` U23); **`OBS-SINK-DEFERRED` OPEN — DESIGNED (the per-internal-graph-node callback the only genuinely deferred item, shape named)**; `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN; composition-root Q1-B divergence OPEN; R2–R5 unwired (R4 a `501` stub); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code**; **no `backend/observability/`**; **`requirements.txt` NOT edited**; **no frozen unit edited** (read-only re-reads of the sibling `backend/` layouts + `pyproject.toml` only); **U4's frozen orchestrator + its frozen test file untouched**; **`secrets-config`'s frozen `Settings` untouched**; the **frozen FD + approved NFR Requirements + approved NFR Design + approved Infrastructure Design re-opened none**; **WIRE-1 · the closed composition root · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) + the 17 frozen P1 units UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q7.

## 🧩 BUILD → `observability` (U21) — Code-Gen Q1–Q7 ANSWERED (all A) + ambiguity-check RAN (CLEAN, 2 folds grounded in the real frozen shapes) → **Part 2 GENERATED + TESTED** → STOP at the Code-Gen 2-option gate; **U21 COMPLETE (LAST stage); 4th Phase-2 unit** — 2026-07-19

**Q1–Q7 all A** (embedded in the plan §5). **Mandatory ambiguity-check RAN (§5.5)**, grounded in the ACTUAL frozen shapes on disk (`MemoTelemetryEvent{recommendation:str, duration_ms:int}` · `rules_engine EvaluationTelemetry.evaluate_micros:int` · `OutlierResult.is_outlier:bool` · `orchestrator.py`'s 4 nodes + `MEMO_CITATION_RETRY_CAP`=2 · **`Recommendation(str, Enum)` — a STR-ENUM**) → **CLEAN (2 folds; no surface-and-stop)**:
- **CG-OBS-Fold-1 [NOEDIT-1 no-mtime realization]** — the *"no-frozen-file-mtime-change"* sub-clause is realized as the **stronger, non-vacuous** structural scan *"no U21 production module imports OR mutates any frozen namespace"* (scan 1 + detector self-test) rather than a literal within-run mtime assertion (vacuous — nothing in a tier-U run touches frozen files — and inconsistent with the project's non-vacuity discipline). Guarantee **preserved + strengthened**: **U21 production imports ZERO backend units**.
- **CG-OBS-Fold-2 [shared str-enum `recommendation` across two event types]** — `recommendation` is a str-enum value carried by BOTH `MemoTelemetryEvent` and `EvaluationTelemetry`, so both survive scalar-projection. Resolved by keying `derive_from_event` **field→metric 1:1** (`recommendation`→decisions counter, `duration_ms`→latency, `evaluate_micros`→rule-duration); per `domain-entities §4` the decisions counter's **source is the MEMO event stream** (one memo run = one decision), and **stream routing is composition wiring** (already `OBS-SINK-DEFERRED`). One `derive_from_event`, one `_EVENT_ALLOWED`, no double-count within the tested contract.

**PART 2 GENERATED — TDD tests-first / leaf-first, plan §4 order** — `backend/observability/`: **3 production modules** (`allowlist.py` = `project_allowlisted` + `ScalarValue` + `_is_scalar` · `trace.py` = `TraceSink` Protocol + `_SPAN_ALLOWED` + `TraceRecorder` [`on_step` callback + `span` context-manager, two callers] + **the deferred-per-node-callback shape named in the header per Q6, NO stub** · `metrics.py` = `MetricExporter` Protocol + `MetricDefinition` ×5 + `MetricContribution` + `_EVENT_ALLOWED`/`_STEP_ALLOWED` disjoint + `derive_from_event` [3] + `derive_from_step_outcome` [2]) + `__init__.py` + **`tests/`** (`fixtures.py` capturing doubles + by-value fixtures + grounded node sequences · `structural.py` AST substrate · **12 `test_*.py` / 57 tests**). **Header-comment deliverables explicit on all three** production modules. `pyproject` gained `--cov=backend/observability` (no omit); **`requirements.txt` NOT edited**.

**RESULT**: backend **1153 passed / 31 skipped** (1096 baseline + **57** new; the **5 pre-existing `audit_store` Docker-absence errors UNCHANGED**) — **zero regression**. `backend/observability` **100%** statements/branches on `allowlist.py`/`trace.py`/`metrics.py`; global **`--cov-fail-under=90` holds at 99.85%**. **U4's frozen suite GREEN and NOT double-collected** (observability imports no U4 test file — only a test-only import of the frozen CONSTANT `MEMO_CITATION_RETRY_CAP` in `test_trace.py` to ground the retry-path length, never a production edge). All **eleven `NFR-OBS-*`** tested at pinned tiers; the **two load-bearing (NOEDIT-1, TRACE-1) at full-highest**; the **five `StructuralGuard` AST scans** each carry a **detector self-test**. Realization: `provider_call_error` is a Code-Gen field name for the LLM-call-error step outcome (no frozen emitter field). One TIERU-1 test initially self-flagged (substring scan matched its own token-literal tuple) → rewritten to **AST import-based** detection (robust).

**`observability` (U21) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ · Code Generation ✓ (Part 1 answered + ambiguity-check RAN [2 folds] + Part 2 GENERATED + TESTED) → STOPPED at the Code-Generation 2-option completion gate.** **This was the LAST of U21's 5 stages → the per-unit loop for U21 is COMPLETE pending gate approval. U21 is the 4th of 6 Phase-2 units.**

**Register (UPDATED — U21 complete pending gate)**: 23-unit decomposition intact (**17 P1 done + 6 P2**; **U18 + U20 + U19 + (pending-gate) U21 COMPLETE**; **2 P2 remain: `llm-judge` (U22) / `deploy-config` (U23)**); **`OBS-SINK-DEFERRED` OPEN — DESIGNED + partially REALIZED** (the injected Protocols + offline fakes are built; the live `langfuse`/`prometheus-client` binding + the per-internal-graph-node callback [named in `trace.py`'s header, not stubbed] are discharged at composition/deploy-config); `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN; composition-root Q1-B divergence OPEN; **R2–R5 still unwired** (R4 still a `501` stub — core demo path still not runnable end-to-end); WIRE-1 **PINNED**; **tier-B still UNAUTHORIZED** (N/A); the **`audit_store` Docker-guard gap still DEFERRED** (31 skips + 5 Docker errors unchanged); `testresults.txt` refreshed this pass.

**Guardrails held (verified)**: **`memo-agent-core` (U4) + all 17 frozen P1 units untouched** (U4's orchestrator/telemetry consumed as documented; its test file never imported; frozen `LLMClient`/graph seam not modified); **`secrets-config`'s frozen `Settings` untouched**; **`outlier-model` (U18) / `memo-extensions` (U19) / `ui-outlier-view` (U20) reached by shape only, never imported** (U21 production imports **ZERO** backend units); **no new dependency**; **no live SDK import at tier-U**; **no fifth module**; **WIRE-1 / the closed composition root untouched**; **tier-B NOT authorized** (N/A); the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. Files written: 4 production files + 14 test/harness files under `backend/observability/`, `pyproject.toml` (one `--cov` line), `guide-docs/build/observability/code/code-summary.md`, `testresults.txt`, the plan (answers + §5.5 folds), this state entry, and the audit entry. **STOPPED** at the Code-Generation 2-option completion gate (1. Request Changes / 2. Continue to Next Stage).

## ✅ BUILD → `observability` (U21, EPIC-6, Phase 2) COMPLETE — the **21st fully-complete unit overall**; the **4th of 6 Phase-2 units** (after `outlier-model` U18 + `ui-outlier-view` U20 + `memo-extensions` U19) — 2026-07-19

**Code Generation APPROVED 2026-07-19 (option 2, Continue)** → the per-unit BUILD loop for `observability` is **CLOSED**. **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ (the 2nd REAL non-skip in the build, after `database`) · Code-Gen ✓.** Backend **1153 passed / 31 skipped** (1096 baseline + **57** new — **zero regression**; the 5 pre-existing `audit_store` Docker-absence errors unchanged); `backend/observability` **100%** statements/branches on `allowlist.py`/`trace.py`/`metrics.py`; global `--cov-fail-under=90` held at **99.85%**; **U4's frozen suite green and NOT double-collected**.

**⭐ observability is the FIRST unit in the build whose ENTIRE purpose was to OBSERVE other completed units without touching them — verified end-to-end**: U21 production imports **ZERO backend units** (the strongest form of BR-OBS-1 / NOEDIT-1); the frozen `memo_agent_core` orchestrator and the frozen `secrets_config` `Settings` model were both left **genuinely untouched** (read-only); the deferred per-internal-graph-node callback (INFRA-OBS-Fold-1c / `OBS-SINK-DEFERRED`) is correctly **DOCUMENTED** in `trace.py`'s header at the exact seam it concerns — **NOT stubbed, NOT silently dropped**.

**Two realization notes recorded (authoritative):**
- **CG-OBS-Fold-1 (NOEDIT-1 no-mtime realization)** — the *"no-frozen-file-mtime-change"* sub-clause is realized as the **stronger, non-vacuous** structural *"no U21 production import/mutate of any frozen namespace"* scan (a literal within-run mtime assertion would be vacuous). U21 production imports **zero** backend units.
- **CG-OBS-Fold-2 (shared str-enum `recommendation`)** — `Recommendation(str, Enum)` means `recommendation` survives scalar-projection from BOTH `MemoTelemetryEvent` and `EvaluationTelemetry`; resolved via the 1:1 field→metric map + the decisions counter sourcing from the **memo stream** (`domain-entities §4`), stream-routing being composition wiring (`OBS-SINK-DEFERRED`). One `derive_from_event`, one `_EVENT_ALLOWED`.

**COMPLETION ROSTER**: **21 of 23 units complete** — **all 17 P1** + **4 P2** (`outlier-model` U18 · `ui-outlier-view` U20 · `memo-extensions` U19 · **`observability` U21**). **2 P2 units remain: `llm-judge` (U22) · `deploy-config` (U23).** `database` + `observability` are the **two REAL Infrastructure-Design non-skips**; observability's Infra pass was the **2nd**.

**Deferred Decisions / cross-cutting register (carried, updated by this completion)**: the **23-unit decomposition unchanged**; the **composition root's Q1-B READ_AUDIT-vs-WIRE-1 divergence still OPEN**; **R2–R5 still unwired** (**R4 still a `501` stub** — the core underwriting demo path still **not runnable end-to-end**); **WIRE-1 PINNED**, untouched; **tier-B corpus run still UNAUTHORIZED** and confirmed **N/A to every unit built so far**; the **`audit_store` Docker-guard hygiene gap still DEFERRED** (31 skips + 5 Docker errors unchanged); **`OUTLIER-IN-PROSE` still OPEN and unassigned**; **`MCP-TRANSPORT-DEFERRED` still OPEN and non-blocking**; **⚑ NEW — `OBS-SINK-DEFERRED` OPEN**: the live Langfuse/Prometheus/Grafana binding + the one genuinely blocked per-internal-graph-node callback — both **DESIGNED but not wired**, discharged only at composition/deploy-config once **AC-7 passes**; **`testresults.txt` append-vs-overwrite** remains **open housekeeping**. **`deploy-config` (U23)** is the unit that would naturally discharge several accumulated open items (`OBS-SINK-DEFERRED` live wiring, `MCP-TRANSPORT-DEFERRED`, the composition-root's remaining unwired routes) if picked up.

**Guardrails held**: no unit started next; **WIRE-1 · the 17 frozen P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `memo-agent-core` (U4) · the closed composition root — UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**. **The next move is the user's decision** — no work started.

## 🧩 BUILD → `deploy-config` (U23, EPIC-6, Phase 2) STARTED → Functional Design Part 1 (Plan) WRITTEN; STOP at the plan-file gate — 2026-07-19

**User picked `deploy-config` (U23)** — the **5th of 6 Phase-2 units** to enter the per-unit loop (U18 + U20 + U19 + U21 complete). **FD is the 1st of its 5 stages.** Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/deploy-config-functional-design-plan.md`. **NO FD artifact; no code; no deploy files created.**

**DISCOVER-carryover check**: greenfield P2, no reverse-engineering, **NO prior U23 artifacts** (`guide-docs/build/deploy-config/` + `backend/deploy_config/` both absent, verified).

**⚑ DEPTH — VERIFIED (not assumed)**: `unit-of-work.md:250` = *"validation deploy on Render + Vercel, free-tier (distinct from Phase-3 production). US-PLAT-11. NFR-DEPLOY-1. **Depth: comprehensive at Infrastructure Design.**"*; `:262` lists `deploy-config` among the pure-wiring **"lighter candidates"** EXCEPT at Infra. ⇒ **verified split: FD depth = LIGHTER; comprehensive reserved for Infrastructure Design** (same pattern as `observability` U21 / `database` U15 — assessed at that stage, not pre-committed). Edges (`unit-of-work-dependency.md:52`): depends on **`database` + all `backend/*` + all `frontend/*`** — *"packages the validation deploy (Render + Vercel)"* / *"wrap the built system"* (a **packaging** relationship, not application-integration). **NFR-DEPLOY-1** = *"validation/staging deployment confirming cloud-readiness"*; **OOS-4**: production deploy is Phase-3; **NFR-CONSTRAINTS-1**: free-tier only.

**⚑ DECISIVE FINDINGS (verified on disk)**: **(a)** Scope-A `integration-summary.md §9` verbatim — the frontend *"cannot run in a browser — no bundler; **`deploy-config` (U23, P2) OWNS that**"*; verified `frontend/` has **NO build entry** (no `index.html`/`main.jsx`/`vite.config.js`, no `build` script — only `vitest`/`eslint`) ⇒ the **frontend bundler/build is squarely U23's**. **(b)** R2–R5 are `501 not_implemented` markers; Scope-A §9 verbatim — R2–R5 *"un-designed domain state, which belongs in its own stage (Scope B/C), not smuggled into a wiring pass"* ⇒ the frozen decomposition **already decided deploy-config proceeds WITHOUT R2–R5**; U23 is **not blocked** on them. **(c)** `deploy-config` is the **convergence point MULTIPLE frozen units named** for env/pipeline wiring: `database` Infra §5/§6 (Render migration release step + role-URL/`DATABASE_URL` env wiring) · `observability` `OBS-SINK-DEFERRED` §3 (`/metrics` scrape config + Grafana dashboard-as-code file + `LANGFUSE_*` env values) · `secrets-config` `.env.example` BR-SEC-6 (reserved Phase-2 shapes) ⇒ strong grounding that U23's scope is **deployment pipeline / topology / env-wiring / build**, NOT application-integration code.

**Plan contents**: §1 unit context (verified classification + edges + what exists to deploy) · §2 the three-register-item + Scope-A §9 **scope-triage table** (which hand-offs are in config scope vs separately-owned) · §3 proposed **lighter** FD structure + **layout OPEN** (a deployment-config unit is largely **declarative** — `render.yaml`/`vercel.json`/build config/env manifest — and **may need NO `backend/deploy_config/` Python package**) · §4 **FIVE blank `[Answer]` questions** · §5 constraints held · §6 STOP.

**FIVE `[Answer]` questions, all BLANK** (the 4 user-named + Q5): **Q1** scope = pipeline/topology/env-wiring/build ONLY vs also live sink-binding integration code (rec **A**: the **deployment half** is in scope — Render+Vercel+Prometheus+Grafana provisioning, `/metrics` scrape, the Grafana dashboard file, the migration release step, env wiring **shapes-only**; the live langfuse **callback ATTACHMENT is composition's/CLOSED**, and **`MCP-TRANSPORT-DEFERRED` is application-integration code NOT deploy-config's** — both remain **separately-owned even after U23**) · **Q2** relationship to R2–R5 (rec **A**: explicitly **OUT of scope** per Scope-A §9 — un-designed domain state = Scope B/C, a separate future decision, **NOT a blocking dependency**) · **Q3** deploy as-it-stands vs contingent/blocked (rec **A**: deploy the current slice with partial-runnability **documented**, NOT contingent — NFR-DEPLOY-1 is validation/staging confirming cloud-readiness, not end-to-end; the frozen edge + Scope-A §9 confirm the decomposition intends U23 to proceed now) · **⚑ Q4** depth/edges/Brief-*"Working deployed demo"* mutual consistency (rec **A**: **consistent** under the validation-deploy reading — the frozen NFR-DEPLOY-1 governs the looser Brief §7.1 header; **SURFACED phrasing tension flagged, not improvised**) · **Q5** FD depth + artifact set + layout (rec **A**: LIGHTER FD, lighter 3-artifact set, **layout OPEN**).

**`deploy-config` (U23) stage status**: **FD ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = the lighter FD artifact set on explicit go) · NFR Requirements ⏳ · NFR Design ⏳ · **Infrastructure Design ⏳ (expected REAL/comprehensive — the "comprehensive at Infrastructure Design" stage; likely the 3rd real non-skip after `database` + `observability`)** · Code Generation ⏳. **The 5th of 6 Phase-2 units; FD is the 1st of its 5 stages.**

**Register (unchanged by this pass)**: 21 of 23 units complete (17 P1 + U18/U20/U19/U21); **U23 at its 1st stage**; **1 P2 remains beyond U23: `llm-judge` (U22)**; composition-root **Q1-B divergence OPEN**; **R2–R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end — **and Q2 confirms U23 does not change this**); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (Q1 triages it as application-integration, NOT U23's); **`OBS-SINK-DEFERRED` OPEN** (Q1 triages: its deployment half is U23's, its code-attachment half is composition's); `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO FD artifact**; **no code**; **no deploy files**; **no frozen unit edited** (read-only re-reads of `unit-of-work*.md` + `requirements.md`/`stories.md` + `integration-summary.md` + `not_wired.py` + the `backend/app` + `frontend/` layout); the **CLOSED composition root untouched**; **WIRE-1 · the 17 P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `observability` (U21) UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q5.

## 🧩 BUILD → `deploy-config` (U23) — FD Part 1 ANSWERED (Q1–Q5 all A) + ambiguity-check CLEAN (3 folds) + **FD Part 2 GENERATED** (3 artifacts, lighter depth); STOP at the FD 2-option gate — 2026-07-19

**Q1–Q5 all A** (embedded in the plan §4). **Mandatory ambiguity-check RAN (§4.5)** grounded in NFR-DEPLOY-1 + OOS-4 + the edges + Scope-A §3/§9 + the `database`/`observability`/`secrets-config` hand-offs + **AC-7's exact text** (`requirements.md:238` — *"Observability · 100% of agent steps traced · Langfuse trace audit"*) → **CLEAN (3 folds; no surface-and-stop)**:
- **DEP-FD-Fold-1 [check i]** — **every named deferred item resolves on ONE side; no gray area survives.** (1) `OBS-SINK-DEFERRED` **deployment half** (Langfuse/Prometheus/Grafana free-tier provisioning + `/metrics` scrape config + the **Grafana dashboard-as-code FILE** [observability Infra left it a *"Code-Gen/deploy-config deliverable, home named-not-created"*] + **SET** the `LANGFUSE_*` env) → **deploy-config**. (2) `OBS-SINK-DEFERRED` **code-attachment half** → **composition CLOSED**, NOT deploy-config. (3) `MCP-TRANSPORT-DEFERRED` → **application-integration**, NOT deploy-config. (4) the reserved `secrets-config` shapes: the split is **SET-vs-CONSUME**, not item-vs-item — deploy-config **SETS** every env shape (`LANGFUSE_*`/`ANTHROPIC_API_KEY`/`OLLAMA_HOST`) while the **consuming** code is composition/application's; the migration **release-step** is env/pipeline (deploy-config) while the **runner** is database's. Set-but-not-necessarily-consumed = the same clean split.
- **DEP-FD-Fold-2 [check ii]** — **AC-7 is PROVISIONED-FOR but NOT dischargeable by deploy-config in the current slice; observability/AC-7-owned, contingent on a deferred composition binding.** AC-7 (deploy-time Langfuse trace audit) fires only once live traces flow → needs the langfuse callback attachment (composition-owned code half of `OBS-SINK-DEFERRED`, deferred). deploy-config **provisions the substrate** (Langfuse backend + env) but AC-7's pass is contingent on the deferred binding and **not** deploy-config's to assert — recorded as honest partial-runnability (Q3-A). No conflict (AC-7 is a trace audit, not a route).
- **DEP-FD-Fold-3 [check iii]** — **the Q1-B divergence is deployed AS-BUILT and DOCUMENTED, not resolved or hidden.** R6/R7 enforce `READ_AUDIT` (admin 403), diverging from WIRE-1 §3's *"authenticated"* (Scope-A §3, still OPEN, separately owned). deploy-config documents R1/R6/R7 as *"working per as-built behavior"* + names the Q1-B divergence as a carried-open item — **neither resolves nor obscures** it (BR-DEP-7). Reconciliation stays composition/contract-owned.

**PART 2 GENERATED — 3 artifacts at LIGHTER depth** at `guide-docs/build/deploy-config/functional-design/`:
- **`domain-entities.md`** — the deployment-config nature; §1 IS/IS-NOT scope table; §2 **config surfaces** (frontend build · Vercel project · Render backend service · env manifest shapes · migration release step · observability deployment half), **layout OPEN** (Q5-A — may need **no `backend/deploy_config/` package**); §3 **reference-not-own** boundary (packaged/consumed, never edited); §4 deferred-to-Infrastructure-Design (comprehensive) list; §5 FD↔later boundary.
- **`business-rules.md`** — **BR-DEP-1..9**, each checkable, no orphan; **load-bearing BR-DEP-1** (no-frozen-edit/packaging) + **BR-DEP-2** (static bundle for Vercel — the browser-runnability Scope-A §9 deferred here); BR-DEP-3 backend boots via fail-closed `Settings`; BR-DEP-4 SEC-3 shapes-only + detector-self-test analog; BR-DEP-5 free-tier/validation not production; BR-DEP-6 R2–R5 stay `501`; BR-DEP-7 honest partial-deploy documentation; BR-DEP-8 `OBS-SINK-DEFERRED` deployment half in / code+MCP out; BR-DEP-9 advisory-only trivial.
- **`business-logic-model.md`** — the **6-step deploy lifecycle** (build → provision → config-env → release → serve → document) + 4 invariants (INV-DEP-FROZEN/SEC3/HONEST/SCOPE) + a **validated rectangle-only Mermaid** (10 nodes; alphanumeric IDs; quoted labels — no hyphens/semicolons/colons/parentheses/special chars; `Q1B`/`AC7`/`R2 to R5` avoid the hyphen; dashed `packaged`/`values`/`deferred` edges) + text alternative + invariant self-check.

**`deploy-config` (U23) stage status**: **FD ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the FD 2-option completion gate** · NFR Requirements ⏳ · NFR Design ⏳ · **Infrastructure Design ⏳ (expected REAL/comprehensive — the "comprehensive at Infrastructure Design" stage; likely the 3rd real non-skip after `database` + `observability`)** · Code Generation ⏳. **The 5th of 6 Phase-2 units; FD is the 1st of its 5 stages.**

**Register (unchanged by this pass)**: 21 of 23 units complete; **U23 at its 1st stage**; **1 P2 remains beyond U23: `llm-judge` (U22)**; composition-root **Q1-B divergence OPEN** (Fold-3: deployed as-built + documented, not resolved); **R2–R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end — Q2 confirms U23 does not change this); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `OUTLIER-IN-PROSE` OPEN; **`MCP-TRANSPORT-DEFERRED` OPEN** (Fold-1: application-integration, NOT U23's); **`OBS-SINK-DEFERRED` OPEN** (Fold-1: deployment half is U23's, code-attachment half composition's; Fold-2: AC-7 provisioned-for not discharged); `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code**; **no deploy files**; **no frozen unit edited** (read-only re-reads of `requirements.md` AC-7 line + the plan answer tags); the **CLOSED composition root untouched**; **WIRE-1 · the 17 P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `observability` (U21) UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (answers + §4.5 folds + gate) + the **3 new FD artifacts**. **STOPPED** at the FD 2-option completion gate (1. Request Changes / 2. Continue → NFR Requirements).

## 🧩 BUILD → `deploy-config` (U23) — **FD APPROVED (Continue)** → NFR Requirements Part 1 (Plan) WRITTEN; STOP at the plan-file gate — 2026-07-19

**FD APPROVED 2026-07-19 (option 2, Continue → NFR Requirements)** — U23's FD **COMPLETE** (3 artifacts frozen: `domain-entities.md` + `business-rules.md` **BR-DEP-1..9** + `business-logic-model.md`). Gate **closed**. U23 advanced to **NFR Requirements — the 2nd of its 5 stages**. Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/deploy-config-nfr-requirements-plan.md`. **NO NFR artifact; no code; no deploy files.** **Depth: lighter.**

**⚑ Central tension stated up front (§1)**: `deploy-config` is the **FIRST genuinely DECLARATIVE unit** in the build — deliverables are config files (`render.yaml`/`vercel.json`/frontend build config/env manifest) + a deploy doc, **not application logic**; FD Q5-A records it **may need no `backend/deploy_config/` Python package**. Every prior unit's NFR targets were **pytest teeth over Python code**; here the testable surface is **different in kind** (config-validation / file-presence / structural-scan), plus a few **inherently Infra/Code-Gen-verified facts** this stage can only **NAME**. Tier convention held (no live cloud deploy at tier-U, no secret values in tests, detector self-test on every structural scan) but the **mechanism shifts** from assert-behavior to validate-config + scan-committed-artifacts. **The plan does NOT pre-assume a pytest-only shape** — Q1/Q3 decide it.

**§3 draft target map — all 9 BR-DEP mapped, NO ORPHAN + the testability split**: BR-DEP-1 → **NFR-DEP-NOEDIT-1** *(LOAD-BEARING: structural path/mtime scan — no U23 deliverable modifies any frozen tree or `backend/app`/`frontend/src/app` + detector self-test)* · BR-DEP-2 → **NFR-DEP-BUILD-1** *(config-presence + shape; the actual bundle build is an Infra/Code-Gen fact, Q3)* · BR-DEP-3 → **NFR-DEP-BOOT-1** *(config-presence: Render start command `backend.app.main:app` + env manifest six shapes; actual boot a deploy-time fact NAMED without teeth, Q3)* · BR-DEP-4 → **NFR-DEP-SEC3-1** *(LOAD-BEARING: secret-value scan over committed artifacts + detector self-test — synthetic `LANGFUSE_SECRET_KEY="sk-…"` flagged)* · BR-DEP-5 → **NFR-DEP-FREETIER-1** *(config scan — free-tier plans only)* · BR-DEP-6 → **NFR-DEP-ROUTES-1** *(route-table equivalence to the frozen composition root; no new route file)* · BR-DEP-7 → **NFR-DEP-DOC-1** *(⚑ Q2: checklist-completeness assertion vs governance item)* · BR-DEP-8 → **NFR-DEP-SCOPE-1** *(structural scan — scrape/dashboard/env config present but no callback-attachment code into `main.py`, no MCP transport module; env set-not-consumed)* · BR-DEP-9 → **NFR-DEP-ADVISORY-1** *(governance — no `Recommendation`/verdict)* · plus **NFR-DEP-SEC-1** (Security-Guardrails governance; SEC-3 load-bearing here).

**THREE `[Answer]` questions, all BLANK**: **Q1** meaningful tier-U surface vs config-validation checks (rec **A** — **HYBRID, config-validation-led**: pytest is the RUNNER but the teeth are file-presence/schema/structural-scan over committed artifacts, not behavior assertions; structural/path scans NOEDIT/SCOPE/ROUTES, secret-value scans SEC3 with detector self-tests, config-format validation FREETIER + `render.yaml`/`vercel.json` well-formed, presence/reference checks BUILD/BOOT; a few targets are inherently deploy-time facts NAMED without teeth) · **Q2** BR-DEP-7 mechanism (rec **A** — **checklist-completeness assertion**: required sections present [live-vs-`501` split · Q1-B divergence · AC-7 contingency · free-tier · env-shape list] + detector self-test; **B** governance-only weaker) · **Q3** proceed-as-if-Python-code vs explicit hybrid (rec **A** — **explicit HYBRID**, record which targets are inherently deploy-time facts NAMED without tier-U teeth; most NFR-DEP-* are config-validation/structural-scan/presence under pytest reading committed files; BUILD-1's actual bundle + BOOT-1's actual boot are Infra/deploy-time facts **observed-never-gated**, not fabricated teeth; **no new dep** beyond pytest + a possible YAML/JSON parse resolved in Part 2 tech-stack).

**`deploy-config` (U23) stage status**: **FD ✓ COMPLETE (approved 2026-07-19)** · **NFR Requirements ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = `nfr-requirements.md` + `tech-stack-decisions.md` on explicit go) · NFR Design ⏳ · **Infrastructure Design ⏳ (expected REAL/comprehensive — likely the 3rd real non-skip after `database` + `observability`)** · Code Generation ⏳. **5th of 6 Phase-2 units; 2 of 5 stages engaged.**

**Register (unchanged)**: 21 of 23 units complete; U23 at its 2nd stage; **1 P2 remains beyond U23: `llm-judge` (U22)**; composition-root Q1-B divergence OPEN (deployed as-built + documented per DEP-FD-Fold-3); R2–R5 unwired (R4 a `501` stub; core demo path not runnable end-to-end); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (application-integration, NOT U23's); `OBS-SINK-DEFERRED` OPEN (deployment half U23's, code half composition's; AC-7 provisioned-for not discharged); `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO NFR artifact**; **no code**; **no deploy files**; the **frozen FD re-opened none**; the **CLOSED composition root untouched**; **WIRE-1 · the 17 P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `observability` (U21) UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q3.

## 🧩 BUILD → `deploy-config` (U23) — NFR Requirements Part 1 ANSWERED (Q1–Q3 all A) + ambiguity-check CLEAN (3 folds) + **Part 2 GENERATED** (2 artifacts); STOP at the NFR-Requirements 2-option gate — 2026-07-19

**Q1–Q3 all A** (embedded in the plan §4). **Mandatory ambiguity-check RAN (§4.5) → CLEAN (3 folds; no surface-and-stop)**:
- **NFR-DEP-Req-Fold-1 [check i]** — **ROUTES-1 is a STATIC comparison against the committed composition-root SOURCE, no live deploy.** The route table is a fixed committed fact (`backend/app/routes/{session,decisions,not_wired}.py` + `main.py`); ROUTES-1 reads it from the frozen route decorators / `main.py` registration (or `app.openapi()["paths"]` built **in-process, no live server** — the TestClient-free introspection Scope-A used) and asserts it equals R1/R6/R7 + the four R2–R5 markers + no new route file. **Detector self-test**: a synthetic extra route / new route-file path is flagged.
- **NFR-DEP-Req-Fold-2 [check ii]** — **DOC-1's "marker present" is a PRECISE token-set check**, keyed to explicit tokens (`ROUTE-STATUS:`/`Q1-B-DIVERGENCE:`/`AC-7-CONTINGENCY:`/`FREE-TIER:`/`ENV-SHAPES:`, finalized at Code-Gen); matches the **token set**, not any heading, so an unrelated heading cannot pass. **Detector self-test**: a doc with a required token removed is flagged.
- **NFR-DEP-Req-Fold-3 [check iii]** — **a detector self-test on EVERY scan-bearing target**, not just the two load-bearing: NOEDIT-1, SEC3-1, ROUTES-1, SCOPE-1, DOC-1 (+ FREETIER-1) each carry their own + a non-vacuity assertion. BUILD-1/BOOT-1 are presence/reference checks whose deploy-time halves are **named observed-never-gated** (Q3), carrying a presence-detector but asserting no deploy behavior.

**PART 2 GENERATED — 2 artifacts** at `guide-docs/build/deploy-config/nfr-requirements/`:
- **`nfr-requirements.md`** — the **eleven `NFR-DEP-*`** targets: **NOEDIT-1 + SEC3-1** the load-bearing pair (full-highest, both with detector self-tests), **ROUTES-1** the third full-highest scan, BUILD-1/BOOT-1/FREETIER-1/SCOPE-1/DOC-1/ADVISORY-1 standard, PERF-1 soft, SEC-1 governance — each pass/fail + acceptance + tier + rigor; the **declarative-unit posture** stated up front (pytest is the RUNNER; teeth are config-validation/scan over committed artifacts; **BUILD-1/BOOT-1's actual bundle/boot are deploy-time facts observed-never-gated**, not fabricated teeth); Q1–Q3 + Req-Fold-1..3 folded in; **traceability, no orphan**; the full **Security-Guardrails compliance table** (SEC-3 load-bearing, CON-BR1 N/A trivially — no data surface, no blocking finding).
- **`tech-stack-decisions.md`** — **DEP-D1..D8**; **⚑ NO NEW DEPENDENCY** — `pytest` runner + **`pyyaml` already floored `>=6.0.0` AND installed (6.0.3)** for the YAML rulebook + stdlib `json` + stdlib `ast`/`pathlib` (verified on disk); `render.yaml` validated with `pyyaml`, `vercel.json` with stdlib `json`; **module/layout OPEN** (FD Q5-A — may need **no `backend/deploy_config/` Python package**; the test home is a Code-Gen decision); `requirements.txt` NOT edited.

**`deploy-config` (U23) stage status**: **FD ✓ · NFR Requirements ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the NFR-Requirements 2-option completion gate** · NFR Design ⏳ · **Infrastructure Design ⏳ (expected REAL/comprehensive — likely the 3rd real non-skip after `database` + `observability`)** · Code Generation ⏳. **5th of 6 Phase-2 units; 2 of 5 stages complete pending gate.**

**Register (unchanged)**: 21 of 23 units complete; U23 at its 2nd stage; **1 P2 remains beyond U23: `llm-judge` (U22)**; composition-root Q1-B divergence OPEN (deployed as-built + documented, DOC-1); R2–R5 unwired (R4 a `501` stub; core demo path not runnable end-to-end); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (application-integration, NOT U23's — SCOPE-1); `OBS-SINK-DEFERRED` OPEN (deployment half U23's, code half composition's; AC-7 provisioned-for not discharged); `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code**; **no deploy files**; **`requirements.txt` NOT edited**; the **frozen FD re-opened none**; the **CLOSED composition root untouched**; **WIRE-1 · the 17 P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `observability` (U21) UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (answers + §4.5 folds + gate) + the **2 new NFR artifacts**. **STOPPED** at the NFR Requirements 2-option completion gate (1. Request Changes / 2. Continue → NFR Design).

## 🧩 BUILD → `deploy-config` (U23) — **NFR Requirements APPROVED (Continue)** → NFR Design Part 1 (Plan) WRITTEN; STOP at the plan-file gate — 2026-07-19

**NFR Requirements APPROVED 2026-07-19 (option 2, Continue → NFR Design)** — U23's NFR Requirements **COMPLETE** (2 artifacts frozen: `nfr-requirements.md` **eleven NFR-DEP-\*** + `tech-stack-decisions.md` **DEP-D1..D8**). Gate **closed**. U23 advanced to **NFR Design — the 3rd of its 5 stages**. Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/deploy-config-nfr-design-plan.md`. **NO NFR-Design artifact; no code; no deploy files.** **Depth: lighter.**

**Design posture (§1, honest to a declarative unit)**: the patterns describe **config-validation MECHANISMS** (path scans, secret-value scans, in-process route introspection, token-set matching, config-format parsing) where that's genuinely the target; the components are a small validator set (or one) **plus the config artifacts themselves** as first-class named entities; **BUILD-1/BOOT-1 are honestly two-part** (tier-U presence check + named-not-tested deploy-time fact). The pattern↔component structure of every prior unit is **preserved; only the mechanism vocabulary shifts**.

**§2 pattern map — ELEVEN patterns `P-DEP-1..11`, all targets covered, NO ORPHAN**: **P-DEP-1 FrozenPathScanPattern** *(load-bearing NOEDIT-1: `pathlib` scan + detector self-test)* · **P-DEP-2 SecretValueScanPattern** *(load-bearing SEC3-1: regex/text scan over every committed artifact + detector self-test — synthetic `LANGFUSE_SECRET_KEY` + `postgresql://user:pass` flagged)* · **P-DEP-3 InProcessRouteIntrospectionPattern** *(load-bearing ROUTES-1: `app.openapi()[paths]` in-process, no live server, **reusing the composition-root pass's TestClient-free mechanism** per Req-Fold-1; detector synthetic extra route flagged)* · **P-DEP-4 TokenSetChecklistPattern** *(DOC-1: canonical heading + machine-checkable anchor tokens; matches the token set not any heading not prose quality, Req-Fold-2)* · **P-DEP-5 PresencePlusDeployTimeFactPattern** *(BUILD-1 + BOOT-1: the honest two-part — tier-U presence/reference check + named-not-tested deploy-time fact observed-never-gated — kept visibly distinct within one pattern)* · **P-DEP-6 ConfigTokenScanPattern** *(FREETIER-1)* · **P-DEP-7 ScopeBoundaryScanPattern** *(SCOPE-1: no callback-attachment into `main.py`, no MCP module, env set-not-consumed)* · **P-DEP-8 ConfigFormatValidationPattern** *(cross-cutting: `render.yaml` via `pyyaml`, `vercel.json` via stdlib `json`)* · **P-DEP-9 GovernanceAssertionPattern** *(ADVISORY-1 + SEC-1)* · **P-DEP-10 ObservedNotGatedPattern** *(PERF-1)* · **P-DEP-11 DetectorSelfTestSubstratePattern** *(cross-cutting: every scan-bearing target carries a detector self-test + non-vacuity, Req-Fold-3)*.

**§3 components `C-DEP-1..5`**: `deploy_validators` (scan logic — one module or a small `tests/`-scanning set, home a Code-Gen decision per DEP-D8) + `render.yaml` + `vercel.json` + frontend build entry (`index.html` + `main` mounting frozen `App.jsx` + `build` script) + env manifest (shapes) + deploy doc. **Three-category reference-not-own** (frozen system packaged-never-edited / config artifacts U23-owned / deferred-to-composition). Planned validated Mermaid with config artifacts → validators → the **frozen-system node with a blocked no-edit edge** (visible structural property) + a packaged edge + a deferred dashed edge to composition.

**THREE `[Answer]` questions, all BLANK**: **Q1** model config artifacts as first-class components vs inputs/data (rec **A** — YES, first-class NAMED components C-DEP-2..5 but explicitly tagged *"config artifact declarative, exact filename/home a Code-Gen decision (DEP-D8)"*; they ARE the unit's primary deliverables, keeps component→target coverage honest, mirrors every prior unit while the declarative tag + OPEN-layout caveat prevent overstating) · **Q2** one `deploy_validators` module vs scan-per-target set (rec **A** — one shared substrate + per-target scan functions each with detector self-test, the sibling `StructuralGuard`/`structural.py` shape adapted; file home a Code-Gen decision) · **Q3** BUILD-1/BOOT-1 two-part shape one pattern vs split (rec **A** — one `P-DEP-5` explicitly carrying both halves kept visibly distinct, models honestly without inventing a second pattern for a fact with no tier-U mechanism).

**`deploy-config` (U23) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = `nfr-design-patterns.md` + `logical-components.md` on explicit go) · **Infrastructure Design ⏳ (expected REAL/comprehensive — likely the 3rd real non-skip after `database` + `observability`)** · Code Generation ⏳. **5th of 6 Phase-2 units; 3 of 5 stages engaged.**

**Register (unchanged)**: 21 of 23 units complete; U23 at its 3rd stage; **1 P2 remains beyond U23: `llm-judge` (U22)**; composition-root Q1-B divergence OPEN (deployed as-built + documented, DOC-1); R2–R5 unwired (R4 a `501` stub; core demo path not runnable end-to-end); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (application-integration, NOT U23's — SCOPE-1); `OBS-SINK-DEFERRED` OPEN (deployment half U23's, code half composition's; AC-7 provisioned-for not discharged); `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO NFR-Design artifact**; **no code**; **no deploy files**; **`requirements.txt` NOT edited**; the **frozen FD + approved NFR Requirements re-opened none**; the **CLOSED composition root untouched**; **WIRE-1 · the 17 P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `observability` (U21) UNTOUCHED**; **no new dependency**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q3.

## 🧩 BUILD → `deploy-config` (U23) — NFR Design Part 1 ANSWERED (Q1–Q3 all A) + ambiguity-check CLEAN (3 folds) + **Part 2 GENERATED** (2 artifacts); STOP at the NFR-Design 2-option gate — 2026-07-19

**Q1–Q3 all A** (embedded in the plan §4). **Mandatory ambiguity-check RAN (§4.5)** grounded in the frozen FD + eleven `NFR-DEP-*` + Req-Fold-1..3 + the **ACTUAL Scope-A composition-root conftest** (`backend/app/tests/conftest.py` — re-read: it calls `create_app()` **directly**, route registration is **env-free**) → **CLEAN (3 folds; no surface-and-stop)**:
- **NFR-ND-DEP-Fold-1 [Q1+Q3 coverage-table interaction]** — config-artifacts-as-components (Q1-A) and P-DEP-5's two-part shape (Q3-A) **AGREE**: C-DEP-2/C-DEP-3 map to the tier-U **PRESENCE** half of BUILD-1/BOOT-1; the **deploy-time fact** is **named-not-tested** (observed-never-gated), so its absence from the tier-U column is **honest, not a gap**.
- **NFR-ND-DEP-Fold-2 [cross-cutting patterns supporting, not orphans]** — **P-DEP-8 (ConfigFormatValidation)** + **P-DEP-11 (DetectorSelfTestSubstrate)** are cross-cutting/composing (a precondition + the shared no-vacuous-scan substrate), **precedented** by prior units' substrate patterns; the traceability table marks them cross-cutting.
- **NFR-ND-DEP-Fold-3 [ROUTES-1 env-free/DB-free + import-to-read ≠ edit]** — the Scope-A conftest calls `create_app()` directly and route registration is env-free, so ROUTES-1 = `create_app().openapi()["paths"]` with **no live server, no live DB, no env/Settings**, **reusing the composition-root pass's `create_app()`+`openapi()` mechanism** (Req-Fold-1). Importing production `backend.app.main` read-only to introspect is **not editing** (NOEDIT-1 forbids writes) → **ROUTES-1 and NOEDIT-1 agree by construction**.

**PART 2 GENERATED — 2 artifacts** at `guide-docs/build/deploy-config/nfr-design/`:
- **`nfr-design-patterns.md`** — **P-DEP-1..11**, each stating how it structurally meets its target; the **load-bearing trio spelled out with actual mechanisms** (P-DEP-1 ALLOWED-vs-FROZEN prefix scan + detector · P-DEP-2 secret-value regex over every committed artifact + detector [name permitted, value flagged, non-vacuously] · P-DEP-3 `create_app().openapi()["paths"]` in-process, the seven exact route+method entries, **reuse not invention**, import-to-read ≠ edit) · P-DEP-4 token-set (not heading/prose) · **P-DEP-5 the two-part** (presence + named deploy-time fact) · P-DEP-6/7/8/9/10 · P-DEP-11 detector substrate; a **validated rectangle-only Mermaid** (config artifacts → validators; `-.reads.->` + `-.blocked.->` frozen [visible no-edit]; `-.packaged.->` frozen; `-.deferred.->` composition) + text alternative; **pattern→target→tier→rigor traceability, P-DEP-8/11 cross-cutting supporting, no orphan**.
- **`logical-components.md`** — **C-DEP-1 `deploy_validators`** (one substrate + per-target scan functions each with a detector self-test — a text listing of the substrate + the ten scans with their patterns; `check_route_table` imports `backend.app.main` read-only) + **C-DEP-2 `render.yaml`** + **C-DEP-3 `vercel.json`+build entry mounting frozen `App.jsx`** + **C-DEP-4 env manifest shapes** + **C-DEP-5 deploy doc**, each tagged *"config artifact (declarative), filename/home a Code-Gen decision (DEP-D8)"*; the **three-category reference-not-own** kept distinct; validated component Mermaid + text alt; **component→target coverage no orphan** (BUILD-1/BOOT-1 presence half → C-DEP-3/C-DEP-2; deploy-time-fact half named-not-tested); settled items held.

**`deploy-config` (U23) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the NFR-Design 2-option completion gate** · **Infrastructure Design ⏳ (expected REAL/comprehensive — the "comprehensive at Infrastructure Design" stage; likely the 3rd real non-skip after `database` + `observability`)** · Code Generation ⏳. **5th of 6 Phase-2 units; 3 of 5 stages complete pending gate.**

**Register (unchanged)**: 21 of 23 units complete; U23 at its 3rd stage; **1 P2 remains beyond U23: `llm-judge` (U22)**; composition-root Q1-B divergence OPEN (deployed as-built + documented, DOC-1); R2–R5 unwired (R4 a `501` stub; core demo path not runnable end-to-end); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (application-integration, NOT U23's — SCOPE-1); `OBS-SINK-DEFERRED` OPEN (deployment half U23's, code half composition's; AC-7 provisioned-for not discharged); `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code**; **no deploy files**; **`requirements.txt` NOT edited** (no new dependency); the **frozen FD + approved NFR Requirements re-opened none**; the **CLOSED composition root untouched** (read-only introspection only NAMED, not executed at this design stage); **WIRE-1 · the 17 P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `observability` (U21) UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (answers + §4.5 folds + gate) + the **2 new NFR-Design artifacts**. **STOPPED** at the NFR Design 2-option completion gate (1. Request Changes / 2. Continue → Infrastructure Design).

## 🧩 BUILD → `deploy-config` (U23) — **NFR Design APPROVED (Continue)** → Infrastructure Design **ASSESSED = REAL/comprehensive (NOT a skip)** → Infrastructure Design Part 1 (Plan) WRITTEN; STOP at the plan-file gate — 2026-07-19

**NFR Design APPROVED 2026-07-19 (option 2, Continue → Infrastructure Design)** — U23's NFR Design **COMPLETE** (2 artifacts frozen: `nfr-design-patterns.md` **P-DEP-1..11** + `logical-components.md` **C-DEP-1..5**). Gate **closed**. U23 advanced to **Infrastructure Design — the 4th of its 5 stages**. This is the stage `unit-of-work.md:250` pins **"comprehensive at Infrastructure Design"**.

**⚑ ASSESSMENT (verified at the stage, outcome NOT pre-assumed) = REAL / COMPREHENSIVE — NOT a skip.** Four-source convergence (the observability discipline): **(1)** `unit-of-work.md:250` — *"comprehensive at Infrastructure Design"*; **(2)** FD `domain-entities.md §4` explicitly hands Infra *"the actual Render/Vercel topology + build commands + env manifest + migration release step + observability scrape/dashboard config"*; **(3)** NFR Requirements (`nfr-requirements.md:12` + `tech-stack-decisions.md:41/48`) names BUILD-1/BOOT-1's actual build/boot *"verified at Infrastructure Design/deploy"*; **(4)** NFR Design (`nfr-design-patterns.md:62/152` + `logical-components.md:127`) repeats the deferred-to-Infra list. CLAUDE.md **"Skip IF"** fails on **both** prongs (infrastructure changes EXIST; not already defined). No prior U23 Infra artifacts (ABSENT). Both named precedent passes (`database`, `observability`) were real non-skips. ⇒ the **3rd real non-skip Infrastructure Design, after `database` (U15) + `observability` (U21)**.

**Substrate re-read on disk (re-derived NONE)**: U23's own FD (`domain-entities §4` deferred list + BR-DEP-1..9) + NFR Requirements (eleven NFR-DEP-* + DEP-D1..D8) + NFR Design (P-DEP-1..11 + C-DEP-1..5); **`observability`'s Infra** `deployment-architecture.md` (three-tier topology + deployment-half boundary) + `OBS-SINK-DEFERRED §3` (`/metrics` scrape + Grafana dashboard-as-code file + `LANGFUSE_*` env = a deploy-config deliverable); **`database`'s Infra** (the migration release step *"wired by deploy-config"* §3.4 + the role-URL secrets contract §5). Both explicitly named as **hand-off sources**.

**Wrote Part 1 (Plan) ONLY**: `guide-docs/build/plans/deploy-config-infrastructure-design-plan.md`. **NO Infrastructure-Design artifact; no code; no deploy files.** Plan mirrors the database/observability precedent: **§1** unit context (built ON C-DEP-1..5 not re-opened + the **six deferred halves** + reference boundaries [database owns Postgres topology · observability owns sink code + dashboard topology · secrets-config owns values · composition root packaged-not-edited] + guardrails); **§2** the mandatory **SEVEN-category** infra pre-assessment (**Deployment CORE** · **Storage reference-database's** · **Compute** the Render service · **Messaging N/A** · **Networking** · **Monitoring** the observability deployment half · **Shared narrow-reference**); **§3** **NINE blank `[Answer]` questions**; **§4** artifacts; **§5** constraints; **§6** STOP.

**NINE `[Answer]` questions, all BLANK** (rec **A** throughout): **Q1** Render backend service topology (Render free-tier Web Service, Python 3.12 pinned, `pip install -r requirements.txt`, start `uvicorn backend.app.main:app`, six Settings env + `GEMINI_API_KEY` dummy, managed TLS) · **Q2** Vercel frontend project (Vite preset, `npm run build`, output `dist`, entry mounting frozen `App.jsx`, free-tier) · **⚑ Q3** frontend↔backend connectivity **WITHOUT editing the frozen composition root** (rec **A**: a **Vercel rewrite/proxy** so the browser makes same-origin `/api` requests Vercel proxies to Render — **NO CORS, NO backend edit**, keeps BR-DEP-1 intact; **B** add-CORS-to-backend rejected [edits the closed composition root]; **C** serve-from-backend rejected) · **Q4** DB provisioning + migration release step (rec **A**: **reference** database's Render Postgres free-tier topology, wire the connection env + the **Render release/pre-deploy migration step** database Infra §3.4 named *"wired by deploy-config"*; runner is database's) · **Q5** env manifest topology (values set in platform never committed; full shape list Phase-1 six + Phase-2 reserved; `GEMINI_API_KEY` dummy; Phase-2 set-not-consumed) · **Q6** observability deployment half (Prometheus scrape → Render `/metrics`; the Grafana dashboard-as-code file **one-dashboard-five-panels 1:1** to observability's five frozen metrics [topology observability's, committed file this deliverable]; Langfuse Cloud + `LANGFUSE_*` env; **live callback attachment NOT here** — composition's; AC-7 provisioned-for not discharged) · **Q7** Compute/Messaging/Storage/Shared per-category (Compute=Render service · Storage=reference database's · Messaging=N/A · Shared=narrow-reference, no separate doc) · **Q8** deploy doc topology (honest partial-deploy — live-vs-`501` split · Q1-B divergence · AC-7 contingency · free-tier · env-shape list, each a DOC-1 token, nothing over-claimed) · **Q9** depth+artifacts+Mermaid (comprehensive, two artifacts + validated Mermaid, no separate shared-infrastructure.md, no code).

**`deploy-config` (U23) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ⏳ ASSESSED = REAL/comprehensive → Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = `infrastructure-design.md` + `deployment-architecture.md` on explicit go) · Code Generation ⏳. **5th of 6 Phase-2 units; 4 of 5 stages engaged; the 3rd real non-skip Infrastructure Design after `database` + `observability`.**

**Register (unchanged)**: 21 of 23 units complete; U23 at its 4th stage; **1 P2 remains beyond U23: `llm-judge` (U22)**; composition-root Q1-B divergence OPEN (deployed as-built + documented, DOC-1/Q8); R2–R5 unwired (R4 a `501` stub; core demo path not runnable end-to-end); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (application-integration, NOT U23's); **`OBS-SINK-DEFERRED` OPEN** — this stage DESIGNS its deployment half (scrape/dashboard-file/env), the code half stays composition's; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO Infrastructure-Design artifact**; **no code**; **no deploy files**; **no frozen unit edited** (read-only re-reads of U23's artifacts + database/observability Infra + confirming absence of prior U23 Infra); the **CLOSED composition root untouched** (Q3's Vercel-rewrite keeps CORS out of the backend); **database's + observability's Infra referenced, not re-opened**; **WIRE-1 · the 17 P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `observability` (U21) UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q9.

## 🧩 BUILD → `deploy-config` (U23) — Infrastructure Design Part 1 ANSWERED (Q1–Q9 all A) + ambiguity-check CLEAN (3 folds) + **Part 2 GENERATED** (2 artifacts); STOP at the Infrastructure-Design 2-option gate — 2026-07-19

**Q1–Q9 all A** (embedded in the plan §3). **Mandatory ambiguity-check RAN (§3.5)** grounded in the frozen U23 stack + `database`'s Infra (§3.4 migration release step, §5 role-URL contract) + `observability`'s Infra (`OBS-SINK-DEFERRED §3` + the frozen five-metric panel topology) → **CLEAN (3 folds; no surface-and-stop)**:
- **INFRA-DEP-Fold-1 [check i]** — Q3's proxied API base URL is a **SHAPE, not a SEC-3-flaggable value**: the Vercel rewrite targets the Render backend's **public host**, which is **not a credential** (SEC-3/SEC3-1 target `sk-…`/`postgresql://user:pass@…`, never a bare public host) and is modeled as a build/env shape (`RENDER_BACKEND_URL`) set in the Vercel env, never committed. No conflict.
- **INFRA-DEP-Fold-2 [check ii]** — the migration release step and the deploy doc's **ENV-SHAPES** section are **consistent about pre-release requirements**: the release step needs, before it runs, the schema-owning `DATABASE_URL` + the role passwords `AUDIT_WRITER_PASSWORD`/`AUDIT_READER_PASSWORD` (grants substitution, `database` Infra §3.2); the doc's ENV-SHAPES lists exactly these among the six Phase-1 required shapes; ordering = env set → migration release step → traffic. Same set, they agree.
- **INFRA-DEP-Fold-3 [check iii]** — the Grafana dashboard-as-code file is **pinned 1:1 to observability's FROZEN five-metric panel topology, no drift**: decision latency · decisions by recommendation type · rule-evaluation duration · LLM-call errors · outlier-flag rate; datasource Prometheus; demographic-free. **observability owns the panel topology (authority); deploy-config owns the committed file that REALIZES it** (reference-not-own) — a panel not in observability's five is out of scope; the five are named explicitly. The exact JSON is a Code-Gen deliverable bound to this topology.

**PART 2 GENERATED — 2 artifacts** at `guide-docs/build/deploy-config/infrastructure-design/`:
- **`infrastructure-design.md`** — §1 component→infra mapping **C-DEP-1..5** (C-DEP-2..5 realized as free-tier cloud topology; C-DEP-1 CI/test logic); §2 the mandatory **SEVEN-category** infra sweep (Deployment CORE · Storage reference-database's · Compute the Render service · Messaging N/A · Networking the Vercel rewrite · Monitoring the observability deployment half · Shared narrow-reference); §3 the **deferred-halves topology** (3.1 Render free-tier Web Service, Python 3.12 pinned, `uvicorn backend.app.main:app`, six Settings env + `GEMINI_API_KEY` dummy · 3.2 Vercel Vite static build → `dist` mounting frozen `App.jsx` · 3.3 the **Vercel rewrite/proxy, no-CORS, no-backend-edit** + Fold-1 · 3.4 DB reference + the Render **migration release step** + Fold-2 · 3.5 the env manifest **full shape table**, shapes only · 3.6 the observability deployment half — Prometheus scrape + the Grafana **dashboard-as-code file 1:1 to the frozen five panels** + Fold-3 + Langfuse, **live callback NOT here** · 3.7 the deploy doc topology, DOC-1 tokens); §4 secrets-config contract shapes-only; §5 reference boundaries; §6 constraints.
- **`deployment-architecture.md`** — §1 three-tier topology table · §2 request/deploy flow · §3 the Vercel rewrite connectivity · §4 migration release step + DB · §5 the observability deployment half · §6 the **validated deployment-topology Mermaid** (rectangle-only, alphanumeric IDs, quoted labels — no hyphens/semicolons/colons/parentheses/special chars, 3 balanced subgraph/end pairs, dashed `traces`/`values`/`topology`/`deferred` edges) + **full text alternative** · §7 settled items held.

**NO key/endpoint/connection VALUES anywhere** — shapes only (incl. `RENDER_BACKEND_URL` a non-secret public-host shape). **NO separate `shared-infrastructure.md`** (Q7-A).

**`deploy-config` (U23) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED → STOPPED at the Infrastructure-Design 2-option completion gate** · Code Generation ⏳. **5th of 6 Phase-2 units; 4 of 5 stages complete pending gate; the 3rd real non-skip Infrastructure Design after `database` + `observability`.**

**Register (unchanged)**: 21 of 23 units complete; U23 at its 4th stage; **1 P2 remains beyond U23: `llm-judge` (U22)**; composition-root Q1-B divergence OPEN (deployed as-built + documented, §3.7); R2–R5 unwired (R4 a `501` stub; core demo path not runnable end-to-end); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (application-integration, NOT U23's); **`OBS-SINK-DEFERRED` OPEN** — this stage DESIGNED its deployment half (Prometheus scrape + Grafana dashboard-as-code file + Langfuse provisioning + `LANGFUSE_*` env); the **code-attachment half stays composition's**, AC-7 provisioned-for not discharged; `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code**; **no `backend/deploy_config/`**; **`requirements.txt` / `package.json` NOT edited**; **no frozen unit edited**; the **CLOSED composition root NOT edited** (the Vercel rewrite keeps CORS out of the backend); **`database`'s + `observability`'s Infra referenced, not re-opened**; **WIRE-1 · the 17 P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `observability` (U21) UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. Files written: the plan (answers + §3.5 folds + gate) + the **2 new Infrastructure Design artifacts**. **STOPPED** at the Infrastructure Design 2-option completion gate (1. Request Changes / 2. Continue → Code Generation).

## 🧩 BUILD → `deploy-config` (U23) — **Infrastructure Design APPROVED (Continue)** → Code Generation Part 1 (Plan) WRITTEN; STOP at the plan-file gate — 2026-07-19

**Infrastructure Design APPROVED 2026-07-19 (option 2, Continue → Code Generation)** — U23's Infrastructure Design **COMPLETE** (2 artifacts frozen: `infrastructure-design.md` + `deployment-architecture.md`; **INFRA-DEP-Fold-1..3**). Gate **closed**. U23 advanced to **Code Generation — the 5th and LAST of its 5 stages**. Wrote **Part 1 (Plan) ONLY**: `guide-docs/build/plans/deploy-config-code-gen-plan.md`. **NO code/config; no files created.** **Depth: comprehensive.**

**⚑ DEP-D8 deferrals RESOLVED on disk**: **(1)** `frontend/package.json`'s own description reads *"Bundler/dev-server + Vercel topology deferred to deploy-config (D6)"* — so adding the build entry + a `build` script is the **SANCTIONED** deploy-config deliverable, **NOT** a frozen-unit edit (`package.json` is shared config, like the `vitest`/`eslint` configs the composition-root pass extended); **(2)** **`vite` is ALREADY installed** (transitive via `vitest`) → **NO new frontend dependency**; **(3)** `pytest testpaths=["backend"]` → the scans must live under `backend/` → a **test-only `backend/deploy_config/`** package (no production `.py`; the deployable artifacts are declarative config at platform-conventional homes); **(4)** `.env.example` is `secrets-config`'s frozen artifact → **referenced, never edited**.

**§2 component→artifact map (DEP-D8 RESOLVED — final locations)**: **C-DEP-2** `render.yaml` at repo **ROOT** (Render Blueprint — web service, `env: python`, `buildCommand: pip install -r requirements.txt`, `startCommand: uvicorn backend.app.main:app`, `plan: free`, `preDeployCommand` the migration release step, `envVars` names-only `sync: false`) · **C-DEP-3** `frontend/vercel.json` (build + `rewrites` `/api`→`RENDER_BACKEND_URL`) + `frontend/index.html` + `frontend/src/main.jsx` (mounts frozen `App.jsx`) + `frontend/vite.config.js` + a `build` script in `frontend/package.json` · **C-DEP-4** the `render.yaml` `envVars` block + the deploy doc ENV-SHAPES section (references frozen `.env.example`) · **C-DEP-5** `deploy/README.md` · **observability deployment half** `deploy/grafana-dashboard.json` (one dashboard, 5 panels 1:1 to observability's frozen metrics) + `deploy/prometheus-scrape.yml` · **C-DEP-1** `backend/deploy_config/` `__init__.py` + `tests/{__init__.py, structural.py, test_*.py}` (**TEST-ONLY**, no production `.py`).

**§3 TDD test→target map — all eleven `NFR-DEP-*`, NO ORPHAN**: **NOEDIT-1 / SEC3-1 / ROUTES-1 load-bearing full-highest** with detector self-tests (ROUTES-1 = `create_app().openapi()["paths"]` in-process, no server/DB/env, reusing the composition-root technique) · **DOC-1** token-set checklist · **BUILD-1/BOOT-1** honest two-part (presence + named deploy-time fact left untested) · **FREETIER-1/SCOPE-1** + detector · **format** (P-DEP-8) `pyyaml`/`json` · **ADVISORY-1+SEC-1** governance · **PERF-1** observed folded; the **Fold-3 five-panel no-drift assertion** on the Grafana file. **§4** leaf-first build order (`structural.py` substrate → `render.yaml` → frontend build entry → grafana dashboard + scrape → `deploy/README.md` → the load-bearing scans + governance → coverage gate). **§6** explicit HOLDS. **§7** the declarative-unit coverage gate.

**SIX `[Answer]` questions, all BLANK** (rec **A** throughout): **Q1** final file locations DEP-D8 resolves (render.yaml root · `frontend/` for vercel+build entry · `deploy/` for doc+dashboard+scrape · env shapes in render.yaml+doc referencing frozen `.env.example` · test-only `backend/deploy_config/`) · **Q2** the frontend build entry + `package.json` `build` script (add `index.html` + `src/main.jsx` mounting frozen `App.jsx` + `vite.config.js` + a `"build":"vite build"` script; **vite already present, NO new dependency**; the script is the sanctioned deliverable the description reserves, not a frozen edit) · **Q3** DOC-1 token literals (`ROUTE-STATUS:`/`Q1-B-DIVERGENCE:`/`AC-7-CONTINGENCY:`/`FREE-TIER:`/`ENV-SHAPES:`) · **Q4** SEC3-1 secret-value regex (flag `sk-`/`pk-`/`postgresql://user:pass@`/`NAME=value`; **PERMIT** bare name shape + the **public `RENDER_BACKEND_URL` host** per Fold-1; detector self-test) · **Q5** render.yaml/vercel.json key structures · **Q6** test integration + coverage meaning (scans integrate into the **existing** backend pytest run via `testpaths=["backend"]`; **NO `--cov=backend/deploy_config`** since no production `.py` — a coverage % does not meaningfully apply; the gate is the scans **PASS** against the committed artifacts; global `--cov-fail-under=90` holds unchanged; **1153/31 additive, zero regression**).

**`deploy-config` (U23) stage status**: **FD ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure Design ✓ · Code Generation ⏳ Part 1 (Plan) WRITTEN → STOPPED at the plan-file gate** (ambiguity-check after answers; Part 2 = the config artifacts + `backend/deploy_config/tests/` scans, on explicit go). **5th of 6 Phase-2 units; 5 of 5 stages engaged; this is the LAST stage — its approval closes the U23 loop and completes the 5th of 6 Phase-2 units.**

**Register (unchanged)**: 21 of 23 units complete; U23 at its 5th/last stage; **1 P2 remains beyond U23: `llm-judge` (U22)**; composition-root Q1-B divergence OPEN (deployed as-built + documented); R2–R5 unwired (R4 a `501` stub; core demo path not runnable end-to-end); tier-B UNAUTHORIZED (N/A); `audit_store` Docker-guard gap DEFERRED; `OUTLIER-IN-PROSE` OPEN; `MCP-TRANSPORT-DEFERRED` OPEN (application-integration, NOT U23's); `OBS-SINK-DEFERRED` OPEN (deployment half DESIGNED by U23's Infra; code half composition's; AC-7 provisioned-for not discharged); `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **NO code/config**; **no files**; **no frozen unit or composition-root file edited** (the Vercel rewrite lives in `frontend/vercel.json`, NOT `backend/app/main.py`); **`database`'s + `observability`'s Infra referenced, not re-derived**; **no new dependency** (`pyyaml` floored, `vite` already installed, stdlib `json`/`ast`/`pathlib`); **no secret values** — shapes only (`RENDER_BACKEND_URL` a non-secret public host, Fold-1); the Grafana **5 panels exactly match observability's frozen topology, no drift**; **R2–R5 stay `501`**; **WIRE-1 · the 17 P1 units · `outlier-model` (U18) · `ui-outlier-view` (U20) · `memo-extensions` (U19) · `observability` (U21) UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors to stay unchanged); **no other unit started**; the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1–Q6.

## ðŸ§© BUILD â†’ `deploy-config` (U23) â€” Code Generation Part 2 **GENERATED + VERIFIED** (resumed after usage-limit interruption); STOP at the Code-Generation 2-option gate â€” 2026-07-19

**Q1â€“Q6 all A** (embedded in the plan Â§5) Â· **ambiguity-check RAN (Â§5.5) â†’ CLEAN (2 folds; no surface-and-stop)** â€” `CG-DEP-Fold-1` (the `/api` rewrite is correct via deploy-config's OWN `main.jsx` supplying the frozen transport's injectable `baseUrl` ctor arg â€” no frozen edit) + `CG-DEP-Fold-2` (`DEPLOY-MIGRATE-DEFERRED` â€” `preDeployCommand` wires WHEN, the runnable CLI entrypoint is database's/composition's, reference-not-own).

**âš‘ RESUMPTION NOTE (why this entry is back-annotated).** A prior session generated **all** of Part 2 (13:19:31 â†’ 13:35:14) but was **interrupted by a usage limit before the two logging steps ran** â€” `guide-state.md` + `audit.md` were left stamped **13:06:52**, i.e. ending at *"Code Generation Part 1 (Plan) WRITTEN"*. This session **re-established ground truth by mtime forensics + live measurement rather than assumption** (the repo's `backend/`/`frontend/`/`deploy/`/`render.yaml` are wholesale **untracked**, so `git diff` gives no granularity), found **every artifact already complete, coherent, and passing**, **regenerated NOTHING**, and closed only the two missing logging steps. The write sequence recovered from disk matches the plan's **Â§4 leaf-first order exactly**; **nothing half-written, nothing broken, no test referencing a missing config nor vice versa**.

**PART 2 GENERATED â€” the Â§2 componentâ†’artifact map, DEP-D8 fully RESOLVED on disk**:
- **C-DEP-2** `render.yaml` (repo **root**, Render Blueprint) â€” `type: web`, `runtime: python`, **`plan: free`**, `buildCommand: pip install -r requirements.txt`, `startCommand: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`, `preDeployCommand` (the migration release slot), **`envVars` names-only `sync: false`** (Phase-1 six + Phase-2 reserved `LANGFUSE_*`/`ANTHROPIC_API_KEY`/`OLLAMA_HOST`).
- **C-DEP-3** `frontend/vercel.json` (`buildCommand: npm run build`, `outputDirectory: dist`, **`rewrites` `/api/:path*` â†’ the backend host**) + `frontend/index.html` + **`frontend/src/main.jsx`** (constructs `createHttpTransport({ baseUrl: '/api', userId })` + `createSeams(transport)` and mounts the **frozen `App.jsx`** in `StrictMode`) + `frontend/vite.config.js` + **only** a `"build": "vite build"` script added to `frontend/package.json`.
- **C-DEP-4** the `render.yaml` `envVars` block + `deploy/README.md` **ENV-SHAPES** (references the frozen `.env.example`, **never edits it**).
- **C-DEP-5** `deploy/README.md` â€” the honest partial-deploy doc, **all five DOC-1 tokens present** (`ROUTE-STATUS:` L15 Â· `Q1-B-DIVERGENCE:` L22 Â· `AC-7-CONTINGENCY:` L28 Â· `FREE-TIER:` L35 Â· `ENV-SHAPES:` L40) + a **MIGRATION (DEPLOY-MIGRATE-DEFERRED)** section (L54â€“56).
- **observability deployment half** `deploy/grafana-dashboard.json` (**one dashboard, exactly five panels**) + `deploy/prometheus-scrape.yml`.
- **C-DEP-1** `backend/deploy_config/` â€” `__init__.py` + `tests/{__init__.py, structural.py, + the ten test_*.py}`, **TEST-ONLY** (no production `.py`), collected by the existing `testpaths=["backend"]`.

**Â§3 testâ†’target map â€” all eleven `NFR-DEP-*` covered, NO ORPHAN, 41 scans**: `test_noedit.py` **5** (**NOEDIT-1 LOAD-BEARING full-highest** â€” allowlist vs frozen-path classifier + additive-`package.json` + detector self-test) Â· `test_sec3.py` **4** (**SEC3-1 LOAD-BEARING** â€” credential-value regex over every committed U23 artifact; **non-vacuous permit** side: bare NAME shape + the public `RENDER_BACKEND_URL` host allowed, Fold-1) Â· `test_routes.py` **4** (**ROUTES-1 LOAD-BEARING** â€” `create_app().openapi()["paths"]` **in-process, no server/DB/env**, == the 7 frozen route templates, no new route file, import-to-read â‰  edit) Â· `test_doc.py` **3** Â· `test_build.py` **6** Â· `test_boot.py` **5** Â· `test_freetier.py` **3** Â· `test_scope.py` **4** (incl. the **Fold-3 five-panel no-drift** assertion vs observability's `METRIC_DEFINITIONS`) Â· `test_format.py` **4** (P-DEP-8 `pyyaml`/`json`) Â· `test_governance.py` **3** (ADVISORY-1 + SEC-1 + PERF-1 observed-folded). Two scans that initially **self-matched their own token literals** were rewritten to **AST import detection** â€” the same fix pattern as observability's TIERU scan.

**âš‘ MEASURED THIS SESSION (not assumed â€” the resume instruction required re-running)**: `python -m pytest` â†’ **1194 passed / 31 skipped / 5 errors** (50.35s). The **5 errors are the pre-existing `audit_store` Docker-absence** ones (`test_pg_integration.py`) â€” **UNCHANGED**. Against the true pre-U23 baseline **1153 passed / 31 skipped** â†’ **+41 additive, ZERO regression**. **Coverage 99.85%**, *"Required test coverage of 90% reached"* â†’ the global **`--cov-fail-under=90` HOLDS**, and **NO `--cov=backend/deploy_config` line added** (declarative unit, no production `.py`; a coverage % does not meaningfully apply â€” **Q6-A**). Isolated: `pytest backend/deploy_config` â†’ **41 passed against the REAL committed artifacts, not stand-in fixtures**. Frontend re-measured independently: **682 passed / 137 files**, **ESLint exit 0**.

**âš‘ The two explicit confirmations**: **(i)** `frontend/vercel.json`'s rewrite mechanism **NEVER touches `backend/app/main.py`** â€” it lives entirely in the Vercel config; `main.py` mtime **16-07-2026 12:22:39** (three days older than U23's 13:19 window, untouched); **no CORS anywhere in `backend/app/*.py`**; neither `render.yaml` nor `vercel.json` names `main.py` as a write target; `App.jsx` untouched (16-07-2026 12:39:09) â€” `main.jsx` only **imports** it. **(ii)** The Grafana file's **five panels exactly match observability's frozen metric topology â€” no drift, no sixth panel**: *decision latency Â· decisions by recommendation type Â· rule-evaluation duration Â· LLM-call errors Â· outlier-flag rate*, datasource **Prometheus**, **no demographic label** (CON-BR1) â€” 1:1 against observability's `infrastructure-design.md` frozen panel table (L99â€“107).

**`deploy-config` (U23) stage status**: **FD âœ“ Â· NFR Requirements âœ“ Â· NFR Design âœ“ Â· Infrastructure Design âœ“ Â· Code Generation âœ“ Part 1 ANSWERED + ambiguity-check CLEAN + Part 2 GENERATED & VERIFIED â†’ STOPPED at the Code-Generation 2-option completion gate.** **5 of 5 stages complete pending this final gate** â€” its approval **closes the `deploy-config` per-unit loop** and completes the **5th of 6 Phase-2 units**.

**Register**: **22 of 23 units complete on approval** (21 complete + U23 at its final gate); **1 P2 remains beyond U23: `llm-judge` (U22)** â€” the only unit left in the entire 23-unit decomposition; composition-root **Q1-B divergence OPEN** (deployed as-built + documented, DOC-1 token in the deploy doc); **R2â€“R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end); **tier-B UNAUTHORIZED (N/A)**; **`audit_store` Docker-guard gap DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN** (application-integration, NOT U23's â€” SCOPE-1 asserts no MCP module); **`OBS-SINK-DEFERRED` OPEN** â€” U23 **discharged its deployment half** (scrape + dashboard-as-code file + `LANGFUSE_*` env shapes); the **code-attachment half stays composition's**, AC-7 **provisioned-for not discharged**; **`DEPLOY-MIGRATE-DEFERRED` NEW/OPEN** â€” `preDeployCommand` wires WHEN, the runnable migration CLI entrypoint is database's/composition's (`backend/database/migrate.py` correctly ABSENT); `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **no frozen unit or composition-root file edited** (the Vercel rewrite lives in `frontend/vercel.json`, **never** `backend/app/main.py` â€” no CORS in the backend); `main.jsx` **imports** the frozen `App`/`seams`/`httpTransport`, edits none; **`database`'s + `observability`'s Infra referenced, not re-derived** (the migration runner is database's; the panel topology is observability's); **no new dependency** (`pyyaml` floored, `vite` already installed transitively via `vitest`, stdlib `json`/`ast`/`pathlib`); **`requirements.txt` NOT edited**; `frontend/package.json` gained **only** the `build` script (the **sanctioned** deliverable its own description reserves for D6); **no secret/key/URL VALUES committed** â€” shapes only (`RENDER_BACKEND_URL` a non-secret public host, Fold-1); **R2â€“R5 stay `501`**; **WIRE-1 Â· the 17 frozen P1 units Â· `outlier-model` (U18) Â· `ui-outlier-view` (U20) Â· `memo-extensions` (U19) Â· `observability` (U21) UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched** (31 skips + 5 Docker errors unchanged); **no other unit started**; the **23-unit decomposition unchanged**. Files written **this session**: **only** the `audit.md` append + this `guide-state.md` back-annotation (Part 2's artifacts + `code-summary.md` + `testresults.txt` were already on disk from the interrupted session, verified accurate â€” **nothing regenerated**). **STOPPED** at the Code Generation 2-option completion gate (1. Request Changes / 2. Continue).

## ðŸ§© BUILD â†’ `deploy-config` (U23) â€” **Code Generation APPROVED (Continue)** â†’ **U23 COMPLETE (5/5 stages)** â€” the **22nd** complete build-loop unit overall, the **5th of 6** Phase-2 units â€” 2026-07-19

**Code Generation APPROVED 2026-07-19T14:21:06Z (option 2, Continue)** â€” the gate is **CLOSED** and the **`deploy-config` per-unit loop is COMPLETE**. All five stages done: **FD âœ“ Â· NFR Requirements âœ“ Â· NFR Design âœ“ Â· Infrastructure Design âœ“ (the 3rd REAL non-skip in the build, after `database` and `observability`) Â· Code Generation âœ“.** U23 is the **22nd complete build-loop unit overall** and the **5th of the 6 Phase-2 units (U18â€“U23)**.

**Final verified numbers (measured, not assumed)**: backend **1194 passed / 31 skipped** â€” 1153 baseline **+ 41 new**, **ZERO regression**; the **5 pre-existing `audit_store` Docker-absence errors UNCHANGED**. Frontend **682 passed / 137 files** unchanged, **ESLint exit 0**. Global **`--cov-fail-under=90` held at 99.85%**, with **NO meaningless `--cov=backend/deploy_config` line added** (a declarative unit has no production `.py` to measure â€” **Q6-A**). **All eleven `NFR-DEP-*` scans (41 tests) verified against the REAL committed artifacts, not stand-in fixtures**; the load-bearing trio **NOEDIT-1 Â· SEC3-1 Â· ROUTES-1** ran at **full-highest rigor** with detector self-tests.

**What U23 delivered** â€” the **first unit in the build whose deliverables are DECLARATIVE CONFIG rather than code**: `render.yaml` (repo root, Render Blueprint, `plan: free`, names-only `envVars`) Â· `frontend/vercel.json` + the build entry (`index.html`, `src/main.jsx`, `vite.config.js`, a `build` script) **mounting the frozen `App.jsx` unmodified** Â· `deploy/README.md` (five DOC-1 tokens) + `deploy/grafana-dashboard.json` + `deploy/prometheus-scrape.yml` Â· a **test-only** `backend/deploy_config/`. **Verified end-to-end**: the **Vercel rewrite mechanism never touches `backend/app/main.py`** (no CORS in the backend; the **closed composition root untouched**), and the Grafana file's **five panels exactly match `observability`'s frozen metric topology with no drift**.

**âš‘ Clean session-interruption recovery (recorded)**: the prior session was cut by a **usage limit** mid-stage, having written every artifact but **neither log entry**. This session **re-established ground truth by mtime forensics + a live pytest run rather than assumption** (`backend/`/`frontend/`/`deploy/`/`render.yaml` are wholesale **untracked**, so `git diff` gave no granularity). All artifacts were found **already complete, coherent, and passing** â€” **nothing regenerated**, **only the two missing log entries written**. The code-gen plan already carried all six `[Answer]: A` tags and `testresults.txt` already reproduced the live numbers exactly; both were **correctly left untouched** rather than rewritten with identical content.

**âš‘ NEW OPEN REGISTER ITEM â€” `DEPLOY-MIGRATE-DEFERRED`**: `render.yaml`'s `preDeployCommand` wires **WHEN** `database`'s forward-only, idempotent migration sequence runs (before traffic), but references a **runner with no CLI entrypoint yet** â€” `MigrationRunner` is a class needing an injected `sa.Engine`, and `backend/database/migrate.py` is **ABSENT**. The runnable entrypoint is **`database`'s / composition's** deliverable (**reference-not-own**). Carried **analogously to AC-7's provisioned-for-not-discharged** pattern and **honestly disclosed** in `deploy/README.md` (MIGRATION section). The scans check the field **shape**, never execute it â€” no scan is broken; the gap is **documented, not hidden**.

**FULL REGISTER â€” Deferred Decisions / cross-cutting constraints (current)**:
- **23-unit decomposition UNCHANGED** â€” **22 of 23 units complete**; **ONE remains: `llm-judge` (U22)**, the **6th and final Phase-2 unit** and the last unit in the entire decomposition.
- **Composition-root `Q1-B` divergence â€” OPEN** (deployed as-built + documented; the `Q1-B-DIVERGENCE:` DOC-1 token now carried in `deploy/README.md`).
- **R2â€“R5 still UNWIRED** â€” **R4 still a `501` stub**; the **core underwriting demo path is still NOT runnable end-to-end** (ROUTES-1 asserts R2â€“R5 stay `501`).
- **tier-B corpus run â€” still UNAUTHORIZED**, and **confirmed N/A to every unit built so far**.
- **`audit_store` Docker-guard hygiene gap â€” still DEFERRED** (the 31 skips + 5 Docker-absence errors, unchanged).
- **`OUTLIER-IN-PROSE` â€” still OPEN and UNASSIGNED.**
- **`MCP-TRANSPORT-DEFERRED` â€” still OPEN, non-blocking** (application-integration, not U23's; SCOPE-1 asserts no MCP module).
- **`OBS-SINK-DEFERRED` â€” still OPEN**: the **live Langfuse/Prometheus/Grafana code-attachment half** remains **composition's** (AC-7 provisioned-for not discharged), **though U23 has now REALIZED the deployment half as committed config** (scrape + dashboard-as-code + `LANGFUSE_*` env shapes).
- **`DEPLOY-MIGRATE-DEFERRED` â€” NEW, OPEN** (disclosed above).
- **`testresults.txt` append-vs-overwrite â€” still OPEN housekeeping.**

**Guardrails held**: **NOTHING STARTED**; no unit begun; **WIRE-1 UNTOUCHED**; the **17 frozen P1 units UNTOUCHED**; **`outlier-model` (U18) Â· `ui-outlier-view` (U20) Â· `memo-extensions` (U19) Â· `observability` (U21) UNTOUCHED**; the **CLOSED composition root UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap UNTOUCHED**; `requirements.txt` NOT edited; no new dependency; no secret VALUES committed (shapes only). Files written for this approval: the `guide-state.md` **top `Current Stage` splice** (prior U21 status preserved behind a `<!-- superseded U21-completion status below -->` marker; the unrelated mid-file historical `Current Stage` occurrence deliberately left untouched) + this completion line + the append-only `audit.md` entry. **STOPPED â€” the next move is the user's.**

## ðŸ§© BUILD â†’ `llm-judge` (U22) â€” FD Part 1 **ANSWERED (Q1â€“Q6 all A)** + mandatory ambiguity-check **RAN â†’ NOT CLEAN (2 folds RESOLVED + 1 GENUINE GAP)** â†’ **SURFACED AND STOPPED; NO FD artifact** â€” 2026-07-19

**Q1â€“Q6 all A** (embedded in the plan Â§5). **Mandatory ambiguity-check RAN (Â§5.5)** against the six answers + the frozen
substrate (`unit-of-work.md` L249/Â§4 Â· `unit-of-work-dependency.md` L51/L200 Â· U4's frozen schemas + `PromptBuilder` Â·
U19's frozen adapters + the FR-PROV-GATE-1/2 split Â· U21's frozen five metrics Â· the actual on-disk promptfoo shim
behaviour Â· U18's `CorpusSource` fixture precedent) â€” grounded in **disk measurement, not inference**.

**âš‘ RESULT: NOT CLEAN â€” 2 folds RESOLVED + 1 GENUINE GAP â†’ SURFACE-AND-STOP. NO FD artifact generated.**

- **âœ… CG-JUDGE-Fold-1 [check (i)] â€” the two deferrals are GENUINELY SEPARABLE: TWO distinct register items, DIFFERENT
  discharge conditions, one-way prerequisite edge â€” NOT the same deferral twice.** The naive reading (*"the live run needs
  both the corpus and the CLI simultaneously, so it is one item"*) is **refuted by asymmetry**:
  **`PROMPTFOO-CLI-DEFERRED` is independently dischargeable WITHOUT the corpus and WITHOUT tier-B** â€” install/pin the Node
  CLI, configure telemetry opt-out, bind the `RubricEngine` adapter, verify end-to-end **against the Q1-A seeded fixtures**
  (a real, independently valuable state reachable while tier-B stays unauthorized). The converse fails:
  **`JUDGE-EVAL-DEFERRED`** cannot discharge without a working engine (Q3-C's in-house scorer was rejected), so it
  **depends on** the CLI item. **Discharge conditions** â€” `PROMPTFOO-CLI-DEFERRED`: Node+npx present, CLI **pinned**,
  telemetry opt-out, adapter bound, verified on fixtures (**no corpus, no tier-B, no live key**). `JUDGE-EVAL-DEFERRED`:
  **tier-B corpus authorized + built** AND live Gemini+Claude keys AND the â‰¥4/5 gate actually evaluated over real memos,
  with the CLI item as **prerequisite**. Precedent: `OBS-SINK-DEFERRED`'s deployment-half/code-half split. No user decision
  needed.
- **âœ… CG-JUDGE-Fold-2 [check (iii)] â€” the Ollama-exemption fixture needs REAL TEETH, and this is NOT an analogy to U19: a
  FROZEN U19 ARTIFACT ASSIGNS THE DUTY TO U22 BY NAME.** `backend/memo_extensions/tests/test_provgate.py` docstring
  (**verbatim on disk**): *"Governance note (NOT a code test): Ollama's ABSENCE from the groundedness/promptfoo target set
  (AC-6 / QA-4 / FR-PROV-GATE-2) is a **tooling-config fact owned by `llm-judge` (U22)**, recorded as an **explicit,
  documented exemption â€” never implicit, and not asserted here**."* U19 **deliberately declined** to assert it and handed
  it to U22. â‡’ A fixture set of **only** Gemini+Claude samples would prove the exclusion **VACUOUSLY**. **The fixture set
  MUST contain â‰¥1 Ollama-sourced sample PRESENT in the assembled set but DEMONSTRABLY EXCLUDED from the scored/aggregated
  set** â€” the non-vacuity discipline of SEC3-1's permit-side detector self-test. U19 also fixes the **boundary**: Ollama is
  exempt from **memo-quality gates only** and **still holds the decision-level gates** (`temperature=0`, CON-BR2-TYPE) â€” so
  the fixture excludes it from **scoring**, never characterises it as untested. No user decision needed.
- **â›” CG-JUDGE-GAP-1 [check (ii)] â€” GENUINE GAP.** **QA-4's few-shot reference-memo anchoring is NOT IMPLEMENTED ANYWHERE
  IN THE CODEBASE**, and **U22 structurally CANNOT implement it without editing the frozen U4** â€” which the guardrails
  forbid. **Measured**: a repo-wide scan of `backend/**/*.py` for `few.?shot|reference_memo|reference memo` returns **ZERO
  HITS**; U4's frozen `PromptBuilder` (read in full) builds the prompt from `MemoAgentInput` **and nothing else** (system
  prompt + read-only recommendation + read-only confidence + rule report + non-demographic facts) â€” **no reference memo, no
  few-shot exemplars**. The clause exists **only** as an unrealized requirement in **exactly two places**:
  `requirements.md` **L206** (QA-4) and `stories.md` **L622** (US-PLAT-10's third bullet). **Why it cannot be improvised**:
  anchoring is a **GENERATION-side** mechanism (exemplars supplied when the memo is **drafted** = U4's `PromptBuilder`),
  but **Q2-A** fixes U22 as **strictly downstream, read-only, editing neither U4 nor U19**. Two coherent readings lead to
  **materially different FD artifacts** (score anchoring-consistency as a rubric dimension **vs** treat the clause as wholly
  out of scope) â€” and **either way an unimplemented acceptance-adjacent requirement has been discovered: QA-4 is only HALF
  realizable by U22 as scoped**. **Escalated as NEW Question 7 (Â§5.6), options A/B/C/D, BLANK â€” this BLOCKS Part 2.**

**`llm-judge` (U22) stage status**: **Functional Design â³ Part 1 ANSWERED (Q1â€“Q6 all A) + ambiguity-check RAN â†’ NOT CLEAN â†’
STOPPED at the ambiguity-check on `CG-JUDGE-GAP-1`, awaiting the Q7 decision.** **NO FD artifact**
(`guide-docs/build/llm-judge/functional-design/` remains **ABSENT**). The **FD 2-option completion gate was NOT presented** â€”
there is nothing to gate on; the stage stopped at the check per the standing *"flag and stop, do not improvise"* discipline.
**U22 is the 6th and FINAL Phase-2 unit and the LAST unit in the entire 23-unit decomposition**; 22 of 23 units complete.

**Register**: 22 of 23 units complete; **1 remains: `llm-judge` (U22)**, at its 1st stage, blocked on Q7. Composition-root
**Q1-B divergence OPEN**; **R2â€“R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end); **tier-B
UNAUTHORIZED**; **`audit_store` Docker-guard gap DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN**;
**`OBS-SINK-DEFERRED` OPEN** (deployment half realized by U23; code half composition's); **`DEPLOY-MIGRATE-DEFERRED` OPEN**;
`testresults.txt` append-vs-overwrite open housekeeping. **PROPOSED-but-not-yet-adopted (pending Q7 / FD Part 2)**:
**`JUDGE-EVAL-DEFERRED`** Â· **`PROMPTFOO-CLI-DEFERRED`** (separable per Fold-1, with a prerequisite edge) Â·
**`FEWSHOT-ANCHOR-UNIMPLEMENTED`** (the Q7-A/B candidate name for the discovered gap).

**Guardrails held**: **NO FD artifact**; **no code**; **no `backend/llm_judge/`** (ABSENT); **`requirements.txt` NOT
edited**; **no new dependency**; **WIRE-1 untouched**; the **17 frozen P1 units untouched** â€” **U4 read-only, NOT edited,
which is precisely the substance of the gap**; **`outlier-model` (U18) Â· `memo-extensions` (U19) Â· `ui-outlier-view` (U20) Â·
`observability` (U21) Â· `deploy-config` (U23) untouched**; the **CLOSED composition root untouched**; **tier-B NOT
authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition
unchanged**. Files written: the plan (Â§5 answers + Â§5.5 ambiguity-check + Â§5.6 the new Q7) + the append-only `audit.md`
entry + this state entry. **STOPPED awaiting the Q7 decision.**

## ðŸ§© BUILD â†’ `llm-judge` (U22) â€” **Q7 ANSWERED (A)** + ambiguity-check **RE-RUN â†’ CLEAN (CG-JUDGE-Fold-3)** + **FD Part 2 GENERATED (3 artifacts)**; STOP at the FD 2-option gate â€” 2026-07-19

**Q1â€“Q7 all A** (embedded in the plan Â§5/Â§5.6). **Ambiguity-check RE-RUN (Â§5.7) â†’ CLEAN â€” 1 new fold, no surface-and-stop.**

- **âœ… CG-JUDGE-Fold-3 [the Q7-A reference-memo question] RESOLVED.** The question is **real** â€” anchoring-consistency
  cannot be scored without a reference. Resolved on three grounded points: **(1) nothing exists to reuse, and reuse would
  be forbidden anyway** â€” scanned on disk, **no shared/golden memo fixture exists**;
  `backend/memo_agent_core/tests/` has **no `fixtures.py`** (unlike `memo_extensions`), and U4's tests construct
  `DecisionMemo` **ad-hoc inline** (`test_schemas.py` L44, `test_memo_hash_adapter.py` L38) â‡’ U22 hand-authors its own, and
  it must **NOT** be added to U4's test tree (that would be a frozen-unit edit); **(2) âš‘ the decisive distinction â€”
  comparison TARGET vs prompt INPUT**: the reference memo is a **scoring comparison target held by the judge**, **not** a
  prompt input â€” **U4 never sees it**. Few-shot anchoring would require passing exemplars **INTO** `PromptBuilder` at draft
  time, which is precisely the forbidden U4 edit and exactly what Q7-A does **not** do â‡’ **Q7-A is structurally compatible
  with Q2-A and the frozen-P1 guardrail**, the two halves of QA-4 separating cleanly **by direction of data flow**;
  **(3) construction is import-to-read, not edit** â€” built via the imported frozen `DecisionMemo` schema (fields read on
  disk: `narrative_prose` L Â· `cited_rule_ids` L Â· `missing_information` D Â· `recommendation` RO Â· `confidence` RO Â·
  `memo_hash` M Â· `model_version` M); instantiating a frozen model is **using** it. **Two constraints pinned so Part 2
  cannot drift**: the judge scores the **`narrative_prose` (L) region ONLY** (judging D/RO/M would re-open CON-BR2-TYPE),
  and per QA-4's *"not claimed bit-identical"* the reference is a **STYLE/STRUCTURE exemplar** â€” **ONE canonical reference**
  for the whole fixture set, itself advisory-only and demographic-free.

**PART 2 GENERATED â€” 3 artifacts** at `guide-docs/build/llm-judge/functional-design/`:
- **`domain-entities.md`** â€” `GroundednessRubric` (threshold **4**, scale **5**) + `RubricDimension` with the **two
  dimensions** (`groundedness` per AC-2/AC-6 Â· `anchoring_consistency` per Q7-A) Â· `JudgedSample` Â· **`ReferenceMemo`** with
  the full Fold-3 resolution table Â· **`ProviderScopeTag`** (gemini/claude **IN-GATE**, ollama **EXEMPT**, quoting U19's
  by-name assignment verbatim) Â· `DimensionScore`/`SampleScore` Â· **`EvalRunResult`** with **`exempt_count` as the
  load-bearing non-vacuity witness** Â· the **`RubricEngine` Protocol** Â· the **explicit reference-not-own table** Â· and the
  honest-scope note on `FEWSHOT-ANCHOR-UNIMPLEMENTED`.
- **`business-rules.md`** â€” **BR-JUDGE-1..11**, each **grounded + checkable with its tier**: â‰¥4/5 with explicit `>=`
  boundary cases (1) Â· Gemini+Claude in-gate, **GATE-1 explicitly left to `quality-gates`** (2) Â· **Ollama exemption with
  NON-VACUOUS teeth + detector self-test, `exempt_count == 0` itself a failure signal** (3) Â· **exempt â‰  untested** (4) Â·
  anchoring-consistency with **paired close/divergent fixtures** (5) Â· **`FEWSHOT-ANCHOR-UNIMPLEMENTED` disclosed with the
  zero-hit scan evidence** (6) Â· advisory-only, verdict **structurally unrepresentable** (7) Â· **`PROMPTFOO-CLI-DEFERRED`**
  with the npx-unpinned-fetch + posthog-telemetry disclosure (8) Â· **`JUDGE-EVAL-DEFERRED`** with the U18 dual-source
  precedent (9) Â· no demographic input + detector (10) Â· **NOEDIT + no new metric** (11) Â· plus a **no-orphan traceability
  table**.
- **`business-logic-model.md`** â€” the **5-step lifecycle** (assemble â†’ scope-filter â†’ score â†’ aggregate â†’ report) Â· the
  **deliberately-composed fixture table** stating what each fixture proves **and what fails without it** Â· the **tier-split
  table** Â· the injected `RubricEngine` seam Â· the **two-deferral comparison table** (Fold-1's one-way dependency) Â· the
  **Fold-3 direction-of-data-flow table** Â· the **validated Mermaid** + **full text alternative** Â· settled items.

**âš‘ MERMAID VALIDATED MECHANICALLY (by script, not by eye) â€” all 7 rules**: 15 node IDs **all alphanumeric** (1) Â· 15 labels
**all quoted** (2) Â· **zero labels containing any non-alphanumeric-or-space character** (3 â€” *"four of five"* for the
threshold, *"tier U"*/*"tier B"* unhyphenated) Â· `subgraph=0`/`end=0` **balanced** (4) Â· **rectangle-only** `ID["label"]`
(5) Â· **zero edge labels**, so no special character can leak in (6) Â· exactly **one** `flowchart` declaration (7). Also
verified: **every edge endpoint resolves to a declared node** (no dangling refs).

**`llm-judge` (U22) stage status**: **Functional Design âœ“ Part 1 ANSWERED (Q1â€“Q7 all A) + ambiguity-check CLEAN + Part 2
GENERATED â†’ STOPPED at the FD 2-option completion gate** Â· NFR Requirements â³ Â· NFR Design â³ Â· Infrastructure Design â³ Â·
Code Generation â³. **1 of 5 stages complete pending gate. U22 is the 6th and FINAL Phase-2 unit and the LAST unit in the
entire 23-unit decomposition**; 22 of 23 units complete.

**Register**: 22 of 23 complete; **1 remains: `llm-judge` (U22)**, at its 1st stage, at the FD gate. Composition-root
**Q1-B divergence OPEN**; **R2â€“R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end); **tier-B
UNAUTHORIZED**; **`audit_store` Docker-guard gap DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN**;
**`OBS-SINK-DEFERRED` OPEN**; **`DEPLOY-MIGRATE-DEFERRED` OPEN**; `testresults.txt` append-vs-overwrite open housekeeping.
**THREE NEW items now carried by U22's FD** (all disclosed by name, none silently dropped): **`PROMPTFOO-CLI-DEFERRED`** Â·
**`JUDGE-EVAL-DEFERRED`** (distinct per Fold-1, one-way prerequisite edge) Â· **`FEWSHOT-ANCHOR-UNIMPLEMENTED`** (the
generation-side half of QA-4, owned by U4 or a future explicitly-authorized change).

**Guardrails held**: **no code**; **no `backend/llm_judge/`**; **`requirements.txt` NOT edited**; **no new dependency**;
**WIRE-1 untouched**; the **17 frozen P1 units untouched INCLUDING `memo-agent-core`** â€” **U4 read-only throughout,
`prompt_builder.py` NOT edited, which is the entire substance of the disclosed gap**; **`outlier-model` (U18) Â·
`memo-extensions` (U19) Â· `ui-outlier-view` (U20) Â· `observability` (U21) Â· `deploy-config` (U23) untouched**; the **CLOSED
composition root untouched**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit
started**; the **23-unit decomposition unchanged**. Files written: the plan (Q7 + Â§5.7 Fold-3) + the **3 FD artifacts**.
**STOPPED** at the FD 2-option completion gate (1. Request Changes / 2. Continue â†’ NFR Requirements).

## ðŸ§© BUILD â†’ `llm-judge` (U22) â€” **Functional Design APPROVED (Continue)** â†’ NFR Requirements Part 1 (Plan) WRITTEN; STOP at the plan-file gate â€” 2026-07-19

**Functional Design APPROVED 2026-07-19 (option 2, Continue â†’ NFR Requirements)** â€” U22's FD is **COMPLETE** (3 artifacts
frozen: `domain-entities.md` Â· `business-rules.md` **BR-JUDGE-1..11** Â· `business-logic-model.md`; folds
**CG-JUDGE-Fold-1..3**; gap **CG-JUDGE-GAP-1** disclosed). Gate **CLOSED**. U22 advanced to **NFR Requirements â€” the 2nd of
its 5 stages**. **Depth: standard**, consistent with the FD decision (`unit-of-work.md` L249 pin).

**Wrote Part 1 (Plan) ONLY**: `guide-docs/build/plans/llm-judge-nfr-requirements-plan.md`. **NO NFR artifact; no code; no
`backend/llm_judge/`; `requirements.txt` and `pyproject.toml` NOT edited.**

**Â§2 â€” ALL ELEVEN `BR-JUDGE-*` mapped to draft `NFR-JUDGE-*` targets, NO ORPHAN**, each with tier/rigor + pass/fail teeth:
**THRESH-1** (`aggregate == 4` **PASSES**, `aggregate == 3.99` **FAILS**, `>=` asserted explicitly) Â· **INGATE-1** Â·
**âš‘ EXEMPT-1 â€” LOAD-BEARING full-highest** (`scored_count == 2` AND `exempt_count == 1` AND the Ollama sample **present**;
**the degenerate-configuration guard â€” an all-in-gate set yielding `exempt_count == 0` is FLAGGED as an invalid
configuration, never silently accepted as a passing run**; detector self-test where a wrongly-scored Ollama sample makes
`scored_count` read `3`) Â· **EXEMPTSCOPE-1** (explicit *memo-quality* reason tag; no artifact implies Ollama is untested) Â·
**ANCHOR-1** (close scores **high**, divergent scores **low**; **detector self-test flagging a single-fixture-only
configuration as insufficient**) Â· **DISCLOSE-1** (governance) Â· **ADVISORY-1 / NOVERDICT-1** (structural
no-`Recommendation`-typed-field + token scan + detector) Â· **CLIDEFER-1** and **EVALDEFER-1** (**two DISTINCT targets**,
disjoint discharge criteria) Â· **NODEMO-1** (demographic scan incl. the hand-authored reference memo, planted-token
detector) Â· **NOEDIT-1 / NOMETRIC-1** (path scan + detector **plus the static byte-unchanged check** of `observability`'s
`METRIC_DEFINITIONS` and `deploy-config`'s dashboard, **without re-running either unit's suite**). **PERF** folded as
observed-never-gated (U22 owns no runtime SLO).

**Â§3 â€” the four called-out clarifications answered**: **(3.1)** BR-JUDGE-6 is **governance/documentation-presence, NOT
executable teeth** â€” a rule whose content is *"this is honestly not implemented"* has no behaviour to exercise; modelled on
**`deploy-config`'s DOC-1** token-set checklist (presence of the `FEWSHOT-ANCHOR-UNIMPLEMENTED` name + owner + rationale Â· a
**negative assertion** that no artifact claims discharge Â· a detector self-test on token removal) â€” and **labelling it so is
honest**, exactly as `deploy-config` labelled BUILD-1/BOOT-1's deploy-time halves *named-not-tested*. **(3.2)** BR-JUDGE-8/9
get **separate acceptance criteria** â€” both are absence proofs but assert **different absences** (no engine present vs no
corpus read) with **disjoint discharge criteria**; merging them would **erase the one-way prerequisite** Fold-1 established.
**(3.3)** the byte-unchanged check is a **static read-only content check**, no suite re-run (import-to-read â‰  edit).
**(3.4)** flagged that the four fixture roles are **not necessarily four disjoint samples** â€” the close/divergent pair may
overlap the provider-tagged samples, a real modelling choice feeding Q1.

**THREE `[Answer]` questions, all BLANK, each written in full with lettered options (rec A throughout) â€” each grounded in
DISK MEASUREMENT rather than assertion**:
- **Q1 fixture-module layout** â€” measured: **both** cited precedents use **ONE shared `fixtures.py`**, but each holds
  **deliberately-separate purpose-built NAMED FAMILIES** (U18 exposes `normal_corpus_profiles` / `typical_profile` /
  `missing_optional_profile` / **`swap_pair`** [bias-only] / **`outlier_profile`** [threshold-only]). Rec **A**: one shared
  module with distinct families â€” `in_gate_samples` Â· **`exempt_witness_sample`** Â· **`anchoring_pair`** (returned together
  so the pair cannot be split) Â· `reference_memo` Â· **`degenerate_all_in_gate_set`** (the negative fixture EXEMPT-1's guard
  needs) â€” with the **anchoring pair NOT overlapped** onto the provider-tagged samples, so a provider-scope edit cannot
  silently move the anchoring baseline (exactly why C is rejected).
- **Q2 `RubricEngine` interop** â€” **âš‘ the cited precedent was re-read and DIFFERS in one decisive respect.**
  `memo_extensions/tests/test_signal.py` **does** carry `test_interop_by_value_u18_outlier_result_satisfies_protocol`, but
  its docstring reads *"A real U18 `OutlierResult` **SHAPE**, constructed **BY VALUE (never imported)**"* â€” plus
  `assert isinstance(by_value, OutlierSignal)` and the non-vacuity `assert not isinstance(object(), OutlierSignal)`.
  **U19 could replicate U18's shape by value because U18's `OutlierResult` is a FROZEN, ON-DISK, verifiable target. For U22
  no such target exists** â€” the promptfoo CLI is **absent**, its output shape **external, version-dependent, unpinned** (an
  `npx` run-time fetch); replicating it would replicate an **ASSUMPTION**, manufacturing false confidence. Rec **A**: keep
  the **honestly-available half** (satisfiable **+** non-vacuous, the exact U19 assertions), **omit the by-value replica
  because the precedent's precondition is absent**, and make **real-shape interop an explicit named criterion of
  CLIDEFER-1's discharge**. B rejected â€” a green test attesting to an assumption would pass while interop is broken,
  **worse than no test**.
- **Q3 coverage for the hybrid unit** â€” measured in `pyproject.toml`: every pure-logic unit adds `--cov=backend/<unit>` with
  *"No omit â€” pure logic, fully unit-coverable"*; **`observability` is the exact hybrid precedent** â€” it added its `--cov`
  line **even though its live SDK binding was deferred (`OBS-SINK-DEFERRED`)**, noting *"no live-SDK/subprocess/network
  module at tier-U"*; `deploy-config` added none **only because it had no production `.py` at all**. Rec **A**: add
  **`--cov=backend/llm_judge`, NO omit** â€” the deferred halves are **ABSENT modules, not uncovered ones**; global
  `--cov-fail-under=90` holds unchanged; **BR-JUDGE-6/8/9's verification is the presence/absence scans, orthogonal to line
  coverage**, stated so the number is not mistaken for covering them.

**`llm-judge` (U22) stage status**: **Functional Design âœ“ Â· NFR Requirements â³ Part 1 (Plan) WRITTEN â†’ STOPPED at the
plan-file gate** (ambiguity-check after the answers; Part 2 = `nfr-requirements.md` + `tech-stack-decisions.md` on explicit
go) Â· NFR Design â³ Â· Infrastructure Design â³ Â· Code Generation â³. **2 of 5 stages engaged. U22 is the 6th and FINAL
Phase-2 unit and the LAST unit in the entire 23-unit decomposition**; 22 of 23 units complete.

**Register (unchanged)**: 22 of 23 complete; **1 remains: `llm-judge` (U22)**, at its 2nd stage. Composition-root **Q1-B
divergence OPEN**; **R2â€“R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end); **tier-B UNAUTHORIZED**;
**`audit_store` Docker-guard gap DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN**;
**`OBS-SINK-DEFERRED` OPEN**; **`DEPLOY-MIGRATE-DEFERRED` OPEN**; **`PROMPTFOO-CLI-DEFERRED` Â· `JUDGE-EVAL-DEFERRED` Â·
`FEWSHOT-ANCHOR-UNIMPLEMENTED`** (U22's three, carried from its frozen FD); `testresults.txt` append-vs-overwrite open
housekeeping.

**Guardrails held**: **no NFR artifact**; **no code**; **no `backend/llm_judge/`**; **`requirements.txt` NOT edited**;
**`pyproject.toml` NOT edited**; the **frozen FD re-opened NONE**; **WIRE-1 untouched**; the **17 frozen P1 units untouched
INCLUDING `memo-agent-core`**; **`outlier-model` (U18) Â· `memo-extensions` (U19) Â· `ui-outlier-view` (U20) Â·
`observability` (U21) Â· `deploy-config` (U23) untouched** (read-only re-reads only); the **CLOSED composition root
untouched**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the
**23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1â€“Q3.

## BUILD -> `llm-judge` (U22) -- **NFR Req Q1-Q3 ANSWERED (all A)** + ambiguity-check **RAN -> CLEAN (3 folds)** + **Part 2 GENERATED (2 artifacts)**; STOP at the NFR Requirements 2-option gate -- 2026-07-19

**Q1-Q3 all A** (already embedded in the plan section 4). **Ambiguity-check WRITTEN AND RUN as plan section 4.5 -> CLEAN --
3 folds resolved, no genuine gap, no surface-and-stop.**

**Resumption correction (measured, not assumed)**: the plan carried the three filled `[Answer]: A` tags and the full
question text, but **NO ambiguity-check section existed** -- it had not yet been run. Written this turn as **section 4.5**
(the slot analogous to the FD plan's 5.5, since these answers live in section 4).

- **NFR-JUDGE-Req-Fold-1 [check (i)] RESOLVED -- `degenerate_all_in_gate_set()` MUST be a genuinely SEPARATE third
  builder.** By content alone the two sets are co-satisfiable today, so aliasing would be *currently* correct -- and still
  structurally wrong: **the two families are defined by DIFFERENT INVARIANTS that merely coincide.** `in_gate_samples()`'s
  contract (*"contains gemini and claude"*) says **nothing** about an exempt sample being absent; that absence is
  **incidental to it and load-bearing for the other**. Q1-A's own principle applies verbatim; U18's frozen precedent is the
  same shape (`swap_pair()` bias-only, `outlier_profile()` threshold-only, deliberately not reused). **Three anti-conflation
  mechanisms pinned**: (1) **distinct `sample_id`s** (never identity-equal); (2) a **self-asserting builder** whose own
  precondition `all(s.provider is not ProviderScopeTag.ollama)` **fails at construction** rather than letting the guard go
  vacuous; (3) **no aliasing** -- it does not call `in_gate_samples()`. Also: EXEMPT-1's **positive** fixture is itself a
  **third composition** (`in_gate_samples()` + `exempt_witness_sample()`), so **three** set-level fixtures exist, not two.
  And the targets do **not** contradict: INGATE-1 asserts the **scope-filter**; EXEMPT-1's guard asserts a **run-validity**
  check -- different function, different level, and **not** a claim that a production run over an Ollama-free corpus is
  invalid.
- **NFR-JUDGE-Req-Fold-2 [check (ii)] RESOLVED -- EXEMPT-1's designation is CORRECT; the real inconsistency is one target
  over.** **Count** is in band (observability TWO full-highest, deploy-config THREE). **Behavioural full-highest is
  precedented** -- the premise *"full-highest is usually a structural scan"* does not hold: **`NFR-OBS-TRACE-1` is
  `component (teeth) + structural` at full (highest)**; deploy-config's three are scans only because it is a declarative
  unit with no production Python. EXEMPT-1 also carries a structural clause (the degenerate guard) inside itself -- TRACE-1's
  exact hybrid. **BUT**: section 2's draft labelled BR-JUDGE-11's **NOEDIT-1/NOMETRIC-1** *"load-bearing-STYLE"*, a hedge
  appearing in **no** prior unit, when **both** units carrying a NOEDIT target designated it outright
  (`NFR-OBS-NOEDIT-1` = full (highest); `NFR-DEP-NOEDIT-1` = [LOAD-BEARING]). **CORRECTION CARRIED INTO PART 2:
  NOEDIT-1/NOMETRIC-1 PROMOTED to full (highest) / LOAD-BEARING** -- restoring observability's exact pairing (one
  **structural** load-bearing target beside one **behavioural** one: there TRACE-1, here EXEMPT-1). **Raises** rigor,
  conforms to precedent, **flagged not silent**, reversible at the gate.
- **NFR-JUDGE-Req-Fold-3 [check (iii)] RESOLVED -- DISCLOSE-1 and CLIDEFER-1's deferred-interop half are GENUINELY
  DISTINCT**, separating on **four independent axes**: **content** (unimplemented generation-side few-shot mechanism vs
  absent scoring engine's unverifiable output shape); **owner** (**`memo-agent-core` (U4) / a future explicitly-authorized
  change -- NEVER U22's to discharge** vs **U22's own seam**); **direction of data flow** (exemplars INTO generation vs
  engine output OUT OF scoring -- Fold-3's axis); **dischargeability** (**structurally BLOCKED by the frozen-P1 guardrail**
  vs **merely not-yet-done, touching no frozen unit**). The owner row is decisive. **Anti-conflation mechanism**:
  DISCLOSE-1's tokens keyed to the register name **+ U4 owner attribution**, CLIDEFER-1's to its **five discharge
  criteria**, and **each detector self-test asserts the other's tokens do NOT mask its own token's removal.**

**PART 2 GENERATED -- 2 artifacts** at `guide-docs/build/llm-judge/nfr-requirements/`:
- **`nfr-requirements.md`** -- the **eleven finalized `NFR-JUDGE-*` targets** (+ PERF-1 soft / SEC-1 governance, carried as
  every prior unit did), each with **pass/fail assertion + acceptance + tier + rigor**. **TWO LOAD-BEARING full-highest**:
  **EXEMPT-1** (mechanism spelled out -- U19's by-name assignment quoted verbatim, *"if U22 does not assert it, NOTHING IN
  THE BUILD DOES"*, **`exempt_count` as a POSITIVE witness** so the exemption is never proven by an absence, plus the
  degenerate-configuration guard with Fold-1's three mechanisms) and **NOEDIT-1/NOMETRIC-1** (promoted per Fold-2; path scan
  + detector + the **static byte-unchanged check** of U21's five `METRIC_DEFINITIONS` and U23's `deploy/grafana-dashboard.json`
  **without re-running either suite**). Plus **THRESH-1** (`aggregate == 4` PASSES / `3.99` FAILS, `>=` explicit) Â·
  **INGATE-1** (GATE-1 left explicitly to `quality-gates`) Â· **EXEMPTSCOPE-1** Â· **ANCHOR-1** (paired, unsplittable,
  non-overlapped) Â· **ADVISORY-1/NOVERDICT-1** (verdict structurally unrepresentable; only the `L` region judged) Â·
  **CLIDEFER-1** (absence + Protocol satisfiability/non-vacuity + **five** discharge criteria incl. the newly-named
  real-shape-interop one) Â· **EVALDEFER-1** Â· **NODEMO-1** Â· **DISCLOSE-1** (governance/doc-presence, honestly labelled).
  **Traceability table with NO ORPHAN** (11 rules -> 11 targets, 1:1) + story/AC coverage + a **fixture-role -> target map**.
  **Full 13-row Security-Guardrails table, NO BLOCKING FINDING**, incl. a **supply-chain/external-tool hygiene** row for the
  npx-unpinned-fetch + posthog telemetry.
- **`tech-stack-decisions.md`** -- on-disk dependency verification; the **shim-vs-engine distinction recorded in full** as
  its own evidence table (pip shim requires Node/npx -- **the Node engine is ABSENT** -- npx would fetch an **unpinned**
  package over the network at run time -- **posthog 7.21.3 telemetry** in a BFSI system -- output shape
  external/version-dependent/unpinned); **JUDGE-D1..D9** (pytest; the **five named fixture families** with why each is its
  own; **D3** the separate degenerate builder; **D4** the Q2-A no-by-value-replica reasoning; **D5** `--cov=backend/llm_judge`
  **no omit** per observability verbatim, stating that **BR-JUDGE-6/8/9's verification is orthogonal to line coverage**;
  **D6** pure-Python determinism; **D7** import-to-read reference memo; **D8** no new emission; **D9** layout open); and all
  **three register items** with discharge criteria + distinctness. **NO NEW DEPENDENCY.**

**`llm-judge` (U22) stage status**: **Functional Design [x]** Â· **NFR Requirements [x] Part 1 ANSWERED (Q1-Q3 all A) +
ambiguity-check CLEAN + Part 2 GENERATED -> STOPPED at the 2-option completion gate** Â· NFR Design [ ] Â· Infrastructure
Design [ ] Â· Code Generation [ ]. **2 of 5 stages complete pending gate. U22 is the 6th and FINAL Phase-2 unit and the LAST
unit in the entire 23-unit decomposition**; 22 of 23 units complete.

**Register (unchanged)**: 22 of 23 complete; **1 remains: `llm-judge` (U22)**, at its 2nd stage, at the NFR Requirements
gate. Composition-root **Q1-B divergence OPEN**; **R2-R5 unwired** (R4 a `501` stub; core demo path not runnable
end-to-end); **tier-B UNAUTHORIZED**; **`audit_store` Docker-guard gap DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**;
**`MCP-TRANSPORT-DEFERRED` OPEN**; **`OBS-SINK-DEFERRED` OPEN**; **`DEPLOY-MIGRATE-DEFERRED` OPEN**;
**`PROMPTFOO-CLI-DEFERRED` Â· `JUDGE-EVAL-DEFERRED` Â· `FEWSHOT-ANCHOR-UNIMPLEMENTED`** (U22's three, carried from its frozen
FD and now each given explicit discharge criteria in `tech-stack-decisions.md`); `testresults.txt` append-vs-overwrite open
housekeeping.

**Guardrails held**: **no code**; **`backend/llm_judge/` still ABSENT** (verified this session); **`requirements.txt` NOT
edited**; **`pyproject.toml` NOT edited** (the `--cov` line lands at Code-Gen); **no new dependency**; the **frozen FD
re-opened NONE**; **WIRE-1 untouched**; the **17 frozen P1 units untouched INCLUDING `memo-agent-core`**; **`outlier-model`
(U18) Â· `memo-extensions` (U19) Â· `ui-outlier-view` (U20) Â· `observability` (U21) Â· `deploy-config` (U23) untouched**
(read-only re-reads only); the **CLOSED composition root untouched**; **tier-B NOT authorized**; the **`audit_store`
Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**. **Files written: 3** --
the plan (section 4.5 appended) + the 2 NFR artifacts (+ the append-only `audit.md` entry and this state entry).
**STOPPED** at the NFR Requirements 2-option completion gate (1. Request Changes / 2. Continue -> NFR Design).


## BUILD -> `llm-judge` (U22) -- **NFR Requirements APPROVED (Continue)** -> NFR Design Part 1 (Plan) WRITTEN; STOP at the plan-file gate -- 2026-07-19

**NFR Requirements APPROVED 2026-07-19 (option 2, Continue -> NFR Design)** -- U22's NFR Requirements is **COMPLETE**
(2 artifacts frozen: `nfr-requirements.md` with the **eleven `NFR-JUDGE-*`** targets + `tech-stack-decisions.md`; folds
**NFR-JUDGE-Req-Fold-1..3**). Gate **CLOSED**. U22 advanced to **NFR Design -- the 3rd of its 5 stages**. **Depth: standard.**

**Wrote Part 1 (Plan) ONLY**: `guide-docs/build/plans/llm-judge-nfr-design-plan.md`. **NO NFR Design artifact; no code; no
`backend/llm_judge/`; `requirements.txt` and `pyproject.toml` NOT edited.**

**Section 2 -- ALL ELEVEN `NFR-JUDGE-*` (+ PERF-1/SEC-1) mapped to FOURTEEN named patterns `P-JUDGE-1..14`, NO ORPHAN.**
- **EXEMPT-1 deliberately takes TWO patterns**: **P-JUDGE-1 `PositiveWitnessExemptionPattern`** (`exempt_count` a
  **required report field**, retained-not-dropped -- proof **BY PRESENCE**) + **P-JUDGE-2 `DegenerateSetGuardPattern`** (the
  **DISTINCT** structural safeguard). Their mechanisms differ **in kind** (behavioural teeth over a three-sample composition
  vs a set-validity predicate), so **one edit cannot weaken both halves**.
- **NOEDIT-1/NOMETRIC-1 likewise paired**: **P-JUDGE-3 `FrozenPathScanPattern`** (the **U23 `P-DEP-1` mechanism REUSED, not
  reinvented** -- `ALLOWED_U22_PREFIXES` vs `FROZEN_PREFIXES`, authored set subset-of allowed AND disjoint-from frozen,
  synthetic-frozen-path detector) + **P-JUDGE-4 `StaticNoDriftAssertionPattern`**.
- **P-JUDGE-5 `SatisfiableNonVacuousProtocolPattern`** -- **the no-by-value-replica rationale written as a FIRST-CLASS
  two-part contract, not a footnote**: the pattern's **PRECONDITION is a frozen on-disk mirror target**, and for U22 that
  precondition is **ABSENT**.
- Plus **P-JUDGE-6** `UnsplittablePairedFixture` (tuple return = unsplittable at the type level) - **P-JUDGE-7**
  `TokenChecklistGovernance` (U23 DOC-1 lineage + anti-conflation) - **P-JUDGE-8** `PureBoundaryArithmetic` - **P-JUDGE-9**
  `ScopePartition` - **P-JUDGE-10** `UnrepresentableVerdict` - **P-JUDGE-11** `DemographicTokenScan` - **P-JUDGE-12**
  `AbsenceProofDeferral` - **P-JUDGE-13** `StructuralGuard` (U18/U19/U21 substrate) - **P-JUDGE-14**
  `ObservedNeverGatedGovernance`.

**Section 3 -- FIVE logical components `C-JUDGE-1..5`** (rubric/domain model - eval pipeline - engine seam - fixtures
substrate - StructuralGuard substrate). **Two things PINNED from the precedent rather than re-derived**: the StructuralGuard
parses every **PRODUCTION** `.py` under `backend/llm_judge/` **EXCLUDING `tests/`** (verbatim U21 `structural.py`) with an
`EXPECTED_PRODUCTION_MODULES` **non-vacuity guard**; and **the offline fake lives in `tests/`, NOT production** -- so no
production module can depend on it and CLIDEFER-1's no-promptfoo-import scan has a clean production set to scan.

**MERMAID DRAFTED AND MECHANICALLY VALIDATED (by script, not by eye) -- ALL 7 RULES PASS**: 14 nodes, 16 edges,
**14/14 strict quoted rectangles**; alphanumeric IDs; **zero labels with any non-alphanumeric-or-space character**; blocks
balanced (no `subgraph`); rectangle-only (shape token checked **per node ID**); **zero edge labels**; exactly **one**
`flowchart` declaration; **no dangling endpoints**. *(One validator false positive caught and fixed -- an over-broad regex
matched the `-->` arrows as a shape token; the diagram itself was never at fault.)*
**Both required properties verified as VISIBLE graph properties BY THE SCRIPT**:
1. **no-frozen-edit** -- `FROZENTREE` has **exactly ONE inbound edge**, from `GUARD` (a read-only scan);
   **AUTHORED (non-guard) edges into the frozen tree: NONE.** The **absence of an authored edge IS the guarantee**, and the
   single guard edge is what proves the absence **non-vacuously**.
2. **exempt-count-as-positive-witness** -- the chain `PIPELINE -> EXEMPTPATH -> WITNESS -> REPORT` verified **intact**: the
   exempt sample terminates in a **counted witness inside the report**, never a dead end.
   The **only** dashed edges are the two deferred paths (`REALCLI -> PROTO`, `CORPUS -> PIPELINE`).

**THREE `[Answer]` questions, all BLANK, each in full with lettered options (rec A throughout), each a genuine fork**:
- **Q1 -- where EXEMPT-1's degenerate-configuration guard LIVES + its signature.** Rec **A**: a **pure predicate in
  production** `is_nonvacuous_exemption_set(samples) -> bool`, **APPLIED by the test** (flags nothing, raises nothing on its
  own) -- honest production logic, tier-U-coverable, keeps the **flagging in the test** where the configuration question
  belongs, keeps EXEMPT-1's halves on **different mechanisms**, and **cannot wrongly reject a legitimate production run**
  over an Ollama-free corpus. **B rejected** (a gate inside report assembly converts a verification-set property into a
  production constraint the FD never asserted); **C rejected** (test-only puts a reusable set property outside the coverable
  tree).
- **Q2 -- how the offline fake PRODUCES ANCHOR-1's high/low scores. âš‘ FLAGGED AS A GENUINE VACUITY RISK, not designed
  around silently.** The **frozen FD defines the fake as returning fixture-DECLARED scores** -- so a pure echo reduces
  ANCHOR-1 to *"the fixture said high and the fake returned high"*: it proves the **plumbing** but **nothing about anchoring
  discrimination**. Rec **A**: keep the fake **exactly as frozen** and **honestly narrow ANCHOR-1's stated tier-U scope** to
  the paired-fixture plumbing + the unsplittable-pair safeguard, adding *"a real judge actually scores divergence lower"* as
  a **named criterion of `PROMPTFOO-CLI-DEFERRED`** -- the build's repeated *deliver-the-verifiable-half, name-the-
  unverifiable-half* pattern; **re-opens no frozen FD text and overclaims nothing**. **B rejected**: an offline similarity
  heuristic would make U22 own **a scoring heuristic that is not what the real engine does**, so a green ANCHOR-1 would
  attest to **U22's own heuristic, not the rubric** -- the same false-confidence failure mode Q2-A rejected for the interop
  replica. **C** offered as a middle path with its risk stated (two competing definitions of one dimension).
- **Q3 -- what P-JUDGE-4's "byte-unchanged" check actually ASSERTS.** Rec **A**: **property assertions** --
  `len(METRIC_DEFINITIONS) == 5` + the five names **by value**, and **exactly five** dashboard panels -- precisely the
  property U22 must not drift (**no sixth metric, no sixth panel**), which is what BR-JUDGE-11 and `deploy-config`'s
  five-panel no-drift scan actually mean; **robust to legitimate unrelated edits** by U21/U23's owners; **invents no magic
  constant**. **B (content-hash pin) rejected as fragile and arguably wrong** -- any future legitimate change to a frozen
  unit would break **U22's** suite, and U22 would assert a hash **it invented at Code-Gen time**, converting *"U22 changed
  nothing"* into *"nobody may ever change these files"*. **C (mtime) rejected** -- not content, not stable across checkout,
  breaks deterministic tier-U.

**`llm-judge` (U22) stage status**: **Functional Design [x]** Â· **NFR Requirements [x]** Â· **NFR Design [ ] Part 1 (Plan)
WRITTEN -> STOPPED at the plan-file gate** (ambiguity-check after the answers; Part 2 = `nfr-design-patterns.md` +
`logical-components.md` on explicit go) Â· Infrastructure Design [ ] Â· Code Generation [ ]. **3 of 5 stages engaged. U22 is
the 6th and FINAL Phase-2 unit and the LAST unit in the entire 23-unit decomposition**; 22 of 23 units complete.

**Register (unchanged)**: 22 of 23 complete; **1 remains: `llm-judge` (U22)**, at its 3rd stage. Composition-root **Q1-B
divergence OPEN**; **R2-R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end); **tier-B UNAUTHORIZED**;
**`audit_store` Docker-guard gap DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN**;
**`OBS-SINK-DEFERRED` OPEN**; **`DEPLOY-MIGRATE-DEFERRED` OPEN**; **`PROMPTFOO-CLI-DEFERRED` Â· `JUDGE-EVAL-DEFERRED` Â·
`FEWSHOT-ANCHOR-UNIMPLEMENTED`** (U22's three); `testresults.txt` append-vs-overwrite open housekeeping.

**Guardrails held**: **no NFR Design artifact**; **no code**; **`backend/llm_judge/` still ABSENT**; **`requirements.txt`
NOT edited**; **`pyproject.toml` NOT edited**; the **frozen FD AND the approved NFR Requirements re-opened NEITHER**;
**WIRE-1 untouched**; the **17 frozen P1 units untouched INCLUDING `memo-agent-core`**; **`outlier-model` (U18) Â·
`memo-extensions` (U19) Â· `ui-outlier-view` (U20) Â· `observability` (U21) Â· `deploy-config` (U23) untouched** (read-only
re-reads only: U21 `tests/structural.py`, the U21+U23 nfr-design artifact pairs, U23 `P-DEP-1`); the **CLOSED composition
root untouched**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**;
the **23-unit decomposition unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting
Q1-Q3.


## BUILD -> `llm-judge` (U22) -- **NFR Design Q1-Q3 ANSWERED (all A)** + ambiguity-check **RAN -> CLEAN (3 folds + 1 disclosure)** + **Part 2 GENERATED (2 artifacts)**; STOP at the NFR Design 2-option gate -- 2026-07-19

**Q1-Q3 all A** (embedded in the plan section 5). **Ambiguity-check RUN as plan section 5.5 -> CLEAN -- 3 folds resolved, no
genuine gap, no surface-and-stop -- plus ONE DISCLOSURE raised for the gate** (blocks nothing, requires no improvisation,
but it is the user's call).

- **NFR-JUDGE-ND-Fold-1 [check (i)] RESOLVED -- a legitimate Design-stage clarification, NOT a material change. The decisive
  reason is PROVENANCE, not interpretation.** The declared-echo behaviour of the tier-U fake is **not an NFR-Design choice
  at all** -- it was **frozen at the FD stage, before NFR Requirements existed**: `domain-entities.md` section 8 defines it
  verbatim as *"Offline deterministic fake ... Returns **fixed, fixture-declared scores**"*, repeated in
  `business-logic-model.md` section 3. **The FD outranks and predates NFR Requirements** -> Q2-A **chooses nothing new**; it
  makes explicit a consequence the frozen FD had already determined. **Confirmed against the approved text read verbatim**:
  ANCHOR-1's four acceptance criteria (pair-driven/unsplittable Â· single-fixture detector Â· style-not-identity Â·
  own-non-overlapped-family) -- **NONE claims engine-side discrimination**; every operative criterion survives **untouched**.
  **âš‘ THE DISCLOSURE**: ANCHOR-1's one-line **Assertion** sentence would read as over-promising **if quoted in isolation**.
  A **presentation** issue, not correctness. **The approved artifact was deliberately NOT retro-edited** -- same discipline
  as never back-dating an audit entry: **approved artifacts are built ON, not revised**. The narrowing instead lives as a
  **first-class clause of P-JUDGE-6's own definition** + the traceability row, and **the choice is offered at the gate**
  (leave as-is, recommended; or a logged one-line amendment).
- **NFR-JUDGE-ND-Fold-2 [check (ii)] RESOLVED -- genuinely different things, not a rename.** Different **subject**
  (**`EvalRunResult`**, an OUTPUT, vs **`Sequence[JudgedSample]`**, an INPUT set), **field** (`exempt_count` vs
  `sample.provider`), **stage** (post-run vs pre-run), **failure mode** (pipeline mis-partitions vs fixture set degenerate).
  **Decisive: one guards the other's PRECONDITION** -- over an all-in-gate set a pipeline **that never implemented exemption
  at all** would still report `scored_count == 2`, so P-JUDGE-1's teeth would pass **VACUOUSLY**; P-JUDGE-2 is what makes
  them non-degenerate. **Anti-collapse pinned**: samples -> bool; it **never constructs, runs, or reads an `EvalRunResult`**.
- **NFR-JUDGE-ND-Fold-3 [check (iii)] RESOLVED ON DISK -- and a mechanism already exists, frozen.** The concern was
  **well-founded in general** (Grafana CAN nest panels in `row` panels, silently under-counting a naive `len()`), **so the
  actual committed file was measured**: top-level `panels` = **5**; **no** nested `panels` key; **no** `type: "row"` panel;
  exprs **exactly** the five frozen metric names -> **flat, unnested, unambiguous**. Moreover `deploy-config`'s **OWN FROZEN**
  `tests/test_scope.py::test_grafana_dashboard_panels_match_observabilitys_frozen_five_no_drift` **already does exactly
  this**, cross-referencing `METRIC_DEFINITIONS` **by value** -> **U22 REUSES the frozen technique rather than inventing
  one**. **âš‘ AND this surfaced a REAL OVERLAP that RE-SCOPED P-JUDGE-4**: since U23's frozen test already catches **both**
  drift directions, a U22 check merely re-asserting it would be a **near-duplicate of a frozen test** (and U22 cannot rely
  on it executing, since re-running either suite is forbidden). **P-JUDGE-4's PRIMARY mechanism is now the one nothing else
  makes** -- an AST scan over **U22's OWN production tree** asserting **no U22 module declares a metric name /
  `MetricDefinition`** (a **provenance** claim genuinely U22's) -- with the read-only five-names/five-panels property
  assertion **corroborating**, pinning the baseline so the provenance scan is non-vacuous. U22 adds **no-nested-`panels`**
  so future row-nesting **fails loudly**.

**PART 2 GENERATED -- 2 artifacts** at `guide-docs/build/llm-judge/nfr-design/`:
- **`nfr-design-patterns.md`** -- **P-JUDGE-1..14**, each with the **real mechanism spelled out** (actual dataclass /
  Protocol / predicate signatures, not prose). **FOUR full-highest LOAD-BEARING patterns**, covering the two load-bearing
  targets **TWO patterns each** so **no single edit can weaken both halves of either**: **P-JUDGE-1 PositiveWitnessExemption**
  + **P-JUDGE-2 DegenerateSetGuard**; **P-JUDGE-3 FrozenPathScan** (U23 `P-DEP-1` reused) + **P-JUDGE-4 StaticNoDrift**
  (re-scoped by ND-Fold-3). **P-JUDGE-5** states the **no-by-value-replica as a PROPERTY OF THE PATTERN** (its precondition
  is a frozen on-disk mirror target; for U22 that precondition is **ABSENT**). **P-JUDGE-6 carries ANCHOR-1's honest scope
  as a first-class clause**, noting that refusing a heuristic fake is **the same principle as refusing the interop replica,
  applied twice deliberately**. Plus P-JUDGE-7..14. **Full traceability, NO ORPHAN.**
- **`logical-components.md`** -- **C-JUDGE-1..5** with **exact signatures**: the full frozen-dataclass domain model
  (**no `Recommendation`-typed field anywhere** -> verdict unrepresentable; **`exempt_count` a REQUIRED field**);
  `partition_by_scope()` / `aggregate_sample()` / `run_eval()`; **`is_nonvacuous_exemption_set(samples: Sequence[JudgedSample])
  -> bool`** with its anti-collapse docstring; the **Protocol in production with the `DeclaredScoreEngine` fake in `tests/`
  ONLY**; the **five named fixture families** (`anchoring_pair()` returning a **tuple** = unsplittable at the type level;
  `degenerate_all_in_gate_set()` a **separate self-asserting builder**); the **six-scan StructuralGuard table** with
  `EXPECTED_PRODUCTION_MODULES` non-vacuity guard and `production_py_files()` **EXCLUDING `tests/`** (verbatim U21). **The
  three-category reference-not-own check kept DISTINCT**, with the explicit note that **a category-3 member on a solid edge
  would mean U22 had quietly discharged a named deferral**. **Component -> target coverage, NO ORPHAN.**

**BOTH MERMAIDS MECHANICALLY RE-VALIDATED (by script, not by eye) -- ALL 7 RULES PASS ON BOTH**: 15 nodes / 17 edges each;
strict quoted rectangles; alphanumeric IDs; **zero labels with any non-alphanumeric-or-space character**; balanced blocks;
rectangle-only (shape token checked **per node ID**); **zero edge labels**; one `flowchart` each; **no dangling endpoints**.
**Three structural properties verified BY THE SCRIPT on both**: **(1)** the frozen-tree node has **exactly ONE inbound
edge**, from the structural guard -- **AUTHORED (non-guard) edges into the frozen tree: NONE**; **(2)** the
**exempt-count positive-witness chain INTACT**; **(3)** the **predicate has NO edge to the report** -- the anti-collapse
mechanism made visible. Only two dashed edges per diagram, both deferrals.

**`llm-judge` (U22) stage status**: **Functional Design [x]** Â· **NFR Requirements [x]** Â· **NFR Design [x] Q1-Q3 ANSWERED +
ambiguity-check CLEAN + Part 2 GENERATED -> STOPPED at the 2-option completion gate** Â· Infrastructure Design [ ] Â·
Code Generation [ ]. **3 of 5 stages complete pending gate. U22 is the 6th and FINAL Phase-2 unit and the LAST unit in the
entire 23-unit decomposition**; 22 of 23 units complete.

**Register (unchanged)**: 22 of 23 complete; **1 remains: `llm-judge` (U22)**, at its 3rd stage. Composition-root **Q1-B
divergence OPEN**; **R2-R5 unwired** (R4 a `501` stub); **tier-B UNAUTHORIZED**; **`audit_store` Docker-guard gap
DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN**; **`OBS-SINK-DEFERRED` OPEN**;
**`DEPLOY-MIGRATE-DEFERRED` OPEN**; **`PROMPTFOO-CLI-DEFERRED` Â· `JUDGE-EVAL-DEFERRED` Â· `FEWSHOT-ANCHOR-UNIMPLEMENTED`**
(U22's three); `testresults.txt` append-vs-overwrite open housekeeping. **NEW at this stage**: the **ND-Fold-1 disclosure**
(ANCHOR-1's assertion sentence in the approved NFR Requirements artifact reads as over-promising in isolation; deliberately
**NOT** retro-edited; user's choice at the gate).

**Guardrails held**: **no code**; **`backend/llm_judge/` still ABSENT**; **`requirements.txt` NOT edited**;
**`pyproject.toml` NOT edited**; the **frozen FD AND the approved NFR Requirements re-opened NEITHER** (the approved
NFR Requirements artifact was **read verbatim but NOT edited**); **WIRE-1 untouched**; the **17 frozen P1 units untouched
INCLUDING `memo-agent-core`**; **`outlier-model` (U18) Â· `memo-extensions` (U19) Â· `ui-outlier-view` (U20) Â·
`observability` (U21) Â· `deploy-config` (U23) untouched** (read-only re-reads only: U23's `test_scope.py`,
`deploy/grafana-dashboard.json`, U21's `METRIC_DEFINITIONS`; **neither unit's suite re-run**); the **CLOSED composition root
untouched**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the
**23-unit decomposition unchanged**. **Files written: 3** -- the plan (section 5.5) + the 2 NFR Design artifacts.
**STOPPED** at the NFR Design 2-option completion gate (1. Request Changes / 2. Continue -> Infrastructure Design).


## BUILD -> `llm-judge` (U22) -- **NFR Design APPROVED (Continue)** -> Infrastructure Design **ASSESSED -> SKIPPED (logged, rule-justified)** = the **20th skip** + **4th Phase-2 skip**; STOP at the Infra 2-option gate; NEXT = Code Generation -- 2026-07-19

**NFR Design APPROVED 2026-07-19 (option 2, Continue -> Infrastructure Design)** -- U22's NFR Design **COMPLETE** (2 artifacts
frozen: `nfr-design-patterns.md` **P-JUDGE-1..14** + `logical-components.md` **C-JUDGE-1..5**; folds
**NFR-JUDGE-ND-Fold-1..3**). Gate **CLOSED**. *(The ND-Fold-1 disclosure was resolved by the approval: ANCHOR-1's assertion
sentence in the approved NFR Requirements artifact stays **as-is, NOT retro-edited** -- the recommended option.)*

**Infrastructure Design ASSESSED AT THE STAGE (not pre-assumed, neither outcome defaulted to) -> logged SKIP. NO infra
artifact created** (`guide-docs/build/llm-judge/infrastructure-design/` **NOT** created -- consistent with all **nineteen**
prior skips).

### FOUR-SOURCE CONVERGENCE -- and this time three of the four sources point the SAME way by ABSENCE

The brief's hypothesis was **correct on every count, and each element was verified on disk rather than assumed**:

1. **`unit-of-work.md` L249 -- U22 carries NO Infrastructure-Design annotation.** Measured verbatim:
   U22 reads only ***"Depth: standard."*** Contrast the two units the brief named:
   **L248 U21** *"Depth: **comprehensive at Infrastructure Design (wiring-heavy)**"* Â· **L250 U23** *"Depth: **comprehensive
   at Infrastructure Design**"*. **âš‘ A grep for "Infrastructure Design" across the whole of `unit-of-work.md` returns
   EXACTLY THREE hits -- L218 (`database`), L248 (U21), L250 (U23) -- and those are EXACTLY the three real non-skip passes
   on disk.** The annotation and the real-pass set are in **perfect 1:1 correspondence**, and **U22 is not in it.**
2. **`execution-plan.md` L199-200 -- U22 is absent from the *Comprehensive* list and covered by the *Lighter* class.**
   L199 enumerates *Comprehensive* as **exactly**: `deploy-config`, `database`, `observability`. **`llm-judge` is NOT
   named.** L200 classes *"pure-logic units ... have **little independent infra**"* -- and U22 **is** a pure-logic unit
   (rubric definition, scope-filtering, aggregation, threshold arithmetic, report assembly).
3. **U22's own FD / NFR-Requirements / NFR-Design named NO infrastructure topology as deferred-to-Infra-Design.** Measured:
   a grep for "Infrastructure Design" across **all five** U22 artifacts returns **only two hits**, both the compound
   catch-all *"Deferred to **Infrastructure Design / Code-Gen**"*, and what they defer is **exact module names, the fake's
   precise surface, the exact scan token sets, and the `--cov` line** -- **every one a Code-Gen concern. Not one line of
   topology: no service, no endpoint, no environment, no network binding, no deployed resource.** Contrast U21, which named
   *"the live Langfuse callback->checkpointer binding, the `/metrics` mount + scrape, the Grafana dashboard, keys via
   `secrets-config`, AC-7's deploy-time audit"* -- **actual topology, pointing at that exact stage.**
4. **U22 matches the U18/U19/U20 skip pattern, not the U21/U23 real-pass pattern.** The three real passes each design a
   **deployed, running service topology** (Postgres+Docker Â· Langfuse+Prometheus/Grafana Â· Render+Vercel). U22 designs
   **none** -- it is a source-level Python package that **wraps the built system** (`unit-of-work-dependency.md` L200) and
   **provisions nothing**.

### Rule justification (explicit, matching the nineteen prior skips)
**CLAUDE.md** Infrastructure Design ***"Skip IF: No infrastructure changes / Infrastructure already defined"*** **+
`execution-plan.md:200`'s** *Lighter / minimal-footprint* classing (*"pure-logic units ... have little independent infra"*).
Mirrors `outlier-model`'s logged-skip shape most closely: **a pure-logic unit that reaches everything it touches through a
seam whose real binding is ALREADY somebody else's logged, deferred concern.**

### All five assessment points verified against the frozen artifacts on disk
1. **No untrusted parsing / no subprocess sandbox** -- U22 parses no document and **spawns no process**. The promptfoo shim
   is the *only* subprocess-bearing thing in view, and **`NFR-JUDGE-CLIDEFER-1`'s AST scan structurally forbids importing
   it in production** -- so the subprocess concern is **not merely absent, it is scan-enforced absent**. At tier-U: **no
   Node, no npx, no network, no telemetry**.
2. **No independent persistence it provisions** -- U22 **persists nothing**: no schema, no migration, no role-grant, no DB
   reach. Its **only** emission is its own `EvalRunResult` report artifact (Q6-A) -- **no Prometheus metric, no dashboard
   panel** (a sixth would be drift against U21's frozen five). Persistence topology stays **`database`'s**.
3. **LLM/provider access exists but adds NO new provider-infrastructure decision** -- the **same inversion U19 established,
   and one step weaker here**: U22 drives **U19's frozen adapters through their EXISTING seam**, with **`temperature=0`
   staying centrally fixed inside those frozen adapters** (U22 neither sets nor overrides it). **At tier-U no provider is
   reached at all** -- the engine is an **offline fake**. Real provider access arrives only with `JUDGE-EVAL-DEFERRED`,
   whose keys are **`secrets-config`'s (SEC-3)**. **U22 introduces no key, no endpoint, no service, no topology.**
4. **No deployed service / no new dependency / no route of its own** -- a source-level Python package under
   `backend/llm_judge/`; **`promptfoo` already floored**, **`requirements.txt` NOT edited**, **no new dependency**; **no
   WIRE-1 route** -- U22 is an out-of-band evaluation harness, never wired to a route.
5. **No new secret / env var / service** -- **no key is read at tier-U**; keys are **`secrets-config`'s**; **no corpus**
   (tier-B **NOT authorized, NOT required**); **no fitted-model artifact**.

### âš‘ The U22-specific question, assessed HEAD-ON rather than waved through: do the three register items constitute infrastructure?
This is the one candidate that could have blocked a skip, so it was tested against the real distinction rather than by
analogy. **All three resolve to application / tooling / generation deferrals with NAMED NON-U22 OWNERS -- none is
infrastructure topology:**
- **`PROMPTFOO-CLI-DEFERRED`** *(the strongest candidate -- Node + npx + a pinned CLI + telemetry opt-out **sounds**
  infrastructure-ish)*. **It is a LOCAL/CI TOOLCHAIN concern, not a cloud topology concern**: it provisions **no service, no
  endpoint, no environment, no network binding, no deployed resource**. The promptfoo CLI is a **dev/eval-time tool run
  out-of-band** -- which is precisely **why `NFR-JUDGE-PERF-1` records that U22 owns NO runtime SLO**: memo-quality
  evaluation is **never on the request path and is never deployed**. Moreover its **five discharge criteria were already
  written and owner-attributed** in the approved NFR Requirements -- it is a **named deferral with its own discharge
  contract**, not an undesigned topology awaiting this stage. And if the CLI is ever wired into CI, **that is CI/deploy
  config -- `deploy-config`'s (U23) domain**, already complete -- the same shape as U4's provider wrapping being deferred
  to deploy-config.
- **`JUDGE-EVAL-DEFERRED`** -- needs the **tier-B corpus** (**`corpus-generator`'s**, via the `R` edge; **NOT authorized**)
  and **live keys** (**`secrets-config`'s**, SEC-3). **Neither is U22's topology to design.**
- **`FEWSHOT-ANCHOR-UNIMPLEMENTED`** -- a **generation-side application** concern owned by **`memo-agent-core` (U4)** or a
  future explicitly-authorized change. **Not infrastructure at any reading.**

**The assessment surfaced NO genuine U22-owned infra concern. Nothing improvised; nothing waved through; neither outcome
defaulted to.** -> **SKIP correct, no STOP.**

**Skip roster now TWENTY**: intake Â· document-sanitizer Â· rules-engine Â· memo-agent-core Â· auth-rbac Â· audit-store Â·
quality-gates Â· corpus-generator Â· secrets-config Â· admin-cli Â· ui-shell Â· ui-queue Â· ui-memo-view Â· ui-approval-gate Â·
ui-override-form Â· ui-history Â· outlier-model Â· ui-outlier-view Â· memo-extensions Â· **llm-judge** -- the **4th Phase-2
skip**. **The three real non-skips remain `database` Â· `observability` Â· `deploy-config`** (re-verified on disk this
session: `ls -d guide-docs/build/*/infrastructure-design` returns **exactly those three**).
**âš‘ This is the FINAL Infrastructure Design assessment in the entire 23-unit build.**

**`llm-judge` (U22) stage status**: Functional Design [x] Â· NFR Requirements [x] Â· NFR Design [x] Â· **Infrastructure Design
[x] SKIPPED (logged, rule-justified)** Â· **Code Generation [ ] -- the LAST stage for U22 and the LAST stage of the entire
23-unit decomposition** (Part-1-plan-then-Part-2-generate, its own approval gate; **no code until the plan is reviewed**).
**4 of 5 stages complete.**

**Register (unchanged)**: 22 of 23 complete; **1 remains: `llm-judge` (U22)**, now at its final stage. Composition-root
**Q1-B divergence OPEN**; **R2-R5 unwired** (R4 a `501` stub); **tier-B UNAUTHORIZED**; **`audit_store` Docker-guard gap
DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN**; **`OBS-SINK-DEFERRED` OPEN**;
**`DEPLOY-MIGRATE-DEFERRED` OPEN**; **`PROMPTFOO-CLI-DEFERRED` Â· `JUDGE-EVAL-DEFERRED` Â· `FEWSHOT-ANCHOR-UNIMPLEMENTED`**
(U22's three, **all three re-confirmed at this stage as NON-infrastructure**); `testresults.txt` append-vs-overwrite open
housekeeping.

**Guardrails held**: **NO infra artifact** (`guide-docs/build/llm-judge/infrastructure-design/` **NOT created**); **no
code**; **`backend/llm_judge/` still ABSENT**; **`requirements.txt` NOT edited**; **`pyproject.toml` NOT edited**; the
frozen FD, the approved NFR Requirements and the approved NFR Design **re-opened NONE**; **WIRE-1 untouched**; the **17
frozen P1 units untouched INCLUDING `memo-agent-core`**; **`outlier-model` (U18) Â· `memo-extensions` (U19) Â·
`ui-outlier-view` (U20) Â· `observability` (U21) Â· `deploy-config` (U23) untouched** (read-only re-reads only:
`unit-of-work.md`, `execution-plan.md`, the skip roster); the **CLOSED composition root untouched**; **tier-B NOT
authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition
unchanged**. **NO file written** beyond this state entry and the append-only `audit.md` entry. **STOPPED** at the
Infrastructure Design 2-option gate (1. Request Changes / 2. Continue -> Code Generation).


## BUILD -> `llm-judge` (U22) -- **Infrastructure Design SKIP APPROVED (Continue)** -> Code Generation Part 1 (Plan) WRITTEN; STOP at the plan-file gate -- 2026-07-19

**Infrastructure Design SKIP APPROVED 2026-07-19 (option 2, Continue -> Code Generation)** -- the logged, rule-justified
SKIP (**the 20th overall Â· the 4th Phase-2 skip**) is **CLOSED**. U22 advanced to **Code Generation -- the 5th and LAST of
its stages, and the LAST stage of the entire 23-unit decomposition.**

**Wrote Part 1 (Plan) ONLY**: `guide-docs/build/plans/llm-judge-code-gen-plan.md`. **NO CODE. Nothing under
`backend/llm_judge/` created (still ABSENT).**

**âš‘ LIVE BASELINE MEASURED, NOT CITED FROM MEMORY**: `pytest backend --collect-only` -> **1230 tests collected**, which
**reconciles exactly** with the recorded **1194 passed / 31 skipped / 5 pre-existing `audit_store` Docker-absence errors**
(1194 + 31 + 5 = 1230). U22 is **purely additive**; the baseline must not regress and **the 5 Docker errors + 31 skips must
stay exactly unchanged**.

**Section 1 -- component -> module map.** Layout is **already PINNED by the approved NFR Design**
(`EXPECTED_PRODUCTION_MODULES = {rubric.py, schemas.py, pipeline.py, engine.py}`) and matches the **measured sibling
convention** (`outlier_model` Â· `memo_extensions` Â· `observability` are all **flat, no subpackages**) -- so it is **stated,
not re-litigated**. **Header-comment deliverables confirmed explicit on ALL FOUR production modules** (holds no LLM Â· edits
no frozen unit Â· declares no verdict Â· no network/Node/npx at tier-U), with the standing rule restated: **documentation
only, NEVER enforcement** -- every one of those properties is **independently enforced by a C-JUDGE-5 scan with a detector
self-test**, and **no test asserts on docstring text** *except* DISCLOSE-1's checklist, whose subject **is** the disclosure.

**Section 2 -- full TDD test -> target map**, every `NFR-JUDGE-*` at its NFR-pinned tier, **both load-bearing pairs at
full-highest**: **EXEMPT-1** positive-witness teeth over the three-sample composition (detector: a wrongly-scored Ollama
makes `scored_count` read **3**) **+** the **genuinely-separate degenerate-set predicate** (detector: the builder's **own
precondition fails at construction**); **NOEDIT-1**'s frozen-path scan **+ NOMETRIC-1**'s **provenance scan as PRIMARY**
with the **corroborating property-read** against `observability`'s `METRIC_DEFINITIONS` and `deploy-config`'s
`grafana-dashboard.json` -- **explicitly read-only, NEITHER SUITE RE-RUN**, technique **reused** from
`deploy_config/tests/test_scope.py` with U22's one addition (**no-nested-`panels`**, so future row-nesting **fails loudly**).
Plus **THRESH-1**'s explicit boundary teeth (`aggregate == 4` PASSES / `3.99` FAILS, `>=` explicit) Â· **INGATE-1** /
**EXEMPTSCOPE-1** scope-partition teeth Â· **ANCHOR-1**'s **honestly-scoped** teeth per Q2-A (**plumbing + unsplittability,
NOT engine-side discrimination**) Â· **DISCLOSE-1**'s token checklist **with the anti-conflation self-test in BOTH
directions** Â· **CLIDEFER-1**'s satisfiable + non-vacuous Protocol teeth **with NO by-value interop replica** Â·
**EVALDEFER-1**'s absence teeth Â· **NODEMO-1**'s planted-token detector Â· **ADVISORY-1/NOVERDICT-1**'s structural + token
teeth. **No orphan.**

**Section 3 -- leaf-first build order** as directed: domain model (no deps) -> fixtures substrate -> engine seam ->
eval pipeline -> **StructuralGuard scanning the COMPLETED production tree** -> coverage gate.
**Section 4 -- coverage gate**: `--cov=backend/llm_judge`, **no omit** (Q3-A, `observability` verbatim); global
**`--cov-fail-under=90` UNCHANGED**; U22's tree expected at **100%**; **restated that BR-JUDGE-6/8/9's verification is the
presence/absence scans, ORTHOGONAL to line coverage**, so 100% must not be misread as covering them.
**Section 5 -- all HOLDS restated.**

**FIVE `[Answer]` questions, all BLANK, in full with lettered options (rec A throughout), each genuinely Code-Gen-only and
none re-opening a frozen or approved decision**:
- **Q1 -- where the `DeclaredScoreEngine` fake lives. âš‘ MEASURED ON DISK, AND IT CONTRADICTS A PARENTHETICAL IN MY OWN
  APPROVED NFR DESIGN**: `logical-components.md` wrote *"(`tests/fakes.py`)"*, but **NO unit in the build has a
  `tests/fakes.py`** -- every fake class lives in that unit's **`tests/fixtures.py`** (`CapturingThinkingClient`,
  `FakeDecisionRecordSource`, `FailingDecisionRecordSource`, `FakeOutlierSignal`, `ByValueOutlierResult` in U19;
  `RecordingTraceSink`, `RecordingMetricExporter` in U21). Rec **A**: `fixtures.py`, matching the convention -- the NFR
  Design's **binding** requirement (**the fake is NEVER in production**, so CLIDEFER-1's scan has a clean production set) is
  satisfied either way since `tests/` is excluded from every production scan; the `fakes.py` parenthetical was
  **illustrative, not load-bearing**. **Flagged rather than silently followed either way.**
- **Q2 -- `sample_id` convention** guaranteeing `degenerate_all_in_gate_set()` and `in_gate_samples()` are **never
  identity-equal**. Rec **A**: distinct literal **prefixes** (`ingate-*` / `exempt-*` / `degen-*` / `anchor-*`) **plus a
  dedicated test asserting the id sets are DISJOINT** -- the separation **asserted, not merely intended**; fully
  deterministic. **B** rejected (adjacent numbering invites a renumber-into-collision); **C** (UUIDs) rejected as
  non-deterministic.
- **Q3 -- where DISCLOSE-1's and CLIDEFER-1's token literals LIVE, and what they are.** Rec **A**: a **`DEFERRED_REGISTER`
  constant in `engine.py`** carrying **item name Â· owner Â· rationale Â· `discharged: False`** per item -- in-tree,
  **greppable**, **line-coverable**, and a **structured** subject for the negative assertion (`discharged is False`, **not
  prose-matching**), keeping tokens **out of `guide-docs/`** so the test tree stays self-contained. Anti-conflation keys
  DISCLOSE-1 on the **name + owner** field and CLIDEFER-1 on the **five discharge criteria** field. **B** rejected (a 5th
  production module when `EXPECTED_PRODUCTION_MODULES` is pinned at four); **C** rejected (prose-matching is exactly what
  U23's DOC-1 avoided -- it matched **tokens, not headings or prose**).
- **Q4 -- test-file organization.** Rec **A**: **one test file per target**, mirroring the measured sibling convention
  (U21 has 12 such files, U19 14, U18 15), with **EXEMPT-1's two halves kept in one `test_exempt.py`** so the pair's
  complementarity is visible in one place **while remaining two distinct mechanisms**, and `test_perf_observed.py` using
  the **exact sibling filename**.
- **Q5 -- `pyproject.toml` `--cov` placement + the `__init__.py` export surface.** Rec **A**: append after
  `--cov=backend/observability`, before `--cov-report=term-missing`, with the standing comment (**gate UNCHANGED**); and
  **`__init__.py` left EMPTY** because **nothing in the build imports `llm_judge`** -- it is the last unit, wraps the built
  system, and **no unit depends on it** -- so an export surface would be **speculative API**.

**`llm-judge` (U22) stage status**: Functional Design [x] Â· NFR Requirements [x] Â· NFR Design [x] Â· **Infrastructure Design
[x] SKIPPED (logged)** Â· **Code Generation [ ] Part 1 (Plan) WRITTEN -> STOPPED at the plan-file gate** (ambiguity-check
**after** the answers; Part 2 = the modules + test suite + `--cov` line + a live full-suite run + `code-summary.md` on
explicit go). **4 of 5 stages complete; the 5th engaged.**

**Register (unchanged)**: 22 of 23 complete; **1 remains: `llm-judge` (U22)**, at its final stage. Composition-root **Q1-B
divergence OPEN**; **R2-R5 unwired** (R4 a `501` stub); **tier-B UNAUTHORIZED**; **`audit_store` Docker-guard gap
DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN**; **`OBS-SINK-DEFERRED` OPEN**;
**`DEPLOY-MIGRATE-DEFERRED` OPEN**; **`PROMPTFOO-CLI-DEFERRED` Â· `JUDGE-EVAL-DEFERRED` Â· `FEWSHOT-ANCHOR-UNIMPLEMENTED`**
(U22's three, **to be disclosed by name in code at Part 2, NONE discharged**); `testresults.txt` append-vs-overwrite open
housekeeping.

**Guardrails held**: **NO CODE**; **`backend/llm_judge/` still ABSENT**; **`requirements.txt` NOT edited**;
**`pyproject.toml` NOT edited** (the `--cov` line lands at Part 2); the frozen FD + approved NFR Requirements + approved
NFR Design + the logged Infra SKIP **re-opened NONE**; **WIRE-1 untouched**; the **17 frozen P1 units untouched INCLUDING
`memo-agent-core`**; **`outlier-model` (U18) Â· `memo-extensions` (U19) Â· `ui-outlier-view` (U20) Â· `observability` (U21) Â·
`deploy-config` (U23) untouched** (read-only re-reads only: sibling module+test layouts, `pyproject.toml`'s `--cov` block,
and a **collect-only** baseline run that **executed no test**); the **CLOSED composition root untouched**; **tier-B NOT
authorized**; the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition
unchanged**. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1-Q5.


## BUILD -> `llm-judge` (U22) -- **Code-Gen Q1-Q5 ANSWERED (all A)** + ambiguity-check **CLEAN (3 folds)** + **Part 2 GENERATED + TESTED**; STOP at the Code Generation 2-option gate -- 2026-07-19

**Q1-Q5 all A** (embedded in the plan section 6). **Ambiguity-check RUN as plan section 6.5 -> CLEAN -- 3 folds resolved,
no genuine gap, no surface-and-stop.**

- **CG-JUDGE-Fold-1 [the called-out check] RESOLVED -- a disclosed Code-Gen-stage clarification, LEFT UN-RETRO-EDITED,
  exactly as ND-Fold-1 was handled.** What the approved `logical-components.md` states as **BINDING is honored exactly** --
  *"the fake lives in `tests/`, NEVER in production, so no production module can depend on it and CLIDEFER-1's scan has a
  clean production set"* -- and **`tests/fixtures.py` IS in `tests/`**. **The `(tests/fakes.py)` parenthetical is
  load-bearing on NOTHING**: `EXPECTED_PRODUCTION_MODULES` names only the four production modules, and C-JUDGE-5's scan
  **excludes `tests/` wholesale**, so no scan, target or pattern references the filename. -> approved artifact **NOT
  retro-edited**; discrepancy **disclosed in `code-summary.md` section 3.1**.
- **CG-JUDGE-Fold-2 RESOLVED -- ADVISORY-1's verdict-token scan is PRODUCTION-ONLY, and that is FORCED by a frozen shape.**
  **`DecisionMemo.recommendation` is a REQUIRED field** on the frozen U4 model, so every memo fixture MUST carry a verdict
  value -- the memo **UNDER JUDGMENT (judge INPUT)**, which the approved NFR text already distinguishes from a verdict
  *"used as a judge OUTPUT"*. The **structural half** carries the real teeth and is unaffected by fixture content.
- **CG-JUDGE-Fold-3 RESOLVED -- NODEMO-1's scope is DELIBERATELY ASYMMETRIC** to ADVISORY-1's: it **also** scans
  `tests/fixtures.py`, because the FD requires the hand-authored **reference memo** be demographic-free. By-construction
  strength recorded: **`JudgedSample` carries `memo` + `rule_report` + `provider` ONLY -- no `ApplicantProfile` field**, so
  no demographic value can structurally enter a judged sample.

**PART 2 GENERATED -- TDD, tests-first, leaf-first exactly per plan section 3.**
**Modules**: `backend/llm_judge/{__init__.py (EMPTY per Q5-A), schemas.py, rubric.py, engine.py, pipeline.py}` +
`tests/{__init__.py, fixtures.py, structural.py}` + **15 test files, one per target** (Q4-A).
**`pyproject.toml`: ONE line added** (`--cov=backend/llm_judge` after observability's, **no omit**, standing comment;
**`--cov-fail-under=90` UNCHANGED**). **`requirements.txt` NOT edited; no new dependency.**

**âš‘ VERIFIED NUMBERS (measured, not assumed)**: backend **1308 passed / 31 skipped / 5 pre-existing `audit_store`
Docker-absence errors**. Baseline **1194 / 31 / 5** -> **+114 new tests, ZERO REGRESSION**; **skips unchanged at 31, Docker
errors unchanged at 5** (U22 adds neither). **`backend/llm_judge` at 100% on EVERY production module** (`__init__` 0 Â·
`engine` 23 Â· `pipeline` 37 Â· `rubric` 7 Â· `schemas` 55 stmts) with **no omit**. **Global 99.86%, gate HELD** (was 99.85%).
Isolated U22 suite: **114 passed in 0.74s**.

**âš‘ FOUR TEST FAILURES FOUND AND FIXED DURING THE RUN -- reported, not quietly patched; ONE WAS A REAL DEFECT IN THE SCAN
ITSELF**: the demographic detector used a naive substring test, so **`"city"` matched inside `"ethnicity"`** -- it would
have reported the WRONG attribute and masked which one actually appeared. **Fixed to whole-word matching** (`\b`
boundaries), with **`test_contains_token_matches_whole_words_only` added as a permanent regression guard**. The other three:
self-scanning files legitimately containing the tokens they scan for; each now **excludes itself by name** (the sibling
units' 'holds the token by necessity' pattern), and **my own docstrings were reworded rather than any assertion weakened**
-- so **all four production modules and the fixtures carrying the reference memo remain fully scanned**.

**Both LOAD-BEARING pairs at full-highest, as realized**:
- **EXEMPT-1** -- positive-witness teeth (`scored_count == 2` âˆ§ `exempt_count == 1` âˆ§ the Ollama sample **PRESENT**), its
  detector (`scored_count` reads **3** on a mis-partition), the engine **provably never asked to score** the exempt sample,
  **plus** the genuinely-separate `is_nonvacuous_exemption_set` guard -- with
  **`test_a_degenerate_set_would_report_exempt_count_zero` demonstrating WHY the guard exists** (the degenerate set is
  otherwise **indistinguishable** from a correct in-gate run) -- **plus three disjointness tests** proving the fixture
  families can never be identity-equal.
- **NOEDIT-1 / NOMETRIC-1** -- the frozen-path scan with a detector over **every** frozen prefix, **plus** the
  **provenance** scan (no U22 module declares a metric -- the claim **nothing else in the build makes**), with the
  read-only property assertions **corroborating** (five names by value; five panels; **no nested `panels` key** so future
  row-nesting fails loudly). **`test_noedit.py` also asserts BEHAVIOURALLY that running the suite leaves both frozen
  artifacts byte-identical.**

**Other realizations disclosed in `code-summary.md`**: `SampleScore.aggregate`/`.passed` are **`None`** for exempt records,
deliberately **not `0.0`/`False`** (which would read as *"failed"* rather than *"not scored"* -- an unacceptable ambiguity
in an advisory system); `EXEMPT_REASON_MEMO_QUALITY` + the `exempt_reason` field are the **realization of approved target
EXEMPTSCOPE-1**, not a new FD entity.

**`llm-judge` (U22) stage status**: Functional Design [x] Â· NFR Requirements [x] Â· NFR Design [x] Â· **Infrastructure Design
[x] SKIPPED (logged, the 20th skip)** Â· **Code Generation [x] Part 2 GENERATED + TESTED -> STOPPED at the 2-option
completion gate**. **5 of 5 stages complete pending the gate. Its approval CLOSES THE FINAL UNIT of the 23-unit
decomposition.**

**Register**: 22 of 23 complete; **`llm-judge` (U22) awaiting its final gate**. Composition-root **Q1-B divergence OPEN**;
**R2-R5 unwired** (R4 a `501` stub; core demo path not runnable end-to-end); **tier-B UNAUTHORIZED**; **`audit_store`
Docker-guard gap DEFERRED**; **`OUTLIER-IN-PROSE` OPEN**; **`MCP-TRANSPORT-DEFERRED` OPEN**; **`OBS-SINK-DEFERRED` OPEN**;
**`DEPLOY-MIGRATE-DEFERRED` OPEN**; **`PROMPTFOO-CLI-DEFERRED` Â· `JUDGE-EVAL-DEFERRED` Â· `FEWSHOT-ANCHOR-UNIMPLEMENTED`**
(**now realized in code as `engine.DEFERRED_REGISTER` with `discharged=False`; NONE discharged**); `testresults.txt`
append-vs-overwrite open housekeeping (**still open** -- the file was overwritten per the established pattern, and that is
noted in the file itself).

**Guardrails held**: **no frozen unit edited** -- U4's `DecisionMemo`/`RuleResultReport` imported **READ-ONLY**, its **test
tree never touched**, `prompt_builder.py` never opened; **U19's provider adapters not imported at all** (U22 drives no
adapter at tier-U -- the seam is the injected `RubricEngine`); **U21's `METRIC_DEFINITIONS` and U23's
`grafana-dashboard.json` read READ-ONLY, NEITHER SUITE RE-RUN, both asserted byte-identical after the run**; **no new
dependency, no promptfoo import in production** (asserted at run time via `sys.modules`); the **17 frozen P1 units and all
five other Phase-2 units untouched**; the **CLOSED composition root untouched**; **tier-B NOT authorized, not reached**;
the **`audit_store` Docker-guard gap untouched**; **no other unit started**; the **23-unit decomposition unchanged**.
**STOPPED** at the Code Generation 2-option completion gate.


## âš‘ BUILD â†’ `llm-judge` (U22) â€” **Code Generation APPROVED (Continue)** â†’ **U22 COMPLETE (5/5)** â†’ **THE ENTIRE 23-UNIT DECOMPOSITION IS COMPLETE** â€” 2026-07-19

**Code Generation APPROVED 2026-07-19 (option 2, Continue)** â€” gate **CLOSED**. `llm-judge` (U22, EPIC-6, Phase 2) is
**COMPLETE â€” all 5 of its 5 stages**: FD âœ“ Â· NFR Requirements âœ“ Â· NFR Design âœ“ Â· **Infrastructure Design âœ“ SKIPPED-logged
(the 20th skip Â· the 4th Phase-2 skip)** Â· **Code Generation âœ“**.

**âš‘ THIS CLOSES THE ENTIRE 23-UNIT DECOMPOSITION.** `llm-judge` is the **23rd and FINAL complete build-loop unit** and the
**6th and final Phase-2 unit**. **All 17 Phase-1 units + all 6 Phase-2 units** (`outlier-model` U18 Â· `ui-outlier-view` U20 Â·
`memo-extensions` U19 Â· `observability` U21 Â· `deploy-config` U23 Â· `llm-judge` U22) are **built**.

**Final verified numbers**: backend **1308 passed / 31 skipped / 5 pre-existing `audit_store` Docker-absence errors
(UNCHANGED)**; baseline **1194 + 114 new, ZERO regression**; **`backend/llm_judge` at 100% on EVERY production module**
(`__init__` 0 Â· `engine` 23 Â· `pipeline` 37 Â· `rubric` 7 Â· `schemas` 55 stmts) with **`--cov=backend/llm_judge` and NO
omit**; **global gate HELD at 99.86%** (was 99.85%). The **two LOAD-BEARING pairs** ran at **full-highest** rigor with
detector self-tests â€” **EXEMPT-1** (positive-witness teeth + the genuinely-separate degenerate-set guard) and
**NOEDIT-1/NOMETRIC-1** (frozen-path scan + the provenance scan with corroborating read-only property assertions;
**neither U21's nor U23's suite re-run**).

**âš‘ QUALITY SIGNAL RECORDED, NOT GLOSSED â€” a REAL defect surfaced BY the process, not a routine green pass.** The
demographic detector initially used a **naive substring test**, so **`"city"` matched inside `"ethnicity"`** â€” it would have
reported the **WRONG attribute** and **masked which one actually appeared**. Fixed to **whole-word matching** (`\b`
boundaries) with **`test_contains_token_matches_whole_words_only` added as a permanent regression guard**. Three further
failures were **self-scanning files legitimately holding the tokens they scan for**; each now **excludes itself by name**
(the sibling units' established pattern) and **the docstrings were reworded rather than any assertion weakened** â€” so all
four production modules and the fixtures carrying the reference memo **remain fully scanned**.

**âš‘ THREE REGISTER ITEMS REMAIN OPEN AND UNDISCHARGED**, carried forward into the **completed-build register** and realized
in code as **`engine.DEFERRED_REGISTER`** with **`discharged=False`** on each: **`PROMPTFOO-CLI-DEFERRED`** Â·
**`JUDGE-EVAL-DEFERRED`** Â· **`FEWSHOT-ANCHOR-UNIMPLEMENTED`**. **U22 claims no discharge of any of them.**

### Final Infrastructure Design tally across the whole build
**3 REAL non-skip passes** â€” `database` Â· `observability` Â· `deploy-config` â€” and **20 logged, rule-justified skips**.
The `unit-of-work.md` *"comprehensive at Infrastructure Design"* annotation appears **exactly three times** (L218, L248,
L250) and maps **1:1** onto those three real passes.

### FINAL DEFERRED-DECISIONS / CROSS-CUTTING REGISTER (complete, carried through)
1. **Composition root â€” Q1-B divergence**: **OPEN**.
2. **R2â€“R5 unwired**; **R4 still a `501` stub**; the **core underwriting demo path is not runnable end-to-end**.
3. **tier-B corpus run**: **UNAUTHORIZED**, and **confirmed not applicable to any unit across the whole build**.
4. **`audit_store` Docker-guard hygiene gap**: **DEFERRED** â€” **31 skips + 5 Docker errors, stable across every unit**
   since first identified.
5. **`OUTLIER-IN-PROSE`**: **OPEN and unassigned**.
6. **`MCP-TRANSPORT-DEFERRED`**: **OPEN**, non-blocking.
7. **`OBS-SINK-DEFERRED`**: **OPEN** â€” the **live Langfuse/Prometheus/Grafana code-attachment half** (the deployment half is
   already realized as committed config).
8. **`DEPLOY-MIGRATE-DEFERRED`**: **OPEN** â€” the migration runner's **CLI entrypoint**.
9. **`PROMPTFOO-CLI-DEFERRED`**: **OPEN** *(new, U22)*.
10. **`JUDGE-EVAL-DEFERRED`**: **OPEN** *(new, U22)*.
11. **`FEWSHOT-ANCHOR-UNIMPLEMENTED`**: **OPEN** *(new, U22 â€” owned by `memo-agent-core` (U4) or a future
    explicitly-authorized change; never U22's to discharge)*.
12. **`testresults.txt` append-vs-overwrite**: **OPEN** housekeeping.

**Guardrails held**: **no unit begun**; **WIRE-1 untouched**; the **17 frozen P1 units untouched INCLUDING
`memo-agent-core`**; **`outlier-model` (U18) Â· `ui-outlier-view` (U20) Â· `memo-extensions` (U19) Â· `observability` (U21) Â·
`deploy-config` (U23) untouched**; the **CLOSED composition root untouched**; **tier-B NOT authorized**; the **`audit_store`
Docker-guard gap untouched**; the **23-unit decomposition unchanged and now COMPLETE**. Files updated for this approval:
the `guide-state.md` **top status** (spliced to BUILD PHASE COMPLETE, prior U23 status preserved behind a
`<!-- superseded -->` marker) + this completion entry + the append-only `audit.md` entry.
**STOPPED â€” NOTHING STARTED. The next decision is the user's alone.**


## âš‘âš‘ SCOPE B OPENED â€” the CLOSED composition root is RE-OPENED and the 23-unit decomposition is EXTENDED (explicitly authorized) â€” 2026-07-19

**AUTHORIZATION**: **explicit, user-given, logged in `audit.md` BEFORE any design work**, mirroring the discipline the
original composition-root **Scope A** pass was logged under.

### What changes status here â€” two things held untouchable for the entire build
1. **The CLOSED composition root (`backend/app/`) is RE-OPENED under Scope B.** It was closed at the end of the Scope A
   integration pass and guarded by a NOEDIT-style scan in **every** subsequent unit for 23 units. **Status: RE-OPENED
   (Scope B).**
2. **The 23-unit decomposition is being EXTENDED.** It was completed earlier today with `llm-judge` (U22). Scope B adds
   genuinely-new domain-state work that **no existing unit owns**. **Status: EXTENDED beyond the frozen 23.**

### Rationale (recorded, as required for a deliberate deviation)
**R2â€“R5 were repeatedly identified across the build as "un-designed domain state which belongs in its own stage
(Scope B/C), not smuggled into a wiring pass."** They are **register item #2 â€” the ONLY item marked BLOCKING** on the
completed-build register: only **R1/R6/R7** are live, so an application cannot today be submitted, drafted and committed
through the running system. Scope B is the stage those deferrals always pointed at, now authorized.

### Scope of the CURRENT pass â€” scoping/planning ONLY
**NO code Â· NO wiring Â· NO FD artifact.** Ground truth re-established **from disk** (not from memory or conversation
summaries), then a plan file surfacing the genuinely-open design decisions as **numbered `[Answer]` tags â€” improvising
none of them**. **STOP at the plan-file gate.**

### Holds accepted for this pass
- All **23 completed units consumed BY SHAPE, editing NONE of their internals.**
- The reopening is scoped to **the composition root + genuinely-new Scope-B domain-state artifacts ONLY**.
- **âš‘ Any need to touch a frozen unit â€” specifically `database`'s (U15) migration sequence â€” is surfaced as its OWN
  explicit authorization question (plan Q3) and is NOT assumed.** This is a real fork with a real consequence.
- **WIRE-1's frozen contract text NOT touched** Â· **tier-B NOT authorized** Â· the **`audit_store` Docker-guard gap NOT
  touched**.

### Register interaction
Addresses **#2 (R2â€“R5 unwired / core demo path not runnable end-to-end)**. **Interacts with #1 (the composition root's
Q1-B divergence)** â€” since Scope B re-opens the root that owns it, whether to resolve or continue deferring it is
**surfaced as plan Q6, not silently decided either way**. All other register items unchanged.

**Next**: disk ground-truth re-establishment â†’ `guide-docs/build/plans/scope-b-r2-r5-plan.md` (eight `[Answer]` questions)
â†’ **STOP at the plan-file gate.**


## SCOPE B â€” Q1â€“Q8 ANSWERED (all A) + ambiguity-check **NOT CLEAN (2 folds + 1 GENUINE GAP)** â†’ **SURFACE-AND-STOP at Q9**; U24 NOT logged, NO FD begun â€” 2026-07-19

**Q1â€“Q8 all A** (embedded in the plan Â§2.9 with the user's verbatim rationale). **Ambiguity-check ran as plan Â§2.5 â†’
NOT CLEAN.** The instruction to confirm U24 and begin FD was **explicitly conditional on "if clean"** â€” it is not, so
**the U24 extension was NOT logged and NO FD was begun.**

- **âœ… SCOPEB-Fold-1 [check (i)] RESOLVED â€” two migration sequences CAN share one database; Q3-A is sound.**
  Measured: `_ensure_tracking_table()` uses **`CREATE TABLE IF NOT EXISTS`** (a second runner is safe); tracking is keyed by
  **`filename VARCHAR PRIMARY KEY`**, not ordinal or path, so U15's `0001_initial_schema.sql` and a U24
  `0001_case_lifecycle.sql` are **distinct keys and may both be numbered `0001`**; `apply_all()` only skips files in **its
  own** `migrations_dir`. **Two constraints pinned for FD**: **(1)** the PK is the **bare filename**, so an identically-named
  U24 migration would be **SILENTLY SKIPPED â€” a no-op, not an error**; and since the glob is `[0-9][0-9][0-9][0-9]_*.sql`, a
  `u24_` prefix would not match, so **the namespace must live in the descriptive part**. **(2) Grants**: `0002_grants.sql`
  grants the audit roles on **`audit_record` + `applicant_profile_snapshot` ONLY**, so new U24 tables have **no audit-role
  grants** â‡’ the pending store is reached via the **`DATABASE_URL` owner engine** the composition root **already
  constructs**. **No new grants required; no U15 edit implied.**
- **âœ… SCOPEB-Fold-2 [check (ii)] RESOLVED â€” no contradiction between Q2-A and Q4-A; the risk is real and routed to FD.**
  Q2-A defines *what* the states are; Q4-A defines *that* advancement is explicit. **But** with a separate trigger an
  application **CAN sit at `submitted`/`profiled`/`evaluated` indefinitely** if nothing invokes the next transition, R4
  honestly reporting `status: pending` forever â€” an **under-specification both answers acknowledge**, not a conflict.
  **Carried as a NAMED FD question** with three sub-decisions: eager-vs-ä¸‰-step advancement; what invokes
  `evaluated â†’ drafted`; and whether a stuck application has a retry/re-drive path.
- **â›” SCOPEB-GAP-1 [check (iii)] â€” GENUINE GAP.** The **writer-engine half IS confined** â€” `backend/app/tests/
  test_no_write_route.py` (incl. `test_no_writer_engine_is_ever_constructed`) sits **inside the re-opened territory**, so
  revising it is within Scope B exactly as Q5-A accepted; U22's and U23's `test_noedit.py` scan **their own** authored sets;
  U23's `test_boot.py` is unaffected; and U23's **route-table** assertion still passes because **Scope B adds NO route**
  (R2â€“R5 already exist at those exact paths/methods and merely stop raising `501`).
  **BUT** `backend/deploy_config/tests/test_routes.py::test_no_new_route_file_added_under_backend_app_by_u23` â€” part of
  **`NFR-DEP-ROUTES-1`, a LOAD-BEARING full-highest target of the FROZEN U23** â€” asserts an **EXACT-SET EQUALITY over
  `backend/app/routes/`**: `assert route_files == {"__init__.py","session.py","decisions.py","not_wired.py"}`.
  **Q1-A states the wiring pass "adds the four route modules"** â‡’ adding **any** file there, or renaming/removing
  `not_wired.py`, **BREAKS a frozen unit's load-bearing test**. Its **stated intent is a provenance claim about U23**, but
  its **implementation is a directory-wide exact-set assertion firing on ANY author's addition** â€” intent and implementation
  diverge, and Scope B is the first thing to hit it. Discovering this at the wiring pass â€” **after U24's five full stages** â€”
  is the late failure this discipline exists to prevent.

**Raised as Question 9** (options: **A** implement R2â€“R5 **in place** in the existing three route files, zero frozen edits;
**B** authorize a **narrow surgical edit** to U23's test â€” **would be the first frozen-unit edit in the build**, currently
forbidden by this pass's holds; **C** accept the regression â€” rejected as a default).

**NOT DONE, deliberately**: the **U24 extension was NOT logged** as a 24th unit; **NO FD plan written**; **NO FD artifact**.
**The decomposition therefore remains at 23 units**; Scope B remains open at its scoping gate.

**Guardrails held**: WIRE-1's contract text **NOT touched**; **Q1-B NOT resolved**; **no frozen unit's internals touched**
(U15 read only through its parameterized seam; U23's test read **read-only** to discover the obstacle); the `audit_store`
Docker-guard gap **NOT touched**; **tier-B NOT authorized**; **no code, no wiring artifact**. **Only 1 file written**: the
plan (Â§2.9 answers + Â§2.5 ambiguity-check + Q9). **STOPPED awaiting the Q9 decision.**


## âš‘ SCOPE B â€” Q9 ANSWERED (A) + re-check **CLEAN** â†’ **DECOMPOSITION EXTENDED TO 24 UNITS: `case-lifecycle` (U24) CONFIRMED** + register now **13 items**; U24 FD Part 1 (Plan) WRITTEN; STOP at the FD plan-file gate â€” 2026-07-19

**Q9: A** â€” implement R2â€“R5 **IN PLACE** in the existing route files; `backend/app/routes/` keeps exactly
`{__init__.py, session.py, decisions.py, not_wired.py}`, so U23's frozen exact-set assertion passes **untouched with ZERO
frozen edits**. The user chose A over B deliberately: B (relaxing U23's test to the provenance check its docstring
describes) is *"the more honest long-term fix"* and the divergence is *"a real latent defect"*, **but** it would be the
**first frozen-unit edit in the entire build** and *"deserves its own separate, deliberate authorization decision â€¦ not
folded into this pass as a side effect."*

### âš‘ NEW REGISTER ITEM #13 â€” `NOTWIRED-FILENAME-STALE`
**What**: once R2â€“R5 are wired in place inside `not_wired.py`, that **filename no longer describes its contents**.
**Why deferred**: U23's frozen `NFR-DEP-ROUTES-1` asserts **exact-set equality** over `backend/app/routes/` rather than the
**provenance claim its docstring describes**, so Scope B must keep the filename to keep that frozen test green. **The rename
and the test relaxation are a MATCHED PAIR** belonging to their own authorized change.
**Owner**: a **future authorized change** Â· **Blocking?** **NON-BLOCKING** (naming honesty only).
**NOT done in Scope B**: the file is **NOT renamed**; U23's test is **NOT edited**. Disclosed rather than silently
reconciled â€” the `DEPLOY-MIGRATE-DEFERRED` / `fixtures.py`-vs-`fakes.py` pattern.
â‡’ **The deferred-decisions register now stands at THIRTEEN items.**

### Ambiguity-check RE-RUN (Q1â€“Q9) â€” **CLEAN** (plan Â§2.6)
- **âœ… SCOPEB-Fold-3** â€” Q1-A's wiring clause **RESTATED and binding**: from *"adds the four route modules"* to
  ***"wires R2â€“R5 IN PLACE in the existing route files, adding NO new file under `backend/app/routes/`."*** Everything else
  in Q1-A unchanged.
- **âœ… SCOPEB-Fold-4** â€” **in-place wiring does NOT push domain logic into `backend/app/`.** Measured: the composition root
  already has a two-layer thin-adapter pattern â€” `session.py` (R1) is `Depends` + dict projection; `decisions.py` (R6/R7)
  is `Depends` + frozen-service call + projection; and `projections.py` is documented verbatim as *"the composition root's
  ONLY transformation layer â€¦ pure functions, no I/O, no state."* Scope B's R2â€“R5 handlers take the **identical** shape,
  with **all domain logic living in U24** and injected via `dependencies.py`. **The invariant holds by following the
  existing pattern, not by exception.**
- **âœ… Composition-root tests to revise â€” ENUMERATED, all confined to `backend/app/tests/`** (re-opened territory; **no
  frozen unit's test touched**). **Still pass**: one-non-GET-route Â· seven-routes-whole-surface Â· others-read-only.
  **Must be revised**: `test_its_first_statement_raises_the_marker` Â· `test_the_marker_module_constructs_no_service_and_
  reads_no_body` Â· `test_no_writer_engine_is_ever_constructed` Â· `test_no_commit_service_or_context_provider_exists` Â·
  `test_no_repository_write_method_is_called`. **âš‘ What must not be lost**: the substantive guarantee becomes *"every write
  goes through the frozen `DecisionCommitService`"* (whose CON-BR4 gate + independent authz re-check run inside
  `commit()`) â€” the revised tests must assert **that**, not simply delete the old ones.

### âš‘ DECOMPOSITION EXTENDED â€” `case-lifecycle` (U24)
**The 23-unit decomposition is now a 24-unit decomposition.** U24 is the **first unit added after the original
decomposition was completed**, authorized under Scope B. It enters the **full per-unit BUILD loop** (FD â†’ NFR Requirements
â†’ NFR Design â†’ Infrastructure Design â†’ Code Generation), exactly as all 23 prior units did. **The in-place
composition-root wiring pass comes ONLY after U24's full loop completes.**

**U24 FD Part 1 (Plan) WRITTEN**: `guide-docs/build/plans/case-lifecycle-functional-design-plan.md`. **NO FD artifact; no
code; no wiring; `backend/case_lifecycle/` ABSENT.** Contains the DISCOVER-carryover check, the frozen contracts re-read
(not re-derived), the **depth recommendation with justification**, and **numbered `[Answer]` questions** â€” including the
three the user named: the **Q3-A migration-namespace/tracking** constraints, the **Q4-A trigger-invocation** detail, and
the **pending-store schema sufficient to reconstruct a `CommitContext`**.

**`case-lifecycle` (U24) stage status**: **Functional Design â³ Part 1 (Plan) WRITTEN â†’ STOPPED at the plan-file gate** Â·
NFR Requirements â³ Â· NFR Design â³ Â· Infrastructure Design â³ Â· Code Generation â³. **0 of 5 stages complete.**

**Guardrails held**: **WIRE-1's contract text NOT touched** Â· **Q1-B NOT resolved** Â· **`not_wired.py` NOT renamed** Â·
**U23's test NOT edited** Â· **no frozen unit's internals touched** (U15 consumed only through its parameterized migration
seam per Q3-A) Â· the **`audit_store` Docker-guard gap NOT touched** Â· **tier-B NOT authorized** Â· **NO code, NO wiring
artifact**. Files written: the Scope B plan (Q9 + item #13 + Â§2.6) + the U24 FD plan + these log entries.


## U24 `case-lifecycle` â€” FD Q1â€“Q7 ANSWERED (all A) + ambiguity-check **NOT CLEAN (2 folds + 1 GENUINE GAP)** â†’ **SURFACE-AND-STOP at Q8**; NO FD artifact â€” 2026-07-19

**Q1â€“Q7 all A** (embedded in the plan Â§4). **Ambiguity-check ran as plan Â§4.5 â†’ NOT CLEAN.** Generation was explicitly
conditional on *"if clean"* â€” it is not, so **NO FD artifact was produced**.

### â›” CASE-GAP-1 [check (i)] â€” GENUINE GAP: Q2-A's JSON serialization diverges from the frozen CANON-SER mechanism
**Measured, not inferred.** `0001_initial_schema.sql` persists **the SAME TWO SHAPES** Q2-A names â€” but **NOT as JSON**:
```
rule_results       BYTEA  -- RuleResultReport as opaque CANON-SER bytes (BR-DB-10)
profile_canonical  BYTEA  -- original ApplicantProfile as opaque CANON-SER bytes (BR-DB-10)
content_hash       VARCHAR -- sha256 of the canonical bytes (pre-replay tamper check)
```
`backend/common/canon_ser.py` states why, verbatim: *"CANON-SER guarantees the Â§2.1 properties so **replay comparison and
`content_hash` integrity checks are meaningful â€” the same logical content serializes to the same bytes on every run**:
**P1** stable lexicographic key ordering Â· **P2** `Decimal` as string, never IEEE float Â· **P3** canonical scalar forms Â·
**P4** no volatile fields injected."* **`model_dump_json()` guarantees none of P1â€“P4.**
**Three concrete consequences**: **(1) hash stability** â€” JSON that reorders keys or renders a `Decimal` as a float breaks
equality **silently on a later run**, not loudly at write time; **(2) a serialization seam across the commit boundary** â€”
the pending store would hold JSON while `audit_record` holds CANON-SER bytes for **the same two shapes**, so the commit
path must convert, and that conversion becomes where replay fidelity is won or lost; **(3) `Decimal` is not incidental** â€”
money fields are `Decimal` throughout (`rules_engine` rejects `float` via `_reject_float`), exactly what P2 protects.
**âš‘ My own Q2-A recommendation was CORRECTED**: it cited *"Precedent: `applicant_profile_snapshot` already persists a
profile as a stored artifact"* â€” **true but imprecise**; the precedent persists it as **canonical bytes, not JSON**.
Q2-A's stated **intent** (no frozen schema duplicated in DDL; version stamps first-class) is **fully satisfied by CANON-SER
too**. **The options differ only in the serializer â€” and only one was designed for replay.**
â‡’ **Raised as Question 8** (rec **A**: CANON-SER `BYTEA` + `content_hash`, reusing the **same shared
`backend/common/canon_ser.py`** `intake` and `audit-store` already use, so artifacts are **byte-identical on both sides of
the commit boundary**; **B** = Q2-A's JSON as stated, costs named; **C** = mixed, rejected).

### âœ… CASE-Fold-1 [check (ii)] â€” RESOLVED **by disclosure**: WIRE-1 is genuinely silent on `failed`
`MemoView.status` is a **CLOSED two-value discriminator** (`ready | pending`), with *"pending â†’ the pipeline has **not
yet** produced a memo."* A failed case fits the **literal** wording but not *"not **yet**"*. â‡’ **WIRE-1 is silent.**
**Resolution consistent with the holds**: `failed` is an **INTERNAL U24 state**, projected to `pending` at the R4 wire
boundary (the only legal value). Nothing frozen is violated; the imprecision is **disclosed, not hidden**.
**âš‘ NEW REGISTER ITEM #14 â€” `MEMOVIEW-FAILED-STATE-UNMODELLED`**: owner **a future authorized WIRE-1 contract amendment**;
**NON-BLOCKING** (the loss is diagnostic precision at the wire, not correctness). Amending WIRE-1 is the honest long-term
fix and is **forbidden by this pass's holds**, exactly as Q9-B's test relaxation was.
â‡’ **The register now stands at FOURTEEN items.**

### âœ… CASE-Fold-2 [check (iii)] â€” RESOLVED: routing is **NOT** internal; U24 **must** invoke it explicitly
**Measured**: a grep of `memo_agent_core/orchestrator.py` for `borderline`/`route_borderline`/`ThinkingMode`/`thinking`
returns **ZERO hits** â€” the orchestrator does not route. `memo_extensions/borderline_router.py` exposes a **free, pure**
`route_borderline(rule_report, outlier_signal=None) -> ThinkingMode` holding **no client, no provider, no network** (a
provider is *structurally un-injectable* â€” there is no `client` parameter), reading the outlier **by shape**.
â‡’ **Concrete FD consequence**: U24's `CasePipeline` must **explicitly** call `route_borderline(...)` after the outlier step
and hand the resulting `ThinkingMode` to the adapter, which takes it as a **constructor argument**. **Routing is not free;
it is a step U24 owns.** No user decision needed â€” **recorded now rather than discovered at NFR Design**.

**NOT DONE, deliberately**: **NO FD artifact** â€” `guide-docs/build/case-lifecycle/` **ABSENT** (no `domain-entities.md`,
no `business-rules.md`, no `business-logic-model.md`); **no code, no wiring**; `backend/case_lifecycle/` **ABSENT**.

**`case-lifecycle` (U24) stage status**: **Functional Design â³ Part 1 ANSWERED + ambiguity-check NOT CLEAN â†’ STOPPED at
Q8** Â· NFR Requirements â³ Â· NFR Design â³ Â· Infrastructure Design â³ Â· Code Generation â³. **0 of 5 stages complete.**

**Guardrails held**: **WIRE-1's contract text NOT touched** (item #14 **discloses** the silence rather than amending it) Â·
**Q1-B NOT resolved** Â· **`not_wired.py` NOT renamed** Â· **U23's test NOT edited** Â· **no frozen unit's internals touched**
(all reads read-only: `0001_initial_schema.sql`, `canon_ser.py`, `orchestrator.py`, `borderline_router.py`, the WIRE-1
contract) Â· the **`audit_store` Docker-guard gap NOT touched** Â· **tier-B NOT authorized** Â· **no code, no wiring**.
**Only 1 file written**: the U24 FD plan (Â§4 answers + Â§4.5 ambiguity-check + item #14 + Q8).
**STOPPED awaiting the Q8 decision.**


## U24 `case-lifecycle` â€” **Q8 ANSWERED (A)** + ambiguity-check **RE-RUN â†’ CLEAN** + **FD Part 2 GENERATED (3 artifacts)**; STOP at the FD 2-option gate â€” 2026-07-19

**Q8: A** â€” reuse the shared **CANON-SER** utility for both `rule_results` and `applicant_profile`, stored as **`BYTEA` +
`content_hash`**, mirroring `0001_initial_schema.sql`'s own pattern rather than introducing a second, weaker serialization
strategy for the same two shapes. The four version stamps stay **first-class scalar columns** exactly as Q2-A decided â€”
**only the encoding of the two nested frozen shapes changed**, from JSON to the shared canonical serializer already built
and tested for this purpose.

### Ambiguity-check RE-RUN (Q1â€“Q8) â€” **CLEAN** (plan Â§4.6)
- **âœ… CASE-Fold-3 [check (i)] â€” RESOLVED, and better than the question assumed.** `canon_ser(value: Any) -> bytes` has
  **NO shape coupling** â€” it is purely structural. **âš‘ One real subtlety, ALREADY SOLVED by a frozen artifact**:
  `canon_ser` accepts **plain values, not Pydantic models**, and the reduction **must** be `.model_dump(mode="python")` â€”
  `mode="json"` would pre-stringify `Decimal`s so the `$dec` envelope never fires, **silently losing P2 type fidelity**.
  **`backend/audit_store/canon_adapter.py` already exists, generic over `BaseModel`, written for EXACTLY these two
  shapes** (*"one convention for both â€¦ no fork, no Â§2.1 change"*) and is the same adapter `commit_service.py:122` uses.
  â‡’ **U24 reuses it BY SHAPE** â€” no new adapter, no re-derivation. Inherited constraint: CANON-SER **reserves `$`-prefixed
  keys**.
- **âœ… CASE-Fold-4 [check (ii)] â€” RESOLVED: canonicalization follows Q4-A's transition boundary, it is not a free choice.**
  The **two rich shapes** are canonicalized **in the eager transaction**; the **four stamps** land at **drafting**. A
  single late point would mean holding un-persisted domain objects across a trigger boundary, defeating the durability the
  pending store exists for. **`content_hash` is computed at the same call site as the bytes it attests**, so it can never
  drift. **âš‘ No interaction with `route_borderline`**: routing sits **downstream**, writes nothing, and **`ThinkingMode` is
  deliberately NOT persisted** â€” it is a pure function of `(rule_report, outlier_signal)`, both persisted, so it is
  **exactly re-derivable from stored state**. Its absence is a decision, not an oversight.

### âš‘ REGISTER ITEM #14 â€” `MEMOVIEW-FAILED-STATE-UNMODELLED` (added)
**What**: WIRE-1's `MemoView.status` admits only `ready | pending`; U24's `failed` terminal state has **no wire
representation** and projects to `pending`, which reads as *"not yet drafted"* rather than *"drafting failed."*
**Why deferred**: adding a third status value **amends WIRE-1's frozen contract text** â€” forbidden by Scope B's holds.
**Owner**: a **future authorized WIRE-1 amendment** Â· **Blocking?** **NON-BLOCKING** (diagnostic precision at the wire, not
correctness). **NOT resolved here.** â‡’ **The register now stands at FOURTEEN items.**

### FD PART 2 GENERATED â€” 3 artifacts at `guide-docs/build/case-lifecycle/functional-design/`
- **`domain-entities.md`** â€” the **five states + the internal `failed`** with its **disclosed wire-projection** Â·
  **`PendingApplication`** and **`PendingRecommendation`** with the **CANON-SER `BYTEA` + `content_hash` + scalar-stamp**
  schema Â· **`PendingCommitContextProvider`** (supplies **context ONLY**; no gate, no authz, no write) Â· **`CasePipeline`**
  with **`route_borderline` as a required explicit step** Â· **`CaseMigrationSequence`** with the namespacing + collision
  guard Â· and the **explicit reference-not-own table** covering every frozen shape/seam/utility **including
  `canon_ser.py` and `borderline_router.py`**.
- **`business-rules.md`** â€” **`BR-CASE-1..14`**, each grounded + checkable at tier-U: the five-state model and legal
  transitions (1â€“2) Â· the **eager-advance / separate-trigger** boundary (3â€“4) Â· the **`failed` terminal state** and its
  **disclosed wire projection** (5â€“6) Â· **CANON-SER byte-identity for replay safety** (7) Â· **frozen-adapter reuse with the
  `mode="python"` rationale** (8) Â· **canonicalization at the finalizing transition** (9) Â· the **explicit
  borderline-routing step with `ThinkingMode` re-derivable** (10) Â· **migration namespacing + collision guard** (11) Â·
  **in-process invocation confined to U24's own sequence** (12) Â· **the commit boundary never re-implemented** (13) Â·
  **no new metric** (14) Â· plus **the five inherited invariants restated** and a **no-orphan traceability table**.
- **`business-logic-model.md`** â€” the step-by-step lifecycle Â· which frozen unit acts at each transition Â· the
  **pending â†” committed boundary table** Â· the **validated Mermaid** + full text alternative Â· the tier split Â· settled
  items.

**âš‘ MERMAID VALIDATED MECHANICALLY (by script, not by eye) â€” ALL 7 RULES PASS**: 18 nodes / 20 edges; alphanumeric IDs;
every label quoted; **zero labels with any non-alphanumeric-or-space character**; blocks balanced (no `subgraph`);
**rectangle-only** (shape token checked per node ID); **zero edge labels**; exactly one `flowchart`; **no dangling
endpoints**. **Four structural claims verified BY THE SCRIPT**: **(1)** `state committed audit record` has **exactly ONE
inbound edge, from the frozen commit service** â€” **NON-service edges into committed: NONE**, so the boundary crossing is a
**visible** graph property; **(2)** the **provider has NO edge to committed** (the structural expression of BR-CASE-13);
**(3)** **`route borderline` sits visibly between outlier and memo**; **(4)** **canonicalization appears twice** (eager
transaction + drafting stamps), and **`failed â†’ r4 view`** makes the disclosed projection visible.

**`case-lifecycle` (U24) stage status**: **Functional Design âœ“ Part 1 ANSWERED (Q1â€“Q8) + ambiguity-check CLEAN + Part 2
GENERATED â†’ STOPPED at the FD 2-option completion gate** Â· NFR Requirements â³ Â· NFR Design â³ Â· Infrastructure Design â³ Â·
Code Generation â³. **1 of 5 stages complete pending gate.**

**Guardrails held**: **WIRE-1's contract text NOT touched** (#14 discloses the silence rather than amending it) Â· **Q1-B
NOT resolved** Â· **`not_wired.py` NOT renamed** Â· **U23's test NOT edited** Â· **no frozen unit's internals touched**
(`canon_ser.py`, `canon_adapter.py`, `borderline_router.py`, `orchestrator.py`, `0001_initial_schema.sql` all **read-only,
by shape**) Â· the **`audit_store` Docker-guard gap NOT touched** Â· **tier-B NOT authorized** Â· **NO code, NO wiring
artifact** Â· `backend/case_lifecycle/` **ABSENT** Â· nothing under `backend/app/` touched.
Files written: the U24 FD plan (Â§4.6) + the **3 FD artifacts** + these log entries.


## U24 `case-lifecycle` â€” **FD APPROVED (Continue)** â†’ NFR Requirements Part 1 (Plan) WRITTEN; STOP at the plan-file gate â€” 2026-07-19

**FD APPROVED 2026-07-19 (option 2, Continue â†’ NFR Requirements)** â€” U24's Functional Design is **COMPLETE** (3 artifacts
frozen: `domain-entities.md` Â· `business-rules.md` **BR-CASE-1..14** Â· `business-logic-model.md`; folds **CASE-Fold-1..4**;
gap **CASE-GAP-1** resolved by Q8-A; register item **#14** disclosed). Gate **CLOSED**. U24 advanced to **NFR Requirements
â€” the 2nd of its 5 stages**. **Depth: comprehensive** (Q1-A).

**Wrote Part 1 (Plan) ONLY**: `guide-docs/build/plans/case-lifecycle-nfr-requirements-plan.md`. **NO NFR artifact; no code;
no wiring; `backend/case_lifecycle/` ABSENT; `pyproject.toml` NOT edited.**

**Â§2 â€” ALL FOURTEEN `BR-CASE-*` mapped to draft `NFR-CASE-*` targets, NO ORPHAN**, each with tier/rigor + pass/fail teeth:
**STATE-1** (full legal transition set) Â· **STATE-2** (explicit rejection teeth over the **illegal** set â€” skip-evaluation,
backward moves, terminal exits â€” with the illegal set **exhaustively enumerated against the state cross-product**) Â·
**EAGER-1** (reaches `evaluated` or leaves **NO partial row**) Â· **TRIGGER-1** (**the R4 read path invokes the pipeline
ZERO times** â€” the injected double records no calls) Â· **FAILED-1** (`failed` internally distinguishable from `evaluated`)
Â· **PROJECT-1** (a `failed` case yields a **WIRE-1-VALID** `MemoView` with `status == "pending"`, **plus a DOC-1-style
token checklist for register #14**, mirroring `llm-judge`'s DISCLOSE-1) Â· **âš‘ CANON-1** Â· **âš‘ ADAPTER-1** Â·
**CANONTIME-1** Â· **ROUTE-1** (router **actually invoked with real arguments**; mode **re-derivable from stored state
alone**) Â· **MIGNAME-1** (synthetic colliding filename **flagged**) Â· **MIGSCOPE-1** (never passes U15's default dir; **no
CLI entrypoint** â€” #8 not adopted) Â· **âš‘ COMMITBOUND-1** Â· **NOMETRIC-1** (mirrors `llm-judge`'s exactly, incl. the static
byte-unchanged check, **neither suite re-run**). Plus **PERF-1** (observed-never-gated) and **SEC-1** (governance).

**Â§3 â€” the proposed LOAD-BEARING set: THREE targets, with the reasoning stated.** Count in band (`deploy-config` 3;
`observability`/`llm-judge` 2 each) and U24 is comprehensive.
- **CANON-1 + ADAPTER-1 are a deliberate PAIR** covering one cluster by **two different mechanisms** â€” the same structure
  `llm-judge` used for EXEMPT-1 and NOEDIT-1/NOMETRIC-1. **CANON-1 is behavioural** (bytes really round-trip; the hash
  really catches a mutation) and would **still pass on a correct-but-FORKED serializer**; **ADAPTER-1 is structural** (U24
  uses the **frozen adapter**, never bypassing or re-deriving it) and would **still pass on a broken one**. **Neither alone
  suffices â€” that is why they are two.** Full-highest because this cluster carries **CASE-GAP-1's entire resolution**: if
  it drifts, hash equality breaks **silently on a later run**, surfacing only at replay.
- **COMMITBOUND-1** is the third and arguably the most consequential in the build â€” the assertion that **U24 never
  finalizes a decision**. Carries **both** a structural scan and a behavioural assertion.

**THREE `[Answer]` questions, all BLANK, in full with lettered options (rec A throughout), each grounded in DISK
MEASUREMENT**:
- **Q1 â€” live-DB tier. âš‘ MEASURED: the two existing Docker guards behave DIFFERENTLY, which is decisive.**
  `audit_store/tests/test_pg_integration.py` uses `pytest.importorskip("testcontainers.postgres")` â€” it skips on a
  **missing module** but **ERRORS at fixture setup when Docker is not running** (**these are the 5 pre-existing errors**,
  register #4). `database/tests/conftest.py` uses `_docker_available()` â†’ `docker.from_env().ping()` and **SKIPS CLEANLY**
  (part of the 31 skips). Rec **A**: **two tiers** â€” all pure logic (state machine, canonicalization, hashing, pipeline
  orchestration, provider assembly, transition rules) at **tier-U with NO database at all**; only the **actual SQL
  round-trip** at `@pytest.mark.integration` using **`database`'s known-good guard**, so it **adds ZERO errors**.
  **âš‘ Flagged**: this **will add new clean SKIPS** when Docker is absent â€” a **visible, expected delta on the 31** that
  must be **stated in the completion report, not discovered**. **C rejected on the evidence** â€” adopting `audit_store`'s
  pattern would **grow the error count**, breaking the standing hold and propagating a known defect sitting one directory
  from a known-good one.
- **Q2 â€” fixture families.** Rec **A**: one shared `tests/fixtures.py` with **deliberately-separate named families** (the
  U18/U19/U22 convention), with **two families given the `llm-judge` treatment specifically**:
  **`illegal_transition_cases()` returned as ONE collection** (mirroring `anchoring_pair()`'s unsplittability, so STATE-2's
  rejection set cannot be trimmed one case at a time) and **`drafting_failure_double()` as its own family** (mirroring
  `exempt_witness_sample()`, so FAILED-1 cannot be weakened by an edit made for the success path).
- **Q3 â€” coverage. âš‘ The brief expected "no omit"; MEASURED, a carve-out IS the established precedent.**
  `pyproject.toml`'s omit list already carves out **every** live-DB/SQL-exec module in the build â€” `pg_repository.py`,
  `database/migration_runner.py`, `schema_introspector.py`, `fidelity_comparator.py`, `admin_cli/pg_writer.py` â€” each with
  the **same** stated rule: *"the pure-logic modules stay counted and are unit-covered to >=90% (QA-6)."* Rec **A**:
  `--cov=backend/case_lifecycle` with a **NARROW omit of exactly U24's SQL-exec shim**, following `pg_repository.py`
  **verbatim**; **everything else counted and expected at 100%**; the `--cov-fail-under=90` gate **UNCHANGED**. **B ("no
  omit") noted as meaning something DIFFERENT here** than it did for `observability`/`llm-judge`, which had **no SQL-exec
  module** â€” so the same words would cost U24 either an artificially low number or live-DB imports at tier-U.

**`case-lifecycle` (U24) stage status**: **Functional Design âœ“** Â· **NFR Requirements â³ Part 1 (Plan) WRITTEN â†’ STOPPED at
the plan-file gate** Â· NFR Design â³ Â· Infrastructure Design â³ Â· Code Generation â³. **2 of 5 stages engaged.**

**Register (unchanged at 14)**: #1 Q1-B Â· #2 R2â€“R5 (the item Scope B addresses) Â· #3 tier-B Â· #4 `audit_store` Docker-guard
Â· #5 `OUTLIER-IN-PROSE` Â· #6 `MCP-TRANSPORT-DEFERRED` Â· #7 `OBS-SINK-DEFERRED` Â· #8 `DEPLOY-MIGRATE-DEFERRED` Â·
#9 `PROMPTFOO-CLI-DEFERRED` Â· #10 `JUDGE-EVAL-DEFERRED` Â· #11 `FEWSHOT-ANCHOR-UNIMPLEMENTED` Â· #12 `testresults.txt` Â·
#13 `NOTWIRED-FILENAME-STALE` Â· #14 `MEMOVIEW-FAILED-STATE-UNMODELLED`.

**Guardrails held**: **no NFR artifact** Â· **no code, no wiring** Â· **`backend/case_lifecycle/` ABSENT** Â·
**`pyproject.toml` NOT edited** Â· the **frozen FD re-opened NONE** Â· **WIRE-1's contract text NOT touched** Â· **Q1-B NOT
resolved** Â· **`not_wired.py` NOT renamed** Â· **U23's test NOT edited** Â· **no frozen unit's internals touched**
(read-only re-reads only: `pyproject.toml`'s omit list, `audit_store` + `database` test guards) Â· the **`audit_store`
Docker-guard gap NOT touched** Â· **tier-B NOT authorized** Â· nothing under `backend/app/` touched.
**Only 1 file written**: the plan. **STOPPED** at the plan-file gate awaiting Q1â€“Q3.


## U24 `case-lifecycle` â€” **NFR Req Q1â€“Q3 ANSWERED (all A)** + ambiguity-check **CLEAN (3 folds)** + **Part 2 GENERATED (2 artifacts)**; STOP at the NFR Requirements 2-option gate â€” 2026-07-20

**Q1â€“Q3 all A** (embedded in the plan Â§4). **Ambiguity-check ran as plan Â§4.5 â†’ CLEAN â€” 3 folds resolved, no gap.**

- **âœ… CASE-Req-Fold-1 [check (i)] â€” the tier-I test is SELF-CONTAINED; U15's migrations are NOT needed.**
  `database/tests/conftest.py` is the exact template: **`_docker_available()` pings the daemon INSIDE the fixture body,
  before any container is constructed** â€” which is precisely why it **skips cleanly** where `audit_store`'s
  `importorskip`-only pattern reaches container construction and **errors** (the 5). U24 mirrors it, passing
  `migrations_dir=<U24's own>`. **No U15 dependency**, for three structural reasons: **(1)** no cross-unit FK â€”
  `PendingRecommendation` FKs to `PendingApplication`, both U24's; the `recommendation_id` later seen in `audit_record` is
  a **logical reference, not a DB FK** (the `BR-DB-11` posture); **(2)** U24's store uses the **owner engine**, so its
  migration **grants to no U15 role** and needs no `0002_grants.sql`; **(3)** `applied_migrations` is created
  **idempotently**. **âš‘ Condition pinned**: if U24's migration ever granted to a U15-owned role, containment would break â€”
  **MIGSCOPE-1 asserts it does not.**
- **âœ… CASE-Req-Fold-2 [check (ii)] â€” a `failed` case STRUCTURALLY cannot reach the commit boundary.** R5 is keyed by
  **`recommendation_id`**, the PK of **`PendingRecommendation`**, which is created **ONLY at the `drafted` transition**. A
  `failed` case **never reaches `drafted`**, so **the object R5 is keyed by never exists for it**; the provider raises and
  R5 returns 404. **The failed path and the commit path do not intersect.** **Two things pinned so this stays structural**:
  **(a) atomicity** â€” creating the `PendingRecommendation` and moving to `drafted` happen in **ONE transaction** (the only
  route by which the intersection could ever open); **(b) a POSITIVE assertion**, not an absence â€” **no
  `PendingRecommendation` exists for any case in state `failed`**, and driving `drafting_failure_double()` to `failed`
  then calling the provider **raises**.
- **âœ… CASE-Req-Fold-3 [check (iii)] â€” âš‘ COVERAGE-OMIT â‰  SCAN-EXCLUSION; conflating them would be a real hole.**
  The coverage `omit` excludes the SQL-exec shim from **line-coverage measurement**; **ADAPTER-1's scan set is NOT
  narrowed by it** and **includes the shim**. **The shim is in the scan set precisely BECAUSE it is out of the coverage
  set** â€” the omit is about *where it is exercised* (tier-I), the scan about *what it may contain*. If the scan inherited
  the omit, a direct `canon_ser(...)` call inside the shim would be **structurally invisible**. And the "right reason" is
  **ASSERTED, not assumed**: ADAPTER-1 asserts **positively** that the shim **contains no canonicalization call at all** â€”
  making *"the shim doesn't canonicalize"* a **tested property rather than a design intention**.

**PART 2 GENERATED â€” 2 artifacts** at `guide-docs/build/case-lifecycle/nfr-requirements/`:
- **`nfr-requirements.md`** â€” **seventeen finalized targets** covering all fourteen `BR-CASE-*` with **NO ORPHAN**, each
  with assertion + acceptance + tier + rigor. **THREE LOAD-BEARING full-highest**, each with its mechanism spelled out:
  **CANON-1** (behavioural byte-identity: round-trip identical Â· `Decimal`/`date` return as themselves Â· hash stable
  across runs Â· **a flipped byte FAILS** Â· a `float` **raises**) Â· **ADAPTER-1** (structural: no direct `canon_ser`, no
  re-implemented `mode="python"` reduction, **the shim IS in the scan set**, detectors for both a synthetic direct call
  **and** a synthetic `mode="json"`) Â· **COMMITBOUND-1** (structural: no gate/authz/`audit_record` write in U24, each with
  its own detector; behavioural: the provider returns **context and nothing more**, raises for an unknown id; **plus
  Fold-2's positive `failed`-case assertion and the atomicity pin**). Plus STATE-1 Â· **STATE-2** (illegal set
  **exhaustively enumerated against the state cross-product**, returned as one **unsplittable** collection) Â· EAGER-1
  (**no partial row**) Â· TRIGGER-1 (**R4 invokes the pipeline ZERO times**) Â· FAILED-1 Â· **PROJECT-1** (WIRE-1-valid
  `pending` projection **+ a DOC-1-style token checklist for register #14**) Â· CANONTIME-1 Â· ROUTE-1 (**spy records the
  real arguments**; mode **re-derivable from stored state**) Â· MIGNAME-1 Â· MIGSCOPE-1 Â· **PERSIST-1 (tier-I)** Â·
  NOMETRIC-1 (mirrors `llm-judge`'s exactly, **neither suite re-run**) Â· PERF-1 Â· SEC-1. **Full traceability table** +
  the five inherited invariants mapped + a **13-row Security-Guardrails table with human-in-the-loop as its own explicit
  LOAD-BEARING row**. **No blocking finding.**
- **`tech-stack-decisions.md`** â€” **CASE-D1..D9**; the fixture families table with **why each is its own family**;
  **CASE-D3** the known-good guard with the *inside-the-fixture-body* mechanism explained; **CASE-D4** the self-containment
  reasoning; **CASE-D5** the frozen-adapter reuse with the `mode="json"` hazard named; the **coverage decision with the
  precedent quoted verbatim** and the **coverage-omit â‰  scan-exclusion** table. **NO NEW DEPENDENCY** â€” verified on disk:
  **`testcontainers[postgresql]>=4.0.0` is floored (L33) AND installed**, and already exercised by `database`'s own
  integration tier. **âš‘ Contrast recorded**: unlike `llm-judge`'s `promptfoo` (floored but a **shim with an absent
  engine**), **U24 has no dependency gap at all.**

**`case-lifecycle` (U24) stage status**: **Functional Design âœ“** Â· **NFR Requirements âœ“ Part 1 ANSWERED + ambiguity-check
CLEAN + Part 2 GENERATED â†’ STOPPED at the 2-option completion gate** Â· NFR Design â³ Â· Infrastructure Design â³ Â·
Code Generation â³. **2 of 5 stages complete pending gate.**

**âš‘ Carried forward for Code-Gen (stated now, not to be discovered)**: U24's **tier-I tests will add new CLEAN SKIPS** to
the 31 when Docker is absent. The **5 errors stay exactly unchanged**. This delta is **expected and must be reported
explicitly** in the completion report.

**Register unchanged at 14 items.**

**Guardrails held**: **no code, no wiring** Â· **`backend/case_lifecycle/` ABSENT** Â· **`requirements.txt` NOT edited** Â·
**`pyproject.toml` NOT edited** (the `--cov` line + omit land at Code-Gen) Â· **no new dependency** Â· the **frozen FD
re-opened NONE** Â· **WIRE-1's contract text NOT touched** Â· **Q1-B NOT resolved** Â· **`not_wired.py` NOT renamed** Â·
**U23's test NOT edited** Â· **no frozen unit's internals touched** (read-only re-reads only: `database/tests/conftest.py`,
`pyproject.toml`'s omit list, `requirements.txt`) Â· the **`audit_store` Docker-guard gap NOT touched** Â· **tier-B NOT
authorized** Â· nothing under `backend/app/` touched. Files written: the plan (Â§4.5) + the **2 NFR artifacts**.
**STOPPED** at the NFR Requirements 2-option completion gate (1. Request Changes / 2. Continue â†’ NFR Design).


## U24 `case-lifecycle` â€” **NFR Requirements APPROVED (Continue)** â†’ NFR Design Part 1 (Plan) WRITTEN; STOP at the plan-file gate â€” 2026-07-20

**NFR Requirements APPROVED (option 2, Continue â†’ NFR Design)** â€” U24's NFR Requirements is **COMPLETE** (2 artifacts
frozen: `nfr-requirements.md` with the **seventeen `NFR-CASE-*`** targets + `tech-stack-decisions.md`; folds
**CASE-Req-Fold-1..3**). Gate **CLOSED**. U24 advanced to **NFR Design â€” the 3rd of its 5 stages**. **Depth:
comprehensive.**

**Wrote Part 1 (Plan) ONLY**: `guide-docs/build/plans/case-lifecycle-nfr-design-plan.md`. **NO NFR Design artifact; no
code; no wiring; `backend/case_lifecycle/` ABSENT; `requirements.txt` and `pyproject.toml` NOT edited.**

**Â§2 â€” ALL SEVENTEEN `NFR-CASE-*` mapped to FIFTEEN named patterns `P-CASE-1..15`, NO ORPHAN.**
**âš‘ Â§2.1 states explicitly why CANON-1 and ADAPTER-1 are TWO patterns, not one** â€” the same reasoning `llm-judge` applied
to EXEMPT-1's and NOEDIT-1/NOMETRIC-1's two mechanisms: **P-CASE-1 is behavioural** (subject = the **bytes**; would **still
pass on a correct-but-FORKED serializer**) and **P-CASE-2 is structural** (subject = the **call sites**; would **still pass
on a broken serializer**). **Neither alone suffices â€” they read different things (bytes vs the AST), so no single edit can
weaken both â€” and they CONVERGE on ONE call site**, which the diagram makes graphical. Also: **P-CASE-3
`ComposedCommitBoundaryPattern`** carrying **both** halves (structural: no gate/authz/write; behavioural: context-only,
raises on unknown id, **plus the positive failed-case-cannot-reach-boundary assertion and its atomicity dependency**);
**P-CASE-4 `ComplementDerivedTransitionPattern`** for STATE-1/STATE-2's exhaustiveness; **P-CASE-8
`TokenChecklistGovernancePattern`** (DISCLOSE-1 / DOC-1 lineage) for PROJECT-1; **P-CASE-12
`SelfContainedIntegrationTierPattern`** scoped to tier-I; plus P-CASE-5/6/7/9/10/11/13/14/15.

**Â§3 â€” EIGHT logical components `C-CASE-1..8`** (six production + two test substrates). **âš‘ C-CASE-3 (the SQL-exec shim) is
modelled explicitly as a DUAL-STATUS component** per CASE-Req-Fold-3: **coverage-OMITTED** (exercised at tier-I, the
`pg_repository.py` precedent) **but INCLUDED in ADAPTER-1's scan set**, with a **positive assertion that it contains no
canonicalization call at all** â€” the two sets are deliberately different.
**Â§3.1 â€” the reference-not-own check with THREE DISTINCT categories**: **(1) consumed BY SHAPE** (`DecisionMemo`,
`RuleResultReport`, `ApplicantProfile`, `OutlierResult` â€” read-only, import-to-read â‰  edit) Â· **(2) DRIVEN THROUGH AN
EXISTING INJECTION POINT** (the U19 provider adapters, `route_borderline`, `MigrationRunner`/`verify_checksums`,
`CanonSerAdapter` â€” invoked through their existing parameters; no seam widened; `temperature=0` stays centrally fixed
inside the frozen adapters) Â· **(3) COMPOSED WITH, NEVER RE-IMPLEMENTED** (`DecisionCommitService` â€” U24 supplies **only**
a `CommitContextProvider` and implements **no gate, no authz check, no write**). **âš‘ Stated explicitly: category 1 is
READ, category 2 is CALLED, category 3 is DEFERRED TO â€” a category-3 member appearing in U24's own logic would mean the
human-in-the-loop enforcement had been duplicated.**

**âš‘ DRAFT MERMAID MECHANICALLY VALIDATED (by script, not by eye) â€” ALL 7 RULES PASS**: 17 nodes / 17 edges; alphanumeric
IDs; every label quoted; **zero labels with any non-alphanumeric-or-space character**; blocks balanced (no `subgraph`);
rectangle-only (shape token checked per node ID); **zero edge labels**; one `flowchart`; **no dangling endpoints**.
**All THREE required structural properties verified BY THE SCRIPT**:
1. **Commit-boundary crossing** â€” `committed audit record` has **exactly ONE inbound edge, from the frozen commit
   service**; **NON-service edges into committed: NONE**; and **the provider's ONLY outbound edge is into the frozen
   service** (the graphical form of *"context only, never a write"*).
2. **The CANON-1 / ADAPTER-1 pair** â€” **both** `canon one behavioural round trip` **and** `adapter one structural scan`
   point at the **SAME** node, `canonicalization call site frozen adapter`: two independent verification paths converging
   on one call site.
3. **tier-I isolation** â€” `database migration sequence not applied here` has **ZERO edges**, and `tier i persistence test`
   is fed **only** by `u24 migration sequence own directory`. **The ABSENCE of any edge is the isolation property**
   (CASE-Req-Fold-1).

**FIVE `[Answer]` questions, all BLANK, in full with lettered options (rec A throughout), each a genuine pattern fork**:
- **Q1 transition-table representation** â€” rec **A**: declare the **LEGAL set only** and derive **ILLEGAL as its COMPLEMENT
  over the cross-product**, so **exhaustiveness is automatic and by construction** (a newly added state instantly appears
  in the derived illegal set with **no test edit**) and **two tables cannot drift**. **B rejected** â€” two hand-maintained
  tables *can* drift, and a new state would be silently absent from the illegal list, precisely the failure STATE-2 exists
  to prevent.
- **Q2 the SQL-exec shim's seam shape** â€” rec **A**: a **`CaseStore` Protocol** with an **in-memory fake at tier-U** and
  the SQL shim at tier-I (the established injected-Protocol precedent: U4's `LLMClient`, U19's adapters, U21's sinks,
  U22's `RubricEngine`). **Why it matters**: it is what makes **the whole pipeline and the provider's assembly logic
  tier-U-testable without a database** â€” including **COMMITBOUND-1's behavioural half** and EAGER-1, both currently
  specified as tier-U â€” and it makes the coverage split honest, since the **omitted module is exactly the Protocol's SQL
  implementation and nothing else**. **B would gut those targets.**
- **Q3 where the migration collision guard executes** â€” rec **A**: **in production at U24's apply call site**, plus a
  tier-U detector test. **Why**: the hazard (**a silently skipped migration â€” a no-op, not an error**) is a **production**
  hazard, so the guard belongs on the production path, where it is also counted and coverable. **C rejected** â€”
  import-time side effects are what this codebase has consistently avoided (the root reads settings at **request** time).
- **Q4 how `CasePipeline` signals a drafting failure** â€” rec **A**: a **`DraftOutcome` result object**, making both
  outcomes ordinary testable return values, the atomic boundary a **visible single branch**, and composing naturally with
  the frozen orchestrator's existing **`DecisionMemo | None`** (a `None` maps to a failure outcome, so **U24 adds no new
  failure vocabulary**).
- **Q5 where the `failed â†’ pending` wire projection lives â€” âš‘ a genuine tension, surfaced not resolved.** PROJECT-1 is
  **U24's** target so U24 must test it, but the composition root's `projections.py` is documented as *"the ONLY
  transformation layer."* Rec **A**: a **PURE projection function in U24** which the root **calls** at wiring time â€”
  the **`failed â†’ pending` decision is domain knowledge** (only U24 knows a failed case exists, and the root must not learn
  that vocabulary), it keeps PROJECT-1 **testable inside the unit that owns it**, and the root still owns assembling the
  wire body. **B noted as the cleanest reading of the root's role but would leave PROJECT-1 untestable within U24**;
  **C rejected** (U24 would own a WIRE-1 shape, becoming a second transformation layer).

**`case-lifecycle` (U24) stage status**: **Functional Design âœ“** Â· **NFR Requirements âœ“** Â· **NFR Design â³ Part 1 (Plan)
WRITTEN â†’ STOPPED at the plan-file gate** Â· Infrastructure Design â³ Â· Code Generation â³. **3 of 5 stages engaged.**

**Register unchanged at 14 items.** **Carried forward for Code-Gen**: U24's tier-I tests will add **new CLEAN SKIPS** to
the 31; the **5 errors stay exactly unchanged** â€” to be **reported explicitly**, not discovered.

**Guardrails held**: **no NFR Design artifact** Â· **no code, no wiring** Â· **`backend/case_lifecycle/` ABSENT** Â·
**`requirements.txt` and `pyproject.toml` NOT edited** Â· the **frozen FD and approved NFR Requirements re-opened NEITHER**
Â· **WIRE-1's contract text NOT touched** Â· **Q1-B NOT resolved** Â· **`not_wired.py` NOT renamed** Â· **U23's test NOT
edited** Â· **no frozen unit's internals touched** Â· the **`audit_store` Docker-guard gap NOT touched** Â· **tier-B NOT
authorized** Â· nothing under `backend/app/` touched. **Only 1 file written**: the plan. **STOPPED** at the plan-file gate
awaiting Q1â€“Q5.


## U24 `case-lifecycle` â€” **NFR Design Q1â€“Q5 ANSWERED (all A)** + ambiguity-check **CLEAN (3 folds)** + **Part 2 GENERATED (2 artifacts)**; STOP at the NFR Design 2-option gate â€” 2026-07-20

**Q1â€“Q5 all A** (embedded in the plan Â§5, with the user's explicit Q5 tradeoff acceptance). **Ambiguity-check ran as plan
Â§5.5 â†’ CLEAN â€” 3 folds resolved, no gap.** **âš‘ One fold CORRECTS a recommendation I made in Â§5; one adds an amplification
note to register #13.**

- **âš‘ CASE-ND-Fold-1 [check (i)] â€” RESOLVED, and it INVERTS my own Â§5 framing.** I had anticipated that exposing a
  transaction primitive would burden the in-memory fake with rollback simulation the SQL shim gets free â€” implying a
  **single composite method**. **Measured: the frozen precedent does the OPPOSITE, deliberately.**
  `audit_store/repository.py`'s **`AuditRepository` Protocol DOES expose `atomic()`**, and `InMemoryAuditRepository`
  **buffers inserts and flushes only on clean exit**, discarding on exception â€” *"simulating a transaction's both-or-neither
  rollback"* â€” with `insert()` **raising outside `atomic()`** and a built-in **`fail_on_insert` fault injector**.
  **âš‘ Why the precedent wins decisively**: with a **composite method** the fake would satisfy atomicity **TRIVIALLY** (a
  single body cannot half-execute in a single-threaded test), so **EAGER-1's *"no partial row"* and COMMITBOUND-1(d) would
  be VACUOUS at tier-U**. With `atomic()` + a buffering fake, the assertion **actually tests something**. â‡’ `CaseStore`
  **exposes `atomic()`**, mirroring the frozen Protocol verbatim; the fake's ~15 lines are **the precedent's own, not new
  machinery**. **My Â§5 concern was wrong and is corrected in the record rather than left standing.**
- **âœ… CASE-ND-Fold-2 [check (ii)] â€” RESOLVED: genuinely separate, with anti-conflation pinned.** Different **domain**
  (migration **filenames** vs **state pairs**), different **operation** (set **disjointness** vs set **membership**),
  different **owner** (C-CASE-7 vs C-CASE-1), different **failure mode** (a silently skipped migration vs an accepted
  illegal move). **âš‘ The only conceivable conflation would be a shared generic "guard" helper â€” pinned: there is none**,
  and *"both are set operations"* is a **superficial** similarity a later refactor must not unify.
- **âœ… CASE-ND-Fold-3 [check (iii)] â€” RESOLVED: no new file, no U23 breakage â€” PLUS a previously-unconsidered interaction
  with #13.** Measured: U23's `test_no_new_route_file_added_under_backend_app_by_u23` globs **`backend/app/routes/*.py`
  ONLY**, and **`projections.py` is at `backend/app/projections.py` â€” NOT under `routes/`**, so an import changes **no file
  set**; the route-table test asserts **(path, method)** and is unaffected; **no frozen test constrains `projections.py`'s
  contents or imports** *(the one out-of-root grep hit, `memo_extensions/tests/test_structural_guard.py`, refers to U19's
  own internal "read projections" concept, not the composition root's module)*; and U23's `structural.py`/`test_noedit.py`
  references to `backend/app` are **detector assertions about U23's own authored paths**, not directory-content
  constraints.
  **âš‘ THE PREVIOUSLY-UNCONSIDERED INTERACTION (flagged as asked)**: the eventual call chain becomes **`not_wired.py`
  (R4's handler) â†’ `projections.py` â†’ U24's `case_to_memo_view_state`**, so once R2â€“R5 are wired in place **the
  misleadingly-named file sits directly on the system's PRIMARY USER JOURNEY**, not merely on four `501` markers. This
  **does not change #13's disposition** â€” the rename stays a **matched pair** with U23's test relaxation, owned by a future
  authorized change â€” but it **materially raises the readability cost** of leaving it stale. **Recorded as an aggravating
  factor on register item #13** so the eventual rename pass has the full rationale.

**PART 2 GENERATED â€” 2 artifacts** at `guide-docs/build/case-lifecycle/nfr-design/`:
- **`nfr-design-patterns.md`** â€” **`P-CASE-1..15`**, each with **real signatures/mechanisms** spelled out. **THREE
  LOAD-BEARING**: **P-CASE-1** (behavioural byte round-trip incl. the mutation detector and the `float`-raises clause) Â·
  **P-CASE-2** (structural AST scan, **the shim IN the scan set** with a **positive no-canonicalization assertion**, and
  the **`mode="json"` detector** whose rationale is the silent P2-fidelity loss) Â· **P-CASE-3** (both halves + the positive
  failed-case assertion + the `atomic()` dependency). Plus **P-CASE-4**'s complement-derived exhaustiveness sweep,
  **P-CASE-5**'s `atomic()`-and-buffering-fake rationale, **P-CASE-8**'s pure projection with its ownership rationale,
  **P-CASE-11**'s production guard with the anti-conflation note, **P-CASE-12**'s clean-skip mechanism and self-containment,
  and P-CASE-6/7/9/10/13/14/15. **Full traceability, NO ORPHAN.**
- **`logical-components.md`** â€” **`C-CASE-1..8`** with **exact signatures**: `LEGAL_TRANSITIONS` as the **single source of
  truth** + `case_to_memo_view_state`'s `Literal["ready","pending"]` return (so a third status is **unrepresentable**) Â·
  the two pending entities with **`BYTEA` + `content_hash` + first-class stamps** Â· **C-CASE-3 as DUAL-STATUS**
  (coverage-omitted, scan-included) Â· **`CaseStore` Protocol WITH `atomic()`** and the buffering fake Â· **`DraftOutcome`**
  Â· the provider whose **return type is `CommitContext`** (so *"the provider committed something"* is unrepresentable) Â·
  `apply_case_migrations` with the **production** collision guard Â· the five fixture families. **The three-category
  reference-not-own check kept DISTINCT (READ / CALLED / DEFERRED TO)** with the explicit warning that a category-3 member
  in U24's logic would mean duplicated human-in-the-loop enforcement. **Component â†’ target coverage, NO ORPHAN.**

**âš‘ BOTH MERMAIDS MECHANICALLY VALIDATED (by script, not by eye) â€” ALL 7 RULES PASS ON BOTH** (patterns: 20 nodes/21 edges;
components: 18 nodes/20 edges). **All THREE required structural properties verified BY THE SCRIPT on BOTH**:
1. **Commit boundary** â€” `committed` has **exactly ONE inbound edge, from the frozen service**; **NON-service edges into
   committed: NONE**; and **the provider's ONLY outbound edge is into the frozen service**.
2. **CANON-1/ADAPTER-1 convergence** â€” **both** `canon one behavioural round trip` **and** `adapter one structural scan`
   point at the **SAME** canonicalization call-site node.
3. **tier-I isolation** â€” `database migration sequence not applied here` has **ZERO edges**; the tier-I test is fed **only**
   by U24's own sequence. Also visible: **one store Protocol with two implementations** (the fake and the shim).

**`case-lifecycle` (U24) stage status**: **Functional Design âœ“** Â· **NFR Requirements âœ“** Â· **NFR Design âœ“ Part 1 ANSWERED
+ ambiguity-check CLEAN + Part 2 GENERATED â†’ STOPPED at the 2-option completion gate** Â· Infrastructure Design â³ Â·
Code Generation â³. **3 of 5 stages complete pending gate.**

**Register at 14 items**, with **#13 `NOTWIRED-FILENAME-STALE` gaining an aggravating factor** (the stale-named file will
sit on the primary user journey once R2â€“R5 are wired in place). **Carried forward for Code-Gen**: U24's tier-I tests will
add **new CLEAN SKIPS** to the 31; the **5 errors stay exactly unchanged** â€” to be **reported explicitly**.

**Guardrails held**: **no code, no wiring** Â· **`backend/case_lifecycle/` ABSENT** Â· **`requirements.txt` and
`pyproject.toml` NOT edited** Â· the **frozen FD and approved NFR Requirements re-opened NEITHER** Â· **WIRE-1's contract
text NOT touched** Â· **Q1-B NOT resolved** Â· **`not_wired.py` NOT renamed** Â· **U23's test NOT edited** Â· **no frozen
unit's internals touched** (read-only re-reads only: `audit_store/repository.py`, `deploy_config/tests/*`,
`memo_extensions/tests/test_structural_guard.py`) Â· the **`audit_store` Docker-guard gap NOT touched** Â· **tier-B NOT
authorized** Â· nothing under `backend/app/` touched. Files written: the plan (Â§5.5) + the **2 NFR Design artifacts**.


## U24 `case-lifecycle` â€” **NFR Design APPROVED (Continue)** â†’ Infrastructure Design **ASSESSED â†’ SKIPPED (logged, rule-justified)** = the **21st skip** + the **FIRST Scope-B Infrastructure Design determination**; STOP at the Infra 2-option gate â€” 2026-07-20

**NFR Design APPROVED (option 2, Continue â†’ Infrastructure Design)** â€” U24's NFR Design is **COMPLETE** (2 artifacts
frozen: `nfr-design-patterns.md` **P-CASE-1..15** + `logical-components.md` **C-CASE-1..8**; folds **CASE-ND-Fold-1..3**).
Gate **CLOSED**. U24 advanced to **Infrastructure Design â€” the 4th of its 5 stages**.

**Infrastructure Design ASSESSED AT THE STAGE (not pre-assumed; neither outcome defaulted to) â†’ logged SKIP. NO infra
artifact created** (`guide-docs/build/case-lifecycle/infrastructure-design/` **NOT** created â€” consistent with all
**twenty** prior skips; the three real non-skips remain `database` Â· `observability` Â· `deploy-config`, re-verified on disk
this session).

> **âš‘ This was genuinely the hardest assessment in the build.** U24 introduces a **new persistent store**, a **new
> migration sequence**, and a **tier-I testcontainers integration test** â€” none of which `llm-judge` had. The determination
> therefore rests on measured comparison, not analogy.

### THE DECIDING INSTRUMENT â€” `database`'s own SEVEN-CATEGORY SWEEP, applied to U24

`database` (U15)'s real pass ran a **mandatory seven-category applicability sweep**. Applying that same instrument:

| # | Category | `database` (U15) â€” the real pass | **`case-lifecycle` (U24)** |
|---|---|---|---|
| 1 | Deployment Environment | **Applicable** â€” three tiers designed (dev Docker Â· **CI testcontainers** Â· prod Render) | **N/A** â€” adds **no tier**; runs in the tiers U15 already designed |
| 2 | Storage Infrastructure | **Applicable (CORE)** â€” *"`database` **IS** the storage topology"*; instance, co-located schema, `postgres:16` **pinned** | **N/A** â€” adds **tables into an already-provisioned, already-designed schema**; **zero new topology decisions** |
| 3 | Compute | N/A (justified) | **N/A** â€” no service, no worker; drafting is **in-process behind a trigger** |
| 4 | Messaging | N/A (justified) | **N/A** â€” **and deliberately so** (see the decisive finding below) |
| 5 | Networking | **Applicable (narrow)** â€” private URL, `sslmode=require`, pooling | **N/A** â€” same connection, same SSL, same pooling; **all U15's**; U24 adds no endpoint |
| 6 | Monitoring | **Applicable (narrow)** â€” provider metrics, readiness probe | **N/A** â€” **Q7-A: no new metric** (a sixth would break U21's frozen five + U23's five-panel scan) |
| 7 | Shared Infrastructure | **Applicable (CENTRAL)** â€” *"`database` **IS** shared infra"* | **N/A as an owner** â€” U24 is a **consumer**, isolated via the **owner engine**; introduces no shared resource and **no new role** |

**`database`: 5 applicable (2 core/central), 2 N/A. `case-lifecycle`: 0 applicable, 7 N/A with justification.**

### Check (1) â€” is "new persistent state + a migration sequence" sufficient on its own? **NO â€” measured against U15.**

**What U15 owns**: which Postgres Â· which **pinned version** Â· how many instances Â· **one-schema co-location** Â·
**three-tier provisioning** Â· the **grant-DDL execution mechanism** Â· connection/pooling/**SSL** Â· **migration execution
per environment** Â· the `secrets-config` env contract (`AUDIT_WRITER_URL`/`AUDIT_READER_URL` as **required**).
**What U24 owns**: **`.sql` files** and a call to an **already-parameterized runner**.

**âš‘ Every topology decision U24's migration depends on was already made and frozen by U15.** The sharpest framing:
**U15 answered *"what infrastructure?"* â€” U24 answers *"what tables?"*** Only the first is an Infrastructure Design
question. Adding rows to an existing, already-designed schema is **schema content**, not **infrastructure topology**.
**And U24 does not even brush the grant model**: MIGSCOPE-1 asserts its migration **grants to no U15-owned role** â€” the one
place it could have touched real topology, it provably does not.

### Check (2) â€” is the tier-I testcontainers pattern "infrastructure"? **NO â€” it is U15's ALREADY-DESIGNED tier.**

**Direct evidence, from U15's own sweep**: category 1 lists ***"CI (testcontainers Postgres, ephemeral per run)"*** as part
of **`database`'s** Deployment Environment. â‡’ the testcontainers tier is **already-designed infrastructure U24 CONSUMES**,
not new infrastructure U24 designs. And U24's use of it was **fully specified two stages ago**: **NFR-Req Q1-A** (which
guard, and why `database`'s clean-skip pattern rather than `audit_store`'s erroring one) and **NFR Design P-CASE-12** (the
exact fixture mechanism, the *ping-inside-the-body* reason it skips cleanly, and the self-containment proof).
**Nothing remains to design** â€” it is a **test-tooling decision, already resolved**.

### Check (3) â€” did U24's artifacts name deferred infrastructure topology? **NO â€” one mention, and it is Code-Gen work.**

**Measured across ALL SEVEN U24 artifacts** (3 FD + 2 NFR-Req + 2 NFR-Design): **exactly ONE** occurrence of
*"Infrastructure Design"*, and it is the compound catch-all
*"**Deferred to Infrastructure Design / Code-Gen**: exact module names; the scan token sets; **the migration file's DDL**;
the `pyproject.toml` `--cov` line"* â€” **every item a Code-Gen concern. Not one line of topology.**
**Contrast the real passes**: `observability` named *"the live Langfuse callbackâ†’checkpointer binding, the `/metrics` mount
+ scrape, the Grafana dashboard, keys via `secrets-config`, AC-7's deploy-time audit"*; `deploy-config` named the Render
service, the Vercel project, the rewrite/proxy, the migration release step. **U24's artifacts name none of that** â€” the
**identical signature to `llm-judge`'s SKIP.**

### âš‘ THE DECISIVE FINDING â€” the topology-bearing option was OFFERED and REJECTED at the FD stage

Scope B's **Q4 option C** was, verbatim:
> *"**A queued/background step** (worker polls `evaluated` â†’ drafts â†’ marks `drafted`). Most production-faithful; **but it
> introduces a worker process and queue infrastructure â€” new deployment topology beyond what `deploy-config` (U23)
> designed, and Infrastructure Design implications.**"*

**The user chose Q4-A, not C.** â‡’ **the one branch that would have made this a real Infrastructure Design pass was
identified, costed and deliberately rejected at the FD stage** â€” and the plan said so **at the time**, before this
assessment existed. The absence of infrastructure here is therefore a **designed property of U24, not an oversight
discovered now.**

### Rule justification (explicit, matching the twenty prior skips)
**CLAUDE.md** Infrastructure Design ***"Skip IF: No infrastructure changes / Infrastructure already defined"*** â€” and here
**BOTH clauses hold**: U24 makes **no infrastructure change** (0 of 7 categories applicable) **and** the infrastructure it
uses is **already defined** by `database` (U15)'s real pass (the tiers, the schema, the CI testcontainers environment, the
runner, the grants). **+ `execution-plan.md:200`**'s *Lighter / minimal-footprint* classing â€” U24 is a **pure-logic +
already-designed-storage consumer**, owning no independent cloud topology.

**Skip roster now TWENTY-ONE**: intake Â· document-sanitizer Â· rules-engine Â· memo-agent-core Â· auth-rbac Â· audit-store Â·
quality-gates Â· corpus-generator Â· secrets-config Â· admin-cli Â· ui-shell Â· ui-queue Â· ui-memo-view Â· ui-approval-gate Â·
ui-override-form Â· ui-history Â· outlier-model Â· ui-outlier-view Â· memo-extensions Â· llm-judge Â· **case-lifecycle** â€”
the **21st skip overall** and the **FIRST Scope-B unit's Infrastructure Design determination**. **The three real non-skips
remain `database` Â· `observability` Â· `deploy-config`.**

**`case-lifecycle` (U24) stage status**: Functional Design âœ“ Â· NFR Requirements âœ“ Â· NFR Design âœ“ Â· **Infrastructure Design
âœ“ SKIPPED (logged, rule-justified)** Â· **Code Generation â³ â€” the LAST stage for U24** (Part-1-plan-then-Part-2-generate,
its own approval gate; **no code until the plan is reviewed**). **4 of 5 stages complete.**

**Register at 14 items** (#13 carrying its ND-Fold-3 aggravating factor). **Carried forward for Code-Gen**: U24's tier-I
tests will add **new CLEAN SKIPS** to the 31; the **5 errors stay exactly unchanged** â€” to be **reported explicitly**.

**Guardrails held**: **NO infra artifact** (`guide-docs/build/case-lifecycle/infrastructure-design/` **NOT created**) Â·
**no code, no wiring** Â· **`backend/case_lifecycle/` ABSENT** Â· **`requirements.txt` and `pyproject.toml` NOT edited** Â·
**WIRE-1's contract text NOT touched** Â· **Q1-B NOT resolved** Â· **`not_wired.py` NOT renamed** Â· **U23's test NOT
edited** Â· **no frozen unit's internals touched** (read-only re-reads only: `database`'s two infra artifacts,
`execution-plan.md`, U24's own seven artifacts) Â· the **`audit_store` Docker-guard gap NOT touched** Â· **tier-B NOT
authorized** Â· nothing under `backend/app/` touched. **NO file written** beyond this state entry and the append-only
`audit.md` entry. **STOPPED** at the Infrastructure Design 2-option gate (1. Request Changes / 2. Continue â†’ Code
Generation).


## U24 `case-lifecycle` â€” **Infrastructure Design SKIP APPROVED (Continue)** â†’ Code Generation Part 1 (Plan) WRITTEN; STOP at the plan-file gate â€” 2026-07-20

**Infrastructure Design SKIP APPROVED (option 2, Continue â†’ Code Generation)** â€” the logged, rule-justified SKIP (**the
21st overall Â· the FIRST Scope-B Infrastructure Design determination**) is **CLOSED**. U24 advanced to **Code Generation â€”
the 5th and LAST of its stages**. Its approval will **complete the first unit added to the original 23-unit
decomposition**.

**Wrote Part 1 (Plan) ONLY**: `guide-docs/build/plans/case-lifecycle-code-gen-plan.md`. **NO CODE. Nothing under
`backend/case_lifecycle/` created (still ABSENT).**

**âš‘ Live baseline re-measured**: `pytest backend --collect-only` â†’ **1344 collected**, reconciling exactly with
**1308 passed / 31 skipped / 5 pre-existing `audit_store` Docker-absence errors**.

**Â§1 â€” component â†’ module map**, C-CASE-1..8 â†’ concrete files, with **header-comment deliverables confirmed explicit on
all production modules** (holds no LLM Â· edits no frozen unit Â· declares no verdict Â· no network at tier-U Â· **never
re-implements the commit gate, the authz check, or a write to `audit_record`**) and the standing rule restated:
**documentation only, never enforcement.**

**Â§2 â€” full TDD test â†’ target map, all SEVENTEEN targets at their NFR-pinned tier.** The **three LOAD-BEARING** at
full-highest: **CANON-1** (behavioural round-trip; **a flipped byte FAILS**; a `float` **raises**) Â· **ADAPTER-1**
(structural AST scan with **`repository.py` explicitly IN SCOPE** and a **positive no-canonicalization assertion**;
detectors for a direct `canon_ser` **and** a `model_dump(mode="json")`) Â· **COMMITBOUND-1** (structural + behavioural,
**including the POSITIVE failed-case-cannot-reach-boundary assertion** and the shared-`atomic()` clause; three separate
detectors). Plus STATE-1/STATE-2 (**exhaustiveness sweep over the state cross-product**), EAGER-1 (**a fault injected
mid-`atomic()` leaves NO partial row** â€” non-vacuous because of the buffering fake), TRIGGER-1 (**pipeline invoked ZERO
times** on the read path), FAILED-1, PROJECT-1 (**+ the DOC-1-style checklist for register #14**), CANONTIME-1, ROUTE-1
(**spy on real args + re-derivation from stored state**), MIGNAME-1, MIGSCOPE-1, **PERSIST-1 (tier-I, using `database`'s
known-good clean-skip guard VERBATIM â€” not `audit_store`'s error-producing pattern)**, PERF-1, SEC-1, and the substrate's
own self-tests.

**Â§3 â€” leaf-first build order** exactly as directed (states â†’ schemas â†’ Protocol+fake â†’ the shim [built, **not exercised at
tier-U**] â†’ pipeline â†’ provider â†’ migrations â†’ StructuralGuard scanning the **completed** tree â†’ coverage gate).

**Â§4 â€” coverage gate with the expected deltas STATED, not left to be discovered**: `--cov=backend/case_lifecycle` with a
**narrow omit of exactly `repository.py`** (the `pg_repository.py` precedent verbatim); everything else counted and
expected at **100%**; `--cov-fail-under=90` **UNCHANGED**. **âš‘ The 5 Docker errors MUST stay exactly 5** (U24 uses the
clean-skip guard precisely so it adds none), and **the 31 skips WILL INCREASE** by U24's tier-I test count when Docker is
absent â€” **expected and correct; that is what a clean skip looks like** â€” with the completion report to state the new
number **and** confirm the error count unchanged.

**FIVE `[Answer]` questions, all BLANK, in full with lettered options (rec A throughout), each genuinely Code-Gen-only**:
- **Q1 module layout** â€” rec **A**: six component-mirroring modules, flat, **plus a small 7th `migrate.py`** holding
  `apply_case_migrations` + the collision guard, **deliberately separated from `repository.py` so the coverage omit cannot
  swallow the guard**, which must stay counted. **B rejected** â€” collapsing `store.py` into `repository.py` would let the
  omit swallow the **pure Protocol** too, silently shrinking what the gate measures.
- **Q2 migration filename** â€” rec **A**: `0001_case_lifecycle.sql`, **one file** (numerically independent of U15's since
  the tracking PK is the **bare filename**; **no grants migration needed** because the store uses the owner engine and
  grants to no U15 role).
- **Q3 how the production collision guard learns U15's filenames** â€” rec **A**: **read them live** via the frozen
  `migration_files(DB_MIGRATIONS_DIR)`, so the guard is **always current** (if U15 ever adds `0003_*.sql` it is seen
  immediately, with **no U24 edit**) and **cannot drift because there is no copy**. **B rejected â€” a hardcoded list goes
  stale silently, and a stale collision guard is WORSE than none because it reads as protection.** **C rejected** â€”
  prefix-only comparison would flag safe pairs and miss unsafe ones, since the PK is the whole filename.
- **Q4 test-file organization â€” grounded in MEASURED sibling precedent**: `llm-judge` put **ONE target's two mechanisms in
  ONE file** (`test_exempt.py`) but **TWO targets in TWO files** (`test_noedit.py` / `test_nometric.py`). Rec **A**: apply
  that rule **as measured** â€” **CANON-1 and ADAPTER-1 are two TARGETS â†’ two files** with **cross-referencing docstrings**
  stating the pairing and why neither alone suffices; **COMMITBOUND-1 is one target with two halves â†’ one file**.
- **Q5 omit comment wording** â€” rec **A**: mirror the five existing entries' shape, **plus one U24 addition â€” an explicit
  NOTE that `repository.py` is OMITTED FROM COVERAGE but REMAINS IN ADAPTER-1's SCAN SET (CASE-Req-Fold-3)** â€” so a future
  reader cannot mistake coverage-omission for scan-exclusion.

**`case-lifecycle` (U24) stage status**: Functional Design âœ“ Â· NFR Requirements âœ“ Â· NFR Design âœ“ Â· **Infrastructure Design
âœ“ SKIPPED (logged)** Â· **Code Generation â³ Part 1 (Plan) WRITTEN â†’ STOPPED at the plan-file gate**. **4 of 5 stages
complete; the 5th engaged.**

**Register at 14 items** (#13 amplified). **Guardrails held**: **NO CODE** Â· **`backend/case_lifecycle/` ABSENT** Â·
**`requirements.txt` NOT edited** Â· **`pyproject.toml` NOT edited** (the `--cov` line + omit land at Part 2) Â· **no new
dependency** (`testcontainers` already floored + installed) Â· the frozen FD / NFR Requirements / NFR Design / Infra SKIP
**re-opened NONE** Â· **WIRE-1's contract text NOT touched** Â· **Q1-B NOT resolved** Â· **`not_wired.py` NOT renamed** Â·
**U23's test NOT edited** Â· **no frozen unit's internals touched** (read-only re-reads only: the sibling test-file
convention, `pyproject.toml`'s omit list, a collect-only run that **executed no test**) Â· the **`audit_store` Docker-guard
gap NOT touched** Â· **tier-B NOT authorized** Â· **nothing under `backend/app/` touched** (the wiring pass comes only after
this stage closes). **Only 1 file written**: the plan.


## U24 `case-lifecycle` â€” **Code-Gen Q1â€“Q5 ANSWERED (all A)** + ambiguity-check **CLEAN (3 folds)** + **Part 2 GENERATED + TESTED**; STOP at the Code Generation 2-option gate â€” 2026-07-20

**Q1â€“Q5 all A** (embedded in the plan Â§6). **Ambiguity-check ran as plan Â§6.5 â†’ CLEAN â€” 3 folds resolved, no gap.**

- **âœ… CG-CASE-Fold-1 [check (i)] â€” no import cycle, no import-order issue.** Measured:
  `database/migration_runner.py` imports **only** `os`/`re`/`pathlib`/`typing`/`sqlalchemy` â€” **no `backend.*` app import
  at all** â€” and `database` **predates U24 by the entire build**, so the dependency is **strictly one-way**.
  `MIGRATIONS_DIR` is computed from `__file__` with **no environment read and no side effect**.
- **âœ… CG-CASE-Fold-2 [check (ii)] â€” the seven modules match every component responsibility**, nothing missing or extra;
  `EXPECTED_PRODUCTION_MODULES` has **exactly seven** entries (asserted in `test_structural_guard.py`).
- **âš‘ CG-CASE-Fold-3 [check (iii)] â€” a REAL bypass risk, caught and pinned.** Had PERSIST-1's fixture called
  `MigrationRunner` **directly**, the **production collision guard would have been bypassed entirely** â€” never executing
  on the path PERSIST-1 verifies. **PINNED: the fixture calls `apply_case_migrations()`**, and **TWO tests enforce it** â€”
  `test_migscope.py` asserts **no U24 test constructs `MigrationRunner` directly**, and a new tier-U test proves the
  **ordering** (`order == ["guard", "runner", "apply"]`) **without needing Docker**.

**PART 2 GENERATED â€” TDD, tests-first, leaf-first exactly per plan Â§3.**
**Modules**: `backend/case_lifecycle/{__init__,states,schemas,store,repository,pipeline,provider,migrate}.py` +
`migrations/0001_case_lifecycle.sql` + `checksums.json` + `tests/{__init__,fixtures,structural}.py` + **16 test files**.
**`pyproject.toml`**: the `--cov` line **plus one narrow omit** (`*/case_lifecycle/repository.py`) with the
**omit-vs-scan NOTE**. **`requirements.txt` NOT edited; no new dependency.**

**âš‘ VERIFIED NUMBERS (measured, not assumed)**: backend **1418 passed / 36 skipped / 5 pre-existing `audit_store`
Docker-absence errors**. Baseline **1308 / 31 / 5** â‡’ **+110 tier-U tests, ZERO regression**.
**âš‘ BOTH DELTAS PREDICTED IN THE PLAN BEFORE THE RUN**: **skips 31 â†’ 36 (EXACTLY +5**, the tier-I tests skipping
**cleanly**) and **errors 5 â†’ 5 (EXACTLY UNCHANGED** â€” U24 uses `database`'s guard, with the daemon ping **inside** the
fixture body, precisely so it adds none). **Every COUNTED module at 100%**; `repository.py` omitted (tier-I only).
**Global 99.86%, `--cov-fail-under=90` HELD.**

**âš‘ FOUR TEST FAILURES ON THE FIRST RUN â€” reported, not quietly patched â€” and ALL OF ONE CLASS: text-based scans matching
the docstrings that DOCUMENT the prohibition.** A header saying *"never writes to `audit_record`"* was read as a write; a
SQL comment saying *"NO GRANTS HERE"* as a `GRANT`; and `Optional[PendingRecommendation]` as the frozen `Recommendation`
type. **Fixed by STRENGTHENING the scans, never weakening the assertions**: `executable_text(tree)` (identifiers +
**non-docstring** literals only â€” *"otherwise the only way to pass would be to delete the disclosure"*),
`annotation_names(tree)` (exact identifiers, so `PendingRecommendation` no longer trips a `Recommendation` check), and
`sql_without_comments(sql)`. **All four now test the CODE rather than the PROSE ABOUT the code.**

**âš‘ TWO COVERAGE GAPS CLOSED WITH REAL TESTS, NOT A WIDER OMIT**: `migrate.py` (90%) and `pipeline.py` (97%) were short.
Rather than widen the carve-out, two genuine tests were added â€” the **guard-ordering test** (which also discharges
Fold-3) and a `draft("no-such-case")` test proving an unknown application yields an ordinary **failure `DraftOutcome`**
rather than an exception (Q4-A). **Both modules now 100%.**

**The three LOAD-BEARING targets, as realized**: **CANON-1** (round-trip byte-identity Â· `Decimal`/`date` return as
themselves Â· hash stable Â· **a flipped byte FAILS** Â· a `float` **raises** Â· key-order independence) Â· **ADAPTER-1**
(no direct `canon_ser`, no re-implemented reduction, **`repository.py` IN the scan set** with a **positive
no-canonicalization assertion**, detectors for a direct call **and** `mode="json"`) Â· **COMMITBOUND-1** (no
gate/authz/`audit_record` with **three** detectors Â· the provider returns a `CommitContext` and raises on an unknown id Â·
**the POSITIVE failed-case assertion** Â· the shared `atomic()` block proven by `atomic_entries == 2`).

**`case-lifecycle` (U24) stage status**: Functional Design âœ“ Â· NFR Requirements âœ“ Â· NFR Design âœ“ Â· **Infrastructure Design
âœ“ SKIPPED (logged, the 21st)** Â· **Code Generation âœ“ Part 2 GENERATED + TESTED â†’ STOPPED at the 2-option completion
gate**. **5 of 5 stages complete pending the gate.** Its approval **completes the FIRST unit added to the original
23-unit decomposition**, leaving **only the in-place composition-root wiring pass** before Scope B's demo path is
runnable end-to-end.

**Register at 14 items â€” NONE discharged**: **#13 `NOTWIRED-FILENAME-STALE`** (amplified; U24 authored nothing under
`backend/app/`) Â· **#14 `MEMOVIEW-FAILED-STATE-UNMODELLED`** (disclosed in `states.py`'s docstring with name + owner +
rationale, verified by PROJECT-1's token checklist) Â· **#8 `DEPLOY-MIGRATE-DEFERRED`** (unchanged â€” U24 authors **no CLI
entrypoint**, asserted by MIGSCOPE-1, and **makes it no worse**).

**Guardrails held**: **no frozen unit edited** â€” `database`'s migration machinery, `canon_ser.py`, `canon_adapter.py`,
`borderline_router.py`, `DecisionCommitService`, `CommitContext` and the `CommitContextProvider` Protocol all consumed
**read-only / through existing seams** Â· **WIRE-1's contract text NOT touched** Â· **Q1-B NOT resolved** Â·
**`not_wired.py` NOT renamed** Â· **U23's test NOT edited** Â· the **`audit_store` Docker-guard gap NOT touched** (5 errors
exactly unchanged) Â· **tier-B NOT authorized** Â· **NOTHING under `backend/app/` touched** Â· **no new dependency**.
Files written: the 8 production files + migrations + 18 test files, `pyproject.toml` (one `--cov` line + one omit),
`code-summary.md`, `testresults.txt`, the plan (Â§6.5 + answers), and these log entries.


## âš‘ SCOPE B â†’ `case-lifecycle` (U24) â€” **Code Generation APPROVED (Continue)** â†’ **U24 COMPLETE (5/5)** â†’ **THE DECOMPOSITION NOW STANDS AT 24 UNITS, 24 OF 24 COMPLETE** â€” 2026-07-20

**Code Generation APPROVED 2026-07-20 (option 2, Continue)** â€” gate **CLOSED**. `case-lifecycle` (U24, Scope B) is
**COMPLETE â€” all 5 of its 5 stages**: FD âœ“ Â· NFR Requirements âœ“ Â· NFR Design âœ“ Â· **Infrastructure Design âœ“ SKIPPED-logged
(the 21st skip Â· the FIRST Scope-B determination)** Â· **Code Generation âœ“**.

**âš‘ U24 is the FIRST unit added beyond the original 23-unit decomposition.** The decomposition now stands at
**24 units, 24 of 24 complete**.

**Final verified numbers**: backend **1418 passed / 36 skipped / 5 pre-existing `audit_store` Docker-absence errors**;
baseline **1308 / 31 / 5** â‡’ **+110 new tier-U tests, ZERO regression**. **Both deltas were PREDICTED IN THE PLAN BEFORE
THE RUN**: **skips 31 â†’ 36, EXACTLY +5** (U24's five tier-I tests skipping **cleanly**) and **errors 5 â†’ 5, EXACTLY
UNCHANGED** (U24 uses `database`'s known-good guard â€” the daemon ping **inside** the fixture body â€” precisely so it adds
none). **`backend/case_lifecycle` at 100% on every module** except the deliberately tier-I-only `repository.py`; global
gate **HELD at 99.86%**. The **three LOAD-BEARING targets** ran at full-highest rigor with detector self-tests.

### âš‘ Quality signals recorded, not glossed
1. **A REAL DEFECT CLASS found and fixed during TDD â€” scans flagging their OWN DOCSTRINGS.** Four first-run failures were
   all one class: text-based scans matching **the prose that DOCUMENTS each prohibition**. A header saying *"never writes
   to `audit_record`"* was read as a write; a SQL comment saying *"NO GRANTS HERE"* as a `GRANT`; and
   `Optional[PendingRecommendation]` as the frozen `Recommendation` type. **Fixed by making the scans STRUCTURE-AWARE** â€”
   `executable_text(tree)` (identifiers + **non-docstring** literals), `annotation_names(tree)` (exact identifiers),
   `sql_without_comments(sql)` â€” **never by weakening an assertion**. Mirrors `llm-judge`'s substring-collision lesson
   (`"city"` inside `"ethnicity"`): **the honest fix strengthens the detector; the dishonest one would have been deleting
   the disclosures so the scans pass.**
2. **âš‘ CG-CASE-Fold-3 caught a genuine BYPASS â€” a quality signal from the ambiguity-check process itself.** Had PERSIST-1's
   tier-I fixture called `MigrationRunner` **directly**, the **production collision guard would never have executed on the
   path PERSIST-1 verifies** â€” the one test exercising real migration application would have proven **nothing** about the
   guard. Now enforced by **two** tests: `test_migscope.py` asserts **no U24 test constructs `MigrationRunner` directly**,
   and a tier-U test proves the **ordering** (`["guard", "runner", "apply"]`) **without needing Docker**.
3. **Two coverage gaps closed with REAL TESTS, not a wider omit** â€” the guard-ordering test (which also discharges Fold-3)
   and a `draft("no-such-case")` test proving an unknown application yields an ordinary **failure `DraftOutcome`** rather
   than an exception (Q4-A). Both modules reached **100%**.

### Register â€” **14 items, NONE newly discharged**
**#13 `NOTWIRED-FILENAME-STALE` â€” AMPLIFIED**: once R2â€“R5 are wired in place, the stale-named file will sit on the
**primary user journey**, not merely on four `501` markers. Disposition unchanged (the rename remains a **matched pair**
with U23's test relaxation, owned by a future authorized change).
**#14 `MEMOVIEW-FAILED-STATE-UNMODELLED` â€” DISCLOSED WITH REAL TIER-U TEETH**: `states.py`'s docstring carries the
**name + owner (a future authorized WIRE-1 amendment) + rationale**, verified by **PROJECT-1's DOC-1-style token
checklist** with a removal detector. **U24 claims no discharge.**
All other items unchanged. **#8 `DEPLOY-MIGRATE-DEFERRED`** explicitly **not adopted and not made worse** (U24 authors
**no CLI entrypoint**, asserted by MIGSCOPE-1).

### âš‘ What exists now, and what does NOT
**EXISTS**: the pending-application / pending-recommendation lifecycle â€” **fully built and tested in isolation** (five
states + the internal `failed`, the `CaseStore` Protocol with `atomic()`, `CasePipeline` with the explicit
`route_borderline` call, the real `PendingCommitContextProvider`, U24's own migration sequence with its production
collision guard, and the pure `case_to_memo_view_state` projection).
**DOES NOT EXIST**: any wiring. **R2â€“R5 remain `501` stubs**; **the composition root is still unwired to U24**;
**nothing under `backend/app/` was touched** (mtimes unchanged at 12:19â€“12:22, the original Scope A pass).
â‡’ **The demo path is NOT yet runnable end-to-end.**

**âš‘ EXACTLY ONE authorized piece of Scope B work remains: the IN-PLACE COMPOSITION-ROOT WIRING PASS** â€” implementing
R2â€“R5 **inside the existing route files** (Q9-A, so U23's frozen exact-set assertion stays green with zero frozen edits),
injecting U24's `CasePipeline` / `PendingCommitContextProvider` / `case_to_memo_view_state`, and **revising the five
composition-root tests already enumerated at NFR Design's Fold-4 check** (`test_its_first_statement_raises_the_marker` Â·
`test_the_marker_module_constructs_no_service_and_reads_no_body` Â· `test_no_writer_engine_is_ever_constructed` Â·
`test_no_commit_service_or_context_provider_exists` Â· `test_no_repository_write_method_is_called`) â€” **preserving the
substantive guarantee that every write goes through the frozen `DecisionCommitService`**. Per the original Scope B
scoping plan this is the **next and final step** before the local-run checklist for the live demo can be meaningfully
attempted. **NOT STARTED.**

**Guardrails held**: **no unit begun beyond U24** Â· **WIRE-1's contract text NOT touched** Â· **Q1-B NOT resolved** Â·
**`not_wired.py` NOT renamed** Â· **U23's test NOT edited** Â· **no frozen unit's internals touched** Â· the **`audit_store`
Docker-guard gap NOT touched** (5 errors exactly unchanged) Â· **tier-B NOT authorized** Â· **nothing under `backend/app/`
touched**. Files updated for this approval: the `guide-state.md` **top status** (spliced to the 24-unit / U24-complete
status, the prior status preserved behind a `<!-- superseded -->` marker) + this completion entry + the append-only
`audit.md` entry. **STOPPED â€” NOTHING STARTED.**


---

## ⚑ COMPOSITION ROOT REOPENED — Scope B in-place wiring pass (2nd and FINAL reopening)

**Timestamp**: 2026-07-20T08:14:48Z · **Stage**: Scope B → in-place composition-root wiring pass → **SCOPING/PLANNING ONLY**

`backend/app/` — held **closed** since the original Scope A integration pass (2026-07-16) — is **REOPENED for the SECOND
and FINAL time** under Scope B authorization, **specifically and only** for the in-place R2–R5 wiring pass. (The first
Scope B reopening was U24's own authorization; in the event U24 touched **nothing** under `backend/app/` — mtimes remain
at the Scope A pass, 12:19–12:22.)

**State of this pass: SCOPING ONLY. No wiring code written. No route file edited. Plan file written, gate not passed.**
Plan: `guide-docs/build/plans/scope-b-wiring-plan.md` — **11 open `[Answer]:` tags, none pre-filled.**

### ⛔ Three BLOCKERS found in the ground-truth pass — the wiring cannot proceed as briefed
Surfaced as the user's decisions (Q1/Q2/Q3 in the plan), **not improvised**:
1. **`CaseStore` has no list/browse method** — R2 is a paginated LIST route and **cannot be wired** against U24's public
   surface as built (`put_application` · `get_application` · `put_recommendation` · `get_recommendation` ·
   `recommendation_for_application` — no enumeration).
2. **No production `CaseSeams` and no production `recommendation_id_factory` exist** — both live only in
   `case_lifecycle/tests/fixtures.py` as test doubles, so `CasePipeline` **cannot be constructed in production**.
3. **Nothing populates the pending store** — WIRE-1 pins R1–R7 with **no ingestion route**, and the frozen route set is
   exact, so `submit()` has no HTTP caller and none may be added. R2/R3/R4 would read a **permanently empty** table.

⇒ **The "demo path runnable end-to-end" claim is NOT achievable by this wiring pass alone.** Recorded here so it is not
discovered later at the local-run checklist.

### Verified safe (read, not assumed)
**U23's `NFR-DEP-ROUTES-1` stays green with ZERO edits**: `_EXPECTED` is keyed by **(path, method)** and **already
contains all four R2–R5 entries** with their current verbs; the companion assertion is over **filenames** only. In-place
wiring changes neither.

### Guardrails held this pass
**No code generated** · `not_wired.py` **NOT renamed** (register #13 stands) · **no file added** under
`backend/app/routes/` · **no frozen unit's internals touched** · **WIRE-1's contract text NOT amended** · **Q1-B
(register #1) NOT resolved** · the frozen `DecisionCommitService` **composed with, never bypassed** · **tier-B NOT
authorized** · the **`audit_store` Docker-guard gap untouched** (5 pre-existing errors stay exactly 5).

**STOPPED at the plan-file gate. The next decision is the user's.**

---

## ⚑ U24 REOPENING AUTHORIZED (Q1-A) + AMBIGUITY-CHECK **NOT CLEAN** — STOPPED

**Timestamp**: 2026-07-20T08:41:12Z · **Stage**: Scope B → in-place composition-root wiring pass → **ambiguity-check gate**

### U24 reopening — AUTHORIZED, SEPARATELY LOGGED, **NOT YET ACTED UPON**
A **small, explicitly scoped reopening of Scope B's OWN unit** (U24 — not one of the original frozen 23), authorized by
Q1-A and recorded **distinctly** from Scope B's original scoping authorization and from U24's original build
authorization, on the same *"deliberate, logged deviation with rationale"* discipline every prior reopening used.

**Authorized scope**: add an enumeration primitive (`list_application_ids()` or equivalent) to the `CaseStore` Protocol,
`PostgresCaseStore`, and the in-memory fake — nothing else.
**Rationale**: the only option that makes R2 genuinely functional, rather than putting SQL in the composition root (Q1-B),
shipping a route that can structurally never return data (Q1-C), or leaving the primary queue journey dead (Q1-D).
⚑ **NO U24 FILE HAS BEEN TOUCHED.** The authorization is recorded; the work is not started.

### Answers Q1–Q11 recorded
All eleven answered and embedded verbatim into `guide-docs/build/plans/scope-b-wiring-plan.md` as **Part 2** (§7–§11),
together with the **six anticipated register items** (confirmed as expected, **not yet created**).

### ⛔ MANDATORY AMBIGUITY-CHECK — **NOT CLEAN. SURFACE-AND-STOP.**
**1 check clean · 1 GENUINE BLOCKER · 1 GENUINE FOLD.** Part 2 code generation **NOT started**.

- **(i) ✅ CLEAN** — Q1-A's list method does **not** disturb ADAPTER-1 or COMMITBOUND-1. An enumeration method performs
  **no canonicalization** (exactly like the existing `get_application`, which already builds a `PendingApplication` from
  row bytes and passes), the scan scope is directory-based and unchanged, and COMMITBOUND-1's forbidden tokens are
  untouched. **⚑ CORRECTION**: `EXPECTED_PRODUCTION_MODULES` needs **no update** — it names the seven production
  *modules*, and Q1-A adds *methods to two existing modules*. The in-memory fake does need the method; **PERSIST-1**
  keeps the two implementations honest.
- **(ii) ⛔ GENUINE BLOCKER — B4: no production `LLMClient` exists.** `CaseSeams.draft_memo` → `LangGraphOrchestrator` →
  `GeminiAdapter` → **`LLMClient` — implemented nowhere in production.** `memo_agent_core/provider.py` states the real
  client *"is wrapped to this at composition"* — **composition never built it**: the **identical failure mode to the
  `CaseSeams` blocker**. The one real adapter (`corpus_generator/build.py::_GeminiLLMClient`) is **tier-B**, which is
  **NOT authorized**. **⚑ Compounding**: `requirements.txt` declares **`google-generativeai`** (legacy SDK) while the
  code imports **`from google import genai`** (the new `google-genai` SDK) — **different distributions**, and
  `google-genai` is **declared nowhere**. ⇒ **`draft()` cannot run**, so no `PendingRecommendation` is ever created,
  **R4 never reaches `ready`**, and **R5 is unreachable**. → **Question 12**.
- **(iii) ⛔ GENUINE FOLD — 400 vs 422 on R5.** The contract half is clean (a `Literal["approve","override"]` rejects
  exactly what WIRE-1 §5 pins, so it is **additive, not an amendment**). **But** a Pydantic `Literal` mismatch raises
  `RequestValidationError`, which the **app-global** handler maps to **400**, while §4 mandates **422**. The handler
  cannot change for R5 alone without regressing `test_error_envelope.py`. **Q6-c's goal is unreachable by its stated
  mechanism.** → **Question 13**.

### ✅ Q8c's gating check — resolved EARLY and CLEAN (no fourth blocker there)
`audit_store/seams.py` ships **real production implementations** — **`UuidGenerator`** (*"Production `decision_id`
generator"*) and **`SystemClock`**. `DecisionCommitService` is fully constructible. **⚑ Q3a resolves to (ii) from disk,
not by choice**: `IdGenerator.new_id()` takes **no argument** while `recommendation_id_factory` is `Callable[[str], str]`
— **the shapes do not fit**, so the `uuid4`-in-seed-script fallback applies.

### What was NOT done (deliberately)
**No code generated** · no U24 file touched · nothing under `backend/app/` touched · **no seed script** · **no test
revised** · **no `scope-b-wiring-summary.md`** · **`BUILD-COMPLETION-REPORT.md` NOT folded** (the register items it would
record are contingent on Q12/Q13) · **`testresults.txt` NOT updated** (no suite run — nothing to run).

### Guardrails held
WIRE-1's contract text **unamended** · **Q1-B unresolved** · `not_wired.py` **not renamed** · **U23's test not edited** ·
`audit_store` Docker-guard gap **untouched** (5 pre-existing errors still exactly 5) · **tier-B not authorized** ·
**nothing added under `backend/app/routes/`** · **frontend untouched**.

**Next**: answer **Q12** (how a memo gets drafted with no production LLM client — recommendation **C**, a disclosed
deterministic offline double) and **Q13** (the 400-vs-422 fold — recommendation **A**, an explicit membership check
yielding 422). Then the code pass proceeds in the agreed sequence: U24 reopening → wiring → seed script → full-suite run.

**STOPPED at the ambiguity-check gate. The next decision is the user's.**

---

## ⚑ U24 REOPENINGS — TWO post-build reopenings, each separately authorized and logged

⚑ **NAMING RECONCILIATION (do not let this drift).** These are the **TWO** reopenings that
occurred **after** U24's original build authorization. The user's instructions refer to the
Q14-A change as *"U24's THIRD reopening"*, counting U24's **original build authorization** as
the first. Both countings describe the same three authorizations — they differ only in whether
the original build is counted as a "reopening". Recorded here so a future reader is never left
guessing which convention a given document used.

**Scope B wiring pass** · Timestamps: reopening #1 2026-07-20T08:41:12Z · reopening #2 2026-07-20T11:03:25Z
*(U24's original build authorization is distinct from both and is NOT counted here.)*

| # | Authorized by | Scope | Why it could not be avoided |
|---|---|---|---|
| **1** | **Q1-A** | `list_application_ids()` on the `CaseStore` Protocol, `PostgresCaseStore`, and the in-memory fake | R2 is a **paginated list** and the Protocol had **no enumeration primitive at all** — R2 was not implementable |
| **2** | **Q14-A** | a U24-owned `memo_from_canonical(bytes) -> DecisionMemo` thin adapter | WIRE-1 §5 binds `status: "ready"` to a **present** `memo`, and **no memo rehydration exists anywhere in the build** |

**Reopening #2's three rejected alternatives**: editing `audit_store`'s frozen `CanonSerAdapter` (a frozen-unit edit,
forbidden) · an ad hoc `canon_deserialize` in `backend/app/` (U24-shaped domain knowledge in the composition root,
breaking the no-domain-logic invariant **and uncaught by any scan**) · `memo: null` when `ready` (a direct WIRE-1 §5
violation).

**Targeted pre-check before reopening #2**: a full `backend/`-wide grep for `DecisionMemo` with
canonical/deserialize/rehydrate/validate terms returned **zero hits**. Only **two** `*_from_canonical` functions exist
build-wide, both on `audit_store`'s frozen adapter. **Nothing existed to reuse.**

### ⚑ ADAPTER-1 is NARROWED, NOT WEAKENED (flagged in advance, not discovered in a diff)
`canon_ser` remains forbidden in **every** U24 production module, without exception. `canon_deserialize` becomes
permitted in **exactly one named allowlisted module** (the new adapter) and stays forbidden everywhere else, with a
**positive assertion that the allowlisted module is a thin adapter and nothing more**, plus a **detector self-test**.
*Before*: no module may call it. *After*: exactly one designated module may, for rehydration only. **Strictly more
specific, not more permissive.**

### ⚑ Deliberately opposite calls on `EXPECTED_PRODUCTION_MODULES`
Reopening **#1** added **methods to existing modules** — the set correctly stayed **unchanged** (7).
Reopening **#2** adds a **new production module** — the set **does** change (7 -> 8). Opposite calls, opposite reasons.

---

## ✅ SCOPE B WIRING PASS — **COMPLETE**. Scope B is CLOSED. — 2026-07-20 (implemented) · 2026-07-21 (verified + disclosed)

**This was Scope B's final authorized step.** R2–R5 are wired **in place** to `case-lifecycle` (U24). **All seven
WIRE-1 routes are live.**

> ⚑ **DOCUMENTATION-TIMING DISCLOSURE.** The implementation completed 2026-07-20 but its **documentation did not** —
> the session was interrupted twice (a 529 API error, then a laptop restart) before reaching its logging step. The
> plan file was left saying *"Part 2 code generation NOT started"* while the tree in fact held a complete, green
> implementation, and ~12 hours of work went unlogged. **Both gaps were reconciled 2026-07-21** and the reconciliation
> is **marked as retroactive, not backdated** — see `audit.md`'s final entry. **The gap in the record is part of the
> record.**

### Verified live, 2026-07-21 — no figure carried forward from a prior session

| Scope | Passed | Failed | Skipped | Errors |
|---|---|---|---|---|
| `backend/case_lifecycle/` | 129 | **0** | 6 | **0** |
| `backend/app/` | 165 | **0** | 0 | **0** |
| **Full `backend/`** | **1492** | **0** | **37** | **5** |

**Coverage 99.87%, `--cov-fail-under=90` HELD.** Pre-wiring baseline **1418 / 36 / 5** → **+74 passed, +1 skipped,
errors EXACTLY unchanged. ZERO REGRESSION.** The 5 errors are the **same five `audit_store` Docker-absence errors by
name** (register #4) — that gap was a standing hold and was **not touched**; this pass added none.

### Five blockers surfaced — each stopped on, none improvised past

| # | Blocker | Resolution |
|---|---|---|
| **B1** | `CaseStore` had **no enumeration primitive at all** — R2 unimplementable | **Q1-A**: U24 reopening #1 |
| **B2** | **No production `CaseSeams` / `recommendation_id_factory`** — pipeline not constructible outside tests | **Q3-D**: pipeline **never constructed** in the composition root; lives in the seed script |
| **B3** | **Nothing populated the pending store**; no ingestion route exists or may be added | **Q2-A**: out-of-band seed script, **adds no route** |
| **B4** | **No production `LLMClient` anywhere in the build** — `draft()` could not run | **Q12-C**: disclosed deterministic offline double → **register #18** |
| **B5** | **No sanctioned way to rehydrate the memo** — surfaced *while wiring R4* | **Q14-A**: U24 reopening #2 |

Plus two decided gaps: **G1** (the flat `CommitRejected` 409/422 ambiguity → **Q13-A**, an explicit closed-enum
membership check yielding 422; Q6-c's Pydantic `Literal` was **abandoned** because the app-global handler makes it
**400**, not the **422** WIRE-1 §4 mandates) and **G2** (→ register **#19**).

### The two authorized U24 reopenings — both logged BEFORE their code was written

| # | By | Scope | Why unavoidable | `EXPECTED_PRODUCTION_MODULES` |
|---|---|---|---|---|
| **1** | **Q1-A** | `list_application_ids()` on the Protocol, `PostgresCaseStore`, and the in-memory fake | R2 is a **paginated list** and **no enumeration primitive existed** | **UNCHANGED (7)** — methods added to existing modules |
| **2** | **Q14-A** | a U24-owned `memo_from_canonical(bytes) -> DecisionMemo` thin adapter | WIRE-1 §5 binds `ready` to a **present** `memo`, and **no memo rehydration existed anywhere in the build** | **CHANGED (7 → 8)** — a new production module |

⚑ **The opposite calls on that set are deliberate, for opposite reasons**, and were stated in advance rather than
discovered in a diff.

⚑ **ADAPTER-1 was NARROWED, NOT WEAKENED.** `canon_ser` (serialize) stays forbidden in **every** U24 production module
without exception; `canon_deserialize` becomes permitted in **exactly one named allowlisted module**, with a positive
thinness assertion and a detector self-test. *Before*: none may call it. *After*: exactly one may, for rehydration
only. **Strictly more specific, not more permissive.**

### The honest scope claim (Q11-A) — stated precisely, NOT drifted

> **"The API layer is exercisable after running the seed script."**

**NOT** *"the demo path is runnable end-to-end"* (needs an ingestion route → a WIRE-1 amendment **and** a frozen-test
edit; **neither permitted**) · **NOT** a clickable UI (frontend untouched, Q10-A) · ⚠️ **seeded memo prose is
SYNTHETIC** — a deterministic offline double stamped `model_version="OFFLINE-DOUBLE-NOT-A-REAL-LLM"`, **not a real
model call**, because **no production `LLMClient` exists** (#18).

### Register: 14 → 20 · six opened, one discharged

**Opened by this pass**: **#15** R2 amplified N+1 · **#16** failed-indistinguishable-from-fresh · **#17**
outlier-data-exists-contract-forbids · **#18** no production `LLMClient` · **#19**
`COMMITTED`-transition-never-performed (**double-commit / duplicate `AuditRecord` risk — the most serious item**) ·
**#20** pending-tables-no-explicit-grants.

**Discharged**: **#2 `R2–R5 unwired`** — the register's **only discharge**, and only **partly** so: the routes are live,
but the end-to-end claim remains scoped per Q11-A.

**Realized/widened**: **#13** (four wired routes under a stale filename) · **#14** (failed cases now render as
`pending` to a **real client**).

`BUILD-COMPLETION-REPORT.md` had lagged at **12**; it was folded to the true **20** in this pass, with #13–#20
documented at the same rigor as #1–#12.

### Holds — all upheld, verified on disk

WIRE-1's text **unamended** · **Q1-B unresolved** *and deliberately **not propagated*** (R2/R3/R4 use
`current_identity`, **not** `require_read_audit`, containing the known divergence rather than spreading it) ·
`not_wired.py` **NOT renamed** · **U23's frozen test NOT edited** (**zero edits needed** — its `_EXPECTED` already held
all seven (path, method) pairs, and wiring in place changed no filename) · `audit_store` Docker-guard gap **untouched**
(5 errors, exactly 5) · **tier-B NOT authorized** · **nothing added under `backend/app/routes/`** · frontend
**untouched** · **no domain logic in `backend/app/`** — `CasePipeline` is never constructed there, making R4
side-effect-free **by construction, not by discipline**.

### Artifacts

`guide-docs/build/composition-root/scope-b-wiring-summary.md` (full disclosure) ·
`guide-docs/build/plans/scope-b-wiring-plan.md` (Q1–Q14 + Part 3 §12, reconciled) ·
`guide-docs/BUILD-COMPLETION-REPORT.md` (register folded to 20) · `testresults.txt` (live figures + baseline).

### Named follow-ons — NOT absorbed here

**#18** a production `LLMClient` (+ resolving the `google-generativeai` vs `google-genai` SDK mismatch) · **#19** the
`drafted → committed` transition, **needing its own commit-boundary (COMMITBOUND-1) review** · **#8**
`DEPLOY-MIGRATE-DEFERRED` — a real CLI entrypoint for **both** U15's and U24's migration sequences (this pass invoked
migrations **from the seed script only**, Q9-B; #8 stays open and unchanged) · **#13**'s rename + U23 test relaxation
**as a matched pair** · binding the four frontend fetch seams · **#20**'s grant review.

**STATUS: SCOPE B CLOSED. Decomposition: 24 units, 24 of 24 complete.**

### ✅ GATE APPROVED AND CLOSED — 2026-07-21T00:58:00Z

User approved option 2 (*"Continue to Next Stage — approve and close the gate. Scope B is CLOSED."*) after reviewing
the diffs: the reconciled plan file, the reconstructed audit entries, the wiring summary, and the register fold.

**Verified state at closure**: backend **1492 / 0 / 37 / 5**, coverage **99.87%** (gate held), **zero regression**
against the 1418/36/5 baseline, the 5 `audit_store` Docker errors **exactly 5 and the same five by name**. Both
`backend/case_lifecycle` and `backend/app` genuinely green. **No code file modified during the reconciliation.**

**Register at closure: 20** — six opened (#15–#20), **one discharged (#2, partly)**, #13 realized, #14 widened.

**⚑ NOTHING FURTHER STARTED.** Scope B was the last authorized work. The named follow-ons below are **recorded, not
begun**; each needs its own authorization:

| Follow-on | Why it needs its own decision |
|---|---|
| **#18** a production `LLMClient` | New dependency + the `google-generativeai` vs `google-genai` SDK mismatch + a live key and real spend. **Until then no genuine LLM memo can be produced.** |
| **#19** the `drafted → committed` transition | **Straddles the commit boundary (COMMITBOUND-1)**; must not be folded into another pass as a convenience. **Double-commit is a real BFSI defect.** |
| **#8** a migration CLI entrypoint | Discharges a register item scoped to `database`/composition, for **both** U15's and U24's sequences. |
| **#13** rename `not_wired.py` | Only valid as a **matched pair** with relaxing U23's frozen exact-set assertion. |
| Frontend fetch seams | Deferred by Scope B's Q7-A; the frontend is still not browser-runnable. |
| **#20** pending-table grants | A **security review** call — deliberately left undecided. |
| **#3 / #9 / #10** tier-B, promptfoo, judge eval | Still unauthorized; the ≥4/5 groundedness gate remains unverified. |

**The next decision is the user's. No recommendation is made and nothing is in progress.**

---

## ⚑ REGISTER ITEM #19 — `COMMITTED-TRANSITION-NEVER-PERFORMED` — SCOPING PASS STARTED (2026-07-21T11:17:26Z)

**Stage**: POST-BUILD → **register-item remediation**, the first work started after **SCOPE B CLOSED**.
**Status**: 🟡 **SCOPING / PLANNING ONLY — NO CODE GENERATED.** Stopped at the plan-file gate.
**Plan of record**: `guide-docs/build/plans/fix-register-19-plan.md` (Q1–Q5, **all blank, none pre-filled**).
**Origin**: register item **#19 `COMMITTED-TRANSITION-NEVER-PERFORMED` (G2)**, opened by the **Scope B in-place
composition-root wiring pass** and deliberately **not fixed there** under **Q6d-ii** — the fix straddles the commit
boundary (**COMMITBOUND-1**), sits outside the frozen service's transaction, and *"must not be folded into a wiring
pass as a convenience."* The register names its owner as **U24 + `audit-store`, needing its own commit-boundary
review**. This pass is that review, begun.

### Ground truth re-established from disk — four checkpoints, **ALL CONFIRMED**

| # | Checkpoint | Finding |
|---|---|---|
| **1** | `case_lifecycle/states.py` | ✅ **CONFIRMED.** `(DRAFTED, COMMITTED)` legal (L52-60); `COMMITTED` terminal (L63). Repo-wide re-scan: **11 `COMMITTED` hits, ZERO production transitions** — the enum/table/terminal-set, the *illegal*-case fixtures (`fixtures.py:255/258`), three state tests, one projection test, and **the register-#19 docstring itself** (`not_wired.py:209`). **The gap is real and exactly as disclosed.** |
| **2** | `pipeline.py` · `provider.py` · `store.py` | ✅ **CONFIRMED**, plus a load-bearing find. `CaseStore` = `atomic()`, `put_application`, `get_application`, `put_recommendation`, `get_recommendation`, `recommendation_for_application`, `list_application_ids()`. `CasePipeline` holds a **private `_transition()`** (L163) of exactly the needed shape — but the pipeline is **never constructed in the composition root** (Q3-D), so R5 cannot reach it. `PendingCommitContextProvider.get()` is **context-assembly only**. ⚑ **`PostgresCaseStore.put_application` is an UPSERT** (`on_conflict_do_update`, `set_={state,...}`, `repository.py:95-104`) — so a state change **is** expressible through the **existing** Protocol surface. ⚠️ It is an **unconditional** upsert with **no CAS semantics**. |
| **3** | R5's handler (`app/routes/not_wired.py:184-238`) | ✅ **CONFIRMED.** Enum wire-check → 422; `service.commit(...)`; `UnauthorizedCommit`→403, `UnknownPendingRecommendation`→404, other `CommitRejected`→409; returns the dump. ⚑ **NOTHING happens to case_lifecycle state after a successful commit — no post-commit statement exists.** The handler holds **no `CaseStore` reference today**. |
| **4** | `audit_store/commit_service.py` | ✅ **CONFIRMED FROZEN AND HOOK-FREE.** Order verified: gate → independent authz re-check → context fetch → full in-memory assemble+validate **before BEGIN** → `with repository.atomic(): insert(record)` → return. **No hook, no callback, no extension point, no post-write seam** — all five injected seams are consumed **before or during** the write, none after. The service **has no concept of case_lifecycle state**. ⚑ **A transition therefore CANNOT run inside the frozen service's transaction — only before `commit()` or after it returns.** |

### ⚠️ ONE DIVERGENCE FROM THE TASK BRIEF — REPORTED, NOT ABSORBED

The brief states U24 was **"reopened three times"** and instructs that a new reopening be logged as **the fourth**.
**The disk does not support this.** The record is **consistent at TWO** across four independent artifacts —
`scope-b-wiring-summary.md §1` (*"reopened **twice**"*), **this file at L3513** (*"reopening #1 … reopening #2"*, with
distinct timestamps `2026-07-20T08:41:12Z` / `2026-07-20T11:03:25Z`), `scope-b-wiring-plan.md:1009/1027`, and
`BUILD-COMPLETION-REPORT.md:158` (*"already reopened **twice**"*). The two are **#1 `list_application_ids()` (Q1-A)**
and **#2 `memo_from_canonical()` (Q14-A)**.

The likely source of the "three" is **`audit.md:4101`**, whose *section heading* reads *"⚑ U24 THIRD REOPENING
AUTHORIZED (Q14-A)"* — **contradicted by its own entry body**, which calls the reopening *"distinct from, and in
addition to, **the** list-method reopening (Q1-A)"* (**one** prior, not two) and then contrasts it with *"**THE FIRST
REOPENING**"*; and contradicted by **`audit.md:4145`**, in the same file, which calls the identical change
***"U24 reopening #2."*** **The heading is a stale mislabel; the substance is two.**

⚑ **Consequence, recorded so it is not silently mis-numbered later: if Q2 concludes a reopening is needed, it is
U24's THIRD authorized reopening — not its fourth.** The `audit.md:4101` heading is **left unedited**: it is a
historical log line, and correcting a past entry in place would damage the append-only record. It is **superseded
here**, not rewritten.

### The core design tension this pass must resolve

**`DecisionCommitService` (audit-store, frozen) and `CaseStore` (U24) are two separate transactional boundaries.**
They cannot be merged into one atomic operation without editing a frozen unit — which every prior pass in this build
has refused to do. Any fix therefore either **prevents** the duplicate before `commit()` is reached, **records** the
transition after it returns, or **both** — with an honestly-named residual window. **Which of those actually
eliminates duplicate `AuditRecord`s versus merely narrows the race is the substance of Q1**, and is the user's call.

### Holds upheld by this pass (verified, nothing touched)

`commit_service.py` and every other frozen-23 unit's internals **UNTOUCHED** · WIRE-1's contract text **NOT amended** ·
`not_wired.py` **NOT renamed** · U23's frozen test **NOT edited** · the `audit_store` Docker-guard gap **UNTOUCHED**
(5 errors stay exactly 5) · **tier-B NOT authorized** · **no route added** under `backend/app/routes/` · **no U24 file
touched and NO reopening authorized** — whether one is even needed is **Q2**, and the answer is the user's.

**Test state carried forward, unchanged and NOT re-run by this pass**: backend **1492 passed / 0 failed / 37 skipped /
5 pre-existing `audit_store` Docker-absence errors**, coverage **99.87%**. **No code was executed or modified.**

**NEXT**: the user answers Q1–Q5 in `fix-register-19-plan.md`. **Nothing proceeds until then.**

---

## ⚑ U24 THIRD AUTHORIZED REOPENING (Q2-b) — the two-step commit claim state (2026-07-21T11:52:04Z)

**Status**: ✅ **AUTHORIZED AND LOGGED — NOT YET ACTED UPON. No U24 file has been touched. No code exists.**
**Plan of record**: `guide-docs/build/plans/fix-register-19-plan.md` — Q1–Q5 + Q3.1/Q4.1/Q5.1 **answered and embedded
verbatim**; §6 carries the ambiguity-check.

### Decisions of record

| Q | Answer |
|---|---|
| **Q1** | **(c) two-step claim state** — CAS `drafted → committing` **before** `commit()`, then `committing → committed` after it returns |
| **Q2** | **(b) reopen U24** — its **third** authorized reopening |
| **Q3** | **(a)** the CAS **is** the detection point; a lost CAS → **409**, `commit()` never invoked |
| **Q3.1** | **(i)** the stronger claim is earned: *"WIRE-1 §4's already-committed 409 is now genuinely enforced, including under concurrent access"* |
| **Q4** | **(c)** the surviving `COMMITTING` window is explicit and reconcilable; **#19 NARROWED, NOT CLOSED**, with the window opened as its own new register item |
| **Q4.1** | **(ii)** a **read-only reconciliation script** in `backend/scripts/` — deliberately **not** a CLI entrypoint on frozen `admin-cli`, avoiding the #8 collision |
| **Q5** | **(b)** tier-U logic tests **+ a tier-I concurrency test** reusing the clean-skip testcontainers guard verbatim |
| **Q5.1** | `case_lifecycle/tests/`, beside PERSIST-1 |

### ⚑ NUMBERING — this is U24's THIRD reopening, not its fourth

**Carried forward from this pass's ground-truth step and not silently absorbed.** The task brief said U24 had been
reopened three times; **the disk says twice** — `scope-b-wiring-summary.md` §1, **this file at L3513** (two distinct
timestamps), `scope-b-wiring-plan.md:1009/1027`, `BUILD-COMPLETION-REPORT.md:158`. The "three" traces to the stale
*heading* at `audit.md:4101`, contradicted by its own body and by `audit.md:4145` ("reopening #2"). **That heading is
left unedited** (append-only discipline) and **superseded**.

### Scope of the third reopening

* **`CaseState.COMMITTING`** — a new, explicitly **non-terminal** state.
* **Three new `CaseStore` methods** — a **CAS** (`drafted → committing`, returning whether it won), a **finalize**
  (`committing → committed`), and a **recovery** (`committing → drafted`).
* **`LEGAL_TRANSITIONS`** gains `DRAFTED→COMMITTING`, `COMMITTING→COMMITTED`, `COMMITTING→DRAFTED`.
* **`case_to_memo_view_state`** maps `COMMITTING → "pending"` — disclosed as a **further widening of register #14**.
* **Expected `EXPECTED_PRODUCTION_MODULES` impact: UNCHANGED at 8** — methods on **existing** modules, mirroring
  reopening #1's correct call for the same reason.

### Rationale — distinct from both prior reopenings

| | Reopening | Gap | Shape |
|---|---|---|---|
| **#1** | `list_application_ids()` (Q1-A) | R2 not implementable — **no enumeration primitive** | a **READ** gap; methods on existing modules; module set **unchanged** |
| **#2** | `memo_from_canonical()` (Q14-A) | **no memo rehydration existed anywhere** in the build | a **NEW production module**; module set 7→8 |
| **#3** | **this one** | **no concurrency control on the write path** | a **WRITE-PATH** gap; the **first reopening driven by a disclosed correctness defect (register #19)** rather than by a route being unimplementable |

**Necessity established from disk, not assumed** — **FIND 2** of this pass proved the existing Protocol
**structurally cannot** express a compare-and-swap: `get_application` reads on a **fresh connection outside
`atomic()`'s transaction** (the `_execute`-inside-`atomic()` discipline governs **WRITES only**, per the unit's own
docstring), so read-then-write is non-atomic **even inside `atomic()`**.

---

## ⛔ MANDATORY AMBIGUITY-CHECK — **NOT CLEAN. SURFACE-AND-STOP.** Code-gen plan NOT written.

| Item | Status |
|---|---|
| **A1** — `TERMINAL_STATES`: the answer says *"COMMITTED remains the **sole** terminal state"*, but **disk has `{COMMITTED, FAILED}`** and `FAILED` has been terminal since U24 was built. Removing it would break `test_no_transition_leaves_a_terminal_state`, contradict **COMMITBOUND-1(c)/FAILED-1**, and newly permit `FAILED → anything` — **which no answer requested**. | ⛔ **BLOCKER** |
| **A2** — the **CAS method's KEY is unspecified**. R5 is keyed by `recommendation_id`; state lives on `PendingApplication` keyed by `application_id`. Keyed by `application_id`, the composition root must resolve first — **re-introducing a TOCTOU window, the exact defect class this fix removes**, and leaking the join into `backend/app/`. | ⛔ **BLOCKER** |
| **A2.1** — the CAS's **return shape**. A bare `bool` **collapses "lost the CAS" and "no such id"**, silently turning today's **404 into a 409 — a WIRE-1 §4 regression introduced by the fix.** Recommended: a 3-valued enum. | ⛔ **BLOCKER** |
| **A-iii.1** — confirm the reconciliation script binds the **OWNER** engine for pending state (register **#20**), inventing no grant and leaving #20 open. | ⛔ **Confirmation required** |
| **A3** — three **hardcoded exact-set assertions** in `test_states.py` (L25-28, L37-44, and L74-77 under A1(ii)) **will fail** and need manual edits. **U24's own tests, so inside scope**; flagged so they are planned, not discovered red. | ⚠️ Disclosed |
| **A4** — under Q1(c)/Q3(a) the CAS flips state **before** `commit()`, so **every** non-crash failure branch (403/404/**409 — including a blank-reason override, a routine user error U8 is built around**) would **strand the case in `COMMITTING`**. Determinate: every `except` must recover, without masking the original rejection, each with its own tier-U test. | ⚠️ Carried into code-gen plan |
| **(i)** complement sweep auto-incorporates `COMMITTING` (7×7=49; 41+8=49, **no test edit**) — **P-CASE-4's claim survives** | ✅ Confirmed, with A3's caveat |
| **(ii)** exactly one in-edge, two out-edges, `COMMITTING` non-terminal, `COMMITTED` reachable **only** via `COMMITTING`. ⚑ Two things the answer set did not state: **`DRAFTED→COMMITTED` must be DELETED**, and the table becomes **cyclic for the first time** (verified harmless). | ✅ Confirmed |
| **(iii)** achievable with the two existing bindings, **no third read path**. ⚠️ The frozen audit surface has **no `recommendation_id` lookup** — resolved via `browse_history(None)` + one membership set. Raw SQL **rejected** (`backend/scripts/` is outside both scan roots → structurally invisible). | ✅ Confirmed |

**Test state carried forward, NOT re-run**: backend **1492 / 0 / 37 / 5**, coverage **99.87%**.
**Nothing executed. Nothing modified.** `git status` verified: **only `guide-docs/` changed; no `backend/` file
touched.**

**NEXT**: the user answers **A1**, **A2**, **A2.1**, **A-iii.1**. **The code-generation plan follows — nothing before.**

---

## ⚑ REGISTER #19 — AMBIGUITY-CHECK ROUND 2 CLEAN · CODE-GEN PLAN WRITTEN (2026-07-21T12:34:51Z)

**Status**: 🟡 **PLAN ONLY — NO CODE WRITTEN.** Stopped at the plan-file gate.
**Plans of record**: `fix-register-19-plan.md` (§7 = round-2 check) · **`fix-register-19-code-gen-plan.md`** (NEW).

### Round-1 blockers — all four RESOLVED

| Item | Resolution |
|---|---|
| **A1** | **(i)** — `TERMINAL_STATES` stays `{COMMITTED, FAILED}`, **unchanged**. `FAILED-1`/`COMMITBOUND-1(c)` untouched. **Two tests drop off the edit list.** |
| **A2** | CAS/finalize/recovery **keyed by `recommendation_id`**; U24 joins internally — no TOCTOU at the call site |
| **A2.1** | **`CommitClaimResult`** = `WON`/`LOST`/`NOT_FOUND` → 200/409/**404** — today's 404 preserved, not regressed |
| **A-iii.1** | `browse_history(None)` + a membership set, **cost disclosed in the script's docstring** |
| **A4** | Carried into the code-gen plan with **three named per-branch recovery tests** + a failure-tolerant-recovery test |

### Directed checks — all three CLEAN

* **(i)** `CommitClaimResult`/`WON`/`LOST`/`NOT_FOUND` contain **none** of `FORBIDDEN_COMMIT_TOKENS`. `NOT_FOUND` is
  a plain existence check — ⚑ **precedent, not argument**: `UnknownPendingRecommendation` already does exactly this
  and is asserted **inside `test_commitbound.py` itself**. ⚠️ **Two traps recorded**: the scan is a **substring**
  test, so **no U24 identifier may contain `authorize` (incl. `authorized`/`unauthorized`)**; and the enum goes in
  **`states.py`** to keep `EXPECTED_PRODUCTION_MODULES` at **8**.
* **(ii)** The join is **expressible in one statement with NO schema change** — `recommendation_id` is already the
  PK, the FK already exists, both tables are already in `repository.py`'s metadata. ⚑ **No migration file** (U24's
  are forward-only/immutable, so adding one would be *wrong*, not merely unnecessary). `rowcount==0`'s
  **LOST-vs-NOT_FOUND ambiguity** resolved by a failure-path-only existence query — **not** a TOCTOU reintroduction.
* **(iii)** **Exactly three edits**, fully enumerated by file+test. ⚑ **Correction 1**: one test **drops off** (A1(i)).
  ⚑ **Correction 2, correcting the instruction itself**: **`case_to_memo_view_state` needs NO LOGIC CHANGE** — its
  `else` branch already yields `"pending"` and its `Literal` is already correct; **docstring only**.

### ⚠️ B1 — NEW, needs sign-off before implementation

`app/tests/test_no_write_route.py`'s thesis — *"every write goes through the frozen `DecisionCommitService`"* —
**becomes false** once R5 writes pending state. **Narrowing proposed** (audit writes → frozen service; pending-state
writes → U24's methods; `backend/app/` still opens no transaction): **strictly more specific, not more permissive**,
per the **ADAPTER-1 "flagged in advance, not discovered in a diff"** precedent. **Violates no hold** — `backend/app/`'s
own test, not frozen-23, not U23's. **Also binding as a design constraint**: the three new methods **must own their
`atomic()` internally**.

**Skip-count predicted in advance**: **37 → 40 (+3)**; **errors 5 → 5 UNCHANGED**.
**Register #19 → NARROWED, NOT CLOSED**; surviving `COMMITTING` window becomes **its own new register item**; **#14 widened**.

**NEXT**: approve the code-gen plan **and** sign off **B1**. **Nothing before that.**

---

## ✅ REGISTER #19 FIX COMPLETE — U24's THIRD REOPENING (2026-07-21T14:06:33Z)

**Status**: ✅ **IMPLEMENTED AND GREEN.** All nine plan steps executed TDD leaf-first, each RED before GREEN.
**Plans of record**: `fix-register-19-plan.md` · `fix-register-19-code-gen-plan.md`.

### Final live numbers (measured this session)

| Metric | Before | After |
|---|---|---|
| Backend suite | 1492 / 0 / 37 / 5 | **1532 passed / 0 failed / 40 skipped / 5 errors** |
| Coverage (`--cov-fail-under=90`) | 99.87% | **99.87% — HELD** |
| `EXPECTED_PRODUCTION_MODULES` | 8 | **8 — UNCHANGED** |

* **⚑ Skips 37 → 40: exactly +3 — the delta PREDICTED IN THE PLAN BEFORE THE RUN.**
* **⚑ Errors 5 → 5, the SAME FIVE BY NAME** — `test_full_record_round_trips`,
  `test_fault_mid_transaction_rolls_back_both_rows`, `test_writer_role_cannot_update_or_delete`,
  `test_reader_role_is_select_only`, `test_browse_and_get_over_real_postgres`. **Docker-guard gap untouched.**
* `compileall` over `case_lifecycle` + `app` + `scripts` exits **0**. **Zero regression.**

### What was built

`CaseState.COMMITTING` (non-terminal) · `CommitClaimResult` (`WON`/`LOST`/`NOT_FOUND`, in `states.py` so the module
set stays 8) · `LEGAL_TRANSITIONS` **+3 edges, −`(DRAFTED, COMMITTED)`** · **`TERMINAL_STATES` UNCHANGED**, pinned by
its own test · three `CaseStore` methods keyed by `recommendation_id`, each owning its `atomic()` · a
single-statement scalar-subquery CAS · **CLAIM-1 (18 tier-U)** + **CLAIM-CONCURRENT-1 (3 tier-I)** · R5's two-step
handler with release-on-every-rejection · the read-only reconciliation script · **`INT-FAITHFUL-1` narrowed a second
time** (B1, authorized) now pinning **two** channels plus a structural ordering test.

**⚑ NO MIGRATION FILE** · **`case_to_memo_view_state`'s logic untouched** (docstring only — its `else` was already
correct) · the STATE-2 complement sweep **self-adjusted with no edit**, confirming P-CASE-4 survives.

### ⚑ Two unanticipated findings — SURFACED, NOT ABSORBED

1. **A vacuous-by-construction test fixture.** `conftest.py::wired_client` built `SequenceIdGenerator()` **inside**
   the override lambda, so every commit produced `decision_id="DEC-1"` and the in-memory repository **silently
   overwrote** rows. A *"only one AuditRecord exists"* assertion would have **passed while duplicates were genuinely
   being written** — vacuous for exactly the reason #19 exists. **Found only by asking why a test passed.** Fixed by
   hoisting the generator; no existing assertion changed.
2. **A newly-unreachable branch.** The claim makes R5's `except UnknownPendingRecommendation` unreachable on the
   normal path (coverage 99.87% → 99.82%). Resolved by **adding a test that genuinely exercises it**, not a pragma.
   **Coverage restored to exactly 99.87%.**

### Register

**#19 NARROWED, NOT DISCHARGED** · **#21 `COMMITTING-CRASH-WINDOW` OPENED** (owner: composition/U24; mitigation:
`backend/scripts/reconcile_committing_cases.py`) · **#14 WIDENED** (`COMMITTING` is a second internal state with no
wire representation). **Register now 21 tracked: 19 open · 1 discharged · 1 narrowed.**

**The honest claim**: duplicate `AuditRecord`s are **ELIMINATED** (a Postgres row-level write lock, proven at tier-I
under real concurrency) and WIRE-1 §4's already-committed **409 is genuinely enforced, including under concurrent
access**. ⚠️ **This is NOT cross-store atomicity** — a crash between the audit write and the finalize leaves the case
in `committing`: explicit, non-terminal, detectable, reconcilable, and **real**.

**Holds upheld**: frozen-23 internals untouched · WIRE-1 unamended · `not_wired.py` not renamed · U23's test not
edited · Docker-guard gap untouched · tier-B not authorized · no new route.

---

## ✅ REGISTER #19 — GATE APPROVED AND CLOSED (2026-07-21T15:11:53Z)

**User decision**: option 2, *"Continue to Next Stage — accept as complete."* **Gate approved. No further code written.**

**Closed as NARROWED, not discharged.** Duplicate `AuditRecord`s **eliminated** (Postgres row-level write lock,
proven at tier-I under real concurrency); WIRE-1 §4's already-committed **409 genuinely enforced, including under
concurrent access**; **cross-store atomicity NOT achieved and never claimed**. **#21 `COMMITTING-CRASH-WINDOW`
opened** (owner: composition/U24 · mitigation: `backend/scripts/reconcile_committing_cases.py`, read-only).
**#14 widened.** **Register: 21 tracked — 19 open · 1 discharged · 1 narrowed.**

**Verified at closure**: **1532 / 0 / 40 / 5** · coverage **99.87%** (gate held) · modules **8** · skip delta **+3 as
predicted** · the **5 Docker errors unchanged by name** · `compileall` **0** · **zero regression**.

**U24's THIRD authorized reopening is COMPLETE** — scope `CaseState.COMMITTING` + three `recommendation_id`-keyed
`CaseStore` methods; rationale (**a write-path concurrency-control gap — the first reopening driven by a disclosed
correctness defect**) distinct from #1's enumeration gap and #2's rehydration gap.

**Holds upheld**: frozen-23 internals untouched · WIRE-1 unamended · `not_wired.py` not renamed · U23's test not
edited · Docker-guard gap untouched · tier-B not authorized · no new route · **#20 left open and undecided**.

⚑ **NO NEW WORK STARTED.** Closing this gate authorized no next stage, and none was inferred.
**Awaiting the user's next authorization.**

---

## 🟡 REGISTER #18 `NO-PRODUCTION-LLMCLIENT` (B4) — SCOPING PASS IN PROGRESS (2026-07-21T15:24:19Z)

**Stage**: POST-BUILD → register-item remediation · the second item taken up after **SCOPE B CLOSED**
(the first was **#19**, closed as NARROWED at 2026-07-21T15:11:53Z).
**Status**: 🟡 **SCOPING / PLANNING ONLY — NO CODE GENERATED.** Stopped at the plan-file gate.
**Plan**: `guide-docs/build/plans/fix-register-18-plan.md`
**Register owner**: composition / `deploy-config` (secrets).
**Register severity, quoted, not softened**: *"**Non-blocking** for the wired API layer and the seeded demo.
**⛔ BLOCKING for any real memo generation** — no genuine LLM-drafted memo can be produced by this system today."*

### Ground truth re-established from disk (5 checkpoints) — gap CONFIRMED

| # | Checkpoint | Result |
|---|---|---|
| CP1 | `LLMClient` Protocol shape (`memo_agent_core/provider.py:37-42`) | ✅ frozen · `generate(*, model, prompt, temperature) -> str` |
| CP2 | GeminiAdapter location | ⚠️ **DIVERGENCE — see below** |
| CP3 | `LLMClient` × genai grep, re-run | ✅ unchanged · **zero production implementations** |
| CP4 | `google-generativeai` vs `google-genai` mismatch | ✅ exactly as disclosed · new SDK declared NOWHERE |
| CP5 | `_SeedSeams.draft_memo` construction (`seed_demo_cases.py:120-124`) | ✅ substitution point is ONE constructor argument |

### ⚑ ONE MATERIAL DIVERGENCE — surfaced, not absorbed

**`GeminiAdapter` is NOT in `memo_extensions/`.** It is in **`memo_agent_core/provider.py:45` (frozen U4)** and is a
**real** adapter awaiting a real client — not a double. `memo_extensions/` holds only `ClaudeAdapter` +
`OllamaAdapter`, and both drive a **DIFFERENT seam**: the U19-local **`ThinkingLLMClient`**
(`provider_secondary.py:34`) with a **fourth kwarg `thinking: bool`**, defined U19-locally *because* the frozen
`LLMClient` could not carry a thinking channel. **Two distinct client seams exist; the Gemini one is owned by
`memo_agent_core`.** Q2 was rewritten around the on-disk layout, not the briefed one.

⚑ **Second find**: `seed_demo_cases.py:121` passes `model=OFFLINE_MODEL_VERSION` — feeding the *version-stamp*
sentinel into the *model-id* slot. A real client requires model-id and version-stamp **separated** (bears on Q6).

⚑ **Third find**: `GEMINI_API_KEY` is **already** a required, fail-closed `Settings` field
(`secrets_config/settings.py:38`, non-empty validator L47-52) and already a Phase-1 REQUIRED placeholder in
`.env.example`. **Q3 is largely settled by disk** — the plan says so rather than manufacturing an open question.

### Eight open questions — ALL `[Answer]` TAGS BLANK, NONE PRE-FILLED

Q1 SDK choice + exact `requirements.txt` change · Q2 where the adapter lives (**bears on whether `memo_extensions`
is reopened**) · Q3 key supply / fail-closed timing · Q4 CaseSeams + seed-script integration (**must not remove
offline testability**) · Q5 **spend control — the first real-money path in the entire build** · Q6 `temperature=0`
+ the reproducibility invariant · Q7 test strategy at tier-U without a key · Q8 scope boundary (adapter alone vs
adapter + seed wiring).

**Holds declared for this pass**: no frozen-23 unit's internals edited (any `memo_extensions` landing is an
explicit, separately-rationalized **reopening**, U24-reopening discipline) · **the `LLMClient` Protocol is
IMPLEMENTED, NEVER MODIFIED** · WIRE-1 unamended · `not_wired.py` not renamed · U23's frozen test not edited ·
Docker-guard gap untouched (**5 errors stay exactly 5**) · **tier-B NOT authorized** · no new route.

**⚑ NO CODE GENERATED. Awaiting the user's answers to Q1–Q8 at the plan-file gate.**


---

## REGISTER #18 — CODE GENERATED & VERIFIED — NARROWED (2026-07-21T17:04:30Z)

**The FIRST production LLM path in the build is now on disk.** Implemented per
`fix-register-18-code-gen-plan.md`, 8 steps, TDD leaf-first, RED before GREEN. New session:
ground truth was reconstructed from disk and confirmed exact (baseline 1532/0/40/5/99.87%) before
any code; `google.genai` confirmed GENUINELY ABSENT from the environment (so test 16 is a real
lazy-import proof, and D1 stays latent).

**Two-piece shape (Q9-A), `backend/app/llm_client.py` — reopens no frozen unit:**
- `CappedGeminiClient` — flag-free, purely-injected wrapper; satisfies the frozen `LLMClient` seam
  STRUCTURALLY; counts every call (incl. retries); temperature/model pass-through; logs prompt
  LENGTH only; holds no key at all.
- `build_gemini_client` — guarded factory; the ONLY spend-capable path; owns the
  `ALLOW_REAL_LLM_CALLS` gate (`os.environ`, exact `"true"`), the `get_settings()` key read, and
  the LAZY `google.genai` import. `# pragma: no cover` on the real-spend construction region — no
  `pyproject.toml` omit entry.

**Change set**: `requirements.txt` (−google-generativeai +google-genai>=1.0.0) · `llm_client.py`
(NEW) · `tests/test_llm_client.py` (NEW, 17 tier-U tests) · `seed_demo_cases.py` (--real-llm
opt-in, dual banner, model-id/version-stamp split, real-call-count exit; `_OfflineLLMClient` +
default banner byte-for-byte unchanged) · `.env.example` (non-secret switch) ·
`composition-root/real-llm-verification.md` (NEW, manual out-of-band) ·
`composition-root/register-18-llm-client-summary.md` (NEW).

**FINAL LIVE FIGURES (ALLOW_REAL_LLM_CALLS UNSET): 1549 passed / 0 failed / 40 skipped / 5 errors
/ 99.87% coverage.** vs advance predictions: passed **1549 = 1532 + 17** (plan predicted +16; the
**+1 is the task-brief-mandated structural key-non-disclosure test**, disclosed not absorbed) ·
failed 0 · **skipped 40 unchanged (+0)** · **errors EXACTLY 5, same audit_store Docker-absence
names** · coverage gate held · **EXPECTED_PRODUCTION_MODULES 8 unchanged**. **Offline-suite
regression CONFIRMED** with the spend flag explicitly unset — zero regression.

**Step 4 was verification only** — both `backend/app/` scanners (23 tests) pass **UNMODIFIED**; no
assertion needed changing (7.1 prediction held, no prediction miss).

**One disclosed refinement**: the pragma covers the contiguous network-bound construction region
(lazy import + `genai.Client` + wrapper construction), broader than the plan's "one line" wording
but narrower than an omit entry — consistent with Confirm 1's "network-bound line(s)"; the
flag/key/refusal paths stay genuinely covered.

**Register #18 → NARROWED, NOT DISCHARGED** (Q8b decided on evidence): a production `LLMClient`
now exists and the chain is complete, but the **manual real-API verification has NOT been run
end-to-end** (no live key/network; google-genai not installed; pinned `gemini-2.5-flash-001`
unconfirmed against the live API), so DISCHARGED would overclaim. **NEW item #22
`MEMO-PROSE-NOT-BIT-REPRODUCIBLE` (#18a)** for the Q6 gap. **Register now: 22 tracked — 19 open ·
1 discharged (#2) · 2 narrowed (#18, #19).**

**HOLDS upheld**: `provider.py`'s `LLMClient` Protocol IMPLEMENTED not modified · `memo_extensions/`
untouched · every other frozen-23 unit untouched · WIRE-1 unamended · `not_wired.py` not renamed
(#13 open) · U23 frozen test unedited · `audit_store` Docker-guard gap untouched (5 stays 5) ·
tier-B NOT authorized (D1 disclosed) · no new route · `dependencies.py` not wired (Q8 — LLM-bearing
composition stays out of the request path; Scope B's Q3-D property survives).

---

## REGISTER #20 — SCOPING PASS STARTED (2026-07-22T16:46:43Z)

**`PENDING-TABLES-NO-EXPLICIT-GRANTS`** — the third register item taken up for review after Scope B
closed (after #19 NARROWED and #18 NARROWED). **Status: 🟡 SCOPING / PLANNING ONLY — no code, no
migration change generated.** New session: ground truth reconstructed from disk and reported at five
checkpoints before any design work.

**The gap is CONFIRMED exactly as located:** `case_lifecycle/migrations/0001_case_lifecycle.sql`
creates `pending_application` / `pending_recommendation` with **no `GRANT` and no `CREATE ROLE`** —
owner-only by default. `dependencies.py` binds `get_case_store()` → `PostgresCaseStore(app_engine())`
(the owner / `DATABASE_URL` engine). `0002_grants.sql` creates only `audit_writer` (INSERT+SELECT)
and `audit_reader` (SELECT) on `audit_record` + `applicant_profile_snapshot` **only**; neither audit
role touches the case store.

**⚑ ONE FRAMING DIVERGENCE from the register, surfaced not absorbed:** the register (BUILD-COMPLETION-
REPORT §5 #20; scope-b-wiring-summary §5 #20) calls this *"explicitly NOT decided / an open
observation."* On disk the no-grants posture is **implemented, documented, and locked by a passing
tier-U test** — `test_migscope.py::test_u24s_migration_grants_to_no_u15_role` (comment-stripped grant
scan), tied to **NFR-CASE-MIGSCOPE-1 (P-CASE-11)**, **BR-CASE-12**, **CASE-Req-Fold-1 / CASE-D4**. The
genuinely-open residual is therefore **narrower than "undecided"**: the *documented* rationale is
**migration self-containment** (keeps U24's tier-I test runnable without U15's `0002_grants.sql`), not
an affirmative **access-model security judgment** about whether the audit roles should ever read
pre-commit drafts. **Decisive precedent:** `app_user` (a table) is itself owner-only with no
audit-role grants, reached via `app_engine()` — the pending tables sit inside the **same established
posture**, not an anomaly.

**Plan of record:** `guide-docs/build/plans/fix-register-20-plan.md` — open decision as numbered
`[Answer]` tags (all blank), on the `fix-register-18`/`#19` model. **STOPPED at the plan-file gate.**

**HOLDS for this pass** (all upheld — no code written): no edit to U15's frozen `0001_initial_schema.sql`
or `0002_grants.sql`; a new U24 migration, IF the decision warrants one, must be forward-only and
collision-guarded per the #19-fix discipline (a new higher-numbered file, never editing
`0001_case_lifecycle.sql`); no edit to any other frozen-23 unit's internals; WIRE-1 text not amended;
`not_wired.py` not renamed; U23's frozen test not edited; the `audit_store` Docker-guard gap untouched
(5 errors stay exactly 5); tier-B not authorized; no new route under `backend/app/routes/`.

**Register unchanged at 22 tracked** (19 open · 1 discharged · 2 narrowed); #20 is among the open items,
now under scoping review. Test state carried forward, NOT re-run this pass: **1549 passed / 0 failed /
40 skipped / 5 errors / 99.87%**.

---

## REGISTER #20 — DISCHARGED (2026-07-22T17:19:09Z) — the register's FIRST clean full discharge

**`PENDING-TABLES-NO-EXPLICIT-GRANTS`** resolved by `fix-register-20-plan.md` (Q1–Q4 answered). This
is a **documentation/disclosure resolution** — no behaviour changed, **no migration written**, no unit
reopened. It is the register's **first CLEAN full discharge**, distinct from #2 (partly discharged) and
#18/#19 (narrowed, each with a surviving residual tracked as #22/#21). **#20 leaves no residual and
opens no new item.**

**CORE-RATIONALE-20 (identical wording in `BUILD-COMPLETION-REPORT.md`, `audit.md`, and the two in-code
notes):** Owner-only access to the pending tables (`pending_application`, `pending_recommendation`) is
**deliberate least privilege, not an unreviewed gap.** The pending tables hold pre-commit,
not-yet-audited drafts. `audit_reader` is scoped to the committed audit trail (R6/R7) and gains nothing
legitimate from reading drafts — doing so would broaden its surface against SEC-4's least-privilege
intent. `audit_writer` has exactly one caller, the frozen `DecisionCommitService`, which receives
fully-assembled `CommitContext` inputs from the owner-engine provider and never touches pending state
directly. No wired caller in R2–R5 reaches the pending tables through a non-owner engine. This is the
same owner-only posture the build already applies to `app_user`, and it is enforced by the passing
tier-U test `test_migscope.py::test_u24s_migration_grants_to_no_u15_role` (NFR-CASE-MIGSCOPE-1 /
BR-CASE-12). No new test and no migration are required; the posture was already correct and asserted.
#20's only genuine defect was that this correctness had been recorded under a *migration-self-
containment* rationale (CASE-Req-Fold-1) and never as an affirmative *access-model security* judgment —
now stated.

**Changed — two docstring-only edits, zero behaviour:** `backend/app/dependencies.py` header note and
`backend/scripts/reconcile_committing_cases.py:44`, both from *"NOT decided / undecided"* to *"RESOLVED
— deliberate owner-only least privilege."* Docstring-stripped by the `backend/app/` AST scanners or
outside every scan root; no forbidden substring. **Full suite byte-for-byte identical: 1549 passed / 0
failed / 40 skipped / 5 errors (same names) / 99.87% coverage.**

**⚑ Disclosed process finding (not smoothed over):** the plan's §1 ground-truth pass found **only one**
in-code #20 reference (`dependencies.py:22`) and **missed the second** (`reconcile_committing_cases.py:44`),
caught **only** by the ambiguity-check's directed check (ii) and surfaced-and-stopped on before any
edit. Without it, the codebase would have shipped a self-contradiction (one file "decided", another
"undecided"). Recorded on the #19-vacuous-fixture / #18-Q9-collision precedent.

**Register now: 22 tracked — 18 open · 2 discharged (#2 partly, #20 fully) · 2 narrowed (#18, #19).**
⚑ **Count note:** #20 was one of the prior 19 open, so discharging it drops open 19 → **18** (18+2+2=22,
tracked total preserved); a "19 open + #20 discharged" reading would double-count to 23.

**HOLDS upheld:** U15 frozen migrations untouched · U24 checksum-locked `0001_case_lifecycle.sql`
untouched · no new migration · no other frozen-23 internal edited · WIRE-1 unamended · `not_wired.py`
not renamed · U23 frozen test unedited · `audit_store` Docker-guard gap untouched (5 stays 5) · tier-B
not authorized · no new route.

---

## REGISTER #8 — SCOPING PASS BEGUN (2026-07-22T17:41:24Z) — `DEPLOY-MIGRATE-DEFERRED`

**New session; ground truth reconstructed from disk and reported at 5 checkpoints.** The fourth register
item taken up after Scope B closed (after #19 NARROWED, #18 NARROWED, #20 DISCHARGED). Register severity,
quoted: *"**Non-blocking** at build time; **blocking for an actual deploy**."*

**The gap, CONFIRMED exactly:** `render.yaml:17`'s `preDeployCommand` is `python -m backend.database.migrate`,
and **`backend/database/migrate.py` is absent** — the referenced CLI entrypoint exists nowhere on disk.
No single command applies both U15's and U24's migration sequences for a fresh deploy. U24 deliberately
authored no entrypoint (MIGSCOPE-1); U15's Infra Design deferred the migration *tool* to Code-Gen and named
a deploy-config-wired pre-deploy step without authoring a Python entrypoint; deploy-config wired the *slot*,
naming the runner as database's/composition's deliverable. **Nobody built it.**

**Findings that shape the open questions (reported, not absorbed):**
- **No hard ordering dependency.** U24's `0001_case_lifecycle.sql` has FKs only between its own two tables —
  **no FK to any U15 table** — so the two sequences are safely applicable in either order (the seed-script
  precedent does U15-then-U24; that order is convention, not a schema requirement).
- **render.yaml is NOT frozen** — U23's `is_under_frozen()` returns False for it (asserted by
  `test_noedit.py:45`); it is root-level config, outside every frozen tree.
- **No test asserts the `preDeployCommand` value** — `test_boot.py:36` asserts only its *presence*; the
  string `backend.database.migrate` appears in no test file.
- **No in-process CLI wrapper exists for U15** — every caller constructs `MigrationRunner` directly.

**This is a SCOPING pass — NO code generated.** `fix-register-8-plan.md` surfaces Q1–Q6 as blank `[Answer]`
tags with grounded recommendations. Register unchanged at **22 tracked** (18 open · 2 discharged · 2 narrowed);
**#8 is among the open items, now under scoping review.** Test state carried forward, NOT re-run this pass:
**1549 passed / 0 failed / 40 skipped / 5 errors / 99.87%.**

---

## REGISTER #8 — Q1–Q6 ANSWERED, AMBIGUITY-CHECK CLEAN, CODE-GEN PLAN WRITTEN (2026-07-22T18:05:11Z)

Answers embedded verbatim into `fix-register-8-plan.md`: **Q1(b)** entrypoint in `backend/scripts/run_migrations.py`
· **Q2(a)** both sequences U15→U24, owner engine, U24 via `apply_case_migrations()` (C-C) · **Q3(a)** hardcoded,
explicitly named · **Q4** idempotency confirmed by construction + fail-loud · **Q5** update `render.yaml`'s
`preDeployCommand` as a named edit · **Q6(c)** tier-U + tier-I, ping-guard clean-skip confirmed.

**Ambiguity-check (3 directed checks) — all resolved:** (i) CLEAN — `backend/scripts` is outside every
structural file-set scan **and** outside `--cov` (coverage-invisible, like the two existing scripts). (ii)
CLEAN — the new tier-I test uses the `_docker_available()` ping-guard, so Docker-absence is a **SKIP, never a
6th error** (mechanism traced against `audit_store`'s importorskip-only pattern that produces the 5 errors);
**5 errors stay exactly 5**. (iii) literal-CLEAN — the `render.yaml` value edit breaks no test (verified vs
`test_boot`/`test_format`/`test_sec3` actual content) — **plus one adjacent doc-consistency finding SURFACED,
not absorbed**: `render.yaml`'s own comment and `deploy/README.md`'s MIGRATION section still frame the
entrypoint as deferred/not-yet-existing and would contradict the fix. Folded into the code-gen plan as flagged
scope (README edit explicitly beyond the literal Q5 answer, for plan-gate approval).

**`fix-register-8-code-gen-plan.md` written** — component inventory (C1 entrypoint + tier-U + tier-I tests +
`render.yaml` + flagged `deploy/README.md` + register update), TDD leaf-first order (tier-U → entrypoint →
tier-I → `render.yaml` last → flagged README → register), RED-before-GREEN, exact count predictions
(**final no-Docker: 1556 passed / 0 / 43 skipped / 5 errors / 99.87%**), and an explicit
**NARROWED-vs-DISCHARGED** honest-claim section (DISCHARGED iff tier-I confirmed green under Docker; else
NARROWED on the #18 precedent, decided on evidence at Step 6).

**STOPPED at the plan-file gate — no code generated.** Register unchanged at **22 tracked** (18 open · 2
discharged · 2 narrowed); **#8 among the open items.** Baseline carried forward, not re-run: **1549 / 0 / 40 /
5 / 99.87%.**

---

## REGISTER #8 — NARROWED (2026-07-22T18:24:22Z) — `DEPLOY-MIGRATE-DEFERRED`

**`DEPLOY-MIGRATE-DEFERRED`** resolved-in-code by `fix-register-8-code-gen-plan.md` (Steps 0–6 executed in
order). The register's **third NARROWED** outcome (after #18, #19), the fourth item after Scope B.

**The missing entrypoint now EXISTS**: `backend/scripts/run_migrations.py` — a cross-unit orchestrator
(Q1-B, in `backend/scripts/` not frozen `backend/database/`) that builds the owner engine from
`get_settings()` and applies **both** sequences in one invocation — U15 via `MigrationRunner`, then U24 via
`apply_case_migrations()` (guard-first, C-C). Hardcoded/explicitly-named (Q3-A), idempotent by construction,
fail-loud (Q4-A), never logs rendered SQL (SEC-3). `render.yaml`'s `preDeployCommand` now names it (was
`python -m backend.database.migrate`, absent).

**Outcome: NARROWED, not DISCHARGED — decided on evidence per plan §7.** Tier-U orchestration contract proven
(7 tests: engine-from-settings, U15-before-U24, U24-via-apply_case_migrations-once, **constructor-arg spy
proving CASE_MIGRATIONS_DIR never reaches the wrong runner**, fail-loud + `dispose()`-via-`finally` on each
half separately, no-rendered-SQL). Tier-I integration test **written** but **SKIPPED here (no Docker)** — the
real-database proof is not executed in this environment, and no CI/Docker run has confirmed it green
observably. The live Render release step is not run. So the entrypoint is structurally complete + tier-U-proven
but the real-DB confirmation is outstanding → **NARROWED** (the #18 precedent; the bar is confirmed-against-a-
real-database, not code quality). **Residual tracked on #8 itself, no new item**: tier-I written-but-unexecuted
(CI-gated) + live release step not run; discharges to DISCHARGED once tier-I is confirmed green under Docker,
no code change needed.

**Adjacent doc-consistency finding (surfaced at ambiguity-check, #20 precedent):** `render.yaml`'s comment
and `deploy/README.md`'s MIGRATION section both said the entrypoint was deferred/not-yet-existing; both
updated (render comment within Q5; README C7 approved at the plan gate as beyond the literal Q5 answer). Both
test-neutral. Historical design/register rows **superseded, not rewritten**.

**Verification — full suite, live, EXACT to advance predictions: 1556 passed / 0 failed / 43 skipped / 5
errors (same names) / 99.87%.** Δ baseline: +7 passed (tier-U), +3 skipped (tier-I), errors 5→5, coverage
unchanged (`backend/scripts` not a `--cov` target — `run_migrations.py` is coverage-invisible; test-covered,
not counted).

**Register now: 22 tracked — 17 open · 2 discharged (#2 partly, #20 fully) · 3 narrowed (#8, #18, #19).**
⚑ Count: #8 was one of the prior 18 open → open 18→17, narrowed 2→3 (17+2+3=22, total preserved), no new item.

**HOLDS upheld:** U15/U24 `.sql` migrations untouched · frozen `MigrationRunner`/`verify_checksums` called
never edited · no other frozen-23 internal or test edited (U23's `deploy_config/tests/*` untouched, 41 pass) ·
WIRE-1 unamended · `not_wired.py` not renamed · `audit_store` Docker-guard gap untouched (5 stays 5) · tier-B
not authorized · no new route.

---

## TIER-B AUTHORIZATION — SCOPING PASS BEGUN (2026-07-23T04:43:32Z) — register #3 + #9 + #10 + #18 + #22

**New session; ground truth reconstructed from disk and reported at 5 checkpoints before any design
work.** The **fifth** item taken up after Scope B closed (after #19 NARROWED, #18 NARROWED, #20
DISCHARGED, #8 NARROWED) — and the **first that is an entire TESTING TIER rather than a single
register item**. It addresses five register items at once:

| # | Item | Relation to tier-B |
|---|---|---|
| **#3** | `tier-B corpus run` | the corpus has never been generated — the tier's headline gap |
| **#9** | `PROMPTFOO-CLI-DEFERRED` | the real rubric engine; **one-way prerequisite of #10** |
| **#10** | `JUDGE-EVAL-DEFERRED` | the real ≥4/5 gate over real memos (AC-6) |
| **#18** | `NO-PRODUCTION-LLMCLIENT` (NARROWED) | supplies the only guarded real-LLM path that exists |
| **#22** | `MEMO-PROSE-NOT-BIT-REPRODUCIBLE` | bounds what a tier-B run may honestly claim about AC-1 |

**Status: 🟡 SCOPING / PLANNING ONLY — no code, no API call, no spend, no corpus generated.**

### Ground truth — 5 checkpoints, all confirmed against disk

1. **`corpus_generator/build.py` — CONFIRMED as the register describes.** 95 lines; argparse `main()`;
   `_GeminiLLMClient(settings.GEMINI_API_KEY)` → `CorpusGenerator` → writes `corpus/profiles.json` +
   `corpus/manifest.json`. **Never run — `corpus/` does not exist.** Coverage-omitted; excluded by name
   from two structural scans (`_EXCLUDED_FILES = {"build.py"}`). **Cannot run today: `google.genai` is
   NOT installed here** (confirmed live), despite `requirements.txt` now declaring `google-genai>=1.0.0`.
   ⚑ **Divergence A** — `--model-id` defaults to the **floating alias** `gemini-2.5-flash`, and that value
   is stamped into `CorpusManifest.model_version`, **contradicting #22's shipped non-floating pin**
   (`REAL_MODEL_ID = "gemini-2.5-flash-001"`). ⚑ **Divergence B** — `_GeminiLLMClient` has **no cap, no
   `ALLOW_REAL_LLM_CALLS` gate, no logging**; **#18's guardrails do not cover it.** ⚑ **Divergence C** —
   `corpus/` has **no `.gitignore` entry**, so a generated corpus is committable by default, undecided.

2. **What "tier-B not authorized" means operationally — THERE IS NO FLAG.** 31 tier-B mentions across
   Python, **all** docstrings / comments / test names. No `TIER_B_AUTHORIZED` constant, no env gate, no
   code path consults anything. tier-B is unauthorized **purely because nothing has ever invoked the
   entrypoints**. The only (negative, indirect) enforcement: the coverage omit, the two scan exclusions,
   and U22's `test_promptfoo_is_never_imported_into_the_running_test_process`.

3. **#18's `llm_client.py` vs `corpus_generator`'s `_GeminiLLMClient` — TWO INDEPENDENT REAL-API CLIENTS
   NOW COEXIST.** Same frozen seam, same SDK, same call — but `CappedGeminiClient` takes an
   already-constructed SDK client (**holds no key**), enforces a **hard cap counting retries**, logs
   prompt **length** only, and is reachable only via `build_gemini_client` (which owns the
   `ALLOW_REAL_LLM_CALLS` gate + key read). `_GeminiLLMClient` takes the **raw key**, has **no cap, no
   gate, no logging**. `build.py` cannot import `backend/app/llm_client.py` without a frozen-boundary
   question (unit → composition-root is the direction every structural scan prevents). **The duplication
   is real and is its own open decision, not defaulted.**

4. **`EvalTier.LIVE` HAS NO CONSUMER.** It appears in exactly two places repo-wide — its own enum member
   and `EvalRunResult.tier`'s default. `run_eval(tier=…)` **stamps** it; nothing branches on it; no
   production caller passes it. **There is no llm-judge entrypoint of any kind.** And the shapes do not
   connect: `CorpusRecord` (profile + documents_text + label + intended_class + edge_case_tags) vs
   `JudgedSample` (memo `DecisionMemo` + rule_report + provider) — **nothing in the build converts one to
   the other.** The corpus **output half is settled**: three independent `from_file` readers
   (`quality_gates/corpus_loader.py`, `outlier_model/corpus_source.py`, tests) already expect exactly
   `corpus/profiles.json`'s JSON-array-of-`CorpusRecord` shape.

5. **Cost/scale — itemized from code; #18's guardrails are NOT adequate, but two gates are FREE.**
   `DocumentTextGenerator._DOC_TYPES` has **three** entries and `generate_for()` calls the LLM **once per
   doc type per profile** → corpus generation is **3 × N**, i.e. **~900 calls at N=300**, not 300.
   Rejection sampling is **pure Python before the prose loop — discarded attempts cost nothing**. Memo
   drafting is **1–2 calls** each (`MEMO_CITATION_RETRY_CAP = 2`). Judge scoring ≈ **1 call per sample**.
   Full scale ≈ **1,500–1,800 real calls** vs **#18's cap default of 20** — **75–90×**.
   ⚑ **DECISIVE, cutting the other way: all four `quality_gates` are LLM-FREE.** Bias-swap,
   reproducibility and rule-coverage drive only `RulesEngine.evaluate()` / `evaluation_output()`;
   coverage reads `pyproject.toml`. Running the four blocking gates over a **real** corpus costs **zero
   additional LLM calls** and **structurally cannot surface #22's prose non-determinism** — they never
   touch prose.

### ⚑ Two further findings — both divergences from the register's framing

**FINDING 1 — #9's stated blockers now have concrete mechanisms; the register's rationale is partly
outdated.** Verified live: **Node v22.17.1 and npx 11.16.0 ARE present** (discharge criterion 1 already
satisfied *here*, though the register says the Node engine is absent). The installed shim is
**promptfoo 0.1.4**; its `cli.py` npx fallback is `npx -y promptfoo@{version}` with
`version = os.environ.get("PROMPTFOO_VERSION", "latest")` — so **pinning is available**
(criterion 2), and `npm install -g promptfoo@<exact>` bypasses npx entirely. Its `telemetry.py` is
**disabled by `PROMPTFOO_DISABLE_TELEMETRY=1`** (criterion 3). **Three of five criteria have mechanisms
today**; criteria 4–5 (bind the adapter, verify real-shape interop) remain genuinely open. This does not
make promptfoo the right route — it makes **both routes real choices**, which is Q2.

**FINDING 2 — a HARD STRUCTURAL BLOCKER the brief's framing did not anticipate.**
**(a)** U22's frozen tests **hard-assert `discharged is False`** for all three register items in **three**
separate tests (`test_governance.py::test_the_three_register_items_are_named_owner_attributed_and_undischarged`,
`test_clidefer.py::test_the_cli_deferral_is_disclosed_with_its_five_discharge_criteria`,
`test_clidefer.py::test_no_register_item_claims_discharge`). **U22's design specifies NO mechanism for
flipping `discharged` to True.** Discharging #9/#10 *in code* is a **MATCHED PAIR** (register edit +
frozen-test edit), exactly the #13 rename problem — neither half valid alone.
**(b)** A real `RubricEngine` adapter **cannot live under `backend/llm_judge/`**:
`test_u22_adds_no_new_dependency_beyond_the_standard_library_and_frozen_units` pins production import
roots to `{backend, dataclasses, enum, typing, __future__}`;
`test_no_production_module_opens_a_network_connection_or_spawns_a_process` forbids
`subprocess/httpx/requests/socket/urllib/aiohttp`;
`test_no_u22_module_reads_a_secret_or_an_environment_variable` forbids `os.environ`/`getenv`/`api_key`
across **production AND tests**; `FORBIDDEN_PRODUCTION_IMPORTS = {"promptfoo"}`. **It must land outside
the unit** — the #18 (`backend/app/llm_client.py`) and #8 (`backend/scripts/run_migrations.py`) shape.

**Plan of record:** `guide-docs/build/plans/tier-b-authorization-plan.md` — open decisions as numbered
**blank** `[Answer]` tags, on the `fix-register-8/18/19/20` model but **deliberately UNBUNDLED** given
this item's scale (an entire tier, five register items, the first real-money path at scale).
**STOPPED at the plan-file gate.**

**HOLDS for this pass** (all upheld — no code written, no call made, no money spent, no corpus
generated): no edit to any frozen-23 unit's internals; **no edit to U22's frozen `DEFERRED_REGISTER`
entries**; WIRE-1 text not amended; `not_wired.py` not renamed; U23's frozen test not edited; the
`audit_store` Docker-guard gap untouched (**5 errors stay exactly 5**); no new route under
`backend/app/routes/`; **#18's spend guardrails neither weakened nor bypassed by this pass** — any change
to them is its own explicit sub-decision (Q3).

**Register unchanged at 22 tracked** (17 open · 2 discharged (#2 partly, #20 fully) · 3 narrowed (#8,
#18, #19)); **#3, #9, #10 are among the open items and #18, #22 among the narrowed/open**, now under
scoping review together. Test state carried forward, **NOT re-run this pass**: **1556 passed / 0 failed /
43 skipped / 5 errors / 99.87%**.

---

## TIER-B — Q1–Q12 ANSWERED · AMBIGUITY-CHECK CLEAN · STAGE 1 CODE-GEN PLAN WRITTEN (2026-07-23T05:25:31Z)

**STAGE 1 ONLY AUTHORIZED (Q1-a): corpus generation + the four LLM-free blocking gates. Stages 2 and 3 are NOT
authorized.** Answers embedded **verbatim** into `tier-b-authorization-plan.md` — **12 filled, 0 blank** (verified
by count).

**Answers**: **Q1(a)** Stage 1 only · **Q2 DEFERRED-PENDING-STAGE-2** (promptfoo-vs-route-around not pre-committed;
recommendation preserved intact) · **Q3(b)+dry-run**, explicitly not (a); gate stays exactly
`ALLOW_REAL_LLM_CALLS=="true"`, caps rise only by explicit argument · **Q4(b)** new guarded entrypoint under
`backend/scripts/`, `build.py` left as-is and disclosed superseded-not-deleted · **Q5(b)→(d)** confirm the served
dated model id via `models.list`, then pin + stamp SDK version · **Q6(c)→(a)** zero-cost offline shape-pilot at
N=300 first, then the real run as a prose swap · **Q7(a)** commit the corpus (not bit-regenerable, so an
uncommitted corpus makes downstream claims unfalsifiable) · **Q8, Q9 DEFERRED-PENDING-STAGE-2** ·
**Q10(d)** — the four-gate floor IN Stage 1, the prose-reproducibility probe deferred, **raw-prose bias-swap
REJECTED outright** · **Q11a(c)** documentation-only + a new register item for the un-recordable discharge;
**11b(a)** report-as-measured, **stated in advance before any number exists** · **Q12(c)** Gemini only, Claude gap
kept on the books.

### Ambiguity-check — 6 directed checks, ALL CLEAN, 2 findings surfaced, 2 constraints discovered

* **(i) CLEAN** — nothing lands in `backend/llm_judge/`; QG's REFNOTOWN scan is `backend/quality_gates`-scoped and
  BLOCKING-1's `_GATE_TEST_MODULES` is a fixed four-name list. **Constraint**: the gate run must be a **SCRIPT**,
  never a corpus-presence-skipped test added to that list.
* **(ii) CLEAN, verified fresh not inherited** — `corpus/` is outside `testpaths`, holds no `.py`, is
  coverage-invisible; **no test enumerates repo-root children**; `U23_ARTIFACTS` is a fixed list. ⚑ **Decisive**:
  both *"no corpus/"* tests use **`tmp_path`**, not the repo root — `test_default_path_needs_no_corpus_file`
  asserts the **pytest temp dir** is empty. **A real `corpus/` breaks neither. 5 errors stay exactly 5.**
* **(iii) CLEAN** — all 17 `test_llm_client.py` tests are monkeypatch-isolated; `test_the_cap_default_is_20` pins
  the **default**, which Q3's explicit-argument rule preserves; the entrypoint must not import `google.genai` at
  module scope. Offline default guarantee intact.
* **(iv) ⚑ ONE ACTIONABLE FINDING + FOUR FROZEN STALENESS LOCATIONS** — first verified **no test asserts** any of
  these substrings. **Actionable, non-frozen**: `backend/scripts/seed_demo_cases.py:97` (*"build.py is a tier-B
  entrypoint that is not authorized"*) becomes **doubly false** — **surfaced, not absorbed**, folded into the
  code-gen plan as **flagged scope for plan-gate approval**. **Frozen, NOT edited** (supersede-not-rewrite):
  `llm_judge/engine.py:88`, `llm_judge/schemas.py:52`, `llm_judge/tests/test_governance.py:7`,
  `case_lifecycle/tests/test_governance.py:6`. ⚑ Precise nuance: the accurate post-Stage-1 position is
  ***"tier-B corpus generation authorized; tier-B judge evaluation NOT authorized"***, so `JUDGE_EVAL_DEFERRED`
  stays **substantially true for its own subject (#10)** — mild staleness, **not a contradiction**.
* **(v) CLEAN on the SDK question, ⚑ MATERIAL NEW FINDING.** Verified **live**: `CorpusGenerator` + all four gates
  import with `'google.genai' in sys.modules == False`. ⚑ **The N=300 pipeline has NEVER been run, even offline** —
  `real_config` builds only the `oracle` fixture; every generator test uses `test_scoped_config` (N=9,
  `tolerance_pp=50`, two-edge subset). **The ±3pp band and the 8-edge checklist have only ever been satisfied by
  `SkewAudit` unit tests over synthetic counts.** So the shape-pilot is a **genuine experiment with a real failure
  mode**; the code-gen plan **defines the failure branch and does NOT predict success**. **Constraint**: the
  entrypoint defines its **own local offline double**, never importing a frozen unit's `conftest`.
* **(vi) CLEAN, one adjacent constraint.** `corpus/` is **NOT gitignored** (`git check-ignore` → not ignored), so
  **Q7(a) needs no `.gitignore` edit** and U16's `test_gitignore_lists_dotenv` is untouched. No repo-size or
  file-count assertion exists. ⚑ **Constraint**: `test_env_example_matches_settings_fields` asserts `.env.example`
  **active** keys **==** `Settings.model_fields`, so **any new switch must be a CLI argument or a commented line —
  never a new active key** (`ALLOW_REAL_LLM_CALLS` passes today only because it is commented out).

### ⚑ Incidental finding — candidate NEW register item, deliberately NOT fixed

**`GUIDE-DOCS-BUILD-GITIGNORED`** — `.gitignore:19`'s **`build/`** rule (written under `# Node / frontend`, plainly
meant for frontend output) is **unanchored** and matches **`guide-docs/build/`**. Confirmed:
`git check-ignore -v guide-docs/build/plans/x.md` → `.gitignore:19:build/`; `git ls-files guide-docs/build/plans/`
returns **nothing**. **Blast radius: the entire BUILD phase** — all 24 unit design directories and all 100+ files in
`guide-docs/build/plans/`, including every `fix-register-*` plan **and both tier-B plans**. DISCOVER, `guide-state.md`
and `audit.md` are **tracked and unaffected**, which is why this never appeared in `git status`. **Not fixed here**:
out of scope for a spend authorization, not risk-free (U16's governance test reads `.gitignore` and runs
`git ls-files`), and the fix is a real decision. **Owner**: repo hygiene, adjacent to register **#12**.
**Non-blocking** for behaviour; a real reproducibility/audit-trail gap. **Disposition: open after Stage 1 closes.**

### Plan of record

**`guide-docs/build/plans/tier-b-stage1-code-gen-plan.md`** — C1 guarded corpus entrypoint
(`backend/scripts/build_corpus.py`, three modes: dry-run / offline-default / `--real-llm`), C2 four-gate runner
(`backend/scripts/run_quality_gates.py`, zero LLM), C3+C4 tier-U tests (9+6), C5 the committed corpus, C6 gate
evidence, **C7 the FLAGGED `seed_demo_cases.py:97` edit**, C8 register updates. **14 steps, TDD leaf-first,
RED-before-GREEN**, with **two explicit STOPS before any billable call** (Step 7 dry-run cost confirmation; Step 8
`models.list` first-network-call). **Advance predictions: 1571 passed / 0 failed / 43 skipped / 5 errors / 99.87%**
(+15 tier-U; `backend/scripts` not a `--cov` target so C1/C2 are coverage-invisible). Includes an explicit
**WILL / WILL NOT establish** section: Stage 1 verifies **AC-1, AC-3, AC-4** over real data and creates the corpus,
but establishes **nothing** about **AC-6**, **#9**, **#10**, or memo quality, and **#22 is inherited** — the corpus's
`documents_text` is LLM-generated and **inside the content hash**, so the corpus is **not bit-regenerable** either.

**STOPPED at the plan-file gate.** **Register unchanged at 22 tracked** (17 open · 2 discharged · 3 narrowed).
Test state carried forward, **not re-run**: **1556 / 0 / 43 / 5 / 99.87%**.

**HOLDS upheld**: no code generated · **no API call, no money spent, no corpus generated** (`corpus/` still absent;
`ALLOW_REAL_LLM_CALLS` unset) · no frozen-23 internals edited · **U22's `DEFERRED_REGISTER` and its frozen tests
untouched** · WIRE-1 unamended · `not_wired.py` not renamed · U23's frozen test unedited · `audit_store` Docker-guard
gap untouched (**5 stays 5**) · no new route · **Stages 2 and 3 NOT authorized** · **#18's guardrails neither
weakened nor bypassed**.

---

## TIER-B STAGE 1 — STEPS 0–6 DONE · SHAPE-PILOT SUCCEEDED · STOPPED AT THE STEP-6 CHECKPOINT (2026-07-23T06:15:47Z)

**NO API CALL · NO MONEY SPENT · NO REAL CORPUS GENERATED.** Steps 7–13 not started.

| Step | Result |
|---|---|
| **0** baseline, **live-confirmed** (not trusted from the plan) | **1556 / 0 / 43 / 5 / 99.87%** — exact |
| **1–2** C1 `backend/scripts/build_corpus.py` | RED → GREEN, **9/9** tier-U |
| **3–4** C2 `backend/scripts/run_quality_gates.py` | RED → GREEN, **6/6** tier-U |
| **5** full suite | **1571 / 0 / 43 / 5 / 99.87%** — ⚑ **EXACT match to advance predictions**, no divergence |
| **6** offline shape-pilot @ N=300 | ⚑ **SUCCEEDED** |

**C1** — three modes, safest default: `--dry-run` (zero cost, **measures** the call count via a counting offline
double, writes nothing) · default **offline** (zero cost, writes artifacts — the Q6c shape-pilot) · `--real-llm`
(billable; requires **also** `ALLOW_REAL_LLM_CALLS=true`, an explicit **non-floating** `--model-id`, and an
explicit `--max-llm-calls` — both with **no default**). The real path runs **exclusively** through
`build_gemini_client`, inheriting both #18 gates.

**C2** — the **missing production caller** for U13's four blocking gates (a repo-wide scan confirms nothing in the
build ever ran them over a corpus). Reads `rulebook_version` **from the manifest** (QG-Fold-2); fail-loud non-zero
exit on any failing gate. Deliberately a **script, not a pytest test** (ambiguity-check (i): BLOCKING-1 forbids
skip markers on QG's four listed modules).

### ⚑ Step 6 — the experiment, and it passed at the designed defaults

Framed in advance as a genuine experiment that might fail, because the ambiguity-check established **the N=300
pipeline had never been run, even offline**. Result: **300 profiles frozen in 2.9 seconds.**

* **Class split 120 / 105 / 75 = 0.4000 / 0.3500 / 0.2500 — band delta 0.00pp on all three classes** (±3pp).
* **All 8 DATA-2 edge cases present.** No `SkewAuditError`, no `BudgetExhaustedError`.
* ⚑ **`tolerance_pp` NOT widened and `attempt_budget` NOT raised** — it succeeded at the designed defaults, untouched.
* **Determinism proven at full scale**: a second independent run produced the **identical** `content_hash`
  `57821891ba502e2e213c096bf3b0f5d3ab9e60107b13b687753b437bb7290525`. **DET-1 holds at N=300.**
* **Size (Q7's input): `profiles.json` 604 KB, `manifest.json` 840 B** — committing is unproblematic, **no Git LFS
  fallback needed**.
* **All three downstream readers verified** against the 300-record artifact (`quality_gates.CorpusLoader.from_file`,
  `outlier_model.CorpusSource.from_file`, both `.profiles()` projections → 300).

### ⚑⚑ The four blocking gates PASS over the 300-profile corpus — and this is decisive for the spend decision

Run in **2.4 seconds, zero model calls**: **bias-swap `delta_count` 0** over 300 profiles (**AC-3**) ·
**reproducibility 100.0%** over 300 × 10 runs (**AC-1**) · **rule coverage 100.0%, 11/11 rules** at rulebook 1.0.0
(**AC-4**) · **coverage-wiring passed**.

> ⚑ **These results are IDENTICAL to what the real corpus would produce.** Every gate consumes only
> `CorpusLoader.profiles(records)` — i.e. `record.profile` — and **no gate reads `documents_text`**. The profiles
> are seeded, deterministic and **real**; only the prose is placeholder. **So AC-1, AC-3 and AC-4 are already
> verified over a genuine 300-profile corpus at ZERO COST, and the real run would not change them.** What Step 9's
> money actually buys is **realistic document prose** — needed for Stage 2/3's memo drafting and judge evaluation,
> and for **nothing in Stage 1's own acceptance criteria.** Stated plainly **before** any spend is authorized.

### ⚑ Three findings surfaced, none absorbed

1. **`seed_demo_cases.py:139` is BROKEN — pre-existing, NOT fixed here.** It calls `RulebookLoader()` with **no
   argument**; `RulebookLoader.__init__(self, rulebook_dir)` **requires** it. **Verified by direct execution**:
   both `RulebookLoader()` and `_SeedSeams()` raise `TypeError`. **No test constructs `_SeedSeams` or imports the
   module** (grep-confirmed), which is why it was never caught. ⚑ **Blast radius**: this is the script **register
   #2's partial discharge depends on** — BUILD-COMPLETION-REPORT **6.1-REVISED** claims *"the API layer is
   exercisable **after running the seed script**"*, and **the seed script crashes on construction**, so that claim
   has evidently never been executed. It also makes **#18's `--real-llm` path unreachable**. **Not fixed**: C7's
   approval covers the **line-97 docstring** only; a behavioural fix to a script two register items depend on is
   its own decision.
2. **The rulebook has ELEVEN rules; PROJECT-BRIEF §3 specifies 25–40.** So **AC-4's "100%" is 100% of the 11 rules
   that exist**, not of the 25–40 the brief scoped. The gate is honest about what it measures; the gap is between
   the rulebook (frozen U3) and the brief, and **predates this pass entirely**. Recorded so the AC-4 claim is never
   read as broader than it is.
3. **One self-introduced test-design defect, found and fixed** — `test_the_offline_double_is_defined_locally` used
   a **naive substring scan** that **false-positived on the module's own docstring** (which legitimately *names*
   `tests/conftest.py` while explaining why it does not import it). Exactly U22's `city`-inside-`ethnicity`
   collision class (llm-judge code-summary §3.4). Rewritten to scan **import statements via `ast`** — the
   assertion was **strengthened, not weakened**.

**HOLDS ALL UPHELD**: `corpus_generator/build.py` **completely untouched** (mtime still Jul 7 — unused,
coverage-omitted, superseded-not-deleted) · `max_calls=20` default in `backend/app/llm_client.py` **unchanged** ·
no frozen-23 unit internal or test edited · U22's `DEFERRED_REGISTER` and its three frozen tests untouched ·
WIRE-1 unamended · `not_wired.py` not renamed · U23's frozen test unedited · **`audit_store` Docker-guard gap
untouched — 5 errors stay exactly 5** · no new route · **Stages 2 and 3 not authorized and not approached** ·
#18's guardrails neither weakened nor bypassed · **C7 not yet applied** (it is Step 12).

**STOPPED at the Step-6 checkpoint** for explicit go-ahead. Steps **7** (dry-run cost confirmation) and **8**
(`models.list`) remain **separate stops**; Step 9's real run needs **both** confirmations.
**Register unchanged at 22 tracked** (17 open · 2 discharged · 3 narrowed).

---

## TIER-B STAGE 1 — CLOSED · #3 NARROWED · #23 OPENED (2026-07-23T06:31:02Z)

**Steps 7, 8 and 9 DELIBERATELY NOT RUN. NO API CALL, NO MONEY SPENT, NO REAL-PROSE CORPUS — in this pass or any
part of tier-B.** Stages 2 and 3 remain **NOT authorized**; Q1–Q12 were **not reopened**.

### The scope reduction, and why

Step 9 (real-prose generation) was authorized and ready, and was **not run** on evidence produced at Step 6:

> **All four blocking gates consume only `record.profile`. NO gate reads `documents_text`.** So the gate results
> are **identical to what a real-prose corpus would give**. The prose has **no consumer** until Stage 2/3 is
> authorized, and would likely need **regenerating against a then-current model** anyway (**#22**'s drift concern
> applied forward). Deferred so **spend and consumption happen together**.

### Delivered

| Artifact | What |
|---|---|
| `backend/scripts/build_corpus.py` | **Guarded** corpus entrypoint — 3 modes (`--dry-run` / offline default / `--real-llm`). Real spend routes **exclusively** through #18's `build_gemini_client`; explicit non-floating `--model-id` and explicit `--max-llm-calls`, both **no default**. **9** tier-U tests. |
| `backend/scripts/run_quality_gates.py` | The **missing production caller** for U13's four gates (a repo-wide scan confirmed there was none). Reads `rulebook_version` **from the manifest** (QG-Fold-2); fail-loud. **6** tier-U tests. |
| `corpus/profiles.json` + `manifest.json` | **300 profiles.** ⚑ **Real, seeded, deterministic, engine-labeled PROFILES with PLACEHOLDER offline PROSE** — `model_version = OFFLINE-DOUBLE-NOT-A-REAL-LLM`. **Never model-authored.** |
| `corpus/gate-reports/` | AC-3 delta **0** · AC-1 **100.0%** · AC-4 **100.0%** (11/11) · coverage-wiring pass. **Decision path only.** |
| `corpus/README.md` | Unambiguous labelling + the evidentiary-vs-unfalsifiability distinction. |
| `seed-script-defect-finding.md` | Separate finding, **reported not fixed**, 4 decision options. |
| C7 | `seed_demo_cases.py:97` docstring **superseded** (kept verbatim, marked superseded). |

### Results

* **Step 6 shape-pilot SUCCEEDED at the designed defaults** — 300 profiles in **2.9s**, band delta **0.00pp** on
  all three classes, all 8 edges. **`tolerance_pp` NOT widened, `attempt_budget` NOT raised.**
* **DET-1 proven at N=300** — **three** independent runs, identical `content_hash 57821891ba502e2e…`. The ±3pp band
  and 8-edge checklist were satisfied **by an actual run for the first time** (previously only by `SkewAudit` unit
  tests over synthetic counts; the N=300 pipeline had **never been run, even offline**).
* **Size 604 KB** — committing unproblematic, **no Git LFS needed**.
* **Final suite: 1571 passed / 0 failed / 43 skipped / 5 errors (same names) / 99.87%** — **EXACT to the advance
  predictions**, unchanged with `corpus/` present and C7 applied. New top-level `corpus/` perturbed **nothing**,
  as the ambiguity-check predicted.

### ⚑ Committing this artifact is EVIDENTIARY, not Q7(a)'s argument

Q7(a) reasoned that a **real-prose** corpus is not bit-regenerable, so an uncommitted one would make downstream
claims unfalsifiable. **That does not apply here and is not claimed**: this corpus **is** deterministically
regenerable. It is committed as the **specific artifact against which AC-1/AC-3/AC-4 were measured**. Q7(a) stands
unchanged for the real-prose corpus it was written about.

### ⛔ Scope limits, so nothing is over-read

* Gate reports verify the **DECISION PATH over real profiles** — **not** document prose, **not** memo quality,
  **not** AC-6.
* **AC-6 remains completely unverified.** **#9** and **#10** untouched, both `discharged=False`. **Q2/Q8/Q9 were
  explicitly deferred, not answered.**
* ⚑ **AC-4's "100%" is 100% of ELEVEN rules.** `PROJECT-BRIEF` §3 specifies **25–40**. The gap is between the
  rulebook (**frozen U3**) and the brief, **predates tier-B**, **out of scope for correction here**.

### Register outcome

**#3 `tier-B corpus run` → NARROWED, not DISCHARGED** — decided on the register's **actual wording**
(*"the **real** 300+ corpus … blocking for real-corpus **quality verification**"*). Two residuals survive: the
**prose is placeholder, not real**, and **AC-6 is unaddressed**.
**#23 `U22-DISCHARGE-UNRECORDABLE-IN-CODE` → NEW** — U22's three frozen tests hard-assert `discharged is False`
with no flip mechanism, so a future #9/#10 discharge is a **matched pair** (#13's shape). Opened per Q11a(c).

**Register now: 23 tracked — 17 open · 2 discharged (#2 partly, #20 fully) · 4 narrowed (#3, #8, #18, #19).**
⚑ Count: #3 was one of the prior 17 open → open 17→16, narrowed 3→4; **#23 is new and open** → open 16→17, tracked
22→23 (17+2+4=23).

### ⚑ Separate finding, reported not fixed

`seed_demo_cases.py:139` calls `RulebookLoader()` with no argument; the constructor requires `rulebook_dir`.
**Confirmed by direct execution** — both it and `_SeedSeams()` raise `TypeError`; no test constructs either.
Bears on **#2's** *"exercisable after running the seed script"* claim (which cannot have been verified by running
it) and **enlarges #18's residual** (the `--real-llm` path is currently **unreachable**, so
`real-llm-verification.md` would fail at step one). **`backend/app/llm_client.py` itself is correct and reachable.**
Write-up: `guide-docs/build/composition-root/seed-script-defect-finding.md`. **Awaiting a decision.**

**Still pending a decision (unchanged):** `GUIDE-DOCS-BUILD-GITIGNORED` (authorization plan §7) — surfaced, not
opened, per instruction that it be decided after Stage 1 closes.

**HOLDS upheld:** `corpus_generator/build.py` untouched (mtime Jul 7) · `max_calls=20` default unchanged ·
no frozen-23 internal or test edited · U22's `DEFERRED_REGISTER` + 3 frozen tests untouched · WIRE-1 unamended ·
`not_wired.py` not renamed · U23's frozen test unedited · `audit_store` Docker-guard gap untouched (**5 stays 5**) ·
no new route · Stages 2/3 not authorized · #18's guardrails neither weakened nor bypassed · seed-script defect
**reported, not fixed**.

---

## SEED-SCRIPT DEFECTS FIXED · TWO CLAIMS CORRECTED (2026-07-23T07:25:19Z)

**5a (claim corrections) + 5b(a) (fix both defects + the tier-U test) — both executed.**

### Two defects, both confirmed by execution, both now fixed

1. **`seed_demo_cases.py:154`** — `RulebookLoader()` called with **no argument**; the constructor takes a
   **required** `rulebook_dir`. `_SeedSeams.__init__` raised **`TypeError` on its first statement**;
   `main()` could not complete under **any** invocation.
2. **The offline double cited `DTI-001` — a rule id that does not exist in this build** (the DTI rule is
   `DTI-CEIL-1`). The condition was **always False**, so it emitted an **empty** `<rule_id>`,
   `CitationValidator` rejected it, the graph retried to the cap and **flagged**. **Every seeded case would
   have landed in `FAILED`, never `drafted`** — and invisibly, since a `failed` case projects to `"pending"`
   (register #14) and `ApplicationSummary` has no status field (register #16).

⚑ **Defect 1 was hiding defect 2.** ⚑ **Shared root cause**: an untested, uncollected, coverage-invisible
module that had **never been run to completion**.

### The fix — and the test IS the fix

`rulebook_dir()` helper + the constructor call corrected; the double now **DISCOVERS** the rule id from the
prompt (`_first_cited_rule_id`) instead of hardcoding one, so it **cannot drift out of step with the rulebook
again**. New `backend/scripts/tests/test_seed_demo_cases.py` — **7 tier-U tests**; the load-bearing one
(`test_drafting_a_demo_case_produces_a_memo_rather_than_blocking`) **fails under EITHER defect**, and
`test_the_demo_path_reaches_drafted_and_r4_reports_ready` drives the real `CasePipeline` over U24's
`InMemoryCaseStore` asserting `DRAFTED` + R4 `"ready"`.

### TIER-U ONLY — stated plainly

**A real Postgres run has NOT confirmed this end-to-end.** No Docker, no live DB here. Per the **#8
precedent** this is an **outstanding residual** — built and tier-U-proven, live confirmation pending — and is
**not** folded into the "fixed" claim.

### Third-defect check — traced, not assumed

Past `DRAFTED`: `case_to_memo_view_state` → **`ready`** · `memo_from_canonical` rehydrates (`REFER`,
`['DTI-CEIL-1']`) · `claim_for_commit` → **WON** → `committing` · **second claim → LOST** (#19's duplicate
guard genuinely working) · `finalize_commit` → **`committed`** · R4 then `pending` (#14's disclosed lossy
projection, not a new defect). **No third logic defect.** The frozen `DecisionCommitService.commit()`
audit-write is **not** exercised — part of the same outstanding residual.

### Third finding — environmental, PRE-EXISTING, reported NOT fixed

On a Windows **cp1252** console the banner `print()`s (lines 326/333, containing an em-dash and a warning
emoji) raise **`UnicodeEncodeError`**. With `PYTHONIOENCODING=utf-8` the script proceeds correctly and fails
only at `get_settings()` for absent DB credentials — **correct fail-closed behaviour**, and proof both real
defects are genuinely fixed. **Authored in #18's pass, not by this fix**; not a logic defect; absent on
Linux/CI/Render. **Out of approved scope — reported, not fixed.**

### Two claims corrected (superseded, never rewritten in place)

1. **§6.1-REVISED's *"the API layer is exercisable after running the seed script"*** → **the demo path is
   proven at tier-U to reach `drafted` with R4 `ready`; end-to-end against a real Postgres is NOT confirmed.**
   The **seven WIRE-1 routes were never in doubt** — only the seeding step.
2. **#18's residual** — *"has not been run"* → ***"is NOT CURRENTLY RUNNABLE"***. **#18 stays NARROWED**;
   only the accuracy of *why* changes. `backend/app/llm_client.py` was never implicated.

Correction sections appended to `BUILD-COMPLETION-REPORT.md` and `scope-b-wiring-summary.md`.

**Verification: 1578 passed / 0 failed / 43 skipped / 5 errors (same names) / 99.87%.** Δ **+7 passed**,
skipped unchanged, **errors exactly 5**, coverage unchanged (`backend/scripts` not a `--cov` target — the
fixed module stays coverage-invisible: test-covered, never counted).

**Register unchanged at 23 tracked** (17 open · 2 discharged · 4 narrowed) — the two defects were never
register items, and #2/#18 keep their statuses; only wording is corrected.

**HOLDS upheld:** no frozen-23 unit internal or test edited (`RulebookLoader` **called correctly, never
modified**) · U22's `DEFERRED_REGISTER` + 3 frozen tests untouched · WIRE-1 unamended · `not_wired.py` not
renamed · U23's frozen test unedited · `audit_store` Docker-guard gap untouched (**5 stays 5**) · no new
route · Stages 2/3 not authorized · #18's guardrails neither weakened nor bypassed · **no API call, no spend**.

**Next: decision 2 — `GUIDE-DOCS-BUILD-GITIGNORED` — to be taken up as its own scoping prompt.**

---

## DECISION 2 CLOSED — #24 `REPO-TRACKING-GAP` OPENED **and** DISCHARGED (2026-07-23T07:55:16Z)

**The repository now contains the BUILD phase for the first time.** Two commits on `main`.

### The item as surfaced UNDERSTATED the problem

Reported as *"`guide-docs/build/` is untracked because of a frontend-intended `build/` rule."* Ground truth found
**only 81 files tracked and `backend/` at ZERO** — the last commit was **`2edaba4`, the DISCOVER close**. **The
entire BUILD phase was uncommitted.** Two distinct problems: **(A)** 650 files never committed (`git add -A`
would have caught them) and **(B)** 311 files **actively ignored** (`git add -A` would have **silently skipped**
them). **(B) was the dangerous half** — a naive fix would have looked complete while omitting the whole design
record. **Second victim, newly found**: `.project-guide-rule-details/build/`, the workflow's **own** BUILD rule
files that `CLAUDE.md` loads, in a directory otherwise **21/27 tracked**. The rule protected nothing — Vite writes
to `dist/`, already covered.

### Ambiguity-check — 3 directed checks, before/after captured, ALL CLEAN

* **(i)** both doc directories **freed**; `frontend/build/assets/app.js` **still ignored** (line 24);
  `frontend/dist/` still ignored (line 18) — exactly the intended discrimination.
* **(ii)** U16's `test_governance.py`, the **only** test reading `.gitignore`: **7/7 pass**.
* **(iii)** ⚑ **the one that mattered** — all ten probed paths (`.env`, `venv/`, `node_modules/`, `__pycache__/`,
  `.coverage`, `.pytest_cache/`, `.hypothesis/`, `backend/.coverage`, `dist/`, `node_modules/`) **stay ignored**.
  **Nothing became stageable as a side effect.**

**Git identity confirmed before staging**: `Nidhi Dhyani <nsdhyani22@gmail.com>`, branch `main`.

### Two commits (Q4-b)

* **`b8d184a`** — `.gitignore` alone: `build/` → **`frontend/build/`** with a comment recording *why*;
  `testresults.txt` ignored (Q5-b) **with an in-file note that this does NOT discharge #12**; plus U16's
  pre-existing `!.env.example` negation.
* **`51935ac`** — **966 files** (961 A / 4 M / 1 D): `backend/` 406 · `guide-docs/` 310 · `frontend/` 228 ·
  `corpus/` 7 · `.project-guide-rule-details/build/` 6 · `deploy/` 3 · `pyproject.toml`, `render.yaml`,
  `.python-version`, `.env.example`. **Pre-commit safety sweep clean** — no `.env`, `*.pem`, `*.key`,
  `node_modules/`, `__pycache__/`, `venv/`, `.coverage` staged.

⚑ **Deliberately NOT a reconstructed per-unit sequence** — synthesising a plausible history would misrepresent
when the work actually happened, against this build's audit-trail discipline.

### Verification — all four RUN, including the load-bearing one

1. ✅ `git check-ignore` → no match. 2. ✅ working tree **clean**; `git ls-files` → **1041** (predicted ≈1040).
3. ✅ ⚑ **THE CLEAN-CHECKOUT TEST RAN AND PASSED** — `git clone` produced `backend/` 406, `guide-docs/build/` 306,
`.project-guide-rule-details/build/` 6, `corpus/` 7, `frontend/` 228, `deploy/` 3; clone tracked count **1041,
exact match**; load-bearing files present; **`.env` and `node_modules/` absent**. No downgrade to
"verified-by-the-other-three" needed. 4. ✅ **Suite unchanged: 1578 / 0 / 43 / 5 / 99.87%.**

### ⚑ What this does NOT do

**It does not discharge register #12.** Ignoring `testresults.txt` stops diff churn; **#12 is about losing
per-unit history**, untouched. **#12 stays OPEN.**

**Register now 24 tracked — 17 open (unchanged) · 3 discharged (#2 partly, #20 fully, #24 fully) · 4 narrowed
(#3, #8, #18, #19).**

**HOLDS upheld:** no frozen-23 unit internal or test edited · U22's `DEFERRED_REGISTER` + 3 frozen tests untouched
· WIRE-1 unamended · `not_wired.py` not renamed · U23's frozen test unedited · `audit_store` Docker-guard gap
untouched (**5 stays 5**) · **tier-B Stages 2 and 3 not authorized** · #18's guardrails untouched · **no API call,
no spend**.

---

## POST-BUILD â€” FRONTENDâ†”BACKEND WIRING: SCOPING PASS **BEGUN** (2026-07-23T12:29:12Z)

**Status**: SCOPING ONLY â€” **no code generated**, plan file written, **STOPPED at the plan-file gate**.
**Plan of record**: `guide-docs/build/plans/frontend-backend-wiring-plan.md` â€” **6 `[Answer]` tags, all BLANK**.

### Ground truth reconstructed fresh from disk â€” three brief premises CORRECTED

1. âš‘ **The four fetch seams are NOT author-only stubs â€” they are COMPLETE.** `memoView/memoFetchSeam.js`,
   `approvalGate/commitFetchSeam.js`, `overrideForm/overrideFetchSeam.js` and `outlierView/fetchSeam.js` are
   fully-implemented `create<X>Fetch(transport)` factories over an **injected** transport, each already
   normalizing failures to the WIRE-1 Â§4 envelope. **The real transport exists too** â€”
   `frontend/src/app/httpTransport.js` (a genuine `fetch()` with `X-User-Id`), composed by
   `frontend/src/main.jsx` at `baseUrl: '/api'`. **The seams need ZERO change**; `App.jsx`'s own header
   comment claiming "no `main.jsx`/`index.html`" is **stale** â€” both exist (U23 authored them).
2. âš‘ **Frontend identity is NOT unbuilt** â€” `VITE_USER_ID` â†’ `X-User-Id` â†’ `current_identity` â†’ `app_user`,
   fail-closing to 401; `sessionClient.js` reads R1 and fail-closes to a `null` role. A **login UI** is absent;
   an identity **concept** is not.
3. âš‘ **The claimed live-Postgres end-to-end verification is ABSENT from the record**, and the record says the
   opposite ("TIER-U ONLYâ€¦ a real Postgres run has NOT confirmed this end-to-end"). The #19 duplicate-guard
   observation was a **traced simulation over `InMemoryCaseStore`**, and **#19 remains an OPEN defect**, not a
   working guard. Not treated as established.

### Confirmed as briefed
`package.json` scripts = `build`/`test`/`test:cov`/`lint` â€” **no `dev`** Â· `vite.config.js` has **no `server` key** Â·
**no CORS middleware anywhere in `backend/`** (`add_middleware`: zero hits) Â· **git clean** at `cb06057` on `main` Â·
**frontend suite re-run LIVE: 682 passed / 137 files / 0 failed**.

### Four findings the brief did not anticipate
* **(a)** The `dev` script is **safe**: U23's frozen `test_frontend_package_json_change_is_additive_only` is a
  **presence** check, not exact-set equality over `scripts`.
* **(b)** âš‘ **The blocker is the composition root, not the seams.** `App.jsx` mounts only `HistoryView`, and
  `app.test.jsx` **asserts** the four other views are unmounted and that `seams` has **exactly five keys**.
  Mounting a view, or adding the outlier seam, **fails existing green tests** â€” a direct collision with the
  "preserve the frontend suite" hold. Surfaced as **Q5**, not resolved unilaterally.
* **(c)** The **outlier seam is absent from `seams.js` entirely** â€” a strictly larger delta than the other three.
* **(d)** U23's own `is_under_frozen` classifier returns **True** for `backend/app/main.py` and
  `frontend/src/app/App.jsx`, **False** for `vite.config.js` / `main.jsx`; and
  `deploy-config/infrastructure-design/deployment-architecture.md` Â§3 already records that adding backend CORS
  "would edit the CLOSED composition root (BR-DEP-1 violation)". The **dev tier was designed, never realized**.

**HOLDS upheld**: no frozen-23 unit internal edited Â· no seam edited Â· WIRE-1 unamended Â· `backend/app/routes/`
untouched, no route added Â· `audit_store` Docker-guard gap untouched Â· **tier-B not authorized, not touched** Â·
`backend/app/llm_client.py` and `backend/scripts/` untouched (#18's spend guardrails unaffected) Â· frontend suite
left green.

**Register unchanged at 24 tracked** â€” 17 open / 3 discharged (#2 partly, #20, #24) / 4 narrowed (#3, #8, #18, #19).

---

## POST-BUILD â€” FRONTENDâ†”BACKEND WIRING: Q1â€“Q6 ANSWERED Â· AMBIGUITY-CHECK CLEAN Â· CODE-GEN PLAN WRITTEN (2026-07-23T12:45:51Z)

**Status**: **STILL PLAN-ONLY â€” no code generated.** Stopped at the code-gen plan-file gate.

**Answers (embedded verbatim, 6/6, 0 blank)**: **Q1(a)** add `"dev": "vite"` now Â· **Q2(a)** Vite `server.proxy`, explicitly **not** CORSMiddleware Â· **Q3(a)** existing `VITE_USER_ID` via `.env.local`, build nothing Â· **Q4(a)** no seam-layer change, outlier stays unregistered Â· **Q5(c)** queue â†’ memo â†’ commit, **#19 exposure accepted knowingly** Â· **Q6(a)** supersede-not-rewrite the Scope-A assertion, add tests via injected `fetchImpl`.

### âš‘ Retroactive audit entry appended (before the ambiguity-check, as instructed)

A previously-unlogged **manual, out-of-band R1â€“R7 walkthrough against a real local Postgres**, performed by the user via `curl`, incl. a second commit attempt returning **409** rather than duplicating an `AuditRecord`. Logged as **reconstruction, not backdating** â€” written now, timestamped now, appended in position; event time given as an approximate range with the lower bound (`07:25:19Z`, the seed-script two-defect fix) **disclosed as an inference**. Epistemic status explicit: **the user's attestation, not independently verified by me, not re-creatable from the repo**. The earlier good-faith *"a real Postgres run has NOT confirmed this end-to-end"* record is **left standing unedited** and superseded going forward.
**âš‘ #19 is UNCHANGED (NARROWED, open).** The entry does not alter its status, and no view is offered on whether it should.

### Ambiguity-check â€” CLEAN, 10 folds, 7 directed checks run

* **Answer-set consistency first**: Q4(a) and Q5(c) **do not conflict** â€” queue/memo/commit seams are *already* registered, so mounting needs no seams change. âœ…
* **âš‘ Check 2 (the flagged highest risk) â€” CONFIRMED REAL.** Backend routes carry **no `/api` prefix**; without a rewrite **all seven 404**. Pinned: `rewrite: (p) => p.replace(/^\/api/, '')`, target **`127.0.0.1`** not `localhost` (Node IPv6-first vs uvicorn IPv4 on Windows), plus a mandatory post-wiring `curl` proof since the rewrite is invisible in the browser.
* **Check 4 â€” `.env.local` ignored, verified BY EXECUTION**: `git check-ignore -v` â†’ `.gitignore:4:.env.*`, exit 0. No disclosure risk.
* **Check 1 â€” baseline**: U23's `test_noedit.py` + `test_build.py` â†’ **11 passed**; the `scripts` assertion is presence-only.
* **âš‘ Check 5 â€” delta predicted test-by-test; blast radius is ONE test, not four.** Only `mounts NO unbacked surface` fails. **`wires all five units seams` stays green untouched** *because* Q4(a) declined the seams change. Plus one **mechanical** await fix (fold 10). Final: **2 existing touched, 1 semantically, 0 deleted.**
* **Checks 3 / 6 / 7**: N/A (no middleware) Â· backend suite **not** re-run, carried at 1578/0/43/5/99.87% Â· discharged by the retroactive entry.

**Four genuine finds**: the `approval-gate` vs `approval-gate-view` **testid mismatch that would have let a test pass by accident** (refused, same as the interop replica and the heuristic fake) Â· the **duplicate R4 fetch** from mounting memo + gate together (disclosed on the **#15** precedent, not optimized) Â· a **coverage-branch risk** (both selection arms must be exercised) Â· the **`src/app` advisory-vocabulary lint**, designed around by having `App.jsx` introduce **no new display copy at all**.

**Plan of record**: `guide-docs/build/plans/frontend-backend-wiring-code-gen-plan.md` â€” 5-item inventory (dev script Â· proxy Â· `.env.local` + `app_user` row Â· `App.jsx` mounting with selection state Â· test updates), 8-step leaf-first TDD order (RED before GREEN), **explicit BEFORE/AFTER for both touched tests**, and a closing section separating what this delivers (a real, clickable **queue â†’ memo â†’ commit** path against a live backend â€” the first time the human-in-the-loop gate is demonstrable by clicking rather than asserted by a unit test) from what it does not (override Â· outlier Â· any login UI Â· any production change Â· **no register item resolved, including #14/#16/#17/#19/#13/#2**).

**HOLDS upheld**: no frozen-23 unit internal edited Â· no seam edited Â· WIRE-1 unamended Â· `backend/app/routes/` **read-only**, no route added, **no backend file written at all** Â· `audit_store` Docker-guard gap untouched (5 stays 5) Â· **tier-B not authorized, not touched** Â· `backend/app/llm_client.py` and `backend/scripts/` untouched (#18 unaffected) Â· **no code generated**.

**Register unchanged at 24 tracked** â€” 17 open / 3 discharged / 4 narrowed. Frontend suite still **682 / 137 / 0**.


---

## POST-BUILD - FRONTEND<->BACKEND WIRING: CODE-GEN PLAN APPROVED, IMPLEMENTATION EXECUTED, SUITE GREEN 687/137/0 (2026-07-25T09:29:36Z)

**Status**: IMPLEMENTED - code generated, suite green, NOT committed. Stopped at the 2-option completion gate.
**Plan of record executed**: `guide-docs/build/plans/frontend-backend-wiring-code-gen-plan.md` (Q1a/Q2a/Q3a/Q4a/Q5c/Q6a), in its 8-step leaf-first TDD order (RED before GREEN).

### What was built (Items 1-5), each gate met

* **Item 1** - `frontend/package.json`: `"dev": "vite"`. U23 test_noedit/test_build -> 11 passed; `npm test` 682 unchanged.
* **Item 2** - `frontend/vite.config.js`: dev-only `server.proxy` `/api` -> `127.0.0.1:8000` with `rewrite` stripping `/api`. Strip PROVEN live through the dev server via a path-echo stub (`/api/session` -> received `/session`, 200, query preserved; control unstripped) - directed check 2 / stop-gate #4 discharged. DB-backed 200 remains the manual Step-7 step (no live Postgres here). `npm test` 682 unchanged.
* **Item 3** - `frontend/.env.local` (gitignored, verified; `VITE_USER_ID=demo-underwriter` placeholder + required app_user underwriter-row documented). No code; no test impact.
* **Item 4** - `frontend/src/app/App.jsx`: `selectedId` state; QueueView always mounted; on selection MemoView + ApprovalGateView (explicit `approval-gate` testid); HistoryView unchanged; Fold-4 disclosed; no new copy. No seams.js/main.jsx change (Q4a).
* **Item 5** - `frontend/src/app/__tests__/app.test.jsx`: separate `backedServer()` helper (fakeServer byte-unchanged); test 6 rewritten (semantic, asserts real `approval-gate` testid); test 4 await strengthened (mechanical); 5 new tests.

### Verification

* **RED** (before Item 4): 7 failed / 8 passed, every failure element-not-found (predicted reason only).
* **Full suite**: 687 / 137 / 0 (682 + 5 new). Delta by name: 2 existing touched (1 semantic `mounts NO unbacked surface` -> `mounts exactly the backed surfaces...`; 1 mechanical await on `renders identically for every role`), 5 added, 0 deleted. Test 8 `wires all five units seams` stayed green untouched - as predicted.
* **Coverage**: App.jsx 100/100/100/100; thresholds 90/90/90/90 unchanged; EXIT 0.
* **Step 7** manual browser confirmation: NOT done (needs live Postgres) - the one manual, non-re-creatable step.

**HOLDS upheld**: no frozen-23 unit internal edited; no seams.js/main.jsx/WIRE-1/backend/** touched (confirmed via `git diff --name-only`); backend/app/routes/, llm_client.py, scripts/ untouched; tier-B not authorized/touched; no API call, no spend; backend suite not re-run (carried 1578/0/43/5/99.87%). NO COMMIT.

**Register UNCHANGED at 24 tracked** - 17 open / 3 discharged / 4 narrowed. **#19 UNCHANGED** - a clickable double-commit is now reachable under Q5(c), accepted knowingly; this pass does not alter its status.

**Changed files (uncommitted)**: frontend/package.json, frontend/vite.config.js, frontend/src/app/App.jsx, frontend/src/app/__tests__/app.test.jsx, frontend/.env.local (gitignored) - plus this guide-state.md and one audit.md entry.

---

## POST-BUILD — LOGIN & SIGNUP: SCOPING PASS **BEGUN** · ⚑ REGISTER #25 OPENED (2026-07-25T10:42:13Z)

**Status**: SCOPING ONLY — **no code generated, no frozen file touched, WIRE-1 not amended, no frozen test relaxed**.
Plan written, **STOPPED at the plan-file gate**.
**Plan of record**: `guide-docs/build/plans/login-signup-plan.md` — **8 `[Answer]` tags, all BLANK**.

### Ground truth reconstructed fresh from disk

**What identity/auth IS today** (four links, all real, all read-only): `frontend/.env.local` → `VITE_USER_ID`
(`main.jsx:23`, a **build-time** env var) → `X-User-Id` header (`httpTransport.js:42`) → `current_identity()`
(`dependencies.py:160-175`) → `SELECT role FROM app_user` on the owner engine → `to_role()` fail-close → **401**
or `Identity`. R1 `GET /session` echoes `{user_id, role}`; the client fail-closes to `null`; the role is
**cosmetic only** (`RoleGate.jsx`).

**What it is NOT — repo-wide scan, verified not assumed**: **no password authentication of any kind** (`app_user`
has exactly three columns — `user_id`, `subject`, `role`; the only `PASSWORD` literals in `backend/` are Postgres
**role** passwords and test fixtures) · **no JWT** · **no session token, cookie, or `Authorization` header**
(`dependencies.py:31-34`: *"deliberately NOT `Authorization: Bearer`, which would imply a token semantic … that
does not exist"*) · **no session state** — R1 issues and stores nothing · **no middleware** (`add_middleware`
zero hits) · **no signup/registration/logout route** · **no login UI**.

⚑ **The identity is trusted from the client entirely.** The ROLE is never trusted (`dependencies.py:168`), but
`X-User-Id: <any known user_id>` **is** authentication — there is no verification step to bypass.

### ⚑ REGISTER #25 `PER-4-AUTHN-UNIMPLEMENTED` — OPENED, NOT RESOLVED

**Login was scoped IN and silently dropped.** Requirements Q6 **rejected A (no real auth)** and **rejected C
(full SSO)**, answering **B — basic login (JWT/session)** → **PER-4** (`requirements.md:78`), phase-tagged
**Phase 1** via **US-PLAT-1**, and carried into `personas.md:21` and `user-journey.md:46` (*"1. Login with
JWT/session; RBAC routes the user by role (PER-4)"*). Only the **federated** half was deferred — **OOS-3**
(`requirements.md:62`).

⚑ **`auth-rbac`'s BR-AUTH-10 defers the authentication flow on the justification *"authn is out of Phase-1
scope"* — which the requirements record does not support.** Between Requirements Analysis and the auth-rbac FD,
*"authn deferred"* widened from *"federated SSO deferred"* to *"all authentication deferred"*, and **no artifact
surfaces, questions, or approves that widening**. Every downstream artifact inherits it in good faith
(`unit-of-work.md:182` → `domain-entities.md:150-151` → WIRE-1 A6/§6:137 → the `X-User-Id` stub).
**Consequence: US-PLAT-1's Gherkin `Given` is unsatisfied while its `Then` clauses are built and tested.**

**Severity**: **non-blocking today** (the stub works, the demo runs, all suites green); **⛔ blocking for any
multi-user or publicly-reachable deployment**. It **materially qualifies two headline claims** — **SEC-4's
segregation of duties is not adversarially enforceable**, and **`AuditRecord.underwriter_id`, the CON-BR4 "WHO",
is an unauthenticated self-asserted string** in a build whose stated invariant is full auditability.

**`auth-rbac` (U11) is NOT defective** — its authz model is correct, single-sourced, enforced at both points and
tested. #25 is the **authentication** half no unit ever owned. **No prior pass is at fault**: each disclosed the
stub accurately as a stub.

⚑ **A new outcome shape**: every prior item recorded a **disclosed deferral** (#2–#24) or an **unwritten
rationale** (#20). **#25 is the first where the requirements record and the shipped behaviour disagree, and the
disagreement was never disclosed at all.**

### ⛔ Structural blocker recorded — four frozen assertions across TWO units

`deploy_config/tests/test_routes.py:36` (**exact-set equality** over the seven WIRE-1 routes; *"LOAD-BEARING —
full-highest"*; ⚑ **app-level introspection — binds wherever the router file lives**) · `:41` (exact filename set
under `backend/app/routes/`) · `app/tests/test_no_write_route.py:107` (**exactly one non-GET route**) · `:239`
(no direct writes under `backend/app/` — a signup INSERT would break the composition root's stated *"every write
goes through the frozen `DecisionCommitService`"* guarantee, `dependencies.py:15-20`). **Same MATCHED-PAIR shape
as #13, but four assertions across two units instead of one.**

### Three bounding constraints named (not acted on)

**C-A** `0001_initial_schema.sql` frozen — credential state, if any, is a **new forward-only migration**, never an
edit · **C-B** `Settings` has **exactly six** required fields; a signing key would be a **seventh**, editing
frozen U16 · **C-C** `Role`/`PERMISSION_MATRIX` are **closed** while `app_user.role` is an open `VARCHAR` — any
signup must assign one of exactly three values or the user cannot authenticate.

### Also surfaced — the Security Guardrails scope

`Enabled (scoped)` (guide-state §Extension Configuration), and the recorded scope **excludes `SECURITY-12:
Authentication and Credential Management`** — fixed at Requirements Analysis under the **same** unsupported
assumption. Widening it would make **MFA for administrative accounts a blocking requirement** per CLAUDE.md.
Surfaced as plan **Q4.2**, not decided.

### Eight open questions (all BLANK)

**Q1** PER-4 discharge vs new feature · **Q2** new domain state / whose / frozen-unit reopening · **Q3** signup =
admin-provisioning vs self-registration (⚑ self-service role assignment over a closed role set is **not**
defensible for BFSI — it would let anyone grant themselves `RBAC_COMMIT`) · **Q4** password storage/hashing **+
the SECURITY-12 scope decision** · **Q5** session mechanism (stateless vs revocable) · **Q6** does WIRE-1 R1
change shape, or does login sit in front of it · **Q7** new route (WIRE-1 §3 amendment) vs layered — **including
the reverse-proxy/platform-gate alternative, presented fairly with its bypass weakness stated** · **Q8** should
relaxing the four frozen assertions be its **OWN separately authorized reopening** (U24 three-reopenings
precedent) rather than bundled.

**HOLDS upheld**: no frozen-23-or-24 unit internal or test edited · **BR-AUTH-10 cited, not edited** · WIRE-1
unamended · `backend/app/routes/` untouched, no route added · **no backend or frontend file written at all** ·
U15's migrations and U16's `Settings` untouched · `not_wired.py` not renamed · U23's frozen test unedited ·
`audit_store` Docker-guard gap untouched (5 stays 5) · tier-B not authorized, not touched ·
`backend/app/llm_client.py` and `backend/scripts/` untouched (#18 unaffected) · **no code generated** · **#25
opened, NOT resolved**.

**Register now 25 tracked** — **18 open** (was 17) / 3 discharged (#2 partly, #20, #24) / 4 narrowed (#3, #8,
#18, #19). Suites carried forward, not re-run: backend **1578 / 0 / 43 / 5 / 99.87%**; frontend **687 / 137 / 0**.

---

## POST-BUILD — LOGIN & SIGNUP: Q1–Q8 ANSWERED · AMBIGUITY-CHECK ⚠️ **NOT CLEAN** · SURFACE-AND-STOP AT Q9–Q11 (2026-07-25T10:42:13Z)

**Status**: **STILL PLAN-ONLY — no code, no schema, no route, no WIRE-1 amendment, no frozen test relaxed.**
⚑ **The standalone frozen-assertion relaxation design was NOT written** — two of the three findings determine its
scope and one changes a disclosure obligation. Writing it now would produce a plan wrong on arrival.

**Answers embedded verbatim (8/8, 0 blank)** in `login-signup-plan.md` §4, with the pre-answer question text
preserved **byte-for-byte**: **Q1(c)** login = #25 discharge / signup = thin layer on the built admin-CLI path ·
**Q2(a)** new `user_credential` table via a new forward-only `database`-owned migration · **Q3(a)**
admin-provisioning only, (d) self-selected roles recorded as considered-and-rejected · **Q4** 4.1(a) Argon2id +
4.2(ii) keep the extension scope, omit MFA and breached-password checking, **narrowing disclosed by name** ·
**Q5(b)** opaque server-side session in a `user_session` table, HttpOnly/Secure/SameSite=Lax cookie · **Q6(a)**
R1's shape unchanged — the reserved seam used as designed · **Q7(a)** new `POST /login` + `POST /logout`, WIRE-1
§3 amended additively · **Q8(c)** relaxation designed+approved standalone, applied as step 0 of the code-gen pass.

### ⚠️ Ambiguity-check — 4 directed checks run against disk · **3 MATERIAL FINDINGS · 4 folds**

* **⚠️ Check (i) — MATERIAL.** The real question is **whose migration sequence owns the tables**. **U15 carries
  THREE exact-set assertions over its migration filenames + a two-entry checksum manifest** —
  `test_migration_apply.py:56`, `test_migration_checksum.py:114`, `test_migration_runner.py:75`,
  `migrations/checksums.json` — and `migration_runner.py:69` discovers **by glob**, so a new `0003_*.sql` is
  auto-discovered and **all three fail**. The U24-precedent alternative (own dir + own manifest + collision
  guard) fires **zero** — but `backend/scripts/run_migrations.py:57-58` **hardcodes exactly two sequences**
  (*"Hardcoded, explicitly named … no dynamic discovery"*) and is **off-limits this pass**, so a third sequence
  would **silently never run at deploy** — register **#8**'s exact, freshly-remediated failure mode. **Neither
  option is free.**
* **✅ Check (ii) — CLEAN (2 folds).** **C-B genuinely avoided** — an opaque token is validated by **lookup, not
  signature**, so `Settings` stays at exactly six fields. **LOGIN-Fold-1**: `test_governance.py:92-94` asserts
  `.env.example` keys **equal** `Settings.model_fields`; any new field is a two-file paired edit across a frozen
  unit — none added, stays green. **LOGIN-Fold-2**: the `Secure`-cookie-over-local-HTTP problem resolves on the
  `llm_client.py:106-120` precedent — SEC-3's `os.environ` rejection is *"scoped to credentials and secret
  material specifically"*; a behavioural toggle is not a credential.
* **⚠️ Check (iii) — MATERIAL (2 folds).** No-CORS property **holds, better than expected** — **LOGIN-Fold-3**:
  `fetch` defaults to `credentials: 'same-origin'` and the topology already is, so cookies flow **automatically**
  and frozen-classified `httpTransport.js` **is not touched at all**. **LOGIN-Fold-4**: editing `App.jsx` is
  **not** blocked (`test_noedit.py` constrains only U23's **own** artifacts — proven by the wiring pass, 11
  passed). **⛔ But `app.test.jsx:261` asserts exact-set equality over seam keys** — a sixth seam breaks it;
  resolvable via `sessionClient.js`'s non-seam precedent, recorded as a **BINDING CONSTRAINT**.
  ⚑ **CONSEQUENCE — §2's blocker figure is UNDERSTATED: "4 assertions across 2 units" is actually 7 across 3**
  (A-1…A-4 + the three U15 assertions). **Q8 was answered explicitly against "the four frozen-assertion
  blocker."** Silently widening 4→7 / 2→3 would be the exact unsurfaced scope-widening **register #25 exists to
  record** — not defensible inside the pass that opened #25.
* **⚠️ Check (iv) — MATERIAL.** Q4.2 names **one** disclosure location; the scope is recorded in **FIVE**:
  `guide-state.md:28-30` · `requirements.md:212-214` (§10) · `requirements.md:261` (§13) ·
  `execution-plan.md:295` (§8) · `requirement-verification-questions.md:152-153` (Q13). **The #20
  directed-check-(ii) precedent exactly.** Four are **approved DISCOVER artifacts**, so disclosing across them
  **exceeds what Q4.2 authorized**.

### Surfaced — Q9 / Q10 / Q11, all BLANK

**Q9** which sequence owns `user_credential`/`user_session` (rec **(a)** — (a) fails **loudly in CI**, (b) fails
**silently in production**) · **Q10** does the relaxation pass widen to 7 across 3 (rec **(c)→(a)** — Q9 and Q10
are one decision viewed twice; **§2 and #25 must be corrected by supersession either way**) · **Q11** where the
SECURITY-12 narrowing is disclosed (rec **(c)** — close the contradiction at `requirements.md` §10 without editing
four approved artifacts for a narrowing not yet implemented; the omitted clauses **MFA** and **breached-password
checking** named explicitly, since an unnamed narrowing is the #25 failure mode).

**HOLDS upheld**: no frozen-23-or-24 unit internal or test edited · `backend/app/routes/`, `backend/app/llm_client.py`,
`backend/scripts/`, tier-B **read-only, untouched** · **no backend or frontend file written at all** · WIRE-1
unamended · **no frozen test relaxed** · U15's migrations + checksum manifest and U16's six-field `Settings`
untouched · `not_wired.py` not renamed · `audit_store` Docker-guard gap untouched (5 stays 5) · **no code
generated** · **#25 still OPEN, unresolved** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Suites carried forward, not re-run:
backend **1578 / 0 / 43 / 5 / 99.87%**; frontend **687 / 137 / 0**.

---

## POST-BUILD — LOGIN & SIGNUP: Q9–Q11 ANSWERED · AMBIGUITY-CHECK RE-RUN ⚠️ **STILL NOT CLEAN** · SURFACE-AND-STOP AT Q12–Q13 (2026-07-25T10:42:13Z)

**Status**: **STILL PLAN-ONLY.** ⚑ **The standalone frozen-assertion relaxation design was NOT written** — Q12
fixes its membership and Q13 fixes whether it spans three units or four.

**Answers embedded verbatim (11/11 filled, 2 blank added)**: **Q9(a)** U15 owns `0003_auth.sql` in its existing
forward-only sequence with its own checksum-manifest entry — chosen because it **fails loudly in CI** rather than
(b)'s **silent deploy-time** failure via `run_migrations.py`'s hardcoded two-sequence list (register #8's
freshly-remediated failure mode) · **Q10(a)** widen the relaxation pass, **correct §2/§8 and #25 by
supersession**, cite exact assertions · **Q11(c)** disclose the SECURITY-12 narrowing at `requirements.md` §10
only, **naming MFA and breached-password-list checking** explicitly.

### ⚑ THE FINDING — my own §8 enumeration was wrong; found by re-verifying it, not trusting it

The Q10 answer ratified *"seven across three"* with a specific membership. **The count was close; the MEMBERSHIP
was wrong.** Re-read of `backend/app/tests/test_no_write_route.py:105-131`: the composition root holds **THREE**
route-surface assertions, not one — `:107` (exactly-one-non-GET) · **`:116`** (`test_every_other_route_is_read_only`,
which fails **twice**, for `/login` and `/logout`) · **`:122`** (`test_the_seven_wire1_routes_are_the_whole_surface`,
exact path set). And **A-4 `:239` PASSES** provided the stores live **outside** `backend/app/`.

**CORRECTED LEDGER — 8 assertions across 3 units**: U23 **2** (`test_routes.py:36`, `:41`) · composition root
**3** (`:107`, `:116`, `:122`) · U15 **3** (`test_migration_runner.py:75`, `test_migration_checksum.py:114`,
`test_migration_apply.py:56`) **+** the `checksums.json` manifest entry. **Net: +`:116`, +`:122`, −A-4;
7 → 8; units unchanged at 3.**

⚑ **TWO items want a BINDING DESIGN CONSTRAINT, not a relaxation — strictly better, the invariant survives
intact**: **A-4** keeps asserting *"every write goes through the frozen `DecisionCommitService`"* iff the
credential/session stores are authored **outside** `backend/app/` (the U24 `PostgresCaseStore` pattern, already
the build's shape) · **`app.test.jsx:261`** keeps its exact seam-key set iff the login client follows
`sessionClient.js`'s **non-seam** precedent.

### ✅ Confirmed CLEAN

* **Q9(a) mechanics — and better than expected.** No collision with U24's guard (`migrate.py:60-68`, live
  filename intersection = ∅). **Ordering is favourable**: `0003_auth.sql` applies **after** `0002_grants.sql`, so
  the new tables are created after the audit roles exist and receive **no grant** — **owner-only by
  construction**, exactly CORE-RATIONALE-20's posture for `app_user`. Glob auto-discovery
  (`migration_runner.py:69`) confirmed ⇒ **no `backend/scripts/` edit**, Q9(a)'s whole point.
* **Q11(c) is test-neutral.** Repo-wide scan: **no test under `backend/` reads `requirements.md` or
  `execution-plan.md`.**

### ⚑ Disclosed evidentiary limit (#8 precedent)

`test_migration_apply.py:56` sits inside `test_migration_sequence_is_forward_only_and_idempotent`, which takes
`migrated_engine`; `conftest.py:41-42` **skips when Docker is absent**. It **skips here and fails only in CI**.
The other two U15 assertions are pure file reads and **do** run locally. The relaxation pass must state the third
is **CI-only** and never claim local green as proof.

### Surfaced — Q12 / Q13, both BLANK

**Q12** ratify the corrected membership + A-4's disposition (rec **(a)**: **8-across-3 with A-4 PRESERVED** via
the store-outside-`backend/app/` constraint — keeping it costs nothing and leaves the composition root's write
guarantee fully intact) · **Q13** `app.test.jsx:261` (rec **(a)**: preserve via the `sessionClient.js` non-seam
precedent, keeping the pass at **three units, not four**). ⚑ Governing principle for both: **relax only what
growth genuinely requires; preserve by design whatever can be preserved.**

⚑ **Q1–Q11 remain answered and stand unchanged** — nothing here revisits a settled decision; this is a correction
to *my own* enumeration, surfaced rather than absorbed, exactly as Q10 required.

**HOLDS upheld**: no frozen-23-or-24 unit internal or test edited · `backend/app/routes/`, `llm_client.py`,
`backend/scripts/`, tier-B **read-only** · **no backend or frontend file written at all** · WIRE-1 unamended ·
**no frozen test relaxed** · U15's migrations + `checksums.json` and U16's six-field `Settings` untouched ·
`audit_store` gap untouched (5 stays 5) · **no code generated** · **#25 still OPEN** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Suites carried forward, not re-run:
backend **1578 / 0 / 43 / 5 / 99.87%**; frontend **687 / 137 / 0**.

---

## POST-BUILD — LOGIN & SIGNUP: Q12–Q13 ANSWERED · FINAL AMBIGUITY-CHECK ✅ **CLEAN** · #25 BLOCKER SUPERSEDED 4→8 · **RELAXATION DESIGN WRITTEN** (2026-07-25T10:42:13Z)

**Status**: **STILL PLAN-ONLY — no test edited, no assertion relaxed, no route, no migration, no code.**
Stopped at the **new** plan's gate. **The login/signup code-gen plan was NOT begun.**
**Plans of record**: `login-signup-plan.md` (**13/13 answered**) · **NEW**
`guide-docs/build/plans/frozen-assertion-relaxation-plan.md` (**3 `[Answer]` tags, all BLANK**).

### ⚑ Method changed deliberately — a sweep, not another recount

The two prior rounds under-counted because each re-checked the assertions already in hand. This round enumerated
**every exact-set / exact-count assertion in the repository perturbable by the three implied changes — +2 routes,
+1 migration file, +2 tables** — and classified each as *breaks* or *survives* **with a reason**.
**The ratified 8-across-3 is CONFIRMED CORRECT.**

**The 8 that break (3 units)**: R-1 `test_routes.py:36` · R-2 `:41` · R-3 `test_no_write_route.py:107` · R-4
`:116` · R-5 `:122` · R-6 `test_migration_runner.py:75` · R-7 `test_migration_checksum.py:114` · R-8
`test_migration_apply.py:56` (**Docker-gated → CI-ONLY here**) + the `checksums.json` entry.

**The 2 PRESERVED by construction**: **A-4** (`:239`+`:258`) via stores authored **outside `backend/app/`** ·
**`app.test.jsx:261`** via `sessionClient.js`'s non-seam precedent. ⚑ Q12(a)'s constraint **independently
verified mechanically safe**: `test_frozen_untouched.py`'s `PRODUCTION_FILES` is `APP_ROOT.rglob` — **scoped to
`backend/app` only** — so `owned == {"app"}` is unaffected, and a new package is not in the hardcoded
`FROZEN_UNITS` set.

**TEN near-misses swept and confirmed SURVIVING**, reasons recorded so no future pass re-derives them — incl.
`test_apply_from_empty_created_the_three_tables:37` (**`<=` subset, not `==`**), `test_rulebook_registry_table_is_absent:89`
(*"NOT a closed-world check"*), U23's other **11** test files (offender-list/subset form), the advisory-vocabulary
lint (verdict tokens only), U24's collision guard (∅), the `.env.example`↔`Settings` drift guard, and the
confirmation that **no test reads `requirements.md`/`execution-plan.md`** (Q11(c) test-neutral).

### Supersessions recorded — never rewrites

`login-signup-plan.md` **§12** supersedes its own **§2** and **§8 Q10** framing; `BUILD-COMPLETION-REPORT.md`
gains a **register-correction** section superseding **#25's structural-blocker row**. Prior text preserved
verbatim in every case. ⚑ **#25's STATUS IS UNCHANGED — still OPEN**; only the blocker's *measurement* is
corrected. **Register count unchanged at 25 (18 open / 3 discharged / 4 narrowed)** — a measurement corrected
inside an open item opens and closes nothing.

### ⚑ Disclosed process finding (#20 / #19 precedent)

**The plan's own §2 under-counted twice** — 4, then 7-with-wrong-membership — and **both were caught by the
mandatory ambiguity-check, not by the ground-truth passes that produced them.** The U15 half was a legitimate
consequence of a later decision (Q9(a)); **the composition-root half was a genuine error** (`:116`/`:122` sat in
a file already read). Lesson recorded verbatim: ***"a ground-truth pass that enumerates what it already knows
about is not a sweep."***

### The relaxation design — `frozen-assertion-relaxation-plan.md`

**Governing principle**: **the guards' strength is EXACT-SET EQUALITY, not the literal being inline.** Each
literal moves into **one declared, per-entry-justified inventory**; **every comparison stays at exact equality**.
Growth still fails until the inventory is updated, and updating it is a **greppable one-line diff** — so **growth
becomes reviewable rather than either forbidden or silent**.

⚑ **R-3 is the substantive one.** The naive widening to `[commit, login, logout]` would keep equality while
**destroying the invariant's meaning**, silently converting a **domain-write** guarantee into a **verb-count**
allowlist. It is therefore **SPLIT**: (a) a declared non-GET allowlist + (b) a **newly separable, structurally
asserted** invariant — **exactly one non-GET route reaches domain state** (login/logout must reference no
`DecisionCommitService` / `CasePipeline` / case store / audit repo / claim method). **That half is STRONGER than
what it replaces.** **R-5** also gains strength by sharing one inventory with **R-1**, closing a **pre-existing**
two-independent-literals drift risk. **R-8 is disclosed CI-only — local green is explicitly NOT proof (#8
precedent).**

**Three blank questions**: **Q1** inventory location (rec **(c)**; ⚑ **(b) ELIMINATED BY EVIDENCE** — it breaks
`test_routes.py:55`, making it a ninth assertion) · **Q2** rename the three now-misdescribing test names (rec
**(a)** — option (b) knowingly mints three new instances of **register #13's exact defect**) · **Q3** structural
vs conventional enforcement of R-3's split (rec **(a)**; ⚑ **if (b), the "STRONGER" claim must be STRUCK**).

**HOLDS upheld**: **all eight assertions untouched on disk** · no frozen-23-or-24 unit internal or test edited ·
`backend/app/routes/`, `llm_client.py`, `backend/scripts/`, tier-B **read-only** · **no backend or frontend file
written at all** · WIRE-1 unamended · U15's migrations + `checksums.json` and U16's six-field `Settings`
untouched · `not_wired.py` not renamed (**#13 open**) · `audit_store` gap untouched (5 stays 5) · tier-B not
authorized · **no code generated** · **#25 still OPEN** · **NO COMMIT**.

Suites carried forward, not re-run: backend **1578 / 0 / 43 / 5 / 99.87%**; frontend **687 / 137 / 0**.

---

## POST-BUILD — FROZEN-ASSERTION RELAXATION: Q1–Q3 ANSWERED · AMBIGUITY-CHECK ✅ **CLEAN** · **CODE-GEN PLAN WRITTEN** (2026-07-25T10:42:13Z)

**Status**: **PLAN ONLY — nothing executed. No test edited, no assertion relaxed, no route, no migration, no
code.** Stopped at the **code-gen** plan-file gate. **The login/signup code-gen plan was NOT begun.**
**Plans of record**: `login-signup-plan.md` (13/13 answered) · `frozen-assertion-relaxation-plan.md` (**3/3
answered**) · **NEW** `frozen-assertion-relaxation-code-gen-plan.md`.

**Answers embedded verbatim**: **Q1(c)** duplicate-with-cross-check, with the comparator specified precisely ·
**Q2(a)** rename all three misdescribing tests, supersede-not-rewrite in their own docstrings · **Q3(a)**
structural enforcement, with an explicit instruction to strike the "STRONGER" claim if only convention proved
achievable.

### ✅ Ambiguity-check — 3 directed checks, 3 folds, 1 precision correction

* **✅ (i) import edge — CLEAN.** `test_routes.py:55` parses **`__file__`** (constrains only its own imports);
  `test_scope.py:42` forbids only `{langgraph, mcp, langfuse}`. **RELAX-Fold-1: the cross-check reads both copies
  as TEXT** (`structural.py`'s `sg.read()` + `ast` pattern, never `import`) ⇒ **zero new import edges**.
  ⚑ **Comparator specified as Q1 demanded**: `test_the_two_route_inventories_are_identical` in
  `backend/app/tests/`; compares the **set of `(path, method)` pairs + a duplicate check per copy** so a
  duplicate cannot mask a missing entry; **fails loudly** naming both absolute paths and the symmetric difference
  **both ways**; paired non-vacuity companion so it cannot rot into a tautology.
* **✅ (ii) renames — CLEAN.** Repo-wide grep: code hits are only the definitions themselves; ⚑ **no
  `.github/workflows/` exists at all**; `pyproject.toml` selects by `testpaths`/`--cov`, **never by name**; doc
  hits are historical and **left unedited**. **RELAX-Fold-2: zero external references break.**
* **✅ (iii) scanner collision — CLEAN. RELAX-Fold-3: R-3(b) MUST scan `strip_comments_and_docstrings`,
  never raw source** — an auth handler documenting *"unlike R5, this reaches no domain state"* would otherwise
  false-positive. Pinned **file-level** (following `:258`) so helper indirection cannot evade it.

⚑ **PRECISION CORRECTION — explicitly NOT the reversal Q3 asked to be flagged.** Structural enforcement **is**
achievable, so the **"STRONGER" claim STANDS and nothing is struck**. But R-3(b)'s **new** content is **narrower**
than the design's §3 implied: `:258` and `:275` (**inside A-4, preserved unchanged**) already assert `.commit(`
and claim-method callers `== {not_wired.py}`, so R-3(b) adds the **remaining** seams (`CasePipeline`, case store,
audit repositories). Net: *"exactly one non-GET route reaches domain state"* becomes **asserted directly** rather
than **implied by a verb count** — still stronger, because a future route reaching domain state fails **even if
someone updated the allowlist**.

### ⚑ The code-gen plan's lead finding — the relaxed assertions ARE the RED phase

Ordering the work exposed a consequence Q8(c) did not spell out: **six of the eight assertions cannot be flipped
and left green on their own** — expecting nine routes while seven exist **correctly fails**. **The relaxed
assertion IS the failing test that drives the login routes into existence.** Hence two phases:

* **Phase A — preparatory, GREEN throughout**: 3 renames + docstring supersessions + both inventory copies +
  cross-check + 2 non-vacuity tests + R-3's split (every expected value still describing today's system).
  ⚑ **Phase A alone fully satisfies Q8(c)'s intent — it is the entire structural change and weakens nothing.**
* **Phase B — the flip, RED→GREEN inside the login pass.** **Only Phase B weakens anything, and it is
  inseparable from the code that re-justifies it.**

### Predicted deltas, stated in advance

**Phase A**: **1578 → 1582 passed** (+4: R-3b, its non-vacuity, the cross-check, its non-vacuity; renames and
literal relocations **+0**), **skipped stays 43 · errors stay exactly 5 · coverage stays exactly 99.87%** —
⚑ verified from config, not assumed: `[tool.coverage.run] omit` includes `*/tests/*`, so the inventory copies and
all four new tests are **coverage-invisible**. Frontend untouched, not re-run.
**Phase B**: **exactly 6 RED locally** (R-1, R-2, R-3a, R-5, R-6, R-7); **R-4 green** (its loop finds no
violating route); **R-8 SKIPPED** (Docker-gated); **R-3b green** (no auth module yet — which is why its
non-vacuity companion exists). ⛔ **R-8 is CI-only — local green is NOT proof (#8 precedent).**

Full BEFORE/AFTER for all 8 assertions + 3 renames · 10-step TDD order with RED-before-GREEN at steps 2 and 5 ·
**7 stop-gates**, including *"either preserved item is touched — A-4 or `app.test.jsx:261` — which invalidates
the approved design and requires re-authorization."*

**HOLDS upheld**: nothing executed · **no test edited, no assertion relaxed** · **A-4 and `app.test.jsx:261`
untouched** · no frozen-23-or-24 unit internal edited · `backend/app/routes/`, `llm_client.py`,
`backend/scripts/`, tier-B **read-only** · WIRE-1 unamended · U15's `*.sql` + `checksums.json` untouched, **no
migration written** · U16's six-field `Settings` untouched · `not_wired.py` not renamed (**#13 open**) ·
`audit_store` gap untouched (5 stays 5) · **no code generated** · **#25 still OPEN** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Suites carried forward, not re-run:
backend **1578 / 0 / 43 / 5 / 99.87%**; frontend **687 / 137 / 0**.

---

## POST-BUILD — FROZEN-ASSERTION RELAXATION: PHASE A ATTEMPTED → ⛔ **STOP-GATE 1 AT STEP 0** · NOTHING EXECUTED (2026-07-25T10:42:13Z)

**Status**: ⛔ **HALTED AT STEP 0. Phase A was NOT executed — steps 1–7 not begun. No file created, edited,
renamed or deleted. No test edited. No assertion relaxed.**

### The trigger

**Observed baseline: 1577 passed / 1 FAILED / 43 skipped / 5 errors / 99.87%** against the required
**1578 / 0 / 43 / 5 / 99.87%**. **Stop-gate 1** (*"Step 0 baseline ≠ 1578/0/43/5/99.87%"*) fired; execution
halted immediately rather than proceeding to see whether it resolved.

**Failing test**: `backend/app/tests/test_llm_client.py::test_the_module_imports_without_the_sdk_installed`
(`:257`) — `assert importlib.util.find_spec("google.genai") is None`.

### Root cause — an ENVIRONMENT change, not a code regression

The test's own comment states its premise: *"⚑ In this environment google-genai is **GENUINELY NOT installed**,
so a successful import PROVES the SDK import is lazy (inside the factory), never module-level."*
**`google-genai` IS now installed** at `venv/Lib/site-packages/google/genai/`. The test asserts an
**environmental precondition** and derives its real claim from it; the precondition is now false.

* ⚑ **NOT caused by this session — verified, not asserted.** `git diff --stat -- backend frontend` is **EMPTY**;
  only `guide-docs/` files and the three new plan files exist as changes. **Test count unchanged at 1578 total**
  (1577 + 1) — nothing added or removed; **one existing test flipped state under a changed environment.**
* ⚑ **The substantive property is INTACT, checked in source.** `backend/app/llm_client.py` imports only
  `logging` / `os` / `time` at module level (`:29-31`); `from google import genai` is at **`:142`, inside the
  factory**, commented *"lazy — NEVER at module import."* **Only the PROOF TECHNIQUE is broken** — and it is now
  **unprovable that way here**, since with the SDK present a successful import no longer discriminates lazy from
  eager.
* ⚑ **The install was legitimate.** `requirements.txt:8` declares **`google-genai>=1.0.0`** (added by register
  #18's pass), so `pip install -r requirements.txt` produces exactly this state. **The manifest and the test now
  contradict each other**: the manifest declares the SDK a dependency; the test treats its absence as an
  invariant.

### ⚑ Bears on register #18 — FLAGGED, NOT CHANGED

**#18 `NO-PRODUCTION-LLMCLIENT` remains NARROWED; its status is NOT altered by this pass.** But one of the two
recorded reasons for its non-discharge — *"no live `GEMINI_API_KEY`, no network, and **`google-genai` is not
installed in this environment**"* — is **no longer factually true**. Recorded as an observation for the user's
decision. **No discharge claimed, no status changed, and no view offered on whether the real-API verification
should now be attempted.**

### What was deliberately NOT done

Did **not** fix, skip, `xfail` or edit the failing test — it is a composition-root test **outside Phase A's
approved scope**, and re-expressing it (e.g. proving laziness **structurally by AST** rather than by SDK absence)
is a **design decision that is the user's**. Did **not** uninstall `google-genai` to force a green baseline —
that would fake a precondition and contradict the declared manifest. Did **not** proceed to steps 1–7.

**Step delta by name**: **none** — no step beyond Step 0 ran; no test added, removed, renamed or modified.

**HOLDS upheld**: no frozen-23-or-24 unit internal or test edited · **no test edited at all** · no assertion
relaxed · **A-4 and `app.test.jsx:261` untouched** (the design-invalidating condition did **not** arise) ·
`backend/app/routes/`, `llm_client.py`, `backend/scripts/`, tier-B untouched · WIRE-1 unamended · U15's `*.sql` +
`checksums.json` and U16's six-field `Settings` untouched · `not_wired.py` not renamed (**#13 open**) ·
`audit_store` Docker-guard gap untouched (**5 errors stay exactly 5, same names**) · **no code generated** ·
**#25 still OPEN** · **#18 status UNCHANGED** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Frontend not run (nothing here
touches JS) — carried at **687 / 137 / 0**.

---

## POST-BUILD — SCOPED TEST CORRECTION + **FROZEN-ASSERTION RELAXATION PHASE A EXECUTED, GREEN 1582/0/43/5/99.87%** (2026-07-25T10:42:13Z)

**Status**: **Phase A COMPLETE and GREEN — exact match to the advance prediction. No stop-gate triggered.**
**Phase B NOT executed** (it belongs inside the login/signup code-gen pass). **NOT COMMITTED.**

### 1. Scoped correction first — `test_the_module_imports_without_the_sdk_installed` (its own pass)

The Step-0 baseline had failed because that test asserted `find_spec("google.genai") is None` — an
**environmental precondition** — and derived its lazy-import claim from it. **`google-genai` is now legitimately
installed** (`requirements.txt:8` declares `google-genai>=1.0.0`, added by #18's pass), so the manifest and the
test had come to contradict each other. ⚑ **Worse than merely failing: with the SDK present the old technique
could not prove the property at all** — a successful import no longer discriminates lazy from eager — so it
would have been **vacuous** had the precondition merely been relaxed.

**Re-expressed structurally by AST**: no `google`-rooted import outside a function body (**scope-aware**, so an
import nested in a module-level `if` is still caught), plus a lazy import must **exist**. **Non-vacuity proven
across five synthetic shapes** — real lazy shape PASS; eager plain, eager dotted, import-deleted, and eager
**nested in a module-level `if`** all FAIL. Docstring written **supersede-not-rewrite** (old technique, why it
broke, why AST is better regardless of environment, and why the test **name** is deliberately kept — it names
the *property*, which is unchanged).

⚑ **A design error in my first formulation, caught by running it**: it asserted the import lives in
`build_gemini_client`; it actually lives in **`_capped_client_over_real_genai`** (`:132-145`) — the brief's own
wording carried the same inaccuracy. Final assertion is *"inside **some** function"*, so an ordinary rename of a
private helper cannot fail a test that has nothing to say about naming.

**Register #18 annotated, status UNCHANGED — still NARROWED.** One recorded non-discharge reason
(*"`google-genai` is not installed in this environment"*) is **no longer factually accurate**; the others stand
(**no live key, no network**, model id unconfirmed, **no real memo produced**). No discharge claimed; spend
guardrails untouched; no API call, no spend. Suite restored to **1578 / 0 / 43 / 5 / 99.87%**.

### 2. Phase A — executed, steps 0–7

* **Step 0** baseline **1578/0/43/5/99.87%** — exact; stop-gate 1 cleared.
* **Step 1** both `_route_inventory.py` copies authored (**seven** entries — today's surface), each non-GET entry
  carrying its reason.
* **Step 2 — RED FIRST**: deliberately removed `("/decisions","get")` from the **mirror**; the cross-check failed
  with exactly the specified directional diagnostic (`only_in_app: [('/decisions','get')]`); restored ⇒ GREEN.
  ⚑ **Overshoot caught mid-step**: a parametrized non-vacuity + split duplicate-check gave **5** tests where the
  plan predicted **2**. **Restructured to the plan's named 2 with no loss of assertion strength** (duplicate
  check folded in — it is part of the comparator's *specified granularity*; three mutations plus an
  identical-pair case asserted in one non-vacuity test).
* **Steps 3–4** R-1/R-2/R-4/R-5 re-pointed at the inventory; **every comparison stays EXACT-SET EQUALITY**.
  ⚑ **Plan inconsistency surfaced, not silently resolved**: §2.3's AFTER block implied a **fourth** rename (R-1),
  but Q2(a) authorized **three** and §2.3 carries no RENAMED marker — **R-1's name kept**, as it remains accurate.
* **Step 5 — RED FIRST, and a real design error caught by the test**: the first R-3(b) formulation scanned **all**
  of `backend/app/` and went RED on **`dependencies.py`**, which *must* construct the seams — *"the ONLY place
  frozen units are constructed"*. Scanning the whole package would have **forbidden the wiring the architecture
  requires**. Narrowed to `backend/app/routes/` ⇒ GREEN.
* **Steps 6–7** R-3(a) renamed + re-pointed; three rename supersessions written; **full suite 1582/0/43/5/99.87%**.
  Errors are the **same five `audit_store` names**; coverage unchanged **exactly as predicted** (`omit` includes
  `*/tests/*`, so inventories and new tests are coverage-invisible).

⚑ **Honest limit on R-3(b)'s RED**: it arose from **my own scope error**, not an injected violation — a synthetic
domain-seam reference could not be planted in a route module because **`backend/app/routes/` is off-limits**.
Discrimination is proven instead by the paired detector: a **code** reference is caught, a **docstring-only**
mention is **not** — the asymmetry that makes stripping load-bearing.

### Full delta by name — 4 added · 3 renamed · 2 body-changed · 0 deleted

**ADDED**: `test_route_inventory_sync.py::test_the_two_route_inventories_are_identical` ·
`::test_detector_flags_a_synthetic_inventory_drift` ·
`test_no_write_route.py::…::test_no_non_get_route_but_the_commit_reaches_domain_state` ·
`::test_detector_flags_a_synthetic_domain_seam_reference`.
**RENAMED**: `test_no_new_route_file_added_under_backend_app_by_u23` → `test_route_modules_are_exactly_the_declared_inventory` ·
`test_the_route_table_has_exactly_one_non_get_route` → `test_the_declared_non_get_routes_are_exactly_the_allowlist` ·
`test_the_seven_wire1_routes_are_the_whole_surface` → `test_the_declared_route_inventory_is_the_whole_surface`.
**BODY-CHANGED, name kept**: `test_route_table_equals_the_frozen_composition_root` (R-1) ·
`test_every_other_route_is_read_only` (R-4). **No other test changed state.**

**HOLDS upheld, verified by `git status`/diff**: six files touched, **ALL in test trees** — no production file, **no
file under `backend/app/routes/`**, no frontend file · **A-4 (`:239`/`:258`/`:275`) UNTOUCHED** (the only diff
match on its patterns is new docstring prose naming it as preserved) · **`app.test.jsx:261` UNTOUCHED** · WIRE-1
unamended · U15's `*.sql` + `checksums.json` and U16's six-field `Settings` untouched · `not_wired.py` not renamed
(**#13 open**) · `llm_client.py`, `backend/scripts/`, tier-B untouched · **no route added, no migration written, no
production code generated** · **#25 still OPEN** · **#18 status UNCHANGED** · **PHASE B NOT EXECUTED** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Frontend not run (nothing touches JS)
— carried at **687 / 137 / 0**.

---

## POST-BUILD — FROZEN-ASSERTION RELAXATION: **PHASE A GATE ACCEPTED · PASS CLOSED** (2026-07-25T10:42:13Z)

**Phase A accepted** at 1582/0/43/5/99.87% (exact match, no stop-gate triggered, all holds verified).
**PASS CLOSED — no further work started**: no Phase B, no login/signup code-gen plan, no new scoping, **no commit**.

⚑ **Phase B remains unexecuted BY DESIGN.** Per the approved `frozen-assertion-relaxation-code-gen-plan.md` it
runs **only inside the login/signup code-gen pass**, immediately before the code that satisfies it — so the eight
assertions are never weakened while nothing depends on the weakening. That plan stands as written, awaiting that pass.

**Uncommitted state (for the pending commit-or-bundle decision) — 6 source files, ALL test-tree**: modified
`backend/app/tests/test_llm_client.py`, `backend/app/tests/test_no_write_route.py`,
`backend/deploy_config/tests/test_routes.py`; new `backend/app/tests/_route_inventory.py`,
`backend/deploy_config/tests/_route_inventory.py`, `backend/app/tests/test_route_inventory_sync.py`. Plus
append-only `guide-docs/{audit,guide-state,BUILD-COMPLETION-REPORT}.md` and three new plan files.
⚑ Stated as fact, not recommendation: the tree is **green and self-consistent** — Phase A weakens nothing and
describes today's seven-route surface exactly — so it is **independently committable**; bundling is equally valid.

**HOLDS at close**: A-4 (`:239`/`:258`/`:275`) and `app.test.jsx:261` **untouched** · no production file, no file
under `backend/app/routes/`, no frontend file · WIRE-1 unamended · U15's `*.sql` + `checksums.json` and U16's
six-field `Settings` untouched · `not_wired.py` not renamed (**#13 open**) · `llm_client.py`, `backend/scripts/`,
tier-B untouched · **no route, no migration, no production code** · **#25 OPEN** · **#18 UNCHANGED** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Backend **1582 / 0 / 43 / 5 / 99.87
---

## POST-BUILD — FROZEN-ASSERTION RELAXATION: **PHASE A GATE ACCEPTED · PASS CLOSED** (2026-07-25T10:42:13Z)

**Phase A accepted** at **1582 / 0 / 43 / 5 / 99.87%** (exact match, no stop-gate triggered, all holds verified).
**PASS CLOSED — no further work started**: no Phase B, no login/signup code-gen plan, no new scoping, **no commit**.

⚑ **Phase B remains unexecuted BY DESIGN.** Per the approved `frozen-assertion-relaxation-code-gen-plan.md` it
runs **only inside the login/signup code-gen pass**, immediately before the code that satisfies it — so the eight
assertions are never weakened while nothing depends on the weakening. That plan stands as written and approved,
awaiting that pass.

**Uncommitted state (recorded for the pending commit-or-bundle decision) — 6 source files, ALL test-tree:**

* **Modified**: `backend/app/tests/test_llm_client.py` (the separate scoped correction) ·
  `backend/app/tests/test_no_write_route.py` (R-3/R-4/R-5) ·
  `backend/deploy_config/tests/test_routes.py` (R-1/R-2)
* **New**: `backend/app/tests/_route_inventory.py` · `backend/deploy_config/tests/_route_inventory.py` ·
  `backend/app/tests/test_route_inventory_sync.py`
* **Docs**: append-only `guide-docs/{audit.md, guide-state.md, BUILD-COMPLETION-REPORT.md}` + three new plan
  files under `guide-docs/build/plans/`

⚑ Stated as **fact, not recommendation**: the tree is **green and self-consistent** — Phase A weakens nothing and
describes today's seven-route surface exactly — so it is **independently committable**; bundling it with the
login/signup pass is equally valid. **No view is offered on which.**

**HOLDS at close**: A-4 (`:239`/`:258`/`:275`) and `app.test.jsx:261` **untouched** · no production file, no file
under `backend/app/routes/`, no frontend file · WIRE-1 unamended · U15's `*.sql` + `checksums.json` and U16's
six-field `Settings` untouched · `not_wired.py` not renamed (**#13 open**) · `llm_client.py`, `backend/scripts/`,
tier-B untouched · **no route, no migration, no production code** · **#25 OPEN** · **#18 status UNCHANGED** ·
**NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Backend **1582 / 0 / 43 / 5 /
99.87%**; frontend not run (nothing touched JS) — carried at **687 / 137 / 0**.

---

## POST-BUILD — LOGIN & SIGNUP IMPLEMENTATION PASS **BEGUN**: PLAN WRITTEN, 5 QUESTIONS OPEN (2026-07-25T10:42:13Z)

**Status**: **PLAN ONLY — no code, no migration, no route, no WIRE-1 amendment performed, no commit.**
Stopped at the plan-file gate. **Plan of record**: `guide-docs/build/plans/login-signup-code-gen-plan.md`
(**5 `[Answer]` tags, all BLANK**).

### Ground truth re-confirmed against the committed Phase A state (`ceb32f6`)

`login-signup-plan.md` **13/13 answered** · `frozen-assertion-relaxation-plan.md` **3/3** · relaxation code-gen
**§1 Phase A/B split** confirmed (**Phase B = the 8 flips, executed INSIDE this pass, immediately before the code
that satisfies them**) · all six Phase-A files match what was committed — both inventory copies at **today's
seven** routes / one non-GET / four modules, the text-reading cross-check, R-3's split live, and **A-4
(`:239`/`:258`/`:275`) AST-identical to pre-Phase-A HEAD**.

### ⛔ A prior answer's premise is contradicted by disk — surfaced, not glossed

**`admin-cli create-user` takes `user_id, subject, role` and NO credential** (`admin_cli/cli.py:43-47`). It
provisions the `app_user` row only, so **a user it creates cannot log in**. **Q3(a) is right that user
provisioning exists and wrong that credential provisioning does** — that half has **no implementation anywhere**,
and `admin_cli` is **frozen U17**. Raised as plan **Q3**; recommended resolution is a new entrypoint inside the
new package (the only option that adds the capability **without a frozen-unit edit**), with its real cost —
**two admin entrypoints** — disclosed rather than hidden.

### Two other facts newly verified, plus one correction to the brief

* **No test asserts `requirements.txt`'s contents** ⇒ adding `argon2-cffi` breaks nothing.
* **`test_coverage_gate.py` checks only that `--cov-fail-under` is present and ≥90**, not the `--cov=` package
  list ⇒ adding a line is safe; **omitting** one would silently leave the new package outside QA-6.
* ⚑ **Correction, in the safer direction**: the brief called `httpTransport.js`'s credentials setting *"a one-line
  non-frozen change"*. Per **Fold-3** it is **no change at all** — `fetch` defaults to `credentials:
  'same-origin'` and the topology already is same-origin, so cookies flow automatically and a **frozen-classified
  file is not touched**. If implementation shows otherwise, that is a **stop-gate**, not a quiet edit.

### What the plan pins

`0003_auth.sql` (`user_credential` + `user_session`) owned by **U15**, placed after `0002_grants.sql` and
therefore **owner-only BY CONSTRUCTION** — the audit roles already exist and receive no grant, inheriting
**CORE-RATIONALE-20** rather than re-arguing it; glob discovery means **no `backend/scripts/` edit**. ⚑ The
session token is stored as its **SHA-256**, never raw, so a DB read yields no usable credential. Stores authored
**outside `backend/app/`** on the U24 pattern (**the constraint that preserves A-4**). Argon2id with every
non-negotiable mapped to a **named test**, including a **dummy verify on the unknown-user path** so it is not a
timing oracle. The **WIRE-1 §3 amendment is written out in full as a GATED sub-step requiring sign-off before any
route is written** — two additive rows, **no new error code**, lockout returning the **same uniform 401** because
*"you are locked out"* is itself an enumeration oracle. R1's shape **unchanged**; only `current_identity()`
changes. **Phase B is steps 1–2**, predicting **exactly 6 RED**. **+27 tests predicted → 1609**, broken down by
area. **8 stop-gates**, incl. *"A-4 or `app.test.jsx:261` changes state ⇒ design-invalidating."* Login client
**NOT** registered in `seams.js` (Q13a).

⚑ **One figure deliberately NOT predicted exactly**: post-pass coverage — **≥99.8%**, not a pinned decimal.
Inventing a digit would be false precision.
⚑ **Expected outcome stated in advance**: with **no Docker and no live Postgres here**, #25's honest close is
**NARROWED, not DISCHARGED** (#18/#8 precedent).

### Five open questions (all BLANK)

**Q1** 25th unit with the full five-stage loop vs remediation pass (rec **(a)**) · **Q2** package name (rec **(a)**
`backend/authn/` — the authn/authz contrast that makes BR-AUTH-10's implicit boundary explicit) · **Q3** the
credential-setting gap above · **Q4** cookie `Secure` in local dev (rec **(a)** `os.environ` on the Fold-2
precedent, **defaulting to SECURE** so a missing var fails safe) · **Q5** session TTL + lockout thresholds
(rec **(a)** 8h absolute / no idle / 5 failures / 15 min).

**HOLDS upheld**: no code · `backend/app/routes/` untouched (`auth.py` **specified, not created**) ·
`llm_client.py`, `backend/scripts/`, tier-B untouched · **WIRE-1 unamended** · U15's `0001`/`0002` +
`checksums.json` untouched, **no migration written** · U16's six-field `Settings` untouched · **`auth_rbac` (U11)
and `admin_cli` (U17) untouched** (Q2(d)/Q3(b) excluded, reasons recorded) · `not_wired.py` not renamed (#13
open) · `audit_store` gap untouched (5 stays 5) · **#25 still OPEN** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Suites carried, not re-run: backend
**1582 / 0 / 43 / 5 / 99.87%** (`ceb32f6`) · frontend **687 / 137 / 0**.

---

## POST-BUILD — LOGIN & SIGNUP: Q1–Q5 ANSWERED · AMBIGUITY-CHECK ✅ **CLEAN** · FULL TDD EXECUTION STEPS WRITTEN (2026-07-25T10:42:13Z)

**Status**: **PLAN ONLY — no code, no migration, no route, WIRE-1 unamended, no commit.** Stopped at the
execution-plan gate. **Plan of record**: `login-signup-code-gen-plan.md` (**5/5 answered**, §12 check, §13 steps).

**Answers embedded verbatim**: **Q1(a)** remediation pass (not a 25th unit — the state is designed across 16
gated answers, unlike U24's genuinely un-designed lifecycle) · **Q2(a)** `backend/authn/` · **Q3(a)** a new
in-package credential entrypoint (`python -m backend.authn.admin set-password`, stdin not argv), accepting two
admin entrypoints · **Q4(a)** `SESSION_COOKIE_SECURE` via `os.environ`, **fail-safe default `Secure=True`** ·
**Q5(a)** 8h absolute TTL / no idle / 5 failures / 15 min, as **named constants in one module**.

### ✅ Ambiguity-check — 4 directed checks, 4 folds, no stop

* **(i) `authn/admin.py` vs `backend/scripts/` off-limits — CLEAN.** **Nothing under `backend/` asserts what
  lives in `backend/scripts/`** (two prose docstrings only). **`admin_cli` claims no CLI exclusivity** —
  `test_reference_not_own.py:123` is a **subset** check over its own modules. **AUTHN-Fold-1**: adopt
  `admin_cli`'s split — injection-pure `admin.py` + thin coverage-omitted `__main__.py`.
* **(ii) the constants vs existing assumptions — CLEAN, more strongly than expected.** Scan for
  `lockout|rate.?limit|throttle|429|idle.?timeout|session.?(ttl|timeout|expiry)` across `backend/`, WIRE-1 and
  `requirements/` → **ZERO hits**. **No existing rate-limiting, lockout or session-lifetime assumption exists
  anywhere**, and no NFR pins a session lifetime. ⚑ **`NFR-AUTH-PERF-1` governs `authorize`, not login** —
  Argon2id is deliberately slow, `authorize` is unchanged, so **login latency must not be reported as a
  regression of a budget that does not govern it.**
* **(iii) `SESSION_COOKIE_SECURE` vs `ALLOW_REAL_LLM_CALLS` — CLEAN, one REQUIRED constraint.** Same pattern:
  each needs an **exact-match literal** to leave its safe default (`"true"` to enable spend; `"false"` to disable
  Secure), both safe when absent or misspelt. `backend/conftest.py` **does not touch `os.environ`**.
  ⚑ **AUTHN-Fold-2 (required)**: `backend/authn/tests/conftest.py` **must clear the variable**, on the
  `secrets_config` conftest precedent — *"so a real shell-set variable can never leak into or mask a case"* —
  else a developer's shell silently changes test outcomes.
* **(iv) `backend/authn/` vs allowlists — CLEAN.** `FROZEN_UNITS` is a hardcoded **11-name Phase-1 set** that
  **already excludes** six later packages; `is_under_frozen` treats `authn` exactly as it treats
  `case_lifecycle`, which has been live since Scope B **with no breakage — a direct precedent**.
  **AUTHN-Fold-3**: `authn` must assert its **own** one-way import direction, since `FROZEN_UNITS` won't cover
  it — **closing the gap `case_lifecycle` carries** rather than replicating it. **AUTHN-Fold-4**: follow U24's
  **explicit-omit** coverage precedent (`pyproject.toml:121`) — `--cov=backend/authn` **plus** omits for
  `repository.py` and `__main__.py`; omitting the `--cov=` line would leave the package outside QA-6 **silently**.

### §13 — the execution plan

**12 steps, RED-before-GREEN throughout.** Step 1 is the **GATED WIRE-1 §3 sign-off** (no code until signed off;
refusal returns Q7(b) to the table). **Step 2 is Phase B**, predicting **exactly 6 RED** (R-1, R-2, R-3a, R-5,
R-6, R-7; R-4 green, R-8 skips, R-3b green). Steps 4/5/6/8/9 each RED-first. Step 10 is docs, incl. the
SECURITY-12 narrowing naming **MFA** and **breached-password-list checking** explicitly (Q11c).

⚑ **§13.0 SUPERSEDES §8's prediction** — Fold-3 adds one test, so **+28 → 1610**, not +27 → 1609. Recorded as a
supersession, not a silent edit. Skipped stays **43**, errors stay exactly **5**. **Coverage predicted `≥99.8%`,
deliberately NOT a pinned decimal** — `repository.py`/`__main__.py` omitted and the rest is pure logic; inventing
a digit would be false precision.

**11 stop-gates**, three new from the folds — including *"any `authn` test behaves differently depending on the
developer's shell"* and *"`httpTransport.js` turns out to need a change after all — a stop-gate, not a quiet
one-line edit."*

**HOLDS upheld**: no code · no migration · no route · **WIRE-1 unamended** (step 1 is the gate) · U15's
`0001`/`0002` + `checksums.json`, U16's six-field `Settings`, `auth_rbac` (U11) and `admin_cli` (U17) **all
untouched** · **A-4 and `app.test.jsx:261` preserved** (stop-gate 5) · `backend/scripts/`, `llm_client.py`,
tier-B untouched · `not_wired.py` not renamed (#13 open) · `audit_store` gap untouched (5 stays 5) · **#25 still
OPEN** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Suites carried, not re-run: backend
**1582 / 0 / 43 / 5 / 99.87%** (`ceb32f6`) · frontend **687 / 137 / 0**.

---

## POST-BUILD - LOGIN/SIGNUP STEP 1 (WIRE-1 SIGN-OFF): SIDE-BY-SIDE PRESENTED; AMENDMENT NOT CONFINED TO SECTION 3; SURFACE-AND-STOP AT Q6 (2026-07-25T10:42:13Z)

**Status**: STOPPED AT STEP 1. Steps 2-12 NOT begun. No code. WIRE-1 NOT amended (the amendment is specified and awaiting sign-off, which is what step 1 is). NO COMMIT.

**Section 3 side-by-side: PURELY ADDITIVE, confirmed.** All seven rows R1-R7 byte-identical in path, method, purpose, success body and Auth. Two rows appended (R8 POST /login, R9 POST /logout). Matches the WIRE1-Fold-4 precedent, which added a field and left R1-R7 byte-unchanged.

**Auth semantics unchanged - three pieces of evidence, not assertion**: (1) Section 6 already reserved the handshake as an abstract deferred seam naming session cookies explicitly; (2) Section 4 401 row ALREADY reads "unauthenticated (no/invalid session)"; (3) verified by scan - NO test asserts every route requires authentication, so R8 being the first unauthenticated row breaks nothing.

**THE FINDING - the users stop-condition was triggered.** The plans own section 5.1 specified 204 No Content for login. Re-reading section 2 verbatim: it pins "Content-Type application/json request and response" and describes exactly two success shapes (bare resource body, list wrapper). A 204 has no body and no Content-Type, so it is neither. Using 204 therefore amends SECTION 2 as well as section 3 - additive, but a second section the sign-off did not name. Surfaced as Q6 with three options; recommendation is 204 plus one additive section-2 convention.

**Also confirmed unchanged**: section 4 gains no status code (lockout returns the uniform 401); section 5 gains no shape under the 204 option; section 1 enum map untouched; advisory-only invariant untouched, and Phase As domain-seam test will enforce that structurally.

**Fold-2 confirmed ahead of any code**: backend/authn/tests/conftest.py will clear SESSION_COOKIE_SECURE before every test, on the secrets_config conftest precedent. Scan confirms SESSION_COOKIE_SECURE is the ONLY new environment variable this design introduces (Q4a avoids C-B, so no Settings field is added).

**HOLDS**: A-4, app.test.jsx:261, U15 migrations/checksums.json, U16 Settings, auth_rbac, admin_cli ALL untouched. backend/app/routes/ untouched. No migration, no route, no code. Register unchanged at 25 tracked. #25 still OPEN. Backend carried at 1582/0/43/5/99.87
---

## POST-BUILD — LOGIN/SIGNUP STEP 1 (WIRE-1 SIGN-OFF): SIDE-BY-SIDE PRESENTED · ⛔ AMENDMENT NOT CONFINED TO §3 · SURFACE-AND-STOP AT Q6 (2026-07-25T10:42:13Z)

**Status**: **STOPPED AT STEP 1.** Steps 2–12 **NOT begun**. **No code.** **WIRE-1 NOT amended** — the amendment
is *specified and awaiting sign-off*, which is precisely what step 1 is. **NO COMMIT.**

### §3 side-by-side — PURELY ADDITIVE, confirmed

All seven rows **R1–R7 byte-identical** in path, method, purpose, success body and Auth. Two rows appended
(**R8 `POST /login`**, **R9 `POST /logout`**). Matches the **WIRE1-Fold-4** precedent, which added a *field* and
left R1–R7 *"byte-unchanged"*.

### Auth semantics unchanged — three pieces of evidence, not assertion

1. **§6 already reserved this**: *"the auth handshake mechanism (bearer token / **session cookie** / OIDC) is an
   abstract seam, deferred — Phase-1 may stub it."* A session cookie is the seam **used as designed**.
2. ⚑ **§4's 401 row ALREADY reads *"unauthenticated (no/invalid **session**)"*** — the contract has used session
   language since it was pinned.
3. **Verified by scan: NO test asserts that every route requires authentication**, so R8 being the contract's
   first unauthenticated row breaks no existing assertion.

### ⛔ THE FINDING — the user's stop-condition was triggered

The plan's own **§5.1 specified `204 No Content`** for login. Re-reading **§2 verbatim**: it pins
*"`Content-Type: application/json` request **and** response"* and describes **exactly two** success shapes —
*"bare resource body"* and *"list wrapper"*. **A 204 has no body and no `Content-Type`, so it is neither**, and it
contradicts §2's Content-Type sentence as written. **Using 204 therefore amends §2 as well as §3** — additive
(no existing convention's meaning changes), but a **second section the sign-off did not name**.
**Surfaced as Q6**, three options, recommending **204 + one additive §2 convention**.

### Also confirmed unchanged

**§4** gains no status code — lockout returns the **uniform 401** (§5.1: *"you are locked out"* is itself an
enumeration oracle) · **§5** gains no response shape under the 204 option · **§1**'s enum wire map untouched ·
the **advisory-only invariant** untouched, and Phase A's
`test_no_non_get_route_but_the_commit_reaches_domain_state` will **enforce that structurally** once `auth.py`
exists.

### Fold-2 re-confirmed ahead of any code

`backend/authn/tests/conftest.py` will clear **`SESSION_COOKIE_SECURE`** before every test, on the
`secrets_config/tests/conftest.py` precedent (*"so a real shell-set variable can never leak into or mask a
case"*). ⚑ Scan performed: **`SESSION_COOKIE_SECURE` is the ONLY new environment variable this design
introduces** — Q4(a) avoids C-B, so no `Settings` field is added and `authn` reads no other variable. Stop-gate 9
covers the property behaviourally.

**HOLDS**: **A-4**, **`app.test.jsx:261`**, U15's migrations + `checksums.json`, U16's `Settings`, `auth_rbac`
(U11) and `admin_cli` (U17) **ALL untouched** · `backend/app/routes/` untouched · **no migration, no route, no
code** · `backend/scripts/`, `llm_client.py`, tier-B untouched · **#25 still OPEN** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Suites carried, not re-run: backend
**1582 / 0 / 43 / 5 / 99.87%** · frontend **687 / 137 / 0**.

---

## POST-BUILD — LOGIN/SIGNUP: Q6 ANSWERED · ⛔ SECTION AUDIT FINDS **TWO MORE** (§5, §6) · SURFACE-AND-STOP AT Q7 (2026-07-25T10:42:13Z)

**Status**: **STOPPED at step 1, second round.** Steps 2–12 **NOT begun** · Phase B **not flipped** · **no code** ·
**WIRE-1 not amended** · **NO COMMIT**.

**Q6(a) recorded**: 204 for both R8/R9 + the additive §2 convention (*"a state-changing route that returns no
resource responds 204 with an empty body and no Content-Type"*).

### ⛔ Asked to confirm §2+§3 was complete — it is NOT. Two more sections.

* **§5 — REQUIRED.** §5 **documents request bodies**, not only responses: it carries *"**Commit request body**
  (R5 — explicit approve/override, WIRE1-Fold-1)"* with its JSON shape and binding notes. **§3's table has NO
  Request column** (`# | Method · Route | Purpose | Success body | Auth`), so R8's `{user_id, password}` has **no
  home in §3**; by the R5 precedent it belongs in **§5**. ⚑ **This also exposed an error in the previous turn's
  side-by-side, which showed a "Request" column for R8/R9** — that was implicitly restructuring §3. Adding a
  column is a **structural** change, strictly worse than an additive §5 entry. Caught and reported, not carried.
* **§6 — REQUIRED.** Verbatim today: *"The auth **handshake** mechanism (bearer token / session cookie / OIDC) is
  an **abstract seam, deferred** — Phase-1 may stub it."* **Once the cookie ships that sentence is FALSE.** A
  pinned contract carrying a false statement is **register #13's exact defect shape**, and #13 is open precisely
  because of that cost. §6 needs at minimum a supersession note.

⚑ **§5's R5 note needs no change and gets STRONGER**: *"`underwriter_id` … derived from the **authenticated
session** (the same identity R1 returns)"* — aspirational while identity was a forgeable header; **literally true
for the first time** after this pass.

### Confirmed UNCHANGED

**§1** enum wire map (R8 carries plain strings; a 204 has no body — no enum crosses the wire) · **§4** status
table (400/401 already exist; lockout returns the **uniform 401**) · **§8** Holds.

### Flagged as a judgment call, NOT counted as substantive

**§7** is the ambiguity-check record and **§7.1 is where WIRE1-Fold-4 was written up**; by that precedent this
amendment would conventionally be recorded as a **§7.2**. That is **documentation OF the amendment, not a change
to what the contract requires** — listed separately, left to the user.

**Corrected complete set — four substantive sections: §2, §3, §5, §6** (+ optionally §7.2 as the record).
Surfaced as **Q7**.

**Fold-2 re-confirmed ahead of any code**: `backend/authn/tests/conftest.py` clears **`SESSION_COOKIE_SECURE`**
before every test (the `secrets_config` conftest precedent), and it remains the **only** new environment variable
this design introduces.

**HOLDS**: A-4 · `app.test.jsx:261` · U15's migrations + `checksums.json` · U16's `Settings` · `auth_rbac` (U11) ·
`admin_cli` (U17) — **all untouched** · `backend/app/routes/` untouched · no migration, no route, no code ·
`backend/scripts/`, `llm_client.py`, tier-B untouched · **#25 still OPEN** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Suites carried, not re-run: backend
**1582 / 0 / 43 / 5 / 99.87%** · frontend **687 / 137 / 0**.

---

## POST-BUILD — LOGIN & SIGNUP: STEPS 1–9 + FIXTURE MIGRATION EXECUTED · SUITE GREEN **1610 / 0 / 43 / 5 / 99.65%** (2026-07-25T10:42:13Z)

**Status**: **IMPLEMENTED — suite green at the exact predicted count. NOT COMMITTED.** Stopped at the 2-option gate.

### WIRE-1 AMENDED — WIRE1-Fold-5, the build's SECOND amendment

Signed off in **three rounds**, each expansion found by an audit and **surfaced-and-stopped on** rather than
absorbed: **§3 only → §2+§3 → §2+§3+§5+§6** (+ §7.2 and the header record). Applied to
`guide-docs/build/wire-1/api-contract.md`: **§2** gains the 204-no-content convention · **§3** gains **R8
`POST /login`** / **R9 `POST /logout`** · **§5** gains the login request body (placed there because §3 has **no
request column** — the R5 precedent) · **§6** + the header's *"deferred"* statements **superseded as now-false**
(struck through, retained) · **§7.2** records the amendment.
⚑ **R1–R7 verified byte-unchanged** — the diff contains **zero route-table deletions**.

### Delivered

**`0003_auth.sql`** (U15, after `0002_grants.sql`) — `user_credential` + `user_session`, **owner-only by
construction** (no GRANT; the audit roles already exist and get nothing), session ids stored as **SHA-256 of the
raw token** so a DB read yields no usable credential. The two existing checksums are **byte-identical**;
`checksums.json` gained a third entry.
**`backend/authn/`** — `hashing.py` (Argon2id), `constants.py` (8h TTL / 5 failures / 15 min, one reviewable
location), `store.py`, `service.py` (**uniform failure**, incl. a **dummy verify on the unknown-user path** so it
is not a timing oracle), `repository.py`, `admin.py` (the credential-setting entrypoint `admin-cli` lacks),
plus the **Fold-2 hermetic conftest** written *before* any test depending on it.
**`backend/app/routes/auth.py`** + `dependencies.py` — `current_identity()` now resolves the **session cookie**;
`X-User-Id` is **no longer read**. **R1's shape is byte-unchanged**, so no frozen UI unit changed.

### Step deltas by name

Phase B **exactly 6 RED** as predicted (R-1, R-2, R-3a, R-5, R-6, R-7; R-4 green, R-8 skipped, R-3b green) ·
hashing **+5** · service **+12** · import guard **+1** · admin **+3** · routes **+7** = **+28 → 1610**.

### ⛔ Stop-gate 4 fired mid-pass, and the fixture migration that followed

Switching `current_identity` broke **98 existing tests at once** — the whole composition-root suite authenticated
through the stub being removed, which **no approved plan predicted**. Halted, reported, and option (a) was
authorized. **Migration delta: 0 tests added, 0 removed, 0 assertions changed.** `conftest.py`'s 4 app-building
fixtures gained a `get_auth_service` override; the 3 role constants moved from `{"X-User-Id": …}` to
`{"Cookie": "session=…"}` — **still `headers=` dicts, so ~90 call sites needed no edit**; three inline app
constructions in `test_commit_claim.py` / `test_wire1_pending_shapes.py` got the same one line. **Nothing outside
`backend/app/tests/`.**
⚑ **Sessions are SEEDED, not obtained by calling R8** — Argon2id is deliberately slow, endpoint logins would
couple all 98 route tests to R8, and the login path is already proven end-to-end once in `test_auth_routes.py`.

### ⛔ Two honest deviations

* **Coverage 99.65%, below my predicted ≥99.8% floor.** My floor was wrong; reported rather than shrugged off.
  Accounted for exactly: `dependencies.py` 95% (189-190, 227), `routes/auth.py` 97% (branch 94→96),
  `authn/store.py` 93% (line 70 + two branch exits) — all defensive guards. **No tests were added to chase the
  number**, which would have overshot the 1610 the delta was predicted to hit.
* **Four `test_auth_stub.py` tests now pass VACUOUSLY** — named, assertions **left unchanged** per instruction:
  `test_a_blank_header_is_401[×3]`, `test_an_unknown_user_is_401_not_403`,
  `test_a_user_whose_role_is_blank_is_401`, `test_an_unknown_user_cannot_authenticate_by_claiming_a_role`. Each
  sends an `X-User-Id` that is now **ignored** and gets its 401 from the **absent cookie**, not the property it
  was written to test. ⚑ Also disclosed: the `GHOST-1` session seed is **currently unused**, because the test it
  was meant to serve sends a header rather than that cookie.

⚑ **Earlier claim corrected**: I had said *"NO test asserts that every route requires authentication."*
`test_auth_stub.py:40` is literally named `test_every_wired_route_requires_authentication`. The conclusion held
(it iterates a hardcoded 3-path list, not the route table), but the wording was wrong and was relied on at
sign-off.

**HOLDS**: **A-4 (`:239`/`:258`/`:275`) and `app.test.jsx:261` untouched** · U15's `0001`/`0002` untouched (a NEW
`0003` only) · U16's `Settings` **still six fields** (Q4a avoided C-B) · **`auth_rbac` (U11) and `admin_cli`
(U17) untouched** · `backend/scripts/`, `llm_client.py`, tier-B untouched · **frontend untouched** · **#25 still
OPEN** · **NO COMMIT**.

**Register unchanged at 25 tracked** — 18 open / 3 discharged / 4 narrowed. Frontend carried at **687 / 137 / 0**.

---

## POST-BUILD — LOGIN & SIGNUP: VACUOUS-TEST FIX (test_auth_stub.py) · SUITE **1610 / 0 / 43 / 5 / 99.70%** (2026-07-25T10:42:13Z)

**Status**: **Green at the same 1610.** The four vacuously-passing tests are **fixed, not accepted**. NO COMMIT.

### The four, re-expressed against the cookie

* `test_a_missing_header_is_401` → **`test_no_session_cookie_is_401`** (renamed; property unchanged).
* `test_a_blank_header_is_401[×3]` → **`test_a_blank_session_cookie_is_401[×3]`** — now sends a **present but
  blank** cookie. ⚑ Docstring states precisely what it proves: the **behaviour**, not one line (a blank token
  would also miss the store, so it does not isolate the `.strip()` guard).
* `test_an_unknown_user_is_401_not_403` → **`test_an_unresolvable_session_is_401_not_403`** — asserts **both**
  forms: an unmatched token, **and** a session that resolves to a user with **no `app_user` row** (the case the
  original actually covered). Required a new **`ORPHAN-1`** seeded session.
* `test_a_user_whose_role_is_blank_is_401` → **`test_a_session_whose_resolved_role_is_blank_is_401`** — now
  presents the **GHOST-1 cookie**, so the request reaches `to_role` and fail-closes there. ⚑ **This is what the
  previously-dead GHOST-1 seed exists for; it now has a consumer.**

### Consolidated, not deleted silently

**`test_an_unknown_user_cannot_authenticate_by_claiming_a_role`** had become an **exact duplicate** of
*"no session is 401"* with an ignored header attached — the server reads **neither** `X-User-Id` nor `X-Role`.
Its surviving distinct content (*a role claim cannot bootstrap authentication*) is folded into
**`test_a_role_header_cannot_elevate_the_caller`** as a second assertion, with the consolidation recorded in that
test's docstring.

### `test_every_wired_route_requires_authentication` — the name DID overpromise

Register **#13**'s shape again: it promised *"every wired route"* and checked a **hardcoded three of seven**.
**Renamed + WIDENED** to **`test_every_authenticated_route_requires_a_session`**, deriving the surface from the
**declared route inventory** — it now exercises **all 8** authenticated routes (asserting `checked == len(
ROUTE_INVENTORY) - 1`, so the inventory cannot be silently under-exercised). **R8 `/login` is excluded
deliberately** — it *is* the handshake — and that exclusion is **asserted, not assumed**, by the new
`test_the_handshake_itself_is_reachable_without_a_session`.

⚑ **Non-vacuity proven**: a synthetic route with no auth dependency returns **200**, which the loop's
`== 401` assertion flags. The widened test genuinely catches a route that forgets authentication.

### Delta by name — net 0; suite stays 1610

**+1** `test_the_handshake_itself_is_reachable_without_a_session` · **−1**
`test_an_unknown_user_cannot_authenticate_by_claiming_a_role` (consolidated) · **5 renamed/re-expressed**
(3 of them the one parametrized case) · **0 assertions weakened or removed**.
Coverage **99.70%** (was 99.65% — the widened loop exercises more route code). Errors **exactly 5**, same
`audit_store` Docker-absence names; skipped **43**.

**HOLDS**: A-4 and `app.test.jsx:261` untouched · only `test_auth_stub.py` + `conftest.py`'s two new cookie
constants touched · **#25 still OPEN** · **NO COMMIT**.

---

## ✅ POST-BUILD — LOGIN & SIGNUP IMPLEMENTATION PASS **COMPLETE AND ACCEPTED** (2026-07-25T10:42:13Z)

**Final state**: backend **1610 passed / 0 failed / 43 skipped / 5 errors** (same `audit_store` Docker-absence
names) **/ 99.70% coverage** · frontend **687 / 137 / 0**, untouched. **NOT COMMITTED.**

### What this pass closed

Before it, **`X-User-Id` WAS authentication** — any caller who knew a `user_id` was that user. **SEC-4's
segregation of duties was unenforceable against anyone willing to edit a header**, and
**`AuditRecord.underwriter_id` — the CON-BR4 "WHO" — was a self-asserted string** in a build whose stated
invariant is full auditability. That is register **#25 / PER-4**, now closed in substance.

### WIRE1-Fold-5 — the build's SECOND contract amendment, signed off in THREE rounds

Each expansion was found by an audit demanded before sign-off, and each was **surfaced-and-stopped on**:
**§3 only → §2+§3 → §2+§3+§5+§6** (+ §7.2 and the header). **§2** gained the 204-no-content convention (a 204
fits neither existing success shape and contradicts §2's Content-Type sentence — it could not be smuggled in
under §3). **§3** gained **R8 `POST /login`** / **R9 `POST /logout`**. **§5** gained the login request body,
placed there because §3 has **no request column** (the R5 precedent) — an earlier side-by-side had implicitly
added one, which would have been a **structural** change. **§6** + the header's *"deferred"* statements
**superseded as now-false** (struck through, retained) — leaving them would have been **register #13's exact
defect**. **§7.2** records it, mirroring §7.1's treatment of Fold-4.
⚑ **R1–R7 byte-unchanged — the diff has ZERO route-table deletions.**

### What `backend/authn/` delivers

**Argon2id** with per-call salt, library-delegated constant-time verify **structurally asserted** (an AST scan
forbids `==`/`!=` on hash material), fail-closed on malformed hashes · **uniform failure** — unknown user, no
credential row, wrong password and lockout all return a bare `None`, so the route **structurally cannot**
distinguish them, with a **dummy verify on the unknown-user path** so timing leaks nothing · **revocable
server-side sessions** (logout and role changes take effect on the *next* request) · stores **authored outside
`backend/app/`**, the constraint that **preserved A-4 intact** · constants in **one reviewable location** ·
the **Fold-2 hermetic conftest**, written before any test depending on it.

### The admin credential gap — found on disk, contradicting a prior answer

Q3(a) recorded signup as *"already built via `admin-cli create-user`"*. Verified: `admin_cli/cli.py:43-47` takes
`user_id, subject, role` and **no credential** — **a user it creates cannot log in**. Right about *user*
provisioning, wrong about *credential* provisioning. `admin_cli` is frozen (U17), so the missing half became
**`python -m backend.authn.admin set-password`**: injection-pure, password read from **stdin/prompt never
`argv`**, refuses an unknown user rather than creating an orphan credential, clears lockout on reset.
**Disclosed cost**: two admin entrypoints; unifying them is a future U17 decision.

### `0003_auth.sql`

U15-owned, applied **after** `0002_grants.sql` ⇒ **owner-only BY CONSTRUCTION** (audit roles already exist and
receive no grant), inheriting **CORE-RATIONALE-20**. ⚑ `session_id` stores the **SHA-256 of the raw token** — a
database read yields **no usable credential**. Both existing checksums **byte-identical**.

### ⛔ Stop-gate 4 fired mid-pass, and was honoured

Switching `current_identity` broke **98 existing tests at once** — the whole composition-root suite authenticated
through the stub being removed, which **no approved plan predicted**. Halted and reported rather than pushed
through. The authorized migration then changed **0 tests, 0 assertions**: four fixtures gained one override, the
role constants moved to `{"Cookie": …}` while staying `headers=` dicts (**~90 call sites unedited**), and three
inline app builds got the same line. **Sessions are seeded, not obtained via R8** — Argon2 is deliberately slow,
endpoint logins would couple 98 route tests to R8, and the login path is proven once in `test_auth_routes.py`.

### ⚑ Two imprecise claims of my own, caught and corrected

1. **The auth-requirement grep miss** — I told the user *"NO test asserts that every route requires
   authentication"* while confirming the amendment. **`test_auth_stub.py:40` was literally named
   `test_every_wired_route_requires_authentication`.** The conclusion survived (hardcoded 3-path list, not the
   route table), but the wording was **wrong and load-bearing at a sign-off gate**.
2. **The vacuous-test docstring overclaim** — my first fix claimed the blank-cookie test isolates the `.strip()`
   guard. **It does not**; a blank token would also miss the store. Corrected to pin the **behaviour**, not a line.

### The vacuity fix

Four tests had gone green **for the wrong reason**. All re-expressed against the cookie; one was an **exact
duplicate** and was **consolidated with its rationale recorded, not deleted silently**; the dead **GHOST-1 seed
now has a consumer** and a new **ORPHAN-1** session covers *"resolves but has no `app_user` row"*.
**`test_every_wired_route_requires_authentication`'s name DID overpromise** — renamed and **widened from a
hardcoded 3 to all 8 authenticated routes**, derived from the declared inventory, R8's exclusion **asserted not
assumed**. **Non-vacuity proven**: a synthetic no-auth route returns 200, which the loop flags.

### ⛔ #25 closes NARROWED, not DISCHARGED — stated in advance and honoured

The mechanism is **structurally complete and tier-U-proven**, but **no live Postgres run has occurred here** (no
Docker, no database), so **no real login against a real database has been confirmed end-to-end**. On the **#18 /
#8 precedent**, DISCHARGED would overclaim exactly the confirmation not performed. Full discharge requires a real
login against real Postgres, driving R2–R7 with that session, and a commit whose `AuditRecord.underwriter_id` is
the authenticated user.

**HOLDS**: **A-4 verified AST-identical to HEAD** · **`app.test.jsx:261` intact, frontend untouched** · U15's
`0001`/`0002` untouched · U16's `Settings` **still six fields** · **`auth_rbac` and `admin_cli` untouched** ·
`backend/scripts/`, `llm_client.py`, tier-B untouched · `not_wired.py` not renamed (#13 open) · `audit_store`
gap untouched (**5 stays 5**) · **NO COMMIT**.

**Register: 25 tracked — 17 open · 3 discharged · 5 narrowed (#3, #8, #18, #19, and now #25).**

---

## REGISTER #26 `CRLF-CHECKSUM-MANIFEST-FRAGILE` OPENED — pre-existing, NOT fixed (2026-07-25)

Surfaced by verifying each login/signup commit at its own SHA in isolated worktrees rather than trusting a
working-tree run. Every fresh checkout shows **two checksum failures the working tree does not**:
`test_migname.py::test_verify_checksums_passes_against_u24s_own_manifest` and
`test_migration_checksum.py::test_committed_manifest_matches_committed_migrations`.

**Cause, proven by bytes**: `core.autocrlf=true` with **no `.gitattributes`**, so git rewrites `.sql` line
endings on checkout. `0001_initial_schema.sql` — manifest `848f6eec…`; working tree `848f6eec…` (0 CRLF);
fresh checkout `14fdf782…` (57 CRLF). Same file, same commit, two digests.

**PREDATES this pass** — reproduced at `ceb32f6` (Phase A close), where both fail identically. **Affects U24s own
manifest**, never touched here; `0003_auth.sql` inherits the property identically. **CI misses it** because Linux
defaults to `autocrlf=false`.

⚑ **Same defect shape as `test_the_module_imports_without_the_sdk_installed`** (fixed earlier this session at
`86e2725`) — an **environment-dependent** test outcome rather than a property-dependent one. Second instance in
one session; kinship recorded so the pattern is recognised rather than re-diagnosed.

**Fix named, NOT applied**: a `.gitattributes` pinning line endings. Repo-wide, needs its own authorization (the
#24 precedent), and must first decide re-compute-manifests vs normalise-checkout.

**Follow-up correction, not a history rewrite**: commit `d6a6876`s *"verified programmatically"* claim is true but
under-qualified — verified against **this working trees bytes**, not universally.

**Register now 26 tracked — 18 open / 3 discharged / 5 narrowed (#3, #8, #18, #19, #25).**
Suite unchanged: **1610 / 0 / 43 / 5 / 99.70
---

## REGISTER #26 `CRLF-CHECKSUM-MANIFEST-FRAGILE` OPENED — pre-existing, NOT fixed (2026-07-25)

Surfaced by verifying each login/signup commit **at its own SHA in isolated worktrees** rather than trusting a
working-tree run. Every fresh checkout shows **two checksum failures the working tree does not**:
`test_migname.py::test_verify_checksums_passes_against_u24s_own_manifest` and
`test_migration_checksum.py::test_committed_manifest_matches_committed_migrations`.

**Cause, proven by bytes**: `core.autocrlf=true` with **no `.gitattributes`**, so git rewrites `.sql` line
endings on checkout. `0001_initial_schema.sql` — manifest `848f6eec…`; working tree `848f6eec…` (**0** CRLF);
fresh checkout `14fdf782…` (**57** CRLF). Same file, same commit, two digests.

**PREDATES this pass** — reproduced at `ceb32f6` (the Phase A close), where both fail identically. **Affects
U24's own manifest**, which this pass never touched; `0003_auth.sql` inherits the property **identically**.
**CI misses it** because Linux defaults to `autocrlf=false`.

⚑ **Why it matters**: these manifests are the integrity mechanism for the **frozen** migrations. A guard that
passes or fails by **checkout platform** rather than **file contents** fails in both directions — it can go red
on an untouched file, and its passing on one machine says nothing about another.

⚑ **Same defect shape as `test_the_module_imports_without_the_sdk_installed`** (fixed earlier this session at
`86e2725`) — an **environment-dependent** test outcome rather than a property-dependent one. **Second instance
in a single session**; the kinship is recorded so the pattern is recognised on its third appearance rather than
re-diagnosed from scratch.

**Fix named, explicitly NOT applied**: a `.gitattributes` pinning line endings (`*.sql text eol=lf`, or
`* text=auto eol=lf`). Repo-wide, so it needs its **own authorization** (the **#24** precedent), and must first
decide **re-compute the manifests** vs **normalise the checkout** — different remedies, different blast radii.

**Follow-up correction, not a history rewrite**: commit `d6a6876`'s *"verified programmatically"* claim is true
but **under-qualified** — verified against **this working tree's bytes**, not universally. Recorded in the
register entry; the commit message stands as written.

**Register now 26 tracked — 18 open · 3 discharged (#2 partly, #20, #24) · 5 narrowed (#3, #8, #18, #19, #25).**

**HOLDS**: no `.gitattributes` · no manifest recomputed · no `.sql` touched · no test edited · no git history
rewritten. Suite unchanged: **1610 / 0 / 43 / 5 / 99.70%**.

---

## ✅ REGISTER #25 `PER-4-AUTHN-UNIMPLEMENTED` — **DISCHARGED** (2026-07-26T07:37:32Z)

**The register's first NARROWED → fully DISCHARGED item.** Manual end-to-end verification by the user via `curl`
and `psql` against a **real local PostgreSQL** (~07:29–07:35 today) met, in full, the bar set publicly in advance
in `login-signup-code-gen-plan.md` §9 and commit **`5e454f2`**:

> *"a real login against a real Postgres, **driving R2–R7 with that session**, and **a commit whose
> `AuditRecord.underwriter_id` is the authenticated user**."*

### The evidence

1. Login as `demo-underwriter` → **204 + `Set-Cookie`**; `/session` resolves with **`role=underwriter`**.
2. Commit of **`REC-DEMO-0002-25a195b9`** through the session cookie →
   `{"recommendation_id":"REC-DEMO-0002-25a195b9","underwriter_id":"demo-underwriter","action":"approve","reason":null}`.
   ⚑ **`underwriter_id` was never sent by the client** (WIRE-1 §5 forbids it in the body) — it was **derived
   server-side from the session**.
3. **Direct `psql` on `audit_record`** — `decision_id 7d29fa12-…`, `underwriter_id=demo-underwriter`,
   `action=approve`: **the persisted row**, not a projection of it.
4. Negative control (a): re-commit → **409 `commit_conflict`** — register **#19**'s claim guard, live against a
   real database.
5. Negative control (b): commit with **no cookie** → **401, not 403** — the commit path is gated by
   **authentication**, not merely authorization.

⚑ **The strongest artifact**: the same query surfaced a **2026-07-23** row (`f67dc658-…`, DEMO-0001) with
**`underwriter_id=demo-user-1`**, written under the old **`X-User-Id` header** stub. **The forgeable mechanism
and its replacement now sit side by side in one table** — the audit trail records its own repair. No test tier
could have produced that.

### Why a full discharge, not another narrowing

Measured against #25's **own recorded wording**: its subject (*"PER-4 … was never built"*) is satisfied; its
severity rationale (*"the audit trail's actor field currently has no authentication behind it"*) is **refuted on
the persisted row**; its blocking claim is discharged; **US-PLAT-1's Gherkin `Given`** now holds.

⚑ **Discharged on evidence, not inertia.** One turn earlier this item was **kept** NARROWED on a walkthrough that
omitted exactly this step. **A bar that only ratchets one way is not a bar** — holding it then requires releasing
it now.

⚑ **New outcome shape**: #20/#24 were discharged without ever being narrowed, #2 is only *partly* discharged, and
#3/#8/#18/#19 remain narrowed. **#25 proves a narrowing is not terminal** — it is an honest interim label that
sufficient later evidence can retire.

### ⛔ What the discharge does NOT claim — named, none a residual of #25

**(1) There is no login UI** — no browser login journey exists (this pass delivered routes, not a form; Q13(a)
kept the login client out of `seams.js`). **Whether that warrants its own register item is the user's call; none
is opened here.** **(2)** The **`SESSION_COOKIE_SECURE=false`** opt-out has never been exercised in a real run.
**(3) `httpTransport.js`** is unproven against a real browser. **(4) `test_migration_apply.py:56`** remains
Docker-gated and unrun — though the walkthrough necessarily applied `0003_auth.sql` for login to work at all.
**(5) #26** untouched and open.

**Register now 26 tracked — 18 open · 4 discharged (#2 partly, #20, #24, #25) · 4 narrowed (#3, #8, #18, #19).**

**HOLDS**: no code touched · no test edited or run · no migration touched · **no commit** — the login/signup
implementation and the `__main__.py` fix remain uncommitted in the working tree, exactly as left. Suite unchanged
at **1615 / 0 / 43 / 5 / 99.63%**.
