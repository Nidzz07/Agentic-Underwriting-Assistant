"""The authn policy constants — ONE reviewable location (Q5a).

⚑ Deliberately gathered here rather than scattered as literals across the service, so that
revisiting a threshold is a single, greppable, reviewable edit.

**Q5(a), and the reasoning, recorded so a future reader does not have to reconstruct it:**

* ``SESSION_TTL = 8h`` — covers one underwriter working day without a mid-review logout.
  A long TTL is **not** the risk it would be with a stateless JWT, because sessions are
  **server-side and revocable**: ``admin-cli set-role``, deactivation, or logout all take
  effect on the **next request**, never at token expiry.
* **No idle timeout** — keeps the first implementation simple and avoids a renewal path that
  would need its own tests. Absolute expiry is enforced server-side on every request.
* ``MAX_FAILED_ATTEMPTS = 5`` / ``LOCKOUT_DURATION = 15min`` — high enough not to lock out an
  ordinary typo, low enough to make online guessing useless against an Argon2id hash.

**Scope note (AUTHN-Fold-2 of the ambiguity-check):** a repo-wide scan found **no other
rate-limiting, lockout or session-lifetime assumption anywhere in the build**, and no NFR
pins a session lifetime — these constants contradict nothing.
"""
from __future__ import annotations

from datetime import timedelta

#: Absolute session lifetime. No sliding renewal, no idle timeout (Q5a).
SESSION_TTL = timedelta(hours=8)

#: Consecutive failures before the account locks.
MAX_FAILED_ATTEMPTS = 5

#: How long the lock holds once tripped.
LOCKOUT_DURATION = timedelta(minutes=15)
