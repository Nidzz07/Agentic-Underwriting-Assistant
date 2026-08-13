"""The uploaded-document temp lifecycle and the orphan sweep (WIRE1-Fold-7, stage 2).

⛔ **NO ROUTE, NO MULTIPART, NO HTTP IN THIS FILE.** Q12(a) gave this its own stage for a reason:
**a retention bug is invisible to a green suite.** Every other test in this package would pass
with a PDF of an applicant's salary slip sitting in a temp directory forever. Isolating the
lifecycle is the only way to review it as the security property it is rather than as plumbing.

⚑ **ONE directory, not two.** Q13(b) — consuming `request.stream()` by hand instead of taking
`UploadFile` parameters — **eliminates starlette's `SpooledTemporaryFile`**, which rolls to real
disk above 1 MB and which the application does not own. So there is exactly one temp artifact per
request, in a root the app defines, and the sweep has exactly one place to look. Under the
rejected `UploadFile` approach the framework would have been writing files the sweep could
neither see nor safely touch.
"""
from __future__ import annotations

import os
import stat
import time
from pathlib import Path

import pytest

from backend.app import upload_storage as us


@pytest.fixture
def root(tmp_path) -> Path:
    """An isolated upload root. ⚑ Never the real one — these tests delete directories."""
    return tmp_path / "uploads"


class TestTheRequestTempDirectory:
    """A1–A5 — the per-request directory, and every exit path out of it."""

    def test_it_is_created_under_the_app_owned_root(self, root):
        with us.upload_temp_dir(root=root) as directory:
            assert directory.is_dir()
            assert directory.parent == root, "a request dir must live under the app-owned root"

    def test_it_is_removed_on_the_success_path(self, root):
        with us.upload_temp_dir(root=root) as directory:
            (directory / "salary_slip.pdf").write_bytes(b"%PDF-1.4 synthetic")
            assert (directory / "salary_slip.pdf").exists()
        assert not directory.exists(), "the request dir survived a normal exit"

    def test_it_is_removed_when_the_body_raises(self, root):
        """⛔ The path a `finally` exists for. An exception mid-request must not strand a PDF."""
        with pytest.raises(RuntimeError):
            with us.upload_temp_dir(root=root) as directory:
                (directory / "bank_statement.pdf").write_bytes(b"%PDF-1.4 synthetic")
                raise RuntimeError("intake blew up")
        assert not directory.exists(), "the request dir survived an exception"

    def test_two_concurrent_requests_get_DIFFERENT_directories(self, root):
        """⚑ NOT in the plan's step list. The sweep deletes by age, and the semaphore (stage 3)
        permits more than one parse at a time — so two requests sharing a directory would let one
        request's cleanup delete another's in-flight document. Cheap to pin, catastrophic to miss."""
        with us.upload_temp_dir(root=root) as first:
            with us.upload_temp_dir(root=root) as second:
                assert first != second
                assert first.exists() and second.exists()
            assert first.exists(), "the inner exit removed the OUTER request's directory"

    @pytest.mark.posix_only
    def test_the_directory_is_owner_only(self, root):
        """A4. ⚑ Marked `posix_only` on the established convention — Windows has no POSIX mode
        bits, and the deployment target is Linux/Render, so this is exercised in CI where it is
        real. The marker's registered reason names `resource.setrlimit`; the condition is the
        same platform split."""
        with us.upload_temp_dir(root=root) as directory:
            mode = stat.S_IMODE(directory.stat().st_mode)
            assert mode == 0o700, f"expected owner-only 0o700, got {oct(mode)}"

    def test_a_failure_inside_the_context_does_not_gain_the_path(self, root):
        """A5. ⛔ The directory name is derived from a request that carried an applicant's
        documents. The helper must re-raise the caller's exception UNCHANGED — wrapping or
        annotating it would put a filesystem path into an error that may reach a log or, worse,
        a WIRE-1 §4 `detail`."""
        with pytest.raises(RuntimeError) as excinfo:
            with us.upload_temp_dir(root=root) as directory:
                raise RuntimeError("intake rejected the application")
        assert str(directory) not in str(excinfo.value)
        assert excinfo.value.args == ("intake rejected the application",)


class TestTheOrphanSweep:
    """B1–B4 — the answer to the one window a `finally` cannot cover."""

    def _aged(self, root: Path, name: str, age_seconds: float) -> Path:
        directory = root / name
        directory.mkdir(parents=True)
        (directory / "leaked.pdf").write_bytes(b"%PDF-1.4 orphan")
        old = time.time() - age_seconds
        os.utime(directory, (old, old))
        return directory

    def test_it_removes_an_orphan_older_than_the_threshold(self, root):
        """⛔ THE WINDOW WITH NO IN-PROCESS ANSWER. A process killed mid-request — OOM, deploy,
        free-tier spin-down — runs no `finally`, so the PDF survives. On Render, spin-down is
        routine, which makes this the *normal* case, not the exceptional one."""
        orphan = self._aged(root, "req-orphan", us.ORPHAN_MAX_AGE_SECONDS + 60)
        removed = us.sweep_orphaned_uploads(root=root)
        assert not orphan.exists()
        assert removed == 1

    def test_it_leaves_a_FRESH_directory_alone(self, root):
        """⛔ THE LOAD-BEARING HALF. The sweep runs at startup while requests may already be in
        flight (and, in tests, while other fixtures hold directories). A sweep that deleted live
        temp dirs would corrupt concurrent requests — strictly worse than the leak it fixes."""
        fresh = self._aged(root, "req-live", 1)
        assert us.sweep_orphaned_uploads(root=root) == 0
        assert fresh.exists(), "the sweep deleted a live request's directory"

    def test_it_tolerates_a_MISSING_root(self, root):
        """First boot on a fresh container: the root does not exist yet."""
        assert not root.exists()
        assert us.sweep_orphaned_uploads(root=root) == 0

    def test_it_tolerates_an_UNREMOVABLE_entry_and_keeps_going(self, root, monkeypatch):
        """⚑ NOT in the plan's step list. A sweep that abandoned the whole run on one bad entry
        would leave every later orphan in place — and the entries it skips are exactly the ones
        most likely to be wedged."""
        self._aged(root, "req-a", us.ORPHAN_MAX_AGE_SECONDS + 60)
        self._aged(root, "req-b", us.ORPHAN_MAX_AGE_SECONDS + 60)

        real_rmtree = us.shutil.rmtree
        calls = {"n": 0}

        def flaky(path, *args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise OSError("device busy")
            return real_rmtree(path, *args, **kwargs)

        monkeypatch.setattr(us.shutil, "rmtree", flaky)
        removed = us.sweep_orphaned_uploads(root=root)
        assert calls["n"] == 2, "the sweep stopped after the first failure"
        assert removed == 1

    def test_the_sweep_itself_never_raises(self, root, monkeypatch):
        """B4, half one — the function is fail-open at its own boundary."""
        monkeypatch.setattr(us, "_iter_request_dirs", lambda _root: (_ for _ in ()).throw(OSError("boom")))
        assert us.sweep_orphaned_uploads(root=root) == 0


class TestTheRootIsAppOwned:
    """C3 — so the sweep can never reach another process's files."""

    def test_the_root_is_NOT_the_system_temp_directory_itself(self):
        """⛔ The sweep deletes by age. Pointed at the system temp root it would delete other
        processes' files — an editor's swap file, another service's socket. It must be an
        app-named SUBTREE, and nothing else may live there."""
        import tempfile as _t

        system_root = Path(_t.gettempdir()).resolve()
        assert us.UPLOAD_TEMP_ROOT.resolve() != system_root
        assert system_root in us.UPLOAD_TEMP_ROOT.resolve().parents
        assert "underwriting" in us.UPLOAD_TEMP_ROOT.name

    def test_the_max_age_is_a_named_constant(self):
        assert isinstance(us.ORPHAN_MAX_AGE_SECONDS, int) and us.ORPHAN_MAX_AGE_SECONDS > 0


class TestTheSweepRunsAtSTARTUP_NotAtConstruction:
    """C1-C2 + B4 — the three constraints the ambiguity-check's Fold B imposed on Q5(a)."""

    def test_create_app_itself_sweeps_NOTHING(self, monkeypatch):
        """C2. ⛔ **`create_app()` CONSTRUCTS NOTHING, and that is load-bearing.**

        Register #2's Fold C established this: the property is what keeps the ~2.6 s outlier fit
        off every app construction, of which the test suite performs several. A sweep placed in
        `create_app()`'s body would be the first eager side effect ever added to it — filesystem
        I/O, no less. It belongs in `lifespan`, which runs at STARTUP.
        """
        from backend.app import main

        sweeps = []
        monkeypatch.setattr(main, "sweep_orphaned_uploads", lambda *a, **k: sweeps.append(1))

        main.create_app()

        assert sweeps == [], "create_app() swept — it must construct nothing and do nothing"

    def test_startup_DOES_sweep(self, monkeypatch):
        """⚑ NON-VACUITY for the assertion above. If the sweep never ran at all, C2 would pass
        for the wrong reason and the orphan window would be silently unguarded."""
        from fastapi.testclient import TestClient

        from backend.app import main

        sweeps = []
        monkeypatch.setattr(main, "sweep_orphaned_uploads", lambda *a, **k: sweeps.append(1))

        with TestClient(main.create_app()):
            pass

        assert sweeps == [1], "startup did not sweep"

    def test_a_sweep_that_RAISES_does_not_prevent_startup(self, monkeypatch):
        """B4. ⛔ **THE STOP-GATE.** A sweep that took the application down at boot would be
        strictly worse than the leaked file it exists to remove — an outage in place of a
        retention issue. The lifespan layer must survive it even though the sweep function is
        already fail-open at its own boundary; this pins the SECOND layer, so a later change that
        makes the sweep raise cannot turn a cleanup failure into an outage.
        """
        from fastapi.testclient import TestClient

        from backend.app import main

        def exploding(*_args, **_kwargs):
            raise OSError("the temp root is unreadable")

        monkeypatch.setattr(main, "sweep_orphaned_uploads", exploding)

        with TestClient(main.create_app()) as client:
            # ⚑ Not merely "startup did not raise" — the app must actually SERVE.
            assert client.post("/applications", json={"form_fields": {}}).status_code == 401

    def test_the_lifespan_sweep_targets_the_APP_OWNED_root_by_default(self, monkeypatch):
        """⚑ NOT in the plan's step list. `sweep_orphaned_uploads()` is called with no argument at
        startup, so its DEFAULT root is what actually gets swept in production. A test that only
        ever passed an explicit `root=` would never exercise that default — and the default is the
        one value where getting it wrong deletes someone else's files."""
        from fastapi.testclient import TestClient

        from backend.app import main

        seen = {}
        monkeypatch.setattr(
            main, "sweep_orphaned_uploads",
            lambda *a, **k: seen.update(args=a, kwargs=k),
        )
        with TestClient(main.create_app()):
            pass

        assert seen == {"args": (), "kwargs": {}}, "startup passed an explicit root; production would not"
        assert us.UPLOAD_TEMP_ROOT.name == "underwriting-uploads"
