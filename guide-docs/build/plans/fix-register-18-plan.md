# Register Item #18 — `NO-PRODUCTION-LLMCLIENT` (B4) · SCOPING PLAN

**Stage**: POST-BUILD → register-item remediation · the **second** item taken up after **SCOPE B CLOSED**
(the first was **#19**, closed as NARROWED at 2026-07-21T15:11:53Z).
**Status**: 🟡 **SCOPING / PLANNING ONLY — NO CODE GENERATED.** Stopped at the plan-file gate.
**Date**: 2026-07-21T15:24:19Z
**Origin**: register item **#18**, opened by the **Scope B in-place composition-root wiring pass** as blocker **B4**
(`guide-docs/build/composition-root/scope-b-wiring-summary.md` §2 B4, §4, §5) and deliberately **not fixed there**
under **Q12-C** — a disclosed deterministic offline double was used instead.
**Owner recorded in the register**: **composition / `deploy-config` (secrets).**

**Register severity, quoted, not softened**: *"**Non-blocking** for the wired API layer and the seeded demo.
**⛔ BLOCKING for any real memo generation** — no genuine LLM-drafted memo can be produced by this system today."*

The register additionally records the meta-failure, and it is worth keeping in view for this pass:
*"⚑ **The build closed with a deferred seam absent from its own register** — the same failure mode as the
`CaseSeams` blocker."*

---

## 0. What this document is and is not

* **IS**: a scoping plan. Ground truth, the design tensions, and **eight open questions** for the user to answer.
* **IS NOT**: a fix, a design, or an authorization. **No code is generated. No unit is reopened.** Whether
  `memo_extensions` is reopened at all is **Q2**, and the answer is the user's.

**Every `[Answer]` tag below is BLANK. None is pre-filled.** Recommendations are given where grounded and are
explicitly marked as recommendations, never as decisions.

⚑ This item is **qualitatively unlike every prior unit in this build.** All 23 original units plus U24 were designed
to run with **zero live external calls at tier-U by construction**. Discharging #18 creates the **first code path in
the entire repository capable of spending real money.** Q5 treats that as a first-class design decision, not an
afterthought.

---

## 1. Ground truth — re-established from disk, not from any summary

Five checkpoints were re-verified against the actual current files. **Four confirm the gap exactly as disclosed.
One material divergence from the task brief was found and is reported in §1.6 rather than absorbed.**

### 1.1 `backend/memo_agent_core/provider.py` — the frozen seam — ✅ CONFIRMED

```python
@runtime_checkable
class LLMClient(Protocol):
    """The minimal Gemini-SDK-shaped seam ``GeminiAdapter`` drives. The real
    google-genai client is wrapped to this at composition (deploy-config/secrets);
    a capturing test double implements it offline (no network, no key)."""

    def generate(self, *, model: str, prompt: str, temperature: float) -> str: ...
```
*(`provider.py:36-42`)*

| Property | On disk |
|---|---|
| Method count | **one** — `generate` |
| Parameters | **keyword-only**: `model: str`, `prompt: str`, `temperature: float` |
| Return | **`str`** — raw XML, parsed by `GeminiAdapter._parse_xml`, not by the client |
| Thinking channel | ❌ **none** — this is exactly why U19 defined its own seam (§1.4) |
| Async | ❌ **synchronous** |
| Error contract | ❌ **unspecified** — no declared exception type. **Bears on Q7 and on retry behaviour.** |

**The docstring names its own unfilled deferral verbatim**: *"The real google-genai client is wrapped to this at
composition (deploy-config/secrets)."* **Composition closed without supplying it.** The module docstring (L11-13)
repeats the same promise. **This is the root cause location of #18.**

> ⚑ **The Protocol is `@runtime_checkable`.** A production implementation needs **no inheritance and no import of
> the Protocol** — structural conformance suffices. This matters for Q2: an adapter can satisfy the seam **without
> `memo_agent_core` knowing it exists**, which is the direction the build's dependency edges already run.

### 1.2 `GeminiAdapter` — the real consumer, already complete — ✅ CONFIRMED

`provider.py:45-71`. It is **not** a stub. It already performs:
* central `temperature=_PRODUCTION_TEMPERATURE` (`=0`, L26) on every call — **never caller-controlled**;
* the XML → `MemoDraftOutput` parse;
* `model_version` exposure via a property.

**It takes `client: LLMClient` as a constructor argument and is otherwise finished.** The missing piece is
**exactly one object**: something satisfying `generate(*, model, prompt, temperature) -> str` against the live API.

### 1.3 Every `LLMClient` implementation on disk — ✅ CONFIRMED, ZERO PRODUCTION

Re-running the original gap grep (`LLMClient` × `genai` across `backend/`) returns **four implementations, none
production-usable**:

| Location | What it is | Usable in production? |
|---|---|---|
| `corpus_generator/tests/conftest.py:23` `CapturingLLMClient` | offline capturing double | ❌ test double |
| `memo_agent_core/tests/test_provider.py:35` | offline capturing double | ❌ test double |
| `scripts/seed_demo_cases.py:71` `_OfflineLLMClient` | the **Q12-C** disclosed synthetic | ❌ **explicitly not** |
| `corpus_generator/build.py:28` `_GeminiLLMClient` | ⚑ **the ONE real adapter** | ⚠️ **tier-B entrypoint; tier-B NOT authorized** |

**The gap stands exactly as described. Nothing on disk contradicts it.**

### 1.4 ⚑ There are **TWO** distinct client seams — this is the divergence (see §1.6)

| Seam | Defined in | Signature | Adapters driving it |
|---|---|---|---|
| **`LLMClient`** (frozen, U4) | `memo_agent_core/provider.py:37` | `generate(*, model, prompt, temperature) -> str` | **`GeminiAdapter`** *(in `memo_agent_core`)* |
| **`ThinkingLLMClient`** (U19-local) | `memo_extensions/provider_secondary.py:34` | `generate(*, model, prompt, temperature, thinking) -> str` | `ClaudeAdapter`, `OllamaAdapter` *(both in `memo_extensions`)* |

`provider_secondary.py`'s own docstring (L4-11) states the reason in full: *"the frozen `memo_agent_core.LLMClient`
seam is `generate(*, model, prompt, temperature) -> str` — **three kwargs, no thinking channel** — and is U4's
Gemini path, left completely UNTOUCHED. U19's new adapters need a thinking channel that seam cannot carry, so U19
defines its OWN thinking-aware client seam here."*

**Consequence for this pass:** a **Gemini** production client targets the **`LLMClient`** seam, which is
`memo_agent_core`'s. It is **not** the seam `memo_extensions`' two adapters drive. **`memo_extensions` is not the
natural home merely because "the adapters live there" — the adapters there drive a different seam.**

### 1.5 `secrets_config` — the SEC-3 path already exists — ✅ CONFIRMED, better than assumed

`secrets_config/settings.py:38` — **`GEMINI_API_KEY: str` is already a required Phase-1 field**, with:
* **no default** → missing var raises *"field required"*;
* a non-empty validator (L47-52) → whitespace-only rejected;
* both surfacing as **one `ValidationError` at `Settings()` construction** — **BR-SEC-1 fail-closed**;
* `get_settings()` is a **plain factory, no cache** (L55-59) — *"construction stays a pure, deterministic
  validation step (DET-1); the composition root holds the single instance."*

`.env.example` already carries `GEMINI_API_KEY=CHANGE_ME` under *"Phase-1 REQUIRED (all six; validated at
construction)"*. `corpus_generator/build.py:62-66` already demonstrates the correct consumption pattern with the
comment *"SEC-3: the key is read via secrets-config, never a literal here."*

> ⚑ **Q3 is therefore substantially SETTLED BY DISK.** The plan says so rather than manufacturing an open
> question. What genuinely remains open in Q3 is narrower than the brief assumed — see Q3.

### 1.6 ⚑ THE DIVERGENCE — reported, not absorbed

**The task brief states**: *"backend/memo_extensions/ — the provider adapters (ClaudeAdapter, OllamaAdapter,
GeminiAdapter if present) and how temperature=0 is centrally fixed inside them, since any new production LLMClient
must slot into this existing seam without editing it."*

**On disk this is not the layout.**

1. **`GeminiAdapter` is NOT in `memo_extensions/`.** It is in `memo_agent_core/provider.py:45` — a **frozen-23 P1
   unit**. `memo_extensions/` contains exactly four modules (`borderline_router`, `mcp_tools`,
   `provider_secondary`, `provider_showcase`), and its `__init__.py` pins that: *"Three axes, four frozen modules
   (`unit-of-work.md:70-71`), **NO fifth**."*
2. **`temperature=0` is not centrally fixed in one place.** It is fixed **twice, independently** — once at
   `memo_agent_core/provider.py:26` for the Gemini path, once at `memo_extensions/provider_secondary.py:30` for
   the Claude/Ollama path. Both are module-private constants named `_PRODUCTION_TEMPERATURE`.
3. **`GeminiAdapter` is not a test double.** It is the finished real adapter, missing only its client.

**Why this matters and is not pedantry:** the brief's Q2 framing presumed `memo_extensions` was the established
home for Gemini-seam adapters and that placing the new client there would be the low-friction choice. **On the real
layout, `memo_extensions` is arguably the *least* natural home** — its `__init__.py` forbids a fifth module, and
its two adapters drive a seam the new client does not implement. **Q2 has been rewritten around the actual
layout.** Adding a fifth module to `memo_extensions` would be a **reopening with a contradiction to justify**, not
a convenience.

### 1.7 `scripts/seed_demo_cases.py` — the integration point — ✅ CONFIRMED

`_SeedSeams.__init__` (L115-124):

```python
self._orchestrator = LangGraphOrchestrator(
    GeminiAdapter(_OfflineLLMClient(), model=OFFLINE_MODEL_VERSION),
    rulebook=self._rulebook,
    model_version=OFFLINE_MODEL_VERSION,
)
```

**The substitution point is exactly ONE constructor argument** — `_OfflineLLMClient()` → a real client. Everything
else in `_SeedSeams` is already genuine (the docstring at L106-113 is accurate: *"Every unit here is REAL [...] The
ONLY substitution is the LLM client"*).

> ### ⚑ FIND — the model-id / version-stamp conflation
> `OFFLINE_MODEL_VERSION = "OFFLINE-DOUBLE-NOT-A-REAL-LLM"` is passed to **BOTH**
> `GeminiAdapter(model=...)` — the **model id sent to the API** — and `LangGraphOrchestrator(model_version=...)` —
> the **audit version stamp** (`audit_store/record_schema.py:50`, `case_lifecycle/schemas.py:58`).
>
> Harmless while offline (the double ignores `model`). **With a real client it breaks immediately**: that string is
> not a valid Gemini model id. A real path must **separate them** — e.g. `model="gemini-2.5-flash"` (the
> `GeminiAdapter` default, `provider.py:49`) and a distinct, meaningful `model_version` stamp. **Bears directly on
> Q6** — the stamp is a reproducibility-invariant field, not a label.

### 1.8 Dependency state — ✅ CONFIRMED, mismatch intact

| File | Line | Declares / imports |
|---|---|---|
| `requirements.txt` | 8 | `google-generativeai>=0.8.0` — the **LEGACY** SDK |
| `corpus_generator/build.py` | 32 | `from google import genai` — the **NEW** `google-genai` SDK |
| `corpus_generator/build.py` | 37 | `from google.genai import types` — likewise |
| `pyproject.toml` | 100 | *comment only*: *"live google-genai LLMClient"* |
| anywhere | — | ❌ **`google-genai` is declared as a dependency NOWHERE** |

`outlier_model/tests/test_advisory_only.py:14` scans for **both** names (`"google.generativeai"`, `"google.genai"`)
in its no-LLM-in-the-deterministic-path assertion — so the **advisory-only scan already anticipates either SDK**
and will not need amendment for a name change. *(Verified: that test guards `outlier_model` only; it does not
constrain where a Gemini client may live.)*

**Net**: installing current `requirements.txt` and running `build.py` **ImportErrors**. The mismatch is real,
unchanged since disclosure, and **must be resolved by Q1 before any adapter can be written.**

---

## 2. The shape of the problem

Discharging #18 requires **exactly one object** — a class satisfying
`generate(*, model: str, prompt: str, temperature: float) -> str` against the live Gemini API. The code is perhaps
fifteen lines; `corpus_generator/build.py:28-44` already demonstrates it working.

**The code is the easy part. Every hard part of this item is a decision, not an implementation:**

| Tension | Why it is not mine to resolve |
|---|---|
| **Which SDK** | A dependency change to a BFSI build's manifest. Also determines whether `build.py`'s existing import is legitimized or orphaned. |
| **Where it lives** | Every candidate location costs something: a frozen-unit reopening, a `__init__` contradiction, or a tier-B promotion. |
| **Spend** | **The first real-money path in the entire build.** No prior unit could spend anything. |
| **Reproducibility** | `temperature=0` does **not** make an LLM bit-reproducible across model versions. The build's reproducibility invariant was written for deterministic logic. This is a genuine, disclosable tension. |
| **Offline testability** | ~1532 tests depend on offline doubles. Nothing here may erode that. |

---

## 3. The eight open questions

> **Answer inline by filling each `[Answer]:` tag.** Multiple sub-answers are marked where they exist.
> **Nothing below is pre-filled.**

---

### Q1 — Which SDK, and the exact dependency change

**The tension**: `requirements.txt` declares `google-generativeai` (legacy); all code imports `google-genai` (new).
These are **different distributions** installing **different top-level packages** (`google.generativeai` vs
`google.genai`). One of them must go.

**Does the frozen Protocol imply one?** ⚑ **No — and this should be stated plainly rather than over-read.** The
seam is `generate(*, model, prompt, temperature) -> str` — deliberately minimal and SDK-agnostic. **Both SDKs can
satisfy it.** The Protocol constrains the *adapter's* surface, not the SDK behind it. What *does* point to
`google-genai` is that **every line of import code already written in this repo targets it**
(`build.py:32,37`), and `provider.py`'s own docstring names *"the real google-genai client"* twice (L11, L39).

**Grounded SDK facts**: `google-generativeai` is the **legacy** Python SDK; Google's unified successor is
**`google-genai`**, which is the actively maintained SDK and the one Google's own current documentation targets.
The legacy package has been in a deprecation posture, with new model and feature support landing in `google-genai`
only. Building new production code against the legacy SDK in 2026 means **starting on a dead dependency**.

**Options**:

* **(a) Adopt `google-genai`; REMOVE `google-generativeai`.** One line replaced in `requirements.txt`:
  `google-generativeai>=0.8.0` → `google-genai>=1.0.0` (exact floor to be pinned at code-gen). Legitimizes
  `build.py`'s existing imports. **Nothing in the repo imports the legacy package** — verified, so removal breaks
  nothing.
* **(b) Adopt `google-genai`; KEEP `google-generativeai` as well.** Both declared. Avoids any chance of an unknown
  transitive need. **Cost**: a knowingly-dead dependency retained in a BFSI manifest with nothing importing it —
  audit noise, and it contradicts the very disclosure #18 makes.
* **(c) Adopt the legacy `google-generativeai`; rewrite `build.py`'s imports to match.** Honors the manifest as
  written. **Cost**: edits a tier-B module this pass has not authorized, and commits new production code to a
  deprecated SDK. **Not recommended.**
* **(d) Neither — defer the dependency decision and write the adapter against a lazily-imported client the caller
  supplies.** **Cost**: does not actually discharge #18; the system still cannot make a real call out of the box.

**Recommendation (grounded)**: **(a)**. It is the only option that leaves the repo *self-consistent* — the manifest
matching the imports, one maintained SDK, no dead declaration. It is also the smallest diff. Note that (a) makes
`corpus_generator/build.py` **importable for the first time** as a side effect; this does **not** authorize tier-B
(see the HOLDS), it merely stops the module being broken-by-manifest.

**Sub-question Q1b — version floor**: pin a **minimum** (`>=`) consistent with the rest of `requirements.txt`, or
pin **exactly** (`==`) for BFSI reproducibility of the dependency itself?
*(Note: every other line in `requirements.txt` uses `>=`. An `==` here would be the only exact pin — consistent
with reproducibility discipline, inconsistent with the file's convention. Genuinely a judgement call.)*

**[Answer]:**

**(a) — adopt `google-genai`, remove `google-generativeai` entirely.** Nothing in the repo imports the legacy package, so removal breaks nothing, and this leaves the manifest **self-consistent with what every line of existing import code already targets**.

**[Answer Q1b]:**

**>= (a minimum floor)**, consistent with every other line in `requirements.txt`'s existing convention. **Pin the exact floor at code-gen time** based on the current stable `google-genai` release.

---

### Q2 — Where the new adapter lives

⚑ **Read §1.6 first.** The brief's premise — that `memo_extensions` is the established home for Gemini-seam
adapters — **does not hold on disk**. The options below are framed against the real layout.

**The build's held convention, stated across many units**: *Protocols and their frozen definitions stay separate
from concrete implementations; concrete implementations live where they are consumed.* Also, repeatedly:
**"reference-don't-own"** and **"extend-don't-modify"**.

**Options**:

* **(a) A new module under `backend/memo_extensions/` — e.g. `provider_primary.py`.**
  * **For**: sits beside the other two concrete provider adapters; `memo_extensions` is explicitly the
    provider-axis unit.
  * **Against**: ⚑ its `__init__.py` states *"four frozen modules ... **NO fifth**"* — a fifth **directly
    contradicts a written invariant**. The two adapters there drive `ThinkingLLMClient`, **not** `LLMClient`, so
    the new module would be the odd one out. **Requires an explicit reopening of `memo_extensions` with its own
    logged rationale** (U24-reopening discipline, per the HOLDS).
* **(b) A new module under `backend/memo_agent_core/` — e.g. `provider_client.py`.**
  * **For**: it is the seam's home and `GeminiAdapter`'s home; no cross-unit edge is introduced.
  * **Against**: ⚑ **directly violates the build's own separation convention** — U4 is a frozen P1 unit whose
    whole design point was that the concrete client is **injected from outside**, deferred to composition. Putting
    it inside makes the unit own a live network+secrets dependency it was explicitly built to avoid, and would
    pull `google-genai` into a `--cov`-counted frozen tree. **Requires reopening a frozen P1 unit.**
* **(c) A new module under `backend/app/` (the composition root) — e.g. `llm_client.py`.**
  * **For**: ⚑ **this is precisely where both docstrings say it belongs** — *"wrapped to this **at composition**
    (deploy-config/secrets)"*, twice. The composition root is already the place that reads settings and assembles
    concrete dependencies. **No frozen unit is reopened at all.** `backend/app` is already `--cov`-counted, so
    coverage discipline applies without a pyproject change.
  * **Against**: the Scope B pass deliberately kept the **LLM-bearing composition out of the request path**
    (`dependencies.py:112-117`, Q3-D) — placing an LLM client module *in* `backend/app/` risks eroding that
    separation **if it were wired into `dependencies.py`**. ⚑ **Mitigation**: adding the *module* does not wire it;
    whether anything in `backend/app/` constructs it is **Q4/Q8's** decision, not this one's.
* **(d) A new small top-level module — e.g. `backend/llm_clients/gemini.py`.**
  * **For**: reopens nothing; owns exactly one concern; unambiguous name.
  * **Against**: creates a **new unit-shaped directory outside the 24-unit decomposition**, which the build has
    not done before. Needs a `--cov=` entry in `pyproject.toml`. Arguably cleanest, arguably scope creep.
* **(e) Promote / reuse `corpus_generator/build.py::_GeminiLLMClient`.**
  * **For**: the code already exists and is known-shaped.
  * **Against**: ⚑ **it is tier-B-scoped and coverage-omitted** (`pyproject.toml:104`). Importing it from a
    production path **promotes tier-B code to production status** — a real decision the HOLDS do not grant — and
    makes a production path depend on a module the manifest omits from coverage. Duplicating it instead is honest
    but leaves **two** real adapters to keep in sync.

**Recommendation (grounded)**: **(c)**, a new module in `backend/app/`. It is the **only option that reopens
nothing** and it is the location **both frozen docstrings explicitly name**. The one objection — Scope B's
keep-the-LLM-out-of-the-request-path discipline — is addressed by scope, not location: the module may exist in
`backend/app/` without `dependencies.py` ever constructing it, and whether it is constructed anywhere is Q4/Q8.
**(d) is a defensible second** if the user prefers a location with no `backend/app/` association at all.
**(a) and (b) both require reopening a frozen unit and should only be chosen if the user wants that cost paid.**

**Sub-question Q2b**: if the answer is **(a)**, do you authorize the **reopening of `memo_extensions`**, accepting
that its `__init__.py` *"NO fifth"* invariant must be amended and that amendment logged with its own rationale —
the same discipline used for all three U24 reopenings?

**[Answer]:**

**(c) — a new module under `backend/app/` (e.g. `llm_client.py`).** This is the **only option that reopens no frozen unit**, and it is the **exact location both frozen docstrings in `memo_agent_core/provider.py` already name** (*"wrapped to this at composition"*). **Adding the module does not by itself wire it into `dependencies.py` or the request path** — that remains Q4/Q8's decision, not this one's.

**[Answer Q2b]:**

**N/A — not choosing (a), so `memo_extensions` is NOT reopened.**

---

### Q3 — How the key is supplied and read

**Largely settled by disk (§1.5)** — this question is narrower than the brief assumed, and the plan reports that
rather than inventing openness. **Already true, requiring no decision**:

* ✅ `GEMINI_API_KEY` is a **required, no-default** `Settings` field with a non-empty validator
  (`secrets_config/settings.py:38,47-52`).
* ✅ `Settings()` is **fail-closed at construction** (BR-SEC-1) — a missing key raises `ValidationError` there.
* ✅ `.env.example` carries a placeholder only; `.env` is gitignored. **No key is committed.**
* ✅ The consumption pattern is demonstrated at `build.py:62-66` — *"read via secrets-config, never a literal."*

**What is genuinely open** is the **timing of the read relative to the adapter's own lifecycle**, which the
existing discipline does not settle:

* **(a) Read the key at composition and pass it to the client constructor** (the `build.py:66` pattern —
  `_GeminiLLMClient(settings.GEMINI_API_KEY)`). The SDK client is built **once**, at construction. Consistent with
  *"the composition root should call `get_settings()` once at startup and hold the instance."*
* **(b) Pass the whole `Settings` object and read `GEMINI_API_KEY` at each `generate()` call.** Picks up rotation
  without restart. **Cost**: a per-call settings read is inconsistent with the *"hold the instance"* discipline,
  and rotation-without-restart is not a stated requirement anywhere in this build.
* **(c) Read the environment directly inside the adapter (`os.environ`), bypassing `secrets_config`.**
  ⛔ **Violates SEC-3 outright. Listed only to be explicitly rejected.**

**Sub-question Q3b — fail-closed timing**: should a **missing/invalid key** fail

* **(i) at construction of the client** — mirroring the `Settings` fail-closed discipline used everywhere else, or
* **(ii) at first `generate()` call** — lazier, but a mis-configured deploy then appears as a *runtime drafting
  failure* rather than a *startup failure*?

⚑ **Note a subtlety that makes (i) nearly automatic**: because `Settings()` itself fails closed and
`GEMINI_API_KEY` is required, **a missing key already fails before any adapter code runs** — provided the adapter
is fed from `get_settings()`. (i) is therefore mostly *inherited* rather than newly built. What (i) would add is a
guard against an **empty-after-validation or structurally-invalid** key at client construction.

**Sub-question Q3c — non-disclosure guarantees**: confirm the adapter must **never** log, echo, `repr()`, or
include the key in any exception message or traceback context — and whether this should be **enforced by a test**
(e.g. asserting the key string never appears in `repr()` or in a raised exception's text) or **held by convention
and code review only**. ⚑ *Note: SDK-raised exceptions may embed request context. A test asserting our own code
never discloses is achievable; guaranteeing the SDK never does is not.* **This limit should be stated, not
over-claimed.**

**Recommendation (grounded)**: **(a)** + **(i)** + a **real test** for **(c)**, since the build has consistently
preferred enforced invariants over documented ones, and the honest scope-limit on SDK-raised exceptions should be
**disclosed in the docstring** rather than silently assumed away.

**[Answer]:**

**(a) — read the key at composition and pass it to the client constructor once**, mirroring `build.py`'s existing correct pattern.

**[Answer Q3b]:**

**(i) — fail closed at client construction.** As the plan notes, this is largely inherited for free from `Settings`' own fail-closed discipline; what (i) adds on top is a guard against a **structurally-invalid** (not just missing) key at construction time.

**[Answer Q3c]:**

**Yes, enforce with a real test** — assert the key string never appears in the adapter's own `repr()` or in any exception text our code raises. **Disclose explicitly in the docstring** that this guarantees *our code* never leaks the key, but **cannot guarantee the SDK's own exceptions never embed request context** — state the limit honestly rather than implying a stronger guarantee than can actually be delivered.

---

### Q4 — Integration with `CaseSeams` and the seed script

⚑ **The hard constraint, stated first**: **~1532 tests across this entire build depend on offline doubles being
available.** Every unit was designed to run at tier-U with **zero live external calls**. **No option here may
remove the ability to test drafting logic without a live key and real spend.** Any answer that does is wrong
regardless of its other merits.

**Options for `_OfflineLLMClient` in `scripts/seed_demo_cases.py`**:

* **(a) Replace it entirely** with the real client. Seeding always makes real calls.
  ⛔ **Removes the ability to seed a demo without a key and spend.** Contradicts the constraint above. **Not
  recommended.**
* **(b) Keep the offline double as the DEFAULT; add the real client as an explicit OPT-IN** (a CLI flag such as
  `--real-llm`, gated additionally by the Q5 environment flag). Offline stays the zero-config, zero-cost path;
  real drafting is reachable but never accidental.
* **(c) Add a separate, parallel "real" seed path** (a second script or a second seams class) leaving
  `seed_demo_cases.py` untouched. Maximum isolation; **cost**: two seed paths to keep in sync, and the existing
  script's prominent *"MEMOS ARE SYNTHETIC PLACEHOLDERS"* banner would need a sibling that says the opposite.
* **(d) Build the adapter only; wire nothing.** The seed script keeps the double unchanged. ⚑ **This is really
  Q8's answer surfacing here** — see Q8.

**Sub-question Q4b — the `model_version` stamp (§1.7's FIND)**: on the real path, `OFFLINE_MODEL_VERSION` must not
be passed as the model id. What should the two values be?

* **model id**: `"gemini-2.5-flash"` (the `GeminiAdapter` default, `provider.py:49`) or an explicit CLI argument?
* **`model_version` stamp** (the **audit** field, `record_schema.py:50`): the bare model id, or something richer
  (e.g. model id + SDK version + a resolved model build identifier if the API returns one)? **Bears on Q6.**

**Sub-question Q4c — the banner**: if **(b)**, the script's header banner and the *"⚠️ Reminder: seeded memo prose
is a placeholder"* footer (L214-216, L229) become **conditionally false**. Should the banner become
**mode-dependent** (printing a *"REAL LLM CALLS — THIS WILL SPEND MONEY"* variant when opted in), and should the
run print a **count of real calls made** at exit? *(Q5 overlaps here.)*

**Recommendation (grounded)**: **(b)**. It preserves the offline path completely — which is non-negotiable — while
making the real path reachable and honestly labelled. It also keeps the Q12-C disclosure intact and truthful for
the default path, rather than deleting a disclosure that is still accurate for how the script will usually run.

**[Answer]:**

**(b) — the offline double stays the DEFAULT; the real client is an explicit OPT-IN** (a CLI flag such as `--real-llm`), **additionally gated by the Q5 environment flag**. ⛔ **The offline path must remain fully intact and zero-config — that is NON-NEGOTIABLE** given how much of this build's test discipline depends on it.

**[Answer Q4b]:**

**model id** — an explicit, **non-floating** model id (see Q6), **not** the `GeminiAdapter` default alias. **`model_version` stamp** — per Q6b, **model id + SDK version at minimum**.

**[Answer Q4c]:**

**Yes — the banner becomes mode-dependent.** Default (offline) run keeps the existing *"MEMOS ARE SYNTHETIC PLACEHOLDERS"* banner **unchanged**. The opted-in real path prints a clearly distinct **"⚠️ REAL LLM CALLS — THIS WILL SPEND MONEY"** banner at start, and a **real-call count summary at exit**.

---

### Q5 — Cost and spend control ⚑ THE FIRST REAL-MONEY PATH IN THE BUILD

**This is not an afterthought and the plan will not treat it as one.** Every one of the 24 units was designed to
run with **zero live external calls at tier-U by construction**. Discharging #18 creates the first code path in
this repository that can **spend real money**, and it does so in a build whose entire testing culture assumes
that is impossible.

**A concrete worked risk**: `seed_demo_cases.py --cases 3` currently costs nothing. With a real client and a
mis-set flag, `--cases 500` in a loop, combined with the memo agent's **bounded citation retry**
(`MEMO_CITATION_RETRY_CAP`, `orchestrator.py`), means **each case can issue MORE THAN ONE call**. Spend is
therefore `cases × (1 + retries)` — **not** `cases`. Any cap must be expressed in **calls**, not cases.

**Candidate guardrails — select any combination**:

* **(a) A required explicit environment flag** — e.g. `ALLOW_REAL_LLM_CALLS=true` — checked at client construction;
  absent ⇒ **hard refusal to construct**. Makes accidental spend require a deliberate act.
* **(b) A hard per-run call cap** enforced **inside the client wrapper** (not the seed script), counting every
  `generate()` invocation and raising once exceeded. ⚑ **Placing it in the wrapper covers retries automatically**;
  placing it in the seed script does not.
* **(c) Log every real call made** — model id, prompt **length** (never prompt content, never the key), latency,
  and a running call count. Gives an audit trail for spend.
* **(d) A `--dry-run` mode** that resolves configuration and prints exactly what *would* be called, spending
  nothing.
* **(e) Nothing beyond the Q4 opt-in flag** — rely on the CLI flag alone.
* **(f) A hard cap on `--cases`** when the real path is active (e.g. refuse `> 10` without a further override).

**Sub-question Q5b — where the cap lives**: **inside the new client wrapper** (covers every caller and every
retry, forever) or **in the seed script** (simpler, but silently absent for any future caller)?

**Sub-question Q5c — the cap's default value**, if **(b)**: a specific number, and whether it is overridable by
argument or fixed in code.

**Recommendation (grounded)**: **(a) + (b) + (c)**, with **(b) placed in the wrapper per Q5b**. (a) prevents
accident, (b) bounds the blast radius including retries, (c) makes spend auditable — which is the same standard
this build applies to every other consequential action. **(e) alone is not recommended**: a single CLI flag is one
typo away from an unbounded loop, and this build has consistently preferred structural guarantees over care.

**[Answer]:**

**(a) + (b) + (c)** — the environment flag, the wrapper-level call cap, and per-call logging (**model id, prompt LENGTH only, latency, running count — never prompt content, never the key**).

**[Answer Q5b]:**

**Inside the client wrapper itself, NOT the seed script** — this is the only placement that automatically covers the **citation retry loop** and **any future caller**, not just today's seed script.

**[Answer Q5c]:**

**A conservative fixed default (e.g. 20 calls per process lifetime)**, **overridable** by an explicit constructor/environment argument so a deliberate larger run is possible but **never accidental**.

---

### Q6 — `temperature=0` and the reproducibility invariant

**The `temperature` half is settled by disk and is a confirmation, not a decision.** ✅ The new client **must not
set, default, or override `temperature` itself.** It receives `temperature` as a parameter and passes it through.
`GeminiAdapter` already fixes `temperature=_PRODUCTION_TEMPERATURE` (`=0`) centrally at `provider.py:26,61`, and
`complete(prompt, schema)` carries **no** temperature parameter — TEMP0-1 part ii. A client that injected its own
temperature would **silently defeat a load-bearing invariant**. *(Note `build.py:39-43` already does this
correctly — it forwards the passed value into `GenerateContentConfig(temperature=temperature)`.)*

**The genuinely open part is the reproducibility tension, and it should be disclosed rather than resolved by
assertion.**

PROJECT-BRIEF §5.1 requires *"Identical input → identical output, 100% of the time"*, and AC-1 pins
**Decision reproducibility 100%** via a **calibration test × 10 runs**. `temperature=0` was the stated mechanism.

⚑ **`temperature=0` does not make an LLM bit-reproducible.** It makes sampling greedy, which is necessary but not
sufficient. Outputs can still differ across: provider-side model updates behind a floating alias
(`gemini-2.5-flash` is such an alias), serving-stack/batching non-determinism, and tokenizer or safety-filter
changes. **This is categorically weaker than U24's CANON-SER-encoded deterministic logic, which is bit-identical
by construction.**

**What is genuinely protected regardless** — and this is the load-bearing point, worth stating plainly: the
**recommendation itself is produced by the deterministic rules engine, never by the LLM.** CON-BR2-TYPE means
`MemoDraftOutput` carries only `narrative_prose` + `cited_rule_ids` — **the model structurally cannot change the
recommendation.** So LLM non-determinism affects **memo prose wording**, not the decision. **The reproducibility
risk is real but scoped to prose, and the architecture already contains it.**

**Options for how this pass handles the tension**:

* **(a) Disclose it as a new register item** — the honest disclosure this build has consistently preferred over
  silent resolution. It would record that AC-1's 100% claim holds for the **decision path** and is **not**
  claimable bit-exactly for **memo prose** under a real LLM.
* **(b) Pin a fully-qualified, non-floating model id** (rather than the `gemini-2.5-flash` alias) so at least
  provider-side model drift is bounded, and stamp that exact id into `model_version`. **Narrows** the window;
  does not close it.
* **(c) Both (a) and (b).**
* **(d) Treat `temperature=0` as sufficient and make no disclosure.** ⛔ **Not recommended** — it would repeat
  exactly the failure mode #18 itself calls out: *"the build closed with a deferred seam absent from its own
  register."*

**Sub-question Q6b — the four version stamps**: `model_version` flows into `AuditRecord`
(`record_schema.py:50`) and `PendingRecommendation` (`case_lifecycle/schemas.py:58`). Should the real path stamp
**(i)** the bare model id, **(ii)** model id + SDK version, or **(iii)** model id + SDK version + any
provider-returned response/model build identifier? *(Richer stamps make replay diagnosis possible; the frozen
field is a plain `str`, so all three fit without a schema change.)*

**Recommendation (grounded)**: **(c)** — pin a non-floating model id **and** disclose the residual gap as a
register item. Plus **(ii)** or **(iii)** for Q6b, since a bare alias in an audit record is precisely the stamp
that makes a future replay unfalsifiable.

**[Answer]:**

**(c) — both**: pin a **fully-qualified, non-floating model id** (not the `gemini-2.5-flash` alias), **and disclose the residual reproducibility gap as its own new register item**. State plainly that **AC-1's 100% reproducibility claim holds for the DECISION path** (structurally guaranteed by CON-BR2-TYPE — the model cannot alter the recommendation) but **cannot be claimed bit-exactly for MEMO PROSE under a real LLM, even at `temperature=0`**.

**[Answer Q6b]:**

**(iii) — model id + SDK version + any provider-returned model/response build identifier, when available**, since a bare floating alias in an audit record is exactly the kind of stamp that makes a future replay attempt **unfalsifiable**. The frozen field is a plain `str`, so this fits with **no schema change**.

---

### Q7 — Test strategy

**The tier-U half is strongly precedented and is nearly a confirmation.** Every provider adapter in this build is
tested offline by injecting a capturing double **at the client seam**:
`memo_agent_core/tests/test_provider.py:35`, `memo_extensions/tests/fixtures.py:37`
(`CapturingThinkingClient`), `corpus_generator/tests/conftest.py:23` (`CapturingLLMClient`). All record the
outgoing request and return canned XML — *"no network, no key."*

But note the **new** thing here: those doubles test the **adapter** by faking the **client**. This pass builds the
**client itself**, so the double must move **one layer lower** — faking the **genai SDK object** the client wraps.

**Options for tier-U**:

* **(a) Inject the `genai` client object into our wrapper's constructor** (constructor seam), so a fake SDK object
  can be supplied in tests. Mirrors the injection discipline used everywhere else in this build.
  ⚑ **Note this changes `build.py`'s shape** — `_GeminiLLMClient(api_key)` constructs its own client internally
  and is therefore **not** unit-testable, which is part of why it is coverage-omitted.
* **(b) Monkeypatch `google.genai.Client` in tests.** Requires no constructor seam. **Cost**: patch-based tests are
  more brittle and are **not** the idiom this build has used anywhere.
* **(c) Do not unit-test the client at all; coverage-omit it** exactly like `pg_repository.py` /
  `corpus_generator/build.py`. ⚑ **Cost**: the spend cap and the key-non-disclosure guarantee from Q3c/Q5 would
  then be **untested**, which is the opposite of how this build treated every other safety-relevant invariant.
* **(d) (a) + (c) hybrid** — inject the seam and unit-test the **guardrails** (cap counting, flag refusal,
  temperature pass-through, no-key-disclosure), while omitting only the thin genuinely-network-bound line.

**Sub-question Q7b — a real-API test**: is **any** test against the live API warranted?

* **(i) None at all.** The tier-U suite plus manual out-of-band verification suffices.
* **(ii) A manual, out-of-band, explicitly-documented verification procedure** — run by a human, never collected
  by pytest (the `build.py` precedent: *"invoked manually / in a dedicated build job, never as a collected pytest
  test"*).
* **(iii) A pytest test gated behind BOTH a custom marker and the `ALLOW_REAL_LLM_CALLS` env flag**, auto-skipped
  otherwise. **⚑ Careful**: this build's `markers` are declared in `pyproject.toml` and `--strict-markers` is on,
  so a new marker means a `pyproject.toml` edit. It also creates a collected test that **can** spend money —
  precisely what the HOLDS caution against.

⚑ **HOLD CHECK**: the HOLDS state *"tier-B not authorized by this pass (a real-API test path, if any, must be
opt-in and never run by default)"*. **(iii) is permitted only if the gating is genuinely fail-closed.** **(ii)
carries no such risk at all.**

**Sub-question Q7c — the 5-errors invariant**: confirm the expectation that this pass leaves the suite at
**5 `audit_store` Docker-absence errors, unchanged and confirmed by name**, and the coverage gate
(`--cov-fail-under=90`, currently **99.87%**) held. *(If Q2 lands the adapter in `backend/app/` or
`memo_extensions/`, it lands in an already-`--cov`-counted tree and must therefore be covered — which argues
against (c).)*

**Recommendation (grounded)**: **(d)** for tier-U and **(ii)** for Q7b. (d) keeps the safety-relevant logic
genuinely tested — this build has never accepted an untested safety invariant — while (ii) gets real-API
confidence with **zero** possibility of a CI run spending money, and needs no `pyproject.toml` marker change.

**[Answer]:**

**(d) — the hybrid**: inject the SDK client object at the wrapper's constructor (a real seam, mirroring this build's injection discipline everywhere else), **unit-test the guardrails genuinely** (cap counting **including retries**, flag refusal, temperature pass-through, no-key-disclosure), and **coverage-omit only the thin, genuinely network-bound execution line** — following the `pg_repository.py`/`build.py` precedent **for that one line, not for the whole module**.

**[Answer Q7b]:**

**(ii) — a manual, out-of-band, explicitly-documented verification procedure**, run by a human, **never collected by pytest**. **No new pytest marker, no `pyproject.toml` edit, zero possibility of a CI run spending money.**

**[Answer Q7c]:**

**Confirmed** — the suite must stay at **exactly 5 `audit_store` Docker-absence errors, confirmed by name**, and the coverage gate must hold **at or above 90%** (currently **99.87%**).

---

### Q8 — Scope boundary

**The question the other seven depend on.** Is this pass:

* **(a) The adapter ONLY.** Build and test the production `LLMClient`; fix the SDK dependency; wire it **nowhere**.
  `seed_demo_cases.py` keeps `_OfflineLLMClient` untouched. **#18 becomes NARROWED** — a production client now
  *exists*, but nothing constructs it, so no real memo is produced yet. **Honest outcome; smaller blast radius;
  no spend possible on completion.**
* **(b) The adapter AND the seed-script wiring** (Q4's opt-in path). **#18 could then be genuinely DISCHARGED** —
  a real LLM-drafted memo becomes producible. ⚑ This is the **upgrade of Scope B's Q11-A claim** from
  *"exercisable after the seed script (synthetic memo)"* to *"exercisable after the seed script — **real memo,
  real spend, opt-in**"*.
* **(c) The adapter, the seed wiring, AND composition-root wiring** so the API path itself can draft.
  ⛔ **Not recommended, and arguably outside the HOLDS**: Scope B deliberately kept `CasePipeline` and the
  LLM-bearing composition **out of the request path** (`dependencies.py:112-117`, Q3-D) — *"which is what makes R4
  side-effect-free BY CONSTRUCTION rather than by discipline."* Reversing that is a separate decision with its own
  review, not a scope extension of #18.

**Sub-question Q8b — the register outcome**: on completion, should #18 be recorded as **DISCHARGED**,
**NARROWED** (the #19 precedent — genuinely improved, residual gap disclosed and tracked), or left **OPEN** with a
partial note? ⚑ Note that under **(a)** *"discharged"* would be **overclaiming** — a client that nothing
constructs does not make a real memo producible, which is exactly what #18 says is blocked.

**Recommendation (grounded)**: **(b)**, paired with **NARROWED-or-DISCHARGED decided at the gate on the evidence
actually produced** rather than promised now. (b) is the smallest scope that genuinely addresses what #18 claims
is blocked — *"no genuine LLM-drafted memo can be produced by this system today"* — while (c) reverses a
deliberate Scope B architectural decision and must not ride along on this item.

**[Answer]:**

**(b) — the adapter AND the seed-script wiring** (the opt-in real path from Q4), but **explicitly NOT composition-root wiring into the live request path**. Reversing Scope B's Q3-D decision to keep the LLM-bearing composition out of the request path is **its own separate, deliberate architectural decision and must not ride along on this item**.

**[Answer Q8b]:**

**Decide DISCHARGED vs NARROWED at the gate based on actual evidence produced, not promised now** — consistent with how **#19** was correctly marked NARROWED rather than closed once its own residual gap was found. Given (b)'s scope, **I'd expect this lands as DISCHARGED** for *"no genuine LLM-drafted memo can be produced"* (since one now can, via the opt-in path) — **but confirm that against whatever the implementation actually delivers, not against this stated expectation.**

---

## 4. HOLDS declared for this pass

| Hold | Status in this plan |
|---|---|
| No frozen-23 unit's internals edited **beyond** `memo_extensions/` **if Q2 lands there** | ⚑ Q2's **recommended** answer (c) reopens **NOTHING**. If (a) is chosen, `memo_extensions` is **explicitly reopened** with its own logged rationale (Q2b) — U24-reopening discipline. If (b) is chosen, that is a **frozen P1 reopening** and needs its own authorization. |
| `LLMClient` Protocol **implemented, never modified** | ✅ Held by design — the Protocol is `@runtime_checkable`, so a production client conforms **structurally without importing it**. `provider.py` is not touched under any Q2 option except (b). |
| WIRE-1's contract text not amended | ✅ Nothing here touches the wire contract. |
| `not_wired.py` not renamed | ✅ Untouched. **#13 stays open.** |
| U23's frozen test not edited | ✅ **No new route**, so `NFR-DEP-ROUTES-1`'s exact-set assertion is unaffected. |
| `audit_store` Docker-guard gap untouched — **5 errors stay exactly 5** | ✅ Confirmed as an explicit verification criterion (Q7c). |
| **tier-B NOT authorized** | ⚑ **Watch item.** Q1(a) makes `corpus_generator/build.py` **importable** for the first time as a side effect of fixing the manifest. **This does not authorize running it.** Q2(e) — reusing its `_GeminiLLMClient` — would be a tier-B promotion and is **not recommended**. Q7b(iii) must be fail-closed if chosen. |
| No new route under `backend/app/routes/` | ✅ None proposed. |
| **NO CODE GENERATED** | ✅ **Held. This document is the entire output of this pass.** |

---

## 5. What happens after the answers

1. Answers are logged **verbatim** to `audit.md` (complete raw input, never summarized).
2. A **separate code-generation plan** (`fix-register-18-code-gen-plan.md`) is written — numbered steps, TDD
   leaf-first, RED before GREEN, with its **own** gate — mirroring the `fix-register-19-code-gen-plan.md`
   discipline.
3. **No code is written until that second plan is approved.**

---

## 6. Summary of recommendations (all non-binding, all awaiting the user)

| Q | Topic | Recommendation |
|---|---|---|
| **Q1** | SDK | **(a)** adopt `google-genai`, **remove** `google-generativeai` |
| **Q2** | Location | **(c)** `backend/app/` — the only option reopening **nothing**, and the location both frozen docstrings name |
| **Q3** | Key | **(a)** + **(i)** + a real non-disclosure test, with the SDK-exception limit **disclosed, not over-claimed** |
| **Q4** | Seed script | **(b)** offline double **stays the default**; real path opt-in |
| **Q5** | Spend | **(a)+(b)+(c)**, cap **inside the wrapper** so retries are covered |
| **Q6** | Reproducibility | **(c)** pin a non-floating model id **and** disclose the residual prose-level gap |
| **Q7** | Tests | **(d)** injected SDK seam + guardrail tests; **(ii)** manual out-of-band real-API check |
| **Q8** | Scope | **(b)** adapter **+** seed wiring; register outcome decided **at the gate on evidence** |

---

---

## 7. ⛔ AMBIGUITY CHECK (run 2026-07-21T15:41:07Z against the complete Q1–Q8 answer set) — **NOT CLEAN**

Three interactions were checked. **(i) and (iii) are clean**, with constraints recorded. **(ii) surfaced ONE genuine
structural collision between two accepted answers.** It is raised as **Q9** rather than improvised.

### 7.1 (i) `backend/app/` coverage + test structure — ✅ CLEAN, 3 constraints recorded

* ✅ **`--cov=backend/app` ALREADY EXISTS** (`pyproject.toml:28`). **No `--cov` change is needed.**
* ✅ `test_frozen_untouched.py:61-69` asserts `owned == {"app"}` — a new module under `backend/app/` **keeps that
  true**. The location is structurally welcome.
* ⛑ **CONSTRAINT A — automatic scan enrollment.** BOTH `test_no_write_route.py:59` AND `test_frozen_untouched.py:16`
  build `PRODUCTION_FILES` via `APP_ROOT.rglob("*.py")`. A new `llm_client.py` is **auto-enrolled in every scan**.
  All eight assertion families were checked against a plausible implementation — `.insert(` / `.atomic(` /
  `.commit(` / `.put_application(` / `.put_recommendation(` / `CasePipeline` / `.draft(` / `.submit(` /
  `AUDIT_WRITER_URL` / `AUDIT_WRITER_PASSWORD` / `DictCommitContextProvider` are **all legitimately absent**.
  **NONE of the five #19-revised assertions breaks. None needs revision.** Verification of this is a named
  code-gen step, not an assumption.
* ⛑ **CONSTRAINT B — naming.** `test_frozen_untouched.py:39-42` forbids top-level defs named `Settings`,
  `AuditRecord`, `Role`, `to_role`, `AuthRBAC`, ... The new module **must not** declare a top-level `Settings`.
* ⛑ **CONFIRMATION 1 REQUIRED — pragma, not omit.** Q7(d) asks to *"coverage-omit only the thin network-bound
  line ... not the whole module"*. **`[tool.coverage.run] omit` is FILE-level only — it cannot omit a line.** The
  line-level mechanism is **`# pragma: no cover`**, already in `exclude_lines` (`pyproject.toml:127`) and already
  precedented **inside `backend/app/`** at `not_wired.py:127`. The intent is achievable **exactly as stated**, but
  via pragma — and therefore **NO new `omit` entry is added to `pyproject.toml`**.
  **[Confirm 1]:**

  **Confirmed** — use `# pragma: no cover` on the **network-bound line(s) only**, following the exact
  `not_wired.py:127` precedent already in `backend/app/`. **No new `[tool.coverage.run] omit` entry**; the rest of
  the module (the factory's flag check, the wrapper's cap logic, temperature pass-through, key non-disclosure)
  **stays genuinely covered and tested**.

### 7.2 (ii) Q5 cap × Q7 injected seam — ⛔ **ONE GENUINE COLLISION → Q9**

✅ **The cap IS tier-U testable.** It counts inside the wrapper's `generate()` — exactly where the orchestrator's
citation-retry loop re-enters (`MEMO_CITATION_RETRY_CAP`) — so **retries ARE counted**, satisfying Q5b's reason.
A duck-typed fake SDK object satisfies the seam with **no key and no `google-genai` installed**.

⛑ **BINDING CONSTRUCTION REQUIREMENT**: the wrapper **MUST import `google.genai` LAZILY** (inside the real-client
factory), **never at module import** — `build.py:32,37`'s precedent. A module-level import would ImportError the
entire offline suite and couple `backend/app/` to the SDK.

> ### ⛔ Q9 — WHERE DOES THE `ALLOW_REAL_LLM_CALLS` GUARD LIVE? (**the collision**)
>
> **Q5(a)** places the flag refusal **at client construction**. **Q7(d)** injects the SDK client **at the wrapper's
> constructor** so tier-U tests construct the wrapper with a **fake**. **These cannot both hold in one constructor**:
> if the guard sits in the wrapper's `__init__`, **every offline test constructing the wrapper with a fake is also
> refused** unless it sets `ALLOW_REAL_LLM_CALLS=true` — which **defeats the guard's meaning** (it becomes routine)
> and **makes the zero-config offline suite depend on a real-spend flag**, contradicting **Q4's non-negotiable**.
>
> * **(A)** Guard lives in a **separate real-client factory** (e.g. `build_gemini_client(settings)`) that constructs
>   the genuine SDK object. The wrapper's `__init__` stays **flag-free and purely injected**. Tier-U constructs the
>   wrapper directly with a fake; the flag guards **only the path that can actually reach the network**.
>   **The cap still lives in the wrapper (Q5b unaffected).**
> * **(B)** Guard in the wrapper `__init__`; tier-U tests monkeypatch the env var. **Cost**: the offline suite
>   depends on a real-spend flag; the guard becomes routine to bypass.
> * **(C)** Guard only at the seed script's opt-in path. **Cost**: contradicts Q5b's own reasoning — the cap would
>   cover future callers but the flag would not.
>
> **Recommendation (grounded)**: **(A)** — it puts the guard exactly on the spend-capable path, keeps the injected
> seam clean, and is the only option that satisfies Q4, Q5, Q5b and Q7 simultaneously. **Not decided here.**
>
> **[Answer Q9]:**
>
> **(A)** — a **separate real-client factory function** (`build_gemini_client(settings)`) carries the
> `ALLOW_REAL_LLM_CALLS` guard and constructs the real SDK-backed client; **the wrapper's own `__init__` stays
> flag-free and purely injected**, taking an already-constructed SDK client object as a parameter. **The cap
> continues to live inside the wrapper (per Q5b)**, so it applies uniformly regardless of how the client was
> constructed. This is the only option that satisfies **Q4's non-negotiable offline-by-default constraint**,
> **Q5's spend guard**, **Q5b's cap-covers-retries requirement**, and **Q7's injection-based testability** all at
> once, **without any of them undermining another**.

⛑ **CONFIRMATION 2 REQUIRED — `os.environ` for the flag.** **`ALLOW_REAL_LLM_CALLS` cannot be added to `Settings`**
— `secrets_config` is a **frozen-23 unit**; adding a field reopens it. It must be read from `os.environ` inside
`backend/app/`. Note `dependencies.py:66-69` **explicitly rejects `os.environ`** — but that rejection is scoped to
**secrets** (SEC-3 single-source). The flag is a **behavioural switch, not a credential**, so `os.environ` is
defensible — **but must be stated explicitly in the docstring**, since it reads as a contradiction of a comment two
files away.
**[Confirm 2]:**

**Confirmed** — `ALLOW_REAL_LLM_CALLS` reads `os.environ` directly in `backend/app/` (**in the factory function
from Q9**, not in `dependencies.py` or `Settings`). **Document explicitly in the factory's docstring why this is
not a SEC-3 violation**: `dependencies.py`'s rejection of `os.environ` is scoped to **credentials and secret
material specifically**; this is a **behavioural on/off switch controlling whether real spend is permitted, not a
credential**, and it **must never be conflated with or read alongside `GEMINI_API_KEY`'s own retrieval path**
(which stays **exclusively** through `get_settings()`).

### 7.3 (iii) Q6 pin × `corpus_generator/build.py`'s model reference — ✅ CLEAN, legitimately independent

`build.py:57` defaults `--model-id` to **`"gemini-2.5-flash"` — a FLOATING alias**. `GeminiAdapter`'s own default
(`provider.py:49`) is **the same floating alias**. **They are legitimately independent and need never match**:
`build.py` stamps `model_id` into the **tier-B corpus manifest** (`config.py:60`); our path stamps `model_version`
into the **`AuditRecord`** (`record_schema.py:50`). Different artifacts, different lifecycles, and **tier-B is not
authorized here**.

⛑ **Two consequences recorded as HOLDS**: this pass must **NOT** change `build.py`'s default (that edits a tier-B
module — out of scope), and Q6's pinned id must be supplied **as an argument at OUR construction site**, **NOT** by
changing `GeminiAdapter`'s default — **which would edit frozen U4 and is forbidden.**

---

## 8. ✅ AMBIGUITY CHECK CLOSED (2026-07-21T15:58:44Z)

**Q9 answered (A)** · **Confirm 1 confirmed** (pragma, not omit) · **Confirm 2 confirmed** (`os.environ` in the
factory, with the SEC-3 scoping rationale documented). **The check is now CLEAN and the shape is determinate:**

> **TWO PIECES, NOT ONE** — a **flag-free, purely-injected wrapper** (owning the cap, the temperature
> pass-through, the logging and the non-disclosure guarantee) **+** a **guarded factory** (owning the
> `ALLOW_REAL_LLM_CALLS` check, the lazy `google.genai` import, and the `get_settings()` key read).

**Code-gen plan written**: `fix-register-18-code-gen-plan.md`.

---

**⛔ STOP — SCOPING COMPLETE. NO CODE GENERATED. Proceed to the code-gen plan's own gate.**
