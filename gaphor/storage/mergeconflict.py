from __future__ import annotations

import io
from pathlib import Path

try:
    import pygit2
except ImportError:
    import warnings

    warnings.warn("Library pygit2 not found", ImportWarning, stacklevel=1)


def in_git_repository(filename: Path) -> bool:
    return bool(pygit2.discover_repository(filename))


def split_ours_and_theirs(
    filename: Path,
    ancestor: io.BufferedIOBase,
    current: io.BufferedIOBase,
    incoming: io.BufferedIOBase,
) -> bool:
    """For a file name, find the current (ours) and incoming (theirs) file and serialize those
    to the respected files.
    """
    if "pygit2" not in globals():
        return False

    repo_path = pygit2.discover_repository(filename)
    if not repo_path:
        return False

    repo = pygit2.Repository(repo_path)
    work_path = Path(repo.workdir)
    if conflicts := repo.index.conflicts:
        for common, ours, theirs in conflicts:
            if work_path / common.path == filename:
                ancestor.write(repo.get(common.id).read_raw())
                current.write(repo.get(ours.id).read_raw())
                incoming.write(repo.get(theirs.id).read_raw())
                return True
    return False
