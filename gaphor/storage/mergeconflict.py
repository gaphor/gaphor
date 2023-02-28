from __future__ import annotations

import io
from pathlib import Path

import pygit2


def split_ours_and_theirs(filename: Path) -> tuple[bytes, bytes] | tuple[None, None]:
    repo_path = pygit2.discover_repository(filename)
    if not repo_path:
        return None, None

    repo = pygit2.Repository(repo_path)
    work_path = Path(repo.workdir)
    if conflicts := repo.index.conflicts:
        for common, ours, theirs in conflicts:
            if work_path / common.path == filename:
                return repo.get(ours.id).data, repo.get(theirs.id).data
    return None, None


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
