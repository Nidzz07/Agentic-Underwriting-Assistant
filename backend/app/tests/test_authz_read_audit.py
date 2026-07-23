"""INT-AUTHZ-1 — READ_AUDIT enforced on R6/R7 via the frozen auth-rbac guard (Q1-B).

This APPLIES the frozen ``PERMISSION_MATRIX`` verbatim rather than deciding to override it:
auth-rbac is the single-sourced RBAC authority and the server is always the real gate.

⚠️ THESE TESTS ENCODE A RECORDED, UNRESOLVED CONTRACT DIVERGENCE (plan §6.6).
``test_admin_is_denied_read_audit`` asserts **403 for admin**, which is what the frozen
PERMISSION_MATRIX requires — and which **contradicts WIRE-1 §3's "authenticated" (any role)**
wording for R6/R7. The divergence is TWO-SIDED, not a one-sided oversight: ui-history's frozen
BR-HIST-7 sided with WIRE-1 on the CLIENT (declining `RoleGate can="read"` precisely because it
"would cosmetically exclude admin"). So the frozen UI assumes any-authenticated while the server
now enforces READ_AUDIT.

This pass does NOT resolve that. Q1-B chose to apply the frozen policy and leave WIRE-1
un-amended, recording the tension for a future deliberate reconciliation (Option C). If that
reconciliation later lands on WIRE-1's reading instead, THIS TEST is the thing that must change
— it is deliberately written to make that consequence visible rather than silent.
"""
from __future__ import annotations

import pytest

from backend.app.tests.conftest import ADMIN, AUDITOR, UNDERWRITER
from backend.auth_rbac.roles import PERMISSION_MATRIX, READ_AUDIT, Role


class TestThePolicyIsAppliedVerbatim:
    def test_the_frozen_matrix_is_the_source_of_this_behaviour(self):
        # Not a re-declaration of the policy — a read of it. underwriter+auditor hold
        # READ_AUDIT; admin does not. The route behaviour below follows from THIS datum.
        assert READ_AUDIT in PERMISSION_MATRIX[Role.UNDERWRITER]
        assert READ_AUDIT in PERMISSION_MATRIX[Role.AUDITOR]
        assert READ_AUDIT not in PERMISSION_MATRIX[Role.ADMIN]


class TestReadAuditIsEnforcedOnTheAuditReadSurface:
    @pytest.mark.parametrize("headers", [UNDERWRITER, AUDITOR])
    def test_read_audit_holders_may_read_r6_and_r7(self, client, headers):
        assert client.get("/decisions", headers=headers).status_code == 200
        assert client.get("/decisions/DEC-1", headers=headers).status_code == 200

    @pytest.mark.parametrize("path", ["/decisions", "/decisions/DEC-1"])
    def test_admin_is_denied_read_audit(self, client, path):
        # ⚠️ RECORDED DIVERGENCE: the frozen PERMISSION_MATRIX says 403; frozen WIRE-1 §3's
        # "authenticated (any role)" implies 200. Q1-B applies the policy. UNRESOLVED.
        response = client.get(path, headers=ADMIN)
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "forbidden"

    def test_admin_authenticates_fine_it_is_authorization_that_denies(self, client):
        # The distinction matters: admin is a known, authenticated user (R1 answers 200).
        # It is READ_AUDIT specifically that denies it — a 403, never a 401.
        assert client.get("/session", headers=ADMIN).status_code == 200
        assert client.get("/decisions", headers=ADMIN).status_code == 403

    def test_the_denial_leaks_no_audit_data(self, client):
        body = client.get("/decisions", headers=ADMIN).json()
        assert "items" not in str(body)
        assert "DEC-1" not in str(body)


class TestAuthenticationPrecedesAuthorization:
    def test_an_unauthenticated_caller_is_401_not_403(self, client):
        # Fail-closed ordering: we do not disclose "forbidden" to someone we cannot identify.
        assert client.get("/decisions").status_code == 401
