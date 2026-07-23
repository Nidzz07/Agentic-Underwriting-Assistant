-- 0001_initial_schema.sql — the Phase-1 production schema (C1 MigrationSequence).
--
-- The SOLE authoritative schema for the co-located audit tables, column-for-column
-- with backend/audit_store/pg_repository.py (18/18 verified at the ambiguity-check),
-- plus the app_user foundational skeleton (open role).
--
-- DATA-5 (BR-DB-6): Postgres-specific types (BYTEA, TIMESTAMPTZ) so the schema
-- cannot silently apply on SQLite. Co-location (BR-DB-7): one database, one schema.
-- SEC-3: no credentials here (grants live in 0002_grants.sql). Forward-only,
-- immutable once published (a change is a NEW higher-numbered migration, BR-DB-4).

-- audit_record — one row per committed decision (the CON-AUDIT-1 6-tuple + the
-- CON-BR4 commit linkage + the OOS-7 seam). 14 columns; append-only (BR-DB-4).
CREATE TABLE audit_record (
    decision_id            VARCHAR      NOT NULL,   -- PK; system-generated committed-decision id (OOS-7 seam key)
    application_id         VARCHAR      NOT NULL,   -- the case id (intake); browse-by-application (indexed below)
    recommendation_id      VARCHAR      NOT NULL,   -- the committed pending recommendation
    rulebook_version       VARCHAR      NOT NULL,   -- 6-tuple; semver replay load key
    rule_results           BYTEA        NOT NULL,   -- 6-tuple; RuleResultReport as opaque CANON-SER bytes (BR-DB-10)
    "timestamp"            TIMESTAMPTZ  NOT NULL,   -- 6-tuple; commit wall-clock (excluded from replay equality)
    model_version          VARCHAR      NOT NULL,   -- 6-tuple; memo LLM/provider version
    memo_hash              VARCHAR      NOT NULL,   -- 6-tuple; committed-memo integrity hash
    engine_version         VARCHAR      NOT NULL,   -- 6-tuple; rules-engine git SHA (forensic)
    underwriter_id         VARCHAR      NOT NULL,   -- WHO (CON-BR4); logical ref to app_user, NOT a DB FK in P1 (BR-DB-11)
    action                 VARCHAR      NOT NULL,   -- WHAT; CommitAction .value string, not a native ENUM (BR-DB-9)
    reason                 VARCHAR      NULL,        -- WHY; mandatory-on-override enforced at the service gate (nullable here)
    status                 VARCHAR      NOT NULL,   -- OOS-7 seam; active/superseded as varchar (BR-DB-8/9); app always writes it
    supersedes_decision_id VARCHAR      NULL,        -- OOS-7 seam; self-reference for a Phase-3 superseding row (null in P1/2)
    CONSTRAINT pk_audit_record PRIMARY KEY (decision_id)
);

-- browse-by-application (matches pg_repository.audit_record.application_id index=True)
CREATE INDEX ix_audit_record_application_id ON audit_record (application_id);

-- applicant_profile_snapshot — the persisted original ApplicantProfile (CANON-SER
-- bytes), a co-located child keyed by decision_id (PK + FK). Co-location is what
-- makes audit-store's single-transaction ATOMIC-1 two-row write valid (BR-DB-2/7).
CREATE TABLE applicant_profile_snapshot (
    decision_id       VARCHAR  NOT NULL,   -- PK + FK -> audit_record.decision_id
    application_id    VARCHAR  NOT NULL,   -- the case id (denormalized for direct lookup)
    profile_canonical BYTEA    NOT NULL,   -- original ApplicantProfile as opaque CANON-SER bytes (BR-DB-10)
    content_hash      VARCHAR  NOT NULL,   -- sha256 of the canonical bytes (pre-replay tamper check)
    CONSTRAINT pk_applicant_profile_snapshot PRIMARY KEY (decision_id),
    CONSTRAINT fk_snapshot_audit FOREIGN KEY (decision_id)
        REFERENCES audit_record (decision_id)
);

-- app_user — the auth-rbac FOUNDATIONAL SKELETON (BR-DB-12). Identity + an OPEN
-- role dimension. NO closing CHECK on role: novel values (e.g. 'admin') must insert
-- without a breaking migration (SCOPE-1). auth-rbac's own FD closes/extends the set.
CREATE TABLE app_user (
    user_id VARCHAR NOT NULL,   -- PK; stable user identifier
    subject VARCHAR NOT NULL,   -- OIDC-ready subject/issuer seam (external identity binding)
    role    VARCHAR NOT NULL,   -- OPEN role dimension; Phase-1 known values underwriter/auditor; NO closed enum (BR-DB-12)
    CONSTRAINT pk_app_user PRIMARY KEY (user_id),
    CONSTRAINT uq_app_user_subject UNIQUE (subject)
);
