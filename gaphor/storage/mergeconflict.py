from __future__ import annotations

import io
from pathlib import Path

from dulwich.errors import NotGitRepository
from dulwich.index import IndexEntry
from dulwich.repo import Repo


def split_ours_and_theirs(
    filename: Path,
    ancestor: io.BufferedIOBase,
    current: io.BufferedIOBase,
    incoming: io.BufferedIOBase,
) -> bool:
    """For a file name, find the current (this/ours), incoming (theirs/other),
    and ancestor (common) blobs and seralize those to the IO buffers.
    """
    try:
        repo = Repo.discover(filename)
    except NotGitRepository:
        return False

    work_path = Path(repo.path)
    index = repo.open_index()
    if not index.has_conflicts():
        return False

    def _write(index_entry: IndexEntry, destination: io.BufferedIOBase):
        for data in repo.get_object(index_entry.sha).as_raw_chunks():
            destination.write(data)

    for relpath, entry in index.iteritems():
        if work_path / relpath.decode("utf-8") == filename:
            _write(entry.ancestor, ancestor)
            _write(entry.this, current)
            _write(entry.other, incoming)
            return True
    return False
