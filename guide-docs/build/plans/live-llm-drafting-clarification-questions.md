# LIVE LLM DRAFTING — CLARIFICATION QUESTIONS

**Status**: ✅ **BOTH ANSWERED 2026-08-16 — Q1: A (per-draft cap) · Q2: A (guard as inferred). BLOCK CLEARED.**
⚑ **SUPERSEDED header, preserved:** *"ONE BLOCKING CONTRADICTION. The code-generation plan is NOT
written until this is answered."* ⚠️ **The re-check against the corrected set found ONE NEW
interaction** created by the answer itself — see the parent plan's **§5.2**. It is resolved by
design, not by another question.
**Created**: 2026-08-16 · **Answered**: 2026-08-16
**Parent**: `live-llm-drafting-plan.md` (all ten answers embedded; ambiguity check at its §4)

The mandatory ambiguity check ran against the complete Q1–Q10 answer set. **Two of the three named
interactions resolved cleanly** and needed no decision — Q4×Q7 compose (with a scope expansion the
plan now names), and Q8's new guard cannot conflict with `case_lifecycle` because both candidate
guard files scan `APP_ROOT` only. **The third did not resolve**, and it is a genuine contradiction
rather than an underspecification, so it is asked rather than inferred.

⚑ Two corrections to the plan's own earlier findings were also forced by the check and are recorded
at its §4.0 — most importantly that **§1.9 was wrong: R4 *does* carry `model_version`** (nested in
`memo`, via `projections.py:184`'s `model_dump()`). Neither correction changes an answer, and
neither is asked about here.

---

## The contradiction

**Q1's answer states the cap's purpose. Q1's answer also adopts a mechanism that does not implement
that purpose once the client lives where this pass puts it.**

Q1 chose **A — full mirror of `CappedGeminiClient`'s shape, including the call cap**, and reframed
the cap explicitly as:

> *"runaway citation-retry-loop containment (provider-independent, and arguably MORE valuable
> against a weaker local model), **not spend control**."*

⛔ **But `CappedGeminiClient`'s counter is per-instance and monotonic, and it is never reset.**
`llm_client.py:60-70`: `self._count = 0` at construction, `self._count += 1` on every `generate`,
refuse permanently once `max_calls` is reached. The client will live inside `_CompositionSeams`,
which is behind `@lru_cache(maxsize=1)` (`dependencies.py:318`) — **one instance, one counter, for
the entire life of the server process.**

That is a **per-process budget**, which is a *spend-control* semantic — the exact framing Q1's
answer said it was moving away from. **Runaway-loop containment is inherently per-draft**: it should
bound how many times *one* drafting attempt may re-enter the model, and reset when the next draft
begins.

**The practical consequence, stated concretely.** At `max_calls=20`, with `MEMO_CITATION_RETRY_CAP`
(`orchestrator.py:118`) able to consume several calls per draft, a long-lived server **permanently
stops drafting after roughly 5–20 drafts** and returns 500s until the process is restarted, with no
reset short of a bounce. ⚑ The shape was safe in `CappedGeminiClient` because its only caller was
`seed_demo_cases.py`, a **short-lived script** where *per-process* ≈ *per-run*. Behind a cached seam
in a long-running FastAPI app it means something different. **Q1 was framed on the seed-script
precedent and could not have anticipated this.**

⚠️ **Q10's verification plan would plausibly hit it** — it drafts, re-drafts for the reproducibility
probe, and exercises the failure path, all within one server process.

---

## Clarification Question 1
Given that Q1's stated purpose is **runaway-loop containment** but `CappedGeminiClient`'s mechanism
is a **never-reset per-process counter**, which does the Ollama client implement?

A) **Per-draft cap** — the counter resets at the start of each drafting attempt (or a fresh
   counting scope is created per draft), so it bounds re-entry *within* one draft and never
   accumulates across drafts. Directly implements Q1's stated purpose; the server never
   self-disables. ⚠️ Departs from `CappedGeminiClient`'s literal shape, so "full mirror" becomes
   "same shape, one deliberate and documented difference."

B) **Keep per-process, raise the bound substantially** (e.g. 500+) and document it honestly as a
   *process budget / runaway backstop* rather than as loop containment. Preserves the mirror
   exactly; accepts that the server can eventually self-disable, but makes it rare enough to be a
   genuine emergency brake.

C) **Both, as two distinct bounds** — a small per-draft cap (true loop containment) *and* a large
   per-process cap (backstop against a pathological run). Most faithful to both readings; costs one
   extra counter and one extra named constant.

D) **Keep `CappedGeminiClient`'s shape exactly as-is** (`max_calls=20`, per-process, never reset)
   and accept that drafting disables itself after ~5–20 drafts until restart, as a deliberate
   conservative default for a first live-provider pass.

E) Other (please describe after [Answer]: tag below)

[Answer]: A — per-draft cap, not a raised per-process bound. This is the only option where the mechanism actually matches the stated purpose: “runaway citation-retry-loop containment” is inherently a per-draft concern (how many times can THIS draft retry before we give up), not a lifetime-of-the-process concern. Change the cap so it resets per invocation rather than accumulating monotonically across the cached client's lifetime — likely meaning the counter needs to live on something constructed per-draft, or be explicitly reset at the start of each draft() call, rather than living on the long-lived cached client instance itself.

Make explicit in the design: a cap-exceeded refusal and a connection failure must be distinguishable in the error message (per your own flag), since they call for opposite operator responses (restart the app vs. start Ollama) — don't let both collapse into an identical generic 500 body.

> **Recommendation: A.** It is the only option under which the mechanism matches the sentence Q1's
> answer actually wrote. ⚑ C is the most complete and is a defensible upgrade if you want the
> backstop too — but the per-process half only ever fires in a scenario the per-draft half already
> prevents, so it buys a second constant for a case that should be unreachable. ⛔ **D is the option
> to reject**: it makes a *server that stops working after a handful of drafts* a designed outcome,
> and because the failure surfaces as a **500 through Q4's new catch**, an operator would see
> *"drafting failed"* with no indication that the cause is a cumulative counter rather than Ollama
> being down — which is precisely the *"trains an operator to ignore FAILED lines"* failure mode
> `DraftOutcome.skipped` was introduced to prevent (`pipeline.py:52-56`). ⚠️ Whichever is chosen,
> **the refusal must be distinguishable from a connection failure in the error message**, since Q4's
> catch necessarily covers both and they call for opposite operator responses (restart the app vs.
> start Ollama).

---

## A second, non-blocking item — answer only if you want to change the default

Not a contradiction; the plan resolves it by inference and will proceed on that basis unless you
say otherwise. Recorded because it is a naming decision that outlives this pass.

Per §4.4, Q8's guard is confirmed to belong in **`test_no_write_route.py`** (which already hosts
`_PIPELINE_MODULES` and `_FILESYSTEM_WRITE_MODULES` in exactly this shape) rather than
`test_frozen_untouched.py`, and its name must carry its `backend/app/` scope so it cannot read as a
broader claim than it checks — the defect the TRIGGER-1 narrowing was written to fix. **The plan
will proceed with a scope-carrying name in `test_no_write_route.py`** unless you direct otherwise.

## Clarification Question 2 (optional)
Do you want to override either of those two inferred choices?

A) **No — proceed as inferred** (guard in `test_no_write_route.py`, scope-carrying name).
B) Yes — different file, different name, or both (describe).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — accept test_no_write_route.py as the guard's home, with the name explicitly carrying its backend/app/ scope (e.g., something like MEMO_EXTENSIONS_IMPORT_MODULES_FROM_APP or similar — avoid a bare/generic name that could later be misread as covering all production imports of memo_extensions project-wide, which is exactly the TRIGGER-1-shaped overclaim you flagged).

---

## What happens on answers

⛔ **On Clarification Question 1, the code-generation plan is written**: staged execution mirroring
Fold-6/Fold-7's multi-gate structure, predicted deltas per stage, RED-before-GREEN ordering, and
named stop-gates — presented for its own separate approval before any code is written.

⛔ **No backend file has been touched. No code has been written.**
