-- 0001_case_lifecycle.sql — U24's pending (pre-commit) store (Scope B).
--
-- ⚑ NAMESPACING (BR-CASE-11 / Q2-A): numerically independent of database (U15)'s sequence.
-- The shared `applied_migrations` tracking table is keyed by the BARE FILENAME, so
-- `0001_case_lifecycle.sql` and `0001_initial_schema.sql` are DISTINCT keys and may both be
-- numbered 0001. The descriptive part carries the namespace because the runner globs
-- `[0-9][0-9][0-9][0-9]_*.sql` — a `u24_` prefix would not match.
--
-- ⚑ NO GRANTS HERE (MIGSCOPE-1 / CASE-Req-Fold-1): U24's store is reached via the
-- DATABASE_URL owner engine and grants to NO U15-owned role. That is what keeps the tier-I
-- test self-contained — it needs neither 0001_initial_schema.sql nor 0002_grants.sql applied.
--
-- DATA-5: Postgres-specific types (BYTEA, TIMESTAMPTZ-free here) so it cannot silently apply
-- on SQLite. Forward-only, immutable once published (a change is a NEW higher-numbered file).
--
-- BR-CASE-7: the two rich shapes are CANON-SER BYTEA + a content_hash, mirroring
-- 0001_initial_schema.sql's own pattern; the four version stamps are first-class scalars.

CREATE TABLE pending_application (
    application_id            VARCHAR NOT NULL,   -- PK; the case id R2/R3/R4 address
    state                     VARCHAR NOT NULL,   -- CaseState .value as varchar (no native ENUM)
    profile_canonical         BYTEA   NOT NULL,   -- ApplicantProfile as CANON-SER bytes
    profile_content_hash      VARCHAR NOT NULL,   -- sha256 over those bytes (tamper check)
    rule_results_canonical    BYTEA   NULL,       -- RuleResultReport as CANON-SER bytes
    rule_results_content_hash VARCHAR NULL,       -- sha256 over those bytes
    rulebook_version          VARCHAR NULL,       -- stamp (reproducibility)
    engine_version            VARCHAR NULL,       -- stamp (reproducibility)
    CONSTRAINT pk_pending_application PRIMARY KEY (application_id)
);

-- ⚑ Created ONLY at the `drafted` transition. Its PK is the key R5 commits by — which is why a
-- `failed` case can never reach the commit boundary (COMMITBOUND-1(c)).
CREATE TABLE pending_recommendation (
    recommendation_id VARCHAR NOT NULL,   -- PK; the key R5 commits by
    application_id    VARCHAR NOT NULL,   -- FK -> pending_application (both U24-owned)
    memo_canonical    BYTEA   NOT NULL,   -- DecisionMemo as CANON-SER bytes
    memo_hash         VARCHAR NOT NULL,   -- stamp
    model_version     VARCHAR NOT NULL,   -- stamp
    engine_version    VARCHAR NOT NULL,   -- stamp
    rulebook_version  VARCHAR NOT NULL,   -- stamp
    outlier_canonical BYTEA   NULL,       -- OutlierResult as CANON-SER bytes (advisory)
    CONSTRAINT pk_pending_recommendation PRIMARY KEY (recommendation_id),
    CONSTRAINT fk_pending_recommendation_application FOREIGN KEY (application_id)
        REFERENCES pending_application (application_id)
);

CREATE INDEX ix_pending_recommendation_application_id
    ON pending_recommendation (application_id);
