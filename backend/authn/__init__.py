"""authn — authentication: who the caller IS. (Register #25 / PER-4.)

⚑ The deliberate counterpart to the FROZEN ``auth_rbac`` (U11), which answers what a
*resolved* identity may DO. ``BR-AUTH-10`` deferred the authentication half as *"authn is
out of Phase-1 scope"* — a scope-widening the requirements record does not support, since
DISCOVER deferred only **OOS-3 (full SSO/OAuth)** while **PER-4 (basic login) was answered
IN and phase-tagged Phase 1**. This package is that missing half; the authn/authz boundary
BR-AUTH-10 left implicit is now explicit in the tree.

**Imports NOTHING from ``backend.app``** — the composition root imports this package, never
the reverse (asserted by ``tests/test_import_direction.py``, since this package is not in
``test_frozen_untouched.py``'s ``FROZEN_UNITS`` and so is not covered by that guard).

**No LLM. No credential VALUES.** Real adapters take an injected ``Engine`` (SEC-3).
"""
