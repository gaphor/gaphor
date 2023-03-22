import pygit2
from pathlib import Path
from tempfile import TemporaryDirectory

from gaphor.ui import run
from gaphor.storage.tests.fixtures import create_merge_conflict


workspace = Path(__file__).parent.parent


def run_gaphor_with_merge_conflict():
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        repo = pygit2.init_repository(tmp_path)

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
