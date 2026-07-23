"""READ-ONLY reconciliation for cases stranded in ``committing``. **Register #19.**

╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  THIS SCRIPT CHANGES NOTHING. It reports, and it recommends. It performs no write, opens  ║
║  no transaction, and takes no recovery action of its own — deliberately. Advancing or     ║
║  reverting a real case is an operator decision, not a script's.                           ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

**Why this exists.** Register #19's fix makes a commit two-step: claim (``drafted ->
committing``) before the frozen ``DecisionCommitService.commit()``, finalize (``committing ->
committed``) after it returns. That **eliminates duplicate ``AuditRecord`` writes** — the CAS is
serialized by Postgres on the case row — but it does **NOT** achieve cross-store atomicity:
``audit_record`` and the pending store are **two transactional boundaries on two engines**, and
merging them would require editing a frozen unit.

**So one window survives, and this script is how it is closed operationally**: if the process
crashes *between* the audit write and the finalize, the case stays in ``committing``. That state
is explicit, non-terminal and detectable — which is exactly why the two-step shape was chosen
over the alternatives.

**The determinate recovery rule** (the operator applies it; this script only reports it):

  * the ``recommendation_id`` **IS** present in ``audit_record``  -> the commit really happened;
    advance the case to ``committed``
  * the ``recommendation_id`` is **ABSENT**                        -> the commit never landed;
    revert the case to ``drafted`` so the underwriter can retry

⚑ **HOW THE AUDIT SIDE IS READ, and its honest cost.** The frozen audit surface exposes
``get(decision_id)``, ``browse(application_id)`` and ``exists_superseding(decision_id)`` — it has
**no lookup by ``recommendation_id``**. So this script calls ``browse_history(None)`` **once** and
builds a single membership set of ``recommendation_id``. **That loads the FULL decision history
into memory.** It is the accepted cost of reusing the existing frozen surface rather than adding
a method to a frozen unit, and it is acceptable **only because this is a low-volume, out-of-band
reconciliation script and not a request-path route.** Stated here rather than left implicit.

⚑ **No raw SQL, deliberately.** ``backend/scripts/`` sits outside both structural-scan roots
(``backend/case_lifecycle`` and ``backend/app``), so a hand-rolled query here would be
**structurally invisible to every guard in the build** — the same reasoning that made an ad hoc
``canon_deserialize`` the wrong call during the Scope B wiring pass.

⚑ **Engines are built from ``get_settings()`` directly**, mirroring ``seed_demo_cases.py`` — this
script does **not** import ``backend.app.dependencies``, keeping FastAPI's ``Depends`` graph out
of an out-of-band tool. The pending tables are read on the **OWNER** engine because they carry no
explicit grants (register **#20**, RESOLVED as deliberate owner-only least privilege — no grant is
invented).

Run (out of band)::

    python -m backend.scripts.reconcile_committing_cases
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Optional

import sqlalchemy as sa

from backend.audit_store.audit_service import AuditService
from backend.audit_store.pg_repository import PostgresAuditRepository
from backend.case_lifecycle.repository import PostgresCaseStore
from backend.case_lifecycle.states import CaseState
from backend.secrets_config import get_settings

#: What the operator should do — named, never performed by this script.
ADVANCE = "advance to committed (the audit record exists)"
REVERT = "revert to drafted (no audit record — the commit never landed)"


@dataclass(frozen=True)
class StrandedCase:
    """One case found in ``committing``, with the recommended action."""

    application_id: str
    recommendation_id: Optional[str]
    audit_record_exists: bool

    @property
    def recommended_action(self) -> str:
        return ADVANCE if self.audit_record_exists else REVERT


def committed_recommendation_ids(audit_service: AuditService) -> set[str]:
    """Every ``recommendation_id`` that reached ``audit_record``.

    ⚑ ONE call, ONE set — see the module docstring on the full-history cost. Building the set
    up front keeps this O(1) per stranded case instead of re-reading history per row.
    """
    return {record.recommendation_id for record in audit_service.browse_history(None)}


def find_stranded_cases(store: PostgresCaseStore, audit_service: AuditService) -> list[StrandedCase]:
    """Every case sitting in ``committing``, cross-referenced against ``audit_record``."""
    committed_ids = committed_recommendation_ids(audit_service)
    stranded: list[StrandedCase] = []
    for application_id in store.list_application_ids():
        application = store.get_application(application_id)
        if application is None or application.state is not CaseState.COMMITTING:
            continue
        recommendation = store.recommendation_for_application(application_id)
        recommendation_id = recommendation.recommendation_id if recommendation else None
        stranded.append(
            StrandedCase(
                application_id=application_id,
                recommendation_id=recommendation_id,
                audit_record_exists=recommendation_id in committed_ids,
            )
        )
    return stranded


def report(stranded: list[StrandedCase]) -> str:
    if not stranded:
        return "No cases are stranded in 'committing'. Nothing to reconcile."
    lines = [
        f"{len(stranded)} case(s) stranded in 'committing' — REVIEW REQUIRED.",
        "This script has changed nothing. Each line names the action an operator should take.",
        "",
    ]
    for case in stranded:
        lines.append(
            f"  application_id={case.application_id}  "
            f"recommendation_id={case.recommendation_id}  -> {case.recommended_action}"
        )
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)

    settings = get_settings()
    case_engine = sa.create_engine(settings.DATABASE_URL)         # owner — register #20
    audit_engine = sa.create_engine(settings.AUDIT_READER_URL)    # SELECT-only, least privilege
    try:
        stranded = find_stranded_cases(
            PostgresCaseStore(case_engine),
            AuditService(PostgresAuditRepository(audit_engine)),
        )
    finally:
        case_engine.dispose()
        audit_engine.dispose()

    print(report(stranded))
    return 0


if __name__ == "__main__":       # pragma: no cover - out-of-band entrypoint
    sys.exit(main())
