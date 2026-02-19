#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory

from dulwich.repo import Repo

from gaphor.storage.tests.fixtures import create_merge_conflict
from gaphor.ui import run

workspace = Path(__file__).parent.parent


def run_gaphor_with_merge_conflict():
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        repo = Repo.init(tmp_path)

        create_merge_conflict(
            repo,
            tmp_path / "RAAML.gaphor",
            (workspace / "test-models" / "RAAML-original.gaphor").read_text(),
            (workspace / "models" / "RAAML.gaphor").read_text(),
            (workspace / "test-models" / "RAAML-incoming.gaphor").read_text(),
        )

        run([__file__, str(tmp_path / "RAAML.gaphor")])


if __name__ == "__main__":
    run_gaphor_with_merge_conflict()
