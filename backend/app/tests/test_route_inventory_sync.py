"""The cross-check that keeps the two declared route inventories identical.

⚑ **Why two copies exist at all** (relaxation design Q1(c)): the inventory is read by
assertions in **two different units** — U23's ``backend/deploy_config/tests/test_routes.py``
and the composition root's ``backend/app/tests/test_no_write_route.py``. Sharing one module
is not available: U23's own ``test_routes.py`` asserts its scan *"imports only the PRODUCTION
composition root, never ``backend/app/tests``"*, and importing the U23 copy from
``backend/app/tests`` would make a frozen unit's test helper a dependency of the composition
root's tests. **Duplication + this cross-check** achieves the anti-drift property with **zero
new import edges**.

⚑ **The copies are read as TEXT and parsed with ``ast`` — never imported.** Reading a file is
not importing it, so no import edge is created in either direction and neither of the two
constraints above is engaged even in principle.

**Granularity**: the parsed **tuples** are compared, not the raw bytes — so comments,
ordering of comments, and formatting may legitimately differ between the copies while any
**semantic** difference fails. Each copy is additionally checked for **duplicate entries**,
so a duplicated entry cannot silently mask a missing one under set comparison.

**On drift**: fails loudly, naming **both absolute paths** and the symmetric difference **in
both directions**.
"""
from __future__ import annotations

import ast
from pathlib import Path

#: The two copies. The composition root's is authoritative; U23's is the deployment mirror.
APP_COPY = Path(__file__).resolve().parents[1] / "tests" / "_route_inventory.py"
DEPLOY_COPY = (
    Path(__file__).resolve().parents[2] / "deploy_config" / "tests" / "_route_inventory.py"
)

#: Every name the two copies must agree on.
SYNCED_NAMES = ("ROUTE_INVENTORY", "NON_GET_ALLOWLIST", "ROUTE_MODULE_INVENTORY")


def parse_inventory(source: str) -> dict[str, tuple]:
    """Extract the declared inventories from a module's SOURCE — by AST, never by import."""
    tree = ast.parse(source)
    found: dict[str, tuple] = {}
    for node in tree.body:
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            if isinstance(node.targets[0], ast.Name):
                target = node.targets[0].id
        if target in SYNCED_NAMES and node.value is not None:
            found[target] = tuple(ast.literal_eval(node.value))
    return found


def inventory_drift(app_source: str, deploy_source: str) -> dict[str, dict[str, list]]:
    """Return every semantic difference between two inventory sources.

    Empty dict == identical. Each entry names the symmetric difference **in both
    directions**, so a failure says exactly what diverged rather than "sets not equal".
    """
    app, deploy = parse_inventory(app_source), parse_inventory(deploy_source)
    drift: dict[str, dict[str, list]] = {}
    for name in SYNCED_NAMES:
        a, d = app.get(name), deploy.get(name)
        if a is None or d is None:
            drift[name] = {"missing_in_app": [] if a else ["<whole declaration>"],
                           "missing_in_deploy_config": [] if d else ["<whole declaration>"]}
            continue
        only_in_app = sorted(set(a) - set(d), key=repr)
        only_in_deploy = sorted(set(d) - set(a), key=repr)
        if only_in_app or only_in_deploy:
            drift[name] = {"only_in_app": only_in_app, "only_in_deploy_config": only_in_deploy}
    return drift


def test_the_two_route_inventories_are_identical():
    app_source = APP_COPY.read_text(encoding="utf-8")
    deploy_source = DEPLOY_COPY.read_text(encoding="utf-8")

    drift = inventory_drift(app_source, deploy_source)
    assert not drift, (
        f"declared route inventories have DRIFTED.\n"
        f"  authoritative: {APP_COPY}\n"
        f"  mirror:        {DEPLOY_COPY}\n"
        f"  differences:   {drift}"
    )

    # ⚑ Duplicate check, per copy — part of the comparator's specified granularity: a
    # duplicated entry collapses under set comparison and could otherwise MASK a missing one.
    for path, source in ((APP_COPY, app_source), (DEPLOY_COPY, deploy_source)):
        for name, entries in parse_inventory(source).items():
            assert len(entries) == len(set(entries)), f"{path}: {name} has duplicate entries"


def test_detector_flags_a_synthetic_inventory_drift():
    # ⚑ NON-VACUITY: the comparator must actually discriminate, or the test above rots into
    # a tautology. Each declaration is mutated in turn and must be reported by name.
    baseline = (
        'ROUTE_INVENTORY = (("/a", "get"),)\n'
        'NON_GET_ALLOWLIST = ()\n'
        'ROUTE_MODULE_INVENTORY = ("__init__.py",)\n'
    )
    mutations = {
        "ROUTE_INVENTORY": 'ROUTE_INVENTORY = (("/a", "get"), ("/b", "post"))',
        "NON_GET_ALLOWLIST": 'NON_GET_ALLOWLIST = (("/b", "post"),)',
        "ROUTE_MODULE_INVENTORY": 'ROUTE_MODULE_INVENTORY = ("__init__.py", "extra.py")',
    }
    for name, replacement in mutations.items():
        mutated = "\n".join(
            replacement if line.startswith(name) else line
            for line in baseline.strip().splitlines()
        )
        drift = inventory_drift(baseline, mutated)
        assert name in drift, f"comparator failed to flag drift in {name}"
        assert drift[name]["only_in_deploy_config"], f"{name}: the added entry must be reported"

    # ...and an identical pair must produce NO drift, so the comparator is not simply
    # reporting difference unconditionally.
    assert inventory_drift(baseline, baseline) == {}
