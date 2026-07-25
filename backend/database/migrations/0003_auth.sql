-- 0003_auth.sql — the authentication tables (register #25 / PER-4, WIRE1-Fold-5).
--
-- Adds credential storage and server-side sessions so that identity stops being a
-- self-asserted `X-User-Id` header. Forward-only and immutable once published: a change
-- is a NEW higher-numbered migration (BR-DB-4). 0001/0002 are NOT touched.
--
-- ⚑ OWNER-ONLY BY CONSTRUCTION — this file contains NO GRANT and NO CREATE ROLE.
-- Because it applies AFTER 0002_grants.sql, `audit_writer` and `audit_reader` already
-- exist and receive nothing here, so both tables are owner-only by default. That is the
-- ratified CORE-RATIONALE-20 posture (register #20), inherited rather than re-argued:
-- the audit roles are scoped to the COMMITTED trail and gain nothing legitimate from
-- credentials or sessions. Reached exclusively through the DATABASE_URL owner engine,
-- exactly as `app_user` is.
--
-- DATA-5 (BR-DB-6): TIMESTAMPTZ keeps the schema Postgres-specific so it cannot silently
-- apply on SQLite. SEC-3: no credential VALUES here — password hashes are written at
-- runtime by `backend/authn`, never seeded in a migration.

-- user_credential — one row per user that HAS a password. The ABSENCE of a row is a
-- legitimate state meaning "this user cannot log in" (provisioned but not activated),
-- which is why this is a separate table and not columns on the frozen `app_user`.
CREATE TABLE user_credential (
    user_id         VARCHAR      NOT NULL,   -- PK + FK -> app_user.user_id
    password_hash   VARCHAR      NOT NULL,   -- argon2id ENCODED string: algorithm + params + salt + digest
    failed_attempts INTEGER      NOT NULL,   -- consecutive failures; reset to 0 on success
    locked_until    TIMESTAMPTZ  NULL,       -- NULL = not locked
    updated_at      TIMESTAMPTZ  NOT NULL,
    CONSTRAINT pk_user_credential PRIMARY KEY (user_id),
    CONSTRAINT fk_user_credential_app_user FOREIGN KEY (user_id)
        REFERENCES app_user (user_id)
);

-- user_session — one row per issued session. Server-side, therefore REVOCABLE: a role
-- change or logout takes effect on the NEXT request rather than at token expiry, which
-- is the property a segregation-of-duties system must not trade away.
--
-- ⚑ session_id holds the SHA-256 OF THE RAW TOKEN, never the token itself. A database
-- read therefore yields no usable session credential — the same reasoning that makes
-- password_hash a hash. SHA-256 rather than argon2 is correct here because the token is
-- high-entropy CSPRNG output, not a human-chosen secret: slow hashing would buy nothing
-- and would cost latency on EVERY authenticated request.
CREATE TABLE user_session (
    session_id VARCHAR      NOT NULL,   -- PK; sha256 hex of the raw token
    user_id    VARCHAR      NOT NULL,   -- FK -> app_user.user_id
    created_at TIMESTAMPTZ  NOT NULL,
    expires_at TIMESTAMPTZ  NOT NULL,   -- absolute expiry, enforced server-side on every request
    revoked_at TIMESTAMPTZ  NULL,       -- set by R9 logout; NULL = live
    CONSTRAINT pk_user_session PRIMARY KEY (session_id),
    CONSTRAINT fk_user_session_app_user FOREIGN KEY (user_id)
        REFERENCES app_user (user_id)
);

-- Revoke-all-for-a-user and expiry sweeps read by user_id.
CREATE INDEX ix_user_session_user_id ON user_session (user_id);
