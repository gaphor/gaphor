from __future__ import annotations

import io
from pathlib import Path

import pygit2


def in_git_repository(filename: Path) -> bool:
    return bool(pygit2.discover_repository(filename))


def split_ours_and_theirs(
    filename: Path, current: io.TextIOBase, incoming: io.TextIOBase
) -> bool:
    """For a file name, find the current (ours) and incoming (theirs) file and serialize those
    to the respected files.
    """
    repo_path = pygit2.discover_repository(filename)
    if not repo_path:
        return False

    repo = pygit2.Repository(repo_path)
    work_path = Path(repo.workdir)
    if conflicts := repo.index.conflicts:
        for common, ours, theirs in conflicts:
            if work_path / common.path == filename:
                current.write(
                    repo.get(ours.id).read_raw().decode("utf-8", errors="replace")
                )
                incoming.write(
                    repo.get(theirs.id).read_raw().decode("utf-8", errors="replace")
                )
                return True
    return False
