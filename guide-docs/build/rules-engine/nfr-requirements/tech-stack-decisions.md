# Tech-Stack Decisions — `rules-engine` (C2)

**Stage**: BUILD → NFR Requirements (per-unit) · cluster unit 2
**Unit**: U3 `rules-engine` — deterministic rulebook engine (pure Python, **zero LLM**)
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** (build-wide, D6 from intake)
**Scope**: Records the **unit-local tech choices** as decisions with rationale. Most are implied by the
brief / frozen FD — this pins them and adds the **rulebook-canonicalization** decision
(NFR-RULES-CANON-1). Exact version pins are a Code-Gen concern; the choices below are settled. **No new
third-party dependency** is introduced by this unit.

---

## 1. Decisions

| # | Decision | Choice | Rationale | Traceability |
|---|---|---|---|---|
| RE-D1 | **Rulebook parsing** | **`pyyaml` `safe_load`** (never `load`) | The rulebook is versioned YAML (brief). `safe_load` refuses arbitrary object construction — a YAML rulebook is **data**, never code (aligns with SEC / no-code-execution). Already in the brief's stack. | Brief §9, FR-RULES-6 |
| RE-D2 | **Rule schema validation** | **Pydantic v2** validates each `Rule` **at load** | `load_rulebook` rejects malformed/adversarial rules **before** evaluation: CON-BR1 `input_fields` allowlist (demographic/unknown → reject, NFR-RULES-BR1-1) **and** operator↔threshold-shape mismatch (§2.1 → reject, NFR-RULES-SCHEMA-1). Consistent with intake's Pydantic-v2 gate. | CON-BR1, FR-RULES-3, FD §2.1/§4 |
| RE-D3 | **Numeric type** | **`Decimal`** for all thresholds + derived `dti_ratio` / `income_multiple`, via the **shared `backend/common/decimal_context`** | Exact-boundary correctness (DTI `0.40`, income-multiple ceiling, BMI bands) with **no IEEE float drift**; the **single declared context** (`ROUND_HALF_UP`, 4dp for derivations) is reused, not re-declared — one rounding authority across the build. | CON-DET-1, NFR-RULES-DEC-1, intake D5 carry-forward |
| RE-D4 | **Engine implementation** | **Pure Python, generic rule interpreter — NO LLM anywhere** | The engine interprets declarative `Rule` data uniformly (no per-rule Python); the recommendation **and** confidence originate here in pure Python. An LLM in this path would break CON-BR2 + CON-DET-1 (non-deterministic). | CON-BR2, CON-DET-1, skill (no LLM in the rules path) |
| RE-D5 | **Rulebook canonicalization / `content_hash`** | **Reference the shared CANON-SER via a rules-engine `RulebookCanonAdapter`** (see §2) | `content_hash` (NFR-RULES-AUDIT-1) needs a deterministic canonical form. Reuse the **single** CANON-SER convention (audit-store §2.1) rather than fork a parallel one — one canonicalization authority across the build. | CON-DET-1, CON-AUDIT-1, NFR-RULES-CANON-1 |
| RE-D6 | **Runtime** | **Python 3.12 (pinned minor)** | Build-wide determinism pin (NFKC/Unicode + wheel consistency across dev/test/CI/Render); `.python-version` = 3.12 + `pyproject requires-python ">=3.12,<3.13"` + intake D6. | CON-DET-1, intake D6 |

---

## 2. RE-D5 in detail — `RulebookCanonAdapter` (Sharpening 1: reference + extend, no fork, no §2.1 change)

**"Extend CANON-SER to the rule-set shapes" = an ADAPTER, not a change to the shared spec/implementation.**
The `RulebookCanonAdapter` (a rules-engine module) **normalizes the `Rulebook` into the EXISTING
`backend/common/canon_ser.py` value space**, then calls the **UNCHANGED** shared utility — exactly the
**`CanonSerAdapter` precedent** intake used for `ApplicantProfile` (`profile.model_dump()` → `canon_ser`).

**Shape → normalization (all into canon_ser's existing value space):**

| Rule-set shape | Normalized to | Under §2.1 property |
|---|---|---|
| `set`-threshold (e.g. `{smoker}`, `{self_employed, contract}`) | a **declared-sorted `list`** — sorted by **canonical string form** (a deterministic total order) | stable ordering (P1) |
| `DecimalRange {low, low_inclusive, high, high_inclusive}` | a **dict** of `Decimal` + `bool` | Decimal-as-string (P2) + canonical scalars (P3) |
| `operator` / `category` / `outcome` (enums) | their **`.value`** | canonical scalars (P3) |
| `ScalarLiteral` (for `eq`) | the **native scalar** (`Decimal` / `str` / enum-value) | P2 / P3 |
| `Decimal` thresholds | native `Decimal` | Decimal-as-string (P2) |

**Guarantees (RE-D5):**
- **No edit to `backend/common/canon_ser.py` and no change to audit-store's §2.1 spec.** The four §2.1
  properties (stable key order, `Decimal`-as-string, canonical scalars/null-explicit, no volatile
  fields) are **sufficient** to express every rule-set shape; the adapter only reduces shapes into that
  value space. **audit-store is unaffected** — it never canonicalizes a rulebook and never passes a
  `set` (its only concern is the `content_hash` string recorded on the report/tuple).
- **The `set` → sorted-`list` total order is declared deterministic** (sorted by canonical string form),
  so the **same logical set → the same canonical bytes** regardless of insertion order (NFR-RULES-CANON-1).
- **Escape hatch (logged, not silent):** if a native-`set` branch on the shared `canon_ser.py` is ever
  preferred over the adapter, that is a **conscious backward-compatible shared-code decision** (audit-store
  passes no sets, so it is non-breaking) that must be **logged** — but the adapter path is preferred
  precisely because it needs **no** shared-code change. If any future rule shape is found **not**
  expressible under the four §2.1 properties, that is **flagged as a cross-unit change needing
  coordination with audit-store (the §2.1 owner)**, never a silent extension.

---

## 3. Explicitly NOT chosen here (owned by other units — reference-not-own)

- **The CANON-SER spec + shared implementation** — owned by `audit-store` (§2.1) / lives in
  `backend/common/canon_ser.py`. This unit **references** it (via `RulebookCanonAdapter`), never edits it.
- **The single `Decimal` context** — `backend/common/decimal_context`. Referenced, not re-declared.
- **Observability stack** (Langfuse / Prometheus / Grafana) — owned by the `observability` unit. This
  unit **emits** signals only (NFR-RULES-OBS-1), via an allowlist schema that structurally excludes
  demographic content.
- **Persistence + replay orchestration** — owned by `audit-store` (`AuditStore` / `ReplayService`) +
  `database` (PostgreSQL, DATA-5). This unit owns **pure, stateless re-evaluation** (`evaluate`); it has
  no concept of "replay" and stores no state.
- **Bias-swap + reproducibility VERIFICATION** — owned by `quality-gates`. This unit **authors its own
  unit tests** and **defines** its `NFR-RULES-*` targets; `quality-gates` aggregates them as blocking gates.
- **Secrets** — owned by `secrets-config` / SEC-3.
- **Cloud infrastructure / deployment topology** — owned by `deploy-config` + `database`.
  **Infrastructure Design is expected to be SKIPPED for this unit** (pure-logic; **no untrusted parsing
  → no sandbox NFR**; no independent cloud topology) — confirmed + logged when that stage is reached.

---

## 4. No new dependencies

All choices are within the brief's stack (`pyyaml`, Pydantic v2, `Decimal`, Python 3.12) plus the
already-built shared `backend/common/` utilities (`canon_ser`, `decimal_context`). **No new third-party
dependency** is introduced by this unit. The rulebook-canonicalization adapter is rules-engine-local
code over the existing shared utility. Exact version pins are set at Code-Gen.

---

*End of tech-stack-decisions.md. Testable NFR targets → `nfr-requirements.md`.*
