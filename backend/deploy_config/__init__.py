"""deploy_config (U23, EPIC-6, Phase 2) — the deployment-config unit.

This package is **test-only**: it holds the ``deploy_validators`` scans (C-DEP-1) that validate
the committed deploy artifacts (`render.yaml`, `frontend/vercel.json` + build entry, `deploy/*`).
The deployable deliverables are **declarative config files at their platform-conventional homes**,
not Python modules here (DEP-D8 resolved). deploy-config edits no frozen unit and no composition
root; it PACKAGES the built system for a free-tier Render + Vercel validation deploy.
"""
