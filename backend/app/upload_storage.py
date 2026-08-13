"""Temp storage for uploaded documents — the retention half of WIRE1-Fold-7.

⛔ **THIS IS THE ONLY MODULE IN ``backend/app/`` THAT WRITES TO THE FILESYSTEM**, and that is
enforced, not conventional: ``test_no_write_route.py``'s ``_FILESYSTEM_WRITE_MODULES`` is an
**exact set** naming this file and nothing else. A second module that writes fails the suite, and
so does this one quietly ceasing to.

**What the contract promises, and this module keeps** (WIRE-1 §5, Fold-7, binding):

> An uploaded document exists on disk **only for the duration of the request that carried it**,
> under an application-owned temp root, and is deleted on **every** exit path. A file surviving an
> abnormal termination is removed by a **sweep at the next startup**.

⚑ **FOUR EXIT PATHS, AND ONLY THREE HAVE AN IN-PROCESS ANSWER.** Success, rejection and an
unhandled exception are all covered by ``upload_temp_dir``'s ``finally``. The fourth — the process
being **killed** (OOM, a deploy, Render's free-tier spin-down) — runs no ``finally`` at all. That
is what ``sweep_orphaned_uploads`` exists for, and on a free tier spin-down is **routine**, so the
"crash" case is the *normal* case rather than the exceptional one.

⚑ **ONE directory per request, not two.** Q13(b) — consuming ``request.stream()`` by hand rather
than declaring ``UploadFile`` parameters — **eliminates starlette's ``SpooledTemporaryFile``**,
which rolls to real disk above 1 MB and which this application does not own. Every uploaded byte
therefore lands in a directory created here, under a root defined here, which is the only reason a
sweep is safe: it never touches a path the framework manages.

**No LLM. No credentials. No applicant data leaves this module** — it moves bytes to a path and
removes them again; what is *in* those bytes is intake's concern.
"""
from __future__ import annotations

import logging
import shutil
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Iterator

_LOG = logging.getLogger(__name__)

#: The application-owned temp root.
#:
#: ⛔ **A SUBTREE of the system temp directory, never the system temp directory itself.** The
#: sweep below deletes by AGE; pointed at the system root it would delete other processes' files.
#: Nothing but this application's request directories may live here, which is what makes an
#: age-based sweep a safe operation rather than a reckless one.
#:
#: ⚑ Module-level and named once so a test can point it elsewhere — the shape
#: ``outlier_composition.CORPUS_DIR`` and ``dependencies.RULEBOOK_DIR`` already use.
UPLOAD_TEMP_ROOT: Path = Path(tempfile.gettempdir()) / "underwriting-uploads"

#: Prefix for a per-request directory. The sweep only ever considers entries carrying it, so an
#: unrelated directory that somehow appears under the root is left alone rather than deleted.
REQUEST_DIR_PREFIX = "req-"

#: How old an orphan must be before the sweep removes it.
#:
#: ⚑ **It must exceed the longest possible request.** Three documents at the 5 s parse timeout is
#: ~15 s; an hour is far beyond that with room for a slow upload on top. ⛔ The margin is the
#: safety property: too short and the sweep would delete a **live** request's directory at
#: startup, which is strictly worse than the leak it exists to remove.
ORPHAN_MAX_AGE_SECONDS: int = 3600


@contextmanager
def upload_temp_dir(root: Path | None = None) -> Iterator[Path]:
    """A per-request directory, removed on **every** exit path.

    ⚑ The caller's exception is re-raised **unchanged**: this contextmanager neither wraps nor
    annotates it. The directory name derives from a request carrying an applicant's documents, and
    an annotated exception is exactly how a filesystem path reaches a log — or, worse, a WIRE-1 §4
    ``detail``.
    """
    root = root if root is not None else UPLOAD_TEMP_ROOT
    root.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix=REQUEST_DIR_PREFIX, dir=root))
    try:
        yield directory
    finally:
        # ⚑ ``ignore_errors`` deliberately, on ``not_wired.py::_release``'s precedent: a cleanup
        # that itself fails must NOT mask the outcome the caller is in the middle of producing.
        # The sweep is the backstop for anything left behind.
        shutil.rmtree(directory, ignore_errors=True)


@contextmanager
def open_document(directory: Path, doc_type) -> Iterator[BinaryIO]:
    """An open handle for one uploaded document, inside ``directory``.

    ⛔ **THE ON-DISK NAME IS DERIVED FROM THE CLOSED ``DocType`` ENUM, NEVER FROM THE CLIENT.** A
    client-supplied filename is a path-traversal primitive, and the decision not to honour one
    belongs **here**, with the module that owns the retention guarantee — not in whatever code
    happens to be parsing the request. Callers pass a ``DocType``; they cannot pass a path.

    ⚑ **Why this exists at all**: so that **every byte this application writes to disk goes
    through this module**. ``multipart_reader`` streams chunks into the handle but never opens a
    file itself, which keeps ``_FILESYSTEM_WRITE_MODULES`` at exactly one member — the strongest
    form of that guard, and the one that makes "who can leave a PDF on disk?" answerable by
    reading a single file.
    """
    target = directory / f"{doc_type.value}.pdf"
    handle = target.open("wb")
    try:
        yield handle
    finally:
        handle.close()


def document_path(directory: Path, doc_type) -> Path:
    """Where :func:`open_document` puts that document. Same derivation, no side effect."""
    return directory / f"{doc_type.value}.pdf"


def _iter_request_dirs(root: Path) -> Iterator[Path]:
    """Request directories under ``root``. ⚑ A shallow ``iterdir``, never a recursive walk — this
    runs at every application startup, including several times per test session."""
    if not root.is_dir():
        return
    for entry in root.iterdir():
        if entry.is_dir() and entry.name.startswith(REQUEST_DIR_PREFIX):
            yield entry


def sweep_orphaned_uploads(
    root: Path | None = None,
    max_age_seconds: int | None = None,
    now: float | None = None,
) -> int:
    """Remove request directories older than ``max_age_seconds``. Returns how many were removed.

    ⛔ **FAIL-OPEN, ALWAYS.** This runs at application startup. A sweep that raised would take the
    whole service down at boot — **strictly worse than the file it was trying to remove**. Every
    failure mode is caught and logged: an unreadable root, a wedged directory, a permissions
    error. ⚑ A single unremovable entry does **not** abandon the run, because the entries most
    likely to be wedged are exactly the ones that would then keep every later orphan alive.

    ⚑ Nothing about an applicant is logged — a count and a directory name, never a document.
    """
    root = root if root is not None else UPLOAD_TEMP_ROOT
    max_age = ORPHAN_MAX_AGE_SECONDS if max_age_seconds is None else max_age_seconds
    cutoff = (time.time() if now is None else now) - max_age
    removed = 0
    try:
        for directory in _iter_request_dirs(root):
            try:
                if directory.stat().st_mtime >= cutoff:
                    continue          # a LIVE request — leave it alone
                shutil.rmtree(directory)
                removed += 1
            except OSError:
                _LOG.warning("upload sweep could not remove %s", directory.name)
                continue              # never abandon the run for one bad entry
    except Exception:                 # noqa: BLE001 - see the docstring: startup must not fail
        _LOG.warning("upload sweep failed; continuing startup")
        return removed
    return removed
