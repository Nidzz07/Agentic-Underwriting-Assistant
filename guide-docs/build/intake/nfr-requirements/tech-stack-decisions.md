# Tech-Stack Decisions — `intake` + `document-sanitizer` (coupled pair)

**Stage**: BUILD → NFR Requirements (per-unit) · cluster unit 1
**Units**: U1 `intake` (SEC-2) + U2 `document-sanitizer` (SEC-1)
**Date**: 2026-07-04
**Scope**: Records the **unit-local tech choices** as decisions with rationale. Most are already
implied by the brief / frozen FD — this pins them and adds the **subprocess-isolation** decision
(NFR-INT-SEC1-SANDBOX). Exact version pins are a Code-Gen concern; the choices below are settled.

---

## 1. Decisions

| # | Decision | Choice | Rationale | Traceability |
|---|---|---|---|---|
| D1 | **Document parsing** | **pdfplumber** (PDF text/field extraction) | Typed extraction per the brief; deterministic output for a given PDF; no new dependency. | Brief §9, FR-INTAKE-2 |
| D2 | **Parse isolation** | **Subprocess-isolated, resource-bounded, killable** (memory/CPU/wall-time limits) | Untrusted PDFs are an attack surface (malformed PDFs can exploit/hang/exhaust the parser). A bounded subprocess contains a crash/hang/exploit **to the subprocess** (killed by the bound), not the main service. In-process-bounded is too weak (a parser failure takes the service down); container/microVM is overkill for a pure-logic library unit on free tier. **Scope = the untrusted-PDF parse step ONLY.** | **SEC-1** (sandbox), Brief §10 FM4, Q1=B |
| D3 | **Validation gate** | **Pydantic v2** (typed SEC-2 gate) | The frozen FD's `validate_gate` is a Pydantic v2 boundary; total-function rejection into `ApplicantProfile \| RejectedIntake`. | **SEC-2**, FR-INTAKE-2 |
| D4 | **Sanitizer implementation** | **Deterministic pattern/heuristic matching in pure Python — NO LLM** | An LLM in the sanitizer would be **non-deterministic** (breaks CON-DET-1) **and** would itself be a **new injection surface** (the very thing being defended). The pattern set is versioned/testable; the adversarial corpus `C` (NFR-INT-SEC1-NEUT) is the guard. | **SEC-1**, **CON-DET-1**, Q11 |
| D5 | **Money / threshold types** | **`Decimal`** (fixed-point) for all monetary + threshold-compared values | Exact-boundary correctness (DTI, income-multiple, BMI bands downstream); no IEEE float drift; CANON-SER serializes `Decimal`-as-string. | Q4 (FD), CON-DET-1 |
| D6 | **Runtime** | **Python 3.12 (pinned minor)** — was "3.11+", tightened at Code-Gen 2026-07-05 | **CON-DET-1 determinism**: `NFKC` output (obfuscation-normalizer) and any Unicode-sensitive behavior depend on the **Python-bundled Unicode version**, which is tied to the Python **minor**. "3.11+" is too loose — a boundary-case NFKC difference between a dev/CI runtime and the Render runtime could cause an **unexplained reproducibility failure**. Pinning ONE minor (3.12 → Unicode 15.0) across **dev / test / CI / Render** removes that drift. 3.12 is native on Render (default is 3.11.8; `.python-version` selects 3.12), and has mature wheels for the whole stack (incl. the Phase-2 ML units: scikit-learn / shap / numpy / pandas). Chosen by the user at the runtime-pin gate. | Brief §9, CON-DET-1, NFR-INT-DET-1 |
| D7 | **Serialization convention** | **Reference `audit-store`'s single CANON-SER spec (§2.1)** — do NOT re-declare | One shared serialization authority across the cluster (the audit-store / memo-agent-core fixes). The `ApplicantProfile` round-trip (NFR-INT-DET-2) uses this spec so the persisted snapshot re-derives identically on replay. | CON-DET-1, CON-AUDIT-1 |

---

## 2. Explicitly NOT chosen here (owned by other units — reference-not-own)

- **Observability stack** (Langfuse / Prometheus / Grafana) — owned by the `observability` unit
  (NFR-OBS-1/2). This unit **emits** signals only (NFR-INT-OBS).
- **Secrets management** — owned by `secrets-config` / SEC-3.
- **Persistence** (PostgreSQL, no SQLite / DATA-5) — owned by `audit-store` + `database`. This unit
  commits only to CANON-SER **serializability** (NFR-INT-DET-2), not the persistence mechanism.
- **The blocking-gate harness** — owned by `quality-gates`. This unit **authors its own unit tests**
  (TDD at Code-Gen) and **defines** its targets; `quality-gates` aggregates them as blocking gates.
- **Cloud infrastructure / deployment topology** — owned by `deploy-config` + `database`.
  **Infrastructure Design is SKIPPED for this unit** (pure-logic; the sandboxed-parsing decision D2 is
  a **security NFR**, not cloud topology).

---

## 3. No new dependencies

All choices are within the brief's stack (pdfplumber, Pydantic v2, `Decimal`, **Python 3.12 pinned** —
D6). The subprocess isolation (D2) uses the standard-library process/resource-bounding facilities —
**no new third-party dependency** is introduced by this unit.

**Runtime pin enforcement (set 2026-07-05, build-wide — first pinned at this unit for the whole build):**
- **`.python-version`** (repo root) = `3.12` — the single source of truth read by **Render** (native
  runtime selection), **pyenv** (dev), and **CI**.
- **`pyproject.toml`** `requires-python = ">=3.12,<3.13"` — metadata guard.
- **D6** (this file) — the authoritative decision + rationale.
- **Action required (env, not code):** the current dev venv is Python **3.14.4** and must be
  **recreated on 3.12** to match the pin; this cannot be done by editing files (a new interpreter must
  be installed). Until recreated, the local NFKC/Unicode version differs from the Render target.

---

*End of tech-stack-decisions.md. Testable NFR targets → `nfr-requirements.md`.*
