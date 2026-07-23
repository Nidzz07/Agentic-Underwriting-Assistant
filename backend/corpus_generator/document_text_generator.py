"""C6 ``DocumentTextGenerator`` — build-time document prose via the injected LLM seam.

Drives the **injected** ``memo_agent_core.provider.LLMClient`` seam
(``generate(model, prompt, temperature) -> str``) to produce salary-slip /
bank-statement / medical-questionnaire **prose** (FR-PROV-4). The LLM produces
PROSE only — it is **never** in the label path (labels come from ``rules_engine``,
CON-BR2). ``memo_agent_core``'s ``complete()`` (XML→Pydantic memo path) is NOT
reused (Q2).

``temperature`` is fixed at the **single central constant** ``_PROSE_TEMPERATURE``
— the one central temperature REFNOTOWN-1 permits ("no temperature literal OTHER
THAN the injected seam's central one"); it is never caller-controlled / per-call.

Injected → a capturing test double drives it offline in CI (no key, no network);
the real google-genai client is wired only at the tier-B ``build.py`` entrypoint.
"""
from __future__ import annotations

from backend.intake.schema import ApplicantProfile, DocType
from backend.memo_agent_core.provider import LLMClient

#: The one central prose temperature (never a per-call / caller-controlled param).
_PROSE_TEMPERATURE = 0

_DOC_TYPES = (DocType.SALARY_SLIP, DocType.BANK_STATEMENT, DocType.MEDICAL_QUESTIONNAIRE)


class DocumentTextGenerator:
    """Injected-seam prose generator (offline-testable via a capturing double)."""

    def __init__(self, client: LLMClient, *, model: str) -> None:
        self._client = client
        self._model = model

    @staticmethod
    def _prompt(doc_type: DocType, profile: ApplicantProfile) -> str:
        """A build-authored prompt over the SYNTHETIC profile (no untrusted input)."""
        return (
            f"Write a realistic synthetic {doc_type.value.replace('_', ' ')} for a "
            f"underwriting test corpus. Applicant occupation: {profile.occupation or 'unspecified'}; "
            f"employment: {profile.employment_type.value if profile.employment_type else 'unspecified'}. "
            f"Do not include any real personal data."
        )

    def generate_for(self, profile: ApplicantProfile) -> dict[str, str]:
        """Prose per document type, keyed by the ``DocType`` value string."""
        out: dict[str, str] = {}
        for doc_type in _DOC_TYPES:
            out[doc_type.value] = self._client.generate(
                model=self._model,
                prompt=self._prompt(doc_type, profile),
                temperature=_PROSE_TEMPERATURE,   # central; not caller-controlled
            )
        return out
