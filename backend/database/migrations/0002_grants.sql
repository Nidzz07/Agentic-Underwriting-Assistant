-- 0002_grants.sql — role-grant DDL (C2 GrantDDL), a dedicated step in the
-- migration sequence, applied AFTER 0001 (the tables must exist).
--
-- BR-DB-4/5, SEC-4/SEC-5, NFR-DB-APPEND-1:
--   audit_writer -> INSERT + SELECT only (no UPDATE, no DELETE) — the DB-role half
--                   of append-only; holds even if the service layer is bypassed.
--   audit_reader -> SELECT only (no write of any kind) — the SEC-4 read-only auditor.
--
-- SEC-3 (BR-DB-13): NO credential VALUES appear here. The passwords are the
-- placeholder tokens ${AUDIT_WRITER_PASSWORD} / ${AUDIT_READER_PASSWORD} ONLY; the
-- migration_runner substitutes them from os.environ at execution time and NEVER logs
-- the rendered SQL. MIGRATE-2's checksum hashes THIS placeholder-bearing file (stable
-- across environments; an edited grant is still caught; the secret lives outside the
-- checksummed content).

CREATE ROLE audit_writer LOGIN PASSWORD '${AUDIT_WRITER_PASSWORD}';
GRANT INSERT, SELECT ON audit_record, applicant_profile_snapshot TO audit_writer;

CREATE ROLE audit_reader LOGIN PASSWORD '${AUDIT_READER_PASSWORD}';
GRANT SELECT ON audit_record, applicant_profile_snapshot TO audit_reader;
