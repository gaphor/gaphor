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


def split(fd: io.TextIOBase, current: io.TextIOBase, incoming: io.TextIOBase):
    CURRENT = 1
    INCOMING = 2
    BOTH = CURRENT | INCOMING
    state = BOTH
    found_merge_conflict = False
    for line in fd.readlines():
        if state == BOTH and line.startswith("<<<<<<<"):
            state = CURRENT
            found_merge_conflict = True
        elif state == CURRENT and line.startswith("======="):
            state = INCOMING
        elif state == INCOMING and line.startswith(">>>>>>>"):
            state = BOTH
        else:
            if state & CURRENT:
                current.write(line)
            if state & INCOMING:
                incoming.write(line)

    current.seek(0)
    incoming.seek(0)
    if found_merge_conflict:
        return current, incoming
    incoming.close()
    return current, None
