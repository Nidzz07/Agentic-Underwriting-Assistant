# Tech-Stack Decisions — `deploy-config` (U23, EPIC-6, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U23 `deploy-config` · EPIC-6 · **Phase 2** · **Depth**: lighter ·
**Date**: 2026-07-19.
**Built ON** the frozen FD + the eleven `NFR-DEP-*` targets — re-opening none. Answers **Q1–Q3 (all A)** + folds
**NFR-DEP-Req-Fold-1..3**.

> **HEADLINE: NO NEW DEPENDENCY.** The config-validation tooling is **`pytest` (runner) + `pyyaml` (already floored+installed) +
> stdlib `json`** — all present. `deploy-config`'s tier-U surface is **file-presence / schema-parse / structural-scan over the
> committed artifacts** (Q1-A/Q3-A), not application behavior.

---

## 1. Dependency verification (on disk, not assumed)

| Library | `requirements.txt` | Installed | Role for U23 |
|---|---|---|---|
| `pytest` (+ `Hypothesis` where a property earns it) | floored | INSTALLED | the tier-U **runner**; the sibling-unit convention |
| **`pyyaml`** | **`>=6.0.0` (floored)** | **INSTALLED (6.0.3)** | parse/validate the **YAML** config (`render.yaml`) is **well-formed** + names expected keys — **already present** (used for the YAML rulebook), **no new dependency** |
| stdlib `json` | — | stdlib | parse/validate the **JSON** config (`vercel.json`) is well-formed |
| stdlib `ast` / `pathlib` | — | stdlib | the structural/path scans (NOEDIT-1, ROUTES-1, SCOPE-1) + the secret-value/token scans (SEC3-1, FREETIER-1, DOC-1) |

**`requirements.txt` is NOT edited.** U23 adds **no** library.

## 2. Decisions (DEP-D1..DEP-D8)

- **DEP-D1 — pytest is the RUNNER, not the tooth-shape** (Q1-A): the assertions **read committed files**, they do not exercise
  application behavior. `deploy-config` is a **declarative** unit — config files + a deploy doc.
- **DEP-D2 — YAML validated with the already-present `pyyaml`; JSON with stdlib `json`**: `render.yaml` parses cleanly and names the
  expected keys (service, start command, plan, env); `vercel.json` parses cleanly and names the build/output keys. **No new
  dependency** — contrast prior units' *"no new dependency"* headline; here it holds **even for the config parser** because `pyyaml`
  was floored for the rulebook.
- **DEP-D3 — structural/path scans reuse the build-wide `ast`/`pathlib` discipline** (NOEDIT-1, ROUTES-1, SCOPE-1): the same AST/path
  mechanism every prior unit used, now over U23's deliverables + a **frozen-tree path check** + the **in-process `app.openapi()`
  route introspection** (no live server, Req-Fold-1).
- **DEP-D4 — secret-value + config-token scans are text/regex over committed artifacts** (SEC3-1, FREETIER-1): a secret-value pattern
  scan (SEC3-1) + a plan-token scan (FREETIER-1), **each with a detector self-test** (Req-Fold-3).
- **DEP-D5 — DOC-1 is a checklist-completeness scan over explicit tokens** (Q2-A / Req-Fold-2): the deploy doc must carry each
  required marker token; the scan matches the **token set**, not any heading, so it cannot pass vacuously.
- **DEP-D6 — BUILD-1's bundle + BOOT-1's boot are deploy-time facts NAMED observed-never-gated** (Q3-A): their tier-U half is a
  **presence/reference** check; the **actual** build/boot is verified at Infrastructure Design/deploy, **not** given fabricated tier-U
  teeth.
- **DEP-D7 — no live cloud deploy at tier-U**: no Render/Vercel API call, no real build-and-push, no network, no key; validation runs
  **offline** against committed files.
- **DEP-D8 — module/layout OPEN** (FD Q5-A): U23 may need **no `backend/deploy_config/` Python package** — the deploy configs live at
  the **workspace root** (`render.yaml`/`vercel.json`/frontend build config/env manifest/deploy doc); the **test home** (where the
  scans live) is a **Code-Gen decision** (a `tests/`-style location scanning the committed deploy artifacts). Exact layout finalized
  at Infrastructure Design / Code-Gen.

## 3. `NFR-DEP-*` tier realization (summary)

| Target | Tooling |
|---|---|
| NOEDIT-1, ROUTES-1, SCOPE-1 | `ast` / `pathlib` structural + path scans (+ in-process `app.openapi()` for ROUTES-1); detector self-tests |
| SEC3-1, FREETIER-1 | text/regex value + token scans; detector self-tests |
| DOC-1 | checklist-completeness token scan; detector self-test |
| BUILD-1, BOOT-1 | presence/reference checks (config) + **named deploy-time facts** (observed-never-gated) |
| ADVISORY-1, PERF-1, SEC-1 | governance (+ a light token check for ADVISORY-1) |

## 4. Held
- **No new dependency**; `requirements.txt` NOT edited. **No frozen unit edited**; the CLOSED composition root untouched;
  **no live cloud deploy at tier-U**; **no secret VALUE** anywhere. **tier-B N/A + NOT authorized**; the **`audit_store` Docker-guard
  gap untouched** (31 skips + 5 Docker errors to stay unchanged). No other unit started; the 23-unit decomposition unchanged.
